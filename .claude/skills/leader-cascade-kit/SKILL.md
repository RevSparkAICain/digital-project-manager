---
name: leader-cascade-kit
description: Build the packet that department leaders and managers use to pass a technology change down through the organization. Use when a rollout needs managers to speak for it instead of relying on an all-staff email, for example "brief the leaders", "write manager talking points", "cascade this through the managers", "what do I tell my department", or when a department is likely to push back, has little time at a desk, or will put hallway questions to its manager. Produces the manager email, the dated ask, talking points, a paste-ready team blurb, an objection FAQ, a team meeting script and a readiness checklist, scaled by tier.
---

# Leader Cascade Kit

An all-staff email lands in inboxes. A manager who says the same thing in a team meeting
lands it with people. This skill builds the packet that lets a manager do that in a few
minutes, in their own voice, without reading any project paperwork.

Two design rules:

1. **Managers hear first.** A manager caught off guard by a question from staff turns into
   the strongest critic of the change. Send the manager email well ahead of the first
   all-staff IT Bulletin, leaving time for a manager to reply before the message goes wide.
2. **The ask is small and dated.** "Please pass this on" asks for nothing specific. A real
   ask names the action, who does it and the day it is due.

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

## Inputs

- The message core for the change (the six answers from `plain-language-translation`, or
  the short form written by hand). Every fact in the packet comes from it.
- The request: the change, the go-live date, the departments involved, the tier (below),
  and the date of the first IT Bulletin.
- From the config: `requester_role`, `approver_role`, `bulletin.name`, `time_zone`,
  `output_dir`. From the audiences file: the `leaders` segment (reading grade 10) and the
  vocabulary of each department that will receive a briefing.

## The parts

| Part | Purpose | Limit |
|---|---|---|
| Manager email | The cover note: what changes and when, who on the team is affected, the ask, what staff will receive and when, where to raise concerns | 200 words |
| The ask | A numbered block of two or three actions, each with a date | 3 actions |
| Talking points | Three to five lines meant to be spoken aloud, each followed by an "if someone asks" answer | 1 sentence each |
| Team blurb | A paste-ready message in the manager's voice, marked with copy lines | 120 words |
| FAQ | The questions staff will really put, in their own words, with honest answers | 60 words per answer |
| Team meeting script | A timed outline of a short meeting slot, built from the talking points | 5 minutes |
| Readiness checklist | Tick boxes so the pod can see who has passed the message on | 4 lines |

### Manager email

Lead with the change and its date in a single sentence. Then say why this team is affected and
what its people must do. Put the ask next, with dates. Close with what staff will receive
and when, and a deadline for the manager to raise concerns. Offer a real window for
feedback only if the plan can absorb it.

### The ask

```
YOUR ACTIONS
1. Present the talking points when your team next meets. Due: <date>.
2. Send the blurb on to people who missed that meeting. Due: <date>.
3. Report anyone who is unable to <take the action>. Due: <date>.
```

### Talking points

Write for the ear. One short sentence each, no acronyms, no project terms. Use the words
from the audiences file for the department in the room. Under each point add an
"if someone asks" line with the honest answer to the likeliest objection.

### Team blurb

```
=== Start of blurb ===
Team,
<blurb>
=== End of blurb ===
```

It carries the same facts as the bulletin and sounds like a colleague, not a notice.

### FAQ

Start from this standing list and drop what does not apply:

- Why are we doing this, and who decided?
- How much of my time will it take?
- What happens if I do nothing?
- Will it slow down my work with customers?
- We changed this recently. Why again?
- My device will not run it. What now?
- Who do I contact when it breaks?
- Does it touch my personal phone or data?
- Can this be undone if it goes badly?

Where the true answer is "this was decided and it is not optional", say that plainly.

### Team meeting script

Three timed beats: open with the change in one sentence (1 minute), read the talking
points and answer from the FAQ (3 minutes), close by restating the ask and its dates
(1 minute). Write it as lines the manager can say, not as notes.

### Readiness checklist

```
[ ] Presented the points to my team          Done on: ______
[ ] Sent the blurb to people who were away   Done on: ______
[ ] Reported people unable to take the step  How many: ____
[ ] Returned questions I could not answer    Done on: ______
```

## Tiers

| Tier | Use for | Contents |
|---|---|---|
| Light | Low-impact change, low expected resistance | Manager email and team blurb |
| Standard | A change that asks staff to act | Every part above |
| Heavy | Work-stopping change, a resistant department, or a change that slipped before | Every part, plus a live briefing for leaders, an offer of a guest slot (see `rollout-roadshow-deck`), and a named contact per department |

## Steps

1. Pick the tier and list the departments and their leaders by role.
2. Load the message core and confirm each date and fact. Mark anything unverified as
   `[UNCONFIRMED: ...]`.
3. Draft the parts in the order of the table. Keep every fact identical to the message core
   and the bulletin.
4. Run the readability check from this folder at the leaders grade:

   ```
   python shared/check_message.py <packet> --grade 10 --allow AM,PM,IT,<ORG>
   ```

   `<ORG>` is the organization's all-caps short name. The script finds the writing standard
   in the lookup order above. Fix failures and rerun until `status` is `pass`.
5. Self-check: managers hear before staff; every action has a due date; each point can be
   said aloud; the blurb stays within its word limit; the hard objections have answers.
6. Save the packet to `output_dir` from `comms-config`, named by the pattern
   `YYYY-MM-DD-leader-cascade-<topic>.md`.
7. Send it through the `deliverable-review` skill when installed; otherwise note in the
   hand-back that it is unreviewed.
8. Hand back to the requester role: the leader list, the send date, the tier, and any
   unconfirmed facts. The skill sends nothing.

## Rules

- Plain spoken language; no acronyms in the points or the blurb.
- Every request to a manager carries a date.
- The blurb is in a manager's voice.
- Facts match the message core exactly.
- The skill follows the writing standard in the lookup order above, including the
  banned-word list and the ban on em dashes.
