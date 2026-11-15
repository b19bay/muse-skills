# Provenance — property-based-testing

- **Upstream:** Trail of Bits — https://github.com/trailofbits/skills
- **Path in repo:** `plugins/property-based-testing/skills/property-based-testing/`
- **Commit installed:** `149d7b21f4067765b82e67029730b42d228ef4b4` (commit 2026-11-12)
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / skills.sh registry; repo 8.1k stars)
- **License:** CC BY-SA 4.0 (Attribution-ShareAlike 4.0 International) — the
  full license text was fetched from the repo root and included here as
  `LICENSE`. Any adaptation must keep attribution and share-alike.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/property-based-testing/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist). Folder name
  drops the `trailofbits-` staging prefix; origin is recorded here and in
  `skill.yaml`.

## Security audit verdict: CLEAN (2026-11-14)

SKILL.md (68 lines) read in full + all files grepped: `references/
generating.md`, `references/interpreting-failures.md`, `references/
libraries.md` (Echidna/Medusa), `references/refactoring.md`, `references/
reviewing.md`, `agents/openai.yaml`, `assets/trail-of-bits-mark.svg`,
`README.md`. This skill contains no executable scripts.

- Methodology for property-based testing (Hypothesis, fast-check, proptest,
  jqwik, Echidna/Medusa for Solidity invariants). The only dangerous-pattern
  grep hit is a mention of `os.environ` as an example of hard-to-test global
  state (`references/refactoring.md`) — prose, not code.
- The only external URL is https://secure-contracts.com (Trail of Bits'
  own site). No `curl|sh`, no network/credential instructions.
- The SVG logo contains no `<script>` / event handlers / `href`;
  `openai.yaml` is display metadata only.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md noting the pairing with the
  local `forensik-kontrak` skill: forensik-kontrak hunts invariants
  manually until they break; this skill encodes those invariants as property
  tests and fuzzer harnesses (Echidna/Medusa for Solidity).
- Added `LICENSE` (CC BY-SA 4.0 full text, fetched from the repo root —
  staging did not include it).
- All methodology and references are upstream-verbatim.
