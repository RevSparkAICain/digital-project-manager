---
name: plain-language-translation
description: Rewrites engineering, security, supplier or project material as everyday business language that an employee outside IT can act on, and builds the message core that all later rollout copy draws from. Reach for it when business staff need a technology change explained, for example a security or IT rollout, a move to a new system, a different way to sign in, a planned outage, a policy update, a set of release notes, or an audit finding written for a non-technical audience. Typical requests include "put this in words the business understands," "rewrite this for people outside IT," "make this clear to end users," "say this so the sales floor follows it," and "simplify this." Outputs the six-answer message core, framing per audience, and a vocabulary map per group; measures reading level with a bundled script; and lists anything the source does not confirm as an open question rather than filling the gap.
---

# Plain-Language Translation

A message that is correct but unreadable has still failed. This skill turns technical
source material into one **message core**: six answers in a set order. The announcement
email, the chat post, the manager talking points, the one-pager and the deck are all
written from that single core, so every piece says the same thing.

In this pod the `tech-translator` agent runs the skill, and the other comms skills take
its output as their input.

## Inputs

- Source material about the change (Step 1 lists the kinds).
- The audience config. Each segment in it carries framing settings and the group's own
  words.
- The benchmark reader, set as `example_persona` in the comms config.
- The house-style writing standard.

## Where each file comes from

For every file the skill reads, use this order:

1. the project's own file, if present:
   - `pods/comms/comms-config.yaml`
   - `pods/comms/audiences.yaml`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
2. otherwise, this folder's shared/ copy:
   - `shared/writing-standard.md`
   - this folder carries no copy of the two config files, so read
     `pods/comms/comms-config.example.yaml` and `pods/comms/audiences.example.yaml`
     until the team writes its own

## Step 1: Collect the facts first

Before drafting anything, read what actually exists about the change. Typical sources:

- the project's entry in the team's tracker;
- the change ticket;
- the supplier's documentation and release notes;
- the engineer's or architect's write-up;
- anything already sent to staff about the same change.

Keep a running list of what the sources leave unconfirmed. Each item on it becomes an open
question in the output. Dates, gains for the reader, figures, supplier behavior and support
promises never come from your own assumptions.

## Step 2: Build the message core

Write these answers in this order. Each one has to make sense when read by itself.

**1. What is changing.** A single sentence of fewer than 25 words, with no acronym in it.
Keep the product or supplier name out of the subject position. Add it in parentheses only
when the reader will actually see that name on screen.

> Before: "Finance is implementing an automated receipt-capture capability within the
> expense management platform."
> After: "You will claim work spending back by taking a photo of the receipt, not by filling
> in a form (the app is called ACME Expenses)."

**2. When.** Give the date, the time and the time zone. For an outage, name the start and
end and list what cannot be used in between.

**3. Why it matters to you.** State what the reader gains, or the hazard that goes away,
in their words. Leave out the program's reasons and the funding case. When the true answer
is that nothing visible improves for them, write that plainly:

> "Day to day, nothing gets better for you. The update keeps the ordering system on a
> version its maker still fixes, and it costs you about two minutes, once."

**4. What you must do.** A numbered list. Every step opens with a verb and carries a due
date. When the reader has no task, the whole answer is "Nothing. This happens for you."

**5. What will look different.** Name the change the reader will see: a new icon, an added
prompt, a changed sign-in screen, a menu in a new place, a slower first start.

**6. Where to get help.** Exactly one route, named: a queue, an article, drop-in hours or a
person. Given three choices, most readers use none.

**7. What is not changing.** Add this line only when it is true. Telling people what stays
put settles more questions than any statement of benefit.

## Step 3: Hold the copy to the language rules

- **Reading level.** Grade 8 for pieces to all staff. Grade 10 for pieces to IT or to
  leaders. Measure it with `scripts/check_message.py` (see "Checking a draft") instead of
  judging by eye.
- **Short units.** Keep the average sentence below 20 words, and no paragraph longer than
  three sentences.
- **Talk to the reader.** Active verbs, addressed to "you". Write "You will confirm the
  sign-in on your phone," not "identity verification will be enforced for all users."
- **Acronyms.** Spell each one out the first time, then keep using the plain wording rather
  than the letters. The reader does not need to learn the term.
- **Figures, not adjectives.** "About 5 extra seconds the first time you sign in" in place
  of "little impact". "Down from 10 PM to 2 AM" in place of "a short outage".
- **Deadlines are dates.** "By Friday, March 15, 2030," never "over the next few weeks."
- **At most one comparison.** Take it from ordinary life or from the reader's job, never
  from another technology. Leave it out if it does not fit well.
- **Remove the product name as a test.** If the sentence no longer makes sense, it is about
  the tool rather than the change to the reader.
- **Be honest about disruption.** If it will be hard, say so, say for how long, and say what
  support is in place. A surprise costs more trust than a warned-about difficulty.
- **Protection, not fear.** For a security change, explain what now protects the reader. Only
  describe the threat when spotting it is the reader's task, as with phishing or a caller
  posing as IT.
- **House style.** None of the banned words or stock phrases from the house-style lists, and
  no em dashes.

The standing term table is `references/jargon-swaps.md`.

## Step 4: Find the receiving group's words

Deciding who receives the message is not part of this skill. Its job is to write in the
words the team already uses for its own work.

Groups name the same thing differently. A support desk works "cases" that the project calls
"tickets". Finance posts entries. Operations runs work orders and hands off shifts. Legal
keeps policies and records. Copy in the reader's own nouns reads as if a colleague wrote
it. Copy in the project's nouns reads as mail from some other department.

Before drafting:

1. Name the group and describe its daily work, starting from its segment in the audience
   config.
2. List three to five of the group's terms for the systems, records and steps the change
   affects. Sources: the segment's `vocabulary` entries, earlier messages to the group,
   meeting transcripts, ticket text, the project record. Ask when none of these has them.
3. Pair each project or supplier term with the group's term. The copy uses the group's
   term; the project term goes in parentheses only where it appears on the reader's screen.
4. Look at the verbs as well, using the segment's `verbs` list ("close a case", "approve an
   invoice", "hand off a shift"). A stock verb is usually the first sign of generic copy.

When a group's terms are unknown, log that as an open question; a wrong internal word does
more harm than a plain one. When you do learn a group's real terms, suggest adding them to
`audiences.yaml`.

## Step 5: Frame for each audience

Across audiences the six answers carry the same facts. What changes is the opening, the
length, the example and the words. Each segment in the audience config sets `lead_with`,
`length`, `example` and `reading_grade`. The example config ships these defaults, summarized
here (the config holds the exact wording):

| Segment | Grade | Target length | Opens on | Example that lands |
|---|---|---|---|---|
| General staff | 8 | 150 to 250 words | What you do differently, and when | Their own daily task |
| Customer-facing and sales staff | 8 | Under 150 words, scannable, mobile-first | Customer impact and time cost | What to say to a customer who asks |
| Customer Support | 8 | Under 150 words | What the customer on the line sees | A live support call |
| Operations | 8 | 200 to 300 words | Process step changes and cutover timing | The step in their queue that changes |
| Finance | 8 | 200 to 300 words | Effect on month-end close and approvals | A step in the month-end close |
| Business leaders | 10 | 250 words plus talking points | The result for the business, the risk, and what they are asked to do | Their team's readiness |
| IT and Engineering | 10 | Full detail | Technical detail, dependencies, support load | Configuration and known issues |
| Legal and Policy | 10 | 200 to 300 words | What the change means for a policy or contract | The policy or contract clause the change touches |

Read the live values from the config at run time; this table only shows the shipped
defaults.

## Step 6: Review before handing over

Answer each of these before the core leaves your hands:

- After one read, would the benchmark reader know what to do?
- Is the copy in the group's nouns and verbs rather than the project's?
- Is each acronym spelled out where it first appears?
- Is each deadline a calendar date?
- Is there one help route, and only one?
- Does any sentence talk about the technology instead of what changes for the person?
- Is any fact, figure, gain or promise unsourced? If so, cut it or move it to the open
  questions.
- Did `scripts/check_message.py` pass on every draft at that segment's grade?
- Did the house-style checklist pass?

## Checking a draft

`scripts/check_message.py` uses only the Python standard library. It tests a draft
against the mechanical rules in Step 3 and prints the result as JSON.

```
python pods/comms/skills/plain-language-translation/scripts/check_message.py DRAFT.md --grade 8
```

The report covers:

- **Readability:** counts of words, sentences and syllables, the mean sentence length, and
  the Flesch-Kincaid grade measured against `--grade` (8 when omitted).
- **Paragraph length:** any paragraph with more than three sentences.
- **Acronyms:** a run of two to six capital letters or digits counts as an acronym. Its
  first appearance passes only when it sits in parentheses right after a phrase whose words
  begin with its letters, for example "optical character recognition (OCR)". `--allow`
  lists acronyms exempt from this; it defaults to `AM,PM,IT`. Add any all-caps company or
  product name, as in `--allow AM,PM,IT,ACME`.
- **Vague timing:** phrases that stand where a date belongs, such as "in the coming weeks",
  "soon" or "shortly". The phrase "as soon as" is ignored.
- **Banned words:** taken from the banned-word table in the house-style
  `writing-standard.md`, counting plurals, other tenses and similar variants. The script
  takes `--standard` when it is passed. If not, it climbs from its own folder, stopping at
  the project root (the nearest folder holding pods/ or .claude/), and, at each level, takes
  `.claude/skills/house-style/writing-standard.md` (an installed skill) before
  `pods/core/skills/house-style/writing-standard.md` (the repository copy). When the climb
  finds neither, or no project root is found, it reads `shared/writing-standard.md` in this
  folder. With no standard at all, the banned-word check is marked "skipped".
- **Em dashes:** counted by searching the raw bytes for `E2 80 94` without decoding. A tool
  that decodes UTF-8 with a legacy one-byte code page sees three unrelated characters there
  and reports zero by mistake.

`status` reads `pass` only if every check passes; the exit code is 0 for pass and 1 for
fail. The script covers mechanics only. Whether the copy uses the group's words, and
whether each fact has a source, is for the Step 6 review.

## Output

Hand back:

- the message core, with six answers, or seven when the "not changing" line applies;
- the framing table, filled in for each audience in scope;
- the **group vocabulary map**, giving the group's term, the project's term and the one the
  copy uses;
- the jargon list, pairing each technical term with the plain wording chosen;
- the check result for each draft;
- the open questions that stand between you and a clean draft.

For a complete worked run, compare `examples/source-change-notes.md` (the synthetic input)
with `examples/expected-message-core.md` (the output).

Treat the message core as binding. Everything written later agrees with it. When a fact
changes, update the core first, then correct each piece from the new core.

## Writing standard

The installed `house-style` skill governs every word this skill produces: subject lines,
email bodies, chat posts, documents, slide text and speaker notes, labels, image
descriptions, answers in an FAQ, manager talking points, file names and the report you send
back. An em dash counts as a
failed build; confirm its absence with the byte scan. Run the house-style checklist before
any handover. Work that breaks the standard is returned for another pass.
