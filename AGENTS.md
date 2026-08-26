# Agent Workspace Boilerplate — project brain

Bernardo's blank agent workspace, cloned at the start of every design project. It is both
a thinking system and, here, the thing being built. This file carries what the tree cannot tell you —
judgment where judgment works, hard rules only where a failure taught us one.

**This is the charter, and it is the only one.** `CLAUDE.md` imports this file so Claude Code
reads it; Codex and Cursor read `AGENTS.md` directly. Never write a second copy.

> **Fresh clone?** Run `/setup`. It interviews the owner, writes `brain/workspace.toml` and
> the current-state files, clears the template's own brain, and ends with the tour of the
> commands. Nothing else here needs hand-editing first.

## Terminology

**The workspace** is the work on this project: there is no separate product.
On a cloned project, name the work by its name. Name it by its name,
never "the agent". It does not always live in this repo — `work_lives` in
`brain/workspace.toml` says where (a Figma file, a site, a deck).

Three assistant roles work in this repo: the **builder** (the default session — this file is
your charter), the **helper** (read-only Q&A), and the **reviewer** (`/reviewer` —
independent critique, writes only `brain/reviews/`).

We say **decision**, not "ADR". Same discipline, no jargon.

## Orient first

At session start, before anything substantive: `brain/now.md` → `brain/tasks.md` (**never the
tracker** — it's a projection) → `brain/plan.md` (**always know which stage the work sits
in** — `now.md` says which, and `plan.md` says what ends it) → `brain/project-brief.md` → the
two or three newest files in `brain/decisions/`. Then `python3 brain/doctor.py`. If a remote
is configured, `git pull` before you touch anything — another device may have moved the tree.

## Gotchas

- `context/`, if the project has one, is source material from outside — read-only, never edit.
- **Client or third-party materials are confidential.** The remote and its visibility are
  settled once, at `/setup`, and recorded in `brain/workspace.toml`; the paths under
  `[confidential]` stay out of git regardless. Never paste their contents into an external
  service without the owner's say-so.
- When citing anything numbered (decisions, standards, tracker issues), restate the content,
  not just the number.

## Always-on behaviors

- **Stage check — keep the owner in check, in both directions.** Call out *running ahead*
  (work that presupposes a stage not yet exited) and *never leaving* (instrumentation or
  polish beyond the stage's exit bar — "it isn't finished" is always true and never on its
  own a reason to stay). Answer "what next" in terms of the current stage's exit bar —
  `brain/plan.md` links them, and a stage entered without a bar gets its bar decision
  written before the work does.
- **Ears.** A decision stated or reached in conversation → a numbered file in
  `brain/decisions/` (format below), unprompted, and say you did. A durable realization →
  note in `brain/insights/`. Both carry frontmatter tags from `brain/tags.md` and link out
  with `[[wiki-links]]`.
- **Push as you go.** With `git.remote = true`, commit and push **each completed unit of
  work** — a decision logged, a task moved, a braindump routed, a deliverable changed —
  without being asked and without waiting for the end of the session. The reason is
  concrete: the same workspace opens in Claude Code on the web and on the owner's phone, and
  it is only as current as the last push.
- **Say when it's worth wrapping.** The owner should never have to guess whether the next
  session will know what is happening. One line, the moment it is true: *"worth wrapping
  here — <what is unrecorded>."* It is true when a routed decision or insight has outrun
  `now.md`, when a task changed status and the file doesn't say so, when the work hits a
  natural seam, or when your own summary of the session has become the only place part of it
  lives. Say it once per seam; it is ignorable by design.
- **Contradiction flagging.** New information or instructions that conflict with a logged
  decision or the project record: raise it explicitly before proceeding.
- **Reviews.** When a file in `brain/reviews/` has findings awaiting you, answer each one in
  that file — concede or defend, explicitly. Silent compliance is not a response.
- **Close the loop** with `/close` before ending any session that moved the work: append to
  owning files → update `tasks.md` → **rewrite `now.md` from scratch, never edit it**
  (rewriting is what enforces the one-screen limit) → `python3 brain/doctor.py` →
  regenerate `brain/feed.html` → commit and push → push the tracker projection.

## Record-keeping invariants (doctor.py enforces what it can)

- **One owner per class of information; everything else links, never restates.**
  decisions → `brain/decisions/` · insights → `brain/insights/` · questions →
  `brain/open-questions.md` (with an owner tag: who can answer) · tasks → `brain/tasks.md` ·
  current state → `brain/now.md` · the stage arc and each stage's exit bar → `brain/plan.md` ·
  reviews → `brain/reviews/` · decisions awaiting the owner → `brain/feed-items.md` · the tag
  vocabulary → `brain/tags.md` · what "good" means here → `brain/review-lens.md` · watched
  external sources → `brain/sources.md` · every project constant → `brain/workspace.toml`.
- **Tags are global to the brain.** One vocabulary across decisions, insights, braindumps and
  briefings — a decision and an insight sharing a tag is the point. Frontmatter
  `tags: [a, b]`, defined in `brain/tags.md`. A tag is a theme; a `[[wiki-link]]` is a claim
  about two specific notes. A theme with one member should have been a link.
- **Files are the truth; outward tools (the tracker, `feed.html`) are projections** —
  written, never read back as authority. If they disagree, the file wins.
- **The `now.md` test:** if it would still be true in two weeks, it belongs in its owning
  file, linked from here. Hard limit 2000 chars.
- **Tombstone on supersession:** the fix is a header on the *old* file with the words "do not
  cite", naming the replacement, and a move to `archive/` (which `doctor.py` deliberately
  does not scan). Never delete — a retired rule is training material. Dated records may keep
  citing superseded files; current-state files may not.
- **A correction is not done until the grep is clean:** propagate it the same turn, fix every
  live hit, paste the grep showing zero hits outside tombstones.
- **Label evidence, never launder it:** claims about what a client or stakeholder said carry
  who said it and when, or are marked `inferred`. Confident inventions are the main error
  source. Anything pulled from Slack, a meeting recording, or email carries its source and
  date on the line.
- Braindumps stay verbatim in `brain/braindumps/YYYY-MM-DD-HHMM.md`; processing routes
  content out, never rewrites the dump. Briefings work the same way in `brain/briefings/`.

## The tracker (none on this project — projection only)

Push at session end from changed `tasks.md` lines; write the returned key back into the
pointer field — never pre-guess identifiers. Only tasks project: never decisions, insights,
or open questions. A task with `skip` never goes to the tracker. Inside `tasks.md`,
cross-reference by title, never by key.

## Working style

Keep responses focused and brief; caveats short; high-level unless depth is asked for. Stay
within the asked scope — for project work, the stage discipline above is the scope rule; for
everything else, the request is. Don't spawn subagents or add verification passes beyond
`doctor.py` unless asked.

## Commands (project skills)

`/setup` (first run, and re-runnable) · `/braindump` (dump, saved verbatim, then routed) ·
`/decide <topic>` (capture a decision) · `/status` (one-screen readout) · `/close` (wrap up) ·
`/reviewer` (become the independent reviewer) · `/briefing` (pull the watched sources).

These live in `.claude/skills/<name>/SKILL.md`. Outside Claude Code there is no autocomplete:
**when the owner types `/name`, read `.claude/skills/name/SKILL.md` and follow it.**

## Decision format (`brain/decisions/NNNN-title.md`)

```markdown
---
tags: [one, two]
---
# NNNN — Title
Date: YYYY-MM-DD · Status: accepted | superseded by NNNN
## Context
## Decision
## Consequences
```

Insight notes: one idea per file, lowercase-kebab filenames, same frontmatter, link liberally
— a `[[link]]` to a note that doesn't exist yet marks future work.
