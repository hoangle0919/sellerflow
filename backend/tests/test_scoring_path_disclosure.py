"""The two scoring paths are not output-equivalent, and the copy must not say they are.

A commit on `main` claimed that because the financing arithmetic never calls the
model, "the numbers shown are identical either way" when scoring falls back from
the ensemble to the heuristic. That is false end to end. The arithmetic is
deterministic *given a risk tier*, but the tier is chosen upstream by whichever
path is active:

    scoring_path -> pd_score -> risk tier -> advance %, remittance %,
                                             cap factor, and eligibility

So a fallback can change every figure a merchant sees, including whether an
offer appears at all. This file exists so the claim cannot come back.

Two kinds of test here, deliberately:

  * Structural proofs that need no model artifact, so they run on a clean
    checkout and in CI. These establish that the tier drives the output and
    that the heuristic cannot be a stand-in for the ensemble.
  * A copy tripwire for the specific phrasing that was wrong.

`conftest.py` points RBF_MODEL_DIR at an empty directory, so the suite never
depends on a developer's untracked .pkl files.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import financing_engine  # noqa: E402
import ml_engine  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_MERCHANT = {
    "monthly_revenue": 200_000_000, "revenue_growth": 0.10, "order_volume": 500,
    "avg_order_value": 400_000, "return_rate": 0.05, "rating": 4.5,
    "days_active": 500, "inventory_turnover": 6.0, "late_ship_rate": 0.03,
    "previous_loans": 1,
}

TIER_FIELDS = ("remittance_pct", "factor_rate", "repayment_cap")


def test_risk_tier_changes_the_financing_output():
    """The arithmetic is deterministic per tier -- and different across tiers."""
    low = financing_engine.financing_structure(200_000_000, "Low Risk")
    med = financing_engine.financing_structure(200_000_000, "Medium Risk")

    differing = [f for f in TIER_FIELDS if low[f] != med[f]]
    assert differing == list(TIER_FIELDS), (
        "Every tier-sensitive field should differ between Low and Medium Risk; "
        f"these did not: {set(TIER_FIELDS) - set(differing)}"
    )
    # Not a rounding difference -- the repayment cap moves by a wide margin.
    assert abs(low["repayment_cap"] - med["repayment_cap"]) > 100_000_000


def test_high_risk_tier_removes_the_offer_entirely():
    """Tier does not merely scale the numbers; it decides whether there are any."""
    high = financing_engine.financing_structure(200_000_000, "High Risk")
    assert high["repayment_cap"] == 0
    assert high["remittance_pct"] == 0
    assert high["factor_rate"] == 0


def test_heuristic_ignores_features_the_ensemble_weights_most():
    """The paths cannot be output-equivalent: they do not read the same inputs.

    The heuristic fallback is a closed form over return_rate, rating and
    late_ship_rate only. revenue_growth carries the largest share of the
    trained ensemble's feature importance and the heuristic cannot see it, so
    two merchants differing only in revenue_growth are indistinguishable to one
    path and separable by the other. No artifact is needed to show this.
    """
    assert ml_engine.model_status()["scoring_path"] == "heuristic", (
        "conftest should pin RBF_MODEL_DIR at an empty directory"
    )

    weak = dict(BASE_MERCHANT, revenue_growth=-0.35)
    strong = dict(BASE_MERCHANT, revenue_growth=0.60)

    assert ml_engine.score(weak)["pd_score"] == ml_engine.score(strong)["pd_score"], (
        "Heuristic is expected to be blind to revenue_growth. If this now fails "
        "the fallback formula changed; re-derive the claim rather than deleting "
        "the test."
    )
    assert "revenue_growth" in ml_engine.FEATURES, (
        "revenue_growth is a model input, so the ensemble can separate two "
        "cases the heuristic reports identically."
    )


def test_score_reports_which_path_produced_it():
    """Whatever runs, the response must name it. This is the diagnostic."""
    result = ml_engine.score(dict(BASE_MERCHANT))
    assert result["scoring_path"] in ("ensemble", "heuristic")
    assert result["model_version"] == (
        ml_engine.ENSEMBLE_VERSION if result["scoring_path"] == "ensemble"
        else ml_engine.HEURISTIC_VERSION
    ), "model_version must reflect the path that actually ran"


# --------------------------------------------------------------------------
# Copy tripwire. Same limits as test_public_copy.py: this catches the named
# phrasing, not the idea. Human review against CLAIM_LEDGER.md is the real gate.
# --------------------------------------------------------------------------

SURFACES = [
    "README.md",
    "frontend/index.html",
    "backend/ENVIRONMENT.md",
    "research/publication/CAREER_PACKAGE.md",
]

# Each pattern asserts the fallback leaves output unchanged. All are false.
INVARIANCE_CLAIMS = [
    r"numbers shown are identical either way",
    r"identical either way",
    r"same numbers (?:either way|regardless)",
    r"(?:output|numbers|figures|results)[^.\n]{0,40}identical[^.\n]{0,40}"
    r"(?:scoring path|fallback|heuristic|ensemble)",
    r"(?:scoring path|fallback|heuristic|ensemble)[^.\n]{0,60}"
    r"(?:does not|doesn't|never) (?:change|affect)[^.\n]{0,30}"
    r"(?:numbers|figures|output|amount)",
]

# A document has to be able to quote the retracted claim in order to retract
# it -- ENVIRONMENT.md and the decision log both do. So an occurrence passes
# when a disowning cue sits close to it, following the convention in
# test_public_copy.py.
#
# The windows are deliberately narrow and directional. An early version of the
# sibling scanner used a 240-character symmetric window that included a bare
# "not ", and it passed the entire repository while two live violations sat in
# lab.py. A wide window does not make a lenient test; it makes a vacuous one.
BEFORE = 90   # retraction framing precedes the quote: 'once claimed that "..."'
AFTER = 70    # retraction follows the quote: '"..." -- that claim is withdrawn'

DISOWNED_BEFORE = re.compile(
    r"(?:once claimed|previously|superseded|earlier|retracted|withdrawn|"
    r"incorrectly|wrongly|false)", re.IGNORECASE)
DISOWNED_AFTER = re.compile(
    r"(?:is withdrawn|are withdrawn|is false|is wrong|is incorrect|"
    r"was withdrawn|that claim is|no longer|retracted|superseded)",
    re.IGNORECASE)


def _is_disowned(text: str, m: re.Match) -> bool:
    before = text[max(0, m.start() - BEFORE):m.start()]
    after = text[m.end():m.end() + AFTER]
    return bool(DISOWNED_BEFORE.search(before) or DISOWNED_AFTER.search(after))


@pytest.mark.parametrize("rel", SURFACES)
def test_no_public_surface_claims_scoring_path_invariance(rel):
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        pytest.skip(f"{rel} not present")
    text = open(path, encoding="utf-8", errors="replace").read()

    for pattern in INVARIANCE_CLAIMS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            if _is_disowned(text, m):
                continue
            line = text[:m.start()].count("\n") + 1
            raise AssertionError(
                f"{rel}:{line} claims the scoring path does not change the "
                f"output: {m.group(0)!r}\n"
                "It does. scoring_path -> pd_score -> risk tier -> advance %, "
                "remittance %, cap factor and eligibility. Say instead: the "
                "financing formulas are deterministic once a risk tier is "
                "supplied, but the active scoring path can change the tier and "
                "therefore the displayed figures.\n"
                "If you are quoting the phrase in order to retract it, put the "
                "retraction next to it."
            )


def test_the_invariance_scanner_can_actually_fail():
    """A check that cannot fail is not a check -- this project has shipped two.

    Guards both directions: the bare claim must trip the scanner, and a
    quotation that is properly retracted must not.
    """
    bare = ("The live demo may be running the heuristic; because the financing "
            "arithmetic never calls the model, the numbers shown are identical "
            "either way.")
    hits = [m for p in INVARIANCE_CLAIMS for m in re.finditer(p, bare, re.I)]
    assert hits, "scanner failed to match the exact sentence it exists to catch"
    assert not any(_is_disowned(bare, m) for m in hits), (
        "the bare claim was treated as disowned -- the window is too wide"
    )

    quoted = ('A README revision once claimed the numbers shown are identical '
              'either way; that claim is withdrawn.')
    hits = [m for p in INVARIANCE_CLAIMS for m in re.finditer(p, quoted, re.I)]
    assert hits and all(_is_disowned(quoted, m) for m in hits), (
        "a properly retracted quotation must pass, or the docs cannot "
        "describe their own corrections"
    )


def test_readme_states_the_tier_dependency():
    """The disclosure must be present, not merely un-contradicted."""
    text = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    assert "deterministic once a risk tier is supplied" in text
    assert re.search(r"can change the assigned tier", text), (
        "README must say the active scoring path can change the tier"
    )
