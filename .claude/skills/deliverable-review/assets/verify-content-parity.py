"""Content parity gate for a restyled PowerPoint deck.

Given the source deck and its restyled copy, show that the restyle changed only the look.
Content (text, notes, table cells, links, shape inventory and geometry, stacking order, icon
artwork) must match exactly; typography differences are warnings unless strict; colors,
fonts, theme and effects are never examined.

Exit status: 0 when content matches, 1 when it does not, 2 when the check could not run.
"""
import argparse
import io
import json
import sys
from collections import Counter
from hashlib import sha1


def _missing(package):
    print("%s is required (install it with: pip install %s)" % (package, package),
          file=sys.stderr)
    sys.exit(2)


try:
    from pptx import Presentation
except ImportError:
    _missing("python-pptx")

try:
    from PIL import Image
except ImportError:
    _missing("Pillow")

try:
    from pptx.shapes.group import GroupShape as _GroupClass
except ImportError:
    _GroupClass = None

BAR_HEAVY = "=" * 72
BAR_LIGHT = "-" * 72
DETAIL_PAD = " " * 18
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SEP = "\x1f"

CONTENT_FIELDS = ("text", "link")
TYPE_FIELDS = ("size", "bold", "italic", "underline", "align", "level")


# --------------------------------------------------------------- small helpers ---

def local_name(element):
    """Tag of an XML element without its namespace."""
    tag = element.tag
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else str(tag)


def flag_value(value):
    """Bold, italic, underline: inherited (None) reads as off; anything set is kept."""
    return False if value is None else value


def align_value(value):
    """Paragraph alignment as a bare name; inherited reads as LEFT."""
    if value is None:
        return "LEFT"
    return str(value).split()[0]


def artwork_signature(blob):
    """Size plus a digest of the alpha mask, so a recolor matches and a new glyph does not."""
    try:
        with Image.open(io.BytesIO(blob)) as img:
            rgba = img.convert("RGBA")
        mask = rgba.getchannel("A").tobytes()
        return "%dx%d:%s" % (rgba.width, rgba.height, sha1(mask).hexdigest()[:12])
    except Exception:
        return "unreadable:" + sha1(blob).hexdigest()[:12]


def embedded_image(shape):
    """Bytes of the image a shape fills itself with, or None when there is none to read."""
    element = shape._element
    for child in element:
        if local_name(child) != "blipFill":
            continue
        for grandchild in child:
            if local_name(grandchild) != "blip":
                continue
            rel_id = grandchild.get("{%s}embed" % REL_NS)
            if not rel_id:
                return None
            try:
                return shape.part.related_part(rel_id).blob
            except (KeyError, AttributeError):
                return None
        return None
    return None


def is_group(shape):
    if _GroupClass is not None:
        return isinstance(shape, _GroupClass)
    return local_name(shape._element) == "grpSp"


def walk(shapes, depth=0):
    """Every shape with its nesting depth, a group ahead of its members."""
    for shape in shapes:
        yield shape, depth
        if is_group(shape):
            for item in walk(shape.shapes, depth + 1):
                yield item


def kind_of(shape):
    try:
        kind = shape.shape_type
    except Exception:
        kind = None
    if kind is None:
        return local_name(shape._element)
    return str(kind)


def turn_of(shape):
    try:
        return int(shape.rotation or 0)
    except Exception:
        return 0


def text_runs(shape):
    """One record per run of a shape's text frame."""
    found = []
    for p_no, para in enumerate(shape.text_frame.paragraphs):
        for r_no, run in enumerate(para.runs):
            font = run.font
            found.append({
                "shape": shape.name,
                "para": p_no,
                "run": r_no,
                "text": run.text,
                "link": run.hyperlink.address,
                "size": None if font.size is None else font.size.pt,
                "bold": flag_value(font.bold),
                "italic": flag_value(font.italic),
                "underline": flag_value(font.underline),
                "align": align_value(para.alignment),
                "level": para.level,
            })
    return found


def profile(slide):
    """Everything about one slide that the gate compares."""
    runs, geometry, cells, icons = [], [], [], []
    for shape, depth in walk(slide.shapes):
        geometry.append((kind_of(shape), depth, shape.left, shape.top, shape.width,
                         shape.height, turn_of(shape)))
        if getattr(shape, "has_text_frame", False):
            runs.extend(text_runs(shape))
        if getattr(shape, "has_table", False):
            for r_no, row in enumerate(shape.table.rows):
                for c_no, cell in enumerate(row.cells):
                    cells.append((shape.name, r_no, c_no, cell.text))
        blob = embedded_image(shape)
        if blob is not None:
            icons.append(artwork_signature(blob))
    spoken = ""
    if slide.has_notes_slide:
        frame = slide.notes_slide.notes_text_frame
        spoken = frame.text if frame is not None else ""
    return {"runs": runs, "shapes": geometry, "tables": cells, "icons": icons,
            "notes": spoken}


def text_key(page):
    return SEP.join(r["text"] for r in page["runs"])


def pick_shift(old_pages, new_pages):
    """Automatic pairing shift; ties keep the full count difference."""
    gap = len(new_pages) - len(old_pages)
    if gap <= 0:
        return gap
    old_keys = [text_key(p) for p in old_pages]
    new_keys = [text_key(p) for p in new_pages]

    def score(shift):
        return sum(1 for i, key in enumerate(old_keys) if new_keys[i + shift] == key)

    best, best_score = gap, score(gap)
    for shift in range(gap):
        candidate = score(shift)
        if candidate > best_score:
            best, best_score = shift, candidate
    return best


# --------------------------------------------------------------------- report ---

def line(category, detail):
    print("  " + category.ljust(14) + detail)


def plural_findings(count):
    return "(%d finding)" % count if count == 1 else "(%d findings)" % count


class Tally(object):
    """Collects failures, warnings and allowed notes for the closing verdict."""

    def __init__(self, strict):
        self.strict = strict
        self.hard = []
        self.warnings = []
        self.allowed = []

    def typography(self, message):
        if self.strict:
            self.hard.append(message)
        else:
            self.warnings.append(message)


def compare_text(tag, old, new, tally):
    old_runs, new_runs = old["runs"], new["runs"]
    clean = len(old_runs) == len(new_runs)
    if not clean:
        line("TEXT", f"RUN COUNT {len(old_runs)} vs {len(new_runs)}")
        tally.hard.append(f"{tag}: run count {len(old_runs)} vs {len(new_runs)}")
    style_count = 0
    for before, after in zip(old_runs, new_runs):
        owner = before["shape"]
        for field in CONTENT_FIELDS:
            if before[field] != after[field]:
                clean = False
                line("TEXT", f"{owner}  {field.upper()} CHANGED")
                print(DETAIL_PAD + "original: " + repr(before[field]))
                print(DETAIL_PAD + "restyled: " + repr(after[field]))
                tally.hard.append(f"{tag}: {field} changed in {owner}")
        for field in TYPE_FIELDS:
            if before[field] != after[field]:
                style_count += 1
                line("TYPOGRAPHY", f"{owner}  {field} {before[field]!r} -> {after[field]!r}")
                tally.typography(
                    f"{tag}: {field} in {owner} changed {before[field]!r} -> {after[field]!r}")
    if clean:
        line("TEXT", f"IDENTICAL ({len(old_runs)} runs)")
    if style_count:
        suffix = "" if tally.strict else " [warning]"
        line("TYPOGRAPHY", f"{style_count} difference(s){suffix}")


def compare_notes(tag, old, new, tally):
    before, after = len(old["notes"]), len(new["notes"])
    if old["notes"] != new["notes"]:
        line("NOTES", f"DIFFER ({before} vs {after} chars)")
        tally.hard.append(f"{tag}: speaker notes differ")
    else:
        line("NOTES", f"IDENTICAL ({before} chars)")


def compare_tables(tag, old, new, tally):
    if old["tables"] != new["tables"]:
        line("TABLES", "DIFFER")
        tally.hard.append(f"{tag}: table cell text differs")
    elif old["tables"]:
        line("TABLES", f"IDENTICAL ({len(old['tables'])} cells)")


def compare_shapes(tag, old, new, tally, allow_extra):
    before, after = Counter(old["shapes"]), Counter(new["shapes"])
    gone, extra = before - after, after - before
    if gone:
        line("SHAPES", f"{sum(gone.values())} REMOVED/MOVED")
        for kind, _depth, left, top, *_rest in gone:
            tally.hard.append(f"{tag}: shape removed or moved ({kind} at {left},{top})")
    if extra:
        count = sum(extra.values())
        if allow_extra:
            line("SHAPES", f"{count} added (allowed)")
            tally.allowed.append(f"{tag}: {count} shape(s) added (allowed)")
        else:
            line("SHAPES", f"{count} ADDED")
            for kind, _depth, left, top, *_rest in extra:
                tally.hard.append(
                    f"{tag}: shape added ({kind} at {left},{top}); rerun with "
                    f"--allow-added-shapes if it is intended decoration")
    if not gone and not extra:
        same_order = old["shapes"] == new["shapes"]
        line("SHAPES", f"IDENTICAL ({len(old['shapes'])}, z-order preserved: {same_order})")
        if not same_order:
            tally.hard.append(f"{tag}: z-order changed")


def compare_icons(tag, old, new, tally, allow_extra):
    before, after = Counter(old["icons"]), Counter(new["icons"])
    lost, gained = before - after, after - before
    if lost:
        line("ICONS", f"{sum(lost.values())} ARTWORK REPLACED")
        for sig in lost:
            tally.hard.append(
                f"{tag}: icon ARTWORK replaced ({sig}). A recolor keeps the alpha mask, "
                f"so this mismatch means a different icon, not a recolored one.")
    if gained:
        count = sum(gained.values())
        if allow_extra:
            line("ICONS", f"{count} added (allowed)")
            tally.allowed.append(f"{tag}: {count} icon(s) added (allowed)")
        else:
            line("ICONS", f"{count} NEW ARTWORK")
            for sig in gained:
                tally.hard.append(f"{tag}: new icon artwork ({sig})")
    if not lost and not gained:
        line("ICONS", f"IDENTICAL ({len(old['icons'])}, alpha-matched)")


def print_verdict(tally):
    block = ["", BAR_HEAVY]
    if tally.hard:
        block.append("RESULT: CONTENT CHANGED  " + plural_findings(len(tally.hard)))
        block.append(BAR_HEAVY)
        block.extend("  - " + finding for finding in tally.hard)
        block.extend([
            "",
            "  The restyle altered content, so it is not a style-only change. Put the",
            "  original content back, then run this gate again before the deck ships.",
        ])
    else:
        block.extend([
            "RESULT: PARITY HELD. No content differences.",
            BAR_HEAVY,
            "  Text, speaker notes, table cells, the shape set with its geometry and",
            "  z-order, link targets and icon artwork all match the original.",
        ])
        if tally.warnings:
            block.append(f"  {len(tally.warnings)} typography warning(s) remain; "
                         "confirm each one below was intended.")
        else:
            block.append("  No typography differences either; only branding and style moved.")
        block.extend([
            "  Not examined here: chart data, SmartArt text and embedded objects.",
            "  Check those by eye in the rendered pages.",
        ])
        block.extend("  note: " + note for note in tally.allowed)
    if tally.warnings:
        block.extend(["", f"  TYPOGRAPHY WARNINGS ({len(tally.warnings)}): "
                          "confirm each change was intended"])
        block.extend("    ! " + warning for warning in tally.warnings)
    print("\n".join(block))


# ----------------------------------------------------------------------- main ---

def build_parser():
    parser = argparse.ArgumentParser(
        description="Confirm that a restyled deck kept every piece of the original content.")
    parser.add_argument("original")
    parser.add_argument("restyled")
    parser.add_argument("--offset", type=int, default=None)
    parser.add_argument("--allow-added-slides", help="accept slides added by the restyle",
                        action="store_true")
    parser.add_argument("--allow-added-shapes",
                        help="accept shapes and icons added by the restyle",
                        action="store_true")
    parser.add_argument("--strict-typography", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def open_deck(path):
    try:
        return Presentation(path)
    except Exception as problem:
        message = str(problem)
        if path not in message:
            message = "%s (%s)" % (message, path)
        print("could not open a file: " + message, file=sys.stderr)
        return None


def main(argv=None):
    opts = build_parser().parse_args(argv)

    old_deck = open_deck(opts.original)
    if old_deck is None:
        return 2
    new_deck = open_deck(opts.restyled)
    if new_deck is None:
        return 2
    try:
        old_pages = [profile(s) for s in old_deck.slides]
        new_pages = [profile(s) for s in new_deck.slides]
    except Exception as problem:
        print("could not read a slide: " + str(problem), file=sys.stderr)
        return 2

    if opts.offset is None:
        shift, source = pick_shift(old_pages, new_pages), "auto"
    else:
        shift, source = opts.offset, "--offset"

    print(BAR_HEAVY)
    print("CONTENT PARITY GATE")
    print(BAR_HEAVY)
    print("  %s: %s  (%d slides)" % ("original".ljust(9), opts.original, len(old_pages)))
    print("  %s: %s  (%d slides)" % ("restyled".ljust(9), opts.restyled, len(new_pages)))
    print("  %s: original slide N  ->  restyled slide N+%d  (%s)"
          % ("mapping".ljust(9), shift, source))

    tally = Tally(opts.strict_typography)
    if len(new_pages) < len(old_pages):
        tally.hard.append(f"FEWER slides in the restyled deck ({len(new_pages)}) "
                          f"than in the original ({len(old_pages)})")
    elif len(new_pages) > len(old_pages) and not opts.allow_added_slides:
        extra = len(new_pages) - len(old_pages)
        tally.hard.append(f"{extra} extra slide(s) in the restyled deck; rerun with "
                          f"--allow-added-slides when they are planned")
    if (old_deck.slide_width != new_deck.slide_width
            or old_deck.slide_height != new_deck.slide_height):
        tally.hard.append(
            f"slide dimensions differ ({old_deck.slide_width}x{old_deck.slide_height} vs "
            f"{new_deck.slide_width}x{new_deck.slide_height} EMU)")

    for index, old in enumerate(old_pages):
        partner = index + shift
        if partner < 0 or partner >= len(new_pages):
            tally.hard.append(f"original slide {index + 1} has no counterpart")
            continue
        new = new_pages[partner]
        tag = "orig %d -> new %d" % (index + 1, partner + 1)
        print("")
        print(BAR_LIGHT)
        print(tag)
        compare_text(tag, old, new, tally)
        compare_notes(tag, old, new, tally)
        compare_tables(tag, old, new, tally)
        compare_shapes(tag, old, new, tally, opts.allow_added_shapes)
        compare_icons(tag, old, new, tally, opts.allow_added_shapes)

    print_verdict(tally)

    if opts.json:
        print("")
        print(json.dumps({
            "parity": not tally.hard,
            "findings": tally.hard,
            "typography_warnings": tally.warnings,
            "allowed": tally.allowed,
        }, indent=2))

    return int(bool(tally.hard))


if __name__ == "__main__":
    sys.exit(main())
