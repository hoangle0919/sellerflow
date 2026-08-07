"""Simulation Lab — serves registered research artifacts to the UI.

RULES THIS MODULE ENFORCES, because the UI cannot be trusted to:

  * Every number originates in a committed, checksummed artifact under
    `research/results/`. Nothing here computes a research finding, and nothing
    is transcribed by hand.
  * Every artifact ships with its checksum and spec version, so a reader can
    verify what they are looking at.
  * Every conclusion carries a CLAIM CLASSIFICATION. "RBF's payment burden is
    constant" and "RBF extends duration in a downturn" are different kinds of
    statement and must not be displayed as though they were the same kind.
  * Contractual money is integer đồng via `money.py`. The frontend receives
    formatted values and performs no financial arithmetic.
  * RBF-G is absent from every public surface (D-018). It is computed by the
    engine but is a rejected design: its floor provably never activates.
  * The illustrative f = 1.20 cap and the equal-effective-cost f* = 1.0945 cap
    are separate arms with separate labels. Neither is "the" price of RBF.

WHY TWO BASELINES. `baseline_v2` prices every scenario at the illustrative
f = 1.20. `baseline_equalcost_v1` prices the same scenarios, same seeds, same
generator at f* = 1.0945 (D-031). Comparing seller burden at one price against
provider recovery at another would be meaningless, so both exist.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from money import to_vnd

RESEARCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "research", "results")

# ── claim taxonomy ──────────────────────────────────────────────────────────

CLAIM_TAXONOMY = {
    "mathematical_property": {
        "label": "Mathematical property",
        "meaning": "Holds for any revenue path, by proof. Independent of the "
                   "simulation, the parameters, and any distributional "
                   "assumption. See research/DERIVATIONS.md.",
        "strength": "strongest",
    },
    "simulation_result": {
        "label": "Simulation result",
        "meaning": "Measured on simulated revenue paths under the frozen "
                   "methodology. Describes the model, not observed sellers.",
        "strength": "conditional on the generative assumptions",
    },
    "sensitivity_result": {
        "label": "Sensitivity result",
        "meaning": "How an output moves when a parameter is swept. Shows what "
                   "the conclusion depends on, not that the parameter is right.",
        "strength": "conditional on the swept range",
    },
    "product_implication": {
        "label": "Product implication",
        "meaning": "A design consequence the author draws from the above. A "
                   "judgement, not a measurement.",
        "strength": "author's inference",
    },
    "open_real_world_question": {
        "label": "Open real-world question",
        "meaning": "Cannot be settled by this project. Requires observed seller "
                   "revenue and adjudicated repayment outcomes, which do not "
                   "exist here.",
        "strength": "unresolved",
    },
}

# ── scenario descriptions (prose, not research numbers) ─────────────────────

SCENARIOS: Dict[str, dict] = {
    "stable":            {"label": "Stable revenue",
                          "family": "baseline",
                          "description": "Flat seasonality, no growth, no shock. The reference case."},
    "seasonal":          {"label": "Moderate seasonality",
                          "family": "baseline",
                          "description": "Ordinary seasonal swing around a flat trend."},
    "seasonal_strong":   {"label": "Strong seasonality",
                          "family": "baseline",
                          "description": "Pronounced peaks and troughs — common for fashion and gift categories."},
    "growth":            {"label": "Growth",
                          "family": "favourable",
                          "description": "3% month-on-month growth with moderate seasonality."},
    "gradual_decline":   {"label": "Gradual decline",
                          "family": "stress",
                          "description": "Revenue steps down toward −40% over six months, then holds."},
    "sustained_decline": {"label": "Sustained decline",
                          "family": "stress",
                          "description": "An immediate, permanent drop to 60% of prior revenue."},
    "severe_downturn":   {"label": "Severe downturn",
                          "family": "stress",
                          "description": "−60% for six months, then a six-month recovery."},
    "disruption_1m":     {"label": "One-month disruption",
                          "family": "stress",
                          "description": "A single month at half revenue, then full recovery."},
    "platform_outage":   {"label": "Platform outage",
                          "family": "stress",
                          "description": "A single month at 30% of revenue — a marketplace suspension or outage."},
    "returns_spike":     {"label": "Returns spike",
                          "family": "stress",
                          "description": "Elevated returns reduce net sales without reducing gross orders."},
}

ARMS = [
    {"id": "FIX-A", "source": "baseline_v2", "arm": "FIX-A",
     "name": "Fixed payment — cost-matched",
     "kind": "fixed",
     "note": "Same principal, same total repayment and same term as the "
             "illustrative RBF contract on the reference path. Only the TIMING "
             "of payments differs, which is what isolates the comparison."},
    {"id": "FIX-B", "source": "baseline_v2", "arm": "FIX-B",
     "name": "Amortizing loan — 18% nominal",
     "kind": "fixed",
     "note": "A conventional 12-month amortizing loan at 18% nominal annual "
             "rate. Not cost-matched; it is the external price reference."},
    {"id": "RBF-EQ", "source": "baseline_equalcost_v1", "arm": "RBF",
     "name": "Revenue-based — equal effective cost (f* = 1.0945)",
     "kind": "rbf",
     "note": "The cap factor was calibrated so the effective cost matches the "
             "amortizing loan ON THE DETERMINISTIC REFERENCE PATH. The APR shown "
             "here is the mean across simulated paths, and it differs: repayment "
             "duration varies with revenue, and a longer duration lowers the "
             "annualised rate for the same total. 'Equal cost' names the "
             "calibration, not a guarantee on every path."},
    {"id": "RBF-ILL", "source": "baseline_v2", "arm": "RBF",
     "name": "Revenue-based — illustrative (f = 1.20)",
     "kind": "rbf",
     "note": "An ILLUSTRATIVE cap factor, not a recommended or market price. "
             "Its higher effective cost is a property of choosing 1.20, not of "
             "revenue-based repayment."},
]

_CACHE: Dict[str, dict] = {}


def _load(stem: str) -> Optional[dict]:
    if stem in _CACHE:
        return _CACHE[stem]
    path = os.path.join(RESEARCH, f"{stem}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        _CACHE[stem] = json.load(fh)
    return _CACHE[stem]


def _checksum(stem: str) -> Optional[str]:
    prov = _load(f"{stem}_provenance")
    return prov.get("canonical_sha256") if prov else None


def artifacts_available() -> bool:
    return _load("baseline_v2_canonical") is not None


def manifest() -> dict:
    """Artifact identity — what the reader is looking at, and how to verify it."""
    out = []
    for stem, role in (("baseline_v2", "Illustrative pricing, f = 1.20"),
                       ("baseline_equalcost_v1", "Equal effective cost, f* = 1.0945")):
        body = _load(f"{stem}_canonical")
        if not body:
            continue
        c = body.get("canonical", {})
        out.append({
            "artifact": f"{stem}_canonical.json",
            "role": role,
            "sha256": _checksum(stem),
            "spec_version": c.get("spec_version"),
            "schema_version": c.get("schema_version"),
            "generator_fingerprint": c.get("generator_fingerprint"),
            "scenario_config_hash": c.get("scenario_config_hash"),
            "n_paths": body.get("n_paths"),
            "base_seed": body.get("base_seed"),
            "determinism": c.get("determinism"),
        })
    val = _load("validation_v1")
    return {
        "artifacts": out,
        "pricing_reference": {
            "artifact": "validation_v1.json",
            "equal_cost": (val or {}).get("pricing", {}).get("equal_cost"),
            "benchmark_b_apr": (val or {}).get("pricing", {}).get("benchmark_b_apr"),
        },
        "claim_taxonomy": CLAIM_TAXONOMY,
        "integrity": {
            "data_basis": "SIMULATED. No observed seller revenue, repayment or "
                          "default outcome exists in this project.",
            "intervals": "Monte Carlo intervals over simulated paths. They "
                         "measure whether enough paths were run for a number to "
                         "be stable — NOT population uncertainty about real "
                         "sellers. Running more paths narrows them without "
                         "adding a single fact about the world.",
            "parameters": "No contract parameter is externally sourced. All are "
                          "illustrative or derived, with sensitivity analysis "
                          "rather than claimed calibration.",
            "underwriting_model": "The RF+LR ensemble is a secondary, explicitly "
                                  "UNVALIDATED component with no measured "
                                  "predictive validity. Its training benchmark "
                                  "was withdrawn as circular. It plays no part "
                                  "in anything on this page.",
            "not_advice": "A research prototype. Not a lending service, a credit "
                          "offer, or financial advice.",
        },
    }


def scenarios() -> List[dict]:
    body = _load("baseline_v2_canonical")
    present = set((body or {}).get("scenarios", {}))
    return [{"key": k, **v, "available": k in present}
            for k, v in SCENARIOS.items() if k in present]


def _fmt_money(x) -> dict:
    v = to_vnd(x)
    return {"vnd": v, "display": f"{v:,} ₫"}


def _arm_block(spec: dict, scenario: str) -> Optional[dict]:
    body = _load(f"{spec['source']}_canonical")
    if not body:
        return None
    sc = body.get("scenarios", {}).get(scenario)
    if not sc or spec["arm"] not in sc:
        return None
    a = sc[spec["arm"]]
    terms = body.get("terms", {})
    total = a.get("total_repaid_mean")

    # FIX-B is a conventional amortizing loan. It has no cap factor and no
    # repayment cap — its total is whatever the annuity schedule sums to. Showing
    # it the RBF contract's ×1.20 cap would attribute economics it does not have,
    # and would sit visibly beside its own smaller total.
    has_cap = spec["id"] != "FIX-B"
    cap = terms.get("cap") if has_cap else None

    dur = a.get("duration_mean")
    return {
        "id": spec["id"],
        "name": spec["name"],
        "kind": spec["kind"],
        "note": spec["note"],
        "source_artifact": f"{spec['source']}_canonical.json",
        "source_sha256": _checksum(spec["source"]),
        "cap_factor": terms.get("f") if has_cap else None,
        "principal": _fmt_money(terms.get("A", 0)),
        "contractual_cap": _fmt_money(cap) if cap is not None else None,
        "cap_basis": ("Advance × cap factor" if has_cap
                      else "No cap — amortizing schedule; the total is the sum of "
                           "the scheduled instalments."),
        "total_repaid_mean": _fmt_money(total or 0),
        "effective_apr": a.get("apr_mean"),
        "burden": {
            "mean": a.get("burden_mean"),
            "p90": a.get("burden_p90"),
            "p95": a.get("burden_p95"),
            "max": a.get("burden_max"),
        },
        "high_burden_months": a.get("n_high_burden", {}),
        "duration_months_mean": dur,
        "duration_sd": a.get("duration_sd"),
        "censored_rate": a.get("duration_censored_rate"),
        "incomplete_recovery_rate": a.get("incomplete_recovery_rate"),
        "recovery_ratio": a.get("recovery_ratio", {}),
    }


def comparison(scenario: str) -> Optional[dict]:
    if scenario not in SCENARIOS:
        return None
    arms = [b for b in (_arm_block(s, scenario) for s in ARMS) if b]
    if not arms:
        return None
    return {
        "scenario": {"key": scenario, **SCENARIOS[scenario]},
        "arms": arms,
        "metric_definitions": METRIC_DEFINITIONS,
        "findings": _findings(scenario, arms),
        "assumptions": ASSUMPTIONS,
        "caveats": CAVEATS,
    }


METRIC_DEFINITIONS = {
    "burden": {
        "label": "Payment burden",
        "definition": "Payment ÷ revenue in a given month. Computed from revenue "
                      "alone; undefined in months with zero revenue.",
        "why": "It is what the seller actually feels: the share of this month's "
               "takings that leaves as a payment.",
    },
    "high_burden_months": {
        "label": "High-payment-burden months",
        "definition": "Count of months where payment burden exceeds a threshold "
                      "(10%, 15%, 20%, 25%).",
        "why": "Averages hide the bad months. This counts them.",
        "caveat": "For RBF this is constant BY CONSTRUCTION — the payment is a "
                  "fixed share of revenue, so its burden cannot rise. The "
                  "informative side is the fixed arm, where burden climbs as "
                  "revenue falls. This metric does not test whether RBF "
                  "stabilises burden; that is definitional, not a finding.",
    },
    "duration_months_mean": {
        "label": "Repayment duration",
        "definition": "Mean months until cumulative payments reach the "
                      "contractual cap, across simulated paths.",
        "why": "The provider's cost of flexibility: revenue-based repayment "
               "extends the term when revenue falls instead of defaulting.",
    },
    "recovery_ratio": {
        "label": "Provider recovery",
        "definition": "Share of the contractual cap recovered by month 12, 18 "
                      "and 24.",
        "why": "The other side of the trade-off. Slower recovery is a real cost "
               "to the financier even when the full amount is eventually repaid.",
    },
    "incomplete_recovery_rate": {
        "label": "Incomplete recovery",
        "definition": "Share of simulated paths that do not reach the cap within "
                      "the 24-month observation window.",
        "why": "Censoring, not default.",
        "caveat": "This is NOT a default rate. No borrower behaviour is modelled "
                  "and no default is simulated.",
    },
    "effective_apr": {
        "label": "Effective APR",
        "definition": "Annualised internal rate of return of the payment stream "
                      "against the principal.",
        "why": "Puts a revenue share and a fixed instalment on one axis.",
    },
}

ASSUMPTIONS = [
    "Revenue paths are generated, not observed. Parameters are illustrative.",
    "Remittance is collected on net sales — gross merchandise value after returns.",
    "The seller draws the advance at month 1 and the observation window is 24 months.",
    "Both fixed arms are modelled as paid in full and on time. No borrower "
    "behaviour, hardship, renegotiation or default is simulated on any arm.",
    "The cost-matched fixed benchmark is computed once on the deterministic "
    "reference path and held constant across every path in a scenario.",
]

CAVEATS = [
    {"text": "Every figure here is simulation output under stated assumptions. "
             "No observed seller revenue, repayment or default outcome exists in "
             "this project.",
     "classification": "open_real_world_question"},
    {"text": "The fixed arms are modelled as always repaid. Real fixed-payment "
             "lending carries default risk that this comparison does not model, "
             "so the fixed arm's recovery here is an upper bound, not a "
             "prediction.",
     "classification": "open_real_world_question"},
    {"text": "Whether revenue-based repayment helps or harms a given provider "
             "depends on the revenue path. It is not universally slower or "
             "faster to recover — the scenarios differ, and both directions "
             "appear in this library.",
     "classification": "simulation_result"},
    {"text": "Intervals reported in the underlying artifacts are Monte Carlo "
             "intervals over simulated paths. They are not population "
             "confidence intervals and say nothing about real sellers.",
     "classification": "open_real_world_question"},
    {"text": "The equal-effective-cost cap factor was calibrated on the "
             "deterministic reference path. Across simulated paths the realised "
             "APR differs from that calibration, because duration varies with "
             "revenue and a longer duration lowers the annualised rate for the "
             "same total repayment. The label describes how the price was "
             "chosen, not an outcome guaranteed on every path.",
     "classification": "sensitivity_result"},
]


def _findings(scenario: str, arms: List[dict]) -> List[dict]:
    """Conclusions for this scenario, each carrying its claim classification.

    Comparative statements are derived from the artifact values just returned —
    the same numbers the UI displays — so a finding cannot drift from the chart
    beside it. Nothing here is a hand-typed research number.
    """
    by_id = {a["id"]: a for a in arms}
    out: List[dict] = [
        {"classification": "mathematical_property",
         "text": "A revenue-share payment is a fixed proportion of revenue, so "
                 "its payment burden cannot rise when revenue falls. This holds "
                 "for every revenue path, by construction — it is a definition, "
                 "not a measurement.",
         "source": "research/DERIVATIONS.md"},
        {"classification": "mathematical_property",
         "text": "A fixed instalment does not adjust, so its burden rises "
                 "exactly in proportion as revenue falls. Repayment is extended "
                 "under a revenue share instead of missed — the trade is timing, "
                 "not forgiveness.",
         "source": "research/DERIVATIONS.md"},
    ]

    fa, eq, ill = by_id.get("FIX-A"), by_id.get("RBF-EQ"), by_id.get("RBF-ILL")

    if fa and ill:
        out.append({
            "classification": "simulation_result",
            "text": (f"In this scenario the cost-matched fixed arm reaches a peak "
                     f"payment burden of {fa['burden']['max']:.1%}, against "
                     f"{ill['burden']['max']:.1%} for the revenue-based arm."),
            "source": "baseline_v2_canonical.json"})
        out.append({
            "classification": "simulation_result",
            "text": (f"Provider recovery by month 12: {fa['recovery_ratio'].get('12', 0):.1%} "
                     f"fixed against {ill['recovery_ratio'].get('12', 0):.1%} "
                     f"revenue-based. Mean duration {fa['duration_months_mean']:.1f} "
                     f"against {ill['duration_months_mean']:.1f} months."),
            "source": "baseline_v2_canonical.json"})

    if eq and ill:
        out.append({
            "classification": "sensitivity_result",
            "text": (f"Price and structure are separable. The same revenue-share "
                     f"structure priced at f* = 1.0945 gives an effective APR of "
                     f"{eq['effective_apr']:.2%}, against {ill['effective_apr']:.2%} "
                     f"at the illustrative f = 1.20. The higher figure is a "
                     f"property of the chosen cap factor, not of revenue-based "
                     f"repayment."),
            "source": "baseline_equalcost_v1_canonical.json + validation_v1.json"})

    out.append({
        "classification": "product_implication",
        "text": "If a financier wants payment burden to stay flat through a "
                "downturn, a revenue share achieves it — and the price of that "
                "is a longer, more variable recovery period. Which side of that "
                "trade is worth taking is a commercial judgement this study does "
                "not make.",
        "source": "author"})
    out.append({
        "classification": "open_real_world_question",
        "text": "Whether real Vietnamese sellers would repay on these paths, and "
                "at what default rate, cannot be answered here. It needs "
                "observed revenue and adjudicated repayment outcomes.",
        "source": "research/CORRECTED_CLAIMS.md"})
    return out
