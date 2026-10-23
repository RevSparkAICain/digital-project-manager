"""Image adapter: SVG paint colors by use count, raster colors by pixel share (Pillow).
Every image is also offered as a logo candidate; merge.py prefers SVG."""
import os
import re

import color
from candidate import Candidate, SourceError

RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MAX_SVG_CHARS = 5_000_000
# No two adjacent unbounded runs of optional whitespace, and the rgb() argument list is capped,
# so the scan stays linear on hostile input.
SVG_PAINT = re.compile(
    r"""(?:fill|stroke|stop-color)[ \t]*[:=][ \t]*["']?(#[0-9a-fA-F]{3,6}\b|rgba?\([^)]{0,40}\))""")


def extract(path):
    ext = os.path.splitext(path)[1].lower()
    src = "image:" + os.path.basename(path)
    if ext == ".svg":
        return _svg(path, src)
    if ext in RASTER:
        return _raster(path, src)
    raise SourceError("unsupported image type %s" % (ext or "(none)"))


def _svg(path, src):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read(MAX_SVG_CHARS)
    except OSError as err:
        raise SourceError("cannot read SVG: %s" % err)
    if "<svg" not in text:
        raise SourceError("not an SVG document")
    counts = {}
    for raw in SVG_PAINT.findall(text):
        hexv = color.normalize_hex(raw)
        if hexv:
            counts[hexv] = counts.get(hexv, 0) + 1
    cands = [Candidate("color", k, float(n), src, "%d paint use(s) in SVG" % n)
             for k, n in sorted(counts.items())]
    cands.append(Candidate("logo", os.path.abspath(path), 1.0, src, "SVG image file"))
    return cands


def _raster(path, src):
    try:
        from PIL import Image
    except ImportError:
        raise SourceError("Pillow is not installed (pip install pillow)")
    try:
        with Image.open(path) as img:
            width, height = img.size
            rgba = img.convert("RGBA")
    except Exception as err:  # Pillow raises several exception types for unreadable files
        raise SourceError("cannot read image: %s" % err)
    rgba.thumbnail((200, 200), Image.Resampling.NEAREST)
    raw = rgba.tobytes()
    pixels = [raw[i:i + 3] for i in range(0, len(raw), 4) if raw[i + 3] >= 128]
    if not pixels:
        raise SourceError("image has no opaque pixels")
    flat = Image.frombytes("RGB", (len(pixels), 1), b"".join(pixels))
    quant = flat.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = quant.getpalette()
    counts = {}
    for count, index in quant.getcolors():
        hexv = color.to_hex(*palette[index * 3:index * 3 + 3])
        counts[hexv] = counts.get(hexv, 0) + count
    total = float(len(pixels))
    cands = [Candidate("color", k, float(n), src, "%.1f%% of opaque pixels" % (100 * n / total))
             for k, n in sorted(counts.items())]
    cands.append(Candidate("logo", os.path.abspath(path), float(width * height), src,
                           "%dx%d raster image" % (width, height)))
    return cands
