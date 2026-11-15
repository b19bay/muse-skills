# The NVIDIA champion method (v5-k2-o140)

## Status

- This method is verified on 6 practice cases with overall loss 0.262796, against a house baseline of 0.363589 and a first public submission reference of 0.279.

- It was locked on 2026-11-13 and submitted to polymarket-nvidia-ceo-forecast-01, then ported unchanged to polymarket-faa-attribution-02, where it scored identically to 6 decimals.

- The full behavioral specification lives in `~/workspace/makefun/poly-nvidia/SPEC.md`, and the variant leaderboard lives in `~/workspace/makefun/poly-nvidia/leaderboard.md`.

- The prototype in `~/workspace/makefun/poly-nvidia/models/v5-k2-o140/main.ts` is reference and verification only, and must never be copied into an entry.

## The model in one paragraph

- For each market independently, with no cross market information, the median forecast at every horizon is the last price, with no drift, no momentum, no mean reversion, and no smoothing.

- The 1 minute move scale sigma comes from the trailing 120 minutes of 1 minute price changes, and the per minute move probability lambda comes from the same window, shrunk slightly toward the 0.13 prior.

- At horizon h the forecast distribution of the price change is a two part mixture, with a point mass at exactly zero change and a normal part whose scale is inflated so the mixture total variance still equals the horizon scale squared.

- The checkpoint timestamp is not used by the forecast, because a time of day adjustment was tested and hurt.

## Constants

- Use a trailing window of 120 minutes for sigma and lambda.

- Use a horizon exponent of 0.32, so width grows as h to the 0.32.

- Floor sigma at 0.0008 and cap sigma at 0.01.

- Multiply the outer quantiles at levels 0.05 and 0.95 by 1.40, and multiply the inner quantiles at levels 0.25 and 0.75 by 1.00.

- Shrink the move rate toward the prior 0.13 with pseudo count strength K equal to 2.

- Cap the point mass probability at 0.95.

## Per market estimation

- Take the market prices in order and let the last price be the checkpoint price x.

- Let m be the smaller of 120 and the number of available 1 minute differences.

- Compute sigma raw as the root mean square of the m trailing differences, then clamp it into the 0.0008 to 0.01 range.

- Use the differences raw, with no winsorizing, no trimming, and no outlier removal, because large past moves carry real information about future width.

- Use a flat window with no recency weighting, because EWMA weighting was tested and hurt.

- If fewer than two prices exist, set sigma to the floor 0.0008 and lambda to the prior 0.13.

- Count the minutes with a nonzero price change and compute lambda as the count plus 2 times 0.13, divided by m plus 2.

- Prefer the 120 minute window because longer windows scored clearly worse and shorter windows scored worse too, and because the 120 minute window excludes the 2026-11-11T23:54Z regime break and the 0.485 new listing plateau from sigma and lambda in every case.

## Quantiles at horizon h

- Compute the horizon scale as sigma times h to the power 0.32.

- Compute the point mass probability as the smaller of 0.95 and one minus lambda to the power h.

- Compute the continuous part scale as the horizon scale divided by the square root of one minus the point mass.

- Set the mass boundaries lo to one minus the point mass divided by two, and hi to one plus the point mass divided by two.

- Set the median quantile to the last price exactly.

- For a level below lo, set the quantile to the last price plus the continuous scale times the inverse normal CDF of the level divided by one minus the point mass, times the level multiplier.

- For a level above hi, set the quantile to the last price plus the continuous scale times the inverse normal CDF of the level minus the point mass divided by one minus the point mass, times the level multiplier.

- For a level inside the point mass interval, set the quantile to the last price exactly.

- Use an inverse normal CDF accurate to at least 1e-7 absolute error, and read the Acklam rational approximation coefficients from SPEC.md section 5 when you implement it.

- Expect the intuition to hold in checks, since 86.7 percent of post break minutes have zero change, so most markets sit still most minutes and the point mass does the real work at short horizons.

## Rounding and clamping

- Clamp every quantile into 0 to 1 first.

- Round every quantile to 6 decimals next, writing negative zero as 0, never as minus 0.

- Enforce non decreasing order left to right last, replacing each value by the maximum of itself and the previous value.

## Edge cases

- For a market with one price only, use sigma 0.0008 and lambda 0.13 and forecast normally from that single price.

- For a market with short history, use all available differences with no padding and no fallback window.

- For a market at exactly 0 or exactly 1, keep the formulas unchanged and let clamping hold every quantile inside 0 to 1.

- For a market with all identical trailing prices, sigma takes the floor and lambda takes its minimum, so the forecast is narrow but nonzero.

- Add no special handling for the 0.485 listing plateau or the 2026-11-11T23:54Z collapse, because the 120 minute window already excludes both.

- Never crash the whole run for one bad market, because a crash invalidates the entire case.

## Expected scores

- The locked model scores overall loss 0.262796, median error 0.767503, and 90 percent coverage 0.908203 on the 6 practice cases.

- Per case losses are p00 0.459032, p01 0.308297, p02 0.331890, p03 0.232099, p04 0.197361, and p05 0.111572.

- The house baseline scores loss 0.363589, median error 0.767503, and coverage 0.949642.

- Median error equals the baseline exactly because both use last price medians, so all of the gain is in width and shape.

- Expect runtime of about 0.2 to 0.6 seconds per case and output of about 226 KB for a 24 market case.

- Pick the winner on robustness inside the noise band, as the locked K equal to 2 was picked over the nominal best K equal to 1 at 0.262559 because K equal to 2 has more shrinkage against dead market wake ups and slightly higher coverage at 0.908 against 0.901.

## What was tested and rejected

- Square root growth or an alpha outside 0.30 to 0.35 lost, and alpha 0.5 scored about 0.33 against the champion 0.263.

- Sigma windows of 60, 90, 180, 360, and 720 minutes all scored worse than 120 minutes.

- Window blends and EWMA weighted sigma scored worse.

- Winsorized sigma and MAD based sigma scored worse than plain RMS.

- Sigma floors and caps outside 0.0008 and 0.01 scored worse.

- Inner quantile narrowing with multipliers 0.6 or 0.8 scored worse.

- Asymmetric tails with downside wider than upside at 1.25 or 1.5 scored worse, and symmetric tails win despite the pooled data looking left skewed.

- Student-t quantiles, variance matched df 3, 5, and 8 or raw df 3, 5, and 8, were no better than normal plus the 1.40 outer multiplier.

- Any drift lost, including constant drift, momentum drift with positive or negative damping, and mean reversion drift.

- Jump triggered sigma widening lost, with or without horizon decay.

- Time of day sigma multipliers lost, shrunk or raw, and the pattern rested on about 1 day per hour with a weekend final.

- A separate larger horizon exponent for the outer quantiles only, 0.40 to 0.50, was no better than the flat 1.40 outer multiplier.

- Horizon shape factors narrowing short horizon quantiles gave no gain on top of the point mass mixture.

- Sum-to-1 normalisation was never implemented and never scored, so it is untested rather than rejected, and it belongs in [untried-classes.md](untried-classes.md).

## Portability warning

- A ported champion still needs its own out of sample check on the new competition data.

- The FAA port kept the NVIDIA parameters, but the floor parameter did not transfer cleanly, since floor 0.0015 looked better on FAA pseudo data at night and lost clearly on the morning validation, so the final entry kept 0.0008.

## The Roblox sibling engine

- Roblox uses a different engine in the same family, namely Monte Carlo in latent score space with score equal to negative rank to the one third power, 5,000 seeded simulations, time averaged over the window.

- Its lessons transfer as warnings, since raw velocity is mostly noise with a momentum slope of 0.05, top places are stickier with a persistence blend decaying by place, and tripling the entrant rate flattens an overconfident distribution.
