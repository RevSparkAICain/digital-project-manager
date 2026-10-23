# Deck structure

`build_deck.py` builds one 16:9 pptx (13.333 x 7.5 in, 960 x 540 pt) from `findings.json`,
starting from a blank presentation every run, never from an earlier deck. The geometry lives
in `scripts/deck_layout.py`; the numbers below are the ones that file holds, and the tests
assert both agree.

## Every slide

- A section label at top left (12pt bold), a title (32pt, `fonts.officeHeading`), a divider
  rule, and a footer `<section> | page <i> of <n>` (10pt), counted within the section after
  every split.
- Speaker notes that begin `As of <as_of>.`
- Continuation slides repeat the title with ` (continued)` and the section label, and carry
  no cover line and no prepared-by line.
- No text refers to another slide by number. Cross references use titles ("see Project
  scorecard").

## The four sections, in order

### 1. Leadership summary

Self-contained for the executive reader role and kept at portfolio altitude: no task-level
detail.

- **Reporting reliability grade.** The letter in a status chip, `(provisional)` under it when
  provisional; the headline (the first portfolio reason); one line per check summarizing its
  split; a panel with two labeled parts, `What this grade measures` and `What it does not
  measure`, from `grade_statement`; and a cover line with the read date, the prior read date
  or `No prior read supplied`, the executive reader role and `Prepared by <prepared_by>`.
  When `reasons_changed` is true, a line says the letter is unchanged and the reasons
  changed. The notes list every reason and the points note.
- **Needs attention.** One card per in-scope exception in severity order: abandoned or
  absent, stale, conflicting records, misaligned, repeated, placeholder (a project's highest
  severity decides its place; ties keep the scorecard order). Each card holds the project
  name (linked), the condition and one evidence line. Above the measured capacity, the rest
  are named on one rollup line, `Also needing attention (<k>): <names>`, ending `and <m>
  more; see Project scorecard` when the names exceed the line's two lines. A closing line
  names the projects reporting well. Held projects never appear.
- **Portfolio snapshot.** Counts and linked names for active, completed and not-started
  lists; the currency split and the color split as labeled figures; held projects only as
  `Out of scope: on hold (<n>)` followed by their names, unlinked; hold-pending projects as
  `Awaiting hold judgment (<n>)`.

### 2. Team scorecard

- **Project scorecard.** A table, one row per in-scope project in ranked order. Columns and
  widths (pt): Project (linked) 175, Lead 80, Latest status (date and age in days) 110, Color
  50, Alignment 90, Newness 85, Records 70, Grade 45, Evidence 175. Provisional grades carry
  `*` with a legend line. The caption area above the footer carries `Context: <n> overdue
  tasks across in-scope lists. Not graded.`
- **Status and color detail.** Cards grouped as not current, repeated or placeholder (with
  consecutive counts and "at least" where flagged) and color conflicts (with the quote); a
  closing line names the projects reporting well. Overflow continues.
- **Method, sources and limits.** Sources, filters with raw and counted numbers, unpaired
  lists, unconfirmed pairs, missing roadmap rows, completed-pair conflicts, not judged,
  discarded judgments, count checks, measurement changes, notes, and the grade statement.
  Each sub-heading keeps its lines together and moves whole to the next slide when it does
  not fit.

### 3. Fix list per lead

- **Fix list by lead.** One group per owner (config order, then `Unattributed`), each line the
  linked project name and the correction. No date and no priority column. Closes with
  `Closed since the prior read`, listing the closed lines, or saying `None.` or `No prior
  read supplied.`
- **Corrections by project.** A table with columns Project (linked) 220, Who corrects 170 and
  Correction 490. Where owners differ within one project, every owner is named and each
  correction line names its owner. Closes with `Nothing needed this read: <names>`.

### 4. Cleanup per person

One page per configured lead, in config order, titled `Cleanup: <lead name>`, with the
`cleanup_subtitle` text under the title, identical on every cleanup page.

- The first page opens with `What to fix (<n>)` and a numbered list of summary lines, each
  with the linked project name. Bucket sections follow: a heading with the label and count,
  then its definition and remedy, then the task lines.
- A continuation keeps the summary on the first page. A bucket that continues repeats its
  heading with ` (continued)` and its definition and remedy, so a forwarded page always
  carries the ask.
- A clean lead gets a page that says there is nothing to correct this read.

## Measure the asset

Card and row capacity is measured from the layout, never guessed and never tuned per run.

1. Lay out one card or row at the intended type sizes and padding.
2. Measure its height, the gap to the next one, and the vertical band available between the
   first card's top and the top of the panel or footer below.
3. Capacity is the largest whole number of cards whose tops plus heights stay inside the
   band: `floor((band + gap) / (height + gap))`.
4. Record the measured numbers beside the layout and assert them in tests.
5. Re-measure only when the layout or type sizes change, never per run, and never by
   tightening the pitch to admit one more card.

Worked example with invented numbers: a 300pt band, 80pt cards and a 20pt gap give
`floor(320 / 100) = 3` cards; a fourth would end at 380pt, past the band.

Measured for the Needs attention slide:

| Quantity | Value | From |
|---|---|---|
| First card top | 92pt | `CARD_TOP`, the body top |
| Card height | 61.6pt | 8pt padding top and bottom, a 14pt name line and two 12pt lines at 1.2 line height |
| Gap | 10pt | `CARD_GAP` |
| Band bottom | 414.4pt | The body bottom (500pt) less two 30.8pt foot lines (rollup and closing) and three 8pt gaps |
| Capacity | 4 | `floor((322.4 + 10) / (61.6 + 10)) = 4`; the fourth card ends at 368.4pt, a fifth would end at 440pt |

A card's name holds one line; a name longer than that line stops the build with exit 4
rather than shrinking. The only fix is a shorter list name in the tracker; the error shows
the limit. The evidence line holds one line; longer evidence is cut at a word
with ` ...`, and the full text appears on Status and color detail and the scorecard.

## Overflow

- **Needs attention:** the top-severity items get cards and the rest are named on the rollup
  line with a count. This is altitude, not fit: the executive page stays one page.
- **Everywhere else:** the slide continues on a new slide with ` (continued)` in the title,
  the table header row repeated, and the page counters renumbered within the section.

## Type floors and the wrapped-text estimate

- Titles 32pt; section labels 12pt; headings 14 to 16pt; body 12 to 14pt; table cells 11pt;
  captions and footers 10pt. Floors: body 12pt, table cells 11pt, captions, labels and
  footers 10pt. No text box uses shrink-on-overflow.
- Height estimate: characters per line = width / (0.55 x font size), or 0.6 for bold text;
  greedy word wrap; height = wrapped lines x font size x 1.2, plus padding.
- Tables paginate on estimated row heights: each row is as tall as its most-wrapped cell
  plus 3pt padding top and bottom (4pt left and right). A table continues when the next row
  would cross the band bottom: 466pt on the scorecard (above a 26pt caption area and an 8pt
  gap), 500pt elsewhere. A single row taller than a whole band stops the build with exit 4.
- The estimate is deliberately wide, so rendered text sits inside its box with room to
  spare in PowerPoint.

## Bounds sweep

After building, every shape on every slide is checked: left and top non-negative, right edge
within the slide width, bottom within the slide height, tables measured by the sum of their
row heights. Any violation exits 4 and nothing is written. A visual pass misses small
overlaps and names cut off at the edge, so the sweep is the check; look at the deck as well
before the review gate.

## Color and contrast

- Titles and body text in `colors.text`; secondary text in `colors.textMuted`; dividers in
  `colors.divider`; panels, cards and the table header in `colors.surface`; links in
  `colors.link`.
- Any color used for text must reach 4.5:1 contrast with its background (WCAG relative
  luminance). The deck has one link style: `colors.link` when it reaches 4.5:1 on both the
  background and the surface, otherwise `colors.text`. Every link is underlined, because
  PowerPoint always underlines links; the brand's `linkUnderline` preference cannot be
  honored. A muted or section-label color that fails falls back to `colors.text`. Link runs
  carry a marker telling PowerPoint to draw them in the run's own color rather than the
  theme's hyperlink color.
- Status colors (`status.good` for A and B, `status.warning` for C, D and F) are used only as
  the grade chip's fill, never as text; a null status color is replaced by
  `colors.textMuted`, and the chip label takes whichever of `colors.text` and
  `colors.background` contrasts more with the fill. No red or critical tone is used: findings
  are record corrections, not alarms.

## Writing rules for lead-facing pages

- Address the reader directly ("your lists").
- A heading states the record's condition, never a judgment of the person.
- No rankings of leads.
- A clean record gets a page that says so.
- Every project name links to its list.

## Out of scope

The deck carries no dates view, no task-tidiness slide and no record register beyond the fix
list.
