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

- **A fresh clone** — `engagement.is_template` is true, or `brain/workspace.toml` still holds
  `{{PLACEHOLDER}}` answers. Full run, including step 3. Set `is_template = false` as part of
  writing the config: that flag is how every later session knows setup has happened.
- **An already-configured project** — the owner wants to change an answer, add a source, or
  connect a tracker. **Skip step 3 entirely.** Ask what they want to change, change only that,
  log a decision if the change is one, and stop. Never re-clear a live brain.

Say which situation you think it is and get a yes before continuing.

## 1 · The interview

Ask in small groups — two or three questions at a time, not a wall. Take short answers; you
are filling files, not writing a spec. Where the owner shrugs, offer a default and move on.
Every answer has a named destination, so say where each one landed as you go.

**Identity.** What is the engagement called — the whole relationship, one client, one owner?
One line: who is building what, for whom, under what arrangement?
→ `brain/workspace.toml` (`engagement.name`, `engagement.owner`), `brain/project-brief.md`,
and the identity lines at the top of `AGENTS.md`.

**Projects.** *"Is this one project, or several strands under one engagement?"* Ask it plainly
and take the answer at face value; most design engagements carry two or three. For each: what
it is called, and where its work actually lives — this repo, a Figma file, a site, a deck.
Give each a short lowercase-kebab key (`portal`, `bioventures`) and say that the key is
permanent because every record cites it, while the label can change freely.
→ `brain/workspace.toml` (`projects.keys`, `projects.labels`, `projects.work_lives`), a
section each in `brain/plan.md`, `brain/now.md` and `brain/tasks.md`, and *The projects* in
`brain/project-brief.md`.

Explain the consequence in one line, because it changes what every later session does: with
more than one key, every decision, insight, exploration, workshop, feed item and task names
its strand, `feed.html` grows a filter, and `doctor.py` fails an untagged record. With one
key, none of that appears. **A second project can be added later** — write the key, then tag
what already exists; `doctor.py` lists exactly what is missing.

**People.** Who are the stakeholders — name, role, and what routes to each? Who decides? Who
has to be kept informed but doesn't decide? → `brain/project-brief.md` (People), **and the
same names into `brain/glossary.md`** under `## Hot`. Ask the follow-up that saves the most
future confusion: what do people around here call things — nicknames, acronyms, the client's
internal name for the product? Those go in the glossary too.

**Sources.** What should be watched outside this repo: Slack channels, meeting recordings
(Fathom, Granola), a mail label, a calendar, a Linear team, Notion pages, a Figma file? Ask
why each matters — a source with no stated reason produces briefings nobody reads.
→ `brain/sources.md`, then step 2 probes them.

**Tracker.** Linear, something else, or none? If yes, the issue-key prefix.
→ `brain/workspace.toml` (`tracker.name`, `tracker.prefix`). Remind them what the tracker is
here: a projection, written outward at wrap-up and never read back as authority.

**Where this came from.** No question to ask — just record it, because a clone otherwise has
no link to the boilerplate at all and every later "check for updates" becomes a conversation.
Run `python3 brain/upstream.py` once: it records the boilerplate commit this clone started
from in `template.version`, which is the floor the next `/update` measures against. Mention
`/update` in the tour and say the one thing that matters about it — it takes the template's
machinery and never touches the project's own work, so nobody has to explain that again.
→ `brain/workspace.toml` (`template.repo`, `template.version`).

**Reminders.** *"When you ask me to remind you of something, where should it actually
fire?"* Explain the reason in one line, because it is the non-obvious part: this repo cannot
remind anyone — a session only runs while they are at the machine, which is exactly when they
do not need reminding. Offer `calendar` (recommended: it reaches the phone and survives the
laptop being shut), `slack` (genuinely schedules, but 120 days out at most), `manual` (draft
it, they set it), or none. Say that email is not on the list because Gmail cannot send later.
→ `brain/workspace.toml` (`reminders.route`, `reminders.target`, `reminders.lead_time`).
Recording it here IS their say-so for writing to that channel, so it is not asked again.

**Task labels.** Offer the design default — `design` `research` `content` `handoff` `method`
`blocked-on-external` `bar` `deferred` — and adjust. Keep `bar` and `deferred`: they are what
makes "is this required before we can move on?" a grep instead of an argument.
→ `brain/workspace.toml` (`tasks.labels`).

**What "good" means here — two answers, two files.** `brain/lenses/` holds one standard per
domain, and `/reviewer` runs exactly one per pass.

- *Record* — ships filled in; it judges the brain, not the work, and is the same everywhere.
  Read it, do not rewrite it. → `brain/lenses/record.md`.
- *Craft* — the one you have to write. **Ask what the work should feel like, and hold out for
  words that reject something.** "Tactile, clicky, satisfying; I pictured cartoony and it felt
  tacky" is usable. "Clean and modern" describes nothing and rules nothing out — push back
  once, in those terms. Then ask the second question, which people skip: **what do you not
  want flagged?** Settled visual territory, work still in exploration, anything a later stage
  owns. → sections 3 and 4 of `brain/lenses/craft.md`.

Offer to seed `brain/references/` while you are here — a handful of images whose *execution*
is the bar, and any anti-references. A critic scores better against a shown bar than a
described one. Client material there is confidential like anything else from outside.

**Generation.** Does this project need real images or video, or is it type and layout? A
coding agent with no generator fakes texture with gradients, which the craft lens scores as a
tell. If yes, pick the route — the agent's own tool, another CLI billed to a subscription, or
a capped API key in `.env.agents` — and say plainly that the key is dev-only and never ships.
→ `brain/workspace.toml` (`generation.route`).

**Confidential material.** Is there client or third-party source material? It goes in
`context/` — read-only, never edited — and stays out of git.
→ `brain/workspace.toml` (`confidential.paths`) and `.gitignore`.

**The arc.** What are the stages, and what is the first one? Offer a design default —
discovery → concept → design → handoff — and let them rename it. Then the one that matters:
**what has to be true to leave stage one?** Write the answer as a decision, one per project, and point
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

- The boilerplate ships blank, so usually there is nothing to clear. Check anyway:
  `brain/braindumps/`, `brain/decisions/`, `brain/insights/`, `brain/reviews/`,
  `brain/briefings/`, `brain/explorations/`, `brain/workshops/` should hold only `README.md` files and
  `brain/decisions/0000-decision-template.md`. Empty anything else.
- `rm -rf archive/` if it is present — it holds the boilerplate's own design rationale, which
  is not this project's record.
- Rewrite `brain/now.md`, `brain/tasks.md`, `brain/open-questions.md`, `brain/feed-items.md`
  from the template shapes, with this project's content.
- Write the project's own first decision — what is being built and why this workspace shape —
  then the stage-one bar decision from the interview. Both are
  `brain/decisions/YYYY-MM-DD-slug.md`, and in a multi-project engagement both name their
  strand in frontmatter.

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

- `/brief` — the first thing to run once any real context exists. States the project back to
  you as a page: what I understood, what I still do not know, the plan, and the next steps —
  with every claim from outside this repo quietly linked to the moment in the recording or
  thread it came from. **The work does not start until you approve it.**
- `/braindump` — talk at length, unstructured. Saved verbatim, then routed into decisions,
  insights, tasks and questions. **The one to reach for first.**
- `/decide <topic>` — capture one decision deliberately, with its context and consequences.
- `/status` — one screen: where we are, what's next, what's blocked, what's open.
- `/close` — wrap up. Rewrites `now.md`, lints, regenerates the page, pushes.
- `/explore` — go wide before committing. Six to eight genuinely different directions,
  seeded so they are not the same idea four times, then sharpened against your reactions.
  Filed in `brain/explorations/` and rendered as a page — every direction's specimen side by
  side, so you judge the work rather than the writing about it. Rejected ones stay.
- `/critique` — the fast loop while building. Screenshots the work, hands it to a critic that
  sees only the picture, scores it against `brain/lenses/craft.md`, repeats until it holds up.
  Writes nothing to the brain.
- `/reviewer <lens> <scope>` — a separate session that critiques independently and writes
  findings to `brain/reviews/`. It takes a lens: `record` for whether the project's record is
  honest, `craft` for whether the work is any good to look at. The craft lens is the one you
  just wrote.
- `/briefing` — pulls the sources you just declared into a dated, attributed catch-up, then
  files what matters. Use it after time away.
- `/workshop` — for when a stakeholder will not get on a call. Turns the questions into
  screens they answer on a phone, in pieces, each one arriving with our assumption already
  selected so agreeing is the fastest way through. A half-finished run is still data, and
  anything they let stand is recorded as our guess, never as their words.
- `/setup` — re-runnable. This, again, to change an answer or add a source.

Mention two working defaults, in a line each, and then stop:

- **Focus mode.** This workspace is written for Claude Code's `/focus` — you see only the
  final message of each turn, and that message carries everything you need. Suggest turning it
  on, and say plainly that `/focus` turns it back off if they want to watch the work.
- **Parallel tabs.** Open as many sessions as they like. One that spots another working in
  this repo takes a git worktree on its own and says so in one line; it will never stop to ask
  what to do about it.

Mention two things about the record, briefly: decisions get logged **unprompted** as they are
reached, and `brain/feed.html` draws the brain as a graph of notes and shared tags, so the
interconnected view needs nothing installed. (It also writes `brain/brain.canvas` for anyone
who opens `brain/` as an Obsidian vault — optional, and nothing depends on it.)

## 6 · One last answer: does the brief get published?

`brief.publish` in `brain/workspace.toml`. `/brief` always writes `brain/brief.html` locally.
`true` also publishes it as an artifact — readable on a phone, shareable with a client — and
that sends whatever the brief quotes to an external service, which is the thing the
confidential rule governs. Ask once, in one sentence, and record the answer. Default `false`.

## 7 · Verify, then hand over

Run `python3 brain/doctor.py`, `python3 brain/feed.py` and `python3 brain/brief.py`, and
fix what they report — an
unfilled placeholder, an unknown tag, a task line that misses the grammar. Then commit, push
if a remote exists, and report in a few lines: what the project is now called, what got
written where, what is `wanted` and not connected, and the single next action.

**Do not claim a step you skipped.** If a probe failed or the owner deferred an answer, say
so and leave the file honest.

Then, if any real context already exists — a `context/` folder, a reachable recording, a
thread the owner pointed at — say that the next step is `/brief`, and offer to run it now.
Setup configures the workspace; the brief is what gets the project agreed. A clone that stops
here has a tidy brain and no shared understanding of what it is for.
