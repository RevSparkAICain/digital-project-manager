"""Read and patch the DrawingML theme inside a .pptx or .docx package (standard library only).

Patching edits the XML text in place instead of re-serializing it, so every namespace prefix
and declaration Office relies on survives byte for byte. Parsing goes through safe_xml, which
refuses any document type declaration: Office parts never carry one, so a DTD means a crafted
file (entity expansion or external entity tricks), and the source is skipped.
"""
import os
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
SLOTS = ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4",
         "accent5", "accent6", "hlink", "folHlink")
FONT_TAGS = {"major": "majorFont", "minor": "minorFont"}
_THEME_PART = re.compile(r"^(?:ppt|word)/theme/theme(\d+)\.xml$")


def safe_xml(data):
    """Parse an XML part from an untrusted package. Only UTF-8 is accepted (Office writes
    UTF-8), so a UTF-16 part cannot hide a DTD from the check; any DTD or entity declaration
    is refused."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("XML part is not UTF-8")
    if "\x00" in text:
        raise ValueError("XML part contains NUL characters")
    declared = re.match(r"""\s*<\?xml[^>]*encoding\s*=\s*["']([^"']+)""", text)
    if declared and declared.group(1).lower().replace("_", "-") not in ("utf-8", "utf8"):
        raise ValueError("XML part declares a non-UTF-8 encoding")
    if "<!DOCTYPE" in text or "<!ENTITY" in text:
        raise ValueError("XML part with a document type declaration refused")
    return ET.fromstring(data)


def theme_member(names):
    """The package's main theme part (lowest theme number), or None."""
    found = sorted((int(m.group(1)), n) for n in names for m in [_THEME_PART.match(n)] if m)
    return found[0][1] if found else None


def read_theme(xml_bytes):
    root = safe_xml(xml_bytes)
    colors = {}
    scheme = root.find(".//{%s}clrScheme" % A)
    if scheme is not None:
        for slot in SLOTS:
            el = scheme.find("{%s}%s" % (A, slot))
            if el is None or len(el) == 0:
                continue
            child = el[0]
            if child.tag == "{%s}sysClr" % A:
                val = child.get("lastClr")
            elif child.tag == "{%s}srgbClr" % A:
                val = child.get("val")
            else:
                continue
            if val and re.fullmatch(r"[0-9A-Fa-f]{6}", val):
                colors[slot] = "#" + val.upper()
    fonts = {}
    for key, tag in FONT_TAGS.items():
        latin = root.find(".//{%s}%s/{%s}latin" % (A, tag, A))
        if latin is not None and latin.get("typeface"):
            fonts[key] = latin.get("typeface")
    return {"colors": colors, "fonts": fonts}


def patch_theme(xml_bytes, colors, fonts):
    """Theme XML with the given color slots set to srgbClr values and the given latin
    typefaces. Raises ValueError for an unknown slot or one the theme does not have."""
    text = xml_bytes.decode("utf-8")
    for slot, hexv in colors.items():
        if slot not in SLOTS:
            raise ValueError("unknown theme slot %r" % slot)
        new = '<a:%s><a:srgbClr val="%s"/></a:%s>' % (slot, hexv.lstrip("#").upper(), slot)
        pattern = re.compile(r"<a:%s>.*?</a:%s>" % (slot, slot), re.S)
        text, count = pattern.subn(lambda m: new, text, count=1)
        if count != 1:
            raise ValueError("theme has no <a:%s> slot" % slot)
    for key, family in fonts.items():
        tag = FONT_TAGS[key]
        pattern = re.compile(r'(<a:%s>\s*<a:latin typeface=")[^"]*(")' % tag)
        safe = escape(family, {'"': "&quot;"})
        text, count = pattern.subn(lambda m: m.group(1) + safe + m.group(2), text, count=1)
        if count != 1:
            raise ValueError("theme has no %s latin typeface" % tag)
    return text.encode("utf-8")


def rewrite_member(path, member, data):
    """Replace one member of a zip package in place, keeping every other member and the order."""
    fd, tmp = tempfile.mkstemp(suffix=".zip", dir=os.path.dirname(os.path.abspath(path)))
    os.close(fd)
    try:
        with zipfile.ZipFile(path) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():
                dst.writestr(info, data if info.filename == member else src.read(info.filename))
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def apply_theme(path, colors, fonts):
    with zipfile.ZipFile(path) as zf:
        member = theme_member(zf.namelist())
        if member is None:
            raise ValueError("%s has no theme part" % os.path.basename(path))
        data = patch_theme(zf.read(member), colors, fonts)
    rewrite_member(path, member, data)
