---
tags: [portability, process]
---
# A product repo lives in `projects/` and runs on its own rules
Date: 2026-10-08 · Status: accepted

## Context

The owner set out to clone the boilerplate as a client workspace and work on the client's own
code repo inside it, under `projects/`. A review by another session found four ways the
template would push to the wrong place or follow the wrong rules:

- `/setup` asked "is there a remote yet?" without checking what `origin` pointed at. A clone
  that skipped README step 1 (`rm -rf .git && git init`) still pointed at the public
  boilerplate, and push-as-you-go would have published the client's brain there.
- Push-as-you-go never said which repo it covered, so a session inside the product repo would
  push client code on the workspace's standing permission.
- Nothing ignored `projects/`, so `git add -A` would commit the product repo as a gitlink
  with no files behind it.
- The charter said nothing about whose rules govern inside a nested repo. Claude Code started
  from the workspace root loads the nested `CLAUDE.md` lazily, never loads a bare `AGENTS.md`,
  and never runs the nested repo's hooks.

Checking the review turned up two more. `template.repo` named the original private repo, which
no other account can see and which stopped receiving commits once the public repo took over,
so `/update` failed in every clone. And `.gitignore` was template-owned, so `/update`
overwrote it wholesale, which would un-ignore the confidential paths `/setup` writes into it.

## Decision

- **A product repo is cloned into `projects/<name>`, which the workspace ignores.** The charter
  gains a *Product repos* section: push-as-you-go covers the workspace only; the product repo's
  own docs govern its code and git; read them before the first edit; run git as `git -C`.
- **`.claude/hooks/guard_push.py` turns any push outside the workspace repo into a question.**
  It compares git common directories, so a workspace worktree still counts as the workspace.
  It asks rather than blocks, because some product repos do allow their agent to push.
- **`doctor.py` fails a clone with a remote pointing at the boilerplate**, and fails a nested
  repo committed as a bare pointer. `/setup` step 4 checks the remote before asking about one.
- **`template.repo` names the public repo.** `upstream.py` redirects a clone that still names
  the former home, and rewrites the line when it next records a version.
- **`.gitignore` and `.claude/settings.json` are merge files, not template-owned.** Both carry
  the project's own lines.

## Consequences

- Clones made before this have to port the *Product repos* section, the `.gitignore` line and
  `.claude/settings.json` by hand: all three are merge files. `/update` lists them.
- A clone whose `template.repo` still names the private repo cannot fetch the new
  `upstream.py` that fixes it. Changing that one line in `workspace.toml` by hand fixes it.
- The hook runs only in Claude Code. In Codex and Cursor the charter sentence is the only guard.
