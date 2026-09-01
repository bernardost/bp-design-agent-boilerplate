# `explorations/` — options, not decisions

`YYYY-MM-DD-<topic>.md`, written by `/explore`. This directory owns **directions that were
considered**, which is a different class of information from every other file in the brain.

**Why it is separate.** Everything else here records what is settled: a decision was reached,
an insight was realized, a task exists. An exploration is the opposite — a spread of options,
most of which will die. Filed in `decisions/` they would corrupt the decision log with
choices nobody made; filed in `insights/` they would claim a durability they have not earned.

## The rules

- **Never edited into a decision.** When a direction is picked, that produces exactly one new
  numbered file in `brain/decisions/` — *we picked C, here is why, here is what it costs* —
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

## The file shape

```markdown
---
tags: [concept, craft]
---
# YYYY-MM-DD · <what was being explored>
Seed: <the string> · Brief: <one line — what was asked for>

## Directions
### A — <name>
<two or three lines: the idea, and what makes it different from the others>
Verdict: live | rejected — <the reason, in the owner's words where there are any>

### B — <name>
…

## Where it went
<blank until a direction is picked, then one line naming the decision file>
```

An exploration with every direction rejected is a good outcome and stays filed. An
exploration with no verdicts is unfinished — `doctor.py` reports it.
