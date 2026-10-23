# Message core: shared printers move to badge release

Synthetic example for the fictional ACME Co. This is the input the `it-bulletin` skill
writes from. `bulletin-printers.md` in this folder is the finished bulletin built from it.

- **Bulletin type:** planned change
- **Requester:** project lead (Jane Doe)
- **Approver:** IT manager
- **Sender:** IT Service Desk
- **Benchmark reader:** Warehouse Associate

## Message core

1. **What is changing.** From Monday, March 4, 2030, shared printers hold your pages until
   you tap your ACME badge on the printer.
2. **When.** Badge release starts Monday, March 4, 2030. Shared printers are off on Sunday,
   March 3, 2030, from 6 PM to 10 PM local time while the IT team sets them up. Badges can
   be linked from Monday, February 25, 2030.
3. **Why it matters to you.** Your pages stay in the printer until you are standing at it,
   so they no longer sit in the tray for anyone to pick up. You can also collect them at
   any shared printer, not only the one you sent them to.
4. **What you must do.**
   1. Link your badge by Friday, March 1, 2030: tap it on the reader on the front of any
      shared printer, then type your employee number. It takes about 1 minute.
   2. From Monday, March 4, 2030, print as you do today, then tap your badge on any shared
      printer to collect your pages.
5. **What will look different.** A small badge reader on the front of each shared printer.
   The printer screen says "Tap your badge" until you do. Pages wait for 24 hours, then
   they are deleted.
6. **Where to get help.** The printing help page at help.acme.example/printing, which also
   opens a request to the IT Service Desk.
7. **What is not changing.** How you print from your computer, the printer names, and the
   label printers on the warehouse floor.

## Audience impact tags

Segments come from `audiences.example.yaml`. Impact is high, medium, low, or none.

| Segment | Impact | Why |
|---|---|---|
| General staff | medium | One badge link before the date, then one tap each time they print |
| Operations | high | Shift teams print work orders at the start of each shift, so the tap lands at the busiest moment |
| Finance | medium | Prints during the close; same steps as general staff |
| Customer Support | low | Prints rarely |
| Customer-facing and sales staff | low | Prints rarely, mostly away from the office |
| Business leaders | low | Same steps as general staff; no team action beyond the badge link |
| IT and Engineering | medium | Expect badge-link requests at the IT Service Desk in the week of February 25, 2030 |
| Legal and Policy | low | No action; printed contracts no longer wait unattended in the tray |

The required action is the same for every segment, so one bulletin covers them all. No
department variant is needed.

## Vocabulary

| Group | Their term | Project term | Copy uses |
|---|---|---|---|
| General staff | your ACME badge | proximity card credential | your ACME badge |
| General staff | collect your pages | secure print release | collect your pages |
| Operations | work order | job record | work order (message core only; the bulletin needs no group term) |

## Facts checked

| Fact | Confirmed with | Date confirmed |
|---|---|---|
| Badge release starts Monday, March 4, 2030 | Print services team (Sam Okafor) | Monday, February 11, 2030 |
| Printers off Sunday, March 3, 2030, 6 PM to 10 PM local time | Print services team (Sam Okafor) | Monday, February 11, 2030 |
| Badge linking opens Monday, February 25, 2030 | Print services team (Sam Okafor) | Monday, February 11, 2030 |
| Pages are deleted after 24 hours | Project lead (Jane Doe) | Tuesday, February 12, 2030 |

## Open questions

1. Can visitor and contractor badges be linked? Not confirmed. The bulletin does not
   mention them until it is. Owner: Jane Doe.
2. Will the label printers on the warehouse floor move to badge release later? Out of
   scope for this change; the bulletin says only that they are not changing now.
