"""The product and research IRR solvers must agree on identical cash flows.

Two implementations of the same equation live in this repository:
`backend/financing_engine.effective_apr` and
`research/rbf_sim/contracts.solve_apr`. They serve different purposes — one
prices a single merchant schedule, the other summarises simulated paths — but
they answer the same question about a given payment stream, and they have now
drifted apart three times:

  * the product mirrored `solve_apr` before A-9 corrected it;
  * A-9 fixed the research side; the product kept the pre-A-9 ceiling;
  * the product then fixed the ceiling and found an endpoint defect the
    research side still had.

Each drift was caught by a human reading both files. This file makes the
machine do it: identical inputs through both implementations, compared
directly. Parity is not an aesthetic preference here — a rate quoted to a
merchant and a rate published in the paper that disagree on the same cash flow
would be a genuine inconsistency in the work.

These fixtures deliberately include the cases where the two previously
disagreed, so a regression in either layer fails here rather than in review.
"""
import math
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "backend"))
sys.path.insert(0, os.path.join(REPO, "research"))

import financing_engine  # noqa: E402
from rbf_sim import contracts as research  # noqa: E402


# (principal, flows, label). Every case that has ever diverged is here.
PARITY_CASES = [
    # The endpoint-residual defect: same contract, two scales. The small one
    # returned None while the large one resolved.
    (100.0, [115.0], "endpoint residual, small scale"),
    (10_000_000.0, [11_500_000.0], "same contract, large scale"),
    # The old hard ceiling of 10.0 and just above it.
    (100.0, [1100.0], "monthly IRR exactly at the analytic bound"),
    (100.0, [1200.0], "monthly IRR above the old ceiling"),
    (100.0, [100_000.0], "root far above the old ceiling"),
    # Zero and negative territory.
    (100.0, [100.0], "S == P, rate exactly zero"),
    (185_000_000.0, [10_000_000.0] * 6, "negative IRR"),
    # The old -1 + 1e-9 floor excluded both of these.
    (1_000_000.0, [1e-6], "near-total loss, tiny payment"),
    (10_000_000_000.0, [1.0], "near-total loss, large advance"),
    # Calendar time.
    (100.0, [0.0, 60.0, 0.0, 0.0, 60.0], "internal zero months"),
    (100.0, [60.0, 60.0], "same payments, compressed"),
    # The one case that is genuinely undefined.
    (185_000_000.0, [0.0] * 24, "no positive payment"),
    (185_000_000.0, [], "empty stream"),
]


@pytest.mark.parametrize("principal,flows,label",
                         PARITY_CASES, ids=[c[2] for c in PARITY_CASES])
def test_both_layers_agree(principal, flows, label):
    product = financing_engine.effective_apr(principal, list(flows))
    study = research.solve_apr(principal, list(flows))

    if study is None or product is None:
        assert study is None and product is None, (
            f"{label}: one layer says undefined and the other does not — "
            f"research={study!r} product={product!r}"
        )
        return

    assert math.isclose(product, study, rel_tol=1e-9, abs_tol=1e-12), (
        f"{label}: research={study!r} product={product!r}"
    )


def test_the_constants_themselves_match():
    """Drift usually starts with one constant, not one formula."""
    assert financing_engine.IRR_MIN_MONTHLY == research.IRR_MIN_MONTHLY
    assert financing_engine.IRR_ENDPOINT_REL_TOL == research.IRR_ENDPOINT_REL_TOL
    assert research.IRR_MIN_MONTHLY == math.nextafter(-1.0, 0.0), (
        "the lower bound must be the format's own limit, not a chosen floor"
    )


def test_upper_bound_agrees_across_layers():
    for principal, flows, label in PARITY_CASES:
        if not flows:
            continue
        assert (financing_engine.irr_upper_bound(principal, list(flows))
                == research.irr_upper_bound(principal, list(flows))), label


def test_undefined_means_no_positive_payment_in_both_layers():
    """`None` has one meaning, and a loss is not it."""
    for fn in (financing_engine.effective_apr, research.solve_apr):
        assert fn(100.0, [0.0, 0.0]) is None
        assert fn(100.0, []) is None
        # Anything that pays something has a rate, however bad.
        assert fn(1e12, [1.0]) is not None


def test_a_residual_beyond_tolerance_is_not_silently_accepted():
    """The endpoint tolerance absorbs float error, not a wrong bracket.

    Feeding a deliberately wrong upper bound must not produce an annualised
    number: a residual too large to be rounding means the bound is invalid, and
    reporting a rate from it would be worse than reporting nothing.
    """
    principal, flows = 100.0, [115.0]
    tol = research.IRR_ENDPOINT_REL_TOL * principal

    def npv(i):
        return -principal + sum(p / (1.0 + i) ** (t + 1) for t, p in enumerate(flows))

    good = research.irr_upper_bound(principal, flows)
    assert 0 <= npv(good) <= tol, "the true bound's residual must be float-scale"

    # A bound below the root leaves a residual far larger than the tolerance.
    bad = good - 0.01
    assert npv(bad) > tol, (
        "this case no longer distinguishes float residual from a wrong bracket"
    )
