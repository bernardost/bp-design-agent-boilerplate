# Project brief — Agent Workspace Boilerplate

*Stable facts. Update only when the engagement itself changes. Volatile state lives in
`now.md`.*

## What this is

Bernardo's blank agent workspace, cloned at the start of every design project. An assistant
(Claude Code preferred; Codex or Cursor acceptable) runs the project from this repo as a
disciplined collaborator: it keeps the decision record, holds current state in one screen,
and lints itself. **The workspace is the product** — there is no separate build directory,
and the method is what ships.

Extracted from a heavy agent-building engagement where each rule was earned by a failure,
then repointed: the discipline stays, the software-practice jargon goes.

## Slice one

A fresh clone plus one `/setup` run yields a configured, self-consistent workspace — the bar
is [[0011-clone-ready-the-stage-1-exit-bar]].

## People

- **Bernardo Presser** · owner, designer, the only stakeholder · every decision routes here.
- Future: colleagues who clone the template. They are why the first-run experience has to
  work without him explaining it.

## Comms channels

None external. The record lives entirely in `brain/`. A cloned project declares its own in
`brain/sources.md`.

## Known failure modes to beat

- **Accreted ceremony.** A check or ritual that has not shown it pays for itself. The
  reviewer treats this as a finding.
- **A clone that starts polluted** with the template's own history, so the owner's first act
  is deleting files.
- **Jargon that makes a designer feel this tool isn't theirs.**
- **A charter that drifted** into two copies, one per assistant.
- **A brain that is current on the desk and stale on the phone.**

## Deliverables

1. `AGENTS.md` — the one charter, imported by `CLAUDE.md`.
2. `brain/` — the record structure, its templates, and its two scripts.
3. The skills: `/setup` `/braindump` `/decide` `/status` `/close` `/reviewer`, later
   `/briefing`.
4. `README.md` — what a person reads before cloning.

## Out of scope

Anything project-specific. The template ships structure and habits, never a client's content.
