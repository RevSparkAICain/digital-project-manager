"""Shared helpers for grade_portfolio.py and build_deck.py: input loading, the config check,
the roadmap pair file, text normalization, contrast and the brand lookup. No CLI.

Standard library only. Every problem raises InputError with one readable sentence; the
calling script turns it into one stderr line and exit 1.
"""
import datetime
import json
import os
import re
import tempfile

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(_SCRIPT_DIR)
SHARED_BRAND = os.path.join(SKILL_DIR, "shared", "brand.json")
ROOT_MARKERS = ("pods", ".claude")

TASK_STATES = ("not_started", "in_progress", "complete", "closed")
ROADMAP_STATES = ("active", "complete", "not_started", "held")
COLORS = ("green", "amber", "red")
BUCKET_KEYS = ("parked", "no_date_no_owner", "overdue", "no_owner", "not_started_past_due",
               "scaffold", "open_raid", "past_due_open", "open_in_finished")
POINT_KEYS = ("aging", "stale", "absent", "repeated", "placeholder", "misaligned", "minor",
              "conflicting")
BAND_KEYS = ("A", "B", "C", "D")
LINE_KEYS = ("f_currency_fail_over", "d_currency_fail_over", "d_color_fail_over",
             "c_currency_fail_over", "c_newness_fail_over", "c_color_or_records_over")


class InputError(Exception):
    """A malformed or unreadable input: exit 1."""


# ----------------------------------------------------------------- files

def load_json(path, label):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except OSError as exc:
        raise InputError("cannot read %s %s: %s" % (label, path, exc.strerror or exc))
    except ValueError as exc:
        raise InputError("%s %s is not valid JSON: %s" % (label, path, exc))


def write_json_atomic(path, data):
    folder = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(folder, exist_ok=True)
        handle, temp = tempfile.mkstemp(prefix=".findings-", suffix=".tmp", dir=folder)
    except OSError as exc:
        raise InputError("cannot write to %s: %s" % (folder, exc.strerror or exc))
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=True)
            fh.write("\n")
        os.replace(temp, path)
    except BaseException:
        if os.path.exists(temp):
            os.remove(temp)
        raise


def write_bytes_atomic(path, payload):
    folder = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(folder, exist_ok=True)
        handle, temp = tempfile.mkstemp(prefix=".deck-", suffix=".tmp", dir=folder)
    except OSError as exc:
        raise InputError("cannot write to %s: %s" % (folder, exc.strerror or exc))
    try:
        with os.fdopen(handle, "wb") as fh:
            fh.write(payload)
        os.replace(temp, path)
    except BaseException:
        if os.path.exists(temp):
            os.remove(temp)
        raise


def parse_date(value, label):
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        raise InputError("%s must be a YYYY-MM-DD date, got %r" % (label, value))
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise InputError("%s is not a real calendar date: %s" % (label, value))


# ----------------------------------------------------------------- config

def _get(data, dotted):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise InputError("config: missing key %s" % dotted)
        node = node[part]
    return node


def _is_type(value, kind):
    if kind is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if kind is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, kind)


CONFIG_KEYS = (
    ("config_version", str), ("title", str), ("executive_reader_role", str),
    ("prepared_by", str), ("grade_statement.measures", str),
    ("grade_statement.does_not_measure", str), ("tracker.kind", str),
    ("tracker.workspace_id", str), ("tracker.space_id", str),
    ("tracker.folders.active.id", str), ("tracker.folders.active.name", str),
    ("tracker.folders.completed.id", str), ("tracker.folders.completed.name", str),
    ("tracker.folders.not_started.id", str), ("tracker.folders.not_started.name", str),
    ("tracker.roadmap_list_id", str), ("tracker.list_url_template", str),
    ("tracker.status_task_match", str), ("tracker.comments_limit", int),
    ("tracker.bot_authors", list), ("tracker.automated_prefixes", list),
    ("tracker.template_list_prefixes", list), ("leads", list), ("lead_separator", str),
    ("status_window_days.current", int), ("status_window_days.aging", int),
    ("status_map", dict), ("first_status", str), ("hold_statuses", list),
    ("queued_statuses", list), ("state_encoding.color_markers", dict),
    ("state_encoding.hold_prefix", str), ("state_encoding.completion_marker", str),
    ("state_encoding.color_field_used", bool),
    ("state_encoding.hold_contradicting_colors", list), ("newness.repeat_lookback", int),
    ("newness.placeholder_phrases", list), ("newness.placeholder_max_words", int),
    ("roadmap.pairs_file", str), ("roadmap.strip_leading", str), ("roadmap.status_map", dict),
    ("cleanup.parked_days", int), ("cleanup.scaffold_min_rows", int),
    ("cleanup.raid_task_match", str), ("cleanup.subtitle", str), ("cleanup.buckets", dict),
    ("grading.points", dict), ("grading.project_bands", dict),
    ("grading.portfolio_lines", dict),
)


def _strings(value, label):
    if not all(isinstance(v, str) for v in value):
        raise InputError("config: %s must hold strings only" % label)


def load_config(path):
    cfg = load_json(path, "config")
    if not isinstance(cfg, dict):
        raise InputError("config %s must hold a JSON object" % path)
    for dotted, kind in CONFIG_KEYS:
        value = _get(cfg, dotted)
        if not _is_type(value, kind):
            raise InputError("config: %s must be %s" % (dotted, kind.__name__))
    for dotted in ("tracker.bot_authors", "tracker.automated_prefixes",
                   "tracker.template_list_prefixes", "hold_statuses", "queued_statuses",
                   "state_encoding.hold_contradicting_colors", "newness.placeholder_phrases"):
        _strings(_get(cfg, dotted), dotted)
    if not cfg["leads"]:
        raise InputError("config: leads must name at least one lead")
    seen = set()
    for i, lead in enumerate(cfg["leads"]):
        if not isinstance(lead, dict) or not isinstance(lead.get("name"), str) \
                or not lead["name"].strip():
            raise InputError("config: leads[%d].name must be a non-empty string" % i)
        aliases = lead.get("aliases", [])
        if not isinstance(aliases, list):
            raise InputError("config: leads[%d].aliases must be a list" % i)
        _strings(aliases, "leads[%d].aliases" % i)
        for name in [lead["name"]] + aliases:
            key = name.strip().lower()
            if key in seen:
                raise InputError("config: lead name or alias %r is used twice" % name)
            seen.add(key)
    for raw, state in cfg["status_map"].items():
        if state not in TASK_STATES:
            raise InputError("config: status_map[%r] must be one of %s"
                             % (raw, ", ".join(TASK_STATES)))
    for raw, state in cfg["roadmap"]["status_map"].items():
        if state not in ROADMAP_STATES:
            raise InputError("config: roadmap.status_map[%r] must be one of %s"
                             % (raw, ", ".join(ROADMAP_STATES)))
    for color, markers in cfg["state_encoding"]["color_markers"].items():
        if color not in COLORS:
            raise InputError("config: state_encoding.color_markers key %r must be one of %s"
                             % (color, ", ".join(COLORS)))
        if not isinstance(markers, list) or not markers:
            raise InputError("config: state_encoding.color_markers.%s must be a list" % color)
        _strings(markers, "state_encoding.color_markers.%s" % color)
    for color in cfg["state_encoding"]["hold_contradicting_colors"]:
        if color not in COLORS:
            raise InputError("config: hold_contradicting_colors holds %r" % color)
    for key in BUCKET_KEYS:
        bucket = cfg["cleanup"]["buckets"].get(key)
        if not isinstance(bucket, dict):
            raise InputError("config: missing key cleanup.buckets.%s" % key)
        for part in ("label", "definition", "remedy"):
            if not isinstance(bucket.get(part), str) or not bucket[part].strip():
                raise InputError("config: cleanup.buckets.%s.%s must be text" % (key, part))
    for key in POINT_KEYS:
        if not _is_type(cfg["grading"]["points"].get(key), int):
            raise InputError("config: grading.points.%s must be an integer" % key)
    last = None
    for key in BAND_KEYS:
        value = cfg["grading"]["project_bands"].get(key)
        if not _is_type(value, int):
            raise InputError("config: grading.project_bands.%s must be an integer" % key)
        if last is not None and value < last:
            raise InputError("config: grading.project_bands must rise from A to D")
        last = value
    for key in LINE_KEYS:
        if not _is_type(cfg["grading"]["portfolio_lines"].get(key), float):
            raise InputError("config: grading.portfolio_lines.%s must be a number" % key)
    if "{list_id}" not in cfg["tracker"]["list_url_template"]:
        raise InputError("config: tracker.list_url_template must contain {list_id}")
    window = cfg["status_window_days"]
    if window["current"] < 0 or window["aging"] < window["current"]:
        raise InputError("config: status_window_days.aging must be at least .current")
    return cfg


# ----------------------------------------------------------------- pair file

PAIR_COLUMNS = ("list id", "project list", "roadmap row", "confirmed")


def _cell(value):
    return value.strip().strip("`").strip()


def parse_pairs(path):
    """Return {"active": {list_id: pair}, "completed": {list_id: pair}}."""
    try:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise InputError("cannot read pair file %s: %s" % (path, exc.strerror or exc))
    tables = {"active": {}, "completed": {}}
    section, header = None, None
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            section = ("active" if "active pairs" in heading else
                       "completed" if "completed pairs" in heading else None)
            header = None
            continue
        if section is None:
            continue
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [_cell(c).lower() for c in cells]
            missing = [c for c in PAIR_COLUMNS if c not in header]
            if missing:
                raise InputError("pair file %s line %d: the table lacks column(s) %s"
                                 % (path, number, ", ".join(missing)))
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, [_cell(c) for c in cells]))
        list_id = row.get("list id", "")
        if not list_id:
            raise InputError("pair file %s line %d: List ID is empty" % (path, number))
        confirmed = row.get("confirmed", "").lower()
        if confirmed not in ("yes", "no"):
            raise InputError("pair file %s line %d: Confirmed must be yes or no, got %r"
                             % (path, number, row.get("confirmed", "")))
        if list_id in tables[section]:
            raise InputError("pair file %s lists %s twice in one table" % (path, list_id))
        roadmap_row = row.get("roadmap row", "")
        tables[section][list_id] = {
            "list_id": list_id, "project_list": row.get("project list", ""),
            "roadmap_row": roadmap_row, "confirmed": confirmed == "yes",
            "none": roadmap_row.lower() == "(none)"}
    return tables


# ----------------------------------------------------------------- text

MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december", "jan", "feb", "mar", "apr", "jun",
          "jul", "aug", "sep", "sept", "oct", "nov", "dec")
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "mon", "tue", "tues", "thu", "thur", "thurs", "fri")
_MONTH = r"(?:%s)\b\.?" % "|".join(MONTHS)
_ORD = r"(?:st|nd|rd|th)?"
_DATE_PATTERNS = (
    re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b"),
    # month/day with a slash, only when both parts are valid calendar values
    re.compile(r"(?<![\d/-])(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])(?:/\d{2,4})?(?![\d/])"),
    # month-day-year with hyphens needs the year, so a bare range like 1-4 stays text
    re.compile(r"(?<![\d/-])(?:0?[1-9]|1[0-2])-(?:0?[1-9]|[12]\d|3[01])-\d{2,4}(?![\d/-])"),
    re.compile(r"\b%s\s+\d{1,2}%s(?:,?\s+\d{4})?\b" % (_MONTH, _ORD)),
    re.compile(r"\b\d{1,2}%s\s+(?:of\s+)?%s(?:,?\s+\d{4})?" % (_ORD, _MONTH)),
    re.compile(r"\b(?:%s)\b" % "|".join(WEEKDAYS)),
)
_PUNCT = re.compile(r"[^\w\s]|_")


def normalize_entry(text):
    """Lowercase; drop dates in ISO, month/day and month-name forms and weekday names; keep
    numeric ranges and fractions that are not dates; drop punctuation; collapse spaces."""
    out = text.lower()
    for pattern in _DATE_PATTERNS:
        out = pattern.sub(" ", out)
    out = _PUNCT.sub(" ", out)
    return " ".join(out.split())


def normalize_row(name, strip_leading):
    """Trim, drop configured leading characters, collapse spaces, lowercase."""
    out = (name or "").strip()
    while out and (out[0] in strip_leading or out[0].isspace()):
        out = out[1:]
    return " ".join(out.split()).lower()


# ----------------------------------------------------------------- color

def luminance(color):
    channels = []
    for i in (1, 3, 5):
        c = int(color[i:i + 2], 16) / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ----------------------------------------------------------------- brand lookup

def project_root(start):
    here = os.path.abspath(start)
    while True:
        for marker in ROOT_MARKERS:
            if os.path.isdir(os.path.join(here, marker)):
                return here
        above = os.path.dirname(here)
        if above == here:
            return None
        here = above


def find_brand(explicit=None, start=None):
    """First hit wins: --brand, BRAND_JSON, brand/brand.json walking up from start to the
    project root, then this skill's shared/brand.json."""
    if explicit:
        if not os.path.isfile(explicit):
            raise InputError("brand file not found: %s" % explicit)
        return explicit
    env = os.environ.get("BRAND_JSON")
    if env:
        if not os.path.isfile(env):
            raise InputError("BRAND_JSON points at a missing file: %s" % env)
        return env
    origin = os.path.abspath(start or _SCRIPT_DIR)
    root = project_root(origin)
    if root is not None:
        here = origin
        while True:
            candidate = os.path.join(here, "brand", "brand.json")
            if os.path.isfile(candidate):
                return candidate
            if os.path.normcase(here) == os.path.normcase(root):
                break
            above = os.path.dirname(here)
            if above == here:
                break
            here = above
    if os.path.isfile(SHARED_BRAND):
        return SHARED_BRAND
    raise InputError("no brand file found; pass --brand <path> or set BRAND_JSON")
