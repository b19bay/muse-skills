# Forecasting for make.fun Bounties

## Build the champion and its scorer

- Start every Polymarket style quantile bounty from the proven NVIDIA champion v5-k2-o140 instead of designing a model from scratch.

- Set the median to the last price at every horizon and estimate sigma per market as the root mean square of trailing 120 minute one minute changes, floored at 0.0008 and capped at 0.01.

- Grow width as h to the 0.32, never as the square root of h, and widen only the outer quantiles by 1.40 while the inner quantiles stay at 1.00.

- Model the no move probability as a point mass with a per market move rate shrunk toward the 0.13 prior with strength K equal to 2, capped at 0.95, and inflate the continuous normal part by one over the square root of one minus the point mass.

- Read the full formulas, constants, edge cases, and rejected list in [references/champion-method.md](references/champion-method.md) before you write a SPEC.

- Build a local replica scorer before you model anything, and score every variant with it instead of trusting the kit check alone.

- Reproduce the kit scoring exactly from the kit rules, including the pinball formula, the invalid case rule, the 8 second per case cap, and the 1,048,576 byte output limit.

- Validate the scorer against the house baseline first, and only trust it when it reproduces the published baseline numbers to 6 decimals.

- Read the scorer workflow in [references/replica-scorer.md](references/replica-scorer.md).

## Sweep variants and diagnose the worst case

- Sweep one parameter at a time from the champion baseline and record every variant in a leaderboard file with per case scores, median error, coverage, and runtime.

- Treat differences inside the noise band as ties and pick the winner on robustness, not on the last 0.0002.

- Use the NVIDIA noise band of 0.0035 as a starting point and measure your own band from the spread of near identical variants on your practice set.

- Diagnose the worst case before you touch any global parameter, because one bad case can dominate the whole loss.

- For NVIDIA, case p00 scored 0.459 and carried 29 percent of the total loss, and fixing it to p01 level would cut the overall score by about 0.025, which is 7 times the entire top 10 spread of 0.0035.

- Ask which regime the worst case represents, and check whether a targeted fix for that regime beats every global tweak.

- Record every rejected idea with its score so it is never retried, and check the rejected list in [references/champion-method.md](references/champion-method.md) before you test an idea that already lost.

## Test the untried classes

- Work through the untried classes in [references/untried-classes.md](references/untried-classes.md) before you lock a champion, because the field has converged on the same sigma and width sweep and the differentiator is one of these classes.

- Vary the median first, since it was an untested axiom in all 150 NVIDIA variants and the median error was identical at 0.767503 across every one of them.

- Test a quantile ensemble next, because averaging final quantiles across 2 to 3 diverse models is a different operation from blending sigma, and 86 percent of Metaculus Fall 2025 winners ensemble or aggregate.

- Label every untried class as untested until a scored test says otherwise, and never present a literature result as a result on your own data.

## Validate out of sample and lock the champion

- Build validation before the model, and require every change to improve both the practice score and a held out score before you keep it.

- Build pseudo cases from fresh real history that the model never saw, and score the finalists on them exactly as the replica scorer scores practice cases.

- Split validation by time, fitting on earlier data and scoring on a later window, and run a blind test where the scoring data stays hidden until the model is frozen.

- Re fetch fresh data near the deadline and re test the finalists, because a morning validation can overturn a night pick.

- Treat a widening gap between practice score and held out score as an overfitting warning and stop tuning when it appears.

- Never chase a practice score, because practice is no guide to the final.

- The FAA-02 kit rules state twice that a practice score is no guide to the final, since practice is cut from the NVIDIA event markets while the final runs on 4 fresh FAA markets over the 48 hours after close.

- Never build a program that detects practice cases and returns memorized answers, because memorized answers cannot transfer to fresh markets and the technique buys nothing for the final.

### Pre-build checklist

- Run the top 10 study for the competition and record what the leaders do differently before you write the SPEC.

- Confirm the replica scorer reproduces the house baseline to 6 decimals.

- Confirm the champion beats the house baseline on practice and on held out pseudo cases.

- Confirm the worst case is diagnosed and the median has been varied at least once.

- Confirm at least one ensemble test and one recalibration test ran with recorded scores.

- Confirm the finalist list is re validated on fresh data near the deadline.

- Confirm determinism with two byte identical runs and runtime under the per case cap.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Websites

- [Metaculus overview of AI forecasting research](https://www.metaculus.com/notebooks/43363/overview-of-ai-forecasting-research/) for the synthesis of 11 analyses behind the ensemble, Platt, and capping findings. Carry the headline numbers into the browser task and verify them against the notebook before you cite them.

- [AI forecasting in 2026, what 11 analyses say](https://fm-prod.effectivealtruism.org/posts/Spyz3wESZu2eeqhDj/ai-forecasting-in-2026-what-11-analyses-say) for the same synthesis in article form.

- [forecast-scaffold Fall 2026 prep review](https://github.com/edisonymy/forecast-scaffold/blob/HEAD/docs/review-2026-09-03-fall-season-prep.md) for a working forecaster ranked change list, including averaging quantiles across repeated runs and a Platt calibration gate.

- [M-competition forecasting learnings](https://github.com/nicholas-tobias-00/comp0191-dissertation/blob/HEAD/FORECASTING_LEARNINGS.md) for per quantile models and validation window discipline from the M4 and M5 winners.
