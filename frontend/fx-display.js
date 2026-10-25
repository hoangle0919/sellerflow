/* Approximate USD equivalents — presentation only.
 *
 * THE RULE THIS FILE EXISTS TO ENFORCE: the VND value is authoritative and is
 * never derived from, replaced by, or round-tripped through its USD display.
 * Callers pass the ORIGINAL INTEGER VND, never a formatted string scraped from
 * the DOM. Locale formatting differs between languages; the mathematical amount
 * does not, and parsing "185.000.000" back out of a page is how that invariant
 * gets broken.
 *
 * ONE SNAPSHOT PER RENDERED GROUP. A result panel takes a single quote and
 * converts every figure in it with that one rate, so the numbers reconcile with
 * each other and with the single reference date shown beside them. A refresh
 * replaces the whole group atomically. It never changes a VND figure.
 *
 * Converted totals can differ by a cent or two from the sum of individually
 * rounded USD lines. That is explained in the UI, not corrected by adjusting
 * a VND total.
 */
(function (global) {
  'use strict';

  var PREF_KEY = 'rbf.amountDisplay';   // 'vnd' | 'dual'
  var quote = null;                      // last /api/fx payload
  var mode = 'dual';

  function t(key, vars) {
    return (global.RBF_I18N && global.RBF_I18N.t(key, vars)) || '';
  }

  function readPref() {
    try {
      var v = global.localStorage.getItem(PREF_KEY);
      return (v === 'vnd' || v === 'dual') ? v : 'dual';
    } catch (e) { return 'dual'; }
  }
  function writePref(v) {
    try { global.localStorage.setItem(PREF_KEY, v); } catch (e) { /* ignore */ }
  }

  /* Integer VND in, decimal string out. Mirrors backend/fx.py::approximate_usd
   * (vnd / R, half-up to cents) so the two layers agree; the backend remains
   * the definition of record. */
  function toUsd(vnd) {
    if (!quote || !quote.vnd_per_usd) return null;
    var r = Number(quote.vnd_per_usd);
    if (!isFinite(r) || r <= 0) return null;
    var n = Number(vnd);
    if (!isFinite(n)) return null;
    return (Math.round((n / r) * 100) / 100).toLocaleString(
      global.RBF_I18N && global.RBF_I18N.lang === 'vi' ? 'vi-VN' : 'en-US',
      { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function usable() {
    return !!quote && (quote.status === 'ok' || quote.status === 'stale');
  }

  /** Secondary line for one amount, or '' when USD must be suppressed. */
  function line(vnd) {
    if (mode !== 'dual' || !usable()) return '';
    var usd = toUsd(vnd);
    return usd === null ? '' : t('fx.approx', { usd: usd });
  }

  /** The dated provenance note that must accompany any USD figure. */
  function provenance() {
    if (!usable()) return { text: t('fx.unavailable'), warn: true };
    var parts = [t('fx.refLine', { date: quote.reference_date })];
    if (quote.status === 'stale') parts.push(t('fx.stale', { days: quote.reference_age_days }));
    if (quote.refresh_failed) parts.push(t('fx.cached'));
    return { text: parts.join(' · '), warn: quote.status === 'stale' || quote.refresh_failed };
  }

  function refresh() {
    return fetch('/api/fx', { credentials: 'omit' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (q) { quote = q; render(); return q; })
      .catch(function () { quote = null; render(); return null; });
  }

  /* Declarative binding: an element carrying data-vnd="<integer>" gets a
   * sibling .fx-line. The integer attribute is the source of truth, so a
   * language switch re-renders from the number and not from the rendered text. */
  function render() {
    global.document.querySelectorAll('[data-vnd]').forEach(function (el) {
      var raw = el.getAttribute('data-vnd');
      var sib = el.nextElementSibling;
      var has = sib && sib.classList && sib.classList.contains('fx-line');
      var txt = line(raw);
      if (!txt) { if (has) sib.remove(); return; }
      if (!has) {
        sib = global.document.createElement('span');
        sib.className = 'fx-line';
        el.insertAdjacentElement('afterend', sib);
      }
      sib.textContent = txt;
    });

    var p = provenance();
    global.document.querySelectorAll('[data-fx-note]').forEach(function (el) {
      el.textContent = (mode === 'dual') ? p.text : '';
      el.classList.toggle('fx-warn', !!p.warn && mode === 'dual');
    });

    global.document.querySelectorAll('[data-fx-option]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-fx-option') === mode ? 'true' : 'false');
    });
  }

  function setMode(next) {
    if (next !== 'vnd' && next !== 'dual') return;
    mode = next;
    writePref(next);
    render();
  }

  function init() {
    mode = readPref();
    global.document.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-fx-option]') : null;
      if (b) { e.preventDefault(); setMode(b.getAttribute('data-fx-option')); }
    });
    // Labels are language-dependent; the rate is not. Re-render, do not refetch.
    global.addEventListener('rbf:languagechange', render);
    refresh();
  }

  global.RBF_FX = {
    line: line, provenance: provenance, refresh: refresh, render: render,
    setMode: setMode, get mode() { return mode; }, get quote() { return quote; }
  };

  if (global.document.readyState === 'loading') {
    global.document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})(window);
