---
name: raid-log-management
description: "Keep one register per project of Risks, Actions, Issues, Decisions: score the risks, give every row one owner and a dated next step, review on the configured rhythm and escalate to the configured role. Use when someone says start the RAID log, log a risk, record a decision, review the register, or what needs escalating. Saves to Markdown, a workbook or the project tracker."
---

# RAID log management

This skill builds and maintains one register per project. RAID here means Risks, Actions,
Issues, Decisions. Each entry has one owner and a dated next step. Risks are scored so they
can be ranked. The register is reviewed on a set rhythm, anything beyond the project's own
authority goes to a configured role, and the top rows feed the status report.

## Where files come from

For the pod config, the tracker profiles and the writing standard, use the first of these
that exists:

1. the project's own file, if present (`pods/pm/pm-config.yaml`, `pods/pm/trackers.yaml`)
2. otherwise, this folder's shared/ copy (`shared/pm-config.example.yaml`,
   `shared/trackers.example.yaml`, `shared/writing-standard.md`)

Config keys used:

| Key | Use |
|---|---|
| `raid.store` | Where the register is kept: `markdown` (default), `xlsx` or `tracker` |
| `review_cadence` (under `raid`) | How often the register is reviewed |
| `escalation_role` | The role that receives escalations |
| `tracker` | The active profile name in `trackers.yaml`, used by the tracker store |
| `output_dir` | Where a Markdown or workbook register is saved |

Prose follows `shared/writing-standard.md`. Never write the review rhythm, an escalation
title or a person into this skill's output from memory; read them from config each run.

## The four types

Each type has its own counter and its own tag.

| Tag | Type | What belongs here | Extra needs |
|---|---|---|---|
| R# | Risk | An uncertain future event that would harm scope, schedule, cost or quality if it happened | Likelihood, impact, score, and a response choice: avoid, reduce, transfer or accept. Write the choice at the start of the Next action cell |
| A# | Action | A committed piece of follow-up work the project has agreed to do | A due date. Done when the work is complete |
| I# | Issue | A problem that is already happening and needs handling now | A due date for the fix or the workaround. When a risk happens, close it and open a new I# that cites the R# |
| D# | Decision | A choice the project has made and must remember | The owner is the person who made the choice. The description says what was chosen and why. The next action is how it is communicated or applied |

## Row format

One Markdown table with these columns, in this order: ID, Type, Description, Owner,
Likelihood, Impact, Score, Next action, Due, Status.

- The Type cell spells out the word that matches the tag letter: R is Risk, A is Action,
  I is Issue, D is Decision.
- Likelihood and impact are whole numbers from 1 to 5. Score is likelihood times impact.
- Rows that are not risks show `-` in Likelihood, Impact and Score.
- Due holds a calendar date. For a decision it is the date the choice is to be communicated
  or applied.
- Status for risks, actions and issues is Open, In progress or Closed. Status for a decision
  is Active or Superseded. A closed row stays in the log.

## Scoring

Score each risk as likelihood times impact, then read the band.

| Score | Band | Handling |
|---|---|---|
| 1 to 4 | Low | Watch it and re-score at review |
| 5 to 9 | Moderate | The owner works the response inside the project |
| 10 to 16 | High | A response is due before the next review, and the risk shows in the status report |
| 20 to 25 | Severe | Escalate to the `escalation_role` at once |

Likelihood anchors:

| Points | Meaning |
|---|---|
| 1 | Very unlikely |
| 2 | Unlikely |
| 3 | Possible, about even odds |
| 4 | Likely |
| 5 | Near certain |

Impact anchors:

| Points | Meaning |
|---|---|
| 1 | Negligible: absorbed without a visible change |
| 2 | Minor: a small slip or cost the owner can absorb |
| 3 | Moderate: a milestone moves or the budget is touched |
| 4 | Major: a key date, the budget or the quality bar is clearly missed |
| 5 | Threatens the goal of the project |

Re-score at every review and record the new numbers in place of the old ones. The score is a
judgment; the log reports it as the owner's judgment and the table facts as facts.

## Owners and next actions

- One named owner per row. A team, a group or "TBD" is not an owner. If nobody accepts the
  row, the missing owner is itself escalated to the `escalation_role`.
- Every row has a concrete next step and a date. A row with neither is incomplete: say so
  before saving, and list it in the output.

## Numbering and reversals

- Each type counts up on its own: R1, R2, then A1, A2, and so on.
- A number is never reused, even after its row is closed. Rows are never renumbered.
- To change a past decision, add a new D# whose description says it reverses the earlier D#
  by ID, and set the earlier row to Superseded. The old row stays visible.
- A risk that happens keeps its R# (set to Closed) and gains a new I# that cites it.
- Closing is the only removal. Never delete a row.

## Review cadence

Read `review_cadence` from config. At each review:

1. Update the status of every open row.
2. Re-score each open risk.
3. Close what is finished.
4. Add rows from the period's meetings and status inputs.
5. List every row whose due date has passed.

## Escalation

Escalate to the role named by `escalation_role`: draft the message for the PM to send.
Escalate when:

- a risk lands in the Severe band;
- a row needs authority, money or people the project does not control;
- no owner can be found;
- a row is overdue by more than one review.

If a security or compliance skill or agent is installed, route a risk acceptance on security work there too; otherwise skip that step.

## Stores

Choose by `raid.store`.

- **markdown** (default): one file per project in `output_dir`, with a title and the single
  table. Name the project in the title.
- **xlsx**: the same columns in a workbook, built through an xlsx skill, if installed. If no
  such skill is installed, say so and save Markdown instead.
- **tracker**: write through the active profile named by `tracker`, found in `trackers.yaml`.
  If no profile exists, run `connecting-a-tracker` first. For ClickUp, Linear, Jira, Asana and Monday.com, hand the
  writes to `updating-trackers`. For any other tracker, write through the
  profile's `write_tools` and read back through its `read_tools`. If the project's tracker
  setup already has an item set aside for the log, write into that item. Otherwise follow
  the profile's `concepts` map, and handle any concept the tracker lacks as the profile's
  `gaps` entry says.

Show every tracker write first as a table of planned changes (item, change, field values).
Nothing is written until the user approves the table. After writing, read each item back,
compare it with the table, and report the IDs and links.

## Feeding status reports

Hand `project-status-reporting` these rows, each with ID, owner and next action:

- open High and Severe risks;
- open issues;
- overdue actions;
- decisions made since the last report.

They inform the status color. This skill supplies the rows and does not set the color.

## Checks before saving

1. IDs are unique, each one a letter plus a number, and the Type word matches the letter.
2. Every risk score equals likelihood times impact, with both inputs from 1 to 5.
3. Non-risk rows show `-` in the three scoring cells.
4. Every row has an owner and a next action, and every action and issue has a due date.
5. Every reversal points to an existing, lower-numbered D#, and that D# is Superseded.
6. Every band label agrees with the table above.
7. Status values come from the sets above.
8. No em dash anywhere, and the writing standard is applied.

## Output of a run

- Where the log is saved: a file path or a tracker link.
- The top rows by score.
- Rows that need escalation or a decision.
- Any incomplete rows found.

## Guardrails

- Never delete a row.
- Never write to a tracker before the user approves the table.
- No secrets or personal contact details in the log. Config names roles, never people.
- Report log contents as facts and label scoring as judgment.
