# REPORT — Assign-at-merge, priced: the merge-queue re-validation tax (PROPOSAL 033)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 033** ·
> 2026-07-13T08:43:05Z · status: sim-ready (idea
> `ideas/superbot/assign-at-merge-queue-tax-2026-07-13.md`, landed via
> idea-engine PR #303, main `11c5a1f`). The standing ORDER 003 FLEET-BACKLOGS
> rotation slot, round 5 — round 2's own verdict-opened thread: VERDICT 023
> REJECTED the shipped Option-1 checker as sufficient and routed the Option-3
> assign-at-merge build while stating verbatim "nothing here prices Option 3's
> build cost". This sim prices that build's operational half: the serialized
> FIFO merge queue with a re-validation V_q at the head that any REAL
> assign-at-merge mechanism forces. Fully hermetic: every fixture is a pinned
> constant committed with the sim; zero repo/network reads in the verdict
> session.
> Run: `python3 sims/verdict-035-assign-at-merge-tax/assign_merge_tax_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — an exact closed-form decision arm
plus a seeded event-driven MC validation arm, band-scored against the
pre-registration): the per-cell re-validation budget V_q*(cell) — the largest
V_q in {0.1, 0.5, 2} h at which policy P3Q (FIFO queue over the shared
migration sequence, one deterministic re-validation V_q at the head, number
assigned at merge) beats VERDICT 023's committed P1 mean open→merge latency.
Arm A is exact and seedless — because every PR's open→queue-entry delay is
the constant W + V, queue arrivals are exactly Poisson λ and the M/D/1
Pollaczek–Khinchine form W + V + λV_q²/(2(1−ρ)) + V_q evaluates every
decision point with zero sampling error; the P1 comparison side enters as
V023's COMMITTED measured numbers quoted verbatim into the fixture (the
chained-anchor pattern), so the decision surface carries no estimation at
all. Arm S re-derives the same numbers by simulating the whole queue. The
ruling rides the exact-Fraction evaluator; the float evaluator is the twin.
This label fills the outbox `evidence: simulation`.

## PREMISE (verified at drafting, pinned into the fixtures — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`,
cross-checked at start — gate G11) and touches no repo state, no network, no
wall clock. The parent's constants travel INSIDE the fixture: the 9-cell P1
committed {mean, p95} table, the P3 means {8.25, 10.0, 32.0} by V column
(exactly W+V — the V_q = 0 regression gate), and the five treadmill cells'
committed T values, all quoted verbatim from
`sims/verdict-023-renumber-treadmill/results.json` @ `c7340ae`. **Anchor
gates, both passed before any anchor was used:** (1) the results.json at
origin/main HEAD `cd47c06` is byte-identical to the `c7340ae` version
(sha256 `53c633b1…`); (2) the parent's committed runner was re-run once
out-of-sim in a scratchpad copy (the V031 precedent): exit 0, `SELF-CHECKS:
16857 passed, 0 failed`, results.json byte-identical to the committed file
(same sha256). Twelve intake-time decisions are disclosed in `fixtures.json`
— most load-bearing: the p95 table riding the reporting seed per the
registration's own seed assignment (decision 1), the censoring convention
read for a queue (decision 2), and the familywise gate arithmetic
(IF = ((1+ρ)/(1−ρ))², tol = max(3.5·SE_pred, 0.02 h), 77 gates, expected
breach count ≈ 0.036 ≪ 1) with the breach protocol pinned BEFORE any draw
(decisions 4 and the pinned protocol). The fixture was committed before the
runner was written (git history is the trail).

## What the sim MODELS

All constants pre-registered in `fixtures.json`, inherited from P021/V023
verbatim: Poisson migration-bearing PRs λ ∈ {1, 4, 12}/day (per-hour 1/24,
1/6, 1/2); develop W = 8 h; validate V ∈ {0.25, 2, 24} h; H = 2,000 h,
warm-up 200 h, M = 40 per (cell, V_q). **Policy P3Q** (the build, the new
object): open → W → V → FIFO queue for the shared migration sequence → one
deterministic re-validation V_q at the head → number assigned at merge.
Zero collisions and zero renumbers by construction — MEASURED as exactly
zero on every replication of every leg (gate G2, the V023 P3-control
discipline). V_q grid: decision {0.1, 0.5, 2} h, control 0 (must reproduce
the committed P3 column exactly — gate G1), stress 8 h reporting-only.
**Stability rule, pre-registered:** ρ = λ·V_q ≥ 0.9 is UNSTABLE and fails
WIN by rule; its only decision-grid member is lam12 × V_q = 2 (ρ = 1.0
exactly — a pre-computable arithmetic exclusion); every other decision point
has ρ ≤ 1/3.

- **Decision rule (registered before any code; evaluated in this order):**
  WIN(cell, V_q) := Arm-A-exact mean ≤ committed P1 mean AND ρ < 0.9;
  V_q*(cell) := largest winning decision-grid V_q. **REJECT first** (V_q*
  exists in ≤ 2 of 5 treadmill cells); APPROVE (V_q* ≥ 2 h in ≥ 4 of 5,
  stability-reproduced, gates passing); NULL otherwise — the frontier table
  is the citable pin, flip axes named via per-axis WIN shares.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**(1) The frontier (Arm A exact, the decision leg).** Per treadmill cell,
P3Q mean open→merge (h) vs the committed P1 mean, and V_q*:

| cell (λ/day, V h) | committed P1 | V_q=0.1 | V_q=0.5 | V_q=2 | V_q* |
|---|---|---|---|---|---|
| lam01·V24 | 183.525239 | 32.1002 W | 32.5053 W | 34.0909 W | **2 h** |
| lam04·V2  | 11.416983  | 10.1008 W | 10.5227 W | 12.5000 L | **0.5 h** |
| lam04·V24 | 493.583020 | 32.1008 W | 32.5227 W | 34.5000 W | **2 h** |
| lam12·V2  | 121.019534 | 10.1026 W | 10.5833 W | UNSTABLE (ρ=1) | **0.5 h** |
| lam12·V24 | 493.408451 | 32.1026 W | 32.5833 W | UNSTABLE (ρ=1) | **0.5 h** |

A winning V_q exists in **5/5** cells (REJECT, checked FIRST, misses by 3
cells); V_q* ≥ 2 h in only **2/5** (APPROVE misses by 2 cells). **RULING:
NULL — the conditional frontier is the finding.** Exact margins at the
binding points: lam04·V2 wins at 0.5 h by 0.894256 h (463/44 vs 11.416983)
and LOSES at 2 h by 1.083017 h (25/2 vs 11.416983) — the drafting
arithmetic reproduced exactly; the two lam12 cells lose 2 h by arithmetic
(ρ = 1.0, no steady state), not by measurement.

**(2) The binding axes (per-axis WIN shares, exact).** λ: lam01 3/3, lam04
5/6, lam12 **2/3**; V: V24 8/9, V2 **2/3** — exactly the registration's two
expected candidates: the serialization ceiling ρ = λ·V_q (lam12 × 2 h is
excluded before any run) and the V = 2 same-day-review column (P1's
committed 11.417 h vs the free 10.0 h leaves only 1.417 h of queue
headroom, which a 2 h re-validation overspends). The conditional rule
ships: **the naive build pays at (λ ≤ 4/day, V_q ≤ 0.5 h) everywhere, pays
at V_q = 2 h only in the V = 24 slow-review column at λ ≤ 4/day, and is
arithmetically unstable at λ = 12/day × V_q = 2 h.**

**(3) Arm S agrees; stability reproduces; the controls land exactly.** 77
familywise gates (main 24 + stability 13 + p95 24 + jitter 13 + stress 3),
**0 breaches, max |z| = 2.065** (a p95-leg calm cell; the pinned protocol
was never engaged); the V_q = 0 control leg reproduced the committed P3
means {8.25, 10.0, 32.0} EXACTLY (float equality, all 9 cells); zero
collisions/renumbers measured on every replication of every leg; Little's
law and busy-fraction ≡ ρ within pinned tolerance on all 64 stable
simulated points; the two 16× aux diagnostics sit on the closed form
(z = −0.263 at lam04·V2×0.5, z = −0.915 at lam12·V0.25×0.1); the stability
leg (seed 20260769, M = 20) lands the same NULL; twin engines (heap
event-driven vs Lindley recursion) agree exactly on hand pins + rep 0 of
every main-leg point; twin decision evaluators (exact-Fraction vs float)
agree on every WIN cell, every V_q*, and the ruling. **16,090 self-checks,
0 failed**, exit 0.

**(4) Reporting-only context (registered as unable to flip; honest
surprises included).**
- **The calm cells split, against the registration's stated expectation.**
  The registration expected P3Q "strictly worse at any realistic V_q" in all
  four calm cells; measured: the two V = 0.25 columns (lam01, lam04) do lose
  at every V_q, but **lam01·V2 admits a 0.1 h win by 0.159 h and
  lam12·V0.25 by 0.008858 h (~32 s)** — thin, reporting-only, and irrelevant
  to the routed build (V023 never routed it for calm cells), but reported
  honestly rather than smoothed. V023's "the checker was worth shipping"
  survives with numbers in the V = 0.25 columns, where P1's residual is
  within 0.10 h of the free oracle.
- **The frontier is service-jitter-robust.** Under exponential service at
  the same mean (M/M/1, the jitter leg's own exact check reproduced within
  gates), the exact WIN map is IDENTICAL at every decision point — the wait
  term doubles but no margin flips; the deterministic/memoryless bracket
  does not move V_q* anywhere.
- **Stress column (V_q = 8 h):** lam01 stable (ρ = 1/3, gated, means
  18.52/19.89/42.18 h) — even a full 8 h re-validation beats the committed
  P1 mean in lam01·V24 (42.18 vs 183.53, the deep-treadmill cell); lam04 and
  lam12 are UNSTABLE by arithmetic (ρ = 4/3, 4) — printed, not simulated.
- **p95 (decision is on means, stated):** P3Q's p95 sits far below P1's
  committed p95 in every stable treadmill point (e.g. lam04·V2 × 0.5 h:
  10.71 vs 17.5; lam12·V2 × 0.5 h: 10.98 vs 440.0) — the queue's tail is
  mild at ρ ≤ 1/3 while the treadmill's tail is its defining pathology.
- **The churn column (the free, un-scored win):** P3Q renumbers = T = 0
  measured everywhere vs committed P1 T = 0.741109 / 0.133333 / 0.845601 /
  0.869564 / 0.846412 — a cell that narrowly misses WIN (lam04·V2 at 2 h,
  1.08 h over) may still be worth building for churn alone; the registered
  ruling stays on the latency metric (Model basis (3), disclosed).
- **Queue traces:** L̄ ≤ 0.087 waiting PRs and max queue length ≤ 5 across
  all stable decision points — the priced mechanism is a short queue, not a
  pile-up, everywhere it is stable.

## What it did NOT settle

- **Where superbot actually sits.** λ, V, W are pinned dials and V_q is a
  swept budget, not a measurement. The NULL consequence names the two
  zero-tooling live probes: V023's git-history probe for (λ, V, W, d) and
  the NEW one this head names — the repo's real V_q measured as CI wall-time
  on migration-touching PRs from its committed Actions history. The frontier
  table turns both into a decision the moment they land.
- **Re-validation FAILURES at the queue head** (a failed re-run adds fix
  latency and re-queues) and the **P1→P3Q transition window** — out of
  registered scope, one-sided against P3Q: APPROVE was the fragile
  direction, and the measured outcome (NULL, not APPROVE) is already on the
  conservative side of that disclosure.
- **Batching / merge-train disciplines** — the named rescue design if a
  future head wants V_q = 2 h at λ = 12/day; out of scope by registration.
- **The materiality lines.** The bands (≤ 2 of 5 / ≥ 4 of 5 / V_q† = 2 h)
  are pre-registered judgments; the full frontier ships, a re-drawn line
  re-reads, never re-runs.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The mechanism does not exist yet — pricing it pre-build is the point, so the
question is about the modeled queue by design. The parent's frame is
inherited verbatim (same λ/V/W grid, same horizon and warm-up, same
censoring), the P1 comparison side is the parent's COMMITTED measurement
(not re-modeled), and the two abstractions most likely to flip a builder's
reading are handled inside the run: service variance (the M/M/1 jitter leg
brackets it — the WIN map is identical at both extremes) and the real
(λ, V_q) cell (the declared flip axis, with both live probes named and the
conditional rule shipped so the probes land in a table, not a vibe).
Re-validation failures and the transition window are disclosed one-sided
against P3Q — they can only push further from APPROVE, and the ruling is
already NULL.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **16,090 self-checks, 0 failed**, exit-coded. The decision arm is
exact (closed forms in Fraction arithmetic vs committed anchors — zero
sampling error, so no seed can move the ruling); Arm S validates the
machinery at 77 familywise-calibrated gates (0 breaches, max |z| = 2.065,
expected breach count pre-computed ≈ 0.036), with the V_q = 0 leg landing
the committed P3 column EXACTLY, zero renumbers measured everywhere,
Little's law/busy-fraction/M/M/1 identities, draw-count sentinels, twin
queue engines, twin decision evaluators, and two hand-derived queue pins.
The full grid ships — decision, control, calm, stress, jitter, p95 —
including the two calm-cell points that came out AGAINST the registration's
stated expectation.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is not knife-edge on the decision surface: REJECT misses by 3 of
its 2-cell budget (5/5 vs ≤ 2), APPROVE by 2 cells (2/5 vs ≥ 4), and the
nearest decision margin is an exact 0.894 h (lam04·V2 at 0.5 h) with the
lam12 × 2 h exclusion arithmetic (ρ = 1.0), not measurement. Flipping any
single WIN cell changes no band. The jitter bracket moves no margin's sign;
the stability half-M seed reproduces the ruling. The one thin number in the
whole run (lam12·V0.25's 32-second calm-cell win) is reporting-only and
flagged as such.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own fixtures.json). Pinned seeds (20260768–71, above the P031 registry
high-water 20260767), pinned loop order, counted streams. stdout AND
results.json byte-identical across TWO complete process runs by external
`diff` (sha256 stdout `5bf9fb19…`, results `7bf93492…`) on cpython-3.11
(pinned and asserted). ~2.5 s per run. The anchor chain is itself
reproducible: parent results.json byte-identical at HEAD and re-derived
byte-identically from the parent's committed runner out-of-sim.

**5. "LIMITS? what this evidence does NOT show."**
It prices the SIMPLEST build only — one FIFO queue, one-at-a-time
deterministic re-validation, no failures, no batching, no transition window
(a REJECT would have ruled on that build only; the NULL's conditional rule
carries the same scope). It does not measure superbot's real λ, V, or V_q
(the two named probes do). It does not score the churn win (R = T = 0 rides
free; the column ships so a reader can re-weigh). Model hours, not
wall-clock — the parent's boundary inherited verbatim.

## Outcome

**NULL** (pre-registered: "anything else — the per-cell V_q* frontier table
IS the citable pin"). Evaluated in the registered order: REJECT (checked
FIRST) misses — a winning V_q exists in 5/5 treadmill cells, not ≤ 2;
APPROVE misses — V_q* ≥ 2 h in 2/5 cells, not ≥ 4. The binding axes are the
registration's own expected candidates, now with exact shares: λ (lam12 WIN
share 2/3 — the ρ = λ·V_q ceiling) and the V = 2 column (WIN share 2/3 —
1.417 h of headroom). Consequence, pre-registered: the conditional frontier
ships — **the naive build pays wherever the repo's real (λ, V_q) sits inside
the frontier** (all five treadmill cells at V_q ≤ 0.5 h; the V = 24 column
at λ ≤ 4/day up to a full 2 h CI) — and the TWO zero-tooling live probes
locate superbot's real cell before any spend: the V023 git-history probe for
(λ, V, W, d) and CI wall-time on migration-touching PRs from committed
Actions history for V_q. V023's interim mitigation (keep held
migration-bearing PRs off the hot path) remains the standing rule until the
probes land.
