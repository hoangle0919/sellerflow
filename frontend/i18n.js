/* RBF bilingual runtime — stable semantic keys, two catalogues, no DOM-wide
 * text replacement and no machine translation at runtime.
 *
 * Switching language re-applies a catalogue over the EXISTING DOM. Nothing
 * reloads and nothing re-renders from scratch, so form values, selected
 * scenarios, open panels, scroll position and focus survive a switch for free.
 * That is the reason for this design, not an incidental property of it.
 *
 * Markup contract:
 *   data-i18n="key"                         -> textContent
 *   data-i18n-html="key"                    -> innerHTML (catalogue strings
 *                                              only; never user input)
 *   data-i18n-attr="aria-label:key|title:k" -> attributes
 *
 * Dynamic copy (results, validation, errors) calls RBF_I18N.t(key, vars) and
 * re-renders on the 'rbf:languagechange' event. A string that only exists at
 * runtime still needs a key in both catalogues — see tools/check_i18n.py,
 * which fails on any key present in one catalogue and missing from the other.
 */
(function (global) {
  'use strict';

  var SUPPORTED = ['en', 'vi'];
  var DEFAULT = 'en';
  var STORAGE_KEY = 'rbf.lang';
  var catalogues = {};
  var current = DEFAULT;

  function isSupported(v) { return SUPPORTED.indexOf(v) !== -1; }

  /* Storage can throw outright in private mode or with site data blocked.
   * A language preference is a convenience; it must never break the page. */
  function readStored() {
    try {
      var v = global.localStorage.getItem(STORAGE_KEY);
      return isSupported(v) ? v : null;
    } catch (e) { return null; }
  }
  function writeStored(v) {
    try { global.localStorage.setItem(STORAGE_KEY, v); } catch (e) { /* ignore */ }
  }

  /* Resolution order is fixed: an explicit URL preference beats a saved one,
   * so a copied link carries its language to someone else's browser. */
  function resolveInitial() {
    var p = null;
    try { p = new URLSearchParams(global.location.search).get('lang'); } catch (e) { p = null; }
    if (isSupported(p)) return p;
    var s = readStored();
    if (s) return s;
    return DEFAULT;
  }

  function fetchCatalogue(lang) {
    if (catalogues[lang]) return Promise.resolve(catalogues[lang]);
    return fetch('/i18n/' + lang + '.json', { credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('catalogue ' + lang + ' ' + r.status);
        return r.json();
      })
      .then(function (c) { catalogues[lang] = c; return c; });
  }

  function lookup(key, lang) {
    var c = catalogues[lang];
    if (c && Object.prototype.hasOwnProperty.call(c, key)) return c[key];
    /* Fall back to English rather than rendering a raw key at a reader. A
     * missing Vietnamese string is a catalogue defect caught by the parity
     * check, not something to surface as "nav.research" on a live page. */
    var en = catalogues[DEFAULT];
    if (en && Object.prototype.hasOwnProperty.call(en, key)) return en[key];
    return null;
  }

  function t(key, vars) {
    var s = lookup(key, current);
    if (s === null) return '';
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        s = s.split('{' + k + '}').join(String(vars[k]));
      });
    }
    return s;
  }

  function applyTo(root) {
    var scope = root || global.document;

    scope.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = lookup(el.getAttribute('data-i18n'), current);
      if (v !== null) el.textContent = v;
    });

    scope.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var v = lookup(el.getAttribute('data-i18n-html'), current);
      if (v !== null) el.innerHTML = v;   // catalogue-authored markup only
    });

    scope.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split('|').forEach(function (pair) {
        var i = pair.indexOf(':');
        if (i < 1) return;
        var attr = pair.slice(0, i).trim();
        var v = lookup(pair.slice(i + 1).trim(), current);
        if (v !== null) el.setAttribute(attr, v);
      });
    });
  }

  function applyDocumentMetadata() {
    var d = global.document;
    d.documentElement.setAttribute('lang', current);
    var title = lookup('meta.title', current);
    if (title !== null) d.title = title;
    var desc = lookup('meta.description', current);
    if (desc !== null) {
      var m = d.querySelector('meta[name="description"]');
      if (m) m.setAttribute('content', desc);
    }
  }

  function syncToggle() {
    global.document.querySelectorAll('[data-lang-option]').forEach(function (b) {
      var on = b.getAttribute('data-lang-option') === current;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) b.setAttribute('aria-current', 'true');
      else b.removeAttribute('aria-current');
    });
  }

  /* Keep the address bar truthful without adding a history entry per toggle:
   * replaceState, so Back still goes where the reader expects. */
  function syncUrl() {
    try {
      var u = new URL(global.location.href);
      if (current === DEFAULT) u.searchParams.delete('lang');
      else u.searchParams.set('lang', current);
      global.history.replaceState(global.history.state, '', u.toString());
    } catch (e) { /* ignore */ }
  }

  function set(lang, opts) {
    if (!isSupported(lang) || lang === current) return Promise.resolve(current);
    /* Translated copy is a different length, so the document reflows and the
     * browser clamps the scroll offset. Capture and restore it, and keep focus
     * where the reader left it. Exactness is not always possible -- if the page
     * becomes shorter than the saved offset the restore is clamped too -- but
     * the common case should not move at all. */
    var savedScroll = global.scrollY;
    var savedFocus = global.document.activeElement;

    return fetchCatalogue(lang).then(function () {
      current = lang;
      if (!opts || opts.persist !== false) writeStored(lang);
      applyTo();
      applyDocumentMetadata();
      syncToggle();
      syncUrl();
      global.dispatchEvent(new CustomEvent('rbf:languagechange', { detail: { lang: current } }));
      if (global.scrollY !== savedScroll) global.scrollTo(0, savedScroll);
      if (savedFocus && savedFocus !== global.document.activeElement &&
          global.document.contains(savedFocus) && savedFocus.focus) {
        savedFocus.focus({ preventScroll: true });
      }
      return current;
    }).catch(function () { return current; });   // keep the page usable
  }

  function wireToggle() {
    global.document.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-lang-option]') : null;
      if (!b) return;
      e.preventDefault();
      set(b.getAttribute('data-lang-option'));
    });
  }

  function init() {
    var want = resolveInitial();
    /* English is already in the markup, so load its catalogue too: dynamic
     * strings need lookups even when no switch has happened. */
    var needed = want === DEFAULT ? [DEFAULT] : [DEFAULT, want];
    return Promise.all(needed.map(fetchCatalogue)).then(function () {
      current = want;
      applyTo();
      applyDocumentMetadata();
      syncToggle();
      wireToggle();
      global.dispatchEvent(new CustomEvent('rbf:languagechange', { detail: { lang: current } }));
      return current;
    }).catch(function () { wireToggle(); return current; });
  }

  global.RBF_I18N = {
    t: t,
    set: set,
    apply: applyTo,
    get lang() { return current; },
    supported: SUPPORTED.slice(),
    ready: null
  };

  if (global.document.readyState === 'loading') {
    global.document.addEventListener('DOMContentLoaded', function () { global.RBF_I18N.ready = init(); });
  } else {
    global.RBF_I18N.ready = init();
  }
})(window);
