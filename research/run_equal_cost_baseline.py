"""Baseline at the EQUAL-EFFECTIVE-COST cap factor f* = 1.0945 (D-031).

    python3 run_equal_cost_baseline.py     # -> results/baseline_equalcost_v1_canonical.json

WHY THIS RUN EXISTS. `baseline_v2` runs every scenario at the **illustrative**
cap factor f = 1.20. The equal-effective-cost factor f* = 1.0945 — the price at
which the RBF contract costs the seller about the same as the 18%-nominal
amortizing benchmark — exists only as a *pricing* result computed on the single
deterministic reference path (`validation_v1.pricing.equal_cost`).

Presenting seller burden and provider recovery for the equal-cost arm therefore
had no artifact to draw on. Charting the reference-path pricing number beside
500-path scenario aggregates would compare two different objects, which is
exactly the error this project exists to avoid. This run produces the missing
one: the same ten scenarios, the same seeds, the same generator, priced at f*.

WHAT IS AND IS NOT NEW. Nothing in the model changes. `rbf_sim` is untouched;
`run_baseline.py` is untouched (its bytes are inside `baseline_v2`'s generator
fingerprint, so editing it would invalidate a registered checksum). The scenario
list, path count and base seed are imported from `run_baseline` rather than
retyped, so the two runs cannot silently diverge. The single difference is the
contract's cap factor — which spec §12 already anticipates as a swept
parameter, and which D-015 established as separable from contract structure.

D-018 stands: RBF-G is a rejected design and is not promoted. It is computed
here only because the engine runs all four arms together; it is excluded from
public comparison surfaces.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbf_sim.canonical import write_canonical_pair
from rbf_sim.contracts import ContractTerms
from rbf_sim.engine import run_scenario
from rbf_sim.generator import PathParams

# Imported, never retyped: the two baselines must share scenarios and seeds.
from run_baseline import N_PATHS, R0, SCENARIOS, TERMS as BASE_TERMS

#: The equal-effective-cost cap factor, from validation_v1.pricing.equal_cost.
#: Not a recommendation — the price at which RBF's effective APR matches
#: Benchmark B's 19.5618%.
F_STAR = 1.0945

BASE_SEED = 20260803

TERMS = ContractTerms(A=BASE_TERMS.A, r=BASE_TERMS.r, f=F_STAR,
                      j=BASE_TERMS.j, N_B=BASE_TERMS.N_B)

W = 78


def main() -> None:
    print("=" * W)
    print("  EQUAL-EFFECTIVE-COST BASELINE  (f* = 1.0945)")
    print("  Simulation output under METHODOLOGY_SPEC.md v1.0 + A-1..A-7")
    print("=" * W)
    print(f"  R0={R0:,.0f} VND | A={TERMS.A:,.0f} | r={TERMS.r} | f={TERMS.f} "
          f"| cap={TERMS.cap:,.0f}")
    print(f"  paths/scenario {N_PATHS} | base seed {BASE_SEED}")
    print("\n  *** ALL FIGURES ARE SIMULATED. NO OBSERVED SELLER DATA. ***\n")

    results = {}
    for name, over in SCENARIOS:
        p = PathParams(R0=R0, T=24, label=name,
                       **{**dict(seasonality="moderate", growth=0.0), **over})
        results[name] = run_scenario(N_PATHS, p, TERMS, base_seed=BASE_SEED)
        print(f"  ran {name}")

    m = results["stable"]["match"]
    print(f"\n  matched benchmark: term {m['term']} months | "
          f"payment {m['payment']:,.0f} VND | APR {m['apr']:.2%}")

    payload = {
        "run": "baseline_equalcost_v1",
        "spec": "METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-7",
        "provenance": "SIMULATED — no observed seller data",
        "purpose": "Seller burden and provider recovery at the equal-effective-cost "
                   "cap factor f* = 1.0945, for like-for-like comparison against "
                   "baseline_v2 (illustrative f = 1.20). Same scenarios, same "
                   "seeds, same generator; only the cap factor differs.",
        "n_paths": N_PATHS, "base_seed": BASE_SEED,
        "f_star_source": "validation_v1.pricing.equal_cost.f_star",
        "terms": {"A": TERMS.A, "r": TERMS.r, "f": TERMS.f, "cap": TERMS.cap,
                  "j": TERMS.j, "N_B": TERMS.N_B},
        "match_benchmark_a": m,
        "scenarios": {k: v["arms"] for k, v in results.items()},
    }

    written = write_canonical_pair(
        payload,
        stem="baseline_equalcost_v1",
        scenario_config={"scenarios": SCENARIOS, "n_paths": N_PATHS,
                         "base_seed": BASE_SEED,
                         "terms": {"A": TERMS.A, "r": TERMS.r, "f": TERMS.f,
                                   "j": TERMS.j, "N_B": TERMS.N_B}},
        spec_version="METHODOLOGY_SPEC.md v1.0 (frozen 2026-08-03) + A-1..A-7",
        extra_sources=("run_equal_cost_baseline.py",),
    )
    print("\n" + "=" * W)
    print("  Written: results/baseline_equalcost_v1_canonical.json")
    print("           results/baseline_equalcost_v1_provenance.json")
    print(f"  SHA-256: {written['sha256']}")
    print("=" * W)


if __name__ == "__main__":
    main()
