# verdict-027 · claim-expiry

Is any silence horizon θ simultaneously twin-safe (T ≤ 0.05) and orphan-fast
(O95 ≤ 120 h) across the activity-gap regimes and check tempos the fleet
spans — and if so, are the kit-planted 24 h / 72 h constants in the feasible
window? Answers idea-engine PROPOSAL 025 (control/outbox.md
2026-07-13T04:49:44Z, idea
`ideas/substrate-kit/claim-expiry-horizon-lane-death-2026-07-13.md`, landed
via idea-engine PR #291, main `a123fda`) — the ORDER 004 rule-3
FLEET-BACKLOGS rotation slot, round 3: the kit-planted claims doctrine, after
round 1's websites backlog (P019 → V021) and round 2's superbot backlog
(P021 → V023). Fully hermetic per the PROPOSAL 017–024 precedent: every
fixture is a pinned constant committed with the sim; zero repo/network reads
in the verdict session.

Model: the silence-expiry race — one claim per replication; an alive lane
emits M+1 visible-activity events separated by i.i.d. gaps from a
two-component exponential mixture (R1 burst w=(0.9,0.1) m=(1.5,12) h M=6 ·
R2 daily (0.7,0.3) (6,24) M=4 · R3 weekend (0.6,0.4) (12,48) M=3); with
p_d = 0.10 the lane instead dies silent forever after a uniformly chosen
intermediate event; contenders check at Poisson rate λ_c ∈ {1/4, 1/12, 1/48}
h⁻¹ (C4/C12/C48) and take over any claim silent past θ ∈ {6, 12, 24, 48, 72,
168} h — both kit-planted constants in-grid. Metrics per (cell, θ): **T** =
P(alive-throughout claim stolen before completion) and **O95** = p95
death→takeover latency for dead claims. **Arm A** (decision-carrying):
seedless exact closed forms — q_i(θ) = e^(−θ/m_i)·λ_c·m_i/(1+λ_c·m_i),
T_A = 1−(1−Σ w_i·q_i)^M, O95_A = θ + ln(20)/λ_c — all 54 points, zero
sampling error. **Arm S**: seeded event-driven MC, M_S = 4,000 per point,
`random.Random(20260744)`, pinned loop order and draw layout; per-point
gates |T_S−T_A| ≤ 1.0 pp and |O95_S−O95_A| ≤ max(4 h, 5%); stability leg
seed 20260745; reporting-only legs seed 20260746; aux stream seed 20260747.
Decision (registered order): Feas(cell) = {θ : T ≤ 0.05 AND O95 ≤ 120 h};
APPROVE iff one θ† feasible in ≥ 8/9 cells; REJECT iff Feas = ∅ in ≥ 5/9;
NULL otherwise.

## Run (one command)

```
python3 sims/verdict-027-claim-expiry/claim_expiry_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — Arm A is closed-form with no
PRNG; Arm S consumes a fixed 2+2M uniforms per claim plus counted check
inter-arrival draws, audited by fresh-Random(seed) stream-rejoin sentinels
per leg. No network, no git, no wall clock, no `hash()`. stdout and
`results.json` are byte-identical across process runs (verified by external
`diff` of two complete runs, cpython-3.11 pinned and asserted). Progress goes
to stderr only.

## Files

- `claim_expiry_sim.py` — stdlib-only driver: exact closed forms (Arm A) +
  event-driven MC (Arm S) + gates with predicted-SE/z-score columns +
  stability leg + reporting legs (p_d sensitivity, takeover chains,
  wasted-sessions, multi-steal) + aux exact-identity legs (p_d = 0 → zero
  orphans; θ→∞ → T = 0 exactly) + 16× gate diagnostics; three hand-derived
  pins asserted.
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file, the bands and decision rule, nine
  disclosed intake-time decisions, the three hand pins, and the
  gate-calibration SE disclosure written before any run.
- `results.json` — committed run output: both full {T, O95} × (cell, θ)
  tables, Feas/θ*/coverage, per-point gate rows, stability and reporting
  legs, diagnostics, ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the
  VERDICT 027 ruling).

## Verdict (summary — full report in REPORT.md)

**reject (the pre-registered ≥ 5/9 infeasibility condition, met at 6/9 —
finalized)** — silence is the wrong signal: no horizon in the grid is
simultaneously twin-safe and orphan-fast outside a burst/standard-tempo
corner, so the routed build is the lease-renewal `renewed:` stamp slice:

- **Arm A (exact):** Feas = ∅ in **6/9 cells** — the entire C48 column is
  structurally infeasible (O95 = θ + 143.795 h > 120 h for every θ ≥ 0, a
  hand-pinned identity); R3 weekend-gapped is infeasible in all three columns
  (twin-safety needs θ = 168, which busts the orphan band: O95 ≥ 179.98 h);
  R2-C4 misses everywhere (θ = 72: T = 0.050244 — a 0.024 pp knife-edge miss
  that cannot flip the ruling: flipping it gives 5/9, still REJECT).
- **Feasible cells:** R1-C4 {48, 72} (θ* = 48), R1-C12 {24, 48, 72}
  (θ* = 24), R2-C12 {72} (θ* = 72). Best single horizon θ = 72 covers 3/9
  (APPROVE needed 8/9 — no θ† exists).
- **Planted constants:** 72 h is the best-covering single horizon yet covers
  only 3/9 cells; the 24 h order-class reading misses the twin band at burst
  check tempo (R1-C4: T = 0.0594 > 0.05) and holds only at R1-C12.
- **Arm S:** MC decision on its own values = REJECT, same 6 cells; stability
  leg (seed 20260745, n = 1,000) = REJECT at 5/9. Registered per-point gates:
  8/54 T + 6/54 O95 breaches on 11 points (max z 2.69σ / 2.14σ) — ALL within
  tolerance at the 16× re-measure; the breaches were predicted from
  closed-form SE arithmetic BEFORE any run (fixtures
  `gate_calibration_disclosure`): the registered tolerances sit at 0.7–1.6σ
  of the registered-M_S estimators, a pre-registration calibration artifact,
  not model disagreement.
- **Model basis (declared):** exponential-mixture gaps × Poisson checks; the
  named most-likely-to-flip alternative is the empirically measured gap
  distribution — deliberately the same `git log --diff-filter=AD` probe the
  NULL case would have shipped.

4,975,945 self-checks, 0 failed; stdout + results.json byte-identical across
two full process runs by external diff on cpython-3.11; ~6 s per run.
