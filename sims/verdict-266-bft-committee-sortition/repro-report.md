# VERDICT 266 reproduction mirror — committee-sortition safety in a Byzantine fleet: exact hypergeometric upper tail, MC agreement, Byzantine-identity invariance, and the with-replacement binomial falsification, PROPOSAL 253

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 266 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block. `control/status.md` is untouched.

**Source proposal:** idea-engine PROPOSAL 253 (fleet · coordination / consensus over a fleet of agents — committee sortition under Byzantine faults: a fleet of N=64 agents with B=21 Byzantine sits EXACTLY at the classical BFT bound N = 3B+1, yet a K=16 sortition committee is UNSAFE — carries ≥ T = ⌊K/3⌋+1 = 6 Byzantine members — with probability equal to the exact hypergeometric upper tail P = ∑_{i=T}^{K} C(B,i)·C(N−B,K−i)/C(N,K))
**Lane:** P253 → V266 (+13 offset)
**Verifier:** `verify_253_bft_committee_sortition.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: argparse, hashlib, json, math, random, fractions, sys)
**SEED:** 20260717
**Command:** `python3 verify_253_bft_committee_sortition.py` (run from inside this directory; captured in `run-stdout.txt`)

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 37567447cc2e96a1b1c57404ed3e43b52d09c829f186293cc5f4f6122a03802d` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (`fractions.Fraction`, zero tolerance) — the hypergeometric upper tail `P = ∑_{i=T}^{K} C(B,i)·C(N−B,K−i)/C(N,K)` computed exactly and cross-checked two independent ways: (A) the full pmf sums to 1 exactly (Vandermonde's identity `∑_i C(B,i)·C(N−B,K−i) = C(N,K)`), `vandermonde_residual = 0`; (B) the tail equals `1 −` the exact lower partial sum, `P == 1 − ∑_{i=0}^{T−1} pmf_i`, `tail_complement_mismatch = 0`. Exact value `P = 296431911/685926212` (`P_float = 0.432163`). `z` not applicable, reported `"exact"` → PASS
- **G2 Monte-Carlo agreement** (i.i.d. committee draws) — each committee is a FRESH independent `random.sample` of K=16 distinct agents, so the per-committee UNSAFE indicators are i.i.d. `Bernoulli(P)`. Over `MC_N = 400000` draws, `p_hat = 0.430443`, exact target `P = 0.432163`, `z = (p_hat − P)/sqrt(P(1−P)/MC_N) = −2.1966`, `|z| = 2.1966 < 3` (Z_ACCEPT = 3.0). Independent draws → the plain i.i.d. binomial SE is honest (no thinning / batch means; stated in the verifier docstring) → PASS
- **G3 invariance** (Byzantine-identity invariance, own direction) — the exact tail depends only on the COUNTS `(N,B,K,T)`, not on WHICH agents are Byzantine; structurally true by construction (`structural_counts_only = true`). Demonstrated EMPIRICALLY too: a SECOND MC block draws committees against a DIFFERENT Byzantine set of the same size `B` (`byz2 = {(i·3) mod N : i ∈ range(B)}`, distinct because `gcd(3,64)=1`; `byz2_differs_from_canonical = true`, `byz2_size = 21`), giving `p_hat2 = 0.432700` against the SAME exact `P`; `z2 = 0.6856`, `|z2| < 3` → PASS
- **G4 falsifiability** (own direction, SAME true without-replacement MC sample as G2) — the naive foil models the committee as K i.i.d. draws WITH replacement at rate `p = B/N`, `P_binom = ∑_{i=T}^{K} C(K,i) p^i (1−p)^{K−i} = 0.435210` (`binom_differs_from_exact = true`). This IGNORES the finite-population NEGATIVE correlation of without-replacement sampling, so it OVERSTATES the tail. On the SAME true sample, `z_foil = (p_hat − P_binom)/sqrt(P_binom(1−P_binom)/MC_N) = −6.0822`, `|z_foil| ≫ 3` → REJECTED, while the same sample ACCEPTS the hypergeometric `P` at `z = −2.1966`. The teeth: with-replacement sampling drops the finite-population correction, inflating the tail; the same evidence discriminates the two models → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

Committee-sortition safety in a Byzantine fleet. A fleet of N=64 agents contains B=21 Byzantine agents, so `N = 3B + 1` — the full system sits EXACTLY at the classical BFT safety bound `n ≥ 3f + 1` with `f = 21`. A committee of K=16 agents drawn UNIFORMLY WITHOUT REPLACEMENT (sortition) is UNSAFE iff it contains ≥ T = ⌊K/3⌋+1 = 6 Byzantine members (a K-node BFT quorum tolerates ⌊(K−1)/3⌋ = 5, so 6 breaks it). The Byzantine count in a committee is `Hypergeometric(N, B, K)`, and the committee-failure probability is the EXACT hypergeometric upper tail `P = ∑_{i=T}^{K} C(B,i)·C(N−B,K−i)/C(N,K) = 296431911/685926212 ≈ 0.432163`. The insight: a GLOBALLY-safe fleet still produces UNSAFE sub-committees ~43% of the time — the expected Byzantine count per committee is `K·B/N = 5.25`, just below the threshold of 6, yet sortition CONCENTRATES Byzantine nodes into some committees. This is exactly why committee-BFT protocols must SIZE committees to bound the sortition failure probability. A uniform i.i.d. Monte-Carlo estimator over 400000 independent committee draws agrees with the exact tail at `z = −2.20`; the value is invariant to which agents are Byzantine (a second, disjoint-by-construction Byzantine set agrees at `z2 = 0.69`); and the single most plausible confusion — modelling the committee as K WITH-replacement draws (Binomial(K, B/N) = 0.435210) — is shown false on the same evidence (rejected at `|z_foil| = 6.08`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_253_bft_committee_sortition.py` (verifier file sha256 `58e4159d96c70fca6cfc7563f67d521c1e5d546e5a09f3a9979984b863b16a0c`). The copy in this directory carries the same sha256 and `diff` against the source is empty (exit 0), confirming a byte-for-byte reproduction of the source verifier; stdlib-only (argparse, hashlib, json, math, random, fractions, sys), no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (`random.seed(SEED)` re-seeding fixes the Monte-Carlo draws so gate order cannot perturb the payload; every float enters the hashed payload via a fixed `f"{x:.6f}"` / `f"{z:.4f}"` string, every exact quantity as a `str(Fraction)` `num/den`, and the exact tail is carried as a rational; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned reference revisions (Wikipedia "Hypergeometric distribution", oldid 1364778061, raw-wikitext sha1 `faaf98ed0a35df30e3201d6b085b18a9da033e54`, 30058 bytes; and "Byzantine fault", oldid 1362230504, raw-wikitext sha1 `b3ad268d56c25ed9b5484ee0ad91ad4cceb8fa8c`, 36223 bytes) and the quoted/derived split live with the source PROPOSAL 253, and the canonical grounding review belongs to the coordinator-driven VERDICT 266 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 266 slice, not here. No `## VERDICT` block, no verdict high-water advance, `control/status.md` untouched._
