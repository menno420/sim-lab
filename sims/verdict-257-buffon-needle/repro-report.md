# VERDICT 257 reproduction mirror — Buffon's needle: a short needle (ℓ ≤ d) crosses a line with probability exactly 2ℓ/(πd), PROPOSAL 244

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 257 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 244 (fleet · geometric probability — Buffon's needle short-needle crossing probability is exactly 2ℓ/(πd))
**Lane:** P244 → V257 (+13 offset)
**Verifier:** `verify_244_buffon_needle.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 20f5616bae9df0533ab9ac0b6f23206cc1f457c2105b83103ed51bec98ff8a1b` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 EXACT identity (fractions.Fraction, no floats) — over the rational grid `ℓ/d ∈ {1/4, 1/2, 3/4, 1}` × rational sines `s ∈ {0, 1/2, 3/5, 4/5, 1}` (20 pairs), the conditional crossing probability `P(cross | sinθ = s)` computed two independent ways — (a) directly `min(1, (ℓ·s)/d)`, and (b) via the offset-area model `((ℓ/2)·s)/(d/2)` clamped to 1 — is EXACTLY equal, `identity_mismatches = 0`; and the exact expectation factorization `E[cross] = (ℓ/d)·mean(s)` (`mean_sines = 29/50`) computed two ways is EXACTLY equal, `expectation_mismatches = 0` → PASS
- G2 Monte-Carlo agreement — continuous model `ℓ/d = 1/2` so `P = 1/π ≈ 0.318309886184`; `N = 2,000,000` i.i.d. drops give `crossings = 636571`, `p̂ = 0.3182855`, `z = −0.0740355452082`; `|z| < 3` (Z_GATE = 3.0). The drops are i.i.d. Bernoulli — NO autocorrelation, so no thinning is needed. Buffon π-estimate `π̂ = 2ℓN/(dC) = 3.14183335402` → PASS
- G3 invariance / robustness — (a) scaling both `ℓ` and `d` by `k ∈ {2, 5, 0.3, 100}` leaves `P̂` within sampling error of `2ℓ/(πd) = 1/π`, each scaled config `|z| < 3` (worst `k = 5`: `z = −1.15685382694`); (b) sampling `θ` over the full circle `[0, 2π)` with `|sinθ|` matches `θ ~ [0, π/2]`, `z = −0.229457897577`; `max|z| = 1.15685382694 < 3` → PASS
- G4 falsifiability — on the SAME G2 sample, the naive "no angle factor" foil `P_naive = ℓ/d = 0.5` disagrees far outside 3σ, `|z| = 513.96622076 ≫ 3` REJECTED; the subtler "assume E[sinθ] = ½" foil `P_naive2 = (ℓ/d)·½ = 0.25` is REJECTED at `|z| = 223.019509108 ≫ 3` → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In Buffon's needle — a needle of length `ℓ` dropped uniformly at random on a plane ruled with parallel lines spaced `d` apart, in the SHORT-needle regime `ℓ ≤ d` (center offset to the nearest line `u ~ Uniform[0, d/2]` and acute angle `θ ~ Uniform[0, π/2]` independent; the needle crosses iff `u ≤ (ℓ/2)·sinθ`) — the crossing probability is EXACTLY `P = 2ℓ/(πd)`. Equivalently, tossing the needle `N` times and counting `C` crossings estimates π via `π̂ = 2ℓN/(dC)`. Two naive rivals are shown false on the same evidence: "no angle factor" `P = ℓ/d = 0.5` (rejected at `|z| ≈ 514`) and "assume E[sinθ] = ½" `P = (ℓ/d)·½ = 0.25` (rejected at `|z| ≈ 223`). π appears because the orientation law is rotationally symmetric — `E[sinθ] = 2/π` over a quarter turn.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_244_buffon_needle.py` (verifier file sha256 `a678b5e68fc84ebec46627be99b99e645d3d3e9b1a3c4a5f59aedb60d2412fcb`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the exact-`Fraction` kernel is deterministic rational arithmetic; a single `random.Random(SEED)` is seeded once and consumed in a fixed order across all Monte-Carlo legs; every float serializes via a fixed format string and every exact rational via `str(Fraction)`; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revision ("Buffon's needle problem", oldid 1356796927) and the quoted/derived split live with the source PROPOSAL 244, and the canonical grounding review belongs to the coordinator-driven VERDICT 257 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 257 slice, not here._
