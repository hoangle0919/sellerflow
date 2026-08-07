"""Outcome metrics — METHODOLOGY_SPEC.md section 10.

Terminology is binding. The primary burden metric is a HIGH-PAYMENT-BURDEN
month, computed from revenue alone. "Distress" requires operating-cost
assumptions and is secondary and assumption-dependent (10.3). Incomplete
recovery is NEVER called a default rate (10.7).
"""
from typing import List, Optional, Dict
import statistics

from .settlement import FLOAT_GUARD_VND

THRESHOLDS = (0.10, 0.15, 0.20, 0.25)     # spec 10.2
CHECKPOINTS = (12, 18, 24)                # spec 10.6


def payment_burden(revenue: List[float], payments: List[float]) -> List[Optional[float]]:
    """PB_t = p_t / R_t. Undefined where R_t = 0 (spec 13, E-1)."""
    return [(p / r if r > 0 else None) for r, p in zip(revenue, payments)]


def burden_stats(revenue: List[float], payments: List[float]) -> Dict:
    """Mean/median/max/p90/p95 over active months (spec 10.1)."""
    vals = [b for b, p in zip(payment_burden(revenue, payments), payments)
            if b is not None and p > 0]
    if not vals:
        return {"n_active": 0, "mean": None, "median": None,
                "max": None, "p90": None, "p95": None}
    s = sorted(vals)

    def pct(q: float) -> float:
        # linear interpolation between order statistics
        if len(s) == 1:
            return s[0]
        k = q * (len(s) - 1)
        lo = int(k)
        hi = min(lo + 1, len(s) - 1)
        return s[lo] + (k - lo) * (s[hi] - s[lo])

    return {"n_active": len(s), "mean": statistics.fmean(s), "median": statistics.median(s),
            "max": max(s), "p90": pct(0.90), "p95": pct(0.95)}


def n_high_burden(revenue: List[float], payments: List[float],
                  thresholds=THRESHOLDS) -> Dict[float, int]:
    """Spec 10.2 — count of high-payment-burden months at each threshold.

    NOTE (spec 10.2): for RBF, PB_t == r until the cap binds, so RBF's burden
    is constant BY CONSTRUCTION. This metric does not test whether RBF
    stabilises burden -- that is definitional. The information is on the fixed
    side: how far and how often a fixed payment's burden rises as revenue falls.
    """
    out = {}
    for th in thresholds:
        out[th] = sum(1 for b, p in zip(payment_burden(revenue, payments), payments)
                      if b is not None and p > 0 and b > th)
    return out


def duration(payments: List[float], cap: float,
             tol: float = FLOAT_GUARD_VND) -> Optional[int]:
    """Spec 10.4. None = censored at horizon (spec 13, E-2).

    ANALYTICAL layer: completion is the exact condition `cumulative >= cap`
    (spec 10.11, mathematical completion). `tol` defaults to the centralized
    FLOAT_GUARD_VND, which absorbs IEEE-754 representation error ONLY — it is
    not a settlement tolerance and is ~5e5x tighter than the 0.5 it replaces
    (D-023). For OPERATIONAL completion in whole dong under a declared policy,
    use `settlement.settlement_duration`.
    """
    total = 0.0
    for t, p in enumerate(payments):
        total += p
        if total >= cap - tol:
            return t + 1
    return None


def total_repaid(payments: List[float]) -> float:
    return sum(payments)


def recovery_at(payments: List[float], k: int) -> float:
    """Spec 10.6 — capital recovered by month k."""
    return sum(payments[:k])


def recovery_ratios(payments: List[float], cap: float,
                    checkpoints=CHECKPOINTS) -> Dict[int, float]:
    return {k: recovery_at(payments, k) / cap for k in checkpoints}


def incomplete_recovery(payments: List[float], cap: float,
                        tol: float = FLOAT_GUARD_VND) -> int:
    """Spec 10.7. NOT a default rate. Failure to reach the cap within the
    observation window on a simulated path.

    ANALYTICAL layer; `tol` is the centralized float guard, not a settlement
    tolerance (D-023). See `duration` and `settlement.py`.
    """
    return int(sum(payments) < cap - tol)


def post_shock_recovery(payments: List[float], onset: int, k: int) -> float:
    """Spec 10.8 — capital recovered in the k months from shock onset."""
    i0 = max(0, onset - 1)
    return sum(payments[i0:i0 + k + 1])


def distress_months(revenue: List[float], payments: List[float],
                    m: float, F: float) -> int:
    """Spec 10.3 — SECONDARY, ASSUMPTION-DEPENDENT. Only report in tables that
    state m and F inline. Never a headline. Subject to the spec 14 coherence
    constraint."""
    return sum(1 for r, p in zip(revenue, payments) if m * r - F - p < 0)


def coherent(m: float, F: float, P_fix_a: float, R0: float) -> bool:
    """Spec 14 — can the seller service the matched payment out of gross profit
    under the base path? If not, the distress metric is degenerate."""
    return (m * R0 - F - P_fix_a) > 0
