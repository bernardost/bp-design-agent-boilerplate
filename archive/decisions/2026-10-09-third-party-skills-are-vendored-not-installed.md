---
tags: [process]
---
# Third-party skills are vendored into the repo, never installed per machine
Date: 2026-10-09 · Status: accepted

## Context

The owner wanted Jakub Krehel's `interfaces` collection — thirteen skills for product UI,
MIT-licensed — available to the agent, with credit, if it did not slow sessions down. The
only always-on cost of a skill is its description in the session's skill list; the thirteen
together are about 1,800 characters. Bodies load on invocation.

The same skills could have been installed at user level (`npx skills add`, or
`~/.claude/skills/`). The owner already had one of them, `make-interfaces-feel-better`, there.

## Decision

- `python3 brain/vendor.py` clones each listed collection, copies every skill whole into
  `.claude/skills/` and `.agents/skills/`, and writes `CREDITS.md` with author, licence text,
  version and pinned commit. `--check` reports drift. **A vendored skill is never edited in
  place**; a rule on top of one goes in `AGENTS.md` or in a skill of ours.
- The repo is the one place these live. A clone takes them through `/update` because the
  skill folders are template-owned, so a phone, a colleague's machine and the web session all
  run the same pinned version.
- The user-level copy of `make-interfaces-feel-better` was removed; `/better-ui` supersedes it.
- The charter says how the four overlapping skills split against ours: ours sets the stage,
  theirs does the craft inside a product repo or a playground piece.

## Consequences

- A skill present at both user and project level is listed twice and resolves by precedence
  with no hint which copy won. Keep each skill at one level; if the collection is ever
  installed globally, delete the project copies the same day.
- Refreshing is one command and one commit; the version in `CREDITS.md` is the record of what
  was taken.
