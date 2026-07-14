# REPORT — VERDICT 062 · chicken-farm faucet self-balance (INTAKE 051 / idea-engine PROPOSAL 051)

**Ruling: REJECT** (pre-registered rules applied in order, REJECT checked FIRST — it fires).
L1 ("Buying hens scales the faucet but each costs more coins (the sink), so the loop
stays self-balancing") fails in the costly direction: the self-funded closed-wallet
collector out-earns the committed daily anchor at 3 of 4 decision cadences, and the
sink stops binding within days at zero further cost forever.

## Headline (Arm A, exact; threshold κ·E[!daily] = 169201/200 = **846.005** coins/day; benchmark E[!daily] = 169201/100 = **1692.01**)

| Δ (cadence) | best-of-family | plateau coins/day (exact) | ×E[!daily] | vs 846.005 | wall day | spend to plateau |
|---|---|---|---|---|---|---|
| 900 (15 min) | GREEDY (PAIR ties) | **8064** | 4.766× | **FIRES** | 3.6875 | 21,887 |
| 3600 (1 h) | PAIR | **6720** | 3.972× | **FIRES** | 4.833 | 22,602 |
| 14400 (4 h) | PAIR | **1320** | 0.780× | **FIRES** | 5.167 | 4,229 |
| 86400 (24 h) | GREEDY | **130** | 0.077× | under | 9.0 | 604 |

REJECT conjuncts, all green: (1) ≥ 2 of 4 cadences over the band — **3 of 4**;
(2) every firing cell confirms in the jittered Arm-S mean (seed 20261341, N = 2,000/cell)
with ≥ 4·SE headroom — 900: mean 6146.31 (headroom 5300.30 vs 4·SE 3.96) · 3600: 5306.08
(4460.08 vs 8.43) · 14400: 1135.62 (**289.61 vs 4.17** — ~278·SE) — jitter and skips cost
income (sub-interval remainder discarded on every collect, merged gaps hit the cap), yet
every firing cell stays far over the band; (3) closed-wallet cumulative spend ≤ 30·E[!daily]
= 50,760.3 at every firing cell (max 22,602 — the runaway is self-funded, the loop's own
coins buy the whole ladder). Stability leg (seed 20261342, N = 500) reproduces REJECT
through BOTH twin evaluators. APPROVE/NULL never reached.

Full 20-cell grid (Arm A plateau / Arm-S mean): GREEDY 8064/6146.3 · 4560/3578.6 ·
1140/910.1 · 130/117.2; PAIR 8064/6145.9 · 6720/5306.1 · 1320/1135.6 · 130/117.0;
HEN_ONLY 3840/2809.1 · 960/799.2 · 240/216.1 · 40/36.0; COOP_ONLY 576/489.9 ·
576/530.8 · 576/468.8 · 130/117.0; ALT 576/489.9 · 576/531.0 · 420/364.8 · 70/62.9
(Δ = 900/3600/14400/86400).

## Mechanism (read off the exact trajectories)

The coupling is cap × cadence, exactly as registered. Below the coop cap a hen's
marginal income is cadence-independent (n·288 eggs/day → 576 coins/day per hen), so the
14-day payback rule admits every hen up to #14 (price 7692 ≤ 576·14 = 8064) at any
cadence that keeps the coop below cap — the "sink" (1.55× price ladder) merely delays
the ladder by ~3.7 days at Δ = 900, it never stops it. The cap only bites the 24 h
idle audience: at Δ = 86400 every hen beyond the starter is worth exactly 0 at every
coop level (F5: 288 ≥ 170 = cap(10)), so the idle player L2 describes plateaus at 130
coins/day (7.7% of a daily) while the 15-min collector mints 4.77 dailies/day forever.
L2 itself is arithmetically exact (F3: exactly 40 coins at t = 6,000 s, nothing more at
7,200 s) — the header's error is not L2 but L1's generalization from it.

- Δ = 900 GREEDY ladder: 13 hens + coops L1–L2, spend 21,887, last buy (hen #14 @7692,
  payback 13.35 d) at day 3.69; plateau 8064/day.
- PAIR's myopia edge is real but reporting-only: joint hen+coop plans extend the wall
  past GREEDY by 3.42 d at Δ = 3600 (plateau 4560 → 6720) and 1.67 d at Δ = 14400
  (1140 → 1320, pulling the 4 h cell over the band); both < 7 d, so the family-split
  axis would not have bound even had REJECT not fired.
- Zero-marginal-hen share at every final state: 0 — the policies never buy a dead hen;
  the deadness shows as the never-bought 2nd hen at Δ = 86400 (F5).

## Reporting legs (seed 20261343 where seeded; never decision-bearing)

- **Extra cadences:** Δ = 300 s best plateau 8064 (identical ceiling — hen ladder,
  cap never binds at n ≤ 20), jittered mean 5439.59; Δ = 604800 (weekly): nothing
  qualifies (coop L1 payback 23.3 d > 14), plateau 40/7 ≈ 5.71/day — the faucet is
  harmless for weekly players, runaway for anyone at ≤ 4 h.
- **κ sweep:** the same 3 cells fire at κ = 1/3 AND κ = 2/3 — margin-thin does not bind;
  the ruling is not knife-edge in the band constant.
- **Jitter widths** (±¼·Δ / ±¾·Δ, N = 500, best policy): 900: 6307.8 / 5958.1;
  3600: 5659.5 / 4959.6; 14400: 1187.2 / 1060.8; 86400: 117.2 / 117.2 — every firing
  cell stays over the band at both widths (self-checked).
- **P_max sweep** (Arm A): P_max = 7 → GREEDY plateaus 6336 / 4560 / 1140 / 100 (still
  2 firing cells at best-of-family); P_max = 28 → 8640 / 4560 / 1140 / 160, spend at
  900 grows to 33,810. Wall day non-decreasing in P_max at every cell (theorem, green).
- **WHALE** (unbounded wallet): same final states and plateaus as closed-wallet in
  every cell, wall at the FIRST check-in — affordability only delays the ladder
  (~days), the payback rule alone sets the plateau. Closed ≤ WHALE holds with equality.
- **Knob table** (the two header knobs the docstring calls tunable): EGG_VALUE 2 → 1
  halves everything (best-of-family 3456 / 2592 / 570 / 50 — the 4 h cell drops under
  the band, the firing count falls to 2 of 4, still a REJECT count); LAY_INTERVAL
  300 → 600 still fires 3 of 4 (best 2112 / 3456 / 1320 / 130) — neither single knob
  alone seals the ≤ 1 h collector; a cooldown or a retune sized off this table is needed.
- **Design ceiling** R(100, 10, Δ) = 32,640 / 8,160 / 2,040 / 340 exactly as registered.

## Gates — all green (35 self-checks, 0 failed, exit 0)

F1 price tables re-derived from the committed float formulas under CPython 3.11
(banker's round) == fixture, coop ladder total 44,506 · F2 settle idempotence +
settling-every-second ≡ settling-once + cap clamp + zero-hen clock + remainder
preservation on the pinned grid · F3 L2 arithmetic exact (40 coins @ 6,000 s, 0 more
@ 7,200 s) · F4 E[!daily] = 169201/100 by exact Fraction · F5 2nd-hen marginal ≡ 0 at
Δ = 86400 for EVERY coop level 0..10 · F6 hand trajectory (Δ = 3600 GREEDY check-ins
1–5: eggs {12,12,20,20,20}, coins {24,24,40,40,40}, buys {—, hen@40, —, —, coop@100},
wallet {24,8,48,88,28}) exact · monotonicity theorems (R in n and L; plateau along the
divisor chain 86400→14400→3600→900 at every final state; wall non-decreasing in P_max;
closed ≤ WHALE) · Arm-S degenerate jitter ≡ Arm A EVENT-FOR-EVENT on all 20 decision
cells with zero rng draws · draw sentinels exact (headline 228,644,714 = 2 × 114,322,357
attempts; stability 57,160,786; reporting 48,796,580 = 2 × 24,398,290) · aux seed
20261344 constructed, never read (getstate identity) · twin independently-written
evaluators agree on class and firing cells, headline and stability · two in-process
Arm-A grid computations identical.

## Reproducibility

One command: `python3 farm_faucet_sim.py` (stdlib only, reads only fixtures.json,
no flags, no wall-clock in any output). Byte identity across two full process runs by
external sha256 —
`run-stdout.txt` `7c3f182cc54f734b8c7acada89ca4744a33fc8767d6c2da7d22f115a2cfb3e9d`,
`results.json` `fc7608e57d00e57daf5cb4f216a7342b595579c4492790dafec477e885b83cab`
(identical both runs). CPython 3.11 pinned and asserted (built under 3.11.15).
Seeds 20261341–344, strictly above the P050/V061 high-water 20261340 — new registry
high-water 20261344.

## Drafter comparison (reported, never gated)

The drafter's disclosed expected landing is reproduced EXACTLY from scratch: GREEDY
plateaus 8064 / 4560 / 1140 / 130, walls 3.69 / 1.42 / 3.50 / 9.0 days, the Δ = 900
ladder self-funding exactly 21,887 coins, myopic stop n = 8 / L = 5 at Δ = 3600 —
no drafter arithmetic error found. (This session's own first hand-sketch of the hen
ladder mis-indexed the price table — hen #14 costs 7692, `chicken_price(13)`, not
11923 — caught by the from-scratch run agreeing with the drafter; a reminder the
committed formula, not a hand-copied table walk, is the source of truth.)

## Anomalies

None material. Disclosed pins beyond the registration (all in fixtures.json
`pinned_interpretations`, chosen before the first run): the PAIR plan-set/tie-break,
ALT permanent-halt semantics, the wall-day definition (payback-walled, affordability
ignored), the Arm-S gap draw map `lo + int(r·span)` (uniform to < 1e-12 quantization,
disclosed in lieu of randint for loop economy), two draws per attempted check-in
including the terminal overshoot, reporting-leg N = 500 (fixture choice, V060
control-N precedent), and the Arm-S confirmation riding the Arm-A best-of-family
policy per cadence.

## Boundaries (as registered)

Cadence-model boundary: no live collect-cadence datapoint exists anywhere in the
fleet — Δ is a grid axis bracketed by the jitter/skip/width legs, never a claim; the
committed `farm:collect` audit rows are the named free measurement. Closed-wallet
boundary: outside coins only accelerate the ladder (WHALE leg: same plateaus, faster) —
generous to APPROVE, so REJECT is robust in the direction that matters. Bounded-policy
boundary: the family brackets real play from below; a cleverer buyer only raises the
plateau (PAIR is in the family precisely to shrink the myopia gap, and it did — it
pulled the 4 h cell over the band). Write-semantics boundary: the model pins the
committed collect/buy stamping @ affd7ea; a future workflow change re-runs, never
reuses. Scope: coins only — collect_eggs XP, multi-guild farms, and the
offline-summary UX are out of registered scope. Streak-weighted !daily only raises
the anchor, weakening the measured ratios — direction favors APPROVE, REJECT robust.
