# INTAKE 003 — wild-encounter activity-spawning tuning sweep

Numeric simulation (method ladder rung 1) settling the tuning/anti-farm economics of the
Encounters subsystem for `menno420/superbot`.

- **Source idea:** idea-engine `control/outbox.md` PROPOSAL 003 (2026-07-10T20:10:06Z), pinned
  `d70a31126f5d2ce318449ab85f018e62e39e3831`; canonical
  `menno420/superbot docs/ideas/wild-encounters-activity-spawning-2026-06-20.md` @ `fd638e3`.
- **Run (one command, deterministic, stdlib-only, exit 0 iff self-checks pass):**
  ```
  python3 sims/intake-003-wild-encounter-spawn-tuning/wild_encounter_spawn_sim.py
  ```
- **Files:** `wild_encounter_spawn_sim.py` (model + sweep + 946 self-checks) · `REPORT.md`
  (the validity-gate answers + the verdict).
- **Verdict:** `needs-more-evidence` · evidence `simulation` · gate PASS on the in-scope
  spawn-frequency + anti-farm-bound claims; reward-inflation vs fishing/mining is out of scope
  (no live earn-rate baseline exists) — see REPORT.md § "What it did NOT settle".
- **Recommended launch defaults:** threshold=24 messages, debounce=30s, cooldown=900s, plus the
  one-live-spawn-per-channel / off-by-default / atomic-claim guardrails; ship with the telemetry
  list in REPORT.md so the reward-economics gap can be closed on live data.
