"""Closure / zero-revenue baselines, at both registered cap factors (D-032).

    python3 run_closure_baseline.py

WHY THIS RUN EXISTS. `baseline_v2` and `baseline_equalcost_v1` contain ten
scenarios, none of which reaches zero revenue. Closure appears in the project
only inside `validation_v1.recovery_boundary`, as single-probe boundary search
output — not as a full scenario with seller-burden and provider-recovery
aggregates.

That gap is not neutral. Every scenario currently exposed in the Simulation Lab
repays the contract in full, so a reader could reasonably conclude that
revenue-based financing always recovers. It does not. Closure is the case where
incomplete recovery is real, and showing only the cases that repay would be the
misleading version of this study. `DERIVATIONS.md` P7a already establishes
closure as absorbing; this run supplies the matching empirical panel.

METHOD. Identical to the other baselines: same generator, same 500 paths, same
base seed, same aggregation. Two shock types the generator already implements
(spec amendment A-2) and the frozen spec already defines:

    closure_m7    permanent closure from month 7   — early, most of the term lost
    closure_m13   permanent closure from month 13  — later, after partial recovery
    temp_closure  three months at zero, then partial recovery to 50%

The fixed benchmark is unaffected by the shock, because `reference_base_path`
is flat R0 with no trend, seasonality, shock or noise (spec 7.1). A contract is
priced at origination; a closure that happens in month 7 cannot retro-price it.
That is what makes the paired comparison valid rather than circular.

`run_baseline.py` and `run_equal_cost_baseline.py` are NOT edited — their bytes
sit inside their own artifacts' generator fingerprints. Shared constants are
imported, never retyped.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbf_sim.canonical import write_canonical_pair
from rbf_sim.contracts import ContractTerms
from rbf_sim.engine import run_scenario
from rbf_sim.generator import PathParams

from run_baseline import N_PATHS, R0, TERMS as BASE_TERMS
from run_equal_cost_baseline import F_STAR

BASE_SEED = 20260803

CLOSURE_SCENARIOS = [
    ("closure_m7",   dict(shock="closure", shock_onset=7)),
    ("closure_m13",  dict(shock="closure", shock_onset=13)),
    ("temp_closure", dict(shock="temporary_closure", shock_depth=0.50, shock_onset=7)),
]

TRACKS = [
    ("baseline_closure_v2", BASE_TERMS.f,
     "Illustrative pricing, f = 1.20 — closure / zero-revenue scenarios"),
    ("baseline_closure_equalcost_v2", F_STAR,
     "Reference-path cost-matched pricing, f* = 1.0945 — closure / zero-revenue scenarios"),
]

W = 78


def main() -> None:
    for stem, f, role in TRACKS:
        terms = ContractTerms(A=BASE_TERMS.A, r=BASE_TERMS.r, f=f,
                              j=BASE_TERMS.j, N_B=BASE_TERMS.N_B)
        print("=" * W)
        print(f"  {role}")
        print("=" * W)
        print(f"  A={terms.A:,.0f} | r={terms.r} | f={terms.f} | cap={terms.cap:,.0f}")
        print(f"  paths/scenario {N_PATHS} | base seed {BASE_SEED}")
        print("\n  *** ALL FIGURES ARE SIMULATED. NO OBSERVED SELLER DATA. ***\n")

        results = {}
        for name, over in CLOSURE_SCENARIOS:
            p = PathParams(R0=R0, T=24, label=name,
                           **{**dict(seasonality="moderate", growth=0.0), **over})
            results[name] = run_scenario(N_PATHS, p, terms, base_seed=BASE_SEED)
            rbf = results[name]["arms"]["RBF"]
            print(f"  {name:14} RBF incomplete recovery "
                  f"{rbf['incomplete_recovery_rate']:.1%} | RR(24) "
                  f"{rbf['recovery_ratio'][24]:.1%}")

        payload = {
            "run": stem,
            "spec": "METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-7",
            "provenance": "SIMULATED — no observed seller data",
            "purpose": "Closure and zero-revenue scenarios. These are the cases "
                       "where incomplete recovery is real; the ten scenarios in "
                       "the other baselines all repay in full.",
            "n_paths": N_PATHS, "base_seed": BASE_SEED,
            "terms": {"A": terms.A, "r": terms.r, "f": terms.f, "cap": terms.cap,
                      "j": terms.j, "N_B": terms.N_B},
            "match_benchmark_a": results["closure_m7"]["match"],
            "scenarios": {k: v["arms"] for k, v in results.items()},
        }

        written = write_canonical_pair(
            payload,
            stem=stem,
            scenario_config={"scenarios": CLOSURE_SCENARIOS, "n_paths": N_PATHS,
                             "base_seed": BASE_SEED,
                             "terms": {"A": terms.A, "r": terms.r, "f": terms.f,
                                       "j": terms.j, "N_B": terms.N_B}},
            spec_version="METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-9",
            extra_sources=("run_closure_baseline.py",),
        )
        print(f"\n  Written: results/{stem}_canonical.json")
        print(f"  SHA-256: {written['sha256']}\n")


if __name__ == "__main__":
    main()
