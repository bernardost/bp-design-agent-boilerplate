# `decisions/` — the decision log

One file per decision, `NNNN-lowercase-kebab-title.md`, numbered in order. We say **decision**,
not "ADR" — same discipline, no software jargon. A decision stated or reached in conversation
gets logged here unprompted; that is the assistant's job, not a favor.

Every file carries frontmatter tags from `brain/tags.md`, and links out with wiki-links in double brackets.

Superseded decisions get their `Status:` line changed to `superseded by NNNN`, plus a "do not
cite" tombstone header, and stay put — `doctor.py` checks both. Copy
`0000-decision-template.md` to start one.
