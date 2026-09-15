---
tags: [process, system]
---
# Projects are strands of one engagement
Date: 2026-09-15 · Status: accepted

## Context

The workspace assumed one project per clone. A real engagement does not work that way:

> *"Right now my project is basically one engagement but with several small projects within.
> So I wouldn't want to deal with multiple agents, because on meetings we talk about multiple
> projects at once. It's just that, when talking to the agent, it should be clear what project
> we're discussing and I wouldn't want an agent to mix up brain items from one project to
> another, like decisions for example."* ^[owner · session · 2026-09-15]

The failure had already happened. Two items reached the owner's feed reading like business
from the strand he had open, and were about another one; he answered the wrong project.
Nothing in the record was wrong — every file was correct and none of them said which project
it belonged to, which is the same thing as being wrong at the moment somebody reads it.

Two shapes were possible. One clone per project makes the mixing impossible, and was the
recommendation. The owner rejected it for a concrete reason: a single meeting covers three
strands, and splitting them across clones means running three sessions to record one
conversation. The engagement is the unit the owner actually works in.

## Decision

**One workspace per engagement; every record names the project it belongs to.**

`[projects]` in `brain/workspace.toml` declares the strands — a permanent lowercase-kebab
`key` that records cite, a display `label` that headings use, and `work_lives` per strand.

1. **Compartmentalize in the projection, never in the storage.** Per-project `decisions/`
   folders were the obvious move and are the wrong one: they trade away the one-owner rule
   that makes a decision findable, to buy a filter that render time gives away. The strand is
   a `project:` key in frontmatter (decisions, insights, explorations, workshops), a
   `project:` line on a feed item, and a `## ` heading in `tasks.md`. `now.md` and `plan.md`
   carry one section per project; `feed.html` renders a chip and a filter, and `/status`
   groups by strand.
2. **Braindumps and briefings are exempt.** Both are verbatim captures that legitimately span
   the engagement. Routing assigns the project — to the decision or task that comes out, never
   to the dump.
3. **Each project runs its own arc.** Two strands are rarely at the same stage, so `plan.md`
   holds a section each and the stage check always runs against the bar of the strand in
   front of you. There is no engagement-wide stage.
4. **`doctor.py` fails an untagged or mis-keyed record — but only above one project.** A
   single-project workspace pays nothing: nothing is tagged, nothing is filtered, and no check
   asks for any of it. The ceremony arrives with the second key and not before.
5. **The agent says which project, and never guesses which one.** Every question to the owner
   carries its strand; a record whose strand is unclear gets a one-line question rather than a
   plausible guess. `all` is a real answer for a record that binds the whole engagement, not
   the safe default for an unsure one.

## Consequences

- The owner stops reading a question against whichever strand he happened to have open.
- One meeting still produces one session, which was the point.
- `[project]` in `workspace.toml` becomes `[engagement]`; the old table name still parses and
  its singular `name` migrates to the workspace's one project key, so existing clones keep
  working without an edit.
- A second project can be added to a live workspace at any time: write the key, then tag what
  already exists. `doctor.py` lists exactly what is missing, so the migration is a checklist
  rather than an audit.
- The cost is a key on every record. It is paid by whoever writes the record, at the moment
  they already know the answer, which is the only moment it is cheap.
