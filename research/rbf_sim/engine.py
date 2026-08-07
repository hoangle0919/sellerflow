"""Paired comparison engine — METHODOLOGY_SPEC.md sections 9, 10.

One revenue path is generated once and consumed by all four contracts.
Comparisons are within-path paired differences only (spec 2, 9).
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import statistics

from . import contracts as K
from . import metrics as M
from .generator import PathParams, SellerPath, generate_cohort, reference_base_path

ARMS = ("FIX-A", "FIX-B", "RBF", "RBF-G")


@dataclass
class ArmResult:
    arm: str
    burden: Dict
    n_high_burden: Dict
    duration: Optional[int]
    censored: bool
    total_repaid: float
    total_cost: float
    multiple: float
    recovery_ratio: Dict
    recovery_abs: Dict
    incomplete_recovery: int
    post_shock_recovery: Dict
    apr: Optional[float]


def run_path(path: SellerPath, terms: K.ContractTerms, match: Dict,
             omega: float = 1.0) -> Dict[str, ArmResult]:
    """Apply all four contracts to ONE path (spec 9, rule 1)."""
    R, T, cap = path.revenue, path.params.T, terms.cap   # R = gmv, burden denominator
    B = path.remittance_base(terms.remittance_basis)      # contractual base (A-1)
    onset = path.params.shock_onset

    pay = {
        "FIX-A": K.fix_a_payments(terms, match, T),
        "FIX-B": K.fix_b_payments(terms, T),
        "RBF":   K.rbf_payments(B, terms, omega),
        "RBF-G": K.rbf_g_payments(B, terms, path.params.R0, omega),
    }

    out = {}
    for arm, p in pay.items():
        # FIX-B is not cost-matched, so its own total is the correct denominator
        target = sum(p) if arm == "FIX-B" else cap
        dur = M.duration(p, target)
        out[arm] = ArmResult(
            arm=arm,
            burden=M.burden_stats(R, p),
            n_high_burden=M.n_high_burden(R, p),
            duration=dur,
            censored=dur is None,
            total_repaid=M.total_repaid(p),
            total_cost=M.total_repaid(p) - terms.A,
            multiple=M.total_repaid(p) / terms.A,
            recovery_ratio=M.recovery_ratios(p, target),
            recovery_abs={k: M.recovery_at(p, k) for k in M.CHECKPOINTS},
            incomplete_recovery=M.incomplete_recovery(p, target),
            post_shock_recovery={k: M.post_shock_recovery(p, onset, k) for k in (6, 12)},
            apr=K.solve_apr(terms.A, [x for x in p if x > 0]),
        )
    return out


def run_scenario(n_paths: int, params: PathParams, terms: K.ContractTerms,
                 omega: float = 1.0, base_seed: int = 20260803) -> Dict:
    """Run a full scenario and aggregate across paths (spec 2, 9, 11)."""
    match = K.match_fix_a(reference_base_path(params, terms), terms)
    cohort = generate_cohort(n_paths, params, base_seed)
    per_path = [run_path(p, terms, match, omega) for p in cohort]

    agg: Dict[str, Dict] = {}
    for arm in ARMS:
        rs = [r[arm] for r in per_path]
        durs = [r.duration for r in rs if r.duration is not None]
        agg[arm] = {
            "n_paths": n_paths,
            "burden_mean":  _mean([r.burden["mean"] for r in rs]),
            "burden_max":   _mean([r.burden["max"] for r in rs]),
            "burden_p90":   _mean([r.burden["p90"] for r in rs]),
            "burden_p95":   _mean([r.burden["p95"] for r in rs]),
            "n_high_burden": {th: _mean([r.n_high_burden[th] for r in rs])
                              for th in M.THRESHOLDS},
            "duration_mean": _mean(durs),
            "duration_sd":   statistics.pstdev(durs) if len(durs) > 1 else 0.0,
            "duration_censored_rate": sum(r.censored for r in rs) / n_paths,
            "total_repaid_mean": _mean([r.total_repaid for r in rs]),
            "multiple_mean":     _mean([r.multiple for r in rs]),
            "recovery_ratio": {k: _mean([r.recovery_ratio[k] for r in rs])
                               for k in M.CHECKPOINTS},
            "incomplete_recovery_rate": _mean([r.incomplete_recovery for r in rs]),
            "post_shock_recovery": {k: _mean([r.post_shock_recovery[k] for r in rs])
                                    for k in (6, 12)},
            "apr_mean": _mean([r.apr for r in rs if r.apr is not None]),
        }

    return {"scenario": params.label or params.shock, "params": asdict(params),
            "terms": asdict(terms), "omega": omega, "match": match,
            "base_seed": base_seed, "arms": agg, "per_path": per_path,
            "regenerations": sum(p.regenerations for p in cohort)}


def paired_delta(result: Dict, metric: str, a: str = "FIX-A", b: str = "RBF",
                 **kw) -> List[float]:
    """Within-path paired differences a - b (spec 9). The ONLY valid comparison."""
    out = []
    for r in result["per_path"]:
        va, vb = _extract(r[a], metric, **kw), _extract(r[b], metric, **kw)
        if va is not None and vb is not None:
            out.append(va - vb)
    return out


def _extract(res: ArmResult, metric: str, **kw):
    if metric == "n_high_burden":
        return res.n_high_burden[kw["threshold"]]
    if metric == "recovery_ratio":
        return res.recovery_ratio[kw["k"]]
    if metric == "burden_max":
        return res.burden["max"]
    return getattr(res, metric, None)


def bootstrap_ci(values: List[float], n_boot: int = 10_000, alpha: float = 0.05,
                 seed: int = 90210) -> Dict:
    """Percentile bootstrap on paired differences (spec 6, 11).

    IMPORTANT (spec 15, rule 4): this interval quantifies MONTE CARLO PRECISION
    only -- whether enough paths were run for the number to be stable. It does
    NOT quantify uncertainty about real sellers. Running more paths narrows it
    without adding a single fact about the world.
    """
    if not values:
        return {"mean": None, "lo": None, "hi": None, "n": 0}
    import numpy as np
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    n = len(v)
    means = v[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    return {"mean": float(v.mean()),
            "lo": float(np.quantile(means, alpha / 2)),
            "hi": float(np.quantile(means, 1 - alpha / 2)),
            "n": n,
            "label": "Monte Carlo interval (simulated-path resampling)",
            "measures": "stability of the mean across simulated paths given the "
                        "chosen generative parameters",
            "does_not_measure": "population-level uncertainty about real sellers"}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None
