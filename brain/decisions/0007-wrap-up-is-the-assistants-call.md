---
tags: [portability, interface]
---
# 0007 — Wrap-up is the assistant's call to make, out loud
Date: 2026-08-26 · Status: accepted

## Context

The owner names the anxiety precisely: *"A common axiety is portability - closing an IDE and
having the next agent know what is happening. I know now.md and the other files solve for
that, but the user needs to know when a wrap up is needed."*

The mechanism exists — `now.md`, `tasks.md`, the decision log, close-the-loop — and it is
entirely dependent on someone remembering to invoke it at a moment (the end of a long
session) when remembering is least likely. The charter told the assistant to close the loop
and told the owner nothing about when to ask for it.

## Decision

The assistant owns the signal, and says it in one line the moment it is true:
**"worth wrapping here — <what is unrecorded>."** It is true when any of these hold:

- a decision, insight, or braindump has been routed but `now.md` has not caught up;
- a task changed status and the file does not say so;
- the work reached a natural seam — a stage bar met, a deliverable shipped, a question
  answered;
- the session has run long enough that the assistant's own summary of it is now the only
  place some of it lives.

`/close` performs the ritual so it is one word, not a checklist the owner recites: append to
owning files → update `tasks.md` → **rewrite `now.md` from scratch** → `python3
brain/doctor.py` → regenerate `feed.html` → commit and push
([[0006-a-private-remote-and-push-as-you-go]]) → project changed task lines to the tracker.

Push-as-you-go does not replace this. Pushing keeps the *files* current; the wrap-up is what
makes `now.md` true, and `now.md` is what the next session reads first.

## Consequences

- The owner never has to know the ritual, only to say yes.
- The signal will sometimes fire when the owner wants to keep going. It is one line and
  ignorable by design; nagging twice for the same seam is the failure mode to avoid.
- `now.md` must be rewritten, never edited. Rewriting is what enforces the one-screen limit.
