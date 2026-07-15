# verdict-082 — the WIP-cap dryness floor (INTAKE 069)

Prices idea-engine PROPOSAL 069's committed pair where it lives: the
owner's "WIP cap 3, backpressure holds" (ORDER 004, idea-engine
`control/inbox.md:50`) against ORDER 003's "the PROPOSAL->VERDICT
pipeline is never dry" (`inbox:31`), with two lived DRY events already on
the committed record (`inbox:188`, `inbox:219`). The pipeline is modeled
as what the orders literally describe: a CLOSED 2-station cyclic loop
(CONWIP) — K tokens between drafting and verdicting, state n =
unverdicted in-flight, births at rate lambda iff n < K, deaths at rate mu
iff n > 0, r = lambda/mu, truncated-geometric stationary law
pi(j) = r^j / sum r^i. DRY = the committed record's own "no unverdicted
proposal exists" (n = 0). Grid K in {1, 2, 3, 4, 6, 12} x r in {1/2, 3/4,
1, 4492/3973, 40428/30847, 2}, decision cell (K = 3, r_hat = 4492/3973)
— the committed cap at the seat's own measured burst cadence (S_d =
3973/2 s from the P064-P068 header gaps 1622/2674/2263/1387; S_v = 2246 s
from the one committed append->finalization pair P065 -> V078). Judged
against pre-registered bands, REJECT-first (D(3, r_hat) >= 1/10 AND
D(3, r) >= 1/20 at every grid r AND D(12, r_hat) >= 1/40 AND
B(3, r_hat) >= 1/5), then INVALID, then APPROVE (D <= 1/50 AND
B <= 1/20), then NULL on named axes. The runner is hermetic — it reads
ONLY `fixtures.json` (committed before the runner); zero repo/network
reads at verdict time; the MEASURED fixture constants were re-verified
firsthand at idea-engine origin/main before the fixture was written.

## Run

```
python3 sims/verdict-082-wip-cap-dryness-floor/wip_cap_dryness_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, < 1 s. Every
decision number is an exact rational; the only seeded arm (R) is
reporting-only and its sole gates are the draw-count sentinels and exact
reproducibility.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  069 block / idea file (the loop model, the K x r grids, the pinned gap
  integers and the anchor-derivation rule, the F3 census anchors
  including the exact D(12, r_hat) rational pin, the decision bands
  {1/10, 1/20, 1/40, 1/5, 1/50}, the F4 hand worlds, the F5 swap
  symmetry, Arm-R parameters {100,000 main / 20,000 stability cycles,
  three service shapes}, seeds 20261610-613), plus fixture-level
  conventions C1-C11 — committed BEFORE the runner existed.
- `wip_cap_dryness_sim.py` — three-arm runner: Arm A seedless
  truncated-geometric closed form (exact Fractions; decision-bearing),
  Arm B INDEPENDENTLY-WRITTEN twin (builds the (K+1)-state generator Q
  and solves pi*Q = 0, sum(pi) = 1 by Fraction Gaussian elimination —
  never via the closed form; second decision evaluator), Arm R seeded
  discrete-event traces of the literal loop at the decision cell under
  three service shapes at the same pinned means (exponential /
  deterministic / measured burst-gap empirical mix; main 20261610,
  stability 20261611, presentation 20261612, aux 20261613 NEVER read).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the exact D/B/E/W surfaces, the three theorem
  verifications (T1 impossibility, T2 frontier, T3 balanced knee), the
  swap symmetry, the deterministic-service exhibit beside its Arm-R
  trace, the K*(r, d) safe-cap table, gates, anomalies, boundaries, the
  pre-registered consequence.

## Ruling

**REJECT** (see REPORT.md; the ruling token is issued by the twin
evaluators per the pre-registered order REJECT -> INVALID -> APPROVE ->
NULL). All four REJECT clauses clear at the decision cell exactly as
disclosed: D(3, r_hat) = 62712728317/304425042745 ~ 0.20600 >= 1/10
(2.06x), grid-worst D(3, 2) = 1/15 >= 1/20 (1.33x), D(12, r_hat) ~
0.03321 >= 1/40 (1.33x), B(3, r_hat) = 90639863488/304425042745 ~
0.29774 >= 1/5 (1.49x). The committed pair (WIP cap 3, never-dry floor)
is jointly unsatisfiable as a stationary guarantee — T1: pi(0) > 0 for
every finite cap; T2: the K->infinity frontier is max(0, 1 - r), so
"never dry" names a LIMIT (K->infinity AND r > 1), not a rule; T3: at
parity the committed cap is dry a quarter, blocked a quarter, running at
3/4 capacity. The tax is variance-born: D_det(3, r_hat) = 0 exactly
(clockwork cadence at the same means satisfies the pair from K = 2 up).
The two lived DRY events are the cap's own arithmetic firing on
schedule — both fell in the day-pause regime where D(3, r_life) ~ 0.63.
