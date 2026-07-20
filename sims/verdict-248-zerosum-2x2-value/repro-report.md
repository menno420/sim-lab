# VERDICT 248 reproduction mirror — value of a 2×2 zero-sum game (von Neumann minimax), PROPOSAL 235

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 248 slice. This mirror does NOT advance the verdict high-water.

**Source proposal:** idea-engine PROPOSAL 235 (fleet · game-theory value identity)
**Lane:** P235 → V248 (+13 offset)
**Verifier:** `verify_235_zerosum_2x2_value.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = a8d766a845b4cd53518fc572f30041dfb154148a67f399c39463476ec1e4276a`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 exact value identity (Fraction, 4-game no-saddle panel + saddle cross-check): PASS
- G2 MC agreement (400000 trials): z = 0.345941, |z| < 3 → PASS
- G3 invariance (minimax guarantee + affine): PASS
- G4 falsifiability (naive "value == pure security level = −1" rejected): z_naive = 462.564053, |z| ≥ 6 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = sim-ready

## Claim reproduced

For a 2×2 zero-sum game M = [[a, b], [c, d]] with no pure saddle point, the value is exactly v = (a·d − b·c)/(a + d − b − c), attained by row = ((d−c)/g, ·) and column = ((d−b)/g, ·) with g = a + d − b − c. For the reference matrix M = [[3, −1], [−2, 1]] the value is v = 1/7 with row = (3/7, 4/7), column = (2/7, 5/7); the pure-strategy security level (maximin) is only −1, strictly below v, so the naive "value == security level" rule is wrong.

## Verifier source integrity

Byte-identical to idea-engine `ideas/fleet/verify_235_zerosum_2x2_value.py` (source sha256 `cb1a12b1e253e727f851e89c874f1e0cb179c328030104c1cad84b92fb7b8dcb`).
