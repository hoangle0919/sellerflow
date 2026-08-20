# Corrected Claims & Validation Results

> **This document is a dated snapshot, not a live status page.** Everything
> below records what was true on **2026-08-03**. Figures, spec version and test
> counts are preserved as written on that date and are deliberately not
> updated; a corrections record that gets edited later cannot be audited. For
> current state see `RESEARCH_MANIFEST.md`, and for the authoritative list of
> what may be claimed see `CLAIM_LEDGER.md`.
>
> Two pointers, because the values below have since moved:
> **Specification** — this snapshot was taken against `METHODOLOGY_SPEC.md`
> v1.0 + amendments **A-1…A-3**. The specification now stands at **A-1…A-8**;
> A-4…A-8 postdate this document and are recorded in the spec and the decision
> log. **Tests** — 169 passing here; see the manifest for the current figure.

**Date:** 2026-08-03 · **Spec at the time:** `METHODOLOGY_SPEC.md` v1.0 + amendments A-1…A-3 *(now A-1…A-8 — see above)*
**Runs:** `results/baseline_v2.json` · `results/validation_v1.json` · **Tests at the time of this document:** 169 passing

> All figures are **reproducible simulation output under modeled assumptions**. No observed seller revenue, repayment, or default outcome exists in this study.

**Excel:** removed from the project entirely per your correction — no dependency, deliverable, blocker, or reconciliation task remains. Every parameter below is sourced from the RBF repository, a documented derivation, or is labelled illustrative with sensitivity analysis.

---

## 1. Corrected claims

| # | Was | Now |
|---|---|---|
| 1 | "Real findings" | **Reproducible simulation findings under modeled assumptions.** Applied throughout; `BASELINE_FINDINGS.md` retitled and the registry entry re-scoped. |
| 2 | "RBF costs ~2.3× the interest of a conventional loan" | **"At the illustrative 1.20× cap, the simulated RBF contract is substantially more expensive than the 18% amortizing loan. This is a pricing result, not an inherent property of revenue-based repayment."** Price and structure are now separated and measured independently (§2, §3). |
| 3 | "Fixed payments are immune to underreporting — a structural advantage" | **"Scheduled fixed payments are invariant to revenue reporting, while RBF remittances decline approximately one-for-one with reported revenue. The simulation does not establish that actual fixed-loan recovery is immune to default."** The model contains no default, insolvency, or liquidity-constrained nonpayment, so no claim about realized fixed-loan collection is supported. |
| 4 | "Confidence intervals" / "bootstrap CIs" | **Monte Carlo intervals over simulated paths.** Each measures the stability of the mean given the chosen generative parameters. None measures population-level uncertainty about real sellers. The label is now emitted by the code itself (`bootstrap_ci` returns `label`, `measures`, `does_not_measure`). |

**Structure vs price — the distinction now enforced in the write-up:**

- **Financing structure** — fixed instalment vs revenue-contingent remittance. Determines *how payment responds to revenue*.
- **Financing price** — factor rate `f`, APR, fees, duration. Determines *how much is paid in total*.

Benchmark A holds price constant and varies structure. The cap sweep holds structure constant and varies price. Conflating them was the error in the previous checkpoint.

---

## 2. Pricing-sensitivity table (cap factor `f`)

Stable reference path, `A = 185,000,000 VND`, `r = 0.10`, remittance basis `net_sales`. Structure held constant; only price moves.

| `f` | Cap (VND) | Duration | Total repaid | Implied effective APR |
|---|---|---|---|---|
| 1.05 | 194,250,000 | 11 | 194,250,000 | 10.47% |
| 1.08 | 199,800,000 | 12 | 199,800,000 | 16.62% |
| **1.0945** | **202,482,500** | **12** | **202,482,500** | **19.54%** ← nearest reference-path APR grid match (residual ≈0.02416pp vs 19.561817%) |
| 1.10 | 203,500,000 | 12 | 203,500,000 | 20.64% |
| 1.12 | 207,200,000 | 12 | 207,200,000 | 24.61% |
| 1.15 | 212,750,000 | 12 | 212,750,000 | 30.48% |
| **1.20** | 222,000,000 | 13 | 222,000,000 | **39.90%** ← illustrative default |
| 1.25 | 231,250,000 | 13 | 231,250,000 | 48.97% |
| 1.30 | 240,500,000 | 14 | 240,500,000 | 57.54% |

**Benchmark B reference:** `j = 18%` nominal, `N_B = 12` → effective APR **19.5618%**, total repaid 203,529,584 VND.

`f = 1.20` is an **illustrative parameter taken from the existing repository** (`financing_engine.py`, `TIER_PARAMS`), not an externally sourced market rate. It is swept as S-3.

---

## 3. Nearest reference-path APR grid match for the RBF cap

> ~~"Equal-effective-cost"~~ **superseded (D-043).** `f*` is the closest point on the swept cap-factor grid, not an exact cost solution: 19.537656% against the reference's 19.561817%, residual **≈0.02416 percentage points**. It was solved on a single flat, shock-free reference path; on simulated paths the realised rate differs because duration moves with revenue.

| | |
|---|---|
| Target effective APR (Benchmark B) | 19.5618% |
| **Nearest-grid-match cap factor `f*`** | **1.0945** (residual ≈0.02416pp) |
| Resulting cap | 202,482,500 VND |
| Duration | 12 months |
| Total repaid | 202,482,500 VND |
| Achieved effective APR | 19.5377% (residual 0.0242%) |

Duration is integer-valued, so effective cost moves in steps and an exact match is not generally attainable. The residual is reported rather than smoothed away.

> **Claim, as it will appear publicly:** *At the illustrative 1.20× cap, the simulated RBF contract is substantially more expensive than the 18% amortizing loan. This is a pricing result, not an inherent property of revenue-based repayment. Repricing the same revenue-contingent structure at f ≈ 1.095 produces approximately equal effective cost under the stable baseline.*

---

## 4. Monte Carlo convergence

Scenario: sustained −40% decline. Paired FIX-A − RBF differences.

| Paths | Δ n_HPB(0.15) | Monte Carlo interval | Δ RR(12) | Monte Carlo interval |
|---|---|---|---|---|
| 500 | 3.1000 | [3.0000, 3.1980] | 16.271pp | [15.982, 16.556] |
| 2,000 | 3.1030 | [3.0515, 3.1535] | 16.400pp | [16.258, 16.546] |
| 5,000 | 3.1108 | [3.0796, 3.1414] | 16.424pp | [16.336, 16.515] |
| **10,000** | **3.1135** | **[3.0909, 3.1357]** | **16.466pp** | **[16.399, 16.534]** |

**Change 5,000 → 10,000:** 0.0027 months and 0.042pp. **Converged** at 2-decimal reporting precision. Headline scenarios will be reported at 10,000 paths.

**What these intervals are.** Monte Carlo intervals from resampling simulated paths. They measure whether enough paths were run for the mean to be stable under the chosen generative parameters. **They are not population confidence intervals** and say nothing about real sellers — running more paths narrows them without adding any fact about the world.

---

## 5. Incomplete-recovery boundary

Baseline v1 reported 0.0% everywhere, which was a horizon artifact. Searching harder located the boundary.

| Probe | T | Write-off | A/R₀ | Incomplete | RR(24) | Duration |
|---|---|---|---|---|---|---|
| **Closure @ month 7** | 24 | — | 1.0 | **100.0%** | 44.3% | never |
| **Closure @ month 13** | 24 | — | 1.0 | **76.0%** | 96.5% | 12.0 |
| Temporary closure 3m + −50% | 24 | — | 1.0 | 2.2% | 100.0% | 23.0 |
| Extended downturn −60% | 24 | — | 1.0 | 0.0% | 100.0% | 21.8 |
| **Extended downturn −80%** | 24 | — | 1.0 | **50.2%** | 98.6% | 24.0 |
| **Sustained −40%, T=18** | 18 | — | 1.0 | **25.7%** | 99.5% | 17.6 |
| **Sustained −60%, T=18** | 18 | — | 1.0 | **100.0%** | 83.1% | never |
| **Write-off @ 18m, sustained −40%** | 24 | 18 | 1.0 | **25.7%** | 99.5% | 17.6 |
| Advance 3×R₀ (any) | 24 | — | 3.0 | cap unreachable on reference — benchmark A undefined | | |
| Write-off @ 12m | 24 | 12 | 1.0–2.0 | cap unreachable on reference — benchmark A undefined | | |

**Boundary characterised — CORRECTED 2026-08-04; refined D-043.** The general criterion is that **some finite `t ≤ H` satisfies `r · Σ_{s≤t} B_s ≥ f·A`** (lowercase `f` — uppercase `F` is fixed operating cost). For finite `H` only, this is equivalent to `r · Σ_{t≤H} B_t ≥ f·A`. Completion is a **finite-time** property: `S_∞ > Θ = f·A/r` **strictly** implies it, `S_∞ < Θ` precludes it, and at `S_∞ = Θ` it holds only if a finite partial sum *attains* `Θ` — which a strictly positive infinite series never does. Routes to incomplete recovery **include, but are not limited to** (the ~~"four distinct causes"~~ exhaustiveness claim is withdrawn):

1. **Zero-revenue months** (business closure) — absorbing. Closure at month 7 → 100% incomplete.
2. **A binding maturity or write-off rule** — write-off at month 18 turns a −40% decline from 0% into 25.7%.
3. **A finite evaluation horizon** — `T = 18` → 25.7%. A measurement artifact, not an economic loss.
4. **Strictly positive but sufficiently fast-decaying revenue** — a path whose *lifetime cumulative* sales are inadequate. Geometric decay completes in finite time **only if `ρ > ρ* = 1 − r·B₀/(f·A)`** (strict). At `ρ = ρ*` the lifetime sum equals the cap exactly but every finite partial sum is strictly below it — an asymptotic boundary case that never completes. Below `ρ*`, lifetime cumulative revenue is simply insufficient. In all these cases revenue is positive in every period forever.

⚠️ **Cause 4 was missing from the previous version of this document,** which asserted that decline alone cannot cause incomplete recovery. That was too broad: it equated *strictly positive revenue* with *revenue bounded away from zero*. See D-020 and `DERIVATIONS.md` §P7.

The simulated scenarios stepping down to a constant floor are bounded away from zero, so their cumulative series diverges and they do complete given time. **That is a property of how those scenarios were specified, not of declining revenue in general** — the scenario library contained no decaying-to-zero path, which is why the gap went unnoticed empirically.

**Honest limitation.** Three probes returned "cap unreachable on reference" — at `A = 3×R₀` or a 12-month write-off, RBF never reaches the cap even on the *stable* reference path, so Benchmark A cannot be matched and the comparison is undefined. This is reported, not silently dropped. It marks the edge of the parameter region where the study's matched design applies at all.

**No default model was introduced.** These are mechanical non-recoveries from zero revenue and maturity rules — not modeled borrower default. Adding a default model without defensible calibration was explicitly avoided.

---

## 6. RBF-G breakpoint decision — **demote**

**Analytic result, not a simulation artifact:**

```
floor BINDS when    r·obs < p_min = 0.25·r·R₀    →   obs <  0.25·R₀
floor APPLIES when  obs ≥ hardship·R₀            →   obs ≥  0.50·R₀
0.25 < 0.50  →  conditions are mutually exclusive
```

**The payment floor can never activate, for any revenue path whatsoever.** It is provably dead code.

> **⚠️ Corrected (D-040).** The sentence that followed — that this "fully explains" the null because RBF-G was bit-identical to RBF — is **withdrawn**. The floor explanation is right; the bit-identity is not. RBF-G differs numerically from RBF in **6 of 10** baseline scenarios, and those six are exactly the ones where the *ceiling* `p_max = 2·r·R₀` binds (1,400 of 12,000 month-observations in `growth`, 11 in `seasonal_strong`, 1 each in `seasonal`, `disruption_1m`, `platform_outage`, `returns_spike`). The differences fall below display precision. The surviving claim is about the floor only.
>
> ~~This fully explains the baseline v1 null result — RBF-G was bit-identical to RBF because one guardrail was unreachable by construction and the other rarely bound.~~
>
> **That sentence is withdrawn too, and it was left standing here by mistake in the first pass of this correction (D-042).** Writing a retraction and then restoring the retracted sentence verbatim two clauses later is worse than not retracting it. Checked directly against `results/baseline_v1.json`: RBF-G differs from RBF in **6 of 10** scenarios *there as well* — `seasonal`, `seasonal_strong`, `growth`, `disruption_1m`, `platform_outage`, `returns_spike`. So the bit-identity claim is false for **v1 and v2 alike**, and the floor explanation does not "fully explain" a null that was never a null. What the floor explains is only that the *floor* never fired.

Breakpoint scan, 36,000 month-observations under strong seasonality + 3%/month growth (the most favourable case for binding):

| `p_min_mult` | `hardship` | Floor status | Floor months | Ceiling months |
|---|---|---|---|---|
| **0.25** | **0.50** | **DEAD** | 0 | 6,009 |
| 0.25 | 0.20 | reachable | 0 | 6,009 |
| 0.60 | 0.50 | reachable | 772 | 6,009 |
| 0.80 | 0.50 | reachable | 3,844 | 6,009 |
| 1.00 | 0.50 | reachable | 9,564 | 6,009 |

**Decision: demote RBF-G from a headline arm to a documented design-flaw finding.** It is retained in the code and the registry as a **floor-only null / design flaw** — the hardship floor is dead, the ceiling is live — and is **not** retuned to make it bind — that would be tuning after seeing results. The floor requires `p_min_mult > hardship` to be reachable at all, which is a coherence condition the original design violated.

**Product implication.** ~~As specified, the guardrail feature is decoration.~~ → **corrected (D-044): only the hardship FLOOR is dead.** The floor never activates on any path (0 of 36,000 month-observations). The **ceiling** `p_max = 2·r·R₀` is live — it binds 6,009 of 36,000 in the breakpoint scan and changes results in **6 of 10** baseline scenarios (mean APR in 6, mean burden in 6, recovery ratio in 3, mean duration in 1), below display precision but present. Calling the whole guardrail design decoration overstates a real finding about one of its two rules. If it ships, the floor multiplier must exceed the hardship threshold, and the two parameters must be validated jointly.

---

## 7. Revenue-definition decision

**`gmv = orders × AOV` is the only exact identity.** Returns, discounts, cancellations, taxes, and platform fees are **deductions from** GMV, not components of the identity. Modeling them inside the identity would have been wrong.

```
gmv_t           = orders_t × aov_t                        ← exact identity, enforced by test
net_sales_t     = gmv_t × (1 − return_rate_t)             ← deduction
cash_receipts_t = net_sales_t × (1 − platform_fee_rate)   ← deduction
```

**Decision: the remittance basis is `net_sales` (GMV net of returns).** ~~Platforms settle after returns~~ → **pending external support (A-8, D-043):** no platform settlement documentation was obtained by this project, so that premise is unverified. The decision rests on the definitional argument alone — on a GMV basis the contract would charge a share of money the seller never receives. `revenue` remains an alias for `gmv` so that "payment-to-revenue" keeps its conventional top-line meaning as the burden denominator.

| Basis | Platform fee | Duration | Total repaid | RR(12) |
|---|---|---|---|---|
| gmv | 0% | 12.52 | 222,000,000 | 98.4% |
| **net_sales** | 0% | **12.87** | 222,000,000 | **96.6%** |
| cash_receipts | 0% | 12.87 | 222,000,000 | 96.6% |
| cash_receipts | 10% | 14.41 | 222,000,000 | 87.5% |

`platform_fee_rate` defaults to **0.0** and is classified **illustrative / awaiting justification** — no Vietnamese platform fee schedule has been sourced, so none is baked in. Swept as S-15.

**Consequence: baseline re-run as v2.** The basis change shifts the matched benchmark from 12 to 13 months (`P = 17,076,923`, implied APR **37.87%**) and materially changes results. `baseline_v1` is superseded and retained only for the audit trail.

### ⚠️ New finding from the correction — the provider effect reverses sign

| Scenario | Seller: Δ n_HPB(0.15) | Provider: Δ RR(12) |
|---|---|---|
| stable | 0.01 [0.00, 0.02] | **−4.3pp** [−4.5, −4.0] |
| growth | 0.04 [0.02, 0.05] | **−7.7pp** [−7.7, −7.7] |
| seasonal (strong) | 0.89 [0.84, 0.94] | −4.2pp [−4.5, −3.9] |
| 1-month disruption | 1.07 [1.04, 1.09] | −1.1pp [−1.4, −0.7] |
| gradual decline | 0.89 [0.83, 0.96] | +8.1pp [7.8, 8.4] |
| sustained decline | 3.10 [3.00, 3.20] | +16.3pp [16.0, 16.6] |
| severe downturn | 6.85 [6.80, 6.90] | +26.9pp [26.6, 27.1] |

Under stable, growing, or mildly disrupted revenue, **RBF recovers capital faster than the matched fixed loan** (negative Δ). Only under decline does the fixed loan recover faster. The provider's exposure is therefore **conditional on the revenue path**, not a uniform cost of the structure.

Per the headline-fragility rule (spec §12), any claim that RBF universally slows provider recovery is **demoted to a condition-dependent observation**, and the reversing condition — non-declining revenue — is named in the abstract.

---

## 8. Assumption classification

Excel is removed from the project. Every parameter is classified against its actual source:

| Parameter | Value | Classification | Source |
|---|---|---|---|
| `f` factor rate | 1.20 | **Illustrative** | `financing_engine.py` `TIER_PARAMS` — repo, not market-sourced. Swept S-3 |
| `r` remittance rate | 0.10 | **Illustrative** | `financing_engine.py` (0.08 low / 0.12 medium). Swept S-2 |
| `A` advance | 1.0 × R₀ | **Illustrative** | Repo sizes at 15% of annual revenue (1.8 × R₀); reduced for coherence (§14). Swept S-4 |
| `j` benchmark APR | 18% | **Illustrative / awaiting justification** | No Vietnamese SME lending rate sourced. Swept S-13 |
| `N_B` benchmark term | 12 | **Illustrative** | Swept S-13 |
| `R₀` baseline revenue | 185,000,000 VND | **Derived** | The repo's own worked example (README `curl` sample) |
| `aov₀` | 440,000 VND | **Derived** | Same worked example |
| `return_rate` | 0.03 | **Derived** | Same worked example (0.028) |
| Seasonality shape | ±20% / ±40% | **Illustrative** | Tết + mega-sale reasoning; unsourced. Swept S-7 |
| `σ` noise | 0.15 | **Illustrative** | Swept S-6 |
| `platform_fee_rate` | 0.0 | **Arbitrary / awaiting justification** | Deliberately zero so no unsourced fee is baked in. Swept S-15 |
| `m`, `F` | — | **Illustrative** | Secondary metric only; never a headline |
| Shock depths | 20/40/60/80% | **Illustrative** | Swept S-8 |

**No parameter is classified "externally sourced."** Phase 2 Layer A work is what would change that. Until then the project's defence is sensitivity analysis, not claimed calibration — which is the honest position.

---

## 9. Integrity-anomaly scenarios

Per your instruction, normal scenarios are internally coherent (identity exact in 100% of rows) and reconciliation testing is done in **separately labelled anomaly scenarios** rather than by corrupting the main generator. Anomaly construction is a Phase 3 item; the design is: generate a coherent path, then apply a labelled corruption (inflated claimed revenue, orders/AOV mismatch, resubmission divergence) and confirm the integrity engine fires. This keeps the model-risk lesson available without letting an internal bug contaminate the research population.

---

## 10. Test evidence

```
$ python3 -m pytest rbf_sim/tests/ -q
169 passed in 0.10s
```

Includes 13 new tests for the revenue chain and closure scenarios: `test_gmv_is_the_only_exact_identity`, `test_deduction_chain_is_monotonically_decreasing`, `test_closure_drives_revenue_to_exactly_zero`, `test_closure_preserves_the_identity_at_zero`, `test_revenue_alias_is_gmv`, and others. The accounting identity holds in **100%** of generated rows across all scenarios including closure boundaries — against **61% violation** in the original generator.
