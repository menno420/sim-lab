# VERDICT 180 — MMR/Elo rating deflation: a competitive ladder's mean rating is not conserved (reproduce PROPOSAL 167)

Reproduce PROPOSAL 167 (P167 → V180, +13, round-39 GAME slot): within a fixed pool every game is a strictly zero-sum transaction — the winner gains exactly what the loser drops — so play moves zero net points and total pool rating is conserved by games alone. Mean rating therefore drifts DOWN only through boundary crossings: newcomers enter at a provisional rating floor BELOW their eventual true level, while climbers who have reached their true skill retire carrying accumulated points ABOVE the floor OUT of the pool. The enter-low / retire-high asymmetry bleeds points out at a rate set by churn, so a strictly zero-sum ladder deflates in the long run with no change in anyone's true skill. The folk belief (inverted here): "a zero-sum game conserves points, so the pool's mean rating is stable" — the error is that conservation holds only WITHIN play; the pool is open at its boundary, and churn across an enter-low/retire-high gap is a strictly one-directional point sink. Model-basis caveat (P024 discipline): the head is a property of the standard Elo update on a single closed pool with provisional-floor entry and skill-reset churn; it is a SIGN / mean-non-conservation claim (mean drift < 0, within-play ledger residual = 0), not a claim about the exact deflation magnitude, which is a function of the pinned churn rate, floor gap, and K.

> **Status:** `complete`
> 📊 Model: Claude Opus · high · review/verify

Born-red HOLD: this card's first commit lands `in-progress`, holding the substrate-gate red while the byte-identical verifier copy, run-stdout, and probe-report are committed in a separate reproduction commit; the card flips `complete` last — after the coordinator heartbeat — which releases the gate. The Outcome below is intentionally unfilled (`_Pending reproduction — filled at flip._`) in this first commit; the digest, gate statistics, and verdict are PENDING until the reproduction is proven and independently audited.

## Objective

Independently reproduce the PROPOSAL 167 verifier byte-for-byte in sim-lab under its pinned world (SEED=20260717 in-source), confirm its compact-canonical results-dict sha256 equals the disclosed digest, confirm determinism (in-process double-run assert + a separate cross-invocation byte-match), evaluate the three ordered gates against the proposal's own pre-registered criteria (z_gate=3.0), verify the churn-ledger identity (within-play conservation to float precision), confirm the head SIGN (mean rating drifts strictly negative while true skill is unchanged), and rule.

## GROUNDING (verified at HEAD)

- Reproduction verifier path (sim-lab): `sims/verdict-180-mmr-rating-deflation/mmr_rating_deflation.py` — to be a byte-identical copy (`diff` exit 0) of the idea-engine reference.
- Reference verifier: `ideas/superbot-games/mmr_rating_deflation.py` at idea-engine HEAD `44bc17c`, file sha256 `b9d14de839ae416677d7062e904a65ef494d97edeb28c556d6b381a63b5bae58`, git blob `687c8ae09a443ea1bcfc204829d9f6cc833b7ac8`.
- Offset authority: P167 → V180 is the constant +13 offset (confirmed P164→V177, P165→V178, P166→V179 at the live cards), round-39 GAME slot.
- Pinned world: SEED=20260717, z_gate=3.0; baseline R=40 ladders, P=60 pool, 15000 steps, conv_games=40, floor=1000, K=32, churn_every=50; shifted floor=700, K=24, churn_every=40.
- Domain reference: https://en.wikipedia.org/wiki/Elo_rating_system (section "Combating deflation") — HTTP 200, fetched 2026-07-19T11:38:17Z: "each game ends in an equal transaction of rating points … this prevents points from entering or leaving the system when games are played … players tend to enter the system as novices with a low rating and retire … with a high rating. Therefore, in the long run a system with strictly equal transactions tends to result in rating deflation." Documents the enter-low/retire-high mechanism exactly.
- Disclosed digest: compact-canonical results-dict sha256 `dcf252dd29f271a68a835046ea712256841c39fb657fc04c4f0aa8747e5855db`.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the ordered results dict carries no `results_sha256` field; `main()` computes the compact-canonical serialization `json.dumps(results, sort_keys=True, separators=(",",":"))`, hashes it with sha256, asserts a second independent run's canonical form is byte-identical (in-process double-run), prints a pretty indent=2 dump plus the sha256, and writes no JSON to disk; every float rounded to 6 dp before serialization.

## Constraints honored

Byte-identical verifier copy (diff exit 0, copy sha256 == source, copy git blob == source blob); stdlib-only (math, json, hashlib, random); deterministic SEED 20260717 pinned in-source; no numpy/scipy; no on-disk JSON; no self-referential digest field; verdict ruled on reproduced evidence, not the proposer's assertion; forward-only git; zero agent merge calls. The mean drift, the within-play ledger residual, and the per-regime z-statistics are measured from the drawn ladder trajectories (points moved by games vs points carried across the boundary by churn), not plugged from a closed form — so the deflation and the conservation identity are attributable to the reproduced sampling, not a tautological substitution.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — deflation-real (across R ladders the pool mean displayed-rating drift is negative at ≥3σ, z < −3, rejecting the zero-sum ⇒ mean-stable folk null): mean_drift −498.683032, z = −78.058838 (< −3), **PASS**.
- G2 — churn-ledger identity anchor (total displayed-rating change == points-in minus points-out to float precision, |residual| < 1e-6 — within-play conservation): max|residual| = 0.0, **PASS**.
- G3 — robustness deeper-floor (under a lower floor + shifted K/churn, deflation persists at ≥3σ AND deepens): shifted drift −797.745574, z = −131.368189, shifted < baseline −498.683032, **PASS**.
- all_pass = true, first_failing_gate = null.

## Probe questions (independent-audit checklist)

**1. Does the reproduced verifier match the reference byte-for-byte (diff exit 0, file sha256 and git blob matching the idea-engine identity at HEAD 44bc17c)?**

**2. Does the reproduced compact-canonical results-dict sha256 equal the disclosed digest dcf252dd29f271a68a835046ea712256841c39fb657fc04c4f0aa8747e5855db exactly?**

**3. Is the run deterministic — does the in-process double-run assert not raise, and are two separate process invocations byte-identical (diff exit 0, exit code 0)?**

**4. Do all three gates pass in the pre-registered order (G1 deflation-real → G2 churn-ledger identity → G3 robustness deeper-floor) with z_gate=3.0, all_pass=true, first_failing_gate=null?**

**5. Is the churn-ledger identity exact — does the within-play ledger residual sit at 0.0 (max|residual| < 1e-6), confirming games move zero net points and all mean drift is a boundary-crossing effect, not a play artifact?**

**6. Is the head SIGN read correctly — the pool mean rating drifts strictly DOWN (negative drift, z well past −3 in both the baseline and the deeper-floor shift) with true skill redrawn independently at churn, i.e. deflation with no change in true skill — and NOT the folk "zero-sum ⇒ mean-stable" null?**

**7. Does the deeper-floor shift DEEPEN the deflation (shifted drift more negative than baseline) rather than merely reproduce it, confirming the enter-low/retire-high gap drives the magnitude?**

## Outcome

**APPROVE.** The reproduced verifier is byte-identical to the idea-engine reference (file sha256 `b9d14de839ae416677d7062e904a65ef494d97edeb28c556d6b381a63b5bae58`), and the reproduced compact-canonical results-dict sha256 `dcf252dd29f271a68a835046ea712256841c39fb657fc04c4f0aa8747e5855db` matches the disclosed digest exactly, deterministic across the in-process double-run assert and a separate cross-invocation. All three ordered gates pass with z_gate=3.0 (all_pass=true, first_failing_gate=null): G1 deflation-real mean_drift −498.683032, z −78.06 < −3; G2 within-play churn-ledger identity max|residual| 0.0, so the drift is boundary-crossing churn and not a play artifact; G3 deeper-floor deepens the deflation to −797.745574, z −131.37, strictly below baseline. Grounding at https://en.wikipedia.org/wiki/Elo_rating_system ("Combating deflation") confirmed live — the strictly-zero-sum ladder deflates through enter-low/retire-high boundary crossings exactly as claimed, with no change in anyone's true skill.

## ⟲ Previous-session review

VERDICT 179 (full-ratchet anti-dilution convexity, P166 → V179, +13, round-39 VENTURE slot) landed a CLEAN APPROVE and advanced the verdict high-water V178 → V179: disclosed compact-canonical results-dict digest `c6c1278f5acb6cc59992e7d4300e69edfc713bef0168cd9571e85c4677c18b59` reproduced EXACTLY, verifier byte-identical (git blob `a5c514fc24c223f09e144991c8d9baaab14c154b`, file sha256 `fc08931…db01c62b`, copied from idea-engine HEAD `0cb2904`), all three gates G1 fr-minus-wa loss → G2 transfer-convexity → G3 shifted-world PASS in order (all_pass=true, first_failing_gate=null, exit 0), with the convexity claim honestly scoped to the SHARE TRANSFER and the non-global ownership-fraction convexity disclosed un-gated. DIGEST-POSTURE carry-forward unbroken: V179 and this V180 are BOTH WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. Contiguity holds: V180 follows V179, +13 offset intact (P167 → V180), round-39 GAME slot. This V180 is BORN RED and NOT yet reproduced — the digest MATCH and gate results remain PENDING until the flip commit; the verdict high-water stays at V179 until this card flips to `complete`. No high-water regression.

## 💡 Session idea

The verifier pins a strictly zero-sum Elo update with a fixed provisional floor and skill-reset churn — the case where deflation is PURE boundary-crossing bleed and the within-play ledger residual is exactly 0. The distinct next slice the head names but holds fixed is the anti-deflation frontier the Elo "Combating deflation" section documents: real ladders inject points (lower K for established high-rated players, bonus schemes for improvers, feeder pools). Pre-register (same SEED-pinned, computed-trajectory discipline): sweep a point-injection rate ι and gate (G-a) the zero-injection base reproduces the pure-deflation result — mean drift < 0 at ≥3σ, ledger residual = 0 — at the pinned floor gap; (G-b) an injection crossover — above a threshold ι* the mean drift crosses to ≥ 0 (the ladder stabilizes or inflates) driven purely by the injected points and NOT by any change in true skill; and (G-c) a conservation-persistence check — across the whole ι sweep the WITHIN-PLAY ledger residual stays at 0 (|residual| < 1e-6), proving the crossover is a pure boundary-flux effect, not a play artifact. The operator lesson sharpens from "a zero-sum ladder deflates" to "a zero-sum ladder deflates through churn alone — so stability is bought only by injecting points at the boundary, never by anything play does."
