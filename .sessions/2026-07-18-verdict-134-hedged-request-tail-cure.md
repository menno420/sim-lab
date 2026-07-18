# VERDICT 134 — hedged-request tail cure

Reproduce PROPOSAL 121 (round-28 FLEET-slot opener, P121 → V134, +13): the "tail at scale" hedged-request cure (Dean & Barroso, CACM 2013). A request served by ONE replica has a heavy-tailed service time whose 99th percentile is dominated by the occasional straggler. The folk fix — "to kill the tail you must duplicate every request and take the first answer" — halves the tail but DOUBLES the load (+100%), and the folk belief holds that any delay before the second copy "leaves latency on the table." Both are wrong. The HEDGED request defers the second copy to a small delay d = the 95th percentile of the service-time distribution: send the primary at t=0, and only if it has not answered by d send a secondary to an INDEPENDENT replica — response = min(primary, d + secondary). The hedge fires on only P(S>p95) ≈ 5% of requests (extra load ≈0.05, not 100%), yet the p99 latency COLLAPSES because a straggler primary is almost always rescued by a fast independent secondary (the hedged tail survives only when BOTH copies straggle, ≈p²≈0.0025, past p99). So the tail cure is almost free; the last sliver of tail benefit that full duplication buys BEYOND the p95 hedge costs ~20× the load (the knee), and fleet dispatch should tie-hedge after ~p95 rather than duplicate.

> **Status:** `in-progress`
> 📊 Model: high · review/verify

Born red by design: this card lands `in-progress` in the first commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the final commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (ORDER 003). No gate is bypassed. PHASE 1 (reproduction + independent digest audit) is under way; the PHASE-2 commit flips the card to `complete` on the audited ruling and re-stamps the status heartbeat to V134 high-water.

## Objective
Reproduce the committed P121 reference verifier byte-identical under its pinned world (SEED=20260717, MEAN_FAST=10.0, MEAN_SLOW=200.0, P_STRAGGLER=0.05, N_REQUESTS=20000, TRIALS=200, HEDGE_PCTL=0.95, CAPTURE_MIN=0.80, LOAD_MAX=0.08, SIGMA_GATE=3.0) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest, (b) all three gates hold as disclosed, in order G1→G2→G3, (c) cross-invocation and in-process double runs are byte-identical. Source header (verbatim): `## PROPOSAL 121 · 2026-07-18T06:31:17Z · status: sim-ready`.

## GROUNDING (verified at HEAD)
- idea-engine HEAD `5c26a043c003ccb05f619f7c67b44a70461e7c0d` (#542); reference verifier `ideas/fleet/hedged_request_tail_cure.py` — git blob `5bd1866e2432bd0e6f90289ea4bac7971e32bbfd`, sha256 `be975454449d39e75f6bf543e952622e3df8966921190f16667d8fb2cd82f1c6`, 254 lines / 11916 bytes. Source: https://github.com/menno420/idea-engine/blob/main/ideas/fleet/hedged_request_tail_cure.py
- Domain reference: Dean & Barroso, "The Tail at Scale", Communications of the ACM 56(2):74-80, 2013 — https://cacm.acm.org/research/the-tail-at-scale/ (the hedged-request / tied-request tail cure).
- sim-lab work branch cut from origin/main HEAD `cdb94b51aad0a25bcb5bbc6a50a2381e139224f0` (#207).
- DIGEST POSTURE: SELF-FIELD / stdout-line (the P119/V132/V133 posture). The verifier computes the digest over `json.dumps(results, sort_keys=True, separators=(",",":"))` BEFORE adding the `results_sha256` field, then writes the on-disk `hedged_request_tail_cure_results.json` pretty-printed (indent=2, sort_keys) WITH the field — so `sha256sum` of the on-disk file is NOT the digest; the disclosed digest is the value printed on the `Results-JSON sha256:` stdout line (and stored in the file's own `results_sha256` field).
- Offset authority: idea-engine control/outbox.md P121 `depends:` ledger (P121→V134 +13, "Offset pinned") + control/status.md baton — not docs/current-state.md (dormant snapshot through V059).

## Constraints honored
Stdlib-only (random, math, json, hashlib); verifier copied byte-identical (diff exit 0, blob + sha256 match); pinned SEED unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed.

## Gate plan (disclosed → reproduced)
- G1 hedge collapses the tail (headline): per-trial mean(p99_base − p99_hedge) > 0 by ≥3σ (/se convention) — deferring the hedge to the p95 delay strictly and largely lowers the 99th-percentile latency.
- G2 the knee: (a) mean capture ratio (p99_base−p99_hedge)/(p99_base−p99_dup) ≥ CAPTURE_MIN=0.80 by ≥3σ AND (b) mean hedge-fire fraction ≤ LOAD_MAX=0.08 (fires on ~p95=5% of requests) while full-dup costs +100% load.
- G3 almost-free efficiency: mean(red_hedge/load_hedge − red_dup/load_dup) > 0 by ≥3σ — the p95 hedge's tail-cut-per-unit-load strictly exceeds full duplication's.

## Outcome — APPROVE (exact reproduction)
Reproduced digest `a76ef737962bd9c3663399dc19425dc3ca697c6d8775be682c3a128aa76b1b4e` == disclosed digest (MATCH). Cross-invocation A + B both printed the identical digest and an in-process double-run produced identical per-trial draws (all exit 0; cross-invocation stdout diff exit 0 AND results-json diff exit 0). Verifier copy diff exit 0; blob `5bd1866e` + sha256 `be975454` match source.
- **G1 hedge collapses the tail: PASS** — per-trial mean tail-cut **261.912252** (se 0.923706) > 0 by **z=283.5451σ**; single-replica p99 **322.613793** → hedge@p95 p99 **60.701541**.
- **G2 the knee: PASS** — (a) mean capture ratio **0.889581** (se 0.000377) ≥ 0.80 by **z_capture=237.7642σ** AND (b) mean hedge-fire load **0.04995** ≤ LOAD_MAX=0.08 (fires on ~p95=5% of requests) while full-dup costs +100%.
- **G3 almost-free efficiency: PASS** — mean efficiency edge (red_hedge/load_hedge − red_dup/load_dup) **4949.106846** (se 17.525819) > 0 by **z=282.3895σ**; hedge tail-cut-per-unit-load **5243.488535** vs full-dup **294.381688** (ratio **17.811871×**).
- Anchors: mixture p95=45.388281, mixture p99=321.887582, full-dup extra load=1.0. Sim: mean p99 base 322.613793, hedge 60.701541, dup 28.232104. all_pass=true, exit 0. First-failing gate: none.

## ⟲ Previous-session review
Prior loop landed VERDICT 133 (P120 German-tank MVUE, +13, sim-lab #207, digest 37cea2bf…) — APPROVE, clean born-red flip, merge-on-green with no agent merge call. That slice closed round-27 on the verdict side at the UNRELATED slot; this slice REOPENS round-28 at the FLEET slot (P121 → V134).

## 💡 Session idea
Hedge delay as a control knob under load-dependent stragglers: P121 pins d at the STATIC p95 of the service-time mixture, but in a real fleet the straggler fraction P_STRAGGLER rises with utilization, so a fixed d drifts off the true p95 exactly when the tail matters most — hedging too little under load, or firing too often (blowing the LOAD_MAX budget) when the fast component slows. Sim: gate that an adaptive d tracking the RUNNING empirical p95 holds the capture ratio ≥0.80 while keeping hedge-fire load ≤0.08 across a rising-P_STRAGGLER sweep, whereas the static-d hedge breaches one of the two by ≥3σ at the high-load end — isolating the hedge's robustness to the load-dependence that P121's fixed mixture assumes away.
