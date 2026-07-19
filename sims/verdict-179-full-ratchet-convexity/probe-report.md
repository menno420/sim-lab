# VERDICT 179 — full-ratchet anti-dilution convexity: probe report (reproduced)

Reproduced from the committed verifier `sims/verdict-179-full-ratchet-convexity/full_ratchet_convexity.py` — a byte-identical copy of idea-engine `ideas/venture-lab/full_ratchet_convexity.py` at HEAD 0cb2904 (file sha256 fc0893116e302ad8dbe97d14d96f5e97a0d1c35ae663248784b09561db01c62b, git blob a5c514fc24c223f09e144991c8d9baaab14c154b). SEED = 20260717 pinned in-source at line 54. Full run output in `run-stdout.txt`.

**Math sanity note.** The full-ratchet share transfer is dAD_FR = N_A·(1/p − 1) = N_A·(1−p)/p = N_A·d/(1−d), with p = 1−d the survival factor and d the drop. Its second difference in the drop, dAD_FR(2d) − 2·dAD_FR(d) = N_A·[2d/(1−2d) − 2·d/(1−d)] > 0 for d ∈ (0, ½), so the transfer is strictly convex (super-linear) in the drop — doubling the drop more than doubles the shares transferred. The weighted-average conversion price CP = P_old·(A+B)/(A+C) with B = money/P_old, C = money/P_new gives a smaller adjustment than the full-ratchet CP = P_new for every positive raise, so full-ratchet founder loss exceeds weighted-average founder loss (G1). (The coordinator-brief shorthand "N_A·d/(1−p)" reduces to N_A since 1−p = d; the correct exact form used by the verifier and head doc is N_A·d/(1−d).)

---

**1. Does the reproduced verifier match the reference byte-for-byte?** Yes. `sha256sum` = fc0893116e302ad8dbe97d14d96f5e97a0d1c35ae663248784b09561db01c62b and `git hash-object` = a5c514fc24c223f09e144991c8d9baaab14c154b, both identical to the idea-engine reference at HEAD 0cb2904; `diff` against the reference is exit 0.

**2. Does the results-dict sha256 equal the disclosed digest?** Yes. The final stdout line is `sha256: c6c1278f5acb6cc59992e7d4300e69edfc713bef0168cd9571e85c4677c18b59`, identical to the digest disclosed in the head doc.

**3. Is the run deterministic?** Yes. Two separate process invocations produce byte-identical stdout (`diff` exit 0); the in-process double-run assertion `canonical(a) == canonical(b)` did not raise; process exit code 0 (`all_pass = true`).

**4. Does gate G1 (full-ratchet loss > weighted-average loss) pass?** Yes. `G1_fr_minus_wa_loss` mean = 0.012813, se = 8.2e-05, z = 155.70736 (≥ 3.0), pass = true. Full-ratchet founder loss strictly exceeds broad-based weighted-average founder loss on the paired scenarios.

**5. Does gate G2 (share-transfer convexity) pass?** Yes. `G2_transfer_convexity` mean = 0.028025, se = 0.000336, z = 83.28419 (≥ 3.0), pass = true. The proportional folk belief is rejected: dAD_FR(2d) − 2·dAD_FR(d) > 0.

**6. Does gate G3 (shifted world) pass?** Yes. `G3_shifted` fr_minus_wa_loss mean = 0.013013, z = 203.899173; transfer_convexity mean = 0.112724, z = 106.647194; pass = true. Both G1 and G2 survive the heavier-preferred / larger-raise / deeper-drop world.

**7. Is the convexity claim honestly scoped?** Yes. The gated convexity (G2, and G3's transfer_convexity) is computed on the share-transfer quantity `extra_shares_full_ratchet(n_a, p) = n_a·(1/p − 1)`, not on the ownership fraction. The ownership-FRACTION second difference is reported un-gated: `nongated_fraction_convexity_mean = 0.001305` (~21× smaller than the gated transfer convexity), with a `nongated_shallow_crossover` field {drop 0.02, loss_full_ratchet 0.00207, loss_weighted_avg 0.000538, gap 0.001532}. The docstring states the fraction convexity is dampened by new-money issuance and is NOT globally positive — an honest, non-gated disclosure.

| Slot | Card's planned gate | Verifier's ACTUAL gate |
|---|---|---|
| G1 | FR founder loss > WA founder loss, z≥3 | `loss_fr − loss_wa` paired mean, z = 155.70736 (matches) |
| G2 | transfer convexity dAD_FR(2d) − 2·dAD_FR(d) > 0, z≥3 | `dad_fr2 − 2·dad_fr` on share transfer, z = 83.28419 (matches) |
| G3 | G1 and G2 in shifted world, z≥3 | shifted `g1` z = 203.90 and shifted `g2` z = 106.65 (matches) |

---

## Recommendation: APPROVE

Byte-identical reproduction, exact digest match (c6c1278f…), deterministic, all three pre-registered gates pass by wide margins, convexity honestly scoped to the share transfer, and the full-ratchet-vs-weighted-average contrast independently corroborated by a reachable primary source (DLA Piper, HTTP 200, 2026-07-19). Source-strength concern from intake resolved.
