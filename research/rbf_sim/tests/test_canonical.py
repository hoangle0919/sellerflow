"""Tests for canonical, checksummable artifact serialization (D-027).

The claim under test is narrow and falsifiable: identical code, configuration
and seeds produce a BYTE-IDENTICAL canonical file, and everything that varies
between runs is confined to the provenance sidecar.
"""
import json
import os

import pytest

from rbf_sim import canonical as C

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "results")

PAYLOAD = {
    "run": "unit",
    "date": "2026-08-07",                 # execution fact — must be stripped
    "timestamp": "12:00:00",              # ditto
    "n_paths": 500,
    "base_seed": 20260803,
    "scenarios": {"b": {"x": 1.5}, "a": {"y": 2.5}},
}
CONFIG = {"scenarios": ["a", "b"], "n_paths": 500}
KW = dict(scenario_config=CONFIG, spec_version="spec v1.0")


# ── the encoding is deterministic ───────────────────────────────────────────

def test_same_object_encodes_to_identical_bytes():
    assert C.canonical_bytes(PAYLOAD) == C.canonical_bytes(PAYLOAD)


def test_dict_insertion_order_does_not_change_the_encoding():
    a = {"z": 1, "a": 2, "m": {"q": 1, "b": 2}}
    b = {"a": 2, "m": {"b": 2, "q": 1}, "z": 1}
    assert a == b
    assert C.canonical_bytes(a) == C.canonical_bytes(b)
    assert C.checksum(a) == C.checksum(b)


def test_encoding_is_ascii_safe():
    """Non-ASCII must not make the bytes locale- or encoding-dependent."""
    payload = {"note": "SIMULATED — no observed seller data (đồng)"}
    raw = C.canonical_bytes(payload)
    assert all(byte < 128 for byte in raw)
    assert json.loads(raw.decode())["note"] == payload["note"]


def test_encoding_is_a_fixed_point_under_round_trip():
    """Regression guard. Integer dict keys once made the encoding non-idempotent:
    {6: .., 12: ..} sorted numerically on write and lexicographically on re-read,
    so a consumer who re-encoded the artifact got a different checksum than the
    file carried. Keys are normalised to str before encoding."""
    payload = {"post_shock_recovery": {6: 1.0, 12: 2.0},
               "recovery_ratio": {12: 0.5, 18: 0.7, 24: 0.9},
               "n_high_burden": {0.1: 5, 0.25: 1}}
    once = C.canonical_bytes(payload)
    twice = C.canonical_bytes(json.loads(once.decode()))
    assert once == twice
    assert C.checksum(payload) == C.checksum(json.loads(once.decode()))


def test_integer_and_string_keys_encode_identically():
    assert C.canonical_bytes({6: "a", 12: "b"}) == C.canonical_bytes({"6": "a", "12": "b"})


def test_float_repr_round_trips_on_this_interpreter():
    """The encoding relies on shortest round-trip float repr. Asserted on the
    running interpreter rather than assumed across versions."""
    vals = [0.1, 1 / 3, 1e-8, 240_000_000.0, 17_076_923.076923076, 2 ** 53 + 1.0]
    decoded = json.loads(C.canonical_bytes(vals).decode())
    assert decoded == vals


# ── execution facts are stripped ────────────────────────────────────────────

@pytest.mark.parametrize("key", C.NON_DETERMINISTIC_KEYS)
def test_non_deterministic_keys_are_stripped(key):
    body = C.build_canonical({**PAYLOAD, key: "varies"}, **KW)
    assert key not in body


def test_canonical_contains_no_wall_clock_anywhere():
    body = C.build_canonical(PAYLOAD, **KW)
    blob = C.canonical_bytes(body).decode()
    for marker in ("2026-08-07", "12:00:00", "run_utc"):
        assert marker not in blob, f"wall-clock leaked into canonical: {marker}"


def test_analytical_content_survives_stripping():
    body = C.build_canonical(PAYLOAD, **KW)
    assert body["n_paths"] == 500
    assert body["base_seed"] == 20260803
    assert body["scenarios"] == PAYLOAD["scenarios"]


# ── identity metadata ───────────────────────────────────────────────────────

def test_canonical_block_carries_the_declared_identity_fields():
    meta = C.build_canonical(PAYLOAD, **KW)["canonical"]
    for k in ("schema_version", "spec_version", "generator_fingerprint",
              "scenario_config_hash"):
        assert meta[k], f"missing identity field {k}"


def test_generator_fingerprint_is_stable_within_a_tree():
    assert C.generator_fingerprint() == C.generator_fingerprint()
    assert len(C.generator_fingerprint()) == 64


def test_generator_fingerprint_changes_when_the_source_set_changes():
    """Adding a source to the fingerprint must move it — otherwise the
    fingerprint is not actually a function of the generating code."""
    base = C.generator_fingerprint()
    widened = C.generator_fingerprint(extra_sources=("run_baseline.py",))
    assert base != widened


def test_generator_fingerprint_marks_absent_sources_rather_than_skipping():
    """A deleted generator module must change the fingerprint, not be ignored."""
    a = C.generator_fingerprint(extra_sources=("rbf_sim/does_not_exist.py",))
    b = C.generator_fingerprint()
    assert a != b


def test_config_hash_separates_different_configurations():
    assert C.config_hash(CONFIG) != C.config_hash({**CONFIG, "n_paths": 501})
    assert C.config_hash(CONFIG) == C.config_hash(dict(reversed(list(CONFIG.items()))))


def test_source_commit_is_absent_from_canonical_by_design():
    """Embedding the commit would make the artifact unable to be both committed
    and reproducible: committing changes HEAD, which changes the next run."""
    blob = C.canonical_bytes(C.build_canonical(PAYLOAD, **KW)).decode()
    assert "source_commit" not in blob


# ── the two-run guarantee ───────────────────────────────────────────────────

def test_writing_twice_produces_byte_identical_canonical_files(tmp_path):
    """The headline claim, executed rather than asserted in prose."""
    first = C.write_canonical_pair(PAYLOAD, stem="t", results_dir=str(tmp_path), **KW)
    b1 = open(first["canonical"], "rb").read()
    p1 = open(first["provenance"], "rb").read()

    second = C.write_canonical_pair(PAYLOAD, stem="t", results_dir=str(tmp_path), **KW)
    b2 = open(second["canonical"], "rb").read()

    assert b1 == b2
    assert first["sha256"] == second["sha256"]
    assert C.checksum(json.loads(b1.decode())) == first["sha256"]
    assert p1  # provenance written and non-empty


def test_provenance_records_the_canonical_checksum(tmp_path):
    w = C.write_canonical_pair(PAYLOAD, stem="t", results_dir=str(tmp_path), **KW)
    prov = json.load(open(w["provenance"]))
    body = json.load(open(w["canonical"]))
    assert prov["canonical_sha256"] == C.checksum(body) == w["sha256"]
    assert prov["artifact"] == "t_canonical.json"


def test_provenance_carries_the_execution_facts(tmp_path):
    w = C.write_canonical_pair(PAYLOAD, stem="t", results_dir=str(tmp_path), **KW)
    prov = json.load(open(w["provenance"]))
    assert prov["run_utc"] and prov["python"] and prov["platform"]
    assert "source_commit" in prov          # present here, not in canonical


# ── the committed artifact ──────────────────────────────────────────────────

def _committed(name):
    path = os.path.join(RESULTS, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} not generated in this tree")
    return path


def test_committed_canonical_matches_its_recorded_checksum():
    """Guards against the artifact and its provenance drifting apart."""
    body = json.load(open(_committed("baseline_v2_canonical.json")))
    prov = json.load(open(_committed("baseline_v2_provenance.json")))
    assert C.checksum(body) == prov["canonical_sha256"]


def test_committed_canonical_is_byte_stable_under_reserialization():
    """Reading and re-encoding must reproduce the file exactly, or the file was
    not written under the canonical encoding."""
    path = _committed("baseline_v2_canonical.json")
    raw = open(path, "rb").read()
    assert C.canonical_bytes(json.loads(raw.decode())) == raw


def test_historical_artifact_is_preserved_and_numerically_equivalent():
    """baseline_v2.json is frozen evidence. It must still exist, still carry its
    wall-clock date, and still agree with the canonical artifact on every
    number -- that equivalence is what licenses citing the canonical one."""
    hist = json.load(open(_committed("baseline_v2.json")))
    can = json.load(open(_committed("baseline_v2_canonical.json")))
    assert "date" in hist, "historical artifact should retain its run date"
    assert "canonical" not in hist, "historical artifact must not be rewritten"

    h = {k: v for k, v in hist.items() if k != "date"}
    c = {k: v for k, v in can.items() if k != "canonical"}
    assert h == c, "canonical artifact changed a number relative to the record"
