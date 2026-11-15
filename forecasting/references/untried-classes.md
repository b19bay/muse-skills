# The untried classes

## Status

- Every class below is UNTESTED on our own data unless its status line says otherwise.

- The field converged on the same sigma and width sweep, and the top 350 NVIDIA entries sit inside a narrow band, so the differentiator is likely one of these classes.

- Test each class with a scored test on practice plus held out pseudo cases, and record the result either way, because a scored negative is as valuable as a scored win.

- Never present a literature result as a result on your own data.

## Per case diagnosis of the worst case

- This class is untested, since no per case regime diagnosis was ever done for NVIDIA or any later bounty.

- Rank the practice cases by loss and compute each case share of total loss.

- Inspect the worst case markets, checkpoints, and regimes, and check whether the loss comes from width, from the median, or from a regime the model cannot see.

- Build a targeted fix for that regime only, and score the fix on practice and on pseudo cases drawn from the same regime.

- Keep the fix only when it wins on both sets.

- For NVIDIA, case p00 scored 0.459 and carried 29 percent of the total loss, and fixing it to p01 level would cut the overall score by about 0.025, which is 7 times the entire top 10 spread of 0.0035.

- Ask the same question for every future forecasting bounty, namely which case or regime dominates the loss.

## Vary the median

- This class is untested on quantile models. Denoised anchors were tried for btc-cent point forecasts and lost, but never for the Polymarket quantile models.

- Replace the last price median with the median of the last N closes for N in 3, 5, 10, and 30, and score each on practice and pseudo cases.

- Try a short EMA anchor as well, and combine a denoised anchor with the champion width shape unchanged, so the median effect is isolated.

- Watch median error first, because it was identical at 0.767503 across all 150 NVIDIA variants, and a median change moves median error directly.

- Remember that median equal to last price is also the house baseline median, so beating the baseline on median error requires a genuinely better anchor.

## Quantile ensemble

- This class is untested. Window blends that average sigma were tried and lost, but averaging the final quantiles is a different operation.

- Pick 2 to 3 diverse models, for example w120 normal plus w360 Student-t plus pmix.

- Generate each model full quantile output, then average the final quantiles level by level.

- Score the average on practice and pseudo cases, and also try a trimmed mean and a median across models.

- Keep the member models diverse in window, distribution family, or mixture shape, because diversity drives ensemble gains more than individual accuracy.

- The evidence for this class is that 86 percent of Metaculus Fall 2025 winners ensemble or aggregate, and a working forecaster asks three times on numeric questions and averages the quantiles, which widens ranges where runs disagree.

## Platt recalibration plus capping

- This class is untested on our data and rests on literature results only.

- Fit a logistic recalibration, known as Platt scaling, on the pseudo case record, mapping raw forecast probabilities to calibrated ones, and apply it as a final stage.

- Cap extreme predictions at a floor and ceiling, starting from the existing sigma floor 0.0008 and cap 0.01 as the capping shape.

- Score with and without each step separately, so the gain is attributable to recalibration or to capping alone.

- Never push probabilities toward the extremes, because extremizing hurts.

- A Metaculus synthesis of 11 analyses found Platt scaling improved Brier by 0.016 on binary questions and 0.005 on multiple choice, with p below 0.001, and Phan et al measured 0.0999 to 0.0934.

- Capping is the strongest within winners differentiator at r plus 0.48 with p 0.005, while extremizing hurts at r minus 0.30.

## Scored sum-to-1

- This class is untested as a scored test. It was rejected on a minus 0.10 correlation and a design preference, never on a scored test.

- Run one scored pseudo case test before dismissing it again.

- Shrink each market median toward its sum constrained value by a factor in 0, 0.25, 0.5, and 1.0, and score each shrinkage level.

- Keep a level only when it wins on practice and pseudo cases.

- Test this because these are mutually exclusive outcome markets, so the prices should sum to about 1.

## Hazard based widening for dead markets

- This class is untested.

- Track each market no move streak length, and fit a streak dependent wake up hazard from history instead of a single shrinkage K.

- Widen the outer quantiles for long streak markets by a factor that grows with the streak.

- Score against the champion on practice and on pseudo cases that include dead market wake ups.

- Test this because the point mass mixture handles no move probability with one K, but a market with a long no move streak has a different wake up hazard than an active one.

## Per horizon calibration

- This class is untested as separate multipliers. Shape variants partially probed this and were neutral.

- Fit separate width multipliers for short horizons and long horizons, for example h up to 60 and h above 60.

- Calibrate each multiplier on held out data, and score against the single exponent 0.32 champion.

- Test this because one exponent for all horizons may misprice short horizons against long ones.

## Regime conditional models

- This class is untested. The exploration found a regime break and a weekend final difference, but the locked model is a single global model.

- Key the regime on trailing realised volatility, quiet versus active.

- Fit separate sigma and width parameters per regime, and switch at runtime on the trailing window realised vol.

- Score on practice and on pseudo cases drawn from both regimes, and require a win in both regimes or a clear overall win before keeping the split.

- A regime break was found at 2026-11-11T23:54Z when nine markets collapsed from 0.485 to 0.005 in one minute, and the final ran over a weekend while the practice pattern rested on about 1 day per hour.

## More untried ideas from the research

- Try per quantile models, with a separate calibrated model per quantile level instead of one sigma scaled to all quantiles, following the M5 uncertainty winner, which trained a separate quantile regressor per level.

- Try a same length window realised movement anchor for width, recording how much the series actually moved over windows of the same length as the forecast horizon, instead of deriving sigma only from trailing 120 minute RMS.

- For point forecast bounties, try a volatility adaptive pull that strengthens when the last price looks like noise, a jump conditional pull that pulls only when the last move looks like a jump, an ensemble of pulls at different spans, and a median anchor plus pull combined.

- Expect small gains from the point forecast ideas, because the btc-cent research found under 1 percent predictable edge on 4 hour ahead BTC from price history alone.
