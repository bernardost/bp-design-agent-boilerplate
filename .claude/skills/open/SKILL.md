---
name: open
description: Open a page, file or URL in the owner's browser. Use for /open, "pull this up", "show me in Chrome".
---

# Open

Run:

```
python3 brain/show.py <path-or-url> [more…] [--browser <name>]
```

- **What to open.** The argument he gave. With no argument, the page or file the conversation
  is about: the last one you built, changed or named. If two are equally likely, open both.
- **Which browser.** His default unless he names one. `--browser` takes `chrome`, `safari`,
  `firefox`, `arc`, `brave`, `edge`, `dia`, or an app's full name.
- **A page the script renders** (`feed.html`, `brief.html`, a spread, a board) is rendered
  first (its script, or `python3 brain/render.py`), then opened. Opening a stale page shows
  him something that is no longer true.
- **Say the path in the reply**, one line. A tab can be closed; the file stays.

If the script prints that there is no screen (a remote session), say so in one line and give
the path.
