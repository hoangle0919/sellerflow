"""Guards for the retracted "identical either way" claim (product-side).

An earlier README paragraph — written by this workstream, not the research one —
said that because the financing arithmetic never calls the model, "the numbers
shown are identical either way" whichever scoring path is active. That is false.
The arithmetic is deterministic *given a risk tier*, but the scorer assigns the
tier, and every downstream term keys off it. These tests pin both halves: the
empirical fact that the paths disagree, and the copy that must not re-assert
the retraction.
"""
import os
import re
import importlib
import tempfile
import random

import pytest

import financing_engine as fe

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BACKEND)          # backend/tests -> backend -> repo root
PUBLIC_COPY = [
    os.path.join(REPO, "README.md"),
    os.path.join(REPO, "frontend", "index.html"),
]


def test_the_public_copy_paths_actually_exist():
    """A skip is not a pass. The copy guard below silently skipped when this
    module computed the repo root one level too shallow; assert the fixtures
    resolve so the guard can never quietly stop guarding."""
    for path in PUBLIC_COPY:
        assert os.path.exists(path), f"public copy fixture missing: {path}"

# The sentence that retracts the claim is allowed to quote it; an active
# assertion of it is not. A line is exempt only if it also carries retraction
# language, which keeps the guard from being defeated by paraphrase.
RETRACTION_MARKERS = ("retract", "was wrong", "no longer", "superseded", "earlier version")
BANNED = re.compile(
    r"identical either way"
    r"|numbers\s+(shown\s+)?are\s+identical"
    r"|same\s+numbers\s+either\s+way"
    r"|(unchanged|identical)\s+(whether|regardless of)\s+(the\s+)?(scoring|model|path)",
    re.I,
)


@pytest.mark.parametrize("path", PUBLIC_COPY)
def test_public_copy_does_not_assert_the_retracted_equivalence(path):
    if not os.path.exists(path):
        pytest.skip(f"{path} not present")
    offenders = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if BANNED.search(line) and not any(m in line.lower() for m in RETRACTION_MARKERS):
            offenders.append(f"{os.path.basename(path)}:{n}: {line.strip()[:140]}")
    assert not offenders, (
        "Public copy asserts the retracted claim that the scoring path does not "
        "change the numbers:\n  " + "\n  ".join(offenders)
    )


def test_the_tier_actually_moves_every_contractual_term():
    """The reason the claim is false: terms key off the tier, so a tier change
    is a term change. Hand-checked at 200M monthly revenue."""
    low = fe.financing_structure(200_000_000, "Low Risk")
    med = fe.financing_structure(200_000_000, "Medium Risk")
    high = fe.financing_structure(200_000_000, "High Risk")

    assert low["repayment_cap"] == 414_000_000
    assert med["repayment_cap"] == 249_600_000
    assert high["recommended_amount"] == 0          # High Risk declines outright

    assert low["remittance_pct"] != med["remittance_pct"]
    assert low["factor_rate"] != med["factor_rate"]
    assert low["recommended_amount"] > med["recommended_amount"]


def test_the_two_scoring_paths_disagree_on_tier_in_practice():
    """Not a theoretical difference. Scored both ways over a fixed pseudo-random
    cohort, the paths assign different tiers for a substantial share of
    profiles — including profiles that one path approves and the other declines.

    Skips (rather than fails) when no ensemble artifact is present, because a
    clean checkout has none and that is a legitimate state.
    """
    import ml_engine

    def tiers_under(model_dir):
        os.environ["RBF_MODEL_DIR"] = model_dir
        importlib.reload(ml_engine)
        ml_engine.load_models()
        return (
            ml_engine.model_status()["scoring_path"],
            [ml_engine.score(p)["risk_tier"] for p in COHORT],
        )

    rng = random.Random(11)
    COHORT = [
        dict(
            monthly_revenue=rng.uniform(20e6, 500e6), revenue_growth=rng.uniform(-0.25, 0.5),
            order_volume=rng.randint(60, 900), avg_order_value=rng.uniform(150e3, 900e3),
            return_rate=rng.uniform(0.005, 0.25), rating=rng.uniform(3.2, 5.0),
            days_active=rng.randint(40, 1300), inventory_turnover=rng.uniform(2, 10),
            previous_loans=rng.randint(0, 4), late_ship_rate=rng.uniform(0.005, 0.2),
        )
        for _ in range(200)
    ]

    original = os.environ.get("RBF_MODEL_DIR")
    try:
        path_a, tiers_a = tiers_under(tempfile.mkdtemp())          # no artifact -> heuristic
        path_b, tiers_b = tiers_under(os.path.join(BACKEND, "models"))
        if path_a == path_b:
            pytest.skip("no ensemble artifact available; cannot compare two paths")
        assert path_a == "heuristic" and path_b == "ensemble"

        disagreements = sum(1 for a, b in zip(tiers_a, tiers_b) if a != b)
        assert disagreements > 0, (
            "The scoring paths agreed on every profile. If this ever becomes "
            "genuinely true, the retracted claim would deserve revisiting — but "
            "verify it deliberately rather than assuming it."
        )
        # And the strong form: at least one profile flips between fundable and not.
        flips = sum(
            1 for a, b in zip(tiers_a, tiers_b)
            if (a == "High Risk") != (b == "High Risk")
        )
        assert flips > 0, "expected at least one approve/decline flip between paths"
    finally:
        if original is None:
            os.environ.pop("RBF_MODEL_DIR", None)
        else:
            os.environ["RBF_MODEL_DIR"] = original
        importlib.reload(ml_engine)
        ml_engine.load_models()
