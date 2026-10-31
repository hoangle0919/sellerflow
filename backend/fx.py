"""USD reference-rate adapter — display metadata only, never contract arithmetic.

WHAT THIS IS. A small cache in front of one fixed upstream pair (USD base,
VND quote) so the website can show an approximate USD equivalent beside a VND
amount. The USD figure is a present-day reference conversion, not a
US-dollar contract, not a historical FX valuation, not an executable quote.

WHAT THIS IS NOT, AND MUST NOT BECOME. This module is deliberately not imported
by `money`, `financing_engine`, `lab`, `rbf_sim` or any future `evaluation`
package. Every contractual figure stays integer VND and is computed without
reference to an exchange rate. A test asserts the non-import
(`tests/test_fx.py::test_fx_is_not_imported_by_calculation_modules`), because an
import added later would otherwise make a network value reachable from a
settlement path without anything failing.

ORIENTATION, FIXED ONCE. The upstream publishes `rate` as VND per one USD:
    1 USD = R VND   =>   approximate_usd = original_vnd / R
`R` is large (tens of thousands). A response whose rate is below
`MIN_PLAUSIBLE_RATE` is rejected as an orientation error rather than inverted,
because silently inverting a mislabelled response would produce figures that
look reasonable and are wrong by nine orders of magnitude.

FRESHNESS IS PRODUCT POLICY, NOT A PROVIDER GUARANTEE. The upstream documents
daily updates and states no SLA. The bands below are this project's choice
about what it is willing to display, and the provider's reference date is
always shown beside the number.
"""
from __future__ import annotations

import http.client
import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Optional

# ── Fixed upstream. One origin, one pair, no caller-supplied URL ──────────────
FX_ORIGIN = "https://api.frankfurter.dev"
FX_PATH = "/v2/rates?base=USD&quotes=VND"
FX_URL = FX_ORIGIN + FX_PATH
FX_DOC_URL = "https://frankfurter.dev/"
FX_PROVIDER = "Frankfurter"
BASE_CODE = "USD"
QUOTE_CODE = "VND"

#: Blended across providers by the upstream. Labelled as such in the UI: it is
#: not a Vietnamese bank's buy/sell quote and must never be presented as one.
RATE_KIND = "blended_reference"

TIMEOUT_S = 6
MAX_BYTES = 256 * 1024
CACHE_TTL_S = 3600

#: Negative caching. After a failed fetch, do not try again for this long,
#: doubling up to the ceiling. Without it, every request during an upstream
#: outage pays the full TIMEOUT_S before failing, which is how a slow third
#: party turns into an outage of ours.
BACKOFF_BASE_S = 60
BACKOFF_MAX_S = 900

#: A USD/VND rate is ~2.5e4. Anything under this is a wrong pair or an
#: inverted orientation, not a cheap dollar.
MIN_PLAUSIBLE_RATE = Decimal("1000")
MAX_PLAUSIBLE_RATE = Decimal("10000000")

FRESH_MAX_AGE_DAYS = 3      # ordinary weekend/holiday gaps
STALE_MAX_AGE_DAYS = 7      # shown, but only with a conspicuous warning

STATUS_OK = "ok"
STATUS_STALE = "stale"
STATUS_UNAVAILABLE = "unavailable"

ERR_UNREACHABLE = "fx_unreachable"
ERR_BAD_RESPONSE = "fx_bad_response"
ERR_BAD_RATE = "fx_bad_rate"
ERR_BAD_DATE = "fx_bad_date"
ERR_TOO_OLD = "fx_rate_too_old"

#: The lock guards the module's state ONLY. It is never held across the
#: network call. An earlier version did hold it, which meant that during an
#: upstream stall every caller queued behind a TIMEOUT_S fetch; because FastAPI
#: runs sync endpoints in a bounded worker pool, enough queued callers would
#: have starved the whole application, not just this endpoint. A third party
#: being slow must never become an outage here.
_lock = threading.Lock()
_cache: Optional[Dict[str, Any]] = None       # last VALIDATED quote
_cache_fetched_at: float = 0.0
_last_error: Optional[str] = None
_fetching: bool = False                       # single-flight: one refresher
_failed_until: float = 0.0                    # negative-cache deadline
_fail_streak: int = 0


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_payload(raw: bytes) -> Dict[str, Any]:
    """Upstream returns a list of pair records for the /v2/rates form.

    Accepts either a one-element list or a bare object, because tolerating the
    documented shape and its obvious singular variant is cheaper than a hard
    failure on a schema the provider may normalise later. Anything else is a
    bad response, not something to guess at.
    """
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception:
        raise ValueError(ERR_BAD_RESPONSE)
    if isinstance(doc, list):
        if len(doc) != 1:
            raise ValueError(ERR_BAD_RESPONSE)
        doc = doc[0]
    if not isinstance(doc, dict):
        raise ValueError(ERR_BAD_RESPONSE)
    return doc


def _validate(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Reject before trusting. Returns a normalised validated quote."""
    if doc.get("base") != BASE_CODE or doc.get("quote") != QUOTE_CODE:
        raise ValueError(ERR_BAD_RATE)

    raw_rate = doc.get("rate")
    if isinstance(raw_rate, bool) or not isinstance(raw_rate, (int, float, str)):
        raise ValueError(ERR_BAD_RATE)
    try:
        rate = Decimal(str(raw_rate))
    except Exception:
        raise ValueError(ERR_BAD_RATE)
    if not rate.is_finite() or rate <= 0:
        raise ValueError(ERR_BAD_RATE)
    if rate < MIN_PLAUSIBLE_RATE or rate > MAX_PLAUSIBLE_RATE:
        # Orientation or pair error. Do NOT invert — see module docstring.
        raise ValueError(ERR_BAD_RATE)

    raw_date = doc.get("date")
    if not isinstance(raw_date, str):
        raise ValueError(ERR_BAD_DATE)
    try:
        ref = date.fromisoformat(raw_date)
    except ValueError:
        raise ValueError(ERR_BAD_DATE)
    if ref > _utc_today():
        raise ValueError(ERR_BAD_DATE)

    return {"rate": rate, "reference_date": ref.isoformat()}


def _ssl_context() -> Optional[ssl.SSLContext]:
    """Explicit CA bundle.

    The interpreter's default trust store is not always populated on macOS or
    in slim containers, and the failure mode is a bare CERTIFICATE_VERIFY_FAILED
    that looks exactly like the provider being down. This project has already
    lost time to that once, in the operator-alert path; `certifi` is pinned for
    the same reason here. Falling back to the default context keeps a working
    store working rather than hard-failing if certifi is absent.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _fetch() -> Dict[str, Any]:
    req = urllib.request.Request(
        FX_URL,
        headers={"Accept": "application/json",
                 # Some providers sit behind a CDN that rejects the default
                 # Python-urllib agent outright. Send an ordinary one.
                 "User-Agent": "Mozilla/5.0 (compatible; RBF-fx/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=_ssl_context()) as r:
            raw = r.read(MAX_BYTES + 1)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError,
            http.client.HTTPException):
        # HTTPException (BadStatusLine, IncompleteRead) is NOT an OSError, so it
        # needs naming explicitly or a malformed upstream response escapes.
        # Upstream status codes and internal exceptions are deliberately not
        # surfaced to the browser; the caller gets a safe code only.
        raise ValueError(ERR_UNREACHABLE)
    if len(raw) > MAX_BYTES:
        raise ValueError(ERR_BAD_RESPONSE)
    return _validate(_parse_payload(raw))


def _age_days(reference_date: str) -> int:
    return (_utc_today() - date.fromisoformat(reference_date)).days


def _render(quote: Dict[str, Any], fetched_at: float, refresh_failed: bool,
            error: Optional[str]) -> Dict[str, Any]:
    age = _age_days(quote["reference_date"])
    if age <= FRESH_MAX_AGE_DAYS:
        status = STATUS_OK
    elif age <= STALE_MAX_AGE_DAYS:
        status = STATUS_STALE
    else:
        return _unavailable(ERR_TOO_OLD)
    return {
        "status": status,
        "provider": FX_PROVIDER,
        "rate_kind": RATE_KIND,
        "doc_url": FX_DOC_URL,
        "base": BASE_CODE,
        "quote": QUOTE_CODE,
        "vnd_per_usd": str(quote["rate"]),
        "reference_date": quote["reference_date"],
        "reference_age_days": age,
        "fetched_at": datetime.fromtimestamp(fetched_at, timezone.utc)
                              .isoformat(timespec="seconds"),
        "from_cache": refresh_failed or (time.time() - fetched_at) < CACHE_TTL_S,
        "refresh_failed": refresh_failed,
        "error": error,
    }


def _unavailable(code: str) -> Dict[str, Any]:
    return {
        "status": STATUS_UNAVAILABLE,
        "provider": FX_PROVIDER,
        "rate_kind": RATE_KIND,
        "doc_url": FX_DOC_URL,
        "base": BASE_CODE,
        "quote": QUOTE_CODE,
        "vnd_per_usd": None,
        "reference_date": None,
        "reference_age_days": None,
        "fetched_at": None,
        "from_cache": False,
        "refresh_failed": True,
        "error": code,
    }


def get_quote(force: bool = False) -> Dict[str, Any]:
    """Display metadata for the current reference rate. Never raises, and never
    blocks on the network while holding the module lock.

    Single-flight: at most one thread fetches at a time. Everyone else is served
    the cached quote, or an unavailable payload, *immediately* -- a stalled
    upstream costs one thread, not the worker pool.

    Lazy: nothing is fetched at import or startup, so an upstream outage cannot
    stop the application booting or affect any VND figure.
    """
    global _cache, _cache_fetched_at, _last_error, _fetching, _failed_until, _fail_streak

    now = time.time()
    with _lock:
        if not force and _cache is not None and now - _cache_fetched_at < CACHE_TTL_S:
            return _render(_cache, _cache_fetched_at, False, None)
        # Someone is already refreshing, or we are inside a backoff window after
        # a failure. Either way, answer from what we have rather than queueing.
        if _fetching or (not force and now < _failed_until):
            if _cache is not None:
                return _render(_cache, _cache_fetched_at, True, _last_error)
            return _unavailable(_last_error or ERR_UNREACHABLE)
        _fetching = True
        cache_snapshot, snapshot_at = _cache, _cache_fetched_at

    # ── network call happens OUTSIDE the lock ────────────────────────────────
    quote: Optional[Dict[str, Any]] = None
    err: Optional[str] = None
    try:
        quote = _fetch()
    except ValueError as e:
        err = str(e)
    except Exception:
        # `_fetch` converts the transport errors it anticipates. Anything it
        # did not must still be contained: this function's contract is that it
        # never raises, and an escape here would leave `_fetching` set.
        err = ERR_UNREACHABLE
    finally:
        # The single-flight flag is released unconditionally, including on an
        # exception that is not an `Exception` at all. Without this, one escaped
        # error wedges the adapter permanently -- every later caller sees a
        # refresh "in progress" that will never finish, so the rate can never
        # recover for the life of the process.
        with _lock:
            _fetching = False

    with _lock:
        if err is not None:
            _last_error = err
            _fail_streak = min(_fail_streak + 1, 8)
            _failed_until = time.time() + min(
                BACKOFF_BASE_S * (2 ** (_fail_streak - 1)), BACKOFF_MAX_S)
            if cache_snapshot is not None:
                # Keep serving the last VALIDATED quote, under the same
                # freshness bands, and say plainly that the refresh failed.
                # `snapshot_at` is NOT rewritten: a failed refresh of an old
                # observation is not a newly dated rate.
                return _render(cache_snapshot, snapshot_at, True, _last_error)
            return _unavailable(_last_error)

        _cache = quote
        _cache_fetched_at = time.time()
        _last_error = None
        _fail_streak = 0
        _failed_until = 0.0
        return _render(_cache, _cache_fetched_at, False, None)


def approximate_usd(vnd: int, vnd_per_usd: str) -> Optional[str]:
    """`vnd / R`, rounded to cents AT PRESENTATION ONLY.

    The VND argument is the authoritative integer amount and is never modified.
    Returns a decimal string, or None if the rate is unusable.
    """
    try:
        r = Decimal(str(vnd_per_usd))
        if not r.is_finite() or r <= 0:
            return None
        return str((Decimal(int(vnd)) / r).quantize(Decimal("0.01"),
                                                    rounding=ROUND_HALF_UP))
    except Exception:
        return None


def _reset_for_tests() -> None:
    global _cache, _cache_fetched_at, _last_error, _fetching, _failed_until, _fail_streak
    with _lock:
        _cache, _cache_fetched_at, _last_error = None, 0.0, None
        _fetching, _failed_until, _fail_streak = False, 0.0, 0
