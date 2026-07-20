# VERDICT 247 reproduction mirror — put-call parity (binomial), PROPOSAL 234

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 247 slice. This mirror does NOT advance the verdict high-water.

**Source proposal:** idea-engine PROPOSAL 234 (venture-lab · option/portfolio identity)
**Lane:** P234 → V247 (+13 offset)
**Verifier:** `verify_234_put_call_parity.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 637c7b8a0b3a12090d377c4cf10994d81880aed0095bc3966a8a9328b587ede4`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 exact parity (Fraction, 4-market panel): PASS
- G2 MC agreement (400000 trials): z = −0.112845, |z| < 3 → PASS
- G3 invariance (volatility + scale): PASS
- G4 falsifiability (naive undiscounted-strike rejected): z_naive = 246.993214, |z| ≥ 6 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = sim-ready

## Claim reproduced

C − P = S₀ − K·R⁻ⁿ exactly in a no-arbitrage binomial market; reference S₀=K=100, u=2, d=1/2, R=5/4, n=2 ⇒ C=48, P=12, C−P=36=100−64.

## Verifier source integrity

Byte-identical to idea-engine `ideas/venture-lab/verify_234_put_call_parity.py` (source sha256 `fb45a5cc536eb03b70669427eb598aeb73f5ebdbcd69b7a22b0b574e5c37c8ae`).
