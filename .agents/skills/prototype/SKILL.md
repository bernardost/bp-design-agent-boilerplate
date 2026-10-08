---
name: prototype
description: Build the first pass of a new design as a playground piece with its controls exposed, so the owner adjusts the values himself instead of describing them. Use for /prototype, after a direction is picked, or whenever the first visual pass of a screen, page or deck template is about to be built.
---

# Prototype — the first pass, with the dials exposed

Between a picked direction and a real build there is one disposable artifact: a screen with
real content, in the states that matter, with no component abstraction and no production
architecture. It exists to answer a question — does this composition work, does this
interaction feel right — and then it is left behind. Premature abstraction locking in a weak
design is the failure this step prevents.

**The first pass is a playground piece, and it ships with its controls, built in the same pass
as the page, before the owner asks for them.** `/playground` is where it lives and how it is
versioned; `brain/playground/_template/piece.html` is the file it starts from. This skill is
about what goes into that first pass and why the controls matter.

## Why the controls exist

An owner's taste for a *new* design cannot be specified in advance. He has not seen it yet, and
he certainly has not seen it move. What comes back from a first pass is never "use 15px" — it
is "the type feels heavy" and "that transition is doing too much", and then you both spend a
round converting adjectives into values.

Moving a slider is faster than arguing values in prose. And **Copy settings turns the pick into
a record**: the owner's taste arrives as JSON you paste into the defaults, rather than as a
paragraph you have to interpret.

## The rule that makes it possible

**Every visual value is a CSS custom property on `:root`, or a `data-` attribute on the
artboard root. Nothing the owner might plausibly want to move is hard-coded.**

That constraint is worth more than the panel itself. **The variable list is the spec** — it is
the honest inventory of every decision the design is making, and writing it forces you to
notice the ones you made without thinking. A value you hard-coded is a decision you hid. It is
also what `/promote` hands to the implementer, so a complete list now is a spec later.

```css
:root{
  --ink:#0d0d0e; --paper:#fff; --accent:#1f4fd8;
  --step-0:16px; --step-1:21px; --step-2:34px; --step-3:56px;
  --track-display:-.03em; --track-body:0;
  --col:12; --gutter:24px; --margin:64px; --measure:62ch;
  --dur:420ms; --stagger:60ms; --ease:cubic-bezier(.22,.61,.36,1);
}
/* Each motion kind is a branch, never a number on a slider. */
[data-motion="rise"] .in{animation-name:rise}
[data-motion="fade"] .in{animation-name:fade}
[data-motion="wipe"] .in{animation-name:wipe}
[data-motion="none"] .in{animation:none}
```

and each of those appears once in `window.PIECE.controls`, which is what builds the panel.

## The controls

- **Hidden until asked for.** `C` opens the panel; it overlays the canvas instead of taking a
  band off every artboard. One small word in the bar says it is there.
- **Styled outside the page's own language.** The chrome is a flat utility grey in a
  monospace face, on purpose: nobody can mistake it for part of the design, and a panel that
  matched the page would be read as a design element and judged as one.
- **Four groups, in this order:**
  1. **Colour** — ground, ink, accent, and any tint the design uses.
  2. **Type** — the size steps, and tracking for display and body separately.
  3. **Layout** — columns, gutter, page margin, measure, density.
  4. **Motion** — last, because it is the one that needs the other three settled.

  Plus **Content** for the switches that drive states: empty, error, long names.

### Motion is chosen, not dialled

**A select of three or four genuinely different kinds, not a slider.** Rise, fade, wipe, none —
each one a CSS branch off `data-motion`, so they differ in kind rather than in degree. A slider
between two numbers cannot tell you that the right answer was a different idea.

**Ease is a select of named curves**, never four raw bezier handles. Standard, entrance, exit,
spring — named, so the owner picks a feel rather than solving a cubic.

**When a reference site has been inspected, its curve joins the select by name**, and a
state preset sets the timing with it. *"Linear's easing"* in the dropdown, and a chip that
applies their duration and stagger alongside it. That is how a reference stops being a thing
you looked at and becomes a thing you can try.

### Three actions, and no more

- **Replay** — re-mounts every artboard, which runs every entrance again without a reload.
  Without this the owner reloads to see a 400ms transition, loses his settings, and stops
  adjusting motion at all.
- **Reset** — back to the shipped defaults.
- **Copy settings** — the current values as JSON on the clipboard. The owner pastes it back to
  you, and **you bake it into the defaults of the next version**. This is the handoff, and it
  is why the panel is worth building.

Settings persist per version in `localStorage`, and the URL carries the non-default ones, so a
link opens on the exact view the owner was looking at.

## The rest of the first pass

- **Real content, or no verdict.** The longest realistic name, the empty list, the error
  message, the number with five digits. A composition judged on tidy placeholder text has been
  judged on a page that will never exist.
- **The states that matter**, as presets in `PIECE.states`, not just the happy one: default,
  empty, loading, error, long.
- **Both boards.** Desktop and mobile side by side from the first version; a design that
  gets its mobile pass later gets a worse one.
- **Look at it before handing it over** — render it, screenshot both boards, read the
  screenshots. Then `/critique` against `brain/lenses/craft.md`.
- **Leave it behind, do not delete it.** When the question is answered, the version has done
  its job; the next one is a new file, and `/promote` carries the variable list forward.

## Guardrails

- **Do not build controls for a design that is already settled.** This is for a *new* look.
  Tuning a page that follows an agreed visual language is a change request, and a change
  request is a new version with the change in it.
- **Do not let the panel become the deliverable.** If you are adding a fifth group or a second
  row of actions, you are building a tool instead of answering the question.
- **The owner's pasted JSON is a decision.** When it settles the look, it gets logged like any
  other — one dated file in `brain/decisions/`, with the values in it — and `/promote` is
  the point where that happens for the whole piece.
- **Nothing with the chrome on it goes to a client.** A client sees a deck (`/deck`) or the
  shipped thing. `doctor.py` reports a tuning drawer left in anything under `brain/decks/`.
