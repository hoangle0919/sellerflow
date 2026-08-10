"""The claim ledger must stay true to the artifacts it cites.

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
    v = _artifact("validation_v1")
    b = _artifact("baseline_v2")
    c = _artifact("baseline_closure_v1")
    ce = _artifact("baseline_closure_equalcost_v1")
    txt = _text()

    cases = [
        ("1.0945", v["pricing"]["equal_cost"]["f_star"], 1.0945),
        ("19.5377", v["pricing"]["equal_cost"]["apr"] * 100, 19.5377),
        ("19.5618", v["pricing"]["benchmark_b_apr"] * 100, 19.5618),
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
    for stem in ("baseline_closure_v1", "baseline_closure_equalcost_v1"):
        rate = _artifact(stem)["scenarios"]["closure_m7"]["RBF"]["incomplete_recovery_rate"]
        assert rate == 1.0, f"{stem}: closure_m7 incomplete rate is {rate}, expected 1.0"


def test_withdrawn_section_names_every_retracted_claim():
    txt = _text().lower()
    for fragment in ("0.92 auc", "2.3×", "confidence interval",
                     "instead of defaulting", "equal cost", "5.77%"):
        assert fragment.lower() in txt, (
            f"withdrawn claim {fragment!r} is missing from the ledger's §6 — a "
            f"retraction that is not written down will be repeated")
