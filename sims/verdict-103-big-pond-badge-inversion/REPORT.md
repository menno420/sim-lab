# VERDICT 103 — REPORT: big-pond badge-starvation inversion (P090, +13)

**Ruling: APPROVE** · first-failing gate: **none** · twins agree APPROVE / None ·
14/14 self-checks pass · double run byte-identical.

## What was tested
idea-engine PROPOSAL 090 claims that on the pinned world a single title in the
**maximum-audience** browse category (idx 8, `T=2400`) is DOMINATED by an interior
pond, because the rank-K category-bestseller badge multiplier is unattainable
where committed competition rises faster than traffic. This is an independent
stdlib-only reimplementation from the registered spec (exact-Poisson daily draws,
sha256 string-keyed RNG streams, 400 reps × H=90), not a copy of the proposal
dry-sim.

## Pinned world
`C=9` · `T=[800,1000,1200,1400,1600,1800,2000,2200,2400]` · `p0=0.01` · `v0=5.0` ·
`b=1.5` · `g=[6,9,13,18,24,31,39,48,58]` · badge `= [1,1,1,1,0,0,0,0,0]` (crossover
at index 4) · `H=90` · `N_REPS=400` · `SEED=20260717`.

## Per-category horizon sales (H=90, 400 reps)

| idx | T | badge | mean | se |
|----:|----:|:---:|---------:|-------:|
| 0 | 800 | 1 | 2251.262 | 2.3347 |
| 1 | 1000 | 1 | 2700.932 | 2.7224 |
| 2 | 1200 | 1 | 3153.472 | 2.6115 |
| **3** | **1400** | **1** | **3605.625** | **3.1823** ← argmax |
| 4 | 1600 | 0 | 1894.335 | 2.1555 |
| 5 | 1800 | 0 | 2071.613 | 2.4189 |
| 6 | 2000 | 0 | 2251.350 | 2.4440 |
| 7 | 2200 | 0 | 2424.730 | 2.3471 |
| 8 | 2400 | 0 | 2613.573 | 2.5613 ← max-audience |

The interior last-badged pond (idx 3, `T=1400`) is the global optimum; the
max-audience pond (idx 8, `T=2400`) sits well below it. The badge cliff at index 4
is stark: idx 4 (`T=1600`, MORE traffic than idx 3) collapses to 1894 once the
badge is lost.

Control (badge off, `b=0`): argmax returns to idx 8, mean **2609.977** — the folk
"biggest pond wins" monotone is restored.

## Gate margins

- **R1 interior-dominates** — PASS. argmax = idx 3 beats idx 8 by **242.8σ** (≥ 3 required).
- **R2 badge-cliff** — PASS. idx 3 outsells idx 4 (first-unbadged, MORE traffic
  `T=1600 > 1400`) by **445.2σ**.
- **R3 robust-interior** — PASS. 7/7 sweep points interior:
  `b=1.0→idx3 · b=1.25→idx3 · b=1.5→idx3 · b=1.75→idx3 · b=2.0→idx3 · g×0.9→idx3 · g×1.1→idx2`.
- **R4 badge-off-control** — PASS. with `b=0` argmax returns to idx 8 by **50.2σ**.

## Twins & self-checks
- Twin evaluators: if-chain = APPROVE/None, table = APPROVE/None — **agree**.
- Self-checks: **14/14 pass** (badge vector, crossover index, argmax interior,
  R1–R4 margins, control badge all-zero, twin agreement).

## Digests
- `results.json`  sha256 `77c7c6f93d67996c6eae165716f37b276a406523848ab4d794c989a3284bb61d`
- `run-stdout.txt` sha256 `d36343580bbdb76d7f12da6b7cad805b7450f079cab295aa2c118ea9c425ad48`
- `fixtures.json`  sha256 `7e32097aa001aa52cdf193c53fb216ebf59708d165b497f10ff1ffd99d78c6c8`
- Double run: `results.json` and `run-stdout.txt` byte-identical.

## Verdict
**APPROVE.** The badge-starvation inversion holds: the maximum-audience browse
category is dominated by an interior badgeable pond because the earned-badge
multiplier is unattainable where competition outruns traffic. Recommended next:
route P090 as a confirmed mechanism and open a variance-weighted category
ALLOCATOR (portfolio of titles across ponds under badge contention).
