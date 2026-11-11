# Lens · house

*How anything generated for the owner should look: `feed.html`, `brief.html`, the exploration
spreads, the desk, a rendered page or document. `/reviewer house <scope>`, and the standard a
renderer is built to.*

**This governs artifacts made for the owner only.** It is not the product's
aesthetic and is never inherited by the work. What a project should look like is a project
decision, explored with `/explore` and judged against `brain/lenses/craft.md`. Applying these
rules to the work by default would substitute the workspace's taste for the project's.

The writing rules for these pages are not here. They live in `AGENTS.md`, because they also
govern every reply and everything that goes to a client.

The style comes from the owner's own business documents: a modernist three-column grid, set
entirely in one typeface at two weights, black on white, with no colour, no boxes, no images
and no logo. Structure comes from black rules, hairlines, and where things sit on the grid.
It should read like an architect's or a type foundry's paperwork: calm, exact and finished.
^[owner · session · 2026-11-06]

**Decide first which kind of page it is.** A page that is **read** (a feed, a report, a
document) follows section 1. A page that is **used** (the reader has to type, choose,
confirm or rank: the brief, a workshop, a review round, an intake sheet) follows section 2 on
top of section 1. The read style is too quiet for a page that is used: a page made only of
hairlines does not show where to write, where a section ends or how much is left, so the
reader either scans past the fields or stops.

## 1 · Every page

**Type.** Geist only, at two weights: 400 for everything, about 560 for titles and emphasis,
never 700. Fallback `"Helvetica Neue", Arial, sans-serif`. No second family and no italics.
Tight tracking is part of the look, and larger type is tracked tighter. Figures are tabular
wherever numbers stack. Sentence case everywhere: no all-caps labels, no letterspaced
uppercase. Load it from Google Fonts (`family=Geist:wght@100..900`) or a local file.

**Colour.** White paper, ink `#0a0a0a`, never pure black and never tinted paper. Everything
secondary (labels, notes, dates, sub-lines) is grey `#737373`; hierarchy comes from grey
against black and from size, not from weight. Hairlines `#dedede`. Commit to light: no
`prefers-color-scheme` block that flips the page dark. The status tags below are the only
other colour, on every page.

**Grid.** Three columns on every row: the **label** on the left (a section number, a row
label, a code), the **content** in the middle, the **aside** on the right (amounts, dates,
status), right-aligned. Every row is the same CSS grid, so the middle column aligns down the
whole page. Never centre anything. A lede spans the middle and right columns together. On
screen: `--cols: 180px 1fr 170px`, `--gap: 48px`, side margin 56px, max width 1200px; one
column below 760px.

**Structure.** Three elements build every page:

- **Section head**: a black rule across the full width, then the section number (560) on the
  left, the title (560) over a one-line grey subtitle in the middle, an optional grey note on
  the right. The page head uses the same pattern: document number, type over subject, dates.
- **Item row**: a grey hairline on top; a small grey code over the item's name on the left,
  the description in the middle, the amount or status on the right.
- **Total or closing row**: a black rule on top.

Black rules start a section or close a sum; grey hairlines separate items inside it. No boxes,
cards, shading, rounded corners, shadows, or icons outside the status tags.

**Status is a tag, and it looks the same on every page**: a tinted fill, a darker word and a
small line icon. *Open* is grey with an empty circle, *Our guess* amber with a dashed circle,
*Needed* red with an exclamation mark (*Waiting on you*, *Not met*), *Done* green with a tick
(*Answered*, *Met*, *Live*, *Final*), *Not applicable* plain grey with a dash (*Rejected*). The
CSS is `TAG_CSS` in `brain/feed.py`; every renderer uses it, so a status never gets a second
look. Grey squares on one page and coloured tags on another made the owner learn two
vocabularies for one idea. ^[owner · session · 2026-11-06]

**Rhythm.** The page should look about a third empty. Where space is short, cut content
before tightening the spacing.

**Diagrams** use the same means as the text: solid black bars for work, light grey `#d4d4d4`
for someone else's turn, small grey labels on hairlines. No colour, no legend box.

**Evidence is present and quiet.** Where a page states something from outside this repo, the
source is one hover away and never in the sentence: a small grey superscript numeral, the full
attribution at the foot.

## 2 · Pages that are used

Everything in section 1 carries over: Geist, the three columns (label · content · status), the
page head, black rules for structure, grey for anything secondary. These change:

1. **A fill means "write here", and only a field has one.** Every field, option row, chip and
   rank row sits on a light warm grey `rgb(241,241,239)`, with a darker bottom edge
   (`#8a8a8a`) on text fields. Text that is only for reading never sits on a fill, so the
   reader can tell at a glance which parts are theirs.
2. **A dashed outline means "our guess".** A proposed answer arrives in a dashed box
   (`#9a9a9a`) with two real buttons, *Keep it* (black) and *Change it* (outlined). Keeping it
   turns the outline solid ink; changing it turns the box into a text field holding our
   wording.
3. **Answered fields turn white with an ink edge.** The page gets calmer as it fills in, and
   that change is itself the progress report.
4. **Sections start with a band and end with a rule.** The band is white, between a black rule
   above and a hairline below, holding the section number, a 30px title, a grey subtitle and a
   count ("2 of 4"), and it sticks under the top bar while its section scrolls. Each section
   closes with a black rule and one grey line saying what comes next.
5. **A sticky top bar** shows the document name, overall progress as a thin black line with a
   count, and the one main action.
6. **Status sits in the right column as a tag** (section 1), plus who can answer. Outside
   the tags, red `#c8102e` still marks only what is needed and still empty. A row of grey
   square markers made the owner read every line to find what needed him.
   ^[owner · session · 2026-11-06]
7. **Buttons look like buttons.** Black filled for the main action, a 1px ink outline for the
   alternative, square corners. Never text links standing in for actions.
8. **Controls match the shape of the answer**: full-width option rows for one choice, chips
   for "pick three", rows with up and down buttons for ranking, sliders with both ends
   labelled and our guess marked beneath, a text field only where the reply is a sentence
   only they have.
9. **Screen sizes, and air that matches the job.** 16px body and field text (phones zoom on
   anything smaller), 13px labels, one column below 760px with the status under the control.
   **A long page the reader types into** (the brief, a workshop) gets the full air: 20px
   questions at weight 520, 52px tap targets, 80px above and below each question, 28px
   between a question and its control, 160px between sections, a 600px measure. **A page
   where each answer is a tap or a line** (the feed, a review round, a note on the desk)
   stays compact: rows about 28px apart, 44px targets, the same fill and the same rules.
   ^[owner · session · 2026-11-06]
10. **Saving is visible.** "Saved" under a field after each edit, and no final submit the
    answers depend on.

The playground's control panel is the one dark surface: it sits on top of the work, which is
usually white. It still uses Geist, sentence case and square corners.

Corners stay square and there are still no shadows or illustrations. The fill, the dashed
outline and the status tags are the only additions, and each one has a single meaning.

## 3 · Printed documents

A4 portrait with no printer margins (`@page { size: A4; margin: 0 }`); each page a fixed
`210mm × 297mm` box with `overflow: hidden`, so overflow is caught on sight. Margins 16mm left
and right, 13mm top, footer 10mm from the bottom. Grid `46mm 1fr 44mm`, gap 7mm. Sizes, and
nothing between them: body 9.2pt / 1.4, small 7.6pt, lede 15.5pt / 1.25, big 19pt / 1.08.
Section rules 0.9pt black, item hairlines 0.6pt. A footer on every page in three grey small
columns: the owner's name, the contact line, the page count. Render with headless Chrome
(`--no-pdf-header-footer --print-to-pdf`), then rasterise every page and look at it.

## 4 · What to refuse

Colour beyond the status tags and, on a used page, the one red; logos, icons outside those
tags, photographs, a second typeface, bold
700, centred titles, boxes or shaded panels, all-caps labels, decorative rules, and anything
that makes the page busier than it needs to be.

## 5 · What is explicitly not the standard here

The project's own work, a client deliverable in the client's identity, and anything the owner
has art-directed. Ask before departing from this lens; do not split the difference.

## The score

Same scale as `craft.md`. Below 7, name what is holding it back.
