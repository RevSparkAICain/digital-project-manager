# comms-visual-assets

Builds the graphics that accompany an internal change notice: one-image summaries, step
flows, old-versus-new panels, timelines, printable one-pagers and cards, chat banners and
email headers. Each asset is a single HTML file styled only from the brand tokens, rendered
to PNG (or printed to PDF) with a headless Chromium-family browser, and delivered with alt
text.

## Inputs

- The settled message core, from the `plain-language-translation` skill or written by hand.
- Brand files: `brand/brand.json` and `brand/tokens.css` if the project has them, otherwise
  `shared/brand.json` and `shared/tokens.css`.
- `comms-config`: `pods/comms/comms-config.yaml` if present, otherwise
  `shared/comms-config.example.yaml`. It supplies the enabled channels, the intranet flag
  and the output folder.

## Outputs

- A PNG or PDF per asset, saved under `output_dir` as `<Topic>-<Asset>-YYYY-MM-DD.<ext>`.
- Alt text for each asset (see `examples/alt-text.md`).
- A short report: path, channel, dimensions, brand files used, anything not checked by eye.

## Rendering

From this folder:

```
python scripts/render_html.py examples/teams-banner.html --out banner.png --width 1200 --height 400
```

The browser is taken from `--chromium`, then the `CHROMIUM_PATH` environment variable, then
PATH, then the default Edge and Chrome locations on Windows. With no browser the script
exits with code 2 and says so. The output PNG has its text and time chunks removed.
The script uses the standard library only.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure the agent follows |
| `scripts/render_html.py` | Headless render to PNG, with metadata chunks removed |
| `examples/infographic.html` | A four-step guide for the ACME scanner update |
| `examples/teams-banner.html` | The matching chat banner |
| `examples/alt-text.md` | Alt text for both examples |
| `shared/` | Copies of the writing standard, the pod config, `brand.json` and `tokens.css` |
