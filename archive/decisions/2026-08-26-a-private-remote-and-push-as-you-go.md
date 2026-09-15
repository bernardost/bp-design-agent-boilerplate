---
tags: [portability, git, onboarding]
---
# [[a-private-remote-and-push-as-you-go]] — A private remote, and push as you go
Date: 2026-08-26 · Status: accepted

## Context

The owner, 2026-08-26: *"user should set up a repo, and agent should explain why: so you can
use this agent on your phone. Massive value in that. What the agent needs to do: every new
thing gets pushed, without user asking to wrap up or something."*

The reason is concrete: with a remote, the same workspace opens in Claude Code on the web
and on the phone. The brain only travels if it is pushed, and a push that waits for
end-of-session is a push that did not happen when the owner opens their phone at lunch.

**This contradicts a standing rule** and the contradiction is resolved here rather than
ignored. The charter said: *"Client or third-party materials are confidential. Never push
this repo to a remote or paste their contents into external services without the owner's
say-so."*

## Decision

1. `/setup` asks about the remote and **explains the phone**, because the value is not
   obvious from the request. Default recommendation: a **private** GitHub repo.
2. The answer is recorded in `brain/workspace.toml`. Recording it **is** the owner's
   say-so, so the confidentiality rule is satisfied once, explicitly, in a file — not
   re-litigated every session. If the owner declines a remote, nothing is ever pushed and
   the assistant does not ask again.
3. With a remote configured, the assistant **commits and pushes each completed unit of
   work**, unprompted — not at session end. A unit of work is one that leaves the brain
   consistent: a decision logged, a task moved, a braindump routed, a deliverable changed.
4. Confidentiality survives regardless: `context/` and any client-material directory named
   at setup stay in `.gitignore`, and a private remote is a recommendation the assistant
   states, not a default it assumes. Public is the owner's explicit choice.

## Consequences

- The phone session is never more than one unit of work behind the desk session.
- History becomes granular and a little noisy. Accepted: legible history is worth less here
  than a brain that is always current on another device.
- A second device editing the same repo can conflict. The assistant pulls before it starts
  work and says so if the tree moved under it.
- This overrides the assistant's generic default of committing only when asked. The
  authorization is durable and lives in the config, which is why it is written down.
