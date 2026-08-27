# Ecosystem survey — what was adopted, and what was rejected

*2026-08-27. Read the sources of 20 published agent skills covering knowledge management,
note-taking, memory, and Obsidian, to see what should change about this workspace. Kept here
rather than in `brain/` because it is about the boilerplate, not about any project run with
it. `/setup` deletes `archive/` on a clone.*

## Nothing was installed

The one plausible install was **`kepano/obsidian-skills@defuddle`** (65K installs, MIT) — a
40-line wrapper that runs `defuddle parse <url> --md` instead of a raw fetch, stripping nav and
ads. No opinion about our files. Not installed yet for a sequencing reason: it only pays off
once `/briefing` has live connectors, and it adds a global npm binary to a workspace whose
whole claim is that it needs nothing but a text editor and `python3`. Revisit when `/briefing`
runs for real.

## Adopted, as our own files

1. **`/briefing`'s design came from `anthropics/knowledge-work-plugins@enterprise-search:digest`**
   — group by topic rather than by source, action items first, dedupe one event reported in two
   places, name which sources were actually searched, and never let one dead connector kill the
   digest. Its per-item `— from [person], [source] ([date])` format is our label-evidence rule
   as a template. Priority-by-question-type ("decisions → chat first, commitments → mail
   first") came from the same family's `source-management`.
2. **`brain/glossary.md`** — from `productivity@memory-management`, which turns out to be an
   entity decoder, not a memory system: nicknames → people, acronyms → expansions, codenames →
   projects. A class of information the brain genuinely did not own. Its hot/full promote-demote
   split is the same instinct as `now.md`'s size limit.
3. **Three `doctor.py` reports** — `orphans` (notes nothing cites, the inverse of the existing
   dangling-link check, from `second-brain-lint`), `now.md` freshness (adapted from PARA's
   mtime staleness, but measured as "did the brain move after `now.md` was written", which is
   the question that actually matters), and `archive` candidates (files carrying a "do not
   cite" tombstone that never moved — the mirror of the existing FAIL).
4. **The graph in `feed.html`** — kepano's `json-canvas` taught the spec, and the survey
   established why a `.canvas` cannot be the primary artifact (see below). The inline SVG is
   ours; the `.canvas` ships alongside for vault users.

## Rejected, with the reason

- **`obsidian-cli`, `obsidian-bases`** — the CLI requires Obsidian to be *running*; `.base`
  files are inert without 1.9.10+. Both break the Obsidian-optional rule. Also: Obsidian's free
  tier is personal use only, so client work would need a paid commercial licence — a licensing
  question this repo currently does not have.
- **A `.canvas` as the visualization** — its `file` nodes only resolve inside Obsidian; every
  other viewer is a cloud app (uploading a client's material) or an npm dependency. Written as
  a side effect, never depended on.
- **`obsidian-markdown`** — we already use the 10% that matters (frontmatter, wiki-links). The
  rest — callouts, block ids, embeds — would render as literal junk in `feed.py`'s deliberately
  partial markdown renderer.
- **The `second-brain` family** — `wiki/index.md` restates every page's summary, a second owner
  of what `decisions/` and `insights/` already own. It splits by noun type (source / entity /
  concept) where we split by epistemic status (decided / realized / open / raw), and for a
  design engagement "is this settled?" is the load-bearing distinction. Its own norm is 10–15
  wiki pages per ingested source. Dormant since April 2026.
- **`task-management`** — no grep-able grammar, no tracker-projection pointer, no owner tags,
  and being `user-invocable: false` it would fire ambiently and write a competing `TASKS.md`
  plus an unrequested `dashboard.html` into the repo root. A second writer on a file our
  single-owner model already assigns.
- **`roadmap-management`** — RICE / MoSCoW scoring. Fights stage discipline: `plan.md` owns the
  arc through exit bars, not scores.
- **`decision-logger`** — writes to `~/.claude/decisions/`, outside the repo, breaking both
  files-are-truth and per-project clone isolation. Two ideas from it are still worth taking and
  have NOT been built: a `DO_NOT_RESURFACE` marker on options a decision explicitly rejected
  (checkable by `doctor.py`), and a retroactive `Superseded by:` back-pointer.
- **`meeting-notes`, `note-taking`** — templates, not capabilities, with no notion of
  who-said-what-when.

## Two traps worth remembering

**Install counts on skills.sh are not quality signals.** `mattpocock@obsidian-vault` shows 201K
installs and was *deleted by its author* on 2026-08-05 — his changelog calls it one of "two that
were only ever mine… hardcoded a path to my own Obsidian vault." The count is lifetime
cumulative and mostly measures how popular the containing repo is. Separately, four of the
`-management` skills had been renamed upstream, so those counts point at frozen snapshots.

**Name collisions can mis-route a session.** `close-management` is *accounting month-end close*
— AP/AR accruals, FX revaluation, period lock. Nothing to do with our `/close`.
`knowledge-management` is *customer-support KB articles*. Read the source, never the name.
