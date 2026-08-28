"""RETIRED. Historical convergence-step driver — no longer part of any recipe.

WHAT IT DID
    Ran one Monte Carlo convergence step at a given N and merged the result into
    `results/validation_v1.json`. The ladder was split across four invocations
    because 10,000 paths in a single process was timing out at the time.

WHY IT IS RETIRED
    `results/validation_v1.json` is now FROZEN. A-9 superseded it, and it is
    retained byte-for-byte as the record of what was published before the IRR
    definition was corrected. Its canonical form carries a registered SHA-256
    that appears in the manuscript, the deck, the results registry and the test
    suite.

    This script's last line was an unconditional `json.dump` into that file. Any
    invocation — including one that failed halfway through the ladder, or one
    run by someone following the old manifest recipe — would have rewritten a
    superseded artifact in place and silently invalidated every checksum quoted
    for it. Nothing in the script asked whether the file it was overwriting was
    still writable evidence.

WHAT TO RUN INSTEAD
    python3 run_validation.py 1

    Section 1 computes the same 500 / 2,000 / 5,000 / 10,000 ladder in one pass
    and writes it to `results/validation_v2.json`, the current raw file, which
    `canonicalize_validation.py` then registers. The split is no longer needed.

This module fails closed. It exits BEFORE importing the simulation package,
before reading anything, and before opening any file for writing, so there is no
path through it that can touch the frozen artifact.
"""
import os
import sys

_RETIRED = """
conv_step.py is RETIRED and will not run.

  Reason:  it wrote into research/results/validation_v1.json, which is now
           frozen historical evidence with a registered SHA-256. Running it
           would rewrite a superseded artifact in place.

  Instead: python3 run_validation.py 1

           Section 1 computes the full convergence ladder
           (500 / 2,000 / 5,000 / 10,000 paths) into
           research/results/validation_v2.json, the current raw file.

  See:     DECISION_LOG D-052, RESEARCH_MANIFEST.md
"""

# Guard first, at import time. Anything below this point would be a bug.
if os.environ.get("RBF_ALLOW_RETIRED_CONV_STEP") != "1":
    sys.stderr.write(_RETIRED)
    raise SystemExit(2)

# The escape hatch exists only so a future archaeologist can read the historical
# code path in context. It still refuses to write to the frozen file.
raise SystemExit(
    "conv_step.py: the historical write target is frozen. Even with "
    "RBF_ALLOW_RETIRED_CONV_STEP=1 this script does not write, because "
    "results/validation_v1.json is registered evidence. Run "
    "`python3 run_validation.py 1` for the current convergence ladder. Read the "
    "docstring, or `git show` an earlier revision for the original body."
)
