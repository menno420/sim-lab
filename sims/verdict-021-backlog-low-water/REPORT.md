# REPORT — backlog low-water signal threshold (PROPOSAL 019)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 019** ·
> 2026-07-13T01:34:28Z · status: sim-ready (idea
> `ideas/fleet/backlog-low-water-signal-tuning-2026-07-13.md`, landed via idea-engine
> PR #284, main `f7906e5`). The ORDER 004 rule-3 FLEET-BACKLOGS rotation slot,
> restarting the cycle after 017 unrelated / 018 venture. Fully hermetic (the
> PROPOSAL 017/018 precedent): every fixture is a pinned constant committed with the
> sim; zero repo/network reads in the verdict session.
> Run: `python3 sims/verdict-021-backlog-low-water/backlog_low_water_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic policy-grid
sweep, band-scored): the pinned never-idle lane wake loop driven through the
full 18-cell × 6-N grid at M=300 seeded replications per (cell, N),
`random.Random(20260719)` in the pinned loop order, all decisions computed in
exact `Fraction` arithmetic on pooled integer counts (no floats in the
decision path). This label fills the outbox `evidence: simulation`. The one
judgment question — whether 0.05 dry / 25-per-100 alarm / +0.10 material are
the RIGHT lines — was pinned by pre-registration in the idea file and is
disputable only about the bands, never about the measured numbers.

## PREMISE (verified this session — hermeticity by construction)

The proposal's premise: fully hermetic, every fixture a pinned constant
committed with the sim. Verified HONESTLY: the sim reads exactly ONE file (its
own committed `fixtures.json`, the pre-registration) and touches no repo
state, no network, no wall clock; every constant ({H, M, b₀, R, N-grid,
L-grid, regime constants incl. the observed multisets, p_c grid, band
constants, seeds}) was copied verbatim from the idea file into
`fixtures.json` BEFORE the runner was written, and the runner cross-checks
its literals against that file at start (including recomputing each regime's
stated mean inflow from its {q, multiset}). ONE intake-time parameter
decision, disclosed: the idea file pins M=300 for the decision grid and M=50
for the stability leg but leaves M for the R/b₀/H sensitivity legs unpinned —
committed in `fixtures.json` before any code ran: sensitivity legs run the
full grid at M=50 (the stability leg's committed scale). Reporting-only; it
cannot touch the decision.

## What the sim MODELS

A never-idle lane's backlog as a discrete-wake inventory process. All
constants pre-registered in `fixtures.json`:

- **Pinned wake loop** (t = 1..H, H=2,000, b₀=6): (1) due replenishment lands
  (+R, R=4 primary); (2) consumption — demand w.p. p_c ∈ {0.6, 1.0}; if
  demand and b > 0, b −= 1; if demand and b = 0, a **dry wake**; (3) organic
  arrival w.p. q of batch g: **A1 steady-small** (q=0.30, g ∈ {1,2,3}; mean
  0.60/wake), **A2 bursty-real** (q=0.10, g on the OBSERVED multiset
  {2,4,5,11}; mean 0.55/wake — anchored to the four measured websites re-pin
  births), **A3 harvest-scarce** (q=0.05, g ∈ {2,3,4}; mean 0.15/wake);
  (4) **signal policy** N ∈ {0(off),1,2,3,4,6}: if b ≤ N and no replenishment
  in flight, emit a signal (one outstanding — the wake-hygiene rule),
  scheduling +R at t+L, L ∈ {1,2,4} wakes (same-sweep / next-sweep /
  overnight — a stated mapping, not a wall-clock claim).
- **Cells:** 3 regimes × 2 p_c × 3 L = 18; per (cell, N) M=300 replications;
  ONE `random.Random(20260719)` stream through the pinned loop order (cells
  lexicographic, N ascending, replications sequential; per-wake draws:
  consumption, arrival-fire, batch-size — all policy-independent, so the
  stream position never depends on N or L).
- **Metrics (pooled over M):** D = dry wakes / demand wakes; S = signals per
  100 wakes; mean backlog (bloat, reporting-only).
- **Decision rule (registered in the idea file before any code; evaluated in
  this order):** N*(cell) = smallest N ∈ {1,2,3,4,6} with D(N) ≤ 0.05 AND
  S(N) ≤ 25; ΔD(cell) = D(0) − D(N*). **REJECT-a** iff D(0) ≤ 0.05 in ≥ 80%
  of cells (checked FIRST); **APPROVE** iff N* exists in ≥ 80% of cells AND
  median ΔD ≥ 0.10 (threshold = grid-median N*, stating whether "~3" lies
  within ±1); **REJECT-b** iff N* exists in < 50% of cells; **NULL**
  otherwise (flip axis named via per-axis N*-exists shares and median ΔD).
- **Legs:** primary (decision); stability M=50 seed 20260720 (must reproduce
  the ruling); reporting-only sensitivity R ∈ {2,8}, b₀ ∈ {3,12}, H=500.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json` (exact fractions kept for the primary leg).

**(1) REJECT-a fails — organic refill does NOT suffice (checked first).**
D(0) ≤ 0.05 in **3/18 cells** (16.7%, vs the 80% bar): only A1 steady-small
at p_c=0.6 (D(0) = 0.028–0.030). Everywhere else the baseline runs dry
hard: A2 p_c=0.6 0.104–0.110 (same mean inflow as A1 — burstiness alone
quadruples baseline dryness), deficit cells 0.40–0.85, A3 harvest-scarce
worst (0.745–0.847).

**(2) APPROVE binds: N* exists in 18/18 cells and median ΔD =
508,621/1,200,000 ≈ 0.424.** Per-cell N* (D and S both inside the bands at
the smallest such N):

| cell (regime·p_c·L) | D(0) | N* | D(N*) | S(N*) /100 wakes | ΔD |
|---|---|---|---|---|---|
| A1·0.6·L1 | 0.0278 | 1 | 0.0 | 0.45 | 0.028 |
| A1·0.6·L2 | 0.0288 | 1 | 0.0 | 0.47 | 0.029 |
| A1·0.6·L4 | 0.0299 | 1 | 0.0035 | 0.43 | 0.026 |
| A1·1.0·L1 | 0.3972 | 1 | 0.0 | 9.97 | 0.397 |
| A1·1.0·L2 | 0.3988 | 1 | 0.0 | 9.98 | 0.399 |
| A1·1.0·L4 | 0.3969 | 2 | 0.0433 | 8.89 | 0.354 |
| A2·0.6·L1 | 0.1040 | 1 | 0.0 | 1.64 | 0.104 |
| A2·0.6·L2 | 0.1078 | 1 | 0.0 | 1.64 | 0.108 |
| A2·0.6·L4 | 0.1102 | 1 | 0.0167 | 1.38 | 0.093 |
| A2·1.0·L1 | 0.4489 | 1 | 0.0 | 11.29 | 0.449 |
| A2·1.0·L2 | 0.4510 | 1 | 0.0 | 11.37 | 0.451 |
| A2·1.0·L4 | 0.4532 | 3 | 0.0 | 11.28 | 0.453 |
| A3·0.6·L1 | 0.7462 | 1 | 0.0 | 11.24 | 0.746 |
| A3·0.6·L2 | 0.7444 | 1 | 0.0 | 11.21 | 0.744 |
| A3·0.6·L4 | 0.7450 | 2 | 0.0344 | 10.72 | 0.711 |
| A3·1.0·L1 | 0.8470 | 1 | 0.0 | 21.21 | 0.847 |
| A3·1.0·L2 | 0.8465 | 1 | 0.0 | 21.21 | 0.847 |
| A3·1.0·L4 | 0.8470 | 3 | 0.0 | 21.28 | 0.847 |

N* distribution: **N*=1 in 14 cells, N*=2 in 2 (A1·1.0·L4, A3·0.6·L4),
N*=3 in 2 (A2·1.0·L4, A3·1.0·L4)**. Grid-median N* = **1**.

**(3) The bullet's "~3" is NOT within ±1 of the grid-median (|3 − 1| = 2).**
As a fleet-wide default, "~3" over-signals: N=1 already clears both bands in
14/18 cells. "~3" is exactly right ONLY in the two hardest cells — every-wake
consumption (p_c=1.0) + overnight latency (L=4) + thin/bursty arrivals (A2,
A3) — where N=3 is also the structural-zero threshold: descending backlog
always fires at exactly b=3 (a landing leaves b ≥ 4−1 = 3 at the signal
step), and L=4 flight consumes at most 3 before the batch lands, so a dry
wake is unreachable (measured D = 0 exactly on 600,000 wakes in both cells).
The threshold the fleet should pin is **N* = 1 default, N* = 3 for
known-hot/long-latency lanes** — the conditional carried into the verdict.

**(4) The alarm band never binds at N* — and it has an analytic shape the
data reproduces.** In sustained-deficit cells the steady-state signal rate is
deficit/R per wake (each signal delivers R): predicted S = 25·(p_c −
inflow)/1 per 100 wakes at R=4 → A1·1.0 predicts 10.0 (measured 8.9–10.0),
A2·1.0 predicts 11.25 (measured 11.28–11.37), A3·0.6 predicts 11.25
(measured 10.7–11.2), A3·1.0 predicts 21.25 (measured 21.21–21.28 — 85% of
the S ≤ 25 budget, the tightest cell in the grid). Balanced/surplus cells
signal rarely (0.43–1.64) because injected batches push the backlog above N
for long stretches (mean backlog at N*: 2.0–32.6 vs baseline 0.36–29.5 —
signal-driven bloat is bounded, reporting-only).

**(5) Stability + sensitivity (reporting-only, none can flip; all scored
under the same rule for the record).** The M=50 seed-20260720 stability leg
reproduces **APPROVE** (18/18, median ΔD 0.426, grid-median N* 1, identical
N* map). R=8 / b₀=3 / b₀=12 / H=500 all land APPROVE with the same or
near-same N* map (b₀ moves nothing — the horizon washes the start; H=500
only shrinks the baseline-pass count to 1/18). **R=2 lands NULL under the
rule** — the one disclosed fragility: at half the replenishment batch the
deficit cells need d/R > 0.25 signals/wake, so S ≤ 25 becomes unsatisfiable
at ANY N in {A2·1.0·L4, A3·1.0·L1/L2/L4} (N* exists 14/18 = 77.8%, between
the bands; largest per-axis spread = regime, 0.50). The approval therefore
carries an explicit rider: the signal contract assumes the manager routes a
meaningful batch (R ≈ 4 work items) per signal; a lane whose replenishment
is ~2 items should expect the alarm budget, not the dry-wake band, to bind.

## What it did NOT settle

- **The regimes are pinned constructs (the pre-registered n=4 anchor
  caveat):** the four observed websites re-pin intervals BRACKET regime A2
  (burst sizes {2,4,5,11}, near-balance); they cannot fit a distribution.
  A1/A3 sweep the bracket's sides. The anchor leg is reporting-only evidence
  about the model family, not about any live lane's true arrival law.
- **Latency is in wakes, not hours:** L ∈ {1,2,4} spans same-sweep to
  overnight as a stated mapping; no wall-clock claim is made or tested.
- **One lane, one signal:** manager-side contention (five lanes signaling at
  once) is out of scope by design — the named follow-up.
- **Where any REAL lane sits in the grid** — which (regime, p_c, L) cell
  idea-engine or any lane actually occupies is unmeasured; the pre-registered
  NULL probe (a ~1-week depth-logging notes-line) remains the cheapest way to
  locate a live cell before per-lane tuning, even under this APPROVE.
- **Alarm fatigue is priced only as a rate** (S ≤ 25); whether a manager
  IGNORES a signal at any rate is a human question no wake loop can answer.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The model abstracts a lane's work loop to {demand coin, arrival coin, batch
draw, one-outstanding signal} — no multi-item wakes, no signal loss, no
manager queueing. The load-bearing conclusion (a low-water signal cuts
dry-wakes by ~42 points at the median cell and N=1 suffices in 14/18 cells)
is a policy-grid property swept across three arrival regimes bracketing the
one measured anchor and both consumption rates; the gap that COULD flip a
per-lane number — the lane's true (regime, p_c, L) cell — is disclosed and
carried as the depth-logging follow-up, not hidden in the default.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **411,339 self-checks, 0 failed**, exit-coded: per-replication
conservation identities (final b = b₀ + landed·R + arrived − consumed, on
every one of the 64,800 replications across all legs), dry+consumed ≡ demand,
p_c=1 ⇒ demand ≡ H, N=0 ⇒ signals ≡ 0, one-outstanding spacing ≥ L and the
1+⌊(H−1)/L⌋ signal-count bound, landed ≤ signals, backlog ≥ 0; an
INDEPENDENT trace-replay re-implementation (different state layout, pending
list, no early exits) agrees exactly on 112 strided (cell,N) traced
replications across all seven legs; two fully hand-derived pin scenarios
(derivations committed in `fixtures.json`, including the tight gap = L
spacing case) pass; fresh `Random(seed)` reproduces each leg's first draws
and the draw-count accounting identity (2·H·reps + fires) closes exactly; the
decision is computed twice by independently-written evaluators (Fraction
shares vs integer cross-multiplication) that must agree on ruling, N* map,
and medians; every fixture constant is cross-checked against the committed
pre-registration. No seeded luck: the primary seed was pre-registered in the
idea file, and a DIFFERENT seed (20260720) at M=50 reproduces the ruling and
the entire N* map. No cherry-picking: the full 18×6 table is committed for
every leg, failures (R=2's NULL) first-class.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The APPROVE is not knife-edge on its own terms: N* exists in 18/18 (bar:
15), median ΔD 0.424 vs the 0.10 bar (4.2×), and the alarm band's tightest
cell sits at 21.28 vs 25 (15% margin) with an analytic prediction (25·d/R)
the measurement reproduces. Disclosed edges: A1·1.0·L4's N*=2 clears the dry
band at D = 0.0433 (13% under 0.05 — the stability leg lands the same N*);
and the R=2 sensitivity leg breaks the alarm band in the four hardest cells
(reporting-only, disclosed as the approval's rider). The grid-median N* = 1
is stable across every leg that approves.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, no network / git / wall clock /
`hash()`; one `random.Random(<pinned seed>)` stream per leg in the pinned
loop order. stdout AND `results.json` byte-identical across TWO complete
process runs by external `diff` on cpython-3.11 (pinned in `results.json`
and checked at start). Runtime ~31 s.

**5. "LIMITS? what this evidence does NOT show."**
It does not show which grid cell any live lane occupies (the depth-logging
probe remains the locator); does not test multi-lane signal contention (out
of scope by design); asserts nothing about wall-clock latency (L is in
wakes); prices alarm cost as a rate, not as human attention; the A2 anchor
BRACKETS four observed intervals rather than fitting them (n=4, pre-
registered); and the R=2 fragility means the threshold row travels with its
replenishment-batch assumption (R ≈ 4), not as a free-standing constant.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Every constant, band, and the decision order were registered in the idea file
before any code; the decision arithmetic is exact (pooled integer Fractions);
the winner is corroborated by an analytic steady-state law the data
reproduces; a second seed reproduces the ruling and the full N* map; and the
one fragile axis found (R) is disclosed as a rider rather than absorbed. The
honest boundary: this strength attaches to the pinned model family — a
per-lane threshold still wants the live-cell probe before hand-tuning.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `approve` — ship the signal; pin the threshold.** By the rule
  committed before any code (REJECT-a checked first: baseline passes only
  3/18 — organic refill does not suffice): N* exists in 18/18 cells, median
  ΔD ≈ 0.424 ≥ 0.10. **Recommended threshold = grid-median N* = 1**, with
  the measured conditional: **N = 3 for every-wake-consumption lanes on
  overnight routing latency** (the two cells where the bullet's constant is
  exactly right).
- **The bullet's "~3" is NOT within ±1 of the grid-median N*** (3 vs 1): as
  a fleet default it over-signals; as a hot-lane setting it is the measured
  structural-zero threshold. The websites bullet graduates from "~3 by vibe"
  to "N*=1 default / N*=3 hot-lane" — relayed via the manager sweep (the
  lane is PARKED).
- **Consequence (pre-registered):** substrate-kit gets the evidence row for a
  `backlog:` heartbeat grammar token with planted default N=1 (declare-time
  option: a per-lane override for hot/long-latency lanes at 3); idea-engine
  adopts as consumer #1, notes-line first per the fold-in-over-declare rule.
- **Riders (measured):** the row assumes the manager routes R ≈ 4 items per
  signal — at R=2 the alarm budget (S ≤ 25) becomes unsatisfiable in the
  hardest cells (the R=2 leg lands NULL under the rule, reporting-only);
  and the latency mapping (L in wakes: same-sweep/next-sweep/overnight) is
  stated, not measured. n=4 anchor caveat restated: the four observed
  websites intervals bracket regime A2, they do not fit a distribution.
- **Named follow-ups (not ordered):** the ~1-week per-wake depth-logging
  notes-line probe on idea-engine (locates a live lane's cell before any
  per-lane tune); manager-side multi-lane signal contention (the single-lane
  boundary, pre-registered).
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V019 slice boundary, with header timestamps from live
`date -u` at append time. -->
