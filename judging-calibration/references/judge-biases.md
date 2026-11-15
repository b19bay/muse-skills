# Pairwise judge biases: sourced versus untested

This file separates what the research sources from what is still unmeasured on make.fun judges. It traces to research/web-research.md sections 3.1, 3.2, and 3.3, winning-playbook.md sections 3.2 and 6, and pattern-bank.md P-33.

## Sourced from published judge literature, not yet measured on make.fun

### Position bias

- Judges systematically favour the response shown first, and it is the number one judge failure mode in the literature.

- Run every local comparison twice with the order swapped, accept a win only when both orders agree, and treat disagreement as a tie.

- This bias is sourced from web-research.md section 3.1, and it is not yet measured on make.fun judges, so apply the swap defense to local self-judge comparisons only and never assume the platform judge has the same bias.

### Verbosity and length confounds

- Longer, list-formatted, and hedging-rich answers win more often than their usefulness warrants, and a naive judge learns length as a feature.

- This confound is sourced from web-research.md section 3.1, and it is not yet measured on make.fun judges.

- The counter-pressure on make.fun runs the other way, because the bytes tie-break rewards smaller artifacts, so length padding is doubly bad here: it costs the tie-break and may not even buy judge favour.

### The 73 percent ceiling

- InstructGPT labelers agreed with each other about 73 percent of the time, so about a quarter of comparisons flip with the annotator.

- This ceiling is sourced from web-research.md section 3.1, and it implies judge variance is structural rather than a bug to fix.

- Rank ranges span hundreds of places as a consequence, so never over-read a single dev score and never rebuild an entry on one narrow loss.

## Sourced from the make.fun kit itself

### First-difference-decisive

- The poem judge prompt reads criteria in order, and the first difference decides unless a later one differs by much more.

- This reading is verified in the agency-poem kit, per rank-improvement-plan.md section 2.1.

- Fix criterion 1 and criterion 2 failures before polishing criterion 4 and criterion 5, because an early-criterion loss decides the game before the later criteria matter.

### House ladder strengths

- Competition.yaml publishes Bradley-Terry strengths for the house ladder rungs, such as the poem rungs at 2.703, 2.442, and 1.694, and the food-picture rungs at 6.42, 4.99, and 3.11.

- These strengths are verified against the kits we have read.

### Pairwise mechanics

- The score is in millionths, games run in Swiss rounds against anchors, and undefeated is the price of the top cluster.

- These mechanics are verified from leaderboard data, with every top-10 poem entry at 15-0, every top-10 token-radar entry at 20-0, and the top 3 FPS entries at 12-0.

### Bytes tie-break

- Ties break on bytes with lower better in all judged competitions.

- This rule is verified in all three judged leaderboard files, with agency-poem ranks 1 to 3 an exact tie at 937,047 broken by 888, 975, and 985 bytes.

## The Goodhart inverted-U

- Gao et al., arXiv 2210.10760, show proxy reward grows monotonically under optimization while true reward first rises and then falls, and the gap between the curves is Goodhart law quantified.

- This finding is sourced from web-research.md section 3.2, and it is consistent with our own observation that calibration buys the top 10 percent while the rest is part quality and part luck.

- Optimize for the rubric stated criteria, not for judge-bias exploits, because past the sweet spot more judge-pleasing tweaks make entries worse against the real judge.

- The recurring hacking gallery from the literature is ever-longer answers, list-and-bold formatting regardless of content, sycophantic agreement, hedging boilerplate, and confident fabrication when the judge cannot check facts.

- Cap self-judge iteration rounds, and stop when a new round moves the dev score by less than the noise between your own variants.

## Calibrating a local judge

- A judge is trustworthy only where it has been compared with labels on the same rubric.

- Make.fun already gives us the calibration set, which is the house ladder rungs with published Bradley-Terry strengths in competition.yaml.

- Validate a local judge against those rungs before trusting its picks, because a self-judge that cannot reproduce the published rung order is uncalibrated and its picks are noise.

- Local comparisons must be pairwise, swap-consistent, and rubric-anchored, with both verdicts recorded and disagreement treated as a tie.

## The hard line

- Never attack the judge, because prompt injection, ASCII smuggling, or system-prompt leakage against the make.fun judge is cheating and risks disqualification.

- Reading the published judge prompt is legitimate and is the documented P-16 move.

- Attack skills such as pentest-web, serangan-agen, and hunt-llm-ai do not apply to the judge, and using them against it would be cheating.
