# VERDICT 224 — PROPOSAL 211 (correlated-equilibrium public coin beats Nash in Chicken)

**Ruling: APPROVE**

Reproduced byte-exact; all four gates independently confirmed in their own direction; grounding caveat honest.

## Reproduction
- Source verifier: idea-engine `ideas/superbot-games/correlated-equilibrium-public-coin-2026-07-20.py`, copied byte-identical (diff exit 0) to `sims/verdict-224-correlated-equilibrium/`.
- SEED=20260717, N=200000, stdlib-only (hashlib, json, math, random, fractions).
- `results_sha256 = 33e42932057eb0ec92c04530b302a1d4cc56314ef9e702099e6d156d9bcf00fa` — FULL-64 EXACT match to the disclosed digest.
- Determinism: in-process double-run true; cross-invocation (two separate process runs) produced byte-identical digests.

## Gate evaluation (each in its own direction)
- **G1 exact CE validity + payoff — CONFIRMED.** Obedience slacks `[1, 1/2]` >= 0 under exact Fraction arithmetic: conditioned on each recommendation, obeying weakly beats deviating, so no player gains by ignoring the device — it is incentive-compatible. The device pays exactly (5, 5).
- **G2 statistical dominance — CONFIRMED.** Monte-Carlo device per-player payoff exceeds independent mixed-NE play with z = 44.05 (>> 3 sigma). Device mean -> 5 vs mixed-NE mean -> 14/3 ~= 4.667.
- **G3 robustness — CONFIRMED.** Valid CE + strict dominance across w in {5, 5.25, 5.5, 5.75, 6}; consistent with the disclosed boundary w* = sqrt(39) ~= 6.245.
- **G4 exact agreement — CONFIRMED.** Closed-form == exhaustive enumeration == 5 (Fraction-exact); per-player gap 1/3, total-welfare gap 2/3; mixed-NE payoff 14/3. Total welfare 10 > every Nash (pure 9, mixed 28/3).

Both directions of the claim hold: the three-card public device, binding on no one and obeyed voluntarily, is incentive-compatible (a correlated equilibrium) AND pays (5,5) / welfare 10, strictly above every Nash.

## Grounding (accuracy scrutinized — per the V222 lesson)
Wikipedia "Correlated equilibrium" oldid 1314415176, canonical revision sha1 `3cc56b870b48a8977dfccbba41497de9b9dc0549` (starts `3cc56b8` — confirmed against the API + action=raw). On-page and matching the verifier: the Chicken payoffs (0,0)/(7,2)/(2,7)/(6,6), the three-card 1/3 device, Aumann 1974, and the device-payoff-of-5 vs the **mixed** Nash comparison. Absent from the page: "traffic light", "mediator", "social welfare", "convex hull", and any comparison to the asymmetric pure Nash as a welfare baseline. The proposal's caveat — that the verifier ADDS the obedience-constraint proof, the total-welfare-vs-every-Nash framing, and the robustness band — accurately describes what is and isn't on the page. (The page does present a second, higher-payoff CE reaching 5.25; this does not contradict the caveat.) A well-scoped, honest disclosure — the good inverse of V222.

## Provenance
- P211: idea-engine PR #778, flip 726374c; disclosed digest 33e42932...bcf00fa.
- Claim: idea-engine PR #779 (merged).
- Reproduction: sim-lab PR #302.
- Verified at: Mon Jul 20 12:39:18 UTC 2026
