# VERDICT 074 — REPORT — menu-width leverage inversion: message-XP widens the D&D menu into FEWER rewards, and no data-only reorder can fix it (INTAKE 063)

**Class: REJECT-REORDER** (pre-registered rules applied in order: gates
F1/F1b/F2/F3/F4 first — all green, so NULL does not fire; APPROVE-REORDER
requires ≥ 1 of the 6 orderings to pass ALL FOUR bands — none does;
REJECT-REORDER certifies the {0, 1/2} partition as the citable result).

Source: idea-engine `## PROPOSAL 063 · 2026-07-14T11:42:16Z · status:
sim-ready` (idea-engine PR #419 @ main 6d6735f; idea doc
`ideas/superbot-games/menu-width-leverage-inversion-2026-07-14.md`; where the
doc and the block differ, the block wins — no disagreement found). Subject
pins re-verified FIRSTHAND this session at superbot-games
`e3930f134119dd36d9e7f37a7dccb4f4b33e3805` (Q-0120: the pinned commit fetched
into the session clone; resolver prefix slice, width law, scene tuples,
escort mint path, TIER_CAPS/GLOBAL_MAX, `_FULL_MENU_XP` all read at that
SHA). Fully hermetic at verdict time: every fixture constant pinned in the
PROPOSAL 063 block / idea doc, copied verbatim into the committed
`fixtures.json`; the runner reads only that file. The drafter's disclosed
closed-form landing was re-derived from scratch with ZERO trust and compared
NEVER gated — 8/8 matches, zero mismatches.

## Reproducibility

- `SELF-CHECKS: 1537 passed, 59 failed`, exit 1 — **the 59 failures are
  ANOMALY A1** (a disclosed tolerance-clause artifact, § Anomalies below;
  every one is an `-once` twin check on a near-one cell; agreement, not
  disagreement). The decision path is exact-arm only; all gates green; every
  PER-APP twin check green on every leg. Carried honestly per the V075
  precedent — the accepted run's failures are reported, never smoothed.
- Byte-identical across two full process runs by external `diff` + sha256:
  `run-stdout.txt` = `3191d60ae538fd236d45f73f936e9cd8007743da7b439e1ee350fe17e6044c6c`,
  `results.json` = `4e6f3b3c27949582ba2698faeeb8a55e61bebf1930f089f211d3c34a71dc7c64`.
- ~75 s/run, stdlib-only, hermetic (reads only its own `fixtures.json`),
  CPython 3.11 pinned and asserted.
- Seeds: 20261559 (leg A, all 90 cells) / 20261560 (independent twin leg B,
  all 90) / 20261561 (B4 clamp-stress, the 36 B4 cells) / 20261562 (holdout,
  the SHIPPED×B1 cells) — the ONLY leg seeds; 219 per-cell substream RNGs
  derived per convention C3, counted and asserted; uniform draws counted:
  111,960,000 (A) / 111,960,000 (B) / 72,000,000 (B4-stress) / 6,000,000
  (holdout); turn sentinels exact (cells × 20,000 × 100). Registered
  strictly above the V075/V076 fleet high-water 20261558 — NEW REGISTRY
  HIGH-WATER 20261562. (The proposal's drafting-time seeds 20261389–392 were
  overtaken by the V075/V076 registration before this slice ran;
  re-registration disclosed in fixtures BEFORE the runner.)
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run — including its 59 artifact failures. Fixtures committed
  BEFORE the runner (git trail on PR #140).
- Every decision number is a seedless exact integer / `fractions.Fraction`.

## Decision — band table (PER-APP, exact arm; the citable result)

| policy | MONOTONE | POSITIVE-FLOOR | FARMER | CONFORM | all four | B1 E[mints,T=20] w2 | w3 (=w4) | B1 long-run w2 | B2 currency T=20 w2 |
|---|---|---|---|---|---|---|---|---|---|
| MNZ (SHIPPED) | ✗ | ✓ | ✗ | ✗ | ✗ | 9961473/1048576 ≈ 9.500 | ≈ 6.167 | 1/2 | 190 |
| MZN | ✗ | ✓ | ✗ | ✓ | ✗ | 9437205/1048576 ≈ 9.000 | ≈ 6.167 | 1/2 | 190 |
| NMZ | ✗ | ✓ | ✗ | ✗ | ✗ | 9961473/1048576 ≈ 9.500 | ≈ 6.167 | 1/2 | 190 |
| NZM | ✓ | ✗ | ✓ | ✓ | ✗ | 0 | ≈ 6.167 | 0 | 0 |
| ZMN | ✗ | ✓ | ✗ | ✓ | ✗ | 9437205/1048576 ≈ 9.000 | ≈ 6.167 | 1/2 | 190 |
| ZNM | ✓ | ✗ | ✓ | ✓ | ✗ | 0 | ≈ 6.167 | 0 | 0 |

w3 cell (every policy, B1): E[mints,T=20] = 21502885715/3486784401 ≈ 6.167;
long-run 1/3. FARMER threshold = 3/4 × 190 = 142.5.

**The certified impossibility (exact, seed-free):** the width-2 B1 long-run
mint rate across all 6 orderings partitions as exactly **{0, 1/2}** — rate =
[M ∈ prefix(2)]/2, asserted per policy. Orderings with the mint in the
width-2 prefix (MNZ, MZN, NMZ, ZMN) run at long-run 1/2 > 1/3, so widening
to w3 strictly LOWERS mints (MONOTONE fails); orderings without it (NZM,
ZNM) run at exactly 0 < 1/6 (POSITIVE-FLOOR fails). MONOTONE and
POSITIVE-FLOOR are jointly unsatisfiable by ANY data-only reorder — a closed
impossibility over the complete 6-permutation fix menu, not a sampled miss.
The JOINT-UNSAT check is asserted per policy in the accepted run.

The inversion headline (SHIPPED × B1): long-run mint rate falls **1/2 → 1/3**
(−1/6 per turn absolute, −33% relative) when the table earns its first 500
message-XP; E[mints, T=20] falls 9.500 → 6.167 (**−35.1%**). Width gates the
farmer NOT AT ALL: B2 lands 19 mints / 190 currency at T=20 at EVERY width
(mint priority finds `escort_step` in every surfaced prefix that contains
it, and SHIPPED surfaces it at index 0). CONFORM is false for MNZ (SHIPPED)
and NMZ: at width 2 the surfaced prefix EXCLUDES the clamp default that
`models.py` §4.1 promises is "always ON the menu" — the invalid-input path
resolves an option the DM was never allowed to surface.

## Gates (all green)

- **F1 identity** — width formula reproduces the pinned table
  {0→2, 499→2, 500→3, 999→3, 1000→4, 5000→4}; all three scene role-tuples
  with defaults = role Z at shipped index 2; mint exactly on `escort_step`;
  `treeline_watch` absorbing at every width and ordering; TIER_CAPS[I] =
  (5, 25, 10); GLOBAL_MAX = (20, 120, 50); `_FULL_MENU_XP = 5000` present as
  the dedup witness.
- **F1b literal-shipped equivalence** (the firsthand finding, asserted not
  assumed) — the literal shipped `waystation_gate` tuple is
  `(enter_common_room, circle_to_treeline, rest_at_gate)` — (N, M, Z) under
  the pinned role map, NOT (M, N, Z). Its surfaced SET equals the MNZ
  policy's at every width (asserted per scene × width, 9/9), and all four
  behaviours are set-based (C1), so the SHIPPED decision cell is exactly the
  MNZ policy cell. Disclosed in fixtures (`_provenance` +
  `shipped_role_positions: "NMZ"`) before the runner.
- **F2 inversion closed form** — exact arm reproduces long-run 1/2 (w2) and
  1/3 (w3), and E[mints, T=20] = 9961473/1048576 (w2) and
  21502885715/3486784401 (w3) EXACTLY.
- **F3 width identity** — w4 ≡ w3 in every cell (all 30 policy × behaviour
  combos: checkpoints and long-run rates exact-equal).
- **F4 hand world** — the by-hand 2-turn SHIPPED×B1×w2 trace matches the
  recursion cell-for-cell: turn 1 mint 1/2, after-state {gate 1/2, treeline
  1/2}; turn 2 mint 1/4, after-state {gate 1/4, treeline 3/4}; E[mints,T=2]
  = 3/4.

## Anomalies (first-class findings)

- **A1 — the 59 recorded twin-check failures are a C7 clause artifact, not a
  twin disagreement.** All 59 are `-once` checks on cells where the exact
  P(≥1 mint) = 1 − ε with ε ∈ [3.21e-13, 8.27e-5]. At n = 20,000 the modal
  MC outcome is p̂ = 1.0 exactly (e.g. P(p̂ = 1) ≈ 0.981 at ε = 9.5e-7); the
  sample variance then degenerates to 0 and the registered zero-variance
  clause ("se = 0 ⇒ exact equality") demands 1.0 == 1 − ε. Under the TRUE
  binomial σ every failing cell sits ≤ 1.29σ from exact — agreement. The
  registered rule is applied as written (exit 1 recorded, failures listed in
  `results.json`), the artifact is named, and nothing is smoothed. Decision
  impact: none — bands, gates, and the partition are exact-arm; every
  PER-APP twin check and every non-degenerate ONCE check is green on every
  leg. Lesson for the NEXT registration (not retro-fitted): near-one ONCE
  cells should be toleranced against the exact-arm binomial σ, not the
  sample σ.

## Reporting legs (ungated)

- **B4 CLAMP-p (the §4.1 gap channel):** the clamp path mints NOTHING (the
  full-scene default is `rest_noop`), so no economy leaks through the gap —
  but it further dilutes leverage: SHIPPED long-run rate at w2 = 19/40
  (p = 1/20) and 3/8 (p = 1/4); at w3 = 19/60 and 1/4. The inversion
  survives the hallucination channel at both p values (the B4-stress leg
  agrees). What the gap DOES break is legality, not economy: at width 2
  under MNZ/NMZ the clamp resolves an option outside the legal surface
  (CONFORM false).
- **B3 STORY-DM:** 0 mints at every ordering × width (prefers N > Z > M) —
  the reward-averse floor; a flavour-first table earns nothing under every
  ordering, unchanged by leverage.
- **ONCE accounting (sensitivity arm):** P(≥1 mint) at T=20 ≥ 0.9997 in
  every mint-reachable B1 cell and exactly 0 in the zero-floor cells — every
  band verdict is unchanged under ONCE (the inversion is driven by mint
  COUNTS, composing with either DND-ESCORT-DOUBLE-MINT ruling, as
  registered).
- **Set-equivalence classes:** MNZ ≡ NMZ and MZN ≡ ZMN cell-for-cell (equal
  width-2 prefix SETS) — the entire grid is driven by prefix membership,
  which is the mechanism finding in one line: under prefix truncation only
  SET composition matters, so ordering can only move options in or out of
  the prefix, never shape rates between 0 and the menu share.
- Distinct-scenes and no-op expectations per cell in `results.json` (e.g.
  SHIPPED×B1 w3 spends E ≈ 6.67 of 20 turns on the do-nothing button that
  width-2 play never sees; NZM/ZNM w2 park the table at E[distinct] = 2
  scenes with zero mints).

## Boundaries (as registered)

- The behaviour family is the declared model-dependent layer (real DMs are
  LLMs): B1 agnostic baseline / B2 revenue adversary / B3 reward-averse
  floor / B4 hallucination channel; every band is keyed to a NAMED
  behaviour, never an average. A logged DM-choice trace from the lane is the
  named free replacement measurement.
- Whether a zero-mint width-2 table (NZM/ZNM) is an acceptable DESIGN is an
  intent call and stays the lane's (V044/V046 posture) — this verdict hands
  over the exact price tag, it does not rule.
- The 3-scene walking skeleton is pinned by F1: more scenes change the
  numbers but not the partition argument (rate = [M ∈ prefix(2)]/2 holds per
  absorbing menu); any scenes.py/resolver change after `e3930f1` forces a
  loud re-pin, never a silent stale verdict.
- TIER_CAPS held fixed (ORDER 006 item (7) territory): any cap retune
  rescales currency linearly and moves no band.

## Transferable law (pre-registered REJECT consequence, verbatim-faithful)

Width must stop SELECTING by prefix: the named mechanic change is per-option
`min_width` data or width-indexed option sets (`resolver.py` /
`leverage.py` / `scenes.py` are the lane's surface; intent stays the lane's,
routed by the manager per Q-0260). NZM/ZNM are priced as the interim
zero-floor menu: they buy MONOTONE + full farmer-gating (B2 w2 currency 0,
−100%) + CONFORM at the price of a zero-mint width-2 game. Cheapest
lane-side reproduction (one line): run the lane's own
`games/dnd/sim/menu_sim.py` at xp ∈ {0, 500} instead of
`_FULL_MENU_XP = 5000`. The reusable pattern: wherever a capability tier is
implemented as a PREFIX over an ordered list (permission tiers, flag
rollouts, unlock-by-rank), the tier gradient is worth exactly what the
ordering puts inside the prefix — audit the SET, not the length.
