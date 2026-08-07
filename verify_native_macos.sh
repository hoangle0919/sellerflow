#!/bin/bash
# Native macOS verification — runs the supported environment on the SSD.
#
# Closes the gap left by the hardening gate: that verification ran in a Linux
# sandbox on Python 3.10, where scikit-learn >= 1.8 cannot be installed at all
# (Requires-Python >=3.11). The pinned dependency set has therefore never been
# installed. This script installs it, on the SSD, and reports what resolved.
#
# Guarantees:
#   * no sudo
#   * nothing written to the internal disk — venv, caches and report all live
#     under the SSD repository
#   * no modification to tracked files (.venv and the report are gitignored)
#
# Usage:   cd /Volumes/SellerFlow-RBF/sellerflow && ./verify_native_macos.sh

set -uo pipefail

REPO="/Volumes/SellerFlow-RBF/sellerflow"
VENV="$REPO/.venv"
REPORT="$REPO/NATIVE_VERIFICATION.md"
REQS="$REPO/backend/requirements.txt"
PORT="${PORT:-8123}"

# Keep every cache on the SSD. pip and pytest otherwise write to ~/Library.
export PIP_CACHE_DIR="$REPO/.cache/pip"
export PYTHONPYCACHEPREFIX="$REPO/.cache/pycache"
mkdir -p "$PIP_CACHE_DIR" "$PYTHONPYCACHEPREFIX"

fail=0
say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()  { printf '  \033[32mOK\033[0m   %s\n' "$*"; }
bad() { printf '  \033[31mFAIL\033[0m %s\n' "$*"; fail=1; }

say "0. Location"
cd "$REPO" || { echo "SSD repo not mounted at $REPO"; exit 1; }
echo "  repo   : $(pwd)"
echo "  branch : $(git branch --show-current)"
echo "  HEAD   : $(git rev-parse --short HEAD)"
echo "  reqs   : $REQS"
[ -f "$REQS" ] || { bad "requirements.txt not found"; exit 1; }

say "1. Interpreter — need Python >= 3.11"
PY=""
for c in python3.13 python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1; then
    v=$("$c" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null) || continue
    maj=${v%%.*}; min=${v##*.}
    if [ "$maj" -eq 3 ] && [ "$min" -ge 11 ]; then PY="$c"; break; fi
  fi
done
if [ -z "$PY" ]; then
  bad "no Python >= 3.11 found (tried python3.13/3.12/3.11/python3)"
  echo "       install one, e.g.:  brew install python@3.12"
  echo "       then re-run this script."
  exit 1
fi
echo "  using  : $PY -> $("$PY" --version 2>&1) at $(command -v "$PY")"
ok "interpreter satisfies >= 3.11"

say "2. Virtualenv on the SSD"
[ -d "$VENV" ] && echo "  reusing $VENV" || "$PY" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "  python : $(python --version 2>&1)"
echo "  path   : $(command -v python)"
case "$(command -v python)" in
  "$REPO"/*) ok "venv is on the SSD" ;;
  *)         bad "venv resolved off-SSD: $(command -v python)" ;;
esac

say "3. Install the pinned dependency set"
python -m pip install --upgrade pip -q
if python -m pip install -r "$REQS" -q; then
  ok "pinned requirements installed"
else
  bad "pip install failed — the pins in backend/requirements.txt do not resolve"
fi
python -m pip install -q pytest httpx

say "4. Resolved versions"
python - <<'PY'
import importlib, platform, sys
print(f"  python         {sys.version.split()[0]}  ({platform.platform()})")
for m in ("sklearn","numpy","pandas","joblib","fastapi","pydantic","uvicorn"):
    try:
        mod = importlib.import_module(m)
        print(f"  {m:<14} {getattr(mod,'__version__','?')}")
    except Exception as e:
        print(f"  {m:<14} MISSING ({e.__class__.__name__})")
PY
python - <<'PY'
import sys
try:
    import sklearn
    maj, minor = (int(x) for x in sklearn.__version__.split(".")[:2])
    assert (maj, minor) >= (1, 9), f"expected >=1.9, got {sklearn.__version__}"
    print("  \033[32mOK\033[0m   scikit-learn satisfies the pin")
except Exception as e:
    print(f"  \033[31mFAIL\033[0m {e}"); sys.exit(1)
PY
[ $? -ne 0 ] && fail=1

say "5. Backend tests — clean-checkout state (no model artifact)"
BK_LOG="$REPO/.cache/backend_tests.log"
( cd "$REPO" && python -m pytest backend/tests/ -q -rxX ) > "$BK_LOG" 2>&1
BK_RC=$?
tail -n 12 "$BK_LOG" | sed 's/^/  /'
[ $BK_RC -eq 0 ] && ok "backend suite passed" || bad "backend suite failed (rc=$BK_RC)"

say "6. Simulation suite"
SIM_LOG="$REPO/.cache/sim_tests.log"
( cd "$REPO/research" && python -m pytest rbf_sim/tests/ -q ) > "$SIM_LOG" 2>&1
SIM_RC=$?
tail -n 4 "$SIM_LOG" | sed 's/^/  /'
[ $SIM_RC -eq 0 ] && ok "simulation suite passed" || bad "simulation suite failed (rc=$SIM_RC)"

say "7. Canonical artifact checksum"
( cd "$REPO/research" && python - <<'PY'
import json, sys
sys.path.insert(0, ".")
from rbf_sim.canonical import checksum
b = json.load(open("results/baseline_v2_canonical.json"))
p = json.load(open("results/baseline_v2_provenance.json"))
c = checksum(b)
print(f"  recomputed : {c}")
print(f"  provenance : {p['canonical_sha256']}")
print(f"  expected   : 264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849")
assert c == p["canonical_sha256"], "artifact and provenance disagree"
assert c == "264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849", "checksum drift"
PY
) && ok "canonical checksum reproduces natively" || bad "canonical checksum mismatch on macOS"

say "8. Production startup and /api/health"
HEALTH_JSON="$REPO/.cache/health.json"
( cd "$REPO/backend" && \
  DASHBOARD_PASSWORD=native-verify DATABASE_URL="$REPO/.cache/native_verify.db" \
  python -m uvicorn main:app --host 127.0.0.1 --port "$PORT" > "$REPO/.cache/uvicorn.log" 2>&1 ) &
UV_PID=$!
CODE=""
for _ in $(seq 1 30); do
  sleep 1
  CODE=$(curl -s -o "$HEALTH_JSON" -w '%{http_code}' "http://127.0.0.1:$PORT/api/health" 2>/dev/null) || true
  [ "$CODE" = "200" ] && break
done
echo "  /api/health  -> HTTP ${CODE:-none}"
[ "$CODE" = "200" ] && ok "health check passed" || bad "health check did not return 200"
[ -s "$HEALTH_JSON" ] && python -c "import json;d=json.load(open('$HEALTH_JSON'));print('  status:',d.get('status'));print('  model :',d.get('model'));print('  path  :',d.get('scoring_path'))"
LAND=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" 2>/dev/null || echo none)
DOCS=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/api/docs" 2>/dev/null || echo none)
echo "  /            -> HTTP $LAND"
echo "  /api/docs    -> HTTP $DOCS"
kill "$UV_PID" 2>/dev/null; wait "$UV_PID" 2>/dev/null

say "9. Nothing written to the internal disk"
case "$VENV" in "$REPO"/*) ok "venv under the SSD repo" ;; *) bad "venv off-SSD" ;; esac
case "$PIP_CACHE_DIR" in "$REPO"/*) ok "pip cache under the SSD repo" ;; *) bad "pip cache off-SSD" ;; esac
DIRTY=$(cd "$REPO" && git status --porcelain | grep -vE '^\?\? (\.venv/|\.cache/|NATIVE_VERIFICATION\.md)' | wc -l | tr -d ' ')
[ "$DIRTY" = "0" ] && ok "no tracked file modified" || { bad "tracked files modified:"; (cd "$REPO" && git status --porcelain | head); }

say "10. Writing report"
{
  echo "# Native macOS verification"
  echo
  echo "Generated by \`verify_native_macos.sh\` on the SSD working copy."
  echo "Closes the gap left by the hardening gate, where the pinned dependency"
  echo "set could not be installed (sandbox was Python 3.10; scikit-learn >= 1.8"
  echo "requires >= 3.11)."
  echo
  echo "- **Date:** $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "- **Host:** $(uname -srm)"
  echo "- **Repo:** \`$REPO\`"
  echo "- **Branch:** \`$(git -C "$REPO" branch --show-current)\`"
  echo "- **Commit:** \`$(git -C "$REPO" rev-parse HEAD)\`"
  echo "- **Interpreter:** $(python --version 2>&1) (\`$(command -v python)\`)"
  echo
  echo '## Resolved versions'
  echo
  echo '```'
  python - <<'PY'
import importlib
for m in ("sklearn","numpy","pandas","joblib","fastapi","pydantic","uvicorn"):
    try:
        mod = importlib.import_module(m)
        print(f"{m:<14} {getattr(mod,'__version__','?')}")
    except Exception:
        print(f"{m:<14} MISSING")
PY
  echo '```'
  echo
  echo '## Backend tests (no model artifact)'
  echo
  echo '```'; tail -n 15 "$BK_LOG"; echo '```'
  echo
  echo '## Simulation tests'
  echo
  echo '```'; tail -n 5 "$SIM_LOG"; echo '```'
  echo
  echo '## Production startup'
  echo
  echo "- \`/api/health\` → HTTP ${CODE:-none}"
  echo "- \`/\` → HTTP $LAND"
  echo "- \`/api/docs\` → HTTP $DOCS"
  echo
  if [ -s "$HEALTH_JSON" ]; then echo '```json'; cat "$HEALTH_JSON"; echo; echo '```'; fi
  echo
  echo '## Result'
  echo
  if [ "$fail" -eq 0 ]; then
    echo '**PASS** — the pinned environment installs and the supported stack is verified natively on the SSD.'
  else
    echo '**FAIL** — see the failures above. The pinned environment is NOT verified.'
  fi
} > "$REPORT"

say "Done"
echo "  report: $REPORT"
if [ "$fail" -eq 0 ]; then
  printf '  \033[32mALL CHECKS PASSED\033[0m\n'
else
  printf '  \033[31mSOME CHECKS FAILED — see above\033[0m\n'
fi
exit "$fail"
