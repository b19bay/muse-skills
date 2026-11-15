# Variant design template

Use this template to plan the 2 to 3 variants in a P-33 calibration loop. Copy the fields below into your working notes and fill them in before any author session starts. It traces to winning-playbook.md section 3.2 and pattern-bank.md P-33.

## Fields to fill in before building

- Competition slug and close time, plus the quota you recorded from `GET /api/competitions/<slug>/quota`.

- Rubric criteria in their published order, copied from competition.yaml.

- House ladder rungs with their published strengths, in one line each.

- Summarize the top-10 meta in two or three sentences, covering what the winners share, what they do that we do not, and which premises or approaches are already taken.

- For each variant, record its premise, its structure, what it tests that the other variants do not, and what it holds constant.

- Write down how you will choose between variants before the dev scores land, and what you will do if the dev scores disagree with the local pick.

- Keep a dev score record with one line per variant, giving its submission id, dev judge score, win-loss-draw record, and 90 percent interval.

- Record the final pick by submission id, and verify that `final_pick` names it.

## What to vary and what to hold constant

- Vary the premise, the structure, or the approach, because those are the choices the judge can actually reward differently.

- Hold the format, the length band, and the quality bar constant, so the dev scores compare like with like and a win traces to the variant design.

- Give every author the same rubric mapping and the same top-10 notes, so differences in score trace to the variant design and not to different instructions.

- Make each variant a genuine alternative rather than a tweak, because variants that differ only in polish teach you nothing about which direction the judge prefers.

- Never vary by copying a top-10 entry or a house rung more closely, because the final scans for copies and a near copy takes no prize.

## Variant ideas by type

- For a poem, draft 3 poems from 3 distinct concrete premises, each built around a different scene, object, or moment, then score each against the 5 rubric criteria in order and ship the winner. This is the director plan from the video-gambar skill.

- For an image entry, generate 6 to 8 candidates across different subjects and compositions, run the P-17 shootout in image-lessons.md, and submit the top 2 to 3 as separate variants when quota allows.

- For a dashboard, vary the model shape between variants, for example the peer pooling rule or the growth factor, and vary the screenshot composition, for example whether the detail view carries a sensitivity grid and stat boxes. Token-radar v2 beat number one on every backtest metric but lacked exactly those two detail-view elements.

- For an FPS or game entry, vary which systems the judged screenshots demonstrate, because the gap between our entry and number one was screenshot direction, not mechanics. Every judged screenshot must demonstrate a different system.

## Session rules per variant

- Each variant gets its own fresh author session and its own bundle, because thinking_reproduces is FIRST-WINS line classification and a re-apply session that diffs first scores near zero authored lines.

- The coordinator writes one SPEC per variant from the shared rubric mapping, and the author of a variant never reads another variant code or entry code.

- Submit all variants early so every dev score lands in time to inform the final pick.
