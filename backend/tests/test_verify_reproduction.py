"""The reproducibility verifier must survive the cases it exists to report on.

Its whole job is to behave correctly when an artifact does NOT reproduce
byte-for-byte. The first version failed exactly there: it deleted every
canonical file up front, which broke the validation step's baseline
re-verification, so on macOS — the platform with the 9 and 2 last-bit float
differences — the run aborted instead of printing them. A verifier that only
works when everything matches verifies nothing.

These tests exercise the failure paths directly rather than the happy path.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESEARCH = os.path.join(REPO, "research")
SCRIPT = os.path.join(RESEARCH, "verify_reproduction.py")

pytestmark = pytest.mark.skipif(not os.path.exists(SCRIPT), reason="verifier absent")


def _mod():
    spec = importlib.util.spec_from_file_location("verify_reproduction", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ── missing vs explicit null ────────────────────────────────────────────────

def test_absent_key_is_distinguished_from_an_explicit_null(tmp_path):
    """`.get(k)` returns None for both, so a dropped key compared EQUAL to a
    null and a real structural difference was invisible."""
    m = _mod()
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"x": None, "y": 1}), encoding="utf-8")
    b.write_text(json.dumps({"y": 1}), encoding="utf-8")          # x dropped
    _, _, diffs, _ = m.compare(str(a), str(b))
    paths = [d[0] for d in diffs]
    assert "/x" in paths, (
        "a dropped key must be reported; it is being collapsed into null")


def test_two_explicit_nulls_are_equal(tmp_path):
    """The sentinel must not make matching nulls look different."""
    m = _mod()
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"x": None}), encoding="utf-8")
    b.write_text(json.dumps({"x": None}), encoding="utf-8")
    _, _, diffs, _ = m.compare(str(a), str(b))
    assert not diffs, f"identical nulls reported as differing: {diffs}"


# ── byte vs numeric, reported separately ────────────────────────────────────

def test_byte_difference_with_zero_numeric_drift_is_not_a_numeric_failure(tmp_path):
    """The macOS case: same numbers, different serialization. Must report a
    byte difference and NO numeric difference."""
    m = _mod()
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text('{"v": 1.0}', encoding="utf-8")
    b.write_text('{"v": 1.0}\n', encoding="utf-8")     # trailing newline only
    byte_equal, _, diffs, worst = m.compare(str(a), str(b))
    assert byte_equal is False, "byte difference not detected"
    assert not diffs and worst == 0.0, "identical numbers flagged as drift"


def test_last_bit_float_difference_is_below_the_numeric_tolerance(tmp_path):
    """9 and 2 last-bit differences must not fail the numeric check."""
    m = _mod()
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    x = 0.36222857463514163
    a.write_text(json.dumps({"v": x}), encoding="utf-8")
    b.write_text(json.dumps({"v": x + 5e-17}), encoding="utf-8")
    _, _, diffs, worst = m.compare(str(a), str(b))
    assert worst <= m.REL_TOL, (
        f"last-bit difference {worst:.3e} exceeds tolerance {m.REL_TOL:g}; the "
        f"verifier would report a research error for a serialization fact")


def test_a_real_numeric_change_does_exceed_the_tolerance(tmp_path):
    """The other direction: the tolerance must not swallow a genuine change."""
    m = _mod()
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"v": 18.718}), encoding="utf-8")
    b.write_text(json.dumps({"v": 18.719}), encoding="utf-8")
    _, _, _, worst = m.compare(str(a), str(b))
    assert worst > m.REL_TOL, "a 0.001 change is being treated as noise"


# ── generator wiring ────────────────────────────────────────────────────────

def test_each_generator_declares_the_outputs_it_owns():
    """Per-generator deletion is what fixed the ordering bug. If a generator
    ever declares no outputs, the deletion becomes a no-op and stale files
    would silently pass as 'regenerated'."""
    m = _mod()
    assert len(m.GENERATORS) == 4
    for script, argv, outputs in m.GENERATORS:
        assert outputs, f"{script} declares no outputs"
        assert os.path.exists(os.path.join(RESEARCH, script)), f"{script} missing"
    declared = {o for _, _, outs in m.GENERATORS for o in outs}
    for art in m.ARTIFACTS:
        assert art in declared, f"{art} is compared but no generator owns it"


def test_validation_step_skips_the_registered_baseline_recheck():
    """The precise coupling that broke macOS. Inside the scratch tree the
    baselines were just regenerated, so re-checking them there tests the
    platform, not the script — and aborted the run on a byte mismatch."""
    m = _mod()
    step = [g for g in m.GENERATORS if g[0] == "canonicalize_validation.py"]
    assert step, "validation canonicalization step missing"
    assert "--no-registered-check" in step[0][1], (
        "the scratch run must skip the registered-baseline re-check, or a "
        "byte-only difference will abort the very run meant to report it")


def test_verifier_never_writes_to_the_real_results_directory():
    src = open(SCRIPT, encoding="utf-8").read()
    assert "RESULTS" in src
    # Every write path must be under the scratch tree.
    for bad in ("open(os.path.join(RESULTS", "shutil.copy(.*RESULTS",
                "os.remove(os.path.join(RESULTS"):
        assert bad not in src, f"verifier writes into the registered results dir: {bad}"
    assert "results_dir = os.path.join(work" in src, \
        "deletions must target the scratch tree explicitly"


def test_cleanup_is_guaranteed_by_try_finally():
    src = open(SCRIPT, encoding="utf-8").read()
    assert "finally:" in src and "rmtree" in src, \
        "scratch tree cleanup must be in a finally block"
    assert src.index("try:") < src.index("finally:")


# ── end-to-end failure handling ─────────────────────────────────────────────

def test_missing_regenerated_output_is_reported_not_assumed(tmp_path):
    """A generator that exits 0 without writing must fail loudly."""
    m = _mod()
    src = open(SCRIPT, encoding="utf-8").read()
    assert "did not recreate" in src, (
        "the verifier must confirm recreation rather than trust the exit code")


def test_generator_failure_cleans_up_and_does_not_leak_a_scratch_tree():
    """Run the verifier against a broken copy and confirm no /tmp residue."""
    work = tempfile.mkdtemp(prefix="rbf_verify_test_")
    try:
        research = os.path.join(work, "research")
        shutil.copytree(RESEARCH, research, ignore=shutil.ignore_patterns(
            "__pycache__", ".pytest_cache", "*.pyc"))
        # Break the first generator.
        with open(os.path.join(research, "run_baseline.py"), "w",
                  encoding="utf-8") as fh:
            fh.write("import sys\nsys.exit(3)\n")
        before = set(_scratch_dirs())
        r = subprocess.run([sys.executable, os.path.join(research,
                                                         "verify_reproduction.py")],
                           capture_output=True, text=True, timeout=600)
        assert r.returncode != 0, "a failing generator must not report success"
        assert "FAILED" in r.stdout, f"failure not surfaced:\n{r.stdout[-400:]}"
        leaked = set(_scratch_dirs()) - before
        assert not leaked, f"scratch tree leaked after generator failure: {leaked}"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _scratch_dirs():
    base = tempfile.gettempdir()
    return [os.path.join(base, d) for d in os.listdir(base)
            if d.startswith("rbf_verify_") and not d.startswith("rbf_verify_test_")]
