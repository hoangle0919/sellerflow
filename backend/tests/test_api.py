"""Route-level tests — the endpoints a real user actually hits.

Runs against a fresh, seeded temp DB (see conftest.py). Assertions avoid exact
counts so tests stay order-independent.
"""
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main  # noqa: E402

client = TestClient(main.app)

VALID_MERCHANT = {
    "shop_name": "Test Shop", "platform": "Shopee", "owner_name": "A", "phone": "",
    "monthly_revenue": 120_000_000, "revenue_growth": 0.12, "order_volume": 300,
    "avg_order_value": 400_000, "return_rate": 0.03, "rating": 4.6, "days_active": 400,
    "inventory_turnover": 5.0, "late_ship_rate": 0.02, "previous_loans": 1,
}
PREVIEW_PARAMS = {
    "monthly_revenue": 185_000_000, "revenue_growth": 0.22, "order_volume": 420,
    "avg_order_value": 440_000, "return_rate": 0.028, "rating": 4.9, "days_active": 680,
    "inventory_turnover": 6.2, "late_ship_rate": 0.018, "previous_loans": 2,
}


def _auth():
    tok = client.post("/api/auth/login", json={"password": "demo2025"}).json()["token"]
    return {"Authorization": f"Bearer {tok}"}


# ── Public surfaces ──
def test_health_operational():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "operational"


def test_config_ok():
    assert client.get("/api/config").status_code == 200


def test_landing_html_served():
    r = client.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]


# ── Preview (powers the live demo) ──
def test_preview_returns_decision_integrity_financing():
    d = client.get("/api/assess/preview", params=PREVIEW_PARAMS).json()
    assert d["decision"] in ("APPROVED", "CONDITIONAL", "REJECTED")
    assert "integrity" in d and "level" in d["integrity"]
    assert "financing" in d and "structure" in d["financing"]


def test_preview_clamps_out_of_range_without_crashing():
    p = dict(PREVIEW_PARAMS, monthly_revenue=-100, rating=99, return_rate=5)
    assert client.get("/api/assess/preview", params=p).status_code == 200


# ── Submit ──
def test_submit_creates_assessment():
    d = client.post("/api/sellers/submit", json=VALID_MERCHANT).json()
    assert d["decision"] in ("APPROVED", "CONDITIONAL", "REJECTED")
    assert d["seller_id"].startswith("RBF-") and "integrity" in d


def test_submit_rejects_invalid_input():
    assert client.post("/api/sellers/submit", json={"shop_name": ""}).status_code == 422
    bad = dict(VALID_MERCHANT, rating=99)  # rating out of 1..5
    assert client.post("/api/sellers/submit", json=bad).status_code == 422


# ── Waitlist (dedup) ──
def test_waitlist_register_then_duplicate():
    payload = {"email": "wl@example.com", "role": "lender"}
    assert client.post("/api/waitlist", json=payload).json()["status"] == "registered"
    assert client.post("/api/waitlist", json=payload).json()["status"] == "already_registered"


# ── API keys (self-serve pilot + dedup) ──
def test_pilot_key_issue_then_duplicate_conflict():
    r1 = client.post("/api/keys/issue", json={"email": "key@example.com"})
    assert r1.status_code == 200 and r1.json()["api_key"].startswith("sf_live_")
    assert client.post("/api/keys/issue", json={"email": "key@example.com"}).status_code == 409


def test_paid_key_requires_auth():
    assert client.post("/api/keys/issue", json={"email": "p@example.com", "plan": "scale"}).status_code == 401


# ── Auth ──
def test_login_rejects_wrong_password():
    assert client.post("/api/auth/login", json={"password": "wrong"}).status_code == 401


# ── Portfolio (auth-gated) ──
def test_portfolio_requires_auth():
    assert client.get("/api/portfolio").status_code == 401


def test_portfolio_with_auth_returns_stats():
    s = client.get("/api/portfolio", headers=_auth()).json()["stats"]
    for key in ("total", "approval_rate", "total_exposure", "visits_total", "live_submissions"):
        assert key in s


# ── Model status (three honest, separated tiers) ──
def test_model_status_keeps_tiers_separate():
    d = client.get("/api/model/status", headers=_auth()).json()
    assert d["training_baseline"]["data"] == "synthetic"
    assert d["methodology_validation"]["data"] == "real_public_credit_benchmarks"
    assert d["real_world_validation"] is None  # no real merchant outcomes yet


# ── Visit beacon ──
def test_visit_beacon_ok():
    assert client.post("/api/visit", json={"path": "/", "referrer": ""}).json()["ok"] is True


# ── Outcomes (learning loop, auth-gated) ──
def test_outcome_requires_auth():
    assert client.post("/api/sellers/RBF-XXXXXX/outcome", json={"outcome": "repaid"}).status_code == 401


def test_outcome_404_on_missing_seller():
    r = client.post("/api/sellers/NOPE/outcome", json={"outcome": "repaid"}, headers=_auth())
    assert r.status_code == 404


def test_outcome_records_on_real_seller():
    sellers = client.get("/api/portfolio", headers=_auth()).json()["sellers"]
    sid = sellers[0]["id"]
    r = client.post(f"/api/sellers/{sid}/outcome", json={"outcome": "repaid"}, headers=_auth())
    assert r.status_code == 200 and r.json()["status"] == "recorded"
