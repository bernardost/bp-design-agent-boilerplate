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

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
sys.path.insert(0, str(BRAIN))

import feed  # noqa: E402
import redate  # noqa: E402

SCRIPTS = ("config.py", "doctor.py", "feed.py", "brief.py", "spread.py", "render.py",
           "redate.py")
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


class RewriteUnit(unittest.TestCase):
    def test_a_year_is_never_mistaken_for_a_decision_number(self):
        renames = {"0007": (Path("x"), "2026-03-04-a-slug.md", "a-slug")}
        text = "In 2026 we shipped, per 0007 and [[0007-a-slug]]."
        out, hits = redate.rewrite(text, renames)
        self.assertIn("In 2026 we shipped", out)
        self.assertEqual(out.count("[[a-slug]]"), 2)
        self.assertEqual(hits, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
