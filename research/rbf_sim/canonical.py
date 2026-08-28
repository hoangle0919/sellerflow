"""Canonical artifact serialization — deterministic, checksummable output.

THE PROBLEM THIS SOLVES (found historically in the superseded `results/baseline_v2.json`, which embedded `date.today()`).
Every quantity in it was reproducible bit-for-bit, but the file was not: two
runs of identical code, configuration and seeds produced two different
checksums. A result you cannot checksum cannot be cited by checksum, and
"reproducible" then rests on someone diffing 1,553 lines by hand.

THE SPLIT. Two files, and the distinction is the whole point:

  CANONICAL   (`*_canonical.json`) — the analytical result. Contains ONLY
      quantities and metadata that are a deterministic function of the code,
      the configuration and the seeds. Identical inputs reproduce it
      NUMERICALLY at published precision on every platform tested, and
      byte-identically within a fixed runtime. ~~MUST produce a
      byte-identical file~~ was withdrawn by D-041: byte equality is a
      property of a serialization on one platform, not of the result. This
      is the artifact to cite, checksum, and diff.

  PROVENANCE  (`*_provenance.json`) — the execution record. Wall-clock time,
      git commit, interpreter and library versions, platform, and the checksum
      of the canonical file produced. Expected to differ between runs; that is
      its job. It answers "who ran this, when, on what" without contaminating
      the result.

WHY `source_commit` LIVES IN PROVENANCE, NOT CANONICAL. Embedding the git
commit in the canonical file is self-defeating: committing the file changes
HEAD, which changes what the next run would emit, so the artifact can never be
both committed and reproducible. Code identity is still captured — by
`generator_fingerprint`, a hash of the generating source itself. That is
strictly stronger for this purpose: it is stable across commits that do not
touch the generator, and it changes exactly when the generator changes, which
is the property actually wanted. The git commit is recorded in provenance,
where it belongs.

DETERMINISM OF THE ENCODING. `sort_keys=True` removes dict-ordering
dependence. `ensure_ascii=True` removes locale and encoding variation. Floats
use Python's shortest round-trip `repr`, which is stable across CPython 3.1+
on IEEE-754 platforms. Cross-major-version stability is asserted by test on the
running interpreter, not assumed.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

#: Bump when the canonical SHAPE changes (not when numbers change).
#: Bumped to 2.0 by A-9: aggregates gained apr_defined_count,
#: apr_defined_rate, completed_count and completed_rate, and the APR
#: values themselves are computed under a corrected definition. A 1.0
#: artifact and a 2.0 artifact are not comparable field-for-field on the
#: rate layer, so the version has to move with the shape.
CANONICAL_SCHEMA_VERSION = "2.0"

#: Source files whose content defines the generated numbers.
_GENERATOR_SOURCES = (
    "rbf_sim/__init__.py",
    "rbf_sim/contracts.py",
    "rbf_sim/engine.py",
    "rbf_sim/generator.py",
    "rbf_sim/metrics.py",
    "rbf_sim/settlement.py",
)

#: Keys stripped from a payload before canonicalization: execution facts, not
#: results. Anything added here must be preserved in the provenance record.
NON_DETERMINISTIC_KEYS = ("date", "run_date", "timestamp", "generated_at", "hostname")


def _research_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generator_fingerprint(extra_sources: Iterable[str] = ()) -> str:
    """SHA-256 over the generating source, in fixed filename order.

    Changes exactly when the code that produces the numbers changes. Missing
    files are recorded as such rather than skipped, so deleting a module is a
    visible fingerprint change rather than a silent one.
    """
    root = _research_root()
    h = hashlib.sha256()
    for rel in sorted(set(_GENERATOR_SOURCES) | set(extra_sources)):
        path = os.path.join(root, rel)
        h.update(rel.encode())
        if os.path.exists(path):
            with open(path, "rb") as fh:
                h.update(fh.read())
        else:
            h.update(b"<ABSENT>")
    return h.hexdigest()


def config_hash(config: Any) -> str:
    """SHA-256 of a configuration object under the canonical encoding."""
    return hashlib.sha256(canonical_bytes(config)).hexdigest()


def _stringify_keys(obj: Any) -> Any:
    """Coerce every mapping key to `str` before encoding.

    Without this the encoding is stable across runs but NOT idempotent under
    round-trip. JSON object keys are always strings, so a dict written with
    integer keys {6: .., 12: ..} sorts numerically on the way out (6, 12) and
    lexicographically on the way back in ("12", "6"). A consumer who loads the
    artifact, re-encodes it and checksums the result would then get a different
    hash than the file's own -- which defeats the point of a checksummable
    artifact. Normalising keys first makes the encoding a fixed point:

        canonical_bytes(json.loads(canonical_bytes(x))) == canonical_bytes(x)
    """
    if isinstance(obj, dict):
        return {str(k): _stringify_keys(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_stringify_keys(v) for v in obj]
    return obj


def canonical_bytes(obj: Any) -> bytes:
    """The one encoding. Every checksum in this project is taken over this."""
    return (json.dumps(_stringify_keys(obj), sort_keys=True, indent=2,
                       ensure_ascii=True, separators=(",", ": "),
                       default=str) + "\n").encode("utf-8")


def checksum(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def build_canonical(payload: Dict[str, Any], *, scenario_config: Any,
                    spec_version: str, extra_sources: Iterable[str] = (),
                    ) -> Dict[str, Any]:
    """Strip execution facts, attach deterministic identity metadata."""
    body = {k: v for k, v in payload.items() if k not in NON_DETERMINISTIC_KEYS}
    body["canonical"] = {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "spec_version": spec_version,
        "generator_fingerprint": generator_fingerprint(extra_sources),
        "scenario_config_hash": config_hash(scenario_config),
        # Corrected while new artifacts were being generated (D-041, D-049).
        # The previous unqualified byte-identity claim was measured by a step
        # that re-hashed the committed file rather than regenerating it, and is
        # false across platforms: macOS CPython 3.11.5 differs from Linux in a
        # handful of last-bit float values.
        "determinism": "Identical code, configuration and seeds reproduce this "
                       "file NUMERICALLY at published precision on every "
                       "platform tested. BYTE equality holds within a fixed "
                       "runtime and is NOT claimed across platforms. "
                       "Wall-clock time, git commit and environment are "
                       "recorded in the provenance sidecar.",
    }
    return body


def _git(*args: str) -> Optional[str]:
    try:
        out = subprocess.run(("git",) + args, cwd=_research_root(),
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def _git_status_porcelain():
    """(succeeded, output). Empty output on success means a clean tree."""
    try:
        out = subprocess.run(("git", "status", "--porcelain"),
                             cwd=_research_root(), capture_output=True,
                             text=True, timeout=10)
        return (out.returncode == 0, out.stdout)
    except Exception:
        return (False, "")


def source_state(declared_outputs: Iterable[str] = ()) -> Dict[str, Any]:
    """Describe the SOURCE state, excluding the outputs this run will create.

    This has to be sampled before anything is written, and it has to ignore the
    files the run declares it is about to produce. The previous version called
    `git status --porcelain` from inside `build_provenance`, which runs *after*
    the canonical file has already been written -- so every sidecar recorded
    `source_tree_dirty: true`, caused by its own output. A provenance record
    that reports dirtiness it created itself cannot distinguish "generated from
    committed source" from "generated from uncommitted edits", which is the one
    question it exists to answer.

    Two exclusions, for two different reasons.

    `declared_outputs` are the specific files this run creates, excluded by
    name. And `results/` as a whole is excluded because it holds OUTPUTS, not
    source: a full regeneration runs the generators in sequence, so each one
    would otherwise see the artifacts written by the ones before it and report
    a dirty source tree caused entirely by its own siblings. "Was this
    generated from committed source?" is a question about source.

    Anything modified outside `results/` is real source dirtiness and is
    reported, with the offending paths named so the answer is checkable rather
    than a bare boolean.
    """
    # `_git` returns None both when the command fails AND when it succeeds with
    # empty output -- and `git status --porcelain` prints nothing precisely when
    # the tree is clean. Using it here made the cleanest possible result
    # indistinguishable from a git failure, and the first artifact of a
    # regeneration (the only one run against a genuinely clean tree) recorded
    # `source_tree_dirty: null`. Ask for the exit status explicitly.
    ok, porcelain = _git_status_porcelain()
    if not ok:
        return {"source_commit": _git("rev-parse", "HEAD"),
                "source_tree_dirty": None, "source_dirty_paths": None,
                "source_state_scope": "git unavailable; state not determined"}

    declared = {os.path.basename(p) for p in declared_outputs}
    residual = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        # Porcelain v1 is "XY PATH", but the status field width is not worth
        # trusting -- an earlier version sliced a fixed [3:] and cut the first
        # character off every path, so the exclusion never matched. Split on
        # whitespace instead and take the last field (renames read "old -> new";
        # the destination is what exists on disk).
        path = line.split()[-1].strip('"')
        if os.path.basename(path) in declared:
            continue
        if f"{os.sep}results{os.sep}" in f"{os.sep}{path}" or path.startswith("results/"):
            continue
        residual.append(path)
    return {
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree_dirty": bool(residual),
        "source_dirty_paths": sorted(residual)[:20] or None,
        "source_state_scope": ("Tracked source outside research/results/. "
                               "Generated artifacts are outputs, not source, "
                               "and are excluded."),
    }


def build_provenance(canonical: Dict[str, Any], *, artifact: str,
                     source: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The execution record. Everything here is expected to vary between runs.

    `source` must be sampled by the caller *before* writing any output; see
    `source_state`. It is computed here only as a fallback for direct callers,
    and that path cannot exclude outputs it does not know about.
    """
    src = source if source is not None else source_state()
    return {
        "artifact": artifact,
        "canonical_sha256": checksum(canonical),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **src,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": _numpy_version(),
        "note": "Execution record only. No number here participates in the "
                "analytical result; the canonical artifact is what to cite.",
    }


def _numpy_version() -> Optional[str]:
    try:
        import numpy
        return numpy.__version__
    except Exception:
        return None


def write_canonical_pair(payload: Dict[str, Any], *, stem: str,
                         scenario_config: Any, spec_version: str,
                         results_dir: Optional[str] = None,
                         extra_sources: Iterable[str] = ()) -> Dict[str, str]:
    """Write `<stem>_canonical.json` and `<stem>_provenance.json`.

    Returns the paths written and the canonical checksum.
    """
    results_dir = results_dir or os.path.join(_research_root(), "results")
    os.makedirs(results_dir, exist_ok=True)

    # Sample the source state FIRST, and tell it which files this run is about
    # to create. Doing it after the write made every sidecar report dirtiness
    # it had caused itself.
    src = source_state((f"{stem}_canonical.json", f"{stem}_provenance.json"))

    canonical = build_canonical(payload, scenario_config=scenario_config,
                                spec_version=spec_version,
                                extra_sources=extra_sources)
    c_path = os.path.join(results_dir, f"{stem}_canonical.json")
    with open(c_path, "wb") as fh:
        fh.write(canonical_bytes(canonical))

    prov = build_provenance(canonical, artifact=f"{stem}_canonical.json",
                            source=src)
    p_path = os.path.join(results_dir, f"{stem}_provenance.json")
    with open(p_path, "wb") as fh:
        fh.write(canonical_bytes(prov))

    return {"canonical": c_path, "provenance": p_path,
            "sha256": prov["canonical_sha256"]}
