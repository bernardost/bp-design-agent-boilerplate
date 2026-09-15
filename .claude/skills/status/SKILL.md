---
name: status
description: One-screen project readout — current focus, open questions by owner, recent decisions, task state. Use for /status or "where are we".
---

# Status

Read (do not guess from memory): `brain/now.md`, `brain/plan.md`,
`brain/open-questions.md`, `brain/tasks.md`, and the three most recent files
in `brain/decisions/`.

**Group the readout by project** when `[projects]` in `brain/workspace.toml` holds more than
one key: each strand gets its stage, its open questions and its tasks under its own heading.
An engagement-wide item (`project: all`) goes in a short section of its own at the end. Never
merge two strands into one list — the owner reads this to decide where to spend the next hour,
and a blended list makes that decision for him badly.

Output one screen, no more:

- **Focus** — from now.md, one line, with the current stage and its bar
- **Next actions** — the top 3, with any blockers
- **Open questions** — grouped by owner tag, count + the most urgent one each
- **Recent decisions** — the last 3, one line each
- **Tasks** — counts by status, and anything `doing` by title
- **Waiting on you to send** — unsent drafts in `brain/drafts/`, by subject and recipient

If now.md's date is older than the newest decision or task change, note that
it may be stale and offer to reconcile — or say it is worth `/close`-ing.
