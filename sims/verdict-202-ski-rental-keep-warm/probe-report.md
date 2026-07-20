# Probe report — VERDICT 202 (Ski-rental keep-warm break-even, reproduce PROPOSAL 189)

## Probe report

Reproduced the disclosed verifier `ski_rental_keep_warm.py` (copied byte-identically from idea-engine `ideas/fleet/ski_rental_keep_warm.py` @27d5f4e, `diff` exit 0) under the in-source SEED=20260717, stdlib-only Python 3. File sha256 `e670dafdb3ef4388a827ae2659cff8eb7844f586404674540d102be5fbd5b158`; git blob `cf5840bb0b277e7fb4f129544ddfcd6729369e1d` (identical to the idea-engine source blob). Offset: PROPOSAL 189 → VERDICT 202 (+13).

**Digest.** Results-dict sha256 = `0a0464162b20350c6d07104fed5bf62f1578021be85c0ecba18b4b07a3964c2b` — MATCHES the disclosed PROPOSAL 189 digest across all 64 hex characters (byte-grep, count 1, no truncation). An independent recompute — `json.dumps(results, sort_keys=True, separators=(",", ":"))` then sha256 — also reproduces the same 64 hex, so the match is not an artifact of the verifier's own printer.

**Determinism.** The in-process double-run determinism assert (`assert r1 == r2`) does not raise; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`, exit 0.

**Gates (z_min = 3.0), order G1 → G2 → G3:**

| Gate | What it tests | Key values | Verdict |
|------|---------------|------------|---------|
| G1 — g1_long_idle_warm_blowup | Long idle (μ=5.0): break-even beats always keep-warm | z=306.250137 (≥3 ✓), ratio_be=1.903787 (<2 ✓), ratio_warm=5.522566 (>2 ✓) | PASS |
| G2 — g2_short_idle_cold_blowup | Short idle (μ=0.2): break-even beats always-cold | z=1524.124639 (≥3 ✓), ratio_be=1.033101 (<2 ✓), ratio_cold=5.030524 (>2 ✓) | PASS |
| G3 — g3_matched_constant_and_shift | Matched cost (μ=1.0): recover randomized e/(e-1) | ratio_be_match=1.579541 vs e/(e-1)=1.581977 → rel_err=0.00154 (<0.02 ✓); ratio_be_hyper=1.601131 (<2 ✓); z_hyper=124.186516 (≥3 ✓) | PASS |

World: B=1.0, R=200000 reps, mu_long=5.0, mu_match=1.0, mu_short=0.2, z_min=3.0, seed=20260717. G1's deterministic break-even ratio-of-means lands at 1.903787 — the ski-rental break-even (rent up to the buy cost, then buy) blows up its cost relative to always keep-warm by only ~1.9× in the worst (long-idle) regime, while the naive always keep-warm policy blows up 5.5×. G2 flips the regime: with short idle gaps, always-cold pays repeated warm-up (5.0×) while break-even stays near optimal (1.03×). G3 pins the matched-cost exponential-idle regime and recovers the randomized competitive ratio e/(e-1) = 1.581977 to within 0.15% (ratio_be_match 1.579541), and a hyper-idle shift keeps ratio_be_hyper at 1.601131, still under the deterministic-2 bound.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `0a046416…3a964c2b` (byte-grep count 1), and an independent JSON-canonical recompute reproduces the same digest.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0; file sha256 and git blob both equal the source (`cf5840bb…`).
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **Do the gates pass their own criteria?** Yes — G1 (z≥3, ratio_be<2, ratio_warm>2), G2 (z≥3, ratio_be<2, ratio_cold>2), and G3 (rel_err<0.02, ratio_be_hyper<2, z_hyper≥3) all pass in order; all_pass=true.
5. **Is the e/(e-1) recovery real?** Yes — G3's matched-cost regime lands ratio_be_match=1.579541 against the closed-form e/(e-1)=1.581977, rel_err 0.00154, independent of the RNG seed's particular draws at R=200000.

## Grounding-strength note

The gated claims rest on the live Wikipedia "Ski rental problem" article (`https://en.wikipedia.org/wiki/Ski_rental_problem`, resolved live this session, HTTP 200). It grounds the deterministic break-even rule — "rent for 9 days and buy on the morning of day 10" (buy when accumulated rent reaches the buy cost) — and the randomized bound — "the expected cost is at most e/(e-1) ≈ 1.58 times ... No randomized algorithm can do better." The verifier's G3 reproduces the e/(e-1) ≈ 1.58 constant to 0.15%.

**Caveat fairness.** The deterministic worst case is framed by the proposer as a ratio-of-means ~1.9× ($19 vs $10 at the tested buy cost, approaching 2× as b→∞) rather than the literal textbook phrase "2-competitive." This is honestly disclosed and is FAIR: the finite-buy-cost ratio-of-means is genuinely below 2 (1.903787 here) and converges to the 2-competitive bound only in the limit — the caveat does not overstate, and it does not gate the verdict, whose mechanism is exact.

**Recommendation: APPROVE.**
