# Contested Seat Watcher

## Prove the whole path before going unattended

- Run the full path once before leaving a watcher alone, from login and token refresh through seat capture, submission, and execution, and record that the proof succeeded.

- Confirm that every credential and session expiry covers the full watching window plus the execution window, and do not start an attempt that could win after its session ends.

- Reverify the session after any new pairing or connection for the same account, because a new connection can displace the session the watcher relies on.

- Treat a simulated result as a prediction only, and report a final number only from the receipt or the on-chain record after execution.

## Classify each failure before retrying

- Read the exact failure class before choosing a retry, and keep timeouts and temporary server errors apart from a blocked endpoint and a seat that is already taken.

- Retry a timeout or a temporary server error a bounded number of times inside one run, with pauses between tries, and return to watching when the answer is still not definite.

- Stop hammering an endpoint that returns a block while other endpoints still succeed, because repeated attempts can harden the block and cost the next seat.

- Switch route or pause after a persistent block, and let the block subside before attacking the same endpoint again.

- Submit each attempt only once, and recheck availability before starting a new attempt after a loss, a failure, or an expiry.

## Keep the session and the state alive

- Write a timestamped log for every check, and keep a supervisor that restarts the watcher when its log goes stale for more than twice the check interval.

- Add a scheduled job as recovery after a restart, so a watcher that dies with its host returns without a manual restart.

- Refresh an expired token and continue, rather than aborting on expiry, and treat a stale saved finding as unproven until a fresh check confirms it.

- Verify that the watcher, its supervisor, and its scheduled job have all stopped after a cancellation, and say so only after that verification.

- Run one account at a time when accounts compete for the same seat pool, unless the user has ordered parallel hunting, so the accounts do not hammer the same endpoint or compete with each other.

## Act inside the window and report only what matters

- Check the execution gates again at the moment of action, including value, destination, a clean preview, and a gas total within the agreed cap, and stop for confirmation when any gate fails.

- Treat a quoted gas price as an estimate only, and keep a margin above it, because execution can settle above the quote.

- Act immediately only under an agreed immediate execution rule when all gates pass and the window is short, and do not insert a confirmation step that the window cannot survive.

- Notify only on attempt entry, on a win, on execution, or on a step that only the user can take, and keep no-change checks out of the main conversation unless the user asked for periodic reports.

- Never display or paste a session token into a browser console or a chat message, and never ask the user to do so.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Wait for the next seat after a loss instead of resubmitting the same attempt, because a new seat needs a new attempt.

- Use the official in-browser route when the outside route is blocked, and keep the browser session open for that route only.

- Lower the check cadence when a block appears, rather than raising it, because a slower check can outlast a block that fast polling creates.
