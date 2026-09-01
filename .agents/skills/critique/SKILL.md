---
name: critique
description: Score a design against brain/lenses/craft.md using a fresh-context critic that sees only the rendered artifact, and loop until it scores 9/10. Writes nothing to the brain. Use for /critique, "how does this look", "is this any good", or as the inner loop while building a visual artifact.
---

# Critique — the fast loop

A design critic that sees **only the picture**. You run it during a build, as many times as
the work needs, and it costs the brain nothing: this skill writes no decision, no insight, no
review file, no task. It exists to raise the quality of the artifact before anyone else looks
at it.

## The one rule that makes it work

**The critic must never see the code, the conversation, or your reasoning.** You cannot
critique work whose intent you already know — you fill the gaps with what you meant instead
of seeing what is there. That is not a discipline problem you can solve by trying harder; it
is why the critic runs in a fresh context with a screenshot and nothing else.

If you find yourself explaining the design to the critic, stop. The explanation is the defect
the critic was there to find.

## Why this is allowed to spawn a subagent

The charter says not to spawn subagents or add verification passes unless asked. Invoking
`/critique` **is** the ask, and it is scoped to this loop. A default session still spawns
nothing on its own, and this skill never fires ambiently.

## The loop

1. **Render.** Screenshot the artifact — the running page, the exported frame, the printed
   view. Capture the states that matter, not one hero shot: default, hover, empty, error,
   narrow. A critic shown only the best frame scores only the best frame.
2. **Spawn the critic.** Fresh context. Hand it *only*: the image(s), the contents of
   `brain/lenses/craft.md`, and anything in `brain/references/`. Use a capable model — this
   is a judgment call, not a mechanical one, and the critic is a small share of the tokens
   because it reads pictures and writes paragraphs.
3. **Ask it for four things**, and reject a reply missing any:
   - what aesthetic the work is reaching for, in its own reading — **not what you told it**
   - how a studio at the top of its field would execute that intent
   - the biggest gaps, specific and ranked, at both composition and detail scale
   - **at least one thing to delete**, or an explicit statement that the work is already tight
   - a score, `n/10`, against the anchors in the lens
4. **Fix the top gaps.** Not all of them — the top ones. Fixing a long list at once makes the
   next score unattributable.
5. **Re-render and re-score in a *new* fresh context.** A critic that saw the last round
   defends its last score and negotiates with you instead of judging.
6. **Stop at 9**, or when the owner says stop. Below 9, keep going.

## Guardrails, each of which was a way this loop fails

- **Cap it.** Five rounds, then report where it plateaued and what the remaining gaps are.
  A loop with no cap will keep finding notes forever, because there are always more notes.
- **Watch for a plateau.** Two rounds at the same score with different reasons means the
  critic is wandering, not converging. Say so and hand the judgment to the owner rather than
  spending a third round.
- **Never soften the lens to reach 9.** If the score will not move, the honest report is
  *"plateaued at 7, here is what is blocking it"*. A 9 obtained by lowering the bar is worse
  than a 7, because it ends the loop.
- **The score is not a finding.** A round that returns a number and no specifics is a failed
  round; ask again.
- **Do not log the rounds.** Intermediate scores are noise in a week. If the loop produced a
  durable realization — a pattern that keeps recurring, a standard worth adding — that is an
  insight or an edit to `brain/lenses/craft.md`, and it goes there deliberately, once.

## What this is not

`/reviewer craft` is the slow, deliberate pass: owner-invoked, writes findings to
`brain/reviews/`, two rounds, and its independence comes from never having been the builder.
This is the fast loop you run on yourself while the work is still moving. Both read
`brain/lenses/craft.md`, which is what keeps them from drifting into two different standards.

Reaching 9 here does not substitute for a review. It means the work is worth someone's time.
