# verdict-074 — menu-width leverage inversion (INTAKE 063)

Prices superbot-games' D&D bounded-menu leverage where it lives: the resolver
implements the message-XP width cap as a PREFIX slice
(`games/dnd/core/resolver.py::_allowed_options` returns `scene.options[:limit]`
@ pin `e3930f134119dd36d9e7f37a7dccb4f4b33e3805`), so WHICH options a low-XP
table can reach is decided entirely by scene option ORDER — plain data in
`games/dnd/data/scenes.py`. At idea-engine PROPOSAL 063's pinned model: the
complete within-scene role-ordering family {MNZ (SHIPPED), MZN, NMZ, NZM, ZMN,
ZNM} × DM behaviours {B1 UNIFORM, B2 GREEDY-FARMER, B3 STORY-DM, B4 CLAMP-p,
p ∈ {1/20, 1/4}} × widths {2, 3, 4} × both escort-mint accountings {PER-APP,
ONCE}, T ∈ {5, 20, 100}, judged against four pre-registered bands (MONOTONE,
POSITIVE-FLOOR ≥ 1/6, FARMER ≤ 3/4×SHIPPED, CONFORM). Fully hermetic: the
runner reads ONLY `fixtures.json` (committed before the runner); zero
repo/network reads at verdict time.

## Run

```
python3 sims/verdict-074-menu-width-leverage/menu_width_leverage_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). ~75 s/run, stdlib-only. Exit 1 on the accepted run — the 59
recorded failures are ANOMALY A1 (a disclosed tolerance-clause artifact on
near-one ONCE cells, ≤ 1.29σ under the true binomial σ; REPORT.md
§ Anomalies), not a twin disagreement; the decision path is exact-arm only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 063
  block / idea doc (the width law + fixture table, the 3 scene role-tuples
  with literal shipped positions and defaults, TIER_CAPS[I] = (5, 25, 10),
  GLOBAL_MAX = (20, 120, 50), `_FULL_MENU_XP = 5000` as the dedup witness,
  6 policies, 4 behaviours with p ∈ {1/20, 1/4}, T ∈ {5, 20, 100}, both
  accountings, the 4 band constants, the F2 rationals, the F4 hand trace),
  plus the fixture-level conventions C1–C10 and the seed re-registration
  (20261559–20261562, above the V075/V076 high-water 20261558) disclosed
  BEFORE the runner existed.
- `menu_width_leverage_sim.py` — two-arm runner: exact `fractions.Fraction`
  forward recursion over (scene, visited, minted) states + DAG absorption
  long-run rates (decision-bearing; gates F1/F1b/F2/F3/F4, bands, partition
  certification); seeded MC twin evaluator (20,000 episodes/cell, legs A /
  twin B / B4-stress / holdout per C10, 3σ agreement per C7).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, band table, gates, anomaly A1, reporting legs,
  boundaries, the pre-registered REJECT consequence.

## Ruling

**REJECT-REORDER** — no within-scene ordering passes all four bands, and the
impossibility is certified, not sampled: across all 6 orderings the width-2
B1 long-run mint rate partitions as exactly **{0, 1/2}** (rate =
[M ∈ prefix(2)]/2), so MONOTONE (needs w2 ≤ w3 = 1/3-rate cell) and
POSITIVE-FLOOR (needs w2 rate ≥ 1/6) are jointly unsatisfiable by ANY
data-only reorder. The shipped data is reward-INVERTED: SHIPPED × B1
long-run mint rate falls 1/2 → 1/3 at the first 500 message-XP
(E[mints, T=20] = 9961473/1048576 ≈ 9.500 → 21502885715/3486784401 ≈ 6.167,
−35.1%), the greedy farmer is not gated by width at all (19 mints / 190
currency at T=20, every width), and the §4.1 "always ON the menu" clamp
promise is false at width 2 for SHIPPED and NMZ. Recommendation escalates to
the named mechanic change: width must stop SELECTING by prefix (per-option
`min_width` data or width-indexed option sets — intent stays the lane's),
with NZM/ZNM priced as the interim zero-floor menu.
