#!/usr/bin/env python3
"""Obscura Guard — fetch one page for the dashboard Jelajah (Browse) tab.

Runs the Obscura headless browser (read-only) and writes a browse record:
title, rendered text, links, and a screenshot. The dashboard backend does
NOT run the browser — this script is the fetch step, run by the agent (or
the guard cron) for each PENDING browse request, and the record is then
submitted to the dashboard via the submitbrowseresult action.

Usage:
  python3 obscura_browse.py <URL> [--source dashboard] [--id <id-antrean>]
      [--out-dir /home/hatch/workspace/obscura-guard/browse]

Output: <out-dir>/<id>.json (+ <id>.png screenshot, <id>_thumb.jpg
thumbnail) and an appended line in <out-dir>/browse.jsonl. The record is
also printed to stdout as JSON.

Record keys on disk (14): id, url, domain, requested_at, status
("SELESAI" | "GAGAL"), title, text (max 8000 chars), links
([{href, text}], max 100), screenshot (full-PNG filename),
screenshot_thumb (thumbnail filename or null), fetched_at,
fetched_at_wib, error (null on success), source. The dashboard record
has 13 keys (no screenshot_thumb): submit with screenshot set to the
data URL of the THUMBNAIL (small, ~15-25 KB) when one exists, else the
data URL of the full PNG, else null.

The --id flag takes the PENDING browse id from listpendingbrowse so the
submit overwrites that queue row instead of creating a duplicate.

Network calls: Obscura subprocess only. Thumbnail needs Pillow (PIL);
if PIL is missing the full screenshot is still saved and
screenshot_thumb is null.
"""

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

OBSCURA_BIN = "/home/hatch/workspace/obscura/target/release/obscura"
DEFAULT_OUT_DIR = "/home/hatch/workspace/obscura-guard/browse"
OBSCURA_TIMEOUT = 120          # seconds, obscura --timeout (navigation)
SUBPROCESS_TIMEOUT = 150       # seconds, hard cap per obscura call
MAX_TEXT_CHARS = 8000
MAX_LINKS = 100
THUMB_WIDTH = 800
THUMB_QUALITY = 70

BANNER_FETCH_RE = re.compile(r"^Fetching\s+\S+")
BANNER_LOADED_RE = re.compile(r'^Page loaded:\s+\S+\s+-\s+"(.*)"\s*$')


def log(msg):
    print("[browse] %s" % msg, file=sys.stderr)


def utc_now():
    return datetime.now(timezone.utc)


def make_id(now):
    return "brw_%s_%s" % (now.strftime("%Y%m%d_%H%M%S"), secrets.token_hex(3))


def fmt_wib(now_utc):
    wib = now_utc.astimezone(timezone(timedelta(hours=7)))
    return wib.strftime("%Y-%m-%d %H:%M WIB")


def strip_banner_lines(text):
    """Drop Obscura's banner lines (Fetching... / Page loaded:...)."""
    out = []
    for line in text.splitlines():
        if BANNER_FETCH_RE.match(line) or BANNER_LOADED_RE.match(line):
            continue
        out.append(line)
    return "\n".join(out)


def parse_title_from_banner(text):
    for line in text.splitlines():
        m = BANNER_LOADED_RE.match(line)
        if m:
            return m.group(1)
    return ""


def run_obscura(url, extra_args, timeout=SUBPROCESS_TIMEOUT):
    """Run one `obscura fetch` call. Returns (ok, stdout, stderr)."""
    cmd = [OBSCURA_BIN, "--allow-private-network", "fetch", url] + extra_args
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "", "obscura call timed out after %ss" % timeout
    except OSError as exc:
        return False, "", "cannot run obscura: %s" % exc
    out = proc.stdout or ""
    err = proc.stderr or ""
    # Banner lines and errors go to stderr when streams are captured
    # separately; treat a navigation error as failure even on exit 0.
    failed = proc.returncode != 0 or "Error: Failed to navigate" in (out + err)
    return (not failed), out, err


def make_thumbnail(png_path, thumb_path):
    """Downscale the screenshot for the dashboard. Returns True on success."""
    try:
        from PIL import Image
    except ImportError:
        log("PIL tidak tersedia - thumbnail dilewati")
        return False
    try:
        with Image.open(png_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            w, h = img.size
            if w > THUMB_WIDTH:
                img = img.resize((THUMB_WIDTH, int(h * THUMB_WIDTH / w)))
            img.save(thumb_path, "JPEG", quality=THUMB_QUALITY)
        return True
    except Exception as exc:
        log("thumbnail gagal: %s" % exc)
        return False


def browse_url(url, source, out_dir, browse_id=None):
    now = utc_now()
    browse_id = browse_id or make_id(now)
    os.makedirs(out_dir, exist_ok=True)
    screenshot_path = os.path.join(out_dir, "%s.png" % browse_id)
    thumb_path = os.path.join(out_dir, "%s_thumb.jpg" % browse_id)

    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")

    fetch_ok = False
    fetch_error = ""
    title = ""
    text = ""
    links = []

    ok_html, out_html, err_html = run_obscura(url, [
        "--dump", "html", "--screenshot", screenshot_path,
        "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_html:
        fetch_ok = True
        title = parse_title_from_banner(out_html + "\n" + err_html)
    else:
        fetch_error = (err_html.strip() or
                       "fetch gagal (lihat stderr obscura)").splitlines()[-1:][0]
        log("html fetch failed for %s: %s" % (url, fetch_error))

    ok_text, out_text, _ = run_obscura(url, [
        "--dump", "text", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_text:
        fetch_ok = True
        text = strip_banner_lines(out_text).strip()
        if len(text) > MAX_TEXT_CHARS:
            text = text[:MAX_TEXT_CHARS] + "\n…(dipotong)"

    ok_links, out_links, _ = run_obscura(url, [
        "--dump", "links", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_links:
        fetch_ok = True
        seen = set()
        for line in strip_banner_lines(out_links).splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            href = parts[0].strip()
            link_text = parts[1].strip() if len(parts) > 1 else ""
            if href and href.lower() not in seen:
                seen.add(href.lower())
                links.append({"href": href, "text": link_text})
            if len(links) >= MAX_LINKS:
                break

    if not title and fetch_ok:
        ok_eval, out_eval, _ = run_obscura(url, [
            "--eval", "document.title", "--timeout", str(OBSCURA_TIMEOUT),
        ])
        if ok_eval:
            lines = strip_banner_lines(out_eval).strip().splitlines()
            title = lines[-1].strip() if lines else ""

    screenshot = None
    if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
        screenshot = "%s.png" % browse_id
    elif os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    screenshot_thumb = None
    if screenshot and make_thumbnail(screenshot_path, thumb_path):
        screenshot_thumb = "%s_thumb.jpg" % browse_id

    fetched = utc_now()
    record = {
        "id": browse_id,
        "url": url,
        "domain": host,
        "requested_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "SELESAI" if fetch_ok else "GAGAL",
        "title": title,
        "text": text,
        "links": links,
        "screenshot": screenshot,
        "screenshot_thumb": screenshot_thumb,
        "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fetched_at_wib": fmt_wib(fetched),
        "error": None if fetch_ok else fetch_error,
        "source": source,
    }
    record_path = os.path.join(out_dir, "%s.json" % browse_id)
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "browse.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record, record_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Obscura Guard browse fetch (read-only).")
    parser.add_argument("url", help="URL halaman yang dibuka")
    parser.add_argument("--source", default="dashboard",
                        help="asal permintaan penjelajahan")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                        help="direktori output record")
    parser.add_argument("--id", default=None,
                        help="pakai id record ini (mis. id PENDING dari "
                             "dashboard) agar hasil submit cocok dengan "
                             "antrean; defaultnya id baru dibuat otomatis")
    args = parser.parse_args(argv)

    try:
        record, record_path = browse_url(args.url, args.source, args.out_dir,
                                         browse_id=args.id)
    except Exception as exc:
        log("ERROR: pipeline gagal: %s" % exc)
        return 1

    print(json.dumps(record, indent=2, ensure_ascii=False))
    log("status %s - record %s" % (record["status"], record_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
