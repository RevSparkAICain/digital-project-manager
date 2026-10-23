"""Website adapter: colors, fonts and type scale from a page's HTML and CSS, plus logo hints.

Standard library only. Reads the page, its <style> blocks, inline style attributes and every
linked stylesheet; it does not crawl other pages or follow @import. A stylesheet that cannot be
read is skipped and the page kept. Relative links resolve against the final URL after
redirects, or an http(s) <base href>. With render=True the HTML comes from agent-browser, so a
page built by scripts exposes its final markup.
"""
import glob
import os
import html as htmllib
import re
import shutil
import subprocess
import time
from urllib.parse import urljoin, urlparse

import color
import fetch
import fonts
from candidate import Candidate, SourceError
from fetch import public_label  # defined in fetch so its errors use it; part of this API

COLOR_PROPS = {"color", "background", "background-color", "border", "border-color",
               "border-top", "border-right", "border-bottom", "border-left", "outline",
               "outline-color", "fill", "stroke", "text-decoration-color"}
_EDGE = r"(?:^|(?<=[\s,>+~]))"
_END = r"(?=$|[\s,>+~:.\[#])"
KEY_SELECTOR = re.compile(
    _EDGE + r"(?:body|html|h1|h2|h3|a|button|header|nav|\.btn[\w-]*)" + _END)
HEADING_SELECTOR = re.compile(_EDGE + r"h[1-6]" + _END)
KEY_WEIGHT = 3.0
MAX_CSS_CHARS = 1_000_000
MAX_STYLESHEETS = 20
MAX_VAR_CHARS = 4096
MAX_HTML_CHARS = 2_000_000
MAX_TAG_CHARS = 4096
AGENT_BROWSER_TIMEOUT_S = 60
_LOWER = {c: c + 32 for c in range(65, 91)}
_ATTR = re.compile(r"""([^\s"'<>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+)))?""")
_TAGNAME = re.compile(r"[A-Za-z][^\s/>]*")
_TOKENS = re.compile(r"([{}])")
_VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^)]{0,256}))?\)")
_SIZE = re.compile(r"\s*([0-9]*\.?[0-9]+)\s*(px|rem|em|pt|%)\s*")
LOGO_EXTS = (".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico")
STYLESHEET_BUDGET_S = 60
CMD_UNSAFE = set('&|<>^%"`()!')
_SHIM_TARGET = re.compile(r'"%~dp0([^"%*?<>|]+?\.exe)"', re.IGNORECASE)


def logo_ext(ref):
    """Lowercase extension of a local path or an http(s) URL's path, or '' when none."""
    remote = urlparse(ref).scheme in ("http", "https")
    return os.path.splitext(urlparse(ref).path if remote else ref)[1].lower()


class _Page:
    """What the scanner collects from one page."""

    def __init__(self):
        self.stylesheets, self.styles, self.inline, self.logos = [], [], [], []
        self.base = None

    def add_tag(self, tag, a):
        if tag == "base" and self.base is None and a.get("href"):
            self.base = a["href"]  # only the first <base> counts, as in a browser
        rel = a.get("rel", "").lower().split()
        if tag == "link" and "stylesheet" in rel and a.get("href"):
            self.stylesheets.append(a["href"])
        elif tag == "link" and "icon" in rel and a.get("href"):
            self.logos.append((a["href"], 0.5, "site icon link"))
        if tag == "img" and a.get("src"):
            hay = " ".join(a.get(k, "") for k in ("src", "alt", "class", "id")).lower()
            if "logo" in hay:
                self.logos.append((a["src"], 1.0, "<img> marked as logo"))
        if a.get("style"):
            self.inline.append(a["style"])


def _attrs(text):
    out = {}
    for m in _ATTR.finditer(text):
        value = m.group(2) if m.group(2) is not None else (
            m.group(3) if m.group(3) is not None else (m.group(4) or ""))
        out[m.group(1).lower()] = htmllib.unescape(value)
    return out


def scan_html(html):
    """Linear scan for the tags the adapter reads. Not a validating parser: comments are
    skipped, an over-long tag is skipped whole, and scanning stops at the first unclosed
    construct."""
    html = html[:MAX_HTML_CHARS]
    low = html.translate(_LOWER)
    page = _Page()
    i, n = 0, len(html)
    while i < n:
        i = html.find("<", i)
        if i < 0:
            break
        if html.startswith("<!--", i):
            k = html.find("-->", i + 4)
            if k < 0:
                break
            i = k + 3
            continue
        j = html.find(">", i + 1)
        if j < 0:
            break
        text = html[i + 1:j]
        i = j + 1
        if len(text) > MAX_TAG_CHARS:
            continue
        m = _TAGNAME.match(text)
        if not m:
            continue
        tag = m.group(0).lower()
        page.add_tag(tag, _attrs(text[m.end():]))
        if tag == "style":
            end = low.find("</style", i)
            if end < 0:
                page.styles.append(html[i:])
                break
            page.styles.append(html[i:end])
            k = html.find(">", end)
            if k < 0:
                break
            i = k + 1
    return page


def _strip_comments(css):
    out, pos = [], 0
    while True:
        i = css.find("/*", pos)
        if i < 0:
            out.append(css[pos:])
            break
        out.append(css[pos:i])
        j = css.find("*/", i + 2)
        if j < 0:  # unterminated comment drops the rest
            break
        pos = j + 2
    return "".join(out)


def parse_rules(css):
    """[(selector, [(property, value)])] from a stylesheet. @-rule preludes are dropped; the
    rules inside an @media block are kept as ordinary rules. Linear in the input size."""
    css = _strip_comments(css[:MAX_CSS_CHARS])
    tokens = _TOKENS.split(css)
    out, stack = [], []  # stack entries: [selector, has_nested_block]
    for i, tok in enumerate(tokens):
        if tok == "{":
            if stack:
                stack[-1][1] = True
            selector = " ".join(tokens[i - 1].rsplit(";", 1)[-1].split()) if i else ""
            stack.append([selector, False])
        elif tok == "}":
            if not stack:
                continue
            selector, nested = stack.pop()
            if not nested and selector and not selector.startswith("@"):
                out.append((selector, parse_declarations(tokens[i - 1])))
    return out


def parse_declarations(body):
    out = []
    for part in body.split(";"):
        if ":" in part:
            prop, value = part.split(":", 1)
            out.append((prop.strip().lower(), value.replace("!important", "").strip()))
    return out


def _resolve(value, custom, cache, depth=0, active=()):
    value = value[:MAX_VAR_CHARS]
    if depth > 8:
        return value if len(value) <= MAX_VAR_CHARS else ""

    def sub(m):
        name = m.group(1)
        if name not in custom:
            return m.group(2) or ""
        if name in cache:
            return cache[name]
        if name in active:  # cycle
            return ""
        cache[name] = _resolve(custom[name], custom, cache, depth + 1, active + (name,))
        return cache[name]

    out = _VAR.sub(sub, value)
    return out if len(out) <= MAX_VAR_CHARS else ""


def _to_px(value, ref):
    m = _SIZE.fullmatch(value)
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    return {"px": n, "rem": n * 16.0, "em": n * ref, "pt": n * 4 / 3, "%": n * ref / 100}[unit]


def _locate(where, href):
    """Resolve a link against the page, or None when the target is unsafe to load."""
    href = href.strip()
    if urlparse(where).scheme in ("http", "https"):
        target = href if urlparse(href).scheme else urljoin(where, href)
        parts = urlparse(target)
        if parts.scheme not in ("http", "https") or parts.username or parts.password:
            return None
        return target
    if urlparse(href).scheme or re.match(r"^[A-Za-z]:", href) or href[:1] in ("/", "\\"):
        return None
    rel = href.split("#")[0].split("?")[0]
    if not rel:
        return None
    root = os.path.realpath(where)
    result = os.path.normpath(os.path.join(where, rel))
    try:
        if os.path.commonpath([root, os.path.realpath(result)]) != root:
            return None
    except ValueError:
        return None
    return result


def _tally(table, key, weight, selector, prop, value):
    entry = table.setdefault(key, [0.0, 0, "%s { %s: %s }" % (selector[:60], prop, value[:60])])
    entry[0] += weight
    entry[1] += 1


def _evidence(entry):
    return "%d CSS declaration(s), first: %s" % (entry[1], entry[2])


def _base(where, href):
    """The page's <base href> resolved against its URL, when both are http(s) and carry no
    credentials; otherwise `where` unchanged. A local file ignores <base>, so its links stay
    inside its own folder."""
    if not href or urlparse(where).scheme not in ("http", "https"):
        return where
    target = urljoin(where, href.strip())
    parts = urlparse(target)
    if parts.scheme not in ("http", "https") or parts.username or parts.password:
        return where
    return target


def _sheet_label(location):
    if urlparse(location).scheme in ("http", "https"):
        return public_label(location)
    return os.path.basename(location)


def from_html(html, where, label, load_css, notes=None):
    """Candidates from one page. `where` resolves relative links: the page URL, or the folder
    that holds a local file. load_css(location) returns a linked stylesheet's text and raises
    SourceError when it cannot; that sheet is skipped and the page is kept. Stylesheets stop
    loading once STYLESHEET_BUDGET_S has passed. Each skipped sheet adds a line to `notes`."""
    notes = [] if notes is None else notes
    page = scan_html(html)
    where = _base(where, page.base)
    sheets = list(page.styles)
    started = time.monotonic()
    for href in page.stylesheets[:MAX_STYLESHEETS]:
        if time.monotonic() - started > STYLESHEET_BUDGET_S:
            notes.append("stopped loading stylesheets after %d s" % STYLESHEET_BUDGET_S)
            break
        location = _locate(where, href)
        if location is None:
            continue
        try:
            sheets.append(load_css(location))
        except SourceError as err:
            notes.append("skipped stylesheet %s: %s" % (_sheet_label(location), err))
    rules = [rule for sheet in sheets for rule in parse_rules(sheet)]
    rules += [("[style]", parse_declarations(style)) for style in page.inline]
    custom = {p: v for _sel, decls in rules for p, v in decls if p.startswith("--")}
    cache = {}

    colors, families = {}, {}
    base_value = h1_value = None
    for selector, decls in rules:
        weight = KEY_WEIGHT if KEY_SELECTOR.search(selector) else 1.0
        parts = {s.strip() for s in selector.split(",")}
        for prop, raw in decls:
            if prop.startswith("--"):
                continue
            value = _resolve(raw, custom, cache)
            if prop in COLOR_PROPS:
                for hexv in color.find_colors(value):
                    _tally(colors, hexv, weight, selector, prop, value)
            elif prop == "font-family":
                family = fonts.first_family(value)
                if family:
                    role = "heading" if HEADING_SELECTOR.search(selector) else "body"
                    _tally(families, (role, family), weight, selector, prop, value)
            elif prop == "font-size":
                if base_value is None and parts & {"html", "body"}:
                    base_value = value
                if h1_value is None and "h1" in parts:
                    h1_value = value

    src = "web:" + label
    cands = [Candidate("color", k, v[0], src, _evidence(v)) for k, v in sorted(colors.items())]
    cands += [Candidate("font", k, v[0], src, _evidence(v)) for k, v in sorted(families.items())]
    base_px = _to_px(base_value, 16.0) if base_value else None
    if base_px:
        cands.append(Candidate("layout", ("baseFontPx", round(base_px, 2)), 1.0, src,
                               "html/body font-size: %s" % base_value))
    h1_px = _to_px(h1_value, base_px or 16.0) if h1_value else None
    if h1_px:
        cands.append(Candidate("layout", ("headingScale", round(h1_px / (base_px or 16.0), 2)),
                               1.0, src, "h1 font-size: %s" % h1_value))
    for href, weight, why in page.logos:
        location = _locate(where, href)
        if location is not None and logo_ext(location) in LOGO_EXTS:
            cands.append(Candidate("logo", location, weight, src, why))
    return cands


def _read_local(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(MAX_CSS_CHARS)
    except OSError:
        raise SourceError("linked stylesheet not found: %s" % os.path.basename(path))


def _read_remote(url):
    if urlparse(url).scheme not in ("http", "https"):
        raise SourceError("stylesheet is not an http(s) URL: %s" % public_label(url))
    return fetch.fetch_bytes(url).decode("utf-8", "replace")


def extract_file(path, notes=None):
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read(MAX_HTML_CHARS)
    return from_html(html, os.path.dirname(os.path.abspath(path)), os.path.basename(path),
                     _read_local, notes=notes)


def extract_url(url, render=False, runner=subprocess.run, notes=None):
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise SourceError("only http and https URLs are fetched")
    if parts.username or parts.password:
        raise SourceError("URLs with credentials are refused")
    # Fetch the URL as given (a query can select content); label without query or fragment.
    label = public_label(url)
    where = url
    if render:
        html = rendered_html(url, runner)
    else:
        data, where = fetch.fetch(url)  # relative links resolve against the final URL
        html = data.decode("utf-8", "replace")
    return from_html(html, where, label, _read_remote, notes=notes)


def _native_from_shim(shim):
    """The native executable an npm .cmd shim launches, when it lives under the shim's folder,
    or None. Running it directly keeps cmd.exe (and its parsing of & | < > ^ %) out of the way."""
    folder = os.path.dirname(os.path.abspath(shim))
    found = []
    try:
        with open(shim, encoding="utf-8", errors="replace") as fh:
            text = fh.read(65536)
        found = [os.path.normpath(os.path.join(folder, *re.split(r"[\\/]", m.group(1))))
                 for m in _SHIM_TARGET.finditer(text)]
    except OSError:
        pass
    found += sorted(glob.glob(os.path.join(folder, "node_modules", "agent-browser", "bin", "*.exe")))
    for exe in found:
        try:
            inside = os.path.commonpath([folder, os.path.abspath(exe)]) == folder
        except ValueError:
            inside = False
        if inside and os.path.isfile(exe):
            return exe
    return None


def _agent_browser():
    """(program, through_cmd): the agent-browser program to launch, and whether Windows will
    run it through cmd.exe because it is a .cmd or .bat file."""
    path = shutil.which("agent-browser")  # on Windows this is usually the npm .CMD shim
    if path is None:
        raise SourceError("agent-browser is not installed or not on PATH")
    if os.path.splitext(path)[1].lower() in (".cmd", ".bat"):
        native = _native_from_shim(path)
        return (native, False) if native else (path, True)
    return path, False


def rendered_html(url, runner=subprocess.run):
    """The page's final markup from agent-browser. The executable path is passed explicitly
    because the CLI does not reliably read AGENT_BROWSER_EXECUTABLE_PATH on its own.

    A .cmd shim is bypassed when it names a bundled native executable. When it cannot be
    bypassed, cmd.exe would read the URL as shell syntax, so a URL carrying any cmd.exe
    metacharacter or whitespace is refused instead of being launched."""
    exe = os.environ.get("AGENT_BROWSER_EXECUTABLE_PATH")
    exe_path, through_cmd = _agent_browser()
    label = public_label(url)
    if through_cmd and any(ch in CMD_UNSAFE or ch.isspace() for ch in url):
        raise SourceError("agent-browser runs through a .cmd shim here, which would treat parts "
                          "of this URL as commands; pass the page without the characters "
                          "& | < > ^ %% \" ` ( ) ! or spaces: %s" % label)

    def run(args):
        # A timeout's text repeats the command line (as a list, backslashes doubled), so it gets
        # a fixed reason. agent-browser may echo the URL: the URL in its output is replaced by
        # its public label (extract.collect also scrubs any query left in another form).
        try:
            res = runner([exe_path] + args, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=AGENT_BROWSER_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise SourceError("agent-browser %s failed: timed out after %d s"
                              % (args[0], AGENT_BROWSER_TIMEOUT_S)) from None
        except OSError as err:
            raise SourceError("agent-browser %s failed: %s"
                              % (args[0], str(err).replace(url, label)))
        if res.returncode != 0:
            detail = (res.stderr or res.stdout or "").replace(url, label).strip()[:200]
            raise SourceError("agent-browser %s failed: %s" % (args[0], detail))
        return res.stdout

    run(["open", url] + (["--executable-path", exe] if exe else []))
    try:
        return "<html>%s</html>" % run(["get", "html", "html"])
    finally:
        try:
            run(["close"])
        except SourceError:
            pass
