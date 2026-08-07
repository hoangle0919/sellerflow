"""Financing contracts — METHODOLOGY_SPEC.md sections 6, 7, 8.

Four contracts, all originating at t=1 with identical principal A:
  FIX-A  fixed payment, matched principal AND matched total repayment (7.1)
  FIX-B  conventional amortizing loan at a documented APR (7.2)
  RBF    baseline revenue-based financing (8.1)
  RBF-G  guardrailed revenue-based financing (8.2)

Pure arithmetic. No model call anywhere in this module.
"""
from dataclasses import dataclass
from typing import List, Optional

from .settlement import FLOAT_GUARD_VND


@dataclass
class ContractTerms:
    A: float = 200_000_000.0   # principal
    r: float = 0.10            # remittance rate
    f: float = 1.20            # factor rate -> cap C = A*f
    # FIX-B (spec 7.2) — provisional, swept in spec 12 S-13
    j: float = 0.18            # nominal annual rate
    N_B: int = 12              # term, months
    # RBF-G guardrails (spec 8.2)
    p_min_mult: float = 0.25   # x r*R0
    p_max_mult: float = 2.00   # x r*R0
    hardship: float = 0.50     # floor suspended below h*R0
    remittance_basis: str = "net_sales"   # spec amendment A-1
    terminal_maturity: int = 0            # 0 = none; else write-off month (A-3)

    @property
    def cap(self) -> float:
        return self.A * self.f


def rbf_payments(revenue: List[float], terms: ContractTerms,
                 omega: float = 1.0) -> List[float]:
    """Spec 8.1. omega is the underreporting factor (spec 10.9): the provider
    observes omega*R_t while the seller's true revenue remains R_t."""
    cap, paid, out = terms.cap, 0.0, []
    for t_i, rev in enumerate(revenue):
        if terms.terminal_maturity and t_i >= terms.terminal_maturity:
            out.append(0.0)          # contract matures; remainder written off (A-3)
            continue
        p = terms.r * rev * omega
        p = max(0.0, min(p, cap - paid))
        paid += p
        out.append(p)
    return out


def rbf_g_payments(revenue: List[float], terms: ContractTerms, R0: float,
                   omega: float = 1.0) -> List[float]:
    """Spec 8.2. Floor is suspended when observed revenue < hardship*R0."""
    cap, paid, out = terms.cap, 0.0, []
    p_min = terms.p_min_mult * terms.r * R0
    p_max = terms.p_max_mult * terms.r * R0
    for rev in revenue:
        obs = rev * omega
        p = terms.r * obs
        if obs >= terms.hardship * R0:      # hardship rule (spec 8.2)
            p = max(p, p_min)
        p = min(p, p_max)
        p = max(0.0, min(p, cap - paid))
        paid += p
        out.append(p)
    return out


def rbf_duration(revenue: List[float], terms: ContractTerms,
                 tol: float = FLOAT_GUARD_VND) -> Optional[int]:
    """First month cumulative RBF payments reach the cap (spec 10.4).
    None = censored at horizon (spec 13, E-2).

    ANALYTICAL layer; `tol` is the centralized float guard, not a settlement
    tolerance (D-023). See `settlement.py` for the operational rule.
    """
    cap, total = terms.cap, 0.0
    for t, p in enumerate(rbf_payments(revenue, terms)):
        total += p
        if total >= cap - tol:
            return t + 1
    return None


def match_fix_a(reference_revenue: List[float], terms: ContractTerms) -> dict:
    """Spec 7.1 — matched principal, matched total repayment, matched term.

    Computed ONCE from the deterministic reference path and held fixed across
    every path in a scenario. The only difference from RBF is payment TIMING.
    """
    N = rbf_duration(reference_revenue, terms)
    if N is None:
        raise ValueError("RBF does not reach the cap on the reference path; "
                         "cannot match benchmark A (spec 7.1).")
    P = terms.cap / N
    return {"term": N, "payment": P, "total": terms.cap,
            "apr": solve_apr(terms.A, [P] * N)}


def fix_a_payments(terms: ContractTerms, match: dict, T: int) -> List[float]:
    """Spec 7.1. Independent of realised revenue -- that is the point."""
    return [match["payment"] if t < match["term"] else 0.0 for t in range(T)]


def fix_b_payments(terms: ContractTerms, T: int) -> List[float]:
    """Spec 7.2 — conventional amortizing annuity at nominal annual rate j."""
    i = terms.j / 12.0
    if i == 0:
        P = terms.A / terms.N_B
    else:
        P = terms.A * i / (1.0 - (1.0 + i) ** (-terms.N_B))
    return [P if t < terms.N_B else 0.0 for t in range(T)]


def solve_apr(principal: float, flows: List[float], iters: int = 300) -> Optional[float]:
    """Annualised IRR by bisection (spec 7.1, 10). None where undefined
    (no sign change) -- reported as undefined, never dropped (spec 13, E-3)."""
    def npv(i: float) -> float:
        return -principal + sum(p / (1.0 + i) ** (t + 1) for t, p in enumerate(flows))
    lo, hi = 1e-12, 2.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (1.0 + (lo + hi) / 2.0) ** 12 - 1.0
