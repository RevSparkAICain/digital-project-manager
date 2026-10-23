---
name: deliverable-review
description: "Quality gate that runs after a deliverable is built and before its reader sees it. Use for any finished deck (.pptx), Word file (.docx), workbook (.xlsx) or substantial written message, and whenever someone asks for a QA pass on a file that already exists. Renders the file to images, looks at them, then checks brand, formatting and structure, wording, and internal consistency. Fixes objective layout and brand defects in place, flags anything touching meaning for approval, and returns a scorecard with a Ship, Ship with fixes applied, or Hold for approval outcome. Also the required first step for a restyle (same content, new look), where a parity script must prove no content changed. Skip only for throwaway drafts and one-line answers with no layout."
---

# Deliverable review

This is step two of every deliverable: the gate between a finished artifact (deck, Word file,
workbook, written message) and whoever reads it, whether that is the operator or an outsider.
The method is to produce images of the file, look at them, and then judge the result through
four lenses: brand, formatting and structure, wording, and internal consistency.

Approval follows sight. Automated probes (shape coordinates, hex codes, keyword searches) are
blind to crowding, collisions, faint contrast and tables nobody can read. Look at the pages.

## When to run it

- By default, as soon as a producer has built a deck, Word file, workbook or substantial
  message.
- On request, to QA a file that already exists.
- Always for a restyle request (keep the content, change the look). In that mode the
  content-parity gate is mandatory and runs before any visual lens. A restyle is judged by
  its words first: if any changed it failed, however it looks.
- Skippable only for throwaway drafts and one-line answers that carry no layout.

## Inputs and where they come from

| Input | Source |
|---|---|
| Brand values | `brand/brand.json`, or `shared/brand.json` when the project has none. The single authority for palette, faces, link color, the avoid-list and any logo or template rule |
| Formatting checklist | `references/formatting-checklist.md` |
| Wording checklist | `references/wording-checklist.md` |
| House style | The rules in `house-style/writing-standard.md`, applied through `references/house-style.md` (forbidden words and phrases, punctuation) |
| Render script | `assets/render-deliverable.ps1`, which drives Office through COM with a time limit and guards on Office processes |
| Parity gate | `assets/verify-content-parity.py`, which shows that a restyle kept every piece of content |

The `brand-extract` skill produces `brand/brand.json`. The copy that ships here is a neutral
stand-in, marked `meta.placeholder: true`. Take brand values from the brand file and from no
other place: not memory, not an earlier deliverable, not a stray template.

### Where files come from

Two files are looked up in a fixed order, the brand file and the writing standard.

1. First choice: the project's own file, if present. That means `brand/brand.json` and
   `.claude/skills/house-style/writing-standard.md` (from the installed `house-style` skill).
2. Fallback: otherwise, this folder's shared/ copy, which means `shared/brand.json` and
   `shared/writing-standard.md`.

The `shared/` pair are copies of the canonical files, kept identical to them, and they count only when the project has no file of its own. The scorecard names the
brand file that was actually used. No script in this skill reads brand data, so there is no
project-root search; the reviewer opens the files directly.

## Platform note

Rendering in this version is Windows only. It automates Word, PowerPoint and Excel through
Office COM, so Office on Windows is required. PNG pages for Word files and workbooks also need
Python with PyMuPDF (`fitz`). The parity gate is portable but needs Python with `python-pptx`
and Pillow; if either is missing it exits `2`. A host that cannot render leaves the
deliverable UNREVIEWED.

## Disposition policy

This policy is fixed. Every finding lands on one side of it.

- **Fix directly (auto-fix)** when the fault is objective layout or brand: overflow past the
  page or slide edge, colors outside the palette, links left in Office's default blue,
  mismatched footers or page numbers, wrong type sizes, misaligned elements, em dashes, and
  forbidden words or phrases that have a swap preserving the sense.
- **Propose only (flag for approval)** when meaning is involved: reworded text, claims, tone,
  restructuring, content added or removed, and any figure that looks wrong. Never touch a
  number. Never reword meaning quietly. Each flag states the exact change proposed.
- A layout fix that would shift meaning, or the designer's intent, becomes a flag instead.

## Restyle mode: the content-parity gate

Use it for any job shaped like "same content, new look": a rebrand, a restyle, applying the
house template, converting an outside deck into the house brand. Only the script proves
parity; comparing decks by eye proves nothing, and the producer's word proves less.

```
python assets/verify-content-parity.py <original.pptx> <restyled.pptx> [--offset N] [--allow-added-slides] [--allow-added-shapes] [--strict-typography] [--json]
```

| Flag | Effect |
|---|---|
| `--offset N` | Pairs original slide N with restyled slide N plus the offset. Omit it for automatic shift search |
| `--allow-added-slides` | Extra slides in the restyle are acceptable (a front cover, a back appendix, a closing slide) |
| `--allow-added-shapes` | Extra decoration such as a logo or wordmark is acceptable; added icons fall under the same switch |
| `--strict-typography` | Typography warnings (tier 2) become failures |
| `--json` | Adds a machine-readable summary with the keys `parity`, `findings`, `typography_warnings` and `allowed` |

Two conditions fail whatever flags are set: fewer slides in the restyle than in the original,
and a change of slide size. Extra slides fail unless `--allow-added-slides` is given.

| Exit | Meaning |
|---|---|
| `0` | Parity held |
| `1` | Content differs; the restyle may not ship |
| `2` | The check could not run; this is also a non-pass |

**Tier 1, content (any mismatch fails):**

- every run of text, verbatim, including grouped shapes at any nesting depth;
- speaker notes, and text inside table cells;
- which shapes exist, where they sit, their dimensions and rotation (group members too), and
  their stacking order;
- link targets;
- icon artwork, meaningful pictures and filled picture placeholders.

**Outside the gate's reach** (check these in the render): chart series data and labels,
SmartArt text, embedded objects, and picture fills on plain shapes.

**Tier 2, typography (warning only):** alignment, size, indent level, bold, underline and
italic. Type may legitimately change in a rebrand, so a person signs off on each warning.
Treat an unexplained size drop as suspect: shrinking text is the easiest way to hide an
overflow.

**Allowed silently, because they are the restyle:** theme, effects, background, typeface, and
the color of fills, outlines and text.

Two mechanics explain why the gate can be trusted:

- Icons are compared on their alpha channel: a recolor keeps the outline and passes, a
  different glyph changes it and fails. Byte comparison would alarm on every recolor until
  people stopped looking; no comparison would let a swapped symbol through.
- Before diffing, inherited formatting is resolved to explicit values. A routine PowerPoint
  save writes inherited alignment out as `LEFT` and `bold=None` as `bold=False`; nothing
  changed on screen, and unresolved those writes would bury real findings.

### Report the mapping, not only the result

- When the restyle adds a cover, every original slide moves up one number; put that offset in
  the scorecard so everyone means the same slide.
- The gate pairs slides with one fixed shift. With no `--offset`, it tries every shift from 0
  up to the difference in slide counts, scores each by how many slides have exactly equal text,
  and takes the best; ties go to the full difference (extras at the front). Extras at the
  start, the end or both therefore pair correctly. The output line labelled `mapping` shows
  the shift and whether it came from `auto` or from `--offset`.
- A slide inserted in the middle defeats a single shift. Either pass `--offset` for the stretch
  you care about, accepting that later slides will read as changed, or run the stretches
  separately.

### Re-check at every hand-off

- Files get edited in Office between turns, so an earlier pass is no evidence about the file
  now. Rerun the gate immediately before reporting and compare the original's modified time
  with the earlier run; if it changed, rebuild from it rather than patch.
- If the gate fails, restore the original's content and rerun, extracting strings with a
  script instead of retyping. New wording stays only when the operator confirms making that
  edit on purpose.

## The review passes

1. **Frame.** Record the kind of deliverable and who reads it (executives, a steering group,
   the project team, the whole company, an outside party). That reader sets the altitude and
   the formality. Note any template or brand to match.

2. **Render, so the file can be seen.** Use `assets/render-deliverable.ps1`; it runs Office
   through COM, guarded and bounded by a timeout. Legacy `.ppt`, `.doc` and `.xls` files take
   the same route.
   - A deck produces `Slide1.PNG`, `Slide2.PNG` and so on inside its own subfolder,
     `<scratch-dir>/r<8hex>/`, which keeps two decks in one scratch folder apart. Open every
     slide image.
   - A Word file or workbook produces one PDF and a PNG per page (`r<8hex>-p01.png` onward).
     Open each page PNG. Do not try to read the PDF itself; many agent readers need an extra
     system tool to rasterize it. Keep the PDF as the record and inspect the PNGs.
   - Run it in the current session and never add an execution-policy override:

     ```
     & "assets/render-deliverable.ps1" -In "<file>" -Out "<scratch-dir>" [-TimeoutSec 180] [-NoPng] [-Dpi 100]
     ```

   - Optional switches: `-TimeoutSec` (seconds, 180 by default), `-NoPng` (PDF only for Word
     files and workbooks) and `-Dpi` (page-image resolution, 100 by default).
   - A plain-text email or announcement is its own render: read the text.
   - Output names leave out the deliverable's own name. A hash of the input path supplies the
     `r<8hex>` stem, stable for a given document. It names a document's PDF and page PNGs and
     a deck's image subfolder. The first output line is the mapping (formats below); use it to
     tie images to the right file and quote it in the report.
   - The reason: long names can exceed the Windows `MAX_PATH` limit (260 characters), and Word
     then reports a vague export failure that looks like a damaged file, not a path problem.
     When even the short output path is too long, the script declines up front with exit `7`,
     printing the length, the limit and the path. Choose a shorter `-Out` and retry. The `\\?\`
     long-path prefix is no remedy, because Word COM ignores it.
   - Any non-zero exit leaves the file UNREVIEWED: say so and stop. No visual sign-off without
     images, and source text never stands in for a render. After exit `5` or `6` a real PDF
     exists that no one has looked through.
   - The script closes only Office instances it started; one already running is used
     read-only, its settings untouched, and left open. For a hung render, shut that Office
     app by hand and run again, or give it a longer `-TimeoutSec`; never kill WINWORD,
     POWERPNT or EXCEL by name, which can close someone's documents and lose unsaved work. Its temp copies start
     `dlrv_`; other temp files are not touched.

3. **Brand pass.** Load the brand file (`brand/brand.json`, or `shared/brand.json` when the
   project has none, per "Where files come from") and check:
   - `colors.primary` is the accent and anchor, never a large flood of fill;
   - text colors: `colors.text` for body, `colors.textMuted` for secondary text;
   - surfaces: `colors.background` behind everything, `colors.surface` for fills,
     `colors.divider` for rules;
   - faces: `fonts.office` in Office files, `fonts.web` in HTML or SVG;
   - links use `colors.link`, never the Office default blue;
   - `status.*` colors appear only as functional signals (at risk, critical) and stay away
     from primary brand elements; if `status` is empty, a conventional red, amber or green is
     fine when used solely as a status signal;
   - nothing named in `avoid`; a color absent from the file counts as off-palette;
   - the `logo` and `templates` rules wherever the file supplies them.

   If `meta.placeholder` is `true`, still run the pass (one palette, one face, styled links),
   state in the scorecard that the brand file is a stand-in, and advise running
   `brand-extract`.

4. **Formatting and structure.** Work through `references/formatting-checklist.md`. Areas:
   bleed and overflow; overlap; grid; whitespace; legibility and contrast; face consistency
   and size floors; readable tables; footers and page numbering; image quality; slide and
   section structure; duplicated or orphaned headers; leftover placeholder text; links that
   are broken or default-styled.

5. **Wording.** Work through `references/wording-checklist.md`. Areas: clarity; voice and tone
   for the reader; answer first; specificity; consistent terminology; facts kept apart from
   judgment; and the house rules as `references/house-style.md` applies them. The forbidden
   lists are read at review time from the project's writing standard, falling back to the
   `shared/` copy (see "Where files come from"). No U+2014 em dash anywhere: use a colon, a
   comma, parentheses or a full stop.

6. **Consistency and facts.** Check that figures, dates, names and totals agree inside the
   deliverable: summary counts equal the detail, and rows add to the stated total. Titles and
   labels match the contents page or section markers, and cross-references land. These are
   flags only. Never invent a correction.

7. **Re-render after fixes** and view the fresh images. A fix can create a new defect, such
   as text pushed into the footer or a table split across pages. Report the clean second
   render.

## Output: the scorecard

| Outcome label | Use when |
|---|---|
| Hold for approval | A blocker is open, or flags need a decision before the file can go out (most cautious) |
| Ship with fixes applied | Auto-fixes were written to the file and nothing open blocks release |
| Ship | The file passed with nothing to fix |

The scorecard carries:

- the outcome label above;
- a result of Pass, Fixed or Flagged for each of Brand, Formatting, Wording and Consistency,
  with the location (slide or page), the problem and the remedy;
- the auto-fixes written into the file;
- the open flags, each with a concrete proposal;
- the path to the corrected file and confirmation of a clean re-render;
- the slide mapping whenever a restyle renumbered slides;
- the brand file used.

Render outputs (PDF, PNG) are disposable and belong in the session's scratch folder. The
final, reviewed and fixed file stays at the producer's save location.

### Severity

- **Blocker:** a defect the target audience would notice and judge (clipped text, wrong
  brand, wrong figure, leftover placeholder); nothing ships until it is fixed or flagged.
- **Should-fix:** a reader may notice it but it does not undermine the file (tight spacing, a
  small mismatch).
- **Polish:** optional.

## Reference: script facts

**Renderer, `assets/render-deliverable.ps1`**

| Parameter | Meaning |
|---|---|
| `-In` | Mandatory. The file to render |
| `-Out` | Mandatory. The output folder |
| `-TimeoutSec` | Integer, 180 if omitted. Reaching it ends the run with exit `2` |
| `-NoPng` | Switch. Word files and workbooks yield the PDF only |
| `-Dpi` | Integer, 100 if omitted. Page-image resolution |

Accepted extensions are `.pptx`, `.ppt`, `.docx`, `.doc`, `.xlsx` and `.xls`. A missing input
file or any other extension stops the script with an error before rendering starts. Slide
images are 1280x720 pixels.

The first output line ties images to the file. Two shapes (the file names are samples):

- Word file or workbook: `artifacts: r1a2b3c4d.pdf / r1a2b3c4d-pNN.png  <-  <name>.docx`
- deck: `artifacts: r5e6f7a8b\Slide*.PNG  <-  <name>.pptx`

| Exit | Meaning |
|---|---|
| `0` | Success; artifacts confirmed present |
| `1` | Refused before rendering: the input is missing, its type is unsupported, or `-Out` is the input's own folder |
| `2` | Time limit reached |
| `3` | No output at all |
| `4` | The worker child never printed its success marker (`RENDER-OK`) |
| `5` | A PDF exists but no page images |
| `6` | The PNG count disagrees with the PDF's page total, or the total was unreadable so no comparison was possible |
| `7` | Declined: the output path would pass `MAX_PATH` |
| other non-zero | Office or COM failure |

**Brand keys the brand pass reads:** `colors.primary`, `colors.text`, `colors.textMuted`,
`colors.background`, `colors.surface`, `colors.divider`, `colors.link`; `fonts.office`,
`fonts.web`; `status.*` (`good`, `warning`, `critical`, all null in the stand-in); `avoid`
(a list); `logo`; `templates` (`pptx`, `docx`, `xlsx`); `meta.placeholder` (a boolean).

## Common mistakes

| Mistake | Do instead |
|---|---|
| Reviewing source text with no render | Render first; text alone hides overlap and overflow |
| Looking only at the PDF of a Word file or workbook | Open the page PNGs; without them nothing was seen |
| Running the renderer with `-ExecutionPolicy Bypass` | Run it inside the session, no override |
| Counting a timeout or an empty render as a pass | Report any non-zero exit as UNREVIEWED; never route around it |
| Ending Office processes by name to free a stuck render | Close the app by hand and retry; the script never kills and neither may the reviewer |
| Treating status amber or red as off-brand | Accept them as signals; only misuse is a fault |
| Taking brand values from anywhere other than `brand/brand.json`, or failing that `shared/brand.json` | Read the brand file per "Where files come from" and name the one used |
| Approving a rebrand with no parity run, or one early run and none at hand-off | Run the parity gate again just before reporting |
| Assuming the original has not moved | Check its modified time and rebuild if it changed |
| Comparing icons byte for byte, or skipping them | Compare the alpha channel: recolors pass, a swapped glyph fails |
| Declaring "text identical" while operator and reviewer number slides differently | State the slide mapping in the scorecard |
| Changing wording or a number silently | Flag it with the exact change proposed |
| Applying a fix that shifts meaning or layout intent without sign-off | Turn it into a flag and wait for approval |

## Handoffs

- `deliverable-reviewer` (`.claude/agents/deliverable-reviewer.md`) owns and runs this whole
  procedure.
- `Chief of Staff` invokes the reviewer as step 2, after a producing agent finishes and
  before the operator receives the result. The reviewer returns the scorecard and the wording
  flags, and `Chief of Staff` raises the flags with the operator.
- `brand-extract` creates real brand values. Recommend it whenever the brand file
  is still the stand-in.
- `house-style` owns `writing-standard.md`, which the wording pass reads.
