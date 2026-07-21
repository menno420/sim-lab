# VERDICT 273 reproduction mirror — Wilson's theorem: (n−1)! ≡ −1 (mod n) ⟺ n prime, PROPOSAL 260

> **Status:** reproduction-only — ruling deferred to the coordinator-driven VERDICT slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 260 (PR #894, squash merge SHA b40d9aedd320c3eab92355acd446c87ad6e5f1a2)
**Lane:** P260 → V273 (+13 offset)
**Verifier:** `verify_260_wilsons_theorem.py` (byte-identical copy of the firsthand idea-engine verifier `ideas/fleet/verify_260_wilsons_theorem.py`; stdlib only: argparse, hashlib, json, math, random, fractions, sys)
**SEED:** 20260721

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 938969bc60f733cea8c9e79e5a29a7b062e661de10619aa8bcdf61719e9ba474` — byte-identical to the idea-engine source digest.
- determinism: default run · in-process double-run (byte-identical) · separate re-invocation — all byte-identical.
- **G1 EXACT (integer/bignum, zero tolerance)** — the Wilson predicate `[(n−1)! ≡ −1 (mod n)]` equals an independent trial-division primality test on every `n` in `[2,1500]` (`checked = 1499`, `mismatches = 0`), and the iterated-mod residue equals the exact full-bignum factorial residue `math.factorial(n−1) % n` on `[2,400]` (`bignum_mismatches = 0`). Direction: exact biconditional ⇔ independent primality → PASS
- **G2 MC agreement (`|z| < 3`)** — `N = 200000` iid uniform draws of `n` in `[2,1500]`; the empirical Wilson-predicate density matches the independently-computed exact prime density `π(1500)/1499 = 239/1499 ≈ 0.159440` (`π(1500) = 239`); `hits = 31622`, `p̂ = 0.158110`, binomial `z = −1.624284`; `|z| < 3` → PASS
- **G3 invariance / robustness (0 violations)** — every composite `n > 4` satisfies `(n−1)! ≡ 0 (mod n)`: `composite_nonzero_exceptions = []`, and the sole composite exception is `n = 4` with residue `n4_residue = 2` (`3! = 6 ≡ 2 (mod 4)`). Direction: composite-side structural invariant → PASS
- **G4 falsifiability (`|z| > 3`)** — the sign-flipped foil `(n−1)! ≡ +1 (mod n) ⟺ prime` has empirical density `0.000675` (`foil_hits = 135`) against the true prime density, `z_foil = −193.948379`; on the SAME population the true predicate matches at `z = −1.624284`. Direction: refute a plausible-but-wrong rule → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

For every integer `n ≥ 2`, `(n−1)! ≡ −1 (mod n)` if and only if `n` is prime — equivalently the residue `(n−1)! mod n` is `n−1` on the primes and `0` on every composite `n > 4`, the sole composite exception being `n = 4` (`3! = 6 ≡ 2 (mod 4)`). Reproduced here by forcing two independent oracles to agree: an exact iterated-modular factorial residue and an independent trial-division primality test, cross-checked against the full-bignum factorial. Exact equivalence holds with zero mismatches across `[2,1500]`, the predicate's density matches Monte-Carlo inside 3σ, and the sign-flip (`≡ +1`) foil is rejected far beyond 3σ while the true predicate makes zero errors. Anchors include the Carmichael numbers 561 and 1105 (both fool the Fermat primality test yet Wilson correctly classifies them composite).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_260_wilsons_theorem.py` (verifier file sha256 `bac228b1bd774d8a5866ae76f3581488b648151caa40ef988f26f6afc59ee609`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction; stdlib-only, no network, SEED hardcoded. `build_results()` is a pure function of SEED and the fixed parameters (no wall clock, no hostname, no unseeded randomness; the sampling gate draws from a fixed `random.Random(SEED)`; every float enters via a fixed 6-dp format string, every count as an int, every fraction as "num/den"), so the in-process double-run and the separate re-invocation are byte-identical and `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned source reference (Wikipedia "Wilson's theorem", oldid 1334572197) and the quoted/derived split live with the source PROPOSAL 260, and the canonical grounding review belongs to the coordinator-driven VERDICT 273 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 273 slice, not here._
