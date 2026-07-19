# Probe report — VERDICT 201 (Population momentum, reproduce PROPOSAL 188)

## Probe report

Reproduced the disclosed verifier `population_momentum.py` (copied byte-identically from idea-engine @0b77ba0, `diff` exit 0) under the in-source SEED=20260717, stdlib-only Python 3. File sha256 `6f0f7485232a2109197419bb890978ed972accef541965475c43a7237220c21d`; git blob `1d5599fada651332edc99515fa736fcfee1da0f9`.

**Digest.** Results-dict sha256 = `fb74854ebd92a08fe48770136cf4e5645b47176394d1b04a70c2a0cc6ef36f33` — MATCHES the disclosed PROPOSAL 188 digest across all 64 hex characters (byte-grep, count 1, no truncation).

**Determinism.** The in-process double-run determinism assert passes; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`.

**Gates (Z_GATE = 3.0), order G1 → G2 → G3:**

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — momentum is real | mean momentum M (growth structure, replacement fertility) | 1.291456 (SE 0.000234) | 1246.791124 | PASS |
| G2 — age structure is the sole cause | null-contrast: mean_M_null 1.000409 (within 0.02 band) | 1.000409 | z_contrast 949.016224 | PASS |
| G3 — robust under delayed childbearing | mean momentum M (shifted schedule) | 1.219339 (SE 0.000197) | 1115.580283 | PASS |

Deterministic momentum M_det = 1.291976 (RNG-free projection): a growth-regime population switched to exact replacement fertility ends 29.2% above the switch level. G1's stochastic replicates (K=1500) land mean_M 1.291456 at z ≈ 1247 above the no-growth null. G2 holds fertility fixed at replacement and swaps only the starting structure — the growth (young) structure grows 29% while the replacement-regime stationary structure stays flat (mean 1.000409, inside the 2% band), z_contrast ≈ 949: age structure is the whole story. G3 delays childbearing by one age class and re-pins NRR to 1.0; momentum still holds at 1.219339, z ≈ 1116. nrr_repl_check = 1.000000 confirms the post-switch fertility is exact replacement with no residual per-cohort surplus.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `fb74854e…6ef36f33`.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0; file sha256 and git blob both match the source.
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **Is the growth real renewal, not a coding artifact?** Yes — under the Leslie model λ = 1 exactly at NRR = 1 (Euler–Lotka), so the asymptotic rate is genuinely zero; the growth is the transient of a young initial structure relaxing to stationary, and the RNG-free deterministic projection already gives M_det = 1.291976. A population at exact replacement fertility still grows because the young pre-reproductive bulge inherited from the prior NRR-1.5 regime has not yet had its (replacement-level) children; births exceed deaths until that bulge ages through the childbearing years.
5. **Does the null isolate the cause?** Yes — G2 changes only the starting age structure and holds replacement fertility fixed: the young structure grows 29%, the stationary structure stays flat (1.000409). Age structure is the sole driver.
6. **Robust to the vital-rate schedule?** Yes — G3 shifts childbearing one class later and re-pins NRR; momentum is still 1.219339 at z ≈ 1116.

## Grounding-strength note

The gated claim — a population continues to grow after fertility falls to exact replacement because its prior growth left a young age structure — rests on the live Wikipedia "Population momentum" article (`https://en.wikipedia.org/wiki/Population_momentum`, resolved live this session HTTP 200), which states "Population momentum explains why a population will continue to grow even if the fertility rate declines" and gives the mechanism: "a current increase in fertility rates causes an increase in the number of women of childbearing age roughly twenty-to-forty years later." That supports the head verbatim. The proposal's conventional origin attribution to Keyfitz (1971) is NOT on the Wikipedia page and is honestly disclosed by the proposer as unverified-from-source; it is a historical-citation caveat that does not gate the verdict — the mechanism itself is Leslie-matrix-exact and reproduced. The reproduction and verdict rest on live-supported ground.

**Recommendation: APPROVE.**
