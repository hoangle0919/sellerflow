"""IRR definition, domain and conditioning — spec amendment A-9.

Three implementation defects were published before A-9, and the suite could not
see any of them because nothing asserted what the rate *meant*:

  1. `engine.run_path` filtered `p > 0` before solving, deleting internal zero
     months and moving later payments earlier in calendar time.
  2. `solve_apr` bracketed `[1e-12, 2.0]`, so a contract recovering less than it
     advanced returned `None` and was published as "undefined" rather than as
     the loss it was.
  3. `apr_mean` averages IRR-defined paths while `duration_mean` averages
     completed paths. Both were described in the publication as survivor
     statistics over completed contracts. For the rate that was false.

These tests pin the corrected semantics. The first three are closed-form and
need no simulation; the rest run the registered closure scenarios, which are
where completion and IRR existence actually come apart.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from rbf_sim.contracts import (ContractTerms, IRR_MIN_MONTHLY, rbf_payments,
                               solve_apr)
from rbf_sim.engine import run_scenario
from rbf_sim.generator import PathParams
from rbf_sim.metrics import duration


# --------------------------------------------------------------------------
# 1-3. The definition itself, in closed form.
# --------------------------------------------------------------------------

def test_internal_zero_months_lower_the_irr_relative_to_a_compressed_stream():
    """The defect, stated as a test. Same payments, later arrival, lower rate.

    Compressing `[0, p, 0, p]` to `[p, p]` is not a tidy-up: it asserts the
    money arrived sooner than it did.
    """
    principal = 100.0
    full = [0.0, 60.0, 0.0, 0.0, 60.0]      # paid in months 2 and 5
    compressed = [60.0, 60.0]                # what the old code solved

    irr_full = solve_apr(principal, full)
    irr_compressed = solve_apr(principal, compressed)

    assert irr_full is not None and irr_compressed is not None
    assert irr_full < irr_compressed, (
        f"deleting internal zeros must inflate the rate; got full={irr_full!r} "
        f"compressed={irr_compressed!r}"
    )
    # Trailing zeros carry no information at any position and must not move it.
    assert math.isclose(solve_apr(principal, full + [0.0, 0.0]), irr_full,
                        rel_tol=1e-12)


def test_repayment_below_principal_yields_a_negative_irr():
    """A loss is a number, not an absence. The old bracket could not say it."""
    irr = solve_apr(185_000_000.0, [10_000_000.0] * 6)   # 60M back on 185M
    assert irr is not None, "a partial recovery has a defined, negative IRR"
    assert irr < 0
    assert irr > -1.0, "an annualised rate cannot fall to or below -100%"


def test_stream_with_no_positive_payment_is_undefined():
    """The only case where the A-9 equation genuinely has no root."""
    assert solve_apr(185_000_000.0, [0.0] * 24) is None
    assert solve_apr(185_000_000.0, []) is None


def test_solver_domain_opens_just_above_minus_one():
    """`i = -1` is the singularity of (1+i)^-t, so the bracket must exclude it."""
    assert -1.0 < IRR_MIN_MONTHLY < -0.999
    # A near-total loss still resolves rather than raising or returning None.
    irr = solve_apr(1_000_000.0, [1.0] + [0.0] * 23)
    assert irr is not None and irr < -0.99


# --------------------------------------------------------------------------
# 4-6. Completion and IRR existence are different events, with different
#      denominators. This is where the published figure was wrong.
# --------------------------------------------------------------------------

R0 = 185_000_000.0
TERMS = ContractTerms(A=R0, r=0.10, f=1.20, j=0.18, N_B=12)


def _closure_scenario(onset: int, n: int = 60):
    params = PathParams(R0=R0, label=f"closure_m{onset}",
                        shock="closure", shock_onset=onset)
    return run_scenario(n, params, TERMS, base_seed=20260803)


def test_closure_m13_has_paths_that_are_incomplete_yet_irr_defined():
    """The exact case the publication mis-described.

    Revenue stops at month 13. Most paths never reach the contractual target,
    but every one of them made real payments for twelve months, so every one
    has a defined return. Completion and IRR existence are independent here.
    """
    res = _closure_scenario(13)
    rbf = res["arms"]["RBF"]
    n = rbf["n_paths"]

    assert rbf["completed_count"] < n, "some paths must fail to complete"
    assert rbf["apr_defined_count"] == n, (
        "every path pays something before closure, so every path has an IRR"
    )
    incomplete_but_defined = rbf["apr_defined_count"] - rbf["completed_count"]
    assert incomplete_but_defined > 0, (
        "this scenario exists to demonstrate that gap; if it closes, the "
        "conditioning claim in A-9 needs re-deriving, not the test deleting"
    )


def test_duration_mean_is_conditioned_on_completion():
    res = _closure_scenario(13)
    rbf = res["arms"]["RBF"]
    durs = [r["RBF"].duration for r in res["per_path"]
            if r["RBF"].duration is not None]

    assert len(durs) == rbf["completed_count"]
    assert math.isclose(rbf["duration_mean"], sum(durs) / len(durs), rel_tol=1e-12)
    assert math.isclose(rbf["completed_rate"], len(durs) / rbf["n_paths"])


def test_apr_mean_is_conditioned_on_irr_existence_not_completion():
    """The published number averaged 500 paths while claiming to average 119."""
    res = _closure_scenario(13)
    rbf = res["arms"]["RBF"]
    per = [r["RBF"] for r in res["per_path"]]

    defined = [r.apr for r in per if r.apr is not None]
    completed_only = [r.apr for r in per
                      if r.apr is not None and r.duration is not None]

    assert math.isclose(rbf["apr_mean"], sum(defined) / len(defined), rel_tol=1e-12)
    assert len(defined) > len(completed_only), (
        "the two denominators must differ in this scenario, or the test proves "
        "nothing"
    )
    # And they give materially different answers -- which is why the mislabel
    # mattered rather than being a wording quibble.
    assert not math.isclose(sum(defined) / len(defined),
                            sum(completed_only) / len(completed_only),
                            rel_tol=0.02)


def test_permanent_early_closure_reports_a_negative_rate_not_undefined():
    """closure_m7 recovers far less than principal. That is a loss, not a gap."""
    res = _closure_scenario(7)
    rbf = res["arms"]["RBF"]

    assert rbf["completed_count"] == 0, "no path should complete after month-7 closure"
    assert rbf["apr_defined_count"] == rbf["n_paths"], (
        "payments were made for six months, so every path has a defined IRR"
    )
    assert rbf["apr_mean"] is not None and rbf["apr_mean"] < -0.5


def test_aggregate_reports_both_denominators_explicitly():
    """A reader must not have to infer which paths a mean was taken over."""
    res = _closure_scenario(13)
    for arm in ("RBF", "FIX-A", "FIX-B", "RBF-G"):
        agg = res["arms"][arm]
        for field in ("apr_defined_count", "apr_defined_rate",
                      "completed_count", "completed_rate"):
            assert field in agg, f"{arm} aggregate is missing {field}"
        assert 0.0 <= agg["apr_defined_rate"] <= 1.0
        assert 0.0 <= agg["completed_rate"] <= 1.0


def test_temporary_closure_rate_falls_once_calendar_time_is_respected():
    """An internal zero spell is exactly where the old defect bound.

    `temp_closure` has three zero-revenue months in the middle of the stream.
    Solving the uncompressed vector must give a strictly lower rate than
    solving the compressed one.
    """
    from rbf_sim.generator import generate_cohort

    params = PathParams(R0=R0, label="temp_closure", shock="temporary_closure",
                        shock_depth=0.50, shock_onset=7)
    cohort = generate_cohort(40, params, 20260803)

    strictly_lower = 0
    for path in cohort:
        payments = rbf_payments(path.remittance_base(TERMS.remittance_basis), TERMS)

        # Only meaningful where a zero sits *inside* the paying window; trailing
        # zeros are immaterial by construction.
        last_paying = max((t for t, x in enumerate(payments) if x > 0), default=-1)
        if last_paying < 0 or all(x > 0 for x in payments[:last_paying]):
            continue

        full = solve_apr(TERMS.A, payments)
        compressed = solve_apr(TERMS.A, [x for x in payments if x > 0])
        assert full is not None and compressed is not None
        assert full < compressed, (
            "an internal zero month must lower the rate; "
            f"full={full!r} compressed={compressed!r}"
        )
        strictly_lower += 1

    assert strictly_lower > 0, (
        "no path in temp_closure had an internal zero month; the scenario or "
        "the generator changed, so re-derive the claim rather than deleting "
        "this test"
    )
