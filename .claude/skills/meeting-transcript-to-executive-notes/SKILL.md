---
name: meeting-transcript-to-executive-notes
description: Turn a raw meeting transcript, rough meeting notes, or both into executive notes grouped by subject, with corrected transcription errors, one block per subject (summary, discussion, decisions, actions, open questions, risks and blockers) and four consolidated registers, then save them as a branded Word file and a matching PDF. Use whenever a transcript or set of notes is handed over and the person wants it cleaned up, written up, summarized, turned into notes, or made sense of, for a meeting, call, standup, interview or review, even if they never say executive notes. With nothing supplied, ask for the source material and stop.
---

# Meeting transcript to executive notes

The output is a document a busy reader can scan: what was covered, what was decided, who owes
what by when, what is still open, and what could go wrong. It is organized by subject, never
by the order things were said.

## Inputs

- Required: a transcript, rough notes, or both.
- Optional, used only to sharpen names and spelling: a participant list with roles, a glossary
  of the systems, suppliers, projects and abbreviations the team uses, an agenda.
- Optional inputs never become content by themselves. A glossary term or agenda line shows up
  in the notes only if the meeting actually covered it. A participant list is ground truth for
  who is who.
- If no transcript or notes arrive with the request, ask for them, mention the optional
  inputs, and stop.

## Where each file comes from

For every file this skill reads, use this order:

1. the project's own file, if present:
   - `pods/meetings/meetings-config.yaml`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
   - `brand/brand.json` (read by `scripts/md2docx.py`, which has its own lookup)
2. otherwise, this folder's shared/ copy:
   - `shared/meetings-config.example.yaml`
   - `shared/writing-standard.md`
   - `shared/brand.json`

## Procedure

1. Read every input to the end before drafting. Build the speaker roster while reading. It
   stays internal.
2. List the subjects. A subject is any thread a reader would follow on its own: a workstream,
   a system, a supplier, a process, an area that needs a decision, or an agenda line.
3. Put each business statement under exactly one subject.
4. Delete business-irrelevant talk entirely: greetings, weekend chatter, weather, health,
   jokes, waiting for late arrivals, goodbyes. Do not summarize it, quote it, or mention that
   it happened.
5. Merge across the whole meeting. If a subject was dropped and picked up again later, gather
   both passes into its single block. Collapse repeats into one statement. There is one block
   per subject, and no statement appears under two subjects.
6. If someone reversed or softened a stance midway, write down where the group finally
   landed, as the decision or agreement. Keep the earlier stance only when the shift altered
   scope, ownership, timing, or something still unresolved. Never retell the debate.
7. Size each subject like an agenda line or a distinct workstream, decision or system. Fold
   small threads into the subject they serve. Split a block that bundles two unrelated
   decisions, owners or systems which readers would follow separately. A one-line subject is
   acceptable only when that line is itself a decision, action or risk.
8. Apply the correction rules, then the rewrite and discussion rules, then the action rules
   (all below).
9. Name each subject with a short noun phrase built from the real system, supplier, project
   or process name, spelled as corrected. No verbs and no people in subject names.
10. Order subjects by where each first got real discussion. If the person asks for importance
    order, put decisions and at-risk items first.
11. Write the output format below, then run the quality checklist silently.

## Speaker roster

Many transcripts carry only generic labels such as `Speaker 1`. Before writing, match each
voice to a name and role. The roster exists only so ownership lands on the right person. Never
print it, and never add an attendee section because of it.

Evidence, strongest first:

1. Names and roles the person supplied, or true name labels in the transcript. Treat as fact.
2. Direct address. A name spoken to someone identifies the listener, and the reply that
   follows usually identifies the responder.
3. Role and ownership language. A remark that ties a voice to a function, a team, or work it
   already did or promised identifies that voice and its later turns.
4. Turn continuity. One voice carrying a thought across adjacent lines, or a clean
   question-and-answer pair, can extend an identification already made. It never starts one.

Rate every identification high, medium or low.

- A supplied name, or being addressed by name: high.
- A role cue that points to one person's function but never names them: medium.
- Continuity alone, or an unclear voice: low.
- When an explicit label disagrees with the interaction cues, keep the label and lower the
  rating one tier.
- A clearly garbled name whose person is obvious is written correctly.
- A weak identification is never presented as fact.

## Rewrite rules

- Turn speech into short business statements. A stated aim becomes a goal line. A question
  becomes an open question. A consent becomes an agreement line, but only when someone is
  clearly on the hook to carry it out. A promise to act becomes an action.
- Drop reporting verbs and every other soft attribution.
- Keep meaning, limits, decisions, commitments, risks, dependencies, specifics, dates,
  owners, due dates and unresolved questions intact.
- Anything unclear goes to that subject's open questions.

## Discussion rules

- No "so-and-so said" phrasing of any kind.
- Each point stands alone and opens with what it concerns. A short leading label (Topic,
  Agreement, Issue, Dependency, Risk) may introduce it. Use only the labels that fit.
- Use a person's name only when that person owns an action or deliverable, is accountable for
  a system, process, workstream or outcome, explicitly approved or decided something, or must
  be named to settle an ambiguity such as competing positions.

## Action rules

- An action exists only when someone plainly commits themselves, or a named group, to doing,
  owning, sending, reviewing, following up, validating, scheduling, creating, updating or
  finishing something.
- No action from general talk, suggestions, possible next steps, implied work, ideas nobody
  took, vague remarks, questions or assumptions.
- One accountable owner per action, never a list of alternatives:
  - owner stated, or roster confidence high: the name;
  - roster confidence medium: `likely <name>`, still a single owner;
  - roster confidence low, or nobody named: `Owner: TBD`.
  - Decisions and discussion points that name an accountable person follow the same tiers.
  - Several candidates raised and none settled: the item is an open question until one is.
- Due date: a date only when it was spoken as the deadline for that very action. Otherwise
  `Due: TBD`. The meeting date is never a due date by default. Example of the mistake: a
  meeting on March 12, 2030 where Jordan Lee agrees to "look at the shared mailbox rules"
  with no deadline. The action reads `Due: TBD`, not `Due: March 12, 2030`.
- When the action and its owner are not both clear, record an open question instead.

## Correction rules

- Fix a mis-heard word, name, product, supplier or term when context makes the intended one
  clear. Normalize product names, abbreviations and tools at high confidence only. A
  transcript line reading "the post gress upgrade" becomes PostgreSQL.
- At low confidence, keep the original wording or move the item to open questions. Do not
  guess.
- Intended meaning beats literal transcription.
- Repair grammar damaged by transcription: broken sentences, doubled words, fragments, stray
  punctuation.
- Remove verbal noise: fillers, false starts, restarts, partial words.
- Settle who said what from context where possible. Ownership the source leaves unclear is
  TBD.
- Never change a decision, commitment, owner, date or scope unless context clearly supports
  the correction.

## Output format

Markdown, with these top-level headings in this order, unnumbered:

```
# Overview
# By subject
# All actions
# All decisions
# All open questions
# All risks and blockers
```

**Overview.** A brief executive summary of the entire meeting that draws on every subject:
what was achieved, the main themes, choices made, exposure, and what happens next.

**By subject.** One `## <Subject>` heading per subject. Inside it, bold labels in this order.
The first two always appear. The rest appear only when the subject has content:

```
**Summary:**           one to three sentences: what was covered and where it landed
**Discussion:**        standalone points, one bullet each
**Decisions:**
**Actions:**
**Open questions:**
**Risks and blockers:**
```

Item lines:

- Action in a block: `- <action> | Owner: <name, likely <name>, or TBD> | Due: <Month D, YYYY or TBD>`
- Action in the register: the same line plus ` | Subject: <subject>`
- Decision, open question or risk in a block: `- <text>`
- Decision, open question or risk in a register: `- <text> | Subject: <subject>`

**Registers.** Four of them: actions, decisions, open questions, and risks and blockers. Each
repeats every entry from the blocks word for word and adds the subject tag, so the counts
match the blocks exactly. An empty register holds exactly one line: `- None recorded.`

Nothing follows the last register. There are no numbered sections or blocks.

## Constraints

- Ground every statement in the inputs. Never invent facts, decisions, actions, risks, owners,
  dates or next steps, and never infer a commitment nobody expressed.
- Never state a headcount, total or fraction nobody said. Carry a speaker's percentage as
  their number. Example of the mistake: a speaker says "about 70% of the databases moved" and
  the notes turn it into "7 of 10 databases", which invents a total.
- The input is invisible in the output. Nothing attributes content to the recording or the
  notes, cites them, or describes how the notes were made. Example of the mistake: an owner
  field reading `Owner: Priya Shah (per the recording)`.
- The document agrees with itself. The overview never contradicts a block or a register, and
  any status, count or date reads the same everywhere. Example of the mistake: an overview
  calling the archive done while its block lists the action as open.
- Organize by subject, never by timeline.
- No hyperlinks, citations, source links, file links or linked text.
- U.S. English spelling, grammar and dates. Plain text or Markdown only. The writing standard
  applies, including its banned words, banned phrases and the ban on the long dash.
- Keep secrets, credentials and personal data out of the notes.

## Saving the notes

1. Read `output_dir`, `notes.file_pattern`, `notes.doc_type` and `notes.type_label` from
   `meetings-config.yaml`. Create `output_dir` if it does not exist.
2. Build the file name from `notes.file_pattern`. The meeting name comes from the agenda, the
   meeting title or the transcript's file name. The date is written `DDMMMYY`, as in
   `12Mar30`. When the meeting date cannot be found, fall back to the date on the transcript
   or its file. When the record gives a day and month but no year, use the current year and
   flag the year as inferred in the notes and the report. Never take the year from the file's
   properties: a template or an edited copy often carries an older year.
3. Same-day repeats: when two or more instances of one meeting share a date, every one of
   them gets its start time appended in parentheses as 24-hour `(HHMM)`. Take the time from
   the transcript's file name, which usually holds a compact date followed by a compact time.
   A meeting alone on its date keeps the plain name.
4. Before every write, list `output_dir` and look for the target name.
   - A file is there and belongs to a different meeting: write yours with the time suffix and
     leave the other file alone. Never overwrite another meeting's notes.
   - A file already holds the plain name and comes from a prior session of this same
     meeting: mention it in the reply and leave any rename to the person. Never rename a file
     that is already in circulation.
5. Write the Markdown to a scratch file, then render it with the bundled script. Run it from
   this folder, or give the full path to `scripts/md2docx.py`:

   ```
   python scripts/md2docx.py <notes.md> --out "<output_dir>/<file name>.docx" \
     --title "<meeting name>" --topic "<what the meeting covered, alone>" \
     --date "<Month D, YYYY>" --operator "<operator name>" \
     --doc-type "<notes.doc_type>" --type-label "<notes.type_label>" \
     [--footer "<left footer text>"] [--brand <brand.json>]
   ```

   - `--operator` is the actual name of whoever is running the session, resolved by the
     orchestrator. Never a placeholder, and never a name carried over from an earlier run or
     from an example.
   - `--topic` is what the meeting was about and nothing else. The script builds the byline
     itself, so a topic that already holds a pipe or "Prepared by" is refused.
   - `--doc-type` and `--type-label` must differ. They are different words on purpose.
   - Do not build the document by hand or edit it afterward. If the output needs to change,
     change the script.
6. Send the finished file through the `deliverable-review` skill before returning it. This
   step is mandatory.
7. Export a PDF of the reviewed `.docx` and save it beside it as `<file name>.pdf`. The PDF
   shows the first-page band and logo in any viewer; some `.docx` viewers skip a first-page
   header. Use the review skill's renderer, which prints through Word:

   ```
   & "<WORKSPACE_ROOT>/.claude/skills/deliverable-review/assets/render-deliverable.ps1" `
     -In "<output_dir>/<file name>.docx" -Out "<scratch folder>" -NoPng
   ```

   Copy the `<stem>.pdf` named on its first output line to `<output_dir>/<file name>.pdf`.
   Export again whenever the `.docx` changes, so the two never differ. When the script exits
   non-zero (no Word on the machine, for example), return the `.docx` alone and say the PDF
   was skipped and why. The check in step 4 covers the `.pdf` name too.
8. Writing the files ends the job. The notes are never sent to anyone from here.

## Quality checklist

Run silently before finalizing.

- Organized by subject, not by timeline.
- One block per subject. Nothing repeats across subjects, revisited threads are merged, final
  positions are recorded, and a debate appears only where it moved scope, an owner, a date or
  an open item.
- Each block opens with a summary and carries discussion points; categories with nothing in
  them are omitted.
- The four registers match the blocks in wording and count, each entry carries its subject,
  and empty registers hold `- None recorded.`
- No links, citations or source references. No numbered sections.
- Nobody is quoted or credited with speaking. A name shows up only where it marks who owns
  something, answers for it, approved it, or clears up confusion.
- Every action was plainly committed to and has an owner field and a due field. Exactly one
  owner, `likely <name>`, or TBD. Every due date was spoken for that action, and none came
  from the meeting date.
- No headcount, total or fraction the inputs did not state. Percentages are the speaker's.
- The input never shows. The overview agrees with every block and register.
- File name checked against the folder. Same-day repeats carry the `(HHMM)` suffix.
- Roster identifications rest on supplied names, being addressed by name, or cues tying a
  voice to a role or task. Uncertain owners are hedged or TBD. The roster is not printed.
- No small talk, speculation or inferred next steps. Corrections made only at high confidence.
- The writing standard is satisfied.
