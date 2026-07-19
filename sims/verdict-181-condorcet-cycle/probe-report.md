# VERDICT 181 — Condorcet voting-cycle paradox: probe report (reproduced)

Reproduced from the committed verifier `sims/verdict-181-condorcet-cycle/condorcet_voting_cycle.py` — a byte-identical copy of idea-engine `ideas/fleet/condorcet_voting_cycle.py` at HEAD 11bb533 (file sha256 259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def, git blob f349dfa78e4c6a1012858d4fc0aab95daa678578). SEED = 20260717 pinned in-source at line 27. Full run output in `run-stdout.txt`.

**Math sanity note.** With m candidates and impartial-culture voters (each voter draws a uniformly random strict ranking), pairwise majority preference need not be transitive: A can beat B, B beat C, and C beat A, leaving no Condorcet winner (no alternative that beats every other head-to-head). The verifier counts, over independent trials, how often the pairwise-majority tournament on m candidates has no source node (no Condorcet winner). For m=3, n=101 voters the documented no-winner rate is ≈0.0869 (asymptotic 0.0877); the measured rate is compared both against zero (the folk "a majority always has a top choice" null) and against that documented value. The cycle probability rises monotonically with m (more candidates ⇒ more room for intransitive majorities), and persists under a tilted Plackett–Luce preference model (voters biased toward stronger candidates) rather than being an artifact of perfect symmetry — the paradox is a structural feature of majority aggregation, not a knife-edge of the uniform model.

---

**1. Does the reproduced verifier match the reference byte-for-byte?** Yes. `sha256sum` = 259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def and `git hash-object` = f349dfa78e4c6a1012858d4fc0aab95daa678578, both identical to the idea-engine reference at HEAD 11bb533; `diff` against the reference is exit 0.

**2. Does the results-dict sha256 equal the disclosed digest?** Yes. The final stdout line is `Results-JSON sha256: 70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe`, identical to the digest disclosed in the head doc.

**3. Is the run deterministic?** Yes. Two separate process invocations produce byte-identical stdout (`diff` exit 0); a fresh `random.Random(SEED)` drives every draw and the in-source assertions did not raise; both invocations exit 0 (`all_pass = true`).

**4. Do all four gates pass in the pre-registered order (z_gate=3.0)?** Yes. G1 cycles_exist z_vs_zero = +61.456062 (> 3) → G2a matches_documented_rate |z_vs_documented| = 0.443753 (< 3, equivalence to the documented rate) → G2b monotone_in_candidates step-z = [19.391074, 11.951024, 18.627769] (all > 3) → G3 robust_under_tilt z_vs_zero = +21.333696 (> 3). `all_pass = true`, `first_failing_gate = null` (not emitted; no gate fails), exit 0.

**5. Do head cycles genuinely exist — is the majority intransitive at all (G1)?** Yes. Over 40000 m=3 trials, `no_condorcet_winner = 3451`, `rate = 0.086275`, `z_vs_zero = 61.456062` — the folk null "a majority always has a Condorcet winner" is rejected at ≥61σ. Intransitive majority cycles are real and common.

**6. Is the measured rate consistent with the documented rate — sign and magnitude read correctly (G2a)?** Yes. The measured m=3 rate 0.086275 vs the documented 0.0869 (n=101) gives `z_vs_documented = -0.443753`, |z| = 0.44 < 3 — statistically indistinguishable from the disclosed value, not merely non-zero. The reproduction lands on the documented probability, not a nearby lookalike.

**7. Does the cycle probability rise monotonically in the number of candidates, and persist under a tilted model (G2b, G3)?** Yes. Scaling m over {3,4,5,7} gives rates {0.0867, 0.1789, 0.2479, 0.3685}, strictly increasing, with per-step z = [19.391074, 11.951024, 18.627769] (all > 3). Under a Plackett–Luce tilt with weights [1.0, 0.85, 0.72], `rate = 0.02225` over 20000 trials with `z_vs_zero = 21.333696` (> 3) — cycles survive at ≥21σ even when voters are biased toward stronger candidates, so the paradox is structural, not a symmetry artifact.

| Gate | Proposal's stated expectation | Verifier's ACTUAL result |
|---|---|---|
| G1 | head cycles exist: z_vs_zero ≈ +61.46 (> 3), PASS | `G1_head_cycles_exist` rate=0.086275, z_vs_zero=61.456062, pass=true (matches) |
| G2a | matches documented rate: \|z_vs_documented\| ≈ 0.44 (< 3), PASS | `G2a_matches_documented_rate` rate=0.086275, z_vs_documented=-0.443753, pass=true (matches) |
| G2b | monotone in candidates: step-z 19.39 / 11.95 / 18.63 (all > 3), PASS | `G2b_monotone_in_candidates` step-z [19.391074, 11.951024, 18.627769], m rates {3:0.0867, 4:0.1789, 5:0.2479, 7:0.3685}, pass=true (matches) |
| G3 | robust under tilt: z_vs_zero ≈ +21.33 (> 3), PASS | `G3_robust_under_tilt` rate=0.02225, z_vs_zero=21.333696, pass=true (matches) |

---

## Recommendation: APPROVE

Byte-identical reproduction (diff exit 0, sha256 and git blob match idea-engine HEAD 11bb533), exact digest match (70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe), deterministic (fresh `random.Random(SEED)` + cross-invocation byte-identical, exit 0), and all four pre-registered gates pass in order (all_pass=true, first_failing_gate=null). Intransitive majority cycles genuinely exist (G1 z=+61.46), the measured m=3 rate 0.086275 is statistically indistinguishable from the documented 0.0869 (G2a |z|=0.44), the cycle probability rises monotonically in candidate count (G2b step-z 19.39 / 11.95 / 18.63, rates 0.0867→0.1789→0.2479→0.3685), and the paradox persists under a tilted Plackett–Luce model (G3 z=+21.33, rate 0.02225) — a structural feature of majority aggregation, not a symmetry artifact.
