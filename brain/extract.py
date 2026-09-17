#!/usr/bin/env python3
"""extract.py — get brand assets *out* of a PDF instead of redrawing them.

    python3 brain/extract.py context/brand-guidelines.pdf
    python3 brain/extract.py <pdf> --page 4 --svg      # that page as vector
    python3 brain/extract.py <pdf> --images            # every raster image
    python3 brain/extract.py <pdf> --spec              # colours, fonts, the written rules

**Why this file exists.** An assistant asked to use a client's brand guidelines rebuilt their
logotype by hand — traced it in code rather than taking the real one. That is the worst thing
a design agent can do with a brand. A redrawn mark is wrong in ways nobody catches in review:
the curve is off, the spacing is not theirs, the weight is close. It looks plausible enough to
ship, and it is the client's trademark.

The excuse it runs on is that extracting felt hard and drawing felt easy. So this makes
extracting easy. A logo in a brand PDF is nearly always vector, and `pdftocairo -svg` brings it
out as vector — not a screenshot of it, not an approximation of it, the actual paths.

Needs poppler (`brew install poppler`). Where it is missing the answer is still not to draw
the thing: it is to ask the owner for the asset pack, which every brand guideline ships with.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
OUT_ROOT = BRAIN / "brand"

NEEDED = ("pdfimages", "pdftocairo", "pdftotext")
# Brand PDFs spell colour every way there is, and eyeballing a hex off a rendered page is the
# same mistake as redrawing the mark — close, and not theirs.
COLOUR = re.compile(
    r"(#[0-9A-Fa-f]{6}\b)"
    r"|\b(?:CMYK|cmyk)[:\s]*([\d]{1,3}\s*[/,]\s*[\d]{1,3}\s*[/,]\s*[\d]{1,3}\s*[/,]\s*[\d]{1,3})"
    r"|\b(?:RGB|rgb)[:\s]*([\d]{1,3}\s*[/,]\s*[\d]{1,3}\s*[/,]\s*[\d]{1,3})"
    r"|\b(PANTONE|Pantone)\s+([0-9]+\s*[A-Za-z]*)")


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def run(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def inventory(pdf: Path) -> None:
    """What is in here, and on which page — so the next command is precise rather than a sweep."""
    print(f"extract — {pdf.relative_to(ROOT) if pdf.is_relative_to(ROOT) else pdf}\n")
    if have("pdfimages"):
        r = run(["pdfimages", "-list", str(pdf)])
        lines = [ln for ln in r.stdout.splitlines()[2:] if ln.strip()]
        print(f"  raster images   {len(lines)}")
        for ln in lines[:8]:
            f = ln.split()
            if len(f) > 4:
                print(f"    page {f[0]:>3}  {f[3]}x{f[4]}  {f[2]}")
        if len(lines) > 8:
            print(f"    … and {len(lines) - 8} more")
        if not lines:
            print("    none — the marks are vector, so --svg is the route, not --images")

    if have("pdftotext"):
        text = run(["pdftotext", "-layout", str(pdf), "-"]).stdout
        # pdftotext emits a formfeed after every page including the last, so the count of
        # separators is the page count — adding one reports a page that is not there.
        pages = text.count("\f") or 1
        print(f"\n  pages           {pages}")
        hits = [m.group(0).strip() for m in COLOUR.finditer(text)]
        seen, uniq = set(), []
        for h in hits:
            if h.lower() not in seen:
                seen.add(h.lower())
                uniq.append(h)
        print(f"  colour values   {len(uniq)} named in the text")
        for h in uniq[:12]:
            print(f"    {h}")
        if len(uniq) > 12:
            print(f"    … and {len(uniq) - 12} more — --spec writes them all out")

    print("\n  next:")
    print("    --spec            the written rules, colours and font names, to a file")
    print("    --page N --svg    page N as vector, which is how a logo comes out intact")
    print("    --images          every raster image")
    print("\n  Nothing here licenses redrawing a mark. If the asset will not come out clean,")
    print("  ask the owner for the asset pack — brand guidelines always ship with one.")


def to_svg(pdf: Path, page: int, out: Path) -> None:
    if not have("pdftocairo"):
        print("extract: pdftocairo missing (brew install poppler). Ask for the asset pack.")
        return
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"page-{page:02d}.svg"
    r = run(["pdftocairo", "-svg", "-f", str(page), "-l", str(page), str(pdf), str(dst)])
    if r.returncode != 0:
        print(f"extract: {r.stderr.strip()[:200]}")
        return
    size = dst.stat().st_size
    print(f"  wrote {dst.relative_to(ROOT)}  ({size // 1024} KB, vector)")
    print("  Open it, isolate the mark, and keep the paths as they are. Re-drawing a path\n"
          "  you have already extracted is the same error with extra steps.")


def images(pdf: Path, out: Path) -> None:
    if not have("pdfimages"):
        print("extract: pdfimages missing (brew install poppler). Ask for the asset pack.")
        return
    out.mkdir(parents=True, exist_ok=True)
    r = run(["pdfimages", "-png", str(pdf), str(out / "img")])
    if r.returncode != 0:
        print(f"extract: {r.stderr.strip()[:200]}")
        return
    got = sorted(out.glob("img-*.png"))
    print(f"  wrote {len(got)} image(s) to {out.relative_to(ROOT)}")
    for p in got[:8]:
        print(f"    {p.name}")
    if got:
        print("  A raster logo is the fallback, not the goal — if the mark is vector in the\n"
              "  PDF, --svg keeps it vector and it will scale.")


def spec(pdf: Path, out: Path) -> None:
    """The written rules, kept verbatim. Clearspace, minimum size, what is forbidden — the
    parts of a brand guideline that get skimmed and then violated."""
    if not have("pdftotext"):
        print("extract: pdftotext missing (brew install poppler).")
        return
    out.mkdir(parents=True, exist_ok=True)
    text = run(["pdftotext", "-layout", str(pdf), "-"]).stdout
    dst = out / "guidelines.txt"
    dst.write_text(text, encoding="utf-8")
    print(f"  wrote {dst.relative_to(ROOT)}  ({len(text)} chars, verbatim)")
    rules = [ln.strip() for ln in text.splitlines()
             if re.search(r"clear\s?space|minimum size|do not|never|must not|exclusion zone",
                          ln, re.I)]
    if rules:
        print(f"\n  {len(rules)} line(s) that read as a constraint — these are the ones that")
        print("  get skimmed and then violated:")
        for ln in rules[:10]:
            print(f"    {ln[:96]}")
        if len(rules) > 10:
            print(f"    … and {len(rules) - 10} more, in the file")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  usage: python3 brain/extract.py <pdf> [--spec|--images|--page N --svg]")
        return 1
    pdf = Path(args[0])
    if not pdf.exists():
        print(f"extract: {pdf} not found")
        return 1
    missing = [t for t in NEEDED if not have(t)]
    if missing:
        print(f"extract: missing {', '.join(missing)} — `brew install poppler`.")
        print("         Until then, ask the owner for the asset pack. Do not redraw.\n")

    out = OUT_ROOT / pdf.stem
    if "--spec" in sys.argv:
        spec(pdf, out)
    elif "--images" in sys.argv:
        images(pdf, out)
    elif "--svg" in sys.argv:
        page = 1
        if "--page" in sys.argv:
            page = int(sys.argv[sys.argv.index("--page") + 1])
        to_svg(pdf, page, out)
    else:
        inventory(pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
