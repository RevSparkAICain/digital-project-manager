"""Font-family helpers: pick the brand family out of a CSS stack, build a fallback stack."""
import re

GENERIC = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
           "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded", "-apple-system",
           "blinkmacsystemfont", "inherit", "initial", "unset", "revert", "emoji", "math"}
SERIF_HINTS = ("serif", "georgia", "times", "garamond", "merriweather", "cambria", "playfair")
SANS_STACK = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
SERIF_STACK = 'Georgia, Cambria, "Times New Roman", Times, serif'
MONO_STACK = 'ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace'
SAFE_PUNCT = set(" -._&+")
FAMILY_MAX = 64


def clean_family(name):
    """A family name reduced to letters, digits, spaces and - . _ & +, at most FAMILY_MAX
    characters (cut at a word boundary when one exists), or None when nothing is left.

    The name comes from untrusted files and lands in CSS, Office XML and the generated
    SKILL.md, so anything that could start markup there (quotes, backticks, brackets,
    parentheses, colons, slashes, semicolons) is dropped."""
    if not name:
        return None
    s = "".join(ch if ch.isalnum() or ch in SAFE_PUNCT else " " if ch.isspace() else ""
                for ch in name)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > FAMILY_MAX:
        cut = s.rfind(" ", 0, FAMILY_MAX + 1)
        s = (s[:cut] if cut > 0 else s[:FAMILY_MAX]).strip()
    return s or None


def first_family(stack):
    """The first named family in a CSS font-family value, or None when only generics remain."""
    for part in stack.split(","):
        raw = part.strip().strip("'\"").strip()
        if raw.lower().startswith("var("):  # checked before cleaning drops the parenthesis
            continue
        name = clean_family(raw)
        if name and name.lower() not in GENERIC:
            return name
    return None


def is_serif(family):
    f = family.lower()
    return "sans" not in f and any(hint in f for hint in SERIF_HINTS)


def web_stack(family):
    name = clean_family(family)
    if name is None:
        return SANS_STACK
    return '"%s", %s' % (name, SERIF_STACK if is_serif(name) else SANS_STACK)
