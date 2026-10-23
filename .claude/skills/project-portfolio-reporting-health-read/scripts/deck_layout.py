"""Deck geometry for build_deck.py: slide frame, type sizes, the measured card capacity, the
wrapped-text height estimate and the pagination rules. No CLI and no third-party imports.

All positions are in points on a 960 x 540 pt slide (13.333 x 7.5 in). The numbers recorded
in references/deck-structure.md come from this file; tests assert both agree.
"""
import math

SLIDE_W = 960
SLIDE_H = 540
MARGIN = 40
CONTENT_W = SLIDE_W - 2 * MARGIN

LINE_FACTOR = 1.2      # line height as a multiple of the font size
WIDTH_FACTOR = 0.55    # average character width as a multiple of the font size
BOLD_FACTOR = 0.6      # the same for bold text

TITLE_PT = 32
LABEL_PT = 12
HEADING_PT = 16
BODY_PT = 14
SMALL_PT = 12
TABLE_PT = 11
CAPTION_PT = 10
GRADE_PT = 72

LABEL_TOP = 16
LABEL_H = 16
TITLE_TOP = 34
TITLE_H = 44
DIVIDER_TOP = 82
BODY_TOP = 92
BODY_BOTTOM = 500
FOOTER_TOP = 512
FOOTER_H = 14
BLOCK_GAP = 6

# Needs attention: one card per exception, then the rollup and closing lines below the band.
CARD_TOP = BODY_TOP
CARD_PAD = 8
CARD_NAME_PT = 14
CARD_LINE_PT = 12
CARD_H = 2 * CARD_PAD + CARD_NAME_PT * LINE_FACTOR + 2 * CARD_LINE_PT * LINE_FACTOR
CARD_GAP = 10
FOOT_LINE_H = 2 * SMALL_PT * LINE_FACTOR + 2   # rollup and closing lines, two lines each
PANEL_GAP = 8
ATTENTION_BAND_BOTTOM = BODY_BOTTOM - (2 * FOOT_LINE_H + 3 * PANEL_GAP)

# Tables: scorecard and corrections.
CELL_PAD_H = 4
CELL_PAD_V = 3
CAPTION_H = 2 * CAPTION_PT * LINE_FACTOR + 2
TABLE_BAND_BOTTOM = BODY_BOTTOM - CAPTION_H - PANEL_GAP
SCORECARD_COLUMNS = (("Project", 175), ("Lead", 80), ("Latest status", 110), ("Color", 50),
                     ("Alignment", 90), ("Newness", 85), ("Records", 70), ("Grade", 45),
                     ("Evidence", 175))
CORRECTION_COLUMNS = (("Project", 220), ("Who corrects", 170), ("Correction", 490))

# Grade slide.
CHIP_W = 170
CHIP_H = 150
RIGHT_X = MARGIN + CHIP_W + 20
RIGHT_W = SLIDE_W - MARGIN - RIGHT_X
PANEL_PAD = 10


class LayoutError(Exception):
    """Content cannot be placed inside the slide: exit 4."""


def capacity(band, height, gap):
    """The largest whole number of items whose tops plus heights stay inside the band."""
    return int(math.floor((band + gap) / (height + gap)))


def attention_capacity():
    return capacity(ATTENTION_BAND_BOTTOM - CARD_TOP, CARD_H, CARD_GAP)


def chars_per_line(width, size, bold=False):
    factor = BOLD_FACTOR if bold else WIDTH_FACTOR
    return max(1, int(width / (factor * size)))


def _lines(words, cpl):
    lines, current = 0, None
    for word in words:
        while len(word) > cpl:
            if current is not None:
                lines += 1
                current = None
            lines += 1
            word = word[cpl:]
        if not word:
            continue
        if current is None:
            current = len(word)
        elif current + 1 + len(word) <= cpl:
            current += 1 + len(word)
        else:
            lines += 1
            current = len(word)
    if current is not None:
        lines += 1
    return max(lines, 1)


def wrap_count(text, width, size, bold=False):
    """Estimated wrapped line count: greedy word wrap at chars_per_line, one paragraph per
    newline, an empty paragraph counting one line."""
    cpl = chars_per_line(width, size, bold)
    return sum(_lines(part.split(), cpl) for part in (text or "").split("\n"))


def text_height(text, width, size, bold=False):
    return wrap_count(text, width, size, bold) * size * LINE_FACTOR


def row_height(cells, widths, size, pad_h=CELL_PAD_H, pad_v=CELL_PAD_V):
    """A table row's height from its tallest wrapped cell plus the cell padding."""
    tallest = max(wrap_count(text, width - 2 * pad_h, size) for text, width in zip(cells, widths))
    return tallest * size * LINE_FACTOR + 2 * pad_v


def paginate_rows(heights, header, top, bottom):
    """Split rows into pages, the header repeated on each; a page continues when the next
    row would cross the band bottom."""
    band = bottom - top
    pages, current, used = [], [], header
    for index, height in enumerate(heights):
        if header + height > band:
            raise LayoutError("a table row of %.0fpt cannot fit a %.0fpt band" % (height, band))
        if used + height > band:
            pages.append(current)
            current, used = [], header
        current.append(index)
        used += height
    if current or not pages:
        pages.append(current)
    return pages


def place_blocks(blocks, top, bottom, repeat=None):
    """Flow blocks down the band and return pages of (block, y).

    A block is a dict with "h" (height) and optional "gap" (space above it, dropped at a page
    top), "group" (keep the run of blocks sharing it together when it fits a fresh page),
    "keep_next" (keep it with the next block) and "context" (a key passed to repeat(), which
    returns blocks to place at the top of a continuation page). Nothing shrinks: a block
    taller than a whole page raises LayoutError.
    """
    pages = [[]]
    state = {"y": top, "content": False}
    band = bottom - top

    def need(block):
        return block["h"] + (block.get("gap", 0) if pages[-1] else 0)

    def new_page(next_block):
        pages.append([])
        state["y"] = top
        state["content"] = False
        if repeat and next_block.get("context") is not None and not next_block.get("head"):
            for extra in repeat(next_block["context"]):
                pages[-1].append((extra, state["y"]))
                state["y"] += extra["h"]

    i = 0
    while i < len(blocks):
        block = blocks[i]
        room = bottom - state["y"]
        group = block.get("group")
        if state["content"] and group is not None and \
                (i == 0 or blocks[i - 1].get("group") != group):
            j, total = i, 0
            while j < len(blocks) and blocks[j].get("group") == group:
                total += blocks[j]["h"] + (blocks[j].get("gap", 0) if j > i else 0)
                j += 1
            if total > room and total <= band:
                new_page(block)
                continue
        if state["content"] and block.get("keep_next") and i + 1 < len(blocks):
            chain, j = need(block), i
            while blocks[j].get("keep_next") and j + 1 < len(blocks):
                j += 1
                chain += blocks[j]["h"] + blocks[j].get("gap", 0)
            if chain > room:
                new_page(block)
                continue
        if need(block) > room:
            if not state["content"]:
                raise LayoutError("a block of %.0fpt cannot fit a %.0fpt band"
                                  % (block["h"], bottom - state["y"]))
            new_page(block)
            continue
        state["y"] += block.get("gap", 0) if pages[-1] else 0
        pages[-1].append((block, state["y"]))
        state["y"] += block["h"]
        state["content"] = True
        i += 1
    return pages
