---
tags: [portability, template-shape]
---
# [[agents-md-is-the-charter]] — AGENTS.md is the charter; CLAUDE.md imports it
Date: 2026-08-26 · Status: accepted

## Context

The owner intends the workspace to run under *"Claude, Codex or some model via an IDE like
cursor"*, with Claude Code preferred. The charter lived only in `CLAUDE.md`, which Codex and
Cursor do not read; they look for `AGENTS.md`. Two copies of a charter is two charters, and
the one that drifts is the one nobody edits.

## Decision

`AGENTS.md` holds the charter. `CLAUDE.md` is one line — `@AGENTS.md` — which Claude Code
resolves as an import, so Claude Code users see no difference and there is exactly one
source.

Skills are Claude Code's format (`.claude/skills/<name>/SKILL.md`). Rather than duplicate
them per tool, the charter states the fallback: **when the owner types `/name`, read
`.claude/skills/name/SKILL.md` and follow it.** Any assistant that can read a file can obey
a slash command.

## Consequences

- One charter, three tools.
- Skills degrade rather than break outside Claude Code: no autocomplete, no auto-invocation
  by description, but the instructions still execute.
- `doctor.py`'s current-state list points at `AGENTS.md`.
