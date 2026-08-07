"""Canonical artifact serialization — deterministic, checksummable output.

THE PROBLEM THIS SOLVES. `results/baseline_v2.json` embedded `date.today()`.
Every quantity in it was reproducible bit-for-bit, but the file was not: two
runs of identical code, configuration and seeds produced two different
checksums. A result you cannot checksum cannot be cited by checksum, and
"reproducible" then rests on someone diffing 1,553 lines by hand.

THE SPLIT. Two files, and the distinction is the whole point:

  CANONICAL   (`*_canonical.json`) — the analytical result. Contains ONLY
      quantities and metadata that are a deterministic function of the code,
      the configuration and the seeds. Identical inputs MUST produce a
      byte-identical file. This is the artifact to cite, checksum, and diff.

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
CANONICAL_SCHEMA_VERSION = "1.0"

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
        "determinism": "Identical code, configuration and seeds produce a "
                       "byte-identical file. Wall-clock time, git commit and "
                       "environment are recorded in the provenance sidecar.",
    }
    return body


def _git(*args: str) -> Optional[str]:
    try:
        out = subprocess.run(("git",) + args, cwd=_research_root(),
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def build_provenance(canonical: Dict[str, Any], *, artifact: str) -> Dict[str, Any]:
    """The execution record. Everything here is expected to vary between runs."""
    dirty = _git("status", "--porcelain")
    return {
        "artifact": artifact,
        "canonical_sha256": checksum(canonical),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree_dirty": bool(dirty) if dirty is not None else None,
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

    canonical = build_canonical(payload, scenario_config=scenario_config,
                                spec_version=spec_version,
                                extra_sources=extra_sources)
    c_path = os.path.join(results_dir, f"{stem}_canonical.json")
    with open(c_path, "wb") as fh:
        fh.write(canonical_bytes(canonical))

    prov = build_provenance(canonical, artifact=f"{stem}_canonical.json")
    p_path = os.path.join(results_dir, f"{stem}_provenance.json")
    with open(p_path, "wb") as fh:
        fh.write(canonical_bytes(prov))

    return {"canonical": c_path, "provenance": p_path,
            "sha256": prov["canonical_sha256"]}
