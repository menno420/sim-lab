# REPORT — VERDICT 058: creature-PvP rarity vs skill (PROPOSAL 047)

**Ruling: reject** — per the pre-registered rule, evaluated IN ORDER, REJECT
FIRST, on the main leg's exact Fractions.

- **REJECT (checked FIRST) fires:** W(c, BEGINNER) < 2/5 in **3 of 3** Common
  compositions (band: ≥ 2 of 3). Measured: W = **0/1 exact in every cell** —
  the max-skill Common side won **zero of 20,000 battles** in each of the 9
  grid cells (and zero in every reporting cell except the mirror). Even
  max-skill Common play loses not 3-in-5 but *every observed battle* to a
  beginner-piloted Epic team: type, ordering, move choice, and setup cannot
  climb 200-vs-300.
- Stability leg (seed 20261326, N = 5,000/cell) reproduces REJECT through
  both twin evaluators. No sensitivity straddle fired (all four reporting
  scenarios land the same class).

## The 9-cell W grid (P(Common side wins), main leg, N = 20,000/cell, exact)

| composition | BEGINNER | MID | SKILLED |
|-------------|----------|-----|---------|
| BAL | 0/1 | 0/1 | 0/1 |
| ATK | 0/1 | 0/1 | 0/1 |
| MIX | 0/1 | 0/1 | 0/1 |

Reporting legs (N = 20,000 each, same seed-20261325 stream, pinned order):
mirror BAL-vs-BAL (both max-skill) **4977/10000 = 0.4977** (calibration gate:
within 1/50 of 1/2, deviation 23/10000 — PASS); naive-vs-naive BAL-vs-Epic
**0/1** (the raw wall, expected direction W < 1/2 — no anomaly flag);
Rare-gradient BEGINNER **0/1**; Rare-gradient SKILLED **0/1**.

**Disclosed anomaly, first-class (stronger than the registered bands
anticipated):** the wall is TOTAL at the modeled widths, not marginal. Zero
Common wins in 425,000 decision+reporting battles — including the Rare
gradient: a max-skill Common team beat a *naively piloted 260-budget Rare
team* zero times in 20,000. By the rule of three, every decision cell's true
W ≤ ~1.5e-4 at 95% confidence — the 2/5 REJECT band is cleared by more than
three orders of magnitude. The registered composition-straddle and
margin-band NULL axes never came into play.

**The mechanism, read off the committed constants:** the budget ratio enters
BOTH sides of the damage quotient — damage-rate ratio between sides scales as
(200/300)² = 4/9 before the type chart — while the type chart's maximum
swing (attacker strong 1.5 / defender forced into 0.67 resist) is
1.5/0.67 ≈ 2.239. Best case, 4/9 × 2.239 ≈ 0.995: **perfect type play
exactly neutralizes the per-hit budget square and buys nothing against the
HP pools** (Common 197 everywhere vs Epic 236–386), which the one committed
+ATK setup buff (+25%, once) cannot bridge either. Skill saturates at
per-hit parity; the fight is then decided by raw HP budget, every time.

## Arm E — the exact stakes (seedless Fractions)

- p(catch specific Epic per encounter) = (6/1884) · (2/5) = **1/785 exact**
  (gate); p(specific Common) = 95/1884.
- E_epic (the committed all-Epic team) = 785 · 49/20 = **7693/4 = 1923.25**
  encounters (inclusion–exclusion ≡ subset-Markov twin at exact equality).
- E_common (BAL) = **23079/475 ≈ 48.59** encounters.
- **TP = E_epic / E_common = 475/12 ≈ 39.58×** (hand span ≈ 39.6 — met): the
  committed catch economy sells the counter-proof-free Epic wall at ~40× the
  Common team's grind. With W ≡ 0 across all skill cells, that multiple buys
  unanswerable ranked power — exactly the Q-0039 pay-to-win shape the level
  normalization was adopted to kill, re-entering through the rarity side door.

## Run evidence

- Command: `python3 battle_sim.py` — exit 0, **104 self-checks, 0 failed**,
  ~20 s, stdlib-only, hermetic (reads only its own fixtures.json), no
  wall-clock in any output.
- **Byte identity:** stdout + results.json byte-identical across two full
  process runs by external diff. sha256 run-stdout.txt
  `369129f9830724981e9bd13e7e7b34c3cc0d710c387476de5c087d351b1e4c0f`;
  results.json
  `7ae143efa3cbfe5f6518fcf2ec63b0ff1635febb568bd799c34484df633a1a9e`.
- **Seeds:** 20261325 main / 20261326 stability / 20261327 sensitivity-
  reporting / 20261328 aux registered-never-drawn (no RNG constructed with
  it, asserted; exactly three RNGs constructed, in pinned order) — strictly
  above the P046/V057 high-water 20261324. NEW REGISTRY HIGH-WATER 20261328.
- **CPython pinned:** 3.11, asserted at startup.
- **Draw sentinels exact:** main leg 36,564,003 jitter draws ≡ 36,564,003
  damage events and 1,877,073 tie-flip draws ≡ 1,877,073 recorded ties (all
  ties live in the mirror leg — the only equal-SPD matchup, itself a wiring
  check); stability 5,562,017 ≡ damage events, 0 ties; sensitivity
  13,395,265 ≡ damage events over the three drawing scenarios with the
  degenerate scenario's sentinel pinned 0 draws, 0 ties. Battle counts
  260,000 / 45,000 / 180,000. Zero stall-guard hits anywhere (F5).
- **Twin evaluators** (Fraction comparisons vs pure-integer
  cross-multiplication, opposite iteration orders) agree on main AND
  stability inputs: (reject=True, approve_band=False, reject_ct=3,
  skilled_below_ct=3) both legs.

## Gates (all green)

F1 the full 7×6 effectiveness hand table exact (Normal row ≡ 1.0,
opposite-element ≡ 1.0); F2 the six derived-stat quadruples exact incl. the
tank-Epic (98, 60, 98, 45) total-301 overshoot; F3 level-50 identities (HP
mult 3.94 exact, off mult 2.715 exact, balanced-Common max_hp 197, tank-Epic
max_hp 386, atk/df 60/50 = 1.2 level-invariant at levels 5 and 50 within
1e-12 — the off mult cancels symbolically); F4 the deterministic
Cindling-vs-Infernox hand fixture at jitter ≡ 0.925 (full 32-event log
reproduced exactly: damages 6 and 13 every action, Cindling first, Infernox
KOs on its 16th action with Cindling at 96 dealt); F5 mirror within 1/50 of
1/2, naive-vs-naive expected-direction, zero stall hits, RARITY_BUDGET
spread 300/200 = 3/2 exact; F6 Arm E anchors (785 exact, the 49/20 equal-p
identity exact, subset-Markov twin ≡ inclusion–exclusion at exact equality).

## Sensitivity legs (seed 20261327, N = 5,000/cell, reporting-only — none flip)

All four scenarios reproduce W ≡ 0 in every cell (class REJECT): jitter
uniform(0.7, 1.0); jitter ≡ 0.925 degenerate; BUFF_CAP 3/4; level 5.
**Disclosed:** the BUFF_CAP leg is inert BY CONSTRUCTION under the committed
policy family — `policy_setup` buffs at most once (it requires
`atk_stage == 0.0`), so the stage is min(cap, 0.25) at either cap value; the
leg was run anyway per the registration and is a derived fact about the
engine, not a measurement. The level-5 leg confirms the registration's
off-mult-cancellation claim empirically: the normalized level value is
cosmetic for the ruling.

## Pre-registered REJECT consequence (verbatim-faithful, routed per Q-0260)

The quantified retune signal ships BEFORE any ranked surface or leaderboard
is built: `RARITY_BUDGET`'s spread (230/260/300 over 200) and
`ELEMENT_POWER`/`STRONG_MULT` are the named one-constant owner-tunables, and
the docstring's anti-P2W promise gains its precondition. The measured
mechanism gives the retune its direction: because budget enters the damage
quotient on both sides, the type chart can only compensate ~the SQUARE ROOT
of the budget ratio — parity of the harvested promise needs either a much
narrower budget spread (√-scaled: e.g. Epic ≈ 1.10–1.15× Common covers the
current type swing with room for skill) or a bigger committed skill surface.
superbot-next inherits the same signal through its parity-locked port (#226).
Routing is the manager's per Q-0260 — this repo never edits superbot files.

## Boundaries (each with its direction)

- **Skill ceiling:** the policy family is the engine's own committed ceiling
  (four policies + one ordering lever; no mid-battle switching exists in the
  engine). A cleverer in-engine policy could only RAISE the Common side —
  this REJECT is conservative in the one direction that matters. The
  saturation argument above (type play already reaches per-hit parity)
  bounds how much any policy could add.
- **Float:** the battle arm's reproducibility is pinned to CPython 3.11 (the
  P017+ Arm-S convention); Arm E is platform-independent exact rationals.
- **Roster:** 6v6 element-complete teams only (the owner's standard);
  off-meta element stacking out of registered scope.
- **Level:** ranked PvP normalizes levels by the engine's own rule — this
  verdict prices the sharper surviving claim; raw-level PvE counters are out
  of scope (the docstring itself routes raw levels to PvE/collection
  prestige).
- **Trading:** trading/gifting economies don't exist in the engine; TP
  prices self-caught grind only.
- **Application guard (pre-registered):** the verdict conditions on the
  36-row catalog @ 1cc5536 (exactly one Epic per element, two Commons per
  element) and the quoted engine constants — a catalog reshuffle or re-tuned
  engine means re-run, not reuse.

## Fixture-choice disclosures (bind no registered constant)

- The reporting legs' battle count (N = 20,000 each) was pinned at fixture
  time — the registration names the legs and requires per-leg counts in the
  fixture but does not number them; 20,000 matches the main grid's
  precision. Stability and sensitivity Ns (5,000) are the registration's own.
- The degenerate-jitter scenario draws no uniforms (sentinel pinned 0 in
  fixtures.json) — the fixture-only hook replaces the draw rather than
  discarding one, disclosed here and pinned there.
