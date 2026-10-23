# transcript-to-tracked-actions

Turns a meeting transcript or rough notes into proposed changes in the tracker (ClickUp, Linear, Jira, Asana or Monday.com). It runs
`meeting-transcript-to-executive-notes` first, finds instructions spoken to the agent, resolves
the project (or projects) each subject belongs to, matches every action and status change
against items that already exist, and shows the result as one numbered reconciliation table.
Only the rows the person approves are written. When the work already has an item, the item is
updated instead of duplicated.

## Inputs

- A transcript, notes, or a captions file. With none, the skill asks for one and stops.
- Optional: the meeting title, attendees with roles, a glossary, default landing spots,
  the projects the meeting normally covers, a map from spoken names to tracker members.
- `meetings-config.yaml` in `pods/meetings/` if the project has one, otherwise
  `shared/meetings-config.example.yaml`. This skill reads `output_dir`, `notes.file_pattern`,
  `notes.doc_type`, `notes.type_label`, `agent_address` and `trackers`.

## Shared files

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## The nine steps

1. Notes, actions and decisions, saved as a Word file with `shared/md2docx.py`.
2. Spoken instructions to the agent, detected in the raw record.
3. Project resolution, for one project or several.
4. In-call status changes to work already tracked.
5. Matching against existing items.
6. The reconciliation table and the approval gate.
7. Real identifiers for every row that will write.
8. Apply, per tracker and per operation.
9. A decision-first report.

## The pm pod is optional

Applying changes needs the pm pod: `updating-trackers` and the agent for each
tracker in use. Where they are not installed, the skill stops after Step 6 and hands over the
approved table. Nothing is written to a tracker either way until the table is approved and the
person gives a final go-ahead.

## Worked example

`examples/reconciliation-table.md` is built from the ACME Co. weekly ops sync of March 12, 2030
(the example in `meeting-transcript-to-executive-notes`). It shows the list of current tracker
items, the spoken instructions above the table, and nine rows covering Create, Update, Close and
Skip, a possible match, a missing owner, and a row changed by a spoken instruction. All tracker
identifiers in it are fictional `DEMO-` items.
