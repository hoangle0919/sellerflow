# Native macOS verification — commit `68b8c3d`

Sanitized record. Usernames, absolute paths, credentials and device identifiers
are excluded by policy; see `evidence/README.md`.

**Result: PASS.**

> **Addendum, 2026-08-20 (D-047). One statement in this record was later found
> to be wrong, and is left in place because an evidence record that gets edited
> after the fact cannot be relied on.** The closing note below says "Nothing
> downstream of the risk score depends on the model". The risk **tier** does:
> the score is thresholded into Low / Medium / High Risk, and the tier sets the
> advance percentage, remittance rate, cap factor and whether financing is
> offered at all. The correct statement is that the financing formulas are
> deterministic *once a risk tier is supplied*, while the active scoring path
> can change that tier and therefore the displayed figures. Everything else in
> this record — the pinned-environment verification it exists to document — is
> unaffected. `verify_native_macos.sh` no longer emits the old wording.

## What this closes

The pre-UI hardening gate ran in a Linux sandbox on Python 3.10, where
scikit-learn ≥ 1.8 **cannot be installed at all** (`Requires-Python >=3.11`).
The pinned dependency set in `backend/requirements.txt` was therefore declared
but never installed, and `backend/ENVIRONMENT.md` recorded that gap explicitly
rather than implying the pins had been tested. This run installs them on the
supported interpreter and closes it.

## Environment

| | |
|---|---|
| Commit tested | `68b8c3da421bbe035235c14d759e7cea35491694` (`68b8c3d`) |
| Branch | `hardening-pre-ui` |
| Verification date | 2026-08-07 (UTC) |
| Operating system | macOS 26.0 (Darwin 25.0.0) |
| Architecture | arm64 (Apple silicon) |
| Python | 3.11.5 |
| Environment location | virtualenv inside the external-SSD working copy |

## Resolved dependency versions

```
scikit-learn   1.9.0
numpy          2.4.6
pandas         2.3.3
joblib         1.5.3
fastapi        0.111.0
pydantic       2.13.4
uvicorn        0.29.0
```

All resolved inside the bounds declared in `backend/requirements.txt`
(`scikit-learn>=1.9.0,<1.10`, `numpy>=1.24.1,<3`, `pandas>=2.0.0,<3`,
`joblib>=1.4.0,<2`). The pins install cleanly on Python 3.11.

## Test evidence

| Suite | Result |
|---|---|
| Backend (`backend/tests/`) | **196 passed**, 0 failed, 0 xfailed |
| Simulation (`research/rbf_sim/tests/`) | **629 passed**, 0 failed |

Counts are identical to those observed in the Linux sandbox, so no failure was
masked by the earlier environment. The backend suite runs in clean-checkout
state: `conftest.py` redirects the model directory to an empty temporary path,
so the suite never loads a locally-built model artifact regardless of what is
present on disk.

## Canonical artifact

> ## ⚠️ THIS SECTION WAS WRONG AND IS WITHDRAWN (D-041)
>
> **The step labelled "recomputed" below did not recompute anything.** It read
> the committed `baseline_v2_canonical.json` and hashed it. Hashing a file
> against its own recorded checksum tests that the file has not been corrupted
> on disk. It does not test reproducibility, and it cannot fail for any reason
> connected to determinism. The conclusion drawn from it — "reproduces
> byte-for-byte on macOS/arm64… determinism is therefore not an artifact of one
> platform" — **was not supported by the evidence presented, and is false.**
>
> **What an actual regeneration on macOS / CPython 3.11.5 found:**
>
> | Artifact | Bytes | Numeric leaves |
> |---|---|---|
> | `baseline_v2_canonical.json` | **9 last-bit float differences** | equal at published precision |
> | `baseline_equalcost_v1_canonical.json` | **2 last-bit float differences** | equal at published precision |
> | `baseline_closure_v1_canonical.json` | byte-identical | equal |
> | `baseline_closure_equalcost_v1_canonical.json` | byte-identical | equal |
> | `validation_v1_canonical.json` | byte-identical | equal |
>
> The correct claim is therefore: **all five artifacts reproduce numerically at
> published precision; three of five reproduce byte-for-byte in the tested
> macOS environment, and all five do on Linux/aarch64 CPython 3.10.12.** Byte
> equality across platforms is **not** established and must not be claimed.
>
> The artifacts were **not** regenerated to force matching hashes. Doing so
> would overwrite the evidence instead of verifying it. Use
> `research/verify_reproduction.py`, which regenerates into a scratch tree and
> reports byte equality and numeric-leaf equality as separate columns.

The original text is preserved below for the audit trail.

```
recomputed  264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849
provenance  264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849
expected    264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849
```

~~`research/results/baseline_v2_canonical.json` reproduces **byte-for-byte** on
macOS/arm64, matching the checksum recorded in `RESULTS_REGISTRY.md` and in the
artifact's own provenance sidecar. Determinism is therefore not an artifact of
one platform.~~

## Production startup

| Endpoint | Result |
|---|---|
| `/api/health` | HTTP 200, `status: operational` |
| `/` | HTTP 200 |
| `/api/docs` | HTTP 200 |

```json
{"status":"operational","version":"1.0.0",
 "model":"RF+LR ensemble v1.0 (synthetic baseline, unvalidated)",
 "scoring_path":"ensemble","sellers_assessed":35,"waitlist_count":0,
 "avg_response_ms":1200,"alerts_configured":false}
```

## Ensemble acceptance path exercised

`scoring_path: "ensemble"` — this run loaded a real model artifact, so the
**acceptance** path was exercised, not only the fallback. That is a stronger
result than the sandbox produced, where no artifact existed and only the
rejection paths ran. Both directions of the D-028 load check are now covered on
the supported environment: an artifact built by the matching scikit-learn passes
the load-time smoke test and is accepted; absent, unreadable and
loads-but-cannot-predict artifacts are each classified and fall back to the
deterministic heuristic.

> **The ensemble is synthetic and unvalidated.** It is a secondary demonstration
> component with **no measured predictive validity**. Its training benchmark
> (0.92 AUC) was withdrawn as circular — the labels were generated by a
> hand-written function of the same features the model consumed (D-026), and
> `GET /api/model/status` reports `auc: null` with
> `validation_status: "withdrawn"`. `sellers_assessed: 35` above is seeded demo
> data, not real merchants. Nothing downstream of the risk score depends on the
> model: the advance, remittance, cap, scenarios and risk findings are
> deterministic arithmetic, and the service is fully functional with no model
> artifact present.

## Environment isolation

- The virtualenv, pip cache and bytecode cache were created **inside the
  external-SSD working copy**, never on the internal disk.
- No `sudo` was used at any point.
- No tracked file was modified by the run; the working tree was clean
  afterwards.

## Reproducing

```bash
./verify_native_macos.sh
```

Requires Python ≥ 3.11 on the host. The script locates an interpreter, builds
the virtualenv beside the repository, installs the pinned set, runs both suites,
re-checks the canonical checksum, starts the service, and writes a sanitized
report. It exits non-zero on any failure.
