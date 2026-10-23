"""PPTX/DOCX adapter: theme colors and fonts, slide size, title position, margins, footer use."""
import os
import re
import zipfile
import zlib
import xml.etree.ElementTree as ET

import office_theme
from candidate import Candidate, SourceError

MAX_PART_BYTES = 20_000_000  # zip bomb guard: no package part is read past this size

# accent1 is the slot Office paints first, so it carries the most evidence.
SLOT_WEIGHT = {"accent1": 3.0, "accent2": 2.0, "accent3": 1.5, "accent4": 1.0,
               "accent5": 1.0, "accent6": 1.0, "dk1": 2.0, "lt1": 2.0, "dk2": 1.0,
               "lt2": 1.0, "hlink": 0.5}
EXTS = {".pptx": "pptx", ".potx": "pptx", ".docx": "docx", ".dotx": "docx"}
EMU_PER_IN = 914400
TWIPS_PER_IN = 1440
A = office_theme.A
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def extract(path):
    kind = EXTS.get(os.path.splitext(path)[1].lower())
    if kind is None:
        raise SourceError("not a .pptx, .potx, .docx or .dotx file")
    src = "template:" + os.path.basename(path)
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise SourceError("not a readable Office package (encrypted or corrupt)")
    with zf:
        try:
            names = zf.namelist()
            cands = []
            member = office_theme.theme_member(names)
            if member:
                theme = office_theme.read_theme(_read(zf, member))
                for slot, hexv in theme["colors"].items():
                    if slot in SLOT_WEIGHT:
                        cands.append(Candidate("color", hexv, SLOT_WEIGHT[slot], src,
                                               "theme slot " + slot))
                for key, role in (("major", "heading"), ("minor", "body")):
                    if key in theme["fonts"]:
                        cands.append(Candidate("font", (role, theme["fonts"][key]), 1.0, src,
                                               "theme %s font" % key))
            layout = _pptx_layout if kind == "pptx" else _docx_layout
            cands += layout(zf, names, src)
        except (ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile,
                zlib.error, RuntimeError, OverflowError) as err:
            raise SourceError("unreadable Office package: %s" % err)
    return cands


def _read(zf, name):
    if zf.getinfo(name).file_size > MAX_PART_BYTES:
        raise SourceError("package part too large: %s" % name)
    return zf.read(name)


def _pptx_layout(zf, names, src):
    out = []
    if "ppt/presentation.xml" in names:
        size = office_theme.safe_xml(_read(zf, "ppt/presentation.xml")).find("{%s}sldSz" % P)
        if size is not None:
            for key, attr in (("slideWidthIn", "cx"), ("slideHeightIn", "cy")):
                out.append(Candidate("layout", (key, round(int(size.get(attr)) / EMU_PER_IN, 3)),
                                     1.0, src, "presentation slide size"))
    masters = sorted(n for n in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n))
    if masters:
        root = office_theme.safe_xml(_read(zf, masters[0]))
        types = []
        for sp in root.iter("{%s}sp" % P):
            ph = sp.find("{%s}nvSpPr/{%s}nvPr/{%s}ph" % (P, P, P))
            if ph is None:
                continue
            types.append(ph.get("type"))
            off = sp.find("{%s}spPr/{%s}xfrm/{%s}off" % (P, A, A))
            if ph.get("type") in ("title", "ctrTitle") and off is not None:
                out.append(Candidate("layout",
                                     ("titleTopIn", round(int(off.get("y")) / EMU_PER_IN, 3)),
                                     1.0, src, "slide master title position"))
        out.append(Candidate("layout", ("footer", "ftr" in types), 1.0, src,
                             "slide master footer placeholder"))
    return out


def _docx_layout(zf, names, src):
    out = []
    if "word/document.xml" in names:
        margin = None
        for m in office_theme.safe_xml(_read(zf, "word/document.xml")).iter("{%s}pgMar" % W):
            margin = m  # the last sectPr is the body section
        left = margin.get("{%s}left" % W) if margin is not None else None
        if left:
            out.append(Candidate("layout", ("pageMarginIn", round(int(left) / TWIPS_PER_IN, 3)),
                                 1.0, src, "document left margin"))
    has_footer = any(re.fullmatch(r"word/footer\d*\.xml", n) for n in names)
    out.append(Candidate("layout", ("footer", has_footer), 1.0, src, "footer part present"))
    return out
