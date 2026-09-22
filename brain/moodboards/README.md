# `moodboards/` — ideas, and the visions they build

`YYYY-MM-DD-<topic>.md`, written by `/moodboard`. This directory owns **the ideas the research
adds up to, and the wholes they assemble into**, and nothing else in the brain holds either.

## The two layers, and the thing between them

**An idea is an atom.** One title, one sentence, enough to sell it — *"evidence carries a
date: every figure has an as-of, and a number without one does not appear."* Something a
reasonable person could disagree with.

**A vision is an assembly.** A whole brand made of a named set of those ideas, with a thesis,
a story, the tension it has to survive, and what it asks of the client before it can be built.

**The interesting layer is between them: the same idea appears in several visions.** That is
the argument — which ideas are load-bearing whichever way the work goes, and which ones only
one vision needs. On a page that relationship is invisible, so `board.py` draws it as wires
and lets you light them from either end. An idea in every vision is a **constant**: the brand
however this lands, and the first thing a guidelines document gets built from. It is derived,
never authored, because a constant claimed by hand is one that a vision quietly dropped.

## What this is not, and what it keeps turning into

**Left unsupervised, an agent asked for a moodboard produces a style guide.** Swatches with
hex values, a type scale, three sections named Colour, Typography and Imagery, a rule about
the logo. That artifact is competent and worthless here: it specifies a design nobody chose,
from research nobody read, at the stage where the question is still what the work is *about*.
It is also the most probable thing to produce, which is why this directory has rules.

**A style guide says what the design is. A moodboard argues what it could mean.** The lenses
below look like a style guide's table of contents and are not: they are the **index** of the
desk, not its argument. The argument is the visions. An idea is filed under Layout the way a
book is filed under a shelf mark — you find it there, you do not read the shelf.

## The rules

- **The unit is an idea, and an idea is arguable.** If nobody could disagree with it, it is a
  description, and it is taking a card the board needed.
- **One title and one sentence sell it.** The desk is read at a glance first, zoomed out. An
  idea that needs its paragraph to make sense has failed its own test; the paragraph is for
  the person who opens it.
- **Every idea belongs to at least one vision.** An idea in none is either the start of a
  vision nobody wrote or it is filler — `board.py` marks it on the card and `doctor.py` says
  so.
- **Nothing is invented.** Every plate is a file that exists in this workspace. Every quote is
  verbatim and every claim about what someone said carries `^[who · where · when]`
  (`brain/sources.md`); anything worked out rather than heard is marked `^[inferred]`.
- **No specification.** No hex values, no type scales, no ratios, no rules about the mark. A
  lens line says what an idea *does* to layout or to type — *"tabular numerals, always"* is
  intention; *"Inter 16/24, 1.25 scale"* is the next stage's work being done early.
- **Every vision carries its tension.** The thing it needs that may not exist, the way it can
  be read wrong, the reason it might be the wrong answer. A vision with no tension has not
  been thought about, and it is the one that quietly wins on presentation.
- **It decides nothing.** A desk is upstream of `/explore` and of any decision. Nothing in the
  brain may cite a vision as chosen. Picking one produces exactly one decision file that links
  back here.

## Plates

A plate is material off the desk: **an image that already exists in this workspace.** Nothing
else — you cannot invent one, which is what keeps every idea tethered to something a person
actually chose or said.

Images come from `brain/references/` or `context/`, written as a path from the repo root.
`python3 brain/board.py` links them relatively so the page works opened straight off disk, and
renders a path that does not resolve as a visible gap. A silently missing plate is a desk that
lies about its evidence.

**Caption what to take from it, never what it is.** *"the way the grid breaks on the third
column"* is a caption; *"Pentagram poster"* is a filename. A third field, a URL, makes the
caption a link back to the source.

## The file shape

```markdown
---
tags: [concept, brand]
project: <key>           # or `all`; omit entirely in a one-project workspace
---
# Ideas, and the visions they build
Subtitle: <the line under the title in the bar — what this desk is, and its date>

## Brief
<one or two paragraphs: what this surface is and how to read it>

Fixed: <a constraint nothing on this desk may break> ^[who · where · when]
Decided: <something already settled, with the decision it came from> ^[[the-slug]]
Rule: <a thing that must never happen> ^[who · where · when]

## Lenses
- Layout — how the page is built, and how a reader moves through it.
- Imagery — what is photographed, and how every photograph is treated.
- Type — which faces, and how hierarchy is carried.
- Voice — what the work says about itself, and where it stands.
- Palette — ground, ink, and the rule for colour.

## Open
- The ground — <what is undecided, and by when> — <who closes it>

## Ideas
### The index is the front door
Lens: Layout
Visions: The Record, The Nameplate
Line: The landing page is a table of contents set large, and nothing else.
Layout: An index landing, then files. Numbered only if there are more than four.
Type: The index is the largest type on the site; nothing competes with it.
Plate: brain/references/density-cravath.png — the homepage leads with a dated deal — https://…
<the detail: how it works, and why the material supports it. Two or three short paragraphs.>

## Visions
### The Record
Mark: R
Thesis: <one sentence — the whole vision>
Layout: <what this vision does to that lens>
Voice: <…one line per lens it answers>
Tension: <what it needs that may not exist, or the way it can be read wrong>
Asks: <what the client has to give us before it can be built>
Plate: brain/references/inspo-cravath.png — Cravath — https://www.cravath.com/
<the story: two or three paragraphs on what this vision is and where it comes from>

```specimen
<self-contained HTML and CSS — one representative composition, composed for 16:9>
```
```

A vision's specimen is optional here and is what `/explore` adds: the desk argues, and a
specimen proves the argument can be executed. A desk with no specimens is a finished
moodboard, not an unfinished one.

`python3 brain/board.py` renders the file to a page beside it. Layout is computed in the
browser because a card's height is its text's height. The page is a projection like every
other one here: delete it and nothing is lost, because this file is the record.
