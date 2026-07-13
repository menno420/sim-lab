# VERDICT 050 — Gloamline plateau survival ceiling: REPORT

> **Status:** `finalized` — INTAKE 039 / VERDICT 050, serving idea-engine
> `control/outbox.md` — `## PROPOSAL 039 · 2026-07-13T16:33:11Z · status:
> sim-ready`. Claim: idea-engine PR #323 → main ab66463. Numbering P039 →
> V050 per the +11 offset map (the number RESERVES, never the position).

## Question

Under the pinned Gloamline night frame (every constant committed in
gba-homebrew @ `d87f9ad`), what is SURV(policy, oil-leg, night) for the
pre-registered keys-only policy family — and does the committed ramp (waves
2·night−1, cap 24 from night 13, all spawns ON the fence perimeter inside
the first 2,400 of 3,600 night frames) ever cap a MOVING bounded player, or
is the nights-survived record (slices 9/11 already build on it) a patience
meter?

## Pre-registration

`fixtures.json` + the whole-file byte-copy `check_gloam_mirror.py` (sha256
`c86d950723b6fff1159a9c6cddb32822f6c8651e65376f2001a86f7372492892`,
re-verified before import) committed BEFORE the runner — engine constants
verbatim, the per-frame loop order with main.c cites (spawn_due main.c:509 →
player step → do_shove_verb main.c:620 → step_the_dead main.c:737 →
contact; start_night main.c:521), policies {IDLE regression; KITE-PERIM
(waypoints (40,56)/(215,56)/(215,151)/(40,151) px, deadzone GL_ONE/2,
advance ≤ 2 px); KITE-GRAD (9 key-sets through gl_player_step, maximin
Chebyshev, ties N/NE/E/SE/S/SW/W/NW/stay); SHOVE-PERIM/SHOVE-GRAD (+A at
cold cooldown with nearest ≤ 24 px)}, oil legs LIT (oil_for_press =
GL_OIL_MAX) vs DARK (oil_for_press = 0), the census/ramp/noise grids, seeds
20261293–96 (strictly above high-water 20261292; new high-water 20261296),
bands 99% / 90% / 50%, decision nights {13, 16, 20, 24}, evaluation order
REJECT → APPROVE → NULL.

## Run

`python3 sims/verdict-050-gloamline-survival-ceiling/gloamline_ceiling_sim.py`
— one command, no flags; stdlib-only, hermetic (reads only its own
`fixtures.json` + `check_gloam_mirror.py`); cpython-3.11 pinned, asserted;
~32 s. **SELF-CHECKS: 8358 passed, 0 failed**, exit 0. stdout +
`results.json` byte-identical across two full process runs by external
diff/cmp (results.json sha256
`94b9be443b30dab159cd12df36c365b375572c7066d823394a1675b267343f48`); no
wall-clock in any output. No fix-forwards on measurement: the runner's
development edits (grad-pruning expression, the DARK-identity counter made
a genuine mirror cross-check, per-leg check aggregation, self-check
bookkeeping) all landed before the first complete run of the registered
pipeline, whose output is the accepted run byte-for-byte.

## Gates (all green, run invalid on any failure)

- **Mirror sha256** re-verified before import; every engine constant
  cross-checked against the imported mirror.
- **IDLE proof-2 regression:** 256 index-0 chases + 1,024 every-spawn
  chases (seeds 0..63 × nights 1..4), all monotone non-increasing with
  contact ≤ 400 frames — worst contact frame **258**, byte-equal to the
  mirror's own committed suite print ("worst contact frame 258").
- **Press-dominance spot gate (proof 11d's committed range):** green;
  worst pressed contact **186**, byte-equal to the mirror's own print.
- **Spawn identities:** 30,720 census spawns — fence perimeter, ≥ 64 px
  from the lamppost, gl_wave_count ≡ min(2n−1, 24), spawn frames
  non-decreasing < 2,400.
- **Stagger-rate identity:** pinned 86,400-cell (id, frame) grid mean
  21638/86400 ≈ 0.25044, inside 3σ of 1/4; **DARK zero-stagger identity**
  measured on every DARK leg via the mirror's own gl_dark_press on every
  no-stride event: 0 violations.
- **Twin engines:** the optimized census loop ≡ the independently-written
  mirror-functions-only reference (structured on main.c) — death frame,
  min-gap, shove connects, final crowd — on all 32 subsample cells + the
  gl_hash-driven noise-path probe replay (no registry draw).
- **Sentinels:** Arm D 1,256,927 frames, zero RNG; Arm S draws counted by
  an independent wrapper equal per-leg executed frames exactly (main
  4,091,553 / stability 2,045,785 / reporting 4,083,328); **aux 20261296:
  ZERO draws**.
- **Twin decision evaluators** agree on main and stability inputs;
  **stability leg (seed 20261294, M = 16) reproduces the ruling**.

## Measured

Arm D census (SURV = survivors/seeds), decision nights:

| policy | LIT 13/16/20/24 | DARK 13/16/20/24 | median death frame (LIT) |
|---|---|---|---|
| KITE-PERIM (128 seeds) | 0/0/0/0 | 0/0/0/0 | 155/173/154/155 |
| SHOVE-PERIM (128 seeds) | 0/0/0/0 | 0/0/0/0 | 284/305/274/284 |
| KITE-GRAD (32 seeds, nights 13/24) | 0 / 0 | 0 / 0 | 311/329 |
| SHOVE-GRAD (32 seeds, nights 13/24) | 0 / 0 | 0 / 0 | 441/457 |

**SURV = 0 in every decision cell** — not a knife-edge read against the
50% band. The shove verb buys frames (median death climbs ~2× with A
presses; SHOVE-PERIM ~223–266 connects per 128-seed cell) but never a
night. Ramp leg (KITE-PERIM · LIT, reporting-only): night 1 = 51/128 ≈
0.398, night 2 = 15/128, night 3 = 1/128, nights 4–12 = 0/128 — the blind
kiter's ceiling is night ~1–3, consistent with the lane's own EARNED
best-nights record (proof 20: best = 1, seed 118). Arm S noise legs: 0
survivors in all 16 legs × all three registry streams (noise only worsens
already-fatal cells). Per-axis survival shares: 0 on every axis.

Mechanism (read-out from the committed frame, not a decision number): the
fence-spawn stream is anchored to the LAMPPOST's safe radius, not the
player — fresh spawns land arbitrarily close to a fence-adjacent player
all through the first 2,400 frames; and the myopic KITE-GRAD corners
itself (one frame ahead, every escape move along a wall scores
tied-or-worse Chebyshev, the pinned tie-break holds the wall-clamped
move) — the registration's own disclosed one-frame-lookahead boundary.

## Ruling

Pre-registered order, REJECT first:

- **REJECT does not fire:** KITE-PERIM · LIT is 0/128 at every decision
  night (band ≥ 99/100) and the ε = 1/16 night-24 LIT leg is 0/1024 (band
  ≥ 90/100) — both conjuncts fail maximally.
- **APPROVE fires:** EVERY swept policy including SHOVE-GRAD posts
  SURV < 50/100 at some decision night (measured: 0 at every one) in BOTH
  oil legs, stability-reproduced through the twin evaluators.

**VERDICT: APPROVE** — "the committed ramp has a real ceiling — the
record is a skill score." The per-policy ceiling table is the pin: every
bounded policy in the family posts its ceiling BELOW night 13 (the blind
kiter below night ~3).

## Boundaries (stated, per the registration)

The family brackets BOUNDED play from below — every SURV is a lower bound
on the best player's, so APPROVE rules on this family only and an optimal
planner could outlive every ceiling here (stated); KITE-GRAD is myopic by
design; the plank/oil/scavenge economy is out of decision scope (nights are
position/crowd-independent by start_night's own reset; oil enters as the
two pinned legs — the LIT−DARK delta measured ≈ 0 nights on this family,
because the family dies inside the lit chase already); policies emit
exactly the key-sets the ROM accepts. Liveness disclosure carried verbatim:
no closed form decided any band; the 2:1 speed ratio argued REJECT, the
fence-spawn stream + lap-geometry argued APPROVE/NULL — measurement, not
expectation, picked APPROVE.

## Consequence (pre-registered APPROVE arm)

The best-nights record system is ratified as a bounded skill score with the
measured ceiling table attached; no difficulty lever demanded. Routing is
the manager's per Q-0260 — this repo never edits gba-homebrew files.
