"""Active surfaces cite current artifacts; historical records may cite old ones.

The A-9 migration renamed five artifacts. A rename sweep that matches
`<name>_canonical` and bare `<name> →` misses every other shape a citation can
take -- the deck's slide-8 footer named two artifacts joined by "and" and kept
pointing at the superseded pair through two review rounds.

This scanner is deliberately NOT a global ban. Superseded artifacts are
preserved evidence and must remain citable in the places that record what was
published: checksum tables under a "Superseded" heading, dated decision-log
entries, the results registry's migration comparison. Banning the names
outright would delete the audit trail in order to tidy the current one.

So the rule is contextual: a superseded stem is fine inside a block marked as
historical, and a defect anywhere else.
"""
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bare stems too, not only the `_canonical` form. `validation_v1.json` and
# `baseline_v2.json` are the raw pre-canonicalization files, and a reproduction
# command or generator docstring pointing at one of them sends a reader to a
# superseded input just as effectively as a checksum row would. The `_canonical`
# suffix was where the last sweep stopped, which is why `lab.manifest()` went on
# reporting `validation_v1.json` while loading `validation_v2`.
SUPERSEDED = re.compile(
    r"baseline_v2_canonical|baseline_v2_provenance|baseline_v2\.json"
    r"|baseline_equalcost_v1|baseline_closure_v1"
    r"|baseline_closure_equalcost_v1"
    r"|validation_v1_canonical|validation_v1_provenance|validation_v1\.json"
    r"|\bbaseline_v2\b|\bvalidation_v1\b")

CURRENT = ("baseline_v3", "baseline_equalcost_v2", "baseline_closure_v2",
           "baseline_closure_equalcost_v2", "validation_v2")

#: Surfaces a reader meets as current claims. Historical documents
#: (DECISION_LOG, CORRECTED_CLAIMS, BASELINE_FINDINGS, evidence/) are absent
#: on purpose -- their whole function is to record superseded state.
ACTIVE_SURFACES = (
    "research/publication/MANUSCRIPT.md",
    "research/publication/PAPER_OUTLINE.md",
    "research/publication/CAREER_PACKAGE.md",
    "research/publication/build_deck.js",
    "backend/lab.py",
    "frontend/lab.html",
    "research/verify_reproduction.py",
    "research/canonicalize_validation.py",
    "RESEARCH_MANIFEST.md",
    "research/CLAIM_LEDGER.md",
    "research/RESULTS_REGISTRY.md",
    # Active generator documentation. A docstring naming a superseded output is
    # read as instruction by the next person to run the script.
    "research/run_baseline.py",
    "research/run_equal_cost_baseline.py",
    "research/run_closure_baseline.py",
    "research/run_validation.py",
    "research/rbf_sim/README.md",
    "research/rbf_sim/canonical.py",
)

#: A line, or the heading above it, that puts a citation in historical context.
HISTORICAL_MARKER = re.compile(
    r"supersede|superseded|historical|preserved byte-for-byte|~~"
    r"|D-04[0-9]|frozen|withdrawn|former|previously|SUPERSEDED", re.I)

#: How far back to look for a heading that governs the line.
BLOCK_LOOKBACK = 12


def _in_historical_block(lines, i):
    """A citation is historical if its own line, or a nearby heading, says so."""
    if HISTORICAL_MARKER.search(lines[i]):
        return True
    for j in range(max(0, i - BLOCK_LOOKBACK), i):
        line = lines[j].strip()
        is_heading = (
            line.startswith(("#", ">", "**"))
            or "| Superseded" in line
            # An italic caption row inside a table governs the rows beneath it.
            # Markdown has no other way to scope a table, and the migration
            # comparison in RESULTS_REGISTRY needs exactly that.
            or re.match(r"^\|\s*\*\(.*\)\*\s*\|", line) is not None
        )
        if is_heading and HISTORICAL_MARKER.search(line):
            return True
    return False


@pytest.mark.parametrize("rel", ACTIVE_SURFACES)
def test_active_surfaces_cite_current_artifacts(rel):
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        pytest.skip(f"{rel} not present")
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()

    offenders = [
        (i + 1, lines[i].strip()[:120])
        for i in range(len(lines))
        if SUPERSEDED.search(lines[i]) and not _in_historical_block(lines, i)
    ]
    assert not offenders, (
        f"{rel} cites a superseded artifact outside a historical block:\n" +
        "\n".join(f"  line {n}: {text}" for n, text in offenders) +
        "\n\nCurrent stems are: " + ", ".join(CURRENT) +
        "\nIf the citation is genuinely historical, put it under a heading that "
        "says so rather than removing the record."
    )


def test_the_scanner_would_catch_the_slide_8_regression():
    """A check that cannot fail is not a check.

    The exact footer that survived two rounds: two artifacts joined by "and",
    which no `_canonical`-suffix sweep matches.
    """
    lines = ['  source(s, "baseline_closure_v1 and baseline_closure_equalcost_v1 '
             '→ /scenarios/*/RBF");']
    assert SUPERSEDED.search(lines[0])
    assert not _in_historical_block(lines, 0)


def test_the_scanner_permits_a_marked_historical_table():
    """And it must not delete the audit trail it is protecting."""
    lines = [
        "**Superseded by A-9 (D-049), preserved byte-for-byte.**",
        "",
        "| Superseded artifact | SHA-256 |",
        "|---|---|",
        "| `baseline_v2_canonical.json` | `264d319b...` |",
    ]
    assert SUPERSEDED.search(lines[4])
    assert _in_historical_block(lines, 4), (
        "a checksum row under a Superseded heading is the record, not a defect"
    )
