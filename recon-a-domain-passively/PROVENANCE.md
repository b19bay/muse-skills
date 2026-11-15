# Provenance — recon-a-domain-passively

- **Upstream:** UseOSINT — https://github.com/UseOSINT/Skills
- **Path in repo:** `skills/recon-a-domain-passively/`
- **SKILL.md URL:** https://github.com/UseOSINT/Skills/blob/main/skills/recon-a-domain-passively/SKILL.md
- **Commit installed:** `06243a5620b0c9c97502edd4ee9e31995a3bdccd`
- **Fetched:** 2026-11-14 (via Hermes Skills Hub / GitHub; part of a 28-skill OSINT collection)
- **License:** MIT — `LICENSE` copied from upstream and included in this folder.
- **Installed:** 2026-11-14 into `~/workspace/custom-skills/recon-a-domain-passively/`
  at the user's order ("pasang semua", 8-skill Hermes shortlist).

## Security audit verdict: CLEAN (2026-11-14)

SKILL.md (256 lines) + `reference/asset-inventory.md` + `ETHICS.md` (35
lines) read in full + grepped. 100% passive OSINT workflow (not one packet
to the target): written scope first, cheapest-and-quietest ordering, asset
inventory schema with provenance + timestamp per row, saturation-based
stopping rule, separate confidence grading for liveness vs attribution,
complete worked example, legal/ToS notes. Zero dangerous-pattern grep hits.
No scripts. No external URLs except a useosint.com reference in the
description. `ETHICS.md` states: passive by default, no login / probing /
exploiting without written authorization, no doxxing/stalking, data
minimization.

## Adaptations made for Muse (2026-11-14)

- Added a Muse adaptation header to SKILL.md: the sibling technique skills
  this workflow routes to (who-owns-this-domain, find-hidden-subdomains,
  find-exposed-servers, read-deleted-pages, google-like-a-spy,
  secrets-in-git-history, find-the-original-image, x-ray-a-company,
  who-really-owns-it, what-an-email-reveals, write-the-intel-brief) are NOT
  installed — each routed step is executed with Muse's own tools (web
  search, page fetch, DNS/public-record lookups via available connectors
  and CLI tools), keeping the same ordering, inventory schema, and stopping
  rule.
- The `disable-model-invocation: true` frontmatter flag is preserved as
  metadata. Muse has no native support for it, so the skill is treated as
  explicitly invoked: run it only when the user (or a parent task) asks for
  passive domain recon. (Note: `skill.yaml` sets `include_in_prompt: true`
  per the user's standing rule that all skills be usable; the
  explicit-invocation intent above still governs when to run it.)
- No other content changed. SKILL.md body, `reference/asset-inventory.md`,
  `ETHICS.md`, and `LICENSE` are upstream-verbatim.
