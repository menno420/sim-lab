# VERDICT 006 — idle-economy sim kernel (SIM-001 / economy-v1)

NUMERIC SIMULATION (ladder rung 1) settling **SIM-001**: do the PROVISIONAL
economy-v1 parameters hit their pre-registered pacing targets (A1–A10) on the
reference world? It **drives the REAL pinned engine** — the `idle_engine/`
package here is a byte-for-byte VENDOR COPY of `menno420/superbot-idle`
`idle_engine/` @ `f11c71a52d4d2adf88b2bf11f5d1134bad495be2` (only `__init__.py`
is reconstructed, re-exporting the five vendored modules; the economy/mechanics
logic is untouched). A re-implementation was explicitly unwanted — float/rounding
drift would invalidate the run — so the sim `import`s the engine and calls its
own `tick`, `offline_progress`, `purchase_upgrade`, `upgrade_cost`,
`prestige_eligible`, `prestige_award`, `apply_prestige`, `production_per_second`,
`build_upgrade_spec`, `build_prestige_spec`.

**Verdict (mechanical): `10/10 PASS` → approve — graduate the PROVISIONAL
parameter table PROVISIONAL → SIM-PINNED.** `[COORDINATOR TO FINALIZE]` — the
coordinator finalizes VERDICT 006 and the heartbeat after reviewing the numbers.

Source idea: `menno420/idea-engine` `control/outbox.md` PROPOSAL 006 @
`7df1d6cd09d52ad8574b6f37adf00abb99179f5e`, relaying superbot-idle **SIM-001**
from `docs/design/economy-v1.md` @ `f11c71a52d4d2adf88b2bf11f5d1134bad495be2`.

## One run command
```
python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py
```
Deterministic, stdlib-only, no RNG. A single run per scenario **is** the
distribution (the engine is pure and integer-exact); determinism is proven by
byte-identical re-run of every scenario, not by seeds. Exit 0 iff every
self-check passes (**62 this cycle**). Prints the O1–O6 tables, the A1–A10
scorecard, and the terminal `SELF-CHECKS: n passed, 0 failed` line. Runs in < 1 s.

## What it models
The economy-v1 **reference world**: one generator `tier1` (`base_rate=1`, count
fixed at 1), one upgrade ladder `boost1` (geometric cost `60·115^L//100^L`,
+25%/level additive), one prestige track (threshold/divisor 100 000,
`isqrt(lifetime//divisor)` award, +10%/unit bonus). Per-second integer rate =
`base·count·(100+25U)·(100+10P)//10000`. Three scenarios: **S1** idle-only,
**S2** check-in every N∈{0.25,2,8,24} h (credit → greedy-buy → prestige-iff-eligible),
**S3** the same policy at 1-second granularity (plus additive **S3b** threshold
policy). Horizon 14 simulated days; O6 slices the first 20 S3 resets.

## Files
- `REPORT.md` — the live verdict (8-section, all five validity-gate answers).
- `idle_economy_sim.py` — the deterministic driver (scenarios + O1–O6 + scorecard + self-checks).
- `idle_engine/` — the VENDORED pinned engine (5 modules byte-copied; `__init__.py` reconstructed).

## Reference-world note (not an engine edit)
`apply_prestige` wipes `owned` (correct: a reset clears the run). economy-v1.md
§ Reference world states a fresh save *starts owning* tier1 (count fixed at 1,
no generator-purchase path exists). The driver therefore re-seeds
`owned={"tier1":1}` on every fresh save after a reset — a **reference-world
rule**, applied in the driver, never a change to the vendored engine.
