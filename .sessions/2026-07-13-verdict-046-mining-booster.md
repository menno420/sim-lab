# Session — VERDICT 046 — mining booster bypass: can a committed-shape cap make the energy throttle bind again? (idea-engine PROPOSAL 035, game-mechanics round 5)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-046 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 035 (2026-07-13T12:12:40Z, status sim-ready, landed idea-engine PR #308; claim landed idea-engine PR #310 → main 9495f7d; offset map PROPOSAL 035 → VERDICT 046 per docs/current-state.md) — "mining booster bypass / throttle seal": V042 (mining economy, approve) measured REPORTING-ONLY that rations (20 coins → 25 energy) and energy drinks (40 → 50) price energy at 4/5 coins per dig, below the faucet at every committed depth row, making boosted active play a coin-profitable ×4.45 (37535/8427) bypass of the lane's ONLY pacing control (the 360/h regen throttle). This head swept the two committed-shape lever families — REPRICE (excluded by the registered arithmetic 11325/896 vs 48/7, rides reporting-only) and the booster-admission CAP C ∈ {60, 75, 100, 125} effective energy/window × window semantics ∈ {sliding-3600 s, fixed-hour} — against three pre-registered bands (SEAL 5/4 · REFILL C ≥ 60 ∧ cost ≤ 2880/7 · PACE ≥ 0.8× the parent's committed Forge anchors) on the parent's own byte-copied engine subtree (13 files @ packet pin 57f69be3, sha256 MANIFEST re-verified before import — zero fresh clones). Every anchor machine-read from `sims/verdict-042-mining-economy/{results,fixtures}.json` and the V043 755/56 hand-pin at the branch base (origin/main c2c90f6). Decision rule pre-registered in fixtures.json BEFORE the runner, evaluated REJECT → APPROVE → NULL. Seeds 20261281–84, strictly above the fleet high-water 20261280; new high-water 20261284. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine untouched.

## What happened

Built `sims/verdict-046-mining-booster-bypass/` — engine byte-copied from the
parent V042 subtree (MANIFEST re-verified 13/13 before copy AND at runtime),
`fixtures.json` (anchors machine-read by a build-time extractor, never
transcribed; 18-cell enumeration, effective-energy admission accounting
forced by the registered drink-mix invariance gate, bands, decision rule,
seeds) committed BEFORE the runner; one pre-run amendment (ladder tolerance
120→180 s, the C=60 cap-touch identity band — engine truths found by code
reading) committed before any execution. Git trail: e72deb9 (card) → b243045
(engine+fixtures) → f9a3b93 (amendment+runner) → dc53307 (accepted run).

**Run:** `SELF-CHECKS: 110 passed, 0 failed`, exit 0; stdout + results.json
byte-identical across two full process runs by external diff; ~65 s/run;
B0 all 37 anchors exact (incl. 755/56 re-derived through the engine, both
bypass ratios, both Forge anchors via the parent's own 10D−480 accounting).

**Fix-forward (disclosed in REPORT.md):** run 1 breached 4 pre-registered
gates — all pipeline defects, none physics: the greedy adversary lacked the
hold-to-top-up move (sliding C=60 admitted 410, not 8C), the C=∞ gate as
first written contradicted the fixture's own registered terminal-absorption
rule (14389 digs/8 h is correct adversary behaviour), and the Arm-A fluid
predictor needed the purchase-cascade model. Fixed, re-run, all gates green;
the sole decision-table delta (C=60-sliding admitted 410→480) moved AWAY
from the ruling's fragile direction.

**Ruling: null** (the pre-registered single-cell arm). C=60 is the ONLY
decision cell passing SEAL+REFILL+PACE — in BOTH semantics (ceiling ρ 1.1512
sliding / 1.1498 fixed; PACE FI 0.8193, FII 0.8331/0.8339). The registered
APPROVE expectation (sliding {60,75}) did NOT survive the measured **ladder
front-load premium**: C=75's Forge I lands 0.7789 vs the 0.8 band where the
sustained-rate closed form predicted 0.8329 (−5.4 pp — a greedy climber
consumes each window's whole cap immediately, and Forge I ≈ 439 digs is
barely one window). C ∈ {100, 125} fail SEAL at the ceiling row (1.2560 /
1.3201 > 5/4) plus PACE. Semantics measured INERT on means, LIVE on the
worst-window audit (fixed leaks 2C = 120 bursts at C=60, peak-window ρ
1.3136; sliding audited ≤ C everywhere). REPRICE realized its registered
exclusion by measurement; casual play (2392 digs/8 h, 16 refills) is
byte-identical at every cell — the cap taxes only the farmer. Stability
(seed 20261282, half M, full table rebuild) reproduces null; twin evaluators
agree. Named live probe: shop telemetry. Re-drawn-line option shipped: at
PACE ≥ 0.775 the {60,75} band passes — a re-drawn line re-reads, never
re-runs.

Landed INTAKE 035 + VERDICT 046 in `control/outbox.md` (append-only; the
INTAKE ledgered in the outbox per the standing INTAKE 014–034 convention —
`control/inbox.md` is the manager-order file, one writer, untouched).
`python3 bootstrap.py check --strict` exit 0 at flip. PR:
https://github.com/menno420/sim-lab/pull/96 (READY; merge-on-green owns the
merge — zero agent merge calls).

## 💡 Session idea

Direction-aware breach protocol: when a pre-registered gate fails on the
first run, the fix classifies itself by which way it moves the result
relative to the registered FRAGILE direction. If the fix moves the table
AWAY from the fragile ruling (here: hold-to-top-up raised C=60-sliding's
admitted energy, strengthening the cell the null already rested on),
fix-forward + disclosure is safe and cheap; if it would move TOWARD the
fragile ruling, stop and re-register (fresh commit, stated rationale) before
re-running, because that is exactly the corridor where pipeline "fixes" can
smuggle in outcome shopping. Prior cards registered fragile directions for
LIVENESS; encoding the same axis into the gate-breach protocol turns an
integrity judgment call into a mechanical rule. Portable to every sim with
pre-registered gates.

## ⟲ Previous-session review

VERDICT 045 (exploration bands, PR #93) is the direct predecessor. Its
NULL-plus-instrument discipline transferred here whole: this null ships the
re-drawn-line table and the telemetry probe the same way V045 shipped its
capability-gap lookup tables. Its drive-the-packet's-own-code move became
this session's rule — energy.py's settle/spend/restore drove every timeline,
so the throttle physics were never reimplemented. One honest criticism: the
V045 card's Objective paragraph compresses nearly the entire verdict into a
single ~40-line sentence, which makes the card grammar pass but costs the
next reader the scan; this card keeps the Objective to the registration and
moves every number into "What happened", which reads faster. Guard recipe
carried from its precedent stack (V042's MANIFEST + closed-form-prediction
discipline): when a fixture pins an identity the engine can silently break
(here `settle()` resetting the regen remainder at the energy cap —
`engine/games/mining/core/energy.py::settle`, exercised by the farmer
identity gate in `booster_bypass_sim.py::build_decision_cells`), register
the identity as a BAND with the mechanism named, not as bare equality.
