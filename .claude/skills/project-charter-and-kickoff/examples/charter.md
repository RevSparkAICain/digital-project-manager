# Project charter: Expense system replacement

Prepared by Jane Doe, project lead. Sponsor: Alex Rivera, Finance Director. Source: business case dated March 12, 2030.

## Purpose

Expense reports are entered twice, once in the current tool and once in the ledger, and the finance team spends about two days each month end fixing the mismatches. This project moves expense reporting to a hosted expense service that posts straight to the ledger and retires the server that is past its support date.

The first year costs $60,000 against a saving of $9,000 a year in server support that starts the year after go-live. The business case recommends the hosted service over keeping the current tool or building one in house.

## Success criteria

- Month-end expense reconciliation drops from about 2 days to under 4 hours within 60 days of go-live.
- Staff are repaid within 10 days of submitting a report, down from about 3 weeks.
- 100% of expense reports are entered once, with no second entry in the ledger.
- The old expense server is switched off within 30 days of the end of hypercare.

## Scope

In scope:

- Configure the hosted expense service and connect it to the ledger.
- Move open reports and the last seven years of receipts.
- Pilot with the finance team, then roll out to all staff.
- Retire the old tool and its server.

Out of scope:

- Changes to the expense policy.
- Corporate card feeds.
- Any new reports beyond those the old tool produced.

Assumption: the vendor quote holds for three years. The price after year three is TBD and Priya Shah is asking the vendor.

## Milestones

| Milestone | Date |
|---|---|
| Business case approved | April 2, 2030 |
| Charter approved | April 16, 2030 |
| Pilot with the finance team | June 4, 2030 |
| Go-live | September 3, 2030 |
| Hypercare ends | September 17, 2030 |
| Close-out | October 1, 2030 |

## RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Approve business case and charter | Jane Doe | Alex Rivera | Sam Okafor | Priya Shah, Jordan Lee |
| Configure and connect the hosted service | Priya Shah | Jane Doe | Alex Rivera | Jordan Lee |
| Confirm receipt retention with the vendor | Sam Okafor | Jane Doe | Priya Shah | Alex Rivera |
| Run the pilot and the rollout | Jane Doe | Alex Rivera | Priya Shah | Jordan Lee, Sam Okafor |
| Support staff during hypercare | Jordan Lee | Priya Shah | Jane Doe | Alex Rivera |

## Budget

The first-year budget is $60,000: $36,000 to implement once and $24,000 for the first year of subscription. People time is carried by existing teams and is not charged to this budget.

## Seed RAID

| Tag | Entry | Owner |
|---|---|---|
| R1 | The receipt retention setting on the hosted service is unconfirmed (receipts are kept seven years). Likelihood 3, impact 4, score 12. | Sam Okafor |
| A1 | Ask the vendor for the subscription price after year three. | Priya Shah |
| A2 | Name an owner for each milestone before the charter is approved. | Jane Doe |

Tracker items for these entries, when created, are DEMO-201 (R1), DEMO-202 (A1) and DEMO-203 (A2).

## Approval

This charter goes to the sponsor review, and work starts only after that sign-off.

## Kickoff agenda

1. Scope, in and out (10 minutes, Jane Doe).
2. Roles from the RACI table (10 minutes, Jane Doe).
3. Plan and milestones from April 16, 2030 to October 1, 2030 (10 minutes, Priya Shah).
4. Status: the weekly status item DEMO-214 in the tracker, read by the sponsor (5 minutes, Jane Doe).
5. Definition of finished: go-live, hypercare closed and the old server retired (10 minutes, Alex Rivera).
6. Actions and owners (5 minutes, Jane Doe).
