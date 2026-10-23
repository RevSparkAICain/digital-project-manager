# Demo: where 400 ACME Co. support tickets landed

A synthetic service-desk export, the mapping that charts it, and the numbers the chart must
reproduce. Every ticket, count and caption is invented.

## Run it

From the skill folder:

```
python examples/demo/make_demo_data.py            # rewrites examples/demo/tickets.xlsx
python scripts/build_spec.py examples/demo/mapping.json spec.json
python scripts/sankey.py spec.json "Sankey - Ticket Flow - 2030-04-01.png"
python scripts/to_pptx.py "Sankey - Ticket Flow - 2030-04-01.png" slide.pptx --author "Jane Doe"
```

`build_spec.py` must print population 400 and the endpoint counts in `expected-counts.json`.
`expected-spec.json` is the full spec the mapping produces.

## The data

| Sheet | Rows | Read? |
|---|---:|---|
| Service Desk | 340 tickets plus 2 note rows with no `Ticket` | yes, keyed on `Ticket` |
| Field Requests | 80 (60 `In Scope` = Y, 15 = N, 5 blank) | yes, in-scope rows only |
| Escalations | 25 | no, see below |

Population: 340 + 60 = 400. By type: Access 120, Software 100, Network 50, Field requests 60,
Hardware 70.

## What the demo shows

**One population from several sheets, each with its own filters.** `Service Desk` supplies
every row that has a `Ticket` key, which also drops the two note rows. `Field Requests` supplies
only the rows whose `In Scope` value is neither `N` nor blank, which is 60 of 80.

**A column absent from one sheet.** `Resolution` exists on `Service Desk` and not on
`Field Requests`. The Duplicate rule still runs against field rows; the missing column reads as
blank, so it never matches there.

**Precedence that changes the answer.** All 20 duplicate tickets carry `Status` = `Closed`.
Only the `Resolution` column marks them as duplicates. The Duplicate rule runs first, so they
land in `Duplicate`. Move it below the Closed rule and `Resolved or closed` reads 220 instead
of 200, overstating finished work by 20. The test checks this.

**A sheet assigning the type.** Field rows have no `Type` column. The first type rule matches on
`{"sheet": "Field Requests"}` instead.

**A status rule that depends on the type stage.** `In Progress` means different work by type:
for hardware it is a device on the repair bench waiting on parts, for everything else it is
desk work. The `{"stage": "type", "in": ["hardware"]}` condition routes the same status value to two
buckets: 20 bench repairs and 55 desk items.

**Brackets that carry the argument.** Off the board 240 (60%), with the customer 40 (10%), open
desk work 100 (25%), open bench repairs 20 (5%). They sum to 400.

## Deliberate exclusion

`Escalations` is not read. Each of its 25 rows is a Service Desk ticket re-logged under its own
`DEMO-7xx` key, with the original in `Parent`. Reading it would count those 25 tickets twice
and inflate the population from 400 to 425. A chart that must show escalation
should give it a stage of its own (total, then type, then escalated or not, then status)
instead of combining the sheets.

## Palette

The demo is drawn with `restrained`, the default palette. Type nodes use `neutral`, which leaves
the status colors on the right to carry the eye. Seven endpoint buckets is near the top of
what the restrained range separates; render with `--palette extended` to compare.
