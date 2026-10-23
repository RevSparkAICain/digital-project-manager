# Linear API gotchas

Every item here was confirmed by writing test data and reading it back, not taken from the
documentation. Anything inferred says so. Examples use fictional ACME Co. data, and each
one reconciles exactly. Read this file before any scripted build.

Two families of behavior silently corrupt data: the weighted progress math (items 1 to 4)
and the SLA date strip (item 5). Items 6 to 19 are narrower: parameter names, read-back
names, limits, and facts the API does not expose. A closing checklist follows the items.

## 1. Milestone progress is weighted by state type, not done over total

Weights follow the state's `statusType`, never its name:

| `statusType` | Typical states | Weight |
|---|---|---|
| completed | Done | 1.0 |
| started | In Progress, In Review, any custom started-type state added later | 0.25 |
| unstarted | Planned, Todo | 0 |
| backlog | Backlog | 0 |

Basic readings: 3 Done plus 2 In Progress over 5 attached reads 70%. 12 Done plus 2 In
Progress over 20 reads 62.5%.

Effects: a 25% reading can hold zero finished work (one started item). The same work reads
differently as more issues are attached, because started credit is diluted. Never compare
percentages across milestones that use different attachment conventions.

Review-stage examples, for a team with estimates off:

| Case | Attached | API value | Working |
|---|---|---|---|
| A | 8 (In Review 3, In Progress 1, Backlog 4) | 12.5 | 4 started items at 0.25, divided by 8 |
| B | 4 (Done 2, In Review 1, In Progress 1) | 62.5 | 2 plus 2 started items at 0.25, divided by 4 |
| C | 20 (In Review 10, In Progress 6, Backlog 4) | 20.0 | 16 started items at 0.25, divided by 20 |
| D | 20 (Done 4, In Review 8, Backlog 8) | 30.0 | 4 plus 8 started items at 0.25, divided by 20 |

Case C shows the sharpest effect. Ten finished-but-unreviewed items earn a quarter each, so
the reading is 20% although half the attached work is built. A reconciliation table with no
In Review row wrongly blames the API.

Check: recompute from the attached state counts with these weights and compare the result to
the API value.

## 2. Canceled issues leave the denominator

They are not scored as zero. They are removed from the count entirely.

Example: 100 attached, 10 Done, 20 Canceled, 70 Planned. The API returns `progress: 12.5`,
which is 10 over 80, not 10 over 100 (10%).

Effects: a test asserting progress equals done over attached raises a false mismatch whenever
canceled work is present. Canceling the remainder can push a milestone toward 100% with
nothing finished.

Check: subtract the canceled issues from the attached count before dividing.

## 3. Team estimates switch the denominator to points

With estimates off, every issue has size 1. With estimates on, the same weights apply but
each issue is sized by its estimate points.

Example: 4 attached issues sized S=2, S=2, M=3, M=3 (10 points). Both M issues are In
Progress, so 6 points are started. Counted by issue, that would be 2 started items at 0.25
over 4, or 12.5%. Linear reports 15%: 6 points at 0.25 over 10.

T-shirt point scale, largest first: XXXL 21, XXL 13, XL 8, L 5, M 3, S 2, XS 1.

Effect: never compare milestone percentages across teams before confirming both have the same
estimates setting.

Check: find out whether the team uses estimates (see item 11), and size by points when it
does.

## Combined formula

Over the attached issues that are not canceled, add up weight times size, then divide by the
sum of size. Size is 1 per issue with estimates off, or the estimate points with them on.
Cases A to D in item 1 apply it with estimates off, so each size is 1.

## 4. The API value is unrounded; the milestone list shows a whole percent

Example: the API returns 62.5 and the screen shows 63%.

Check: when reconciling against the screen, compare with the rounded value. Against the API,
use the raw one.

## 5. A team SLA policy can remove due dates at creation

This depends on the target team's SLA settings. A team without a policy never shows it, so
find out before a batch.

When the policy covers a priority, issues created at that priority lose `dueDate` and gain
unrequested `slaStartedAt`, `slaBreachesAt` and `slaType`. A policy over Urgent and High hits
every Urgent or High issue created.

- It touches only the covered priorities, and only on creation. Later update-only writes
  strip nothing.
- Timing is asynchronous: the strip can land after your first read, so one read straight
  after the create proves nothing; a date written again later stays.
- Mitigation: after the batch, wait, re-read, and repair each null `dueDate` with an isolated
  `save_issue` call holding only `id` and `dueDate`, then re-read. Never drop an issue's
  priority to escape the policy; that trades correct data for one field.
- Workspace automation changes issues silently; only a diff of sent against returned shows
  it. Verify any field that matters.

Check: after a delay, re-read every created issue and list any null `dueDate`.

## 6. Some tool parameter names differ from the obvious guess

Confirmed from the Linear MCP tool schemas:

- `save_project` takes `addTeams` or `setTeams`, not `team`, and one of them is required on
  create.
- `save_project` takes `addInitiatives` or `setInitiatives`, not `initiative`.
- `save_initiative` has no team parameter, only an optional `leadTeam`.
- `save_issue` takes `assignee`, not `assigneeId`.
- `get_issue` takes `id`, not `query`, unlike the other `get_*` tools.

The `save_issue` parameters that do match the expected name, in no particular order:
`assignee`, `description`, `dueDate`, `estimate`, `labels`, `milestone`, `parentId`,
`priority`, `project`, `state`, `team`, `title`.

Check: read the tool schema before the first call of each tool in a batch.

## 7. `save_milestone` needs `name` on create

Its schema lists only `project` as required, but the tool description demands `name`.

Check: always send `name` when creating a milestone.

## 8. Attachment goes in under one field name and comes out under another

Writes take `milestone`; `list_issues` returns attachment only as `projectMilestone` (its
enum has no `milestone`). Checking the wrong name reports every issue unattached; not
checking hides a real drop.

Check: assert attachment on `projectMilestone`, every time.

## 9. `list_projects` returns at most 50 per page

Most list tools allow 250.

Check: page until `hasNextPage` is false before reporting a count.

## 10. A heavy `list_projects` request exceeds the complexity cap

A large field selection combined with `includeMilestones` goes over the API complexity cap
of 10000 and fails outright.

Check: on a complexity failure, narrow the fields or split the request into two calls.

## 11. An unset `estimate` is omitted, not returned as null

So a missing field does not show that estimates are off for the team.

Check: infer that estimates are on if any issue on the team carries an `estimate`, and label
that as inferred.

## 12. `get_team` exposes no team settings

Its fields stop at id, name, description, icon, timestamps and visibility. The estimates and
cycles settings cannot be read.

Check: infer settings from issue data and mark them inferred.

## 13. An empty `list_cycles` result is ambiguous

It can mean cycles are off, or on with none created. No field tells the two apart.

Check: confirm with a team admin, and mark the value inferred until then.

## 14. Project milestones have no URL

Neither `get_milestone` nor `list_milestones` returns `url`, so a milestone cannot be linked.
Point readers at the project and name the milestone, or link an attached issue; anything that
must be linkable needs another home.

Check: no output link points at a milestone.

## 15. Issues, projects and initiatives return a real `url`

Use it exactly as returned. Never assemble one from a slug pattern, even if the pattern looks
stable.

Check: every link in the output traces to a returned `url` field.

## 16. The roadmap plots only projects and milestones

The timeline shows projects and milestones, never issues, at any zoom; to be on the roadmap
a thing must be one of those two. That is the strongest everyday argument for naming real
milestones.

Check: each item the operator wants on the roadmap is a project or a milestone.

## 17. Markdown links in descriptions are stored in angle-bracket form

`[text](url)` is accepted and stored as `[text](<url>)`, which is CommonMark. This is
normalization, not damage.

Check: normalize the angle brackets before diffing a description against what was sent.

## 18. Hyphen bullets are stored as asterisks

`-` list markers come back as `*` in stored description text. It is cosmetic.

Check: normalize bullet markers before diffing descriptions.

## 19. Transient `upstream_unavailable` (502) errors

Reads and writes alike can hit them. A retry normally succeeds.

Check: the batch retries these calls instead of aborting.

## Verification checklist for a scripted build

Run every line at the end and report each result rather than claiming success.

- [ ] Object counts match the plan: initiatives, projects, milestones, issues.
- [ ] Issue identifiers run contiguously, or each gap is explained.
- [ ] Spot-check every child's `parentId` against the parent its title or spec names; a
  right total can hide crossed wires.
- [ ] `projectMilestone` is set on exactly the intended issues, matching the one attachment
  convention.
- [ ] Children are due strictly before their parent; if the parent sits on the earliest
  allowed date, move the parent out rather than squeeze the child.
- [ ] No null `dueDate` anywhere, above all at priorities an SLA policy covers (item 5).
- [ ] Assignee and labels are present on every issue.
- [ ] Read back each milestone's `targetDate`; a dropped date write fails silently.
- [ ] Each progress reading equals the formula's prediction; report a gap and leave states
  alone.
- [ ] Every field that was written but is missing on read-back is listed.
