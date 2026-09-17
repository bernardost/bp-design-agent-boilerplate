---
tags: [system, process, portability]
---
# Ownership is code, not a briefing
Date: 2026-09-17 · Status: accepted

## Context

The owner runs this workspace on a real project and reported the friction:

> *"Every time I ask my other agent to check this repo for updates, I have to explain to the
> agent not to override any project customizations and that this is its original
> scaffolding."* ^[owner · session · 2026-09-17]

The cause is in the adoption instructions. Step one of the README is `rm -rf .git && git init`,
which is right — a project's history should start empty and carry none of the template's
commits. But it leaves a clone with no link of any kind to the boilerplate: no remote, no
version, and no record of which files arrived from the template and which the project wrote.

So the ownership map existed only in the owner's head, and he re-read it aloud to an assistant
on every update. That is not a safeguard. A rule enforced by remembering to say it holds until
the first time nobody says it, and the cost of that once is a template placeholder written over
`now.md`, or a craft lens filled at `/setup` replaced by the blank it was filled from.

This is the same argument the workspace already makes about `doctor.py`: the rules that survive
are the ones a program refuses to let you past. Ownership had simply never been written down
where a program could read it.

## Decision

**`brain/upstream.py` holds the ownership rules in code, and `/update` is the only sanctioned
way to take an upstream change.**

1. **Three classes, and an unrecognised file is never OWNED.** `owned` is the template's
   machinery — `brain/*.py`, the skills, the workflow, the format READMEs — overwritten
   wholesale. `project` is the owner's work and current state, which is **not even compared**
   against upstream. `merge` is a file the template ships part of and `/setup` fills the rest
   of: `AGENTS.md`, `craft.md`, `tags.md`. Anything unclassified falls to `merge`, because a
   wrong `merge` costs one question and a wrong `owned` costs somebody's work.
2. **A shallow clone, never a git remote.** Adding the boilerplate as a remote entangles two
   unrelated histories and puts the template's commits in every later `git log`. `/update`
   borrows the files into a temp directory and throws the repo away.
3. **`template.version` in `workspace.toml` records the commit last taken**, written by the
   tool rather than typed, so the next check has a floor and a divergence is visible.
4. **Projects may widen `project`, never `owned`.** `template.extra_project_paths` protects a
   file the template has never heard of. There is deliberately no matching way to widen what
   gets overwritten: that direction is the dangerous one, and it belongs upstream where
   everyone gets the change.
5. **The charter carries the one-line version**, in Gotchas, so an assistant that never loads
   the skill still knows not to hand-copy files in. `doctor.py` prints where the clone stands
   on every run.
6. **A dirty tree is refused**, so `git diff` is the review and `git checkout .` is the undo.

## Consequences

- The owner stops being the manifest. The explanation that used to be repeated every session is
  now a file that travels with the template that makes the claim.
- Five tests pin the classification of every path an owner would care about by name, including
  that `compare()` never so much as reads `now.md` from upstream.
- `brain/decisions/README.md` and the decision blank live inside a project-owned folder and are
  still the template's, so they are checked before the folder pattern. That carve-out is the
  one fiddly part and it has its own test.
- A project that has locally edited a template-owned file will lose that edit. `/update` says
  so before it happens, and offers `extra_project_paths` as the permanent fix.
- The list will drift as the template grows a file nobody classifies. The `merge` fallback makes
  that drift safe rather than silent — an unclassified file shows up asking for a human.
