# updating-trackers

The house standard for writing to ClickUp, Linear, Jira, Asana and Monday.com. It tells an
agent to resolve real IDs before writing, read the current state first, fill the required
fields on every item (status, one owner, a real due date, priority, the current period, an
audit comment), get approval for agent-proposed changes, read back every write, keep work that
lives in more than one tracker in sync under one system of record, and confirm before any bulk
or destructive change.

## Inputs
- A request to change tracked work: "move DEMO-101 to Done", "push the pilot dates a week",
  "reassign Alex's open tasks to Priya", or a reconciliation table the PM approved.
- Access to the tracker's tools, directly or through its agent: `clickup-agent`,
  `linear-agent`, `jira-agent`, `asana-agent` or `monday-agent`.

## Outputs
- The updates themselves, applied in the tracker and read back.
- An update report: each item's ID and URL, old and new values, and anything left for a
  person to decide. See `examples/expected-update-report.md`.

## How to run
Ask for a tracker update in a session where the skill is installed, or invoke it by name
(`updating-trackers`). The `project-manager` agent and the five tracker agents load it for
every write. There is no script; the skill is a procedure the agent follows.

## Prerequisites
- An MCP connection to the tracker with write permission.
- Optional: the tracker's agent from this folder.

## Examples
- `examples/input-request.md`: a synthetic update request against ACME Co. work in Linear and
  ClickUp.
- `examples/expected-update-report.md`: the report the skill should return for it.
