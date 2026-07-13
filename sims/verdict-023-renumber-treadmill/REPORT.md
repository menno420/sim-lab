# REPORT — migration renumber-treadmill residual (PROPOSAL 021)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 021** ·
> 2026-07-13T02:36:37Z · status: sim-ready (idea
> `ideas/superbot/migration-renumber-treadmill-residual-2026-07-13.md`, landed via
> idea-engine PR #287, main `8022a9d`). The ORDER 004 rule-3 FLEET-BACKLOGS rotation
> slot, round 2 — the deepest, barely-tapped backlog (superbot's 237-doc index).
> Harvest source: the captured migration-number-collision-guard doc @ `fd638e3`
> (byte-same at superbot live HEAD `4522522`; Option-1 checker answering 200) — the
> doc's own open fork: Option 1 (shipped re-pick-at-push checker) vs Option 3
> (assign-number-at-merge, "the real fix but a meaningful infra change"). Fully
> hermetic (the PROPOSAL 017/018/019/020 precedent): every fixture is a pinned
> constant committed with the sim; zero repo/network reads in the verdict session.
> Run: `python3 sims/verdict-023-renumber-treadmill/renumber_treadmill_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic policy-grid
sweep, band-scored, dual-arm): a continuous-time event simulation of the
shared-append-point migration-number race driven through the full 9-cell ×
3-policy endogenous grid at M=40 seeded replications per (cell, policy),
`random.Random(20260723)` in the pinned loop order, GATED by an exact
seedless analytic arm (the exogenous single-PR closed forms) that the same
engine re-run in exogenous mode must reproduce within 1.0 pp; all decisions
computed in exact `Fraction` arithmetic on pooled integer counts (no floats
in the decision path). This label fills the outbox `evidence: simulation`.
The one judgment question — whether 0.10 renumbers/PR, 1% and 5% treadmill
share are the RIGHT lines — was pinned by pre-registration in the idea file
and is disputable only about the bands, never about the measured numbers.

## PREMISE (verified this session — hermeticity by construction)

The proposal's premise: fully hermetic, every fixture a pinned constant
committed with the sim. Verified HONESTLY: the sim reads exactly ONE file
(its own committed `fixtures.json`, the pre-registration) and touches no repo
state, no network, no wall clock; every constant ({λ-grid, V-grid, W, d, H,
warm-up, M per leg, seeds 20260723–26, band constants, per-policy pick-time
definitions}) was copied verbatim from the idea file into `fixtures.json`
BEFORE the runner was written, and the runner cross-checks its literals
against that file at start. Intake-time decisions, disclosed in
`fixtures.json` before any code ran: sensitivity/jitter legs at M=8 (the idea
file leaves their M unpinned; the stability leg's committed scale — the
VERDICT 021 precedent); the jitter redraw granularity (W per PR, V per
validation round, d per fix); the warm-up population convention (merge
instant > 200 h, full per-PR attributes); the p95 and inflation conventions;
and the exogenous-leg truncation (each focal PR simulated through its first
TWO rounds — N recorded as 0/1/≥2, all the gate reads; necessitated by the
closed form's own arithmetic: E[N] ≈ 2.1×10⁵ rounds per focal PR at the
harshest cell). ONE post-runner amendment, disclosed in-place in
`fixtures.json`: hand-pin HAND-1's expected duration sum carried a
hand-arithmetic slip (10 + 12.5 written as 23.5), corrected to 22.5 after
the engine AND the independently-written replay both computed 22.5; every
other pin value stood as derived, and no decision constant was touched.

## What the sim MODELS

The shared-append-point migration-number race as a continuous-time event
process. All constants pre-registered in `fixtures.json`:

- **Lifecycle:** migration-bearing PRs arrive Poisson λ ∈ {1, 4, 12}/day
  ({1/24, 1/6, 1/2}/h) over H = 2,000 h; develop W = 8 h (open → push);
  validate V ∈ {0.25, 2, 24} h (auto-merge fast-lane / same-day review /
  held-for-review — #1279's class); at the merge attempt, if the held number
  was merged by another PR since pick → **collision**: renumber (fix latency
  d = 0.5 h), re-validate (another V), re-attempt. First 200 h discarded as
  warm-up; metrics on the post-warm-up merged population, pooled over M=40
  replications.
- **Number arithmetic:** pick = max(main)+1 at the pick instant; collision at
  attempt iff held ≤ max(main); main stays contiguous by construction
  (every successful merge lands exactly max+1 — a checked invariant). Events
  processed in (time, PR id) order (ties by PR id, pre-registered).
- **Policies (pick time only):** **P0** picks at open + at each fix start
  (round-1 exposure W+V, later rounds d+V — the pre-2026-06-22 world);
  **P1** re-picks at every push (every round's exposure = V exactly — the
  shipped Option-1 checker's semantics); **P3** assigns at the merge instant
  (exposure 0; MUST measure exactly zero collisions — the built-in control).
- **Metrics:** R = renumbers per merged PR; T = share of merged PRs with ≥ 2
  renumbers (the treadmill class — #1279's class); reporting-only: mean/p95
  open→merge inflation vs the same cell's P3, max simultaneous holders of one
  number, and R_endo/R_exo with R_exo = Arm A's exact E[N].
- **Arm A (exact, seedless):** with p(w) = 1 − e^(−λw) and per-policy windows
  (w₁, w₂) — P0: (W+V, d+V); P1: (V, V) — P(N≥1) = p(w₁), P(N≥2) =
  p(w₁)·p(w₂), E[N] = p(w₁)·e^(λw₂), every cell × {P0, P1}, each computed
  twice by independent float paths.
- **Validation gate (run INVALID if failed):** Arm S re-run in EXOGENOUS mode
  (appends = external Poisson at λ modeled as instant-merge external PRs
  through the SAME engine, one focal PR, M=20,000 per cell-policy, seed
  20260726) within **1.0 pp absolute** of Arm A on P(N≥1) and P(N≥2) in all
  36 covered comparisons; AND endogenous P3 exactly zero collisions.
- **Decision rule (registered in the idea file before any code; evaluated in
  this order on the ENDOGENOUS P1 cells):** **APPROVE** iff R ≤ 0.10 AND
  T ≤ 0.01 in ≥ 8 of 9 cells, gate passed (checked FIRST — the build-nothing
  arm); **REJECT** iff T > 0.05 in ≥ 5 of 9 cells (attach the per-cell
  residual-tax table); **NULL** otherwise (flip axis named via per-axis
  APPROVE-pass shares and median T).
- **Legs:** primary (decision); stability M=8 seed 20260724 (must reproduce
  the ruling); reporting-only sensitivity d ∈ {0.25, 2}, W ∈ {1, 24} (M=8);
  jitter seed 20260725 (W/V/d redrawn exponentially at the pinned means);
  the #1279 anchor (λ=12/day, V=2, d=0.5, P0).

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json` (exact fractions kept for the primary leg).

**(1) APPROVE fails first (checked first): 2/9 cells pass, vs the ≥ 8 bar.**
Only the two fast-lane cells at calm/busy rates clear both bands:
λ=1/day·V=0.25 (R = 1/99 ≈ 0.0101, T = 0) and λ=4/day·V=0.25 (R ≈ 0.0445,
T ≈ 0.0026). The shipped checker's residual is not negligible fleet-wide.
Disclosed near-miss: λ=1/day·V=2 sits at R = 63/607 ≈ 0.1038 — 3.8% OVER the
0.10 band (T = 0.0092, inside) — decision-irrelevant at 2 vs 8 either way.

**(2) REJECT binds: T > 0.05 in exactly 5/9 cells (bar: ≥ 5) — margin-heavy
membership, identical in all seven legs.** The pre-registered residual-tax
table (endogenous P1, primary leg; inflation = mean open→merge vs the same
cell's P3):

| cell (λ/day · V h) | R | T | mean infl vs P3 | p95 infl | max holders | T > 0.05? |
|---|---|---|---|---|---|---|
| 1 · 0.25 | 0.0101 | 0.0000 | 1.001 | 1.00 | 2 | no |
| 1 · 2 | 0.1038 | 0.0092 | 1.026 | 1.25 | 3 | no |
| 1 · 24 | 6.185 | 0.7411 | 5.735 | 14.78 | 27 | **yes** |
| 4 · 0.25 | 0.0445 | 0.0026 | 1.004 | 1.00 | 3 | no |
| 4 · 2 | 0.5668 | 0.1333 | 1.142 | 1.75 | 6 | **yes** |
| 4 · 24 | 18.840 | 0.8456 | 15.424 | 43.11 | 293 | **yes** |
| 12 · 0.25 | 0.1487 | 0.0209 | 1.014 | 1.09 | 4 | no |
| 12 · 2 | 44.408 | 0.8696 | 12.102 | 44.00 | 149 | **yes** |
| 12 · 24 | 18.833 | 0.8464 | 15.419 | 42.34 | 967 | **yes** |

The five reject cells run T = 0.133–0.870 — 2.7× to 17× the 0.05 band; the
nearest NON-member (λ=12·V=0.25) sits at T = 0.021, 42% of the band. The
same five-cell set reproduces in the stability leg, the jitter leg, and all
four sensitivity legs. The cell-count lands exactly at the bar (5), but
membership is nowhere near knife-edge.

**(3) The headline deliverable — endogenous amplification is real and
double-sided.** R_endo/E[N]_ArmA per P1 cell: ≈ 1.0 where collision pressure
is light (0.965–1.19 at V=0.25 and the calm V=2 cells), **25.8× at
(λ=12/day, V=2)** — Arm A prices E[N] = 1.72, the coupled system measures
R = 44.4: every renumber delays a merge, delayed merges bunch, bunched
merges collide everyone else — the positive feedback the idea file said no
closed form prices. At the saturated cells (V=24, λ ≥ 4/day) the ratio
COLLAPSES (0.35 at λ=4, 0.0001 at λ=12, where Arm A's E[N] = e^(λ(d+V)) ≈
1.6×10⁵): the treadmill destabilizes the system, merge throughput falls
below λ (in-flight PRs pile up hundreds deep, max simultaneous holders of
one number reaches 967), and the exogenous form — which assumes appends keep
landing at λ — overprices a pressure the system can no longer sustain. The
closed form is neither a bound nor a proxy in the hot cells; only the
endogenous measurement prices the middle of the grid, in both directions.

**(4) The latency tax (the Option-3 evidence row's second column).** Where
the treadmill binds, P1's open→merge inflation vs P3 runs 1.14× (λ=4·V=2)
to **15.4×** (mean 493.6 h vs 32.0 h at λ=4·V=24), p95 up to 44×. P3's
measured mean equals W+V exactly in every cell (the control behaving as
constructed). Under P0 the same cells run 1.03×–23.1×.

**(5) The #1279 anchor (plausibility vs an n=1 anecdote, never a fit).** At
the incident's class (λ=12/day, V=2, d=0.5, P0), Arm A gives E[N] = 3.47,
P(N≥3) = 0.506, P(N≥4) = 0.361 — a four-renumber afternoon is a ~36% event
even in the exogenous approximation, i.e. comfortably inside the model's
mass. The endogenous measurement at that cell is far harsher (R = 88.5,
share ≥ 4 = 0.976): the recorded incident is what this model considers
ordinary, not tail.

**(6) Validation gate + stability (the run is VALID).** Exogenous Arm S vs
Arm A: max |dev| = **0.684 pp** (at λ=12·V=2, P0, P(N≥2)) across all 36
comparisons vs the 1.0 pp gate; endogenous P3 measured exactly ZERO
collisions on every leg (per-replication checks on primary, stability, all
sensitivity, jitter). The stability leg (M=8, fresh seed 20260724)
reproduces REJECT with the identical five-cell reject set; the jitter leg
(all windows exponential — no fixed-window knife-edging) and all four
sensitivity legs (d halved to 0.25, d quadrupled to 2, W=1, W=24) also land
REJECT with the identical reject set (their only movement: the near-miss
λ=1·V=2 cell drifts across the 0.10 R-line on the APPROVE side, 3 passes
instead of 2 — never decision-relevant).

## What it did NOT settle

- **Which cell superbot actually occupies.** λ, V, W, d are pinned dials,
  not measurements (the pre-registered models-are-models boundary). The
  named cheap locator stands even under this REJECT: one `git log` pass over
  `migrations/` merge timestamps and PR open/push/merge times gives the
  repo's real (λ, V, W, d) — worth running before the Option-3 build is
  scheduled, to know how hot the lane actually is.
- **Arrival law:** Poisson arrivals by pre-registration; the endogenous mode
  generates bunching from the mechanism itself and the jitter leg redraws
  every window, but exogenous burst processes are out of scope by design.
- **Uniform compliance (the direction of error is known):** every simulated
  author runs the checker on every push under P1 — real compliance is ≤
  that, so P1's simulated residual is a FLOOR and the REJECT is the
  CONSERVATIVE reading (an APPROVE would have been the fragile direction).
- **One repo, one sequence:** cross-repo or per-directory number sequences
  are not modeled.
- **What Option 3 costs to build.** This verdict prices what NOT building it
  costs (the residual-tax table); the infra effort side of the ledger is the
  Option-3 plan's own question.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The model abstracts PR life to {Poisson open, fixed develop, fixed validate,
fixed fix latency} with a single integer append point — no CI queueing, no
human batching, no partial compliance. The load-bearing conclusion (the
checker's residual treadmill is catastrophic wherever λ·V ≳ 1 and material
at λ=4/day·V=2) is swept across a 3×3 grid that brackets the anchor
incident's class on both axes, and the two known gaps push in DIFFERENT,
disclosed directions: compliance < 1 makes live STRICTLY WORSE than P1's
floor (strengthens REJECT), while the pinned dials could place the live repo
in a calm cell (the git-history probe is the named locator). No gap silently
favors the ruling.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **16,857 self-checks, 0 failed**, exit-coded: per-replication main
contiguity (every merge lands exactly max+1), max_main ≡ total merges,
collisions ≡ renumbers, treadmill-count and warm-up-subset identities, P3
zero-collision + exact-duration (W+V) controls on every endogenous leg, P3
merged-count reconciled against the arrival list; an INDEPENDENT
re-implementation (no heap — min-scan scheduling, SET-membership collision
test, max-holders recomputed from an interval-overlap sweep instead of the
engine's acquire-time counter) agrees EXACTLY — including float duration
sums — on strided traced replications across all seven endogenous legs plus
both hand pins; the exogenous leg is replayed by an interval-membership
re-formulation on 200 strided focal PRs; two fully hand-derived pin
scenarios (derivations committed in `fixtures.json`; HAND-2 exercises the
chained two-collision treadmill and the warm-up filter at two warm-up
values) pass; draw-count accounting closes exactly on every leg (arrival
draws = arrivals + reps; jitter draws = 2·arrivals + 2·collisions; exogenous
draws = appends + focal count); Arm A computed twice by independent float
paths; every fixture constant cross-checked against the committed
pre-registration at start; the decision computed twice by
independently-written evaluators (Fraction comparison vs integer
cross-multiplication) agreeing on ruling and both cell sets. No seeded luck:
all four seeds pre-registered in the idea file, and a DIFFERENT seed
reproduces the ruling and the exact reject set. No cherry-picking: the full
9×3 table is committed for every leg. One found-and-fixed bug is disclosed
here rather than hidden: the first run's replay twin missed censored holders
(holds still open at H) in its interval sweep — the twin was wrong, the
engine right; fixed and re-run in full. The HAND-1 duration-sum amendment is
disclosed in the PREMISE section and in `fixtures.json` itself.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The REJECT's cell count lands exactly at the bar (5 of 9 vs "≥ 5") — that is
the honest edge, and it survives every variation swept: the five member
cells clear the T band by 2.7×–17× (the nearest non-member is at 42% of the
band, a 2.4× gap to membership), and the IDENTICAL five-cell set reproduces
under a fresh seed, exponential windows (jitter), d ∈ {0.25, 2}, and
W ∈ {1, 24}. For the count to drop below 5, some member's T would have to
fall 63% (λ=4·V=2, the weakest member at 0.133) — while the pre-registered
compliance boundary says live can only be WORSE than the simulated floor.
The one knife-edge found (λ=1·V=2's R at 3.8% over the 0.10 APPROVE band)
belongs to the APPROVE test, which fails 2 vs 8 regardless.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, no network / git / wall clock /
`hash()`; one `random.Random(<pinned seed>)` stream per leg in the pinned
loop order. stdout AND `results.json` byte-identical across TWO complete
process runs by external `diff` + `cmp` on cpython-3.11 (pinned in
`fixtures.json` and `results.json`, asserted at start). Runtime ~58 s.

**5. "LIMITS? what this evidence does NOT show."**
It does not show which grid cell superbot occupies (the git-history probe is
the named locator); does not model burst arrivals beyond
mechanism-generated bunching, CI-capacity coupling, partial compliance
(floor stated), or cross-repo sequences; prices the latency tax in model
hours against P3, not in wall-clock or developer attention; and prices
nothing on the build-cost side of Option 3. The anchor leg is a
plausibility check against an n=1 anecdote, never a fit.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Every constant, band, seed, and the evaluation order were registered in the
idea file before any code; the decision arithmetic is exact (pooled integer
Fractions, twin evaluators); the simulator is gated by an exact analytic arm
it reproduces to 0.68 pp; a second seed and five perturbation legs reproduce
the ruling with the identical reject set; and the two edges that exist (the
5-of-9 count at the bar; the λ=1·V=2 APPROVE near-miss) are disclosed with
their margins rather than absorbed. The honest boundary: this strength
attaches to the pinned model family — the live repo's own cell is unmeasured
and named as the follow-up probe.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — the shared append point must go; route the Option-3
  assign-at-merge build.** By the rule committed before any code (APPROVE
  checked first: 2/9 cells vs ≥ 8 — the build-nothing arm loses on its own
  terms): T > 0.05 in 5/9 endogenous P1 cells, every member 2.7×–17× over
  the band, membership identical across all seven legs. The per-cell
  residual-tax table {R, T, latency inflation vs P3} above rides to the
  Option-3 plan as its pre-registered evidence row.
- **What the checker is and is not (the priced difference):** Option 1 moves
  detection to push time and keeps fast lanes clean (V=0.25: R ≤ 0.045,
  T ≤ 0.0026 at λ ≤ 4/day) — but it cannot shrink the push→merge window,
  and wherever λ·V ≳ 1 the residual is a treadmill (T 0.13–0.87, latency
  5.7×–15.4×, renumber storms amplifying up to 25.8× over the single-PR
  arithmetic). "We have a checker" ≠ "the race is gone", now with numbers.
- **Per-PR-class reading (carried with the row, not instead of it):**
  auto-merge fast-lane PRs are safe at any swept rate below 12/day; same-day
  review (V=2) is safe only on a calm lane (1/day); held-for-review PRs
  (V=24 — #1279's class) are treadmill-bound at EVERY swept rate. The
  binding axis is V (approve-pass spread 0.667 vs λ's 0.333) — as the idea
  file predicted.
- **Consequence (pre-registered):** the Option-3 assign-at-merge design gets
  this evidence row (routed lane-side via the manager sweep, Q-0260 — the
  canonical doc is superbot's, never edited from here). Until Option 3
  lands, the cheap interim named by the class reading: keep held
  migration-bearing PRs OFF the shared sequence's hot path (their V is the
  poison), and run the git-history probe (one `git log` pass) to locate
  superbot's real (λ, V) cell before scheduling the build.
- **Riders (measured):** P1's residual is a FLOOR (uniform compliance
  pre-registered) — live can only be worse; the REJECT is the conservative
  ruling. Poisson-arrivals boundary stated: endogenous bunching is generated
  by the mechanism, exogenous bursts are out of scope. Model hours, not
  wall-clock.
- **Named follow-ups (not ordered):** the git-history probe (superbot's real
  cell at zero new tooling); the doc's own unfinished ask (wiring the
  shipped checker into the Stop hook / pre-pr step — still worth having
  UNDER Option 3 for the transition window); Option-3 plan's build-cost
  side.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V022 slice boundary, with header timestamps from live
`date -u` at append time. -->
