# verdict-092 · owned-track-launch-flag-dial

The owned milestone track on the SHIPPED superbot-idle runtime. Answers
idea-engine PROPOSAL 079 (`## PROPOSAL 079 · 2026-07-16T00:39:30Z · status:
sim-ready`, idea
`ideas/superbot-idle/owned-track-launch-flag-dial-2026-07-16.md` @
idea-engine main 636e21d, landed via idea-engine PR #444): with no generator
purchase verb in the committed engine, the runtime grant makes "TOTAL
generators owned" the session constant s·n (launch flag × roster) — so is
the owned ladder a progression surface or a launch-configuration predicate?
Six structure theorems, re-derived from scratch on the vendored engine:
invariance (T1), the birth/never dichotomy with flip law ceil(θ/n) (T2),
the 54-slot frozen lock-line census (T3), the +5%..+15% flag dial with its
floor-gated payout rows (T4), the theme-gate-passing 10-vs-9-generator
roster back door (T5), and the boundary lag (T6).

## Run (one command)

```
python3 sims/verdict-092-owned-track-launch-flag-dial/owned_track_launch_flag_dial_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: stdout and `results.json`
are byte-identical across process runs (no wall clock, no paths, no
network, no git at run time). CPython 3.11 pinned and asserted.
Environment note: the vendored lane's own committed dependencies apply —
`idle_engine/theme.py` imports **PyYAML** and `tools/theme_gate.py` imports
**jsonschema** (the gate's committed docstring: "the theme-gate workflow
pip-installs it"). Every decision computation is stdlib + the vendored
engine; no third-party call sits in any decision path of this runner
itself.

## Layout

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  079 block / idea file, committed BEFORE the runner; carries the vendor
  sha256 manifest, the seven committed-sentence pins, the registered
  anchors, the Arm-R grammar + previews, and the disclosed sim-chosen
  conventions (vacancy-derived, per the fixture's own notes).
- `vendor/` — byte-for-byte copy of superbot-idle @
  `884aeae9687742a389a2e2086a4cc930e5a4f3ee` (35 files,
  sha256-manifest-verified at every run start; the V017 precedent),
  mirroring the lane's layout so `tools/play.py` and `tools/theme_gate.py`
  run unchanged. The sim is otherwise hermetic — zero repo/network reads at
  verdict time.
- `witness/` — the constructed 10/9-generator base-20 witness pair
  (invented-but-pinned per the registration; differ ONLY in roster length,
  asserted field-by-field).
- `owned_track_launch_flag_dial_sim.py` — the three-arm runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

## Arms

- **Arm A** — seedless exact integer closed forms (DECISION-bearing): the
  predicate s·n ≥ θ_k, the flip law ceil(θ/n), the committed fold
  `base_rate · count · upgrade_pct · prestige_pct · milestone_pct ·
  theme_pct // 100_000_000`, the dial/lag arithmetic.
- **Arm B** — the REAL vendored engine + runtime driven through
  `play.dispatch` / `play.advance` (independently-written walker with its
  own bookkeeping): the 11-command canonical corpus over all 216 cells
  (18 packs × the registered 12-value flag grid), the rendered lock-line
  census, the margin-0 flip quadruple quantified over the whole pack
  class, the live theme-gate subprocess over the assembled 20-pack
  catalog. Tied to Arm A through the four typed contacts C1–C4.
- **Arm R** — seeded random command traces, REPORTING-ONLY (seeds
  20261710/711/712, 2,000 traces each; aux 20261713 never read): the
  registered draw-order grammar with draw-count sentinels; the registered
  preview triples (violations, blessed, boundaries) reproduced exactly.

Decision rule (registered order, evaluated by two independently-written
evaluators over an ENUMERATED boolean input set): REJECT → INVALID →
APPROVE → NULL. Full grammar in `fixtures.json`.
