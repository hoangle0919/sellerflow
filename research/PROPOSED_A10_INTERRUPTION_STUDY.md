# PROPOSAL — A-10: conditional interruption sensitivity study

**STATUS: PROPOSAL FOR REVIEW. NOT REGISTERED. NOTHING HAS BEEN RUN.**

This document is a specification and analysis plan only. It registers no result,
amends no spec, and creates no artifact. `METHODOLOGY_SPEC.md` §16 is **not**
edited by this document — if approved, A-10 would be appended there as a separate
act.

**Amendment register checked 2026-10-05:** §16 of `METHODOLOGY_SPEC.md` contains
A-1 … A-9 (A-9 being the IRR definition amendment, 2026-08-20). No A-10 exists
anywhere under `research/`. **A-10 is therefore free and is the number proposed
here.**

**Registered results are preserved.** `baseline_v3`,
`baseline_equalcost_v2`, `baseline_closure_v2`,
`baseline_closure_equalcost_v2` and `validation_v2` are untouched, as are claims
S-1 … S-5. §6 below is written specifically to keep their checksums
reproducible, which is a binding constraint on the implementation and not a
preference.

---

## 1. Research question

**Conditional on a revenue interruption occurring, how do its timing, duration
and post-interruption recovery affect seller payment burden, financier recovery,
and contractual completion?**

Three things are deliberately outside this question:

- **Interruption frequency** — how often interruptions occur. §8 of
  `CALIBRATION_EVIDENCE.md` records that the evidence for this is not adequate.
  Everything here is conditional on an interruption occurring.
- **Population default probabilities.** No default model exists in this study and
  none is introduced. Incomplete recovery is a contractual-completion measure,
  never a default rate (spec 10.7, and the `FORBIDDEN` patterns in
  `backend/tests/test_public_copy.py`).
- **Any claim of calibration to Vietnamese merchants.** Per A-8 the study is
  Vietnam-*motivated* and illustratively parameterized. **Every range in §3 is
  illustrative unless this document states a specific source for it, and none
  currently does.**

---

## 2. Reference and continuity cells

Two cells exist to anchor the design to what is already registered.

| Cell | Definition | Purpose | Must satisfy |
|---|---|---|---|
| **REF** | no interruption (`d = 0`), all else at centre | interruption-free reference | reproduces `baseline_v3` → `/scenarios/seasonal/` numerically at published precision |
| **CONT** | `onset = 7`, `d = 3`, mode `step`, `λ = 0.50` | continuity check against the existing `temp_closure` | reproduces `baseline_closure_v2` → `/scenarios/temp_closure/` for **all four arms** |

**CONT is load-bearing twice over.** It is both the continuity check the review
asked for and the correctness test for the implementation route in §6: the
existing `temp_closure` is exactly `onset = 7, d = 3, step, λ = 0.50`
(`run_closure_baseline.py:54` with `generator.py:62-67`), so new code that cannot
reproduce it is wrong, and no other cell should be believed until it does.

---

## 3. Factor definitions and illustrative ranges

The interruption acts through the existing shock-multiplier channel: a vector
`K_t` applied multiplicatively inside path generation, **before** the
orders/AOV identity is formed, so `gmv = orders × aov` continues to hold exactly
(spec 4; audit RI-2). It is *not* applied to a generated series after the fact.

### 3.1 Onset — `m₀`

**Definition.** The 1-indexed month of the **first** interrupted month.

**Illustrative range.** `m₀ ∈ {4, 7, 10, 13, 16, 19, 22}`.

**Why these.** They straddle the 13-month matched base-case term at `f = 1.20`,
so the design spans interruptions arriving well before, at, and well after the
point where an undisturbed contract would have completed. `m₀ = 7` is the centre
and matches every existing shock scenario.

### 3.2 Duration — `d`

**Definition.** The number of **consecutive** months with `K_t = 0` exactly, for
`t ∈ [m₀, m₀ + d − 1]`. In those months `gmv_t = 0`, `net_sales_t = 0`, and the
remittance base is `0`.

**Illustrative range.** `d ∈ {0, 1, 2, 3, 6, 9}`, where `d = 0` is REF and
`d = 3` is CONT.

**Explicitly not claimed.** These lengths are **not** drawn from the World Bank
household-business figures. §8 of `CALIBRATION_EVIDENCE.md` records that the
reviewed aggregates do not identify contiguous episode lengths, so no value of
`d` here is evidence-backed. The range is chosen to span the span, not to
estimate it.

**Single contiguous episode only.** This design does not model repeated or
intermittent interruptions. That is a deliberate scope limit, and it means the
study cannot speak to the distinction between one long and several short
interruptions — which is, separately, the thing the published aggregates could
not identify.

### 3.3 Post-interruption recovery — `λ` and mode

**Definition.** For `t ≥ m₀ + d`, revenue resumes at a fraction of the
**counterfactual uninterrupted path** for that month — i.e. `λ` multiplies the
same trend × seasonality × idiosyncratic draw the path would have had anyway. It
is a fraction of the counterfactual, **not** a fraction of `R0`; the two differ
whenever seasonality or growth is non-flat. (See U4 — this is a reviewable
choice.)

**Two modes, exactly defined:**

| Mode | `K_t` for `t ≥ m₀ + d` |
|---|---|
| **`step`** | `K_t = λ`, constant for the remainder of the horizon — a permanent level change |
| **`ramp`** | `K_t = λ + (1 − λ)·min((t − (m₀+d) + 1) / r, 1)`, rising linearly from `λ` to `1.0` over `r` months |

**Illustrative range.** `λ ∈ {0.00, 0.25, 0.50, 0.75, 1.00}`; mode ∈
{`step`, `ramp`}; `r = 6` fixed (matching the ramp length already used by
`decline_gradual` and `downturn_multi` in `generator.py`).

**Naming the three cases the review asked to be distinguished:**

- **Immediate** recovery = `step` with `λ = 1.00` — revenue returns to the
  counterfactual at once.
- **Gradual** recovery = `ramp` — reaches the counterfactual after `r` months.
- **Permanent** impairment = `step` with `λ < 1.00` — never returns.

`λ = 0.00` under `step` is permanent closure with a delayed label; it should
reproduce the existing `closure_m{m₀}` behaviour and is retained as a second
continuity probe rather than a new finding.

---

## 4. Shared revenue paths and random-number control

**The requirement:** identical underlying revenue paths across contracts and
across matched experimental cells, with controlled streams.

**This already holds by construction, and the design depends on it.** In
`generator.generate_path`, a single `random.Random(seed)` draws `eps` and the AOV
perturbation per month, and **neither draw depends on `K_t`**. The shock enters
only as a multiplier on the target revenue. Therefore, for a fixed seed:

- the `eps` and AOV sequences are **identical across every cell** in §3, and
- all four arms within a cell see the **same** path object.

So differences between cells are attributable to the interruption geometry alone,
and differences between arms to contract structure alone.

**Seeding.** `base_seed = 20260803` (spec 11) and the existing per-path seed
derivation, unchanged. Path *i* in cell X has the same seed as path *i* in cell Y.

**The one way this can break, and the guard.** The AOV loop regenerates on a
non-positive draw, which consumes extra randomness and would desynchronise the
stream. It requires a draw below `−1/aov_sigma = −20σ`, so it should never fire —
but "should never" is not a check. **V3 in §8 asserts `regenerations == 0` across
the entire run and asserts stream equality directly rather than inferring it.**

---

## 5. Contract terms are fixed before the interruption

**No repricing after observing a shock.** This is already structural, and the
design does not weaken it:

- FIX-A is matched on `reference_base_path(params, terms)`, which is flat `R0`
  with no trend, seasonality, shock or noise (spec 7.1). It therefore **cannot**
  see `K_t`.
- The `match` dict is computed once per cell from that reference path. Because the
  reference path is shock-free, **`match` must be byte-identical across every
  cell in the design** — asserted as V5 in §8.
- `f` (the cap factor) and FIX-B's `(j, N_B)` are inputs, not fitted quantities.

A contract is priced at origination; an interruption in month `m₀` cannot
retro-price it. That is what keeps the paired comparison non-circular, and it is
the same argument `run_closure_baseline.py` already makes.

---

## 6. Implementation route — **the principal unresolved choice**

`canonical.generator_fingerprint()` hashes the six `rbf_sim` modules, and the
resulting digest sits **inside** `body["canonical"]`, which `canonical_sha256`
then hashes (`rbf_sim/canonical.py:62-70, 136-158, 255`). So **editing any of the
six modules changes the canonical checksum of every artifact regenerated
afterwards** — including the checksums cited in `CLAIM_LEDGER.md`
(`36372901…`, `b3ebfe6a…`, `21b8e207…`, `e1e6d81b…`, `7d9b9d0f…`).

Three routes exist. **They are not equivalent and the choice needs approval.**

| Route | What it changes | Cost |
|---|---|---|
| **R1 — new module, no edits to the six** *(recommended)* | adds `rbf_sim/interruption.py` + `run_interruption_sensitivity.py`, declared via `extra_sources` | ~40 lines of cohort/aggregation glue duplicated from `engine.run_scenario`; divergence risk, mitigated by V1/V2/V7 |
| **R2 — edit `generator.py` and `engine.py`** | cleanest code, no duplication | **breaks regenerability of all five registered checksums.** Not acceptable without explicit approval |
| **R3 — add a generic `K`-vector hook to `generator.py` only** | smaller edit than R2 | same fingerprint consequence as R2 |

**Why R1 works.** `generator_fingerprint(extra_sources)` already accepts extra
files, and every existing runner declares itself that way
(`run_baseline.py:203`, `run_closure_baseline.py:110`,
`run_equal_cost_baseline.py:108`). A new artifact can fingerprint the new module
without the six changing, so existing artifacts keep reproducing exactly.

**Why R1 needs care.** `engine.run_scenario` generates its own cohort internally
and inlines the aggregation, and `generator.shock_multipliers` *raises* on an
unknown kind, so there is no injection point for an arbitrary `K`. R1 therefore
reimplements the generation loop with an injected `K` and the aggregation block.
**Duplicated financial logic is exactly how two sources of truth appear**, so R1
is only acceptable with V1, V2 and V7 passing — V7 in particular asserts the new
glue reproduces `engine.run_scenario` exactly for a shock the existing generator
already supports.

**Post-hoc multiplication is rejected outright.** Generating a shock-free path
and multiplying `gmv` afterwards would break `gmv = orders × aov` — the identity
whose violation in 61% of rows was audit finding RI-2. The interruption must
enter before orders are derived.

---

## 7. Outcomes, with denominators stated

Per cell, per arm. Existing metric definitions are reused unchanged; the
denominator conventions are those of A-6 and A-9.

| Outcome | Field | Denominator / conditioning |
|---|---|---|
| Completion share | `completed_rate` | all paths |
| Rate-definedness | `apr_defined_rate` | all paths — **a different denominator from completion** (A-9) |
| Amount recovered at horizon | `total_repaid_mean` | all paths |
| **Amount outstanding at horizon** | `outstanding_at_T` = `cap − total_repaid` | all paths; **new derived field**, floored at 0. `cap = A · f` (`contracts.py:35`); note `A = 185,000,000` in `run_baseline.py:25`, not the dataclass default — so `cap = 222,000,000` at `f = 1.20` |
| Duration | `duration_mean`, `duration_sd` | **completed paths only** — must be printed adjacent to `completed_rate`, never alone |
| Effective rate | `apr_mean` | **paths with a defined IRR only** (A-9), reported beside `apr_defined_rate` and `irr_upper_bound` |
| Payment burden | `burden_mean/max/p90/p95` | **active months only** — see §7.1 |
| High-burden months | `n_high_burden[θ]`, θ ∈ {.10,.15,.20,.25} | active months |

### 7.1 Payment burden when revenue is zero — a measurement gap this design must close

`metrics.payment_burden` returns `None` where `R_t = 0` (spec 13, E-1), and
`burden_stats` keeps only months where the burden is defined **and** `p_t > 0`.

For RBF that is harmless: `p_t = r · 0 = 0` in an interrupted month, so there is
nothing to report. **For the fixed arms it is actively misleading.** FIX-A and
FIX-B owe their full scheduled payment while revenue is zero — the single worst
month a fixed schedule can produce — and that month is **silently dropped** from
every burden statistic because the ratio is undefined. In a study whose whole
subject is revenue interruption, the metric excludes the months of interest.

An unbounded ratio is not the fix. The proposal is three complementary
non-ratio measures, reported per arm per cell:

| New field | Definition |
|---|---|
| `zero_revenue_months` | count of `t` with `R_t = 0` (a property of the path; identical across arms) |
| `payments_due_on_zero_revenue` | count of `t` with `R_t = 0` **and** `p_t > 0` |
| `vnd_due_on_zero_revenue` | `Σ p_t` over those months, in đồng |

and a reporting rule: **wherever `burden_*` appears, `zero_revenue_months` and
`payments_due_on_zero_revenue` appear beside it**, so a reader can see how many
months the burden statistic excluded. This is the same discipline A-9 applied to
`apr_mean` and `duration_mean`.

These live in the new module under R1, not in `metrics.py` (see U2).

### 7.2 Interruptions near or beyond the horizon

Three distinct edge cases, handled distinctly rather than by truncation:

1. **Interruption would extend past `T`** (`m₀ + d − 1 > T`). **The cell is
   excluded from the design and listed as excluded** (table T1). A truncated
   interruption confounds duration with horizon censoring, so including it would
   corrupt exactly the comparison the study is making.
2. **Contract may already have completed before onset.** Legitimate and
   informative, not a defect — a late interruption *should* do nothing to a
   contract already closed. Reported as a new field
   **`share_completed_before_onset`**, and any cell where it is non-zero must
   carry it alongside the outcome, because the interruption effect there is
   diluted by construction.
3. **Path does not complete by `T`.** The existing convention stands: no duration
   is defined, the path enters `incomplete_recovery_rate`, and `duration_mean`
   remains a survivor statistic (A-6).

---

## 8. Comparison strategy, and the limits on any ranking

**Within a cell, between arms.** Paired at the path level — same seed, same
revenue — using the existing `paired_delta` and `bootstrap_ci`.

**Across cells.** Three levels, in increasing strength of claim:

1. **Main-effect ranges.** For each factor, vary it alone around the centre cell
   (`m₀ = 7`, `d = 3`, `step`, `λ = 0.50`) and report the range each outcome
   spans.
2. **Two-factor surfaces.** Full factorial on `onset × duration` at centre `λ`,
   and on `duration × λ` at centre onset. These are the two pairs most likely to
   interact: duration determines how much of the term is lost, onset determines
   *which* part, and `λ` determines whether the remaining term can make it up.
3. **Interaction contrasts** read off those surfaces — specifically whether the
   effect of duration depends on onset (expected, since a long interruption
   starting at month 19 has less remaining term to recover in).

**Binding limits on interpretation:**

- **Any importance ranking is conditional on the chosen ranges and the chosen
  outcome measure, and the ranges in §3 are illustrative.** A ranking is a
  statement about this grid, not a property of revenue-based financing. §7 of
  `CALIBRATION_EVIDENCE.md` already records that the recovery level has *not*
  been shown to matter more than timing or duration; this design is what would
  test that, and its answer inherits the grid's arbitrariness.
- **Bootstrap intervals describe Monte-Carlo sampling error over the 500-path
  ensemble only.** They are not uncertainty about Vietnamese sellers, and no
  population inference may be drawn from them.
- **No frequency-weighted statement** may be assembled from these cells. Without
  an interruption frequency, a weighted average across cells has no meaning, and
  producing one would smuggle in the parameter §1 excludes.

---

## 9. Run budget, verification, and planned output

### 9.1 Budget

| Stage | Cells | Basis |
|---|---|---|
| Reference + continuity | 3 | REF, CONT, `λ=0` probe |
| Main effects | ~14 | one factor varied at a time around centre |
| `onset × duration` | 7 × 5 = 35 | at `λ = 0.50`, `step` |
| `duration × λ` | 5 × 5 = 25 | at `m₀ = 7`, `step` |
| `ramp` mode subset | ~10 | headline cells only (U7) |
| **Total** | **≈ 80 cells**, minus overlaps and §7.2(1) exclusions | 500 paths × 4 arms per cell |

≈ 80 cells is ~8× one existing baseline run (10 scenarios × 4 arms × 500 paths).

**A timing probe is required before implementation is approved**, not after: one
cell timed end-to-end, multiplied out, reported back. If the projection is
unacceptable the grid shrinks — `onset × duration` is the stage to cut first.
**No silent truncation:** if any cell is dropped for budget, T1 lists it as
dropped-for-budget, distinct from excluded-by-§7.2.

**Both cap factors?** S-4 showed the `closure_m13` incomplete rate moving by a
factor of ten between `f = 1.20` and `f* = 1.0945` — price alone. Running the
full grid at both doubles the budget; running at one risks reporting a
price-specific result as a structural one. **Recommendation: full grid at
`f = 1.20`, plus the main-effect and continuity cells at `f*`**, with every
headline figure labelled by its `f`. (U5.)

### 9.2 Verification checks — all must pass before any result is reported

| | Check |
|---|---|
| **V1** | **CONT** reproduces `baseline_closure_v2` → `temp_closure` for all four arms, numerically at published precision |
| **V2** | **REF** reproduces `baseline_v3` → `/scenarios/seasonal/`. That is the right target because the closure runner sets no `seasonality` or `growth`, so both inherit the `PathParams` defaults (`moderate`, `0.0`) |
| **V3** | Stream control: for every pair of cells, per-path `eps` and `aov` sequences are **equal**; and `regenerations == 0` across the whole run. Asserted directly, not inferred |
| **V4** | Identity `gmv_t = orders_t × aov_t` holds exactly in **every** month of every path, including interrupted months (`n = 0 → gmv = 0`) |
| **V5** | `match` is byte-identical across all cells (follows from §5; if it is not, the reference path is seeing the shock and the design is invalid) |
| **V6** | Registered artifacts still reproduce: `verify_reproduction.py` passes unchanged, and the five canonical checksums are byte-recomputed and compared |
| **V7** | Under R1, the new glue reproduces `engine.run_scenario` **exactly** for a shock the existing generator supports |
| **V8** | Sanity, reported not assumed: `outstanding_at_T` non-decreasing in `d` at fixed `(m₀, λ, mode)`. A violation is investigated, not smoothed |

V6 is the one that protects the existing claim system; if it fails, the route is
R2/R3 in disguise and the work stops for re-approval.

### 9.3 Planned tables and figures

- **T1** — design grid: cells run, excluded by §7.2(1), dropped for budget
- **T2** — main-effect range per outcome, with the centre cell stated
- **T3** — continuity and verification results (V1–V8), pass/fail with figures
- **T4** — burden table: `burden_*` with `zero_revenue_months` and
  `payments_due_on_zero_revenue` in adjacent columns, per arm
- **F1** — completion share over `onset × duration`, one panel per arm
- **F2** — `outstanding_at_T` against `d`, one line per `λ`, per arm
- **F3** — `vnd_due_on_zero_revenue` against `d`, by arm — the fixed-vs-contingent
  contrast that §7.1 exists to make visible
- **F4** — duration-conditional-on-completion against onset, with
  `completed_rate` plotted on the same panel so the denominator is never hidden

---

## 10. Unresolved choices requiring a decision before implementation

| | Choice | Recommendation |
|---|---|---|
| **U1** | Implementation route R1 / R2 / R3 (§6) | **R1.** R2 and R3 cost the regenerability of five registered checksums |
| **U2** | New zero-revenue metrics in the new module, or amend `metrics.py` | **New module.** Amending `metrics.py` triggers the §6 fingerprint problem |
| **U3** | The factor ranges in §3 | Need sign-off. All illustrative; none evidence-backed |
| **U4** | `λ` relative to the counterfactual path (proposed) or to `R0` | **Counterfactual**, consistent with existing `K_t` shocks — but it means `λ` interacts with seasonality, which `R0`-relative would not |
| **U5** | One cap factor or both (§9.1) | Full grid at `f = 1.20`, main effects also at `f*` |
| **U6** | Total budget after the timing probe | Probe first, then decide; cut `onset × duration` first |
| **U7** | Include `ramp` in stage 1, or defer to a follow-up | Include a small subset — "gradual vs permanent" is one of the three cases the question names, so omitting it answers only two-thirds of it |
| **U8** | Whether `share_completed_before_onset > 0` cells belong in the main grid or a separate panel | Separate panel. Their interruption effect is diluted by construction and mixing them into a mean would understate the effect |

---

## 11. What this study can and cannot conclude

**Can.** Which interruption patterns — in timing, length and aftermath — a
revenue-contingent structure absorbs and a fixed schedule does not, and at what
cost in duration and provider recovery, **under stated and illustrative
assumptions**, conditional on an interruption occurring.

**Cannot.** How often interruptions occur; any default rate; anything about
observed Vietnamese sellers; and any frequency-weighted or portfolio-level
statement. The A-8 generalization limit applies to every output: findings are
statements about contract mechanics under stated assumptions, in a
Vietnam-motivated and illustratively parameterized range.

**Deliverable on approval:** implementation under the chosen route, V1–V8
reported before any substantive figure, then T1–T4 and F1–F4. A-10 would be
appended to `METHODOLOGY_SPEC.md` §16 at that point, not before.
