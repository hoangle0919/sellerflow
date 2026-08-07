"""Tests for the centralized VND settlement policy (D-023, spec 10.11).

Two things are under test, and they are deliberately different things:

  1. the OPERATIONAL layer really is integer dong, really is clipped to the
     contractual cap, and really does settle exactly (epsilon 0);
  2. the ANALYTICAL layer is unchanged by any of it -- the propositions in
     DERIVATIONS.md are statements about exact arithmetic and must not move.

Expected values are hand-derived, never read back from the implementation.
"""
import math
import random
from decimal import Decimal, ROUND_HALF_UP

import pytest

from rbf_sim.contracts import ContractTerms, rbf_payments
from rbf_sim import metrics as M
from rbf_sim.settlement import (FLOAT_GUARD_VND, VND_ROUNDING, SettlementPolicy,
                                EXACT_SETTLEMENT, to_vnd, settle_payments,
                                mathematically_complete, operationally_complete,
                                settlement_duration)

R0 = 100_000_000.0
T = 36


def terms(**kw):
    d = dict(A=100_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)
    d.update(kw)
    return ContractTerms(**d)


def paths(n=25, seed=7):
    """Same adversarial variety as the derivation tests: flat, trending,
    spiky, seasonal, zero months."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        kind = rng.choice(("flat", "trend", "spiky", "seasonal", "zeros"))
        base = rng.uniform(0.3, 2.0) * R0
        p = []
        for t in range(T):
            if kind == "flat":
                v = base
            elif kind == "trend":
                v = base * (1 + rng.uniform(-0.04, 0.04)) ** t
            elif kind == "spiky":
                v = base * (4.0 if rng.random() < 0.1 else rng.uniform(0.2, 1.0))
            elif kind == "seasonal":
                v = base * (1 + 0.6 * math.sin(2 * math.pi * t / 12))
            else:
                v = 0.0 if rng.random() < 0.25 else base
            p.append(max(0.0, v))
        out.append(p)
    return out


PATHS = paths()


# ── the rounding rule is the DOCUMENTED one, not Python's default ────────────

def test_to_vnd_is_half_up_not_bankers():
    """Python's round() is banker's rounding: round(0.5)==0, round(2.5)==2.
    The documented rule is HALF-UP. If someone swaps Decimal for round(), the
    rule silently changes and these fail."""
    assert to_vnd(0.5) == 1
    assert to_vnd(1.5) == 2
    assert to_vnd(2.5) == 3          # banker's would give 2
    assert to_vnd(-0.5) == -1        # half-up is away from zero at .5
    assert round(2.5) == 2           # documents the trap being avoided


def test_to_vnd_returns_whole_dong():
    for x in (0.0, 1.4, 1.6, 12_345_678.9, 1e9 + 0.499):
        v = to_vnd(x)
        assert isinstance(v, int)
        assert v == int(v)


def test_to_vnd_matches_decimal_half_up_reference():
    for x in (123.4, 999.5, 1_000_000.5, 7.05, 0.49999):
        expect = int(Decimal(str(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        assert to_vnd(x) == expect


def test_default_rounding_constant_is_half_up():
    assert VND_ROUNDING == ROUND_HALF_UP


# ── the policy object is explicit and refuses float-shaped epsilons ──────────

def test_default_policy_is_exact():
    assert EXACT_SETTLEMENT.epsilon_vnd == 0
    assert "exact by construction" in EXACT_SETTLEMENT.describe()


def test_fractional_epsilon_is_rejected():
    """A fractional epsilon is precisely the workaround D-023 removes."""
    with pytest.raises(ValueError):
        SettlementPolicy(epsilon_vnd=0.5)


def test_negative_epsilon_is_rejected():
    with pytest.raises(ValueError):
        SettlementPolicy(epsilon_vnd=-1)


def test_declared_nonzero_epsilon_must_announce_itself():
    """spec 10.11: a completion month derived from a non-zero eps may never be
    reported bare. The policy's own description carries the warning."""
    p = SettlementPolicy(epsilon_vnd=1)
    assert "DECLARED" in p.describe()
    assert "1 VND" in p.describe()


# ── the cap invariant: the contract's actual promise ────────────────────────

@pytest.mark.parametrize("path", PATHS)
def test_settled_payments_are_all_whole_dong(path):
    t = terms()
    for p in settle_payments(path, t.r, t.cap):
        assert isinstance(p, int)


@pytest.mark.parametrize("path", PATHS)
def test_settled_total_never_exceeds_the_cap(path):
    """Rounding happens BEFORE clipping, so rounding can never breach the cap.
    This is the invariant a borrower is entitled to: you never repay more than
    f x A, not even by one dong."""
    t = terms()
    cap_vnd = to_vnd(t.cap)
    assert sum(settle_payments(path, t.r, t.cap)) <= cap_vnd


@pytest.mark.parametrize("path", PATHS)
def test_settled_payments_are_never_negative(path):
    t = terms()
    assert all(p >= 0 for p in settle_payments(path, t.r, t.cap))


def test_final_payment_is_an_exact_remainder_not_a_rounded_one():
    """The clip is applied last, so the completing payment closes the balance
    to zero exactly -- no residual dong, no overshoot."""
    t = terms()
    flat = [R0] * T                       # completes comfortably
    pay = settle_payments(flat, t.r, t.cap)
    cap_vnd = to_vnd(t.cap)
    assert sum(pay) == cap_vnd
    d = settlement_duration(pay, cap_vnd)
    assert d is not None
    assert sum(pay[:d]) == cap_vnd        # settled exactly at the completion month
    assert all(p == 0 for p in pay[d:])   # and nothing is taken afterwards


def test_settlement_is_exact_so_no_epsilon_is_needed():
    """eps = 0 completes. If integer arithmetic were wrong, this would need slack."""
    t = terms()
    pay = settle_payments([R0] * T, t.r, t.cap)
    assert operationally_complete(pay, to_vnd(t.cap), EXACT_SETTLEMENT)
    assert (to_vnd(t.cap) - sum(pay)) == 0


def test_zero_revenue_never_settles_and_is_censored_not_imputed():
    t = terms()
    pay = settle_payments([0.0] * T, t.r, t.cap)
    assert sum(pay) == 0
    assert settlement_duration(pay, to_vnd(t.cap)) is None
    assert not operationally_complete(pay, to_vnd(t.cap))


def test_underreporting_scales_settled_payments_before_the_cap_binds():
    """omega enters the operational layer the same way it enters the analytical
    one (spec 10.9): the provider observes omega*R_t."""
    t = terms()
    path = [R0 * 0.2] * T                        # small, so the cap never binds
    full = settle_payments(path, t.r, t.cap, omega=1.0)
    under = settle_payments(path, t.r, t.cap, omega=0.8)
    assert sum(full) < to_vnd(t.cap)             # cap genuinely not binding
    for a, b in zip(full, under):
        assert b == to_vnd(0.8 * a) or abs(b - 0.8 * a) <= 1


# ── the two completion concepts stay separate (spec 10.11) ──────────────────

def test_mathematical_completion_has_no_epsilon_at_rho_star():
    """P7 boundary. rho = rho* approaches the cap asymptotically and NEVER
    attains it. The analytical layer must say so at every finite horizon --
    this is the property an epsilon would destroy."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    assert math.isclose(rho_star, 11 / 12, rel_tol=1e-12)
    for H in (24, 100, 500, 2000):
        path = [R0 * rho_star ** k for k in range(H)]
        assert not mathematically_complete(rbf_payments(path, t), t.cap)


def test_operational_and_mathematical_completion_can_disagree_by_design():
    """At rho* a DECLARED eps of 1 VND settles in finite time while the
    mathematics never does. That is not a bug -- it is why spec 10.11 requires
    naming the concept. Both statements are true of different objects."""
    t = terms()
    rho_star = 1 - (t.r * R0) / (t.f * t.A)
    H = 400
    path = [R0 * rho_star ** k for k in range(H)]
    assert not mathematically_complete(rbf_payments(path, t), t.cap)

    cap_vnd = to_vnd(t.cap)
    declared = SettlementPolicy(epsilon_vnd=1)
    pay = settle_payments(path, t.r, t.cap)
    assert settlement_duration(pay, cap_vnd, declared) is not None


def test_mathematical_completion_is_exact_at_the_boundary():
    """Cumulative == cap exactly must count as complete: the definition is
    `>=`, and an epsilon-free implementation must not miss equality."""
    t = terms()
    cap_vnd = to_vnd(t.cap)
    assert mathematically_complete([cap_vnd], t.cap)
    assert not mathematically_complete([cap_vnd - 1], t.cap)


# ── agreement with the analytical layer: the "0 of 10 scenarios" claim ──────

@pytest.mark.parametrize("path", PATHS)
def test_settlement_duration_agrees_with_analytical_duration(path):
    """The correction must not move any registered result. Integer-dong
    settlement and the float analytical layer must report the same completion
    month on every path."""
    t = terms()
    analytical = M.duration(rbf_payments(path, t), t.cap)
    operational = settlement_duration(settle_payments(path, t.r, t.cap),
                                      to_vnd(t.cap))
    assert analytical == operational


@pytest.mark.parametrize("path", PATHS)
def test_settled_total_matches_float_total_within_one_dong(path):
    """Quantization moves money by less than the unit of account, by definition."""
    t = terms()
    float_total = sum(rbf_payments(path, t))
    settled_total = sum(settle_payments(path, t.r, t.cap))
    assert abs(settled_total - float_total) <= len(path)


# ── the float guard is a numerical guard, not money ─────────────────────────

def test_float_guard_is_far_below_the_unit_of_account():
    """A guard that could absorb a real monetary shortfall would be a
    settlement policy in disguise. 1e-6 VND cannot: the smallest amount of
    money that exists is 1 VND, a million times larger."""
    assert FLOAT_GUARD_VND < 1
    assert FLOAT_GUARD_VND * 1_000_000 <= 1


def test_float_guard_exceeds_measured_representation_error():
    """Measured worst-case per-payment deviation from exact rational arithmetic
    is ~9.24e-8 VND (D-023, re-measured over 3,000 paths in this repository).
    The guard must cover it with margin, and nothing more."""
    assert FLOAT_GUARD_VND > 9.24e-8
    assert FLOAT_GUARD_VND < 1e-4


def test_no_module_reintroduces_a_half_dong_default():
    """Regression guard for the specific defect: 0.5 and 1.0 tolerance defaults
    scattered across modules. Defaults must now be the one central constant."""
    import inspect
    from rbf_sim import contracts as K
    for fn in (M.duration, M.incomplete_recovery, K.rbf_duration):
        default = inspect.signature(fn).parameters["tol"].default
        assert default == FLOAT_GUARD_VND, f"{fn.__name__} has tol={default}"
