"""Source-level guard: the withdrawn 0.92 benchmark must not reappear.

The API-response guard in `test_api.py` checks what the running service emits.
This checks the shipped source itself, because a withdrawn claim can leak back
through a print statement, a UI string, or a template that no endpoint returns.

Every occurrence in a public surface must be on the allowlist below with a
stated reason. Adding a new one is a deliberate act that requires editing this
file, which is the point -- P0-2 was originally missed precisely because the
figure lived in three places and nobody enumerated them.
"""
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Files a user, reviewer, or API consumer can actually reach.
PUBLIC_SURFACES = [
    "backend/main.py",
    "backend/demo_learning_loop.py",
    "backend/financing_engine.py",
    "backend/integrity_engine.py",
    "backend/ml_engine.py",
    "backend/train_model.py",
    "backend/validate_on_real_data.py",
    "frontend/index.html",
]

# (file, matched text fragment) -> why this occurrence is legitimate.
ALLOWED = {
    ("backend/main.py", '"withdrawn_value": 0.92'):
        "Explicitly labelled as the retracted figure inside the withdrawal "
        "notice. Naming what was withdrawn is the opposite of promoting it.",
}

# 0.92 as a bare number, or with more precision, in any shipped surface.
PATTERN = re.compile(r"0\.92\d*")


def _public_files():
    for rel in PUBLIC_SURFACES:
        path = os.path.join(REPO, rel)
        if os.path.exists(path):
            yield rel, path


def test_every_public_occurrence_of_the_withdrawn_figure_is_justified():
    unexplained = []
    for rel, path in _public_files():
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in PATTERN.finditer(line):
                    frag = line.strip()
                    if any(rel == a_rel and a_frag in frag
                           for (a_rel, a_frag) in ALLOWED):
                        continue
                    unexplained.append(f"{rel}:{lineno}: {frag[:110]}")
    assert unexplained == [], (
        "Unjustified appearance of the withdrawn 0.92 benchmark in a public "
        "surface. Either remove it, or add it to ALLOWED with a reason:\n  "
        + "\n  ".join(unexplained))


def test_no_public_surface_calls_the_synthetic_baseline_a_current_result():
    """Phrasings that present the withdrawn benchmark as a live figure."""
    banned = [
        "synthetic train auc:    0.92",
        "a synthetic baseline today",
        '"auc": 0.92',
    ]
    hits = []
    for rel, path in _public_files():
        text = open(path, encoding="utf-8").read().lower()
        for phrase in banned:
            if phrase in text:
                hits.append(f"{rel}: {phrase!r}")
    assert hits == [], f"withdrawn framing still present: {hits}"


def test_audit_trail_retains_the_withdrawal_evidence():
    """The withdrawal must stay explainable. 0.9098 vs 0.9182 is the evidence
    that the benchmark was circular; deleting it would remove the reason."""
    eip = os.path.join(REPO, "research/analysis/00_audit_evidence.py")
    assert os.path.exists(eip), "audit evidence script missing"
    src = open(eip, encoding="utf-8").read()
    assert "0.9182" in src, "reported ensemble AUC missing from audit trail"

    readme = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    assert "0.9098" in readme and "0.9182" in readme, \
        "README must retain the circularity arithmetic that justifies withdrawal"


@pytest.mark.parametrize("path", ["research/DECISION_LOG.md", "research/BACKLOG.md"])
def test_decision_record_exists_for_the_withdrawal(path):
    text = open(os.path.join(REPO, path), encoding="utf-8").read()
    assert "P0-2" in text or "D-026" in text, f"{path} does not record the withdrawal"
