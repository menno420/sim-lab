# REPORT — book breadth vs versioning depth: fixed-budget allocation sweep (PROPOSAL 018)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 018** ·
> 2026-07-13T01:15:34Z · status: sim-ready (idea
> `ideas/venture-lab/book-versioning-breadth-depth-allocation-2026-07-13.md` @
> `cb2b6ee`, landed via idea-engine PR #283, main `d0dca70`).
> Grounding (pinned in the idea file, verbatim): the owner's BOOKS night-run
> directive, venture-lab `control/inbox.md` ORDER 008 @ `81c47ec` — "multiple new
> book ideas AND multiple versions of each (different angles, audiences, lengths)
> — versions are cheap once the research exists".
> Run: `python3 sims/verdict-020-book-versioning/book_versioning_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic,
parameter-swept), **fully hermetic** (the PROPOSAL 017 precedent): every fixture
is a pinned constant in `grid.json`, copied verbatim from the idea file; zero
repo/network reads in this verdict session by design. Two pre-registered arms:
Arm A (analytic, seedless — Simpson quadrature of the order-statistic integral,
stdlib `math.erf`) on the Mode P f=1 slice, and Arm S (seeded MC, M=20,000 per
(mode, cell, K), seeds 20260716/20260717, pinned loop order) on the full
2 × 81-cell grid. This label fills the outbox `evidence: simulation`.

## PREMISE (hermetic by pre-registration — nothing to verify live)

The proposal pre-registered the entire model, grids, seeds, bands, and decision
rule BEFORE any code existed; the sim constructs every fixture itself. The one
external premise — that the owner's directive contains an untested allocation
policy — was verified at drafting (raw fetch of ORDER 008 @ `81c47ec`, pinned in
the idea file) and is not re-verified here (fully hermetic session, per spec).
The spec at idea-engine HEAD `d0dca70` was re-read at intake and is followed
exactly as registered — no redesign.

## What the sim MODELS

A production night: budget **B = 12** (size leg B = 6, hit legs only — the
fractional-T_eff headline is B-invariant by linearity, stated and verified).
New title costs 1; each extra version costs **c ∈ {0.25, 0.5, 0.75}**; policy
**K ∈ {1, 2, 3, 4, 6}** versions per title; T_eff = B/(1+c·(K−1)). Title appeal
θ ~ N(0,1); version quality θ+ε, ε ~ N(0, σ_v²), **σ_v ∈ {0.2, 0.5, 1.0}**;
revenue exp(q+L) in relative units, L ~ N(−σ_m²/2, σ_m²) so E[exp(L)] = 1,
**σ_m ∈ {0.5, 1.5, 2.5}**. **Mode P (pick-best)**: publish 1 of K, true-best
picked with probability **f ∈ {0.2, 0.6, 1.0}**, else uniform. **Mode A
(publish-all)**: all K listed, R = (1−s)·max_i r_i + s·Σ_i r_i, audience
separation **s ∈ {0, 0.5, 1}**. Headline per cell: **K\* = argmax_K E[revenue
per unit budget]** = E[R_title(K)]/(1+c·(K−1)) and **ΔR = value(K\*)/value(1) − 1**.

Estimators (disclosed; the spec pins model/grids/seeds/M/draw order, not the
estimator formula): unbiased conditional-expectation / control-variate
estimators over exactly the pinned draws — required because the raw exp(q+L)
sample mean has relative SE ~26% at σ_m = 2.5 and could never satisfy the
pre-registered 1.5% Arm A/S gate at M = 20,000. Mode P integrates θ, L, the
pick draw, and the uniform branch out analytically and estimates E[exp(max ε)]
by a sign-flip-antithetic loser-sum control variate (zero-variance at K=1);
Mode A integrates θ out and uses the β=1 control variate on the exact identity
E[Σ exp(ε_i+L_i)] = K·e^{σ_v²/2}. Full formulas in `grid.json` and the sim
docstring. The raw revenue draws (θ and L exactly as drawn) feed the
distributional hit-probability legs unchanged. An **analytic diagnostic layer**
(the full mean structure is closed-form via the same quadrature — σ_m provably
inert in Mode P means since E[exp(L)] = 1) self-checks every Arm S cell; the
pre-registered arms and ruling are unchanged by it.

## What it SETTLED (the load-bearing claims — relative units only)

**(1) The two publication modes give OPPOSITE allocation defaults — the
pre-registered NULL, and the mode split is the finding.**

- **Mode P (pick-best): breadth dominates.** K\* = 1 in **69/81 = 85.19%** of
  cells (clears REJECT's own 80% line single-handedly); K\*≥2 in 12/81 =
  14.81%; **median ΔR = +0.0000**. K\* counts {1: 69, 2: 9, 3: 3, 4: 0, 6: 0}.
  Versioning only wins when THREE dials align — cheap versions AND wide version
  spread AND high selection fidelity: the only cells with ΔR > +0.10 are
  (c=0.25, σ_v=1.0, f=1.0) at K\*=3, **ΔR ≈ +0.27** (one per σ_m — σ_m
  measured inert in Mode P, per-axis K\*≥2 share exactly flat at 14.81%);
  every other winning cell gains ≤ +5.1%. At f=0.2 versioning NEVER wins a
  cell.
- **Mode A (publish-all): versioning dominates.** K\*≥2 in **72/81 = 88.89%**
  of cells (clears APPROVE's cell-share line), **median ΔR = +0.4062**;
  K\* counts {1: 9, 2: 5, 3: 6, 4: 6, 6: 55} — the grid-median K\* is 6, the
  top of the swept range. At s=1 every cell has K\*=6 with ΔR = 6/(1+5c) − 1
  (+166.7% / +71.4% / +26.3% by c) — pure ticket-count arithmetic. K\*=1
  survives only in the corner where versions are dear and both spreads small:
  the 9 losing cells all have (c ≥ 0.5, s ≤ 0.5, σ_m ≤ 1.5) with 7 of 9 at
  c=0.75.
- **Ruling per the pre-registered rule: NULL** — APPROVE fails (Mode P
  14.81% < 80% and median ΔR 0 < +0.10), REJECT fails (Mode A K\*=1 share
  11.11% < 80%). Neither "always version" nor "always breadth" may be cited as
  settled.

**(2) The named flip axes (pre-registered NULL obligation, tie-aware).** Per
mode, per-value K\*≥2 cell-shares:

- Mode P — **c, σ_v, f exactly tied** at spread 0.3333: c {0.25: 33.3%,
  0.5: 11.1%, 0.75: 0%}, σ_v {0.2: 0%, 0.5: 11.1%, 1.0: 33.3%}, f {0.2: 0%,
  0.6: 11.1%, 1.0: 33.3%}; σ_m flat at 14.81% (inert, as the model predicts).
- Mode A — **c, σ_m, s exactly tied** at spread 0.2593: c {0.25: 100%,
  0.5: 92.6%, 0.75: 74.1%}, σ_m {0.5: 74.1%, 1.5: 92.6%, 2.5: 100%},
  s {0: 74.1%, 0.5: 92.6%, 1: 100%}; σ_v spread only 0.1111.
- The proposal's expected candidates (s and f) are each on their mode's tied
  frontier, but the **publication mode itself is the binding fork**, with
  version cost c the only axis on BOTH frontiers.

**(3) The conditional rule (the citable finding).** Version-heavy allocation is
justified exactly when extra versions are actually LISTED and reach separated
audiences (Mode A, s > 0), or — under pick-best — only when versions are cheap
(c=0.25), genuinely different (σ_v=1), and the best one is reliably identified
(f=1). Under pick-best with realistic fidelity, breadth (new-titles-first) is
the measured default. The owner's "versions are cheap" clause (low c) is
necessary but NOT sufficient in Mode P: at c=0.25 versioning still loses 18 of
27 pick-best cells.

**(4) Hit-probability legs (reporting-only, integer T = ⌊T_eff⌋, B ∈ {6, 12} —
they cannot flip the decision and they do not).** Mode P: K=1 maximizes the
B=12 P(≥1 title beats the within-cell K=1 p90) in 73/81 cells — breadth also
wins the lottery-ticket framing under pick-best. Mode A: K=1 maximizes it in
only 8/81 cells. Full per-cell tables committed in `results.json` (both B
legs).

**(5) Arms agree; the run is valid per its own pre-registered gates.** Arm S vs
Arm A on every f=1 cell × K: **max relative deviation 0.240%** (gate 1.5%,
135 checks) — and Arm S reproduces the analytic K\* exactly, 27/27, on that
slice. Analytic diagnostic layer over ALL 810 (mode, cell, K) means: max
deviation 0.240% (P) / 0.836% (A). **Decision-stability leg** (M=2,000, seed
20260718, one stream): ruling **NULL reproduced** (shares 14.81%/88.89%
identical, medians 0.0/+0.4045).

## What it did NOT settle

- **Anything in currency.** Relative units only; the exp link pins quality
  elasticity at 1 (bracketed by the σ_m sweep, which spans
  quality-driven → lottery-drowned). This sim allocates effort; it never
  forecasts earnings — Q-0259 r.4 forecast discipline untouched.
- **The real values of s and f for the venture pipeline.** The whole NULL
  turns on them; they are model dials here, not measurements. The cheapest
  live probe is named below.
- **Adaptive K.** Static quota only; per-title adaptation on early signal is a
  named follow-up, not scope creep.
- **Cross-title cannibalization and demand saturation** — independence across
  titles is assumed by the model (and by the hit-leg independence formula).

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The lognormal discovery lottery and normal quality spread are standard neutral
choices, not sales data — the same epistemic stance as PROPOSAL 017's IC/IAC,
and exactly why the pre-registered rule demands BOTH modes clear a band and
rules the straddle NULL. The NULL's direction is analytic, not knife-edge: at
s=1 versioning wins by pure arithmetic (K tickets at cost 1+c(K−1) < K·1), and
under pick-best the best-of-K gain E[exp(σ_v·M_K)] flattens as ~√(2·ln K)
while cost grows linearly — no plausible parameter gap makes the two modes
agree inside the swept ranges.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **4,144 self-checks, 0 failed**, exit-coded: fixture pins re-asserted
against grid.json; quadrature identities (I(1,σ) = e^{σ²/2} to 1e−9 for all 12
σ values in play; strict K-monotonicity); per-leg draw-count audits at the RNG
API (810 legs, exact); estimator unbiasedness against the closed-form
diagnostic layer on all 810 means at ≤ max(1%, 6·SE); K=1 zero-variance
identities; Mode P σ_m-inertness; the pre-registered 1.5% Arm A/S gate (135
checks); in-process prefix replay (first 6 cells per mode, fresh streams,
bit-identical); independent recount of the headline shares; K=1 hit-leg
p_single = 0.1000 exact. Seeds: pinned by the proposal (20260716/17/18); the
stability leg is the pre-registered seed-robustness test and reproduces the
ruling. Cherry-picking: the FULL 2 × 81-cell table is committed in
`results.json`; the decision rule was registered in the proposal before any
code existed and is applied mechanically.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is margin-free on both sides: Mode P misses APPROVE's cell-share line
by 65 points (14.81% vs 80%) and its median-ΔR line by the full +0.10; Mode A
misses REJECT's line by 69 points (11.11% vs 80%). The M=2,000 leg (10× fewer
titles, fresh seed) reproduces every headline share exactly. Worst-case MC SE
on any mean is ~0.15%; no cell-share sits anywhere near a decision line that
estimates this tight could bridge.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, no network / git / wall clock /
hash(); fixed seeds from the committed fixture; stdout AND `results.json`
byte-identical across TWO complete process runs by external `diff`; Arm A is
seedless quadrature (platform-independent); Arm S pinned to CPython 3.11
(asserted at startup). Runtime ~2 min.

**5. "LIMITS? what this evidence does NOT show."**
No live sales data anywhere in the loop — model-true, not market-true; s and f
are unmeasured dials; elasticity pinned by the exp link (bracketed, disclosed);
static K only; title-independence assumed; the hit legs use an independence
approximation across titles; conclusions in relative revenue units, never
currency or forecasts.

## EVIDENCE STRENGTH: **moderate** — gate PASS

Strong internally (pre-registered, dual-arm, analytic-anchored, margin-free
NULL); bounded externally by the model-not-market limit both this report and
the proposal state up front.

## VERDICT & recommendation (for the fleet manager to route)

**null** — the pre-registered honest straddle, finalized (not a re-run
request): the two publication modes give opposite defaults, so neither "always
version" nor "always breadth" may be cited as settled for the venture book
pipeline.

The citable CONDITIONAL rule (the pre-registered NULL consequence): **route by
publish mode first** — (i) if the night's plan is publish-all with any real
audience separation (different angles/audiences/lengths listed separately,
s > 0), version-heavy allocation is robustly right (grid-median K\* = 6, the
swept top; ΔR at s=1 is +166.7%/+71.4%/+26.3% by c ∈ {0.25, 0.5, 0.75});
(ii) if the plan is pick-best-then-publish-one, new-titles-first is the
measured default — versioning pays only at the aligned corner (c = 0.25,
σ_v = 1.0, f = 1.0: K\* = 3, ΔR ≈ +0.27) and never at f = 0.2. Named flip
axes (tie-aware): Mode P {c, σ_v, f} at spread 0.3333; Mode A {c, σ_m, s} at
spread 0.2593; version cost c is the only axis on both frontiers, and σ_m is
measured inert in Mode P (E[exp(L)] = 1 by construction). The lane's cheapest
LIVE probe, named per the pre-registered consequence: publish two versions of
ONE existing-research book with disjoint audience keywords and record whether
their draws actually separate — measuring s in the wild for one night-slice's
budget. Caveats restated per the done-when: the exp link pins quality
elasticity at 1 (bracketed by the σ_m sweep); relative units only — this sim
allocates effort, it never forecasts earnings (Q-0259 r.4 untouched); the
hit-probability and B=6 legs are sensitivity reporting and cannot flip the
decision (they did not).
