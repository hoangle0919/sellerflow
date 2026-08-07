"""Unit tests for the product monetary policy (D-030).

Written after mutation testing found two surviving mutants that the
end-to-end parity tests did not catch:

  * building `Decimal` from a binary float instead of its string form
  * clipping the payment BEFORE quantizing it, instead of after

Both are silent in aggregate and wrong in the specific. They are pinned here.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import money  # noqa: E402


# ── Decimals are built from strings, not binary floats ─────────────────────

def test_to_decimal_uses_the_string_form_of_a_float():
    """`Decimal(0.1)` is 0.1000000000000000055511151231257827021181583404541015625.
    `Decimal("0.1")` is exactly 0.1. Building from the binary float silently
    reintroduces the error the policy exists to remove."""
    assert money.to_decimal(0.1) == Decimal("0.1")
    assert money.to_decimal(0.1) != Decimal(0.1)
    assert money.to_decimal(0.15) == Decimal("0.15")
    assert money.to_decimal(1.15) == Decimal("1.15")


def test_to_decimal_is_exact_for_the_tier_rates():
    for r in ("0.15", "0.08", "0.12", "1.15", "1.30"):
        assert money.to_decimal(float(r)) == Decimal(r)


def test_binary_float_error_would_change_a_tie():
    """Concretely: with Decimal(float) the realistic tie lands below .5 and
    rounds the wrong way. This is why the string form is mandatory."""
    rev = Decimal(100_002_500)
    exact = rev * Decimal(12) * money.to_decimal(0.15)
    binary = rev * Decimal(12) * Decimal(0.15)
    assert exact == Decimal("180004500")
    assert binary < Decimal("180004500")          # strictly below the tie
    assert exact.quantize(Decimal("1E+3"), rounding=ROUND_HALF_UP) == Decimal("1.80005E+8")
    assert binary.quantize(Decimal("1E+3"), rounding=ROUND_HALF_UP) == Decimal("1.80004E+8")


# ── rounding rule ──────────────────────────────────────────────────────────

def test_to_vnd_is_half_up_not_bankers():
    assert money.to_vnd(2.5) == 3          # banker's would give 2
    assert money.to_vnd(1.5) == 2
    assert money.to_vnd(0.5) == 1
    assert round(2.5) == 2                 # documents the trap being avoided


def test_to_increment_is_half_up_at_the_thousand_boundary():
    assert money.to_increment(4_500) == 5_000       # banker's -> 4,000
    assert money.to_increment(13_500) == 14_000
    assert money.to_increment(22_500) == 23_000     # banker's -> 22,000
    assert money.to_increment(4_499) == 4_000


def test_to_vnd_returns_int_not_float():
    v = money.to_vnd(1_234.6)
    assert isinstance(v, int) and not isinstance(v, bool)


# ── the fixed order ────────────────────────────────────────────────────────

def test_cap_is_derived_from_the_rounded_advance():
    """The advance is what is actually disbursed, so the cap must reconcile
    against it. Deriving from the raw figure gives a cap the merchant cannot
    check against the money received."""
    adv = money.recommended_advance(100_002_500, "0.15")
    assert adv == 180_005_000
    assert money.repayment_cap(adv, "1.15") == 207_005_750


def test_raw_advance_is_exact_and_unrounded():
    assert money.raw_advance(100_002_500, "0.15") == Decimal("180004500")


# ── settle(): quantize, THEN clip ───────────────────────────────────────────

def test_settle_never_exceeds_the_cap():
    assert sum(money.settle([300] * 10, 1_000)) == 1_000


def test_settle_clips_the_final_payment_to_the_exact_remainder():
    s = money.settle([300] * 10, 1_000)
    assert s[:3] == [300, 300, 300]
    assert s[3] == 100                       # exact remainder, not a rounded 300
    assert s[4:] == [0] * 6
    assert sum(s) == 1_000


def test_settle_clips_a_single_oversized_payment():
    assert money.settle([10**15], 1_000) == [1_000]


def test_settle_quantizes_before_clipping():
    """The mutation that survived first time round: clipping a raw float and
    quantizing afterwards lets a rounded-up payment exceed the remaining
    balance. Rounding first makes the clip exact."""
    s = money.settle([333.6, 333.6, 333.6], 1_000)
    assert s == [334, 334, 332]              # 334+334=668, remainder 332
    assert sum(s) == 1_000


@pytest.mark.parametrize("cap", [1, 7, 999, 1_000, 207_005_750])
@pytest.mark.parametrize("pay", [0.4, 1, 333.5, 8_000_200])
def test_settle_invariants_hold_generally(cap, pay):
    s = money.settle([pay] * 200, cap)
    assert all(p >= 0 for p in s)
    cum = 0
    for p in s:
        cum += p
        assert cum <= cap
        assert cap - cum >= 0
    assert sum(s) <= cap


def test_settle_with_zero_payments_never_settles():
    assert sum(money.settle([0] * 50, 1_000)) == 0


def test_settle_returns_integers_only():
    assert all(isinstance(p, int) for p in money.settle([333.6] * 5, 1_000))


# ── illustrative schedule ──────────────────────────────────────────────────

def test_illustrative_schedule_totals_the_cap_exactly():
    s = money.illustrative_schedule(1_000, 300)
    assert s["full_payments"] == 3
    assert s["final_payment"] == 100
    assert s["final_payment_is_partial"] is True
    assert s["completion_month"] == 4
    assert s["total_contractual_repayment"] == 1_000


def test_illustrative_schedule_when_the_cap_divides_exactly():
    """No phantom zero-value final payment when it divides evenly."""
    s = money.illustrative_schedule(900, 300)
    assert s["full_payments"] == 2
    assert s["final_payment"] == 300
    assert s["final_payment_is_partial"] is False
    assert s["completion_month"] == 3
    assert s["total_contractual_repayment"] == 900


def test_illustrative_schedule_is_none_where_undefined():
    assert money.illustrative_schedule(0, 300) is None
    assert money.illustrative_schedule(1_000, 0) is None


def test_illustrative_schedule_agrees_with_settle():
    """The projection and the settlement routine must describe one schedule."""
    cap, pay = 207_005_750, 8_000_200
    ill = money.illustrative_schedule(cap, pay)
    sched = [p for p in money.settle([pay] * 200, cap) if p > 0]
    assert len(sched) == ill["completion_month"]
    assert sched[-1] == ill["final_payment"]
    assert sum(sched) == ill["total_contractual_repayment"] == cap
