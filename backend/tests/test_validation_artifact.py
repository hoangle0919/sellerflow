"""`validation_v1` must be checksum-verifiable and numerically identical to its source.

The validation battery is where the two most quotable numbers in the project
live — the reference-path cost-matched cap `f* = 1.0945` and Benchmark B's
19.5618% APR. Until D-038 it was the only registered result with no canonical
form, which meant the figures most likely to appear in a write-up were the ones
a reader could least easily check.

These tests hold the canonicalization to the promise it was made under: it is a
re-expression, not a recomputation. If a single scalar moves, that promise is
broken and the artifact must not be cited.
"""
import hashlib
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(REPO, "research", "results")
SOURCE = os.path.join(RESULTS, "validation_v1.json")
CANON = os.path.join(RESULTS, "validation_v1_canonical.json")
PROV = os.path.join(RESULTS, "validation_v1_provenance.json")

pytestmark = pytest.mark.skipif(
    not os.path.exists(CANON), reason="validation_v1 canonical artifact not present")


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _scalars(obj, path="", out=None):
    out = {} if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            _scalars(v, f"{path}/{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _scalars(v, f"{path}[{i}]", out)
    else:
        out[path] = obj
    return out


def test_canonical_checksum_matches_its_provenance_record():
    got = hashlib.sha256(open(CANON, "rb").read()).hexdigest()
    assert got == _load(PROV)["canonical_sha256"], (
        "canonical file and its provenance record disagree — one of them was "
        "edited by hand")


def test_every_scalar_from_the_source_survives_unchanged():
    """The load-bearing test. Canonicalization may reorganise; it may not round,
    retype, drop or recompute."""
    src = _load(SOURCE)
    canon = _load(CANON)
    shared = {k: v for k, v in src.items() if k != "_meta"}
    src_nums = _scalars(shared)
    canon_nums = _scalars({k: v for k, v in canon.items() if k in shared})

    drift = {k: (v, canon_nums.get(k)) for k, v in src_nums.items()
             if canon_nums.get(k, object()) != v}
    assert not drift, (
        f"{len(drift)} scalar(s) changed during canonicalization:\n  " +
        "\n  ".join(f"{k}: {a!r} -> {b!r}" for k, (a, b) in list(drift.items())[:10]))
    assert len(src_nums) > 100, "source unexpectedly small; check the fixture"


def test_the_headline_pricing_numbers_are_traceable():
    """Named explicitly, because these are the two that will be quoted."""
    src, canon = _load(SOURCE), _load(CANON)
    assert canon["pricing"]["equal_cost"] == src["pricing"]["equal_cost"]
    assert canon["pricing"]["benchmark_b_apr"] == src["pricing"]["benchmark_b_apr"]
    blob = json.dumps(canon["pricing"])
    assert "1.0945" in blob, "f* missing from the canonical pricing block"


def test_the_run_date_moved_to_provenance_rather_than_vanishing():
    """It was the only non-deterministic field. Dropping it would lose the
    execution record; leaving it in the body would break reproducibility."""
    canon, prov = _load(CANON), _load(PROV)
    assert "date" not in json.dumps(canon.get("config", {})), \
        "a run date is still inside the canonical body"
    assert prov.get("original_run_date"), \
        "the source run date was dropped instead of moved to provenance"


def test_registered_baseline_checksums_are_untouched():
    """Canonicalizing the battery must not disturb anything already registered."""
    expected = {
        "baseline_v2_canonical.json":
            "264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849",
        "baseline_equalcost_v1_canonical.json":
            "6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7",
        "baseline_closure_v1_canonical.json":
            "0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470",
        "baseline_closure_equalcost_v1_canonical.json":
            "49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9",
    }
    for name, want in expected.items():
        p = os.path.join(RESULTS, name)
        assert os.path.exists(p), f"{name} missing"
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want, f"{name} checksum changed: {got}"
