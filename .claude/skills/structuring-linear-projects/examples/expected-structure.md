# Expected output: structure proposal

**Recommendation:** one project, no initiative, eight milestones, two-level issue tree,
epics and children both attached. The three integrations become epics under one milestone,
not milestones of their own, and the finance credential dependency is an issue with a
`blocks` relation.

## Decisions

| Level | Decision | Why |
|---|---|---|
| Initiative | None | One project in this area; an initiative earns its place at three or more |
| Project | `Field Service App Rollout`, target 2030-08-30, lead Alex Rivera | Has a closing day: legacy system off and hypercare exited |
| Milestones | 8 dated states, zero-padded | See below; each answers "has this happened yet?" |
| Tree depth | Two levels (epic plus children) | No middle tier has its own owner and finish date |
| Attachment | Epics and children both attached | Child completion moves the bar; one epic cannot swing it |
| Dependencies | `blocks` relations, recorded now | Billing needs credentials that another team produces |

## Milestones

| Milestone | Target date | True when |
|---|---|---|
| M01 Configuration Complete | 2030-03-29 | App configured to the approved design |
| M02 Integrations Live in Test | 2030-04-12 | Scheduling, inventory and billing pass end-to-end tests |
| M03 Pilot Live | 2030-04-22 | 20 pilot technicians working orders in the app |
| M04 Pilot Exit Approved | 2030-05-20 | Pilot exit criteria signed off by Sam Okafor |
| M05 Wave 1 Rolled Out | 2030-06-17 | 90 more technicians live |
| M06 Wave 2 Rolled Out | 2030-07-15 | Remaining 90 technicians live |
| M07 Legacy System Decommissioned | 2030-07-29 | Paper work-order process and old system retired |
| M08 Hypercare Exit | 2030-08-30 | A month of support completed and volume back to baseline |

## On the requested progress bars

- **Per phase:** met. Each phase is a milestone, and milestones are where Linear computes
  progress.
- **Per integration:** not available as asked. An epic gives a tree, never a progress bar.
  The three integrations are epics under `M02 Integrations Live in Test`, so M02's bar
  covers all three. If each integration truly needs its own number, it needs its own
  milestone; that would make 10 milestones and three of them would be activities, not
  states, so the recommendation is to keep one.

## Issue layout under M02 (sample)

```
M02 Integrations Live in Test
├ DEMO-110 Scheduling integration live in test      (epic, PLAT, Alex Rivera)
│  ├ DEMO-111 Scheduling API mapping approved
│  ├ DEMO-112 Scheduling sync built
│  └ DEMO-113 Scheduling end-to-end test passed
├ DEMO-114 Inventory integration live in test       (epic, PLAT, Priya Shah)
│  └ ... 3 children
└ DEMO-118 Billing integration live in test         (epic, PLAT, Alex Rivera)
   ├ DEMO-119 Billing API credentials received       (blocks DEMO-120; finance team)
   ├ DEMO-120 Billing sync built
   └ DEMO-121 Billing end-to-end test passed
All 12 issues attached to M02.
```

## Build notes

- Build order: project, milestones, epics, children. Canary: build all of M01, read it back
  field by field, then the rest.
- Integration issues land on team `PLAT`. Any created at Urgent or High will lose their
  `dueDate` to the SLA policy: after the batch, wait, re-read, and repair nulls with an
  isolated `dueDate` write.
- Verify against the checklist in `references/api-gotchas.md`, asserting attachment on
  `projectMilestone`, and report each check's result.
