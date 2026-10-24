"""Guards for the live-audit findings of 2026-09-02 (P1, P2, P4, P5, P7).

The audit's framing was right and is worth preserving in a test: the landing
page presented a commercial lender while the paper described a demonstration,
and it collected personal data like one. Those are one defect seen twice, so
they are guarded together.
"""
import os
import re

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)
BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BACKEND)          # backend/tests -> backend -> repo root
INDEX = os.path.join(REPO, "frontend", "demo.html")

# Deliberately NOT guarded with pytest.skip. An earlier guard in this repo
# skipped when its path was wrong, and a skip reads exactly like a pass. A
# missing fixture should stop the suite, not quietly excuse it.
assert os.path.exists(INDEX), f"landing page fixture not found at {INDEX}"


def _landing():
    return open(INDEX, encoding="utf-8").read()


# ── P1: the deployment's status must be visible where the visitor arrives ──
def test_landing_page_states_it_is_not_a_lending_service():
    """It previously appeared only in lab.html, a page most visitors never open,
    while the paper cited the landing URL."""
    src = _landing()
    assert "not a lending service" in src
    assert "holds no capital" in src.lower()


def test_the_disclosure_is_above_the_nav_not_buried():
    """A footnote below three screens of pricing is not a disclosure."""
    src = _landing()
    banner = src.index('<div class="demo-banner">')
    nav = src.index('<nav class="nav"')
    assert banner < nav, "the demonstration banner must precede the nav"


def test_commercial_sections_are_labelled_illustrative():
    """Pricing tiers, cohorts and API CTAs may stay, but must not read as
    services on sale."""
    src = _landing()
    pricing = src.index('id="pricing"')
    window = src[pricing:pricing + 1200]
    assert "Illustrative product design" in window
    assert "not a service" in window.lower() or "not a lending service" in window.lower()


# ── P2: stop collecting personal data the assessment never reads ──
def test_no_contact_name_or_phone_is_collected():
    """`owner_name` and `phone` are absent from ml_engine.FEATURES — they fed no
    computation and were stored anyway. Data that is not needed is not
    collected."""
    src = _landing()
    assert "f_owner_name" not in src
    assert "f_phone" not in src
    from ml_engine import FEATURES
    assert "owner_name" not in FEATURES and "phone" not in FEATURES

    # The `f_`-prefixed assertions above cover COLLECTION only, and for a while
    # that was all this test checked -- while the admin table still rendered
    # `owner_name` and the CSV export still shipped it as a column. Not
    # collecting a field and not disclosing it are different properties, and a
    # guard that conflates them reads as protection it does not provide.
    # `phone` is deliberately NOT asserted absent: it appears in the privacy
    # copy, which is the page telling the reader the field is not requested.
    assert "owner_name" not in src, (
        "owner_name reappeared in the public surface -- check the portfolio "
        "table and the CSV export column list, not just the form inputs"
    )


def test_access_list_input_is_retired():
    """The redesign does not solicit emails through a stored waitlist."""
    assert 'id="wl-email"' not in _landing()
    assert 'class="waitlist-form"' not in _landing()

def test_the_privacy_notice_is_current_and_does_not_call_this_a_pilot():
    src = _landing()
    page = src[src.index('id="page-privacy"'):]
    page = page[:6000]
    assert "research demonstration" in page
    assert "RBF is in pilot" not in page, "the pilot framing contradicts the banner"
    assert "Last updated July 2026" not in page, "stale date"


# ── P4: the SPA catch-all must not swallow everything ──
def test_robots_txt_is_a_real_file_not_the_landing_page():
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert "User-agent" in r.text


def test_unknown_paths_return_404_not_the_landing_page():
    r = client.get("/this-page-does-not-exist-12345")
    assert r.status_code == 404


def test_the_spa_routes_still_serve_the_app():
    for path in ("/", "/lab.html"):
        assert client.get(path).status_code == 200


# ── P5: baseline security headers ──
def test_security_headers_present():
    r = client.get("/")
    for h in ("Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options",
              "Referrer-Policy", "Strict-Transport-Security"):
        assert h in r.headers, f"missing {h}"
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]


# ── P7: a date that expires silently ──
def test_no_stale_cohort_date_is_advertised():
    """"next cohort · august 2026" was still live in September. Same defect class
    as the undated negative the research package corrected."""
    src = _landing().lower()
    assert "next cohort · august 2026" not in src
    assert not re.search(r"next cohort\s*·\s*\w+ 20\d\d", src), \
        "a hard-coded future cohort date will expire silently again"


def test_robots_expresses_an_allowlist_rather_than_implying_one():
    """Without a bare `Disallow: /`, Allow lines are inert — everything not
    explicitly disallowed is crawlable, so the file read as an allowlist while
    behaving as a blocklist. Flagged by the research chat's audit."""
    body = client.get("/robots.txt").text
    directives = "\n".join(l for l in body.splitlines() if not l.strip().startswith("#"))
    assert "Disallow: /" in directives, "the Allow lines are inert without it"
    for path in ("Allow: /$", "Allow: /lab", "Allow: /lab.html"):
        assert path in directives, f"missing {path}"


def test_both_lab_routes_resolve_so_both_must_be_listed():
    """`lab` is an SPA route and `lab.html` is the file; naming only one leaves
    the other governed by the blanket Disallow."""
    for path in ("/lab", "/lab.html"):
        assert client.get(path).status_code == 200


# ── R1: the disclosure must not break the field it describes ──

def test_contact_is_a_mail_link_not_a_collection_form():
    assert 'mailto:lehuuhoang1909@gmail.com' in _landing()
    assert 'onclick="submitWaitlist()"' not in _landing()

def test_prototype_warns_before_submission():
    src = _landing()
    banner = src[src.index('<div class="demo-banner">'):src.index('<nav class="nav"')]
    assert 'synthetic examples only' in banner.lower()
    assert 'stored' in banner and 'notifications' in banner

def test_prototype_shares_the_institutional_stylesheet():
    assert 'href="/institutional.css"' in _landing()

def test_new_markup_uses_classes_that_actually_exist():
    """The regressions shared one root cause: markup written against `.container`
    and a bare `.sub`, neither of which is defined, so it inherited nothing and
    fell back to inline styles sitting beside the design system."""
    src = open(INDEX, encoding="utf-8").read()
    assert 'class="container' not in src, ".container is not defined in this stylesheet"
    assert 'class="sub" style' not in src, "bare .sub is a no-op outside .app-card"
    for rule in (".waitlist-privacy{", ".demo-note{", ".field-note{"):
        assert rule in src, f"missing rule {rule}"


def test_prototype_mobile_navigation_exposes_its_state():
    src = _landing()
    assert 'aria-controls="mobile-menu"' in src
    assert "setAttribute('aria-expanded',String(open))" in src

# ── P8: the Lab comparison table on a phone ──

def test_lab_table_stacks_in_a_narrow_container():
    """Measured at 375px before the fix: a 760px table in a 313px scroller, so
    reading one contract meant scrolling ~2.4 screen-widths sideways. Below
    600px each row becomes a card. Asserted on the source because the layout is
    CSS-only; the rendered geometry was verified in a browser at 375 and 1280."""
    src = open(os.path.join(REPO, "frontend", "lab.html"), encoding="utf-8").read()
    assert "container-type:inline-size" in src, "the query needs a container"
    assert "@container (width < 600px)" in src, "a container query, not a media query"
    assert "#dur-table thead{display:none;}" in src, "header row must leave the a11y tree too"
    assert "#dur-table table{min-width:0;width:100%;}" in src, (
        "table.data carries min-width:760px; display:block does not relax it, "
        "and leaving it keeps the horizontal scrollbar alive when stacked")


def test_lab_table_labels_request_alternative_text_without_the_colon():
    """Check CSS alternative-text syntax; this is not a screen-reader test."""
    src = open(os.path.join(REPO, "frontend", "lab.html"), encoding="utf-8").read()
    for n in range(2, 8):
        assert f'#dur-table td:nth-child({n})::before{{content:var(--l{n}) ": " / var(--l{n});}}' in src, \
            f"column {n} has no labelled ::before with an accessible name"
