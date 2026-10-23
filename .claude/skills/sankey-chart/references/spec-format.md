# Sankey spec and mapping reference

Two JSON documents are involved. The **mapping** is written by the author and read by
`scripts/build_spec.py`. The **spec** is what `build_spec.py` writes and `scripts/sankey.py`
draws. A spec can also be written by hand; the smallest valid one holds only `columns` and
`links`.

## Mapping keys

### Top level

| Key | Type | Rules |
|---|---|---|
| `source` | string | Required unless `--source` is given. A `.xlsx`, `.xlsm` or `.csv` path (extension case ignored). A relative path is resolved against the mapping's folder. Missing file: error. Any other extension: error asking for `.xlsx` or `.csv`. Windows drive-letter form only. |
| `sheets` | list | Required for workbooks: the sheets to load, each with its own row filters. A CSV uses only the first entry; with no entry, a CSV has no key column and an empty sheet name. A mapping with no `sheets` key at all exits 1, for a CSV too; write `"sheets": []` instead. |
| `stages` | list | Required. The chart columns, left to right. |
| `groups` | list | Optional brackets for the final column, copied into the spec unchanged. Their counts go to `_group_counts`. Adjacency is checked by the renderer, not here. |
| `palette` | string | Optional. Copied into the spec only when set. `restrained` (default), `extended`, or a new entry in `assets/palette.json`. |
| `color_by` | string | Optional, default `target`. Whether a band takes the color of its `target` node or its `source` node. |
| `label_sides` | list | Optional. One `"left"` or `"right"` per column. Default: right for the first column, left for the rest. |
| `label_columns` | list of strings | Optional. Column names used to name a row in error messages. Tried in this order: the sheet's `key_column`, these, then `Name`, `Title`, `Summary`; otherwise `<unnamed>`. |
| `title`, `subtitle`, `footer`, `prepared_by` | strings | Optional captions, empty by default. |

Other keys are ignored.

### sheets entries

- `name` (string, required): the exact sheet name. If absent from the workbook, the error lists
  the sheets that are present.
- `key_column` (string, optional): rows where this cell is blank are skipped. That removes
  spacer rows, note rows and formatted-but-empty rows. With no key column, a workbook row that
  is blank in every cell is skipped.
- `filters` (list, optional): every filter must pass for a row to count.

Reading rules: row 1 is the header and data starts on row 2. A cell is read as its stored
value, so a formula contributes its result. Columns are named by header text, never by letter.
A sheet's own `key_column` and its filter columns must exist on that sheet; otherwise the error
says the sheet (or file) has no column of that name and lists the headers found. A column used
only inside assignment rules may be missing from some sheets: there it reads as blank. A rule
column that appears on no sheet at all is treated as a typo and is an error.

A filter holds a `column` plus any of: `equals` (string), `in` (list), `not_in` (list),
`blank` (true), `not_blank` (true). Several fields in one filter all apply.

### stages entries

A stage takes one of two forms.

**Constant stage** (usually the left column): `id` (string), optional `title`, and `constant`,
an object `{node, label, color}`. Every row gets that node. `label` defaults to the node id and
`color` to `total`.

**Assigned stage**: `id`, optional `title` (defaults to the id and becomes the column
header), `nodes` and `assign`.

- `nodes` is a list of `{id, label, color}`. Only `id` is required: `label` defaults to the
  id and `color` to `neutral`. The list order is the drawn order, top to bottom.
- `assign` is an ordered list of `{when, node}`. Rules are tried in order and the first match
  wins. An empty `when` list matches every row, which makes it usable as a catch-all last rule.
- Each rule's `node` should be one the stage declares. The builder does not check this; the
  renderer then rejects the link for naming a node that is in no column.
- A declared node that ends with zero rows is removed from its column, and stderr gets
  `NOTE: node '<id>' matched no rows...`. A stage left with no nodes is an error.

### `when` conditions

All conditions in the list must hold. Several keys in one condition all apply.

- `{"sheet": "<name>"}`: the row came from that sheet.
- `{"column": "<header>", ...}` with `equals`, `in`, `not_in`, `blank: true` or
  `not_blank: true`. Text is compared with surrounding whitespace removed. An empty cell, or a
  column the row's sheet lacks, counts as blank.
- `{"stage": "<earlier stage id>", ...}` with `equals`, `in` or `not_in`: compares the node id
  an earlier stage gave the row.

Demo uses: `{"sheet": "Field Requests"}`; `{"column": "Status", "equals": "Closed"}`; and
`{"stage": "type", "in": ["hardware"]}`, which sends `In Progress` hardware tickets to the
bench bucket.

Each row adds 1 to the link between its two nodes in every pair of adjacent stages.

### Build failures (exit 1)

- No rows remain after the filters.
- Some rows match no rule in a stage. The message contains `matched no assignment rule`, gives
  the count and lists up to 20 rows as `<label> (sheet <name>) matched no rule in stage '<id>'`.
- A missing sheet or column, as described above.

## groups entries (mapping and spec)

| Key | Type | Rules |
|---|---|---|
| `label` | string | Required. The bracket heading, and the key used in `_group_counts`. |
| `nodes` | list of ids | Required. Final-column node ids; all must be in the final column and adjacent there. |
| `color` | role, `cat:<n>` or hex | Optional. Color of the bracket line and label. Default: the text color. |
| `note` | string | Optional. An italic line under the count, wrapped at about 30 characters. |

Shown values: the count is the sum of the member node totals, the total is the sum over the
final column, and the percentage is rounded to a whole number. Example, from the demo:
`{"label": "Open: desk work", "nodes": ["in_progress", "queue"], "color": "active"}`.

## Spec keys

| Key | Type | Rules |
|---|---|---|
| `columns` | list of lists of ids | Required. Left to right; each inner list runs top to bottom. An id may appear only once across all columns. The last list is the final column. |
| `links` | list | Required. Items are `{"source": id, "target": id, "value": n}`. Both ends must be in some column. A value of 0 or less is not drawn. If every node total is zero, the render fails. |
| `labels` | object, id to string | Optional display names; default is the id. Demo example: `total` shows as `All tickets`. |
| `colors` | object, id to color | Optional. Each value is a role name, `cat:<n>` or `#RRGGBB`. Missing or empty means the `neutral` role. `cat:<n>` wraps around the categorical series by modulo, and with no series it falls back to `neutral`. An unknown role is an error. |
| `column_titles` | list of strings | Optional. A header above each column, aligned to that column's label side. |
| `label_sides` | list | Optional. One entry per column (supply every one). Any value other than `"left"` acts as right. Default: right for the first column, left after it. |
| `color_by` | string | Optional, default `target`. With `target` a band takes its destination node's color; any other value uses its origin node (documented value: `source`). |
| `groups` | list | Optional brackets, as described above. When present, the plot widens on the right to make room. |
| `palette` | string | Optional palette name; a `--palette` flag on the command line wins over it. |
| `title`, `subtitle` | strings | Optional. Drawn top left; empty or absent means not drawn. |
| `footer` | string | Optional. Drawn bottom left and wrapped at about 120 characters so it stays clear of `prepared_by`. |
| `prepared_by` | string | Optional. Drawn at the lower right. |
| `_population`, `_stage_counts`, `_endpoint_counts`, `_group_counts` | records | Written by `build_spec.py` for reconciliation and ignored by the renderer. `_stage_counts` maps a stage id to its node counts, `_endpoint_counts` holds the final stage's counts, and `_group_counts` exists only when brackets do. |

## Geometry the renderer applies

- A node is as tall as the larger of its inflow and outflow. If both are nonzero and differ,
  stderr gets a `WARNING` naming the node and both values. The node is drawn at the larger
  value and nothing is rescaled.
- Thickness uses one scale for the whole chart: a band of 50 is as thick in the first gap as
  the last.
- Nodes keep their declared order; bands leave each node ordered by the declaration of the
  node at their other end.

## Render failures (exit 1)

Structural problems are collected and listed together.

| Condition | Notes |
|---|---|
| An id appears more than once across all columns | A repeat inside one column counts too |
| A link names a source or target that belongs to no column | Usually a typo, or a node the builder removed for having zero rows |
| A bracket names nodes outside the final column | |
| A bracket's members are not adjacent | Message contains `not contiguous` |
| Every link value is zero | The filters removed everything |
| A color is not a known role | Message contains `unknown color role '<name>'` and lists the valid roles; valid forms are a role, `cat:<n>` or `#RRGGBB` |
| A palette recipe points at an unset brand value and has no fallback | The message names the dotted reference |
| The palette name is unknown | The message lists the palettes available |

## Colors, roles and recipes

Resolution runs from a role name, to a palette recipe, to a brand value.

Thirteen roles exist, in two groups.

- Node and bracket roles (nine): `neutral`, `total`, `complete`, `active`, `blocked`,
  `dormant`, `excluded`, `pending_heavy`, `pending_light`.
- Text and background roles (four): `text`, `text_muted`, `text_tertiary`, `background`.

Recipe forms in `assets/palette.json`:

- `{"ref": "colors.primary"}` reads that dotted key from the brand file.
- `{"ref": "colors.textMuted", "tint": 0.4}` blends it 40 percent of the way toward white.
- `{"ref": "colors.primary", "shade": 0.3}` blends it 30 percent of the way toward black.
- `{"ref": "colors.accent1", "or": {...}}` uses the `or` recipe when the key is absent or null.

A bare string recipe counts as a ref. A brand entry shaped `{"value": "#hex", ...}` is read
through its `value`. Three-digit hex is accepted. Results are uppercase hex: a blended color
is `#RRGGBB`, and an unmodified three-digit value keeps its short form (`#abc` gives `#ABC`).

`restrained` builds on the primary, text, muted and divider colors, with generated tints and
shades. `extended` draws on `status.good`, `status.warning` and `colors.accent1` to
`colors.accent3` when set, each with a fallback to tints and shades of the primary and text
colors.

## What the PNG looks like

- PNG: a 16 by 9 inch figure at 120 dpi, tight bounding box, 0.35 inch padding: about 1790 by
  1120 px.
- Type sizes: title 25 pt bold; subtitle 13.5 pt; node labels 13 pt, with the first column at
  15 pt bold; column headers 12 pt bold; bracket label 15 pt bold and bracket count 12 pt;
  bracket note, footer and prepared-by 10.5 pt.
- Background, text and band colors come from the palette. The typeface is `fonts.office`; if it
  is not installed, the renderer prints a NOTE and draws with matplotlib's default face.
- A node's label is its display name, two spaces, then its total.
