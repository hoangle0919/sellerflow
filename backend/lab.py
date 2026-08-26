"""Simulation Lab — serves registered research artifacts to the UI.

RULES THIS MODULE ENFORCES, because the UI cannot be trusted to:

  * Every number originates in a committed, checksummed artifact under
    `research/results/`. Nothing here computes a research finding, and nothing
    is transcribed by hand.
  * Every artifact ships with its checksum and spec version.
  * Every conclusion carries a CLAIM CLASSIFICATION. A proof and a simulation
    output are different kinds of evidence and must not be displayed alike.
  * Every rate carries its BASIS — reference-path or mean-across-simulated-paths.
    They are different quantities and the design audit found the page conflating
    them (D-033).
  * Every recovery figure carries its DENOMINATOR. The amortizing loan has no
    contractual cap; its denominator is scheduled total repayment.
  * Contractual money is integer đồng via `money.py`. The frontend receives
    formatted values and performs no financial arithmetic.
  * RBF-G is absent from every public surface (D-018).
  * Colour is CATEGORICAL, never valenced. The API emits a palette key; it does
    not emit "good" or "bad".

FOUR ARTIFACTS, TWO PRICE TRACKS. Ten ordinary scenarios and three closure
scenarios, each priced at the illustrative f = 1.20 and at the reference-path
cost-matched f* = 1.0945. A scenario is resolved against whichever artifact in
its track contains it.
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
                   "methodology, FOR THE SELECTED SCENARIO. Describes the model, "
                   "not observed sellers, and does not generalise to other "
                   "scenarios.",
        "strength": "conditional on the scenario and the generative assumptions",
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

# ── glossary (D-033: specialist labels were unexplained in place) ───────────

GLOSSARY = {
    "cap factor": "The multiple of the advance that the seller repays in total. "
                  "A cap factor of 1.20 on a 100M advance means 120M repaid.",
    "contractual cap": "The total amount repayable — advance × cap factor. "
                       "Collection stops when it is reached.",
    "remittance": "The share of each month's revenue that goes to the financier. "
                  "Fixed as a percentage; the amount moves with revenue.",
    "effective APR": "The annualised internal rate of return of the payment "
                     "stream against the advance. It puts a revenue share and a "
                     "fixed instalment on one axis.",
    "payment burden": "Payment ÷ GMV in a given month — the share of that "
                      "month's gross takings that leaves as a payment. The "
                      "contract charges its share on NET sales, so this equals "
                      "r·(1 − return rate) and varies when returns vary.",
    "90th percentile": "The value exceeded in only 10% of active months. It "
                       "describes a bad month, not a typical one.",
    "Monte Carlo interval": "A range showing whether enough simulated paths were "
                            "run for a number to be stable. It is NOT a "
                            "confidence interval and says nothing about real "
                            "sellers.",
    "canonical artifact": "A committed, checksummed result file. Identical code, "
                          "configuration and seeds reproduce it byte-for-byte "
                          "within a fixed runtime, and numerically at published "
                          "precision on every platform tested — so any figure "
                          "here can be traced to a verifiable file.",
    "reference path": "A flat, shock-free revenue path used once to price the "
                      "fixed benchmark. Contracts are priced at origination, so "
                      "a later shock cannot retro-price them.",
}

# ── scenarios (prose, not research numbers) ─────────────────────────────────

SCENARIOS: Dict[str, dict] = {
    "stable":            {"label": "Stable revenue", "family": "baseline", "order": 1,
                          "description": "Flat seasonality, no growth, no shock. The reference case."},
    "seasonal":          {"label": "Moderate seasonality", "family": "baseline", "order": 2,
                          "description": "Ordinary seasonal swing around a flat trend."},
    "seasonal_strong":   {"label": "Strong seasonality", "family": "baseline", "order": 3,
                          "description": "Pronounced peaks and troughs. The shape is a "
                                         "specified input, not an observed category "
                                         "pattern; no category data informs it."},
    "growth":            {"label": "Growth", "family": "favourable", "order": 4,
                          "description": "3% month-on-month growth with moderate seasonality."},
    "gradual_decline":   {"label": "Gradual decline", "family": "stress", "order": 5,
                          "description": "Revenue steps down toward −40% over six months, then holds."},
    "sustained_decline": {"label": "Sustained decline", "family": "stress", "order": 6,
                          "description": "An immediate, permanent drop to 60% of prior revenue."},
    "severe_downturn":   {"label": "Severe downturn", "family": "stress", "order": 7,
                          "description": "−60% for six months, then a six-month recovery."},
    "disruption_1m":     {"label": "One-month disruption", "family": "stress", "order": 8,
                          "description": "A single month at half revenue, then full recovery."},
    "platform_outage":   {"label": "Platform outage", "family": "stress", "order": 9,
                          "description": "A single month at 30% of revenue — a marketplace suspension."},
    "returns_spike":     {"label": "Returns spike", "family": "stress", "order": 10,
                          "description": "Elevated returns reduce net sales without reducing gross orders."},
    "closure_m7":        {"label": "Closure, month 7", "family": "closure", "order": 11,
                          "description": "The business closes permanently in month 7. Revenue is zero "
                                         "from then on and never recovers."},
    "closure_m13":       {"label": "Closure, month 13", "family": "closure", "order": 12,
                          "description": "Permanent closure in month 13, after most of the term has "
                                         "already been repaid."},
    "temp_closure":      {"label": "Temporary closure", "family": "closure", "order": 13,
                          "description": "Three months at zero revenue, then partial recovery to 50%."},
}

#: A scenario is looked up in its track, first artifact that has it.
TRACKS = {
    "illustrative": ["baseline_v3", "baseline_closure_v2"],
    "cost_matched": ["baseline_equalcost_v2", "baseline_closure_equalcost_v2"],
}

ARMS = [
    {"id": "FIX-A", "track": "illustrative", "arm": "FIX-A", "palette": "fixed-a",
     "name": "Fixed payment — cost-matched",
     "short": "Fixed payment",
     "chart_label": "Fixed payment",
     "kind": "fixed",
     "note": "Same principal, same total repayment and same term as the "
             "illustrative revenue-based contract on the reference path. Only "
             "the TIMING of payments differs, which is what isolates the "
             "comparison."},
    {"id": "FIX-B", "track": "illustrative", "arm": "FIX-B", "palette": "fixed-b",
     "name": "Amortizing loan — 18% nominal",
     "short": "Amortizing loan",
     "chart_label": "Amortizing loan",
     "kind": "fixed",
     "note": "An illustrative 12-month amortizing loan at 18% nominal annual "
             "rate. The 18% is an assumption chosen for this study — not a "
             "market rate, and not observed or externally sourced anywhere in "
             "this project. Not cost-matched; it is the external price "
             "reference."},
    {"id": "RBF-EQ", "track": "cost_matched", "arm": "RBF", "palette": "rbf-ref",
     "name": "Reference-path cost-matched RBF",
     "short": "Revenue-based, cost-matched",
     "chart_label": "Revenue-based 1.0945×",
     "kind": "rbf",
     "note": "The cap factor was chosen so this contract's cost matches the "
             "amortizing loan ON THE REFERENCE PATH — a flat, shock-free path "
             "used once at pricing time. On simulated paths the realised rate "
             "differs, because duration moves with revenue. The name describes "
             "how the price was set, not an outcome guaranteed on any path."},
    {"id": "RBF-ILL", "track": "illustrative", "arm": "RBF", "palette": "rbf-ill",
     "name": "Illustrative RBF (cap factor 1.20)",
     "short": "Revenue-based, illustrative",
     "chart_label": "Revenue-based 1.20×",
     "kind": "rbf",
     "note": "An ILLUSTRATIVE cap factor, not a recommended or market price. "
             "Its higher cost is a property of choosing 1.20, not of "
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


def _resolve(track: str, scenario: str):
    """First artifact in the track containing this scenario."""
    for stem in TRACKS[track]:
        body = _load(f"{stem}_canonical")
        if body and scenario in body.get("scenarios", {}):
            return stem, body
    return None, None


def artifacts_available() -> bool:
    return _load("baseline_v3_canonical") is not None


def manifest() -> dict:
    roles = {
        "baseline_v3": "Illustrative pricing (cap factor 1.20) — ten scenarios",
        "baseline_equalcost_v2": "Reference-path cost-matched pricing — ten scenarios",
        "baseline_closure_v2": "Illustrative pricing — closure / zero-revenue",
        "baseline_closure_equalcost_v2": "Reference-path cost-matched — closure / zero-revenue",
    }
    out = []
    for stem, role in roles.items():
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
            "n_paths": body.get("n_paths"),
            "base_seed": body.get("base_seed"),
        })
    val = _load("validation_v2")
    return {
        "artifacts": out,
        "pricing_reference": {
            # Names the artifact actually loaded. This previously said the
            # superseded validation_v1.json
            # while _load() read validation_v2 -- the page reported provenance
            # for a file it was not using.
            "artifact": "validation_v2_canonical.json",
            "sha256": _checksum("validation_v2"),
            "spec_version": ((val or {}).get("canonical") or {}).get("spec_version"),
            "equal_cost": (val or {}).get("pricing", {}).get("equal_cost"),
            "benchmark_b_apr": (val or {}).get("pricing", {}).get("benchmark_b_apr"),
            "note": "The cost-matched cap factor was solved on the reference "
                    "path so that its effective rate equals the amortizing "
                    "loan's. Rates realised on simulated paths differ.",
        },
        "claim_taxonomy": CLAIM_TAXONOMY,
        "glossary": GLOSSARY,
        "integrity": {
            "data_basis": "SIMULATED. No observed seller revenue, repayment or "
                          "default outcome exists in this project.",
            "intervals": "Monte Carlo intervals over simulated paths. They "
                         "measure whether enough paths were run for a number to "
                         "be stable — NOT population uncertainty about real "
                         "sellers.",
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
    out = []
    for k, v in SCENARIOS.items():
        stem, _ = _resolve("illustrative", k)
        if stem:
            out.append({"key": k, **v, "available": True})
    return sorted(out, key=lambda s: s["order"])


def _fmt_money(x) -> dict:
    v = to_vnd(x)
    return {"vnd": v, "display": f"{v:,} ₫"}


def _censoring(a: dict) -> dict:
    """Duration and rate have DIFFERENT denominators. Report both separately.

    This function used to derive one qualifier from `incomplete_recovery_rate`
    and attach it to the duration *and* the rate. That was wrong, and A-9
    corrected it:

      * `duration_mean` averages paths that COMPLETED within the horizon.
      * `apr_mean` averages paths where an IRR EXISTS, which is a different and
        usually larger set. A path can fail to reach the contractual target and
        still have a perfectly well-defined return on the payments it made.

    At `closure_m13`, f = 1.20: 119 of 500 paths complete, but all 500 have a
    defined IRR. Labelling the rate "among completed paths" described 500 paths
    as 119 and understated the completed-path figure by about nine points.

    The artifacts now report `completed_rate` and `apr_defined_rate` explicitly,
    so neither denominator is inferred here. Older artifacts lack those fields;
    the fallbacks keep the Lab working against them without pretending to a
    precision they cannot supply.
    """
    incomplete = a.get("incomplete_recovery_rate") or 0.0
    completed = a.get("completed_rate")
    if completed is None:                       # pre-A-9 artifact
        completed = max(0.0, 1.0 - incomplete)
    apr_defined = a.get("apr_defined_rate")
    if apr_defined is None:                     # pre-A-9 artifact
        apr_defined = 1.0 if a.get("apr_mean") is not None else 0.0

    # ---- duration: conditioned on completion ------------------------------
    if 0.0 < completed < 1.0:
        duration_label = "Mean duration among completed paths"
        duration_basis = (
            f"Averaged over the {completed:.1%} of simulated paths that reached "
            f"the repayment target within 24 months. The remaining "
            f"{1.0 - completed:.1%} did not and are excluded from this figure, "
            f"not counted as long.")
    elif completed >= 1.0:
        duration_label = "Mean duration"
        duration_basis = ("Mean across simulated paths for this scenario. Every "
                          "path reached the repayment target.")
    else:
        duration_label = "Mean duration"
        duration_basis = "No path reached the repayment target within 24 months."

    # ---- rate: conditioned on IRR existence, NOT on completion ------------
    if apr_defined <= 0.0:
        apr_label = "Effective APR"
        apr_basis = ("No payment was made on any simulated path, so the rate "
                     "equation has no root and no APR is defined.")
    elif completed >= 1.0:
        apr_label = "Mean simulated APR"
        apr_basis = ("Mean across simulated paths for this scenario. Every path "
                     "has a defined rate and every path reached the repayment "
                     "target.")
    else:
        apr_label = "Mean simulated APR among rate-defined paths"
        apr_basis = (
            f"Averaged over the {apr_defined:.1%} of simulated paths with a "
            f"defined internal rate of return — a different set from the "
            f"{completed:.1%} that reached the repayment target. A path can "
            f"miss the target and still have a rate on the payments it made. "
            f"Where the target is not reached this is the rate over the "
            f"observed 24-month window, not a final lifetime return; read it "
            f"beside the incomplete-recovery figure.")

    return {
        # `censored` is keyed to duration, which is what it always meant -- but
        # it previously read `0 < completed < 1`, so a scenario where NOTHING
        # completed reported `censored: False`. That is the most censored case
        # there is, and the flag gates whether the page shows its basis text at
        # all: at closure_m7 the reader saw a rate and a blank duration with no
        # explanation of either. Any incompleteness is now censoring, and the
        # total case is flagged separately rather than folded into "not
        # censored".
        "censored": completed < 1.0,
        "fully_censored": completed == 0.0,
        "completed_share": completed,
        "apr_defined_share": apr_defined,
        "denominators_differ": abs(apr_defined - completed) > 1e-12,
        "apr_label": apr_label,
        "duration_label": duration_label,
        "apr_basis": apr_basis,
        "duration_basis": duration_basis,
    }


def _arm_block(spec: dict, scenario: str) -> Optional[dict]:
    stem, body = _resolve(spec["track"], scenario)
    if not body:
        return None
    sc = body["scenarios"].get(scenario)
    if not sc or spec["arm"] not in sc:
        return None
    a = sc[spec["arm"]]
    terms = body.get("terms", {})
    total = a.get("total_repaid_mean")

    # The amortizing loan is an annuity: no cap factor, no contractual cap. Its
    # recovery denominator is the scheduled total, not a cap. Attributing the
    # RBF contract's cap to it would show a cap larger than its own total.
    has_cap = spec["id"] != "FIX-B"
    cap = terms.get("cap") if has_cap else None

    # Both arms have a repayment target; they differ in what defines it. A
    # revenue-based or cost-matched contract stops at a contractual cap. An
    # annuity has no cap at all — its target is simply what the schedule sums
    # to. Rendering the annuity as "no cap" said what it lacks instead of what
    # it owes, which is not a number a reader can use.
    target = {
        "label": "Contractual cap" if has_cap else "Scheduled total repayment",
        "amount": _fmt_money(cap if has_cap else (total or 0)),
        "basis": ("Advance × cap factor. Collection stops here."
                  if has_cap else
                  "Sum of the 12 scheduled instalments. This loan has no cap; "
                  "the schedule itself defines the total."),
    }

    return {
        "id": spec["id"],
        "name": spec["name"],
        "short": spec["short"],
        "chart_label": spec["chart_label"],
        "kind": spec["kind"],
        "palette": spec["palette"],
        "note": spec["note"],
        "source_artifact": f"{stem}_canonical.json",
        "source_sha256": _checksum(stem),
        "cap_factor": terms.get("f") if has_cap else None,
        "principal": _fmt_money(terms.get("A", 0)),
        "repayment_target": target,
        "contractual_cap": _fmt_money(cap) if cap is not None else None,
        "cap_basis": target["basis"],
        "total_repaid_mean": _fmt_money(total or 0),
        "effective_apr": a.get("apr_mean"),
        # A-9: undefined means the rate equation has no root -- i.e. no payment
        # was made at all. It does NOT mean the contract failed to complete;
        # closure_m7 misses the target on every path and still returns roughly
        # -86.5%, which is a result, not an absence.
        "apr_undefined_reason": (None if a.get("apr_mean") is not None else
                                 "no payment was made, so the rate equation "
                                 "has no root"),
        **_censoring(a),
        "burden": {
            "mean": a.get("burden_mean"),
            "p90": a.get("burden_p90"),
            "p95": a.get("burden_p95"),
            "max": a.get("burden_max"),
        },
        "high_burden_months": a.get("n_high_burden", {}),
        "duration_months_mean": a.get("duration_mean"),
        "duration_sd": a.get("duration_sd"),
        "censored_rate": a.get("duration_censored_rate"),
        "incomplete_recovery_rate": a.get("incomplete_recovery_rate"),
        "recovery_ratio": a.get("recovery_ratio", {}),
        "recovery_denominator": ("Contractual cap (advance × cap factor)" if has_cap
                                 else "Scheduled total repayment (this loan has no cap)"),
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
        "summary": _summary(scenario, arms),
    }


def underreporting() -> Optional[dict]:
    """The omega sweep. Deliberately NOT presented as a scenario.

    It is a sensitivity sweep run on one revenue shape: the provider observes
    only ω of true revenue. Listing it beside 'severe downturn' would imply it
    is a revenue path, which it is not.
    """
    body = _load("baseline_v3_canonical")
    if not body or "underreporting" not in body:
        return None
    rows = []
    for omega in sorted(body["underreporting"], key=float):
        a = body["underreporting"][omega]
        rows.append({
            "omega": float(omega),
            "observed_share": f"{float(omega):.0%}",
            "duration_months_mean": a.get("duration_mean"),
            "incomplete_recovery_rate": a.get("incomplete_recovery_rate"),
            "burden_mean": a.get("burden_mean"),
            "effective_apr": a.get("apr_mean"),
            "total_repaid_mean": _fmt_money(a.get("total_repaid_mean") or 0),
        })
    # Derived from `rows`, never typed. A hard-coded "12.9 → 18.7" would go
    # stale silently the day the artifact changes — the exact failure mode the
    # literal scanner exists to catch on the HTML side.
    if not rows:                           # artifact present but sweep empty
        return None
    full, least = rows[-1], rows[0]        # rows ascend by ω: [0]=lowest
    all_complete = all(not (r["incomplete_recovery_rate"] or 0) for r in rows)
    if all_complete:
        observed = (
            f"In this sweep every path still reached the cap inside the "
            f"24-month window, so the total stayed at the cap and only the "
            f"duration moved: {full['duration_months_mean']:.1f} → "
            f"{least['duration_months_mean']:.1f} months as ω falls "
            f"{full['omega']:.0%} → {least['omega']:.0%}. That is this "
            f"sweep's result, not a general guarantee.")
    else:
        observed = (
            "In this sweep some paths did NOT reach the cap inside the "
            "24-month window, so the total is not invariant across all of "
            "them — read the incomplete-recovery column.")

    return {
        "rows": rows,
        "source_artifact": "baseline_v3_canonical.json",
        "source_sha256": _checksum("baseline_v3"),
        "why_not_a_scenario": "This is a parameter sweep, not a revenue path. ω "
                              "is the share of true revenue the provider "
                              "observes; the underlying revenue shape is held "
                              "fixed. It is shown separately so it is not read "
                              "as one of the scenarios.",
        # A list, and split by claim class on purpose. The invariance argument
        # is a property of the contract; the duration numbers are an output of
        # one sweep. Carrying both under a single "mathematical_property" label
        # would promote a simulation result to a theorem.
        "findings": [
            {
                "classification": "mathematical_property",
                "text": "Under-reporting does not change what is owed. It "
                        "rescales the UNCAPPED remittances — the final "
                        "payment is clipped to whatever is left, so it does "
                        "not scale with \u03c9 — and raises the cumulative "
                        "sales needed to reach the cap. Invariance of the "
                        "total is conditional on the cap actually being "
                        "reached: under-reporting severe enough to push the "
                        "contract past the horizon leaves the cap unreached "
                        "and the total short.",
                "source": "research/DERIVATIONS.md",
            },
            {
                "classification": "simulation_result",
                "text": observed,
                "source": "research/results/baseline_v3_canonical.json",
            },
        ],
    }


METRIC_DEFINITIONS = {
    "burden": {
        "label": "Payment burden",
        "definition": "Payment ÷ GMV in a given month — note the denominator is "
                      "GMV while remittance is charged on net sales, so this "
                      "is r·(1 − return rate), not r. Computed from revenue "
                      "alone; undefined in months with zero revenue.",
        "why": "It is the share of this month's takings that leaves as a payment.",
        "caveat": "Burden is measured against REVENUE, not against what the "
                  "seller has left. Margins, operating costs, reserves and other "
                  "debts are not modelled, so a lower burden here does not "
                  "establish that a contract is affordable.",
    },
    "high_burden_months": {
        "label": "Months above a burden threshold",
        "definition": "Count of months where payment burden exceeds 10%, 15%, "
                      "20% or 25%, out of a 24-month window.",
        "why": "Averages hide bad months. This counts them.",
        "caveat": "These thresholds are ILLUSTRATIVE reporting bands chosen for "
                  "this study. They are not validated hardship cutoffs and no "
                  "claim is made that crossing one causes distress. For a "
                  "revenue share the count is constant in these scenarios, but "
                  "NOT by construction: the remittance is a fixed share of net "
                  "sales while this count is measured against payment ÷ GMV, so "
                  "it can move when the return rate moves. It is constant only "
                  "while the net-sales/GMV ratio holds fixed. The informative "
                  "side is the fixed arm.",
    },
    "duration_months_mean": {
        "label": "Repayment duration",
        "definition": "Mean months until cumulative payments reach the "
                      "repayment target — computed ONLY over paths that reached "
                      "it within the 24-month window. Paths that did not are "
                      "excluded from this mean and reported separately as "
                      "incomplete recovery.",
        "why": "Revenue-based repayment extends the term when revenue falls, "
               "rather than holding the payment fixed. In the scenarios where "
               "the term extends, that extension is the provider's cost. "
               "Extension is NOT the same as preventing default: where revenue "
               "stops PERMANENTLY BEFORE COMPLETION while a contractual "
               "balance remains, no further payment occurs and the cap is "
               "never reached. A temporary zero-revenue spell is a different "
               "case and usually still completes -- temp_closure leaves 2.0% "
               "of paths incomplete at f = 1.20 and none at f*. Read this "
               "beside the incomplete-recovery rate.",
        "caveat": "Where any path fails to complete, this is a SURVIVOR "
                  "statistic. It describes the contracts that finished, not the "
                  "portfolio. A scenario with a short mean duration and a high "
                  "incomplete-recovery rate is not a fast contract — it is one "
                  "where the slow paths were dropped rather than counted.",
    },
    "recovery_ratio": {
        "label": "Provider recovery",
        "definition": "Share of the arm's own repayment target recovered by "
                      "month 12, 18 and 24. For the revenue-based and "
                      "cost-matched fixed arms the denominator is the "
                      "contractual cap; for the amortizing loan, which has no "
                      "cap, it is scheduled total repayment.",
        "why": "The other side of the trade-off. Where recovery is slower it is "
               "a real cost to the financier even when the full amount is "
               "eventually repaid — but the direction is not universal. "
               "Revenue-contingent recovery may lead or lag the cost-matched "
               "fixed arm depending on the realised path (P4), and both occur "
               "in the registered scenarios. Read the direction per scenario.",
        "caveat": "Denominators differ by arm, so read each arm against its own "
                  "target rather than comparing absolute amounts recovered.",
    },
    "incomplete_recovery_rate": {
        "label": "Incomplete recovery",
        "definition": "Share of simulated paths that do not reach the repayment "
                      "target within the 24-month observation window.",
        "why": "Censoring, not default.",
        "caveat": "This is NOT a default rate. No borrower behaviour and no "
                  "default is simulated on any arm.",
    },
    "effective_apr": {
        "label": "Effective APR",
        "definition": "Annualised internal rate of return of the payment stream "
                      "against the advance, averaged ONLY over paths where a "
                      "rate exists. A path that never repays has no internal "
                      "rate of return and is excluded.",
        "why": "Puts a revenue share and a fixed instalment on one axis.",
        "caveat": "Two conditions apply. This is the MEAN ACROSS SIMULATED "
                  "PATHS for the selected scenario, not the reference-path rate "
                  "the cost-matched contract was priced on. And where any path "
                  "fails to complete it is a SURVIVOR statistic — the "
                  "non-completing paths are absent from it, so it understates "
                  "the cost of the scenario to the provider rather than "
                  "summarising it. Those paths are not 'unprofitable' — "
                  "profitability is computed nowhere in this project; they "
                  "simply did not reach the cap inside the horizon.",
    },
}

ASSUMPTIONS = [
    "Revenue paths are generated, not observed. Parameters are illustrative.",
    "Remittance is collected on net sales — gross merchandise value after returns.",
    "The seller draws the advance at month 1 and the observation window is 24 months.",
    "Both fixed arms are modelled as paid in full and on time. No borrower "
    "behaviour, hardship, renegotiation or default is simulated on any arm.",
    "The cost-matched fixed benchmark is priced once on a flat, shock-free "
    "reference path and held constant across every path in a scenario — a "
    "contract cannot be retro-priced by a shock that happens later.",
]

CAVEATS = [
    {"text": "Every figure here is simulation output under stated assumptions. "
             "No observed seller revenue, repayment or default outcome exists in "
             "this project.",
     "classification": "open_real_world_question"},
    {"text": "The fixed arms are modelled as paid in full and on time in every "
             "month of the schedule. The fixed arm is therefore an OPTIMISTIC "
             "SCHEDULED-RECOVERY BENCHMARK: it shows what the schedule would "
             "deliver under that assumption. It is not an upper bound derived "
             "from anything measured here, and this project makes no claim "
             "about how often real fixed-payment borrowers miss payments.",
     "classification": "open_real_world_question"},
    {"text": "Whether revenue-based repayment recovers faster or slower depends "
             "on the revenue path, and both directions appear in this scenario "
             "library. Nothing here supports a universal claim in either "
             "direction.",
     "classification": "simulation_result"},
    {"text": "Intervals in the underlying artifacts are Monte Carlo intervals "
             "over simulated paths. They are not population confidence intervals "
             "and say nothing about real sellers.",
     "classification": "open_real_world_question"},
    {"text": "The cost-matched cap factor was solved on the reference path. "
             "Across simulated paths the realised rate differs, because duration "
             "varies with revenue and a longer duration lowers the annualised "
             "rate for the same total. The label describes how the price was "
             "chosen, not an outcome guaranteed on any path.",
     "classification": "sensitivity_result"},
    {"text": "Mean duration and mean rate are computed only over paths that "
             "reached the repayment target. Where recovery is incomplete they "
             "describe the contracts that finished and exclude those that did "
             "not, so they must not be read as portfolio averages.",
     "classification": "simulation_result"},
    {"text": "Payment burden is measured against revenue, not against what the "
             "seller retains. Margins, operating costs, reserves and other debts "
             "are outside the model, so a lower burden is not by itself evidence "
             "that a contract is affordable.",
     "classification": "open_real_world_question"},
]


def _summary(scenario: str, arms: List[dict]) -> dict:
    """A compact headline for the top of the page, derived from this scenario's
    own values so it cannot drift from the charts below it."""
    by = {a["id"]: a for a in arms}
    fa, ill = by.get("FIX-A"), by.get("RBF-ILL")
    if not (fa and ill):
        return {}
    faster = "the fixed arm" if fa["recovery_ratio"].get("12", 0) >= ill["recovery_ratio"].get("12", 0) \
        else "the revenue-based arm"
    _ = None
    return {
        "scenario_label": SCENARIOS[scenario]["label"],
        "peak_burden_fixed": fa["burden"]["max"],
        "peak_burden_rbf": ill["burden"]["max"],
        "recovery12_fixed": fa["recovery_ratio"].get("12"),
        "recovery12_rbf": ill["recovery_ratio"].get("12"),
        "incomplete_rbf": ill["incomplete_recovery_rate"],
        "faster_by_month_12": faster,
        "sentence": (f"In this scenario, peak payment burden reaches "
                     f"{fa['burden']['max']:.1%} under the fixed arm against "
                     f"{ill['burden']['max']:.1%} under the revenue-based arm, "
                     f"and {faster} has recovered more by month 12."),
    }


def _findings(scenario: str, arms: List[dict]) -> List[dict]:
    """Conclusions for THIS scenario, each carrying its claim classification.

    Comparative statements are derived from the values just returned — the same
    numbers the UI displays — so a finding cannot drift from the chart beside it.
    Every scenario-dependent statement names the scenario.
    """
    by = {a["id"]: a for a in arms}
    label = SCENARIOS[scenario]["label"].lower()
    out: List[dict] = [
        {"classification": "mathematical_property",
         "text": "Contractual remittance is a fixed share of NET SALES, so the "
                 "contractual burden is constant by construction. The burden "
                 "shown here uses a different denominator — payment ÷ GMV — "
                 "so it equals r·(1 − return rate) and MOVES when the return "
                 "rate moves. It is constant only in scenarios where the "
                 "net-sales/GMV ratio is fixed. Most registered scenarios hold "
                 "that ratio fixed; `returns_spike` is the explicit exception "
                 "where the displayed burden moves.",
         "source": "research/DERIVATIONS.md"},
        {"classification": "mathematical_property",
         "text": "A fixed instalment does not adjust, so its burden rises in "
                 "INVERSE proportion to revenue: halve revenue and the burden "
                 "doubles. (It does not rise 'in proportion' — that would mean "
                 "falling with revenue, which is what the revenue share does.) "
                 "Under a revenue share the expected repayment period lengthens "
                 "instead. That is a statement about the payment rule, not about "
                 "whether the contract is ultimately repaid: where revenue stops "
                 "before the cap is reached, a balance goes unrecovered. The "
                 "trade is timing, not forgiveness — and not immunity.",
         "source": "research/DERIVATIONS.md"},
    ]

    fa, eq, ill = by.get("FIX-A"), by.get("RBF-EQ"), by.get("RBF-ILL")

    if fa and ill:
        out.append({
            "classification": "simulation_result",
            "text": (f"In the {label} scenario, the cost-matched fixed arm reaches "
                     f"a peak payment burden of {fa['burden']['max']:.1%}, against "
                     f"{ill['burden']['max']:.1%} for the revenue-based arm."),
            "source": fa["source_artifact"]})

        f12, r12 = fa["recovery_ratio"].get("12", 0), ill["recovery_ratio"].get("12", 0)
        direction = "ahead of" if f12 >= r12 else "behind"
        out.append({
            "classification": "simulation_result",
            "text": (f"In the {label} scenario, provider recovery by month 12 is "
                     f"{f12:.1%} for the fixed arm and {r12:.1%} for the "
                     f"revenue-based arm — the fixed arm is {direction} the "
                     f"revenue-based arm here. This ordering is a property of "
                     f"this scenario and does not hold across all of them."),
            "source": ill["source_artifact"]})

        if ill["incomplete_recovery_rate"] > 0:
            out.append({
                "classification": "simulation_result",
                "text": (f"In the {label} scenario "
                         f"{ill['incomplete_recovery_rate']:.1%} of simulated "
                         f"paths do not reach the repayment target within the "
                         f"24-month window. That is censoring under this "
                         f"scenario's revenue path, not a modelled default."),
                "source": ill["source_artifact"]})

    if eq and ill and eq["effective_apr"] is not None and ill["effective_apr"] is not None:
        # A-9 / D-050. This comparison is between two RATES, so the question is
        # whether the two rates were averaged over comparably selected sets --
        # which means comparing their APR-DEFINED shares, not their completion
        # shares. The previous version branched on `censored`, a duration
        # property, and then quoted completion shares as though they were the
        # rate's denominator. At closure_m7 that produced the worst possible
        # output: `censored` is False because *nothing* completed, so the page
        # asserted "every path completed under both" over 0/500.
        eq_defined = eq.get("apr_defined_share", 1.0)
        ill_defined = ill.get("apr_defined_share", 1.0)
        same_rate_population = abs(eq_defined - ill_defined) < 1e-9
        partial = min(eq["completed_share"], ill["completed_share"]) < 1.0

        # Completion is reported on its own, always, and never inferred from
        # the rate. It is a separate sentence because it is a separate fact.
        completion_note = (
            f"Completion is reported separately and differs between them: "
            f"{eq['completed_share']:.1%} of the cost-matched arm's paths and "
            f"{ill['completed_share']:.1%} of the illustrative arm's reached "
            f"the repayment target."
            if abs(eq["completed_share"] - ill["completed_share"]) > 1e-9 else
            f"Completion is reported separately: {eq['completed_share']:.1%} of "
            f"paths reached the repayment target under both.")

        # Where the target is not reached, the rate is an observed-window
        # figure over the 24-month horizon -- not the cost of a repaid
        # contract. It must never be read as a completed-contract price.
        window_note = (
            " Where the target is not reached the rate is an observed-window "
            "IRR over the payments made inside the 24-month horizon, not the "
            "cost of a completed contract." if partial else "")

        if same_rate_population:
            # Where the two rates COINCIDE there is no difference to attribute,
            # and saying the cap factor caused one would be an explanation of
            # nothing. At closure_m7 neither cap binds before revenue stops, so
            # the payment streams are identical and so are the rates -- the
            # targets differ but never become reachable.
            rates_equal = abs(eq["effective_apr"] - ill["effective_apr"]) < 5e-5
            if rates_equal:
                body = (f"Both cap factors give the same mean simulated rate of "
                        f"{ill['effective_apr']:.2%} in the {label} scenario. "
                        f"Neither cap binds before revenue stops, so the two "
                        f"contracts make identical payments and their "
                        f"observed-window rates coincide despite different "
                        f"contractual targets. There is no price effect here to "
                        f"attribute — the difference the cap factor makes "
                        f"elsewhere requires the cap to be reachable.")
            else:
                body = (f"Price and structure are separable. The same "
                        f"revenue-share structure priced at the reference-path "
                        f"cost-matched factor shows a mean simulated rate of "
                        f"{eq['effective_apr']:.2%} in the {label} scenario, "
                        f"against {ill['effective_apr']:.2%} at the illustrative "
                        f"1.20 factor. Both means are taken over the same share "
                        f"of paths — {eq_defined:.1%} have a defined rate under "
                        f"each — so the rate comparison is like-for-like and the "
                        f"difference is a property of the chosen cap factor, not "
                        f"of revenue-based repayment.")
            out.append({
                "classification": "sensitivity_result",
                "text": f"{body} {completion_note}{window_note}",
                "source": eq["source_artifact"]})
        else:
            out.append({
                "classification": "simulation_result",
                "text": (f"In the {label} scenario these two revenue-based arms "
                         f"cannot be compared on rate alone. The cost-matched arm "
                         f"shows {eq['effective_apr']:.2%}, averaged over the "
                         f"{eq_defined:.1%} of its paths with a defined rate; the "
                         f"illustrative arm shows {ill['effective_apr']:.2%} over "
                         f"{ill_defined:.1%} of its paths. Those are differently "
                         f"selected sets, so the difference between them combines "
                         f"the cap factor with differing selection and no "
                         f"like-for-like price conclusion is drawn. "
                         f"{completion_note}{window_note}"),
                "source": eq["source_artifact"]})
    elif ill and ill["effective_apr"] is None:
        out.append({
            "classification": "mathematical_property",
            "text": ("Effective rate is UNDEFINED for the revenue-based arm in "
                     "this scenario — not because repayment was incomplete, but "
                     "because no payment was made at all, so the rate equation "
                     "has no root. An incomplete contract that paid something "
                     "does have a rate, and it is reported. Here no discount "
                     "rate sets its present "
                     "value equal to the amount lent. The study reports this as "
                     "undefined rather than substituting a number "
                     "(specification §13, exclusion E-3)."),
            "source": "research/METHODOLOGY_SPEC.md §13"})

    out.append({
        "classification": "product_implication",
        "text": "A revenue share makes the CONTRACTUAL remittance a fixed share "
                "of net sales, so the contractual burden does not rise when "
                "revenue falls. The burden displayed here uses a different "
                "denominator — payment ÷ GMV — so it is constant only while the "
                "net-sales/GMV ratio is fixed, and it varies when returns vary. "
                "The price of the revenue-contingent structure is a MORE "
                "VARIABLE recovery period whose direction depends on the "
                "realised path: under P4 revenue-contingent recovery leads a "
                "cost-matched fixed schedule when the realised mean eligible "
                "base clears B* = P/r and lags when it does not, and both "
                "occur in the registered scenarios. Calling it uniformly "
                "longer would state one scenario's direction as a property "
                "of the structure. Which side of that trade is worth taking "
                "is a commercial judgement this study does not make.",
        "source": "author"})
    out.append({
        "classification": "open_real_world_question",
        "text": "Whether real sellers would repay on these paths, and at what "
                "default rate, cannot be answered here. It needs observed revenue "
                "and adjudicated repayment outcomes.",
        "source": "research/CORRECTED_CLAIMS.md"})
    return out
