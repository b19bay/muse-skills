# Provenance — variant-analysis

- **Upstream:** Trail of Bits — https://github.com/trailofbits/skills
- **Path in repo:** `plugins/variant-analysis/skills/variant-analysis/`
- **Commit installed:** `149d7b21f4067765b82e67029730b42d228ef4b4` (commit 2026-11-12)
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry; repo 8.1k stars)
- **License:** CC BY-SA 4.0 (Attribution-ShareAlike 4.0 International) — the
  full license text was fetched from the repo root and included here as
  `LICENSE`. Any adaptation must keep attribution and share-alike.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/variant-analysis/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist). Folder name
  drops the `trailofbits-` staging prefix; origin is recorded here and in
  `skill.yaml`.

## Security audit verdict: CLEAN (2026-11-14)

Entire SKILL.md (76 lines) + all supporting files read in full:
`references/root-cause.md`, `references/searching.md`, `references/triage.md`,
`references/reporting.md`, `resources/variant-report-template.md`, 5 CodeQL
query templates (`resources/codeql/*.ql` — python/javascript/java/go/cpp),
5 Semgrep rules (`resources/semgrep/*.yaml`), `agents/openai.yaml`,
`assets/trail-of-bits-mark.svg`. This skill contains no scripts.

- Pure methodology + detection-query templates; no network commands, no
  credentials, no executed code. Occurrences of `os.system` / `subprocess` /
  `eval` / `exec` appear ONLY inside Semgrep/CodeQL detection patterns
  (strings being detected, not executed) — each context verified.
- CodeQL templates are standard taint-tracking queries (source/sink/barrier,
  `[VARIANT_NAME]` / `[ORIGINAL_BUG_ID]` placeholders); Semgrep rules are
  standard taint + pattern-match rules with `paths.exclude` for test/vendor
  directories. Shell commands mentioned are local `rg` (ripgrep) and example
  `semgrep` invocations — no `curl|sh`, no URLs.
- The SVG logo contains no `<script>` / event handlers / `href`;
  `openai.yaml` is display metadata only.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md mapping the two companion skills
  this skill references but which are NOT installed here:
  `audit-context-building` → use the recon phase of the local
  `forensik-kontrak` skill (or the `security-audit` skill's recon phase);
  `issue-writer` → use the local `bug-hunter` report templates
  (HackerOne/Bugcrowd/Immunefi).
- Added `LICENSE` (CC BY-SA 4.0 full text, fetched from the repo root —
  staging did not include it).
- All methodology, references, and query templates are upstream-verbatim.
