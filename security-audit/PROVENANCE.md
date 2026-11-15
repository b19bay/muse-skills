# Provenance — security-audit

- **Upstream:** Cloudflare, Inc. — https://github.com/cloudflare/security-audit-skill
- **Path in repo:** `skills/security-audit/`
- **SKILL.md URL:** https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md
- **Commit installed:** `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry; repo ~25,600 stars, ranked #1 in Security)
- **License:** MIT — `LICENSE` copied from upstream and included in this folder.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/security-audit/` at the user's order ("pasang semua", 8-skill Hermes shortlist).

## Security audit verdict: CLEAN (2026-11-14)

SKILL.md + HUNTING.md read in full; all files grepped. Defensive, source-first
workflow; target execution only inside an OS sandbox (no external network,
allowlisted empty env, read-only target); explicit bans on probing live
endpoints, real credentials, and production data. The `.cjs` validators use
only `node:fs/path/util`, read files read-only (`O_RDONLY|O_NOFOLLOW|
O_NONBLOCK`), no network, no exec, no env reads; the only `spawnSync` is in
the `.test.cjs` harness files (running the validators themselves). No prompt
injection phrases, no external URLs, no `curl|sh` / exfiltration in any `.md`
file. No script was executed during audit or install.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md mapping the skill's agent-neutral
  platform terms: Parent = coordinating (parent) agent; Task tool / delegation
  = `subagent.spawn`; `research` / `general` agents = Muse subagents with the
  same role boundaries. Write-isolation and independence boundaries preserved.
- No other content changed. Validators (`validate-findings.cjs`,
  `validate-coverage-ledger.cjs` + tests), `report-schema.json`, and all 14
  domain reference files are upstream-verbatim.
