import pytest

from integrity_engine import screen_integrity, DISCLOSURE


def clean_profile(**over):
    base = dict(
        monthly_revenue=185_000_000, revenue_growth=0.22, order_volume=420,
        avg_order_value=440_000, return_rate=0.028, rating=4.9,
        days_active=680, inventory_turnover=6.2, late_ship_rate=0.018,
        previous_loans=2,
    )
    base.update(over)
    return base


def by_name(result, name):
    return next(c for c in result["checks"] if c["check"] == name)


def test_clean_profile_is_clear():
    r = screen_integrity(clean_profile(), prior_submissions=[])
    assert r["level"] == "clear"
    assert r["flags"] == 0
    assert r["checks_run"] == 5
    assert all(c["status"] == "pass" for c in r["checks"])


def test_disclosure_always_present():
    r = screen_integrity(clean_profile())
    assert r["disclosure"] == DISCLOSURE
    assert r["method"] == "deterministic_rules"


def test_preview_mode_skips_resubmission_check():
    r = screen_integrity(clean_profile(), prior_submissions=None)
    assert r["checks_run"] == 4
    assert all(c["check"] != "Resubmission consistency" for c in r["checks"])


def test_inflated_revenue_flags_reconciliation():
    # claimed revenue ~3.2x what orders x AOV support -> high severity
    r = screen_integrity(clean_profile(monthly_revenue=600_000_000))
    c = by_name(r, "Revenue reconciliation")
    assert c["status"] == "flag"
    assert c["severity"] == "high"
    assert r["level"] == "high"


def test_moderately_inconsistent_revenue_is_medium():
    # ratio ~2.0 -> outside band but below the 2.5x high threshold
    r = screen_integrity(clean_profile(monthly_revenue=370_000_000))
    c = by_name(r, "Revenue reconciliation")
    assert c["status"] == "flag"
    assert c["severity"] == "medium"
    assert r["level"] == "review"


def test_perfect_rating_with_high_returns_contradicts():
    r = screen_integrity(clean_profile(return_rate=0.18, monthly_revenue=150_000_000,
                                       order_volume=340))
    c = by_name(r, "Quality-signal consistency")
    assert c["status"] == "flag"
    assert "returns" in c["evidence"]


def test_young_store_with_stacked_loans_is_high():
    r = screen_integrity(clean_profile(days_active=45, previous_loans=3))
    c = by_name(r, "Exposure velocity")
    assert c["status"] == "flag"
    assert c["severity"] == "high"
    assert r["level"] == "high"


def test_mature_store_hypergrowth_is_soft_flag():
    r = screen_integrity(clean_profile(revenue_growth=0.5, days_active=900))
    c = by_name(r, "Growth plausibility")
    assert c["status"] == "flag"
    assert c["severity"] == "low"
    assert r["level"] == "watch"


def test_resubmission_divergence_flags_large_delta():
    r = screen_integrity(
        clean_profile(),
        prior_submissions=[{"monthly_revenue": 90_000_000}],
    )
    c = by_name(r, "Resubmission consistency")
    assert c["status"] == "flag"
    assert c["severity"] == "high"


def test_resubmission_within_band_passes():
    r = screen_integrity(
        clean_profile(),
        prior_submissions=[{"monthly_revenue": 170_000_000}],
    )
    c = by_name(r, "Resubmission consistency")
    assert c["status"] == "pass"


def test_integrity_never_returns_decision_fields():
    """The screen must stay a parallel signal: it never emits credit-decision
    vocabulary that could be mistaken for (or merged into) the PD model."""
    r = screen_integrity(clean_profile())
    assert "decision" not in r and "pd_score" not in r and "credit_limit" not in r
