"""Two different APRs live in this repository. They must never be conflated.

`b047cc8` put an effective APR on the product surface, and A-9 corrected what
the research APR means. Both are called "effective APR" in ordinary English and
they are not the same quantity:

  PRODUCT  `financing_engine.effective_apr` -- the annualised IRR of ONE
           deterministic base-case schedule, computed from the merchant's
           submitted figures at the assigned risk tier. A single number about a
           single hypothetical contract. No simulation, no distribution.

  RESEARCH `lab.effective_apr` -- the MEAN observed-window IRR across the
           rate-defined paths of a registered simulation scenario. A summary
           statistic over 500 generated revenue paths, carrying a denominator,
           a censoring caveat and an artifact checksum.

Different inputs, different populations, different evidentiary weight. The
product figure is an illustration for one merchant; the research figure is
simulation output under modelled assumptions and is not evidence about any
merchant at all.

This file is narrow on purpose. It does not re-derive either calculation and
does not reopen the product formulas -- it asserts only that the two surfaces
keep saying which one they are.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import financing_engine  # noqa: E402
import lab  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_the_two_aprs_are_computed_from_different_things():
    """A structural check, so the distinction is not merely a wording promise.

    The product APR takes a principal and one explicit payment schedule. The
    research APR is read out of a registered artifact as a mean across paths.
    If these ever become the same call, the copy separating them is fiction.
    """
    product = financing_engine.effective_apr(100_000_000.0, [10_000_000.0] * 12)
    assert product is not None and isinstance(product, float)

    body = lab._load("baseline_closure_v2_canonical")
    if body is None:
        pytest.skip("registered artifact not present")
    arm = body["scenarios"]["closure_m13"]["RBF"]

    # The research figure carries a denominator and a path count. The product
    # figure has neither, because it describes one schedule.
    assert "apr_defined_count" in arm and "n_paths" in arm
    assert arm["apr_defined_count"] <= arm["n_paths"]


def test_product_surface_labels_its_apr_as_a_base_case():
    """`effective_apr_base_case` must not be presented as a study result."""
    html = open(os.path.join(REPO, "frontend", "index.html"),
                encoding="utf-8", errors="replace").read()
    assert "effective_apr_base_case" in html
    assert re.search(r"APR \(base case\)|base[- ]case", html, re.I), (
        "the product APR must be labelled as a base case, not as 'the APR'"
    )
    # And must not borrow the research vocabulary.
    for research_only in ("observed-window", "rate-defined", "simulated paths",
                          "Monte Carlo"):
        assert research_only not in html, (
            f"product page uses research-only APR vocabulary: {research_only!r}"
        )


def test_lab_surface_never_presents_its_apr_as_a_merchant_quote():
    """The research APR is a mean over simulated paths, and says so."""
    lab_html = open(os.path.join(REPO, "frontend", "lab.html"),
                    encoding="utf-8", errors="replace").read()
    for product_only in ("effective_apr_base_case", "base case APR",
                         "your APR", "merchant APR"):
        assert product_only not in lab_html, (
            f"Lab borrows product APR vocabulary: {product_only!r}"
        )
    # The Lab must render the API-supplied basis rather than a fixed label --
    # for BOTH statistics. The page rendered `duration_basis` only, so the
    # rate's denominator and its observed-window caveat never reached a reader.
    assert "apr_label" in lab_html and "duration_label" in lab_html
    assert "apr_basis" in lab_html, (
        "the rate's basis is never rendered; the A-9 explanation stops at the API"
    )
    assert "duration_basis" in lab_html
    assert "Observed-window rate" in lab_html


def test_neither_surface_claims_the_other_validates_it():
    """The dangerous sentence would be one implying the two agree.

    Nothing may suggest that the simulation validates the product's quoted
    rate, or that the product demonstrates the simulation. They share a name
    and nothing else.
    """
    pattern = re.compile(
        r"(simulation|research|study)[^.\n]{0,60}(validates?|confirms?|"
        r"matches|verifies)[^.\n]{0,40}(APR|rate)"
        r"|(APR|rate)[^.\n]{0,40}(validated|confirmed|verified)[^.\n]{0,40}"
        r"(by the )?(simulation|study)", re.I)
    for rel in ("frontend/index.html", "frontend/lab.html", "README.md",
                "backend/lab.py", "backend/financing_engine.py"):
        text = open(os.path.join(REPO, rel), encoding="utf-8",
                    errors="replace").read()
        m = pattern.search(text)
        assert m is None, f"{rel} ties the two APRs together: {m.group(0)!r}"
