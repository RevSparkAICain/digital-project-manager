# plain-language-translation

Rewrites engineering, security, supplier or project material in everyday business language
and builds the **message core**: six answers in a fixed order (what is changing, when, why
it matters to you, what you must do, what will look different, where to get help), plus an
optional seventh, what is not changing. Every later piece of rollout copy is written from
that core. The skill also frames the core for each audience, maps each group's own words,
lists the jargon it replaced, and records an open question for anything the source leaves
unconfirmed. A bundled script measures each draft's reading grade and mechanics.

## Inputs

- What the source says about the change: the project record, the change ticket, supplier
  documentation, release notes, engineer notes. See `examples/source-change-notes.md`.
- The audience config: `pods/comms/audiences.yaml`, falling back to
  `pods/comms/audiences.example.yaml` until the team writes its own. Each segment sets a
  reading grade, an opening, a length, an example, and the group's own nouns and verbs.
- The benchmark reader: `example_persona` in `pods/comms/comms-config.yaml`, or in the
  example config.
- The writing standard from the installed `house-style` skill
  (`.claude/skills/house-style/writing-standard.md`).

## Outputs

- The message core, the framing table, the group vocabulary map, the jargon list and the
  open questions. See `examples/expected-message-core.md`.
- A JSON check report for every draft written from the core. See
  `examples/expected-check-all-staff.json` (a pass) and `examples/expected-check-weak.json`
  (a fail).

## How to run

In this pod the `tech-translator` agent runs the skill: ask it to translate a change for the
audiences you name. To check one draft yourself:

```
python pods/comms/skills/plain-language-translation/scripts/check_message.py DRAFT.md --grade 8 --allow AM,PM,IT,ACME
```

Pass `--grade 10` for pieces aimed at IT or at leaders. An exit code of 0 means all checks
passed.

The script looks for the house-style `writing-standard.md` in this order:

1. `--standard PATH`, if given.
2. An installed `house-style` skill: climbing from the script's folder, the first folder
   holding `.claude/skills/house-style/writing-standard.md`, or failing that, at the same
   level, the repository copy `pods/core/skills/house-style/writing-standard.md`.
3. This skill's own `shared/` copy, so the folder still works when it is shared by itself.

When none of these exists, the report marks the banned-word check as "skipped".

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Prerequisites

- Python 3.9 or later; the script uses the standard library only.
- A writing standard for the banned-word list: the installed `house-style` skill, or the
  `shared/` copy when that skill is absent.
- Optional: the `comms-director` agent and the other comms skills, which take the message
  core as input. The skill and its agent run without them.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Procedure the agent follows |
| `references/jargon-swaps.md` | Standing table of technical terms and their plain wording |
| `scripts/check_message.py` | Reading-grade and mechanics check that writes a JSON report |
| `shared/writing-standard.md` | House-style writing standard, copied in for use when no installed copy is found |
| `examples/` | Synthetic source notes, the expected message core, two drafts, their expected check reports, and a stand-in writing standard for the tests |
