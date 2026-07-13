# REPORT — Drift-regime observability: is the arm of V024's conditional trust rule readable from the basket stream in time to act? (PROPOSAL 034)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 034** ·
> 2026-07-13T09:12:01Z · status: sim-ready (idea
> `ideas/trading-strategy/xsec-drift-regime-observability-2026-07-13.md`,
> main `eea4e5b`). The standing ORDER 003 VENTURE rotation slot, round 5,
> trading half (rounds 1–4: P018 books → V020 null, P022 trading → V024
> null, P026 trading → V028 approve, P030 books → V032 reject) — round 5
> follows the trading line's own joint open thread: V024's first "What it
> did NOT settle" line ("Which null arm the lane's real data lives in") and
> V028's LIMITS line ("a bar registered for a regime-switching world should
> be recomputed under it"). Fully hermetic: every fixture a pinned constant
> in `fixtures.json`; zero repo/network reads at run time; ZERO real market
> bars; no dev-candidate evaluated on any data; the owner-gated post-2026
> protocol untouched (P022's harvest-hazard clause inherited verbatim).
> Run: `python3 sims/verdict-036-drift-observability/drift_observability_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — a seeded deterministic
operating-characteristic sweep, band-scored against the pre-registration by
twin independently-written decision evaluators, with an exact seedless
analytic arm gating every control leg): 18 threshold detectors × 9
(occupancy, sojourn) cells × M = 1,000 switching paths of T = 2,595 bars,
scored bars t ∈ [252, T). Arm A (exact, platform-independent closed forms:
pure-window Gaussian OCs via math.erf, exact Binomial OCs via math.comb,
exact stationary occupancies/baselines/flip-count expectations and their
closed-form variances) covers every quantity that has a closed form; Arm S
(seeded MC, seeds 20260772–75, pinned loop order, one uniform per normal)
contributes the mixed-window realized error the closed forms cannot price —
the P033 arm-split pattern. This label fills the outbox `evidence:
simulation`. The one judgment question — whether +0.10 of
trust-misallocation removed is the right materiality line — was pinned by
pre-registration in the idea file; the full E/BA/ΔE/lag tables ship in
`results.json`, so a re-drawn line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration, landed BEFORE the runner — git history is the trail) and
touches no repo state, no network, no wall clock. Every constant
(δ = 1.15/√252 = 0.07244319066010188, p_D = Φ(δ) = 0.528875393055249, the
S-grid {126, 252, 1008}², T = 2,595, scoring start 252, the
statistic/window/λ grids with their threshold formulas h = λ·1.15 and
u = 1/2 + λ·(p_D − 1/2), M per leg {1,000 / 250 / 500 / 400}, seeds
20260772–75, band constants (+0.10 / ≥ 3 of 9 / ≥ 7 of 9), the exact π_D
and min(π_D, π_Z) tables, the V024 anchor pair with its results.json pin
`cd47c06`, familywise gate tolerances with their pre-run SE arithmetic, the
occupancy-leg layout rule) was copied verbatim from the idea file into
`fixtures.json`, and the runner cross-checks its literals against that file
at start. Fifteen intake-time decisions are disclosed in `fixtures.json`
(window convention, up-bar rule, integer UP thresholds, E pooling, the
swap-gate scope with its mathematical reason, the ρ-invariance leg's cell
and M, lag conventions, the occupancy-leg block layout, the ceiling-table
E_∞ convention, the realized-sd normalizer, the twin-evaluator split, the
frozen-leg draw structure, the stability-leg scope, output formatting, and
the scratchpad pilot on throwaway seeds 990101–04 — no committed number
read from it). Seed-registry note: seeds 20260772–75 sit strictly above the
P033 high-water 20260771; new high-water 20260775.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Stream (per-bar Sharpe units):** x_t = μ_{s_t} + ε_t, ε_t i.i.d.
  N(0,1); state D mean δ = 1.15/√252 (V024's matched arm — its committed
  basket-Sharpe constant), state Z mean 0. The reduction is exact and
  ρ-invariant BY CONSTRUCTION (V024 pins the matched drift to basket Sharpe
  1.15 at every ρ) — asserted as a code-level identity at ρ ∈ {0, 0.3, 0.6}
  AND as a byte-identity gate. Vol model IID only, by citation: V024
  measured the vol axis inert (spread 0.000, the P026 demotion precedent).
- **Regime chain:** 2-state Markov, geometric sojourns, per-bar stay
  probability 1 − 1/S, stationary start; 9 decision cells (S_D, S_Z) ∈
  {126, 252, 1008}² with exact π_D ∈ {0.500, 0.333, 0.111, 0.667, 0.500,
  0.200, 0.889, 0.800, 0.500}.
- **Detectors (18):** SR_w = trailing w-bar annualized Sharpe with PINNED
  vol normalizer, threshold h = λ·1.15; UP_w = trailing w-bar up-share,
  threshold u = 1/2 + λ·(p_D − 1/2) (integer form: count ≥ ⌈w·u⌉, never a
  tie); w ∈ {63, 126, 252}, λ ∈ {0.3, 0.5, 0.7}; classify drift-on iff
  statistic ≥ threshold at every scored bar. Disclosed discreteness: the
  exact ⌈w·u⌉ collapses UP w=63 across all λ (k = 33) and UP w=126 across
  λ ∈ {0.3, 0.5} (k = 65) — a property of the registered detector, kept as
  distinct rows.
- **Score:** E = misclassified scored bars / scored bars;
  ΔE_oracle = min(π_D, π_Z) − E vs the EXACT best-static-prior oracle (the
  V032 beat-the-best-static discipline); win iff ΔE_oracle ≥ +0.10.
- **Decision rule (registered before any code, evaluated in this order):**
  REJECT iff NO variant wins ≥ 3 of 9 cells (checked FIRST); APPROVE iff
  ONE variant (same statistic, w, λ) wins ≥ 7 of 9, stability-reproduced;
  NULL otherwise.
- **Reporting-only legs (cannot flip):** post-flip lag tables, ΔE_always =
  π_Z − E, the realized-sd SR variant (ΔBA column), and the
  occupancy-graded bar leg (V024's committed G6 panel machinery at its
  IID/ρ = 0.3 cell, J = 9, the lane's R3 rule verbatim, M = 400 per point,
  φ_D ∈ {0, 0.25, 0.5, 0.75, 1} as one leading D-block, chained to V024's
  committed anchors).

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`. Main leg M = 1,000/cell, seed 20260772.

**(1) The frontier table — the decision leg.** ΔE_oracle ≥ +0.10 is reached
ONLY in the (1008, 1008) cell, by 15 of 18 variants; NO variant wins more
than **1 of 9 cells** (REJECT bar: 3). Per-cell best over all 18 variants:

| cell (S_D, S_Z) | π_D | min(π_D,π_Z) | best ΔE_oracle | best variant | win? |
|---|---|---|---|---|---|
| (126, 126) | 0.500 | 0.500 | +0.0721 | SR w=63 λ=0.5 | no |
| (126, 252) | 0.333 | 0.333 | −0.0593 | SR w=252 λ=0.7 | no |
| (126, 1008) | 0.111 | 0.111 | −0.1685 | SR w=252 λ=0.7 | no |
| (252, 126) | 0.667 | 0.333 | −0.0553 | SR w=252 λ=0.3 | no |
| (252, 252) | 0.500 | 0.500 | +0.0959 | SR w=126 λ=0.5 | no (−0.0041 short) |
| (252, 1008) | 0.200 | 0.200 | −0.1020 | SR w=252 λ=0.7 | no |
| (1008, 126) | 0.889 | 0.111 | −0.1671 | SR w=252 λ=0.3 | no |
| (1008, 252) | 0.800 | 0.200 | −0.1022 | SR w=252 λ=0.3 | no |
| (1008, 1008) | 0.500 | 0.500 | **+0.1660** | SR w=252 λ=0.5 | **yes** |

The largest measured win anywhere: SR w=252 λ=0.5 at (1008, 1008) — E =
0.3340, BA = 0.6660, ΔE_oracle = +0.1660. The same variant's E in the
skewed cells runs 0.334–0.345 — the detector's error is roughly constant
while the oracle-static error collapses with skew, so ΔE_oracle inverts.

**(2) Band arithmetic (registered order).** REJECT — checked FIRST — is
MET: max cells won by any variant = 1/9 < 3. It is not knife-edge on the
bar: to miss REJECT a variant needs THREE winning cells, and every
variant's third-best cell sits at ≤ +0.072 — 2.8 pp below the +0.10 line —
while the second-best cell peaks at +0.0959 (SR w=126 λ=0.5 at (252, 252),
0.41 pp short; flipping that single cell would still leave 2/9 < 3).
APPROVE was never near (needs 7/9). **Ruling: REJECT — "cheap drift-gating
never materially pays — build no lane tooling; the round-3 registration
carries the quantified unhedgeable-degradation caveat, with the exact
pure-window ceiling table as the evidence row."** Stability leg (seed
20260773, M = 250): REJECT reproduced — max cells won 2/9 (SR w=126 λ=0.7),
still < 3, twin-evaluator-agreed.

**(3) The ceiling arithmetic — why this REJECT is structural, not sampled.**
Arm A's exact pure-window table caps BA at Φ(0.575·√(w/252)): 0.613 / 0.658
/ 0.717 by window (the proposal's own detection arithmetic, reproduced as a
hand-pin gate). Combining the exact OCs with the exact occupancies: in 6 of
9 cells (every cell with min(π_D, π_Z) ≤ 1/3) NO registered variant clears
the +0.10 band EVEN AT THE PURE-WINDOW CEILING — best ceiling E 0.2276 at
min_π = 0.111 (needs ≤ 0.011), 0.2413 at min_π = 0.200 (needs ≤ 0.100),
0.2620 at min_π = 0.333 (needs ≤ 0.233) — so the skewed two-thirds of the
grid was unwinnable by arithmetic BEFORE mixing, and the measured sweep
shows mixing then eats the balanced cells too: at S = 126–252 the realized
best falls 0.4–2.8 pp short even where π = 0.5. Only sojourns ≥ 4× the
longest window (1008 vs 252) leave enough pure-window bars to pay.

**(4) Flip-axis reading (per-axis pass shares, pooled over variants).**
min-sojourn axis: {126: 0.000, 252: 0.000, 1008: 0.833} — spread 0.833, the
binding axis exactly as the registration's arithmetic predicted
("at S = 126 every swept window straddles flips"); min_π axis: {0.111:
0.000, 0.2: 0.000, 0.333: 0.000, 0.5: 0.278} — occupancy skew kills the
rest. The conditional-rule shape the registration named for a NULL is
visible in the REJECT table (gate only where occupancy is uncertain AND
sojourns clear the window = the (1008, 1008) corner), but it clears the
materiality band in that ONE corner only — below the 3-cell floor the
registration set for building anything.

**(5) Reporting-only legs (could not flip; did not).**
- **ΔE_always (vs the lane's de-facto always-trust rule):** the detector
  crushes always-trust where Z dominates (up to +0.6093 at (126, 1008)) and
  LOSES to it in every drift-heavy cell (down to −0.3233; 54 of 162 rows
  negative) — trust gating pays against the naive rule only where the world
  is mostly untrustworthy, which is exactly where V024's own zero-drift
  null already withholds trust.
- **Lag tables:** in flip-heavy cells the median post-flip lag is 0–7 bars
  but only because a BA ≈ 0.58 classifier chatters (p90 lags 78–187 bars,
  censor fractions 7–36%); in the one winning cell the median lag is 24
  bars each direction (p90 211) — a quarter-year to read a flip with the
  best variant. Full per-(cell, variant, direction) tables committed.
- **Realized-sd SR variant:** |ΔBA| ≤ 0.0004 across all 27 (cell, w, λ)
  rows — estimating the vol normalizer from the window is FREE in this
  frame (unit true vol); the pinned-normalizer simplification carries no
  load.
- **Occupancy-graded bar leg (V024's G6 machinery, M = 400/point):**
  q99(Δ_max(G6)) = 0.5553 / 0.4992 / 0.5603 / 0.5065 / 0.3473 at φ = 0 /
  0.25 / 0.5 / 0.75 / 1. CHAINED ANCHORS PASS: N_exc(φ=1 vs committed
  0.366902) = 3 ≤ 12; N_exc(φ=0 vs committed 0.604101) = 3 ≤ 12 (expected
  ≈ 4.4 under the parent tail) — both committed arms reproduce. The q50/q90
  columns fall monotonically with φ (q50 +0.1207 → −0.0687; q90 +0.3598 →
  +0.1642), but the q99 point estimates are NOT pointwise monotone at
  M = 400 (the 0.25/0.50 inversion is inside tail noise) — so the honest
  reading is: the bar moves DOWN with occupancy and the endpoints anchor
  exactly, but a q99-level interpolation rule would need a bigger M; a
  partial-occupancy reading calibrates the bar's BODY (q50/q90) by
  interpolation, not yet its q99 tail.

**(6) Validity.** All gates PASS, **489 self-checks, 0 failed**, exit 0:
fixture crosscheck (every constant, both V024 anchors, all 36 pre-pinned
frozen tolerances recomputed and matched); Arm A identities (SR swap
TPR(λ) = TNR(1−λ) exact; UP mirror identity via two independently written
binomial routines; the ceiling hand-pins); frozen-state control legs
(M = 500 each, seed 20260774) reproduce Arm A's exact TPR/FPR on all 36
gate points — max |deviation|/tolerance 0.287, max absolute deviation
0.0113; occupancy and flip-count gates on all 27 points (exact closed-form
variances); the Arm S swap gate (SR family, 90 unique transpose
comparisons, cluster-robust SE — the 162 registered ordered identity
readings dedupe to 90 unique comparisons, each distinct pair implying its
mirror algebraically) max |z| = 2.04 vs tolerance 4.5; the ρ-invariance
gate (50 paths × 2 basket-vol scales, all 18 variants, classifications
byte-identical); per-leg draw-count sentinels exact over 113,142,000
uniforms (main 46,710,000 / stability 11,677,500 / frozen 2,595,000 /
occupancy 51,900,000 / ρ 259,500); determinism replay on the first path of
every leg; twin G6 evaluator per φ point (≤ 1e-9); twin decision
evaluators (integer arithmetic vs fractions.Fraction) agree on every win
flag, count, and ruling, main and stability. stdout AND `results.json`
byte-identical across two complete process runs by external diff (sha256
stdout `026353f0…`, results `ab8bf6b8…`); cpython-3.11 pinned and
asserted; stdlib-only, hermetic, ~92 s per run.

## What it did NOT settle

- **The lane's real cell.** The world here is the two-arm inheritance —
  real drift is a continuum with unknown sojourns; the two-point gap is the
  HARDEST fixed-gap version of the question (smooth decay between arms
  would flatter every detector near the boundary, stated in the model
  basis). The measurement that locates the lane's real (π_D, S) cell is the
  live probe the NULL branch would have named; under REJECT it is NOT
  ordered — but the frontier table makes any future reading decision-ready.
- **Richer detector families.** This REJECT rules on the registered
  threshold family (two cheap statistics × three windows × three
  thresholds) ONLY. CUSUM / likelihood-ratio composite filters are the
  named rescue family and carry their own sim if ever routed.
- **The q99-level occupancy interpolation.** Endpoints anchor and the bar
  body interpolates; the q99 tail at M = 400 is too noisy for a pointwise
  monotone claim (reported, not smoothed).
- **The materiality line itself.** +0.10 is a pre-registered judgment; the
  full ΔE tables ship, so a re-drawn line re-reads, never re-runs. (Not
  knife-edge here: only one cell clears +0.10 at all, and the REJECT bar
  needs three.)

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The world is model-true by design and inheritance: both drift states are
V024's own committed arms (the state-D constant is V024's basket-Sharpe
1.15, ρ-invariance asserted as a code identity and a byte-identity gate),
and the one new axis — the regime chain — is swept over 9 (occupancy,
sojourn) cells spanning "flips inside a dev window" to "one regime is most
of the history". The abstractions that could flip the reading are declared:
a drift CONTINUUM between the arms (the two-point gap is the hardest
fixed-gap version — a continuum flatters detectors near the boundary, but
near the boundary the arms' nulls also converge, so the trust stakes
shrink with the gap); the real sojourn structure (the declared flip axis;
the un-ordered live probe is the instrument); fat tails / vol regimes
(excluded by V024's measured vol-axis inertness, the P026 demotion
precedent). Within the registered family the REJECT is arithmetic-backed:
6 of 9 cells are unwinnable at the exact pure-window ceiling before any
mixing.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. 489 self-checks, 0 failed, exit-coded: an exact seedless arm gates
the MC arm at 36 frozen-state points (tolerances pre-pinned in the fixture
with their SE arithmetic, familywise-calibrated BEFORE any run — the
V027/V031 lesson with V028's calibration lesson applied at design time; max
deviation 0.29 of tolerance), 27 occupancy/flip points against exact
closed-form variances, 90 swap-transpose comparisons, a byte-identity
ρ-invariance gate, exact draw-count sentinels over 113.1M uniforms, twin G6
and twin decision evaluators, and two chained V024 anchors reproduced at
fresh seed inside pre-pinned tail-count bands. No seeded luck: the ruling
reproduces on the fresh-seed stability leg; the deciding margins are
multiples of the MC noise (the third-best cell misses by 2.8 pp). No
cherry-picking: all 162 (cell, variant) rows ship, including the one
winning corner and the 54 rows where the detector loses even to
always-trust; the "best variant" line is reported WITH the tie (15 variants
share the 1/9 score).

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes. The REJECT bar needs 3 winning cells; the measured max is 1, the
second-best cell misses its win by 0.41 pp (flipping it changes nothing),
and the third-best by 2.8 pp — while 6 of 9 cells are closed by EXACT
ceiling arithmetic that no MC variation can reopen. The stability leg
(fresh seed, M = 250) reproduces REJECT with the same structure (max 2/9).
The one edge case is disclosed rather than smoothed: (252, 252)'s best
variant sits 0.41 pp under the win line — within MC noise of winning — but
a 2-win world is still REJECT, and the pre-registered bar was set at 3
precisely so a single noisy corner could not buy lane tooling. The
reporting legs could not flip the decision and did not.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own `fixtures.json`). Byte-identical stdout AND `results.json` across
TWO complete process runs by external `diff` (sha256 stdout `026353f0…`,
results `ab8bf6b8…`). Pinned seeds 20260772–75, pinned loop order, one
uniform per normal, per-leg sentinels, determinism replays, cpython-3.11
pinned and asserted. ~92 s per run.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure the lane's real bars — no live data anywhere in the
loop; real-world quantities (real sojourns, real drift levels, fat tails)
are dials or exclusions, stated. The REJECT is family-scoped: it prices
cheap threshold detectors on two statistics, not detection in general
(composite filters are the named rescue family). ΔE_oracle is conservative
TOWARD tooling (the oracle prior is unknowable in practice, so a detector
that cannot beat it is truly dead — but ΔE_always ships for re-weighing
against the lane's de-facto rule, where the detector DOES pay in Z-heavy
worlds). Nothing here trades: trust gating only, and the weakest KEEP
margin +0.130 stays promotion-weightless per V024 under EVERY regime
reading (restated, not re-run).

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying comparison couples an exact analytic arm (which
already closes 6 of 9 cells by ceiling arithmetic) with a gated MC arm
whose deciding margins are several times its noise; every constant, band,
seed, tolerance and the evaluation order were registered before any code;
the ruling reproduces on a fresh seed; and both chained parent anchors
reproduce. The honest boundary: this strength attaches to the two-arm
threshold-detector frame — the REJECT kills THIS family's lane tooling, not
the question of drift observability under richer filters or gentler drift
structure.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — "cheap drift-gating never materially pays — build
  no lane tooling; the round-3 registration carries the quantified
  unhedgeable-degradation caveat."** By the rule committed before any code
  (REJECT checked FIRST): no variant clears ΔE_oracle ≥ +0.10 in ≥ 3 of 9
  cells — measured max 1 of 9 (the (1008, 1008) corner), stability-
  reproduced, twin-evaluator-agreed.
- **The pre-registered REJECT consequence, verbatim:** NO regime-gating
  tooling is built; V024's static matched-arm reading stays the operative
  conditional; and the round-3 registration carries the measured caveat
  that its trust degrades UNDETECTABLY at the swept windows — the exact
  pure-window ceiling table is the evidence row (BA ceilings 0.613 / 0.658
  / 0.717 at w = 63 / 126 / 252; 6 of 9 cells unwinnable at the ceiling;
  the detector's realized E ≈ 0.33–0.44 everywhere). A REJECT here rules on
  this threshold-detector family only, stated — composite filters (CUSUM,
  likelihood-ratio) are the named rescue family carrying their own sim.
- **The citable numbers:** the full 162-row frontier table (committed);
  the one paying corner — SR w=252 λ=0.5 at (S_D, S_Z) = (1008, 1008):
  E 0.334, BA 0.666, ΔE_oracle +0.166, median post-flip lag 24 bars — and
  the flip axes: min-sojourn pass shares {126: 0, 252: 0, 1008: 0.833},
  occupancy-skew pass shares {skewed cells: 0 everywhere}; ΔE_always spans
  +0.609 (Z-heavy) to −0.323 (D-heavy) — the detector only beats
  always-trust where V024's zero-drift null already withholds trust; the
  vol-estimation price is nil (|ΔBA| ≤ 0.0004).
- **The occupancy-graded bar (reporting):** both committed arms reproduce
  under the chained tail-count anchors (N_exc 3 and 3 vs bands ≤ 12); the
  bar's body (q50/q90) interpolates monotonically with drift occupancy —
  q99 itself needs a bigger M for a pointwise rule. A partial-occupancy
  reading can calibrate the bar's body by interpolation; the q99 tail
  stays per-arm.
- **Named follow-ups (not ordered):** the composite-filter rescue head (the
  only registered path back to lane gating); the lane-side live probe
  (running any pinned variant on the lane's committed dev bars to locate
  its real (π_D, S) cell — decision-ready against the committed frontier
  table even under REJECT); a bigger-M occupancy leg if any future head
  needs the q99-level interpolation.
- **Rotation proof for ORDER 003, stated:** VENTURE round 5 SERVED from the
  trading half at its parents' own named open thread — the same
  pre-registered fixtures-first discipline, byte-reproducible, honest
  reject.
