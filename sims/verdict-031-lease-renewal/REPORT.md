# REPORT — Lease-renewal claim expiry: pricing V027's routed slice (PROPOSAL 029)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 029** ·
> 2026-07-13T06:51:49Z · status: sim-ready (idea
> `ideas/substrate-kit/lease-renewal-claim-expiry-2026-07-13.md`, landed via
> idea-engine PR #297, main `0e168bf`). The ORDER 004 rule-3 FLEET-BACKLOGS
> rotation slot, round 4 — not a fourth harvest source but round 3's own
> verdict-opened thread: VERDICT 027 REJECTED silence-keyed claim expiry and
> routed the lease-renewal `renewed:` slice while its LIMITS line left the
> mechanism undesigned. This sim prices the routed mechanism's three unpinned
> constants (renewal cadence, expiry horizon on the renewal stream, and the
> compliance it silently assumes) on V027's own bands. Fully hermetic: every
> fixture is a pinned constant committed with the sim; zero repo/network reads
> in the verdict session.
> Run: `python3 sims/verdict-031-lease-renewal/lease_renewal_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — exact DP + exact mixture quantiles
on all 45 decision points plus a seeded event-driven MC validation arm,
band-scored against the pre-registration): the twin-work risk T and the
deadlock cost O95 of renewal-keyed claim expiry, per (wake-cadence ×
compliance) cell and renewal-expiry horizon θ_r. Arm A is exact and seedless —
the deterministic wake lattice makes T a finite trailing-run DP (a maximal run
of j consecutive forgets exposes (j·p_w − θ_r)⁺ hours;
P(takeover) = 1 − E[exp(−λ_c·total exposure)]) and O95 an exact mixture
quantile of (θ_r − A)⁺ + Exp(λ_c) — so the decision surface carries zero
sampling error; Arm S re-derives the same numbers by event-driven simulation.
This label fills the outbox `evidence: simulation`. The judgment lines
(0.05 / 120 h / 8-of-9 / 5-of-9) are inherited VERBATIM from V027 by
pre-registration; the full curves ship in `results.json`, so a re-drawn line
re-reads, never re-runs.

## PREMISE (verified at drafting, pinned into the fixtures — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`
pre-registration, cross-checked at start) and touches no repo state, no
network, no wall clock. The parent's constants travel INSIDE the fixture:
V027's committed regime mixtures, its committed Feas map (the chained
anchor), its C48 identity, and the two empirical multisets the idea file
measured at drafting (11 work-claim lifetimes, median 2.65 h; 19 heartbeat
re-stamp gaps, median 1.08 h — the first fleet datapoint of its kind,
reporting-only brackets). Thirteen intake-time decisions are disclosed in
`fixtures.json` — most load-bearing: the overdue convention (the unique
reading under which the registered run-exposure formula AND the registered
p_f = 0 ⇒ zero-exposure self-check are both satisfiable, decisions 1–3), the
death-age convention with its registered-formula match (decision 4), and the
**≥ 2.5σ gate pre-check rule with its handling protocol pinned BEFORE any
run** (see What it settled, item 4). The fixture was committed before the
runner was written; a fixture amendment pinning the leg-E forget probability
also predates the runner (git history is the trail).

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Lane:** claims at t = 0 (the claim event carries a fresh `renewed:`
  stamp), wakes deterministically every p_w ∈ {2, 12, 24} h (N = 84/14/7
  wakes over the decision-binding hold H_c = 168 h), re-stamps at each wake
  EXCEPT an i.i.d. forget with p_f ∈ {0.02, 0.10, 0.25} — the compliance axis
  no prior grid carries. **Death:** with p_d = 0.10 the lane instead dies
  silent at a uniformly chosen wake (p_d deliberately NOT a decision axis —
  T conditions on alive claims, O95 on dead ones; V027's construction).
- **Observer:** contenders check at Poisson λ_c and take over any claim whose
  renewal is overdue past θ_r ∈ {6, 12, 24, 48, 72} h (a stamp is current
  until its successor due time s + p_w; takeable at t > s + p_w + θ_r).
  Metrics composed worst-case-per-metric: **T at λ_c = 1/4 h⁻¹** (fastest
  tempo), **O95 at λ_c = 1/12 h⁻¹** (slowest decision tempo); the C48 column
  reporting-only via the restated identity. The planted
  `WORK_CLAIM_STALE_HOURS = 72` is in-grid by design.
- **Arm A (decision-carrying, exact):** trailing-run DP for T; closed-form
  piecewise quantile for O95 (age distribution
  P(A = m·p_w) = (1/N)·p_f^m·(1 + (N−m−1)(1−p_f)), derived two independent
  ways and asserted equal in exact Fractions). Cross-arms: an independent
  exposure-distribution DP agrees to 1e−9 on all 45 points; a full 2^N
  exact-Fraction brute force agrees to 1e−12 on every p_w ∈ {12, 24} point.
- **Arm S (validation):** event-driven MC, M_S = 4,000 per point,
  `random.Random(20260756)`, pinned loop order and per-claim draw layout.
  Registered gates |T_S − T_A| ≤ 1.0 pp, |O95_S − O95_A| ≤ max(4 h, 5%);
  **effective tolerance = max(registered, 2.5σ of the predicted estimator)**
  per the fixture's pre-check rule. Stability leg seed 20260757 (M = 1,000)
  must reproduce the ruling. Reporting legs seed 20260758 (wake jitter,
  H_c ∈ {4, 24}, p_d ∈ {0.02, 0.30}, the exact C48 column, the
  empirical-anchor leg at the quoted multisets). Aux stream seed 20260759
  (exact-identity legs + 16× diagnostics). Seeds 20260756–59 sit strictly
  above the P027 registry high-water 20260755 (P028 drew zero).
- **Chained anchor:** a silence-keyed baseline leg re-computes V027's
  committed closed forms at its committed regime constants and must reproduce
  its committed Feas map EXACTLY — run invalid on mismatch.
- **Decision rule (registered before any code; evaluated in this order):**
  Feas(cell) = {θ_r : T ≤ 0.05 AND O95 ≤ 120 h}. **REJECT first**
  (Feas = ∅ in ≥ 5/9 cells); APPROVE (∃ single θ_r† feasible in ≥ 8/9,
  gates + stability holding) with the pinned row; NULL otherwise.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**(1) The chained anchor reproduced — twice.** In-sim: the silence-baseline
leg recomputed V027's 9 × 6 atlas from its committed closed form and regime
constants and reproduced the committed Feas map EXACTLY (feasible cells
{R1-C4: {48, 72}, θ* = 48; R1-C12: {24, 48, 72}, θ* = 24; R2-C12: {72},
θ* = 72}; all six other cells empty). Out-of-sim, before this build: the
committed V027 runner re-run in a scratchpad copy produced `results.json`
byte-identical to the committed file at main `fcb39e3` (exit 0, 4,975,945
self-checks). The ΔFeas headline is therefore clean: **silence-keyed 3/9
cells feasible → renewal-keyed 9/9 cells non-empty on the SAME bands** (exact
arm).

**(2) Arm A — the exact feasibility atlas.** NO cell is infeasible — REJECT
(checked FIRST, the protect-the-build-budget arm) misses by the full margin
(0/9 vs ≥ 5/9). The orphan band binds nowhere in the decision cells (max
O95 = 107.9 h < 120 at θ_r = 72), exactly as the registration disclosed —
renewal moves the whole game to the twin side. T_A per cell (pp), bold =
infeasible at that θ_r:

| cell (p_w, p_f) | θ=6 | θ=12 | θ=24 | θ=48 | θ=72 | Feas | θ* |
|---|---|---|---|---|---|---|---|
| 2 h, 0.02 | 0.0005 | ~0 | ~0 | ~0 | ~0 | all 5 | 6 |
| 2 h, 0.10 | 0.31 | 0.0003 | ~0 | ~0 | ~0 | all 5 | 6 |
| 2 h, 0.25 | **10.50** | 0.17 | ~0 | ~0 | ~0 | {12…72} | 12 |
| 12 h, 0.02 | **19.70** | 0.48 | 0.009 | ~0 | ~0 | {12…72} | 12 |
| 12 h, 0.10 | **67.95** | **10.86** | 1.04 | 0.009 | ~0 | {24…72} | 24 |
| 12 h, 0.25 | **95.36** | **49.10** | **13.41** | 0.73 | 0.037 | {48, 72} | 48 |
| 24 h, 0.02 | **13.05** | **12.57** | 0.24 | 0.004 | ~0 | {24…72} | 24 |
| 24 h, 0.10 | **51.76** | **50.30** | **5.44** | 0.46 | 0.037 | {48, 72} | 48 |
| 24 h, 0.25 | **86.30** | **85.04** | **28.10** | **6.22** | 1.27 | {72} | 72 |

Coverage per θ_r: 6 → 2, 12 → 4, 24 → 6, **48 → 8, 72 → 9 (all nine)**. Both
APPROVE-shaped horizons exist: θ_r† = 48 h by the registered min-selection
rule (coverage 8/9, all but daily-sloppy), and the planted 72 h is the unique
FULL-coverage horizon (9/9) — the planted constant does NOT lie at the
min-rule θ_r† but is the only horizon feasible everywhere. Compliance floor
at θ_r† = 48: p_f = 0.10 (at p_w = 24 the sloppy column busts it: T = 6.22 pp);
at 72 h the floor is the full swept range 0.25. Per-axis medians θ*: cadence
6 → 24 → 48 h across p_w; compliance 12 → 24 → 48 h across p_f. No knife-edge
point exists (nearest T_A to the band: 5.44 pp at (24 h, 0.10, 24)).

**(3) Arm S agrees; stability reproduces.** The MC decision applied to its
own measured values = the same pattern with the same tables (0/9 infeasible);
the stability leg (seed 20260757, M = 1,000) reproduces the exact-arm pattern
(same θ_r† = 48). Exact-identity legs: p_f = 0 alive claims realized ZERO
steals (4,500 claims); θ_r → ∞ produced T = 0 exactly and zero takeovers; all
draw-count sentinels rejoined their streams; 1,691,638 self-checks, 0 failed.

**(4) The gates — and why the ruling is NULL, not APPROVE.** The registered
absolute gates (1.0 pp / max(4 h, 5%)) were pre-checked in the fixture
against closed-form SEs BEFORE any draw, per the registration's own ≥ 2.5σ
design rule: the pre-check found them sub-2.5σ on mid-range points (the V027
lesson realized a second time — 2.5σ ≈ 1.24% two-sided per boundary point)
and RAISED those points to exactly 2.5σ, with the residual false-breach risk
accepted and disclosed in writing before the run. Measured: registered-gate
breaches 2/45 (T) + 5/45 (O95); **effective-gate breaches 1 + 1 of 90**
(pw12-pf0.25@72: z_O95 = 2.73σ; pw24-pf0.25@12: z_T = 2.51σ — a reporting
point, not near any band). Both re-measured at 16× (M = 64,000) on the aux
stream: residuals 0.007 pp / 1.12 h and 0.12 pp / 0.81 h — **far inside the
same tolerances: sampling noise, not model disagreement** (max z anywhere in
the 90-gate table: 2.73σ). Handling, pinned before the run: an
effective-gate breach BARS APPROVE and can neither create nor destroy
REJECT/NULL. The registered evaluation order therefore lands: REJECT no
(0/9), APPROVE barred, **NULL** — with the conditional rule as the citable
finding, exactly as the registration's honest-null clause provides. The
ruling is not bent toward APPROVE by the 16× diagnosis: the diagnostics
distinguish noise from model error for the READER; they do not un-bar the
clause.

**(5) Reporting-only context (registered as unable to flip).**
- **Wake jitter is the mechanism's real boundary.** Under exponential jitter
  at the same MEAN cadence (grace kept at nominal p_w), T explodes:
  (24 h, 0.10) @ θ_r = 24: 79.0 pp vs 5.4 on the lattice; @ 48: 31.9 vs 0.46;
  (24 h, 0.25) @ 72: 19.0 vs 1.27. An irregular waker reads delinquent under
  a fixed grace even at perfect compliance — the pinned row is conditional on
  cadence REGULARITY, not just cadence rate (the kit's Stop-hook reminder is
  load-bearing, and the grace must budget the gap tail, not the mean).
- **The measured claim class barely meets the mechanism.** The
  empirical-anchor leg at the quoted multisets (H_c from the 11 lifetimes,
  gaps from the 19 re-stamp gaps, grace 1.08 h): T = 0 at every θ_r — tonight's
  median-2.65 h claims complete before any swept horizon can bite; O95 ranges
  41–112 h. The renewal mechanism prices multi-day claims; the sub-day class
  is protected by completion itself.
- **p_d sensitivity flat** (T at (24 h, 0.10) @ 48: 0.61/0.44/0.29 pp across
  p_d = 0.02/0.10/0.30 — within noise; the p_d-free construction holds).
- **C48 restated:** exact renewal-side O95 at λ_c = 1/48 spans 148.5–215.8 h —
  every point above the 143.795 h distribution-free floor (= ln 20/λ_c;
  stronger than V027's silence-side identity since (θ_r − A)⁺ ≥ 0) and above
  the 120 h band: sparse-checked lanes remain unmeetable under ANY signal
  design. **θ_r = 168 exclusion:** exact O95 = 201.4–203.9 h per cell — all
  far above 120 (the idea file's "≥ 203.9" shorthand is exact only in the
  p_f → 0 limit; the exclusion itself is unaffected — disclosed, intake
  decision 12).
- **H_c legs:** at H_c = 4 h no swept cell wakes often enough to expose
  (T = 0 everywhere); at H_c = 24 h eager horizons already twin sloppy lanes
  (θ_r = 6: T = 36.4 pp at p_w = 12, p_f = 0.25).

## What it did NOT settle

- **The mechanism recommendation itself.** The exact arm met the APPROVE
  bands (8/9 at 48 h, 9/9 at 72 h) but the run's own pre-pinned validation
  contract barred the APPROVE stamp on a 2-of-90 gate breach diagnosed as
  pure sampling noise. What converts it: a re-registration at M_S ≈ 16,000
  (making the registered absolutes ≥ 3σ: worst T point needs
  n_alive ≥ ~11,500; the O95 gate needs n_dead ≥ ~1,540), or per-point
  tolerances registered as familywise-calibrated SE multiples (≈ 3.5σ over 90
  gates → expected breaches 0.04). Either is a mechanical re-run of committed
  art — no new modeling.
- **Real compliance.** p_f is swept, not measured — no fleet datapoint exists
  until the `renewed:` field ships; i.i.d. forgetting is the disclosed weakest
  joint (correlated forgetting — a sick harness missing EVERY renewal — sits
  between the sweep and lane death). The registered live probe measures it:
  ship the field warn-first, count missed-renewal warnings per lane-week.
- **Real cadence regularity.** The jitter leg brackets it (reporting-only):
  deterministic-cadence twin-safety does NOT transfer to exponential-jitter
  wakers at the same mean. A grace keyed to the measured gap tail (the
  heartbeat multiset's max is 5.5 h against a 1.08 h median) is design input
  for the kit lane, not a constant this sim pins.
- **Adversarial silence / contender contention** — out of scope by
  registration (V027's boundaries inherited).
- **The materiality lines.** 0.05 / 120 h / 8-of-9 / 5-of-9 are inherited
  pre-registered judgments; full curves ship, a re-drawn line re-reads.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The question is about a modeled renewal race by design (the mechanism does
not exist yet — that is the point of pricing it pre-build). The two
abstractions that could flip a builder's reading are both measured here
rather than assumed away: compliance (swept as a decision axis — the first
grid to carry it) and cadence regularity (the jitter leg brackets its failure
mode at the same mean cadence). The contender-side boundary is
distribution-free arithmetic (C48 ≥ 143.8 h for ANY signal design). The
declared flip alternative — the real, possibly correlated forget process —
is the registered live probe's exact target.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **1,691,638 self-checks, 0 failed**, exit-coded: the decision arm is
exact (trailing-run DP + closed-form quantile) and is triple-checked — an
independent exposure-distribution DP agrees to 1e−9 on all 45 points, a full
2^N exact-Fraction brute force agrees to 1e−12 on all 30 p_w ∈ {12, 24}
points, and the age distribution is derived two independent ways and asserted
equal in exact Fractions; four hand-derived pins (single-full-run identity,
the p_f = 0 O95 closed form, the C48 dominance floor, the θ→∞ exact zero);
the registered exact-identity legs both land exactly; per-leg draw-count
sentinels rejoin all four streams; the chained anchor reproduces the parent's
committed map exactly. No seeded luck: the ruling rides the exact arm; the
stability seed reproduces the pattern; the ONLY seed-sensitive outcome (the
2-of-90 gate breach) was disclosed as a quantified pre-run risk, is shipped
with z-scores, and its handling was pinned before the first draw — it could
not be resolved in APPROVE's favor after the fact, and was not.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The band arithmetic is nowhere near an edge: REJECT misses 0/9 vs 5/9; the
feasibility atlas has NO knife-edge point (nearest miss 5.44 pp vs the 5 pp
band, nearest pass 1.27 pp below); flipping every point within 0.2 pp of the
band changes nothing (the set is empty). Coverage 9/9 at 72 h has a full-cell
margin over the 8/9 bar. The NULL-vs-APPROVE boundary is the one seed-level
edge, and it is governed by the pre-pinned protocol, not by judgment applied
after seeing the draw.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own `fixtures.json`). Pinned seeds, pinned loop order, pinned per-claim
draw layout, counted streams. stdout AND `results.json` byte-identical across
TWO complete process runs by external `diff` (sha256 stdout `e71c191a…`,
results `5245a14b…`) on cpython-3.11 (pinned and asserted). ~9 s per run.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure any real lane's compliance or cadence regularity (those
are the named live probe and the jitter bracket); it prices a modeled race
under declared neutral assumptions. It does not ship an APPROVE mechanism
row — the conditional table is the deliverable, pending the named cheap
re-registration or the live counter. It says nothing about adversarial lanes,
contender arbitration, or horizons for the sub-day claim class (which
completes before the mechanism engages).

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying arm is exact (zero sampling error on all 45 points,
triple-cross-checked, four hand pins); every constant, band, seed and the
evaluation order were registered before any code; the chained anchor
reproduces the parent's committed map exactly; and the one stochastic element
of the ruling — the 2.5σ gate contract — was calibrated, risk-quantified, and
protocol-pinned in the fixture before the first draw. The honest boundary:
the NULL is a validation-contract outcome, not a band outcome; the exact-arm
feasibility numbers are as strong as the parent's and ship in full.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `null` — finalized, not a re-run request.** By the rule
  committed before any code, evaluated in the registered REJECT-first order:
  REJECT misses by the full margin (0/9 infeasible cells vs ≥ 5/9); APPROVE's
  band condition is met on the exact arm (θ_r† = 48 h covers 8/9; 72 h covers
  9/9; stability reproduces) but is BARRED by the pre-pinned gate protocol
  (2 of 90 effective point-gates breached at z = 2.51σ/2.73σ, both converging
  at 16× — sampling noise, disclosed as an accepted pre-run risk); NULL lands
  with the conditional rule as the citable finding.
- **The conditional rule (the citable finding, exact-arm numbers):**
  renewal-keyed expiry clears BOTH V027 bands in EVERY swept cell at
  **θ_r = 72 h** — the planted `WORK_CLAIM_STALE_HOURS = 72`, read onto the
  renewal stream, is the unique full-coverage horizon in the grid — and at
  **48 h** everywhere except daily-cadence × sloppy (p_w = 24, p_f = 0.25).
  Required horizon scales with cadence × compliance (median θ*: 6 → 24 → 48 h
  across p_w; 12 → 24 → 48 h across p_f). Compliance floors: 0.25 at 72 h,
  0.10 at 48 h. ΔFeas over the parent: silence-keyed 3/9 → renewal-keyed 9/9
  non-empty on shared bands — **the routed signal fixes the parent's
  infeasibility in-model**, conditional on the compliance and regularity
  boundaries above.
- **The pre-registered NULL consequence, verbatim:** the conditional
  per-cadence/per-compliance rule ships, and the cheapest LIVE probe is
  named — ship the `renewed:` field warn-first and count missed-renewal
  warnings per lane-week; p_f, the axis this sim can only sweep, becomes
  MEASURABLE the day the field exists, at zero extra tooling.
- **Reading for the kit-lane designer (reporting-only):** the jitter leg is
  the sharpest design input — twin-safety at a fixed grace collapses under
  irregular wakes at the same mean (79 pp vs 5.4 pp at daily/typical,
  θ_r = 24), so the grace must budget the measured gap TAIL (max 5.5 h vs
  median 1.08 h in the quoted multiset), and the Stop-hook renewal reminder
  is load-bearing, not cosmetic. The measured sub-day claim class (median
  2.65 h) completes before any swept horizon engages — the mechanism prices
  multi-day claims.
- **Cheapest conversion to a mechanism verdict (named follow-up, not
  ordered):** re-register the identical committed sim at M_S ≈ 16,000 (the
  registered absolute gates become ≥ 3σ) or with familywise-calibrated
  SE-multiple tolerances (~3.5σ over 90 gates), and re-run — pure mechanics,
  no new modeling; the V027 pipeline lesson now has two data points
  (per-point 2.5σ contracts across ~90 gates carry ~50% aggregate breach
  odds; calibrate familywise, not per-point).
- **Model basis (declared, scope-limiting):** deterministic-cadence wakes ×
  i.i.d. forgets × Poisson checks; the single most-likely-to-flip alternative
  is the real (correlated) forget process — exactly what the warn-first
  counter measures.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015-V030 slice boundary, with header timestamps from live
`date -u` at append time. -->
