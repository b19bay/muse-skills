# Provenance — supply-chain-risk-auditor

- **Upstream:** Trail of Bits — https://github.com/trailofbits/skills
- **Path in repo:** `plugins/supply-chain-risk-auditor/skills/supply-chain-risk-auditor/`
- **Commit installed:** `149d7b21f4067765b82e67029730b42d228ef4b4` (commit 2026-11-12)
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry; repo 8.1k stars)
- **License:** CC BY-SA 4.0 (Attribution-ShareAlike 4.0 International) — the
  full license text was fetched from the repo root and included here as
  `LICENSE`. Any adaptation must keep attribution and share-alike.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/supply-chain-risk-auditor/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist). Folder name
  drops the `trailofbits-` staging prefix; origin is recorded here and in
  `skill.yaml`.

## Security audit verdict: CLEAN (2026-11-14)

Entire SKILL.md (122 lines) + all supporting files read in full: `scripts/
collect.py` (1,568 lines), `scripts/sources.py` (683), `scripts/model.py`
(402), `scripts/render.py` (809), 4 test files (1,863 lines), `pyproject.toml`,
`uv.lock`, `agents/openai.yaml`, `assets/trail-of-bits-mark.svg`. No script
was executed.

- Network only to known public registries/advisories, via stdlib `urllib`:
  `api.osv.dev`, `registry.npmjs.org`, `api.npmjs.org`, `pypi.org`,
  `proxy.golang.org`, `api.deps.dev`, `api.github.com`, `api.scorecard.dev`.
  `pyproject.toml` has `dependencies = []`.
- GitHub token read via `gh auth token` (subprocess, no shell) and used ONLY
  as an `Authorization: Bearer` header to `api.github.com`; never written to
  files/logs or sent elsewhere.
- `pip-audit` is invoked with `--no-deps --disable-pip` so it never executes
  untrusted dependency code (stated in code comments).
- No `shell=True`, `eval`/`exec`, `curl|sh`, data exfiltration, or
  destructive commands. HTTP cache written mode `0o700` with cache-ownership
  verification; the renderer has Markdown anti-injection escaping plus
  `check_no_forged_lines` / `check_flags_reconcile` guards.
- The SVG logo contains no `<script>` / event handlers / `href`;
  `openai.yaml` is display metadata only.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md (scripts untested on this VM —
  sandbox-test before first use; the `allowed-tools` frontmatter field is a
  Claude Code convention, inert in Muse).
- Added `LICENSE` (CC BY-SA 4.0 full text, fetched from the repo root —
  staging did not include it).
- Scripts and tests are upstream-verbatim; no logic changed.

## Before first use (mandatory)

The scripts have NEVER been executed on this VM. Test them in a sandbox on a
throwaway project first: run the collector on a small lockfile, confirm the
network calls go only to the hosts listed above, and confirm `pip-audit`
runs with `--no-deps --disable-pip`.
