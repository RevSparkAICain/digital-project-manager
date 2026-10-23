# Scoring rules

Every decision brand-extract makes, in the order `scripts/merge.py` makes it. The constants
named here are defined at the top of `merge.py`; change both together. Every ordering is
deterministic: ties break by value, so input order never changes the profile.

## 1. Collect

Each `--file` goes to the adapter for its extension; each `--url` goes to the website adapter.
An unknown type, an unreadable file, a failed fetch or any unexpected error inside an adapter
is logged as `skipped <name>: <reason>` and the run continues. A URL is named without its
userinfo, query or fragment (`fetch.public_label`) in the log and in the generated skill.
Every logged reason (skip lines, stylesheet notes, `logo not copied` and the build failure
line) also has the query and fragment cut from each URL-like token (`extract.scrub_urls`: in
text between whitespace and quotes that holds a `/` or `%2F`, everything from the first `?`,
`#`, `%3F` or `%23` after it), and two errors that quote the URL in other forms get a fixed
reason instead: an invalid URL (`URL contains spaces or control characters, or a non-numeric
port`) and an agent-browser timeout (`timed out after 60 s`). A URL with userinfo is refused
before any fetch, and the refusal does not quote it. Within a page, a
stylesheet that cannot be read is logged as `<page>: skipped stylesheet <name>: <reason>` and
the page is still used. The run fails only when no source yields anything. Outputs are built
in a staging folder first and moved into `--out` only after the whole build succeeds; on a
build failure nothing is written. The move is all or nothing: every file it will replace, and
every stale logo, is first backed up inside the staging folder, and if any step fails the new
files are removed and the backups restored (`failed: <reason>; previous output restored`). If
a file cannot be put back (another program holds it open), the run exits 1 with
`failed: <reason>`, then `; could not restore <names>` (earlier files that did not go back),
`; could not remove <names>` (new files with no earlier version that stayed) and
`; previous copies kept in <folder>` (only while the backup still holds a file). The folder is
`.brand-extract-backup-<suffix>` beside `--out`, or the staging folder's `backup` folder if
that move fails. Whether the backup is kept depends only on whether it still holds a file, so
an interrupt during the move keeps it too.

| Adapter | Reads | Evidence per candidate |
|---|---|---|
| Template (`.pptx`, `.potx`, `.docx`, `.dotx`) | Theme color slots, theme major and minor fonts, slide size, master title position, footer placeholder, page margin | Slot weight: accent1 3, accent2 2, accent3 1.5, accent4 to accent6 1, dk1 2, lt1 2, dk2 1, lt2 1, hlink 0.5 |
| PDF | Filled shapes, text colors, embedded font names | Area in square points. Text at 1.3 times the page's median size or more votes for the heading font. Standard-14 fonts (Helvetica, Times, Courier, Symbol, ZapfDingbats) are ignored |
| Website (URL, `.html` or `.htm`) | `<style>` blocks, linked stylesheets, inline styles, `var()` values, `<img>` tags marked as logos, icon links | 1 per declaration, 3 when the selector includes `body`, `html`, `h1` to `h3`, `a`, `button`, `header`, `nav` or `.btn` |
| Image (`.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`) | SVG paint colors; raster colors quantized to 8 | SVG: uses per color. Raster: opaque pixel count |

Untrusted input limits, enforced in the adapters and `fetch.py`:

- Website: HTML read to 2,000,000 characters and scanned linearly; each stylesheet to
  1,000,000 characters; at most 20 linked stylesheets per page, and no further sheet is loaded
  once 60 seconds of stylesheet loading have passed for that page (`web.STYLESHEET_BUDGET_S`);
  `var()` values to 4,096 characters. Relative links resolve against the page's final URL
  after redirects, or against its `<base href>` when that is http or https; a local file
  ignores `<base>`. With `--render`, they resolve against the URL as given, not the browser's
  final URL after redirects (a known limitation).
- Network: http and https only, redirects re-checked, URLs with credentials refused, no
  cookies, 5 MB per response, 10 second timeout per operation and 30 seconds per fetch (the
  page, each stylesheet, a remote logo). The 30 seconds cover connect, redirects, headers and
  body: the request runs in a worker thread that is abandoned when the deadline passes.
- Links found inside fetched pages are not checked against private or loopback addresses.
- A remote SVG logo is copied unchanged; downstream skills should show it with `<img>`, never
  inline its markup.
- `--render` on Windows launches agent-browser's bundled executable directly; when only a
  `.cmd` or `.bat` launcher exists, a URL with whitespace, a backtick or any of
  `& | < > ^ % " ( ) !` is refused.
- Office: XML parts must be UTF-8 with no DTD; each part at most 20 MB.
- SVG: read to 5,000,000 characters.
- Logo candidates must have an image extension (`.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`,
  `.webp`, `.bmp`, `.ico`). A local link must resolve inside the page's own folder; a remote
  one must be http or https.
- Font names keep only letters, digits, spaces and `- . _ & +`, collapsed and capped at 64
  characters, cut at the last space under the cap when there is one (`fonts.clean_family`). The company name has XML-invalid control characters removed and
  whitespace collapsed (`emit_tokens._xml_text`), then is escaped per output: `*/` is
  neutralized in the `tokens.css` comment, and in the generated skill comment markers are
  stripped and the description is JSON-quoted.

## 2. Weight

Within one source, color weights are scaled to sum to 1 and font weights likewise, so a long
stylesheet cannot outvote a short template. Each weight is then multiplied by source
precedence: template 1.0, PDF 0.8, website 0.6, image 0.4. The same value from several sources
adds up; contributions are summed in a fixed order with `math.fsum`, so input order cannot
flip a near-tie. The single heaviest contribution supplies that value's provenance.

Normalization is per file, so each file carries a full share. Several pages of one site
therefore add up and can outweigh a single template; pass one page per site when the template
should lead.

## 3. Cluster colors

Colors are taken heaviest first, ties by hex value. A color within CIE76 Delta E 3 of a
heavier color folds into it and adds its weight (`DELTA_E_CLUSTER`).

## 4. Assign color roles

- **Neutral** means CIE Lab chroma below 12 (`color.NEUTRAL_CHROMA`).
- **background:** the heaviest neutral with relative luminance 0.7 or more
  (`LIGHT_LUMINANCE`); failing that, the lightest neutral at 0.5 or more (`MID_LUMINANCE`);
  failing that, `#FFFFFF` with a warning.
- **text:** chosen after the background, from the remaining neutrals: the heaviest with
  luminance below 0.18 (`DARK_LUMINANCE`); failing that, the darkest below 0.5; failing that,
  `#222222` with a warning.
- **primary:** the heaviest non-neutral; failing that, `#1F6FEB` with a warning.
- **accent1 to accent3:** the next non-neutrals whose hue is at least 30 degrees
  (`ACCENT_HUE_GAP`) from every color already chosen. Unfilled accents stay empty, without a
  warning.
- **textMuted:** text mixed 25 percent toward background. **surface:** background mixed 5
  percent toward text. **divider:** background mixed 15 percent toward text. **link:** primary.
- **chart:** primary, then the accents, then tints of primary (30, 45, 60, 75 and 90 percent
  toward white) until there are six (`CHART_LEN`, `CHART_TINTS`).

## 5. Check contrast

Three pairs must reach WCAG 4.5:1 (`CONTRAST_TARGET`): text on background, white on primary,
and muted text on background. Text is checked first, so the muted color derives from the final
text color. A failing color moves its lightness away from the other color in 1 percent steps,
keeping hue and saturation; if 100 steps do not reach the target it becomes black or white.
The change is appended to that value's provenance evidence and to `adjustments`.

## 6. Fonts

The heaviest family voting `body` becomes the body font; the heaviest voting `heading` becomes
the heading font. A missing heading borrows the body font, and a missing body borrows the
heading font. With neither, both become Arial with `WARNING: body font defaulted`.

## 7. Logo

Any SVG candidate beats any raster one. Otherwise the heaviest candidate wins: a raster file
weighs its pixel area times 0.4; a web `<img>` logo weighs 1.0 and an icon link 0.5, times 0.6. The file is copied unchanged as `logo.<ext>`, and only when its
extension is in the image allowlist and it is at most 5 MB.

## 8. Layout

Each key takes its heaviest candidate (ties by value, then source); with none, the default
applies and provenance says `"source": "default"`.

| Key | From | Default |
|---|---|---|
| `slideWidthIn`, `slideHeightIn` | PPTX slide size | 13.333, 7.5 |
| `titleTopIn` | PPTX master title position | 0.5 |
| `footer` | PPTX footer placeholder or DOCX footer part | true |
| `pageMarginIn` | DOCX left margin | 1.0 |
| `baseFontPx` | First `html` or `body` font-size | 16 |
| `headingScale` | First `h1` font-size divided by the base | 2.0 |

A candidate that is not a finite number is dropped (the next one, or the default, applies) and
the drop is listed in `adjustments`. The chosen value is then clamped (`merge.LAYOUT_RANGES`):
`baseFontPx` 8 to 72, `headingScale` 1 to 6, `pageMarginIn` 0 to 4, `slideWidthIn` and
`slideHeightIn` 1 to 56, `titleTopIn` 0 to the chosen slide height. A clamp is appended to that
value's provenance evidence and to `adjustments`. `brand.json` is written as strict JSON.

The starter templates apply the slide size and page margin. The other keys are recorded so
reviewers can check deliverables against them.

## Warnings

A required role filled by a default prints `WARNING: <role> defaulted` and is listed in
`brand.json` `warnings` and in the generated skill's "Defaulted values" section. Required roles
are the primary, text and background colors and the body font.

## Generated skill

The blurb between `<!-- blurb:start -->` and `<!-- blurb:end -->` is at most 800 characters
with no HTML comment markers; a leading markdown character is escaped, and the `description`
line is JSON-quoted. `--blurb-file` checks these limits before anything is written.
