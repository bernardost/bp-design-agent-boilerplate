# Tags

*The owner of the tag vocabulary. Tags are **global to the brain** — one vocabulary across
decisions, insights, braindumps and briefings, so a decision and an insight can carry the same
tag. That is the point of having them.*

**Format.** Frontmatter at the top of every brain file:

```markdown
---
tags: [onboarding, portability]
---
```

**Not a project.** Which strand of work a record belongs to is `project:` in frontmatter, a
separate key with a closed vocabulary from `[projects]` in `brain/workspace.toml`. Never make a
tag for it: tags are open, global and thematic — a decision and an insight sharing one is the
point — while a project is a compartment the projections filter on, and mixing the two would
make both useless.

**Tag or link?** A tag is membership in a theme; a wiki-link in double brackets is a claim about two
specific notes. If a tag would have exactly one member, it wanted to be a link. `doctor.py`
reports tags that aren't defined here, tags defined here and never used, and files with no
tags at all — all reports, never failures, because a new tag is usually legitimate.

**The graph, free.** Frontmatter tags plus wiki-links are exactly what Obsidian reads. Open
`brain/` as a vault and the interconnected view is there, with nothing committed to this repo
and no dependency added. Optional, never assumed.

---

## Vocabulary

*A starter set for a design project — `/setup` reshapes it from the interview, and it should
end up describing this project's themes, not these.*

- `brief` — what the client asked for, and how that has moved
- `research` — what we learned about users, the market, or the existing thing
- `concept` — direction, exploration, the shape of the idea
- `exploration` — a spread of options put on the table before one was chosen
- `craft` — visual and interaction execution: type, colour, motion, detail
- `accessibility` — who can and cannot use what we made
- `system` — tokens, components, patterns, the reusable layer
- `handoff` — what engineering or the client needs to carry it forward
- `process` — how we work: rituals, tools, what to do differently next time
- `stage-bar` — what has to be true to leave a stage
