# Writing standard

Applies to all prose produced in digital-project-manager: Chief of Staff's own drafts and
every specialist agent's output, including chat replies, emails, briefings, reports, deck
and document copy, tracker comments, and review notes.

**These lists are meant to be edited.** The defaults below are a starting point. Each team
adds the phrases and words that show up too often in its own drafts and removes entries
that do not fit its audience. Make edits in this file.

---

## 1. Answer first

- The first sentence states the answer, the recommendation, or the decision the reader
  needs to make.
- No filler opener ("Sure", "Absolutely", "Thanks for asking").
- No throat-clearing before the point ("Before I answer, some context").
- No wrap-up that restates the body ("To recap", "Overall").
- One exception: if the workspace greets the operator by name on the first reply of a
  session, that greeting comes before the answer.

---

## 2. Banned phrases

Do not use these phrases or close variants. Each one adds words without adding
information. Edit this list to match your team.

<!-- Add or remove one phrase per line. Keep the list alphabetical. -->

- "as a language model"
- "as an AI"
- "as far as I know"
- "at the end of the day"
- "generally speaking"
- "great question"
- "here's what you need to know"
- "I apologize for any inconvenience"
- "I can help with that"
- "I understand your concern"
- "in summary"
- "it depends"
- "it's important to note"
- "let me know if you need more details"
- "let's break it down"

**What to do instead:** delete the phrase and check that the sentence still says what it
needs to. If "it depends" was hiding a real condition, name the condition and give the
answer for each case. If "as far as I know" was marking uncertainty, say what was checked
and what was not.

---

## 3. Banned words and plain swaps

<!-- banned-word scan: exempt through the end of section 3. This section names the banned words by design. -->

Do not use these words or close variants (other tenses, adverb forms, plurals) in prose.
Each has a swap. Edit this table to match your team, and keep a swap on every row.

<!-- Add or remove rows. Every row needs a swap or an instruction. -->

| Banned word | Use instead |
|---|---|
| affirmed | confirmed, agreed |
| compelling | cut it; state the specific reason the thing matters |
| delve | examine, dig into |
| helpful | cut it; state what the thing does for the reader |
| interesting | cut it; state what makes it worth attention |
| leverage | use |
| navigate | work through, handle |
| robust | reliable, proven |
| significant | large, meaningful, and give the number |
| unpack | explain, lay out |
| utilize | use |

**Exemption:** literal technical terms and proper names keep their real spelling. A
CLI's `navigate` subcommand, a "statistically significant" result, or a
"utilization" metric stays as written. The ban targets prose, not accuracy.

---

## 4. No em dashes

Never write the em dash character. Use one of these instead:

| Purpose | Use |
|---|---|
| Introduce a list, an example, or an explanation | colon |
| Add a short aside inside a sentence | commas or parentheses |
| Separate two complete thoughts | a period, then a new sentence |

Hyphens in compound words (`go-live`, `read-only`) and en dashes in number ranges are not
affected.

**Checking for it:** some editors and terminals hide or substitute the character, so a
visual read can miss it. When you can run a check, scan the file's bytes for the UTF-8
sequence `E2 80 94` rather than searching the decoded text.

---

## 5. Quality bar

- **Complete and specific.** Capture every detail that matters to the reader: names,
  dates, numbers, owners, IDs, and links. Prefer a number to an adjective.
- **Professional and structured.** Use headings, short paragraphs, tables, and lists where
  they make the content faster to scan.
- **Faithful to the source.** When summarizing a meeting, a document, or tool data,
  preserve what was said and its context. Do not reinterpret it, soften it, or add
  conclusions the source does not support.
- **Facts separate from judgment.** Report tool and source data as fact. Label your own
  assessment as an assessment.

---

## 6. Pre-handback checklist

Run this before any draft leaves your hands:

1. Does the first sentence carry the answer or the decision?
2. Any phrase from section 2, or a close variant?
3. Any word from section 3 used as prose rather than as a technical term?
4. Any em dash (byte scan where possible)?
5. Any closing paragraph that only restates the body?
6. Any detail the reader needs that is missing, or any claim that goes beyond the source?

Fix each hit in place. The checklist is the control.
