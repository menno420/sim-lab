# Probe report — VERDICT 200 (Glicko RD order-sensitivity, reproduce PROPOSAL 187)

## Probe report

Reproduced the disclosed verifier `glicko_rd_order_sensitivity.py` (copied byte-identically from idea-engine @678c37c, `diff` exit 0) under the in-source SEED=20260717, stdlib-only Python 3. File sha256 `2267c694d63e3a1de95f88bec885c1e455f916e1bd597cb470c947b4ff9e6f98`; git blob `59d95a4ede7b449cf8a694794ad7dc7cb974c37f`.

**Digest.** Results-dict sha256 = `d4f690a51493a8fc32dd0971548078b059277ba81b6e02c84364415f4d168ba6` — MATCHES the disclosed PROPOSAL 187 digest across all 64 hex characters (byte-grep, count 1, no truncation).

**Determinism.** The in-process double-run determinism assert passes; a separate cross-invocation (two independent `python3` processes) produced byte-identical stdout (`diff` exit 0). `all_pass = true`.

**Gates (Z_GATE = 3.0), order G1 → G2 → G3:**

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — order effect exists | mean rating gap (streak − alternating) | −60.205174 | −118.692568 | PASS |
| G2 — sign + magnitude | same-sign frac (≥0.90) · \|mean\| (≥5.0) | 0.9996 · 60.205174 | — | PASS |
| G3 — robust (+200 opponent shift) | mean rating gap | −54.313763 | −100.513794 | PASS |

Base field (opponent mean 1500): the streak order (WWWWWWLLLLLL) settles a mean −60.205174 Glicko points below the alternating order (WLWLWL) for the identical 6W-6L record, at z ≈ −118.69 across TRIALS=5000; the effect is same-signed in 0.9996 of trials. Shifted field (+200, opponent mean 1700): the gap holds at −54.313763 (z ≈ −100.51), same negative sign. The binding thresholds — |z| ≥ 3, same-sign ≥ 0.90, |mean| ≥ 5.0 — clear by roughly 40×, wide, and 12× respectively. all_pass=true.

## Probe answers

1. **Digest match?** Yes — 64/64 hex characters match the disclosed `d4f690a5…d168ba6`.
2. **Byte-identical verifier?** Yes — `diff` against the idea-engine source exits 0; file sha256 and git blob both match the source.
3. **Byte-identical reruns?** Yes — the in-process double-run assert holds and the cross-invocation stdout diff exits 0.
4. **Is the mechanism sound, not a sampling artifact?** Yes — in Glicko-1 the rating deviation RD shrinks after each game, so early (high-RD) games carry a larger g(RD)·(s−E)-weighted update than late (low-RD) ones; a streak front-loads all same-result games into the high-RD regime while alternating spreads them, so an identical 6W-6L record lands at a different rating purely by order. The verifier's pinned constants (R0=1500, RD0=350, N_GAMES=12, one game per rating period) implement exactly the Glicko-1 Step-2 update the paper defines.

## Grounding-strength note

The gated claim — a per-event rating that shrinks its confidence interval as evidence accumulates makes the final score order-dependent — rests on Mark Glickman's "The Glicko system" (`http://www.glicko.net/glicko/glicko.pdf`, resolved live this session, authentic 6-page PDF). It defines RD as the standard-deviation measure of rating uncertainty (p2), gives the Step-2 update weighting each game by `g(RDⱼ)·(sⱼ − E)` with `g(RD)=1/√(1+3q²RD²/π²)` (p3), and states that "game outcomes always decrease a player's RD" as more information accumulates (p2, worked 200→151.4 on p4) — exactly the RD-shrink-weights-early-games mechanism the gates measure. The reproduction and verdict rest on live-supported ground.

**Recommendation: APPROVE.**
