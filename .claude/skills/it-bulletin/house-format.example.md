# IT Bulletin house format (ACME Co. example)

This file is the layout the `it-bulletin` skill fills in. It sets the subject pattern, the
ordered blocks and their labels, the sign-off, and a word-count target per bulletin type.
The skill fills this format and adds nothing to it: no extra block, no extra label, no
sign-off of its own.

**Replace it with your own.** Copy this file to `house-format.md` in the same folder and
edit it. The skill reads `house-format.md` first and falls back to this example. Keep the
`format` block below in step with the prose: the tests and the other comms skills read the
subject pattern and the block order from that block, not from the prose.

## Machine block

```format
subject: ^(?=.{24,72}$)\[IT Bulletin\] (Planned change|Service disruption|Reminder|Completed change): [A-Z0-9].*$
blocks: At a glance | Who is affected | What you need to do | What to expect | Get help
disruption_extra: Updates, after What you need to do, newest entry first
```

- `subject` is a Python regular expression the full subject line must match. It requires
  the `bulletin.subject_prefix` value from `comms-config` (here `[IT Bulletin]`), then the
  bulletin type, a colon, and a topic that starts with a capital letter or a digit. The
  lookahead caps the whole line at 72 characters so it fits a phone's message list.
- `blocks` lists every required block, in order. Each block is a `## <Label>` heading in
  the markdown draft.
- `disruption_extra` names the one block that only a service disruption carries.

## Subject line

`[IT Bulletin] <Type>: <Topic>`

- **Type** is one of the four types, written exactly as in the regex.
- **Topic** names the system or the thing people use, in their words, and what happens to
  it. A planned change and a reminder end on the date (month and day). A service
  disruption names the symptom. A completed change says what is now in place.
- Never an urgency word alone ("Urgent", "Action required", "Important"). The type label
  already tells the reader what kind of notice it is.

| Type | Example subject |
|---|---|
| Planned change | `[IT Bulletin] Planned change: Printers need your badge from March 4` |
| Service disruption | `[IT Bulletin] Service disruption: Shared drive is slow to open files` |
| Reminder | `[IT Bulletin] Reminder: Link your badge to the printers by March 1` |
| Completed change | `[IT Bulletin] Completed change: Shared printers now use your badge` |

## Blocks

The action comes before the explanation. Every type uses the same five blocks in the same
order; only what goes inside them changes.

| Block | Planned change | Service disruption | Reminder | Completed change |
|---|---|---|---|---|
| At a glance | What changes and the date it starts, in one or two sentences | The symptom and when it started | The action still due and its date | What is now different |
| Who is affected | The groups, in plain words, and who is not affected | Who sees the symptom | Who still has the action to do | Who sees the difference |
| What you need to do | Numbered steps, each starting with a verb and carrying a date | A workaround with a date, or "Nothing. Keep working as normal." | The outstanding step and its date | One recovery step if a reader may need it, or "Nothing. This is done for you." |
| What to expect | The change window, what will look different, what stays the same | The effect on work and who is working on it | What happens after the date | Anything still settling, and what stays the same |
| Get help | One help path | One help path | One help path | One help path |

**Service disruption only:** an `Updates` block sits right after `What you need to do`. Each
entry starts with the time it was posted, in the bulletin's time zone. The newest entry
goes at the top, and older entries stay below it unchanged.

Rules for the blocks:

1. **Who is affected** names the audience so a reader can tell in one line whether the
   bulletin is about them. If nobody outside a group is affected, say so.
2. **What you need to do** is never left out. Number each step, start it with a verb, and
   give it a calendar date. When there is nothing to do, write that in this block.
3. **Get help** gives exactly one path, as a descriptive link or a named queue. Never a raw
   address, never "click here", never a list of options.
4. Write times in one time zone and name it once, at the first time in the body. With
   `time_zone: local` in `comms-config`, write "local time".

## Sign-off

The last line of the bulletin is the `bulletin.signature_line` value from `comms-config`,
alone, after the `Get help` block. For ACME that is `ACME IT Service Desk`. No greeting
before it, no thanks, no closing pleasantry, no personal name.

## Word-count targets

Count the words from `At a glance` through `Get help`. The subject and the sign-off do not
count. Trim to the target before the readability check.

| Type | Target |
|---|---|
| Planned change | 150 to 250 words |
| Service disruption | 80 to 200 words, plus 40 words per update entry |
| Reminder | 60 to 120 words |
| Completed change | 60 to 150 words |

## Silent fixes

When you write `house-format.md`, apply these fixes silently and list each one in the
handoff note for whoever owns the format. The draft goes out with the fix in place; the
bulletin itself never mentions it.

Defects to look for and fix this way:

- a deadline written as a span of time ("within two weeks") instead of a date
- times with no time zone, or with more than one
- an action buried below the explanation
- more than one help path
- a raw web address or a "click here" link
- a subject that is only an urgency word
- an apology paragraph or a closing pleasantry
- an acronym used before it is spelled out

A missing audience, action, or help block is not a silent fix. If the format has no place
for who is affected, what to do and by when, or where to get help, stop and report the gap
to the requester before drafting.
