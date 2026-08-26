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
- **labels** — see `TASK_LABELS` in `brain/doctor.py` (edit both together). **`bar`** =
  inside the current stage's exit criterion; **`deferred`** = real work that is explicitly
  *not* a prerequisite for the current stage, and must never be presented as one.
  Grep `` `bar` `` to see what is left.
- **last field** — the projection pointer: the tracker key once mirrored, `—` if not yet,
  `skip` if it deliberately never goes to the tracker.

Grep-friendly on purpose. `python3 brain/doctor.py` checks the shape of every line here.

---

## {{PRODUCT_NAME}}

### Stage 1 · {{NAME_THE_FIRST_STAGE}}
