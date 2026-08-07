import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rbf_sim.contracts import ContractTerms
from rbf_sim.engine import run_scenario, paired_delta, bootstrap_ci
from rbf_sim.generator import PathParams

N = int(sys.argv[1]); FP = "results/validation_v1.json"
p = PathParams(R0=185_000_000.0, T=24, shock="decline_sustained", shock_depth=0.40,
               seasonality="moderate", label="sustained_decline")
res = run_scenario(N, p, ContractTerms(A=185_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12))
b = bootstrap_ci(paired_delta(res, "n_high_burden", threshold=0.15), n_boot=2000)
r = bootstrap_ci(paired_delta(res, "recovery_ratio", k=12), n_boot=2000)
d = json.load(open(FP)) if os.path.exists(FP) else {}
d.setdefault("convergence", {})[str(N)] = {"d_n_hpb": b, "d_rr12": r}
json.dump(d, open(FP, "w"), indent=2, default=str)
print(f"N={N:>6}  d n_HPB(0.15) = {b['mean']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"
      f"   d RR(12) = {r['mean']*100:.3f}pp [{r['lo']*100:.3f},{r['hi']*100:.3f}]")
