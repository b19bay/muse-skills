# muse-skills

A collection of 39 agent skills built for security research, forensic
auditing, bug-bounty hunting, and autonomous agent work — written in
Indonesian and English, used daily by a working security researcher.

Each directory is one skill: a `SKILL.md` playbook plus its references,
scripts, and checklists. Drop a directory into your agent's skills folder
and follow its `SKILL.md`.

## Skills

| Skill | What it does |
|---|---|
| `audit-pasar-agen` | Audit agent marketplaces: trust flows author → victim, not just client → server |
| `binance-square-post` | Publish text/image/video posts to Binance Square via the official Square OpenAPI (official Binance skill, verbatim + local vault-auth amendment) |
| `bounded_solver_retry` | Gate time-boxed solver attempts on a measured fit with the live window |
| `bsc-contract-audit` | BSC contract & NFT mint audit: 4 gates, /100 rubric, GO/CAUTION/BLOCK |
| `bug-hunter` | Bug Hunter — recon to report (from awarexone/Agentic-Bug-Hunter, adapted) |
| `contested_seat_watcher` | Unattended watcher that captures a scarce seat inside its window |
| `forecasting` | Win forecasting bounties: champion method, replica scorer, variant sweep |
| `forensik-kontrak` | Forensik Kontrak v2 — hunt from patterns, not function lists |
| `forensik-node` | Forensik Node — hunt from duplicate maps & cross-subsystem imbalance |
| `hunt-llm-ai` | Hunt LLM & agentic AI vulnerabilities (prompt injection, tool-use abuse, RCE) |
| `humanize-skills` | Rewrite, edit, or draft text so it reads as specifically human-written (CC-BY-4.0, Adem Kurtipek; 10 modes, 20 languages) |
| `judging-calibration` | Calibrate judge-scored entries: study top 10, build variants, keep the best |
| `launch-curve-audit` | Launch Curve Audit |
| `makefun-bounty` | Build a make.fun bounty entry from kit to submission-ready bundle |
| `makefun_recorder_choreography` | Record make.fun builds correctly: recorder first, author after, one seal at a time |
| `multi_account_post_dedup` | Stop the same topic being posted twice across accounts you own |
| `multichain-contract-audit` | Multichain contract & NFT mint audit (EVM + Solana annex) |
| `nft-detail` | Complete NFT detail: metadata, marketplaces, floor, volume, offers |
| `obscura-forensik` | Obscura Forensik — a browser eye for forensic skills |
| `onchain-price-accuracy` | On-chain price accuracy: never trust a quoted price without verification |
| `pentest-web` | Pentest Web — pattern-anchored hunting with a 3-tier authorization gate |
| `perf-profiling` | Win agent-server bounties on performance: attribute the gap, profile, fix |
| `perkataan-mutlak` | Working doctrine: the user's word is the highest rule; evidence over inference |
| `property-based-testing` | Property-based tests — Hypothesis, fast-check, proptest, Echidna/Medusa |
| `recon-a-domain-passively` | End-to-end passive recon for a domain, website, or IP (UseOSINT) |
| `riset-x` | Research agent & free NFT projects found on X, with a strict filter |
| `scheduled_delivery_proof` | Verify scheduled delivery from the chat transcript, never from state files |
| `security-audit` | Security guidance & vulnerability review — 6-phase audit orchestration |
| `serangan-agen` | Serangan Agen — agent-pipeline attack methodology (from a real campaign study) |
| `serok` | Find NFTs listed far below their collection floor, verified only |
| `skill-foundation` | Doctrine: skills are the foundation of every substantial task |
| `skill-security-audit` | Audit a skill for security risks before installing it (SafeClaw) |
| `simular-box-browsing` | Cloud-Linux-desktop browsing fallback when Cloudflare or an IP block stops the normal route |
| `square_post_preflight` | Preflight checks for social posts: count cashtags by mentions, recompute figures |
| `supply-chain-risk-auditor` | Audit dependencies for supply-chain risk (Trail of Bits) |
| `token-integration-analyzer` | Token integration analysis: ERC20/ERC721 conformity + weird-token patterns |
| `variant-analysis` | Hunt for the other instances of a bug already found (Trail of Bits) |
| `video-gambar` | Make video & images end to end: AI ads, code animation, motion graphics |
| `wayfinder-assist` | Division of labor with the Wayfinder API (read-only scans + wallet info) |

## Principles

- **Evidence over inference.** A finding is only real after source → proof →
  self-refutation → cross-check. A simulation is not a result.
- **Authorization gates.** Active testing only with verified permission;
  read-only work and testing on your own accounts need no extra approval,
  everything else does.
- **Rules only count when installed.** A lesson written in a pattern bank
  but not wired into the brief, cron, or skill that does the work is dead text.

## Licenses

Most skills here are original work, shared as-is. A few are adapted from
upstream projects and keep their own `LICENSE` files — check the license
inside each skill directory before reuse (notably `bug-hunter` and the
Trail of Bits / Cloudflare-origin security skills). `humanize-skills` is CC-BY-4.0 (declared in its `SKILL.md` frontmatter); `binance-square-post` is Binance's official skill, included verbatim with a local amendment.

## No personal data

This repository intentionally contains no personal data: no real email
addresses, phone numbers, private keys, seeds, API keys, or personal wallet
addresses. Contract addresses that appear are public on-chain protocol
contracts used as audit examples. Email addresses in examples are
placeholders (`attacker@evil.com`, `victim@test.com`).
