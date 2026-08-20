#!/usr/bin/env bash
# Deploy entrypoint. Replaces the inline startCommand that read:
#
#   cd backend && python train_model.py --skip-if-exists 2>/dev/null; python -m uvicorn ...
#
# Two defects there. `2>/dev/null` discarded the only evidence of why training
# failed, and the `;` meant the service started regardless -- so a failure was
# both invisible and indistinguishable from success. The live demo ran on the
# heuristic fallback for an unknown period and nothing in the logs said so.
#
# The fallback itself is intentional and supported (see ENVIRONMENT.md §3).
# What follows makes entering it a decision with a record, not an accident.
#
# Note the absence of `set -e`: a training failure must NOT abort the deploy.
# That is the deliberate part.

set -uo pipefail

cd "$(dirname "$0")"

echo "[startup] Building model artifact (train_model.py --skip-if-exists)..."

# stderr is deliberately NOT redirected. Whatever fails here belongs in the logs.
if python train_model.py --skip-if-exists; then
  echo "[startup] Model artifact present. ml_engine will load and smoke-test it;"
  echo "[startup] if the smoke test fails it falls back and says so."
else
  rc=$?
  echo "[startup] ============================================================"
  echo "[startup] WARNING: model training FAILED (exit ${rc})."
  echo "[startup] Continuing deliberately into the deterministic heuristic path."
  echo "[startup]"
  echo "[startup] This is a supported fallback, not a crash. But it is NOT"
  echo "[startup] output-neutral. The active scoring path sets pd_score, which"
  echo "[startup] selects the risk tier, which sets the advance percentage, the"
  echo "[startup] remittance rate, the cap factor, and whether financing is"
  echo "[startup] offered at all. Displayed figures can differ between paths."
  echo "[startup]"
  echo "[startup] Diagnose with: GET /api/health -> scoring_path, sklearn_runtime."
  echo "[startup] A null sklearn_runtime means scikit-learn is absent from the"
  echo "[startup] image: the service does not import it at request time, so it"
  echo "[startup] boots cleanly while training cannot run at all."
  echo "[startup] ============================================================"
fi

exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
