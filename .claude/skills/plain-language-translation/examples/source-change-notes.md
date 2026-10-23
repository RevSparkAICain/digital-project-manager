# DEMO-101: Expense claims, paper form to ACME Expenses (project notes)

Synthetic source material for the plain-language-translation example. ACME Co. is
fictional. Author: Alex Rivera (finance systems). Project lead: Jane Doe.

## Summary

Retire paper expense form EXP-1 and move expense claims to the travel and expense (T&E)
module of the enterprise resource planning (ERP) system, branded for users as
"ACME Expenses". Receipt capture uses optical character recognition (OCR) in the mobile
app. Users authenticate through single sign-on (SSO). The approval workflow routes each
claim through the cost center hierarchy.

## Schedule (all times local)

- App published to work phones and the intranet launcher: Monday, March 4, 2030.
- Users must complete first sign-in and confirm their reimbursement account by Friday,
  March 15, 2030.
- Data freeze window: Saturday, March 16, 2030, 10 PM to Sunday, March 17, 2030, 2 AM.
  Claim submission unavailable while open paper claims are loaded. Email and chat (SaaS)
  are not affected.
- Paper form EXP-1 decommissioned: Monday, March 18, 2030. Paper claims received after
  this date are returned to the sender.

## Technical detail

- SSO session persists on the device; no separate password for the app after first
  sign-in.
- First sign-in and account confirmation: pilot group of 40 users measured a median of
  2 minutes.
- New tile on the phone home screen and in the intranet launcher (green receipt icon).
- OCR reads merchant, date and amount from a receipt photo; the user confirms the fields
  before submitting.
- Approval routing: cost center hierarchy copied from the current paper sign-off list; no
  approver changes intended. Reimbursement schedule unchanged.
- OCR on the first receipt of the day adds latency; pilot reports "a few seconds", not
  measured.

## Support

- Service desk queue: Expenses. Knowledge article at help.acme.example/expenses.
  Escalation to finance systems.
- Office hours: proposed, owner not yet confirmed.

## Open items from the project record

- Shared shift kiosks in Operations: can staff without a work phone submit from a kiosk?
  Not decided.
- Does the freeze window delay claims already approved but not yet paid? Pending answer
  from the system supplier.
