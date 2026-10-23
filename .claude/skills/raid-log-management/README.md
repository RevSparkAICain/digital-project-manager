# raid-log-management

Keeps one register per project with four kinds of entry: Risks, Actions, Issues, Decisions.
It scores risks, gives every row one owner and a dated next step, reviews the register on the
configured rhythm, escalates to the configured role, and hands its top rows to
`project-status-reporting`. No script; the agent follows the steps in `SKILL.md`.

Some teams expand the acronym differently. This pod uses the four types above.

## What it does

- Defines the four types and one table format with fixed columns.
- Scores risks as likelihood times impact on 1 to 5 scales, with published bands and anchors.
- Never reuses a tag. A changed decision is a new entry that reverses the old one.
- Saves to Markdown (default), a workbook, or the project tracker after the user approves the
  table of planned changes.

## Inputs
- New or changed entries, often from meeting notes or status inputs.
- `pm-config.yaml` keys `raid.store`, `raid.review_cadence`, `escalation_role`, `tracker` and
  `output_dir`.

## Outputs
- The saved log (file path or tracker link).
- The top rows by score, the rows needing escalation or a decision, and any incomplete rows.

## Prerequisites
- For the tracker store: a profile in `trackers.yaml`, or `connecting-a-tracker` to create one.
- Optional, if installed: an xlsx skill for the workbook store.

## Examples
- `examples/raid-log.md`: the log for the expense system replacement at ACME Co.

## Shared files
Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.
