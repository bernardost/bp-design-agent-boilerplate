---
tags: [process]
---
# [[stop-slop-is-embedded-not-vendored]] — The prose rules are embedded, not vendored
Date: 2026-09-15 · Status: accepted

## Context

The owner found `stop-slop` (Hardik Pandya, MIT) and asked whether to package it with this
workspace:

> *"Should we package it with the agent? should we somehow embed it in the agent? So it speaks
> more naturally. I don't want to bloat the agent too much but it does improve my understanding
> of what the agent is saying."* ^[owner · session · 2026-09-15]

Three facts settled it. He already has the skill installed globally, so a copy in
`.claude/skills/` would be a second owner of one set of rules, drifting from upstream the first
time it is updated. A skill reaches Claude Code only, and this repo's charter is read by Codex
and Cursor too. And most of the skill already exists here: the "Do not" list under *How to talk
to the owner* bans stock phrases, analogies, flattery, quotability and imposed skeletons.

## Decision

Vendor nothing. Add the delta to `AGENTS.md` as a short subsection, *The sentences themselves*,
scoped to every piece of prose the repo produces rather than to replies alone.

Seven rules the charter did not have: name the actor instead of letting an inanimate thing take
a human verb, active voice, no throat-clearing openers, no "not X, it's Y", no vague
declaratives, cut the adverbs doing no work, vary the rhythm.

Three of the skill's rules were rejected, each for a stated reason:

- **"Remove every em dash."** That rule exists to avoid detection, not to be understood. This
  charter and every file in `brain/` are written with em dashes and read well. The habit gets
  capped at roughly one per paragraph instead.
- **"Kill all adverbs."** Narrowed to the ones doing no work, because an adverb that changes
  the meaning of its sentence is doing work.
- **The 1–10 scoring table.** `/critique` already owns scoring against a lens, and a second
  scoring loop for prose would be the bloat the owner asked to avoid.

## Consequences

- The rules reach Codex and Cursor, which a skill never would.
- `AGENTS.md` grows by about twenty lines and gains no new file, directory or command.
- The upstream skill stays the owner's, global and updatable, with no fork here to maintain.
- The em-dash carve-out is written down, so a later session does not quietly strip them and
  claim the charter said to.
