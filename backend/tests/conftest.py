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
