---
tags: [terminology]
---
# [[say-decision-not-adr]] — Say "decision", not "ADR"
Date: 2026-08-26 · Status: accepted

## Context

The workspace called its decision log "ADRs" (architecture decision records) — inherited
from software practice. The owner is a designer working with designers and clients: *"that's
developer lingo, isn't it. Tracking decisions, yes, tagging stuff, yes, but the ADR thing I
fail to see the benefit of the nomenclature."* (owner, 2026-08-26 braindump.)

## Decision

Drop the acronym everywhere in prose, skills, and script output. Keep everything the
acronym was attached to: `brain/decisions/`, the `NNNN-kebab-title.md` numbering, the
Context / Decision / Consequences shape, `/decide`, the supersession-plus-tombstone rule.

The shape stays because `feed.py` parses `## Decision` and a stage bar's numbered
conditions, and `doctor.py` parses `Status:` — the structure is load-bearing, the name was
not. `0000-adr-template.md` is renamed `0000-decision-template.md`.

## Consequences

- Terminology cost is one rename; nothing about the record changes.
- "decision [[wrap-up-is-the-assistants-call]]" is now the citation form. The restate-the-content rule still applies:
  cite the substance, not the number.
