# project-charter-and-kickoff

Opens a project. It produces a business case (through `business-case-from-transcript`), a
short charter with nine fixed headings, a project set up in the connected tracker, and an
agenda for the first all-hands session. No script; the agent follows the steps with the
requester.

## The four steps

1. **Business case** from the scoping transcript, or a note in the charter that it is missing.
2. **Charter** with the headings Purpose, Success criteria, Scope, Milestones, RACI, Budget,
   Seed RAID, Approval and Kickoff agenda.
3. **Tracker set-up** through the active profile in `trackers.yaml`, after the user approves
   the planned-changes table.
4. **Kickoff** agenda, follow-up notes and assigned actions.

## Inputs
- A scoping transcript and supporting files (optional).
- `pm-config.yaml` keys `approval_gate`, `tracker` and `output_dir`.

## Outputs
- A dated Markdown charter in `output_dir`.
- Tracker items with IDs and links.
- The kickoff agenda and actions.

## Prerequisites
- A connected tracker, or `connecting-a-tracker` to connect one.
- Optional helpers, if installed: superpowers `brainstorming` and `writing-plans`, and a docx skill.

## Examples
- `examples/charter.md`: the charter for the expense system replacement at ACME Co.

## Shared files
Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.
