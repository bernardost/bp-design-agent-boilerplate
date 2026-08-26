---
name: braindump
description: Capture an unstructured braindump from the user, save it verbatim, then extract and route decisions, insights, tasks, and questions into the brain. Use when the user wants to dump thoughts, thinks out loud at length, or invokes /braindump.
---

# Braindump

## Capture

1. If the user provided the dump as arguments or in the message, use that.
   Otherwise ask for it and let them talk — do not interrupt, structure, or
   summarize while they're dumping. Short acknowledgments only.
2. Save the raw dump **verbatim** to `brain/braindumps/YYYY-MM-DD-HHMM.md`
   with a one-line topic header. Never rewrite or clean up the original.

## Process

Extract and route, quoting or tightly paraphrasing the source:

- **Decisions** (stated or clearly arrived at) → new ADR in
  `brain/decisions/` (next number, standard format), linked back to the dump.
- **Insights** (durable realizations, not task-level) → small notes in
  `brain/insights/` with `[[links]]` to related notes and decisions.
- **Tasks / next actions** → `brain/tasks.md`, in the line grammar.
- **Questions** → `brain/open-questions.md` with an owner tag.
- **Contradictions**: if anything in the dump conflicts with a logged
  decision, flag it to the user — do not silently file it.

## Report

End with a short filing report: what went where, one line per item, with
paths. If something was ambiguous (decision vs. musing), say you left it
unfiled and ask.
