# Session — VERDICT 006 · SIM-001 sweep — parameter-sensitivity appendix (economy-v1)

> **Status:** `complete`
> 📊 Model: Claude Opus 4 · 2026-07-11 · VERDICT 006 sweep (follow-up) session
> Objective: close the ROBUST validity-gate half-answer on the merged VERDICT 006 sim — the
> 10/10-PASS conclusion was scored at the SINGLE provisional economy-v1 point ("only unswept
> edge: the single parameter point"). Add an honest ±20% parameter-sensitivity sweep so the gate
> answer becomes "swept, conclusion survives (with caveat)" rather than "unswept."

## What happened

Born-red card, first commit of the VERDICT 006 sweep follow-up session (heartbeat-before-work,
CONVENTIONS §"Heartbeat-before-work"; born-red per §"Born-red session card"). As a newly-ADDED
card it is the substrate-gate's advisory sentinel; the READY PR is expected to pass green once
this card is flipped to `complete` as the deliberate close-out. This is a **forward-only
follow-up PR** on top of merged main HEAD `d0afeb0` — never a rewrite of the merged verdict.

Extends `sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py` with a
`PARAMETER-SENSITIVITY SWEEP` section (new functions, base run / self-checks / determinism
untouched). The sweep constructs the engine's own `UpgradeSpec` / `PrestigeSpec` dataclasses
**directly** with perturbed field values — the provisional builders emit only the single point —
and drives the **same real engine functions** (`upgrade_cost`, `purchase_upgrade`,
`production_per_second`, `tick`/`offline_progress`, `prestige_eligible`/`prestige_award`/
`apply_prestige`); no economy math is re-implemented. Faithfulness is self-checked: at the
provisional cell the direct-spec path reproduces the base run's O1–O6 **byte-identically**.

**Load-bearing result:** across a ±20% sweep of all 7 parameters (each ×{0.8,0.9,1.0,1.1,1.2},
plus two all-move corners), the 10/10 conclusion **survives ±20% on 6 of 7 parameters** but is
**NOT uniformly robust**: the **growth ratio** is a one-sided downside cliff —
`cost(L)=base·ratio^L` compounds over ~40 levels, so the `×0.9` growth cell (ratio `1.15→1.04`)
collapses the curve and **flips A3 (S3 first-prestige 1.56 h < [2,8] h) and A6 (A4/A3 17.8× >
[4,12]×)**; growth `×0.8` (ratio 0.92) is INFEASIBLE (engine `num<den` guard). The all-`×1.2`
corner is 9/10 (A7). base_cost / effect / threshold / bonus each hold 10/10 across the full
±20% range. Verdict stays **approve at the pinned point** with a **robustness caveat** (pin
growth 1.15 as a near-floor); routing call handed to the fleet manager. Self-checks: **70
passed, 0 failed** (62 base + 8 sweep).

## Run command

```
python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py
```
Deterministic, stdlib-only, exit 0 iff every self-check passes. Prints O1–O6, the A1–A10
scorecard, the new PARAMETER-SENSITIVITY SWEEP appendix (full grid + corners + headline), and
the terminal `SELF-CHECKS: n passed, 0 failed` line; the whole sweep is run twice and asserted
byte-identical, and every reported cell value is reproducible.

## 💡 Session idea

A **direct-spec sweep harness over a byte-vendored pure engine** is a reusable rung-1 pattern:
when the provisional-config builders emit only one point, you sweep by constructing the engine's
own frozen dataclasses with perturbed fields and driving the *same* functions — then prove
faithfulness by asserting the provisional cell reproduces the base run byte-for-byte. That single
equality check turns "I re-scored off-point" from a trust-me into a proof, and makes an honest
anti-cherry-pick sweep (report the FULL grid, headline the first flip) cheap for any deterministic
kernel. The standing candidate for `harness/`: a `sweep(spec_fields, engine_call)` helper paired
with a `reproduces_base` assertion.

## ⟲ Previous-session review

VERDICT 006 (base) drove the REAL pinned engine and scored A1–A10 at the single PROVISIONAL
point, honestly flagging in its own gate 3 that "the one edge the criteria do not probe is the
parameter grid itself (only the single PROVISIONAL point is run)." This follow-up closes exactly
that gap with the discipline the base session set: drive the real artifact (never a
re-implementation), report the whole grid not the best cell, and treat a flip as a headline not a
footnote — which is why the growth-`×0.9` flip is the lead finding, not a buried caveat, and the
approval is now explicitly *qualified* rather than silently strengthened.
