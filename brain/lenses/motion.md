# Lens · motion

*Does the work move the way this project decided it should? `/reviewer motion <scope>`, and
the standard `/critique` scores motion against during a build.*

**Sections 3 and 4 are this project's own answer and start empty.** `/motion` fills them once a
vocabulary is chosen, and the decision that chose it is logged like any other. **Until they are
written, say so in the verdict** rather than quietly scoring against a generic ideal — a
project whose motion has not been decided cannot fail a review for disagreeing with one.

## 1 · What to look at

**The thing running**, at desktop and phone width. Motion cannot be reviewed from source or
from a still, and a screenshot taken on a timer will tell you an animation is broken when it
had not started. Measure with `getAnimations()` or computed `opacity`.

Also look at it **with motion disabled**. If that frame is weak, the finding is about the
composition and belongs to `craft.md`.

## 2 · What to refuse to look at

The implementation, the library, and the builder's reasoning. A reader experiences timing, not
a timeline object.

One permitted input: **which context this is** — a long scrolling page, an app UI, a presented
deck, or a prototype. Several rules invert between them, so a review that does not know which
one it is reviewing is guessing.

## 3 · This project's vocabulary

*(Filled by `/motion`. One entrance gesture, the named eases and the rule for which goes where,
the duration band, the stagger. Half a page. Until it exists, say so.)*

## 4 · What is explicitly not the standard here

*(Name the motion this project has decided against, and anything a reference was measured for
but not adopted. Without this, every review re-litigates a settled question.)*

## 5 · What it is judged on regardless

These hold whatever the project chose, and a finding against one of them stands even when
sections 3 and 4 are empty.

1. **One vocabulary.** Every element enters the same way. Three different entrances means the
   page reads as assembled from parts.
2. **At most one timed moment**, finishing quickly, and nothing else moving unprompted. Zero in
   an app UI.
3. **Nothing loops in the content.** Idle loops are decoration, never the thing being read.
4. **A small fixed set of eases.** Count the distinct curves on the page — that number is a
   good proxy for whether anyone decided anything.
5. **Duration from the ease's tail, not from a big number.** Past about a second, a reveal the
   reader is waiting for reads as sluggish.
6. **Hover dips, never jumps.** Nothing bounces, nothing moves position under the cursor.
7. **`prefers-reduced-motion` is honoured** and the page still works. This one is a FAIL, not a
   note.
8. **No tuning drawer**, if this is going to a client. `/prototype` ships one; it is stripped
   before anyone outside sees the work.

## The score

Same scale as `craft.md`. A broken `prefers-reduced-motion`, or more than one timed moment,
caps it at 5 whatever else is true.
