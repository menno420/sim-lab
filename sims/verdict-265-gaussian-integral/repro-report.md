# VERDICT 265 reproduction mirror — the Gaussian integral ∫_{−∞}^{∞} e^{−x²} dx = √π: exact rational even-moment backbone, MC agreement, scale-invariance, and √(2π) falsification, PROPOSAL 252

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 265 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block. `control/status.md` is untouched.

**Source proposal:** idea-engine PROPOSAL 252 (fleet · pure mathematics / analysis / the Gaussian (Euler–Poisson) integral — a self-contained closed form outside the fleet/venture/game domains: ∫e^{−x²}dx = √π, verified through the exactly-rational dimensionless even-moment ratios R_m = M_{2m}/M_0 = (2m−1)!!/2^m)
**Lane:** P252 → V265 (+13 offset)
**Verifier:** `verify_252_gaussian_integral_sqrt_pi.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions, sys)
**SEED:** 20260717
**Command:** `python3 verify_252_gaussian_integral_sqrt_pi.py` (run from inside this directory; captured in `run-stdout.txt`)

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = f8d553495590f7e0dc52d702e6b3dbb813464b4b48e8bc3a159f140b1e88c0d8` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (`fractions.Fraction`, zero tolerance) — for m=0..12 assert that the integration-by-parts recurrence route `R_m = ∏_{j=1}^m (2j−1)/2`, the closed form `(2m)!/(4^m·m!)`, and the `(2m−1)!!/2^m` route are all exactly equal, and that the integer identity `(2m−1)!!·2^m·m! == (2m)!` holds. `checked = 13`, `mismatches = 0`. The dimensionless ratio is exactly rational — the irrational √π cancels — so the recurrence and closed-form routes are independent derivations that agree with zero tolerance. `z` not applicable, reported `"exact"` → PASS
- **G2 Monte-Carlo agreement** (i.i.d. importance draws) — estimate ∫_{−6}^{6} e^{−x²} dx by uniform importance sampling, `N = 400000`, `X ~ Uniform[−6, 6]`, estimator `12·e^{−X²}`. Sample estimate `1.776277`, SE `0.005459`, honest target `√π·erf(6) = 1.772454` (erf(6) = 1 − 2.2·10⁻¹⁷ underflows to exactly 1.0 in IEEE double → zero truncation bias in the comparison), `z = (x̄ − target)/SE = 0.7004`, `|z| = 0.7004 < 3` (Z_ACCEPT = 3.0). Each draw is an INDEPENDENT sample, so the plain i.i.d. SE is honest (no thinning / batch means; stated in the verifier docstring) → PASS
- **G3 invariance** (own direction) — two independent legs: (a) **exact scale-invariance** (`Fraction`, 0 mismatches) — for `a ∈ {1, 2, 3, 5, 1/2}` and m=0..12 the scaled recurrence `M_{2m}(a) = ((2m−1)/(2a))·M_{2m−2}(a)` gives the dimensionless quantity `a^m · (M_{2m}(a)/M_0(a)) == (2m−1)!!/2^m` INDEPENDENT of `a`; `exact_checked = 65`, `exact_mismatches = 0`; (b) **MC scale + translation law** (`|z| < 3`) — the full integral obeys `√a·∫e^{−a(x−μ)²}dx = √π` for every scale `a` and shift `μ`; across 6 configs `(a,μ) ∈ {(1,0),(2,0),(½,0),(1,3),(1,−2),(3,1)}` every `√a·estimate` agrees with √π, `max |z| = 1.5375`. → PASS
- **G4 falsifiability** (own direction, SAME MC sample as G2) — the naive foil confusing the Gaussian integral ∫e^{−x²}dx = √π with the standard-normal normalizer ∫e^{−x²/2}dx = √(2π) ≈ `2.506628` (also Stirling's constant) is REJECTED: on the same N=400000 sample, `z_foil = (x̄ − √(2π))/SE = −133.7896`, `|z_foil| ≫ Z_REJECT = 50.0`, while the same sample AGREES with √π at `z = 0.7004`. The teeth: the ½ in the standard-normal exponent rescales the integral by 1/√2 — √π and √(2π) are genuinely different values, and the same sample discriminates them → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

The Gaussian (Euler–Poisson) integral ∫_{−∞}^{∞} e^{−x²} dx = √π, with the even moments M_{2m} = ∫x^{2m}e^{−x²}dx = √π·(2m−1)!!/2^m. Because √π is irrational, the exact teeth come from the DIMENSIONLESS moment ratio R_m = M_{2m}/M_0 = (2m−1)!!/2^m = (2m)!/(4^m·m!), which is exactly rational (√π cancels) and satisfies the integration-by-parts recurrence M_{2m} = ((2m−1)/2)·M_{2m−2}. Headline exact ratios `R_1 = 1/2`, `R_2 = 3/4`, `R_3 = 15/8`, `R_6 = 10395/64` (three independent routes agree, 0 mismatches over m=0..12). A uniform-importance Monte-Carlo estimator of ∫_{−6}^{6} e^{−x²} dx agrees with √π·erf(6) at `z = 0.70`; the dimensionless ratio is exactly scale-invariant (65 `Fraction` checks, 0 mismatches) and the full integral obeys `√a·∫e^{−ax²}dx = √π` across 6 (a, μ) configs (max `|z| = 1.54`). The single most plausible confusion — that ∫e^{−x²}dx equals the standard-normal normalizer √(2π) — is shown false on the same evidence (rejected at `|z_foil| = 133.8`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_252_gaussian_integral_sqrt_pi.py` (verifier file sha256 `1f348d8524b2a4f6f662c880455662c0fe1daa00226a0fc24e76464f51dd5115`). The copy in this directory carries the same sha256 and `diff` against the source is empty (exit 0), confirming a byte-for-byte reproduction of the source verifier; stdlib-only (json, hashlib, math, random, fractions, sys), no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (`random.seed(SEED)` is re-seeded at the START of each Monte-Carlo gate so gate order cannot perturb the payload; every float enters the hashed payload via a fixed `f"{x:.6f}"` / `f"{z:.4f}"` string and every exact ratio as a `str(Fraction)`; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned reference revision (Wikipedia "Gaussian integral", oldid 1365252560, raw-wikitext sha1 `6d8b0d941ef6028c1331a63443a49c199f3c1c2d`, 22230 bytes) and the quoted/derived split live with the source PROPOSAL 252, and the canonical grounding review belongs to the coordinator-driven VERDICT 265 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 265 slice, not here. No `## VERDICT` block, no verdict high-water advance, `control/status.md` untouched._
