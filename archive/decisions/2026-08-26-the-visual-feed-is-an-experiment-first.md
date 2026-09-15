---
tags: [interface]
---
# [[the-visual-feed-is-an-experiment-first]] — The visual feed is an experiment before it is a rule
Date: 2026-08-26 · Status: accepted

## Context

The owner wants `feed.html` to become the real second interface: *"I think the HTML needs to
be more enforced - it needs to be visual. When possible, the agent should take screenshots
to show before and after a change… Past feed items should recede visually (they already do)
but also be collapsed by default."* Then, on reflection: *"About the before/after
screenshots, and the broader role of HTML, it sounds fancy but let's test it first - it might
be too slow and cluncky."*

Both are right. A before/after pair per visual change is the most compelling thing the page
could carry, and it is also a browser or Figma round-trip plus image handling on every
change — the kind of instrumentation that quietly doubles the cost of small work.

## Decision

Separate what is cheap and certain from what needs evidence.

**Do now** (no cost to prove): past and answered feed items render collapsed by default,
only what is awaiting the owner is open · `feed.py` runs as part of `/close` instead of
by memory · `doctor.py` reports a stale page, using the `--check` path that already exists.

**Test before adopting**: before/after screenshots, and any further expansion of the page's
role. The experiment is one real visual change, instrumented end to end, measured on wall
clock added and whether the pair was worth looking at. It is a task, and the honest possible
outcome is "too slow, dropped."

Rejected for now: making screenshots a charter rule with a `doctor.py` check behind them.
Enforcing a habit that has not been shown to pay is how the workspace acquires ceremony.

## Consequences

- The clone-ready stage is not blocked on the expensive half.
- `now.md` and `feed.html` keep their division: `now.md` is what the assistant reads to
  orient, the page is what the owner looks at. The page renders `now.md`; it never competes
  with it, and it is a projection — written outward, never read back as authority.
