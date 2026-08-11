# Analytical Backbone — Structural Properties of the Contracts

**Status:** Mathematical results. **Independent of any simulation, parameter choice, or revenue distribution.**
**Validated by:** `rbf_sim/tests/test_derivations.py` — every proposition is asserted numerically against the engine.

> **Why this exists.** None of the project's thirteen parameters is externally calibrated. Numerical magnitudes are therefore *illustrations*, not estimates. The propositions below hold for **any** revenue path, so the simulations demonstrate proven structural relationships rather than estimating real-world impact. This is what the project can legitimately claim.

---

## Setup

Months `t = 1, 2, …`. All quantities in one currency.

| Symbol | Meaning | Constraint |
|---|---|---|
| `B_t` | Remittance base in month `t` (contractually, net sales) | `B_t ≥ 0` |
| `S_k = Σ_{t≤k} B_t` | Cumulative remittance base through month `k` | non-decreasing |
| `A` | Advance principal | `A > 0` |
| `f` | Factor rate | `f > 1` |
| `C = A·f` | Repayment cap | `C > A` |
| `r` | Remittance rate | `r ∈ (0, 1)` |
| `P` | Fixed monthly payment | `P > 0` |
| `N` | Fixed-loan term | `N ∈ ℕ` |
| `ω` | Proportional reporting factor | `ω ∈ (0, 1]` |

**RBF contract.** `p_t = min( r·B_t , C − Σ_{s<t} p_s )`, and `p_t ≥ 0`.

**Fixed contract (Benchmark A).** `q_t = P` for `t ≤ N`, else `0`, with `N·P = C`.

No distributional assumption is made about `B_t` anywhere below. `B_t` may be deterministic, stochastic, seasonal, trending, or zero.

---

## P1 — RBF payment burden equals the remittance rate until the final capped payment

**Proposition.** Let `k* = min{ k : r·S_k ≥ C }` (`= ∞` if no such `k`). Then

```
p_t / B_t = r          for all t < k*  with B_t > 0
p_{k*} / B_{k*} ≤ r    at the capped month
p_t = 0                for all t > k*
```

**Proof.** For `t < k*` we have `r·S_{t} < C`, and since `p_s = r·B_s` for all `s < t` by induction, the residual is `C − r·S_{t−1} > r·B_t`. The `min` therefore selects `r·B_t`, giving `p_t/B_t = r`. At `t = k*` the residual `C − r·S_{k*−1}` is by definition `≤ r·B_{k*}`, so the `min` selects the residual and the ratio is `≤ r`. Beyond `k*` the residual is zero. ∎

**Consequence for interpretation.** RBF's flat payment burden is **definitional, not empirical**. No simulation can provide evidence for it, and none is claimed. What simulation contributes is the *magnitude of the contrast* with the fixed arm, and the duration cost incurred to obtain it.

**Implementation note.** The engine reports burden against `gmv`, while remittance is charged on `net_sales`. The reported burden is therefore `r·(1 − return_rate)`, constant for constant return rate. P1 holds exactly with respect to the contractual base.

---

## P2 — Fixed-payment burden rises strictly as revenue falls

**Proposition.** For the fixed contract with `t ≤ N`, burden `PB_t = P/B_t` is strictly decreasing in `B_t`, with constant elasticity `−1`:

```
d(PB_t)/d(B_t) = −P/B_t² < 0        and        d ln PB_t / d ln B_t = −1
```

and `PB_t → ∞` as `B_t → 0⁺`. If revenue falls by a factor `λ ∈ (0,1)`, burden rises by exactly `1/λ`.

**Proof.** Immediate by differentiation; the elasticity follows from `ln PB_t = ln P − ln B_t`. ∎

**Consequence.** A −50% revenue month **doubles** fixed-payment burden, exactly, for any `P` and any `B_t`. This is the structural asymmetry the project studies, and it requires no calibration to state.

---

## P3 — Cumulative-sales condition for reaching the cap

**Proposition.** The RBF contract reaches its cap by month `k` **if and only if**

```
S_k  ≥  C / r  =  A·f / r
```

The repayment duration is `D = min{ k : S_k ≥ A·f/r }`.

**Proof.** By P1, cumulative RBF payments through `k` equal `min(r·S_k, C)`. This equals `C` iff `r·S_k ≥ C`. ∎

**Consequence — path shape is irrelevant to *whether*, only to *when*.** The threshold `A·f/r` is a constant. Seasonality, volatility, and shock timing affect duration only through their effect on the *cumulative* series.

> **⚠️ Scope correction (D-042).** This paragraph previously continued: ~~"Two sellers with identical cumulative sales reach the cap at the same month regardless of how differently that revenue was distributed in time."~~ **Withdrawn — it confuses the terminal cumulative total with the cumulative trajectory.** Duration is the **first passage time** `D = min{k : S_k ≥ A·f/r}`, a property of the whole path `S_1, S_2, …`, not of its endpoint. Two sellers with the same *terminal* cumulative base can cross the threshold in different months: front-loaded revenue crosses earlier, back-loaded later. Equal first-passage months follow only from **identical cumulative trajectories up to the crossing**, or trivially from both crossing at the same `k`. What the proposition actually says is that duration depends on the path *only through* `S_k` — which is a much weaker and correct statement.

At `A = R₀`, `f = 1.20`, `r = 0.10`: required cumulative base `= 12·R₀`. The contract needs twelve months of baseline revenue in total, whenever it arrives.

---

## P4 — When RBF provider recovery leads or lags fixed-payment recovery

**Proposition.** Define the **break-even revenue level**

```
B*  =  P / r
```

For any horizon `k ≤ N`, before either contract caps out, RBF cumulative recovery exceeds fixed cumulative recovery **if and only if the mean remittance base over the first `k` months exceeds `B*`**:

```
r·S_k  >  k·P        ⟺        (1/k)·S_k  >  P/r  =  B*
```

**Proof.** Cumulative fixed recovery through `k ≤ N` is `k·P`. Cumulative RBF recovery is `r·S_k` while uncapped (P1). Compare and divide by `k·r > 0`. ∎

**This proposition explains the sign reversal observed in R-012.** Whether RBF recovers faster or slower is **not** a property of the structure — it is determined entirely by whether realized average revenue exceeds `B*`.

**Corollary (why the stable scenario favours RBF).** Benchmark A sets `N = ⌈C/(r·B̄)⌉` on a reference path with constant base `B̄`. Then

```
B* = P/r = C/(r·N) = C / (r·⌈C/(r·B̄)⌉)  ≤  B̄
```

with equality only when `C/(r·B̄)` is an integer. **Whenever the duration rounds up, `B* < B̄` strictly, so RBF leads on recovery even at exactly baseline revenue.** In `baseline_v2`, `C/(r·B̄) = 12.37` rounds to `13`, giving `B* ≈ 0.951·B̄` — which is why the stable scenario shows RBF ahead by 4.3pp rather than tied. The effect is an artifact of integer rounding in the matching rule, and is now documented rather than mistaken for an economic finding.

---

## P5 — Proportional underreporting scales recovery exactly, and raises the cumulative-sales threshold by `1/ω`

> **⚠️ Heading and summary corrected (D-040).** This section was previously titled "…and duration inversely", and the §A summary read "duration by `1/ω`". **That is wrong and is withdrawn.** What scales exactly by `1/ω` is the *required cumulative remittance base* `S_k ≥ A·f/(r·ω)` — a threshold. Duration is the **first passage time** to that threshold, which depends on the shape of the path, not only on the threshold's level. The proof below always said this correctly; only the heading and the summary overstated it. Empirically, in the `baseline_v2` sweep mean duration runs 12.862 months at `ω = 1.00` and 18.690 at `ω = 0.70`; exact inverse scaling would give 12.862/0.70 = 18.374.

**Proposition.** If the provider observes `ω·B_t`, then while the cap is not binding:

```
recovery through k:   G_k(ω) = ω · G_k(1)          (exactly linear in ω)
duration:             D(ω) = min{ k : S_k ≥ A·f/(r·ω) }
total repaid:         unchanged at C, provided S_T ≥ A·f/(r·ω)
```

**Proof.** Substituting `ω·B_t` into P1 gives `p_t = r·ω·B_t` while uncapped, so cumulative recovery scales by `ω`. The cap condition of P3 becomes `r·ω·S_k ≥ C`, i.e. `S_k ≥ A·f/(r·ω)`. ∎

**Consequence.** Underreporting is a **timing attack, not a principal-loss attack**, so long as the horizon is long enough. The required cumulative sales scales as `1/ω`; the total eventually collected is unchanged. Recovery-ratio pass-through is exactly one-for-one, which is why the simulated `RR(12) ≈ ω` to within 0.2pp — that near-identity is a theorem, not a fitted result.

**What this does not establish.** The fixed contract's `q_t = P` contains no `B_t` term, so it is **contractually** invariant to `ω`. This says nothing about whether a lender *collects* `P` from a seller whose revenue has fallen. The model contains no default, insolvency, or liquidity-constrained nonpayment. **Contractual invariance is not collection immunity**, and no claim of the latter is made.

---

## P6 — Effective cost depends jointly on the cap and on revenue timing

**Proposition (a) — the money multiple is path-independent.** If the cap is reached, total repaid is `C = A·f` for every revenue path. The multiple is exactly `f`.

**Proposition (b) — the internal rate of return is path-dependent.** Let `p` and `p′` be two RBF payment streams that both sum to `C`. If `p` arrives weakly earlier — `Σ_{t≤k} p_t ≥ Σ_{t≤k} p′_t` for all `k`, with strict inequality for some `k` — then

```
IRR(p)  >  IRR(p′)
```

**Proof.** Write `NPV(i) = Σ_t p_t·v^t` with `v = 1/(1+i) ∈ (0,1)`. By Abel summation, `NPV(i) = Σ_k (Σ_{t≤k} p_t)(v^k − v^{k+1}) + (Σ_t p_t)·v^{T+1}`. Since `v^k − v^{k+1} > 0` and the totals agree, dominance of partial sums gives `NPV_p(i) > NPV_{p′}(i)` for every `i > 0`. Both are strictly decreasing in `i` with the same limits, so the root of `NPV(i) = A` is strictly larger for `p`. ∎

**Consequence — "the APR of RBF" is not well defined as a contract property.** Two sellers on *identical terms* `(A, r, f)` face different effective APRs purely because their revenue arrives at different speeds. Faster revenue → earlier payments → same total, higher APR.

This is the formal reason the earlier claim "RBF costs 2.3× a conventional loan" was wrong on two counts: it fixed `f = 1.20` as though it were intrinsic (P6a shows cost is proportional to `f`), and it quoted a single APR as though it were a contract property (P6b shows APR is jointly determined by `f` and the path).

**Equal-cost pricing.** Since total cost is `A·f` and is monotone increasing in `f`, for any target cost there exists an `f` attaining it — subject only to the integrality of duration. Solving against the 18% amortizing benchmark gives `f* ≈ 1.0945`. **Price and structure are separable, and P6 is why.**

---

## P7 — Exact conditions for incomplete recovery

> **⚠️ CORRECTED 2026-08-04.** An earlier version of this section claimed "decline alone cannot cause incomplete recovery," justified by a parenthetical equating *strictly positive revenue* with *revenue bounded away from zero*. **Those are not the same condition.** A geometrically decaying path is strictly positive in every period yet has a **finite** lifetime sum, so the cap may be unreachable with no zero-revenue month, no maturity rule, and no horizon limit. The general statement is about **cumulative lifetime revenue**, not about revenue remaining positive. Full correction below; the superseded claim is recorded in D-020.

### P7 (general form)

**Proposition.** The RBF contract completes repayment over an applicable horizon `H` (a finite evaluation horizon, a contractual maturity, or the business lifetime, whichever binds first) **if and only if**

```
r · Σ_{t ≤ H} B_t  ≥  f · A          equivalently        S_H  ≥  f·A / r
```

Incomplete recovery is exactly the complement: `S_H < f·A/r`.

**Proof.** Immediate from P3 applied at `H`, together with monotonicity of `S_k`. ∎

**This is the complete characterisation.** Everything below is a special case of it.

### Four distinct causes of incomplete recovery

| # | Cause | Mechanism |
|---|---|---|
| 1 | **Business closure / zero-revenue periods** | `B_t = 0` for `t ≥ c` freezes `S` at `S_{c−1}`. Absorbing: no horizon extension helps. |
| 2 | **Binding maturity or write-off rule** | `H = M` truncates the sum before the threshold is reached. |
| 3 | **Finite evaluation horizon** | `H = T`. A *measurement* artifact, not an economic loss — the contract might still complete later. |
| 4 | **Strictly positive but sufficiently fast-decaying revenue** | `Σ_{t=1}^{∞} B_t` **converges** to a finite value below `f·A/r`. Revenue is positive in every period, forever, and the cap is still never reached. |

Cause 4 was **missing** from the earlier version. It is not exotic: any geometric decline is of this form.

### The convergence criterion

Let `S_∞ = Σ_{t=1}^{∞} B_t ∈ (0, ∞]`.

```
S_∞ = ∞   (series diverges)   →  completion is guaranteed given an unbounded horizon
S_∞ < ∞   (series converges)  →  completion iff  S_∞ ≥ f·A/r ;  otherwise NEVER, at any horizon
```

### Completion is a finite-time property

**Definition (binding).** The contract **completes** iff there exists a **finite** month `T` with

```
r · Σ_{t ≤ T} B_t  ≥  f · A
```

Completion in the limit is **not** completion. This distinction is vacuous when `S_∞ = ∞` but decisive at the convergent boundary, below.

**Worked case — geometric decay.** Indexing follows the implementation (`generator`/test helper `geometric`, `k in range(n)`): `B_t = B_0·ρ^{t}` for `t = 0, 1, 2, …`, so `B_0` enters at full weight.

```
S_∞ = B_0 / (1 − ρ)
S_T = B_0 (1 − ρ^{T+1}) / (1 − ρ)   <   S_∞      strictly, for every finite T
```

Because `ρ^{T+1} > 0` for all finite `T`, **no finite partial sum ever attains `S_∞`.** Therefore:

```
completion in finite time  ⟺  r·S_∞ > f·A  ⟺  ρ  >  ρ* = 1 − r·B_0/(f·A)
```

**The inequality is strict.** An earlier version of this section wrote `ρ ≥ ρ*`, which is wrong — see D-022.

With `A = B_0 = 100M`, `f = 1.20`, `r = 0.10`: `ρ* = 1 − 10/120 = 11/12 ≈ 0.916667`. **At the other registered cap factor `f* = 1.0945`, `ρ* = 0.908634`** — the threshold moves with the price, so 11/12 must never be quoted as *the* threshold (D-040).

| Case | Lifetime `r·S_∞` | Verdict |
|---|---|---|
| `ρ = 0.90 < ρ*` | 100M < 120M | **Never completes.** Revenue positive every month forever; lifetime cumulative is simply insufficient. |
| **`ρ = 11/12 = ρ*`** | **= 120M exactly** | **Never completes in finite time.** Repayment approaches the cap asymptotically from below and never reaches it. An *asymptotic boundary case*, not a completion. |
| `ρ = 0.95 > ρ*` | 200M > 120M | Completes at a finite month. |

**The boundary case, computed.** At `ρ = ρ*` the shortfall `f·A − r·S_T` is strictly positive at every horizon:

| `T` | `r·S_T` | Shortfall (VND) |
|---|---|---|
| 24 | 106,370,898.56 | 13,629,101.44 |
| 60 | 119,405,599.68 | 594,400.32 |
| 100 | 119,981,696.40 | 18,303.60 |
| 200 | 119,999,996.95 | 3.05 |
| 250 | 119,999,999.96 | 0.04 |

Monotonically decreasing, never zero.

### Two completion concepts — both legitimate, and distinct

The 1-VND-scale tolerance in the engine does **not** make the boundary a bug. It creates a second, separately meaningful notion of completion. The research states both.

| Concept | Definition | At `ρ = ρ*` |
|---|---|---|
| **Mathematical completion** | ∃ finite `T` with `r·Σ_{t≤T} B_t ≥ f·A` in exact arithmetic | **Never occurs.** Shortfall is strictly positive at every finite `T`. |
| **Operational completion** | remaining balance `≤ ε`, a settlement tolerance | **Occurs**, at a month determined entirely by `ε`. |

Operational completion month at `ρ = ρ*`, by tolerance:

| `ε` (VND) | First month reported complete |
|---|---|
| 1.00 | 213 |
| 0.50 *(engine default)* | **221** |
| 0.01 | 266 |
| 1e-6 | 373 |
| 0 (exact) | never |

A lender settling to the nearest đồng would genuinely regard the balance as discharged long before month 221. That is a real commercial concept, not an artifact — provided `ε` is a **declared policy** rather than an accident.

> **⚠️ In this codebase it is currently an accident.** See D-023: the tolerance is `0.5` in `metrics.py`/`contracts.py` but `1.0` in the test module, appears nowhere in the frozen specification, and is ~8.4 × 10⁶ times larger than the floating-point error it guards against (measured worst-case deviation from exact rational arithmetic: **5.96 × 10⁻⁸ VND**). It is therefore classified as a floating-point workaround, and an integer-VND correction is **proposed but not applied** — changing financial behaviour requires approval, and D-023 records that it changes **zero** registered results.

**Reported values must name their concept.** "Completion at month 221" without qualification is ambiguous; the paper writes "operational completion (ε = 0.5 VND) at month 221" or "no mathematical completion."

### Corrected logical status

```
"revenue bounded away from zero"   →  SUFFICIENT for eventual completion, NOT necessary
"revenue strictly positive"        →  NOT SUFFICIENT   ← the corrected error
"Σ B_t diverges"                   →  SUFFICIENT for eventual completion (unbounded horizon)
"S_H ≥ f·A/r"                      →  NECESSARY AND SUFFICIENT   ← the general criterion
```

`Σ B_t = ∞` is strictly weaker than `B_t ≥ B_min > 0` — the harmonic path satisfies the former and violates the latter — so the divergence criterion properly generalises the old corollary.

### What this changes about the simulated boundary

The empirical boundary results are **unaffected**: closure at month 7 → 100% incomplete; write-off at 18 months turns a −40% decline from 0% to 25.7%; a −40%/−60% decline over `T = 24` → 0%.

What changes is their **explanation**. Those `decline_sustained` and `extended_downturn` paths step down to a *constant floor* — bounded away from zero — so their cumulative series diverges and the cap is reached given enough time. That is a property of **how those particular scenarios were specified**, not a general property of declining revenue. **The simulation never tested a decaying-to-zero path**, which is precisely why the gap in the theorem went unnoticed: the scenario library had no path that could have exposed it.

This is the sharpest available illustration of why the analytical layer exists. A theorem quantifies over *all* paths; a scenario library only covers the paths someone thought to write down.

---

## Claim taxonomy

Every statement the project makes falls into exactly one of these five classes. The paper, poster, deck, README, and app must label which.

### A. Mathematical properties — hold for any revenue path, no calibration needed
- **P1** RBF burden ≡ `r` until the capped payment.
- **P2** Fixed burden has elasticity `−1` in revenue; a −50% month doubles it.
- **P3** Cap reached iff `S_k ≥ A·f/r`. Path shape affects only *timing* — but note that two paths with the **same terminal cumulative base need not reach the threshold in the same month**. Equal first-passage months follow only from identical cumulative trajectories up to the crossing, or from the crossing occurring at the same `k`.
- **P4** RBF leads fixed on cumulative recovery through `k` iff the **realized mean eligible base** `(1/k)·S_k > B* = P/r` — the exact condition at P4 above. It is *not* captured by the labels "declining" versus "non-declining": a declining path whose realized mean still clears `B*` leads, and a flat path below `B*` lags. Integer rounding of `N` makes `B* < B̄`, which is why the stable scenario leads.
- **P5** Underreporting scales recovery by `ω` exactly and raises the required cumulative base by `1/ω`. **Duration does not generally scale by `1/ω`** — it is the first passage time to that threshold (corrected, D-040).
- **P6** The **contractual repayment target** is `A·f`, path-independently. **Realized total repayment equals it only upon completion**; where the cap is never reached the realized total falls short. APR is path-dependent; price and structure are separable.
- **P7** Completion iff `r·Σ B_t ≥ f·A` over the applicable horizon. Four causes of incomplete recovery: zero revenue, maturity/write-off, finite horizon, **or a strictly positive but fast-decaying path with inadequate lifetime cumulative sales.** Bounded-away-from-zero is sufficient, not necessary; positive is not sufficient. Completion is a **finite-time** property: for geometric decay it requires `ρ > ρ*` **strictly**, since at `ρ = ρ*` the cap is approached asymptotically and never attained.

### B. Simulation results — illustrate A under stated illustrative parameters
Magnitudes in `baseline_v2.json` and `validation_v1.json`. **Not estimates for Vietnamese sellers.** Example: "under the illustrative severe-downturn scenario, RBF removes 6.85 high-burden months at θ=0.15" — a property of that scenario specification, nothing more.

### C. Sensitivity results — how B moves across the parameter grid
S-1…S-16. Where a sign reverses, the claim is demoted to condition-dependent (spec §12).

### D. Product implications — design consequences
- Advance sizing on revenue alone omits repayment capacity (spec §14).
- The RBF-G floor is unreachable as specified (P-RBF-G below); guardrails need joint parameter validation.
- A findings surface must render from versioned result files, never hand-typed numbers.
- Any cost comparison must state the cap factor, by P6.

### E. Questions this project cannot answer
- Actual repayment or default behaviour of real sellers.
- Whether real Vietnamese sellers would accept these terms.
- Realized collection on fixed loans under distress (no default model — P5 note).
- Whether observed revenue volatility resembles the simulated processes.
- Any causal effect of financing structure on business outcomes.

---

## P-RBF-G — the guardrail floor is unreachable (rejected design)

**Proposition.** Under the specified rules — floor `p_min = μ·r·R₀` applied only when `B_t ≥ h·R₀` — the floor binds only if

```
r·B_t < μ·r·R₀   ⟺   B_t < μ·R₀
```

while it applies only if `B_t ≥ h·R₀`. **If `μ ≤ h`, the two conditions are mutually exclusive and the floor can never activate on any revenue path.**

With the specified `μ = 0.25`, `h = 0.50`: `μ < h`, so the floor is **dead code**. ∎

**Exact invariant.** The correct statement of the consequence is:

```
p_t^{RBF-G}  ≤  r·B_t        for every t, on every path
```

and cumulatively, RBF-G can only ever lag plain RBF, never lead it.

**⚠️ Scope correction — the ceiling is a separate rule and does bind.** An earlier draft of this section claimed RBF-G is identical to RBF on every path. That is **too strong and is withdrawn.** The ceiling `p_max = 2·r·R₀` binds whenever `B_t > 2·R₀`, which occurs on spiky paths. The correct decomposition:

| Rule | Status |
|---|---|
| **Floor** | **Provably unreachable** for `μ ≤ h`. Universal, path-independent. Binds **0 of 36,000** month-observations in the breakpoint scan. |
| **Ceiling** | Binds when `B_t > 2·R₀`. **It does bind in the baseline scenarios** — see the count below. Scenario-specific, not a theorem. |

> **⚠️ Second scope correction (D-040) — the row above previously read "Did **not** bind in the ten baseline scenarios because revenue never reached 2× baseline there." That is false and is withdrawn.** Counting month-observations where `r·B_t > p_max = 2·r·R₀` across the full 500 paths of each `baseline_v2` scenario:
>
> | Scenario | Obs. where the ceiling binds | Paths touched |
> |---|---|---|
> | `growth` | 1,400 / 12,000 (11.67%) | 497 / 500 |
> | `seasonal_strong` | 11 / 12,000 | 11 / 500 |
> | `seasonal` | 1 / 12,000 | 1 / 500 |
> | `disruption_1m` | 1 / 12,000 | 1 / 500 |
> | `platform_outage` | 1 / 12,000 | 1 / 500 |
> | `returns_spike` | 1 / 12,000 | 1 / 500 |
> | `stable`, `gradual_decline`, `sustained_decline`, `severe_downturn` | 0 | 0 |
>
> **The correspondence is exact:** RBF-G differs numerically from RBF in precisely those **six** scenarios and is identical in precisely the four where the ceiling never binds. So the observation "RBF-G ≡ RBF in all ten scenarios" is **false as stated**. What is true: the *floor* is universally dead, and the *ceiling* is what makes the two arms coincide in four scenarios and diverge in six. The divergences are small — e.g. `disruption_1m` mean APR 0.36222857 vs 0.36222809 — and vanish at the Lab's display precision, which is why they went unnoticed. **Invisible at display precision is not identical.**
>
> The `platform_outage` and `returns_spike` scenarios were previously offered as cases where the ceiling could not bind. Both in fact bind on one month-observation each.

**A second correction, recorded because it is instructive.** An intermediate test asserted `p_t^{RBF-G} ≤ p_t^{RBF}` pointwise. That is also false: a ceiling-reduced early payment leaves more residual under the cap, so RBF-G can pay *more* in a later month than RBF, which has already capped out. Cap timing confounds any pointwise comparison between the arms. The invariant against `r·B_t` above is confound-free, and is what the test now asserts. **Three attempts were needed to state the consequence correctly; the proposition itself never changed.**

**Decision (D-018).** RBF-G is removed from all public-facing comparisons and selling points. It is preserved in the decision log and this appendix as a **rejected design**. It was **not** retuned after observing results, and no redesigned guardrail enters the frozen analysis as if preregistered. A corrected guardrail requiring `μ > h` is future work.
