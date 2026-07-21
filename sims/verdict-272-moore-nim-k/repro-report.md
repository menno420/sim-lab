# VERDICT 272 reproduction mirror — Moore's Nim (Nim_k) P-positions via column-sums mod (k+1), PROPOSAL 259

> **Status:** reproduction-only — ruling deferred to the coordinator-driven VERDICT slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 259 (PR #892, merge SHA pending — native squash auto-merge on green)
**Lane:** P259 → V272 (+13 offset)
**Verifier:** `verify_259_moore_nim_k.py` (byte-identical copy of the firsthand idea-engine verifier `ideas/superbot-games/verify_259_moore_nim_k.py`; stdlib only: argparse, functools, hashlib, itertools, json, math, random, sys, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = da147d54d970d71754baa2994189c9e5f73cfbbf1ad36c7b2366f9ddf870402d` — byte-identical to the idea-engine source digest.
- determinism triple: default run · `--selfcheck` (in-process double-run, byte-identical) · separate re-invocation — all byte-identical.
- **G1 EXACT (exhaustive, integer/XOR, zero tolerance)** — for `k ∈ {1,2,3}` enumerate ALL positions with `m` heaps (`m = 1..4`) and each heap in `[0,H)` (`k=1: H=8` → 4680 positions, `k=2: H=6` → 1554, `k=3: H=5` → 780) and assert `moore_predicate(heaps,k) == (outcome_oracle(heaps,k) is P)` for every position: `positions_checked = 7014`, `mismatches = 0` across three distinct moduli `k+1 ∈ {2,3,4}`. Direction: theorem ⇔ true game outcome → PASS
- **G2 MC agreement (`|z| < 3`)** — `(k,m,b) = (2,5,6)`, heaps uniform in `[0,2^6)`; independently-derived exact P-fraction `f = (11/32)^6 = 1771561/1073741824 ≈ 0.001650` (per column `(C(5,0)+C(5,3))/2^5 = 11/32`, `b=6` independent columns); `N = 200000` iid draws give `p̂ = 0.001765`, binomial `z = 1.268354`; `|z| < 3` → PASS
- **G3 invariance / robustness (0 violations)** — (a) k=1 collapse: over an exhaustive range (`m ≤ 4`, `H ≤ 8`) `moore_predicate(heaps,1) == (xor_all(heaps) == 0)`, `collapse_violations = 0`. (b) permutation + zero-pad: over 400 random positions (random `k ∈ {1,2,3}`, `m ≤ 4`) both `moore_predicate` and `outcome_oracle` survive a random heap permutation and appending zero heaps, `perm_violations = 0`, `pad_violations = 0`. Direction: structural symmetries → PASS
- **G4 falsifiability (`|z| > 3`)** — the ordinary-Nim rule (predict P ⇔ nim-sum XOR `== 0`, columns mod 2) applied to Moore's Nim with `k=2` (true modulus 3) misclassifies against the TRUE outcome oracle on `N = 5000` random small `k=2` positions (`m=4`, heaps `0..3`) at error rate `ê = 0.345800`, `z_foil = 51.409363`; on the SAME sample the true theorem predicate makes `theorem_errors = 0`. Direction: refute a plausible-but-wrong rule → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In Moore's Nim (Nim_k) under normal play (last player to move wins), a position is a multiset of heap sizes `(a_1,…,a_m)`; a move selects between 1 and k heaps inclusive and removes a positive number of tokens from each selected heap. Writing every heap in binary and letting `c_j = Σ_i bit_j(a_i)` be the column-sum of bit `j` across all heaps, the position is a P-position (the player to move loses) IF AND ONLY IF `c_j ≡ 0 (mod k+1)` for every bit-position `j`. For `k=1` the modulus is 2, so the criterion collapses to "every binary column-sum is even" — the nim-sum (XOR) is 0 — which is exactly ordinary Nim (Bouton's theorem). Reproduced here by an independent memoized P/N outcome oracle (`outcome_oracle`) that does NOT assume the theorem, compared position-by-position against the closed-form `moore_predicate`, with the game oracle alone driving every P/N classification: exact equivalence holds with zero mismatches across three moduli, the predicate's P-density matches Monte-Carlo inside 3σ, and the ordinary-Nim (mod 2) foil applied to k=2 is rejected far beyond 3σ while the true predicate makes zero errors.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/superbot-games/verify_259_moore_nim_k.py` (verifier file sha256 `e8e117d135dc4875744d060a764f920840957a6bf15ca3efe0b86901f9e03969`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. `build_results()` is a pure function of SEED and the fixed model params (no wall clock, no hostname, no unseeded randomness; every sampling gate draws from a fresh `random.Random(SEED[+offset])`; states are canonicalised to sorted tuples; every float enters via a fixed 6-dp format string and every count as an int; fractions are stored as "num/den"), so the in-process double-run (`--selfcheck`) and the separate subprocess re-invocation are byte-identical and the `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned source reference (Wikipedia "Nim", oldid `1362772636`, § Index-k nim) and the quoted/derived split live with the source PROPOSAL 259, and the canonical grounding review belongs to the coordinator-driven VERDICT 272 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 272 slice, not here._
