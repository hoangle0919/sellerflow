"""Canonicalize the validation battery — additively, with zero numeric change.

    python3 canonicalize_validation.py          # verify only, writes nothing
    python3 canonicalize_validation.py --write  # write the canonical/provenance pair

WHY THIS EXISTS. `validation_v1.json` is the only registered result file with no
checksummed canonical form. It is also the source of the two numbers most likely
to be quoted in a write-up: the reference-path cost-matched cap `f* = 1.0945`
and Benchmark B's 19.5618% APR. Quoting a figure that cannot be checked against
a hash is the gap this project closed everywhere else, and leaving it open here
would mean the most quotable numbers are the least verifiable ones.

WHY IT IS A SEPARATE SCRIPT, NOT AN EDIT TO `run_validation.py`. That file's
bytes are part of what produced the artifact. Rewriting it to emit a canonical
pair would change the generating source without changing the numbers, which is
precisely the confusion the fingerprint exists to prevent. This script reads the
committed artifact and re-expresses it; it never recomputes a result.

THE ONLY NON-DETERMINISM, MEASURED NOT ASSUMED. Re-running every section from a
clean tree (`conv_step.py` at N = 500/2000/5000/10000, then `run_validation.py`
sections 2, 4, 5, 6) reproduces the committed file with exactly one difference:

    /_meta/date: '2026-08-04' vs '2026-08-10'

Zero numeric differences. Both `run_scenario` (base_seed 20260803) and
`bootstrap_ci` (seed 90210) carry deterministic defaults, so the battery was
already reproducible — it simply had no artifact to prove it with. `_meta.date`
is a *when-it-ran* fact, so it belongs in provenance; the rest of `_meta` is
configuration and stays in the canonical body.

Note that `NON_DETERMINISTIC_KEYS` strips top-level keys only, and this date is
nested one level down. Rather than widen that constant — which would alter the
behaviour of the writer that produced four already-registered baselines — the
split is done explicitly here, and `--write` re-verifies all four baseline
checksums afterwards.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbf_sim.canonical import (canonical_bytes, generator_fingerprint,
                               write_canonical_pair)

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
SOURCE = os.path.join(RESULTS, "validation_v2.json")
STEM = "validation_v2"

#: Sources that produced the battery. Both, because the convergence ladder comes
#: from `conv_step.py` and the remaining sections from `run_validation.py`.
EXTRA_SOURCES = ("run_validation.py", "conv_step.py")

#: Execution facts inside `_meta`. Everything else there is configuration.
META_PROVENANCE_KEYS = ("date",)

#: The CURRENT registered baselines (A-9 generation). Re-checked after any
#: write, because this script imports the same writer they were produced by.
#: The superseded v1/v2 generation is checked separately in
#: backend/tests/test_validation_artifact.py -- those files are preserved as
#: historical evidence and must never move, but they are not what this script
#: can now reproduce.
REGISTERED = {
    "baseline_v3_canonical.json":
        "818c145ad557ea1f95311fe80d311252103464ba7a7ecac602aab67374ae8308",
    "baseline_equalcost_v2_canonical.json":
        "9cc6885a3d0d2d54fb08ae85301ae5889e7059f2780cdcfca693b3a8ec47802d",
    "baseline_closure_v2_canonical.json":
        "c032625a8e7c17c55a590eac673e447f178fdb192812fe98ee6df0b6e228fd75",
    "baseline_closure_equalcost_v2_canonical.json":
        "de7de916cfa73b7ff1c3b153f068ecdae90670ad4e0283e27c9ce36bb544458a",
}

#: Superseded by A-9, preserved byte-for-byte. Kept here only so the names are
#: discoverable from the canonicalizer; their integrity is asserted by test.
SUPERSEDED = {
    "baseline_v2_canonical.json":
        "264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849",
    "baseline_equalcost_v1_canonical.json":
        "6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7",
    "baseline_closure_v1_canonical.json":
        "0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470",
    "baseline_closure_equalcost_v1_canonical.json":
        "49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9",
}

W = 78


def split_payload(raw):
    """Return (canonical_payload, execution_facts) with no number touched."""
    body = {k: v for k, v in raw.items() if k != "_meta"}
    meta = dict(raw.get("_meta") or {})
    facts = {k: meta.pop(k) for k in META_PROVENANCE_KEYS if k in meta}
    payload = {
        "run": STEM,
        "spec": meta.get("spec", "METHODOLOGY_SPEC.md v1.0 + amendments A-1..A-3"),
        "provenance": meta.get("provenance", "SIMULATED — no observed seller data"),
        "purpose": "Validation battery: Monte Carlo convergence, pricing "
                   "sensitivity and the reference-path cost-matched cap f*, "
                   "incomplete-recovery boundary search, RBF-G guardrail "
                   "breakpoint, and revenue-definition sensitivity.",
        "config": {k: v for k, v in meta.items()
                   if k not in ("spec", "provenance")},
        **body,
    }
    return payload, facts


def numbers_of(obj, path="", out=None):
    """Flatten every scalar to (path, value) so a diff cannot hide one."""
    out = {} if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            numbers_of(v, f"{path}/{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            numbers_of(v, f"{path}[{i}]", out)
    else:
        out[path] = obj
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write the canonical/provenance pair (default: verify only)")
    ap.add_argument("--no-registered-check", action="store_true",
                    help="skip the post-write baseline checksum re-verification. "
                         "Only meaningful inside a scratch tree, where the "
                         "baselines were themselves just regenerated.")
    args = ap.parse_args()

    if not os.path.exists(SOURCE):
        print(f"  ERROR: {SOURCE} not found")
        return 1

    raw = json.load(open(SOURCE, encoding="utf-8"))
    payload, facts = split_payload(raw)

    print("=" * W)
    print("  CANONICALIZE validation_v2 — additive, zero numeric change")
    print("=" * W)
    print(f"  source            : results/validation_v2.json (left untouched)")
    print(f"  moved to provenance: {facts or 'nothing'}")

    # The load-bearing check: every scalar in the source must survive, by path
    # and by value. Section keys are re-parented under the payload, so compare
    # on the shared subtree rather than on the whole document.
    src_nums = numbers_of({k: v for k, v in raw.items() if k != "_meta"})
    out_nums = numbers_of({k: v for k, v in payload.items()
                           if k in raw and k != "_meta"})
    missing = {k: v for k, v in src_nums.items() if out_nums.get(k, object()) != v}
    print(f"  scalars in source : {len(src_nums)}")
    print(f"  scalars preserved : {len(src_nums) - len(missing)}")
    if missing:
        print("  *** NUMERIC DRIFT — refusing to write ***")
        for k, v in list(missing.items())[:10]:
            print(f"     {k}: {v!r} -> {out_nums.get(k)!r}")
        return 1
    print("  numeric drift     : NONE ✓")

    fp = generator_fingerprint(EXTRA_SOURCES)
    print(f"  generator fp      : {fp[:16]}…")

    if not args.write:
        import hashlib
        from rbf_sim.canonical import build_canonical
        c = build_canonical(payload, scenario_config=payload.get("config"),
                            spec_version=payload["spec"],
                            extra_sources=EXTRA_SOURCES)
        print(f"  would write sha256: {hashlib.sha256(canonical_bytes(c)).hexdigest()}")
        print("\n  (verify only — pass --write to emit the pair)")
        return 0

    written = write_canonical_pair(
        payload, stem=STEM,
        scenario_config=payload.get("config"),
        spec_version=payload["spec"],
        extra_sources=EXTRA_SOURCES,
    )

    # `build_provenance` composes its own record and takes no extra fields, so
    # without this the date would be DROPPED, not moved — and the line printed
    # above would be a false statement about what this script did. Rather than
    # widen `canonical.py` (four registered baselines depend on that writer),
    # extend the emitted record here and re-encode it canonically.
    if facts:
        with open(written["provenance"], encoding="utf-8") as fh:
            prov = json.load(fh)
        prov["original_run_date"] = facts["date"]
        prov["original_source"] = "validation_v2.json"
        prov["note"] = (prov.get("note", "") + " `original_run_date` is the "
                        "date stamped by the battery when it first ran; it was "
                        "the only non-deterministic field in the source.")
        with open(written["provenance"], "wb") as fh:
            fh.write(canonical_bytes(prov))

    print(f"\n  written: results/{STEM}_canonical.json")
    print(f"           results/{STEM}_provenance.json")
    print(f"  SHA-256: {written['sha256']}")

    if args.no_registered_check:
        # WHY THIS FLAG EXISTS (D-043). This check asks "did writing the
        # validation pair disturb the registered baselines?" — a real question
        # against the repository. Inside `verify_reproduction.py`'s scratch
        # tree the baselines were themselves just regenerated seconds earlier,
        # so the check is not only meaningless there, it is actively harmful:
        # on a platform where a baseline reproduces numerically but not
        # byte-for-byte (macOS CPython 3.11.5: 9 and 2 last-bit float
        # differences), it aborted the very run whose purpose was to MEASURE
        # and report that difference.
        print("\n  registered-baseline re-check SKIPPED (--no-registered-check):")
        print("    running inside a scratch tree; the baselines here were just")
        print("    regenerated, so comparing them to the registered checksums")
        print("    would test the platform, not this script.")
        print("=" * W)
        return 0

    print("\n  re-verifying the four registered baselines:")
    import hashlib
    bad = 0
    for name, expected in sorted(REGISTERED.items()):
        p = os.path.join(RESULTS, name)
        got = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "ABSENT"
        ok = got == expected
        bad += (not ok)
        print(f"    {'✓' if ok else '✗'} {name:46} {got[:16]}…")
    print("=" * W)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
