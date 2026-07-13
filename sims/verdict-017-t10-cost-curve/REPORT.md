# REPORT — generator purchase path: T10 cost-curve sweep (PROPOSAL 015)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 015** @
> 2026-07-12T23:08:19Z (idea `ideas/superbot-idle/generator-purchase-path-t10-2026-07-12.md`
> @ `18778ff`, landed via idea-engine PR #277).
> Engine driven: `idle_engine/` @ `c753bc8f5ace96e4632510f43b53f0ee45e2def5`
> (`menno420/superbot-idle`), **vendored byte-for-byte, all 11 modules, sha256-manifest-pinned**.
> Run: `python3 sims/verdict-017-t10-cost-curve/t10_cost_curve_sim.py`

## METHOD LABEL: NUMERIC SIMULATION

Rung 1 of the method ladder is the cheapest ADEQUATE evidence: the economy is a
fully-specified, pure, integer-exact deterministic system (no wall clock, no
randomness, no I/O), so its pacing under any committed cost curve is *computed*,
not sampled. The sim does not model the economy — it **drives the real economy
engine** at the fresh pin and reads the answer; the ONLY driver-level addition
is the candidate mechanic itself (a generator cost curve + purchase function),
which cannot be driven from the engine because **the engine has no generator
purchase path at `c753bc8` — the sim's verified premise** (tree-grep at the pin:
`purchase_upgrade`/`purchase_upgrades` only). No RNG anywhere, so a single run
per (cell, policy) *is* the distribution; determinism is proven by
byte-identical re-run (gate 4). This label fills the outbox `evidence: simulation`.

## What it MODELS / MEASURES

The economy-v1 **reference world extended to two generator specs** (the
proposal's world), every held parameter read live from the vendored
`idle_engine.economy` and self-checked equal to the graduated table:

- `GeneratorSpec("tier1","primary",base_rate=1)` as shipped, owned `{"tier1":1}`
  fresh; `GeneratorSpec("tier2","primary",base_rate=R2)` (swept), owned 0;
  neutral theme pct (100, the spec default) — theme-independent by construction.
- ONE upgrade ladder `build_upgrade_spec("boost1", tier1)`; ONE prestige track
  `build_prestige_spec("prestige","primary")`; the NINE registered milestone
  slots `build_milestone_specs("primary","prestige")` — the engine surface that
  LANDED after the `f11c71a` verdicted pin (the drift the baseline leg isolates).
  Production fold at the pin: `base_rate·count·upgrade_pct·prestige_pct·
  milestone_pct·theme_pct // 100_000_000` (self-checked against hand values).
- **The candidate mechanic (driver-level, disclosed):** generator cost curve
  `cost(next copy | n owned) = BASE · g_num^n // g_den^n` — the upgrade-curve
  family, exact big-int, one floor — with `BASE = base_rate·COST_SECONDS`
  (the `UPGRADE_BASE_COST_SECONDS` unit convention). Tier-2 `COST_SECONDS = C2`
  (swept; unlock at 0 owned costs exactly C2). Tier-1 copies at
  `COST_SECONDS = 60` — NOT swept, held at the engine's only registered cost
  anchor (a modelling choice, committed in `grid.json`, consequences measured
  and headlined below). Purchase semantics mirror `purchase_upgrade` exactly:
  exact spend or nothing, balance-only, lifetime untouched, `owned += 1`
  (self-checked, incl. rejection). `apply_prestige` wipes `owned` (engine
  semantics, untouched): every purchased copy is LOST at reset and re-bought —
  the run-scoped-counts semantics the proposal names as the design fork.
- **The committed greedy buy rule** (`grid.json § buy_rule`): at each action
  boundary, repeat-buy the highest marginal-production-per-unit-cost option
  among the AFFORDABLE {next upgrade level, next tier-1 copy, next tier-2
  copy}, deltas measured by calling the REAL `production_per_second` on the
  hypothetical post-purchase state, ratios compared as exact integer
  cross-products, committed tie-breaks — SIM-001's "repeat-buy while
  affordable" extended to the three-option set. Additive **S3g** saving
  variant (argmax over ALL options, save for a positive-delta winner) reported
  never-instead-of S3, the SIM-001 S3b precedent. Milestones bank via the REAL
  `award_milestones` at every boundary; S3's 1-second player banks a milestone
  the second it crosses (event-jump boundary, proven byte-identical to a
  literal per-second loop); S2 banks at visits only (the reference world's
  "the player can only act when present" rule).
- **Scenarios** per world: S1 idle-only; S2 check-in N ∈ {0.25, 2, 8, 24} h;
  S3 optimal-active at 1-s granularity by exact event-jump; S3g. Horizon 14
  days, S3 capped at 25 resets (the SIM-001 cap; every criterion + T10 + O6
  resolve well inside it).
- **Legs:** baseline **B0** (no purchase path, milestones OFF — must equal
  VERDICT 006, the drift-isolation anchor), baseline **B1** (no purchase path,
  the real HEAD fold — the honest drift leg), the **36-cell committed grid**,
  and two disclosed additive DIAGNOSTIC shapes per cell: **D1** (no tier-1
  copies — tier-2 unlock/copies only) and **D2** (unlock-only: tier-2 capped
  at one copy, T10's registered wording read literally; the g axis is inert in
  D2 by construction).
- **Scored per cell:** T10 (first tier-2 purchase; band PASS = S3's T10 in
  [900, 2700] s, reported under S3/S3g/every S2(N)); A1–A10 re-scored
  **dual-read** — LITERAL counts boost1 upgrade purchases only where the
  registered wording names upgrades (T1/T2/T7/T8), INTENT counts all
  purchases; both committed, headline PASS = INTENT, every divergence listed;
  early-inert fraction (share of first-15-min S3 purchases with zero marginal
  rate delta, vs VERDICT 006's 3-in-4); owned-rung arrival times per profile.

## What it SETTLED (the load-bearing claims)

Every number is a committed output of the one run command
(`results.json` + stdout).

**1. The engine drift since the verdicted pin is benign — B1 scores 10/10.**
B0 (milestones off) reproduces VERDICT 006's published numbers EXACTLY,
self-check-pinned: A1 60 s, A2 12, A3 12573 s, A4 100000 s, A5 21600 s,
resets 12573/11536/10475, A7 (6,16), A8 gap 1215 s, awards all 1, early-inert
9/12. B1 (the real HEAD fold: milestones + schema-bounded theme pct at
neutral) shifts A3 to 12134 s (−3.5%), A9 r2 to 0.8205, and confirms the
achievements doc's designed double-hit (lifetime-2 + prestige-1 both bank at
the first reset, t=12134) — **all ten criteria stay PASS; no first-class
drift finding.**

**2. The committed count-stacking shape is rejected at EVERY cell — 0/36.**
Binding criteria A3 AND A6 in 36/36 (intent reading; literal identical):
S3 first-prestige collapses from the verdicted 3.49 h to **501–971 s
(8.4–16.2 minutes)** and A6 balloons to **103–200×** against its 4–12× band.
Every cell's S3 T10 (350–655 s = 5.8–10.9 min) also undershoots the 15-min
band floor — even C2=1800 (30 min of tier-1 output) is affordable-in-passing
by ~10 min. Mechanism, measured: a tier-1 copy costs `60·g^n` but adds a full
count's worth of pct-multiplied output, so income compounds faster than the
g ≤ 1.2 curve grows — a runaway the swept tier-2 knobs never touch. **The
tier-1 copy anchor is the binding surface, not (C2, R2, g).**

**3. Any count-stacking loop at these growth rates runs away — D1 is 0/36
too.** With tier-1 copies removed, tier-2 copy-stacking alone still breaks
A3 (1145–5683 s) and A6 (17.6–87.3×) in every cell. The failure is the
mechanic SHAPE (count-purchases whose cost grows at g ≤ 1.2 against
count-linear income), not the tier-1 anchor value.

**4. The unlock-only shape passes, at exactly one (C2, R2) — the verdict's
row.** D2 (buying the second generator TIER is a one-off unlock; no
count-stacking on either tier): 27/36 in the T10 band, and the
**(C2=900, R2=5)** column (its three g-cells — g is inert in D2) is the ONLY
(C2, R2) with all ten criteria PASS on BOTH scorecard readings:
**T10 = 1948 s ≈ 32.5 min** (registered target 30), policy-robust
(S3g 900 s and S2(0.25 h) 900 s — the band floor exactly; S2(2 h) first
visit 7200 s), A3 8518 s (2.37 h), A5 21600 s, A6 **11.74** (near the 12×
edge — disclosed), A7 (6,19), A8 8.9%, A9 (0.824, 0.932), A10 PASS.
Band-edge cells marked per the done-when: C2=300 (T10 940 s, 40 s above the
floor), C2=600|R2=5 (A6 12.04 — misses by 0.04×), C2=1800|R2=5 (10/10 but
T10 3081 s, 381 s past the ceiling); R2 ∈ {10, 25} breaks A6 (and mostly A3)
at every C2 — the tier-2 rate, folded through prestige+milestone pcts,
drags first-prestige under 2 h.

**5. The registered `owned` milestone ladder and pacing-compatible generator
purchases are mutually exclusive as registered.** In the passing shape total
owned maxes at 2 — owned-10/100/1,000 are UNREACHABLE, permanently. In the
rejected stacking shapes rung 1 arrives in 295–431 s (S3), rung 2 only for
the S2(24 h) profile (30/36 cells, at ~2 days), rung 3 never (14-day
horizon) — but those shapes kill T3/T6. The achievements doc's deferred
question 3 is answered: not under any swept curve without re-registration.

**6. Early-inert relief and pacing preservation are in tension.** The
stacking shapes crush VERDICT 006's 3-in-4 floor (2–5 inert of 61–185 early
purchases ≈ 2–7% — generator deltas are never floored away) but break
pacing; the passing unlock-only shape keeps the baseline 9/12 floor
untouched (its first 15 minutes are upgrades-only). VERDICT 006's named
base_rate follow-up stays open.

## What it did NOT settle

- **Whether a steeper generator curve rescues count-stacking.** g > 1.2,
  count-scaled bases, or per-copy rate decay are OUTSIDE the committed grid;
  this sweep proves the registered grid dies, not that no stacking curve
  exists. That is the named follow-up sweep axis.
- **The tier-1 copy price as a free knob.** 60 s is the only registered cost
  anchor and was held, not swept; the committed-shape rejection is the
  anchor's consequence at every swept g. A dearer tier-1 anchor changes the
  committed shape's numbers — but D1 shows removing tier-1 copies entirely
  still fails, so no tier-1 price rescues the stacking shape at g ≤ 1.2.
- **Live players.** Greedy-myopic and greedy-saving bound the active player;
  real players do neither perfectly. T10's policy spread is reported
  (winner: 900–1948 s across S3g/S3/S2(0.25)) — all in band, but that is a
  property of the winning cell, not of players.
- **A2's "purchases are noise" ceiling.** economy-v1's prose calls T2 above
  ~12 "noise, not decisions"; the registered PASS is only ≥5, and stacking
  cells hit 61–185 purchases by 15 min. Scored as registered (PASS); flagged
  here because any future stacking curve should carry a ceiling criterion.
- **The A6 edge margin.** The winner's 11.74× is 2.2% under the 12× cap; a
  future retune of anything feeding A3/A4 re-opens it (guardrail below).

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

The engine-side mechanics ARE the shipped code at the fresh pin — zero
model-vs-engine gap on costs, folds, floors, prestige, milestones (B0's exact
equality to VERDICT 006 is the proof the harness reproduces verdicted
reality). The abstractions: (a) the CANDIDATE mechanic is driver-level by
necessity (no purchase path exists — the premise); its cost family and
semantics are the engine's own conventions, committed in `grid.json`; a
future engine implementation that deviates from `cost = BASE·g^n//den^n` or
run-scoped counts invalidates the numbers (stated in the recommendation).
(b) The tier-1 copy anchor (60 s, held): could a different anchor flip the
committed-shape rejection? No — D1 removes tier-1 copies entirely and still
fails 36/36 on the same criteria; the rejection is shape-driven, not
anchor-driven. (c) Players are greedy/grid abstractions (SIM-001's own);
the winner's T10 holds across both S3 policies and the densest check-in grid.
(d) S2 times are visit-grid-quantised (disclosed; per the design's own
time-to-actionable rule).

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

- *Bugs:* **201 self-checks, 0 failed**, exit 0 iff clean: sha256 manifest of
  all 11 vendored files verified before import; the seven graduated
  parameters + milestone table asserted equal to `grid.json`'s pins; the
  five-factor rate identity hand-verified at 96 sampled states (two
  generators, milestone marks); tick == offline closed form on the 2-gen
  world; the candidate mechanic's cost curve, exact-spend, lifetime-
  untouched and rejection semantics; comparator ratio/tie-break cases; the
  B0 == VERDICT 006 cross-pins (nine exact values incl. the 9/12 inert
  floor); **event-jump == literal per-second loop byte-identity over the
  first two resets on THREE worlds** (B1, a grid cell, a D2 cell) covering
  purchases, prestiges AND milestone-banking seconds.
- *Seeded luck:* no RNG exists; n/a and disclosed — reproducibility is
  bit-identity (gate 4), the strongest form.
- *Cherry-picking:* the FULL 36-cell table for all three shapes is printed
  and committed, failures first (the committed shape's 0/36 is the
  headline); the diagnostic legs are additive and labeled, never replacing
  the committed grid's scoring; the winner comes from a winner rule
  committed in `grid.json` BEFORE results existed; literal-vs-intent
  scorecard divergences (A7 in 2 rejected cells) are listed, and the
  recommended row diverges on nothing.

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

The REJECTION is grid-wide and monotone: A3/A6 fail in all 36 committed
cells INCLUDING the dearest corner (C2=1800, R2=5, g=1.2), in all 36 D1
cells, and the T10 undershoot spans the whole committed grid — no edge cell
is close (nearest A6: 103× vs a 12 cap). The APPROVAL's robustness is
narrower and stated: the winning column is stable across the inert g axis
and across policies (S3 1948 s / S3g 900 s / S2(0.25) 900 s all in band),
but A6 = 11.74 sits 2.2% under its cap and the neighbouring C2=600 column
misses A6 by 0.04× — the (C2=900, R2=5) row is a REAL frontier point, not
the middle of a plateau, which is why the verdict is conditional rather than
a clean approve. R2 is the sharp axis: 10 and 25 fail A6 at every C2.

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Committed code (manifest-pinned engine byte-copy + driver + `grid.json`),
ONE documented command, no flags, no network, stdlib-only, no wall clock.
Two complete process runs diffed **byte-identical** on stdout and
`results.json` (external `diff`), plus an in-process re-evaluation of a
committed 6-cell subset and both baselines asserted canonical-JSON-identical.
Runtime ~4 minutes.

**5. LIMITS?** *"what this evidence does NOT show"*

It prices the registered grid on the reference world; it does not show any
shape FEELS good live (no churn, no fatigue, no telemetry). The passing
shape leaves the early-inert floor and the owned-milestone ladder exactly
where the baseline put them — two registered surfaces that now need lane
decisions, not sim decisions. The stacking rejection is bounded by the grid:
g ≤ 1.2 with count-independent bases; a redesigned curve family is unswept.
The A2 noise ceiling is un-criterioned. S3's 25-reset cap bounds owned-rung
observation for the optimal profile (S2 runs cover the full 14 days).
Launch telemetry (real T10, session lengths, day-2 retention) remains the
only test of the "feel" targets.

## EVIDENCE STRENGTH: moderate-strong — gate PASS

Gates 2 and 4 are the strongest available for the class (real engine, exact
cross-pins to the prior verdict, bit-reproducibility, three-world event-jump
faithfulness proofs). Gate 1 carries the necessary driver-mechanic
abstraction — priced, disclosed, and hedged by D1's anchor-independence
result. Gate 3 is decisive for the rejection (uniform, margin-free failure
across the whole grid) and honest about the approval's frontier position.
The grade stays `moderate-strong` because the recommended row is a frontier
point with a 2.2% A6 margin and the candidate mechanic is driver-modelled
ahead of its engine implementation by design.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: conditional.** The proposal's committed question has a
  two-part answer: (1) **NO (C2, R2, g) cell rescues the committed
  count-stacking purchase path** — A3/A6 break in 36/36 (and in 36/36 of
  the no-tier-1 variant); T10 undershoots everywhere; the finding the
  done-when names ("no cell hits T10's band without breaking a named
  A-criterion") holds with the binding criteria stated (A3, A6) and
  band-edge cells marked. (2) **The unlock-only reshape passes at exactly
  one (C2, R2)** — the mechanic-shape fork the proposal itself carved out
  (Q4(c)) — so the lane gets its registration row conditional on the shape.
- **Target:** `menno420/superbot-idle` (economy-v1.md new doc version +
  achievements-v0.md owned-track note; the mechanic build slice follows the
  re-registration, per the lane's integrity floor).
- **Recommended registration row (conditional on the unlock-only shape —
  v1 generator purchase = the tier-2 unlock, one copy, run-scoped,
  re-bought after prestige; no count-stacking on either tier):**
  `GENERATOR_T2_COST_SECONDS = 900` · `GENERATOR_T2_BASE_RATE = 5` ·
  measured T10 = 1948 s ≈ 32.5 min active (band 15–45, target 30);
  proposed criterion text **A11: "S3's first tier-2 generator purchase
  within T10's band (15–45 min); re-run this sim on any retune."**
  **Do NOT register a generator cost-growth g from this sweep** — g is
  inert in the passing shape, and every swept value (1.10/1.15/1.20) fails
  under stacking; g gets registered if-and-when a stacking slice passes a
  future sweep (steeper growth / count-scaled bases are the named axis).
  Runners-up, honestly characterized: the two g-siblings of the winner
  (identical numbers), then C2=1800|R2=5 (10/10 but T10 51.4 min, out of
  band) and C2=600|R2=5 (T10 25 min in-band, A6 12.04 near-miss).
- **Guardrails:** the seven VERDICT 006-graduated parameters and the 1.15
  upgrade growth-ratio near-floor were held fixed and are NOT re-opened by
  this sweep (restated per the proposal's done-when). A6 = 11.74 is 2.2%
  under its cap: any retune touching A3/A4 re-opens T10's row. The engine
  implementation must match the committed driver semantics (cost family,
  exact-spend, lifetime-untouched, run-scoped counts) or this verdict does
  not transfer — re-run the sim against the real implementation before
  graduating the row (the parity-test pattern the lane already uses).
- **Routed findings (lane decisions, not sim decisions):** (a) the
  registered owned-milestone ladder (10/100/1,000) is unreachable under the
  passing shape and lethal-to-pacing under the shapes that reach it —
  re-register the owned track (e.g. lower rungs, or defer to a future
  stacking slice) in the same doc version; (b) the base_rate=1 early-inert
  floor (9/12) survives the passing shape — VERDICT 006's follow-up (raise
  tier1 base_rate or pre-floor scaling) remains open and is now the only
  early-game relief lever; (c) T10's S2 quantisation means a 15-min
  check-in player meets T10 at the band floor exactly — fine as registered,
  worth a telemetry check at launch.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015/V016 slice boundary, with header timestamps from live
`date -u` at append time. -->
