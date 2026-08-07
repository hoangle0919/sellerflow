# Baseline Findings — Reproducible Simulation Results Under Modeled Assumptions

> **SUPERSEDED in part by `CORRECTED_CLAIMS.md` (2026-08-03).** This document reports `baseline_v1` on the `gmv` remittance basis. The basis was corrected to `net_sales` (spec amendment A-1) and the baseline re-run as `baseline_v2`. Provider-side figures here are superseded by R-012; the F-2 cost claim is superseded by the price/structure separation in D-015. Retained for audit trail.

**Run:** `baseline_v1` · 2026-08-03 · 500 paths/scenario · base seed 20260803
**Spec:** `METHODOLOGY_SPEC.md` v1.0 (frozen before this run)
**Code:** `rbf_sim/` · `run_baseline.py` → `results/baseline_v1.json`
**Tests:** 146 passing (`pytest rbf_sim/tests/ -q`)

> ⚠️ **Every figure below is simulated.** No observed seller revenue, repayment, or default outcome exists in this study. These are statements about contract mechanics under the assumptions in the frozen spec — not about Vietnamese sellers. See spec §15.

**Parameters:** `R₀ = 185,000,000 VND` · `A = 185,000,000` · `r = 0.10` · `f = 1.20` → `cap = 222,000,000` · `T = 24` · Benchmark B: `j = 18%` nominal, `N_B = 12`.

---

## Benchmark A matching — verified

| | |
|---|---|
| RBF base-case duration `N` | 12 months |
| Matched fixed payment `P` | 18,500,000 VND/month |
| Matched total repayment | 222,000,000 VND (= cap) |
| **Implied APR, solved** | **41.30%** |

Principal, total repayment, and term are identical to RBF on the reference path. **Only payment timing differs.** This is the identification claim, and it is asserted by test (`test_benchmark_a_is_cost_matched_to_rbf_exactly`).

---

## F-1 — The core trade-off, quantified

Paired within-path differences, **FIX-A minus RBF**. Positive seller column = RBF gives fewer high-burden months. Positive provider column = fixed recovers more capital by month 12. Brackets are bootstrap intervals on Monte Carlo precision only.

| Scenario | Seller: Δ high-burden months (θ=0.15) | Provider: Δ RR(12) |
|---|---|---|
| stable | 0.06 [0.04, 0.08] | 1.6pp [1.4, 1.8] |
| seasonal | 0.29 [0.25, 0.33] | 1.6pp [1.4, 1.8] |
| seasonal (strong) | 1.32 [1.26, 1.38] | 1.6pp [1.4, 1.9] |
| growth | 0.15 [0.12, 0.18] | 0.0pp [0.0, 0.0] |
| 1-month disruption | 1.28 [1.24, 1.32] | 4.1pp [3.8, 4.4] |
| platform outage | 1.28 [1.24, 1.32] | 5.4pp [5.1, 5.7] |
| gradual decline | 0.92 [0.84, 1.00] | 13.2pp [12.9, 13.5] |
| sustained decline | 3.67 [3.57, 3.76] | 21.6pp [21.3, 21.9] |
| **severe downturn** | **6.24 [6.19, 6.28]** | **32.5pp [32.3, 32.8]** |

**Reading.** The benefit is real and scales with severity: under a severe downturn RBF removes ~6 of 24 months in which the payment would have exceeded 15% of revenue. The cost scales too — the provider recovers 32.5pp less of the cap by month 12, and mean duration extends from 12.0 to 18.3 months.

**What is definitional vs measured.** That RBF's burden is flat is *definitional* — `PB_t ≡ r` until the cap binds, asserted in `test_rbf_burden_is_constant_by_construction`. What is *measured* is the magnitude on the fixed side (max burden reaching 30.0% under severe downturn vs 10.0% for RBF) and the size of the duration/recovery price paid for it.

---

## F-2 ⚠️ At these parameters, RBF is materially more expensive than a conventional loan

Benchmark B — a plain 18% nominal amortizing loan over 12 months — repays **203.6M** on a 185M advance. Benchmark A, cost-matched to the RBF cap, repays **222.0M**, an implied **41.30% APR**.

**RBF at `f = 1.20` over a 12-month base case costs roughly 2.3× the interest of an 18% conventional loan.** Mean payment burden is correspondingly higher for FIX-A (10.2%) than FIX-B (9.4%) in the stable scenario.

This runs against the product and is reported as a headline, not a footnote. The defensible framing is not "RBF is cheaper" — it is not — but "RBF converts a fixed obligation into a revenue-contingent one, and that conversion has a measurable price." Whether that price is worth paying depends on the seller's volatility, which is exactly what F-1 quantifies.

*Caveat:* `j = 18%` and `N_B = 12` are provisional assumptions pending Phase 2 sourcing, and are swept in S-13. The direction is robust across the sweep range; the magnitude is not yet sourced.

---

## F-3 ⚠️ Within a 24-month horizon, RBF's risk is timing, not loss

Incomplete-recovery rate is **0.0% in every scenario**, including severe downturn. Total repaid is 222,000,000 (multiple 1.200) in all ten scenarios. The cap is always reached; only the date changes.

**Implication.** At these parameters the provider's exposure is *duration risk*, not principal loss. Provider-side language must say so precisely. Any claim that RBF increases provider losses is unsupported by this run.

**Limitation, stated plainly.** This is partly an artifact of horizon and shock design: `T = 24` with a 12-month base duration leaves substantial headroom. The parameter region where recovery genuinely fails has not yet been located. **Phase 3 must find it** — via S-11 (`T = 18`), deeper shocks, larger advances (S-4), and combined underreporting. Reporting 0% incomplete recovery without searching for the failure region would be a weak result presented as a strong one.

---

## F-4 — Underreporting delays recovery almost exactly proportionally

| ω | RBF duration | RR(12) | RR(24) | Total repaid |
|---|---|---|---|---|
| 1.00 | 12.5 | 98.4% | 100.0% | 222,000,000 |
| 0.95 | 13.1 | 94.9% | 100.0% | 222,000,000 |
| 0.90 | 13.9 | 90.2% | 100.0% | 222,000,000 |
| 0.80 | 15.9 | 80.2% | 100.0% | 222,000,000 |
| 0.70 | 18.1 | 70.1% | 100.0% | 222,000,000 |
| **FIX-A** | **12.0** | **100.0%** | **100.0%** | **222,000,000** *(invariant)* |

`RR(12) ≈ ω` to within 0.2pp across the range — underreporting passes through to 12-month recovery essentially one-for-one, while 24-month recovery is unaffected.

**The finding that runs against the product:** a fixed payment cannot be diverted from, because it never reads revenue. This is a genuine structural advantage of fixed-payment financing and appears in the paper as such, not buried in a limitations paragraph.

---

## F-5 ⚠️ The default guardrails never bind — RBF-G is currently a null arm

RBF-G is **identical to RBF in all ten scenarios**, to every reported digit.

Cause: `p_min = 0.25·r·R₀ = 4.625M` requires revenue below 25% of baseline to bind; `p_max = 2.0·r·R₀ = 37M` requires revenue above 200%. Neither occurs at `σ = 0.15` with shocks of ≤60%.

**This is a null result and is reported as one.** The guardrail design as currently parameterized does nothing. Phase 3 runs S-12 "tight" to locate where guardrails begin to matter, and reports the boundary. If they never matter within plausible ranges, that is the finding — and it is a direct product implication: the guardrail feature would be decoration.

---

## Verification performed

| Check | Result |
|---|---|
| Accounting identities across 2,400+ generated rows | 0 violations (was 61% in the original generator) |
| Reconciliation ratio vs integrity engine's [0.55, 1.75] band | all rows at exactly 1.00 (was 62.3% flagged) |
| Benchmark A cost-matching | exact to <1 VND |
| Annuity formula | NPV discounts back to principal to 1e-9 |
| Determinism | identical seeds reproduce bit-for-bit |
| Test suite | 146 passed |

One test failure occurred during development: a hand-computed annuity constant was wrong (9,174,708 vs the correct 9,168,000). **The constant was corrected, not the code** — and an independent NPV round-trip test was added so the assertion no longer depends on a hand-typed number.

---

## What this run does NOT establish

- Nothing about real Vietnamese sellers. No observed data exists.
- No default prediction. Incomplete recovery is not a default rate.
- No causal claim.
- No significance claim. Intervals are Monte Carlo precision; more paths narrow them without adding facts about the world.
- Seasonality shapes, shock magnitudes, `j`, `N_B`, `m`, and `F` remain **assumptions** pending Phase 2 sourcing.

---

## Next actions

1. **Locate the recovery-failure region** (F-3) — S-11, S-4, deeper shocks, combined underreporting.
2. **Find where guardrails bind** (F-5) — S-12 tight.
3. **Source `j`, `N_B`, seasonality** (F-2) — Phase 2 Layer A.
4. Full S-1…S-14 sweep with the headline-fragility rule applied.
5. Correct the public README and remove the stale deployment link — **blocked on repository access**.
