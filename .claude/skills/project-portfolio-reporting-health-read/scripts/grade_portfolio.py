"""Grade how reliably a project portfolio is reported in its tracker, from a tracker export.

    python scripts/grade_portfolio.py <export.json> --config <cfg> --as-of <YYYY-MM-DD>
        [--judgments <judgments.json>] [--prior <findings.json>] --out <findings.json>

Four checks per in-scope active project: a status entry within the window (currency), an
entry that says something new (newness), a reported color the written entry supports
(color), and records that agree about where the project sits (placement). The judgment
checks come from the judgments file; a missing judgment is "not judged", never a pass.

Exit 0 written and complete; 1 malformed or unreadable input, unmapped status, bad judgment,
a date after --as-of, a --prior not dated before --as-of, or a usage error; 3 written with items not judged or holds pending.
Every failure is one stderr line. Standard library only.
"""
import argparse
import datetime
import os
import sys

sys.dont_write_bytecode = True
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

import health_core as core  # noqa: E402
from health_core import InputError  # noqa: E402

PROG = "grade_portfolio"
FOLDERS = ("active", "completed", "not_started")
CHECKS = ("color", "repeat", "status_field", "hold", "off_record")
VERDICTS = {"color": ("aligned", "misaligned"), "repeat": ("repeated", "new"),
            "status_field": ("stale", "current")}
TERMINAL = ("complete", "closed")
SEVERITY_ORDER = {"F": 0, "D": 1, "C": 2}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("%s: usage error: %s\n" % (PROG, message))
        sys.exit(1)


def parse_args(argv):
    parser = Parser(prog="grade_portfolio.py",
                    description="Grade portfolio reporting reliability from a tracker export.")
    parser.add_argument("export", help="tracker export JSON written by the adapter")
    parser.add_argument("--config", required=True, help="health read config JSON")
    parser.add_argument("--as-of", required=True, help="read date, YYYY-MM-DD")
    parser.add_argument("--judgments", default=None, help="judgments JSON written by the agent")
    parser.add_argument("--prior", default=None, help="last read's findings.json")
    parser.add_argument("--out", required=True, help="findings.json to write")
    return parser.parse_args(argv)


# ----------------------------------------------------------------- export checks

def _need(obj, key, kinds, where, nullable=False):
    if not isinstance(obj, dict) or key not in obj:
        raise InputError("export: %s is missing %s" % (where, key))
    value = obj[key]
    if value is None and nullable:
        return None
    if isinstance(value, bool) and bool not in kinds:
        raise InputError("export: %s.%s has the wrong type" % (where, key))
    if not isinstance(value, kinds):
        raise InputError("export: %s.%s has the wrong type" % (where, key))
    return value


def _date_or_none(obj, key, where):
    value = obj.get(key)
    if value is None:
        return None
    return core.parse_date(value, "export: %s.%s" % (where, key)).isoformat()


def check_export(data):
    if not isinstance(data, dict):
        raise InputError("export must hold a JSON object")
    if data.get("export_version") != 1:
        raise InputError("export: export_version must be 1, got %r" % data.get("export_version"))
    folders = _need(data, "folders", (dict,), "export")
    seen = set()
    for folder in FOLDERS:
        where = "folders.%s" % folder
        node = _need(folders, folder, (dict,), "folders")
        _need(node, "reported_task_total", (int,), where)
        lists = _need(node, "lists", (list,), where)
        for i, lst in enumerate(lists):
            lw = "%s.lists[%d]" % (where, i)
            list_id = _need(lst, "list_id", (str,), lw)
            if list_id in seen:
                raise InputError("export: list_id %s appears twice" % list_id)
            seen.add(list_id)
            _need(lst, "name", (str,), lw)
            _need(lst, "task_total", (int,), lw)
            st = _need(lst, "status_task", (dict,), lw, nullable=True)
            if st is not None:
                sw = lw + ".status_task"
                for key in ("task_id", "name", "status"):
                    _need(st, key, (str,), sw)
                for key in ("assignee", "status_field", "color_field"):
                    if key in st:
                        _need(st, key, (str,), sw, nullable=True)
                    else:
                        st[key] = None
                for j, e in enumerate(_need(st, "entries", (list,), sw)):
                    ew = "%s.entries[%d]" % (sw, j)
                    _need(e, "author", (str,), ew)
                    _need(e, "text", (str,), ew)
                    core.parse_date(_need(e, "date", (str,), ew), "export: %s.date" % ew)
            tasks = _need(lst, "tasks", (list,), lw, nullable=True)
            for j, t in enumerate(tasks or []):
                tw = "%s.tasks[%d]" % (lw, j)
                for key in ("task_id", "name", "status"):
                    _need(t, key, (str,), tw)
                assignees = _need(t, "assignees", (list,), tw)
                if not all(isinstance(a, str) for a in assignees):
                    raise InputError("export: %s.assignees must hold strings" % tw)
                _date_or_none(t, "due", tw)
                _date_or_none(t, "start", tw)
                core.parse_date(_need(t, "status_since", (str,), tw),
                                "export: %s.status_since" % tw)
    roadmap = data.get("roadmap", [])
    if not isinstance(roadmap, list) or not all(isinstance(r, dict) for r in roadmap):
        raise InputError("export: roadmap must be a list of rows")
    return data


def check_judgments(data, as_of, known_ids):
    if not isinstance(data, dict):
        raise InputError("judgments file must hold a JSON object")
    if data.get("judgments_version") != 1:
        raise InputError("judgments: judgments_version must be 1")
    if data.get("as_of") != as_of:
        raise InputError("judgments file is dated %s, not the --as-of date %s; judgments are "
                         "never reused across reads" % (data.get("as_of"), as_of))
    items = data.get("items")
    if not isinstance(items, list):
        raise InputError("judgments: items must be a list")
    keyed, off_record, seen = {}, {}, set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise InputError("judgments: items[%d] must be an object" % i)
        pid, check = item.get("project_id"), item.get("check")
        if pid not in known_ids:
            raise InputError("judgment names %s, which is not in the export" % pid)
        if check not in CHECKS:
            raise InputError("judgments: items[%d].check must be one of %s, got %r"
                             % (i, ", ".join(CHECKS), check))
        if check in VERDICTS:
            if item.get("verdict") not in VERDICTS[check]:
                raise InputError("judgment for %s %s has verdict %r; allowed: %s"
                                 % (pid, check, item.get("verdict"),
                                    ", ".join(VERDICTS[check])))
        if check in ("color", "repeat"):
            core.parse_date(item.get("entry_date"), "judgment %s %s entry_date" % (pid, check))
        if check == "hold":
            for key in ("narrative_records_hold", "dependency_and_owner_named"):
                if not isinstance(item.get(key), bool):
                    raise InputError("judgment for %s hold needs %s true or false" % (pid, key))
            if item.get("resumed_on") is not None:
                core.parse_date(item["resumed_on"], "judgment %s hold resumed_on" % pid)
        if check == "off_record":
            if not isinstance(item.get("note"), str) or not item["note"].strip():
                raise InputError("judgment for %s off_record needs a note" % pid)
            off_record.setdefault(pid, []).append(item)
            continue
        if (pid, check) in seen:
            raise InputError("judgments name %s %s twice" % (pid, check))
        seen.add((pid, check))
        keyed[(pid, check)] = item
    return keyed, off_record


# ----------------------------------------------------------------- the grader

def pct(line):
    return "%g" % round(line * 100, 6)


def plural(n, word, many=None):
    return "%d %s" % (n, word if n == 1 else (many or word + "s"))


class Grader:
    def __init__(self, cfg, export, pairs, judgments, off_record, prior, as_of, sources):
        self.cfg = cfg
        self.export = export
        self.pairs = pairs
        self.judg = judgments
        self.off_record = off_record
        self.prior = prior
        self.as_of = as_of
        self.as_of_date = datetime.date.fromisoformat(as_of)
        self.sources = sources
        enc = cfg["state_encoding"]
        self.markers = {}
        for color, tokens in enc["color_markers"].items():
            for token in tokens:
                self.markers[token.lower()] = color
        self.status_map = {k.strip().lower(): v for k, v in cfg["status_map"].items()}
        self.roadmap_map = {k.strip().lower(): v
                            for k, v in cfg["roadmap"]["status_map"].items()}
        self.lead_names = [l["name"] for l in cfg["leads"]]
        self.lead_keys = {}
        for lead in cfg["leads"]:
            for name in [lead["name"]] + lead.get("aliases", []):
                self.lead_keys[name.strip().lower()] = lead["name"]
        self.bots = {b.lower() for b in cfg["tracker"]["bot_authors"]}
        self.prefixes = [p.lower() for p in cfg["tracker"]["automated_prefixes"]]
        self.placeholders = [core.normalize_entry(p)
                             for p in cfg["newness"]["placeholder_phrases"]]
        self.method = {"unpaired_active_lists": [], "unconfirmed_pairs": [],
                       "missing_roadmap_rows": [], "completed_pair_conflicts": [],
                       "not_judged": [], "discarded_judgments": [], "count_checks": [],
                       "measurement_changes": [], "notes": []}
        self.requests = []

    # ------------------------------------------------------------- small helpers

    def mapped(self, raw):
        return self.status_map[raw.strip().lower()]

    def url(self, list_id):
        return self.cfg["tracker"]["list_url_template"].replace("{list_id}", list_id)

    def days(self, iso):
        return (self.as_of_date - datetime.date.fromisoformat(iso)).days

    def note(self, text):
        self.method["notes"].append(text)

    def discard(self, pid, check, why):
        self.method["discarded_judgments"].append("%s %s: %s" % (pid, check, why))

    def is_template(self, name):
        return any(name.lower().startswith(p.lower())
                   for p in self.cfg["tracker"]["template_list_prefixes"])

    def lead_of(self, lst):
        sep = self.cfg["lead_separator"]
        name = lst["name"]
        if sep and sep in name:
            tail = name.rsplit(sep, 1)[1].strip().lower()
            if tail in self.lead_keys:
                return self.lead_keys[tail]
        st = lst["status_task"]
        if st and st.get("assignee") and st["assignee"].strip().lower() in self.lead_keys:
            return self.lead_keys[st["assignee"].strip().lower()]
        return None

    def configured(self, person):
        if not person:
            return None
        return self.lead_keys.get(person.strip().lower())

    def status_rows(self, lst):
        st = lst["status_task"]
        st_id = st["task_id"] if st else None
        rows = lst["tasks"] or []
        return [t for t in rows if t["task_id"] == st_id], \
               [t for t in rows if t["task_id"] != st_id]

    def human_entries(self, st, resumed_on=None):
        if not st:
            return []
        out = []
        for e in st["entries"]:
            if e.get("is_bot") or e["author"].strip().lower() in self.bots:
                continue
            if any(e["text"].lstrip().lower().startswith(p) for p in self.prefixes):
                continue
            if resumed_on and e["date"] < resumed_on:
                continue
            out.append(e)
        return sorted(out, key=lambda e: e["date"], reverse=True)

    def encoding(self, st):
        enc = self.cfg["state_encoding"]
        name = st["name"] if st else ""
        tokens = name.split()
        found = []
        for t in tokens:
            color = self.markers.get(t.lower())
            if color and color not in found:
                found.append(color)
        color, source, note = None, None, None
        field_color = None
        if enc["color_field_used"] and st and st.get("color_field"):
            value = st["color_field"].strip().lower()
            field_color = value if value in enc["color_markers"] else None
        if len(found) == 1:
            color, source = found[0], "name"
        elif len(found) > 1:
            note = "the status task name carries two different color markers"
        elif field_color:
            color, source = field_color, "field"
        completion = enc["completion_marker"].lower()
        i = 0
        while i < len(tokens) and (tokens[i].lower() in self.markers
                                   or (completion and tokens[i].lower() == completion)):
            i += 1
        rest = " ".join(tokens[i:]).lower()
        prefix = enc["hold_prefix"].lower()
        hold_prefix = bool(prefix.strip()) and (rest + " ").startswith(prefix)
        completed = bool(completion) and any(t.lower() == completion for t in tokens)
        return {"color": color, "source": source, "note": note, "hold_prefix": hold_prefix,
                "completion": completed, "field_color": field_color}

    def find_row(self, wanted):
        strip = self.cfg["roadmap"]["strip_leading"]
        key = core.normalize_row(wanted, strip)
        for row in self.export.get("roadmap", []):
            if isinstance(row.get("name"), str) and core.normalize_row(row["name"], strip) == key:
                return row
        return None

    def roadmap_state(self, row):
        raw = row.get("status")
        if not isinstance(raw, str) or raw.strip().lower() not in self.roadmap_map:
            raise InputError("roadmap row %r has status %r, which roadmap.status_map does not "
                             "cover; extend the map" % (row.get("name"), raw))
        return self.roadmap_map[raw.strip().lower()]

    # ------------------------------------------------------------- input-wide rules

    def precheck(self):
        unknown = set()
        for folder in FOLDERS:
            for lst in self.export["folders"][folder]["lists"]:
                st = lst["status_task"]
                raws = [t["status"] for t in lst["tasks"] or []]
                if st:
                    raws.append(st["status"])
                    for e in st["entries"]:
                        if e["date"] > self.as_of:
                            raise InputError("list %r has an entry dated %s, after --as-of %s"
                                             % (lst["name"], e["date"], self.as_of))
                for raw in raws:
                    if raw.strip().lower() not in self.status_map:
                        unknown.add(raw)
        if unknown:
            raise InputError("statuses not covered by status_map: %s; extend the map"
                             % ", ".join(sorted(unknown)))

    # ------------------------------------------------------------- one active project

    def grade_active(self, lst, lead):
        pid, name = lst["list_id"], lst["name"]
        st = lst["status_task"]
        enc = self.encoding(st)
        hold_j = self.judg.get((pid, "hold"))
        has_hold = enc["hold_prefix"] or bool(
            st and st["status"].strip().lower() in
            [h.strip().lower() for h in self.cfg["hold_statuses"]]) or bool(
            hold_j and hold_j["narrative_records_hold"])
        rule_misaligned, hold_minor, scope = False, False, "in"
        if has_hold:
            if enc["color"] in self.cfg["state_encoding"]["hold_contradicting_colors"]:
                rule_misaligned = True
            elif hold_j is None:
                scope = "pending"
            elif hold_j["dependency_and_owner_named"]:
                scope = "held"
            else:
                hold_minor = True
        if scope == "held":
            return {"scope": "held"}
        entries_all = self.human_entries(st)
        newest_all = entries_all[0] if entries_all else None
        if scope == "pending":
            self.request(pid, name, "hold", newest_all, enc, answered=False)
            return {"scope": "pending"}
        if has_hold and not rule_misaligned:
            self.request(pid, name, "hold", newest_all, enc, answered=True)
        resumed_on = hold_j.get("resumed_on") if hold_j else None
        entries = self.human_entries(st, resumed_on)
        newest = entries[0] if entries else None
        provisional = False

        currency = self.currency(lst, st, entries, resumed_on, name)
        newness = self.newness(pid, name, st, entries, currency)
        color = self.color(pid, name, enc, newest, currency, newness, rule_misaligned)
        if color["band"] == "not_judged":
            provisional = True
        records, field_pending = self.records(lst, lead, st, enc, newest, currency, has_hold,
                                              hold_minor)
        provisional = provisional or field_pending
        if enc["note"]:
            self.note("%s %s: %s; color not assessable" % (pid, name, enc["note"]))
        points = self.points(currency, newness, color, records)
        grade = "F" if currency["abandoned"] else self.letter_for(points)
        return {"scope": "in", "project": {
            "project_id": pid, "name": name, "url": self.url(pid), "lead": lead,
            "points": points, "grade": grade, "provisional": provisional,
            "checks": {"currency": currency, "newness": newness, "color": color,
                       "records": records}}}

    def request(self, pid, name, check, newest, enc, answered, field_value=None):
        self.requests.append({
            "project_id": pid, "project_name": name, "check": check,
            "entry_date": newest["date"] if newest else None,
            "entry_text": newest["text"] if newest else None,
            "reported_color": enc["color"], "field_value": field_value,
            "answered": answered})
        if not answered:
            label = {"hold": "hold judgment", "color": "color judgment",
                     "status_field": "status field judgment"}[check]
            self.method["not_judged"].append("%s %s: %s missing" % (pid, name, label))

    def currency(self, lst, st, entries, resumed_on, name):
        window = self.cfg["status_window_days"]
        check = {"band": "absent", "latest_entry_date": None, "age_days": None,
                 "author": None, "abandoned": False, "resumed_on": resumed_on,
                 "result": "fail"}
        if entries:
            newest = entries[0]
            age = self.days(newest["date"])
            check.update(latest_entry_date=newest["date"], age_days=age,
                         author=newest["author"])
            if age <= window["current"]:
                check.update(band="current", result="pass")
            elif age <= window["aging"]:
                check.update(band="aging", result="minor")
            else:
                check.update(band="stale", result="fail")
        elif st is not None and resumed_on and self.days(resumed_on) <= window["current"]:
            check.update(band="current", result="pass")
            self.note("%s %s: resumed on %s with no entry since; read as current"
                      % (lst["list_id"], name, resumed_on))
        if lst["tasks"] is None:
            self.note("%s %s: tasks not pulled; trip wire and cleanup skipped"
                      % (lst["list_id"], name))
        elif st is not None:
            _, rows = self.status_rows(lst)
            first = self.status_map.get(self.cfg["first_status"].strip().lower())
            untouched = all(self.mapped(t["status"]) == first for t in rows)
            st_first = st["status"].strip().lower() == self.cfg["first_status"].strip().lower()
            undated = not any(t["due"] or t["start"] for t in rows)
            if untouched and st_first and undated:
                check.update(abandoned=True, result="fail")
        return check

    def same(self, a, b):
        na, nb = core.normalize_entry(a["text"]), core.normalize_entry(b["text"])
        if a.get("truncated") or b.get("truncated"):
            n = min(len(na), len(nb))
            if n:
                return na[:n] == nb[:n]
        return na == nb

    def is_placeholder(self, entry):
        text = core.normalize_entry(entry["text"])
        limit = self.cfg["newness"]["placeholder_max_words"]
        for phrase in self.placeholders:
            if not phrase:
                continue
            if text == phrase:
                return True
            if text.startswith(phrase + " ") and len(text.split()) <= limit \
                    and not any(ch.isdigit() for ch in text):
                return True
        return False

    def newness(self, pid, name, st, entries, currency):
        check = {"band": "not_applicable", "consecutive_same": 0, "at_least": False,
                 "basis": "rule", "result": None}
        rj = self.judg.get((pid, "repeat"))
        if currency["band"] == "absent" or not entries:
            if rj:
                self.discard(pid, "repeat", "there is no human entry to judge")
            return check
        if self.is_placeholder(entries[0]):
            check.update(band="placeholder", consecutive_same=1, result="fail")
        else:
            lookback = entries[1:1 + self.cfg["newness"]["repeat_lookback"]]
            if any(self.same(entries[0], e) for e in lookback):
                run_length = 1
                for e in entries[1:]:
                    if not self.same(entries[0], e):
                        break
                    run_length += 1
                at_least = run_length == len(entries) and \
                    len(st["entries"]) >= self.cfg["tracker"]["comments_limit"]
                check.update(band="repeated", consecutive_same=run_length, at_least=at_least,
                             result="fail")
            else:
                check.update(band="new", consecutive_same=1, result="pass")
                if len(entries) == 1:
                    self.note("%s %s: first entry, so newness reads new" % (pid, name))
        if rj:
            if rj["entry_date"] != entries[0]["date"]:
                self.discard(pid, "repeat", "entry_date %s is not the newest human entry (%s)"
                             % (rj["entry_date"], entries[0]["date"]))
            elif rj["verdict"] == "repeated" and check["band"] == "new":
                check.update(band="repeated", basis="judgment", result="fail",
                             consecutive_same=2 if len(entries) > 1 else 1)
            elif rj["verdict"] == "new" and check["band"] in ("repeated", "placeholder"):
                self.discard(pid, "repeat", "a new verdict never overturns a rule result (%s)"
                             % check["band"])
        return check

    def color(self, pid, name, enc, newest, currency, newness, rule_misaligned):
        check = {"reported": enc["color"], "source": enc["source"], "band": "not_assessable",
                 "quote": None, "basis": "rule", "result": None}
        cj = self.judg.get((pid, "color"))
        if rule_misaligned:
            check.update(band="misaligned", result="fail")
            if cj:
                self.discard(pid, "color", "a recorded hold with a %s marker sets this check "
                             "by rule" % enc["color"])
            return check
        if enc["color"] is None or currency["band"] == "absent" or newest is None \
                or newness["band"] == "placeholder":
            if cj:
                self.discard(pid, "color", "the color is not assessable for this project")
            return check
        check["basis"] = "judgment"
        if cj and cj["entry_date"] == newest["date"]:
            check.update(band=cj["verdict"], quote=cj.get("quote"),
                         result="pass" if cj["verdict"] == "aligned" else "fail")
            self.request(pid, name, "color", newest, enc, answered=True)
            return check
        if cj:
            self.discard(pid, "color", "entry_date %s is not the newest human entry (%s)"
                         % (cj["entry_date"], newest["date"]))
        check["band"] = "not_judged"
        self.request(pid, name, "color", newest, enc, answered=False)
        return check

    def item(self, kind, severity, detail, owner, counted=True):
        return {"kind": kind, "severity": severity, "detail": detail, "owner": owner,
                "counted": counted}

    def records(self, lst, lead, st, enc, newest, currency, has_hold, hold_minor):
        pid, name = lst["list_id"], lst["name"]
        items = []
        field_pending = False
        _, rows = self.status_rows(lst)
        if enc["completion"]:
            items.append(self.item("placement_finished_in_active", "conflict",
                                   "The name carries the completion marker while the list "
                                   "sits in the active folder.", lead))
        elif rows and all(self.mapped(t["status"]) in TERMINAL for t in rows):
            items.append(self.item("placement_finished_in_active", "conflict",
                                   "Every task is complete while the list sits in the active "
                                   "folder.", lead))
        pair = self.pairs["active"].get(pid)
        if pair is None:
            self.method["unpaired_active_lists"].append(name)
        elif not pair["none"]:
            if not pair["confirmed"]:
                self.method["unconfirmed_pairs"].append(name)
            row = self.find_row(pair["roadmap_row"])
            if row is None:
                self.method["missing_roadmap_rows"].append(
                    "%s: roadmap row '%s' not found" % (name, pair["roadmap_row"]))
            else:
                state = self.roadmap_state(row)
                owner = self.configured(row.get("owner")) or lead
                kind = detail = severity = None
                if state in ("complete", "not_started"):
                    kind, severity = "roadmap_status_conflict", "conflict"
                    detail = ("The roadmap row '%s' reads '%s' while the list sits in the "
                              "active folder." % (row["name"], row["status"]))
                elif state == "held" and not has_hold:
                    kind, severity = "roadmap_status_conflict", "conflict"
                    detail = ("The roadmap row '%s' reads '%s' while the project records no "
                              "hold." % (row["name"], row["status"]))
                elif has_hold and state != "held":
                    kind, severity = "roadmap_hold_conflict", "minor"
                    detail = ("The project records a hold; the roadmap row '%s' reads '%s'."
                              % (row["name"], row["status"]))
                if kind:
                    if not pair["confirmed"]:
                        detail = "Unconfirmed pair: " + detail
                    items.append(self.item(kind, severity, detail, owner, pair["confirmed"]))
        if st and st.get("status_field"):
            sj = self.judg.get((pid, "status_field"))
            if sj is None:
                field_pending = True
                self.request(pid, name, "status_field", newest, enc, answered=False,
                             field_value=st["status_field"])
            else:
                self.request(pid, name, "status_field", newest, enc, answered=True,
                             field_value=st["status_field"])
                if sj["verdict"] == "stale":
                    why = sj.get("note")
                    detail = "The status field reads '%s'" % st["status_field"]
                    detail += " (%s)." % why if why else "."
                    items.append(self.item("status_field_stale", "minor", detail, lead))
        if currency["band"] != "absent" and newest is not None:
            author = newest["author"]
            assignee = st.get("assignee") if st else None
            if not assignee:
                items.append(self.item("owner_mismatch", "minor",
                                       "The status task has no owner; the newest entry is by "
                                       "%s." % author, lead))
            elif assignee.strip().lower() != author.strip().lower():
                items.append(self.item("owner_mismatch", "minor",
                                       "The status task is assigned to %s; the newest entry is "
                                       "by %s." % (assignee, author), lead))
        if self.cfg["state_encoding"]["color_field_used"] and enc["source"] == "name" \
                and enc["field_color"] and enc["field_color"] != enc["color"]:
            items.append(self.item("color_field_conflict", "minor",
                                   "The name shows %s; the color field reads '%s'."
                                   % (enc["color"], st["color_field"]), lead))
        for judged in self.off_record.get(pid, []):
            items.append(self.item("off_record_update", "minor",
                                   "Off-record: %s." % judged["note"].rstrip("."), lead))
        if hold_minor:
            items.append(self.item("hold_no_dependency", "minor",
                                   "The hold is recorded, but the entry names neither what it "
                                   "waits on nor who owns that.", lead))
        counted = [i for i in items if i["counted"]]
        if any(i["severity"] == "conflict" for i in counted):
            band, result = "conflicting", "fail"
        elif counted:
            band, result = "minor", "minor"
        else:
            band, result = "clean", "pass"
        return {"band": band, "items": items, "result": result}, field_pending

    def points(self, currency, newness, color, records):
        pts = self.cfg["grading"]["points"]
        total = 0
        if currency["band"] in ("aging", "stale", "absent"):
            total += pts[currency["band"]]
        if newness["band"] in ("repeated", "placeholder"):
            total += pts[newness["band"]]
        if color["band"] == "misaligned":
            total += pts["misaligned"]
        if records["band"] == "minor":
            total += pts["minor"]
        elif records["band"] == "conflicting":
            total += pts["conflicting"]
        return total

    def letter_for(self, points):
        for letter in core.BAND_KEYS:
            if points <= self.cfg["grading"]["project_bands"][letter]:
                return letter
        return "F"

    # ------------------------------------------------------------- outside the active folder

    def grade_outside(self, lst, folder, lead):
        if lst["tasks"] is None:
            self.note("%s %s: tasks not pulled; placement and cleanup skipped"
                      % (lst["list_id"], lst["name"]))
            return []
        _, rows = self.status_rows(lst)
        if folder == "not_started":
            started = [t for t in rows if self.mapped(t["status"]) in ("in_progress", "complete")]
            if started:
                return [self.item("placement_started_in_not_started", "conflict",
                                  "%s started while the list sits in the not-started folder."
                                  % plural(len(started), "task is", "tasks are"), lead)]
            return []
        open_rows = [t for t in rows if self.mapped(t["status"]) in ("not_started", "in_progress")]
        if open_rows:
            return [self.item("placement_open_in_completed", "conflict",
                              "%s open while the list sits in the completed folder."
                              % plural(len(open_rows), "task is", "tasks are"), lead)]
        return []

    # ------------------------------------------------------------- grades

    def grade_group(self, projects, outside_count):
        lines = self.cfg["grading"]["portfolio_lines"]
        n = len(projects)
        if n == 0 and outside_count == 0:
            return {"grade": None, "reasons": [], "keys": [],
                    "shares": {"currency_fail": 0.0, "newness_fail": 0.0, "color_fail": 0.0,
                               "color_or_records_issue": 0.0}}
        cur = sum(1 for p in projects if p["checks"]["currency"]["result"] == "fail")
        new = sum(1 for p in projects
                  if p["checks"]["newness"]["band"] in ("repeated", "placeholder"))
        col = sum(1 for p in projects if p["checks"]["color"]["band"] == "misaligned")
        issue = sum(1 for p in projects
                    if p["checks"]["color"]["result"] == "fail"
                    or any(i["counted"] for i in p["checks"]["records"]["items"]))
        issue += outside_count
        den = n + outside_count

        def share(k, d):
            return round(k / d, 4) if d else 0.0

        shares = {"currency_fail": share(cur, n), "newness_fail": share(new, n),
                  "color_fail": share(col, n), "color_or_records_issue": share(issue, den)}
        fired = []
        for level, key in (("F", "f_currency_fail_over"), ("D", "d_currency_fail_over"),
                           ("C", "c_currency_fail_over")):
            if shares["currency_fail"] > lines[key]:
                fired.append((level, key, "%d of %d projects have no current status, above "
                              "the %s percent line" % (cur, n, pct(lines[key]))))
                break
        if shares["color_fail"] > lines["d_color_fail_over"]:
            fired.append(("D", "d_color_fail_over",
                          "%d of %d projects report a color their written status does not "
                          "support, above the %s percent line"
                          % (col, n, pct(lines["d_color_fail_over"]))))
        if shares["newness_fail"] > lines["c_newness_fail_over"]:
            fired.append(("C", "c_newness_fail_over",
                          "%d of %d projects repeat an earlier entry or file a placeholder, "
                          "above the %s percent line" % (new, n, pct(lines["c_newness_fail_over"]))))
        if shares["color_or_records_issue"] > lines["c_color_or_records_over"]:
            fired.append(("C", "c_color_or_records_over",
                          "%d of %d projects and lists have a color or record issue, above the "
                          "%s percent line" % (issue, den, pct(lines["c_color_or_records_over"]))))
        fired.sort(key=lambda f: SEVERITY_ORDER[f[0]])
        if fired:
            grade = fired[0][0]
            reasons = [f[2] for f in fired]
            keys = [f[1] for f in fired]
        else:
            short = sum(1 for p in projects if p["grade"] != "A")
            reasons, keys = [], []
            if short:
                reasons.append("%d of %d projects have at least one check short of a pass"
                               % (short, n))
                keys.append("b_projects")
            if outside_count:
                reasons.append("%s outside the active folder %s record items"
                               % (plural(outside_count, "list"),
                                  "has" if outside_count == 1 else "have"))
                keys.append("b_outside")
            if reasons:
                grade = "B"
            else:
                grade = "A"
                reasons, keys = ["Every in-scope project passes all four checks"], ["a"]
        return {"grade": grade, "reasons": reasons, "keys": keys, "shares": shares}

    # ------------------------------------------------------------- fix items

    def fix_item(self, owner, project, check, kind, what):
        return {"owner": owner, "project_id": project["project_id"],
                "project_name": project["name"], "url": project["url"], "check": check,
                "kind": kind, "what": what}

    def project_fixes(self, p, st_by_id):
        out = []
        lead = p["lead"]
        cur, new, col = (p["checks"]["currency"], p["checks"]["newness"],
                         p["checks"]["color"])
        if cur["result"] in ("minor", "fail"):
            if cur["abandoned"]:
                out.append(self.fix_item(lead, p, 1, "abandoned",
                                         "Start using the list or record why it waits. No task "
                                         "has left the first status, the status task has not "
                                         "advanced and no task carries a date."))
            elif cur["band"] == "absent":
                what = ("Start the status record. The list has no status task."
                        if st_by_id.get(p["project_id"]) is None else
                        "Start the status record. The status task has no entries.")
                if cur["resumed_on"]:
                    what = ("Start the status record. There is no entry since the project "
                            "resumed on %s." % cur["resumed_on"])
                out.append(self.fix_item(lead, p, 1, "absent", what))
            else:
                out.append(self.fix_item(lead, p, 1, cur["band"],
                                         "Add a status entry. The newest entry is dated %s, %s "
                                         "before this read." % (cur["latest_entry_date"],
                                                                plural(cur["age_days"], "day"))))
        if new["band"] == "repeated":
            if new["basis"] == "judgment":
                what = ("Write what changed since the previous entry. The newest entry repeats "
                        "the open item from the previous one.")
            elif new["consecutive_same"] < 2:
                what = ("Write what changed since the previous entry. The newest entry "
                        "matches an earlier one once dates are set aside.")
            else:
                what = ("Write what changed since the previous entry. %s last %d entries "
                        "match once dates are set aside."
                        % ("At least the" if new["at_least"] else "The",
                           new["consecutive_same"]))
            out.append(self.fix_item(lead, p, 2, "repeated", what))
        elif new["band"] == "placeholder":
            st = st_by_id.get(p["project_id"])
            text = self.human_entries(st, cur["resumed_on"])[0]["text"]
            out.append(self.fix_item(lead, p, 2, "placeholder",
                                     "Replace the placeholder with what happened. The newest "
                                     "entry reads: '%s'" % text))
        if col["band"] == "misaligned":
            if col["basis"] == "rule":
                out.append(self.fix_item(lead, p, 3, "hold_color_conflict",
                                         "Make the color and the hold agree. The name records a "
                                         "hold and shows %s." % col["reported"]))
            else:
                said = ("the entry says: '%s'" % col["quote"] if col["quote"]
                        else "the newest entry does not support it")
                out.append(self.fix_item(lead, p, 3, "misaligned",
                                         "Make the color and the written status agree. The name "
                                         "shows %s; %s" % (col["reported"], said)))
        for item in p["checks"]["records"]["items"]:
            if item["counted"]:
                out.append(self.fix_item(item["owner"], p, 4, item["kind"],
                                         RECORD_LEADS[item["kind"]] + " " + item["detail"]))
        return out

    # ------------------------------------------------------------- cleanup

    def attribute(self, task, list_lead):
        names = [self.configured(a) for a in task["assignees"]]
        names = [n for n in names if n]
        if list_lead in names:
            return list_lead
        return names[0] if names else list_lead

    def cleanup(self, active_lists, completed_lists, leads):
        cfg = self.cfg["cleanup"]
        parked_days = cfg["parked_days"]
        queued = [q.strip().lower() for q in self.cfg["queued_statuses"]]
        filters = {"parked_raw": 0, "parked_counted": 0, "status_tasks_excluded": 0,
                   "finished_tasks_excluded": 0}
        lines = {name: {key: [] for key in core.BUCKET_KEYS} for name in self.lead_names}
        summary_counts = {name: [] for name in self.lead_names}

        def add(lead, key, task, lst, detail, task_name=None):
            if lead not in lines:
                self.note("%s %s: a cleanup line has no configured lead and is left out"
                          % (lst["list_id"], lst["name"]))
                return
            lines[lead][key].append({
                "task_id": task["task_id"] if task else None,
                "task_name": task_name or task["name"], "project_name": lst["name"],
                "url": self.url(lst["list_id"]), "detail": detail})

        def tally(lst):
            st_rows, rows = self.status_rows(lst)
            filters["status_tasks_excluded"] += len(st_rows)
            for t in st_rows + rows:
                if self.mapped(t["status"]) not in TERMINAL and \
                        self.days(t["status_since"]) > parked_days:
                    filters["parked_raw"] += 1
            filters["finished_tasks_excluded"] += sum(
                1 for t in rows if self.mapped(t["status"]) in TERMINAL)
            return rows

        for lst, lead in active_lists:
            if lst["tasks"] is None:
                continue
            rows = tally(lst)
            per_bucket = {}
            scaffold = [t for t in rows if self.mapped(t["status"]) == "not_started"
                        and not t["due"] and not t["assignees"]]
            use_scaffold = len(scaffold) >= cfg["scaffold_min_rows"]
            skip = {t["task_id"] for t in scaffold} if use_scaffold else set()
            for t in rows:
                state = self.mapped(t["status"])
                if state in TERMINAL or t["task_id"] in skip:
                    continue
                owner = self.attribute(t, lead)
                age = self.days(t["status_since"])
                active = state == "in_progress"
                is_queued = t["status"].strip().lower() in queued
                past = bool(t["due"]) and t["due"] < self.as_of
                key = detail = None
                if active and age > parked_days:
                    key = "parked"
                    detail = "In progress since %s (%s)" % (t["status_since"], plural(age, "day"))
                elif active and not t["due"] and not t["assignees"]:
                    key, detail = "no_date_no_owner", "In progress with no due date and no owner"
                elif (active or is_queued) and past:
                    key = "overdue"
                    detail = "%s, due %s" % ("In progress" if active else "Ready to start",
                                             t["due"])
                elif (active or is_queued) and not t["assignees"]:
                    key = "no_owner"
                    detail = "%s, %s" % ("In progress" if active else "Ready to start",
                                         "due %s" % t["due"] if t["due"] else "no due date")
                elif state == "not_started" and past:
                    key, detail = "not_started_past_due", "Not started, due %s" % t["due"]
                if key:
                    add(owner, key, t, lst, detail)
                    per_bucket.setdefault((owner, key), 0)
                    per_bucket[(owner, key)] += 1
                    if key == "parked":
                        filters["parked_counted"] += 1
            if use_scaffold:
                n = len(scaffold)
                add(lead, "scaffold", None, lst, "Not started, with no due date and no owner",
                    task_name="%d undated, unowned rows" % n)
                per_bucket[(lead, "scaffold")] = n
            for (owner, key), count in per_bucket.items():
                if owner in summary_counts:
                    summary_counts[owner].append((lst, key, count))

        for lst, lead in completed_lists:
            if lst["tasks"] is None:
                continue
            rows = tally(lst)
            match = cfg["raid_task_match"].lower()
            for t in rows:
                state = self.mapped(t["status"])
                if state in TERMINAL:
                    continue
                owner = self.attribute(t, lead)
                if match and match in t["name"].lower():
                    add(owner, "open_raid", t, lst, "Open (%s)" % t["status"])
                elif t["due"] and t["due"] < self.as_of:
                    add(owner, "past_due_open", t, lst, "Open, due %s" % t["due"])
                else:
                    add(owner, "open_in_finished", t, lst, "Open (%s)" % t["status"])

        out = {}
        for name in self.lead_names:
            buckets = []
            for key in core.BUCKET_KEYS:
                if lines[name][key]:
                    spec = cfg["buckets"][key]
                    buckets.append({"key": key, "label": spec["label"],
                                    "definition": spec["definition"], "remedy": spec["remedy"],
                                    "lines": lines[name][key]})
            summary = [{"project_name": f["project_name"], "url": f["url"], "what": f["what"]}
                       for f in leads[name]]
            ordered = sorted(summary_counts[name],
                             key=lambda s: core.BUCKET_KEYS.index(s[1]))
            seen_lists = []
            for lst, _, _ in summary_counts[name]:
                if lst["list_id"] not in seen_lists:
                    seen_lists.append(lst["list_id"])
            ordered.sort(key=lambda s: (seen_lists.index(s[0]["list_id"]),
                                        core.BUCKET_KEYS.index(s[1])))
            for lst, key, count in ordered:
                spec = cfg["buckets"][key]
                unit = plural(count, "row") if key == "scaffold" else plural(count, "task")
                summary.append({"project_name": lst["name"], "url": self.url(lst["list_id"]),
                                "what": "%s: %s" % (spec["label"], unit)})
            out[name] = {"summary": summary, "what_to_fix_count": len(summary),
                         "buckets": buckets, "clean": len(summary) == 0}
        return out, filters

    # ------------------------------------------------------------- the run

    def run(self):
        self.precheck()
        cfg = self.cfg
        folders = self.export["folders"]
        skipped, kept = [], {f: [] for f in FOLDERS}
        for folder in FOLDERS:
            for lst in folders[folder]["lists"]:
                if self.is_template(lst["name"]):
                    skipped.append(lst["name"])
                else:
                    kept[folder].append(lst)
        st_by_id = {lst["list_id"]: lst["status_task"] for f in FOLDERS for lst in kept[f]}

        for list_id in self.pairs["active"]:
            if any(l["list_id"] == list_id for l in kept["completed"]):
                self.note("the pair for %s sits in the active pairs table, but the list is in "
                          "the completed folder; move the pair" % list_id)
        known = {l["list_id"] for f in FOLDERS for l in folders[f]["lists"]}
        for table in ("active", "completed"):
            for list_id in self.pairs[table]:
                if list_id not in known:
                    self.note("the pair file names %s, which is not in the export" % list_id)

        projects, held, pending, active_in = [], [], [], []
        for lst in kept["active"]:
            lead = self.lead_of(lst)
            result = self.grade_active(lst, lead)
            if result["scope"] == "held":
                held.append({"project_id": lst["list_id"], "name": lst["name"]})
            elif result["scope"] == "pending":
                pending.append({"project_id": lst["list_id"], "name": lst["name"]})
            else:
                projects.append(result["project"])
                active_in.append((lst, lead))
                if lead is None:
                    self.note("%s %s: no configured lead matches the list name or the status "
                              "task owner; its fix items are unattributed"
                              % (lst["list_id"], lst["name"]))
        projects.sort(key=lambda p: (not p["checks"]["currency"]["abandoned"], -p["points"],
                                     p["name"]))
        rank = {p["project_id"]: i for i, p in enumerate(projects)}
        active_in.sort(key=lambda pair: rank[pair[0]["list_id"]])

        outside, completed_in = [], []
        for folder in ("completed", "not_started"):
            for lst in kept[folder]:
                lead = self.lead_of(lst)
                items = self.grade_outside(lst, folder, lead)
                if folder == "completed":
                    completed_in.append((lst, lead))
                    pair = self.pairs["completed"].get(lst["list_id"])
                    if pair and not pair["none"]:
                        row = self.find_row(pair["roadmap_row"])
                        if row is None:
                            self.method["missing_roadmap_rows"].append(
                                "%s: roadmap row '%s' not found" % (lst["name"],
                                                                    pair["roadmap_row"]))
                        elif self.roadmap_state(row) != "complete":
                            self.method["completed_pair_conflicts"].append(
                                "%s: the roadmap row '%s' reads '%s' although the list is in "
                                "the completed folder" % (lst["name"], row["name"],
                                                          row["status"]))
                if items:
                    outside.append({"project_id": lst["list_id"], "name": lst["name"],
                                    "url": self.url(lst["list_id"]), "folder": folder,
                                    "lead": lead, "items": items})

        # fix items, in rank order then outside lists
        fixes = []
        for p in projects:
            fixes += self.project_fixes(p, st_by_id)
        for o in outside:
            for item in o["items"]:
                fixes.append({"owner": item["owner"], "project_id": o["project_id"],
                              "project_name": o["name"], "url": o["url"], "check": 4,
                              "kind": item["kind"],
                              "what": RECORD_LEADS[item["kind"]] + " " + item["detail"]})
        by_lead = {name: [] for name in self.lead_names}
        unattributed = []
        for f in fixes:
            (by_lead[f["owner"]] if f["owner"] in by_lead else unattributed).append(f)

        corrections, order = {}, []
        for f in fixes:
            pid = f["project_id"]
            if pid not in corrections:
                order.append(pid)
                corrections[pid] = {"project_id": pid, "name": f["project_name"],
                                    "url": f["url"], "owners": [], "corrections": []}
            owner = f["owner"] or "Unattributed"
            if owner not in corrections[pid]["owners"]:
                corrections[pid]["owners"].append(owner)
            corrections[pid]["corrections"].append({"owner": owner, "what": f["what"]})
        lead_rank = {name: i for i, name in enumerate(self.lead_names)}
        for entry in corrections.values():
            entry["owners"].sort(key=lambda o: lead_rank.get(o, len(lead_rank)))
            entry["corrections"].sort(key=lambda c: lead_rank.get(c["owner"], len(lead_rank)))
        fixed_ids = set(order)

        cleanup, filters = self.cleanup(active_in, completed_in, by_lead)

        portfolio = self.grade_group(projects, len(outside))
        leads_out = []
        for name in self.lead_names:
            mine = [p for p in projects if p["lead"] == name]
            mine_out = [o for o in outside if o["lead"] == name]
            group = self.grade_group(mine, len(mine_out))
            leads_out.append({
                "name": name, "grade": group["grade"],
                "provisional": any(p["provisional"] for p in mine),
                "project_ids": [p["project_id"] for p in mine] +
                               [o["project_id"] for o in mine_out],
                "fix_list": by_lead[name], "cleanup": cleanup[name]})

        splits = {
            "currency": {k: 0 for k in ("current", "aging", "stale", "absent")},
            "newness": {k: 0 for k in ("new", "repeated", "placeholder", "not_applicable")},
            "color": {k: 0 for k in ("aligned", "misaligned", "not_assessable", "not_judged")},
            "records": {"clean": 0, "minor": 0, "conflicting": 0}}
        for p in projects:
            splits["currency"][p["checks"]["currency"]["band"]] += 1
            splits["newness"][p["checks"]["newness"]["band"]] += 1
            splits["color"][p["checks"]["color"]["band"]] += 1
            splits["records"][p["checks"]["records"]["band"]] += 1

        # week over week, counts and context
        folder_counts = {}
        for folder in FOLDERS:
            lists = folders[folder]["lists"]
            pulled = sum(len(l["tasks"]) if l["tasks"] is not None else l["task_total"]
                         for l in lists)
            folder_counts[folder] = {"lists": len(lists), "tasks": pulled}
            reported = folders[folder]["reported_task_total"]
            if pulled != reported:
                self.method["count_checks"].append(
                    "%s folder: %d task rows pulled against a reported total of %d"
                    % (folder.replace("_", "-"), pulled, reported))
            if folders[folder].get("counts_reused"):
                self.note("%s folder: per-list counts were reused from the prior read because "
                          "its total did not change" % folder.replace("_", "-"))
        prior_as_of = prior_grade = None
        reasons_changed = False
        closed = []
        if self.prior is not None:
            prior = self.prior
            prior_as_of = prior.get("as_of")
            prior_grade = (prior.get("portfolio") or {}).get("grade")
            prior_keys = (prior.get("portfolio") or {}).get("reason_keys")
            if prior_keys is None:
                changed = set((prior.get("portfolio") or {}).get("reasons") or []) != \
                    set(portfolio["reasons"])
            else:
                changed = set(prior_keys) != set(portfolio["keys"])
            reasons_changed = prior_grade == portfolio["grade"] and changed
            now = {(f["project_id"], f["kind"]) for f in fixes}
            prior_fixes = list(prior.get("unattributed") or [])
            for lead in prior.get("leads") or []:
                prior_fixes += lead.get("fix_list") or []
            on_hold = {h["project_id"] for h in held + pending}
            for f in prior_fixes:
                if f.get("project_id") in on_hold:
                    continue
                if (f.get("project_id"), f.get("kind")) not in now:
                    closed.append({"owner": f.get("owner"),
                                   "project_name": f.get("project_name"),
                                   "what": f.get("what")})
            old_counts = (prior.get("method") or {}).get("folder_counts") or {}
            for folder in FOLDERS:
                old = old_counts.get(folder)
                if not old:
                    continue
                new = folder_counts[folder]
                for key, word in (("lists", "lists"), ("tasks", "task rows")):
                    if old.get(key) != new[key]:
                        self.method["count_checks"].append(
                            "%s folder: %d %s now, %s at the prior read"
                            % (folder.replace("_", "-"), new[key], word, old.get(key)))
            if prior.get("config_version") != cfg["config_version"]:
                self.method["measurement_changes"].append(
                    "config version changed from %s to %s" % (prior.get("config_version"),
                                                              cfg["config_version"]))
            old_sub = (prior.get("method") or {}).get("includes_subtasks")
            if old_sub != self.export.get("includes_subtasks", False):
                self.method["measurement_changes"].append(
                    "subtasks were %s at the prior read and are %s now"
                    % ("included" if old_sub else "left out",
                       "included" if self.export.get("includes_subtasks") else "left out"))
        else:
            self.note("No prior read supplied; week-over-week lines are empty")

        overdue = 0
        for lst, _ in active_in:
            _, rows = self.status_rows(lst)
            overdue += sum(1 for t in rows if self.mapped(t["status"]) not in TERMINAL
                           and t["due"] and t["due"] < self.as_of)

        pts = cfg["grading"]["points"]
        bands = cfg["grading"]["project_bands"]
        points_note = ("Project points: %s. Letters: A at %d, B up to %d, C up to %d, D up to "
                       "%d, F above %d or when the list was set up and never used."
                       % (", ".join("%s %d" % (k, pts[k]) for k in core.POINT_KEYS),
                          bands["A"], bands["B"], bands["C"], bands["D"], bands["D"]))
        provisional = any(p["provisional"] for p in projects) or bool(pending)
        complete = not self.method["not_judged"]
        method = {"pulled_at": self.export.get("pulled_at"),
                  "includes_subtasks": self.export.get("includes_subtasks", False),
                  "sources": self.sources, "folder_counts": folder_counts,
                  "filters": filters}
        method.update(self.method)
        return {
            "findings_version": 1,
            "config_version": cfg["config_version"],
            "as_of": self.as_of,
            "prior_as_of": prior_as_of,
            "title": cfg["title"],
            "executive_reader_role": cfg["executive_reader_role"],
            "prepared_by": cfg["prepared_by"],
            "grade_statement": {"measures": cfg["grade_statement"]["measures"],
                                "does_not_measure": cfg["grade_statement"]["does_not_measure"]},
            "cleanup_subtitle": cfg["cleanup"]["subtitle"],
            "complete": complete,
            "portfolio": {"grade": portfolio["grade"], "provisional": provisional,
                          "points_note": points_note, "reasons": portfolio["reasons"],
                          "reason_keys": portfolio["keys"], "prior_grade": prior_grade,
                          "reasons_changed": reasons_changed, "in_scope_count": len(projects),
                          "shares": portfolio["shares"]},
            "inventory": {
                "active": [{"project_id": p["project_id"], "name": p["name"], "url": p["url"]}
                           for p in projects],
                "completed": [{"project_id": l["list_id"], "name": l["name"],
                               "url": self.url(l["list_id"])} for l in kept["completed"]],
                "not_started": [{"project_id": l["list_id"], "name": l["name"],
                                 "url": self.url(l["list_id"])} for l in kept["not_started"]],
                "held": held, "hold_pending": pending, "skipped_templates": skipped},
            "splits": splits,
            "projects": projects,
            "outside_findings": outside,
            "leads": leads_out,
            "unattributed": unattributed,
            "corrections_by_project": [corrections[pid] for pid in order],
            "projects_needing_nothing": [p["name"] for p in projects
                                         if p["project_id"] not in fixed_ids],
            "reporting_well": [p["name"] for p in projects if p["grade"] == "A"],
            "closed_since_prior": closed,
            "judgment_requests": self.requests,
            "method": method,
            "context": {"overdue_tasks_total": overdue},
        }


RECORD_LEADS = {
    "placement_finished_in_active": "Move the list or reopen the work.",
    "roadmap_status_conflict": "Make the roadmap row and the project agree.",
    "roadmap_hold_conflict": "Make the roadmap row and the hold agree.",
    "status_field_stale": "Bring the status field up to date.",
    "owner_mismatch": "Make the status task owner and the entry author agree.",
    "color_field_conflict": "Make the color field and the name agree.",
    "off_record_update": "Put the update in the tracker.",
    "hold_no_dependency": "Name what the hold waits on and who owns it.",
    "placement_started_in_not_started": "Move the list or reset the tasks.",
    "placement_open_in_completed": "Close or move the open work.",
}


# ----------------------------------------------------------------- main

def main(argv=None):
    args = parse_args(argv)
    as_of = core.parse_date(args.as_of, "--as-of").isoformat()
    cfg = core.load_config(args.config)
    export = check_export(core.load_json(args.export, "export"))
    pairs_path = os.path.join(os.path.dirname(os.path.abspath(args.config)),
                              cfg["roadmap"]["pairs_file"])
    pairs = core.parse_pairs(pairs_path)
    known = {l["list_id"] for f in FOLDERS for l in export["folders"][f]["lists"]}
    judgments, off_record = {}, {}
    sources = ["export: %s (pulled %s, %s)" % (os.path.basename(args.export),
                                               export.get("pulled_at"),
                                               export.get("tracker_kind")),
               "config: %s (version %s)" % (os.path.basename(args.config),
                                            cfg["config_version"]),
               "pair file: %s" % os.path.basename(pairs_path)]
    if args.judgments:
        data = core.load_json(args.judgments, "judgments")
        judgments, off_record = check_judgments(data, as_of, known)
        sources.append("judgments: %s (by %s)" % (os.path.basename(args.judgments),
                                                  data.get("judged_by")))
    else:
        sources.append("judgments: none supplied")
    prior = None
    if args.prior:
        prior = core.load_json(args.prior, "prior findings")
        if not isinstance(prior, dict) or prior.get("findings_version") != 1:
            raise InputError("prior findings %s must have findings_version 1" % args.prior)
        prior_date = core.parse_date(prior.get("as_of"), "as_of in --prior %s" % args.prior)
        if prior_date.isoformat() >= as_of:
            raise InputError("--prior %s is dated %s, which is not before the --as-of date %s; "
                             "pass the earlier read's findings" % (args.prior,
                                                                   prior_date.isoformat(),
                                                                   as_of))
        sources.append("prior read: %s (as of %s)" % (os.path.basename(args.prior),
                                                      prior.get("as_of")))
    findings = Grader(cfg, export, pairs, judgments, off_record, prior, as_of, sources).run()
    core.write_json_atomic(args.out, findings)
    pending = len(findings["method"]["not_judged"])
    portfolio = findings["portfolio"]
    if pending:
        sys.stderr.write("%s: wrote %s; %s not judged, so the grade is provisional\n"
                         % (PROG, args.out, plural(pending, "item")))
        return 3
    print("%s: portfolio grade %s, %d projects in scope; wrote %s"
          % (PROG, portfolio["grade"], portfolio["in_scope_count"], args.out))
    return 0


def run():
    try:
        return main()
    except InputError as exc:
        sys.stderr.write("%s: %s\n" % (PROG, exc))
        return 1
    except Exception as exc:  # one clean line, never a traceback
        sys.stderr.write("%s: unexpected error: %s\n" % (PROG, exc))
        return 1


if __name__ == "__main__":
    sys.exit(run())
