# Example input: notes and tracker data

Operator: Priya Shah, ACME Co. Reporting week ending 2030-04-12.

## Meeting notes: Field Service App Rollout, pilot readiness check, 2030-04-10

Attendees: Priya Shah (PM), Alex Rivera (platform lead), Sam Okafor (field operations).

- Alex confirmed all 40 pilot devices were enrolled on 4/8.
- Sam ran the pilot group training session on 4/9; 18 of 20 technicians attended.
  The two who missed it are booked for 4/15.
- The offline sync defect (DEMO-131) is still open. Alex expects a fix by 4/17. If it
  slips past 4/19, the 4/22 pilot start moves.
- Decision: pilot start stays 2030-04-22 for now; revisit on 4/17.
- Notes stored at: <notes link>

## Tracker data (Linear, read 2030-04-12)

| Issue | Title | State | Owner | Due |
|---|---|---|---|---|
| DEMO-128 | Pilot devices enrolled | Done (4/8) | Alex Rivera | 2030-04-08 |
| DEMO-129 | Pilot group trained | In Progress | Sam Okafor | 2030-04-15 |
| DEMO-131 | Offline sync defect fixed | In Progress | Alex Rivera | 2030-04-17 |
| DEMO-133 | Pilot started | Todo | Priya Shah | 2030-04-22 |

Milestone `M03 Pilot Live`: 12 issues attached, 6 Done, 4 In Progress, 2 Todo
(API progress 58.33).

## Portfolio data for the rollup

| Project | Last RAG | Milestone progress | Progress a week earlier | Next milestone | Top open item |
|---|---|---|---|---|---|
| Field Service App Rollout | Green | 58% (`M03 Pilot Live`) | 56% | Pilot Live, 2030-04-22 | DEMO-131 offline sync defect, fix due 4/17 |
| Warehouse Scanner Refresh | Yellow | 30% (`M02 Vendor Selected`) | 30% | Vendor Selected, 2030-04-30 | Second bid not received; the bidder asked for a 2-week extension; decision needed by 2030-04-17 |
| Shared Drive Cleanup | Green | 90% (`M05 Legacy Shares Retired`) | 75% | Legacy Shares Retired, 2030-04-19 | None |
