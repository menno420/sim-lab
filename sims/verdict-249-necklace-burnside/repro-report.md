# VERDICT 249 reproduction mirror — counting necklaces under rotation (cyclic group C_n orbit count), PROPOSAL 236

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling and the external Wikipedia grounding are deferred to the coordinator-driven VERDICT 249 slice. This mirror does NOT advance the verdict high-water and deliberately omits the grounding pin per the mirror convention.

**Source proposal:** idea-engine PROPOSAL 236 (fleet · combinatorics / group-action orbit count)
**Lane:** P236 → V249 (+13 offset)
**Verifier:** `verify_236_necklace_burnside.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 4ce987eb3da551811389d54d5d70f72ec27cadcd8600efc73320ad9860938ece`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 exact orbit count (Fraction, 5-instance panel; closed form == brute min-rotation enumeration == expected, denominator 1): PASS
- G2 MC agreement (400000 uniform colourings of (6,3), N_hat = 129.934834): z = −0.842145, |z| < 3 → PASS
- G3 invariance (orbit count invariant to a colour relabel, cyclic +1 mod k): PASS
- G4 falsifiability (naive "N == k^n/n = 121.5" rejected): z_reject = 109.003526, |z| ≥ 6 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

The number of distinct necklaces of n beads in k colours, counting two colourings equivalent when one is a rotation of the other (the cyclic group C_n acting on bead positions), is the exact integer N_k(n) = (1/n)·Σ_{d|n} φ(d)·k^(n/d), where φ is Euler's totient. For the headline n = 6, k = 3: (1/6)[φ(1)·3^6 + φ(2)·3^3 + φ(3)·3^2 + φ(6)·3^1] = (1/6)[729+27+18+6] = 780/6 = 130 exactly. The naive "divide by the group order" rule N = k^n/n = 729/6 = 121.5 is provably wrong (not even an integer; it ignores the non-free orbits — the constant and shorter-period colourings whose orbits are smaller than n).

## Verifier source integrity

Byte-identical to idea-engine `ideas/fleet/verify_236_necklace_burnside.py` (source sha256 `6a78c77ae7fa7d412a57bc834993f91674e0e9b059ce73237bdd063331cc2302`; landed on idea-engine origin/main via PR #844, merge commit ab34f8ff7d5418cbcb782fccaacf124bde3f963f).
