# Results Registry — RBF Project

Every analysis that produces a number goes here before it is quoted anywhere.
A result that is not in this registry may not appear in the paper, poster, deck,
README, app, or resume.

**Columns:** analysis · dataset/version · key assumptions · output location · exploratory vs confirmatory · public-safe?

---

## Canonical artifacts *(added 2026-08-07, D-027)*

Results are cited by **checksum**, from the canonical artifact. Canonical files contain only quantities and deterministic identity metadata; wall-clock time, git commit and environment live in the provenance sidecar.

> **⚠️ Determinism claim corrected (D-041).** This paragraph previously ended "Identical code, configuration and seeds produce a byte-identical canonical file." **That is true within a platform and false across platforms, and is withdrawn as stated.** Measured: on Linux/aarch64 CPython 3.10.12 all five artifacts regenerate byte-identically; on macOS CPython 3.11.5, `baseline_v2` shows **9** last-bit floating-point differences and `baseline_equalcost_v1` shows **2**, while the other three are byte-identical. **All five are numerically equal at published precision in both environments.** The correct claim is therefore *numeric* reproducibility everywhere and *byte* reproducibility within a fixed runtime. Verify with `python3 research/verify_reproduction.py`, which reports the two separately. Artifacts were not regenerated to force matching hashes.

| Artifact | SHA-256 | Status |
|---|---|---|
| `results/baseline_v3_canonical.json` | `2673438a9ff64914ef0a99d03b229d7c38fa5375ea88b6f4b9ad642a31331674` | **Canonical (A-9). Cite this.** See R-014. |
| `results/baseline_equalcost_v2_canonical.json` | `5f57487c1c81cbd644f47bbd41a8e213f49abf562e99e3cf31d25aae8f61bb58` | **Canonical (A-9).** Cost-matched track. |
| `results/baseline_closure_v2_canonical.json` | `ab2bdcfb1d265925abb9ea0d6e880af2781239a62a763050114de5d596da669f` | **Canonical (A-9).** Closure track, `f = 1.20`. |
| `results/baseline_closure_equalcost_v2_canonical.json` | `f40b7a12c888198eceb5ba7f8419174d5beeefa801af5af63ed5c62f63d2a9df` | **Canonical (A-9).** Closure track, `f* = 1.0945`. |
| `results/validation_v2_canonical.json` | `7fce85ab39913bf47e6a17867802540c608d6ac84f444780cff97859317656d3` | **Canonical (A-9).** Cite this for validation figures. |
| `results/baseline_v2_canonical.json` | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` | **SUPERSEDED by A-9 (D-049).** Preserved byte-for-byte; the record of what was published before 2026-08-20. Do not cite as current. |
| `results/baseline_v2_provenance.json` | *(varies by run — that is its purpose)* | Execution record for the above |
| `results/baseline_v2.json` | `b09ae1f7ec3a92c6b751222f639cc562ee793d71c453298612a5d30e6da356e0` | **Frozen historical evidence.** Not rewritten. Numerically identical to the canonical artifact (0 differing leaves); differs only by an embedded run date. |
| `results/baseline_equalcost_v1_canonical.json` | `6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7` | **SUPERSEDED by A-9 (D-049), preserved byte-for-byte.** ~~Canonical.~~ Reference-path cost-matched pricing, f\* = 1.0945 (D-031). Same scenarios, seeds and generator as `baseline_v2`; only the cap factor differs. |
| `results/baseline_equalcost_v1_provenance.json` | *(varies by run)* | Execution record for the above |
| `results/baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` | **SUPERSEDED by A-9 (D-049), preserved byte-for-byte.** ~~Canonical.~~ Closure / zero-revenue at f = 1.20 (D-032). The cases where incomplete recovery is real. |
| `results/baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` | **SUPERSEDED by A-9 (D-049), preserved byte-for-byte.** ~~Canonical.~~ Closure / zero-revenue at f* = 1.0945 (D-032). |
| `results/validation_v1_canonical.json` | `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4` | **SUPERSEDED by A-9 (D-049), preserved byte-for-byte.** ~~Canonical.~~ Cite this for validation figures (D-038). Produced by `canonicalize_validation.py`, which re-expresses the source without recomputing: all 174 scalars preserved, verified by `test_validation_artifact.py`. |
| `results/validation_v1_provenance.json` | *(varies by run)* | Execution record, including `original_run_date` = 2026-08-04 — the one non-deterministic field in the source. |
| `results/validation_v1.json` | `a1b439c2427e0cbc44a3ec325bb6ddaae7d7043fec2fae0af1b315fc675dde07` | **Frozen historical evidence.** The pre-canonicalization source, retained unmodified. Re-running the whole battery reproduces it with exactly one difference — `_meta.date` — and zero numeric drift. |

Verify: `python3 -c "import json,sys;from rbf_sim.canonical import checksum;print(checksum(json.load(open(sys.argv[1]))))" results/baseline_v2_canonical.json`

> ### ⚠️ Embedded metadata field `canonical.determinism` is SUPERSEDED — not corrected in place (D-043)
>
> Every one of the five artifacts carries this string inside its own `canonical` block:
>
> > *"Identical code, configuration and seeds produce a byte-identical file."*
>
> **That is the claim D-041 withdrew**, and it is embedded in the very files whose checksums are registered above.
>
> **It has NOT been changed, deliberately.** Editing it means editing `rbf_sim/canonical.py` and regenerating all five artifacts, which changes all five registered checksums — invalidating the reproducibility record in order to correct a sentence *about* reproducibility. That trade is not worth making without explicit approval, and this correction pass is not authorised to make it.
>
> **Status of the field:** superseded by the measured table above. The current claim is *numeric* reproducibility at published precision on every platform tested, and *byte* reproducibility within a fixed runtime. **No public surface renders `canonical.determinism`** — asserted by `test_no_public_surface_renders_the_superseded_determinism_field`. Anyone reading the raw JSON should read this note instead.
>
> > **SUPERSEDED BY D-049 (2026-08-20).** The trade this paragraph declined — regenerating five artifacts to correct a sentence — was reopened when an independent audit demonstrated a genuine implementation defect in the effective-rate calculation. Regeneration then had to happen for a substantive reason, so the embedded `determinism` string was corrected in the same pass at no additional cost. The **new** artifacts carry the accurate wording; the superseded five keep the old string and are preserved unchanged. The decision below was correct for its moment and is retained for the audit trail.
>
> **DECISION — FINAL (D-044).** The five registered artifacts are **not** regenerated. Their checksums and their embedded historical metadata stand as written. The embedded sentence is **superseded by D-041 and D-043**, and the corrected reproduction claim — numeric equality at published precision everywhere, byte equality within a fixed runtime — is the only one that may appear in the paper, the API, the Lab, the README or any provenance description. This is not deferred; there is nothing further to decide.

---

## R-000 — Phase 0 audit evidence

| Field | Value |
|---|---|
| **Analysis** | Circularity, population-validity, and engine-consistency checks on the existing synthetic baseline |
| **Script** | `research/analysis/00_audit_evidence.py` |
| **Dataset** | `generate_data.generate_seller_data()`, n=3,000, seed=42, repo @ `bff1477` |
| **Assumptions** | Generating function transcribed verbatim from `generate_data.py`; reconciliation band `[0.55, 1.75]` taken from `integrity_engine.py` rather than chosen by the analyst; integrity screen run on the first 1,000 rows for runtime |
| **Outputs** | `auc_generating_function = 0.9098` · `auc_reported_model = 0.9182` · `max_abs_pairwise_correlation = 0.0448` · `median_revenue_over_orders_x_aov = 0.9751` · `share_outside_reconciliation_band = 0.6097` · `revenue_reconciliation_flag_rate = 0.6230` |
| **Type** | **Confirmatory** — tests a specific pre-stated claim about committed code (the label is a function of the features) |
| **Public-safe** | **Yes.** No participant data. Concerns only the project's own synthetic generator |
| **Status** | ✅ Reproduced 2026-08-03; runs clean from a fresh clone |
| **Used in** | `PHASE0_AUDIT.md` §4 (RI-1, RI-2, RI-3) · `DECISION_LOG.md` D-001, D-006 · planned: paper Limitations, Q&A prep |

---

## R-001 — Synthetic-baseline training metrics *(demoted, do not quote)*

| Field | Value |
|---|---|
| **Analysis** | RF + LR ensemble trained on synthetic seller data |
| **Script** | `backend/train_model.py` |
| **Dataset** | `generate_data.py`, n=3,000, seed=42, 80/20 stratified split |
| **Outputs** | RF AUC 0.9001 · LR AUC 0.9237 · Ensemble AUC 0.9182 · feature importances |
| **Type** | **Exploratory** |
| **Public-safe** | ❌ **NO — DO NOT QUOTE.** Superseded by R-000. The metric measures the generator's noise variance, not predictive skill. Retired from all public surfaces per D-001 |
| **Status** | Reproduced 2026-08-03 · **demoted** |

---

## R-002 — Methodology validation on public credit benchmarks

| Field | Value |
|---|---|
| **Analysis** | Same RF+LR ensemble, 5-fold stratified CV on two real public credit datasets |
| **Script** | `backend/validate_on_real_data.py` |
| **Dataset** | UCI Statlog German Credit (n=1,000) · UCI Default of Credit Card Clients, Taiwan (n=30,000) |
| **Assumptions** | Hyperparameters identical to production; no tuning on these datasets |
| **Outputs** | ~0.80 and ~0.77 ensemble AUC per README — **not yet independently re-run in this audit** |
| **Type** | **Confirmatory** (of the method, not of the merchant model) |
| **Public-safe** | ⚠️ **Conditional.** Quotable only with the population mismatch stated in the same sentence: consumer borrowers, fixed-installment products, Germany 1994 / Taiwan 2005 — no e-commerce seller, no revenue share, no repayment cap |
| **Status** | ⬜ Re-run pending (Phase 5 V-03) |

---

## R-003 — Spec verification and coherence diagnostic ⚠️ *(exploratory — not quotable)*

| Field | Value |
|---|---|
| **Analysis** | Reference implementation of the three arms; checks C1–C5 against `METRIC_DEFINITIONS.md` |
| **Script** | `research/analysis/01_verify_spec.py` |
| **Dataset** | None. Deterministic illustrative paths, `R_0 = 185M VND`, `T = 36`, `A = 200M`, `r = 0.10`, `f = 1.20` |
| **Assumptions** | `m` and `F` **not yet sourced** — swept illustratively. This is the reason the entry is not quotable |
| **Type** | **Exploratory** — a spec check, not a test of any hypothesis |
| **Public-safe** | ⚠️ **No — do not quote.** Single path, unsourced parameters, throwaway reference implementation. Supersede with Phase 3 results |
| **Status** | ✅ All five checks pass, 2026-08-03 |

**Verified:** cost-matching exact to <1 VND at base case (total repaid 240,000,000 both arms, N = D = 13 months, implied fixed APR 37.87%) · PTR constant at `r` pre-cap, confirming the §4.1 degeneracy · under −40% decline RBF pays 39.9% less in month 12 but runs 18 months vs 13 · FIX invariant to `ω`, RBF duration extends 13 → 19 months at `ω = 0.70`.

### ⚠️ Preliminary signal — H2 may fail, and for an interesting reason

Under a −40% sustained decline, distress-month counts (T-0):

| `m` | `F/R_0` | FIX | RBF | |
|---|---|---|---|---|
| 0.25 | 0.20 | 36 | 36 | degenerate — see D-011 |
| 0.25 | 0.10 | **7** | **11** | **RBF worse** |
| 0.35 | 0.15 | 7 | 0 | RBF better |
| 0.45 | 0.10 | 0 | 0 | tie |

**Mechanism.** Under cost-matching, RBF's lower monthly payment is purchased with a longer term. In a declining scenario the fixed loan *finishes* — at month 13 its payment drops to zero — while RBF is still remitting at month 18. Per-month relief can therefore be outweighed by the extra months in which any payment is made at all. Whether relief or duration dominates depends on where `m·R_t − F` sits relative to the payment.

**Why this matters now:** H2 is genuinely at risk, and its outcome is likely *conditional* rather than directional. The pre-specified sensitivity grid (§7 S-4, S-5) and the headline-fragility rule already cover this, which is the intended function of pre-registration. **If Phase 3 confirms it, the paper's headline is a conditional result — "RBF reduces distress only when gross margin clears a threshold" — which is more useful and more defensible than a directional claim.**

**Not a finding.** One path, one shock, unsourced margins, reference code. Registered so that the Phase 3 result cannot later be presented as a surprise, and so that no one can claim the sensitivity grid was designed after seeing it.

---

## R-010 — Baseline comparison run `baseline_v1` ✅ *(first reproducible outcome result)*

| Field | Value |
|---|---|
| **Exact scenario** | 10 scenarios × 4 contracts: stable · seasonal · seasonal-strong · growth · gradual decline · sustained decline · severe downturn · 1-month disruption · platform outage · returns spike. Plus underreporting sweep `ω ∈ {1.00, 0.95, 0.90, 0.80, 0.70}` |
| **Parameters** | `R₀ = 185,000,000 VND` · `A = 185,000,000` · `r = 0.10` · `f = 1.20` · `cap = 222,000,000` · `T = 24` · `σ = 0.15` · Benchmark B `j = 18%`, `N_B = 12` · 500 paths/scenario |
| **Simulation version** | `rbf_sim` v1.0.0 implementing `METHODOLOGY_SPEC.md` v1.0 · base seed 20260803 · bootstrap seed 90210 |
| **Code producing the result** | `rbf_sim/{generator,contracts,metrics,engine}.py` · `run_baseline.py` → `results/baseline_v1.json` |
| **Type** | **Confirmatory** — spec frozen before the run; all metrics and thresholds pre-specified |
| **Public-safe** | ⚠️ **Conditional.** Quotable only with (a) the SIMULATED label, (b) the parameter set inline, and (c) the assumption status of `j`, `N_B`, and seasonality. Not quotable as a claim about Vietnamese sellers |
| **Status** | ✅ Reproduced 2026-08-03 · 146 tests pass · deterministic on rerun |

### Interpretation

- **F-1 — trade-off quantified.** Severe downturn: RBF removes 6.24 [6.19, 6.28] high-burden months (θ=0.15) at a cost of 32.5pp [32.3, 32.8] lower 12-month recovery and duration 12.0 → 18.3 months. Benefit and cost both scale with shock severity.
- **F-2 ⚠️ against the product — ~~"costs ~2.3× the interest of a conventional loan"~~ SUPERSEDED (D-015, `CORRECTED_CLAIMS.md` #2, `DERIVATIONS.md` P6).** The arithmetic stands: Benchmark A implies **41.30% APR**; Benchmark B (18% nominal) repays 203.6M vs 222.0M. The *interpretation* does not. P6 shows the contractual repayment **target** `A·f` is proportional to `f` — realised repayment equals that target only upon completion — and that APR is jointly determined by `f` and the revenue path, so a ratio computed at the illustrative `f = 1.20` is a **pricing** result, not a property of revenue-based repayment. Correct framing: at the illustrative 1.20× cap the simulated contract is substantially more expensive than the illustrative 18% amortizing reference; at the reference-path cost-matched `f* = 1.0945` it is not. **Do not quote the 2.3× ratio.**
- **F-3 ⚠️ null — HORIZON- AND SCENARIO-BOUNDED; the failure region has since been located (D-032).** Incomplete recovery 0.0% in all ten scenarios; total repaid identical at 222,000,000 — but none of those ten reaches zero revenue. `baseline_closure_v1` supplies the missing cases: at `f = 1.20`, `closure_m7` is **100.0%** incomplete and `closure_m13` **76.2%**. **F-3 must not be presented as "RBF recovers in full" or "provider exposure is duration risk, not principal loss" without qualification** — that holds only for the ten non-closure scenarios inside `T = 24`.
- **F-4 ⚠️ against the product.** `RR(12) ≈ ω` to within 0.2pp. Fixed payments are invariant to underreporting because they never read revenue. ~~a genuine structural advantage~~ → **superseded (A-8, D-043): this is contractual schedule invariance, not a demonstrated advantage.** The model assumes fixed payments are made in full and on time, so it cannot compare *realized* collection between the arms. Original wording follows for the audit trail: a genuine structural advantage of FIX.
- **F-5 ⚠️ null — ~~"bit-identical to RBF in all ten scenarios"~~ SUPERSEDED (D-040).** The **floor** never binds — 0 of 36,000 month-observations, provably unreachable since `μ = 0.25 < h = 0.50`. The **ceiling** does bind — 6,009 of 36,000 month-observations in the breakpoint scan — in 6 of 10 baseline scenarios, and those are exactly the 6 where RBF-G differs numerically from RBF. By field: `apr_mean` in 6, `burden_mean` in 6, `recovery_ratio` in 3, `duration_mean` in 1. Present the surviving null as *"the hardship floor never activates by construction"*, never as *"the guardrails never bind"*.

### Limitations

F-3 is partly a horizon artifact (`T = 24` against the **13-month** matched base term at `f = 1.20`). ~~the recovery-failure region has **not been located** and Phase 3 must search for it (D-013)~~ → **STALE, superseded (D-032/D-043): the failure region HAS been located.** `baseline_closure_v1` and `baseline_closure_equalcost_v1` are the registered artifacts; `closure_m7` is 100.0% incomplete at both cap factors.

F-5's surviving null concerns the hardship **floor only**: ~~F-5 means the guardrail arm currently carries no information~~ → **withdrawn (D-040/D-045).** The floor carries a real null (0 of 36,000 month-observations, provably unreachable), but the **ceiling is live** — 6,009 of 36,000, changing 6 of 10 scenarios. The arm is not information-free; one of its two rules is. `j`, `N_B`, seasonality shapes, `m`, `F` are unsourced assumptions. No observed data of any kind. No causal or predictive claim. Intervals are Monte Carlo precision only.

### Safe for public presentation?

**Conditionally, with mandatory framing — and F-2 is no longer presentable as written.** F-1 and F-4 are presentable with the simulated label and parameters stated. **F-2's 2.3× ratio is retracted** (see above); only the underlying arithmetic, framed as a pricing result at the illustrative cap and paired with `f*`, may be shown. **F-3 must not be presented as "RBF is safe for providers"** — the Phase 3 search is now complete and found the failure region (D-032); present F-3 only alongside the closure results. **N-2′ is the hardship-floor null** — that is what may be presented, and it must not be omitted. The **live ceiling result must accompany it**: the ceiling binds 6,009 of 36,000 month-observations and changes 6 of 10 scenarios (`apr_mean` 6, `burden_mean` 6, `recovery_ratio` 3, `duration_mean` 1). Presenting the floor null alone reads as a whole-arm null, which is false.

---

## R-011 — Validation battery ✅ *(convergence, pricing, boundary, breakpoint, revenue definition)*

| Field | Value |
|---|---|
| **Exact scenario** | (a) convergence at 500/2,000/5,000/10,000 paths on sustained −40%; (b) cap sweep `f ∈ [1.05, 1.30]` on the stable reference; (c) reference-path cost-matched cap solve (JSON key `pricing.equal_cost`); (d) 12-probe recovery-boundary search; (e) RBF-G breakpoint scan over 36,000 month-observations; (f) remittance-basis sweep |
| **Parameters** | `R₀ = 185,000,000` · `A = 185,000,000` · `r = 0.10` · `f = 1.20` · `T = 24` · basis `net_sales` · Benchmark B `j = 18%`, `N_B = 12`. All illustrative or derived — none externally sourced |
| **Simulation version** | `rbf_sim` v1.0.0 + spec amendments A-1…A-5 · seeds 20260803 / 90210 |
| **Code** | `run_validation.py`, `conv_step.py` → `results/validation_v1.json`; `run_baseline.py` → `results/baseline_v2.json` |
| **Type** | **Confirmatory** for convergence, pricing, breakpoint, revenue definition. **Exploratory** for the boundary probes (a search, not a pre-specified test) |
| **Public-safe** | ⚠️ **Conditional** — simulated label, parameter set, and assumption classification must appear with any quoted figure |
| **Status** | ✅ 2026-08-03 · 169 simulation tests + 47 backend tests passing |

**Interpretation.** Converged (Δ 0.0027 months, 0.042pp from 5,000→10,000). Reference-path cost-matched cap **f\* = 1.0945** at 19.54% APR vs Benchmark B's 19.5618% — price and structure are separable, so the 39.90% APR at `f = 1.20` is a **pricing** result. Incomplete recovery is exactly the failure of the binding criterion: **no finite `t ≤ H` has `S_t ≥ Θ = f·A/r`** (for finite `H`, equivalently `S_H < Θ`). Zero-revenue months, a binding horizon and a terminal write-off are **examples of how that can happen, not an exhaustive list** (D-043/D-045) — a strictly positive but fast-decaying path whose lifetime sum converges below `Θ` is a fourth, and nothing here proves there is no fifth. Empirically, a −40%/−60% decline alone over 24 months does not produce it. RBF-G's floor is **provably unreachable** (`p_min_mult 0.25 < hardship 0.50`).

**Limitations.** Three boundary probes returned "cap unreachable on reference" — at `A = 3×R₀` or a 12-month write-off, benchmark A cannot be matched and the comparison is undefined. Reported, not dropped. No default model was introduced; non-recoveries are mechanical (zero revenue, maturity), not modeled borrower default. `platform_fee_rate` is arbitrary-and-awaiting-justification, defaulted to 0.

**Safe for public presentation?** Yes with mandatory framing. **The reference-path cost-matched cap `f*` must accompany any cost comparison** — quoting 39.90% without `f*` would repeat the error this run corrected. Say "reference-path cost-matched", not "equal cost": the cap factor was solved on a single flat, shock-free reference path, and on simulated paths the realised rate differs because duration moves with revenue.

---

## R-012 ⚠️ — Provider-recovery effect reverses sign *(supersedes part of R-010)*

| Field | Value |
|---|---|
| **Analysis** | Paired FIX-A − RBF ΔRR(12) across 10 scenarios, `baseline_v2`, basis `net_sales` |
| **Code** | `run_baseline.py` → `results/baseline_v2.json` |
| **Type** | **Confirmatory** — pre-specified metric, pre-specified scenarios |
| **Public-safe** | ⚠️ **Conditional, and the condition is the point** |

Under stable (−4.3pp), growth (−7.7pp), 1-month disruption (−1.1pp) and strong seasonality (−4.2pp), **RBF recovers capital faster** than the matched fixed loan. Only under decline does the fixed loan lead: gradual +8.1pp, sustained +16.3pp, severe downturn +26.9pp.

**Per the headline-fragility rule (spec §12), any claim that RBF universally slows provider recovery is demoted to a condition-dependent observation, and the reversing condition is stated **exactly** (D-044): RBF leads on cumulative recovery through `k` iff the realized mean eligible base `(1/k)·S_k` exceeds `B* = P/r`. ~~non-declining revenue~~ is a label, not the condition — a declining path whose realized mean still clears `B*` leads, and a flat path below `B*` lags. Note also that Benchmark A's integer rounding makes `B* < B̄` strictly whenever the term rounds up (in `baseline_v2`, 12.37 → 13, giving `B* ≈ 0.951·B̄`), which is why the stable scenario leads at exactly baseline revenue. The label is named in the abstract.** R-010's provider figures were computed on the `gmv` basis and are superseded by these.

---

## R-013 — Null results: one preserved, one superseded

> **⚠️ Heading corrected (D-043).** ~~"Two null results, preserved"~~ — only **N-1** survives as stated. **N-2 is superseded**: RBF-G is not bit-identical to RBF, and the surviving null is the narrower **N-2′** below.

| ID | Null result | Status |
|---|---|---|
| **N-1** | Incomplete recovery = 0.0% across all ten baseline scenarios | **Preserved.** Explained as a horizon artifact by R-011's boundary search, not deleted. The original null and its explanation both stand. |
| **N-2** | ~~RBF-G bit-identical to RBF in all ten scenarios~~ | ❌ **SUPERSEDED — the null result as stated is false (D-040).** RBF-G differs numerically from RBF in **6 of 10** scenarios. The *floor* is indeed unreachable by construction and binds 0 of 36,000 month-observations; the *ceiling* `p_max = 2·r·R₀` binds in six scenarios (1,400 of 12,000 observations in `growth`; 11 in `seasonal_strong`; 1 each in `seasonal`, `disruption_1m`, `platform_outage`, `returns_spike`) and the six binding scenarios are exactly the six that differ. The differences fall below display precision, which is why the null survived review. **Parameters were still not retuned.** The surviving null is narrower: **N-2′ — the RBF-G hardship floor never activates on any path, by construction.** |

Both remain in the registry permanently. Neither was removed once explained.

---

## Pending — Phase 3 confirmatory results

Each becomes a registry entry the moment it produces a number. All are blocked on
the frozen metric definitions (backlog R-02) per decision D-004.

| ID | Analysis | Hypothesis | Type |
|---|---|---|---|
| R-010 | Paired fixed-vs-RBF payment burden across revenue paths | H1 | Confirmatory |
| R-011 | Distress-month counts under seasonal + negative shocks | H2 | Confirmatory |
| R-012 | Provider recovery, duration variance, incomplete-recovery rate | H3 | Confirmatory |
| R-013 | Affordability-signal comparison under simulated stress | H4 (reframed) | Exploratory |
| R-014 | Underreporting / revenue-diversion sensitivity | H5 | Confirmatory |
| R-015 | Distress-threshold sensitivity sweep | robustness | Confirmatory |
| R-016 | Monte Carlo intervals on all headline metrics (bootstrap resampling over simulated paths — **not** population CIs, D-014) | robustness | Confirmatory |
| R-017 | New generator passes the integrity engine (before/after RI-3) | H5 | Confirmatory |

---

## Registry rules

1. **No number without an entry.** If it appears in public, it has a row here.
2. **Exploratory results may not be reported as findings.** They generate hypotheses; they do not confirm them.
3. **Confirmatory requires a pre-registered definition.** The analysis plan commit must predate the first run.
4. **Null and unfavorable results get entries too.** A result that contradicts a hypothesis is registered and reported, not quietly dropped.
5. **Public-safe is a deliberate decision, not a default.** Mark ❌ or ⚠️ freely; R-001 is the worked example.
6. **Re-run before shipping.** Phase 5 V-03 regenerates every ✅ entry from committed code.


---

## R-014 — A-9 artifact generation: corrected IRR definition, domain and conditioning
**Date:** 2026-08-20 · **Decision:** D-049 · **Spec:** v1.0 + A-1…A-9

**Registered, current:**

| Artifact | SHA-256 |
|---|---|
| `baseline_v3_canonical.json` | `2673438a9ff64914ef0a99d03b229d7c38fa5375ea88b6f4b9ad642a31331674` |
| `baseline_equalcost_v2_canonical.json` | `5f57487c1c81cbd644f47bbd41a8e213f49abf562e99e3cf31d25aae8f61bb58` |
| `baseline_closure_v2_canonical.json` | `ab2bdcfb1d265925abb9ea0d6e880af2781239a62a763050114de5d596da669f` |
| `baseline_closure_equalcost_v2_canonical.json` | `f40b7a12c888198eceb5ba7f8419174d5beeefa801af5af63ed5c62f63d2a9df` |
| `validation_v2_canonical.json` | `7fce85ab39913bf47e6a17867802540c608d6ac84f444780cff97859317656d3` |

**Superseded, preserved byte-for-byte:** `baseline_v2`, `baseline_equalcost_v1`,
`baseline_closure_v1`, `baseline_closure_equalcost_v1`, `validation_v1`. These
are the files every figure published before 2026-08-20 came from. They are
retained so the published record stays verifiable, are never cited as current,
and are asserted unchanged by `backend/tests/test_validation_artifact.py`.

**What moved, and only what moved.** Compared leaf-by-leaf before registration:

| Pair | Leaves | APR fields moved | New denominator keys | Unexpected |
|---|---|---|---|---|
| `baseline_v2` → `v3` | 1105 → 1285 | 25 | 180 | 0 |
| `baseline_equalcost_v1` → `v2` | 862 → 1022 | 20 | 160 | 0 |
| `baseline_closure_v1` → `v2` | 273 → 321 | 6 | 48 | 0 |
| `baseline_closure_equalcost_v1` → `v2` | 273 → 321 | 6 | 48 | 0 |
| `validation_v1` → `v2` | 189 → 190 | 1 | 1 | 0 |

Burden, recovery, duration, settlement, scenario inputs and seeds are unchanged.

**Headline movements.**

| Figure | Before | After | Cause |
|---|---|---|---|
| `temp_closure` `apr_mean`, `f = 1.20` | 29.1869% | **24.1407%** | internal zero months no longer deleted |
| `temp_closure` `apr_mean`, `f* = 1.0945` | 14.9885% | **12.4321%** | same |
| `closure_m7` `apr_mean`, both `f` | *undefined* | **−86.5129%** | solver now spans `i > −1` |
| `closure_m13` denominators, `f = 1.20` | one qualifier | **119 completed / 500 rate-defined** | published separately |

**Public-safety classification.** Quotable with the A-9 qualifiers: name the
scenario; pair any horizon-limited rate with its incomplete-recovery figure;
never share one qualifier between `duration_mean` (completion-conditioned) and
`apr_mean` (IRR-conditioned).
