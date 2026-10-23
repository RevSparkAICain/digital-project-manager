"""brand-extract command line: learn a visual brand from collateral and write the profile.

    python extract.py --name "ACME Co." --out <folder> --file deck.pptx --file guide.pdf \\
        --file site/index.html --url https://acme.example/ [--render] [--slug acme] \\
        [--blurb-file blurb.txt]

Writes brand.json, tokens.css, template.pptx, template.docx, logo.<ext> and
<slug>-brand/SKILL.md into --out. Each source is read on its own: one that fails is logged
and skipped. Exit 0 when at least one source gave values (warnings may still print); exit 1
when none did, and then nothing is written. Outputs are built in a staging folder beside --out
and moved in only once every one is complete. The move itself is all or nothing: files it
would replace are backed up first and put back if any step fails (for example a template held
open in Word), so a failure part-way leaves --out as it was. If a file cannot be put back
either, the run says which (could not restore: an earlier file did not go back; could not
remove: a new file with no earlier version stayed), keeps any previous copies in
.brand-extract-backup-<suffix> beside --out (or, if that move fails, in the backup folder of
the .brand-extract-<suffix> staging folder), and exits 1. The same folder keeps them when the
run is interrupted part-way through the move.
"""
import argparse
import functools
import os
import re
import secrets
import shutil
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import emit_skill  # noqa: E402
import emit_templates  # noqa: E402
import emit_tokens  # noqa: E402
import fetch  # noqa: E402
import merge  # noqa: E402
from candidate import SourceError, normalize  # noqa: E402
from sources import image, office, pdf, web  # noqa: E402

READ_ERRORS = (SourceError, OSError, ValueError, zipfile.BadZipFile, ET.ParseError)
EXT_SHAPE = re.compile(r"^\.[a-z]{3,4}$")
MAX_LOGO_BYTES = 5_000_000
TOKEN = re.compile(r"[^\s'\"]+")  # runs of text between whitespace and quotes
SLASH = re.compile(r"/|%2f", re.IGNORECASE)
URL_MARK = re.compile(r"[?#]|%3f|%23", re.IGNORECASE)


def _cut_query(match):
    token = match.group()
    slash = SLASH.search(token)
    mark = URL_MARK.search(token, slash.end()) if slash else None
    return token[:mark.start()] if mark else token


def scrub_urls(text):
    """Error text with the query and fragment cut from every URL-like token: in a token (text
    between whitespace and quotes) holding a "/" (or "%2F"), the first "?" or "#" (or "%3F" or
    "%23") after it and everything after that. Linear in the length of the text.

    Adapter errors can repeat a URL in forms its public label cannot match (fragment dropped,
    percent-encoded, backslashes doubled), so every logged reason passes through here."""
    return TOKEN.sub(_cut_query, str(text))


def adapter_for(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in office.EXTS:
        return office.extract
    if ext == ".pdf":
        return pdf.extract
    if ext in (".html", ".htm"):
        return web.extract_file
    if ext == ".svg" or ext in image.RASTER:
        return image.extract
    return None


def collect(files, urls, render, log):
    """Run every source through its adapter. Returns (candidates, labels of sources used)."""
    jobs = [(path, os.path.basename(path), adapter_for(path)) for path in files]
    # A URL is labelled without userinfo, query or fragment: a signed link must not leak into
    # the log or the generated skill.
    jobs += [(url, web.public_label(url), functools.partial(web.extract_url, render=render))
             for url in urls]
    cands, used = [], []
    for target, label, adapter in jobs:
        if adapter is None:
            log("skipped %s: unsupported file type" % label)
            continue
        notes = []  # web pages report skipped stylesheets here
        if adapter is web.extract_file or getattr(adapter, "func", None) is web.extract_url:
            adapter = functools.partial(adapter, notes=notes)
        try:
            found = normalize(adapter(target))
        except READ_ERRORS as err:
            log("skipped %s: %s" % (label, scrub_urls(err)))
            continue
        except Exception as err:  # noqa: BLE001 - one hostile source must not end the run
            log("skipped %s: unexpected error: %s" % (label, scrub_urls(err)))
            continue
        finally:
            for note in notes:
                log("%s: %s" % (label, scrub_urls(note)))
        if not found:
            log("skipped %s: no brand values found" % label)
            continue
        cands += found
        used.append(label)
    return cands, used


def place_logo(ref, out_dir):
    """Copy (or download) the chosen logo unchanged to <out_dir>/logo.<ext>.

    Only image files qualify: the extension must be in the image allowlist and nothing else
    is read, so a page cannot make the profile carry a sibling document. The extension check
    runs before any fetch or copy."""
    ext = web.logo_ext(ref)
    if ext not in web.LOGO_EXTS or not EXT_SHAPE.fullmatch(ext):
        raise SourceError("logo is not an image file")
    name = "logo" + ext
    if urlparse(ref).scheme in ("http", "https"):
        data = fetch.fetch_bytes(ref)  # fetch first, so a failed download writes no file
        with open(os.path.join(out_dir, name), "wb") as fh:
            fh.write(data)
        return name
    if not os.path.isfile(ref):
        raise SourceError("logo file not found")
    if os.path.getsize(ref) > MAX_LOGO_BYTES:
        raise SourceError("logo file is larger than 5 MB")
    shutil.copyfile(ref, os.path.join(out_dir, name))
    return name


def build_outputs(profile, args, slug, used, blurb, staging):
    """Write every output into the staging folder. Returns (brand, SKILL.md path relative to it)."""
    logo = None
    if profile["logo"]:
        try:
            logo = place_logo(profile["logo"], staging)
        except (OSError, SourceError) as err:
            print("logo not copied: %s" % scrub_urls(err))
    brand = emit_tokens.build_brand(profile, args.name, logo_file=logo,
                                    templates={"pptx": "template.pptx", "docx": "template.docx"})
    for kind, writer in (("pptx", emit_templates.write_pptx), ("docx", emit_templates.write_docx)):
        try:
            writer(brand, os.path.join(staging, brand["templates"][kind]))
        except ImportError as err:
            brand["templates"][kind] = None
            brand["warnings"].append("WARNING: template.%s skipped (%s)" % (kind, err))
    emit_tokens.write_tokens(brand, staging)
    if blurb is None:
        blurb = emit_skill.default_blurb(brand, used)
    skill_path = emit_skill.write_skill(brand, staging, slug, blurb)
    return brand, os.path.relpath(skill_path, staging)


def _makedirs(path, created):
    """os.makedirs that records, outermost first, every folder it had to create."""
    missing = []
    while path and not os.path.isdir(path):
        missing.append(path)
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    for folder in reversed(missing):
        os.mkdir(folder)
        created.append(folder)


class RestoreFailed(Exception):
    """publish failed and could not put every file in --out back as it was.

    `error` is the failure that stopped the move. `unrestored` names the files (relative to
    --out) that existed before and whose previous copy did not go back; `unremoved` names new
    files, with no previous copy, that could not be removed. `backup` is the folder that holds
    any previous copies that could not be moved back."""

    def __init__(self, error, unrestored, unremoved, backup):
        super().__init__(str(error))
        self.error, self.backup = error, backup
        self.unrestored, self.unremoved = unrestored, unremoved


def publish(staging, out):
    """Move every staged file into --out, all or nothing.

    Every destination file about to be replaced, and every stale logo (a logo name this tool
    writes that the new run did not produce), is first moved into a backup folder inside
    staging; then the new files are moved in, and on success the backup folder is removed. If
    any step fails, the new files are removed, the backups go back where they were, and the
    error is raised again, so --out is left as it was. If any file cannot be put back (for
    example one that another program holds open), RestoreFailed is raised instead, naming
    those files; the backup folder is left in place. An interrupt (KeyboardInterrupt or
    SystemExit) is always raised again as itself; whatever it left in the backup folder stays
    there for the caller to keep (see release_staging)."""
    plan = []
    for root, _dirs, files in os.walk(staging):
        rel = os.path.relpath(root, staging)
        for name in files:
            plan.append((os.path.join(root, name), os.path.normpath(os.path.join(out, rel, name))))
    # Only names this tool writes ("logo" + an allowlisted extension) are candidates for removal.
    ours = {"logo" + ext for ext in web.LOGO_EXTS}
    fresh = {name for name in os.listdir(staging) if name in ours}
    stale = []
    if os.path.isdir(out):
        stale = [os.path.join(out, name) for name in sorted(os.listdir(out))
                 if name in ours and name not in fresh and os.path.isfile(os.path.join(out, name))]
    backup = os.path.join(staging, "backup")
    created, moved, placed = [], [], []
    try:
        _makedirs(out, created)
        for dest in [d for _src, d in plan if os.path.lexists(d)] + stale:
            saved = os.path.join(backup, os.path.relpath(dest, out))
            _makedirs(os.path.dirname(saved), [])
            os.replace(dest, saved)
            moved.append((saved, dest))
        for src, dest in plan:
            _makedirs(os.path.dirname(dest), created)
            os.replace(src, dest)
            placed.append(dest)
    except BaseException as err:
        stuck = set()  # new files that could not be removed
        for dest in reversed(placed):
            try:
                os.remove(dest)
            except OSError:
                stuck.add(dest)
        unrestored = set()  # files that existed before and did not go back
        for saved, dest in reversed(moved):
            try:
                os.replace(saved, dest)
                stuck.discard(dest)  # the previous copy is back over the new one
            except OSError:
                unrestored.add(dest)
        stuck -= unrestored  # a previous copy that did not go back is reported as that
        for folder in reversed(created):
            try:
                os.rmdir(folder)  # only succeeds while the folder is empty
            except OSError:
                pass
        if (unrestored or stuck) and isinstance(err, Exception):
            def rel(dests):
                return sorted(os.path.relpath(dest, out) for dest in dests)
            raise RestoreFailed(err, rel(unrestored), rel(stuck), backup) from err
        raise
    shutil.rmtree(backup, ignore_errors=True)  # the previous output is replaced for good


def _holds_file(folder):
    """True when folder, or any folder below it, contains a file."""
    return any(files for _root, _dirs, files in os.walk(folder))


def keep_backup(backup, parent):
    """Move the backup folder to <parent>/.brand-extract-backup-<suffix>, out of the staging
    folder that is about to be removed. Returns the new folder, or None if it could not move."""
    for _ in range(10):
        kept = os.path.join(parent, ".brand-extract-backup-" + secrets.token_hex(4))
        if os.path.lexists(kept):
            continue
        try:
            os.rename(backup, kept)
        except OSError:
            return None
        return kept
    return None


def release_staging(staging, parent):
    """Remove the staging folder, unless its backup folder still holds a file.

    The decision rests on what the backup folder holds, not on how the run ended, so an
    interrupt part-way through publish or its restore cannot delete the only copy of a previous
    output. A backup that holds a file is moved to <parent>/.brand-extract-backup-<suffix>; if
    that move fails, the staging folder is left in place. Returns the folder that now holds the
    previous copies, or None when there were none."""
    backup = os.path.join(staging, "backup")
    kept = None
    if _holds_file(backup):
        kept = keep_backup(backup, parent) or backup
    if kept != backup:  # staging no longer holds anything worth keeping
        shutil.rmtree(staging, ignore_errors=True)
    return kept


def failure_message(err, existed, kept):
    """The one line printed when publish fails. `kept` is the folder holding previous copies."""
    if isinstance(err, RestoreFailed):
        parts = ["failed: %s" % err.error]
        if err.unrestored:
            parts.append("could not restore %s" % ", ".join(err.unrestored))
        if err.unremoved:
            parts.append("could not remove %s" % ", ".join(err.unremoved))
    elif kept:  # the restore did not finish, so it cannot claim the output is as it was
        parts = ["failed: %s" % err]
    else:
        parts = ["failed: %s" % err, "previous output restored" if existed else "nothing written"]
    if kept:
        parts.append("previous copies kept in %s" % kept)
    return "; ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Learn a visual brand from collateral.")
    ap.add_argument("--name", required=True, help='company name, for example "ACME Co."')
    ap.add_argument("--out", required=True, help="folder for the brand profile (usually brand/)")
    ap.add_argument("--file", action="append", default=[],
                    help="a .pptx/.potx/.docx/.dotx, .pdf, .html, .svg or image file (repeatable)")
    ap.add_argument("--url", action="append", default=[], help="an http(s) page (repeatable)")
    ap.add_argument("--render", action="store_true", help="load --url pages through agent-browser")
    ap.add_argument("--slug", help="the generated skill is <slug>-brand (default: from --name)")
    ap.add_argument("--blurb-file", help="text file whose paragraph replaces the default blurb")
    args = ap.parse_args(argv)
    if not args.file and not args.url:
        ap.error("give at least one --file or --url")
    slug = args.slug or emit_skill.slugify(args.name)
    if not emit_skill.SLUG.fullmatch(slug):
        ap.error("--slug must be lowercase letters, digits and single hyphens")
    if args.blurb_file and not os.path.isfile(args.blurb_file):
        ap.error("--blurb-file not found: %s" % args.blurb_file)
    blurb = None
    if args.blurb_file:
        # Validate before any work or output, so a bad blurb cannot leave a partial profile.
        try:
            with open(args.blurb_file, encoding="utf-8") as fh:
                blurb = fh.read()
            emit_skill.validate_blurb(blurb)
        except (OSError, ValueError) as err:
            ap.error("--blurb-file: %s" % err)

    cands, used = collect(args.file, args.url, args.render, print)
    if not cands:
        print("no source yielded brand values; nothing written")
        return 1

    staging = None
    try:
        try:
            profile = merge.merge(cands)
            out_parent = os.path.dirname(os.path.abspath(args.out))
            os.makedirs(out_parent, exist_ok=True)
            staging = tempfile.mkdtemp(prefix=".brand-extract-", dir=out_parent)
            brand, skill_rel = build_outputs(profile, args, slug, used, blurb, staging)
        except Exception as err:  # noqa: BLE001 - any failure must leave --out untouched
            print("failed: %s; nothing written" % scrub_urls(err))
            return 1
        existed = os.path.exists(args.out)
        try:
            publish(staging, args.out)
        except Exception as err:  # noqa: BLE001 - publish has put back all it could
            kept, staging = release_staging(staging, out_parent), None
            print(failure_message(err, existed, kept))
            return 1
    finally:
        # Reached with staging set after a build failure, a success or an interrupt: it keeps any
        # previous copy still in the backup folder, whichever way the run ended.
        if staging is not None:
            kept = release_staging(staging, out_parent)
            if kept:
                try:
                    print("previous copies kept in %s" % kept)
                except Exception:  # noqa: BLE001 - stdout may already be gone
                    pass

    c, f = brand["colors"], brand["fonts"]
    print("brand profile written to %s: primary %s, background %s, text %s, heading font %s, "
          "body font %s; %d source(s) used"
          % (args.out, c["primary"], c["background"], c["text"], f["officeHeading"],
             f["office"], len(used)))
    print("generated skill: %s" % os.path.join(args.out, skill_rel))
    for line in brand["adjustments"]:
        print("adjusted: %s" % line)
    for line in brand["warnings"]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
