# Workshops

*The owner of **questions put to a stakeholder asynchronously, and the answers that come
back**. `/workshop` writes both. A workshop is not a form and not a survey: it is a call,
taken apart into screens somebody can answer on a phone in a taxi, in pieces, over a day.*

Two kinds of file live here, and they are different things.

## The outline — `YYYY-MM-DD-<topic>-outline.md`

The content source, written and cut **before anything is built**. One chapter per heading, one
screen per block, and every screen that has a guessable answer arrives with our guess already
in it. The owner cuts this file, not the code — cutting five screens costs nothing here and
costs an afternoon once it is built.

```markdown
---
tags: [brief, research]
---
# Async workshop — <topic>
For: <name, role> · Sent: YYYY-MM-DD · Lives at: <url>

## Chapter 1 — <name>
### <screen title>
Kind: single | checklist | rank | sliders | matrix | wall | fields | text
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

The built workshop is work, not record — it lives wherever `work_lives` in
`brain/workspace.toml` says the work lives, never in `brain/`. Only the outline, the answers,
and the decisions they produce belong here.
