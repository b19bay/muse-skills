# Evidence and traceability

## Verified on our own data

- The locked champion v5-k2-o140 scored 0.262796 on the 6 NVIDIA practice cases, against a house baseline of 0.363589 and a first public submission reference of 0.279.

- Median error was identical at 0.767503 across all 150 NVIDIA variants, because every variant changed only the width.

- The top 10 NVIDIA variants sat inside a 0.0035 band, and the winner was picked on robustness rather than the last 0.0002.

- Case p00 scored 0.459 and carried 29 percent of the total loss, and it was never diagnosed.

- The FAA morning validation overturned the night pick, with floor 0.0008 beating floor 0.0015 on all 7 fresh pseudo cases, 0.117516 against 0.125938.

- Our FAA and NVIDIA entries are the same program, with identical loss, median error, and coverage to 6 decimals.

- The btc-cent research tested ridge, LAD regression, mean reversion, EMA pulls, median denoising, hour of day drift, and in window drift on out of sample checkpoints, and everything either lost to persistence or tied it.

- The FAA-02 kit rules state twice that a practice score is no guide to the final, and silver-fox-78 first submission scored 0.256 before the memorized practice submission scored 0.00236.

## Literature results, not yet tested on our data

- 86 percent of Metaculus Fall 2025 winners ensemble or aggregate across multiple forecasts.

- Platt scaling improved Brier by 0.016 on binary questions and 0.005 on multiple choice, with p below 0.001, and Phan et al measured 0.0999 to 0.0934.

- Capping predictions is the strongest within winners differentiator at r plus 0.48 with p 0.005, while extremizing hurts at r minus 0.30.

- The M5 uncertainty winner trained a separate quantile regressor per quantile level, and both M5 winners carved out a real validation window.

- Kaggle Grandmaster doctrine holds that a change must move both cross validation and the public leaderboard, and a widening gap between the two is the number one overfitting red flag.

- A working forecaster asks three times on numeric questions and averages the quantiles, and records how much the series actually moved over windows of the same length as the forecast horizon.

## Source map

- The champion method section traces to `~/workspace/makefun/poly-nvidia/SPEC.md` and `~/workspace/makefun/poly-nvidia/leaderboard.md`.

- The replica scorer section traces to `~/workspace/makefun/poly-nvidia/score.mjs` and its notes in `~/workspace/makefun/poly-nvidia/scorer-NOTES.md`.

- The variant sweep and noise band section traces to pattern P-14 in `~/workspace/makefun/pattern-bank.md`.

- The untried classes trace to playbook section 3.1 in `~/workspace/makefun/winning-playbook.md`, to section 3.2 of `~/workspace/makefun/rank-improvement-plan.md`, and to pattern P-34 in `~/workspace/makefun/pattern-bank.md`.

- The Metaculus, Platt, capping, and M-competition findings trace to section 4 of `~/workspace/makefun/research/web-research.md`.

- The FAA-02 practice mirage traces to section 6 of `~/workspace/makefun/research/platform-research.md`.

- The btc-cent point forecast findings trace to section 2.3 of `~/workspace/makefun/rank-improvement-plan.md`.
