"""Revenue-path generation — METHODOLOGY_SPEC.md section 4 and 5.

Replaces backend/generate_data.py, whose ten features were drawn independently
and so violated revenue = orders x AOV in 61% of rows (audit RI-2).

Rule enforced here: exactly one of {revenue, orders, AOV} is derived; the other
two are sampled. Identities are computed, never sampled. Verified by
tests/test_identities.py, not by convention.
"""
from dataclasses import dataclass, field
from typing import List
import math
import random

BASE_SEED = 20260803  # spec section 11

# ── Seasonality (spec 5.1) ────────────────────────────────────────────────────
# Shape: Q4 mega-sale lift (9.9/10.10/11.11/12.12), pre-Tet lift, post-Tet trough.
# ASSUMPTION, not measurement. Mean-normalised to 1.0 so seasonality
# redistributes revenue within a year without changing the annual total.
_SHAPE = [1.05, 0.80, 0.90, 0.95, 1.00, 0.95, 0.95, 1.00, 1.10, 1.15, 1.30, 1.25]


def seasonal_profile(amplitude: str = "moderate") -> List[float]:
    """Return a 12-month multiplier vector with mean exactly 1.0."""
    scale = {"flat": 0.0, "moderate": 1.0, "strong": 2.0}[amplitude]
    raw = [1.0 + scale * (s - 1.0) for s in _SHAPE]
    mean = sum(raw) / len(raw)
    return [x / mean for x in raw]


# ── Shocks (spec 5.2) ─────────────────────────────────────────────────────────

def shock_multipliers(kind: str, T: int, depth: float = 0.40, onset: int = 7) -> List[float]:
    """K_t vector. onset is 1-indexed month; K_t = 1 outside the shock window."""
    K = [1.0] * T
    i0 = onset - 1
    if kind == "none":
        return K
    if kind == "disruption_1m":
        if i0 < T:
            K[i0] = 1.0 - depth
    elif kind == "platform_outage":
        if i0 < T:
            K[i0] = 1.0 - 0.70
    elif kind == "decline_sustained":
        for t in range(i0, T):
            K[t] = 1.0 - depth
    elif kind == "decline_gradual":
        for t in range(i0, T):
            step = min((t - i0 + 1) / 6.0, 1.0)
            K[t] = 1.0 - depth * step
    elif kind == "downturn_multi":
        for t in range(i0, min(i0 + 6, T)):
            K[t] = 1.0 - depth
        for k, t in enumerate(range(i0 + 6, min(i0 + 12, T))):
            K[t] = 1.0 - depth * (1.0 - (k + 1) / 6.0)
    elif kind == "closure":
        # Business closure: revenue goes to zero permanently (spec amendment A-2)
        for t in range(i0, T):
            K[t] = 0.0
    elif kind == "temporary_closure":
        # Zero revenue for 3 months, then partial recovery to (1-depth)
        for t in range(i0, min(i0 + 3, T)):
            K[t] = 0.0
        for t in range(i0 + 3, T):
            K[t] = 1.0 - depth
    elif kind == "extended_downturn":
        # Deep and long: depth for 12 months, then recovery over 6
        for t in range(i0, min(i0 + 12, T)):
            K[t] = 1.0 - depth
        for k, t in enumerate(range(i0 + 12, min(i0 + 18, T))):
            K[t] = 1.0 - depth * (1.0 - (k + 1) / 6.0)
    elif kind == "returns_spike":
        pass  # acts on return_rate, not gross revenue (spec 5.2)
    else:
        raise ValueError(f"unknown shock kind: {kind}")
    return K


@dataclass
class PathParams:
    """All parameters of one revenue path. Every field appears in the spec."""
    R0: float = 185_000_000.0
    T: int = 24
    growth: float = 0.0                 # g, monthly (spec 4)
    sigma: float = 0.15                 # idiosyncratic noise (spec 4)
    seasonality: str = "moderate"       # spec 5.1
    shock: str = "none"                 # spec 5.2
    shock_depth: float = 0.40
    shock_onset: int = 7
    aov0: float = 440_000.0
    aov_sigma: float = 0.05
    return_rate: float = 0.03
    platform_fee_rate: float = 0.0   # ILLUSTRATIVE, unsourced; swept in S-15
    label: str = ""


@dataclass
class SellerPath:
    """One simulated seller. All fields satisfy the identities in spec 4.

    Revenue chain (spec amendment A-1). Only ONE identity is exact by
    construction; the rest are deductions FROM it, not parts of it:
        gmv_t          = orders_t x aov_t          <- the exact identity
        net_sales_t    = gmv_t x (1 - return_rate_t)
        cash_receipts_t= net_sales_t x (1 - platform_fee_rate)
    `revenue` is retained as an alias for `gmv` so that "payment-to-revenue"
    keeps its conventional top-line meaning.
    """
    gmv: List[float]
    orders: List[int]
    aov: List[float]
    return_rate: List[float]
    net_sales: List[float]
    cash_receipts: List[float]
    returns: List[float]
    params: PathParams
    seed: int
    regenerations: int = 0
    provenance: str = field(default="simulated", init=False)

    @property
    def revenue(self) -> List[float]:
        """Alias for gmv - the top line, used as the payment-burden denominator."""
        return self.gmv

    def remittance_base(self, basis: str = "net_sales") -> List[float]:
        """The series a remittance is actually charged on (spec amendment A-1)."""
        return {"gmv": self.gmv, "net_sales": self.net_sales,
                "cash_receipts": self.cash_receipts}[basis]


def generate_path(seed: int, p: PathParams) -> SellerPath:
    """Generate one path. Deterministic given (seed, params) — spec 11."""
    rng = random.Random(seed)
    season = seasonal_profile(p.seasonality)
    K = shock_multipliers(p.shock, p.T, p.shock_depth, p.shock_onset)

    mu = -(p.sigma ** 2) / 2.0  # so E[eps] = 1 exactly (spec 4)
    gmv, orders, aov, rr, net, cash, rets = [], [], [], [], [], [], []
    regens = 0

    for t in range(p.T):
        G = (1.0 + p.growth) ** t
        S = season[t % 12]
        eps = math.exp(rng.gauss(mu, p.sigma))
        r_target = p.R0 * G * S * K[t] * eps

        # AOV sampled; regenerate on non-positive draw (spec 13, E-5)
        a = p.aov0 * (1.0 + rng.gauss(0.0, p.aov_sigma))
        while a <= 0:
            a = p.aov0 * (1.0 + rng.gauss(0.0, p.aov_sigma))
            regens += 1

        # orders DERIVED then gmv recomputed, so the identity holds EXACTLY
        # with integer order counts. This is the correction to audit RI-2.
        # Zero-revenue months (closure) are representable: n = 0 is allowed.
        n = max(0, round(r_target / a)) if K[t] == 0.0 else max(1, round(r_target / a))
        g = n * a

        base_rr = p.return_rate
        if p.shock == "returns_spike" and p.shock_onset - 1 <= t < p.shock_onset + 2:
            base_rr = min(0.40, base_rr * 3.0)

        ns = g * (1.0 - base_rr)                      # deduction, not identity
        cr = ns * (1.0 - p.platform_fee_rate)         # deduction, not identity

        gmv.append(g)
        orders.append(n)
        aov.append(a)
        rr.append(base_rr)
        rets.append(base_rr * n)
        net.append(ns)
        cash.append(cr)

    return SellerPath(gmv, orders, aov, rr, net, cash, rets, p, seed, regens)


def generate_cohort(n_paths: int, p: PathParams, base_seed: int = BASE_SEED) -> List[SellerPath]:
    """Cohort with seed = BASE_SEED + index (spec 11)."""
    return [generate_path(base_seed + i, p) for i in range(n_paths)]


def reference_base_path(p: PathParams, terms=None) -> List[float]:
    """Deterministic reference path used ONLY for benchmark matching (spec 7.1).

    Flat R0: no trend, no seasonality, no shock, no noise. Matching must be
    computed once and held fixed across every path in a scenario -- otherwise
    the fixed benchmark would adapt to the shock it is meant to be compared
    against, destroying the paired design.
    """
    if terms is None:
        return [p.R0] * p.T
    # Reference must use the SAME contractual basis as the live contract (A-1),
    # otherwise benchmark A is matched against a different quantity than RBF pays on.
    scale = {"gmv": 1.0,
             "net_sales": (1.0 - p.return_rate),
             "cash_receipts": (1.0 - p.return_rate) * (1.0 - p.platform_fee_rate)
             }[terms.remittance_basis]
    return [p.R0 * scale] * p.T
