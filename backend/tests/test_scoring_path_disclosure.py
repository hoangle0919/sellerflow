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
import importlib
import json
import os
import random
import re
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import financing_engine  # noqa: E402
import ml_engine  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Added by the ff59333 merge. The `main` workstream computed the same two
#: directories under different names; keeping one definition of each avoids
#: two constants that could drift apart while looking authoritative.
BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert REPO == os.path.dirname(BACKEND), (
    "REPO and BACKEND disagree about the repo root; one of the two merged definitions is wrong")
fe = financing_engine          # `main`'s tests below use the short alias

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
    "backend/ml_engine.py",
    "backend/main.py",
    "backend/start_railway.sh",
    "research/publication/CAREER_PACKAGE.md",
    "research/publication/MANUSCRIPT.md",
]

# Each pattern asserts the fallback leaves output unchanged. All are false.
# Every one of these was live somewhere in this repository.
INVARIANCE_CLAIMS = [
    r"numbers shown are identical either way",
    r"identical either way",
    r"same numbers (?:either way|regardless)",
    r"(?:output|numbers|figures|results)[^.\n]{0,40}identical[^.\n]{0,40}"
    r"(?:scoring path|fallback|heuristic|ensemble)",
    r"(?:scoring path|fallback|heuristic|ensemble)[^.\n]{0,60}"
    r"(?:does not|doesn't|never) (?:change|affect)[^.\n]{0,30}"
    r"(?:numbers|figures|output|amount)",
    # ml_engine.py's docstring, until this pass.
    r"nothing downstream[^.\n]{0,40}depends",
    # ENVIRONMENT.md §"what happens when the model is missing", until this pass.
    r"(?:financing )?structure and scenarios are unchanged",
    r"(?:advance|remittance|cap factor|financing)[^.\n]{0,50}(?:is|are) unchanged",
    # model_status()'s note field, until this pass. Ambiguous rather than
    # false on its own -- "does not use it" is true of the arithmetic and
    # false of the pipeline -- and ambiguity is what let it survive review.
    r"deterministic and does not use it",
    # Unconditional scorer descriptions. The ensemble runs only when its
    # artifact loads; stating it flatly misdescribes a heuristic deploy.
    r"A Random Forest and Logistic Regression ensemble produces",
    r"The risk score comes from a trained ensemble",
    r"[Ii]ts risk score is trained on synthetic data with a circular label",
    r"RBF turns platform data into",
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


# The exact strings that were live in this repository before this pass. Each
# must trip the scanner, or removing it from the source achieved nothing.
STALE_STATEMENTS = [
    ("README.md (f652b94)",
     "because the financing arithmetic never calls the model, the numbers "
     "shown are identical either way."),
    ("ml_engine.py docstring",
     "Nothing downstream of the PD estimate depends on a model: the advance, "
     "remittance, cap, scenarios and risk findings are plain deterministic "
     "arithmetic in `financing_engine.py`."),
    ("ENVIRONMENT.md model-missing section",
     "assessments are produced via the heuristic, the financing structure and "
     "scenarios are unchanged, and the full backend and simulation suites "
     "pass."),
    ("model_status() note",
     "The underwriting ensemble is a secondary, explicitly unvalidated "
     "component. Financing arithmetic is deterministic and does not use it."),
    ("index.html step 2",
     "A Random Forest and Logistic Regression ensemble produces an "
     "unvalidated demo risk score and per-signal flags."),
    ("README.md model description",
     "The risk score comes from a trained ensemble and is an unvalidated "
     "demo score, not a probability of default."),
]


def test_every_removed_statement_would_be_caught_if_restored():
    """Restoring any of these must fail the scan. Otherwise the fix is cosmetic.

    One test over all fixtures rather than one test each: the fixture list grows
    every time a claim is retired, and a per-fixture parametrize would make the
    suite's headline count drift for reasons that have nothing to do with
    coverage. Failures name the origin, so diagnosis is unaffected.
    """
    for origin, text in STALE_STATEMENTS:
        hits = [m for p in INVARIANCE_CLAIMS for m in re.finditer(p, text, re.I)]
        assert hits, (
            f"scanner does not catch the statement removed from {origin}; "
            "it could be reintroduced without failing a test"
        )
        assert not all(_is_disowned(text, m) for m in hits), (
            f"the statement from {origin} was treated as disowned in isolation "
            "-- the disowning window is too wide"
        )


def test_health_endpoint_exposes_the_diagnostic_fields():
    """start_railway.sh points operators at these. They have to exist.

    A startup message naming a field the endpoint does not return is an
    instruction that cannot be followed -- which is how the fallback went
    unnoticed in the first place.
    """
    from fastapi.testclient import TestClient
    import main

    body = TestClient(main.app).get("/api/health").json()
    for field in ("scoring_path", "sklearn_runtime", "scoring_path_note"):
        assert field in body, f"/api/health must expose {field}"
    assert body["scoring_path"] in ("ensemble", "heuristic")

    note = body["scoring_path_note"].lower()
    assert "tier" in note, "the note must name the risk tier as what changes"
    for term in ("advance", "remittance", "cap factor"):
        assert term in note, f"the note must name {term} among the affected terms"

    blob = json.dumps(body).lower()
    for leak in ("password", "api_key", "secret", "token", "/users/", "/sessions/"):
        assert leak not in blob, f"/api/health leaked {leak!r}"


def test_hero_badge_fails_closed():
    """The badge must never assert the ensemble it has not confirmed.

    It was previously the literal string "RF+LR ENSEMBLE v1.0", rendered
    whether or not the artifact had loaded.
    """
    html = open(os.path.join(REPO, "frontend/index.html"),
                encoding="utf-8", errors="replace").read()
    assert "ACTIVE SCORER — UNKNOWN" in html, (
        "the unreachable-/api/health path must fall back to an explicit "
        "unknown state, never to a named scorer"
    )
    hero = re.search(r'id="hero-model"[^>]*>([^<]*)<', html)
    assert hero, "hero-model element not found"
    assert "ENSEMBLE" not in hero.group(1).upper(), (
        f"hero badge ships asserting a scorer: {hero.group(1)!r}"
    )


def test_public_scorer_copy_is_conditional():
    """Describing the ensemble unconditionally misstates what may be running."""
    unconditional = [
        r"A Random Forest and Logistic Regression ensemble produces",
        r"The risk score comes from a trained ensemble",
        r"Its risk score is trained on synthetic data with a circular label",
        r"RBF turns platform data into",
    ]
    for rel in ("README.md", "frontend/index.html"):
        text = open(os.path.join(REPO, rel), encoding="utf-8",
                    errors="replace").read()
        for pattern in unconditional:
            assert not re.search(pattern, text, re.I), (
                f"{rel} describes the scorer unconditionally: {pattern!r}. "
                "The ensemble runs only when its artifact loads; otherwise the "
                "heuristic does. Neither has measured predictive validity."
            )
        assert re.search(r"active scorer|whichever scorer", text, re.I), (
            f"{rel} must name the active scorer rather than one fixed path"
        )


# Every surface is scanned for the false claim; these must additionally state
# the true one. Kept as its own list rather than a skip inside the parametrize,
# so a skip meaning "not applicable" never enters a count that should mean
# "could not run". The browser checks are the only skips this suite is meant to
# produce, but their granularity is environment-dependent -- pytest may report
# one skipped module or nine skipped cases depending on whether Playwright,
# Chromium, or neither is installed. Do not assert an exact skip number.
MUST_DISCLOSE = [
    "README.md",
    "backend/ENVIRONMENT.md",
    "backend/ml_engine.py",
    "frontend/index.html",
]


@pytest.mark.parametrize("rel", MUST_DISCLOSE)
def test_surfaces_that_should_name_the_dependency_do(rel):
    """Removing the false claim is not the same as stating the true one."""
    text = open(os.path.join(REPO, rel), encoding="utf-8", errors="replace").read()
    assert re.search(r"risk tier|assigned tier|the tier", text, re.I), (
        f"{rel} must name the risk tier as the thing the scorer changes"
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
    """The disclosure must be present, not merely un-contradicted.

    Matched on emphasis-stripped text. The ff59333 merge italicised *once a
    risk tier is supplied* — the correct thing to emphasise, since it is the
    qualifier the retracted claim dropped — and a literal substring match
    failed on its own asterisks. Pinning prose to its markdown punctuation
    makes the guard fire on formatting and teaches the next person to weaken
    it; pinning the words does not.
    """
    raw = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    text = re.sub(r"[*_`]", "", raw)

    assert "deterministic once a risk tier is supplied" in text, (
        "README must keep the determinism-GIVEN-A-TIER qualifier; dropping it "
        "is how the retracted claim was stated in the first place")

    # The path→tier link, in either branch's phrasing. Both are accepted
    # because both are true and neither is weaker than the assertion was.
    link = re.search(r"can change the assigned tier"
                     r"|scorer is what assigns that tier"
                     r"|active scoring path changes the result", text, re.I)
    assert link, "README must tie the active scoring path to the assigned tier"

    # And the empirical strength ff59333 added, which the earlier wording
    # lacked: not merely that the paths *can* differ, but that they *do*.
    assert re.search(r"disagree on the tier", text, re.I), (
        "README must state that the two paths actually disagree in practice, "
        "not only that they could")
    assert "414,000,000" in text and "249,600,000" in text, (
        "the worked tier-to-cap figures must survive; they are what make the "
        "disclosure checkable rather than assertable")


# ══════════════════════════════════════════════════════════════════════
# Merged from `origin/main` ff59333 (product workstream).
#
# Both branches independently created a file at this path, so this was an
# add/add conflict with no shared ancestor. The two sets are complementary
# and neither is weakened here:
#
#   above   this branch's structural proofs that the tier drives every
#           term, the fail-closed hero badge, the health-endpoint fields,
#           and a scanner that must itself be shown capable of failing.
#   below   `main`'s EMPIRICAL demonstration that the two paths actually
#           disagree on a cohort, its copy tripwire, and the A-9 checks
#           that the main assessment surface renders `apr_basis` and
#           labels the closure rate as an observed window.
#
# The overlap is only in subject matter. There are no duplicated test
# names, and the structural and empirical arguments answer different
# objections: one shows the mechanism exists, the other that it fires.
# ══════════════════════════════════════════════════════════════════════

PUBLIC_COPY = [
    os.path.join(REPO, "README.md"),
    os.path.join(REPO, "frontend", "index.html"),
]


def test_the_public_copy_paths_actually_exist():
    """A skip is not a pass. The copy guard below silently skipped when this
    module computed the repo root one level too shallow; assert the fixtures
    resolve so the guard can never quietly stop guarding."""
    for path in PUBLIC_COPY:
        assert os.path.exists(path), f"public copy fixture missing: {path}"

# The sentence that retracts the claim is allowed to quote it; an active
# assertion of it is not. A line is exempt only if it also carries retraction
# language, which keeps the guard from being defeated by paraphrase.
RETRACTION_MARKERS = ("retract", "was wrong", "no longer", "superseded", "earlier version")
BANNED = re.compile(
    r"identical either way"
    r"|numbers\s+(shown\s+)?are\s+identical"
    r"|same\s+numbers\s+either\s+way"
    r"|(unchanged|identical)\s+(whether|regardless of)\s+(the\s+)?(scoring|model|path)",
    re.I,
)


@pytest.mark.parametrize("path", PUBLIC_COPY)
def test_public_copy_does_not_assert_the_retracted_equivalence(path):
    if not os.path.exists(path):
        pytest.skip(f"{path} not present")
    offenders = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if BANNED.search(line) and not any(m in line.lower() for m in RETRACTION_MARKERS):
            offenders.append(f"{os.path.basename(path)}:{n}: {line.strip()[:140]}")
    assert not offenders, (
        "Public copy asserts the retracted claim that the scoring path does not "
        "change the numbers:\n  " + "\n  ".join(offenders)
    )


def test_the_tier_actually_moves_every_contractual_term():
    """The reason the claim is false: terms key off the tier, so a tier change
    is a term change. Hand-checked at 200M monthly revenue."""
    low = fe.financing_structure(200_000_000, "Low Risk")
    med = fe.financing_structure(200_000_000, "Medium Risk")
    high = fe.financing_structure(200_000_000, "High Risk")

    assert low["repayment_cap"] == 414_000_000
    assert med["repayment_cap"] == 249_600_000
    assert high["recommended_amount"] == 0          # High Risk declines outright

    assert low["remittance_pct"] != med["remittance_pct"]
    assert low["factor_rate"] != med["factor_rate"]
    assert low["recommended_amount"] > med["recommended_amount"]


def test_the_two_scoring_paths_disagree_on_tier_in_practice():
    """Not a theoretical difference. Scored both ways over a fixed pseudo-random
    cohort, the paths assign different tiers for a substantial share of
    profiles — including profiles that one path approves and the other declines.

    Skips (rather than fails) when no ensemble artifact is present, because a
    clean checkout has none and that is a legitimate state.
    """
    import ml_engine

    def tiers_under(model_dir):
        os.environ["RBF_MODEL_DIR"] = model_dir
        importlib.reload(ml_engine)
        ml_engine.load_models()
        return (
            ml_engine.model_status()["scoring_path"],
            [ml_engine.score(p)["risk_tier"] for p in COHORT],
        )

    rng = random.Random(11)
    COHORT = [
        dict(
            monthly_revenue=rng.uniform(20e6, 500e6), revenue_growth=rng.uniform(-0.25, 0.5),
            order_volume=rng.randint(60, 900), avg_order_value=rng.uniform(150e3, 900e3),
            return_rate=rng.uniform(0.005, 0.25), rating=rng.uniform(3.2, 5.0),
            days_active=rng.randint(40, 1300), inventory_turnover=rng.uniform(2, 10),
            previous_loans=rng.randint(0, 4), late_ship_rate=rng.uniform(0.005, 0.2),
        )
        for _ in range(200)
    ]

    original = os.environ.get("RBF_MODEL_DIR")
    try:
        path_a, tiers_a = tiers_under(tempfile.mkdtemp())          # no artifact -> heuristic
        path_b, tiers_b = tiers_under(os.path.join(BACKEND, "models"))
        if path_a == path_b:
            pytest.skip("no ensemble artifact available; cannot compare two paths")
        assert path_a == "heuristic" and path_b == "ensemble"

        disagreements = sum(1 for a, b in zip(tiers_a, tiers_b) if a != b)
        assert disagreements > 0, (
            "The scoring paths agreed on every profile. If this ever becomes "
            "genuinely true, the retracted claim would deserve revisiting — but "
            "verify it deliberately rather than assuming it."
        )
        # And the strong form: at least one profile flips between fundable and not.
        flips = sum(
            1 for a, b in zip(tiers_a, tiers_b)
            if (a == "High Risk") != (b == "High Risk")
        )
        assert flips > 0, "expected at least one approve/decline flip between paths"
    finally:
        if original is None:
            os.environ.pop("RBF_MODEL_DIR", None)
        else:
            os.environ["RBF_MODEL_DIR"] = original
        importlib.reload(ml_engine)
        ml_engine.load_models()


# ── A-9: a rate must carry its basis to the reader (research handoff §7.2) ──

def test_engine_emits_a_basis_whenever_it_emits_a_rate():
    low = fe.financing_structure(185_000_000, "Low Risk", return_rate=0.028)
    assert low["effective_apr_base_case"] is not None
    assert low["apr_basis"], "a rate was produced without a basis"
    assert "base-case" in low["apr_basis"].lower()


def test_the_main_surface_actually_renders_the_apr_basis():
    """The engine produced `apr_basis` and index.html dropped it, so a reader saw
    'Effective APR (base case) 13.2%' with nothing stating what the base case
    assumes or which way a decline moves it. The Lab carries its duration basis;
    the main surface must carry the rate's.

    Asserted on the source because this string is assembled in JS at render time;
    the browser-level equivalent lives in the Lab suite.
    """
    idx = os.path.join(REPO, "frontend", "index.html")
    src = open(idx, encoding="utf-8").read()
    assert "structure.apr_basis" in src, "index.html never reads structure.apr_basis"
    # and it must not be confined to a branch that other notes can displace
    assert "noteTxt=(noteTxt?noteTxt+' ':'')+structure.apr_basis" in src, (
        "apr_basis must be appended to whichever note branch fired, not placed "
        "inside one of them — a merchant with outstanding information "
        "requirements would otherwise see the rate with no basis at all"
    )


def test_the_closure_return_is_labelled_observed_window():
    """A-9: on a path that never completes, the rate is an observed-window figure
    and must not read as a lifetime return."""
    idx = os.path.join(REPO, "frontend", "index.html")
    src = open(idx, encoding="utf-8").read()
    assert "observed_apr_to_closure" in src
    assert "observed window, not a lifetime return" in src
