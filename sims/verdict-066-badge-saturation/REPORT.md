# REPORT — VERDICT 066: badge saturation — Coin Magnate vs the committed daily faucet (PROPOSAL 055)

**Ruling: REJECT** ("age badge — the catalog's own discrimination claim
fails against the hub's committed faucet; the sample calibration is dead
on arrival"). Checked FIRST per the pre-registered order; fires on ALL
THREE conjuncts on Arm A's exact Fractions at the decision world σ = 1/2:
P(T ≤ 90) ≥ 19/20 at **3 of 4** claim-rate cells (p = 1: exactly 1;
p = 1/2: 1 − ε, float 1.000000; p = 1/4: 0.986615; only p = 1/10 at
0.205567 stays out), median T = **7 days ≤ 14** at the full-engagement
(p = 1, σ = 0) cell, and **every firing cell confirms in Arm S** (worst
|dev| 0.000265 ≤ 1/100; worst finite headroom 44.7·SE ≥ 4·SE). The
stability leg (seed 20261358) reproduces REJECT through both twin
evaluators. APPROVE/NULL not reached.

## Registration

Source: `## PROPOSAL 055 · 2026-07-14T02:25:10Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main
`18f31718b20cb1c5f3fad6cb2767babe124c691a`, landed via idea-engine PR
#385; idea doc
`ideas/superbot-mineverse/badge-saturation-coin-magnate-2026-07-14.md` @
the same HEAD — the outbox `idea:` line's blob pin `4df5043…` is a
pre-squash branch commit, anomaly A2 below). Source pins, both firsthand
at drafting: superbot-mineverse
`b983291cd9fc4b0d037a25a139c7ef5991e1236f` (badge rule + both calibration
comments + shared-wallet contract + 7-miner sample), superbot
`34775943da081dd0a1dc7cf858efc0889726fcf6` (`_DAILY_TIERS`,
`_DAILY_COOLDOWN = 86400`). Every fixture constant was copied verbatim
into `fixtures.json` and committed BEFORE the runner; zero repo/network
reads at verdict time (the runner reads only its own fixtures.json).

## Model (registered)

Committed: badge rule `coins >= 10_000`; wallet integer ≥ 0, "mutated
only by `economy_service`"; faucet pmf = six integer-uniform tiers,
weights {45, 25, 15, 8, 5, 2}/100, per-value numerators over 10^5
{90, 25, 15, 8, 5, atom 2000} (exact; see anomaly A1), E[!daily] =
169201/100 exact, SD ≈ 1197.78 (exact Var 14346764899/10000); threshold
= 1000000/169201 = **5.9101 expected dailies**. Invented-but-pinned:
fresh wallet 0; per day claim w.p. p then spend floor(σ·claim) same day;
T = first day wallet ≥ 10,000; H = 90; grid p ∈ {1, 1/2, 1/4, 1/10} ×
σ ∈ {0, 1/2, 9/10}, decision world σ = 1/2; σ worlds and H ∈ {30, 180}
reporting-only; non-daily faucets excluded (understates income —
REJECT-robust, direction stated).

## The decision numbers (Arm A exact, alone decision-bearing; σ = 1/2)

| p | P(T ≤ 30) | P(T ≤ 90) | P(T ≤ 180) | median T | fires ≥ 19/20 |
|---|---|---|---|---|---|
| 1 | 1.000000 | **1 exactly** | 1 | 12 | YES |
| 1/2 | 0.788551 | **1 − ε (1.000000)** | 1.000000 | 25 | YES |
| 1/4 | 0.089402 | **0.986615** | 1.000000 | 49 | YES |
| 1/10 | 0.000792 | **0.205567** | 0.897998 | 122 | no |

Full-engagement (p = 1, σ = 0): median T = **7**, E[T] = 6.660268,
Var[T] = 3.075239, CV[T] = **0.2633** (exact rationals in results.json) —
crossing times concentrate in the badge's first week: the age-badge mark.
Exact decision Fractions committed in results.json (denominators
(2·10^6)^90; e.g. the p = 1/2 cell is 1 − ε with a 182-digit
denominator — strictly below 1, float 1.000000).

σ worlds (reporting-only, exact): σ = 0 → 1 / 1 / 0.999949 / 0.801463
(even the once-in-ten-days claimer crosses w.p. 0.80 in a season at zero
spend); σ = 9/10 → 1.000000 / 0.022956 / 0.000000 (< 10⁻⁶) / 0.000000 —
the registered flip confirmed exactly: in the deep-spend world only
p = 1 fires. The decision rides the pinned σ = 1/2; σ is the named
fragility axis (no live spend datapoint exists — the pre-priced live
probe: one day of the snapshot feed's own 60 s re-renders).

## C* threshold menu (exact minimal C with P(T ≤ 90) ≤ 1/2) + re-expression

| p | C* | C*/E[!daily] | P90 @ 20,000 | @ 50,000 | @ 100,000 |
|---|---|---|---|---|---|
| 1 | 76,043 | 44.9 | 1.000000 | 1.000000 | 0.000044 |
| 1/2 | 37,916 | 22.4 | 0.999809 | 0.022093 | 0.000000 |
| 1/4 | 18,823 | 11.1 | 0.397892 | 0.000000 | 0.000000 |
| 1/10 | 7,362 | 4.4 | 0.000417 | 0.000000 | 0.000000 |

A one-line constant swap to C = 20,000 already restores discrimination
at the p = 1/4 archetype (share 0.398); C ≈ 38,000 makes the badge a
median-season mark for the every-other-day claimer. Computed from the
exact day-90 wallet law (binomial-mixture machinery, asserted equal to
the absorbing arm at C = 10,000 on every cell — exact Fraction equality).

## Arm S / stability / reporting

Arm S (seed 20261357, N = 20,000/cell): est 1.000000 / 1.000000 /
0.986350 / 0.208150; every decision cell within 1/100 absolute (worst
0.002583, non-firing cell); firing-cell headroom above 19/20: ∞ (SE = 0,
exact 1) / 4.2·10⁵·SE / 44.7·SE — all ≥ 4·SE. Draw sentinels exact:
7,200,000 Bernoulli (= N·90·4), 3,330,986 value draws (= claim events;
value ≡ Bernoulli on p = 1). Stability (seed 20261358, N = 10,000):
class REJECT through both twin evaluators — REPRODUCES. Reporting MC
(seed 20261359, N = 10,000): all 8 σ-world cells within 0.0022 of exact.
RNGs constructed in pinned order 20261357 → 20261358 → 20261359 and
nothing else; aux seed 20261360 never constructed, never read. New
registry high-water 20261360 (reserved by the registration).

## Gates (all green; run invalid on any failure)

- **F1 anchor:** E = 169201/100 exact; weights sum 100; per-value
  numerator table re-derived and asserted (see A1).
- **F2 identities:** P(T ≤ 1) = 0, P(T ≤ 2) = 1/2500 exactly (the
  two-Mythic path), P(T ≤ 20) = 1 exactly at (1, 0); P(T ≤ 3) = 0 at
  σ = 1/2 on all four p cells.
- **F3 sample calibration:** `earned_achievements` re-implemented
  verbatim over the 7 fixture miners reproduces every hit list exactly —
  Coin Magnate {DeepDelver, MagmaMaven}, Packrat {SilverSeeker,
  CavernCrawler}, Tool Breaker {RustyRelic}, Balanced Build
  {SilverSeeker}, The Answer {DeepDelver}, Fully Geared {GearGoblin},
  Deep Diver {DeepDelver, MagmaMaven}; pack totals, wear maxima, the
  42-stone row, record_depth-vs-max_depth all asserted.
- **F4 monotonicity:** P(T ≤ n) non-decreasing in n (every cell, every
  day) and in p; non-increasing in σ and in C; median T non-increasing
  in p — all exact.
- **F5 degenerate transform:** σ = 0 net pmf ≡ committed pmf
  identically; DP mass + absorbed = 1 exactly every day of every cell.
- **Mechanical:** draw-count sentinels exact; twin independently-written
  decision evaluators agree (headline AND stability); cpython-3.11
  pinned and asserted; aux seed never read; `SELF-CHECKS: 166 passed,
  0 failed`, exit 0, ~1m41s/run.

**Byte identity (external sha256, two full process runs):**
`run-stdout.txt` =
`d11c2530b7969a0b90a3fc3e33d2371f8aa3c1f7f174c9b431b0fcf433c78e45`,
`results.json` =
`3a037d0d99989bc365b9c8253d238fd0bfc3e69f686f095129183e73c9ddbf3d` —
identical hashes on both runs; no wall-clock in any output. No
fix-forwards — the first complete run of the registered pipeline is the
accepted run.

## Drafter-reference comparison (never gated)

Every disclosed drafting-time value reproduces from scratch EXACTLY at
6-decimal precision: σ = 1/2 row 1.000000 / 1.000000 / 0.986615 /
0.205567; σ = 9/10 row 1.000000 / 0.022956 / 0.000000 / 0.000000;
full-engagement median 7; (1, σ = 1/2) median 12. No drafter arithmetic
error found in any decision-bearing number.

## Anomalies (first-class)

- **A1 (registration transcription):** the PROPOSAL 055 block and idea
  doc write the per-value probability table as "{9, 25, 15, 8, 5}/10^5
  per ranged value"; the Common row is a denominator slip — Common spans
  500 values, so its exact per-value probability is 9/10^4 (= 90/10^5).
  9/10^5 would leave total pmf mass 0.595, contradicting the same
  registration's own "weights sum 100" and E = 169201/100 exact. The
  committed source table is unambiguous; asserted both ways in F1.
  Reporting-side only; decision unaffected.
- **A2 (pin hygiene):** the outbox `idea:` line pins blob commit
  `4df5043249e86f250114394a6223c47bdcf9edaa` — a pre-squash branch
  commit absent from idea-engine main history (PR #385 squashed to
  18f3171). The HEAD copy was verified constant-identical to the outbox
  block and is authoritative.
- **A3 (source disclosure):** superbot's `_daily_weights(streak)` shifts
  weight from Common/Uncommon toward higher tiers as streak grows
  (luck = min(streak, 60), shift = 0.25/day). The registered model rides
  the BASE weights — the streak-0 floor. Direction stated by the
  registration itself: streaks concentrate T further (the age-badge
  direction), so this REJECT is robust to the disclosed mechanic.

## Boundaries (application guard, carried from the registration)

The verdict conditions on the pinned σ = 1/2 spend world (the σ = 9/10
flip is disclosed above — a deep-spend guild keeps the badge
discriminating; the live probe is pre-priced: one day of the snapshot
feed's 60 s re-renders yields the guild's real coins distribution at
zero new tooling); on daily-only income (understates — every excluded
faucet only accelerates T; V062 measured the farm alone at up to 4.77
dailies/day; REJECT-robust); and on i.i.d. Bernoulli claims (streaks
concentrate T further — A3). Scope: Coin Magnate is the decision badge
(the only one wired to a committed absolute faucet); Packrat's ore
faucet is mining-module-owned, out of scope, named; the other six badges
ride as exact static rows. A future catalog retune, a wallet cap, or a
measured spend distribution means re-run, never reuse.

## Validity gate (five questions)

- **COMPARABLE TO LIVE?** Every decision number is an exact Fraction
  under the registration's own pinned frame; every game constant is
  committed source, quoted verbatim at the pins; the only invented
  widths (p, σ, H, bands) are grid axes or disclosed pins.
- **UNCORRUPTED?** Fixtures committed BEFORE the runner (git trail on PR
  #124: born-red card → fixtures → runner + accepted run); bands, grid,
  seeds, draw order, evaluation order all registered in PROPOSAL 055
  before this session existed; 166 self-checks, 0 failed; no
  fix-forwards; the drafter's disclosed landing re-derived from scratch
  with zero trust and the comparison reported, never gated.
- **ROBUST?** Nothing knife-edge on the ruling: the p = 1 and p = 1/2
  cells sit at/next to probability 1 (headroom above 19/20 = 0.05 with
  SE 0 and 1.2·10⁻⁷), p = 1/4 clears the band by 0.0366 ≈ 45·SE, the
  median conjunct clears by half its band (7 vs 14), REJECT needs 3
  firing cells and has exactly its 3 with the fourth cell 0.74 BELOW the
  band (the surviving discriminator, reported as a finding); stability
  reproduces through both twin evaluators. The named fragility axis (σ)
  is a reported flip, not a smoothed edge.
- **REPRODUCIBLE?** One command, no flags, stdlib-only, hermetic; Arm A
  platform-independent exact rationals, alone decision-bearing; stdout +
  results.json byte-identical across two full process runs by external
  sha256 (hashes above); cpython-3.11 pinned and asserted; seeds
  20261357–360 strictly above the P054 high-water 20261356.
- **LIMITS?** Model-true under the registered frame, not a live
  measurement — the σ pin, daily-only income, and i.i.d. claims are the
  three stated directions (two REJECT-robust, one disclosed flip); the
  4·SE gate half is float by disclosure on a ruling with ≥ 45·SE
  margins; live wallet evidence supersedes wherever a future measured
  frame disagrees.
