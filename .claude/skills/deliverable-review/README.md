# deliverable-review

The review procedure behind step 2 of every deliverable. It renders a finished deck, document
or spreadsheet, looks at the images, and checks the file through four passes: brand,
formatting and structure, wording, and consistency. Objective formatting and brand defects are
fixed in the file; wording, claims and numbers are flagged for approval. A separate gate
proves that a restyle changed no content.

## Inputs

- The deliverable: `.pptx`, `.docx`, `.xlsx` (or legacy `.ppt`, `.doc`, `.xls`), or the text
  of a written communication.
- The project's `brand/brand.json`, or `shared/brand.json` when the project has none (see
  "Where files come from" in `SKILL.md`), the only source of brand values.
- `references/formatting-checklist.md`, `references/wording-checklist.md` and
  `references/house-style.md`, read at review time.
- For a restyle: the original file and the restyled file.

## Outputs

- A review scorecard: overall verdict (Ship, Ship with fixes applied, or Hold for approval), a
  Pass, Fixed or Flagged result per pass with slide or page specifics, the auto-fixes applied,
  the flags with a proposed change each, and the slide mapping when a restyle renumbered
  slides.
- The corrected file, saved where the producer saved it.
- Render artifacts in a scratch folder: one PNG per slide for a deck, or a PDF plus one PNG
  per page for a document or spreadsheet, under a short `r<8hex>` stem.

## How to run

The `deliverable-reviewer` agent in this pod runs the skill end to end. To use the scripts by
hand, from the skill folder:

```
& "assets/render-deliverable.ps1" -In "<file>" -Out "<scratch-dir>" [-TimeoutSec 180] [-NoPng] [-Dpi 100]
python assets/verify-content-parity.py <original.pptx> <restyled.pptx> [--offset N] [--allow-added-slides] [--allow-added-shapes] [--strict-typography] [--json]
```

The render script exits 0 when the artifacts are on disk and non-zero otherwise (timeout,
nothing produced, page count mismatch, or an output path over the 260-character limit); any
non-zero exit leaves the deliverable unreviewed. The parity gate exits 0 when content is
unchanged, 1 when content changed and 2 when the comparison could not run.

## Prerequisites

See `docs/prerequisites.md` at the top of this folder. Rendering needs Windows with
Microsoft Office and Windows PowerShell, plus Python with PyMuPDF for page images. The parity
gate needs Python with `python-pptx` and `Pillow` and runs on any host.

## Files

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure, disposition policy and severity scale |
| `assets/render-deliverable.ps1` | Office render with a timeout and process guards |
| `assets/verify-content-parity.py` | Content-parity gate for restyles |
| `references/formatting-checklist.md` | Formatting and structure pass |
| `references/wording-checklist.md` | Wording pass |
| `references/house-style.md` | How the wording pass applies the banned words, phrases and punctuation rules in `house-style/writing-standard.md` |
