"""Underwriting ensemble loading and scoring.

THE MODEL IS SECONDARY AND EXPLICITLY UNVALIDATED. Its training benchmark was
withdrawn as circular (D-026). Nothing downstream of the PD estimate depends on
a model: the advance, remittance, cap, scenarios and risk findings are plain
deterministic arithmetic in `financing_engine.py`. The service is fully
functional with no model artifact at all.

MODEL ARTIFACTS ARE NOT IN THE REPOSITORY. `*.pkl` is gitignored. Production
trains its own at deploy time (`railway.toml`: `train_model.py
--skip-if-exists`) from `generate_data.py`, so the artifact is always built by
the same interpreter and scikit-learn that will consume it. A clean checkout has
no model and must not pretend otherwise -- hence the honest fallback below.

WHY LOADING IS NOT ENOUGH (D-028). A pickle written by a different
scikit-learn version frequently *unpickles successfully* and then raises at
first use, because attributes added or renamed between versions are missing on
the reconstructed estimator. Guarding only `joblib.load` therefore catches the
easy case (absent file) and misses the dangerous one (present but unusable),
which surfaces later as a 500 from a request handler. Every artifact is
smoke-tested against a fixed feature row at load time; anything that cannot
produce a prediction is rejected and the deterministic fallback is used.
"""
import os
import warnings

import joblib
import pandas as pd

from database import _build_reasoning
from money import to_increment

BASE = os.path.dirname(__file__)

#: Overridable so tests never depend on a developer's untracked artifacts.
MODEL_DIR = os.environ.get("RBF_MODEL_DIR") or os.path.join(BASE, "models")

FEATURES = [
    'monthly_revenue', 'revenue_growth', 'order_volume', 'avg_order_value',
    'return_rate', 'rating', 'days_active', 'inventory_turnover',
    'late_ship_rate', 'previous_loans'
]

MODEL_FILES = {"rf": "rf_model.pkl", "lr": "lr_model.pkl", "scaler": "scaler.pkl"}

#: Fixed row used to prove a loaded artifact can actually predict. Values are
#: arbitrary but constant, so the check is deterministic.
_SMOKE_ROW = {
    'monthly_revenue': 120_000_000, 'revenue_growth': 0.12, 'order_volume': 300,
    'avg_order_value': 400_000, 'return_rate': 0.03, 'rating': 4.6,
    'days_active': 400, 'inventory_turnover': 5.0, 'late_ship_rate': 0.02,
    'previous_loans': 1,
}

_rf = _lr = _scaler = None
_STATUS = {"available": False, "reason": "not_loaded", "detail": None}

HEURISTIC_VERSION = "heuristic-fallback-v1"
ENSEMBLE_VERSION = "v1.0-synthetic"


def _sklearn_version():
    try:
        import sklearn
        return sklearn.__version__
    except Exception:
        return None


def model_status() -> dict:
    """Whether the ensemble is usable, and if not, precisely why."""
    return {**_STATUS, "sklearn_runtime": _sklearn_version(),
            "model_dir": MODEL_DIR,
            "scoring_path": "ensemble" if _STATUS["available"] else "heuristic",
            "note": "The underwriting ensemble is a secondary, explicitly "
                    "unvalidated component. Financing arithmetic is "
                    "deterministic and does not use it."}


def load_models(model_dir: str = None) -> bool:
    """Load and VALIDATE the ensemble. Never raises; returns availability.

    Failure is classified rather than collapsed into one message, because
    "you never trained a model" and "your model was built by another
    scikit-learn" need different actions from an operator.
    """
    global _rf, _lr, _scaler, _STATUS
    d = model_dir or MODEL_DIR
    _rf = _lr = _scaler = None

    missing = [f for f in MODEL_FILES.values() if not os.path.exists(os.path.join(d, f))]
    if missing:
        _STATUS = {"available": False, "reason": "artifacts_absent",
                   "detail": f"missing {', '.join(sorted(missing))} in {d}"}
        print(f"ℹ️  No model artifacts in {d} ({', '.join(sorted(missing))}). "
              f"Scoring uses the deterministic heuristic fallback. "
              f"Build one with: python train_model.py")
        return False

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")      # version warnings become errors
            rf = joblib.load(os.path.join(d, MODEL_FILES["rf"]))
            lr = joblib.load(os.path.join(d, MODEL_FILES["lr"]))
            scaler = joblib.load(os.path.join(d, MODEL_FILES["scaler"]))
    except Exception as e:
        _STATUS = {"available": False, "reason": "artifact_unreadable",
                   "detail": f"{type(e).__name__}: {e}"}
        print(f"⚠️  Model artifacts in {d} could not be read ({type(e).__name__}: {e}). "
              f"Scoring uses the deterministic heuristic fallback. "
              f"Rebuild with: python train_model.py")
        return False

    # A cross-version pickle often loads and only fails on use. Prove it works.
    try:
        X = pd.DataFrame([_SMOKE_ROW])[FEATURES]
        rf.predict_proba(X)
        lr.predict_proba(scaler.transform(X))
    except Exception as e:
        _STATUS = {"available": False, "reason": "artifact_incompatible",
                   "detail": f"loaded but unusable — {type(e).__name__}: {e}",
                   "sklearn_runtime": _sklearn_version()}
        print(f"⚠️  Model artifacts in {d} loaded but cannot predict "
              f"({type(e).__name__}: {e}). This usually means they were built by a "
              f"different scikit-learn (runtime: {_sklearn_version()}). "
              f"Scoring uses the deterministic heuristic fallback. "
              f"Rebuild with: python train_model.py")
        return False

    _rf, _lr, _scaler = rf, lr, scaler
    _STATUS = {"available": True, "reason": None, "detail": None}
    return True


def score(data: dict) -> dict:
    """Run credit assessment. Returns full result dict."""
    features = {f: data.get(f, 0) for f in FEATURES}

    if _STATUS["available"] and _rf is not None and _lr is not None and _scaler is not None:
        X = pd.DataFrame([features])[FEATURES]
        pd_rf = float(_rf.predict_proba(X)[0][1])
        pd_lr = float(_lr.predict_proba(_scaler.transform(X))[0][1])
        scoring_path = "ensemble"
    else:
        scoring_path = "heuristic"
        # Heuristic fallback (no models)
        r = features
        pd_rf = (r['return_rate'] / 0.40) * 0.28 + ((5 - r['rating']) / 4) * 0.20 + (r['late_ship_rate'] / 0.40) * 0.18
        pd_rf = min(0.99, max(0.01, pd_rf))
        pd_lr = pd_rf

    pd_score = round(pd_rf * 0.65 + pd_lr * 0.35, 4)
    rev = features['monthly_revenue']

    if pd_score < 0.25:
        decision, tier, credit_limit, interest_rate = "APPROVED",    "Low Risk",    rev * 0.45, 12.5
    elif pd_score < 0.55:
        decision, tier, credit_limit, interest_rate = "CONDITIONAL", "Medium Risk", rev * 0.20, 18.0
    else:
        decision, tier, credit_limit, interest_rate = "REJECTED",    "High Risk",   0,          0.0

    def flag(val, lo, hi):
        return "green" if val <= lo else "amber" if val <= hi else "red"

    def flag_rev(val):
        return "green" if val >= 0.10 else "amber" if val >= 0 else "red"

    return {
        "pd_score":      pd_score,
        "pd_rf":         round(pd_rf, 4),
        "pd_lr":         round(pd_lr, 4),
        "decision":      decision,
        "risk_tier":     tier,
        # D-030: contractual money — integer đồng, ROUND_HALF_UP, not banker's.
        "credit_limit":  to_increment(credit_limit),
        "interest_rate": interest_rate,
        # Must reflect what actually produced the score. Reporting
        # "v1.0-synthetic" while the heuristic ran would be the same class of
        # defect as the withdrawn AUC: the artifact contradicting its label.
        "model_version": ENSEMBLE_VERSION if scoring_path == "ensemble" else HEURISTIC_VERSION,
        "scoring_path": scoring_path,
        "signals": {
            "return_rate":        {"value": features['return_rate'],        "flag": flag(features['return_rate'], 0.08, 0.15)},
            "late_ship_rate":     {"value": features['late_ship_rate'],     "flag": flag(features['late_ship_rate'], 0.06, 0.12)},
            "revenue_growth":     {"value": features['revenue_growth'],     "flag": flag_rev(features['revenue_growth'])},
            "rating":             {"value": features['rating'],             "flag": "green" if features['rating'] >= 4.5 else "amber" if features['rating'] >= 3.8 else "red"},
            "days_active":        {"value": features['days_active'],        "flag": "green" if features['days_active'] > 365 else "amber" if features['days_active'] > 180 else "red"},
            "inventory_turnover": {"value": features['inventory_turnover'], "flag": "green" if features['inventory_turnover'] > 4 else "amber" if features['inventory_turnover'] > 2 else "red"},
        },
        "reasoning": _build_reasoning(decision, features)
    }
