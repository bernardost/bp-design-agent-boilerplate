---
name: setup
description: First-run setup for a fresh clone of this workspace — interview the owner, write brain/workspace.toml and the current-state files, clear the template's inherited brain, survey which connectors are reachable, and end with the tour of the commands. Re-runnable later to change an answer or add a source. Use for /setup, or when a session opens on an unconfigured clone.
---

# Setup

You are configuring a fresh clone of this workspace for a real project. When you are done the
owner should have a workspace that knows what the project is, who is in it, what it watches,
what "good" means, and where it is going — and should know which commands exist.

## Before anything: which situation is this?

Run `python3 brain/config.py` and read `brain/decisions/` .

- **A fresh clone** — the config still says `Agent Workspace Boilerplate`, or the decisions
  in `brain/decisions/` are the template's own (0001–0011 are about building the template).
  Full run, including the clear-out in step 3.
- **An already-configured project** — the owner wants to change an answer, add a source, or
  connect a tracker. **Skip step 3 entirely.** Ask what they want to change, change only that,
  log a decision if the change is one, and stop. Never re-clear a live brain.

Say which situation you think it is and get a yes before continuing.

## 1 · The interview

Ask in small groups — two or three questions at a time, not a wall. Take short answers; you
are filling files, not writing a spec. Where the owner shrugs, offer a default and move on.
Every answer has a named destination, so say where each one landed as you go.

**Identity.** What is the project called? One line: who is building what, for whom, under what
arrangement? Where does the work actually live — this repo, a Figma file, a site, a deck?
→ `brain/workspace.toml` (`project.name`, `project.owner`, `project.work_lives`),
`brain/project-brief.md`, and the identity lines at the top of `AGENTS.md`.

**People.** Who are the stakeholders — name, role, and what routes to each? Who decides? Who
has to be kept informed but doesn't decide? → `brain/project-brief.md` (People).

**Sources.** What should be watched outside this repo: Slack channels, meeting recordings
(Fathom, Granola), a mail label, a calendar, a Linear team, Notion pages, a Figma file? Ask
why each matters — a source with no stated reason produces briefings nobody reads.
→ `brain/sources.md`, then step 2 probes them.

**Tracker.** Linear, something else, or none? If yes, the issue-key prefix.
→ `brain/workspace.toml` (`tracker.name`, `tracker.prefix`). Remind them what the tracker is
here: a projection, written outward at wrap-up and never read back as authority.

**Task labels.** Offer the design default — `design` `research` `content` `handoff` `method`
`blocked-on-external` `bar` `deferred` — and adjust. Keep `bar` and `deferred`: they are what
makes "is this required before we can move on?" a grep instead of an argument.
→ `brain/workspace.toml` (`tasks.labels`).

**What "good" means here.** What would make this project's output bad? For design work this is
usually accessibility, brand and token consistency, file hygiene in the design tool, handoff
completeness, and whether the artifact matches the brief. → `brain/review-lens.md`, which
`/reviewer` reads on every pass.

**Confidential material.** Is there client or third-party source material? It goes in
`context/` — read-only, never edited — and stays out of git.
→ `brain/workspace.toml` (`confidential.paths`) and `.gitignore`.

**The arc.** What are the stages, and what is the first one? Offer a design default —
discovery → concept → design → handoff — and let them rename it. Then the one that matters:
**what has to be true to leave stage one?** Write the answer as a numbered decision, and point
`brain/plan.md` at it. → `brain/plan.md` plus a new bar decision in `brain/decisions/`.

**Tags.** Seed five or six themes from what they just told you, defined one line each.
→ `brain/tags.md`.

## 2 · Survey what is actually reachable

For each source the owner named, try one cheap real call — list the Slack channel, list recent
meetings, fetch the Linear team. Connections are per-person and per-machine, so this is the
only way to know.

Mark each line in `brain/sources.md` `connected` or `wanted`. **Never mark something connected
because it ought to be.** `wanted` is not a failure; it is the fix-it list for when a
connector shows up, and it is honest.

## 3 · Clear the inherited brain — fresh clones only

Confirm out loud first, listing what will go. Then:

- Empty `brain/braindumps/`, `brain/decisions/`, `brain/insights/`, `brain/reviews/`,
  `brain/briefings/` — **keeping** every `README.md` and `brain/decisions/0000-decision-template.md`.
- Rewrite `brain/now.md`, `brain/tasks.md`, `brain/open-questions.md`, `brain/feed-items.md`
  from the template shapes, with this project's content.
- Write the project's own decision 0001: what is being built and why this workspace shape.
  Then the stage-one bar decision from the interview as 0002.

The template's decisions are the design rationale for the template. They are not this
project's decisions, and keeping them would mean the owner's first act is deleting files.

## 4 · The repo, and why it matters

Ask whether there is a remote yet, and **explain the reason rather than just asking**: with a
remote, this same workspace opens in Claude Code on the web and on their phone. The brain
travels only if it is pushed — that is the whole value, and it is not obvious from the outside.

- Recommend a **private** repo. Public is a choice the owner makes explicitly, out loud, and
  it is the wrong one if `context/` or briefings hold anyone else's material.
- If they want one and `gh` is available, offer to create it.
- Record the answer in `brain/workspace.toml` under `[git]`. **Recording it is the
  authorization** — from then on you commit and push each completed unit of work without
  asking, and you never ask about the remote again.
- If they decline a remote, set `remote = false` and do not raise it again.

Then explain the other half of portability: closing the session is safe because `now.md`,
`tasks.md` and the decision log are what the next session reads first — and that **you** will
say when it is worth wrapping, so they never have to guess.

## 5 · The tour

End with the commands, one line each, in the order they'll first want them. Do not paste the
whole charter at them.

- `/braindump` — talk at length, unstructured. Saved verbatim, then routed into decisions,
  insights, tasks and questions. **The one to reach for first.**
- `/decide <topic>` — capture one decision deliberately, with its context and consequences.
- `/status` — one screen: where we are, what's next, what's blocked, what's open.
- `/close` — wrap up. Rewrites `now.md`, lints, regenerates the page, pushes.
- `/reviewer` — a separate session that critiques the work independently and writes findings
  to `brain/reviews/`. It reads `brain/review-lens.md`, which you just wrote.
- `/setup` — re-runnable. This, again, to change an answer or add a source.

Mention two things about the record, briefly: decisions get logged **unprompted** as they are
reached, and tags are global to the brain, so opening `brain/` in Obsidian gives the
interconnected graph free — optional, and nothing here depends on it.

## 6 · Verify, then hand over

Run `python3 brain/doctor.py` and `python3 brain/feed.py`, and fix what they report — an
unfilled placeholder, an unknown tag, a task line that misses the grammar. Then commit, push
if a remote exists, and report in a few lines: what the project is now called, what got
written where, what is `wanted` and not connected, and the single next action.

**Do not claim a step you skipped.** If a probe failed or the owner deferred an answer, say
so and leave the file honest.
