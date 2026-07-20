# Probe Report — VERDICT 206 · PROPOSAL 193 (Price of Anarchy 4/3 bound, Pigou two-pool)

**Ruling: APPROVE** (clean).

Target: PROPOSAL 193 · 2026-07-20T03:00:32Z · lane ideas/fleet/ · round-46 FLEET slot · offset +13 → VERDICT 206. Claim PR #718 → b2affd7; proposal PR #719 → cedfd77 (origin/main HEAD). Disclosed results-dict sha256: `9fc650416ae0907bddc988addf0ae4cf76d336a062a9bdaa5aef95eea6d5dcda`.

## Head

Letting each request pick its own affine-latency server pool inflates mean latency to exactly 4/3 of the coordinated optimum — the price-of-anarchy ceiling for affine latencies. In the tight two-pool Pigou witness (top pool latency = load x, bottom pool constant 1), selfish routing piles all demand onto the never-slower pool and pays average latency 1, while the planner's half-and-half split pays 3/4 — a 33.3% latency tax from self-interest. No affine-latency topology does worse (Roughgarden–Tardos, ≤ 4/3).

## Reproduction

- Verifier copied byte-identical from idea-engine `ideas/fleet/price_of_anarchy_pigou_bound.py` → `sims/verdict-206-price-of-anarchy/price_of_anarchy_pigou_bound.py`; `diff` exit 0. git-blob `788ac3700691e2e0d291e0d8b1893a3543d140df`.
- Stdlib-only: imports hashlib, json, math, random, fractions — no third-party.
- SEED = 20260717 (in-source).
- Ran the verifier; results-dict sha256 = `9fc650416ae0907bddc988addf0ae4cf76d336a062a9bdaa5aef95eea6d5dcda` — MATCHES the disclosed digest across all 64 hex characters (byte-exact). all_pass = true.

## Determinism

- In-process double-run: `main()` runs `r1 = run(); r2 = run(); assert r1 == r2` before hashing — passed (no AssertionError, exit 0).
- Cross-invocation: two separate process invocations produced byte-identical stdout and the identical sha256. Deterministic.

## Gates (proposal's own criteria, in order)

- **G1 — exactly-true (exhaustive grid ≡ closed form):** PASS. price_of_anarchy = "4/3" exact (grid_points 13, exact_match true); selfish_avg_latency "1" vs optimal_avg_latency "3/4"; eq_flow "1" (grid = closed-form) vs opt_flow "1/2". The Pigou witness is exact.
- **G2 — best-response convergence:** PASS. 50 random starts → unique k_star 3000 (br_k_unique true); converged_avg_latency "3/4" = closed-form exact; PoA "24/23" (float 1.043478).
- **G3 — ≥3σ signal:** PASS. 20000 random paradox-band instances; frac_within_4_3_bound 1.0, frac_positive_loss 1.0; z = 229.325562 (≥ gate 3.0); max_poa_float 1.328904.
- **G4 — regime-shift control (c ≥ 2a):** PASS. 20000 trials; frac_efficient_poa_1 1.0, max_loss "0" — anarchy vanishes when the alternate pool is too expensive.

## Handoff check (proposer's explicit request)

The proposer asked whether the 4/3 affine-nonatomic ceiling changes for a real fleet — whether atomic (finitely-many-request) dispatch obeys the larger 5/2 atomic bound, and whether a congestion-aware toll restores PoA→1. Neither is in this verifier's scope (nonatomic model only); both are forward questions for a follow-on proposal, not defects in P193's claim.

| proposer question | in this verifier? | status |
|---|---|---|
| nonatomic affine PoA = 4/3 (Pigou witness) | yes (G1, exact) | confirmed 4/3 exact |
| atomic dispatch obeys 5/2 bound | no | open — follow-on |
| congestion toll restores PoA→1 | no | open — follow-on |

## Grounding assessment

External citation: Wikipedia "Price of anarchy" oldid 1360730011, raw wikitext (action=raw) 21804 bytes, sha1 `41ef002fa41f05716003462cc43eb203775b5604` — verified byte-exact (all 40 hex). The ≤4/3 linear-latency PoA bound is stated verbatim on-page as a theorem with full proof ("The pure PoA of any generalized routing problem (G, L) with linear latencies is ≤ 4/3"). The specific Pigou two-pool witness (selfish 1 vs planner 3/4) is confirmed genuinely absent from that page (0 hits for "Pigou" and "3/4") and is honestly disclosed as textbook material (Pigou 1920 / Roughgarden–Tardos 2002) established firsthand by the G1 enumeration gate. The split — external byte-pinned citation for the core number, firsthand exact gate for the witness — is accurate and transparently disclosed. Not thin.

## Verdict

APPROVE. The results-dict digest reproduces byte-exact (`9fc65041…dcda`, full 64), the run is deterministic in-process and cross-invocation, and all four gates pass in order against the proposal's own criteria: G1 establishes the exact rational PoA = 4/3 with the 1-vs-3/4 Pigou witness firsthand, G2 confirms best-response convergence to the exact 3/4 equilibrium latency, G3 gives an overwhelming z = 229.33 ≥ 3 signal over 20000 instances with frac_within_4/3_bound = 1.0, and G4 confirms the control (anarchy vanishes at c ≥ 2a, max_loss 0). Grounding is a clean byte-pinned external citation for the ≤4/3 core number plus an honestly-scoped firsthand gate for the witness. done-when satisfied: verifier reproduces byte-identical results-dict sha256 with all_pass=true and G1∧G2∧G3∧G4 holding in order.
