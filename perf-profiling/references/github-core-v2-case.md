# Case study: github-core-clone-01 v2

The full numbers behind the perf-profiling skill. Every figure here comes from the v2 verification record, the v2 top-10 study, or the platform research snapshot of 15 Nov 2026. Nothing here is projected except where it says estimate.

## The score and the gap

- Total score is feature 600 plus agent 200 plus perf 200, for a 1000 maximum.

- Perf is 4 workloads times 50 points each: push, clone, read, write.

- Each workload scores round of clamp of 25 minus 12.5 times log2 of t divided by T_ref, clamped between 0 and 50.

- T_ref values from the production kit are push 1640.82 milliseconds, clone 266.941 milliseconds, read 2759.715 milliseconds, and write 348.965 milliseconds.

- At exactly T_ref a workload scores 25 points, for 100 total. At half of T_ref a workload scores about 38, for about 152 total. At a quarter of T_ref a workload scores 50, for 200 total.

- v1 scored 898 total: feature 600, agent 200, perf 98, with p50 828,243 microseconds.

- Rank 1 scored 953 total: feature 600, agent 200, perf 153, with p50 387,494 microseconds.

- The whole 55-point gap was perf. Both entries maxed feature and agent, so no feature work could close any of it.

- The arithmetic closes exactly: 828,243 divided by 387,494 is 2.14, log2 of 2.14 is about 1.10, 12.5 times 1.10 is about 13.7 points per workload, and 13.7 times 4 workloads is about 55 points.

- perf p50 is 1000 times the geometric mean of the four workload medians, and it is a tie-break only. The reference geometric mean is 805,899 microseconds.

## The top-10 band

- All top-10 entries scored feature 600 and agent 200. Perf ran 147 to 153 and p50 ran 387,000 to 421,000 microseconds.

- Top-10 entries sit near half of T_ref on every workload.

- Perf down the board: rank 251 scored perf 135 with p50 501,000 microseconds, rank 501 scored perf 130 with p50 529,000, rank 1001 scored perf 123 with p50 585,000, and rank 2001 scored perf 110 with p50 709,000.

- Techniques the top 10 advertise in their titles: microsecond caching at rank 1, pack cache plus oid-carrying packs at rank 10, flat hash-table store plus lazy pack builder at rank 6, lock-free raw-socket plus shared pack cache at rank 12, and a native Go port at rank 11.

- Final-stage gate: only the top 60 on the qualifying trial go on to the 3-instance final, and a prize needs a score strictly above the reference forge.

## v1 per-workload breakdown

- Local grade-local trials gave v1 perf 69, 96, and 104 across three trials, with p50 from 770,000 to 1,229,000 microseconds. The server grade gave perf 98 with p50 828,243 microseconds, consistent with local trials 1 and 2.

- Clone was the weakest workload at 14 to 19 points, running slower than T_ref. Push, read, and write each scored 26 to 29 points, at 0.82 to 0.93 times T_ref.

- The clone workload is 50 concurrent depth-1 clones.

## v1 profiling: what the instrumented run found

- Method: an instrumented copy of the v1 entry driven by a same-process driver. Function CPU time is exact in one process. Wall times were inflated by the shared-CPU throttle.

- parsePack: 206 calls, 1603 to 2494 milliseconds total, 7.8 to 12.1 milliseconds average per call. Root cause was finding each zlib stream end with an exponential probe plus binary search using about 16 inflateSync calls per entry, most of them throwing exceptions. A 3-object push pack paid about 50 throwing inflates.

- planFetch: 55 calls, 155 to 243 milliseconds total, 2.8 to 4.4 milliseconds average per call. Root cause was walking the full 200-commit history 3 or more times per depth-1 clone and re-parsing every commit on each walk.

- buildPack: 55 calls, 22 to 40 milliseconds total, 394 to 736 microseconds average. It was rebuilt per clone, so 50 identical clones produced 50 identical packs.

- advertisementV0: 206 calls, 15 to 20 milliseconds total, 72 to 95 microseconds average. It was rebuilt per info refs GET.

- issueJson: 2211 calls, 8 to 16 milliseconds total, 4 to 7 microseconds average. createIssueRec ran 18 to 20 microseconds.

- REST handlers were already lean. Read and write wall time was dominated by client plus transport plus HTTP-stack overhead, not by handler CPU.

- Floor experiment: a minimal canned-JSON server measured slower than v1 on the same workload, which proved local VM wall times are dominated by shared-CPU throttle noise of 2x or more between runs.

## v2 handler-level results

- Pack parse fell to 0.175 milliseconds, against v1 profiled at 7.8 to 12.1 milliseconds.

- Depth-1 plan fell to 0.021 milliseconds, against v1 at 2.8 to 4.4 milliseconds.

- Plan plus build together measured 0.263 milliseconds.

- The pack cache was verified with 50 identical clone responses.

- These handler numbers came from the author's direct function-call benches, which are valid. The author's HTTP benches are not valid, as the next section explains.

## The invalid HTTP benches

- The author's bench2 and bench3 HTTP numbers are invalid. They sent a wrong Bearer token and never checked status, so they measured 401 error responses.

- The author passed one token to createApp and sent a different Bearer token in bench2 and bench3. Every request returned 401.

- The reported numbers from those benches, including 0.49 milliseconds per request CPU and 6.1 milliseconds per request matching the suite, measured error responses and mean nothing.

- The failure was caught only by the coordinator's independent re-measurement with status assertions.

## The redaction trap

- A literal Bearer token written in a tool-call argument is replaced with a placeholder BEFORE execution. This was proven: the runtime string length was 17 against an expected 10.

- The file on disk then contains the placeholder, and a strict-auth server returns 401.

- Build auth headers dynamically at runtime by concatenating the scheme and the token value. Never write a literal Bearer token in a tool call, a heredoc, or an edit.

## CPU A/B: the valid comparison

- Driver: raw node http keep-alive, client plus server CPU in one process, status-checked, 3 alternating passes. Throttle-invariant.

- Read CPU: v2 0.468 against v1 0.537 milliseconds per request. v2 was about 13 percent faster and won all 3 passes.

- Write CPU: v2 0.619 against v1 0.603 milliseconds per request. Tied.

- Both versions returned identical 304-byte bodies in the read A/B.

- Read wall time: v2 won 2 of 3 passes, which is consistent with the CPU result but not the basis for it.

## Why wall time is unreadable locally

- A/B grade-local on the same kit, back to back: v1 perf 20 with p50 2.54 million microseconds, v2 perf 8 with p50 3.53 million microseconds.

- v1 itself fell from perf 96 to 104 on a quiet VM to 20 under throttle, with no code change.

- Single-trial pair, v2 slower on all four workloads locally, worst on read. That local wall-time result contradicts the CPU A/B, which is why wall time is discarded and CPU time is trusted.

## Production estimate and stop decision

- Estimate for production on an unthrottled harness: perf about 120 to 130, up from v1's 98, with p50 about 550,000 to 650,000 microseconds, down from 828,000.

- This is an estimate projected from CPU A/B numbers, not a measurement. The real figure comes only from the production grade.

- The top-10 band at perf 147 and above was judged likely out of reach. REST workloads are bounded by client plus HTTP-stack overhead that no server change removes, and the remaining push and clone gains are sub-2x.

- Expected rank improvement was from around 2295 toward roughly 1000 to 1500. Rank 1001 sits at perf 123.

- Decision: submit v2 as a strict improvement with zero correctness risk, read the production per-workload breakdown when it grades, and decide on a v3 from real numbers rather than more throttled local runs.

## Correctness held through the rebuild

- v2 scored feature 600, agent 200, and 120 of 120 checks, with replay reproduced.

- The coordinator's own grade-local runs confirmed both v1 and v2 at 120 of 120 with 0 failed.

- The v2 SPEC section 11 was confirmed in code: Adler-scan pack reader with at most 2 inflates per entry and no probe loops, depth-bounded planner, pack cache capped at 8 and version-invalidated, advertisement cache, commit and tree caches, no per-request logging, and no wall-clock or unseeded randomness in handlers.
