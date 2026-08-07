# Execution Backlog — RBF Project, August 2026

Frozen scope. Items are ordered by dependency, not by preference.
Status: `todo` · `doing` · `done` · `frozen` · `cut`

**Legend — priority:** P0 = blocks credibility today · P1 = blocks the research question · P2 = quality · P3 = nice-to-have.

---

## Phase 0 — Audit & scope (Aug 3–4)

| ID | Item | Pri | Status | Notes |
|---|---|---|---|---|
| A-01 | Clone, install, run tests, retrain, fetch live site | P0 | **done** | 47 tests pass; ensemble AUC 0.9182 reproduces |
| A-02 | Write `PHASE0_AUDIT.md` | P0 | **done** | 8 integrity risks, 6 gaps |
| A-03 | Write `audit_evidence.py` (reproducible RI-1/2/3) | P0 | **done** | Becomes `research/analysis/00_audit_evidence.py` |
| A-04 | Backlog + decision log + results registry | P0 | **done** | This file, `DECISION_LOG.md`, `RESULTS_REGISTRY.md` |
| A-05 | Confirm Q1–Q5 with Hoang | P0 | todo | Blocks Phase 1 framing |
| P0-1 | **Redeploy Railway from `bff1477`; verify RBF live** | P0 | todo | Highest credibility/effort ratio in the project |
| P0-2 | Retire 0.92 AUC from README, `/api/model/status`, UI | P0 | **done** | RI-1. D-026, 2026-08-07: API returns `auc: null` + `validation_status: "withdrawn"`; demo, UI and README purged. Enforced by `test_no_withdrawn_claims.py` (source scan, allowlist with reasons). Open elsewhere: `docs/GXS-Stage2-Proposal.md` (gitignored, competition material). |
| P0-3 | Remove "12.5% vs 40–80% informal rate" claim | P0 | todo | RI-5 — unsourced impact claim |
| P0-4 | Drop `owner_name` / `phone` from model, form, DB, CSV | P0 | todo | RI-6 |
| P0-5 | Un-ignore `docs/`; create versioned `research/` tree | P0 | **partial** | `research/` tree created and committed 2026-08-06 (bundle v5). **Still open:** `docs/` remains gitignored. |
| P0-6 | Fix README test count 29→47 | P2 | **done** | GAP-6. De-hardcoded entirely — README now states counts are whatever the suites report. |
| P0-7 | Remove `demo2025` default password from 3 files | P1 | **done** | RI-7. D-025: no default; unset ⇒ dashboard login disabled (503), fails closed. Enforced by `test_login_rejects_the_withdrawn_default_credential`. |
| P0-8 | Move GXS competition section to separate branch/appendix | P2 | todo | RI-8 — wrong audience |
| P0-9 | Rounding-rule divergence: `financing_engine` used banker's `round()`, policy is ROUND_HALF_UP | P1 | **done** | D-029 diagnosed, **D-030 fixed** 2026-08-07. `backend/money.py`: Decimal-from-strings, integer đồng, ROUND_HALF_UP. No cap overshoot ever existed — the earlier 5.77% claim was an analyst error, withdrawn. |
| P0-10 | Product money is `float`, not integer đồng | P1 | **done** | D-030. All contractual monetary API fields serialize as integer VND. |
| P0-11 | API does not disclose the partial final payment | P1 | **done** | D-030. `illustrative_schedule` on every structure and scenario row: full payments, partial final payment, completion month, total, and constant-revenue caveat. |

---

## Phase 1 — Research design (Aug 5–8)

| ID | Item | Pri | Status | Notes |
|---|---|---|---|---|
| R-01 | Final research question + revised title | P1 | todo | "Simulation-Based", not "Evidence-Based" |
| R-02 | **Freeze metric definitions in committed file** | P1 | todo | **Must precede any analysis run.** Commit timestamp is the pre-registration defense |
| R-03 | Define distress month + 3 alternative thresholds | P1 | todo | Sensitivity planned in advance, not post hoc |
| R-04 | Hypothesis restatement (H4 → affordability-under-stress) | P1 | todo | H4 untestable as prediction without labels |
| R-05 | Literature matrix, 12–18 Layer A sources | P1 | todo | WB Enterprise Survey VN 2023 + ADB + peer-reviewed RBF/merchant-cash-advance lit |
| R-06 | Research protocol document | P1 | todo | |
| R-07 | Pre-registered analysis plan | P1 | todo | Written before results exist |
| R-08 | Human-subjects determination | P1 | todo | Default: drop Layer B (see Q4) |
| R-09 | Financial-fairness matching spec (fixed vs RBF) | P1 | todo | Principal, origination, horizon, fees, cap, early repayment — all disclosed |

---

## Phase 2 — Evidence & data (Aug 9–15)

| ID | Item | Pri | Status | Notes |
|---|---|---|---|---|
| D-01 | Layer A extraction into literature matrix | P1 | todo | Every claim traceable to page/table |
| D-02 | Calibrated revenue-path generator | P1 | todo | Seeded, documented, provenance-tagged, **not** `generate_data.py` |
| D-03 | Calibration parameter table with cited sources | P1 | todo | Each parameter: value, source, or "assumption" |
| D-04 | Scenario library (9 scenarios from brief §5) | P1 | todo | Stable, seasonal, decline, growth, 1-mo disruption, high returns, outage, severe downturn, underreporting |
| D-05 | Data dictionary | P1 | todo | Required deliverable |
| D-06 | Data provenance record | P1 | todo | Required deliverable |
| D-07 | Enforce `revenue = orders × AOV` identity in generator | P1 | todo | Fixes RI-2 in the new data |
| D-08 | Verify new generator passes the integrity engine | P1 | todo | Closes RI-3 loop; result goes in the paper |
| D-09 | Public-safe sample dataset, clearly labeled synthetic | P2 | todo | |

---

## Phase 3 — Analysis & product integration (Aug 16–22)

| ID | Item | Pri | Status | Notes |
|---|---|---|---|---|
| C-01 | **`comparison_engine.py` — fixed-payment arm** | P1 | todo | **Critical path.** Does not exist today (GAP-3) |
| C-02 | RBF arm (wrap `financing_engine.py`) | P1 | todo | Reuse, don't rewrite |
| C-03 | Guardrailed RBF arm (floor/cap/hardship rules) | P1 | todo | Third comparison arm |
| C-04 | Paired runner — same revenue path, all three arms | P1 | todo | |
| C-05 | Seller-side metrics module | P1 | todo | Per frozen R-02 definitions |
| C-06 | Provider-side metrics module | P1 | todo | Recovery, duration variance, incomplete-recovery rate |
| C-07 | Bootstrap CIs | P1 | todo | |
| C-08 | Sensitivity: distress threshold, share %, cap, shock size | P1 | todo | |
| C-09 | Underreporting / diversion analysis | P1 | todo | H5, SQ4 |
| C-10 | Figures + tables, regenerated from code | P1 | todo | No hand-made numbers anywhere |
| C-11 | Results registry entries for every run | P1 | todo | |
| PR-01 | Revenue-history input (form + API + DB) | P1 | todo | GAP-4; activates dead `revenue_metrics()` history path |
| PR-02 | Fixed-vs-RBF comparison view | P1 | todo | |
| PR-03 | Stress-test panel | P1 | todo | |
| PR-04 | Explainability panel (which factors drove this) | P2 | todo | |
| PR-05 | Methodology page | P1 | todo | |
| PR-06 | **Findings page rendered from analysis output file** | P1 | todo | Never hand-typed — guarantees paper/app agreement |
| PR-07 | Model card | P1 | todo | Must state the placeholder status of the ensemble |
| PR-08 | Privacy + responsible-use notice rewrite | P1 | todo | Fix `hello@sellerflow.io` dead contact |
| PR-09 | Tests for comparison engine | P1 | todo | Hand-computed expectations, matching existing style |
| PR-10 | Route-level API tests | P2 | todo | Known gap in README |

---

## Phase 4 — Writing & presentation (Aug 23–27)

| ID | Item | Pri | Status |
|---|---|---|---|
| W-01 | Paper, 8–12 pp | P1 | todo |
| W-02 | Appendix: assumptions + metric definitions | P1 | todo |
| W-03 | Executive summary, 1 p | P1 | todo |
| W-04 | Research poster | P2 | todo |
| W-05 | 10-slide deck | P1 | todo |
| W-06 | README rewrite (public-facing) | P1 | todo |
| W-07 | 30s / 2–3min / 5–7min pitches | P2 | todo |
| W-08 | Guided demo script | P2 | todo |
| W-09 | Q&A prep — **lead with RI-1/RI-3** | P1 | todo |
| W-10 | Resume bullets (actual results only) | P2 | todo |
| W-11 | LinkedIn / portfolio copy + abstract | P2 | todo |
| W-12 | Portfolio screenshots | P3 | todo |

---

## Phase 5 — Red-team & ship (Aug 28–31)

| ID | Item | Pri | Status |
|---|---|---|---|
| V-01 | Trace every public number to source or code | P0 | todo |
| V-02 | Open and verify every citation | P0 | todo |
| V-03 | Regenerate every figure from committed code | P0 | todo |
| V-04 | Full test suite + production build | P0 | todo |
| V-05 | Deployment verified against repo HEAD | P0 | todo |
| V-06 | Placeholder / dead-link / secret sweep | P0 | todo |
| V-07 | Paper ↔ poster ↔ deck ↔ README ↔ app consistency check | P0 | todo |
| V-08 | Adversarial mock defense | P1 | todo |
| V-09 | Final release checklist + archive tag | P1 | todo |

---

## Frozen — explicitly not August work

Stripe / payments / checkout · API keys, quotas, plans, pricing page · lead capture + email alerts · visit beacon · multi-tenancy / per-user accounts · PDF export · document upload / OCR · supervised fraud model · continuous-learning retraining cadence · GXS competition framing · domain / repo rename · **any retraining or improvement of the synthetic ensemble**.

*Rationale for the last item:* improving a circular benchmark makes the circularity worse, not better. The ensemble is demoted to a labeled structural placeholder; the project's quantitative weight moves to the deterministic comparison engine, which needs no labels and can be verified line by line.

---

## Cut list (if the schedule compresses)

Cut in this order. Do **not** cut C-01…C-10 or R-02.

1. W-12 portfolio screenshots
2. W-07 pitch variants (keep one, the 2–3 min)
3. W-04 poster
4. PR-10 route-level tests
5. PR-04 explainability panel
6. C-03 guardrailed RBF arm → reduce to two arms, state the reduction as a limitation
