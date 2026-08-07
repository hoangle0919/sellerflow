"""Parity between the product settlement layer and the research settlement layer.

Written as the diagnostic for the reported "cap overshoot" (D-029). Two
findings, and they point in opposite directions:

  1. THERE IS NO CAP OVERSHOOT. Across 6,794 structures spanning realistic and
     adversarial inputs, the settled total never exceeds the contractual cap and
     the product's duration always agrees with integer-VND settlement. The
     earlier "5.77% overshoot" figure was an inference from
     `duration x periodic_remittance`, which assumes every payment is full-size.
     The RBF contract clips the final payment to the remaining balance, so the
     last payment is partial and the total lands exactly on the cap. The
     inference was wrong; these tests pin the correct behaviour so it stays
     correct.

  2. THE TWO LAYERS DISAGREE ON THE ROUNDING RULE. `financing_engine` uses
     Python's `round()`, which is banker's rounding (ties to even).
     `settlement.to_vnd` uses the documented ROUND_HALF_UP. Where a value lands
     exactly on a tie this changes the advance a merchant is shown. That is
     recorded below as a strict xfail, not fixed: it changes displayed financial
     terms and is awaiting approval.

Why xfail rather than a red test: a committed failing test makes every future
run red and trains people to ignore it. `strict=True` means the suite fails if
the defect is ever silently fixed without removing the marker, so the record
cannot rot in either direction.
"""
import math
import sys
from decimal import Decimal, ROUND_HALF_UP

import pytest

sys.path.insert(0, __file__.rsplit("/tests/", 1)[0])
sys.path.insert(0, __file__.rsplit("/backend/", 1)[0] + "/research")

from financing_engine import financing_structure, scenario_analysis, TIER_PARAMS  # noqa: E402

settlement = pytest.importorskip("rbf_sim.settlement",
                                 reason="research package not present")
to_vnd = settlement.to_vnd
settle_payments = settlement.settle_payments
settlement_duration = settlement.settlement_duration

TIERS = ("Low Risk", "Medium Risk")


def _schedule(revenue, tier, cap, extra=40):
    return settle_payments([revenue] * (extra + 60), TIER_PARAMS[tier]["remittance_pct"], cap)


# ── the cap invariant actually holds ────────────────────────────────────────

@pytest.mark.parametrize("revenue", [
    10_000_000, 48_000_000, 92_000_000, 120_000_000, 185_000_000,
    340_000_000, 520_000_000, 999_999_999,
])
@pytest.mark.parametrize("tier", TIERS)
def test_settled_total_never_exceeds_the_contractual_cap(revenue, tier):
    s = financing_structure(revenue, tier)
    cap_vnd = to_vnd(s["repayment_cap"])
    assert sum(_schedule(revenue, tier, s["repayment_cap"])) <= cap_vnd


@pytest.mark.parametrize("revenue", [10_000_000, 120_000_000, 520_000_000])
@pytest.mark.parametrize("tier", TIERS)
def test_completed_schedule_lands_exactly_on_the_cap(revenue, tier):
    """Not 'within a tolerance of' — exactly."""
    s = financing_structure(revenue, tier)
    cap_vnd = to_vnd(s["repayment_cap"])
    assert sum(_schedule(revenue, tier, s["repayment_cap"])) == cap_vnd


@pytest.mark.parametrize("revenue", [10_000_000, 120_000_000, 520_000_000])
@pytest.mark.parametrize("tier", TIERS)
def test_final_payment_is_partial_not_a_full_remittance(revenue, tier):
    """The fact that makes `duration x remittance` the wrong total."""
    s = financing_structure(revenue, tier)
    nz = [p for p in _schedule(revenue, tier, s["repayment_cap"]) if p > 0]
    assert nz[-1] <= nz[0]
    assert sum(nz) == to_vnd(s["repayment_cap"])


@pytest.mark.parametrize("revenue", [10_000_000, 120_000_000, 520_000_000])
@pytest.mark.parametrize("tier", TIERS)
def test_product_duration_agrees_with_integer_vnd_settlement(revenue, tier):
    s = financing_structure(revenue, tier)
    sched = _schedule(revenue, tier, s["repayment_cap"])
    assert settlement_duration(sched, to_vnd(s["repayment_cap"])) == s["base_case_duration_months"]


# ── property tests over the schedule ────────────────────────────────────────

@pytest.mark.parametrize("revenue", [7_000_000, 120_000_000, 863_000_000])
@pytest.mark.parametrize("tier", TIERS)
def test_schedule_properties(revenue, tier):
    s = financing_structure(revenue, tier)
    cap_vnd = to_vnd(s["repayment_cap"])
    sched = _schedule(revenue, tier, s["repayment_cap"])

    assert all(p >= 0 for p in sched), "payments must be non-negative"

    cum, prev = 0, 0
    for p in sched:
        cum += p
        assert cum >= prev, "cumulative payment must be monotonic"
        assert cum <= cap_vnd, "cumulative payment must never exceed the cap"
        assert cap_vnd - cum >= 0, "remaining balance must never go negative"
        prev = cum
    assert cum == cap_vnd, "a completed schedule ends exactly at the cap"


def test_zero_revenue_never_settles_and_never_breaches():
    s = financing_structure(120_000_000, "Low Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    sched = settle_payments([0.0] * 60, TIER_PARAMS["Low Risk"]["remittance_pct"],
                            s["repayment_cap"])
    assert sum(sched) == 0
    assert settlement_duration(sched, cap_vnd) is None


def test_declining_path_never_breaches_the_cap():
    s = financing_structure(200_000_000, "Medium Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    path = [200_000_000 * (0.93 ** k) for k in range(400)]
    assert sum(settle_payments(path, TIER_PARAMS["Medium Risk"]["remittance_pct"],
                               s["repayment_cap"])) <= cap_vnd


def test_growth_path_never_breaches_the_cap():
    s = financing_structure(50_000_000, "Low Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    path = [50_000_000 * (1.15 ** k) for k in range(60)]
    assert sum(settle_payments(path, TIER_PARAMS["Low Risk"]["remittance_pct"],
                               s["repayment_cap"])) <= cap_vnd


def test_a_single_enormous_payment_is_clipped_to_the_cap():
    """Final payment far ABOVE the remaining balance."""
    s = financing_structure(120_000_000, "Low Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    sched = settle_payments([1e15], TIER_PARAMS["Low Risk"]["remittance_pct"],
                            s["repayment_cap"])
    assert sum(sched) == cap_vnd and sched[0] == cap_vnd


def test_long_schedule_of_tiny_payments_never_breaches():
    """Final payment slightly BELOW the remaining balance, repeatedly."""
    s = financing_structure(120_000_000, "Low Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    sched = settle_payments([1_000] * 5_000, TIER_PARAMS["Low Risk"]["remittance_pct"],
                            s["repayment_cap"])
    assert sum(sched) <= cap_vnd


@pytest.mark.parametrize("revenue", [120_000_000, 185_000_000])
def test_scenario_projections_never_imply_a_breach(revenue):
    """Scenario rows carry (remittance, duration). Under clipping, each row's
    settled total must still land on the cap — the scenarios must not describe
    a schedule that over-collects."""
    s = financing_structure(revenue, "Low Risk")
    cap_vnd = to_vnd(s["repayment_cap"])
    for row in scenario_analysis(revenue, 0.10, s):
        rev_s = row["scenario_monthly_revenue"]
        sched = settle_payments([rev_s] * (row["repayment_duration_months"] + 10),
                                TIER_PARAMS["Low Risk"]["remittance_pct"],
                                s["repayment_cap"])
        assert sum(sched) <= cap_vnd


# ── the real divergence: rounding rule, not cap logic ───────────────────────

def _half_up_thousands(x):
    return float(Decimal(repr(x)).quantize(Decimal("1E+3"), rounding=ROUND_HALF_UP))


def test_the_divergence_is_deterministic_not_floating_point_noise():
    """Documents the CAUSE. 180,004,500.0 is exactly representable in binary, so
    no float error is involved; the two layers simply apply different rounding
    rules at a tie."""
    raw = 100_002_500 * 12 * 0.15
    assert Decimal(raw) == Decimal("180004500"), "value is exact in binary"
    assert round(raw, -3) == 180_004_000.0          # banker's: ties to even
    assert _half_up_thousands(raw) == 180_005_000.0  # documented policy
    results = {financing_structure(100_002_500, "Low Risk")["recommended_amount"]
               for _ in range(200)}
    assert len(results) == 1, "divergence is deterministic, not intermittent"


@pytest.mark.xfail(strict=True, reason=(
    "D-029, OPEN: financing_engine uses round() (banker's, ties-to-even) while "
    "the documented settlement policy is ROUND_HALF_UP. At a tie this changes "
    "the advance the merchant is shown by 1,000 VND and the cap by 1,150 VND. "
    "Reachable at ~1 in 10,000 whole-VND revenues. NOT FIXED: it changes "
    "displayed financial terms and is awaiting approval."))
def test_smallest_reproducible_case_product_advance_follows_the_documented_rule():
    """SMALLEST REPRODUCIBLE CASE — revenue 2,500 VND.

        raw advance = 2,500 x 12 x 0.15 = 4,500.0   (exact in binary)
        product  round(4500, -3)        = 4,000     (banker's, ties to even)
        policy   ROUND_HALF_UP          = 5,000
        divergence                      = 1,000 VND
    """
    s = financing_structure(2_500, "Low Risk")
    assert s["recommended_amount"] == _half_up_thousands(2_500 * 12 * 0.15)


@pytest.mark.xfail(strict=True, reason=(
    "D-029, OPEN: same rounding-rule divergence at realistic scale."))
def test_realistic_scale_case_product_advance_follows_the_documented_rule():
    """Revenue 100,002,500 VND — advance diverges by 1,000 VND, cap by 1,150."""
    s = financing_structure(100_002_500, "Low Risk")
    assert s["recommended_amount"] == _half_up_thousands(100_002_500 * 12 * 0.15)


@pytest.mark.xfail(strict=True, reason=(
    "D-029, OPEN: product money is float, not integer dong. The settlement "
    "policy requires integer VND at the operational boundary."))
@pytest.mark.parametrize("field", ["recommended_amount", "repayment_cap",
                                   "periodic_remittance"])
def test_product_money_is_integer_dong(field):
    assert isinstance(financing_structure(120_000_000, "Low Risk")[field], int)


@pytest.mark.xfail(strict=True, reason=(
    "D-029, OPEN: the API emits (cap, remittance, duration) with no indication "
    "the final payment is partial and no final_payment field. A consumer who "
    "multiplies remittance x duration overstates the total by up to one "
    "remittance. Disclosure gap, not an arithmetic error."))
def test_structure_discloses_the_partial_final_payment():
    s = financing_structure(120_000_000, "Low Risk")
    assert "final_payment" in s
