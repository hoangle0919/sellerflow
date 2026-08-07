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
    assert "prov-grid" in html and "foot-spec" in html


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
    assert "equal effective cost" in eq["name"].lower()
    assert "illustrative" in ill["name"].lower()
    # The illustrative arm must say it is not a market price.
    assert "not a recommended" in ill["note"].lower() or "illustrative" in ill["note"].lower()
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
    assert "not universally" in caveats


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
    assert "calibrated on the deterministic reference path" in caveats
