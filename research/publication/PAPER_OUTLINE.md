# Paper Outline

**Status:** Publication phase. Gate A passed at `af2fc2d`. Subsequent editorial corrections to Gate-A prose — the recovery-ordering and target-versus-cost families — are logged in **D-047** and **D-048**; they changed **no formula, no generator, and no registered artifact**, and all five canonical checksums are unchanged.
**Governing documents:** `research/CLAIM_LEDGER.md` (what may be claimed), `research/METHODOLOGY_SPEC.md` v1.0 + A-1…A-9 (what was specified), `research/publication/LITERATURE_MATRIX.md` (what external evidence exists).

---

## The argument, in one paragraph

**Pricing and payment structure are separate questions, and conflating them is the error this project made and corrected.** A revenue-contingent contract makes each payment a fixed share of realised revenue, so the seller's payment falls when eligible revenue falls. Under adverse revenue paths this reduces the seller's payment burden relative to a fixed instalment carrying the same contractual repayment target on the reference path.

The provider side is not the mirror image of that statement. It changes *when* the provider is repaid, and the direction is conditional: revenue-contingent recovery may **lead or lag** the cost-matched fixed schedule according to the exact P4 condition on realised mean eligible base against `B* = P/r`. Both directions occur in this scenario library — recovery lags in the severe downturn and leads at exactly baseline revenue — so the direction is reported per scenario and never as a property of the structure. Where permanent cessation precedes completion while a contractual balance remains, no further payment occurs and the balance stays unrecovered. The two effects are the same mechanism seen from opposite sides of the contract, and any honest comparison must report both.

Separating the price of the contract (the cap factor `f`) from its structure (revenue-contingent versus fixed) is what makes the comparison interpretable at all: at one price the revenue-contingent arm looks expensive, and at another it does not. What repricing leaves unchanged is the **pre-cap payment rule** — each payment remains the same fixed share of net sales. What it changes is the **contractual target** `A·f`, and therefore the stopping point, the terminal clipped payment, and the realised outcomes on every path. Price and payment rule are analytically separable but jointly determine what actually happens, so **do not write "structural behaviour unchanged"**.

---

## Why this is a simulation, stated up front

The head-to-head question — how a revenue-contingent contract and a **cost-matched** fixed contract compare on seller burden *and* provider recovery under **identical** revenue paths — requires observing both contracts on the same seller. That counterfactual does not exist in any public dataset. The literature reviewed (see `LITERATURE_MATRIX.md` §5, Gap R-2) contains no head-to-head provider-recovery comparison for small-business financing. A paired simulation is the available instrument. Its limitation is exactly its design: it describes contract mechanics under stated assumptions, not seller behaviour.

---

## Section plan, with every figure bound to a source

**Numbering matches the manuscript exactly.** The manuscript's Abstract is unnumbered; numbered sections run §1–§15. An earlier draft of this outline numbered the Abstract as §1 and omitted "Why simulation", putting every subsequent reference one out of step.

Notation: **[ledger-ID | artifact → JSON path]**. Every quantitative statement in the manuscript carries one. Figures are described here; they are **not** generated in Phase B.

### Abstract *(unnumbered in the manuscript)*
**Contains the headline results**, each with its artifact source note, and each accompanied in the same passage by: that it is simulation output; that 15% is an illustrative burden band; that burden is payment ÷ GMV; and that the fixed arm's recovery is scheduled recovery under a full-and-on-time payment assumption. *(An earlier draft of this outline said the abstract contained no numbers. It does.)*

### §1 Introduction and motivation
- MSME finance constraint as motivation **[L-01]**. Vietnam-motivated, illustratively parameterised — **no parameter claim** (A-8).
- Platform-recorded revenue makes revenue-contingent contracting mechanically possible **[L-02, L-05]**.
- **No CIC prevalence claim** (Gap V-1).

### §2 Why simulation, and what that costs
- The counterfactual — both contracts on one seller under one realised path — is not in public data, and each seller takes at most one contract.
- Negative claims scoped to the documented searches: *"We did not identify … in the searches documented through 2026-08-13."* Never "the absence is a finding".
- States the cost of the method: the revenue process is one we specified.

### §3 Related literature
Four strands, each with its transfer limit stated in the text:
1. Contingent repayment theory — **[L-09, L-10]**. Student loans.
2. Revenue-based financing empirics — **[L-07]** (closest to this contract; working paper; South Africa), **[L-08]**.
3. Repayment burden — **[L-11, L-12, L-13, L-15]**. Student loans; **[L-16, L-17]** firms/households but a different mechanism.
4. Pricing of contingency — **[L-18, L-19]**.
- State **Gap R-1** (no academic MCA literature) and **Gap R-2** (no head-to-head provider-recovery comparison) explicitly. These define the contribution.

### §4 Research question and contribution
- Question: under identical revenue paths, how do seller burden and provider recovery move together when repayment is revenue-contingent rather than fixed, holding the contractual repayment target constant on the reference path?
- Contribution: (a) the paired cost-matched design; (b) analytical propositions independent of the simulation; (c) the price/structure separation; (d) an explicit incomplete-recovery characterisation.

### §5 Contract definitions and comparison design
| Arm | Definition | Source |
|---|---|---|
| **RBF** | `p_t = min(r·B_t, C − Σ_{s<t} p_s)`, `C = A·f` | `DERIVATIONS.md` Setup |
| **FIX-A** | `q_t = P` for `t ≤ N`, `N·P = C` — matched principal, total and term on the reference path | `METHODOLOGY_SPEC.md` §7.1 |
| **FIX-B** | Illustrative 18%/12-month amortizing reference | `METHODOLOGY_SPEC.md` §7.2 (A-8) |

- Matched benchmark at `f = 1.20`: term **13** months, payment **17,076,923 VND**, implied APR **37.8694%** **[baseline_v3 → /match_benchmark_a]**.
- At `f* = 1.0945`: term **12**, payment **16,873,542**, APR **18.3980%** **[baseline_equalcost_v2 → /match_benchmark_a]**.
- Duration is integer-valued, so cost-matching is exact on total but stepwise in APR — **[M-3, P-1]**.
- Comparability limit: an APR loan prices time, a factor-rate cap prices a multiple regardless of time **[L-23, L-24]**.

**Figure 1** — contract payment schedules on the reference path, three arms. **[baseline_v3 → /match_benchmark_a; /terms]**

### §6 Simulation methodology
- Frozen spec before outcome analysis; ADEMP-style reporting **[L-27]**; pre-specification defends against researcher degrees of freedom **[L-31]**.
- 500 paths/scenario, base seed 20260803, bootstrap seed 90210 **[baseline_v3 → /n_paths, /base_seed]**.
- **Terminology, load-bearing:** intervals are **Monte Carlo intervals over simulated paths**, never confidence intervals — synthesis of **[L-28, L-27, L-29]**, per **Gap M-1**. They measure whether enough paths were run; more paths narrow them without adding a fact about the world.
- Convergence checked for **two estimators on one scenario only**: `Δn_HPB(θ=0.15)` and `ΔRR(12)` under sustained −40% decline, moving **0.0027 months** and **0.042pp** from 5,000→10,000 paths **[P-3 | validation_v2 → /convergence]**. **Do not write "estimates are converged".**
- Burden denominator disclosure: contractual remittance is a share of **net sales**; displayed burden is payment ÷ **GMV**, equal to `r·(1 − return rate)`, constant only where that ratio is fixed — `returns_spike` is the explicit exception.

### §7 Analytical propositions
Stated as theorems, **not** simulation output — the ledger's class-dependent qualifier applies **[CLAIM_LEDGER §0]**.

**Column note.** "Related ledger row" is *related*, not equivalent — not every proposition has a dedicated ledger entry, and a ledger row is a **claim licence**, not a proof. The proof always lives in `DERIVATIONS.md`. An earlier draft mapped P1→M-1 and P4→I-3 as though the ledger row *were* the proposition; both were wrong.

| Proposition | Proof | Statement | Related ledger row |
|---|---|---|---|
| P1 | `DERIVATIONS.md` **P1** | RBF burden ≡ `r` on the contractual base until the final capped payment | *(none — M-1 is the cap-settlement inequality `Σ payments ≤ cap`, a different result)* |
| P2 | `DERIVATIONS.md` **P2** | Fixed burden has elasticity −1 in revenue; a −50% month doubles it | *(none)* |
| P3 | `DERIVATIONS.md` **P3** | Cap reached by `k` iff `S_k ≥ A·f/r`; duration is first passage, not a function of the terminal total | *(none — M-2 is under-reporting)* |
| P4 | `DERIVATIONS.md` **P4** | For `k ≤ N`, before either arm caps out: RBF leads on recovery iff `(1/k)·S_k > B* = P/r`; integer rounding makes `B* < B̄` | *(none — I-3 is a downstream product judgement drawing on P4, not its proof)* |
| P5 | `DERIVATIONS.md` **P5** | Under-reporting rescales **uncapped** payments and raises the required cumulative base by `1/ω`; duration does **not** scale by `1/ω` | **M-2** |
| P6 | `DERIVATIONS.md` **P6** | `A·f` is the contractual **target**, path-independent; realised total equals it only on completion. APR is path-dependent | **M-3, M-4** |
| P7 | `DERIVATIONS.md` **P7** | Completion ⇔ ∃ finite `t ≤ H` with `S_t ≥ Θ = f·A/r`. For finite `H` only, equivalent to `S_H ≥ Θ`. `S_∞ = Θ` completes only if a finite partial sum attains it | **M-5, M-6, M-7** |

**Figure 2** — P7 boundary: geometric decline, completion vs ρ, showing ρ\* = 11/12 at `f = 1.20` and 0.9086 at `f* = 1.0945`. **[M-6 | DERIVATIONS P7]**

### §8 Results
**Table 1** — arm comparison across the ten non-closure scenarios. **[baseline_v3 → /scenarios/*]**

Stable scenario **[baseline_v3 → /scenarios/stable]**:
- RBF duration **12.86** months, mean burden **0.0933**, RR(12) **96.56%**
- FIX-A duration 13, burden **0.0943**, RR(12) **92.31%**
- FIX-B duration 12, burden **0.0936**, RR(12) **100%**
- RBF leads FIX-A on RR(12) by **4.25pp** — an artifact of integer rounding in the matching rule (P4 corollary), **not** an economic finding. **[I-3]**

Severe downturn **[baseline_v3 → /scenarios/severe_downturn]**:
- RBF: duration **18.718**, burden **0.0943**, high-burden months at θ=0.15 **0.0**, RR(12) **65.46%**
- FIX-A: duration 13, burden **0.1636**, high-burden months **6.85**, RR(12) **92.31%**
- **Both halves, always** — this is the paper's central table and neither column may appear alone. **[S-1, I-3]**

**Figure 3** — seller burden and provider recovery on one panel per scenario, paired. Never a burden-only chart.
**Figure 4** — high-burden month counts by threshold (10/15/20/25%), stressing these are **illustrative reporting bands, not validated hardship cutoffs** **[Q-4]**. Distributional reporting follows **[L-13]**.

### §9 Pricing versus structure
- At `f = 1.20` the simulated contract is substantially more expensive than the illustrative 18% amortizing reference; at `f* = 1.0945` it is not **[P-2]**. State precisely what is held constant: the **pre-cap payment rule** is unchanged, the **cap factor changes the contractual target** and therefore completion timing, terminal clipping and the realised stream. Price and payment rule are analytically separable but **jointly determine realised outcomes** — do not write "structural behaviour unchanged".
- `f* = 1.0945` is the **nearest grid match**: 19.537656% against 19.561817%, residual **≈0.02416pp** **[P-1 | validation_v2 → /pricing/equal_cost, /pricing/benchmark_b_apr]**. Not an exact solution — duration is integer-valued, so achievable APRs are discrete.
- Same scenarios repriced **[baseline_equalcost_v2 → /scenarios/*]**: stable duration **11.784**, severe downturn **17.504**, sustained decline **16.01**.
- **The retracted claim.** An earlier version stated "RBF costs ~2.3× the interest of a conventional loan". Withdrawn (D-015): the contractual repayment target `A·f` is proportional to `f` (P6a) — and realised repayment equals that target only upon completion — while APR, among completed paths with IRR-defined payment streams, is jointly determined by `f` and the path and is undefined where a path does not complete (P6b), so a ratio quoted at one `f` is a pricing result, not a structural property. **Reporting the retraction is part of the contribution** — it is the concrete instance of the conflation the paper argues against.
- Regulatory recognition of the comparability problem **[L-23, L-24]**; contingency carries a premium **[L-18, L-19]**.

**Figure 5** — cap-factor sweep: effective APR against `f`, with the reference APR and `f*` marked, showing the step structure. **[validation_v2 → /pricing/sweep]**

### §10 Closure, incomplete recovery and censoring
- Across the ten non-closure scenarios, incomplete recovery is **0.0%** and total repaid identical at the cap **[S-2]** — **horizon- and scenario-bounded**, and none of those ten reaches zero revenue. Must never appear without §10's closure results.
- Closure at `f = 1.20` **[S-3 | baseline_closure_v2 → /scenarios/*/RBF]**: `closure_m7` **100.0%** incomplete (RR(24) 44.30%); `closure_m13` **76.2%** (RR(24) 96.53%); `temp_closure` **2.0%** (RR(24) 99.98%).
- At `f* = 1.0945` **[S-4 | baseline_closure_equalcost_v1]**: **100.0%**, **7.6%**, **0.0%**. The `closure_m13` figure moves by a factor of ten with **price alone** — P6a made visible.
- **Incomplete recovery ≠ principal loss** **[I-3]**. `closure_m13` recovers ≈214.3M against a 185M advance — principal covered despite 76.2% incomplete. Only `closure_m7` (≈98.3M) shows a principal shortfall, and it recovers the **same absolute amount at both cap factors** because that path is revenue-limited, not cap-limited.
- **Censoring, two different denominators (A-9).** `duration_mean` is computed over completing paths — a survivor statistic estimating `E[T | completion occurs by horizon H]`, not `E[T]`. `apr_mean` is computed over **IRR-defined** paths, which is a different and generally larger set: an incomplete path that made payments still has a rate. In `closure_m13` at `f = 1.20` that is 119 completed against 500 rate-defined. Never share one qualifier between them. Do **not** write `E[T | T ≤ C]`: `C` is already the VND contractual cap. Framed via **[L-36, L-37]**, machinery via **[L-33, L-34, L-35]**. Per **Gap M-2**, the downward bias is argued as a mathematical consequence and **no source is cited as having quantified it**.
- A short mean duration beside a high incomplete-recovery rate is not a fast contract — it is one where the slow paths were dropped rather than counted.

**Figure 6** — closure panel: incomplete recovery and RR(24) at both cap factors, three closure scenarios.

> ~~**Figure 7** — survivor illustration: duration distribution with the censoring boundary marked.~~ **REMOVED (D-046).** The registered artifacts are **aggregates** — `duration_mean`, `duration_sd`, `incomplete_recovery_rate` — and do **not** contain the path-level duration distribution this figure would require. Producing it would mean generating a new artifact, which this pass is not authorised to do. The censoring point is made in prose and by the paired `duration_mean` / `incomplete_recovery_rate` reporting instead.

### §11 Product implications
- Price and structure must be reported separately, or a pricing choice is silently attributed to a structural property **[I-2]**.
- A provider is exposed to duration risk in ordinary downturns and to an unrecovered contractual balance where permanent closure precedes completion **[I-3]**.
- The guardrail finding, both halves: the hardship **floor** never activates — 0 of 36,000 month-observations, `μ = 0.25 < h = 0.50` — while the **ceiling binds**, 6,009 of 36,000, changing 6 of 10 scenarios (`apr_mean` 6, `burden_mean` 6, `recovery_ratio` 3, `duration_mean` 1). **[N-2′ | validation_v2 → /rbf_g_breakpoint; baseline_v3 → /scenarios/*/RBF-G]**. Presenting the floor null alone would read as a whole-arm null, which is false.
- **No predictive-validity claim.** The demonstration score is trained on synthetic data whose label is a formula over the same features. Own evidence: generating-function AUC **0.9098** vs reported ensemble **0.9182** **[R-000 | research/analysis/00_audit_evidence.py]**. Adjacent mechanism **[L-38]**; per **Gap S-1** the circularity argument is made in the paper's own words.
- Fixed arms are modelled as **paid in full and on time** — an optimistic scheduled-recovery benchmark, not a realized-recovery one **[Q-3]**.

### §12 Limitations and responsible use
- No observed seller revenue, repayment or default outcome exists anywhere in this project. No causal, predictive or population claim.
- **No affordability claim** — burden is measured against revenue, not against what the seller retains **[Q-2]**; thresholds are illustrative bands **[Q-4]**.
- **No default-prevention claim** — §10 is the counterexample.
- Parameters `j`, `N_B`, seasonality shapes, `m`, `F` are unsourced assumptions **[Q-5]**.
- Synthetic-data limits **[L-39, L-40]**; self-reported-data limits **[L-41, L-42, L-43]** — note the ω sweep is **mechanical**, whereas **[L-07]** documents *behavioural* revenue diversion, which this study does not model.
- Structural-uncertainty framing **[L-30]**.
- Responsible use: this is not underwriting guidance, and the demonstration product must not be presented as validated.

### §13 Conclusion
Restate the separation. State plainly what would change the conclusion: observed seller revenue paired with adjudicated repayment outcomes.

### §14 References
Every entry from `LITERATURE_MATRIX.md`, verified. No entry may appear that is not in the matrix.

### §15 Reproducibility statement
- Five canonical artifacts with SHA-256 **[CLAIM_LEDGER §0]**.
- **Numeric** reproducibility at published precision on every platform tested; **byte** reproducibility within a fixed runtime — 3/5 byte-identical on macOS CPython 3.11.5 (9 and 2 last-bit float differences), 5/5 on Linux 3.10.12 **[D-041, D-043]**. **Never claim cross-platform byte determinism.**
- Verifier: `research/verify_reproduction.py`, reporting byte and numeric equality separately.
- Disclose: the embedded `canonical.determinism` field carries the withdrawn claim and is **superseded, not rewritten** (D-044) — the artifacts were not regenerated.
- Test counts: **1,042 non-browser tests pass — 403 backend and 639 simulation.** Nine browser checks are defined and excluded from that total; they passed in the earlier browser-capable run recorded at D-036, and skip where Playwright or Chromium is absent. Skips are never reported as passes.

---

## Binding rules checklist for drafting

| Rule | Where enforced |
|---|---|
| No predictive-validity claim | §11, §12 |
| No observed-seller / causal / population claim | §2, §12 |
| No affordability or default-prevention claim | §10, §12 |
| Contractual target vs realized repayment distinguished | §7 (P6), §9, §10 |
| Survivor statistics vs portfolio outcomes distinguished | §10 |
| Seller burden paired with provider recovery | §8 Table 1, Figures 3 and 6 |
| `f = 1.20` paired with `f* = 1.0945` | §9, §10 |
| Hardship-floor null beside live ceiling result | §11 |
| Uncomfortable and null results preserved | §9 (2.3× retraction), §11 (N-2′), §8 (4.25pp is a rounding artifact) |
| Every quantitative statement has a ledger ID + artifact path | throughout |
| Withdrawn 0.92 cited only to explain its withdrawal | §11 |
| Recovery ordering stated per scenario, never as a universal direction | §8, §13; P4 |
| Editorial corrections to Gate-A prose logged, with no formula, generator or registered artifact changed | D-047, D-048 |

**If the literature contradicts a frozen claim: stop and report. Do not silently edit.**
