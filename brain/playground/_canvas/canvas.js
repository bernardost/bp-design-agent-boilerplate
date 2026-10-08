/* canvas.js — gives a piece file its controls, its version menu, and optionally a canvas.

   A piece declares `window.PIECE` and a `<template id="screen">` holding the design, and
   includes this file last. Everything else is derived from that declaration, so a piece
   carries its design and the list of what can be tuned, and nothing about how the chrome works.

     window.PIECE = {
       title:   'Checkout — summary panel',
       controls:[{group:'Colour', key:'accent', label:'Accent', kind:'color', value:'#1f4fd8', css:'--accent'},
                 {group:'Type',   key:'body',   label:'Body',   kind:'range', value:16, min:14, max:20, unit:'px', css:'--step-0'},
                 {group:'Layout', key:'density',label:'Density',kind:'select',value:'comfortable', options:['comfortable','compact'], attr:'data-density'},
                 {group:'State',  key:'empty',  label:'Empty',  kind:'toggle',value:false, attr:'data-empty'}],
       states:  {'Default':{}, 'Empty cart':{empty:true}},
       mount(root, board, values){},          // optional: wire up interactivity, query inside root only
       // boards: [{id:'desktop', width:1440}, {id:'mobile', width:390, height:844, scroll:true}],
     };

   Two modes:

   PAGE (default, no `boards`)  The design is mounted straight into <body>. Resize the window for
     widths; write `@media` breakpoints like production CSS. The only chrome is a tab in the
     corner that opens the panel.
   CANVAS (`boards` declared)  Artboards side by side, each a CSS container named `screen`, with
     a bar for toggling boards. Breakpoints must then be `@container screen (…)`.

   CASES: a piece holding several components or states stacks them. Any element in the
   template carrying `data-case="Name"` (and optionally `data-note="…"`) gets a labelled rule
   above it and a line in the panel's case list. A case may carry state attributes itself —
   `<section data-case="Empty" data-empty>` — so one piece shows several states at once.

   How a value reaches the design, in both modes:
     css   → a custom property set on <html>:                      var(--accent)
     attr  → an attribute on the design root — <html> in page mode, each artboard in canvas
             mode — so a selector written `[data-density="compact"] …` works in both.
             A toggle sets the attribute when true and removes it when false.
     apply → apply(value, roots, values) for anything those two cannot express

   `kind`: color · range · select · toggle · text. A select is segmented while its labels fit
   and a dropdown otherwise.

   Values persist per piece version in localStorage, and the URL carries the non-default ones
   so a link opens on an exact view. `C` toggles the panel, `R` replays — replay re-mounts the
   design, which restarts entrance animations and anything in mount(). Copy settings puts the
   current values on the clipboard as JSON: that JSON is the handoff, and the agent bakes it
   into the defaults of the next version. */

(function () {
  'use strict';
  const PIECE = window.PIECE || {};
  const PG = window.PLAYGROUND || null;          // written by brain/playground.py
  const file = decodeURIComponent(location.pathname.split('/').pop() || '');
  const KEY = 'pg:' + (PG && PG.slug ? PG.slug + '/' : '') + file;
  const controls = PIECE.controls || [];
  const states = PIECE.states || {};
  const boards = PIECE.boards || [];
  const CANVAS = boards.length > 0;
  const defaults = Object.fromEntries(controls.map(c => [c.key, c.value]));
  const values = Object.assign({}, defaults);
  let shown = Object.fromEntries(boards.map(b => [b.id, b.hidden !== true]));

  // ── stored and linked state ─────────────────────────────────────────
  try {
    const s = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (s.values) for (const k in s.values) if (k in defaults) values[k] = s.values[k];
    if (s.boards) shown = Object.assign(shown, s.boards);
  } catch (e) { /* no storage: defaults */ }
  const q = new URLSearchParams(location.search);
  for (const c of controls) {
    if (!q.has(c.key)) continue;
    const raw = q.get(c.key);
    values[c.key] = c.kind === 'toggle' ? raw !== '0' && raw !== 'false'
      : c.kind === 'range' ? Number(raw) : raw;
  }
  if (CANVAS && q.has('boards')) {
    const on = q.get('boards').split(',');
    for (const b of boards) shown[b.id] = on.includes(b.id);
  }

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify({ values, boards: shown })); } catch (e) { /* ignore */ }
    const p = new URLSearchParams();
    for (const c of controls) if (values[c.key] !== defaults[c.key]) p.set(c.key, String(values[c.key]));
    if (CANVAS && boards.some(b => !shown[b.id])) p.set('boards', boards.filter(b => shown[b.id]).map(b => b.id).join(','));
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  // ── DOM helpers ─────────────────────────────────────────────────────
  const el = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    for (const k in attrs || {}) {
      if (k === 'class') n.className = attrs[k];
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    }
    for (const kid of kids) if (kid != null && kid !== '') n.append(kid);
    return n;
  };
  // The design roots: each artboard in canvas mode, <html> in page mode.
  const roots = () => CANVAS ? Array.from(document.querySelectorAll('.pg-screen')) : [document.documentElement];

  // ── apply values to the design ──────────────────────────────────────
  function apply() {
    const style = document.documentElement.style;
    const rs = roots();
    for (const c of controls) {
      const v = values[c.key];
      if (c.css) {
        if (c.kind === 'toggle') style.setProperty(c.css, v ? (c.on ?? '1') : (c.off ?? '0'));
        else style.setProperty(c.css, String(v) + (c.unit || ''));
      }
      if (c.attr) for (const r of rs) {
        if (c.kind === 'toggle') v ? r.setAttribute(c.attr, '') : r.removeAttribute(c.attr);
        else r.setAttribute(c.attr, String(v));
      }
      if (typeof c.apply === 'function') c.apply(v, rs, values);
    }
    document.querySelectorAll('[data-pg-state]').forEach(b => {
      const target = Object.assign({}, defaults, states[b.dataset.pgState] || {});
      b.setAttribute('aria-pressed', String(controls.every(c => values[c.key] === target[c.key])));
    });
    window.dispatchEvent(new CustomEvent('pg:change', { detail: { values } }));
  }
  function set(key, v) { values[key] = v; apply(); persist(); syncPanel(); }

  // ── mounting the design ─────────────────────────────────────────────
  const tpl = document.getElementById('screen');
  function mountInto(host, board) {
    host.replaceChildren();
    if (tpl && tpl.content) host.append(document.importNode(tpl.content, true));
    labelCases(host, board);
    if (typeof PIECE.mount === 'function') PIECE.mount(host, board, values);
  }
  // Each `[data-case]` gets a chrome label before it and an id the panel can jump to.
  function labelCases(host, board) {
    host.querySelectorAll('[data-case]').forEach((c, i) => {
      const n = String(i + 1).padStart(2, '0');
      c.id = c.id || 'case-' + (board ? board.id + '-' : '') + n;
      const label = el('div', { class: 'pg-case-label', 'data-pg-chrome': '' },
        el('span', { class: 'pg-n' }, n), el('span', { class: 'pg-name' }, c.dataset.case),
        c.dataset.note ? el('span', { class: 'pg-note' }, c.dataset.note) : null);
      c.before(label);
    });
  }
  function caseList() {
    const host = CANVAS ? document.querySelector('.pg-screen') : pageHost;
    const cases = host ? Array.from(host.querySelectorAll('[data-case]')) : [];
    if (cases.length < 2) return null;
    const ul = el('ul', { class: 'pg-cases' });
    cases.forEach((c, i) => ul.append(el('li', null, el('a', { href: '#' + c.id,
      onclick: e => { e.preventDefault(); document.getElementById(c.id).previousElementSibling.scrollIntoView({ behavior: 'smooth', block: 'start' }); } },
      el('span', { class: 'pg-n' }, String(i + 1).padStart(2, '0')), c.dataset.case))));
    return ul;
  }
  let pageHost = null;
  function mountAll() {
    if (CANVAS) document.querySelectorAll('.pg-screen').forEach(s => mountInto(s, boards.find(b => b.id === s.dataset.board)));
    else mountInto(pageHost, null);
  }
  function replay() { mountAll(); apply(); }

  function buildCanvas() {
    const canvas = el('div', { class: 'pg-canvas' });
    for (const b of boards) {
      const w = b.width || 1440;
      const screen = el('div', { class: 'pg-screen', 'data-board': b.id });
      if (b.height) { screen.style.setProperty('--pg-h', b.height + 'px'); if (b.scroll) screen.setAttribute('data-scroll', ''); }
      const board = el('div', { class: 'pg-board', 'data-board': b.id, 'data-pg-note': b.note || null },
        el('div', { class: 'pg-board-label' }, el('b', null, b.label || b.id), el('span', null, w + (b.height ? '×' + b.height : '') + ' px')),
        screen);
      board.style.setProperty('--pg-w', w + 'px');
      board.hidden = !shown[b.id];
      canvas.append(board);
    }
    return canvas;
  }

  // ── version menu and state chips (shared by bar and panel) ──────────
  function versionMenu() {
    if (!PG || !PG.versions || PG.versions.length < 2) return null;
    const sel = el('select', { class: 'pg-select', 'aria-label': 'Version', onchange: e => { location.href = e.target.value + location.search; } });
    for (const v of PG.versions) {
      const o = el('option', { value: v.file }, v.label + (v.date ? ' · ' + v.date : '') + (v.file === PG.final ? ' · final' : ''));
      if (v.file === file) o.selected = true;
      sel.append(o);
    }
    return sel;
  }
  function stateChips() {
    const names = Object.keys(states);
    if (!names.length) return null;
    const g = el('div', { class: 'pg-group pg-states' });
    for (const name of names) g.append(el('button', {
      class: 'pg-chip', 'data-pg-state': name, type: 'button',
      onclick: () => { Object.assign(values, defaults, states[name]); apply(); persist(); syncPanel(); },
    }, name));
    return g;
  }

  // ── bar (canvas mode only) ──────────────────────────────────────────
  function buildBar() {
    const bar = el('header', { class: 'pg-bar' });
    bar.append(el('a', { class: 'pg-home', href: '../index.html', title: 'Playground index' }, '←'));
    const title = el('div', { class: 'pg-title' }, PIECE.title || (PG && PG.title) || document.title);
    bar.append(title);
    const vm = versionMenu();
    if (vm) bar.append(el('div', { class: 'pg-group' }, vm));
    else if (PG && PG.versions && PG.versions.length === 1) title.append(el('small', null, PG.versions[0].label));
    bar.append(el('div', { class: 'pg-spacer' }));
    const sc = stateChips();
    if (sc) bar.append(sc);
    if (boards.length > 1) {
      const g = el('div', { class: 'pg-group', 'data-pg-boards': '' });
      for (const b of boards) g.append(el('button', {
        class: 'pg-chip', type: 'button', 'aria-pressed': String(!!shown[b.id]),
        onclick: e => {
          shown[b.id] = !shown[b.id];
          e.currentTarget.setAttribute('aria-pressed', String(shown[b.id]));
          document.querySelector('.pg-board[data-board="' + b.id + '"]').hidden = !shown[b.id];
          persist();
        },
      }, b.label || b.id));
      bar.append(g);
    }
    bar.append(el('div', { class: 'pg-group' }, el('button', {
      class: 'pg-chip', type: 'button', 'data-pg-toggle': '', 'aria-pressed': 'false', onclick: togglePanel,
    }, 'Controls', el('kbd', null, 'C'))));
    return bar;
  }

  // ── tab (page mode only) ────────────────────────────────────────────
  function buildTab() {
    const cur = PG && PG.versions ? PG.versions.find(v => v.file === file) : null;
    return el('button', { class: 'pg-tab', type: 'button', 'data-pg-toggle': '', 'aria-pressed': 'false',
      title: 'Controls, versions, states', onclick: togglePanel },
      cur ? el('b', null, cur.v) : null, cur ? 'Controls' : el('b', null, 'Controls'), el('kbd', null, 'C'));
  }

  // ── panel ───────────────────────────────────────────────────────────
  const inputs = {};
  function row(c) {
    const label = el('label', { for: 'pg-' + c.key }, c.label || c.key);
    let field, val = null;
    if (c.kind === 'range') {
      val = el('output', null, String(values[c.key]) + (c.unit || ''));
      field = el('input', { type: 'range', id: 'pg-' + c.key, min: c.min ?? 0, max: c.max ?? 100, step: c.step ?? 1, value: values[c.key],
        oninput: e => { set(c.key, Number(e.target.value)); } });
      inputs[c.key] = v => { field.value = v; val.textContent = String(v) + (c.unit || ''); };
    } else if (c.kind === 'color') {
      const code = el('code', null, values[c.key]);
      field = el('div', { class: 'pg-color' }, code, el('input', { type: 'color', id: 'pg-' + c.key, value: values[c.key],
        oninput: e => set(c.key, e.target.value) }));
      inputs[c.key] = v => { field.querySelector('input').value = v; code.textContent = v; };
    } else if (c.kind === 'toggle') {
      const box = el('input', { type: 'checkbox', id: 'pg-' + c.key, onchange: e => set(c.key, e.target.checked) });
      box.checked = !!values[c.key];
      field = el('span', { class: 'pg-switch' }, box, el('i'));
      inputs[c.key] = v => { box.checked = !!v; };
    } else if (c.kind === 'select') {
      const opts = (c.options || []).map(o => typeof o === 'string' ? { value: o, label: o } : o);
      // Segmented while the labels fit the column; a dropdown once they would be clipped.
      if (opts.length <= 4 && opts.reduce((n, o) => n + o.label.length, 0) <= 16) {
        field = el('div', { class: 'pg-seg', role: 'group', id: 'pg-' + c.key });
        for (const o of opts) field.append(el('button', { type: 'button', 'aria-pressed': String(values[c.key] === o.value),
          onclick: () => set(c.key, o.value) }, o.label));
        inputs[c.key] = v => field.querySelectorAll('button').forEach((b, i) => b.setAttribute('aria-pressed', String(opts[i].value === v)));
      } else {
        field = el('select', { class: 'pg-select', id: 'pg-' + c.key, onchange: e => set(c.key, e.target.value) });
        for (const o of opts) { const op = el('option', { value: o.value }, o.label); if (o.value === values[c.key]) op.selected = true; field.append(op); }
        inputs[c.key] = v => { field.value = v; };
      }
    } else {
      field = el('input', { class: 'pg-input', type: 'text', id: 'pg-' + c.key, value: values[c.key] ?? '', oninput: e => set(c.key, e.target.value) });
      inputs[c.key] = v => { field.value = v; };
    }
    return el('div', { class: 'pg-row', 'data-kind': c.kind }, label, val, el('div', { class: 'pg-field' }, field));
  }
  function syncPanel() { for (const c of controls) if (inputs[c.key]) inputs[c.key](values[c.key]); }
  function buildPanel() {
    const head = el('div', { class: 'pg-panel-head' });
    head.append(el('div', { class: 'pg-title' }, el('b', null, PIECE.title || (PG && PG.title) || document.title),
      el('a', { href: '../index.html' }, 'All pieces →')));
    const field = (kicker, node) => node && el('div', { class: 'pg-field' }, el('span', { class: 'pg-kicker' }, kicker), node);
    if (!CANVAS) {           // the bar carries these in canvas mode
      head.append(field('Version', versionMenu()) || '', field('States', stateChips()) || '');
    }
    head.append(field('Cases', caseList()) || '');
    const body = el('div', { class: 'pg-panel-body' });
    const groups = [];
    for (const c of controls) { const g = c.group || 'Controls'; if (!groups.includes(g)) groups.push(g); }
    for (const g of groups) {
      const sec = el('section', { class: 'pg-section' }, el('h3', null, el('span', null, g)));
      for (const c of controls) if ((c.group || 'Controls') === g) sec.append(row(c));
      body.append(sec);
    }
    const actions = el('div', { class: 'pg-actions' },
      el('button', { type: 'button', onclick: replay }, 'Replay', el('kbd', null, 'R')),
      el('button', { type: 'button', onclick: () => { Object.assign(values, defaults); apply(); persist(); syncPanel(); } }, 'Reset'),
      el('button', { type: 'button', class: 'pg-primary', onclick: copySettings }, 'Copy settings'));
    return el('aside', { class: 'pg-panel', 'aria-label': 'Controls' }, head, body, actions);
  }
  function togglePanel() {
    const open = document.body.getAttribute('data-pg-panel') !== 'open';
    document.body.setAttribute('data-pg-panel', open ? 'open' : 'closed');
    document.querySelectorAll('[data-pg-toggle]').forEach(t => t.setAttribute('aria-pressed', String(open)));
  }
  let toastTimer;
  function toast(msg) {
    let t = document.querySelector('.pg-toast');
    if (!t) { t = el('div', { class: 'pg-toast' }); document.body.append(t); }
    t.textContent = msg; t.setAttribute('data-on', '');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.removeAttribute('data-on'), 1600);
  }
  function copySettings() {
    const out = {};
    for (const c of controls) out[c.key] = values[c.key];
    const text = JSON.stringify({ piece: (PG && PG.slug) || null, version: file, values: out }, null, 2);
    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
      .then(() => toast('Settings copied — paste them back to the agent'))
      .catch(() => { window.prompt('Copy these settings', text); });
  }

  // ── boot ────────────────────────────────────────────────────────────
  function boot() {
    document.body.classList.add('pg-root');
    document.body.setAttribute('data-pg-mode', CANVAS ? 'canvas' : 'page');
    document.body.setAttribute('data-pg-panel', 'closed');
    if (CANVAS) {
      document.body.append(buildBar(), buildCanvas());
    } else {
      // The design is the page: a display:contents host as the body's first child, so the
      // design's own elements lay out as if they were written straight into <body>.
      pageHost = el('div', { 'data-pg-host': '' });
      pageHost.style.display = 'contents';
      document.body.prepend(pageHost);
      document.body.append(buildTab());
    }
    mountAll();
    document.body.append(buildPanel());
    apply();
    document.addEventListener('keydown', e => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) return;
      if (e.key === 'c' || e.key === 'C') togglePanel();
      if (e.key === 'r' || e.key === 'R') replay();
    });
  }
  window.pg = { values, set, replay, roots };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
