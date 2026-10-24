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
  const shapes = {
    steady: { y: [40,40,40,40,40,40], text: 'With revenue unchanged, both indexed payments stay level. This diagram does not compare their monetary amounts.', title: 'Conceptual steady revenue: both indexed payment series stay level.' },
    decline: { y: [40,40,100,100,100,100], text: 'As revenue falls, an uncapped revenue-share payment falls with it. A fixed payment stays unchanged.', title: 'Conceptual decline: revenue-share payments fall with revenue; the fixed payment does not.' },
    interruption: { y: [40,40,205,205,120,120], text: 'With eligible revenue at zero, the revenue-share payment is zero. Restarting revenue can restart payments; reaching the repayment target is not assured.', title: 'Conceptual interruption: the revenue-share payment falls to zero before partially recovering; the fixed obligation stays level.' }
  };
  const points = [30,122,214,306,398,490];
  document.querySelectorAll('[data-shape]').forEach(button => {
    button.addEventListener('click', () => {
      const shape = shapes[button.dataset.shape];
      const line = shape.y.map((y,i) => (i ? 'L' : 'M') + points[i] + ' ' + y).join('');
      document.getElementById('chart-share').setAttribute('d', line);
      document.getElementById('chart-area').setAttribute('d', line + 'L490 205L30 205Z');
      document.getElementById('chart-end').setAttribute('cy', shape.y[5]);
      document.getElementById('shape-description').textContent = shape.text;
      document.getElementById('chart-title').textContent = shape.title;
      document.querySelectorAll('[data-shape]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    });
  });
})();
