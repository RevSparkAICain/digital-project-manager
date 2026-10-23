# Example input: an update request

Operator: Jane Doe, ACME Co. Request made on 2030-03-11.

> Configuration slipped a week because the vendor delivered the test environment late. Push
> DEMO-104 and DEMO-105 out by seven days, mark DEMO-102 done (Alex finished the config
> review on Friday), and make sure the ClickUp copy of the work-order form task matches.
> Also close every open task in the old "Field Service Planning" list, we don't need it any
> more.

## Current state read before writing (tool data, 2030-03-11)

| Item | Tool | Status | Assignee | Due | Priority | Cycle / list |
|---|---|---|---|---|---|---|
| DEMO-102 Configuration review complete | Linear | In Review | Alex Rivera | 2030-03-08 | High | Cycle 6 |
| DEMO-104 Work-order form configured | Linear | In Progress | Priya Shah | 2030-03-15 | High | Cycle 6 |
| DEMO-105 Technician roles configured | Linear | Todo | Sam Okafor | 2030-03-22 | Medium | Cycle 7 |
| Work-order form configured (mirror of DEMO-104) | ClickUp | in progress | Priya Shah | 2030-03-15 | high | Field Service Rollout |
| "Field Service Planning" list | ClickUp | 12 open tasks | see below | see below | various | n/a |

Team cycles (Linear): Cycle 6 runs 2030-03-04 to 2030-03-17, Cycle 7 runs 2030-03-18 to
2030-03-31, Cycle 8 runs 2030-04-01 to 2030-04-14.

"Field Service Planning" list detail: 12 open tasks. 3 were updated in the last 14 days.
1 is assigned to Jordan Lee, due 2030-03-18. The other 11 are unassigned with no due date.

Exit criterion recorded on DEMO-102: "Config review signed off by the reviewer in a comment."
A sign-off comment from Alex Rivera dated 2030-03-08 is present.
