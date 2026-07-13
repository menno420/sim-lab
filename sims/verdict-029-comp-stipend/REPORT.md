# REPORT — Comp/stipend envelope: the LAST routed lever (PROPOSAL 027)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 027** ·
> 2026-07-13T06:04:37Z · status: sim-ready (idea
> `ideas/superbot/casino-comp-stipend-envelope-2026-07-13.md`, landed via
> idea-engine PR #294, main `3978df1`). The ORDER 004 rule-3 GAME-MECHANICS
> rotation slot, round 3 — the program's first three-generation chained
> verdict line: V022 (odds, reject) → V025 (entry fee, reject) → here (comp,
> the last of V022's routed levers). Fully hermetic: every fixture is a
> pinned constant committed with the sim; zero repo/network reads in the
> verdict session; both parents' anchors quoted from their committed files @
> `5e356ed`.
> Run: `python3 sims/verdict-029-comp-stipend/comp_stipend_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — a seeded deterministic 48-cell ×
4-policy × farmer-family four-band grid sweep, band-scored against the
pre-registration in exact integer/Fraction comparisons by twin independently
coded evaluators, with a seedless exact analytic arm — comp-shifted
`math.comb` binomials, bigint DP convolutions, a banded-Fraction stopper DP,
ruin closed form/elimination/capped DP — gating the MC at the pre-registered
1.0 pp and carrying every decision-relevant exact quantity). The FUN band and
every Arm-A-covered MINT leg are decided on EXACT values; SAFE/SINK/DET and
the MC-only MINT legs on integer count totals. This label fills the outbox
`evidence: simulation`. The judgment lines (0.25/0.05/0.10/0) were pinned by
pre-registration; full curves ship in `results.json`, so a re-drawn line
re-reads, never re-runs.

## PREMISE (verified at drafting, pinned into the fixtures — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`,
cross-checked at start) and touches no repo state, network, or wall clock.
The substrate is VERDICT 025's measured surviving frame, inherited
cell-for-cell BY DESIGN: B₀ = 1,000 chips, F = 10, **c = 5 FIXED** (both
parents measured the tight cap load-bearing), shapes T1/T2 with T3 excluded
by citation of V025's measured walls (+ a monotonicity spot cell), takes
t ∈ {0.05, 0.10} + t=0 control. The σ=0 baseline Fractions and V025's
measured baseline rows are quoted verbatim in the fixtures and re-verified
in-run (exact rational equality for the exact quantities — the grid's third
chained verdict on one binomial). Eighteen intake-time decisions are
disclosed in `fixtures.json` BEFORE the runner existed, including the σ = t
boundary rule, MINT exact-where-covered, stopper ρ-invariance, and the
pre-run gate-calibration SE arithmetic (the V027 lesson, applied at
registration). One disclosed correction: hand-pin 1's originally committed
expectation mis-applied the b ≤ ⌊bankroll/F⌋ affordability clamp on its final
round (asserted 5 tickets where bank = 400 cu affords 4); the kernel and the
independently written twin both followed the registered rule, and the pin's
EXPECTATION was corrected before the accepted runs
(`fixtures.json` → `hand_derived_pins[0].derivation_correction`). No decision
constant, band, seed, M, or convention changed.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Comp designs** on the ticket frame (exact integer centi-unit
  arithmetic): **D1 qualified stipend** σ·B₀ at session end iff handle ≥ B₀;
  **D2 handle rebate** σ·F per ticket, continuous and spendable, session cap
  2σ·B₀ (= exactly 200 rebated tickets); **D3 loss rebate** ρ·(B₀ − final)⁺
  at session end. D1/D2 over σ ∈ {0.02, 0.05, 0.10, 0.20}, D3 over
  ρ ∈ {0.2, 0.4, 0.6, 0.8}. 48 decision cells + 4 σ=0 baseline cells that
  must reproduce V025's committed rows.
- **Players:** policies R1/R5/RG/MC and profiles CASUAL / GRINDER (wealth-
  including-comp stop targets; > 1% cap-hits = indeterminate) / COMPULSIVE
  (reporting-only) verbatim from V025. **Farmer family (the MINT attack):**
  D1 wash-qualifier (exactly the minimum qualifying handle), D2 cap-chaser
  (to the rebate cap), D3 12-variant optimal-stopping grid (b ∈ {1,5} ×
  τ ∈ {1.1, 1.25, 1.5}·B₀ × φ ∈ {0, 0.5·B₀}, max EV taken — a LOWER bound
  on the exploit).
- **Bands (all four must hold; determinate cells only):** FUN — reference
  R1 P_ahead incl. comp ≥ 0.25; SAFE — max-policy P_wipe incl. comp ≤ 0.05;
  SINK — max-policy P_double incl. comp ≤ 0.10 (inherited verbatim from
  V022/V025 BY DESIGN); **MINT** — max over the 8 policy legs AND the farmer
  family of E[session net incl. comp] ≤ 0 (weak; max = 0 exactly ⇒ marked
  BOUNDARY — the σ = t knife-edge).
- **Arm A (exact):** comp-shifted FUN for all 52 cells; exact casual-R1
  wipe (D3 wipe ≡ 0 for every ρ ≥ 0.2 — wealth at total ruin is ρ·B₀) and
  E[net incl. comp]; identities D1-FUN ≡ D2-FUN and D3-FUN ≡ baseline-FUN;
  the pump line D1-wash EV = (σ−t)·B₀ exactly (D2 cap-chaser sign-exact by
  Wald, = 0 exactly at σ = t); exact banded-Fraction stopper exit
  distributions on T1 (b=1 variants ≡ the gambler's-ruin closed form,
  asserted); V025's three-derivation grinder machinery; t=0 P_double = 1/3.
- **Arm S:** `random.Random(20260752)` primary (M = 5,000/2,000 per
  cell-policy; farmers 5,000/2,000/4,000), 20260753 stability (half M, must
  reproduce the ruling), 20260754 reporting (t=0 control, compulsive, T3
  spot, aggregation spot check), 20260755 aux (8× re-measure protocol for
  gate breaches; the aggregation twin). Pinned loop order, one
  `rng.random()` per ticket, counted streams.
- **Decision rule (registered order):** REJECT iff NO (design, size)
  rescues C1 = (T1, t=0.10) and none rescues C2 = (T2, t=0.05) — boundary
  and indeterminate passes BLOCK reject but can never support APPROVE;
  APPROVE iff some design rescues C1 at ≥ 2 CONSECUTIVE clean sizes,
  stability-reproduced; NULL otherwise, flip axis named.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**RULING: NULL — the registered straddle, reproduced by the stability leg
and by both twin evaluators. Neither "comp fixes it" nor "comp is dead" may
be cited as settled; the per-design signature table below is the pin.**

**(1) C1 = (T1, t=0.10), the FUN-dead sink-firm take, IS rescued — but only
one size deep.** Baseline FUN 0.13457621… (the committed parent value, exact
identity). The comp-shifted exact FUN ladder at C1: σ = 0.02 → 0.1827,
**σ = 0.05 → 0.3069**, σ = 0.10 → 0.4587, σ = 0.20 → 0.8169. Clean
all-four-pass rescues: **D1 σ=0.05 and D2 σ=0.05 only** (SAFE ≤ 0.0376,
SINK 0.0000, determinate, MINT max = −5.0 units exact — the (σ−t)·B₀ line).
The next size up, σ = 0.10 = t, passes all four bands **at the MINT
boundary exactly** (farmer EV = (σ−t)·B₀ = 0, the pre-named mint
knife-edge) — boundary cells cannot join an APPROVE band, so no design
reaches 2 consecutive clean sizes. σ = 0.20 MINTS exactly (+0.10·B₀ per
session via the wash-qualifier/casual player — the pump line measured AND
proven). **APPROVE's condition fails exactly where the proposal pre-named
the race: "whether D1's qualification threads FUN, SINK, and MINT at
(t=0.10, σ ∈ {0.05, 0.10})" — it threads at 0.05 and lands on the knife-edge
at 0.10.**

**(2) C2 = (T2, t=0.05), the SAFE near-miss, is NOT cleanly rescued — its
whole column is censoring-indeterminate.** D1/D2 at σ=0.02 fail SAFE
outright (worst-policy P_wipe 0.0556/0.0518 vs 0.05). D2 σ=0.05 genuinely
closes the SAFE gap (0.0316, from the parent's 0.0608) — but σ = t puts it
ON the mint boundary, and the cell (like every C2 cell) is INDETERMINATE:
the R1-grinder 4,000-round cap-hit fraction sits at 0.0115 at the baseline
(V025's own committed row was 0.0095 — the parent's near-1% censoring
knife-edge re-measured on the other side of the line) and every comp design
lengthens sessions (D1 0.0115 → D3 ρ=0.4 0.0340). Indeterminate routes to
NULL, never to APPROVE or a rescue — registered. D3 ρ ∈ {0.2, 0.4} pass all
four bands there but ride the same indeterminacy; ρ ≥ 0.6 MINT-fails
EXACTLY via the PLAIN CASUAL PLAYER (E[net incl. comp] = +1.05 / +3.07
units at ρ = 0.6/0.8, exact rationals) — the loss rebate mints through
bounded honest play, no optimal stopping needed (the T1 stopper grid's best
EV is −2.68 units at its most favorable cell; on T2's fatter tail the
stopper's measured max reaches +5.02 units at ρ=0.8).

**(3) The per-design signature table (the NULL pin).** Per-axis clean-pass
shares over the 48 cells: design D1 2/16 · D2 2/16 · **D3 4/16**; size
index 1st 4/12 · 2nd 3/12 · 3rd 1/12 · 4th 0/12; take t=0.05 3/24 ·
t=0.10 5/24; shape T1 5/24 · T2 3/24. The 8 clean cells:
`T1|t=0.05|D1|0.02`, `T1|t=0.05|D2|0.02`, `T1|t=0.05|D3|0.2`,
`T1|t=0.1|D1|0.05`, `T1|t=0.1|D2|0.05`, `T2|t=0.1|D3|0.2/0.4/0.6`.
Signatures, measured: **D1 stipend** — the only lever that buys FUN at the
sink-firm take without touching in-session walks; mints exactly above σ = t;
one clean size. **D2 handle rebate** — reference-FUN identical to D1
(exact identity held); the predicted grinder SINK re-arm did NOT materialize
at c = 5 (P_double stayed ≤ 0.10 everywhere — the tight cap tames the
effective-take cut); its real value is SAFE (closes C2's gap at σ = 0.05)
but only ON the mint knife-edge. **D3 loss rebate** — provably cannot move
FUN (identity: all 8 C1 cells FUN-fail at 0.1346); buys SAFE absolutely
(P_wipe ≡ 0 exactly for every ρ ≥ 0.2 — "cashback buys SAFE, never FUN"
measured as registered); mints at ρ ≥ 0.6 through the casual player.
**The unanticipated clean band:** D3 composes with the TIERED shape at the
sink-firm take — (T2, t=0.10, ρ ∈ {0.2, 0.4, 0.6}) is a 3-consecutive-size
clean sweep (baseline T2 FUN 0.2671 already passes; the rebate kills the
0.1778 SAFE wall to exactly 0; SINK ≤ 0.005; MINT ≤ −2.0 units exact;
determinate) — not a target cell, so it cannot flip the ruling, but it is
the grid's strongest composed row and ships as reporting.

**(4) House-net table (attached per the registration).** Incumbent (T1,
t=0.05, no comp): casual 5.0% of B₀ exact (measured 4.86%; parent 5.155%),
worst-policy 25.0%. The C1 rescuers price at: D1/D2 σ=0.05 @ t=0.10 —
casual house-net (t−σ)·B₀ = **5.0% of B₀ EXACT, the same casual price as
the incumbent**, at FUN 0.3069 vs the incumbent's 0.2738, with worst-policy
house-net 45.3%/39.9% (the sink-firm take bites overstakers). The composed
D3 row (T2, t=0.10, ρ=0.2): casual 7.33% exact at FUN 0.2671. A single-size
knife-edge separates "comp dominates the incumbent" from the mint line —
exactly why this is a NULL, not an APPROVE.

**(5) Validity.** Identity gate EXACT (T1 Fractions ≡ V022/V025 committed at
t ∈ {0, 0.05, 0.10}; T2 P_ahead/P_wipe Fractions ≡ V025; uncapped ruin
Fractions and capped-DP floats ≡ V025; t=0 P_double = 1/3 in closed form
AND independent elimination). Agreement gates: **66 pooled probability
points, max deviation 0.8854 pp vs the 1.0 pp band, ZERO breaches** (the
pre-run SE arithmetic priced the stopper points at ~1.6σ and expected
breaches by construction; none realized — the 8× aux protocol stayed idle);
**164 EV gates at 4·SE, all pass**; D2 cap-chaser Wald signs all correct;
every D3 casual leg produced exactly 0 wipes (the exact-zero identity).
**2,668,600 self-checks, 0 failed** in the accepted runs: per-replication
conservation on every session, an independently written twin kernel exact
on 1,664 traced replays, five hand-derived pins with committed derivations
(incl. the D2 cap-exact stop, the D1 qualification-at-exactly-100 edge, the
D3 stranded class, and the stipend-jump double), exact draw-count sentinels
closing at 935,017,192 + 467,352,942 uniforms, twin decision evaluators
agreeing on every band of every cell. Stability leg (seed 20260753, half
M): **NULL reproduced** — same C1 rescue set; C2's D2 σ=0.05 flips between
indeterminate-pass and boundary-pass under half-M noise (both
NULL-support classes; the ruling is class-robust). stdout + results.json
byte-identical across two full process runs by external diff on pinned
cpython-3.11; ~6.8 min per run.

**(6) Reporting-only legs (registered as unable to flip).** t=0 control:
capped MC within 4 SE of the capped DP, uncapped exact 1/3. T3 monotonicity
spot cell: baseline P_double 0.2135 → D1 σ=0.2 0.3180 — comp RAISES
P_double on the jackpot shape as cited; T3's exclusion direction verified.
Compulsive harm context: the D2 rebate PROLONGS compulsive play — median
rounds-to-ruin 1,838 (baseline T1 t=0.05) → 2,560 at σ=0.2, ruin_frac 1.0
in both; D1/D3 compulsive ≡ baseline by identity (end comp cannot alter an
in-session walk). D3 ρ=0.8 grinder sessions end STRANDED (total bankroll
ruin with wealth = ρ·B₀ between the bands) in 97.15% of T1 t=0.05 sessions
— the loss rebate converts the grinder's half-stop into play-to-extinction,
the behavioral cost of the "SAFE" it buys. Aggregated-draw spot check:
agrees within 4 SE (every decision number used per-ticket draws).

## What it did NOT settle

- **Absolute pricing.** All conclusions are bankroll-RELATIVE — nothing
  here prices the casino sink against fishing/mining faucet mint in
  absolute chips/hr; the live earn-rate baseline whose absence V001/V008
  named (and V022/V025 restated) stays walled; the telemetry caveat applies
  verbatim and is restated, not re-attempted.
- **Cross-session comp banking** — out of scope by registration; the
  multi-session mint rate is bounded linearly by the per-session farmer EV
  the MINT band caps.
- **Comp-triggered behavior change** (comp as marketing — session frequency
  and stake appetite) — the declared model basis names the live probe:
  session-frequency telemetry before/after a comp toggle on one game, zero
  new balance sims.
- **The exploit optimum.** The D3 stopper grid is 12 variants, not an
  optimum proof: its max EV is a LOWER bound, so the measured MINT failures
  stand, and any pass at the grid edge would have been marked (none was
  load-bearing).
- **The C2 determinacy question.** Whether (T2, t=0.05) plus a small comp
  line holds all four bands is CENSORED, not answered: the 4,000-round
  grinder cap bites 1.1–3.4% of R1 sessions there (the parent's own 0.95%
  knife-edge, pushed over the line by every comp design). A re-registration
  wanting that cell determinate needs a longer cap or a narrower R1 leg —
  a re-run request is deliberately NOT this verdict.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The pre-registered question is about which (design, size) cells hold the
parents' bands under the pinned i.i.d. ticket-frame family — the same
family both parents priced, extended by a linear per-session comp layer.
The one abstraction that could flip the headline reading (comp-triggered
behavior change) is declared in the model basis with the zero-tooling live
probe named; strategy spread folds into the take as the REALIZED take by
construction. The decisive numbers (FUN ladder, pump line, D3 casual mint,
wipe ≡ 0) are exact arithmetic on the registered model, not sampled
estimates.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. 2,668,600 self-checks, 0 failed, exit-coded; the identity gate ties
the σ=0 baselines to BOTH parents' committed values by exact rational
equality; 66 pooled agreement points (0 breaches, max 0.8854 pp) + 164 4·SE
EV gates against a seedless exact arm; an independently written twin kernel
and twin decision evaluators; five hand-derived pins committed with
derivations before the runner (one expectation corrected after the first
run mis-applied its own affordability arithmetic — disclosed in fixtures,
here, and in the session card; the kernel followed the registered rule).
Every constant, band, seed and the evaluation order registered in the idea
file before any code; the full 48-cell four-band tables ship for both legs
including the cells that cut against every reading (the D1 σ=0.05 rescue
AND its σ=0.10 knife-edge; the D3 clean band at a non-target cell).

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is the robust reading of a genuinely knife-edged grid: the C1
rescue is margin-clean at σ=0.05 (MINT −5.0 units exact, SAFE 1.3 pp under
band) but single-size BY EXACT ARITHMETIC (the σ=0.10 boundary is EV = 0
exactly, not a sampled near-zero — no M increase moves it); C2's
indeterminacy is structural (censoring grows with every comp design); the
stability leg reproduces NULL with the one knife-edge cell flipping between
two NULL-support classes. REJECT was never near (4 clean rescues exist);
APPROVE fails on an exact boundary, not a sampling margin.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic. Pinned
seeds, pinned loop order, one uniform per ticket, counted streams with
exact rejoin sentinels. stdout AND `results.json` byte-identical across TWO
complete process runs by external `diff` on cpython-3.11 (pinned and
asserted). ~6.8 min per run.

**5. "LIMITS? what this evidence does NOT show."**
Bankroll-relative only; per-session comp accounting; finite policy + farmer
sets (bracket, not enumerate); the D3 stopper grid is a lower bound on the
exploit; C2's four-band question is censored, not answered; T3 is excluded
by citation (spot-verified directionally), not re-run; the
0.25/0.05/0.10/0 lines are pre-registered judgments with full curves
shipped so a re-drawn line re-reads, never re-runs.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying quantities are exact where the ruling turns on them
(the FUN ladder, the σ = t boundary, the pump line, the D3 casual mint, the
D3 wipe identity), the MC arm agrees everywhere within the registered gates
with zero breaches, the stability leg reproduces the ruling, and the honest
boundary — one hand-pin expectation corrected for its own arithmetic error
— is disclosed at every layer. NULL is the registered outcome for exactly
this shape: real rescues exist, and every path to APPROVE dies on an exact
knife-edge or a censored cell.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `null` — the pre-registered straddle, finalized (not a re-run
  request).** By the rule committed before any code, evaluated in the
  registered order: REJECT fails (C1 has 4 rescues — 2 clean, 2 boundary);
  APPROVE fails (no design reaches 2 consecutive CLEAN sizes at C1 — the
  band {0.05, 0.10} is broken at σ = t by an exact-zero farmer EV, and
  boundary cells were registered as unable to support APPROVE); everything
  else is NULL with the flip axes named: **the σ = t mint knife-edge** and
  **the design axis** (both pre-named in the proposal), plus C2's
  **censoring axis** (the inherited near-1% grinder cap-hit line).
- **The pin that ships (per-design signature, citable):** *a stipend buys
  FUN at the sink-firm take and mints above σ = t — one clean size exists
  (σ = 0.05 at t = 0.10, house-net 5.0% of B₀ exact, FUN 0.3069 vs the
  incumbent's 0.2738 at 5.2%); a handle rebate is FUN-identical to the
  stipend and closes the tiered shape's SAFE gap only ON the knife-edge; a
  loss rebate buys SAFE absolutely (wipe ≡ 0), never FUN, and mints at
  ρ ≥ 0.6 through the PLAIN CASUAL PLAYER — the classic stopper exploit is
  strictly weaker than just playing bounded and collecting.* Neither "comp
  fixes it" nor "comp is dead" may be cited as settled.
- **For the World seat's consolidation (consequence of NULL, registered):**
  the fairness-lever triage does NOT close with a strike — the incumbent
  row (T1, t=0.05, c=5, no comp) remains the default house-bankable cell;
  the two measured near-rows ride as reporting for the owner's judgment:
  (i) the D1 σ=0.05 @ t=0.10 row (same exact casual price as the incumbent,
  better FUN, single-size — adopting it means accepting a one-step-from-
  mint sizing rule), and (ii) the D3 ρ∈{0.2–0.6} @ (T2, t=0.10) composed
  row (the grid's only multi-size clean band, at a non-target cell, with
  the measured behavioral cost that the rebate converts grinder half-stops
  into play-to-extinction). MINT discipline for ANY adopted comp line:
  σ < t strictly, ρ < 0.6 strictly, qualification thresholds at or above
  the wash line.
- **The reusable art:** the MINT band + farmer family (wash-qualifier,
  cap-chaser, stopper grid) are the importable guard for every future
  economy-lever sim (loyalty points, daily bonuses, season passes) — the
  first grid in this repo to price a faucet, and the measured lesson is
  that the faucet's binding attacker was the HONEST bounded player, not
  the optimizer.
- **Model basis (declared, scope-limiting):** i.i.d. tickets × linear
  per-session comp; the single most-likely-to-flip alternative is
  comp-triggered behavior change (session frequency / stake appetite),
  deliberately the same measurement as the cheapest live probe:
  session-frequency telemetry before/after a comp toggle on one game.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V028 slice boundary, with header timestamps from live
`date -u` at append time. -->
