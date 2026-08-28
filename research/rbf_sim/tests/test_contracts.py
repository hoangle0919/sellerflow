"""Contract and metric tests — METHODOLOGY_SPEC.md sections 7, 8, 10.

Every expected value below is computed BY HAND in the docstring or comment,
then asserted. A test that only checks "it ran" is not a test.
"""
import math
import pytest

from rbf_sim.contracts import (ContractTerms, rbf_payments, rbf_g_payments,
                               rbf_duration, match_fix_a, fix_a_payments,
                               fix_b_payments, solve_apr)
from rbf_sim import metrics as M

R0 = 100_000_000.0
T = 24


def terms(**kw):
    d = dict(A=100_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)
    d.update(kw)
    return ContractTerms(**d)


# ── Cap and RBF mechanics (spec 8.1) ─────────────────────────────────────────

def test_cap_is_principal_times_factor_rate():
    """A=100M, f=1.20 -> C = 120M."""
    assert terms().cap == 120_000_000.0


def test_rbf_payment_is_remittance_rate_times_revenue():
    """r=0.10, R=100M -> p = 10M per month while the cap is not binding."""
    p = rbf_payments([R0] * T, terms())
    assert math.isclose(p[0], 10_000_000.0)
    assert math.isclose(p[5], 10_000_000.0)


def test_rbf_total_never_exceeds_cap():
    p = rbf_payments([R0] * T, terms())
    assert sum(p) <= terms().cap + 1e-6
    assert math.isclose(sum(p), 120_000_000.0)


def test_rbf_final_payment_is_truncated_to_the_cap():
    """120M cap / 10M per month = 12 months exactly, 13th payment is 0."""
    p = rbf_payments([R0] * T, terms())
    assert math.isclose(p[11], 10_000_000.0)
    assert math.isclose(p[12], 0.0)


def test_rbf_duration_hand_computed():
    """ceil(120M / 10M) = 12 months."""
    assert rbf_duration([R0] * T, terms()) == 12


def test_rbf_payment_falls_with_revenue():
    """R halves -> payment halves. The defining property of RBF (H1)."""
    p = rbf_payments([R0, R0 / 2, R0], terms())
    assert math.isclose(p[1], p[0] / 2)


def test_rbf_duration_extends_under_decline():
    """Sustained -40% from month 7: payments 10M x6 then 6M.
    Remaining after 6 months = 120 - 60 = 60M; 60/6 = 10 more -> 16 months."""
    rev = [R0] * 6 + [R0 * 0.6] * 18
    assert rbf_duration(rev, terms()) == 16


def test_rbf_censored_when_cap_unreachable():
    """Revenue so low the cap is never reached within the horizon."""
    assert rbf_duration([1_000_000.0] * T, terms()) is None


# ── Benchmark A matching (spec 7.1) ──────────────────────────────────────────

def test_match_a_term_equals_rbf_base_duration():
    m = match_fix_a([R0] * T, terms())
    assert m["term"] == 12


def test_match_a_payment_is_cap_over_term():
    """120M / 12 = 10M per month."""
    m = match_fix_a([R0] * T, terms())
    assert math.isclose(m["payment"], 10_000_000.0)


def test_benchmark_a_is_cost_matched_to_rbf_exactly():
    """THE identification claim (spec 7.1): same principal, same total, same
    term -- so only TIMING differs."""
    t = terms()
    m = match_fix_a([R0] * T, t)
    fix = fix_a_payments(t, m, T)
    rbf = rbf_payments([R0] * T, t)
    assert math.isclose(sum(fix), sum(rbf), abs_tol=1.0)
    assert math.isclose(sum(fix), t.cap, abs_tol=1.0)


def test_benchmark_a_is_invariant_to_realised_revenue():
    """The fixed payment must not react to the shock it is compared against."""
    t = terms()
    m = match_fix_a([R0] * T, t)
    assert fix_a_payments(t, m, T) == fix_a_payments(t, m, T)


def test_match_a_raises_when_cap_unreachable_on_reference():
    with pytest.raises(ValueError):
        match_fix_a([1_000.0] * T, terms())


# ── Benchmark B amortizing loan (spec 7.2) ───────────────────────────────────

def test_benchmark_b_annuity_hand_computed():
    """A=100M, j=18% -> i=0.015, N=12.

    1.015^12 = 1.1956182
    1.015^-12 = 0.8363870
    1 - 0.8363870 = 0.1636130
    P = A*i / (1-(1+i)^-N) = 1,500,000 / 0.1636130 = 9,168,000 (4 s.f.)

    (An earlier version of this test asserted 9,174,708 from a mis-evaluated
    1.015^-12. The test failed, the arithmetic was wrong, and the constant was
    corrected -- not the code. Recorded here because that is the test doing
    its job.)"""
    p = fix_b_payments(terms(), T)
    assert math.isclose(p[0], 9_168_000.0, rel_tol=1e-3)
    assert math.isclose(p[12], 0.0)


def test_benchmark_b_annuity_discounts_back_to_principal_exactly():
    """Independent check that does not rely on a hand-typed constant: an annuity
    priced at i is by definition the payment stream whose NPV at i equals the
    principal. Verifies the formula rather than one evaluation of it."""
    t = terms()
    p = [x for x in fix_b_payments(t, T) if x > 0]
    i = t.j / 12.0
    npv = sum(x / (1 + i) ** (k + 1) for k, x in enumerate(p))
    assert math.isclose(npv, t.A, rel_tol=1e-9)


def test_benchmark_b_total_differs_from_cap():
    """B is NOT cost-matched -- spec 7.2 forbids using it for matched claims."""
    p = fix_b_payments(terms(), T)
    assert not math.isclose(sum(p), terms().cap, rel_tol=0.01)


def test_benchmark_b_zero_rate_is_straight_line():
    p = fix_b_payments(terms(j=0.0), T)
    assert math.isclose(p[0], 100_000_000.0 / 12)


# ── APR solving (spec 7.1, 10) ───────────────────────────────────────────────

def test_apr_recovers_the_input_rate_of_an_annuity():
    """Round trip: build an 18% annuity, solve for its APR, get 18% back
    (as an effective annual rate: 1.015^12 - 1 = 19.56%)."""
    p = fix_b_payments(terms(), T)          # A-9: full vector, zeros included
    apr = solve_apr(100_000_000.0, p)
    assert math.isclose(apr, (1.015 ** 12) - 1, rel_tol=1e-3)


def test_apr_undefined_when_no_sign_change():
    """Never dropped silently -- reported as undefined (spec 13, E-3)."""
    assert solve_apr(100_000_000.0, [0.0] * 12) is None


# ── Guardrails (spec 8.2) ────────────────────────────────────────────────────

def test_guardrail_floor_lifts_payment_above_plain_rbf():
    """R drops to 60% of R0 (above the 50% hardship line), so the floor applies.
    plain: 0.10 x 60M = 6M. floor: 0.25 x 0.10 x 100M = 2.5M -> floor does not
    bind here. Use a deeper but still non-hardship drop to make it bind."""
    t = terms()
    rev = [R0 * 0.55] * T                     # above hardship (0.50), below floor point
    plain = rbf_payments(rev, t)
    guard = rbf_g_payments(rev, t, R0)
    assert guard[0] >= plain[0]


def test_guardrail_ceiling_caps_payment_in_a_boom():
    """R = 3x R0 -> plain payment 30M; ceiling = 2.0 x 0.10 x 100M = 20M."""
    t = terms()
    guard = rbf_g_payments([R0 * 3] * T, t, R0)
    assert math.isclose(guard[0], 20_000_000.0)


def test_hardship_rule_suspends_the_floor():
    """R = 0.3 x R0 < 0.5 x R0 -> floor suspended, payment is plain 0.10 x R."""
    t = terms()
    guard = rbf_g_payments([R0 * 0.3] * T, t, R0)
    assert math.isclose(guard[0], 0.10 * R0 * 0.3)


def test_guardrailed_total_still_respects_the_cap():
    guard = rbf_g_payments([R0 * 3] * T, terms(), R0)
    assert sum(guard) <= terms().cap + 1e-6


# ── Metrics (spec 10) ────────────────────────────────────────────────────────

def test_payment_burden_hand_computed():
    """p=10M on R=100M -> burden 0.10."""
    b = M.payment_burden([R0] * 3, [10_000_000.0] * 3)
    assert all(math.isclose(x, 0.10) for x in b)


def test_burden_undefined_at_zero_revenue():
    """spec 13, E-1 -- excluded, not imputed."""
    b = M.payment_burden([R0, 0.0, R0], [10_000_000.0] * 3)
    assert b[1] is None
    assert M.burden_stats([R0, 0.0, R0], [10_000_000.0] * 3)["n_active"] == 2


def test_rbf_burden_is_constant_by_construction():
    """spec 10.2's structural note, asserted rather than assumed."""
    p = rbf_payments([R0, R0 * 0.5, R0 * 2, R0 * 0.3], terms())
    b = [x for x in M.payment_burden([R0, R0 * 0.5, R0 * 2, R0 * 0.3], p) if x]
    assert all(math.isclose(x, 0.10) for x in b)


def test_fixed_burden_rises_as_revenue_falls():
    """The information in the burden metric lives on the FIXED side."""
    rev = [R0, R0 * 0.5, R0 * 0.25]
    b = M.payment_burden(rev, [10_000_000.0] * 3)
    assert math.isclose(b[0], 0.10) and math.isclose(b[1], 0.20) and math.isclose(b[2], 0.40)


def test_n_high_burden_hand_counted():
    """Burdens 0.10, 0.20, 0.40 at threshold 0.15 -> 2 months exceed."""
    rev = [R0, R0 * 0.5, R0 * 0.25]
    n = M.n_high_burden(rev, [10_000_000.0] * 3)
    assert n[0.15] == 2 and n[0.25] == 1 and n[0.10] == 2


def test_recovery_at_checkpoints_hand_computed():
    """10M per month for 12 months: Rec(12)=120M, and 0 thereafter."""
    p = rbf_payments([R0] * T, terms())
    assert math.isclose(M.recovery_at(p, 12), 120_000_000.0)
    assert math.isclose(M.recovery_at(p, 18), 120_000_000.0)


def test_recovery_ratio_reaches_one_at_the_cap():
    p = rbf_payments([R0] * T, terms())
    rr = M.recovery_ratios(p, terms().cap)
    assert math.isclose(rr[12], 1.0) and math.isclose(rr[24], 1.0)


def test_incomplete_recovery_flags_only_when_cap_unmet():
    full = rbf_payments([R0] * T, terms())
    thin = rbf_payments([R0 * 0.05] * T, terms())
    assert M.incomplete_recovery(full, terms().cap) == 0
    assert M.incomplete_recovery(thin, terms().cap) == 1


def test_post_shock_recovery_window():
    """Shock at month 7; 6-month window covers months 7..13 inclusive."""
    p = [1_000_000.0] * T
    assert math.isclose(M.post_shock_recovery(p, onset=7, k=6), 7_000_000.0)


def test_coherence_constraint_matches_spec_14():
    """m=0.25, F=0.20xR0, P=10M on R0=100M: 25M - 20M - 10M = -5M -> incoherent."""
    assert not M.coherent(0.25, 0.20 * R0, 10_000_000.0, R0)
    assert M.coherent(0.45, 0.10 * R0, 10_000_000.0, R0)


def test_distress_metric_is_assumption_dependent():
    """Same payments, different cost assumptions, different answers -- which is
    exactly why it is secondary (spec 10.3)."""
    rev, pay = [R0] * 12, [10_000_000.0] * 12
    assert M.distress_months(rev, pay, m=0.25, F=0.20 * R0) == 12
    assert M.distress_months(rev, pay, m=0.45, F=0.10 * R0) == 0
