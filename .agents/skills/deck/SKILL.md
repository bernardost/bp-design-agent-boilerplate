---
name: deck
description: Build a deck or a client document that reads like an agency made it — titles that carry the whole argument, plain English, a held grid, ideas drawn rather than bulleted, and every page looked at before it is called done. Use for /deck, "make me a deck", "put together a strategy presentation", or whenever a deliverable is going to a client as slides or as a document.
---

# Deck — titles first, then the grid, then look at it

A deck made by an agent fails the same four ways every time: too many words in a register
nobody speaks, sentences explaining what the reader can already see, lists where a picture was
needed, and nobody ever looked at the rendered pages. This fixes them in that order, because
the first one determines everything after it.

`brain/lenses/deck.md` is the standard. Read it before you start; this is the process for
meeting it.

## 1 · Ask the two questions, before anything exists

Both change what gets made, and neither can be guessed. One `AskUserQuestion`, two questions,
up front:

**Is it presented or standalone?** Presented means somebody is talking over it, so each page
carries the minimum that survives without their voice — a title, one supporting line or a
short list, one image or diagram. Standalone means it is read alone and has to carry itself,
so body copy is allowed: a short paragraph, in a narrow measure, placed deliberately. Building
for the wrong one is wrong whatever the layout.

**Which title style?** Either **labels only** — *Brand traits* — or **label plus a
conversational title**, which is the default and the one that makes a deck skimmable:

```
Brand traits
Six key concepts describe the brand's personality
```

Take the brand or visual direction from the project if one is settled — `brain/decisions/`,
the brand files, the chosen exploration. If none is, say so in one line and propose using the
client's existing brand rather than inventing a look inside a deck.

## 2 · Write every title first, and get them approved

**The titles are the deck.** Before a single page is built, write the full sequence — overtitle
and title for every page, in order, as a plain list — and hand it over.

Then read it yourself, titles only, start to finish, and ask whether a stranger would now know
the argument. If there is a gap, the deck has a gap; no layout will cover it.

This is also the cheapest possible round of feedback. Restructuring a list of eighteen lines
costs a minute; restructuring eighteen built pages costs the afternoon.

**Write real sentences.** A title has a subject and a verb and asserts something:

> Brand traits · **Six key concepts describe the brand's personality**
> Next steps · **We'll focus on Wednesday's deadline and scaffold the main deliverable in parallel**

**Not fragments, and not aphorisms.** The pull toward compression and rhythm is strong and it
produces lines that sound authored and say nothing:

> ~~Say what it is. Date it. Stop.~~
> ~~One route, held by a line~~
> ~~A wall is a rope: it holds~~

If you cannot say the title out loud to a colleague without them asking what you mean, it is
one of these. Rewrite it as the sentence you would have said instead.

## 3 · Decide what gets drawn

Go through the approved titles and mark every page whose content is a **relationship, a
process, a comparison, a structure or a quantity**. Those are drawn, not bulleted — and they
are the pages a generated deck reliably turns into three bullets, because text is cheaper than
geometry.

Say which pages you are drawing and what the drawing shows, before building. A deck where
every page is a title and a list is the failure this step exists to prevent, and it is
invisible until you see the pages side by side.

Diagrams are built from real geometry: a labelled grid, a sequence with actual proportion, two
columns of specimens, a do/don't pair, a quantity at the size it really is. Not three rounded
boxes with arrows, not an icon on top of every item.

## 4 · Build on a frame you define once

Set the page frame before page one and never vary it: the hairline edge rule, the section
number in the first column, the overtitle at the top of the second, the mark and page number
in fixed corners. Twelve columns, a narrow left band for words and a wide right band for the
thing being shown.

Body copy small, short measure, starting at the same grid row on every page. Statement pages
set the sentence large, flush left, tight leading, ragged right. Flat colour, full bleed, no
shadows. Images bleed to the edge or sit exactly on column edges.

The rest of the grammar, and the reasons, are in `brain/lenses/deck.md` § 3.

## 5 · Look at it — this is not optional and it is the step that gets skipped

**Render every page and look at every screenshot before you say a word about being done.** Not
the first page. Not a sample. Every one.

The build is HTML, so screenshot it the way the rest of this workspace does — a headless
browser over the rendered file, one image per page, then read them.

What you are looking for, and you will find at least one of each on a first build:

- text overflowing its box, or colliding with the frame
- a page where the frame drifted — the rule, the number or the mark in a different place
- the same layout four pages in a row, which means step 3 was skipped
- a title that reads fine in the outline and is three lines long at this size
- an image at the wrong aspect, or floating in a box with equal margins all round
- a page that is empty in the wrong way, as opposed to the right way

Fix, re-render, look again. Then run `/critique` against `brain/lenses/deck.md` for a
fresh-context read, and loop until it holds up.

**A deck nobody looked at is a draft, whatever its state.** Saying it is done without the
screenshots is the one failure in this skill that is always your fault, and the deck lens caps
the score at 5 for it.

## 6 · Hand it over

Say where it is, which of the two modes it was built for, and what you would change with more
time. If any page is carrying a claim that came from outside the repo, it carries its source
the way `brain/sources.md` specifies.

## Guardrails

- **The client's brand, not the workspace's.** The house style in `AGENTS.md` is for pages the
  owner reads. A client deck follows the client's brand or the direction this project chose.
  Brand assets are extracted or supplied, never redrawn — the charter's rule is absolute and a
  deck is exactly where a redrawn wordmark gets shipped.
- **Do not write the deck in the charter's voice.** `AGENTS.md` is tight and aphoristic
  because it is a rulebook for an agent. That register is the source of the bad titles above.
- **Do not pad to a page count.** If the argument is nine pages, the deck is nine pages.
- **Ask before departing from the lens**, rather than splitting the difference.
