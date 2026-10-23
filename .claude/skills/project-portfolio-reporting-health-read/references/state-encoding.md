# State encoding

A state encoding is the convention a team uses to record project state in the tracker: how a
project's color, a hold and completion are written down. This package treats the encoding as
configuration under `state_encoding` in the config. The example convention shipped in
`assets/health-read-config.example.json` is one option among many.

## The example convention

| Element | Config key | Example value | Where it lives |
|---|---|---|---|
| Color marker | `state_encoding.color_markers` | `{"green": ["[G]"], "amber": ["[A]"], "red": ["[R]"]}` | A token in the status task name: `[A] Weekly note` |
| Hold prefix | `state_encoding.hold_prefix` | `"PAUSED: "` | At the start of the name, after any color markers: `[A] PAUSED: Weekly note` |
| Completion marker | `state_encoding.completion_marker` | `"[DONE]"` | A token anywhere in the name: `[DONE] Weekly note` |
| Color field use | `state_encoding.color_field_used` | `false` | The tracker's own color field is not used |
| Colors that contradict a hold | `state_encoding.hold_contradicting_colors` | `["green"]` | A recorded hold reported as green is a conflict |

Config files stay ASCII. A team that marks color with emoji writes each marker with JSON
unicode escapes (a backslash, the letter u and the character's four hex digits), and the
grader matches the decoded character as a whole token.

## Parsing rules

1. Split the status task name on whitespace into tokens.
2. A token matches a color marker when it equals the marker as a whole token, ignoring case.
   `[g]` matches `[G]`; `[G]x` does not.
3. One color found: that color, source `name`. When two different colors are found there
   is no color, a method note is added, and check 3 reads not assessable.
4. No marker found: when `color_field_used` is true, the color field value is mapped through
   the color names (`green`, `amber`, `red`), source `field`. When false, the field is never
   read and never mentioned anywhere in the findings or the deck.
5. Set leading color and completion markers aside, then test the rest of the name for the
   hold prefix, ignoring case.
6. The completion marker matches as a whole token anywhere in the name.

## What each element feeds

- **Color marker:** the reported color for check 3, shown in the scorecard's Color column.
- **Hold prefix:** one of three hold signals for the scope rules (the others are a status in
  `hold_statuses` and a `hold` judgment saying the narrative records a hold).
- **Completion marker:** on a list filed as active, a `placement_finished_in_active` item
  under check 4. In the completed folder it means nothing extra.
- **Color field:** a second color source and, when both are set and differ, a
  `color_field_conflict` item, only when `color_field_used` is true. Otherwise never read.

## Describing another team's convention

A convention using only the tracker's color field, with holds recorded as a status:

```
"state_encoding": {
  "color_markers": {"green": ["Green"], "amber": ["Amber"], "red": ["Red"]},
  "hold_prefix": "",
  "completion_marker": "",
  "color_field_used": true,
  "hold_contradicting_colors": ["green"]
},
"hold_statuses": ["paused"]
```

No name carries a marker, so every color comes from the field. An empty hold prefix and
completion marker match nothing.

A convention putting the hold at the end of the name (`Weekly note (paused)`) cannot be
matched by a prefix. Record the hold through the status instead (`"hold_statuses":
["paused"]`), or through the `hold` judgment, which reads the narrative. Keep
`hold_prefix` empty so no name is misread.

## The encoding is never a finding

A hold prefix, a completion marker, a color marker, and every symptom of a correctly
recorded hold (unchanged text, past dates, unmoved tasks) are the convention working as
intended, and they are never reported as a finding.
