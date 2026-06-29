import os, joblib, pandas as pd
from database import _build_reasoning

BASE = os.path.dirname(__file__)
FEATURES = [
    'monthly_revenue', 'revenue_growth', 'order_volume', 'avg_order_value',
    'return_rate', 'rating', 'days_active', 'inventory_turnover',
    'late_ship_rate', 'previous_loans'
]

_rf = _lr = _scaler = None


def load_models():
    global _rf, _lr, _scaler
    try:
        _rf     = joblib.load(f"{BASE}/models/rf_model.pkl")
        _lr     = joblib.load(f"{BASE}/models/lr_model.pkl")
        _scaler = joblib.load(f"{BASE}/models/scaler.pkl")
        return True
    except Exception as e:
        print(f"⚠️  Models not loaded: {e}. Using heuristic fallback.")
        return False


def score(data: dict) -> dict:
    """Run credit assessment. Returns full result dict."""
    features = {f: data.get(f, 0) for f in FEATURES}

    if _rf and _lr and _scaler:
        X = pd.DataFrame([features])
        pd_rf = float(_rf.predict_proba(X)[0][1])
        pd_lr = float(_lr.predict_proba(_scaler.transform(X))[0][1])
    else:
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
        "credit_limit":  round(credit_limit, -3),  # Round to nearest 1000 VND
        "interest_rate": interest_rate,
        "model_version": "v1.0-synthetic",
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
