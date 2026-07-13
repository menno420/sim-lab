# VERDICT 052 — spool-scale go/no-go margin error budget: NULL (table-parity)

> **Source:** idea-engine `control/outbox.md` → PROPOSAL 041 ·
> 2026-07-13T18:01:18Z · status: sim-ready (the source of truth, @ idea-engine
> main 65dcf3a, landed via idea-engine PR #331; idea doc
> `ideas/fleet/spool-scale-go-no-go-margin-2026-07-13.md`). INTAKE 041 →
> VERDICT 052 per the docs/current-state.md offset map (+11 from PROPOSAL 035
> onward). Harvest source: curious-research
> `projects/spool-weight-scale/README.md` @ a9fd5fa (two doc lines quoted
> verbatim in `fixtures.json` — citation only; the runner is hermetic).
> **Run:** `python3 sims/verdict-052-spool-scale-margin/spool_margin_sim.py` —
> stdlib-only, hermetic (reads only its own `fixtures.json`), exit 0, ~14 s,
> `SELF-CHECKS: 15 passed, 0 failed`; stdout + `results.json` byte-identical
> across two full process runs by external diff (sha256: results.json
> `3d735a6e7b07aee499da354483dfdf6f995feb8c79d12329f034e384ac32fdb4`, run
> stdout `3b38dabc92459f32b357748a8bca661ba2cb265d332bf151bc9631954ab32094`);
> cpython-3.11 pinned and asserted. Accepted run = the first complete run of
> the registered pipeline (no fix-forwards).

## The question (registered before any code)

Under the pinned scenario model (integer grams; F ~ U{0..1000}; W = F + E +
ε_s with ε_s ~ U{−5..+5}, the cited ±5 g resolution; F̂ = W − Ê, no clamping;
R-OWN: E ~ U{80..306}, Ê = E + ε_t, ε_t ~ U{−2..+2}; R-TABLE: brand ~
U{201, 256, 225, 224}, Ê = seed, E = seed + δ, δ ~ U{−15..+15}; R-GUESS
control: Ê = 193, E ~ U{80..306}; Ĵ from the mix 1/2 U{5..50} · 3/10
U{51..200} · 1/5 U{201..800}; U = Ĵ + ⌈Ĵ·u/100⌉, u ~ U{0..5}; START iff F̂ ≥
Ĵ + M over M ∈ {0, 5, 10, 15, 25, 40, 60, 100}; RUN-OUT iff started AND
U > F; FEASIBLE iff F ≥ U; FORGONE iff declined AND feasible), what are
RUNOUT(R, M) = P(run-out | started) and FORGONE(R, M) = P(declined |
feasible), with Feas(R) = {M : RUNOUT ≤ 1/100 AND FORGONE ≤ 1/5} and M*(R) =
min Feas(R) — and does the result land REJECT (Feas(R-OWN) = ∅, checked
FIRST), APPROVE (M*(R-OWN) ≤ 25 AND (Feas(R-TABLE) = ∅ OR M*(R-TABLE) ≥
M*(R-OWN) + 15), stability-reproduced), or NULL (four pre-registered axes)?

## Ruling: NULL — table-parity (pre-registered axis ii)

Applied in the pre-registered order:

0. **Agreement gate (validity): PASS.** Max |ArmS − ArmA| over all 24 cells:
   RUNOUT 0.000951 ≤ 3/1000, FORGONE 0.001283 ≤ 1/100 — the run is valid, a
   ruling issues.
1. **REJECT (checked FIRST): does not fire.** Feas(R-OWN) = {0, 5, 10, 15,
   25, 40, 60, 100} — the whole grid, not ∅. Already at M = 0 the measured
   tare clears both bands: RUNOUT(R-OWN, 0) = 18563243/3223848750 ≈
   **0.005758** ≤ 1/100 and FORGONE(R-OWN, 0) = 2606928/3207892435 ≈
   0.000813 ≤ 1/5. **M*(R-OWN) = 0.**
2. **APPROVE: does not fire.** Pocket conjunct holds (M*(R-OWN) = 0 ≤ 25),
   but the habit conjunct fails: Feas(R-TABLE) is also the whole grid —
   RUNOUT(R-TABLE, 0) = 323132657/39971233500 ≈ **0.008084** ≤ 1/100,
   FORGONE(R-TABLE, 0) ≈ 0.003262 ≤ 1/5 — so **M*(R-TABLE) = 0 <
   M*(R-OWN) + 15 = 15**. (The stability conjunct itself was satisfied:
   seed-20261302 reproduces the same class through both twin evaluators.)
3. **NULL — binding axis: table-parity.** M*(R-OWN) ≤ 25 but M*(R-TABLE) <
   M*(R-OWN) + 15 — the pre-registered axis (ii): *"beats the seeded table,
   EVERY TIME" is overstated for go/no-go purposes at the pinned spreads.*

**One-line reason:** at the cited ±5 g resolution both the measured tare and
the seeded brand table already clear the registered bands at ZERO margin
(RUNOUT 0.0058 / 0.0081 ≤ 1/100 at M = 0), so the weigh-it-empty habit buys
0 g of go/no-go margin against the seeded table (< the registered 15 g) —
the habit's measured payoff lives elsewhere: against GUESSING (R-GUESS
control M* = 60) and against a skipped fresh tare (drift moves R-TABLE off
zero, 0 → 5, while R-OWN holds at 0).

Per the proposal's pre-registered NULL consequence, the conditional finding
ships with its named axis and **the cheapest live probe is the next step**:
on the real bench, weigh ONE spool ten times with a fresh tare each time
(pins ε_s), and weigh three empty spools of one brand (pins δ) — zero new
tooling — before the band is re-litigated. On table-parity the docs soften
"every time" to the measured Δ (here: Δ = 0 g at the pinned spreads, on this
metric).

## The measured tables (Arm A exact — the decision arm; Arm S @ 200k in parentheses)

Feasible share (all regimes, M-independent): 58325317/69069000 ≈ 0.8444.

### R-OWN (measured tare, Ê = E + ε_t)

| M (g) | RUNOUT | FORGONE | start rate | ArmS RUNOUT / FORGONE |
|-------|--------|---------|------------|------------------------|
| 0 | 0.005758 | 0.000813 | 0.8487 | 0.005873 / 0.000912 |
| 5 | 0.002674 | 0.003611 | 0.8437 | 0.002650 / 0.003872 |
| 10 | 0.001433 | 0.008278 | 0.8387 | 0.001461 / 0.008513 |
| 15 | 0.000838 | 0.013598 | 0.8337 | 0.000858 / 0.013806 |
| 25 | 0.000232 | 0.024827 | 0.8237 | 0.000237 / 0.024687 |
| 40 | 0.000005 | 0.042350 | 0.8087 | 0.000000 / 0.042205 |
| 60 | 0.000000 | 0.066006 | 0.7887 | 0.000000 / 0.065194 |
| 100 | 0.000000 | 0.113327 | 0.7488 | 0.000000 / 0.112680 |

### R-TABLE (seeded brand table, Ê = seed, E = seed + δ)

| M (g) | RUNOUT | FORGONE | start rate | ArmS RUNOUT / FORGONE |
|-------|--------|---------|------------|------------------------|
| 0 | 0.008084 | 0.003262 | 0.8486 | 0.008422 / 0.003109 |
| 5 | 0.005027 | 0.005989 | 0.8436 | 0.005167 / 0.005969 |
| 10 | 0.002786 | 0.009624 | 0.8387 | 0.002719 / 0.009817 |
| 15 | 0.001410 | 0.014162 | 0.8337 | 0.001290 / 0.014294 |
| 25 | 0.000397 | 0.024987 | 0.8237 | 0.000425 / 0.025189 |
| 40 | 0.000041 | 0.042385 | 0.8087 | 0.000068 / 0.042656 |
| 60 | 0.000000 | 0.066006 | 0.7887 | 0.000000 / 0.066098 |
| 100 | 0.000000 | 0.113327 | 0.7488 | 0.000000 / 0.114610 |

### R-GUESS (control — Ê = 193, no tare knowledge)

| M (g) | RUNOUT | FORGONE | start rate | ArmS RUNOUT / FORGONE |
|-------|--------|---------|------------|------------------------|
| 0 | 0.026062 | 0.031264 | 0.8399 | 0.026828 / 0.030920 |
| 5 | 0.024350 | 0.034177 | 0.8359 | 0.025242 / 0.033612 |
| 10 | 0.022674 | 0.037220 | 0.8319 | 0.023624 / 0.036548 |
| 15 | 0.021035 | 0.040394 | 0.8278 | 0.021986 / 0.039774 |
| 25 | 0.017877 | 0.047132 | 0.8193 | 0.018607 / 0.046647 |
| 40 | 0.013460 | 0.058217 | 0.8061 | 0.013951 / 0.057748 |
| 60 | 0.008244 | 0.074820 | 0.7878 | 0.008420 / 0.074638 |
| 100 | 0.001065 | 0.114280 | 0.7487 | 0.001124 / 0.114340 |

### Feas / M* (bands: RUNOUT ≤ 1/100 AND FORGONE ≤ 1/5)

| regime | Feas | M* |
|--------|------|----|
| R-OWN | {0, 5, 10, 15, 25, 40, 60, 100} | **0** |
| R-TABLE | {0, 5, 10, 15, 25, 40, 60, 100} | **0** |
| R-GUESS (control) | {60, 100} | **60** |

The R-GUESS control lands in the expected direction (M*(R-GUESS) = 60 ≥
M*(R-TABLE) + 15 — "guessing is useless" measured: guessing needs a 60 g
pocket where any tare knowledge needs none; no anomaly flagged). The FORGONE
band (≤ 1/5) never binds anywhere on the grid — even at M = 100 the worst
forgone share is ≈ 0.114; the whole decision is carried by the RUNOUT band.

### Per-job-class RUNOUT splits (reporting — the risk concentrates in large jobs)

R-OWN at M = 0: small 0.002157, medium 0.004591, large **0.026333**; at
M = 25 the large-job class is down to 0.002013 and the other classes are ≈ 0.
The composed risk is a large-job phenomenon (overshoot ⌈Ĵ·u/100⌉ scales with
Ĵ) — a 25 g pocket specifically de-risks large prints even though the bands
never demanded it.

## Drift + sensitivity legs (Arm A exact, seed-20261303 MC confirmations — reporting-only, cannot flip; none flipped)

| leg | M*(R-OWN) | M*(R-TABLE) | note |
|-----|-----------|-------------|------|
| baseline | 0 | 0 | the decision row |
| drift d ~ U{0..8} (skipped fresh tare) | 0 | 5 | prices "re-zero each session": the table regime is pushed off zero margin, the measured tare is not |
| ε_t ∈ {0} | 0 | — | |
| ε_t ∈ {−5..+5} | 0 | — | |
| δ ∈ {−8..+8} | — | 0 | |
| δ ∈ {−30..+30} | — | 5 | doubling the brand-lot spread costs the table one grid step |
| u ∈ {0..2} | 0 | 0 | |
| u ∈ {0..10} | 5 | 5 | heavier overshoot moves BOTH regimes together — no straddle |
| job mix {1/4, 1/4, 1/2} | 5 | 5 | large-heavy mix moves both together |

**Sensitivity straddle check: NONE.** No reporting-only pair flips any
primary conjunct (the habit conjunct is False on the baseline and stays
False on every variant; the pocket conjunct stays True; the REJECT conjunct
stays False). MC confirmation max deltas (20k per cell) vs the exact
variants: |ΔRUNOUT| ≤ 0.00243, |ΔFORGONE| ≤ 0.00713 — consistent with the
sampling noise at n = 20,000.

## Gates (all green — 15 self-checks, 0 failed)

Six-scenario hand fixture verified at startup against the shared scenario
evaluator (all 7 outputs per scenario); zero-error identity leg (ε_s = ε_t =
δ = u = 0, Ê = E: RUNOUT ≡ 0 for all M and FORGONE(0) = 0 — exact zeros);
convolution spot-check — the net-error collapse reproduces the direct
product enumeration EXACTLY (Fraction equality) on all 48 pinned cells
(Ĵ ∈ {20, 100, 400, 800} × u ∈ {0, 5} × 3 regimes × M ∈ {0, 25}), so the
collapse is permitted and the ruling rides it; exact monotonicity in M
(RUNOUT non-increasing, FORGONE non-decreasing) on all 25 (table, arm)
combinations — hard gate; arm agreement gate (above); draw-count sentinels
exact (main 4,000,000 = 200k × (7+7+6); stability 400,000; reporting
2,220,000; aux seed 20261304 ZERO draws — never read); twin
independently-written decision evaluators (Fraction/Feas-set logic vs pure
integer cross-multiplication M*-scan) agree on the main and stability
inputs; stdout + results.json byte-identical across two full process runs
by external diff; CPython 3.11 pinned and asserted. Seeds 20261301–304
verified distinct and strictly above the V051 registry high-water 20261300
— new high-water 20261304.

**Stability leg (seed 20261302, 20k/regime):** within the same agreement
gate against Arm A on all cells, and both twin evaluators return the same
class (null / table-parity) as the Arm-A ruling — the ruling is
stability-reproduced.

**Hand-fixture disclosure:** the idea doc's scenario 2 (F = 100, Ĵ = 100,
u = 3 → U = 103) carries a trailing tag "feasible"; under the PROPOSAL 041
block's own pinned convention (FEASIBLE iff F ≥ U) it is INFEASIBLE
(100 < 103) — a started run-out is definitionally infeasible. The outbox
block is the registered source of truth, so the fixture pins the
convention-consistent expectation and the discrepancy is disclosed here
(and in `fixtures.json`), not silently absorbed. No other scenario is
affected; the gate passed on all six.

## Reproduce

```
cd sim-lab
python3 sims/verdict-052-spool-scale-margin/spool_margin_sim.py   # run 1
sha256sum sims/verdict-052-spool-scale-margin/results.json        # 3d735a6e…
python3 sims/verdict-052-spool-scale-margin/spool_margin_sim.py   # run 2 — byte-identical
```

One command, no flags; stdlib-only; the runner reads only its own
`fixtures.json`. Arm A is platform-independent exact rationals; Arm S is
pinned to CPython 3.11 (asserted at startup). Committed accepted-run
outputs: `results.json`, `run-stdout.txt`.

## Boundaries (registered)

- **Invented widths:** ε_t (±2), δ (±15), u (0–5%), and the job mix carry NO
  bench datapoint anywhere in the fleet (the source repo's own sketch has
  never compiled) — the sweeps bracket scale, not shape. The named live
  probe (ten weighings of one spool with fresh tares; three empties of one
  brand) measures ε_s and δ directly at zero new tooling — and is exactly
  the pre-priced NULL next step.
- **Independence:** a shared calibration-gain bias would partially cancel in
  F̂ = W − Ê under R-OWN, making the real measured-tare regime BETTER than
  modeled — independence is conservative against APPROVE's habit-pays
  conjunct. Note the direction: correcting it would make R-OWN stronger but
  cannot rescue the habit conjunct here, because parity failed on the
  R-TABLE side clearing the band, not on R-OWN missing it.
- **Pinned world:** 1 kg spools, uniform F over {0..1000}; 250 g / 2.3 kg
  spools and clustered real shelves are named out of registered scope. The
  verdict is a property of THIS registered frame; live bench evidence
  supersedes wherever a future measured frame disagrees.

## What a reader does differently

The two harvested doc lines get their honest numbers, routed lane-side per
Q-0260 (this repo never edits curious-research files): "leave yourself
margin" is, at the pinned widths, already satisfied at a fresh measured or
seeded tare with a 0 g pocket against the 1%-run-out band — the honest
pocket advice for LARGE jobs is ≈ 25 g (the per-class split), and the drift
row prices the "re-zero each session" rule (skipping it costs the table
regime its zero margin). "Beats the seeded table, every time" softens to
the measured Δ = 0 g on the go/no-go metric at the pinned spreads — the
habit's real measured payoffs are vs guessing (60 g) and vs stale tares.
The bench probe (ε_s, δ) is the named, pre-priced step before any
re-litigation of the band.
