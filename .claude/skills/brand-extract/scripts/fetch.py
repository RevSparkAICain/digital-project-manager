"""Bounded HTTP(S) fetch: timeout, size cap, no cookies, no credentials, TLS verified."""
import http.client
import threading
import time
import urllib.request
from urllib.parse import urlparse, urlsplit, urlunsplit

from candidate import SourceError

TIMEOUT_S = 10
TOTAL_TIMEOUT_S = 30
CHUNK = 65536
MAX_BYTES = 5_000_000
USER_AGENT = "brand-extract/1.0"
# http.client.InvalidURL quotes the path and query (or the host), so its text is never logged.
INVALID_URL = "URL contains spaces or control characters, or a non-numeric port"


def public_label(url):
    """The URL as it may appear in logs and outputs: no userinfo, query or fragment.

    Lives here, not in sources/web.py (which imports this module and re-exports it), so that
    fetch's own error messages can use it without an import cycle."""
    try:
        parts = urlsplit(url)
        host = parts.netloc.rsplit("@", 1)[-1]
        return urlunsplit((parts.scheme, host, parts.path, "", ""))
    except ValueError:  # malformed, for example an unclosed IPv6 bracket
        bare = url.split("#")[0].split("?")[0]
        scheme, sep, rest = bare.partition("://")
        if not sep:
            return bare
        netloc, slash, path = rest.partition("/")
        return scheme + sep + netloc.rsplit("@", 1)[-1] + slash + path


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to http(s) targets that carry no credentials."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urlparse(newurl)
        if parts.scheme not in ("http", "https"):
            raise SourceError("redirect to a non-http(s) URL refused: %s"
                              % public_label(newurl))
        if parts.username or parts.password:
            raise SourceError("redirect to a URL with credentials refused")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _download(opener, request, timeout, max_bytes, deadline, url):
    """(body, final URL). Runs in the worker thread that fetch() bounds."""
    with opener.open(request, timeout=timeout) as response:
        final = getattr(response, "url", None) or url
        chunks, size = [], 0
        # read1 returns after one recv, so the deadline is checked between bytes arriving;
        # read(n) would block until n bytes and never reach the check.
        read = getattr(response, "read1", response.read)
        while size <= max_bytes:
            if time.monotonic() > deadline:
                raise SourceError("fetch exceeded %d s: %s"
                                  % (TOTAL_TIMEOUT_S, public_label(url)))
            chunk = read(min(CHUNK, max_bytes + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
    return b"".join(chunks), final


def fetch(url, timeout=TIMEOUT_S, max_bytes=MAX_BYTES):
    """(body bytes, final URL after redirects).

    Every socket operation has its own `timeout`, and the whole request (connect, redirects,
    headers and body) must finish within TOTAL_TIMEOUT_S. The request runs in a daemon worker
    thread; when the deadline passes, SourceError is raised and that thread is abandoned. The
    abandoned thread is not guaranteed to end soon: `timeout` applies to each receive, so a
    server that keeps trickling bytes can keep it alive until the process exits. Because it is
    a daemon thread, it never blocks that exit.

    Error messages name the URL by public_label (no userinfo, query or fragment), because the
    caller logs them."""
    label = public_label(url)
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise SourceError("only http and https URLs are fetched: %s" % label)
    if parts.username or parts.password:
        raise SourceError("URLs with credentials are refused")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(_SafeRedirect)  # no cookie jar
    deadline = time.monotonic() + TOTAL_TIMEOUT_S
    outcome = {}

    def work():
        try:
            outcome["value"] = _download(opener, request, timeout, max_bytes, deadline, url)
        except http.client.InvalidURL:
            outcome["error"] = SourceError("fetch failed for %s: %s" % (label, INVALID_URL))
        except (OSError, http.client.HTTPException) as err:
            outcome["error"] = SourceError("fetch failed for %s: %s" % (label, err))
        except BaseException as err:  # noqa: BLE001 - re-raised in the calling thread
            outcome["error"] = err

    worker = threading.Thread(target=work, name="brand-extract-fetch", daemon=True)
    worker.start()
    worker.join(max(0.0, deadline - time.monotonic()))
    if worker.is_alive():
        raise SourceError("fetch exceeded %d s: %s" % (TOTAL_TIMEOUT_S, label))
    if "error" in outcome:
        raise outcome["error"]
    data, final = outcome["value"]
    if len(data) > max_bytes:
        raise SourceError("response over %d bytes: %s" % (max_bytes, label))
    return data, final


def fetch_bytes(url, timeout=TIMEOUT_S, max_bytes=MAX_BYTES):
    """The body only; see fetch()."""
    return fetch(url, timeout=timeout, max_bytes=max_bytes)[0]
