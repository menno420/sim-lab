# Session — VERDICT 027 — claim-expiry horizons vs lane death (idea-engine PROPOSAL 025)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-027 slice-worker session
> Objective: settle idea-engine PROPOSAL 025 (control/outbox.md · 2026-07-13T04:49:44Z · status: sim-ready; idea `ideas/substrate-kit/claim-expiry-horizon-lane-death-2026-07-13.md`, the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, round 3 — the kit-planted claims doctrine after round 1's websites backlog (P019 → V021) and round 2's superbot backlog (P021 → V023)). Build the fully hermetic pre-registered measurement of whether silence-inferred claim abandonment can be tuned to be simultaneously twin-safe (T ≤ 0.05) and orphan-fast (O95 ≤ 120 h) across the fleet's activity-gap regimes and check tempos. Model: one claim per replication; an alive lane emits M+1 visible-activity events separated by i.i.d. gaps from a two-component exponential mixture — R1 burst (w 0.9 on mean 1.5 h + 0.1 on 12 h, M=6), R2 daily (0.7 on 6 h + 0.3 on 24 h, M=4), R3 weekend (0.6 on 12 h + 0.4 on 48 h, M=3); with p_d = 0.10 the lane dies silent forever after a uniformly chosen intermediate event; contenders check at Poisson rate λ_c ∈ {1/4, 1/12, 1/48} h⁻¹ (C4/C12/C48) and take over any claim silent past θ ∈ {6, 12, 24, 48, 72, 168} h — both kit-planted constants (24 h order / 72 h work, substrate-kit check_claims.py:95/:102 @ 917261b3) in-grid by design. Arm A: seedless exact closed forms (q_i(θ) = e^(−θ/m_i)·λ_c·m_i/(1+λ_c·m_i); T_A = 1−(1−Σ w_i·q_i)^M; O95_A = θ + ln(20)/λ_c — all 54 decision points, zero sampling error). Arm S: seeded event-driven MC, M_S = 4,000 per (cell, θ), seed 20260744, pinned loop order; gates |T_S−T_A| ≤ 1.0 pp and |O95_S−O95_A| ≤ max(4 h, 5%) per point; stability leg seed 20260745 (M_S = 1,000) must reproduce the ruling; reporting-only legs seed 20260746 (p_d ∈ {0.02, 0.30}, takeover chains, wasted-sessions, multi-steal); aux stream seed 20260747 (p_d = 0 zero-orphan and θ→∞ T = 0 exact-identity legs; gate diagnostics). Decision (registered order): Feas(cell) = {θ : T ≤ 0.05 AND O95 ≤ 120 h}; APPROVE iff a single θ† is feasible in ≥ 8/9 cells; REJECT iff Feas = ∅ in ≥ 5/9 cells → route the lease-renewal `renewed:` stamp slice; NULL otherwise with the flip axis named. Hermetic: zero repo/network reads at run time; byte-identical re-run on pinned cpython-3.11.

## What happened

Built `sims/verdict-027-claim-expiry/` — a stdlib-only NUMERIC SIMULATION
(rung 1), fully hermetic: the sim reads exactly one file (its own committed
`fixtures.json` pre-registration, cross-checked at start) and touches no repo
state, network, or wall clock. The pre-registration (all constants verbatim
from the idea file; nine disclosed intake-time decisions including the draw
layout, the empirical-p95 convention, and the death-position convention with
its decision-independence proof; three hand-derived pins) was committed BEFORE
the runner. A scratchpad feasibility probe ran before the fixtures commit and
is disclosed inside fixtures.json — every decision constant was pinned by the
idea file and every convention written down before the probe, so no free
parameter remained tunable.

**The one genuinely new methodological event this slice:** the closed-form SE
arithmetic, done BEFORE any run and pinned into fixtures.json
(`gate_calibration_disclosure`), showed the proposal's per-point Arm-S gates
are MISCALIBRATED at the registered M_S = 4,000 — the O95 tolerance at C48
(7.5–15.6 h) sits at 0.7–1.5σ of the empirical-p95 estimator over ~400 dead
claims (SE ≈ 10.5 h), and the 1.0 pp T tolerance sits at ~1.2–1.6σ on ~30
mid-range points — so registered-gate breaches were expected BY CONSTRUCTION.
The handling protocol was pinned before the first draw: report every gate
result as measured with predicted SE + z-score, re-measure every failing point
at 16× (M_diag = 64,000) on the aux stream, and apply the proposal's own
registered evaluation order (APPROVE → REJECT → NULL, gates conditioning
APPROVE alone) to Arm A exact values, with the "run invalid" vs done-when
conflict disclosed verbatim rather than silently resolved.

**Run output summary:** `SELF-CHECKS: 4975945 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
diff), cpython-3.11 pinned, ~6 s per run. **Ruling: REJECT — silence is the
wrong signal; route the lease-renewal `renewed:` stamp slice.** Arm A (exact):
Feas(cell) = ∅ in **6 of 9 cells** (≥ 5/9): the whole C48 column is
structurally infeasible (O95 = θ + 143.795 h > 120 h for EVERY θ ≥ 0 — a
hand-pinned identity), R3 (weekend-gapped) is infeasible in ALL THREE columns
(twin-safety needs θ = 168 h, which busts the orphan band everywhere:
O95 ≥ 179.98 h), and R2-C4 misses at every θ (θ = 72: T = 0.050244, a
0.024 pp knife-edge miss; flipping it feasible still leaves 5/9 — REJECT is
count-robust). Feasible cells: R1-C4 {48, 72}, R1-C12 {24, 48, 72}, R2-C12
{72} — best single horizon θ = 72 h covers 3/9 cells (APPROVE needed 8/9; no
θ†). Planted-constant readings: WORK_CLAIM_STALE_HOURS = 72 is the
best-covering single horizon yet covers only 3/9 cells; the 24 h order-class
constant read against the burst columns misses the twin band at C4 tempo
(T = 0.0594 > 0.05) and holds only at R1-C12. Arm S: MC decision on its own
values = REJECT with the same 6 cells; stability leg (seed 20260745) = REJECT
at 5/9 (the knife-edge R2-C4 flips under n = 1,000 noise — count-robust).
Gates as registered: 8/54 T-points + 6/54 O95-points breached (11 distinct
points, max z_T = 2.69σ, max z_O95 = 2.14σ); ALL 11 land within the same
tolerances at the 16× re-measure — sampling noise, not model disagreement;
p_d = 0 leg produced zero orphan events and the θ→∞ leg produced T = 0
exactly; per-leg draw-count sentinels all rejoined.

Slice boundary this cycle (the V015–V026 precedent): this session carries the
INTAKE 025 and VERDICT 027 control/ appends itself; control/status.md stays
coordinator-only and is untouched; control/inbox.md untouched (manager-order
file). The tail at append was VERDICT 026 @ 6526959 — numbering +2 offset
preserved (P025 → V027), origin/main re-checked immediately before the
append. No @codex step — suspended per the outbox codex-line escalation @
dedc12e. Born-red card and complete flip land in one push (the V018–V026
choreography).

## Run command

```
python3 sims/verdict-027-claim-expiry/claim_expiry_sim.py
```

## 💡 Session idea

Pre-registrations that pin BOTH a per-point tolerance AND a sample size should
be forced to show their z-arithmetic at registration time: a one-line
closed-form SE audit (tolerance ÷ predicted SE per point class) would have
revealed at drafting that max(4 h, 5%) against an empirical p95 over ~400
dead claims is a 0.7σ gate — unsatisfiable by construction, not by any model
defect. The portable rule for every future dual-arm head: register gate
tolerances as multiples of the registered-n sampling SE (e.g. "≤ 4σ of the
binomial/order-statistic SE, floored at X absolute"), or register the n that
makes the absolute tolerance ≥ 3σ; and when executing someone else's
miscalibrated gate, do the SE arithmetic BEFORE the first draw and pin the
handling protocol in the fixtures — an expected breach discovered after the
run looks like motivated reasoning; the same breach predicted in writing
before any randomness ran is just arithmetic.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-026-braess-added-edge.md`: complete and
honest; its exports are adopted here directly. (1) The one-push born-red
choreography is followed verbatim. (2) Fixtures-before-runner including
hand-derived pins with committed derivations — reused (three pins: the exact
T_A closed form at (R1, C4, θ=12); O95_A at (C12, θ=24) = 24 + 12·ln 20; and
the C48 structural-infeasibility identity θ + 48·ln 20 > 120 ∀θ, which
decides a third of the grid by hand). (3) Its "construct cheaply, verify
exactly" export — transposed: here the closed forms ARE the decision arm
(zero sampling error), and the event-driven MC is the independently-mechanised
twin; its per-claim invariants (gap positivity, latency > θ, partition
counts) run on every replication. (4) Its exact draw-count sentinel
discipline — reused per leg (fixed 2+2M uniforms per claim plus counted
check draws; fresh Random(seed) rejoins each stream exactly). (5) Its
disclosure nuance ("say why no free parameter remained tunable by the
pre-commit probe") — followed, and extended one step: this slice also
pre-disclosed the EXPECTED gate breaches from closed-form SE arithmetic
before any draw ran (fixtures `gate_calibration_disclosure`), which is the
same honesty rule applied to someone else's registration error.
