# VERDICT 241 — Probe report (reproduces PROPOSAL 228)

> Feller's no-return identity for the simple symmetric random walk on Z: the probability the walk AVOIDS the origin throughout the first 2n steps equals the probability it is AT the origin at time 2n, both equal to u_{2n}=C(2n,n)/4ⁿ. Over all 2^(2n) sign sequences #{S_{2n}=0}=#{never revisit 0 in 1..2n}=C(2n,n) EXACTLY.

- **Slice:** round-54 UNRELATED slot · PROPOSAL 228 → VERDICT 241 (+13 offset)
- **Branch:** `claude/verdict-241-random-walk-no-return`
- **Sim dir:** `sims/verdict-241-random-walk-no-return/`
- **Source:** idea-engine `ideas/fleet/random-walk-no-return-2026-07-20.md` (PROPOSAL 228, control/outbox.md)
- **Ruling recommendation:** APPROVE

## 1. Verifier copy — firsthand artefact

`random-walk-no-return.py` is stdlib-only (sys, json, math, hashlib, random, math.comb, fractions.Fraction). It is the firsthand artefact; the idea-engine doc references it by path. `SEED = 20260717`.

## 2. Digest — full-64

`results_sha256 = 75f5b3c166916598983389896cc762c906b1ef346c70f8b5c639b3a60e140f46`

Whole-dict sha256 over the canonical `json.dumps(sort_keys=True, separators=(",",":"))` form, no self-field embedded, printed to stdout only. This is the digest disclosed to the PROPOSAL 228 idea doc and outbox block.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice and asserts the canonical forms are byte-identical (`sys.exit(3)` on divergence). Holds.
- **Separate re-invocation:** a second independent `python3 random-walk-no-return.py` prints the identical digest; `diff` of the two stdouts is empty (0 differences). Holds.
- Single `random.Random(20260717)` consumed in the fixed order G2 → G3 → G4 (G1 is exhaustive/RNG-free; G4 reuses the G2 sample, drawing no fresh randomness). All sampler-derived floats rounded to 6 decimals.

## 4. Gates — four, all PASS, each in its own direction

| Gate | Direction | Test | Result |
|------|-----------|------|--------|
| G1 | EQUALITY (exact) | exhaustive all 2^(2n) sign sequences, n∈{1,2,3,4,5,6}: A=#{S_{2n}=0}==B=#{never touch 0}==C(2n,n) and Fraction(A,4ⁿ)==Fraction(B,4ⁿ)==C(2n,n)/4ⁿ==u_{2n} | PASS — counts {2,6,20,70,252,924}=C(2n,n) at every n; A==B exact |
| G2 | AGREEMENT \|z\|<3 | MC n=12 (24 steps), N=200000: p̂_return & p̂_noreturn each vs shared exact u_24=0.16118026 | PASS — p̂_return=0.161965 (z=+0.9544), p̂_noreturn=0.158995 (z=−2.6578), both \|z\|<3 |
| G3 | INVARIANT + AGREEMENT | n∈{5,8,12,20}: p̂_noreturn vs exact u_{2n}; left/right symmetry P(strictly +)≈P(strictly −) | PASS — z_noreturn ∈ {+0.398,−0.833,−1.679,−1.182}; symmetry z ∈ {−1.529,+1.503,−0.902,+0.250}, all \|z\|<3 |
| G4 | REJECTION \|z\|>6 | naive independence fallacy P(no-return)=2⁻ⁿ=1/4096≈0.000244 vs observed ≈0.161 on the SAME G2 sample | PASS — z_vs_naive=+4544.27, naive REJECTED (true u_24≈0.161, ~660× the fallacy) |

**Teeth read:**
- G1 is a zero-slack integer / Fraction equality over the complete 2^(2n) path space — the exact core. The two counts (land on 0 at time 2n; never touch 0 in 1..2n) are provably equal, both equal to the central binomial C(2n,n), for every n through 6.
- G2 confirms the exact shared u_24 survives at n=12 under 200k-sample MC from both the return side and the no-return side.
- G3 shows the identity is size-independent across n∈{5,8,12,20} and that the no-return event splits into two symmetric one-sided excursions (strictly-positive ≈ strictly-negative), the mirror symmetry of the ±1 walk.
- G4 is the falsifiability tooth: the intuitive "avoiding 0 over 2n steps ~ n independent coin-pair survivals ⇒ 2⁻ⁿ" is wrong by three orders of magnitude and is rejected at ~4544σ. The no-return probability decays like 1/√(πn), NOT geometrically — the walk's stickiness (null recurrence) is exactly what the naive independence model misses.

## 5. Grounding

The identity is Feller, *An Introduction to Probability Theory and Its Applications*, Vol. I, Ch. III (§III.3, the theorem that P{no return to 0 through step 2n} = P{S_{2n}=0} = u_{2n}, with u_{2n}=C(2n,n)2^(−2n)). The exact statement for general n rests on that cited theorem; here it is additionally PROVEN firsthand by exhaustive enumeration of the complete path space for n≤6 (G1, zero slack), and confirmed by Monte-Carlo agreement and a pre-registered falsifiability gate for larger n. The +13 offset (PROPOSAL 228 → VERDICT 241) is the standing round convention.

## 6. Ruling

**APPROVE.** The core identity is exactly true (exhaustive G1 over n∈{1..6}, both counts = C(2n,n)), reproduces byte-identically across an in-process double-run and a separate re-invocation, agrees with the exact u_{2n} under MC at n=12 and across n∈{5,8,12,20} (G2/G3), and survives a pre-registered falsifiability gate that rejects the naive 2⁻ⁿ independence model at ~4544σ (G4). Exhaustive coverage stops at n=6 by combinatorial necessity (2^12 paths); n≥7 rests on the cited theorem plus the Monte-Carlo invariant gates — the intended division of labour. Digest `75f5b3c1…e140f46`.
