# Workshops

*The owner of **questions put to a client, live or async, and the answers that come back**.
`/workshop` writes all of it.*

## A live workshop — `YYYY-MM-DD-<client>-<title>/`

One folder per workshop run with `brain/workshop.py` (the `/workshop` skill has the commands).

```
deck.json    the boards, their questions and every answer. The truth; the page writes it.
notes.md     the answers as markdown, rewritten on every save. Read and route from this.
history/     a copy of deck.json every ten minutes and before a conflicting write. Gitignored.
send/        the deck's questions as a form file, one per person it was emailed to.
responses/   one file per form sent: the questions as sent and the answers that came back.
```

`notes.md` carries an *Answers from <name>* section per form. Those answers were typed by the
client alone, so they are quotable as theirs; the deck's own answers were typed by the owner.

Never edit either file by hand while the workshop's page is open: the page's next save wins.
`notes.md` carries `tags:` and, in a workspace with several projects, `project:`, from the
deck; `doctor.py` reads it like any other record here.

## A built async workshop

For when a form is not enough: the questions rebuilt as screens with our assumptions in them.

A workshop is not a form and not a survey: it is a call, taken apart into screens somebody can
answer on a phone in a taxi, in pieces, over a day. Two kinds of file, and they are different
things.

## The outline — `YYYY-MM-DD-<topic>-outline.md`

The content source, written and cut **before anything is built**. One chapter per heading, one
screen per block, and every screen that has a guessable answer arrives with our guess already
in it. The owner cuts this file, not the code — cutting five screens costs nothing here and
costs an afternoon once it is built.

```markdown
---
tags: [brief, research]
project: <key>           # or `all`; omit entirely in a one-project workspace
---
# Async workshop — <topic>
For: <name, role> · Sent: YYYY-MM-DD · Lives at: <url>

## Chapter 1 — <name>
### <screen title>
Kind: rank | pick | slider | matrix | tabs | wall | flow | sentences | single | checklist | text
Ask: <the question, in the words the stakeholder will read>
Our assumption: <the option that arrives selected, and why we believe it>
^[who · where · when](link)   ← if the assumption came from something they said
```

Every assumption that came from outside this repo carries its source tag
(`brain/sources.md`). An assumption we invented is marked `^[inferred]`, and stays marked
that way all the way into the answers file — that is the whole reason the method is safe.

## The answers — `YYYY-MM-DD-<topic>-answers.md`

What came back, one line per screen, each tagged **`chose`**, **`let stand`** or
**`not reached`**.

A let-stand answer is *our assumption, unopposed*. It is evidence, and it is weaker evidence
than a tap. It is never quoted as the stakeholder's words, and anything built on one says so.
Losing that distinction is how a guess of ours hardens into a client requirement, which is the
one failure this folder exists to prevent.

Answers are source material, so they get routed out like a braindump: decisions to
`brain/decisions/`, realizations to `brain/insights/`, what is still unanswered to
`brain/open-questions.md`. The answers file stays verbatim.

## The thing itself

A built async workshop is work, not record — it lives wherever `work_lives` in
`brain/workspace.toml` says the work lives, never in `brain/`. Only the outline, the answers,
and the decisions they produce belong here. The live deck is the exception: its code is the
template's own (`brain/workshop/`), and only its folders land here.
