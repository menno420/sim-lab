# VERDICT 058 — creature-PvP rarity vs skill (idea-engine PROPOSAL 047)

Prices superbot's committed level-normalized creature-PvP battle engine
(`disbot/utils/creatures/battle.py` @ 1cc553651a19016a4b1439f048b49e7baa28dfb1)
on its own never-cross-rarity-tested promise — the `RARITY_BUDGET` comment
"rarer = stronger, but level + type + move choice still let a Common counter
an Epic" and the module docstring "rewards *skill*, not *time spent*" — per
the registration (PROPOSAL 047, idea-engine
`ideas/superbot/creature-rarity-skill-counter-2026-07-13.md` @ main 2808b16).

Run: `python3 sims/verdict-058-creature-rarity/battle_sim.py`

- `fixtures.json` — every registered constant + all 24 quoted catalog rows,
  committed BEFORE the runner.
- `battle_sim.py` — Arm S (seeded-MC decision arm: the 9-cell max-skill-Common
  × Epic-pilot grid, mirror/naive/Rare-gradient reporting legs, stability +
  sensitivity legs) + Arm E (seedless exact-Fraction catch-economics stakes
  arm) + gates F1–F6 + twin evaluators.
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two process runs; sha256s in REPORT.md).
- `REPORT.md` — ruling, the 9-cell W table, gates, boundaries.

Ruling: **reject** (checked FIRST, fires — the budget wall stands: the
max-skill Common side won 0 of 425,000 decision+reporting battles; the type
chart's best case exactly neutralizes the per-hit budget square and never the
HP pool). Hermetic, stdlib-only, CPython 3.11 pinned, seeds 20261325–328,
TP = 475/12 ≈ 39.58× grind premium.
