# Example: progress reconciliation

A milestone shows a percentage that someone doubts. This example reconciles four of them
with the weighted formula in `references/api-gotchas.md` (items 1 to 3 and the combined
formula).

Weights by `statusType`: Done 1.0; In Progress and In Review 0.25; Todo, Planned and
Backlog 0; Canceled issues are excluded from the count. With team estimates off, every issue
has size 1. With estimates on, size is the estimate points.

Rows 1 to 3 belong to the Field Service App Rollout project, whose team has estimates off
(see `examples/input-brief.md`). Row 4 belongs to Dock Scheduling Rollout on team `WHSE`,
which uses T-shirt estimates (see `references/workspace-profile.template.md`). Milestone
names follow `examples/expected-structure.md`.

## Input

| # | Milestone | Estimates | Attached states | API value |
|---|---|---|---|---|
| 1 | `M03 Pilot Live` | off | Done 6, In Progress 4, Todo 2 | 58.33 |
| 2 | `M05 Wave 1 Rolled Out` | off | Done 10, Canceled 20, Planned 70 | 12.5 |
| 3 | `M02 Integrations Live in Test` | off | Done 0, In Review 8, Backlog 4 | 16.67 |
| 4 | `Dock Scheduling Rollout: M01 Dock Calendar Configured` | on | In Progress 2 (sizes M=3 and M=3), Todo 2 (sizes S=2 and S=2) | 15.0 |

## Expected output

| # | Attached | Excluded | Credit | Denominator | Predicted | Reconciles |
|---|---|---|---|---|---|---|
| 1 | 12 | none | 7 (Done 6, plus In Progress 4 at 0.25) | 12 | 58.33 | yes |
| 2 | 100 | 20 Canceled | 10 | 80 | 12.5 | yes |
| 3 | 12 | none | 2 (In Review 8 at 0.25) | 12 | 16.67 | yes |
| 4 | 4 issues, 10 points | none | 1.5 points (6 started points at 0.25) | 10 points | 15.0 | yes |

## Working and reading

**1. `M03 Pilot Live`.** Credit 7 of 12 attached, which is 58.33%. The milestone list
displays 58%, the rounded form of the same value. Meaning: half the pilot work is Done
and a third is under way; the weighted reading of 58.33 is correct.

**2. `M05 Wave 1 Rolled Out`.** Credit 10 of 80 counted issues, which is 12.5%. The 20
Canceled issues leave the denominator. Dividing Done by everything attached gives 10 of 100,
which is 10%, and would wrongly report a mismatch. Meaning: an eighth of the countable work
is done, and the Canceled items do not drag the bar down.

**3. `M02 Integrations Live in Test`.** Credit 2 of 12 attached, which is 16.67%. Nothing
is Done. The 8 items awaiting review each earn a quarter, so the bar moves although no
issue has closed. Meaning: nothing is finished, 8 items are waiting on review.

**4. `Dock Scheduling Rollout: M01 Dock Calendar Configured`.** Credit is 6 started points
x 0.25 = 1.5 points, over a denominator of 10 points: 1.5 / 10 = 15.0%. Counted per issue it
would be half a credit over 4 issues: 0.5 / 4 = 12.5%, which is the wrong basis here.
Estimates move the denominator to points. Meaning: the two medium issues are under way and
carry most of the weight.

## Closing rule

Give the reading, the working and a plain-language meaning for each milestone. All four
reconcile. When one does not, report the mismatch as a finding and never change issue states
to force the number.
