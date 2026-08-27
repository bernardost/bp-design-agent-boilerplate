---
tags: [review, onboarding]
---
# 0005 — The reviewer's lens is a project file, not skill text
Date: 2026-08-26 · Status: accepted

## Context

`/reviewer` is written for the engagement it came from: its priorities are provenance,
laundering, evals, stage discipline. The owner: *"the reviewer skill will probably change
depending on the project, and I'm not sure how we would operationalize that."* Editing the
skill per project means every clone forks it, and the independence rules — the part that
must not be negotiable — get edited by accident along with the priorities.

## Decision

Split invariant from variable.

- **The skill keeps what must never bend:** artifacts-only independence, the `⚖️` tell, no
  benefit of the doubt, point-at-a-run, agreement-is-cheap, the findings format and
  severities, the two-round limit, and `brain/reviews/` as its only write location.
- **`brain/review-lens.md` holds what "good" means on this project** — written by `/setup`,
  editable any time, read by the skill at the start of every pass. Design projects get
  accessibility, brand and token consistency, file hygiene, handoff completeness; a build
  gets provenance and evals.

The skill's priority list becomes: stage discipline and decision-trail consistency first
(structural, always), then the lens (project-specific), then architecture and scope.

## Consequences

- The skill text is identical in every clone, so improvements to it are portable.
- An empty or unwritten lens is a real risk: the reviewer says so in its verdict rather than
  quietly reviewing against nothing.
