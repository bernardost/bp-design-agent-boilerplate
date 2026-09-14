---
tags: [process]
---
# 0016 — Close is one command, and a few minutes

Date: 2026-09-14 · Status: accepted

## Context

Testing the template, the owner's report was that `/close` takes too long. Measured, the four
scripts it ran are not the cost: `doctor.py`, `feed.py`, `spread.py` and `brief.py` together
take 0.2 seconds of CPU. The cost was shape, in two places.

Four commands meant four round trips at the tail of every session, which is the part a person
waits through. And the skill's own framing — eight numbered steps, "a sequence, not a menu",
six routing destinations to consider in step 1 — read as an instruction to re-derive the whole
session from scratch, even though push-as-you-go means most of it is already on disk by then.

## Decision

`brain/render.py` runs the four `main()`s in one process, under labelled rules, exiting on
doctor's code. `/close` step 5 and the charter's close line call that one command. Each script
stays independently runnable, because `/explore` and `/brief` call them singly.

The close skill now says what it is: catching the remainder, not re-deriving the session;
steps 1 to 4 write to four different files and are read in one batch; a step whose answer is
"nothing" is not narrated.

## Consequences

- One tool call where there were four, and the skill no longer invites a step-by-step crawl.
- `render.py` adds no behavior of its own. Anything it appears to do differently from running
  the four by hand is a bug in `render.py`, not a new rule.
- A close that outlasts the work it records is one that gets skipped — that is the failure
  this is aimed at, and it is worth re-measuring on a session with real content to route.
