# Decision Log — RBF Project

Every entry: decision · date · alternatives considered · reason · research/product consequence.
Append-only. Do not edit past entries; supersede them with a new entry.

---

### D-001 — Demote the synthetic ensemble to a labeled structural placeholder
**Date:** 2026-08-03
**Alternatives considered:**
1. Keep the 0.92 AUC with the existing "synthetic" disclaimer.
2. Retrain on a better synthetic generator to get a "more defensible" number.
3. Delete the ML model entirely.
4. Demote it: keep the code, retire the number, move quantitative weight to deterministic analysis. ← **chosen**

**Reason:** The label in `generate_data.py` is a hand-written weighted function of the same ten features the model consumes, plus `N(0,0.08)` noise. Measured: the generating function itself scores AUC 0.9098 against its own label, versus the model's 0.9182. The metric therefore measures the author's choice of noise variance, not predictive skill. Option 1 leaves a claim that collapses the moment a reviewer opens one file. Option 2 makes the circularity more elaborate without removing it. Option 3 discards working, honest, well-tested code and the provenance system built around it.

**Consequence:**
- *Research:* the project no longer claims default prediction. Quantitative claims rest on repayment mechanics and cash-flow resilience under simulated revenue paths — which require no labels and are verifiable line by line.
- *Product:* `/api/model/status` and the UI must stop reporting 0.92. The model card must state placeholder status explicitly.
- *Narrative:* this becomes a strength. "I found my own headline metric was circular and retired it" is a better story than any AUC.

---

### D-002 — Title changes "Evidence-Based" → "Simulation-Based"
**Date:** 2026-08-03
**Alternatives considered:** keep "Evidence-Based Evaluation"; use "Mechanical Evaluation"; use "Simulation-Based Evaluation". ← **chosen**

**Reason:** No observed seller repayment outcomes will exist by August 31. Layer A public evidence motivates the problem; Layer C simulation answers the mechanical question. A title that announces its own method cannot be attacked on method. "Evidence-Based" invites a reviewer's first question to be the one question the project cannot answer.

**Consequence:** Paper, poster, deck, README, and abstract all use the simulation framing. The evidence hierarchy is unchanged.

---

### D-003 — Drop Layer B (primary seller interviews/survey) by default
**Date:** 2026-08-03 *(provisional — reversible on Hoang's answer to Q4)*
**Alternatives considered:** 10–15 interviews; 30–50 survey responses; small mixed-method; none. ← **chosen by default**

**Reason:** Recruiting, consent, instrument design, and analysis inside a 28-day window, with human-subjects review unresolved, is the highest schedule risk on the plan. A rushed convenience sample adds little defensible evidence and considerable exposure. Absence of primary evidence is a clean, statable limitation; a poorly run study is not.

**Consequence:** Layer A + Layer C project. "No primary seller evidence" appears in Limitations and Future Research. **Reversible** if Hoang confirms institutional coverage and wants it in scope.

---

### D-004 — Freeze metric definitions before running any analysis
**Date:** 2026-08-03
**Alternatives considered:** define metrics as the analysis develops; define after seeing initial results; freeze in a committed file first. ← **chosen**

**Reason:** The brief requires that "distress month" not be defined arbitrarily after seeing results. A committed file with a timestamp preceding the first analysis run is the only verifiable defense against that charge. Sensitivity analysis over alternative thresholds is planned in the same file, in advance.

**Consequence:** R-02 blocks C-01. No comparison run happens before the definitions commit exists.

---

### D-005 — Redeploy before building anything new
**Date:** 2026-08-03
**Alternatives considered:** redeploy at the end alongside new features; redeploy now. ← **chosen**

**Reason:** The live site currently serves the superseded SellerFlow credit-limit product. The last six commits — the entire RBF rename, the integrity engine, real-data validation — are not deployed. Every day the link is shared, it shows a product that contradicts the README. This is a one-command fix with the highest credibility-per-effort ratio available.

**Consequence:** P0-1 runs first. Deployment parity with repo HEAD becomes a standing checklist item, re-verified in Phase 5 (V-05).

---

### D-006 — Reframe the integrity-engine contradiction as a research finding
**Date:** 2026-08-03
**Alternatives considered:** fix the generator silently; suppress the finding; document it as a limitation only; promote it to a named result. ← **chosen**

**Reason:** `integrity_engine.revenue_reconciliation()` flags 62.3% of the rows the credit model was trained on, because the synthetic generator draws revenue, order volume, and AOV independently and so violates `revenue = orders × AOV` in 61% of rows. Silently fixing it discards a genuine, reproducible demonstration of a real model-risk failure mode: synthetic underwriting data can violate accounting identities that downstream fraud controls depend on, and neither component detects the conflict.

**Consequence:** The new generator (D-02) enforces the identity, and the before/after comparison becomes a named result supporting H5. It is also the anchor of Q&A prep — the strongest available answer to "how do you know your data is any good?"

---

### D-007 — Freeze all monetization and competition scaffolding
**Date:** 2026-08-03
**Alternatives considered:** keep as evidence of product thinking; keep but hide; freeze and remove from the narrative. ← **chosen**

**Reason:** Stripe checkout, API-key quotas, plan pricing, lead capture, and the GXS Bank problem-statement section serve a different audience with different success criteria. They pull the story toward capabilities not built (adaptive fraud, continuous learning) and away from the single claim the project can defend. Scope discipline in a 28-day window matters more than breadth.

**Consequence:** Code stays in the repo but is removed from README narrative, deck, and demo script. The GXS section moves to a branch or appendix.

---

### D-009 — Scope confirmed by Hoang: Vietnam · no Layer B · pure simulation · recruiters weighted
**Date:** 2026-08-03
**Alternatives considered:** presented as four decisions with options; all four resolved to the recommended option.

**Decisions:**
1. **Population — Vietnam-focused.** Shopee / TikTok Shop / Lazada, VND, CIC bureau-gap framing. Generalizability beyond Vietnam stated as an explicit limitation.
2. **Layer B — dropped.** D-003 is now confirmed rather than provisional. No interviews, no survey, no human subjects. No IRB question arises.
3. **Layer C — pure simulation.** No real seller revenue histories. Parameters calibrated to cited public statistics with full sensitivity analysis; every path labeled simulated.
4. **Audience — recruiters first**, faculty close second. If the final week compresses, product polish and deck outrank paper length.

**Reason:** Each is the lower-risk option in a 28-day window, and together they make the project's evidential claim internally consistent: a Vietnam-motivated, simulation-answered, mechanically-verifiable study. The title change in D-002 now matches the actual method exactly.

**Consequence:**
- *Research:* the paper claims **no** empirical finding about real seller behavior. Every quantitative result is a statement about repayment mechanics under stated assumptions. Limitations must say this in the abstract, not only in §7.
- *Product:* the findings page presents simulated results with unmistakable labeling.
- *Schedule:* Phase 2 loses recruitment and consent work entirely, freeing ~3 days. Reallocate to the comparison engine (C-01…C-10), which is the critical path.
- *Statistics:* see `METRIC_DEFINITIONS.md` §6 — because paths are simulated, confidence intervals describe Monte Carlo precision only, never uncertainty about real sellers. This distinction is load-bearing and must never be blurred.

---

### D-010 — Primary distress definition: negative post-payment operating cash flow
**Date:** 2026-08-03
**Alternatives considered:**
1. Payment-to-revenue ratio above a threshold, e.g. `PTR_t > 0.15`.
2. Payment exceeds some share of gross profit.
3. Post-payment operating cash flow below zero. ← **chosen**
4. Missed-payment / default indicator.

**Reason:** Option 4 is unavailable — no labeled outcomes exist, and using it would reintroduce exactly the default-prediction claim D-001 removed. Option 1 is the most common choice but is arbitrary in its threshold and, worse, is *mechanically favorable to RBF by construction* (RBF holds PTR constant at `r` by definition, so an RBF arm can never breach a PTR threshold — the comparison would be rigged). Option 3 is economically meaningful, is not trivially satisfied by either arm, and depends on margin and fixed costs, which forces those assumptions into the open where they can be challenged.

**Consequence:** `D_t = 1` iff `OCF_t < 0`. Gross margin `m` and fixed operating cost `F` become named, sourced assumptions subject to sensitivity analysis. Three alternative thresholds are pre-specified in `METRIC_DEFINITIONS.md` §4.3 and will be reported regardless of whether they agree with the primary definition.

**This entry is the pre-registration.** Its commit timestamp must precede the first run of the comparison engine.

---

### D-012 — Binding decisions from Hoang; three of my earlier decisions superseded
**Date:** 2026-08-03
**Source:** Hoang, after reviewing the Phase 0 audit. Adopted in full.

**Title adopted:** *Revenue-Contingent Financing Under Volatile Sales: A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers.*

**Binding:**
1. The ensemble underwriting model is a **secondary demonstration component**, not a source of findings.
2. The 0.92 AUC is removed from headline claims; retained only where needed to explain the methodological correction.
3. **Do not deploy** until misleading performance claims and synthetic-data inconsistencies are corrected; label or remove the stale link immediately.
4. The primary quantitative contribution is the deterministic fixed-vs-RBF comparison.
5. All results described as simulation findings under stated assumptions.
6. The generator must respect accounting and operational identities.
7. The integrity-screen conflict is a documented model-risk lesson, **not** the main research conclusion.
8. No interviews, surveys, default prediction, or complex ML in August scope.

**Supersessions — three of my earlier decisions were wrong:**

| Superseded | Was | Now | Why Hoang is right |
|---|---|---|---|
| **D-005** | Redeploy first, before anything else | Deploy **last**, after claims are corrected | Redeploying now would publish a correctly-branded version of an *uncorrected* claim. The stale link is a documentation problem, fixed by labelling it — not by shipping the 0.92 AUC to production. |
| **D-006** | Integrity conflict promoted to a named result and Q&A anchor | Demoted to a documented model-risk lesson in Limitations | An internal bug in one's own synthetic generator is not a research contribution. Leading with it would make the project's headline "I found my own bug," which is a weaker claim than the financing comparison and invites the reviewer to doubt everything else. |
| **D-010** | Primary metric = "distress month" (`OCF < 0`) | Primary = **high-payment-burden month** (revenue-only); distress demoted to secondary and assumption-dependent | "Distress" asserts a financial state that revenue alone cannot establish, and it made the headline metric depend on `m` and `F`, which are unsourced. The burden metric needs no cost assumptions and is therefore more defensible. |

**Correction to my own reasoning.** In D-010 I rejected a payment-to-revenue burden threshold on the grounds that RBF holds `PB_t ≡ r` by construction and would therefore "rig" the comparison. That reasoning was wrong. The constancy *is* the structural fact under study; the information lives on the fixed-payment side, in how far and how often its burden rises as revenue falls. The correct response is to **state** what is definitional — done in spec §10.2 and asserted by `test_rbf_burden_is_constant_by_construction` — not to avoid the metric.

**Consequence:** `METRIC_DEFINITIONS.md` v0.1 superseded by `METHODOLOGY_SPEC.md` v1.0, frozen before the first outcome run. v0.1 retained for the audit trail.

---

### D-013 — Report F-3 and F-5 as null/negative results and go looking for the failure region
**Date:** 2026-08-03
**Trigger:** Baseline run `baseline_v1`.

**Alternatives considered:**
1. Report 0% incomplete recovery as evidence RBF is safe for providers.
2. Retune parameters until incomplete recovery appears.
3. Report both as stated, name the artifact, and pre-commit to searching for the failure region. ← **chosen**

**Reason:** Incomplete recovery is 0.0% in all ten scenarios and RBF-G is bit-identical to RBF in all ten. Option 1 would present a horizon artifact as a substantive safety finding — `T = 24` against a 12-month base duration leaves too much headroom for the metric to bind. Option 2 is parameter-shopping toward a desired result. Option 3 keeps both as honest null results and converts them into a specific Phase 3 task.

**Consequence:**
- *Research:* F-3 and F-5 enter the results registry as null results with their artifact status named. Phase 3 must locate the recovery-failure boundary (S-11 `T=18`, S-4 larger advances, deeper shocks, combined underreporting) and the guardrail-binding boundary (S-12 tight).
- *Product:* if guardrails never bind within plausible ranges, the guardrail feature is decoration and should not ship as a selling point. That is a finding driving a product decision — the project's stated goal.
- *Honesty:* "we found no failure region *and here is exactly where we looked*" is defensible; "we found no failure region" alone is not.

---

### D-030 — Product monetary policy corrected: Decimal, integer đồng, ROUND_HALF_UP
**Date:** 2026-08-07
**Approved by:** Hoang, on the D-029 diagnosis.
**Status:** **APPLIED.** Closes P0-9, P0-10, P0-11 and discharges D-029's open items.

**What was wrong.** `financing_engine` computed contractual money with binary floats and Python's `round()` — *banker's* rounding, ties to even — while the documented policy (D-023/D-024) is ROUND_HALF_UP on integer đồng. Deterministic divergence at ties; ~1 in 10,000 whole-VND revenues. Separately, the API emitted `(cap, remittance, duration)` with no indication that the final payment is partial.

**The fix.** A product-layer module, `backend/money.py`, with a fixed order:

1. raw advance = `revenue × 12 × advance_pct` — **Decimal, built from strings**
2. advance = ROUND_HALF_UP to the 1,000 VND increment
3. raw cap = `advance × factor_rate` — Decimal, from the **rounded** advance
4. cap = ROUND_HALF_UP to whole đồng
5. candidate payment = ROUND_HALF_UP to whole đồng
6. actual payment = `min(candidate, remaining balance)`
7. cumulative never exceeds the cap

Rounding *before* clipping is what makes step 7 unconditional. Deriving the cap from the **rounded** advance is deliberate: the advance is the amount actually disbursed, so it is the amount a merchant can reconcile the cap against.

**Rates are declared as strings.** `Decimal(0.15)` is 0.1499999999999999944…; `Decimal("0.15")` is exact. `TIER_RATES` now holds decimal strings and `TIER_PARAMS` derives floats for display only. No float enters a monetary calculation.

**Before / after**

| | revenue 2,500 | revenue 100,002,500 |
|---|---|---|
| advance before | 4,000 | 180,004,000 |
| advance after | **5,000** | **180,005,000** |
| cap before | 4,600 | 207,004,600 |
| cap after | **5,750** | **207,005,750** |
| type before | `float` | `float` |
| type after | **`int`** | **`int`** |

**Disclosure.** Every structure and every scenario row now carries `illustrative_schedule`: full-payment count and amount, the **partial final payment**, completion month, total contractual repayment, and explicit statements that the projection holds revenue constant and is not a guaranteed payment or duration. This is the field whose absence produced the error in D-029 — the gate report computed `remittance × duration` because nothing said the last payment was smaller. The disclosure exists so no reader repeats it.

**No research import into production.** `backend/money.py` re-implements the rule rather than importing `rbf_sim.settlement`; the research package is independent of the backend and must stay so. Seven cross-layer parity fixtures — including ties in both rounding directions — run the same inputs through both layers and require identical results. That is what keeps two implementations of one rule from drifting.

**`round()` audit — every monetary use classified.** Replaced: `financing_engine` advance / cap / remittance / scenario revenue / scenario remittance; `ml_engine.credit_limit`; `database` seeded credit limit. **Deliberately not replaced:** averages and medians of revenue (statistics *of* money, not contractual terms), and all ratios, probabilities, AUC and percentages. Changing those would be churn, and the instruction was to replace contractual money only.

**Research artifacts did not move.** `baseline_v2.json`, `baseline_v2_canonical.json` and `validation_v1.json` are byte-identical (`b09ae1f7…`, `264d319b…`, `a1b439c2…`); the `research/` tree is untouched by this commit; 629 simulation tests pass. `rbf_sim` has no backend dependency, so no registered finding is reachable from this change.

**Consequence:** backend tests 119 + 6 xfailed → **158 passing, 0 xfailed**. All six xfails converted, with before/after values written into the assertions so the correction cannot be silently reverted.

---

### D-029 — Cap-overshoot diagnostic: no overshoot exists; a rounding-rule divergence does
**Date:** 2026-08-07
**Status:** **DIAGNOSIS. Superseded by D-030, which applies the correction.** Retained unedited: the wrong claim, its correction, and the evidence are the record.

**Correcting my own earlier report.** The research-foundation gate report claimed `financing_engine.py` over-collects in 100% of structures, worst case 36,000,000 VND / 5.77% of the cap. **That was wrong**, and the error was mine: it computed the total as `duration × periodic_remittance`, which assumes every payment is full-size. The RBF contract clips the final payment to the remaining balance, so the last payment is partial and the total lands exactly on the cap. The figure measured my inference, not the code.

**There is no cap overshoot.** Searched systematically — 3,962 realistic whole-VND structures (10M–1B VND, both tiers) plus 2,832 adversarial ones (half-đồng boundaries, advances to 9.9×10¹¹, revenues down to 1 VND, requested amounts of 1/7/333/1.5/2.5 VND, factor rates engineered to land caps on exact halves):

| | Result |
|---|---|
| Structures where settled total exceeds the cap | **0 of 6,794** |
| Structures where product duration disagrees with integer-VND settlement | **0 of 3,962** realistic |
| Completed schedules landing exactly on the integer-VND cap | all |

The 45 duration disagreements found in the adversarial sweep occur only at revenues **below 500 VND/month** — degenerate inputs, and they resolve to the same rounding-rule cause below.

**What is real — a rounding-rule divergence between the two layers.** `financing_engine` uses Python's `round()`, which is **banker's rounding** (ties to even). The centralized policy in `rbf_sim/settlement.py` documents **ROUND_HALF_UP**. At an exact tie the two disagree.

**Minimal reproducible case**

```
revenue                       2,500 VND      (smallest whole-VND case)
advance_pct_of_annual_revenue 0.15
raw advance = 2,500 × 12 × 0.15 = 4,500.0    exact in binary — no float error
product   round(4500, -3)     = 4,000        banker's, ties to EVEN
policy    ROUND_HALF_UP       = 5,000
divergence                    = 1,000 VND
```

**At realistic scale**

```
revenue                       100,002,500 VND
raw advance                   180,004,500.0  exact in binary
product recommended_amount    180,004,000
policy  recommended_amount    180,005,000    divergence  +1,000 VND
product repayment_cap         207,004,600
cap under policy advance      207,005,750    divergence  +1,150 VND
periodic_remittance            8,000,200 VND
base_case_duration            26 months
cumulative before final       207,004,600 → final payment partial
total paid                    = cap exactly,  OVERSHOOT 0 VND
```

**Classification.** Cause is the **rounding rule**, not binary floating point (the value is exactly representable) and not contract logic (the cap invariant holds). **Deterministic** — 200 identical calls give one result. **Density: ~1 in 10,000** whole-VND revenues (100 in a 1,000,001-wide band). Surface: **API output and UI display** of `recommended_amount` and `repayment_cap`; *not* internal settlement, *not* scenario projections, *not* registered findings — `rbf_sim` is independent of the backend and its results are untouched.

**Two further gaps found by the same diagnostic:**
- Product money is `float`, not integer đồng (`repayment_cap = 248400000.0`).
- The API emits `(cap, remittance, duration)` with **no `final_payment` field and no statement that the last payment is partial**. A consumer who multiplies overstates the total by up to one remittance — which is exactly the mistake my earlier report made, so the disclosure gap is demonstrably misleading in practice.

**Why this is not being fixed here.** It is material by the standing rule: **> 1 VND and it changes a displayed financial term.** Financial behaviour is not changed without approval. Six strict-`xfail` tests record each defect precisely; `strict=True` means the suite fails if any is silently fixed without removing the marker, so the record cannot rot in either direction. A committed *red* test was rejected as the alternative — it trains people to ignore failures.

**Recommended sequence when approved** (matches D-024's established order): define the cap under the centralized policy → quantize the candidate with documented ROUND_HALF_UP → compute the exact remaining integer balance → pay `min(quantized, remaining)` → final payment is the exact remainder → cumulative never exceeds the cap. Belongs in the UI-integration commit, since it changes displayed terms and the Simulation Lab renders them.

**Consequence:** backend tests 71 → 119 passing + 6 xfailed. 48 new parity tests pin the cap invariant, monotonicity, non-negativity, exact-cap completion, zero-revenue, decline, growth, over-large final payment, long tiny-payment schedules, and scenario rows.

---

### D-028 — Backend no longer depends on an untracked model artifact
**Date:** 2026-08-07
**Raised by:** Hoang — *"a clean checkout must not claim backend reproduction while relying on a local `.pkl` produced under another scikit-learn version."*

**How the model is obtained.** It is never committed: `.gitignore` excludes `*.pkl`. Production trains its own at deploy (`railway.toml` → `train_model.py --skip-if-exists`) from `generate_data.py`, so the artifact is always built by the interpreter and scikit-learn that will consume it. A clean checkout has **no model**, by design.

**The defect.** `ml_engine.load_models()` wrapped only `joblib.load` in `try/except`. A pickle from a different scikit-learn **unpickles successfully and raises at first use**, because estimator attributes are added or renamed between minor versions. The guard therefore caught the easy failure (file absent) and missed the dangerous one (file present, unusable) — which surfaced during the previous gate as a *collection error that took down the entire backend suite*, and in production would surface as a 500 from a request handler. `database._seed_sellers()` had a second, weaker copy of the same guard, so an unusable artifact crashed app startup outside either.

**Three classified outcomes, none of which crash and none of which misreport:**

| Condition | `reason` | Behaviour |
|---|---|---|
| No `.pkl` present | `artifacts_absent` | Heuristic; informational log naming `train_model.py` |
| Present, unreadable | `artifact_unreadable` | Heuristic; warning with the exception |
| Loads, cannot predict | `artifact_incompatible` | Heuristic; warning naming the runtime scikit-learn |

Every artifact is **smoke-tested against a fixed feature row at load time**. Loading is not evidence of usability, so usability is what gets checked.

**Honest labelling, which is the same principle as D-026.** A heuristic score now reports `model_version: "heuristic-fallback-v1"` and `scoring_path: "heuristic"` — never `v1.0-synthetic`. `/api/health` said *"RF+LR ensemble v1.0 (synthetic baseline)"* unconditionally, including when no model existed; it now describes what is actually loaded. Reporting the model's label while the fallback ran is the artifact contradicting its own description, which is the defect this project exists to avoid.

**Tests no longer depend on anyone's artifacts.** `conftest.py` points `RBF_MODEL_DIR` at an empty temp directory before import, so the suite runs in clean-checkout state. The incompatible-artifact case is exercised with objects that unpickle cleanly and raise on use — the same *shape* as a cross-version failure, without needing two scikit-learns installed. The acceptance path is covered by a deterministically-built throwaway ensemble (seed 20260803) that is created in `tmp_path` and never committed. **No pickle was committed to make anything pass.**

**Environment.** `scikit-learn>=1.4.0` had no ceiling — the exact condition that lets a build/consume mismatch appear silently. Now bounded (`>=1.9.0,<1.10`), with numpy/pandas/joblib bounded likewise, and Python `>= 3.11` documented. `backend/ENVIRONMENT.md` answers the four questions in full.

**Verification limit, stated rather than buried.** The pinned set was **not installed during this gate**: verification ran on Python 3.10, where scikit-learn 1.9 cannot be installed (`Requires-Python >=3.11`). What was verified is that the suite passes with **no artifact present** — the clean-checkout path, which the pins do not affect — and that all three failure modes are classified correctly under scikit-learn 1.7.2. **The pinned combination needs one confirming install-and-test run on a Python 3.11+ machine.**

**The model is not necessary.** Everything downstream of the PD estimate is deterministic arithmetic in `financing_engine.py`; `research/rbf_sim/` does not import the backend or scikit-learn at all. Both independence claims are asserted by test, by source inspection, so they cannot rot silently.

**Consequence:** backend tests 56 → 71. Mutation-tested: removing the smoke test, always reporting the ensemble version, failing to clear the globals on rejection, and dropping the `RBF_MODEL_DIR` redirect are each caught.

---

### D-027 — Canonical, checksummable results; wall-clock moved to provenance
**Date:** 2026-08-07
**Raised by:** the research-foundation gate report; prioritized by Hoang as *"worth fixing but cheap."*

**The problem.** `results/baseline_v2.json` embedded `date.today()`. Every quantity in it reproduced bit-for-bit, but the *file* did not: two runs of identical code, configuration and seeds produced two different checksums. A result that cannot be checksummed cannot be cited by checksum, and "reproducible" then rests on someone diffing 1,553 lines by hand — which is exactly what the gate report had to do to prove nothing changed.

**Decision.** Split the artifact in two.

| | Contents | Expected to vary? |
|---|---|---|
| `baseline_v2_canonical.json` | the analytical result + deterministic identity metadata: schema version, spec version, generator fingerprint, scenario-config hash | **No.** Byte-identical for identical code, config and seeds. |
| `baseline_v2_provenance.json` | wall-clock UTC, git commit, tree-dirty flag, Python/NumPy versions, platform, and the canonical file's SHA-256 | **Yes.** That is its job. |

**`baseline_v2.json` is preserved unmodified** as historical evidence and is no longer written by `run_baseline.py`. A test asserts it still exists, still carries its date, and still agrees with the canonical artifact on **every** number — that equivalence is what licenses citing the canonical one instead.

**Why `source_commit` is in provenance, not canonical.** Hoang's list named it as canonical metadata; putting it there is self-defeating. Committing the artifact changes `HEAD`, which changes what the next run emits, so the file could never be both committed and reproducible. Code identity is captured instead by `generator_fingerprint`, a SHA-256 over the generating source. That is strictly stronger here: stable across commits that do not touch the generator, and changing exactly when the generator changes. The commit is still recorded — in provenance.

**A real defect the tests caught.** The first implementation was stable across runs but **not idempotent under round-trip**. `post_shock_recovery` uses integer keys `{6: …, 12: …}`; `sort_keys=True` sorts them numerically on write (6, 12) and lexicographically after re-reading, since JSON keys are strings ("12", "6"). A consumer who loaded the artifact, re-encoded it, and checksummed the result would have got a hash different from the file's own — defeating the purpose. Keys are now normalised to `str` before encoding, making the encoding a fixed point: `canonical_bytes(json.loads(canonical_bytes(x))) == canonical_bytes(x)`. This was found by a test written to check exactly that property, not by inspection.

**Encoding.** `sort_keys` removes dict-ordering dependence; `ensure_ascii` removes locale/encoding variation; floats use shortest round-trip `repr`, asserted on the running interpreter rather than assumed across versions.

**Verification.** Two full baseline runs produce byte-identical canonical files (SHA-256 `264d319b…ac5a7849`); the provenance sidecars differ only in `run_utc`. Numerical comparison against the frozen `baseline_v2.json`: **0 differing leaves.** No finding changes.

**Consequence:** 25 tests added (`rbf_sim/tests/test_canonical.py`). Simulation tests 604 → 629. `RESULTS_REGISTRY.md` gains the canonical artifact and its checksum. `validation_v1.json` is **not** migrated in this commit — it has the same `_meta.date` issue and should follow the same split when next regenerated; recorded so it is not forgotten.

---

### D-026 — Withdrawn 0.92 benchmark purged from every public surface (P0-2 closed)
**Date:** 2026-08-07
**Raised by:** Hoang, reviewing the research-foundation gate report.

**The finding, in his words:** *"`backend/main.py:401` serving `training_baseline.auc = 0.92` is not a leftover — it's the original sin of this project reappearing. The entire Phase 0 finding was that the deployed artifact contradicted the documentation."*

That is the correct reading, and the baseline commit understated it by filing P0-2 as merely "partial". The README withdrew the figure with the circularity arithmetic while `GET /api/model/status` continued to hand it out on request. A reviewer who read the README and then curled the API would have found the two disagreeing — which is precisely the defect PHASE0_AUDIT.md was written about, reproduced by us, after we had documented it.

**Decision.** The withdrawn benchmark is removed from every public surface. `training_baseline.auc` is **`null`**, accompanied by `validation_status: "withdrawn"`, `reason: "synthetic circular-label benchmark"`, and a disclaimer carrying the circularity arithmetic.

**Why `null` rather than deleting the key.** Removing `auc` entirely would break any consumer reading it and, worse, would make the withdrawal *invisible* — an absent field reads as "not implemented yet", not "retracted". A null beside an explicit `validation_status` states the retraction rather than hiding it. `withdrawn_value: 0.92` is retained under a name that cannot be mistaken for a current result, so the record of *what* was withdrawn survives.

**Scope — what was deliberately NOT withdrawn.** The UCI cross-validation (0.80 German Credit, 0.77 Taiwan default) is a different claim on **real borrowers with real adjudicated outcomes**. It validates the method, not the merchant model, and the README already says so. A test asserts it survives, so an over-broad future purge cannot take it as collateral damage.

**Surfaces changed.** `backend/main.py` (`/api/model/status`); `backend/demo_learning_loop.py` (printed "Synthetic train AUC: 0.92 [for reference]" — a withdrawn figure offered as a reference point is still a claim); `frontend/index.html` ("a synthetic baseline today"); `README.md` §Learning loop and the GXS "what must never be claimed" line, both of which still described the figure as extant.

**Enforcement.** Four API-level tests plus a source-level scanner, `backend/tests/test_no_withdrawn_claims.py`, which walks every shipped surface and fails on any unexplained `0.92`. Each permitted occurrence must be entered in an allowlist **with a written reason**. P0-2 was originally missed because the figure lived in three places and no one enumerated them; enumeration is now a test rather than an intention. The scanner also asserts the audit trail *retains* 0.9098 vs 0.9182 — a withdrawal that deletes its own evidence is not auditable.

**Not in this repository.** `docs/GXS-Stage2-Proposal.md` still contains the old framing. It is gitignored and therefore not published through the repo, but it is competition material and must be corrected before submission. Recorded here rather than edited, because `docs/` is outside the tracked tree.

**Consequence:** backlog P0-2 moves from *partial* to **done**. Backend tests 48 → 56.

---

### D-025 — Shipped default credential removed; dashboard fails closed
**Date:** 2026-08-06
**Raised by:** integration review, at the baseline commit.
**Approved by:** Hoang.

**The problem.** `patches/README_corrections.patch` rewrote the README to say *"Set `DASHBOARD_PASSWORD` before running. There is no default value in the repository."* The corresponding code change was never made: `backend/main.py` still read `os.environ.get("DASHBOARD_PASSWORD", "demo2025")`, and `start.sh` / `start-dev.sh` printed the password on startup. Applying the patch as instructed would have made the repository's own documentation false — in a project whose central claim is that documentation, code, and results agree.

**Why it mattered more than a doc bug.** A fallback credential in a public repository is a published credential. It was also reachable: `DASHBOARD_PASSWORD` was consulted at import time, so any deploy that forgot the variable accepted `demo2025` and **failed open, silently**.

**Decision.** Remove the default. An unset `DASHBOARD_PASSWORD` now **disables dashboard login** and returns `503` with a message naming the missing variable; it does not fall back to any value. The rest of the API and the health check continue to serve, so a misconfigured deploy fails **closed and visibly** rather than open and quietly.

**Alternative rejected.** Raising at import time would have taken the whole service down — including `/api/health` — over a dashboard-only setting, converting a configuration mistake into an outage.

**Consequence.** `backend/main.py` auth block; `conftest.py` supplies the suite's own password so exactly one password literal exists in the test tree; `test_api.py` reads it from the environment. One test added — `test_login_rejects_the_withdrawn_default_credential` — which asserts `demo2025` is refused, so the README's claim is now enforced by test rather than by intention. **Backend tests 47 → 48.** No research code, result, or proposition is touched.

**Scope note.** This is outside the monetary correction that motivated this commit. It is included because the instruction to apply the README patch is what introduced the false claim, and shipping a knowingly untrue statement was the worse option.

---

### D-024 — D-023 APPROVED and applied; monetary policy centralized
**Date:** 2026-08-06
**Approved by:** Hoang, at repository transfer.
**Status of D-023:** its "PROPOSED, not applied" caveat is now **discharged**. D-023 is retained below unedited as the reasoning that produced this change.

**What was applied.**
1. **One module owns money.** `rbf_sim/settlement.py` holds the settlement policy, the rounding rule, both completion concepts, and the float guard. There is no longer a monetary constant anywhere else.
2. **Operational layer = integer đồng.** `settle_payments()` quantizes each payment with `Decimal` under an explicit `ROUND_HALF_UP` rule, then clips to the remaining cap — **in that order**. Rounding therefore cannot breach the cap, and the completing payment is an exact remainder rather than a rounded one. `Decimal` is used deliberately instead of `round()`, whose banker's rounding would have silently applied a rule other than the documented one; a test asserts the difference.
3. **`eps = 0` by construction**, not by tolerance. `SettlementPolicy` rejects a fractional `epsilon_vnd` outright — a fractional epsilon is the exact defect D-023 identified.
4. **Analytical layer keeps no epsilon.** `mathematically_complete()` is exact. The `tol = 0.5` defaults and the tests' `CAP_TOL = 1.0` become one `FLOAT_GUARD_VND = 1e-6`, documented as a representation-error guard and nothing else.

**Evidence that the guard is a guard, not a policy.** Re-measured in this repository across 3,000 paths spanning all ten baseline scenarios, float payments recomputed against exact `fractions.Fraction` arithmetic:

| Quantity | Measured |
|---|---|
| worst per-payment deviation | 9.2387 × 10⁻⁸ VND |
| worst cumulative-sum deviation | 8.9407 × 10⁻⁸ VND |
| paths failing to reach an exactly-reached cap at `tol = 0` | 0 of 3,000 |

`1e-6` covers that with ~11× margin and is 10⁶ times **smaller** than 1 VND — it cannot absorb a real monetary shortfall, which is the property that distinguishes a numerical guard from a settlement rule.

**Impact on registered results: zero — verified, not assumed.** `baseline_v2.json` and `validation_v1.json` were regenerated after the change and compared leaf-by-leaf against the registered artifacts. **One differing leaf: the embedded run date.** Because nothing changed, the registered files are **retained unmodified** rather than rewritten — versioning an output that is bit-identical apart from a timestamp would create churn while destroying the ability to checksum it.

**Tests: 461 → 604.** The 461 inherited tests pass unchanged, *including* with `CAP_TOL` tightened by a factor of 10⁶ — direct evidence the old tolerance was never load-bearing. 143 new tests cover the settlement layer. The new suite was **mutation-tested** rather than merely observed green: clipping before rounding (25 failures), `ROUND_DOWN` instead of half-up (4), reintroducing a `0.5` default (1), adding an epsilon to mathematical completion (3), and removing the cap clip (48) are each caught.

**Consequence:** spec amendment A-7 adds the current state to §10.11. `DERIVATIONS.md` is **byte-identical** — no proposition moved. The `ε` table at `ρ*` is reclassified from engine behaviour to declared-policy sensitivity.

**Known limitation, stated rather than fixed.** The engine still computes in floating point and quantizes at the boundary; it does not carry `Decimal` end-to-end. That is sufficient for the operational guarantee actually claimed (integer settlement, exact cap) and is not sufficient to call the analytical layer exact-arithmetic. Where exactness matters — the P7 boundary — the result is established analytically, not by running the simulator, as D-022 already required.

---

### D-023 — Cap tolerance is a floating-point workaround; integer-VND correction PROPOSED, not applied
**Date:** 2026-08-04
**Question posed:** is the ~1 VND cap tolerance (a) an intentional whole-đồng settlement rule, or (b) merely a floating-point workaround?

**Verdict: (b), a floating-point workaround.** Five pieces of evidence:

1. **Inconsistent between modules.** `0.5` in `metrics.duration`, `metrics.incomplete_recovery`, `contracts.rbf_duration`; `1.0` in `tests/test_derivations.py`. A settlement policy would be one constant in one place.
2. **Absent from the frozen specification.** `METHODOLOGY_SPEC.md` — which governs all financial behaviour — contained zero mentions of tolerance, settlement, rounding, or epsilon before this entry.
3. **Over-provisioned by ~8.4 × 10⁶.** Measured worst-case per-payment deviation from exact rational arithmetic across 300 strong-seasonality paths: **5.96 × 10⁻⁸ VND**. The tolerance is 0.5 VND.
4. **It is a default argument**, not a named contract parameter alongside `A`, `r`, `f`.
5. **It is not shaped like a whole-đồng rule.** A genuine one would *round payments to integer đồng*; this compares cumulative sums within a slack band while emitting fractional-VND payments freely.

**Impact of correcting it: zero.** Duration and incomplete-recovery were recomputed at `tol = 0.5` and `tol = 0.0` across all ten baseline scenarios × 300 paths. **0 of 10 scenarios changed**; durations identical to four decimal places; incomplete recovery 0.0% under both.

**Correction to my own earlier report.** I previously stated the boundary flip occurs at T = 213. That used the *test module's* `CAP_TOL = 1.0`, not the engine's `0.5`. The engine-relevant flip is **T = 221**. The discrepancy is the inconsistency in evidence item 1, now surfaced rather than reconciled away.

**Proposed correction — NOT APPLIED, awaiting approval.** Represent money as integer VND minor units (the đồng has no circulating subunit): `p_t = min(round(r·B_t), cap − paid)` with an explicit, documented rounding rule; cap comparison becomes exact and `eps` becomes 0 by construction. A settlement tolerance may then be *reintroduced deliberately* as a declared policy parameter and swept as sensitivity. **Not applied because it changes financial code**, and financial behaviour is not to be changed silently — even where the measured impact is nil.

**Consequence:** spec amendment A-6 adds §10.11 defining both completion concepts. `DERIVATIONS.md` §P7 gains the two-concept table with flip months by `ε` (213 / 221 / 266 / 373 / never). Four tests parameterise the flip point over `ε` and assert the tolerance changes no registered result. The engine's behaviour is **unchanged**.

---

### D-022 — P7 boundary: completion requires ρ > ρ*, strictly
**Date:** 2026-08-04
**Raised by:** Hoang, final review before repository transfer.

**The error.** D-020's corrected geometric characterisation still wrote `completion ⟺ ρ ≥ ρ*`. The weak inequality is wrong at the boundary.

**Why.** Completion is a **finite-time** property: it requires a finite `T` with `r·Σ_{t≤T} B_t ≥ F·A`. With the implementation's indexing (`B_t = B₀ρ^t`, `t = 0, 1, …`, verified against `geometric()` which runs `k in range(n)`), the partial sum is `S_T = B₀(1−ρ^{T+1})/(1−ρ)`. Since `ρ^{T+1} > 0` for every finite `T`, `S_T < S_∞` **strictly, always**. At `ρ = ρ*` the infinite sum equals the cap exactly, so every finite partial sum is strictly below it: repayment approaches the cap asymptotically and **never attains it**. Completion in the limit is not completion.

**Corrected statement:** `completion in finite time ⟺ ρ > ρ*`, where `ρ* = 1 − r·B₀/(F·A)`. Below `ρ*`, lifetime cumulative revenue is insufficient. **At `ρ*`, it is an asymptotic boundary case that does not complete in finite time.**

**Computed at `ρ* = 11/12`.** Shortfall `F·A − r·S_T`: 13,629,101.44 at `T=24` · 594,400.32 at `T=60` · 18,303.60 at `T=100` · 3.05 at `T=200` · 0.04 at `T=250`. Monotone decreasing, never zero.

**Honest limitation, now asserted by test.** The engine tests cap attainment with `CAP_TOL = 1 VND`. At `ρ = ρ*` the shortfall drops below 1 VND at **T = 213**, so the *numerical* check reports "complete" from month 213 even though the contract mathematically never completes. That is a property of the tolerance, not a counterexample — and it is the reason this boundary had to be settled analytically rather than by running the simulator. Simulation could not have found this; at the boundary it actively reports the wrong answer.

**Consequence:** `DERIVATIONS.md` §P7 gains a finite-time completion definition, the strict inequality, the indexing convention it depends on, the shortfall table, and the tolerance caveat. Ten tests added (indexing convention, exact equality of `r·S_∞` and cap, strict sub-cap partial sums at six horizons, engine-level non-completion, strict straddle, tolerance flip at exactly 213, monotone shortfall). **457 tests pass.** No empirical result changes — no scenario in the library sits at or near `ρ*`.

---

### D-020 — Correct Proposition 7; positive revenue is not sufficient for completion
**Date:** 2026-08-04
**Raised by:** Hoang, reviewing the analytical backbone.

**The error.** `DERIVATIONS.md` §P7 Corollary (b) claimed "decline alone cannot cause incomplete recovery," justified by the parenthetical "*revenue bounded below by some B_min > 0, however small (any decline that does not reach zero)*". **That parenthetical silently equates two different conditions.** A geometrically decaying path is strictly positive in every period yet is *not* bounded away from zero, and its lifetime sum is finite. If that finite sum falls below `F·A/r`, the cap is unreachable — with no zero-revenue month, no maturity rule, and no horizon limit.

**Corrected general statement.** Completion over applicable horizon `H` holds **iff**
`r · Σ_{t≤H} B_t ≥ F · A`.
Four causes of incomplete recovery: (1) closure/zero revenue, (2) binding maturity or write-off, (3) finite evaluation horizon, (4) **strictly positive but sufficiently fast-decaying revenue with inadequate lifetime cumulative sales.** Cause 4 was missing.

**Corrected logical status.** "Bounded away from zero" is **sufficient, not necessary**. "Strictly positive" is **not sufficient**. `Σ B_t = ∞` is sufficient and strictly weaker than boundedness — the harmonic path satisfies it and violates boundedness.

**Geometric threshold.** For `B_t = B₀ρ^t`: completion iff `ρ ≥ ρ* = 1 − r·B₀/(F·A)`. At `A = B₀ = 100M`, `F = 1.20`, `r = 0.10`: `ρ* = 11/12 ≈ 0.9167`. At `ρ = 0.90` the contract never completes despite positive revenue forever.

**Why the simulation missed it.** Every declining scenario in the library steps down to a *constant floor* — bounded away from zero — so all of them diverge and complete. **The scenario library contained no decaying-to-zero path.** 447 passing tests could not have caught this, because none of them quantified over the space of paths. This is the clearest possible argument for the analytical layer: a theorem quantifies over all paths; a scenario library covers only the paths someone thought to write.

**Consequence:** `DERIVATIONS.md` §P7 rewritten to the general criterion. Nine adversarial tests added (fast/slow geometric decay, harmonic divergence, exact boundary, straddle, horizon-invariance of the failure). Empirical boundary numbers are **unchanged**; their *explanation* is corrected. `CORRECTED_CLAIMS.md` §5 updated. No claim survives that decline alone cannot cause incomplete recovery.

---

### D-021 — Working title revised to separate general theory from Vietnamese motivation
**Date:** 2026-08-04

**New title:** *Revenue-Contingent Financing Under Volatile Sales: A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers.*

**Reason:** the prior title implied Vietnam-specific empirical calibration that does not exist — no parameter is externally sourced. The revised title places Vietnam where it belongs (problem motivation) and announces both layers: the propositions are general and path-independent; the numerical parameters are explicitly illustrative. Supersedes D-002.

**Consequence:** propagated across all documents. Paper, poster, deck, README, and abstract adopt it.

---

### D-018 — RBF-G removed from public comparisons; retained as a rejected design
**Date:** 2026-08-04

**Decision:** RBF-G is removed from all public-facing comparisons, selling points, and the product interface. It is preserved in this log and in `DERIVATIONS.md` §P-RBF-G as a **rejected design**.

**Reason:** the guardrail floor is provably unreachable. It binds only when observed revenue is below `μ·R₀ = 0.25·R₀`, but applies only when revenue is at or above `h·R₀ = 0.50·R₀`. For `μ ≤ h` the conditions are mutually exclusive on every possible revenue path. It is not a weak guardrail — it is not a guardrail.

**Not done:** the parameters were **not** retuned after observing results. A corrected design requiring `μ > h` is named as future work and does **not** enter the frozen analysis as if it had been preregistered.

**Consequence:** RBF-G stays in the code and test suite (its behaviour is now pinned by four tests) but is excluded from findings, the paper's comparison tables, and the product UI.

---

### D-019 — Add an analytical backbone; reclassify all claims
**Date:** 2026-08-04

**Reason:** none of the thirteen parameters is externally calibrated, so numerical magnitudes cannot be estimates of anything real. Deriving the structural properties formally means the simulations *illustrate proven relationships* rather than appearing to estimate real-world impact — which is both more honest and a stronger contribution.

**Seven propositions derived and test-validated** (`DERIVATIONS.md`, `test_derivations.py`): P1 burden ≡ `r` until the capped payment · P2 fixed-burden elasticity is exactly −1 · P3 cap reached iff `S_k ≥ A·f/r` · P4 RBF leads recovery iff mean revenue `> B* = P/r` · P5 underreporting scales recovery by `ω`, duration by `1/ω` · P6 multiple is `f` path-independently while APR is path-dependent · P7 incomplete recovery iff `S < A·f/r`, caused only by zero revenue, maturity, or horizon.

**Two prior results are now explained rather than merely observed:**
- **R-012's sign reversal** is P4 plus integer rounding. When `C/(r·B̄)` is not an integer, `N` rounds up, so `B* < B̄` strictly and RBF leads on recovery *even at exactly baseline revenue*. In `baseline_v2`, `12.37 → 13` gives `B* ≈ 0.951·B̄`. **This was an artifact of the matching rule, not an economic finding** — a misreading avoided.
- **The recovery boundary** is P7: decline alone can never cause incomplete recovery given positive revenue and enough time.

**Consequence:** claims are now partitioned into five classes — mathematical properties, simulation results, sensitivity results, product implications, and questions the project cannot answer. Every public claim must declare its class. Illustrative magnitudes are never described as estimates for Vietnamese sellers.

**Test-driven corrections during this work, recorded:** three successive attempts were needed to state the RBF-G consequence correctly (full equality → pointwise dominance → invariant against `r·B_t`); a P4 corollary test was written on parameters where the rounding case does not arise. In every instance the **test was corrected, not the proposition**, and the proposition itself never changed.

---

### D-014 — Excel removed from the project entirely
**Date:** 2026-08-03
**Source:** Hoang — "my Excel project is completely separate from RBF and this research."

**Decision:** every Excel-related dependency, assumption, deliverable, blocker, and reconciliation task is removed. No file is awaited. The assumption-reconciliation table is deleted rather than left pending.

**Consequence:** all RBF parameters must come from the repository, credible external literature, a documented derivation, or be labelled illustrative with sensitivity analysis. `CORRECTED_CLAIMS.md` §8 classifies all thirteen parameters accordingly. **None is classified "externally sourced"** — the project's defence is sensitivity analysis, not claimed calibration, and saying so is more honest than implying a calibration that does not exist.

---

### D-015 — Separate financing *price* from financing *structure*
**Date:** 2026-08-03
**Trigger:** The previous checkpoint claimed "RBF costs ~2.3× the interest of a conventional loan." That conflated two independent things.

**Alternatives considered:** keep the claim with caveats; drop the cost comparison; separate price from structure and measure each independently. ← **chosen**

**Reason:** the 39.90% implied APR is a consequence of the illustrative `f = 1.20` taken from `financing_engine.py` — not a property of revenue-contingent repayment. Solving for the cap that equalizes effective cost against the 18% benchmark gives **f\* = 1.0945** (19.54% vs 19.5618%). The same revenue-contingent structure, repriced, costs the same as the conventional loan. The original claim was therefore a statement about one parameter dressed up as a statement about a financing type.

**Consequence:** Benchmark A holds price constant and varies structure; the cap sweep holds structure constant and varies price. Public phrasing is fixed: *"At the illustrative 1.20× cap, the simulated RBF contract is substantially more expensive than the 18% loan. This is a pricing result, not an inherent property of revenue-based repayment."* The equal-cost cap must accompany any cost comparison.

---

### D-016 — Restrict the underreporting claim to contractual invariance
**Date:** 2026-08-03

**Was:** "Fixed payments are immune to underreporting — a genuine structural advantage."
**Now:** *"Scheduled fixed payments are invariant to revenue reporting, while RBF remittances decline approximately one-for-one with reported revenue. The simulation does not establish that actual fixed-loan recovery is immune to default."*

**Reason:** the model contains no default, insolvency, liquidity-constrained nonpayment, or business-closure-driven missed payment for the fixed arm. A fixed schedule is invariant *contractually* — the borrower still owes it — but nothing in this simulation shows the lender *collects* it. Claiming immunity of realized recovery was an unsupported leap from contract terms to outcomes, and would have been the easiest claim in the project to attack.

**Consequence:** the fixed arm's `RR` figures describe *scheduled* recovery, not realized recovery, and are labelled as such. A default model was **not** added — the user's constraint against uncalibrated default modeling is respected, and the limitation is stated instead.

---

### D-017 — Remittance basis = net sales; identity scope fixed
**Date:** 2026-08-03

**Alternatives considered:** GMV; net sales after returns; cash receipts after platform fees. ← **net sales chosen**

**Reason:** `gmv = orders × AOV` is an exact accounting identity. Returns, discounts, cancellations, taxes, and platform fees are **deductions from** GMV, not components of the identity — folding them in would have been mathematically wrong. Separately, the *contractual* remittance base is a different question from the identity, and platforms settle after returns, so remitting on GMV would charge a share of money the seller never receives.

**Consequence:** spec amendment A-1. Materially changes results — baseline re-run as `baseline_v2`, matched benchmark 12 → 13 months, implied APR 37.87%. `baseline_v1` superseded, retained for audit trail. `platform_fee_rate` defaults to 0 and is classified *arbitrary / awaiting justification* so no unsourced fee is baked in. Surfaced R-012: the provider-recovery effect reverses sign under non-declining revenue.

---

### D-011 — Add a base-case coherence constraint; treat advance sizing as a research question
**Date:** 2026-08-03
**Trigger:** Spec verification, run before any analysis, found the distress metric degenerate under plausible parameters.

**Alternatives considered:**
1. Loosen the distress definition until the arms separate.
2. Pick margin/cost parameters that make the comparison work.
3. Add an explicit coherence constraint, report the incoherent region as a result, and treat advance sizing as a research question. ← **chosen**

**Reason:** Options 1 and 2 are threshold-shopping and parameter-shopping respectively — the precise failure mode D-004 exists to prevent, and doing either *after seeing* that the metric was degenerate would be indefensible. Option 3 keeps the frozen definition intact and converts the problem into information: the region where no financing structure is affordable is a real bound on the population RBF can serve, and it is worth reporting.

The underlying cause is that `financing_engine.py` sizes the advance off revenue alone, with no margin or fixed-cost input, so repayment capacity is never tested. Under illustrative parameters the recommended advance is roughly double an indicative serviceable bound.

**Consequence:**
- *Research:* `METRIC_DEFINITIONS.md` §3.4 added **before** first analysis run and logged as such. The incoherent parameter region becomes a reported robustness result rather than a silent exclusion.
- *Product:* a candidate design change — size the advance off gross profit, not revenue — with a research result behind it. This is the clearest example so far of evidence driving product, which is the project's stated goal.
- *Honesty:* the finding is marked **provisional** until `m` and `F` are sourced in Phase 2. It is not quotable until then, and `RESULTS_REGISTRY.md` R-003 marks it ⚠️ accordingly.

---

### D-008 — Remove `owner_name` and `phone` from the submission path
**Date:** 2026-08-03
**Alternatives considered:** keep (they are excluded from `FEATURES` and never scored); keep but mask in exports; remove entirely. ← **chosen**

**Reason:** They are correctly never used as model inputs, but they are stored alongside the assessment, exported to CSV, and presented inside the credit-application flow on the live form. They serve no research purpose. Collecting identifiable personal data in an underwriting submission is indefensible under scrutiny regardless of downstream use.

**Consequence:** `models.py`, the form, DB writes, and CSV export change. Privacy notice is rewritten. Removes a whole category of hostile question.
