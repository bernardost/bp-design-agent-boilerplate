---
tags: [integrations, onboarding, brain-structure]
---
# [[sources-are-declared-in-one-file]] — External sources are declared in one file and land as dated briefings
Date: 2026-08-26 · Status: accepted

## Context

The owner wants the assistant watching the project's real surfaces: *"who are the
stakeholders, Slack channels to keep track of, so that the agent can produce briefings and
keep track of fathom, granola, email, calendar and slack activity. Linear is also a thing.
User might want Notion for some reason."*

Two problems. Connections are per-user, not per-repo — the template can ship the *list* of
what to check, never the credentials — and pulled content is other people's words, which the
existing rule governs: *label evidence, never launder it.*

## Decision

- **`brain/sources.md` declares what to watch**: one line per source, its kind
  (slack · fathom · granola · gmail · calendar · linear · notion), its identifier, why it
  matters, and its state — `connected`, or `wanted` when the source is real but the
  connector is not reachable from this machine. `/setup` writes it by asking, then probing
  what is actually available.
- **`/briefing` reads those sources and writes `brain/briefings/YYYY-MM-DD.md`**, then
  routes decisions, insights, tasks, and questions out of it exactly as `/braindump` does.
  The briefing file is the dated record; it is never the owner of anything.
- **Every pulled line carries who said it, where, and when**, with a link where one exists.
  A summary with no attribution is laundering and is not written.
- `brain/briefings/` holds third-party words, so it falls under the confidentiality rule in
  [[a-private-remote-and-push-as-you-go]]: if the project's material is confidential
  and the remote is not private, briefings are gitignored.

## Consequences

- A source the owner cares about but cannot reach is visible as `wanted` rather than
  silently absent — which is also the list to fix when connectors change.
- `/briefing` is the largest new capability and the most likely to invent. It is scoped to a
  stage of its own, after clone-ready.
