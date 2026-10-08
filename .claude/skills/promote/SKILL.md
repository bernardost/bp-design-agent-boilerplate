---
name: promote
description: Take a playground piece the owner has called final out of the playground — log the decision, freeze the version, write what it takes to implement it, and once it ships, keep an HTML counterpart of what went live. Use for /promote, "this is final", "ship it", "promote this", "it's done, what's next", or whenever a design is about to be built for real somewhere else.
---

# Promote — a piece leaves the playground

A piece is finished when the owner says so, and that sentence sets off four things that are
easy to skip in the moment: the record that says which version won and with which settings,
the file freeze that keeps it from drifting, the notes an implementer needs, and — later —
the HTML counterpart of what actually shipped. This command does them in that order.

## 1 · Pin down what "final" means

Ask only what the conversation has not settled, in one message:

- **Which version**, if the piece has more than one and the owner has not named it.
- **Which settings**, if he tuned it: *Copy settings* in the panel, pasted back. Those values
  become the defaults.
- **Where it is going**: a product repo, a Figma file, a site, a deck. This decides what the
  implementation notes look like.

In a multi-project workspace, name the project in the question.

## 2 · Freeze it, and write the decision

- Bake the settings into the final version's defaults if they are not already, and make that
  the last edit the file ever gets.
- Write `brain/decisions/YYYY-MM-DD-<slug>.md`: what was picked, the version file, the settings
  as JSON, why, what it costs, with `[[links]]` to the exploration it came from and the piece's
  `piece.md`. Same `project:` key as the piece.
- In `piece.md`: `status: final`, `Final: vNN`, `Decision: [[slug]]`.
- `python3 brain/playground.py`, commit, push. Say the decision was logged.

`doctor.py` reports a final piece with no decision, so the order is not optional.

## 3 · Write what it takes to implement it

Into `piece.md` under a `## Implementation` heading, and in the reply. The variable list is
the spec, so most of this is already in the file; the job is to say it in the implementer's
terms:

- **Tokens.** Every custom property with its final value, mapped onto the destination's
  tokens where they exist and named as new where they do not. A value the destination has no
  token for is a decision the implementer will otherwise make alone.
- **Breakpoints.** Which widths, and what changes at each. If the piece was built on a canvas,
  each `@container screen` rule becomes a `@media` rule at the same width.
- **States.** Each preset, what triggers it, and what the copy says. Empty, error and loading
  are the ones that get built last and wrong.
- **Motion.** The chosen kind, duration, ease and stagger, and what happens under
  `prefers-reduced-motion`. `/motion` holds the project's vocabulary if there is one.
- **Assets.** Which brand assets the design uses and where the real files are
  (`brain/brand/`, `source:` declared). A redrawn mark never leaves the playground.
- **Accessibility.** Contrast at the final colours, focus order, what the screen reader says
  for anything that is only visual.
- **What the destination's own rules add.** If it is a product repo under `projects/`, its
  docs govern the code: read them, and say which of its conventions the design has to meet
  before a line is written there. The charter's *Product repos* section applies, and nothing
  is pushed there without asking.

Then stop. Building it in the destination is the destination's work, under its rules — in
Figma through the Figma tools, in a product repo in its own session or worktree.

## 4 · When it has shipped

The owner says it is live, merged, or published. Then:

- **`shipped.html`** in the piece folder: the HTML counterpart of what actually went live.
  Start from the final version and bring it to what shipped — the implementer will have
  changed things, and this file is where those changes are recorded in the design's own
  terms. A comment at the top of the file lists every deviation from the final version and
  why it happened. Keep the controls that still apply; drop the ones that no longer do.
- In `piece.md`: `status: shipped`, `Shipped: <where> · <date>` — a URL, a commit, a Figma
  link, with who confirmed it.
- Log an insight if the implementation taught something that will happen again.
- `python3 brain/playground.py`, commit, push.

`doctor.py` reports a shipped piece with no `shipped.html`. The counterpart matters because
the next round of changes starts from what exists, not from what was intended — and
without it the next session redesigns from the final version and discovers the gap in
review.

## Guardrails

- **"Final" is the owner's word.** A critique score, a plateau, or the agent's own sense that
  the work is done does not change the status.
- **Do not strip the chrome from the final version.** It stays a playground piece. What goes
  to a client is a deck or the shipped thing.
- **Do not promote a piece whose brand assets are placeholders.** Text standing in for a
  wordmark is honest in the playground and a defect in the product. Get the asset first.
- **One decision per piece per promotion.** A piece promoted twice gets a second decision
  that supersedes the first, tombstone and all.
