"""Regenerate every artifact in a clean copy and report byte and numeric equality SEPARATELY.

    python3 verify_reproduction.py            # regenerate in a temp tree, compare, report
    python3 verify_reproduction.py --keep     # keep the temp tree for inspection

WHY THE TWO ARE REPORTED SEPARATELY. Until D-041 this project claimed its
artifacts "reproduce byte-for-byte". That claim was made on Linux and is not
true everywhere: an independent regeneration on macOS / CPython 3.11.5 produced
9 last-bit floating-point differences in the baseline and 2 in the
cost-matched track (measured on the v2/v1 generation; the finding is about
the platform, not the artifact version). Byte equality is a statement about a *serialization* on
one platform; numeric equality at published precision is the statement a reader
actually needs. Collapsing them hid a real cross-platform limitation behind a
stronger-sounding word.

WHAT THIS SCRIPT WILL NOT DO. It never rewrites a registered artifact. Chasing
byte equality by regenerating the committed files on whichever machine happens
to be running would destroy the evidence and prove nothing — the artifact would
match because it was just overwritten, which is exactly the defect found in
`evidence/2026-08-07-native-macos-verification.md`, whose "recomputed" step only
re-hashed the committed JSON instead of regenerating it.

EXIT CODE. Non-zero if any artifact fails NUMERIC equality at the comparison
tolerance, or is missing. Byte differences are reported but do not fail the run;
they are a platform fact, not a research error. Read the table.
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

#: Each generator paired with the canonical artifact it is responsible for.
#:
#: ORDERING BUG FIXED (D-043). The first version deleted *every* canonical and
#: provenance file up front, then ran the generators. That broke
#: `canonicalize_validation.py`, whose `--write` path re-verifies the four
#: registered baseline checksums after writing and therefore requires them to
#: exist — so on any machine where a baseline did not regenerate byte-identically
#: (which is the case on macOS: 9 and 2 last-bit float differences), the run
#: aborted instead of reporting the difference it exists to report.
#:
#: Now each generator's own output is deleted immediately before that generator
#: runs, and recreation is confirmed. Nothing else is touched.
GENERATORS = (
    ("run_baseline.py", (), ("baseline_v3_canonical.json",
                             "baseline_v3_provenance.json")),
    ("run_equal_cost_baseline.py", (), ("baseline_equalcost_v2_canonical.json",
                                        "baseline_equalcost_v2_provenance.json")),
    ("run_closure_baseline.py", (), ("baseline_closure_v2_canonical.json",
                                     "baseline_closure_v2_provenance.json",
                                     "baseline_closure_equalcost_v2_canonical.json",
                                     "baseline_closure_equalcost_v2_provenance.json")),
    # `--no-registered-check`: inside this scratch tree the baselines were just
    # regenerated, so re-checking them against the registered checksums would
    # abort the run on exactly the platform whose difference we are trying to
    # measure. See the flag's rationale in `canonicalize_validation.py`.
    ("canonicalize_validation.py", ("--write", "--no-registered-check"),
     ("validation_v2_canonical.json", "validation_v2_provenance.json")),
)

ARTIFACTS = (
    "baseline_v3_canonical.json",
    "baseline_equalcost_v2_canonical.json",
    "baseline_closure_v2_canonical.json",
    "baseline_closure_equalcost_v2_canonical.json",
    "validation_v2_canonical.json",
)

#: Distinguishes "key absent" from "key present with value null". `None` cannot
#: do that job: `a.get(k)` returns `None` in both cases, so a dropped key and an
#: explicit null compared equal and a real structural difference was invisible.
MISSING = object()

#: Published precision. Nothing in the paper is quoted beyond ~6 significant
#: figures, so a relative difference below this is invisible to every consumer
#: of these files. Last-bit float noise is ~1e-16 relative.
REL_TOL = 1e-9
W = 96


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def leaves(obj, path="", out=None):
    out = {} if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            leaves(v, f"{path}/{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            leaves(v, f"{path}[{i}]", out)
    else:
        out[path] = obj
    return out


def compare(a_path, b_path):
    """Return (byte_equal, n_leaves, numeric_diffs, worst_rel)."""
    byte_equal = sha(a_path) == sha(b_path)
    with open(a_path, encoding="utf-8") as fh:
        a = leaves(json.load(fh))
    with open(b_path, encoding="utf-8") as fh:
        b = leaves(json.load(fh))
    diffs, worst = [], 0.0
    for k in sorted(set(a) | set(b)):
        # MISSING, not None — a dropped key and an explicit null are different
        # findings, and `.get(k)` collapses them into the same value.
        x, y = a.get(k, MISSING), b.get(k, MISSING)
        if x is MISSING or y is MISSING:
            diffs.append((k, "<ABSENT>" if x is MISSING else x,
                          "<ABSENT>" if y is MISSING else y, float("inf")))
            continue
        if x == y:
            continue
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) \
                and not isinstance(x, bool) and not isinstance(y, bool):
            denom = max(abs(x), abs(y), 1e-300)
            rel = abs(x - y) / denom
            worst = max(worst, rel)
            diffs.append((k, x, y, rel))
        else:
            diffs.append((k, x, y, float("inf")))
    return byte_equal, len(a), diffs, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="rbf_verify_")
    try:
        return _run(tmp, args)
    finally:
        # try/finally, so a generator crash cannot leave a scratch tree behind.
        if args.keep:
            print(f"\n  scratch tree kept at {os.path.join(tmp, 'research')}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


def _run(tmp, args):
    work = os.path.join(tmp, "research")
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", "*.pyc"))

    print("=" * W)
    print("  CLEAN-COPY REGENERATION — byte equality and numeric equality reported separately")
    print("=" * W)
    print(f"  platform : {platform.platform()}")
    print(f"  python   : {sys.version.split()[0]}")
    try:
        import numpy
        print(f"  numpy    : {numpy.__version__}")
    except Exception:
        pass
    print(f"  scratch  : {work}")
    print(f"  registered artifacts are READ-ONLY here and are never rewritten\n")

    results_dir = os.path.join(work, "results")
    for script, argv, outputs in GENERATORS:
        # Delete only THIS generator's outputs, immediately before running it.
        # Wiping everything up front broke `canonicalize_validation.py`, which
        # re-verifies the four baseline checksums on write.
        for out in outputs:
            p = os.path.join(results_dir, out)
            if os.path.exists(p):
                os.remove(p)

        r = subprocess.run([sys.executable, script, *argv], cwd=work,
                           capture_output=True, text=True)
        if r.returncode:
            print(f"  FAILED {script}")
            print((r.stderr or r.stdout)[-800:])
            return 2

        # Confirm recreation, rather than assuming a zero exit means it wrote.
        absent = [o for o in outputs
                  if not os.path.exists(os.path.join(results_dir, o))]
        if absent:
            print(f"  FAILED {script} — exited 0 but did not recreate: "
                  f"{', '.join(absent)}")
            return 2
        print(f"  ran {script}  →  recreated {len(outputs)} file(s)")

    print()
    print(f"  {'artifact':<46}{'bytes':<9}{'leaves':<9}{'numeric':<10}{'worst rel'}")
    print("  " + "-" * (W - 4))
    failures = byte_mismatch = 0
    detail = []
    for name in ARTIFACTS:
        ref, new = os.path.join(RESULTS, name), os.path.join(work, "results", name)
        if not os.path.exists(ref) or not os.path.exists(new):
            print(f"  {name:<46}{'MISSING':<9}")
            failures += 1
            continue
        be, n, diffs, worst = compare(ref, new)
        numeric_ok = all(d[3] <= REL_TOL for d in diffs)
        failures += (not numeric_ok)
        byte_mismatch += (not be)
        print(f"  {name:<46}{'EQUAL' if be else 'DIFFER':<9}{n:<9}"
              f"{'EQUAL' if numeric_ok else 'DIFFER':<10}{worst:.3e}")
        if diffs:
            detail.append((name, diffs))

    if detail:
        print("\n  differing leaves (first 10 per artifact):")
        for name, diffs in detail:
            print(f"    {name}  — {len(diffs)} leaf/leaves")
            for k, x, y, rel in diffs[:10]:
                print(f"      {k}\n        committed {x!r}\n        regenerated {y!r}  (rel {rel:.3e})")

    print("\n" + "=" * W)
    print(f"  byte-identical      : {len(ARTIFACTS) - byte_mismatch}/{len(ARTIFACTS)}")
    print(f"  numerically equal   : {len(ARTIFACTS) - failures}/{len(ARTIFACTS)}  (rel tol {REL_TOL:g})")
    if byte_mismatch and not failures:
        print("\n  Byte differences with zero numeric differences are a SERIALIZATION")
        print("  fact about this platform, not a research error. Do not 'fix' them by")
        print("  regenerating the committed artifacts — that would overwrite the")
        print("  evidence rather than verify it.")
    print("=" * W)
    # Cleanup happens in main()'s finally block, so a crash above cannot leak
    # the scratch tree.
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
