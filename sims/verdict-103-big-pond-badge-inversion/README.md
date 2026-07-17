# VERDICT 103 — big-pond badge-starvation inversion (P090, +13)

Independent, stdlib-only, hermetic verification of idea-engine **PROPOSAL 090**
(`control/outbox.md` · 2026-07-17T02:45:45Z · sim-ready).

## Question
On the pinned world, does placing a single title in the **maximum-audience**
browse category get DOMINATED by an interior pond — because a rank-K
category-bestseller badge multiplier is unattainable where committed competition
rises faster than traffic?

## Pinned world (one-liner)
`C=9` browse categories, `T=[800,1000,1200,1400,1600,1800,2000,2200,2400]` browse/day,
`p0=0.01`, `v0=5.0/day`, badge lift `b=1.5` (effective conv `= p0*(1+b*badge)`),
committed rank-K competition `g=[6,9,13,18,24,31,39,48,58]`, badge earned iff
`v0+T_c*p0 ≥ g_c` → `badge=[1,1,1,1,0,0,0,0,0]` (crossover at index 4),
`H=90`, `N_REPS=400`, `SEED=20260717`, exact Poisson daily draws.

## Model
Daily sales in category `c` ~ `Poisson(v0 + T_c*p_eff)` with
`p_eff = p0*(1+b*badge_c)` (exact thinning of a `Poisson(T_c)` browse stream plus an
independent `Poisson(v0)` baseline). Horizon total = sum of `H` independent daily
draws. Badge is **earned, not given**: where competition outruns traffic the badge
is unattainable and the multiplicative lift never applies, so the biggest pond
starves.

## Pre-registered decision rule (APPROVE iff ALL)
- **R1** argmax mean-sales is interior (idx ≠ 8) AND beats idx 8 by ≥ 3σ.
- **R2** last-badged pond (idx 3) outsells first-unbadged pond (idx 4) by ≥ 3σ,
  despite idx 4 carrying MORE browse traffic.
- **R3** argmax stays interior across `b∈{1.0,1.25,1.5,1.75,2.0}` (nominal g) and
  `g×{0.9,1.1}` (nominal b) — union of the two 1-D sweeps (7 points).
- **R4** with `b=0` (badge off) argmax returns to idx 8 (max audience) by ≥ 3σ.

Twin evaluators (ordered if-chain + independent table scan) must agree on the
verdict token AND first-failing gate, else `SystemExit`.

## How to run
```
python3 big_pond_badge_inversion_sim.py
```
Writes `fixtures.json` (first run; committed anchor), `results.json`
(`sort_keys`), `run-stdout.txt`, and prints the log. 14 self-checks gate exit 0.
Deterministic: sha256 string-keyed `random.Random` per (regime,rep,category);
byte-identical across a double run.

## Outcome
**APPROVE** — all gates R1–R4 clear; 14/14 self-checks pass; twins agree
APPROVE / first-fail None. The maximum-audience pond (idx 8) is dominated by the
interior last-badged pond (idx 3). See `REPORT.md` for margins and digests.
