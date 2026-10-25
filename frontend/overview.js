/* Presentation only. No scorer, payment arithmetic, storage or API requests. */
(() => {
  'use strict';
  // Preserve established SPA entry routes without moving or changing API routes.
  const route = location.pathname.replace(/^\/+|\/+$/g, '');
  if (['apply', 'dashboard', 'pricing'].includes(route)) {
    location.replace('/demo.html' + location.search + '#' + (route === 'pricing' ? 'pricing' : route));
    return;
  }
  if (new URLSearchParams(location.search).has('session_id')) {
    location.replace('/demo.html' + location.search);
    return;
  }
  const menuButton = document.getElementById('menu-toggle');
  const menu = document.getElementById('site-menu');
  function closeMenu(restoreFocus = false) {
    menu.hidden = true;
    menuButton.setAttribute('aria-expanded', 'false');
    if (restoreFocus) menuButton.focus();
  }
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menu.hidden = !open;
    menuButton.setAttribute('aria-expanded', String(open));
  });
  menu.addEventListener('click', e => { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !menu.hidden) closeMenu(true);
  });
  const wide = matchMedia('(min-width: 821px)');
  wide.addEventListener('change', () => closeMenu());

  // Fixed explanatory SVG coordinates, not a financial model or research data.
  // Geometry stays here; the copy lives in the catalogues so both languages
  // read naturally. The English strings are unchanged -- see i18n/en.json
  // keys figure.shape.*.desc and figure.chart.title.*.
  const shapes = {
    steady:       { y: [40,40,40,40,40,40] },
    decline:      { y: [40,40,100,100,100,100] },
    interruption: { y: [40,40,205,205,120,120] }
  };
  let activeShape = 'decline';   // matches the markup's pressed button

  function copy(key) {
    return (window.RBF_I18N && window.RBF_I18N.t(key)) || '';
  }

  function paintCopy(name) {
    const desc = copy('figure.shape.' + name + '.desc');
    const title = copy('figure.chart.title.' + name);
    const d = document.getElementById('shape-description');
    const t = document.getElementById('chart-title');
    // Point the declarative binding at the active shape so a later language
    // switch re-renders THIS shape's copy, not the one the page loaded with.
    if (desc) { d.textContent = desc; d.setAttribute('data-i18n', 'figure.shape.' + name + '.desc'); }
    if (title) { t.textContent = title; t.setAttribute('data-i18n', 'figure.chart.title.' + name); }
  }
  const points = [30,122,214,306,398,490];
  document.querySelectorAll('[data-shape]').forEach(button => {
    button.addEventListener('click', () => {
      const name = button.dataset.shape;
      const shape = shapes[name];
      activeShape = name;
      const line = shape.y.map((y,i) => (i ? 'L' : 'M') + points[i] + ' ' + y).join('');
      document.getElementById('chart-share').setAttribute('d', line);
      document.getElementById('chart-area').setAttribute('d', line + 'L490 205L30 205Z');
      document.getElementById('chart-end').setAttribute('cy', shape.y[5]);
      paintCopy(name);
      document.querySelectorAll('[data-shape]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    });
  });

  // The selected shape must survive a language switch: re-paint its copy
  // rather than letting the page fall back to the shape it loaded with.
  window.addEventListener('rbf:languagechange', () => paintCopy(activeShape));
})();
