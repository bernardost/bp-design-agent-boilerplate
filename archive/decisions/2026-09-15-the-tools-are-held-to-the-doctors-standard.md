---
tags: [system, process]
---
# The tools are held to the doctor's standard
Date: 2026-09-15 · Status: accepted

## Context

An independent review read the tree and reported eleven findings. Checking each one against
the code rather than accepting or dismissing it produced three groups, and the split is the
useful part of the exercise.

**Real, and mine.** The move to dated decision filenames left `feed.py` matching `^(\d{4})-`
on a filename to find a decision's id. On `2026-09-15-slug.md` that captures the *year*, so
every mention of "2026" in any prose became a link to whichever decision sorted last that
year — and `[[the-slug]]`, the citation form the charter had just started mandating, was not
registered as a key at all. I had fixed that same pattern in `doctor.py` and missed its twin.

**Real, and older.** Citation hrefs accepted any scheme, so a `javascript:` or `data:` URL in
a source tag shipped as a clickable link — and source tags are not all owner-written, because
`/briefing` routes text in from Slack, mail and recordings. Generated pages embedded absolute
`/Users/…` hrefs, which break on the phone the remote exists to serve and print the owner's
directory layout into a shared file. `redate.py` advised a clean tree without requiring one,
and rewrote every citation in the tree before renaming a single file.

**Not real.** A reported `&amp;amp;` double-escape came from a test that escaped the input
before calling a function that escapes its own input; the live path was correct, and I
reproduced the bug only by making the same mistake. A reported staleness bug cited the feed
check, which compares full mtimes — though the neighbouring freshness report genuinely was
date-granular, which hides an edit made an hour after a same-day rewrite. Four findings
described code the review had not fetched.

`doctor.py` would not have caught any of the real ones. It lints the content of a brain and
has nothing to say about the tools that render it.

## Decision

**`brain/test_brain.py`, run by GitHub Actions on every push, alongside `doctor.py`.**

1. **Every case exists because something broke or nearly did.** A test with no failure behind
   it is one nobody maintains. The current set: a slug and a full stem resolve and a year
   never does; a legacy number still resolves; unsafe schemes are not clickable and `&` is
   escaped exactly once; no page ships an absolute home path; the migration preserves all
   three citation forms, refuses a dirty tree, and changes nothing on a second run; one
   project asks for no tagging and two enforce it.
2. **Pure functions are imported; anything that reads a brain runs as a subprocess against a
   temporary workspace.** The scripts resolve their paths from `__file__`, and faking that
   would be testing the fake.
3. **Fixes stand on their own evidence.** Each of the three real findings was reproduced
   before it was fixed, and the mutation was re-applied afterwards to confirm the test fails
   without the fix. A review is a prompt to check, not a verdict to act on — in both
   directions.

## Consequences

- A clone inherits the workflow file and is checked from its first commit.
- `render.py` stays fast: `/close` runs the linter, not the suite. CI is what makes the suite
  unskippable, which is the same argument as `doctor.py` being a program and not a README.
- Stdlib only, like everything else here, so there is nothing to install and no lockfile.
- The suite covers the tools, not the taste. Nothing here checks that a page looks right, and
  `brain/lenses/craft.md` with `/critique` stays the only answer to that.
