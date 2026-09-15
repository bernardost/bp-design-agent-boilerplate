# Tasks

*The owner of task state. Files are the truth; the tracker is a projection pushed outward at
session end — never read back as authority.*

This file exists because `now.md` cannot hold a backlog: its rule is *"if it would still be
true in two weeks, it does not belong there,"* and a backlog is exactly that. `now.md` carries
one line and a link here.

## Line format

```
- `status` · Pn · `label` … · PROJ-n — **Title**
      optional note, indented
```

- **status** — `later` `todo` `doing` `blocked` `done`. `blocked` means waiting on someone
  else; if the next move is ours, it is `todo` however unpleasant.
- **Pn** — `P1` urgent · `P2` high · `P3` medium · `P4` low.
- **labels** — the vocabulary is `tasks.labels` in `brain/workspace.toml`. **`bar`** = inside
  the current stage's exit criterion; **`deferred`** = real work that is explicitly *not* a
  prerequisite for the current stage, and must never be presented as one. Grep `` `bar` `` to
  see what is left.
- **project** — not a field on the line. Tasks sit under a `## ` heading naming the project,
  because the line is dense enough and a heading is what you read anyway. `doctor.py` fails a
  task line that sits under no project heading once the engagement runs more than one.
- **last field** — the projection pointer: the tracker key once mirrored, `—` if not yet,
  `skip` if it deliberately never goes to the tracker. With no tracker configured, every line
  is `—` or `skip`.

Grep-friendly on purpose. `python3 brain/doctor.py` checks the shape of every line here.

---

## {{PRODUCT_NAME}}

*(One `##` section per project in `brain/workspace.toml`. Stages are per project too —
`plan.md` owns the arcs, and two strands are rarely at the same stage.)*

### Stage 1 · {{NAME_THE_FIRST_STAGE}}
