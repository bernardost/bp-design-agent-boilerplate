---
name: status
description: One-screen project readout — current focus, open questions by owner, recent decisions, task state. Use for /status or "where are we".
---

# Status

Read (do not guess from memory): `brain/now.md`, `brain/plan.md`,
`brain/open-questions.md`, `brain/tasks.md`, and the three most recent files
in `brain/decisions/`.

Output one screen, no more:

- **Focus** — from now.md, one line, with the current stage and its bar
- **Next actions** — the top 3, with any blockers
- **Open questions** — grouped by owner tag, count + the most urgent one each
- **Recent decisions** — last 3 ADRs, one line each
- **Tasks** — counts by status, and anything `doing` by title

If now.md's date is older than the newest decision or task change, note that
it may be stale and offer to reconcile.
