---
tags: [portability, process]
---
# The public boilerplate is a separate repo with rewritten history
Date: 2026-10-02 · Status: accepted

## Context

The owner asked to make the workspace public so a colleague could clone it. A security pass
found a real client's name and email address used as an illustrative example in
`brain/drafts/README.md`, a meeting-recording URL with what looked like a real call ID, the
client's and the studio's initialisms, a colleague's name, and a client Slack channel. The
author email on 23 of 31 commits was the owner's work address.

Scrubbing the working tree was not enough: making a repo public publishes its history, and all
of it was in commits.

A first attempt published the repo after verifying `origin/main` was clean. A fresh clone was
not clean — a stale branch, `bernardost/speed-up-close-command`, still pointed at pre-rewrite
history, and `filter-branch` had rewritten `main` only. The repo was public for about a minute.

## Decision

- Rewrite every commit on `main` to scrub the identifiers, and rewrite the author and committer
  to the owner's GitHub noreply address.
- Publish to a **new** repository, `bernardost/bp-design-agent-boilerplate`, rather than
  force-pushing over the old one. GitHub keeps force-pushed and deleted-branch commits
  fetchable by exact SHA, and those SHAs had been briefly reachable from a public clone.
- Keep the original repo private, with its history intact.

## Consequences

- **Verification means cloning the published repo, not inspecting `origin/main`.** That is the
  only check that would have caught the stale branch, and it is now the step that matters.
- The repo-local git identity is set to the noreply address so new commits do not reintroduce
  the work address.
- The private repo still holds the pre-scrub history. It is the undo, and deleting it is the
  owner's call.
- Examples in the template now use invented people and domains. A real contact in an example
  is a leak waiting for the repo to go public.
