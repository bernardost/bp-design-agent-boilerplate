---
tags: [process]
---
# The charter states each rule and points to the skill that holds its procedure
Date: 2026-11-05 · Status: accepted

## Context

`AGENTS.md` had grown to 46 KB, roughly 11,000 tokens loaded at the start of every session. A
third of it was the 19 always-on behaviors, most of which repeated, step by step, procedure
that already lived in a skill or README (`/remind`, `/transcript`, `/prototype`,
`/playground`, `brain/brand/README.md`). The owner asked for a trim after agents kept missing
the rule to open pages, which sat 200 lines into the file. ^[owner · session · 2026-11-05]

## Decision

- Every rule stays. Each one keeps its opening action and the failure that caused it, and
  points to the skill that has the steps.
- The *Product repos in `projects/`* section (4.5 KB) moved whole into a new skill,
  `/product-repo`, which loads when the work touches a cloned repo. The charter keeps the
  three rules that must hold before anyone reads it: never push there without asking, run git
  with `-C` and name the repo, read that repo's own instructions first.
- Repetition between *The sentences themselves* and *What you generate* was merged; the
  history of the old `NNNN-` decision numbering went, since this archive records it.
- *How this file is written* gained a rule: put procedure where it loads only when used.

The file went from 46,722 to about 24,600 characters.

## Consequences

Clones see the trimmed charter as a MERGE diff on `/update`. The three places that cited the
*Product repos* section by name (`/setup`, `/promote`, `README.md`) now point to
`/product-repo`.
