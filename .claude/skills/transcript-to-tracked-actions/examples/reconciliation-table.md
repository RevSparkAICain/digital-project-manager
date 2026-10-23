# Reconciliation table: Weekly Ops Sync, March 12, 2030

Built from the worked example in `meeting-transcript-to-executive-notes` (the transcript in
`examples/transcript-weekly-ops-sync.txt` and the notes in `examples/expected-notes.md`). Prepared
for Jane Doe. Nothing has been written to a tracker.

Projects resolved from the subject blocks (confirmed by the person before matching):

- Jira migration, PostgreSQL upgrade, Monitoring vendor renewal, Retention schedule: one project
  each, mapped from the four subjects.

Current tracker items found by the search:

- DEMO-101 Plan sixty-day parallel run (In progress), Jira migration
- DEMO-102 Intake form wording for new queues (To do), Jira migration
- DEMO-103 Vendor driver certification follow-up (To do), PostgreSQL upgrade
- DEMO-104 Monitoring vendor renewal pricing (In progress), Monitoring vendor renewal
- DEMO-105 Log retention schedule review (To do), Retention schedule
- DEMO-106 Vendor terms review (To do), Monitoring vendor renewal
- DEMO-107 Ping vendor about driver status (To do), PostgreSQL upgrade

Spoken instructions:

- Chief of Staff, "mark the renewal notice as high priority": said by Jane Doe near the end
  of the vendor discussion. Priority override covering row 7. Address is clear; confirmation not
  needed. Row 7 shows it.
- Checked and not treated as an instruction: Priya Shah's remark about a vendor's AI summarizer
  add-on. AI is the topic of that sentence, so nobody is addressing the agent. It stays an open
  question in the notes.

| # | Change | Kind | Project | Owner | Due | Existing item | Proposed operation | Lands in | Spoken instruction |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Send agents the intake freeze notice | action | Jira migration | Jordan Lee | March 26, 2030 | none | Create | Linear: team OPS, project Jira migration | |
| 2 | Update the intake form wording for the new queue names | action | Jira migration | Jordan Lee | TBD | DEMO-102 Intake form wording for new queues (To do) | Update | DEMO-102 | |
| 3 | Archive the old system's ticket export before it goes read-only | action | Jira migration | Priya Shah | April 1, 2030 | none | Create | Linear: team OPS, project Jira migration | |
| 4 | Drop the sixty-day parallel run; the group decided on no parallel run | status change | Jira migration | Jordan Lee | n/a | DEMO-101 Plan sixty-day parallel run (In progress) | Close | DEMO-101 | |
| 5 | Ask the vendor for a firm driver certification date | action | PostgreSQL upgrade | Priya Shah | March 19, 2030 | DEMO-103 Vendor driver certification follow-up (To do) | Update | DEMO-103 | |
| 6 | Vendor replied to Priya's message: certification next quarter, no firm date | status change | PostgreSQL upgrade | Priya Shah | n/a | DEMO-107 Ping vendor about driver status (To do) | Close | DEMO-107 | |
| 7 | Send the vendor written notice that the renewal is under negotiation (priority High) | action | Monitoring vendor renewal | TBD | March 29, 2030 | none | Create | ClickUp: list ACME Projects / Intake (the project has no ClickUp list, so the config default applies) | Priority override from Jane Doe |
| 8 | Negotiate the renewal price with the vendor | action | Monitoring vendor renewal | Alex Rivera | TBD | DEMO-104 Monitoring vendor renewal pricing (In progress) | Update | DEMO-104 | |
| 9 | Compare the retention schedule against the new vendor terms | action | Retention schedule | likely Sam Okafor | March 22, 2030 | possible: DEMO-105, DEMO-106 | Skip | none until the match is confirmed | |

Flags for the reply:

- Row 7 has no owner (`TBD`); the group left it open on purpose.
- Rows 2 and 8 have no due date (`TBD`); none was spoken.
- Row 9 is held as `Skip` until you pick DEMO-105, DEMO-106, or neither. Choosing one turns it into
  an Update of that item; choosing neither turns it into a Create.
- Row 4 closes DEMO-101 on the decision stated in the call; say so if you would rather leave it open.
