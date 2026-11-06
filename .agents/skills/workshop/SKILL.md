---
name: workshop
description: Run a workshop with the client, live on a call or sent as a form. Live is the default — a deck of boards picked from a design-brief library, presented from this repo, every answer saved to brain/workshops/ as it is typed, with notes that can go to Notion. The same deck's questions can go to a client as a plain form, by email as a file or as a hosted link, and the answers come back into the workshop's notes. Use for /workshop, "set up the kickoff", "make a workshop", "send the client the questions", or when a call was missed, a promised document never arrived, or the work is blocked on information only a stakeholder has.
---

# Workshop — live first, a form when the call does not happen

Three shapes. **Live** is the default: the owner presents a deck of boards on a call and types
the answers into it as people talk. **A form** sends the same deck's questions to a client to
answer alone. **A built async workshop** (further down) is for when a form is not enough. Ask
which only when the conversation has not made it obvious.

## Live: the workshop deck

`brain/workshop.py` is a local server and `brain/workshop/` is the deck it serves: the boards
of Far Wall, AE Kickoff's design of record, with the questions rewritten for a design brief
(`library.json`). Standard library only, no database, no account.

```
python3 brain/workshop.py serve --open                       # home page: new workshop, past ones
python3 brain/workshop.py new "Brand kickoff" --client Acme --date 2026-11-12 --open
python3 brain/workshop.py new --spec brain/workshops/<spec>.json --open
python3 brain/workshop.py library                            # the boards and their keys
python3 brain/workshop.py notes <id>                         # rewrite notes.md by hand
```

**Where it saves.** One folder per workshop, `brain/workshops/YYYY-MM-DD-<client>-<title>/`:
`deck.json` is the truth, `notes.md` is the same answers as markdown, rewritten on every save,
and `history/` (gitignored) holds a copy every ten minutes and before any conflicting write.
The page keeps every keystroke in the browser first and sends it a moment later, so a dropped
connection, a stopped server or a refresh loses nothing; the foot says *Not saved to disk ·
kept in this browser* until the server answers again. Reopening lands on the board the owner
left, with the time spent on each board kept.

**Generating one for this project.** Read `brain/project-brief.md` and the open questions
first, as for any workshop. Then write a spec rather than taking the defaults: switch on the
boards this project needs, and rewrite or add questions in the client's own words, with what
is already known left out. A spec is the library's shape, trimmed:

```json
{"title": "Brand and app kickoff", "client": "Acme", "date": "2026-11-12", "us": "Studio",
 "project": "<key, when the workspace has more than one>",
 "boards": ["team", "mv", "goals", "tl", "pers", "traits", "raci", "pre", "steps",
   {"key": "brand", "questions": [{"q": "What do enterprise buyers say about you today?", "d": ""}]},
   {"key": "pricing", "kind": "questions", "name": "Pricing", "title": "What it costs, and why",
    "questions": ["What do customers pay today?", "Who has said it is too expensive?"]}]}
```

Listed boards are switched on, every other library board is in the deck switched off (the
owner can switch it in during the call from the gear), and a new key must be a `questions`,
`rows` or `goals` board. Show the owner the board list and the questions you changed before
the call, in one message, and let him cut them.

**During and after.** Never edit a `deck.json` while its page is open: the page's next save
overwrites the edit (the replaced copy lands in `history/`). After the call, read `notes.md`
and route it like a transcript: decisions to `brain/decisions/`, insights to `brain/insights/`,
what stayed open to `brain/open-questions.md`, and the brief where the workshop moved it.
An answer the owner typed during the call is the client's word only if he says it was; ask
once when it matters.

**Notion.** Notes go to Notion as a projection, never as the store. Load the Notion connector
(authenticate if asked), and create one page under the parent named in `[workshop]
notion_parent` in `brain/workspace.toml` (ask once and write it there if it is empty), titled
with the workshop's title and date, its body `notes.md` without the frontmatter. Put the page's
link at the top of the answers routing you report. Re-running replaces that page's content;
it never creates a second one.

**Brand assets.** The cover sets the studio's name and the client's as text. Never draw a
logo in; the rule in `AGENTS.md` has no exceptions here either.

## Sent as a form: the async workshop

Prep exactly as for a live workshop: create the deck, switch boards, edit the questions. Then
send it. The client gets one page in the same design as the brief (`brain/lenses/house.md`,
section 2): contents with what is left in each section, a sticky bar with progress and *Send
answers*, a band per section, a status tag per question, and the two steps that send the
answers back spelled out at the end. Nothing is pre-filled and there is nothing to log in to.
Team, timeline, RACI, week and next steps belong to a call and stay out.

**Make answering a tap wherever the answer has a shape.** A question with a `pick` is answered
with options instead of a text field. The library already gives one to the questions that
have a short list of likely answers; give one to every question you write whose answers you
can list, and leave a text field only for an answer that is a sentence only they have:

```json
{"q": "What should it drive?", "d": "",
 "pick": {"type": "many", "options": ["Signups", "Retention", "Trust"], "max": 3, "other": true}}
```

`type` is `one` (a stack of options), `many` (chips, `max` to cap them) or `scale` (two words
on seven steps: `"a": "Simple", "b": "Deep"`). `other` adds *Something else* with a field;
`note` adds *Add a note*. A pick's own `d` replaces the question's hint, so a hint that only
listed the options can go. The live deck ignores `pick`; it still shows the question.

```
python3 brain/workshop.py preview <id>                       # what the client will see; sends nothing
python3 brain/workshop.py send <id> --to "Dana Ruiz" [--due "Friday 13 November"] [--note "…"]
                                    [--reply-to studio@example.com]   # or [workshop] reply_to
python3 brain/workshop.py receive ~/Downloads/<…>-answers-dana-ruiz.html
python3 brain/workshop.py pull [<id>]                        # hosted forms: fetch the answers
python3 brain/workshop.py host                               # once per workspace, for --via vercel
```

One form per person; a second person gets a second `send`. Each send writes
`responses/<who>-<token>.json` in the workshop's folder: the questions as sent and whatever
came back. Answers never go into `deck.json`, so a deck open in a tab cannot overwrite them,
and `notes.md` gains an *Answers from <name>* section for each.

**Two ways to send it.** `--via` picks one; `[workshop] send_via` in `brain/workspace.toml` is
the default, and `file` needs nothing set up. Ask the owner which the first time and write it
there; a template clone may not want its client answers on Vercel at all.

- **`file`** writes one HTML file to `send/` and reveals it in Finder for the owner to attach
  to an email. The client's answers stay in their browser as they type. At the end they
  download a copy of the page with the answers inside and email it back; `receive` reads it.
  Nothing arrives until they send it, and a different browser starts empty.
- **`vercel`** gives each person a link; every answer is saved as it is typed, from any
  device, and `pull` fetches them. `host` sets it up once: it links a Vercel project, adds an
  Upstash Redis store for the answers, puts a key in `.env.agents` that only this workspace
  holds, deploys `brain/workshop/hosted/`, and writes the address to `[workshop] host_url`.
  It needs the Vercel CLI logged in, and the CLI may ask the owner to accept Upstash's terms,
  so the owner runs it himself the first time: `! python3 brain/workshop.py host`. Re-run it
  after `form.html` changes to redeploy. Deploying is publishing: ask before the first one.

**When answers arrive**, route them like the notes of a call. These are the client's own words,
typed alone; quote them as such. A blank is `_open_`, never a no.

---

# A built async workshop — when a form is not enough

A client misses the workshop, does not send the document he promised, and will not read an
email with nine questions in it. The work needs his answers anyway. The move is to take the
call apart into screens he can answer alone, on a phone, in pieces, over a day — because every
tap is data and **a half-finished run is still data**, which is more than a cancelled call
gives you.

The method in one sentence, and it is the whole method: **state the assumption, let him
confirm it.** The more we assume and ask him to confirm, the less thought it costs him, and
cost to him is the only variable that decides whether this gets answered at all.

## When this is not the right move

When the question is one the stakeholder has to think out loud to answer. Every screen here
has to be a choice between things we could already draw. If you cannot write a defensible
assumption for a screen, that screen belongs in a conversation, not in a workshop — cut it and
say so.

Also not the move when nobody has read `brain/project-brief.md` and the open questions. A
workshop that asks what the client already told us on a recorded call is how you lose him on
screen two.

## The rules that hold up

1. **Every guessable screen arrives with our answer selected.** The fastest path through the
   whole thing is tapping Next. That is the design, not a shortcut.
2. **`chose` and `let stand` are different records.** Next with nothing touched saves our
   default flagged `let_stand`. In the answers file that is *inferred*, never his words.
   Without the flag, every default he skipped past hardens into a quote.
3. **The chapters you need to start come first.** Order so that stopping after chapter three
   still lets the work move. Never tell him where he may stop — a screen saying "that is
   everything we need" is an invitation to close the tab.
4. **Never ask what has already been heard.** Go through the brief, the briefings and the
   recordings first, and mark what is already known as off-limits.
5. **Some things stay ours.** Anything he has called interchangeable is our call to propose,
   not his to answer. Anything that is really an email stays an email. Taste questions can
   wait for a moment where taste is the subject.
6. **A tick must always add something.** "What should stay unsaid, all pre-ticked" reads as a
   trap. Invert it: "what may this say", nothing ticked. Ticking adds, never removes.
7. **Show, don't ask.** A question the stakeholder has to picture in his head is a question
   he postpones. Draw the thing and let him move, rank, tick or drag. The section below is
   the working part of this rule.
8. **Later screens read earlier answers.** Ask "what should each visitor take away?" using the
   audiences he ranked three screens ago, with a guess per audience. Building on his own
   answers is what makes it a workshop rather than a form.
9. **The container must not vote.** White, one sans, hairlines. It is the brief for work whose
   look is undecided; a mood in the chrome pre-empts the mood question. This is the one place
   the house style in `AGENTS.md` does apply to something a client sees, and for that reason.
10. **One link, one person, no login.** The token in the URL is the identity. A second person
    gets a second link. Nothing to sign up for, nothing to remember.
11. **Save on tap, no submit.** There is no finished state we depend on. Reopening lands on
    the first unanswered screen; the chapter menu is one tap away.
12. **Phone first.** He will open it in a taxi. Every drawing survives 390 pixels or it is not
    in the build.
13. **Never call it a quiz where he can see it.** To him it is the brief, in questions.

## Make it answerable — the visual half

This is where an async workshop is won or lost. The written outline is the content; the
controls are what make answering cost seconds instead of thought. **A screen that could be a
picture and is a paragraph instead is a screen he skips.**

**Match the control to the shape of the answer.** These are the ones that earn their place, and
each came from a board zone that worked in the room first:

| The answer is… | The control | Looks like |
|---|---|---|
| an order of importance | **rank** — drag the cards, cross out the ones that don't apply | audience cards, each with one line explaining who they are |
| a shortlist from many | **pick three** — a grid of stickies, three slots | "what must this do?" with the rest left as nice-to-have |
| a position between two poles | **a 2×2 with a draggable marker**, peers already plotted on it | where the company sits among the people it will be compared to |
| a reaction to alternatives | **tabs of drawn options**, one on screen at a time | three sitemaps as small trees, not three columns of bullets |
| taste | **a wall of real screenshots**, tap what feels right | peer sites and outside references, each with one line of why it is there |
| a word between two words | **a slider**, both ends labelled, seeded where we think it sits | discreet ←→ loud, investor ←→ operator |
| a sequence | **a flow of boxes he can rewrite** | what a visitor lands on, reads, believes, then does |
| a prohibition | **finish-the-sentence cards**, some already filled | "this must never…" with four of ours and a blank |
| a sentence only he has | **one short text field**, and only here | the thesis line, the relationship in his words |

**Seed every control with our guess, visibly.** A slider starts where we think it sits. A rank
starts in an order. Stickies arrive with our words on them, sourced where they came from
something he said. He is correcting, not composing, and correcting is fast.

**Use his words on the cards.** Take the option wording, the brand adjectives and the slider
pairs from the recordings and threads, not from your own vocabulary — and tag them, so he
recognizes his own sentence instead of decoding ours. A guess in our language is a guess he has
to translate before he can agree with it.

**Write it the way you would say it.** Plain, non-technical, one idea per screen. No preamble —
the title and one line of setup, then the control. Never the word "quiz", never our internal
vocabulary (stage, bar, lens, exploration, IA), never a term of art where a plain one exists.
If a screen needs a paragraph to explain what it is asking, the question is wrong, not the
explanation.

**Every drawing is built for 390 pixels.** Trees and 2×2s are SVG on a fixed viewBox, scaled,
with labels flipped where they would run off the edge. Three things side by side become tabs.
A wall of screenshots takes the full width and goes large — a desktop with one small image per
row is a wasted screen.

## The run

**1 · Outline before code.** Write `brain/workshops/YYYY-MM-DD-<topic>-outline.md` in the shape
`brain/workshops/README.md` specifies: chapters, screens, and our assumption on every screen
with its source tag. Then **give the owner the path and let him cut it.** He will remove
screens, collapse a chapter, turn word-pairs into sliders, and rule on whatever you left open.
All of that is free here and expensive later. Do not build until he has cut it.

**2 · One data file is the workshop.** An array of screens — kind, options, default — plus a
`defaultValue()` for the let-stand row and a `summarize()` that renders any answer as one line
for our view. A dozen or so kinds covers everything: text, single, checklist, rank, pick,
sliders, matrix, wall, fields, toggles, sitemap, confirm-or-tick. The code mirrors the outline
and the outline stays the content source.

**3 · One component, one renderer, one table.** A client component holding position, answers, a
save queue and the chapter menu; a renderer that switches on kind; a "say it your way" text
field folded under every screen. Storage is one table keyed `(guest, screen)` with columns for
the value, a note, the `let_stand` flag and a timestamp, upserted through one route that checks
the token against a list of guests in an env var. No UI library, no diagram library — the
drawings are inline SVG.

**4 · Our view is a page.** `/answers?k=<admin>`: every screen, its answer in one line, and a
`chose` / `let stand` / `not reached` tag. That page is the one-page brief we send back, and it
is what you transcribe into `…-answers.md`.

**5 · Walk it headless at phone width. Then the owner runs it on a real phone.** Budget this;
it is not optional. The first run on a real engagement produced seven fixes that a headless
walk had shown as fine: a tick-to-exclude screen that read as a trap, three diagrams side by
side that did not fit, a screen that invited him to stop, optional fields that did not say they
were optional, a wall screen wasting a desktop, a screen ignoring the ranking he had just done,
and an end screen whose big button said "back to the start" so the whole thing read as
unfinished. Revise, then walk it again.

**6 · Wipe before sending, and build the reset button on day one.** The owner's test runs sit
in the same table under the client's name. That first run needed three wipes and had no reset
button. Put one in.

**7 · Send it, then watch.** The covering message is a draft in `brain/drafts/` like any other —
one link, one sentence about what it is, no instructions he has to follow. Then leave it alone.

## When the answers come back

Transcribe to `brain/workshops/YYYY-MM-DD-<topic>-answers.md`, verbatim, `chose` / `let stand`
/ `not reached` on every line. Then route it like a braindump: decisions to
`brain/decisions/`, realizations to `brain/insights/`, what is still open to
`brain/open-questions.md`, and update `brain/project-brief.md` where the workshop moved the
understanding. **Anything resting on a `let stand` says so where it is used.** Commit, push,
and tell the owner what changed and what he still has to chase.

## Cost

Roughly half a day from go to sent, including two revision passes, when the reference images
already exist in `brain/references/`. It is cheaper than rescheduling the call, and unlike the
call it produces a written record with attribution on every line.

## Next time

- The reset button goes in from the start.
- Take word-pairs and option wording from the source material before building, not from your
  own vocabulary — guesses there are guesses the client has to correct.
- Consider a ping to us on each chapter close, so we are not polling to see whether he started.
