# VERDICT 255 reproduction mirror — Markowitz global minimum-variance portfolio & two-fund separation, PROPOSAL 242

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 255 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 242 (venture-lab · portfolio optimization / mean-variance — the Markowitz GMV portfolio and two-fund separation)
**Lane:** P242 → V255 (+13 offset)
**Verifier:** `verify_242_min_variance_two_fund.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 3c1ec97050d0ca481e084976055ce3ea0e435c86b794e909507757e3eedf3f9c`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical · `--selfcheck`: byte-identical
- G1 EXACT identity — closed form == matrix GMV; FOC equalised, exact via `fractions.Fraction`. Two independent exact routes to (w*, σ*²) — the two-asset closed form and the general matrix form via a Fraction Gauss-Jordan solve of Σx=𝟙 — agree bit-for-bit; w* = (1/8, 7/8), σ*² = 15/16; across a 2/3/4-asset SPD panel (Σw*)_i == σ*² for all i and 𝟙ᵀw* == 1; error_count = 0 → PASS
- G2 Monte-Carlo agreement — 200 000 iid return vectors with covariance exactly Σ (Cholesky map L = [[2,0],[1/4, √15/4]] of iid standard normals); the GMV portfolio's sample variance s²_gmv = 0.9389802396 agrees with σ*² = 0.9375 at z = 0.4992990385; |z| < 3 (Z_ACCEPT = 3.0). The draws are iid (not a correlated sample path), so the Gaussian sample-variance SE = σ²·√(2/N) is honest with NO thinning needed → PASS
- G3 invariance — (i) scale-equivariance: Σ → kΣ (k = 4) leaves w* identical and scales σ*² by exactly k (Fraction), and the MC z is byte-identical under the √k sample-path rescaling (mc_z_base = mc_z_scaled = 0.4992990385); (ii) two-fund separation: on a 3-asset frontier w(m) is affine in m, verified exactly by w(m_C) == α·w(m_A) + (1−α)·w(m_B) with α = 1/2, each w(m) summing to 1, and the GMV recovered on the frontier at m = B/A → PASS
- G4 falsifiability — on the SAME MC sample: the naive "equal weights are optimal" (variance 3/2) is rejected at z_eq = 191.0595200324, and the naive "hold the single lowest-variance asset" (variance 1) is rejected at z_a2 = 21.4684726468; both |z| ≥ 6 (Z_REJECT = 6.0); and exactly 3/2 ≠ 15/16 and 1 ≠ 15/16 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

For n risky assets with a symmetric positive-definite covariance matrix Σ, the global minimum-variance (GMV) portfolio — the fully-invested (𝟙ᵀw = 1) portfolio of least return variance — is

    w* = Σ⁻¹𝟙 / (𝟙ᵀΣ⁻¹𝟙),      σ*² = 1 / (𝟙ᵀΣ⁻¹𝟙),

equivalently every asset's marginal variance contribution is equalised, (Σw*)_i = σ*² for all i. For Σ = [[4, 1/2], [1/2, 1]] (variances 4 and 1, covariance 1/2, correlation 1/4): w* = (1/8, 7/8), σ*² = 15/16 — strictly below the best single asset (variance 1) and far below naive equal-weight (variance 3/2). Two naive rivals are shown false on the same evidence: "equal weights 1/n are optimal" (variance 3/2 ≠ 15/16, rejected at ≈191σ where 15/16 agrees at <1σ) and "hold the single lowest-variance asset" (variance 1 > 15/16, rejected at ≈21σ, and exactly 15/16 < 1). Efficient weights w(m) are affine in the target mean return m (two-fund separation).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/venture-lab/verify_242_min_variance_two_fund.py` (verifier file sha256 `b0e251b21c889e1c5f1dc9c36c33a2e9c1acaf3adfaa037aff381eb9ca101817`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. build_results() is a pure function of SEED and the module constants (the Monte-Carlo sample consumes its own random.Random(SEED)-seeded stream in a fixed order; exact rationals serialize via str(Fraction) and every float via a fixed f"{v:.10f}" string; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revision (Modern portfolio theory, oldid 1359858554) and the quoted/derived split live with the source PROPOSAL 242, and the canonical grounding review belongs to the coordinator-driven VERDICT 255 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 255 slice, not here._
