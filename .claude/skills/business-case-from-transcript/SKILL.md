---
name: business-case-from-transcript
description: "Write a business case Word file from a recorded scoping or funding call and any files that came with it. The agent drafts a grounded content.json and a script places it into a blank template by anchors. Use when someone supplies call notes or a recording and asks for the case to be written up. Gaps are marked TBD and listed, never guessed. Not for charters, status reports or minutes."
---

# Business case from a transcript

The agent reads a recorded or transcribed project discussion and writes the business case as
one JSON file, `content.json`. Two scripts do the layout: `scripts/make_template.py` builds a
blank branded template when the team has none, and `scripts/fill_business_case.py` places the
content into a template by the anchors named in a profile. The result is a Word document with
two registers at the end. It goes through review, then on to the approval step the config names.

## Inputs

- **The discussion record (required).** A transcript, call notes or raw meeting notes.
- **Supporting files (optional).** PDFs, Word files, decks, email threads, earlier notes.
- **Settings.** Keys in the pod config: `business_case.template`, `business_case.profile`,
  `output_dir`, `approval_gate`.

Read every input in full before drafting. These inputs are the whole factual basis. General
knowledge, guesses about the organization and figures from memory are not sources. With no
discussion record, ask for it and stop.

## Where files come from

For the pod config and the writing standard, use the first of these that exists:

1. the project's own file, if present (`pods/pm/pm-config.yaml`)
2. otherwise, this folder's shared/ copy

How the settings resolve:

- `business_case.template`: a team's own blank template. Empty means run `make_template.py`
  and use what it writes.
- `business_case.profile`: the anchors profile for that template. Empty means
  `references/anchors.example.json`, which describes the generated template.
- `output_dir`: where the finished document is saved, under a dated file name.
- `approval_gate`: the step the finished case goes to. Never hard-code the gate's name in
  this skill or in code; read it from the config.

The generated template takes its fonts and colors from the brand file: `--brand`, then the
`BRAND_JSON` environment variable, then the nearest `brand/brand.json`, stopping at the project
root (the nearest folder holding pods/ or .claude/), then `shared/brand.json`.

## The sections

The generated template has eight sections. Each has one job, and that job is the drafting guide.

| Section | What it is for | How to write it |
|---|---|---|
| Summary | One short read for a busy approver | State the request, the option recommended and the exact decision sought. |
| Problem or opportunity | Why anything should change | Who is affected, what it costs now, with figures and dates. Do not describe the fix here. |
| Options considered | The choice set | One entry per option, doing nothing included, with the reason each other option lost. |
| Recommended option | The answer | Name it, say what it consists of, and tie each reason back to the options. |
| Costs and benefits | The money | Table rows: item, type, amount, timing. A total only when a source gives it or it is plain arithmetic on sourced figures; otherwise `TBD`. |
| Risks | What could go wrong with the recommendation | Table rows: risk, likelihood, impact, score (likelihood times impact), response, owner. An owner not named in the sources is `TBD`. |
| Timeline | When | Milestones with target dates and owners. A date the sources do not give is `TBD`. |
| Approval | Who decides | Roles and names only when the sources name them. Decision and date stay `TBD` until a decision exists. Never fill a signature. |

Keep goals apart from the measures that show they were met, and planning assumptions apart from hard limits. Say which is which.

The detail fields are `project`, `sponsor`, `prepared_by` and `date`. They come from the
sources and the operator. `prepared_by` is the person running the skill.

## Steps

1. **Read and extract.** List the facts first: numbers, dates, scope, people and roles,
   options, decisions, risks and stated assumptions. Note where each came from (timestamp,
   page, section or speaker turn).
2. **Draft `content.json`.** Write each section from those facts alone, in short decision-first
   prose that follows the writing standard. Shape:

   ```json
   {"fields": {"project": "", "sponsor": "", "prepared_by": "", "date": ""},
    "sections": {"summary": ["paragraph", "paragraph"]},
    "tables": {"costs": [["Item", "Type", "Amount", "Timing"]]},
    "sources": ["file and place in it"],
    "missing": ["what is missing, or what needs confirming"]}
   ```

   `fields`, `sections` and `tables` hold exactly the profile's keys. Every section list has at
   least one paragraph. Every table row is as wide as its header. Values are strings only.
3. **Handle gaps.** A missing or unclear value is written `TBD`, or `TBD: <what is missing>`
   where the cell needs to say. Never leave it blank and never guess. Every `TBD` has a
   matching entry in `missing`. When two sources conflict, use the more authoritative or more
   recent one and add a `missing` entry that names the conflict and asks for confirmation.
4. **Ask only when stuck.** Ask a question only when a sound draft is impossible without the
   answer, and ask at most five. Otherwise draft with `TBD` and let review catch the rest.
5. **Get a template.** Use `business_case.template` if set. Otherwise run
   `python scripts/make_template.py --out <template.docx>`.
6. **Fill.** Run:

   ```
   python scripts/fill_business_case.py --template <template.docx> --profile <anchors.json> --content content.json --out <output_dir>/<dated name>.docx
   ```

   The script checks the profile and the content first, then every anchor, and writes the file
   only when all of them were found. Exit code 0 prints the path. Exit code 1 prints one line
   naming the problem: fix it and run again. A partly filled document is never handed on.
7. **Review.** Send the saved file through `deliverable-review` before the user sees it.
8. **Route.** Pass the reviewed file to the step named by `approval_gate`. The skill drafts;
   people approve. It never marks an approval as given.

## The two registers

The fill appends two registers after the last section, titled by the profile's `registers`
entry. In the example profile they are `Sources used` and `Missing information`.

- **Sources used:** one bullet per source and the place in it. `sources` is never empty.
- **Missing information:** one bullet per gap, assumption to confirm or conflict. With none, the
  document shows `None.`.

## Grounding rules

- Never invent a figure, date, name, benefit, cost, risk or decision. If the sources do not say
  it, it does not appear as fact.
- Trace every material claim to an entry in `sources`.
- Pick one name for the project, each option and each person, and use it everywhere.
- Report what was said in the sense it was said. A summary must not change who decided what.
- Stay inside the sources. No secrets, credentials or personal data beyond the names and roles
  the case needs.

## The template is filled, never edited

The skill does not restyle a template, add, remove, rename or reorder its sections or tables,
or change fonts, spacing, shading, headers or footers. It fills the detail fields, replaces each
placeholder with content in the placeholder's paragraph style, fills table rows (adding rows
in the existing row format when there are more than the template holds) and appends the two
registers. The template file is never overwritten: the fill refuses an `--out` that is the
template, under any spelling of the path. If the content seems to need a structural change,
stop and ask the template owner (a role, not a person).

## Writing a profile for your own template

The profile is a JSON file with four parts, shaped like `references/anchors.example.json`:

- `fields`: content key to the label text in column 1 of a details-table row.
- `sections`: content key to the `heading` text and the opening words of the placeholder
  paragraph under it.
- `tables`: content key to the exact header row texts, as a `header` list.
- `registers`: the titles for the sources and missing registers.

To write one: open the team template, copy each heading and the first few words of its
placeholder, copy each table header row, choose a content key for each, then run a fill with a
test content file. A failed fill names every profile key that did not match, so the author fixes
those entries and runs again. Matching ignores extra spaces, line breaks and curly-versus-straight
quotes.

## Quality checks before handing over

- `content.json` passes the content check against the profile in use (the fill runs it first).
- Every `TBD` has a `missing` entry, and every `missing` entry points at something in the
  document or at a conflict.
- Every figure and date appears in a source. Check each total by hand.
- `sources` names the place in each source, not only the file.
- Names of the project, people and options are identical across sections and tables.
- No placeholder text remains on the rendered page.
- The writing standard holds: no banned words, no em dashes.
- The fill exited 0 and the output opens and renders.

## Never

- Invent a fact to avoid a `TBD`.
- Change a template's look or structure.
- Overwrite the template, or hand on a document from a failed fill.
- Install packages from the scripts. If python-docx is missing, the fill stops with the line
  `pip install python-docx`; run that yourself.
- Record a decision, a signature or an approval that the sources do not show.
