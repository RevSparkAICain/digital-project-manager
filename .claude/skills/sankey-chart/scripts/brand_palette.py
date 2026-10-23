"""Shared helpers for the sankey-chart scripts: where the brand file is, how palette
recipes turn into colors, and the Windows check for drive paths written the MSYS way.

This is a library. Importing it only defines names; it never prints or writes a file.
Every failure ends the process through sys.exit with a one-line reason (exit status 1).
Standard library only.
"""
import json
import os
import re
import sys

# A folder holding either of these directories is the top of a project. The brand
# walk-up never looks above it.
ROOT_MARKERS = ("pods", ".claude")

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)

# Brand copy that ships with the skill; the last place the finder looks.
SHARED_BRAND = os.path.join(_SKILL_DIR, "shared", "brand.json")

_PALETTE_JSON = os.path.join(_SKILL_DIR, "assets", "palette.json")
_DEFAULT_PALETTE_NAME = "restrained"
_WHITE = "#FFFFFF"
_BLACK = "#000000"

# "/x/..." where x is one ASCII letter: a Git Bash drive path that Windows Python would
# read as a folder under the current drive's root.
_DRIVE_IN_MSYS_FORM = re.compile(r"/([A-Za-z])/")


def _read_json(path):
    """Parse a UTF-8 JSON file."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# ------------------------------------------------------------------ project and brand file

def project_root(start):
    """Nearest folder, from start upward and start included, that has a pods/ or .claude/
    directory. Returns its absolute path, or None when the top of the disk is reached."""
    here = os.path.abspath(start)
    while True:
        for marker in ROOT_MARKERS:
            if os.path.isdir(os.path.join(here, marker)):
                return here
        above = os.path.dirname(here)
        if above == here:
            return None
        here = above


def _walk_to_root(origin, root):
    """Folders from origin up to and including root, nearest first."""
    stop = os.path.normcase(root)
    here = origin
    while True:
        yield here
        if os.path.normcase(here) == stop:
            return
        above = os.path.dirname(here)
        if above == here:
            return
        here = above


def _must_exist(path, who):
    """Return a brand path the user asked for, or stop when nothing is there."""
    if os.path.exists(path):
        return path
    sys.exit("The brand file %s does not exist: %s" % (who, path))


def _fallback_candidates(start):
    """Ordered places to try when no path was named: brand/brand.json in each folder from
    start up to the project root (none when there is no root), then the shared copy."""
    origin = os.path.abspath(start if start else _SCRIPTS_DIR)
    root = project_root(origin)
    places = []
    if root is not None:
        places = [os.path.join(folder, "brand", "brand.json")
                  for folder in _walk_to_root(origin, root)]
    places.append(SHARED_BRAND)
    return places


def find_brand_file(explicit=None, start=None):
    """Pick the brand file. First hit wins:

    1. explicit (a --brand value), returned as given; a missing file stops the run;
    2. the BRAND_JSON environment variable when non-empty, same rule;
    3. brand/brand.json in start or any folder above it, up to the project root;
    4. the skill's shared/brand.json;
    5. otherwise stop with instructions.
    """
    if explicit:
        return _must_exist(explicit, "you named")
    env_choice = os.environ.get("BRAND_JSON")
    if env_choice:
        return _must_exist(env_choice, "named by BRAND_JSON")
    for candidate in _fallback_candidates(start):
        if os.path.exists(candidate):
            return candidate
    sys.exit("No brand file found (looked for a project brand/brand.json, then %s). "
             "Set BRAND_JSON or give --brand <path>." % SHARED_BRAND)


def load_brand(explicit=None):
    """Return (brand dict, path it came from)."""
    brand_file = find_brand_file(explicit)
    return _read_json(brand_file), brand_file


def lookup(brand, dotted):
    """Value at a dot-separated key path, or None. An entry shaped {"value": ...} is read
    through its value (one level)."""
    found = brand
    for part in dotted.split("."):
        found = found.get(part) if isinstance(found, dict) else None
        if found is None:
            return None
    if isinstance(found, dict) and "value" in found:
        return found["value"]
    return found


# ------------------------------------------------------------------ palettes

def load_palette(name=None, brand_path=None):
    """Resolve a named palette against the brand file.

    Returns (roles, categorical, fonts): roles maps each role to a color in the order the
    palette file lists them; categorical is a list of colors (may be empty); fonts holds
    exactly 'body' and 'heading', each a face name or ''.
    """
    palette_doc = _read_json(_PALETTE_JSON)
    defined = {}
    for key, entry in palette_doc.get("palettes", {}).items():
        if not key.startswith("_"):
            defined[key] = entry
    wanted = name or palette_doc.get("default") or _DEFAULT_PALETTE_NAME
    if wanted not in defined:
        sys.exit("Unknown palette '%s'. Available: %s"
                 % (wanted, ", ".join(sorted(defined))))

    brand, _ = load_brand(brand_path)
    chosen = defined[wanted]

    roles = {}
    for role, recipe in chosen.get("roles", {}).items():
        if not role.startswith("_"):
            roles[role] = _resolve(brand, recipe, "palette '%s', role '%s'" % (wanted, role))

    series_where = "palette '%s', categorical" % wanted
    categorical = [_resolve(brand, recipe, series_where)
                   for recipe in chosen.get("categorical") or []]

    office_face = lookup(brand, "fonts.office") or ""
    title_face = lookup(brand, "fonts.officeHeading") or office_face
    faces = dict(body=office_face, heading=title_face)
    return roles, categorical, faces


# ------------------------------------------------------------------ recipes

def _channels(color):
    """(red, green, blue) from '#RRGGBB', 'RRGGBB' or the 3-digit short form."""
    digits = color.lstrip("#")
    if len(digits) == 3:
        digits = "".join(ch + ch for ch in digits)
    return tuple(int(digits[start:start + 2], 16) for start in (0, 2, 4))


def _mix(color, toward, amount):
    """Move each channel of color toward another color by amount (0 keeps it, 1 reaches
    it). Python's round() settles halves to even; results are clamped to 0..255."""
    def step(start, end):
        return min(255, max(0, round(start + (end - start) * amount)))

    red, green, blue = (step(a, b) for a, b in zip(_channels(color), _channels(toward)))
    return "#{:02X}{:02X}{:02X}".format(red, green, blue)


def _is_hex_color(value):
    return isinstance(value, str) and value.startswith("#")


def _resolve(brand, recipe, where):
    """Turn one recipe into one uppercase color string."""
    if isinstance(recipe, str):
        recipe = {"ref": recipe}
    elif not isinstance(recipe, dict):
        recipe = {}
    ref = recipe.get("ref")
    value = lookup(brand, ref) if ref else None

    if not _is_hex_color(value):
        if "or" in recipe:
            # The fallback stands on its own: this recipe's tint and shade do not apply.
            return _resolve(brand, recipe["or"], where)
        sys.exit("%s: brand value %r is not set to a #hex color and the recipe has no "
                 "'or' fallback." % (where, ref))

    color = value
    for key, target in (("tint", _WHITE), ("shade", _BLACK)):
        amount = recipe.get(key)
        if amount:
            color = _mix(color, target, float(amount))
    return color.upper()


# ------------------------------------------------------------------ path guard

def guard_path(p, prog="sankey-chart"):
    """Return p unchanged, unless this is Windows and p looks like /c/... for any drive
    letter; then stop with a hint to write the drive form instead."""
    if os.name != "nt" or not p:
        return p
    hit = _DRIVE_IN_MSYS_FORM.match(p)
    if hit is None:
        return p
    drive = hit.group(1).upper()
    sys.exit("%s: path '%s' is in MSYS form. On Windows it would point under the root of "
             "whichever drive is current, not at drive %s. Write it as %s:/%s instead."
             % (prog, p, drive, drive, p[3:]))
