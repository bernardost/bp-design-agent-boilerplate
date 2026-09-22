# `explorations/` — options, not decisions

`YYYY-MM-DD-<topic>.md`, written by `/explore`. This directory owns **directions that were
considered**, which is a different class of information from every other file in the brain.

**Why it is separate.** Everything else here records what is settled: a decision was reached,
an insight was realized, a task exists. An exploration is the opposite — a spread of options,
most of which will die. Filed in `decisions/` they would corrupt the decision log with
choices nobody made; filed in `insights/` they would claim a durability they have not earned.

**Upstream of this is `brain/moodboards/`**, which holds what the research *means* — ideas
grouped into narratives. A board argues; a spread answers it with directions; a decision picks
one. Directions generated with no board behind them are guesses with specimens attached.

## The rules

- **Never edited into a decision.** When a direction is picked, that produces exactly one new
  `YYYY-MM-DD-slug.md` file in `brain/decisions/` — *we picked C, here is why, here is what it costs* —
  which wiki-links back to this exploration by its filename. That single link is the entire seam
  between diverging and converging, and it is the only one.
- **Rejected directions stay.** They are the point of keeping the file. A direction that was
  wrong for this project may be right for the next one, and a direction that a model could
  not execute this year is worth re-running on a better one. Deleting them costs the whole
  archive to save a few kilobytes.
- **The seed is part of the record.** An exploration that does not carry the seed string that
  produced it cannot be re-run, which makes it an anecdote rather than a record.
- **Nothing here is authority.** `now.md` may say the work is exploring; it may not cite a
  direction as though it were chosen.
- **Every direction carries a specimen.** Eight directions described in prose is a wall of
  text, and a wall of text gets judged on which one was *described* best. The specimen is
  what makes the spread comparable at a glance, so it is part of the file, not a nicety.

## The specimen

A fenced ` ```specimen ` block inside each direction: self-contained HTML and CSS, no scripts,
no external assets, **forty to sixty lines**. The palette *in use* rather than as swatches,
the type pairing set in the real faces at three sizes with real words, and the layout logic as
an actual composition. `python3 brain/spread.py` renders the file to a page next to it, each
specimen inside a sandboxed frame — so a direction's own colours and type are its own, and
cannot be overridden by the page around them or leak into it.

**Composed for 4:3.** That is the frame `spread.py` renders into. A specimen that overruns it
scrolls rather than being cropped, but a design whose bottom edge is off-screen gets judged
wrong, so compose to fit.

**Big enough to judge.** A swatch card cannot be judged, and a direction nobody can judge gets
picked on its prose instead. The page gives a specimen three to four times the area it gives
the words about it, and that ratio is the point of the page.

**The same content in every specimen.** The `Content:` line at the top of the file holds the
real words — a headline, a paragraph, a label, a number, an action — and every direction
renders those, in the same frame. This is what lets a specimen be fleshed out without the
best-written pitch winning: hold the content constant and the only variable left is the
design.

**A specimen is still not a mockup.** It shows how a direction handles type, colour, space and
hierarchy on one representative composition — never the product's navigation, its real routes,
or eight sections. Building the screen at pitch stage is how a well-executed weak idea beats a
roughly-sketched strong one, and it makes the command slow enough that nobody runs it. The
screen belongs to the stage after this one. The rendered page is a projection like any other:
delete it and nothing is lost, because this file is the record.

## The file shape

```markdown
---
tags: [concept, craft]
project: <key>           # or `all`; omit entirely in a one-project workspace
---
# YYYY-MM-DD · <what was being explored>
Seed: <the string> · Brief: <one line — what was asked for>

Content: <the headline · the paragraph · the label · the number · the action — the real words
every specimen on this page renders, written once so the directions differ by design and not
by who got the better sentence>

## Directions
### A — <name>
<one line: what this direction believes that the others do not>
Verdict: live | rejected — <the reason, in the owner's words where there are any>

```specimen
<div style="height:100%;background:#faf8f4;padding:16px;font:13px/1.5 Inter,sans-serif">
  … swatches, the type pairing set for real, the layout logic as a few blocks …
</div>
```

### B — <name>
…

## Where it went
<blank until a direction is picked, then one line naming the decision file>
```

An exploration with every direction rejected is a good outcome and stays filed. An
exploration with no verdicts is unfinished — `doctor.py` reports it.
