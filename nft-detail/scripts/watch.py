#!/usr/bin/env python3
"""Watcher for the nft-detail skill: poll a check command, diff, log.

The check command is supplied by the caller and must print one JSON
object on stdout, e.g.:
  {"floor": 0.001, "currency": "BNB", "listed": 71,
   "token_listed": false, "offers": []}
This script does NOT fetch a marketplace itself and does NOT invent
data. A failed or empty check is logged as ERROR and is NOT treated
as a change and does NOT stop the watcher.

Usage:
  watch.py --check-cmd "my-check.sh" --state state.json --log watch.log
           [--interval 60] [--max-runs 0]  # 0 = run until interrupted
  watch.py --once --check-cmd "my-check.sh" --state state.json --log watch.log
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone


def log_line(log_path, msg):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} {msg}"
    print(line, flush=True)
    if log_path:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def run_check(cmd):
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    text = out.stdout.strip()
    if out.returncode != 0 or not text:
        return None, f"check failed rc={out.returncode} stderr={out.stderr.strip()[:200]}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, f"check output is not JSON: {e}"


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_state(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".watch-state-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def diff(old, new):
    changes = []
    if old is None:
        return ["first snapshot"]
    for key in sorted(set(old) | set(new)):
        if old.get(key) != new.get(key):
            changes.append(f"{key}: {old.get(key)!r} -> {new.get(key)!r}")
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-cmd", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--log", default="")
    ap.add_argument("--interval", type=float, default=60)
    ap.add_argument("--max-runs", type=int, default=0)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    runs = 0
    while True:
        runs += 1
        data, err = run_check(args.check_cmd)
        if err:
            log_line(args.log, f"ERROR {err}")
        else:
            old = load_state(args.state)
            changes = diff(old, data)
            if changes:
                log_line(args.log, "CHANGED " + "; ".join(changes))
            else:
                log_line(args.log, "NO_CHANGE")
            save_state(args.state, data)
        if args.once or (args.max_runs and runs >= args.max_runs):
            break
        time.sleep(max(args.interval, 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
