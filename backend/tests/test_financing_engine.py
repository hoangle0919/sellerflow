"""Tests for backend/financing_engine.py.

These assert financial outcomes with independently hand-computed expected
values (shown in the comments), not just "the function ran without error."
"""
import math
import pytest

from financing_engine import (
    revenue_metrics,
    financing_structure,
    scenario_analysis,
    risk_findings,
    build_financing_analysis,
)

GOOD_FEATURES = {
    "monthly_revenue": 150_000_000, "revenue_growth": 0.22, "order_volume": 420,
    "avg_order_value": 440_000, "return_rate": 0.028, "rating": 4.9,
    "days_active": 680, "inventory_turnover": 6.2, "late_ship_rate": 0.018,
    "previous_loans": 0,
}
BAD_FEATURES = {
    "monthly_revenue": 30_000_000, "revenue_growth": -0.20, "order_volume": 60,
    "avg_order_value": 200_000, "return_rate": 0.22, "rating": 3.0,
    "days_active": 45, "inventory_turnover": 1.0, "late_ship_rate": 0.18,
    "previous_loans": 2,
}


# ── revenue_metrics ──

def test_revenue_metrics_single_period_reports_insufficient_data():
    r = revenue_metrics(100_000_000, 0.15, revenue_history=None)
    assert r["current_monthly_revenue"]["value"] == 100_000_000
    assert r["reported_mom_growth"]["value"] == 0.15
    assert r["data_sufficiency"] == "single_period_only"
    assert r["average_monthly_revenue"] is None
    assert r["volatility_coefficient_of_variation"] is None
    assert "missing_data_note" in r


def test_revenue_metrics_with_history_computes_real_statistics():
    # mean=87.6, variance=25.04, stdev≈5.00399, cov≈0.0571
    # sorted=[80,85,88,90,95] -> median=88
    # peak path: 80->85->90 (peak=90); 88 is a decline of (90-88)/90=0.02222; 95 resets peak (no decline calc)
    # negative periods: only 88<90 -> 1
    history = [80, 85, 90, 88, 95]
    r = revenue_metrics(87_600_000, 0.05, revenue_history=history)
    assert r["data_sufficiency"] == "full_history"
    assert r["average_monthly_revenue"]["value"] == 88  # round(87.6)
    assert r["median_monthly_revenue"]["value"] == 88
    assert r["volatility_coefficient_of_variation"]["value"] == pytest.approx(0.0571, abs=1e-4)
    assert r["max_peak_to_trough_decline"]["value"] == pytest.approx(0.0222, abs=1e-4)
    assert r["negative_growth_periods"]["value"] == 1


def test_revenue_metrics_single_point_history_is_still_insufficient():
    r = revenue_metrics(50_000_000, 0.0, revenue_history=[50_000_000])
    assert r["data_sufficiency"] == "single_period_only"


# ── financing_structure ──

def test_financing_structure_low_risk_base_case():
    # annual = 1,800,000,000; recommended = 0.15 * annual = 270,000,000
    # repayment_cap = 270,000,000 * 1.15 = 310,500,000
    # periodic_remittance = 150,000,000 * 0.08 = 12,000,000
    # duration = ceil(310,500,000 / 12,000,000) = ceil(25.875) = 26
    s = financing_structure(150_000_000, "Low Risk")
    assert s["recommended_amount"] == 270_000_000
    assert s["amount_used_for_structure"] == 270_000_000
    assert s["exceeds_recommendation"] is False
    assert s["repayment_cap"] == 310_500_000
    assert s["periodic_remittance"] == 12_000_000
    assert s["base_case_duration_months"] == 26


def test_financing_structure_high_risk_declines_structure():
    s = financing_structure(150_000_000, "High Risk")
    assert s["recommended_amount"] == 0.0
    assert s["repayment_cap"] == 0.0
    assert s["base_case_duration_months"] is None
    assert "note" in s


def test_financing_structure_requested_amount_exceeding_recommendation_is_flagged():
    # annual = 1,200,000,000; recommended = 0.08 * annual = 96,000,000
    # requested 150,000,000 > recommended -> exceeds_recommendation True
    # repayment_cap = 150,000,000 * 1.30 = 195,000,000
    # periodic_remittance = 100,000,000 * 0.12 = 12,000,000
    # duration = ceil(195,000,000 / 12,000,000) = ceil(16.25) = 17
    s = financing_structure(100_000_000, "Medium Risk", requested_amount=150_000_000)
    assert s["recommended_amount"] == 96_000_000
    assert s["amount_used_for_structure"] == 150_000_000
    assert s["exceeds_recommendation"] is True
    assert s["repayment_cap"] == 195_000_000
    assert s["base_case_duration_months"] == 17


def test_financing_structure_requested_amount_below_recommendation_is_not_flagged():
    s = financing_structure(100_000_000, "Medium Risk", requested_amount=50_000_000)
    assert s["amount_used_for_structure"] == 50_000_000
    assert s["exceeds_recommendation"] is False


def test_financing_structure_zero_revenue_does_not_crash():
    s = financing_structure(0, "Low Risk")
    assert s["recommended_amount"] == 0.0
    assert s["base_case_duration_months"] is None


# ── scenario_analysis ──

def test_scenario_analysis_base_matches_structure_duration():
    structure = financing_structure(150_000_000, "Low Risk")  # duration 26, remittance 12,000,000
    scenarios = scenario_analysis(150_000_000, 0.10, structure)
    base = next(s for s in scenarios if s["case"] == "base")
    assert base["scenario_monthly_revenue"] == 150_000_000
    assert base["periodic_remittance"] == 12_000_000
    assert base["repayment_duration_months"] == structure["base_case_duration_months"] == 26


def test_scenario_analysis_decline_and_growth_cases():
    # repayment_cap=310,500,000, remittance_pct=0.08, growth input 0.10 (above 5% floor)
    structure = financing_structure(150_000_000, "Low Risk")
    scenarios = {s["case"]: s for s in scenario_analysis(150_000_000, 0.10, structure)}

    moderate = scenarios["moderate_decline"]
    assert moderate["scenario_monthly_revenue"] == 120_000_000  # -20%
    assert moderate["periodic_remittance"] == 9_600_000
    assert moderate["repayment_duration_months"] == math.ceil(310_500_000 / 9_600_000) == 33

    severe = scenarios["severe_decline"]
    assert severe["scenario_monthly_revenue"] == 90_000_000  # -40%
    assert severe["periodic_remittance"] == 7_200_000
    assert severe["repayment_duration_months"] == math.ceil(310_500_000 / 7_200_000) == 44

    growth = scenarios["growth"]
    assert growth["scenario_monthly_revenue"] == 165_000_000  # +10%
    assert growth["periodic_remittance"] == 13_200_000
    assert growth["repayment_duration_months"] == math.ceil(310_500_000 / 13_200_000) == 24

    # Merchant's retained revenue share is unchanged by revenue level -- proportional remittance.
    assert all(s["merchant_retained_revenue_pct"] == pytest.approx(0.92) for s in scenarios.values())

    # Duration must strictly worsen (increase) moving from growth -> base -> moderate -> severe.
    durations = [scenarios["growth"]["repayment_duration_months"], scenarios["base"]["repayment_duration_months"],
                 moderate["repayment_duration_months"], severe["repayment_duration_months"]]
    assert durations == sorted(durations)


def test_scenario_analysis_growth_rate_floor_applies_when_reported_growth_is_negative():
    # reported growth -0.05 is below the 5% floor, so the growth case uses +5% not -5%.
    structure = financing_structure(150_000_000, "Low Risk")
    scenarios = {s["case"]: s for s in scenario_analysis(150_000_000, -0.05, structure)}
    growth = scenarios["growth"]
    assert growth["scenario_monthly_revenue"] == 157_500_000  # 150M * 1.05


def test_scenario_analysis_empty_when_structure_has_no_remittance():
    structure = financing_structure(150_000_000, "High Risk")
    assert scenario_analysis(150_000_000, 0.10, structure) == []


# ── risk_findings ──

def test_risk_findings_covers_expected_categories():
    categories = {f["category"] for f in risk_findings(GOOD_FEATURES)}
    assert categories == {
        "Revenue trend", "Revenue stability", "Fulfillment and customer experience",
        "Business maturity", "Operational efficiency", "Existing obligations", "Data completeness",
    }


def test_risk_findings_all_marked_deterministic():
    assert all(f["deterministic"] is True for f in risk_findings(GOOD_FEATURES))


def test_risk_findings_good_profile_is_mostly_low_severity():
    findings = {f["category"]: f for f in risk_findings(GOOD_FEATURES)}
    assert findings["Revenue trend"]["severity"] == "low"
    assert findings["Fulfillment and customer experience"]["severity"] == "low"
    assert findings["Business maturity"]["severity"] == "low"
    assert findings["Operational efficiency"]["severity"] == "low"
    assert findings["Existing obligations"]["severity"] == "low"
    # Revenue stability is always "unknown" -- single-period data can't say otherwise.
    assert findings["Revenue stability"]["severity"] == "unknown"


def test_risk_findings_bad_profile_is_mostly_high_severity():
    findings = {f["category"]: f for f in risk_findings(BAD_FEATURES)}
    assert findings["Revenue trend"]["severity"] == "high"
    assert findings["Fulfillment and customer experience"]["severity"] == "high"
    assert findings["Business maturity"]["severity"] == "high"
    assert findings["Operational efficiency"]["severity"] == "high"
    assert findings["Existing obligations"]["severity"] == "medium"
    assert findings["Existing obligations"]["resolution_needed"] is not None


# ── build_financing_analysis (integration) ──

def test_build_financing_analysis_good_profile_completeness():
    result = build_financing_analysis(GOOD_FEATURES, "Low Risk")
    assert set(result.keys()) == {
        "revenue", "structure", "scenarios", "risk_findings", "information_needed", "data_completeness_pct",
    }
    # 7 findings total; only "Revenue stability" and "Data completeness" carry an
    # unconditional resolution note for this profile -> 2/7 missing.
    assert len(result["information_needed"]) == 2
    assert result["data_completeness_pct"] == pytest.approx(71.0, abs=0.5)
    assert len(result["scenarios"]) == 4


def test_build_financing_analysis_bad_profile_has_more_gaps():
    result = build_financing_analysis(BAD_FEATURES, "High Risk")
    # High Risk -> no financing structure -> no scenarios.
    assert result["structure"]["recommended_amount"] == 0.0
    assert result["scenarios"] == []
    # Missing-resolution findings for this profile: Revenue trend (growth < 0),
    # Revenue stability (always), Business maturity (days_active <= 365),
    # Existing obligations (previous_loans > 0), Data completeness (always) -> 5/7.
    assert len(result["information_needed"]) == 5
    assert result["data_completeness_pct"] == pytest.approx(28.6, abs=0.5)
