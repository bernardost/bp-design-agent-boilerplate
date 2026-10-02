---
name: prototype
description: Build the first pass of a new design as a disposable page with a tuning drawer, so the owner adjusts the values himself instead of describing them. Use for /prototype, after a direction is picked, or whenever the first visual pass of a screen, page or deck template is about to be built.
---

# Prototype — the first pass, with the dials exposed

Between a picked direction and a real build there is one disposable artifact: a screen with
real content, in the states that matter, with no component abstraction and no production
architecture. It exists to answer a question — does this composition work, does this
interaction feel right — and then it is thrown away. Premature abstraction locking in a weak
design is the failure this step prevents.

**The first pass ships with a tuning drawer, built in the same pass as the page, before the
owner asks for one.** That is the part of this skill that matters most, and it is below.

## Why the drawer exists

An owner's taste for a *new* design cannot be specified in advance. He has not seen it yet, and
he certainly has not seen it move. What comes back from a first pass is never "use 15px" — it
is "the type feels heavy" and "that transition is doing too much", and then you both spend a
round converting adjectives into values.

Moving a slider is faster than arguing values in prose. And **Copy settings turns the pick into
a record**: the owner's taste arrives as JSON you paste into the defaults, rather than as a
paragraph you have to interpret.

## The rule that makes it possible

**Every visual value is a CSS custom property, or a `data-` attribute on `<body>`. Nothing the
owner might plausibly want to move is hard-coded.**

That constraint is worth more than the drawer itself. **The variable list is the spec** — it is
the honest inventory of every decision the design is making, and writing it forces you to
notice the ones you made without thinking. A value you hard-coded is a decision you hid.

```html
<body data-motion="rise" data-ease="standard">
<style>
  :root{
    --ink:#0d0d0e; --paper:#fff; --accent:#1f4fd8;
    --step-0:16px; --step-1:21px; --step-2:34px; --step-3:56px;
    --track-display:-.03em; --track-body:0;
    --col:12; --gutter:24px; --margin:64px; --measure:62ch;
    --dur:420ms; --stagger:60ms; --ease:cubic-bezier(.22,.61,.36,1);
  }
  /* Each motion kind is a branch, never a number on a slider. */
  [data-motion="rise"]  .in{transform:translateY(16px);opacity:0}
  [data-motion="fade"]  .in{opacity:0}
  [data-motion="wipe"]  .in{clip-path:inset(0 100% 0 0)}
  [data-motion="none"]  .in{transform:none;opacity:1}
</style>
```

## The drawer

- **Hidden by default.** One key toggles it — `T` is a reasonable default — and one small word
  sits in a corner so the owner can find it without being told twice.
- **Styled outside the page's own language.** A different typeface, a flat utility grey, a
  hard edge. Nobody should be able to mistake the drawer for part of the design, and a drawer
  that matches the page gets read as a design element and judged as one.
- **Four groups, in this order:**
  1. **Colour** — ground, ink, accent, and any tint the design uses.
  2. **Type** — the size steps, and tracking for display and body separately.
  3. **Grid and margins** — columns, gutter, page margin, measure.
  4. **Motion** — last, because it is the one that needs the other three settled.

### Motion is chosen, not dialled

**A select of three or four genuinely different kinds, not a slider.** Rise, fade, wipe, none —
each one a CSS branch off `data-motion`, so they differ in kind rather than in degree. A slider
between two numbers cannot tell you that the right answer was a different idea.

**Ease is a select of named curves**, never four raw bezier handles. Standard, entrance, exit,
spring — named, so the owner picks a feel rather than solving a cubic.

**When a reference site has been inspected, its curve joins the select by name**, and a
one-click preset sets the timing with it. *"Linear's easing"* in the dropdown, and a button
that applies their duration and stagger alongside it. That is how a reference stops being a
thing you looked at and becomes a thing you can try.

### Three actions, and no more

- **Replay** — re-runs every entrance animation without reloading the page. Without this the
  owner reloads to see a 400ms transition, loses his settings, and stops adjusting motion at
  all.
- **Reset** — back to the shipped defaults.
- **Copy settings** — the current values as JSON on the clipboard. The owner pastes it back to
  you, and **you bake it into the defaults**. This is the handoff, and it is why the drawer is
  worth building.

**Settings persist in `localStorage`**, so closing the tab does not throw away an hour of
fiddling.

## Before a client sees it

**Remove the drawer.** It is scaffolding for the conversation between you and the owner, and a
client finding a panel of sliders on their brand presentation draws exactly the wrong
conclusion about what they are being shown. Strip it in the same commit that prepares the
client version, and keep the custom properties — those are the design now.

`doctor.py` reports a drawer left in anything under `brain/decks/`.

## The rest of the first pass

- **Real content, or no verdict.** The longest realistic name, the empty list, the error
  message, the number with five digits. A composition judged on tidy placeholder text has been
  judged on a page that will never exist.
- **The states that matter**, not just the happy one: default, empty, loading, error, narrow.
- **Throw it away.** When the question is answered, the prototype has done its job. Carry the
  variable list forward and leave the markup behind.
- **Look at it before handing it over** — render it, screenshot it, read the screenshots. Then
  `/critique` against `brain/lenses/craft.md`.

## Guardrails

- **Do not build the drawer for a design that is already settled.** This is for a *new* look.
  Tuning a page that follows an agreed visual language is a change request, not an exploration.
- **Do not let the drawer become the deliverable.** If you are adding a fifth group or a second
  row of actions, you are building a tool instead of answering the question.
- **The owner's pasted JSON is a decision.** When it settles the look, it gets logged like any
  other — one dated file in `brain/decisions/`, with the values in it.
