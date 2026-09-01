---
name: explore
description: Generate genuinely different design directions before committing to one — seeded for variety, sharpened against the owner's taste, filed in brain/explorations/. Use for /explore, "give me options", "what else could this be", or whenever work is about to converge on the first idea anyone had.
---

# Explore — go wide on purpose

Every other command in this workspace converges: decisions get logged, bars get met, the
record gets tightened. This one is the opposite, and it is the only one. Its job is to put
real alternatives on the table before the work commits, and to make sure they are *different
from each other* rather than three versions of the same instinct.

## Why the seed matters

Asked for a design with no constraint, a model returns the most probable one — which is the
same one it returned last time and the same one it returned for someone else. That is not a
failure of effort; it is what predicting the likely next token does. The fix is to make the
starting point arbitrary, so the direction is derived rather than recalled.

```bash
head -c 96 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 48; echo
```

Read the string for structure — runs, repeats, symmetry, numbers that suggest a ratio, a
substring that reads like a word — and let what you find set the direction: palette, layout
logic, type pairing, motion, material. **Never show the string in the work, and never explain
a design choice by pointing at it.** It is a starting position, not a meaning. One fresh seed
per direction; reusing one seed for all of them reproduces the problem.

## The run

**1 · Take the brief in one line.** What is being designed, and for whom. If the owner has a
feeling but not a brief, that is fine — capture the feeling verbatim, it is worth more than a
tidied version of it.

**2 · Go broad, not deep.** Generate **six to eight** directions, seeded separately, two or
three lines each. Name each one. At this stage they are pitches, not designs — resist
building.

Then check the spread honestly before showing them: if four of them differ only in colour,
they are one direction and you owe the owner three more. Real variance means disagreeing
about layout logic, density, tone, and what the work is *for*, not about hue. Include at
least one that is uncomfortable — the rule the article and the practice agree on is that the
safe six are the ones nobody remembers. Say which one that is.

**3 · Sharpen against the owner's taste, and this is the step that matters.** Ask what they
react to, and take the reaction in their own words — *"tactile, clicky, satisfying; I pictured
cartoony and it felt tacky; needs texture"* is usable, *"more modern"* is not. Push back for
specifics when what you get is an adjective that rejects nothing.

Then rewrite the shortlist through what they said. This is the whole point of the command:
directions the owner steered are ones only this project could have produced, where directions
the model picked unaided are ones any project would have.

**4 · Record verdicts.** Every direction gets `live` or `rejected` and a reason. Rejected
directions stay in the file — see `brain/explorations/README.md` for why.

**5 · Write the file.** `brain/explorations/YYYY-MM-DD-<topic>.md`, in the shape that README
specifies, seeds included. Tag it from `brain/tags.md`.

**6 · Hand over a build prompt.** For each surviving direction, write a concise prompt that
an agent could build a first pass from: the aesthetic, the layout logic, what it must not do,
and the one thing that makes it that direction and not another. Then stop. Building is not
this command's job, and `/critique` is what raises the first pass afterwards.

## Picking, later

When the owner picks, that is a decision and it gets logged like any other — one numbered
file in `brain/decisions/` saying what was picked, why, and what it costs, linking back to
the exploration with `[[YYYY-MM-DD-topic]]`. **That link is the only seam between this
directory and the record.** Until it exists, nothing in the brain may treat a direction as
chosen, and `now.md` says the work is exploring rather than naming a direction.

## Guardrails

- **Exploring is a stage state, not stage drift.** The charter's stage check flags work that
  runs ahead of the current stage; going wide inside the stage you are in is not that. It
  ends when a direction is picked, and if it has not ended after two rounds, say so — that is
  a real signal, and usually it means the brief is the thing that is unclear.
- **Do not explore what is already decided.** Check `brain/decisions/` first. Re-opening a
  settled question needs the owner to say they are re-opening it; quietly generating
  alternatives to a logged decision is contradiction, and the charter says raise it instead.
- **Do not converge early.** Recommending a favourite in step 2 collapses the spread you were
  asked to produce. Recommend after step 3, when the owner's taste is in the room.
- **Do not carry the house style into the work.** `AGENTS.md` describes how artifacts *for
  the owner to read* should look. It is not the product's aesthetic, and a direction that
  inherits it by default is one direction fewer.
