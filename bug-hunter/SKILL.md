---
name: bug-hunter
description: End-to-end bug bounty hunting workflow — recon (subdomain enumeration, live hosts, URL crawling, nuclei, JS secrets), pre-hunt learning (disclosed reports, threat modeling), vulnerability hunting (IDOR, SSRF, XSS, auth bypass, race conditions, GraphQL, business logic, LLM/AI security), bug chaining (A→B→C escalation), finding validation (7-Question Gate, 4 pre-submission gates), and report writing (HackerOne/Bugcrowd/Immunefi templates, CVSS 3.1, PoC). Use for ANY bug bounty task — starting a new target, doing recon, hunting a specific vuln class, validating a finding before reporting, or writing a report. Adapted from AwareXone Agentic-Bug-Hunter (MIT). The pentest-web 3-tier authorization gate applies to every step.
---

# Bug Hunter — Recon to Report

Full pipeline: **Recon → Learn → Hunt → Validate → Report.** One skill for everything.

Source: adapted from [AwareXone/Agentic-Bug-Hunter](https://github.com/awarexone/Agentic-Bug-Hunter) (MIT, v6.0.1, cloned 2026-11-13). See `ATTRIBUTION.md` + `LICENSE`. The upstream repo is a Claude Code plugin + Python CLI; this skill is the **playbook + tooling** ported for Muse. The upstream autopilot/agent mode (`bughunter hunt`, `/autopilot`) is **NOT** ported — Muse drives every step, and no request is sent to a target without the authorization gate below.

## Authorization gate (decide the tier BEFORE touching the target)

This skill inherits the **pentest-web 3-tier gate** — read `~/workspace/custom-skills/pentest-web/SKILL.md` for the full text. Summary:

- **Tier 0 — Passive observation.** Public sources, public pages, public DNS, disclosed reports, source code the target published. Always allowed.
- **Tier 1 — Safe probes on your OWN account/data.** Only on accounts the user owns or test accounts the assignment provides, and only on in-scope assets.
- **Tier 2 — Active probes.** Injection payloads outside your own account, access to other accounts' objects, state changes, race requests, cache poisoning on shared URLs, takeover claims. **ONLY with explicit written authorization** — a bounty program scope that allows the technique, a written assignment, or the owner's written instruction. In this workspace the user's phrase **"lakukan simulasi nyata"** (or an equivalent written permission) is the gate for Tier 2. Without it, stop at Tier 1 and report candidates + the test plan.
- **Hard bans, no exceptions:** destructive/DoS actions outside explicit scope; touching real users' data beyond the minimum needed for a PoC; **copying/storing third-party PII values — record existence and shape, never the value**; claiming takeover resources when the program forbids it; continuing after a program says out-of-scope.

The upstream TERMS.md says the same thing in its own words: targets must be listed in an active bounty program and the asset must be in scope. If scope is unclear, verify scope first — never assume.

## The only question that matters

> **"Can an attacker do this RIGHT NOW against a real user who has taken NO unusual actions — and does it cause real harm (stolen money, leaked PII, account takeover, code execution)?"**
>
> If the answer is NO — **STOP. Do not write. Do not explore further. Move on.**

Kill these immediately: "could theoretically allow…", preconditions stacked 3 deep, wrong-but-harmless implementation, dead code with a bug, source maps without secrets, SSRF with DNS-only callback (need data exfil or internal access), open redirect alone (need ATO/OAuth chain), "could be used in a chain if…" (build the chain first, THEN report). **"Could" is not a bug. Prove it works or drop it.**

## Critical rules

1. **READ FULL SCOPE FIRST** — verify every asset/domain belongs to the target org.
2. **NO THEORETICAL BUGS** — the question above, every time.
3. **KILL WEAK FINDINGS FAST** — run the 7-Question Gate (`references/triage-validation.md`) BEFORE writing any report.
4. **Validate before writing** — check CHANGELOG, design docs, deployment scripts FIRST.
5. **One bug class at a time** — go deep, don't spray.
6. **Verify data isn't already public** — check the web UI in incognito before reporting API "leaks".
7. **5-MINUTE RULE** — if a target shows nothing after 5 min probing (all 401/403/404), MOVE ON.
8. **IMPACT-FIRST HUNTING** — ask "what's the worst thing if auth was broken?" If nothing valuable, skip the target.
9. **CREDENTIAL LEAKS need exploitation proof** — finding keys isn't enough, must PROVE what they access.
10. **STOP SHALLOW RECON SPIRALS** — don't probe 403s, don't grep for analytics keys, don't chase staging domains that lead nowhere.
11. **BUSINESS IMPACT over vuln class** — severity depends on CONTEXT, not just vuln type.
12. **UNDERSTAND THE TARGET DEEPLY** — before hunting, learn the app like a real user.
13. **DON'T OVER-RELY ON AUTOMATION** — automated scans hit WAFs, trigger rate limits, find the same bugs everyone else finds.
14. **HUNT LESS-SATURATED VULN CLASSES** — XSS/SSRF/XXE have the most competition. Expand into: cache poisoning, business logic, race conditions, OAuth/OIDC chains, CI/CD pipeline attacks, LLM/AI features.
15. **ONE-HOUR RULE** — stuck on one target for an hour with no progress? SWITCH CONTEXT.
16. **TWO-EYE APPROACH** — systematic testing (checklist) + anomaly detection (watch for unexpected behavior).
17. **Evidence before claims** — this workspace's standing rule: inference is not fact, simulation is not result. A finding is real only with a reproducible request + response (or fork/test PoC for contracts).

## Workflow per target

### Phase 0 — Scope & authorization
Write down: target, owner/program, scope (in/out), the gate tier that applies, test accounts available, techniques the program forbids. Without this, Tier 0 only.

### Phase 1 — Recon & surface map
Full pipeline in `references/web2-recon.md`. Standard sequence (Tier 0–1):
```bash
export PATH="$HOME/workspace/tools/bug-hunter-bin:$PATH"
subfinder -d target.com -all -o subs.txt          # subdomains (passive sources)
dnsx -l subs.txt -resp -o resolved.txt            # resolve + live hosts
httpx -l resolved.txt -title -tech-detect -o live.txt
katana -u https://target.com -d 3 -o urls.txt    # crawl (Tier 0 on public pages)
nuclei -l live.txt -t ~/nuclei-templates/ -o nuclei.txt   # template scan — check program rules first; some programs restrict automated scanning
```
**Nuclei on this VM stalls ~180 s at startup, EVERY run** (deterministic: 181 s in three separate runs) — then the scan itself runs in under a second. Never use a 60–120 s timeout: earlier runs killed at 60/100/120 s looked like a hang but were only mid-stall. Always run nuclei with `timeout 300` minimum (or in the background) and write output to a file, not through a pipe. Verified 2026-11-13: smoke scan 3×, all exit 0, 10/10 expected findings.
Then: JS analysis (LinkFinder/SecretFinder patterns in `references/web2-recon.md`), waybackurls/gau for historical URLs, ffuf for directory/parameter discovery (Tier 1+ — sends requests; keep `-rate` low, use `-ac`).
Result of this phase = a **prioritized surface list**, not findings.

### Phase 2 — Learn
Read disclosed reports for the target/program (HackerOne Hacktivity, Bugcrowd, Immunefi). Learn the app like a real user: crown-jewel thinking (what's the most valuable asset?), developer empathy (what would the dev forget to check?), trust-boundary mapping. See `references/bb-methodology.md` for the full 5-phase non-linear methodology.

### Phase 3 — Hunt
One bug class at a time. Vuln-class playbooks:
- Web2 classes: `references/web2-vuln-classes.md` + the 26 pattern cards in skill `pentest-web` (`POLA-WEB.md`) — the cards are the deeper reference for web vuln patterns; this skill's classes are the hunting checklist.
- Per-class command playbooks: `references/commands/` (jwt-scan, nosqli, cors, bypass-403, param-discover, secrets-hunt, takeover, token-scan, scan-cves, sast).
- GraphQL: `references/graphql-audit.md`. LLM/AI features: `references/llm-redteam.md`. MCP servers: `references/mcp-server-audit.md`.
- Smart contracts / Web3: skill `forensik_kontrak` is the deeper contract-forensics reference; this skill adds `references/web3-audit.md` + `references/web3/` (Solidity audit, DEX/LP attacks, Solana token audit, meme-coin bugs, PoC + Foundry).

### Phase 4 — Chain (A→B signal method)
When you find bug A, systematically hunt for B and C nearby. Single bugs pay; chains pay 3–10× more. Known chains: IDOR(read) → PUT/DELETE same endpoint → full data manipulation; SSRF → cloud metadata 169.254.169.254 → IAM creds → RCE; stored XSS + session cookie without HttpOnly → session hijack → ATO; open redirect + OAuth redirect_uri → auth code theft → ATO; S3 listing → JS bundles → OAuth client_secret → OAuth chain; rate-limit bypass → OTP brute force → ATO. Full table + 6-step cluster protocol: `references/bug-chaining.md`.

### Phase 5 — Validate (BEFORE writing anything)
Run the **7-Question Gate** in `references/triage-validation.md` — one wrong answer = STOP, kill the finding. Then the 4 pre-submission gates + the 60-second pre-submit checklist. Check the always-rejected list. A finding that fails validation is not reported — an N/A hurts the validity ratio; Informative is neutral.
- Python verifiers (SSRF-safe, single-hop): `scripts/bughunter/tools/verifiers/` — per-class oracles for XSS, SQLi, IDOR, redirect, auth bypass, sensitive file, OOB. The tools tree uses `from tools.…` imports, so run from `scripts/bughunter/` (or with `PYTHONPATH=scripts/bughunter`): `python3 -m tools.verifiers --help`. Also `scripts/bughunter/tools/scope_checker.py` (scope enforcement), `port_scanner.py` (nmap is not installed in this VM — use this), `sast_scan.py`, `token_scanner.py`.
- For contracts: the forensik 4-layer proof standard (source evidence → fork/test PoC → self-refutation → audit/postmortem cross-check) still applies — see skill `forensik_kontrak`.

### Phase 6 — Report
Templates by vuln class + CVSS 3.1 + PoC generation + submission checklist: `references/report-writing.md`. Bugcrowd-specific: `references/bugcrowd-reporting.md` (Bugcrowd VRT severity — same standard as pentest-web). **Bounty reports are written in English** (standing user rule); internal notes may be Indonesian. Human tone, no AI tells. Title formula + the "always-rejected" list are in the triage reference.

## Tooling installed in this VM

Recon binaries (Go, installed 2026-11-13): `~/workspace/tools/bug-hunter-bin/` — subfinder v2.17.0, httpx v1.12.0, nuclei v3.11.1, katana v1.8.0, dnsx 1.3.1, ffuf 2.1.0-dev, waybackurls, gau 2.2.4. Nuclei templates: `~/nuclei-templates/` (installed via `git clone --depth 1` of projectdiscovery/nuclei-templates — `nuclei -update-templates` TIMES OUT through this VM's proxy on the large download, so update templates with `git -C ~/nuclei-templates pull` instead; the "outdated" warning is cosmetic).
- **Nuclei ~180 s startup stall (this VM, proven 2026-11-13):** every nuclei invocation sits idle ~3 min after printing the PDCP-directory line, before the scan starts — regardless of template source (full 14,233-file dir or a 1-template dir), proxy env vars, or `-duc`. Cause: nuclei's startup remote check dials api.github.com directly, ignoring the proxy env vars, and the sandbox's direct route to that host blackholes (curl `--noproxy` to api.github.com hangs in connect >25 s; the same URL via the proxy answers in ~2 s). The check eventually times out and nuclei proceeds normally. No flag disables it (`-duc` does not help). Rule: `timeout 300` minimum per nuclei run; run in background for long scans. Finding order varies run to run — compare sorted output. Go toolchain: `~/workspace/tools/go/bin/go` (go 1.25.4; nuclei/katana auto-switch to the go1.26.11 toolchain). **Go builds MUST set `GOTMPDIR` to a directory on the main disk (e.g. `~/workspace/tools/go-tmp`) — `/tmp` is a 512 MB tmpfs and large builds (nuclei) fail with "no space left on device".**
- **nmap is NOT installed** (no apt/sudo in this VM) — use `scripts/bughunter/tools/port_scanner.py` instead.
- **semgrep** is optional (pip install semgrep) — the skill's SAST reference is `references/commands/sast.md`; `scripts/bughunter/tools/sast_scan.py` covers the common case.
- Optional free API keys improve recon coverage (Chaos, VirusTotal, SecurityTrails, Censys, Shodan) — configure in `~/.config/subfinder/config.yaml`. The pipeline works without them. Keys go in the Secure Vault flow, never in chat or files.

## Sibling skills — which one to use when

- **`pentest-web`** — the deeper web vuln pattern bank (26 cards + 7 chains, WSTG codes, false-positive traps) and the home of the authorization gate. For pattern-level hunting on a known surface, read its cards.
- **`forensik_kontrak`** — contract forensics (EVM logic, P-01..P-34, K-01..K-07). For smart-contract targets, this is the primary lens; bug-hunter's web3 references are the audit-workflow companion.
- **`forensik_node`** — node/API forensics (N-01..N-16). For node-implementation targets (consensus, P2P, node APIs).
- **`multichain-contract-audit`** — the 4-gate contract audit rubric (GO/CAUTION/BLOCK) across EVM + Solana.
- **`bug-hunter` (this skill)** — the end-to-end hunt workflow: recon pipeline, methodology, chaining, validation gates, reporting. It orchestrates; the sibling skills go deep.

## What this skill does NOT do

- No autopilot: nothing sends requests to a target on its own. Every probe is a deliberate, authorized step.
- No CLI agent mode: the upstream `bughunter` CLI needs an AI provider API key (Groq/Gemini/OpenRouter) — irrelevant here, Muse is the agent. The vendored Python package is used only for its standalone tools (verifiers, scanners, scope checker).
- No credential harvesting, no DoS, no data exfiltration beyond the minimum PoC — see the gate.
