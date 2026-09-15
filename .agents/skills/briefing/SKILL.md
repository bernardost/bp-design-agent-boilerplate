---
name: briefing
description: Pull what happened across the project's declared external sources — Slack, meeting recordings, mail, calendar, tracker, Notion — into a dated file in brain/briefings/, then route decisions, insights, tasks and questions out to their owning files. Use for /briefing, "what did I miss", "catch me up", or at the start of a session after time away.
---

# Briefing

Answer one question: **what happened that I need to know about?** Not "what is in each tool" —
the owner does not think in tools, and a readout organized by source makes them do the
assembly the assistant should have done.

## 1 · Scope it

Default window: since the last file in `brain/briefings/`, or the last 7 days if there is
none. Take an explicit window from the arguments if given ("since Monday", "last two weeks").
Say which window you used.

Read `brain/sources.md` for what to look at. Only `connected` sources get called; `wanted`
ones are named as gaps at the end, never silently skipped.

## 2 · Pull, in priority order by question type

Different questions live in different places, so search in the order that matches:

- **decisions and direction** → chat first, then meetings, then mail
- **commitments and deadlines** → mail and tracker first
- **what a specific person said** → chat and meetings
- **schedule and who was in the room** → calendar

Where a source fails — not connected, rate-limited, timed out — **carry on and report it**.
One dead connector must never take the whole briefing down with it.

## 3 · Group by topic, never by source

This is the rule that makes a briefing readable. One heading per topic — a decision, a thread,
a deliverable, a person's blocker — with the evidence gathered under it from wherever it came.
The same decision mentioned in Slack and confirmed by email is **one item**, not two.

Order: **action items first** (things needing the owner), then decisions and changes, then
context worth knowing, then noise-level mentions if any.

## 4 · Attribute every line

Non-negotiable, and the reason this skill exists rather than a summary in chat. Every claim
carries who said it, where, and when:

```
- Marcy wants the nav simplified before Thursday's review — from Marcy Okonkwo, #proj-design (2026-08-24), [link]
```

If you are characterizing rather than quoting, mark it `inferred`. A briefing is where someone
else's half-sentence hardens into a project fact, and that is the failure the charter's
label-evidence rule exists to stop. **No attribution, no line.**

New people, nicknames, acronyms or codenames you had to decode go to `brain/glossary.md` — that
is what it owns, and a briefing is where they surface.

## 5 · Write the dated file, then route

Write `brain/briefings/YYYY-MM-DD.md`: the window, the sources actually searched, the grouped
items, and the gaps. Frontmatter tags from `brain/tags.md`.

Then route out, exactly as `/braindump` does — the briefing is a **dated record and owns
nothing**. A briefing legitimately spans the engagement, so the file itself carries no project
key and **every item routed out of it names its strand**. Where the source does not say which,
ask; collect the ambiguous ones into one question rather than asking per item:

- a decision someone else made that we must live with → `brain/decisions/`
- something needing the owner's answer → `brain/feed-items.md`, stating what it blocks
- a next action → `brain/tasks.md` in the line grammar
- a question only a named person can answer → `brain/open-questions.md` with the owner tag
- a durable realization → `brain/insights/`
- a contradiction with a logged decision → **raise it in chat before filing anything**

## 6 · Report

Lead with the count of things needing the owner, then the topics one line each. Close with
**which sources were searched and which were not** — a briefing whose scope is invisible reads
as complete when it isn't.

If the material is confidential and the remote is not private, say so: `brain/briefings/`
holds other people's words and belongs in `.gitignore` on that setup.
