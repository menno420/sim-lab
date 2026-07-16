# verdict-099 · series-readthrough-saturation-crossover

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 086
(`## PROPOSAL 086 · 2026-07-16T17:48:11Z · status: sim-ready`, idea
`ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md`). P086 → V099
under the constant +13 PROPOSAL↔VERDICT offset.

The head prices a KDP series author's choice between two quality-budget allocations over
an N=4-book multiplicative read-through funnel: CONCENTRATE (all budget on book 1) vs
SPREAD (even across the three transitions). The claim is a SATURATION-DRIVEN CROSSOVER —
concentrate wins at small budgets (its entry-step reach is highest), but the optimum
FLIPS to spread once the entry step saturates at the read-through ceiling r_max, and the
reversal is located AT the world's own stability bound. On a pinned world (entry cohort
C=2000 readers/seed, seeds S=[1,2,3,4,5], base read-through r_base=0.30, ceiling
r_max=0.85 strictly <1, linear map r_k=min(r_max, r_base+slope·b_k) with slope=0.05 so a
single step saturates at b=(0.85−0.30)/0.05=11 budget units, CONCENTRATE bs=(B,0,0) vs
SPREAD bs=(B/3,B/3,B/3), grid B∈{6,11,16,22,33}), each of the C readers draws three
uniforms (u1,u2,u3) ONCE per seed and BOTH allocations are evaluated on that identical
matrix across ALL budgets (COMMON RANDOM NUMBERS — else the paired comparison would be
NULL). A reader advances transition k iff u_k < r_k and books are cumulative (stop at the
first failed transition); revenue = total books bought across the cohort. P086
pre-registered an ACCEPT rule requiring ALL four gates R1–R4. The measured run ACCEPTS:
R1 (B=6 CONCENTRATE > SPREAD all 5 seeds, 29.81σ), R2 (B=33 SPREAD > CONCENTRATE all 5
seeds, 156.67σ), R3 (all realized r_k ∈ [0.30,0.85] and mean revenue monotone
non-decreasing in B for both), R4 (crossover B\*=22 ∈ (11,22] with CONCENTRATE mean
revenue flat at 4336.6 books across B∈{11,16,22,33}). The measured table reproduces the
proposal's disclosed dry-sim calibration to the book from an independent
re-implementation — VERDICT ACCEPT, first failing gate None.

## Run (one command)

```
python3 sims/verdict-099-series-readthrough-saturation-crossover/series_readthrough_saturation_crossover_sim.py
```

Exit 0 iff every self-check passes (7/7). Deterministic: `results.json` and
`run-stdout.txt` are byte-identical across process runs — no wall clock, no network, no
git at run time. Stdlib only, CPython 3.11.15. The RNG is `random.Random(seed)` over the
in-file seed constants S=[1,2,3,4,5]; both allocations share one per-seed uniform matrix
so CONCENTRATE and SPREAD are compared on identical reader draws.

## Structure — two allocations + twin evaluators

- **CONCENTRATE** — bs=(B,0,0): the whole budget on the entry step, r_1=min(r_max,
  r_base+slope·B), r_2=r_3=r_base. Highest per-unit reach while unsaturated, but pinned at
  r_max once b_1≥11.
- **SPREAD** — bs=(B/3,B/3,B/3): even across all three transitions, each r_k=min(r_max,
  r_base+slope·B/3). Every unit still buys reach far longer because each step gets only a
  third of the budget.
- **Common random numbers** — per seed each reader's three uniforms (u1,u2,u3) are drawn
  ONCE and the identical matrix is reused for BOTH allocations and ALL budgets, so any
  revenue gap is attributable to the allocation, not the draws. A per-mode matrix
  fingerprint is compared; a divergence raises `SystemExit("NULL: allocations saw
  different draws")`.
- **Twin evaluators** — an if-chain scorer and an independently transcribed table-driven
  scorer agree on the ruling token AND the first-failing gate over the measured gate
  outcomes — ACCEPT/None both.

## Decision rule (pre-registered, from P086)

**ACCEPT iff R1 AND R2 AND R3 AND R4**, the rule firing in order R1→R2→R3→R4; else
**REJECT** at the first failing gate.

- **R1 reach regime:** at B=6, per-seed rev(CONCENTRATE) > rev(SPREAD) for all 5 seeds
  AND paired margin_sigma (diffs CONC−SPREAD) ≥ 3.
- **R2 saturation reversal:** at B=33, per-seed rev(SPREAD) > rev(CONCENTRATE) for all 5
  seeds AND paired margin_sigma (diffs SPREAD−CONC) ≥ 3.
- **R3 well-posedness:** every realized r_k ∈ [0.30, 0.85] AND mean revenue monotone
  non-decreasing in B for BOTH allocations.
- **R4 crossover at the entry-step ceiling:** B\* (smallest grid B with mean rev(SPREAD)
  ≥ mean rev(CONCENTRATE)) ∈ (11, 22] AND CONCENTRATE mean revenue flat across
  B∈{11,16,22,33}.

`margin_sigma = mean(d) / (sample_std(d, ddof=1)/sqrt(5))` — the paired t-statistic.
Full grammar and the pinned world in `fixtures.json`.

## Layout

- `fixtures.json` — the pinned world (N, C, seeds, r_base/r_max/slope, budget grid,
  allocation shapes, the rate map and common-random-numbers grammar), the pre-registered
  gates and decision rule, the source proposal header, and the seed-1 B=6
  first-50-reader (u1,u2,u3) draws with books-bought under BOTH allocations on the
  identical draws (the committed fixture, re-verified each run).
- `series_readthrough_saturation_crossover_sim.py` — the single runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

**VERDICT: ACCEPT** (first failing gate None) — 7/7 self-checks, exit 0, byte-identical
double run, twin evaluators agree ACCEPT/None.
