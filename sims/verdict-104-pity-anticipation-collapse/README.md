# VERDICT 104 — pity-timer anticipation collapse (P091, +13)

Independent, stdlib-only, hermetic verification of idea-engine **PROPOSAL 091**
(`control/outbox.md` · 2026-07-17T05:15:39Z · sim-ready).

## Question
Does the TIGHTEST pity ceiling get DOMINATED by an INTERIOR ceiling K — because a
too-tight ceiling floods the schedule with predictable forced rewards
(variable-ratio anticipation collapse → boredom churn) while a too-loose ceiling
lets long droughts drive frustration churn, so retention peaks at a middle K, not
the kindest-looking one?

## Pinned world (one-liner)
base per-pull reward prob `p=0.12`; pity ceiling `K` guarantees a reward on the
K-th consecutive miss. Cycle length `L=min(G,K)`, `G~Geometric(p)` on {1,2,…};
`L==K ⟺ forced ceiling reward`. Per-cycle quit hazard
`h(L)=min(1, a·max(0,L−L0)+c·1[L==K])` with `L0=6, a=0.03, c=0.14`. retention =
completed reward-cycles survived before the quit. Ceiling grid
`K∈{2,3,4,5,6,7,8,9,10,11,12,14,16}` (Kmin=2 tightest, Kmax=16 loosest),
`N_REPS=30000`, `SEED=20260718`, `cap=8000`.

## Model
Per (K,rep) stream `random.Random((SEED*1000003+rep*97+K*13) mod 2^63)`. Per cycle,
draw pulls 1..K−1 (uniform<p ⇒ natural hit, L=pull, stop; else L=K), then one
uniform for the quit test against h(L). retention = cycles survived. The exact
per-cycle expected hazard `E[h_total](K)=a·E[max(0,L−L0)]+c·(1−p)^(K−1)` is computed
in closed form (no RNG) alongside the Monte-Carlo sweep.

## Pre-registered decision rule (APPROVE iff ALL, order R1→R2→R3→R4)
- **R1** argmax mean-retention is interior (K∉{2,16}) AND beats BOTH endpoints by ≥3σ.
- **R2** exact `E[h_total](K)` strictly unimodal with unique min at interior K*=6
  (strictly ↓ on {2..6}, strictly ↑ on {6..16}); AND `E[h_frust]≡0` for every K≤L0=6
  (tight-arm climb is pure boredom relief), strictly ↑ for K>L0.
- **R3** argmax stays interior across `p∈{0.10,0.12,0.15}` × `a∈{a×0.8,a×1.0,a×1.2}` (9 worlds).
- **R4** dual control: `c=0` → argmax at tight endpoint Kmin=2 (peak vanishes);
  `a=0` → argmax at loose endpoint Kmax=16 by ≥3σ over K=14.

Twin evaluators (ordered if-chain + independent table scan) must agree on the
verdict token AND first-failing gate, else `SystemExit`.

## How to run
```
python3 pity_anticipation_collapse_sim.py
```
Writes `fixtures.json` (first run; committed anchor, drift-guarded), `results.json`
(`sort_keys`), `run-stdout.txt`, and prints the log. 16 self-checks gate exit 0.
Deterministic: keyed `random.Random` per (K,rep); byte-identical across a double run.

## Outcome
**APPROVE** — all four gates R1–R4 clear (R1 K*=6 by 61.4σ/43.1σ; R2 unimodal min
at K=6, E[h_frust]≡0 for K≤6; R3 9/9 interior; R4 c=0→K*=2, a=0→K*=16 at 31.6σ);
twins agree APPROVE/None; 16/16 self-checks; double run byte-identical. The
independent reimplementation reproduces the proposal dry-sim retention sweep and
hazard surface to the decimal. One non-gating finding: the proposal's disclosed
first-12 fixture anchor does not reproduce under the registered stream; the
committed fixture carries the actual anchor (see REPORT). See `REPORT.md` for
margins and digests.
