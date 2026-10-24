# Retrospective contract-mechanics evaluator — reviewed specification

**STATUS: PROPOSAL FOR REVIEW. NOT APPROVED. NOTHING BUILT.**
No `evaluation/` package exists in this repository (verified 2026-10-24).
This document registers no result, changes no research artifact, and authorises
no construction. The gate in §10 remains closed.

**Supersedes in role, not in record:** `EVALUATION_PLAN.md` (19 Oct) and
`evidence/2026-10-23-evaluation-plan-review.md` (23 Oct). Both are retained
unchanged as the audit trail. Where this document differs from either, the
difference is stated and the reason given.

**Why a successor was needed.** `EVALUATION_PLAN.md` was written against
`SELLERFLOW_STARTUP/sellerflow` at `1563c5e` and states plainly that it could
*not* confirm whether `origin/main` had moved. It had. That path no longer
exists — the directory is now `RBF-Revenue-Based-Financing` — and `origin/main`
is `226487e`, two merges ahead (#6 redesign, #7 declaration correction). Every
load-bearing claim has therefore been re-verified against current code; §2
records the outcome, including **two claims that did not survive**.

---

## 1. Scope

**What this is.** A proposed offline tool that applies *explicitly specified*
financing contracts to *supplied* monthly revenue histories, shows the resulting
contractual cash flows and repayment behaviour under stated assumptions, and
explains its own arithmetic.

**What it is not, and must never become without a separate authorised scope:**
approval, creditworthiness, suitability, default prediction, a credit
recommendation, a pricing recommendation, or any claim about a merchant's
future. It makes no use of the risk scorer.

**First slice is synthetic-only.** Construction and all testing use synthetic
revenue histories and synthetic terms. Real lender data is a separate gate
(§10), not a later convenience.

---

## 2. Verified repository facts

Re-verified 2026-10-24 against the current tree by five independent checks, each
required to produce file:line evidence or literal command output. **Two claims
were refuted.** Both are recorded here because both change the design.

### 2.1 Confirmed

| Fact | Evidence |
|---|---|
| `money.py` exposes `to_decimal, to_vnd, to_increment, raw_advance, recommended_advance, repayment_cap, periodic_payment, settle, illustrative_schedule` | `backend/money.py:55,64,76,85,90,95,106,111,126` |
| Rounding is `ROUND_HALF_UP`, unit is integer VND | `money.py:39,45,52,71-73`; `to_vnd(2.5)==3` while builtin `round(2.5)==2` |
| `settle` rounds **before** clipping; cumulative total never exceeds cap | `money.py:116-123`; `settle([40.6]*5, 100) == [41,41,18,0,0]` |
| `money.py` imports **only** stdlib — three import lines, no lazy imports | `money.py:37,39,40` (`__future__`, `decimal`, `typing`) |
| `ADVANCE_INCREMENT = Decimal("1E+3")` = 1,000 VND | `money.py:49`; exponent form is what makes `quantize` hit the thousands place |
| `financing_engine.py` has **zero** `ml_engine` references | grep returns nothing |
| Tier table hard-coded exactly as previously stated: Low 15%/8%/1.15, Medium 8%/12%/1.30, High zero | `financing_engine.py` tier table |
| `revenue_metrics(..., revenue_history=None)` accepts a list | signature read |
| `effective_apr(principal, flows)` and `irr_upper_bound(principal, flows)` accept an **arbitrary flow vector** and are free of tier coupling | signature read |
| FIX-B truncation trap is **real** | `research/rbf_sim/contracts.py:108` constructs only `T` payments |
| Importing `money` in a fresh process pulls in no scorer/web/ML module | empirical: `sys.modules` intersection is `[]` |

### 2.2 Refuted — and what changes because of it

**R-1 · `import backend.financing_engine` fails outright.**
`financing_engine.py:30` uses a flat `from money import ...`, so importing it as
a submodule raises `ModuleNotFoundError: No module named 'money'`. The plan's
implicit assumption that one import strategy serves both modules is false.
**Consequence:** §5 fixes the import route explicitly rather than leaving it to
whoever writes the first file.

**R-2 · The frontend does not *collect* `owner_name`/`phone` — but it still
displays and exports `owner_name`.**
No contact field exists among the 12 form ids in `frontend/demo.html:788-816`,
and the submitted payload omits both (`demo.html:1107,1109,1134`). However
`demo.html:1334` renders `${s.owner_name||''}` in the admin portfolio table and
`demo.html:1338` includes `owner_name` in the CSV export column list.
**Consequence:** see §11, D-1. This is a live defect in the product, not in the
plan, and the existing guard does not catch it.

### 2.3 Behaviours found that the plan does not mention

These are not defects; they are properties that would silently break a naive
implementation.

1. **`settle` does not short-circuit.** Once the cap is exhausted it keeps
   iterating and appends `0` for every remaining candidate, so output length
   always equals input length. Trailing zeros are meaningful padding. **Any
   assertion of the form "schedule length == number of payments made" is wrong.**
2. **`settle` floors each payment at zero** (`max(0, ...)`), so a negative
   candidate becomes `0` rather than a credit or an error. Negative input must be
   rejected at validation — **do not rely on `settle`'s clamp as validation.**
3. **The `money.py:114` docstring says `sum(settle(...)) <= cap_vnd` "exactly and
   always."** That fails for a negative cap: `settle([10], -5) == [0]`, and
   `0 > -5`. Harmless in the product (caps derive from a positive advance) but a
   property test over arbitrary integers would falsify the word "always".
4. **`repayment_cap` does not enforce its own documented precondition.** The
   docstring requires the already-rounded advance; the function accepts any
   `Number`. The ordering discipline lives in the callers, so **no claim may be
   made that `money.py` itself guarantees the rounding order.**
5. **The dependency arrow points the other way.** `money` is a shared leaf:
   `financing_engine.py:30`, `ml_engine.py:49`, `database.py:7` and `lab.py:33`
   all import it. The correct isolation statement is *"the evaluator imports
   `money` without pulling in the scorer"* — **not** *"`money` belongs to the
   deterministic layer."* A change to `money`'s rounding helpers touches
   `ml_engine` and `database` too.
6. **`financing_structure` takes a scalar `monthly_revenue`**, derives duration
   as `ceil(cap / remittance)` and produces only the flat base case. It
   **structurally cannot** price a declining, volatile or interrupted revenue
   path. This is the decisive reason to bypass it, stronger than the tier
   argument.
7. **`net_collectible_revenue` silently clamps `return_rate` to `[0.0, 0.95]`.**
   A sweep passing a higher rate gets `0.95` back with no error.
8. **`run_path` has no input channel for observed payments at all.**
   `engine.py:41-46` builds every payment vector from `terms`. Even a perfectly
   faked `SellerPath` returns simulated payments. Lead with this, because
   "expects `SellerPath` metadata" invites someone to synthesise the metadata.
9. **`SellerPath` hard-codes `provenance: str = field(default="simulated",
   init=False)`** (`generator.py:121`). Lender data routed through this class
   would be stamped *simulated* with no way to override, and the field is read
   nowhere, so nothing would catch it. That is the registry's mislabelling
   hazard running in the dangerous direction.

---

## 3. Required boundary table

The seven areas that must be reviewable before construction.

| Area | Boundary |
|---|---|
| **Calculations** | Reuse `money.to_vnd, to_decimal, repayment_cap, periodic_payment, settle`, and `financing_engine.effective_apr / irr_upper_bound` (flow-vector form only). Integer VND throughout; `ROUND_HALF_UP`; round **then** clip. Bypass `financing_structure` (§2.3-6) and every `rbf_sim` engine entry point (§2.3-8,9). |
| **Inputs** | Complete calendar months; explicit `data_status ∈ {observed, missing, partial}`; **missing is never zero**; integer non-negative VND; decimal-string rates; validation rejects before any helper is called. Schema in §6. |
| **Results** | Contractual cash flows and repayment behaviour under one named, restated assumption. Three panels that never merge or share an axis (§8). Unreached cap at horizon is reported as *not completed within this window under the stated assumption*. |
| **Conclusions** | Excluded by construction: approval, creditworthiness, default prediction, suitability, pricing advice, any forward-looking claim. "Incomplete" is never "default" — there is no default model in this project (`backend/tests/test_public_copy.py`: *"no default model exists in this study; non-recovery is mechanical"*). |
| **Isolation** | Import route A (§5). No scoring import, no production database handle, no HTTP server, no Resend, no Stripe, no writes outside a caller-specified output directory. Asserted in a fresh process, not inferred from directory layout. |
| **Verification** | Hand-computed fixtures whose expected values are **not** emitted by the code under test. Rejection tests for every unsupported class. §9. |
| **Real data** | A separate gate requiring permissions, lawful basis, access separation, retention/deletion rules, and a passing isolation suite. Not reachable by this specification (§10). |

---

## 4. Reuse boundary

| Decision | Reason (verified) |
|---|---|
| **Reuse** `money.repayment_cap, periodic_payment, settle, to_vnd, to_decimal` | Pure arithmetic over explicit arguments; stdlib-only; `settle` already implements the cap clipping that is easiest to get subtly wrong by hand |
| **Reuse** `effective_apr(principal, flows)` / `irr_upper_bound(principal, flows)` | Accept an arbitrary flow vector, no tier coupling. **The 19 Oct plan missed these** — they are the correct rate layer |
| **Bypass** `financing_structure()` | Scalar revenue only; cannot express a revenue path (§2.3-6). Also applies the hard-coded tier table, and a lender's "Tier A" is not `TIER_RATES["Low Risk"]` |
| **Bypass** `rbf_sim.engine.run_path / run_scenario` | No input channel for supplied payments (§2.3-8); `SellerPath` stamps `provenance="simulated"` unchangeably (§2.3-9); FIX-B truncation trap (§2.1) |
| **Permitted new code, with its own fixtures** | Validation, calendar alignment, integer sales-minus-returns, running totals, complete-schedule totals, report assembly |
| **Forbidden new code** | Duplicating monetary primitives, inventing contract terms, inferring tiers, generating amortisation schedules, adding a rate solver |

*This replaces the 19 Oct plan's blanket "do not reimplement any arithmetic",
which was unworkable — the adapter logic above is necessary and new.*

---

## 5. Import route — decided

**Route A: `import backend.money`, with no `sys.path` manipulation.**
Empirically verified to work and to pull in no scorer, web or ML module.

**Route B (`sys.path.insert(0, <repo>/backend)`) is rejected** for the evaluator.
It is the convention used by `conftest.py` and `tools/preview_redesign.py`, but it
places `backend/` at the *front* of `sys.path`, making `ml_engine`, `main`,
`database`, `models`, `lab` and `data` importable as top-level names.
`main` and `data` are generic enough to shadow a third-party package. Route A
avoids this entirely.

A test must assert the **resolved file path** of the imported `money` module, so
that an unrelated installed package named `money` cannot satisfy the import
silently.

---

## 6. Input schema

Pseudonymous `merchant_id` only. **No names, phones or account identifiers.**

| File | Key | Required fields |
|---|---|---|
| `run_manifest.json` | — | schema_version; code revision + dirty flag; extraction timestamp; input hashes; `currency=VND`; `period_basis=monthly`; window start/end; `input_provenance ∈ {synthetic, real}`; stated assumptions |
| `merchant_periods.csv` | `(merchant_id, period_start)` | period_start, period_end (ISO); gross_sales_vnd; returns_vnd; `data_status ∈ {observed, missing, partial}` |
| `contracts.csv` | `(merchant_id, contract_id)` | `contract_kind ∈ {revenue_share_capped, fixed_schedule}`; `role ∈ {historical, alternative}`; origination_date; principal_vnd; `eligible_base ∈ {gross, net_of_returns}`; remittance_rate; factor_rate; maturity_date |
| `scheduled_obligations.csv` | `(contract_id, due_date)` | due_amount_vnd; `schedule_completeness ∈ {complete_contractual, observation_window_only}` |

**`contract_kind` is separate from `role`.** Evidentiary role cannot choose a
calculation; revenue-share fields apply only to `revenue_share_capped`, a
supplied schedule only to `fixed_schedule`. Contradictory or irrelevant terms are
rejected, never ignored.

`observed_payments.csv` is **not ingested in the first slice.** The report prints
*"Observed collections: not supplied / not evaluated."*

---

## 7. Calendar and semantics — decided for the first slice

1. **Calendar.** Complete calendar months; period-end settlement; origination at
   the preceding month-end; no mid-month advances, no prorating. A clipped final
   payment occurs **on a period's settlement date** — not "mid-period". A monthly
   aggregate cannot identify the day revenue reached the target.
2. **Missing ≠ zero.** A zero is an explicit observed amount with complete
   coverage. A merchant with any missing or partial required month is **excluded
   from calculation** and listed in the receipt; no estimation. Other merchants
   proceed, with explicit included/excluded counts.
3. **Observation end ≠ maturity ≠ completion.** A supplied fixed schedule's
   contractual total is the **whole schedule sum**, including rows due after the
   observation end; due-in-window and due-after-window are shown separately.
   Never insert a terminal payment to make a schedule look complete.
4. **First slice supports only contracts with no terminal maturity clause.**
   Balloon, write-off and mandatory catch-up terms are rejected until modelled.
5. **Obligations ≠ collections.** The only supported assumption is full timely
   payment at each period end; the resulting stream is labelled **"hypothetical
   collections under full timely payment."** Partial payments, arrears and
   delayed remittance are unsupported. **No observed-payments panel may ever be
   populated from computed remittances.**
6. **Rounding authority.** Integer VND, `ROUND_HALF_UP`, round then clip, stated
   in every report. The product's 1,000-VND advance increment is **not** applied
   — supplied principal is preserved exactly.
7. **Validation precedes helpers.** Reject NaN, infinity, fractional VND,
   negative amounts, duplicate periods, overlaps, unknown contract references,
   unrecognised columns, and returns exceeding gross sales — *before* any
   `money.py` call. Per §2.3-2, `settle`'s zero-clamp is not validation.

---

## 8. Report

Panels that never merge, never share an axis, never pool into an unlabelled mean:

1. **Scope banner** — synthetic or supplied data; mechanical counterfactual; no
   live decision; no predictive claim.
2. **Data receipt** — rows, merchants, complete/missing/partial counts,
   exclusions, input hashes, schema version, code revision, rounding rules.
3. **Contract specification** — every term as supplied, with its source.
4. **Panel A — Observed payments.** First slice: *not supplied / not evaluated.*
5. **Panel B — Computed obligations** under the specified contract.
6. **Panel C — Hypothetical collections** under full timely payment, with the
   assumption restated inside the panel.
7. **Unrecovered contractual target at horizon** — explicitly *not* principal
   loss, *not* default.

Self-contained HTML plus a machine-readable JSON receipt. All input text escaped;
no scripts, external fonts, remote images or telemetry. No CSV export in this
slice (formula-injection surface).

---

## 9. Verification required before any result is reported

| | Check |
|---|---|
| V1 | Hand-computed fixtures, expectations written into the fixture and **never** emitted by the code under test: cap clipping at a period end, exact cap division, genuine zero months, no completion within window, supplied schedule extending beyond observation, and both `eligible_base` values |
| V2 | **Padding semantics** — assert `settle` output length equals input length and trailing zeros are preserved (§2.3-1) |
| V3 | **Missing vs zero** — a missing month and a genuine zero month produce different outputs; missing never becomes zero |
| V4 | **Rejection tests** for every unsupported class in §7.7, each raising its named error rather than coercing |
| V5 | **Import isolation in a fresh process** — `ml_engine, sklearn, fastapi, database, main, numpy, pandas` absent from `sys.modules`; plus an assertion on the **resolved path** of `money` (§5) |
| V6 | **Socket-blocked execution** of the synthetic workflow. Recorded as evidence about *the tested path* — not proof that every execution is offline |
| V7 | **Output containment** — no file written outside the caller-specified directory; no input file overwritten; no registered research artifact touched |
| V8 | **No PII** — scoped to `evaluation/`'s own files, written as an **allowlist** of permitted field names, not a denylist of two strings (§11, D-2) |
| V9 | **Truncation refusal** — an `observation_window_only` schedule must refuse to report completion |

---

## 10. Gates

**Gate 1 — construction.** Closed until this specification is reviewed and the
§12 decisions are settled.

**Gate 2 — real data.** Closed until V1–V9 pass on synthetic fixtures *and*
permissions, lawful basis, access separation, retention and deletion are settled
in writing. Passing tests do not open this gate. Neither does a lender's verbal
assurance. Vietnamese data-handling and cross-border requirements are a separate
question this document does not address.

**Gate 3 — any claim of usefulness.** Tests establish arithmetic, not commercial
value and not predictive validity. Nothing here licenses a claim that a lender
benefits.

---

## 11. Defects found during verification

**D-1 · `owner_name` is displayed and exported after being dropped from collection.**
`frontend/demo.html:1334` renders it in the admin portfolio table and `:1338`
includes it in the CSV export columns, for records submitted before the field was
removed. The existing guard `backend/tests/test_public_surface_disclosure.py:58-66`
asserts only that the `f_`-prefixed input ids are absent, so it passes over the
display and export path entirely. **This is a product defect, not a plan defect.**
Decide deliberately whether it is intended backward compatibility for historical
rows or residue to remove — and either way, the evaluator must not mirror it.

**D-2 · The planned PII test, as written, cannot work.** A repo-wide "no
`owner_name` / no `phone`" grep would fail on code that is correct and in use:
`backend/main.py:334,341`, `backend/database.py:28-29`, `backend/tests/test_api.py:17`.
The assertion must be scoped to `evaluation/`'s own files and written as an
allowlist, so a *future* PII field is caught too.

**D-3 · A dated factual claim now sits in public copy.** `demo.html:928` states
the fields "were removed in September 2026 because the assessment never used
them." Dated negatives expire silently; this one should be reviewed for accuracy
and kept current or rephrased.

---

## 12. Decisions still required before construction

| | Decision | Recommendation |
|---|---|---|
| U1 | `eligible_base` default | None. Require it explicitly per contract; reject silence |
| U2 | Principal basis | Positive whole VND, disbursement == principal in this slice; reject withheld fees and multiple advances; defer APR output rather than implying a rate solver exists for arbitrary dated flows |
| U3 | Is `observed_payments.csv` needed at all in slice 1? | **No.** Panels B and C need only revenue history and terms; requiring a payment ledger raises the data-sensitivity bar for outputs that do not need it |
| U4 | Report format | Self-contained HTML + JSON receipt; no CSV |
| U5 | Location | `evaluation/` in this repository, no route, no endpoint. A separate repository is cleaner for a lender security review and costs more to maintain — defer |
| U6 | Rounding if the lender's ledger differs | Agree in advance whether to adopt their convention or report the delta. Do **not** silently normalise |
| U7 | D-1 above — backward compatibility or residue? | Product decision, not the evaluator's |

---

**Nothing in this document authorises construction, deployment, real-data access,
or any claim about commercial usefulness.**
