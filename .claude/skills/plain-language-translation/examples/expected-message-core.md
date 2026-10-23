# Message core: a new way to claim expenses (DEMO-101)

Expected output of the plain-language-translation skill for
`source-change-notes.md`. Audiences in scope: General staff, Operations, Finance.
Benchmark reader: Warehouse Associate (`example_persona` in the example comms-config).

## Message core

1. **What is changing.** You will no longer fill in a paper form to get paid back for what
   you spend on work (the new app is called ACME Expenses).
2. **When.** The app arrives on your work phone on Monday, March 4, 2030. Sign in once by
   Friday, March 15, 2030. You cannot send a claim from Saturday, March 16, 2030, 10 PM to
   Sunday, March 17, 2030, 2 AM local time. Email and chat keep working during that window.
3. **Why it matters to you.** After your first sign-in, you claim by taking a photo of the
   receipt instead of filling in a form, and the app fills in the date and amount for you.
4. **What you must do.**
   1. Look for the green receipt icon on your work phone after Monday, March 4, 2030.
   2. Open it, sign in with your usual work password, and check that the account you get
      paid back into is right, by Friday, March 15, 2030. It takes about 2 minutes.
5. **What will look different.** A green receipt icon on your work phone and in the
   intranet launcher. Paper forms are no longer accepted from Monday, March 18, 2030, and
   any sent after that come back to you.
6. **Where to get help.** The Expenses article at help.acme.example/expenses, which also
   opens a request to the service desk.
7. **What is not changing.** Your password, the manager who approves your claims, and when
   you get paid back.

## Framing for audiences in scope

| Audience | Lead with | Length | Example |
|---|---|---|---|
| General staff | Sign in once by Friday, March 15, 2030, then claim with a photo | 150 to 250 words | Claiming back a work lunch |
| Operations | The paper step at the end of a shift that goes away, and the freeze window | 200 to 300 words | Claiming fuel bought on a delivery run |
| Finance | Paper claims stop on Monday, March 18, 2030, and approvals follow the same managers | 200 to 300 words | A claim that reaches the close after the freeze window |

## Group vocabulary map

| Group | Their term | Project term | Copy uses |
|---|---|---|---|
| General staff | your work phone | managed mobile device | your work phone |
| General staff | signing in | SSO authentication | signing in |
| General staff | getting paid back | reimbursement | getting paid back |
| Operations | shift handoff | (none) | not used, no effect confirmed |
| Finance | entry | transaction record | entry |
| Finance | the close | period-end processing | the close |

## Jargon list

| Technical term | Plain replacement |
|---|---|
| ERP travel and expense (T&E) module | the new app (ACME Expenses) |
| Paper expense form EXP-1 | the paper form you fill in today |
| Single sign-on (SSO) | signing in with your usual work password |
| OCR receipt capture | take a photo of the receipt and the app fills in the rest |
| Approval workflow, cost center hierarchy | the same manager approves your claims |
| Data freeze window | the time when you cannot send a claim |
| Decommission | paper forms are no longer accepted |
| SaaS | (dropped: the reader only needs "email and chat keep working") |

## Open questions blocking a clean draft

1. Can Operations staff without a work phone send a claim from the shared shift kiosks?
   The Operations version cannot say what kiosk users do until this is decided. Owner:
   Jane Doe.
2. Does the freeze window delay claims already approved but not yet paid? The Finance
   version holds until the system supplier answers. Owner: Alex Rivera.
3. How much time does reading the first receipt of the day add? The pilot says "a few
   seconds" but nobody measured it, so the copy states no number.
4. Will there be office hours, and who runs them? Not named as a help path until an owner
   is confirmed.
