Integrates the audited simulation research foundation and four hardening corrections. Seven commits, `42b7b1e` → `ae78bfc`. Verified natively on macOS/arm64 with Python 3.11.5.

`research-foundation` does not need merging separately — `42b7b1e` is the first commit in this branch.

---

## 1. Simulation research foundation

Integrates research bundle v5 (SHA-256 `6b86194a…f606811`, verified at integration) into `research/`: a frozen methodology spec, seven proved propositions in `DERIVATIONS.md`, a simulation package with accounting identities enforced by test, an append-only decision log, and a results registry. This repository is now the source of truth; earlier bundle copies are historical backups.

The quantitative contribution is a **deterministic, line-by-line-verifiable comparison of fixed-payment and revenue-based financing** — not default prediction. It needs no labels.

## 2. Circular AUC withdrawal

The previously reported 0.92 AUC is withdrawn. `generate_data.py` built the `defaulted` label by evaluating a hand-written weighted formula over **the same ten features the model consumed**, so the model was scored on rediscovering a formula written 60 lines away. Measured: the generating function scores **0.9098** against its own label versus the model's **0.9182** — the figure measured the chosen noise variance, not skill.

`GET /api/model/status` now returns `auc: null`, `validation_status: "withdrawn"`, `reason: "synthetic circular-label benchmark"`. Purged from the API, the demo script, the UI and the README. The key is nulled rather than deleted — an absent field reads as "not built yet", not "retracted".

Deliberately **not** withdrawn: the UCI cross-validation (0.80 German Credit, 0.77 Taiwan default) on real borrowers with real adjudicated outcomes. Different claim, asserted by test so a future over-broad purge can't take it.

Enforced by `backend/tests/test_no_withdrawn_claims.py`, a source scanner over every shipped surface that fails on any unexplained `0.92` and requires each permitted occurrence to carry a written reason.

## 3. Deterministic canonical artifacts

`baseline_v2.json` embedded `date.today()`: every quantity reproduced bit-for-bit, but the *file* did not, so it could not be cited by checksum.

Split into `baseline_v2_canonical.json` (result + deterministic identity: schema version, spec version, generator fingerprint, scenario-config hash) and `baseline_v2_provenance.json` (wall-clock, git commit, interpreter/library versions, and the canonical checksum). The original is **preserved unmodified** as historical evidence and is no longer written by `run_baseline.py`; a test asserts it still agrees with the canonical artifact on every number.

Canonical SHA-256 `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849`, reproduced byte-for-byte on both Linux and macOS.

`source_commit` lives in provenance, not canonical: committing the artifact changes `HEAD`, which changes what the next run emits, so it could never be both committed and reproducible. Code identity is captured by a hash of the generating source instead.

## 4. Reproducible environment

Model artifacts are never committed (`*.pkl` is gitignored); production trains its own at deploy. The test suite nonetheless loaded whatever `.pkl` was on the developer's disk, so it passed or failed depending on whose machine ran it.

`load_models()` guarded only `joblib.load`. A pickle from a different scikit-learn **unpickles successfully and raises at first use**, so the guard caught the easy failure and missed the dangerous one — which took down the entire test suite at collection. Every artifact is now smoke-tested against a fixed feature row at load, and failure is classified: `artifacts_absent` / `artifact_unreadable` / `artifact_incompatible`.

`scikit-learn>=1.4.0` had no ceiling — exactly what lets a build/consume mismatch appear silently. Now bounded, with Python ≥ 3.11 documented in `backend/ENVIRONMENT.md`.

## 5. Integer-VND ROUND_HALF_UP policy

`financing_engine` computed contractual money with binary floats and Python's `round()` — **banker's** rounding, ties to even — while the documented settlement policy is **ROUND_HALF_UP** on integer đồng. Deterministic divergence at ties, reachable at ~1 in 10,000 whole-VND revenues.

| | revenue 2,500 | revenue 100,002,500 |
|---|---|---|
| advance | 4,000 → **5,000** | 180,004,000 → **180,005,000** |
| cap | 4,600 → **5,750** | 207,004,600 → **207,005,750** |
| type | `float` → **`int`** | `float` → **`int`** |

`backend/money.py` holds the product policy in a fixed order: raw advance (Decimal, built from strings) → ROUND_HALF_UP to the 1,000 VND increment → cap from the **rounded** advance → ROUND_HALF_UP to whole đồng → quantize candidate payment → clip to the remaining balance. Rounding before clipping is what makes "cumulative never exceeds the cap" unconditional.

Production does **not** import the research package; the rule is shared, the implementations are separate, and seven cross-layer parity fixtures keep them from drifting.

**A correction to an earlier claim in this branch's own history:** a gate report asserted the engine over-collected by up to 5.77% of the cap. That was wrong — it computed the total as `duration × remittance`, assuming every payment is full-size. Across 6,794 structures the settled total **never** exceeds the cap. The wrong claim, its correction and the evidence are all retained in `DECISION_LOG.md` (D-029, D-030).

## 6. Final-payment disclosure

The API emitted `(cap, remittance, duration)` with no indication the final payment is partial — which is precisely what produced the error above. Every structure and scenario row now carries `illustrative_schedule`: full-payment count and amount, the partial final payment, completion month, total contractual repayment, and explicit statements that the projection **holds revenue constant** and is **not a guaranteed payment or duration**.

## 7. Native macOS verification

macOS 26.0 / arm64, Python 3.11.5, commit `68b8c3d`. Resolved: scikit-learn 1.9.0, numpy 2.4.6, pandas 2.3.3, joblib 1.5.3 — all inside the declared bounds. Both suites pass with counts identical to Linux, so nothing was masked. Canonical checksum reproduces byte-for-byte. `/api/health` 200. The run exercised the **ensemble acceptance** path, complementing the sandbox which only exercised rejection.

Evidence committed at `evidence/2026-08-07-native-macos-verification.md`, sanitized — no usernames, absolute paths, credentials, tokens, device serials or host names. `verify_native_macos.sh` reproduces it and emits sanitized output by default.

## 8. Research and product limitations

- **All quantitative output is simulation under modeled assumptions.** No observed seller revenue, repayment or default outcome exists in this project.
- **The underwriting ensemble is a secondary, explicitly unvalidated component** with no measured predictive validity. Nothing downstream of the risk score depends on it; the service is fully functional with no model artifact.
- **No causal claim, no significance test.** Intervals are Monte Carlo intervals over simulated paths — they measure whether enough paths were run, not population uncertainty about real sellers.
- **No contract parameter is externally sourced.** All are illustrative or derived, with sensitivity analysis rather than claimed calibration.
- **Null and unfavourable results are retained**, including a guardrail design (RBF-G) that provably never activates — preserved as a rejected design, and excluded from public comparisons.
- **Not a lending service, credit offer, or financial advice.** Seeded dashboard data is labelled demo data.
- **Known open items:** `docs/` remains gitignored; the illustrative `1.20×` cap is not a recommendation; `validation_v1.json` is not yet canonicalized (recorded in D-027).

## 9. Test evidence

| Suite | Before | After |
|---|---|---|
| Backend | 47 | **196** |
| Simulation | — | **629** |

Both green from a clean clone and natively on macOS. The 461 inherited simulation tests pass unchanged **including with the cap tolerance tightened by 10⁶**, which is direct evidence the old tolerance was never load-bearing.

New suites were **mutation-tested**, not merely observed green. Deliberate defects — clipping before rounding, `ROUND_DOWN` for half-up, reintroducing a `0.5` default, an epsilon in mathematical completion, removing the cap clip, reinstating the withdrawn AUC, dropping the artifact smoke test, building `Decimal` from a binary float — are each caught. Two mutants initially survived and exposed a genuine gap in coverage; `backend/tests/test_money.py` was added to close it.

## 10. No Excel dependency

Confirmed: no imports, file references, paths, or data dependencies on any Excel project or file. Every remaining mention across the tree is prose recording Excel's **exclusion** (D-014) in the audit trail. No absolute host paths entered the repository.

---

**Do not auto-merge.** Simulation Lab work starts on a fresh `simulation-lab` branch cut from `main` after this merges.
