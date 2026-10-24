"""Homepage/redesign guards, distinct from the legacy prototype's checks.

The Node cases execute the actual overview script with a minimal fake DOM.
They are logic tests, not browser, layout or assistive-technology evidence.
The routing fixture follows this suite's TestClient convention: conftest points
the application at a throwaway database and empty model directory before import.
"""
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.words = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, value):
        self.words.append(value)

    @property
    def text(self):
        return " ".join(" ".join(self.words).split()).lower()

    @property
    def ids(self):
        return {attrs["id"] for _, attrs in self.elements if "id" in attrs}


@pytest.fixture(scope="module")
def homepage():
    return Document((FRONTEND / "index.html").read_text())


def test_actual_homepage_is_protected_by_public_disclosures(homepage):
    """Moving prototype tests must not silently abandon the new landing page."""
    assert "not a lending service" in homepage.text
    assert "independent research" in homepage.text
    assert "neither path has measured predictive validity" in homepage.text
    assert "synthetic benchmark remains withdrawn" in homepage.text
    assert "scoring is not used to generate the simulation lab" in homepage.text
    assert "no credit recommendation" in homepage.text


def test_scope_keeps_proposed_tool_separate_from_available_prototype(homepage):
    assert "proposed / not available" in homepage.text
    assert "no ingestion service or lender pilot is offered here" in homepage.text
    assert "construction awaits a reviewed specification" in homepage.text
    assert "real data requires separate permissions and security review" in homepage.text
    assert "observed payments kept distinct from hypothetical cash flows" in homepage.text


def test_homepage_does_not_collect_merchant_data(homepage):
    assert not any(tag in {"form", "input", "textarea", "select"}
                   for tag, _ in homepage.elements)
    assert "use synthetic examples only" in homepage.text
    assert "store records" in homepage.text and "administrator notifications" in homepage.text
    assert "please do not send confidential merchant records" in homepage.text


def test_conceptual_diagram_is_not_presented_as_registered_output(homepage):
    assert "conceptual illustration, not research output" in homepage.text
    assert "indexed to its own starting level" in homepage.text
    assert "excludes cap clipping, rounding and settlement" in homepage.text
    assert "fixed net-sales/gmv ratio is assumed" in homepage.text


def test_homepage_has_no_inline_api_or_scoring_dependencies(homepage):
    scripts = [attrs for tag, attrs in homepage.elements if tag == "script"]
    assert scripts == [{"src": "/overview.js", "defer": None}]
    assert not any(name.startswith("on") for _, attrs in homepage.elements for name in attrs)
    script = (FRONTEND / "overview.js").read_text()
    for pattern in (r"\bfetch\s*\(", r"\bXMLHttpRequest\b", r"\bWebSocket\b",
                    r"\bsendBeacon\s*\(", r"\b(?:local|session)Storage\b",
                    r"/api/", r"\bimport\s", r"\brequire\s*\("):
        assert not re.search(pattern, script), pattern


def test_local_assets_exist_and_homepage_fragments_resolve(homepage):
    for tag, attrs in homepage.elements:
        href = attrs.get("href", "")
        if tag == "a" and href.startswith("#"):
            assert href[1:] in homepage.ids, href
        source = attrs.get("src") if tag == "script" else attrs.get("href") if tag == "link" else None
        if source:
            assert source.startswith("/") and not source.startswith("//"), source
            assert (FRONTEND / source.lstrip("/")).is_file(), source
    css = (FRONTEND / "institutional.css").read_text()
    for path in re.findall(r"url\(['\"]?([^)'\"]+)", css):
        assert path.startswith("/") and not path.startswith("//"), path
        assert (FRONTEND / path.lstrip("/")).is_file(), path


def test_homepage_links_to_existing_lab_sections(homepage):
    lab = Document((FRONTEND / "lab.html").read_text())
    links = [a["href"] for tag, a in homepage.elements
             if tag == "a" and a.get("href", "").startswith("/lab#")]
    assert links
    for link in links:
        assert link.partition("#")[2] in lab.ids, link


def test_prototype_metadata_describes_a_demonstration_not_a_recommendation():
    page = Document((FRONTEND / "demo.html").read_text())
    metadata = {a.get("property", a.get("name")): a.get("content", "")
                for tag, a in page.elements if tag == "meta"}
    assert "Interactive research prototype" in metadata["og:title"]
    assert metadata["og:url"].endswith("/demo.html")
    assert "unvalidated" in metadata["twitter:description"].lower()
    for value in metadata.values():
        assert "underwriting support" not in value.lower()
        assert "financing recommendations" not in value.lower()
        assert "<br>" not in value


def test_synthetic_entry_fields_have_associated_labels():
    page = Document((FRONTEND / "demo.html").read_text())
    labels = {a.get("for") for tag, a in page.elements if tag == "label"}
    fields = {a["id"] for tag, a in page.elements
              if tag in {"input", "select"} and a.get("id", "").startswith("f_")}
    assert len(fields) == 12
    assert fields <= labels


def test_full_example_and_dashboard_keep_demonstration_boundaries():
    source = (FRONTEND / "demo.html").read_text()
    result_source = source.split('<div id="page-result"', 1)[1].split('<div id="page-dashboard"', 1)[0]
    result = Document(result_source).text
    for label in ("demo score — unvalidated", "not a prediction of repayment or a credit recommendation",
                  "illustrative factors", "illustrative positive signals", "additional information",
                  "not a loan offer", "new synthetic example"):
        assert label in result
    for retired in ("pd score", "why this decision?", "approval drivers", "what would improve this offer",
                    "new application", "lender dashboard"):
        assert retired not in Document(source).text
    assert "Prototype dashboard" in source
    dashboard_source = source.split('<div id="page-dashboard"', 1)[1].split('<div id="page-privacy"', 1)[0]
    dashboard = Document(dashboard_source).text
    for label in ("legacy demo limit", "sum of demo limits", "unvalidated demonstration records",
                  "separate from the financing terms", "illustrative tier distribution"):
        assert label in dashboard
    # Label clarification must not substitute a different measure or change the
    # existing API bindings, including the legacy amounts in stored records.
    assert "document.getElementById('st-exposure').textContent=fmtVND(stats.total_exposure)" in source
    assert '<td class="t-num">${fmtVND(s.credit_limit)}</td>' in source
    # The scorer's legacy rationale uses a different advance rule. Neither
    # result surface may republish it as the financing explanation.
    assert "textContent=s.reasoning" not in source
    assert "textContent=d.reasoning" not in source
    assert "renderFindings(financing.risk_findings||[])" in source
    assert "renderIntegrity(s.integrity)" in source
    assert "do not model default or establish affordability" in result


@pytest.fixture(scope="module")
def static_client():
    import main
    return TestClient(main.app)


@pytest.mark.parametrize("path,expected", [
    ("", "index.html"), ("apply", "index.html"),
    ("dashboard", "index.html"), ("pricing", "index.html"),
    ("demo.html", "demo.html"), ("lab.html", "lab.html"), ("lab", "lab.html"),
    ("overview.js", "overview.js"), ("institutional.css", "institutional.css"),
    ("rbf-mark.svg", "rbf-mark.svg"),
])
def test_production_static_responder_serves_redesign_files(static_client, path, expected):
    response = static_client.get("/" + path)
    assert response.status_code == 200
    assert response.content == (FRONTEND / expected).read_bytes()


def test_static_responder_still_rejects_unknown_paths(static_client):
    assert static_client.get("/no-such-redesign-route").status_code == 404


# Minimal fake elements record only behaviour this script uses. Network/storage
# APIs throw, so the exercised overview paths cannot silently acquire a backend
# dependency. This is deliberately not a simulated accessibility tree.
NODE_HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const config = JSON.parse(process.env.RBF_OVERVIEW_CASE);
const source = fs.readFileSync(process.env.RBF_OVERVIEW_SOURCE, 'utf8');
function element(attrs={}) {
  return { attrs:{...attrs}, hidden: 'hidden' in attrs, textContent:'', listeners:{},
    dataset: Object.fromEntries(Object.entries(attrs).filter(([k])=>k.startsWith('data-')).map(([k,v])=>[k.slice(5),v])),
    setAttribute(k,v){ this.attrs[k]=String(v); }, getAttribute(k){ return this.attrs[k]; },
    addEventListener(k,fn){ this.listeners[k]=fn; }, focus(){ this.focused=true; } };
}
const nodes = Object.fromEntries(config.elements.filter(x=>x[1].id).map(([tag,a])=>[a.id,element(a)]));
const shapes = config.elements.filter(x=>x[1]['data-shape']).map(([tag,a])=>element(a));
const events={}; const media=element(); const redirects=[];
const forbidden=()=>{ throw Error('Overview must not access network or storage'); };
const document={ getElementById(id){ assert.ok(nodes[id],id); return nodes[id]; },
  querySelectorAll(q){ assert.equal(q,'[data-shape]'); return shapes; },
  addEventListener(k,fn){ events[k]=fn; } };
const context={document, location:{pathname:config.path||'/',search:config.search||'',replace(x){redirects.push(x);}},
  URLSearchParams, matchMedia(){return media;}, fetch:forbidden, XMLHttpRequest:forbidden,
  WebSocket:forbidden, localStorage:new Proxy({}, {get:forbidden}),
  sessionStorage:new Proxy({}, {get:forbidden}), navigator:{sendBeacon:forbidden}};
vm.runInNewContext(source,context);
if(config.action==='redirect'){
  assert.deepEqual(redirects,[config.expected]);
}else{
  assert.deepEqual(redirects,[]);
  const toggle=nodes['menu-toggle'],menu=nodes['site-menu'];
  assert.equal(menu.hidden,true);
  toggle.listeners.click();
  assert.equal(menu.hidden,false); assert.equal(toggle.attrs['aria-expanded'],'true');
  events.keydown({key:'Escape'});
  assert.equal(menu.hidden,true); assert.equal(toggle.attrs['aria-expanded'],'false'); assert.equal(toggle.focused,true);
  toggle.listeners.click(); menu.listeners.click({target:{closest(){return {};}}});
  assert.equal(menu.hidden,true);
  toggle.listeners.click(); media.listeners.change(); assert.equal(menu.hidden,true);
  const expected={steady:'40',decline:'100',interruption:'120'};
  for(const button of shapes){
    button.listeners.click();
    assert.equal(nodes['chart-end'].attrs.cy,expected[button.dataset.shape]);
    assert.ok(nodes['chart-share'].attrs.d.startsWith('M30 40'));
    assert.ok(nodes['chart-area'].attrs.d.endsWith('L490 205L30 205Z'));
    assert.equal(shapes.filter(b=>b.attrs['aria-pressed']==='true').length,1);
    assert.equal(button.attrs['aria-pressed'],'true');
    assert.ok(nodes['chart-title'].textContent.startsWith('Conceptual'));
    assert.ok(nodes['shape-description'].textContent.length>30);
  }
  assert.ok(nodes['shape-description'].textContent.includes('not assured'));
}
"""


def run_overview_case(homepage, **case):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node unavailable: overview logic tests not executed")
    environment = {**os.environ, "RBF_OVERVIEW_SOURCE": str(FRONTEND / "overview.js"),
                   "RBF_OVERVIEW_CASE": json.dumps({"elements": homepage.elements, **case})}
    result = subprocess.run([node, "-e", NODE_HARNESS], env=environment,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


def test_overview_menu_and_diagram_logic_without_network(homepage):
    run_overview_case(homepage, action="interactions")


@pytest.mark.parametrize("path,search,expected", [
    ("/apply", "", "/demo.html#apply"),
    ("/dashboard", "?source=bookmark", "/demo.html?source=bookmark#dashboard"),
    ("/pricing/", "", "/demo.html#pricing"),
    ("/", "?session_id=cs_synthetic", "/demo.html?session_id=cs_synthetic"),
])
def test_overview_legacy_entry_redirect_logic(homepage, path, search, expected):
    run_overview_case(homepage, action="redirect", path=path, search=search, expected=expected)
