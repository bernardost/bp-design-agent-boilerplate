# Now

*2026-08-26 · One screen. If it would still be true in two weeks, it belongs in its owning
file, linked from here. Rewrite this file; never grow it. `python3 brain/doctor.py`*

## Where we are

**Stage 1 · Clone-ready**, against the six conditions in
[[0011-clone-ready-the-stage-1-exit-bar]] — five met or partly met, one not.

Repointed the workspace from the engagement it was extracted from to Bernardo's blank
design-project workspace, in one session from a two-part braindump. Eleven decisions logged
(0001–0011). Terminology is plain ("decision", not ADR). Project constants now live in
`brain/workspace.toml` behind `brain/config.py`; neither script holds one, which also fixed a
tracker-key check that had never fired. `AGENTS.md` is the single charter and `CLAUDE.md`
imports it, so Codex and Cursor read the same file. Tags are global, defined in
`brain/tags.md`, reported by `doctor.py`. `/setup` and `/close` are written; the reviewer now
reads `brain/review-lens.md` instead of carrying project standards in its own text.

Push-as-you-go and the wrap-up signal are charter behavior now — the reasoning is in
[[0006-a-private-remote-and-push-as-you-go]] and
[[0007-wrap-up-is-the-assistants-call]].

## What's next

1. **Run a real clone end to end** — the last unmet bar condition, and the only honest test of
   `/setup`. FEED-1 asks how: a fixture run by me, or your next actual project.
2. Then Stage 2 decides whether the visual feed earns its cost
   ([[0008-the-visual-feed-is-an-experiment-first]]) — deliberately deferred, not forgotten.

## Blockers

None. FEED-1 is waiting on you but nothing stops in the meantime.

*Owners: arc → `plan.md` · decisions → `decisions/` · questions → `open-questions.md` ·
tasks → `tasks.md` · tags → `tags.md` · config → `workspace.toml` · waiting on you →
`feed-items.md` → `feed.html`.*
