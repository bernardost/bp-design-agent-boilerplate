# Lens · craft

*Is the work any good to look at? `/reviewer craft <scope>`. Also the standard `/critique`
scores against during a build, which is why the two stay in sync by both reading this file.*

**If this file is still a template below the line, say so in the verdict** rather than quietly
scoring against nothing. `/setup` fills sections 3 and 4; the rest ships as written.

## 1 · What to look at

**The rendered artifact, and nothing else.** A screenshot, an exported frame, the live URL,
the printed page. If it cannot be seen, it cannot be reviewed under this lens — ask for a
render rather than reading the source and imagining one.

Judge at two scales in the same pass, and say which scale each finding belongs to:

- **Composition** — the shape of the whole. Hierarchy, focal point, rhythm, density, where
  the eye goes first and whether that is the right place.
- **Detail** — the fine grain. Optical alignment, spacing consistency, type colour, corner and
  shadow logic, the moments a real designer would have fussed over.

## 2 · What to refuse to look at

The code, the decisions, the brief, the builder's reasoning, and the conversation that
produced the work. Knowing what it was *trying* to do is exactly what stops you noticing that
it did not. If context arrives anyway, review the render as if it had not.

The one permitted input beyond the artifact is `brain/references/` — the quality bar as
images. Those are the standard to *measure against*, never a thing to copy toward.

## 3 · What it is judged on

**The question, asked in this order:** What aesthetic is this work reaching for? How would a
studio at the top of its field execute that same intent? Where are the biggest gaps between
the two? Be specific and bold — a safe note is worth less than a wrong one.

1. *(Fill at `/setup`: what this project's work should feel like, in the owner's own words.
   "Tactile, clicky, satisfying — not cartoony" beats "clean and modern", which describes
   nothing and rejects nothing.)*
2. *(The non-negotiables — brand, accessibility floor, platform conventions this must obey.)*
3. **Restraint.** What would you delete? Additive drift is the default failure: elements
   accumulate, nothing is ever removed, and the result explains itself instead of working.
   Every pass names at least one thing to cut, or states plainly that the work is already
   tight — those are the only two acceptable answers.
4. **AI tells.** Penalize them explicitly and by name. The standing list, extend it per
   project:
   - a gradient, glow, or blur standing in for art nobody made
   - centred hero: headline, subhead, two buttons, nothing at risk
   - a row of three identical cards, icon on top
   - one corner radius and one shadow applied to everything, with no light source implied
   - emoji doing an icon's job
   - a label on every element, because nothing was trusted to be self-evident
   - text that describes what the reader can already see
   - copy that asserts rather than says: *powerful, simple, beautiful, seamless*
   - perfect symmetry with no focal point, or decoration that never resolves into meaning
   - one sans, one weight, one size ramp, applied evenly and meaning nothing

## 4 · What is explicitly not the standard here

*(Name what you do not want flagged: visual territory already settled, work still in
exploration, anything a later stage owns. Without this the craft lens re-litigates decided
questions every pass, which is how a critic gets ignored.)*

## The score

One number, `n/10`, on how close the artifact sits to studio-grade for the intent it is
reaching for — not to a generic ideal, and not to the reviewer's own taste.

| | |
|---|---|
| **1–3** | reads as generated. Multiple tells from the list above, no point of view. |
| **4–6** | competent and forgettable. Nothing wrong; nothing anyone would remember. |
| **7–8** | a clear point of view, executed unevenly. Name what is holding it back. |
| **9** | a studio could ship it. Remaining notes are preferences, and say so. |
| **10** | reserve it. A 10 you give away costs the 9 its meaning. |

**The stop: 9 or higher, judged in fresh context, on a render the judge has not scored
before.** Below that, findings are what to fix next. A score is not a finding — a pass that
returns only a number has failed.
