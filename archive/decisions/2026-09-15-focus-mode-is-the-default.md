---
tags: [process]
---
# [[focus-mode-is-the-default]] — Focus mode is the default, and the final message carries everything
Date: 2026-09-15 · Status: accepted

## Context

Claude Code added `/focus`, which hides tool calls and shows only the final message of each
turn. The owner wants it on by default:

> *"If that could be the standard way of working, I think that would be nice, but the agent
> should tell the user that /focus can be switched off."* ^[owner · session · 2026-09-15]

It fits what decision [[the-reply-has-two-zones]] already established. That decision split the reply into a zone of
one-line process notes and a zone of things the owner has to act on, because the two were
arriving mixed. Focus mode enforces the same split at the harness level: the process zone
simply is not shown.

## Decision

`AGENTS.md` assumes focus mode is on. Two rules follow.

**Say it once.** Early in the first session, one line — *"writing for focus mode; `/focus`
turns it off if you want to watch the work"* — and never again. A default the owner cannot
turn off is a trap, and a default explained every session is noise.

**The final message is the only message.** Nothing important may live only in a mid-turn line
or a tool call: no "as I said above", no finding that appeared once while the work was
happening and was never restated. The mid-work one-liners stay in the charter, because they
are still right when focus is off and they still make the transcript readable, but they carry
nothing the final message does not.

`/setup` recommends turning focus mode on, in the same breath as saying how to turn it off.

## Consequences

- [[the-reply-has-two-zones]]'s two-zone rule is now the mechanism behind a harness feature rather than only a style
  preference, which makes it harder to drift away from.
- The box at the end of a reply matters more, not less: under focus mode it is the only place
  the owner's half of the session appears.
- Sessions get quieter. The cost is that a lazy reply — one that gestured at work done rather
  than reporting it — now reads as an empty turn, which is the correct failure mode.
