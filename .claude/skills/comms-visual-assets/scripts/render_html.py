"""Render an HTML asset to a PNG with a headless Chromium-family browser (Chromium, Chrome, Edge).

Usage: python render_html.py <page.html> --out <file.png> [--width 1200] [--height 675] [--chromium PATH]
The browser comes from --chromium, then the CHROMIUM_PATH environment variable, then the usual
names on PATH, then the default Edge and Chrome locations on Windows. The PNG is rewritten
without text and time chunks so it carries no tool or path metadata.
Standard library only. Exit code 0 on success, 2 when no browser is found, 1 when rendering fails.
"""
import argparse
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

NAMES = ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge")
WINDOWS_PATHS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)
PNG_SIG = b"\x89PNG\r\n\x1a\n"
DROP = {b"tEXt", b"iTXt", b"zTXt", b"tIME"}
TIMEOUT_SECONDS = 60


def find_chromium(explicit=None, environ=None):
    """An explicit or CHROMIUM_PATH value is used as given (None when it is not a file)."""
    environ = os.environ if environ is None else environ
    for candidate in (explicit, environ.get("CHROMIUM_PATH")):
        if candidate:
            return candidate if os.path.isfile(candidate) else None
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return found
    if os.name == "nt":
        for path in WINDOWS_PATHS:
            if os.path.isfile(path):
                return path
    return None


def build_command(chromium, html, out, width, height, profile):
    return [chromium, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--no-first-run", f"--user-data-dir={profile}",
            f"--window-size={width},{height}", f"--screenshot={os.path.abspath(out)}",
            pathlib.Path(os.path.abspath(html)).as_uri()]


def strip_text_chunks(data):
    if not data.startswith(PNG_SIG):
        raise ValueError("not a PNG file")
    out, pos = [PNG_SIG], len(PNG_SIG)
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        end = pos + 12 + length
        if data[pos + 4:pos + 8] not in DROP:
            out.append(data[pos:end])
        pos = end
    return b"".join(out)


def render(html, out, width=1200, height=675, chromium=None):
    browser = find_chromium(chromium)
    if browser is None:
        raise FileNotFoundError("no Chromium-family browser found; set CHROMIUM_PATH")
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(build_command(browser, html, out, width, height, profile),
                       check=True, timeout=TIMEOUT_SECONDS,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(out, "rb") as fh:
        data = strip_text_chunks(fh.read())
    with open(out, "wb") as fh:
        fh.write(data)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("html")
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=675)
    parser.add_argument("--chromium", default=None)
    args = parser.parse_args(argv)
    if find_chromium(args.chromium) is None:
        print("render_html: no Chromium-family browser found; set CHROMIUM_PATH", file=sys.stderr)
        return 2
    try:
        render(args.html, args.out, args.width, args.height, args.chromium)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"render_html: {exc}", file=sys.stderr)
        return 1
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
