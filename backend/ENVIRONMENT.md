# Backend environment and model artifacts

Answers the four questions raised at the pre-UI hardening gate (D-028).

## 1. How does production obtain the model?

It trains its own, at deploy time. `railway.toml`:

```
startCommand = "bash backend/start_railway.sh"
```

`train_model.py` builds the ensemble from `generate_data.py` — synthetic data
generated in-process — and writes four `.pkl` files to `backend/models/`.

**Superseded form, and why.** Until 2026-08-20 the start command was inline:

```
cd backend && python train_model.py --skip-if-exists 2>/dev/null; \
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

Both halves were wrong. `2>/dev/null` discarded the only evidence of why
training failed, and the bare `;` started the service regardless — so entering
the fallback was silent and indistinguishable from success. The live demo ran
on the heuristic for an unknown period with nothing in the logs saying so; it
was noticed only because `/api/health` reports `scoring_path`.
`start_railway.sh` keeps the fallback — it is a supported path — but logs the
failure, states the consequence, and continues deliberately rather than through
shell punctuation.

**The fallback is not output-neutral.** `scoring_path` sets `pd_score`, which
selects the risk tier, which sets the advance percentage, the remittance rate,
the cap factor and whether financing is offered at all. A README revision once
claimed the displayed numbers were "identical either way"; that claim is
withdrawn, and `tests/test_scoring_path_disclosure.py` fails if it returns.

**No model artifact is in the repository.** `.gitignore` line 4 excludes `*.pkl`.
A clean checkout has no model, by design. The consequence is that the artifact
is always produced by the same interpreter and scikit-learn that will consume
it, which is the property that matters; a pickle is not a portable format.

## 2. Python and scikit-learn compatibility

| | Version | Status |
|---|---|---|
| Python | **>= 3.11** | Required by scikit-learn >= 1.8 |
| scikit-learn | **>= 1.9.0, < 1.10** | Pinned range |
| numpy / pandas / joblib | bounded ranges | See `requirements.txt` |

**Verification status: VERIFIED** on 2026-08-07, commit `68b8c3d`.

The pinned set was installed and exercised on macOS 26.0 / arm64 with Python
3.11.5. Resolved: scikit-learn 1.9.0, numpy 2.4.6, pandas 2.3.3, joblib 1.5.3 —
all inside the declared bounds. 196 backend and 629 simulation tests passed,
counts identical to the Linux sandbox, so nothing was masked by the earlier
environment. Evidence:
[`evidence/2026-08-07-native-macos-verification.md`](../evidence/2026-08-07-native-macos-verification.md).

Re-verify at any time with `./verify_native_macos.sh` from the repository root.

*Historical note:* the pre-UI hardening gate could not check this. It ran on
Python 3.10, where scikit-learn 1.9 cannot be installed at all
(`Requires-Python >=3.11`), so the pins were declared but untested and that gap
was recorded here rather than glossed over. This entry replaces it.

## 3. What happens when the model is missing or incompatible?

Three classified outcomes. None of them crashes the service, and none of them
misreports which path produced a score.

| Condition | `model_artifact.reason` | Behaviour |
|---|---|---|
| No `.pkl` files | `artifacts_absent` | Deterministic heuristic; informational log naming `train_model.py` |
| Files present, unreadable | `artifact_unreadable` | Heuristic; warning with the exception |
| Files load but cannot predict | `artifact_incompatible` | Heuristic; warning naming the runtime scikit-learn version |

**Why the third case needed its own handling.** A pickle written by a different
scikit-learn frequently *unpickles successfully* and raises only at first use,
because estimator attributes are added or renamed between minor versions.
Guarding `joblib.load` alone catches the easy case and misses the dangerous
one, which then surfaces as a 500 from a request handler — or, as happened
here, as a collection error that took down the entire test suite. Every
artifact is now smoke-tested against a fixed feature row at load time.

`GET /api/model/status` exposes this as `model_artifact`, including
`scoring_path` (`ensemble` or `heuristic`). Every assessment carries the same
signal in its `model_version` and `scoring_path` fields: a heuristic score
reports `heuristic-fallback-v1`, never `v1.0-synthetic`. Reporting the model's
label while the fallback ran would be the same class of defect as the withdrawn
AUC — the artifact contradicting its own description.

## 4. Is the model necessary for the research-integrated product?

**No.** It is a secondary, explicitly unvalidated component whose training
benchmark was withdrawn as circular (D-026).

Everything downstream of the PD estimate — advance, remittance percentage,
repayment cap, scenario durations, risk findings — is plain deterministic
arithmetic in `financing_engine.py`, with no model call in the path. The
research layer (`research/rbf_sim/`) has no dependency on the backend at all
and does not import scikit-learn.

Concretely, with no model artifact present: the API serves, `/api/health`
returns `operational`, assessments are produced via the heuristic, the
financing structure and scenarios are unchanged, and the full backend and
simulation suites pass. Asserted by `tests/test_model_artifacts.py`.

## Rebuilding the model locally

```bash
cd backend
python train_model.py                 # writes backend/models/*.pkl
python train_model.py --skip-if-exists  # no-op if already present
```

To run against a different artifact directory — or to force the heuristic path
without deleting anything:

```bash
RBF_MODEL_DIR=/tmp/empty python -m uvicorn main:app
```

The test suite sets `RBF_MODEL_DIR` to an empty temp directory so it never
depends on a developer's untracked artifacts.
