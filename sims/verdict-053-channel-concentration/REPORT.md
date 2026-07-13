# VERDICT 053 — channel concentration vs diversification at fixed build budget

**Ruling: APPROVE** (pre-registered rules applied in order, REJECT checked FIRST).

Serves idea-engine PROPOSAL 042 (`control/outbox.md` @ 94fd30c, landed via
idea-engine PR #333; idea doc
`ideas/venture-lab/channel-concentration-vs-diversification-2026-07-13.md` @
8aad290). Harvest grounding (citation only — the runner is hermetic):
menno420/venture-lab @ be6c75d — the products batch's own Kill-Rule-2 note
("all three ride the same saturated agent-ops/dev-article funnel that has
produced 0 organic sales across 7 click-queued products so far…") and the
ledger's "0 organic sales as of 2026-07-13" line.

Run: `python3 sims/verdict-053-channel-concentration/channel_sim.py`
(stdlib-only, hermetic — reads only its own `fixtures.json`; CPython 3.11
pinned and asserted; ~32 s; stdout + results.json byte-identical across two
full process runs by external diff; results.json sha256
`8c149d8d1247286995bbda098ddecc4705ae49d02f6c75cbf7e685fd2bb210c0`).

## The question

At the batch's own fixed cycle budget (T = 180k tokens, incumbent build 60k,
untested-channel build 90k), does CONCENTRATE (3 incumbent builds/cycle, 12
exposures over H = 4) beat SPLIT (2 untested builds/cycle round-robin
u1,u2,u3 -> (3,3,2), zero incumbent) and EXPLORE-THEN-COMMIT (probe u1+u2,
then u3+incumbent, commit cycles 3-4 to the argmax posterior-mean channel) on
**P_any = P(>=1 organic sale by horizon end)**, across 9 pre-registered prior
cells = {SKEPTIC, NEUTRAL, HOPEFUL} optimism pmfs x incumbent evidence
n_inc in {7, 3, 1} exposures with 0 successes?

## Decision table (Arm A — seedless exact Fractions; decision-bearing alone)

CON = P_any(CONCENTRATE) · DIV = max(P_any(SPLIT), P_any(ETC)) — SPLIT carries
DIV in **all nine cells**.

| cell | CON | DIV | DIV − CON | >= 1/100? |
|---|---|---|---|---|
| SKEPTIC/n7 | 0.124981 | 0.339255 | 0.214274 | yes |
| SKEPTIC/n3 | 0.173584 | 0.339255 | 0.165671 | yes |
| SKEPTIC/n1 | 0.224560 | 0.339255 | **0.114695** (min) | yes |
| NEUTRAL/n7 | 0.268186 | 0.703350 | 0.435164 | yes |
| NEUTRAL/n3 | 0.391416 | 0.703350 | 0.311933 | yes |
| NEUTRAL/n1 | 0.504337 | 0.703350 | 0.199013 | yes |
| HOPEFUL/n7 | 0.384866 | 0.715888 | 0.331022 | yes |
| HOPEFUL/n3 | 0.504360 | 0.715888 | 0.211528 | yes |
| HOPEFUL/n1 | 0.594426 | 0.715888 | 0.121462 | yes |

Exact rationals for every cell are in `results.json`
(`verdict_053.cells_con_div`); e.g. the minimum margin SKEPTIC/n1 =
915724491130827228084799929/7984000000000000000000000000.

## Rule trace (pre-registered order)

- **REJECT (checked FIRST)**: DIV − CON < 1/100 in >= 7 of 9 cells — **does
  not fire** (0 of 9 cells below the margin).
- **APPROVE**: DIV − CON >= 1/100 in >= 7 of 9 (measured 9/9) AND in >= 2 of
  the 3 n_inc = 1 cells (measured 3/3: 0.1147 / 0.1990 / 0.1215) AND the
  seed-20261306 stability leg reproduces the ruling (it does — the same twin
  evaluators return APPROVE-CELLS on the stability MC table; worst
  |ArmS − ArmA| on that leg 0.01195 <= 15/1000) — **fires**.
- Twin independently written evaluators (Fraction comprehension vs integer
  cross-multiplication) agree on both the Arm-A and stability inputs.

**The landing:** at honest costs (a 1.5x per-build premium, a one-third
exposure tax — 8 exposures vs 12), spreading the batch's fixed budget across
three fresh channels beats deepening the 0-for-n_inc incumbent in every
registered belief cell. The mechanism, read off the table: P_any in a single
channel saturates against the channel's dead-rate mass (p = 0 carries 1/2
SKEPTIC / 1/5 NEUTRAL / 1/10 HOPEFUL prior mass), so one channel caps
CONCENTRATE at 1 − P(incumbent dead), while three independent rate draws
hedge the dead-channel event (e.g. SKEPTIC: P(all three fresh channels dead)
= 1/8 vs P(incumbent dead | 0/1) ~ 0.53). Diversification's win is
option-value over dead-channel risk, not exposure count.

## Reporting-only legs (CANNOT flip; did not)

- **SPLIT-vs-ETC decomposition:** SPLIT carries DIV in all 9 cells; ETC sits
  between (its probe round sends the committed budget to u1 far more often
  than home: committed-incumbent share 1.3%–7.9% across cells — the
  0-successes handicap keeps the incumbent's posterior mean below a fresh
  probe's posterior mean unless every probe fails too).
- **E_hits (secondary, never decision-bearing):** the comparison inverts in
  places — e.g. NEUTRAL/n1: CONCENTRATE E_hits 1.590 > SPLIT 1.392 (ETC
  1.710) while CONCENTRATE's P_any is 0.199 lower — concentration buys more
  expected sales conditional on a live channel, diversification buys the
  higher chance of at least one. The registered metric is P_any.
- **c_new in {60k, 120k}:** at equal cost (60k) the direction check held in
  every n_inc = 7 cell (SPLIT >= CONCENTRATE — no anomaly fired); min margin
  0.1906. At 2x (120k) the cell-count conjuncts still land APPROVE-CELLS
  (no sensitivity straddle), but the honest boundary shows: HOPEFUL/n1 flips
  sign (CON 0.5944 vs DIV 0.5786, −0.0159) — under the most optimistic prior,
  the weakest evidence reading, and a doubled fresh-channel premium,
  concentration edges ahead; SKEPTIC/n1 is carried by ETC there (0.2553 vs
  SPLIT 0.2190).
- **H in {2, 8}:** APPROVE-CELLS at both; min margins 0.0556 (H = 2,
  HOPEFUL/n1) and 0.1609 (H = 8). Horizon monotonicity gate exact in Arm A
  and by-construction (nested prefix draws) in Arm S: clean.

## Gates (all green; run-invalid on any failure)

297 self-checks, 0 failed, exit 0. Hand fixture F1–F6 (SKEPTIC/n1 posterior
(800, 392, 180, 75, 50)/1497; NEUTRAL 2-exposure P_any = 14171/50000;
committer tie -> incumbent, tested both as the bare tie rule and end-to-end
at a point-mass prior; SPLIT counts (3, 3, 2); budget arithmetic
floor(180/60) = 3 / floor(180/90) = 2 / 150k + 30k lost; point-prior identity
1 − (9/10)^12); degenerate-zero gate (point mass at 0 -> exact zeros, all
policies); horizon monotonicity (exact, both arms); equal-cost direction
check (no anomaly); arm agreement — main leg (seed 20261305, 200,000/cell)
worst |ArmS − ArmA| = 0.00199 <= 5/1000, stability (20261306, 20,000/cell)
worst 0.01195 <= 15/1000, all reporting legs (20261307, 20,000/cell) within
15/1000; per-leg draw-count sentinels exact (main 57,753,986 · stability
5,775,514 · reporting 6,840,000 / 4,515,444 / 10,846,266 / 5,775,302 — each
equal to its independently accumulated per-trajectory total); aux seed
20261308 ZERO draws; twin decision evaluators agree; two-process
byte-identity by external diff.

## Boundaries (stated with the ruling)

- **Independence (the named most-likely flip, GENEROUS TO APPROVE):** channels
  are modeled independent. If the 0-sales evidence indicts the products or
  market appetite rather than the channel, fresh channels inherit the
  handicap and diversification's option value collapses toward REJECT. This
  APPROVE must be read net of that direction.
- **Invented constants:** c_new = 1.5x, H = 4, K = 3, the three pmfs, and the
  n_inc = 3 midpoint carry no measurement (disclosed in the registration; the
  c_new/H sensitivity pairs bracket scale, and the 2x leg locates the real
  cost boundary at the HOPEFUL/n1 corner).
- **Scope:** success = the >=1-organic-sale leg only (the reads/inbound
  kill-rule leg is out of registered scope); rates stationary (the doc's own
  "saturated" hints at decay — out of scope, named); multiple sales per
  product uncounted (E_hits secondary only).
- **Application guard (consumer-side):** the verdict conditions on "0 organic
  sales as of 2026-07-13" — an incumbent organic sale before application
  (e.g. the T+7 checkpoint 2026-07-19 or T+14 kill-rule 2026-07-26) stales
  the conditioning and the lane applies nothing without a re-run.
- **ETC generalization (reporting legs only, disclosed):** the sensitivity
  legs generalize the pinned ETC schedule by deterministic greedy probe
  packing; at the registered base (c_new = 90k, H = 4) the code reproduces
  the pinned schedule exactly (asserted as a gate).

## Files

- `fixtures.json` — every registered constant, committed BEFORE the runner.
- `channel_sim.py` — both arms + gates + twin evaluators, one command, no flags.
- `results.json` — full exact tables (all legs), rule trace, draw counts.
- `run-stdout.txt` — the accepted run's stdout (byte-identical re-run verified).
