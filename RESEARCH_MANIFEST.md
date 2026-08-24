# RBF Research — Manifest

**Project:** Revenue-Contingent Financing Under Volatile Sales — A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers

> ✅ **This repository is the source of truth.** The research lives at `research/` in the `sellerflow` repository (`https://github.com/hoangle0919/sellerflow.git`), integrated from bundle v5 on 2026-08-06. The earlier bundle copies — including the one that sat inside an unrelated Excel research folder because it was the only writable location at the time — are **historical backups only**. They are not authoritative and must not be edited, read from, or depended upon. Nothing in this project depends on, reads, or relates to any Excel file.

**Created:** 2026-08-03 · **Integrated into this repository:** 2026-08-06 (from bundle v5, SHA-256 `6b86194a…f606811`, verified at integration) · **Spec:** `METHODOLOGY_SPEC.md` v1.0 + amendments A-1…A-8

> Everything needed to reproduce every number in the project is in this repository.
>
> ⚠️ All quantitative output is **simulation under modeled assumptions**. No observed seller revenue, repayment, or default outcome exists in this project.

---

## Files

### `research/` — documents

| File | Purpose |
|---|---|
| `METHODOLOGY_SPEC.md` | **The frozen specification.** Population, unit of analysis, horizon, revenue-path generation, seasonality and shocks, both fixed benchmarks, matched-comparison rules, metric formulas, seeds, sensitivity ranges, exclusion rules, interpretation limits. §16 logs all amendments. Frozen before any outcome analysis. |
| `DECISION_LOG.md` | Every decision with date, alternatives, reason, consequence. Includes the methodological correction (D-001) and all supersessions. Append-only. |
| `RESULTS_REGISTRY.md` | Every result with scenario, parameters, code, interpretation, limitation, and public-safety classification. Null results are kept even when they turn out wrong: **N-1 preserved** (0.0% incomplete recovery across the ten non-closure scenarios, horizon- and scenario-bounded); **N-2 superseded** — RBF-G is *not* bit-identical to RBF, and only the narrower **N-2′** (the hardship floor never activates) survives (R-013). |
| `CORRECTED_CLAIMS.md` | **Current claim set.** Corrected interpretation layer, pricing sensitivity, reference-path cost-matched cap, convergence, recovery boundary, RBF-G decision, revenue definition, parameter classification. |
| `DERIVATIONS.md` | **Analytical backbone.** Seven propositions with proofs, established analytically rather than by simulation. P1–P6 hold for any revenue path; P7's completion threshold is exact under the geometric-decline model and depends on the cap factor (ρ\* = 11/12 at `f = 1.20`, 0.9086 at `f* = 1.0945`). Includes the five-class claim taxonomy and the rejected RBF-G design. |
| `PHASE0_AUDIT.md` | Original audit: 8 integrity risks, 6 gaps, evidence appendix. |
| `BASELINE_FINDINGS.md` | `baseline_v1` results. **Partly superseded** — banner at top explains what and why. Retained for audit trail. |
| `METRIC_DEFINITIONS.md` | v0.1, **superseded** by `METHODOLOGY_SPEC.md`. Retained for audit trail. |
| `BACKLOG.md` | Prioritized execution backlog, freeze list, cut list. |

### `research/rbf_sim/` — simulation package

| File | Purpose |
|---|---|
| `generator.py` | Revenue-path generation. **Accounting identities enforced**: `gmv = orders × AOV` exact; returns and fees are deductions. Seasonality, 9 shock types incl. closure. |
| `contracts.py` | FIX-A (matched principal/total/term), FIX-B (amortizing annuity), RBF, RBF-G. Pure arithmetic, no model calls. APR solver. |
| `metrics.py` | Payment burden, high-payment-burden months, duration, total repaid, recovery at checkpoints, incomplete recovery, post-shock recovery, underreporting. |
| `engine.py` | Paired runner — one path, all contracts. Monte Carlo intervals with self-describing labels. |
| `settlement.py` | **Centralized VND settlement policy** (D-024, spec §10.11). Integer-đồng operational layer with a documented ROUND_HALF_UP rule, cap clipping, and both completion concepts. The single home of every monetary constant. |
| `README.md` | Package overview and terminology rules. |
| `tests/test_identities.py` | Accounting-identity tests. Regression guard for the 61%-violation defect. |
| `tests/test_contracts.py` | Contract and metric tests, all expected values hand-derived. |
| `tests/test_derivations.py` | Validates every proposition in `DERIVATIONS.md` against the engine, across adversarial paths (zeros, spikes, seasonal, trending). |
| `tests/test_settlement.py` | Settlement-policy tests: whole-đồng output, the cap invariant, rounding-rule identity, and the mathematical/operational completion split. Mutation-tested. |

### `research/analysis/` — standalone analyses

| File | Purpose |
|---|---|
| `00_audit_evidence.py` | Reproduces the three audit findings: circular AUC, impossible population, engine self-contradiction. |
| `01_verify_spec.py` | **RETIRED — historical only (D-045).** Five checks that `METRIC_DEFINITIONS.md` v0.1 was implementable; produced coherence constraint §3.4. Superseded by `METHODOLOGY_SPEC.md` v1.0 and by `rbf_sim/tests/`, and carries the pre-A-7 `tol=0.5`. Not part of current verification. |

### `research/` — run scripts

| File | Purpose |
|---|---|
| `run_baseline.py` | 10 scenarios × 4 contracts × 500 paths → `results/baseline_v2.json` |
| `run_validation.py` | Sections 1/2/4/5/6 → `results/validation_v1.json` |
| `conv_step.py` | Single-N convergence step (large N split to avoid timeouts) |

### `research/results/` — versioned outputs

| File | Purpose |
|---|---|
| `baseline_v2_canonical.json` | **Current baseline — cite this.** Deterministic and checksummable (D-027): identical code, config and seeds reproduce it **numerically at published precision on every platform tested**, and byte-identically within a fixed runtime (D-041 — 9 last-bit float differences on macOS CPython 3.11.5). SHA-256 `264d319b…ac5a7849`. |
| `baseline_v2_provenance.json` | Execution record for the above — wall-clock, git commit, interpreter/library versions, and the canonical checksum. Expected to differ between runs. |
| `baseline_v2.json` | **Frozen historical evidence.** The pre-canonicalization baseline, `net_sales` remittance basis. Numerically identical to the canonical artifact; retained unmodified and no longer written by `run_baseline.py`. |
| `baseline_v1.json` | Superseded (`gmv` basis). Audit trail. |
| `validation_v1_canonical.json` | **Cite this for validation figures.** Checksummed canonical form (D-038), `f89fd2ba…`. Numerically identical to `validation_v1.json` — all 174 scalars preserved, verified by `test_validation_artifact.py`. |
| `validation_v1_provenance.json` | Execution record for the above, including `original_run_date` (2026-08-04), the one non-deterministic field in the source. |
| `validation_v1.json` | Convergence, pricing, reference-path cost-matched cap (JSON key `pricing.equal_cost`), recovery boundary, RBF-G breakpoint, revenue definition. Retained unmodified as the pre-canonicalization source. |
| `baseline_v2_log.txt` | Full console output of the baseline run. |

### `patches/`

| File | Purpose |
|---|---|
| `README_corrections.patch` | Verified with `git apply --check` against `sellerflow` origin/HEAD. Removes stale deployment link, withdraws 0.92 AUC with the circularity arithmetic, adds research-integrity statement, removes `demo2025` default, de-hardcodes test count. |
| `README.corrected.md` | The resulting README in full, if you prefer to replace rather than patch. |

---

## Reproducing every result

```bash
cd research                       # from the repository root
pip install pytest numpy          # only dependencies

# 1. Simulation suite  (expect: 629 passed)
python3 -m pytest rbf_sim/tests/ -q
#    Backend suite (expect: 401 non-browser tests passed). The suite also
#    contains 9 Playwright browser checks, EXCLUDED from that figure. They
#    PASSED in the earlier browser-capable run recorded at D-036 (browser
#    tests 5 -> 9, no skips). Where Playwright or Chromium is absent they
#    skip, and pytest may report one skipped module or nine skipped cases
#    depending on which of the two is missing — this sandbox reports
#    "401 passed, 9 skipped". Skips are never counted as passes.
python3 -m pytest ../backend/tests -q
#    Reproducibility (byte vs numeric equality, reported separately — D-041)
python3 verify_reproduction.py

# 2. Baseline — 10 scenarios x 4 contracts x 500 paths
#    -> results/baseline_v2_canonical.json   (deterministic; checksum it)
#    -> results/baseline_v2_provenance.json  (execution record)
python3 run_baseline.py

# 3. Validation battery
python3 run_validation.py 2                 # pricing + reference-path cost-matched cap
python3 run_validation.py 4                 # incomplete-recovery boundary
python3 run_validation.py 5                 # RBF-G breakpoint
python3 run_validation.py 6                 # revenue-definition sensitivity

# 4. Monte Carlo convergence (run separately; 10k paths takes ~45s)
python3 conv_step.py 500
python3 conv_step.py 2000
python3 conv_step.py 5000
python3 conv_step.py 10000

# 5. Audit evidence — run from backend/ so its modules are importable
cd ../backend
python3 ../research/analysis/00_audit_evidence.py

# 6. (RETIRED) analysis/01_verify_spec.py is HISTORICAL and is no longer part of
#    current verification (D-045): it checks the superseded METRIC_DEFINITIONS.md
#    v0.1 and carries the pre-A-7 tol=0.5. R-003 already marks its output
#    exploratory and not quotable. Use rbf_sim/tests/ instead.
```

**Determinism.** Base seed `20260803`, bootstrap seed `90210`.

> ~~Identical seeds reproduce bit-for-bit. Any run that does not reproduce is a bug, not variance.~~ **Corrected (D-041).** Identical seeds reproduce **numerically at published precision on every platform tested**. **Byte** equality holds within a fixed runtime, not across runtimes: on Linux/aarch64 CPython 3.10.12 all five canonical artifacts are byte-identical; on macOS CPython 3.11.5, `baseline_v2` differs in **9** last-bit floating-point values and `baseline_equalcost_v1` in **2**. That is IEEE-754 serialization, not variance in the model — but it is not bit-for-bit, and the stronger word was withdrawn rather than defended. Check with `python3 research/verify_reproduction.py`, which reports byte equality and numeric-leaf equality separately and fails only on numeric drift.

### Applying the README patch

**Already applied** in this repository on 2026-08-06; the result was verified byte-identical to `patches/README.corrected.md`. Retained for the audit trail:

```bash
git apply patches/README_corrections.patch
# verified to apply cleanly against origin/HEAD as of 2026-08-03
```

---

## Expected key numbers

Spot-check any reproduction against these:

| Quantity | Value | Source |
|---|---|---|
| Simulation tests passing | 629 (461 inherited + 143 settlement + 25 canonical) | `pytest rbf_sim/tests/ -q` |
| Non-browser tests passing | **1,030 — 401 backend and 629 simulation.** Nine Playwright browser checks are defined and are **excluded from that total**. They **passed in the earlier browser-capable run recorded at D-036** (browser tests 5 → 9, no skips). In environments lacking Playwright or Chromium they skip, and pytest may report one skipped module or nine skipped cases depending on what is installed — the current sandbox reports `401 passed, 9 skipped`. Skips are never counted as passes. Historical composition at the D-028 checkpoint was 71 = 47 inherited + 1 credential guard (D-025) + 8 withdrawn-claim guards (D-026) + 15 model-artifact guards (D-028); the suite has grown since with the claim-integrity guards of D-037…D-045 and the scoring-path disclosure guards of D-047 | `pytest backend/tests/ -q` — runs with **no model artifact**, the clean-checkout state |
| Canonical baseline SHA-256 | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` | `results/baseline_v2_canonical.json` |
| Matched benchmark term / payment | 13 months / 17,076,923 VND | `baseline_v2` |
| Benchmark A implied APR | 37.87% | `baseline_v2` |
| Benchmark B effective APR | 19.5618% | `validation_v1` |
| **Reference-path cost-matched cap `f*`** | **1.0945** (19.5377% APR) | `validation_v1_canonical` |
| Convergence Δ 5,000→10,000 | 0.0027 months, 0.042pp | `validation_v1` |
| Accounting-identity violations | 0 of ~2,400 rows | `test_cohort_wide_identity_holds_for_every_row` |
| Circular-AUC evidence | 0.9098 generating fn vs 0.9182 model | `00_audit_evidence.py` |
| Geometric completion threshold `ρ*` | 11/12 ≈ 0.9167 | `test_P7_geometric_threshold_rho_star_is_one_minus_r_B0_over_FA` |
| P7 completion inequality | **strict** — `ρ > ρ*`; `ρ = ρ*` never completes in finite time | `test_P7_at_rho_star_every_finite_partial_sum_is_strictly_below_the_cap` |
| Operational completion at `ρ*`, `ε`=1.0 / 0.5 / 0.01 | T = 213 / 221 / 266 — **declared-policy sensitivity**, not engine behaviour; engine `ε = 0` since D-024 | `test_P7_operational_completion_flip_point_by_epsilon` |
| Mathematical completion at `ρ*` | never, for any finite T | `test_P7_mathematical_completion_never_occurs_at_rho_star_for_any_epsilon` |
| Tolerance impact on registered results | zero — 0 of 10 scenarios change; verified again post-correction, 1 differing JSON leaf (the run date) | `test_P7_engine_tolerance_is_not_a_binding_settlement_policy` |
| Settlement rounding rule | ROUND_HALF_UP to whole đồng; cap clipped after rounding | `test_to_vnd_is_half_up_not_bankers`, `test_settled_total_never_exceeds_the_cap` |
| Measured worst-case float deviation | 9.2387 × 10⁻⁸ VND over 3,000 paths | D-024 |

---

## Status

**Complete:** Phase 0 audit · frozen methodology · corrected generator · simulation package · baseline · validation battery · corrected claims · README patch · **analytical backbone (7 propositions, test-validated)** · **repository integration and centralized VND settlement policy (D-024)**.

**Also complete since this line was last accurate:** product integration — the Simulation Lab (`frontend/lab.html` + `backend/lab.py`) renders every figure from the canonical artifacts and merged to `main` in PR #2; the centralized monetary policy (`backend/money.py`, D-030); the closure baselines (D-032); `validation_v1` canonicalization (D-038); and the claim ledger with its enforcement tests (D-037…D-041).

**Publication phase — complete as of 2026-08-20, on branch `publication-final`:**

| Deliverable | State |
|---|---|
| Literature matrix | `research/publication/LITERATURE_MATRIX.md` — 44 verified sources, 6 evidence gaps stated |
| Paper outline | `research/publication/PAPER_OUTLINE.md` — every figure mapped to a ledger ID |
| Manuscript | `research/publication/MANUSCRIPT.md`, ~8,400 words, 15 sections + Appendix A |
| Manuscript PDF | `research/publication/MANUSCRIPT.pdf`, 17 pages. Built by `build_pdf.sh`; gated by `check_pdf_bounds.py` at zero text outside the media box |
| Deck | `research/publication/RBF_DECK.pptx`, 13 slides with speaker notes. Built by `build_deck.js` |
| Career package | `research/publication/CAREER_PACKAGE.md` |
| Poster | **not started** — no longer planned; the deck supersedes it |
| Deployment | live demonstration at `sellerflow-production.up.railway.app`. It holds no capital and makes no credit decisions. The deploy in production predates this branch, so the corrections on `publication-final` are **not yet deployed** |

**Gate:** the publication phase was gated on the Gate A claim audit, which passed
at `af2fc2d` and is frozen. `publication-final` is unpushed at the time of
writing; the branch is five-plus commits ahead of `origin/main`.

**Not in this project:** Excel. Removed entirely per instruction 2026-08-03 — no dependency, assumption, deliverable, blocker, or reconciliation task remains.
