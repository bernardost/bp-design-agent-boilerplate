# Lens · record

*Is the project's record honest? The default lens: `/reviewer` with no lens named runs this
one. Ships filled in — unlike `craft.md`, this standard is the same on every project, because
it judges the brain rather than the work. Extend it, don't replace it.*

## 1 · What to look at

The brain as it stands, and the artifacts it makes claims about. Read widely — this lens
*needs* the surrounding context, which is what separates it from `craft`.

Orientation, every pass: `brain/now.md` → `brain/plan.md` → `brain/tasks.md` (know which
stage the work claims to sit in, and what that stage's exit bar is) → the decisions the work
touches or should touch → then the artifacts, fresh.

## 2 · What to refuse to look at

The builder's conversation, transcript, or summary of its own work. If the owner offers
context about what the builder "meant", note it and review the files as they stand.

## 3 · What it is judged on

1. **Stage discipline.** *Running ahead* — artifacts that presuppose a stage not yet exited.
   *Never leaving* — instrumentation or polish beyond the exit bar. Read the bar's decision
   before endorsing or condemning any new check or fixture. A stage entered with no bar
   decision written is itself a finding.
2. **Decision-trail consistency.** Does the work follow the logged decisions? Flag
   contradictions with any accepted decision, current-state files citing tombstoned material,
   and significant choices with no logged decision — name the decision that should exist, do
   not write it.
3. **Provenance.** Claims about what a client or stakeholder said carry who-said-it-and-when,
   or are marked `inferred`. **Laundering** — an inference hardening into a fact as it moves
   between files — is blocking, always.
4. **Claim-versus-page.** Do `now.md`, READMEs, and status claims match what the files
   actually do? A fluent summary of work not yet done is a known failure mode: verify counts
   and capabilities by re-running or re-reading, never by trusting the summary.
5. **One owner.** Is anything restated where it should be linked? A second copy of a fact is
   a second thing to update, and the one that rots is never the one you are reading.
6. **Structure and scope.** The simplest structure that satisfies the logged decisions.
   Ceremony that has not shown it pays for itself is a finding, not a virtue.

Point at a run, not an impression: `python3 brain/doctor.py`, the tests, the tool over a
fixture. A finding backed by a run outranks one backed by a read.

## 4 · What is explicitly not the standard here

- **Visual quality.** Not this lens. `craft.md` owns it, and mixing them produces a pass that
  is rigorous about neither.
- **Cosmetic nitpicks** that do not affect correctness, the record, or maintainability.
- **Prose style** in the brain's own files, unless it makes a claim ambiguous.
