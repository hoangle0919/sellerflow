# Frozen Metric Definitions & Pre-Registered Analysis Plan

**Project:** Revenue-Contingent Financing Under Volatile Sales: A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers
**Status:** 🔒 **FROZEN 2026-08-03, before any comparison-engine run.**
**Authority:** `DECISION_LOG.md` D-004 (freeze before analysis) and D-010 (distress definition).

> **Amendment rule.** Any change after the first analysis run must be appended to §9 as a dated amendment stating what changed, why, and what result was already visible when the change was made. Silent edits invalidate the pre-registration. If §9 is empty at submission, no definition was changed after seeing a result.

---

## 1. Notation

| Symbol | Meaning | Units |
|---|---|---|
| `t = 1 … T` | Month index; `T = 36` simulation horizon | months |
| `R_t` | Seller gross revenue in month `t` | VND |
| `R_0` | Pre-financing baseline monthly revenue | VND |
| `A` | Advance principal, identical across all arms | VND |
| `m` | Gross margin | fraction |
| `F` | Fixed monthly operating cost | VND |
| `p_t^{(a)}` | Financing payment in month `t` under arm `a` | VND |
| `a ∈ {FIX, RBF, RBF-G}` | Financing arm | — |
| `r` | RBF remittance rate (share of revenue) | fraction |
| `f` | RBF factor rate; total obligation `C = A·f` | multiple |
| `C` | Total repayment cap `= A · f` | VND |
| `N` | Fixed-loan contractual term | months |
| `ω` | Revenue-underreporting factor; provider observes `ω·R_t`, `ω ≤ 1` | fraction |

**Convention.** Payments are month-end, non-negative, and never exceed the remaining obligation. All arms share the same origination month `t = 1`.

---

## 2. The three financing arms

### 2.1 FIX — fixed-payment loan

```
p_t^{FIX} = P              for t = 1 … N
p_t^{FIX} = 0              for t > N
```

`P` is constant and **independent of `R_t`**. This independence is the entire object of study.

### 2.2 RBF — baseline revenue-based financing

```
p_t^{RBF} = min( r · R_t ,  C − Σ_{s<t} p_s^{RBF} )
```

Payment stops when cumulative payments reach the cap `C`. There is no contractual maturity — duration is an *output*, not an input. This is the structural difference from FIX.

### 2.3 RBF-G — guardrailed revenue-based financing

```
p_t^{RBF-G} = min( max( r · R_t , p_min ) , p_max , C − Σ_{s<t} p_s^{RBF-G} )
```

subject to a hardship rule: if `R_t < 0.5 · R_0` then `p_t^{RBF-G} = r · R_t` (the floor `p_min` is suspended).

Defaults, subject to §7 sensitivity: `p_min = 0.25 · r · R_0`, `p_max = 2.0 · r · R_0`.

RBF-G exists to test whether provider-side protection can be added without destroying the seller-side benefit. If it destroys it, that is a finding and will be reported as one.

---

## 3. Financial fairness matching — the identification strategy

> This section is the paper's most attackable point. It is therefore specified first, in full, and its limitation is stated before any result.

**Primary matching — cost-matched at base case.** Given an RBF contract `(A, r, f)` and the base-case revenue path `R_t^{base}`:

1. **Principal:** `A^{FIX} = A^{RBF} = A`.
2. **Total contractual cost:** `N · P = C = A · f`.
3. **Term:** `N = D^{RBF}(R^{base})`, the RBF base-case payoff month (§5.4).

Therefore `P = C / N`.

**Interpretation.** Under the base-case path, the two arms are *identical in every financial respect* — same principal, same total repaid, same duration. All observed divergence in any other scenario is attributable to the **payment structure alone**, not to price. This is what makes the comparison a clean structural contrast rather than a repricing exercise.

**Implied fixed-loan APR** is reported, never assumed. It is solved from the cash flows:

```
A = Σ_{t=1..N} P / (1 + i)^t         →  APR = (1 + i)^12 − 1
```

**Secondary matching — APR-matched (sensitivity).** A second FIX arm priced at an assumed nominal APR (`j = 18%`, `N_B = 12`), where total cost differs from `C`. Reported separately and never mixed into the primary comparison. The 18% is an assumption chosen for this study — **not a market rate**, and not observed or externally sourced anywhere in this project. See `CLAIM_LEDGER.md` Q-5.

**Stated limitation (goes in the paper, not only here).** An APR loan and a factor-rate cap are not natively commensurable: one prices time, the other prices a multiple regardless of time. Cost-matching at base case makes them comparable *at a single point* — the base path — and the equivalence degrades as realized revenue departs from it. Every reported comparison names its matching basis. **We do not claim the two products are economically equivalent; we claim they are matched at the base case and then diverge, and we measure that divergence.**

### 3.4 🔒 Base-case coherence constraint *(added 2026-08-03 during spec verification, before first analysis run)*

A scenario is **coherent** only if the seller can service the matched payment out of gross profit under the base-case path:

```
m · R_0 − F − P  >  0
```

**Why this is mandatory.** Spec verification (`research/analysis/01_verify_spec.py`) found that at `m = 0.25`, `F = 0.20·R_0`, and the advance size the current product recommends, the distress metric returns **36/36 months for both arms** — the seller is unprofitable after financing regardless of structure, so `n_distress` cannot discriminate and H2 becomes untestable by degeneracy rather than by evidence.

**Rule.** Every calibration is checked against §3.4 before it enters the scenario library. Incoherent parameter combinations are **not silently dropped** — they are reported in the robustness table as the region where *no* financing structure is affordable, which is itself a substantive result: it bounds the population RBF can help.

**Consequential product finding — provisional, pending Phase 2 calibration.** `financing_engine.py` sizes the advance as a percentage of **annual revenue** (15% low-risk / 8% medium-risk) and never reads gross margin or fixed costs. Capacity to repay is therefore never checked. Under the illustrative parameters above, the recommended advance is ~1.80 × monthly revenue while an indicative serviceable bound is ~0.92 × monthly revenue — roughly **half**. This is flagged as **provisional** because `m` and `F` are not yet sourced; it becomes a reportable finding only once Phase 2 calibrates them against citable evidence. If it survives calibration, it is a direct, honest product implication: **revenue-based sizing without a margin input systematically overstates capacity**, and the fix — sizing off gross profit — is a concrete design change the research would have produced.

---

## 4. Seller-side metrics

### 4.1 Payment-to-revenue ratio
```
PTR_t^{(a)} = p_t^{(a)} / R_t          (undefined and excluded where R_t = 0)
```
Reported: mean, median, max, and the 90th and 95th percentiles over `t` where `p_t > 0`.

> **Known degeneracy — stated up front.** By construction `PTR_t^{RBF} ≡ r` whenever the cap is not binding. This metric therefore *describes* RBF rather than testing it, and is reported for transparency only. **It is not used to evaluate H1 or H2.** Any threshold rule built on `PTR` would be trivially satisfied by the RBF arm and would rig the comparison — this is precisely why D-010 rejected it as the distress definition.

### 4.2 Post-payment operating cash flow
```
OCF_t^{(a)} = m · R_t − F − p_t^{(a)}
```

The seller's monthly cash position after cost of goods, fixed operating costs, and the financing payment. `m` and `F` are named assumptions calibrated in Phase 2 and swept in §7.

### 4.3 Distress month — 🔒 primary definition

```
D_t^{(a)} = 1   if   OCF_t^{(a)} < 0
            0   otherwise
```

**Primary outcome:** `n_distress^{(a)} = Σ_{t=1..T} D_t^{(a)}`
**Secondary:** `%distress^{(a)} = n_distress^{(a)} / T`

**Pre-specified alternative thresholds** — all four are reported in the robustness table regardless of whether they agree with the primary:

| ID | Rule | Rationale |
|---|---|---|
| **T-0 (primary)** | `OCF_t < 0` | Cannot cover costs plus payment from that month's revenue |
| T-1 | `OCF_t < 0.05 · R_t` | Thin-buffer variant |
| T-2 | `OCF_t < 0` for **two consecutive months** | Persistence variant; isolates transient dips |
| T-3 | `m·R_t − F − p_t < −0.10 · (m·R_0 − F)` | Deterioration relative to pre-financing baseline |

**Falsification.** If the sign of the FIX − RBF difference in `n_distress` is not stable across T-0…T-3, H2 is **not** supported and the paper will say the result is threshold-dependent.

### 4.4 Maximum payment burden
```
maxPTR^{(a)} = max_t { PTR_t^{(a)} : p_t > 0 }
```

### 4.5 Recovery time after a shock
For a shock beginning at month `t_s`:
```
RT^{(a)} = min{ k ≥ 0 : OCF_{t_s+k}^{(a)} ≥ 0 and OCF_{t_s+j}^{(a)} ≥ 0 ∀ j ∈ [k, k+2] }
```
Three consecutive non-negative months required, to avoid counting a single lucky month as recovery. Right-censored at `T`; censoring is reported, not imputed.

### 4.6 Total financing cost
```
TotalCost^{(a)} = Σ_{t=1..T} p_t^{(a)} − A
```
Reported alongside `Σ p_t / A` (money multiple) and completion status (§5.5).

### 4.7 Time to full repayment
```
D^{(a)} = min{ t : Σ_{s≤t} p_s^{(a)} ≥ C }        ( = ∞ if never, within T )
```

---

## 5. Provider-side metrics

### 5.1 Capital recovered by horizon
```
Rec_T^{(a)} = Σ_{t=1..T} p_t^{(a)}
```

### 5.2 Recovery ratio
```
RR^{(a)} = Rec_T^{(a)} / C
```

### 5.3 Time to recover principal
```
TTP^{(a)} = min{ t : Σ_{s≤t} p_s^{(a)} ≥ A }      ( = ∞ if never, within T )
```

### 5.4 Time to cap
`D^{(a)}` as defined in §4.7.

### 5.5 Incomplete-recovery indicator
```
IR^{(a)} = 1   if   Rec_T^{(a)} < C
```
Reported as a **rate across simulated paths**. 

> ⚠️ **Naming discipline.** This is *not* a default rate and must never be called one. It measures failure to reach the cap within a 36-month observation window under a simulated revenue path. It carries no information about borrower behavior, willingness to pay, or credit loss. The paper uses the phrase "incomplete recovery within horizon" throughout.

### 5.6 Duration dispersion
```
sd(D)   and   IQR(D)   across paths within a scenario
```
This is the direct test of H3 — the price the provider pays for seller-side flexibility.

### 5.7 Provider IRR
```
solve:  −A + Σ_{t=1..T} p_t / (1 + i)^t = 0        →   IRR = (1+i)^12 − 1
```
Placed beside `TotalCost` so that seller cost and provider return are read together. Undefined cases (no sign change) are reported as undefined, not dropped.

### 5.8 Underreporting sensitivity
Provider observes `ω · R_t`; the seller's true revenue remains `R_t`.
```
p_t^{RBF}(ω) = min( r · ω · R_t ,  C − Σ_{s<t} p_s )
```
Reported: `∂RR/∂ω` and `∂D/∂ω` over `ω ∈ {1.00, 0.95, 0.90, 0.80, 0.70}`.

FIX is invariant to `ω` by construction — the fixed loan cannot be diverted from, because it never looks at revenue. **This is a genuine and underappreciated advantage of fixed-payment structures and the paper will state it plainly rather than burying it.** It is the clearest case where the evidence runs against the product being built.

---

## 6. Statistical procedure — and its hard limits

**Design.** Fully paired. Every revenue path `R_t` is generated once and passed to all three arms. All comparisons are within-path differences:
```
Δ^{FIX−RBF} = metric^{FIX} − metric^{RBF}      (per path)
```

**Reported per scenario:** `n_paths`, mean Δ, median Δ, and a **BCa bootstrap interval** (10,000 resamples, seed fixed and recorded) on the paired difference.

### 🔒 6.1 What the intervals mean — and what they do not

> **The intervals quantify Monte Carlo precision. They do not quantify uncertainty about real sellers.**
>
> Every path in this study is generated by a model whose parameters we chose. Running more paths narrows every interval toward zero **without adding a single fact about the world.** An interval here answers "have we run enough simulations for this number to be stable?" — never "how confident are we that this holds for Vietnamese sellers?"
>
> Consequently the paper reports **no p-values and makes no significance claims.** A statistically significant result in a simulation of one's own assumptions is a statement about arithmetic, not about sellers. Uncertainty about the world is addressed *only* through the sensitivity analysis in §7, and even then only over the parameter ranges we specified.

This constraint is not a weakness to be minimized in the writing. It is the correct epistemics for a simulation study, and stating it precisely is a stronger signal of competence than any confidence interval would be.

### 6.2 Effect reporting
Paired differences are reported in **native units** (months, VND, count of distress months) rather than standardized effect sizes. Standardized effect sizes would invite comparison to empirical literature, which does not apply here.

---

## 7. Pre-specified sensitivity analyses

Run in full and reported whether or not they support the hypotheses.

| # | Parameter | Range |
|---|---|---|
| S-1 | Distress threshold | T-0 · T-1 · T-2 · T-3 (§4.3) |
| S-2 | Remittance rate `r` | 0.06 · 0.08 · 0.10 · 0.12 · 0.15 |
| S-3 | Factor rate `f` | 1.10 · 1.15 · 1.20 · 1.30 |
| S-4 | Gross margin `m` | 0.15 · 0.25 · 0.35 · 0.45 |
| S-5 | Fixed cost `F` | 0.10 · 0.20 · 0.30 × baseline revenue |
| S-6 | Advance size `A` | 0.5 · 1 · 2 · 3 × monthly revenue |
| S-7 | Shock magnitude | −20% · −40% · −60% |
| S-8 | Shock duration | 1 · 3 · 6 months |
| S-9 | Underreporting `ω` | 1.00 · 0.95 · 0.90 · 0.80 · 0.70 |
| S-10 | Guardrails `p_min`, `p_max` | off · default · tight |
| S-11 | Horizon `T` | 24 · 36 · 48 months |

**Headline-fragility rule.** Any headline claim that reverses sign anywhere in S-1…S-11 is demoted from "finding" to "condition-dependent observation," and the reversing condition is named in the abstract.

---

## 8. Hypotheses — and what would falsify each

| ID | Statement | Primary metric | Falsified if |
|---|---|---|---|
| **H1** | RBF produces a lower payment burden than FIX in low-revenue months | `p_t` in months where `R_t < R_0` | RBF payment ≥ FIX payment in low-revenue months under cost-matching |
| **H2** | RBF produces fewer distress months under seasonal and negative shocks | `n_distress` (T-0) | Δ ≤ 0, **or** sign unstable across T-0…T-3 |
| **H3** | Seller-side flexibility costs the provider duration and recovery variance | `sd(D)`, `IR` rate | RBF duration dispersion ≤ FIX **and** `IR^{RBF} ≤ IR^{FIX}` |
| **H4** *(reframed per audit; wording corrected A-8)* | Revenue stability, turnover, returns, and tenure predict **whether a simulated path clears the illustrative burden bands (10/15/20/25% of revenue)** better than revenue size alone | ΔR² for stability vs. size predicting `n_distress` | Revenue size alone performs equally or better |
| **H5** | Underreporting and data quality are material risks requiring conservative design | `∂RR/∂ω`, `∂D/∂ω` | Recovery is insensitive to `ω` across the tested range |

> **H1 is partly true by construction and the paper says so in the same sentence it reports the result.** `p_t^{RBF} = r·R_t` falls mechanically when `R_t` falls; no simulation is needed to know the direction. The research contribution is the **magnitude**, the **cost of that relief** in duration and total repayment, and **whether it is enough to change distress outcomes** (H2) — which is not true by construction and could genuinely fail.

**Expected-to-fail note.** ~~Under cost-matching at base case, RBF's relief in bad months is funded by longer duration and higher total cost in good ones.~~ → **corrected (D-040): this is conditional, not universal.** Whether the revenue-share arm recovers faster or slower than the fixed arm follows the exact P4 condition — realized mean eligible base `(1/k)·S_k` relative to `B* = P/r` — and **both directions occur** in the scenario library. Under a path whose realized mean clears `B*`, the revenue share leads on recovery with no duration penalty at all; the stable scenario is such a case, by integer rounding of `N`. The original sentence describes the base-case *expectation*, and it is entirely plausible that H2 fails at realistic margins — that RBF smooths payments without preventing distress, because distress is driven by `m·R_t − F`, which financing structure does not touch. **If that is the result, it is the paper's finding and it will be the headline.** It is a more interesting and more defensible result than confirmation.

---

## 9. Amendments after first analysis run

*(Empty. Any post-hoc change to §1–§8 is recorded here with date, rationale, and the result already visible at the time of the change.)*

---

## 10. Reproducibility

| Item | Commitment |
|---|---|
| Seeds | Fixed and recorded per run; bootstrap seed separate from path seed |
| Path generation | Independent of any arm — generated once, passed to all three |
| Outputs | Written to versioned files under `research/results/`; figures regenerated from committed code only |
| Registry | Every run gets a `RESULTS_REGISTRY.md` entry before it is quoted anywhere |
| Verification | Phase 5 V-03 regenerates every figure from a clean checkout |
