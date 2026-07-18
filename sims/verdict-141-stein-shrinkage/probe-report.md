# Probe report — VERDICT 141 · James-Stein shrinkage dominance (P128 → V141, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/fleet/stein_shrinkage_dominance.py` at main `122feea` (PROPOSAL 128).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/stein_shrinkage_dominance.py` — `diff` exit **0**, file sha256 `2dc8b4a42e8ada031dad0fc7df19d4db160ed9728aaa03ef789cb7ebb01aea03`, git blob `c66cc62a39b88134403562accf9dce5f2578e1e5`, **217** lines / **10473** bytes. Permalink: https://github.com/menno420/idea-engine/blob/122feeaa553b0bf352e2a44bde7ba6c51f7bb28f/ideas/fleet/stein_shrinkage_dominance.py
- Pinned world: **SEED=20260717**, TRIALS=**200000**, DIM=**10**, DIM_LO=**3**, DIM_HI=**20**, DIM_BOUNDARY=**2**, TAU=**1.0**, NOISE_SD=**1.0**, TARGET=**0.0**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. A fixed true mean vector θ is drawn once (Normal(0,TAU²), DIM_HI coords) and held constant; risk is averaged over the X-noise via paired common random numbers, with the James-Stein advantage (R_MLE−R_JS) evaluated per trial. Gate z-scores are on the estimated mean via its standard error (se=std/√TRIALS).
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>` and `ALL_PASS: <bool>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 176–212 in the script text, not assumed. This verifier exposes no `run()` entry point — the whole computation lives in `main()`; the in-process double-run invokes `main()` twice with stdout captured, parses each pretty dump, recompacts and hashes.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P128 outbox / verifier `Results-JSON sha256:` line) | `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b` |
| cross-invocation B (fresh `python3`) | `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b` |
| in-process double-run #1 (`main()`, compact-hashed in-process) | `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b` |
| in-process double-run #2 (`main()` again, compact-hashed in-process) | `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** existence advantage (shrinkage dominates MLE) | mean adv(p=10)=**3.956766** > 0, z=**502.9231** | mean **3.956766**, z **502.9231** | **PASS** |
| **G2** dose-response (gain grows with dimension) | dose(adv[20]−adv[3])=**6.648803** > 0, z=**507.6366** | dose **6.648803**, z **507.6366** | **PASS** |
| **G3** specificity boundary (p=2 exactly zero) | max\|advantage\|@p2 = **0.0** exactly | max\|adv\|@p2 **0.0** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**, `ALL_PASS: True`.

## Sim & anchors (all match disclosed exactly)
- Existence (G1): mean MLE risk (p=10) **10.009055** vs mean JS risk **6.052289** → mean paired advantage **3.956766** (se 0.007868), z **502.9231σ**.
- Dose-response (G2): mean advantage p=3 **0.79675** (se 0.007699) → p=20 **7.445553** (se 0.010596), dose **6.648803** (se_dose 0.013098), z **507.6366σ** — the shrinkage gain is monotone increasing in p.
- Specificity (G3): at p=2 mean MLE risk **2.006887** = mean JS risk **2.006887**, max|advantage| **0.0** exactly — the (p−2) factor zeroes the shrinkage, no dominance at the boundary.
- Closed-form anchors: R_MLE(p=10) **10.0**; R_JS(p=10) closed form **6.047064** (sim JS 6.052289); advantage closed form **3.952936** vs sim 3.956766, anchor advantage z **0.4868** (<3, sim matches closed form); R_JS(p=3) closed form **2.230204**; θ=0 → R_JS **2.0** for all p; θ-norm² DIM **9.264243**, DIM_LO **0.807136**.

**Headline:** the "obvious" MLE (raw sample mean) is provably beatable. Under squared-error loss in dimension p≥3 the James-Stein estimator's risk **6.052289** strictly dominates the MLE's **10.009055** at p=10 — a mean advantage of **3.956766** by **z=502.9σ** (G1) — and the advantage GROWS monotonically with dimension from **0.79675** (p=3) to **7.445553** (p=20), a dose of **6.648803** by **z=507.6σ** (G2). The dominance VANISHES exactly at the p=2 boundary (max|advantage| **0.0**, the (p−2) shrinkage factor is zero, G3), isolating p≥3 as the regime where shrinkage wins. The simulation lands on the closed form R_JS = p − (p−2)²·E[1/‖X‖²] < p (closed advantage 3.952936, anchor z **0.4868** < 3) and reproduces the θ=0 → R_JS=2.0 collapse for all p — byte-for-byte across cross-invocations A/B and an in-process double-run, results-dict sha256 `689ae146…a4a5f57b` matching the disclosed digest EXACTLY. Operator lesson: when you fit many independent parameters at once, the naive per-parameter estimate is provably beatable in aggregate squared error for p≥3 — shrink toward a pooled prior and you strictly win. Anchor: Stein's paradox (Stein 1956; James & Stein 1961). **APPROVE.**
