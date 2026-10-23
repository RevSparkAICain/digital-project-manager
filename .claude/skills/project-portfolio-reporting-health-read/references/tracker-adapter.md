# Tracker adapter

No script reads the tracker. The agent reads it through a tracker agent and writes one export
JSON, and `grade_portfolio.py` starts from that file. ClickUp is the reference adapter; any
tracker that can fill the same shape works.

## The ClickUp reference adapter (read-only)

The agent asks `clickup-agent` for these pulls, in order, and nothing beyond them.

| Pull | Fields read | Export fields |
|---|---|---|
| 1. Each of the three folders in `tracker.folders`, one paginated pull per folder | List names, list IDs, task totals | `folders.<folder>.lists[].list_id`, `name`, `task_total`; `reported_task_total` |
| 2. In every active list, the status task (name contains `tracker.status_task_match`), one task at a time | Name as written, owner, current status, the populated status field if any, the color field if the team uses it, and the newest entries up to `tracker.comments_limit`, each with author and date | `status_task` with `task_id`, `name`, `status`, `assignee`, `status_field`, `color_field`, `entries[]` (`author`, `date`, `text`, optional `is_bot`, optional `truncated`) |
| 3. One paginated task pull per active and completed list | Task name, status, assignees, due date, start date, and the date the task entered its current status (from the tracker's status-history data) | `tasks[]` with `task_id`, `name`, `status`, `assignees`, `due`, `start`, `status_since` |
| 4. The roadmap list (`tracker.roadmap_list_id`), one pull | Row name, status, owner, due date | `roadmap[]` with `row_id`, `name`, `status`, `owner`, `due` |

Export shape (see `examples/portfolio-export.json` for a full file):

```
{
  "export_version": 1,
  "tracker_kind": "clickup",
  "pulled_at": "2030-03-12T08:30",
  "includes_subtasks": false,
  "folders": {
    "active":      {"reported_task_total": 62, "lists": [...]},
    "completed":   {"reported_task_total": 4,  "lists": [...], "counts_reused": false},
    "not_started": {"reported_task_total": 3,  "lists": [...], "counts_reused": false}
  },
  "roadmap": [{"row_id": "RM-01", "name": "...", "status": "in progress",
               "owner": "Jane Doe", "due": "2030-06-30"}]
}
```

Rules for the conversion:

- `list_id` is unique across folders and is the project ID everywhere downstream.
- Names are copied exactly as the tracker holds them.
- A list with no status task is exported with `"status_task": null`; check 1 reads absent.
- The status task also appears among the list's `tasks` with the same `task_id`; the grader
  uses that to leave it out of every task rule.
- `"tasks": null` means the list's tasks were not pulled; the trip wire and cleanup are
  skipped for it with a method note.
- Entries are newest first. Long text that came back cut short is kept with
  `"truncated": true`.
- `includes_subtasks` says whether subtasks were pulled. A change from the prior read is
  disclosed as a measurement change.

## Do not pull

- Per-task last-updated or start fields that cost one read per task.
- RAID subtask trees: they can exceed response limits and nothing scores them.
- Roadmap custom fields.
- When a completed or not-started folder's total is unchanged since the prior read, its
  per-list counts may be reused; set `"counts_reused": true` on that folder so the method
  page says so.

## Pagination, rate limits and boundaries

- Page every list pull until a short page arrives. A pull that stops at a full page has been
  truncated and undercounts silently.
- Compare the pulled task count with the folder's reported total. The grader adds a count
  check line when they differ; record both numbers rather than correcting either.
- Read one task at a time. Parallel per-task reads can trip rate limits. On a rate-limit
  error, stop, wait, then resume serially.
- Use complete, unfiltered pulls only. A date-range filter can leave out items due on the
  edge date.
- A tracker status the config does not map stops the grader with a message naming it.
  Extend `status_map`; never guess a mapping.

## Mapping another tracker

| This package's term | ClickUp | Linear (example mapping) |
|---|---|---|
| Folder (active, completed, not started) | Folder | A project status group, or a project label per state |
| List (one project) | List | Project |
| Status task | A task named with `tracker.status_task_match` | The project's status updates, or a pinned issue that holds them |
| Entry | Comment on the status task | Project update or comment |
| Task row | Task | Issue |
| Roadmap row | Task in the roadmap list | Initiative or roadmap item |

`linear-agent` plays the role of `clickup-agent` for such a mapping. Keep `export_version` 1
and the same field names; set `tracker_kind` to the tracker's name.

## Keeping the roadmap pair file

The pair file is hand-kept markdown (template `assets/roadmap-project-pairs.example.md`). The
read uses it exactly as written.

- Update it in the same change as any project add, rename or completion in the tracker.
- Keep two tables, under headings containing `Active pairs` and `Completed pairs`. Move a
  pair to the completed table when its project finishes.
- Columns, found by header text in any order: `List ID`, `Project list`, `Roadmap row`,
  `Confirmed`. Extra columns are ignored. Values may be wrapped in backticks.
- Mark a doubtful pair `no` in `Confirmed`: the read still shows what it finds for it, labeled
  unconfirmed and not counted.
- Write `(none)` in `Roadmap row` for a project that deliberately has no roadmap row, so the
  read stops asking.
- Matching uses trimmed, case-insensitive names with the characters in
  `roadmap.strip_leading` removed from the start and runs of spaces collapsed. Nothing is
  matched by likeness: a name that merely contains another never pairs with it.
