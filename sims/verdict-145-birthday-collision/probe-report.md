# Probe report — VERDICT 145 · the birthday-collision √N scaling law (P132 → V145, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/fleet/birthday_collision_sqrt_n.py` at main `cf2e20f` (PROPOSAL 132, #565).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/birthday_collision_sqrt_n.py` — `diff` exit **0**, file sha256 `a952116e774eb8b9aaa120309ca342564088248fa3a01bea7db347ca4ef40ba4`, git blob `be81b3b5ac1a2a2e410dad47a78f865d880a2793`, **247** lines / **10288** bytes. Permalink: https://github.com/menno420/idea-engine/blob/cf2e20fa69eb04b243b5a553d7270739e6f96c43/ideas/fleet/birthday_collision_sqrt_n.py
- Pinned world: **SEED=20260717**, TRIALS=**120000**, N_GRID=**(365, 1024, 4096, 16384)** (365 = the classic birthday space), N_LO=**1024**, N_HI=**16384** (√(N_HI/N_LO)=√16=**4.0** exactly), SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Draw `randrange(N)` into a set one at a time off the SINGLE pinned `random.Random(SEED)` stream until the first repeat, over N_GRID in fixed order; record mean waiting time, unbiased variance, and (at N_HI) the fraction of trials collided by draw m*. Exact deterministic anchors (no RNG): E[T_N]=Σ_{k=0}^{N} P(first k draws distinct) and the smallest m with P(collision within m)≥0.5. Gate z-scores are on the ESTIMATED statistic via its standard error (se=√(var/TRIALS) for the mean; delta-method se for the ratio; Bernoulli se=√(p0(1−p0)/TRIALS) for the proportion), the P104..P130 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 217–243 in the script text, not assumed. The computation lives in `run()` (returns the results dict), so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P132 outbox / verifier `Results-JSON sha256:` line) | `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` |
| cross-invocation B (fresh `python3`) | `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced the identical results dict AND identical digest run-to-run (`run()` #1 == `run()` #2 as dicts).

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** sim-correct (MC mean at N_HI within 3σ of exact E[T_16384]) | mean **161.135750** vs exact **161.091690**, z **+0.183** | mean **161.13575**, exact **161.09169039641162**, z **+0.18284** | **PASS** |
| **G2** √N law (MC ratio within 3σ of exact ratio; sqrt_not_linear) | ratio_mc **3.947145** vs exact **3.950654** ~ √16=**4.0** (folk 16.0), z **−0.425** | ratio_mc **3.947145058263201**, exact **3.950654103686657**, sqrt_leading **4.0**, folk **16.0**, z **−0.42494**, sqrt_not_linear **True** | **PASS** |
| **G3** inversion (MC frac collided by m* > 0.5, within 3σ of anchor 0.500101, m*/(N/2)≪1) | frac **0.500183** > 0.5, anchor **0.500101**, m*=**151**, m*/(N/2)=**0.018433**, z **+0.057** | frac **0.5001833333333333**, anchor **0.5001010975997842**, m* **151**, m*/(N/2) **0.0184326171875**, z **+0.05697**, majority **True**, tiny_fraction **True** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Exact deterministic waiting-time means E[T_N]=1+Q(N): E[T_365]=**24.616586** (matches published 24.61659), E[T_1024]=**40.775954**, E[T_4096]=**80.880396**, E[T_16384]=**161.091690**. MC means: N=365→**24.582992**, 1024→**40.823367**, 4096→**80.736133**, 16384→**161.135750**. MC mean/√N → C=√(π/2)=**1.253314**: {365: **1.286733**, 1024: **1.275730**, 4096: **1.261502**, 16384: **1.258873**}.
- **G1 (sim-correct, headline):** MC mean at N_HI=16384 = **161.13575** vs exact E[T_16384]=**161.09169039641162**, se=√(var/TRIALS), z=**+0.18284** — |z| < 3σ, the Monte-Carlo mean waiting time lands on the exact finite-N anchor.
- **G2 (√N scaling law):** MC ratio mean(T@16384)/mean(T@1024) = **3.947145058263201** vs the EXACT-mean ratio E[T_16384]/E[T_1024] = **3.950654103686657**, z (delta method) = **−0.42494** < 3σ; the exact ratio is a √N-law value (|3.950654 − 4.0|=0.049 ≪ |3.950654 − 16.0|=12.049 ⇒ sqrt_not_linear=**True**), decisively far from the linear-N folk prediction **16.0**. The mean grows like √N, not N — doubling the space (×2) buys only √2≈1.41× more draws.
- **G3 (inversion):** m*=**151** = smallest m with exact P(collision by m)≥0.5 (exact anchor P=**0.5001010975997842**); MC fraction of trials collided by draw m* = **0.5001833333333333** > 0.5 (majority=**True**), z (Bernoulli se) = **+0.05697** < 3σ; m*/(N/2) = **0.0184326171875** ≪ 0.1 (tiny_fraction=**True**). A collision is more-likely-than-not after only ~1.1774√N draws — a vanishing 1.84% of N/2 — reversing the "need ~N/2 draws" folk belief.
- Leading coefficients (deterministic): C_MEAN=√(π/2)=**1.2533141373155001**, C_HALF=√(2 ln 2)=**1.1774100225154747**.

> NOTE on G2 anchor: the idea-engine outbox dry-sim narrative rounds the exact ratio as `3.950637`; the actual results-dict value is `3.950654103686657` (the outbox figure is a display artifact in the prose). The reproduced digest `838bee17…` matches the disclosed digest EXACTLY over the whole dict, so the exact dict value `3.950654103686657` is the one baked into the authoritative digest — reproduced bit-for-bit.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/fleet/birthday_collision_sqrt_n.py \
   sims/verdict-145-birthday-collision/birthday_collision_sqrt_n.py
diff idea-engine/ideas/fleet/birthday_collision_sqrt_n.py \
     sims/verdict-145-birthday-collision/birthday_collision_sqrt_n.py     # exit 0
sha256sum <both>   # a952116e774eb8b9aaa120309ca342564088248fa3a01bea7db347ca4ef40ba4 (both)

# cross-invocation A/B (fresh processes)
python3 birthday_collision_sqrt_n.py > run-stdout.txt       # exit 0
python3 birthday_collision_sqrt_n.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51

# in-process double-run + independent compact-digest recompute
python3 -c "run() x2; sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs 838bee17…710c51 == disclosed; dict identical run-to-run
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, sha256 `a952116e…40ba4`), the results-dict sha256 reproduces the disclosed digest `838bee178afb150de05ebeaf65f4d712eedb39d1fd861f311a4f2b1c4f710c51` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.
