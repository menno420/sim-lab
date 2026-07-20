# Reproduction mirror — PROPOSAL 232 / VERDICT 245 (coprime density = 6/π²)

> **Status:** `reproduction` — PRE-VERDICT reproduction of idea-engine PROPOSAL 232; the byte-identical verifier reproduced green. The verdict slice owns the ruling: the canonical independent APPROVE/QUALIFIED/REJECT VERDICT 245 is a separate coordinator-driven slice, and this PR lands only the reproduction material — it does not append a VERDICT block and does not advance the verdict high-water.

## Source
idea-engine PROPOSAL 232 — ideas/fleet/verify_232_coprime_density.py (branch claude/proposal-232-coprime-density). Byte-identical copy here: sims/verdict-245-coprime-density/verify_232_coprime_density.py (diff exit 0).

## Claim
For two integers drawn independently and uniformly from {1,…,N}, the probability they are coprime is the exact Möbius-inversion density Q(N)=(1/N²)·Σ_{k=1}^{N} μ(k)·⌊N/k⌋², converging to 6/π²=1/ζ(2)≈0.6079271018540267 as N→∞ (Basel ζ(2)=π²/6, Cesàro 1881) — NOT the naive "avoid a shared factor of 2 ⇒ 3/4" value.

## Reproduced firsthand
- SEED=20260717, stdlib-only (json, hashlib, math, random, fractions), Python 3.11.15.
- results_sha256 = 754580401315c5e987d30467f1d99ee125605f6203de69d9340f910308840fec (full 64 hex), byte-identical across the in-process double-run guard + a separate re-invocation (see run-stdout.txt).
- G1 EXACT identity, two independent routes: brute A(N)=#{(a,b)∈[1,N]²: gcd=1} == Möbius B(N)=Σμ(k)(N//k)² as ints AND as Fractions for every N∈{1,2,3,4,5,6,10,50,100,200}; Q(6)=23/36.
- G2 MC agreement N=10000 M=200000: Q_N=60794971/100000000≈0.60794971; p̂=0.608795; z_agreement=+0.774312 (|z|<3); asymptote 6/π²≈0.6079271018540267.
- G3 EXACT partition invariant: Σ_{d=1}^{N} A(⌊N/d⌋)==N² (unique-gcd decomposition) for every N∈{1,2,3,10,20,50,100,200}; 0<Q(N)<1 for N≥2 (Q(1)=1 boundary).
- G4 falsifiability: the naive parity-only 3/4 rejected on the SAME MC sample at z_naive=−145.835897 (|z|≥8) while the exact density is accepted. The 2-only fallacy predicts 0.75; the true density is 6/π²≈0.6079.
- all_pass=true, first_failing_gate=null.

## Grounding (from the proposal, recorded for the ruling slice)
Wikipedia "Coprime integers" oldid 1363371102 sha1 254a5e6988f14ce74d40502b159f687ea8c4947c (raw-wikitext self-computed sha1 == API revision sha1; 17,251 bytes). QUOTED on the pinned revision: the Euler product/limit ∏(1−1/p²)=1/ζ(2)=6/π²≈0.607927102, the Basel evaluation ζ(2)=π²/6, and P_N→6/π² as N→∞ (Cesàro 1881, Hardy–Wright Theorem 332). DERIVED firsthand (absent from the page): the exact finite-N Möbius identity Q(N)=(1/N²)Σμ(k)⌊N/k⌋², the partition invariant Σ_d A(⌊N/d⌋)=N², the 3/4 falsifier, and every Monte-Carlo z-value.

## Deferred
The independent adversarial ruling (re-grounding quoted-vs-derived firsthand, re-evaluating each gate in its own direction, and the APPROVE/QUALIFIED/REJECT verdict) is the dedicated VERDICT 245 slice's deliverable.
