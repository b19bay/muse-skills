#!/usr/bin/env python3
"""Obscura Guard - link safety check (read-only, Tier 0).

Usage:
    python3 obscura_linkcheck.py <URL> [--source chat|dashboard|telegram-guard]
                                       [--out-dir DIR]

Pipeline (all read-only, no logins, no signatures, no state changes):
  1. Fetch the URL with the local Obscura headless browser (title, rendered
     HTML, links, assets, screenshot).
  2. Extract EVM addresses / links / forms / "connect wallet" wording.
  3. Domain checks: punycode, lookalike vs curated official list,
     known-mirror list, http-only, IP-literal host.
  4. Contract checks: spam-factory blocklist match + on-chain code via
     BSC RPC eth_getCode (curl).
  5. Verdict AMAN / WASPADA / BLOKIR / GAGAL + risk score + reasons.
  6. Write <out-dir>/<id>.json, append to <out-dir>/checks.jsonl,
     save screenshot as <out-dir>/<id>.png when captured.

Exit 0 even for BLOKIR (the verdict is data). Exit 1 only when no record
could be written at all.

Stdlib only. No secrets. Network calls: Obscura subprocess + BSC RPC only.
"""

import argparse
import ipaddress
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

OBSCURA_BIN = "/home/hatch/workspace/obscura/target/release/obscura"
BLOCKLIST_PATH = "/home/hatch/workspace/tools/crowd-scan/blocklist.json"
DEFAULT_OUT_DIR = "/home/hatch/workspace/obscura-guard/checks"
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"
OBSCURA_TIMEOUT = 120          # seconds, obscura --timeout (navigation)
SUBPROCESS_TIMEOUT = 150       # seconds, hard cap per obscura call
RPC_TIMEOUT = 30               # seconds per curl attempt
RPC_ATTEMPTS = 3               # 1 attempt + 2 retries
MAX_RPC_CHECKS = 20            # bound on eth_getCode calls per check

# Curated official domains. A host that IS one of these (or a subdomain of
# one) is trusted; anything else that borrows the brand is a lookalike.
OFFICIAL_DOMAINS = [
    "binance.com",
    "bnbchain.org",
    "pancakeswap.finance",
    "uniswap.org",
    "bscscan.com",
    "etherscan.io",
    "coingecko.com",
    "coinmarketcap.com",
    "binance.us",
]

# Third-party affiliate mirrors of binance.com (verified 2026-11-04): they
# proxy Binance pages with a sharer referral code and serve sideloaded APKs.
KNOWN_MIRRORS = [
    "bmwweb.biz",
    "bmwweb.me",
    "bmwweb.cloud",
    "bmwweb.academy",
    "bsmkweb.com",
    "marketwebb.io",
]

# Well-known addresses that legitimately have no code; never raise the
# no-code warning for them (they are still listed in contracts[]).
KNOWN_NO_CODE = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}

ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
FORM_RE = re.compile(r"<form[\s>]", re.IGNORECASE)
CONNECT_WALLET_RE = re.compile(r"connect\s+(your\s+)?wallet", re.IGNORECASE)
BANNER_FETCH_RE = re.compile(r"^Fetching\s+\S+")
BANNER_LOADED_RE = re.compile(r'^Page loaded:\s+\S+\s+-\s+"(.*)"\s*$')


def log(msg):
    print(f"[linkcheck] {msg}", file=sys.stderr)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def levenshtein(a, b):
    """Edit distance for short strings (pure python, stdlib only)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def utc_now():
    return datetime.now(timezone.utc)


def make_id(now):
    return "chk_%s_%s" % (now.strftime("%Y%m%d_%H%M%S"), secrets.token_hex(3))


def fmt_wib(now_utc):
    wib = now_utc.astimezone(timezone(timedelta(hours=7)))
    return wib.strftime("%Y-%m-%d %H:%M WIB")


def strip_banner_lines(text):
    """Drop Obscura's stdout banner lines (Fetching... / Page loaded:...)."""
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


# --------------------------------------------------------------------------
# blocklist (READ-ONLY - never written by this script)
# --------------------------------------------------------------------------

def load_blocklist_map(path=BLOCKLIST_PATH):
    """Build {address_lower: {"operator": str, "project": str|None}}.

    Handles every schema variant found in the file:
      - deployer entry address (+ optional distinct `operator` field)
      - projects[]: token / distributor / contract fields
      - contracts[]: flat list of addresses (3 entries use this instead
        of projects)
    First match wins when an address appears under several operators.
    """
    addr_map = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        log(f"WARNING: cannot read blocklist {path}: {exc}")
        return addr_map

    def add(addr, operator, project):
        if not addr or not isinstance(addr, str):
            return
        key = addr.strip().lower()
        if re.fullmatch(r"0x[0-9a-f]{40}", key) and key not in addr_map:
            addr_map[key] = {"operator": operator, "project": project}

    for entry in data.get("deployers", []) or []:
        deployer = entry.get("address", "")
        operator = entry.get("operator") or deployer
        add(deployer, operator, None)
        if entry.get("operator"):
            add(entry["operator"], operator, None)
        for proj in entry.get("projects", []) or []:
            name = proj.get("name")
            for field in ("token", "distributor", "contract"):
                add(proj.get(field), operator, name)
        for contract in entry.get("contracts", []) or []:
            add(contract, operator, None)
    return addr_map


def match_blocklist(address, addr_map):
    """Return (operator, project) for an address, or (None, None)."""
    hit = addr_map.get(address.strip().lower())
    if hit:
        return hit["operator"], hit["project"]
    return None, None


# --------------------------------------------------------------------------
# obscura
# --------------------------------------------------------------------------

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
    # Treat a navigation error as failure even if the exit code is 0.
    # NOTE: Obscura's banner lines ("Fetching ...", "Page loaded: ...")
    # and its error messages go to STDERR when the streams are captured
    # separately (they only looked like stdout under `2>&1` merging).
    failed = proc.returncode != 0 or "Error: Failed to navigate" in (out + err)
    return (not failed), out, err


# --------------------------------------------------------------------------
# BSC RPC (eth_getCode via curl)
# --------------------------------------------------------------------------

def eth_get_code(address, rpc_url=BSC_RPC_URL):
    """True if the address has code on BSC, False if not, None if unknown.

    Uses curl (proxy env inherited). 1 attempt + 2 retries.
    """
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getCode",
        "params": [address, "latest"],
    })
    last_err = ""
    for attempt in range(RPC_ATTEMPTS):
        try:
            proc = subprocess.run(
                ["curl", "-sS", "--max-time", str(RPC_TIMEOUT),
                 "-X", "POST", "-H", "Content-Type: application/json",
                 "-d", payload, rpc_url],
                capture_output=True, text=True, timeout=RPC_TIMEOUT + 10,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            last_err = str(exc)
        else:
            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    resp = json.loads(proc.stdout)
                except ValueError:
                    last_err = "RPC returned non-JSON"
                else:
                    result = resp.get("result")
                    if isinstance(result, str) and result.startswith("0x"):
                        return len(result) > 2
                    last_err = "RPC error: %s" % (resp.get("error") or "no result")
            else:
                last_err = (proc.stderr or "").strip() or "empty RPC response"
        if attempt < RPC_ATTEMPTS - 1:
            time.sleep(2)
    log(f"eth_getCode failed for {address}: {last_err}")
    return None


# --------------------------------------------------------------------------
# domain checks
# --------------------------------------------------------------------------

def domain_checks(host, scheme):
    """Return (flags, reasons) for the URL host."""
    flags = []
    reasons = []
    if not host:
        return flags, reasons

    if "xn--" in host:
        flags.append("punycode")
        reasons.append({
            "code": "punycode",
            "severity": "medium",
            "detail": "Host %s memakai punycode (xn--) - ciri umum domain "
                      "homoglyph/tiruan." % host,
        })

    for mirror in KNOWN_MIRRORS:
        if host == mirror or host.endswith("." + mirror):
            flags.append("known_mirror")
            reasons.append({
                "code": "known_mirror",
                "severity": "critical",
                "detail": "Domain %s ada di daftar mirror terverifikasi "
                          "(mirror afiliasi pihak ketiga, bukan domain "
                          "resmi)." % host,
            })
            break

    trusted = any(
        host == off or host.endswith("." + off) for off in OFFICIAL_DOMAINS
    )
    if not trusted:
        for off in OFFICIAL_DOMAINS:
            brand = off.split(".")[0]
            lookalike = None
            if brand in host:
                lookalike = ("memakai merek '%s' padahal bukan domain resmi "
                             "%s" % (brand, off))
            elif levenshtein(host, off) <= 2:
                lookalike = ("jarak edit %d dari domain resmi %s"
                             % (levenshtein(host, off), off))
            if lookalike:
                flags.append("lookalike")
                reasons.append({
                    "code": "lookalike_domain",
                    "severity": "high",
                    "detail": "Host %s %s." % (host, lookalike),
                })
                break

    if scheme == "http":
        flags.append("http_only")
        reasons.append({
            "code": "http_only",
            "severity": "medium",
            "detail": "URL memakai http tanpa TLS - lalu lintas tidak "
                      "terenkripsi dan mudah dipalsukan.",
        })

    try:
        ipaddress.ip_address(host)
        flags.append("ip_host")
        reasons.append({
            "code": "ip_host",
            "severity": "medium",
            "detail": "Host %s adalah alamat IP mentah, bukan nama domain."
                      % host,
        })
    except ValueError:
        pass

    return flags, reasons


# --------------------------------------------------------------------------
# main pipeline
# --------------------------------------------------------------------------

def check_url(url, source, out_dir, check_id=None):
    now = utc_now()
    check_id = check_id or make_id(now)
    os.makedirs(out_dir, exist_ok=True)
    screenshot_path = os.path.join(out_dir, "%s.png" % check_id)

    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    scheme = (parsed.scheme or "").lower()

    reasons = []
    notes = []
    fetch_ok = False
    fetch_error = ""
    title = ""
    html = ""
    links = []
    assets = []

    # --- 1. obscura fetches (each resilient; one failure must not kill
    # --- the check - domain findings are independent of the fetch).
    ok_html, out_html, err_html = run_obscura(url, [
        "--dump", "html", "--screenshot", screenshot_path,
        "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_html:
        fetch_ok = True
        # Banner lives on stderr; parse the combined output.
        title = parse_title_from_banner(out_html + "\n" + err_html)
        html = strip_banner_lines(out_html)
    else:
        fetch_error = (err_html.strip() or
                       "fetch gagal (lihat stderr obscura)").splitlines()[-1:][0]
        log(f"html fetch failed for {url}: {fetch_error}")

    ok_links, out_links, _ = run_obscura(url, [
        "--dump", "links", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_links:
        fetch_ok = True
        for line in strip_banner_lines(out_links).splitlines():
            line = line.strip()
            if line:
                links.append(line.split("\t")[0].strip())
    links = sorted(set(links))

    ok_assets, out_assets, _ = run_obscura(url, [
        "--dump", "assets", "--timeout", str(OBSCURA_TIMEOUT),
    ])
    if ok_assets:
        fetch_ok = True
        for line in strip_banner_lines(out_assets).splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("url"):
                    assets.append(rec["url"])
    assets = sorted(set(assets))

    if not title and fetch_ok:
        ok_eval, out_eval, _ = run_obscura(url, [
            "--eval", "document.title", "--timeout", str(OBSCURA_TIMEOUT),
        ])
        if ok_eval:
            title = strip_banner_lines(out_eval).strip().splitlines()
            title = title[-1].strip() if title else ""

    screenshot = None
    if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
        screenshot = "%s.png" % check_id
    elif os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    # --- 2. extraction from rendered content.
    searchable = html + "\n" + "\n".join(links)
    addresses = []
    seen = set()
    for m in ADDR_RE.finditer(searchable):
        addr = m.group(0)
        if addr.lower() not in seen:
            seen.add(addr.lower())
            addresses.append(addr)
    has_forms = bool(FORM_RE.search(html))
    has_connect_wallet = bool(CONNECT_WALLET_RE.search(html))
    if has_connect_wallet:
        reasons.append({
            "code": "connect_wallet",
            "severity": "info",
            "detail": "Halaman memuat ajakan 'connect wallet' - wajar untuk "
                      "dApp, tapi selalu periksa kontraknya sebelum "
                      "menghubungkan wallet.",
        })
    if has_forms:
        notes.append("halaman memuat <form>")
    if has_connect_wallet:
        notes.append("halaman memuat ajakan 'connect wallet'")

    # --- 3. domain checks.
    domain_flags, domain_reasons = domain_checks(host, scheme)
    reasons.extend(domain_reasons)

    # --- 4. contract checks.
    addr_map = load_blocklist_map()
    if not addr_map:
        reasons.append({
            "code": "blocklist_unavailable",
            "severity": "low",
            "detail": "Daftar blocklist tidak bisa dibaca - pencocokan "
                      "kontrak dilewati untuk pemeriksaan ini.",
        })
    contracts = []
    rpc_failed = False
    no_code_count = 0
    for i, addr in enumerate(addresses):
        operator, project = match_blocklist(addr, addr_map)
        blocklisted = operator is not None
        has_code = None
        if i < MAX_RPC_CHECKS:
            has_code = eth_get_code(addr)
            if has_code is None:
                rpc_failed = True
        elif i == MAX_RPC_CHECKS:
            notes.append("cek eth_getCode dibatasi %d alamat pertama"
                         % MAX_RPC_CHECKS)
        contracts.append({
            "address": addr,
            "chain": "BSC",
            "has_code": has_code,
            "blocklisted": blocklisted,
            "blocklist_operator": operator,
            "blocklist_project": project,
        })
        if blocklisted:
            reasons.append({
                "code": "blocklisted_contract",
                "severity": "critical",
                "detail": "Alamat %s masuk blocklist pabrik spam "
                          "(operator %s%s)." % (
                              addr, operator,
                              ", proyek %s" % project if project else ""),
            })
        elif has_code is False and addr.lower() not in KNOWN_NO_CODE:
            no_code_count += 1
            reasons.append({
                "code": "contract_no_code",
                "severity": "medium",
                "detail": "Alamat %s tidak punya code on-chain BSC "
                          "(EOA atau kontrak belum deploy) - bukan bukti "
                          "penipuan, tapi patut dicurigai bila diklaim "
                          "sebagai kontrak." % addr,
            })
    if rpc_failed:
        reasons.append({
            "code": "rpc_unavailable",
            "severity": "low",
            "detail": "Sebagian cek eth_getCode gagal (RPC BSC tidak "
                      "menjawab) - has_code=null untuk alamat tersebut.",
        })
        notes.append("sebagian cek eth_getCode gagal (RPC tidak menjawab)")

    if not fetch_ok:
        notes.append("fetch gagal: %s" % fetch_error)
        reasons.append({
            "code": "fetch_failed",
            "severity": "medium",
            "detail": "Obscura tidak bisa memuat halaman (%s) - temuan "
                      "domain/kontrak di atas tetap berlaku." % fetch_error,
        })

    # --- 5. verdict + score.
    is_mirror = "known_mirror" in domain_flags
    any_blocklisted = any(c["blocklisted"] for c in contracts)
    warn_flags = {"punycode", "lookalike", "http_only", "ip_host"}
    has_warn_domain = bool(warn_flags & set(domain_flags))
    has_no_code = no_code_count > 0

    score = 0
    if is_mirror:
        score += 80
    if any_blocklisted:
        score += 80
    if "punycode" in domain_flags:
        score += 35
    if "lookalike" in domain_flags:
        score += 40
    if "http_only" in domain_flags:
        score += 15
    if "ip_host" in domain_flags:
        score += 20
    score += min(40, 25 * no_code_count)

    # Precedence: a named BLOKIR match (mirror / blocklisted contract) is a
    # fact about the domain/address and stands even if the fetch failed.
    if is_mirror or any_blocklisted:
        verdict = "BLOKIR"
        score = max(61, min(100, score))
    elif has_warn_domain or has_no_code:
        verdict = "WASPADA"
        score = max(21, min(60, score))
    elif fetch_ok:
        verdict = "AMAN"
        score = min(20, score)
        reasons.append({
            "code": "checks_passed",
            "severity": "info",
            "detail": "Tidak ada temuan: domain bukan mirror/tiruan, tidak "
                      "ada kontrak ter-blocklist.",
        })
    else:
        verdict = "GAGAL"
        score = None

    record = {
        "id": check_id,
        "url": url,
        "domain": host,
        "checked_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checked_at_wib": fmt_wib(now),
        "verdict": verdict,
        "score": score,
        "reasons": reasons,
        "title": title,
        "contracts": contracts,
        "domain_flags": domain_flags,
        "links_count": len(links),
        "assets_count": len(assets),
        "screenshot": screenshot,
        "source": source,
        "notes": "; ".join(notes),
    }

    # --- 6. persist.
    record_path = os.path.join(out_dir, "%s.json" % check_id)
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "checks.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record, record_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Obscura Guard link safety check (read-only).")
    parser.add_argument("url", help="URL yang diperiksa")
    parser.add_argument("--source", default="chat",
                        choices=["chat", "dashboard", "telegram-guard"],
                        help="asal permintaan pemeriksaan")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                        help="direktori output record")
    parser.add_argument("--id", default=None,
                        help="pakai id record ini (mis. id PENDING dari "
                             "dashboard) agar hasil submit cocok dengan "
                             "antrean; defaultnya id baru dibuat otomatis")
    args = parser.parse_args(argv)

    try:
        record, record_path = check_url(args.url, args.source, args.out_dir,
                                        check_id=args.id)
    except Exception as exc:  # last resort: still try to write a GAGAL record
        log(f"ERROR: pipeline gagal: {exc}")
        try:
            now = utc_now()
            check_id = args.id or make_id(now)
            os.makedirs(args.out_dir, exist_ok=True)
            host = (urlparse(args.url).hostname or "").lower()
            record = {
                "id": check_id,
                "url": args.url,
                "domain": host,
                "checked_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "checked_at_wib": fmt_wib(now),
                "verdict": "GAGAL",
                "score": None,
                "reasons": [{"code": "pipeline_error", "severity": "medium",
                             "detail": "Pipeline pemeriksaan gagal: %s" % exc}],
                "title": "",
                "contracts": [],
                "domain_flags": [],
                "links_count": 0,
                "assets_count": 0,
                "screenshot": None,
                "source": args.source,
                "notes": "pipeline gagal: %s" % exc,
            }
            record_path = os.path.join(args.out_dir, "%s.json" % check_id)
            with open(record_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
            with open(os.path.join(args.out_dir, "checks.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as exc2:
            log(f"ERROR: tidak bisa menulis record GAGAL: {exc2}")
            return 1

    print(json.dumps(record, indent=2, ensure_ascii=False))
    log("verdict %s - record %s" % (record["verdict"], record_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
