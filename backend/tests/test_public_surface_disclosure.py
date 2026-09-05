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
INDEX = os.path.join(REPO, "frontend", "index.html")

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
    banner = src.index("demo-banner")
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


def test_the_remaining_personal_field_carries_a_notice_where_it_is_collected():
    """The waitlist email is the only personal datum left; the notice sits beside
    the input, not only on a page the user must go looking for."""
    src = _landing()
    i = src.index('id="wl-email"')
    window = src[i:i + 900]
    assert "only personal data" in window
    assert "delete" in window.lower() or "removed" in window.lower()


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

def test_waitlist_form_holds_exactly_the_input_and_the_button():
    """`.waitlist-form` is `display:flex` with `input{flex:1}` and was built for
    two children. The P2 privacy paragraph was inserted as a third, which claimed
    the row, collapsed the email input to a sliver and stretched the button to the
    paragraph's height — the page's primary interaction, unusable at desktop
    width. Invisible on mobile, where the container reflows to a column, which is
    how it shipped.

    The existing tests asserted the disclosure TEXT was present. None asserted the
    field still worked. This is that test.
    """
    import re
    src = open(INDEX, encoding="utf-8").read()
    m = re.search(r'<div class="waitlist-form">(.*?)</div>', src, re.S)
    assert m, "waitlist-form not found"
    children = re.findall(r"<(input|button|p|div|select|textarea)\b", m.group(1))
    assert children == ["input", "button"], (
        f"waitlist-form must contain exactly [input, button]; found {children}. "
        "A third flex child collapses the email field."
    )


def test_the_privacy_line_is_a_sibling_of_the_form_not_a_child():
    src = open(INDEX, encoding="utf-8").read()
    assert 'class="waitlist-privacy"' in src
    form_end = src.index('<div class="waitlist-form">')
    form_end = src.index("</div>", form_end)
    assert src.index('class="waitlist-privacy"') > form_end, \
        "the privacy line must follow the form, not sit inside it"


def test_the_flex_row_centres_its_children():
    """Without align-items the default `stretch` sizes the button to the tallest
    sibling, which is what produced the oversized button."""
    src = open(INDEX, encoding="utf-8").read()
    assert "align-items:center" in src[src.index(".waitlist-form{"):src.index(".waitlist-form{") + 120]


def test_new_markup_uses_classes_that_actually_exist():
    """The regressions shared one root cause: markup written against `.container`
    and a bare `.sub`, neither of which is defined, so it inherited nothing and
    fell back to inline styles sitting beside the design system."""
    src = open(INDEX, encoding="utf-8").read()
    assert 'class="container' not in src, ".container is not defined in this stylesheet"
    assert 'class="sub" style' not in src, "bare .sub is a no-op outside .app-card"
    for rule in (".waitlist-privacy{", ".demo-note{", ".field-note{"):
        assert rule in src, f"missing rule {rule}"
