"""Phase 0 audit evidence — reproducible measurements behind PHASE0_AUDIT.md §4.

Place at:  sellerflow/research/analysis/00_audit_evidence.py
Run from:  sellerflow/backend/   (needs generate_data.py + integrity_engine.py on path)

    cd backend && python3 ../research/analysis/00_audit_evidence.py

Establishes three findings about the project's own synthetic baseline. All are
properties of committed code, not opinions — each prints a number a third party
can reproduce.

  RI-1  The 0.92 AUC is circular: the label is a hand-written function of the
        same features the model consumes, so the metric measures the chosen
        noise variance rather than predictive skill.
  RI-2  The synthetic population is internally impossible: features are drawn
        independently, violating the identity revenue = orders x AOV.
  RI-3  The project's own integrity engine flags the majority of the population
        its credit model was trained on.

Author: Phase 0 audit, 2026-08-03
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backend"))

from generate_data import generate_seller_data  # noqa: E402
from integrity_engine import screen_integrity   # noqa: E402

FEATURES = [
    "monthly_revenue", "revenue_growth", "order_volume", "avg_order_value",
    "return_rate", "rating", "days_active", "inventory_turnover",
    "late_ship_rate", "previous_loans",
]

# Reported by train_model.py at audit time; re-run it to confirm.
REPORTED_ENSEMBLE_AUC = 0.9182

RULE = "=" * 74


def generating_function(df: pd.DataFrame) -> pd.Series:
    """The exact risk_score expression from generate_data.py, recomputed here.

    Kept verbatim rather than imported, so this file stands alone as evidence
    of what the label-generating process actually is.
    """
    return (
        0.28 * (df["return_rate"] / df["return_rate"].max())
        + 0.22 * (1 - (df["rating"] - 1) / 4)
        + 0.18 * (df["late_ship_rate"] / df["late_ship_rate"].max())
        + 0.15 * (1 - df["revenue_growth"].clip(-0.35, 0.90).add(0.35) / 1.25)
        + 0.10 * (1 - df["days_active"] / 1800)
        + 0.07 * (1 - df["inventory_turnover"] / 14)
    )


def ri1_circularity(df: pd.DataFrame) -> dict:
    """Is the benchmark measuring skill, or measuring the author's noise term?"""
    print("\nRI-1  CIRCULARITY OF THE SYNTHETIC BENCHMARK")
    print("-" * 74)
    score = generating_function(df)
    auc_dgp = roc_auc_score(df["defaulted"], score)
    print(f"  label prevalence                          : {df['defaulted'].mean():>7.2%}")
    print(f"  AUC of the hand-written generating fn     : {auc_dgp:>7.4f}")
    print(f"  reported ensemble AUC (train_model.py)    : {REPORTED_ENSEMBLE_AUC:>7.4f}")
    print()
    print("  The label is generating_function(X) + N(0, 0.08), thresholded at 0.475.")
    print("  The generating function is therefore the Bayes-optimal ranker for this")
    print("  data, and it scores what the model scores. The reported AUC is a")
    print("  measurement of sigma=0.08 -- an author's choice -- not of any property")
    print("  of e-commerce sellers, credit risk, or the model.")
    return {"auc_generating_function": round(float(auc_dgp), 4),
            "auc_reported_model": REPORTED_ENSEMBLE_AUC,
            "label_prevalence": round(float(df["defaulted"].mean()), 4)}


def ri2_impossible_population(df: pd.DataFrame) -> dict:
    """Do the synthetic sellers satisfy the accounting identity they must?"""
    print("\n\nRI-2  THE SYNTHETIC POPULATION IS INTERNALLY IMPOSSIBLE")
    print("-" * 74)
    corr = df[FEATURES].corr().abs().values.copy()
    np.fill_diagonal(corr, 0.0)
    max_corr = float(corr.max())

    ratio = df["monthly_revenue"] / (df["order_volume"] * df["avg_order_value"])
    # [0.55, 1.75] is integrity_engine.revenue_reconciliation()'s own pass band.
    outside = float(((ratio < 0.55) | (ratio > 1.75)).mean())

    print(f"  max |pairwise correlation| among 10 features : {max_corr:>7.4f}")
    print(f"  median  revenue / (orders x AOV)             : {ratio.median():>7.2f}   (must be ~1.00)")
    print(f"  share of rows outside the [0.55, 1.75] band  : {outside:>7.1%}")
    print()
    print("  Near-zero correlation means every feature was drawn independently.")
    print("  But revenue = orders x AOV is an accounting identity, not a tendency.")
    print("  It is violated in the majority of rows, so no real seller could be")
    print("  drawn from this distribution. Consequence: the model's reported")
    print("  feature_importance describes the generating formula's own weights and")
    print("  must never be presented as a finding about sellers.")
    return {"max_abs_pairwise_correlation": round(max_corr, 4),
            "median_revenue_over_orders_x_aov": round(float(ratio.median()), 4),
            "share_outside_reconciliation_band": round(outside, 4)}


def ri3_engines_disagree(df: pd.DataFrame, n: int = 1000) -> dict:
    """Would the fraud screen accept the population the credit model was fit on?"""
    print("\n\nRI-3  THE INTEGRITY ENGINE REJECTS ITS OWN TRAINING DATA")
    print("-" * 74)
    statuses = []
    for _, row in df.head(n).iterrows():
        result = screen_integrity({f: row[f] for f in FEATURES})
        checks = result.get("checks", result) if isinstance(result, dict) else result
        match = [c for c in checks if c.get("check") == "Revenue reconciliation"]
        statuses.append(match[0]["status"] if match else "unknown")

    counts = pd.Series(statuses).value_counts(normalize=True)
    flag = float(counts.get("flag", 0.0))
    print(f"  revenue-reconciliation over {n:,} training rows")
    print(f"    flag : {flag:>7.1%}")
    print(f"    pass : {float(counts.get('pass', 0.0)):>7.1%}")
    print()
    print("  The project's own fraud screen would reject the majority of the")
    print("  population its credit model was trained on. The two engines encode")
    print("  contradictory beliefs about what a seller looks like.")
    print()
    print("  Reframed, this is the strongest honest result available: a concrete,")
    print("  reproducible demonstration that synthetic underwriting data can")
    print("  silently violate the accounting identities downstream fraud controls")
    print("  depend on -- and that neither component detects the conflict.")
    return {"n_rows_screened": n, "revenue_reconciliation_flag_rate": round(flag, 4)}


def main() -> None:
    print(RULE)
    print("  RBF PROJECT -- PHASE 0 AUDIT EVIDENCE")
    print("  Measurements behind PHASE0_AUDIT.md section 4 (research-integrity risks)")
    print(RULE)

    df = generate_seller_data()  # seed=42, fixed in generate_data.py
    print(f"\n  synthetic cohort: n={len(df):,}  (generate_data.py, seed=42)")

    results = {}
    results.update(ri1_circularity(df))
    results.update(ri2_impossible_population(df))
    results.update(ri3_engines_disagree(df))

    print("\n" + RULE)
    print("  MACHINE-READABLE SUMMARY")
    print(RULE)
    for k, v in results.items():
        print(f"  {k:<38} {v}")
    print(RULE)
    print("  These findings concern the SYNTHETIC BASELINE ONLY. They do not")
    print("  invalidate financing_engine.py, whose arithmetic is independently")
    print("  unit-tested and requires no labels. See PHASE0_AUDIT.md section 2.")
    print(RULE)


if __name__ == "__main__":
    main()
