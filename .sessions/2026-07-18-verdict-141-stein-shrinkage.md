# VERDICT 141 — stein shrinkage dominance

Reproduce PROPOSAL 128 (round-29 FLEET slot, P128 → V141, +13): James-Stein shrinkage dominates the maximum-likelihood estimator in dimension p≥3 — estimation / decision-theoretic risk. Estimating a p-dimensional mean θ from a single noisy observation X ~ Normal(θ, σ²I) under squared-error loss, the "obvious" estimator is the MLE (the raw observation itself), which is unbiased and minimax. Stein's paradox (Stein 1956; James & Stein 1961) is that for p≥3 the MLE is INADMISSIBLE: the James-Stein estimator, which shrinks the observation toward a fixed target point by the data-driven factor (1−(p−2)σ²/‖X‖²), has strictly SMALLER risk than the MLE at EVERY θ, R_JS = p − (p−2)²·E[1/‖X‖²] < p. The dominance is uniform (no θ where the MLE wins), it GROWS with dimension (the (p−2)² gain factor rises with p — a monotone dose-response), and it VANISHES at the boundary p=2 where the (p−2) factor is zero (no shrinkage estimator dominates in dimensions 1 or 2). The extreme case θ=0 gives R_JS = 2.0 for every p≥3 — a p-dimensional MLE with risk p is beaten down to risk 2 by shrinking toward the truth. The counter-intuitive core: p unrelated quantities (a batting average, a wheat yield, the speed of light) are better estimated JOINTLY with shrinkage than each on its own by its own MLE, even though the problems share nothing — pooling toward a common point borrows strength from the geometry of high-dimensional squared-error loss, not from any real relationship between the coordinates. The operator lesson: when you fit many independent parameters at once (per-segment conversion rates, per-item demand means, per-cohort effects), the naive per-parameter estimate is provably beatable in aggregate squared error — regularize/shrink toward a pooled prior and you strictly win for p≥3.

> **Status:** `in-progress`
> 📊 Model: opus · high · review/verify

Born red by design: this card lands `in-progress` in the FIRST commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the deliberate LAST commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (ORDER 003). No gate is bypassed. This born-red HOLD is the ONLY reason the gate reads red pre-flip; a red gate AFTER the flip is a real defect, not the HOLD.

## Objective
Reproduce the committed P128 reference verifier byte-identical under its pinned world (SEED=20260717, TRIALS=200000, DIM=10, DIM_LO=3, DIM_HI=20, DIM_BOUNDARY=2, TAU=1.0, NOISE_SD=1.0, TARGET=0.0, SIGMA_GATE=3.0) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest `689ae146cb519e89d9ce8a9ed43919fdc87ad7c263531a122516cf74a4a5f57b`, (b) all three gates hold as disclosed, in order G1→G2→G3, (c) cross-invocation runs are byte-identical AND an in-process double-run is deterministic. Target: sim-lab (VERDICT 141, +13 offset).

## GROUNDING (verified at HEAD)
- Reference verifier `ideas/fleet/stein_shrinkage_dominance.py` — file sha256 `2dc8b4a42e8ada031dad0fc7df19d4db160ed9728aaa03ef789cb7ebb01aea03`, git blob `c66cc62a39b88134403562accf9dce5f2578e1e5`, **217** lines / **10473** bytes. Pinned source (permalink): https://github.com/menno420/idea-engine/blob/122feeaa553b0bf352e2a44bde7ba6c51f7bb28f/ideas/fleet/stein_shrinkage_dominance.py (idea-engine main `122feea`).
- Domain reference: Stein's paradox / James-Stein estimator (C. Stein, "Inadmissibility of the usual estimator for the mean of a multivariate normal distribution", Proc. 3rd Berkeley Symp. 1956; W. James & C. Stein, "Estimation with quadratic loss", 1961) — the risk identity R_JS = p − (p−2)²·E[1/‖X‖²] < p for p≥3, no dominance at p≤2.
- sim-lab work branch cut from origin/main HEAD (VERDICT 140 landed, sim-lab #214 `fc33d90`).
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY**. `main()` builds a results dict that carries NO `results_sha256` field, computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>` and `ALL_PASS: <bool>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 176–212 in the script text, not assumed. NOTE: this verifier exposes no `run()` entry point — the whole computation lives in `main()`; the in-process double-run therefore invokes `main()` twice with stdout captured, parses each pretty dump, recompacts and hashes.

## Constraints honored
Stdlib-only (random, math, json, hashlib); verifier copied byte-identical (diff exit 0, sha256 match); pinned SEED=20260717 unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed; zero agent merge calls (merge-on-green lands claude/* on the green head SHA per ORDER 003).

## Gate plan (disclosed → reproduced), order G1→G2→G3
- G1 existence advantage (shrinkage dominates MLE): mean paired advantage (R_MLE−R_JS) at p=DIM=10 > 0 with z=mean/se ≥ SIGMA=3.0 — the James-Stein estimator's squared-error risk beats the MLE's. Disclosed: mean **3.956766**, z **502.9231σ**.
- G2 dose-response (gain grows with dimension): mean advantage rises from p=DIM_LO=3 to p=DIM_HI=20 by ≥ 3σ — the shrinkage advantage is monotone increasing in dimension, not a fixed offset. Disclosed: dose (adv[20]−adv[3]) **6.648803**, z **507.6366σ**.
- G3 specificity boundary: at the p=DIM_BOUNDARY=2 boundary the advantage is EXACTLY 0 every trial (max|advantage| = 0.0) — the (p−2) shrinkage factor kills dominance at p=2, isolating p≥3 as the regime where shrinkage wins. Disclosed: max|adv|@p2 **0.0** exactly.
- Closed-form anchors: R_JS = p − (p−2)²·E[1/‖X‖²] < p; R_MLE(p=10)=10.0, R_JS(p=10) closed form **6.047064**; advantage closed form **3.952936**, anchor advantage z **0.4868** (<3, sim matches closed form); θ=0 → R_JS = **2.0** for all p.

## Outcome
[[fill: APPROVE ruling + reproduction evidence — completed at the born-red flip (LAST commit)]]

## ⟲ Previous-session review
[[fill: one honest line reviewing the V140 card/PR #214 — completed at the flip]]

## 💡 Session idea
[[fill: one deduped session idea — completed at the flip]]
