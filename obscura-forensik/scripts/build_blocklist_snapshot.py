#!/usr/bin/env python3
"""Build the normalized blocklist snapshot for the Obscura Dashboard.

Reads the source blocklist (READ-ONLY, never modified) and writes the
dashboard-shaped snapshot:
  {"operators": [{"address", "blocked_at",
                  "projects": [{"name", "token", "distributor"}]}],
   "total_addresses": int, "updated_at": ISO-8601 UTC}

Source:  /home/hatch/workspace/tools/crowd-scan/blocklist.json
Output:  /home/hatch/workspace/obscura-guard/blocklist_snapshot.json

The source has several schema variants and this builder handles all of them:
  - "projects" lists (project "name" may be null; the project address may
    sit in "token" or in "contract"; "distributor" may be absent).
  - Flat "contracts" lists (plain address strings). Two entries have ONLY
    a contracts list and no "projects" key at all; one entry has both.
  - A distinct "operator" field on some entries (usually equal to the
    deployer address, sometimes different).

Normalization rules:
  - Null project names become "(nama tidak tercatat)" (the dashboard's
    syncblocklist action requires every name to be a string).
  - Flat contracts become projects with the placeholder name and the
    contract address as "token".
  - Projects are deduplicated per operator by lowercase token address,
    so a flat contract that duplicates a project token is listed once.
  - total_addresses counts unique lowercase addresses across deployer
    address, operator field, project token/contract/distributor, and
    flat contracts.

Usage: python3 build_blocklist_snapshot.py
Exit 0 on success; prints a summary line.
"""

import json
import re
from datetime import datetime, timezone

SRC = "/home/hatch/workspace/tools/crowd-scan/blocklist.json"
DST = "/home/hatch/workspace/obscura-guard/blocklist_snapshot.json"
PLACEHOLDER = "(nama tidak tercatat)"
ADDR_RE = re.compile(r"0x[0-9a-f]{40}")


def _valid(addr):
    """True only for well-formed EVM addresses (0x + 40 hex).

    The source contains 2 malformed 39-char entries; they stay in the
    records as-is but are excluded from total_addresses.
    """
    return isinstance(addr, str) and bool(ADDR_RE.fullmatch(addr.strip().lower()))


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    operators = []
    all_addresses = set()
    null_names = 0

    for dep in data.get("deployers", []) or []:
        address = dep.get("address")
        if _valid(address):
            all_addresses.add(address.lower())
        operator = dep.get("operator")
        if _valid(operator):
            all_addresses.add(operator.lower())

        projects = []
        seen_tokens = set()

        def add_project(name, token, distributor):
            nonlocal null_names
            if name is None:
                name = PLACEHOLDER
                null_names += 1
            if token:
                key = token.lower()
                if key in seen_tokens:
                    return
                seen_tokens.add(key)
                if _valid(key):
                    all_addresses.add(key)
            if distributor and _valid(distributor):
                all_addresses.add(distributor.lower())
            projects.append(
                {"name": name, "token": token, "distributor": distributor}
            )

        for p in dep.get("projects", []) or []:
            token = p.get("token") or p.get("contract")
            add_project(p.get("name"), token, p.get("distributor"))

        for c in dep.get("contracts", []) or []:
            # Flat address strings; may duplicate a project token.
            if isinstance(c, str):
                add_project(None, c, None)
            elif isinstance(c, dict):
                add_project(
                    c.get("name"), c.get("token") or c.get("contract"),
                    c.get("distributor"),
                )

        operators.append(
            {
                "address": address,
                "blocked_at": dep.get("blocked_at") or "",
                "projects": projects,
            }
        )

    snapshot = {
        "operators": operators,
        "total_addresses": len(all_addresses),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(DST, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)

    n_projects = sum(len(o["projects"]) for o in operators)
    print(
        f"wrote {DST}: {len(operators)} operators, {n_projects} projects, "
        f"{len(all_addresses)} unique addresses, "
        f"{null_names} null names normalized"
    )


if __name__ == "__main__":
    main()
