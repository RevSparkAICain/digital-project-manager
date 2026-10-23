---
name: project-charter-and-kickoff
description: "Open a project: turn scoping material into a business case, a short charter with fixed headings, a set-up project in the connected tracker, and a kickoff agenda. Use when a project is approved to start, or someone says write the charter, set up the project, or plan the kickoff. The charter goes to the gate named in the pod config."
---

# Project charter and kickoff

This skill makes ownership and the finish line explicit before any build work starts. It
runs four steps in order: a business case, a charter, a tracker set-up and a kickoff
agenda. Keep the charter short. A couple of pages of decisions beat long narrative.

## Where files come from

For the pod config, the tracker profiles and the writing standard, use the first of these
that exists:

1. the project's own file, if present (`pods/pm/pm-config.yaml`, `pods/pm/trackers.yaml`)
2. otherwise, this folder's shared/ copy (`shared/pm-config.example.yaml`,
   `shared/trackers.example.yaml`, `shared/writing-standard.md`)

Config keys used: `approval_gate` (the sign-off step the charter goes to), `tracker` (the
active profile name) and `output_dir` (where the charter is saved). Prose follows
`shared/writing-standard.md`.

## Inputs

- A transcript of the scoping discussion plus any notes, slides or emails. Optional, and the
  best starting point.
- The person who asked for the project, available while the charter is drafted.

## Steps

### 1. Business case first

The purpose, the cost and benefit picture, the scope edges and the early risks all come
from a business case. Run `business-case-from-transcript` on the transcript and supporting
files, then lift from its output. Do not re-derive what it already states.

With no source material, write the Purpose section from what the user tells you and add a
visible line in the charter saying the business case is missing. Suggest producing one once
material exists. If the work is complex and intent is still unclear, the superpowers
`brainstorming` skill, if installed, can help before scope is fixed.

### 2. Draft the charter

Draft with the requester and settle open questions while writing, not during the build.
Use these `## ` headings, exactly, in this order, with nothing extra at that level:

1. **Purpose**: the problem or opportunity, the value, why now, and a short cost against
   benefit view taken from the business case.
2. **Success criteria**: at least three bullets. Each carries a number or threshold that
   can be checked later. A criterion nobody can measure is a defect.
3. **Scope**: two labeled parts, "In scope" and "Out of scope". The exclusions matter as
   much as the inclusions, because they stop later growth. Fold assumptions and constraints
   in here or into Seed RAID; there is no heading for them.
4. **Milestones**: each key output with a calendar date.
5. **RACI**: one table with the columns Activity, Responsible, Accountable, Consulted,
   Informed. At least four activities. Every cell is a comma-separated list of names, or
   `-` when empty. Exactly one Accountable per row. Cover the sponsor, the project lead,
   contributors and approvers.
6. **Budget**: people, tools and spend, with the figure written out.
7. **Seed RAID**: the opening entries for the RAID log (Risks, Actions, Issues,
   Decisions), tagged R#, A#, I# or D#, each with an owner. At least one risk and one
   action. `raid-log-management` maintains them from here.
8. **Approval**: one sentence saying the charter goes to the gate named by `approval_gate`
   in config, and that work starts only after that sign-off. Read the gate name from
   config every time. Never write it into this skill.
9. **Kickoff agenda**: see step 4.

Facts come from the business case or the user. Write a gap as TBD rather than inventing a
value. Save the charter in `output_dir` with a dated filename. The Markdown file is the
canonical output; a `.docx` copy is optional through a docx skill, if installed. If the
workspace has a deliverable review step, send the finished charter through it.

### 3. Set up the tracker

1. Read `tracker` from config and find that profile in `trackers.yaml`.
2. No active profile, or the named one is missing: run `connecting-a-tracker` first, then
   return here.
3. ClickUp, Linear, Jira, Asana or Monday.com: hand the writes to `updating-trackers`. For Linear, also
   follow `structuring-linear-projects` for how the project is shaped.
4. Any other tracker: write through the profile's `write_tools` and read back through its
   `read_tools`. Use the profile's `concepts` names, and its `gaps` handling when a concept
   does not exist in that tool.
5. Plan these creations: the project container, the milestones from the charter with their
   dates, a place for the RAID entries, and a recurring weekly status item. Give each an
   owner and a start date.
6. Show the plan as a table of item, change and field values.
   Nothing is written until the user approves the table.
7. After writing, read back every item, compare it with the table, and report the IDs and
   links and any difference.

### 4. Kickoff

Write an agenda for the opening session with all stakeholders. It covers scope (both
sides), who holds which role, the plan and milestones, how often and through which channel
status is shared, and the agreed definition of finished. Also draft the follow-up notes and
the list of actions assigned in the session, each with an owner. The superpowers
`writing-plans` skill, if installed, can turn the charter into a build sequence after
kickoff.

## Checks before handing over

- All nine headings are present, in order.
- Every success criterion holds a measurable value.
- Scope lists both what is in and what is out.
- Every milestone has a date.
- RACI has the exact columns, four or more rows and one Accountable per row, and every
  name is a real stakeholder from the source.
- Seed RAID entries carry tags and owners, numbered from 1 for each type.
- Approval names the configured gate.
- The business case is cited as the source, or flagged as missing.
- No em dash anywhere.

## Output

- The charter file path.
- The created tracker items with IDs and links.
- The kickoff agenda and the assigned actions.

## Guardrails

- Never write to a tracker before the user approves the table. Read back after every write.
- No secrets in chat or in files. Tracker credentials live in environment variables or the
  connector's sign-in.
- Gate names, escalation roles and output locations come from config, never from this text.
