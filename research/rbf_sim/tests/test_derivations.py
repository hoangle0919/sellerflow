"""Validate every proposition in DERIVATIONS.md against the engine.

These are not property demonstrations on one lucky path -- each proposition is
asserted across many randomly-shaped paths, including adversarial ones (zero
months, spikes, closure). If a proposition is wrong, or the engine drifts from
it, these fail.
"""
import math
import random
import pytest

from rbf_sim.contracts import (ContractTerms, rbf_payments, rbf_g_payments,
                               fix_a_payments, match_fix_a, solve_apr)
from rbf_sim import metrics as M
from rbf_sim.settlement import FLOAT_GUARD_VND

R0 = 100_000_000.0
T = 36


def terms(**kw):
    d = dict(A=100_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)
    d.update(kw)
    return ContractTerms(**d)


def random_paths(n=25, seed=7):
    """Adversarial variety: flat, trending, spiky, seasonal, zero months."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        kind = rng.choice(["flat", "trend", "spiky", "seasonal", "zeros"])
        p = []
        for t in range(T):
            if kind == "flat":
                v = R0
            elif kind == "trend":
                v = R0 * (1 + rng.uniform(-0.06, 0.06)) ** t
            elif kind == "spiky":
                v = R0 * rng.choice([0.2, 0.6, 1.0, 1.5, 3.0])
            elif kind == "seasonal":
                v = R0 * (1 + 0.5 * math.sin(2 * math.pi * t / 12))
            else:
                v = 0.0 if rng.random() < 0.25 else R0 * rng.uniform(0.5, 1.5)
            p.append(max(0.0, v))
        out.append(p)
    return out


PATHS = random_paths()

# D-023: this module used to define its own CAP_TOL = 1.0, inconsistent with the
# engine's 0.5. Both are gone. There is now ONE constant, in one place, and it is
# a float-representation guard rather than a settlement rule.
CAP_TOL = FLOAT_GUARD_VND


# ── P1 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_P1_burden_equals_r_until_capped_payment(path):
    """p_t/B_t = r for every month strictly before the capped one."""
    t = terms()
    pay = rbf_payments(path, t)
    # locate the capped month: first month cumulative reaches the cap
    cum, kstar = 0.0, None
    for i, x in enumerate(pay):
        cum += x
        if cum >= t.cap - CAP_TOL:
            kstar = i
            break
    end = kstar if kstar is not None else len(pay)
    for i in range(end):
        if path[i] > 0:
            assert math.isclose(pay[i] / path[i], t.r, rel_tol=1e-9), f"month {i}"
    if kstar is not None and path[kstar] > 0:
        assert pay[kstar] / path[kstar] <= t.r + 1e-9      # capped month: <= r
        for i in range(kstar + 1, len(pay)):
            assert pay[i] == 0.0                            # nothing after


# ── P2 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("lam", [0.9, 0.75, 0.5, 0.25, 0.1])
def test_P2_fixed_burden_scales_exactly_as_one_over_lambda(lam):
    """Revenue falls by factor lam -> fixed burden rises by exactly 1/lam."""
    P = 10_000_000.0
    b_hi = M.payment_burden([R0], [P])[0]
    b_lo = M.payment_burden([R0 * lam], [P])[0]
    assert math.isclose(b_lo / b_hi, 1.0 / lam, rel_tol=1e-12)


def test_P2_elasticity_is_minus_one():
    """d ln(PB) / d ln(B) = -1, checked numerically."""
    P, h = 10_000_000.0, 1e-6
    b1 = math.log(P / (R0 * math.exp(-h)))
    b2 = math.log(P / (R0 * math.exp(h)))
    assert math.isclose((b2 - b1) / (2 * h), -1.0, rel_tol=1e-6)


# ── P3 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_P3_cap_reached_iff_cumulative_base_exceeds_threshold(path):
    """Cap reached by k  <=>  S_k >= A*f/r. Threshold is a constant."""
    t = terms()
    threshold = t.cap / t.r
    pay = rbf_payments(path, t)
    cum_pay, cum_base = 0.0, 0.0
    for k in range(len(path)):
        cum_pay += pay[k]
        cum_base += path[k]
        assert (cum_pay >= t.cap - CAP_TOL) == (cum_base >= threshold - CAP_TOL / t.r), \
            f"month {k}: S_k={cum_base:.0f} vs threshold={threshold:.0f}"


def test_P3_threshold_value_is_A_f_over_r():
    t = terms()
    assert math.isclose(t.cap / t.r, t.A * t.f / t.r, rel_tol=1e-12)
    assert math.isclose(t.cap / t.r, 12 * R0, rel_tol=1e-12)   # 100M*1.2/0.10


@pytest.mark.parametrize("perm_seed", [1, 2, 3, 4, 5])
def test_P3_duration_depends_only_on_cumulative_series(perm_seed):
    """Reordering months changes WHEN revenue arrives; the cap is still reached
    iff total cumulative base clears the threshold at that point."""
    t = terms()
    base = [R0 * (1 + 0.4 * math.sin(i)) for i in range(T)]
    shuffled = base[:]
    random.Random(perm_seed).shuffle(shuffled)
    tot_a = sum(rbf_payments(base, t))
    tot_b = sum(rbf_payments(shuffled, t))
    assert math.isclose(tot_a, tot_b, abs_tol=CAP_TOL)   # totals identical


# ── P4 ───────────────────────────────────────────────────────────────────────

def test_P4_break_even_revenue_is_P_over_r():
    """B* = P/r, and at exactly B* the two arms tie on cumulative recovery."""
    t = terms()
    m = match_fix_a([R0] * T, t)
    B_star = m["payment"] / t.r
    flat = [B_star] * T
    fix = fix_a_payments(t, m, T)
    rbf = rbf_payments(flat, t)
    for k in (3, 6, 9):
        assert math.isclose(sum(rbf[:k]), sum(fix[:k]), rel_tol=1e-9), f"k={k}"


@pytest.mark.parametrize("mult,expect_rbf_ahead", [(1.30, True), (1.10, True),
                                                   (0.90, False), (0.70, False)])
def test_P4_sign_of_recovery_gap_follows_mean_vs_break_even(mult, expect_rbf_ahead):
    """RBF leads on recovery iff mean base > B*. Both directions asserted."""
    t = terms()
    m = match_fix_a([R0] * T, t)
    B_star = m["payment"] / t.r
    flat = [B_star * mult] * T
    rbf = rbf_payments(flat, t)
    fix = fix_a_payments(t, m, T)
    k = 6
    ahead = sum(rbf[:k]) > sum(fix[:k]) + 1e-6
    assert ahead == expect_rbf_ahead


def test_P4_corollary_break_even_equals_baseline_when_duration_is_exact():
    """f=1.20: C/(r*Bbar) = 12.0 exactly -> no rounding -> B* == Bbar, arms tie."""
    t = terms(f=1.20)
    exact = t.cap / (t.r * R0)
    assert float(exact).is_integer()
    B_star = match_fix_a([R0] * T, t)["payment"] / t.r
    assert math.isclose(B_star, R0, rel_tol=1e-12)


@pytest.mark.parametrize("f", [1.25, 1.15, 1.07])
def test_P4_corollary_integer_rounding_puts_break_even_below_baseline(f):
    """When C/(r*Bbar) is NOT an integer, N rounds UP, so B* < Bbar strictly --
    which is why RBF leads on recovery even at exactly baseline revenue.
    This is the mechanism behind the stable-scenario sign in R-012."""
    t = terms(f=f)
    exact = t.cap / (t.r * R0)
    assert not float(exact).is_integer()
    m = match_fix_a([R0] * T, t)
    B_star = m["payment"] / t.r
    assert m["term"] == math.ceil(exact)
    assert B_star < R0                       # strictly below baseline
    # and therefore RBF is strictly ahead on cumulative recovery at baseline
    rbf = rbf_payments([R0] * T, t)
    fix = fix_a_payments(t, m, T)
    assert sum(rbf[:6]) > sum(fix[:6])


# ── P5 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("omega", [1.0, 0.95, 0.9, 0.8, 0.7, 0.5])
@pytest.mark.parametrize("path", PATHS[:8])
def test_P5_recovery_scales_exactly_with_omega_while_uncapped(omega, path):
    t = terms()
    full = rbf_payments(path, t, omega=1.0)
    under = rbf_payments(path, t, omega=omega)
    cum_f = cum_u = 0.0
    for k in range(len(path)):
        cum_f += full[k]; cum_u += under[k]
        if cum_f < t.cap - CAP_TOL:                # still uncapped: exact scaling
            assert math.isclose(cum_u, omega * cum_f, rel_tol=1e-9), f"k={k}"


@pytest.mark.parametrize("omega", [0.9, 0.8, 0.7])
def test_P5_required_cumulative_base_scales_as_one_over_omega(omega):
    t = terms()
    flat = [R0] * 200
    d_full = M.duration(rbf_payments(flat, t, omega=1.0), t.cap)
    d_under = M.duration(rbf_payments(flat, t, omega=omega), t.cap)
    assert math.isclose(d_under, math.ceil(d_full / omega), abs_tol=1.0)


def test_P5_fixed_arm_is_contractually_invariant_to_omega():
    """Contractual invariance only. Says nothing about collection under distress."""
    t = terms()
    m = match_fix_a([R0] * T, t)
    assert fix_a_payments(t, m, T) == fix_a_payments(t, m, T)


# ── P6 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_P6a_multiple_is_f_whenever_cap_is_reached(path):
    t = terms()
    pay = rbf_payments(path, t)
    if sum(pay) >= t.cap - CAP_TOL:
        assert math.isclose(sum(pay) / t.A, t.f, rel_tol=1e-6)


def test_P6b_earlier_arrival_gives_strictly_higher_irr():
    """Two streams with the SAME total but earlier arrival -> higher IRR."""
    t = terms()
    fast = rbf_payments([R0 * 2] * T, t)
    slow = rbf_payments([R0 * 0.5] * T, t)
    assert math.isclose(sum(fast), sum(slow), abs_tol=CAP_TOL)   # same total
    irr_fast = solve_apr(t.A, fast)         # A-9: full vector, zeros included
    irr_slow = solve_apr(t.A, slow)
    assert irr_fast > irr_slow


def test_P6_cost_is_monotone_increasing_in_f():
    flat = [R0] * T
    prev = -1.0
    for f in (1.05, 1.10, 1.15, 1.20, 1.25, 1.30):
        t = terms(f=f)
        total = sum(rbf_payments(flat, t))
        assert total > prev
        prev = total


def test_P6_apr_is_not_a_contract_property():
    """Same (A, r, f); different paths; different APR. This is why quoting a
    single 'RBF APR' as intrinsic was wrong."""
    t = terms()
    a = solve_apr(t.A, rbf_payments([R0 * 2] * T, t))    # A-9: full vector
    b = solve_apr(t.A, rbf_payments([R0 * 0.6] * T, t))
    assert not math.isclose(a, b, rel_tol=0.05)


# ── P7 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_P7_incomplete_iff_cumulative_below_threshold(path):
    t = terms()
    pay = rbf_payments(path, t)
    incomplete = M.incomplete_recovery(pay, t.cap)
    assert incomplete == int(sum(path) < t.cap / t.r - CAP_TOL / t.r)


@pytest.mark.parametrize("c", [4, 7, 10, 13, 20])
def test_P7a_closure_is_absorbing(c):
    """After closure, cumulative base is frozen: extending the horizon cannot
    recover anything more."""
    t = terms()
    short = [R0] * c + [0.0] * (T - c)
    long_ = [R0] * c + [0.0] * (T * 3 - c)
    assert math.isclose(sum(rbf_payments(short, t)), sum(rbf_payments(long_, t)),
                        abs_tol=CAP_TOL)
    expected_incomplete = (c * R0) < t.cap / t.r
    assert bool(M.incomplete_recovery(rbf_payments(short, t), t.cap)) == expected_incomplete


@pytest.mark.parametrize("floor_frac", [0.5, 0.3, 0.1, 0.02])
def test_P7_bounded_away_from_zero_is_SUFFICIENT_for_completion(floor_frac):
    """Revenue bounded below by a POSITIVE CONSTANT => cumulative sum diverges
    linearly => cap always eventually reached.

    NOTE the exact scope: this tests 'bounded away from zero', which is
    SUFFICIENT but NOT NECESSARY. It is emphatically NOT a test that 'positive
    revenue suffices' -- see the geometric-decay tests below, where revenue is
    positive forever and the cap is never reached."""
    t = terms()
    needed = t.cap / t.r
    horizon = int(needed / (R0 * floor_frac)) + 5
    path = [R0 * floor_frac] * horizon
    assert M.incomplete_recovery(rbf_payments(path, t), t.cap) == 0


# ── P7 general criterion: completion depends on CUMULATIVE LIFETIME revenue ──
# rho* = 1 - r*B0/(F*A).  With A=B0=100M, F=1.20, r=0.10  ->  rho* = 11/12.

def geometric(B0, rho, n):
    """B_t = B0 * rho^t.

    Horizon note: rho^n underflows to exactly 0.0 in IEEE-754 double once
    n*ln(rho) < -745 (e.g. 0.5^5000). That is a floating-point artifact, not
    the mathematics -- the terms are positive for all finite n. Tests that
    assert strict positivity therefore use a horizon inside representable
    range; because the series converges geometrically, the partial sum is
    already within float precision of S_inf long before that point."""
    return [B0 * rho ** k for k in range(n)]


def geometric_safe_n(rho, cap_n=5000):
    """Largest n <= cap_n with rho^n still strictly representable."""
    if rho >= 1.0:
        return cap_n
    return min(cap_n, int(-700.0 / math.log(rho)))


def test_P7_geometric_threshold_rho_star_is_one_minus_r_B0_over_FA():
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    assert math.isclose(rho_star, 11 / 12, rel_tol=1e-12)


@pytest.mark.parametrize("rho", [0.50, 0.75, 0.85, 0.90])
def test_P7_fast_geometric_decay_NEVER_completes_despite_positive_revenue(rho):
    """THE CORRECTION. Revenue is strictly positive in every one of 5,000
    months and still the cap is never reached, because the lifetime sum is
    FINITE and below F*A/r. No zero month, no maturity, no horizon limit."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    assert rho < rho_star
    path = geometric(R0, rho, geometric_safe_n(rho))
    assert all(x > 0 for x in path)                       # positive throughout
    assert math.isclose(sum(path), R0 / (1 - rho), rel_tol=1e-6)   # finite sum
    assert t.r * sum(path) < t.cap                        # below the threshold
    assert M.incomplete_recovery(rbf_payments(path, t), t.cap) == 1


@pytest.mark.parametrize("rho", [0.95, 0.97, 0.99])
def test_P7_slow_geometric_decay_DOES_complete(rho):
    """Above rho*, the finite lifetime sum still clears the threshold."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    assert rho > rho_star
    path = geometric(R0, rho, geometric_safe_n(rho))
    assert all(x > 0 for x in path)
    assert t.r * sum(path) >= t.cap
    assert M.incomplete_recovery(rbf_payments(path, t), t.cap) == 0


def test_P7_indexing_convention_B0_enters_at_full_weight():
    """Pin the convention the threshold depends on: geometric() runs k in
    range(n), so B_t = B0*rho^t starting at t=0 and S_inf = B0/(1-rho).
    A t=1 start would change rho*, so this is asserted, not assumed."""
    path = geometric(R0, 0.9, 4)
    assert math.isclose(path[0], R0)
    assert math.isclose(path[1], R0 * 0.9)
    assert math.isclose(sum(geometric(R0, 0.9, 4000)), R0 / (1 - 0.9), rel_tol=1e-9)


def test_P7_at_exactly_rho_star_infinite_sum_equals_the_cap():
    """r * S_inf == F*A exactly at the boundary."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    assert math.isclose(rho_star, 11 / 12, rel_tol=1e-12)
    assert math.isclose(t.r * (R0 / (1 - rho_star)), t.f * t.A, rel_tol=1e-12)
    assert math.isclose(t.r * (R0 / (1 - rho_star)), t.cap, rel_tol=1e-12)


@pytest.mark.parametrize("T", [12, 24, 60, 100, 150, 200])
def test_P7_at_rho_star_every_finite_partial_sum_is_strictly_below_the_cap(T):
    """THE BOUNDARY CORRECTION. At rho = rho*, S_T < S_inf strictly for every
    finite T because rho^(T+1) > 0. Repayment approaches the cap asymptotically
    and never attains it, so the contract does NOT complete in finite time."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    S_T = R0 * (1 - rho_star ** (T + 1)) / (1 - rho_star)
    assert t.r * S_T < t.cap
    assert t.cap - t.r * S_T > 0


def test_P7_at_rho_star_does_not_complete_at_practically_relevant_horizons():
    """Asserted against the engine, not only the closed form."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    for n in (24, 60, 120, 200):
        path = geometric(R0, rho_star, n)
        assert all(x > 0 for x in path)
        assert M.incomplete_recovery(rbf_payments(path, t), t.cap) == 1, f"n={n}"


def test_P7_completion_inequality_is_STRICT_just_above_and_just_below():
    """rho > rho* completes; rho < rho* never does. Straddle by 0.5%."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    below, above = rho_star * 0.995, rho_star * 1.005
    assert below < rho_star < above
    p_below = geometric(R0, below, geometric_safe_n(below))
    p_above = geometric(R0, above, geometric_safe_n(above))
    assert all(x > 0 for x in p_below) and all(x > 0 for x in p_above)
    assert t.r * (R0 / (1 - below)) < t.cap
    assert t.r * (R0 / (1 - above)) > t.cap
    assert M.incomplete_recovery(rbf_payments(p_below, t), t.cap) == 1
    assert M.incomplete_recovery(rbf_payments(p_above, t), t.cap) == 0


@pytest.mark.parametrize("eps,expected_flip", [(1.0, 213), (0.5, 221), (0.01, 266)])
def test_P7_operational_completion_flip_point_by_epsilon(eps, expected_flip):
    """MATHEMATICAL vs OPERATIONAL completion (spec 10.11).

    Mathematical completion: a finite T with cumulative remittances >= cap in
    exact arithmetic. At rho = rho* this NEVER occurs.

    Operational completion: remaining balance <= settlement tolerance eps.
    This DOES occur, at a month determined entirely by eps.

    The two are different concepts, not a bug and a fix.

    HISTORICAL NOTE (D-023, now applied). These flip months were once the
    engine's actual behaviour: eps = 0.5 in metrics.duration gave T = 221, while
    this module's own CAP_TOL = 1.0 gave T = 213 -- the inconsistency D-023
    identified. Under the approved correction neither value is a default any
    more: the operational layer settles in whole dong with eps = 0 by
    construction (settlement.py), and the analytical layer has no epsilon at
    all. The table below is retained as the DECLARED-POLICY SENSITIVITY it
    always should have been: if a commercial eps were ever declared, this is the
    completion month it would produce, and spec 10.11 requires reporting it
    alongside the number."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)

    def shortfall(T):
        return t.cap - t.r * R0 * (1 - rho_star ** (T + 1)) / (1 - rho_star)

    flip = next(T for T in range(1, 5000) if shortfall(T) < eps)
    assert flip == expected_flip
    assert shortfall(flip) > 0          # mathematically still incomplete
    assert shortfall(flip - 1) >= eps   # and the flip is sharp


def test_P7_mathematical_completion_never_occurs_at_rho_star_for_any_epsilon():
    """With eps = 0 (exact arithmetic) there is no finite completion month."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    for T in (24, 100, 500, 2000):
        S_T = R0 * (1 - rho_star ** (T + 1)) / (1 - rho_star)
        assert t.r * S_T < t.cap


def test_P7_engine_tolerance_is_not_a_binding_settlement_policy():
    """Evidence for D-023, retained as a REGRESSION GUARD after the correction.

    The original finding: the old 0.5 tolerance was ~8.4e6x larger than the
    float error it guarded against and changed no registered result. That claim
    is asserted here across the full adversarial path set, at the OLD default
    (0.5), the OLD test constant (1.0), the NEW float guard (1e-6) and exact
    zero. All four must agree. If a future change ever makes the tolerance
    load-bearing, this fails -- which is the point."""
    t = terms()
    for path in PATHS:
        pay = rbf_payments(path, t)
        durations = {tol: M.duration(pay, t.cap, tol=tol)
                     for tol in (1.0, 0.5, FLOAT_GUARD_VND, 0.0)}
        assert len(set(durations.values())) == 1, durations
        incompletes = {tol: M.incomplete_recovery(pay, t.cap, tol=tol)
                       for tol in (1.0, 0.5, FLOAT_GUARD_VND, 0.0)}
        assert len(set(incompletes.values())) == 1, incompletes


def test_P7_asymptotic_shortfall_is_monotone_decreasing_and_never_zero():
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    gaps = [t.cap - t.r * R0 * (1 - rho_star ** (T + 1)) / (1 - rho_star)
            for T in range(1, 300)]
    assert all(g > 0 for g in gaps)
    assert all(x > y for x, y in zip(gaps, gaps[1:]))


def test_P7_divergent_slow_decay_completes_but_takes_enormous_time():
    """Harmonic decay B_t = B0/t: strictly declining, sum DIVERGES, so
    completion is guaranteed -- needing H_n >= F*A/(r*B0) = 12, i.e. n ~ 9.1e4
    months. Divergence guarantees completion; it says nothing about useful time."""
    t = terms()
    need = t.cap / (t.r * R0)                     # = 12 harmonic units
    assert math.isclose(need, 12.0, rel_tol=1e-12)
    short = [R0 / k for k in range(1, 50_001)]
    long_ = [R0 / k for k in range(1, 200_001)]
    assert M.incomplete_recovery(rbf_payments(short, t), t.cap) == 1   # not yet
    assert M.incomplete_recovery(rbf_payments(long_, t), t.cap) == 0   # eventually


def test_P7_divergence_is_strictly_weaker_than_bounded_away_from_zero():
    """The harmonic path has no positive lower bound yet still completes, so
    the divergence criterion properly generalises the old corollary."""
    t = terms()
    path = [R0 / k for k in range(1, 200_001)]
    assert min(path) < R0 * 1e-4                    # NOT bounded away from zero
    assert M.incomplete_recovery(rbf_payments(path, t), t.cap) == 0


@pytest.mark.parametrize("rho", [0.80, 0.90])
def test_P7_fast_decay_is_not_rescued_by_extending_the_horizon(rho):
    """Unlike a horizon artifact, this failure is permanent: 10x the horizon
    recovers no additional capital beyond the finite lifetime sum."""
    t = terms()
    a = sum(rbf_payments(geometric(R0, rho, 2000), t))
    b = sum(rbf_payments(geometric(R0, rho, 20000), t))
    assert math.isclose(a, b, rel_tol=1e-9)
    assert a < t.cap


def test_P7_general_criterion_holds_across_all_adversarial_paths():
    """S_H >= F*A/r is necessary AND sufficient, on every path in the suite
    plus the decaying families."""
    t = terms()
    threshold = t.f * t.A / t.r
    extra = [geometric(R0, r_, 500) for r_ in (0.5, 0.9, 0.95, 0.99)]
    extra += [[R0 / k for k in range(1, 501)]]
    for path in PATHS + extra:
        complete = sum(rbf_payments(path, t)) >= t.cap - CAP_TOL
        assert complete == (sum(path) >= threshold - CAP_TOL / t.r)


def test_P7_maturity_truncates_and_can_create_incomplete_recovery():
    t_none = terms()
    t_mat = terms(terminal_maturity=8)
    path = [R0 * 0.6] * T
    assert M.incomplete_recovery(rbf_payments(path, t_none), t_none.cap) == 0
    assert M.incomplete_recovery(rbf_payments(path, t_mat), t_mat.cap) == 1


# ── P-RBF-G ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_P_rbfg_payment_never_exceeds_the_proportional_amount(path):
    """THE proposition, stated as its exact invariant: with mu=0.25 <= h=0.50
    the FLOOR can never activate, so RBF-G never pays more than r*B_t in any
    month. This is the direct test and is free of cap-timing confounds.

    (Two earlier versions of this test were wrong. The first asserted RBF-G ==
    RBF on every path -- too strong, because the CEILING is a separate rule
    that does bind on spiky paths. The second asserted RBF-G <= RBF pointwise
    -- also wrong, because a ceiling-reduced early payment leaves more residual
    under the cap, so RBF-G can pay more in a LATER month than RBF, which has
    already capped out. Both were test errors. The proposition -- the floor
    never activates -- survived unchanged, and is what is asserted here.)"""
    t = terms()
    assert t.p_min_mult <= t.hardship
    for i, (g, b) in enumerate(zip(rbf_g_payments(path, t, R0), path)):
        assert g <= t.r * b + 1e-6, f"floor activated at month {i}: {g} > r*B={t.r*b}"


@pytest.mark.parametrize("path", PATHS)
def test_P_rbfg_cumulative_never_leads_plain_rbf(path):
    """Cumulative form of the same invariant: with the floor dead, RBF-G can
    only ever be slower, never faster, than plain RBF."""
    t = terms()
    cg = cb = 0.0
    for i, (g, b) in enumerate(zip(rbf_g_payments(path, t, R0), rbf_payments(path, t))):
        cg += g; cb += b
        assert cg <= cb + 1e-6, f"RBF-G led at month {i}: {cg} > {cb}"


@pytest.mark.parametrize("path", PATHS)
def test_P_rbfg_reductions_are_attributable_to_the_ceiling(path):
    """Any month where RBF-G pays strictly less than the proportional amount
    must have the ceiling binding, or the cap residual binding -- never a floor."""
    t = terms()
    g_pay = rbf_g_payments(path, t, R0)
    paid = 0.0
    for i, g in enumerate(g_pay):
        prop = t.r * path[i]
        residual = t.cap - paid
        if g < prop - 1e-6:
            ceiling_binds = prop > t.p_max_mult * t.r * R0 - 1e-6
            cap_binds = residual <= prop + 1e-6
            assert ceiling_binds or cap_binds, f"unexplained reduction at month {i}"
        paid += g


def test_P_rbfg_ceiling_did_not_bind_in_the_baseline_scenarios():
    """Explains why baseline_v2 showed RBF-G identical to RBF: revenue never
    reached 2x R0 there. The equality was scenario-specific for the ceiling and
    universal only for the floor."""
    t = terms()
    for path in ([R0] * T, [R0 * 0.6] * T, [R0 * 1.4] * T):
        assert rbf_g_payments(path, t, R0) == rbf_payments(path, t)


def test_P_rbfg_floor_becomes_reachable_only_when_mu_exceeds_h():
    """Documents the corrected condition WITHOUT adopting it into the analysis."""
    t_dead = terms(p_min_mult=0.25, hardship=0.50)
    t_live = terms(p_min_mult=0.80, hardship=0.50)
    path = [R0 * 0.6] * T                      # above hardship, below 0.80*R0
    assert rbf_g_payments(path, t_dead, R0) == rbf_payments(path, t_dead)
    assert rbf_g_payments(path, t_live, R0) != rbf_payments(path, t_live)
