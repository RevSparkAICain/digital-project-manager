# Rollout plan: Handheld scanner app update

Prepared by Jane Doe, project lead. Config in force: `comms-config.example.yaml` (the example
values; no project config exists).

## Change profile

| Field | Value |
|---|---|
| Change | The warehouse handheld scanners move to a new version of the inventory app. |
| Go-live | Monday, March 18, 2030, 6:00 AM, local time |
| Outage window | Sunday, March 17, 2030, 8:00 PM to Monday, March 18, 2030, 5:30 AM: scanners cannot look up stock |
| Disruption level | Noticeable |
| Action required | Yes: sign in once on the new version before the first pick on Monday |
| Reversible | Yes, within 2 hours |
| Earlier announcement that slipped | No |
| Owner and approver | The project owner owns the facts; the IT manager approves each send |

Open question: does the night shift reach the service desk before 6:00 AM? The project owner
to confirm by March 4, 2030.

## Audience matrix

| Group | Level | What they must do | Depth | How they receive information | Their words | Leader |
|---|---|---|---|---|---|---|
| Warehouse pickers and packers | Act | Sign in on the new version before the first pick | Low | Shared kiosk, short breaks | pick, scan, the bin | Shift lead |
| Night shift | Act | Same step, before 6:00 AM, with no service desk on site | Low | Leader and printed card only | pick, the bin | Night supervisor |
| Receiving and procurement | Adapt | Notice the new screen layout when logging a delivery | Low | Email at a desk | receipt, PO, the dock | Operations manager |
| Customer Support | Adapt | Know that stock counts may lag until 6:30 AM | Low | Between calls | case, the queue | Support lead |
| Sales and account managers | Aware | None | Low | Phone | quote, the account | Sales director |
| Finance | Aware | None | Low | Email | entry, the close | Controller |
| IT and Engineering | Act | Staff the cutover and the rollback path | High | Direct from the project | deploy, roll back | IT manager |

Groups that get missed, each checked by name:

- Shared workstations: Warehouse kiosk users get a printed card at the kiosk.
- Remote and field staff: two traveling reps use a loaner scanner; their manager carries the
  message.
- Shift and after-hours: the night shift is an Act group with its own leader touch.
- Contractors: temporary pickers from the staffing agency are briefed by the shift lead.
- Staff on leave: the T-0 notice is resent on return through the leader.
- New hires: the onboarding trainer receives the one-pager on March 11, 2030.

Every Act group has a bulletin, a leader touch, a reference it can keep and one help path
(the IT Service Desk phone line).

## Channels

Enabled channels per config: email, Teams, team meeting. No intranet is configured, so the
durable reference for every Act group is an attached PDF, not a link.

| Audience | Channels | Why |
|---|---|---|
| Warehouse pickers and packers | Team meeting at shift start, printed card, leader | Little desk time; the card stays at the kiosk |
| Night shift | Leader chat in Teams, printed card | No daytime meeting; the card is the reference |
| Receiving and procurement | Department email with an attached PDF | Reads at a desk |
| Customer Support | Teams post, then one line in the department email | Quick nudge between calls |
| Sales, Finance | One line in the IT Bulletin roundup | Aware only |
| IT and Engineering | Direct email with the cutover runbook attached | Needs full detail |

## Send sequence

Go-live is March 18, 2030. All times local.

| Date | Offset | Piece | Audience | Owner | Approver |
|---|---|---|---|---|---|
| Mon, Feb 25, 2030 | T-21 | Leader packet | Shift leads, department leaders | comms-copywriter | IT manager |
| Mon, Mar 4, 2030 | T-14 | IT Bulletin 1, heads-up | Everyone affected | comms-copywriter | IT manager |
| Mon, Mar 11, 2030 | T-7 | Department emails with attached PDF and FAQ; shift-start slots booked | Act groups | comms-copywriter | IT manager |
| Fri, Mar 15, 2030 | T-3 | Teams post and updated talking points | Act groups and leaders | comms-copywriter | IT manager |
| Sun, Mar 17, 2030 | T-1 | Reminder, action only | Act groups | comms-copywriter | IT manager |
| Mon, Mar 18, 2030 | T-0 | Go-live notice | Everyone affected | comms-copywriter | IT manager |
| Wed, Mar 20, 2030 | T+2 | Adoption nudge with the three common sign-in problems | Act groups | comms-copywriter | IT manager |
| Mon, Apr 1, 2030 | T+14 | Wrap-up | Everyone affected and leaders | comms-copywriter | IT manager |

Calendar check: no competing rollout found. March month-end falls after the window, and no
holiday sits inside it.

## Approvals

| Step | Role |
|---|---|
| Facts and dates | Project owner |
| Wording | Project lead (requester role), go-ahead from the IT manager (approver role) |
| Sensitive-area framing | Not needed: no sensitive area touched |
| Send | IT Service Desk, from the bulletin mailbox |
| Recipient lists | The channel owner |

Each package handed to the IT Service Desk holds the subject line, the body, the plain-text
version, the target group, and the send date and time.

## Measurement

Open and click rates are not available (the config has telemetry off), so the plan uses counts.

| Measure | Source | Baseline | Read on |
|---|---|---|---|
| Service desk tickets tagged scanner | Service desk | Weekly count for February 2030, captured March 1, 2030 | T+14 |
| Scanners signed in on the new version | The app's own sign-in count | 0 | T+2 |
| Shift-start slot attendance and questions asked | Shift leads | n/a | T+2 |
| Reactions and replies on the Teams post | Teams | n/a | T+2 |
| Leader question: did your team know what to do? | Reply to a one-line Teams chat | n/a | T+7 |

## Risks

| Risk | Effect | Mitigation | Owner |
|---|---|---|---|
| Night shift has no one to call before 6:00 AM | Scanners sit unused and picks stall | Night supervisor holds the printed card and a phone number for the on-call engineer | Project owner |
| Pickers read the first bulletin as extra work | Low sign-in on Monday | Shift leads present the one step at shift start | Shift leads |
| Service desk overloaded at 6:00 AM | Long hold times | Extra desk cover from 5:30 AM to 8:00 AM | IT manager |
| Temporary pickers never see an email | They try the old version | Staffing agency briefing on March 14, 2030 | Project lead |

## Build list

| Deliverable | For | Made by | Using | Draft due | Goes out |
|---|---|---|---|---|---|
| Message core | Everyone | tech-translator | plain-language-translation | Feb 18, 2030 | n/a |
| Leader packet and FAQ | Leaders | comms-copywriter | leader-cascade-kit | Feb 21, 2030 | Feb 25, 2030 |
| IT Bulletin 1 | Everyone affected | comms-copywriter | it-bulletin | Feb 28, 2030 | Mar 4, 2030 |
| Printed kiosk card (PDF) | Pickers, night shift | comms-designer | comms-visual-assets | Mar 6, 2030 | Mar 11, 2030 |
| Shift-start deck | Warehouse shifts | comms-designer | rollout-roadshow-deck | Mar 6, 2030 | Mar 11, 2030 |
