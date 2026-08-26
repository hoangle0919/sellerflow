"""The deployment entrypoint stays a script, and the script stays honest.

Two branches independently fixed the same defect -- the training step's stderr
being sent to the null device, which made a failed deploy look exactly like a
successful one. That is how the live site came to serve the heuristic fallback
without anyone noticing.

They fixed it differently: one inline in `railway.toml`, one by moving the logic
into `backend/start_railway.sh`. The merge kept the script, because a script can
explain itself, can state the consequence of falling back, and can be tested --
which is what this file does. Nothing here re-litigates that choice; it pins it
so a future edit has to be deliberate.
"""
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAILWAY = os.path.join(REPO, "railway.toml")
SCRIPT = os.path.join(REPO, "backend", "start_railway.sh")


def _railway():
    return open(RAILWAY, encoding="utf-8").read()


def _railway_directives():
    """Only the active TOML lines. Comments explain history and are not config."""
    return "\n".join(l for l in _railway().splitlines()
                     if l.strip() and not l.lstrip().startswith("#"))


def test_start_command_is_the_script_and_nothing_else():
    m = re.search(r'^startCommand\s*=\s*"(.*)"$', _railway_directives(), re.M)
    assert m, "railway.toml has no startCommand"
    assert m.group(1) == "bash backend/start_railway.sh", (
        f"startCommand is {m.group(1)!r}; the deployment entrypoint is the "
        "script, so its diagnostics cannot be bypassed by editing one line of "
        "TOML"
    )


def test_no_inline_training_or_server_command_survives():
    """An inline command would run *instead of* the script's diagnostics."""
    directives = _railway_directives()
    for banned in ("train_model.py", "uvicorn", "2>/dev/null", "/dev/null"):
        assert banned not in directives, (
            f"railway.toml directive contains {banned!r}; training and startup "
            "belong in start_railway.sh where failure is logged and explained"
        )


def test_health_and_restart_configuration_is_preserved():
    """The merge kept the incoming operational settings; only the command moved."""
    d = _railway_directives()
    for expected in ('healthcheckPath = "/api/health"',
                     "healthcheckTimeout = 300",
                     'restartPolicyType = "ON_FAILURE"',
                     "restartPolicyMaxRetries = 3"):
        assert expected in d, f"railway.toml lost {expected!r} in the merge"


def _script_code():
    """Executable lines only.

    The script's header quotes the command it replaced, redirection and all, in
    order to explain what was wrong with it. A file has to be able to name the
    defect it fixes; banning the literal string outright would force the
    explanation out and leave a fix nobody can read.
    """
    return "\n".join(l for l in open(SCRIPT, encoding="utf-8").read().splitlines()
                     if l.strip() and not l.lstrip().startswith("#"))


def test_the_script_exists_and_never_discards_training_stderr():
    assert os.path.exists(SCRIPT), "railway.toml points at a script that is absent"
    code = _script_code()
    for banned in ("2>/dev/null", "2>&-", "2>/dev/nul"):
        assert banned not in code, (
            f"the script discards training stderr ({banned}) -- the defect it "
            "exists to fix"
        )
    assert "train_model.py" in code and "uvicorn" in code


def test_the_script_states_the_consequence_of_falling_back():
    """Announcing the fallback is not enough; it must say what changes.

    The discarded inline comment said the financing arithmetic never calls the
    ensemble, which implies a fallback is output-neutral. It is not: the active
    scorer sets the tier, and the tier sets the terms.
    """
    body = open(SCRIPT, encoding="utf-8").read().lower()
    assert "tier" in body, "the script must name the risk tier as what changes"
    for term in ("advance", "remittance", "cap factor"):
        assert term in body, f"the script must name {term} among the affected terms"
    assert "not" in body and "output-neutral" in body.replace("output neutral",
                                                             "output-neutral"), (
        "the script must say explicitly that the fallback is NOT output-neutral"
    )


def test_the_script_does_not_abort_the_deploy_on_a_training_failure():
    """Training is best-effort. That part of the incoming change was right."""
    body = open(SCRIPT, encoding="utf-8").read()
    assert not re.search(r"^\s*set\s+-e\b", body, re.M), (
        "`set -e` would turn a best-effort training failure into an outage"
    )
    assert "exec python -m uvicorn" in body or "exec " in body, (
        "the server must start regardless of the training outcome"
    )
