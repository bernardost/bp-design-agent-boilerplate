#!/usr/bin/env python3
"""show.py — put a page or a file in front of the owner.

    python3 brain/show.py brain/feed.html                  # the default browser
    python3 brain/show.py brain/feed.html --browser safari # a named one
    python3 brain/show.py https://example.com --browser chrome
    python3 brain/show.py --reveal brain/drafts/dana.md    # select it in Finder

A page or a URL goes to a browser, never to whatever app the OS has associated with `.html`
(on a designer's machine that is often a code editor). The default browser is the one the
OS uses for web links. `--browser` takes a short name (chrome, safari, firefox, arc, brave,
edge, dia) or an app's full name. `--reveal` opens the file's folder with the file selected.

Several paths open several tabs. A path that does not exist is an error: an agent that
prints "opened" for a typo has told the owner something false.

With no screen to open on (an SSH or cloud session) it prints the paths and exits 0, so the
agent can say "you are not at the machine" rather than fail.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

MAC_APPS = {
    "chrome": "Google Chrome",
    "safari": "Safari",
    "firefox": "Firefox",
    "arc": "Arc",
    "brave": "Brave Browser",
    "edge": "Microsoft Edge",
    "dia": "Dia",
    "opera": "Opera",
    "vivaldi": "Vivaldi",
}
LINUX_CMDS = {
    "chrome": "google-chrome",
    "firefox": "firefox",
    "brave": "brave-browser",
    "edge": "microsoft-edge",
}


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://", "file://"))


def no_screen() -> bool:
    if os.environ.get("SSH_CONNECTION") or os.environ.get("CLAUDE_CODE_REMOTE"):
        return True
    if sys.platform.startswith("linux"):
        return not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return False


def mac_default_browser() -> str | None:
    """The bundle id macOS opens https links with, or None if it was never changed."""
    plist = Path.home() / (
        "Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist"
    )
    try:
        handlers = plistlib.loads(plist.read_bytes()).get("LSHandlers", [])
    except (OSError, plistlib.InvalidFileException, ValueError):
        return None
    for scheme in ("https", "http"):
        for h in handlers:
            if h.get("LSHandlerURLScheme") == scheme and h.get("LSHandlerRoleAll"):
                return h["LSHandlerRoleAll"]
    return None


def browse(targets: list[str], browser: str | None) -> int:
    if sys.platform == "darwin":
        if browser:
            app = MAC_APPS.get(browser.lower(), browser)
            cmd = ["open", "-a", app, *targets]
        else:
            # Safari is the default until the person picks another, and then the plist says so.
            cmd = ["open", "-b", mac_default_browser() or "com.apple.Safari", *targets]
        return subprocess.run(cmd).returncode
    if sys.platform.startswith("linux"):
        if browser:
            exe = LINUX_CMDS.get(browser.lower(), browser)
            return subprocess.run([exe, *targets]).returncode
        import webbrowser
        return 0 if all(webbrowser.open(t) for t in targets) else 1
    if sys.platform == "win32":
        rc = 0
        for t in targets:
            args = ["cmd", "/c", "start", "", browser, t] if browser else ["cmd", "/c", "start", "", t]
            rc |= subprocess.run(args).returncode
        return rc
    print(f"show.py: no way to open a browser on {sys.platform}", file=sys.stderr)
    return 1


def reveal(paths: list[Path]) -> int:
    rc = 0
    for p in paths:
        if sys.platform == "darwin":
            rc |= subprocess.run(["open", "-R", str(p)]).returncode
        elif sys.platform == "win32":
            subprocess.run(["explorer", f"/select,{p}"])  # explorer exits 1 on success
        elif shutil.which("xdg-open"):
            rc |= subprocess.run(["xdg-open", str(p if p.is_dir() else p.parent)]).returncode
        else:
            print("show.py: no file manager found", file=sys.stderr)
            return 1
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("targets", nargs="+", help="paths or URLs")
    ap.add_argument("--browser", "-b", help="chrome, safari, firefox, arc, brave, edge, dia, or an app name")
    ap.add_argument("--reveal", "-r", action="store_true", help="show the file in Finder instead")
    args = ap.parse_args()

    resolved: list[str] = []
    for t in args.targets:
        if is_url(t):
            if args.reveal:
                print(f"show.py: cannot reveal a URL: {t}", file=sys.stderr)
                return 2
            resolved.append(t)
            continue
        p = Path(t).expanduser().resolve()
        if not p.exists():
            print(f"show.py: no such file: {t}", file=sys.stderr)
            return 2
        resolved.append(str(p))

    if no_screen():
        print("show.py: no screen here (remote session); paths for the owner:")
        for r in resolved:
            print(f"  {r}")
        return 0

    if args.reveal:
        rc = reveal([Path(r) for r in resolved])
    else:
        # A browser gets URLs; a bare path to a non-HTML file would go to the browser's
        # file viewer, which is what the owner asked for when he named a browser.
        rc = browse([r if is_url(r) else Path(r).as_uri() for r in resolved], args.browser)
    if rc == 0:
        verb = "revealed" if args.reveal else "opened"
        for r in resolved:
            print(f"{verb}: {r}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
