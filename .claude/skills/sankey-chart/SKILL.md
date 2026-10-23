---
name: sankey-chart
description: "Draw a Sankey flow diagram from spreadsheet or CSV rows, as a branded PNG and, when asked, a one-slide PowerPoint. Use when someone asks for a sankey or a flow diagram, wants to show how a total splits and where each part ends up, needs a funnel, a split or a multi-stage breakdown (total, then category, then status), wants summary brackets that give a count and a share for groups of end buckets, needs a chart re-rendered because the data changed, or wants it in a different palette. Band width equals row count. Not for bar charts, line charts, pie charts or trends over time."
---

# sankey-chart

Turn the rows of a spreadsheet or CSV into a multi-stage flow picture. One total node sits at
the left, one or more classification columns follow, and the final buckets stand at the right.
A band is as wide as the number of rows it carries. Optional brackets beside the last column
bundle neighboring buckets and print each bundle's count and its share of the whole.

The result is a PNG. On request it is also a one-slide `.pptx` built from that PNG.

## When to pick it

Use it when the reader needs the proportions of one population as it passes through stages,
for example "how much of the intake is finished, how much is parked with someone else, how much
is still open". If the reader only needs single counts, a table is the better tool; say so.

## Inputs

- A source file: `.xlsx`, `.xlsm` or `.csv`.
- A `mapping.json` that the author writes. Its fields are listed in
  `references/spec-format.md`.
- A spec JSON can also be written by hand. That skips the source file and the mapping.
- A brand file. Every color and the chart font come from it; the scripts hold no color and no typeface.

## Where files come from

Brand values are read in two tiers:

- Tier 1: the project's own file, if present: `brand/brand.json`.
- Tier 2: otherwise, this folder's shared/ copy: `shared/brand.json`.

A `--brand` path given on the command line, or a `BRAND_JSON` setting in the environment,
takes priority over both tiers.

The full order used by `scripts/brand_palette.py`, matching `docs/architecture.md`:

1. `--brand <path>`. A missing file is an error that names the path.
2. `BRAND_JSON`. A missing file is an error that names the path.
3. `brand/brand.json`, searched while walking upward from the scripts folder. The walk stops
   at the project root, the nearest ancestor that holds a `pods/` or `.claude/` folder. With
   no project root, this step searches nothing.
4. `shared/brand.json` inside the skill folder.
5. Nothing found: an error telling the user to pass `--brand` or set `BRAND_JSON`.

`build_spec.py` reads no brand file. Only `sankey.py` and `to_pptx.py` do.

Brand keys in use:

| Key | Used for |
|---|---|
| `colors.*`, `status.*` | Every chart color, reached through the recipes in `assets/palette.json` |
| `fonts.office` | Chart text and slide body text |
| `fonts.officeHeading` | Slide title; falls back to `fonts.office` |
| `colors.text`, `colors.textMuted` | Slide title and takeaway colors |
| `templates.pptx` | Slide template |

To create or refresh the brand file, use the `brand-extract` skill. Every chart follows the
new file on its next render.

## Steps

1. **Look at the source before mapping.** Count the rows on each sheet. List the distinct
   values in every column the mapping will use. Compare the totals with the figure the
   operator (the person running the session) expects. Settle with the operator which rows are
   in, which are out and why, and whether any record appears twice under two keys, because
   double counting cannot be seen in the finished picture. The demo's `Escalations` sheet is
   the worked case; see `examples/demo/README.md`.
2. **Write the mapping.** Copy `examples/demo/mapping.json` and edit it. Assignment rules are
   tried from the top and the first hit wins, so the overriding rule goes first. A row that no
   rule catches stops the build, so nothing is dropped quietly. A relative `source` is read
   relative to the folder that holds the mapping file.
3. **Produce the spec.**

   ```
   python scripts/build_spec.py tickets-mapping.json tickets-spec.json [--source <file>]
   ```

   The console prints the population, the total for each final bucket and the total for each
   bracket. Reconcile them with the source before drawing anything; a mapping fix costs least
   at this point.
4. **Render the PNG.**

   ```
   python scripts/sankey.py tickets-spec.json tickets-chart.png [--palette restrained|extended] [--brand <brand.json>]
   ```

5. **Open the PNG and look at it.** A zero exit only says the script finished. Look for
   labels touching or overprinting, a bucket you cannot read, bracket labels running
   together, the footer crowding the prepared-by stamp, and a band so thin it vanishes. A
   font NOTE on stderr means a substitute face with different widths, so recheck labels.
6. **Make the slide, only when asked.**

   ```
   python scripts/to_pptx.py tickets-chart.png tickets-slide.pptx [--template <deck.pptx>] [--title "..."] [--takeaway "..."] [--author "<Operator Name>"] [--layout <name>] [--brand <brand.json>]
   ```

   Then send the result to review (see Handoffs).

Each step writes its result to disk, so you can pause after any step, edit, and resume; the
spec is the hand-off between builder and renderer.

## Flags

`build_spec.py <mapping> <out_spec>`

| Flag | Meaning |
|---|---|
| `--source` | Replaces the mapping's `source` (`.xlsx` or `.csv`). Default: none. A relative path here is used as given, from the current folder, unlike the mapping's own `source`. |

`sankey.py <spec> <out_png>`

| Flag | Meaning |
|---|---|
| `--palette` | Palette name from `assets/palette.json`. Beats the spec's `palette`. Default: none, so the spec's value applies, else the file's default (`restrained`). An unknown name is an error that lists the palettes available. |
| `--brand` | Brand JSON path. Default: none, so the lookup order above applies. |

`to_pptx.py <png> <out_pptx>`; every option defaults to empty.

| Flag | Meaning |
|---|---|
| `--template` | Base `.pptx`. A missing file is an error. It is copied to the output path first, so the template is untouched and any slides already in it stay. |
| `--title` | Text at the top of the slide: 28 pt bold, `colors.text`, heading face. |
| `--takeaway` | One line under the title: 14 pt, `colors.textMuted`, body face. |
| `--author` | Sets the deck's author and last-modified-by properties. |
| `--layout` | Layout name, matched without regard to case. If it is not found, stderr gets a NOTE listing the layouts and the fallback applies. The fallback, which is also the default, is the layout with the fewest placeholders. Every placeholder is removed from the new slide. |
| `--brand` | Brand JSON path. |

Template order: `--template`, then `templates.pptx` from the brand file (resolved against the
folder that holds the brand file; absolute paths are used as given), then a blank 13.333 by
7.5 inch deck. If the brand file names a template that is absent, stderr gets a NOTE containing
the word "missing" and the blank deck is used. The picture is placed inside 0.5 inch margins
below the title and takeaway, keeps its proportions and is centered. A missing PNG is an error.

Exit codes, all three scripts: bad or absent arguments print the usage text on stderr and exit
2. Any other failure prints one message on stderr and exits 1; `build_spec.py` messages start
with `build_spec: `. Notes and warnings on stderr leave the exit code at 0.

## Editorial rules

- **Node order.** The renderer draws nodes exactly where you list them and never moves one
  to reduce crossings.
- **Band order.** Within a node, bands leave in the order their other ends are listed, so
  swap far-end nodes to untangle.
- **Demo.** In the demo, finished buckets sit above open ones, and `Hardware` is listed last
  because it alone feeds `On the repair bench`, the bottom bucket, so its band runs
  straight.
- **Brackets.** A bracket covers neighboring final buckets. It shows its label, then
  `<count> of <total>` with a whole-number percentage, then an optional italic note. Members
  must be neighbors in the last column; a split group is rejected at render time. Fix it by
  reordering the column or by splitting the bracket. Counts and percentages are computed,
  never typed.
- **Palette choice.** `restrained` is the default and suits internal work up to about seven
  final buckets. `extended` brings in the brand's accent and status colors when the brand file
  has them, for charts that need more separation. When `extended` is used, give the reason in
  the footer or the hand-off note. A new palette is a new entry in `assets/palette.json`, with
  no script change.
- **Color references.** In a mapping or spec, prefer a role name or `cat:<n>`. A literal hex
  value bypasses the palette and the brand, so a brand change has no effect on it. A
  misspelled role stops the render and lists the valid roles.

## Guardrails

- Every number comes from the source. When a row is ambiguous, ask; never guess.
- Write the footer so a reader can check the chart: source, what was left out, and the rule
  order.
- On Windows pass `C:/data/tickets.xlsx`, never `/c/data/tickets.xlsx`; Windows Python reads
  the second as a folder under the current drive root, so every script rejects it for any
  drive letter.
- Final files: `<WORKSPACE_ROOT>/deliverables/Sankey - <Subject> - <YYYY-MM-DD>.png` (and
  `.pptx`), `<WORKSPACE_ROOT>` being the install folder holding `brand/`; working files stay
  in scratch.
- Put the operator's name on the work: both the `prepared_by` caption and `--author` take the
  name of whoever is running the session, looked up at run time and never written into a file
  ahead of time.

## Outputs

- `spec.json`: UTF-8 JSON with a one-space indent. It holds the chart keys plus four record
  keys used for reconciliation.
- `build_spec.py` prints, in order: `population: <n>`; one line per final bucket, highest
  count first; one `[group]` line per bracket label; then the output path. On the demo that is
  population 400, then done 200, in_progress 55, queue 45, waiting 40, then bench, canceled
  and duplicate at 20 each, then bracket totals 240, 40, 100 and 20.
- The PNG is a 16 by 9 inch figure at 120 dpi, saved with a tight bounding box and 0.35 inch
  padding: about 1790 by 1120 px (1792 by 1126 measured with Arial; the exact size depends on
  the typeface). The script prints the output path.
- The `.pptx` is the template copy, or a blank deck, plus one added slide. The script prints
  the output path.
- Node labels read as the display name, two spaces, then the node's total.
- Chart type sizes are in `references/spec-format.md`; slide title and takeaway sizes are in
  the `to_pptx.py` flag table above.

## Quality checks

- Reconcile the printed counts with the source before rendering (step 3).
- Inspect the picture by eye (step 5).
- Each stage boundary carries the whole population: a middle node sends out what it takes in,
  and the final buckets, like the brackets, each add up to the population. `build_spec.py`
  prints the counts; on the demo they must equal `examples/demo/expected-counts.json`.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_spec.py` | Mapping and source into `spec.json` |
| `scripts/sankey.py` | Spec into PNG |
| `scripts/to_pptx.py` | PNG into a one-slide deck |
| `scripts/brand_palette.py` | Brand file lookup and palette resolution |
| `assets/palette.json` | Named palettes, written as recipes against the brand file |
| `references/spec-format.md` | Every mapping and spec key, and the validation rules |
| `examples/demo/` | Synthetic ACME Co. ticket data, mapping, expected counts and expected spec |

## Requirements

`openpyxl` for workbook input, `matplotlib` for drawing, `python-pptx` and `Pillow` for the
slide step. Python 3.9 or later. No network access and no plotting service.

## Handoffs

- Send the finished PNG or slide to the `deliverable-reviewer` agent, which runs the
  `deliverable-review` skill, before the operator sees it.
- To refresh the brand file, use the `brand-extract` skill.
