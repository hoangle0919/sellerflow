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

### D-045 — Final line edits: restatements, retired verification script, RBF-G scope, burden denominator
**Date:** 2026-08-10
**Raised by:** the final read-only audit of `b1cef86`. **Artifact/reproducibility gate PASSED; Gate A narrowly failed on a dozen sentences.**
**Status:** APPLIED on `publication-package`. No new framework, scanner, artifact, simulation or broad rewrite. No financial change.

**1. `S_H ≥ Θ` restated without limiting `H`.** Two places still called it the general or complete criterion: the §"complete characterisation" line and the logical-status block. Both now state the binding rule — `completion ⇔ ∃ finite t ≤ H with S_t ≥ Θ` — and note that the reduction to `S_H ≥ Θ` holds **only for finite `H`**, because `S_k` is non-decreasing. The lifetime case is where it fails and is why the rule is written this way.

**2. Current-engine language in the tolerance section.** "The 1-VND-scale tolerance **in the engine**", `0.50 *(engine default)*`, and an instruction telling the paper to report operational completion at `ε = 0.5` all described pre-A-7 behaviour. Since D-024 the operational layer settles in **integer đồng with `ε = 0` by construction**; `FLOAT_GUARD_VND = 1e-6` is analytical representation-error protection and **is not a settlement tolerance**. The `ε` table is retained, relabelled as **hypothetical declared-policy** values, and the reporting instruction now requires any such figure to be marked hypothetical.

**`research/analysis/01_verify_spec.py` retired rather than patched.** It still defaulted to `tol=0.5`. Updating the constant would have been the smaller edit and the wrong one: the script verifies `METRIC_DEFINITIONS.md` **v0.1**, which `METHODOLOGY_SPEC.md` v1.0 superseded, and describes itself as "a throwaway reference implementation — it is not the engine". R-003 already marks its output exploratory and not quotable. It is now banner-marked historical, removed from the reproduction instructions in `RESEARCH_MANIFEST.md`, and retained only so coherence constraint §3.4 has a traceable origin.

**3. RBF-G scope, in the two places that still generalised it.** `CORRECTED_CLAIMS.md` "retained as a null result" → **floor-only null / design flaw**. `RESULTS_REGISTRY.md` "F-5 must be presented as a null result" → **N-2′ is the hardship-floor null, and the live ceiling result must accompany it** (6,009 of 36,000; 6 of 10 scenarios). Also closed an unmatched strikethrough I left in the registry's limitations paragraph, where a D-040 insertion had opened `~~` without closing it and swallowed the following sentence into a struck region.

**4. R-011's incomplete-recovery list** said recovery failure "requires zero revenue, a binding horizon, or a terminal write-off". That is a closed list stated as a requirement. Replaced with the exact criterion plus the same examples marked explicitly non-exhaustive.

**5. The burden denominator, in the two places the D-044 pass missed.** `high_burden_months` still said the count is constant **"BY CONSTRUCTION"**, and a product implication said a revenue share "achieves" flat burden through a downturn. Both overstate: the contractual remittance is a fixed share of **net sales**, while the displayed count and burden use **GMV**, so they equal `r·(1 − return rate)` and move when returns move. Constant only while the net-sales/GMV ratio is fixed.

**6. Remaining live copy.** `index.html`: "if revenue stops, the cap is never reached" → permanent cessation **before completion while a balance remains**; "holds funding for verification" → marks the demonstration assessment for manual review; "verify revenue before disbursing" → verify submitted revenue before relying on the assessment. `README.md`: "gates the credit decision" → marks the demonstration assessment for review. `RESEARCH_MANIFEST.md`: the backend count said **71** in the verification table while saying 379/9 in the reproduction block — the 71 is now labelled as the historical D-028 composition and the current figure is stated.

**Suites:** 379 backend passed / 9 skipped, 629 simulation passed.

---

### D-044 — Final editorial consistency pass: active claims that survived three correction rounds
**Date:** 2026-08-10
**Raised by:** the final read-only Gate A audit of `ff470b4` — **FAIL, narrowly.**
**Status:** APPLIED on `publication-package`. **No financial change, no simulation run, no artifact regeneration.**

**The shape of this round.** D-043 corrected the completion theorem, the RBF-G null, the underwriting language and the verifier — and in several places corrected the *summary* while the *active* statement survived elsewhere in the same file. The verifier repair itself passed natively (3/5 byte-identical, 5/5 numerically equal, exit 0, cleanup confirmed). What remained was editorial.

**P7's proposition itself, not just its summary.** The proposition read `completion ⇔ S_H ≥ f·A/r` for any `H` "including the business lifetime". For a **finite** `H` that is right, and the reduction is sound because `S_k` is non-decreasing. For an unbounded lifetime it is **not**: the limit is not a partial sum. The proposition now states the finite-time criterion — `∃ finite t ≤ H with S_t ≥ Θ` — notes the finite-`H` equivalence explicitly, and marks the unconditional form superseded. D-043 fixed the criterion *below* the proposition and left the proposition itself saying the older thing.

**"For any target cost there exists an `f` attaining it."** True of the **contractual repayment target** `A·f`, which is continuous and monotone. False of **effective APR on the reference path**, which moves in steps because duration is integer-valued — so a target APR generally has *no* exactly-attaining `f`. The two statements are now separated, with the 0.02416pp residual attached to the second.

**Stale ε paragraphs.** `DERIVATIONS.md` still described `ε = 0.5` as the engine default and the integer-VND correction as "not applied" — stale since A-7 applied it. Superseded in place; the `ε` table is retained as **declared-policy sensitivity examples**, which is what it always was.

**Remaining actives.** `CORRECTED_CLAIMS.md`: one uppercase `F·A` in the ρ\* formula, and "the guardrail feature is decoration" — only the **floor** is dead. `METHODOLOGY_SPEC.md`: Benchmark B "represents a realistic alternative", and the incoherent region described as where "no financing structure is affordable" (now: fails the study's illustrative burden/coherence rule).

**Precision the registry lacked.** RBF-G differences are now stated by field — `apr_mean` **6** scenarios, `burden_mean` **6**, `recovery_ratio` **3**, `duration_mean` **1** — rather than as a bare "6 of 10". The P4 reversing condition is stated exactly (realized mean eligible base against `B* = P/r`, plus the integer-rounding qualification that makes `B* < B̄`) instead of the "non-declining revenue" label, which is not the condition.

**The ledger's universal disclaimer was flattening §1.** "Every figure is simulation output" is right for §2–§3 and **wrong for the theorem rows**, which are proved and hold for any path. Applying the simulated-output caveat to them under-claims them and mislabels their warrant; their real limitation is that a contract is not a market. The disclaimer is now class-dependent, with the one unconditional part — no observed seller data, no evidence about any seller — stated first. Source paths for S-2 and S-5 now list every field the claim asserts, rather than the one field that happened to be cited.

**The burden denominator was misstated, and this one is subtle.** `lab.py` said a revenue-share payment's burden "cannot rise when revenue falls… by construction". The contractual remittance is a fixed share of **net sales** — but the burden the Lab *displays* uses **GMV**, so it equals `r·(1 − return rate)` and **moves when returns move**. It is constant only where the net-sales/GMV ratio is fixed. The returns-spike scenario is precisely where the two denominators come apart, and the page was asserting universality over a quantity that is not universal. `DERIVATIONS.md` P1's implementation note had this right all along; the product copy did not.

**Live copy.** README: closure conditioned on permanent zero revenue *before completion while a balance remains*, with the three closure scenarios distinguished (100.0% / 76.2% / 2.0%) rather than a blanket "runs to 100%"; the guardrail split into dead floor and binding ceiling; the exact P4 threshold; and — the honest one — **the README claimed the withdrawn 0.92 "is not reported by the API"**, which is false. It is returned as `withdrawn_value`, deliberately, as audit metadata. The README is corrected rather than the API. "RBF answers the credit-underwriting half today" is removed: it is an unvalidated demonstration. `index.html` keeps the backend enum values for compatibility but displays **illustrative low/medium/high-risk tiers** instead of Approved/Conditional/Not approved, in the verdict map, the dashboard counts and the explanations; "enough signal", "exceeds the risk threshold", "credit decision" and "before disbursing" are gone, and an integrity flag now marks the **demonstration assessment for manual review**.

**Canonical metadata — decision recorded, not deferred.** Approved: **do not regenerate the five registered artifacts.** Checksums and embedded historical metadata stand. The embedded determinism sentence is superseded by D-041/D-043, the corrected reproduction claim is the only one permitted on any surface, and the regression test proving the raw field is never publicly rendered stays. `RESULTS_REGISTRY.md` no longer says "awaiting a call".

---

### D-043 — Completion-theorem edge case, remaining document contradictions, underwriting language, and a verifier that could not report its own finding
**Date:** 2026-08-10
**Raised by:** the third Codex claim audit. **Gate A round 2 failed at `f2b84f9`.**
**Status:** APPLIED on `publication-package`. **No financial formula, seed, scenario, contract, settlement rule or registered numeric result changed. No registered artifact rewritten.**

**1. The completion theorem was wrong at the boundary.** P7's convergence criterion read `completion iff S_∞ ≥ Θ` where `Θ = f·A/r`. **The weak inequality is false at equality**, because the limit is not itself a partial sum: where revenue is strictly positive every period, the partial sums increase strictly toward `S_∞` and never attain it. So `S_∞ = Θ` means the cap is approached asymptotically and reached at no finite horizon. The correct statement is `S_∞ > Θ` **strictly** implies completion; `S_∞ < Θ` precludes it; equality is sufficient only where the series has finitely many non-zero terms so the sum is *achieved*. This is D-022's `ρ > ρ*` argument, which had been applied to the geometric special case but not to the general criterion above it. Corrected in `DERIVATIONS.md`, `CLAIM_LEDGER.md` M-7, `CORRECTED_CLAIMS.md`.

**"Exactly four mechanisms" is withdrawn.** The complete characterisation is the inequality; the four rows are *examples*. Cause 4 was itself missing from an earlier draft — an enumeration that has already been wrong once should not be advertised as closed.

**S-3's matched term was wrong.** It said closure at month 7 precedes "the base-case 12-month completion". At `f = 1.20` the matched term is **13** months (`match_benchmark_a.term`, payment 17,076,923, APR 37.8694%); 12 is the term at `f* = 1.0945`. The two price tracks were crossed.

**2. Document contradictions.** `CORRECTED_CLAIMS.md` still said "equal-cost"/"equal-effective-cost" for `f*` (now: nearest reference-path APR grid match, residual ≈0.02416pp), used uppercase `F·A`, and asserted "platforms settle after returns" — a premise A-8 marks unverified. `DERIVATIONS.md`'s pricing section called `f*` an exact cost solution and stated the under-reporting conclusion unconditionally (it holds only where the contract still completes, which needs both an adequate horizon and `S_∞ > Θ/ω`). `METHODOLOGY_SPEC.md` A-6 still said the integer-VND correction was "**not applied**" — stale since A-7 applied it. `RESULTS_REGISTRY.md` carried the fixed-payment value judgement, "the failure region has **not been located**" (it has, D-032), a whole-guardrail null, and "Two null results, preserved" when one is superseded. `METRIC_DEFINITIONS.md` now carries a document-level banner marking its affordability and fixed-payment-advantage claims superseded.

**3. Underwriting language in the shipped prototype.** The product presented an unvalidated synthetic score as a **probability of default**, labelled outcomes **"Approved"**, headed the demo **"LIVE ASSESSMENT"**, told users a merchant **"clears the underwriting bar"**, promised **"three minutes, no documents"** and a result **"in about a second"**, and said **funding is held pending verification** — for a product that holds no capital. It also described merchant-submitted figures as platform-sourced: **the shipped prototype connects to no platform API.** All corrected in markup *and* in the JavaScript render paths. `/api/model/status` now ships the UCI figures as `validation_status: "pending_rerun"` with the numbers renamed `reported_*`, matching R-002 instead of contradicting it — a registry note nobody curls is not a qualification.

**D-026's "purged from every public surface" was itself inaccurate.** `/api/model/status` still returns `training_baseline.withdrawn_value: 0.92`, deliberately and with an allow-list entry in `test_no_withdrawn_claims.py`. Retaining it is right — deleting a retracted number destroys the audit trail — but "purged" is then false. Corrected to *retired as a current result, retained as an explicit withdrawal record.*

**4. The verifier could not report the finding it was written for.** `verify_reproduction.py` deleted every canonical file up front, then ran the generators. `canonicalize_validation.py --write` re-verifies the four registered baseline checksums, so on any platform where a baseline reproduces numerically but **not** byte-for-byte — precisely macOS, with the 9 and 2 last-bit differences — the run aborted instead of printing them. **A verifier that only works when everything matches verifies nothing.** Fixed: per-generator deletion immediately before each run with recreation confirmed; a `--no-registered-check` flag for the scratch tree, with the reasoning recorded at the flag; a `MISSING` sentinel so a dropped key is no longer indistinguishable from an explicit `null`; and `try/finally` cleanup that survives a generator crash. Eleven focused tests, including one that breaks a generator and asserts no scratch tree leaks.

**5. Stale metadata inside the artifacts — raised, contained, NOT changed.** All five canonical files embed `canonical.determinism = "Identical code, configuration and seeds produce a byte-identical file."` — the claim D-041 withdrew. Correcting it means editing `rbf_sim/canonical.py` and regenerating all five, **changing all five registered checksums to fix a sentence about reproducibility**. That is a deliberate re-registration and this pass is not authorised to make it. The field is marked superseded in `RESULTS_REGISTRY.md`, and `test_no_public_surface_renders_the_superseded_determinism_field` asserts no backend or frontend surface reads it. **Awaiting a decision; no artifact touched.**

**Suites:** 1,008 passed, 9 skipped (browser, chromium unavailable — not counted as passes).

---

### D-042 — Nine incomplete corrections found by re-auditing D-040/D-041, including a retraction that restored its own retracted sentence
**Date:** 2026-08-10
**Raised by:** an adversarial verification run against the D-040/D-041 working tree *before* committing.
**Status:** APPLIED on `publication-package`.

**Why this entry exists.** D-040 and D-041 were written, tested and self-verified. A hostile re-read then found **nine** defects. Every claimed *number* survived independent recomputation; every failure was an **incomplete or self-contradicting correction**. That is now the third consecutive audit in which the pattern was the same: I fixed the instances I had in front of me and not the family.

**The worst one — a retraction that un-retracted itself.** `CORRECTED_CLAIMS.md:132`. I wrote a blockquote opening *"the sentence that followed… is **withdrawn**"*, gave the correct 6-of-10 breakdown, and then **restored the withdrawn sentence verbatim and unmarked two clauses later**: *"This fully explains the baseline v1 null result — RBF-G was bit-identical to RBF…"*. Checked directly against `results/baseline_v1.json`: RBF-G differs from RBF in **6 of 10** scenarios there as well (`seasonal`, `seasonal_strong`, `growth`, `disruption_1m`, `platform_outage`, `returns_spike`). So the sentence is false for **v1 and v2 alike**, and the null it "fully explains" was never a null. Writing a retraction and then reinstating the retracted text is worse than not retracting at all, because it looks corrected.

**The rest:**

| # | Defect | Fix |
|---|---|---|
| 2 | `DERIVATIONS.md:80` still asserted *"Two sellers with identical cumulative sales reach the cap at the same month"* — directly contradicted by the §A summary I had just corrected, in the same document | Scope-corrected: duration is **first passage**, a property of the trajectory, not of the terminal total |
| 3 | `DERIVATIONS.md:217` kept the last uppercase `F = 1.20` — in the ρ\* worked example that M-6 specifically says must not carry it | Lowercased; added the `f*` value 0.908634 beside 11/12 |
| 4 | `METHODOLOGY_SPEC.md:255` still read `r·S_T ≥ F·A`. **A-8's own table claimed this substitution had been made.** An amendment asserting a change it did not make | Completed |
| 5 | `METHODOLOGY_SPEC.md:282` and `rbf_sim/README.md:16` said *"reproduce bit-for-bit"* — the D-041 claim, in a synonym the scanner did not watch for | Both corrected; `bit[- ]for[- ]bit` added to the tripwire |
| 6 | `rbf_sim/README.md:29` kept the *"61% of rows"* identity wording the README had just been corrected away from | Corrected, with the sample sizes distinguished (60.97% of n=3,000 outside the band; 62.30% flagged on the first 1,000) |
| 7 | `CLAIM_LEDGER.md` P-4 asserted *"Platforms settle after returns"* as fact — a premise A-8 marks **unverified** three files away. The governing document contradicted the spec it governs | Marked pending external support |
| 8 | `CLAIM_LEDGER.md` was exempt from the per-phrase marker check, which is why #7 survived | Moved into `AUTHORITATIVE`: the document that decides what may be said is now the *most* scrutinized, not the least |
| 9 | `CLAIM_LEDGER.md` cited spec version `A-1..A-7` after A-8 was added | Corrected |

**Also noted, not fixed, and disclosed rather than hidden.** All five canonical artifacts embed `canonical.determinism = "Identical code, configuration and seeds produce a byte-identical file."` (`rbf_sim/canonical.py`). `validation_v1_canonical.json` is new in this work, so a fresh artifact was minted carrying a claim D-041 withdrew. It is not rendered on any surface. Correcting it would require changing `canonical.py` and regenerating every artifact, which would invalidate four registered checksums to fix a string — a worse trade. **Recorded here so the next reader finds it from the log rather than from the JSON.**

**The lesson, restated because restating it has not yet been enough.** Three audits, three times the same failure mode: a correction scoped to the example that prompted it. The countermeasure that actually worked each time was an adversarial reader instructed to attack, not a test I wrote. Gate B and Gate C must be adversarial before they are confirmatory, and the claim ledger's human review — not the scanner — is the gate.

---

### D-041 — The byte-for-byte reproducibility claim was overstated; byte and numeric equality now reported separately
**Date:** 2026-08-10
**Raised by:** the second Codex claim audit at Gate A.
**Status:** APPLIED on `publication-package`.

**Trigger.** The project claimed its artifacts "reproduce byte-for-byte". An independent regeneration on **macOS / CPython 3.11.5** produced **9** last-bit floating-point differences in `baseline_v2_canonical.json` and **2** in `baseline_equalcost_v1_canonical.json`. The three other artifacts were byte-identical. On Linux/aarch64 CPython 3.10.12 all five are byte-identical. **All five are numerically equal at published precision in both environments.**

**The evidence file was worse than the claim.** `evidence/2026-08-07-native-macos-verification.md` presented a step labelled "recomputed" as proof of cross-platform determinism. That step read the committed `baseline_v2_canonical.json` and hashed it. **Hashing a file against its own recorded checksum tests only that the file is uncorrupted on disk — it cannot fail for any reason connected to determinism.** The conclusion drawn from it was not supported by the evidence shown. The section is now marked withdrawn, with the measured result in its place and the original text preserved beneath.

**Alternatives considered:**
1. Regenerate the artifacts on macOS so the hashes match. **Rejected, emphatically.** That overwrites the evidence instead of verifying it, and would make the checksums agree for the trivial reason that they had just been written. It is the same error as the "recomputed" step, committed deliberately.
2. Weaken the claim to "reproducible" without qualification. Rejected — that hides which property holds.
3. **Chosen:** report the two properties separately, everywhere, and state the platform.

**Reason.** Byte equality is a statement about a *serialization* on one runtime; numeric equality at published precision is the statement a reader needs in order to trust a figure. Collapsing them made the weaker guarantee sound like the stronger one and hid a real cross-platform limitation. IEEE-754 last-bit divergence between CPython builds is expected; presenting it as a research defect would be as wrong as hiding it.

**Consequence.** New `research/verify_reproduction.py` regenerates every artifact into a scratch tree and prints byte equality and numeric-leaf equality as separate columns, with a non-zero exit only on numeric failure. It never writes to `results/`. `RESULTS_REGISTRY.md`, `CLAIM_LEDGER.md` §0 and the evidence file now carry the measured table. **Cross-platform byte determinism is not claimed and must not be claimed until a clean regeneration demonstrates it.**

---

### D-040 — Second claim audit: missing conditions, a false null result, and unsupported factual premises
**Date:** 2026-08-10
**Raised by:** the second Codex claim audit at Gate A. **Gate A did not pass.**
**Status:** APPLIED on `publication-package`. **No formula, seed, scenario, contract, settlement rule or registered result changed.**

**1. Ledger theorems were missing necessary conditions.** Each was true in the case that motivated it and false in general:

| Claim | Missing condition |
|---|---|
| M-2 | Under-reporting rescales the **uncapped** payments. The clipped final payment is `min(r·ω·B_t, remaining)` and need not scale. |
| M-3 | `A·f` is the **contractual target**; realized total equals it **only upon completion**. |
| M-4 | Path-dependent APR comparison requires **completed, IRR-defined** payment streams. |
| M-5 | Permanent closure prevents recovery **only where an unrecovered balance remains**. A contract completed before closure is unaffected. |
| M-6 | ρ\* depends on the cap factor; and the formula used **uppercase `F`**, which denotes fixed operating cost elsewhere. Now lowercase `f`, throughout `DERIVATIONS.md` and `METHODOLOGY_SPEC.md`. |
| S-3 | "Where revenue reaches zero, recovery fails" is wrong: **temporary** zero-revenue spells often complete — `temp_closure` is 2.0% incomplete at `f = 1.20` and 0.0% at `f*`. The condition is **permanent closure before completion**. |
| I-3 | **Incomplete recovery ≠ principal loss.** `closure_m13` is 76.2% incomplete yet recovers ≈214.3M against a 185M advance — principal covered. Only `closure_m7` (≈98.3M) shows a principal shortfall, and it recovers the *same absolute amount at both cap factors* because that path is revenue-limited, not cap-limited. |
| Q-3 | Replaced an unsourced real-world default assertion with what the model actually assumes: fixed payments made in full and on time, giving an **optimistic scheduled-recovery benchmark**. |
| P-1 | `f* = 1.0945` is the **nearest grid match**, not an exact one: 19.537656% vs 19.561817%, residual **≈0.02416pp**. |
| P-3 | Convergence was checked for **two estimators on one scenario** (`Δn_HPB`, `ΔRR(12)`, sustained −40%). "Estimates are converged" overstated it. |

**2. N-2 was a false null result, and I preserved it as true.** "RBF-G bit-identical to RBF in all ten scenarios" is wrong: **6 of 10** differ. D-039 caught the ledger's version; this audit found the same false claim still standing in `RESULTS_REGISTRY.md` (F-5 and N-2), `DERIVATIONS.md` and `CORRECTED_CLAIMS.md`. The mechanism is now measured exactly rather than asserted — counting month-observations where `r·B_t > p_max = 2·r·R₀` across the full 500 paths per scenario:

`growth` 1,400/12,000 · `seasonal_strong` 11 · `seasonal` 1 · `disruption_1m` 1 · `platform_outage` 1 · `returns_spike` 1 · the other four **0**.

**The correspondence is exact**: the six scenarios where the ceiling binds are precisely the six where RBF-G differs. `DERIVATIONS.md` previously offered `platform_outage` and `returns_spike` as cases where the ceiling could not bind; both bind on one observation. The surviving null is narrower — **N-2′: the hardship floor never activates on any path, by construction** (0 of 36,000, `μ = 0.25 < h = 0.50`).

**3. Analytical summaries overstated their propositions.** P5's heading and summary said duration scales by `1/ω`; what scales is the **required cumulative base** — duration is the *first passage time* to that threshold and depends on path shape (12.862 → 18.690 observed against 18.374 predicted by inverse scaling). P3's summary implied equal terminal cumulative sales give equal first-passage months. P4's summary used "declining vs non-declining" where the exact condition is realized mean eligible base against `B* = P/r`, and both directions occur. `METRIC_DEFINITIONS.md`'s expected-to-fail note asserted unconditionally that relief is funded by longer duration.

**4. Unsupported factual premises.** Spec amendment **A-8** supersedes "Vietnam-calibrated" → "Vietnam-motivated and illustratively parameterized"; "conventional" / "what a seller would realistically be offered" / "externally cited market APR" → "illustrative 18%/12-month amortizing reference"; and marks "platforms settle after returns" and "real RBF contracts commonly carry a maturity date" as **pending external support** while retaining the definitional and mechanical rationales that actually carry those amendments. Public copy: CIC prevalence, "richer than any bureau file", "third-party verified and updated daily", "one API call in under a second", "common for fashion and gift categories", the unvalidated "Default probability 2.4%" label (now "Demo score — synthetic, not a validated default probability", in the markup *and* both JS render paths), the UCI figures reconciled against R-002's *re-run pending* status, and the "61% of rows" identity wording corrected to what the audit measured (median ratio 0.9751, 60.97% outside the band, 62.30% flagged).

**5. The scanner is reclassified.** It is a **named-regression tripwire**, not a semantic proof of safe copy, and its docstring now says so. It discovers `frontend/**/*.html` by glob instead of a static list, covers `backend/main.py` and `backend/financing_engine.py`, and no longer blanket-exempts the registry and backlog: those two now get a per-phrase supersession-marker check, because a stale claim in the document that decides what may be quoted is live whatever the file is labelled. Seventeen fixtures for the exact claims corrected here. One instructive bug found while writing it: the pattern for the byte-for-byte overclaim excluded any sentence containing the word "platform", so *"reproduce byte-for-byte on every platform"* disabled its own pattern. **Human review against `CLAIM_LEDGER.md` remains the real gate.**

---

### D-039 — Adversarial review of D-037: a false ledger claim, and the retracted sentence still live
**Date:** 2026-08-10
**Raised by:** an independent adversarial verification of the D-037/D-038 commit, run before Gate A.
**Status:** APPLIED on `publication-package`.

**Why this entry exists.** D-037 and D-038 were committed, self-verified, and reported as done. A separate adversarial pass then found that two of the three things that commit claimed to do, it had not done. Both failures shared a shape: **the check was built from the examples that motivated it, so it could only catch those examples.**

**Finding 1 — the worst sentence in the project was still on the two most-read pages.** D-037 called "extends the term… instead of defaulting" the most misleading sentence in the product, removed it from `lab.py`, and listed it in the ledger under "do not restate in any form". It was left standing, one word away, on `README.md:32` ("extends the repayment term **instead of triggering a default** — that **mechanical fact**…") and `frontend/index.html:714` ("a slow month extends the term instead of triggering a default"). The README version was worse than the one removed, because it labelled the claim a mechanical fact. Both scanned clean: the regex was the literal string `instead of defaulting`.

**Finding 2 — the ledger contained a claim its own cited artifact falsifies.** S-6 said RBF-G is "bit-identical to RBF in all ten scenarios" and credited the hardship floor. Diffing the cited JSON path: **6 of 10 scenarios differ**. The floor genuinely never binds (`floor_months: 0`, `reachable: false`), but the **ceiling** `p = min(p, 2.00·r·R0)` binds **6,009 of 36,000** month-observations — a number recorded in the ledger's *other* cited artifact. The differences sit below the Lab's display precision, which is why nobody had noticed. `test_claim_ledger.py` did not test S-6.

**Also corrected:** "equal-effective-cost" (hyphenated) survived in six places across `RESEARCH_MANIFEST.md` and `RESULTS_REGISTRY.md` because the regex checked the spaced form, which this project never uses — including a headline results table. `METRIC_DEFINITIONS.md:86` described FIX-B as priced at "an externally cited market APR", contradicting `lab.py` and ledger Q-5. `README.md:147` and `RESEARCH_MANIFEST.md:25` claimed all seven propositions hold "independent of parameter choice"; P7's threshold is ρ\* = 1 − r·B₀/(F·A), which is 11/12 at `f = 1.20` and **0.9086** at `f* = 1.0945` — quoting 11/12 as *the* threshold is the price/structure conflation D-015 exists to prevent. Ledger M-5 cited `DERIVATIONS.md` "P7a", a label that does not exist in that file.

**Scanner defects found by constructing evasions rather than by inspection.** A bare `"not "` cue at a 90-character window meant **24.6% of README insertion points** already sat inside a pre-disowned zone; nine assertive sentences passed simply by following an unrelated negation ("Fees are not modelled. Benchmark B is a conventional loan priced at 18% nominal."). At a 48-character window "This is a simulation, not a forecast, and the structure is proven safe for providers" still passed — the negation was about *forecast*. The window is now 20 characters, cues must bind to the term, and Python adjacent-string-literal joins are collapsed first so that a qualifier split across source lines still counts.

**Consequence:** window 240 → 48 → **20**; bare `"not "` removed; patterns extended to plurals, tenses, passive voice and hyphen variants; fifteen evasion sentences added as fixtures; `CLAIM_LEDGER.md` and `BACKLOG.md` added to the scanned set; S-6 rewritten and bound by test; §7 of the ledger now states its three known gaps instead of implying full coverage. Suites: 975 → see final count in the Gate A report.

**The lesson, recorded because it will recur.** A verification written by the same author who wrote the thing being verified inherits that author's blind spots. Both failures here were invisible to me and obvious to a reviewer told to attack. Gate B and Gate C should be adversarial by default, not confirmatory.

---

### D-038 — `validation_v1` canonicalized additively; zero numeric change
**Date:** 2026-08-10
**Raised by:** the Phase A publication audit, asking which quotable numbers lacked a checksum.
**Status:** APPLIED on `publication-package`.

**Trigger:** `validation_v1.json` was the only registered result with no canonical form — and it holds the two figures most likely to reach a slide: the reference-path cost-matched cap `f* = 1.0945` and Benchmark B's 19.5618% APR. The most quotable numbers were the least verifiable.

**Alternatives considered:**
1. Leave it and forbid citing validation-only numbers in the paper. Rejected — `f*` is load-bearing for the price/structure separation (D-015); a paper that cannot cite it cannot make its own central argument.
2. Rewrite `run_validation.py` to emit a canonical pair. Rejected — that file's bytes are part of what produced the artifact. Changing the generating source without changing the numbers is the confusion the fingerprint exists to prevent.
3. Widen `NON_DETERMINISTIC_KEYS` to strip nested keys. Rejected — that constant governs the writer that produced four already-registered baselines. Not worth the blast radius for one nested field.
4. **Chosen:** a separate `canonicalize_validation.py` that reads the committed artifact and re-expresses it, never recomputing.

**Reason:** Re-running the entire battery from a clean tree (`conv_step.py` at N = 500/2000/5000/10000, then sections 2/4/5/6) reproduced the committed file with **exactly one** difference — `/_meta/date` — and **zero** numeric drift across all 174 scalars. Both `run_scenario` (base_seed 20260803) and `bootstrap_ci` (seed 90210) already carried deterministic defaults, so the battery was reproducible all along; it simply had no artifact to prove it with. The date is a *when-it-ran* fact and belongs in provenance.

**Consequence:** `validation_v1_canonical.json` = `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4`. `validation_v1.json` is untouched. The original run date is preserved as `original_run_date` in the provenance record — an earlier draft of the script *dropped* it while printing that it had moved it, which would have made the script lie about its own behaviour. All four baseline checksums re-verified unchanged, and the script re-verifies them on every write. Bound by `test_validation_artifact.py`.

---

### D-037 — Copy reconciled against the artifacts; a claim ledger now governs public wording
**Date:** 2026-08-10
**Raised by:** the Phase A publication audit.
**Status:** APPLIED on `publication-package`.

**Trigger:** Public copy asserted more than the artifacts support, and the results registry still authorized a claim the derivations had formally retracted.

> **Correction, same day (see D-039).** This entry originally opened "Four live surfaces asserted…". That was wrong on both halves: three of the four items below are in a single file (`backend/lab.py`), and the fourth (`RESULTS_REGISTRY.md`) is classified as *historical*, not live, by the very scanner this entry introduces. It also omitted the `RESEARCH_MANIFEST.md` change it made. A decision log that miscounts its own scope is the same failure as a ledger that miscounts its artifacts.

**What was wrong, and why each is not cosmetic:**

1. **`lab.py`: "extends the term when revenue falls *instead of defaulting*."** Asserts default-prevention. `closure_m7` is **100.0%** incomplete at *both* registered cap factors — the contract does not extend, it never completes. This was the most misleading sentence in the product.
2. **`lab.py`: "takes *proportionally* longer… the total is invariant."** Both unconditional. Invariance holds only when the cap is reached inside the horizon; and 12.862 → 18.690 months against ω 1.00 → 0.70 is not exact proportionality (integrality and clipping). Now derived from the artifact at request time rather than typed, so it cannot go stale.
3. **`lab.py`: "A *conventional* 12-month amortizing loan at 18%."** Implies a sourced market rate. The 18% is an assumed input; no market survey backs it.
4. **`RESULTS_REGISTRY.md` R-010** restated "RBF costs ~2.3× the interest of a conventional loan" *and* listed F-2 as publicly presentable — while `DERIVATIONS.md` P6 says that claim "was wrong on two counts" and `CORRECTED_CLAIMS.md` #2 records the correction. A retracted claim was live on the document that decides what may be quoted. F-3's null was likewise unmarked despite D-032 having located the failure region.

**Also corrected:** the ω finding carried a `mathematical_property` label over text that mixed a proof with a measurement; it is now two findings under their own classes, because promoting a simulation result to a theorem is the same error at smaller scale.

**Not touched, deliberately:** `METHODOLOGY_SPEC.md` (frozen; its "Vietnam-calibrated" phrasing is a *limiting* disclaimer, the honest direction) and `DERIVATIONS.md` P1–P7 (load-bearing proofs; "Equal-cost pricing" there names an exact mathematical operation). `BASELINE_FINDINGS.md` retains F-2 as written — it is audit trail and carries a banner naming F-2 as superseded.

**Consequence:** `research/CLAIM_LEDGER.md` now lists every public claim with its class, artifact, JSON path, checksum, required qualifier and superseded predecessor. Enforced by `test_public_copy.py` and `test_claim_ledger.py`.

**A note on the enforcement test, because it failed in an instructive way.** Its first version used a 240-character symmetric negation window including the bare word "not". In dense technical prose that disowns essentially every match: the scanner passed the entire repository while both `lab.py` violations were still in it. A scanner that cannot fail on the text that motivated it is worse than none, because it certifies. The window is now directional and tight, and the test suite includes the verbatim retracted sentences as fixtures — so the scanner must prove it catches the copy this project actually shipped.

---

### D-036 — Closing two partially-implemented acceptance criteria
**Date:** 2026-08-09
**Raised by:** the final-gate audit, re-verifying D-035.
**Status:** APPLIED. Lab functionality frozen. Remaining Lab work is real Safari/iPhone verification only.

**1. Raw exception text could still reach the page.** D-035 closed the non-2xx body leak but two paths remained: a **200 carrying malformed JSON** — whose `SyntaxError` message quotes the offending bytes — and any **render-time exception**, both of which fell through to `show("error", e.message)`.

Errors are now split by provenance. Only errors this code constructs carry `publicSafe: true`; everything else is replaced with fixed copy, *"The page could not display this research result."* The flag is a **whitelist**, so a future `throw` is safe by default rather than safe only if someone remembers. `r.json()` is guarded and parse failures become their own fixed message. Console diagnostics carry route, status, a sanitized code, and a request id from a response *header* — never response content, never an exception message. A source test asserts every `show("error", …)` call routes through `publicMessage()`; browser tests inject `password=hunter2 /srv/app/db.py` through a malformed 200 and through a forced render exception and assert it reaches neither the DOM nor captured console output.

**2. Survivor conditioning was in the API but not in front of the reader.** The card labels changed in D-035; the settlement table still carried one unconditional "Mean duration" header across rows conditioned differently, and the pricing finding still described the rate gap as a cap-factor effect.

At `closure_m13` the cost-matched arm completes **92.4%** of paths and the illustrative arm **23.8%**. Their survivor rates are averages over differently selected subsets, so the difference between them mixes price with selection. Describing it as a pricing effect would be the survivorship error restated as a finding — in the scenario added to demonstrate honest failure.

Now: each partially censored card shows **"Paths completing within 24 months: X%"**; the settlement table qualifies the duration cell **per row** with *"completed paths only"* and adds an explicit completion column; the arm disclosure carries the API's basis text. The pricing finding branches — where both arms complete it stands and says so explicitly; where either is censored it is replaced by a statement reporting **both** survivor rates with **both** completion shares and noting that differently selected subsets prevent a like-for-like comparison. `temp_closure` is pinned as the lightly censored case; `closure_m7` keeps "Undefined — repayment incomplete".

**Consequence:** backend 283 → 295, browser tests 5 → 9 with no skips. No file under `research/results/` changed; all four canonical checksums byte-identical.

**Still open:** Safari and iPhone remain unverified — no claim is made. The survivor conditioning is a property of the registered artifacts (`duration_mean` and `apr_mean` exclude non-completing paths in **every** artifact, `baseline_v2` included); whether to publish a censoring-aware duration is a methods decision for the paper, not a display change.

---

### D-035 — Final-gate corrections: leakage, atomicity, and a survivor-statistic mislabel
**Date:** 2026-08-09
**Raised by:** an independent final-gate audit that reproduced 270 backend tests, 629 simulation tests and all four canonical checksums from a clean checkout, then found four issues the suite could not.
**Status:** APPLIED. Lab functionality remains frozen.

**1. Error sanitization was incomplete — the leak had been moved, not removed.** D-034 stopped rendering the server's `detail` string but still parsed it and printed it verbatim with `console.warn`. Console output is readable by anyone with devtools open and is captured wholesale by error-reporting SDKs, so an internal path or credential in an exception message still reached the browser. The response body is now **never read** on the error path. Diagnostics carry the route, the HTTP status, and a request id taken from a response *header* if the server chose to expose one — never response content. Verified by injecting `password=hunter2 /srv/app/db.py` and asserting it appears in neither the DOM nor captured console output.

**2. Scenario selection was not atomic.** `select()` called `markSelected()` before its request resolved and accepted responses in arrival order, so a slow request for A landing after a fast one for B left B's pill above A's figures. Every request now carries a monotonically increasing token and a superseded response is discarded before touching a single DOM node; the pill moves *with* the data rather than ahead of it. A browser test holds request A, lets B resolve, then releases A, and asserts the page is entirely B.

**3. The page became "ready" before it had anything to show.** `show("ready")` ran before the first comparison request, briefly presenting an empty research view as a result. Ready is now reached only after the first comparison has loaded **and** rendered; a failed initial comparison shows the sanitized error or unavailable state instead of a blank page.

**4. Duration and rate were survivor statistics presented as unconditional means.** This is the serious one. `engine.run_scenario` averages duration over `[r.duration for r in rs if r.duration is not None]` and the rate over paths where an IRR exists — both silently exclude paths that never reached the repayment target.

At `closure_m13` the illustrative arm displayed **11.99 months and 30.33% APR** while **76.2% of paths never completed**. Those figures describe the surviving 23.8%. Presenting them unqualified is the same error class as the withdrawn AUC: a number labelled as something it is not — and it appeared in precisely the scenario added to show honest failure.

Wherever `0 < incomplete_recovery_rate < 1`, the fields are now labelled **"Mean APR among completed paths"** and **"Mean duration among completed paths"**, with a basis naming the share included and stating that the excluded paths are dropped rather than counted as long or expensive. The metric definitions carry the conditioning; a caveat states it in the limitations panel. Where every path completes, the plain labels remain and the basis says no path is excluded. Where none completes, "Undefined — repayment incomplete" and "Not completed within 24 months" stand. Pinned by test at `closure_m13` for both revenue-based arms and at `temp_closure`.

**5. The footer fallback could be overwritten with nothing.** `renderProvenance()` assigned `spec_version || ""`, so a blank or malformed value replaced good default copy with an empty string and reproduced *"Simulation output under ."* It now only overwrites when the value is a non-empty string.

**What the existing tests could not catch, and why.** The suite asserted that served values matched the artifact — which they did. It never asked what the artifact's values *mean*, so a correctly-transcribed survivor statistic passed every check. Two of these four were timing- or console-dependent and invisible to static inspection; `backend/tests/test_lab_browser.py` now covers them with a real event loop.

**Open, deliberately not changed here.** The conditioning is a property of the registered artifacts, not of the Lab — `duration_mean` and `apr_mean` are survivor statistics in **every** artifact including `baseline_v2`, and any duration or rate quoted from a scenario with incomplete recovery carries it. Whether the artifacts should additionally report an unconditional or censoring-aware duration is a research question for the paper. Changing a registered result to improve a display would be the wrong order.

**Consequence:** backend tests 270 → 283, plus 5 browser tests. No research artifact modified; all four canonical checksums byte-identical.

---

### D-034 — Simulation Lab closing fixes; functionality now frozen
**Date:** 2026-08-08
**Status:** APPLIED. **Lab functionality is frozen after this entry.** The only remaining Lab work is real Safari/iPhone verification and genuine browser-specific fixes.

Four visible defects, all spotted by Hoang in the delivered screenshots rather than by any test — which is itself the finding: the suite proved the numbers were right and said nothing about whether they were legible.

**1. Clipped axis labels.** A fixed 206 px label gutter silently truncated the longer revenue-based labels, which measured ~244 px. SVG text draws past `x=0` rather than wrapping, so the overflow was invisible in code review and only showed on screen. The right-hand value reserve had the same defect: `10.16 mo` overran a fixed 60 px by 4 px at full-length bars. Both gutters are now **measured at runtime** with a canvas metric against the actual font, and the axis labels were shortened at source. Verified: **0 clipped text nodes across 8 widths × 4 scenarios**, from 360 px to 1440 px.

**2. Malformed footer in non-ready states.** The footer read *"Simulation output under ."* whenever the manifest failed, because the spec version is injected by `renderProvenance()` — which never runs on the error path. `#foot-spec` now ships with sensible default copy that the manifest overwrites when it arrives.

**3. Raw server text rendered to the user.** `getJSON` echoed the response body's `detail` straight into the error panel. A 500 from a real deployment could therefore print an internal path, an upstream driver message, or a connection string. User-facing copy is now selected **from the status code**; the detail is written to the console for a developer and never enters the DOM. Verified with an injected `psycopg2.OperationalError at /srv/app/db.py:88 password=hunter2` — absent from the DOM, present in the console. A network failure now has its own message rather than falling through to a generic one.

**4. Amortizing loan described by what it lacks.** The card read *"Repayment target: no cap"* — true, and useless. It now reports **"Scheduled total repayment: 203,529,584 ₫"** with the basis stated, because that is the number a reader can actually use. Each arm carries a `repayment_target` object naming its own label, amount and basis, so the annuity and the capped contracts are described in their own terms rather than one being rendered as a deficient version of the other.

**Closure wording**, as requested: an incomplete contract now reads **"Undefined — repayment incomplete"** for the rate and **"Not completed within 24 months"** for duration, instead of an em-dash that read as missing data rather than a finding.

**Consequence:** backend tests 263 → 270. No research artifact modified; all four canonical checksums verified byte-identical.

---

### D-033 — Simulation Lab refinement pass after external design audit
**Date:** 2026-08-08
**Trigger:** an independent Dieter Rams audit of the rendered surface scored the Lab **21/30 — REFINE, not redesign**, with principles 8 (thorough) and 10 (as little design as possible) at 1/3.
**Status:** APPLIED on `simulation-lab`. Pre-refinement checkpoint preserved at `d11035d`.

**Terminology and honesty (audit principles 4 and 6, the highest-priority finding).**

| Was | Now | Why |
|---|---|---|
| "Revenue-based — equal effective cost" | **"Reference-path cost-matched RBF"** | The displayed APRs were *not* equal. The factor was solved on the reference path; realised rates differ because duration moves with revenue. The title claimed a result the numbers beneath it contradicted. |
| "Effective APR" | **"Mean simulated APR"**, with `apr_basis` on every arm | Reference-path and mean-simulated rates are different quantities; the page showed one and named the other. |
| "Contractual cap" for all arms | **"Repayment target"**, per-arm denominator declared | The amortizing loan has no cap. It was being shown the RBF contract's ×1.20 cap while displaying its own smaller total. |
| "Flexibility for the seller is slower recovery" | Conditional on the selected scenario, with the direction computed per scenario | The universal phrasing contradicted the project's own caveat that direction depends on the revenue path. |
| Burden thresholds unqualified | Marked **illustrative reporting bands, not validated hardship cutoffs** | No evidence exists that crossing 15% causes distress. |
| "Lower is easier to carry" | Removed; replaced with an explicit statement that burden is measured against revenue, not against what the seller retains | Margins, operating costs, reserves and other debts are outside the model. The phrase claimed affordability the metric cannot support. |

A **glossary** now defines cap factor, remittance, effective APR, 90th percentile, Monte Carlo interval, canonical artifact and reference path in place.

**Closure exposed (audit principle 2).** Every scenario previously selectable repaid in full, so a reader could reasonably infer that revenue-based financing always recovers. It does not. `run_closure_baseline.py` registers three closure/zero-revenue scenarios at both price tracks (D-032 artifacts). At month-7 closure the revenue-based arm shows **100% incomplete recovery** and **undefined** effective rate — when revenue stops, no discount rate equates the payment stream to the advance, and the study reports that rather than substituting a number (spec §13, E-3). This cross-validates `validation_v1`'s independent boundary probe exactly.

**Under-reporting surfaced — but deliberately NOT as a scenario.** The audit asked for it "as a selectable registered scenario". It is an ω sweep on a fixed revenue shape, not a revenue path; listing it beside "severe downturn" would mislabel it. It has its own panel, which states why it is not a scenario.

**Compression (audit principle 10).** The audited mobile page was ~9,862 px. This pass **added** three scenarios, an under-reporting panel, a glossary and a provenance table, and the mobile page is now **8,868 px** — 10% shorter with materially more content. Achieved by a sticky summary with jump navigation, three provenance blocks consolidated to one, three identical legends consolidated to one, secondary panels folded on narrow viewports only, and tightened mobile chart metrics. **Limitations, assumptions and every caveat remain expanded at all widths** — collapsing those while promoting favourable findings is the anti-pattern the brief names, and a test asserts the caveat list is not nested inside a closed disclosure.

The fold defaults are **closed in markup and opened by script on wide viewports**, so the compact layout is what a phone — or a browser where the script fails — gets by default.

**States (audit principle 8, scored 1/3).** Loading, API-error with working retry, and artifacts-unavailable are implemented, screenshotted and asserted. Keyboard traversal verified: skip link → 8 jump links → 13 scenario buttons, focus visible at every stop, Enter activates and updates the summary. The settlement table shows a scroll affordance only when it actually overflows.

**Palette (audit principle 3).** Red-versus-green read as *fixed = bad, revenue-based = good* before any copy. Replaced with an Okabe–Ito-derived **categorical** palette. Measured: all 13 text pairs pass WCAG AA (5.14:1 to 17.40:1); two bar fills initially failed the 3:1 non-text threshold and were darkened until all four pass. Every bar also carries its printed value, so colour is never the sole channel.

**Weight, measured rather than estimated (audit principle 9).** `lab.html` 37,165 B (11,575 B gzipped); inline JS 15,893 B (5,337 B gzipped); **zero** third-party bytes. Cold load: 8 requests, 197,975 B — of which 138,856 B is three self-hosted fonts. API payloads: manifest 5,327 B, scenarios 2,277 B, comparison 12,525 B, under-reporting 1,825 B. Localhost headless Chromium: DOM interactive 38 ms, FCP 52 ms, load 45 ms.

**Not done, and why.** Real Safari/iOS remains **unverified**. Playwright's WebKit needs GTK4 and 13 other system libraries that cannot be installed in the verification sandbox (no root; the package mirror is proxy-blocked). One real WebKit risk was fixed blind: SVGs now carry explicit `width`/`height` attributes as well as a `viewBox`, because WebKit does not always derive an intrinsic height from the viewBox alone and collapses the element. **This still needs one pass on real Safari and a real iPhone.**

**Regression checks on the three principles that scored 3** are now tests: one scenario choice still updates every section; no modal, autoplay, or conversion CTA; serif/sans/mono roles preserved with no gradients, backdrop filters or keyframe animation.

**Consequence:** backend tests 245 → 263. No research artifact modified; `baseline_v2` and `baseline_equalcost_v1` verified byte-identical.

---

### D-032 — Closure / zero-revenue baselines registered
**Date:** 2026-08-08

Three scenarios — permanent closure at month 7 and month 13, and a three-month temporary closure — run at both registered cap factors, using the unmodified generator, same 500 paths and same base seed. `run_baseline.py` and `run_equal_cost_baseline.py` are untouched; their bytes sit inside their own artifacts' generator fingerprints, so shared constants are imported rather than retyped.

The fixed benchmark is unaffected by the shock because `reference_base_path` is flat, shock-free R0 by construction (spec §7.1). A contract is priced at origination; a closure in month 7 cannot retro-price it. That is what keeps the paired comparison valid rather than circular.

| Artifact | SHA-256 |
|---|---|
| `baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` |
| `baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` |

At month-7 closure the revenue-based arm reaches 44.3% recovery by month 24 at the illustrative factor and 48.6% at the cost-matched factor, with 100% incomplete recovery in both. `DERIVATIONS.md` P7a already established closure as absorbing; this is the matching empirical panel.

---

### D-031 — Equal-effective-cost baseline registered; Simulation Lab renders from artifacts
**Date:** 2026-08-07
**Status:** APPLIED, on `simulation-lab`.

**The gap.** `baseline_v2` prices every scenario at the **illustrative** f = 1.20. The equal-effective-cost factor f\* = 1.0945 existed only as a *pricing* result on the single deterministic reference path (`validation_v1.pricing.equal_cost`). Showing seller burden and provider recovery for an equal-cost arm therefore had no artifact behind it, and charting a reference-path pricing number beside 500-path scenario aggregates would compare two different objects — the exact error this project exists to avoid.

**Decision.** Add `run_equal_cost_baseline.py`, producing `baseline_equalcost_v1_canonical.json` (SHA-256 `6f9c71b1…52da68e7`). Same ten scenarios, same 500 paths, same base seed `20260803`, same generator. **The only difference is the cap factor.** Spec §12 already anticipates swept parameters and D-015 established price as separable from structure, so this is in-scope sensitivity, not a new model.

**`run_baseline.py` was NOT edited.** Its bytes are inside `baseline_v2`'s `generator_fingerprint`; editing it would invalidate a registered checksum. The new script *imports* `SCENARIOS`, `N_PATHS` and `R0` from it rather than retyping them, so the two runs cannot silently diverge. `baseline_v2` verified byte-identical after the change: `264d319b…ac5a7849`.

**The Simulation Lab** (`backend/lab.py`, `frontend/lab.html`, `/lab`, `/api/lab/*`) renders from these artifacts. Enforced by test, not by intention:

- Every displayed metric is asserted equal to the value in the canonical file it names.
- The page is scanned for research literals; **a first draft failed it**, having written the equal-cost factor into a chart label as a string. It now reads the factor from the API.
- Narrative findings must quote the same numbers the charts show, so a sentence cannot drift from the bar beside it.
- The page is scanned for financial arithmetic. It scales a value to a pixel width; it computes no money, cap, duration or APR.
- Artifact checksums are displayed and asserted to match the files on disk.

**Two corrections the build surfaced:**

1. **FIX-B was being shown the RBF cap.** The amortizing benchmark is an annuity with no cap factor and no repayment cap, but it inherited `terms.f = 1.20` and a 222,000,000 cap from the artifact's contract block — displayed directly beside its own smaller total of 203,529,584. It now reports no cap, with the basis stated.
2. **Charts were illegible on a phone.** A fixed 760-unit viewBox squeezed into 326 px rendered 12-unit text at **5.15 px**, measured. The viewBox is now sized to the container and the layout switches to labels-above-bars below 560 px; text renders 12–13 px at every width, re-measured across desktop, tablet and mobile.

**Integrity surfaces asserted absent:** the withdrawn AUC (by metric name and by exact value — a naive substring check is wrong, since recovery ratio 12/13 is 0.923076…), RBF-G in any form (D-018), any claim of observed Vietnamese seller outcomes, and the phrase "confidence interval". Asserted present: the by-construction caveat on RBF burden, "incomplete recovery is not a default rate", the fixed arms' unmodelled default risk, that recovery direction is not universal, and that constant-revenue schedules are illustrative projections.

**Consequence:** backend tests 196 → 229. Research artifacts and `rbf_sim` code unchanged.

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

### D-026 — Withdrawn 0.92 benchmark retired from every public surface as a *result* (P0-2 closed)

> **⚠️ Heading and wording corrected (D-043).** ~~"purged from every public surface"~~ overstates what was done and what should be done. `GET /api/model/status` **still returns the figure**, as `training_baseline.withdrawn_value: 0.92`, deliberately — alongside `auc: null`, `validation_status: "withdrawn"` and the circularity arithmetic. That is the correct design: silently deleting a retracted number destroys the audit trail and lets it reappear unchallenged. But "purged" is then false, and `test_no_withdrawn_claims.py` allow-lists that exact line with a reason. The accurate statement is: **retired as a current result, retained as an explicit withdrawal record.**
**Date:** 2026-08-07
**Raised by:** Hoang, reviewing the research-foundation gate report.

**The finding, in his words:** *"`backend/main.py:401` serving `training_baseline.auc = 0.92` is not a leftover — it's the original sin of this project reappearing. The entire Phase 0 finding was that the deployed artifact contradicted the documentation."*

That is the correct reading, and the baseline commit understated it by filing P0-2 as merely "partial". The README withdrew the figure with the circularity arithmetic while `GET /api/model/status` continued to hand it out on request. A reviewer who read the README and then curled the API would have found the two disagreeing — which is precisely the defect PHASE0_AUDIT.md was written about, reproduced by us, after we had documented it.

**Decision.** The withdrawn benchmark is removed from every public surface **as a current result** — retained as a labelled withdrawal record. `training_baseline.auc` is **`null`**, accompanied by `validation_status: "withdrawn"`, `reason: "synthetic circular-label benchmark"`, and a disclaimer carrying the circularity arithmetic.

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

---

## D-047 — Scoring-path disclosure, claim-family sweep, and publication reconciliation
**Date:** 2026-08-20 · **Branch:** `publication-final` (unpushed at time of writing)

**Decision: state the scorer→tier→terms dependency on every active surface, and
correct three claim families that had drifted apart across documents.**

**Trigger.** A README revision (`f652b94`) stated that when scoring falls back
from the ensemble to the heuristic "the numbers shown are identical either
way". Verified false against the code: `ml_engine.score()` computes `pd_score`
differently on each path and thresholds it into Low / Medium / High Risk;
`financing_engine.RATES` keys every term off that tier. At 200M monthly
revenue the repayment cap is 414,000,000 at Low Risk against 249,600,000 at
Medium, and High Risk zeroes the advance, remittance rate and cap so no offer
appears. The same false or ambiguous claim was live in four further places:
`ml_engine.py`'s docstring and `model_status()` note, `ENVIRONMENT.md`,
`.github/PULL_REQUEST_BODY.md` and the generator in `verify_native_macos.sh`.

**Alternatives considered:** correct the README only (rejected — leaves the
repository self-contradictory, which is how the claim survived); drop the
fallback so the question cannot arise (rejected — the fallback is the honest
behaviour and removing it would trade a documentation defect for an outage);
state the dependency everywhere and make entering the fallback observable
← **chosen**.

**Three claim families swept repo-wide, not instance by instance.** The
recurring failure in this project has been fixing the instance in front of us
and missing the family, so each was searched across every tracked surface:

1. **Recovery ordering.** Universal formulations ("the financier waits longer",
   "the same mechanism delays recovery") contradicted P4, which makes the
   ordering conditional on realised mean eligible base against `B* = P/r`. Both
   directions occur in the registered scenarios. Corrected in the manuscript
   abstract, results and conclusion, deck slides 2 and 5, the career package
   and `backend/lab.py`. Scenario-specific statements are retained where the
   scenario is named. This had already been recorded at D-042 and never
   propagated — the reason it is being recorded again.
2. **Cost proportional to `f`.** Only the contractual repayment *target* `A·f`
   is proportional to `f`; realised repayment equals it only upon completion.
   Corrected in `DERIVATIONS.md`, `CLAIM_LEDGER.md`, `RESULTS_REGISTRY.md`,
   `PAPER_OUTLINE.md`, the manuscript, deck slide 7 and the copy scanner's
   documentation.
3. **Time-sensitive negatives.** "Has never received an external submission" is
   a claim about the present that expires the moment anyone visits the site.
   Replaced everywhere with the dated form: "As of August 2026, no external
   merchant data were used in this study; the public deployment is a
   demonstration, not a lending service."

**Consequence.**
- `railway.toml` now runs `backend/start_railway.sh`, which never discards
  training stderr and enters the fallback deliberately rather than through a
  bare `;`. The previous inline command hid the failure and started the service
  regardless, so the live demo ran on the heuristic for an unknown period with
  nothing in the logs saying so.
- `/api/health` exposes `sklearn_runtime` alongside `scoring_path`. The startup
  warning had told operators to read a field that did not exist.
- `frontend/index.html` reads the active path from `/api/health` and fails
  closed; the hero badge was previously the literal string "RF+LR ENSEMBLE
  v1.0" whether or not the ensemble had loaded.
- `tests/test_scoring_path_disclosure.py` (22 tests) proves the tier drives the
  output, proves the heuristic is blind to `revenue_growth` — the ensemble's
  highest-importance feature — so the paths cannot be output-equivalent, and
  holds each removed statement as a fixture asserted to trip the scanner.
- Backend suite 379 → 401 passing. The nine browser checks still skip here;
  `RESEARCH_MANIFEST.md` now states that the skip count is environment-
  dependent rather than a fixed expectation.

**Not done, deliberately.** Dated records are not rewritten. `DECISION_LOG.md`
entries D-042 and D-046 keep their contemporaneous counts;
`CORRECTED_CLAIMS.md` is marked as a 2026-08-03 snapshot with pointers to
current state rather than edited in place; and
`evidence/2026-08-07-native-macos-verification.md` keeps its incorrect closing
note with a dated addendum above it. An evidence record that is edited after
the fact cannot be relied on.

**Underlying training failure: not reproduced, not diagnosed.** Training
succeeds in the development sandbox (exit 0, 1.53s, 153MB peak). The mechanism
that allows a silent failure is established — `train_model.py` imports
scikit-learn at module top while `ml_engine` imports it only inside a guarded
helper, so the service boots in an image without scikit-learn and only training
fails — but the production cause is not. `ENVIRONMENT.md` records Python 3.10
as a known gap where scikit-learn 1.9 cannot install, and there is no
interpreter pin for the builder. That is a candidate, not a finding. The next
deploy's logs and `sklearn_runtime` will settle it.

---

## D-048 — Final publication-integrity reconciliation
**Date:** 2026-08-20 · **Branch:** `publication-final` (unpushed at time of writing)
**Raised by:** an independent read-only gate that passed the branch on engineering
and visual grounds and failed it on claim consistency and stale provenance.

**Decision: correct seven wording/provenance families and one factual error of
my own before the branch is publishable.** No formula, generator, settlement
routine or registered artifact changes; all five canonical checksums are
unchanged and `research/results/` is untouched.

**1. A factual error I introduced, corrected.** D-047 and the manifest stated
that in every environment this project has run in, neither Playwright nor
Chromium was available. **That is false.** D-036 records "browser tests 5 → 9
with no skips" — the nine browser checks *passed* in a browser-capable run. The
agreed wording now used everywhere: *1,030 non-browser tests pass — 401 backend
and 629 simulation. Nine browser checks are defined and excluded from that
total. They passed in the earlier browser-capable run recorded at D-036. In
environments lacking Playwright or Chromium they skip; pytest may report one
skipped module or nine skipped cases depending on what is installed.* Three
things were being conflated: passing tests, browser checks defined, and a skip
count that is a property of the machine rather than of the suite.

**2. The PR body was an obsolete hardening description.** It carried six claims
that are no longer true — 0.92 "purged from the API", 5/5 cross-platform byte
identity, the whole RBF-G guardrail never activating, `validation_v1` not
canonicalized, 196 tests, the Simulation Lab as future work — plus a stale
commit range. Replaced with a current description of the publication package,
the runtime disclosure, and the actual reproducibility position: byte equality
is platform-dependent and not claimed across platforms, and only the narrower
N-2′ floor null survives while the ceiling binds 6,009 of 36,000.

**3. `PAPER_OUTLINE.md` claimed Gate A was untouched.** Its header said "nothing
here amends a Gate A document" and its checklist asserted "No Gate A document
edited", while D-047 had in fact made editorial corrections to Gate-A prose in
`DERIVATIONS.md`, `CLAIM_LEDGER.md` and `RESULTS_REGISTRY.md`. The header now
states that those corrections happened, are logged here, and changed no formula,
generator or registered artifact. The opening argument also carried the
forbidden "structural behaviour unchanged" phrasing as an assertion — removed,
along with "that flexibility is not free" and "it is not insurance", both of
which smuggle in a universal provider-side direction that P4 forbids. The two
surviving occurrences of the phrase are prohibitions against writing it.

**4. Unconditional scorer descriptions.** `README.md` and `index.html` described
the RF+LR ensemble as the scoring path without qualification, which misdescribes
any deploy running the heuristic — including, on present evidence, the live one.
All now name the **active scorer** and state that neither path has measured
predictive validity. `README.md` also claimed RBF "turns platform data" into an
analysis; the prototype connects to no platform API, so this is now
merchant-submitted operational data with direct integration named as design
intent, not shipped.

**5. Target versus realised cost, and APR without completion.** Two remaining
instances of "contractual cost" meant the contractual repayment *target*, and
P6(b) asserted that identical terms produce different APRs without saying among
what. Both families were searched rather than patched at the reported instances:
P6(b) and its §9.1 restatement are now qualified to **completed paths with
IRR-defined payment streams**, with the further point that on a non-completing
path no realised total exists to discount and the APR is *undefined*, not merely
different. Corrected in the manuscript, `DERIVATIONS.md` and the outline.

**6. Deck.** Slide 2 said any revenue stop leaves a balance unrecovered, which
`temp_closure` contradicts — 2.0% incomplete at `f = 1.20` and 0.0% at `f*`.
Replaced with the precise condition: permanent cessation *before completion
while a contractual balance remains*. Slide 13's calibration-versus-causal-
identification statement now carries a `[Sources]` block naming it as this
project's own methodological inference and pointing at `MANUSCRIPT.md` §13 — no
external citation was invented for it, because none supports it.

**7. Tests strengthened without changing the count.** The four parametrized
stale-statement fixtures became one test looping over six, freeing room for
three new checks at a constant 22: `/api/health` must expose `scoring_path`,
`sklearn_runtime` and `scoring_path_note` with the note naming the tier and the
affected terms and leaking no credentials; the hero badge must retain its
fail-closed `ACTIVE SCORER — UNKNOWN` path and must not ship asserting a scorer;
and public scorer copy must be conditional. A fixture list that grows on every
retraction should not make the suite's headline count drift for reasons
unrelated to coverage.

**Consequence.** Backend 401 passed / 9 skipped, simulation 629 passed — counts
unchanged by this pass, so no downstream figure needed republishing.
`MANUSCRIPT.pdf` 17 pages, zero text outside the media box, four metadata fields
set. `RBF_DECK.pptx` 13 slides, 13 notes slides, `[Sources]` on 12 of 13 — slide
1 is the title and states no externally sourced claim. Five canonical checksums
verified unchanged.

**Left alone deliberately.** The California SB 362 citation is unchanged; it has
been independently confirmed against the official chaptered text. Dated records
are still not rewritten.

---

## D-049 — A-9: the IRR was wrong, and the artifacts are regenerated
**Date:** 2026-08-20 · **Branch:** `publication-final` (unpushed at time of writing)
**Raised by:** an independent audit that reproduced the engine's effective-rate
calculation against the registered artifacts.
**Status:** APPLIED. Supersedes the APR passages of **D-034**, **D-036** and
**D-048**, and reopens the deferral in **D-044**. Those entries are dated
records and are not rewritten.

**This is the first change in this project to alter a registered result.** Every
earlier correction pass moved words. This one moves numbers, because the numbers
were wrong.

**Three defects, reproduced before any edit was made.**

1. **Calendar time was collapsed.** `engine.run_path` passed
   `[x for x in p if x > 0]` to `solve_apr`, deleting zero-payment months from
   the middle of a stream. Every later payment was then discounted as though it
   had arrived earlier. Trailing zeros are immaterial at any position, so this
   bound exactly where a scenario contained an *internal* zero-revenue spell:
   `temp_closure` moved 29.1869% → **24.1407%** at `f = 1.20`, and 14.9885% →
   **12.4321%** at `f*`.

2. **The solver could not express a loss.** The bracket was `[1e-12, 2.0]`.
   A contract recovering less than it advanced produced no sign change,
   returned `None`, and was published as *undefined*. `closure_m7` recovers
   about 98.3M against a 185M advance; its annualised IRR is **−86.5129%**.
   "Undefined" reads like a technicality and was concealing an adverse result.

3. **Two denominators were reported as one.** `duration_mean` is conditioned on
   completion. `apr_mean` is conditioned on IRR existence — a different and
   generally larger set, because a path can miss the contractual target and
   still have a well-defined return on the payments it made. In `closure_m13`
   at `f = 1.20`: **119 of 500** complete, **500 of 500** are rate-defined, so
   **381** paths are simultaneously incomplete and rate-defined. The published
   30.33% averaged all 500 while the surrounding prose said "among completed
   paths", where the completed-only figure is **39.37%**.

**Alternatives considered.** (a) Correct the prose and leave the numbers —
rejected: the numbers are wrong, not merely mislabelled. (b) Regenerate in
place, overwriting the five registered artifacts — rejected: that destroys the
record of what was published, and this project's own audit trail depends on
being able to check a superseded figure against the file it came from.
(c) **Amend the specification, regenerate under new stems, preserve the old
five byte-for-byte** ← chosen.

**Specification.** Amendment **A-9** defines the IRR over the complete monthly
vector including internal zeros; solves over `i > −1`; states existence and
uniqueness under the project's one-negative-then-non-negative sign pattern;
separates completion from IRR existence; and adds the observed-window caveat
for incomplete non-absorbing paths.

**Migration.** New: `baseline_v3`, `baseline_equalcost_v2`,
`baseline_closure_v2`, `baseline_closure_equalcost_v2`, `validation_v2`, with
provenance sidecars, registered at R-014. Superseded: the previous five,
preserved byte-for-byte and asserted unchanged by test. Canonical schema
1.0 → 2.0; aggregates gained `apr_defined_count`, `apr_defined_rate`,
`completed_count` and `completed_rate` so no denominator has to be inferred.

**The leaf gate earned its place.** Before registration, old and new artifacts
were compared leaf-by-leaf with an allow-list of rate fields, new denominator
keys and identity metadata. It failed on the first attempt: removing the
`x > 0` filter in `run_validation.sec2` also broke a `len(pay)` that was doing
double duty as the count of paying months, turning every reported pricing
duration into the 24-month horizon. Caught, fixed, re-run clean — 0 unexpected
leaves across all five pairs. Burden, recovery, duration, settlement, scenario
inputs and seeds are unchanged.

**A latent inconsistency surfaced.** `validation_v1_canonical.json` could not
have been regenerated from the committed `run_validation.py`: the raw
`validation_v1.json` predates a `convergence.converged` key added in `42b7b1e`.
The registered artifact was canonicalized from a raw file produced by an older
script. Nothing was published from that key, and `validation_v2` is generated
from the current code, so the inconsistency is closed rather than carried.

**D-044 reopened.** That entry declined to regenerate five artifacts in order to
correct an embedded sentence about reproducibility, on the ground that the trade
was not worth it. Correct at the time. Regeneration now had to happen for a
substantive reason, so the `canonical.determinism` string was corrected in the
same pass at no extra cost: numeric equality at published precision across
tested platforms, byte equality only within a fixed runtime.

**Consequence for public surfaces.** The Lab's `_censoring` helper derived one
qualifier from `incomplete_recovery_rate` and attached it to both the duration
and the rate; it now reports the two denominators separately and labels a
horizon-limited rate as an observed-window figure. `frontend/lab.html` no longer
prints "Undefined — repayment incomplete", which asserted a causal link that
does not exist. Four Lab tests that encoded the old semantics were rewritten
rather than deleted, and now assert the corrected behaviour.

**Not claimed.** A-9 changes what the rate *means* and how it is computed. It
does not make the rate evidence about real sellers, and it does not change the
paper's argument: price and structure remain separable, the burden and recovery
findings are untouched, and the product's financing arithmetic never used this
layer at all.

**Suites:** 403 backend passed / 9 skipped, 639 simulation passed.

---

## D-050 — A-9 round 2: the engine was right, everything around it was not
**Date:** 2026-08-24 · **Branch:** `publication-final` (unpushed at time of writing)
**Raised by:** an independent audit of the A-9 migration.
**Status:** APPLIED. D-049 is preserved as dated history; the APR passages of
D-034, D-036, D-044 and D-048 remain superseded as recorded there.

**The mathematics of A-9 was sound and its headline figures never moved.** All
six registered closure rates are bit-identical before and after this pass, and a
leaf comparison of the round-1 artifacts against the round-2 ones shows **zero
data leaves changed** — only spec identifiers and generator fingerprints. What
failed was synchronisation: the engine was corrected and the documents, the Lab,
the artifact identity and the verifier went on describing the old rule.

**Nine defects, each reproduced before it was touched.**

**1–2. The solver had a ceiling I chose rather than derived.** `IRR_MAX_MONTHLY
= 10.0` made `solve_apr(100, [1200])` return `None`, though its unique monthly
IRR is 11 — the same failure A-9 exists to remove, relocated from the lower
bound to the upper one. And a root sitting exactly on an endpoint was discarded,
because the code demanded a strict sign change: `solve_apr(100, [1100])` has
monthly IRR exactly 10.0. Replaced with an analytic bound `i* ≤ S/P − 1`, valid
for `i > 0`; the inequality **reverses** below zero, which cost one iteration to
notice — for `S < P` the root is negative and `NPV(0) = S − P < 0` brackets it
directly. Endpoint roots are recognised. The single documented numerical limit
is float64 overflow in annualisation above roughly `i = 1.4e25`.

**3–5. The Lab confused completion with rate-definition.** `censored` meant
`0 < completed < 1`, so `closure_m7` — where **0 of 500** paths complete —
reported `censored: False`, took the uncensored branch, and printed *"Every path
completed under both."* The same flag gates the page's basis text, so a reader
saw a −86.51% rate and a blank duration with no explanation of either. The
cross-arm rate comparison branched on that duration flag and then quoted
completion shares as the rate's denominator.

Now: `censored` is any incompleteness, `fully_censored` marks the total case,
the rate comparison branches on the **APR-defined** shares, completion is
reported separately and never inferred, and where the target is unreached the
figure is labelled an observed-window IRR and paired with the completion share.

**A further defect surfaced while fixing it:** `lab.html` rendered
`duration_basis` under a single heading covering "these averages" and **never
rendered `apr_basis` at all** — so the denominator and the observed-window
caveat, the entire point of A-9, stopped at the API boundary and never reached a
reader. Both bases are now rendered under separate headings.

**6. The verifier asked for files that no longer exist.** Every entry paired a
current canonical with a superseded provenance stem. Repaired and pinned.

**7. Provenance measured its own contamination.** `build_provenance` sampled
`git status` *after* writing the canonical file, so every sidecar recorded
`source_tree_dirty: true` caused by its own output — destroying the one question
provenance answers. Two further defects in the fix, both found by regenerating
and reading the sidecars rather than trusting the change: a fixed `[3:]` slice
cut the first character off every path so the exclusion never matched, and
`_git()` returns `None` both on failure and on empty output — which is exactly
what a clean tree produces, so the cleanest possible result was reported as
"unknown". `results/` is now excluded as a category, because it holds outputs
and the question is about source.

The round-1 sidecars also recorded `source_commit: b91d2796`, a commit **amended
away** and unreachable from the branch — an artifact claiming descent from
something that does not exist. All five now record `a58e696`, reachable, with a
clean source tree.

**8. Artifacts disagreed with themselves about their own specification.**
Top-level `spec` read v1.0 with no amendments in `baseline_v3`, `A-1..A-7` in
three others and `A-1..A-3` in `validation_v2`, while `canonical.spec_version`
said `A-1..A-9`.

**9. A claim I wrote in round 1 contradicted A-9.** P6(b) and its restatements
said *"on a path that never completes there is no realised total to discount,
and no effective APR is defined at all"* — written in the same pass that
introduced A-9, whose central example is `closure_m7`: completes on no path,
defined rate of −86.5129%. Corrected in `DERIVATIONS.md`, `MANUSCRIPT.md` and
`PAPER_OUTLINE.md`.

**Terminology boundary, new in this pass.** `b047cc8` put an effective APR on
the product surface. It is the annualised IRR of one deterministic base-case
schedule for one merchant. The Lab's APR is a mean observed-window IRR across
the rate-defined paths of a registered scenario. Same words, different
calculation, different data, different evidentiary weight.
`tests/test_apr_surface_boundary.py` asserts each surface keeps saying which one
it is and that neither claims the other validates it. The incoming product
formulas were not reopened.

**Artifacts regenerated a third time**, from a clean committed tree, so
provenance could honestly record what produced them. Superseded five unchanged
throughout. New stem-currency scanner (`test_artifact_stem_currency.py`) is
contextual rather than a blanket ban: a superseded name inside a marked
historical block is the audit trail, and only an unmarked one is a defect. It
carries the deck's slide-8 footer — two artifacts joined by "and", which no
suffix-based sweep matched — as a fixture.

**Consequence.** Backend 403 → 437 passing, simulation 639 → 643. Verifier runs
from a clean temporary checkout at exit 0, 5/5 byte-identical and 5/5
numerically equal. Manuscript 17 → 18 pages. Deck unchanged at 13 slides.

---

## D-051 — Convergence: one IRR, one reproduction, one lineage
**Date:** 2026-08-24 · **Branch:** `publication-final` (unpushed at time of writing)
**Status:** APPLIED. D-050 preserved as dated history.

**No research finding changed.** Compared leaf-by-leaf against the previous A-9
generation: **zero numeric leaves moved**. What moved was three generator
fingerprints, three lineage-metadata strings and one new lineage field.

**1. Two implementations of one equation had drifted three times.** The product
mirrored `solve_apr` before A-9 corrected it; A-9 fixed the research side and
the product kept the old ceiling; the product then fixed the ceiling and found
an endpoint defect the research side still had. Every drift was caught by a
person reading both files.
`backend/tests/test_irr_cross_layer_parity.py` now runs thirteen identical cash
flows through both and compares them, including every case where they
previously disagreed. A rate quoted to a merchant and a rate published in the
paper must not differ on the same stream.

**2. An exact float comparison made the solver scale-dependent.** `f_hi == 0.0`
assumed the analytic bound `S/P − 1` is exactly representable. It is not:
`solve_apr(100, [115])` leaves a residual of ~1.4e-14 and returned `None`, while
`(10_000_000, [11_500_000])` — the same contract at a larger scale — returned
4.35. **A financial contract yielding a rate or "no rate" depending on how the
money was expressed is worse than a consistent failure**, because nothing about
the input looks wrong. Found downstream in `206cb48` by the product chat and
ported here, where it originated. Tolerance is `abs(principal) × 1e-9`:
relative, because NPV carries the principal's units; seven orders above
float64's ~1e-16 resolution; 0.185 VND on a 185,000,000 advance. A residual
above it still returns `None`, because that means the bound is wrong rather
than that rounding occurred.

**3. The lower floor was a guess, not a limit.** `-1.0 + 1e-9` is seven orders
coarser than the format allows and excluded real roots —
`solve_apr(1_000_000, [1e-6])` and `solve_apr(10_000_000_000, [1])` both
returned `None`, reporting "no rate exists" for streams that pay something.
That is the precise confusion A-9 was written to remove, surviving in the
opposite corner of the domain. Now `math.nextafter(-1.0, 0.0)` in both layers,
with the correctly rounded boundary returned where a root falls below it.
`None` means only what A-9 says it means: no positive payment.

**4. The verifier was not verifying validation.** `canonicalize_validation.py`
re-expresses `results/validation_v2.json`; it computes nothing. The scratch
tree is a `copytree`, so that raw file arrived already written and the step
rebuilt a canonical form from a committed input — **`run_validation.py` never
ran, and a completely broken battery would have verified clean.** The raw file
is now a declared output, deleted with the pair, and the battery runs sections
1, 2, 4, 5 and 6 first. Three tests cover the ordering, the dependency, and an
end-to-end break. Writing the third exposed a flaw in my own first attempt: the
injected failure was appended, so it fired *after* the section had already
written its output, and the battery "failed" while still producing a file.

**5. Lineage.** `run_equal_cost_baseline` embedded `f_star_source =
validation_v1` and a comparison against `baseline_v2` in its **current** output;
`f_star_origin` now records where the value was first derived, kept separate
from where it is sourced. `lab.manifest()` reported
`artifact: validation_v1.json` while loading `validation_v2` — provenance for a
file it was not using. `test_claim_ledger` validated today's headline figures
against the superseded artifacts. The stem scanner now covers bare stems and
generator docstrings, not only the `_canonical` suffix where the last sweep
stopped.

**6. Measurements nobody took are no longer quoted.** The macOS byte-difference
counts — 9 and 2 — are real measurements of the **superseded** generation on
commit `68b8c3d`. They were carried across when rows were renamed, asserting a
measurement of files that have never been regenerated on that platform. Removed
from every current-generation claim rather than guessed, with the method for
obtaining them recorded. The superseded figures stay where they belong.

**7. `railway.toml`, resolved.** Both branches fixed the same silent-error
defect, inline versus script. The script entrypoint is kept: it preserves
training stderr, announces the fallback, and states its consequence. The
incoming inline comment said the financing arithmetic never calls the ensemble
"so a training failure must not stop the service" — the second half is right
and the first half implies output-neutrality, the claim D-047 withdrew.

**Two incoming fixes worth recording as theirs.** `206cb48` found the endpoint
defect described above. `00f6b37` diagnosed the production failure I could not:
`warnings.simplefilter("error")` around unpickling promoted a benign NumPy 2.5
DeprecationWarning raised inside a dependency, so a good artifact was rejected
as unreadable and the site pinned itself to the heuristic while training
succeeded every boot. Across three passes I established the mechanism and
reported honestly that I could not reproduce the cause. That was the cause.

**Consequence.** Backend 480 passed / 9 skipped, simulation 643 passed.
Reproduction verifier from a clean temporary checkout: exit 0, 5/5
byte-identical, 5/5 numerically equal — the first run in which the validation
battery genuinely executed. Five artifacts regenerated from clean committed
source `9c2f460`, all sidecars clean and reachable.

---

## D-052 — Release closure: a page that describes the file it names

**Date:** 2026-08-26 · **Branch:** `publication-final` · **Preceded by:** D-051

The hard correction was A-9 and it is not reopened here. This entry records a
consistency pass: five places where a surface said something the files behind it
did not support. **No finding, formula, scenario input, seed or numerical result
changed.** One checksum moved, for a reason recorded below.

### 1. The pricing block described one file with the contents of another

`lab.manifest()` published a block labelled `validation_v2_canonical.json`,
carrying that file's SHA-256, while reading its **values** out of the raw
`validation_v2.json`. The raw file has no `canonical` key, so `spec_version`
came back `null` sitting directly beside a canonical checksum.

This is the second time the same block has been wrong, and the sequence is worth
recording because the first fix is what set up the second. Originally it named
the superseded `validation_v1.json` while reading `validation_v2`. That fix
corrected the **name and the hash** and left the **read** where it was. The
label became right, the data stayed wrong, and the null `spec_version` — the one
visible symptom — was in the payload the whole time.

A reader who checksummed the named file would have verified bytes that never
produced the numbers displayed next to them. Fixed by reading the canonical
artifact, so name, hash, spec version and values all refer to the same bytes.

### 2. "Equals" was never true

The same block said the cost-matched cap factor was solved "so that its
effective rate **equals** the amortizing loan's". It does not. `f*` is chosen by
`min(grid, key=gap)` over an 800-point sweep; duration is an integer, so cost
moves in steps and an exact match is not generally attainable. The correct
statement — nearest point on the swept grid, `19.537656%` against `19.561817%`,
a residual of about `0.02416` percentage points — was in `run_validation.py`'s
own printed output from the beginning. Only the Lab dropped it.

Corrected in the pricing note, the RBF-EQ arm note and the pricing caveat. The
three numbers are **computed from the canonical artifact at request time**, not
typed in: a residual quoted as a literal is a residual that outlives the sweep
it describes. The wording is derived too — if a future sweep lands exactly on
target, the page says so without an edit, and a test pins that branch. The
`1.0945×` chart label, previously hand-typed, now formats the artifact's own
cap factor.

### 3. The rate was still conditioned on completion in the copy

A-9 separated completion from IRR existence in the **artifacts** and in
`_censoring()`. Two prose surfaces did not follow:
`METRIC_DEFINITIONS["effective_apr"]["caveat"]` and the corresponding entry in
`CAVEATS` both still said the mean rate excluded non-completing paths. Both now
state the two denominators separately — `duration_mean` over completing paths,
`apr_mean` over paths with a defined IRR, an incomplete path that made payments
having a defined observed-window rate, and neither conditional mean being
automatically a portfolio-wide outcome.

**A test was holding the wrong claim in place.**
`test_metric_definitions_disclose_the_survivor_conditioning` asserted the word
"survivor" appeared in the **rate's** caveat. That is the pre-A-9 reading, so
correcting the prose broke a green test — the suite was pinning the defect. The
assertion now pins the corrected conditioning. Duration keeps "survivor",
because duration genuinely is one.

The nine browser checks had the same problem at a second remove: they required
`"Mean APR among completed paths"` and a `closure_m13` finding saying the arms
"cannot be compared on rate alone". Both `closure_m13` arms are **100%**
rate-defined while completing at 92.4% and 23.8%, so the rates are comparable
and what differs is coverage. Rewritten to pin both denominators, the
observed-window note, and the absence of the withdrawn finding.

### 4. The documented reproduction recipe corrupted frozen evidence

`RESEARCH_MANIFEST.md` told the reader to run `conv_step.py` four times. That
script's last statement was an unconditional `json.dump` into
`results/validation_v1.json` — now frozen, superseded, and carrying a registered
checksum quoted in the manuscript, the deck and the registry. **Following the
documented steps would have rewritten registered evidence in place.** Nothing in
the script asked whether its target was still writable.

It was also redundant: `run_validation.py 1` computes the same
500/2,000/5,000/10,000 ladder in one pass into the current raw file. The split
existed to dodge a timeout that no longer applies.

`conv_step.py` now fails closed — before importing the simulation package,
before reading anything, before opening any file — and names its replacement.
The recipe runs sections 1/2/4/5/6 and then the canonicalizer. A test invokes
the retired script both documented ways and asserts the frozen file's bytes
**and mtime** are unchanged; mtime, because a rewrite with identical content
still means the file was opened for writing.

`conv_step.py` was also listed in `canonicalize_validation.py`'s
`EXTRA_SOURCES`, with a comment claiming the convergence ladder came from it.
True of `validation_v1`; never true of `validation_v2`. Editing a retired script
would have moved a current artifact's fingerprint, and a reader tracing
provenance would have been sent to code that never ran. Removed.

**This changes `validation_v2_canonical.json`'s generator fingerprint, and
therefore its checksum.** That is the intended consequence of correcting a
provenance record. The regeneration is a separate commit, made from clean
committed source, and is verified to move metadata only — zero numeric leaves.

### 5. Two documentation pointers aimed at superseded files

`DERIVATIONS.md`'s claim taxonomy sent readers to `baseline_v2.json` and
`validation_v1.json` for **current** simulation magnitudes. `METRIC_DEFINITIONS.md`'s
superseded banner said the authoritative spec ran to **A-8** — one amendment
short of A-9, which redefines the very metric that file is named for. Both now
point at the current artifacts and the current amendment. Dated historical
passages keep their original stems; `CORRECTED_CLAIMS.md` remains a 2026-08-03
snapshot, with its forward pointers updated.

### 6. The macOS reproducibility row is now a measurement

D-051 removed the macOS byte-difference counts rather than guess them: the 9 and
2 figures measured the **superseded** generation on `68b8c3d` and had been
carried across when the rows were renamed. The column read "not measured",
which was honest and useless.

An independent audit has now run `research/verify_reproduction.py` against
current HEAD on **macOS 26.0 arm64, CPython 3.11.5, NumPy 2.2.6**:

| Artifact | Bytes | Last-bit leaves | Worst rel. diff |
|---|---|---|---|
| `baseline_v3_canonical.json` | differ | 11 | `5.351e-15` |
| `baseline_equalcost_v2_canonical.json` | differ | 3 | `1.532e-16` |
| `baseline_closure_v2_canonical.json` | identical | 0 | `0` |
| `baseline_closure_equalcost_v2_canonical.json` | identical | 0 | `0` |
| `validation_v2_canonical.json` | identical | 0 | `0` |

**3/5 byte-identical, 5/5 numerically equal** at relative tolerance `1e-9`.

**The counts are 11 and 3, not 9 and 2.** Had the old figures been carried
across, both rows would have been wrong. That is the case for removing an
unverified number rather than letting it ride, and it is why this is recorded as
an **independent audit run** on a platform this project has no access to, rather
than as something run here.

The deck already carried "3 of 5 byte-identical on macOS" — a figure that
happened to be right while being unsupported and while every other current
surface said "not measured". It is retained now that the evidence sits behind
it, with the environment and the audit provenance attached.

### Consequence

Backend 480 → 495 (13 pricing-provenance tests, 2 retired-script tests);
simulation 643 unchanged; **1,138 non-browser**. Nine browser checks defined,
**rewritten in this pass, zero executed** — Chromium is unavailable here and a
skip is not a pass. Browser execution is an open external gate and is now
described that way on every surface, including the deck note that previously
credited them to the D-036 run. That credit no longer holds: the assertions
those checks make today did not exist when D-036 ran.

---

## D-053 — The browser gate executed, and `main` came back with two corrections

**Date:** 2026-08-27 · **Branch:** `publication-final` · **Merges:** `origin/main` `ff59333`

Two independent events, both external to this workstream, and both of which
changed what may be written down. **No research figure, formula, scenario input,
seed or registered artifact is touched by this entry.**

### 1. The gate ran

D-052 recorded nine browser checks as defined, rewritten, and **never
executed** — Chromium is unavailable in the environment that runs these suites,
and a skip is not a pass. That was the honest state and it was also useless: it
is indistinguishable from nine checks that would fail.

They have now been run:

```
python3 -m pytest backend/tests/test_lab_browser.py -q
......... [100%]
9 passed in 21.55s
```

macOS 26.0 arm64, Python 3.11.5, Playwright Chromium, local HTTP server, at
commit `dcbfc3b`. Independent of this workstream.

**Why the result carries across the subsequent merge, argued rather than
assumed.** `ff59333` changed `README.md`, `frontend/index.html` and one product
test file. All nine checks load `/lab` and nothing else, and every input they
exercise — `frontend/lab.html`, `backend/lab.py`, `backend/main.py` and
`research/results/` — is **byte-identical** to `dcbfc3b`, verified per file. The
evidence therefore describes the current Lab surface. It does not describe a
post-merge execution, and no surface claims one.

**A defect the run exposed, in the test rather than the page.** The failing
assertion before this run was `"How the rate is computed" in arms_text`. That
string is at `frontend/lab.html:589` and renders correctly; it sits inside
`<details><summary>What this contract is`, which carries no `open` attribute, so
`page.inner_text()` — rendered text — cannot see it. The reported diagnosis was
that the heading "was never implemented" and the proposed remedies were to add
it or amend the assertion, escalated as a disclosure decision. Both rested on
the string being absent; `origin/main` carries the pre-A-9 file, which is where
that grep landed. Fixed in `dcbfc3b` by splitting the assertion: what a reader
sees unprompted (both denominators, both labels, and the observed-window caveat)
before opening, and the two basis blocks after setting `d.open = true` — which
proves the text is *reachable*, where `text_content()` would have passed on
`display:none`.

Recorded because a plausible diagnosis attached to a real failure is how a
correct page gets "fixed" into a worse one.

### 2. `main` corrected two things this branch had wrong or missing

**The scoring-path claim was worse than this branch had documented.** D-047
corrected "the numbers shown are identical either way" to a statement that the
active path *can* change the assigned tier. `main` established that it *does*,
on a 200-profile cohort, for a majority of profiles — including profiles one
path approves and the other declines. Worked case: heuristic **APPROVED
212,238,000₫**, ensemble **REJECTED**. The consequence `main` draws is the
uncomfortable one: the model-load repair in `00f6b37`, which this branch merged
and described as neutral, **changed live assessment outcomes**. Merged in full,
including the worked cap figures that make the disclosure checkable.

**`apr_basis` was computed and thrown away on the main surface.** The §7.2 item
in the handoff was flagged as unaudited, and it turned out to be a real instance
of the A-9 family: `financing_engine.py` emitted the basis and `index.html`
rendered it zero times, so the rate appeared with nothing stating what the base
case assumes. `main`'s fix also handles the sharper form — the structure note
has three competing branches, and a merchant with outstanding information
requirements previously saw the rate with **no** basis at all, on the branch
where rates run highest. Merged.

**One thing this branch did not take.** `main`'s "Financing structure" bullet
ends "The extension is the provider's cost" — the universal formulation P4
withdrew. This branch's conditional wording is kept. Merging it would have
reintroduced a corrected claim family through a merge, which is the quietest way
a correction gets undone.

**One test amended, not weakened.** `test_readme_states_the_tier_dependency`
matched a literal string that the merge italicised — correctly, that being the
qualifier the retracted claim dropped. It now strips emphasis before matching,
and gained two assertions `main`'s wording earns: that the README says the paths
*do* disagree, not merely that they could, and that the worked cap figures
survive.

### Consequence

Backend 495 → **502 passed, 10 skipped**; simulation 643; **1,145 non-browser**.
The tenth skip is `main`'s two-path cohort comparison, which needs an ensemble
artifact a clean checkout does not have — reported as a skip, not a pass, and
named as such in the manifest.

Every surface that described the browser checks as unexecuted or an open gate
now records the 9/9 run with its environment and commit: `RESEARCH_MANIFEST.md`,
`.github/PULL_REQUEST_BODY.md`, `MANUSCRIPT.md`, `PAPER_OUTLINE.md`,
`CAREER_PACKAGE.md`, `build_deck.js`. `MANUSCRIPT.pdf` and `RBF_DECK.pptx` are
rebuilt **only** because those statements changed. All ten registered checksums
— five current, five superseded — are unchanged, and the reproduction verifier
still reports 5/5 byte-identical and 5/5 numerically equal.

---

## D-054 — The browser gate ran on the merged tip

**Date:** 2026-08-27 · **Branch:** `publication-final` · **Follows:** D-053

**Documentation only.** This entry changes no Lab input, research result, model,
financing logic or registered artifact.

### The evidence is now direct

D-053 recorded a 9/9 run at `dcbfc3b` and then had to *argue* that it carried
forward past the `ff59333` merge: all nine checks load `/lab`, and every input
they exercise was verified byte-identical to `dcbfc3b`. That argument was sound
and it was checkable, which is why it was written out rather than asserted. It
was still an inference.

An independent run has now executed the suite against the merged tip:

```
9 passed in 23.55s
```

macOS 26.0 arm64, Python 3.11.5, Playwright 1.62.0 with Chromium, local server,
at commit `c8261c6`.

Active publication surfaces now cite that run. **They no longer need the
carry-forward argument, so it has been removed from them** — a reader should not
have to reason about byte-identity across a merge to learn whether the tests
passed. Six surfaces state the same substance:
`.github/PULL_REQUEST_BODY.md`, `RESEARCH_MANIFEST.md`, `MANUSCRIPT.md`,
`PAPER_OUTLINE.md`, `CAREER_PACKAGE.md`, `build_deck.js`.

Once each, with one deliberate exception: `RESEARCH_MANIFEST.md` carries it in
**two** places, because it serves two readers. The status table answers "what is
the current state of this project", and the reproduction-recipe comment block
answers "what should I expect when I run this command" — someone following the
recipe never reads the table. Duplication across *files* would be a
maintenance hazard; these two are the same fact addressed to two different
questions, and collapsing them would leave one of the two readers without it.

`CAREER_PACKAGE.md` carries it twice for a different reason: once in the source
index at the foot of the file, and once inside the résumé and LinkedIn text,
where it appears as a short parenthetical rather than the full statement.

**D-053 is untouched.** It is the dated record of what was known when the merge
was made, and the inference it contains was correct at the time. Rewriting it to
match what is known now would destroy exactly the thing this log exists for.

### The editorial defect this pass fixes

D-053's reconciliation replaced only the *tail* of the browser sentence on four
surfaces, leaving the original lead-in in place. The result was the sentence
"Nine browser checks are defined and excluded from that total" immediately
followed by "Nine Playwright browser checks are defined and are excluded from
that total" — visible as a doubled line on page 17 of the PDF.

A regex that matched from mid-sentence rather than from the start of the claim.
Not a research defect, and it changed no figure, but it is the kind of thing a
reader notices first and reasonably reads as carelessness about the surrounding
numbers. Removed from all four.

### Verification

Zero duplicated browser sentences. No active surface references `dcbfc3b`; the
only remaining references are inside D-053, where they belong. All ten
registered checksums unchanged, nothing under `research/results/` changed, and
no backend, frontend, simulation or financing-engine code touched. The PDF and
deck were rebuilt for the changed sentences alone.

---

## D-055 — Two release-metadata statements outlived their facts

**Date:** 2026-08-27 · **Branch:** `publication-final` · **Follows:** D-054

**Documentation only.** No code, registered result, checksum, publication binary
or research figure is touched. Earlier entries are unchanged.

Found by reading the PR description end to end after the branch was pushed —
the one artifact nobody had read as a document, because it is assembled rather
than authored and had only ever been checked in pieces.

### 1. A base-commit hash, four merges stale

`.github/PULL_REQUEST_BODY.md` opened with "Branch `publication-final`, based on
`f652b94`". True when written. The branch has since merged `main` four times and
the merge base is now `ff59333`.

**Not corrected to `ff59333`.** That would have restarted the same clock: the
next merge invalidates it again, and a base hash in prose is a fact with a
half-life measured in merges. The line now states the branch name only and
explains why no base is named. GitHub computes the real merge base and shows it
on the PR; a hand-maintained copy can only ever disagree with it.

### 2. A page count that a formatting fix moved

Both the PR body and `RESEARCH_MANIFEST.md` said the manuscript PDF was **17**
pages. It has been **18** since the page-bounds and break-opportunity work.
`pdfinfo` reports 18; both surfaces now say 18.

### 3. A decision-log summary that stopped at D-048

The PR's §6 described `D-047` and `D-048` and nothing after — so a reviewer
reading it would have seen the scoring-path disclosure and the publication
reconciliation, and no mention of **A-9**, the artifact migration, the solver
unification, the reproduction repair, or the browser gate. That is the entire
substantive arc of this branch, absent from the document written to introduce
it. Now summarised through D-055.

### What these three have in common

Each is a statement *about the release* rather than about the research, and none
is covered by any of the guards built during this project. The claim ledger
binds research figures to artifacts; the currency tests catch superseded artifact
stems; the copy scanners catch retracted phrasings. A page count and a base hash
are outside all of them, so they aged silently while the figures they sit beside
were checked repeatedly.

Worth stating plainly: the verification effort concentrated where the risk was
believed to be, and the two errors that survived to the final review were both
in the packaging. Neither changes a result. Both are exactly the kind of thing a
reader encounters first, and reasonably reads as evidence about the care taken
with everything after it.
