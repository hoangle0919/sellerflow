# Frozen Methodology Specification

**Project:** Revenue-Contingent Financing Under Volatile Sales — A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers
**Version:** 1.0
**Status:** 🔒 **FROZEN 2026-08-03**, before any outcome analysis.
**Supersedes:** `METRIC_DEFINITIONS.md` v0.1 (retained for audit trail; §4.3 terminology and §3 benchmark structure are superseded here).

> **Amendment rule.** Changes after the first outcome run are appended to §15 with date, rationale, and the result visible at the time. Silent edits invalidate the freeze. An empty §15 at submission means no definition changed after a result was seen.

---

## 1. Population and Vietnam context

**Target population.** Small e-commerce sellers operating on Shopee, TikTok Shop, or Lazada in Vietnam, transacting in VND, with limited or no credit-bureau (CIC) file — the population the product was designed for.

**What this study does and does not observe.** No Vietnamese seller is observed. No revenue, repayment, or default outcome in this study is empirical. The population definition scopes which *parameter ranges* are plausible and which public evidence is relevant; it does not license any claim about seller behaviour.

**Vietnam-specific structure entering the model** (all flagged `assumption` until Phase 2 sources them):

| Feature | Treatment |
|---|---|
| Tết (lunar new year, Jan–Feb) | Demand distortion — pre-Tết lift, post-Tết trough |
| Platform mega-sale events (9.9, 10.10, 11.11, 12.12) | Q4 revenue concentration |
| Currency | VND throughout; no FX |
| Credit-bureau coverage | Motivates the problem only; not a model input |

**Generalization limit (binding on all outputs).** ~~in a Vietnam-calibrated parameter range~~ → **superseded by A-8: "Vietnam-*motivated* and illustratively parameterized."** No parameter in this spec was estimated from Vietnamese data; the market motivates the study and does not calibrate it. Findings are statements about contract mechanics under stated assumptions, in a Vietnam-motivated and illustratively parameterized range. They do not generalize to other markets, to sellers outside the modelled range, or to observed behaviour anywhere.

---

## 2. Unit of analysis

**One (seller revenue path × financing contract) pair over the simulation horizon.**

A *path* is one realization of monthly revenue. A *run* applies all four contracts (§7–§8) to the **same** path. Comparisons are always within-path paired differences; no cross-path comparison is made.

---

## 3. Simulation horizon

- **Primary:** `T = 24` months.
- **Reported recovery checkpoints:** 12, 18, 24 months.
- **Sensitivity:** `T ∈ {18, 24, 36}`.

Rationale: 24 months covers the base-case payoff of all contracts with margin for shock-extended durations, while keeping the horizon binding enough that incomplete recovery is informative. At `T = 36` the horizon rarely binds (verified: `01_verify_spec.py` check C3), making incomplete-recovery rates uninformative.

---

## 4. Revenue-path generation

Multiplicative decomposition:

```
R_t = R_0 · G_t · S_t · K_t · ε_t
```

| Term | Meaning | Default |
|---|---|---|
| `R_0` | Baseline monthly revenue | 185,000,000 VND |
| `G_t = (1+g)^t` | Deterministic trend | `g ∈ {-0.03, 0, +0.03}` monthly |
| `S_t` | Seasonal multiplier, period 12 | §5 |
| `K_t` | Shock multiplier | §5 |
| `ε_t ~ LogNormal(−σ²/2, σ²)` | Idiosyncratic noise, `E[ε]=1` | `σ = 0.15` |

**Coupled operational variables — accounting identities enforced, not sampled.** Correcting the independence defect found in the original generator (audit RI-2):

```
AOV_t  = AOV_0 · (1 + δ_t),   δ_t ~ Normal(0, 0.05)     [sampled]
orders_t = R_t / AOV_t                                   [DERIVED — identity]
returns_t = return_rate_t · orders_t                     [DERIVED — identity]
net_revenue_t = R_t · (1 − return_rate_t)                [DERIVED — identity]
```

**Rule.** Exactly one of `{R_t, orders_t, AOV_t}` may be derived; the other two are sampled. Any field linked by an identity is **never** independently drawn. Enforced by test, not by convention (§10, `test_identities.py`).

**Non-negativity.** `R_t ≥ 0` by construction (all multipliers positive). Paths are not truncated or reflected.

---

## 5. Seasonality and shock assumptions

### 5.1 Seasonality
`S_t` is a fixed 12-month multiplier vector, mean-normalized to 1.0 so seasonality redistributes revenue without changing the annual total.

| Profile | Shape |
|---|---|
| `flat` | all 1.0 |
| `moderate` | Q4 lift, post-Tết trough, amplitude ±20% |
| `strong` | same shape, amplitude ±40% |

⚠️ The moderate/strong shapes are **assumptions**, not measurements. Phase 2 attempts calibration against public Vietnamese e-commerce seasonality evidence; if none of adequate quality is found, they remain assumptions and are swept in §12. Their status is stated wherever a seasonal result appears.

### 5.2 Shocks
`K_t = 1` outside the shock window.

| Shock | Definition |
|---|---|
| `none` | `K_t = 1 ∀t` |
| `disruption_1m` | one month at `1 − d` |
| `decline_sustained` | from `t_s` onward, `1 − d` permanently |
| `decline_gradual` | linear decay to `1 − d` over 6 months, then flat |
| `downturn_multi` | `1 − d` for 6 months, then linear recovery over 6 |
| `platform_outage` | one month at `1 − d`, `d = 0.7` |
| `returns_spike` | `return_rate` × 3 for 3 months (affects net revenue, not gross) |

Defaults: `d ∈ {0.20, 0.40, 0.60}`, `t_s = 7`.

---

## 6. Contract set

Four contracts per path. All originate at `t = 1` with identical principal `A`.

| ID | Contract |
|---|---|
| **FIX-A** | Fixed payment, matched principal **and** matched total repayment (§7.1) |
| **FIX-B** | ~~Conventional~~ → **Illustrative 18%/12-month amortizing reference** at an assumed APR (§7.2, A-8) |
| **RBF** | Baseline revenue-based financing (§8.1) |
| **RBF-G** | Guardrailed revenue-based financing (§8.2) |

---

## 7. Fixed-payment benchmarks

### 7.1 Benchmark A — matched principal, matched total repayment *(primary)*

```
N   = D_RBF(base path)                  RBF base-case payoff month
P_A = C / N                             where C = A · f
p_t^{FIX-A} = P_A   for t ≤ N,   0 otherwise
```

Principal, total repayment, and term are all identical to RBF under the base path. **The only difference is the timing of payments within the term.** This isolates repayment timing and is the primary benchmark for H1–H3.

Implied APR is **solved and reported**, never assumed:
```
A = Σ_{t=1..N} P_A / (1+i)^t      →     APR = (1+i)^12 − 1
```

### 7.2 Benchmark B — illustrative 18%/12-month amortizing reference *(practical comparison)*
> ~~"conventional amortizing loan"~~ superseded by A-8. "Conventional" implies a prevailing market product; `j = 18%` and `N_B = 12` are assumed inputs, neither sourced nor observed.

Standard annuity at documented nominal annual rate `j`, monthly `i = j/12`, term `N_B`:

```
P_B = A · i / (1 − (1+i)^{−N_B})
```

Total repayment `N_B · P_B ≠ C` in general. **B is never used for cost-matched claims.** ~~It answers "what would a seller realistically be offered instead?"~~ → **superseded by A-8.** It answers "how does this contract compare against an illustrative 18%/12-month amortizing reference?" No claim is made that such a product is available to this population, or on these terms. It is reported in a separate column with `j` and `N_B` stated inline.

Defaults: `j = 0.18`, `N_B = 12`, both provisional pending Phase 2 sourcing and swept in §12.

> **Commensurability limit — stated wherever A and B appear together.** An APR loan prices time; a factor-rate cap prices a multiple regardless of time. A is matched at the base path and diverges as revenue departs from it. B is not matched at all. We claim neither product is economically equivalent to RBF — only that A isolates timing and B is an ~~realistic alternative~~ → **illustrative reference (A-8)**: an 18%/12-month amortizing schedule at an assumed rate. No claim is made that such a product is available to this population, or on these terms.

---

## 8. RBF contracts

### 8.1 RBF — baseline
```
p_t^{RBF} = min( r · R_t ,  C − Σ_{s<t} p_s )        C = A · f
```
No contractual maturity. Duration is an **output**.

### 8.2 RBF-G — guardrailed
```
p_t^{RBF-G} = min( max( r·R_t , p_min ) , p_max , C − Σ_{s<t} p_s )
```
Hardship rule: if `R_t < h · R_0` the floor `p_min` is suspended (`p_t = r·R_t`).

Defaults: `p_min = 0.25·r·R_0`, `p_max = 2.0·r·R_0`, `h = 0.5`.

---

## 9. Matched-comparison rules

1. **Shared path.** One path generated per seed; all four contracts consume the identical `R_t` vector.
2. **Shared principal.** `A` identical across contracts.
3. **Shared origination.** `t = 1`.
4. **Disclosed, never assumed:** principal, origination, horizon, factor rate, remittance rate, cap, floor/ceiling, hardship rule, APR (solved for A, stated for B), fees, early-repayment treatment.
5. **Fees.** Zero in v1.0. Non-zero fees are out of scope and named as a limitation.
6. **Early repayment.** Not modelled — no contract prepays. Named as a limitation.
7. **Reporting.** Every table names its benchmark (A or B). A and B never appear in the same cost-matched comparison.

---

## 10. Metric formulas

### 10.1 Payment burden
```
PB_t = p_t / R_t                    undefined where R_t = 0 (excluded, §13)
```
Reported: mean, median, **max**, **p90**, **p95** over months where `p_t > 0`.

### 10.2 🔒 High-payment-burden month *(primary; renamed per binding decision)*
```
HPB_t(θ) = 1  if  PB_t > θ
n_HPB(θ) = Σ_t HPB_t(θ)
```
**Pre-specified thresholds, all reported:** `θ ∈ {0.10, 0.15, 0.20, 0.25}`.

> **Structural note, stated wherever this metric appears.** For RBF, `PB_t ≡ r` until the cap binds, so RBF's burden is constant *by construction*. The metric therefore does not test whether RBF stabilizes burden — that is definitional. The information is on the fixed side: **how far, how often, and under which conditions a fixed payment's burden rises as revenue falls**, and what that costs in duration. Direction is by construction; magnitude and the duration trade-off are not.

**Terminology (binding).** This metric is computed from revenue alone. It is called a **high-payment-burden month** and never "distress," because revenue alone cannot establish that a seller is in financial distress.

### 10.3 Distress month *(secondary, assumption-dependent)*
```
OCF_t = m·R_t − F − p_t
D_t   = 1 if OCF_t < 0
```
Reported **only** in tables that state `m` and `F` inline, always labelled assumption-dependent. Never a headline. Subject to the coherence constraint in §14.

### 10.4 Repayment duration
```
Dur = min{ t : Σ_{s≤t} p_s ≥ C }      ( = censored at T if never )
```
Censoring reported as a rate; never imputed.

### 10.5 Total repaid and cost
```
TotalRepaid = Σ_{t≤T} p_t
TotalCost   = TotalRepaid − A
Multiple    = TotalRepaid / A
```

### 10.6 Provider recovery at checkpoints
```
Rec(k)  = Σ_{t≤k} p_t              k ∈ {12, 18, 24}
RR(k)   = Rec(k) / C
```

### 10.7 Incomplete recovery within horizon
```
IR = 1  if  Σ_{t≤T} p_t < C
```
> ⚠️ **Not a default rate and never called one.** It measures failure to reach the cap within the observation window on a simulated path. It carries no information about borrower behaviour, willingness to pay, or credit loss. Papers, slides, and UI use "incomplete recovery within horizon."

### 10.8 Recovery following a negative shock
For shock onset `t_s`:
```
PostShockRec(k) = Σ_{t=t_s..t_s+k} p_t          k ∈ {6, 12}
```

### 10.9 Underreporting sensitivity
Provider observes `ω·R_t`; true revenue is `R_t`.
```
p_t^{RBF}(ω) = min( r·ω·R_t , C − Σ_{s<t} p_s )
```
Reported: `Rec(k)`, `RR(k)`, `Dur`, `IR` across `ω ∈ {1.00, 0.95, 0.90, 0.80, 0.70}`.
FIX-A and FIX-B are invariant to `ω` by construction. ~~reported plainly as an advantage of fixed structures~~ → **superseded by A-8:** the supportable statement is **contractual schedule invariance** — `q_t = P` contains no revenue term. It is not a collection claim, and the model assumes those payments are made in full and on time.

### 10.11 Completion concepts *(added 2026-08-04, amendment A-6)*

```
Mathematical completion:  exists finite T with  r · S_T  >=  f · A     (exact arithmetic)
Operational completion:   f·A − r·S_T  <=  eps                          (settlement tolerance)
```

`eps` is a **declared settlement policy**, not a numerical convenience. Every reported completion month names which concept and, if operational, the value of `eps`.

**Current state (amendment A-7, 2026-08-06 — D-023 applied).** `eps = 0` by construction. The operational layer settles in **integer đồng** (`rbf_sim/settlement.py`): each payment is quantized under a documented ROUND_HALF_UP rule and then clipped to the remaining contractual cap, so the cap is reached exactly and no tolerance is required. The analytical layer carries **no epsilon at all**; where it is evaluated in floating point it uses one centralized `FLOAT_GUARD_VND = 1e-6`, which is a representation-error guard and is a million times smaller than the smallest unit of account. A non-zero `eps` remains permissible as a **declared commercial term** and must then be reported alongside any completion month derived from it.

### 10.10 Flexibility / recovery trade-off
```
Flexibility (seller) : Δ n_HPB(θ)     = n_HPB^{FIX-A} − n_HPB^{RBF}
Cost (provider)      : Δ Dur          = Dur^{RBF} − N
                       Δ RR(12)       = RR^{FIX-A}(12) − RR^{RBF}(12)
                       sd(Dur), IQR(Dur) across paths
```
Reported as a paired table and a scatter of `Δn_HPB` against `ΔRR(12)`.

---

## 11. Random seeds

| Stream | Rule |
|---|---|
| Path generation | `seed = BASE_SEED + path_index`, `BASE_SEED = 20260803` |
| Bootstrap resampling | `BOOTSTRAP_SEED = 90210`, independent stream |
| Parameter sweeps | Seeds held **fixed** across arms and parameter values, so differences are structural, not sampling artifacts |

Every recorded result stores its seeds. Reruns with identical seeds must reproduce **numerically at published precision**, and byte-identically **within a fixed runtime** (A-8 / D-041). ~~bit-for-bit~~ was too strong: on macOS CPython 3.11.5 two artifacts differ in 9 and 2 last-bit floating-point values. Check with `research/verify_reproduction.py`.

---

## 12. Sensitivity ranges

| # | Parameter | Range |
|---|---|---|
| S-1 | Burden threshold `θ` | 0.10 · 0.15 · 0.20 · 0.25 |
| S-2 | Remittance rate `r` | 0.06 · 0.08 · 0.10 · 0.12 · 0.15 |
| S-3 | Factor rate `f` | 1.10 · 1.15 · 1.20 · 1.30 |
| S-4 | Advance `A` | 0.5 · 1.0 · 2.0 · 3.0 × `R_0` |
| S-5 | Trend `g` | −0.03 · 0 · +0.03 monthly |
| S-6 | Noise `σ` | 0.05 · 0.15 · 0.30 |
| S-7 | Seasonal amplitude | flat · moderate · strong |
| S-8 | Shock depth `d` | 0.20 · 0.40 · 0.60 |
| S-9 | Shock type | all seven of §5.2 |
| S-10 | Underreporting `ω` | 1.00 · 0.95 · 0.90 · 0.80 · 0.70 |
| S-11 | Horizon `T` | 18 · 24 · 36 |
| S-12 | Guardrails | off · default · tight |
| S-13 | Benchmark B rate `j`, term `N_B` | j ∈ {0.12, 0.18, 0.24}; N_B ∈ {12, 18, 24} |
| S-14 | Margin `m`, fixed cost `F` *(secondary metric only)* | m ∈ {0.15,0.25,0.35,0.45}; F/R₀ ∈ {0.10,0.20,0.30} |

**Headline-fragility rule.** Any headline claim that reverses sign anywhere in S-1…S-14 is demoted from "finding" to "condition-dependent observation," and the reversing condition is named in the abstract.

---

## 13. Exclusion rules

Pre-specified, applied mechanically, and **reported as counts** — never silently dropped.

| # | Rule | Handling |
|---|---|---|
| E-1 | `R_t = 0` in month `t` | `PB_t` undefined; month excluded from burden stats, retained for payments |
| E-2 | Contract never reaches cap within `T` | `Dur` censored at `T`; counted in `IR` |
| E-3 | IRR has no sign change | Reported "undefined"; path retained |
| E-4 | Parameter set violates §14 coherence | Excluded from the *secondary* distress metric only; retained for all primary metrics; count reported |
| E-5 | `AOV_t ≤ 0` after sampling | Path regenerated with next seed; regeneration count reported |

No path is excluded for producing an unfavourable result. Exclusion counts appear in every results table.

---

## 14. Coherence constraint (secondary metric only)

For the assumption-dependent distress metric (§10.3), a parameter set is coherent only if:
```
m·R_0 − F − P_A > 0
```
Verification found that at `m = 0.25`, `F = 0.20·R_0` and the advance size the current product recommends, distress returns 100% of months for *both* arms — the metric fails by degeneracy rather than by evidence.

**Handling.** Incoherent sets are excluded from §10.3 only (E-4), never from primary metrics, and the incoherent region is **reported as a result**: it bounds the parameter space in which a financing structure of this size ~~is affordable~~ → **fails the study's illustrative burden/coherence rule (A-8)**. That is a statement about the stated rule, not about affordability, which this project cannot assess. Original wording follows for the audit trail: in which no financing structure of this size is affordable.

**Related product observation — provisional, not quotable until Phase 2 sources `m` and `F`.** `financing_engine.py` sizes the advance as a percentage of annual revenue and never reads margin or fixed costs, so repayment capacity is never tested. Under illustrative parameters the recommended advance is roughly double an indicative serviceable bound.

---

## 15. Limits on interpretation *(binding on paper, poster, deck, README, and UI)*

1. **No observed outcomes.** Every number is generated by a model whose parameters we chose. No claim about any real seller, lender, or market is supported.
2. **No default prediction.** No labeled outcomes exist. `IR` is not a default rate (§10.7).
3. **No causal claims.** A simulation of one's own assumptions cannot identify a causal effect.
4. **No significance testing.** Intervals quantify **Monte Carlo precision only** — how stable a number is given the number of paths run. Running more paths narrows every interval without adding a fact about the world. No p-values are reported. Uncertainty about the world is addressed *only* through §12, and only over the ranges specified there.
5. **Direction vs magnitude.** H1 is partly true by construction (§10.2). Reported results distinguish what is definitional from what is measured, in the same sentence.
6. **Benchmark provenance.** Every comparison names benchmark A or B and its matching basis.
7. **Assumption status.** Seasonality, shock shapes, `m`, `F`, `j`, `N_B` are assumptions until Phase 2 sources them, and are labelled as such wherever they appear.
8. **The ensemble model is a secondary demonstration component.** It is not the source of any research finding. The historical 0.92 AUC appears only where needed to explain the methodological correction.

---

## 16. Amendments after first outcome run

### A-8 — Terminology and unsupported factual premises corrected · 2026-08-10
**Visible at the time:** every registered result. **This amendment changes no parameter, no formula, no seed, no scenario and no result.** It corrects wording that claimed more external grounding than this project has, and one notation collision. Recorded here rather than silently edited, per the amendment rule in §0.

| Was | Now | Why |
|---|---|---|
| "Vietnam-calibrated parameter range" (§2) | "Vietnam-**motivated** and illustratively parameterized" | No parameter was estimated from Vietnamese data. The market motivates the study; it does not calibrate it. |
| "Conventional amortizing loan" (§7, §7.2) | "Illustrative 18%/12-month amortizing reference" | "Conventional" implies a prevailing market product. `j = 18%`, `N_B = 12` are assumed inputs, neither sourced nor observed. |
| "what would a seller realistically be offered instead?" (§7.2) | "how does this contract compare against an illustrative 18%/12-month amortizing reference?" | The original asserts knowledge of the offer set facing this population. None was gathered. |
| "platforms settle after returns" (A-1 rationale) | **Pending external support.** The *definitional* argument is retained; the factual premise is marked unverified. | No platform settlement documentation was obtained or cited. |
| "Real RBF contracts commonly carry a maturity date" (A-4 rationale) | **Pending external support.** The mechanical rationale is retained. | No market survey of RBF terms was conducted, so "commonly" is unsupported. |
| `F·A` in the completion condition | `f·A` | **Notation collision.** `F` denotes fixed operating cost in `METRIC_DEFINITIONS.md`; the factor rate is lowercase `f` in this spec's own notation table. |

**Affordability.** Wherever an arm was described as "affordable", the supportable statement is only whether it clears **the illustrative burden bands chosen for this study** (10/15/20/25% of revenue). Those bands are reporting thresholds, not validated hardship cutoffs, and burden is measured against revenue rather than against what the seller retains. No affordability claim is made or supported.

**Fixed-payment "advantage".** The supportable statement is **contractual schedule invariance** — `q_t = P` contains no revenue term, so the schedule does not respond to reported revenue. This is not a collection claim: the model assumes fixed payments are made in full and on time, and therefore represents an **optimistic scheduled-recovery benchmark**.

**Rationale.** Raised by an external claim audit at Gate A. Every item above was a statement the project could not support from its own artifacts or any cited source. Correcting them changes no number; leaving them would have put unsupported factual assertions into a paper.

---

### A-7 — Integer-VND settlement applied; scattered tolerances removed · 2026-08-06
**Change.** D-023's proposed correction is **approved and applied**. A single module, `rbf_sim/settlement.py`, now holds the monetary rule. The operational layer represents money as integer đồng: payments are quantized under an explicit ROUND_HALF_UP rule, then clipped to the remaining contractual cap, in that order — so rounding can never breach the cap and the final payment is an exact remainder. Cap comparison is integer equality, so the settlement `eps` is **0 by construction**. The analytical layer keeps the exact definition `r·S_T ≥ f·A` with **no epsilon**; the `tol = 0.5` defaults in `metrics.duration`, `metrics.incomplete_recovery` and `contracts.rbf_duration`, and `CAP_TOL = 1.0` in the derivation tests, are replaced by one centralized `FLOAT_GUARD_VND = 1e-6`.
**Rationale.** D-023 established that the 0.5 was a floating-point workaround, not a settlement rule: inconsistent across modules, absent from this specification, over-provisioned by ~5×10⁶, and not shaped like a whole-đồng rule. Re-measured in this repository over 3,000 paths × 10 baseline scenarios against exact `fractions.Fraction` arithmetic, worst-case per-payment deviation is **9.2387×10⁻⁸ VND** and no path fails to reach an exactly-reached cap at `tol = 0`.
**Impact on registered results: zero.** `baseline_v2.json` and `validation_v1.json` were regenerated after the change and compared leaf-by-leaf against the registered artifacts: **1 differing leaf, the embedded run date.** Every quantity is unchanged, including `f* = 1.0945`, the matched 13-month / 17,076,923 VND benchmark, and the 37.87% implied APR. The registered result files are therefore **retained unmodified** — nothing changed, so nothing is replaced.
**Not changed.** No proposition in `DERIVATIONS.md` (byte-identical, verified). The `ε` sensitivity table at `ρ*` (213 / 221 / 266 for `ε` = 1.0 / 0.5 / 0.01) is retained and reclassified from "engine behaviour" to **declared-policy sensitivity**, which is what it always described.

### A-1 — Revenue definition and remittance basis · 2026-08-03
**Visible at the time:** `baseline_v1` results (§F-1…F-5 of `BASELINE_FINDINGS.md`).
**Change.** §4 now specifies the full revenue chain. `gmv = orders × AOV` is the **only exact identity**; returns, platform fees, and taxes are **deductions from** GMV, not components of it. Added `net_sales`, `cash_receipts`, `platform_fee_rate`, and a contractual `remittance_basis` parameter. **Decision: remittance basis = `net_sales`.** `revenue` remains an alias for `gmv` as the burden denominator.
**Rationale.** Requested as a definitional clarification, independent of any result. ~~platforms settle after returns~~ → **superseded by A-8: pending external support.** No platform settlement documentation was obtained or cited by this project, so the factual premise is unverified. The *definitional* argument stands on its own and is what the amendment rests on: if remittance were computed on GMV, it would charge a share of money the seller never receives. Not result-driven — the change was specified before its effect was computed.
**Consequence.** Materially changes results. Baseline re-run as **`baseline_v2`**; `baseline_v1` superseded and retained only for audit trail. Matched benchmark moves 12 → 13 months, `P = 17,076,923`, implied APR 37.87%. Added sweep **S-16** over `{gmv, net_sales, cash_receipts}` and **S-15** over `platform_fee_rate ∈ {0, 0.05, 0.10}`.

### A-2 — Closure and zero-revenue scenarios · 2026-08-03
**Change.** Added shocks `closure` (revenue → 0 permanently), `temporary_closure` (3 zero months then partial recovery), and `extended_downturn` (deep, 12 months, then 6-month recovery). §13 E-5 amended: `orders = 0` is permitted so zero-revenue months are representable while the identity still holds exactly at the boundary.
**Rationale.** Baseline v1 found 0.0% incomplete recovery everywhere. Rather than accept a horizon artifact as a safety finding, the spec was extended to search for the failure region (decision D-013, committed before this run).
**Consequence.** Located the boundary — see `CORRECTED_CLAIMS.md` §5.

### A-3 — Terminal maturity / write-off rule · 2026-08-03
**Change.** `ContractTerms.terminal_maturity` (0 = none). After that month the contract matures and any unrecovered balance is written off.
**Rationale.** ~~Real RBF contracts commonly carry a maturity date.~~ → **superseded by A-8: pending external support.** No market survey of RBF contract terms was conducted, so "commonly" is unsupported. The amendment rests on the mechanical reason alone: without a maturity date, incomplete recovery could not bind at any horizon, so the model could not represent the failure case it exists to study.
**Consequence.** Write-off at month 18 turns a −40% sustained decline from 0% to 25.7% incomplete recovery.

### A-4 — Interpretation-layer corrections · 2026-08-03
**Change.** (i) "Findings" → "reproducible simulation findings under modeled assumptions" throughout. (ii) Price and structure separated: cost claims must name the cap factor. (iii) The underreporting conclusion is restricted to *contractual* invariance — the model contains no default, insolvency, or liquidity-constrained nonpayment, so no claim about realized fixed-loan collection is supported. (iv) Intervals are labelled **Monte Carlo intervals over simulated paths**, never confidence intervals; `bootstrap_ci` now returns `label`, `measures`, and `does_not_measure` fields so the framing travels with the number.
**Rationale.** Four interpretation errors identified in review before the claims became public.
**Consequence.** §15 rules 4 and 9 strengthened. No numeric result changed.

### A-6 — Completion concepts and settlement tolerance · 2026-08-04
**Change.** §10.11 added, distinguishing **mathematical completion** (exact `r·S_T ≥ f·A` at finite `T`) from **operational completion** (`f·A − r·S_T ≤ ε`). Every reported completion month must name its concept and, if operational, its `ε`.
**Rationale.** At the geometric boundary `ρ = ρ*` the two diverge permanently: mathematical completion never occurs; operational completion occurs at month 213 / 221 / 266 for `ε` = 1.0 / 0.5 / 0.01. Reporting a single unqualified "completion month" would be ambiguous.
**Not changed *at the time of A-6*.** ~~The engine's `ε = 0.5` default is retained… which is not applied.~~ → **STALE, superseded by A-7 (D-043):** the integer-VND correction **was** subsequently approved and applied (D-024), `ε = 0` by construction, and the `0.5` defaults were replaced by a single `FLOAT_GUARD_VND = 1e-6`. Read A-7 for current behaviour. Original text retained below for the audit trail. The engine's `ε = 0.5` default is retained. D-023 classifies it as a floating-point workaround and proposes an integer-VND correction, which is **not applied** — financial behaviour is not changed without approval, and the measured impact on registered results is zero.

### A-5 — RBF-G demoted · 2026-08-03
**Change.** RBF-G moves from headline arm to documented design-flaw finding.
**Rationale.** Analytic result: the floor binds only when observed revenue `< p_min_mult·R₀ = 0.25·R₀`, but applies only when revenue `≥ hardship·R₀ = 0.50·R₀`. The conditions are mutually exclusive, so **the floor can never activate on any revenue path**. Provably dead code, which fully explains the baseline v1 null.
**Not done:** the parameters were **not** retuned to make the guardrail bind. That would be tuning after seeing results. The breakpoint scan reports where it *would* activate; the design flaw stands as the finding.
