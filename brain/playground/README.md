# `playground/` — the work, in HTML, every iteration kept

One folder per **piece** — a screen, a component, a flow — holding every version of it as a
plain HTML file that opens straight from disk. `/playground` writes here, `/prototype` builds
its first pass here, and `/promote` is how a piece leaves. `python3 brain/playground.py`
renders `index.html`, the one page that lists everything, and a `versions.js` per piece that
gives each file its version strip.

**Why HTML.** A round in Figma or in product code costs minutes to hours; a round on an HTML
file costs seconds, and the owner can move the values himself instead of describing them. So
the work happens here, whether it started from an existing design or from nothing, and only
leaves once it is settled.

## The folder

```
brain/playground/
  README.md
  index.html                   ← generated, gitignored
  _canvas/canvas.css, canvas.js   the chrome every piece shares — template-owned
  _template/piece.html, piece.md  what a new piece is copied from — template-owned
  <slug>/
    piece.md                   ← the record: brief, status, source, the version log
    v01-<name>.html            ← never edited once v02 exists
    v02-<name>.html
    shipped.html               ← after shipping: the HTML counterpart of what went live
    versions.js                ← generated, gitignored
```

Pieces and their versions are **the work, not projections**: they are committed. `index.html`
and `versions.js` are regenerated from them and are not.

## The rules

- **Nothing is lost. Ever.** A change the owner might want to walk back starts a new file,
  `vNN-<what-changed>.html`, and the previous file is never touched again. Concretely: a new
  version begins when the owner has seen the current one and asks for a change, when a change
  discards something that exists, or when a different direction is being tried. Small fixes to
  a version the owner has not seen yet stay in that version. **Say it when a new version
  starts** — *"Starting v03: the header without the lede. v02 stays."* — and log it in
  `piece.md` the same turn. The version strip in the bar is how the owner goes back.
- **An existing design arrives as-is first.** When a piece starts from a Figma frame, a live
  page or a file, `v01` is the faithful translation and nothing in it is changed: same type,
  same values, same spacing, measured, never eyeballed. Iteration starts at `v02`. Without
  that baseline nobody can say what an iteration changed.
- **Desktop and mobile sit side by side.** Each artboard is a CSS container named `screen`,
  so the design's breakpoints are `@container screen (min-width: …)`, never `@media`, and
  `vw`/`vh` are `cqw`/`cqh`. There is no zoom: a 1440px artboard is 1440px wide and the canvas
  scrolls. Boards can be hidden from the bar, and a piece can declare other widths.
- **Every piece has controls.** Every visual value is a custom property on `:root` and every
  switch is a `data-` attribute on the artboard root, and the `controls` list in `window.PIECE`
  is the inventory of both — the honest spec of every decision the design makes. Four groups
  by convention: Colour, Type, Layout, Motion; plus Content for states. Motion is a select of
  kinds, never a slider between two numbers. Named **states** are presets of control values
  and sit in the bar as chips: Default, Empty, Error, Long titles, whatever the piece needs.
- **The panel is hidden until asked for.** `C` opens it; it overlays the canvas rather than
  taking a strip off every artboard. That is the fix for the last playground's chrome, which
  took a band of every screen for controls nobody was using at that moment.
- **Copy settings is the handoff.** The owner tunes, copies, pastes the JSON back. The agent
  bakes those values into the defaults of the next version and logs the pick as a decision
  when it settles something.
- **Interactivity queries inside its own artboard.** Two boards means two copies of the
  design in one document; `PIECE.mount(root, board, values)` is called once per board, and a
  `document.querySelector` inside it finds the wrong one.
- **Real content.** The longest real name, the five-digit number, the empty list, the error.
  Placeholder text judges a page that will never exist.
- **Say which project.** `project:` in `piece.md`, like every other record. The index filters
  on it.

## Status, and what moves it

`exploring` → `current` → `final` → `shipped`, written in `piece.md`.

- **exploring** — versions are being made; nothing is chosen.
- **current** — the owner has said which version he is working from. Others stay.
- **final** — the owner said it is done. `/promote` writes the decision that says so (it names
  the version and the settings), fills `Final:` and `Decision:`, and hands over the
  implementation notes. The final version file is never edited again. `doctor.py` reports a
  final piece with no decision.
- **shipped** — the design exists somewhere real: product code, a Figma file, a live site.
  `Shipped:` says where and when, and **`shipped.html` is the HTML counterpart** of what went
  live — same chrome, same controls where they still apply, with a note in the file's head
  saying what differs from the final version and why. It is the reference the next round
  starts from, and `doctor.py` reports a shipped piece without one.

## What this is not

- **Not where directions are compared.** Six directions at once are `/explore`, filed in
  `brain/explorations/` as specimens at 4:3; the index links the spreads so they are one click
  away. A direction that survives becomes a piece here, with `Exploration:` pointing back.
- **Not a client deliverable.** A piece has a bar, a version strip and a panel of dials. What
  a client sees is a deck (`brain/decks/`) or the shipped thing. The chrome never goes to a
  client.
- **Not the record of what was decided.** `brain/decisions/` is. A piece's `piece.md` points
  at the decision; it does not restate it.
