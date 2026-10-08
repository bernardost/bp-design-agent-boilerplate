/* canvas.js — turns a piece file into a canvas: artboards, version strip, states, controls.

   A piece declares `window.PIECE` and a `<template id="screen">` holding the design, and
   includes this file last. Everything else here is derived from that declaration, so a piece
   carries its design and the list of what can be tuned, and nothing about how the chrome works.

     window.PIECE = {
       title:   'Checkout — summary panel',
       boards:  [{id:'desktop', width:1440}, {id:'mobile', width:390, height:844, scroll:true}],
       controls:[{group:'Colour', key:'accent', label:'Accent', kind:'color', value:'#1f4fd8', css:'--accent'},
                 {group:'Type',   key:'body',   label:'Body',   kind:'range', value:16, min:14, max:20, unit:'px', css:'--step-0'},
                 {group:'Layout', key:'density',label:'Density',kind:'select',value:'comfortable', options:['comfortable','compact'], attr:'data-density'},
                 {group:'State',  key:'empty',  label:'Empty',  kind:'toggle',value:false, attr:'data-empty'}],
       states:  {'Default':{}, 'Empty cart':{empty:true}},
       mount(root, board, values){},          // optional: wire up interactivity, query inside root only
     };

   How a value reaches the design:
     css   → a custom property set on <html>, so every artboard inherits it:  var(--accent)
     attr  → an attribute on each artboard's .pg-screen root:   .pg-screen[data-density="compact"] …
             a toggle sets the attribute when true and removes it when false
     apply → apply(value, screens, values) for anything those two cannot express

   `kind` is one of: color · range · select · toggle · text. A select renders as a segmented
   control while its labels are short enough to fit, and as a dropdown otherwise.

   Values persist per piece version in localStorage, and the URL carries the non-default ones
   (`?accent=%231f4fd8&density=compact`) so a link opens on an exact view. `C` toggles the
   panel, `R` replays — replay re-mounts every artboard, which restarts the design's entrance
   animations and any script in mount(). Copy settings puts the current values on the clipboard
   as JSON, for the owner to paste back: that JSON is the handoff, and the agent bakes it into
   the defaults of the next version. */

(function () {
  'use strict';
  const PIECE = window.PIECE || {};
  const PG = window.PLAYGROUND || null;          // written by brain/playground.py
  const file = decodeURIComponent(location.pathname.split('/').pop() || '');
  const KEY = 'pg:' + (PG && PG.slug ? PG.slug + '/' : '') + file;
  const controls = PIECE.controls || [];
  const states = PIECE.states || {};
  const boards = (PIECE.boards && PIECE.boards.length) ? PIECE.boards
    : [{ id: 'desktop', width: 1440 }, { id: 'mobile', width: 390 }];
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
  if (q.has('boards')) {
    const on = q.get('boards').split(',');
    for (const b of boards) shown[b.id] = on.includes(b.id);
  }

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify({ values, boards: shown })); } catch (e) { /* ignore */ }
    const p = new URLSearchParams();
    for (const c of controls) if (values[c.key] !== defaults[c.key]) p.set(c.key, String(values[c.key]));
    const hidden = boards.filter(b => !shown[b.id]);
    if (hidden.length) p.set('boards', boards.filter(b => shown[b.id]).map(b => b.id).join(','));
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
    for (const kid of kids) if (kid != null) n.append(kid);
    return n;
  };
  const screens = () => Array.from(document.querySelectorAll('.pg-screen'));

  // ── apply values to the design ──────────────────────────────────────
  function apply() {
    const root = document.documentElement.style;
    const scr = screens();
    for (const c of controls) {
      const v = values[c.key];
      if (c.css) {
        if (c.kind === 'toggle') root.setProperty(c.css, v ? (c.on ?? '1') : (c.off ?? '0'));
        else root.setProperty(c.css, String(v) + (c.unit || ''));
      }
      if (c.attr) for (const s of scr) {
        if (c.kind === 'toggle') v ? s.setAttribute(c.attr, '') : s.removeAttribute(c.attr);
        else s.setAttribute(c.attr, String(v));
      }
      if (typeof c.apply === 'function') c.apply(v, scr, values);
    }
    document.querySelectorAll('[data-pg-state]').forEach(b => {
      const preset = states[b.dataset.pgState] || {};
      const target = Object.assign({}, defaults, preset);
      b.setAttribute('aria-pressed', String(controls.every(c => values[c.key] === target[c.key])));
    });
    window.dispatchEvent(new CustomEvent('pg:change', { detail: { values } }));
  }

  function set(key, v) { values[key] = v; apply(); persist(); syncPanel(); }

  // ── artboards ───────────────────────────────────────────────────────
  const tpl = document.getElementById('screen');
  function mountScreen(screen, board) {
    screen.replaceChildren();
    if (tpl && tpl.content) screen.append(document.importNode(tpl.content, true));
    if (typeof PIECE.mount === 'function') PIECE.mount(screen, board, values);
  }
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
      mountScreen(screen, b);
      canvas.append(board);
    }
    return canvas;
  }
  function replay() {
    document.querySelectorAll('.pg-screen').forEach(s => mountScreen(s, boards.find(b => b.id === s.dataset.board)));
    apply();
  }

  // ── bar ─────────────────────────────────────────────────────────────
  function buildBar() {
    const bar = el('header', { class: 'pg-bar' });
    bar.append(el('a', { class: 'pg-home', href: '../index.html', title: 'Playground index' }, '←'));
    const title = el('div', { class: 'pg-title' }, PIECE.title || (PG && PG.title) || document.title);
    bar.append(title);
    if (PG && PG.versions && PG.versions.length > 1) {
      const sel = el('select', { class: 'pg-select', 'aria-label': 'Version', onchange: e => { location.href = e.target.value + location.search; } });
      for (const v of PG.versions) {
        const o = el('option', { value: v.file }, v.label + (v.date ? ' · ' + v.date : '') + (v.file === PG.final ? ' · final' : ''));
        if (v.file === file) o.selected = true;
        sel.append(o);
      }
      bar.append(el('div', { class: 'pg-group' }, sel));
    } else if (PG && PG.versions && PG.versions.length === 1) {
      title.append(el('small', null, PG.versions[0].label));
    }
    bar.append(el('div', { class: 'pg-spacer' }));
    const names = Object.keys(states);
    if (names.length) {
      const g = el('div', { class: 'pg-group' });
      for (const name of names) g.append(el('button', {
        class: 'pg-chip', 'data-pg-state': name, type: 'button',
        onclick: () => { Object.assign(values, defaults, states[name]); apply(); persist(); syncPanel(); },
      }, name));
      bar.append(g);
    }
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
    if (controls.length) {
      bar.append(el('div', { class: 'pg-group' }, el('button', {
        class: 'pg-chip', type: 'button', 'data-pg-toggle': '', 'aria-pressed': 'false',
        onclick: togglePanel,
      }, 'Controls', el('kbd', null, 'C'))));
    }
    return bar;
  }

  // ── panel ───────────────────────────────────────────────────────────
  const inputs = {};
  function row(c) {
    const label = el('label', { for: 'pg-' + c.key }, c.label || c.key);
    let field;
    if (c.kind === 'range') {
      const out = el('output', null, String(values[c.key]) + (c.unit || ''));
      label.append(out);
      field = el('input', { type: 'range', id: 'pg-' + c.key, min: c.min ?? 0, max: c.max ?? 100, step: c.step ?? 1, value: values[c.key],
        oninput: e => { set(c.key, Number(e.target.value)); } });
      inputs[c.key] = v => { field.value = v; out.textContent = String(v) + (c.unit || ''); };
    } else if (c.kind === 'color') {
      const code = el('code', null, values[c.key]);
      field = el('div', { class: 'pg-color' }, code, el('input', { type: 'color', id: 'pg-' + c.key, value: values[c.key],
        oninput: e => set(c.key, e.target.value) }));
      inputs[c.key] = v => { field.querySelector('input').value = v; code.textContent = v; };
    } else if (c.kind === 'toggle') {
      field = el('input', { type: 'checkbox', id: 'pg-' + c.key, onchange: e => set(c.key, e.target.checked) });
      field.checked = !!values[c.key];
      inputs[c.key] = v => { field.checked = !!v; };
    } else if (c.kind === 'select') {
      const opts = (c.options || []).map(o => typeof o === 'string' ? { value: o, label: o } : o);
      // Segmented while the labels fit the column; a dropdown once they would be clipped.
      if (opts.length <= 4 && opts.reduce((n, o) => n + o.label.length, 0) <= 16) {
        field = el('div', { class: 'pg-seg', role: 'group', id: 'pg-' + c.key });
        for (const o of opts) field.append(el('button', { type: 'button', 'aria-pressed': String(values[c.key] === o.value),
          onclick: () => set(c.key, o.value) }, o.label));
        inputs[c.key] = v => field.querySelectorAll('button').forEach((b, i) => b.setAttribute('aria-pressed', String(opts[i].value === v)));
      } else {
        field = el('select', { id: 'pg-' + c.key, onchange: e => set(c.key, e.target.value) });
        for (const o of opts) { const op = el('option', { value: o.value }, o.label); if (o.value === values[c.key]) op.selected = true; field.append(op); }
        inputs[c.key] = v => { field.value = v; };
      }
    } else {
      field = el('input', { type: 'text', id: 'pg-' + c.key, value: values[c.key] ?? '', oninput: e => set(c.key, e.target.value) });
      inputs[c.key] = v => { field.value = v; };
    }
    return el('div', { class: 'pg-row' }, label, field);
  }
  function syncPanel() { for (const c of controls) if (inputs[c.key]) inputs[c.key](values[c.key]); }
  function buildPanel() {
    const body = el('div', { class: 'pg-panel-body' });
    const groups = [];
    for (const c of controls) { const g = c.group || 'Controls'; if (!groups.includes(g)) groups.push(g); }
    for (const g of groups) {
      const sec = el('section', { class: 'pg-section' }, el('h3', null, g));
      for (const c of controls) if ((c.group || 'Controls') === g) sec.append(row(c));
      body.append(sec);
    }
    const actions = el('div', { class: 'pg-actions' },
      el('button', { type: 'button', onclick: replay }, 'Replay', el('kbd', null, ' R')),
      el('button', { type: 'button', onclick: () => { Object.assign(values, defaults); apply(); persist(); syncPanel(); } }, 'Reset'),
      el('button', { type: 'button', onclick: copySettings }, 'Copy settings'));
    return el('aside', { class: 'pg-panel', 'aria-label': 'Controls' }, body, actions);
  }
  function togglePanel() {
    const open = document.body.getAttribute('data-pg-panel') !== 'open';
    document.body.setAttribute('data-pg-panel', open ? 'open' : 'closed');
    const t = document.querySelector('[data-pg-toggle]');
    if (t) t.setAttribute('aria-pressed', String(open));
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
    document.body.setAttribute('data-pg-panel', 'closed');
    document.body.append(buildBar(), buildCanvas());
    if (controls.length) document.body.append(buildPanel());
    apply();
    document.addEventListener('keydown', e => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) return;
      if (e.key === 'c' || e.key === 'C') { if (controls.length) togglePanel(); }
      if (e.key === 'r' || e.key === 'R') replay();
    });
  }
  window.pg = { values, set, replay, screens };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
