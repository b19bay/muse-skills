# Provenance — token-integration-analyzer

- **Upstream:** Trail of Bits — https://github.com/trailofbits/skills
- **Path in repo:** `plugins/building-secure-contracts/skills/token-integration-analyzer/`
- **Commit installed:** `149d7b21f4067765b82e67029730b42d228ef4b4` (commit 2026-11-12)
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry; repo 8.1k stars)
- **License:** CC BY-SA 4.0 (Attribution-ShareAlike 4.0 International) — the
  full license text was fetched from the repo root and included here as
  `LICENSE`. Any adaptation must keep attribution and share-alike.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/token-integration-analyzer/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist). Folder name
  drops the `trailofbits-` staging prefix; origin is recorded here and in
  `skill.yaml`.

## Security audit verdict: CLEAN (2026-11-14)

Entire SKILL.md (362 lines) + all supporting files read in full:
`resources/ASSESSMENT_CATEGORIES.md` (571 lines), `resources/
REPORT_TEMPLATES.md` (141 lines), `agents/openai.yaml`,
`assets/trail-of-bits-mark.svg`. This skill contains no scripts.

- Pure Markdown instructions + checklists + report templates; no network
  commands, no executed code, no credentials, no URLs other than general
  documentation references.
- The only shell commands are examples of local analysis tools
  (`slither-check-erc`, `slither --print human-summary/contract-summary`,
  `slither-prop`) — all local, no network arguments. On-chain query
  examples use placeholders (`RPC_URL`, `token.methods...call()`) and state
  explicitly "only if the user provides a contract address + RPC endpoint;
  do not hallucinate".
- The SVG logo contains no `<script>` / event handlers / `href`;
  `openai.yaml` is display metadata only.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md noting the relationship to the
  local skills: this is the *integrator* lens (how a protocol handles
  non-standard tokens) vs `forensik-kontrak` / `bsc-contract-audit` /
  `multichain-contract-audit` as the *due-diligence* lens; use together.
- Added `LICENSE` (CC BY-SA 4.0 full text, fetched from the repo root —
  staging did not include it).
- All checklists, the 24-pattern weird-ERC20 database, and templates are
  upstream-verbatim.
