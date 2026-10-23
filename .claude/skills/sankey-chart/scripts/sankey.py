"""Draw a Sankey spec (written by build_spec.py, or by hand) as an image.

    python scripts/sankey.py <spec> <out_png> [--palette NAME] [--brand PATH]

Every color comes from a palette in assets/palette.json, resolved against the brand file, and
the typeface is the brand's fonts.office. Nodes stay where the spec lists them; the script
never reorders anything. Structural mistakes in the spec are gathered and reported together
before any drawing starts. references/spec-format.md describes the spec keys.
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path as FilePath
from textwrap import fill as wrap_text

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand_palette import guard_path, load_palette  # noqa: E402

PROG = "sankey"

# Node bars and bands (axis units; the plot height is 1).
BAR_W = 0.016
GAP = 0.018
BAND_ALPHA = 0.82
CURVE_PULL = 0.42

# Text wrapping, in characters per line.
FOOTER_WIDTH = 120
NOTE_WIDTH = 30

# Label and heading offsets from the bars.
LABEL_PAD_LEFT = 0.008
LABEL_PAD_RIGHT = 0.009
HEADING_Y = -0.045

# Bracket gutter.
BRACKET_OFFSET = 0.030
TICK = 0.011
BRACKET_TEXT_GAP = 0.014
COUNT_DROP = 0.032
NOTE_DROP = 0.052

# Plot limits; the y axis runs downward.
X_MIN = -0.13
X_MAX_PLAIN = 1.06
X_MAX_BRACKETS = 1.40
Y_LOW = 1.06
Y_HIGH = -0.10

# Output image.
FIG_SIZE = (16, 9)
DPI = 120
SAVE_PAD = 0.35

NEEDED_ROLES = ("background", "text", "text_muted", "text_tertiary", "neutral")


def reject(lines):
    sys.exit("Spec rejected:\n" + "\n".join("  - " + line for line in lines))


# ------------------------------------------------------------------ font

def pick_font(face):
    """Return the rcParams family list for the whole figure."""
    stock = matplotlib.rcParamsDefault["font.sans-serif"][0]
    if not face:
        return [stock]
    try:
        font_manager.findfont(font_manager.FontProperties(family=face),
                              fallback_to_default=False)
    except ValueError:
        print("NOTE: font '%s' is not installed here, so matplotlib's default face is "
              "used instead; recheck that every label still fits." % face, file=sys.stderr)
        return [stock]
    return [face, stock]


# ------------------------------------------------------------------ color

class ColorBook(object):
    """Turns a spec color value (role, cat:<n>, #hex or blank) into a drawable color."""

    def __init__(self, roles, series):
        self.roles = roles
        self.series = series

    def get(self, value, default):
        if not value:
            return default
        if value.startswith("#"):
            return value
        if value.startswith("cat:"):
            if not self.series:
                return default
            try:
                index = int(value[4:])
            except ValueError:
                sys.exit("Spec rejected: color '%s' needs a whole number after cat:." % value)
            return self.series[index % len(self.series)]
        if value in self.roles:
            return self.roles[value]
        sys.exit("Spec rejected: unknown color role '%s'. The palette knows these roles: %s. "
                 "Literal forms cat:<n> and #RRGGBB are accepted too."
                 % (value, ", ".join(sorted(self.roles))))


# ------------------------------------------------------------------ validation

def structure_problems(spec):
    """Every structural fault in the spec, as message lines (empty when sound)."""
    columns = spec["columns"]
    problems = []

    tally = Counter(node for column in columns for node in column)
    repeated = sorted(node for node, count in tally.items() if count > 1)
    if repeated:
        problems.append("listed more than once in the columns: "
                        + ", ".join("'%s'" % node for node in repeated))

    for link in spec["links"]:
        src, dst = link["source"], link["target"]
        for end in (src, dst):
            if end not in tally:
                problems.append("link %s -> %s: '%s' is not in any column" % (src, dst, end))

    final = columns[-1] if columns else []
    slot = {node: pos for pos, node in enumerate(final)}
    for group in spec.get("groups") or []:
        label = group["label"]
        members = group["nodes"]
        strays = [n for n in members if n not in slot]
        if strays:
            problems.append("group '%s' names nodes that are not in the final column: %s"
                            % (label, ", ".join("'%s'" % n for n in strays)))
            continue
        if not members:
            continue
        spots = sorted(set(slot[n] for n in members))
        if spots[-1] - spots[0] != len(spots) - 1:
            problems.append("group '%s' has members that are not contiguous; put them next "
                            "to each other in the last column, or break it into two groups"
                            % label)
    return problems


# ------------------------------------------------------------------ sizing and layout

def node_sizes(columns, links):
    """Size per node (larger of inflow and outflow), printing a warning for any node whose
    two sides are both nonzero and disagree."""
    inflow = {}
    outflow = {}
    for link in links:
        outflow[link["source"]] = outflow.get(link["source"], 0) + link["value"]
        inflow[link["target"]] = inflow.get(link["target"], 0) + link["value"]
    sizes = {}
    notices = []
    for column in columns:
        for node in column:
            took, gave = inflow.get(node, 0), outflow.get(node, 0)
            sizes[node] = max(took, gave)
            if took and gave and took != gave:
                notices.append("WARNING: node '%s' takes in %s but sends out %s; the larger "
                               "is drawn." % (node, took, gave))
    for line in notices:
        print(line, file=sys.stderr)
    return sizes


def place_nodes(columns, sizes, scale):
    """Top and bottom of every node, columns centered in the unit height."""
    spans = {}
    for column in columns:
        height = sum(sizes[n] * scale for n in column) + GAP * max(len(column) - 1, 0)
        cursor = (1.0 - height) / 2.0
        for node in column:
            bottom = cursor + sizes[node] * scale
            spans[node] = (cursor, bottom)
            cursor = bottom + GAP
    return spans


def band_path(x0, top0, x1, top1, thickness):
    pull = CURVE_PULL * (x1 - x0)
    bot0, bot1 = top0 + thickness, top1 + thickness
    points = [(x0, top0), (x0 + pull, top0), (x1 - pull, top1), (x1, top1),
              (x1, bot1), (x1 - pull, bot1), (x0 + pull, bot0), (x0, bot0), (x0, top0)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    return Path(points, codes)


# ------------------------------------------------------------------ drawing

def draw_brackets(ax, groups, final, sizes, spans, paint, roles):
    total = sum(sizes[n] for n in final)
    spine_x = 1.0 + BAR_W + BRACKET_OFFSET
    text_x = spine_x + TICK + BRACKET_TEXT_GAP
    muted = {"color": roles["text_muted"], "fontsize": 12}
    italic = {"color": roles["text_tertiary"], "fontsize": 10.5, "style": "italic",
              "linespacing": 1.35}
    for group, color in zip(groups, paint):
        wanted = set(group["nodes"])
        members = [n for n in final if n in wanted]
        if not members:
            continue
        top = min(spans[n][0] for n in members)
        bottom = max(spans[n][1] for n in members)
        middle = (top + bottom) / 2.0
        value = sum(sizes[n] for n in members)
        share = round(100.0 * value / total) if total else 0

        stroke = {"zorder": 5, "color": color, "solid_capstyle": "butt", "linewidth": 2.0}
        for xs, ys in (([spine_x, spine_x], [top, bottom]),
                       ([spine_x - TICK, spine_x], [top, top]),
                       ([spine_x - TICK, spine_x], [bottom, bottom]),
                       ([spine_x, spine_x + TICK], [middle, middle])):
            ax.plot(xs, ys, **stroke)

        place = {"ha": "left", "zorder": 5}
        heading = {"color": color, "fontsize": 15, "fontweight": "bold"}
        ax.text(text_x, middle, group["label"], va="baseline", **dict(place, **heading))
        ax.text(text_x, middle + COUNT_DROP, "%s of %s   %d%%" % (value, total, share),
                va="baseline", **dict(place, **muted))
        note = group.get("note") or ""
        if note:
            ax.text(text_x, middle + NOTE_DROP, wrap_text(note, NOTE_WIDTH), va="top",
                    **dict(place, **italic))


def caption_rows(spec, roles):
    """(text, x, y, style) for each caption the spec fills in."""
    footer = spec.get("footer")
    table = [
        (spec.get("title"), 0.055, 0.955,
         {"fontsize": 25, "fontweight": "bold", "color": roles["text"]}),
        (spec.get("subtitle"), 0.055, 0.918,
         {"fontsize": 13.5, "color": roles["text_muted"]}),
        (wrap_text(footer, FOOTER_WIDTH) if footer else footer, 0.055, 0.018,
         {"va": "bottom", "fontsize": 10.5, "color": roles["text_tertiary"],
          "linespacing": 1.3}),
        (spec.get("prepared_by"), 0.945, 0.018,
         {"ha": "right", "va": "bottom", "fontsize": 10.5, "color": roles["text_tertiary"]}),
    ]
    return [row for row in table if row[0]]


def render(spec, out_png, palette_flag, brand_path):
    problems = structure_problems(spec)
    if problems:
        reject(problems)

    chosen_palette = palette_flag or spec.get("palette") or None
    roles, series, fonts = load_palette(chosen_palette, brand_path)
    families = pick_font(fonts.get("body") or "")
    missing = [role for role in NEEDED_ROLES if role not in roles]
    if missing:
        sys.exit("%s: the palette defines no %s role" % (PROG, ", ".join(missing)))
    book = ColorBook(roles, series)

    columns = spec["columns"]
    links = spec["links"]
    groups = spec.get("groups")
    group_list = groups if isinstance(groups, list) else []
    spec_colors = spec.get("colors") or {}
    labels = spec.get("labels") or {}

    fill = {}
    for column in columns:
        for node in column:
            fill[node] = book.get(spec_colors.get(node), roles["neutral"])
    bracket_paint = [book.get(g.get("color"), roles["text"]) for g in group_list]

    sizes = node_sizes(columns, links)
    grand = max(sum(sizes[n] for n in column) for column in columns) if columns else 0
    if grand <= 0:
        reject(["every link value is zero, so there is nothing to draw"])

    widest = max(len(column) - 1 for column in columns)
    scale = (1.0 - GAP * widest) / grand
    spans = place_nodes(columns, sizes, scale)

    count = len(columns)
    col_x = [(i / float(count - 1)) if count > 1 else 0.0 for i in range(count)]
    where = {}
    rank = {}
    for col_index, column in enumerate(columns):
        for pos, node in enumerate(column):
            where[node] = col_index
            rank[node] = pos
    given_sides = spec.get("label_sides")
    if given_sides:
        on_left = [given_sides[i] == "left" for i in range(count)]
    else:
        on_left = [i > 0 for i in range(count)]

    background = roles["background"]
    with matplotlib.rc_context({"font.family": "sans-serif", "font.sans-serif": families}):
        fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
        fig.patch.set_facecolor(background)
        ax.set_facecolor(background)

        ordered = sorted(links, key=lambda k: (where[k["source"]], rank[k["source"]],
                                               rank[k["target"]]))
        leave = {n: spans[n][0] for n in spans}
        arrive = {n: spans[n][0] for n in spans}
        by_target = spec.get("color_by", "target") == "target"
        for link in ordered:
            value = link["value"]
            if value <= 0:
                continue
            src, dst = link["source"], link["target"]
            thick = value * scale
            path = band_path(col_x[where[src]] + BAR_W, leave[src], col_x[where[dst]],
                             arrive[dst], thick)
            leave[src] += thick
            arrive[dst] += thick
            ax.add_patch(PathPatch(path, facecolor=fill[dst] if by_target else fill[src],
                                   edgecolor="none", linewidth=0, alpha=BAND_ALPHA,
                                   zorder=1))

        halo = {"boxstyle": "square,pad=0.24", "facecolor": background, "edgecolor": "none",
                "alpha": 0.88}
        for col_index, column in enumerate(columns):
            x = col_x[col_index]
            first = col_index == 0
            for node in column:
                top, bottom = spans[node]
                ax.add_patch(Rectangle((x, top), BAR_W, bottom - top, facecolor=fill[node],
                                       edgecolor="none", linewidth=0, zorder=2))
                text = "%s  %s" % (labels.get(node, node), sizes[node])
                if on_left[col_index]:
                    tx, align = x - LABEL_PAD_LEFT, "right"
                else:
                    tx, align = x + BAR_W + LABEL_PAD_RIGHT, "left"
                ax.text(tx, (top + bottom) / 2.0, text, ha=align, va="center",
                        fontsize=15 if first else 13,
                        fontweight="bold" if first else "normal", color=roles["text"],
                        zorder=3, bbox=halo)

        draw_brackets(ax, group_list, columns[-1], sizes, spans, bracket_paint, roles)

        for col_index, heading in enumerate(spec.get("column_titles") or []):
            x = col_x[col_index]
            if on_left[col_index]:
                hx, align = x - LABEL_PAD_LEFT, "right"
            else:
                hx, align = x + BAR_W, "left"
            ax.text(hx, HEADING_Y, heading, ha=align, va="bottom", fontsize=12,
                    fontweight="bold", color=roles["text_muted"])

        ax.set_xlim(X_MIN, X_MAX_BRACKETS if group_list else X_MAX_PLAIN)
        ax.set_ylim(Y_LOW, Y_HIGH)
        ax.axis("off")

        for text, x, y, style in caption_rows(spec, roles):
            fig.text(x, y, text, **style)

        fig.savefig(out_png, dpi=DPI, bbox_inches="tight", pad_inches=SAVE_PAD,
                    facecolor=background)
        plt.close(fig)


# ------------------------------------------------------------------ CLI

def parse_args(argv):
    parser = argparse.ArgumentParser(prog="sankey.py",
                                     description="Draw a Sankey chart image from a spec file.")
    parser.add_argument("spec", help="spec JSON to draw")
    parser.add_argument("out_png", help="image file to write")
    parser.add_argument("--palette", default=None,
                        help="palette from assets/palette.json; wins over the spec's palette")
    parser.add_argument("--brand", default=None,
                        help="brand JSON file; default is the usual brand lookup order")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    spec_path = guard_path(args.spec, PROG)
    out_png = guard_path(args.out_png, PROG)
    brand_path = guard_path(args.brand, PROG)
    try:
        spec = json.loads(FilePath(spec_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("%s: cannot read spec %s: %s" % (PROG, spec_path, exc))
    try:
        render(spec, out_png, args.palette, brand_path)
    except (AttributeError, KeyError, IndexError, TypeError, ValueError) as exc:
        sys.exit("%s: cannot render %s (%s: %s)" % (PROG, spec_path, type(exc).__name__, exc))
    print(args.out_png)


if __name__ == "__main__":
    main()
