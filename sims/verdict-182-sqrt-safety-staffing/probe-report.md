# verdict-182 — sqrt safety staffing: independent-audit checklist

Mechanical reproduction of the idea-engine verifier `sqrt_safety_staffing.py`.
Factual record only; no verdict rendered here.

## Artifact identity

- File: `sims/verdict-182-sqrt-safety-staffing/sqrt_safety_staffing.py`
- sha256: `3f5fda4c41f3ed2a7c3526136483a0edd2a8436cbddde3a43f5a2db89b3ce6cc`
- git blob (`git hash-object`): `92377e7524bf8ac0486131e10d78c3f52c299de4`
- Byte-identity to idea-engine original (`ie/ideas/fleet/sqrt_safety_staffing.py`):
  `diff` exit code = **0** (byte-identical).

## Determinism

- Fixed seed: `SEED=20260717`.
- Invocation 1 exit code: **0**.
- Invocation 2 exit code: **0**.
- Cross-invocation stdout `diff` exit code: **0** (byte-identical across
  separate process invocations).
- In-process double-run: the script's `__main__` calls `run()` twice
  (`r1 = run()`, `r2 = run()`) and asserts `canonical(r1) == canonical(r2)`
  ("non-deterministic run()"). Exit 0 confirms the assertion held. No separate
  "invocation 1/2" line is printed to stdout; the equality is enforced by the
  in-process assertion, and the disclosed sha256 is taken over `canonical(r1)`.

## Results-JSON digest

- Reported Results-JSON sha256:
  `2597a50513127f663123c741aaca2bf646198035388a3325cbf4706e29092de8`
- Expected:
  `2597a50513127f663123c741aaca2bf646198035388a3325cbf4706e29092de8`
- Comparison: **MATCH**

## Aggregate

- `all_pass`: **true**

## Gates (observed vs pre-registered thresholds)

### G1 — pooling / decoupling (exact, Erlang-C)
- `pass`: **true**
- R = 1024, rho = 0.98367
- per_unit_slack = **0.016602** (pre-registered reference: 0.016602)
- erlangC_pwait = 0.48514, mm1_pwait_same_rho = 0.98367, effect = 0.49853

### G2 — square-root staffing form
- `pass`: **true**
- headroom_over_sqrtR at R_max = **0.53125**
- beta = 0.506054
- gap = **0.025196** (< 0.05 threshold) — pre-registered: 0.53125 vs
  beta 0.506054, gap 0.025196 < 0.05

### G3 — hyperexponential robustness (replicated DES)
- `pass`: **true**
- R = 64, rho = 0.927536
- z = **15.418819** (>= z_gate 3.0) — pre-registered: z ≈ 15.42 >= 3
- des_h2_pwait (mean P{wait}_H2) = **0.494776** (< 0.9 saturation bound) —
  pre-registered: 0.494776 < 0.9
- des_h2_se = 0.028067, effect = 0.43276

## Meta (from output)

- seed = 20260717, count = 25000, warmup = 15000, reps = 15
- alpha_target = 0.5, beta = 0.506054, z_gate = 3.0
- ledger_loads = [16, 64, 256, 1024], des_loads = [16, 64]
- des_matches_exact_within_3sigma = true
- grounding: Gans-Koole-Mandelbaum sec 4.1.1, eqs 14-15
  (https://www.columbia.edu/~ww2040/tutorial.pdf)
