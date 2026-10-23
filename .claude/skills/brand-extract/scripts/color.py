"""Color math for brand-extract: parsing, CIE Lab distance, WCAG contrast, lightness moves."""
import colorsys
import math
import re

NEUTRAL_CHROMA = 12.0
_TOKEN = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)")
_RGB_FN = re.compile(
    r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([0-9.]+)\s*)?\)")


def normalize_hex(value):
    """'#RRGGBB' for '#abc', '#aabbcc', 'aabbcc' or 'rgb(r, g, b)'. None for anything this
    skill does not read: named colors, percentages, a fully transparent rgba()."""
    v = value.strip()
    m = _RGB_FN.fullmatch(v)
    if m:
        if m.group(4) is not None:
            try:
                alpha = float(m.group(4))
            except ValueError:  # a malformed alpha such as "1.2.3"
                return None
            if alpha == 0:
                return None
        return to_hex(*(int(x) for x in m.group(1, 2, 3)))
    if not v.startswith("#"):
        v = "#" + v
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        v = "#" + "".join(ch * 2 for ch in v[1:])
    if re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        return v.upper()
    return None


def find_colors(text):
    """Every color written in a CSS value, in order of appearance."""
    out = []
    for m in _TOKEN.finditer(text):
        hexv = normalize_hex(m.group(0))
        if hexv:
            out.append(hexv)
    return out


def rgb(hexv):
    return tuple(int(hexv[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in (r, g, b))


def _linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexv):
    """WCAG relative luminance, 0 (black) to 1 (white)."""
    r, g, b = (_linear(c) for c in rgb(hexv))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def lab(hexv):
    """CIE L*a*b* under D65."""
    r, g, b = (_linear(c) for c in rgb(hexv))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    """CIE76 distance in Lab. Below 3 reads as the same color to most viewers."""
    return math.dist(lab(a), lab(b))


def chroma(hexv):
    _, a, b = lab(hexv)
    return math.hypot(a, b)


def is_neutral(hexv):
    return chroma(hexv) < NEUTRAL_CHROMA


def hue(hexv):
    return colorsys.rgb_to_hls(*(c / 255.0 for c in rgb(hexv)))[0] * 360


def hue_distance(a, b):
    d = abs(hue(a) - hue(b)) % 360
    return min(d, 360 - d)


def mix(a, b, t):
    """a moved toward b by fraction t (0 keeps a, 1 gives b), in sRGB."""
    return to_hex(*(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def ensure_contrast(fg, against, target=4.5):
    """(color, changed). When fg misses the WCAG ratio against `against`, move its lightness
    away from `against` in 1 percent steps, keeping hue and saturation."""
    if contrast(fg, against) >= target:
        return fg, False
    h, lightness, s = colorsys.rgb_to_hls(*(c / 255.0 for c in rgb(fg)))
    step = -0.01 if luminance(against) >= luminance(fg) else 0.01
    for i in range(1, 101):
        moved = min(1.0, max(0.0, lightness + step * i))
        cand = to_hex(*(c * 255 for c in colorsys.hls_to_rgb(h, moved, s)))
        if contrast(cand, against) >= target:
            return cand, True
    return ("#000000" if step < 0 else "#FFFFFF"), True
