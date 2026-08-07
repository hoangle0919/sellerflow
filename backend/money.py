"""Product-layer monetary policy — integer đồng, ROUND_HALF_UP (D-030).

WHY THIS EXISTS. `financing_engine` computed contractual money with binary
floats and Python's `round()`, which is *banker's* rounding (ties to even).
The project's documented settlement policy — `research/rbf_sim/settlement.py`,
decision D-023/D-024 — is ROUND_HALF_UP on integer đồng. At an exact tie the
two disagreed: a merchant with 100,002,500 VND of monthly revenue was shown an
advance of 180,004,000 instead of 180,005,000, and a cap 1,150 VND lower than
policy. Deterministic, and reachable at roughly 1 in 10,000 whole-VND revenues
(D-029).

WHY THIS IS NOT AN IMPORT OF `rbf_sim.settlement`. The research package is
deliberately independent of the backend — asserted by test — and production
should not take a dependency on a research tree to reuse one helper. The rule
is shared, the implementation is not. What keeps them honest is
`tests/test_settlement_parity.py`, which runs the same fixtures through both
layers and requires identical results.

DECIMALS ARE BUILT FROM STRINGS. `Decimal(0.15)` is
0.1499999999999999944488848768742172978818416595458984375; `Decimal("0.15")` is
exactly 0.15. Every rate below is declared as a string for that reason, and
`to_decimal` routes floats through `repr` so a caller passing a float cannot
silently reintroduce the binary artifact.

THE ORDER MATTERS AND IS FIXED (D-030):
  1. raw advance      = monthly_revenue x 12 x advance_pct     (Decimal)
  2. advance          = ROUND_HALF_UP to the 1,000 VND increment
  3. raw cap          = advance x factor_rate                  (Decimal)
  4. cap              = ROUND_HALF_UP to whole VND
  5. candidate payment= ROUND_HALF_UP to whole VND
  6. actual payment   = min(candidate, remaining balance)
  7. cumulative       <= cap, always
Rounding before clipping is what makes step 7 unconditional: the clip is
applied to an already-rounded amount, so rounding cannot breach the cap and the
final payment is an exact remainder rather than a rounded one.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Iterable, List, Optional, Union

Number = Union[int, float, str, Decimal]

#: The đồng has no circulating subunit: the minor unit IS the đồng.
VND = Decimal(1)

#: Advances are quoted to the nearest 1,000 VND. A product convention, not a
#: numerical one — stated here so it can be argued with.
ADVANCE_INCREMENT = Decimal("1E+3")

#: The documented rounding rule. Half-up is what a borrower can check by hand.
ROUNDING = ROUND_HALF_UP


def to_decimal(x: Number) -> Decimal:
    """Decimal from a string form, never from a binary float directly."""
    if isinstance(x, Decimal):
        return x
    if isinstance(x, int):
        return Decimal(x)
    return Decimal(repr(x)) if isinstance(x, float) else Decimal(str(x))


def to_vnd(x: Number) -> int:
    """ROUND_HALF_UP to whole đồng.

    Not `round()`: Python's round is banker's rounding on floats and would
    apply a different rule than the one documented. That divergence is the
    defect this module exists to remove (D-029).
    """
    with localcontext() as ctx:
        ctx.prec = 34
        return int(to_decimal(x).quantize(VND, rounding=ROUNDING))


def to_increment(x: Number, increment: Decimal = ADVANCE_INCREMENT) -> int:
    """ROUND_HALF_UP to the nearest `increment` đồng."""
    with localcontext() as ctx:
        ctx.prec = 34
        return int(to_decimal(x).quantize(increment, rounding=ROUNDING))


# ── the fixed order ─────────────────────────────────────────────────────────

def raw_advance(monthly_revenue: Number, advance_pct: Number) -> Decimal:
    """Step 1 — exact, unrounded."""
    return to_decimal(monthly_revenue) * Decimal(12) * to_decimal(advance_pct)


def recommended_advance(monthly_revenue: Number, advance_pct: Number) -> int:
    """Steps 1-2 — advance in whole đồng, quoted to the 1,000 VND increment."""
    return to_increment(raw_advance(monthly_revenue, advance_pct))


def repayment_cap(advance_vnd: Number, factor_rate: Number) -> int:
    """Steps 3-4 — cap from the ROUNDED advance, then rounded to whole đồng.

    Deriving the cap from the rounded advance (not the raw one) is deliberate:
    the advance is the amount actually disbursed, so it is the amount the cap
    must be a multiple of. Deriving from the raw figure would produce a cap the
    merchant cannot reconcile against the money they received.
    """
    return to_vnd(to_decimal(advance_vnd) * to_decimal(factor_rate))


def periodic_payment(revenue: Number, share_rate: Number) -> int:
    """Step 5 — candidate payment, quantized to whole đồng."""
    return to_vnd(to_decimal(revenue) * to_decimal(share_rate))


def settle(candidates: Iterable[Number], cap_vnd: int) -> List[int]:
    """Steps 5-7 — quantize, then clip to the remaining balance.

    Guarantees `sum(settle(...)) <= cap_vnd`, exactly and always.
    """
    paid = 0
    out: List[int] = []
    for c in candidates:
        p = to_vnd(c)
        p = max(0, min(p, cap_vnd - paid))
        paid += p
        out.append(p)
    return out


def illustrative_schedule(cap_vnd: int, payment_vnd: int) -> Optional[dict]:
    """Constant-revenue projection, with the partial final payment made explicit.

    This is the disclosure that was missing. Emitting only
    (cap, payment, duration) invites the reader to compute
    `payment x duration`, which overstates the total by up to one payment --
    a mistake made in this project's own gate report before it was caught.

    Returns None where no schedule is defined.
    """
    if not cap_vnd or not payment_vnd or payment_vnd <= 0 or cap_vnd <= 0:
        return None

    n_full, remainder = divmod(cap_vnd, payment_vnd)
    if remainder:
        full_payments, final_payment, completion = n_full, remainder, n_full + 1
    else:
        # Divides exactly: the last payment is a full one, not a partial.
        full_payments, final_payment, completion = n_full - 1, payment_vnd, n_full

    total = full_payments * payment_vnd + final_payment
    assert total == cap_vnd, "illustrative schedule must total exactly the cap"

    return {
        "full_payments": full_payments,
        "full_payment_amount": payment_vnd,
        "final_payment": final_payment,
        "final_payment_is_partial": final_payment < payment_vnd,
        "completion_month": completion,
        "total_contractual_repayment": total,
        "basis": "illustrative_projection",
        "assumption": "Holds monthly revenue constant at the stated figure. "
                      "Actual remittance varies with actual revenue, so the "
                      "number of payments and the completion month will differ.",
        "not_a_guarantee": "These are illustrative projections, not guaranteed "
                           "payment amounts or a guaranteed duration.",
    }
