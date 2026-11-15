# Performance Profiling for Agent-Server Entries

Use this skill when a make.fun agent-server entry loses on speed and you need to find where the time goes, prove a rebuild is faster, and know when to stop. It is built from the github-core-clone-01 v2 perf rebuild, the only perf rebuild in our records with measured before and after numbers. Read the case study in [references/github-core-v2-case.md](references/github-core-v2-case.md) for the full numbers and the procedure in [references/profiling-procedure.md](references/profiling-procedure.md) for the bench checklist.

## Attribute the gap before you optimize

- Split the total score into its parts before you touch any code, and attribute the whole gap arithmetically.

- Read the perf formula from the kit before you estimate anything, since the formula decides what a speedup is worth.

- Work the github-core arithmetic as your model: v1 scored feature 600 and agent 200, both tied with rank 1, and perf 98 against rank 1's 153.

- Compare p50 the same way: v1 ran 828,243 microseconds against rank 1's 387,494, which is 2.14x slower.

- Convert the slowdown into points with the log formula: log2 of 2.14 is about 1.10, so 12.5 times 1.10 is about 13.7 points per workload, and times 4 workloads is about 55 points.

- Treat the result as the whole diagnosis when the arithmetic closes exactly: the entire 55-point gap was perf, and no feature work could close any of it.

- Compare against the top-10 band, not just rank 1: every top-10 entry maxed feature and agent, with perf from 147 to 153 and p50 from 387,000 to 421,000 microseconds.

- Break the perf gap down per workload before you choose what to fix: v1's clone workload scored 14 to 19 points and ran slower than the reference, while push, read, and write each scored 26 to 29.

- Check the final-stage gate before you decide how much perf matters: only the top 60 on the qualifying trial reach the 3-instance final, and a prize needs a score strictly above the reference forge.

## Measure CPU time, not wall time

- Treat grade-local wall time as unreadable on this VM: v1's own grade-local perf fell from 96 to 104 on a quiet VM to 20 under throttle, with no code change at all.

- Compare versions by CPU time and per-request counts, never by wall time, since CPU time is throttle-invariant on a shared-CPU VM.

- Run A/B comparisons in one process with alternating passes: the proven driver runs client and server in one process over raw node http keep-alive, alternates the two versions, and repeats 3 passes.

- Keep every A/B on the same machine under the same conditions, and repeat it across multiple passes before you believe it.

- Report the per-pass winner, not just the mean: v2 read CPU won all 3 passes at 0.468 against v1's 0.537 milliseconds per request, about 13 percent faster.

- Call a tie a tie: write CPU measured 0.619 against 0.603 milliseconds per request, which is no difference, and a win that does not repeat across passes is noise.

- Verify identical response bodies before you believe a CPU comparison: both versions returned identical 304-byte bodies in the read A/B, so the faster version did the same work.

## Keep every bench honest

- Assert the HTTP status code before you time anything: the v2 author's bench2 and bench3 measured 401 error responses because the bench sent a different Bearer token than the one passed to createApp, with no status checks anywhere.

- Treat any timing from an unchecked bench as meaningless: the author's 401 timings looked like real measurements until the coordinator re-measured with status assertions.

- Build auth headers dynamically at runtime, never as literals: a literal Bearer token written in a tool call gets redacted before execution, so the executed string differs from the one you wrote.

- Never write a literal Bearer token in a tool call, a heredoc, or an edit: concatenate the scheme and the token value at runtime instead.

- Have the coordinator re-measure independently: the 401 bench was caught only by the coordinator's own status-checked re-measurement, never by the author.

- Record the bench conditions with the numbers: which machine, which kit, how many passes, and what the status assertions were.

- Run the full checklist in [references/profiling-procedure.md](references/profiling-procedure.md) before you trust any bench result.

## Profile the hot paths before you rewrite

- Profile the current version before you design the rebuild: v1 profiling found the two hot paths that set the whole v2 scope.

- Use an instrumented copy with a same-process driver: function CPU time is exact in one process, while wall time is inflated by the shared-CPU throttle.

- Rank hot paths by total CPU, not by single-call cost: parsePack averaged 7.8 to 12.1 milliseconds across 206 calls and dominated, while planFetch averaged 2.8 to 4.4 milliseconds across 55 calls.

- Name the root cause of each hot path in mechanism terms: parsePack paid about 16 inflateSync calls per entry, most throwing exceptions, to find each zlib stream end by probe and binary search.

- Trace the second hot path the same way: planFetch walked the full 200-commit history 3 or more times per depth-1 clone and re-parsed every commit on each walk.

- Measure the floor before you promise a gain: REST handlers already cost 4 to 7 microseconds each, so read and write wall time is dominated by client, transport, and HTTP-stack overhead that no server change removes.

- Guard every perf rebuild with a conformance suite: v2 kept 120 of 120 checks, feature 600, and agent 200 while changing the hot paths, and a perf gain that regresses conformance is a loss.

- Pair the rebuild with the regression suite in [Property-Based Testing](~/workspace/custom-skills/property-based-testing/SKILL.md) so the new version must reproduce the old version's responses byte-identically on the recorded workload.

## Apply the proven techniques

- Parse packs with an Adler scan instead of probing for stream ends: zlib inflateSync tolerates trailing bytes, so one inflate on the remainder yields the entry bytes, and the stream end is found by scanning for the 4-byte Adler-32 checksum that ends a zlib stream, confirmed by one more inflate on the sliced range.

- Count the win in inflates: at most 2 inflates per entry and zero throws on the success path, against about 16 mostly-throwing inflates before, and pack parse fell from 7.8 to 12.1 milliseconds to 0.175 milliseconds.

- Bound fetch planning by depth: never visit a commit at a distance equal to or greater than the requested depth, skip the ancestor set entirely when there are no haves, order only the included commits, and compute shallow boundaries over included commits only.

- Count that win too: depth-1 plan fell from 2.8 to 4.4 milliseconds to 0.021 milliseconds, and plan plus build together measured 0.263 milliseconds.

- Cache at every layer, each with an invalidation rule: a pack cache keyed by repo, wants, haves, deepen, shallow, and include-tag, capped at 8 entries and version-invalidated on mutation.

- Cache the advertisement per repo, service, and refs version, and treat the v2 advertisement as a startup constant.

- Cache responses for idempotent single-object GETs on the record itself, and clear them on mutation in the same code path that mutates.

- Cache parsed commits and parsed trees as immutable objects that never invalidate.

- Keep the request path lean: one URL parse by manual split, no slice copies, synchronous GET handlers, and a single-chunk readBody fast path.

- Keep state in memory in Maps and look up by index: never scan a repo per request, never walk full history for a depth-1 fetch, and emit plain objects only in packs with no deltas.

- Never log per request, never parse or stringify anything large inside a handler, and never await a timer inside a handler, since each of these stalls the single-threaded server.

- Build the clone pack from the tip commit directly: the clone workload is 50 concurrent depth-1 clones, so a pack built from the tip with no history walk is the whole workload.

- Check what caching already exists before you add more: v1 already carried pack, advertisement, branch, parsed-object, and JSON caches, so the remaining work was in the timed workload paths, not in adding another cache layer.

## Know when to stop

- Stop when the remaining gains are bounded by overhead you cannot remove: v2 was estimated at perf 120 to 130, up from 98, with the top-10 band at 147 and above likely out of reach because REST workloads are bounded by client and HTTP-stack overhead.

- Treat that estimate as an estimate, not a measurement: it was projected from CPU A/B numbers, and the real figure comes only from the production grade.

- Stop local iteration when local measurement cannot distinguish versions: decide a v3 from the production per-workload breakdown after the entry grades, not from more throttled local runs.

- Submit a strict improvement instead of chasing the band: v2 was submitted as a strict improvement with zero correctness risk even though the top-10 band was likely out of reach, with rank expected to improve from around 2295 toward roughly 1000 to 1500.

- Stop optimizing a workload whose handler CPU is already a small fraction of its total: when handlers cost microseconds and the wall time is transport, further handler work buys nothing.

- Never trade correctness for speed: every cache needs an invalidation rule, and the conformance suite must stay green.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Read the live top-10 titles before designing a rebuild, since winners advertise their techniques in titles and the study names the techniques to match.

- When local measurement cannot separate two versions, submit the strict improvement and read the production per-workload breakdown to plan the next version.
