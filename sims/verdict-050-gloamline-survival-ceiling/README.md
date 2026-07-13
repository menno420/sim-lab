# verdict-050-gloamline-survival-ceiling

> **Status:** `in-progress` — VERDICT 050 (INTAKE 039), idea-engine PROPOSAL
> 039 ("Gloamline plateau survival ceiling", game-mechanics rotation round 6 —
> the first head sourced from the Game Lab repo; consumer =
> `menno420/gba-homebrew`'s difficulty backlog + best-nights record system,
> routed via the manager sweep, Q-0260).

Pre-registered survival-ceiling census for Gloamline's committed difficulty
curve: does the night ramp (waves 2·night−1, cap 24 from night 13, all spawns
ON the fence perimeter inside the first 2,400 of 3,600 night frames) ever cap
a MOVING bounded player, or is the nights-survived record a patience meter?
Engine = the lane's own committed pure mirror `tools/check-gloam.py` @
`d87f9ad`, **byte-copied whole** into this directory as
`check_gloam_mirror.py` (sha256
`c86d950723b6fff1159a9c6cddb32822f6c8651e65376f2001a86f7372492892`,
re-verified before import — the V042/V043 byte-reuse precedent applied to a
sibling lane's proof mirror). Every constant verbatim from the PROPOSAL 039
block / idea file. Details and the full ruling in [REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-050-gloamline-survival-ceiling/gloamline_ceiling_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` +
  `check_gloam_mirror.py` — one command, no flags; stdout + `results.json`
  byte-identical across two full process runs by external diff — no
  wall-clock in any output; cpython-3.11 pinned and asserted)
- **Pre-registration:** `fixtures.json` + the mirror byte-copy committed
  BEFORE the runner (git trail, this PR's commits) — engine constants, the
  per-frame loop order with main.c cites, waypoint/tie-break/policy
  constants, the night and game-seed grids, the ε grid, M per leg, registry
  seeds 20261293–96 (new registry high-water 20261296), band constants
  (99%, 90%, 50%, decision nights {13, 16, 20, 24}), decision rule
  REJECT → APPROVE → NULL evaluated in order, REJECT first
- **Arms:** Arm D — deterministic policy census, ZERO RNG (game seeds are
  enumerated fixture inputs, not registry seeds): {KITE-PERIM, SHOVE-PERIM}
  × {LIT, DARK} × nights {13, 16, 20, 24} × seeds 0..127, {KITE-GRAD,
  SHOVE-GRAD} × {LIT, DARK} × nights {13, 24} × seeds 0..31, ramp leg
  nights 1..12 × seeds 0..127 × KITE-PERIM × LIT reporting-only; Arm S —
  seeded execution noise (each frame w.p. ε ∈ {1/16, 1/4} the chosen
  key-set replaced by a uniform draw over the 9 key-sets, one
  `random.random()` per frame), {KITE-PERIM, KITE-GRAD} × {LIT, DARK} ×
  nights {13, 24} × ε, M = 32 × seeds 0..31; seeds 20261293 main /
  20261294 stability (M = 16, must reproduce the ruling) / 20261295
  reporting / 20261296 aux (never read by any decision number, zero draws)
- **Gates (run invalid on any failure):** mirror sha256 before import ·
  IDLE proof-2 regression (monotone chase, contact ≤ 400 frames) · spawn
  identities on every census spawn · stagger-rate 3σ identity + DARK-leg
  zero staggers beyond 24 px · press-dominance spot gate (proof 11d's own
  range) · per-leg frame/draw-count sentinels · twin engines (optimized
  census loop ≡ mirror-functions-only reference on the pinned subsample) ·
  twin independently-written decision evaluators · two-process
  byte-identity · CPython minor pinned
- **Ruling:** see REPORT.md (exactly one of APPROVE/REJECT/NULL per the
  pre-registered rule, REJECT checked first; an honest NULL lands as a
  finalized verdict)
