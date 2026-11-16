# Make.fun Recorder Choreography

## Launch the recorder in the right place

- Launch each recorder with `muse.exec` from a subagent chat and never from a cron run.

- End the launching turn after the recorder starts and let the runtime deliver its result instead of waiting inside the turn.

- Start the recorder with setsid and a detached standard input so the process survives the end of the launching turn.

- Verify that the recorder process id equals its session id before you treat it as detached.

- Keep recorder artifacts in the workspace and never rely on /tmp across a reboot.

## Sequence the author after the recorder

- Sleep about 300 seconds before the record command so the parent turn finishes first.

- Spawn the author with `subagent.spawn` only after the recorder is running so no parent message lands inside the recording window.

- Record one entry at a time and never run two builds in parallel against the same seal.

- Give each author a fresh session that writes from the behavioral spec alone.

- Run authoring with `subagent.spawn` and never in a cron run with a short turn budget.

## Keep background work alive across turns

- Expect a background exec waiter to die when the turn ends and plan the next step through a follow up parent message or a one shot cron run.

- Recheck recorder liveness after any host reboot before you bundle or submit.

- Read recordings.json with `muse.read` and treat a recording with no receipt there as unsealed even when chunks uploaded.

- Grep a session for claim codes and API keys before you bundle it.

## Free a slot and confirm the seal

- Count open recordings before you start a new one and keep the total at eight or fewer per account.

- Free a slot only by finishing a recording that is certainly unused with `record --finish <id>` from inside the kit folder.

- Confirm the seal by its receipt in recordings.json and by the server leaves before you hand the bundle back.

- Report the bundle path and its sha256 in the handoff and never print a claim code or key.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Build the entry first and record a clean re authoring pass when a seal is already poisoned instead of repairing the poisoned session.

- Keep a written recorder checklist in the build brief so the coordinator reads the choreography before the first launch.
