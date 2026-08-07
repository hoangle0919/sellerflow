"""Centralized VND settlement policy — METHODOLOGY_SPEC.md 10.11, decision D-023.

TWO LAYERS, DELIBERATELY SEPARATE. Conflating them is the defect D-023 names.

  ANALYTICAL LAYER — exact mathematical definitions.
      Completion means  r * S_T >= F * A  in exact arithmetic, at some finite T.
      There is NO completion epsilon at this layer, ever. Where the layer is
      evaluated in IEEE-754 doubles, FLOAT_GUARD_VND absorbs representation
      error and nothing else. It is a NUMERICAL guard, not a settlement rule.
      It is sized to the measured error (see below), not chosen for comfort.

  OPERATIONAL LAYER — money is an integer number of dong.
      The Vietnamese dong has no circulating subunit, so a *settled* payment
      cannot be fractional. Payments are quantized under an explicit, documented
      rounding rule and clipped to the remaining contractual cap. The cap
      comparison is then exact integer arithmetic, so the settlement epsilon is
      ZERO BY CONSTRUCTION. A non-zero epsilon may still be *declared* as
      commercial policy and swept as sensitivity — but it is then a stated
      contract term, never a numerical patch.

WHY THIS MODULE EXISTS (D-023, approved).
      Before this correction the codebase carried `tol = 0.5` in
      `metrics.duration`, `metrics.incomplete_recovery` and
      `contracts.rbf_duration`, and `CAP_TOL = 1.0` in the derivation tests:
      four constants, three modules, two values, and zero mentions in the frozen
      specification. That is a floating-point workaround shaped like a
      settlement policy. It is now one constant in one place, and the monetary
      rule it was impersonating is written down explicitly.

MEASURED FLOAT ERROR (this repository, 3,000 paths x 10 baseline scenarios,
      float payments recomputed against exact `fractions.Fraction` arithmetic):
          worst per-payment deviation      9.2387e-08 VND
          worst cumulative-sum deviation   8.9407e-08 VND
          paths where the float cumulative sum fails to reach an exactly
          reached cap at tol = 0                            0 of 3,000
      FLOAT_GUARD_VND = 1e-6 is ~11x the measured worst case and ~5.0e5 times
      TIGHTER than the 0.5 it replaces. It cannot absorb a real monetary
      shortfall: the smallest unit of account is 1 VND, one million times larger.

THIS MODULE CHANGES NO PROPOSITION. `DERIVATIONS.md` P1-P7 are statements about
exact arithmetic and are untouched. What changes is that the code now says which
layer it is speaking from.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Iterable, List, Optional, Union

Number = Union[int, float, Decimal]

# ── numerical guard (NOT money) ───────────────────────────────────────────────
# Absorbs IEEE-754 representation error when the ANALYTICAL layer is evaluated
# in floating point. Sized to measured error; see module docstring. This is not
# a settlement tolerance and must never be presented as one.
FLOAT_GUARD_VND = 1e-6

# The dong has no circulating subunit: the minor unit IS the dong.
VND_MINOR_UNIT = Decimal(1)

# Documented rounding rule for the operational boundary. Half-up is the
# convention used for consumer-facing money in Vietnam and is the rule a
# borrower would expect to be able to check by hand. Chosen explicitly so that
# it can be disagreed with; not inherited from Python's default.
VND_ROUNDING = ROUND_HALF_UP


def to_vnd(amount: Number, rounding: str = VND_ROUNDING) -> int:
    """Quantize an amount to whole dong under the documented rounding rule.

    Uses Decimal, not round(), because Python's round() is banker's rounding on
    floats and would silently apply a different rule than the one documented.
    """
    with localcontext() as ctx:
        ctx.prec = 34
        return int(Decimal(str(amount)).quantize(VND_MINOR_UNIT, rounding=rounding))


@dataclass(frozen=True)
class SettlementPolicy:
    """An explicit, declared operational settlement rule.

    epsilon_vnd
        Remaining balance at or below which the contract is treated as settled.
        DEFAULT 0: with integer-dong arithmetic the cap is reached exactly, so
        no tolerance is required. Any non-zero value is a commercial term that
        must be stated wherever a completion month derived from it is reported
        (spec 10.11).
    rounding
        The documented rounding rule applied at the operational boundary.
    """
    epsilon_vnd: int = 0
    rounding: str = VND_ROUNDING

    def __post_init__(self) -> None:
        if self.epsilon_vnd < 0:
            raise ValueError("epsilon_vnd must be non-negative")
        if int(self.epsilon_vnd) != self.epsilon_vnd:
            raise ValueError("epsilon_vnd must be a whole number of dong; "
                             "a fractional epsilon is a float workaround, "
                             "which is exactly what D-023 removes")

    def quantize(self, amount: Number) -> int:
        return to_vnd(amount, self.rounding)

    def describe(self) -> str:
        return (f"integer-VND settlement, rounding={self.rounding}, "
                f"epsilon={self.epsilon_vnd} VND"
                + (" (exact by construction)" if self.epsilon_vnd == 0 else
                   " (DECLARED commercial tolerance — must be reported alongside "
                   "any completion month derived from it)"))


#: The default policy. Exact settlement in whole dong.
EXACT_SETTLEMENT = SettlementPolicy(epsilon_vnd=0)


def settle_payments(remittance_base: Iterable[Number], r: Number, cap: Number,
                    omega: Number = 1.0,
                    policy: SettlementPolicy = EXACT_SETTLEMENT) -> List[int]:
    """Operational RBF payment schedule in whole dong (spec 8.1 + 10.11).

    Each payment is quantized to whole dong and then clipped to the remaining
    contractual cap, in that order. Clipping last is what guarantees the
    invariant the contract actually promises:

        sum(settle_payments(...)) <= cap_vnd,  always and exactly.

    Rounding before clipping cannot breach the cap, because the clip is applied
    to the already-rounded amount. The final payment is therefore an exact
    integer remainder, not a rounded one.
    """
    cap_vnd = policy.quantize(cap)
    paid = 0
    out: List[int] = []
    for rev in remittance_base:
        p = policy.quantize(Decimal(str(r)) * Decimal(str(rev)) * Decimal(str(omega)))
        p = max(0, min(p, cap_vnd - paid))      # clip to remaining cap (D-023)
        paid += p
        out.append(p)
    return out


def mathematically_complete(payments: Iterable[Number], cap: Number) -> bool:
    """ANALYTICAL completion: cumulative payments reach the cap in exact
    arithmetic. No epsilon. This is the concept `DERIVATIONS.md` P7 reasons
    about, and the one under which rho = rho* never completes at any finite T.
    """
    total = Decimal(0)
    for p in payments:
        total += Decimal(str(p))
    return total >= Decimal(str(cap))


def operationally_complete(payments: Iterable[int], cap_vnd: int,
                           policy: SettlementPolicy = EXACT_SETTLEMENT) -> bool:
    """OPERATIONAL completion: remaining balance <= the DECLARED epsilon.

    With the default policy this is exact integer equality — the contract is
    settled when the last dong is paid, and not one month before.
    """
    return (cap_vnd - sum(payments)) <= policy.epsilon_vnd


def settlement_duration(payments: Iterable[int], cap_vnd: int,
                        policy: SettlementPolicy = EXACT_SETTLEMENT) -> Optional[int]:
    """First month at which the contract is OPERATIONALLY settled.

    Returns None where the cap is not reached within the supplied schedule —
    censoring, never imputed as completion (spec 13, E-2).
    """
    total = 0
    for t, p in enumerate(payments):
        total += p
        if (cap_vnd - total) <= policy.epsilon_vnd:
            return t + 1
    return None
