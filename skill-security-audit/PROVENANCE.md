# Provenance — skill-security-audit

- **Upstream:** SafeClaw Security (safeclaw-sec) — https://github.com/safeclaw-sec/skill-security-audit
- **SKILL.md URL:** https://github.com/safeclaw-sec/skill-security-audit/blob/main/SKILL.md
- **Commit installed:** `9f13e9d95892b1168a3b5dac9fabb4e261be9607`
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / ClawHub registry)
- **License:** MIT (declared in the upstream README; no LICENSE file exists
  in the upstream repo, so none is included here).
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/skill-security-audit/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist).

## Security audit verdict: CLEAN (2026-11-14)

SKILL.md (498 lines) read in full; all scripts grepped and critical parts
read: `scripts/audit.py` (1,477 lines), `scripts/intent_analyzer.py`
(522 lines), `scripts/sandbox.py` (355 lines), `scripts/install.sh`,
`scripts/build-sandbox.sh`, `Dockerfile`. No script was executed during
audit or install.

- `audit.py` uses only Python stdlib; its only network call is an optional
  GET to `https://clawhub.ai/api/skills/<name>` (author-reputation lookup,
  5-second timeout, disableable with `--no-clawhub`). Occurrences of
  `eval`/`exec`/`subprocess`/`base64`/`os.environ` in `audit.py` are
  REGEX DETECTION PATTERN STRINGS (the scanner detecting those patterns in
  other skills), not executed code — contexts verified.
- `sandbox.py` runs docker/bwrap/firejail as fixed argument lists (no
  shell) + `audit.py` inside the sandbox; `Dockerfile` uses a non-root
  user and only copies `audit.py`. `install.sh` only git-clones this repo
  itself + optional docker build. `intent_analyzer.py` is stdlib-only,
  reads local files, no network.
- No credential exfiltration, no `curl|sh`, no URLs other than clawhub.ai
  and docs.docker.com.
- The skill's defensive "vaccine" framing (instructions to treat audited
  content as UNTRUSTED DATA + per-session hash encapsulation tags) is the
  skill's purpose, not an attack — and matches this workspace's own policy
  of treating outside content as data.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md: "OpenClaw skill" here means
  any agentskills.io-format skill (Muse custom skills in
  `~/workspace/custom-skills/` and staged candidates in
  `~/workspace/hermes-skills/`); install paths default to
  `~/workspace/custom-skills/`; the intent-analysis model table has no Muse
  entry — state the model as "Muse (unlisted — use the `unknown`
  confidence row)"; scripts untested on this VM — sandbox-test before first
  real use.
- `scripts/audit.py`: skill-name resolution now tries the Muse paths first
  (`~/workspace/custom-skills/<name>`, `~/workspace/hermes-skills/<name>`),
  keeping the upstream OpenClaw paths as fallbacks. No other logic changed.
- `scripts/install.sh`: default `SKILLS_DIR` changed to
  `$HOME/workspace/custom-skills` (env overrides `MUSE_SKILLS_DIR`, then
  legacy `OPENCLAW_SKILLS_DIR`, preserved).
- `README.md` + `AI_INSTALL_GUIDE.md`: install-path examples changed from
  `~/.openclaw/skills` to `~/workspace/custom-skills/`; the audit-test
  example target changed to a staged Hermes candidate
  (`~/workspace/hermes-skills/weather`); "OpenClaw skill directory"
  reworded to "agentskills.io-format skill directory".
- All other content (SKILL.md body, `intent_analyzer.py`, `sandbox.py`,
  `Dockerfile`, `TESTING.md`) is upstream-verbatim.

## Before first use (mandatory)

The scripts have NEVER been executed on this VM. Test `audit.py` in a
sandbox on a known-clean skill before first real use.
