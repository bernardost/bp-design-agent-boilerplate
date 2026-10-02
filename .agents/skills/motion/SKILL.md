---
name: motion
description: Choose and build a project's motion — the principles that hold across brands, how to measure a reference site's motion rather than guess at it, and how to write this project's own vocabulary down so every page moves the same way. Use for /motion, "how should this animate", "the transitions feel wrong", or before adding motion to a first pass.
---

# Motion — pick a vocabulary, measure your references, write it down

Motion is the part of a page an owner judges in the first two seconds and cannot specify in
advance. This skill holds three things: what is true about motion regardless of the brand, how
to read motion off a reference site instead of guessing, and how to turn both into **this**
project's vocabulary, written down in `brain/lenses/motion.md` so every page agrees.

**The drawer that lets the owner tune it is `/prototype`.** Build it in the same pass; do not
restate it here.

## 1 · Say which context you are in, first

Most motion advice is written for one context and silently assumes it. These four want
different answers, and several rules invert between them.

- **A long scrolling page.** Scroll is the timeline. Entrances are choreographed, sections can
  be sticky and scrubbed, and the reader's hand drives everything.
- **An app or tool UI.** Motion is feedback and continuity, not choreography. Much shorter —
  roughly 120–240ms — and tied to a state change the user caused. Entrance animations on a
  dashboard the user opens forty times a day are an irritation, not a finish.
- **A presented deck.** The presenter is the clock. Motion is per-slide and triggered by them,
  never by a timer, and a build that outruns the speaker is worse than no build.
- **A prototype answering whether something feels right.** Motion is the question rather than
  the finish, so it is exaggerated, isolated, and compared against alternatives.

Say which one you are in before writing a single transition. The rest of this file marks where
a rule is context-specific.

## 2 · What holds regardless of brand or context

These are the ones worth treating as rules.

- **One vocabulary per page.** Every element enters the same way. A mark that draws, a heading
  that fades and a footer that slides are three vocabularies, and the page reads as assembled
  from parts. Pick one entrance and reuse it.
- **One timed moment, at most.** A page may have exactly one thing that moves on its own clock,
  and it finishes quickly. After it, nothing moves until the reader does. *(In an app: zero.)*
- **Nothing loops in the content.** Idle loops are decoration only, never the thing the reader
  is meant to read. A element that lifts and lowers forever is a screensaver.
- **A small, fixed set of eases, chosen once.** Two or three for the whole project, named, with
  a rule for which goes where. The number of distinct curves on a page is a good proxy for
  whether anyone decided anything.
- **Duration comes from the ease's tail, not from a big number.** "Slow and elegant" is a
  long-tailed curve, not a long transition. Past roughly a second, a reveal the reader is
  waiting for reads as sluggish rather than considered.
- **Transform and opacity animate together on slightly different timings**, because they are
  perceived differently. Opacity usually wants to be a little shorter than movement.
- **Hover is a dip, not a jump.** Nothing bounces, nothing jumps position under the cursor.
- **Honour `prefers-reduced-motion`.** Durations collapse to near zero and the page still
  works. This is not optional and it is not a nice-to-have.
- **Motion cannot rescue a still frame that does not work.** Screenshot the page with every
  animation disabled. If that image is weak, no ease fixes it, and reaching for motion at that
  point is avoidance.

## 3 · Derive the vocabulary from the brand, not from a reference

The specific answers — what enters, from where, on which curve — belong to the project, and
two good brands give opposite answers. Ask:

- **What does the brand claim to be?** Precise and institutional, or warm and physical, or
  fast and utilitarian? Motion is the most direct expression of that, and the wrong one
  contradicts everything the type and colour are doing.
- **What is the content?** Editorial long-form, a dense tool, a portfolio of images, a
  presentation. Masked line reveals suit a page built on large type; they are noise on a
  dashboard.
- **Who uses it, how often?** Something seen once wants finish. Something seen daily wants to
  get out of the way.

Then pick: **one entrance gesture, two or three named eases with a rule for each, a duration
band, and a stagger.** That is the whole vocabulary, and it fits on half a page.

## 4 · Measure a reference instead of guessing

When the owner names a site, do not describe it from the screenshots. Measure it, with the
Playwright MCP. Three evaluations answer most of it:

1. **Stack and stylesheets.** List `document.scripts` sources; test for the animation libraries
   on `window`; walk `document.styleSheets` for `@keyframes`, transition shorthands, timing
   functions and durations; list `document.getAnimations()` with `effect.getTiming()`. A
   library that is module-scoped and invisible on `window` still leaves inline-style
   fingerprints on split-text wrappers.
2. **Grep the bundles.** `fetch` each same-origin chunk and regex for `ease:`, `duration:`,
   `stagger:`, `scrub:`, `pin:`, `clipPath:`, `lerp:`. **Tally the eases — the distribution is
   the vocabulary**, and it tells you how many decisions the site actually made.
3. **Sample a real reveal.** Reload, then read `opacity` and `transform` of the first heading's
   wrappers every 60ms for two seconds. The curve you get back is the true duration and ease,
   whatever the CSS claims.

Then scroll to two or three positions, wait longer than the longest duration, screenshot, and
read any `position: sticky` elements and their heights.

**The trap:** headless Chromium starts transitions late on first paint. Measure with
`getAnimations()` or computed `opacity`, never with a screenshot taken on a timer — you will
conclude the animation is broken when it had not started.

**Report it as a vocabulary** — what moves, how, on which curve, for how long — and then as
numbered changes to our page. **Take the grammar, never the look.** A measured reference joins
the ease select in the tuning drawer by name, with a preset for its timing, so the owner can
try it rather than be told about it.

## 5 · Write it down, once

The chosen vocabulary goes in **`brain/lenses/motion.md`**, so `/critique` and
`/reviewer motion` judge against the project's own answer instead of a generic one, and the
next session does not re-derive it. The decision that picked it gets logged like any other,
with the values in it.

A measured reference goes in `brain/sources.md` with its date, because a site's motion changes
and a measurement is only true on the day it was taken.

## 6 · Before showing the owner

- **Run it headless at desktop and phone width.** Screenshot each state after waiting longer
  than the longest duration plus stagger.
- **If something looks missing, read computed `opacity` before assuming the CSS is wrong.**
  The usual cause is specificity — an `#id .x` rule beating `.in .x`, or the state class landing
  on an element the selector does not actually chain through.
- **Check the one timed moment finishes quickly** and that nothing else moves unprompted.
- **Check `prefers-reduced-motion`.**
- **Screenshot it with motion disabled** and look at that frame on its own.
- Say in the box which single vocabulary the page uses, and ask only the question the drawer
  cannot answer.

## Appendix · One measured example

Measured 2026-10-02 from two editorial marketing sites built with GSAP and ScrollTrigger.
**This is a sample of what one pair of well-made pages chose, not a standard to copy.** It is
here so the shape of a finished vocabulary is concrete.

> Transform on a cubic ease-out, `cubic-bezier(.215,.61,.355,1)`, 0.5s; opacity on a sine
> ease-out, `cubic-bezier(.39,.575,.565,1)`, 0.35s, run together on the same element. Heavier
> reveals on `cubic-bezier(.165,.84,.44,1)`. Groups at 0.7s with a 0.15s stagger. Ease-in-out
> reserved for decorative idle drift, linear only for a marquee.
>
> Text enters as masked lines: each line wrapped in `overflow: clip`, the inner element rising
> from `translateY(100%)` and `opacity: 0`. Media enters as a `clip-path` wipe from
> `inset(100% 0 0 0)` to `inset(0)` with the image settling from `scale(1.1)`.
>
> Scroll is the timeline — no snap, no auto-advance. Long sections are sticky blocks whose
> height is a multiple of the viewport, scrubbed by scroll progress at `scrub: 0.6–0.8`.

Note what generalises and what does not. The structure — two eases with a rule, a short
duration band, one entrance device reused — is worth copying. The specific curves, the masked
lines and the scroll scrubbing are that kind of site's answer, and a tool, a deck or a quiet
institutional page should reach a different one.
