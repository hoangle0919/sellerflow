"""Deterministic revenue-based-financing (RBF) analysis.

Every function here is pure arithmetic over the fields the seller submits.
Nothing in this module calls a language model — RBF's own rule (Part V of
its own design brief) is that AI may explain a number, never compute one.

RBF structure, in one paragraph: a financier advances a lump sum against a
share of future revenue ("remittance"). The merchant repays a fixed multiple
of the advance (the "repayment cap"), collected as remittance_pct of revenue
each period until the cap is paid off. Because the periodic payment is a
percentage of revenue rather than a fixed installment, it shrinks when
revenue shrinks — the tradeoff is a longer repayment period, not a missed
payment. That's the whole reason RBF underwriting cares about revenue
*trend* and *stability* more than a traditional fixed-installment lender
would: a decline doesn't default the merchant, it extends the term.
"""

import math
from typing import Optional, List

# Risk-tier parameters. These are underwriting policy, not a fitted model —
# documented here so they're one place to change, not scattered constants.
TIER_PARAMS = {
    "Low Risk":    {"advance_pct_of_annual_revenue": 0.15, "remittance_pct": 0.08, "factor_rate": 1.15},
    "Medium Risk": {"advance_pct_of_annual_revenue": 0.08, "remittance_pct": 0.12, "factor_rate": 1.30},
    "High Risk":   {"advance_pct_of_annual_revenue": 0.00, "remittance_pct": 0.00, "factor_rate": 0.00},
}

MIN_MEANINGFUL_GROWTH = 0.05  # floor used only to keep the "growth case" distinct from base


def revenue_metrics(monthly_revenue: float, revenue_growth: float, revenue_history: Optional[List[float]] = None) -> dict:
    """Revenue-shape metrics. Only computes what the submitted data actually supports.

    `revenue_history` is optional (oldest first). The current product only
    collects a single current-period revenue figure plus a reported MoM
    growth rate — so unless a caller supplies history, volatility-type
    metrics are honestly reported as missing rather than invented from one
    data point.
    """
    result = {
        "current_monthly_revenue": {"value": round(monthly_revenue, 0), "provenance": "user_entered_fact"},
        "reported_mom_growth": {"value": round(revenue_growth, 4), "provenance": "user_entered_fact"},
        "average_monthly_revenue": None,
        "median_monthly_revenue": None,
        "volatility_coefficient_of_variation": None,
        "max_peak_to_trough_decline": None,
        "negative_growth_periods": None,
        "data_sufficiency": "single_period_only",
    }
    if not revenue_history or len(revenue_history) < 2:
        result["missing_data_note"] = (
            "Only one revenue period was provided. Average revenue, volatility, and drawdown "
            "cannot be computed from a single figure — submit monthly revenue history to unlock them."
        )
        return result

    n = len(revenue_history)
    mean = sum(revenue_history) / n
    variance = sum((x - mean) ** 2 for x in revenue_history) / n
    stdev = math.sqrt(variance)
    sorted_hist = sorted(revenue_history)
    median = (sorted_hist[n // 2] if n % 2 else (sorted_hist[n // 2 - 1] + sorted_hist[n // 2]) / 2)

    peak = revenue_history[0]
    max_decline = 0.0
    negative_periods = 0
    for i in range(1, n):
        if revenue_history[i] > peak:
            peak = revenue_history[i]
        elif peak > 0:
            decline = (peak - revenue_history[i]) / peak
            max_decline = max(max_decline, decline)
        if revenue_history[i] < revenue_history[i - 1]:
            negative_periods += 1

    result.update({
        "average_monthly_revenue": {"value": round(mean, 0), "provenance": "system_derived_metric"},
        "median_monthly_revenue": {"value": round(median, 0), "provenance": "system_derived_metric"},
        "volatility_coefficient_of_variation": {
            "value": round(stdev / mean, 4) if mean > 0 else None, "provenance": "system_derived_metric"
        },
        "max_peak_to_trough_decline": {"value": round(max_decline, 4), "provenance": "system_derived_metric"},
        "negative_growth_periods": {"value": negative_periods, "provenance": "system_derived_metric"},
        "data_sufficiency": "full_history",
    })
    return result


def financing_structure(monthly_revenue: float, risk_tier: str, requested_amount: Optional[float] = None) -> dict:
    """Recommended RBF structure for the given revenue and risk tier.

    Formulas (all deterministic):
      recommended_amount = monthly_revenue * 12 * advance_pct_of_annual_revenue[tier]
      repayment_cap       = amount * factor_rate[tier]
      periodic_remittance = monthly_revenue * remittance_pct[tier]
      base_case_duration  = ceil(repayment_cap / periodic_remittance)   [months]
    """
    params = TIER_PARAMS.get(risk_tier, TIER_PARAMS["High Risk"])
    annual_revenue = monthly_revenue * 12
    recommended_amount = round(annual_revenue * params["advance_pct_of_annual_revenue"], -3)

    if params["remittance_pct"] == 0 or recommended_amount <= 0:
        return {
            "risk_tier": risk_tier,
            "recommended_amount": 0.0,
            "requested_amount": requested_amount,
            "remittance_pct": 0.0,
            "factor_rate": 0.0,
            "repayment_cap": 0.0,
            "periodic_remittance": 0.0,
            "base_case_duration_months": None,
            "note": "This risk tier does not support a financing recommendation. No structure is proposed.",
        }

    amount = requested_amount if requested_amount and requested_amount > 0 else recommended_amount
    exceeds_recommendation = bool(requested_amount and requested_amount > recommended_amount)

    repayment_cap = round(amount * params["factor_rate"], 0)
    periodic_remittance = round(monthly_revenue * params["remittance_pct"], 0)
    duration_months = math.ceil(repayment_cap / periodic_remittance) if periodic_remittance > 0 else None

    return {
        "risk_tier": risk_tier,
        "recommended_amount": recommended_amount,
        "requested_amount": requested_amount,
        "amount_used_for_structure": amount,
        "exceeds_recommendation": exceeds_recommendation,
        "remittance_pct": params["remittance_pct"],
        "factor_rate": params["factor_rate"],
        "repayment_cap": repayment_cap,
        "periodic_remittance": periodic_remittance,
        "base_case_duration_months": duration_months,
    }


def scenario_analysis(monthly_revenue: float, reported_growth: float, structure: dict) -> list[dict]:
    """Base / moderate decline / severe decline / growth repayment scenarios.

    Because remittance is a fixed percentage of revenue, the merchant's
    post-remittance revenue share is unchanged by revenue swings — what
    changes is the absolute remittance amount and, inversely, how long
    repayment takes. That mechanical fact is the actual point of RBF
    scenario analysis, so it's stated explicitly rather than buried in a
    chart.
    """
    remittance_pct = structure.get("remittance_pct", 0)
    repayment_cap = structure.get("repayment_cap", 0)
    if not remittance_pct or not repayment_cap:
        return []

    growth_case_rate = max(reported_growth, MIN_MEANINGFUL_GROWTH)
    cases = [
        ("base", "Base case", 0.0),
        ("moderate_decline", "Moderate revenue decline (-20%)", -0.20),
        ("severe_decline", "Severe revenue decline (-40%)", -0.40),
        ("growth", f"Revenue growth (+{growth_case_rate:.0%})", growth_case_rate),
    ]
    out = []
    for key, label, shift in cases:
        scenario_revenue = round(monthly_revenue * (1 + shift), 0)
        periodic_remittance = round(scenario_revenue * remittance_pct, 0)
        duration_months = math.ceil(repayment_cap / periodic_remittance) if periodic_remittance > 0 else None
        out.append({
            "case": key,
            "label": label,
            "assumption": "system_derived_metric" if key == "base" else "assumption",
            "scenario_monthly_revenue": scenario_revenue,
            "periodic_remittance": periodic_remittance,
            "repayment_duration_months": duration_months,
            "merchant_retained_revenue_pct": round(1 - remittance_pct, 4),
        })
    return out


# (category, condition_field, severity_thresholds, evidence_fmt, why_it_matters, resolution)
def risk_findings(features: dict) -> list[dict]:
    """Deterministic, categorized risk findings from the submitted signals.

    Every finding here is a rule over a submitted field — none of it is
    inferred by a model or a language model. `deterministic: True` on every
    entry is the explicit claim being made.
    """
    findings = []

    def sev(value, low, high, higher_is_worse=True):
        if higher_is_worse:
            return "low" if value <= low else "medium" if value <= high else "high"
        return "low" if value >= low else "medium" if value >= high else "high"

    growth = features.get("revenue_growth", 0)
    findings.append({
        "category": "Revenue trend",
        "severity": sev(growth, 0.10, 0.0, higher_is_worse=False),
        "evidence": f"{growth:+.0%} month-over-month",
        "why_it_matters": "Revenue-based repayment scales with revenue — a declining trend extends the repayment period even without a missed payment.",
        "deterministic": True,
        "resolution_needed": None if growth >= 0 else "Provide trailing revenue history to confirm whether the decline is transient or structural.",
    })

    findings.append({
        "category": "Revenue stability",
        "severity": "unknown",
        "evidence": "Only a single current-period revenue figure was submitted.",
        "why_it_matters": "Volatility and seasonality materially affect how reliably a merchant can sustain a fixed remittance percentage.",
        "deterministic": True,
        "resolution_needed": "Submit 6–12 months of revenue history to assess volatility and seasonality.",
    })

    ret = features.get("return_rate", 0)
    late = features.get("late_ship_rate", 0)
    rating = features.get("rating", 5)
    fulfillment_sev = "high" if (ret > 0.15 or late > 0.12 or rating < 3.8) else "medium" if (ret > 0.08 or late > 0.06 or rating < 4.5) else "low"
    findings.append({
        "category": "Fulfillment and customer experience",
        "severity": fulfillment_sev,
        "evidence": f"{ret:.1%} return rate · {late:.1%} late shipments · {rating:.1f}/5.0 rating",
        "why_it_matters": "Elevated returns and late shipments both suppress net revenue and signal operational strain that can precede a revenue decline.",
        "deterministic": True,
        "resolution_needed": None,
    })

    days_active = features.get("days_active", 0)
    findings.append({
        "category": "Business maturity",
        "severity": sev(days_active, 365, 180, higher_is_worse=False),
        "evidence": f"{days_active} days active on the platform",
        "why_it_matters": "Shorter operating history means fewer revenue cycles to evaluate stability against — the same revenue figure carries more uncertainty from a newer store.",
        "deterministic": True,
        "resolution_needed": None if days_active > 365 else "Longer operating history would reduce uncertainty; not resolvable before more time has passed.",
    })

    turnover = features.get("inventory_turnover", 0)
    findings.append({
        "category": "Operational efficiency",
        "severity": sev(turnover, 4, 2, higher_is_worse=False),
        "evidence": f"{turnover:.1f}x inventory turnover",
        "why_it_matters": "Slow-moving inventory ties up cash that would otherwise support the remittance obligation.",
        "deterministic": True,
        "resolution_needed": None,
    })

    prev_loans = features.get("previous_loans", 0)
    findings.append({
        "category": "Existing obligations",
        "severity": "medium" if prev_loans > 0 else "low",
        "evidence": f"{prev_loans} prior financing arrangement(s) on record",
        "why_it_matters": "Concurrent remittance obligations compound the share of revenue already committed away from operations.",
        "deterministic": True,
        "resolution_needed": "Provide the repayment schedule and remaining balance of any existing financing to net it against capacity." if prev_loans > 0 else None,
    })

    findings.append({
        "category": "Data completeness",
        "severity": "medium",
        "evidence": "No operating-expense, margin, or platform-concentration data submitted.",
        "why_it_matters": "Gross margin and fixed costs determine how much of remitted revenue the merchant can actually absorb without straining operations.",
        "deterministic": True,
        "resolution_needed": "Submit gross margin, operating expenses, and platform revenue split to complete the assessment.",
    })

    return findings


def build_financing_analysis(features: dict, risk_tier: str, requested_amount: Optional[float] = None) -> dict:
    """Orchestrates the full deterministic RBF analysis for one submission."""
    revenue = revenue_metrics(features.get("monthly_revenue", 0), features.get("revenue_growth", 0))
    structure = financing_structure(features.get("monthly_revenue", 0), risk_tier, requested_amount)
    scenarios = scenario_analysis(features.get("monthly_revenue", 0), features.get("revenue_growth", 0), structure)
    risks = risk_findings(features)
    missing = [f["resolution_needed"] for f in risks if f.get("resolution_needed")]
    return {
        "revenue": revenue,
        "structure": structure,
        "scenarios": scenarios,
        "risk_findings": risks,
        "information_needed": missing,
        "data_completeness_pct": round(100 * (1 - len(missing) / max(len(risks), 1)), 0),
    }
