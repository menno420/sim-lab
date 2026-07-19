# Probe report — VERDICT 199 (follow-on reserve starvation, reproduce PROPOSAL 186)

## Probe report

Reproduced the disclosed verifier `follow_on_reserve_starvation.py` (copied byte-identically from idea-engine @702e168, `diff` exit 0) under the in-source SEED=20260717, stdlib-only Python 3. File sha256 `3d3805429768437fc25a1a46d14df17d95b6101645051cf4481e94c83235e391`; git blob `8cf9962dc68a12e54bc242122362f118596174ff`.

**Digest.** Results-dict sha256 = `b917778d026e7beea3aff07e8e6b8f6afad7b8df099f39a2773214f79ec2950f` — MATCHES the disclosed PROPOSAL 186 digest across all 64 hex characters (byte-grep, count 1, no truncation).

**Determinism.** The in-process double-run determinism assert passes; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`.

**Gates (Z_GATE = 3.0), order G1 → G2 → G3:**

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — reserves beat spray | ΔMOIC = MOIC(reserve) − MOIC(spray) | 0.431911 | 20.933485 | PASS |
| G2 — edge is the winners | top-decile share of positive edge | 0.823121 | — | PASS |
| G3 — robust (steeper tail α=1.4) | cold ΔMOIC | 1.323610 | 15.911868 | PASS |

Base: spray MOIC 3.836963 vs reserve MOIC 4.268874 (paired ΔMOIC +0.431911 at z ≈ 20.93). Cold tail (α=1.4): spray 5.008969 vs reserve 6.332579 (ΔMOIC +1.323610 at z ≈ 15.91, top-decile share 0.874894). dilution_factor = (1−0.30)^4 = 0.2401; the mechanism condition (1−RESERVE_FRAC)=0.5 > 0.2401 holds with wide margin. The binding constraint is G2's concentration bound (0.75), satisfied at 0.823.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `b917778d…2950f`.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0.
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **Head honestly scoped as regime-dependent?** Yes — reserves beat spray only where `(1−RESERVE_FRAC) > (1−d)^R` (0.5 > 0.2401) AND the tail is fat enough; the doc's caveats disclose the α=2.0 thin-tail reversal (ΔMOIC < 0) and state the algebraic dilution condition. The shipped verifier params (RESERVE_FRAC=0.50, d=0.30, R=4, α=1.6/1.4) match the doc's pinned constants — no plan-vs-verifier divergence.

## Grounding-strength note

The gated claim — reserving capital to defend pro-rata in the power-law winners raises fund MOIC — rests on GoingVC, "Follow On in Venture Capital" (live HTTP 200 this session), which states managers "fight for pro-rata rights to maintain their ownership stake" and that being able to "'double down' on the 'winners'" is "an important factor in the success of venture fund managers, especially those at the seed stage." The reproduction and verdict rest on live-supported ground.

## Scoping-honesty note

The proposer disclosed that the effect is regime-bound: the "Caveats & crossovers" section states the boundary `(1−RESERVE_FRAC) > (1−d)^R` and gives a concrete thin-tail reversal (Pareto α=2.0 → ΔMOIC < 0). The dilution-schedule crossover is disclosed algebraically (condition + "Pinned so this reads 0.5 > 0.2401") but not with a worked mild-dilution counterexample the way the tail crossover is — a minor transparency asymmetry, not over-claiming, since the head is explicitly conditioned "under a power-law portfolio" and the mechanism states the boundary. Ruling: APPROVE.

**Recommendation: APPROVE.**
