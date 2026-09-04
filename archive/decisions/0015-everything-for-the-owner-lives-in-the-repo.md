---
tags: [process, handoff]
---
# 0015 — Everything for the owner lives in the repo
Date: 2026-09-04 · Status: accepted

## Context

The assistant drafted an email for the owner to send and saved it as a markdown file in its
own scratch directory — a session-specific path outside the repo:

> *"How am I supposed to know how to access the scratchpad? There should be a drafts folder
> inside brain."*

The scratchpad is the right place for the assistant's working files and the wrong place for
anything the owner has to act on: its path is unguessable, it is outside the tree that gets
pushed, and a message he cannot find is a message he never sends.

The cause was worse than a missing folder. `feed.py` already read a `comms/outbound` directory
and rendered a thread from it, complete with a "draft, unsent" pill. Nothing in `AGENTS.md`,
the README or any skill mentioned it, and no clone ever created the folder. So there was no
findable answer to "where does a draft go", and the scratch directory won by default.
**Undocumented scaffolding is worse than no scaffolding** — it looks like a decision has been
made without making one.

## Decision

`brain/drafts/` owns anything written for the owner to send: email, Slack message, a comment
on someone else's ticket. One file per message, `YYYY-MM-DD-slug.md`, with `to`, `channel`,
`subject` and `status` in frontmatter, and **the body being exactly what gets sent** — no
heading, no note about the draft — so the whole body pastes into Gmail or Slack unedited.

`feed.html` lists the unsent ones first, each with a button that copies the body, and keeps
the sent ones as a quiet record underneath. A draft addressed to nobody renders in red; one
unsent for a week gets a pill. `doctor.py` reports the same three failures. Drafts stay after
sending, with the body updated to what was actually sent — a record that disagrees with what
the client received is worse than none, because the next session will quote it.

The `comms/` code path is replaced rather than left beside this one.

The charter gets the general rule and not just this case: **everything for the owner lives in
the repo, in the folder that owns it, and you say the path.** The test is whether he could find
it tomorrow without asking.

## Consequences

- `brain/drafts/` is the fourth thing on the feed that is explicitly "waiting on you", which
  is beginning to be the page's real subject.
- What was said to a client is now part of the record, which the evidence-labelling rule in
  [[0014-the-brief-is-a-gate-and-evidence-is-cited-quietly]] can cite like any other source.
- The general rule does the work here. This bug was one instance; the charter now covers the
  class, so the next one of its kind does not need its own decision.
- Worth watching for elsewhere in the workspace: code that reads a path nothing documents. It
  is the shape of failure this decision came from, and `comms/` was not necessarily the only one.
