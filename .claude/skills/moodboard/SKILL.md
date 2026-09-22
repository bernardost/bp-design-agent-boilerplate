---
name: moodboard
description: Turn the research already in the workspace into ideas, assemble the ideas into whole visions for the brand, and render the lot as a desk you can move around on — with the wires showing which ideas build which vision. Use for /moodboard, "put a moodboard together", "what does all this research add up to", or whenever the material has piled up and nobody has said what it means.
---

# Moodboard — the desk

A moodboard documents ideas and articulates them into visions for the brand. Everything it is
built from is already in this workspace: the client's own words, the references, the briefing,
the braindumps, the brief. **The job is connection, not production.** You are not designing
anything here and you are not collecting anything new.

## Read this first, because it is the failure

**Asked for a moodboard, a model produces a style guide.** Swatches with hex values, a type
scale, three sections named Colour, Typography and Imagery, a rule about the logo. It happens
every time, it is not a lapse in effort, and it is what predicting the likely next token
returns — "moodboard" sits next to a million brand manuals in the training data and next to
almost nothing that reasons.

The artifact it produces is worse than nothing. It specifies a design nobody chose, from
research nobody read, at the stage where the question is still what the work is *about*. It
looks finished, so it ends the conversation it was supposed to start.

**A style guide says what the design is. A moodboard argues what it could mean.**

## The shape of the thing

Two layers, and the interesting part is between them.

**Ideas** are the atoms. One title, one sentence, enough to sell it. Something a reasonable
person could disagree with. Each is filed under one **lens** — Layout, Imagery, Type, Voice,
Palette — which is the desk's *index*, not its argument.

**Visions** are the assemblies. A whole brand built from a named set of ideas, with a thesis,
a story, the tension it has to survive, and what it asks of the client before it can exist.

**The same idea appears in several visions, and that is the argument.** An idea every vision
shares is a **constant** — the brand whichever way this lands, and the first thing a
guidelines document gets built from. `board.py` derives constants, draws the wires between
the two layers, and lets you light them from either end. Do not claim a constant by hand.

## Where this sits

Research → **`/moodboard`** (what does it all mean, and what wholes could it make) →
`/explore` (specimens that prove a vision can be executed) → a decision. **This command
decides nothing**, and nothing in the brain may cite a vision as chosen.

## The run

**1 · Read the desk.** Before writing a word: `context/`, `brain/references/` (including
`against/`), the newest `brain/briefings/`, the `brain/braindumps/`, `brain/project-brief.md`,
`brain/decisions/`, `brain/open-questions.md`, and `brain/glossary.md` so you decode names
rather than guessing at them. Note what the client said in their own words.

If there is almost nothing there, stop and say so. A desk built from an empty workspace is
built from the model's priors, which is the style guide again wearing a different hat.

**2 · Write the brief card first.** What this surface is, and the constraints everything on it
has to survive: `Fixed:` what cannot change, `Decided:` what is already settled and where that
decision lives, `Rule:` what must never happen. Each carries who said it and when. This is
the part that stops a desk drifting into ideas nobody can use.

**3 · Name the lenses.** Four to six, each with one line on what it covers. They are the
columns. Layout, Imagery, Type, Voice, Palette is the usual set and there is no prize for
inventing a different one — the lenses are the index, and an index nobody recognizes is worse
at its one job.

**4 · Find the ideas.** Ten to twenty. Pull them out of the material: a phrase the client
repeated, a tension between two things they said, a reference that does not fit the others and
is more interesting for it. Each gets:

- a **title** and a **line** — and that pair has to sell it alone, because the desk is read
  zoomed out first;
- a **lens** it files under;
- the **visions** it belongs to (write this once, on the idea — the vision's list is derived,
  so the two can never disagree);
- one line per lens it touches, saying what it *does*: *"tabular numerals, always"* is
  intention, *"Inter 16/24, 1.25 scale"* is specification and belongs to a later stage;
- **plates** — images that already exist in this workspace, captioned with what to take from
  them, never with what they are;
- the **detail** underneath: how it works, and why the material supports it.

**5 · Assemble the visions.** Three to five. A vision is not a bucket of ideas that resemble
each other; it is a whole brand that only works if those ideas are all true at once. Each
gets a thesis in one sentence, a story of two or three paragraphs, one line per lens, its
plates, and two things nothing else on the desk carries:

- **Tension** — what it needs that may not exist, or the way it can be read wrong. A vision
  with no tension has not been thought about, and it is the one that quietly wins on
  presentation rather than on merit.
- **Asks** — what the client has to give us before it can be built. Name the person.

**Check the spread before you render.** If two visions differ only in tone, they are one
vision and you owe the owner another. Real difference means disagreeing about what the work
is *for*, not about hue. And if every idea ends up in every vision, there is only one vision
here wearing three hats — say so rather than shipping the illusion of choice.

**6 · Write the file and render it.** `brain/moodboards/YYYY-MM-DD-<topic>.md` in the shape
`brain/moodboards/README.md` specifies, tagged from `brain/tags.md`, carrying the strand's
`project:` key. Then `python3 brain/board.py`, read the page yourself before handing it over,
and give the owner the path.

**7 · Take the reaction, in their words.** Ask which vision they would build and which ideas
they would kill. Take it verbatim — *"marginalia is too cute next to a balance"* is usable,
*"I don't love it"* is not. The page has a note box on every card that saves to their browser;
what they type there is theirs, and it does not reach this repo, so ask for the reaction
rather than waiting to find it.

Then rewrite through what they said. **Nothing is deleted** — an idea they killed loses its
visions and stays on the desk, which is what the file is for.

## Guardrails

- **No new material.** If the desk needs an image nobody has, that is a task and a line in
  `now.md`, not a description of an image you wish existed. Generating one is worse: it puts
  a made-up artefact next to real evidence and they read as equals.
- **Brand assets are never drawn.** The charter's rule is absolute and applies here even
  though this looks like a sketch. A plate showing the client's mark is their file, extracted
  with `brain/extract.py` or supplied — never redrawn to make a specimen look finished.
- **Specimens are optional, and they are `/explore`'s layer.** A desk with no specimens is a
  finished moodboard. Add one to a vision when the argument needs proof it can be executed,
  and expect `/explore` to be where they are really made and judged.
- **One project per desk.** The ideas are judged against one strand's brief. A desk mixing two
  strands argues for a brand nobody is building.
- **Not a client deliverable** unless the owner says so. It is a thinking artifact, and it
  holds quotes and references that may be confidential.
- **The house style is the page's, not the work's.** `board.py` renders in the workspace's own
  look because the owner is reading it. Nothing on the desk prescribes that look for the
  project — a specimen has its own aesthetic, sandboxed so it cannot leak either way.
- **Do not re-open what is decided.** Check `brain/decisions/` first. A desk arguing for
  something already settled is contradiction, and the charter says raise it rather than
  quietly proposing around it.

## Where it goes next

A desk that changed what the work is about produces either an exploration (`/explore`, taking
the surviving visions as its brief) or a decision — and whichever it is links back to this
file by name. Until one exists, `now.md` says the work is making sense of the research, and
names no vision.
