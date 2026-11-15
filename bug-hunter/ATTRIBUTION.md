# Attribution

This skill adapts content from **Agentic-Bug-Hunter** by AwareXone
(https://github.com/awarexone/Agentic-Bug-Hunter), cloned 2026-11-13,
version 6.0.1, released under the **MIT License**
(Copyright (c) 2026 Claude Bug Bounty Hunter Contributors).
The full license text is in `LICENSE` in this folder.

## What was adapted

- Root `SKILL.md` (bug-bounty master workflow) — rewritten as this skill's
  `SKILL.md` for Muse (Claude Code /slash-command references removed,
  Muse tooling + the workspace's pentest-web 3-tier authorization gate added).
- 12 sub-skills copied as `references/*.md`: web2-recon, web2-vuln-classes,
  bug-chaining, triage-validation, report-writing, bb-methodology, web3-audit,
  graphql-audit, llm-redteam, mcp-server-audit, security-arsenal (+ its
  cheatsheet and references), bugcrowd-reporting.
- 8 web3 docs copied as `references/web3/*.md`.
- 16 command playbooks copied as `references/commands/*.md`.
- The `bughunter` Python package copied as `scripts/bughunter/` (used only
  for its standalone tools: verifiers, scope checker, port scanner, SAST scan,
  token scanner).

## What was NOT ported

- The autopilot / agent mode (`bughunter hunt`, `/autopilot`, the AI-provider
  CLI) — Muse drives every step; nothing sends requests autonomously.
- 13 sub-skills not curated (mobile-pentest, cloud-pentest, cicd-security,
  agentic-app-audit, argus, client-reverse, credential-attack, johnwick,
  jsmax, omni-killchain, pii-hunter, bug-bounty [root, adapted as SKILL.md],
  meme-coin-audit) — available in the upstream repo if needed later.
- 24 command playbooks not curated — same, available upstream.

## Local additions (not upstream)

- The pentest-web 3-tier authorization gate (Tier 0/1/2 + hard bans).
- The forensik 4-layer proof standard for contract findings.
- Tooling notes specific to this VM (Go binary paths, no nmap/semgrep,
  proxy-only egress, Secure Vault for API keys).
- The sibling-skill map (pentest-web, forensik_kontrak, forensik_node,
  multichain-contract-audit).
