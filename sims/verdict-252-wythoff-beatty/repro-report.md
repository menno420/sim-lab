# VERDICT 252 reproduction mirror — Wythoff's game cold positions are the golden-ratio Beatty pairs, PROPOSAL 239

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 252 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 239 (fleet · Wythoff's game / golden-ratio Beatty P-positions)
**Lane:** P239 → V252 (+13 offset)
**Verifier:** `verify_239_wythoff_beatty.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 9fe0e90d2c4544a9c38c051be34b9369fdf84f12b53e4ed16818feb5c87eabcc`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 EXACT — the Grundy-0 (cold / P) board positions from a mex-DP equal EXACTLY the isqrt-Beatty pairs on panels N ∈ {30,60,90}; the integer identity b_n − a_n == n holds with zero errors over n ∈ [0, 200000]; and {a_n} ∪ {b_n} partitions 1..M exactly (no gap, no overlap) on M ∈ {1000, 100000, 1000000} with lower density → 309017/500000 = 0.618034; error_count = 0 → PASS
- G2 Monte-Carlo agreement — 200 000 uniform draws in [1, 1000000] land in the lower Wythoff set with p̂ = 0.61729 vs the theoretical 1/φ = 0.618034, z = −0.684799 (|z| < 3, Z_ACCEPT = 3.0) → PASS
- G3 invariance — (i) the isqrt-Beatty generator and the greedy-mex construction (a_n = mex{a_i,b_i : i<n}, b_n = a_n + n) agree exactly on every panel; (ii) the Grundy table is pile-swap symmetric G(x,y) == G(y,x) with zero asymmetric cells; mismatch_count = 0 → PASS
- G4 falsifiability — on the SAME MC sample the naive even-split foil "lower density = 1/2" is rejected at z_reject = 104.907365 (|z| ≥ 6, Z_REJECT = 6.0); and the naive universal foil "every P-position is (k, 2k)" is refuted exactly, holding only at the two coincidental fits n=0 (0,0) and n=1 (1,2) and breaking with first counterexample at n=2 → (3,5), 199 999 counterexamples in range → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In Wythoff's game (two piles; a move removes k ≥ 1 from one pile, or removes the SAME k ≥ 1 from both piles; last to move wins), the cold / P-positions (Sprague-Grundy value 0, previous-player-wins) are exactly the golden-ratio Beatty pairs

    P_n = (a_n, b_n),   a_n = ⌊n·φ⌋,   b_n = ⌊n·φ²⌋,   n = 0, 1, 2, …

with φ = (1 + √5)/2 the golden ratio, and the exact integer identity b_n = a_n + n. Computed float-free via a_n = (n + isqrt(5·n²)) // 2, b_n = a_n + n. The lower and upper Wythoff sequences {a_n} (OEIS A000201) and {b_n} (A001950) partition the positive integers by Beatty's theorem, since 1/φ + 1/φ² = 1: every positive integer sits in exactly one of them. The lower sequence therefore carries natural density 1/φ ≈ 0.618034 — the golden-ratio split, not 1/2. Two naive rivals are shown false on the same evidence: the even-split belief (density 1/2) and the universal (k, 2k) rule (b_n = 2·a_n), the latter surviving only at the two smallest coincidences n=0 and n=1 and failing at every n ≥ 2 starting with (3, 5).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_239_wythoff_beatty.py` (verifier file sha256 `1c7f252ad6bc52e1a8f2b993a72e8f71e59197469eb69ca24188e1d91bc8685c`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The build_results() payload is a pure function of SEED and the module constants (one seeded random.Random(SEED) consumed in fixed order), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 252 slice, not here._
