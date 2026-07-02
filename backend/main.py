import os, uuid, hmac, secrets
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from models import SellerSubmission, WaitlistSignup, LoginRequest
from database import get_db, init_db
from ml_engine import load_models, score, FEATURES

# ── Init ──
app = FastAPI(title="SellerFlow API", version="1.0.0", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

load_models()
init_db()

# ── Auth ──
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "demo2025")
_sessions: set[str] = set()


def require_auth(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    if not token or token not in _sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")


@app.post("/api/auth/login")
def login(data: LoginRequest):
    if not hmac.compare_digest(data.password.encode(), DASHBOARD_PASSWORD.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = secrets.token_urlsafe(32)
    _sessions.add(token)
    return {"token": token}

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


@app.post("/api/sellers/submit")
def submit_seller(data: SellerSubmission):
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
    return {
        "seller_id": seller_id,
        "timestamp": datetime.now().isoformat(),
        **result
    }


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


@app.post("/api/waitlist")
def join_waitlist(data: WaitlistSignup):
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
    return {"status": "registered", "position": count, "waitlist_id": wid}


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
