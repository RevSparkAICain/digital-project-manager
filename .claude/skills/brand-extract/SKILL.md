---
name: brand-extract
description: Learn a company's visual brand from collateral it already has (a website URL, a PowerPoint or Word template, a PDF brand guide or brochure, or logo files) and write the brand profile every deliverable skill renders in, which is brand.json, tokens.css, starter .pptx and .docx templates, and a generated `<slug>-brand` skill. Use when someone asks to learn, extract or match a brand from a site or files, or when brand/brand.json still holds the neutral placeholder values.
---

# Brand extract

Point it at collateral and get a brand profile. The run is fully automatic, with no approval
step: every value in `brand.json` records the source and evidence it came from, and a value
the sources do not supply falls back to a default and prints `WARNING: <role> defaulted`.

Use it only on brands you are authorized to work with.

## Run

1. **Collect inputs.** Any mix of a website URL, a `.pptx`, `.potx`, `.docx` or `.dotx`
   template, a PDF brand guide or brochure, saved `.html` or `.htm` pages, and logo files
   (`.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`). A template gives the strongest signal.
2. **Run the extractor** from this skill's folder:

   ```
   python scripts/extract.py --name "<Company>" --slug <short-name> --out <WORKSPACE_ROOT>/brand \
       --file <template.pptx> --file <brand-guide.pdf> --file <logo.svg> --url https://<site>/
   ```

   Add `--render` when the site builds its pages with scripts; the page is then loaded
   through `agent-browser`.
3. **Read the console output.** It lists skipped sources with the reason, any contrast
   adjustments, and any `WARNING:` lines. A warning means a default stands in for a brand
   value: tell the operator which one.
4. **Write the blurb.** Open `<out>/<slug>-brand/SKILL.md` and replace the paragraph between
   `<!-- blurb:start -->` and `<!-- blurb:end -->` with two or three sentences on how the brand
   looks, using only what the profile shows. The checked path is to put the paragraph in a text
   file and pass `--blurb-file` on the run: it must be 800 characters or fewer, with no HTML
   comment markers, and a leading markdown character is escaped. A hand edit follows the same
   limits. Change nothing else in the file. This paragraph is the only text you write; every
   other value comes from the scripts.
5. **Review.** Send `template.pptx` and `template.docx` through the `deliverable-review` skill.
6. **Hand off.** `brand.json` and `tokens.css` in `brand/` take effect for every skill at once.
   To use the generated `<slug>-brand` skill as well, copy its folder into `.claude/skills/`
   after the PM approves the review.

## How values are chosen

| Step | Rule |
|---|---|
| Weight | Each source's color and font evidence is scaled to sum to 1, then multiplied by precedence: template 1.0, PDF 0.8, website 0.6, image 0.4 |
| Cluster | Colors closer than Delta E 3 merge into the heavier one |
| Roles | Background is the heaviest light neutral (else the lightest neutral at luminance 0.5 or more), text the heaviest dark neutral (else the darkest below 0.5), primary the heaviest non-neutral, and accents the next hues at least 30 degrees apart |
| Contrast | Text on background, muted text on background and white on primary must reach 4.5:1. A failing color is darkened or lightened along its own hue and the change is recorded |
| Fonts | The theme major font, CSS on `h1` to `h6`, and large PDF text vote for headings; the rest vote for body |
| Logo | Any SVG wins; otherwise the heaviest candidate (a raster file weighs its pixel area times 0.4; a web `<img>` logo weighs 1.0 and an icon link 0.5, times 0.6). It is copied as is, never traced or edited |

Ties break by value, so the order of the inputs never changes the profile.
`references/scoring.md` spells out every rule and constant.

## Outputs (in `--out`)

| File | Contents |
|---|---|
| `brand.json` | The shared brand schema plus `chart`, `layout`, `provenance`, `adjustments`, `warnings` |
| `tokens.css` | The same values as CSS custom properties |
| `template.pptx`, `template.docx` | Starter files with the brand theme colors, fonts, slide size and margins |
| `logo.<ext>` | The chosen logo, unchanged |
| `<slug>-brand/SKILL.md` | The generated brand skill |

Outputs are built in a staging folder next to `--out` first and moved into `--out` only after
the whole build succeeds. On a build failure nothing is written and the exit code is 1. The
move is all or nothing: files about to be replaced are backed up first, and if any file cannot
be replaced (a template open in Word, for example) the run prints
`failed: <reason>; previous output restored`, puts the earlier output back and exits 1. If a
file cannot be put back either, it prints `failed: <reason>` followed by
`; could not restore <names>` for earlier files that did not go back, `; could not remove
<names>` for new files (with no earlier version) that stayed in `--out`, and
`; previous copies kept in <folder>` when earlier copies are left over, and exits 1. That
folder is `.brand-extract-backup-<suffix>` next to `--out`, or, if it could not be moved
there, the `backup` folder inside the `.brand-extract-<suffix>` staging folder next to
`--out`; the message names whichever it is. Copy the files back by hand once the other
program lets go. If the run is interrupted (Ctrl+C) during the move, any earlier copies not
yet put back are kept the same way and the folder is printed.

## Prerequisites

Python 3.11 or later, plus, installed separately: PyMuPDF for PDF input, Pillow for raster
images, and python-pptx and python-docx for the templates (without them the templates are
skipped with a warning). `agent-browser` is needed only for `--render`.

## Limits

- Visual tokens and layout only: no voice and tone.
- Reads each given page and its linked stylesheets; it does not crawl a site or follow
  `@import`. A stylesheet that cannot be read is skipped with a logged note and the page is
  still used. Relative links resolve against the page's final URL after redirects, or against
  its `<base href>` when that is http or https. With `--render`, they resolve against the URL
  as given instead, not the browser's final URL after redirects, so a page that redirects to
  another path or host can point its stylesheets and logo at the wrong place.
- Evidence is normalized per file, so several pages of one site can together outweigh a
  single template. Pass one page per site when the template should lead.
- PDF standard-14 fonts (Helvetica, Times, Courier, Symbol, ZapfDingbats) are ignored because
  they mean no brand face was embedded.
- Network: http and https only, redirects re-checked, URLs with credentials refused, no
  cookies, 5 MB cap per response, 10 second timeout per operation and 30 seconds per fetch
  covering connect, redirects, headers and body (the page, each stylesheet, a remote logo).
  No further stylesheet is loaded once 60 seconds of stylesheet loading have passed for a
  page; a sheet already started can still take up to its own 30 second fetch limit.
- Links found inside fetched pages (stylesheets, logos) are not checked against private or
  loopback addresses. Run it only on sites you trust to that extent.
- A remote SVG logo is copied unchanged. Downstream skills should show it with `<img>`, never
  inline its markup.
- On Windows, `--render` launches agent-browser's bundled executable directly. When only a
  `.cmd` or `.bat` launcher exists, a URL containing whitespace, a backtick or any of
  `& | < > ^ % " ( ) !` is refused, because cmd.exe would run part of it as a command.
- Untrusted input is capped: HTML at 2,000,000 characters, each stylesheet at 1,000,000, at
  most 20 linked stylesheets per page, SVG at 5,000,000 characters. Office XML parts must be
  UTF-8 with no DTD and at most 20 MB each.
- Logo candidates need an image extension (`.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`,
  `.bmp`, `.ico`). A local link must stay inside the page's own folder; a remote one must be
  http or https.
- Font names keep only letters, digits, spaces and `- . _ & +`, at most 64 characters (cut at
  a word boundary). Layout numbers that are not finite fall back to the default, and the rest
  are clamped (base font 8 to 72 px, heading scale 1 to 6, page margin 0 to 4 in, slide size 1
  to 56 in, title top 0 to the slide height) with the change listed in `adjustments`. The company
  name has XML-invalid control characters removed and whitespace collapsed, then is escaped per
  output: `*/` is neutralized in the `tokens.css` comment, and in the generated skill comment
  markers are stripped and the description is JSON-quoted.
