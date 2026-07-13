# verdict-025 · ticket-envelope

Can the entry-fee-with-prize structure — the second of the three non-odds
levers VERDICT 022 routed after REJECTING the odds lever — hold FUN, SAFE,
and SINK simultaneously in some (take rate t × per-round ticket cap c)
cell, per prize shape? The direct successor to VERDICT 022 (its "Named
follow-ups" list requested this head verbatim: "an entry-fee/prize-table
envelope sim — the SAFE-band successor question"), with the parent's three
bands held fixed BY DESIGN so every cell names its parent cell. Answers
idea-engine PROPOSAL 023 (control/outbox.md 2026-07-13T03:53:03Z, idea
`ideas/superbot/casino-entry-fee-ticket-envelope-2026-07-13.md`, landed via
idea-engine PR #289, main `15d1802`) — the ORDER 004 rule-3 GAME-MECHANICS
rotation slot, round 2. Fully hermetic per the PROPOSAL 017–022 precedent:
every fixture is a pinned constant committed with the sim, zero
repo/network reads in the verdict session; the parent's anchor constants
are quoted verbatim in `fixtures.json` from its committed
REPORT.md/results.json @ `fda94d0`.

Model: B₀ = 1,000 integer chips, ticket price F = 0.01·B₀ = 10 (a table
constant no policy can escalate — every walk is exact integer F-units);
prize schedules with probabilities scaled by (1−t) so E[prize] = (1−t)·F
exactly — T1 double-up {2F w.p. (1−t)/2}, T2 tiered {8F, 3F, 1F w.p.
(1−t)·{0.05, 0.10, 0.30}}, T3 jackpot {25F, 5F w.p. (1−t)·{0.024, 0.08}};
take grid t ∈ {0.01, 0.02, 0.05, 0.10} + t=0 control; per-round ticket
caps c ∈ {5, 25, 100}; re-buy policies R1 / R5 / RG-greedy / MC-chase
(b ≤ c and b ≤ ⌊bankroll/F⌋; b tickets = b independent draws, so per-round
volatility grows like √b, not b — the structure lever under test);
profiles CASUAL / GRINDER (4,000-round cap, > 1% cap-hits = indeterminate)
/ COMPULSIVE (reporting-only). 36 decision cells. Arm A exact: FUN tails
for all 36 cells (T1 binomial required to reproduce VERDICT 022's
committed G1 values EXACTLY — the pre-registered cross-verdict identity),
T2/T3 by integer-support DP convolution, T1×R1 grinder ruin closed forms
(+ independent tridiagonal elimination + the exact finite-horizon capped
DP), T1×R1 casual wipe DP, t=0 P_double = 1/3 optional-stopping control.
Arm S seeded MC gated at 1.0 pp. Ruling REJECT (E* = ∅ at every cap in
≥ 2/3 shapes, checked FIRST) / APPROVE (a shared 2-consecutive-take band
across all shapes at some cap) / NULL per the decision rule registered in
the idea file before any code existed.

## Run (one command)

```
python3 sims/verdict-025-ticket-envelope/ticket_envelope_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — the only randomness is
`random.Random(20260730)` (primary) / `random.Random(20260731)` (stability,
half M) / `random.Random(20260732)` (aggregation spot check) /
`random.Random(20260733)` (aux self-checks), each consumed in the pinned
loop order (shape T1→T2→T3, t ascending with the control first, c
ascending, policy R1/R5/RG/MC, profile casual → grinder → compulsive,
replications sequential, exactly one `rng.random()` per ticket). No
network, no git, no wall clock, no `hash()`. stdout and `results.json` are
byte-identical across process runs (verified by external `diff` of two
complete runs, cpython-3.11). Progress goes to stderr only.

## Files

- `ticket_envelope_sim.py` — stdlib-only driver: exact Arm A (binomial +
  bigint DP convolution + ruin closed form/elimination/capped DP), the
  three shape kernels, an independently written twin kernel replaying
  traced replications, twin decision evaluators (one in exact integer
  cross-multiplication, one in Fractions), the pooled 1.0 pp agreement
  gate, Wald t=0 prize-fairness controls, per-replication conservation,
  exact draw-count sentinels (1,214,568,503 primary + 605,734,597
  stability uniforms), hand-derived pins, stability/aux/spot legs.
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file, the pinned loop/draw order, the
  decision rule + evaluation order, twelve disclosed intake-time
  decisions, two hand-derived pin scenarios with full derivations, and
  VERDICT 022's committed G1 identity values + anchor constants quoted
  verbatim @ `fda94d0`.
- `results.json` — committed run output: the full {P_ahead, P_wipe,
  P_double, cap_frac, expected loss, median rounds-to-ruin} × (shape, t,
  c, policy) tables for both legs, the E* envelope maps, per-axis shares,
  identity/agreement-gate results, the four chained anchors, and the
  ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the
  VERDICT 025 ruling).

## Verdict (summary — full report in REPORT.md)

**reject** — by the rule committed before any code (REJECT evaluated
first): E\*(g, c) = ∅ at EVERY cap in 2 of 3 shapes (T2 tiered and T3
jackpot; the rule needs 2/3), both arms where covered,
stability-reproduced. The fee frame's structural taming is REAL but
shape-bound: it rescues only the even-money shape.

- **The headline chained measurement:** the parent's near-miss cell
  transposed — T1 (t=0.05, c=5) — now PASSES all three bands: FUN 0.2738
  (exact, the identity), worst-policy P_wipe **0.0024** vs the parent's
  0.1358 SAFE failure (57× reduction — the "bounded fee" hypothesis
  measured TRUE for even-money), worst-policy P_double 0.0000 (parent
  0.0895). E\*(T1, c=5) = {0.05}, the grid's only surviving cell.
- **Why REJECT anyway:** T2 dies in a pincer — SINK fails at low take
  (worst-policy P_double 0.244 / 0.163 at t ≤ 0.02, EVERY cap) and SAFE
  fails at high take (0.0608 at its best cell (t=0.05, c=5), 1.2× the
  band); T3 fails SINK everywhere (0.148–0.346 vs 0.10, the parent's
  0.195–0.323 wall reproduced in the fee frame) AND SAFE everywhere
  (0.275–1.000 — five 16-variance tickets per round out-wipe the parent's
  single stake).
- **Residual gap per shape (the failing band at the shape's best cell):**
  T2 SAFE 0.0608 vs 0.05 at (t=0.05, c=5); T3 SINK 0.1480 vs 0.10 at
  (t=0.10, c=5). T1's gap is CLOSED at (t=0.05, c=5).
- **Cap rider:** c=5 is load-bearing — at c ≥ 25 the greedy re-buyer
  recreates exactly the wipe the parent measured (RG P_wipe 0.116–1.000);
  any surviving house-banked ticket surface should pin the per-round spend
  cap at 5%·B₀.
- **Gates:** cross-verdict identity EXACT on all five takes; agreement
  gate max pooled deviation 0.78 pp (band 1.0); t=0 control = 1/3 exactly;
  stability leg reproduces REJECT with the identical envelope map.

1,925,723 self-checks, 0 failed; stdout + results.json byte-identical
across two full process runs by external diff on cpython-3.11; ~5.2 min
per run.
