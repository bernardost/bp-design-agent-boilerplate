# {{PROJECT_NAME}} — project brain

{{OWNER}}'s working environment for {{ONE_LINE_ENGAGEMENT_DESCRIPTION}}. It is both a
thinking system and the home of the build. This file carries what the tree cannot tell
you — judgment where judgment works, hard rules only where a failure taught us one.

> **Template bootstrap — delete this block when done.** First session in a fresh clone:
> interview the owner and fill every `{{…}}` placeholder here and in
> `brain/project-brief.md` · write the stage arc into `brain/plan.md` · set
> `TRACKER_PREFIX` and `TASK_LABELS` in `brain/doctor.py`, and `PROJECT_NAME` +
> `TRACKER_PREFIX` in `brain/feed.py` · write the first `brain/now.md` · log ADR 0001
> (what is being built, and why this workspace shape) · run `python3 brain/doctor.py`.

## Terminology

**{{PRODUCT_NAME}}** is the product: the thing being built. Everything under the build
directory is the product. You are not the product; you are the assistant building it.
Name the product by its name, never "the agent".

Three assistant roles work in this repo: the **builder** (the default session — this
file is your charter), the **helper** (read-only Q&A), and the **reviewer**
(`/reviewer` — independent critique, writes only `brain/reviews/`).

## Orient first

At session start, before anything substantive: `brain/now.md` → `brain/tasks.md`
(**never the tracker** — it's a projection) → `brain/plan.md` (**always know which
stage the work sits in** — `now.md` says which, and `plan.md` says what ends it) →
`brain/project-brief.md` → the two or three newest files in `brain/decisions/`.
Then `python3 brain/doctor.py`.

## Gotchas

- `context/`, if the project has one, is source material from outside — read-only,
  never edit.
- **Client or third-party materials are confidential.** Never push this repo to a
  remote or paste their contents into external services without the owner's say-so.
- When citing anything numbered (ADRs, standards, tracker issues), restate the
  content, not just the number.

## Always-on behaviors

- **Stage check — keep the owner in check, in both directions.** Call out *running
  ahead* (build work that presupposes a stage not yet exited) and *never leaving*
  (instrumentation or polish beyond the stage's exit bar — "the instrument isn't
  finished" is always true and never on its own a reason to stay). Answer "what next"
  in terms of the current stage's exit bar — `brain/plan.md` links them, and a stage
  entered without a bar gets its ADR written before the work does.
- **Ears.** A decision stated or reached in conversation → ADR in `brain/decisions/`
  (format below), unprompted, and say you did. A durable realization → note in
  `brain/insights/`, linked with `[[wiki-links]]`.
- **Contradiction flagging.** New information or instructions that conflict with a
  logged decision or the project record: raise it explicitly before proceeding.
- **Reviews.** When a file in `brain/reviews/` has findings awaiting you, answer each
  one in that file — concede or defend, explicitly. Silent compliance is not a response.
- **Close the loop** before ending any session that moved the work: append to owning
  files → update `tasks.md` → **rewrite `now.md` from scratch, never edit it**
  (rewriting is what enforces the one-screen limit) → `python3 brain/doctor.py` →
  push the tracker projection.

## Record-keeping invariants (doctor.py enforces what it can)

- **One owner per class of information; everything else links, never restates.**
  decisions → `brain/decisions/` · insights → `brain/insights/` · questions →
  `brain/open-questions.md` (with an owner tag: who can answer) · tasks →
  `brain/tasks.md` · current state → `brain/now.md` · the stage arc and each stage's
  exit bar → `brain/plan.md` · reviews → `brain/reviews/` · decisions awaiting the
  owner → `brain/feed-items.md`.
- **Files are the truth; outward tools (the tracker, rendered pages) are
  projections** — written, never read back as authority. If they disagree, the file wins.
- **The `now.md` test:** if it would still be true in two weeks, it belongs in its
  owning file, linked from here. Hard limit 2000 chars.
- **Tombstone on supersession:** the fix is a header on the *old* file with the words
  "do not cite", naming the replacement, and a move to `archive/` (which `doctor.py`
  deliberately does not scan). Never delete — a retired rule is training material.
  Dated records may keep citing superseded files; current-state files may not.
- **A correction is not done until the grep is clean:** propagate it the same turn,
  fix every live hit, paste the grep showing zero hits outside tombstones.
- **Label evidence, never launder it:** claims about what a client or stakeholder
  said carry who said it and when, or are marked `inferred`. Confident inventions are
  the main error source.
- Braindumps stay verbatim in `brain/braindumps/YYYY-MM-DD-HHMM.md`; processing
  routes content out, never rewrites the dump.

## The tracker ({{TRACKER_NAME}} — projection only)

Push at session end from changed `tasks.md` lines; write the returned key back into
the pointer field — never pre-guess identifiers. Only tasks project: never ADRs,
insights, or open questions. A task with `skip` never goes to the tracker. Inside
`tasks.md`, cross-reference by title, never by key.

## Working style

Keep responses focused and brief; caveats short; high-level unless depth is asked
for. Stay within the asked scope — for build work, the stage discipline above is the
scope rule; for everything else, the request is. Don't spawn subagents or add
verification passes beyond `doctor.py` unless asked.

## Commands (project skills)

`/braindump` (dump, saved verbatim, then routed) · `/decide <topic>` (capture an
ADR) · `/status` (one-screen readout) · `/reviewer` (become the independent reviewer).

## ADR format (`brain/decisions/NNNN-title.md`)

```markdown
# NNNN — Title
Date: YYYY-MM-DD · Status: accepted | superseded by NNNN
## Context
## Decision
## Consequences
```

Insight notes: one idea per file, lowercase-kebab filenames, link liberally — a
`[[link]]` to a note that doesn't exist yet marks future work.
