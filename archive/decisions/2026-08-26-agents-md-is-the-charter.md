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

## Revisited 2026-09-15 — splitting into core plus trigger-loaded playbooks

A review proposed cutting the charter into a short always-on core plus playbooks loaded on
trigger, on the grounds that reading ~30 KB before every request costs latency and context.
The owner declined it. Recorded because the proposal is a reasonable-looking one that will be
made again, and the answer is not obvious from the file.

1. **A slash command degrades outside Claude Code; a trigger does not.** The fallback above
   works because the owner types `/name` and any assistant can then read that file. A
   trigger-loaded playbook has no such event: nothing invokes it, so it depends on the agent
   noticing it should go and fetch a rule. Codex and Cursor have no mechanism for that at all,
   which would make the split quietly reintroduce the per-tool duplication this decision
   exists to prevent.
2. **Recognition is the rule.** The rules most worth having always-on are the ones broken
   without noticing — that a claim came from outside the repo and needs a source tag, that a
   draft is heading for a scratch directory, that the reply never said which project. An agent
   that already knew to load the relevant playbook was not the agent about to break it.
3. **The arithmetic does not support it.** Of 437 lines, the two largest sections — *How to
   talk to the owner* (126) and *Always-on behaviors* (97) — are always-on by definition. What
   is genuinely situational comes to roughly 60 lines, an eighth of the file, bought at the
   price of a loading mechanism and a second place rules can live.
4. **Fourteen internal cross-references** would either dangle or be duplicated, and
   duplication is what this decision bans.

The latency premise was also weak: ~7k tokens read once per session and cached is not what
makes a session slow. What did cut per-turn work was the read-only fast path and pulling only
before a write onto a clean tree, both of which landed the same day without touching the
file's structure. **If the charter feels heavy the answer is to cut it, not to relocate it** —
*How to talk to the owner* has accumulated examples that restate rules stated above them.
