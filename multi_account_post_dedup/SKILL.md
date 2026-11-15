# Multi-Account Posting Deduplication

## Keep one shared post log

- Record every successful post in one log shared by all accounts, with the account, the posting time, the normalized topics and cashtags, and the post id or link when the platform returns one.

- Log a post accepted without an id as posted, and never retry it, because a retry creates a duplicate on the same account.

- Read the log before you choose a topic, not after you publish, so a duplicate is caught while it is still avoidable.

- Update the log immediately after each successful post, in the routine state location that all posting routines can read.

## Check sibling accounts before posting

- Compare the candidate topic and cashtags against the recent posts of every other account the user owns, not only against the posting account's own history.

- Check at least the same calendar day and at least the three most recent posts from each sibling account, whichever set is larger.

- Normalize topics and cashtags before comparing, by lowercasing them and stripping surrounding punctuation, so a case change does not hide a match.

- Treat a match on the same topic or cashtag as a duplicate even when the surrounding wording differs, because readers see the same subject from both accounts.

## Hold a duplicate instead of rewriting it

- Skip the duplicate post and report the sibling post it matches, with the sibling account, the time, and the topic.

- Do not rewrite, translate, shorten, or add hashtags to approved text to dodge a match, because approval covers only the text the user saw.

- Pick a different approved topic when the routine has one, and otherwise hold the post for a fresh user decision.

- Report the check result for every post, naming the sibling accounts checked and whether a match was found.

## Available connectors

- [Binance Square](~/workspace/custom-connectors/custom.binance-square/CONNECTOR.md) for publishing text posts from one account.

- [Binance Square (akun 2 / b19)](~/workspace/custom-connectors/custom.binance-square-b19/CONNECTOR.md) for publishing text posts from a second account.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Assign each account its own topic queue for the day, so a routine never needs to choose between two accounts on the same subject.

- Space sibling posts on the same subject across different days when both accounts must cover it, and record the planned day in the shared log.

- Ask the user for a topic list once per day and split it across accounts before any routine runs, so duplicates are prevented at planning time rather than at posting time.
