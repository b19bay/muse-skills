# Square Post Preflight

## Count cashtags by mentions

- Count every cashtag occurrence in the whole draft before you present it for approval.

- Count a repeated cashtag again each time it appears, and count mentions of $BTC, $ETH and $USDT the same way.

- Keep the total at 3 mentions or fewer across all coins in the draft.

- Report the count as a total number of mentions, never as a number of distinct coins.

- Reduce the draft to 3 mentions or fewer before approval when the count is higher.

## Recompute every figure

- List every number in the draft and recheck each one against a live source in the same pass before approval.

- Recompute every derived percentage from the raw numbers yourself, using the current price against the all time high, the price 30 days ago and the price a year ago.

- Never copy a percentage from an earlier draft or from another coin draft, because a reused figure can be wrong for the new coin.

- Check the units on every large number, such as tokens against dollars and millions against billions, before you keep it.

- Read the Fear and Greed value once for the morning and use that one value in every post that day, so both accounts never print different values.

- Drop any figure you cannot verify from a live source, and hold the draft when a central figure cannot be verified.

## Hold a failing draft instead of publishing it

- Run this preflight before the draft goes for approval, so a fix still needs only a fresh approval.

- Hold a draft that fails the cashtag count or a figure check, and report the failing count or figure with the correct value.

- Never edit text the user already approved to fix a failure, because approval covers only the text the user saw.

- Send the corrected draft for fresh approval before anything is published.

## Available connectors

- [Binance Square](~/workspace/custom-connectors/custom.binance-square/CONNECTOR.md) for publishing text posts from one account.

- [Binance Square (akun 2 / b19)](~/workspace/custom-connectors/custom.binance-square-b19/CONNECTOR.md) for publishing text posts from a second account.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Draft the post around one coin and one comparison coin, so the cashtag count stays inside the limit without cutting content.

- Keep a short list of the live sources you rechecked, so the next draft for the same coin starts from verified numbers.
