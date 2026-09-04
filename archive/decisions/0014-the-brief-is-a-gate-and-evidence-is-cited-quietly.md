---
tags: [brief, process, craft]
---
# 0014 — The brief is a gate, and evidence is cited quietly
Date: 2026-09-04 · Status: accepted

## Context

Running the workspace on a real project, the owner found it configuring itself and then
working, with nothing ever putting a stated understanding of the project in front of him:

> *"I'm using the agent now and it's moving ahead, but it's not writing any briefs or plans to
> keep us grounded. Maybe it's because the project hasn't really started, but it would be nice
> if it at least said 'I read the context and here's the preliminary brief, the unknowns and
> the immediate next steps' as an artifact for me to read."*

"The project hasn't really started" is exactly when the brief is due — it is what has to
happen before the work starts, not a report on work in progress.

`brain/project-brief.md` already existed and `/setup` wrote it, but nothing rendered it,
nothing asked for approval, and no behavior made producing it the next step after context
arrived. So the work advanced on the assistant's private reading of the project, which is the
expensive kind of wrong: it surfaces once a deliverable is aimed at the wrong thing.

He also asked for the citations, and for their restraint: *"discreetly, it should link
statements to sources, parts of the transcripts. But that shouldn't obfuscate the content."*
That names a real tension in this charter. **Label evidence, never launder it** requires every
claim about what a client said to carry who said it and when — and a document that prints that
inline is a document nobody finishes reading.

## Decision

**`/brief` is a gate.** When the first real context lands, the next thing produced is the
brief, not the work: what I understood · what I still do not know · the shape of the work ·
what I would do next. `brain/brief.py` renders `brain/brief.html` from the four files that
already own those things, so the page cannot disagree with the brain. Unwritten sections
render as gaps rather than being hidden — seeing the hole is how it gets filled.

Approval is the `Status:` line in `project-brief.md`: `draft`, then
`approved YYYY-MM-DD · [[NNNN-slug]]` naming the decision that recorded the yes. An approved
brief naming no decision is a verbal yes the record does not keep, and `doctor.py` reports it.
**Stage-1 work does not start off a brief nobody has agreed to.**

**Citations resolve the tension by rendering, not by compromise.** One inline form in any brain
file — `^[who · where · when](link)`, the link going to the moment rather than the tool — which
`feed.py` renders as a faint superscript numeral: hover for the attribution, click for the
timestamped recording, full list at the foot of the page. `^[inferred]` is mandatory for
anything worked out rather than heard and renders as its own word in ochre. The requirement
stays absolute and costs the reader nothing, which is the only way a requirement like that
survives contact with a document someone has to read.

`brain/sources.md` owns the format. `brief.publish` in `workspace.toml` is settled once, like
`git.remote`, because publishing sends what the brief quotes to an external service.

## Consequences

- Rendering citations in `feed.py` means every page gets them, not just the brief.
- `doctor.py` can now count sections carrying no attribution, which turns a judgment rule into
  a number. That is the second rule in this workspace to become countable rather than merely
  written down.
- The brief holds stable facts only. It is not re-run weekly; `now.md` owns everything volatile.
- Ordered lists had to be added to the shared markdown renderer — a brief's Deliverables
  section was collapsing into a paragraph, which is how the gap was found.
- A clone that runs `/setup` and stops has a tidy brain and no shared understanding of what it
  is for, so `/setup` now hands off to `/brief` when any context exists.
