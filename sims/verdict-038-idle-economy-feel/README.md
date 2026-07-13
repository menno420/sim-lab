# verdict-038-idle-economy-feel — superbot-idle SIM-001 economy-FEEL sim (ORDER 005 SIM-REQUEST 2)

> **Status:** `finalized` — VERDICT 038 (conditional). Report: [REPORT.md](REPORT.md).

Serves idea-engine ORDER 005 SIM-REQUEST 2 (control/inbox.md @ 8218d66; fm ORDER 043
relay, Q-0264 fan-in; requesting seat **superbot-idle**): the SIM-001 economy-FEEL
cluster — ASK 1 (first-upgrade no-op), ASK 2 (weak prestige payoff), ASK 3 (A10
strict-vs-trend ruling + graduation) — implemented against the registered spec
`docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" at pin
`menno420/superbot-idle @ d992c5688e802b28d11c0ec6c835fa54a87149ec`.

## Contents

- `fixtures.json` — the PRE-REGISTRATION (committed before the runner): B0 validity
  anchors (packet numbers + V006 cross-pins), all ASK 1/2/3 arms, FEEL probe bands,
  every mechanical decision rule, 13 disclosed intake-time decisions, 1 disclosed
  amendment (A7 anchor mapping).
- `fixtures/` — byte-for-byte vendor copy of `idle_engine/` (all 11 modules) plus the
  repo's own committed SIM-001 harness `tools/simulate.py`, sha256-pinned in
  `fixtures/MANIFEST.json` and re-verified before anything is imported.
- `idle_economy_feel_sim.py` — the driver. Drives the REAL engine and the REAL
  committed harness (`run_report` / `simulate_s2` / `simulate_s3`); nothing economic
  reimplemented. NO RNG (zero seeds drawn; fleet high-water 20260775 untouched).
- `results.json` — committed output.

## Run

```
python3 sims/verdict-038-idle-economy-feel/idle_economy_feel_sim.py
```

Exit 0 iff all 77 self-checks pass (~23 s). Deterministic: stdout + results.json are
byte-identical across two full process runs (sha256 pinned in REPORT.md).
