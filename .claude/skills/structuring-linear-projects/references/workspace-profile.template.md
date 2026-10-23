# Linear workspace profile (template)

Copy this file to `workspace-profile.md` in the same folder and fill it in from your own
workspace. The skill reads the filled copy when it builds or restructures work there. The
example rows describe a fictional ACME Co. workspace; replace them.

The filled copy holds workspace IDs. Keep it in your private workspace, never in a public
repo.

## Contents

1. Workspace
2. Teams
3. Workflow states
4. Cycles
5. Labels
6. Initiatives
7. Picking a home for new work

---

## 1. Workspace

| Field | Value |
|---|---|
| Workspace slug | `<your-slug>` (example: `acme`) |
| Linear connection used by the agent | `<MCP server name or API key reference; never the key itself>` |
| Sandbox workspace, if any | `<slug>`, and whether the agent's connection can reach it |

How to fill it: read the slug from any issue URL the API returns. Confirm which workspace
the connection writes to before any write; a sandbox and production workspace can share the
same team names.

## 2. Teams

| Team | Key | ID | Estimates | Cycles | SLA policy | Time zone | Owns |
|---|---|---|---|---|---|---|---|
| Platform | `PLAT` | `<team-uuid>` | off | on, 2-week | Urgent/High strip `dueDate` on create | UTC | Infrastructure and internal tooling |
| Field Operations | `FOPS` | `<team-uuid>` | off | off | none | UTC | Field service rollouts |
| Warehouse | `WHSE` | `<team-uuid>` | T-shirt | off | none | UTC | Warehouse equipment and process changes |
| `<team>` | `<KEY>` | `<team-uuid>` | `<off / T-shirt / points>` | `<on, cadence / off>` | `<describe or none>` | `<tz>` | `<scope>` |

How to fill it: `list_teams` gives names, keys and IDs. `get_team` does not expose settings,
so infer estimates from issue data (an `estimate` present on any issue means they are on)
and cycles from `list_cycles` (empty is ambiguous; ask a team admin). Mark each inferred
value as inferred.

## 3. Workflow states

Record each team's states in board order with their `statusType`, because progress weights
follow the type, not the name.

| Team | State | statusType | Weight | ID |
|---|---|---|---|---|
| PLAT | Triage | triage | n/a | `<state-uuid>` |
| PLAT | Backlog | backlog | 0 | `<state-uuid>` |
| PLAT | Todo | unstarted | 0 | `<state-uuid>` |
| PLAT | In Progress | started | 0.25 | `<state-uuid>` |
| PLAT | In Review | started | 0.25 | `<state-uuid>` |
| PLAT | Done | completed | 1.0 | `<state-uuid>` |
| PLAT | Canceled | canceled | excluded | `<state-uuid>` |

Note any custom state a team added, and its type. A custom started-type state (for example
`Ready for Release`) weights 0.25 like any other.

## 4. Cycles

| Team | Cycles | Cadence | Starts on | Actively used |
|---|---|---|---|---|
| PLAT | on | 2 weeks | Monday | yes |
| FOPS | off | n/a | n/a | n/a |
| WHSE | off | n/a | n/a | n/a |

## 5. Labels

| Group | Labels | Scope | Notes |
|---|---|---|---|
| Component | `Mobile`, `Backend`, `Integrations` | workspace | Use instead of a parent issue for grouping |
| Phase | `Phase A`, `Phase B`, `Later` | FOPS | Rollout grouping |
| Reporting | `exclude-from-reports` | workspace | Marks sample or scaffolding issues |

Record label IDs only if the agent writes labels by ID. Note any label that marks
example-only or test data so reports can exclude it.

## 6. Initiatives

| Initiative | Projects | Lead team | Notes |
|---|---|---|---|
| Warehouse Modernization | Warehouse Scanner Refresh, Dock Scheduling Rollout, Inventory Recount Automation | WHSE | 3 projects, so it earns an initiative |
| `<initiative>` | `<projects>` | `<team>` | `<notes>` |

Note how many active projects sit under no initiative, so a portfolio read knows what it is
missing.

## 7. Picking a home for new work

Write the routing rules the skill should apply when someone asks to set up new work.

| If the work is about | Team | Initiative | Notes |
|---|---|---|---|
| Infrastructure, servers, internal tools | PLAT | per project | Mind the SLA policy on Urgent/High |
| Field service devices and rollouts | FOPS | none (one project in this area) | Estimates off: progress counts issues |
| Warehouse equipment and processes | WHSE | Warehouse Modernization | Estimates on: progress is point-weighted |
| Anything else | ask the operator | n/a | Do not guess a team |
