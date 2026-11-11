---
tags: [process]
---
> **Superseded the same day — do not cite.** Replaced by
> [[the-moodboard-skill-is-interactive-moodboard]]: the owner would not remember `/visions`.

# The moodboard skill is now `/visions`, so "moodboard" can mean a plain one again
Date: 2026-11-11 · Status: superseded by [[the-moodboard-skill-is-interactive-moodboard]]

## Context

`/moodboard` builds a desk: ideas drawn from the research, visions assembled from them, and
wires between the two. The owner pointed out that someone asking for a moodboard often wants
the plain thing, a page of collected references. With the skill named `moodboard`, that
request loaded the full desk procedure.

## Decision

The skill is renamed `/visions` and its records folder `brain/moodboards/` becomes
`brain/visions/`. `board.py` keeps its name and renders `brain/visions/*.md`; `doctor.py`
reports on that folder. The skill's description now says it is not for a plain moodboard.
The charter's rule keeping the desk, exploration and decision apart now names the desk and
says a plain moodboard needs no skill.

## Consequences

- A request for "a moodboard" no longer triggers the desk procedure.
- Projects cloned earlier still have `brain/moodboards/` and `.claude/skills/moodboard/`.
  `upstream.py` keeps `brain/moodboards/**` project-owned so `/update` never touches what is
  there. When a project takes this update, it should delete the old skill folder and
  `git mv` any desk files into `brain/visions/`. As of today, none of the six local projects
  that took the desk has filed one.
- Dated records that say `/moodboard` (archived decisions, the 2026-10-02 deck) stay as
  written.
