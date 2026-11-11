---
name: product-repo
description: Work inside a product repo cloned into projects/<name>, on its own git, rules, checks and PR conventions. Use before the first edit, commit, push or PR under projects/, or to clone a product's code in.
---

# Working in a product repo

When the product is code in its own repo, it is cloned into `projects/<name>`, and that repo
runs on its own rules, not the charter's. The workspace holds the thinking about the work; the
product repo holds the work. Two git repos sit in one folder tree, and git acts on whichever
one contains the current directory, so every git step has to say which repo it means.

## Git

- **Push-as-you-go covers the workspace repo only.** Never push inside a product repo without
  asking, unless that repo's own docs say its agent may. A product repo usually works through
  branches and pull requests, and a push from a session following the workspace's rule lands
  on whatever branch is checked out. `.claude/hooks/guard_push.py` turns any push outside the
  workspace into a question in Claude Code; in Codex and Cursor, this sentence is the guard.
- **Run git with an explicit path and name the repo.** `git -C projects/app status`, and say
  *"in the app repo"* or *"in the workspace"* when you report it. A bare `git` after a `cd` is
  how a commit lands in the wrong history.
- **Isolate parallel code work with a worktree of the product repo**, not of the workspace.
  `projects/` is gitignored in the workspace, so a workspace worktree contains no product code.

## Before the first edit

- **Read the product repo's own instructions**: its `CLAUDE.md`, its `AGENTS.md`, whatever
  they import, and its `.claude/settings.json`. Claude Code started from the workspace root
  loads the product repo's `CLAUDE.md` only after you read a file in that folder, never loads a
  bare `AGENTS.md`, and does not run its hooks at all, so the checks that repo relies on are
  yours to run by hand. For a long stretch of code work, suggest opening a session inside
  `projects/<name>` instead, where all of it loads natively.
- **Its conventions govern the code.** The workspace's design process (the tuning drawer,
  every visual value as a custom property) governs prototypes made in the workspace, and
  reaches product code only where the product repo agrees. If the product repo keeps its own
  decision log, technical decisions go there; `brain/decisions/` records the design and
  engagement decision and links to it. If its rules and the charter's conflict, raise it
  rather than picking one.
- **Its writing rules override the charter's for anything written into it.** Page copy,
  commit messages, PR titles and bodies, a rewrite you propose in a comment: all of it follows
  that repo's voice rules. The two will disagree. One site this workspace served banned em
dashes and every contrastive pattern ("rather than", "instead of", "X over Y") while the
charter bans a shorter list; a session drafting under the
  workspace rules would have failed that site's copy tests on every PR. Find the product
  repo's rules before the first line of text, and treat its tests on wording as the spec.
- **A skill name can exist in both repos.** If the product repo ships its own `/setup` or
  `/status`, ask which one the owner means before running either.

## Before a PR

- **Run the product repo's own checks.** Its CI workflow (`.github/workflows/`), its test
  script and its build are the checks it relies on, and a session started from the workspace
  runs none of them on its own. Name each one you ran in the PR. If the repo pins a runtime
  version, switch to it first; a build that passes on the wrong Node proves nothing.
- **Find out what merging deploys before you touch the default branch.** A product repo may
  deploy straight to production from `main`, with no staging step in between. Read the deploy
  config and the repo's docs for this, say what you found, and if it is production, a
  PR is the only route and the owner merges it.
- **Follow the repo's PR conventions, including any disclosure of AI work.** Read a few recent
  merged PRs for the shape: the sections it uses, where screenshots go, what the title has to
  state. If the repo asks PRs to name the human owner and say what a person has and has not
  reviewed, that section is written truthfully, not as boilerplate.

## Declaring it

Declare each product repo in `work_lives` in `brain/workspace.toml`,
`"app: projects/app (own git repo)"`, so the next session knows the folder is a repo rather
than a directory of loose files. `doctor.py` fails a product repo that has been committed into
the workspace as a bare pointer.
