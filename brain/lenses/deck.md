# Lens · deck

*Is this deck or document something an agency would hand over? `/reviewer deck <scope>`, and
the standard `/critique` scores a deck against during a build.*

This lens governs **what goes out** — a brand deck, a strategy presentation, a proposal, a
written document for a client. It is not the house style in `AGENTS.md`, which governs pages
generated for the owner to read. The two share a language standard and nothing else.

## 1 · What to look at

**Rendered pages, in order, at the size they will be seen.** A deck reviewed as an outline is
a deck reviewed as prose, and prose is the one thing a deck is not. Screenshot every page.

Then read it twice: **once at the titles only**, then in full. The first pass is the real test
and it is described below.

## 2 · What to refuse to look at

The build, the source, the brief, and the conversation that produced it. A deck is read by
someone who was not in any of those, which is the condition this lens reproduces.

The one permitted input is the audience: **standalone or presented**, which changes how much
text is correct. Get that from the deck's own brief, not from the builder's reasoning.

## 3 · What it is judged on

### The title test, and it comes first

**Read only the overtitles and titles, in order, start to finish. Do you now know the
argument?** If yes, the deck is structurally sound and everything else is refinement. If no,
nothing further matters — fix that before looking at a single layout.

The structure both halves serve:

- **Overtitle** — the label. What section this is. *Brand traits. Next steps. Competitive
  landscape.* Two or three words, no verb, no cleverness.
- **Title** — a complete sentence saying the one idea of the page. *"Six key concepts
  describe the brand's personality."* *"We'll focus on Wednesday's deadline and scaffold the
  main deliverable in parallel."*

A title is a sentence, with a subject and a verb. It is not a fragment, not a label, not a
phrase. A reader skimming only titles should finish with the whole argument, which is only
possible if each one asserts something.

**The failure to watch for is cleverness, and it is the dominant one.** A model writing
titles reaches for compression and rhythm, and produces aphorisms:

> *Say what it is. Date it. Stop.*
> *One route, held by a line.*
> *A wall is a rope: it holds.*

Every one of these is a fragment pretending to be a thought. They sound authored, they survive
a read-through because they scan, and they say nothing a reader can act on. Three-beat
rhythms, a colon doing the work of a verb, a metaphor standing in for the claim, a sentence
that would need the slide to explain it — all the same failure. **The test is whether a
stranger reading the title alone learns the point.** Flag every title that fails it, quote it,
and write the replacement.

### The language

Plain English, and *straightforward* is the whole instruction. Short words. One idea per
sentence. The sentence a competent person would say out loud to a colleague.

- **No meta-commentary.** *"This slide explores…"*, *"The following framework outlines…"*,
  *"As we can see…"*, *"It's worth noting that…"*. The page is in front of the reader and
  somebody is standing next to it. Delete the sentence; it has no content.
- **No throat-clearing before the point**, and no restating the title in the body. If the body
  paragraph is the title again at greater length, cut the paragraph.
- **No words that sound like consulting.** *Leverage, synergy, holistic, robust, seamless,
  best-in-class, unlock, elevate, journey, ecosystem* — where a plain word exists, it wins.
- **Name the actor, active voice.** *"We'll ship the portal on the 14th"*, not *"The portal
  is slated for delivery."*
- **Nothing asserted that the work does not show.** *Powerful, beautiful, simple* are claims
  the page must earn by being those things.

### The amount of text, which the audience decides

- **Presented** — the page carries the minimum that survives without the speaker's voice. One
  title, one supporting line or a short list, one image or diagram. Body paragraphs belong in
  the notes, not on the page.
- **Standalone** — the page has to work with nobody in the room, so body copy is allowed and
  expected: a short paragraph in a narrow measure, placed deliberately. Still never a wall.

A deck built for the wrong one of these is wrong whatever its layout, which is why the
question gets asked before anything is made.

### The layout grammar

Elegant, minimal, strongly gridded — the register of a good brand guideline.

1. **A visible grid, held.** Twelve columns. A narrow left band for the labels and the words,
   a wide right band for the thing being shown. Items snap to column edges, and the same
   element sits at the same coordinate on every page.
2. **A fixed page frame.** A hairline rule at the top or bottom edge, full bleed. The section
   number in the first column. The overtitle at the top of the second. A small mark and the
   page number in fixed corners. **Identical on every page** — the frame is what makes a deck
   read as one object, and it is the first thing a generated deck gets wrong.
3. **Body copy small, in a short measure, at a fixed row.** Around 45 characters, around 14px
   at slide scale, starting at a grid row that repeats page to page. Not vertically centered,
   not filling its column, not growing to meet the image beside it.
4. **Statement pages set the sentence large and flush left.** Tight leading, ragged right, no
   centering. The sentence is the whole page.
5. **Empty space is finished, not unfinished.** A page holding one paragraph and one image is
   a page. The instinct to fill is the instinct to beat.
6. **Flat colour, full bleed.** A field of one colour with text on it. No gradients, no drop
   shadows, no rounded cards with a glow, no stock-photo overlay with a scrim.
7. **Images bleed to the page edge** or sit exactly on column edges. Never floated, never
   centered in a box with equal margins all round.
8. **One sans, few sizes.** Four or five steps across the whole deck, used consistently.

### Diagrams, which are usually missing

**A relationship, a process, a comparison or a structure is drawn, not bulleted.** A model
defaults to a list because a list is text and text is cheap, and the result is a deck where
every page looks the same and nothing is actually shown.

Every pass names at least one page that should be a diagram and is a list — or states plainly
that the deck is already visual, which is the only other acceptable answer.

What a drawn page looks like: a labelled grid, a sequence with real geometry, a comparison
laid out as two columns of specimens, a quantity shown at the size it actually is, a do/don't
pair. What it does not look like: three rounded boxes with arrows between them, an icon on top
of every item, or a shape that decorates without carrying information.

## 4 · What is explicitly not the standard here

- **Sounding like the workspace's own files.** `AGENTS.md`, the skills and these lenses are
  written so that whoever is deciding what to do next understands them. A deck is not
  failing because it does not sound like them, and where they still lapse into epigram, that
  is their bug and not a style to carry into a deliverable.
- **The workspace house style.** White paper, Inter, hairline rules — that governs `feed.html`
  and the pages made for the owner. A client deck follows the client's brand, or the direction
  chosen for the project, and is judged against that.
- Anything the brief has settled: a fixed template, a client's mandated typeface, a required
  section order.

## The score

One number, `n/10`, on how close this sits to what a good agency would hand the client.

| | |
|---|---|
| **1–3** | reads as generated. Fragment titles, meta-commentary, bulleted everything. |
| **4–6** | competent and forgettable. Correct, says nothing, looks like every deck. |
| **7–8** | a clear argument, executed unevenly. Name what is holding it back. |
| **9** | an agency could send it. Remaining notes are preferences, and say so. |
| **10** | reserve it. |

**Two things cap the score at 5 whatever else is true:** titles that fail the title test, and
a deck nobody screenshotted before calling it done. Both are checkable in a minute and both
are the difference between a draft and a deliverable.
