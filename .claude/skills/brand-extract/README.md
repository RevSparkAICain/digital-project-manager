# brand-extract

Learns a company's visual brand from the collateral it already has and writes a brand profile
that every deliverable skill in this repository renders in.

**In:** any mix of a website, a PowerPoint or Word template, a PDF brand guide or brochure, and
logo files.
**Out:** `brand.json`, `tokens.css`, starter `template.pptx` and `template.docx`, the logo, and
a generated `<slug>-brand` skill.

## How it works

Each input type has its own adapter (`scripts/sources/`) that turns the file into weighted
candidates: a color, a font with its role, a logo, or a layout measurement, each carrying the
evidence behind it. One pure function (`scripts/merge.py`) makes every decision by fixed
rules: source precedence, color clustering, role assignment, WCAG contrast checks and
defaults. Ties break by value, so input order never changes the result. Nothing is guessed by
a model; Claude writes only a short descriptive paragraph in the generated skill. Every value
in `brand.json` records where it came from, which is why the run needs no approval step.

Inputs are treated as untrusted: size caps on HTML, stylesheets, SVG and Office parts, an
http/https-only rule on the network with a 30 second limit per fetch, no further stylesheet
loaded once 60 seconds of stylesheet loading have passed for a page (a sheet already started
can still take its own 30 seconds), and no DTDs in Office XML. A stylesheet that cannot be read is
skipped and the rest of the page is still used. Font names keep only letters, digits, spaces
and `- . _ & +` (at most 64 characters), out-of-range layout numbers are clamped, and the
company name is escaped for each output. A source that fails in any way is logged and skipped.
Outputs are built in a staging folder first and moved into `--out` only after the whole build
succeeds, and the move is all or nothing: if a file cannot be replaced (a template open in
Word, for example), the previous output is restored. If a file cannot be put back either, the
run names it (`could not restore` for an earlier file, `could not remove` for a new one), keeps
any previous copies in `.brand-extract-backup-<suffix>` beside `--out` (or, if that move fails,
in the staging folder's `backup` folder, which the message names), and exits 1. An interrupt
during the move keeps them the same way.

Evidence is normalized per file, so several pages of one site can together outweigh a single
template. Links found inside fetched pages are not checked against private or loopback
addresses, and a remote SVG logo is copied unchanged: downstream skills should show it with
`<img>`, never inline it. With `--render`, relative links resolve against the URL as given,
not the browser's final URL after redirects.

Rules and constants: [references/scoring.md](references/scoring.md).

## Demo on fictional ACME Co.

```
python .claude/skills/brand-extract/examples/acme/make_fixtures.py --out demo
python .claude/skills/brand-extract/scripts/extract.py --name "ACME Co." --slug acme --out demo/brand \
    --file demo/acme-deck.pptx --file demo/acme-brand-sheet.pdf --file demo/acme-logo.png \
    --file .claude/skills/brand-extract/examples/acme/site/index.html \
    --file .claude/skills/brand-extract/examples/acme/site/about.html \
    --file .claude/skills/brand-extract/examples/acme/site/contact.html \
    --file .claude/skills/brand-extract/examples/acme/site/img/logo.svg
```

The expected profile is in `examples/acme/expected/`: Roadrunner Red `#C8102E` as primary,
Desert Sand `#F5EBDD` as background, Anvil Gray `#3A3F44` as text, Canyon Orange and Mesa Teal
as accents, Inter for headings and Source Serif 4 for body.

## Prerequisites

Python 3.11+, PyMuPDF, Pillow, python-pptx and python-docx, installed separately.
`agent-browser` only for `--render`.
