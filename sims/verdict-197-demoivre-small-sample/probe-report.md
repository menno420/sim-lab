# Probe report — VERDICT 197 (de Moivre small-sample variance, reproduce PROPOSAL 184)

## Probe report

Reproduced the disclosed verifier `demoivre_small_sample_variance.py` (copied byte-identically from idea-engine @ec4706b, `diff` exit 0) under SEED=20260717, stdlib-only Python 3. File sha256 `4755ab568c7c40a4eadc34b0a43d78620a45723ffc9a287254105b5c7fbf8283`; git blob `2774108842d0b57ce7f4672383e0cff827283c24`.

**Digest.** Results-dict sha256 = `8b9506d1182b6c5f3121ff8b585dfb7032d47a337013e30d4f7fbfc1e0968871` — MATCHES the disclosed PROPOSAL 184 digest across all 64 hex characters (byte-grep, count 1, no truncation).

**Determinism.** The in-process double-run determinism assert passes; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`, `first_failing_gate = null`.

**Gates (Z_GATE = 3.0):**

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — de Moivre scaling law | corr(\|r̂−p\|, 1/√n) | 0.570449 | 238.774053 | PASS |
| G2 — extremes small-n dominated | pop_mean_n − extremes_mean_n | 147.021788 | 213.047828 | PASS |
| G3a — robust (shifted p=0.1) | corr | 0.570124 | 219.519762 | PASS |
| G3b — robust (shifted n∈[25,250]) | delta | 38.443275 | 129.55551 | PASS |

Smallest margin is G3b at z ≈ 129.56 — still ~43× the z_gate = 3.0 threshold.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `8b9506d1…8871`.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0.
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **σ/√n grounding live?** Yes — the pinned Wikipedia "Standard error" revision (oldid 1362665393) states verbatim "the standard error of the mean equals the standard deviation divided by the square root of the sample size" (SE = σ/√n), the exact law gate G1 tests.

## Grounding-strength note

The de Moivre / Wainer "most dangerous equation" framing is CITED-not-fetched — there is no standalone article and Wainer 2007 was unfetchable in-env — and the proposer disclosed this honestly. The GATED claim, SD of an observed proportion = √(p(1−p)/n) ∝ 1/√n, is textbook-exact and live-supported by the "Standard error" source, so the missing attribution article does not undercut the reproduction or the verdict.

**Recommendation: APPROVE.**
