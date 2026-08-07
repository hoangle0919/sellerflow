"""Model-artifact handling: absent, unreadable, incompatible (D-028).

The suite must never depend on a developer's untracked `.pkl`. `conftest.py`
points `RBF_MODEL_DIR` at an empty temp directory, so these run in the same
state as a clean checkout. Tests that need a real ensemble build a throwaway
one here and delete it; nothing is committed.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ml_engine  # noqa: E402
import financing_engine  # noqa: E402

MERCHANT = {
    "monthly_revenue": 120_000_000, "revenue_growth": 0.12, "order_volume": 300,
    "avg_order_value": 400_000, "return_rate": 0.03, "rating": 4.6,
    "days_active": 400, "inventory_turnover": 5.0, "late_ship_rate": 0.02,
    "previous_loans": 1,
}


class LoadsButCannotPredict:
    """Unpickles cleanly, raises on use — the shape of a cross-version artifact.

    Defined at module level because joblib pickles classes by reference; a
    class defined inside a test function is not importable and cannot be
    dumped.
    """

    def predict_proba(self, X):
        raise AttributeError("'LogisticRegression' object has no attribute 'n_iter_'")

    def transform(self, X):
        return X


def _write_broken_artifacts(directory):
    import joblib
    for name in ml_engine.MODEL_FILES.values():
        joblib.dump(LoadsButCannotPredict(), os.path.join(str(directory), name))


# ── the suite is independent of any developer's artifacts ───────────────────

def test_suite_does_not_use_the_repository_model_directory():
    """Regression guard for the defect that started this: the suite passed or
    failed depending on whose .pkl was on disk."""
    assert os.environ.get("RBF_MODEL_DIR"), "conftest must redirect the model dir"
    repo_models = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "models")
    assert os.path.abspath(ml_engine.MODEL_DIR) != os.path.abspath(repo_models)


def test_model_artifacts_are_not_tracked_by_git():
    """A pickle must never be committed to make tests pass."""
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    gitignore = open(os.path.join(repo, ".gitignore"), encoding="utf-8").read()
    assert "*.pkl" in gitignore


# ── absent ──────────────────────────────────────────────────────────────────

def test_absent_artifacts_are_classified_not_crashed(tmp_path):
    assert ml_engine.load_models(str(tmp_path)) is False
    st = ml_engine.model_status()
    assert st["available"] is False
    assert st["reason"] == "artifacts_absent"
    assert st["scoring_path"] == "heuristic"


def test_scoring_works_with_no_model_at_all(tmp_path):
    ml_engine.load_models(str(tmp_path))
    out = ml_engine.score(MERCHANT)
    assert 0.0 <= out["pd_score"] <= 1.0
    assert out["decision"] in ("APPROVED", "CONDITIONAL", "REJECTED")


def test_heuristic_scores_are_labelled_as_heuristic(tmp_path):
    """The score must not claim to come from the ensemble when it did not.
    Same class of defect as the withdrawn AUC: label contradicting artifact."""
    ml_engine.load_models(str(tmp_path))
    out = ml_engine.score(MERCHANT)
    assert out["scoring_path"] == "heuristic"
    assert out["model_version"] == ml_engine.HEURISTIC_VERSION
    assert out["model_version"] != ml_engine.ENSEMBLE_VERSION


def test_heuristic_scoring_is_deterministic(tmp_path):
    ml_engine.load_models(str(tmp_path))
    assert ml_engine.score(MERCHANT) == ml_engine.score(MERCHANT)


# ── unreadable ──────────────────────────────────────────────────────────────

def test_unreadable_artifacts_are_classified_not_crashed(tmp_path):
    for name in ml_engine.MODEL_FILES.values():
        (tmp_path / name).write_bytes(b"this is not a pickle")
    assert ml_engine.load_models(str(tmp_path)) is False
    st = ml_engine.model_status()
    assert st["available"] is False
    assert st["reason"] == "artifact_unreadable"
    assert st["detail"]


# ── incompatible: loads, then cannot predict ────────────────────────────────

def test_artifact_that_loads_but_cannot_predict_is_rejected(tmp_path):
    """THE case that motivated D-028. A cross-version pickle unpickles fine and
    raises only at predict_proba. Guarding the load alone catches the easy
    failure and misses this one, which then surfaces from a request handler.

    Simulated with objects that unpickle cleanly and fail on use -- the same
    shape as the real cross-version failure, without needing two sklearns."""
    _write_broken_artifacts(tmp_path)

    assert ml_engine.load_models(str(tmp_path)) is False
    st = ml_engine.model_status()
    assert st["reason"] == "artifact_incompatible"
    assert "unusable" in st["detail"]
    assert st["sklearn_runtime"]                      # names the runtime version


def test_rejected_artifact_does_not_leak_into_scoring(tmp_path):
    """Rejection must actually clear the globals, not merely set a flag."""
    _write_broken_artifacts(tmp_path)
    ml_engine.load_models(str(tmp_path))

    out = ml_engine.score(MERCHANT)                   # must not raise
    assert out["scoring_path"] == "heuristic"
    assert ml_engine._rf is None and ml_engine._lr is None and ml_engine._scaler is None


# ── a genuine ensemble, built deterministically and thrown away ─────────────

@pytest.mark.slow
def test_a_freshly_trained_artifact_is_accepted_and_labelled(tmp_path):
    """Proves the acceptance path still works — otherwise the tests above could
    pass with a loader that rejects everything."""
    sk = pytest.importorskip("sklearn")
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    import joblib

    rng = np.random.default_rng(20260803)          # deterministic fixture
    X = pd.DataFrame(rng.normal(size=(80, len(ml_engine.FEATURES))),
                     columns=ml_engine.FEATURES)
    y = (rng.random(80) < 0.3).astype(int)
    y[0], y[1] = 0, 1                              # guarantee both classes

    scaler = StandardScaler().fit(X)
    rf = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, y)
    lr = LogisticRegression(max_iter=200).fit(scaler.transform(X), y)

    joblib.dump(rf, tmp_path / ml_engine.MODEL_FILES["rf"])
    joblib.dump(lr, tmp_path / ml_engine.MODEL_FILES["lr"])
    joblib.dump(scaler, tmp_path / ml_engine.MODEL_FILES["scaler"])

    assert ml_engine.load_models(str(tmp_path)) is True
    st = ml_engine.model_status()
    assert st["available"] is True and st["scoring_path"] == "ensemble"

    out = ml_engine.score(MERCHANT)
    assert out["scoring_path"] == "ensemble"
    assert out["model_version"] == ml_engine.ENSEMBLE_VERSION
    assert sk.__version__                            # runtime recorded


# ── the deterministic layer is model-independent ────────────────────────────

def test_financing_arithmetic_does_not_depend_on_any_model(tmp_path):
    """The research-integrated product must stand without the ensemble."""
    ml_engine.load_models(str(tmp_path))             # force heuristic
    a = financing_engine.financing_structure(120_000_000, "Low Risk")
    b = financing_engine.financing_structure(120_000_000, "Low Risk")
    assert a == b
    assert a["repayment_cap"] > 0 and a["base_case_duration_months"] > 0

    scenarios = financing_engine.scenario_analysis(120_000_000, 0.10, a)
    assert len(scenarios) == 4


def test_financing_engine_imports_no_ml_stack():
    """Deterministic money math must not reach for sklearn."""
    src = open(financing_engine.__file__, encoding="utf-8").read()
    for banned in ("sklearn", "joblib", "ml_engine", "torch"):
        assert banned not in src, f"financing_engine imports {banned}"


def test_research_package_is_independent_of_the_backend():
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pkg = os.path.join(repo, "research", "rbf_sim")
    if not os.path.isdir(pkg):
        pytest.skip("research package not present")
    for root, _dirs, files in os.walk(pkg):
        if "__pycache__" in root:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            src = open(os.path.join(root, f), encoding="utf-8").read()
            for banned in ("import sklearn", "from sklearn", "import ml_engine",
                           "from ml_engine", "import main", "financing_engine"):
                assert banned not in src, f"research/{f} depends on the backend: {banned}"


# ── the API reports artifact state honestly ─────────────────────────────────

def test_health_does_not_advertise_a_model_it_is_not_running():
    """/api/health is the most-read surface in the app. With no artifact it
    must not claim an ensemble is scoring."""
    from fastapi.testclient import TestClient
    import main
    d = TestClient(main.app).get("/api/health").json()
    assert d["scoring_path"] == "heuristic"
    assert "ensemble" not in d["model"].lower()
    assert "heuristic" in d["model"].lower()


def test_model_status_endpoint_exposes_artifact_state():
    from fastapi.testclient import TestClient
    import main
    client = TestClient(main.app)
    # Login is rate-limited to 10 per 5 min per IP and the suite shares one
    # client address; clear the bucket so this test is order-independent.
    main._hits.clear()
    tok = client.post("/api/auth/login",
                      json={"password": os.environ["DASHBOARD_PASSWORD"]}).json()["token"]
    d = client.get("/api/model/status",
                   headers={"Authorization": f"Bearer {tok}"}).json()
    art = d["model_artifact"]
    assert art["scoring_path"] in ("ensemble", "heuristic")
    assert "available" in art and "sklearn_runtime" in art
    # The suite runs with an empty model dir, so this must be the honest answer.
    assert art["available"] is False
    assert art["reason"] == "artifacts_absent"
