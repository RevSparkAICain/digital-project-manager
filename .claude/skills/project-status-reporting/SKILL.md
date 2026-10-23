---
name: project-status-reporting
description: "Write the weekly status for one project and the executive rollup for a portfolio, each with a RAG color, from tracker data (ClickUp, Linear, Jira, Asana or Monday.com). Covers progress, risks, blockers and next steps, a dated-line comment for the project's status task, and an exceptions-first rollup that keeps tool data apart from judgment. Use when someone asks for a status update, a weekly report, a RAG call or a portfolio rollup."
---

# Project status reporting

This skill turns tracker data into two products: a weekly status for a single project and a
rollup across a portfolio. Both carry a RAG color. Data comes from the active tracker, or from several when work spans them.
A status covers progress, risks, blockers and what happens next.

The target reader is a leader who should be able to act on the report in about 30 seconds.
Write it candidly, keep the shape identical from one week to the next, and lead with the
decisions that someone has to make. Green is a conclusion that evidence has to support. It
is never where you start.

## Inputs

- Meeting notes, or a short account of what happened in the period.
- Live tracker data for the project or projects.
- The RAID rows, when the project keeps a log. RAID in this pod stands for Risks, Actions,
  Issues, Decisions. The expansion is deliberate, and `raid-log-management` uses the same
  one.

### Workspace settings

Set these once for the workspace. The defaults apply when nothing else is configured.

| Setting | Default | Used for |
|---|---|---|
| Status task name | `Weekly Status` | Receives the weekly comment; one per project |
| RAG field | `RAG` | Dropdown field; values Green, Yellow, Red |
| RAG source | the RAG field | Which place holds the current color: the field, or a name prefix like `[Green]` |
| Narrative fields | `Status Narrative`, `Executive Summary` | Long-form text, written in the same update as the comment |
| Notes link | `<notes link>` | Location of the notes; goes last on the lead line |

### Where files come from

Brand values matter only for a formal memo or slides. Use the first of these that exists:

1. the project's own file, if present (`brand/brand.json`)
2. otherwise, this folder's shared/ copy (`shared/brand.json`)

Name the file you used in the report. If it still holds placeholder values, say that too.
This lookup is an instruction to you. No script performs it and nothing walks up to a
project root.

## Steps

1. **Pull current data.** Ask the project's tracker agent for it (`project_trackers`, otherwise `tracker`, in
   `pods/pm/pm-config.yaml`). Send large
   cross-tool rollups and charts to `pm-analyst`.
2. **Deduplicate.** An item tracked in two trackers is one item. Resolve that before you count
   anything.
3. **Decide the color from evidence.** Look at dates, percent complete and open blockers.
   | Color | Test | Must come with |
   |---|---|---|
   | Green | Scope, schedule and quality are safe on current evidence | Nothing required |
   | Yellow | A believable threat, with recovery work already started | Cause plus plan |
   | Red | A miss is certain without intervention | Cause plus the decision needed |

   Write the colors as words: Green, Yellow, Red.
4. **Assemble the project status** from five parts:
   - Status: the color, with a headline of one line.
   - Done this period (task IDs): only items that actually finished.
   - Coming up (owner and due date each): the next milestones or tasks.
   - Risks and blockers: the leading items, each carrying an owner and the action needed.
     Pull them from the RAID log through `raid-log-management` when that optional skill is
     installed; otherwise rely on the meeting notes and tracker data.
   - Asks (decision and the date it is needed by): every explicit request for a decision.

   From the RAID log, accept open High and Severe risks, open issues, overdue actions and
   decisions made since the last report, each with ID, owner and next action. These rows
   inform the color. The RAID skill never sets it.
5. **Show, then post and update together.** Show the PM the comment in the layout below and
   the RAG and narrative field values. After the PM approves, put the comment on the
   project's status task and, in the same pass, update the RAG field and the narrative
   fields. Long text belongs
   in the fields, so the comment stays short.
6. **For a portfolio, build the executive rollup** described below.
7. **Separate fact from judgment** everywhere. Tool data is fact. The color call and any
   forecast are judgment, and the reader should be able to see which is which.
8. **Quote counts and dates.** Never write a vague claim of progress.
9. **Follow `updating-trackers`** for every comment and field write.
10. **Review formal files.** Run any memo or deck through `deliverable-review` before
    handing it over.

## Outputs

- **Quick ask:** a short status in the reply itself.
- **Formal or executive:** a `docx` memo, or a `pptx` of 1 to 2 slides. Styling comes from
  `brand-extract`, the skill your workspace configuration names, and brand values come
  from the lookup above (the project's file first, then the shared/ copy). Return the file
  path or paths.
- **Optional:** the tracker's agent can post this week's status to the project's status task
  once the PM approves it.

### Status comment layout

The labels and separators are fixed. Reword the bracketed placeholders freely.

```
<M/D> - <one or two sentences about the period, ending with the notes link or path if any>

Accomplishments:
<M/D> - <a finished item>
<M/D> - <another finished item>

RISKS - <the main risk in a sentence, or None.>
ISSUES - <the main open issue in a sentence, or None.>
```

Rules for the comment, by line of the layout:

- **Lead line:** dated by the event, not the posting day; it is the header, so nothing sits
  above it.
- **Accomplishment lines:** one per finished item, own date, latest first.
- **RISKS and ISSUES:** both always present, one line each, `None.` when empty.
- **Every line:** one or two plain sentences, no nesting or bold.
- **Content:** only what notes or trackers show; the color goes in the RAG field.

Worked example for a fictional ACME Co. project, the Field Service App Rollout:

```
4/10 - Held pilot readiness check; pilot start holds at 4/22, to be revisited on 4/17 against the offline sync fix. Notes from this discussion: <notes link>.

Accomplishments:
4/9 - Trained 18 of 20 pilot technicians; the remaining 2 are booked for 4/15.
4/8 - Enrolled all 40 pilot devices (DEMO-128).

RISKS - Offline sync defect (DEMO-131) fix due 4/17; a slip past 4/19 moves the 4/22 pilot start.
ISSUES - None.
```

### Executive rollup

The shape matches `examples/expected-exec-rollup.md`:

- Open with one bold sentence that counts the Yellow and Red projects and names the nearest
  decision date.
- `## Exceptions`: one entry per Yellow or Red project, giving color, trend, progress to the
  key milestone, the cause and what leadership must supply, plus an italic `*Judgment:*`
  line.
- `## Portfolio`: a table with the columns Project, RAG, Progress, Key milestone, Top risk
  and Trend (Improving, Steady or Slipping).
- Close with a `Facts:` note saying where the progress figures came from and that colors
  and trends are judgment.
- Progress figures from Linear are milestone progress, weighted by state so an in-progress
  issue counts as 25%. A milestone with 12 issues, 6 Done, 4 In Progress and 2 Todo reads
  58.33.

## Quality checks

- Each Yellow or Red has a cause and a plan or decision attached.
- The color rests on dates, percent complete or blockers, not on tone.
- Nothing is counted twice across trackers.
- The comment passes its own rules: event date leads, accomplishments are dated and newest
  first, both RISKS and ISSUES lines exist, and there is no bold, sub-bullet, prose section
  or title line.
- Judgment is labelled as judgment. The rollup example uses an italic `*Judgment:*` label
  and closes with a facts note.
- The brand file used is named, and placeholder values are flagged.
- Formal files have passed `deliverable-review`.

## Handoffs

- The tracker's agent reads the data and, after approval, posts the comment. In Asana it
  can post a project status update with its own color.
- `pm-analyst` handles heavy cross-tool rollups and charts.
- `raid-log-management` (optional) supplies the risk and issue rows.
- `updating-trackers` governs every comment and field write.
- `deliverable-review` gates the memo or slides.
- `brand-extract` styles formal output.

## Examples

See `examples/` for synthetic meeting notes, the comment they should yield and the rollup
for the three-project portfolio.
