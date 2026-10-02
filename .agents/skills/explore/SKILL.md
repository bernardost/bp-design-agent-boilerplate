---
name: explore
description: Generate genuinely different design directions before committing to one — seeded for variety, sharpened against the owner's taste, filed in brain/explorations/ and rendered as a page you can judge at a glance. Use for /explore, "give me options", "what else could this be", or whenever work is about to converge on the first idea anyone had.
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

**0 · Know what you are exploring from.** If `brain/moodboards/` holds a board for this
strand, its surviving visions are the brief — the directions here are answers to what the
board argued, and an exploration that ignores one is starting from the model's priors again.
If there is no board and the research has piled up unread, say in one line that `/moodboard`
comes first. Options generated before anyone said what the work is about are six ways of
guessing.

**1 · Take the brief in one line.** What is being designed, and for whom. If the owner has a
feeling but not a brief, that is fine — capture the feeling verbatim, it is worth more than a
tidied version of it.

**2 · Go broad, not deep.** Generate **six to eight** directions, seeded separately. Name
each one and give it **a one-line thesis** — what this direction believes that the others do
not. One line, not a paragraph: the page is for looking, and every sentence you add is space
taken from the thing being looked at.

**3 · Write a real specimen.** Forty to sixty lines of self-contained HTML and CSS, showing
the palette in use rather than as swatches, the type pairing set in the real faces at three
sizes with real words, and the layout logic as an actual composition. Fleshed out enough that
taste can act on it — a swatch card cannot be judged, and a direction nobody can judge is one
that gets picked on its prose.

**The control that makes this safe: every specimen renders the same content, in the same
frame.** Write that content once, in the `Content:` block at the top of the file — a real
headline, a real paragraph, a real label, a real number, a real action. Then the specimens
differ by *direction* and not by who got the better sentence, which is what keeps the
best-executed pitch from beating the best idea. Same words, same frame, different design.

**Fit the frame.** The page renders each specimen at 4:3. Compose for that — a specimen that
overruns scrolls, and a design judged with its bottom edge off-screen is judged wrong.

Still not a screen. A specimen shows how this direction handles type, colour, space and
hierarchy on one representative composition — not the product's navigation, not its real
routes, not eight sections. If you find yourself building the page, you have left this command
and should be in `/prototype`.

Then check the spread honestly: if four of them differ only in colour, they are one direction
and you owe the owner three more. Real variance means disagreeing about layout logic,
density, tone, and what the work is *for*, not about hue. Include at least one that is
uncomfortable — the safe six are the ones nobody remembers. Say which one that is.

**4 · Write the file, render it, and hand over the page.** The markdown goes to
`brain/explorations/YYYY-MM-DD-<topic>.md` in the shape README specifies, seeds included,
tagged from `brain/tags.md`. Then `python3 brain/spread.py` and give the owner the path.

Do this *before* asking for reactions, not after. Eight directions pasted into a chat window
is too much to judge, so what gets judged is whichever one you described best. The page puts
the specimens side by side, which is what lets taste act on the work rather than on the prose
about it. Your own spread check gets easier here too: if the eight specimens look alike on
one screen, they were one direction and no amount of distinct prose changes that.

**5 · Sharpen against the owner's taste, and this is the step that matters.** Ask what they
react to, and take the reaction in their own words — *"tactile, clicky, satisfying; I pictured
cartoony and it felt tacky; needs texture"* is usable, *"more modern"* is not. Push back for
specifics when what you get is an adjective that rejects nothing.

Then rewrite the shortlist through what they said. This is the whole point of the command:
directions the owner steered are ones only this project could have produced, where directions
the model picked unaided are ones any project would have.

**6 · Record verdicts and re-render.** Every direction gets `live` or `rejected` and a reason.
Rejected directions stay in the file, and stay on the page — greyed and in place, never
deleted. See `brain/explorations/README.md` for why. Re-run `spread.py` so the page and the
file agree.

**7 · Hand over a build prompt.** For each surviving direction, write a concise prompt that
an agent could build a first pass from: the aesthetic, the layout logic, what it must not do,
and the one thing that makes it that direction and not another. Then stop. Building is not
this command's job, and `/critique` is what raises the first pass afterwards.

## Picking, later

When the owner picks, that is a decision and it gets logged like any other — one
`YYYY-MM-DD-slug.md` file in `brain/decisions/` saying what was picked, why, and what it
costs, carrying the same `project:` key as the exploration and linking back to it with
`[[YYYY-MM-DD-topic]]`. **That link is the only seam between this
directory and the record.** Until it exists, nothing in the brain may treat a direction as
chosen, and `now.md` says the work is exploring rather than naming a direction.

## Guardrails

- **Exploring is a stage state, not stage drift.** The charter's stage check flags work that
  runs ahead of the current stage; going wide inside the stage you are in is not that. It
  ends when a direction is picked, and if it has not ended after two rounds, say so — that is
  a real signal, and usually it means the brief is the thing that is unclear.
- **Explore one project at a time.** The directions are judged against that strand's brief
  and its lens, and a spread mixing two strands compares things that were never alternatives.
  The file carries that strand's `project:` key.
- **Do not explore what is already decided.** Check `brain/decisions/` first. Re-opening a
  settled question needs the owner to say they are re-opening it; quietly generating
  alternatives to a logged decision is contradiction, and the charter says raise it instead.
- **Do not converge early.** Recommending a favourite in step 2 collapses the spread you were
  asked to produce. Recommend after step 4, when the owner's taste is in the room.
- **The page is a projection, never the record.** `spread.py` writes HTML next to the
  markdown and never reads it back. If the two disagree, the file wins and you re-render.
- **Do not carry the house style into the work.** `AGENTS.md` describes how artifacts *for
  the owner to read* should look. It is not the product's aesthetic, and a direction that
  inherits it by default is one direction fewer.
