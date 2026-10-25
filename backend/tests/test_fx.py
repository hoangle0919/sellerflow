"""FX adapter — mocked throughout. No test here depends on today's live rate.

One test (`test_live_smoke`) touches the network and is skipped unless
RBF_FX_LIVE=1. It demonstrates connectivity only. It is never a correctness
oracle: a provider outage must not turn this suite red.
"""
import json
import threading
import urllib.error
from datetime import date, datetime, timedelta, timezone

import pytest

import fx


_UNSET = object()


def _doc(rate=25807, ref=_UNSET, base="USD", quote="VND"):
    # NOT `ref or today`: that collapses "" (a malformed date we must reject)
    # into a valid one, which silently defeated the malformed-date test.
    return [{"date": fx._utc_today().isoformat() if ref is _UNSET else ref,
             "base": base, "quote": quote, "rate": rate}]


class _Resp:
    def __init__(self, payload): self._b = json.dumps(payload).encode()
    def read(self, n=-1): return self._b[:n] if n and n > 0 else self._b
    def __enter__(self): return self
    def __exit__(self, *a): return False


@pytest.fixture(autouse=True)
def _clean():
    fx._reset_for_tests()
    yield
    fx._reset_for_tests()


def _patch(monkeypatch, payload=None, exc=None):
    def fake(req, timeout=None, context=None):
        if exc is not None:
            raise exc
        return _Resp(payload)
    monkeypatch.setattr(fx.urllib.request, "urlopen", fake)


# ── orientation and arithmetic ───────────────────────────────────────────────

def test_orientation_is_vnd_per_usd():
    # 1 USD = 25,000 VND  =>  250,000,000 VND is 10,000 USD, not 6.25e12
    assert fx.approximate_usd(250_000_000, "25000") == "10000.00"


def test_rounds_to_cents_half_up_at_presentation_only():
    assert fx.approximate_usd(1, "8") == "0.13"          # 0.125 -> 0.13
    assert fx.approximate_usd(0, "25000") == "0.00"


def test_zero_and_large_amounts():
    assert fx.approximate_usd(0, "25807") == "0.00"
    assert fx.approximate_usd(10**13, "25000").endswith(".00")


@pytest.mark.parametrize("bad", ["0", "-5", "abc", "NaN", "Infinity", ""])
def test_unusable_rate_yields_none_not_a_guess(bad):
    assert fx.approximate_usd(1_000_000, bad) is None


# ── validation ───────────────────────────────────────────────────────────────

def test_wrong_pair_rejected(monkeypatch):
    _patch(monkeypatch, _doc(base="EUR"))
    assert fx.get_quote()["error"] == fx.ERR_BAD_RATE


def test_missing_vnd_quote_rejected(monkeypatch):
    _patch(monkeypatch, _doc(quote="THB"))
    assert fx.get_quote()["error"] == fx.ERR_BAD_RATE


def test_inverted_orientation_is_rejected_not_silently_inverted(monkeypatch):
    # 1/25807 would "work" arithmetically and be wrong by 9 orders of magnitude
    _patch(monkeypatch, _doc(rate=0.0000387))
    q = fx.get_quote()
    assert q["status"] == fx.STATUS_UNAVAILABLE
    assert q["error"] == fx.ERR_BAD_RATE


@pytest.mark.parametrize("bad", [0, -1, "nope", None, True])
def test_malformed_rate_rejected(monkeypatch, bad):
    _patch(monkeypatch, _doc(rate=bad))
    assert fx.get_quote()["status"] == fx.STATUS_UNAVAILABLE


def test_future_reference_date_rejected(monkeypatch):
    future = (fx._utc_today() + timedelta(days=2)).isoformat()
    _patch(monkeypatch, _doc(ref=future))
    assert fx.get_quote()["error"] == fx.ERR_BAD_DATE


@pytest.mark.parametrize("bad", ["2026-13-01", "not-a-date", "", 20261024])
def test_malformed_date_rejected(monkeypatch, bad):
    _patch(monkeypatch, _doc(ref=bad))
    assert fx.get_quote()["error"] == fx.ERR_BAD_DATE


def test_oversized_response_rejected(monkeypatch):
    class Big:
        def read(self, n=-1): return b"x" * (fx.MAX_BYTES + 1)
        def __enter__(self): return self
        def __exit__(self, *a): return False
    monkeypatch.setattr(fx.urllib.request, "urlopen", lambda r, timeout=None, context=None: Big())
    assert fx.get_quote()["error"] == fx.ERR_BAD_RESPONSE


def test_multi_record_response_rejected(monkeypatch):
    _patch(monkeypatch, _doc() + _doc())
    assert fx.get_quote()["error"] == fx.ERR_BAD_RESPONSE


# ── freshness bands ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("age,expected", [
    (0, fx.STATUS_OK), (3, fx.STATUS_OK),          # inside the weekend-gap band
    (4, fx.STATUS_STALE), (7, fx.STATUS_STALE),    # shown, but warned
    (8, fx.STATUS_UNAVAILABLE),                    # suppressed
])
def test_reference_age_boundaries(monkeypatch, age, expected):
    ref = (fx._utc_today() - timedelta(days=age)).isoformat()
    _patch(monkeypatch, _doc(ref=ref))
    q = fx.get_quote()
    assert q["status"] == expected
    if expected == fx.STATUS_UNAVAILABLE:
        assert q["vnd_per_usd"] is None
    else:
        assert q["reference_age_days"] == age
        assert q["reference_date"] == ref


# ── transport failures ───────────────────────────────────────────────────────

@pytest.mark.parametrize("exc", [
    urllib.error.URLError("down"),
    urllib.error.HTTPError("u", 429, "rate limited", {}, None),
    urllib.error.HTTPError("u", 503, "unavailable", {}, None),
    TimeoutError("slow"),
    OSError("socket"),
])
def test_transport_failure_is_a_safe_code_not_an_exception(monkeypatch, exc):
    _patch(monkeypatch, exc=exc)
    q = fx.get_quote()
    assert q["status"] == fx.STATUS_UNAVAILABLE
    assert q["error"] == fx.ERR_UNREACHABLE
    # no upstream status code or internal text leaks to the browser
    assert "503" not in json.dumps(q) and "429" not in json.dumps(q)


def test_no_fallback_constant_is_ever_synthesized(monkeypatch):
    _patch(monkeypatch, exc=urllib.error.URLError("down"))
    assert fx.get_quote()["vnd_per_usd"] is None


# ── cache, failed refresh, recovery ──────────────────────────────────────────

def test_cache_avoids_a_second_fetch(monkeypatch):
    calls = []
    monkeypatch.setattr(fx.urllib.request, "urlopen",
                        lambda r, timeout=None, context=None: (calls.append(1), _Resp(_doc()))[1])
    fx.get_quote(); fx.get_quote(); fx.get_quote()
    assert len(calls) == 1


def test_expired_cache_refetches(monkeypatch):
    calls = []
    monkeypatch.setattr(fx.urllib.request, "urlopen",
                        lambda r, timeout=None, context=None: (calls.append(1), _Resp(_doc()))[1])
    fx.get_quote()
    fx._cache_fetched_at -= (fx.CACHE_TTL_S + 1)
    fx.get_quote()
    assert len(calls) == 2


def test_failed_refresh_serves_cache_and_says_so_without_rewriting_fetched_at(monkeypatch):
    _patch(monkeypatch, _doc())
    first = fx.get_quote()
    assert first["refresh_failed"] is False

    # Age the cache past its TTL so the next call attempts a real refresh.
    fx._cache_fetched_at -= (fx.CACHE_TTL_S + 1)
    aged_at = datetime.fromtimestamp(fx._cache_fetched_at, timezone.utc) \
                      .isoformat(timespec="seconds")

    _patch(monkeypatch, exc=urllib.error.URLError("down"))
    second = fx.get_quote()

    assert second["status"] in (fx.STATUS_OK, fx.STATUS_STALE)
    assert second["refresh_failed"] is True
    assert second["error"] == fx.ERR_UNREACHABLE
    assert second["vnd_per_usd"] == first["vnd_per_usd"]
    # A refetch of an old observation is NOT a newly dated rate: the failed
    # refresh must report the ORIGINAL fetch time, not "now".
    assert second["fetched_at"] == aged_at
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    assert second["fetched_at"] < now_iso


def test_service_recovery_clears_the_failed_flag(monkeypatch):
    _patch(monkeypatch, exc=urllib.error.URLError("down"))
    assert fx.get_quote()["status"] == fx.STATUS_UNAVAILABLE
    _patch(monkeypatch, _doc())
    good = fx.get_quote()
    assert good["status"] == fx.STATUS_OK and good["refresh_failed"] is False


def test_concurrent_refreshes_are_deduplicated(monkeypatch):
    calls = []
    def slow(req, timeout=None, context=None):
        calls.append(1)
        import time as _t; _t.sleep(0.05)
        return _Resp(_doc())
    monkeypatch.setattr(fx.urllib.request, "urlopen", slow)
    ts = [threading.Thread(target=fx.get_quote) for _ in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    assert len(calls) == 1


def test_reference_date_and_fetch_time_are_distinct_fields(monkeypatch):
    ref = (fx._utc_today() - timedelta(days=2)).isoformat()
    _patch(monkeypatch, _doc(ref=ref))
    q = fx.get_quote()
    assert q["reference_date"] == ref
    assert q["fetched_at"].startswith(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    assert q["reference_date"] != q["fetched_at"][:10]


# ── the boundary that matters most ───────────────────────────────────────────

def test_fx_is_not_imported_by_calculation_modules():
    """A network value must not be reachable from a settlement path.

    Checked by source inspection rather than sys.modules, because an import
    added inside a function would not show up in a fresh-import check.
    """
    import os, re
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo = os.path.dirname(here)
    targets = [os.path.join(here, "money.py"),
               os.path.join(here, "financing_engine.py"),
               os.path.join(here, "lab.py")]
    for rel in ("generator.py", "contracts.py", "engine.py", "metrics.py", "settlement.py"):
        targets.append(os.path.join(repo, "research", "rbf_sim", rel))
    pat = re.compile(r"^\s*(import\s+fx\b|from\s+fx\s+import|from\s+\.\s*fx\s+import)", re.M)
    for t in targets:
        if os.path.exists(t):
            assert not pat.search(open(t, encoding="utf-8").read()), \
                f"{os.path.relpath(t, repo)} imports fx — a rate must never reach contract arithmetic"


@pytest.mark.skipif(not __import__("os").environ.get("RBF_FX_LIVE"),
                    reason="live provider smoke test; set RBF_FX_LIVE=1 to run")
def test_live_smoke():
    """Connectivity demonstration only. Never an oracle for correctness."""
    q = fx.get_quote(force=True)
    assert q["status"] in (fx.STATUS_OK, fx.STATUS_STALE, fx.STATUS_UNAVAILABLE)
