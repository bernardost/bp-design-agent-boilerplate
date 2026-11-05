---
tags: [process]
---
# One script opens pages in the browser and reveals files in Finder
Date: 2026-11-05 · Status: accepted

## Context

The owner reported that agents were not opening pages in his browser on their own. The charter
already required it, but two skills told the agent otherwise: `/explore` said to run
`spread.py` "and give the owner the path", and `/moodboard` said the same of `board.py`, both
without `--open`. An agent follows the step in front of it over a rule 200 lines up in a
46 KB charter. The rule also covered HTML pages only, so a draft or a PDF he had to look at was
named in the reply and left for him to find. ^[owner · session · 2026-11-05]

He asked for a command to pull something up in his browser, the default one unless he names
another, and one to reveal a file in Finder.

## Decision

- `brain/show.py` does both. A page or URL goes to the browser macOS uses for web links, read
  from LaunchServices, not to whatever app owns `.html` (often a code editor on a designer's
  machine). `--browser <name>` picks another; `--reveal` selects the file in Finder. A missing
  path is an error, and a remote session prints the paths instead of failing.
- `/open` and `/reveal` wrap it.
- The charter's rule now covers any file the owner should look at: pages are opened, other
  files are revealed. It is shorter than the rule it replaced.
- `/explore` and `/moodboard` now pass `--open`.

## Consequences

The charter's size is a separate problem and is not addressed here: 46 KB, a third of it in
the 19 always-on behaviors. A trim is its own piece of work.
