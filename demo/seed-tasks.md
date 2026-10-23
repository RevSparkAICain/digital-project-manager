# Seed tasks for the demo

The demo transcripts talk about work that is already in the tracker. Load these items before you
run the demo, so the reconciliation table can update and close real items next to the new ones.
Keep the ID at the start of each title; it makes each match easy to see in the table.

There are two examples. The live demo uses the first. The second is the worked example that
ships with the skills, and it also runs offline.

## Live demo: one call, five trackers

`Sample_Transcript_sanitized.docx` is an internal pursuit call about a customer's sustainability
requirements. Its work splits into four workstreams, and each one lives in its own tracker, so
one call updates all five tools:

| Project | Tracker | What it covers |
|---|---|---|
| Building management | Jira | The building management system follow-up, device monitoring |
| Network design | Linear | The high-level design, bill of materials, cabling and PoE |
| LEED advisory | Asana | LEED Gold scope, the architect conversation, green IT principles |
| Specialist outreach | Monday.com | The carbon assessment team, data center and workplace specialists |
| Pursuit admin | ClickUp | Anything that belongs to none of the four |

Create one demo project, board or list per row, named as in the Project column. Then load:

| Title | Status | Project | Tracker |
|---|---|---|---|
| SUS-101 Schedule the building management deep dive with the network vendor | To do | Building management | Jira |
| SUS-102 Decide the building management approach: partner product or our own | In progress | Building management | Jira |
| SUS-103 Network high-level design | In progress | Network design | Linear |
| SUS-104 Confirm the cabling supports high-power PoE | To do | Network design | Linear |
| SUS-105 Clarify the LEED Gold expectations with the customer | To do | LEED advisory | Asana |
| SUS-106 Brief the carbon assessment team on the pursuit | To do | Specialist outreach | Monday.com |
| SUS-107 Send the sustainability requirements summary to the team | In progress | Pursuit admin | ClickUp |

Ask for each tracker's items separately, for example "create SUS-101 and SUS-102 in my Jira
Building management project, with the status shown". Each tracker agent shows its creates and
writes them after you approve.

During onboarding, map the projects when it asks which project lives where. The result in
`pods/pm/pm-config.yaml`:

```yaml
tracker: clickup                 # Pursuit admin, and anything outside the four projects
project_trackers:
  Building management: jira
  Network design: linear
  LEED advisory: asana
  Specialist outreach: monday
```

What the call should do to them. The table is built live from the transcript, so read this as
the expected shape, then check it on the screen:

- SUS-102 closes: the group decided to line up with the network vendor's product.
- SUS-104 closes: the building already has Category 6A cabling, which supports high-power PoE.
- SUS-107 closes: the requirements summary went out before the call.
- SUS-101, SUS-103, SUS-105 and SUS-106 are updated: the deep dive still needs scheduling, the
  design has a target date of the 30th, the LEED question moves to the customer's architect, and
  the carbon team briefing happens before next week's call.
- New items are proposed as creates, among them the bill of materials for the carbon and energy
  footprint, a call on green IT principles, the question list on partitioned grids and solar,
  and the formal notes sent with the recording.
- Owners named in the call who are not members of your tracker stay unassigned, and the table
  says so.

## Offline example: the ACME Weekly Ops Sync

The sample call that ships with the notes skill, a Weekly Ops Sync for the fictional ACME Co.,
talks about seven items:

| Title | Status | Project | Tracker in a multi-tool run |
|---|---|---|---|
| DEMO-101 Plan sixty-day parallel run | In progress | Jira migration | Jira |
| DEMO-102 Intake form wording for new queues | To do | Jira migration | Jira |
| DEMO-103 Vendor driver certification follow-up | To do | PostgreSQL upgrade | Linear |
| DEMO-104 Monitoring vendor renewal pricing | In progress | Monitoring vendor renewal | Asana |
| DEMO-105 Log retention schedule review | To do | Retention schedule | Monday.com |
| DEMO-106 Vendor terms review | To do | Monitoring vendor renewal | Asana |
| DEMO-107 Ping vendor about driver status | To do | PostgreSQL upgrade | Linear |

For a single tracker, ask: "Create the seven DEMO tasks in demo/seed-tasks.md in my demo list,
with the status and project shown." Seven creates count as a bulk change, so the agent shows them
as a table first.

What the sample call does to them, per the worked example in
`.claude/skills/transcript-to-tracked-actions/examples/reconciliation-table.md`:

- DEMO-101 closes: the group dropped the parallel run.
- DEMO-102, DEMO-103 and DEMO-104 are updated in place.
- DEMO-107 closes: the vendor replied.
- The retention-schedule action has no confirmed match, so that row is held for you to decide.
  The worked example offers DEMO-105 and DEMO-106; a live run searches the row's own project
  first, so it may offer DEMO-105 alone.
