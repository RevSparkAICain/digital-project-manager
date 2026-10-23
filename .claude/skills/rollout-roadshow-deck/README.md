# rollout-roadshow-deck

Plans and builds a short guest-speaker deck for presenting a technology change at another
department's team meeting. The deck follows a fixed slide sequence, shifts three slides to
suit the audience, carries spoken notes on every slide, and ends with the questions to
expect. A script turns a JSON slide spec into a .pptx in the brand's fonts and colors.

## Inputs

- A message core, from the `plain-language-translation` skill.
- An audience segment from `pods/comms/audiences.yaml`, or `pods/comms/audiences.example.yaml`
  when the team has not written its own. The tailoring table in `SKILL.md` maps to those
  segments.
- A brand file: `brand/brand.json` if the project has one, otherwise `shared/brand.json`.
- A slide spec in JSON. See `examples/deck-spec.json`.

## Outputs

- A `.pptx` deck of 6 to 10 slides with speaker notes.
- A report naming the audience, the running time and the questions to expect.

## Building a deck

From this folder:

```
python scripts/build_deck.py examples/deck-spec.json --out roadshow.pptx --author "<operator name>"
```

Options:

- `--author "<operator name>"` sets the author and last-modified-by properties to the
  operator who produced the deck (default: empty). Created and modified are the current time.
- `--deterministic` fixes the dates (and, without `--author`, the author) to sample values so
  preview and test builds repeat byte for byte. Never use it for a real deck.
- `--brand <path>` uses that brand file.
- The `BRAND_JSON` environment variable does the same when `--brand` is absent.
- Without either, the script walks up from its own folder to the nearest `brand/brand.json`,
  stopping at the project root (the nearest folder holding pods/ or .claude/), then falls
  back to `shared/brand.json`.

The script needs python-pptx (`pip install python-pptx`). Reading the spec and finding the
brand file need only the standard library. When `brand.json` names a slide template under
`templates.pptx`, the deck starts from it; otherwise it starts from the python-pptx default.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure the agent follows |
| `scripts/build_deck.py` | Brand lookup, spec validation and the deck build |
| `examples/deck-spec.json` | A finished 9-slide spec for a parts-ordering portal change |
| `shared/` | Copies of the writing standard, the pod config, and the brand files |
