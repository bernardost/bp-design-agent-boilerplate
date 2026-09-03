---
name: brief
description: Turn the first context into a brief the owner can read and approve — what I understood, what I still do not know, the plan, and the immediate next steps — rendered as a page with every claim quietly linked to its source. Use for /brief, after /setup or a /briefing that brought in outside material, or whenever the work is about to move on an understanding nobody has agreed to.
---

# Brief

The failure this prevents: context arrives, the session starts moving, and the work advances
on **your** reading of the project. Nobody ever agreed to that reading. It surfaces weeks
later as a deliverable aimed at the wrong thing, and by then the wrong thing has been paid for.

So before the work moves, the owner gets one page: *this is what I understood, this is what I
still do not know, this is the shape of the work, this is what I would do next.* Then it waits
for a yes.

**This is a gate, not a document.** Run it when the first real context lands. Do not run it
weekly — the brief holds stable facts, and `now.md` holds everything volatile.

## 1 · Read the context, all of it

Everything that has arrived: `context/` if the project has one, the sources in
`brain/sources.md`, the transcripts and threads a `/briefing` pulled, whatever the owner said
in the session. Read it before writing a line of the brief. A brief assembled from a summary
of the context inherits the summary's mistakes and hides them behind your confidence.

## 2 · Write `brain/project-brief.md` — and cite it

Fill the sections that file already has. Two rules, and the second one is the reason this
skill exists:

**Cite every claim that came from outside this repo.** The form is a source tag, inline:

```
The client wants SSO before launch. ^[Dana · kickoff call · 2026-08-11 14:20](https://meetings.example.com/r/4821?t=860)
The roster is a version behind. ^[Ravi · #client-portal · 2026-08-28](https://slack.com/…)
Two more workstreams are probably coming. ^[inferred]
```

- `who · where · when`, and a link straight to the moment where one exists — a timestamped
  recording URL, a permalink to the message, the mail thread. Not a link to the tool.
- **`^[inferred]` is mandatory for anything you worked out rather than heard.** It renders as
  its own word in ochre. A guess that reads like a quote is the exact failure the charter's
  "label evidence, never launder it" rule exists to stop, and this is how the page enforces it.
- Name every person, nickname and acronym you had to decode in `brain/glossary.md`. A decoded
  name that lives only in the brief is a guess that will harden into a fact.

The markers render as faint superscript numerals, so the owner reads the argument and the
provenance stays one hover away. That is the point: do not write provenance into the prose.

Add the status line under the title if it is not there:

```
Status: draft
```

## 3 · Make sure the rest of the page has something to show

The brief page reads four files. Three of them are not yours to fill from the brief, so fill
them properly:

- **`brain/open-questions.md`** — every unknown, numbered, **each with an owner tag: who can
  answer it.** A question with no owner renders in red, because nobody can answer it. Do not
  soften this list. An early brief with two unknowns has not been checked.
- **`brain/plan.md`** — the stage arc. Stage 1 is current; later stages get a name and an
  entry event, never a bar.
- **The current stage's exit bar** — a numbered decision, written now if it does not exist.
  Without it the page prints "this stage has no exit bar", which is accurate and is the thing
  to fix, not to hide.
- **`brain/tasks.md`** — the immediate next steps as real task lines, with `bar` on the ones
  inside the exit criterion.

## 4 · Render it

```
python3 brain/brief.py --open
```

Then check what it printed: unwritten sections, question count, step count. An unwritten
section renders as a gap on the page — fix it or say why it stays empty.

If `brief.publish` in `brain/workspace.toml` is `true`, also publish the page as an artifact
and hand over the link. If it is `false`, **do not publish** — the brief quotes client
material, and `AGENTS.md` says that does not reach an external service without the owner's
say-so. Offer, once, and record the answer in `workspace.toml` rather than asking again.

## 5 · Hand it over, and stop

Say what you are handing over in two or three lines, then the box. Nothing else — the page
is the deliverable, and re-narrating it in the terminal defeats the purpose.

```
┌─ YOUR TURN ──────────────────────────────┐
│ 1. Read brain/brief.html.                │
│ 2. Tell me what's wrong, or approve it.  │
│ 3. Q7 needs Joe: "<the question>"        │
└──────────────────────────────────────────┘
```

Then **stop**. Do not start stage-1 work off an unapproved brief. If the owner is away and
something is genuinely unblocked and reversible, do that and say you did — but a brief waiting
on a yes is a brief waiting.

## 6 · On approval

1. A numbered decision in `brain/decisions/`: what was approved, what the owner changed on the
   way through, and what it commits the project to. This is the record of the yes.
2. Change the brief's status line to name it:
   `Status: approved 2026-09-04 · [[0004-the-brief-is-approved]]`
3. Re-render, `python3 brain/doctor.py`, commit and push.

Corrections the owner makes are the valuable part of this whole exercise. Each one goes into
the file it belongs to — and if a correction contradicts something already logged, say so
before you write it.
