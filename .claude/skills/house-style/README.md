# house-style

The writing standard for every piece of prose the workspace produces: chat replies, emails,
briefings, reports, deck and document copy, tracker comments and review notes. It applies to
the orchestrator and to every specialist agent.

## Inputs

A draft to write or revise, or a draft to check. The standard itself lives in
`writing-standard.md`.

## Outputs

Prose that follows five rules:

1. Answer first: the first sentence carries the answer, recommendation or decision.
2. No banned phrases (section 2 of the standard).
3. No banned words; each one has a plain swap (section 3).
4. No em dashes; use a colon, comma, parentheses or a period (section 4).
5. The quality bar: complete, specific, structured, faithful to the source, facts kept
   separate from judgment (section 5).

Literal technical terms and proper names keep their real spelling even when they match a
banned word.

## How to use it

The skill triggers whenever an agent writes or revises text a person will read, or checks a
draft against the lists. Before handing a draft back, run the six-question pre-handback
checklist in section 6 of `writing-standard.md` and fix each hit in place. To find em dashes
reliably, scan the file's bytes for `E2 80 94`.

The lists are meant to be edited. Change `writing-standard.md` to match your team, keeping each
banned word paired with a swap.

## Prerequisites

None. It is a prompt-only skill with no scripts. See `docs/prerequisites.md` for the rest of
the folder.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The rules in short and how to apply them |
| `writing-standard.md` | The full standard and the editable lists |
