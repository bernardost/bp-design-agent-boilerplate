# `moodboards/` — ideas connected into a vision

`YYYY-MM-DD-<topic>.md`, written by `/moodboard`. This directory owns **the ideas the
research adds up to**, and nothing else in the brain holds that.

## What this is, and the thing it keeps turning into

A moodboard documents ideas and articulates them into a vision for the brand. Material
already in the workspace — the client's own words, the references, the briefing, the
braindumps — gets grouped into ideas, and the ideas get grouped into narratives that say
how they fit together and why they fit this brand. Layout, imagery, type, tone of voice,
palette: the board says how they could come together into something new.

**Left unsupervised, an agent asked for a moodboard produces a style guide.** Swatches with
hex values, a type scale, a rule about the logo's clearspace, three sections named Colour,
Typography and Imagery. That artifact is competent and worthless here: it specifies a design
nobody has agreed to, from research nobody has read, at a stage where the question is still
what the work is *about*. It is also the most probable thing to produce, which is exactly why
it needs a directory with rules.

The difference in one line: **a style guide says what the design is; a moodboard argues what
it could mean.** A board whose sections are Colour / Type / Imagery has been organized by the
designer's toolbox instead of by the argument, and is the failure wearing a nicer layout.

## The rules

- **The unit is an idea, not a category.** An idea is something a reasonable person could
  disagree with — *"the work should feel like it was made by hand, and slowly"* — carried by
  one title and one sentence. If nobody could argue with it, it is a description, not an idea,
  and it fills space the board needed.
- **One title and one sentence sell it; the detail is underneath.** The board is read at a
  glance first. Every idea must survive that glance on its title and its line alone, and only
  then reward someone who reads the paragraphs.
- **Ideas connect, or they are a list.** `Connects:` names other ideas on the board by title,
  and a board where nothing connects to anything is research that was sorted rather than
  thought about. The narratives are where the story lives; the connections are what make it
  one story and not four.
- **Nothing is invented.** Every plate is a file that exists in this workspace, every quote is
  verbatim with its attribution in the inline `^[who · where · when]` form
  (`brain/sources.md`), and anything you worked out rather than heard is marked `^[inferred]`.
  A board that describes an image nobody has is a board that cannot be checked.
- **No specification.** No hex tables, no type scales, no ratios, no rules about the mark. If
  a passage could be pasted into a brand manual unchanged, cut it. Saying *how* an idea shows
  up in type or colour is the job; naming the typeface and the value is the next stage's.
- **It decides nothing.** A board is upstream of `/explore`, which is upstream of a decision.
  Nothing in the brain may cite an idea as chosen. When a board sends the work somewhere, that
  is an exploration or a decision, and it links back here.
- **Rejected ideas stay**, marked `Cut:` with the reason. The same argument as
  `explorations/`: an idea that was wrong for this project may be right for the next one.

## Plates

A plate is a piece of material off the desk: **an image already in the workspace, or a
verbatim quote from the research.** Nothing else. That constraint is what stops the board
drifting into specification — you cannot invent a plate, so every idea stays tethered to
something a person actually said or an image somebody actually chose.

Images come from `brain/references/` or `context/`, referenced by path relative to the repo
root. `python3 brain/board.py` copies nothing and resolves nothing: a path that does not exist
renders as a visible gap, because a silently missing plate is a board that lies about its
evidence.

**Caption what to take from it, never what it is.** *"the way the grid breaks on the third
column"* is a caption; *"Pentagram poster"* is a filename.

An idea with no plate at all is allowed and is reported by `doctor.py` — sometimes the idea
arrived before the material. An idea that never gets one was never grounded.

## The file shape

```markdown
---
tags: [concept, brand]
project: <key>           # or `all`; omit entirely in a one-project workspace
---
# YYYY-MM-DD · <what this board is a vision for>
Vision: <one paragraph — what all of it adds up to, in the owner's language where there is any>

## Narrative — <name>
<one line: the story this group tells, and why it belongs to this brand>

### <Idea title>
<one sentence — the whole sell, and it has to be enough>

Plate: brain/references/density-bloomberg.png — the way the grid breaks on the third column
Quote: "we're not a bank, we just keep their money" ^[Joe Nadir · kickoff call · 2026-09-04]
Connects: <Another idea's title>, <A third>
Size: wide            # optional — wide | full; default is derived from the plates

<The detail. How this idea shows up: what the layout has to do, what the imagery is of, what
the type is doing, how it sounds when it speaks, where the colour goes. Prose, two or three
short paragraphs, no specification.>

### <A cut idea>
<its line>
Cut: <why — in the owner's words where there are any>
```

`python3 brain/board.py` renders the file to a page beside it. The page is a projection like
every other one here: delete it and nothing is lost, because this file is the record.
