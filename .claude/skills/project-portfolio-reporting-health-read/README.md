# project-portfolio-reporting-health-read

Grades how reliably a project portfolio is reported in its tracker and builds the health read
deck. Each in-scope active project is checked for a current status entry, an entry that says
something new, a reported color its own written status supports, and records that agree
about where the project sits. Judgment calls come from a judgments file the agent writes; a
missing judgment stays not judged and the grade is marked provisional. The grade measures
reporting reliability, not delivery.

## Inputs

- A tracker export JSON written by the tracker adapter (ClickUp is the reference adapter; see
  `references/tracker-adapter.md`).
- A config copied from `assets/health-read-config.example.json`.
- A roadmap pair file kept by hand, from the template `assets/roadmap-project-pairs.example.md`.
- A judgments JSON the agent writes after reading each newest status entry (optional).
- Last read's `findings.json` (optional).
- A brand file for colors and fonts: the project's `brand/brand.json` when it has one,
  otherwise the `shared/brand.json` copy.

## Outputs

- `findings.json`: per-project checks, points and grades, per-lead grades, fix lists and
  cleanup pages, the portfolio grade with its reasons, judgment requests and method notes.
- A 16:9 `.pptx` in four sections: leadership summary, team scorecard, fix list per lead,
  and a cleanup page per person.

## How to run

Run these from the skill folder (`.claude/skills/project-portfolio-reporting-health-read/`):

```
python scripts/grade_portfolio.py examples/portfolio-export.json --config examples/demo-config.json --as-of 2030-03-12 --judgments examples/judgments.json --out work/findings.json
python scripts/build_deck.py work/findings.json --out work/health-read.pptx
```

The first command exits 3 with `1 item not judged, so the grade is provisional` (one
project's color judgment is deliberately missing) and writes a file equal to
`examples/expected-findings.json`: portfolio grade C, provisional, with 2 of 10 projects not
current. The second writes an 18-slide deck. Delete `work/` afterwards.

### Flags

| Script | Flag | Meaning |
|---|---|---|
| `grade_portfolio.py` | `--config` | Health read config JSON (required) |
| `grade_portfolio.py` | `--as-of` | Read date, `YYYY-MM-DD` (required) |
| `grade_portfolio.py` | `--judgments` | Judgments JSON dated for the same read (optional) |
| `grade_portfolio.py` | `--prior` | Last read's `findings.json` (optional) |
| `grade_portfolio.py` | `--out` | `findings.json` to write; parent folder created (required) |
| `build_deck.py` | `--out` | pptx to write; parent folder created (required) |
| `build_deck.py` | `--brand` | Brand JSON; otherwise `BRAND_JSON`, then the bounded walk-up to `brand/brand.json`, then `shared/brand.json` |

Exit codes: `grade_portfolio.py` 0 complete, 1 input, config or usage error
(`<script>: usage error: ...`), 3 written with items not judged; `build_deck.py` 0 written,
1 input, brand or usage error, 4 layout check failed. Each failure is one stderr line and
writes nothing.

### Config keys

| Key | Meaning |
|---|---|
| `config_version` | Config version; a change is disclosed as a measurement change |
| `title` | Deck and findings title |
| `executive_reader_role` | Role title of the leadership summary's reader |
| `prepared_by` | Operator name for the byline and author property |
| `grade_statement` | What the grade measures and does not measure |
| `tracker` | Tracker kind, scope placeholders, folders, roadmap list, URL template, status task match, entries pulled, bot authors, automated prefixes, template prefixes |
| `leads` | Leads in display order, each with aliases |
| `lead_separator` | Separator before the lead's name in a list name |
| `status_window_days` | Day limits for current and aging |
| `status_map` | Raw task status to its state |
| `first_status` | The status a new task starts in |
| `hold_statuses` | Statuses that signal a hold |
| `queued_statuses` | Not-started statuses that mean queued |
| `state_encoding` | Color markers, hold prefix, completion marker, color field use, colors that contradict a hold |
| `newness` | Repeat look-back, placeholder phrases and their word limit |
| `roadmap` | Pair file path, leading characters to strip, roadmap status map |
| `cleanup` | Parked days, scaffold rows, RAID task match, page subtitle and bucket texts |
| `grading` | Points per outcome, project letter bands and portfolio share lines |

`SKILL.md` has every nested key, the steps, scope rules, quality checks and failure modes.
The references hold the check rules, the state encoding, grading, the tracker adapter and the
deck structure with its measured capacities.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Prerequisites

Python 3.9 or later. `grade_portfolio.py` uses the standard library only; `build_deck.py`
needs `python-pptx`. Finished decks go through `deliverable-reviewer` before they reach the
operator.
