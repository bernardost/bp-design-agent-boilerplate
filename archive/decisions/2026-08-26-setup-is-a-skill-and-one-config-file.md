---
tags: [onboarding, template-shape]
---
# [[setup-is-a-skill-and-one-config-file]] — /setup is a skill, and configuration is one file
Date: 2026-08-26 · Status: accepted

## Context

Adoption was a "delete this block when done" paragraph at the top of the charter, which
asked the assistant to hand-edit Python constants in two places: `TRACKER_PREFIX` and
`TASK_LABELS` in `doctor.py`, and `PROJECT_NAME` + `TRACKER_PREFIX` in `feed.py`. Nothing
checked that the two prefixes agreed. A self-deleting block is also unrepeatable: when a
project acquires a Slack channel or a tracker in month two, there is nothing to re-run.

The owner wants first use to be a quiz that shapes the workspace to the project, and to
double as the tour of the available commands.

## Decision

Two changes.

1. **`brain/workspace.toml` is the single configuration file.** `brain/config.py` reads it
   (`tomllib`, with a small fallback parser for Python < 3.11 so a stock macOS `python3`
   still works); `doctor.py` and `feed.py` both import from there and hold no project
   constants of their own. A prefix can no longer disagree with itself.
2. **`/setup` is a re-runnable skill** (`.claude/skills/setup/`), not a block in the
   charter. It interviews, writes the config and the current-state files, blanks the
   inherited brain per [[a-design-project-workspace-that-resets-on-clone]], surveys
   which connectors are actually reachable, ends with the command tour, and can be re-run
   later to add a source or a tracker.

The quiz's answers each have a named destination: project identity and where the work
lives → `project-brief.md` and the config · people and what routes to them →
`project-brief.md` · watched sources → `brain/sources.md`
([[sources-are-declared-in-one-file]]) · tracker and task labels → the config · what
"good" means here → `brain/review-lens.md`
([[the-reviewers-lens-is-a-project-file]]) · the first stage and its bar → `plan.md`
plus a bar decision · confidential material → `context/` and `.gitignore` · the remote →
[[a-private-remote-and-push-as-you-go]].

## Consequences

- Adding an integration later is editing a declared file, not editing code.
- `/setup` is the one skill that may write anywhere, and the only destructive one.
- A stale `workspace.toml` is now a possible failure; `doctor.py` reports unfilled
  placeholders so a half-configured workspace announces itself.
