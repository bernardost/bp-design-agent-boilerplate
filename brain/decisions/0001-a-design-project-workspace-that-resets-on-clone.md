---
tags: [template-shape, onboarding]
---
# 0001 — A design-project workspace that resets on clone
Date: 2026-08-26 · Status: accepted

## Context

This repo was extracted from a heavy agent-building engagement. It is now being repointed:
it is the blank workspace its owner clones at the start of every **design** project, with an
assistant (Claude Code preferred, Codex or Cursor acceptable) as the disciplined collaborator.

That creates a recursion. The template's own brain — this decision included — is a record of
building the template. A clone's brain must be a record of the clone's project. If the two
share a directory, every new project starts polluted with the template's history, and the
owner's first act is deleting files.

## Decision

The template is developed **in its own brain, dogfooding every rule**, and `/setup` blanks
that brain on a fresh clone: `brain/braindumps/`, `brain/decisions/`, `brain/insights/`,
`brain/reviews/` are emptied (READMEs and `0000-decision-template.md` survive), and the
current-state files are rewritten from the quiz answers.

Rejected: keeping the template's records on a branch (invisible, and the owner would never
see the method working); and not dogfooding at all (the rules are only trustworthy if the
repo that ships them obeys them).

The product here is **the workspace itself**. There is no separate build directory.

## Consequences

- Every rule in the charter is tested against real use before a clone inherits it.
- `/setup` is destructive by design, so it confirms before it wipes, and it refuses to run
  a second time without `--reset` (see [[0003-setup-is-a-skill-and-one-config-file]]).
- The template's decisions are the design rationale a future maintainer needs, and they are
  lost to each clone. That is correct: they are not that project's decisions.
