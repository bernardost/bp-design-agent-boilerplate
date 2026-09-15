# `decisions/` — the decision log

One file per decision, `YYYY-MM-DD-lowercase-kebab-title.md`. We say **decision**, not "ADR" —
same discipline, no software jargon. A decision stated or reached in conversation gets logged
here unprompted; that is the assistant's job, not a favor.

**The date orders the log; the slug is the identity.** Cite a decision as `[[the-slug]]`,
without the date, so the citation survives a corrected date. Two decisions may not share a
slug — `doctor.py` fails on that, because `[[the-slug]]` has to name one file.

Decisions used to be numbered `NNNN-`. The number did two jobs, and one of them broke: the next
free number depends on a commit a parallel session has not fetched, so two sessions writing at
once both claimed it and found out at merge. A date is already on the file and orders it just
as well. `python3 brain/redate.py` migrates an older log, citations included.

Every file carries frontmatter: `tags` from `brain/tags.md`, and — in an engagement running
more than one project — `project:` naming the strand it belongs to, or `all` for a decision
that governs the whole engagement. Link out with wiki-links in double brackets.

Superseded decisions get their `Status:` line changed to `superseded by [[slug]]`, plus a "do
not cite" tombstone header, and stay put — `doctor.py` checks both. Copy
`0000-decision-template.md` to start one.
