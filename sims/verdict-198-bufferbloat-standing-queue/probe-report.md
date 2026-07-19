# Probe report — VERDICT 198 (bufferbloat standing queue, reproduce PROPOSAL 185)

## Probe report

Reproduced the disclosed verifier `bufferbloat_standing_queue.py` (copied byte-identically from idea-engine @0772612, `diff` exit 0) under SEED=20260717, stdlib-only Python 3. File sha256 `e25b54637e20c961bf963c812755b97df8bf2189ebf70b6348d4e7ad99cb8762`; git blob `416280d408fef395a81363189ab500778539fa27`.

**Digest.** Results-dict sha256 = `d968600582b39bde30bbbead4b192a0d08c4d1bcb64c3b5c1a17f40924139142` — MATCHES the disclosed PROPOSAL 185 digest across all 64 hex characters (byte-grep, count 1, no truncation).

**Determinism.** The in-process double-run determinism assert passes; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`, `first_failing_gate = null`.

**Gates (Z_GATE = 3.0), order G1 → G2 → G3:**

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — latency scales with buffer | ΔW = W(K_LARGE) − W(K_SMALL) | 49.954161 | 508.993574 | PASS |
| G2 — no goodput dividend | \|thr(K_SMALL) − thr(K_LARGE)\| | 0.000265 | — | PASS |
| G3 — robust (shifted load ρ=1.5) | ΔW | 50.033018 | 581.376023 | PASS |

W(K_SMALL) = 21.09712 → W(K_LARGE) = 71.05128 as K goes 25 → 75 (ratio 3.367819, slightly above the 3.0 K-ratio because the −ρ/(ρ−1) offset shrinks the small-K wait). Throughputs: G2 0.999952 vs 0.999687 (gap 0.000265, both ≥ 0.98μ); G3 1.000961 vs 1.000406 (gap 0.000555). The G1/G3 latency margins are enormous (z ≈ 509 and 581); the binding constraint is the throughput bound (gap ≤ 0.02μ), satisfied with ~75× headroom.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `d968600582…139142`.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0.
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **Standing-queue law grounding live?** Yes — the Wikipedia "Bufferbloat" revision (revid 1354864082) states verbatim "In a first-in first-out queuing system, overly large buffers result in longer queues and higher latency, and do not improve network throughput" — the exact affine-in-K-latency / flat-throughput law the gates test.

## Grounding-strength note

The Gettys & Nichols "Bufferbloat: Dark Buffers in the Internet" (ACM Queue, 2011) framing is CITED-on-page not separately fetched; the GATED claim — under saturation a bigger FCFS buffer converts one-for-one into standing queue (W affine in K at slope 1/μ) while goodput stays pinned at μ — is stated verbatim on the live "Bufferbloat" page and is exactly what G1/G2/G3 measure, so the reproduction and the verdict rest on live-supported ground.

**Recommendation: APPROVE.**
