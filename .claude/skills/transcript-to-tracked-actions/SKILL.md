---
name: transcript-to-tracked-actions
description: Convert a call transcript or rough meeting notes into proposed changes in the tracker (ClickUp, Linear, Jira, Asana or Monday.com), show them as a numbered reconciliation table, and apply only the rows the person approves, updating existing items instead of creating duplicates. Use whenever a transcript or notes arrive and the person wants the follow-ups captured or reconciled as tasks or issues, for example "put these actions in ClickUp", "turn this call into tickets", "log the follow-ups", or "update the tickets from this meeting". Works for one project or several in the same call. With no record supplied, ask for one and stop.
---

# Transcript to tracked actions

This skill turns one meeting record into proposed tracker changes and applies the ones a person
approves. It chains three parts:

1. `meeting-transcript-to-executive-notes` (this pod), which produces subject blocks and the
   registers of actions, decisions, open questions and risks.
2. The logic in this file: spoken-instruction detection, project resolution, status-change
   extraction, matching against existing items, and the reconciliation table.
3. The pm pod: the `updating-trackers` standard and the tracker agents
   (`clickup-agent`, `linear-agent`, `jira-agent`, `asana-agent`, `monday-agent`), which perform the writes and return identifiers and links.

Three properties hold throughout. Every proposed change belongs to a project. The trackers stay
untouched until the person approves the table and then gives a final go-ahead. When an item for
the work already exists, that item changes; a weekly meeting must not add a fresh copy of the
same task every week.

Speakers who state owners and real dates aloud, label decisions, announce topic changes, spell
out acronyms and make one request per sentence make extraction cleaner. Use those cues when they
are there, and do not depend on them.

## Inputs

- Required: a meeting record, as pasted text, a file path, or a captions export (plain text or
  Word). With no record, ask for one and stop. Never fill the table with invented work.
- Optional, asked for only when the answer unblocks a decision: the meeting title or the record's
  file name (it often names the project); attendees and roles (the authority on owners); a
  glossary of systems, projects and abbreviations; default landing spots for new items; the
  projects, lists or teams the meeting normally covers; a mapping from spoken names to tracker
  member names.

## Where each file comes from

For every file this skill reads, use this order:

1. the project's own file, if present:
   - `pods/meetings/meetings-config.yaml`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
   - `brand/brand.json`
2. otherwise, this folder's shared/ copy:
   - `shared/meetings-config.example.yaml`
   - `shared/writing-standard.md`
   - `shared/brand.json`

Keys read from the config: `output_dir`, `notes.file_pattern`, `notes.doc_type`,
`notes.type_label`, `agent_address`, and the `trackers` defaults.

## Step 1: Write the notes and save them

Run `meeting-transcript-to-executive-notes` on the record. Use its `# All actions` register (one
line per action with owner, due date and subject), its `# All decisions` register, and the
subject blocks, which often describe changes to work that already exists.

Save the notes as a Word file with this folder's `shared/md2docx.py`:

```
python shared/md2docx.py <notes.md> --out "<output_dir>/<file name>.docx" \
  --title "<meeting name>" --topic "<what the meeting covered>" --date "<Month D, YYYY>" \
  --operator "<the name the orchestrator supplies>" \
  --doc-type "<notes.doc_type>" --type-label "<notes.type_label>" \
  [--footer "<left footer text>"] [--brand <brand.json>]
```

- `output_dir` comes from the config, and the file name comes from `notes.file_pattern`.
- Name clashes, including when the ` (HHMM)` suffix applies, follow the "Saving the notes"
  section of `meeting-transcript-to-executive-notes`: list the folder before each write, and
  never replace the file of a different meeting.
- The saved file is a deliverable. It goes through `deliverable-review` before anyone receives
  it. Keep secrets, credentials and personal data out of it. Saving is not sending, and this
  skill sends nothing.

## Step 2: Find instructions spoken to the agent

During a call a speaker may tell the agent how work should be recorded, owned, bounded or
placed. That line is an instruction to the agent. It is neither a discussion point nor an
action item.

Scan the raw record, because the notes skill strips these asides out. A line qualifies only
when both tests pass:

- It addresses the agent by one of the names listed under `agent_address`, used as a form of
  address (usually the first words of the sentence).
- It then asks the agent to do something about the notes, tasks, ownership, scope, dates,
  priority, project placement or the state of a tracked item.

A generic aside such as "for the record" is a weak address cue. It lowers confidence and never
qualifies a line alone.

One configured name is the short word "AI". Because AI is also a common topic of conversation,
a sentence where AI is the topic, as its subject or its object (a policy about it, a vendor
selling it, an assessment of it), does not address the agent and is never an instruction. Only
a direct address followed by a capture, assignment, scope or routing request counts.

The short name "Chief" works the same way. It counts only as a direct address, usually the
first word of the sentence ("Chief, make that high priority"). Inside a job title or about a
person ("the chief engineer", "our Chief Financial Officer", "ask the chief") it is never an
address and never an instruction.

When the address is uncertain, do not apply the line. Carry it as a candidate instruction for the
person to confirm or reject in the table.

Classify each instruction by its effect, noting the speaker and the rough position in the call:

- Scope filter: suppresses action creation for a stretch of discussion, or forces an item to
  become an action.
- Assignment override: sets the owner on the rows it covers.
- Due, priority or project override: sets a default date, priority or project on those rows.
- Status instruction: asks for a tracked item to be updated or closed.

An instruction supplies a default or a filter over the rows it covers. It never skips review.
Apply it while building the table in Step 6, mark every row it changed, and let the person
reverse it. A blanket instruction (one owner for everything, one date for everything, nothing
here is an action) has high impact: it needs explicit confirmation before it stands, and every
row it changed stays visible. One misheard sentence must not reassign or erase a whole meeting.

## Step 3: Resolve the project or projects

Resolve projects before any matching or creating, because the project bounds the duplicate
search and decides where new items land. Signals, strongest first:

1. The meeting title or the record's file name. A clear match to a project name is strong.
2. The subject blocks from the notes, compared through the tracker agents against folders,
   lists, projects and initiatives. A subject that maps cleanly to one existing project is
   strong.
3. Context the person supplied.

Single-project meeting: when the signals point clearly at one existing project, say which one and
continue. When they are weak or split, show the best guess with the alternatives and wait. Never
assume.

Multi-project meeting (a portfolio review, a staff meeting): do not collapse everything into one
project. Map each subject to its own project, show the subject-to-project map, and ask for
confirmation or correction.

Each candidate row takes the project of the subject it came from. That project bounds its search
in Step 5 and sets its default landing spot in Step 6. It also sets the row's tracker: the
project's entry in `project_trackers` in `pods/pm/pm-config.yaml`, otherwise `tracker`. One
meeting can therefore land rows in several trackers, and every row names its tracker. A subject with no confident project
becomes a flagged row, and the skill never guesses one.

## Step 4: Pull out in-call status changes

Read the notes and the record for statements that alter work already tracked. These are updates,
not new tasks:

- an item finished or closed;
- a change of status, scope, due date or owner, or a new blocker;
- a decision that moves an item to a different priority, owner, date or state.

Turn each into a candidate Update or Close that names the exact field change, tagged with the
project of its subject. Base it strictly on what was said. Never infer a closure or a new date
from hints; an ambiguous statement becomes a flagged row with no operation.

## Step 5: Match against existing items

For every candidate, new action or status change, search for an existing item before
considering a Create. Search inside the row's project first and widen only if that finds
nothing. Search on the subject name, the main nouns of the action, the owner, and the project's
list or board. Three outcomes:

- Match: one existing item clearly corresponds. Record its identifier, title, current status and
  link. The default operation becomes Update or Close.
- Possible match: one or more related items, none certain. List them as candidates for the
  person to accept or reject. Never edit on a guess, because changing the wrong item does more
  harm than adding one extra item.
- No match: nothing corresponds. The default operation is Create, except for a status change.
  With nothing tracked to change, a status change becomes `Skip` with the reason
  `nothing tracked` and stays in the notes. It is not held for a question, even in a
  pre-approved run, and the person can still turn it into a Create in the table.

Lean toward updating. Before proposing any Create, look for a broader parent item of which the
action is one step. If one exists, propose changing it (its state, a checklist entry or a
comment) instead of opening another item. Propose Create only when nothing existing reasonably
covers the work. Every match is a proposal, and the person confirms each one in the table.

## Step 6: Build the reconciliation table and get approval

Build one numbered table that holds both new actions and status changes. Write nothing yet.
The columns, in this order, are `#`, `Change`, `Kind`, `Project`, `Owner`, `Due`,
`Existing item`, `Proposed operation`, `Lands in` and `Spoken instruction`.

- `Kind` is `action` or `status change`.
- `Project` is the Step 3 project for the row's subject. Rows from a multi-project call carry
  different values. Flag any project still unconfirmed.
- `Existing item` is `none`, one item written `DEMO-<n> <title> (<status>)`, or
  `possible: DEMO-<n>, DEMO-<m>`. Every Update or Close names exactly the item that will change,
  so a wrong match can be vetoed.
- `Proposed operation` is `Create`, `Update`, `Close` or `Skip`. It starts from the match result
  and can be changed per row.
- `Lands in` is the concrete destination of a Create: the list, team and project, project or
  board in the row's tracker (Step 3). It defaults to the project's entry in
  `project_containers` in `pods/pm/pm-config.yaml`, then to a container named after the row's
  project, then to the `trackers` defaults in the config (ClickUp and Linear), then to that
  tracker profile's `default_container` in `pods/pm/trackers.yaml`. A Create with no
  destination means ask before creating. When `mirror_tracker` is set, every row that writes
  also shows `+ <mirror tracker>` (Step 8).
- `Spoken instruction` names the Step 2 instruction that changed the row's owner, date, project,
  priority or existence, and is empty otherwise. A "nothing here is an action" instruction turns
  its rows into `Skip` with the instruction named.
- An unknown owner or date stays `TBD`. Never fill one in, and flag every `TBD`.

Above the table, print the current tracker items found in Step 5 as a bullet list, then a
`Spoken instructions` bullet list showing each detected instruction, who gave it, and whether it
still needs confirmation, including candidates whose address was uncertain. Blanket instructions
must be confirmed before they take effect. No `|` character appears above the table.

The approval gate has three moves:

1. Ask for routing and corrections for every row in a single reply: the operation per row, fixes
   to wrong projects, matches to reject, instructions to ignore.
2. Restate the final table with those changes applied.
3. Get an explicit go-ahead before any write. Handle this as a bulk change as defined by
   `updating-trackers`. Nothing reaches a tracker before this approval.

When the person's own request pre-approves the run, as the project's approval rules define it,
that stands in for moves 1 to 3 for every Create row and every Update on a Match (Step 5). Hold
every other row in the table for the person to confirm at the end, without stopping to ask.
The approval is the person's own words. Quote them word for word in every dispatch to
`project-manager` and to each tracker agent, and never cite a config or instruction file as
the approval.

If the pm pod's standard or its tracker agents are not installed, stop here and hand over the
approved table as the output.

## Step 7: Look up real identifiers

For each row that will write, look up the identifiers first and never guess them:

- Create: the destination container in the row's tracker (list, team and project, project or
  board), plus the member identifier for the owner.
- Update or Close: the confirmed item's identifier, plus a member identifier when the owner
  changes.

When a spoken owner name maps to no tracker member, leave the assignment alone and report it.
Never assign somebody else in its place.

## Step 8: Apply the approved rows

Dispatch per tracker and per operation, following `updating-trackers`. Send each
tracker's batch to its agent as an independent dispatch, all in parallel. Each agent returns
the identifier, link and before and after values for every item it touched.

- Create: set the title, description, assignee, due date and priority at the destination. Record
  the source subject, the project and the meeting date (stated as created from those notes) in
  the description or a comment. When the destination is not named after the row's project (a
  `project_containers` entry, a default container or the mirror), start the title with
  `<project>: `.
- Update: read the item's current state first. Change only the fields the meeting changed (state,
  date, owner, priority, scope), and add a comment that says what changed and which meeting date
  it came from. Leave every other field as it was.
- Close: move the item to its done state only when the record plainly says the work is finished,
  or a decision in the call ends it, and comment with the closing decision and its date.
- Mirror: when `mirror_tracker` is set in `pods/pm/pm-config.yaml`, each row written to another
  tracker is written again to the mirror, in `mirror_container`, by the mirror's agent, once
  the row's own write has returned its identifier.
  - A Create makes the same item in the same state, with the line
    `Also tracked in: <tracker> <identifier and link>` in its description.
  - An Update or Close changes the counterpart that line points to, and creates the
    counterpart when there is none.
  - A row whose tracker is the mirror is written once.
  - The mirror write is part of the approved row and needs no approval of its own. The row's
    own tracker stays the system of record.

## Step 9: Report

Lead with the result. In this order:

1. One summary line: meeting name and date, the project or projects, and the counts of created,
   updated, closed and skipped rows.
2. Created: project, identifier, title, owner, due date, link, and the mirror's identifier and
   link when there is one.
3. Updated: project, identifier, title, each changed field with its old and new value, link.
4. Closed: project, identifier, title, link.
5. Skipped: the item and the reason.
6. Needs input: a project still awaiting confirmation, a match still awaiting confirmation, an
   owner with no member mapping, a Create with no destination, a closure that was not plainly
   stated, and a spoken instruction still awaiting confirmation.

Attach the path of the saved notes. Flag anything still `TBD`, unassigned or unconfirmed.

## Other trackers

ClickUp, Linear, Jira, Asana and Monday.com go through their tracker agents. For any other tracker, find the active
profile in two lookups:

1. The row's tracker: its project's entry in `project_trackers`, otherwise `tracker`, from
   `pods/pm/pm-config.yaml` when that file is present. With no pm config, or neither set, ask
   the user which profile to use.
2. The profiles: read `pods/pm/trackers.yaml` when it is present, otherwise this folder's
   `shared/trackers.example.yaml`.

The profile whose `name` matches the row's tracker is the one this skill uses for that row.

The reconciliation table, the match rules and the approval rules do not change. Only the tool
calls do:

- Candidate matches and the read-back after each write use the profile's `read_tools`.
- Every approved create, update and close goes through the profile's `write_tools`.
- A concept the profile lists under `gaps` is handled as the profile says. The row stays in the
  table, and its Lands in cell names the substitute.
- The report states each write only as the tool returned it.

Nothing is written until the user approves the table.

With no profile for the tracker, run the `connecting-a-tracker` skill first. It probes the
server read-only and saves a profile, then this skill resumes at the table.

## Guardrails

- Confirm the project whenever the correlation is weak or the meeting spans projects. Filing work
  under a guessed project does as much damage as a duplicate.
- Extraction, project resolution and matching run on their own. Every write waits for approval
  of the table and the final go-ahead, or a pre-approval in the person's own request, so no
  tracker sees a change before that approval.
- A confirmed match rules out Create for that row; the row becomes an Update of that item.
  Prefer Update over Create.
- No Update or Close on a match the person has not confirmed. A pre-approved run confirms
  Updates on a Match only; its Closes still wait.
- Change a state, date or status only on a plain statement in the record. Ambiguity becomes a
  flagged row.
- Apply a spoken instruction only when it clearly addresses the agent. AI as the topic is not an
  instruction, uncertain ones are confirmed rather than applied, and blanket ones are confirmed
  first with their rows kept visible.
- Report results only as the tracker agents returned them. Claim no write that was not confirmed
  back.
- Fabricate nothing. No action, update, project, owner or date appears unless the record or the
  person's reply to the table supplies it.
- No side effects beyond the approved rows, and no sharing or permission changes.
- Keep the notes and the record out of external services. Save locally and let the person route
  them.
- Reporting follows the pod's writing standard: U.S. English, decision first, identifiers and
  links attached, open questions flagged.
