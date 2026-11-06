---
tags: [process]
---
# The brief asks the design questions, and shows which are missing
Date: 2026-11-06 · Status: accepted

## Context

`/brief` produced a useful page, but a tactical one: people, channels, deliverables, the plan.
It never asked what a design brief asks — why now, for whom, what the brand should feel like,
which surfaces are in scope, who decides — so those gaps surfaced later, in design reviews.
The owner asked for those questions, answered from the context or asked, with the page
showing at a glance what is missing and inferred, and a kickoff workshop proposed for the
important gaps. He supplied the question set. ^[owner · session · 2026-11-06]

## Decision

- `.claude/skills/brief/questions.md` holds the questions, in eight sections, with ★ on the
  key ones. It is template-owned, so clones get it through `/update`; the brief itself is the
  project's and holds the answers.
- `/brief` copies the sections that fit the project. A section that does not apply stays as
  `n/a — why`; a small job gets a short brief.
- An answer's state is read from how it is written: cited text is answered, `^[inferred]` is
  inferred, `?` is missing (with an optional owner tag), `n/a` is not applicable.
- The page gets a side navigation with a missing-count per section, a coverage bar whose
  legend filters the page, a distinct mark per state, and a kickoff call listing the missing
  key questions with a button that copies the full agenda.
- Missing design questions stay in the brief and are not copied into `open-questions.md`,
  which keeps the other unknowns.

- The owner can answer on the page: a field under each missing question, and confirm or
  correct under each inferred answer. Replies stay in the browser until he copies them as one
  block and pastes it into the session, the same contract as the review page. `/brief` step 8
  routes them, cited to him and the brief page. ^[owner · session · 2026-11-06]

## Consequences

A brief written before this has no question sections; the page says so and `/brief` adds
them. Slice one, Deliverables and Out of scope moved from prose sections into questions under
*Scope, process and decisions*.
