# verdict-088 — the hint that hides: max_depth visibility clip (INTAKE 075)

Prices idea-engine PROPOSAL 075's harvested tension where it lives: the
mineverse v1 READ contract commits `max_depth` as an **OPTIONAL
world-shape hint** ("Consumers must fall back gracefully when absent",
`schemas/mining_snapshot.v1.schema.json:24-28` @ `b9ade33`) and bounds
miner `depth`/`record_depth` 0–3 **independently**, with ZERO cross-field
applicators anywhere in the schema — so the committed validator accepts
all 80 (hint × depth × record) lattice cells — while the world views
consume the same hint as a **hard render gate** three ways:
`build_ladder` and `build_minimap` render bands
`range(max_depth + 1)` ONLY (`server/views.py:216/316`, the schema-bound
fallback 3 reserved for ABSENCE, `:633-634`), and the flagship Deep
Diver badge is `record_depth == max_depth` **exact equality**
(`:446-448`). Four exact theorems carry the verdict: **T1** a miner is
FULLY INVISIBLE in the world views (no `here` row, no record chip, no
minimap point, not even `unplotted`) on exactly **(3−m)² cells per
present hint — 14/80 total** (minimap-invisible 24; ghost-chip-only 10,
where a stale "Name · record" chip is the only trace of a miner whose
live position renders nowhere) — against the same file's committed
doctrine "listed honestly, never silently dropped" (`:310-311`);
**T2** deep_diver ⇔ r = m_eff everywhere (20/80 earn), with **12
non-monotone flip cells** — digging ONE band past the hint LOSES the
"deepest" badge — 24 overshoot denials, and the m = 0 inversion (the
never-dug newcomer earns Deep Diver while the r = 3 explorer is
denied); **T3** one validator-accepted witness ranks **#1 on the depth
board AND #1 on the coins board** (the leaderboards never read the
hint) while appearing NOWHERE in the world views, with the badge
inverted — omitting the optional field flips all three at once;
**T4** hint domination: absence ≥ presence on all 64 comparisons,
strict on exactly the 14 — the optional field can only ever HIDE. All
decision arithmetic is seedless exact integers (REJECT checked first).
The runner is hermetic — it reads ONLY `fixtures.json` (committed
before the runner); every pin was re-verified FIRSTHAND on a read-only
public-HTTPS shallow clone at exactly `b9ade33`, and a scratch
rehearsal drove the ACTUAL committed `views.py` +
`snapshot_validation.py` over the full lattice reproducing every
disclosed census BEFORE the fixture was written (zero harvest
anomalies).

## Run

```
python3 sims/verdict-088-max-depth-hint-visibility-clip/max_depth_hint_visibility_clip_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~0.1 s. Every
decision number is an exact small integer; the seeded Arm R carries no
statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 075 block / idea file (the pinned schema constants + the
  empty applicator inventory, the four laws with their file:line
  quotes, the pinned sample-derived miner template, the census closed
  forms, the T3 witness, the G5 hand world, the three G6 repair worlds,
  the typed margin ledger, the Arm-R document model, seeds, the
  decision rule, conventions C1–C13).
- `max_depth_hint_visibility_clip_sim.py` — the four-arm runner
  (A closed forms / B independent enumerator / F verbatim transcription
  / R seeded reporting).
- `results.json` — canonical machine-readable outputs (sorted keys, no
  timestamps): the full 80-cell table (four outputs per cell), every
  census with its cell lists, the witness transcripts, the repair-world
  numbers, the structured anomaly census, the seed registry.
- `run-stdout.txt` — the accepted run's stdout.
- `REPORT.md` — the ruling against the pre-registered bands, the
  numbers, the margin ledger, falsifiability, and the consequence
  hand-off.
