# meeting-transcript-to-executive-notes

Turns a raw meeting transcript, rough notes, or both into executive notes grouped by subject.
Each subject gets one block (summary, discussion, decisions, actions, open questions, risks and
blockers), and four registers at the end collect every action, decision, open question and risk
in one place. Transcription errors on product names are corrected, small talk is dropped, and
every action carries one owner (or `likely <name>`, or `TBD`) and a due date only when one was
spoken. The notes are saved as a branded `.docx` by the bundled `scripts/md2docx.py`, go
through `deliverable-review`, and are then exported to a matching `.pdf` through Word.

## Inputs

- A transcript, notes, or both.
- Optional: a participant list with roles, a glossary, an agenda.
- `meetings-config.yaml` in `pods/meetings/` if the project has one, otherwise
  `shared/meetings-config.example.yaml`. It supplies `output_dir`, `notes.file_pattern`,
  `notes.doc_type` and `notes.type_label`.
- The brand file for the `.docx` (`brand/brand.json` if present, otherwise `shared/brand.json`).
- The writing standard (the installed house-style skill if present, otherwise
  `shared/writing-standard.md`).

## Shared files

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Worked example

`examples/transcript-weekly-ops-sync.txt` is a fictional ACME Co. weekly ops sync held on
March 12, 2030, written with anonymous `Speaker N:` labels. `examples/expected-notes.md` is the
output you get by following `SKILL.md` on it. It shows:

- the opening small talk removed;
- two transcription errors on product names fixed (Jira and PostgreSQL);
- a subject left and revisited later, merged into one block;
- a change of position recorded as a decision;
- an action with no owner (`Owner: TBD`) and an owner identified only from a role cue
  (`likely Sam Okafor`);
- due dates that were spoken, and one action left at `Due: TBD`;
- a percentage carried as the speaker's own number.

The transcript also holds an instruction spoken to the agent, which does not belong in the
notes. The `transcript-to-tracked-actions` skill reads that line.

## Render the example

From this folder, run:

```
python scripts/md2docx.py examples/expected-notes.md \
  --out "Notes - Weekly Ops Sync - 12Mar30.docx" \
  --title "Weekly Ops Sync" \
  --topic "Ticket migration, database upgrade, vendor renewal, retention schedule" \
  --date "March 12, 2030" --operator "Jane Doe" \
  --doc-type "Executive Meeting Notes" --type-label "Executive Notes"
```

With the default `notes.file_pattern` (`Notes - {meeting} - {DDMMMYY}`), the file name for this
meeting is `Notes - Weekly Ops Sync - 12Mar30.docx`. A second meeting on the same date would
add its start time, for example `Notes - Weekly Ops Sync - 12Mar30 (0930).docx`.

`scripts/md2docx.py` needs python-docx. It refuses a blank or placeholder `--operator`, and it
refuses a `--doc-type` equal to `--type-label`.
