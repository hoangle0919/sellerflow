"""Accounting-identity tests — METHODOLOGY_SPEC.md section 4.

These exist because the original generator drew all ten features
independently, violating revenue = orders x AOV in 61% of rows (audit RI-2)
and causing the project's own integrity engine to flag 62.3% of the data its
credit model was trained on (RI-3).

The identities are enforced by these tests, not by convention.
"""
import math
import pytest

from rbf_sim.generator import (PathParams, generate_path, generate_cohort,
                               seasonal_profile, shock_multipliers)

SEEDS = list(range(20260803, 20260803 + 40))


@pytest.mark.parametrize("seed", SEEDS)
def test_revenue_equals_orders_times_aov_exactly(seed):
    """THE identity the original generator violated in 61% of rows."""
    p = generate_path(seed, PathParams(T=24, seasonality="strong", shock="decline_sustained"))
    for t in range(p.params.T):
        assert math.isclose(p.revenue[t], p.orders[t] * p.aov[t], rel_tol=1e-9), \
            f"identity broken at t={t}: {p.revenue[t]} != {p.orders[t]} * {p.aov[t]}"


@pytest.mark.parametrize("seed", SEEDS[:20])
def test_net_sales_deduction(seed):
    p = generate_path(seed, PathParams(T=24))
    for t in range(p.params.T):
        assert math.isclose(p.net_sales[t], p.revenue[t] * (1 - p.return_rate[t]), rel_tol=1e-9)


@pytest.mark.parametrize("seed", SEEDS[:20])
def test_returns_count_identity(seed):
    p = generate_path(seed, PathParams(T=24))
    for t in range(p.params.T):
        assert math.isclose(p.returns[t], p.return_rate[t] * p.orders[t], rel_tol=1e-9)


@pytest.mark.parametrize("seed", SEEDS[:20])
def test_all_quantities_non_negative(seed):
    p = generate_path(seed, PathParams(T=24, shock="downturn_multi", shock_depth=0.60))
    assert all(x >= 0 for x in p.revenue)
    assert all(n >= 1 for n in p.orders)
    assert all(a > 0 for a in p.aov)
    assert all(0 <= r <= 0.40 for r in p.return_rate)


def test_cohort_wide_identity_holds_for_every_row():
    """The regression test for RI-2: 61% violation must become 0%."""
    violations = 0
    total = 0
    for shock in ("none", "decline_sustained", "downturn_multi", "returns_spike"):
        for p in generate_cohort(25, PathParams(T=24, shock=shock)):
            for t in range(p.params.T):
                total += 1
                if not math.isclose(p.revenue[t], p.orders[t] * p.aov[t], rel_tol=1e-9):
                    violations += 1
    assert total > 2000
    assert violations == 0, f"{violations}/{total} rows violate revenue = orders x AOV"


def test_reconciliation_ratio_inside_integrity_engine_pass_band():
    """The original data failed integrity_engine's [0.55, 1.75] band 61% of the
    time. Every generated row must now sit at ~1.00."""
    for p in generate_cohort(30, PathParams(T=24, seasonality="strong")):
        for t in range(p.params.T):
            ratio = p.revenue[t] / (p.orders[t] * p.aov[t])
            assert 0.55 <= ratio <= 1.75
            assert math.isclose(ratio, 1.0, rel_tol=1e-9)


def test_seasonal_profile_is_mean_normalised():
    """Seasonality must redistribute revenue, not create it (spec 5.1)."""
    for amp in ("flat", "moderate", "strong"):
        s = seasonal_profile(amp)
        assert len(s) == 12
        assert math.isclose(sum(s) / 12, 1.0, rel_tol=1e-12)


def test_flat_seasonality_is_exactly_one():
    assert all(math.isclose(x, 1.0) for x in seasonal_profile("flat"))


def test_strong_amplitude_exceeds_moderate():
    mod, strong = seasonal_profile("moderate"), seasonal_profile("strong")
    assert max(strong) - min(strong) > max(mod) - min(mod)


def test_no_shock_leaves_multipliers_at_one():
    assert shock_multipliers("none", 24) == [1.0] * 24


def test_sustained_decline_shape():
    K = shock_multipliers("decline_sustained", 24, depth=0.40, onset=7)
    assert K[:6] == [1.0] * 6
    assert all(math.isclose(k, 0.60) for k in K[6:])


def test_one_month_disruption_is_one_month():
    K = shock_multipliers("disruption_1m", 24, depth=0.50, onset=7)
    assert math.isclose(K[6], 0.50)
    assert all(math.isclose(k, 1.0) for i, k in enumerate(K) if i != 6)


def test_returns_spike_raises_return_rate_not_gross_revenue():
    """spec 5.2: the returns shock acts on return_rate, not on gross revenue."""
    base = generate_path(1, PathParams(T=24, shock="none", sigma=0.0))
    spike = generate_path(1, PathParams(T=24, shock="returns_spike", shock_onset=7, sigma=0.0))
    assert base.gmv == spike.gmv                              # gross untouched
    assert spike.return_rate[6] > base.return_rate[6]         # rate raised
    assert spike.net_sales[6] < base.net_sales[6]         # net falls


def test_generation_is_deterministic_given_seed():
    """spec 11 — reruns with identical seeds reproduce bit-for-bit."""
    a = generate_path(42, PathParams(T=24))
    b = generate_path(42, PathParams(T=24))
    assert a.revenue == b.revenue and a.orders == b.orders and a.aov == b.aov


def test_different_seeds_give_different_paths():
    a = generate_path(1, PathParams(T=24))
    b = generate_path(2, PathParams(T=24))
    assert a.revenue != b.revenue


def test_expected_noise_multiplier_is_one():
    """E[eps] = 1 so noise does not bias the revenue level (spec 4)."""
    cohort = generate_cohort(400, PathParams(T=12, sigma=0.15, seasonality="flat"))
    mean_rev = sum(sum(p.revenue) / 12 for p in cohort) / len(cohort)
    assert math.isclose(mean_rev, 185_000_000.0, rel_tol=0.03)


# ── Revenue-definition chain (spec amendment A-1) ────────────────────────────

@pytest.mark.parametrize("seed", SEEDS[:15])
def test_gmv_is_the_only_exact_identity(seed):
    """gmv = orders x AOV is EXACT. net_sales and cash_receipts are DEDUCTIONS
    from it, not parts of the identity."""
    p = generate_path(seed, PathParams(T=24, platform_fee_rate=0.10))
    for t in range(p.params.T):
        assert math.isclose(p.gmv[t], p.orders[t] * p.aov[t], rel_tol=1e-9)
        assert math.isclose(p.net_sales[t], p.gmv[t] * (1 - p.return_rate[t]), rel_tol=1e-9)
        assert math.isclose(p.cash_receipts[t], p.net_sales[t] * 0.90, rel_tol=1e-9)


def test_revenue_alias_is_gmv():
    """`revenue` must remain the top line so payment-to-revenue keeps its
    conventional meaning (spec A-1)."""
    p = generate_path(1, PathParams(T=12))
    assert p.revenue == p.gmv


def test_deduction_chain_is_monotonically_decreasing():
    p = generate_path(7, PathParams(T=24, return_rate=0.05, platform_fee_rate=0.10))
    for t in range(p.params.T):
        assert p.gmv[t] >= p.net_sales[t] >= p.cash_receipts[t]


def test_remittance_base_selector():
    p = generate_path(3, PathParams(T=12, platform_fee_rate=0.08))
    assert p.remittance_base("gmv") == p.gmv
    assert p.remittance_base("net_sales") == p.net_sales
    assert p.remittance_base("cash_receipts") == p.cash_receipts


def test_zero_platform_fee_leaves_cash_equal_to_net_sales():
    p = generate_path(4, PathParams(T=12, platform_fee_rate=0.0))
    assert all(math.isclose(a, b) for a, b in zip(p.cash_receipts, p.net_sales))


# ── Closure and terminal scenarios (spec amendment A-2) ──────────────────────

def test_closure_drives_revenue_to_exactly_zero():
    """Business closure must produce true zero-revenue months, not small ones."""
    p = generate_path(11, PathParams(T=24, shock="closure", shock_onset=7))
    assert all(x > 0 for x in p.gmv[:6])
    assert all(x == 0.0 for x in p.gmv[6:])
    assert all(n == 0 for n in p.orders[6:])


def test_closure_preserves_the_identity_at_zero():
    """0 orders x AOV = 0 gmv. The identity must not break at the boundary."""
    p = generate_path(12, PathParams(T=24, shock="closure", shock_onset=5))
    for t in range(p.params.T):
        assert math.isclose(p.gmv[t], p.orders[t] * p.aov[t], rel_tol=1e-9)


def test_temporary_closure_recovers_partially():
    p = generate_path(13, PathParams(T=24, shock="temporary_closure",
                                     shock_onset=7, shock_depth=0.30, sigma=0.0))
    assert all(x == 0.0 for x in p.gmv[6:9])
    assert p.gmv[9] > 0


def test_extended_downturn_is_longer_than_multi_downturn():
    from rbf_sim.generator import shock_multipliers
    ext = shock_multipliers("extended_downturn", 36, depth=0.5, onset=7)
    multi = shock_multipliers("downturn_multi", 36, depth=0.5, onset=7)
    assert sum(ext) < sum(multi)
