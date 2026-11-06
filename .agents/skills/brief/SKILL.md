---
name: brief
description: Turn the first context into a brief the owner can read and approve — the design-brief questions (business, audience, brand, visual language, product scope, UX, constraints, decisions) answered from the context or flagged as missing, the plan, and the next steps — rendered as a page that shows at a glance what is answered, inferred and missing, and proposes a kickoff workshop for the key gaps. Use for /brief, after /setup or a /briefing that brought in outside material, or whenever the work is about to move on an understanding nobody has agreed to.
---

# Brief

The failure this prevents: context arrives, the session starts moving, and the work advances
on **your** reading of the project. Nobody ever agreed to that reading. It surfaces weeks
later as a deliverable aimed at the wrong thing, and by then the wrong thing has been paid for.

So before the work moves, the owner gets one page: *this is what I understood, this is what I
still do not know, this is the shape of the work, this is what I would do next.* Then it waits
for a yes.

**A design brief answers design questions, not only admin ones.** Who the work is for, why it
is happening now, what the brand should feel like, which surfaces are in scope, who decides.
An earlier version of this skill produced a tidy page of people, channels and deliverables
that never asked any of that, and the gaps only surfaced in the first design review.

**This is a gate, not a document.** Run it when the first real context lands. Do not run it
weekly — the brief holds stable facts, and `now.md` holds everything volatile.

## 1 · Read the context, all of it

Everything that has arrived: `context/` if the project has one, the sources in
`brain/sources.md`, the transcripts and threads a `/briefing` pulled, whatever the owner said
in the session. Read it before writing a line of the brief. A brief assembled from a summary
of the context inherits the summary's mistakes and hides them behind your confidence.

## 2 · Write `brain/project-brief.md` — answer the design questions, and cite them

Fill the prose sections the file already has (Overview, Working arrangements). Then add the
design questions:

1. **Pick the sections that fit the project** from `questions.md` beside this skill. A brand
   project skips *Product and UI scope* and *UX and interaction*; a UI project inside an
   existing brand keeps *Brand strategy* short. A section that does not apply stays as its
   heading and one line, `n/a — why`, so the owner sees it was considered. Inside a section
   you keep, keep every ★ question; drop an unstarred one only when it plainly cannot apply.
   A small job gets a short brief. Do not pad it.
2. **Insert them between Overview and Working arrangements**, in the order `questions.md`
   gives, as `## ` sections of bullets in exactly the form `questions.md` shows. The page
   reads that form, so do not reword the markers.
3. **Answer each one from the context**, cited. What you worked out rather than heard carries
   `^[inferred]`. What nobody has said is `?`, with an owner tag `**[who]**` when you know who
   can answer, and a short note when the context half-answers it. Never fill a gap with a
   plausible answer: a confident guess on this page is what the owner will approve.

Two rules for every answer, and the second one is the reason this skill exists:

**Cite every claim that came from outside this repo.** The form is a source tag, inline:

```
The client wants SSO before launch. ^[Dana · kickoff call · 2026-08-11 14:20](https://meetings.example.com/r/4821?t=860)
The roster is a version behind. ^[Ravi · #client-portal · 2026-08-28](https://slack.com/…)
Two more workstreams are probably coming. ^[inferred]
```

- `who · where · when`, and a link straight to the moment where one exists — a timestamped
  recording URL, a permalink to the message, the mail thread. Not a link to the tool.
- **`^[inferred]` is mandatory for anything you worked out rather than heard.** It renders as
  a small dashed tag. A guess that reads like a quote is the exact failure the charter's
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

- **`brain/open-questions.md`** — every unknown that is not one of the design questions,
  numbered, **each with an owner tag: who can answer it.** A missing design question stays in
  the brief, not here; one owner per question. A question with no owner renders in red,
  because nobody can answer it.
- **`brain/plan.md`** — the stage arc. Stage 1 is current; later stages get a name and an
  entry event, never a bar.
- **The current stage's exit bar**, per project — a decision each, written now if missing.
  Without it the page prints "this stage has no exit bar", which is accurate and is the thing
  to fix, not to hide.
- **`brain/tasks.md`** — the immediate next steps as real task lines, with `bar` on the ones
  inside the exit criterion.

## 4 · Render it

```
python3 brain/brief.py --open
```

Then check what it printed: answered, inferred and missing counts, the key questions still
missing, unwritten sections, steps. An unwritten section renders as a gap on the page — fix it
or say why it stays empty. Read the page before handing it over.

If `brief.publish` in `brain/workspace.toml` is `true`, also publish the page as an artifact
and hand over the link. If it is `false`, **do not publish** — the brief quotes client
material, and `AGENTS.md` says that does not reach an external service without the owner's
say-so. Offer, once, and record the answer in `workspace.toml` rather than asking again.

## 5 · Propose a kickoff workshop when key questions are missing

When any ★ question is still `?`, the page opens with a kickoff call: the opening question,
the key questions grouped by section with who can answer each, and a button that copies the
full agenda. Say it in the hand-over too, in one sentence with the count: *"Six key questions
are unanswered, mostly about audience and scope; I'd put them to Dana in a kickoff."* If the
owner agrees, write the agenda to `brain/drafts/YYYY-MM-DD-kickoff-agenda.md` (the copied
agenda is the starting point) and add the session as a task. If a meeting is hard to get,
offer `/workshop`, which sends the same questions as assumptions to confirm on a phone.

After the kickoff, route the answers back into the brief: each `?` becomes a cited answer, and
the page re-renders with the gap closed.

## 6 · Hand it over, and stop

Say what you are handing over in two or three lines, then the box. Nothing else — the page
is the deliverable, and re-narrating it in the terminal defeats the purpose.

```
┌─ YOUR TURN ──────────────────────────────┐
│ A. Read the brief. Confirm or correct    │
│    the inferred answers and fill what    │
│    you know, then paste the replies.     │
│ B. Tell me what's wrong, or approve it.  │
│ C. Answer: "Kickoff with Dana for the 6  │
│    key questions?"                       │
└──────────────────────────────────────────┘
```

Then **stop**. Do not start stage-1 work off an unapproved brief. If the owner is away and
something is genuinely unblocked and reversible, do that and say you did — but a brief waiting
on a yes is a brief waiting.

## 7 · On approval

1. A decision in `brain/decisions/`: what was approved, what the owner changed on the
   way through, and what it commits the project to. This is the record of the yes.
2. Change the brief's status line to name it:
   `Status: approved 2026-09-04 · [[the-brief-is-approved]]`
3. Re-render, `python3 brain/doctor.py`, commit and push.

Corrections the owner makes are the valuable part of this whole exercise. Each one goes into
the file it belongs to — and if a correction contradicts something already logged, say so
before you write it.

## 8 · When the owner pastes brief replies

The page lets the owner answer on it: a field under each missing question, and *That is
right* / *Correct it* under each inferred answer. The replies come back as one pasted block
starting `Brief replies — <engagement> · <date>`. Treat that block as the owner's own words:

- **An answer** replaces the `?` (and its note and owner tag) with the text, cited
  `^[<owner> · brief page · <date>]`.
- **Confirmed** replaces `^[inferred]` on that answer with the same citation.
- **A correction** replaces the inferred answer with his text, cited the same way. If the
  correction contradicts something already logged, say so before you write it.

Match each reply to its question by section and question text. If one no longer matches,
because the brief changed since he opened the page, say which and ask; never guess. Then
re-render with `python3 brain/brief.py` (no `--open`: he has the page; tell him to refresh,
and the answered replies drop out of his tray), commit, and say in one line how many key
questions are still missing.

