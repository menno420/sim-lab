# VERDICT 131 — the sales-ramp capacity drag

Reproduce PROPOSAL 118 (round-27 VENTURE slot, P118 → V131, +13): a Monte-Carlo of a steadily-hiring sales force where each rep's booked quota ramps linearly over R=6 months and reps churn at rate δ. In steady state the realized productivity per active rep is the closed form φ(β)=(1−e^{−βR})/(βR) with β = monthly headcount growth + attrition. Faster headcount growth (β_fast=g_fast+δ_low=0.11) and a matched attrition bump (β_attr=g_slow+δ_hi=0.11) both drag realized quota ≈0.157 below the slow-growth baseline (β_slow=g_slow+δ_low=0.04) — i.e. growth and attrition are interchangeable drags on capacity.

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · review/verify

Born red by design: this card lands `in-progress` in the first commit so the substrate-gate HOLD holds the PR red until the reproduction is proven; the final commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (ORDER 003). No gate was bypassed.

## Objective
Reproduce the committed P118 reference verifier byte-identical under its pinned world (SEED=20260717, TRIALS=400, N_REPS=20000) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest, (b) all three gates hold as disclosed, (c) cross-invocation runs are byte-identical. Source header (verbatim): `## PROPOSAL 118 · 2026-07-18T05:30:18Z · status: sim-ready` / `target: sim-lab (VERDICT 131, +13 offset)`.

## GROUNDING (verified at HEAD)
- idea-engine HEAD 4310ff22ebdac308f2b0f0a17dcbb07a555ae6c7; reference verifier `ideas/venture-lab/sales_ramp_capacity_drag.py` — git blob 87503489bd55fe9073a4268c46fa46d09917387e, sha256 e42b0e8c64891f81449643710e3358d6a7d3cb93ed099b1472ce205243225e89, 220 lines / 9297 bytes. Source: https://github.com/menno420/idea-engine/blob/main/ideas/venture-lab/sales_ramp_capacity_drag.py
- sim-lab work branch cut from origin/main HEAD 9b0a0e9fee54f91201f9af0cb74bf99334cbc8d5.
- DIGEST POSTURE: WHOLE-DICT / no-self-field / stdout-only — results dict carries no `results_sha256`; digest = sha256 over json.dumps(results, sort_keys=True, separators=(",",":")) printed as a sibling `sha256:` line; the verifier writes no file. The committed `sales_ramp_capacity_drag_results.json` here is that exact compact-canonical line (no trailing newline) so `sha256sum` of the file reproduces the digest.
- Offset authority: idea-engine control/outbox.md P118 `depends:` ledger (P118→V131 +13, "Offset pinned") + control/status.md baton — not docs/current-state.md (dormant snapshot through V059).

## Constraints honored
Stdlib-only (random, math, json, hashlib); verifier copied byte-identical (diff exit 0, blob + sha256 match); pinned SEED unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed.

## Gate plan (disclosed → reproduced)
- G1 growth-capacity-drag: mean(φ_slow − φ_fast) ≥ GAP_MIN=0.05 by ≥3σ.
- G2 attrition-interchangeability: mean(φ_slow − φ_attr_hi) ≥ 0.05 by ≥3σ, with φ_fast ≈ φ_attr.
- G3 anchor-match: sim φ reproduces closed form (1−e^{−βR})/(βR) at both β within 3σ.

## Outcome — APPROVE (exact reproduction)
Reproduced digest `9b7d3b078fa1af3ce2406a245a9422263e09024828656cd06d83f921cfa6d6ff` == disclosed digest (MATCH). Cross-invocation runs byte-identical (both exit 0). Verifier copy diff exit 0; blob + sha256 match source.
- **G1 growth-capacity-drag: PASS** — mean 0.157056 (se 0.000155) ≥ 0.05, **z=689.8382σ**.
- **G2 attrition-interchangeability: PASS** — mean 0.156907 (se 0.000158) ≥ 0.05, **z=676.4328σ**; fast-vs-attr interchange_abs_diff 0.000148.
- **G3 anchor-match: PASS** — φ_slow 0.888962 vs cf 0.889051 |z|=0.9879; φ_fast 0.731906 vs cf 0.732043 |z|=1.1052 (all |z|<3).
- Observed φ_slow 0.888962, φ_fast 0.731906, φ_attr 0.732055; closed-form gap 0.157007. all_pass=true, exit 0. First-failing gate: none.

## ⟲ Previous-session review
Prior loop landed VERDICT 130 (P117 Young–Daly checkpoint interval, +13, sim-lab #204, digest 43a77ca7…) — APPROVE, clean born-red flip, merge-on-green landed with no agent merge call. Standing fleet-lane gap persists: verdict-126 (P113) never landed while V127–V130 merged; flagged, not this slice's scope.

## 💡 Session idea
The discount-cadence habituation trap (venture): when promotions recur on a predictable cadence, buyers learn to defer purchases to the next markdown, shifting the inter-purchase interval distribution rightward and eroding effective price. Sim: model arrivals with a learned "wait-for-discount" hazard that strengthens with observed promo frequency; gate that steady-state realized margin under a fixed-cadence promo policy falls below a randomized/Poisson-timed promo policy by ≥ a floor at ≥3σ, with a closed-form anchor from a geometric-deferral approximation. Distinct from the ramp/attrition mechanics here — it is about demand-side timing, not supply-side capacity.
