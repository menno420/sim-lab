# VERDICT 079 — kill-clock anchor vs owner-gated funnel onset (idea-engine PROPOSAL 066) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT → INVALID → APPROVE → NULL; both independently-written decision
evaluators agree REJECT/REJECT; every decision number a seedless exact
rational):

- **R1 — the SAME viable product flips risk class on click timing alone:**
  FK(τ=13) = (99/100)^60 ≈ **0.547157 ≥ 1/2** (1.0943× over the line) AND
  FK(τ=0) = (99/100)^192 ≈ **0.145197 ≤ 1/5** (1.3774× under). A product the
  committed rule kills with probability 14.5% when the funnel wires same-day
  is killed with probability 54.7% when the SAME product's funnel wires 13
  days late — the verdict moved 3.77× on a quantity (owner click latency)
  with nothing to do with viability.
- **R2 — the doubling sits inside the window itself:** doubling onset
  min{τ ∈ grid : FK(τ) ≥ 2·FK(0)} = **13 ≤ 13** (ratio 3.7684× there;
  τ = 10 lands 1.9608× — one grid step below the doubling line, the
  registered knife-edge, disclosed and confirmed).
- **R3 — the repair is free and exact:** A-CAP30 (anchor at funnel-live,
  hard-capped at the lane's own committed 30-day signal window) holds
  FK(τ) = FK(0) **EXACTLY** at every grid τ ≤ 16 ({0, 3, 7, 10, 13} all at
  N = 192), with worst-case slot occupancy **30 ≤ 30** days (vs A-FUNNEL's
  unbounded τ + 14 = 34 at τ = 20). Both repair constants — 14 and 30 — are
  already committed lane-side; truncation resumes only past the cap (τ = 20
  admits N = 174, FK ≈ 0.17399, vs the committed anchor's exact 1).

The committed listing-live anchor makes the T+14 verdict a measurement of
owner click latency, not product viability: under A-LIST the evidence mass
collapses monotonically (BURN N = 192 → 179 → 155 → 125 → 60 → 0 across the
τ grid) and τ ≥ 14 is a CERTAIN false kill of every viable product at every
shape and every q (FK = 1 exactly — the committed "BASE CASE 0 sales until a
distribution channel is wired" as arithmetic).

## Gates — ALL GREEN (32 self-checks, 0 failed, exit 0)

- **F1** — N recomputed identically by both arms (all 54 cells); FK =
  (1 − q)^N re-verified against the twin's N at every cell and q;
  conservation in-window + pre-window + post-window = shape total mass
  (every cell, literal day-walk); monotonicity (FK nonincreasing in q and in
  N, every cell); anchor coincidence at τ = 0 (all three anchors agree
  exactly, every shape and q).
- **F2** — the three structure theorems, exact, FULL grid: (1) ANCHOR
  INVARIANCE — A-FUNNEL N and FK exactly τ-invariant at every shape and q;
  (2) SPIKE STEP — A-LIST SPIKE N = 200·1[τ ≤ 13], FK constant (1 − q)^200
  through τ = 13 and exactly 1 at τ ≥ 14; (3) CAP-30 EQUIVALENCE +
  BOUNDEDNESS — A-CAP30 ≡ A-FUNNEL exactly at every grid τ ≤ 16 (every
  shape and q), occupancy ≤ 30 on the full grid, truncation resuming at
  τ = 20 with the BURN pencil cell N = 174; plus MONOTONE TRUNCATION —
  A-LIST N nonincreasing in τ and zero at τ ≥ 14, FK nondecreasing and
  exactly 1 at τ ≥ 14, every shape and q.
- **F3** — closed-form anchors, all hit exactly: BURN cumulative first-14
  schedule (60, 90, 110, 125, 137, 147, 155, 162, 168, 174, 179, 184, 188,
  192); BURN A-LIST N row (192, 179, 155, 125, 60, 0); BURN total mass 261;
  DRIP N = 2·(14 − τ)⁺; (99/100)^5 = 9509900499/10000000000 exact; the
  CAP30 τ = 20 BURN cell N = 174.
- **F4** — hand world (shape (3, 2, 1), window 3, q = 1/2, τ = 1): A-LIST
  N = 5, FK = 1/32; funnel anchor N = 6, FK = 1/64 — both arms, matching
  the pencil.
- **F5** — degeneracies: q = 0 → FK = 1 everywhere (the dead-product row —
  perfect specificity by construction, this head prices sensitivity only);
  q = 1 → FK = 1[N = 0] exactly; the τ = 20 A-LIST row = 1 exactly at every
  shape and q (the committed base case as arithmetic).
- **F6** — Arm B (literal calendar day-walk, independently written)
  exact-equal on every published number (N + FK across all cells and all q
  including degeneracies, plus the hand world); twin decision evaluators
  agree REJECT/REJECT; Arm-R draw sentinels exact (one uniform per in-window
  visit — 63,600,000 main + 12,720,000 stability draws == episodes × N per
  cell); aux seed 20261583 never read (constructor registry:
  [20261580, 20261581, 20261582]); stdout + results.json byte-identical
  across two full process runs; CPython 3.11 asserted.

## Reproducibility

One command, no flags:
`python3 sims/verdict-079-kill-clock-anchor/kill_clock_anchor_sim.py`.
Two full process runs externally diffed — byte-identical. sha256:
`run-stdout.txt`
`132eb2375c925319ccb9eab7d01c6d40c52568113c5258b4e6ff8b5eea248428`,
`results.json`
`53ea4587c36fa9cee4ecf454fd5df9fe225acf3ce626ae17acab0bdc4f991037`.
~28 s/run on CPython 3.11.15, stdlib-only, hermetic (reads only its own
`fixtures.json`). Seeds constructed: 20261580 (Arm-R main), 20261581 (Arm-R
stability), 20261582 (presentation shuffle — read by the shuffled stdout
grid listing only); aux 20261583 asserted never read. This session
allocated NO seeds of its own — the P066 drafter's registered allocation is
the session seed set (the V077/V078 precedent).

## Headline tables (exact; full 270-cell FK surface in results.json)

Decision profile FK(τ) at (BURN, q = 1/100), exact rationals (99/100)^N:

| τ | 0 | 3 | 7 | 10 | 13 | 20 |
|---|---|---|---|----|----|----|
| A-LIST N | 192 | 179 | 155 | 125 | 60 | 0 |
| A-LIST FK | 0.145197 | 0.165463 | 0.210598 | 0.284708 | 0.547157 | 1.000000 |
| A-FUNNEL FK | 0.145197 | 0.145197 | 0.145197 | 0.145197 | 0.145197 | 0.145197 |
| A-CAP30 FK | 0.145197 | 0.145197 | 0.145197 | 0.145197 | 0.145197 | 0.173990 |
| A-FUNNEL occupancy | 14 | 17 | 21 | 24 | 27 | 34 |
| A-CAP30 occupancy | 14 | 17 | 21 | 24 | 27 | 30 |

Doubling-onset row under A-LIST (min grid τ with FK ≥ 2·FK(0)): BURN
q = 1/100 → **13** (the decision cell); BURN q = 1/30 → 7; BURN q = 1/300 →
off-grid-right (the window fails even at τ = 0 — dial territory, V061);
SPIKE → 20 at q ∈ {1/30, 1/100} (the step: constant, then certainty),
off-grid-right at 1/300; DRIP q = 1/100 → off-grid-right (FK(0) = 0.754719
already — 2× exceeds 1), DRIP q = 1/30 → 13.

## Arm R (seeded, REPORTING-ONLY — no statistical gate)

Literal Bernoulli visit process at the decision cell, 100,000 episodes
(main, seed 20261580) / 20,000 (stability, 20261581), one uniform per
in-window visit in schedule order, exact-rational conversion comparison:

| cell | N | exact FK | main FK-hat | stability FK-hat |
|------|---|----------|-------------|------------------|
| A-LIST τ=0 | 192 | 0.145197 | 0.14357 | 0.14545 |
| A-LIST τ=13 | 60 | 0.547157 | 0.54593 | 0.54550 |
| A-CAP30 τ=0 | 192 | 0.145197 | 0.14655 | 0.14315 |
| A-CAP30 τ=13 | 192 | 0.145197 | 0.14521 | 0.14540 |

Named finding, ruling-neutral: every trace sits within ~0.0015 of its exact
FK — the literal process reproduces the exact arithmetic; the A-CAP30
τ = 13 main trace lands on 0.14521 (the flat repair measured live).

## Anomalies — first-class, never smoothed

**None.** All 20 drafter-disclosed landing values re-derived from scratch
and compared at their stated precision (convention C9) — 20/20 match: the
full decision FK profile (6 values), both R1 margins (1.094× / 1.377×
under), the doubling onset 13 with both ratios (3.768× / 1.9608×), the
A-CAP30 flat value and τ = 20 cell (0.145197 / 0.17399), the SPIKE constant
(0.13398), both q edges (0.130799 with ratio 87.8× / 0.526729), and the
DRIP row (0.754719). The V077/V078 anomaly channel (unlabeled
approximations, unevaluated inline expressions) is empty this time — the
P066 drafter's disclosed landing carried no derivation-text slips; the V078
session card's registration-time anchor-self-evaluation recommendation
appears to have been honored by construction.

## Reporting rows (never gated)

- **SPIKE at the decision q lands the APPROVE clauses exactly** (FK constant
  0.13398 through τ = 13: FK(13) = FK(0) ≤ (6/5)·FK(0) and ≤ 1/4) — the
  truncation tax is a slow-burn phenomenon; the decision-shape choice is
  load-bearing and justified by the lane's one wired channel BEING the
  slow-burn dev.to article. Registered falsifiability, confirmed.
- **Both q edges land outside R1, as registered:** q = 1/30 → FK(13) =
  0.130799 < 1/2 (R1 fails — high-conversion products survive truncation in
  absolute class, though the τ-ratio is 87.8×); q = 1/300 → FK(0) =
  0.526729 > 1/5 (R1 fails — the window fails even at τ = 0: V061's dial
  territory, not an anchor problem).
- **DRIP:** FK(0) = 0.754719 — the "near-zero but free" channel cannot feed
  a 14-day ≥1-sale rule at 1% under ANY anchor; the row that gives the
  committed "BASE CASE 0 sales" sentence its number.
- **10-product queue row** (reporting multiplication, 10·FK at the decision
  cell under A-LIST): 1.45 expected false kills at τ = 0 → 5.47 at τ = 13 →
  10.00 at τ = 20 — if the batched publish clicks fire in one sitting while
  funnels wire ≥ 14 days late, the committed rule delists the entire queue
  regardless of product quality.
- **The lived launch sits at τ = 0** by the committed timestamps (listing
  2026-07-12T16:25:16Z, funnel-top article 17:18:47Z, same day) — the
  committed rule has never yet been exercised at the τ values where it
  misbehaves, which is exactly why pricing it BEFORE the 10-product queue
  clears is the cheap moment.

## Boundaries (pre-registered, ride the verdict)

- **Exposure-conversion boundary:** demand = visits × per-visit i.i.d.
  conversion; correlated visit bursts and word-of-mouth compounding are
  named unmodeled channels, direction stated — positive correlation fattens
  the zero-sale tail and moves every FK REJECT-ward.
- **Magnitude boundary:** the shape totals are pinned readings of committed
  ADJECTIVES — the three theorems and the τ ≥ 14 certainty row are
  magnitude-free; the R1/R2 levels are not, which the q and shape grids
  bracket; the lane's own dashboards handing over measured visit schedules
  is the named free follow-up (the committed FK function re-runs on any
  schedule at zero marginal cost).
- **Threshold boundary:** the ≥1-sale leg only; the qualified-inbound leg is
  out of scope (P050's own scoping inherited).
- **Dial boundary:** T = 14 held fixed — the dial is V061's served
  territory; this verdict prices the ANCHOR at the committed dial value.
- **Single-product boundary:** per-product arithmetic; the queue row is a
  reporting multiplication with no cross-product interaction — deliberately
  NOT the dropped release-cadence head.

## Consequence (pre-registered REJECT branch, verbatim-faithful)

Routing is the manager's per Q-0260 — this repo never edits venture-lab
files; nothing here builds, publishes, or spends. APPLICATION GUARD, two
conditions: (1) the verdict conditions on the committed rule text — the
T+14 ≥1-organic-sale-from-listing-live deadline and the 30-day signal window
as committed @ 520bdfc; an amended kill-rule grammar means re-run, not
reuse; (2) it conditions on the funnel being a SEPARATE owner-gated click —
a lane that wires the funnel in the same sitting as the publish click sits
at the τ = 0 column by construction, where all three anchors coincide
exactly.

Paste-ready structured choice to the lane via the manager, recommendation
first per Q-0263.2:

- **(a, recommended: zero new constants)** re-anchor the kill window at
  FUNNEL-LIVE with the committed 30-day listing-live cap (A-CAP30): one line
  in the vetting-packet §7 kill-rule grammar / LAUNCH-LOG template — "T+14
  counted from funnel-live, never past listing-live + 30" — τ-invariant
  evidence for every onset ≤ 16 days (exact, theorem 3), occupancy bounded
  by the constant the lane already ships.
- **(b)** keep the listing-live anchor but SYNCHRONIZE the clicks — each
  product's funnel-wiring click rides the same owner-queue sequence as its
  publish click (queue composition, zero rule changes; composes with V073's
  served attention-order verdict).
- **(c)** treat a zero-evidence window (no funnel wired by T+14) as VOID
  (re-arm once) rather than NEGATIVE — a rule-grammar change whose measured
  basis is the τ = 20 row's exact FK = 1.

An owner/lane intent call, never ruled by fiat here. Transferable law, one
line, for every fleet surface: a CALENDAR-ANCHORED DEADLINE whose EVIDENCE
CHANNEL is gated on a separate un-synchronized click measures the click,
not the subject — probe windows armed before instrumentation, checkpoint
reviews, KDP launches vs marketing onset, deadman expiries with gated
activity channels all inherit FK(τ). Named follow-ups, none in scope:
measured visit schedules from the lane's dashboards; correlated-burst
exposure; the qualified-inbound leg; richer evidence thresholds.
