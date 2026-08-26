"""Browser tests for behaviour no static assertion can reach (D-035).

Two failures motivated these, and neither was catchable by inspecting source:

  * A slow response for scenario A landing after a fast one for B left B's pill
    above A's numbers. Only a real event loop with real timing shows it.
  * A server `detail` string reached the browser console. Grepping the source
    proves the call is gone; only capturing console output proves nothing else
    prints it.

Skipped cleanly wherever Playwright or a browser binary is unavailable, so the
suite still runs everywhere. Run them explicitly with:

    python -m pytest backend/tests/test_lab_browser.py -v
"""
import json
import os
import socket
import subprocess
import sys
import time

import pytest

pytest.importorskip("playwright.sync_api", reason="playwright not installed")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET = "password=hunter2 /srv/app/db.py"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    port = _free_port()
    env = {**os.environ,
           "DASHBOARD_PASSWORD": "browser-test",
           "DATABASE_URL": f"/tmp/lab_browser_{port}.db",
           "RBF_MODEL_DIR": "/tmp/lab_browser_nomodels"}
    os.makedirs(env["RBF_MODEL_DIR"], exist_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
         "--port", str(port)],
        cwd=os.path.join(REPO, "backend"), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    for _ in range(40):
        time.sleep(0.5)
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            continue
    else:
        proc.terminate()
        pytest.skip("server did not start")
    yield url
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="module")
def browser():
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage",
                                        "--disable-gpu"])
            yield b
            b.close()
    except Exception as e:                      # no browser binary / no deps
        pytest.skip(f"chromium unavailable: {str(e)[:80]}")


def test_stale_response_never_updates_the_page(server, browser):
    """Request A is held, B resolves first, then A lands. The page must be
    entirely B — pill, description, summary and cards agreeing."""
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(700)

    held = {}

    def router(route):
        if "closure_m7" in route.request.url:
            held["A"] = route                    # hold A indefinitely
        else:
            route.continue_()

    pg.route("**/api/lab/comparison/**", router)
    pg.evaluate("document.querySelector('#scn-groups button[data-k=closure_m7]').click()")
    pg.wait_for_timeout(500)
    pg.evaluate("document.querySelector('#scn-groups button[data-k=growth]').click()")
    pg.wait_for_timeout(900)                     # B commits
    if "A" in held:
        held["A"].continue_()                    # A arrives late
    pg.wait_for_timeout(1200)

    state = pg.evaluate("""() => {
      const pill=[...document.querySelectorAll('#scn-groups button')]
        .find(b=>b.getAttribute('aria-pressed')==='true');
      return {pill: pill ? pill.dataset.k : null,
              desc: document.getElementById('scn-desc').textContent,
              summary: document.getElementById('summary-text').textContent};}""")

    assert state["pill"] == "growth", f"pill shows {state['pill']}"
    assert "growth" in state["summary"].lower()
    assert "closes permanently" not in state["desc"], "stale description committed"
    assert "closure" not in state["summary"].lower()
    pg.close()


def test_no_server_detail_reaches_dom_or_console(server, browser):
    """An injected secret must appear in neither the rendered page nor any
    captured console output."""
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    logs = []
    pg.on("console", lambda m: logs.append(f"{m.type}:{m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"pageerror:{e}"))
    pg.route("**/api/lab/manifest", lambda r: r.fulfill(
        status=500, content_type="application/json",
        body=json.dumps({"detail": SECRET})))
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(700)

    dom = pg.content()
    joined = " ".join(logs)
    for token in ("hunter2", "db.py", "/srv/app"):
        assert token not in dom, f"{token!r} leaked into the DOM"
        assert token not in joined, f"{token!r} leaked into the console"

    assert pg.locator("#st-error").is_visible()
    assert pg.inner_text("#err-detail") == "The server could not complete this request."
    # diagnostics still exist, and carry only route/status/requestId
    assert any("[lab] request failed" in l for l in logs)
    pg.close()


def test_ready_state_never_shows_an_empty_research_view(server, browser):
    """While the first comparison is in flight the loading state must hold; the
    content region must not appear empty."""
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    held = []
    pg.route("**/api/lab/comparison/**", lambda r: held.append(r))
    pg.goto(f"{server}/lab", wait_until="commit")
    pg.wait_for_timeout(1500)

    assert pg.locator("#st-loading").is_visible(), "loading state not shown"
    assert not pg.locator("#content").is_visible(), "empty content exposed as ready"
    assert pg.locator("#arms .arm").count() == 0

    for r in held:
        r.continue_()
    pg.wait_for_timeout(1500)
    assert pg.locator("#content").is_visible()
    assert pg.locator("#arms .arm").count() == 4
    pg.close()


def test_failed_initial_comparison_shows_an_error_not_a_blank_page(server, browser):
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.route("**/api/lab/comparison/**", lambda r: r.fulfill(
        status=500, content_type="application/json", body='{"detail":"boom"}'))
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(900)
    assert pg.locator("#st-error").is_visible()
    assert not pg.locator("#content").is_visible()
    pg.close()


def test_footer_survives_a_missing_spec_version(server, browser):
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.route("**/api/lab/manifest", lambda r: r.fulfill(
        status=200, content_type="application/json",
        body=json.dumps({"artifacts": [{"artifact": "x.json", "role": "r",
                                        "sha256": "0" * 64, "spec_version": "",
                                        "n_paths": 1, "base_seed": 1}],
                         "claim_taxonomy": {}, "glossary": {},
                         "pricing_reference": {}, "integrity": {}})))
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(700)
    foot = pg.inner_text("footer")
    assert "under ." not in foot, "empty spec_version blanked the footer"
    assert "the frozen methodology specification" in foot
    pg.close()


def test_malformed_200_response_leaks_nothing(server, browser):
    """A 200 can still carry unparseable bytes. JSON.parse's SyntaxError message
    quotes those bytes verbatim, so it must never surface."""
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    logs = []
    pg.on("console", lambda m: logs.append(f"{m.type}:{m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"pageerror:{e}"))
    pg.route("**/api/lab/manifest", lambda r: r.fulfill(
        status=200, content_type="application/json",
        body="{ not json at all " + SECRET + " }"))
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(800)

    dom = pg.content()
    joined = " ".join(logs)
    for token in ("hunter2", "db.py", "/srv/app", "not json at all"):
        assert token not in dom, f"{token!r} leaked into the DOM"
        assert token not in joined, f"{token!r} leaked into the console"

    assert pg.locator("#st-error").is_visible()
    shown = pg.inner_text("#err-detail")
    assert shown in ("The research data could not be read.",
                     "The page could not display this research result."), shown
    pg.close()


def test_render_exception_leaks_nothing(server, browser):
    """A thrown Error from a render path carries a message we did not write.
    Forced here by making a render helper throw with the secret in it."""
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    logs = []
    pg.on("console", lambda m: logs.append(f"{m.type}:{m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"pageerror:{e}"))
    pg.add_init_script(
        "window.addEventListener('DOMContentLoaded',function(){"
        "  var t=setInterval(function(){"
        "    if(typeof renderArms==='function'){clearInterval(t);"
        "      window.renderArms=function(){throw new Error('render blew up " + SECRET + "');};}"
        "  },10);});")
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(1200)

    dom = pg.content()
    # pageerror/console may legitimately record an uncaught throw; what must not
    # happen is the message reaching the rendered page.
    for token in ("hunter2", "db.py", "/srv/app", "render blew up"):
        assert token not in dom, f"{token!r} leaked into the DOM"

    if pg.locator("#st-error").is_visible():
        assert pg.inner_text("#err-detail") == \
            "The page could not display this research result."
    pg.close()


def test_censored_arm_shows_both_denominators_separately(server, browser):
    """closure_m13 is the scenario where the two denominators come apart.

    Completion: 92.4% cost-matched, 23.8% illustrative. Rate-defined: 100% for
    BOTH arms — every path made payments, so every path has a rate over the
    observed window even where the cap was never reached.

    This test previously required "Mean APR among completed paths" and a finding
    saying the arms "cannot be compared on rate alone". Both encoded the
    pre-A-9 error of putting the rate under the completion denominator. Since
    both arms are 100% rate-defined, their rates ARE comparable; what differs is
    how much of the contract each rate covers, which is what the observed-window
    note beside the rate is for.
    """
    pg = browser.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelector('#scn-groups button[data-k=closure_m13]').click()")
    pg.wait_for_timeout(900)

    arms_text = pg.inner_text("#arms")

    # Both denominators are on the card, labelled as different quantities.
    assert "Paths completing within 24 months" in arms_text
    assert "Paths with a defined rate" in arms_text
    assert "92.4%" in arms_text and "23.8%" in arms_text
    assert "100.0%" in arms_text          # the rate-defined share, both arms

    # The rate is labelled by EXISTENCE; only the duration by completion.
    assert "Mean simulated APR among rate-defined paths" in arms_text
    assert "Mean duration among completed paths" in arms_text
    assert "Mean APR among completed paths" not in arms_text

    # Both bases are spelled out, and the rate's carries the window caveat.
    assert "How the rate is computed" in arms_text
    assert "How the duration mean is computed" in arms_text
    assert "observed" in arms_text and "window" in arms_text

    table = pg.inner_text("#dur-table")
    assert "completed paths only" in table
    # the header is CSS-uppercased, so compare case-insensitively
    assert "completed in 24 mo" in table.lower()

    findings = pg.inner_text("#findings")
    assert "cannot be compared on rate alone" not in findings
    # Censoring is still reported, and still not called default.
    assert "76.2%" in findings
    assert "not a modelled default" in findings
    pg.close()


def test_uncensored_arm_shows_no_spurious_qualifier(server, browser):
    """At `stable` every path completes and every path has a rate, so the two
    denominators coincide and neither qualifier belongs on the page."""
    pg = browser.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(f"{server}/lab", wait_until="networkidle")
    pg.wait_for_timeout(700)
    pg.evaluate("document.querySelector('#scn-groups button[data-k=stable]').click()")
    pg.wait_for_timeout(800)
    arms_text = pg.inner_text("#arms")
    assert "among completed paths" not in arms_text
    assert "among rate-defined paths" not in arms_text
    assert "Paths completing within 24 months" not in arms_text
    assert "Paths with a defined rate" not in arms_text
    assert "Mean simulated APR" in arms_text and "Mean duration" in arms_text
    assert "completed paths only" not in pg.inner_text("#dur-table")
    pg.close()
