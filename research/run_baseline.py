"""First reproducible baseline run — METHODOLOGY_SPEC.md v1.0.

    python3 run_baseline.py            # prints report, writes results/baseline_v3_canonical.json

Every number is a SIMULATION output under stated assumptions. No observed
seller outcome appears anywhere. See spec section 15 for binding interpretation
limits.
"""
import json

from rbf_sim.canonical import write_canonical_pair
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbf_sim.contracts import ContractTerms
from rbf_sim.engine import run_scenario, paired_delta, bootstrap_ci
from rbf_sim.generator import PathParams
from rbf_sim.metrics import THRESHOLDS, CHECKPOINTS

N_PATHS = 500
R0 = 185_000_000.0
TERMS = ContractTerms(A=185_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)

SCENARIOS = [
    ("stable",            dict(shock="none", seasonality="flat",     growth=0.0)),
    ("seasonal",          dict(shock="none", seasonality="moderate", growth=0.0)),
    ("seasonal_strong",   dict(shock="none", seasonality="strong",   growth=0.0)),
    ("growth",            dict(shock="none", seasonality="moderate", growth=0.03)),
    ("gradual_decline",   dict(shock="decline_gradual",   shock_depth=0.40)),
    ("sustained_decline", dict(shock="decline_sustained", shock_depth=0.40)),
    ("severe_downturn",   dict(shock="downturn_multi",    shock_depth=0.60)),
    ("disruption_1m",     dict(shock="disruption_1m",     shock_depth=0.50)),
    ("platform_outage",   dict(shock="platform_outage")),
    ("returns_spike",     dict(shock="returns_spike")),
]

W = 78


def hdr(t):
    print("\n" + "=" * W); print(f"  {t}"); print("=" * W)


def fmt(x, nd=2, pct=False):
    if x is None:
        return "  n/a"
    return f"{x*100:.{nd}f}%" if pct else f"{x:,.{nd}f}"


def main():
    print("=" * W)
    print("  FINANCING VOLATILE REVENUE - BASELINE RUN v1.0")
    print("  Simulation output under METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03)")
    print(f"  Run date {date.today()} | paths/scenario {N_PATHS} | base seed 20260803")
    print("=" * W)
    print(f"  R0={R0:,.0f} VND | A={TERMS.A:,.0f} | r={TERMS.r} | f={TERMS.f} "
          f"| cap={TERMS.cap:,.0f}")
    print(f"  Benchmark B: amortizing, j={TERMS.j:.0%} nominal, N_B={TERMS.N_B} months")
    print("\n  *** ALL FIGURES ARE SIMULATED. NO OBSERVED SELLER DATA. ***")

    results = {}
    for name, over in SCENARIOS:
        p = PathParams(R0=R0, T=24, label=name,
                       **{**dict(seasonality="moderate", growth=0.0), **over})
        results[name] = run_scenario(N_PATHS, p, TERMS)

    m = results["stable"]["match"]
    hdr("BENCHMARK A MATCHING (spec 7.1) - computed once on the reference path")
    print(f"  RBF base-case duration N       : {m['term']} months")
    print(f"  matched fixed payment P        : {m['payment']:,.0f} VND/month")
    print(f"  matched total repayment        : {m['total']:,.0f} VND  (= cap)")
    print(f"  implied APR (solved, reported) : {m['apr']:.2%}")
    print("  -> principal, total repayment and term all identical to RBF on the")
    print("     reference path. Only payment TIMING differs.")

    # ── payment burden ────────────────────────────────────────────────────────
    hdr("1. PAYMENT BURDEN  (spec 10.1)  - mean over paths")
    print(f"  {'scenario':<19}{'arm':<8}{'mean':>9}{'max':>9}{'p90':>9}{'p95':>9}")
    print("  " + "-" * (W - 4))
    for name in ("stable", "seasonal_strong", "sustained_decline", "severe_downturn"):
        for arm in ("FIX-A", "FIX-B", "RBF", "RBF-G"):
            a = results[name]["arms"][arm]
            print(f"  {name if arm=='FIX-A' else '':<19}{arm:<8}"
                  f"{fmt(a['burden_mean'],1,True):>9}{fmt(a['burden_max'],1,True):>9}"
                  f"{fmt(a['burden_p90'],1,True):>9}{fmt(a['burden_p95'],1,True):>9}")
        print()

    # ── high-burden months ────────────────────────────────────────────────────
    hdr("2. HIGH-PAYMENT-BURDEN MONTHS  (spec 10.2)  - mean count per path")
    print("  NOTE: RBF burden is constant at r by construction. Direction is")
    print("  definitional; the information is on the FIXED side.\n")
    print(f"  {'scenario':<19}{'arm':<8}" + "".join(f"{'th='+str(t):>9}" for t in THRESHOLDS))
    print("  " + "-" * (W - 4))
    for name, _ in SCENARIOS:
        for arm in ("FIX-A", "RBF"):
            a = results[name]["arms"][arm]
            print(f"  {name if arm=='FIX-A' else '':<19}{arm:<8}"
                  + "".join(f"{a['n_high_burden'][t]:>9.2f}" for t in THRESHOLDS))
        print()

    # ── duration / repayment ──────────────────────────────────────────────────
    hdr("3. DURATION AND TOTAL REPAID  (spec 10.4, 10.5)")
    print(f"  {'scenario':<19}{'arm':<8}{'dur_mean':>10}{'dur_sd':>8}"
          f"{'censored':>10}{'repaid':>16}{'mult':>7}")
    print("  " + "-" * (W - 4))
    for name, _ in SCENARIOS:
        for arm in ("FIX-A", "RBF", "RBF-G"):
            a = results[name]["arms"][arm]
            print(f"  {name if arm=='FIX-A' else '':<19}{arm:<8}"
                  f"{fmt(a['duration_mean'],1):>10}{fmt(a['duration_sd'],2):>8}"
                  f"{fmt(a['duration_censored_rate'],0,True):>10}"
                  f"{a['total_repaid_mean']:>16,.0f}{a['multiple_mean']:>7.3f}")
        print()

    # ── provider recovery ─────────────────────────────────────────────────────
    hdr("4. PROVIDER RECOVERY  (spec 10.6, 10.7, 10.8)")
    print(f"  {'scenario':<19}{'arm':<8}" + "".join(f"{'RR('+str(k)+')':>10}" for k in CHECKPOINTS)
          + f"{'incompl':>10}{'postshk6':>14}")
    print("  " + "-" * (W - 4))
    for name, _ in SCENARIOS:
        for arm in ("FIX-A", "RBF"):
            a = results[name]["arms"][arm]
            print(f"  {name if arm=='FIX-A' else '':<19}{arm:<8}"
                  + "".join(f"{fmt(a['recovery_ratio'][k],1,True):>10}" for k in CHECKPOINTS)
                  + f"{fmt(a['incomplete_recovery_rate'],1,True):>10}"
                  + f"{a['post_shock_recovery'][6]:>14,.0f}")
        print()

    # ── underreporting ────────────────────────────────────────────────────────
    hdr("5. UNDERREPORTING SENSITIVITY  (spec 10.9)")
    print("  FIX-A and FIX-B are invariant to omega by construction: a fixed")
    print("  payment never reads revenue, so it cannot be diverted from.\n")
    print(f"  {'omega':<8}{'RBF dur':>10}{'RR(12)':>10}{'RR(24)':>10}"
          f"{'incompl':>10}{'repaid':>16}")
    print("  " + "-" * (W - 4))
    p_ur = PathParams(R0=R0, T=24, label="underreport", shock="none", seasonality="moderate")
    ur = {}
    for w in (1.00, 0.95, 0.90, 0.80, 0.70):
        r = run_scenario(N_PATHS, p_ur, TERMS, omega=w)
        a = r["arms"]["RBF"]
        ur[w] = a
        print(f"  {w:<8.2f}{fmt(a['duration_mean'],1):>10}"
              f"{fmt(a['recovery_ratio'][12],1,True):>10}{fmt(a['recovery_ratio'][24],1,True):>10}"
              f"{fmt(a['incomplete_recovery_rate'],1,True):>10}"
              f"{a['total_repaid_mean']:>16,.0f}")
    fa = run_scenario(N_PATHS, p_ur, TERMS)["arms"]["FIX-A"]
    print(f"  {'FIX-A':<8}{fmt(fa['duration_mean'],1):>10}"
          f"{fmt(fa['recovery_ratio'][12],1,True):>10}{fmt(fa['recovery_ratio'][24],1,True):>10}"
          f"{fmt(fa['incomplete_recovery_rate'],1,True):>10}"
          f"{fa['total_repaid_mean']:>16,.0f}   (invariant)")

    # ── flexibility / recovery trade-off ──────────────────────────────────────
    hdr("6. SELLER FLEXIBILITY vs PROVIDER RECOVERY  (spec 10.10)")
    print("  Paired within-path differences, FIX-A minus RBF.")
    print("  Intervals = MONTE CARLO PRECISION ONLY, not uncertainty about real")
    print("  sellers (spec 15 rule 4). More paths narrow them without adding facts.\n")
    print(f"  {'scenario':<19}{'seller: d n_HPB(0.15)':>26}{'provider: d RR(12)':>24}")
    print("  " + "-" * (W - 4))
    tradeoff = {}
    for name, _ in SCENARIOS:
        d_b = paired_delta(results[name], "n_high_burden", threshold=0.15)
        d_r = paired_delta(results[name], "recovery_ratio", k=12)
        cb, cr = bootstrap_ci(d_b), bootstrap_ci(d_r)
        tradeoff[name] = {"d_n_hpb_015": cb, "d_rr12": cr}
        print(f"  {name:<19}{cb['mean']:>10.2f} [{cb['lo']:>5.2f},{cb['hi']:>5.2f}]"
              f"{cr['mean']*100:>13.1f}pp [{cr['lo']*100:>5.1f},{cr['hi']*100:>5.1f}]")
    print("\n  Positive seller column = RBF gives fewer high-burden months.")
    print("  Positive provider column = fixed recovers more capital by month 12.")

    # ── persist ───────────────────────────────────────────────────────────────
    # D-027: `results/baseline_v2.json` is FROZEN historical evidence and is no
    # longer written by this script. Its numbers are identical to the canonical
    # artifact below; it differs only by carrying an embedded wall-clock date,
    # which is what made it un-checksummable. It is preserved, not rewritten.
    os.makedirs("results", exist_ok=True)
    payload = {
        "run": "baseline_v3",
        # Must match canonical.spec_version exactly. These drifted apart in
        # the first A-9 generation: this field still read "v1.0" with no
        # amendments while the canonical block said A-1..A-9, so an artifact
        # disagreed with itself about which specification produced it.
        "spec": "METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-9",
        "provenance": "SIMULATED — no observed seller data",
        "n_paths": N_PATHS, "base_seed": 20260803,
        "terms": {"A": TERMS.A, "r": TERMS.r, "f": TERMS.f, "cap": TERMS.cap,
                  "j": TERMS.j, "N_B": TERMS.N_B},
        "match_benchmark_a": m,
        "scenarios": {k: v["arms"] for k, v in results.items()},
        "underreporting": {str(k): v for k, v in ur.items()},
        "tradeoff": tradeoff,
    }
    written = write_canonical_pair(
        payload,
        stem="baseline_v3",
        scenario_config={"scenarios": SCENARIOS, "n_paths": N_PATHS,
                         "base_seed": 20260803,
                         "terms": {"A": TERMS.A, "r": TERMS.r, "f": TERMS.f,
                                   "j": TERMS.j, "N_B": TERMS.N_B}},
        spec_version="METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-9",
        extra_sources=("run_baseline.py",),
    )
    print("\n" + "=" * W)
    print("  Written: results/baseline_v3_canonical.json")
    print("           results/baseline_v3_provenance.json")
    print(f"  SHA-256: {written['sha256']}")
    print("  Reproduce: python3 run_baseline.py  — identical code, config and")
    print("             seeds reproduce it NUMERICALLY at published precision")
    print("             on every platform tested. BYTE equality holds within a")
    print("             fixed runtime and is not claimed across platforms (D-041).")
    print("  Note:    results/baseline_v2.json is frozen historical evidence")
    print("           (same numbers, embedded run date) and is not rewritten.")
    print("=" * W)


if __name__ == "__main__":
    main()
