"""The one record every source adapter returns, plus source precedence."""
from collections import namedtuple

# kind "color":  value "#RRGGBB"
# kind "font":   value ("heading" or "body", family name)
# kind "logo":   value a local absolute path or an http(s) URL
# kind "layout": value (key, number or bool)
# weight:   evidence within one source; normalize() turns color and font weights into shares
# source:   "<type>:<name>", type a PRECEDENCE key, name a file basename or a URL
# evidence: short human-readable reason, copied into brand.json provenance
Candidate = namedtuple("Candidate", "kind value weight source evidence")

PRECEDENCE = {"template": 1.0, "pdf": 0.8, "web": 0.6, "image": 0.4}


class SourceError(Exception):
    """A source could not be read. extract.py logs the reason and moves on."""


def source_type(source):
    return source.split(":", 1)[0]


def normalize(cands):
    """Scale color and font weights so each kind sums to 1.0 within one source, so a long
    stylesheet cannot outvote a short template. Logo and layout weights are left alone."""
    totals = {}
    for c in cands:
        if c.kind in ("color", "font"):
            totals[c.kind] = totals.get(c.kind, 0.0) + c.weight
    out = []
    for c in cands:
        total = totals.get(c.kind)
        out.append(c._replace(weight=c.weight / total) if total else c)
    return out
