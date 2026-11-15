# Judging Calibration for make.fun

Use this skill when you build or rebuild a judge-scored make.fun bounty entry, which means a poem, an image, a dashboard, or a game whose score comes from pairwise judge comparisons rather than a programmatic harness. Read it before you write the SPEC, because calibration decisions made after the build are mostly too late. Pair it with [makefun-bounty](~/workspace/custom-skills/makefun-bounty/SKILL.md) for the build flow, [video-gambar](~/workspace/custom-skills/video-gambar/SKILL.md) for the multi-candidate director plan, [image-search](/opt/muse/skills/image-search/SKILL.md) for style references, and [wide-research](/opt/muse/skills/wide-research/SKILL.md) for a parallel top-10 study.

## Read the judge before you write the SPEC

- Read the kit competition.yaml before you write a word of the SPEC, and copy the judge rubric criteria into the SPEC in their published order.

- Read the house ladder rungs in the same file with their published strengths, because the rungs show what the judge rewards most in this exact competition.

- Map every rubric criterion to one concrete structural choice in the entry, and write that mapping into the SPEC so the author can build to it.

- Treat the published judge prompt as legitimate reading material, because the platform publishes it and reading it is the documented P-16 move.

- Never copy a house rung or a top-10 entry, because the final scans for copies and a near copy takes no prize.

## Run the calibration loop

- Start with a P-13 study of the live top 10, fetch the leaderboard and the winning artifacts, and write notes on what each top entry does before you design anything.

- Build 2 to 3 variants with different premises or approaches, and give each variant its own fresh author session and its own bundle.

- Submit all variants early, while the dev judge scores still have time to land and while quota remains for a further round.

- Check the quota before you plan the rounds with `GET /api/competitions/<slug>/quota`, because max per day is 1, 5, or 10 by competition, capped further by a country tier and a 20 per account ceiling.

- Read the dev judge scores for every variant, and keep the best one with the final-entry pick before the close.

- Set the final pick with `node cli/makefun.mjs final <slug> <submission_id>` or `PUT /api/competitions/<slug>/final-entry` with the submission id, then verify that `final_pick` names it in the owner status.

- Verify the deadline commitment after the close with `GET /api/competitions/<slug>/deadline-commitment`, because an entry value of null means the entry is not graded.

- Follow the full step-by-step procedure in [references/calibration-procedure.md](references/calibration-procedure.md).

## Design variants that differ

- Vary the premise, the structure, or the approach between variants, and hold the format, the length band, and the quality bar constant so the dev scores compare like with like.

- Make each variant a genuine alternative rather than a tweak, because variants that differ only in polish teach you nothing about which direction the judge prefers.

- Give the author of each variant the same rubric mapping and the same top-10 notes, so differences in score trace to the variant design and not to different instructions.

- Plan the variants with the template in [references/variant-design-template.md](references/variant-design-template.md).

## Read dev scores and pick the winner

- Compare variants on dev judge score first, then on win-loss record, because an undefeated record is what puts an entry in the top score cluster.

- Treat a small score gap between two of your own variants as noise when their 90 percent intervals overlap, and pick on the rubric mapping rather than on the last few thousand points.

- Remember that dev rank is not the final outcome for judged finals with fresh games, except where the final is screened on the dev ladder, as token-radar is at place 40.

- Keep the artifact small, because ties break on bytes with lower better, and we already win the bytes tie-break against every current number one we have compared.

- Never rely on the latest submission being the best, because scores dip between versions and a pick is what locks the best one in.

## Learn from the poem

- Map each rubric criterion to a structural choice, using the agency-poem rubric as the worked example in [references/poem-rubric-mapping.md](references/poem-rubric-mapping.md).

- End a poem on an image rather than a thesis, because the rubric bans slogans and our v1 failed criteria 2 and 3 with a slogan ending.

- Build a turn into the poem, because the number one poem is a 3-scene reversal with dialogue and our v2 is one static scene with no turn.

- Draft 3 poems from 3 distinct concrete premises, score each against the 5 rubric criteria in order, and ship the winner.

## Learn from the images

- Generate 6 to 8 candidates across different subjects and compositions, view each at full size, and score them against the rubric before you pick.

- Downscale the top 3 candidates to about 300 pixels side by side and pick on appetite plus readability plus craft, because the judge reads small.

- Prefer compositions with no hands and no text unless the brief needs them, because broken hands and garbled text are the main artifact risks.

- Save a photo entry as JPEG bytes inside a file named entry.png when a PNG would exceed the 1 MiB cap, and verify the JPEG magic bytes and the dimensions after the copy.

- Verify every stated fact against at least two independent wire reports for a news entry, and record them with the verification time.

- Find the full image procedures, the screenshot-and-critic loop, and the novelty premium in [references/image-lessons.md](references/image-lessons.md).

## Know where to stop

- Optimize for the rubric stated criteria, not for judge-bias exploits such as length padding or formatting tricks, because those are the features that collapse under a different judge draw.

- Cap self-judge iteration rounds, because proxy reward rises monotonically while true reward rises then falls, and past the sweet spot more judge-pleasing tweaks make the entry worse against the real judge.

- Stop iterating when a new round moves the dev score by less than the noise between your own variants, or when quota or time leaves no room for a further scored round.

- Never attack the judge, because prompt injection, ASCII smuggling, or system-prompt leakage against the make.fun judge is cheating and risks disqualification.

- Validate any local judge against the house ladder first, because a self-judge that cannot reproduce the published rung order is uncalibrated and its picks are noise.

## What is verified and what is not

- Our own builds verified the poem v1 failure and v2 jump, the token-radar v2 jump, the image lessons P-17, P-18, and P-19, the bytes tie-break, and the final-entry pick mechanism.

- Sourced from published judge literature but not yet measured on make.fun judges: position bias, verbosity and length confounds, and the 73 percent annotator agreement ceiling.

- Sourced from the make.fun kit itself: the first-difference-decisive rubric reading, the house ladder strengths, and the judge mechanics in competition.yaml.

- Find the full sourced versus untested split in [references/judge-biases.md](references/judge-biases.md).

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
