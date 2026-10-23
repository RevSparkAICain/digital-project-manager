"""Turn candidates from every source into one brand profile.

Pure and deterministic: no I/O, no randomness, ties broken by value. references/scoring.md
states the same rules in plain English; keep the two in step.
"""
import math

import color
from candidate import PRECEDENCE, source_type

DELTA_E_CLUSTER = 3.0
LIGHT_LUMINANCE = 0.7
DARK_LUMINANCE = 0.18
MID_LUMINANCE = 0.5
ACCENT_HUE_GAP = 30.0
CONTRAST_TARGET = 4.5
CHART_LEN = 6
CHART_TINTS = (0.3, 0.45, 0.6, 0.75, 0.9)
WHITE = "#FFFFFF"

DEFAULTS = {"colors.primary": "#1F6FEB", "colors.text": "#222222",
            "colors.background": "#FFFFFF", "fonts.body": "Arial"}
LABELS = {"colors.primary": "primary color", "colors.text": "text color",
          "colors.background": "background color", "fonts.body": "body font"}
LAYOUT_DEFAULTS = {"slideWidthIn": 13.333, "slideHeightIn": 7.5, "titleTopIn": 0.5,
                   "footer": True, "pageMarginIn": 1.0, "baseFontPx": 16.0,
                   "headingScale": 2.0}
# (low, high) per numeric layout key; None means "the chosen slide height".
LAYOUT_RANGES = {"slideWidthIn": (1.0, 56.0), "slideHeightIn": (1.0, 56.0),
                 "titleTopIn": (0.0, None), "pageMarginIn": (0.0, 4.0),
                 "baseFontPx": (8.0, 72.0), "headingScale": (1.0, 6.0)}


def _finite(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _effective(c):
    return c.weight * PRECEDENCE[source_type(c.source)]


def score(cands, kind):
    """Sum precedence-weighted evidence per value. The heaviest single contribution supplies
    the provenance (source and evidence) for that value."""
    contributions = {}
    for c in cands:
        if c.kind == kind:
            contributions.setdefault(c.value, []).append((c.source, c.evidence, _effective(c)))
    totals = {}
    for value, parts in contributions.items():
        parts.sort()  # fixed order, and math.fsum is exact, so input order cannot flip a tie
        best = min(parts, key=lambda p: (-p[2], p[0], p[1]))
        totals[value] = {"weight": math.fsum(p[2] for p in parts), "best": best[2],
                         "source": best[0], "evidence": best[1]}
    return totals


def ranked(totals):
    return sorted(totals.items(), key=lambda kv: (-kv[1]["weight"], str(kv[0])))


def cluster(totals):
    """Fold each color within DELTA_E_CLUSTER of a heavier one into it.
    Returns [(hex, entry)] heaviest first; entry["members"] lists every folded hex."""
    heads = []
    for hexv, entry in ranked(totals):
        for head_hex, head in heads:
            if color.delta_e(head_hex, hexv) < DELTA_E_CLUSTER:
                head["weight"] += entry["weight"]
                head["members"].append(hexv)
                break
        else:
            heads.append((hexv, dict(entry, members=[hexv])))
    return sorted(heads, key=lambda h: (-h[1]["weight"], h[0]))


def _pick_neutral(neutrals, light, exclude):
    pool = [h for h in neutrals if h[0] != exclude]

    def lum(h):
        return color.luminance(h[0])

    if light:
        preferred = [h for h in pool if lum(h) >= LIGHT_LUMINANCE]
        fallback = [h for h in pool if lum(h) >= MID_LUMINANCE]
        if preferred:
            return preferred[0]
        return max(fallback, key=lum) if fallback else None
    preferred = [h for h in pool if lum(h) < DARK_LUMINANCE]
    fallback = [h for h in pool if lum(h) < MID_LUMINANCE]
    if preferred:
        return preferred[0]
    return min(fallback, key=lum) if fallback else None


def _set(profile, role, value):
    section, key = role.split(".", 1)
    profile[section][key] = value


def _fix_contrast(profile, role, against, why):
    key = role.split(".", 1)[1]
    old = profile["colors"][key]
    new, changed = color.ensure_contrast(old, against, CONTRAST_TARGET)
    if changed:
        profile["colors"][key] = new
        profile["provenance"][role]["evidence"] += "; contrast-adjusted from %s" % old
        profile["adjustments"].append("%s changed from %s to %s so %s reaches %.1f:1"
                                      % (role, old, new, why, CONTRAST_TARGET))


def merge(cands):
    profile = {"colors": {}, "chart": [], "fonts": {}, "logo": None, "layout": {},
               "provenance": {}, "adjustments": [], "warnings": []}
    prov = profile["provenance"]

    def take(role, value, entry):
        _set(profile, role, value)
        prov[role] = {"source": entry["source"], "evidence": entry["evidence"],
                      "weight": round(entry["weight"], 3)}

    def fallback(role):
        _set(profile, role, DEFAULTS[role])
        prov[role] = {"source": "default", "evidence": "no candidate found"}
        profile["warnings"].append("WARNING: %s defaulted" % LABELS[role])

    def derive(role, value, how):
        _set(profile, role, value)
        prov[role] = {"source": "derived", "evidence": how}

    # Colors: cluster, split neutrals from hues, assign roles.
    heads = cluster(score(cands, "color"))
    neutrals = [h for h in heads if color.is_neutral(h[0])]
    chromatic = [h for h in heads if not color.is_neutral(h[0])]
    c = profile["colors"]

    bg = _pick_neutral(neutrals, light=True, exclude=None)
    if bg:
        take("colors.background", *bg)
    else:
        fallback("colors.background")
    tx = _pick_neutral(neutrals, light=False, exclude=c["background"])
    if tx:
        take("colors.text", *tx)
    else:
        fallback("colors.text")
    if chromatic:
        take("colors.primary", *chromatic[0])
    else:
        fallback("colors.primary")

    accents = []
    for hexv, entry in chromatic[1:]:
        if len(accents) == 3:
            break
        chosen = [c["primary"]] + [a[0] for a in accents]
        if all(color.hue_distance(hexv, other) >= ACCENT_HUE_GAP for other in chosen):
            accents.append((hexv, entry))
    for i in range(3):
        if i < len(accents):
            take("colors.accent%d" % (i + 1), *accents[i])
        else:
            c["accent%d" % (i + 1)] = None

    _fix_contrast(profile, "colors.text", c["background"], "text on background")
    _fix_contrast(profile, "colors.primary", WHITE, "white text on primary")

    derive("colors.textMuted", color.mix(c["text"], c["background"], 0.25),
           "text mixed 25% toward background")
    _fix_contrast(profile, "colors.textMuted", c["background"], "muted text on background")
    derive("colors.surface", color.mix(c["background"], c["text"], 0.05),
           "background mixed 5% toward text")
    derive("colors.divider", color.mix(c["background"], c["text"], 0.15),
           "background mixed 15% toward text")
    derive("colors.link", c["primary"], "same as primary")

    chart = [c["primary"]] + [c[k] for k in ("accent1", "accent2", "accent3") if c[k]]
    for t in CHART_TINTS:
        if len(chart) >= CHART_LEN:
            break
        chart.append(color.mix(c["primary"], WHITE, t))
    profile["chart"] = chart

    # Fonts: heaviest family per role; a missing role borrows the other one.
    families = ranked(score(cands, "font"))
    body = next(((v, e) for v, e in families if v[0] == "body"), None)
    heading = next(((v, e) for v, e in families if v[0] == "heading"), None)
    if body:
        take("fonts.body", body[0][1], body[1])
    elif heading:
        derive("fonts.body", heading[0][1], "no body font found; uses the heading font")
    else:
        fallback("fonts.body")
    if heading:
        take("fonts.heading", heading[0][1], heading[1])
    else:
        derive("fonts.heading", profile["fonts"]["body"],
               "no heading font found; uses the body font")

    # Logo: any SVG beats any raster; otherwise the heaviest candidate.
    logos = ranked(score(cands, "logo"))
    svgs = [kv for kv in logos if kv[0].lower().split("?")[0].endswith(".svg")]
    pick = svgs or logos
    if pick:
        profile["logo"] = pick[0][0]
        prov["logo"] = {"source": pick[0][1]["source"], "evidence": pick[0][1]["evidence"]}

    # Layout: heaviest candidate per key, else a marked default. Numbers that are not finite
    # are dropped and the rest clamped to a sane range, so brand.json stays valid JSON and the
    # templates can always be written.
    layout = profile["layout"]
    for key, default in LAYOUT_DEFAULTS.items():
        options = [x for x in cands if x.kind == "layout" and x.value[0] == key]
        if key in LAYOUT_RANGES:
            dropped = sorted({x.source for x in options if not _finite(x.value[1])})
            if dropped:
                profile["adjustments"].append("layout.%s ignored a non-finite value from %s"
                                              % (key, ", ".join(dropped)))
            options = [x for x in options if _finite(x.value[1])]
        if options:
            best = min(options, key=lambda x: (-_effective(x), str(x.value[1]), x.source, x.evidence))
            layout[key] = best.value[1]
            prov["layout." + key] = {"source": best.source, "evidence": best.evidence}
        else:
            layout[key] = default
            prov["layout." + key] = {"source": "default", "evidence": "no candidate found"}
        if key in LAYOUT_RANGES:
            low, high = LAYOUT_RANGES[key]
            high = layout["slideHeightIn"] if high is None else high
            value = float(layout[key])
            if not low <= value <= high:
                clamped = min(max(value, low), high)
                layout[key] = clamped
                prov["layout." + key]["evidence"] += "; clamped from %r" % value
                profile["adjustments"].append("layout.%s clamped from %r to %r (allowed %g to %g)"
                                              % (key, value, clamped, low, high))
    return profile
