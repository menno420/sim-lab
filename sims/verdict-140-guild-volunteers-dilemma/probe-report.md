# Probe report — VERDICT 140 · guild-contribution free-riding / the volunteer's dilemma (P127 → V140, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `## PROPOSAL 127 · 2026-07-18T08:46:46Z · status: sim-ready`.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/guild_volunteer_dilemma.py` — `diff` exit **0**, git blob `31b2e57dcadebe0796da139f0d9aa7adb31ec1b8`, file sha256 `d2de85b438200d3cbb7ef62660741fa108cd9071f8f7518a3ce86d9e006dc1c0`, **209** lines / **8470** bytes. Landed via idea-engine PR #555, main `2bfa25a`.
- Pinned world: **SEED=20260717**, TRIALS=**200000**, BENEFIT=**1.0**, COST=**0.5** (c/b=0.5), N_LO=**2**, N_STAR=**10**, N_HI=**20**, N_GRID=**[2,3,5,8,10,15,20]**, N_MAX=**20**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Paired common random numbers: each trial draws one shared N_MAX-length Uniform(0,1) vector u; member i volunteers at level N iff u_i<p*(N) (strategic) and iff u_i<p0=p*(N_LO) (fixed-rate control); provision fails iff no member volunteers. Gate z-scores are on the ESTIMATED MEAN via its standard error (se=std/√TRIALS).
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the P105/P109/P110/P114/P118/P122/P123/P126 family, DIFFERS from the V126/V138 SELF-FIELD/PRETTY-ON-DISK posture. `run()` returns a results dict carrying **NO** `results_sha256` field; `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>` and the gate lines. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 194–205 in the script text, not assumed.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P127 outbox / verifier `Results-JSON sha256:` line) | `6e6bf01ba2862addbd5a288d9fe8c71e6f1d3b398e8d5a2393da919b1f2e5933` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `6e6bf01ba2862addbd5a288d9fe8c71e6f1d3b398e8d5a2393da919b1f2e5933` |
| cross-invocation B (fresh `python3`) | `6e6bf01ba2862addbd5a288d9fe8c71e6f1d3b398e8d5a2393da919b1f2e5933` |
| in-process double-run #1 (run(), compact-hashed in-process) | `6e6bf01ba2862addbd5a288d9fe8c71e6f1d3b398e8d5a2393da919b1f2e5933` |
| in-process double-run #2 (run() again, compact-hashed in-process) | `6e6bf01ba2862addbd5a288d9fe8c71e6f1d3b398e8d5a2393da919b1f2e5933` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** bystander existence | mean(fail[20]−fail[2])=**0.231335** > 0, z=**159.8593** | mean **0.231335**, z **159.8593** | **PASS** |
| **G2** fixed-rate control sign-flip | mean(fail0[20]−fail0[2])=**−0.25004** < 0, z=**−258.2264** | mean **−0.25004**, z **−258.2264** | **PASS** |
| **G3** equilibrium anchor | max\|anchor z\|=**1.4147** < 3, z_vol=**1.1002** < 3, grid_monotone_increasing **True** | max\|anchor z\| **1.4147**, z_vol **1.1002**, monotone **True** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Failure curve (monotone rising): N=2 **0.25004**, N=3 0.35446, N=5 0.42214, N=8 0.45546, N=10 **0.464515**, N=15 0.476005, N=20 **0.481375**.
- G3 closed-form anchors: fail_2 **0.25004** vs (c/b)^{2/1}=**0.25** (z 0.0413) / fail_10 **0.464515** vs **0.46293736** (z 1.4147) / fail_20 **0.481375** vs **0.482088** (z −0.6382), max|anchor z| **1.4147** < 3.
- Constant total effort: mean volunteers @N=20 **0.71853** vs theory N·p*(N)=**0.71648004** (z **1.1002** < 3), near −ln(c/b)=**0.69314718**.
- Equilibrium volunteer probabilities: p*(2)=**0.5**, p*(10)=**0.07412529**, p*(20)=**0.035824**.

**Headline:** a "someone will do it" guild mechanic gets RISKIER with a bigger roster. Under the symmetric mixed-strategy equilibrium the probability NOBODY volunteers RISES from **0.25004** (N=2) to **0.481375** (N=20) toward the ceiling c/b=0.5 (**z=159.9σ**, G1), while a fixed-rate control (all members volunteer at the small-group rate p0=0.5) SIGN-FLIPS to a FALLING failure rate (**z=−258.2σ**, G2) — proving the rise is strategic equilibrium dilution, not group size. The strategic failure rate reproduces the exact (c/b)^{N/(N−1)} law at N=2/10/20 (max|z|=**1.4147** < 3, G3) and the mean volunteer count stays pinned near −ln(c/b)=0.693 (constant total effort — twenty members supply the same ~0.7 expected volunteers as a tuned pair), byte-for-byte across cross-invocations and an in-process double-run. Operator lesson: recruiting is not insurance — measure the pivotal-cost ratio c/b, read (c/b)^{N/(N−1)} as your coverage-failure floor, and remove the substitutability by ASSIGNING the duty to a named role (restoring provision to ~1), paying the volunteer a private surplus, or converting the shared good into an individually-rewarded task. Anchor: the volunteer's dilemma (Diekmann, JCR 1985), with the bystander effect / diffusion of responsibility (Darley & Latané 1968). **APPROVE.**
