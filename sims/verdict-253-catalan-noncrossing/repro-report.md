# VERDICT 253 reproduction mirror — Catalan numbers count non-crossing handshakes, PROPOSAL 240

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 253 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 240 (fleet · enumerative combinatorics / non-crossing perfect matchings (Catalan))
**Lane:** P240 → V253 (+13 offset)
**Verifier:** `verify_240_catalan_noncrossing.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions, itertools)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 6b7c1a8ba3ca4a96e91ca5405c089cb037d3cf32d933fcf20b508e5f8faf24bf`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 EXACT — closed form == brute force, exact rational via `fractions.Fraction`. For n ∈ {2,3,4,5,6} the three Catalan routes (recurrence, binom(2n,n)/(n+1), binom(2n,n)−binom(2n,n+1)) agree exactly; for n ∈ {2,3,4} the code enumerates all (2n−1)!! perfect matchings, counts the non-crossing ones, and asserts total == (2n−1)!! and non-crossing == C_n, with P_brute = Fraction(non_crossing, total) equal to Fraction(C_n, (2n−1)!!) exactly; error_count = 0; P_exact = {2: 2/3, 3: 1/3, 4: 2/15} → PASS
- G2 Monte-Carlo agreement — 200 000 uniform random matchings per estimate; for n = 3 (P = 1/3) z = 1.0262, for n = 4 (P = 2/15) z = −0.8332; both |z| < 3 (Z_ACCEPT = 3.0) → PASS
- G3 invariance — (i) the n = 3 MC re-run applying a random dihedral relabeling (rotation + optional reflection) each trial still agrees with P = 1/3 at z = 0.3336 (|z| < 3); (ii) exactly, the brute-force non-crossing COUNT is identical under all 2n rotations and reflection for n ∈ {3,4}, exact_invariance_all_true = True → PASS
- G4 falsifiability — on the SAME n = 3 MC sample the naive belief P_naive = 1/2 ("half of all matchings are planar") is rejected at z_naive = −148.1037 (|z| ≥ 6, Z_REJECT = 6.0), opposite polarity to G2; and the naive "non-crossing count = 2^(n−1)" fails exactly, 2^(3−1) = 4 ≠ 5 = C_3 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

Fix 2n points labelled 0, 1, …, 2n−1 in circular order on a circle. A perfect matching pairs them into n chords ("handshakes"); the number of perfect matchings is the odd double factorial (2n−1)!! = 1·3·5···(2n−1). Draw a matching uniformly at random. The probability that it is non-crossing (no two chords cross) is exactly

    P(n) = C_n / (2n−1)!!,

where C_n = binom(2n,n)/(n+1) is the n-th Catalan number, because the number of non-crossing perfect matchings of 2n circle points is exactly C_n. Headline exact values: n = 2 → 2/3 (3 matchings, 2 non-crossing); n = 3 → 1/3 (15 matchings, 5 non-crossing); n = 4 → C_4 / 7!! = 14/105 = 2/15. Two chords (a,b), (c,d) with a < b, c < d cross iff a < c < b < d or c < a < d < b (standard interleaving test). Two naive rivals are shown false on the same evidence: the even-split belief P = 1/2 (rejected at ~148σ on the same n = 3 sample where 1/3 agrees at |z| < 1.1) and the "non-crossing count = 2^(n−1)" rule (2^(3−1) = 4 ≠ 5 = C_3, exact).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_240_catalan_noncrossing.py` (verifier file sha256 `d6a8712b7fae7a00c650e3f8e0bb90a0a89b93ed0b42e96679071241665761ea`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. build_results() is a pure function of SEED and the module constants (each Monte-Carlo stream consumes its own random.Random(SEED) in a fixed order; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the two pinned Wikipedia revisions and the quoted/derived split live with the source PROPOSAL 240, and the canonical grounding review belongs to the coordinator-driven VERDICT 253 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 253 slice, not here._
