---
name: comms-visual-assets
description: "Make the pictures that travel with an internal change notice for your organization: one-image summaries, step flows, old-versus-new panels, dated timelines, printable one-pagers and reference cards, chat banners and email header images. Use when readers should grasp a change in seconds instead of reading it, for example \"make an infographic\", \"we need a one-pager\", \"a graphic for the chat post\", \"a printable cheat sheet\", \"show before and after\". Builds self-contained HTML styled only from the brand token file, renders it to PNG or PDF with a headless Chromium-family browser, writes alt text for every asset, and hands the result to the review step."
---

# Communication Visual Assets

A picture in an internal notice has one task: let a reader understand the change in the
seconds before deciding whether to read on. It does not decorate the text and it does not
repeat the email.

Draw from the same message core as the written pieces (the `plain-language-translation`
skill produces it). A graphic that states something the written notice does not is a defect.

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

Real assets link the project's `brand/tokens.css`. The files under `examples/` link
`../shared/tokens.css` so they render from this folder alone. Say in your report which
brand files you used, and say so plainly when they still hold placeholder values.

## Brand

Colors, fonts and logo rules live in the brand files and nowhere else.

- Style every asset through `var(--brand-*)` custom properties. Type no hex value, color
  function or font name into an asset.
- Treat the primary color as an accent for headers, numbers and callouts. Keep large areas
  neutral.
- Follow the `logo` and `avoid` entries in `brand.json`. Keep shapes flat, corners
  lightly rounded, and skip gradients, shadows and glows.
- Put the organization name (`meta.organization` in `brand/brand.json`) and the internal-use line
  (`For internal use only.`) on printable pieces.

## Choose the asset

| Need | Asset | Size |
|---|---|---|
| The whole change on one picture | Infographic | 1600 px wide PNG, plus a Letter PDF for print |
| Old routine beside the new one | Old-versus-new panels | Inline SVG or HTML |
| Actions in order | Step flow, five steps at most | Inline, or a 1200 px PNG on its own |
| What comes next and when | Timeline band with the current day marked | 1600 x 500 PNG |
| A desk reference during the change | One-pager | Letter, portrait, one side |
| The steps and nothing else | Reference card | Half sheet or 4 x 6 in, printable |
| Draw the eye to a chat post | Banner | 1200 x 400 PNG |
| Give the bulletin an identity | Email header | 1200 x 300 PNG |

Check `channels` in `comms-config`: skip assets for a channel set to `enabled: false`. When
`intranet.present` is false, the one-pager must stand alone with no link to an internal
page.

## Layout patterns

| Pattern | Fits when | Build rules |
|---|---|---|
| Step flow | The reader acts in sequence | Numbered circles, a verb opens each label, a single duration, and the help path closes the piece |
| Old versus new | A familiar routine changes | Two equal panels with the same rows; label them Today and Starting on the date; differ by label and panel treatment, never by color alone |
| Timeline | The reader needs dates | Four to six markers; the action deadline is the biggest; a vertical rule shows today |
| Number blocks | Scale or measured results matter | Three or four sourced figures with plain labels, one sentence of context, nothing rounded up |
| Question card | Uncertainty is the real problem | Four to six questions in the reader's own words, one-line answers |
| One-pager | A desk reference is needed | What is changing, what you do, when, what looks different, common questions, one named help path, the internal-use line |

## Rules for clarity

- **One message per graphic.** If it needs a paragraph to explain, split it in two.
- **Short copy.** An infographic carries a headline, five to seven labeled parts and one
  footer line with the help path, in fewer than 40 words of body text.
- **Works without color.** Test in grayscale. Pair every color cue with a label, an icon
  or a position.
- **Real values only.** Dates, numbers and names on the artwork are the confirmed ones. No
  placeholder text ships.
- **One icon style.** Stroke icons at one weight, each with a label.
- **Readable at delivery size.** Body text of 16 px or more and labels of 24 px or more,
  checked on the rendered image at final scale.
- **Alt text for every asset.** Write one or two sentences that carry the message and the
  action. `examples/alt-text.md` shows the pattern.
- **The action and the help path also appear as text** in whatever channel carries the
  image. An image alone is not accessible.

## Render

1. Build one self-contained HTML file with the CSS inline apart from the token link.
   Keep working files out of the deliverables folder.
2. Render a PNG with the bundled script:

   ```
   python scripts/render_html.py examples/infographic.html --out infographic.png --width 1600 --height 1100
   ```

   The script finds a Chromium-family browser from `--chromium`, then `CHROMIUM_PATH`, then
   PATH, then the default Edge and Chrome locations on Windows. It exits 2 when none is
   found. It rewrites the PNG without text and time chunks so no tool or path metadata
   remains.
3. For a print piece, declare the paper in the HTML with `@page { size: Letter; margin: 12mm; }`
   and print to PDF using the same browser's `--print-to-pdf` option.
4. Open the rendered file and look at it. Overflow, clipped edges and font fallback show
   only in the render. An asset nobody has looked at is not finished.
5. Save final files to `output_dir` from `comms-config`, named
   `<Topic>-<Asset>-YYYY-MM-DD.<ext>`.
6. Hand the files to the review step before they go to the requester.

## Checklist before handover

- Every asset has alt text that states its message.
- Grayscale test passed.
- Text contrast checked on the rendered image.
- Nothing depends on color alone.
- Action and help path also present as plain text.
- Every claim matches the message core.

## Output

For each asset: the file path, the channel and placement, the alt text, the dimensions,
the brand files used, and anything you could not check by eye.

## Writing standard

The rules in the writing standard apply to every word on the artwork and in the alt text:
no em dashes, none of the listed banned words or phrases, the answer first. Run the check
described there before handing anything over. Literal technical terms keep their real
spelling.
