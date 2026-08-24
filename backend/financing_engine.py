"""Deterministic revenue-based-financing (RBF) analysis.

Every function here is pure arithmetic over the fields the seller submits.
Nothing in this module calls a language model — RBF's own rule (Part V of
its own design brief) is that AI may explain a number, never compute one.

RBF structure, in one paragraph: a financier advances a lump sum against a
share of future revenue ("remittance"). The merchant repays a fixed multiple
of the advance (the "repayment cap"), collected as remittance_pct of revenue
each period until the cap is paid off. Because the periodic payment is a
percentage of revenue rather than a fixed installment, it shrinks when
revenue shrinks — so a decline lengthens the expected repayment period
rather than raising the scheduled payment.

That is a statement about the payment RULE, not about outcomes. This is not a
claim of default prevention. Where revenue stops for long
enough before the cap is reached, the cap is simply never reached and a
contractual balance goes unrecovered: in the simulated closure scenarios,
permanent closure from month 7 leaves 100% of paths incomplete at both
registered cap factors. Revenue-contingency changes who bears the timing
risk; it does not remove the risk. See `research/CLAIM_LEDGER.md` S-3, I-3.

This is why RBF underwriting attends to revenue *trend* and *stability*:
duration, not just level, drives recovery.
"""

import math
from typing import Optional, List

from money import (illustrative_schedule, periodic_payment, recommended_advance,
                   repayment_cap, to_vnd)

# Risk-tier parameters. These are underwriting policy, not a fitted model —
# documented here so they're one place to change, not scattered constants.
#
# Rates are declared as STRINGS and converted with Decimal (D-030). `0.15` as a
# binary float is 0.1499999999999999944…; every contractual figure derived from
# it inherits that error, and at a rounding tie the error decides the merchant's
# advance. The float forms below are for API/display only and never enter a
# monetary calculation.
TIER_RATES = {
    "Low Risk":    {"advance_pct_of_annual_revenue": "0.15", "remittance_pct": "0.08", "factor_rate": "1.15"},
    "Medium Risk": {"advance_pct_of_annual_revenue": "0.08", "remittance_pct": "0.12", "factor_rate": "1.30"},
    "High Risk":   {"advance_pct_of_annual_revenue": "0.00", "remittance_pct": "0.00", "factor_rate": "0.00"},
}

TIER_PARAMS = {
    tier: {k: float(v) for k, v in rates.items()} for tier, rates in TIER_RATES.items()
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
        # D-030 classification: NOT contractual money. This echoes a user-entered
        # input and the statistics below summarise it; neither is a term the
        # merchant is offered, so neither goes through the VND settlement policy.
        # Only advance, cap, remittance and credit limit do.
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

    Formulas — all deterministic, all in integer đồng under ROUND_HALF_UP
    (D-030; see `money.py` for why the order is fixed):
      1. raw advance       = monthly_revenue * 12 * advance_pct[tier]   (Decimal)
      2. recommended_amount= ROUND_HALF_UP to the 1,000 VND increment
      3. raw cap           = amount * factor_rate[tier]                 (Decimal)
      4. repayment_cap     = ROUND_HALF_UP to whole VND
      5. periodic_remittance = ROUND_HALF_UP(monthly_revenue * remittance_pct)
      6. final payment clipped to the remaining balance
      7. cumulative never exceeds the cap

    `base_case_duration_months` is `ceil(cap / remittance)` — correct, because
    the final payment is PARTIAL. `illustrative_schedule` states that
    explicitly so no reader computes `remittance * duration` and overstates
    the total (D-029).
    """
    rates = TIER_RATES.get(risk_tier, TIER_RATES["High Risk"])
    params = TIER_PARAMS.get(risk_tier, TIER_PARAMS["High Risk"])
    recommended_amount = recommended_advance(monthly_revenue,
                                             rates["advance_pct_of_annual_revenue"])

    if params["remittance_pct"] == 0 or recommended_amount <= 0:
        return {
            "risk_tier": risk_tier,
            "recommended_amount": 0,
            "requested_amount": requested_amount,
            "remittance_pct": 0.0,
            "factor_rate": 0.0,
            "repayment_cap": 0,
            "periodic_remittance": 0,
            "base_case_duration_months": None,
            "illustrative_schedule": None,
            "note": "This risk tier does not support a financing recommendation. No structure is proposed.",
        }

    amount = (to_vnd(requested_amount)
              if requested_amount and requested_amount > 0 else recommended_amount)
    exceeds_recommendation = bool(requested_amount and requested_amount > recommended_amount)

    cap = repayment_cap(amount, rates["factor_rate"])
    remittance = periodic_payment(monthly_revenue, rates["remittance_pct"])
    duration_months = math.ceil(cap / remittance) if remittance > 0 else None

    return {
        "risk_tier": risk_tier,
        "recommended_amount": recommended_amount,
        "requested_amount": requested_amount,
        "amount_used_for_structure": amount,
        "exceeds_recommendation": exceeds_recommendation,
        "remittance_pct": params["remittance_pct"],
        "factor_rate": params["factor_rate"],
        "repayment_cap": cap,
        "total_contractual_repayment": cap,
        "periodic_remittance": remittance,
        "base_case_duration_months": duration_months,
        "illustrative_schedule": illustrative_schedule(cap, remittance),
        "monetary_policy": "integer VND, ROUND_HALF_UP; final payment clipped "
                           "to the remaining balance (D-030)",
    }


# Month at which the illustrative permanent-closure scenario stops revenue.
# 7 is the registered simulation case (research/CLAIM_LEDGER.md S-3, I-3): at
# both registered cap factors, permanent closure from month 7 leaves 100% of
# paths incomplete. It is the earliest registered case and therefore the
# honest one to show — the decline rows already cover the survivable end.
CLOSURE_SCENARIO_MONTH = 7


def scenario_analysis(monthly_revenue: float, reported_growth: float, structure: dict) -> list[dict]:
    """Base / moderate decline / severe decline / growth / closure scenarios.

    Because remittance is a fixed percentage of revenue, the merchant's
    post-remittance revenue share is unchanged by revenue swings — what
    changes is the absolute remittance amount and, inversely, how long
    repayment takes. That mechanical fact is the actual point of RBF
    scenario analysis, so it's stated explicitly rather than buried in a
    chart.

    The decline rows all repay: that is the mechanism working. The closure row
    is the case where it does not. Revenue-contingency moves timing risk to the
    provider; it does not remove the risk, and a scenario table that only shows
    survivable declines would overstate the instrument. See the module
    docstring and `research/CLAIM_LEDGER.md` S-3, I-3.
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
    # Use the exact decimal string for the tier, not the float echo, so the
    # scenario rows are computed under the same policy as the structure.
    share_rate = TIER_RATES.get(structure.get("risk_tier", ""), {}).get(
        "remittance_pct", repr(remittance_pct))
    out = []
    for key, label, shift in cases:
        # D-030: integer đồng under ROUND_HALF_UP, same policy as the structure.
        scenario_revenue = to_vnd(monthly_revenue * (1 + shift))
        scenario_remittance = periodic_payment(scenario_revenue, share_rate)
        duration_months = (math.ceil(repayment_cap / scenario_remittance)
                           if scenario_remittance > 0 else None)
        out.append({
            "case": key,
            "label": label,
            "assumption": "system_derived_metric" if key == "base" else "assumption",
            "scenario_monthly_revenue": scenario_revenue,
            "periodic_remittance": scenario_remittance,
            "repayment_duration_months": duration_months,
            "merchant_retained_revenue_pct": round(1 - remittance_pct, 4),
            # D-029 disclosure: the last payment is partial in every scenario
            # too, so each row states its own schedule rather than inviting
            # `remittance x duration`.
            "illustrative_schedule": illustrative_schedule(repayment_cap, scenario_remittance),
        })

    # Closure: revenue is permanent-zero from CLOSURE_SCENARIO_MONTH onward, so
    # collection stops after the months actually traded. Everything still owed
    # at that point is unrecovered — there is no later period to collect it in.
    # Reported as an amount and a share of the cap rather than a duration,
    # because "duration" has no meaning for a balance that is never reached.
    base_remittance = periodic_payment(to_vnd(monthly_revenue), share_rate)
    months_paid = CLOSURE_SCENARIO_MONTH - 1
    collected = min(to_vnd(base_remittance * months_paid), repayment_cap)
    unrecovered = to_vnd(repayment_cap - collected)
    out.append({
        "case": "closure",
        "label": f"Merchant closes at month {CLOSURE_SCENARIO_MONTH} (permanent)",
        "assumption": "assumption",
        "scenario_monthly_revenue": 0,
        "periodic_remittance": 0,
        # A cap that is never reached has no repayment duration. Null, not a
        # large number, so nothing downstream reads it as "repaid, eventually".
        "repayment_duration_months": None,
        "merchant_retained_revenue_pct": None,
        "months_collected_before_closure": months_paid,
        "amount_collected": collected,
        "amount_unrecovered": unrecovered,
        "share_of_cap_unrecovered": (round(unrecovered / repayment_cap, 4)
                                     if repayment_cap else None),
        "note": ("Revenue-contingent repayment reschedules a decline; it does not "
                 "survive a stop. Collection ends with trading, and the balance "
                 "outstanding at that moment is unrecovered."),
        "illustrative_schedule": None,
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
