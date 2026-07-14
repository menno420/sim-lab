# verdict-070 — prestige reset-policy optimality (INTAKE 059 / idea-engine PROPOSAL 059)

Prices superbot-idle's committed "optimal-play" claim at the multiplier fold
the engine actually ships (source pin `5ddd5a230d4a6504c06b52805cba5dc8b3276b44`):
a pre-registered, fully deterministic, exact-integer 15-policy reset-schedule
grid (never / fixed-m / hybrid-k / cooldown-τ) over the registered SIM-001
14-day horizon, twin-arm (Arm A exact event scheduling, decision; Arm B
independently written per-second evaluator, must match every total exactly),
plus seeded REPORTING-ONLY random-policy probes (Arm R). The lane's flagged
reset-cadence cap is priced as the cooldown arms. Fully hermetic: the runner
reads only its own `fixtures.json`.

## Run

```
python3 sims/verdict-070-prestige-reset-policy/prestige_reset_policy_sim.py
```

One command, no flags, stdlib-only, CPython 3.11 (pinned and asserted).
Deterministic: stdout + `results.json` are byte-identical across process runs.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 059
  block / idea doc, plus fixture-level choices C1–C9 (committed BEFORE the runner).
- `prestige_reset_policy_sim.py` — the runner (both arms, Arm R, gates F1–F6,
  pre-registered decision evaluated REJECT → INVALID → APPROVE → NULL).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, tables, gate answers, boundaries.

## Ruling

**REJECT** — the committed "optimal-play" label is FALSE at the HEAD fold:
hybrid-1000 (one patient 10,000,000-lifetime run at P ≥ 1000, then greedy)
produces 27,411,200,535 vs greedy's 25,386,048,335 = 1.0798× (≥ the
registered 101/100 line, exact big-int, both arms; hybrid-10000 is a second
cell above the line at 1.0585×). Attribution holds: the same beater LOSES
with milestones OFF (0.9789×) — the beat is exactly what `tools/simulate.py`
omits. The docstring's grind half is simultaneously CONFIRMED: greedy =
1024.97× never-reset. All gates F1–F6 green; 72 self-checks, 0 failed.
