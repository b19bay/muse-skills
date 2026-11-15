#!/usr/bin/env python3
"""Obscura Guard - Tier-0 web recon (read-only).

Usage:
    python3 obscura_recon.py <URL> [--out-dir DIR]

Fetches one public URL with the local Obscura headless browser and writes
a surface report: rendered title, links, sub-resource assets, external
hosts, script-bundle URLs, form count, and emails found in the text.

Tier 0 ONLY: public pages, no payloads, no logins, no form submissions,
no state changes. Anything beyond passive observation needs the
pentest-web 3-tier gate (see skill bug-hunter / pentest-web).

Output: <out-dir>/<domain>_<YYYYMMDD_HHMMSS>.json (stdout prints the path
plus a short summary). Exit 0 on success, 1 if no report could be written.

Stdlib only. No secrets. The only network call is the Obscura subprocess.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

OBSCURA_BIN = "/home/hatch/workspace/obscura/target/release/obscura"
DEFAULT_OUT_DIR = "/home/hatch/workspace/obscura-guard/recon"
OBSCURA_TIMEOUT = 120
SUBPROCESS_TIMEOUT = 150
MAX_ITEMS = 500

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
BANNER_FETCH_RE = re.compile(r"^Fetching\s+\S+")
BANNER_LOADED_RE = re.compile(r'^Page loaded:\s+\S+\s+-\s+"(.*)"\s*$')

# One eval returning everything as JSON (single extra page load instead of
# three): form count, distinct external hostnames referenced by the page,
# and script-bundle URLs. Wrapped in an IIFE: a bare multi-statement eval
# starting with const/let returns null in V8.
EVAL_JS = (
    "(function(){"
    "var hosts={};"
    "document.querySelectorAll('a[href],script[src],link[href],img[src],"
    "iframe[src],source[src]').forEach(function(e){"
    "try{var u=new URL(e.href||e.src);"
    "if(u.hostname!==location.hostname){hosts[u.hostname]=1;}}catch(_){}});"
    "var scripts=Array.from(document.scripts)"
    ".map(function(s){return s.src;}).filter(Boolean);"
    "return JSON.stringify({forms:document.forms.length,"
    "hosts:Object.keys(hosts),scripts:scripts});"
    "})()"
)


def log(msg):
    print(f"[recon] {msg}", file=sys.stderr)


def strip_banner_lines(text):
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
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, "", f"obscura call timed out after {timeout}s"
    except OSError as exc:
        return False, "", f"cannot run obscura: {exc}"
    out = proc.stdout or ""
    err = proc.stderr or ""
    # NOTE: Obscura's banner lines ("Fetching ...", "Page loaded: ...")
    # and its error messages go to STDERR when the streams are captured
    # separately (they only looked like stdout under `2>&1` merging).
    failed = proc.returncode != 0 or "Error: Failed to navigate" in (out + err)
    return (not failed), out, err


def host_of(raw_url):
    try:
        return (urlparse(raw_url).hostname or "").lower()
    except ValueError:
        return ""


def recon_url(url, out_dir):
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower().rstrip(".")
    now = datetime.now(timezone.utc)
    os.makedirs(out_dir, exist_ok=True)

    notes = []
    title = ""
    html = ""
    text = ""
    links = []
    assets = []
    forms_count = None
    eval_hosts = []
    eval_scripts = []
    any_ok = False

    ok, out, err = run_obscura(url, [
        "--dump", "html", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok:
        any_ok = True
        # Banner lives on stderr; parse the combined output.
        title = parse_title_from_banner(out + "\n" + err)
        html = strip_banner_lines(out)
    else:
        notes.append("dump html gagal: %s" % (err.strip() or "unknown"))

    ok, out, err = run_obscura(url, [
        "--dump", "links", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok:
        any_ok = True
        for line in strip_banner_lines(out).splitlines():
            line = line.strip()
            if line:
                links.append(line.split("\t")[0].strip())
    else:
        notes.append("dump links gagal: %s" % (err.strip() or "unknown"))

    ok, out, err = run_obscura(url, [
        "--dump", "assets", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok:
        any_ok = True
        for line in strip_banner_lines(out).splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("url"):
                    assets.append(rec["url"])
    else:
        notes.append("dump assets gagal: %s" % (err.strip() or "unknown"))

    ok, out, err = run_obscura(url, [
        "--dump", "text", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok:
        any_ok = True
        text = strip_banner_lines(out)
    else:
        notes.append("dump text gagal: %s" % (err.strip() or "unknown"))

    ok, out, err = run_obscura(url, [
        "--eval", EVAL_JS, "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok:
        any_ok = True
        body = strip_banner_lines(out).strip()
        try:
            data = json.loads(body)
            forms_count = data.get("forms")
            eval_hosts = data.get("hosts") or []
            eval_scripts = data.get("scripts") or []
        except ValueError:
            notes.append("eval JS tidak mengembalikan JSON yang valid")
    else:
        notes.append("eval JS gagal: %s" % (err.strip() or "unknown"))

    if not any_ok:
        raise RuntimeError("semua panggilan obscura gagal untuk %s" % url)

    links = sorted(set(links))[:MAX_ITEMS]
    assets = sorted(set(assets))[:MAX_ITEMS]

    # External hosts: union of the JS-observed hosts and the hosts found in
    # the dumped links/assets, minus the page's own domain.
    external = set(h for h in eval_hosts if h and h != domain)
    for raw in links + assets:
        h = host_of(raw)
        if h and h != domain and not h.endswith("." + domain):
            external.add(h)
    external_hosts = sorted(external)

    scripts = sorted(set(eval_scripts))[:MAX_ITEMS]
    if forms_count is None:
        forms_count = len(re.findall(r"<form[\s>]", html, re.IGNORECASE))
        notes.append("forms_count dari regex HTML (eval gagal)")

    emails = sorted(set(EMAIL_RE.findall(text + "\n" + html)))[:50]

    safe_domain = re.sub(r"[^A-Za-z0-9.\-]+", "_", domain) or "unknown"
    fname = "%s_%s.json" % (safe_domain, now.strftime("%Y%m%d_%H%M%S"))
    report = {
        "url": url,
        "domain": domain,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": title,
        "links": links,
        "assets": assets,
        "external_hosts": external_hosts,
        "scripts": scripts,
        "forms_count": forms_count,
        "emails": emails,
        "notes": "; ".join(notes),
    }
    report_path = os.path.join(out_dir, fname)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return report, report_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Obscura Guard Tier-0 web recon (read-only).")
    parser.add_argument("url", help="URL publik yang di-recon")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                        help="direktori output laporan")
    args = parser.parse_args(argv)

    try:
        report, report_path = recon_url(args.url, args.out_dir)
    except Exception as exc:
        log(f"ERROR: {exc}")
        return 1

    print("report: %s" % report_path)
    print("title: %s" % (report["title"] or "(kosong)"))
    print("links: %d | assets: %d | external_hosts: %d | scripts: %d | "
          "forms: %s | emails: %d" % (
              len(report["links"]), len(report["assets"]),
              len(report["external_hosts"]), len(report["scripts"]),
              report["forms_count"], len(report["emails"])))
    if report["external_hosts"]:
        print("external_hosts: %s" % ", ".join(report["external_hosts"]))
    if report["notes"]:
        log("notes: %s" % report["notes"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
