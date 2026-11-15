# Verify Scheduled Delivery Before Claiming It

## Define what counts as delivered

- Treat delivery as complete only when an assistant message for that alert is visible in the chat transcript.

- Treat a state file update as a worker record only, never as proof that the user received the alert.

- Treat a daily log line as a worker record only, never as proof that the user received the alert.

- Treat a worker report that says sent as a claim to verify, never as proof by itself.

## Verify the claim against the transcript

- Re-read the chat transcript for the exact alert before you mark it delivered.

- Search the transcript for the alert content and the alert time, not only for a sent flag in state.

- Record the transcript message handle when you find the visible message.

- Record the alert as not delivered when no visible message matches the claim.

## Mark state only after verification

- Update the delivered timestamp only after the transcript check finds the visible message.

- Leave the delivered timestamp unset when the transcript check finds no message.

- Re-check the transcript again when a worker report and the transcript disagree.

- State the disagreement plainly in the next user visible report.

## Recover a missing delivery safely

- Send the missing alert once from the main conversation when the transcript shows no delivery and the alert still matters.

- Check the transcript again after that send before you mark the alert delivered.

- Do not send a second copy when the transcript already shows the alert.

- Keep the alert pending for the next run when the send does not appear in the transcript.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Keep one transcript message handle per alert in the worker state, so the next run verifies the handle instead of searching the whole transcript again.

- Ask the worker to return the transcript handle for each alert it claims to have sent, so the main conversation can check that handle directly.
