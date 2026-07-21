# VERDICT 250 reproduction mirror — slotted-ALOHA finite-n throughput ceiling, PROPOSAL 237

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling and the external Wikipedia grounding are deferred to the coordinator-driven VERDICT 250 slice. This mirror does NOT advance the verdict high-water and deliberately omits the grounding pin per the mirror convention.

**Source proposal:** idea-engine PROPOSAL 237 (fleet · random-access channel throughput / finite-n ceiling)
**Lane:** P237 → V250 (+13 offset)
**Verifier:** `verify_237_slotted_aloha.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = fb72d76e05c3e41d3f671f7d324a76dde84ea815a6360be1652508db4fc0cb9a`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 exact rational identity (S(n,p)=n·p·(1−p)^(n−1) maximised at p*=1/n; ceiling as an exact rational): error 0 → PASS
- G2 Monte-Carlo agreement (empirical throughput at p*=1/n vs. closed form): max |z| = 2.2817 (< 3) → PASS
- G3 relabeling invariance + exact monotone-decrease of S_max(n) + strict 1/e lower bound: PASS
- G4 falsifiability (naive "throughput == offered load == 1.0" rejected): min |z| = 445.44 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

For n stations each transmitting in a slot independently with probability p, the single-slot success throughput is S(n,p) = n·p·(1−p)^(n−1). It is maximised at p* = 1/n, giving the exact finite-n ceiling S_max(n) = (1−1/n)^(n−1) = (n−1)^(n−1)/n^(n−1), which decreases monotonically toward the limit 1/e ≈ 0.367879 as n → ∞. The naive "throughput equals the offered load = 1.0" rule (every station transmitting always, so the channel is saturated to unit throughput) is provably wrong: it ignores collisions, which drive success throughput strictly below the finite-n ceiling and toward 1/e.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_237_slotted_aloha.py` (verifier file sha256 `dd6974d391ace15980b4c99001a3fc17bd791b97409425fd6b3cf9079bde4c85`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded.

---

_Reproduction-only mirror; the canonical grounding and the APPROVE/QUALIFIED/REJECT ruling live in the idea-engine PROPOSAL 237 and the coordinator-driven VERDICT 250 slice, not here._
