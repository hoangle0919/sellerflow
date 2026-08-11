# Revenue-Contingent Financing Under Volatile Sales: Separating Price from Structure in a Paired Simulation Study

**Draft — Phase B.** Gate A frozen at `af2fc2d`. No Gate A document is amended by this manuscript.

> **Source-note convention.** Every quantitative statement carries a bracketed note of the form **[ledger-ID | artifact → JSON path]** identifying the claim-ledger entry (`research/CLAIM_LEDGER.md`) and the canonical artifact it derives from. A number without such a note is a defect, not a stylistic choice.
>
> **All quantitative output is simulation under modelled assumptions.** No observed seller revenue, repayment, or default outcome exists anywhere in this study.

---

## Abstract

Revenue-contingent financing makes each repayment a fixed share of realised revenue rather than a fixed instalment. The intuitive case for it is that the seller's payment falls when revenue falls. The intuitive case against it is that the financier waits longer to be repaid. Both are correct, and they are the same mechanism observed from opposite sides of the contract; reporting either alone misstates the product.

This paper separates two questions that are routinely conflated: the **price** of a revenue-contingent contract, set by its cap factor, and its **structure**, meaning how payments respond to revenue. Using a paired simulation in which a revenue-contingent contract and a cost-matched fixed instalment are applied to identical revenue paths, we show that at the illustrative cap factor `f = 1.20` the revenue-contingent arm removes **6.85** months above a 15% burden threshold in a severe-downturn scenario while recovering **65.46%** of its target by month 12 against the fixed arm's **92.31%** **[S-1 | `baseline_v2_canonical.json` → `/scenarios/severe_downturn`]**. Repricing the identical structure at the nearest reference-path grid match `f* = 1.0945` changes the cost comparison entirely without changing the structural behaviour **[P-1, P-2 | `validation_v1_canonical.json` → `/pricing`]** — which is why a cost ratio quoted at a single cap factor is a pricing result and not a property of revenue-contingent repayment.

We further characterise incomplete recovery exactly. Completion requires that some **finite** month `t ≤ H` satisfy `S_t ≥ f·A/r`; for a finite horizon this reduces to the terminal condition, but for an unbounded lifetime it does not, and equality of the lifetime sum is insufficient unless a finite partial sum attains the threshold. Where permanent revenue cessation precedes completion while a balance is outstanding, recovery genuinely fails: closure from month 7 leaves **100.0%** of simulated paths incomplete at both registered cap factors **[S-3, S-4]**. Incomplete recovery is not equivalent to principal loss, and we distinguish them.

We make no predictive, causal, affordability or default-prevention claim. The propositions are proved and hold for any revenue path; the magnitudes are illustrations under parameters we chose.

---

## 1. Introduction and motivation

Access to finance is a persistent constraint on small enterprises in developing economies. The IFC/SME Finance Forum *MSME Finance Gap* database estimates that roughly 40% of formal micro, small and medium enterprises in developing countries — some 65 million firms — have unmet financing needs (L-01). That estimate is a benchmarking construct rather than an observation: it applies debt-to-sales ratios from ten developed markets to the enterprise population of each developing economy, and its own documentation states the assumption that firms "have the same willingness and ability to borrow as their counterparts in well-developed credit markets". We use it to motivate the question, not to parameterise anything.

The motivating setting for this study is small e-commerce sellers in Vietnam, where platform activity — revenue, order counts, returns, fulfilment performance — accrues continuously in a form a financier could in principle observe (L-02). **This study is Vietnam-motivated and illustratively parameterised, not Vietnam-calibrated.** No parameter in the specification was estimated from Vietnamese data, and we make no claim about the prevalence of thin credit-bureau files among Vietnamese sellers; we found no source that would support one.

Continuously recorded revenue makes a particular contract mechanically possible: repayment as a fixed percentage of revenue, continuing until a contractual cap is reached. The question this paper addresses is what that contract does — to the seller, and to the financier — relative to a fixed instalment of the same contractual cost, under the same revenue path.

---

## 2. Why simulation, and what that costs

Answering the question empirically requires observing two contracts on the same seller over the same revenue realisation. That counterfactual does not exist in public data. The literature we reviewed contains no head-to-head comparison of seller burden and provider recovery under revenue-contingent versus cost-matched fixed schedules for small-business financing (Gap R-2, `LITERATURE_MATRIX.md` §5).

A paired simulation supplies the missing counterfactual by construction: every contract is applied to the identical generated path, and all comparisons are within-path paired differences. The cost is equally clear. The revenue process is one we specified. The results describe **contract mechanics under stated assumptions**, and nothing about how sellers behave. We state this once here and again in §12, and we have tried not to blur it anywhere between.

Underwriting on cash-flow data — as distinct from repayment structure — is a separate and better-evidenced literature (L-04, L-05, L-06). We touch it only in §11, and only to disclaim.

---

## 3. Related literature

**Contingent repayment theory.** The canonical treatment is the income-contingent loan literature, where repayment scales with realised income and the obligation carries consumption-smoothing and default-insurance properties (L-09). Nerlove (1975) states the standard critique — adverse selection, incentive effects, and the transfer of risk to the financier (L-10). This body is about **students**, not firms; the construct transfers, the findings do not, and we flag this at each use.

**Revenue-based financing.** Russel, Shi and Clarke (2025) is the closest published work to the contract studied here: transaction-level data from a South African payments platform, with repayment as automatic deduction of a fixed share of daily on-platform revenue until a set amount is repaid (L-07). They state directly that the structure "shifts risk to the financier, as repayment speed changes with revenue", and document that financed firms routed approximately 16% less revenue through the platform after eight months, slowing repayment. Two limits matter for us: it is a working paper, and its central finding is **behavioural revenue diversion**, which our model does not represent. Our under-reporting sweep is mechanical — we impose ω, we do not model a seller choosing it. Cordaro et al. (2022) provide experimental evidence on performance-contingent repayment for small firms (L-08).

**We found no peer-reviewed academic study of the US merchant cash advance market** (Gap R-1). Searches returned vendor marketing and search-optimised content, which we excluded. The only authoritative US-market material is regulatory (L-23, L-24, L-26). The absence is itself informative: a product class with documented enforcement actions has attracted regulatory attention without a corresponding academic literature.

**Repayment burden.** Chapman and Dearden (2017) define repayment burden as the proportion of income required to service the obligation and argue it drives both default probability and living standards (L-11); Chapman and Lounkaew (2015) show fixed schedules concentrate burden severely in low-income states (L-12); Barr et al. (2019) state the design contrast plainly — fixed repayment creates high burden precisely when income is low, whereas income-linked repayment builds in automatic insurance against inability to repay (L-15). Chapman et al. (2010) establish the methodological point we adopt: burden must be computed **across the distribution**, not at the mean (L-13), which is why we report high-burden month counts and percentiles rather than means alone.

Two firm-side and household-side sources bear on the mechanism but test different instruments. Battaglia, Gulesci and Madestam (2024) randomise a payment-**deferral option** and find flexibility acts as insurance, raises risk-taking and lowers default (L-16) — this is not revenue-proportional repayment and we do not describe it as such. Ganong and Noel (2020) show that short-term payment size, not total obligation, drives default and consumption, since principal reduction had no effect while maturity extension had large ones (L-17) — consumer mortgages, and again a different instrument.

**The price of contingency.** Herbst and Hendren (2024) quantify the risk-shifting critique: adverse selection implies a typical borrower would repay about $1.64 in present value per dollar financed for an equity-like market to clear (L-18). Igan, Kim and Levy (2022) find persistent, material premia on state-contingent sovereign instruments (L-19). Neither is about SME finance, but the logic — a contingent contract must be priced above fixed debt to compensate the financier — is exactly why price and structure must be separated before either is discussed.

---

## 4. Research question and contribution

**Question.** Under identical revenue paths, how do seller payment burden and provider recovery move together when repayment is revenue-contingent rather than fixed, holding contractual cost constant?

**Contribution.**

1. **A paired, cost-matched design.** Principal, total contractual repayment and term are matched on a reference path, so the only difference between the primary arms is the *timing* of payments within the term.
2. **Analytical propositions independent of the simulation.** Seven propositions, proved for any revenue path and asserted numerically against the engine, so the structural claims do not rest on the generated data.
3. **An explicit price/structure separation**, including a documented retraction of our own earlier conflation (§9).
4. **An exact characterisation of incomplete recovery**, including the boundary case where the lifetime sum equals the threshold but no finite partial sum attains it (§7, §10).

---

## 5. Contract definitions and comparison design

Let `B_t` be the remittance base in month `t` (contractually, net sales), `S_k = Σ_{t≤k} B_t`, `A` the advance, `f` the factor rate, `C = A·f` the contractual cap, and `r` the remittance rate.

**Revenue-contingent arm (RBF).** `p_t = min(r·B_t, C − Σ_{s<t} p_s)`, `p_t ≥ 0`. Payments continue until cumulative payments reach the cap.

**Fixed arm, matched (FIX-A).** `q_t = P` for `t ≤ N`, zero afterwards, with `N·P = C`. Principal, total contractual repayment and term are identical to RBF **on the reference path**. This isolates payment timing and is the primary comparison.

**Fixed arm, external reference (FIX-B).** An illustrative 18% nominal, 12-month amortizing schedule. The 18% is an assumption chosen for this study — **not a market rate**, and not observed or externally sourced anywhere in this project (spec amendment A-8).

At the illustrative cap factor `f = 1.20`, matching on the reference path gives a term of **13 months**, a payment of **17,076,923 VND** and an implied APR of **37.8694%** **[`baseline_v2_canonical.json` → `/match_benchmark_a`]**. At `f* = 1.0945` the matched term is **12 months**, payment **16,873,542 VND**, APR **18.3980%** **[`baseline_equalcost_v1_canonical.json` → `/match_benchmark_a`]**.

**A comparability limit, stated wherever the arms appear together.** An APR loan prices time; a factor-rate cap prices a multiple regardless of time. The two are not commensurable without conversion, and financial regulators have said so: New York's 23 NYCRR 600 requires standardised disclosure including APR for commercial financing under $2.5m (L-23), and California's disclosure regime identifies describing price as an "X% fee rate" or "Y% factor rate" — particularly where those diverge materially from APR — as a confusing representation (L-24). We report both, and we never quote one as the other.

---

## 6. Simulation methodology

The specification was frozen before any outcome analysis; amendments are logged with the result visible at the time. This matters because researcher degrees of freedom in choosing a data-generating mechanism and performance measures allow spurious claims of superiority for essentially any method (L-31). We follow simulation-reporting practice in pre-specifying and reporting the design, the number of replications, and how it was chosen (L-27), and adopt the standard separation of parameter, stochastic, heterogeneity and structural uncertainty (L-30).

Monthly revenue is generated multiplicatively from a baseline level with deterministic trend, a fixed seasonal multiplier, a shock multiplier and lognormal idiosyncratic noise. Operational variables are **derived through accounting identities rather than sampled independently** — `orders = R/AOV`, returns and fees as deductions — correcting an independence defect in the project's original generator. Each run applies all arms to the same path; 500 paths per scenario, base seed 20260803 **[`baseline_v2_canonical.json` → `/n_paths`, `/base_seed`]**.

**Two terminological commitments, both load-bearing.**

*First, intervals.* Every interval reported in the underlying artifacts is a **Monte Carlo interval over simulated paths**. It measures whether enough paths were run for a number to be stable under our chosen generative parameters. It is **not** a confidence interval and says nothing about real sellers; running more paths narrows it without adding a single fact about the world. We could find no single source stating this prohibition, and we present it as synthesis: Monte Carlo error is a distinct quantity from inferential uncertainty (L-28); Monte Carlo standard error quantifies uncertainty arising from finite repetitions (L-27); and international measurement standards deliberately use "coverage interval" rather than "confidence interval" for precisely this distinction (L-29).

*Second, convergence.* We checked convergence for **two estimators on one scenario**: the paired differences `Δn_HPB(θ = 0.15)` and `ΔRR(12)` under a sustained −40% decline, which move **0.0027 months** and **0.042 percentage points** between 5,000 and 10,000 paths **[P-3 | `validation_v1_canonical.json` → `/convergence`]**. This does not establish that every estimator in the study is converged, and we do not claim it.

**A disclosure about the burden denominator.** The contract charges its share on **net sales**. The burden statistic we display uses **GMV** as its denominator, so it equals `r·(1 − return rate)` and moves when the return rate moves. It is constant only in scenarios where the net-sales/GMV ratio is fixed; most registered scenarios hold it fixed, and `returns_spike` is the explicit exception where the displayed burden varies.

---

## 7. Analytical propositions

These are theorems about the contract, proved in `research/DERIVATIONS.md` and asserted numerically against the engine. **They are not simulation output**, and the simulated-output qualifier that governs §8–§10 does not apply to them. Their limitation is different in kind: they describe a contract, and a contract is not a market.

**P1 — Burden is definitional.** Until the final capped payment, `p_t / B_t = r` exactly on the contractual base. The revenue-contingent arm's flat contractual burden is a definition, not an empirical finding, and no simulation could provide evidence for it.

**P2 — Fixed burden has elasticity −1.** For the fixed arm, burden `P/B_t` is strictly decreasing in `B_t` with constant elasticity −1: a revenue fall by factor λ raises burden by exactly `1/λ`. A −50% month doubles it, for any `P` and any `B_t`. This is the structural asymmetry the study exists to quantify, and it requires no calibration to state.

**P3 — Cap condition.** The cap is reached by month `k` iff `S_k ≥ A·f/r`. Duration is the **first passage time** to that threshold — a property of the cumulative trajectory, not of its endpoint. Two paths with the same terminal cumulative base need not cross in the same month.

**P4 — Recovery ordering, exactly.** Before either contract caps out, revenue-contingent cumulative recovery exceeds fixed cumulative recovery through `k` **iff** the realised mean eligible base exceeds `B* = P/r`. This is not captured by the labels "declining" versus "non-declining": a declining path whose realised mean still clears `B*` leads, and a flat path below `B*` lags. A corollary matters for reading §8: benchmark matching sets `N = ⌈C/(r·B̄)⌉`, so whenever the term rounds up, `B* < B̄` strictly.

**P5 — Under-reporting.** If the provider observes `ω·B_t`, cumulative recovery scales exactly by ω and the required cumulative base rises by `1/ω`. **Duration does not scale by `1/ω`** — the threshold does, and duration is first passage to it. Only **uncapped** payments rescale; the final payment is clipped to the remaining balance and need not scale. Invariance of the total is conditional on the cap still being reached.

**P6 — Cost and rate.** (a) `A·f` is the contractual repayment **target**, path-independent; realised total repayment equals it **only upon completion**. (b) Effective APR is not a well-defined property of the contract: two sellers on identical terms face different APRs purely because revenue arrives at different speeds.

**P7 — Completion, exactly.** The contract completes over horizon `H` **iff there exists a finite `t ≤ H` with `S_t ≥ Θ`**, where `Θ = f·A/r`. For a **finite** `H` this reduces to `S_H ≥ Θ`, since `S_k` is non-decreasing. For an unbounded lifetime it does not reduce: the limit is not a partial sum. Writing `S_∞` for the lifetime sum, `S_∞ > Θ` strictly implies completion, `S_∞ < Θ` precludes it at any horizon, and `S_∞ = Θ` completes only if a finite partial sum **attains** `Θ` — which a strictly positive infinite series never does. Under geometric decline the condition is `ρ > ρ*` **strictly**, where `ρ* = 1 − r·B₀/(f·A)`: **11/12 ≈ 0.9167 at `f = 1.20` and 0.9086 at `f* = 1.0945`** **[M-6]**. The threshold moves with the price, so 11/12 must never be quoted as *the* threshold.

Routes to incomplete recovery include zero revenue, a binding maturity or write-off, a binding evaluation horizon, and strictly positive but fast-decaying revenue whose lifetime sum converges below `Θ`. **This list is illustrative, not exhaustive** — the complete characterisation is failure of the finite-time condition, and one route was already overlooked in an earlier draft of our own derivations.

---

## 8. Results

Across the ten non-closure scenarios, all figures below are means across 500 simulated paths **[`baseline_v2_canonical.json` → `/scenarios`]**.

**Stable scenario** **[`baseline_v2_canonical.json` → `/scenarios/stable`]**. The revenue-contingent arm runs **12.86** months mean duration with mean displayed burden **0.0933** and recovers **96.56%** of its target by month 12. FIX-A runs 13 months, burden **0.0943**, RR(12) **92.31%**. FIX-B runs 12 months, burden **0.0936**, RR(12) **100%**.

The revenue-contingent arm leads FIX-A on twelve-month recovery by **4.25 percentage points** at exactly baseline revenue **[I-3 | `baseline_v2_canonical.json` → `/scenarios/stable/{RBF,FIX-A}/recovery_ratio/12`]**. **This is an artifact of integer rounding in the matching rule, not an economic finding** — P4's corollary: `C/(r·B̄) = 12.37` rounds to 13, giving `B* ≈ 0.951·B̄`. We report it as an artifact because reporting it as a result would be the kind of thing this paper argues against.

**Severe downturn.** The trade-off appears in full **[S-1 | `/scenarios/severe_downturn`]**:

| | Duration (months) | Mean burden | Months above 15% burden | RR(12) |
|---|---|---|---|---|
| **RBF** | **18.718** | 0.0943 | **0.0** | **65.46%** |
| **FIX-A** | 13.0 | **0.1636** | **6.85** | **92.31%** |
| FIX-B | 12.0 | 0.1606 | 5.906 | 100% |

The revenue-contingent arm removes **6.85** months above the 15% threshold and holds mean burden essentially at its stable-scenario level — a rise of **1.14%** against stable — while the fixed arm's burden rises by **73.5%** **[S-1 | `baseline_v2_canonical.json` → `/scenarios/{stable,severe_downturn}/{RBF,FIX-A}/burden_mean`, `/n_high_burden/0.15`]**. The same mechanism costs the provider **26.85 percentage points** of twelve-month recovery and extends mean duration by **5.718 months**.

**Neither column may be reported without the other.** The burden reduction and the recovery delay are one mechanism, and a chart showing only the first is a misrepresentation of the second.

The pattern is monotone in shock severity across the stress scenarios: gradual decline (RBF duration 16.148, RR(12) 84.21%; FIX-A 0.894 high-burden months), sustained decline (17.952, 76.04%; FIX-A 3.1), severe downturn as above **[`/scenarios/*`]**.

**On the thresholds.** The 10/15/20/25% bands are **illustrative reporting bands chosen for this study**. They are not validated hardship cutoffs, and no claim is made that crossing one causes distress **[Q-4]**. We report counts across bands rather than a single mean because burden distributions, not burden means, are what the repayment-burden literature identifies as decision-relevant (L-13).

---

## 9. Pricing versus structure

At the illustrative cap factor `f = 1.20`, the simulated revenue-contingent contract is substantially more expensive than the illustrative 18%/12-month amortizing reference. At `f* = 1.0945` it is not. **The structure is identical in both cases.** Whatever one concludes about cost, therefore, is a conclusion about the price, not about revenue-contingent repayment.

`f* = 1.0945` is the **nearest match on the swept cap-factor grid** to the reference path's effective APR, not an exact solution: **19.537656%** against **19.561817%**, a residual of approximately **0.02416 percentage points** **[P-1 | `validation_v1_canonical.json` → `/pricing/equal_cost`, `/pricing/benchmark_b_apr`]**. An exact match is not generally attainable, because duration is integer-valued and the achievable APRs therefore form a discrete set. We report the residual rather than smoothing it away.

Repricing the identical structure **[`baseline_equalcost_v1_canonical.json` → `/scenarios`]** shortens duration in every scenario — stable **11.784**, sustained decline **16.01**, severe downturn **17.504** — because a lower cap is reached sooner. The structural behaviour is unchanged; only the price moved.

### 9.1 A retraction, reported as part of the result

An earlier version of this project stated that "RBF costs approximately 2.3× the interest of a conventional loan." **That claim is withdrawn**, and the reason is the argument of this section. It was wrong on two counts: it fixed `f = 1.20` as though it were intrinsic, when P6(a) shows total contractual cost is proportional to `f`; and it quoted a single effective APR as though it were a contract property, when P6(b) shows APR is jointly determined by the price and the revenue path.

We report the retraction rather than quietly correcting it because it is the concrete instance of the conflation this paper argues against, produced by authors who were actively trying to avoid it. That it survived several drafts is the useful part of the anecdote.

Two external observations support treating price and structure separately as a matter of course. Regulators have concluded that factor-rate pricing is not comparable to APR without conversion and must be disclosed alongside it (L-23, L-24). And the theoretical literature is clear that contingency must be priced above fixed debt to compensate the financier for bearing risk — quantified for human capital at roughly $1.64 per dollar financed (L-18), and observed as persistent premia on state-contingent sovereign instruments (L-19). A revenue-contingent contract priced at parity with a fixed loan would be the anomaly requiring explanation.

---

## 10. Closure, incomplete recovery and censoring

### 10.1 The null result, and its boundaries

Across the ten non-closure scenarios, incomplete recovery is **0.0%** and total repaid is identical at the cap **[S-2 | `baseline_v2_canonical.json` → `/scenarios/*/RBF/incomplete_recovery_rate`, `/total_repaid_mean`]**.

This is **horizon- and scenario-bounded**, and stating it alone would be misleading: none of those ten scenarios reaches zero revenue, and the horizon is 24 months against a 13-month matched base term. An earlier version of this project reported this null as evidence that provider exposure was "duration risk, not principal loss". That framing is withdrawn.

### 10.2 Where recovery actually fails

Permanent closure occurring **before completion, while a contractual balance remains outstanding**, is the case where recovery genuinely fails. Both halves of the table below carry their own source: the `f = 1.20` columns are **[S-3 | `baseline_closure_v1_canonical.json` → `/scenarios/*/RBF/incomplete_recovery_rate`, `/recovery_ratio/24`]** and the `f* = 1.0945` columns are **[S-4 | `baseline_closure_equalcost_v1_canonical.json` → same paths]**.

| Scenario | Incomplete recovery, `f = 1.20` | RR(24) | Incomplete recovery, `f* = 1.0945` | RR(24) |
|---|---|---|---|---|
| `closure_m7` | **100.0%** | 44.30% | **100.0%** | 48.57% |
| `closure_m13` | **76.2%** | 96.53% | **7.6%** | 99.88% |
| `temp_closure` | 2.0% | 99.98% | **0.0%** | 100% |

Three things in this table deserve emphasis.

**Timing decides it, not zero revenue as such.** A temporary three-month cessation leaves only 2.0% of paths incomplete at `f = 1.20` and none at `f*`. Closure at month 7 — before the matched 13-month term — leaves every path incomplete. It is not the presence of zero-revenue months that prevents completion; it is permanent cessation before the threshold is crossed while a balance remains.

**Price moves the failure rate by an order of magnitude.** `closure_m13` incomplete recovery falls from 76.2% to 7.6% on the cap factor alone **[S-4 | `baseline_closure_equalcost_v1_canonical.json`]**. This is P6(a) made visible: a lower cap is a nearer threshold.

**Incomplete recovery is not principal loss.** `closure_m13` recovers approximately **214.3M VND** against a **185M** advance — the principal is covered despite 76.2% of paths failing to reach the contractual target. Only `closure_m7` shows a principal shortfall, recovering approximately **98.3M**, and it recovers the **same absolute amount at both cap factors** because that path is revenue-limited rather than cap-limited **[I-3]**. A 76.2% incomplete-recovery rate is not a 76.2% loss rate, and we are careful not to let the first number stand in for the second.

### 10.3 Censoring, and what our own statistics omit

Mean duration and mean effective APR are computed **only over paths that reached the repayment target within the window**. They are survivor statistics: they estimate `E[T | T ≤ C]`, not `E[T]`, and they describe the contracts that finished, not the portfolio.

The framing is standard sample selection — computing a statistic on a non-randomly selected subsample is a specification error (L-36), and conditioning on completion is conditioning on a common effect (L-37). The machinery is standard right-censoring (L-32, L-33), and in an economics setting the duration-data treatment (L-34, L-35) is the appropriate reference. We found no dedicated source quantifying this particular bias, and we do not cite one; the direction follows immediately from the definition.

The practical consequence is a reading rule. **A scenario with a short mean duration and a high incomplete-recovery rate is not a fast contract — it is one where the slow paths were dropped rather than counted.** `closure_m13` at `f = 1.20` reports a mean duration of 11.99 months alongside 76.2% incomplete recovery; reporting the first without the second would invert the finding.

---

## 11. Product implications

These are judgements we draw, not measurements.

**Report price and structure separately, always.** Otherwise a pricing choice is silently attributed to a structural property. This is the methodological recommendation, and §9.1 is the evidence that it is easy to get wrong.

**Provider exposure has two distinct forms.** Duration risk in ordinary downturns, and an unrecovered contractual balance where permanent closure precedes completion. Both belong in a term sheet, and the second cannot be inferred from ten scenarios that never reach zero revenue.

**The guardrail result, both halves.** The design includes a hardship payment floor and a payment ceiling. The **floor never activates on any path** — 0 of 36,000 month-observations — because the floor multiplier is below the hardship threshold (`μ = 0.25 < h = 0.50`), making it dead by construction **[N-2′ | `validation_v1_canonical.json` → `/rbf_g_breakpoint/pmin0.25_hard0.5`]**. The **ceiling does bind**: 6,009 of 36,000 observations in the breakpoint scan, and in the baseline it changes results in **6 of 10** scenarios — mean APR in 6, mean burden in 6, recovery ratio in 3, mean duration in 1 **[`baseline_v2_canonical.json` → `/scenarios/*/RBF-G`]**. The differences fall below display precision, which is why they went unnoticed through several reviews. **Invisible at display precision is not identical**, and presenting the floor null alone would read as a whole-arm null, which is false. As specified, the floor is decoration; the ceiling is not.

**No predictive-validity claim, and a worked reason.** The demonstration product includes a machine-learning risk score. It is trained on synthetic data whose default label was generated by a hand-written weighted formula over the same features the model consumes — so the model was scored on its ability to rediscover that formula. Our own reproducible evidence: the AUC of the generating function against its own label is **0.9098**, against the reported ensemble AUC of **0.9182** **[R-000 | `research/analysis/00_audit_evidence.py`]**. The reported figure measured the chosen noise variance, not predictive skill, and is **withdrawn**; we cite it here only to explain the withdrawal. The general mechanism — leakage inflating apparent performance — is documented across 294 papers in 17 fields (L-38). We found no source stating the specific circularity result, and argue it from our own evidence rather than attaching a citation that does not establish it.

**The fixed arm is an optimistic benchmark.** Fixed payments are modelled as made in full and on time in every month of the schedule. The fixed arm therefore represents scheduled recovery under that assumption, not realised recovery, and the comparison flatters it. Correcting this would require a default model, which this study does not have and does not claim to have.

---

## 12. Limitations and responsible use

**No observed data.** No observed seller revenue, repayment or default outcome exists anywhere in this study. Every figure is simulation output. Nothing here is evidence about Vietnamese sellers, or about any seller.

**No causal, predictive or population claim.** The design supports statements about contract mechanics under our assumptions. It does not support statements about what sellers would do, which sellers would accept these terms, or how a portfolio would perform.

**No affordability claim.** Burden is measured against **revenue**, not against what the seller retains. Margins, operating costs, reserves and other obligations are outside the model, so a lower burden here does not establish that a contract is affordable **[Q-2]**. The threshold bands are reporting devices, not validated hardship cutoffs **[Q-4]**.

**No default-prevention claim.** §10 is the counterexample. Revenue-contingency changes who bears timing risk; it does not remove risk.

**Unsourced parameters.** The benchmark rate `j = 18%`, term `N_B = 12`, the seasonality shapes, the margin `m` and fixed cost `F` are assumptions. None was externally sourced **[Q-5]**. The generalization limit binding on all outputs is that findings are statements about contract mechanics in a Vietnam-motivated, illustratively parameterised range (A-8).

**Synthetic-data limits.** Using synthetic data as though it were real yields analyses that do not generalise (L-39); institutional guidance identifies nuances easily overlooked in deployment (L-40). Our synthetic component is a demonstration, and §11 states what it cannot support.

**Self-reported-data limits.** The under-reporting sweep is motivated by the finding that evasion is near zero for third-party-reported income and substantial for self-reported income (L-42), and that the self-employed under-report by roughly 25% in household surveys (L-43). Neither magnitude transfers to marketplace revenue, and we do not transfer them. Measurement error in self-reported data is frequently non-classical, biasing in unpredictable directions rather than merely attenuating (L-41). **Our sweep is mechanical**: we impose ω and observe the contract's response. Russel et al. (2025) document *behavioural* revenue diversion under real contracts (L-07) — a materially different and harder object, which we do not model.

**Structural uncertainty.** We report parameter and stochastic uncertainty. Structural uncertainty — whether the revenue process itself is the right model — is not quantified, and by the standard taxonomy (L-30) that is the largest unquantified component.

**Responsible use.** This is not underwriting guidance. The demonstration product must not be presented as a validated risk model, and its risk score must not be described as a probability of default. Misrepresentation of terms in this product class has been the subject of federal enforcement (L-26), which is a reason for care rather than a finding about any particular provider.

---

## 13. Conclusion

Revenue-contingent repayment and fixed instalment repayment differ in *when* money moves, and that difference has two faces. Under adverse revenue paths the revenue-contingent contract holds the seller's payment burden roughly flat while the fixed contract's burden rises inversely with revenue; the same mechanism delays the provider's recovery and, where permanent closure precedes completion, leaves a contractual balance unrecovered. Reporting either face alone misstates the contract.

The price of the contract is a separate question from its structure, and the two are easy to conflate — we conflated them ourselves, published the conflation, and withdrew it. At one cap factor the revenue-contingent arm looks expensive; at another it does not; the structure is identical in both. Any cost comparison that does not name its cap factor is uninterpretable.

**What would change these conclusions:** observed seller revenue paths paired with adjudicated repayment outcomes, for both contract types, on comparable sellers. That data would replace the simulation entirely, and it is the only thing that would.

---

## 14. References

All entries verified against a publisher deposit, DOI resolution, or the issuing institution's page. Full annotation, including what each source does **not** support, is in `research/publication/LITERATURE_MATRIX.md`.

**L-01** International Finance Corporation & SME Finance Forum. *MSME Finance Gap.* https://www.smefinanceforum.org/data-sites/msme-finance-gap
**L-02** World Bank. *Digital Vietnam: The Path to Tomorrow.* World Bank Open Knowledge Repository. https://openknowledge.worldbank.org/entities/publication/fc34874a-23fc-5f5d-8875-336f08aff359
**L-04** Cornelli, G., Frost, J., Gambacorta, L. & Jagtiani, J. (2022). *The impact of fintech lending on credit access for U.S. small businesses.* BIS Working Papers 1041. https://www.bis.org/publ/work1041.htm
**L-05** Hair, C.M., Howell, S.T., Johnson, M.J. & Matsumoto, S. (2025). *Modernizing Access to Credit for Younger Entrepreneurs: From FICO to Cash Flow.* NBER WP 33367. https://doi.org/10.3386/w33367
**L-06** Ben-David, I., Johnson, M.J. & Stulz, R.M. (2021, rev. 2024). *Models Behaving Badly: The Limits of Data-Driven Lending.* NBER WP 29205. https://doi.org/10.3386/w29205
**L-07** Russel, D., Shi, C. & Clarke, R. (2025). *Revenue-Based Financing.* Working paper, Harvard University. SSRN 4608506. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4608506
**L-08** Cordaro, F., Fafchamps, M., Mayer, C., Meki, M., Quinn, S. & Roll, K. (2022). *Microequity and Mutuality: Experimental Evidence on Credit with Performance-Contingent Repayment.* NBER WP 30411. https://doi.org/10.3386/w30411
**L-09** Chapman, B., Higgins, T. & Stiglitz, J.E. (eds.) (2014). *Income Contingent Loans: Theory, Practice and Prospects.* Palgrave Macmillan. https://doi.org/10.1057/9781137413208
**L-10** Nerlove, M. (1975). Some Problems in the Use of Income-contingent Loans for the Finance of Higher Education. *Journal of Political Economy* 83(1), 157–183. https://doi.org/10.1086/260311
**L-11** Chapman, B. & Dearden, L. (2017). Conceptual and Empirical Issues for Alternative Student Loan Designs. *ANNALS of the AAPSS* 671(1), 249–268. https://doi.org/10.1177/0002716217703969
**L-12** Chapman, B. & Lounkaew, K. (2015). An analysis of Stafford loan repayment burdens. *Economics of Education Review* 45, 89–102. https://doi.org/10.1016/j.econedurev.2014.11.003
**L-13** Chapman, B., Lounkaew, K., Polsiri, P., Sarachitti, R. & Sitthipongpanich, T. (2010). Thailand's Student Loans Fund. *Economics of Education Review* 29(5), 685–694. https://doi.org/10.1016/j.econedurev.2010.04.001
**L-14** Chapman, B. & Lounkaew, K. (2010). Income contingent student loans for Thailand. *Economics of Education Review* 29(5), 695–709. https://doi.org/10.1016/j.econedurev.2010.04.002
**L-15** Barr, N., Chapman, B., Dearden, L. & Dynarski, S. (2019). The US college loans system: Lessons from Australia and England. *Economics of Education Review* 71, 32–48. https://doi.org/10.1016/j.econedurev.2018.07.007
**L-16** Battaglia, M., Gulesci, S. & Madestam, A. (2024). Repayment Flexibility and Risk Taking. *Review of Economic Studies* 91(5), 2635–2675. https://doi.org/10.1093/restud/rdad107
**L-17** Ganong, P. & Noel, P. (2020). Liquidity versus Wealth in Household Debt Obligations. *American Economic Review* 110(10), 3100–3138. https://doi.org/10.1257/aer.20181243
**L-18** Herbst, D. & Hendren, N. (2024). Opportunity Unraveled. *American Economic Review* 114(7), 2024–2072. https://doi.org/10.1257/aer.20211653
**L-19** Igan, D., Kim, T. & Levy, A. (2022). *The premia on state-contingent sovereign debt instruments.* BIS Working Papers 988. https://www.bis.org/publ/work988.htm
**L-20** Macaulay, F.R. (1938). *Some Theoretical Problems Suggested by the Movements of Interest Rates, Bond Yields and Stock Prices in the United States since 1856.* NBER.
**L-21** Fisher, L. & Weil, R.L. (1971). Coping with the Risk of Interest-Rate Fluctuations. *Journal of Business* 44(4), 408–431. https://doi.org/10.1086/295402
**L-22** Shen, H. & Ziderman, A. (2009). Student loans repayment and recovery. *Higher Education* 57(3), 315–333. https://doi.org/10.1007/s10734-008-9146-0
**L-23** New York State Department of Financial Services. *23 NYCRR 600 — Commercial Financing Disclosure.* https://www.dfs.ny.gov/industry_guidance/regulations/final_financial_services/rf_finservices_23nycrr600_text
**L-24** California Department of Financial Protection and Innovation. *Commercial Financing Disclosure Regulations* (SB 1235). https://dfpi.ca.gov/wp-content/uploads/sites/337/2022/06/PRO-01-18-Commercial-Financing-Disclosure-Regulation-Final-Text.pdf
**L-25** Federal Register (2023). *Truth in Lending; Determination of Effect on State Laws.* https://www.federalregister.gov/documents/2023/03/31/2023-06719/truth-in-lending-determination-of-effect-on-state-laws-california-new-york-utah-and-virginia
**L-26** Federal Trade Commission (2022). *Merchant Cash Advance Providers Banned from Industry.* https://www.ftc.gov/news-events/news/press-releases/2022/01/merchant-cash-advance-providers-banned-industry-ordered-redress-small-businesses
**L-27** Morris, T.P., White, I.R. & Crowther, M.J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine* 38(11), 2074–2102. https://doi.org/10.1002/sim.8086
**L-28** Koehler, E., Brown, E. & Haneuse, S.J.-P.A. (2009). On the Assessment of Monte Carlo Error. *The American Statistician* 63(2), 155–162. https://doi.org/10.1198/tast.2009.0030
**L-29** JCGM 101:2008. *Propagation of distributions using a Monte Carlo method.* BIPM et al. https://doi.org/10.59161/JCGM101-2008
**L-30** Briggs, A.H., Weinstein, M.C., Fenwick, E.A.L., Karnon, J., Sculpher, M.J. & Paltiel, A.D. (2012). Model Parameter Estimation and Uncertainty Analysis. *Medical Decision Making* 32(5), 722–732. https://doi.org/10.1177/0272989X12458348
**L-31** Pawel, S., Kook, L. & Reeve, K. (2024). Pitfalls and potentials in simulation studies. *Biometrical Journal* 66(1), e2200091. https://doi.org/10.1002/bimj.202200091
**L-32** Kaplan, E.L. & Meier, P. (1958). Nonparametric Estimation from Incomplete Observations. *JASA* 53(282), 457–481. https://doi.org/10.1080/01621459.1958.10501452
**L-33** Klein, J.P. & Moeschberger, M.L. (2003). *Survival Analysis*, 2nd ed. Springer. https://doi.org/10.1007/b97377
**L-34** Lancaster, T. (1990). *The Econometric Analysis of Transition Data.* Cambridge University Press. https://doi.org/10.1017/CCOL0521265967
**L-35** Van den Berg, G.J. (2001). Duration Models. In *Handbook of Econometrics*, Vol. 5, 3381–3460. https://doi.org/10.1016/S1573-4412(01)05008-5
**L-36** Heckman, J.J. (1979). Sample Selection Bias as a Specification Error. *Econometrica* 47(1), 153–161. https://doi.org/10.2307/1912352
**L-37** Hernán, M.A., Hernández-Díaz, S. & Robins, J.M. (2004). A Structural Approach to Selection Bias. *Epidemiology* 15(5), 615–625. https://doi.org/10.1097/01.ede.0000135174.63482.43
**L-38** Kapoor, S. & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4(9), 100804. https://doi.org/10.1016/j.patter.2023.100804
**L-39** van Breugel, B., Qian, Z. & van der Schaar, M. (2023). Synthetic Data, Real Errors. *ICML*, PMLR 202, 34793–34808. https://proceedings.mlr.press/v202/van-breugel23a.html
**L-40** Jordon, J. et al. (2022). *Synthetic Data — what, why and how?* Commissioned by The Royal Society. https://doi.org/10.48550/arXiv.2205.03257
**L-41** Bound, J., Brown, C. & Mathiowetz, N. (2001). Measurement Error in Survey Data. In *Handbook of Econometrics*, Vol. 5, 3705–3843. https://doi.org/10.1016/S1573-4412(01)05012-7
**L-42** Kleven, H.J., Knudsen, M.B., Kreiner, C.T., Pedersen, S. & Saez, E. (2011). Unwilling or Unable to Cheat? *Econometrica* 79(3), 651–692. https://doi.org/10.3982/ECTA9113
**L-43** Hurst, E., Li, G. & Pugsley, B. (2014). Are Household Surveys Like Tax Forms? *Review of Economics and Statistics* 96(1), 19–33. https://doi.org/10.1162/REST_a_00363
**L-44** Slemrod, J. (2007). Cheating Ourselves: The Economics of Tax Evasion. *Journal of Economic Perspectives* 21(1), 25–48. https://doi.org/10.1257/jep.21.1.25

---

## 15. Reproducibility statement

**Artifacts.** Every figure in this manuscript derives from one of five canonical, checksummed artifacts:

| Artifact | SHA-256 |
|---|---|
| `baseline_v2_canonical.json` | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` |
| `baseline_equalcost_v1_canonical.json` | `6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7` |
| `baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` |
| `baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` |
| `validation_v1_canonical.json` | `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4` |

**Reproducibility, stated at the strength the measurement supports.** All five artifacts reproduce **numerically at published precision** from a clean tree on every platform tested. **Byte equality is platform-dependent and is not claimed across platforms:** on Linux/aarch64 CPython 3.10.12 all five regenerate byte-identically; on macOS CPython 3.11.5, `baseline_v2` differs in 9 last-bit floating-point values and `baseline_equalcost_v1` in 2, while the other three are byte-identical. Verify with `python3 research/verify_reproduction.py`, which regenerates into a scratch tree and reports byte equality and numeric-leaf equality as separate columns.

An earlier version of this project claimed byte-for-byte reproducibility without qualification, on the basis of an evidence step that re-hashed the committed file rather than regenerating it. That step could not have failed for any reason connected to determinism. Both the claim and the evidence are corrected.

**A disclosed inconsistency.** Each artifact embeds a metadata field `canonical.determinism` carrying the superseded unqualified claim. The artifacts were **not** regenerated to correct it, because doing so would change all five registered checksums in order to fix a sentence about reproducibility. The field is marked superseded in `research/RESULTS_REGISTRY.md`, and a regression test asserts that no public surface renders it.

**Tests.** 629 simulation tests and 379 backend tests pass. Nine browser tests **skip** where no chromium build is available; they are reported as skips and are not counted as passes.

**Governing documents.** `research/METHODOLOGY_SPEC.md` v1.0 + amendments A-1…A-8 (frozen specification); `research/DERIVATIONS.md` (propositions and proofs); `research/CLAIM_LEDGER.md` (what may be claimed, with required qualifiers); `research/RESULTS_REGISTRY.md` (every registered result); `research/DECISION_LOG.md` (every decision and supersession, including our own retracted claims).
