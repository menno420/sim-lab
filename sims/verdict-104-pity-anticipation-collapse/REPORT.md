# VERDICT 104 — REPORT: pity-timer anticipation collapse (P091, +13)

**Ruling: APPROVE** · first-failing gate: **none** · twins agree APPROVE / None ·
16/16 self-checks pass · double run byte-identical.

## What was tested
idea-engine PROPOSAL 091 claims that on the pinned world a gacha/loot **pity
ceiling** that guarantees a reward after K dry pulls maximizes retention at an
INTERIOR K*, not the tightest — a too-tight ceiling collapses the variable-ratio
schedule into predictable forced rewards (boredom churn) while a too-loose ceiling
lets long droughts drive frustration churn, and removing EITHER hazard collapses
the optimum to the opposite endpoint. This is an independent stdlib-only
reimplementation from the registered spec (keyed per-(K,rep) RNG streams, closed-form
exact-hazard surface, 30000 reps × 13 ceilings), not a copy of the proposal dry-sim.

## Pinned world
`p=0.12` · `K∈{2,3,4,5,6,7,8,9,10,11,12,14,16}` · `L0=6` · `a=0.03` · `c=0.14` ·
`N_REPS=30000` · `SEED=20260718` · `cap=8000`. Cycle `L=min(Geom(p),K)`; `L==K ⟺`
forced ceiling; `h(L)=min(1, a·max(0,L−6)+c·1[L==K])`; retention = cycles survived.

## Per-ceiling retention + exact hazard decomposition (30000 reps)

| K | retention | se | E[h_frust] | E[h_bore] | E[h_total] |
|----:|---------:|------:|-------:|-------:|-------:|
| 2 | 7.203 | 0.0444 | 0.0000 | 0.1232 | 0.1232 ← tightest |
| 3 | 8.200 | 0.0500 | 0.0000 | 0.1084 | 0.1084 |
| 4 | 9.435 | 0.0577 | 0.0000 | 0.0954 | 0.0954 |
| 5 | 10.925 | 0.0659 | 0.0000 | 0.0840 | 0.0840 |
| **6** | **12.568** | **0.0752** | **0.0000** | **0.0739** | **0.0739** ← argmax / min hazard |
| 7 | 11.604 | 0.0704 | 0.0139 | 0.0650 | 0.0789 |
| 8 | 10.971 | 0.0656 | 0.0262 | 0.0572 | 0.0834 |
| 9 | 10.480 | 0.0633 | 0.0370 | 0.0503 | 0.0873 |
| 10 | 9.982 | 0.0609 | 0.0465 | 0.0443 | 0.0908 |
| 11 | 9.522 | 0.0581 | 0.0548 | 0.0390 | 0.0938 |
| 12 | 9.282 | 0.0564 | 0.0622 | 0.0343 | 0.0965 |
| 14 | 8.965 | 0.0545 | 0.0743 | 0.0266 | 0.1009 |
| 16 | 8.614 | 0.0527 | 0.0838 | 0.0206 | 0.1043 ← loosest |

Retention peaks at the interior ceiling K=6 and falls off on both sides. The tight
arm (K≤6) climbs with `E[h_frust]≡0` throughout — the entire climb is pure boredom
relief (the forced-reward fraction `(1−p)^(K−1)` falling), zero frustration confound.
Past K=6 the rising drought tail (frustration) takes over.

## Gate margins
- **R1 interior-dominates** — PASS. argmax = K*=6 beats Kmin=2 by **61.4σ** and Kmax=16 by **43.1σ** (≥3σ each).
- **R2 two-hazard peak** — PASS. exact `E[h_total]` strictly unimodal, unique min at interior K=6 (0.0739); `E[h_frust]≡0` for all K≤6, strictly increasing for K>6.
- **R3 robust-interior** — PASS. 9/9 worlds interior; eight land K*=6, the ninth (p=0.15, a×0.8) lands K*=14 — still strictly interior.
- **R4 dual-control** — PASS. `c=0` (boredom off) → interior peak vanishes, argmax collapses to tight endpoint K*=2 (the K≤L0 arm saturates at the cycle cap, an exact degeneracy — with no boredom, tightening is strictly free); `a=0` (frustration off) → argmax collapses to loose endpoint K*=16 by **31.6σ** over K=14.

## Twins & self-checks
- Twin evaluators: if-chain = APPROVE/None, table = APPROVE/None — **agree**.
- Self-checks: **16/16 pass** (R1–R4 argmaxes and margins, exact-hazard unimodality + K≤L0 zero-frustration, retention-peak/hazard-trough coincidence, dual-control degeneracy, twin agreement).

## Cross-check against the proposal dry-sim
The independent reimplementation reproduces the proposal's disclosed dry-sim to the
decimal: K*=6 retention 12.568 (disclosed 12.568), Kmin=2 7.203 (7.203), Kmax=16
8.614 (8.615); R1 61.4σ/43.1σ (disclosed 61.41σ/43.06σ); the E[h_total] surface is
identical; R3 9/9 with the same p=0.15/a×0.8→K14 corner; R4 a=0 31.6σ (disclosed 31.56σ).

## Finding (non-gating) — disclosed fixture-anchor defect
The proposal discloses a first-12 fixture anchor (K=6, rep 0)
`L=[4,6,6,6,6,3,6,6,6,6,6,6]`. Under the registered per-(K,rep) stream the actual
reproducible anchor is `L=[4,6,6,6,4,6,6,6,6,6,6,5]` (ceiling flags
`[F,T,T,T,F,T,T,T,T,T,T,F]`), diverging at cycles 5, 6 and 12. Because the
aggregate retention sweep and hazard surface reproduce the dry-sim exactly, the
disclosed anchor is an isolated fixture-transcription defect in the proposal, not
a model discrepancy. The committed `fixtures.json` carries the ACTUAL reproducible
anchor; the decision (R1∧R2∧R3∧R4) is unaffected. Recommended: correct the
proposal's disclosed anchor to match.

## Digests
- `results.json`  sha256 `7e8d0ac655799f8785b3767df1164ab101a58c71f71d5f0e4d6981cda55188a3`
- `run-stdout.txt` sha256 `d42c63683827e259137080275e9ab3d05a0294b68fe822914db3047a1bd71e02`
- `fixtures.json`  sha256 `4697f91c2a62d8f17ab256fe63e38c8be1f7c1ea6d8c515cd439518bb6642717`
- Double run: `results.json` and `run-stdout.txt` byte-identical.

## Verdict
**APPROVE.** The pity-timer anticipation collapse holds: the tightest pity ceiling
is dominated by an interior ceiling because a too-tight ceiling collapses the
variable-ratio schedule (boredom churn) and a too-loose ceiling lengthens droughts
(frustration churn); removing either hazard collapses the optimum to the opposite
endpoint. The "tighter is always kinder" heuristic is the dominated choice.
Recommended next: route P091 as a confirmed mechanism; follow-ups = a two-currency
soft+hard pity interaction and a heterogeneous frustration-tolerance mixture (each
a named follow-up, none in scope).
