# agent-workspace-boilerplate

A blank workspace for running a project with an assistant — Claude Code, Codex, or a model in
an IDE like Cursor — as a disciplined collaborator. Clone it at the start of a new project,
run `/setup`, and the assistant reads `AGENTS.md` as its charter and keeps the record honest
from day one.

Built for design projects: the work being designed often lives elsewhere (a Figma file, a
site, a deck) and this repo is the brain that runs it. Extracted from a live engagement where
every rule here was earned by a failure — the product code and client material were stripped,
and the method is the part that carries.

## How to adopt it

1. Clone, then `rm -rf .git && git init` — your project's history starts empty.
2. Open a session in the root and run **`/setup`**. It interviews you, writes the config and
   the current-state files, clears the template's own brain, checks which of your connectors
   are actually reachable, and ends with the tour of the commands.
3. From then on: start sessions by orienting, and let the assistant tell you when it's worth
   wrapping. `/close` does the wrap-up.

## Why a remote is worth setting up

`/setup` will ask, and the reason is not obvious: with a **private** repo, the same workspace
opens in Claude Code on the web and on your phone. The assistant pushes every completed unit
of work as it goes, so the brain on your phone is never more than one step behind your desk.

## What's inside

| Path | What it is |
|---|---|
| `AGENTS.md` | the charter — behaviors, invariants, session ritual. `CLAUDE.md` imports it |
| `brain/workspace.toml` | every project constant, in one file, read by both scripts |
| `brain/now.md` | the one-screen current state; rewritten, never grown (2000-char limit) |
| `brain/plan.md` | the stage arc; each stage's exit bar is a decision written on entry |
| `brain/tasks.md` | the owner of task state, in a grep-able line grammar |
| `brain/decisions/` | one numbered file per decision, logged unprompted as they're reached |
| `brain/insights/` | durable realizations, one idea per file, `[[wiki-linked]]` |
| `brain/tags.md` | the tag vocabulary — global across the whole brain |
| `brain/open-questions.md` | questions with owner tags: who can answer |
| `brain/braindumps/` | verbatim dumps; processing routes content out, never rewrites |
| `brain/briefings/` | dated pulls from the sources in `brain/sources.md` |
| `brain/sources.md` | what the assistant watches outside this repo, and what it can reach |
| `brain/review-lens.md` | what "good" means on this project — the reviewer reads it |
| `brain/reviews/` | the independent reviewer's findings and the builder's answers |
| `brain/feed-items.md` | decisions awaiting the owner, rendered into `feed.html` |
| `brain/doctor.py` | lints the brain: hard FAILs for rules with no exceptions, reports for the rest |
| `brain/feed.py` | renders `brain/feed.html` — a self-glossing readout of where things stand |
| `.claude/skills/` | `/setup` · `/braindump` · `/decide` · `/status` · `/close` · `/reviewer` |

## The ideas underneath

- **One owner per class of information.** Everything else links, never restates.
- **Files are the truth; outward tools are projections.** The tracker and `feed.html` are
  written outward and never read back as authority.
- **Enforce with a program, not a README.** The rules that survive are the ones
  `doctor.py` refuses to let you past.
- **Stages end by a bar written on entry.** Otherwise every next step is genuinely useful and
  nothing ever ends.
- **Tags are global to the brain.** A decision and an insight share one vocabulary — and
  because tags and `[[links]]` are what Obsidian reads, opening `brain/` as a vault gives you
  the interconnected graph with nothing installed and nothing committed.
- **Portability is the assistant's job, not yours.** It pushes as it goes and tells you when a
  wrap-up is due, so closing the laptop is never a gamble.
- **Never delete; tombstone.** A superseded file gets a "do not cite" header naming its
  replacement and moves to `archive/`.

## Requirements

Python 3 for the two scripts — standard library only, no dependencies. Works on a stock macOS
`python3`.
