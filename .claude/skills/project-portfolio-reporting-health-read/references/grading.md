# Grading

The grade measures reporting reliability: whether status reporting is current, new,
consistent with the reported color, and correctly placed. It never measures delivery. The
deck's grade slide states both halves from `grade_statement` in the config.

## Project points and letters

Points per outcome come from `grading.points`:

| Outcome | Key | Example points |
|---|---|---|
| Check 1 aging | `aging` | 1 |
| Check 1 stale | `stale` | 2 |
| Check 1 absent | `absent` | 2 |
| Check 2 repeated | `repeated` | 2 |
| Check 2 placeholder | `placeholder` | 2 |
| Check 3 misaligned | `misaligned` | 2 |
| Check 4 band minor | `minor` | 1 |
| Check 4 band conflicting | `conflicting` | 2 |

Check 4 scores its band once, however many items it holds. Not applicable, not assessable
and not judged score nothing.

The letter comes from `grading.project_bands`, the largest points value per letter: in the
example A at 0, B up to 1, C up to 3, D up to 5, and F above 5. A project whose list was set
up and never used (the trip wire in `checks.md`) is F whatever its points. A project with a
not-judged color, or a populated status field with no judgment, is marked provisional.

## Portfolio and lead letters

Over the N in-scope projects:

- `currency_fail`: share whose check 1 fails (stale, absent or the trip wire);
- `newness_fail`: share repeated or placeholder;
- `color_fail`: share misaligned;
- `color_or_records_issue`: in-scope projects with a check 3 fail or a counted check 4 item,
  plus lists outside the active folder with an item, divided by N plus those outside lists.

Letter, first match, with the lines from `grading.portfolio_lines` (example values):

| Letter | Fires when |
|---|---|
| F | `currency_fail` above `f_currency_fail_over` (0.5) |
| D | `currency_fail` above `d_currency_fail_over` (0.3), or `color_fail` above `d_color_fail_over` (0.5) |
| C | `currency_fail` above `c_currency_fail_over` (0.1), or `newness_fail` above `c_newness_fail_over` (0.2), or `color_or_records_issue` above `c_color_or_records_over` (0.2) |
| B | Any in-scope project is not A, or any outside list has an item |
| A | Otherwise |

Each line that fired becomes a reason in plain words with counts and the line, for example
"2 of 10 projects have no current status, above the 10 percent line". A measure is reported
once, at the highest line it crosses, and reasons are ordered F, then D, then C. The first
reason is the headline on the grade slide. `reason_keys` records which lines fired, so the
next read can tell a changed reason from a changed count.

A lead's letter uses the same rule over that lead's in-scope projects and that lead's lists
outside the active folder. A lead with neither gets no letter (null) and still gets a
cleanup page. A lead is provisional when any of their projects is.

## Provisional marking

Any judgment request still unanswered after the second pass (a color, a populated status
field, or a hold) leaves the item not judged, marks the project and the portfolio
provisional, lists it on the method page, and makes `grade_portfolio.py` exit 3. Not judged
is never a pass: a guessed "aligned" would turn an unread entry into a clean record, which is
the one mistake the read exists to catch.

## Outside lists

Placement items in the completed and not-started folders count toward the lead and portfolio
letters through `color_or_records_issue` and the B rule, appear in the fix list and the
corrections table, and never create a scorecard row.

## Same letter, different reasons

With `--prior`, `reasons_changed` is true when the prior letter equals this letter and the set
of fired lines differs. The grade slide then says the letter is unchanged and the reasons
changed, so a steady letter never hides a shift underneath it. A project on hold this read
is never listed as closed since the prior read, even when the prior read carried a fix item
for it.

## Worked example (the ACME fixture)

| Project | Lead | Outcomes | Points | Letter |
|---|---|---|---|---|
| Intranet page refresh | Jane Doe | absent, trip wire | 2 | F |
| New hire welcome pack refresh | Priya Shah | misaligned 2, records minor 1 (stale status field) | 3 | C |
| Payroll report refresh | Jane Doe | placeholder 2, records minor 1 (owner mismatch) | 3 | C |
| Furniture inventory reconciliation | Alex Rivera | repeated 2 | 2 | C |
| Meeting room booking rollout | Alex Rivera | misaligned by rule 2 | 2 | C |
| Training library inventory | Jane Doe | records conflicting 2 | 2 | C |
| Visitor parking redesign | Sam Okafor | stale 2 (the unconfirmed roadmap item is not counted) | 2 | C |
| Annual handbook review | Priya Shah | aging 1, color not judged | 1 | B, provisional |
| Expense report form update | Jordan Lee | none | 0 | A |
| Quarterly town hall program | Jordan Lee | none | 0 | A |

Shared drive clean-up is a qualified hold and has no grade.

Portfolio, N = 10: `currency_fail` 2 of 10 = 0.2, above 0.1, so C. `color_fail` 0.2 is under
the D line. `newness_fail` 0.2 is not above 0.2. `color_or_records_issue` is 4 in-scope
projects (welcome pack, payroll, training library, meeting room) plus 2 outside lists
(office relocation, new-starter handbook) out of 12 = 0.5, above 0.2. Grade C, provisional,
with two reasons.

Leads:

- Jordan Lee: two A projects, nothing outside. A.
- Alex Rivera: 2 projects plus 1 outside list. `color_fail` 0.5 is not above 0.5;
  `newness_fail` 0.5 is above 0.2. C.
- Priya Shah: 2 projects. `color_or_records_issue` 0.5 is above 0.2. C, provisional (the
  handbook review's color is not judged).
- Jane Doe: 3 projects. `currency_fail` 1 of 3 = 0.33, above 0.3. D.
- Sam Okafor: 1 project plus 1 outside list. `currency_fail` 1 of 1, above 0.5. F.
