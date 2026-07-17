# VERDICT 107 — Refund window as a conversion instrument: net revenue is non-monotone in refund-window length W, peaking at an INTERIOR window (W=13), the day before the window arms wardrobe abusers at W_abuse=14 — longer is not more revenue

> **Status:** `complete`
> 📊 Model: claude-opus-4-8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Verify idea-engine PROPOSAL 094 (+13 → VERDICT 107): a merchant tuning a digital-product refund window would assume longer window = more conversions = more revenue, monotonically. This verdict shows net revenue is NON-MONOTONE in refund-window length W — the safety-net conversion lift (`conv` rises then saturates) trades off against refund cost, which step-jumps once the window arms wardrobe abusers at `W_abuse=14`. The net-revenue-maximizing window is INTERIOR at W=13, the day before the extraction threshold.

## Constraints honored
- Independent stdlib-only reimplementation from the registered spec — aggregated exact-binomial draws (geometric-gap sampling), NOT the proposal's per-buyer Bernoulli loop; same semantics, distinct code path.
- Deterministic: seeded RNG (SEED=20260717), byte-identical double run; results digest intentionally differs from the proposal's disclosed c3cfdae… (independent draws, CONFIRM of gate outcomes not digit-reproduction).
- Twin evaluators (if-chain + table); gates fired R1→R2→R3→R4 in order; verdict per the pre-registered rule, never softened.
- SEEDLESS: pins own SEED=20260717 in-file, NOT a ledger draw; shared seed-ledger block 20261730 untouched.

## What happened
APPROVE — all four gates hold (first-failing gate: none). Independent stdlib-only sim (`sims/verdict-107-refund-window-abuse-threshold/refund_window_sim.py`) reimplemented the pinned world from the registered spec. Twins agree APPROVE/None, 15/15 self-checks, byte-identical double run, MC-vs-analytic max rel-err 0.4108% (band 1.5%).

- R1 interior optimum: PASS — argmax mean-netrev at W=13 (interior idx5), beats W=0 by 96.7σ and W=30 by 20.6σ (need ≥3σ).
- R2 abuse cliff: PASS — last-safe W=13 nets $9740.30 vs first-armed W=14 $8859.90 by 21.2σ despite HIGHER conversion at W=14 (0.05656→0.05709); the +φ=0.08 wardrobe-refund step swamps the conversion gain.
- R3 sweep robustness: PASS — argmax stays interior at all 7 sweep points (φ∈{0.06,0.07,0.08,0.09,0.10}, ρ×{0.8,1.2}); φ=0.09 tips one grid point left to W=12 (still interior), rest W=13.
- R4 dC=0 knockout: PASS — removing conversion lift returns argmax to W=0 by 9.7σ (folk monotone restored), isolating the lift as the cause of the interior optimum.

Digests: results.json sha256 `0d7cfe5c…`, run-stdout.txt sha256 `53ac6279…`, fixtures.json sha256 `7447b8d4…`. `bootstrap.py check --strict` exit 0.

## ⟲ Previous-session review
V106 (P093 metastable retry-storm collapse, APPROVE, #179) landed clean via merge-on-green — the born-red + heartbeat-before-flip choreography held. This session reuses that shape; no regressions observed in the sim-lab lane at boot (origin/main tip 1dfaffff).

## 💡 Session idea
The abuse cliff is a reusable owner-facing knob: net revenue = P·(buyers − refunds), and the marginal window day W→W+1 adds conversion (a real gain) but at W=W_abuse the wardrobe-abuse cohort (+φ=0.08 of buyers) begins refunding, a step of ≈$880/rep that no conversion gain within reach can offset. The optimum is therefore always the last day before the extraction threshold, independent of how far conversion keeps rising past it — a template for auditing any generous-policy dial (refund window, free-trial length, return period) for an abuse-armed step discontinuity before setting it by the folk-monotone intuition.

📊 Model: claude-opus-4-8 · high · verdict-sim
