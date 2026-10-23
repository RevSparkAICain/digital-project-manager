# Expected output: update report

Three items updated in Linear, one mirrored in ClickUp. The bulk close of the
"Field Service Planning" list is **not done**: it closes 12 tasks, so it waits for your
explicit go-ahead.

## Applied

| Item | Field | Old → New | Comment added |
|---|---|---|---|
| [DEMO-102](https://linear.example.com/acme/issue/DEMO-102) | Status | In Review → Done | "Exit criterion met: sign-off comment from Alex Rivera, 2030-03-08." |
| [DEMO-104](https://linear.example.com/acme/issue/DEMO-104) | Due date | 2030-03-15 → 2030-03-22 | "Slipped 7 days: vendor test environment delivered late. Mirror: ClickUp task abc123." |
| [DEMO-105](https://linear.example.com/acme/issue/DEMO-105) | Due date | 2030-03-22 → 2030-03-29 | "Slipped 7 days, follows DEMO-104 (vendor test environment delivered late)." |
| [Work-order form configured](https://clickup.example.com/t/abc123) | Due date | 2030-03-15 → 2030-03-22 | "Mirrors DEMO-104 (system of record: Linear)." |

Read back: all four items were read again after writing, and every field matches the value
sent.

## Left for a person to decide

- **Bulk close of "Field Service Planning" (12 open tasks).** Before I close them: 3 of the
  12 were updated in the last 14 days, and 1 is assigned to Jordan Lee, due 2030-03-18.
  Confirm closing all 12, or name the ones to keep.
- **DEMO-104 cycle.** The new date (2030-03-22) falls in Cycle 7 (2030-03-18 to
  2030-03-31), but the issue sits in Cycle 6. I left the cycle unchanged; say if it should
  move. DEMO-105's new date (2030-03-29) still falls inside its Cycle 7, so it needs no
  change.

URLs above are illustrative. In a real run, use the URL each tool returns, verbatim.
