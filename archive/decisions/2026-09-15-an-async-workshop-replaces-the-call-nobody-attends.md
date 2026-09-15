---
tags: [process, brief, research]
---
# [[an-async-workshop-replaces-the-call-nobody-attends]] — An async workshop replaces the call nobody attends
Date: 2026-09-15 · Status: accepted

## Context

On a live engagement the decision-maker missed the discovery workshop, never sent the document
he had promised, and was not going to read a list of questions. A FigJam board had been
prepared for a call that did not happen. The team rebuilt it as something he could answer
alone, on his phone, in pieces, over a day — and it worked.

The account lead's steer was the entire method in one sentence: *the more we can make
assumptions and ask them to confirm, the better, as it will require less of their thought.*
The workshop shipped in about half a day, including two revision passes, and the run produced a
written record with attribution on every line — which the call would not have.

The owner brought the whole write-up back to the boilerplate as something worth generalizing.
^[owner · session · 2026-09-15]

## Decision

`/workshop` becomes a command, and `brain/workshops/` becomes the owner of the questions put to
a stakeholder asynchronously and the answers that come back. The charter gains one behavior:
when the work is blocked on a person, propose the async version **once**, as an offer.

Three things carry from the instance and are non-negotiable in the skill:

1. **Every guessable screen arrives with our assumption selected.** The fastest path through is
   agreeing. That is what makes it cheaper for the stakeholder than a call.
2. **`chose` and `let stand` are recorded differently.** Tapping Next with nothing touched
   saves our default flagged as ours. In the record that is inferred, never their words.
   Without the flag, every default they skipped past hardens into a client requirement — which
   is the failure mode this workspace's evidence rule exists to prevent, arriving by a new
   route.
3. **Show, don't ask, and use his words on the cards.** Ranking, a pick-three, a draggable
   2×2 with the peers already plotted, sitemaps as small trees in tabs, a wall of real
   screenshots, sliders seeded where we think they sit. A question he has to picture in his
   head is one he postpones, and the wording on every card comes from the recordings rather
   than from our vocabulary, so he is recognizing a sentence instead of translating one. Plain
   language, one idea per screen, no preamble.
4. **The outline is cut before anything is built**, and the phone run happens before anything
   is sent. Seven of the instance's fixes were invisible in a headless walk at phone width and
   obvious in the owner's hand.

The built workshop is work, so it lives wherever `work_lives` says. Only the outline, the
answers, and the decisions they produce live in the brain.

## Consequences

- A stalled stakeholder is no longer a blocker with no move against it; `brain/tasks.md` gains
  a real alternative to `blocked-on-external`.
- The container for a workshop follows the house style on purpose — white, one sans, hairlines
  — which is the single exception to "the house style never reaches the client", and it exists
  because a mood in the chrome would pre-empt the questions about mood.
- `doctor.py` now resolves `[[links]]` and checks tags inside `brain/workshops/`, so the
  answers file is held to the same record standard as a braindump.
- Answers are routed out like a braindump and the file stays verbatim, which means the
  stakeholder's exact words survive the routing.
