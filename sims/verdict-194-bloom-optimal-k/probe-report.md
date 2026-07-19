# VERDICT 194 — Bloom-filter optimal-k FPR floor (reproduce PROPOSAL 181)

## Probe report

Independent reproduction of PROPOSAL 181's head: a Bloom filter's false-positive rate FPR(k) = (1 − e^{−kn/m})^k is convex (U-shaped) in the number of hash functions k, minimized at k* = (m/n)·ln2, and the achievable minimum is floored at φ = (½)^{(m/n)·ln2} ≈ 0.6185^{(m/n)} by bits-per-element alone.

**Reproduction fidelity**

- Verifier copied byte-identically from idea-engine `ideas/fleet/bloom-optimal-k-fpr-floor-2026-07-19.py` (diff exit 0; sha256 `b65a197a7044f640a9cdd23d79204d2f269aaa867fa92728b83514222706bfef`, git-blob `2e8b7ad3aaa8a1cb3ba69978e2de5297cac7ec75`).
- WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest posture: sha256 of the compact-canonical `json.dumps(sort_keys=True, separators=(',',':'))` results dict.
- Results-dict sha256 = `3fdfc867123a80a1476d414610413060c24b3580841f1d808dac10a75f8b5d7f` — MATCHES the disclosed digest (all 64 hex; confirmed both by the verifier's printed line and an independent recompute of `compute()`).
- SEED=20260717 double-run: in-process double-call asserted equal inside `main()`, AND two separate cross-invocation runs produced byte-identical stdout (diff exit 0). Both exit 0 (all_pass=true).

**Gate G1 — optimum dominance (c = 8 bits/element, m = 12000)**

Both ends of the k-sweep strictly exceed the optimum, each at ≫3σ: FPR 11.79% at k=1 (z_low_vs_opt ≈ +118.376354) and FPR 4.93% at k=12 (z_high_vs_opt ≈ +42.297910) both beat the 2.22% optimum at k* = 6 (fpr_opt 0.022213). The sweep is U-shaped, not monotone. **PASSED** (`gate_g1_optimum_dominance_pass = true`, `dom_pass = true`).

**Gate G2 — more hashes hurt (the head) + memory floor (c = 8)**

Past-optimum penalty = FPR[2k*] − FPR[k*] = +0.027067 (+2.71 points) at z ≈ +42.297910 > 0 and ≥ 3σ — extra hashes past the optimum measurably worsen false positives. The achieved optimum sits on the bits-per-element floor: fpr_opt 0.022213 (2.22%) vs φ = 0.021416 (2.14%), within TOL·φ (TOL=0.20; |Δ|/φ ≈ 3.7% ≪ 20%), closed-form predicted 0.021577 (2.16%), and no tested k beats φ by more than tolerance. **PASSED** (`gate_g2_more_hashes_hurt_and_floor_pass = true`, `penalty_sig = true`, `floor_pass = true`).

**Gate G3 — robustness under shifted config (c = 12 bits/element, m = 18000)**

The U-shape persists: FPR 8.10% at k=1 (z ≈ +129.804852) and 0.75% at k=16 (z ≈ +18.148262) both beat the 0.33% optimum at k* = 8 (fpr_opt 0.003324); past-optimum penalty +0.00416 positive at z ≈ +18.148262; optimum on floor φ = 0.003134 (0.31%), predicted 0.003142. Not an artifact of c=8. **PASSED** (`gate_g3_robust_shift_pass = true`, `dom_pass`/`penalty_sig`/`floor_pass` all true).

**Overall:** all three gates reproduce in order G1 → G2 → G3 on PROPOSAL 181's own criteria; `all_pass = true`, exit 0.

**Grounding:** https://en.wikipedia.org/wiki/Bloom_filter@15d7f16cabd1b2e9f33543aa383f4aee8a81896b (fetched 2026-07-19T19:05:56Z) — documents k* = (m/n)·ln2 minimizing FPR = (1 − e^{−kn/m})^k (Bloom 1970) and Kirsch–Mitzenmacher double hashing.

**Theory:** ε = FPR(k) = (1 − e^{−kn/m})^k is U-shaped in k. Each extra hash cuts both ways — it adds one more bit a false positive must clear (checking win), but sets one more bit per inserted key, filling the array faster (fill cost). Below k* the checking win dominates; above k* the fill cost dominates and FPR climbs. The curve is minimized at k* = (m/n)·ln2 with minimum value φ = (½)^{(m/n)·ln2}, which depends on bits-per-element (m/n) alone — k beyond k* over-saturates the array and raises the FPR, and no choice of k crosses the memory floor. The only lever that lowers φ is more bits per element.
