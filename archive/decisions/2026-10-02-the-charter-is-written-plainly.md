---
tags: [process, system, onboarding]
---
# The charter is written plainly, like everything else
Date: 2026-10-02 · Status: accepted

## Context

This session added a rule banning fragments and aphorisms from client decks, and justified
keeping them in `AGENTS.md` on the grounds that a charter is read by an agent rather than a
person. The owner pushed back:

> *"It worries me that you said that this style of language is the right way to document
> guidelines to an agent. You might be right, but the original agent who wrote this repo,
> Claude Opus 5, was famous for its compressed, unintelligible writing. So we might be
> replicating that confusing writing here because the backbone of this repo was written by
> that agent. … Language is our primary way of communicating, and I spend my entire day
> reading what agents write to me. Comprehension is vital."* ^[owner · session · 2026-10-02]

He was right. The justification was a rationalization of an inherited habit.

Two things make it a real problem rather than a matter of taste:

- **An agent copies the style of its instructions more reliably than it follows instructions
  about style.** A charter written in epigrams teaches epigrams, which then reach the owner
  and the client. `AGENTS.md` already said *"use the simplest word that carries the idea"* and
  was itself written in the register it banned.
- **An instruction that has to be decoded gets decoded wrong.** `**Ears.**` was a rule in this
  file for months. It meant *log decisions and insights as they happen*, and nothing about the
  word says so.

An audit also found a defect rather than a style problem: inside the `**Do not:**` list, three
rules were bolded as positive imperatives — *"Make a case for a small ask"*, *"Use the brain's
vocabulary on the owner"*, *"Report what you already handled as news"*. Three bullets below the
heading, the bolded line is the whole instruction a scanning reader receives, and it said the
opposite of the rule.

## Decision

Write the instructions the way we want the agent to write.

- Twelve rule lead-ins rewritten to state the action and make sense alone.
- Every item in a "Do not" list written as a negative.
- A `## How this file is written` section added to `AGENTS.md`, so edits stop reintroducing
  the register. Its rule: **keep one concrete fact per sentence, and stop squeezing rules into
  slogans.**
- The same standard extends to `brain/lenses/`, the skills, and every README in `brain/`.

The owner later caught the same construction three more times in the rewrite itself, including
a heading — *"Write to be understood, not to be admired"* — that was the `not X, it's Y` form
the text forbade four lines below it. Those are fixed. The relapse rate is the point: this is a
default to be checked for, not a habit that gets cured once.

## Consequences

- Density survives and compression goes. One fact per line with the specific failure that
  caused the rule is what makes the file worth reading; cutting the slogans must not add
  hedges or restatement.
- The body prose of `AGENTS.md` was not rewritten, only the rule lead-ins and the sections
  this session touched. A full pass is still available and was deliberately not taken.
- `archive/` keeps its own voice. A dated record is not rewritten to match a later standard.
