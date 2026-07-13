# REPORT — entry-fee ticket envelope (PROPOSAL 023)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 023** ·
> 2026-07-13T03:53:03Z · status: sim-ready (idea
> `ideas/superbot/casino-entry-fee-ticket-envelope-2026-07-13.md`, landed via
> idea-engine PR #289, main `15d1802`). The ORDER 004 rule-3 GAME-MECHANICS
> rotation slot, round 2 — the direct successor to VERDICT 022, whose "Named
> follow-ups" list requested this head verbatim. Fully hermetic (the PROPOSAL
> 017–022 precedent): every fixture is a pinned constant committed with the
> sim; zero repo/network reads in the verdict session; the parent's anchor
> constants quoted verbatim in `fixtures.json` from its committed files @
> `fda94d0`.
> Run: `python3 sims/verdict-025-ticket-envelope/ticket_envelope_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic,
band-scored against the pre-registration, with a dual ANALYTIC arm gating
the Monte Carlo): integer-F-unit bankroll walks driven through the full
36-cell × 4-policy grid at M = 5,000 casual / 2,000 grinder / 500
compulsive per cell-policy, `random.Random(20260730)` in the pinned loop
order, exactly one draw per ticket; Arm A computes every FUN and R1-wipe
tail EXACTLY (math.comb binomial + bigint DP convolution, seedless
Fractions) plus the T1×R1 grinder chain three independent ways (closed
form, tridiagonal elimination, finite-horizon capped DP), and Arm S must
agree within the pre-registered 1.0 pp before any MC number is believed;
every band decision is an exact integer cross-multiplication, confirmed by
a second independently coded Fraction evaluator. This label fills the
outbox `evidence: simulation`. The one judgment question — whether
0.25 / 0.05 / 0.10 are the RIGHT lines — was settled by the PARENT's
pre-registration and inherited unchanged BY DESIGN (the comparability
contract); the full curves ship in `results.json` so a re-drawn line
re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock;
every constant ({B₀, F, prize schedules, t-grid, c-grid, policy constants,
profile stop rules, M per profile, seeds 20260730–33, band constants}) was
copied verbatim from the idea file into `fixtures.json` BEFORE the runner
was written, and the runner cross-checks its literals against that file at
start (including asserting E[prize] = (1−t)·F exactly, per (shape, t), in
Fractions, and the t=0 per-ticket variances {1, 3.4, 16}·F² exactly).
Twelve intake-time decisions, ALL disclosed in `fixtures.json` before any
runner code: the agreement-gate pooling granularity (per Arm-A-covered
cap-independent quantity, across cap-legs and primary+stability legs — at
per-cap granularity the 1.0 pp gate sits at ~1 MC SE, the parent's
disclosure-1 logic; all 210 per-leg deviations additionally reported), the
capped-quantity gate reading for the grinder leg (the pre-registered
closed form is uncapped; where the 4,000-round cap bites — the proposal's
own expectation on T1×R1 low-take cells — the gate reads against the exact
finite-horizon DP of the same capped chain, with the capped-vs-uncapped
gap reported), MC-chase net-zero and exponent-clip identities, the
compulsive median convention, the Wald form of the t=0 fairness control,
the aux stream scope, the draw-count sentinel form, and the
aggregation-clause disposition (NOT exercised for decisions — every
decision number comes from per-ticket draws; the permitted aggregated draw
was implemented only for the pre-registered seed-20260732 spot check,
which agrees within 4 MC SE and feeds nothing). Two hand-derived pin
scenarios (the MC-chase seven-round loss-streak wipe consuming exactly 100
draws; the jackpot three-round double under the tight cap) were committed
with full derivations in the fixtures BEFORE the runner and replay exactly
through BOTH kernels. The pinned decision machinery (grids, seeds, bands,
rule, evaluation order) is untouched by any disclosure.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Ticket frame:** B₀ = 1,000 integer chips; ticket price F = 0.01·B₀ =
  10, a table constant no policy can escalate; all walks in exact integer
  F-units. Prize schedules (probabilities scaled by (1−t), E[prize] =
  (1−t)·F exactly): **T1** double-up {2F w.p. (1−t)/2}, **T2** tiered
  {8F, 3F, 1F w.p. (1−t)·{0.05, 0.10, 0.30}, variance 3.4·F² at t=0},
  **T3** jackpot {25F, 5F w.p. (1−t)·{0.024, 0.08}, variance 16·F²}.
  Takes t ∈ {0.01, 0.02, 0.05, 0.10} + t=0 control (reporting-only). Caps
  c ∈ {5, 25, 100} tickets/round (5%, 25%, 100% of B₀ — the parent's
  m-grid mirrored, every cell naming its parent cell).
- **Re-buy policies (4 swept; b ≤ c and b ≤ ⌊bankroll/F⌋; b tickets = b
  INDEPENDENT draws, per-round volatility √b not b):** R1 b=1; R5
  b=min(5,·); RG greedy b=max affordable; MC chase b=min(2^L,·), L =
  consecutive net-losing rounds, reset on a net win.
- **Profiles:** CASUAL (100 rounds or bankroll < F; P_ahead = P(final >
  B₀), P_wipe = P(final ≤ 0.1·B₀)); GRINDER (to ≥ 2·B₀ or ≤ 0.5·B₀, cap
  4,000 rounds; P_double, cap-hits > 1% marking the cell indeterminate — a
  NULL path, never silently absorbed; measured P_double a LOWER bound so
  SINK failures stand); COMPULSIVE (reporting-only, R1, to ruin or 20,000
  rounds).
- **Bands (held from VERDICT 022 BY DESIGN):** FUN = R1 reference P_ahead
  ≥ 0.25 (Arm A exact) · SAFE = max-policy P_wipe ≤ 0.05 · SINK =
  max-policy P_double ≤ 0.10. **E\*(g, c)** = takes where all three hold,
  determinate cells only. **Decision rule (registered before any code;
  evaluated in this order):** REJECT iff E\* = ∅ at every cap in ≥ 2/3
  shapes (both arms where covered); APPROVE iff some cap c\* gives ≥ 2
  consecutive shared takes across all shapes (stability-reproduced,
  determinate only); NULL otherwise, flip axis named via per-axis shares.
- **Legs:** primary (decision, seed 20260730); half-M stability (seed
  20260731, must reproduce the ruling); aggregation spot check (20260732,
  reporting-only); aux self-check stream (20260733, never read by any
  decision number).

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json` (Arm A values kept as exact fractions).

**(1) The cross-verdict identity gate PASSES EXACTLY — the chained
comparison is licensed.** The five T1 FUN Fractions (t ∈ {0, 0.01, 0.02,
0.05, 0.10}) equal VERDICT 022's committed G1 reference Fractions
(0.46020538…, 0.42067415…, 0.38192128…, 0.27375402…, 0.13457621…) by exact
rational equality against the strings quoted from the parent's
results.json @ fda94d0 — the two verdicts' FUN legs are the same binomial,
so every T1 cell is cell-addressable against its G1 parent.

**(2) The agreement gate PASSES — the MC is believed.** Max pooled
deviation across all 35 pre-registered comparisons (15 FUN + 15 R1-wipe +
5 T1×R1 grinder-capped): 0.78 pp vs the 1.0 pp band. The t=0 optional-
stopping control reproduces P_double = 1/3 exactly in BOTH the closed form
and the independent tridiagonal elimination; the capped finite-horizon DP
agrees with the capped MC on every take (capped-vs-uncapped gap disclosed:
at t=0 the 4,000-round cap holds back 1/3 → 0.1123 of doubling mass — the
pre-registered indeterminacy machinery, not a bug). Of the 210 per-leg
readings additionally reported, 19 exceed 1.0 pp (max 2.45 pp ≈ 2.8
per-leg MC SE at the stability leg's M — the noise level disclosure 1
anticipated; no reading exceeds 3 SE). The aux stream corroborates every
Arm-A tail at 4 SE.

**(3) The envelope: ONE surviving cell — E\*(T1, c=5) = {0.05}; every T2
and T3 cell fails.** Per-band anatomy:

- **T1 (even-money): the structure lever WORKS at the tight cap.** At
  (t=0.05, c=5): FUN 0.2738 (exact), worst-policy P_wipe 0.0024 (binding
  policy RG), worst-policy P_double 0.0000 measured (uncapped exact
  4.5e−05), determinate (cap_frac 0.0035). Its parent cell (G1, e=0.05,
  m=0.05) died on SAFE at 0.1358 — the fee frame cuts the worst-policy
  wipe **57×** and closes the parent's only gap. t ∈ {0.01, 0.02} at c=5
  pass all three bands on measured numbers but are INDETERMINATE
  (R1-grinder cap_frac 0.32 / 0.17 — the slow unit-step walk, the
  parent's F-0.01 precedent) and route to NULL-support only, never
  APPROVE; t=0.10 fails FUN (0.1346, the parent's identical value). At
  c ≥ 25 SAFE collapses via the greedy re-buyer (RG P_wipe 0.116–1.000)
  — RG's compounding at high caps recreates exactly the wipe the parent
  measured, while c=5 tames it.
- **T2 (tiered): dead in a pincer, all 12 cells.** SINK fails at low take
  at EVERY cap (worst-policy P_double 0.244 / 0.163 at t = 0.01 / 0.02 —
  inside the parent's 0.195–0.323 wall) and SAFE fails at high take
  (best cell (t=0.05, c=5): worst-policy P_wipe 0.0608, 1.2× the band,
  binding RG; 0.173 at t=0.10). No take clears both walls: the residual
  gap is real but small — 0.0608 vs 0.05 — and pre-registered as the
  quantified gap, not rounded away.
- **T3 (jackpot): SINK unreachable, all 12 cells — the parent's wall
  reproduced in the fee frame.** Worst-policy P_double 0.148–0.346 vs the
  0.10 band at every (t, c) (parent G3: 0.220–0.296): one 25F hit from
  B₀ jumps a quarter of the way to double, and the take moves the hit
  probability only by the factor (1−t). SAFE also fails everywhere
  (0.275–1.000): five 16-variance tickets per round out-wipe the parent's
  single 5% stake. Both failing bands sit 1.5–20× over their lines at
  the shape's best cell (t=0.10, c=5: SINK 0.1480, SAFE 0.4574).

**(4) The pre-registered REJECT rule fires: E\* = ∅ at every cap in 2 of 3
shapes (T2, T3; the rule needs ≥ 2), both arms where covered, evaluated
FIRST.** The per-shape residual gap (the failing band at the shape's best
cell): T2 SAFE 0.0608 vs 0.05 at (t=0.05, c=5); T3 SINK 0.1480 vs 0.10 at
(t=0.10, c=5); T1's gap is CLOSED at (t=0.05, c=5) — reported prominently
because the envelope table ships on every outcome, but one surviving shape
cannot block the rule the proposal registered.

**(5) Indeterminacy touched nothing load-bearing.** 10 of 36 decision
cells are indeterminate (T1 t ≤ 0.02 all caps and T2 t ≤ 0.02 all caps,
via the R1/R5 slow walks; max cap_frac 0.32) — but every indeterminate T2
cell already fails SINK on measured lower bounds (failures stand under
censoring by construction), and the two indeterminate-PASS cells (T1
t ∈ {0.01, 0.02} at c=5) could at most ADD T1 takes — they cannot rescue
T2/T3 emptiness, which is what REJECT reads. The pre-registered
indeterminate-routes-to-NULL path was never load-bearing.

**(6) Stability + controls.** The half-M seed-20260731 leg reproduces
REJECT with the IDENTICAL envelope map ({0.05} at (T1, c=5), all else
empty) and the identical two indeterminate-pass cells. The t=0 Wald
prize-fairness control passes on every t=0 leg; per-replication
conservation holds on all 1,845,000 primary + 922,500 stability
replications; 1,620 traced replications replay exactly through the
independently written twin kernel; draw-count accounting closes exactly
(1,214,568,503 primary + 605,734,597 stability draws, one per ticket,
fresh-Random sentinels). Twin decision evaluators (exact integer
cross-multiplication vs Fractions) agree on ruling, envelope, and shares.
**1,925,723 self-checks, 0 failed.**

**(7) Harm context (reporting-only) + the price tag.** Compulsive R1 play
ruins in a median of 622–1,432 rounds on T3 (ruin fraction 0.87–1.00 at
any take incl. t=0), 851–6,227 on T2, 969–7,238 on T1 (t ≥ 0.01) — the
jackpot shape again eats bankrolls fastest regardless of take. The
expected-loss price tag at the surviving cell (T1, t=0.05, c=5): a casual
R1 session costs 5.2% of B₀ on average; the worst swept policy (RG) 25.2%
— bounded, unlike the parent's unbounded stake escalation, but not small.

## What it did NOT settle

- **Absolute economy pricing (the pre-registered boundary, restated
  verbatim):** all conclusions are bankroll-RELATIVE (chips normalized to
  B₀) — nothing here prices the casino sink against fishing/mining faucet
  mint in absolute chips/hr; that needs the live earn-rate baseline whose
  absence V001 and V008 both named and VERDICT 022 restated, and their
  telemetry caveat applies verbatim (no live fishing/mining earn-rate
  baseline exists in source, so reward-VALUE conclusions stay provisional
  until the named telemetry slice exists upstream).
- **Skill and strategy:** tickets are i.i.d.; a game's strategy spread
  folds into the take grid as the REALIZED take.
- **The re-buy policy space:** R1/R5/RG/MC bracket unit, bounded,
  greedy-compounding, and loss-chasing behavior; any b-policy is bounded
  between R1 and RG by the cap — stated, not proven.
- **The bands themselves:** inherited from the parent BY DESIGN; full
  curves ship in `results.json` so a re-drawn line re-reads, never
  re-runs. (Note: no plausible re-draw rescues T3 — SINK and SAFE both
  carry its emptiness at multiples of the bands.)
- **Comp/stipend design:** the third routed lever is NOT simulated here —
  it remains routed, now the natural next head.
- **Mixed prize tables:** three schedules bracket the shape axis;
  interpolation is on the consumer.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The model abstracts a house-banked ticket minigame to i.i.d. integer
F-unit draws against a pinned prize schedule — no skill, no mixed tables,
no session psychology. The load-bearing conclusion (T2/T3 cannot hold the
three bands in ANY (t, c) cell — SINK is not take-controllable for
high-variance prize shapes, and multi-ticket re-buys re-import the wipe
risk the fee removed from stakes) is variance arithmetic that any real
prize table with these shapes inherits; a mixed table lands between the
swept brackets. The one gap that could move a number — a
strategy-dependent realized take — is folded into the t-grid by
construction and disclosed.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **1,925,723 self-checks, 0 failed**, exit-coded: per-replication
conservation (final = B₀ + prizes − tickets on every one of the 2,767,500
replications), the exact cross-verdict identity gate, DP-mass and
support-bound identities, closed-form ≡ elimination ≡ (capped DP → closed
form) on the grinder chain, the t=0 = 1/3 and Wald fairness controls, an
INDEPENDENTLY WRITTEN twin kernel replaying 1,620 traced replications
exactly, two hand-derived pins committed with derivations BEFORE the
runner, exact draw-count sentinels closing at 1.82 billion uniforms,
fixture cross-checks in Fractions, and twin decision evaluators. No
seeded luck: Arm A is seedless and exact; the MC passes the 1.0 pp gate
against it and a DIFFERENT seed (20260731) reproduces the ruling and the
entire envelope map. No cherry-picking: the full 36 × 4 × 3-profile table
is committed for both legs, including the t=0 control, the
indeterminate-pass cells, and the surviving T1 cell that does NOT support
the ruling's direction.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The REJECT is margin-heavy on its decisive components: T3's SINK failures
sit 1.5–3.5× over the band across ALL 12 cells (MC SE ≈ 1.0 pp) with SAFE
failures 5–20× over; T2's low-take SINK failures sit 1.6–2.5× over at
every cap. The one knife-edge in the grid — T2 (t=0.05, c=5) SAFE at
0.0608 vs 0.05 (≈ 3.5 pooled SE above the band; stability leg agrees on
the failure) — is decision-relevant only jointly with T2's SINK wall one
grid step away (0.163 at t=0.02, 1.6× the band); no single knife-edge
carries the ruling. The stability leg reproduces every emptiness
determination at half M on a fresh seed. FUN values are exact, not
sampled.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, hermetic; one
`random.Random(<pinned seed>)` stream per leg consumed in the pinned loop
order, exactly one draw per ticket. stdout AND `results.json`
byte-identical across TWO complete process runs by external `diff` on
cpython-3.11 (pinned in `results.json` and asserted at start). Arm A is
platform-independent exact rational arithmetic. Runtime ~5.2 min per run.

**5. "LIMITS? what this evidence does NOT show."**
It prices nothing in absolute chips/hr (the V001/V008 telemetry wall,
restated above); it says nothing about skill-based tickets beyond the
realized-take fold-in; the 0.25/0.05/0.10 lines are the parent's
pre-registered judgments, inherited by design (full curves shipped); the
policy set brackets rather than enumerates re-buy behavior; 10
already-failing or T1-only cells carry > 1% grinder censoring (disclosed,
never load-bearing for the ruling); and the COMPULSIVE leg is harm
CONTEXT, not a behavioral model of real players.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Every constant, band, seed, and the evaluation order were registered in
the idea file before any code; the decision arithmetic is exact integer
cross-multiplication confirmed by an independent Fraction evaluator; the
MC is gated by a seedless exact arm and passes; the cross-verdict identity
is exact; the ruling reproduces on a second seed at half M; and the
emptiness determinations are definitive even under the disclosed
censoring. The honest boundary: this strength attaches to the pinned
i.i.d. ticket-frame family and the inherited bands — it rules the
ENTRY-FEE LEVER out as a universal house frame, it does not design the
comp/stipend lever, and it explicitly does NOT kill the even-money ticket
row it measured healthy.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — the fee frame cannot do it either (as a one-rule
  house frame).** By the rule committed before any code (REJECT evaluated
  first): E\*(g, c) = ∅ at EVERY cap in 2 of 3 shapes (T2 tiered, T3
  jackpot; the rule needs 2/3), both arms where covered,
  stability-reproduced. The second of VERDICT 022's three routed levers is
  struck from the list with its gap quantified; **comp/stipend and
  rake-only PvP are the only levers left standing**, and tonight's
  consolidation does not spend design effort on fee/prize shapes as a
  general mechanism.
- **The headline chained measurement (reported with equal prominence):**
  the structure lever's hypothesis — "turns the SAFE failure from a
  bankroll event into a bounded fee" — measured TRUE for the even-money
  shape: the parent's near-miss cell, transposed to T1 (t=0.05, c=5),
  passes ALL THREE bands (FUN 0.2738 exact-identical, worst-policy P_wipe
  0.0024 vs the parent's 0.1358, worst-policy P_double 0.0000 with
  uncapped exact 4.5e−05). E\*(T1, c=5) = {0.05} is the grid's one
  surviving cell. What kills the LEVER is shape-universality: T2's
  SINK/SAFE pincer (0.244/0.163 doubling at low take; 0.0608 wipe at its
  best cell) and T3's reproduced SINK wall (0.148–0.346 everywhere) — the
  same variance arithmetic that killed the odds lever, now measured in
  the fee frame.
- **If a house-banked ticket game ships anyway** (owner's call against
  the one-rule reading), the measured row is: even-money double-up ONLY,
  ticket 0.01·B₀, per-round cap 5 tickets (5%·B₀), take 0.05 — with the
  riders that c=5 is load-bearing (at c ≥ 25 the greedy re-buyer wipes
  0.12–1.00 of sessions — the parent's MAXBET ≤ 0.05·B₀ rider transposes
  intact), t=0.10 breaks FUN (0.1346), and t ≤ 0.02 leaves the grinder
  question censored (indeterminate, a NULL path). Tiered and jackpot
  prize tables are NOT house-bankable under these bands at any swept
  (t, c) — they inherit the parent's PvP/rake routing.
- **Riders (measured):** the expected-loss price tag at the surviving
  cell is 5.2% of B₀ per casual R1 session (25.2% for the greedy
  re-buyer) — bounded, unlike the parent's unbounded stake escalation,
  but not small; compulsive harm context: median 622–1,432 R1 rounds to
  ruin on jackpot shapes at every take, ruin fraction ≥ 0.87 even at t=0
  within 20,000 rounds.
- **Boundary restated (pre-registered):** all numbers are
  bankroll-relative; the V001/V008 earn-rate-baseline caveat applies
  verbatim to any absolute chips/hr reading; tickets are i.i.d. with
  strategy spread folded into the realized take; reporting-only legs
  (compulsive, t=0 control, chained anchors, expected-loss table) cannot
  and did not flip the decision.
- **Named follow-ups (not ordered):** the comp/stipend envelope sim — the
  THIRD routed lever, now the last unpriced one (the natural successor
  head this REJECT routes); the wager-flow-map tracer head consumes the
  per-shape take check only if a house-banked ticket surface survives the
  consolidation; the earn-rate telemetry wall stays walled and is
  restated, not re-attempted.
- **Codex review:** none this cycle — the @codex step is suspended per
  the outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey
  stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V024 slice boundary, with header timestamps from live
`date -u` at append time. -->
