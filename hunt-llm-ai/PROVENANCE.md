# Provenance — hunt-llm-ai

- **Upstream:** h-mmer/pentest-agents — https://github.com/h-mmer/pentest-agents
- **Path in repo:** `skills/hunt-llm-ai/SKILL.md`
- **Registry listing:** https://www.skills.sh/h-mmer/pentest-agents/hunt-llm-ai
- **Commit installed:** `41d49b644e1bc0f3031819410fc5406918360c4e`
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry)
- **License:** MIT (declared in the repo's `pyproject.toml`: `license = { text
  = "MIT" }`; no LICENSE file exists in the upstream repo root, so none is
  included here. The repo README states: "For authorized security testing
  only. Follow responsible disclosure.")
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/hunt-llm-ai/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist).

## Security audit verdict: CLEAN, with standing cautions (2026-11-14)

The full SKILL.md (991 lines, single file, no scripts/references) was read
completely by the installer during installation — no segment left unread.
The earlier survey audit read lines 351–991 in full and lines 1–350 via
targeted pattern scans; the installer's full re-read confirms the same
verdict.

- The file contains live prompt-injection / jailbreak payload examples BY
  DESIGN — that is the skill's content (hunting playbook), all anchored to
  public CVEs, GHSAs, and disclosures (LangChain, Ollama, BentoML, MLflow,
  Open WebUI, Microsoft 365 Copilot, Shortwave, etc.). The payload examples
  are examples to test against a target, NOT instructions to the agent
  reading this skill.
- The skill's own Gate 0 validation requires: scope check, a controlled test
  account / own data, redacted proof, and STOP if any of its 5 conditions
  fails. Its "minimum proof ceiling" requires own mailbox / own document /
  own tenant / synthetic RAG corpus, and redacted length + hash instead of
  real secrets.
- No `curl|sh`, no instruction to ignore authorization/scope, no command
  stealing the user's credentials or sending data to a real external server.
  URLs in the file are security-research domains (genai.owasp.org,
  embracethered.com, insinuator.net, simonwillison.net, arxiv.org, NVD,
  penligent.ai, zeropath.com) plus PoC placeholders (`attacker.com`, `oob`,
  `169.254.169.254`, `localhost`).
- NOTE: one read of this file during installation was flagged by the runtime
  safety filter — that is the filter reacting to the payload examples, not
  evidence of malice. No instruction in the file was followed by the
  installer; installation was performed solely under the user's explicit
  order and the parent task.

## Adaptations made for Muse (2026-11-14)

- Added a binding AUTHORIZATION GATE header to SKILL.md tying this skill to
  the pentest-web 3-tier gate: Tier 0 passive always allowed; Tier 1 safe
  probes on the user's OWN account/data only; Tier 2 active probes ONLY with
  explicit written authorization (in-scope bounty program, written
  assignment, or the user's phrase "lakukan simulasi nyata"). The payload
  examples were NOT removed — their use is governed by the gate.
- No other content changed. The file is upstream-verbatim apart from the
  added header.
