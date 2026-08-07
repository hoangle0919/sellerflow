import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Isolate the whole test run from the real database: point DATABASE_URL at a
# throwaway file BEFORE database.py is imported (it reads the path at import
# time). Route tests then run against a fresh, seeded temp DB and never touch
# data/sellerflow.db.
_test_db = os.path.join(tempfile.gettempdir(), "rbf_test.db")
for _p in (_test_db, _test_db + "-wal", _test_db + "-shm"):
    try:
        os.remove(_p)
    except OSError:
        pass
os.environ["DATABASE_URL"] = _test_db

# main.py reads DASHBOARD_PASSWORD at import time and has no default, so the
# suite must supply its own. Defined here rather than hard-coded in the tests so
# there is exactly one place a password literal appears.
TEST_DASHBOARD_PASSWORD = "test-dashboard-password"
os.environ["DASHBOARD_PASSWORD"] = TEST_DASHBOARD_PASSWORD

# D-028: point the model directory at an empty temp dir BEFORE ml_engine is
# imported. The suite must never load a developer's untracked `.pkl` — those are
# gitignored, are built by whatever scikit-learn happened to be installed, and
# made the suite pass or fail depending on whose machine it ran on. Tests
# therefore exercise the deterministic heuristic path by default, which is also
# the state of a clean checkout. Tests that need a real ensemble build a
# throwaway fixture themselves (see test_model_artifacts.py).
_empty_models = os.path.join(tempfile.gettempdir(), "rbf_test_models_empty")
os.makedirs(_empty_models, exist_ok=True)
os.environ["RBF_MODEL_DIR"] = _empty_models
