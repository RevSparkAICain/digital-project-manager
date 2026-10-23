# structuring-linear-projects

Decides and builds the shape of a project in Linear: whether it needs an initiative, which
milestones are real dated checkpoints, how deep the issue tree goes, which issues attach to
each milestone so progress means something, and where the dependencies are. It also carries
Linear API behaviors that quietly damage data on a scripted build: weighted milestone
progress, the canceled-issue denominator, estimate weighting, an SLA policy that can remove
due dates, and a field written under one name and read back under another. A verification
checklist closes the list.

## Inputs
- A chartered project: purpose, scope, owner, target date (from
  `project-charter-and-kickoff`, an optional skill; if it is not installed, the operator
  states them).
- Optional: an existing Linear project to restructure.
- Optional: a filled `references/workspace-profile.md` describing your teams, states,
  labels and cycles.

## Outputs
- A structure proposal: initiative decision, dated milestone list, epic and child layout,
  attachment convention, and recorded dependencies. See `examples/expected-structure.md`.
- When asked to build: the objects in Linear, built canary first, and a verification report
  against the checklist in `references/api-gotchas.md`.
- When a progress number looks wrong: a reconciliation against the weighted formula. See
  `examples/progress-reconciliation.md`.

## How to run
Ask to "set up <project> in Linear", "restructure this project", or "why is this milestone
at 25%?", or invoke the skill by name. The `project-manager` agent and `linear-agent` load
it before any Linear build. There is no script; the formula and checks are applied by the
agent.

## Prerequisites
- A Linear connection (the Linear MCP server or API access) with write permission for builds.
- Recommended: copy `references/workspace-profile.template.md` to
  `references/workspace-profile.md` and fill it in. Keep the filled copy private.

## Examples
- `examples/input-brief.md`: a synthetic ACME Co. project brief.
- `examples/expected-structure.md`: the structure the skill should propose for it.
- `examples/progress-reconciliation.md`: milestone state counts and the progress values the
  formula predicts.

The examples use `DEMO-` issue identifiers as placeholders whatever team the issue sits on;
a real build gets the team's own key.
