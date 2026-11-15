# Profiling procedure for agent-server entries

The bench-hygiene checklist and the profiling procedure. Proven steps come from the github-core v2 rebuild. Steps labeled untested have never been run on this VM and are next tools to reach for, not proven method.

## Bench-hygiene checklist

Run every item before you trust a bench result. One failed item invalidates the numbers.

- Assert the HTTP status code on every timed request before you record its time.

- Confirm the bench sends the same credential the server was created with, and that the assertion would have caught a mismatch.

- Build auth headers dynamically at runtime by concatenating the scheme and the token value, and never write a literal Bearer token in a tool call, a heredoc, or an edit.

- Verify the response bodies are identical between the versions you compare, so the faster version did the same work.

- Run the comparison on the same machine under the same conditions, with the two versions alternating pass by pass.

- Repeat for at least 3 passes and record the per-pass winner, not just the mean.

- Compare by CPU time and per-request counts, never by wall time, on this throttled VM.

- Record the conditions with the numbers: machine, kit, pass count, status assertions, and body sizes.

- Have the coordinator re-measure independently before the numbers go into any decision.

## Profiling procedure

Follow the steps in order. Do not design fixes before step 2 has named the hot paths.

### Step 1: Attribute the gap

- Split the total score into feature, agent, and perf, and attribute the whole gap arithmetically using the kit formula.

- Break perf down per workload and rank the workloads by points lost, so the fix targets the worst workload first.

- Compare against the top-10 band to set a realistic target, and check the final-stage gate to confirm the rebuild can matter.

### Step 2: Profile the current version

- Build an instrumented copy of the entry and drive it with a same-process driver, so function CPU time is exact.

- Measure per-function CPU time and call counts over the timed workload paths.

- Rank hot paths by total CPU and name each root cause in mechanism terms, the way the v1 profile named probe-and-binary-search inflates and repeated full-history walks.

- Measure the floor: time the cheapest possible handler for each workload shape, so you know how much of the total is handler CPU and how much is client, transport, and HTTP-stack overhead.

- Keep grade-local runs for conformance only. They confirm 120 of 120 checks. They do not measure perf on this VM.

### Step 3: Design fixes from the profile

- Write one fix per hot path, each with a stated mechanism, the way the v2 SPEC wrote Adler-scan packs for parsePack and depth-bounded fetch for planFetch.

- Give every cache an invalidation rule in the same design step that adds the cache.

- Check what caching already exists before you add more, since the remaining work may sit in the timed workload paths rather than in another cache layer.

- State the expected gain per fix in the same units the profile measured, so step 4 can confirm or refute it.

### Step 4: A/B the new version

- Run the CPU A/B with the checklist above: same process, alternating passes, at least 3 passes, status-checked, identical bodies.

- Confirm the handler-level numbers separately with direct function-call benches, the way v2 confirmed pack parse at 0.175 milliseconds and depth-1 plan at 0.021 milliseconds.

- Confirm conformance is unchanged: the same checks that passed before must pass after, and responses on the recorded workload must match byte-identically.

- Treat a local wall-time result that contradicts the CPU A/B as throttle noise and discard it.

### Step 5: Decide from production numbers

- Submit a strict improvement with zero correctness risk even when the top-10 band looks out of reach.

- Read the production per-workload breakdown when the entry grades, and plan the next version from those numbers.

- Do not run more throttled local rounds to settle a question only production numbers can answer.

## When to stop

- Stop a workload when its handler CPU is already a small fraction of its total, since further handler work buys nothing against transport overhead.

- Stop local iteration when local measurement cannot distinguish the versions.

- Stop the rebuild when the remaining gains are sub-2x and the top-10 band stays out of reach on the estimate, and submit the strict improvement instead.

- Never trade correctness for speed. A perf gain that regresses conformance is a loss.

## Tools to reach for

Each tool is labeled by whether it is proven on this VM or still untested.

### Proven on this VM

- Handler-cost accounting by instrumented copy plus same-process driver. This is how the v1 profile was produced: per-function CPU time and call counts over the timed paths. Use it first on every agent-server perf job.

- CPU-time A/B driver in one process with alternating passes. This is how v2 was proven about 13 percent faster than v1 on read CPU. Use it for every version comparison.

- Direct function-call benches for handler-level numbers. This is how pack parse and depth-1 plan were measured. Use them to confirm a fix at the level the profile named.

### Untested on this VM

- Flame graphs. Named in the winning playbook as a gap in the catalog, but never run on this VM for a make.fun entry. Reach for them when handler-cost accounting shows a hot function whose cost you cannot explain from its own code, since a flame graph shows where inside the function and its callees the time goes. Verify the tooling works on this VM before you trust its output.

- Allocation profiling. Also named in the playbook as a catalog gap and never run on this VM. Reach for it when a hot path allocates heavily per request, since allocation pressure shows up as garbage-collection CPU that handler-cost accounting attributes to the wrong function. Verify the tooling works on this VM before you trust its output.

- Do not report flame-graph or allocation results as findings until the tooling has produced a verified run on this VM. Until then they are aspirational next steps, not evidence.
