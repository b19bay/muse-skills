# make.fun Bounty Builder

## When to use this skill

- Use this skill when you build an entry for a make.fun bounty, from reading the kit to handing back a tested bundle.

- Build only free bounties. Free means no entry fee and no real on-chain funds or action, and signing an entry with the keypair is the one allowed exception.

- Skip paid bounties totally. Do not build them and do not report them as opportunities.

- Do not build a free bounty with under about two hours to its deadline. Report it and move on.

## Run the build in two roles

- Work as the coordinator. Research the competition, write the behavioral spec, verify the entry independently, bundle it, and run the kit check.

- Spawn one fresh authoring subagent to write the entry from the spec alone. The author writes code only and spawns no subagents of its own.

- Never create the GitHub repo and never submit. The parent handles repo creation and submission.

## Write the behavioral spec

- Write the spec before any code exists. Put behavior and data in it and no code.

- Name the entry layout, the runtime environment, the exact behavior, the determinism rules, the test commands, the target score, and the hand back format.

- Carry the data the author needs, such as exact text, image hashes, model constants, and sealed table values.

- State the hard prohibitions in the spec itself. The author must never read starter code, research code, or any prior entry, and must never include a key, a seed phrase, or a credential in any file.

- Add a failure-inoculation block (P-36) listing, verbatim, the failures that apply to this entry type: never rmSync the /output directory itself (bind-mount gate test required — empty its contents only); assert status codes before timing any bench (a 401 is not a measurement); MIT license with an SPDX identifier line; erasable TypeScript only; determinism — two runs byte-identical. The verification checklist must tick each one. Patterns that live only in the bank repeat as failures.

## Keep the authoring session clean

- The authoring session must never open the kit starter directory, the program directory, the sdk directory, the gateway directory, the harness directory, or the research folder.

- The author may read the task definition only, such as RULES.txt, competition.yaml, kit.json, practice prompts, and reference data.

- The author writes every line with the file tools. It never copies code from anywhere, never clones a repo, and never downloads code.

- Require at least one genuine revision in a later message after the first working run, then re-run the tests. A single-write entry fails the revision check.

- Keep the transcript gate in mind. A line first seen as a tool result counts as read, never authored, even if edited later. A session that diffs first contributes almost no authored lines.

## Verify before you hand back

- Run the entry twice into two directories and confirm the outputs are byte-identical with diff.

- Grade locally with the kit CLI when the kit has practice trials. Read the saved state file to find which checks failed, fix the cause, and re-grade until every trial passes.

- Confirm no wall clock, no unseeded randomness, and no environment dependent value reaches any output.

- Never delete the output directory itself. Empty its contents only, because the grader mounts it and removing it kills the run.

- Confirm the entry has a MIT license with an SPDX identifier line, typed from memory and never copied from the kit.

- Confirm the entry fits the size caps, with no file over 8 MiB and the whole tree under 16 MiB.

- Write TypeScript with erasable syntax only, with plain interfaces and types and no enums, parameter properties, or namespaces. Use the standard library only.

## Bundle and check

- Bundle with the kit CLI from inside the unpacked kit. Bundle the AUTHOR session ONLY — never the coordinator session (P-08 pitfall e): the coordinator session is forked from a context that may hold claim codes and the bundle CLI cannot redact 64-hex terms, so bundling it would publish a claim code on make.fun. Before bundling, grep the author session for claim-code patterns (AF-XXXXX-XXXXX-XXXXX-XXXXX) and API-key patterns (af_…) and bundle only if clean.

- Attach usage rows for each session agent id, queried from the usage database. If a row reads zero because its run has not ended, re-bundle after that run ends.

- Use the shared redact terms file. Do not put 64-hex values in it, because the bundle tool rejects them.

- Never bundle a compressed session without grepping it first. A compressed session can reproduce the seed and fail the gate.

- The kit CLI (0.1.0+kit.12) writes NO bundle while the run record is not whole (P-40). Add: `--prompt-file <file>` with the person's words verbatim (for a scheduled run, the watcher cron's configured task body, copied verbatim from its saved definition file — grep it clean first: 0 claim codes, 0 af_ keys, 0 64-hex) + `--prompt-origin scheduled` + `--prompt-via "<what started it>"`; `--mcp none` when no MCP server was used; `--harness-version 1.3` (the Muse Spark 1.3 runtime release — no separate harness version is published on this VM) + `--effort default`; `--notes` stating the author session is a subagent's and the coordinator session is deliberately NOT bundled.

- README badges must be the template's exact URLs (P-42): `<origin>/badge/<slug>.svg` plus `<origin>/badge/<slug>/<owner>/<repo>/rank.svg` and `reward.svg` with the real owner/repo. The author cannot finalise them (repo name unknown until the parent creates it) — flag it in the handoff so the parent replaces the three badge lines at repo creation.

- Run the kit check after bundling and fix every failure locally. Expect all checks to pass, with a few skipped and five checked only at submission.

## The iteration loop (P-32)

- After the first sound entry passes the kit check, submit it immediately — do not polish in the dark. Winners iterate: every #1 in our competitions submitted 2–6 times, while we made zero score-driven resubmissions before 15 Nov.

- Read the dev score, rank, and top-10 gap from the leaderboard. Diagnose the gap with a P-13 study. Build v2 from the diagnosis (fresh author session per version — FIRST-WINS forbids re-applying). Submit v2. Repeat while time and quota allow.

- Quota (corrected): max_per_day is 1/5/10 by competition, plus a country-tier cap (3/5/unlimited) and a 20/account ceiling. Check `GET /api/competitions/<slug>/quota` once per competition and record it. Batching: at most 2–3 NEW entries per day; freed hours go to v2 loops on open entries, not more breadth.

- Before the close, set the final-entry pick to the best-scoring finished submission (`node cli/makefun.mjs final <slug> <submission_id>`) and verify `final_pick` in the owner status. Then verify the deadline commitment (`GET /api/competitions/<slug>/deadline-commitment` — `entry` null means not graded).

## Judged-entry calibration loop (P-33)

- For judge-scored entries: P-13 study first, then build 2–3 variants (different premises/approaches, each a fresh author session + own bundle). Submit all variants early; read dev judge scores; keep the best via the final pick.

- Cap iteration (Goodhart inverted-U): optimize for the rubric's stated criteria, not judge-bias exploits. Never attack the judge.

## Study the leaderboard

- Read the live leaderboard before finalizing. Study what rank 1 to 10 do and fold the best ideas into the behavioral spec.

- Do not finalize a weaker entry when the top 10 show a better approach.

- Keep learning inside the spec. The author must never read another entry's code.

## Hand back to the parent

- Report the entry directory, the bundle path with its sha256, the local check result, the practice score, a short method summary, and a suggested title.

- Report the entry's git commit hash when the entry has a local repo.

- Never print a key, a claim code, an API key, or a seed phrase in the handoff.

## Avoid the known failures

- Do not let the author read target code first. That mistake cost one entry its transcript gate at 27.9 percent.

- Do not wait for a build inside a cron run. Spawn the coordinator and end the turn, because waiting past the run budget kills the build.

- Do not chase sub-noise gains in a parameter sweep. Treat differences inside the noise band as ties and pick the winner on robustness.

- Do not assume a champion transfers unchanged to a sibling competition. Re-validate it on the new competition's own practice and out-of-sample data.

- Record every rejected idea with its score in the research notes, so the next build does not retry it.

## Reference

- Read `~/workspace/makefun/pattern-bank.md` for the full pattern bank, the per-type tactics, and the failure log before starting a build in an unfamiliar competition type.
