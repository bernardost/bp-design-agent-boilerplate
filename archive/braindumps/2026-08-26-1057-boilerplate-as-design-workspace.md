---
tags: [template-shape, onboarding, interface, portability]
---
# Turning the boilerplate into the blank agent for design projects

*Verbatim. Two messages, in order, 2026-08-26. Processing routes content out; the dump is
never rewritten.*

---

## Message 1

Ok, let's configure this agent boilerplate. I want this to become the blank agent I use across my design projects. There are some things here that come from a heavy agent-building project, which I think might not be super relevant for future projects. For example, the concept of ADR - that's developer lingo, isn't it. Tracking decisions, yes, tagging stuff, yes, but the ADR thing I fail to see the benefit of the nomenclature. Anyway, it works well.

The experience I'm looking for:

- User clones the repo and starts up their agent (could be Claude, Codex or some model via an IDE like cursor. I prefer Claude Code). On first use, agent takes the user through a small quiz to set up the agent architecture. I'm not sure what the questions could be, I forgot, but I think some things need to be tweaked depending on what the project is all about. For example, who are the stakeholders, Slack channels to keep track of, so that the agent can produce briefings and keep track of fathom, granola, email, calendar and slack activity. Linear is also a thing. User might want Notion for some reason.
- Another thing the onboarding serves is to show the user the commands like /braindump and the other skills. And by the way, the reviewer skill will probably change depending on the project, and I'm not sure how we would operationalize that.
- I love the whole concept of a brain with tags. Tags should be global to the brain, so that an ADR and an insight can share the same tag. I would want this to work really well and for the user to be able to visualize the brain somehow (interconnected nodes are awesome, but it would require obsidian right? Don't want to bloat this too much tho)
- Now.md works really well, with the doctor.py. However, we also have feed.html. Both seem to overlap. I want the HTML to be the secondary interface with the agent. i think the HTML needs to be more enforced - it needs to be visual. When possible, the agent should take screenshots to show before and after a change, for example. Past feed items should recede visually (they already do) but also be collapsed by default.

This is my braindump. Any other ideas or thoughts?

---

## Message 2

All sounds good. A couple of other things - user should set up a repo, and agent should explain why: so you can use this agent on your phone. Massive value in that. What the agent needs to do: every new thing gets pushed, without user asking to wrap up or something. Which brings me to wrapping up. A common axiety is portability - closing an IDE and having the next agent know what is happening. I know now.md and the other files solve for that, but the user needs to know when a wrap up is needed. About the before/after screenshots, and the broader role of HTML, it sounds fancy but let's test it first - it might be too slow and cluncky.
