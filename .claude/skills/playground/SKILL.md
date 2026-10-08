---
name: playground
description: Do the design work as HTML pieces in brain/playground/ — a faithful translation of an existing design or a page from scratch, desktop and mobile side by side, every visual value on a control, and every iteration kept as its own numbered file. Use for /playground, "put this in the playground", "make a version of this I can tweak", "translate this Figma frame to HTML", "iterate on the header", or whenever a screen or component is about to be designed, changed or tuned.
---

# Playground — the work happens in HTML, and nothing is lost

A round on a Figma file or in product code costs minutes to hours. A round on an HTML file
costs seconds, and the owner moves the values himself instead of describing them. So this is
where screens and components get designed and changed: as **pieces** under
`brain/playground/<slug>/`, each a folder of numbered versions that open straight from disk,
with desktop and mobile artboards side by side and a panel of controls for everything that can
be tuned. `brain/playground/README.md` is the format; this is the procedure.

## 0 · Say which project, and check the stage

In a multi-project workspace the piece carries a `project:` key and the question is settled
before the folder exists. Then the stage check: a piece that builds a screen presupposes a
direction. If `brain/decisions/` holds none for this strand and `brain/explorations/` holds no
spread, say so in one line and offer `/explore` first. Translating an existing design as-is is
exempt — a baseline is not a direction.

## 1 · Start a piece

Copy `brain/playground/_template/piece.md` to `brain/playground/<slug>/piece.md` and fill it:
title, one-line brief, `source`, `status: exploring`, `project`. The slug is lowercase-kebab
and permanent, like a decision slug.

**From an existing design, v01 is the as-is translation and nothing in it is changed.** The
source is a Figma frame (read it with the Figma tools; measure, never eyeball), a live page
(screenshot it at both widths, read its computed styles), or a file. Match type, size, colour,
spacing and radii exactly, with the real brand assets under the charter's rule — extracted,
asked for, or a text placeholder, never redrawn. Name it `v01-as-is.html`. The owner judges
every later version against it, so an inexact baseline poisons every comparison after it.

**From nothing, v01 is the first pass.** `/prototype` is the procedure for that pass and it
builds here; read it before building.

Either way the file is `_template/piece.html` with the design swapped in, and three things
hold:

- **Breakpoints are `@container screen (min-width: …)`, never `@media`.** Each artboard is a
  CSS container, which is what lets the mobile board be 390px wide on a 1440px display.
  `vw`/`vh` become `cqw`/`cqh`.
- **Every visual value is a custom property on `:root`; every switch is a `data-` attribute on
  the artboard root; and the `controls` list in `window.PIECE` names all of them.** A value
  hard-coded in the CSS is a decision hidden from the owner. Four groups by convention —
  Colour, Type, Layout, Motion — plus Content for states. Motion is a select of kinds, never
  a slider between two numbers.
- **States are presets** in `PIECE.states`: Default, Empty, Error, Long names, Loading —
  whatever this piece has to survive. Real content in each: the longest real name, the
  five-digit number, the error message that will actually be shown.

Then `python3 brain/playground.py`, open the file, and **look at it at both widths before
handing it over**. Screenshot both boards and read the screenshots. A piece nobody looked at
is a draft whatever its state.

## 2 · Iterate, and keep everything

**A new version is a new file, and the old file is never touched again.** `v02-<what-changed>.html`,
copied from the version it builds on. Start one when:

- the owner has seen the current version and asks for a change;
- the change discards something — a section, a layout, a direction;
- a different direction is being tried alongside the current one.

Small fixes to a version the owner has not seen yet stay in that version. Everything else is a
new file, because the only way back is a file that still exists.

**Announce it, every time, in one line:** *"Starting v03: the header without the lede, and the
accent back on the action. v02 stays."* Then, the same turn, add the line to `## Versions` in
`piece.md` and run `python3 brain/playground.py` so the version strip in the bar knows about
the new file. A version that is not in the log is a version the next session cannot explain.

**Tune before you redesign.** When the owner's reaction is *"the type feels heavy"*, that is a
control, not a version: ask him to move it, or move it yourself and say which value. A new
version is for a change in kind. Pasted-back settings JSON from *Copy settings* gets baked into
the defaults of the next version, and logged as a decision when it settles something.

When the owner says which version he is working from, `status: current` and say so.

## 3 · Hand it over

The reply names the file path and what to look at, and nothing about how the chrome works
beyond the first time: *"`C` opens the controls, `R` replays the motion, the version menu in
the bar goes back."* Say it once per engagement, like focus mode.

If the piece came out of an exploration, `Exploration:` in `piece.md` points at it, and the
exploration's *Where it went* names the piece.

## 4 · When the owner says it is done

That is `/promote`. Do not change the status to final here; the decision that says so, the
implementation notes and the shipped counterpart are that command's job.

## Guardrails

- **Do not put the chrome in front of a client.** A piece has a bar, a version menu and a
  panel of dials. A client sees a deck or the shipped thing.
- **Do not edit a superseded version to fix a typo.** Fix it in the current one. The old file
  is the record of what the owner saw.
- **Do not build the house style into the work.** `brain/lenses/house.md` is for pages made
  for the owner to read; the chrome is deliberately styled outside both.
- **Do not let the controls become the design.** A fifth group, or a control nobody would
  move, is a tool being built instead of a question being answered.
- **Interactivity queries inside its own artboard.** `PIECE.mount(root, board, values)` runs
  once per board; a `document.querySelector` in it finds the wrong copy.
- **A piece is one strand.** Two projects' screens in one piece compare things that were never
  alternatives.
