# Probe report — VERDICT 138 · USL coherency retrograde-throughput cliff (P125 → V138, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `## PROPOSAL 125 · 2026-07-18T08:03:18Z · status: sim-ready`.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/usl_coherency_retrograde_cliff.py` — `diff` exit **0**, git blob `08806218ebf2a2638d545e5a493f967b60629e04`, file sha256 `f46b0241c10f4415f20ab9ce44dbb8b12aaf0cbea7119ff2565bacd1ca9b9183`, **270** lines / **11536** bytes.
- Pinned world: **SEED=20260717**, ALPHA=**0.03**, BETA=**0.001**, TRIALS=**400**, BATCH=**200**, N_GRID=**(1,2,4,8,16,24,31,48,64,96,128,200)**, N_STAR=**31**, N_HI=**200**, SIGMA=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Each fleet realization draws T(N)=(1−α)/N·Ā+(α−β)·S+β·B from unit-mean components (Ā=Gamma(N,1)/N averaging N Exp(1) draws → the 1/N EMERGES; S=Exp(1); B=Gamma(N,1) summing N Exp(1) draws → the βN coherency EMERGES), so E[T(N)] is exactly the USL time and the retrograde peak emerges from competing 1/N-vs-βN draws, not asserted. Gate z-scores are on the ESTIMATED MEAN via its standard error (se=std/√TRIALS).
- DIGEST POSTURE: **SELF-FIELD / PRETTY-ON-DISK** — same family as the V126 exemplar, DIFFERS from the V135/V136 NO-SELF-FIELD/COMPACT-STDOUT posture. `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode())` BEFORE adding a self-field, THEN sets `results["results_sha256"]=digest`, writes PRETTY JSON `json.dumps(results, indent=2, sort_keys=True)` to `usl_coherency_retrograde_cliff_results.json`, and prints the pretty dump + `Results-JSON sha256: <digest>` + 3 gate lines + summary + `ALL_PASS: True`. The disclosed digest is thus the sha256 of the results dict **WITHOUT** its own `results_sha256` field.
- Reconciliation (honest): the on-disk `usl_coherency_retrograde_cliff_results.json` is PRETTY (indent=2, 2463 bytes) and DOES carry the `results_sha256` self-field, so a naive `sha256sum` of that file is **`2f3318a80d222607283fc475f92953ac2505755f9a85910ac26edf7dc091879b`** — NOT the digest. The disclosed digest is recovered by loading the json, dropping `results_sha256`, re-serializing compact (`sort_keys=True, separators=(",",":")`), and re-hashing → `e496837c…9557`. Two independent confirmations both land on the disclosed digest: (a) the self-field stored on disk == `e496837c…9557`, and (b) the compact re-hash with the self-field dropped == `e496837c…9557`. `run-stdout.txt` is the pretty dump + `Results-JSON sha256:` line + gate/summary lines. Classified against `main()` in the script text, not assumed.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P125 outbox / verifier `Results-JSON sha256:`) | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` |
| cross-invocation B (fresh `python3`) | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` |
| in-process double-run (run() ×2, hashed compact in-process) | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` (both) |
| `results_sha256` self-field on disk | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` |
| compact re-hash of json with self-field dropped | `e496837c6dd8bbbaec79701528507185a0a08cb8c008255317d3719d99795557` |
| naive `sha256sum` of pretty on-disk json (self-field present, informational — NOT the digest) | `2f3318a80d222607283fc475f92953ac2505755f9a85910ac26edf7dc091879b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**, on-disk json diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** retrograde existence | mean(T(200)−T(31))=**0.142452** > 0, z=**959.9168** ≥ 3σ (se **0.000148**) | mean **0.142452**, se **0.000148**, z **959.9168** | **PASS** |
| **G2** coherency-necessity (β=0 Amdahl control) | mean(T0(200)−T0(31))=**−0.026410** < 0, z=**−189.0673** ≤ −3σ (se **0.000140**) | mean **−0.026410**, se **0.000140**, z **−189.0673** | **PASS** |
| **G3** USL-anchor + peak | \|z_star\|=**0.0507** / \|z_hi\|=**0.5417** < 3 AND grid argmin=**N*=31** | z_star **−0.0507**, z_hi **−0.5417**, argmin **31**, full-grid max\|z\| **1.6993** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Closed form: N* = √((1−α)/β) = √(0.97/0.001) = **31.144823** → grid **31**; Amdahl ceiling 1/α = **33.333**.
- USL speedup: C(31) = **10.954064**, C(200) = **4.276245**, peak/hi ratio = **2.561608** (a 200-agent fleet delivers under half the 31-agent peak).
- Measured time curve (rises-then-falls in throughput ⇒ dips-then-rises in time): T(31) **0.091285** (cf **0.091290**), T(200) **0.233791** (cf **0.233850**), grid argmin = **31**. Measured speedup curve N=1→**1.000**, 16→**9.510**, 31→**11.019** (peak), 64→**9.302**, 128→**6.114**, 200→**4.302**.

**Headline:** a fleet on a coordinated job does NOT scale N× and does NOT merely saturate — with any pairwise coherency cost β>0 it follows the Universal Scalability Law C(N)=N/(1+α(N−1)+βN(N−1)), which PEAKS at N*=√((1−α)/β) then DECLINES. On the pinned world (α=0.03, β=0.001) the peak is at **N*=31** and the retrograde cliff is real and large: past the peak, adding agents strictly increases completion time — mean(T(200)−T(31))=**0.142452** at **z=959.9σ** (G1). The drop is caused by COHERENCY, not fleet size: the β=0 Amdahl control on the SAME fleet FLIPS the sign to monotone-faster — mean(T0(200)−T0(31))=**−0.026410** at **z=−189.1σ** (G2). The measured curve reproduces the exact USL closed form at N*/N_hi (|z_star|=**0.0507**, |z_hi|=**0.5417**, full-grid max|z|=**1.6993**) with its grid argmin pinned at **N*=31** (G3), and the closed-form anchors C(31)=**10.954064** / C(200)=**4.276245** (peak/hi **2.561608**) reproduce — byte-for-byte across cross-invocations and an in-process double-run. Operator lesson: a coordinated fleet has a finite optimal size N*; to go faster past the peak, CUT coordination (partition state, batch merges, hub-not-mesh gossip) to lower β — adding agents cannot; only a genuinely β≈0 independent-subtask job scales with more agents, itself still Amdahl-capped at 1/α. Anchor: Gunther, the universal law of computational scalability, with Amdahl's law as the β=0 control. **APPROVE.**
