#!/usr/bin/env python3
"""Score one X project against the riset-x filters.

Input: one JSON object on stdin or as argv[1], with boolean-ish fields:
  active, ramai_mint, has_price, not_spam, free
  plus optional bonuses: kol_named (named KOL follow/repost/interaction
  WITH a link), market_saat_mint (while mint is still running, a
  floor >0 OR an active offer already exists for the same contract,
  with a snapshot time - floor is a seller listing, offer is a buyer
  bid; either one counts for this single +1 point, not +1 each), and
  situs_web_terverifikasi (official site linked from the project's X
  profile, readable content, checkable docs such as llms.txt, and a
  site contract matching the on-chain contract - all must pass).
  ramai_mint = crowded during the mint window: distinct accounts
  posting/minting, supply moving, real market activity - NOT account
  size, NOT follower count. has_price = floor>0 with listings/sales
  PLUS a live buy/sell marketplace, real trading volume with its
  stated window, and recent trading activity - price alone is NOT
  enough; a good NFT must have market, volume, and activity.
  not_spam = no spam signal found.
Output: JSON with per-filter pass/fail, base score, bonuses, and verdict.
A project passes (LOLOS) only if ALL five base filters pass.
Bonuses add ranking only and CANNOT rescue a project that failed a
base filter: 4/5 + bonuses is still DITOLAK.
"""
import json
import sys

FILTERS = ["active", "ramai_mint", "has_price", "not_spam", "free"]


def score(data):
    results = {f: bool(data.get(f)) for f in FILTERS}
    passed = sum(results.values())
    kol_bonus = 1 if data.get("kol_named") else 0
    market_bonus = 1 if data.get("market_saat_mint") else 0
    situs_bonus = 1 if data.get("situs_web_terverifikasi") else 0
    bonus = kol_bonus + market_bonus + situs_bonus
    display = f"{passed}/{len(FILTERS)}"
    if kol_bonus:
        display += " +1 bonus KOL"
    if market_bonus:
        display += " +1 bonus market saat mint"
    if situs_bonus:
        display += " +1 bonus situs web"
    return {
        "filters": results,
        "score": f"{passed}/{len(FILTERS)}",
        "kol_bonus": kol_bonus,
        "market_saat_mint_bonus": market_bonus,
        "situs_web_bonus": situs_bonus,
        "score_display": display,
        "total_including_bonus": passed + bonus,
        "verdict": "LOLOS" if passed == len(FILTERS) else "DITOLAK",
        "failed": [f for f, ok in results.items() if not ok],
    }


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(score(json.loads(raw)), indent=2))
