# The four checks

Every in-scope active project is scored on four checks and nothing else. This page gives
each band, the config key behind each threshold, the rules `grade_portfolio.py` applies, and
a worked example from the ACME fixture (`examples/portfolio-export.json`, read date
2030-03-12).

## Which entries count

An entry on the status task counts as a person's entry when all three hold:

- it is not marked `is_bot: true` in the export;
- its author is not listed in `tracker.bot_authors`;
- its text does not start with an entry in `tracker.automated_prefixes`.

Only these entries feed checks 1 to 3 and the owner comparison in check 4. A reminder
posted yesterday by the tracker's automation never makes a project current. When a project
resumed after a hold, entries dated before `resumed_on` are set aside as well.

## Check 1: currency

| Band | Rule | Result |
|---|---|---|
| current | Newest entry at most `status_window_days.current` days before the read | pass |
| aging | At most `status_window_days.aging` days | minor |
| stale | Older than that | fail |
| absent | No status task, or no entry from a person | fail |

- Age is counted in whole days from the newest entry's date to `--as-of`.
- A resumed project with no entry since `resumed_on`, and resumed no more than
  `status_window_days.current` days ago, reads current with a method note.
- **Trip wire (set up and never used).** Only when the export holds the list's task rows.
  All three at once: every task except the status task maps to the same state as
  `first_status`; the status task's own raw status equals `first_status`; and no task carries
  a due or start date. Then `abandoned` is true, check 1 fails whatever its band, and the
  project grade is F. Two of the three is not enough, and shares of tasks with owners or
  dates never stand in for the test.

ACME examples: `Visitor parking redesign - Sam Okafor` has a bot reminder dated 2030-03-11
and a person's entry dated 2030-02-12, so it is stale at 28 days. `Annual handbook review -
Priya Shah` was last updated 2030-03-01: aging at 11 days. `Intranet page refresh - Jane
Doe` has no entries, nothing left `to do`, the status task is still `to do` and no task has a
date: absent and abandoned.

## Check 2: newness

Not applicable when check 1 is absent. Each person's entry is normalized before comparing:

1. lowercase;
2. remove ISO dates (`2030-03-12`), month and day with a slash when both parts are valid
   calendar values, with or without a year (`3/12`, `3/12/2030`), a hyphen form only with a
   year (`3-12-2030`), month-name dates in either order with an optional year (`March 12`,
   `12 March 2030`, `Mar 12, 2030`), and weekday names. Numeric ranges such as `1-4` are
   kept, so "Chapters 1-4" and "Chapters 5-8" are different entries. A fraction that reads as
   a valid month and day (`1/3` against `3/12`) cannot be told apart from a date;
3. remove punctuation;
4. collapse whitespace.

| Band | Rule | Result |
|---|---|---|
| placeholder | The normalized newest entry equals a phrase in `newness.placeholder_phrases`, or starts with one, has at most `newness.placeholder_max_words` words and no digit | fail |
| repeated | The normalized newest entry equals any of the previous `newness.repeat_lookback` entries | fail |
| new | Anything else; a single entry is new with a "first entry" note | pass |

- `consecutive_same` counts matching entries from the newest back without a break, the
  newest included. `at_least` is true when every pulled entry matched and the export pulled
  `tracker.comments_limit` entries, because older entries may match too ("at least the last
  3 entries match").
- An entry marked `truncated` is compared only up to the shorter normalized length.
- A `repeat` judgment of `repeated` turns `new` into `repeated` (basis judgment). A `repeat`
  judgment of `new` never overturns a rule result and is listed in `discarded_judgments`. A
  repeat judgment whose `entry_date` is not the newest entry's date is discarded.

ACME examples: `Furniture inventory reconciliation - Alex Rivera` filed five entries that
differ only in the date ("next check-in March 17", "March 10", "March 3", and two in
February): repeated, at least 5. `Payroll report refresh - Jane Doe` filed "No update this
week.": placeholder. A line such as "No update: supplier delivered 40 desks" carries a
fact and a digit, so it is new.

## Check 3: color consistency

Two signals: the color the state encoding reports (see `state-encoding.md`) and the newest
person's entry. Only the newest entry is read; an older entry is superseded history.

| Band | Rule | Result |
|---|---|---|
| misaligned (rule) | The project carries a hold signal and its color is in `state_encoding.hold_contradicting_colors` | fail |
| not assessable | No color, check 1 absent, or the newest entry is a placeholder | not scored |
| aligned / misaligned | From the `color` judgment whose `entry_date` equals the newest entry's date | pass / fail |
| not judged | No usable judgment | not scored; project and portfolio provisional |

- The rule result stands even when a color judgment says aligned; that judgment is listed as
  discarded. A color judgment for a not-assessable project is discarded too.
- A misaligned verdict keeps its quote, so the fix line reads "The name shows green; the
  entry says: '...'". The finding reports the conflict and never says what the color should
  be.

ACME examples: `New hire welcome pack refresh - Priya Shah` shows `[G]` while the newest
entry reads "Blocked until the department lists arrive; no date yet.": judged misaligned.
`Meeting room booking rollout - Alex Rivera` is named `[G] PAUSED: Weekly note`: misaligned
by rule, and the "aligned" judgment filed for it is discarded. `Annual handbook review` has
no color judgment: not judged, grade B provisional.

A check that is not scored (not applicable, not assessable, not judged) carries `result:
null` in `findings.json`.

## Check 4: placement

Items, each with a severity. Nothing else is compared.

| Item | Severity | Rule |
|---|---|---|
| `placement_finished_in_active` | conflict | The completion marker is in the status task name, or every task except the status task is complete or closed (and there is at least one) |
| `roadmap_status_conflict` | conflict | The paired roadmap row maps to `complete` or `not_started` while the project is in scope, or to `held` while the project carries no hold signal |
| `roadmap_hold_conflict` | minor | The project carries a hold signal and its row maps to anything but `held` |
| `status_field_stale` | minor | The status field is populated and a `status_field` judgment says stale |
| `owner_mismatch` | minor | The status task owner is empty or differs from the newest entry's author; skipped when check 1 is absent |
| `color_field_conflict` | minor | Only when `state_encoding.color_field_used` is true: the name marker and the field are both set and differ |
| `off_record_update` | minor | One per `off_record` judgment: a lead gave an update outside the tracker |
| `hold_no_dependency` | minor | A hold is recorded but the narrative names neither what it waits on nor who owns it |

- Band: conflicting when any counted conflict item exists; minor when any counted minor item
  exists; otherwise clean.
- Roadmap rows are matched through the pair file only, by exact equality after
  normalization: trim, remove leading characters listed in `roadmap.strip_leading`, collapse
  spaces, lowercase. A pair whose row is not found is listed in `missing_roadmap_rows` and
  raises no item.
- An unconfirmed pair's items carry `counted: false`, say "Unconfirmed pair" in their
  detail, never set the band and raise no fix line. The pair is listed in
  `unconfirmed_pairs`.
- An active list with no pair is listed in `unpaired_active_lists`; a `(none)` pair records a
  deliberate absence and raises nothing.
- A populated status field with no judgment adds a judgment request and a not-judged note,
  and no item. An empty status field raises nothing, ever.
- Roadmap item owner: the row's owner when that owner is a configured lead; otherwise the
  project lead.
- An off-record update is recorded as a minor item and never used as evidence for another
  check.

ACME examples: `Training library inventory - Jane Doe` is paired with a roadmap row reading
"done" while the list is active: a counted conflict owned by the row owner, Priya Shah, so the
correction names both Jane Doe and Priya Shah. Its status task has no owner: a minor item
owned by Jane Doe. `Visitor parking redesign` is paired, unconfirmed, with a row reading "on
hold": the item is shown but not counted, and the band stays clean.

## Outside the active folder

- **Not-started folder:** `placement_started_in_not_started` (conflict) when any task except
  the status task is in progress or complete. Example: `Office relocation planning - Alex
  Rivera` has two tasks in progress.
- **Completed folder:** `placement_open_in_completed` (conflict) when any task except the
  status task is not started or in progress; the detail gives the count. Example:
  `New-starter handbook update - Sam Okafor` has an open RAID log task and an open past-due
  task.
- A completed pair whose roadmap row maps to anything but `complete` adds a
  `completed_pair_conflicts` method line, never an item.
- Nothing else is checked in these folders. These items count toward the lead and portfolio
  letters (see `grading.md`) without adding a scorecard row.

## Scope rules

- **Held.** Hold signals: the hold prefix in the status task name, a status task status in
  `hold_statuses`, or a `hold` judgment with `narrative_records_hold: true`. With any signal:
  a color in `hold_contradicting_colors` keeps the project in scope with check 3 misaligned
  by rule; otherwise, with no `hold` judgment, the project is hold pending; with
  `dependency_and_owner_named: true` it is held; with false it stays in scope with a
  `hold_no_dependency` item.
- A held project appears only in `inventory.held` and on the snapshot slide as a bare
  inventory line. Its stale entries and overdue tasks appear nowhere, and a fix item the
  prior read carried for it is never listed in `closed_since_prior`. Example: `Shared drive
  clean-up - Sam Okafor`.
- **Hold pending:** not graded, listed in `inventory.hold_pending`, raises a judgment request
  and makes the run exit 3.
- **Resumed:** `resumed_on` on a `hold` judgment sets aside every entry before that date.
- **Pre-kickoff:** work not yet kicked off has no list, and the missing list is the right
  state.
- **Templates:** lists whose name starts with a `tracker.template_list_prefixes` entry are
  listed in `inventory.skipped_templates` and nowhere else.
- **Roadmap:** only rows named in the pair file are read.

## Never a finding

| Item | Why it never counts |
|---|---|
| An empty tracker color field when the encoding marks the field unused | When `state_encoding.color_field_used` is false the field carries no state, so its emptiness says nothing about reporting; the grader never reads it |
| Any reasoning that cites that field | The field carries no state, so no reasoning can rest on it |
| An empty status field | Empty is a valid state; only a populated field that contradicts the project can be wrong |
| An empty or missing RAID log, or open RAID item counts | The read grades status reporting, not RAID upkeep |
| Counts or shares of tasks with assignees or due dates, the number still in the first status, overdue counts | Task hygiene belongs on the cleanup pages; the overdue total is a context line only |
| Duplicate, near-duplicate, misspelled, scaffold or orphan task rows | Tidiness inside a lead's own lists is cleanup, not a check |
| Roadmap rows outside the pair file, rows without an owner or date, name typos, stray spaces, rows that are not projects (for example an event) | Only paired rows are in scope; the roadmap's own upkeep is not graded |
| The state encoding itself and the symptoms of a correctly recorded hold | A hold prefix, a completion marker, unchanged text, past dates and unmoved tasks are what a hold looks like |
| Anything about delivery | The grade measures reporting reliability, not whether work finishes on time |
