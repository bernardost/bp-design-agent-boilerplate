#!/usr/bin/env python3
"""test_brain.py — the checks that lock down what `doctor.py` cannot check about itself.

    python3 brain/test_brain.py           # all of it, stdlib unittest, no dependencies

`doctor.py` lints the *content* of a brain. This lints the *tools*: that a link resolves, that
a migration does not lose a citation, that a page does not ship a `javascript:` href or the
owner's home directory. Every case here exists because something broke or nearly did — a test
with no failure behind it is a test nobody maintains.

Two styles, on purpose. Pure functions are imported and called. Anything that reads a brain is
run as a subprocess against a temporary workspace, because the scripts resolve their own paths
from `__file__` at import time and faking that would be testing the fake.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
sys.path.insert(0, str(BRAIN))

import config  # noqa: E402
import feed  # noqa: E402
import redate  # noqa: E402
import upstream  # noqa: E402
import when  # noqa: E402

SCRIPTS = ("config.py", "doctor.py", "feed.py", "brief.py", "spread.py", "render.py",
           "redate.py", "when.py", "playground.py")
CARRIED = ("now.md", "plan.md", "tasks.md", "feed-items.md", "open-questions.md",
           "project-brief.md", "tags.md", "glossary.md", "sources.md")


def workspace(tmp: Path, projects: list[tuple[str, str]] | None = None) -> Path:
    """A throwaway brain: the real scripts, the template's own current-state files, and a
    config naming whichever projects the test needs."""
    (tmp / "brain").mkdir(parents=True)
    for name in SCRIPTS:
        shutil.copy(BRAIN / name, tmp / "brain" / name)
    for name in CARRIED:
        if (BRAIN / name).exists():
            shutil.copy(BRAIN / name, tmp / "brain" / name)
    for d in ("decisions", "insights", "explorations", "workshops", "braindumps",
              "briefings", "drafts", "reviews", "lenses", "references"):
        (tmp / "brain" / d).mkdir()

    projects = projects or [("core", "The Product")]
    keys = ", ".join(f'"{k}"' for k, _ in projects)
    labels = ", ".join(f'"{v}"' for _, v in projects)
    (tmp / "brain" / "workspace.toml").write_text(f'''[engagement]
name = "Testbed"
owner = "Tester"
is_template = false

[projects]
keys = [{keys}]
labels = [{labels}]
work_lives = []

[tracker]
name = ""
prefix = ""

[tasks]
labels = ["design", "research", "bar", "deferred"]

[git]
remote = false

[generation]
route = ""

[brief]
publish = false

[confidential]
paths = ["context/"]
''')
    return tmp


def decision(folder: Path, name: str, title: str, date: str, *,
             project: str = "", body: str = "x") -> Path:
    fm = "---\ntags: [craft]\n" + (f"project: {project}\n" if project else "") + "---\n"
    path = folder / f"{name}.md"
    path.write_text(f"{fm}# {title}\nDate: {date} · Status: accepted\n"
                    f"## Context\n{body}\n## Decision\n{body}\n## Consequences\n{body}\n")
    return path


def run(ws: Path, script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ws / "brain" / script), *args],
                          capture_output=True, text=True, timeout=60, cwd=str(ws))


class Links(unittest.TestCase):
    """A dated decision is cited by its slug. Nothing may be cited by its year."""

    def test_slug_and_stem_resolve_and_the_year_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            d = ws / "brain" / "decisions"
            decision(d, "2026-09-15-the-portal-is-live", "The portal is live", "2026-09-15")
            decision(d, "2026-09-16-we-use-linear", "We use Linear", "2026-09-16")
            out = run(ws, "feed.py")
            self.assertEqual(out.returncode, 0, out.stderr)

            sys.path.insert(0, str(ws / "brain"))
            g = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, 'brain'); import feed; "
                 "g = feed.glossary(); print(sorted(k for k in g))"],
                capture_output=True, text=True, cwd=str(ws), timeout=60)
            keys = g.stdout
            self.assertIn("the-portal-is-live", keys)
            self.assertIn("2026-09-15-the-portal-is-live", keys)
            # The bug this exists for: `^(\\d{4})-` on a dated filename captures the year, and
            # every mention of "2026" in any prose becomes a link to one arbitrary decision.
            self.assertNotIn("'2026'", keys)

    def test_legacy_numbered_decision_still_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            decision(ws / "brain" / "decisions", "0007-the-portal-is-live",
                     "0007 — The portal is live", "2026-03-04")
            g = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, 'brain'); import feed; "
                 "print(sorted(feed.glossary()))"],
                capture_output=True, text=True, cwd=str(ws), timeout=60)
            self.assertIn("0007", g.stdout)
            self.assertIn("0007-the-portal-is-live", g.stdout)


class Urls(unittest.TestCase):
    """A briefing routes text in from Slack and mail, and the page opens on a phone."""

    def setUp(self):
        feed.cite_reset()

    def hrefs(self, text: str) -> list[str]:
        return re.findall(r'href="([^"]*)"', feed._inline(text, {}))

    def test_unsafe_schemes_are_not_clickable(self):
        for bad in ("javascript:alert(1)", "data:text/html,zz", "vbscript:x"):
            feed.cite_reset()
            self.assertEqual(self.hrefs(f"^[a · b · c]({bad})"), ["#"], bad)

    def test_http_survives_and_ampersand_is_escaped_exactly_once(self):
        got = self.hrefs("^[a · b · c](https://x.com/a?b=1&c=2)")
        self.assertEqual(got, ["https://x.com/a?b=1&amp;c=2"])
        self.assertNotIn("&amp;amp;", got[0])

    def test_the_footer_matches_the_inline_link(self):
        feed.cite_reset()
        feed._inline("^[a · b · c](https://x.com/a?b=1&c=2) ^[d · e · f](javascript:x)", {})
        footer = re.findall(r'href="([^"]*)"', feed.cite_list_html())
        self.assertIn("https://x.com/a?b=1&amp;c=2", footer)
        self.assertIn("#", footer)
        self.assertFalse(any("&amp;amp;" in h for h in footer))


class GeneratedPages(unittest.TestCase):
    def test_no_absolute_home_paths_ship_in_a_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            decision(ws / "brain" / "decisions", "2026-09-15-a-decision", "A decision",
                     "2026-09-15")
            self.assertEqual(run(ws, "feed.py").returncode, 0)
            html = (ws / "brain" / "feed.html").read_text()
            for href in re.findall(r'href="([^"]*)"', html):
                self.assertFalse(href.startswith("/Users/") or href.startswith("/home/"),
                                 f"absolute path in a shipped page: {href}")


class Freshness(unittest.TestCase):
    def test_last_touched_keeps_the_time_of_day(self):
        import doctor
        values = list(doctor._last_touched().values())
        self.assertTrue(values, "no files timestamped")
        # Date granularity silences the freshness report for the rest of any day on which
        # now.md was rewritten — which is exactly when a long session drifts.
        self.assertTrue(all(len(v) == 19 and "T" in v for v in values), values[:3])


class Migration(unittest.TestCase):
    def repo(self, tmp: Path) -> Path:
        ws = workspace(tmp)
        subprocess.run(["git", "init", "-q", "."], cwd=str(ws), check=True)
        subprocess.run(["git", "add", "-A"], cwd=str(ws), check=True,
                       capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "init"], cwd=str(ws), check=True,
                       capture_output=True)
        return ws

    def test_every_citation_form_survives_the_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            d = ws / "brain" / "decisions"
            decision(d, "0007-the-portal-is-live", "0007 — The portal is live", "2026-03-04")
            (d / "0008-we-use-linear.md").write_text(
                "---\ntags: [process]\n---\n# 0008 — We use Linear\n"
                "Date: 2026-03-05 · Status: superseded by 0007\n"
                "## Context\nFrom 0007, [[0007]] and [[0007-the-portal-is-live]].\n"
                "## Decision\ny\n## Consequences\nz\n")
            subprocess.run(["git", "add", "-A"], cwd=str(ws), capture_output=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "d"], cwd=str(ws), capture_output=True)

            out = run(ws, "redate.py", "--apply")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("every rewritten link verified", out.stdout)

            self.assertTrue((d / "2026-03-04-the-portal-is-live.md").exists())
            moved = (d / "2026-03-05-we-use-linear.md").read_text()
            self.assertEqual(moved.count("[[the-portal-is-live]]"), 4)
            self.assertNotIn("0007", moved)
            # The file's own heading is not a citation, and must not become one.
            head = (d / "2026-03-04-the-portal-is-live.md").read_text()
            self.assertIn("# The portal is live", head)
            self.assertNotIn("[[", head.split("\n")[3])

    def test_a_dirty_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            decision(ws / "brain" / "decisions", "0007-x", "0007 — X", "2026-03-04")
            out = run(ws, "redate.py", "--apply")
            self.assertEqual(out.returncode, 1)
            self.assertIn("uncommitted", out.stdout)

    def test_running_it_twice_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            decision(ws / "brain" / "decisions", "0007-x", "0007 — X", "2026-03-04")
            subprocess.run(["git", "add", "-A"], cwd=str(ws), capture_output=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "d"], cwd=str(ws), capture_output=True)
            self.assertEqual(run(ws, "redate.py", "--apply").returncode, 0)
            before = sorted(p.name for p in (ws / "brain" / "decisions").glob("*.md"))
            run(ws, "redate.py")
            after = sorted(p.name for p in (ws / "brain" / "decisions").glob("*.md"))
            self.assertEqual(before, after)
            self.assertEqual(before, ["2026-03-04-x.md"])


class Projects(unittest.TestCase):
    TWO = [("portal", "Client Portal"), ("bio", "BioVentures")]

    def test_one_project_asks_for_no_tagging(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            decision(ws / "brain" / "decisions", "2026-09-15-a", "A", "2026-09-15")
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 0, out.stdout)
            self.assertIn("one project", out.stdout)

    def test_two_projects_require_a_key_on_every_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp), self.TWO)
            decision(ws / "brain" / "decisions", "2026-09-15-a", "A", "2026-09-15")
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("name no project", out.stdout)

    def test_an_invented_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp), self.TWO)
            decision(ws / "brain" / "decisions", "2026-09-15-a", "A", "2026-09-15",
                     project="marketing")
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("unknown project", out.stdout)

    def test_all_is_accepted_and_the_run_goes_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp), self.TWO)
            decision(ws / "brain" / "decisions", "2026-09-15-a", "A", "2026-09-15",
                     project="all")
            decision(ws / "brain" / "decisions", "2026-09-16-b", "B", "2026-09-16",
                     project="portal")
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 0, out.stdout)

    def test_the_feed_separates_the_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp), self.TWO)
            items = (ws / "brain" / "feed-items.md")
            items.write_text(items.read_text().replace("## BAR", """## FEED-2 · 2026-09-12 · awaiting-you

**Who signs the wordmark?**
project: bio
owner: Tester
blocks: the identity stage

Body.

## FEED-1 · 2026-09-11 · awaiting-you

**Which nav shape?**
project: portal
owner: Tester
blocks: the screens

Body.

## BAR"""))
            self.assertEqual(run(ws, "feed.py").returncode, 0)
            html = (ws / "brain" / "feed.html").read_text()
            self.assertIn('data-pf="portal"', html)
            self.assertIn('data-pf="bio"', html)
            self.assertIn('data-project="portal"', html)
            self.assertIn('data-project="bio"', html)
            self.assertIn("Client Portal", html)

    def test_an_untagged_feed_item_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp), self.TWO)
            items = (ws / "brain" / "feed-items.md")
            items.write_text(items.read_text().replace(
                "## BAR",
                "## FEED-1 · 2026-09-11 · awaiting-you\n\n**Which nav?**\nowner: Tester\n"
                "blocks: the screens\n\nBody.\n\n## BAR"))
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("names no project", out.stdout)


class Slugs(unittest.TestCase):
    def test_two_records_may_not_share_a_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            d = ws / "brain" / "decisions"
            decision(d, "2026-09-15-the-same-thing", "One", "2026-09-15")
            decision(d, "2026-10-01-the-same-thing", "Two", "2026-10-01")
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("share the slug", out.stdout)


class Spread(unittest.TestCase):
    """The exploration page exists so taste acts on the work rather than on the prose about
    it, which only holds while the work gets most of the page."""

    FILE = """---
tags: [concept]
---
# 2026-09-17 · A topic
Seed: abc123 · Brief: something

Content: Headline · A real paragraph. · LABEL · 18:00 · Do the thing

## Directions
### A — First
One line of thesis.

```specimen
<style>body{background:#fff;color:#111}</style>
<h1>Headline</h1><p>A real paragraph.</p>
```

Verdict: live — works

### B — Second
Another line.

```specimen
<style>body{background:#111;color:#eee}</style>
<h1>Headline</h1><p>A real paragraph.</p>
```

Verdict: rejected — no
"""

    def render(self, tmp):
        ws = workspace(Path(tmp))
        (ws / "brain" / "explorations" / "2026-09-17-a-topic.md").write_text(self.FILE)
        out = run(ws, "spread.py")
        self.assertEqual(out.returncode, 0, out.stderr)
        return (ws / "brain" / "explorations" / "2026-09-17-a-topic.html").read_text()

    def test_every_direction_and_its_specimen_reach_the_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = self.render(tmp)
            self.assertIn("First", html)
            self.assertIn("Second", html)
            self.assertEqual(html.count("<iframe"), 2)
            # A rejected direction stays on the page. Hiding it would make the page disagree
            # with the record, which is the reason the file keeps rejected directions at all.
            self.assertIn("rejected", html)

    def test_the_specimen_frame_is_not_a_fixed_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = self.render(tmp)
            # Regression guard for the layout the owner asked to change: a fixed short frame
            # plus a reserved five-line prose block spent as much of each card on commentary
            # as on the design being judged.
            self.assertIn("aspect-ratio", html)
            self.assertNotIn("min-height:calc(5 *", html)


class Ownership(unittest.TestCase):
    """The classification `/update` acts on. Getting one of these wrong writes a template
    placeholder over somebody's real work, which is the failure the whole mechanism exists to
    prevent — so every path the owner would care about is pinned here by name."""

    def check(self, want, paths):
        for rel in paths:
            self.assertEqual(upstream.classify(rel), want, rel)

    def test_the_owners_work_is_never_read_from_upstream(self):
        self.check("project", [
            "brain/now.md", "brain/tasks.md", "brain/plan.md", "brain/project-brief.md",
            "brain/feed-items.md", "brain/open-questions.md", "brain/glossary.md",
            "brain/sources.md", "brain/workspace.toml",
            "brain/decisions/2026-09-01-a-real-decision.md",
            "brain/insights/nested/deep/note.md", "brain/explorations/2026-09-01-x.md",
            "brain/workshops/w.md", "brain/braindumps/d.md", "brain/briefings/b.md",
            "brain/drafts/mail.md", "brain/reviews/r.md", "brain/references/bar.png",
            "context/client/deck.pdf", "brain/feed.html", "archive/notes.md",
            "projects/app/src/index.ts", "projects/app/AGENTS.md",
            "brain/playground/checkout/piece.md", "brain/playground/checkout/v03-tighter.html",
            "brain/playground/checkout/shipped.html", "brain/decks/2026-10-02-pitch.html",
        ])

    def test_the_templates_machinery_is_takeable(self):
        self.check("owned", [
            "brain/doctor.py", "brain/feed.py", "brain/upstream.py",
            ".claude/skills/close/SKILL.md", ".agents/skills/update/SKILL.md",
            ".github/workflows/brain.yml", "brain/lenses/record.md",
            # These two live inside a project-owned folder and are still the template's.
            "brain/decisions/README.md", "brain/decisions/0000-decision-template.md",
            "brain/insights/README.md", ".claude/hooks/guard_push.py",
            "brain/playground.py", "brain/playground/README.md",
            "brain/playground/_canvas/canvas.js", "brain/playground/_template/piece.html",
        ])

    def test_shared_files_need_a_human(self):
        self.check("merge", [
            "AGENTS.md", "CLAUDE.md", "README.md", "brain/lenses/craft.md", "brain/tags.md",
            # `/setup` writes confidential paths into it; a wholesale overwrite un-ignores them.
            ".gitignore", ".claude/settings.json",
        ])

    def test_an_unknown_file_is_a_question_not_a_guess(self):
        # The bias that makes this safe: never OWNED by default, because the cost of a wrong
        # "owned" is destroyed work and the cost of a wrong "merge" is one question.
        self.check("merge", ["some/new/thing.md", "scripts/deploy.sh", "brain/newfile.py.bak"])

    def test_compare_never_even_looks_at_project_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            theirs = Path(tmp) / "up"
            (theirs / "brain").mkdir(parents=True)
            (theirs / "brain" / "now.md").write_text("# Now\n\ntemplate placeholder\n")
            (theirs / "brain" / "doctor.py").write_text("# upstream version\n")
            groups = upstream.compare(theirs)
            flat = [rel for g in groups.values() for rel, _ in g]
            self.assertNotIn("brain/now.md", flat)
            self.assertIn("brain/doctor.py", [rel for rel, _ in groups["owned"]])


class Repos(unittest.TestCase):
    """The two ways a workspace pushes to the wrong place: a clone still wired to the public
    boilerplate, and a product repo under `projects/` pushed on the workspace's standing
    permission."""

    def repo(self, tmp: Path) -> Path:
        ws = workspace(tmp)
        subprocess.run(["git", "init", "-q", "."], cwd=str(ws), check=True)
        return ws

    def test_every_spelling_of_a_github_url_is_the_same_repo(self):
        want = "bernardost/bp-design-agent-boilerplate"
        for url in ("https://github.com/bernardost/bp-design-agent-boilerplate.git",
                    "https://github.com/Bernardost/bp-design-agent-boilerplate",
                    "git@github.com:bernardost/bp-design-agent-boilerplate.git",
                    "ssh://git@github.com/bernardost/bp-design-agent-boilerplate/"):
            self.assertEqual(config.repo_id(url), want, url)

    def test_a_clone_still_pointing_at_the_template_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            subprocess.run(["git", "remote", "add", "origin",
                            "git@github.com:bernardost/bp-design-agent-boilerplate.git"],
                           cwd=str(ws), check=True)
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("points at the boilerplate", out.stdout)

    def test_the_projects_own_remote_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            subprocess.run(["git", "remote", "add", "origin",
                            "https://github.com/someone/their-client-brain.git"],
                           cwd=str(ws), check=True)
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 0, out.stdout)

    def test_a_product_repo_committed_as_a_bare_pointer_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            app = ws / "app"
            subprocess.run(["git", "init", "-q", str(app)], check=True)
            (app / "x").write_text("x")
            subprocess.run(["git", "-C", str(app), "add", "x"], check=True)
            subprocess.run(["git", "-C", str(app), "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-qm", "x"], check=True, capture_output=True)
            subprocess.run(["git", "add", "app"], cwd=str(ws), check=True, capture_output=True)
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("bare pointer", out.stdout)

    def hook(self, ws: Path, command: str) -> str:
        hooks = ws / ".claude" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / ".claude" / "hooks" / "guard_push.py", hooks / "guard_push.py")
        event = '{"tool_input": {"command": %s}, "cwd": %s}' % (
            json.dumps(command), json.dumps(str(ws)))
        r = subprocess.run([sys.executable, str(hooks / "guard_push.py")], input=event,
                           capture_output=True, text=True, timeout=30)
        return r.stdout

    def test_a_push_inside_a_product_repo_becomes_a_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            subprocess.run(["git", "init", "-q", str(ws / "projects" / "app")], check=True)
            for cmd in ("cd projects/app && git push origin main",
                        "git -C projects/app push"):
                self.assertIn('"ask"', self.hook(ws, cmd), cmd)

    def test_the_workspaces_own_push_passes_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.repo(Path(tmp))
            subprocess.run(["git", "init", "-q", str(ws / "projects" / "app")], check=True)
            self.assertEqual(self.hook(ws, "git push"), "")
            self.assertEqual(self.hook(ws, "git -C projects/app status"), "")


class Playground(unittest.TestCase):
    """The index and the version strip are projections of `piece.md` plus the files beside it.
    What breaks: a version file the log forgot, a final piece with no decision, a shipped piece
    with no counterpart — each of which the next session would otherwise trust."""

    def piece(self, ws: Path, slug: str, record: str, files: tuple) -> Path:
        d = ws / "brain" / "playground" / slug
        d.mkdir(parents=True)
        (d / "piece.md").write_text(record)
        for f in files:
            (d / f).write_text("<!doctype html><title>x</title>")
        return d

    def test_versions_come_from_the_files_and_notes_from_the_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            self.piece(ws, "list", "---\nstatus: current\n---\n# Reading list\nBrief: b\n\n"
                       "## Versions\n- v01 — 2026-10-01 — first\n- v02 — 2026-10-02 — second\n",
                       ("v01-first.html", "v02-second.html", "notes.html"))
            out = run(ws, "playground.py")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            js = (ws / "brain" / "playground" / "list" / "versions.js").read_text()
            data = json.loads(js.split("= ", 1)[1].rstrip().rstrip(";"))
            self.assertEqual([v["file"] for v in data["versions"]], ["v01-first.html", "v02-second.html"])
            self.assertEqual(data["versions"][1]["note"], "second")
            index = (ws / "brain" / "playground" / "index.html").read_text()
            self.assertIn("v02 · second", index)
            self.assertIn("Reading list", index)

    def test_an_unlogged_version_and_a_final_without_a_decision_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            self.piece(ws, "card", "---\nstatus: final\n---\n# Card\nFinal: v01\n\n"
                       "## Versions\n- v01 — 2026-10-01 — first\n",
                       ("v01-first.html", "v02-oops.html"))
            out = run(ws, "doctor.py")
            self.assertIn("v02 not in the version log", out.stdout)
            self.assertIn("no `Decision:`", out.stdout)
            self.assertEqual(out.returncode, 0, "bookkeeping is reported, never failed")

    def test_a_shipped_piece_needs_its_counterpart(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            self.piece(ws, "nav", "---\nstatus: shipped\n---\n# Nav\nFinal: v01\n"
                       "Decision: [[nav-is-final]]\nShipped: site · 2026-10-05\n\n"
                       "## Versions\n- v01 — 2026-10-01 — first\n", ("v01-first.html",))
            out = run(ws, "doctor.py")
            self.assertIn("no shipped.html", out.stdout)
            (ws / "brain" / "playground" / "nav" / "shipped.html").write_text("<!doctype html>")
            out = run(ws, "doctor.py")
            self.assertNotIn("no shipped.html", out.stdout)

    def test_the_template_folder_is_not_a_piece(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            d = ws / "brain" / "playground" / "_template"
            d.mkdir(parents=True)
            (d / "piece.md").write_text((BRAIN / "playground" / "_template" / "piece.md").read_text())
            out = run(ws, "playground.py")
            self.assertIn("0 piece(s)", out.stdout)


class Brand(unittest.TestCase):
    """A client's logotype was rebuilt by hand instead of taken from their PDF. Nothing can
    detect a trace by inspection, so the enforceable thing is the declaration."""

    MARK = '<svg viewBox="0 0 100 40"><path d="M 10 10 L 20 20 Z"/></svg>\n'

    def brand_dir(self, tmp):
        ws = workspace(Path(tmp))
        (ws / "brain" / "brand").mkdir()
        return ws

    def test_a_mark_with_no_source_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.brand_dir(tmp)
            (ws / "brain" / "brand" / "acme-logo.svg").write_text(self.MARK)
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)
            self.assertIn("where they came from", out.stdout)

    def test_each_declared_source_clears_it(self):
        for src in ("extracted · acme.pdf p.1 · 2026-09-17",
                    "supplied · asset pack · 2026-09-17",
                    "own-work · designed in this engagement · 2026-09-17"):
            with tempfile.TemporaryDirectory() as tmp:
                ws = self.brand_dir(tmp)
                (ws / "brain" / "brand" / "acme-logo.svg").write_text(
                    f"<!-- source: {src} -->\n" + self.MARK)
                out = run(ws, "doctor.py", "--quiet")
                self.assertEqual(out.returncode, 0, f"{src}\n{out.stdout}")

    def test_a_drawn_file_that_calls_itself_a_wordmark_is_caught_by_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.brand_dir(tmp)
            # Filename says nothing; the markup does.
            (ws / "brain" / "brand" / "mark.svg").write_text(
                '<svg><title>Acme wordmark</title><path d="M 1 1 L 2 2 Z"/></svg>')
            out = run(ws, "doctor.py", "--quiet")
            self.assertEqual(out.returncode, 1)

    def test_a_plain_asset_is_not_treated_as_a_mark(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = self.brand_dir(tmp)
            (ws / "brain" / "brand" / "grid.svg").write_text('<svg><rect width="4"/></svg>')
            self.assertEqual(run(ws, "doctor.py", "--quiet").returncode, 0)


class Promises(unittest.TestCase):
    def test_a_deferral_with_no_task_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            decision(ws / "brain" / "decisions", "2026-09-09-the-wordmark-is-drawn",
                     "The wordmark is drawn", "2026-09-09",
                     body="The wordmark is drawn, not set. One swap when the client sends "
                          "a vector.")
            out = run(ws, "doctor.py")
            self.assertIn("promises", out.stdout)
            self.assertIn("One swap when the client sends", out.stdout)

    def test_a_deferral_cited_by_a_task_is_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace(Path(tmp))
            decision(ws / "brain" / "decisions", "2026-09-09-the-wordmark-is-drawn",
                     "The wordmark is drawn", "2026-09-09",
                     body="One swap when the client sends a vector.")
            tasks = ws / "brain" / "tasks.md"
            tasks.write_text(tasks.read_text()
                             + "\n- `todo` · P1 · `design` · — — **Swap the wordmark**\n"
                               "      the-wordmark-is-drawn\n")
            out = run(ws, "doctor.py")
            self.assertIn("no unrouted deferrals", out.stdout)


class RewriteUnit(unittest.TestCase):
    def test_a_year_is_never_mistaken_for_a_decision_number(self):
        renames = {"0007": (Path("x"), "2026-03-04-a-slug.md", "a-slug")}
        text = "In 2026 we shipped, per 0007 and [[0007-a-slug]]."
        out, hits = redate.rewrite(text, renames)
        self.assertIn("In 2026 we shipped", out)
        self.assertEqual(out.count("[[a-slug]]"), 2)
        self.assertEqual(hits, 2)


class When(unittest.TestCase):
    """A reminder scheduled on the wrong day is worse than none: it replaces the owner's own
    note and then fails silently. Every case here is a phrase a person actually says."""

    # A Wednesday, deliberately — the weekday bugs hide when "now" is a Monday.
    NOW = datetime(2026, 9, 16, 18, 0)

    def r(self, phrase):
        return when.resolve(phrase, self.NOW)

    def test_a_bare_weekday_means_the_next_one(self):
        got = self.r("friday")
        self.assertEqual((got.year, got.month, got.day), (2026, 9, 18))
        self.assertEqual(got.strftime("%A"), "Friday")

    def test_next_weekday_is_the_one_after_that(self):
        self.assertEqual(self.r("next friday").day, 25)

    def test_the_same_weekday_as_today_never_means_today(self):
        # Said on a Wednesday, "wednesday" means the coming one — a reminder for a moment
        # that has already passed today is the bug, not a literal reading.
        got = self.r("wednesday")
        self.assertEqual(got.day, 23)
        self.assertEqual(got.strftime("%A"), "Wednesday")

    def test_clock_times_attach_to_the_day(self):
        self.assertEqual((self.r("friday 9am").hour, self.r("friday 9am").minute), (9, 0))
        self.assertEqual(self.r("friday 2pm").hour, 14)
        self.assertEqual(self.r("friday at 14:30").hour, 14)
        self.assertEqual(self.r("friday at 14:30").minute, 30)
        self.assertEqual(self.r("tomorrow 12pm").hour, 12)   # noon, not midnight
        self.assertEqual(self.r("tomorrow 12am").hour, 0)

    def test_a_bare_day_lands_in_the_morning_not_at_midnight(self):
        self.assertEqual(self.r("tomorrow").hour, 9)

    def test_relative_spans(self):
        self.assertEqual(self.r("in 3 days").day, 19)
        self.assertEqual(self.r("in 2 weeks").day, 30)
        self.assertEqual(self.r("in 2 hours").hour, 20)
        self.assertEqual(self.r("in 90 minutes").hour, 19)

    def test_an_explicit_date_wins(self):
        got = self.r("2026-10-01")
        self.assertEqual((got.year, got.month, got.day), (2026, 10, 1))

    def test_an_unknown_phrase_refuses_instead_of_guessing(self):
        for bad in ("the third thursday after the retro", "soon", "before the launch",
                    "when Dana replies"):
            with self.assertRaises(when.Unresolved, msg=bad):
                self.r(bad)

    def test_the_resolved_moment_is_always_in_the_future(self):
        for phrase in ("friday", "tomorrow", "in 3 days", "wednesday", "next monday"):
            self.assertGreater(self.r(phrase), self.NOW, phrase)


if __name__ == "__main__":
    unittest.main(verbosity=2)
