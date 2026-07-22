"""ILLUSTRATIVE demonstration of the retro-validation / learning loop.

WHAT THIS IS: a mechanism demo. It scores a cohort of merchants with the
real model, then SIMULATES repayment outcomes and runs the exact same
retro-validation the production loop runs on real outcomes. It shows the
wiring works and what the reported numbers look like.

WHAT THIS IS NOT: a real-world result. The outcomes here are simulated,
not observed. The AUC printed below is the model scored against SIMULATED
labels. Real validation requires lender-recorded outcomes via
POST /api/sellers/{id}/outcome, at which point GET /api/model/status
reports the genuine figure. Do not quote this number as accuracy.

Run:  python demo_learning_loop.py
"""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(__file__))

from ml_engine import score
from main import _auc


def realistic_cohort(n=120, seed=7):
    """A spread of plausible merchant profiles (not the polished seed set)."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        health = rng.random()  # latent quality 0..1, unknown to the model
        out.append({
            "monthly_revenue": rng.uniform(25, 500) * 1e6,
            "revenue_growth": rng.uniform(-0.25, 0.6) * (0.4 + health),
            "order_volume": rng.randint(60, 900),
            "avg_order_value": rng.uniform(150_000, 900_000),
            "return_rate": max(0.005, 0.20 * (1 - health) + rng.uniform(-0.03, 0.03)),
            "rating": min(5.0, 3.6 + 1.4 * health + rng.uniform(-0.2, 0.2)),
            "days_active": rng.randint(40, 1300),
            "inventory_turnover": rng.uniform(2, 10),
            "late_ship_rate": max(0.005, 0.18 * (1 - health) + rng.uniform(-0.02, 0.02)),
            "previous_loans": rng.randint(0, 4),
            "_latent_health": health,
        })
    return out


def simulate_outcome(profile, rng):
    """Outcome driven by latent health the model never sees, plus noise —
    so the model has REAL but IMPERFECT skill, like real life."""
    true_default_prob = (1 - profile["_latent_health"]) ** 1.8
    true_default_prob = min(0.95, max(0.02, true_default_prob + rng.uniform(-0.12, 0.12)))
    roll = rng.random()
    if roll < true_default_prob:
        return "defaulted"
    if roll < true_default_prob + 0.12:
        return "late"
    return "repaid"


def main():
    rng = random.Random(42)
    cohort = realistic_cohort()
    scores, labels = [], []
    for p in cohort:
        feats = {k: v for k, v in p.items() if not k.startswith("_")}
        pd = score(feats)["pd_score"]
        outcome = simulate_outcome(p, rng)
        scores.append(pd)
        labels.append(1 if outcome in ("defaulted", "late") else 0)

    bad = sum(labels)
    auc = _auc(scores, labels)

    print("=" * 68)
    print("  ILLUSTRATIVE LEARNING-LOOP DEMONSTRATION  (simulated outcomes)")
    print("=" * 68)
    print(f"  Cohort size:            {len(cohort)} merchants")
    print(f"  Simulated bad outcomes: {bad} ({bad/len(cohort):.0%}) [defaulted or late]")
    print(f"  Model rank AUC:         {auc}  <-- vs SIMULATED labels, not real")
    print(f"  Synthetic train AUC:    0.92   [held-out synthetic, for reference]")
    print("-" * 68)
    print("  Pipeline exercised: score cohort -> collect outcomes -> compute")
    print("  real-world AUC (Mann-Whitney U) -> gate retrain on holdout lift.")
    print("  This is the SAME code path /api/model/status runs on real")
    print("  outcomes. The number above is on SIMULATED data and must never")
    print("  be presented as RBF's accuracy.")
    print("=" * 68)


if __name__ == "__main__":
    main()
