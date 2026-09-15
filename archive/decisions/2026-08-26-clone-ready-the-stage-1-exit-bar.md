---
tags: [stage-bar, template-shape]
---
# [[clone-ready-the-stage-1-exit-bar]] — Clone-ready: the Stage 1 exit bar
Date: 2026-08-26 · Status: accepted

## Context

The stage arc rule is that a stage's exit bar is written when the stage is entered, or the
stage never ends — every next improvement to a template is genuinely useful. Stage 1 is
repointing this workspace from the engagement it came from to the blank design-project
workspace of [[a-design-project-workspace-that-resets-on-clone]].

The temptation here is unusually strong, because the workspace is the product: better
onboarding copy is always available.

## Decision

Stage 1 exits when all of the following are true.

1. **A fresh clone plus one `/setup` run yields a configured workspace.** The quiz's answers
   land in the files named in [[setup-is-a-skill-and-one-config-file]], the inherited
   brain is blank, `python3 brain/doctor.py` PASSes, and `python3 brain/feed.py` renders.
2. **No project constant lives in a script.** `doctor.py` and `feed.py` read
   `brain/workspace.toml` through `brain/config.py`; a placeholder left unfilled is reported,
   not silently accepted.
3. **The charter is portable and says "decision".** `AGENTS.md` is the single charter,
   `CLAUDE.md` imports it, and the word "ADR" appears nowhere outside this stage's own
   records.
4. **Push-as-you-go and the wrap-up signal are in the charter and observably followed** —
   each completed unit of work committed and pushed without being asked, and the one-line
   wrap-up signal fired at a real seam.
5. **Tags work end to end.** Every brain file carries frontmatter tags, `brain/tags.md` owns
   the vocabulary, and `doctor.py` reports unknown tags and counts.
6. **The cheap half of the feed is done and the expensive half is a task, not a promise** —
   past items collapsed, `feed.py` inside `/close`, staleness reported; screenshots left as
   the experiment [[the-visual-feed-is-an-experiment-first]] describes.

**Not required to exit:** the screenshot experiment · `/briefing` and any connector work ·
`brain/map.html` · onboarding copy polish · a second project's worth of validation.

## Consequences

- The bar is checkable by running two commands and reading one grep, which is the property
  that makes it a bar rather than an ambition.
- Stage 2 is the feed experiment; Stage 3 is sources and briefings. Their bars get written
  on entry, not now.
