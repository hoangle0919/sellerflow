"""Financing contracts — METHODOLOGY_SPEC.md sections 6, 7, 8.

Four contracts, all originating at t=1 with identical principal A:
  FIX-A  fixed payment, matched principal AND matched total repayment (7.1)
  FIX-B  conventional amortizing loan at a documented APR (7.2)
  RBF    baseline revenue-based financing (8.1)
  RBF-G  guardrailed revenue-based financing (8.2)

Pure arithmetic. No model call anywhere in this module.
"""
import math
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


#: Lower end of the economically valid monthly-rate domain. `i = -1` is the
#: singularity of `(1+i)^-t`, so the bracket opens just above it. A monthly rate
#: at this bound is a near-total loss; nothing below it has meaning.
IRR_MIN_MONTHLY = -1.0 + 1e-9


def irr_upper_bound(principal: float, flows: List[float]) -> float:
    """Exact analytic upper bracket for the monthly IRR. No arbitrary ceiling.

    A fixed upper bracket is a silent correctness bug, not a convenience. The
    first version of this solver used a hard `10.0`, which returned `None` for
    `solve_apr(100, [1200])` -- a stream whose unique monthly IRR is 11 -- and
    reported it as "no rate exists". A ceiling chosen for comfort will always
    be exceeded by some input, and the failure mode is indistinguishable from
    a genuine absence.

    The bound is derivable instead, in two cases, because the key inequality
    reverses sign at `i = 0` -- which cost one iteration of this function to
    notice.

    **Repaid more than advanced (`S > P`), so the root is positive.** For any
    `t >= 1` and `i > 0`, `(1+i)^t >= (1+i)`, so

        NPV(i) = -P + sum_t f_t/(1+i)^t  <=  -P + S/(1+i)

    which is `<= 0` as soon as `1+i >= S/P`. NPV is strictly decreasing, so
    `i* <= S/P - 1`, with equality exactly in the single-payment case.

    **Repaid less than advanced (`S < P`), so the root is negative.** The
    inequality above does not hold for `i < 0`: there `(1+i) < 1`, so
    `(1+i)^t <= (1+i)` and the direction flips. But no bound is needed --
    `NPV(0) = S - P < 0` directly, so `0` brackets the root from above.

    `S == P` puts the root exactly at `0`, which the caller handles as an
    endpoint root.
    """
    total = sum(flows)
    if principal <= 0:
        raise ValueError("principal must be positive to bracket an IRR")
    return max(total / principal - 1.0, 0.0)


def solve_apr(principal: float, flows: List[float], iters: int = 400) -> Optional[float]:
    """Annualised IRR of the FULL monthly flow vector, over `i > -1` (spec A-9).

    Two things here were wrong before A-9, and both moved published figures.

    **The vector must not be compressed.** Callers previously passed
    `[x for x in payments if x > 0]`, which deletes internal zero months and so
    moves every later payment earlier in calendar time. A stream paying nothing
    in months 7-9 and resuming in month 10 was discounted as though month 10
    arrived in month 7. Pass the whole vector, zeros included; position is the
    information. Trailing zeros are harmless at any position, so the defect bound
    exactly where a scenario had an *internal* zero-revenue spell -- in
    `temp_closure` it overstated the annualised rate by roughly five points.

    **The domain must include losses.** The bracket was `[1e-12, 2.0]`, which
    cannot represent a negative return, so a contract recovering less than it
    advanced returned `None` and was published as *undefined*. Permanent closure
    at month 7 recovers about 98.3M against 185M; its IRR is roughly -86.5%.
    Reporting that as undefined hid an adverse result behind a word that reads
    like a technicality.

    Existence, under this project's sign pattern: one negative advance at `t = 0`
    followed by non-negative payments. NPV is then strictly decreasing in `i`
    wherever any payment is positive, so the root is unique and bisection is
    sufficient. `None` is returned only when **no payment is positive** -- the
    one case in which no rate satisfies the equation.

    Note this is the rate over the payments actually made within the observation
    horizon. On an incomplete, non-absorbing path that is an observed-window
    figure, not the final lifetime return (A-9 iv), and must be reported beside
    incomplete-recovery information.
    """
    if not any(p > 0 for p in flows):
        return None                      # no root exists under the A-9 definition

    def npv(i: float) -> float:
        """NPV at monthly rate `i`, with the `i -> -1+` limit handled explicitly.

        As `i` approaches -1 from above, `(1+i)**(t+1)` underflows to 0.0 for
        long vectors and a naive expression raises ZeroDivisionError. The limit
        is not undefined, it is `+inf`: the discount factor diverges and any
        positive payment dominates the finite principal. Returning `inf` keeps
        the bracket valid instead of crashing at the edge of the domain.
        """
        total = -principal
        base = 1.0 + i
        for t, p in enumerate(flows):
            if p == 0.0:
                continue                 # position still counts; the term is 0
            d = base ** (t + 1)
            if d == 0.0:                 # underflow: term -> +inf
                return math.inf
            total += p / d
        return total

    lo, hi = IRR_MIN_MONTHLY, irr_upper_bound(principal, flows)
    f_lo, f_hi = npv(lo), npv(hi)

    # A root sitting exactly on a bracket endpoint is still a root. The previous
    # version required a strict sign change, so `solve_apr(100, [1100])` --
    # monthly IRR exactly 10.0, the old hard ceiling -- was reported as having
    # no rate. With the analytic bound above, the single-payment case lands on
    # the endpoint by construction, so this is the common case rather than a
    # curiosity.
    if f_hi == 0.0:
        return _annualise(hi)
    if f_lo == 0.0:
        return _annualise(lo)

    # With one negative advance followed by non-negative payments, NPV is
    # strictly decreasing in `i`: it tends to +inf as i -> -1+ and is <= 0 at
    # the analytic upper bound. A sign change is therefore guaranteed whenever
    # some payment is positive, and this branch should be unreachable. It is
    # kept because "should be unreachable" has been wrong before in this project.
    if not (f_lo > 0 > f_hi):
        return None

    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return _annualise((lo + hi) / 2.0)


def _annualise(monthly: float) -> float:
    """Monthly rate -> effective annual rate.

    The one documented numerical limit in this module: `(1+i)**12` overflows a
    float64 above roughly `i = 1.4e25`, which needs a stream repaying about
    1e25x the advance in a single month. No contract this project models can
    produce it, and a real one would be a data error. If it ever happens the
    overflow is raised rather than silently returned as `inf`, because an
    infinite return reported as a number is worse than a crash.
    """
    return (1.0 + monthly) ** 12 - 1.0
