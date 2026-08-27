# Sources

*The owner of **what the assistant watches** outside this repo. `/setup` writes it by asking,
then probing what is actually reachable; `/briefing` reads it and writes a dated file in
`brain/briefings/`.*

**Connections are per-person, not per-repo.** This file can name a Slack channel or a Linear
team; it can never carry credentials, and a connector that works on one machine may be absent
on another. So every line carries a state:

- `connected` — reachable from this machine, and confirmed by an actual call
- `wanted` — the source is real and matters, but the connector isn't reachable here

**Format.** One line per source:

```
- `kind` · identifier · state — why it matters
```

`kind` is one of: `slack` · `fathom` · `granola` · `gmail` · `calendar` · `linear` · `notion`
· `figma` · `other`.

**Every line a briefing pulls from a source is attributed** — who said it, where, when, with a
link where one exists. A summary with no attribution is laundering and does not get written.

---

## Watched

*(none yet — `/setup` fills this by asking, then probing what is actually reachable)*

## Wanted, not connected

*(sources worth having when the connector becomes available — this is also the fix-it list)*
