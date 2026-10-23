"""Measure a plain-language draft against the mechanical rules of the
plain-language-translation skill and print a JSON report.

Checks: reading grade (Flesch-Kincaid), average sentence length, paragraph
length, unexpanded acronyms, vague time phrases, banned words from the
house-style writing standard, and em dashes found by a raw byte scan.

Standard library only. Exit code 0 when every check passes, 1 otherwise.
"""

import argparse
import json
import os
import re
import sys

EM_DASH_BYTES = bytes([0xE2, 0x80, 0x94])
MAX_AVG_SENTENCE_WORDS = 20
MAX_PARAGRAPH_SENTENCES = 3
DEFAULT_ALLOW = ("AM", "PM", "IT")
# (label shown in the report, pattern). "soon" skips "as soon as".
VAGUE_TIME = (
    ("in the coming (days/weeks/months)", r"in the coming (?:days|weeks|months)"),
    ("in due course", r"in due course"),
    ("shortly", r"shortly"),
    ("soon", r"(?<!as )soon(?! as)"),
)
STANDARD_NAME = "writing-standard.md"
ROOT_MARKERS = ("pods", ".claude")
# Checked at each folder from the script's folder up to and including the
# project root, in this order: the installed house-style skill, then the
# repo's core pod copy.
STANDARD_RELS = (
    os.path.join(".claude", "skills", "house-style", STANDARD_NAME),
    os.path.join("pods", "core", "skills", "house-style", STANDARD_NAME),
)


# ---------------------------------------------------------------- text prep

def strip_markdown(text):
    """Return prose blocks (paragraphs) with markdown syntax removed.

    Headings, code fences, tables and HTML comments are dropped; blockquote
    markers, emphasis, inline code and link syntax are unwrapped. Each list
    item is its own block, so a list does not count toward the paragraph cap
    of the text around it, and an item without end punctuation is closed
    with a period so it counts as one sentence.
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    blocks = []
    state = {"lines": [], "item": False}

    def flush():
        if state["lines"]:
            block = " ".join(state["lines"])
            if state["item"] and not re.search(r"[.!?:]$", block):
                block += "."
            blocks.append(block)
        state["lines"] = []
        state["item"] = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|") or re.fullmatch(r"-{3,}", line):
            flush()
            continue
        line = re.sub(r"^>\s?", "", line)
        item = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if item:
            flush()
            state["item"] = True
            line = item.group(1)
        elif state["item"] and not raw[:1].isspace():
            flush()
        line = re.sub(r"`[^`]*`", "code", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = line.replace("**", "").replace("__", "")
        state["lines"].append(line)
    flush()
    return [b for b in blocks if b.strip()]


def split_sentences(paragraph):
    # Protect common abbreviations and decimals before splitting.
    protected = re.sub(r"\b(e\.g|i\.e|etc|vs|Mr|Ms|Dr|No)\.", lambda m: m.group(1) + "<DOT>", paragraph)
    protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", protected)
    parts = re.split(r"(?<=[.!?])[\"')\]]*\s+", protected)
    return [p.replace("<DOT>", ".").strip() for p in parts if re.search(r"[A-Za-z0-9]", p)]


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")


def words_of(text):
    return WORD_RE.findall(text)


def syllables(word):
    w = word.lower()
    if w.isdigit():
        return max(1, len(w) // 2)
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 1
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


# ---------------------------------------------------------------- checks

def spelled_out_before(prose, start, acronym):
    """True when the words just before position start begin with the
    acronym's letters, as in "optical character recognition (OCR)".

    Hyphenated words count as separate words ("point-of-sale (POS)").
    Digits in the acronym are not matched.
    """
    letters = [c.lower() for c in acronym if c.isalpha()]
    if not letters:
        return False
    words = re.findall(r"[A-Za-z0-9]+", prose[:start])
    if len(words) < len(letters):
        return False
    initials = [w[0].lower() for w in words[-len(letters):]]
    return initials == letters


def find_acronyms(prose, allow):
    """Return acronyms whose first use is not expanded.

    An acronym is a run of two to six capitals or digits starting with a
    capital, with an optional plural "s". It counts as expanded when its
    first use is written "(ABC)" directly after a phrase whose words start
    with the same letters. A bare "(ABC)" with no matching phrase does not
    count.
    """
    seen = {}
    for m in re.finditer(r"\(?\b[A-Z][A-Z0-9]{1,5}s?\b\)?", prose):
        token = m.group(0)
        core = token.strip("()")
        if core.endswith("s") and core[:-1].isupper():
            core = core[:-1]
        if not core.isupper() or core in allow or core in seen:
            continue
        wrapped = token.startswith("(") and token.endswith(")")
        seen[core] = wrapped and spelled_out_before(prose, m.start(), core)
    return sorted(k for k, expanded in seen.items() if not expanded)


def find_vague_time(prose):
    hits = []
    for label, pattern in VAGUE_TIME:
        count = len(re.findall(r"\b" + pattern + r"\b", prose, flags=re.I))
        if count:
            hits.append({"phrase": label, "count": count})
    return hits


def load_banned_words(standard_path):
    """Read the first column of the banned-words table in the writing standard.

    The table sits under a heading containing "Banned words". Rows are
    "| word | swap |"; the header row and the separator row are skipped.
    """
    with open(standard_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    words = []
    in_section = False
    for line in lines:
        if line.startswith("#"):
            in_section = "banned words" in line.lower()
            continue
        if not in_section or not line.startswith("|"):
            continue
        cell = line.strip("|").split("|")[0].strip()
        if not cell or set(cell) <= set("-: ") or cell.lower().startswith("banned"):
            continue
        words.append(cell.lower())
    return words


def find_banned(prose, banned):
    hits = []
    for word in banned:
        stem = re.escape(word)
        if word.endswith("e"):
            stem = re.escape(word[:-1]) + r"(?:e|es|ed|ing)"
        pattern = r"\b" + stem + r"(?:s|es|d|ed|ing|ly)?\b"
        count = len(re.findall(pattern, prose, flags=re.I))
        if count:
            hits.append({"word": word, "count": count})
    return hits


def project_root(start):
    """Return the nearest folder at or above start that holds pods/ or .claude/, or None."""
    folder = os.path.abspath(start)
    while True:
        if any(os.path.isdir(os.path.join(folder, marker)) for marker in ROOT_MARKERS):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def locate_standard(start):
    """Find the writing standard for a script that lives in folder start.

    From start up to and including the project root (the nearest folder
    that holds pods/ or .claude/), each folder is tried for the installed
    house-style copy, then the repo's pods/core copy; the walk stops at the
    project root, and with no project root no folder is tried. If no folder
    has one, the copy in the skill's own shared/ folder is used: shared/
    beside start, or start itself when the script sits in shared/. Returns
    None when none exists.
    """
    here = os.path.abspath(start)
    root = project_root(here)
    while root is not None:
        for rel in STANDARD_RELS:
            candidate = os.path.join(here, rel)
            if os.path.isfile(candidate):
                return candidate
        if here == root:
            break
        here = os.path.dirname(here)
    skill_copy = os.path.join(os.path.dirname(os.path.abspath(start)), "shared", STANDARD_NAME)
    return skill_copy if os.path.isfile(skill_copy) else None


def check(path, grade=8.0, allow=DEFAULT_ALLOW, standard=None):
    with open(path, "rb") as f:
        raw = f.read()
    em_dashes = raw.count(EM_DASH_BYTES)
    text = raw.decode("utf-8", errors="replace")
    paragraphs = strip_markdown(text)
    prose = " ".join(paragraphs)

    sentence_total = 0
    long_paragraphs = []
    for index, para in enumerate(paragraphs, start=1):
        n = len(split_sentences(para))
        sentence_total += n
        if n > MAX_PARAGRAPH_SENTENCES:
            long_paragraphs.append({"paragraph": index, "sentences": n})

    words = words_of(prose)
    word_total = len(words)
    syllable_total = sum(syllables(w) for w in words)
    if word_total and sentence_total:
        avg = word_total / sentence_total
        fk = 0.39 * avg + 11.8 * (syllable_total / word_total) - 15.59
    else:
        avg = 0.0
        fk = 0.0

    if standard:
        banned = load_banned_words(standard)
        banned_hits = find_banned(prose, banned)
        banned_source = "checked"
    else:
        banned_hits = []
        banned_source = "skipped: writing standard not found"

    report = {
        "file": os.path.basename(path),
        "words": word_total,
        "sentences": sentence_total,
        "syllables": syllable_total,
        "avg_sentence_words": round(avg, 1),
        "fk_grade": round(fk, 1),
        "target_grade": grade,
        "grade_ok": round(fk, 1) <= grade,
        "avg_sentence_ok": round(avg, 1) < MAX_AVG_SENTENCE_WORDS,
        "long_paragraphs": long_paragraphs,
        "unexpanded_acronyms": find_acronyms(prose, set(allow)),
        "vague_time": find_vague_time(prose),
        "banned_words": banned_source,
        "banned_hits": banned_hits,
        "em_dashes": em_dashes,
    }
    failed = (
        not report["grade_ok"]
        or not report["avg_sentence_ok"]
        or report["long_paragraphs"]
        or report["unexpanded_acronyms"]
        or report["vague_time"]
        or report["banned_hits"]
        or report["em_dashes"]
    )
    report["status"] = "fail" if failed else "pass"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("draft", help="path to a .md or .txt draft")
    parser.add_argument("--grade", type=float, default=8.0,
                        help="target reading grade (8 all staff, 10 IT and leaders)")
    parser.add_argument("--allow", default=",".join(DEFAULT_ALLOW),
                        help="comma-separated acronyms that need no expansion")
    parser.add_argument("--standard", default=None,
                        help="path to the house-style writing-standard.md")
    parser.add_argument("--out", default=None, help="also write the JSON report here")
    args = parser.parse_args(argv)

    standard = args.standard or locate_standard(os.path.dirname(os.path.abspath(__file__)))
    allow = tuple(a.strip() for a in args.allow.split(",") if a.strip())
    report = check(args.draft, grade=args.grade, allow=allow, standard=standard)
    out = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(out + "\n")
    print(out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
