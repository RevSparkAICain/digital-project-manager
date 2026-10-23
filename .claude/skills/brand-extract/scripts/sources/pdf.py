"""PDF adapter (PyMuPDF): fill colors by area, text colors by area, embedded fonts by role."""
import os
import re
import statistics

from candidate import Candidate, SourceError

BASE14 = {"helvetica", "times", "courier", "symbol", "zapfdingbats"}
HEADING_RATIO = 1.3  # text this many times the page's median size votes for the heading font


def font_family(name):
    """'ABCDEF+SourceSerif4-Bold' gives 'Source Serif 4'. None for the standard 14 PDF fonts,
    which mean the document did not embed a brand face."""
    name = re.sub(r"^[A-Z]{6}\+", "", name or "")
    name = re.split(r"[-,]", name)[0].strip()
    key = name.lower().replace(" ", "")
    if not name or key in BASE14 or key.startswith("times"):
        return None
    return re.sub(r"(?<=[a-z])(?=[A-Z0-9])", " ", name)


def _hex(fill):
    if len(fill) == 1:
        fill = (fill[0],) * 3
    elif len(fill) == 4:
        c, m, y, k = fill
        fill = ((1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in fill[:3])


def _add(table, key, amount):
    table[key] = table.get(key, 0.0) + amount


def _scan(doc, fills, texts, faces):
    for page in doc:
        for drawing in page.get_drawings():
            fill = drawing.get("fill")
            if fill:
                rect = drawing["rect"]
                _add(fills, _hex(fill), abs(rect.width * rect.height))
        spans = [s for block in page.get_text("dict")["blocks"]
                 for line in block.get("lines", []) for s in line["spans"]
                 if s["text"].strip()]
        if not spans:
            continue
        median = statistics.median(s["size"] for s in spans)
        for s in spans:
            x0, y0, x1, y1 = s["bbox"]
            area = abs((x1 - x0) * (y1 - y0))
            _add(texts, "#%06X" % s["color"], area)
            family = font_family(s["font"])
            if family:
                role = "heading" if s["size"] >= HEADING_RATIO * median else "body"
                _add(faces, (role, family), area)


def extract(path):
    try:
        import fitz
    except ImportError:
        raise SourceError("PyMuPDF is not installed (pip install pymupdf)")
    src = "pdf:" + os.path.basename(path)
    try:
        doc = fitz.open(path, filetype="pdf")
    except Exception as err:  # PyMuPDF raises its own exception types for unreadable files
        raise SourceError("cannot open PDF: %s" % err)
    fills, texts, faces = {}, {}, {}
    with doc:
        if doc.needs_pass:
            raise SourceError("PDF is password protected")
        if doc.page_count == 0:
            raise SourceError("PDF has no pages")
        try:
            _scan(doc, fills, texts, faces)
        except SourceError:
            raise
        except Exception as err:  # a MuPDF error on a damaged page skips the source
            raise SourceError("cannot read PDF content: %s" % err)
    cands = [Candidate("color", k, v, src, "filled area %.0f pt2" % v)
             for k, v in sorted(fills.items())]
    cands += [Candidate("color", k, v, src, "text area %.0f pt2" % v)
              for k, v in sorted(texts.items())]
    cands += [Candidate("font", k, v, src, "%s text, %.0f pt2" % (k[0], v))
              for k, v in sorted(faces.items())]
    return cands
