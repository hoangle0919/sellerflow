import os, uuid, hmac, secrets, time, hashlib
import json as jsonlib
import urllib.request
from collections import defaultdict, deque
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from models import SellerSubmission, WaitlistSignup, LoginRequest, KeyRequest
from database import get_db, init_db
from ml_engine import load_models, score, FEATURES

# ── Init ──
app = FastAPI(title="SellerFlow API", version="1.0.0", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
def issue_key(data: KeyRequest, request: Request, authorization: str = Header(default="")):
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
            raise HTTPException(status_code=409, detail="An active key already exists for this email. Write to hello@sellerflow.io to rotate it.")
        raw = f"sf_live_{secrets.token_urlsafe(24)}"
        conn.execute(
            "INSERT INTO api_keys (id, key_hash, company, email, plan, assessments_used, assessments_limit, created_at, active, period) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4())[:8].upper(), _hash_key(raw), data.company or "", data.email,
             plan, 0, PLAN_LIMITS[plan], datetime.now().isoformat(), 1, _current_period()),
        )
        conn.commit()
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
        raise HTTPException(status_code=422, detail="No email found on the payment. Write to hello@sellerflow.io.")

    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM stripe_claims WHERE session_id=?", (session_id,)).fetchone():
            return {"status": "already_claimed",
                    "detail": "A key was already issued for this payment. If you lost it, write to hello@sellerflow.io."}
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
def submit_seller(data: SellerSubmission, request: Request):
    usage = consume_api_key(request)
    if usage is None:
        rate_limit(request, "submit", limit=30, window_s=3600)
    result = score(data.dict())
    seller_id = f"SF-{str(uuid.uuid4())[:6].upper()}"
    conn = get_db()
    conn.execute("""
        INSERT INTO sellers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        seller_id, data.shop_name, data.platform, data.owner_name, data.phone,
        data.monthly_revenue, data.revenue_growth, data.order_volume, data.avg_order_value,
        data.return_rate, data.rating, data.days_active, data.inventory_turnover,
        data.late_ship_rate, data.previous_loans,
        result['pd_score'], result['pd_rf'], result['pd_lr'],
        result['decision'], result['credit_limit'], result['interest_rate'],
        result['risk_tier'], result['reasoning'],
        datetime.now().isoformat(), 'active'
    ))
    conn.commit()
    conn.close()
    payload = {
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        **result
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
    return dict(row)


@app.get("/api/portfolio")
def get_portfolio(_: None = Depends(require_auth)):
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM sellers ORDER BY created_at DESC").fetchall()]
    conn.close()
    total = len(rows)
    approved = sum(1 for r in rows if r['decision'] == 'APPROVED')
    conditional = sum(1 for r in rows if r['decision'] == 'CONDITIONAL')
    rejected = sum(1 for r in rows if r['decision'] == 'REJECTED')
    exposure = sum(r['credit_limit'] or 0 for r in rows)
    avg_pd = round(sum(r['pd_score'] or 0 for r in rows) / total, 4) if total else 0
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
        }
    }


# ── Signup notifications (active once RESEND_API_KEY + NOTIFY_EMAIL are set) ──
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")
NOTIFY_FROM = os.environ.get("NOTIFY_FROM", "SellerFlow <onboarding@resend.dev>")


def notify_signup(email: str, role: str, position: int):
    if not (RESEND_API_KEY and NOTIFY_EMAIL):
        return
    try:
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=jsonlib.dumps({
                "from": NOTIFY_FROM,
                "to": [NOTIFY_EMAIL],
                "subject": f"SellerFlow lead #{position}: {email}",
                "text": f"{email} ({role}) joined the waitlist at {datetime.now().isoformat()}.",
            }).encode(),
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass  # a failed notification must never affect the signup itself


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
    data = dict(
        monthly_revenue=monthly_revenue, revenue_growth=revenue_growth,
        order_volume=order_volume, avg_order_value=avg_order_value,
        return_rate=return_rate, rating=rating, days_active=days_active,
        inventory_turnover=inventory_turnover, late_ship_rate=late_ship_rate,
        previous_loans=previous_loans
    )
    return {"timestamp": datetime.now().isoformat(), **score(data)}


# ── Serve Frontend ──
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
@app.get("/{path:path}")
def serve_spa(path: str = ""):
    index = os.path.join(FRONTEND, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse({"message": "SellerFlow API running. Frontend not found.", "docs": "/api/docs"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
