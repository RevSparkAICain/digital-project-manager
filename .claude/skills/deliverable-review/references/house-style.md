# House Style

The banned phrases, banned words with their plain swaps, the em dash rule and the quality bar
live in `house-style/writing-standard.md` (the `house-style` skill, installed
beside this skill). Read them from there at review time. This file keeps no copy of the
lists, so there is one place to edit them and nothing to drift.

## How the wording pass applies them

- **Scope.** Every piece of prose in the deliverable: slide and page text, speaker notes,
  table and chart labels, alt text, headers and footers, cell text in spreadsheets, and the
  body and subject line of a written communication.
- **Sections to read.** Section 2 (banned phrases), section 3 (banned words and plain
  swaps), section 4 (no em dashes) and section 5 (quality bar) of `writing-standard.md`.
- **Fix or flag.** An em dash, or a banned word or phrase with a meaning-neutral swap, is an
  auto-fix. Any other wording change is a flag with a proposed rewrite, per the disposition
  model in `SKILL.md`.
- **Exemption.** Literal technical terms and proper names keep their real spelling, as the
  standard's exemption says. Do not "fix" a command name, a statistical term, a metric named
  in a source system, or a product name.
- **Em dash check.** Confirm with a byte scan for `E2 80 94`, not by eye.
- **Missing standard.** If `house-style/writing-standard.md` cannot be found, say so in the
  scorecard and run the em dash check only. Do not fall back on a remembered list.
