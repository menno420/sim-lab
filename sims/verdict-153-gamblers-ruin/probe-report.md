# Probe report — VERDICT 153 · gambler's ruin edge asymmetry (P140 → V153, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order CFG_MOD → CFG_FAIR → CFG_EDGE. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/fleet/gamblers_ruin_edge_asymmetry.py` at `10047e1b` (PROPOSAL 140, round-32 UNRELATED slot CLOSER, landed via idea-engine #582). Permalink: https://github.com/menno420/idea-engine/blob/10047e1b84eab76621b5fac5475f7ed988b1e99f/ideas/fleet/gamblers_ruin_edge_asymmetry.py

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/gamblers_ruin_edge_asymmetry.py` — `diff` exit **0**, file sha256 `96b74bc0008fd89baaf458f1e34ebbd4ce21f5c79f22954d9661379ecebc3653`, git blob `60fd0dbdd39e4ee35b8dd70e2778ec4fc95f64e8`, **180** lines / **7855** bytes.
- Pinned world: **SEED=20260717**, **SIGMA_GATE=3.0**, linear-intuition anchor **LINEAR_ANCHOR=0.485**. Three configs drawn sequentially off ONE `random.Random(SEED)` stream in the fixed order: **CFG_MOD** p=0.48 i=20 N=40 trials=200000, **CFG_FAIR** p=0.50 i=20 N=40 trials=200000, **CFG_EDGE** p=0.485 i=100 N=200 trials=100000. Stdlib-only (hashlib, json, random); no numpy/scipy.
- Method: for each config the exact closed form is computed with no RNG — `closed_form(p,i,N)` returns i/N when p==0.5 else (1−r^i)/(1−r^N) with r=q/p — then `simulate()` runs `trials` fixed-stake ±1 walks from `i` to absorption at 0 or N (each step +1 with probability p else −1, off the single pinned stream) and counts the walks that reach N. The empirical reach probability mc = successes/trials, Bernoulli se = √(mc·(1−mc)/trials). The two agreement configs gate on z=(mc−closed)/se with PASS on |z|<3σ; the headline config gates on z=(L−mc)/se with PASS on z≥3σ. The single pinned stream drawn in the fixed config order makes the run deterministic — identical double-run → identical results dict → identical sha256.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the pretty `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump printed on stdout — recompute over the compact form. The compute entry is `run()`; `main()` itself calls `run()` twice, compact-hashes both, and asserts the two digests equal (the in-process double-run determinism check is built into the verifier).

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P140 outbox / verifier `Results-JSON sha256:` line) | `d6668ff14304a95d575b45f747efcbff4186e63cc6e306161da390a4f896a6ba` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `d6668ff14304a95d575b45f747efcbff4186e63cc6e306161da390a4f896a6ba` |
| cross-invocation B (fresh `python3`) | `d6668ff14304a95d575b45f747efcbff4186e63cc6e306161da390a4f896a6ba` |
| in-process run 1 (`run()` compact-hashed inside `main()`) | `d6668ff14304a95d575b45f747efcbff4186e63cc6e306161da390a4f896a6ba` |
| in-process run 2 (`run()` compact-hashed inside `main()`) | `d6668ff14304a95d575b45f747efcbff4186e63cc6e306161da390a4f896a6ba` |

**All canonical computations == the disclosed digest EXACTLY.** all_gates_pass=**true**, exit **0**, byte-identical across cross-invocation A/B (stdout diff exit **0**) and across the asserted in-process double-run.

## Gates (disclosed → reproduced), order CFG_MOD → CFG_FAIR → CFG_EDGE
| gate | criterion | disclosed | reproduced | result |
|---|---|---|---|---|
| **CFG_MOD** verifier-correctness agreement | MC reach vs exact closed form 0.167862, \|z\|<3σ (Bernoulli se) | mc **0.167100**, z **−0.914** | mc **0.167100** vs closed **0.167862**, se **0.000836**, z **−0.913774** | **PASS** |
| **CFG_FAIR** fair-game agreement | MC reach at p=0.5 vs exact i/N=0.5, \|z\|<3σ | mc **0.500710**, z **+0.635** | mc **0.500710** vs closed **0.500000**, z **+0.635044** | **PASS** |
| **CFG_EDGE** counterintuitive headline (z≥3) | MC reach z≥3σ BELOW linear anchor L=0.485 | mc **0.002510**, z **+3049.279** | mc **0.002510** vs L **0.485** (closed **0.002468**), se **0.000158**, z **+3049.279125** | **PASS** |

First-failing gate: **none**. all_gates_pass=**true**, exit **0**.

## Closed forms & observed (all match disclosed exactly)
- **CFG_MOD** (p=0.48, i=20, N=40): exact closed form P=(1−r^20)/(1−r^40)=**0.16786226899122164**; Monte-Carlo mc=**0.1671** over 200000 walks; z=(mc−closed)/se=**−0.913774** — the simulator's walks-to-absorption reproduce the biased-game closed form at a moderate edge.
- **CFG_FAIR** (p=0.50, i=20, N=40): exact i/N=**0.5**; Monte-Carlo mc=**0.50071** over 200000 walks; z=**+0.635044** — the fair-game baseline is a plain ratio with no exponential term (r=1, the geometric form degenerates to i/N).
- **CFG_EDGE** (p=0.485, i=100, N=200): exact closed form P=(1−r^100)/(1−r^200)=**0.00246818501883934**; Monte-Carlo mc=**0.00251** over 100000 walks; z=(L−mc)/se with L=**0.485**=**+3049.279125** — with a 1.5% edge the observed reach probability sits ~3049σ BELOW the linear-intuition anchor. A symmetric fair start worth 0.5 collapses to ~0.00247, a ~200× drop — NOT the ~0.485 a linear-in-the-edge intuition predicts. The penalty is exponential in the target distance N through the barrier ratio (q/p)^N, not linear in the edge.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = anyone reasoning about a fixed-stake sequential wager against a persistent edge — a bankroll grinder, a repeated-bet gambler, or more broadly any operator running an ADDITIVE random process toward a target between an absorbing floor and ceiling (a runway-to-milestone, a token-budget-to-goal, a survive-to-payout process). The transferable correction: **a small per-step edge does NOT cost a small, linear amount — the probability of reaching your target before ruin collapses EXPONENTIALLY in the target distance N through the barrier ratio (q/p)^N.** For a ±1 fixed-stake walk starting at i between barriers 0 and N, P(reach N before 0)=(1−(q/p)^i)/(1−(q/p)^N) for p≠0.5 (i/N for the fair game): a symmetric start (i=N/2) worth 0.5 in a fair game collapses to ~1/(1+(q/p)^{N/2}) under a small edge, so a 1.5% edge at N=200 is a ~200× penalty, not a ~1.5% one. To act on it: never read a small edge as a small penalty over a long grind — the per-step disadvantages MULTIPLY through the barrier ratio (they do not add), so a modest edge over a large target distance is ruinous, and "play longer to recover" makes it strictly worse. DISTINCT from the Kelly overbet-ruin head (a growth-optimal bet FRACTION on a MULTIPLICATIVE wealth process — a bet-sizing / log-utility object) and from the arcsine lead-illusion head (a FAIR-walk sojourn-time distribution — a lead-fraction law, not a biased two-barrier absorption): here the object is the first-passage reach probability of an additive fixed-stake walk, and the fair-game control (p=0.5, plain ratio i/N with no exponential term) proves the collapse is caused by the barrier ratio, not a magnitude or sim artifact.
