# VERDICT 179 — full-ratchet anti-dilution convexity: a down round hands the ratcheted investor a super-linear share transfer that always exceeds broad-based weighted-average dilution

Reproduce PROPOSAL 166 (P166 → V179, +13, round-39 VENTURE slot): a down round issues new stock at price P_new = p·P_old with drop d = 1−p; a full-ratchet anti-dilution clause resets the prior investor's conversion price all the way to P_new, handing them extra as-converted shares dAD_FR = N_A·(1/p − 1) = N_A·d/(1−d), convex in the drop d. The folk belief (inverted here): "anti-dilution is anti-dilution; a d-percent down round costs founders about d-percent" — two errors, because full-ratchet is strictly worse than broad-based weighted-average, and the share transfer is convex (super-linear) in the drop, not proportional. It is NOT a claim that founders' ownership FRACTION is globally convex in the drop — new-money issuance inflates the base and dampens that second difference, so the convexity claim is scoped to the SHARE TRANSFER, disclosed honestly as a non-gated field. Three ordered z-gates (z_gate=3.0): G1 full-ratchet founder loss > weighted-average founder loss; G2 transfer convexity dAD_FR(2d) − 2·dAD_FR(d) > 0; G3 both hold in a shifted heavier-preferred / deeper-drop world. Model-basis caveat (P024 discipline): the result is a property of the standard NVCA / Venture-Deals full-ratchet and broad-based weighted-average conversion-price formulas on a normalized single-prior-investor cap table, one down round, no pay-to-play / carve-outs / forfeiture.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · high · review/verify

Born-red HOLD: this card's first commit (2026-07-19T11:02:16Z) lands `in-progress`, holding the substrate-gate red while the byte-identical verifier copy, run-stdout, and probe-report are committed; the card flips `complete` last — after the coordinator heartbeat — which releases the gate.

## Objective

Independently reproduce the PROPOSAL 166 verifier byte-for-byte in sim-lab, confirm its results-dict sha256 equals the disclosed digest, confirm determinism (in-process double-run + separate cross-invocation byte-match), evaluate the three ordered gates against the proposal's own pre-registered criteria, verify the convexity gate is scoped to the share transfer (not the ownership fraction), and rule.

## GROUNDING (verified at HEAD)

- Reference verifier: `ideas/venture-lab/full_ratchet_convexity.py` at idea-engine HEAD `0cb2904`, file sha256 `fc0893116e302ad8dbe97d14d96f5e97a0d1c35ae663248784b09561db01c62b`, git blob `a5c514fc24c223f09e144991c8d9baaab14c154b`.
- Offset authority: P166 → V179 is the constant +13 offset (confirmed P164→V177, P165→V178 at the live cards).
- Domain reference (independently strengthened): DLA Piper, "What is anti-dilution and why does it matter to me as a company founder?" (HTTP 200, fetched 2026-07-19) — "A full ratchet provision will always result in a larger conversion rate adjustment than a weighted average provision" and full-ratchet "is more detrimental to founders and other common stockholders." This explicitly documents the full-ratchet-vs-weighted-average contrast the proposer could not reach (the Wikipedia "Anti-dilution provision" title 404s; the proposer grounded on the general "Stock dilution" page, which confirms anti-dilution provisions exist but does not itself draw the contrast).
- Disclosed digest: results-dict sha256 `c6c1278f5acb6cc59992e7d4300e69edfc713bef0168cd9571e85c4677c18b59`.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — canonical (sort_keys, tight separators) JSON of the ordered results dict is hashed; digest printed after a pretty indent=2 dump; floats rounded to 6 dp.

## Constraints honored

Byte-identical verifier copy (diff exit 0); stdlib-only; deterministic seed 20260717 pinned in-source; no on-disk JSON; no self-referential digest field; verdict ruled on reproduced evidence, not the proposer's assertion.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — full-ratchet founder loss − weighted-average founder loss (paired mean > 0): mean 0.012813, se 8.2e-05, **z = 155.70736**, PASS.
- G2 — transfer convexity dAD_FR(2d) − 2·dAD_FR(d) > 0 (super-linear share transfer): mean 0.028025, se 0.000336, **z = 83.28419**, PASS.
- G3 — shifted world (heavier preferred, larger raise, deeper drops): fr−wa loss mean 0.013013, **z = 203.899173**; transfer convexity mean 0.112724, **z = 106.647194**; PASS.
- all_pass = true, first_failing_gate = null.
- Scope check: G2 and G3's convexity component are computed on the share-transfer quantity `extra_shares_full_ratchet(n_a, p) = n_a·(1/p − 1)`, NOT the ownership fraction. The ownership-FRACTION second difference is deliberately un-gated: `nongated_fraction_convexity_mean = 0.001305` (≈21× smaller than the gated transfer convexity), plus a `nongated_shallow_crossover` field at drop 0.02 — an honest disclosure that the fraction convexity is not global.

## Probe questions (independent-audit checklist)

**1. Does the reproduced verifier match the reference byte-for-byte?** — **YES.** sha256 `fc08931…db01c62b` and git blob `a5c514f…b14c154b` both match; diff against the idea-engine copy is exit 0.

**2. Does the reproduced results-dict sha256 equal the disclosed digest?** — **YES.** `c6c1278f5acb6cc59992e7d4300e69edfc713bef0168cd9571e85c4677c18b59`, identical to the disclosed value.

**3. Is it deterministic?** — **YES.** Two separate process invocations are byte-identical (diff exit 0); the in-process double-run assertion did not raise; exit code 0.

**4. Do all three gates pass on the proposal's own criteria?** — **YES.** G1 z=155.71, G2 z=83.28, G3 z=203.90 / 106.65, all ≥ 3.0; first_failing_gate null.

**5. Is the convexity claim scoped honestly (share transfer, not fraction)?** — **YES.** The gates test dAD_FR = N_A·(1/p−1); the ownership-fraction convexity is reported un-gated as 0.001305 and flagged not-global in the docstring — the caveat is disclosed, not hidden.

**6. Is the down-round algebra sound?** — **YES.** dAD_FR = N_A·(1/p − 1) = N_A·d/(1−d) is exact and convex increasing in d on (0,1); the coordinator-brief shorthand "N_A·d/(1−p)" reduces to N_A and is a mis-transcription — the verifier and head doc both use the correct N_A·d/(1−d).

## Outcome

**APPROVE.** The verifier reproduces byte-identically, the disclosed digest matches exactly, the run is deterministic, and all three pre-registered gates pass by wide margins on the proposal's own criteria. The convexity claim is honestly scoped to the share transfer, with the non-global ownership-fraction convexity disclosed un-gated. The one source-strength concern flagged at intake — that the proposer's citation (general "Stock dilution" Wikipedia page) does not itself draw the full-ratchet-vs-weighted-average contrast — is resolved: an independent, reachable primary source (DLA Piper, HTTP 200, fetched 2026-07-19) explicitly documents that full-ratchet "will always result in a larger conversion rate adjustment than a weighted average provision" and is "more detrimental to founders." The specific head therefore rests on both textbook-exact algebra and an explicit external source, not on the model's algebra alone. **Verdict: APPROVE.**

## ⟲ Previous-session review

VERDICT 178 (memoryless / constant-hazard preventive maintenance is pure waste, P165 → V178, round-39 FLEET slot) landed QUALIFIED-APPROVE and advanced the verdict high-water V177 → V178. Contiguity holds: V179 follows V178, +13 offset intact (P166 → V179), round-39 VENTURE slot. No high-water regression.

## 💡 Session idea

Next round-39 slot is the game-lane P167 (sibling, running concurrently) → V180. A future cross-cutting probe worth pre-registering: sweep the full-ratchet vs weighted-average gap across pay-to-play and carve-out variants, to map where the strict-dominance result (G1) weakens — the current model excludes those by assumption.
