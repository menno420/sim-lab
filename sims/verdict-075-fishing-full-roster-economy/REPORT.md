# VERDICT 075 — fishing full-roster sell/XP curve — REPORT

> **Status:** `complete`
> Source: superbot-games `## SIM-REQUEST · fishing-full-roster-economy · 2026-07-13` (filed 2026-07-13T22:06:03Z, games PR #92 commit `21937f3`), read at packet pin `ed2fabbef58f3b97a03e6586a4e03ad0ab89c451`, status `open`.
> Ruling: **NULL — band-straddle (needs-reframing)**, with two theorem-grade findings and a named three-way fork.

## 1. What was asked

Pin sell values (a) and per-catch XP (b) for the 29 not-yet-pinned legacy fishing
species — 18 shore + 11 deepwater, ranks quoted verbatim from the request — "on
the same curve family V043 pinned" (minnow 8 · bass 13 · pike 27 · legend_carp
80), including where the deepwater venue premium should sit, plus the
`xp_to_next`/milestone consequence of a 21-rank table. Cook-leg asks folded into
sibling VERDICT 076 per the request's own fold-in clause.

## 2. Method

V043/V044 packet discipline: 16-file byte-copied import closure at the pin
(sha256 `MANIFEST.sha256`, re-verified before import), driven ONLY through the
packet's own `resolve_cast` + `catch_sim.run()`; species table swapped as DATA
(the packet's documented growth surface); registration committed BEFORE the
runner (one pre-runner amendment, § 3); eval seeds 20261389–20261488, stability
20261489–20261508, all above fleet high-water 20261388; CPython 3.11 asserted;
double run byte-identical — sha256 `run-stdout.txt`
`8002bf2a21936d6d8e29a7614fd076982fa88fcf286e4d5c8312371508a9c51f`,
`results.json`
`b9388721832d4f5d1d3001e7e95b58bd001e9afc05f0abbe47311ebe7cc91a05`.

**B0 (all green):** every committed constant exact (sell curve, XP curve,
catch/bite constants, energy engine incl. the flat `"cooked fish": 30`, market
ration 20 / drink 40, cooked-fish item non-sellable, spot profiles); the V043
family identity `sell == round(8·50/rarity_weight)` reproduced on all four rows;
the packet harness at its own defaults reproduced every published V043 §5 anchor
EXACTLY (dock-fresh bite 54.36%, fresh bites 10,483/8,697/7,539, dock-fresh
shares 49.66/29.90/15.01/5.44, aggregate 55.66/63.70/79.86, mean energy 2).

**Naming leg (mechanical):** the supersede reading (legend_carp = legacy carp,
rank 10, verbatim 80) breaks even WEAK monotonicity against pinned pike 27 at
rank 11 → **DISTINCT**. Carp stays; all 29 rows stand; legend_carp placed at
shore rank 22 (strict apex). This answers the request's "state which reading" ask.

## 3. Finding F-STRICT (theorem, registration-time)

Strict integer monotonicity (V043's A5) is IMPOSSIBLE on the unified 21-rank
shore scale given the verbatim pins: minnow = 8 at rank 1 and bass = 13 at rank
9 leave SEVEN intermediate ranks (2–8) but only FOUR intermediate integers
(9–12). No weight assignment can fix this — arithmetic, not tuning. A5' was
re-registered weakly-increasing pre-runner (amendment in `fixtures.json`, its
own commit, before any run).

## 4. The sweep and the pincer finding

Grid: k ∈ {0.85…1.20} (new-species weight scale) × δ ∈ {0.4, 0.6, 0.8, 1.0}
(deepwater rarity discount = venue premium 1/δ); weight law = piecewise
log-linear through the committed anchors (1,50)(9,30)(11,15)(22,5); sell =
round(400/w), the V043 family at c = 8 verbatim; pinned 4 never rescaled.

**Finding F-PINCER: exactly ONE k-column is eligible.** At k ≤ 1.05 the parity
anchor breaks high (fresh@dock W1 4.85–5.83 > 4.8 = 1.05·32/7); at k ≥ 1.15 the
guppy floor breaks (round(400/(k·46.9)) = 7 < minnow's pinned 8 — weak
monotonicity fails). Only k = 1.1 threads both (parity 4.747, margin 1.1%;
guppy = 8, a tie at the floor; 5 adjacent shore ties total). Eligible cells:
k = 1.1 × all four δ. Selector S1 (min δ = max premium) picked (k 1.1, δ 0.4):
eval max coins/energy 13.411 vs ceiling 755/56 ≈ 13.482 (margin 0.5%), median
deep premium 2.5×.

**Stability leg (20 fresh seeds) broke both bands** — the registered NULL axis:
parity 4.929 (+2.7% past the 4.8 edge) and max coins/energy 14.014 (+3.9% past
the ceiling). The decision-leg margins (1.1%, 0.5%) are SMALLER than seed-batch
noise at n=20; and the A1' break is δ-independent (the k = 1.1 column itself
straddles the band edge). The family + band are mutually near-exclusive at
N = 33: equal-contribution (each species contributes ≈ 400 weight·coins)
forces E[sell|catch] ≈ 400·N/Σw upward as the roster grows, while the guppy
integer floor caps how common the new tail can be made.

## 5. XP arm (reported; conditional on the sell frame resolving)

Mapping `game_xp = size_rank` CONFIRMED on the unified/own scales; the 21-rank
table breaks V043's pacing bands at the committed ladder: L25 in 10.9 h (s=1,
band [24,120]). Ladder rescale s = 3 (`xp_to_next(L) = 150·L`) is the smallest
passing cell: two-burst fresh@dock XP 247.5 ≥ 150 (P1'), gear gradient strict at
every spot (P2'), L25 at 32.7 h sustained master@deep (P3'; stability 33.2 h).
Consequence named: adopting the unified scale re-prices per-catch XP for
bass (2→9), pike (3→11), legend_carp (4→22) and re-sizes reported catches
(`size_rank·12` cm base) — the seam should land ladder ×3 with the roster, or
V043's pacing contract breaks 2.2×.

## 6. Boat-gate finding (W2, reporting)

With deepwater rows reachable ungated, the TOP faucet cell is
**tide_pool/master 13.41 coins/energy** — the calm shallows become the richest
water because rare deepwater rows leak into every spot at base weights (venue
logic inverted). The boat/venue gate is LOAD-BEARING for any roster landing:
deepwater rows must be venue-gated, and since the packet's own bias-never-gate
rule forbids zero multipliers, the gate belongs at the action/venue layer
(e.g. a boat requirement on deep venues).

## 7. Ruling and the fork

**NULL (band-straddle)** per the registered C9 axis. The candidate table
(`results.json.published_table`, 33 rows, k 1.1/δ 0.4) is published
**NOT-PINNED — wire nothing**. The smallest reframings, each sufficient alone:

1. **Re-center the parity band** to admit fresh@dock ≈ 4.75–4.95 (relax the
   "at-or-below mining parity" cue by ~3–10%) — then k = 1.1 approves with
   margin, and δ = 0.6 (premium 1.67×, ceiling margin 8.7%) is the stable
   interior choice.
2. **Cap per-species contribution** for the new tail (drop equal-contribution
   above a rank threshold) — a NEW family, needs its own registration.
3. **Land the roster in waves** (N ≈ 12–16 per wave, re-simmed per wave) —
   each wave has parity headroom.

Anomaly A1 (disclosed, never smoothed): the runner's printed ruling line
applies S1/S2 without the C9 stability demotion; the demotion is carried by the
recorded `stability:A1`/`stability:A3` self-check failures and exit code 1 —
the registered rule applied to the accepted run's own numbers lands NULL.

## 8. Self-checks & reproducibility

85 self-checks: 83 passed, 2 failed — the two failed checks ARE the finding
(§ 4). First complete run of the registered pipeline = the accepted run; no
fix-forwards. Byte-identical double run (hashes § 2). Hermetic: reads only its
own `fixtures.json` + `fixtures/`; the only `random.Random` constructed are the
per-cast streams derived from the packet's own `fishing_seed`.
