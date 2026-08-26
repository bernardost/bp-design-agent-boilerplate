---
tags: [brain-structure, interface]
---
# 0004 — Tags are global to the brain, and the vault is the graph
Date: 2026-08-26 · Status: accepted

## Context

The owner: *"I love the whole concept of a brain with tags. Tags should be global to the
brain, so that an ADR and an insight can share the same tag… I would want this to work
really well and for the user to be able to visualize the brain somehow (interconnected nodes
are awesome, but it would require obsidian right? Don't want to bloat this too much tho)."*

The brain already has one cross-reference mechanism — wiki-links in double brackets — and no tags.

## Decision

Tags live in **YAML frontmatter** at the top of every brain file: `tags: [a, b]`. One
vocabulary across the whole brain, owned by `brain/tags.md` (one line per tag: what it
means, and nothing else). A decision and an insight sharing a tag is the point.

Frontmatter `tags:` plus those wiki-links is exactly what Obsidian reads, so **the
visualization requires no code and no dependency**: open `brain/` as a vault and the graph
is there. Obsidian is optional and never assumed — nothing in the workspace reads it, and
no plugin, config, or `.obsidian/` directory is committed.

`doctor.py` REPORTs (never FAILs) tags outside the vocabulary and prints tag counts. A new
tag is usually legitimate; failing on it would train the owner to ignore the output.

Deferred, not rejected: a dependency-free `brain/map.html` (nodes = files, edges = links and
shared tags, hand-rolled force layout in inline SVG) so the graph is visible without
Obsidian. It waits on [[0008-the-visual-feed-is-an-experiment-first]] proving the HTML
surface is worth building on at all.

## Consequences

- Every new brain file carries frontmatter; the templates and skills all emit it.
- Two ways to relate notes now exist. The division: a wiki-link is a specific claim about
  *these two* notes; a tag is membership in a theme. If a tag would have one member, it is a
  wiki-link.
- `feed.py` already skips leading frontmatter when it reads a first paragraph, so tooltips
  are unaffected.
