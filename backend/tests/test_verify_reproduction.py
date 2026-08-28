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
    # Five since D-051 split validation into battery + canonicalization.
    assert len(m.GENERATORS) == 5
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


# ── A-9 round 2 (D-050): stem pairing and provenance honesty ────────────────

def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_reproduction", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_canonical_and_provenance_stems_are_never_crossed():
    """The A-9 migration renamed canonicals and left provenance behind.

    `verify_reproduction.py` asked for `baseline_v3_canonical.json` beside
    `baseline_v2_provenance.json` — a file the current generators no longer
    write. The run would then report a missing output for a file it had asked
    for by the wrong name, which reads as a reproducibility failure and is not
    one. Every declared output must share the stem of its partner.
    """
    mod = _load_verifier()
    for script, _flags, outputs in mod.GENERATORS:
        canon = [o for o in outputs if o.endswith("_canonical.json")]
        prov = [o for o in outputs if o.endswith("_provenance.json")]
        assert len(canon) == len(prov), f"{script}: unpaired outputs {outputs}"
        canon_stems = sorted(o[: -len("_canonical.json")] for o in canon)
        prov_stems = sorted(o[: -len("_provenance.json")] for o in prov)
        assert canon_stems == prov_stems, (
            f"{script}: crossed stems — canonical {canon_stems} against "
            f"provenance {prov_stems}"
        )


def test_verifier_targets_only_current_artifact_stems():
    """Superseded artifacts are evidence, not regeneration targets."""
    mod = _load_verifier()
    superseded = ("baseline_v2_", "baseline_equalcost_v1_",
                  "baseline_closure_v1_", "baseline_closure_equalcost_v1_",
                  "validation_v1_")
    for _script, _flags, outputs in mod.GENERATORS:
        for o in outputs:
            assert not o.startswith(superseded), (
                f"verifier tries to regenerate the superseded artifact {o}; "
                "those are preserved byte-for-byte and must never be rewritten"
            )


def test_provenance_excludes_its_own_outputs_from_the_dirty_check():
    """A sidecar must not report dirtiness it caused itself.

    `build_provenance` used to sample `git status` after the canonical file had
    already been written, so every artifact recorded `source_tree_dirty: true`
    — which destroys the one question provenance answers: was this generated
    from committed source?
    """
    sys.path.insert(0, RESEARCH)
    from rbf_sim.canonical import source_state

    declared = ("baseline_v3_canonical.json", "baseline_v3_provenance.json")
    state = source_state(declared)
    assert set(state) >= {"source_commit", "source_tree_dirty"}
    for path in state.get("source_dirty_paths") or ():
        assert os.path.basename(path) not in declared, (
            "declared outputs must be excluded from the source-state check"
        )


# ── A-9 round 3 (D-051): validation must actually be regenerated ────────────

def test_validation_battery_is_run_before_canonicalization():
    """`canonicalize_validation.py` computes nothing; it re-expresses a file.

    The scratch tree is a copytree of the real one, so `validation_v2.json`
    arrived already written and the canonical step rebuilt its canonical form
    from a committed input. `run_validation.py` never executed, and a totally
    broken validation battery would have verified clean.
    """
    mod = _load_verifier()
    scripts = [g[0] for g in mod.GENERATORS]
    assert "run_validation.py" in scripts, (
        "the validation battery is never run; canonicalization alone proves "
        "only that the canonicalizer works"
    )
    assert scripts.index("run_validation.py") < scripts.index("canonicalize_validation.py")

    entry = next(g for g in mod.GENERATORS if g[0] == "run_validation.py")
    _script, argv, outputs = entry
    assert "validation_v2.json" in outputs, (
        "the raw file must be a declared output, or it is never deleted and the "
        "inherited copy is silently reused"
    )
    sections = [a[0] for a in argv]
    assert sections == ["1", "2", "4", "5", "6"], (
        f"the battery accumulates across five sections; got {sections}"
    )


def test_canonicalization_cannot_succeed_without_the_raw_battery_output():
    """The dependency that makes the ordering matter, proved rather than assumed.

    If `canonicalize_validation.py` could produce a canonical file without the
    raw one, deleting the raw file would not force `run_validation.py` to run
    and the fix above would be cosmetic.
    """
    tmp = tempfile.mkdtemp(prefix="rbf_canon_dep_")
    try:
        work = os.path.join(tmp, "research")
        shutil.copytree(RESEARCH, work,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        raw = os.path.join(work, "results", "validation_v2.json")
        assert os.path.exists(raw), "fixture expects the raw file to be present"
        os.remove(raw)

        r = subprocess.run(
            [sys.executable, "canonicalize_validation.py", "--write",
             "--no-registered-check"],
            cwd=work, capture_output=True, text=True)
        assert r.returncode != 0, (
            "canonicalize_validation.py succeeded without its raw input — it "
            "would mask a broken run_validation.py"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_a_broken_validation_battery_fails_reproduction():
    """End-to-end on the validation leg only: break the battery, expect failure.

    Running the whole verifier here would take minutes, so this exercises the
    same two steps the verifier now runs, in the same order, against a
    deliberately broken `run_validation.py`.
    """
    tmp = tempfile.mkdtemp(prefix="rbf_broken_batt_")
    try:
        work = os.path.join(tmp, "research")
        shutil.copytree(RESEARCH, work,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        os.remove(os.path.join(work, "results", "validation_v2.json"))

        # Break it BEFORE it does any work. An earlier version of this test
        # appended the failure, which runs after `if __name__ == "__main__"`
        # has already executed the section and written its output -- so the
        # battery "failed" while still producing a file, and canonicalization
        # then succeeded. The injection has to precede the work it invalidates.
        script = os.path.join(work, "run_validation.py")
        src = open(script, encoding="utf-8").read()
        with open(script, "w", encoding="utf-8") as fh:
            fh.write("raise SystemExit(3)  # injected by test\n" + src)

        failed = False
        for section in ("1", "2", "4", "5", "6"):
            r = subprocess.run([sys.executable, "run_validation.py", section],
                               cwd=work, capture_output=True, text=True)
            if r.returncode:
                failed = True
                break
        assert failed, "a broken battery ran to completion"

        # And the canonical step cannot cover for it.
        r = subprocess.run(
            [sys.executable, "canonicalize_validation.py", "--write",
             "--no-registered-check"],
            cwd=work, capture_output=True, text=True)
        assert r.returncode != 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
