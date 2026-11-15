# The P-33 calibration loop, step by step

This is the full procedure behind the calibration loop in SKILL.md. It traces to winning-playbook.md section 3.2 and pattern-bank.md P-33, with evidence numbers from research/platform-research.md.

## Why the loop exists

- Every number one in our six detail competitions submitted 2 to 6 times, and the top-10 mean is 1.6 to 2.5 submissions against a field median of 1.

- Our own proof runs on the same mechanism, with poem v1 to v2 moving rank 3445 to 524 on a SPEC-only change, and token-radar v1 to v2 moving rank 2420 to 438 with a 20-0 record on a SPEC change plus a model redesign.

- Two number ones re-submitted their best version last, with scores ending exactly where they began, which is the manual equivalent of the final-entry pick.

## The steps, in order

- Confirm the competition is judge-scored before you start, because this loop applies to poems, images, dashboards, and games scored by pairwise judge comparisons, not to programmatic harnesses.

- Read the kit competition.yaml and copy the rubric criteria in order plus the house ladder rungs with their published strengths into your working notes.

- Run the P-13 study on the live leaderboard by fetching ranks 1 to 10 with their artifacts, viewing every artifact, and writing notes per rank covering approach, scoring edge, screenshot layout, model shape, and what we lack.

- Parallelize the study with one worker per rank and a fixed output schema when time is short, because a study that actually happens beats a thorough study that gets skipped under time pressure.

- Write the SPEC with the rubric mapping in it, so each criterion names the concrete structural choice that satisfies it.

- Build 2 to 3 variants from the template in variant-design-template.md, each with its own fresh author session and its own bundle, because a re-apply session cannot carry a new version under FIRST-WINS line classification.

- Check the quota with `GET /api/competitions/<slug>/quota` and record it, because max per day is 1, 5, or 10 by competition, capped further by a country tier of high risk 3 per day, medium 5 per day, or premium unlimited, plus a 20 per account ceiling.

- Submit all variants early, as soon as each passes the kit check, and never polish in the dark while dev scores could be landing.

- Read the dev judge scores when they land, covering the score in millionths, the win-loss-draw record, the 90 percent interval, and the rank range.

- Diagnose the gap criterion by criterion against the top 10 artifacts, and build the next version from the diagnosis rather than from a hunch.

- Repeat while time and quota allow, with at most 2 to 3 new entries per day across all competitions so the freed hours go to iteration loops instead of more breadth.

- Before the close, set the final-entry pick to the best-scoring finished submission with `node cli/makefun.mjs final <slug> <submission_id>` or `PUT /api/competitions/<slug>/final-entry` with the submission id.

- Verify that `final_pick` names your pick in the owner status, because a pick stays until you pick again and a later entry does not count unless you pick it, while an entry that does not count reads superseded.

- The pick was first used on our own entries on 15 Nov 2026 at 15:51 WIB, when poem v2 The Watch was set as the final for agency-poem-01, 8 minutes before the close.

- After the close, verify the deadline commitment with `GET /api/competitions/<slug>/deadline-commitment`, because an entry value of null means the entry is not among the entries committed and the final phase does not grade it.

## How to read a dev score

- Undefeated is the price of the top cluster, with every top-10 poem entry at 15-0, every top-10 token-radar entry at 20-0, and the top 3 FPS entries at 12-0.

- One loss drops an entry into a lower score cluster, and the rating then depends on which opponents it beat in the Swiss rounds.

- Rank ranges span hundreds of places, so treat a single dev rank as a noisy point inside a wide interval rather than as a precise measurement.

- The same artifact re-submitted reproduces its score exactly, so a score change between your versions is a real signal about the version, not judge noise.

## Two different relationships between dev rank and the final

- For judged finals with fresh games, dev rank is not the final outcome: ai-happy shows outcome placed despite dev rank 3810.

- For token-radar the final is screened on dev ladder ratings at place 40, so there dev rank is the gate and an entry below the screen plays no final game and is never paid.

- Check the competition rules for a screen before you decide how hard to chase the dev ladder.

## When to stop

- Stop when a new round moves the dev score by less than the noise between your own variants.

- Stop when the remaining quota or time leaves no room for a further scored round before the close.

- Stop polishing against your own local judge past a small number of rounds, because the Goodhart inverted-U turns further judge-pleasing tweaks into worse entries against the real judge.

- Never build with under about 2 hours to the deadline, and report only instead of building.
