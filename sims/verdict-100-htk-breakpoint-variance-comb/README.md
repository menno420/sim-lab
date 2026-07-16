# verdict-100 · htk-breakpoint-variance-comb

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 087
(`## PROPOSAL 087 · 2026-07-16T18:59:26Z · status: sim-ready`, registered spec
`htk-breakpoint-variance-comb`). P087 → V100 under the constant +13 PROPOSAL↔VERDICT
offset.

The head prices a game-balance question: two equal-cost weapon builds differ ONLY in
their per-hit damage distribution — TIGHT ~ Uniform[100,110] (mean 105, low variance) vs
WILD ~ Uniform[75,165] (mean 120, high variance) — and the claim is that "lower mean
damage wins" is NON-MONOTONE in target HP because of a discrete breakpoint (hits-to-kill,
HTK) comb. WILD has the higher mean, yet against certain HP values the LOWER-mean TIGHT
build has the lower (better) mean HTK, and the sign of the advantage combs +,+,−,+,− as
HP sweeps the grid. On a pinned world (single target with HP H, dies when cumulative
realized damage ≥ H; HTK = number of hits to reach H with floor ≥ 1; cohort C=4000 trials
per seed, seeds S=[1,2,3,4,5], HP grid H∈{80,100,140,300,500}), each trial draws a single
stream of MAX_HITS=25 uniforms u_i∈[0,1) from ONE `random.Random(seed)` and BOTH builds
consume the SAME u_i sequence, each mapping u_i to its own [lo,hi] via
damage = lo + u_i·(hi−lo) (COMMON RANDOM NUMBERS — else the paired comparison would be
NULL). The same seed's stream is re-drawn fresh per seed so the identical trials are
evaluated at every H (CRN across H too). P087 pre-registered an ACCEPT rule requiring ALL
four gates R1–R4. The measured run ACCEPTS: R1 (H=100 mean HTK TIGHT < WILD all 5 seeds,
74.90σ), R2 (H=500 mean HTK WILD < TIGHT all 5 seeds, 110.60σ), R3 (every realized HTK ≥ 1
and mean HTK monotone non-decreasing in H for both builds), R4 (comb sign vector
[+,+,−,+,−] matches AND the variance-free control HTK=ceil(H/mean) has WILD ≤ TIGHT at
every H). The measured means reproduce the proposal's disclosed dry-sim calibration
(TIGHT [1,1,2,3,5]; WILD [1.0547, 1.2785, 1.7193, 3.0413, 4.6905]) from an independent
re-implementation — VERDICT ACCEPT, first failing gate None.

## Run (one command)

```
python3 sims/verdict-100-htk-breakpoint-variance-comb/htk_breakpoint_variance_comb_sim.py
```

Exit 0 iff every self-check passes (8/8) AND the twin evaluators agree. Deterministic:
`results.json` and `run-stdout.txt` are byte-identical across process runs — no wall
clock, no network, no git at run time. Stdlib only, CPython 3. The RNG is
`random.Random(seed)` over the in-file seed constants S=[1,2,3,4,5]; both builds share one
per-seed×per-trial uniform stream so TIGHT and WILD are compared on identical draws.

## Structure — two builds + twin evaluators

- **TIGHT** — Uniform[100,110], mean 105, min 100. Low variance; against many HP values
  the number of hits it needs is deterministic (its narrow range never straddles the
  breakpoint), e.g. TIGHT always kills an H=100 target in exactly 1 hit.
- **WILD** — Uniform[75,165], mean 120, min 75, max 165. Higher mean damage but wide
  variance; its per-hit damage frequently straddles a breakpoint, so its HTK is a mixture
  (e.g. at H=100 a fraction of trials need a 2nd hit because the first landed in [75,100)).
- **Common random numbers** — per seed each trial's MAX_HITS=25 uniforms are drawn ONCE
  and the identical stream is mapped by BOTH builds (damage = lo + u_i·(hi−lo)) and reused
  at ALL HP values, so any HTK gap is attributable to the damage distribution, not the
  draws. A per-build matrix fingerprint is compared against the seed's canonical
  fingerprint; a divergence raises `SystemExit("NULL: builds saw different draws")`.
- **Twin evaluators** — an if-chain scorer and an independently transcribed table-driven
  scorer agree on the ruling token AND the first-failing gate over the measured gate
  outcomes — ACCEPT/None both.

## Decision rule (pre-registered, from P087)

**ACCEPT iff R1 AND R2 AND R3 AND R4**, the rule firing in order R1→R2→R3→R4; else
**REJECT** at the first failing gate.

- **R1 reach regime @ H=100:** mean HTK TIGHT < WILD for all 5 seeds AND margin(100) ≥ 3σ.
- **R2 saturation reversal @ H=500:** mean HTK WILD < TIGHT for all 5 seeds AND
  margin(500) ≥ 3σ.
- **R3 well-posedness:** every realized HTK ≥ 1 AND mean HTK monotone non-decreasing in H
  for BOTH builds.
- **R4 comb + control:** (R4a) sign of mean_d(H) over H∈[80,100,140,300,500] equals
  [+,+,−,+,−]; AND (R4b) the deterministic control HTK = ceil(H/mean) (TIGHT mean=105,
  WILD mean=120) has WILD ≤ TIGHT at every H — removing variance shows the stochastic
  TIGHT wins are variance-driven, not mean-driven.

`d_s(H) = meanHTK_WILD − meanHTK_TIGHT` (positive ⇒ TIGHT wins); `mean_d(H)` = mean over
the 5 seeds; `sigma(H) = stdev(d_s, ddof=1)/sqrt(5)`; `margin(H) = |mean_d| / sigma`. Full
grammar and the pinned world in `fixtures.json`.

## Layout

- `fixtures.json` — the pinned world (C, seeds, HP grid, TIGHT/WILD bounds and means,
  MAX_HITS, the damage map and common-random-numbers grammar), the pre-registered gates
  and decision rule, the source proposal header, and the seed-1 H=100 first-20-trial
  uniform streams with HTK-under-both-builds on the identical draws (the committed
  fixture, re-verified each run).
- `htk_breakpoint_variance_comb_sim.py` — the single runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

**VERDICT: ACCEPT** (first failing gate None) — 8/8 self-checks, exit 0, byte-identical
double run, twin evaluators agree ACCEPT/None.
