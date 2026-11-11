---
tags: [process]
---
# The moodboard skill is `/interactive-moodboard`, and it starts by picking regular or interactive
Date: 2026-11-11 · Status: accepted

## Context

`/moodboard` always built the full desk: ideas drawn from the research, visions assembled from
them, and wires between the two. Someone asking for a moodboard often wants a regular one,
references collected on one surface. [[the-moodboard-skill-is-now-visions]] renamed the skill
`/visions` the same morning; the owner said he would not remember a skill by that name.

## Decision

The skill is `/interactive-moodboard`. It still answers every moodboard request, and its first
step is to pick the kind:

- **Regular** when the work lives in Figma, when the owner asked for references, or when
  there is too little research to argue from. It goes on a Figma page, or into
  `brain/references/<topic>/` with captions.
- **Interactive** when research has piled up or several directions need comparing. This is
  the desk as before.

When neither is clear, the agent asks once and sells the interactive one by what it does: it
connects the insights and notes to each idea, so you see where every idea comes from.

The records folder stays `brain/moodboards/`, so projects cloned earlier keep working.
`board.py` and `doctor.py` are unchanged apart from wording.

## Consequences

- Projects that took the old skill get the new folder `.claude/skills/interactive-moodboard/`
  on `/update` and should delete `.claude/skills/moodboard/` by hand.
- Regular moodboards leave no record in `brain/moodboards/`; they live where the work lives.
