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
    pw = os.environ["DASHBOARD_PASSWORD"]      # set by conftest; no default exists
    tok = client.post("/api/auth/login", json={"password": pw}).json()["token"]
    return {"Authorization": f"Bearer {tok}"}


def test_login_rejects_the_withdrawn_default_credential():
    """Regression guard: `demo2025` was a shipped fallback until 2026-08-06.
    The README now states no default exists; this asserts the code agrees."""
    assert main.DASHBOARD_PASSWORD is not None          # conftest configured one
    r = client.post("/api/auth/login", json={"password": "demo2025"})
    assert r.status_code == 401


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


# ── The withdrawn synthetic benchmark (P0-2 / D-026) ──
def test_training_baseline_reports_withdrawn_not_a_number():
    """The 0.92 AUC was withdrawn as a circular synthetic benchmark. The API
    must say so explicitly rather than serving the figure."""
    tb = client.get("/api/model/status", headers=_auth()).json()["training_baseline"]
    assert tb["auc"] is None                              # null, not a value
    assert "auc" in tb                                    # key retained for consumers
    assert tb["validation_status"] == "withdrawn"
    assert tb["reason"] == "synthetic circular-label benchmark"


def test_no_public_surface_promotes_a_synthetic_accuracy_figure():
    """Regression guard for P0-2. Scans the ENTIRE /api/model/status payload for
    any numeric value that could be read as the withdrawn benchmark. The only
    permitted appearance of 0.92 is `withdrawn_value`, which is explicitly
    labelled as the retracted figure."""
    d = client.get("/api/model/status", headers=_auth()).json()

    def numbers(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from numbers(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from numbers(v, f"{path}[{i}]")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield path, node

    offenders = [(p, v) for p, v in numbers(d)
                 if abs(v - 0.92) < 0.005 and not p.endswith("withdrawn_value")]
    assert offenders == [], f"withdrawn figure served at: {offenders}"


def test_real_data_benchmarks_survive_the_withdrawal_but_carry_their_status():
    """The 0.92 withdrawal is scoped — the UCI cross-validation on REAL
    borrowers with REAL outcomes is a different claim and must not be
    collateral damage. But `RESULTS_REGISTRY` R-002 marks those figures
    "Re-run pending (Phase 5 V-03)", and the API previously served them as
    settled. The status now travels with the numbers, because a registry note
    nobody curls is not a qualification."""
    mv = client.get("/api/model/status", headers=_auth()).json()["methodology_validation"]
    assert mv["reported_auc_uci_german_credit"] == 0.80
    assert mv["reported_auc_uci_taiwan_default"] == 0.77
    assert mv["validation_status"] == "pending_rerun", \
        "the pending-re-run status must ship with the figures"
    assert "NOT YET RE-VERIFIED" in mv["disclaimer"]
    assert "auc_uci_german_credit" not in mv, \
        "the unqualified key must not remain as an alias"


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
