# verdict-077 — cascade independence quota (INTAKE 064)

Prices idea-engine PROPOSAL 064's folk claim where it lives: "more visible
history never hurts — the crowd self-corrects." In the pinned
Bikhchandani–Hirshleifer–Welch world (binary state, prior 1/2, i.i.d. signals
correct w.p. p, agents acting in order on all prior ACTIONS plus own signal,
follow-own-signal tie-break), full transparency locks the crowd into a
cascade after ~2/(1 − 2pq) actions and caps accuracy at the N-INDEPENDENT
constant 1 − q²/(1 − 2pq). The priced counter-mechanism is a mandated
blind-first INDEPENDENCE QUOTA k (the first k actors follow their own
signal, indices public), judged against pre-registered bands at the decision
cell (p = 7/10, N = 100): REJECT-first (G ≥ 6 AND k* ≥ 5 AND
e(k*) ≤ e(0)/2, all exact), APPROVE (G ≤ 2 AND k* ≤ 2), NULL otherwise on
named axes, INVALID on any F1–F6 gate failure. Three hand-proved structure
theorems ride as gates: QUOTA-NULL (k ∈ {0, 1, 2} change nothing), PARITY
(e(2m+1) = e(2m+2) — optimal panels are ODD), KNIFE-EDGE (the quota's
long-run leverage lives entirely at the cascade boundary ±2, closed form).
Fully hermetic: the runner reads ONLY `fixtures.json` (committed before the
runner); zero repo/network reads at verdict time.

## Run

```
python3 sims/verdict-077-cascade-independence-quota/cascade_independence_quota_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). Stdlib-only. Every decision number is a seedless exact
`fractions.Fraction`; the only seeded arm (R) is reporting-only with NO
statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 064
  block / idea doc (the p grid {11/20, 7/10, 4/5, 9/10} with decision cell
  7/10 and controls {1/2, 1}; N ∈ {25, 100, 400} with decision cell 100; the
  quota window {0..min(N, 120)} with interiority bound 118; the
  follow-own-signal tie-break token; the decision constants {6, 2, 5, 2,
  1/2-halving}; the F2–F5 anchors incl. 441/14500; Arm-R parameters and
  seeds 20261563–566), plus fixture-level conventions C1–C12 and the
  drafter's disclosed landing (compared, never gated) — committed BEFORE the
  runner existed.
- `cascade_independence_quota_sim.py` — three-arm runner: Arm A seedless
  exact forward absorbing-walk DP (decision-bearing), Arm B
  independently-written backward memoized recursion + Gaussian-elimination
  ruin solve (exact-equal on every published number; second decision
  evaluator), the algorithm-free 2^12 path census at N = 12, and Arm R
  seeded reporting-only traces of the literal 100-agent process.
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, tables, theorem verifications, gates, reporting
  legs, boundaries, the pre-registered consequence.

## Ruling

See REPORT.md (written from the accepted run; the ruling token is issued by
the twin evaluators per the pre-registered order REJECT → INVALID → APPROVE
→ NULL).
