---
name: rollout-roadshow-deck
description: Make a short slide deck for a guest slot at another department's team meeting, where a presenter from IT explains a technology change in person to people who skip written notices. Use for requests like "a deck for the support team meeting", "I am presenting this change to a department", "roadshow deck", "slides for a guest slot", or any talk that goes with a rollout notice. Produces a JSON slide spec of 6 to 10 slides drawn from the message core behind the IT Bulletin, tailored to the audience in the room, with spoken notes on every slide and a list of questions to expect, then builds a .pptx from the spec with python-pptx.
---

# Rollout Roadshow Deck

A written notice is easy to skip. A short talk in a team's own meeting, with their own lead
sitting there, is harder to ignore. This skill plans that talk and builds the slides for it.
The slot belongs to someone else, so the deck has to earn its minutes.

Every claim on a slide comes from the message core that the `plain-language-translation`
skill produces, the same core the IT Bulletin uses. Any claim on a slide must also appear
in the bulletin; a slide that adds a new claim is wrong.

## Where each file comes from

For every file the skill reads, use this order:

1. the project's own file, if present:
   - `pods/comms/comms-config.yaml`
   - `brand/brand.json`
   - `brand/tokens.css`
   - the installed house-style skill (`.claude/skills/house-style/writing-standard.md`)
2. otherwise, this folder's shared/ copy:
   - `shared/comms-config.example.yaml`
   - `shared/brand.json`
   - `shared/tokens.css`
   - `shared/writing-standard.md`

Brand questions (colors, fonts, logo placement) go to the `brand-extract` skill when the
project has one. Otherwise the two brand files are the whole answer. Say in your report which
brand file you used, and say so when it still holds placeholder values.

## Defaults you can change

These numbers are starting points. If the project's config or the meeting host says
otherwise, follow them and note the change in your report.

| Setting | Default |
|---|---|
| Speaking time | 10 minutes of content, with the rest of the slot for questions |
| Slide count | 6 to 10, counting the title and the questions slide |
| Title size | 36 to 44 pt; `build_deck.py` sets 40 pt |
| Section label size | 20 to 24 pt |
| Body size | 14 to 16 pt; `build_deck.py` sets 16 pt |
| Typeface and colors | Whatever `brand.json` names; never typed by hand into a slide |

## Ground rules

- **Plan for less time than you were promised.** Guests get cut short. Put the action slide
  early enough to survive that.
- **Fewer slides, more spoken.** When the deck runs long, delete a slide before you shrink
  its text.
- **The room is not technical.** No architecture drawings, no vendor logo as the topic of a
  slide, no acronym without the plain words beside it.
- **Each title states the point.** "You approve sign-ins on your phone from June 3, 2030"
  tells the room something; "Sign-in overview" does not.
- **Mind the title length.** At 40 pt in the default layouts, a title-slide title holds up to
  64 characters on two lines. A bullets title may run to two lines, up to 64 characters,
  and stays on one line up to 32. Shorten any title over 64 characters, then check the render.
- **The slide holds the anchor; the notes hold the detail.** Write the notes as spoken
  sentences with a time against each slide, because the person presenting may not be the
  person who built the deck.
- **Save room for questions.** What people ask shows where the written copy fell short.

## Slide sequence

| # | Slide | Content | Note |
|---|---|---|---|
| 1 | Title | Name of the change, its start date, who is speaking | Use the title layout |
| 2 | The change | A single sentence beside a single picture | Take the before-and-after or step graphic from `comms-visual-assets` |
| 3 | Relevance to this group | What this audience gains, or what risk goes away, worded their way | Varies by audience. State plainly when nobody gains anything visible |
| 4 | How it looks | The on-screen difference: a new dialog, button or page | A genuine screenshot beats a verbal description |
| 5 | Your steps | Numbered actions, each with a due date | Most photographed slide, so design it to be legible in a phone picture |
| 6 | Dates | A dated strip with today flagged and the due date in the accent color | |
| 7 | Staying the same | Add only when it settles a genuine worry | Often calms the room more than the benefit slide |
| 8 | Getting help | A single named route, plus office hours if offered | |
| 9 | Questions | Starter prompts for discussion | Give this slide the longest stretch |
| 10 | Group extra | The one item that only this group needs | Keep it only when it earns its place |

When time is short, cut slides before reducing type size. Six slides that end on time beat
ten that overrun.

## Tailor to the audience

The facts never change. Slides 3, 4 and 10 are the ones that bend. Take the segments from
`pods/comms/audiences.yaml`, or from `pods/comms/audiences.example.yaml` when the team has
not written its own, and adapt this table to them.

| Segment | Slide 3 starts with | Slide 4 shows | Slide 10 candidate |
|---|---|---|---|
| General staff | A task they do daily | The new dialog or page | Using a shared device |
| Customer-facing and sales | Minutes saved and the effect on a customer | The phone or tablet view | A reply for a customer who asks |
| Customer Support | What the caller experiences | The case page | A case that is open during the switch |
| Operations | The queue step that is different | The work-order page | Switch-over day routines |
| Finance | Effect on close and approvals | The approval page | Timing around month-end |
| Business leaders | The result and what they must do | A readiness summary for their team | Warning signs inside a team |
| IT and Engineering | Support volume and open defects | Settings and configuration | Who to escalate to |
| Legal and Policy | Effect on a policy | Where the record is kept | Who signs off a policy change |

## Build

1. Write the slide plan first: slide number, title, what is on it, the spoken notes, the
   timing. Check it against the message core.
2. Put the plan into a JSON spec, using the schema below. `examples/deck-spec.json` is a
   finished one.
3. Build the deck with the script in this folder:

   ```
   python scripts/build_deck.py examples/deck-spec.json --out roadshow.pptx --author "<operator name>"
   ```

   Pass `--author "<operator name>"` with the name of the operator who produced the deck; it
   sets the author and last-modified-by properties, and the created and modified dates are
   the current time. `--deterministic` fixes the dates (and, without `--author`, the author)
   to the script's sample values; use it only for preview and test builds, never for a real
   deck. Add `--brand <path>` to point at a specific brand file. The script reads fonts and
   colors from `brand.json` and applies them to every slide. Use the slide template named in
   brand.json if one exists; when none is named, the deck starts from the python-pptx
   default and you say so in your report.
4. Reuse the pictures `comms-visual-assets` already drew. The timeline and the step flow
   should be the artwork the employee saw in the email, added to the deck by hand after the
   build, since the script places text only.
5. Put the anticipated-questions list at the end of the notes, with honest answers, the
   uncomfortable ones included. Take them from the leader cascade FAQ.

### Spec schema

```json
{"title": "<deck title>", "slides": [{"layout": "title|bullets", "title": "...", "subtitle": "...", "bullets": ["..."], "notes": "..."}]}
```

- `layout` is `title` or `bullets`.
- `subtitle` applies to `title` slides only.
- `bullets` is required for `bullets` slides, as a list of strings.
- `notes` is optional in the schema, but every slide in a real deck carries it.

A spec that breaks these rules fails with a message naming the slide.

## Finish

1. Export the deck to images and inspect every slide for overflow and weak contrast. Check
   that slide 5 stays legible when photographed from the rear row.
2. Save to the `output_dir` from `comms-config`, named
   `Roadshow-<topic>-<audience>-YYYY-MM-DD.pptx`.
3. Hand the deck to the review step before it goes to the presenter.
4. Report: the deck path, the audience it targets, the running time, a short summary of the
   notes, plus the questions likely to come up.

## After the session

Pass the questions people asked to `comms-copywriter`, who adds them to the FAQ. Pass the
attendance figure to `comms-strategist` for the measurement log. A talk whose feedback never
reaches the plan was a presentation, not part of the communication.

## Writing standard

The rules in the house-style writing standard apply to every word a person will read:
slide titles and bullets, speaker notes, file names and your own report. No em dashes, none
of the banned words, no stock filler phrases, answer first. Run the pre-handback checklist
in the writing standard (lookup order above) before handing anything over.
