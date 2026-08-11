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
