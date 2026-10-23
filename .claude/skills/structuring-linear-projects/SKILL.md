---
name: structuring-linear-projects
description: "Settle the shape of work in Linear before or while it is built: initiative or none, the project, dated-state milestones, epic and issue depth, which issues attach to each milestone, and blocking links. Use for a new Linear project, a project that has grown hard to read, set up a project in Linear, milestone versus epic versus issue questions, a stuck or misleading progress bar, a rollout or migration plan, or any bulk build through the API. Load it before a scripted build: it holds the SLA date-stripping policy and the weighted progress math."
---

# Structuring Linear projects

This skill decides how a body of work is laid out in Linear and, when asked, builds it. It
also carries the measured API behaviors that matter on a scripted build, plus a closing
verification checklist (the end of `references/api-gotchas.md`). Use it on a bare "set up a
project in Linear" and on a question about one level, such as only the milestones.

## Where this skill sits

| Question | Owner |
|---|---|
| What the project is: scope, owner, target date | `project-charter-and-kickoff` |
| How the project is shaped in Linear | this skill |
| Writing a status, assignee, date or dependency correctly | `updating-trackers` |
| Risks and how they are tracked | `raid-log-management` |

Order of work: charter, then structure, then field writes. With no charter yet, structuring
is early, so route to the charter skill first. The charter skill and the RAID skill are
optional installs. If either is missing, take the purpose, scope, owner and target date
straight from the operator, and fold the risks into the structure proposal.

## Inputs

- The chartered basics: purpose, scope, owner and target date.
- Optional: an existing Linear project to restructure.
- Optional workspace config: copy `references/workspace-profile.template.md` to
  `references/workspace-profile.md`, fill it in (teams, keys, estimates, cycles, SLA
  policies, states and their `statusType`, labels, initiatives, routing for new work) and
  keep it private, because it holds workspace IDs. Read the filled copy when building in
  that workspace. If it is absent, ask the operator for the team, the estimates setting and
  the SLA policy instead of guessing.
- For builds: a Linear connection (MCP server or API) with write rights.

## Why shape is costly to change

- Progress is computed, never typed. Issue states feed milestone attachment, attachment
  feeds project progress, and project progress feeds the initiative bar. Every shape choice
  changes that number.
- Linear never issues a number twice, so 200 issues permanently use up 200 numbers on the
  team.
- Structure changes are hand work and lose information: a moved issue leaves its history
  split across two projects, and a rename changes the URL slug. Settle the shape before any
  issue exists.

## Decision sequence, top down

Skipping a level leaves a flat pile of issues with nothing to report against.

### 1. Initiative or none

- Add one only once three or more projects share a goal; over one project it is an extra
  page that tells you nothing.
- The API allows sub-initiatives. Treat a nested initiative like a four-level issue tree:
  one layer probably wants to be a project.

### 2. The project

- A project must be able to finish. Ask what its closing day looks like: a rollout has one,
  upkeep does not (team backlog or recurring cycle). A single checkpoint is a milestone in a
  bigger project.

### 3. Milestones

Milestones matter most, since they are what people outside the delivery team see.

- Each milestone names a verifiable condition that holds by a date. It is never an activity.
  Test, answered yes or no: has it happened?
- Good: "Pilot Live", "Legacy System Decommissioned". Bad: a bare "Testing" or "Migration
  work", which name effort and never become true.
- Aim for five to twelve: at one a week they are sprints renamed; at two in six months they
  carry no signal.
- Number them in date order with a leading zero (`M01`, never `M1`), so every view sorts
  them chronologically.
- Milestones are flat and have no parent field. All hierarchy inside a project lives in
  issues.
- Date a milestone on the day its condition first becomes true; a slip moves every later
  milestone with it.

### 4. Issue tree depth

- "Epic" and "sub-issue" are only positions of Linear's one work object: an issue with
  children, an issue with a parent. Linear handles three levels correctly.
- Default to two levels: an epic and its children. Add a third only when the middle tier is a
  real deliverable with its own owner and finish date. A middle tier that only groups should
  be a label.
- Each extra level hides the bottom further while costing the same upkeep; past three nobody
  reads the leaves.

| Level | Owner | Children | Span |
|---|---|---|---|
| Epic | One accountable person | 3 to 8 | 2 weeks to 2 months |
| Issue | One person who handles it fully | Usually a checklist | 1 to 10 working days |
| Sub-issue | One person | None | 1 or 2 days |

- Epics never show a percentage; Linear calculates progress for milestones and projects
  only. A group that needs a number becomes a milestone. Expecting an epic bar is the most
  frequent structural error.

### 5. Milestone attachment

- Progress counts only issues attached to the milestone, and the team chooses what attaches,
  so identical work can report different numbers.
- Default: attach epics and their children.
- Worked comparison on the same work (5 epics with 3 children each; 3 epics finished with
  all their children; the other 2 epics In Progress with children not started). Epics only:
  denominator 5, reads 70%. Epics plus children: denominator 20, reads 62.5%. The gap is
  7.5 points.
- Three reasons to prefer the larger denominator. Child completion shows (under epics only,
  9 of the 15 children can be done and the bar does not move, since only the 5 epic states
  count). No single item swings the bar (with a denominator of 5, one epic changing state
  moves it 5 to 20 points). The denominator tracks real volume.
- Attaching everything is bookkeeping: choose one convention per project and hold it, or
  milestone figures stop being comparable.

### 6. Dependencies

- Hierarchy says nothing about order.
- Log a blocker when it is discovered, usually mid-flight.
- `blocks` / `blocked by` mark true sequence only: B cannot start without something A
  delivers. Neat ordering, or one person doing both, is not a reason.
- Hierarchy is composition; a block is sequence. Imagine the parent deleted: if the children
  are still meaningful work, the link should have been a dependency. A parent implies one
  owner, so another team's deliverable filed as a child is hidden from them.
- External blockers (a vendor, another department, a signature) still get an issue.

## Building

- Show the build plan first: one row per object with its parent and key fields. Build only
  after the PM approves it.
- For a handful of objects, use the Linear UI. Before a scripted build, or one above roughly
  twenty issues, read `references/api-gotchas.md`.
- Build in parent order: initiative, project, milestones, epics, children. When the server has
  no initiative tool, create the initiative in the Linear UI, or skip it.
- Canary: create the first milestone's whole subtree, compare every field on read-back, then
  create the rest; a dropped field found at 20 objects is cheap, at 200 it is a cleanup.
- After each batch, read the objects back. A success response proves the call returned, not
  that each field was stored; compare sent with returned.
- Teams with an SLA policy can strip due dates at creation. The repair is to wait, re-read,
  and write each missing `dueDate` alone (see item 5 in the gotchas).
- Assert attachment on `projectMilestone`, the name the field is read back under.
- Finish with the checklist at the end of `references/api-gotchas.md`. At minimum: object
  counts, each child's parent, a uniform attachment convention, each child date before its
  parent's, and no field silently missing. Report what was checked, never a bare "done".

## Structural smells

| Symptom | Fix |
|---|---|
| A parent named for a category, holding unrelated items that end on different dates | Replace the grouping with a label and a saved view, then remove the parent |
| Twenty-six milestones, one per fortnight | Keep only the 5 to 12 checkpoints that matter; cycles hold the two-week rhythm |
| A milestone called "Testing" or another activity | Name the condition the activity is meant to achieve |
| An epic with one child only | Fold it into one issue and use its checklist |
| Four tiers where tier three means nothing | Turn the empty tier into labels |
| An initiative containing a single project | Remove the initiative or add the projects it should hold |
| A deep tree whose owner wants a percentage | Put the group under a milestone |
| Work sitting outside any project | Move it into a project, or record that it is deliberately untracked |

## Worked skeleton

A starting point, not a fixed template.

```
Initiative (only at 3+ projects)
  Project: <name>, target date <YYYY-MM-DD>
    M01 <state>   <date>      e.g. Configuration Complete
    M02 <state>   <date>      e.g. Integrations Live in Test
    ...
    M08 <state>   <date>      e.g. Hypercare Exit
      Epic (3-8 under each milestone)
        Issue (3-8 per epic, attached to the same milestone)
    blockers drawn across milestones wherever sequence is real
```

The eight-milestone list in `examples/expected-structure.md` (M01 to M08) is a ready model.
Outsiders track milestones; the epics and issues beneath them are the team's working detail.

## Outputs

- A structure proposal: whether an initiative is used, the milestones with dates, how epics
  and children are laid out, the attachment convention and the dependencies. The shape is in
  `examples/expected-structure.md`: a recommendation line, a Decisions table (Level,
  Decision, Why), a Milestones table (Milestone, Target date, True when), notes on any
  requested progress bars, a sample issue layout and build notes. The matching request is
  `examples/input-brief.md`.
- On a build request: the Linear objects, built canary first, then a report that runs the
  closing checklist of `references/api-gotchas.md` and gives each check's result.
- When a progress figure looks off: reconcile it with the weighted formula, laid out as in
  `examples/progress-reconciliation.md` (the reading, the working, whether it reconciles, and
  what it means in plain language). Report a mismatch as a finding. Never change states to
  force the number.

## Quality checks

- Each milestone passes the has-it-happened test and carries the date it becomes true.
- Five to twelve milestones, zero-padded and date-ordered.
- Tree depth is two unless a middle deliverable has its own owner and date.
- One attachment convention across the whole project.
- Dependencies are `blocks` relations, not hierarchy, and external blockers have issues.
- After a build, every item of the gotchas checklist was run and reported.

## Handoffs

- `project-charter-and-kickoff` comes before this skill.
- `updating-trackers` governs every field write once the structure is settled.
- `raid-log-management` tracks the risks.
- `project-status-reporting` reports on the project afterward.
- The `project-manager` and `linear-agent` agents read this skill ahead of every Linear
  build. There is no script: the agent applies the formula and the checks.
