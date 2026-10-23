# Formatting Checklist

Apply this list to the rendered images: the slide PNGs for a deck, the page PNGs for a Word
file or workbook. Give every item a result of Pass, Fixed or Flagged, and attach the slide or
page to every issue. Colors and faces are read from the brand file in lookup order,
`brand/brand.json` first and `shared/brand.json` when the project has none (see "Where files
come from" in `SKILL.md`). This checklist states no values of its own.

## 1. All formats

### Layout

| Check | A failure looks like |
|---|---|
| Canvas: content stays within the page or slide, clear of the edges and margins | Text or a picture running off the edge |
| Collisions: no element (text, picture, shape or chart) sits on top of another | A caption printed across a chart |
| Grid: tops, left edges and columns line up | One box sitting a few pixels off the rest |
| Whitespace: neither packed nor empty, with steady margins and gutters | A slide crammed edge to edge beside a nearly bare one |

### Type

| Check | A failure looks like |
|---|---|
| Faces: every face matches `fonts` in the brand file | A foreign face carried in by a paste |
| Size floors: slide body about 14pt or larger, captions about 10pt, table text about 8pt | Table text too small to read in the render |
| Capitalization: titles and headers hold to one scheme, sentence case or title case | Half the headings in title case, half not |
| Em dash: search the bytes for `E2 80 94`; on a rendered page the em dash is hard to tell from an en dash or a hyphen | A long dash that looks like a hyphen on screen |

### Color and links

| Check | A failure looks like |
|---|---|
| Contrast: body copy and large text stay readable; aim for 4.5:1 for body and 3:1 for large | Washed-out gray body copy on white, or dark text on a strong fill at small size |
| Links: they use `colors.link` and each one reaches the right destination | Underlined Office blue, or a link that goes nowhere |

### Content

| Check | A failure looks like |
|---|---|
| Leftovers: nothing unfinished remains | "Lorem ipsum", "TODO", "TBD", "[name]", "XX", template boilerplate or unfilled double-brace tokens |
| Images: sharp and in proportion | A stretched or pixelated picture |

## 2. Decks (.pptx)

| Check | A failure looks like |
|---|---|
| Footer and slide marker: identical in wording and placement on every slide, with the right numbers or part markers; when house convention calls for a classification footer, its text is `For internal use only.` | A footer that shifts or changes wording between slides |
| Titles: every content slide has the right title | A duplicated or orphaned title |
| Tables: they fit the slide and the cells are readable | The footer cutting off the last row |
| Charts: categories labelled, colors from the brand palette, values matching the figures elsewhere in the deck | A legend colliding with the title or plot area |
| Tiles and callouts: a row of them shares one size and alignment | Tiles of mixed heights in one row |
| Section order: slides follow the planned flow (for example summary, detail, appendix) and carry matching section tags | An appendix slide ahead of the summary |
| Bullets: nesting stays shallow and even | Three levels of indent on one slide |
| Template: layouts follow `templates.pptx` in the brand file when it is set | A slide built on a layout the template never offered |

## 3. Word files (.docx)

| Check | A failure looks like |
|---|---|
| Heading styles: real Heading 1, 2 and 3 | Bold text posing as a heading |
| Headers, footers and page numbers: correct on every page | A footer missing from page 3 |
| Table of contents: any contents list agrees with the actual headings and pages | A contents entry pointing to a renamed section |
| Lists: built from list styles, numbering unbroken | Numbering that restarts mid-list |
| Keep with next: each heading shares a page with its first paragraph; tables break only between row groups | A heading stranded at the foot of a page, or a table split mid-row |
| Margins and spacing: even throughout | Accidental doubled paragraph breaks |
| Cross-references: each "see Figure N" or cross-reference lands on the item it names | A caption number that no longer matches |
| Authorship: the author property and the prepared-by line both name the producing operator | A prepared-by line naming someone else |

## 4. Workbooks (.xlsx)

| Check | A failure looks like |
|---|---|
| Print area: it includes every column, and header rows repeat across printed pages | A column cut off on the second printed page |
| Number formats: one style each for currency, percentages and dates | A raw date serial, `#REF!` or `#DIV/0!` |
| Frozen headers and widths: header rows frozen on long tables, columns wide enough for their content | `####` in a narrow column |
| Working cells: helper columns and hidden working cells are removed, so an export carries nothing extra | A leftover debug column in the export |
| Last row: it survives the footer margin in print or export | The final row hidden under the footer |

## 5. Structure and consistency (flag only, never auto-changed)

| Check | A failure looks like |
|---|---|
| Totals: summary totals and counts agree with the detail beneath them | A stated total that does not equal the rows |
| Names and dates: they agree everywhere they appear | One project spelled two ways |
| Purpose: read as the intended audience would: does it do the job it states? | A deck that never reaches its own ask |
