---
name: updating-trackers
description: Use when updating project data in ClickUp, Linear, Jira, Asana or Monday.com. The standard for setting statuses, owners, due dates, priorities, sprints and cycles, comments and dependencies, for getting approval and reading back every write, and for keeping trackers consistent when work is tracked in more than one.
---

# Updating trackers

## Overview
Keep the trackers an accurate, trustworthy source of truth. A board that lies is worse
than no board. Update deliberately, resolve real IDs, and never guess.

## Who writes
Each tracker has one agent that owns its writes. Hand the write to it, or use that tracker's
own tools when this skill runs standalone.

| Tracker | Agent | Where work lives | Item | How status changes | Comment |
|---|---|---|---|---|---|
| ClickUp | `clickup-agent` | Space, Folder, List | Task | the task's Status | task comment |
| Linear | `linear-agent` | Team, Project, Milestone, Cycle | Issue | the issue's workflow state | comment |
| Jira | `jira-agent` | site, Project (key), Sprint | Issue (key such as OPS-12) | a workflow transition, never a direct status set | issue comment |
| Asana | `asana-agent` | Workspace, Team, Project, Section | Task | `completed`, plus the section or a status custom field | comment (story) |
| Monday.com | `monday-agent` | Workspace, Board, Group | Item | the board's status column value | update |

Any other tracker writes through its profile in `pods/pm/trackers.yaml`, set up once by
`connecting-a-tracker`.

## Before you write
- **Resolve, don't guess.** Look up the real container, status or transition, column, and
  assignee IDs first. Never pass a display name where the tracker wants an ID.
- **Read the current state** of the item before changing it, so you know what you are
  overwriting.

## Update standard (every item should have)
- **Status** that matches reality (not "in progress" for something untouched in weeks).
- **Owner:** a single accountable person.
- **Due date** that is real; if it slipped, change the date AND note why in a comment.
- **Priority** set intentionally for anything active.
- **Period:** the sprint or cycle (Jira, Linear), list or sprint (ClickUp), section
  (Asana) or group (Monday.com) that reflects the current period, where the team uses one.
- **A comment** capturing material changes, decisions, and blockers: the audit trail.

## Cross-tool consistency
When the same work exists in more than one tracker:
- Pick the **system of record** for that work and keep the others in sync (or link them).
- Flag genuine **duplicates** rather than silently updating both and letting them drift.
- Mirror status changes and dates; note the counterpart's ID in a comment.
- `mirror_tracker` in `pods/pm/pm-config.yaml` names a tracker that gets a copy of every row
  a transcript writes. The row's own tracker is the system of record, and the copy's
  description links back to it (see `transcript-to-tracked-actions`, Step 8).

## Status hygiene rules
- Move to **done/complete only** when the acceptance/exit criteria are actually met.
- Don't leave items unassigned or perpetually "in progress": chase or re-plan them.
- Reflect blockers as a blocked status/flag plus a comment naming the blocker and owner.

## Safety
- **Approve agent-proposed changes first.** Changes the agents worked out (from a transcript,
  mail, a status report, a sync or a plan) are shown as a table and written only after the PM
  approves it. A direct request that names its own change is the approval for exactly that
  change.
- **Read back every write** and compare the stored values with what was sent. Report any
  difference; never fix one silently.
- **Confirm before bulk or destructive changes** (creating, closing or deleting more than five items at once, mass
  reassignment, moving lists, boards or projects). State exactly what will change and get
  go-ahead. A PM's pre-approval of a run's creates and updates is that go-ahead; closes and
  deletes still need their own.
- **Use the named tools.** A server's general-purpose tools (raw API, GraphQL or code
  execution) skip the checks above. Use them only to read, and only when no named tool
  returns what you need.
- Never change sharing/permissions as a side effect of an update.

## Output
The concrete updates made, each with the item **ID and URL**, old → new values,
and anything you intentionally left for a human to decide.

See `examples/` for a sample request and the update report it should produce.
