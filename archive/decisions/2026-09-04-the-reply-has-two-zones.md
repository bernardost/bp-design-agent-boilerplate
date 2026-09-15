---
tags: [process]
---
# [[the-reply-has-two-zones]] — The reply has two zones, and the owner's half is in a box
Date: 2026-09-04 · Status: accepted

## Context

The owner ran the workspace on a real project and brought back the transcript. The complaint
was not that sentences were wordy. It was that **process narration and things needing his
attention arrived mixed together**, so finding the part addressed to him meant reading all of
it.

Four specific failures in one session's output:

- The same three findings were announced as they were discovered and then restated in full in
  a summary block. He had to read both to know they matched.
- A one-sentence ask came wrapped in a case for the ask: who to contact, and why that person
  would know. His rewrite: *"Joe mentioned sending over the artifact and spreadsheet. Do you
  have it?"*
- Internal vocabulary was spoken at him — *"bar condition 1's first task can't be done"*. His
  note: *"I have no idea what that is, and the project just started. The agent could have said
  nothing."*
- The closing next-actions list, the only part he needed, was three justified paragraphs. His
  rewrite was three imperatives, one of which quoted the question instead of naming its number.

The last one matters most as a diagnosis: the useful content was there, and the shape hid it.

## Decision

`AGENTS.md` gains a **shape of a reply** section. Any reply longer than a few lines has two
zones with a line between them.

**While tools run:** one short line per action. No findings, no reasoning, no plan for the
next call. What you find there is not explained there.

**At the end:** a drawn box, 44 characters wide, emitted inside a code fence so the terminal
cannot reflow it, holding only numbered actions for the owner. He chose the box over a
horizontal rule and over a blockquote gutter, shown as rendered previews. Never widen it — cut
the line instead. If nothing needs him, there is no box and one line says so.

Four rules follow it: a finding is reported once; do not make a case for a small ask; never
speak the brain's own vocabulary at him, and a number that must appear carries its content;
corrections you already made get a clause, not a section.

The stage-check behavior gains a matching clause — **reason in that vocabulary, do not speak
it** — so the two rules cannot fight.

## Consequences

- The box is the one permitted repetition at the end of a long reply, replacing the older
  "restate the conclusion" rule.
- The 44-character width is a hard constraint on how much can be asked at once, which is
  probably the useful side effect.
- Nothing enforces this — `doctor.py` lints files, not replies. It holds only as long as the
  charter is read, which is the same footing as every other communication rule here.
- Unresolved: the owner's global `human-comms` skill fires on any message a human reads and
  bans em dashes outright, while this charter uses them freely. Ask which wins rather than
  splitting the difference.
