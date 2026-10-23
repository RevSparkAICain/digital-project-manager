# sankey-chart

Draws a Sankey flow diagram from a spreadsheet or CSV (a PNG, optionally placed on a PowerPoint
slide). The whole population starts at the left, passes through one or more grouping columns,
and ends in the final buckets at the right. Optional brackets give the count and share of a
group of neighboring buckets.

## Inputs

- A source `.xlsx` or `.csv`.
- A `mapping.json`: which sheets and rows count, first-match-wins rules that assign each row a
  node per stage, brackets and captions. Field reference: `references/spec-format.md`.
- A brand file for every color and the font: the project's `brand/brand.json` when it has
  one, otherwise the `shared/brand.json` copy.

## Outputs

- `spec.json`: the inspectable intermediate, with population and per-stage counts.
- A PNG chart, about 1790 by 1120 px.
- Optionally a `.pptx` with the chart on one slide, built on the brand template when
  `brand.json` names one.

## How to run

Run these from the skill folder (`pods/reporting/skills/sankey-chart/` in this repo,
`.claude/skills/sankey-chart/` in a rendered project):

```
python scripts/build_spec.py mapping.json spec.json
python scripts/sankey.py spec.json chart.png [--palette restrained|extended]
python scripts/to_pptx.py chart.png slide.pptx --title "..." --author "<Operator Name>"
```

`sankey.py` and `to_pptx.py` accept `--brand <path>` (or the `BRAND_JSON` environment
variable) to point at a different brand file; `build_spec.py` reads no brand
file. A worked example lives in `examples/demo/`.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Prerequisites

Python 3.9 or later with `openpyxl`, `matplotlib`, `python-pptx` and `Pillow`, installed by the
user. No network access. Finished charts go through `deliverable-reviewer` before they reach
the operator.
