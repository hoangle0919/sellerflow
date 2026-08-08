"""Simulation Lab — the UI may not invent, hide, or misattribute a number.

The load-bearing tests here are the negative ones. It is easy to build a
research page that looks right and quietly hard-codes a figure someone typed in
once; this suite makes that fail.
"""
import json
import os
import re
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main  # noqa: E402
import lab  # noqa: E402

client = TestClient(main.app)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB_HTML = os.path.join(REPO, "frontend", "lab.html")
RESULTS = os.path.join(REPO, "research", "results")

pytestmark = pytest.mark.skipif(not lab.artifacts_available(),
                                reason="research artifacts not present")


def _canonical(stem):
    with open(os.path.join(RESULTS, f"{stem}_canonical.json"), encoding="utf-8") as fh:
        return json.load(fh)


# ── routes ──────────────────────────────────────────────────────────────────

def test_lab_page_is_served():
    r = client.get("/lab")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]


@pytest.mark.parametrize("path", ["/api/lab/manifest", "/api/lab/scenarios"])
def test_lab_endpoints_return_ok(path):
    assert client.get(path).status_code == 200


def test_every_listed_scenario_has_a_comparison():
    for s in client.get("/api/lab/scenarios").json()["scenarios"]:
        assert client.get(f"/api/lab/comparison/{s['key']}").status_code == 200


def test_unknown_scenario_is_404_not_a_silent_empty_page():
    assert client.get("/api/lab/comparison/does_not_exist").status_code == 404


# ── provenance is displayed ─────────────────────────────────────────────────

def test_manifest_reports_artifact_checksums():
    arts = client.get("/api/lab/manifest").json()["artifacts"]
    assert arts, "no artifacts reported"
    for a in arts:
        assert re.fullmatch(r"[0-9a-f]{64}", a["sha256"] or ""), a["artifact"]
        assert a["spec_version"] and a["n_paths"] and a["base_seed"]


def test_served_checksum_matches_the_artifact_on_disk():
    """The page must not display a checksum that no longer describes the file."""
    sys.path.insert(0, os.path.join(REPO, "research"))
    from rbf_sim.canonical import checksum
    for a in client.get("/api/lab/manifest").json()["artifacts"]:
        stem = a["artifact"].replace("_canonical.json", "")
        assert a["sha256"] == checksum(_canonical(stem)), stem


def test_page_renders_the_checksum_and_spec_version():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "sha256" in html
    assert "prov-table" in html and "foot-spec" in html


# ── values originate in the artifact ────────────────────────────────────────

@pytest.mark.parametrize("scenario", ["stable", "sustained_decline", "severe_downturn"])
def test_arm_values_match_the_canonical_artifact_exactly(scenario):
    """Every displayed metric is traced back to the file it came from."""
    data = client.get(f"/api/lab/comparison/{scenario}").json()
    for arm in data["arms"]:
        stem = arm["source_artifact"].replace("_canonical.json", "")
        spec = next(a for a in lab.ARMS if a["id"] == arm["id"])
        src = _canonical(stem)["scenarios"][scenario][spec["arm"]]
        assert arm["burden"]["mean"] == src["burden_mean"]
        assert arm["burden"]["max"] == src["burden_max"]
        assert arm["duration_months_mean"] == src["duration_mean"]
        assert arm["recovery_ratio"] == src["recovery_ratio"]
        assert arm["effective_apr"] == src["apr_mean"]
        assert arm["incomplete_recovery_rate"] == src["incomplete_recovery_rate"]


def test_findings_quote_the_same_numbers_the_charts_show():
    """A narrative sentence must not drift from the chart beside it."""
    d = client.get("/api/lab/comparison/sustained_decline").json()
    by = {a["id"]: a for a in d["arms"]}
    txt = " ".join(f["text"] for f in d["findings"])
    assert f"{by['FIX-A']['burden']['max']:.1%}" in txt
    assert f"{by['RBF-ILL']['burden']['max']:.1%}" in txt
    assert "sustained decline" in txt.lower(), "scenario-dependent findings must name the scenario"


def test_no_research_number_is_hard_coded_in_the_page():
    """The HTML must contain no research figure. Everything comes from the API.

    Scans for the registered constants and for any long decimal that looks like
    a transcribed result. Layout numbers (viewBox units, font sizes, colours)
    are not research output and are expected."""
    html = open(LAB_HTML, encoding="utf-8").read()
    for forbidden in ("1.0945", "0.9098", "0.9182", "17076923", "222000000",
                      "202482500", "37.87", "19.5618", "19.5377", "264d319b"):
        assert forbidden not in html, f"research value {forbidden!r} hard-coded in lab.html"
    # No 4+ decimal-place floats, which is what a pasted result looks like.
    leaked = [m for m in re.findall(r"\b\d+\.\d{4,}\b", html)]
    assert not leaked, f"suspicious precise literals in lab.html: {leaked[:5]}"


def test_page_performs_no_contractual_arithmetic():
    """Financial logic stays in the backend. The page may scale a bar to a
    pixel width; it may not compute money, a cap, a duration or an APR."""
    html = open(LAB_HTML, encoding="utf-8").read()
    for banned in ("factor_rate *", "* factor", "cap *", "* cap",
                   "/ 12", "Math.pow", "apr =", "cap ="):
        assert banned not in html, f"looks like financial arithmetic in the page: {banned!r}"


# ── the two RBF prices cannot be confused ───────────────────────────────────

def test_equal_cost_and_illustrative_arms_are_distinct_and_labelled():
    d = client.get("/api/lab/comparison/stable").json()
    by = {a["id"]: a for a in d["arms"]}
    eq, ill = by["RBF-EQ"], by["RBF-ILL"]

    assert eq["cap_factor"] != ill["cap_factor"]
    assert eq["source_artifact"] != ill["source_artifact"]
    assert "reference-path cost-matched" in eq["name"].lower()
    assert "illustrative" in ill["name"].lower()
    # The illustrative arm must say it is not a market price.
    assert "illustrative" in ill["note"].lower()
    assert "not of revenue-based" in ill["note"].lower() or "property of choosing" in ill["note"].lower()


def test_illustrative_price_is_never_called_the_price_of_rbf():
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    for bad in ("rbf costs", "the cost of rbf is", "rbf's price is"):
        assert bad not in html


# ── monetary serialization ──────────────────────────────────────────────────

def test_monetary_fields_are_integer_vnd_with_display_strings():
    d = client.get("/api/lab/comparison/stable").json()
    for a in d["arms"]:
        for key in ("principal", "contractual_cap", "total_repaid_mean"):
            m = a[key]
            if m is None:            # amortizing arm has no cap, by design
                assert key == "contractual_cap" and a["id"] == "FIX-B"
                continue
            assert isinstance(m["vnd"], int) and not isinstance(m["vnd"], bool)
            assert m["display"].endswith("₫")
            assert str(m["vnd"])[0] in m["display"].replace(",", "")[0]


def test_contractual_cap_equals_principal_times_cap_factor_in_whole_dong():
    """Cross-check the served cap against the centralized money policy."""
    from money import to_vnd, to_decimal
    d = client.get("/api/lab/comparison/stable").json()
    for a in d["arms"]:
        if a["cap_factor"] and a["contractual_cap"]:
            expect = to_vnd(to_decimal(a["principal"]["vnd"]) * to_decimal(a["cap_factor"]))
            assert a["contractual_cap"]["vnd"] == expect, a["id"]


# ── disclosure ──────────────────────────────────────────────────────────────

def test_final_partial_payment_is_disclosed_on_the_page():
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "final payment is partial" in html
    assert "overstates" in html


def test_metric_definitions_ship_with_their_caveats():
    defs = client.get("/api/lab/comparison/stable").json()["metric_definitions"]
    assert "by construction" in defs["high_burden_months"]["caveat"].lower()
    assert "not a default rate" in defs["incomplete_recovery_rate"]["caveat"].lower()


def test_every_finding_carries_a_claim_classification():
    tax = set(lab.CLAIM_TAXONOMY)
    for s in ("stable", "severe_downturn"):
        for f in client.get(f"/api/lab/comparison/{s}").json()["findings"]:
            assert f["classification"] in tax
            assert f["source"]


def test_all_five_claim_classes_are_defined_and_rendered():
    tax = client.get("/api/lab/manifest").json()["claim_taxonomy"]
    assert set(tax) == {"mathematical_property", "simulation_result",
                        "sensitivity_result", "product_implication",
                        "open_real_world_question"}
    html = open(LAB_HTML, encoding="utf-8").read()
    for k in tax:
        assert f"cls-{k}" in html, f"no style for claim class {k}"


# ── prohibited claims ───────────────────────────────────────────────────────

def test_withdrawn_auc_appears_nowhere_in_the_lab():
    """Targets the withdrawn benchmark specifically.

    A naive `"0.92" not in blob` is wrong: recovery ratio 12/13 is
    0.923076923…, a legitimate figure that has nothing to do with the AUC. The
    check is therefore for the metric NAME and for a value that is exactly 0.92.
    """
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "AUC" not in html and "auc" not in html.replace("because", "")

    payloads = [client.get("/api/lab/manifest").json()]
    for s in ("stable", "severe_downturn"):
        payloads.append(client.get(f"/api/lab/comparison/{s}").json())

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from walk(v, f"{path}[{i}]")
        else:
            yield path, node

    for p in payloads:
        for path, v in walk(p):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                assert abs(v - 0.92) > 1e-9 or "recovery" in path.lower(), \
                    f"withdrawn 0.92 benchmark served at {path}"
            if isinstance(v, str):
                assert "AUC" not in v, f"AUC referenced at {path}"


def test_rbf_g_is_not_promoted_anywhere():
    """D-018: a design whose floor provably never activates is not a product."""
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "RBF-G" not in html
    blob = json.dumps(client.get("/api/lab/comparison/stable").json())
    assert "RBF-G" not in blob
    assert all(a["id"] != "RBF-G" for a in client.get("/api/lab/comparison/stable").json()["arms"])


def test_ensemble_is_described_as_synthetic_and_unvalidated():
    m = client.get("/api/lab/manifest").json()
    assert "unvalidated" in m["integrity"]["underwriting_model"].lower()
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "unvalidated" in html


def test_no_claim_of_observed_vietnam_seller_outcomes():
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "no observed seller revenue" in html
    for bad in ("we observed", "actual seller data", "real seller outcomes",
                "based on real merchants"):
        assert bad not in html


def test_intervals_are_not_called_population_confidence_intervals():
    m = client.get("/api/lab/manifest").json()["integrity"]
    assert "not" in m["intervals"].lower() and "population" in m["intervals"].lower()
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "confidence interval" not in html


def test_fixed_arm_default_risk_is_not_implied_away():
    """The fixed arms are modelled as always repaid. Saying so is the point."""
    caveats = " ".join(c["text"].lower()
                       for c in client.get("/api/lab/comparison/stable").json()["caveats"])
    assert "default risk" in caveats and "does not model" in caveats


def test_no_universal_claim_about_provider_recovery_direction():
    caveats = " ".join(c["text"].lower()
                       for c in client.get("/api/lab/comparison/stable").json()["caveats"])
    assert "depends on the revenue path" in caveats
    assert "universal claim" in caveats


def test_constant_revenue_projections_are_labelled_illustrative():
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "illustrative" in html
    ill = next(a for a in client.get("/api/lab/comparison/stable").json()["arms"]
               if a["id"] == "RBF-ILL")
    assert "illustrative" in ill["name"].lower()


# ── accessibility basics ────────────────────────────────────────────────────

def test_page_has_language_viewport_title_and_skip_link():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert '<html lang="en">' in html
    assert 'name="viewport"' in html
    assert "<title>" in html
    assert 'class="skip"' in html


def test_charts_and_controls_carry_accessible_names():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert html.count('role="img"') >= 3
    assert html.count("aria-labelledby") >= 4
    assert "aria-pressed" in html          # scenario toggles announce state
    assert "focus-visible" in html         # keyboard focus is visible


def test_amortizing_arm_is_not_given_the_rbf_cap():
    """FIX-B is an annuity: no cap factor, no repayment cap. Attributing the
    RBF contract's ×1.20 cap to it would show a cap larger than its own total."""
    d = client.get("/api/lab/comparison/stable").json()
    b = next(a for a in d["arms"] if a["id"] == "FIX-B")
    assert b["cap_factor"] is None
    assert b["contractual_cap"] is None
    assert "no cap" in b["cap_basis"].lower()
    a_ = next(a for a in d["arms"] if a["id"] == "FIX-A")
    assert a_["contractual_cap"]["vnd"] == a_["total_repaid_mean"]["vnd"]


def test_equal_cost_label_does_not_overclaim_on_stochastic_paths():
    """The cap factor was calibrated on the deterministic reference path. Across
    simulated paths the realised APR differs, because duration varies. Saying
    'equal effective cost' without that caveat would overclaim."""
    d = client.get("/api/lab/comparison/stable").json()
    eq = next(a for a in d["arms"] if a["id"] == "RBF-EQ")
    note = eq["note"].lower()
    assert "reference path" in note and "differs" in note
    caveats = " ".join(c["text"].lower() for c in d["caveats"])
    assert "solved on the reference path" in caveats


# ── refinement pass (D-033): terminology, scenarios, states, palette ────────

def test_closure_scenarios_are_selectable():
    """Every scenario previously exposed repays in full. Closure is where
    incomplete recovery is real; omitting it would flatter the result."""
    keys = {s["key"] for s in client.get("/api/lab/scenarios").json()["scenarios"]}
    assert {"closure_m7", "closure_m13", "temp_closure"} <= keys


def test_closure_shows_genuine_incomplete_recovery():
    d = client.get("/api/lab/comparison/closure_m7").json()
    rbf = next(a for a in d["arms"] if a["id"] == "RBF-ILL")
    assert rbf["incomplete_recovery_rate"] > 0.5
    assert rbf["recovery_ratio"]["24"] < 1.0


def test_undefined_apr_is_reported_not_substituted():
    """When revenue stops the payment stream never repays, so no IRR exists.
    Spec 13 E-3 requires reporting undefined rather than inventing a number."""
    d = client.get("/api/lab/comparison/closure_m7").json()
    rbf = next(a for a in d["arms"] if a["id"] == "RBF-ILL")
    assert rbf["effective_apr"] is None
    txt = " ".join(f["text"].lower() for f in d["findings"])
    assert "undefined" in txt


def test_every_rate_declares_its_basis():
    for a in client.get("/api/lab/comparison/stable").json()["arms"]:
        assert "mean across simulated paths" in a["apr_basis"]


def test_recovery_denominator_is_declared_per_arm():
    d = client.get("/api/lab/comparison/stable").json()
    by = {a["id"]: a for a in d["arms"]}
    assert "no cap" in by["FIX-B"]["recovery_denominator"].lower()
    assert "cap" in by["FIX-A"]["recovery_denominator"].lower()
    assert "denominator" in d["metric_definitions"]["recovery_ratio"]["caveat"].lower()


def test_burden_thresholds_are_marked_illustrative():
    caveat = client.get("/api/lab/comparison/stable").json()[
        "metric_definitions"]["high_burden_months"]["caveat"].lower()
    assert "illustrative" in caveat
    assert "not validated hardship cutoffs" in caveat


def test_burden_is_not_claimed_to_measure_affordability():
    """'Lower is easier to carry' outran the metric: margins, costs and other
    debts are outside the model."""
    d = client.get("/api/lab/comparison/stable").json()
    assert "affordable" in d["metric_definitions"]["burden"]["caveat"].lower()
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    assert "easier to carry" not in html


def test_scenario_dependent_findings_name_their_scenario():
    for key, label in (("growth", "growth"), ("closure_m7", "closure, month 7")):
        d = client.get(f"/api/lab/comparison/{key}").json()
        for f in d["findings"]:
            if f["classification"] == "simulation_result":
                assert label in f["text"].lower(), f["text"]


def test_underreporting_is_offered_but_not_as_a_scenario():
    u = client.get("/api/lab/underreporting").json()
    assert len(u["rows"]) >= 4
    assert "not a revenue path" in u["why_not_a_scenario"].lower()
    keys = {s["key"] for s in client.get("/api/lab/scenarios").json()["scenarios"]}
    assert not any("underreport" in k for k in keys)


def test_glossary_defines_the_specialist_terms():
    g = client.get("/api/lab/manifest").json()["glossary"]
    for term in ("cap factor", "remittance", "effective APR",
                 "Monte Carlo interval", "canonical artifact", "reference path"):
        assert term in g and len(g[term]) > 30


def test_page_implements_loading_error_and_unavailable_states():
    html = open(LAB_HTML, encoding="utf-8").read()
    for sid in ("st-loading", "st-error", "st-unavailable", "retry"):
        assert f'id="{sid}"' in html, f"missing state element {sid}"
    assert "aria-live" in html


def test_palette_is_categorical_not_valenced():
    """Red-versus-green read as fixed = bad, revenue-based = good before any
    copy was read. Colour now identifies a contract, nothing more."""
    html = open(LAB_HTML, encoding="utf-8").read()
    for tok in ("--c-fixed-a", "--c-fixed-b", "--c-rbf-ref", "--c-rbf-ill"):
        assert tok in html
    for banned in ("--decline", "--approve", "#2E6B4F", "#8C3A38"):
        assert banned not in html, f"old valenced colour {banned} still present"
    for a in client.get("/api/lab/comparison/stable").json()["arms"]:
        assert a["palette"] in {"fixed-a", "fixed-b", "rbf-ref", "rbf-ill"}
        assert "good" not in json.dumps(a).lower().replace("goods", "")


def test_one_shared_legend_not_one_per_chart():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert html.count('class="legend"') == 1


def test_mobile_table_has_a_scroll_affordance():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "dur-scrollnote" in html and "scrollnote" in html
    assert "Scroll the table sideways" in html


def test_limitations_are_not_collapsed_behind_disclosure():
    """Anti-pattern guard: favourable findings must not be prominent while
    limitations hide in collapsed content."""
    html = open(LAB_HTML, encoding="utf-8").read()
    limits = html.split('id="s-limits"', 1)[1].split("</section>", 1)[0]
    assert 'id="caveats"' in limits
    before = limits.split('id="caveats"', 1)[0]
    # Nesting depth, not mere presence: a sibling card may legitimately use a
    # disclosure (the glossary does). What matters is whether the caveats list
    # itself sits inside one that is still open.
    depth = before.count("<details") - before.count("</details>")
    assert depth == 0, "limitations list is inside a collapsed element"


# ── contrast, weight, and the audit's "keep" regressions ───────────────────

def _luminance(hexs):
    hexs = hexs.lstrip("#")
    ch = [int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in ch)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


@pytest.mark.parametrize("fg,bg,label", [
    ("#1A1A1A", "#FAF9F4", "body text"),
    ("#54544D", "#FFFFFF", "muted text"),
    ("#6E6E66", "#FFFFFF", "faint text"),
    ("#005B8F", "#E7F1F8", "fixed-a badge"),
    ("#15607F", "#E8F4FB", "fixed-b badge"),
    ("#7A5500", "#FBF2E0", "rbf-ref badge"),
    ("#8A3F6B", "#F9EDF4", "rbf-ill badge"),
])
def test_text_contrast_meets_wcag_aa(fg, bg, label):
    assert _contrast(fg, bg) >= 4.5, f"{label}: {_contrast(fg, bg):.2f}:1"


@pytest.mark.parametrize("fill", ["#0072B2", "#239DE2", "#C68900", "#CC79A7"])
def test_bar_fills_meet_non_text_contrast(fill):
    """WCAG 1.4.11: graphical objects carrying meaning need 3:1."""
    assert _contrast(fill, "#FFFFFF") >= 3.0, f"{fill}: {_contrast(fill, '#FFFFFF'):.2f}:1"


def test_page_loads_no_framework_or_third_party_asset():
    """Principle 9 regression: the page stays a hand-written client."""
    html = open(LAB_HTML, encoding="utf-8").read()
    for bad in ("cdn.", "unpkg", "jsdelivr", "googleapis", "react", "vue",
                "jquery", "chart.js", "d3.", "gtag", "analytics"):
        assert bad not in html.lower(), f"third-party dependency: {bad}"
    assert html.count("<script") == 1
    assert "src=" not in html.split("<script")[1].split(">")[0]


def test_inline_javascript_stays_small():
    """Measured, not estimated. A budget that fails loudly if the page grows a
    framework by accident."""
    html = open(LAB_HTML, encoding="utf-8").read()
    js = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    assert len(js.encode()) < 40_000, f"inline JS is {len(js.encode()):,} B"


# Principle 5 (unobtrusive) — scored 3, must not regress.
def test_no_modal_autoplay_or_conversion_cta():
    html = open(LAB_HTML, encoding="utf-8").read().lower()
    for bad in ("<dialog", "autoplay", "<video", "role=\"dialog\"",
                "sign up", "get started", "buy now", "subscribe", "book a demo"):
        assert bad not in html, f"interruptive/promotional element: {bad}"


# Principle 7 (long-lasting) — scored 3, must not regress.
def test_typographic_roles_and_flat_surfaces_preserved():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "Fraunces" in html and "Archivo" in html and "Spline Sans Mono" in html
    for trend in ("linear-gradient", "radial-gradient", "backdrop-filter",
                  "@keyframes", "animation:"):
        assert trend not in html, f"dated visual trend introduced: {trend}"


# Principle 2 (useful) — scored 3, must not regress.
def test_one_scenario_choice_updates_every_registered_section():
    """A single selection must still drive the whole comparison."""
    a = client.get("/api/lab/comparison/stable").json()
    b = client.get("/api/lab/comparison/severe_downturn").json()
    assert a["scenario"]["key"] != b["scenario"]["key"]
    for section in ("arms", "findings", "summary"):
        assert a[section] != b[section], f"{section} did not change with the scenario"
    assert a["arms"][0]["burden"]["max"] != b["arms"][0]["burden"]["max"]


def test_summary_is_derived_from_this_scenarios_own_values():
    d = client.get("/api/lab/comparison/severe_downturn").json()
    by = {x["id"]: x for x in d["arms"]}
    s = d["summary"]
    assert s["peak_burden_fixed"] == by["FIX-A"]["burden"]["max"]
    assert s["peak_burden_rbf"] == by["RBF-ILL"]["burden"]["max"]
    assert f"{by['FIX-A']['burden']['max']:.1%}" in s["sentence"]


def test_uncompleted_duration_is_stated_not_dashed():
    """At closure no path reaches the target, so the mean duration is undefined.
    The page says so rather than printing a bare dash."""
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "Not completed within 24 months" in html


# ── closing pass (D-034): label clipping, states copy, annuity wording ─────

def test_chart_labels_are_short_enough_not_to_clip():
    """The gutter is measured at runtime, but a runaway label would still push
    it to the clamp. Keep the axis labels compact at source."""
    for a in client.get("/api/lab/comparison/stable").json()["arms"]:
        assert a["chart_label"], a["id"]
        assert len(a["chart_label"]) <= 24, f"{a['id']}: {a['chart_label']!r}"


def test_chart_gutter_is_measured_not_hard_coded():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "measureText" in html, "label width must be measured"
    assert "padL=narrow?0:206" not in html, "fixed gutter reintroduced"


def test_footer_reads_correctly_before_the_manifest_loads():
    """The spec version is injected by renderProvenance(), which never runs when
    the manifest fails — leaving 'Simulation output under .' on screen."""
    html = open(LAB_HTML, encoding="utf-8").read()
    foot = html.split('id="foot-spec"', 1)[1].split("</span>", 1)[0]
    assert foot.strip(">").strip(), "foot-spec has no default text"
    assert "under <span" not in html.replace('\n', ' ') or "the frozen" in html


def test_server_error_text_is_never_rendered_to_the_user():
    """A detail string may carry stack context, an internal path, or an upstream
    message. Copy is chosen from the status code; the detail goes to the console."""
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "ERROR_COPY" in html and "userMessage(" in html
    assert "console.warn" in html
    # the error panel must never be handed a server string
    assert 'show("error",e.message)' in html
    assert "body.detail" not in html and "(body&&body.detail)" not in html


def test_amortizing_loan_reports_its_scheduled_total_not_no_cap():
    d = client.get("/api/lab/comparison/stable").json()
    by = {a["id"]: a for a in d["arms"]}
    b = by["FIX-B"]
    assert b["repayment_target"]["label"] == "Scheduled total repayment"
    assert b["repayment_target"]["amount"]["vnd"] == b["total_repaid_mean"]["vnd"]
    assert "no cap" in b["repayment_target"]["basis"].lower()
    assert isinstance(b["repayment_target"]["amount"]["vnd"], int)

    a = by["FIX-A"]
    assert a["repayment_target"]["label"] == "Contractual cap"
    assert a["repayment_target"]["amount"]["vnd"] == a["contractual_cap"]["vnd"]

    html = open(LAB_HTML, encoding="utf-8").read()
    assert '"no cap"' not in html, "the page still prints a bare 'no cap'"


def test_incomplete_closure_contracts_use_the_agreed_wording():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "Undefined — repayment incomplete" in html
    assert "Not completed within 24 months" in html
    d = client.get("/api/lab/comparison/closure_m7").json()
    rbf = next(a for a in d["arms"] if a["id"] == "RBF-ILL")
    assert rbf["effective_apr"] is None
    assert rbf["apr_undefined_reason"] == "repayment incomplete"


def test_network_failure_has_its_own_message():
    html = open(LAB_HTML, encoding="utf-8").read()
    assert "could not be reached" in html.lower()
