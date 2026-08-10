# RBF Research — Manifest

**Project:** Revenue-Contingent Financing Under Volatile Sales — A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers

> ✅ **This repository is the source of truth.** The research lives at `research/` in the `sellerflow` repository (`https://github.com/hoangle0919/sellerflow.git`), integrated from bundle v5 on 2026-08-06. The earlier bundle copies — including the one that sat inside an unrelated Excel research folder because it was the only writable location at the time — are **historical backups only**. They are not authoritative and must not be edited, read from, or depended upon. Nothing in this project depends on, reads, or relates to any Excel file.

**Created:** 2026-08-03 · **Integrated into this repository:** 2026-08-06 (from bundle v5, SHA-256 `6b86194a…f606811`, verified at integration) · **Spec:** `METHODOLOGY_SPEC.md` v1.0 + amendments A-1…A-7

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
| `RESULTS_REGISTRY.md` | Every result with scenario, parameters, code, interpretation, limitation, and public-safety classification. Includes both preserved null results (R-013). |
| `CORRECTED_CLAIMS.md` | **Current claim set.** Corrected interpretation layer, pricing sensitivity, equal-effective-cost cap, convergence, recovery boundary, RBF-G decision, revenue definition, parameter classification. |
| `DERIVATIONS.md` | **Analytical backbone.** Seven propositions with proofs, holding for any revenue path independent of simulation or parameters. Includes the five-class claim taxonomy and the rejected RBF-G design. |
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
| `01_verify_spec.py` | Five checks that the frozen spec is implementable. Produced coherence constraint §3.4. |

### `research/` — run scripts

| File | Purpose |
|---|---|
| `run_baseline.py` | 10 scenarios × 4 contracts × 500 paths → `results/baseline_v2.json` |
| `run_validation.py` | Sections 1/2/4/5/6 → `results/validation_v1.json` |
| `conv_step.py` | Single-N convergence step (large N split to avoid timeouts) |

### `research/results/` — versioned outputs

| File | Purpose |
|---|---|
| `baseline_v2_canonical.json` | **Current baseline — cite this.** Deterministic and checksummable (D-027): identical code, config and seeds produce byte-identical output. SHA-256 `264d319b…ac5a7849`. |
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

# 1. Test suite  (expect: 629 passed)
python3 -m pytest rbf_sim/tests/ -q

# 2. Baseline — 10 scenarios x 4 contracts x 500 paths
#    -> results/baseline_v2_canonical.json   (deterministic; checksum it)
#    -> results/baseline_v2_provenance.json  (execution record)
python3 run_baseline.py

# 3. Validation battery
python3 run_validation.py 2                 # pricing + equal-effective-cost cap
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

# 6. Spec verification (standalone, no dependencies)
cd ../research && python3 analysis/01_verify_spec.py
```

**Determinism.** Base seed `20260803`, bootstrap seed `90210`. Identical seeds reproduce bit-for-bit. Any run that does not reproduce is a bug, not variance.

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
| Backend tests passing | 71 (47 inherited + 1 credential guard D-025 + 8 withdrawn-claim guards D-026 + 15 model-artifact guards D-028) | `pytest backend/tests/ -q` — runs with **no model artifact**, the clean-checkout state |
| Canonical baseline SHA-256 | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` | `results/baseline_v2_canonical.json` |
| Matched benchmark term / payment | 13 months / 17,076,923 VND | `baseline_v2` |
| Benchmark A implied APR | 37.87% | `baseline_v2` |
| Benchmark B effective APR | 19.5618% | `validation_v1` |
| **Equal-effective-cost cap `f*`** | **1.0945** (19.5377% APR) | `validation_v1` |
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

**Not started:** product integration · paper · poster · deck · deployment.

**Gate:** product integration begins only after the baseline commit is approved.

**Not in this project:** Excel. Removed entirely per instruction 2026-08-03 — no dependency, assumption, deliverable, blocker, or reconciliation task remains.
