# Wording Checklist

The wording pass reads the deliverable as its intended reader would and asks one question
of every sentence: does this help that reader understand or decide something? Work the
sections in order. Record each finding with its location so the producer can act on it
without searching.

## 1. Fix or flag

The reviewer edits wording only where the change cannot alter meaning. Everything else is
a proposal for the operator to accept or decline.

| Auto-fix (write it to the file) | Flag (propose, do not apply) |
|---|---|
| An em dash replaced with a colon, comma, parentheses, or a period | Any rewrite that changes what a sentence claims |
| A banned word swapped for its listed plain equivalent, where the swap keeps the meaning | A banned word whose only fix needs the sentence rebuilt |
| A banned filler phrase deleted where the sentence stands without it | Tone shifts (more formal, less formal, softer, firmer) |
| Spelling and obvious typos | Cutting, adding, or reordering content |
| Doubled words, stray spaces, mismatched quote marks | Any number, date, name, or total |
| A term spelled two ways, normalized to the spelling used most | A term used in two senses, or two terms for one thing where the choice matters |

When unsure which column an edit belongs in, it belongs in the flag column.

## 2. Audience and altitude

- [ ] **Named reader.** State who the deliverable is for before judging it. An executive
      audience reads for decisions and exposure; a project team reads for tasks and dates;
      an all-staff notice reads for "what do I have to do and by when."
- [ ] **Right altitude.** Executive material carries outcomes, decisions, cost, and risk,
      not implementation detail. Team material carries the detail.
- [ ] **No unexplained jargon.** Every acronym is spelled out at first use unless the whole
      audience uses it daily. Product and internal system names get a short plain
      description the first time.
- [ ] **Consistent register.** The piece does not swing between casual and formal.

## 3. Lead with the answer

- [ ] **First lines carry the point.** The decision, recommendation, status, or request
      appears in the opening sentence or the slide title, not after the background.
- [ ] **Slide titles are statements.** "Two of five milestones are late" tells the reader
      something; "Milestone status" does not.
- [ ] **One message per slide or section.** If a title needs "and", consider whether it is
      two slides. Flag, do not split.
- [ ] **No throat-clearing opener and no wrap-up that repeats the body.**
- [ ] **The ask is explicit.** If the reader must act, the action, the owner, and the
      deadline are stated in one place, not scattered.

## 4. Specific over general

- [ ] **Quantify.** Replace "many", "a large number", "soon", "recently" with the count,
      the share, or the date, if the source has it. If it does not, flag the gap; never
      invent a figure.
- [ ] **Concrete subjects.** "The vendor will deliver the patch by 2030-03-15" beats "it is
      expected that the patch will be delivered."
- [ ] **Named owners.** Actions have a person or role attached.
- [ ] **Hedges earn their place.** "Might", "could", "potentially" stay only where the
      uncertainty is real and stated. Stacked hedges are flagged.

## 5. Clarity at the sentence level

- [ ] **Active voice by default.** Passive voice is acceptable when the actor is unknown or
      irrelevant; otherwise name who does what.
- [ ] **Sentence length.** Flag sentences over about 30 words; propose a split.
- [ ] **One idea per sentence.** Two claims joined by "and" or "while" often read better apart.
- [ ] **Parallel lists.** Bullet items in a list share a grammatical form (all start with a
      verb, or all are noun phrases).
- [ ] **Nominalizations unwound.** "Make a decision" becomes "decide"; "perform an
      assessment of" becomes "assess".
- [ ] **No ambiguous pronouns.** "It", "this", and "they" point at one clear thing.

## 6. Facts versus judgment

- [ ] **Data stated as data.** Figures pulled from a system, export, or record read as fact
      and name their source or as-of date where the reader needs it.
- [ ] **Judgment labeled as judgment.** Assessments, forecasts, and recommendations are
      marked as such ("Assessment:", "We recommend", "Our read is").
- [ ] **No fabricated detail.** Any figure, quote, name, or date the reviewer cannot trace
      to a source is flagged as unverified.
- [ ] **Context preserved.** Summaries do not reinterpret what a meeting, document, or
      person said.

## 7. House style

The banned word list, banned phrase list, and punctuation rules live in
`house-style/writing-standard.md`; `references/house-style.md` says how this pass applies
them. Read them from there at review time; do not keep a copy here, because two copies drift
apart.

- [ ] **No em dashes** (code point U+2014). Confirm with a byte scan for `E2 80 94`, not by eye.
- [ ] **No banned words**, except literal technical terms and proper names that keep their
      real spelling (a command name, a statistical term, a product name).
- [ ] **No banned phrases** or close variants.
- [ ] **Dates and numbers** follow one format throughout the piece.
- [ ] **Prepared-by line** names the operator who produced the deliverable.

## 8. Format-specific checks

**Email and announcements**
- [ ] Subject line states the topic and, where relevant, the action and deadline.
- [ ] The first two sentences answer "what is happening" and "what do I need to do".
- [ ] One clear call to action, with a link or contact for help.
- [ ] Signature block present and correct for the sender.

**Slides**
- [ ] Titles are statements (see section 3).
- [ ] Bullets are fragments of consistent form, not full paragraphs.
- [ ] Speaker notes, if present, agree with the slide.

**Documents and reports**
- [ ] Executive summary stands alone: a reader who stops there has the answer.
- [ ] Headings describe content, so the table of contents reads as an outline.

**Spreadsheets**
- [ ] Sheet names, column headers, and units are plain and unambiguous.
- [ ] Any notes or legend cells use the same terms as the headers.

## 9. Recording a flag

Every flag carries five fields so the operator can approve or decline it in one read:

| Field | Content |
|---|---|
| Location | Slide, page, sheet and cell, or paragraph |
| Current text | Quoted exactly |
| Proposed text | The replacement, written out in full |
| Reason | The checklist item it fails, in a few words |
| Severity | Blocker, Should-fix, or Polish |
