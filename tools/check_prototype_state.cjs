/* Node unit tests of the actual prototype state functions, using a fake DOM.
 * No browser, network, financial calculation or accessibility claim is made.
 * Run: node --test tools/check_prototype_state.cjs
 */
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');

const source = readFileSync(join(__dirname, '../frontend/demo.html'), 'utf8');
const start = source.indexOf('const HERO_FIXED=');
const end = source.indexOf('/* Premium scroll-reveal', start);
assert(start > 0 && end > start, 'prototype state-function boundaries exist');
const hero = source.slice(start, end);

function setup() {
  const nodes = new Map();
  const get = id => {
    if (!nodes.has(id)) nodes.set(id, {
      value: '1', min: '0', max: '1000', textContent: '', innerHTML: '',
      hidden: false, disabled: false, style: {}, className: '',
      classList: { add() {}, remove() {}, toggle() {} }, addEventListener() {},
    });
    return nodes.get(id);
  };
  const values = { 'hc-rev':185, 'hc-growth':22, 'hc-return':2.8,
    'hc-rating':4.9, 'hc-late':1.8, 'hc-days':680 };
  Object.entries(values).forEach(([id, value]) => { get(id).value = value; });
  const ranges = Object.keys(values).map(get);
  const presets = [{}, {}, {}, {}].map(() => ({ classList: { toggle() {}, remove() {} } }));
  const requests = [], results = [];
  const context = vm.createContext({
    document: { getElementById:get, querySelectorAll:selector => selector.includes('input') ? ranges : presets },
    URLSearchParams, performance: { now:() => 100 },
    fmtVND:String, pct:String, signed:String,
    VERDICT: { APPROVED:'Illustrative low risk' },
    callAPI:route => new Promise(resolve => requests.push({route, resolve})),
    clearTimeout() {}, setTimeout:() => 1,
    renderResult:value => results.push(value), go() {}, window: { scrollTo() {} },
  });
  vm.runInContext(hero, context);
  const run = code => vm.runInContext(code, context);
  return { get, run, requests, results };
}
function payload(amount = 100) {
  return { decision:'APPROVED', risk_tier:'LOW', pd_score:0.1,
    financing:{ structure:{ recommended_amount:amount, repayment_cap:120,
      remittance_pct:0.1, collection_base:'net_of_returns', base_case_duration_months:12,
      effective_apr_base_case:0.2 } }, signals:{}, reasoning:'Synthetic example' };
}
async function finish(request, value) {
  request.resolve(value);
  await new Promise(resolve => setImmediate(resolve));
}

test('initial load shows no fabricated result and cannot open full details', () => {
  const s = setup();
  assert(s.get('hero-full-link').disabled);
  assert.equal(s.get('hd-limit').textContent, '—');
  s.run('heroViewFull()');
  assert.equal(s.results.length, 0);
});

test('successful response enables the matching full example', async () => {
  const s = setup();
  await finish(s.requests[0], payload(100));
  assert.equal(s.get('hd-limit').textContent, '100');
  assert.equal(s.get('hero-full-link').disabled, false);
  s.run('heroViewFull()');
  assert.equal(s.results[0].shop_name, 'Thời Trang Linh Chi');
});

test('preset immediately invalidates the previous result while request waits', async () => {
  const s = setup();
  await finish(s.requests[0], payload(100));
  s.run("heroApplyPreset('growth', null)");
  assert(s.get('hero-full-link').disabled);
  assert.equal(s.get('hd-limit').textContent, '—');
  s.run('heroViewFull()');
  assert.equal(s.results.length, 0);
  await finish(s.requests[1], payload(200));
  s.run('heroViewFull()');
  assert.equal(s.results[0].shop_name, 'GadgetHub VN');
  assert.equal(s.results[0].financing.structure.recommended_amount, 200);
});

test('a stale in-flight response is dropped before a pending preset renders', async () => {
  const s = setup();
  s.run("heroApplyPreset('volatile', null)");
  await finish(s.requests[0], payload(100));
  assert.equal(s.get('hd-limit').textContent, '—');
  assert(s.get('hero-full-link').disabled);
  assert.equal(s.requests.length, 2);
  await finish(s.requests[1], payload(300));
  s.run('heroViewFull()');
  assert.equal(s.results[0].shop_name, 'Mộc Decor');
  assert.equal(s.results[0].financing.structure.recommended_amount, 300);
});

test('slider change clears a prior success immediately', async () => {
  const s = setup();
  await finish(s.requests[0], payload());
  s.get('hc-rev').value = 50;
  s.run('heroOnInput()');
  assert(s.get('hero-full-link').disabled);
  assert.equal(s.get('hd-limit').textContent, '—');
});

test('unavailable and malformed responses render a fixed honest failure state', async () => {
  for (const response of [null, {}, {__rate_limited:true}, {decision:'APPROVED'}]) {
    const s = setup();
    await finish(s.requests[0], response);
    assert.equal(s.get('hd-word').textContent, 'Preview unavailable');
    assert(s.get('hero-full-link').disabled);
    assert.equal(s.get('hero-retry').hidden, false);
    assert.match(s.get('hero-foot').textContent, /No example figures are shown/);
  }
});

test('render exceptions clear partial values and replace the footer without leaking detail', async () => {
  const s = setup();
  const response = payload();
  Object.defineProperty(response, 'signals', { get() { throw new Error('PRIVATE_RENDER_ERROR'); } });
  await finish(s.requests[0], response);
  assert.equal(s.get('hd-limit').textContent, '—');
  assert.equal(s.get('hd-word').textContent, 'Preview unavailable');
  assert.match(s.get('hero-foot').textContent, /No example figures are shown/);
  assert(!s.get('hero-foot').textContent.includes('PRIVATE_RENDER_ERROR'));
  assert(s.get('hero-full-link').disabled);
});
