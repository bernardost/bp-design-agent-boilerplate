# `workshop/` — the live workshop deck

*The template's own code, served by `brain/workshop.py`. The workshops themselves live in
`brain/workshops/`; the `/workshop` skill has the commands and the routine.*

```
library.json   the boards a workshop can hold, their questions and defaults. A question's
               `pick` is how the async form asks it: options, chips or a scale instead of a field. Edit to change
               what every new workshop starts with; an existing deck keeps its own copy.
deck.html      the page, deck.css its styles, deck.js every board and the saving.
home.html      the home page: a new workshop with its boards picked, and the past ones.
form.html      the async form: a deck's questions as one page a client fills in alone, in
               the house style for pages that are used, the same design as brief.html.
               `workshop.py send` fills it in and writes it as a file, or serves it hosted.
hosted/        the hosted form for Vercel: `api/form.js` saves answers to Upstash Redis.
               `workshop.py host` links, deploys and checks it; nothing here holds answers.
```

The boards are ported from Far Wall v24, the design of record of AE Kickoff: the same type
scale, lines, containers, corners, Deck panel, timeline, audiences and ending, without its
canvas controls, photos or brand mark. The look is set on `<html>` in `deck.html` and in the
custom properties at the top of `deck.css`; change it there, not per board.

Board kinds: `cover`, `agenda`, `team`, `rows` (labelled rows against one or more columns),
`goals` (buckets of entries), `timeline`, `questions` (any number of these), `personas`,
`raci`, `traits` (pairs of words on seven steps), `week`, `steps`, `end`. Only `questions`,
`rows` and `goals` can be added under a new key; the rest exist once, under their library key.
