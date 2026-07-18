# VERDICT 133 — German-tank MVUE

Reproduce PROPOSAL 120 (round-27 UNRELATED slot closer, P120 → V133, +13): the German-tank problem — minimum-variance unbiased estimation of the maximum of a discrete-uniform population. You observe K=5 distinct serial numbers drawn WITHOUT replacement from an unknown fleet numbered 1..N and must estimate N. The naive estimate "N = the largest serial I have seen" (the sample maximum m) is systematically too LOW: E[m]=K(N+1)/(K+1)<N (bias (N−K)/(K+1)) because a finite sample almost never catches the top of the range. The counterintuitive fix ADDS BACK the expected gap — the MVUE EXTRAPOLATES ABOVE the largest observed serial: N̂=m(1+1/K)−1 = "sample maximum + the average gap between the ordered samples", exactly unbiased (E[N̂]=N) with exact variance (N−K)(N+1)/(K(K+2)), and since m≥K always, N̂≥m always. It is the MVUE because m is a complete sufficient statistic (Lehmann–Scheffé); a competing unbiased estimator Ñ=2x̄−1 is also unbiased but strictly less efficient — Var(Ñ)/Var(N̂)=(K+2)/3≈2.33× noisier at K=5 — so the best estimate of a population size is LARGER than the largest one you have seen, and the max-based correction is both correct and minimum-variance.

> **Status:** `in-progress`
> 📊 Model: high · review/verify

Born red by design: this card lands `in-progress` in the first commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the final commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (ORDER 003). No gate is bypassed. Reproduction + independent digest audit follow in the next commits; the outcome ruling below is filled only once the disclosed digest is reproduced byte-identical and all three gates hold.

## Objective
Reproduce the committed P120 reference verifier byte-identical under its pinned world (SEED=20260717, N_TRUE=1000, K=5, SAMPLES=4000, TRIALS=200, SIGMA_GATE=3.0) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest, (b) all three gates hold as disclosed, in order G1→G2→G3, (c) cross-invocation and in-process double runs are byte-identical. Source header (verbatim): `## PROPOSAL 120 · 2026-07-18T06:09:44Z · status: sim-ready` / `target: sim-lab (VERDICT 133, +13 offset)`.

## GROUNDING (verified at HEAD)
- idea-engine HEAD `0f61ea8026d401febe83aa0859c2d86e5e00d8fb` (#537); reference verifier `ideas/fleet/german_tank_mvue.py` — git blob `de5487e5bf706163188f811b97ed3b4723fc148a`, sha256 `130ebaafa72f8931440ac929954f8b0987d14ff947d5e7b09f36e8fe5b006aaf`, 188 lines / 8497 bytes. Source: https://github.com/menno420/idea-engine/blob/main/ideas/fleet/german_tank_mvue.py
- Domain reference: https://en.wikipedia.org/wiki/German_tank_problem (frequentist MVUE N̂=m(1+k⁻¹)−1 = sample max + average gap, unbiased with variance (N−K)(N+1)/(K(K+2))).
- sim-lab work branch cut from origin/main HEAD `acf8bf83ba41d6bb6762094c99b9adff4a80f401` (#206).
- DIGEST POSTURE: SELF-FIELD / stdout-line (the P119/V132 posture). The verifier computes the digest over `json.dumps(results, sort_keys=True, separators=(",",":"))` BEFORE adding the `results_sha256` field, then writes the on-disk `german_tank_mvue_results.json` pretty-printed (indent=2, sort_keys) WITH the field — so `sha256sum` of the on-disk file (`145db407…`) is NOT the digest; the disclosed digest is the value printed on the `Results-JSON sha256:` stdout line (and stored in the file's own `results_sha256` field).
- Offset authority: idea-engine control/outbox.md P120 `depends:` ledger (P120→V133 +13, "Offset pinned") + control/status.md baton — not docs/current-state.md (dormant snapshot through V059).

## Constraints honored
Stdlib-only (random, math, json, hashlib); verifier copied byte-identical (diff exit 0, blob + sha256 match); pinned SEED unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed.

## Gate plan (disclosed → reproduced)
- G1 MVUE-unbiased (headline+control): measured mean N̂ within 3σ of N=1000 (|z|<3, /se convention) — the estimator that extrapolates ABOVE the largest observed serial is spot-on for N.
- G2 max-biased-low + MVUE-above-max: (a) mean sample max strictly BELOW N by ≥3σ AND (b) mean N̂ exceeds mean sample max by ≥3σ — the estimate lands above the largest serial observed, the counterintuitive core.
- G3 closed-form-anchor + efficiency: (a) empirical Var(N̂) reproduces (N−K)(N+1)/(K(K+2))=28457.0 within 3σ (|z|<3) AND (b) the MVUE strictly more efficient than Ñ=2x̄−1: Var(Ñ)−Var(N̂)≥0 by ≥3σ.

## Outcome — PENDING (born-red HOLD)
Reproduction + independent digest audit in progress; this section is filled with the audited ruling in a later commit, and only then is the card flipped to `complete`.

## ⟲ Previous-session review
Prior loop landed VERDICT 132 (P119 PRD proc-rate compression, +13, sim-lab #206, digest ce121bd9…) — APPROVE, clean born-red flip, merge-on-green with no agent merge call. This slice closes round-27 on the verdict side at the UNRELATED slot (fleet P117→V130, venture P118→V131, game P119→V132, unrelated P120→V133).

## 💡 Session idea
Length-biased sampling of live serial ranges (fleet/ops): the German-tank MVUE assumes a static 1..N with uniform, gap-free numbering, but a monotonically-growing ID space sampled at a random wall-clock instant is length-biased toward the current high-water — sampling K live request/invoice IDs from a stream whose max is still climbing over-weights recent IDs, so the naive max is biased HIGH relative to the true issued-count-at-sample-time while the static MVUE gap-correction over-shoots. Sim: gate that a growing-stream sampler's realized N̂ over-estimates the true count-at-instant by a floor at ≥3σ (a sign-flip of P120's under-estimate), isolating how much of the gap correction is an artifact of the static-population assumption — distinct from P120's fixed-N discrete-uniform object.
