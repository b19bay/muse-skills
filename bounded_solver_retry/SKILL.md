# Bounded Solver Retry

## Measure feasibility before the next attempt

- Measure the solver on a board of the same size and difficulty before you spend a live window on it.

- Compare that measured time with the full live window, including login, fetch, and submission time.

- Record the board size, the difficulty tier, the window length, the solver used, and the time it took for every attempt.

- Treat an estimate as unproven until a fresh check from the service confirms the cooldown and the next eligibility time.

- Check whether difficulty rises as supply falls, and report that trend instead of assuming the next draw will be easier.

## Cap identical retries and escalate

- Stop automatic rescheduling after three consecutive failures in the same mode.

- Ask the user whether to continue, change method, or stop, and present the failure count, the measured times, and the difficulty trend with that question.

- Wait for that decision before you schedule another attempt in the same mode.

- Change at least one material factor before a further attempt, such as a faster solver, more compute, a parallel search, or a different solving strategy.

- Do not consume a cooldown window on an unchanged method after the cap, because each wasted window also loses supply to other solvers.

## Schedule only a changed attempt

- Verify that the changed method has a benchmark that fits inside the live window before you schedule it.

- Verify that login, session, and token expiry cover the full attempt window before you start.

- Schedule the next attempt only after the verified cooldown ends, not after an estimated cooldown.

- Report the result as solved or unsolved with the board size, the tier, the time used, and the remaining supply, and do not report a predicted result as a final result.

- Retire the method for this task when the changed method also fails inside its window, and ask the user for a new direction instead of looping again.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Run solvers in parallel on separate boards when the task allows parallel work and the service allows it.

- Split a large board only when the service accepts partial boards, and otherwise treat the whole board as one unit.

- Ask for stronger compute or a different solver early, when the benchmark shows the current setup cannot fit the window.
