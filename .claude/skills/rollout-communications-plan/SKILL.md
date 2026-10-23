---
name: rollout-communications-plan
description: Plan how a workforce hears about a technology change before any copy is written. Use for a rollout, go-live, migration, login or policy change, or scheduled downtime when people must be told and no plan exists yet, or when someone asks who needs to know, how to announce it, or what goes out when. Produces a change profile, an audience matrix ranked by impact (Act, Adapt, Aware), a channel assignment, a dated T-minus send sequence, an approval and handoff path, a measurement plan limited to what the team can collect, a risk list, and a build list for the writing and design agents. Plans only; it writes no copy and sends nothing.
---

# Rollout communications plan

Rollouts go wrong in a predictable way: one long email, sent late, to everyone.
Readers learn to skim past it. This skill prevents that by fixing who hears what, through
which channel, on which day, before a single sentence of copy exists. The plan is the
blueprint that the translator, copywriter and designer build from. `examples/rollout-plan.md`
shows a finished one.

## Where each file comes from

For every file the skill reads, use this order:

1. the project's own file, if present:
   - `pods/comms/comms-config.yaml`
   - `pods/comms/audiences.yaml`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
2. otherwise, this folder's shared/ copy:
   - `shared/comms-config.example.yaml`
   - `shared/audiences.example.yaml`
   - `shared/writing-standard.md`

Say in the plan's header which config was in force. If it was the example, say so plainly.

## What the config decides

Facts about the environment come from the config, never from memory. Write wording that
follows the values:

| Config field | Effect on the plan |
|---|---|
| `channels` | Only entries with `enabled: true` may carry an audience. Leave disabled ones out. |
| `intranet.present` | When false, no step may rely on an internal page link. The durable reference is an attached PDF, written so it makes sense with no link to follow. When true, a page link is allowed. |
| `telemetry` | When open and click rates are false, the measurement section says they are not available and uses the counts listed under "Measurement". |
| `bulletin.sender_role` | The role that sends the IT Bulletin and any targeted email. Name the role, not a person. |
| `requester_role`, `approver_role` | Who owns the wording, and who gives the go-ahead for each send. |
| `time_zone` | Every time in the plan is stated in this zone, named once. |

## Step 1: Intake

Plan from confirmed facts, taken from the project's own record rather than from guesswork.
Collect:

- what is changing, in the project's own terms
- the go-live date and time, and whether the date has moved before
- any outage or cutover window
- who is affected, as the project team sees it
- whether anyone must act, and what happens if they do not
- whether the service desk is briefed and an article exists
- whether the change can be reversed, and how quickly
- the owner, the sponsor, and the role that approves wording
- who owns the channel for each audience group, so finished drafts reach the right sender

Record every unconfirmed item as an open question, and keep it listed in the plan.

## Step 2: Change profile

One table, one row per field: change (a single plain sentence), go-live, outage window,
disruption level, action required, reversibility, earlier announcements that slipped, owner
and approver.

Disruption level sets how heavy the plan is:

| Level | Plan weight |
|---|---|
| None | A single notice |
| Low | A notice plus a reference attachment |
| Noticeable | The standard sequence below |
| Work stops | The full sequence, a team-meeting slot for each Act group, and leader involvement |

## Step 3: Audience matrix

Rank people by how far the change reaches into their work, not by the org chart. Read
`audiences.yaml` (or its example) for each segment's reading grade, length, vocabulary and
verbs, then add one row per group.

Name groups, never distribution lists. Recipient lists belong to whoever owns the channel; the
plan describes groups and never picks recipients. The plan only owes a picture of each group sharp enough for the copy to use
its vocabulary.

| Level | Meaning | Delivery |
|---|---|---|
| Act | Must do something | Most touches, plainest steps, a calendar date |
| Adapt | Sees something new, owes nothing | One notice, one place to look |
| Aware | Not touched, but should hear it occurred | A single roundup line |

Matrix columns: group, level, required step, comfort with technology, the channel that truly
reaches them, their own words for the work, and their leader.

A worked reference for ACME, a mid-size tools-and-parts company:

| Group | Typical reading habit | What lands | What fails |
|---|---|---|---|
| Warehouse and shipping floor | Shared kiosks, short breaks, little desk time | One step, one date, what to tell a driver | Anything needing a desk and ten quiet minutes |
| Customer Support | Between calls, queue-driven | What the caller will see change | Background and rationale |
| Sales and account managers | Phone first, on the road | Customer effect and time cost, under 150 words | Long email, extra admin |
| Operations and procurement | Process-minded, notice step changes fast | The exact step that moves and the cutover time | Vague promises of improvement |
| Finance | Reads for deadlines and approvals | Effect on month-end close | Generic all-staff framing |
| IT and Engineering | Wants the detail | Dependencies, known issues, support load | Simplified text that hides specifics |
| Legal and Policy | Looks for what must be written down | The rule and where it is recorded | Unsupported claims |
| Department leaders | Scans for their own task and the load on their staff | Outcome, risk, what you need | Learning at the same moment as their team |

### Groups that get missed

Check each by name on every plan, and write down how each will be reached:

- staff on shared workstations with no reading window
- remote and field staff who cannot reach internal resources until they sign in
- off-hours and shift workers who hit the change while the service desk is empty
- contractors and vendors holding company accounts
- people on leave during the window, who come back to a change nobody mentioned
- new hires being trained on the old way during the window

### Coverage rule

Every Act group needs all four of these, or the plan is unfinished: a bulletin that states the
action and its date; a leader touch, so a manager can answer a hallway question; a reference
the person can keep that stands alone; one named help path.

## Step 4: Channels

Use only enabled channels. Typical ACME defaults are email, Teams and a slot in a team
meeting. Everything else rides one of them.

| Channel | Good for | Poor for |
|---|---|---|
| Email (the IT Bulletin, or a department-only message) | Announcing, keeping a record, listing the steps | Discussion, long nuance |
| Teams (channel post, or a chat with one leader) | A nudge for skimmers, chasing a cascade | Anything that must be found later |
| Team meeting (guest slot, with a deck) | Commitment, questions, groups likely to push back | Reaching everyone at once |

Attachments and graphics ride a channel: the leader packet, a one-pager or reference card, an
infographic, an FAQ, the deck, a calendar invite. With no intranet configured, give each
Act group an attached PDF in place of a link.

## Step 5: Send sequence

Convert T-minus offsets to real dates from the go-live date. Starting point, adjusted for
disruption level:

| When | Piece | Audience |
|---|---|---|
| T-21 | Leader packet | Leaders |
| T-14 | First IT Bulletin, a heads-up | Everyone affected |
| T-7 | Department emails with reference and FAQ attached; team-meeting slots booked | Act groups |
| T-3 | Teams post; talking points updated | Act groups and leaders |
| T-1 | Reminder the day before; the action and nothing else | Act groups |
| T-0 | Go-live notice | Everyone affected |
| T+2 | Adoption nudge with the common issues | Act groups |
| T+14 | Wrap-up | Everyone affected and leaders |

Each row also names an owner and an approver. Rules:

- The first notice is never the day of the change.
- Leaders hear before their teams, every time. A manager caught off guard in front of staff
  becomes the loudest objector.
- Look at the calendar before fixing dates: other rollouts, month-end, quarter close and
  holidays all compete. Two bulletins landing in one week split the readers' attention.
- A same-day or emergency change gets only the go-live notice and the adoption nudge; the
  notice says outright that warning was brief, and gives the reason.

## Step 6: Approvals and handoff

| Step | Role |
|---|---|
| Dates and facts | Whoever owns the project or the technology |
| Wording | The `requester_role`; the `approver_role` signs off |
| Sensitive-area framing, when relevant | The owner of that area, before anything goes wide |
| Send | The `bulletin.sender_role` |
| Recipient lists | The channel owner |

The sender sends exactly what they receive. Every package therefore leaves the pod complete:
subject line, body, plain-text version, target group, send date and time. Anything the
sender must correct is a defect in the package.

## Step 7: Measurement

Pick only measures the team can collect. When `telemetry` shows open and click rates as off,
write that they are not available and rely on:

- service desk tickets by category before and after (capture the starting figure ahead of go-live, since a
  later comparison has nothing to stand on)
- a count from the system itself, such as sign-ins, enrollments or records processed
- who showed up to team-meeting slots, and what they asked, since questions reveal gaps in the copy
- reactions and replies on the Teams post, as a rough sign anyone saw it
- one question to leaders afterward: did your team know what to do?

If telemetry is on, rates may be added and labelled as secondary.

## Step 8: Risks and build list

Name the risks that apply: short notice; competing rollouts; a group with no reliable channel;
a department that will read this as extra work or lost control; an earlier announcement that
slipped; a service desk not staffed for the load the announcement creates; an action nobody
enforces.

Close with the build list. Each asset gets a row giving its audience, the agent who makes it,
the skill that agent uses, when the draft is due and when it goes out.

| Asset | Owner agent | Skill |
|---|---|---|
| Message core | `tech-translator` | `plain-language-translation` |
| IT Bulletin and department variants | `comms-copywriter` | `it-bulletin` |
| Leader packet and FAQ | `comms-copywriter` | `leader-cascade-kit` |
| Graphics and one-pager | `comms-designer` | `comms-visual-assets` |
| Team-meeting deck | `comms-designer` | `rollout-roadshow-deck` |

## Output

Save the plan to `output_dir` as `YYYY-MM-DD-rollout-plan-<topic>.md`. Return it with the
recommendation on top: the proposed sequence in one paragraph, then the dated table, the build
list, outstanding approvals, and open questions. Route a document form through the
`deliverable-review` skill when it is installed; otherwise say the plan is unreviewed.

## Writing standard

All text this skill produces follows the house-style writing standard, read in the lookup order
above: plan prose, table cells, file names and the report back. Treat an em dash as a build
failure. Start with the answer.
