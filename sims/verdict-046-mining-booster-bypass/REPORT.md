# VERDICT 046 — mining booster bypass: can a committed-shape cap make the energy throttle bind again?

> **Ruling:** `null` — the pre-registered "anything else" arm, landed as a
> finalized verdict per the registration: exactly ONE decision cell (C = 60)
> passes all three bands, in BOTH window semantics; the APPROVE bar (≥ 2 cells
> within one semantics — the P031 two-consecutive-cells rule) is not met and
> REJECT does not fire. Stability-reproduced; twin evaluators agree.
>
> Intake: **035** (idea-engine PROPOSAL 035, PR #308; claim PR #310) ·
> Engine pin: `superbot-games @ 57f69be3` (V042's committed subtree,
> byte-reused) · Anchors: `sims/verdict-042-mining-economy/{results,fixtures}.json`
> + V043's 755/56 hand-pin, machine-read · Seeds 20261281–84 · cpython-3.11.

## The question (registered)

V042 ratified every mining constant but measured, reporting-only, that
boosters convert coins → energy at 4/5 coins per dig — below E[coins/dig] at
every committed row (32/7 · 848/175 · 2703/440 · 8427/1150 · ceiling 755/56)
— so boosted active play nets 270252/23 ≈ 11,750 coins/h at P3 vs 303372/115
≈ 2,638 throttled: a ×4.45 (37535/8427) profitable bypass of the lane's only
pacing control. This head prices the committed-shape seal menu: admission cap
C ∈ {60, 75, 100, 125} effective energy per window × {sliding-3600 s,
fixed-hour}, bands SEAL (best-policy boosted mean net coins/h ≤ 5/4 × the
measured throttled control at EVERY row), REFILL (a full-bar emergency refill
per window, ≤ 2880/7 coins), PACE (boosted NP-1 Forge times ≥ 0.8 × the
parent's committed throttled anchors). REPRICE was excluded by registered
arithmetic (seal needs e ≥ 11325/896 ≈ 12.64; refill affordability needs
e ≤ 48/7 ≈ 6.86) and rides reporting-only. Decision rule, registered order:
REJECT (no cell passes) → APPROVE (≥ 2 cells within one semantics) → NULL.

## Validity

B0 (37 anchors, all exact, BEFORE any lever cell): MANIFEST sha256 13/13;
every depth-row fraction re-derived through the engine; 4/5 both items;
7507/1150; 270252/23; bypass ratios 37535/8427 and 38455/8427; Forge anchors
1005258865/2292144 digs / 4476179765/1146072 s and 3554578865/2292144 /
17222779765/1146072 (the parent's own 10D−480 accounting reproduced exactly);
REPRICE exclusion pair; committed refill = 60 coins; fishing max 40797/4000 <
755/56. Gates: C=0 ≡ throttled control (2939 digs/8 h, byte-equal); C=∞ ≡ the
bypass anchor (14389 digs/8 h = 1800/h minus the registered terminal
absorption — the adversary buys only what the horizon can dig; admitted
11450 = digs − control exactly, both semantics identical); farmer dig
identity (delta 0 at C mod 25 = 0; delta ≤ 8 cap-touches at C=60, band
registered pre-run); admitted = 8C on every decision cell; independent
sliding-window re-audit ≤ C on every sliding cell; drink-mix invariance
(three mixes: identical digs/admitted/spend); affordability exact at the P0
floor; Arm-A fluid agreement ≤ 180 s on all 16 ladder runs; twin
independently-written decision evaluators (Fraction vs float) agree on main
AND stability; MC (M = 400 main / 200 stability / N = 200k per row) max rel
err 0.003 vs the 0.01 familywise-pre-checked gate over 13+ points; stdout +
results.json byte-identical across two full process runs; **110 self-checks,
0 failed, exit 0**.

Fix-forward disclosure (all pipeline, none post-hoc band-fitting): after the
first run, three runner defects were fixed and the run re-accepted — (1) the
greedy adversary lacked the hold-to-top-up move (sliding C=60 admitted only
410; holding regen-bound digs to buy the 10-unit residual is strictly
dominant and matches the registered "a greedy adversary can exhaust any C"),
(2) the C=∞ gate as first written contradicted the fixture's own registered
terminal-absorption rule (14389 is correct adversary behaviour, band
[14380, 14400] adopted and disclosed), (3) the Arm-A fluid predictor gained
the purchase-cascade model (rations land at cur 34 every 62.5 s from t = 65).
The measured physics never changed; the decision table is identical before
and after except C=60-sliding's admitted 410 → 480 (which moves that cell
AWAY from the ruling's fragile direction).

## The decision table (ceiling row 755/56 = the binding row)

| cell | ρ mean (measured) | ρ closed form | SEAL | REFILL | PACE FI | PACE FII | all three |
|---|---|---|---|---|---|---|---|
| sliding C=60 | **1.1512** | 1.1568 | P | P (60 coins) | **0.8193** | 0.8331 | **PASS** |
| sliding C=75 | 1.1920 | 1.1960 | P | P | **0.7789 F** | 0.7927 F | fail |
| sliding C=100 | 1.2560 **F** | 1.2613 | F | P | 0.7149 F | 0.7371 F | fail |
| sliding C=125 | 1.3201 **F** | 1.3266 | F | P | 0.6508 F | 0.7271 F | fail |
| fixed C=60 | **1.1498** | 1.1568 | P | P | **0.8193** | 0.8339 | **PASS** |
| fixed C=75 | 1.1920 | 1.1960 | P | P | 0.7789 F | 0.7927 F | fail |
| fixed C=100 | 1.2560 **F** | 1.2613 | F | P | 0.7149 F | 0.7336 F | fail |
| fixed C=125 | 1.3201 **F** | 1.3266 | F | P | 0.6508 F | 0.7236 F | fail |

Exact fractions in results.json (e.g. sliding C=60 ceiling ρ =
510893/443789; C=100 fixed = 557421/443789 — 1.2560 > 5/4, a 0.006 knife-edge
FAIL at the ceiling row while its P3 row passes at 1.2423, exactly the
drafting table's shape). SEAL on means shows a small NEGATIVE engine premium
(−0.004 to −0.007): the closed form denominates at 360/h while both arms
share the measured full-bar burst (control 2939 digs/8 h, not 2880).

## The finding: the engine premium lives on the LADDER, and it kills C=75

The registered APPROVE expectation — sliding {60, 75} by the sustained-rate
closed form, 0.054 SEAL margin — did NOT survive the measured ladder
front-load premium: a greedy climber consumes each window's whole cap
immediately, so a short goal (Forge I ≈ 439 digs, barely one window) sees
boost density far above the sustained rate. Measured Forge I boosted time at
C=75: 3042 s = 0.7789 × the parent's throttled anchor vs the sustained-rate
prediction 0.8329 — a **−5.4 pp premium**; Forge II 0.7927 vs 0.8290
(−3.6 pp). Both semantics identical (ladder timelines equal at C=75; FI equal
at 0.8193 for C=60). C=60 survives because one bar-quantum per window is
front-loadable only 60 digs' worth: FI 0.8193, FII 0.8331/0.8339 ≥ 0.8.

Semantics fork, measured: **inert on every mean** (equal totals 8C, equal
spends, near-equal digs) — the expected "fixed-hour gaming premium" on means
is zero — but **live on the worst-window audit**: fixed-hour admits 2C = 120
in a trailing hour at C=60 (peak-window ρ at the ceiling 1.3136 > 5/4), and
C + 60 at higher C (125/150/175 measured — the 60-energy bar caps any
instantaneous burst below the naive 2C bound); sliding is audited ≤ C
everywhere. If the seat wants the throttle to bind as a *window rate* (its
original semantics), only sliding qualifies; on horizon means both do.

## Reporting legs (cannot flip; did not)

- **REPRICE realized its registered exclusion**: e = 11325/896 seals every
  row (ceiling ρ 1.2435, no purchases anywhere else) but prices the refill at
  169875/224 ≈ 758 coins (> 2880/7 ≈ 411); e = 48/7 keeps the refill exactly
  at the bar (2880/7) but leaves P3 at 1.2502 (> 5/4) and the ceiling at
  2.9144; e = 32/7 seals only P0 (indifference, strict-profit rule); e = 2 is
  a ×3.2–4.3 bypass. Committed-granularity refill (75e nominal) ships as its
  own column. No price-only cell passes both bands — measured, as registered.
- **HYBRID** (C=75 sliding, e=2): ρ ceiling 1.1739 — the cap does the work,
  the reprice adds nothing decision-relevant; PACE still fails via C=75.
- **HONEST-CASUAL immunity**: 2392 digs across 8 × 30-min sessions, 16 refill
  purchases (480 coins) — byte-identical at EVERY decision cell and uncapped:
  the cap taxes only the farmer; the booster's convenience purpose survives
  every cell (REFILL band passes 8/8).
- **Boundary gamer** (fixed-hour, deliberate window-edge bursts): peaks
  120/125/150/175 at C = 60/75/100/125 — the measured fixed-hour premium is a
  worst-window phenomenon bounded by C + 60, not a mean phenomenon.

## Ruling and consequence (pre-registered NULL arm)

REJECT does not fire (C=60 passes, both semantics, stability-reproduced).
APPROVE does not fire (no semantics carries 2 passing cells). **NULL**, with
the conditional rule as the citable finding:

> A committed-shape booster-admission cap seals the mining sink ONLY at
> C = 60 — the exact full-bar quantum — and does so in both window semantics
> (sliding additionally holds the seal in every trailing window; fixed-hour
> leaks 2C bursts). Every looser committed-shape cell fails the ratified
> goal-ladder pacing under front-loaded purchasing, a −5.4 pp engine premium
> no sustained-rate arithmetic predicts.

The registration's two-cells rule exists precisely so a single measured point
cannot buy a shipped constant. What the seat gets: (a) the full priced menu
(this table) for the intent call V042 left open — "possibly intended per the
shop's own comment" restated verbatim, the seat's/owner's decision, never
ruled here; (b) the one passing cell C=60 with its exact margins, if the
seat wants a seal today; (c) the re-drawn-line option: at PACE ≥ 0.775 the
{60, 75} band passes in both semantics — full tables ship so a re-drawn line
re-reads, never re-runs (the parent's own rule); (d) the named cheapest LIVE
probe before committing any cell: **shop telemetry** (booster purchases per
player-hour + purchase-time energy level), locating the real purchase and
waste rates at zero new tooling; (e) the rescue family if a real seal-with-
headroom is wanted: diminishing restore / boost-fatigue — a mechanism change,
out of this head's registered scope, its own future sim.

## Boundaries (registered)

Intent is priced, not ruled. INT-1 = 2 s is V042's registered assumption —
and the cap family is INT-1-robust where the bypass numbers are not: once C
binds, sustained digs/h = 360 + C at any interaction floor. The adversary is
greedy-registered, not exhaustive; the sliding-window re-audit and the exact
identities (admitted = 8C, digs = control + admitted) bound extraction, and
the boundary-gamer leg lower-bounds fixed-hour gaming. Booster coin spend's
extra dig need was ignored in the ladder legs — conservative against APPROVE,
disclosed. Fun/retention, multiplayer/trade, the amount-inert pickaxe flag
(V042's other row, named runner-up), and cross-session cap persistence (host
territory, V044 precedent) are out of scope. Fishing rows ride reporting-only
by arithmetic (max 40797/4000 < 755/56).
