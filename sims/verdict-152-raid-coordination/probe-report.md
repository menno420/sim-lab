# Probe report — VERDICT 152 · raid team-size coordination overhead / the Ringelmann DPS cliff (P139 → V152, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/superbot-games/raid_coordination_overhead.py` at `086733e5` (PROPOSAL 139, round-32 GAME slot, landed via idea-engine #580). Permalink: https://github.com/menno420/idea-engine/blob/086733e5eae49d5ee55a6829a3e1d9910397d36f/ideas/superbot-games/raid_coordination_overhead.py

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/raid_coordination_overhead.py` — `diff` exit **0**, file sha256 `b3c5137967233f107e16066cd69772eb37401bbf48d3961f66d86c879287ff85`, git blob `0268dea7126d6ba96545a8f609e5c93858d7c155`, **238** lines / **9445** bytes.
- Pinned world: **SEED=20260717**, **TRIALS=20000**, **NMAX=8**, base_i ~ Gamma(**K_SHAPE=4.0**, **THETA=25.0**) → mean 100 / CoV 1/√K=**0.5**, uptime decay **C_UPTIME=0.06** / **FLOOR=0.35**, collision waste **Q_COLLISION=0.07**, interior null **P0_INTERIOR=0.5**, **SIGMA_GATE=3.0**. Stdlib-only (hashlib, json, math, random); no numpy/scipy.
- Method: each trial draws NMAX i.i.d. base DPS values base_i ~ Gamma(K=4, θ=25), forms prefix sums, and evaluates DPS(N) = (Σ_{i=1..N} base_i)·uptime(N)·(1−q)^(N−1) for every N=1..NMAX. The SAME base draw feeds every N AND both the overhead world and the zero-overhead PLACEBO (c=0, q=0) — so the G1 cliff difference DPS(N*)−DPS(NMAX) and the G3 placebo difference DPS(NMAX)−DPS(N*) are within-trial PAIRED, and the SE is the paired-difference std/√TRIALS over 20000 i.i.d. trials. The per-trial argmax roster size feeds the G2 interior fraction (a one-proportion z vs p0=0.5). The mean-model peak N* is computed by `peak_roster()` = argmax over N of MU·N·uptime(N)·(1−q)^(N−1) (MU=100), i.e. **not hard-coded**.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the pretty `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump printed on stdout — recompute over the compact form. The compute entry is `run()`, so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P139 outbox / verifier `Results-JSON sha256:` line) | `16225c9a8e53cc23cfaa6a5df4b9631e5224d36a80ebada7f1a86546606c9fa3` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `16225c9a8e53cc23cfaa6a5df4b9631e5224d36a80ebada7f1a86546606c9fa3` |
| cross-invocation B (fresh `python3`) | `16225c9a8e53cc23cfaa6a5df4b9631e5224d36a80ebada7f1a86546606c9fa3` |
| in-process run 1 (`run()` compact-hashed) | `16225c9a8e53cc23cfaa6a5df4b9631e5224d36a80ebada7f1a86546606c9fa3` |
| in-process run 2 (`run()` compact-hashed) | `16225c9a8e53cc23cfaa6a5df4b9631e5224d36a80ebada7f1a86546606c9fa3` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across cross-invocation A/B (stdout diff exit **0**) and across the in-process double-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | criterion | disclosed | reproduced | result |
|---|---|---|---|---|
| **G1** cliff (smaller premade out-DPSes full roster) | mean DPS(N*)−DPS(NMAX) > 0 AND z ≥ 3σ (one-sided /se) | mean **+13.1796**, z **+62.61** | mean **+13.179610** (se **0.210501**), z **+62.610617** | **PASS** |
| **G2** interior peak (argmax strictly interior) | interior_fraction one-proportion z vs p0=0.5 ≥ 3σ AND mean-model N* interior | frac **0.85980**, z **+101.77** | frac **0.85980** vs p0 **0.5**, z **+101.766808**, N*=**6** interior | **PASS** |
| **G3** placebo (c=0,q=0 ⇒ monotone, full roster wins) | interior_fraction = 0.0 exactly AND mean DPS(NMAX)−DPS(N*) > 0, z ≥ 3σ | frac **0.0**, full-beats **+199.4478**, z **+399.62** | frac **0.0**, full-beats **+199.447810** (se **0.499088**), z **+399.624601** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & mean-model (all match disclosed exactly)
- **Deterministic mean-model DPS by roster N** (MU·N·uptime(N)·(1−q)^(N−1), MU=100, no RNG): {1: **100.0**, 2: **174.84**, 3: **228.3336**, 4: **263.829096**, 5: **284.259764**, 6: **292.189115**, 7: **289.851602**, 8: **279.189204**}. The product rises to N=6 then falls — single-peaked at the interior N*=**6**; mean_dps_at_n_star=**292.1891151059999**, mean_dps_at_nmax=**279.18920396191237** (peak strictly beats the full roster by +13.00).
- **G1 (cliff):** the paired per-trial difference DPS(N*=6)−DPS(NMAX=8) has Monte-Carlo mean **+13.179610** with z=**+62.610617** — the six-body premade STRICTLY out-DPSes the eight-stack at a fixed pre-registered roster size, not by post-hoc selection.
- **G2 (interior peak):** the per-trial argmax roster size is strictly interior (1 < N*_t < 8) in **85.980%** of the 20000 trials; the one-proportion z against p0=0.5 is **+101.766808** (≥3σ), and the mean-model peak N*=6 is itself interior — the optimum is an interior team size, neither solo nor full stack.
- **G3 (placebo):** removing the overhead (C_UPTIME=0, Q_COLLISION=0) makes DPS(N)=Σ base_i monotone increasing, so the interior fraction is **0.0** EXACTLY and the paired mean DPS(NMAX)−DPS(N*)=**+199.447810** with z=**+399.624601** — the full roster reliably wins with no overhead. The interior peak is CAUSED by the coordination-overhead terms (uptime decay + burst collision), not by Monte-Carlo noise.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = any co-op-game raid/party leader, guild officer, or PvE group composer choosing a roster size against a DPS-race objective (enrage-timer boss, speed clear, damage check) — and more broadly any coordinator sizing a team whose per-capita output falls with headcount. The transferable correction: **realized total output is a nominal sum times a group-size-decaying overhead product, so it PEAKS at an interior roster size N* < the cap — "more bodies = more output" is FALSE past N*.** For a co-op raid, DPS(N) = (Σ base_i)·uptime(N)·(1−q)^(N−1): the sum grows linearly but per-member uptime (movement, mechanic-dodges, target-swaps) and burst-window collision (overkill, shared debuff caps) both decay in N, so the product maxes at an interior N* (here N*=6 for an 8-cap raid, +13 DPS / ~4.7% above the full stack). To act on it: measure your own uptime-decay rate c and collision-waste q, solve N* = argmax N·uptime(N)·(1−q)^(N−1), and right-size the premade — against an enrage timer the right-sized N* group clears where the full stack wipes. This is the Ringelmann effect (per-member productivity falls with group size through coordination and motivation loss). DISTINCT from a rock-paper-scissors / replicator fixed-point (a composition-mix result on WHICH members, not HOW MANY) and from a tail-amplification / union-over-leaves object (a rare-event tail probability, not a mean single-peak): here the mean itself is single-peaked in the count, and a zero-overhead placebo proves the overhead is the sole cause.
