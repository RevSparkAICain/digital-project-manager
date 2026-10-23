---
name: it-bulletin
description: Write the IT Bulletin, the organization-wide email about a technology change, filled into the team's own house format and handed back as a send-ready package. Use whenever someone asks for an IT Bulletin, a bulletin, an all-staff technology notice, a maintenance or change notice, an outage or service disruption notice, an update on a disruption, a reminder about an IT action with a deadline, a notice that a change is complete, or a department version of one. Covers four bulletin types (planned change, service disruption, reminder, completed change). Produces the subject line, the body in the house format's block order, a plain-text version, the audience impact tags, and a handoff note for the sender role, checks the reading level with a script, and never sends anything itself.
---

# IT Bulletin

This skill turns a settled message core into one IT Bulletin: a subject line and a body in
the house format, ready for the sender role to paste and send without edits. It fills the
house format and adds nothing to it. Layout belongs to the format file; wording belongs to
the message core; recipient lists belong to whoever owns the channel, and the skill describes
groups but never picks recipients; send approval belongs to the approver role. The skill
never sends.

`examples/message-core-printers.md` is a worked input and `examples/bulletin-printers.md`
is the bulletin built from it.

## Inputs

- **Message core.** The six answers (what is changing, when, why it matters to you, what
  you must do, what will look different, where to get help), plus "what is not changing"
  when true. It comes from the `plain-language-translation` skill when that is installed.
  If it is not, write it in place (see "No message core yet" below).
- **comms-config.** The bulletin name, `sender_role`, `sender_address`, `signature_line`,
  `subject_prefix`, the enabled `channels`, `time_zone`, `approver_role`, `requester_role`,
  `brand_language_rules`, and `output_dir`.
- **House format.** The subject pattern, the ordered blocks and their labels, the sign-off,
  and the word-count target per type.
- **Audiences.** The segments, their reading grade, and their own vocabulary, used to tag
  each segment's impact and to pick the reader's words.
- **The request.** The bulletin type, the system or topic, the affected audience, and the
  timing: start and end for a planned change, a verified start for a disruption, the due
  date for a reminder, the completion time for a completed change. For a disruption, also
  the symptom, the effect on work, and who is working on it.

## Where each file comes from

For every file the skill reads, use this order:

1. the project's own file, if present:
   - `pods/comms/comms-config.yaml`
   - `pods/comms/audiences.yaml`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
   - `house-format.md` in this folder
2. otherwise, this folder's shared/ copy:
   - `shared/comms-config.example.yaml`
   - `shared/audiences.example.yaml`
   - `shared/writing-standard.md`
   - for the house format, `house-format.example.md` in this folder (the ACME example;
     the house format has no `shared/` copy)

So the house format comes from `house-format.md` when the team has written one, and from
`house-format.example.md` otherwise. Say in the handoff note which one you used.

## Bulletin types

Classify every request as exactly one of these. If it fits none, return it to the
requester instead of inventing a fifth type.

| Type | Use when | Required content |
|---|---|---|
| planned change | Something will change or go offline on a known date | Dated, numbered steps; one help path; the change window; what stays the same |
| service disruption | Something is broken or slow now | The symptom; the effect on work; who is working on it; an updates area, newest entry first |
| reminder | An action from an earlier bulletin is still due | The outstanding action and its date |
| completed change | A change has finished | What is now different; one recovery step if a reader may still need it |

## No message core yet

If `plain-language-translation` is not installed, write the message core yourself before
drafting, using this short form of its method:

1. Read the real source (ticket, project record, vendor notes) and list every fact you cannot confirm as an open question.
2. Write the six answers in order (what is changing, when, why it matters to you, what you must do, what will look different, where to get help), plus what is not changing when true.
3. Make each step numbered, start it with a verb, and give it a calendar date; name exactly one help path.
4. Aim for grade 8: short sentences, every acronym spelled out at first use, and a change that still makes sense with the product name removed.
5. Use each audience's own nouns and verbs from the audiences file, not the project's terms.

## Steps

1. **Choose the type.** Pick one of the four types above.
2. **Confirm the facts.** Check every date, time, system name, and the affected audience
   with the team that owns it. Never carry a time forward from an earlier bulletin without
   checking it again. Mark anything unconfirmed as `[UNCONFIRMED: ...]` in the draft
   rather than guessing, and list it in the handoff note.
3. **Load the house format.** Read the subject pattern, the block list, and the sign-off
   from its `format` block, and the word-count target for the type from its prose. If the
   format has no place for who is affected, what to do and by when, or where to get help,
   stop and report the gap. If it has smaller defects (see the format's "Silent fixes"
   section), fix them silently in the draft and list them in the handoff note.
4. **Fill in the format.** Write every block from the same message core so no fact drifts
   between the subject, the body, the plain text, and any variant.
   - Put the action block above the explanation. Number each step, start it with a verb,
     and give it a calendar date. If the reader has nothing to do, say so in that block.
   - Give exactly one help path, as descriptive link text, never a raw address.
   - Write the times in one time zone and name it once.
   - Spell out every acronym at first use.
   - Use second person and active voice for what the reader does, third person for what
     the IT team does. No apology paragraph, no sales framing, no closing pleasantry.
   - Compose the subject from the pattern. It must match the regex, fit a phone, and never
     be only an urgency word.
   - End with the `bulletin.signature_line` value, nothing more.
   - Trim to the type's word-count target.
5. **Tag each audience's impact.** For each segment in the audiences file, record high,
   medium, low, or none, with a one-line reason. If one segment's required action differs
   from the rest, it is a separate audience: return it for planning, to `comms-strategist`
   when installed, otherwise to the requester role, rather than forking the bulletin. When the request asks for department variants, keep
   every fact identical and change only the lead, length, example, and vocabulary.
6. **Run the readability check** from this folder:

   ```
   python shared/check_message.py <draft> --allow AM,PM,IT,<ORG>
   ```

   `<ORG>` is the organization's all-caps short name (`ACME` in the examples). The script
   finds the writing standard in the lookup order above: the installed house-style skill
   first, then `shared/writing-standard.md`. The bulletin goes to all staff, so the default
   grade 8 applies.
   Fix every failure and run it again until `status` is `pass`.
7. **Run the house-style checklist.** Work through the pre-handback checklist in section 6
   of the writing standard. Apply `brand_language_rules` if the config names a file. The
   standard covers the subject, the plain text, alt text, file names, and the report back.
8. **Make the plain-text version.** Remove the markdown. The action, the dates, and the
   help path must still read correctly with no formatting. If the bulletin uses an image,
   write alt text that carries the same message, and keep the action, the dates, and any
   error text in the body as well.
9. **Save.** Write the draft to `output_dir` as `YYYY-MM-DD-it-bulletin-<topic>.md` and the
   plain text next to it as `YYYY-MM-DD-it-bulletin-<topic>.txt`. The first line of the
   markdown draft is `Subject: <subject>`.
10. **Send it through review.** Route the draft through the `deliverable-review` skill when
    it is installed, apply the formatting fixes it returns, and pass
    wording or content flags to the approver role. If it is not installed, say in the
    handoff note that the draft is unreviewed.

## Handoff note

Return a short note with the draft. It names:

- the `sender_role` who sends it (for ACME, the IT Service Desk) and the channel: email
  from `bulletin.sender_address`, unless the request names another enabled channel in
  `channels`
- the `approver_role` who approves it before it goes out
- a reminder that the channel owner picks the recipients
- the exact subject and the saved file paths
- the audience and the impact tags from step 5
- the intended send date and time
- which house format file was used, and any format defects fixed silently
- any `[UNCONFIRMED: ...]` facts and the review result

Recipient lists belong to whoever owns the channel; this skill describes groups and never picks
recipients.
Anything the sender would have to edit before sending is a defect in the package; fix it
before handing over. The skill never sends.

## Rules

1. The house format governs layout. Add no block, label, or sign-off of your own.
2. A planned change without dated steps, the action block, or a help path has failed.
3. A service disruption always has an updates area, newest entry first.
4. Every deadline is a calendar date, never a span of time.
5. At most one help path per bulletin.
6. Anything the reader must act on has to appear as live text. When an image shows the required step, the due date, or an error string, the body also spells it out in words.
7. Never carry an unconfirmed time forward, and never let the meaning depend on a pasted
   screenshot.

## Writing standard

Everything this skill produces follows the house-style writing standard (read in the
lookup order above): the subject, the body, the plain text, alt text, file names, and the
handoff note. Treat an em dash as a build failure and confirm with the byte scan the check
script runs.
