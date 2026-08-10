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
| `baseline_v2_canonical.json` | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` |
| `baseline_equalcost_v1_canonical.json` | `6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7` |
| `baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` |
| `baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` |
| `validation_v1_canonical.json` | `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4` |

All five reproduce byte-for-byte from a clean tree. The first four were verified
by re-running their generators; the fifth was verified by re-running the whole
battery and diffing — the only difference across the entire document was the
run-date stamp, with **zero** numeric drift (D-038).

**Universal qualifier — applies to every row below.** Every figure is simulation
output under `METHODOLOGY_SPEC.md` v1.0 + A-1..A-7. No observed seller revenue,
repayment or default outcome exists anywhere in this project. Nothing here is
evidence about Vietnamese sellers, or about any seller.

---

## 1. Mathematical properties — hold by proof, independent of the simulation

| ID | Class | Claim | Source | Required qualifier | Surfaces |
|---|---|---|---|---|---|
| **M-1** | mathematical_property | A revenue-share contract with a cap repays at most the cap: `sum(payments) ≤ cap`, exactly, under integer-VND settlement. | `DERIVATIONS.md` P1; enforced in `backend/money.py::settle` and `rbf_sim/settlement.py`; mutation-tested in `test_money.py` | State that this is a property of the contract and the settlement code, not an empirical finding | all |
| **M-2** | mathematical_property | Under-reporting rescales each payment. It does not change what is owed; it lengthens the time to reach the cap. | `DERIVATIONS.md` P3 | **Invariance of the total is conditional on the cap being reached.** Under-reporting severe enough to push the contract past the horizon leaves the cap unreached and the total short | all |
| **M-3** | mathematical_property | Total contract cost is `A·f` — proportional to the cap factor and independent of the revenue path. | `DERIVATIONS.md` P6a | Must appear wherever a cost comparison appears; it is why a cost ratio quoted at one `f` is a pricing result, not a structural one | all |
| **M-4** | mathematical_property | Effective APR is *not* a well-defined property of a revenue-share contract. Two sellers on identical terms `(A, r, f)` face different APRs purely because revenue arrives at different speeds. | `DERIVATIONS.md` P6b | Never quote "the APR of RBF" unqualified; always name the path or the arm | all |
| **M-5** | mathematical_property | Permanent closure is absorbing: once revenue is zero and stays zero, no further payment occurs and the cap is never reached. | `DERIVATIONS.md` P7a | — | all |
| **M-6** | mathematical_property | Geometric revenue decline completes the contract only above the threshold ρ\* = 11/12. | `DERIVATIONS.md` P7 | State the threshold is exact under the geometric model, not an empirical rate | paper, appendix |

---

## 2. Simulation results — measured, under assumptions we chose

| ID | Class | Claim | Source (artifact → JSON path) | Checksum | Required qualifier | Supersedes |
|---|---|---|---|---|---|---|
| **S-1** | simulation_result | In the severe-downturn scenario the revenue-based arm runs **18.718** months mean duration against the amortizing loan's 12, and recovers **65.4576%** (→ 65.46%) by month 12 against FIX-B's 100%. | `baseline_v2` → `/scenarios/severe_downturn/RBF/{duration_mean,recovery_ratio/12}` | `264d319b…` | Name the scenario. Mean duration is a **survivor statistic** — here `incomplete_recovery_rate` is 0.0, so all 500 paths completed and the mean is unconditional | — |
| **S-2** | simulation_result | Across the ten non-closure scenarios, incomplete recovery is **0.0%** and total repaid is identical at the cap. | `baseline_v2` → `/scenarios/*/RBF/incomplete_recovery_rate` | `264d319b…` | **Horizon- and scenario-bounded.** None of those ten reaches zero revenue, and `T = 24`. Must be presented adjacent to S-3, never alone | R-010 F-3 as originally worded ("provider exposure is duration risk, not principal loss") |
| **S-3** | simulation_result | Where revenue reaches zero, recovery genuinely fails. At the illustrative cap `f = 1.20`, `closure_m7` is **100.0%** incomplete and `closure_m13` is **76.2%**. | `baseline_closure_v1` → `/scenarios/{closure_m7,closure_m13}/RBF/incomplete_recovery_rate` | `0fe503d7…` | This is the counterexample to "revenue-contingency prevents default". It must appear wherever S-2 appears | the absence of any closure panel before D-032 |
| **S-4** | simulation_result | The same closure scenarios at the cost-matched cap `f* = 1.0945` give **100.0%** and **7.6%** incomplete. The `closure_m13` figure moves by a factor of ten with price alone. | `baseline_closure_equalcost_v1` → same paths | `49b6f8ef…` | Read beside S-3: the structure is identical, only the price differs. This is M-3 made visible | — |
| **S-5** | simulation_result | In the ω sweep every path still reached the cap inside 24 months; mean duration moves **12.862 → 18.690** months as ω falls 1.00 → 0.70, with total repaid unchanged. | `baseline_v2` → `/underreporting/{1.0,0.7}/duration_mean` | `264d319b…` | "In this sweep" — not a general guarantee. The invariance is M-2's conditional form. The Lab renders these to one decimal (12.9 → 18.7); quote either, but do not mix precisions in one sentence | "Fixed payments are immune to underreporting — a structural advantage" (`CORRECTED_CLAIMS.md` #3) |
| **S-6** | simulation_result | RBF-G is bit-identical to RBF in all ten scenarios; the guardrail floor never binds. | `baseline_v2` → `/scenarios/*/RBF-G`; `validation_v1` → `/rbf_g_breakpoint` | `264d319b…`, `f89fd2ba…` | Present as a **null result**, not omitted. The floor is provably unreachable because `p_min_mult 0.25 < hardship 0.50` | — |

---

## 3. Sensitivity and pricing results

| ID | Class | Claim | Source | Checksum | Required qualifier | Supersedes |
|---|---|---|---|---|---|---|
| **P-1** | sensitivity_result | The cap factor at which the contract's cost matches the 18%/12-month amortizing reference **on the reference path** is `f* = 1.0945`, giving 19.5377% against the reference's 19.5618%. | `validation_v1` → `/pricing/equal_cost/f_star`, `/pricing/benchmark_b_apr` | `f89fd2ba…` | Say **"reference-path cost-matched"**, never "equal cost". `f*` was solved on one flat, shock-free path; on simulated paths the realised rate differs because duration moves with revenue | — |
| **P-2** | sensitivity_result | At the illustrative cap `f = 1.20`, the simulated contract is substantially more expensive than the 18% amortizing reference. At `f* = 1.0945` it is not. | `validation_v1` → `/pricing/sweep`; `baseline_v2` vs `baseline_equalcost_v1` | `f89fd2ba…`, `6f9c71b1…` | This is a **pricing** result. `f*` must accompany it. Do **not** quote a cost ratio computed at a single `f` as a property of revenue-based financing | ~~"RBF costs ~2.3× the interest of a conventional loan"~~ — retracted, D-015 / P6 / `CORRECTED_CLAIMS.md` #2 |
| **P-3** | sensitivity_result | Estimates are converged: the change from 5,000 to 10,000 paths is 0.0027 months and 0.042pp. | `validation_v1` → `/convergence` | `f89fd2ba…` | Intervals are **Monte Carlo intervals over simulated paths** — they measure whether enough paths were run, not uncertainty about real sellers. Never "confidence interval" | "bootstrap CIs" (`CORRECTED_CLAIMS.md` #4) |
| **P-4** | sensitivity_result | The remittance basis is `net_sales`, not GMV; the sweep shows the choice is material. | `validation_v1` → `/revenue_definition` | `f89fd2ba…` | Platforms settle after returns, so GMV would charge a share of money never received. Spec amendment A-1 | the original GMV basis in `baseline_v1` |

---

## 4. Product implications — judgements, not measurements

| ID | Class | Claim | Basis | Required qualifier |
|---|---|---|---|---|
| **I-1** | product_implication | Revenue-contingency converts a fixed obligation into a variable one, and that conversion has a measurable price. | M-3, P-1, P-2 | The defensible framing is **not** "RBF is cheaper" — at the illustrative cap it is not. It is that price and structure are separable and were separated here |
| **I-2** | product_implication | Price and structure must be reported separately, or a comparison silently attributes a pricing choice to a structural property. | M-3, M-4, D-015 | This is the methodological contribution. State it as a design rule the project adopted after getting it wrong |
| **I-3** | product_implication | A provider underwriting revenue-contingent contracts is exposed to duration risk in ordinary downturns and to principal loss in closure. | S-2 with S-3 | Both halves, always. S-2 alone reads as "RBF always recovers", which S-3 falsifies |

---

## 5. Open real-world questions — cannot be settled by this project

| ID | Claim | Why it is open |
|---|---|---|
| **Q-1** | Whether any of this describes real seller behaviour. | No observed revenue, repayment or default data exists in the project. |
| **Q-2** | Whether the modelled contracts are affordable. | Burden is measured against revenue, not against what the seller retains. Margins, costs, reserves and other debts are outside the model. |
| **Q-3** | Whether the fixed-arm comparison is fair. | The fixed arms are modelled as **always repaid**. Real fixed-payment lending carries default risk this comparison does not model, which flatters the fixed arm. |
| **Q-4** | Whether the burden thresholds (10/15/20/25%) mark real hardship. | They are illustrative reporting bands chosen for this study. No validated hardship cutoff was used and none is claimed. |
| **Q-5** | Whether `j = 18%`, `N_B = 12`, the seasonality shapes, `m` and `F` reflect the Vietnamese market. | All are assumed inputs. None was externally sourced. Phase B's literature matrix is where this gets tested. |

---

## 6. Withdrawn — do not restate in any form

| Claim | Why withdrawn | Reference |
|---|---|---|
| "0.92 AUC" / any predictive-skill number from the ensemble | Circular: `generate_data.py` creates the `defaulted` label by evaluating a hand-written weighted formula over the same features the model is then trained on. The metric measures the generator's noise variance | D-001; `README.md`; enforced by `test_no_withdrawn_claims.py` |
| "RBF costs ~2.3× the interest of a conventional loan" | Conflates price with structure. Cost is proportional to `f` (P6a) and APR is jointly determined by `f` and the path (P6b) | D-015; `DERIVATIONS.md` P6; `CORRECTED_CLAIMS.md` #2 |
| "Fixed payments are immune to underreporting — a structural advantage" | True that scheduled payments do not read revenue; the value judgement does not follow | `CORRECTED_CLAIMS.md` #3 |
| "Confidence intervals" / "bootstrap CIs" | They are Monte Carlo intervals over simulated paths | D-014; `CORRECTED_CLAIMS.md` #4 |
| "Revenue-based repayment extends the term instead of defaulting" | Asserts default-prevention. `closure_m7` is 100.0% incomplete at **both** registered cap factors | D-037 (this phase); S-3 |
| "A conventional 12-month amortizing loan at 18%" | "Conventional" implies a sourced market rate. The 18% is an assumed input | D-037 (this phase) |
| "Equal cost" as a name for `f*` | The cap was solved on one flat reference path; on simulated paths the realised rate differs | D-037 (this phase) |
| A 5.77% cap-overshoot rate | My own error — computed `duration × remittance` while ignoring the clipped final payment. 0 breaches in 6,794 structures | D-029 |

---

## 7. Enforcement

Three tests keep this ledger from becoming decoration:

- `backend/tests/test_no_withdrawn_claims.py` — the withdrawn model metrics cannot reappear on any surface.
- `backend/tests/test_public_copy.py` — scans live surfaces for the phrasings in §6, with a directional negation window so a disavowal stays legal and an assertion fails. It is itself tested against the verbatim sentences this project retracted.
- `backend/tests/test_validation_artifact.py` — the `validation_v1` canonical form is numerically identical to its source, and the four registered baselines are unchanged.

A claim added to a draft but not to this table is caught by review, not by CI.
That is a known gap and the reason Gate C exists.
