# it-bulletin

Writes the IT Bulletin: one organization-wide email about a technology change, in one of
four types (planned change, service disruption, reminder, completed change). It fills the
team's house format from a settled message core, checks the reading level with a script,
saves a dated draft, and hands back a send-ready package with a handoff note for the
sender role. It never sends anything itself.

## Inputs

- A message core: the six answers from the `plain-language-translation` skill, or written
  in place by the short method in `SKILL.md` when that skill is not installed. See
  `examples/message-core-printers.md`.
- `comms-config`: `pods/comms/comms-config.yaml` if the project has one, otherwise
  `shared/comms-config.example.yaml`. It supplies the subject prefix, the signature line,
  the sender and approver roles, the time zone, and the output folder.
- The house format: `house-format.md` in this folder if present, otherwise
  `house-format.example.md`.
- Audiences: `pods/comms/audiences.yaml` if present, otherwise
  `shared/audiences.example.yaml`.
- The writing standard: the installed house-style skill if present, otherwise
  `shared/writing-standard.md`.

## Outputs

- A markdown draft whose first line is `Subject: <subject>`, with one `## <Label>` heading
  per house-format block and the signature line at the end. See
  `examples/bulletin-printers.md`.
- A plain-text version of the same body.
- Audience impact tags (high, medium, low, none) per segment.
- A handoff note naming the sender role, the channel, the approver role, the send date and
  time, and any unconfirmed facts.

Drafts are saved under `output_dir` from `comms-config` as
`YYYY-MM-DD-it-bulletin-<topic>.md` and `.txt`.

## Checking a draft

From this folder:

```
python shared/check_message.py examples/bulletin-printers.md --allow AM,PM,IT,ACME
```

The script prints a JSON report (reading grade, sentence and paragraph length, unexpanded
acronyms, vague time phrases, banned words, em dash byte count) and exits 0 when every
check passes. Replace `ACME` with your organization's all-caps short name.

## Using your own house format

1. Copy `house-format.example.md` to `house-format.md` in this folder.
2. Edit the subject pattern, the block labels and order, the sign-off, and the word-count
   targets.
3. Update the `format` block to match: `subject:` is a Python regular expression for the
   whole subject line, and `blocks:` lists the block labels in order, separated by ` | `.
   Keep your `bulletin.subject_prefix` in the regex.
4. Keep `house-format.example.md` in place. The skill reads `house-format.md` first and
   falls back to the example only when yours is missing.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure the agent follows |
| `house-format.example.md` | The ACME house format, with the `format` machine block |
| `examples/message-core-printers.md` | Worked input: the message core for a printer change |
| `examples/bulletin-printers.md` | Worked output: the finished bulletin |
| `shared/` | Copies of the writing standard, the pod config, the audiences file, and the readability check script |
