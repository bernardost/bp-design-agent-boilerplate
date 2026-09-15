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
| `brain/glossary.md` | people, nicknames, acronyms, codenames — the project's proper nouns |
| `brain/open-questions.md` | questions with owner tags: who can answer |
| `brain/braindumps/` | verbatim dumps; processing routes content out, never rewrites |
| `brain/briefings/` | dated pulls from the sources in `brain/sources.md` |
| `brain/sources.md` | what the assistant watches outside this repo, and what it can reach |
| `brain/lenses/` | what "good" means, one file per domain — `/reviewer` runs one per pass |
| `brain/explorations/` | directions considered but not chosen; rejected ones stay |
| `brain/workshops/` | questions put to a stakeholder asynchronously, and the answers back |
| `brain/references/` | the quality bar as images — measured against, never copied |
| `brain/reviews/` | the independent reviewer's findings and the builder's answers |
| `brain/drafts/` | messages written for you to send — before they go out, and after |
| `brain/feed-items.md` | decisions awaiting the owner, rendered into `feed.html` |
| `brain/doctor.py` | lints the brain: hard FAILs for rules with no exceptions, reports for the rest |
| `brain/brief.py` | renders `brain/brief.html` — the brief the owner approves, with every outside claim linked to its source |
| `brain/spread.py` | renders an exploration as a page — every direction's specimen, pitch and verdict side by side |
| `brain/feed.py` | renders `brain/feed.html` — a self-glossing readout, including the brain drawn as a graph |
| `brain/render.py` | the four above in one command — what `/close` runs, exiting non-zero on a doctor FAIL |
| `.claude/skills/` | `/setup` · `/brief` · `/braindump` · `/decide` · `/status` · `/close` · `/briefing` · `/workshop` · `/explore` · `/critique` · `/reviewer` |

## The ideas underneath

- **One owner per class of information.** Everything else links, never restates.
- **Files are the truth; outward tools are projections.** The tracker and `feed.html` are
  written outward and never read back as authority.
- **Enforce with a program, not a README.** The rules that survive are the ones
  `doctor.py` refuses to let you past.
- **Stages end by a bar written on entry.** Otherwise every next step is genuinely useful and
  nothing ever ends.
- **Tags are global to the brain.** A decision and an insight share one vocabulary, and
  `feed.html` draws the result — notes, shared tags, and the links between them — as an inline
  SVG graph. Stdlib only, self-contained, nothing uploaded. Because tags and `[[links]]` are
  also what Obsidian reads, opening `brain/` as a vault works too, and a `brain.canvas` is
  written for it; nothing depends on either.
- **Nothing starts until the brief is agreed.** Once the first context lands, `/brief` states
  the project back as a page — what was understood, what is still unknown and who can answer
  it, the stage arc, the next steps — and waits for a yes. The failure it prevents is the
  expensive one: work advancing for weeks on the assistant's private reading of the project.
- **Evidence is present and quiet.** A claim that came from outside the repo carries
  `^[who · where · when](link)`, which renders as a faint superscript numeral — hover for the
  attribution, click for the timestamped moment in the recording. Anything the assistant
  worked out rather than heard is marked `^[inferred]` in ochre. The requirement is absolute
  and it costs the reader nothing, which is the only way a requirement like that survives.
- **Nothing for you is left outside the repo.** A drafted email goes to `brain/drafts/` and
  shows up on the feed with a button that copies it, ready to paste and send. Not a scratch
  directory whose path you would have to be told — that is how a written message becomes an
  unsent one.
- **When the stakeholder will not show up, move the workshop to his phone.** `/workshop`
  takes the questions a missed call would have answered and turns them into screens that
  arrive with our assumption already selected, so the fastest path through is agreeing. A
  half-finished run is still data, and an answer he let stand is recorded as ours, never
  quoted as his.
- **Parallel sessions get worktrees, silently.** Open as many tabs as you like. A session that
  notices another one working here takes a worktree and says so in one line, instead of
  stopping to ask you what you would like it to do about the situation you set up on purpose.
- **Focus mode is assumed.** The charter is written for Claude Code's `/focus`, where you see
  only the final message of each turn — so that message carries everything, and nothing
  important lives in a tool call you never opened. `/focus` toggles it off.
- **Portability is the assistant's job, not yours.** It pushes as it goes and tells you when a
  wrap-up is due, so closing the laptop is never a gamble.
- **Never delete; tombstone.** A superseded file gets a "do not cite" header naming its
  replacement and moves to `archive/`.
- **Diverge before you converge, and keep the losers.** `/explore` puts six to eight
  genuinely different directions on the table, seeded so they are not one idea four times.
  They live in `brain/explorations/`, and picking one produces exactly one decision that
  links back — the only seam between the two halves.
- **Show the spread, don't describe it.** Eight directions in prose get judged on which was
  described best. `brain/spread.py` renders them side by side — each with a specimen of its
  palette, type and layout logic — so taste acts on the work instead of on the writing
  about it.
- **Two critics, one standard.** `/critique` is the fast loop while building: a fresh-context
  critic that sees only the render, scores it, and writes nothing. `/reviewer craft` is the
  slow independent pass that writes findings. Both read `brain/lenses/craft.md`, so there is
  one bar and not two.

## Requirements

Python 3 for the scripts — standard library only, no dependencies. Works on a stock macOS
`python3`.
