# REPORT — casino fairness envelope (PROPOSAL 020)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 020** ·
> 2026-07-13T02:04:02Z · status: sim-ready (idea
> `ideas/superbot/casino-house-edge-fairness-envelope-2026-07-13.md`, landed via
> idea-engine PR #286, main `da20713`). The ORDER 004 rule-3 GAME-MECHANICS rotation
> slot, taken early because the consumer window (tonight's superbot minigame/casino
> consolidation — inbox ORDER 004 "World's balance pins") closes tonight. Fully
> hermetic (the PROPOSAL 017/018/019 precedent): every fixture is a pinned constant
> committed with the sim; zero repo/network reads in the verdict session.
> Run: `python3 sims/verdict-022-casino-fairness/casino_fairness_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic, band-scored
against the pre-registration, with a dual ANALYTIC arm gating the Monte
Carlo): integer-chip bankroll walks driven through the full 36-cell ×
5-policy grid at M = 5,000 casual / 2,000 grinder / 500 compulsive per
cell-policy, `random.Random(20260721)` in the pinned loop order; Arm A
computes the FUN reference tails and the G1×C grinder probabilities EXACTLY
(Fraction arithmetic, seedless; the ruin closed form independently re-derived
by tridiagonal elimination) and Arm S must agree within the pre-registered
1.0 pp before any MC number is believed; every band decision is an exact
integer cross-multiplication. This label fills the outbox `evidence:
simulation`. The one judgment question — whether 0.25 / 0.05 / 0.10 are the
RIGHT lines — was pinned by pre-registration in the idea file and is
disputable only about the bands, never about the measured numbers (the full
P_ahead / P_wipe / P_double curves ship in `results.json`, so a re-drawn line
re-reads, never re-runs).

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock; every
constant ({B₀, k-grid, e-grid, m-grid, policy constants, profile stop rules,
M per profile, seeds, band constants}) was copied verbatim from the idea file
into `fixtures.json` BEFORE the runner was written, and the runner
cross-checks its literals against that file at start (including asserting EV
per unit staked = −e exactly, per (k, e), in Fractions). Intake-time
decisions, ALL disclosed in `fixtures.json`: the agreement-gate granularity
reading (per-edge pooled across the three cap-legs of the cap-independent
G1×C process — at the registered M=2,000 a per-cap reading puts the whole
1.0 pp gate at ~1 MC standard error, a coin flip on noise; the 15 per-cap
deviations are additionally reported), the martingale target-clip identity,
the P_double denominator, the compulsive median convention, the aux
self-check stream (seed 20260723, never read by any decision number), and
ONE amendment made after a throwaway-seed smoke run but BEFORE any
pinned-seed run: the e=0 fairness self-check statistic was changed from a
mean-final t-check (statistically invalid on the heavy-tailed k=19
fixed-fraction legs — the sample SD wildly under-estimates the true SD and
false-alarms on a fair game) to the win-indicator Wald martingale check. The
pinned decision machinery (grids, seeds, bands, rule, evaluation order) is
untouched by any disclosure.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Bankroll walk:** B₀ = 1,000 integer chips, min stake 1; per bet, stake =
  min(policy raw stake, MAXBET, bankroll), one `rng.random()` draw, win pays
  stake·k, loss costs the stake. Archetypes (p = (1−e)/(k+1), EV per unit
  staked = −e exactly): **G1** even-money k=1, **G2** mid-variance k=5,
  **G3** jackpot k=19. Edges e ∈ {0.01, 0.02, 0.05, 0.10} + e=0 control
  (reporting-only). Caps MAXBET = m·B₀, m ∈ {0.05, 0.25, 1.0}.
- **Policies (5 swept):** F-0.01 / F-0.05 / F-0.10 fixed-fraction
  (max(1, ⌊β·bankroll⌋), exact integer floors), C constant-50, M capped
  martingale (base 10, double on loss, reset on win); plus the analytic-only
  constant-10 FUN reference leg (exact binomial: ahead iff wins·(k+1) > 100).
- **Profiles:** CASUAL (100 bets or bust; P_ahead = P(final > B₀), P_wipe =
  P(final ≤ 100)); GRINDER (to ≥ 2,000 or ≤ 500, cap 4,000 bets; P_double =
  doubles/M, cap-hits counted separately, > 1% marks the cell indeterminate —
  a NULL path, never silently absorbed); COMPULSIVE (reporting-only, C
  policy, to ruin or 20,000 bets; median bets-to-ruin).
- **Bands:** FUN = reference P_ahead ≥ 0.25 · SAFE = max-policy P_wipe ≤
  0.05 · SINK = max-policy P_double ≤ 0.10. **E\*(g, m)** = edges where all
  three hold. **Decision rule (registered before any code; evaluated in this
  order):** REJECT iff E\* = ∅ at every cap in ≥ 2/3 archetypes (both arms
  where covered); APPROVE iff some cap m\* gives ≥ 2 consecutive shared
  edges across all archetypes (stability-reproduced, determinate cells
  only); NULL otherwise, flip axis named via per-axis envelope shares.
- **Legs:** primary (decision, seed 20260721); half-M stability (seed
  20260722, must reproduce the ruling); aux self-check stream (seed
  20260723, reference-leg MC corroboration only).

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json` (Arm A values kept as exact fractions).

**(1) The agreement gate PASSES — the MC is believed.** Pooled per-edge
G1×C P_double deviations from the exact closed form: e=0 0.167 pp, e=0.01
0.447 pp, e=0.02 0.720 pp, e=0.05 0.109 pp, e=0.10 0.051 pp — all inside
the pre-registered 1.0 pp. The e=0 control reproduces P_double = 1/3
(measured 0.3317 pooled, exact 1/3 by optional stopping; the closed form and
the independently coded tridiagonal elimination agree exactly on all five
edges). Per-cap deviations (disclosed per fixtures disclosure 1): 4 of 15
exceed 1.0 pp, max 1.93 pp at e=0, m=0.25 — consistent with the ~1.05 pp
per-cap MC standard error the pooling disclosure anticipated; no per-cap
deviation exceeds 2 SE. Aux reference-leg MC agrees with the exact binomial
tails on all 15 (g, e) cells within 4 SE (max dev 2.0 pp at 2.8 SE bound).

**(2) The envelope is EMPTY — all 36 cells fail, at every cap, in all three
archetypes (the rule needs 2/3).** Per-band anatomy:

- **SINK fails in 33/36 cells.** Worst-policy P_double across the whole
  grid: G2 0.195–0.323, G3 0.220–0.296, G1 0.017–0.376 — vs the 0.10 band.
  For G2/G3 NO edge at NO cap passes SINK: p = (1−e)/(k+1) moves only by the
  factor (1−e) as e sweeps 0.01 → 0.10 (for k=19, p goes 0.0495 → 0.045), so
  the house edge barely dents a high-variance grinder's doubling odds — one
  19:1 hit from B₀ jumps most of the way to double. The doubling probability
  is variance-dominated, not edge-controlled: at the e=0 control the same
  cells measure 0.30–0.41, and a 10% edge buys back only a few points.
  Only G1 — where the gambler's-ruin closed form applies — is
  edge-controllable: SINK passes exactly at (e=0.05, m=0.05) 0.0895 (exact
  Arm A for the binding C policy: 0.0899 = 1,721/19,147…≈), (e=0.10, m=0.05)
  0.0170, (e=0.10, m=0.25) 0.0975.
- **SAFE fails in 36/36 cells.** At the tight cap m=0.05 the binding policy
  is flat C-50 (5% of B₀): P_wipe 0.063 (G1, e=0.01) → 0.725 (G3, e=0.10);
  at m ≥ 0.25 the capped martingale is the wipe machine: 0.182 → 0.983.
  Structural: even at the e=0 control, C-50 wipes 5.7% (G1, m=0.05) and
  martingale wipes 27.6–97.5% (m=1.0) — within 100 bets, wipe risk is
  gambler's-ruin VARIANCE, not edge; no odds setting in the grid (or outside
  it) can pull flat-5%-stake wipe under the 0.05 band.
- **FUN fails in 3/36 cells** (Arm A exact): only G1 at e=0.10 (0.1346 <
  0.25). FUN is otherwise comfortable: G2 0.4879–0.3275 and G3 0.3750–0.2950
  pass at EVERY edge in the grid — high-variance shapes stay "winnable"
  even at a 10% edge, which is exactly why they cannot be sink-proofed.

**(3) The nearest miss quantifies the three-way bind.** (G1, e=0.05,
m=0.05) passes FUN (0.2738 exact, 9.5% over the band) AND SINK (0.0895) but
fails SAFE at 2.7× the band (P_wipe 0.1358, via flat C-50; the martingale is
TAMED there by the tight cap — M P_wipe 0.007). One cell to the right,
(G1, e=0.10, m=0.05), SAFE worsens to 0.268 and FUN collapses to 0.1346.

**(4) The pre-registered REJECT gap, per archetype (FUN at the smallest
SINK-passing edge):** G1 m=0.05 → e=0.05, FUN there 0.2738 (FUN survives;
SAFE is what kills the cell); G1 m=0.25 → e=0.10, FUN there 0.1346 (the
classic fun/sink tension: the edge that stops grinders starts boring
casuals); G1 m=1.0 and ALL of G2/G3 at every cap → NO SINK-passing edge in
the grid (the gap is unbounded in-grid; the odds lever cannot reach it).

**(5) Indeterminacy touched nothing.** 7 cells are indeterminate (grinder
cap-hits > 1%, all via F-0.01's slow walk: G1 e ∈ {0.01, 0.02} at all caps,
0.19–0.38 cap fraction; G2 e=0.01 m=0.05 at 0.012) — but every one of them
fails DEFINITIVELY anyway: FUN is analytic, SAFE sessions always complete,
and measured P_double is a lower bound on the uncapped quantity, so SINK
failures stand. The pre-registered indeterminate-routes-to-NULL path was
never load-bearing; `c_leg_band_side_flips_G1` is empty (MC and exact agree
on every band side Arm A covers).

**(6) Stability + controls.** The half-M seed-20260722 leg reproduces
REJECT with the identical all-36-empty envelope. The e=0 win-martingale
fairness check passes on all 99 × 2 control legs; per-replication
conservation holds on all 2,598,750 replications; 1,980 traced replications
replay exactly through the independently written twin kernel; draw-count
accounting closes exactly (247,448,560 primary + 123,439,648 stability
draws, one per bet). **13,392,272 self-checks, 0 failed.**

**(7) Harm context (reporting-only).** Compulsive flat-50 play at m=1.0
ruins in a median of 40 bets on G3 (any edge), 92–173 on G2, 160–525 on G1;
ruin fraction ≥ 0.98 at every e ≥ 0.01 (and 0.92–0.98 even at e=0 within
20,000 bets). A jackpot-shaped house game eats a session bankroll in ~40
flat bets regardless of how "fair" the edge is.

## What it did NOT settle

- **Absolute economy pricing (the pre-registered boundary, restated
  verbatim):** all conclusions are bankroll-RELATIVE (chips normalized to
  B₀) — nothing here prices the casino sink against fishing/mining faucet
  mint in absolute chips/hr; that needs the live earn-rate baseline whose
  absence V001 and V008 both named, and their telemetry caveat applies
  verbatim (no live fishing/mining earn-rate baseline exists in source, so
  reward-VALUE conclusions stay provisional until the named telemetry slice
  exists upstream).
- **Skill and strategy:** bets are i.i.d.; a game's strategy-spread edge is
  folded into the e-grid as the REALIZED edge. Card-counting-like state is
  out of scope.
- **The FUN line itself:** P_ahead ≥ 0.25 is the pre-registered, disputable
  proxy; the full curves ship in `results.json` so a re-drawn line re-reads,
  never re-runs. (Note: no plausible re-draw rescues the envelope — SAFE
  and SINK, not FUN, carry the emptiness.)
- **Mixed-payout games:** k ∈ {1, 5, 19} brackets the shape axis;
  interpolation is on the consumer.
- **Session psychology, comps, stipends:** the named non-odds levers are
  routed, not simulated — they are follow-up design questions, priced here
  only by the measured gap they must close.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The model abstracts a wager minigame to an i.i.d. integer bankroll walk with
a pinned (p, k) pair — no skill, no mixed payout tables, no session
psychology. The load-bearing conclusion (no (edge × cap) cell can hold
FUN ∧ SAFE ∧ SINK simultaneously; for high-variance shapes SINK is not
edge-controllable at all) is driven by variance arithmetic that any real
house-banked game with these payout shapes inherits; a mixed-payout real
game lands between the swept brackets. The one gap that could move a
number — a strategy-dependent realized edge — is folded into the e-grid by
construction and disclosed.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **13,392,272 self-checks, 0 failed**, exit-coded: per-replication
conservation (final = B₀ + won − lost on every one of the 2,598,750
replications), stop-validity and outcome-classification invariants, G1×C
exact-boundary hits, an INDEPENDENTLY WRITTEN twin kernel (dict state,
name-keyed dispatch, per-bet stake-bound assertions) replaying 1,980 traced
replications exactly, two hand-derived pin scenarios with committed
derivations (the seven-loss martingale wipe path; the two-win jackpot double
under the tight cap), draw-count accounting against a fresh Random(seed)
(first draw + post-sweep sentinel), the e=0 win-martingale fairness control
on every e=0 leg, exact-Fraction Arm A identities (binomial mass = 1, closed
form = elimination, e=0 = 1/3, EV = −e per (k, e)), fixture cross-checks,
and twin decision evaluators (independent code paths) agreeing on ruling,
envelope map, and shares. No seeded luck: Arm A is seedless and exact; the
MC passes the pre-registered 1.0 pp gate against it, and a DIFFERENT seed
(20260722) reproduces the ruling and the entire (empty) envelope. No
cherry-picking: the full 36 × 5 × 3-profile table is committed for both
legs, including the e=0 control and the near-miss cells.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The REJECT is margin-heavy on its decisive components: G2/G3 SINK failures
sit 2.0–3.2× over the band across ALL 24 cells (worst-policy P_double
0.195–0.323 vs 0.10) with MC SE ≈ 0.9 pp; SAFE failures run 1.3–20× over
the band across the grid. The one knife-edge in the whole grid — G1
(e=0.05, m=0.05) SINK at 0.0895 vs the 0.10 band — PASSES SINK and is
irrelevant to the ruling (its cell dies on SAFE at 2.7× the band; and G1's
emptiness is not needed for the ≥ 2/3 rule that G2+G3 already satisfy).
The stability leg reproduces every empty-envelope determination at half M
on a fresh seed. FUN values are exact, not sampled.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, hermetic; one
`random.Random(<pinned seed>)` stream per leg consumed in the pinned loop
order, one draw per bet. stdout AND `results.json` byte-identical across TWO
complete process runs by external `diff` on cpython-3.11 (pinned in
`results.json` and asserted at start). Arm A is platform-independent exact
rational arithmetic. Runtime ~72 s.

**5. "LIMITS? what this evidence does NOT show."**
It prices nothing in absolute chips/hr (the V001/V008 telemetry wall,
restated above); it says nothing about skill-based games beyond the
realized-edge fold-in; the 0.25/0.05/0.10 lines are pre-registered
judgments, not measurements (full curves shipped for re-reading); k ∈
{1, 5, 19} brackets rather than enumerates the payout-shape axis; the
grinder's 4,000-bet cap leaves 7 already-failing cells with > 1% censoring
(disclosed, never load-bearing); and the COMPULSIVE leg is harm CONTEXT, not
a behavioral model of real players.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Every constant, band, and the decision order were registered in the idea
file before any code; the decision arithmetic is exact integer
cross-multiplication; the MC is gated by a seedless exact arm and passes;
the ruling reproduces on a second seed at half M; and the emptiness
determinations are definitive even under the disclosed censoring. The honest
boundary: this strength attaches to the pinned i.i.d. bankroll-walk family
and the pre-registered bands — it rules the ODDS LEVER out, it does not
design the replacement lever.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — odds cannot do the job.** By the rule committed
  before any code (REJECT evaluated first): E\*(g, m) = ∅ at EVERY cap in
  3/3 archetypes (the rule needs 2/3), both arms where covered, stability-
  reproduced. No (house-edge band × max-bet cap) cell holds FUN ∧ SAFE ∧
  SINK simultaneously for ANY payout shape in the grid.
- **The consequence, pre-registered and binding:** tonight's minigame/casino
  consolidation does NOT tune per-game odds hoping to reconcile fun with
  sink-proofing — the sim proves the reconciliation does not exist inside
  the odds lever. The named non-odds levers ride to the World seat with the
  quantified gap: **rake-only PvP framing** (the PvP-rake identity prices it
  free: even-money PvP with pot-rake r is G1 at e = r for each symmetric
  player — at r = 0.05 that is the measured near-miss row: FUN 0.2738,
  P_double 0.0899 exact, and the house takes rake risk-free, making SINK
  structural rather than statistical), **session comp/stipend**, and
  **entry-fee-with-prize** shapes (both turn the SAFE failure from a
  bankroll event into a bounded fee, the one thing no in-grid cell could
  do).
- **The two measured shapes of the gap** (what the levers must close): for
  high-variance shapes (G2/G3) SINK is unreachable by odds — worst-policy
  P_double 0.195–0.323 at EVERY edge and cap vs the 0.10 band, because the
  edge barely moves p when k is large; for even-money (G1) the classic
  fun/sink tension binds at m=0.25 (SINK first passes at e=0.10 where FUN
  is 0.1346 < 0.25), and at the tight cap m=0.05 the survivor cell
  (e=0.05: FUN 0.2738, SINK 0.0895) dies on SAFE (flat-5% wipe 0.1358,
  2.7× the band) — wipe risk within 100 bets is variance, not edge.
- **If a house-banked game ships anyway** (owner's call against this
  evidence), the least-bad in-grid row is the G1 near-miss (k=1, e=0.05,
  MAXBET = 0.05·B₀) with its measured SAFE violation stated: 13.6% of
  flat-50 casual sessions lose ≥ 90% of the session bankroll. The verdict
  does not recommend it; it prices it.
- **Riders (measured):** the martingale cap matters — at m=0.05 the cap
  tames capped-martingale wipe to 0.007 at the near-miss cell, at m ≥ 0.25
  martingale wipes 0.18–0.98 of sessions (any consolidation that keeps ANY
  house-banked wager surface should pin MAXBET ≤ 0.05·B₀ for SAFE reasons
  alone); compulsive harm context: median 40 flat bets to ruin on
  jackpot shapes at any edge.
- **Boundary restated (pre-registered):** all numbers are bankroll-relative;
  the V001/V008 earn-rate-baseline caveat applies verbatim to any absolute
  chips/hr reading; reporting-only legs (compulsive, e=0 control, PvP-rake
  identity, per-policy curves) cannot and did not flip the decision.
- **Named follow-ups (not ordered):** a rake-band sweep for the PvP lane
  (the G1 row already prices r ∈ {0.01…0.10} analytically); an
  entry-fee/prize-table envelope sim (the SAFE-band successor question);
  the wager-flow-map tracer head consumes this verdict's per-game (p, k)
  edge check only if a house-banked surface survives the consolidation.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V021 slice boundary, with header timestamps from live
`date -u` at append time. -->
