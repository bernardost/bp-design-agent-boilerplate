---
name: transcript
description: Take a pasted or attached meeting transcript, save it verbatim, and interrogate it before trusting a word of it — a numbered table of what the transcript cannot tell you, with timestamps, answered in one pass. Use for /transcript, and whenever a full transcript arrives in a session however it arrives.
---

# Transcript — read it for what it got wrong

A transcript looks like evidence and is not. It is a machine's best guess at what was said,
and **it is least reliable exactly where it matters most**: proper nouns, numbers, who was
speaking, and the thing somebody was pointing at on a shared screen.

The person who pastes it was in the room. They read straight past the errors, because they
know what was meant. You were not in the room, so you cannot — and if you route a transcript
straight into decisions and tasks, a mishearing becomes a project fact with a citation
attached to it. That is the exact failure the charter's label-evidence rule exists to stop,
arriving through the one door that looks like a quotation.

**So: save it, interrogate it, ask once, then route.** Never route first.

## 1 · Save it verbatim, before anything else

`brain/briefings/YYYY-MM-DD-<meeting>-transcript.md`, exactly as pasted. Frontmatter tags from
`brain/tags.md`; no `project:` key, because a meeting legitimately spans the engagement and
routing is what assigns a strand.

**You never edit a transcript.** Not to fix a name, not to tidy a sentence, not after the
owner confirms what was really said. It is a verbatim capture and it is governed by the same
rule as a braindump: processing routes content out, it does not rewrite the source.
Corrections live in their own section underneath (step 4).

## 2 · Read it for the six things it cannot tell you

Go through the whole transcript once, looking for these. Quote the line and keep the
timestamp — a question without a timestamp makes the owner search for the moment themselves.

1. **Something on screen with no words for it.** *"this one"*, *"as you can see here"*,
   *"the one on the left"*, *"that number"*. A screen was shared and the transcript recorded
   the pointing, not the thing. Ask for the screenshot, the file or the link. This is the
   single most common hole and the one that silently loses the actual content of a review.
2. **Proper nouns the recogniser guessed at.** A name spelled two ways in the same file, an
   acronym that is not in `brain/glossary.md`, a product or company name that is also an
   ordinary word. Speech recognition collapses on exactly the vocabulary a project runs on,
   because it is the vocabulary the model has never heard.
3. **Who actually said it.** `Speaker 2`, an unlabelled turn, or a line attributed to someone
   it does not sound like — a client's commitment in the agency's mouth, or the reverse. A
   decision filed under the wrong person is worse than an unfiled one, because it is wrong in
   a place nobody rereads.
4. **Numbers, dates, money and versions.** The category transcription handles worst and the
   category most likely to be quoted into a brief. *"fifteen"* / *"fifty"*, a date with no
   year, a budget figure, *"v2"* heard as *"B2"*.
5. **`[inaudible]`, crosstalk and sentences that stop mid-clause.** Most are noise. The ones
   that matter are the ones sitting next to a decision, a number or a commitment — flag those
   and leave the rest.
6. **Lines whose meaning is carried by tone.** Flat text cannot tell a commitment from a joke
   from a hypothetical. *"We could just ship it Friday"* is a plan or a groan, and the
   difference is the whole project. Only raise these where something would be filed on the
   strength of them.

**What not to raise.** Filler, false starts, a misheard word whose meaning is obvious from the
sentence around it, and anything you can settle from `brain/glossary.md`, `brain/decisions/`
or the brief. Check those first. A table of twenty questions, most of them answerable from the
repo, trains the owner to skim the table — and then the one question that mattered goes
unanswered.

## 3 · Ask once, as a numbered table

One pass, every question together, in the transcript file **and** in your reply. Never a
question at a time: the owner answers a transcript in one sitting or not at all.

```markdown
## Questions

| # | time | what the transcript says | what I need | my reading |
|---|------|--------------------------|-------------|------------|
| 1 | 00:14:32 | "we should just use the **Vericel** approach" | Spelled Vericel once, Veracell twice at 00:31 and 00:47. Which, and is it a company or a protocol? | a company — the regulated comparator from the brief |
| 2 | 00:22:05 | "so **this** is the one we'd ship" | A screen was shared. Which artifact? A screenshot or the file name. | the portal dashboard, not the marketing page |
| 3 | 00:41:18 | Speaker 2: "we'll have it by the 14th" | Speaker 2 is unlabelled here and labelled Dana at 00:12. Same person? | Dana |
| 4 | 00:58:40 | "about **fifteen** thousand for the build" | 15 or 50 — the brief says the band is 40–60k. | fifty |
```

**Always propose your reading.** A question the owner answers by confirming takes five
seconds; a blank they have to fill takes a minute and often does not get filled at all. Same
reason `/workshop` sends assumptions rather than blanks. Where you genuinely have no reading,
say so — an invented guess is worse than an empty cell.

Order the table by how much turns on the answer, not by timestamp. The question that blocks a
decision goes first.

In your reply, put the table above the box; the box carries one line pointing at it.

## 4 · Route what is safe, hold what is not

Do not stop and wait. Route everything whose meaning does not depend on an open question —
`/briefing`'s step 5 is the routing, and it applies here unchanged. Hold back only the items
that would change depending on an answer, and say which those are.

Anything you do file on an unconfirmed reading carries `^[inferred]`, in the form
`brain/sources.md` specifies. The transcript is the source; cite it by filename and timestamp:

```
The build lands by the 14th. ^[Dana · kickoff transcript 00:41:18 · 2026-10-02]
```

## 5 · When the answers come back

- **Corrections go in a `## Corrections` section** at the foot of the transcript file: the
  timestamp, what the transcript says, what was actually said, and who confirmed it. The
  transcript body stays exactly as it was. Anyone reading the file later sees both the
  machine's version and the human's, which is what makes the record checkable.
- **Decoded names go to `brain/glossary.md`** — every person, acronym, codename and internal
  name you had to ask about. That is what it owns, and it is the file that stops the same
  question being asked after the next meeting.
- **Screenshots and files the owner sends go to `context/`**, which owns source material from
  outside, and the table row that asked for them cites the path.
- **Then route the held items**, and re-check anything already filed on a reading that turned
  out wrong. A correction is not done until the grep is clean — the charter's rule, and it
  applies to a misheard name propagated into three files.

## Guardrails

- **A long transcript is not a reason to skim.** If it is too long to read closely, say so and
  read it in passes — never sample it and present the result as though you had read it all.
- **Do not summarise instead of interrogating.** A summary of a transcript you have not
  questioned is a confident restatement of its errors, and it reads as more authoritative than
  the transcript did.
- **The owner's own words about the meeting are not a transcript.** If they describe what
  happened rather than pasting the record, that is a `/braindump`.
- **Confidential by default.** A transcript is other people's words. `brain/briefings/` holds
  it, and on a non-private remote that directory belongs in `.gitignore` — say so once if the
  setup needs it.
