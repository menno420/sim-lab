# VERDICT 180 — MMR/Elo rating deflation: probe report (reproduced)

Reproduced from the committed verifier `sims/verdict-180-mmr-rating-deflation/mmr_rating_deflation.py` — a byte-identical copy of idea-engine `ideas/superbot-games/mmr_rating_deflation.py` at HEAD 44bc17c (file sha256 b9d14de839ae416677d7062e904a65ef494d97edeb28c556d6b381a63b5bae58, git blob 687c8ae09a443ea1bcfc204829d9f6cc833b7ac8). SEED = 20260717 pinned in-source at line 32. Full run output in `run-stdout.txt`.

**Math sanity note.** Every game applies a symmetric Elo update: player a gains `d = K·(sa − pa)` and player b loses the same `d`, so each game moves EXACTLY zero net points into the pool — total displayed rating is conserved by play. Points enter or leave the pool ONLY at the boundary: on churn a retiring player of accumulated rating `disp[r]` is removed (`ledger_out += disp[r]`) and a fresh player enters at the provisional floor (`ledger_in += floor`), with true skill redrawn `gauss(mu, sigma)`. Because eligible retirees have climbed above the floor (they have accumulated points to reach true skill ≈ mu=1500 » floor 1000/700), each churn event removes more than it injects — a strictly one-directional point sink. Hence the identity `Δtotal == ledger_in − ledger_out` holds to float precision (residual 0.0, G2), and mean drift `Δtotal/P` is strictly negative (G1). No true-skill change occurs — the deflation is pure boundary flux, and it deepens when the floor is lowered (G3), because the enter-low/retire-high gap widens.

---

**1. Does the reproduced verifier match the reference byte-for-byte?** Yes. `sha256sum` = b9d14de839ae416677d7062e904a65ef494d97edeb28c556d6b381a63b5bae58 and `git hash-object` = 687c8ae09a443ea1bcfc204829d9f6cc833b7ac8, both identical to the idea-engine reference at HEAD 44bc17c; `diff` against the reference is exit 0.

**2. Does the results-dict sha256 equal the disclosed digest?** Yes. The final stdout line is `Results-JSON sha256: dcf252dd29f271a68a835046ea712256841c39fb657fc04c4f0aa8747e5855db`, identical to the digest disclosed in the head doc.

**3. Is the run deterministic?** Yes. Two separate process invocations produce byte-identical stdout (`diff` exit 0); the in-process double-run assertion `assert c1 == c2` did not raise; both invocations exit 0 (`all_pass = true`).

**4. Do all three gates pass in the pre-registered order (z_gate=3.0)?** Yes. G1 deflation_real z = −78.058838 (< −3) → G2 churn_ledger_identity residual = 0.0 (< 1e-6) → G3 robustness_deeper_floor z = −131.368189 (< −3) and shifted −797.745574 < baseline −498.683032. `all_pass = true`, `first_failing_gate = null`, exit 0.

**5. Is the churn-ledger identity exact — within-play conservation?** Yes. `baseline.max_identity_residual = 0.0` and `shifted.max_identity_residual = 0.0`, so `max_residual = 0.0` < 1e-6. Total displayed-rating change equals points-in minus points-out to float precision — games move zero net points, and all mean drift is a boundary-crossing (churn) effect, not a play artifact.

**6. Is the head SIGN read correctly — deflation with no change in true skill?** Yes. The pool mean displayed rating drifts strictly DOWN: baseline `mean_drift = −498.683032` (z = −78.06), shifted `mean_drift = −797.745574` (z = −131.37), both far past −3. True skill is redrawn independently at each churn (`gauss(mu, sigma)`), so nobody's true skill falls — the drop is the enter-low/retire-high boundary bleed, NOT the folk "zero-sum ⇒ mean-stable" null, which is rejected at ≥78σ.

**7. Does the deeper-floor shift deepen the deflation?** Yes. `g3_robustness_deeper_floor.deepens = true`: the shifted world (floor 700, K 24, churn_every 40) drifts −797.745574, more negative than the baseline −498.683032. Widening the enter-low/retire-high gap (lower floor) increases the per-churn point sink, confirming churn × floor-gap drives the magnitude.

| Gate | Card's planned gate | Verifier's ACTUAL gate |
|---|---|---|
| G1 | deflation-real: mean_drift −498.683032, z=−78.058838 (< −3), PASS | `deflation_real` z=−78.058838, pass=true (matches) |
| G2 | churn-ledger identity anchor: max\|residual\|=0.0, PASS | `churn_ledger_identity` residual=0.0, pass=true (matches) |
| G3 | robustness deeper-floor: shifted −797.745574, z=−131.368189, shifted < baseline, PASS | `robustness_deeper_floor` z=−131.368189, shifted_drift −797.745574 < baseline_drift −498.683032, deepens=true, pass=true (matches) |

---

## Recommendation: APPROVE

Byte-identical reproduction (diff exit 0, sha256 and git blob match idea-engine HEAD 44bc17c), exact digest match (dcf252dd29f271a68a835046ea712256841c39fb657fc04c4f0aa8747e5855db), deterministic (in-process assert + cross-invocation byte-identical, exit 0), and all three pre-registered gates pass in order (all_pass=true, first_failing_gate=null). The churn-ledger identity is exact (residual 0.0), confirming play conserves points and the strictly-negative mean drift (z = −78.06 baseline, −131.37 shifted) is a pure boundary-crossing sink that deepens with a lower floor — deflation with no change in true skill. The head is corroborated by the Elo "Combating deflation" section (Wikipedia, HTTP 200, fetched 2026-07-19), which documents the enter-low/retire-high mechanism verbatim.
