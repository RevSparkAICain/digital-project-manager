---
name: project-portfolio-reporting-health-read
description: "Grade how reliably a project portfolio is reported in its tracker, from a tracker export, and build the health read deck. Use when someone asks for the portfolio health read, a tracker health check, a reporting scorecard for project leads, or the per-lead list of record corrections. Each active project is checked for a current status entry, an entry that says something new, a reported color its own written status supports, and records that agree about where the project sits; the agent supplies the judgment calls, a missing judgment stays not judged, and the deck carries a leadership summary, a team scorecard, a fix list per lead and a cleanup page per person. Not for judging delivery, editing the tracker, or writing a project status report."
---

# project-portfolio-reporting-health-read

A periodic (usually weekly) read of how well a project portfolio is reported in its tracker.
It grades the record, not the work: a project running late that reports currently, honestly
and specifically passes; a project going well that is recorded badly is a finding. Two
scripts do the offline work: `grade_portfolio.py` turns the tracker export, the agent's
judgments and the roadmap pair file into `findings.json`, and `build_deck.py` turns the
findings into a branded pptx.

## When to use

- Someone wants a periodic read of the portfolio's reporting: does each active project have
  a current status entry, does that entry add anything, is the reported color backed by the
  written status, and does the project sit in the folder and roadmap state its records claim.
- Someone asks for the portfolio health read, a tracker health check, a reporting scorecard
  for project leads, or the per-lead list of record corrections.
- Not for: judging delivery (dates, plans, approach, likely outcome); editing anything in the
  tracker; building a project status report (use `project-status-reporting`); checking
  tidiness inside a lead's own task lists beyond the cleanup pages.
- The read is about the record. Every finding names a record condition a lead can change.

## Inputs

| Input | Where it comes from |
|---|---|
| Config (`health-read-config.json`) | Copied from `assets/health-read-config.example.json` and edited per portfolio. Holds the tracker kind, workspace, space and folder IDs (placeholders in the example), the three folder names, the roadmap list, the list URL template, the leads, the status window, the executive reader role, the state encoding, the status vocabulary, cleanup thresholds and grading lines. No tenant value lives in code. Every key is in Config keys below |
| Roadmap pair file | A hand-kept markdown file (template `assets/roadmap-project-pairs.example.md`) mapping each active or completed project list to its roadmap row. The config key `roadmap.pairs_file` names it, relative to the config file. The read uses it as written and never derives a pair itself |
| Tracker export (`export.json`) | Written by the tracker adapter (ClickUp is the reference adapter; see `references/tracker-adapter.md`). Holds the three folders' lists, each active list's status task with its newest entries, the task rows per list, and the roadmap rows |
| Judgments file (`judgments.json`) | Written by the agent after reading each project's newest status entry: is the color supported by the narrative, does a textually different entry still repeat the same open item, does a populated status field describe a state the project has left, does a hold name its dependency and owner, and any update a lead gave outside the tracker. Optional: without it every judgment check reads not judged |
| Prior findings | Last read's `findings.json`, optional, for the week-over-week lines |
| Brand values | `brand/brand.json`, through the lookup below |

## Where files come from

Brand values are read in two tiers:

- Tier 1: the project's own file, if present: `brand/brand.json`.
- Tier 2: otherwise, this folder's shared/ copy: `shared/brand.json`.

A `--brand` path or a `BRAND_JSON` setting in the environment takes priority over both tiers.
The full order used by `build_deck.py`:

1. `--brand <path>`. A missing file stops the run with exit 1 naming the path.
2. `BRAND_JSON`. Same rule.
3. `brand/brand.json`, searched while walking up from the scripts folder. The walk stops at
   the project root, the nearest ancestor holding a `pods/` or `.claude/` folder.
4. `shared/brand.json` inside this skill folder.
5. Nothing found: exit 1 telling the user to pass `--brand` or set `BRAND_JSON`.

The script prints which brand file it used. Brand keys read: `colors.primary`, `colors.text`,
`colors.textMuted`, `colors.background`, `colors.surface`, `colors.divider`, `colors.link`
(falls back to `colors.primary` when absent), `status.good`, `status.warning`, `fonts.office`
and `fonts.officeHeading` (falls back to `fonts.office`). To replace the placeholder brand
file, use the `brand-extract` skill; this skill only reads `brand.json`.

The writing standard is read the same way: the installed `house-style` skill's
`writing-standard.md` when present, otherwise `shared/writing-standard.md`.

## Steps

1. **Confirm the folder set.** Read the three folders fresh each run and count the active
   lists directly. Rule: last week's number is never reused.
2. **Pull the export, serially.** Ask `clickup-agent` (or the matching tracker agent) for the
   data set in `references/tracker-adapter.md` and nothing beyond it. Rules: reads only;
   per-task reads go one at a time, never in parallel.
3. **Check the pair file.** Note any active list with no pair row, any pair marked
   unconfirmed, and any pair whose list has moved to the completed folder. Rule: report these
   on the method page and ask the operator (the person running the session) to update the
   file; never guess a pair from name likeness.
4. **First grading pass, without judgments.**

   ```
   python scripts/grade_portfolio.py export.json --config health-read-config.json --as-of YYYY-MM-DD --out work/findings.json
   ```

   It writes the rule-based results and a `judgment_requests` list naming every project and
   check that needs a reading, with the newest entry's text and date attached. Exit 3 here
   is expected.
5. **Write the judgments.** For each request, read the newest status entry only and record a
   verdict with a short quote in `judgments.json`, dated with the same read date. Rules:
   report a conflict, never resolve it (write "green in the name, a blocker in the entry";
   never write which color it ought to be); a lead's spoken
   account is recorded as an `off_record` item, never as evidence; leave a request
   unanswered rather than guess. A `repeat` judgment is optional: add one only when a
   textually new entry plainly carries the same open item as the previous one.
6. **Second grading pass, with judgments.**

   ```
   python scripts/grade_portfolio.py export.json --config health-read-config.json --as-of YYYY-MM-DD --judgments judgments.json [--prior last/findings.json] --out work/findings.json
   ```

   Any request still unanswered stays not judged and the grade is marked provisional (exit
   3). Rule: not judged is never counted as a pass.
7. **Build the deck.**

   ```
   python scripts/build_deck.py work/findings.json --out <WORKSPACE_ROOT>/deliverables/health-read/<as-of>/health-read.pptx
   ```

   `<WORKSPACE_ROOT>` is the install folder that holds `brand/`. Rule: overflow continues on
   a new slide; text never shrinks below the floors. Never build from an older findings file
   after a failed grading run.
8. **Review gate.** Hand the deck to the `deliverable-reviewer` agent before anyone else sees
   it, the operator included.
9. **Report back, decision-first.** Lead with the portfolio grade and what moved since the
   prior read, then the deck path, then any provisional items, unpaired lists and review
   flags. Separate fact (tracker data) from judgment (bands, verdicts, grades).

## The four checks

Every in-scope active project is scored on these and nothing else. Full rules, bands and
worked examples are in `references/checks.md`.

1. **Currency:** is there a status task with at least one entry written by a person, and how
   old is the newest one? Bands: current, aging, stale, absent. A separate trip wire marks a
   list that was set up and never used: no task ever left the first status, the status task
   never advanced, and no task carries a date. All three at once, never two.
2. **Newness:** does the newest entry differ from the ones before it once dates are set
   aside? Bands: new, repeated, placeholder. A status filed on time that adds nothing is a
   finding on its own.
3. **Color consistency:** does the written entry support the color the state encoding
   reports? Bands: aligned, misaligned, not assessable, not judged. A recorded hold with a
   color the config lists in `state_encoding.hold_contradicting_colors` is misaligned by rule.
4. **Placement:** the folder against task activity, the paired roadmap row against the
   project, a populated status field against the project's present state, and the status
   task owner against the person writing entries. Bands: clean, minor, conflicting.

## Scope rules

- **Held projects leave the read.** A project is held only when all three are true: the hold
  is recorded somewhere (name prefix, a status in `hold_statuses`, or the narrative; any one
  is enough), the reported color does not contradict it, and the narrative names what is
  awaited and who owns it. A held project appears only as a bare inventory line (count and
  names under an out-of-scope heading) and nowhere else: no row, no card, no split, no
  footnote.
- A hold that fails any of the three stays in scope as an active project, and the failure is
  the finding (a color contradiction under check 3, a missing dependency or owner under
  check 4).
- A hold whose dependency call has not been judged yet is hold pending: not graded, listed on
  the snapshot and method pages and in the judgment requests.
- A resumed project re-enters scope from its resume date only. Nothing before that date is
  scored.
- **Work not yet kicked off has no list; the missing list is the right state.** Never ask for
  a list or a placeholder early.
- Lists in the not-started folder are checked only for started work. Lists in the completed
  folder are checked only for open work. Template lists are skipped entirely.
- Only roadmap rows named in the pair file are in scope. A pair whose list is finished goes on
  the method page and earns no score.

## Cleanup pages

- A separate, forwardable page per lead listing record tidy-ups in that lead's own active and
  completed lists: started-then-idle tasks, overdue tasks, active work with no owner, active
  work with neither date nor owner, not-started tasks past their date, one line for an unused
  block of setup rows, and open work left in a finished project.
- The page opens with "What to fix (n)": a numbered list combining that lead's fix items
  with one line per project and bucket, so a single page carries the whole ask.
- Not-started folder, held, hold-pending and template lists are out of scope here. Status
  tasks and finished tasks never enter a bucket.
- A task with an explicit owner who is another configured lead goes on that lead's page;
  otherwise the list lead's.
- Every lead gets a page, including a lead with nothing to fix.
- Bucket rules (first match wins, in this order, for active lists): `parked` (in progress
  longer than `cleanup.parked_days`), `no_date_no_owner`, `overdue` (in progress or in
  `queued_statuses`, due before the read date), `no_owner`, `not_started_past_due`. A list
  with at least `cleanup.scaffold_min_rows` not-started rows with no date and no owner gets
  one `scaffold` line instead. Completed lists: `open_raid`, `past_due_open`,
  `open_in_finished`; these are detail under the list's placement item and add no summary
  line.

## Flags

`grade_portfolio.py <export.json>`

| Flag | Meaning |
|---|---|
| `--config` | Required. Health read config JSON (see Config keys). The pair file path comes from `roadmap.pairs_file`, relative to this file. |
| `--as-of` | Required. The read date, `YYYY-MM-DD`. Ages are counted to it, and an entry dated after it stops the run. |
| `--judgments` | Optional. The judgments JSON. Its `as_of` must equal `--as-of`; judgments are never reused across reads. |
| `--prior` | Optional. Last read's `findings.json`, for the prior read date, the closed lines, the same-letter-different-reasons line, count changes and measurement changes. Its `as_of` must be before `--as-of`. A project on hold this read is never listed as closed. |
| `--out` | Required. The `findings.json` to write; the parent folder is created when missing. |

`build_deck.py <findings.json>`

| Flag | Meaning |
|---|---|
| `--out` | Required. The pptx to write; the parent folder is created when missing. |
| `--brand` | Brand JSON path. Default: none, so the lookup order above applies. |

## Exit codes

`grade_portfolio.py`:

| Code | Meaning |
|---|---|
| 0 | Written and complete: every judgment request answered. |
| 1 | Malformed or unreadable input, a missing or mistyped config key, a status not covered by `status_map` (all named), a paired roadmap row status not covered by `roadmap.status_map`, a bad judgment (unknown project, verdict outside the allowed set, a duplicate, or a judgments file dated for another read), an entry dated after `--as-of`, a `--prior` dated on or after `--as-of`, or a usage error (`grade_portfolio: usage error: ...`). |
| 3 | Written, with one or more items not judged or holds pending. The stderr line names the count. |

`build_deck.py`:

| Code | Meaning |
|---|---|
| 0 | Written. |
| 1 | Unreadable or malformed findings, a `findings_version` other than 1, an unreadable or malformed brand file, python-pptx missing (with an install hint), or a usage error (`build_deck: usage error: ...`). |
| 4 | Layout check failed: a block taller than a page, a card name longer than one card line, or a shape outside the slide. Nothing is written. |

Every failure prints exactly one line on stderr, starting `grade_portfolio: ` or
`build_deck: `, with no traceback. Outputs are written to a temporary name in the same folder
and moved into place, so a failed run leaves an existing file as it was.

## Config keys

Every key in `assets/health-read-config.example.json`. Copy the file and edit it.

| Key | Meaning |
|---|---|
| `config_version` | Version of this config. A change from the prior read is disclosed as a measurement change. |
| `title` | Deck and findings title; also the deck's title property. |
| `executive_reader_role` | Role title of the leadership summary's reader. A role, never a name. |
| `prepared_by` | Name of the operator running the read: the deck byline and author property. |
| `grade_statement` | Object holding the two panel texts below. |
| `grade_statement.measures` | What the grade measures, shown on the grade slide. |
| `grade_statement.does_not_measure` | What it does not measure, shown beside it. |
| `tracker` | Object describing the tracker scope. |
| `tracker.kind` | Adapter that produced the export, for example `clickup`. |
| `tracker.workspace_id` | Placeholder for the workspace ID the adapter reads. The example's placeholders use angle brackets (`<workspace-id>`); double-brace tokens are reserved for the install renderer. |
| `tracker.space_id` | Placeholder for the space ID. |
| `tracker.folders` | The three folders, each `{id, name}`. |
| `tracker.folders.active` | The active projects folder: `id` and `name`. |
| `tracker.folders.completed` | The completed projects folder: `id` and `name`. |
| `tracker.folders.not_started` | The not-started projects folder: `id` and `name`. |
| `tracker.roadmap_list_id` | Placeholder for the roadmap list ID. |
| `tracker.list_url_template` | URL pattern for a list; `{list_id}` is replaced. Every project name in the deck links here. |
| `tracker.status_task_match` | Text identifying the status task in each list (the adapter's match rule). |
| `tracker.comments_limit` | Entries pulled per status task. Used for the "at least" repeat case. |
| `tracker.bot_authors` | Entry authors never counted as a person. |
| `tracker.automated_prefixes` | Entry text prefixes never counted as a person's entry. |
| `tracker.template_list_prefixes` | List name prefixes skipped entirely. |
| `leads` | The leads in display order; every lead gets a cleanup page. |
| `leads[].name` | The lead's display name. |
| `leads[].aliases` | Other spellings accepted at the end of a list name. |
| `lead_separator` | Separator before the lead's name at the end of a list name. |
| `status_window_days` | Object holding the two day limits below. |
| `status_window_days.current` | Days for current (inclusive). |
| `status_window_days.aging` | Days for aging (inclusive); older is stale. |
| `status_map` | Raw tracker status to `not_started`, `in_progress`, `complete` or `closed`. A status missing here stops the run. |
| `first_status` | The raw status a new task starts in (trip wire). |
| `hold_statuses` | Raw statuses that signal a hold. |
| `queued_statuses` | Raw not-started statuses that mean queued to start (overdue and no-owner buckets). |
| `state_encoding` | Object describing how the team records project state; see `references/state-encoding.md`. |
| `state_encoding.color_markers` | Color name (`green`, `amber`, `red`) to marker tokens in the status task name. |
| `state_encoding.hold_prefix` | Name prefix that records a hold. |
| `state_encoding.completion_marker` | Name token that records completion. |
| `state_encoding.color_field_used` | Whether the tracker's own color field carries state. When false the field is never read and never mentioned. |
| `state_encoding.hold_contradicting_colors` | Colors that contradict a recorded hold. |
| `newness` | Object holding the newness settings below. |
| `newness.repeat_lookback` | Previous entries compared with the newest. |
| `newness.placeholder_phrases` | Phrases that mark an empty entry. |
| `newness.placeholder_max_words` | Word limit for a phrase-led placeholder. |
| `roadmap` | Object holding the roadmap settings below. |
| `roadmap.pairs_file` | Pair file path, relative to the config file. |
| `roadmap.strip_leading` | Leading characters removed before matching row names. |
| `roadmap.status_map` | Roadmap status to `active`, `complete`, `not_started` or `held`. |
| `cleanup` | Object holding the cleanup settings below. |
| `cleanup.parked_days` | Days in progress before a task counts as parked. |
| `cleanup.scaffold_min_rows` | Undated, unowned not-started rows that make one scaffold line. |
| `cleanup.raid_task_match` | Task name text marking a RAID log task. |
| `cleanup.subtitle` | Line under every cleanup page title. |
| `cleanup.buckets` | `{label, definition, remedy}` for each bucket key: `parked`, `no_date_no_owner`, `overdue`, `no_owner`, `not_started_past_due`, `scaffold`, `open_raid`, `past_due_open`, `open_in_finished`. Copied onto every bucket heading on every page. |
| `grading` | Object holding the grading settings below; see `references/grading.md`. |
| `grading.points` | Points per outcome: `aging`, `stale`, `absent`, `repeated`, `placeholder`, `misaligned`, `minor`, `conflicting`. |
| `grading.project_bands` | Largest points value per letter: `A`, `B`, `C` and `D`; above D is F. |
| `grading.portfolio_lines` | Share lines for the portfolio and lead letters: `f_currency_fail_over`, `d_currency_fail_over`, `d_color_fail_over`, `c_currency_fail_over`, `c_newness_fail_over`, `c_color_or_records_over`. |

## Outputs

- `findings.json` (`findings_version` 1), two-space indent, ASCII, the same bytes for the same
  inputs. Top-level keys: `findings_version`, `config_version`, `as_of`, `prior_as_of`,
  `title`, `executive_reader_role`, `prepared_by`, `grade_statement`, `cleanup_subtitle`
  (copied from the config so the deck needs no config), `complete`, `portfolio` (grade,
  provisional, `points_note`, `reasons`, `reason_keys`, `prior_grade`, `reasons_changed`,
  `in_scope_count`, `shares`), `inventory` (active, completed, not started, held,
  hold pending, skipped templates), `splits`, `projects` (in-scope active projects, ranked
  by concern), `outside_findings`, `leads` (every configured lead in config order, each with
  grade, fix list and cleanup), `unattributed`, `corrections_by_project`,
  `projects_needing_nothing`, `reporting_well`, `closed_since_prior`, `judgment_requests`
  (each with `answered`, and `field_value` for a status field request), `method` (sources,
  `folder_counts`, filters, pair and roadmap notes, not judged, discarded judgments, count
  checks, measurement changes, notes) and `context` (the overdue total, never graded). A
  check that is not scored (not applicable, not assessable, not judged) carries `result`
  null. `examples/expected-findings.json` is the worked example.
- The deck: one 16:9 pptx built from a blank presentation every run, in four sections
  (Leadership summary, Team scorecard, Fix list per lead, Cleanup per person). Every slide
  has a section label, a title, a footer `<section> | page <i> of <n>` counted within the
  section, and speaker notes that begin `As of <as_of>.` The slide list, columns and the
  measured capacities are in `references/deck-structure.md`.

## Quality checks

- **Never a finding.** None of these appears in a check, a grade reason, the leadership
  summary, the scorecard, the fix list, a footnote or an evidence cell, softened or not. The
  per-person cleanup pages are the one place task-level tidy-ups appear, and they never feed
  a check, a band or a grade:
  - an empty tracker color field when the state encoding marks the field unused, and any
    reasoning that cites it;
  - an empty status field (a populated one that contradicts the project can be);
  - an empty or missing RAID log, or open RAID item counts;
  - counts or shares of tasks with assignees or due dates, the number still in the first
    status, and overdue task counts (the portfolio overdue total appears once as a context
    line in the scorecard footer, never as a driver);
  - duplicate, near-duplicate, misspelled, scaffold or orphan task rows in a lead's list;
  - roadmap rows outside the pair file, roadmap rows without an owner or date, roadmap name
    typos or stray spaces, and rows that are not projects (for example an event);
  - the state encoding itself (a hold prefix, a completion marker, a color marker) and every
    symptom of a correctly recorded hold (unchanged text, past dates, unmoved tasks);
  - anything about delivery.
- **Report, never prescribe.** The deck never says what a color should be and never puts a
  due date or priority on a lead's correction.
- **Use names as written.** Project and list names are shown exactly as the tracker holds
  them, never paraphrased. Keep the team's own terms and product names; do not translate them
  for the executive reader.
- **Name behavior, not people.** "The newest entry is 28 days old" is a finding. A statement
  about a person's competence is never written.
- **Every number comes from the export or the judgments file.** Nothing is estimated.
- **Measurement changes are disclosed.** When the config version, the subtask basis or a
  reused count differs from the prior read, the method page says so and the movement is not
  presented as a change in behavior.
- **The grade states what it measures:** reporting reliability, not delivery. When the letter
  is unchanged but the reasons changed, the grade slide says so.
- **Deck layout:** every shape inside the slide; text at or above the floors (body 12pt,
  table cells 11pt, captions and footers 10pt); continuations instead of shrinking; cross
  references by slide title, never by number. The build sweeps every shape and exits 4 on a
  violation; open the deck and look as well, then hand it to the reviewer.
- **Links:** every project name on the snapshot, scorecard, fix list, corrections and cleanup
  pages links to its list. Every link is underlined and the deck has one link style: the link
  color when it reaches 4.5:1 on both the background and the card surface, otherwise the text
  color. A status color is only ever a fill behind text that reaches 4.5:1.
- **Long list names:** a list name longer than one card line stops the build with exit 4. The
  only fix is a shorter list name in the tracker; the error shows the limit.

## Failure modes

Each is a rule. Numbers are invented and round.

- Grading delivery instead of the record: a project with 20 overdue tasks whose lead filed a
  current, specific entry explaining the slip is not a concern. Overdue counts never move a
  band or a grade.
- Citing an unused field: when `state_encoding.color_field_used` is false, the field's
  emptiness is never a reason, a footnote or a grade driver. The grader never reads it.
- Reading only the newest entry hides a repeat: compare it with the previous entries and state
  the run of identical entries in a row ("the last 3 entries match").
- A repeat that differs only by its date is still a repeat. Dates are stripped before
  comparing: ISO dates, month and day (`3/12`), and month names with a day. Numeric ranges
  such as `1-4` are kept, so they make an entry new. A fraction written like a date
  (`1/3` against `3/12`) cannot be told apart from one.
- Treating an automated reminder as a filing: a bot comment posted yesterday on a status task
  whose last entry from a person is 30 days old leaves the project stale.
- Judging an older entry: a color phrase in an entry two weeks back is superseded history. A
  judgment whose entry date is not the newest entry from a person is discarded as not judged.
- Reusing last week's judgments: a judgments file dated for a different read is rejected
  outright (exit 1).
- Fuzzy roadmap matching: matching names by likeness produces false pairs. Only exact matches
  after the documented normalization count, and only through the pair file.
- Parked work counted from raw time in status: rows idle past `cleanup.parked_days` include
  setup rows that were never started. Only in-progress tasks count as parked; untouched setup
  rows never do. The method page shows the raw and counted numbers.
- Status tasks counted as parked: a status task stays in progress for its whole life by
  design, so it always reads as hundreds of days stuck. It is excluded and counted.
- Asking a finished task for a date: complete or closed tasks never enter a missing-date or
  missing-owner bucket.
- Every bucket heading carries its definition and remedy on every page, continuations
  included, so each page stands alone.
- Parallel per-task reads against a tracker can trip its rate limits. Pull serially.
- One page of a long list undercounts silently. Page until a short page arrives, and
  compare the pulled count with the folder's reported total (the grader reports a gap as a
  count check).
- A date-range filter can leave out items due on the edge date, so every total comes from
  complete, unfiltered pulls only.
- A count that changes between reads with no explanation is reported on the method page,
  never swapped in silently.
- Card pitch and type size never change to admit more cards; above the measured capacity the
  attention slide rolls up and every other slide continues.
- Shrinking text to hold the slide count: a scorecard at 8pt is unreadable. The number of
  slides is free; readability is not.
- A visual pass misses small overlaps and names cut off at the edge. The build verifies with a
  shape bounds sweep, not by eye.
- Table rows grow past their declared height when text wraps, so a table that passes a
  declared-height check can run through the footer. Pagination uses heights estimated from
  the wrapped text.
- A number in a cross reference ("see slide 9") goes wrong after any split. Refer to titles.
- The deck is built from brand values every run, never from an earlier deck.
- A held project appears in the inventory only. Its hold symptoms are never raised as
  findings, rows or notes.

## Connector contracts

No script calls a live system. Every script starts from the export JSON, the judgments JSON
and the pair file.

- **Tracker read (ClickUp reference adapter, read-only).**
  - Method: the agent asks `clickup-agent` for, in order: each of the three folders (list
    names, IDs and task totals, one paginated pull per folder); in every active list the
    status task, one task at a time (name as written, owner, current status, the populated
    status field if any, and the newest entries up to `tracker.comments_limit`, each with
    author and date); one paginated task pull per active and completed list (name, status,
    assignees, due date, start date, and the date the task entered its current status); and
    the roadmap list in one pull (row name, status, owner, due date).
  - Do not pull: per-task fields that cost one read per task, RAID subtask trees, or roadmap
    custom fields. When a completed or not-started folder's total is unchanged since the
    prior read, its per-list counts may be reused and the export marks them
    `counts_reused`.
  - Output the scripts consume: the export JSON in `references/tracker-adapter.md`
    (`examples/portfolio-export.json` is a full example), written to the session's scratch
    area.
  - Failure modes: a paged pull that stops at a full page has been truncated, so keep paging;
    a folder whose pulled count differs from its reported total is recorded with both
    numbers; a rate-limit error mid-pull means stop, wait and resume serially, never retry in
    parallel; a list with no status task is exported with a null status task (check 1 reads
    absent); long entry text that comes back cut short is kept with `truncated: true`, and
    newness compares only the shared prefix; a tracker status the config does not map stops
    the grader with a message naming it, so extend the map, never guess.
- **Judgment pass (agent-side).**
  - Method: read `judgment_requests` from the first grading pass, read each quoted newest
    entry, and write the judgments JSON (`examples/judgments.json`). Allowed verdicts:
    `color` aligned or misaligned; `repeat` repeated or new; `status_field` stale or current;
    `hold` carries `narrative_records_hold` and `dependency_and_owner_named` (true or false)
    and an optional `resumed_on` date; `off_record` carries a note.
  - Failure modes: a judgment against an older entry is discarded; a judgment for a project
    the export does not contain stops the grader; a verdict outside the allowed set stops the
    grader; a `repeat` verdict of new never overturns a rule result and is listed as
    discarded.

## Handoffs

- `clickup-agent`: performs the read-only tracker pulls for the reference
  adapter. `linear-agent` plays the same role if a team maps Linear projects into the export
  shape.
- `pm-analyst`: may run the scripts and assemble the report-back.
- `deliverable-reviewer` agent (skill `deliverable-review`): reviews the deck
  before it reaches anyone.
- `house-style`: governs all deck copy, judgment notes and the report-back.
- `brand-extract`: owns `brand.json`; this skill only reads it.
- `project-status-reporting`: the place for delivery status; this read never
  produces one.

## References

- `references/checks.md`: the four checks with every band, threshold key and rule, which
  entries count as a person's, the trip wire, newness normalization, color signals,
  placement comparisons, scope rules, the never-a-finding table and worked ACME examples.
- `references/state-encoding.md`: what a state encoding is, the parsing rules, what each
  element feeds, and how to describe another team's convention.
- `references/grading.md`: points, letters, portfolio and lead lines, provisional marking,
  outside lists, the grade statement and a worked example reproducing the fixture's grades.
- `references/tracker-adapter.md`: the read-only ClickUp reference adapter, the export shape,
  mapping another tracker, pagination and rate-limit rules, and keeping the pair file.
- `references/deck-structure.md`: every slide in order with its contents, the
  measure-the-asset method and the measured capacities, overflow, type floors, the bounds
  sweep, contrast and the writing rules for lead-facing pages.

## Files

| Path | Purpose |
|---|---|
| `scripts/grade_portfolio.py` | Export, config, pair file, judgments and prior into `findings.json` |
| `scripts/build_deck.py` | `findings.json` into the pptx, with the bounds sweep |
| `scripts/health_core.py` | Shared: input loading, config check, pair file parsing, text normalization, contrast, brand lookup. No CLI |
| `scripts/deck_layout.py` | Shared: slide geometry, type sizes, measured capacity, wrapped-text estimate, pagination. No CLI |
| `assets/health-read-config.example.json` | Example config with every key |
| `assets/roadmap-project-pairs.example.md` | Pair file template with upkeep rules and two rows |
| `examples/portfolio-export.json` | Example export: 14 ACME lists across the three folders, read date 2030-03-12 |
| `examples/judgments.json` | Example judgments for that read |
| `examples/roadmap-pairs.md` | The full pair file the demo config points to |
| `examples/demo-config.json` | The asset config with `roadmap.pairs_file` set to `roadmap-pairs.md` |
| `examples/expected-findings.json` | The exact output of the example run |
| `shared/brand.json`, `shared/writing-standard.md` | Fallback copies (see Where files come from) |

## Requirements

Python 3.9 or later. `grade_portfolio.py` uses the standard library only; `build_deck.py`
needs `python-pptx`. No network access.
