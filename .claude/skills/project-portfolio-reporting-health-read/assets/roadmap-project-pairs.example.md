# Roadmap and project list pairs

This file tells the health read which roadmap row belongs to which project list. The read
uses it exactly as written and never pairs a list with a row on its own, so a pair that is
missing here is reported, not guessed.

How to keep it:

- Change this file in the same edit as any project being added, renamed or finished in the
  tracker.
- When a project finishes, move its row from the active table to the completed table.
- Put `no` in the Confirmed column for any pair you are unsure of. The read still shows what
  it finds for that pair, but labels it unconfirmed and does not count it.
- When a project deliberately has no roadmap row, write `(none)` in the Roadmap row column,
  so the read stops asking for one.
- The Roadmap row value must match the roadmap row name after trimming spaces, removing the
  leading characters set in `roadmap.strip_leading`, and ignoring case. Nothing else is
  matched.
- Columns are found by their header text and may appear in any order. Extra columns are
  ignored, and values may be wrapped in backticks.

## Active pairs

| List ID | Project list | Roadmap row | Confirmed |
|---|---|---|---|
| DEMO-404 | Visitor parking redesign - Sam Okafor | Visitor parking redesign | no |

## Completed pairs

| List ID | Project list | Roadmap row | Confirmed |
|---|---|---|---|
| DEMO-412 | New-starter handbook update - Sam Okafor | New-starter handbook update | yes |
