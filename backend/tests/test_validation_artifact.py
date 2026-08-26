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


def test_no_public_surface_renders_the_superseded_determinism_field():
    """`canonical.determinism` still says "produce a byte-identical file" inside
    all five artifacts — the claim D-041 withdrew.

    D-044 settled this: the artifacts are NOT regenerated. Their checksums and
    historical metadata stand; the sentence is superseded in the registry, and
    the containment is that no surface renders it. This test IS that
    containment, so it is the thing standing between a superseded claim and a
    reader."""
    surfaces = []
    for root, _dirs, files in os.walk(os.path.join(REPO, "backend")):
        if "__pycache__" in root or "/tests" in root:
            continue
        surfaces += [os.path.join(root, f) for f in files if f.endswith(".py")]
    surfaces += [os.path.join(REPO, "frontend", f)
                 for f in os.listdir(os.path.join(REPO, "frontend"))
                 if f.endswith(".html")]
    leaking = []
    for path in surfaces:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            if "determinism" in fh.read():
                leaking.append(os.path.relpath(path, REPO))
    assert not leaking, (
        "a public surface reads or renders `canonical.determinism`, which "
        f"carries the withdrawn byte-reproducibility claim: {leaking}")

    # And confirm the field really is still there, so this test cannot pass
    # merely because the artifact changed shape without anyone noticing.
    assert "determinism" in _load(CANON).get("canonical", {}), (
        "the superseded field is gone — if an artifact was regenerated, the "
        "registry note and the checksums both need revisiting")


# Superseded by A-9. Preserved byte-for-byte as historical evidence: the
# published figures were computed from these, so the record of what was
# published has to remain verifiable even though the method was wrong.
SUPERSEDED_CHECKSUMS = {
    "baseline_v2_canonical.json":
        "264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849",
    "baseline_equalcost_v1_canonical.json":
        "6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7",
    "baseline_closure_v1_canonical.json":
        "0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470",
    "baseline_closure_equalcost_v1_canonical.json":
        "49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9",
    "validation_v1_canonical.json":
        "f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4",
}

# The current generation, produced under A-9.
CURRENT_CHECKSUMS = {
    "baseline_v3_canonical.json":
        "363729016298b3d7307ec066c8df37c60e1c9aa2582db2c058c5cc74df894d55",
    "baseline_equalcost_v2_canonical.json":
        "b3ebfe6a5a7e7f48726d7e501295b02f84258a3fe9ee4e048875125b1270e0ee",
    "baseline_closure_v2_canonical.json":
        "21b8e207ff2db9ac866b8cb2bab47c8c2e434d2bff03d802eb6f53a66fdcea4b",
    "baseline_closure_equalcost_v2_canonical.json":
        "e1e6d81bbeeb60f0e923c27a8df44d26674f4b8ad788c6c9796c17ef40622665",
    "validation_v2_canonical.json":
        "4f26f04e3e0f16b14eea8b9bfcd46c05b3cfc86af8ae8e388c8d22d7f9c6dd94",
}


def test_superseded_artifacts_are_preserved_byte_for_byte():
    """A-9 replaced these; it must never have deleted or rewritten them."""
    for name, want in SUPERSEDED_CHECKSUMS.items():
        p = os.path.join(RESULTS, name)
        assert os.path.exists(p), (
            f"{name} is missing. Superseded artifacts are evidence of what was "
            "published and are retained, not removed."
        )
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want, f"{name} checksum changed: {got}"


def test_current_artifacts_match_their_registered_checksums():
    for name, want in CURRENT_CHECKSUMS.items():
        p = os.path.join(RESULTS, name)
        assert os.path.exists(p), f"{name} missing"
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want, f"{name} checksum changed: {got}"


def test_current_artifacts_carry_the_new_denominator_fields():
    """A-9's whole point: the denominator is reported, not inferred."""
    body = _load(os.path.join(RESULTS, "baseline_closure_v2_canonical.json"))
    arm = body["scenarios"]["closure_m13"]["RBF"]
    for field in ("apr_defined_count", "apr_defined_rate",
                  "completed_count", "completed_rate"):
        assert field in arm, f"closure_m13/RBF is missing {field}"
    assert arm["apr_defined_count"] > arm["completed_count"], (
        "closure_m13 is the scenario where the two denominators come apart; "
        "if they no longer do, the A-9 conditioning claim needs re-deriving"
    )
    assert body["canonical"]["schema_version"] == "2.0"
