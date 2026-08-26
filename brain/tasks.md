# Tasks

*The owner of task state. Files are the truth; the tracker is a projection pushed outward at
session end — never read back as authority.*

This file exists because `now.md` cannot hold a backlog: its rule is *"if it would still be
true in two weeks, it does not belong there,"* and a backlog is exactly that. `now.md` carries
one line and a link here.

## Line format

```
- `status` · Pn · `label` … · PROJ-n — **Title**
      optional note, indented
```

- **status** — `later` `todo` `doing` `blocked` `done`. `blocked` means waiting on someone
  else; if the next move is ours, it is `todo` however unpleasant.
- **Pn** — `P1` urgent · `P2` high · `P3` medium · `P4` low.
- **labels** — the vocabulary is `tasks.labels` in `brain/workspace.toml`. **`bar`** = inside
  the current stage's exit criterion; **`deferred`** = real work that is explicitly *not* a
  prerequisite for the current stage, and must never be presented as one. Grep `` `bar` `` to
  see what is left.
- **last field** — the projection pointer: the tracker key once mirrored, `—` if not yet,
  `skip` if it deliberately never goes to the tracker. With no tracker configured, every line
  is `—` or `skip`.

Grep-friendly on purpose. `python3 brain/doctor.py` checks the shape of every line here.

---

## The workspace

### Stage 1 · Clone-ready

- `done` · P1 · `charter` `bar` · skip — **Say decision, not ADR, everywhere**
      Renamed in charter, skills, both scripts, README. Grep is clean outside dated records.
- `done` · P1 · `scripts` `bar` · skip — **One config file both scripts read**
      brain/workspace.toml + brain/config.py. Fixed the tracker-key regex bug found on the way.
- `done` · P1 · `charter` `bar` · skip — **AGENTS.md is the charter, CLAUDE.md imports it**
- `done` · P1 · `scripts` `bar` · skip — **Global tags with a doctor report**
      Frontmatter tags, brain/tags.md owns the vocabulary, unknown/unused/untagged reported.
- `done` · P2 · `interface` `bar` · skip — **Past feed items collapse by default**
      Only what is awaiting the owner opens itself; verified on a fixture with one of each.
- `done` · P1 · `skills` `bar` · skip — **/setup: the first-run quiz, re-runnable**
      Written and re-runnable; the interview itself is untested against a real project.
- `done` · P1 · `skills` `bar` · skip — **/close: the wrap-up ritual as one word**
- `done` · P2 · `skills` `bar` · skip — **Reviewer reads brain/review-lens.md**
      Split the invariant skill from the project-specific standard.
- `doing` · P1 · `charter` `bar` · skip — **Run a real clone end to end**
      Mechanics verified 2026-08-26: fresh clone has all six skills, excludes feed.html, the
      charter import resolves, doctor PASSes and feed.py renders. The /setup interview itself
      is NOT tested — that needs real answers, which is what FEED-1 asks about.

### Stage 2 · The second interface — deferred

- `later` · P2 · `interface` `deferred` · skip — **Test before/after screenshots on one change**
      Measure wall clock added and whether the pair was worth looking at. "Too slow, dropped"
      is an acceptable outcome.
- `later` · P3 · `interface` `deferred` · skip — **brain/map.html: the graph without Obsidian**
      Nodes are files, edges are wiki-links and shared tags. Only if the page proves its worth.

### Stage 3 · Sources and briefings — deferred

- `later` · P2 · `integrations` `deferred` · skip — **/briefing over the declared sources**
      Reads brain/sources.md, writes brain/briefings/YYYY-MM-DD.md, routes content out.
