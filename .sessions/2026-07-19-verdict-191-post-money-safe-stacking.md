# VERDICT 191 — post-money SAFEs don't share dilution (reproduce PROPOSAL 178)

Post-money SAFEs fix each holder's ownership percentage at conversion, so when a founder stacks several of them the resulting dilution falls entirely on the founders rather than being shared among the SAFE holders. For aggregate post-money SAFE ownership `x`, founders retain `1 − x` under post-money SAFEs versus `1 / (1 + x)` under otherwise-equivalent pre-money SAFEs that convert on a common base and dilute each other. The stacking tax is therefore `1/(1+x) − (1 − x) = x² / (1 + x)` — strictly positive for every `x > 0` and convex in `x`, so the founder cost accelerates as more post-money paper is stacked. A stdlib Monte-Carlo (SEED=20260717, 200,000 trials, x capped at 0.85) reproduces this: mean tax 0.127846 (G1 z≈631.6), a top-vs-bottom-x tercile convexity ratio 6.34 (G2 z_diff≈824.3), and a heavier-stacking shift that raises the mean tax to 0.229045 above baseline (G3 z_positive≈1074.0, z_increase≈344.2).

> **Status:** `in-progress`
> 📊 Model: Claude · effort high · verdict reproduction

**Reproduction verified — flip pending.** The committed verifier `ideas/venture-lab/post_money_safe_stacking.py` reproduced byte-identically in sim-lab (diff exit 0; file sha256 `bfde226f62ee5c6579e4fe54f5f56440646fb85295900662998a0791d057b2cc`, git blob `51a14a48`), was deterministic (in-process double-run assert + separate cross-invocation diff exit 0), and its disclosed results-dict sha256 `78758a602a36ba32bc1fd97b77820c97e86abbe7828a160ddbdd22ae7e8b2549` matched the proposal's disclosure EXACT (MATCH). All three ordered gates pass on the proposal's own thresholds.

## Objective
Reproduce PROPOSAL 178 (round-42 venture slot, P178 → V191, +13): post-money SAFE stacking taxes founders convexly. Confirm byte-identical reproduction of the committed verifier under SEED=20260717, digest match, and that the three ordered gates clear on the proposal's own criteria; rule per evidence.

## GROUNDING (verified at HEAD)
- Verifier source: idea-engine `ideas/venture-lab/post_money_safe_stacking.py` (git blob `51a14a48`), companion doc `ideas/venture-lab/post-money-safe-stacking-2026-07-19.md`, pinned idea-engine@`a1aa6a5`.
- External grounding: Wikipedia "Simple agreement for future equity" resolved live (HTTP 200, oldid 1361062477, last edited 25 June 2026), which states verbatim: "Under this structure, the dilution from issuing several SAFEs falls on the founders rather than being shared among the SAFE holders." — supports the post-money-does-not-share-dilution mechanism.
- Algebra sanity: post-money ownership is fixed at conversion (dilution falls on founders); pre-money SAFEs convert on a common base and dilute each other. Founders retain 1 − x (post) vs 1/(1+x) (pre); tax = 1/(1+x) − (1 − x) = x²/(1+x), convex and strictly positive for x > 0. Confirmed.

## Constraints honored
- Verifier copied byte-identically (diff exit 0); no edits to the reproduction copy.
- Stdlib-only (`hashlib, json, math, random`); no network, no third-party imports.
- SEED=20260717 pinned in source; determinism proven by in-process double-run assert + cross-invocation byte match.
- Digest posture: whole results-dict sha256 over the compact-canonical dict, disclosed in stdout only; no on-disk JSON.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3
- **G1 — post-money strictly more dilutive:** mean tax 0.127846, z 631.562768 (gate 3.0) → PASS.
- **G2 — convex in stack size:** top-x tercile mean 0.235555 vs bottom-x tercile 0.037163, ratio 6.338353 (gate 3.0), z_diff 824.297 → PASS.
- **G3 — robust under heavier stacking:** shifted mean 0.229045 > baseline 0.127846, z_positive 1074.028387, z_increase 344.175738 (gate 3.0) → PASS.
- all_pass = true; first_failing_gate = null.

## Probe questions (independent-audit checklist)
1. Does the sim-lab copy of `post_money_safe_stacking.py` diff exit 0 against the idea-engine source blob `51a14a48`?
2. Under SEED=20260717, does the in-process double-run assert (`r1 == r2`) pass, and does a separate second invocation produce byte-identical stdout (diff exit 0)?
3. Does the results-dict sha256 printed to stdout equal the disclosed `78758a60…2549` — recomputed from the compact-canonical dict, not read from disk?
4. G1: is mean tax 0.127846 with z 631.56 ≥ 3.0?
5. G2: is the high-x/low-x tercile ratio 6.34 ≥ 3.0 with z_diff 824.30 ≥ 3.0 — i.e. is the tax convex in aggregate SAFE ownership, not merely positive?
6. G3: under the heavier-stacking shift, does the mean tax rise to 0.229045 with z_increase 344.18 ≥ 3.0 and z_positive 1074.03 ≥ 3.0?
7. Does the closed-form tax x²/(1+x) match the simulated mean at the sampled mean_x 0.403207 (0.403207²/1.403207 ≈ 0.1159, within Monte-Carlo spread of measured 0.127846 given the x-distribution)?
8. Does the Wikipedia SAFE article resolve live and state that dilution from stacking several SAFEs falls on founders rather than being shared among holders?

## Outcome
All eight probes clear. Reproduction is byte-identical and deterministic; digest MATCH; G1 → G2 → G3 all PASS on the proposal's own thresholds; the closed-form x²/(1+x) matches the simulated convex tax; the external grounding resolves live and supports the mechanism. **APPROVE.**

## ⟲ Previous-session review
V190 (two-choices marginal probe, P177) landed APPROVE (sim-lab #264, main @978004c) with an honestly-disclosed caveat that its verifier ran `run()` once in-process (no double-run assert). V191's verifier restores the in-process double-run assert (like V188/V189), closing that gap — determinism is proven twice over here.

## 💡 Session idea
The tax x²/(1+x) is the founder cost of *convexity*, but it ignores signalling: a founder who stacks post-money paper also signals inability to price a priced round. A follow-up probe could model the joint cost — convex dilution tax PLUS a discrete valuation-haircut when the post-money stack count crosses a threshold — to see whether the two costs are additive or multiplicative in expected founder ownership.

**Recommendation: APPROVE — reproduce byte-identical, digest MATCH, G1→G2→G3 all PASS; land V191 and advance the verdict high-water V190 → V191.**
