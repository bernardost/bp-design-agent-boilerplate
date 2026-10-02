# bp-design-agent-boilerplate

A blank workspace for running a project with an assistant — Claude Code, Codex, or a model in
an IDE like Cursor — as a disciplined collaborator. Clone it at the start of a new project,
run `/setup`, and the assistant reads `AGENTS.md` as its charter and keeps the record honest
from day one.

Built for design projects: the work being designed often lives elsewhere (a Figma file, a
site, a deck) and this repo is the brain that runs it. Extracted from a live engagement where
every rule here was earned by a failure — the product code and client material were stripped,
and the method is the part that carries.

## Why this and not a general assistant

Claude Cowork, a chat window with project memory, an IDE assistant — they all work, and for
plenty of tasks they are less setup than this. Five things they do not give you.

**One agent per project, and its context is the project.** A general assistant accumulates
everything you have ever discussed with it, and retrieval decides what resurfaces. Here the
boundary is a directory: one clone, one engagement, one brain. Nothing bleeds between clients,
which is not a nicety when two of them have you under NDA. It also means the assistant can be
told to read everything rather than guess at what matters — the whole context fits, because
you decided what goes in it.

**You own the files, so fixing what it knows is editing a file.** The knowledge is markdown in
a directory you can grep, diff, edit and delete. When the assistant has the wrong idea about
your project you correct `now.md` or archive a decision — you do not argue with a memory you
cannot see and cannot address. Every change is a commit, so you can see what it learned and
when. `doctor.py` then holds the whole thing to rules a README could only suggest.

**Any model, and more than one.** `AGENTS.md` is the charter: Claude Code reads it through
`CLAUDE.md`, Codex and Cursor read it directly. The scripts are standard-library Python with
no dependencies and no API of their own. Switch models between sessions, run two at once in
separate tabs, or hand the repo to someone using a different tool entirely — the record is
plain text either way, and nothing about it expires when a product does.

**The commands are design work, not coding work.** `/moodboard` turns research into ideas and
assembles them into visions. `/explore` puts six to eight genuinely different directions on
the table with real specimens. `/critique` scores a render against a craft lens you wrote.
Brand assets are extracted from the client's PDF, never redrawn. A general assistant has no
opinion about any of that, because it was not built with a designer in the room.

**It follows you to your phone.** Because the brain is a repo you own, a private remote makes
it portable: the same workspace opens in Claude Code on the web and on your phone, and Codex
reads the same files. The assistant pushes every completed unit of work as it goes without
being asked, so what you read on the train is never more than one step behind your desk.
`/setup` asks about this, and this is the reason it does.

**What it costs:** a few minutes of `/setup`, and a repo you keep. If the work is one
conversation long, open a chat window instead.

## How to adopt it

1. Clone, then `rm -rf .git && git init` — your project's history starts empty.
2. Open a session in the root and run **`/setup`**. It interviews you, writes the config and
   the current-state files, clears the template's own brain, checks which of your connectors
   are actually reachable, and ends with the tour of the commands.
3. From then on: start sessions by orienting, and let the assistant tell you when it's worth
   wrapping. `/close` does the wrap-up.

## Taking later improvements without losing your work

Step 1 above cuts the git link on purpose, so your project's history starts empty. That leaves
nothing for an assistant to read when you ask it to check the boilerplate for updates — which
is why it used to need telling, every time, which files were its own scaffolding.

Now it doesn't. Run **`/update`**. `brain/upstream.py` holds the ownership rules in code:
`brain/*.py`, the skills and the workflow are the template's and get taken; your decisions,
insights, tasks, `now.md`, `plan.md`, the craft lens and `workspace.toml` are yours and are
never even compared. Files that carry both — `AGENTS.md`, `craft.md`, `tags.md` — get listed
for you to port by hand, never copied over. Anything it does not recognise is treated as
yours, because a wrong guess in that direction costs a question and a wrong guess in the other
costs your work.

## What's inside

| Path | What it is |
|---|---|
| `AGENTS.md` | the charter — behaviors, invariants, session ritual. `CLAUDE.md` imports it |
| `brain/workspace.toml` | every constant, in one file: the engagement, its projects, the tracker |
| `brain/now.md` | the one-screen current state, a section per project; rewritten, never grown |
| `brain/plan.md` | the stage arc per project; each stage's exit bar is a decision written on entry |
| `brain/tasks.md` | the owner of task state, in a grep-able line grammar |
| `brain/decisions/` | one dated file per decision, logged unprompted as they're reached |
| `brain/insights/` | durable realizations, one idea per file, `[[wiki-linked]]` |
| `brain/tags.md` | the tag vocabulary — global across the whole brain |
| `brain/glossary.md` | people, nicknames, acronyms, codenames — the project's proper nouns |
| `brain/open-questions.md` | questions with owner tags: who can answer |
| `brain/braindumps/` | verbatim dumps; processing routes content out, never rewrites |
| `brain/briefings/` | dated pulls from the sources in `brain/sources.md` |
| `brain/sources.md` | what the assistant watches outside this repo, and what it can reach |
| `brain/lenses/` | what "good" means, one file per domain — `record`, `craft`, `deck`, `house`; `/reviewer` runs one per pass |
| `brain/decks/` | decks and client documents — deliverables, judged against `brain/lenses/deck.md` |
| `brain/moodboards/` | ideas the research adds up to, and the visions they assemble into |
| `brain/explorations/` | directions considered but not chosen; rejected ones stay |
| `brain/workshops/` | questions put to a stakeholder asynchronously, and the answers back |
| `brain/references/` | the quality bar as images — measured against, never copied |
| `brain/reviews/` | the independent reviewer's findings and the builder's answers |
| `brain/drafts/` | messages written for you to send — before they go out, and after |
| `brain/feed-items.md` | decisions awaiting the owner, rendered into `feed.html` |
| `brain/doctor.py` | lints the brain: hard FAILs for rules with no exceptions, reports for the rest |
| `brain/redate.py` | one-way migration of an older `NNNN-` decision log to dated filenames |
| `brain/test_brain.py` | what `doctor.py` cannot check about itself: links resolve, migrations keep every citation, pages ship no unsafe or absolute URLs, two projects stay separate |
| `brain/brief.py` | renders `brain/brief.html` — the brief the owner approves, with every outside claim linked to its source |
| `brain/board.py` | renders a moodboard as a desk you can pan and zoom — ideas, visions, and the wires between them |
| `brain/spread.py` | renders an exploration as a page — every direction's specimen, pitch and verdict side by side |
| `brain/feed.py` | renders `brain/feed.html` — a self-glossing readout, including the brain drawn as a graph |
| `brain/render.py` | the renderers above in one command — what `/close` runs, exiting non-zero on a doctor FAIL |
| `brain/when.py` | resolves "next friday 9am" to an exact instant, so no reminder is scheduled off arithmetic a model did in its head |
| `brain/brand/` | the client's real assets, each declaring where it came from — never a redrawn mark |
| `brain/extract.py` | pulls logos, colours and the written rules out of a brand PDF, so extracting is easier than redrawing |
| `brain/upstream.py` | which paths the template owns and which the project does, in code — what makes `/update` safe |
| `.claude/skills/` | `/setup` · `/brief` · `/braindump` · `/decide` · `/remind` · `/update` · `/status` · `/close` · `/briefing` · `/transcript` · `/workshop` · `/moodboard` · `/explore` · `/prototype` · `/critique` · `/deck` · `/reviewer` |

## The ideas underneath

- **A brand asset is obtained, never reconstructed.** Given a client's guidelines, the
  assistant extracts the mark from the PDF as real vector, or asks for the asset pack, or falls
  back to the name set in plain text — never a redraw, and never the right structure with
  invented letterforms, which is the version that survives review and ships. Every file in
  `brain/brand/` declares whether it was extracted, supplied, or designed here, and `doctor.py`
  fails one that does not.
- **One engagement, several projects, one brain.** A client relationship usually carries two
  or three strands of work, and a single meeting covers all of them. Every record names its
  strand; `feed.html`, `/status` and the tracker push filter on it. Nothing is stored per
  project — compartmentalizing in the storage would fork the one log that makes a decision
  findable, to buy a filter that render time gives away. With one project none of it appears.
- **One owner per class of information.** Everything else links, never restates.
- **Files are the truth; outward tools are projections.** The tracker and `feed.html` are
  written outward and never read back as authority.
- **Enforce with a program, not a README.** The rules that survive are the ones
  `doctor.py` refuses to let you past — and the tools themselves are held to the same
  standard by `brain/test_brain.py`, which GitHub Actions runs on every push.
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
- **A transcript is a guess, and it is wrong where it matters.** Speech recognition fails
  hardest on the words a project runs on — names, acronyms, numbers, who was speaking — and
  whoever was in the room reads straight past the errors. `/transcript` saves the file
  verbatim, then asks once, as a numbered table: timestamp, the line as transcribed, what is
  needed, and the assistant's own reading, so answering is confirming rather than filling in
  blanks. The commonest hole is a shared screen nobody named — *"this one"*, *"as you can see
  here"* — which is where the actual content of a review goes missing. The transcript is never
  edited; corrections sit beneath it, the machine's version and the human's both visible.
- **Evidence is present and quiet.** A claim that came from outside the repo carries
  `^[who · where · when](link)`, which renders as a faint superscript numeral — hover for the
  attribution, click for the timestamped moment in the recording. Anything the assistant
  worked out rather than heard is marked `^[inferred]` in ochre. The requirement is absolute
  and it costs the reader nothing, which is the only way a requirement like that survives.
- **A reminder leaves the repo, or it is not a reminder.** "Remind me Friday" is not a
  note-taking request: the session will not be running on Friday, and a file in `brain/` fires
  at nobody. `/remind` resolves the date with a program rather than in the model's head, says
  the weekday back so a misread dies early, and puts the alarm in your calendar or as a
  scheduled message. With no channel configured it says so in one line and hands you the date,
  instead of promising something it cannot do.
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
- **A decision is dated, not numbered.** `brain/decisions/2026-09-15-the-slug.md`: the date
  orders the log, the slug is what `[[links]]` point at. A number would have to be claimed
  from a pool every open tab shares, and the collision only shows up at merge — which it did,
  here, and cost a three-file renumber. `brain/redate.py` migrates an older log.
- **Focus mode is assumed.** The charter is written for Claude Code's `/focus`, where you see
  only the final message of each turn — so that message carries everything, and nothing
  important lives in a tool call you never opened. `/focus` toggles it off.
- **The prose rules live in the charter, not in a skill.** The parts of `stop-slop` the
  charter did not already ban — name the actor, active voice, no throat-clearing, no "not X,
  it's Y", no vague declaratives — are written into `AGENTS.md`, so Codex and Cursor get them
  too. Em dashes are kept on purpose; that rule is about not being detected, not about being
  understood.
- **Portability is the assistant's job, not yours.** It pushes as it goes and tells you when a
  wrap-up is due, so closing the laptop is never a gamble.
- **Never delete; tombstone.** A superseded file gets a "do not cite" header naming its
  replacement and moves to `archive/`.
- **A moodboard argues; a style guide specifies.** Asked for a moodboard, a model reliably
  produces a brand manual — swatches, a type scale, sections named Colour and Typography —
  which settles a design nobody chose from research nobody read. `/moodboard` builds the other
  thing: **ideas**, one title and one sentence each and arguable, and **visions** that assemble
  named sets of them into whole brands. The same idea appears in several visions, and that
  overlap is the argument — `brain/board.py` draws it as wires you can light from either end,
  and an idea present in every vision is the brand whichever way the work lands.
- **Diverge before you converge, and keep the losers.** `/explore` puts six to eight
  genuinely different directions on the table, seeded so they are not one idea four times.
  They live in `brain/explorations/`, and picking one produces exactly one decision that
  links back — the only seam between the two halves.
- **The first pass of a new design ships with its dials exposed.** An owner cannot specify
  taste for something he has not seen move, so what comes back is *"the type feels heavy"* and
  a round goes into converting adjectives into values. `/prototype` builds a tuning drawer in
  the same pass as the page: every visual value is a CSS custom property, nothing is
  hard-coded, and **the variable list is the honest spec of every decision the design is
  making** — a value you hard-coded is a decision you hid. Motion is a select of three or four
  genuinely different kinds rather than a slider, because a slider cannot tell you the right
  answer was a different idea. Copy settings puts the owner's pick on the clipboard as JSON,
  which gets baked into the defaults and logged as a decision. `doctor.py` reports a drawer
  left in anything under `brain/decks/`.
- **Show the spread, don't describe it.** Eight directions in prose get judged on which was
  described best. `brain/spread.py` renders them side by side — each with a specimen of its
  palette, type and layout logic — so taste acts on the work instead of on the writing
  about it.
- **A title is a sentence, not a label and never an aphorism.** Asked for a deck, a model
  writes fragments that scan and say nothing — *"Say what it is. Date it. Stop."* — then
  explains each slide in a paragraph the presenter will say out loud anyway. `/deck` asks two
  questions first (presented or standalone; labels or labels plus conversational titles),
  writes **every title before a single page is built**, and holds them to one test: read the
  titles alone, in order, and you should have the whole argument. *Brand traits · "Six key
  concepts describe the brand's personality."* Then it marks which pages are a relationship
  rather than a list and draws those, and it screenshots every page before calling anything
  done. `brain/lenses/deck.md` is the standard, and it caps the score at 5 for fragment titles
  or for a deck nobody looked at.
- **Three lenses, one bar each.** `/critique` is the fast loop while building: a fresh-context
  critic that sees only the render, scores it, and writes nothing. `/reviewer craft` is the
  slow independent pass that writes findings. Both read `brain/lenses/craft.md`, so there is
  one bar and not two.

## Requirements

Python 3 for the scripts — standard library only, no dependencies. Works on a stock macOS
`python3`.
