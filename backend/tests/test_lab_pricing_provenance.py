"""The Lab's pricing reference must describe the file it names.

Two defects motivated this suite, and they are the kind that a green test run
will happily carry forever because nothing about them looks wrong on the page.

**Mixed provenance.** `manifest()` labelled its pricing block
`validation_v2_canonical.json` and attached that file's SHA-256, while reading
its VALUES out of the raw `validation_v2.json`. The raw file has no `canonical`
block, so `spec_version` came back null next to a canonical checksum — a record
whose name, hash and contents referred to two different files. A reader
checksumming the named file would have verified bytes that never produced the
numbers displayed beside them.

**Overclaimed exactness, then a false explanation for it.** The block first said
the cost-matched cap factor was solved "so that its effective rate equals the
amortizing loan's". It does not equal it. The replacement then explained the
residual by saying duration integrality makes an exact match unattainable —
which is **also wrong (D-056)**. Within a fixed paying-month count the clipped
final payment varies continuously with `f`, so APR does too, and a numerical
root exists at approximately `f = 1.09462066267694`. The residual is a
**grid-resolution** result: the registered `1.0945` is the nearest point the
0.0005-step search visited.

Neither defect changed a number. Both changed what the page promised about a
number, which is the harder failure to notice.
"""
import contextlib
import copy
import json
import os
import re
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main  # noqa: E402
import lab  # noqa: E402

client = TestClient(main.app)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(REPO, "research", "results")
LAB_HTML = os.path.join(REPO, "frontend", "lab.html")

pytestmark = pytest.mark.skipif(not lab.artifacts_available(),
                                reason="research artifacts not present")


def _read(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as fh:
        return json.load(fh)


def _pricing_reference():
    return client.get("/api/lab/manifest").json()["pricing_reference"]


@contextlib.contextmanager
def _cache(**entries):
    """Swap entries in the Lab's artifact cache, then put them back.

    This never touches a file on disk. Registered artifacts are evidence; a test
    that rewrote one to prove a point would be destroying the thing it was
    checking.
    """
    saved = dict(lab._CACHE)
    lab._CACHE.update(entries)
    try:
        yield
    finally:
        lab._CACHE.clear()
        lab._CACHE.update(saved)


# ── 1. the values come from the canonical file ──────────────────────────────

def test_pricing_values_and_spec_version_come_from_the_canonical_file():
    canon = _read("validation_v2_canonical.json")
    ref = _pricing_reference()

    assert ref["artifact"] == "validation_v2_canonical.json"
    assert ref["equal_cost"] == canon["pricing"]["equal_cost"]
    assert ref["benchmark_b_apr"] == canon["pricing"]["benchmark_b_apr"]

    # The regression that motivated the suite: a canonical name beside a null
    # spec version is the signature of reading the raw file.
    assert ref["spec_version"], "spec_version is null — the raw file is being read"
    assert ref["spec_version"] == canon["canonical"]["spec_version"]
    assert "A-9" in ref["spec_version"], (
        "the pricing block should carry the current specification, which runs "
        "through A-9")


def test_the_raw_file_could_not_have_supplied_the_spec_version():
    """Proves the previous assertion is not vacuous.

    If the raw file happened to carry a `canonical` block too, reading the wrong
    file would produce a correct-looking spec version and the test above would
    pass while the defect stayed. It does not carry one.
    """
    raw = _read("validation_v2.json")
    assert "canonical" not in raw, (
        "the raw artifact now has a canonical block; "
        "test_pricing_values_and_spec_version_come_from_the_canonical_file no "
        "longer distinguishes the two files and needs a different discriminator")


# ── 2. the checksum describes that same file ────────────────────────────────

def test_the_emitted_checksum_describes_the_named_canonical_file():
    import hashlib

    ref = _pricing_reference()
    path = os.path.join(RESULTS, ref["artifact"])
    on_disk = hashlib.sha256(open(path, "rb").read()).hexdigest()

    assert ref["sha256"] == on_disk, (
        f"the page publishes {ref['sha256']} for {ref['artifact']}, but that "
        f"file hashes to {on_disk}. A reader checksumming the named file would "
        f"conclude the page had been tampered with.")

    # And it is not accidentally the raw file's hash.
    raw_hash = hashlib.sha256(
        open(os.path.join(RESULTS, "validation_v2.json"), "rb").read()).hexdigest()
    assert ref["sha256"] != raw_hash


def test_the_provenance_record_and_the_named_file_agree():
    prov = _read("validation_v2_provenance.json")
    assert _pricing_reference()["sha256"] == prov["canonical_sha256"]


# ── 3. mixed provenance cannot pass silently ────────────────────────────────

def test_changing_the_canonical_input_moves_the_published_block():
    """The read must actually be bound to the canonical artifact."""
    poisoned = copy.deepcopy(_read("validation_v2_canonical.json"))
    poisoned["pricing"]["benchmark_b_apr"] = 0.123456
    poisoned["canonical"]["spec_version"] = "SENTINEL SPEC"

    with _cache(validation_v2_canonical=poisoned):
        ref = _pricing_reference()
        assert ref["benchmark_b_apr"] == 0.123456
        assert ref["spec_version"] == "SENTINEL SPEC"


def test_changing_the_raw_input_cannot_move_the_published_block():
    """The mirror image, and the one that actually failed.

    Under the defect this test would have gone the other way: poisoning the raw
    file moved the displayed values while the canonical name and checksum
    stayed put — mixed provenance, published without a warning.
    """
    before = _pricing_reference()

    poisoned = copy.deepcopy(_read("validation_v2.json"))
    poisoned["pricing"]["benchmark_b_apr"] = 0.987654
    poisoned["pricing"]["equal_cost"]["apr"] = 0.987654
    poisoned["canonical"] = {"spec_version": "RAW FILE SENTINEL"}

    with _cache(validation_v2=poisoned):
        after = _pricing_reference()

    assert after == before, (
        "the pricing block moved when only the RAW artifact changed, so it is "
        "reading a file it does not name or checksum")
    assert after["spec_version"] != "RAW FILE SENTINEL"
    assert after["benchmark_b_apr"] != 0.987654


def test_the_residual_is_recomputed_from_the_artifact_not_hard_coded():
    """The quoted residual must follow the file, or it will outlive it."""
    poisoned = copy.deepcopy(_read("validation_v2_canonical.json"))
    # Move the benchmark a clean 1 percentage point above the achieved rate.
    poisoned["pricing"]["benchmark_b_apr"] = \
        poisoned["pricing"]["equal_cost"]["apr"] + 0.01

    with _cache(validation_v2_canonical=poisoned):
        ref = _pricing_reference()
        assert ref["grid_pricing"]["residual_pp"] == pytest.approx(1.0)
        assert "1.00000 percentage points" in ref["note"]

    # Back to the real file: the real residual, from the real numbers.
    canon = _read("validation_v2_canonical.json")
    expected = abs(canon["pricing"]["benchmark_b_apr"]
                   - canon["pricing"]["equal_cost"]["apr"]) * 100.0
    assert _pricing_reference()["grid_pricing"]["residual_pp"] == pytest.approx(expected)


def test_an_exact_grid_hit_would_be_described_as_exact():
    """The wording is derived, not asserted, so it survives a better sweep."""
    poisoned = copy.deepcopy(_read("validation_v2_canonical.json"))
    poisoned["pricing"]["benchmark_b_apr"] = poisoned["pricing"]["equal_cost"]["apr"]

    with _cache(validation_v2_canonical=poisoned):
        ref = _pricing_reference()
        low = ref["note"].lower()
        assert ref["grid_pricing"]["exact_match"] is True
        # The wording is derived, so a grid that happens to land on target says
        # so. It still must not claim mathematical exactness for a float
        # comparison -- "to displayed precision" is the honest form (D-057).
        assert "lands on the benchmark" in low
        assert "displayed precision" in low
        assert "grid-resolution result" not in low, (
            "on an exact hit there is no residual to attribute to the grid")


# ── 4. no active copy conditions the rate on completion ─────────────────────

#: Phrasings that put the RATE under the completion denominator. Duration is
#: legitimately conditioned on completion, so patterns must not fire on it.
#:
#: The gap class excludes `"` as well as `.`. Without it the scanner joined two
#: adjacent JSON fields — `"apr_label": "...rate-defined paths",
#: "duration_label": "Mean duration among completed paths"` — and reported a
#: correct pair of labels as a violation. A quote is a sentence boundary in a
#: serialised payload just as a full stop is in prose.
_GAP = r'[^."]'
RATE_UNDER_COMPLETION = [
    re.compile(rf"\b(apr|rate){_GAP}{{0,60}}among completed", re.I),
    re.compile(rf"\b(apr|rate){_GAP}{{0,60}}only over (?:the )?paths that (?:reached|complete)", re.I),
    re.compile(rf"mean (?:duration and mean )?rate{_GAP}{{0,80}}reached the repayment target", re.I),
    re.compile(rf"\b(apr|rate){_GAP}{{0,60}}excludes? (?:all )?(?:non-completing|incomplete) paths", re.I),
]


def _active_copy() -> str:
    """Everything the Lab actually shows a reader.

    Deliberately the API payloads and the page, NOT the Python source: the
    module's docstrings describe the withdrawn wording in order to explain why
    it was withdrawn, and a scanner that could not tell those apart would force
    the explanation to be deleted.
    """
    parts = [json.dumps(client.get("/api/lab/manifest").json())]
    for s in client.get("/api/lab/scenarios").json()["scenarios"]:
        parts.append(json.dumps(
            client.get(f"/api/lab/comparison/{s['key']}").json()))
    u = client.get("/api/lab/underreporting")
    if u.status_code == 200:
        parts.append(json.dumps(u.json()))
    parts.append(open(LAB_HTML, encoding="utf-8").read())
    return "\n".join(parts)


def test_no_active_lab_copy_conditions_the_rate_on_completion():
    copy_text = _active_copy()
    hits = []
    for pat in RATE_UNDER_COMPLETION:
        hits += [m.group(0)[:120] for m in pat.finditer(copy_text)]
    assert not hits, (
        "active Lab copy still puts the effective rate under the COMPLETION "
        "denominator. A-9 separated them: a path can miss the contractual "
        "target and still have a defined rate over the observed window.\n  " +
        "\n  ".join(hits[:5]))


def test_the_rate_and_duration_denominators_are_both_stated():
    """Not saying the wrong thing is only half of it."""
    d = client.get("/api/lab/comparison/closure_m13").json()
    apr_def = d["metric_definitions"]["effective_apr"]
    text = (apr_def["definition"] + " " + apr_def["caveat"]).lower()
    assert "duration" in text and "completing paths" in text
    assert "defined internal rate of return" in text
    assert "observed window" in text
    assert "portfolio" in text

    arm = next(a for a in d["arms"] if a["id"] == "RBF-ILL")
    assert arm["apr_defined_share"] == 1.0
    assert arm["completed_share"] < 1.0
    assert arm["denominators_differ"] is True
    assert "rate-defined" in arm["apr_label"]
    assert "completed" in arm["duration_label"]


# ── 5. no active copy implies exact reference-path equality ─────────────────

EXACT_EQUALITY = [
    re.compile(r"(?:rate|cost)[^.]{0,40}equals the amortiz", re.I),
    re.compile(r"so that its effective rate equals", re.I),
    re.compile(r"cost (?:exactly )?(?:equals|matches) the (?:amortizing|loan|benchmark)", re.I),
    re.compile(r"equal[- ]effective[- ]cost cap factor (?:solves|gives) an exact", re.I),
]

#: The three withdrawn explanations for the residual (D-056). Each was, at some
#: point, live copy on a public page. Banning the words is weaker than
#: understanding why they were wrong, but it stops a regression reaching a
#: reader while nobody is looking.
WITHDRAWN_DISCRETENESS = [
    re.compile(r"cost moves in steps", re.I),
    re.compile(r"achievable APRs?[^.]{0,30}(?:are |form a )?discrete", re.I),
    re.compile(r"attainable APRs?[^.]{0,30}(?:are |form a )?discrete", re.I),
    re.compile(r"exact match is (?:not |un)(?:generally )?(?:attainable|available)", re.I),
    re.compile(r"duration is an integer[^.]{0,60}(?:step|exact|attain)", re.I),
    re.compile(r"integer[- ]valued[^.]{0,60}(?:no exact|not attainable|discrete)", re.I),
]


def test_no_active_lab_copy_explains_the_residual_by_discreteness():
    """The withdrawn family must not reach a reader through the API or page."""
    copy_text = _active_copy()
    hits = []
    for pat in WITHDRAWN_DISCRETENESS:
        hits += [m.group(0)[:120] for m in pat.finditer(copy_text)]
    assert not hits, (
        "active Lab copy explains the pricing residual by duration integrality. "
        "D-056 withdrew that: APR is piecewise continuous in the cap factor and "
        "a numerical root exists at approximately 1.09462066267694. The residual "
        "is a grid-resolution result.\n  " + "\n  ".join(hits[:5]))


def test_the_lab_states_the_corrected_grid_and_continuity_explanation():
    """Not saying the wrong thing is only half. It must say the right thing."""
    note = _pricing_reference()["note"]
    low = note.lower()
    assert "0.0005" in note, "the grid step must be named, since the residual is its consequence"
    assert "grid-resolution" in low or "grid resolution" in low, (
        "the note must attribute the residual to the search grid")
    assert "continuous" in low, "the note must state APR varies continuously within a fixed term"
    assert "numerical root" in low, "the note must call the root numerical, not exact"
    assert "1.09462066267694" in note, "the note must quote the approximate root"
    assert "kink" in low and "gap" in low, (
        "the note must distinguish kinks at term changes from gaps in the range")
    # And it must not overclaim the root.
    assert "exact root" not in low
    assert re.search(r"exactly[^.]{0,40}1\.0946", note) is None


def test_the_registered_grid_result_is_unchanged_by_the_correction():
    """The correction is about the explanation, not the number."""
    g = _pricing_reference()["grid_pricing"]
    assert g["f_star"] == 1.0945
    assert g["achieved_apr"] == 0.1953765648184853
    assert g["benchmark_apr"] == 0.19561817146154947
    assert g["residual_pp"] == pytest.approx(0.02416, abs=5e-6)
    assert g["exact_match"] is False


def test_no_active_lab_copy_implies_exact_reference_path_equality():
    copy_text = _active_copy()
    hits = []
    for pat in EXACT_EQUALITY:
        hits += [m.group(0)[:120] for m in pat.finditer(copy_text)]
    assert not hits, (
        "active Lab copy claims the cost-matched contract's rate EQUALS the "
        "amortizing loan's. It does not: f* is the nearest point on a swept "
        "grid and a residual remains.\n  " + "\n  ".join(hits[:5]))


def test_the_grid_basis_and_residual_are_stated_where_the_claim_is_made():
    canon = _read("validation_v2_canonical.json")
    a = canon["pricing"]["equal_cost"]["apr"]
    t = canon["pricing"]["benchmark_b_apr"]

    ref = _pricing_reference()
    low = ref["note"].lower()
    assert "grid" in low
    # Was: `assert "not an exact match" in ref["note"]`. That phrasing carried
    # the withdrawn implication that no f attains the target. The claim now
    # required is stronger AND correct: nearest point found on a stepped grid,
    # residual attributed to resolution (D-056/D-057).
    assert "nearest point found on the registered" in low
    assert "grid-resolution" in low or "grid resolution" in low
    assert f"{a:.6%}" in ref["note"] and f"{t:.6%}" in ref["note"]

    d = client.get("/api/lab/comparison/stable").json()
    note = next(x for x in d["arms"] if x["id"] == "RBF-EQ")["note"]
    assert "grid" in note.lower() and "numerical root" in note.lower()

    caveats = " ".join(c["text"] for c in d["caveats"])
    assert "grid" in caveats.lower() and "numerical root" in caveats.lower()


def test_the_chart_label_carries_the_artifacts_own_cap_factor():
    """It used to be the string "Revenue-based 1.0945×", hand-typed."""
    d = client.get("/api/lab/comparison/stable").json()
    for arm_id, stem in (("RBF-EQ", "baseline_equalcost_v2"),
                         ("RBF-ILL", "baseline_v3")):
        arm = next(a for a in d["arms"] if a["id"] == arm_id)
        f = _read(f"{stem}_canonical.json")["terms"]["f"]
        assert arm["cap_factor"] == f
        assert f"{f:g}".rstrip("0").rstrip(".") in arm["chart_label"].replace("0×", "×")
        assert arm["chart_label"].endswith("×")
