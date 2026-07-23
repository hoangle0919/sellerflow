import os, uuid, hmac, secrets, time, hashlib, ssl
import json as jsonlib
import urllib.request, urllib.error
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Header, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from models import MerchantSubmission, WaitlistSignup, LoginRequest, KeyRequest, OutcomeRecord, VisitPing
from database import get_db, init_db
from ml_engine import load_models, score, FEATURES
from financing_engine import build_financing_analysis
from integrity_engine import screen_integrity

# ── Init ──
app = FastAPI(title="RBF API", version="1.0.0", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(Exception)
async def _unhandled_exception(request: Request, exc: Exception):
    """Never show a user a stack trace. HTTPException/validation errors are
    handled by FastAPI; this catches genuine bugs and returns a clean 500."""
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error",
                 "detail": "Something went wrong on our end. Please try again."},
    )


load_models()
init_db()

# ── Rate limiting (per-IP, in-memory sliding window) ──
_hits: dict[str, deque] = defaultdict(deque)


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request, bucket: str, limit: int, window_s: int):
    key = f"{bucket}:{client_ip(request)}"
    now = time.time()
    q = _hits[key]
    while q and q[0] < now - window_s:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    q.append(now)


# ── Auth ──
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "demo2025")
SESSION_TTL_S = 12 * 3600
_sessions: dict[str, float] = {}  # token -> expiry epoch


def require_auth(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    expiry = _sessions.get(token)
    if not token or expiry is None or expiry < time.time():
        _sessions.pop(token, None)
        raise HTTPException(status_code=401, detail="Not authenticated")


@app.post("/api/auth/login")
def login(data: LoginRequest, request: Request):
    rate_limit(request, "login", limit=10, window_s=300)
    if not hmac.compare_digest(data.password.encode(), DASHBOARD_PASSWORD.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    now = time.time()
    for t, exp in list(_sessions.items()):
        if exp < now:
            _sessions.pop(t, None)
    token = secrets.token_urlsafe(32)
    _sessions[token] = now + SESSION_TTL_S
    return {"token": token, "expires_in": SESSION_TTL_S}

# ── API Routes ──


@app.get("/api/health")
def health():
    conn = get_db()
    sellers = conn.execute("SELECT COUNT(*) FROM sellers").fetchone()[0]
    waitlist = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
    conn.close()
    return {
        "status": "operational",
        "version": "1.0.0",
        "model": "RF+LR ensemble v1.0 (synthetic baseline)",
        "sellers_assessed": sellers,
        "waitlist_count": waitlist,
        "avg_response_ms": 1200,
        "alerts_configured": bool(RESEND_API_KEY and NOTIFY_EMAIL),
    }


# ── API keys & plan metering ──
PLAN_LIMITS = {"pilot": 100, "scale": 5000}
STRIPE_PAYMENT_LINK = os.environ.get("STRIPE_PAYMENT_LINK", "")


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _current_period() -> str:
    return datetime.now().strftime("%Y-%m")


def consume_api_key(request: Request):
    """If an X-API-Key header is present, validate it and consume one assessment
    from the monthly quota. Returns usage info, or None for keyless requests."""
    raw = request.headers.get("x-api-key", "").strip()
    if not raw:
        return None
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM api_keys WHERE key_hash=? AND active=1", (_hash_key(raw),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid API key")
        period = _current_period()
        used = row["assessments_used"] if row["period"] == period else 0
        if used >= row["assessments_limit"]:
            raise HTTPException(
                status_code=429,
                detail=f"Monthly quota reached ({row['assessments_limit']} on the "
                       f"{row['plan']} plan). Resets next month or upgrade at /#pricing.",
            )
        conn.execute(
            "UPDATE api_keys SET assessments_used=?, period=? WHERE id=?",
            (used + 1, period, row["id"]),
        )
        conn.commit()
        return {"plan": row["plan"], "used": used + 1,
                "limit": row["assessments_limit"], "period": period}
    finally:
        conn.close()


@app.post("/api/keys/issue")
def issue_key(data: KeyRequest, request: Request, background: BackgroundTasks, authorization: str = Header(default="")):
    rate_limit(request, "keys", limit=5, window_s=86400)
    plan = data.plan.lower()
    if plan not in PLAN_LIMITS:
        raise HTTPException(status_code=422, detail=f"plan must be one of {sorted(PLAN_LIMITS)}")
    if plan != "pilot":
        # Paid plans are issued by the operator (post-payment), not self-serve
        require_auth(authorization)
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM api_keys WHERE email=? AND active=1", (data.email,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An active key already exists for this email. Write to lehuuhoang1909@gmail.com to rotate it.")
        raw = f"sf_live_{secrets.token_urlsafe(24)}"
        conn.execute(
            "INSERT INTO api_keys (id, key_hash, company, email, plan, assessments_used, assessments_limit, created_at, active, period) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4())[:8].upper(), _hash_key(raw), data.company or "", data.email,
             plan, 0, PLAN_LIMITS[plan], datetime.now().isoformat(), 1, _current_period()),
        )
        conn.commit()
        background.add_task(
            notify,
            f"RBF API key issued · {data.email} ({plan})",
            f"An API key was issued to {data.email} "
            f"(company: {data.company or '-'}) on the {plan} plan "
            f"at {datetime.now().isoformat()}.",
        )
    finally:
        conn.close()
    return {"api_key": raw, "plan": plan, "monthly_limit": PLAN_LIMITS[plan],
            "note": "Store this key now — it is shown only once. Send it as an X-API-Key header."}


@app.get("/api/keys/usage")
def key_usage(request: Request):
    raw = request.headers.get("x-api-key", "").strip()
    if not raw:
        raise HTTPException(status_code=401, detail="Send your key as an X-API-Key header")
    conn = get_db()
    row = conn.execute("SELECT * FROM api_keys WHERE key_hash=? AND active=1", (_hash_key(raw),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")
    period = _current_period()
    used = row["assessments_used"] if row["period"] == period else 0
    return {"plan": row["plan"], "used": used, "limit": row["assessments_limit"],
            "remaining": row["assessments_limit"] - used, "period": period}


@app.get("/api/config")
def public_config():
    return {"stripe_payment_link": STRIPE_PAYMENT_LINK}


# ── Stripe checkout → instant key issuance ──
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")


@app.get("/api/stripe/claim")
def stripe_claim(session_id: str, request: Request, background: BackgroundTasks):
    """Called by the frontend after Stripe redirects back with a checkout
    session id. Verifies the session was paid, then issues a Scale key —
    exactly once per session."""
    rate_limit(request, "claim", limit=15, window_s=3600)
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payments are not configured yet.")
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(status_code=422, detail="Invalid checkout session id.")

    req = urllib.request.Request(
        f"https://api.stripe.com/v1/checkout/sessions/{session_id}",
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            sess = jsonlib.load(r)
    except urllib.error.HTTPError:
        raise HTTPException(status_code=404, detail="Payment session not found.")
    except Exception:
        raise HTTPException(status_code=502, detail="Could not reach Stripe. Try again in a moment.")

    if sess.get("payment_status") != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed for this session.")
    email = (sess.get("customer_details") or {}).get("email") or sess.get("customer_email") or ""
    email = email.strip().lower()
    if not email:
        raise HTTPException(status_code=422, detail="No email found on the payment. Write to lehuuhoang1909@gmail.com.")

    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM stripe_claims WHERE session_id=?", (session_id,)).fetchone():
            return {"status": "already_claimed",
                    "detail": "A key was already issued for this payment. If you lost it, write to lehuuhoang1909@gmail.com."}
        # Upgrade path: retire any existing (e.g. pilot) key for this email
        conn.execute("UPDATE api_keys SET active=0 WHERE email=? AND active=1", (email,))
        raw = f"sf_live_{secrets.token_urlsafe(24)}"
        kid = str(uuid.uuid4())[:8].upper()
        conn.execute(
            "INSERT INTO api_keys (id, key_hash, company, email, plan, assessments_used, assessments_limit, created_at, active, period) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (kid, _hash_key(raw), "", email, "scale", 0, PLAN_LIMITS["scale"],
             datetime.now().isoformat(), 1, _current_period()),
        )
        conn.execute("INSERT INTO stripe_claims VALUES (?,?,?,?)",
                     (session_id, kid, email, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()
    background.add_task(notify_signup, email, "PAID — Scale subscription", 0)
    return {"api_key": raw, "plan": "scale", "monthly_limit": PLAN_LIMITS["scale"], "email": email,
            "note": "Store this key now — it is shown only once. Send it as an X-API-Key header."}


@app.post("/api/sellers/submit")
def submit_seller(data: MerchantSubmission, request: Request, background: BackgroundTasks):
    usage = consume_api_key(request)
    if usage is None:
        rate_limit(request, "submit", limit=30, window_s=3600)
    result = score(data.model_dump())
    seller_id = f"RBF-{str(uuid.uuid4())[:6].upper()}"
    conn = get_db()
    # Integrity screen: compare against this merchant's own recent submissions
    # (matched on shop name or phone) before this one is inserted.
    cutoff = (datetime.now() - timedelta(days=90)).isoformat()
    priors = [dict(r) for r in conn.execute(
        "SELECT monthly_revenue FROM sellers WHERE created_at >= ? AND "
        "(LOWER(TRIM(shop_name)) = LOWER(TRIM(?)) OR (phone != '' AND phone = ?))",
        (cutoff, data.shop_name, data.phone or ""),
    ).fetchall()]
    integrity = screen_integrity(data.model_dump(), prior_submissions=priors)
    conn.execute("""
        INSERT INTO sellers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        seller_id, data.shop_name, data.platform, data.owner_name, data.phone,
        data.monthly_revenue, data.revenue_growth, data.order_volume, data.avg_order_value,
        data.return_rate, data.rating, data.days_active, data.inventory_turnover,
        data.late_ship_rate, data.previous_loans,
        result['pd_score'], result['pd_rf'], result['pd_lr'],
        result['decision'], result['credit_limit'], result['interest_rate'],
        result['risk_tier'], result['reasoning'],
        datetime.now().isoformat(), 'active', 'live'
    ))
    conn.commit()
    conn.close()
    channel = "API key" if usage is not None else "web form"
    background.add_task(
        notify,
        f"RBF assessment · {data.shop_name} -> {result['decision']}",
        f"A real merchant was assessed via {channel} at {datetime.now().isoformat()}.\n\n"
        f"Merchant : {data.shop_name} ({data.platform})\n"
        f"Revenue  : {data.monthly_revenue:,.0f}/mo\n"
        f"Decision : {result['decision']} · {result['risk_tier']} · PD {result['pd_score']:.1%}\n"
        f"Integrity: {integrity['level']} ({integrity['flags']} flag(s))\n"
        f"Seller ID: {seller_id}\n\n"
        f"See the dashboard: https://sellerflow-production.up.railway.app",
    )
    payload = {
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        **result,
        "integrity": integrity,
        "financing": build_financing_analysis(data.model_dump(), result["risk_tier"]),
    }
    if usage is not None:
        payload["usage"] = usage
    return payload


@app.get("/api/sellers/{seller_id}")
def get_seller(seller_id: str, _: None = Depends(require_auth)):
    conn = get_db()
    row = conn.execute("SELECT * FROM sellers WHERE id=?", (seller_id.upper(),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Seller not found")
    record = dict(row)
    record["financing"] = build_financing_analysis(record, record.get("risk_tier", "High Risk"))
    conn2 = get_db()
    record["outcomes"] = [dict(r) for r in conn2.execute(
        "SELECT outcome, amount_remitted, note, recorded_at FROM outcomes "
        "WHERE seller_id=? ORDER BY recorded_at DESC", (seller_id.upper(),)
    ).fetchall()]
    conn2.close()
    return record


@app.post("/api/sellers/{seller_id}/outcome")
def record_outcome(seller_id: str, data: OutcomeRecord, _: None = Depends(require_auth)):
    """Record a real, adjudicated repayment outcome. This is the only way a
    ground-truth label enters the system — always lender-recorded, never
    inferred by the model. These labels are what the learning loop trains on
    once enough accumulate (see /api/model/status)."""
    conn = get_db()
    row = conn.execute("SELECT id FROM sellers WHERE id=?", (seller_id.upper(),)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")
    oid = str(uuid.uuid4())[:8].upper()
    conn.execute(
        "INSERT INTO outcomes VALUES (?,?,?,?,?,?)",
        (oid, seller_id.upper(), data.outcome, data.amount_remitted,
         data.note, datetime.now().isoformat()),
    )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM outcomes").fetchone()[0]
    conn.close()
    return {"status": "recorded", "outcome_id": oid, "total_outcomes": total}


@app.get("/api/model/status")
def model_status(_: None = Depends(require_auth)):
    """The learning loop's honest state. Reports the synthetic training
    baseline AND real-world validation computed from recorded outcomes —
    never conflating the two. Real metrics appear only once enough
    adjudicated outcomes exist to compute them."""
    conn = get_db()
    rows = [dict(r) for r in conn.execute(
        "SELECT s.pd_score, s.decision, o.outcome FROM outcomes o "
        "JOIN sellers s ON s.id = o.seller_id"
    ).fetchall()]
    conn.close()

    MIN_FOR_METRICS = 30
    n = len(rows)
    # A defaulted or late outcome is the positive class (bad); repaid is good.
    labels = [1 if r["outcome"] in ("defaulted", "late") else 0 for r in rows]
    scores = [float(r["pd_score"] or 0) for r in rows]
    bad = sum(labels)
    good = n - bad

    real = None
    if n >= MIN_FOR_METRICS and bad > 0 and good > 0:
        real = {
            "outcomes_used": n,
            "observed_default_rate": round(bad / n, 4),
            "real_auc": _auc(scores, labels),
            "note": "Computed from lender-recorded outcomes on real merchants.",
        }

    return {
        "training_baseline": {
            "auc": 0.92,
            "data": "synthetic",
            "disclaimer": "Measured on held-out SYNTHETIC validation data. It "
                          "describes separation of synthetic-good from synthetic-bad, "
                          "NOT real-world predictive accuracy.",
        },
        "methodology_validation": {
            "data": "real_public_credit_benchmarks",
            "auc_uci_german_credit": 0.80,
            "auc_uci_taiwan_default": 0.77,
            "method": "5-fold cross-validated AUC of the production RF+LR ensemble "
                      "on real borrowers with real, adjudicated default outcomes.",
            "disclaimer": "Validates the MODELING METHOD on real data — NOT the "
                          "production merchant model, which uses e-commerce features "
                          "and still has no real merchant outcomes. Reproduce: "
                          "backend/validate_on_real_data.py.",
        },
        "real_world_validation": real,
        "learning_loop": {
            "outcomes_recorded": n,
            "outcomes_needed_for_metrics": max(0, MIN_FOR_METRICS - n),
            "status": "collecting_outcomes" if real is None else "validated",
            "retrain_policy": "Retrain + recalibrate when a cohort of adjudicated "
                              "outcomes is available; promote only if real-world AUC "
                              "on a holdout beats the incumbent.",
        },
    }


def _auc(scores, labels):
    """Rank-based ROC AUC (Mann-Whitney U). No sklearn dependency at request time."""
    pairs = sorted(zip(scores, labels), key=lambda p: p[0])
    ranks = {}
    i = 0
    # average ranks for ties
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2 + 1
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    pos = sum(ranks[idx] for idx, (_, lab) in enumerate(pairs) if lab == 1)
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    auc = (pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return round(auc, 4)


@app.get("/api/portfolio")
def get_portfolio(_: None = Depends(require_auth)):
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM sellers ORDER BY created_at DESC").fetchall()]
    today = datetime.now().date().isoformat()
    v_total = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    v_today = conn.execute("SELECT COUNT(*) FROM visits WHERE created_at >= ?", (today,)).fetchone()[0]
    v_last = conn.execute("SELECT MAX(created_at) FROM visits").fetchone()[0]
    conn.close()
    total = len(rows)
    approved = sum(1 for r in rows if r['decision'] == 'APPROVED')
    conditional = sum(1 for r in rows if r['decision'] == 'CONDITIONAL')
    rejected = sum(1 for r in rows if r['decision'] == 'REJECTED')
    exposure = sum(r['credit_limit'] or 0 for r in rows)
    avg_pd = round(sum(r['pd_score'] or 0 for r in rows) / total, 4) if total else 0
    live = sum(1 for r in rows if r.get('source') == 'live')
    return {
        "sellers": rows,
        "stats": {
            "total": total,
            "approved": approved,
            "conditional": conditional,
            "rejected": rejected,
            "approval_rate": round(approved / total, 3) if total else 0,
            "total_exposure": exposure,
            "avg_pd": avg_pd,
            "live_submissions": live,
            "visits_total": v_total,
            "visits_today": v_today,
            "last_visit": v_last,
        }
    }


@app.post("/api/visit")
def record_visit(data: VisitPing, request: Request):
    """Anonymous page-view beacon — no IP, no cookie, no fingerprint stored.
    The frontend fires it once per browser session so this counts visits,
    not reloads."""
    rate_limit(request, "visit", limit=240, window_s=3600)
    conn = get_db()
    conn.execute(
        "INSERT INTO visits VALUES (?,?,?,?)",
        (str(uuid.uuid4())[:8], (data.path or "/")[:200],
         (data.referrer or "")[:300], datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


# ── Signup notifications (active once RESEND_API_KEY + NOTIFY_EMAIL are set) ──
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")
NOTIFY_FROM = os.environ.get("NOTIFY_FROM", "RBF <onboarding@resend.dev>")


def notify(subject: str, text: str):
    """Best-effort operator alert via Resend. No-op unless RESEND_API_KEY and
    NOTIFY_EMAIL are set. A failed notification must never affect the request."""
    if not (RESEND_API_KEY and NOTIFY_EMAIL):
        return
    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=jsonlib.dumps({
                "from": NOTIFY_FROM,
                "to": [NOTIFY_EMAIL],
                "subject": subject,
                "text": text,
            }).encode(),
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
                # Resend is behind Cloudflare, which blocks the default
                # Python-urllib User-Agent (error 1010). Send a normal one.
                "User-Agent": "Mozilla/5.0 (compatible; RBF-notify/1.0)",
            },
        )
        urllib.request.urlopen(req, timeout=8, context=ctx)
    except Exception as e:
        # A failed alert must never affect the request — but log it so a
        # silent failure (like the SSL + Cloudflare bugs) can't hide again.
        print(f"[notify] alert send failed: {type(e).__name__}: {e}", flush=True)


def notify_signup(email: str, role: str, position: int):
    notify(f"RBF lead #{position}: {email}",
           f"{email} ({role}) joined the waitlist at {datetime.now().isoformat()}.")


@app.post("/api/waitlist")
def join_waitlist(data: WaitlistSignup, request: Request, background: BackgroundTasks):
    rate_limit(request, "waitlist", limit=10, window_s=3600)
    conn = get_db()
    existing = conn.execute("SELECT id FROM waitlist WHERE email=?", (data.email,)).fetchone()
    if existing:
        count = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
        conn.close()
        return {"status": "already_registered", "position": count}
    wid = str(uuid.uuid4())[:8].upper()
    conn.execute("INSERT INTO waitlist VALUES (?,?,?,?,?,?)", (
        wid, data.email, data.company or "", data.role,
        conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0] + 1,
        datetime.now().isoformat()
    ))
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
    conn.close()
    background.add_task(notify_signup, data.email, data.role, count)
    return {"status": "registered", "position": count, "waitlist_id": wid}


@app.get("/api/waitlist/entries")
def waitlist_entries(_: None = Depends(require_auth)):
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM waitlist ORDER BY created_at DESC").fetchall()]
    conn.close()
    return {"entries": rows}


@app.get("/api/waitlist/count")
def waitlist_count():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
    conn.close()
    return {"count": count}


@app.get("/api/assess/preview")
def preview_assess(
    request: Request,
    monthly_revenue: float = 150_000_000,
    revenue_growth: float = 0.15,
    order_volume: int = 300,
    avg_order_value: float = 350_000,
    return_rate: float = 0.04,
    rating: float = 4.5,
    days_active: int = 400,
    inventory_turnover: float = 5.0,
    late_ship_rate: float = 0.03,
    previous_loans: int = 1,
):
    rate_limit(request, "preview", limit=400, window_s=3600)
    monthly_revenue = max(1.0, min(monthly_revenue, 1e13))
    revenue_growth = max(-0.35, min(revenue_growth, 0.90))
    order_volume = max(1, min(order_volume, 10_000_000))
    avg_order_value = max(1.0, min(avg_order_value, 1e10))
    return_rate = max(0.0, min(return_rate, 0.40))
    rating = max(1.0, min(rating, 5.0))
    days_active = max(1, min(days_active, 20_000))
    inventory_turnover = max(0.0, min(inventory_turnover, 1000.0))
    late_ship_rate = max(0.0, min(late_ship_rate, 0.40))
    previous_loans = max(0, min(previous_loans, 1000))
    data = dict(
        monthly_revenue=monthly_revenue, revenue_growth=revenue_growth,
        order_volume=order_volume, avg_order_value=avg_order_value,
        return_rate=return_rate, rating=rating, days_active=days_active,
        inventory_turnover=inventory_turnover, late_ship_rate=late_ship_rate,
        previous_loans=previous_loans
    )
    result = score(data)
    return {
        "timestamp": datetime.now().isoformat(),
        **result,
        "integrity": screen_integrity(data),  # keyless preview: no identity, resubmission check skipped
        "financing": build_financing_analysis(data, result["risk_tier"]),
    }


# ── Serve Frontend ──
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
@app.get("/{path:path}")
def serve_spa(path: str = ""):
    if path:
        root = os.path.realpath(FRONTEND)
        candidate = os.path.realpath(os.path.join(root, path))
        if candidate.startswith(root + os.sep) and os.path.isfile(candidate):
            return FileResponse(candidate)
    index = os.path.join(FRONTEND, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse({"message": "RBF API running. Frontend not found.", "docs": "/api/docs"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
