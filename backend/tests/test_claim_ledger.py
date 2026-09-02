"""CURRENT-CLAIM checks read the CURRENT artifacts.

These assertions are about what the project may say today, so they must read
the A-9 generation -- baseline_v3, baseline_equalcost_v2, the two closure v2
tracks and validation_v2. They previously read the superseded v1/v2 files,
which meant every headline figure was being validated against the artifacts
the publication no longer cites.

Preservation of the superseded artifacts is a separate concern with its own
test: `test_validation_artifact.py::test_superseded_artifacts_are_preserved_byte_for_byte`.
Those files must never change; these claims must never come from them.

The claim ledger must stay true to the artifacts it cites.

A ledger is only worth having if it fails when it drifts. These tests read
`research/CLAIM_LEDGER.md` as data: every checksum it prints must match the file
on disk, and every headline figure it quotes must still be derivable from the
artifact it names. Otherwise the ledger becomes what it was written to prevent —
a confident-looking document that nobody re-checked.
"""
import hashlib
import json
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER = os.path.join(REPO, "research", "CLAIM_LEDGER.md")
RESULTS = os.path.join(REPO, "research", "results")

pytestmark = pytest.mark.skipif(not os.path.exists(LEDGER), reason="ledger absent")


def _text():
    with open(LEDGER, encoding="utf-8") as fh:
        return fh.read()


def _artifact(stem):
    with open(os.path.join(RESULTS, f"{stem}_canonical.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_every_checksum_in_the_ledger_matches_the_file_on_disk():
    rows = re.findall(r"`(\w+_canonical\.json)`\s*\|\s*`([0-9a-f]{64})`", _text())
    assert len(rows) >= 5, f"expected >=5 checksum rows, parsed {len(rows)}"
    for name, claimed in rows:
        path = os.path.join(RESULTS, name)
        assert os.path.exists(path), f"ledger cites {name}, which does not exist"
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        assert got == claimed, (
            f"{name}: ledger says {claimed[:16]}…, file is {got[:16]}… — the "
            f"ledger was not updated when the artifact changed")


def test_claim_ids_are_unique():
    ids = re.findall(r"\*\*([MSPIQ]-\d+)\*\*", _text())
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate claim IDs: {sorted(dupes)}"
    assert len(ids) >= 18, f"only {len(ids)} claims found; ledger looks truncated"


def test_headline_figures_still_match_their_artifacts():
    """Spot-checks the numbers most likely to be quoted in the paper."""
    v = _artifact("validation_v2")
    b = _artifact("baseline_v3")
    c = _artifact("baseline_closure_v2")
    ce = _artifact("baseline_closure_equalcost_v2")
    txt = _text()

    cases = [
        ("1.0945", v["pricing"]["equal_cost"]["f_star"], 1.0945),
        # Six decimals, because P-1 must show the residual against the
        # reference rather than imply an exact cost match (Gate A round 2).
        ("19.537656", v["pricing"]["equal_cost"]["apr"] * 100, 19.537656),
        ("19.561817", v["pricing"]["benchmark_b_apr"] * 100, 19.561817),
        ("18.718", b["scenarios"]["severe_downturn"]["RBF"]["duration_mean"], 18.718),
        ("76.2", c["scenarios"]["closure_m13"]["RBF"]["incomplete_recovery_rate"] * 100, 76.2),
        ("7.6", ce["scenarios"]["closure_m13"]["RBF"]["incomplete_recovery_rate"] * 100, 7.6),
    ]
    for literal, actual, expected in cases:
        assert literal in txt, f"ledger no longer quotes {literal}"
        assert round(actual, 4) == pytest.approx(expected, abs=5e-4), (
            f"artifact value for {literal} drifted to {actual}")


def test_closure_falsifies_the_default_prevention_claim():
    """The specific fact that retires 'extends the term instead of defaulting'.

    Asserted at BOTH registered cap factors, because a reader's first instinct
    is that the illustrative price is what causes the failure. It is not.
    """
    for stem in ("baseline_closure_v2", "baseline_closure_equalcost_v2"):
        rate = _artifact(stem)["scenarios"]["closure_m7"]["RBF"]["incomplete_recovery_rate"]
        assert rate == 1.0, f"{stem}: closure_m7 incomplete rate is {rate}, expected 1.0"


def test_f_star_is_presented_as_a_grid_match_with_its_residual():
    """P-1. `f*` is the nearest point on the swept cap-factor grid, not an
    exact cost match. Stating it without the residual implies equality."""
    v = _artifact("validation_v2")
    residual = abs(v["pricing"]["equal_cost"]["apr"]
                   - v["pricing"]["benchmark_b_apr"]) * 100
    assert round(residual, 5) == pytest.approx(0.02416, abs=5e-5), \
        f"residual drifted to {residual:.6f}pp"
    txt = _text()
    assert "0.02416" in txt, "P-1 must state the residual in percentage points"
    # Matched on the claim, not one phrasing of it. D-056 replaced "nearest grid
    # match" with the more precise "nearest point on the registered 0.0005-step
    # grid", because the residual is a property of the GRID that was searched --
    # a numerical root sits at approximately f = 1.09462066267694. Pinning the old
    # words would have blocked a correction that strengthens the same claim.
    assert ("nearest point on the registered" in txt or "nearest grid match" in txt
            or "grid match" in txt), "P-1 must not imply an exact cost match"
    # And the withdrawn reasoning must not come back anywhere in the ledger.
    for banned in ("achievable APRs form a discrete set",
                   "duration is integer-valued, so effective cost moves in steps"):
        assert banned.lower() not in txt.lower(), (
            f"the discrete-APR reasoning withdrawn by D-056 reappeared: {banned!r}")


def test_rbf_g_floor_never_binds_but_the_ceiling_does():
    """S-6. The first draft of the ledger said RBF-G was 'bit-identical to RBF
    in all ten scenarios' and credited the floor. The artifact it cited says
    otherwise, and no test checked it — so the false claim shipped."""
    bp = _artifact("validation_v2")["rbf_g_breakpoint"]["pmin0.25_hard0.5"]
    assert bp["floor_months"] == 0, "the floor is claimed never to bind"
    assert bp["reachable"] is False, "the registered setting is claimed unreachable"
    assert bp["ceiling_months"] == 6009, (
        f"ledger S-6 cites 6,009 ceiling months, artifact says {bp['ceiling_months']}")

    scen = _artifact("baseline_v3")["scenarios"]
    differing = [s for s, arms in scen.items()
                 if "RBF-G" in arms and arms["RBF-G"] != arms["RBF"]]
    assert len(differing) == 6, (
        f"ledger S-6 says 6 of 10 scenarios differ; artifact says {len(differing)}: "
        f"{sorted(differing)}")

    txt = _text()
    assert "bit-identical" not in txt.split("Supersedes")[0] or "~~" in txt, \
        "the retracted 'bit-identical' wording must be struck, not restated"


def test_rho_star_is_never_quoted_without_its_cap_factor():
    """M-6. rho* depends on f — 11/12 at f=1.20, 0.9086 at f*=1.0945. Quoting
    11/12 as *the* threshold is the price/structure conflation M-3 warns about."""
    txt = _text()
    if "11/12" in txt:
        window = txt[max(0, txt.index("11/12") - 400): txt.index("11/12") + 400]
        assert "1.20" in window, "11/12 quoted without naming the cap factor f = 1.20"
        assert "0.9086" in window or "1.0945" in window, \
            "11/12 quoted without the contrasting value at f*"


def test_withdrawn_section_names_every_retracted_claim():
    txt = _text().lower()
    for fragment in ("0.92 auc", "2.3×", "confidence interval",
                     "instead of defaulting", "equal cost", "5.77%"):
        assert fragment.lower() in txt, (
            f"withdrawn claim {fragment!r} is missing from the ledger's §6 — a "
            f"retraction that is not written down will be repeated")
