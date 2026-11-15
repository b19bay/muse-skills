# The replica scorer workflow

## Why build a scorer

- The kit grades the entry on practice data on your own machine the way the server grades it, so a local replica scorer is the verifier for every model decision.

- Score every variant with the same scorer and the same answers, or the variant scores are not comparable.

- The working NVIDIA scorer lives at `~/workspace/makefun/poly-nvidia/score.mjs`, and it is the template for a new competition scorer.

## What the scorer must reproduce

- Score pinball per item as 100 times the maximum of tau times y minus q and tau minus 1 times y minus q, with y and q as fractions in 0 to 1.

- Score loss as the mean over every case, market, minute, and quantile, reported to 6 decimals, with lower better.

- Score median error as the mean over every market minute of 100 times the absolute difference between y and the median.

- Score 90 percent coverage as the share of market minutes with q05 below or equal to y below or equal to q95.

- Score an invalid case as if every quantile were 0.5, and flag the case invalid in the output.

- Run one case per run with only that case input file in the input directory, enforce the 8 second per case cap, and enforce the 1,048,576 byte output limit.

- Validate the output shape strictly, with exactly one top level key named forecasts, exactly one row per market, 240 rows per market, 5 finite numbers in 0 to 1 per row, and non decreasing values within each row.

- Read the exact scoring rules from the competition kit rules file first, because the numbers above are the NVIDIA kit values and a new competition may differ.

## How to build it

- Fetch the answer grids from the public source the kit names, and store them beside the scorer so every run scores against the same answers.

- For NVIDIA the answers came from Polymarket price history fetched with the research scripts in `~/workspace/makefun/poly-nvidia/`, and the kit input files live in the kit input directory.

- Run the candidate in a fresh temporary input and output directory per case, pass the directories through MAKEFUN_INPUT_DIR and MAKEFUN_OUTPUT_DIR, and kill the run at the cap.

- Print per case loss, median error, and coverage, then the overall numbers, and compare against the expected house baseline numbers when all cases ran.

- Support scoring existing output files without re running the candidate, so a sweep can reuse outputs.

## How to validate the scorer

- Score the house baseline first and require the published numbers to 6 decimals.

- For NVIDIA the baseline is loss 0.363589, median error 0.767503, and coverage 0.949642.

- Score the locked champion next and require loss 0.262796 with per case losses matching SPEC.md section 9 within plus or minus 0.000002.

- Treat a scorer that cannot reproduce both numbers as uncalibrated, and treat its variant rankings as noise.

## How to use it in a sweep

- Score the champion baseline first and record it as the reference row.

- Change one parameter at a time, score the variant, and append one row per variant to the leaderboard file.

- Keep the per case columns, because a variant can win overall while losing badly on one case.

- Record median error and coverage on every row, because a loss gain bought with collapsed coverage is a robustness loss.

- Re run the top finalists on fresh pseudo cases before locking, using the same scorer code with different answer files.

- Re fetch fresh data near the deadline and re test the finalists, because a morning validation can overturn a night pick.

## The FAA morning validation example

- The FAA floor 0.0015 won on night pseudo data and lost on fresh morning data, so the entry flipped to floor 0.0008.

- Floor 0.0008 beat 0.0015 on all 7 fresh pseudo cases, 0.117516 against 0.125938, a gap of 0.008422 above the 0.002 noise bar.

- Treat a flip like this as the validation working, not as a failure, and record the numbers in the leaderboard file.
