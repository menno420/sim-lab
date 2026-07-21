# VERDICT 259 reproduction mirror — Gordon growth / dividend-discount model present value PV = D1/(r−g) (exact geometric-series closed form), PROPOSAL 246

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 259 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** PROPOSAL 246 (idea-engine PR #866, merged, main a134ebf)
**Lane:** P246 → V259 (+13 offset)
**Verifier:** byte-identical copy, sha256 `afdd5047a87a048bf86f8a4b1c13e0307da2826c914e616bedfe3b7e8b89da9f`
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 3cb527ff7b7873d2bacb56dcb4eea6f490ef7817b67766f45696ab6d706230e4` — byte-identical to the idea-engine source digest.
- determinism triple: in-process double-run (`--selfcheck`) byte-identical · `--selfcheck` prints the same digest · separate re-invocation `diff` empty — all three byte-identical.
- **G1 EXACT identity** (`fractions.Fraction`, zero tolerance) — over the 10-case battery the exact geometric-series partial sum `Σ_{t=1}^{T} D1·(1+g)^{t−1}/(1+r)^t` (with `T_terms = 60`) and the closed form `D1/(r−g)` agree, and the pinned anchor table `{(D1=1, r=1/10, g=0)→10; (1, 1/10, 4/100)→50/3; (6, 1/10, 2/100)→75; (3, 1/5, 1/20)→20; (2, 12/100, 5/100)→200/7}` matches exactly — `mismatches = 0`, `anchor_mismatches = 0`, **max discrepancy exactly 0** (z not applicable, reported `null`/`"exact"`) → PASS
- **G2 Monte-Carlo agreement** — headline `D1=1, r=1/10, g=4/100`, `N = 100000` INDEPENDENT i.i.d. discounted-cashflow paths (per-period mean-1 multiplicative noise, `delta = 0.3`, horizon `T = 160`); `mean_hat = 16.6681667254` vs the exact finite-`T` target `target_exact_finiteT = 16.6645563219` (`se = 0.088431733702`), `z = 0.0408270129`; the infinite-horizon closed form `E_infinite = 16.6666666667 = 50/3`. `|z| < 3` (Z_ACCEPT = 3.0). Paths are INDEPENDENT (one present-value estimate per path) so NO thinning is needed → PASS
- **G3 invariance / robustness** — the present value depends ONLY on `(D1, r, g)`, not on the per-period noise regime: config A (`delta = 0.3`, mean-1) `zA = 0.0408270129`, config B (`delta = 0.5`, mean-1) `zB = −0.0034001459` (`meanA = 16.6681667254`, `meanB = 16.662406346`), two-sample invariance `two_sample_z = 0.0090221259`, all `|z| < 3`. Exact shift-invariance battery (12 cases) → `shift_invariance_mismatches = 0` → PASS
- **G4 falsifiability** — on the SAME headline sample, the naive belief "level perpetuity `P = D1/r` (ignores growth)" `= 10.0` is REJECTED at `z_naive = 75.4046816262 ≫ 3` (Z_REJECT = 3.0), while the same sample agrees with the exact growing-perpetuity value at `z_exact_for_contrast = 0.0408270129` — the teeth: ignoring growth understates the value (10 vs 50/3 ≈ 16.67) → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

The present value of a growing perpetuity (Gordon growth / dividend-discount model) with first cashflow `D1` one period out, discount rate `r`, and constant growth rate `g < r` is EXACTLY `PV = D1/(r−g)`. This is the closed form of the geometric series `PV = Σ_{t=1}^{∞} D1·(1+g)^{t−1}/(1+r)^t = (D1/(1+r)) · Σ_{k≥0} ((1+g)/(1+r))^k = (D1/(1+r)) · 1/(1 − (1+g)/(1+r)) = D1/(r−g)`. The pinned anchor table confirms it exactly: `(D1=1, r=1/10, g=0)→10`, `(1, 1/10, 4/100)→50/3`, `(6, 1/10, 2/100)→75`, `(3, 1/5, 1/20)→20`, `(2, 12/100, 5/100)→200/7`. The plausible naive belief that a level perpetuity `P = D1/r` (ignoring growth) captures the value is shown false on the same evidence: at `D1=1, r=1/10, g=4/100` the truth is `50/3 ≈ 16.67`, not `10` (rejected at `z ≈ 75.40`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier (verifier file sha256 `afdd5047a87a048bf86f8a4b1c13e0307da2826c914e616bedfe3b7e8b89da9f`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the exact-`Fraction` kernel is deterministic rational arithmetic; a single seeded RNG is consumed in a fixed order across the Monte-Carlo legs; every float serializes via a fixed format string and every exact rational via `str(Fraction)`; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is deferred to the coordinator-driven VERDICT 259 slice by design — the pinned Wikipedia revision and the quoted/derived split live with the source PROPOSAL 246, and the canonical grounding review belongs to that slice, not to this reproduction-only mirror (as the P245 mirror did).

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 259 slice, not here._
