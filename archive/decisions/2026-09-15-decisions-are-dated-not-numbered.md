---
tags: [process, system]
---
# Decisions are dated, not numbered
Date: 2026-09-15 · Status: accepted

## Context

`[[parallel-sessions-take-worktrees-unprompted]]` claimed that decisions, insights and drafts
"are new files per unit of work; they merge clean." That was false for decisions, and the same
decision's own consequences recorded it being false: writing it collided with another session's
`0016` and three files had to be renumbered on the rebase. The fix recorded there — pull first,
renumber on rebase — treats a design fault as a discipline problem.

The fault is that `NNNN-` does two jobs. It **identifies** the file that `[[0047-…]]` points
at, and it **orders** the log. Ordering is fine. Identity is not, because the next free number
depends on a commit the session has not fetched, so two sessions writing at once both pick it
and find out at merge, after both files exist. No amount of pulling fixes a number chosen from
a pool that every open tab shares.

A second proposal came from the agent running this workspace on a live project: write
unnumbered, and have a script assign numbers in date order at merge. It keeps the `0047`
shorthand, and it breaks something quieter — a number that can change after the file is
written means every citation of a bare number rots, and `doctor.py` counts bare numbers as
citations today.

## Decision

**`brain/decisions/YYYY-MM-DD-slug.md`. The date orders the log; the slug is the identity.**

1. **Citations are `[[the-slug]]`**, without the date, so a citation survives a corrected date.
   `doctor.py` resolves the slug, the full stem, and a legacy bare number.
2. **Two decisions may not share a slug.** `doctor.py` fails on that — `[[the-slug]]` has to
   name one file, and that is the one rule here with no legitimate exception.
3. **Nothing is assigned at merge.** Two parallel sessions collide only by writing the same
   decision on the same day, which is a collision they should have.
4. **The heading loses its number too**, so the identifier does not survive in the one place
   nothing checks it.
5. **`brain/redate.py` migrates an older log**, filenames and citations together, dry run by
   default. Legacy `NNNN-` names are reported by `doctor.py`, never failed: a half-migrated
   tree has to keep working.

## Consequences

- The worktree rule's claim becomes true, and `AGENTS.md` now says which change made it true.
- `FEED-n` still numbers from a shared pool. It stays that way because feed items are
  short-lived and live in one file, which the worktree rule already leaves to the merging
  session — but that is why `feed-items.md` is on that list.
- The `0047` shorthand is gone. The charter already required restating a decision's content
  rather than citing its number at the owner, so the loss is to agent-to-agent shorthand only.
- Alphabetical order in the folder is now chronological order, which numbering also gave.
- The migration is one-way and rewrites citations across the tree. Run on a clean tree; the
  dry run is the review. A number is only unique within one folder, so a repo with two
  numbered logs migrates them one at a time.
