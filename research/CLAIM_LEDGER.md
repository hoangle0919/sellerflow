# Claim Ledger

**Purpose.** One row per claim this project is willing to make in public, and the
exact file, JSON path and checksum that backs it. A claim absent from this table
is not cleared for a paper, a slide, a poster or a conversation — not because it
is necessarily false, but because nobody has yet written down what would make it
false.

**Status:** Phase A (pre–Gate A). Built on branch `publication-package`.
**Governs:** the paper, the deck, the poster, the executive summary, the demo
script, the portfolio page, the README, and anything said out loud in an
interview about this work.

---

## 0. How to read a row

| Column | Meaning |
|---|---|
| **ID** | Stable handle. Cite these in drafts so a reviewer can grep. |
| **Class** | One of the five in `CLAIM_TAXONOMY` (`backend/lab.py`). The class is the claim's warrant — a `mathematical_property` is proved, a `simulation_result` is measured under assumptions we chose, a `product_implication` is a judgement. |
| **Source** | Artifact + JSON path, or the proof reference. |
| **Checksum** | SHA-256 of the canonical artifact. Any figure whose checksum is absent is not citable. |
| **Required qualifier** | Must travel with the claim. Not a footnote — the same sentence or the adjacent one. |
| **Surfaces** | Where the claim may appear. |
| **Supersedes** | The earlier wording this replaces, so a reviewer reading old drafts can see the correction. |

### Canonical artifacts and their checksums

| Artifact | SHA-256 |
|---|---|
| `baseline_v3_canonical.json` | `363729016298b3d7307ec066c8df37c60e1c9aa2582db2c058c5cc74df894d55` |
| `baseline_equalcost_v2_canonical.json` | `b3ebfe6a5a7e7f48726d7e501295b02f84258a3fe9ee4e048875125b1270e0ee` |
| `baseline_closure_v2_canonical.json` | `21b8e207ff2db9ac866b8cb2bab47c8c2e434d2bff03d802eb6f53a66fdcea4b` |
| `baseline_closure_equalcost_v2_canonical.json` | `e1e6d81bbeeb60f0e923c27a8df44d26674f4b8ad788c6c9796c17ef40622665` |
| `validation_v2_canonical.json` | `7d9b9d0f9b0fd0fea7011625026a7a5da28c1d4fab009e9a2bf2bd7639af52cc` |

**Superseded by A-9 (D-049), preserved byte-for-byte.** Every figure published
before 2026-08-20 was computed from these files, so the record of what was
published stays independently verifiable. They are historical evidence: never
cited as current, never regenerated, never deleted. Their integrity is asserted
by `backend/tests/test_validation_artifact.py`.

| Superseded artifact | SHA-256 |
|---|---|
| `baseline_v2_canonical.json` | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` |
| `baseline_equalcost_v1_canonical.json` | `6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7` |
| `baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` |
| `baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` |
| `validation_v1_canonical.json` | `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4` |

**Reproducibility — measured, and stated at the strength the measurement supports (D-041).**

All five artifacts **reproduce numerically at published precision** from a clean
tree. **Byte equality is platform-dependent and is not claimed across platforms.**

| Artifact | Bytes (Linux 3.10.12) | Bytes (macOS 26.0 arm64, 3.11.5) | Worst rel. diff | Numeric leaves |
|---|---|---|---|---|
| `baseline_v3` | identical | **11 last-bit leaves differ** | `5.351e-15` | equal |
| `baseline_equalcost_v2` | identical | **3 last-bit leaves differ** | `1.532e-16` | equal |
| `baseline_closure_v2` | identical | identical | `0` | equal |
| `baseline_closure_equalcost_v2` | identical | identical | `0` | equal |
| `validation_v2` | identical | identical | `0` | equal |

**Totals:** Linux 5/5 byte-identical; macOS **3/5** byte-identical; **5/5
numerically equal** at relative tolerance `1e-9` in both environments.

**Provenance of the macOS column.** These are the results of an **independent
audit run** of `research/verify_reproduction.py` against the current HEAD on
macOS 26.0 arm64, CPython 3.11.5, NumPy 2.2.6. They were not produced by the
project's own Linux environment, which has no macOS available; the figures are
recorded here on the auditor's report.

The column previously read "not measured", and before that carried "9 last-bit
float differences" for the baseline and "2" for the cost-matched track. Those
older counts were real measurements — of the
**superseded** `baseline_v2` / **superseded** `baseline_equalcost_v1`
generation, on commit `68b8c3d` — that had been carried
across to the A-9 rows when the rows were renamed, asserting a measurement
nobody had taken. They were removed rather than guessed, and the row is now
filled from an actual run of the current artifacts. Note that the current
counts (11 and 3) are **not** the old ones (9 and 2): the guess would have been
wrong in both rows. The superseded figures remain in `RESULTS_REGISTRY.md`,
labelled as measurements of the generation they describe.

Reproduce with `./verify_native_macos.sh` on a macOS host.

Verify with `python3 research/verify_reproduction.py`, which regenerates into a
scratch tree and reports the two columns separately. The registered artifacts
were **not** regenerated to force matching hashes; the differences are a
serialization fact about IEEE-754 rounding in the two runtimes, not a research
error. `validation_v2`'s canonicalization was separately verified by re-running
the whole battery and diffing: the only difference across the entire document
was the run-date stamp, with **zero** numeric drift (D-038).

**Universal qualifier — and what it does and does not cover (D-044).**

No observed seller revenue, repayment or default outcome exists anywhere in this
project. **Nothing in this ledger is evidence about Vietnamese sellers, or about
any seller.** That applies without exception.

The rest of the qualifier is *class-dependent*, and flattening it would misstate
§1 in the opposite direction from the usual error:

- **§1 rows (M-\*) are not simulation output.** They are theorems, proved in `DERIVATIONS.md` and asserted against the engine by `test_derivations.py`. They hold for any revenue path, independent of the simulation, the parameter choices and any distributional assumption. Calling them "simulation output under stated assumptions" would under-claim them and mislabel their warrant. Their limitation is different: they describe the **contract**, and a contract is not a market.
- **§2–§3 rows (S-\*, P-\*) are simulation output** under `METHODOLOGY_SPEC.md` v1.0 + A-1..A-9, for the stated scenarios, seeds and parameters. These are the rows the simulated-output disclaimer is about.
- **§4 rows (I-\*) are judgements** the author draws from the two above. Not measurements.

Where a row mixes classes, it is split rather than labelled with the stronger of
the two — see the ω finding in `backend/lab.py`, which is served as two findings
for exactly this reason.

---

## 1. Mathematical properties — hold by proof, independent of the simulation

| ID | Class | Claim | Source | Required qualifier | Surfaces |
|---|---|---|---|---|---|
| **M-1** | mathematical_property | A revenue-share contract with a cap repays at most the cap: `sum(payments) ≤ cap`, exactly, under integer-VND settlement. | `DERIVATIONS.md` P1; enforced in `backend/money.py::settle` and `rbf_sim/settlement.py`; mutation-tested in `test_money.py` | State that this is a property of the contract and the settlement code, not an empirical finding | all |
| **M-2** | mathematical_property | Under-reporting rescales the **uncapped** payments `p_t = r·ω·B_t`, raising the cumulative base required to reach the cap by `1/ω`. | `DERIVATIONS.md` P5 | Two conditions, both necessary. **(a)** Only uncapped payments rescale — the **final clipped payment is `min(r·ω·B_t, remaining)` and need not scale with ω**. **(b)** Invariance of the total is conditional on the cap being reached; under-reporting severe enough to push the contract past the horizon leaves the cap unreached and the total short. **Duration does not scale by `1/ω`** — the threshold does; duration is first passage to it | all |
| **M-3** | mathematical_property | `A·f` is the **contractual repayment target**, proportional to the cap factor and independent of the revenue path. | `DERIVATIONS.md` P6a | **Realized total repayment equals `A·f` only if the cap is reached.** Where recovery is incomplete the realized total is strictly less. Say "target", not "cost", unless completion is established. Must appear wherever a cost comparison appears — it is why a cost ratio quoted at one `f` is a pricing result, not a structural one | all |
| **M-4** | mathematical_property | Effective APR is *not* a well-defined property of a revenue-share contract. Two sellers on identical terms `(A, r, f)` face different APRs purely because revenue arrives at different speeds. | `DERIVATIONS.md` P6b | Never quote "the APR of RBF" unqualified; always name the path or the arm. **Any path-dependent APR comparison requires IRR-defined payment streams**, and for a *completed-contract* cost comparison, completed ones. ~~an incomplete path has no well-defined internal rate of return, which is why `apr_mean` is a survivor statistic~~ → **withdrawn (A-9, D-049): false.** An incomplete path that made payments has a perfectly well-defined IRR; the rate is undefined only where no payment occurs. `apr_mean` is conditioned on **IRR existence**, `duration_mean` on **completion** — different denominators, both now published as `apr_defined_count`/`apr_defined_rate` and `completed_count`/`completed_rate`. Never share one qualifier between them | all |
| **M-5** | mathematical_property | Permanent closure is absorbing **for an unrecovered balance**: if revenue goes to zero and stays there *while a contractual balance remains outstanding*, no further payment occurs and the cap is never reached. | `DERIVATIONS.md` § "P7 — Exact conditions for incomplete recovery" | **Closure only matters if it precedes completion.** A contract that reached its cap before closure has already been repaid in full and is unaffected — closure is not a loss event per se. State the timing | all |
| **M-6** | mathematical_property | Under geometric decline the contract completes in finite time only if ρ > ρ\* = 1 − r·B₀/(f·A), **strictly**. At the illustrative `f = 1.20` that is 11/12 ≈ 0.9167; at the cost-matched `f* = 1.0945` it is 0.9086. | `DERIVATIONS.md` P7, D-022 | Exact **under the geometric-decline model**, not an empirical rate. **Lowercase `f` is the factor rate**; uppercase `F` denotes fixed operating cost elsewhere in the project and must not appear in this formula. **Always name the cap factor** — ρ\* depends on `f`, so quoting 11/12 as *the* threshold is the same price/structure conflation M-3 warns about. The inequality is strict: at ρ = ρ\* repayment approaches the cap asymptotically and never attains it | paper, appendix |
| **M-7** | mathematical_property | Completion is a **finite-time** property: it holds iff some finite `t ≤ H` has `S_t ≥ Θ = f·A/r`. Against the lifetime sum: `S_∞ > Θ` **strictly** implies completion; `S_∞ < Θ` precludes it at any horizon; at `S_∞ = Θ` completion requires a finite partial sum to **attain** `Θ`, which a strictly positive infinite series never does. | `DERIVATIONS.md` P7, § "Completion is a finite-time property"; D-022 | **Do not write `S_∞ ≥ Θ`.** The weak inequality on the limit is false at equality — the limit is not a partial sum. Routes to incomplete recovery (zero revenue, maturity/write-off, finite horizon, positive-but-fast-decaying revenue) are **examples, not an exhaustive set**; the complete characterisation is the inequality itself. One route was already overlooked once | paper, appendix |

---

## 2. Simulation results — measured, under assumptions we chose

| ID | Class | Claim | Source (artifact → JSON path) | Checksum | Required qualifier | Supersedes |
|---|---|---|---|---|---|---|
| **S-1** | simulation_result | In the severe-downturn scenario the revenue-based arm runs **18.718** months mean duration against the amortizing loan's 12, and recovers **65.4576%** (→ 65.46%) by month 12 against FIX-B's 100%. | `baseline_v3` → `/scenarios/severe_downturn/RBF/{duration_mean,recovery_ratio/12}` | `36372901…` | Name the scenario. Mean duration is a **survivor statistic** — here `incomplete_recovery_rate` is 0.0, so all 500 paths completed and the mean is unconditional | — |
| **S-2** | simulation_result | Across the ten non-closure scenarios, incomplete recovery is **0.0%** and total repaid is identical at the cap. | `baseline_v3` → `/scenarios/*/RBF/incomplete_recovery_rate` **and** `/scenarios/*/RBF/total_repaid_mean` (the second field carries the "total repaid identical at the cap" half; the first alone does not) | `36372901…` | **Horizon- and scenario-bounded.** None of those ten reaches zero revenue, and `T = 24`. Must be presented adjacent to S-3, never alone | R-010 F-3 as originally worded ("provider exposure is duration risk, not principal loss") |
| **S-3** | simulation_result | **Permanent closure occurring before completion** leaves a contractual balance unrecovered. In the `closure_m7` scenario — permanent closure from month 7, before the **13-month** matched base-case term at `f = 1.20` — **100.0%** of paths end incomplete; in `closure_m13`, **76.2%**. | `baseline_closure_v2` → `/scenarios/{closure_m7,closure_m13}/RBF/incomplete_recovery_rate` | `21b8e207…` | Say **permanent closure before completion**, not "where revenue reaches zero": a temporary zero-revenue spell does not necessarily prevent completion — `temp_closure` is only 2.0% incomplete at `f = 1.20` and 0.0% at `f*`. This is the counterexample to "revenue-contingency prevents default" and must appear wherever S-2 appears | the absence of any closure panel before D-032 |
| **S-4** | simulation_result | The same closure scenarios at the cost-matched cap `f* = 1.0945` give **100.0%** and **7.6%** incomplete. The `closure_m13` figure moves by a factor of ten with price alone. | `baseline_closure_equalcost_v2` → same paths | `e1e6d81b…` | Read beside S-3: the structure is identical, only the price differs. This is M-3 made visible | — |
| **S-5** | simulation_result | In the ω sweep every path still reached the cap inside 24 months; mean duration moves **12.862 → 18.690** months as ω falls 1.00 → 0.70, with total repaid unchanged. | `baseline_v3` → `/underreporting/{1.0,0.7}/duration_mean` for the durations, `/underreporting/*/incomplete_recovery_rate` for "every path reached the cap", and `/underreporting/*/total_repaid_mean` for "total repaid unchanged" — three fields, because the claim makes three assertions | `36372901…` | "In this sweep" — not a general guarantee. The invariance is M-2's conditional form. The Lab renders these to one decimal (12.9 → 18.7); quote either, but do not mix precisions in one sentence | "Fixed payments are immune to underreporting — a structural advantage" (`CORRECTED_CLAIMS.md` #3) |
| **S-6** | simulation_result | RBF-G's hardship **floor** never binds: `floor_months` is **0** of 36,000 month-observations at the registered setting, and the setting is marked unreachable — `p_min_mult 0.25 < hardship 0.50`. Its payment **ceiling** does bind, in **6,009** of 36,000. | `validation_v2` → `/rbf_g_breakpoint/pmin0.25_hard0.5`; `baseline_v3` → `/scenarios/*/RBF-G` | `7d9b9d0f…`, `36372901…` | Present as a **null result about the floor**, not omitted. Do **not** say RBF-G is identical to RBF: because the ceiling binds, **6 of 10** scenarios differ. By field: `apr_mean` in **6**, `burden_mean` in **6**, `recovery_ratio` in **3**, `duration_mean` in **1** (`growth`, 11.284 vs 11.286). The differences fall below the Lab's display precision, which is why they are invisible on screen — that is a rendering fact, not an equality | ~~"RBF-G is bit-identical to RBF in all ten scenarios"~~ — my own error in the first draft of this ledger, falsified by the artifact it cited (D-039) |

---

## 3. Sensitivity and pricing results

| ID | Class | Claim | Source | Checksum | Required qualifier | Supersedes |
|---|---|---|---|---|---|---|
| **P-1** | sensitivity_result | `f* = 1.0945` is the **nearest grid match** on the reference path to the illustrative 18%/12-month amortizing reference: **19.537656%** against **19.561817%**, a residual of **≈ 0.02416 percentage points**. | `validation_v2` → `/pricing/equal_cost/{f_star,apr}`, `/pricing/benchmark_b_apr` | `7d9b9d0f…` | **Not an exact match** — it is the closest point on the swept cap-factor grid, and the residual must be stated wherever the figure is. Say **"reference-path cost-matched"**, never "equal cost": `f*` was solved on one flat, shock-free path, and on simulated paths the realised rate differs because duration moves with revenue | ~~"equal-effective-cost cap"~~, and any wording implying exact cost equality |
| **P-2** | sensitivity_result | At the illustrative cap `f = 1.20`, the simulated contract is substantially more expensive than the 18% amortizing reference. At `f* = 1.0945` it is not. | `validation_v2` → `/pricing/sweep`; `baseline_v3` vs `baseline_equalcost_v2` | `7d9b9d0f…`, `b3ebfe6a…` | This is a **pricing** result. `f*` must accompany it. Do **not** quote a cost ratio computed at a single `f` as a property of revenue-based financing | ~~"RBF costs ~2.3× the interest of a conventional loan"~~ — retracted, D-015 / P6 / `CORRECTED_CLAIMS.md` #2 |
| **P-3** | sensitivity_result | **Two specific estimators** were checked for convergence — `Δn_HPB(θ=0.15)` and `ΔRR(12)`, under the sustained −40% decline scenario only. From 5,000 to 10,000 paths they move 0.0027 months and 0.042pp. | `validation_v2` → `/convergence` | `7d9b9d0f…` | **Do not say "estimates are converged" or "the study is converged".** Convergence was established for those two paired differences on one scenario; no other estimator, scenario or cap factor was tested. Intervals are **Monte Carlo intervals over simulated paths** — they measure whether enough paths were run, not uncertainty about real sellers. Never "confidence interval" | ~~"Converged"~~ as an unscoped claim; "bootstrap CIs" (`CORRECTED_CLAIMS.md` #4) |
| **P-4** | sensitivity_result | The remittance basis is `net_sales`, not GMV; the sweep shows the choice is material. | `validation_v2` → `/revenue_definition` | `7d9b9d0f…` | **Premise pending external support (A-8):** no platform settlement documentation was obtained by this project, so "platforms settle after returns" is unverified. The *definitional* argument is what carries the amendment — on the GMV basis the contract would charge a share of money never received. Spec amendment A-1 | the original GMV basis in `baseline_v1` |

---

## 4. Product implications — judgements, not measurements

| ID | Class | Claim | Basis | Required qualifier |
|---|---|---|---|---|
| **I-1** | product_implication | Revenue-contingency converts a fixed obligation into a variable one, and that conversion has a measurable price. | M-3, P-1, P-2 | The defensible framing is **not** "RBF is cheaper" — at the illustrative cap it is not. It is that price and structure are separable and were separated here |
| **I-2** | product_implication | Price and structure must be reported separately, or a comparison silently attributes a pricing choice to a structural property. | M-3, M-4, D-015 | This is the methodological contribution. State it as a design rule the project adopted after getting it wrong |
| **I-3** | product_implication | A provider underwriting revenue-contingent contracts is exposed to duration risk in ordinary downturns and to an **unrecovered contractual balance** where permanent closure precedes completion. | S-2 with S-3 | Both halves, always — S-2 alone reads as "RBF always recovers", which S-3 falsifies. **Do not equate incomplete recovery with principal loss.** Incomplete recovery means the *contractual target* `A·f` was not reached; whether the shortfall touches principal depends on how much was recovered relative to `A`. The artifacts demonstrate a principal shortfall in **one** scenario: `closure_m7` recovers ≈98,349,287 VND against an advance of 185,000,000 — and recovers the *same absolute amount at both cap factors*, because that path is revenue-limited, not cap-limited. `closure_m13` (≈214,307,075) and `temp_closure` both clear the advance and show a shortfall against the **target only**, despite 76.2% incomplete recovery in `closure_m13`. That contrast is the point: a 76.2% incomplete-recovery rate with full principal recovery is not a 76.2% loss rate |

---

## 5. Open real-world questions — cannot be settled by this project

| ID | Claim | Why it is open |
|---|---|---|
| **Q-1** | Whether any of this describes real seller behaviour. | No observed revenue, repayment or default data exists in the project. |
| **Q-2** | Whether the modelled contracts are affordable. | Burden is measured against revenue, not against what the seller retains. Margins, costs, reserves and other debts are outside the model. |
| **Q-3** | Whether the fixed-arm comparison is fair. | The model **assumes fixed payments are made in full and on time** in every month of the schedule. The fixed arms therefore represent an **optimistic scheduled-recovery benchmark**, not a realized-recovery one. No claim is made here about how often real fixed-payment borrowers miss payments — that would require observed data this project does not have. |
| **Q-4** | Whether the burden thresholds (10/15/20/25%) mark real hardship. | They are illustrative reporting bands chosen for this study. No validated hardship cutoff was used and none is claimed. |
| **Q-5** | Whether `j = 18%`, `N_B = 12`, the seasonality shapes, `m` and `F` reflect the Vietnamese market. | All are assumed inputs. None was externally sourced. Phase B's literature matrix is where this gets tested. |

---

## 6. Withdrawn — do not restate in any form

| Claim | Why withdrawn | Reference |
|---|---|---|
| "0.92 AUC" / any predictive-skill number from the ensemble | Circular: `generate_data.py` creates the `defaulted` label by evaluating a hand-written weighted formula over the same features the model is then trained on. The metric measures the generator's noise variance | D-001; `README.md`; enforced by `test_no_withdrawn_claims.py` |
| "RBF costs ~2.3× the interest of a conventional loan" | Conflates price with structure. The contractual repayment **target** `A·f` is proportional to `f` (P6a), and realised repayment equals that target only upon completion; APR is jointly determined by `f` and the path (P6b) | D-015; `DERIVATIONS.md` P6; `CORRECTED_CLAIMS.md` #2 |
| "Fixed payments are immune to underreporting — a structural advantage" | True that scheduled payments do not read revenue; the value judgement does not follow | `CORRECTED_CLAIMS.md` #3 |
| "Confidence intervals" / "bootstrap CIs" | They are Monte Carlo intervals over simulated paths | D-014; `CORRECTED_CLAIMS.md` #4 |
| "Revenue-based repayment extends the term instead of defaulting" | Asserts default-prevention. `closure_m7` is 100.0% incomplete at **both** registered cap factors | D-037 (this phase); S-3 |
| "A conventional 12-month amortizing loan at 18%" | "Conventional" implies a sourced market rate. The 18% is an assumed input | D-037 (this phase) |
| "Equal cost" as a name for `f*` | The cap was solved on one flat reference path; on simulated paths the realised rate differs | D-037 (this phase) |
| A 5.77% cap-overshoot rate | My own error — computed `duration × remittance` while ignoring the clipped final payment. 0 breaches in 6,794 structures | D-029 |

---

## 7. Enforcement

Four tests keep this ledger from becoming decoration:

- `backend/tests/test_no_withdrawn_claims.py` — the withdrawn model metrics cannot reappear on any surface.
- `backend/tests/test_public_copy.py` — scans the nine live surfaces for every §6 phrasing, with a tight directional negation window so a disavowal stays legal and an assertion fails. It carries the verbatim retracted sentences *and* fifteen evasions that defeated earlier versions of itself.
- `backend/tests/test_claim_ledger.py` — every checksum in §0 matches the file on disk; the headline figures still derive from the artifacts they cite; S-6's floor/ceiling asymmetry is asserted against the artifact.
- `backend/tests/test_validation_artifact.py` — the `validation_v2` canonical form is numerically identical to its source, and the four registered baselines are unchanged.

**Known gaps, stated rather than papered over.**

1. A claim added to a draft but not to this table is caught by review, not by CI. That is the reason Gate C exists.
2. The scanner matches *phrasings*, not meanings. A sufficiently novel wording of a retracted claim will pass. The evasion fixtures exist because the first version of that scanner passed the whole repository while two violations were live in `lab.py`, and the second still let "instead of triggering a default" through on the README and the landing page — both caught by adversarial review, not by the test.
3. `RESULTS_REGISTRY.md` is allow-listed as historical, yet it is also the document that decides what may be quoted. That is an uncomfortable classification and it is why R-010's F-2 and F-3 now carry explicit supersession markers inline.
