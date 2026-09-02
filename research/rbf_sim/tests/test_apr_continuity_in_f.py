"""APR is piecewise continuous in the cap factor, not discrete (D-056).

`DERIVATIONS.md` P6 asserted, until this suite existed, that "APR depends on `f`
*and* on the integer duration, which moves in steps, so the achievable APRs form
a discrete set and a given target APR generally has **no** `f` attaining it
exactly."

That is false, and the reason is visible in the contract definition. The
terminal payment is clipped to whatever remains of the cap:

    p_t = min(r·B_t, C − Σ_{s<t} p_s),      C = A·f

Inside a region of `f` where the paying term does not change, that final residue
is a continuous function of `f`. So the payment vector moves continuously, and
so does its internal rate of return. Duration integrality introduces **kinks**
where the term steps — it makes the map piecewise. It does not put gaps in the
range.

The practical consequence is that an exact reference-path solution to the
benchmark APR *does* exist. The registered `f* = 1.0945` is not that root; it is
the nearest point on the 0.0005-step grid that `run_validation.py` actually
searched. That distinction is the whole correction: the residual is a property
of **the grid**, not of attainability.

Nothing here changes the engine, a generator, or a registered artifact. These
tests read the same reference path the pricing section reads and assert
properties of it.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rbf_sim.contracts import (  # noqa: E402
    ContractTerms, fix_b_payments, rbf_payments, solve_apr,
)
from rbf_sim.generator import PathParams, reference_base_path  # noqa: E402

R0 = 185_000_000.0
BASE = dict(A=185_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)

#: The grid `run_validation.py::sec2` sweeps: 1.0005 … 1.4000, step 0.0005.
GRID_STEP = 0.0005
GRID = [1.0 + i * GRID_STEP for i in range(1, 801)]

#: Registered result. Must not move.
REGISTERED_F_STAR = 1.0945
REGISTERED_APR = 0.1953765648184853

#: The exact continuous root on the reference path, located by bisection.
EXACT_F = 1.0946206626769461


def _ref():
    return reference_base_path(PathParams(R0=R0), ContractTerms(**BASE))


def _paying(v):
    return sum(1 for x in v if x > 0)


def _apr_and_term(f, ref):
    t = ContractTerms(**{**BASE, "f": f})
    pay = rbf_payments(ref, t)
    return solve_apr(t.A, pay), _paying(pay), pay


@pytest.fixture(scope="module")
def ref():
    return _ref()


@pytest.fixture(scope="module")
def benchmark():
    return solve_apr(BASE["A"], fix_b_payments(ContractTerms(**BASE), 24))


# ── 1. the exact continuous root ────────────────────────────────────────────

def test_an_exact_reference_path_root_exists(ref, benchmark):
    """The counterexample that falsifies the discreteness claim.

    If achievable APRs were a discrete set, no `f` would hit the benchmark. One
    does, to floating-point precision.
    """
    apr, term, _ = _apr_and_term(EXACT_F, ref)

    assert term == 12, "the exact root must lie in the 12-month region"
    assert apr == pytest.approx(benchmark, abs=1e-13), (
        f"f = {EXACT_F} gives APR {apr!r} against benchmark {benchmark!r}; "
        f"gap {apr - benchmark:.3e}")
    # Tight enough to be floating-point noise rather than a real residual.
    assert abs(apr - benchmark) < 1e-14


def test_the_root_is_findable_by_bisection_not_just_asserted(ref, benchmark):
    """Re-derive it rather than trusting the constant above.

    A hard-coded root proves nothing if the engine moves under it. Bisection is
    only valid because the function is continuous on the bracket — which is the
    property under test.
    """
    lo, hi = 1.0940, 1.0950
    assert _apr_and_term(lo, ref)[0] < benchmark < _apr_and_term(hi, ref)[0]

    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _apr_and_term(mid, ref)[0] < benchmark:
            lo = mid
        else:
            hi = mid
    root = (lo + hi) / 2.0

    assert root == pytest.approx(EXACT_F, abs=1e-13), (
        f"bisection converged to {root!r}, not the recorded {EXACT_F!r}")


# ── 2. continuity within a fixed-term region ────────────────────────────────

def test_the_final_payment_varies_continuously_with_f(ref):
    """The mechanism. The clipped terminal payment is what moves."""
    finals = []
    for f in (1.0940, 1.0942, 1.0944, 1.0946, 1.0948, 1.0950):
        _, term, pay = _apr_and_term(f, ref)
        assert term == 12, f"term moved at f={f}; pick a tighter bracket"
        finals.append(pay[term - 1])

    assert finals == sorted(finals), "final payment should increase with f"
    assert finals[-1] > finals[0]
    # Smooth, not jumpy: successive differences stay within a factor of two.
    steps = [b - a for a, b in zip(finals, finals[1:])]
    assert min(steps) > 0
    assert max(steps) / min(steps) < 2.0, f"uneven steps suggest a term change: {steps}"


def test_apr_is_continuous_and_strictly_increasing_in_f_at_fixed_term(ref):
    """No gaps in the range — the direct contradiction of "discrete set"."""
    fs = [1.0940 + i * 0.00002 for i in range(51)]
    aprs, terms = [], []
    for f in fs:
        a, t, _ = _apr_and_term(f, ref)
        aprs.append(a)
        terms.append(t)

    assert set(terms) == {12}, "bracket must stay inside one paying-term region"
    assert aprs == sorted(aprs), "APR should be increasing in f"

    steps = [b - a for a, b in zip(aprs, aprs[1:])]
    assert min(steps) > 0, "a flat step would indicate a genuinely discrete range"
    # Continuity: no jump is disproportionate to the step in f.
    assert max(steps) / min(steps) < 1.5, f"a jump would show here: {max(steps)/min(steps):.3f}"


def test_intermediate_value_property_holds_between_two_grid_points(ref):
    """Between two adjacent GRID points, every intermediate APR is attained.

    This is what "not discrete" means operationally: the gap between
    consecutive grid APRs is filled, not empty.
    """
    f_lo, f_hi = 1.0945, 1.0950
    a_lo, _, _ = _apr_and_term(f_lo, ref)
    a_hi, _, _ = _apr_and_term(f_hi, ref)

    for frac in (0.25, 0.5, 0.75):
        target = a_lo + frac * (a_hi - a_lo)
        lo, hi = f_lo, f_hi
        for _ in range(120):
            mid = (lo + hi) / 2.0
            if _apr_and_term(mid, ref)[0] < target:
                lo = mid
            else:
                hi = mid
        got, term, _ = _apr_and_term((lo + hi) / 2.0, ref)
        assert term == 12
        assert got == pytest.approx(target, abs=1e-12), (
            f"APR {target!r} between two grid points was not attainable")


# ── 3. the registered grid result is unchanged ──────────────────────────────

def test_registered_f_star_is_still_the_nearest_point_on_the_searched_grid(ref, benchmark):
    """The correction must not move a registered number."""
    best = min(GRID, key=lambda f: abs((_apr_and_term(f, ref)[0] or 9.0) - benchmark))
    assert best == pytest.approx(REGISTERED_F_STAR, abs=1e-12), (
        f"nearest grid point is now {best!r}, not the registered "
        f"{REGISTERED_F_STAR!r}")

    apr, term, _ = _apr_and_term(REGISTERED_F_STAR, ref)
    assert apr == REGISTERED_APR
    assert term == 12
    assert (benchmark - apr) * 100 == pytest.approx(0.02416, abs=5e-6)


def test_the_exact_root_is_not_on_the_searched_grid(ref):
    """Why the registered value is a nearest match and not the root.

    The grid steps by 0.0005; the root falls between 1.0945 and 1.0950. That
    is the entire explanation, and it is about the grid rather than about
    duration integrality.
    """
    assert not any(abs(g - EXACT_F) < 1e-9 for g in GRID)
    assert REGISTERED_F_STAR < EXACT_F < REGISTERED_F_STAR + GRID_STEP

    gap_to_grid = min(abs(g - EXACT_F) for g in GRID)
    assert 0 < gap_to_grid < GRID_STEP


def test_duration_integrality_makes_the_map_piecewise_not_discrete(ref):
    """Sanity: the term does step somewhere, so "piecewise" is the right word.

    Guards against overcorrecting. Integrality is real and does introduce
    kinks; the withdrawn claim was that it introduces *gaps*.
    """
    terms = {}
    for f in (1.05, 1.08, 1.10, 1.15, 1.20, 1.25, 1.30):
        _, t, _ = _apr_and_term(f, ref)
        terms[f] = t
    assert len(set(terms.values())) > 1, (
        f"expected the paying term to change across the sweep, got {terms}")
