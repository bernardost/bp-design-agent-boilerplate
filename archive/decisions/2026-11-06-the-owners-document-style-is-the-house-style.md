---
tags: [process]
---
# The owner's document style is the house style, with a variant for pages that are used
Date: 2026-11-06 · Status: accepted

## Context

The house lens set Inter, white paper and an architecture-magazine register. The owner has
since built his own visual language for his business documents — Geist, a three-column grid,
black rules, no colour — and a tuned variant for documents people fill in on screen. He asked
for it to be his default, with the fill-in variant for pages like the brief, which are used
rather than read. ^[owner · session · 2026-11-06]

## Decision

- `brain/lenses/house.md` is rewritten around his style: section 1 for every page, section 2
  for pages that are used (fill means "write here", dashed means "my guess", answered goes
  white with an ink edge, sticky bands and top bar, red only for needed and empty), section 3
  for printed documents.
- The brief page is rebuilt in the section 2 style. Its replies keep the same pasted format,
  so `/brief` step 8 is unchanged. The side navigation became a contents block at the top
  plus sticky section bands, which is how the specimen navigates.
- Geist loads from Google Fonts, as Inter did, so no font file ships with the template.
- His identity details (company line, tax number) stay out of the template.

## Consequences

`feed.html`, the spreads, the desk, the review page and the playground canvas still use the
old Inter styling until each is converted. Until then they disagree with the lens.
