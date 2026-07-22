"""Validate the RBF modeling METHODOLOGY on REAL public credit data.

WHAT THIS PROVES: the exact RF + LR ensemble RBF uses in production
(same hyperparameters as train_model.py) has genuine out-of-sample
predictive skill on REAL borrowers with REAL, adjudicated default
outcomes — reported as 5-fold cross-validated AUC.

WHAT THIS DOES NOT PROVE: that RBF's production *merchant* model is
validated. That model scores e-commerce features (revenue, growth,
returns, ratings, fulfillment) that no public credit dataset contains,
and it still awaits real merchant repayment outcomes — GET /api/model/status
reports that honestly and returns a null real-world figure until they exist.
This file validates the METHOD on real data, not the merchant model, and
must never be quoted as "RBF's accuracy on merchants".

Datasets (real, public, citable; bundled under validation_data/):
- UCI Statlog German Credit — 1,000 real loan applicants, good/bad outcome.
- UCI 'Default of Credit Card Clients' (Taiwan) — 30,000 real accounts,
  default-payment-next-month outcome.

Run:  python validate_on_real_data.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

DATA = os.path.join(os.path.dirname(__file__), "validation_data")


def rbf_ensemble_cv(X, y, n_splits=5, seed=42):
    """RBF's production ensemble (train_model.py), cross-validated for an
    honest out-of-sample AUC: RF (300 trees, depth 8) blended 0.65 with
    a StandardScaler->LogisticRegression at 0.35, class-weight balanced."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    aucs = {"rf": [], "lr": [], "ensemble": []}
    for tr, te in skf.split(X, y):
        Xtr, Xte, ytr, yte = X[tr], X[te], y[tr], y[te]

        rf = RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=10,
            class_weight="balanced", random_state=seed)
        rf.fit(Xtr, ytr)
        p_rf = rf.predict_proba(Xte)[:, 1]

        scaler = StandardScaler().fit(Xtr)
        lr = LogisticRegression(max_iter=1000, class_weight="balanced")
        lr.fit(scaler.transform(Xtr), ytr)
        p_lr = lr.predict_proba(scaler.transform(Xte))[:, 1]

        p_ens = 0.65 * p_rf + 0.35 * p_lr
        aucs["rf"].append(roc_auc_score(yte, p_rf))
        aucs["lr"].append(roc_auc_score(yte, p_lr))
        aucs["ensemble"].append(roc_auc_score(yte, p_ens))
    return {k: (float(np.mean(v)), float(np.std(v))) for k, v in aucs.items()}


def load_german():
    df = pd.read_csv(os.path.join(DATA, "german.data-numeric"),
                     sep=r"\s+", header=None)
    X = df.iloc[:, :24].values
    y = (df.iloc[:, 24].values == 2).astype(int)  # 2 = bad credit -> 1
    return X, y, "UCI Statlog German Credit  (1,000 real applicants)"


def load_taiwan():
    df = pd.read_csv(os.path.join(DATA, "taiwan.csv"))
    y = df["default payment next month"].astype(int).values
    X = df.drop(columns=["ID", "default payment next month"]).values
    return X, y, "UCI Taiwan credit-card default  (30,000 real accounts)"


def report(name, X, y):
    r = rbf_ensemble_cv(X, y)
    bad, n = int(np.sum(y)), len(y)
    print(f"\n  {name}")
    print(f"    real bad-outcome rate : {bad}/{n} = {bad/n:.1%}")
    print(f"    RF-only   AUC : {r['rf'][0]:.4f} +/- {r['rf'][1]:.4f}")
    print(f"    LR-only   AUC : {r['lr'][0]:.4f} +/- {r['lr'][1]:.4f}")
    print(f"    ENSEMBLE  AUC : {r['ensemble'][0]:.4f} +/- {r['ensemble'][1]:.4f}"
          f"   (5-fold, out-of-sample)")
    return r["ensemble"][0]


def main():
    print("=" * 72)
    print("  RBF MODELING METHODOLOGY  --  VALIDATED ON REAL PUBLIC CREDIT DATA")
    print("=" * 72)
    print("  Same RF+LR ensemble as production (train_model.py). 5-fold CV.")
    print("  REAL borrowers. REAL, adjudicated default outcomes.")

    results = []
    for loader in (load_german, load_taiwan):
        X, y, name = loader()
        results.append((name, report(name, X, y)))

    print("\n" + "-" * 72)
    print("  Reads as: the RBF approach separates real defaulters from real")
    print("  non-defaulters well above chance (0.50) on two independent real")
    print("  credit datasets. That is genuine, out-of-sample skill on real data.")
    print("  It does NOT validate the production MERCHANT model (different")
    print("  features, no merchant outcomes yet -- see /api/model/status).")
    print("=" * 72)


if __name__ == "__main__":
    main()
