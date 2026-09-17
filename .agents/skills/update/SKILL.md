---
name: update
description: Take improvements from the boilerplate this workspace was cloned from, without overwriting anything the project wrote. Use for /update, "check the boilerplate for updates", "is there a newer version of the scaffolding", or when the owner mentions changes made upstream.
---

# Update — take the template's improvements, keep the project's work

**You are running inside a project, not inside the boilerplate.** Most of what is here belongs
to the owner: their decisions, their current state, their craft lens, their charter with their
project's identity in it. A little of it is scaffolding that came from the template and gets
better over time. Telling those apart by eye is how the owner's `now.md` ends up as a template
placeholder.

**So do not tell them apart by eye.** `brain/upstream.py` holds the ownership rules in code,
and it is the only thing that decides what may be written.

## 1 · Look

```
python3 brain/upstream.py
```

It shallow-clones the repo named in `template.repo`, compares it against this workspace, and
reports in three groups: **template-owned** (safe to take), **needs you** (the template ships
part of the file and `/setup` filled the rest), and everything it refuses to even compare.

Read the report out loud to the owner in a sentence or two. If nothing changed, say that and
stop — there is no step 2.

## 2 · Take the safe ones

```
python3 brain/upstream.py apply
```

It refuses a dirty tree, so `git diff` is the review and `git checkout .` is the undo. It
writes only template-owned files, records the boilerplate commit in `workspace.toml`, and
leaves the rest alone.

**Never hand-copy a file out of the upstream clone.** That bypasses the one mechanism keeping
the project's work safe. If a file is in the "needs you" group, it is there because a copy
would destroy something.

## 3 · Port the "needs you" files by hand, one at a time

These carry both the template's content and the project's answers — `AGENTS.md` has the
charter plus this project's identity lines; `brain/lenses/craft.md` ships sections 1, 2 and 5
with 3 and 4 written at setup; `brain/tags.md` ships a vocabulary this project extended.

For each: read the upstream version, find what actually changed, and apply *that change* to
the project's file. Keep every project-specific line. When a change conflicts with something
this project decided, **say so and stop** — that is a contradiction to raise, not to resolve
quietly. Check `brain/decisions/` before assuming the upstream version is the better one; the
project may have overridden it deliberately.

## 4 · Verify, then record

```
python3 brain/doctor.py && python3 brain/test_brain.py
```

Both must pass before you commit. Then log a decision in `brain/decisions/` naming which
boilerplate commit was taken and anything deliberately not taken, so the next update knows
what is a conscious divergence rather than a missed change. Commit and push.

## If the owner has local changes to a template-owned file

They lose them, and they should hear that before it happens rather than after. Check with
`git log -- <path>` whether the project has touched it. If it has, treat that file like a
"needs you" one: port the upstream change into their version instead of overwriting, and offer
to add the path to `template.extra_project_paths` in `workspace.toml` so it is never
overwritten again.

## What this command never does

- Write anything under `brain/decisions/`, `insights/`, `explorations/`, `workshops/`,
  `braindumps/`, `briefings/`, `drafts/`, `reviews/`, `references/`, or `context/`.
- Touch `now.md`, `tasks.md`, `plan.md`, `project-brief.md`, `feed-items.md`,
  `open-questions.md`, `glossary.md`, `sources.md`, or `workspace.toml` beyond the one version
  line it stamps.
- Add the boilerplate as a git remote. The project's history stays its own.
