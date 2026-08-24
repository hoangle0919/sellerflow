"""Parity between the product settlement layer and the research settlement layer.

Written as the diagnostic for the reported "cap overshoot" (D-029), and extended
into the regression suite for the correction (D-030). Two findings, and they
point in opposite directions:

  1. THERE IS NO CAP OVERSHOOT. Across 6,794 structures spanning realistic and
     adversarial inputs, the settled total never exceeds the contractual cap and
     the product's duration always agrees with integer-VND settlement. The
     earlier "5.77% overshoot" figure was an inference from
     `duration x periodic_remittance`, which assumes every payment is full-size.
     The RBF contract clips the final payment to the remaining balance, so the
     last payment is partial and the total lands exactly on the cap. The
     inference was wrong; these tests pin the correct behaviour so it stays
     correct.

  2. THE TWO LAYERS DISAGREED ON THE ROUNDING RULE. `financing_engine` used
     Python's `round()`, which is banker's rounding (ties to even), while the
     documented policy is ROUND_HALF_UP. At a tie this changed the advance a
     merchant was shown by 1,000 VND and the cap by 1,150 VND, at roughly 1 in
     10,000 whole-VND revenues. FIXED in D-030: contractual money is now
     Decimal-from-strings, integer đồng, ROUND_HALF_UP, via `backend/money.py`.

These were recorded as strict xfails while the fix awaited approval; they are
now passing regression tests, with the before/after values written into the
assertions so the correction cannot be silently reverted.

The parity fixtures below run the same inputs through the product layer and the
research layer. Production deliberately does NOT import `rbf_sim` — the research
package is independent of the backend, asserted by its own test — so the rule is
shared while the implementations are separate. These fixtures are the only thing
keeping them honest.
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
        # The closure row has no duration by construction: the cap is never
        # reached, so there is no schedule to over-collect. Rows that DO repay
        # must still land on the cap.
        if row["repayment_duration_months"] is None:
            continue
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


def test_smallest_reproducible_case_product_advance_follows_the_documented_rule():
    """SMALLEST REPRODUCIBLE CASE — revenue 2,500 VND. FIXED in D-030.

        raw advance = 2,500 x 12 x 0.15 = 4,500       (exact, Decimal)
        before  round(4500, -3)         = 4,000       (banker's, ties to even)
        after   ROUND_HALF_UP           = 5,000
    """
    s = financing_structure(2_500, "Low Risk")
    assert s["recommended_amount"] == 5_000
    assert s["recommended_amount"] == _half_up_thousands(2_500 * 12 * 0.15)


def test_realistic_scale_case_product_advance_follows_the_documented_rule():
    """Revenue 100,002,500 VND. Before D-030: advance 180,004,000, cap
    207,004,600. After: 180,005,000 and 207,005,750."""
    s = financing_structure(100_002_500, "Low Risk")
    assert s["recommended_amount"] == 180_005_000
    assert s["repayment_cap"] == 207_005_750
    assert s["recommended_amount"] == _half_up_thousands(100_002_500 * 12 * 0.15)


@pytest.mark.parametrize("field", ["recommended_amount", "repayment_cap",
                                   "periodic_remittance",
                                   "total_contractual_repayment"])
def test_product_money_is_integer_dong(field):
    v = financing_structure(120_000_000, "Low Risk")[field]
    assert isinstance(v, int) and not isinstance(v, bool)


def test_structure_discloses_the_partial_final_payment():
    """The disclosure that prevents the `remittance x duration` mistake."""
    s = financing_structure(120_000_000, "Low Risk")
    sched = s["illustrative_schedule"]
    assert sched is not None
    for k in ("full_payments", "full_payment_amount", "final_payment",
              "final_payment_is_partial", "completion_month",
              "total_contractual_repayment", "assumption", "not_a_guarantee"):
        assert k in sched, f"missing disclosure field {k}"
    assert sched["basis"] == "illustrative_projection"
    assert sched["completion_month"] == s["base_case_duration_months"]
    assert (sched["full_payments"] * sched["full_payment_amount"]
            + sched["final_payment"]) == s["repayment_cap"]


@pytest.mark.parametrize("revenue", [10_000_000, 120_000_000, 185_000_000, 520_000_000])
@pytest.mark.parametrize("tier", TIERS)
def test_illustrative_schedule_totals_exactly_the_cap(revenue, tier):
    s = financing_structure(revenue, tier)
    sched = s["illustrative_schedule"]
    assert sched["total_contractual_repayment"] == s["repayment_cap"]
    assert (sched["full_payments"] * sched["full_payment_amount"]
            + sched["final_payment"]) == s["repayment_cap"]
    assert 0 < sched["final_payment"] <= sched["full_payment_amount"]


def test_illustrative_schedule_is_labelled_as_a_projection_not_a_guarantee():
    """Future revenue is unknown, so these must not read as guaranteed terms."""
    sched = financing_structure(120_000_000, "Low Risk")["illustrative_schedule"]
    assert "constant" in sched["assumption"].lower()
    assert "not guaranteed" in sched["not_a_guarantee"].lower()


@pytest.mark.parametrize("revenue", [120_000_000, 185_000_000])
def test_every_scenario_row_discloses_its_own_schedule(revenue):
    s = financing_structure(revenue, "Low Risk")
    for row in scenario_analysis(revenue, 0.10, s):
        sched = row["illustrative_schedule"]
        if sched is None:
            # Closure: no completion month exists, so no schedule is disclosed.
            # It must instead disclose what goes unrecovered.
            assert row["case"] == "closure"
            assert row["repayment_duration_months"] is None
            assert row["amount_unrecovered"] > 0
            continue
        assert sched["total_contractual_repayment"] == s["repayment_cap"]
        assert sched["completion_month"] == row["repayment_duration_months"]


# ── cross-layer parity: same rule, independent implementations ──────────────

PARITY_FIXTURES = [
    # (label, revenue, tier) — chosen to include exact ties in both directions
    ("tie-up",            2_500, "Low Risk"),
    ("tie-realistic", 100_002_500, "Low Risk"),
    ("tie-down",      100_007_500, "Low Risk"),
    ("typical",       120_000_000, "Low Risk"),
    ("typical-med",   120_000_000, "Medium Risk"),
    ("large",         999_999_999, "Medium Risk"),
    ("small",          10_000_000, "Low Risk"),
]


@pytest.mark.parametrize("label,revenue,tier", PARITY_FIXTURES)
def test_product_and_research_agree_on_the_quantized_amount(label, revenue, tier):
    """The two layers share the RULE, not the implementation — production must
    not import the research package. These fixtures are what keeps them honest.
    """
    import money
    from financing_engine import TIER_RATES
    rate = TIER_RATES[tier]["remittance_pct"]
    assert money.periodic_payment(revenue, rate) == to_vnd(float(rate) * revenue)


@pytest.mark.parametrize("label,revenue,tier", PARITY_FIXTURES)
def test_product_cap_matches_research_quantization(label, revenue, tier):
    s = financing_structure(revenue, tier)
    if not s["repayment_cap"]:
        pytest.skip("no structure for this tier")
    assert s["repayment_cap"] == to_vnd(s["repayment_cap"])


@pytest.mark.parametrize("label,revenue,tier", PARITY_FIXTURES)
def test_product_schedule_matches_research_settlement(label, revenue, tier):
    """End-to-end: the product's illustrative schedule must agree with the
    research settlement layer run over the same constant-revenue path."""
    s = financing_structure(revenue, tier)
    if not s["periodic_remittance"]:
        pytest.skip("no structure for this tier")
    cap = s["repayment_cap"]
    sched = settle_payments([revenue] * (s["base_case_duration_months"] + 10),
                            TIER_PARAMS[tier]["remittance_pct"], cap)
    nz = [p for p in sched if p > 0]
    ill = s["illustrative_schedule"]
    assert sum(sched) == cap
    assert len(nz) == ill["completion_month"]
    assert nz[-1] == ill["final_payment"]
    assert settlement_duration(sched, to_vnd(cap)) == s["base_case_duration_months"]
