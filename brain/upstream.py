#!/usr/bin/env python3
"""upstream.py — pull boilerplate improvements into a project without eating the project.

    python3 brain/upstream.py             # what changed upstream, grouped by who owns it
    python3 brain/upstream.py apply       # take the template-owned changes; touch nothing else
    python3 brain/upstream.py apply --dry-run

**The problem this solves.** A clone starts with `rm -rf .git && git init`, so it has no link
to the boilerplate at all: no remote, no version, and no record of which files came from the
template and which the project wrote. An assistant asked to "check for updates" therefore has
to be told, every single time, which files are its own scaffolding and which are the owner's
work — and being told is not a safeguard, because the one time nobody says it the assistant
overwrites `now.md` with a template placeholder.

**So ownership lives here, in code, versioned with the template that claims it.**

Three classes, and the bias is deliberate: anything unrecognised is MERGE, never OWNED. The
failure being prevented is clobbering, so an unclassified file gets a human, not a guess.

  OWNED    the template's own machinery. Overwritten wholesale on `apply`.
  PROJECT  the owner's work and current state. Never read from upstream, never written.
  MERGE    the template ships part and `/setup` fills the rest — `AGENTS.md` carries the
           charter plus this project's identity lines, `craft.md` ships sections 1, 2 and 5
           with 3 and 4 written at setup. A diff here is shown and left alone.

A project can extend PROJECT through `template.extra_project_paths` in `workspace.toml`. There
is deliberately no way to extend OWNED: widening what gets overwritten is the dangerous
direction, and it belongs upstream where everyone gets it.
"""

from __future__ import annotations

import ast
import fnmatch
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
sys.path.insert(0, str(BRAIN))

from config import CONFIG, TEMPLATE_HOME, FORMER_TEMPLATE_HOMES, repo_id  # noqa: E402

DEFAULT_REPO = TEMPLATE_HOME

# The template's machinery. Improvements to these are the whole point of checking upstream.
OWNED = (
    "brain/*.py",
    ".claude/skills/**",
    ".agents/skills/**",
    ".github/workflows/**",
    ".claude/hooks/**",
    "CREDITS.md",
    "brain/*/README.md",
    "brain/lenses/record.md",
    "brain/decisions/0000-decision-template.md",
)

# The owner's work and the project's current state. Nothing upstream has an opinion on these,
# and a template placeholder written over one of them destroys real work.
PROJECT = (
    "brain/workspace.toml",
    "brain/now.md",
    "brain/tasks.md",
    "brain/plan.md",
    "brain/project-brief.md",
    "brain/feed-items.md",
    "brain/open-questions.md",
    "brain/glossary.md",
    "brain/sources.md",
    "brain/decisions/*.md",
    "brain/insights/**",
    "brain/explorations/**",
    "brain/moodboards/**",
    "brain/workshops/**",
    "brain/braindumps/**",
    "brain/briefings/**",
    "brain/drafts/**",
    "brain/reviews/**",
    "brain/references/**",
    "brain/playground/**",
    "brain/decks/**",
    "context/**",
    # Product repos cloned into the workspace. Each is its own git repo with its own history,
    # and nothing upstream may read or write inside one.
    "projects/**",
    ".env.agents",
    "brain/*.html",
    "brain/brain.canvas",
    "archive/**",
)

# Template files that live *inside* a project-owned folder. `brain/decisions/` holds the
# project's decisions and also the template's blank and its format README, so these are
# checked before PROJECT or the folder pattern would swallow them.
OWNED_INSIDE_PROJECT = (
    "brain/*/README.md",
    "brain/decisions/0000-decision-template.md",
    "brain/playground/_canvas/**",
    "brain/playground/_template/**",
)

# Template above, project below, in the same file. Only a human can merge these.
MERGE = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    # `/setup` appends this project's confidential paths. Overwriting the file wholesale on
    # `/update` would un-ignore client material, and the next push would publish it.
    ".gitignore",
    ".claude/settings.json",
    "brain/lenses/craft.md",
    "brain/tags.md",
)


def _match(rel: str, patterns) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(rel, pat):
            return True
        # `dir/**` should also match `dir/a/b/c`, which fnmatch does not do on its own.
        if pat.endswith("/**") and (rel + "/").startswith(pat[:-2]):
            return True
    return False


RULE_NAMES = ("OWNED", "PROJECT", "OWNED_INSIDE_PROJECT", "MERGE")


def rules_from(path: Path) -> dict | None:
    """The four ownership tuples out of another copy of this file, read with `ast` so nothing
    in it runs. `/update` uses the *upstream* copy's rules to classify an update, because the
    rules that know about a new template folder arrive in the same update as the folder: a
    clone classifying with its own, older rules filed `brain/playground/_canvas/` as "needs
    you" and the owner copied it in by hand, which is the one thing this script exists to make
    unnecessary."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id in RULE_NAMES:
            try:
                out[node.targets[0].id] = tuple(ast.literal_eval(node.value))
            except ValueError:
                return None
    return out if all(k in out for k in RULE_NAMES) else None


def classify(rel: str, rules: dict | None = None) -> str:
    """`owned` | `project` | `merge` for a repo-relative path.

    Order matters. A project's own `extra_project_paths` win outright. Then the handful of
    template files that sit inside project folders — `brain/decisions/README.md` and the blank
    — because otherwise `brain/decisions/*.md` swallows them. Then PROJECT, so the project's
    actual decisions are never read from upstream. MERGE is the fallback, because an
    unrecognised file is a question rather than an answer.

    `rules` overrides the tuples in this file — see `rules_from`."""
    r = rules or {"OWNED": OWNED, "PROJECT": PROJECT,
                  "OWNED_INSIDE_PROJECT": OWNED_INSIDE_PROJECT, "MERGE": MERGE}
    extra = tuple(CONFIG.get("template", {}).get("extra_project_paths") or ())
    if _match(rel, extra):
        return "project"          # the project's own additions always win
    if _match(rel, r["OWNED_INSIDE_PROJECT"]):
        return "owned"
    if _match(rel, r["PROJECT"]):
        return "project"
    if _match(rel, r["MERGE"]):
        return "merge"
    if _match(rel, r["OWNED"]):
        return "owned"
    return "merge"


def fetch(repo: str, into: Path) -> str | None:
    """Shallow-clone upstream into a temp dir. Returns its HEAD sha, or None on failure.

    A clone rather than a remote on purpose: adding the boilerplate as a remote entangles two
    unrelated histories, and every later `git log` in the project carries the template's
    commits. This borrows the files and throws the repo away."""
    r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", repo, str(into)],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"upstream: could not clone {repo}\n  {r.stderr.strip()[:300]}")
        return None
    h = subprocess.run(["git", "-C", str(into), "rev-parse", "HEAD"],
                       capture_output=True, text=True, timeout=30)
    return h.stdout.strip()[:12] if h.returncode == 0 else "unknown"


def walk(root: Path) -> dict:
    out = {}
    skip = {".git", "__pycache__", "node_modules", "context", "projects"}
    for p in sorted(root.rglob("*")):
        if not p.is_file() or skip & set(p.relative_to(root).parts):
            continue
        out[str(p.relative_to(root))] = p
    return out


def compare(theirs: Path) -> dict:
    """`{class: [(rel, state)]}` where state is `new` or `changed`. Unchanged files are
    dropped — a report listing what is already correct is a report nobody reads."""
    groups: dict = {"owned": [], "merge": [], "project": []}
    mine = walk(ROOT)
    rules = rules_from(theirs / "brain" / "upstream.py")
    for rel, src in walk(theirs).items():
        cls = classify(rel, rules)
        if cls == "project":
            continue          # never even compared: upstream has no opinion here
        dst = mine.get(rel)
        if dst is None:
            groups[cls].append((rel, "new"))
        elif dst.read_bytes() != src.read_bytes():
            groups[cls].append((rel, "changed"))
    return groups


def stamp(sha: str) -> None:
    """Record which boilerplate commit this project last took, so the next check has a floor.

    Written with a regex rather than a TOML writer because `workspace.toml` is full of
    comments that carry the reasoning, and a round-trip through a serializer would delete
    every one of them."""
    p = BRAIN / "workspace.toml"
    text = p.read_text(encoding="utf-8")
    if re.search(r"^\s*version\s*=", text, re.M) and "[template]" in text:
        text = re.sub(r"(\[template\](?:.|\n)*?^\s*version\s*=\s*)\"[^\"]*\"",
                      lambda m: m.group(1) + f'"{sha}"', text, count=1, flags=re.M)
    else:
        text += (f'\n[template]\n# The boilerplate commit this project last took, written by\n'
                 f'# `python3 brain/upstream.py apply`. It is the floor for the next check.\n'
                 f'repo = "{DEFAULT_REPO}"\nversion = "{sha}"\nextra_project_paths = []\n')
    for former in FORMER_TEMPLATE_HOMES:
        text = text.replace(f'repo = "{former}"', f'repo = "{DEFAULT_REPO}"')
    p.write_text(text, encoding="utf-8")


# Generated noise is not work at risk, and blocking an update on a stale `__pycache__` teaches
# people to pass whatever flag makes the guard go away.
NOISE = ("__pycache__", ".DS_Store")


def dirty() -> list:
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return []
    return [ln[3:] for ln in r.stdout.splitlines()
            if ln.strip() and not any(n in ln for n in NOISE)]


def main() -> int:
    do_apply = "apply" in sys.argv
    dry = "--dry-run" in sys.argv
    tmpl = CONFIG.get("template", {})
    repo = tmpl.get("repo") or DEFAULT_REPO
    if repo_id(repo) in {repo_id(u) for u in FORMER_TEMPLATE_HOMES}:
        print(f"upstream: template.repo names the boilerplate's former home; reading\n"
              f"          {DEFAULT_REPO} instead. Update template.repo to match.")
        repo = DEFAULT_REPO
    known = tmpl.get("version") or ""

    if do_apply and not dry and (changes := dirty()):
        print(f"upstream: the tree has {len(changes)} uncommitted change(s). Commit or stash "
              f"first,\n         so `git diff` reviews the update and `git checkout .` undoes "
              f"it.\n         e.g. {', '.join(changes[:3])}")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        theirs = Path(tmp) / "upstream"
        sha = fetch(repo, theirs)
        if not sha:
            return 1
        groups = compare(theirs)

        print(f"upstream — {repo}")
        print(f"  at {sha}" + (f", this project last took {known}" if known else
                               ", this project has never recorded a version"))
        total = sum(len(v) for v in groups.values())
        if not total:
            print("\n  nothing to take: every template file here matches upstream.")
            if do_apply and not dry:
                stamp(sha)
            return 0

        if groups["owned"]:
            print(f"\n  template-owned — safe to take ({len(groups['owned'])}):")
            for rel, state in groups["owned"]:
                print(f"    {state:8} {rel}")
        if groups["merge"]:
            print(f"\n  needs you — template and project share these ({len(groups['merge'])}):")
            for rel, state in groups["merge"]:
                print(f"    {state:8} {rel}")
            print("    → read the upstream diff and port what you want by hand. Never copy\n"
                  "      one of these over: it carries this project's own answers.")
        print("\n  untouched: every file under brain/decisions, insights, explorations,\n"
              "  moodboards, workshops, braindumps, briefings, drafts, reviews,\n"
              "  references, plus\n"
              "  now.md, tasks.md, plan.md, project-brief.md, workspace.toml, context/\n"
              "  and projects/.")

        if not do_apply:
            print("\n  `python3 brain/upstream.py apply` takes the template-owned ones.")
            return 0

        for rel, _ in groups["owned"]:
            dst = ROOT / rel
            if dry:
                print(f"  would write {rel}")
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(theirs / rel, dst)
        if dry:
            print(f"\n  dry run — {len(groups['owned'])} file(s) would be written.")
            return 0
        stamp(sha)
        print(f"\n  took {len(groups['owned'])} template-owned file(s); recorded {sha}.")
        print("  Review with `git diff`, then `python3 brain/doctor.py` and "
              "`python3 brain/test_brain.py`.")
        if groups["merge"]:
            print(f"  {len(groups['merge'])} file(s) still need you — listed above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
