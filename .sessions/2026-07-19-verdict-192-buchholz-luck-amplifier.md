# VERDICT 192 — Buchholz Swiss-tiebreak luck amplifier (reproduce PROPOSAL 179)

Reproduces PROPOSAL 179's head that among players finishing tied on match points in a Swiss-system tournament, the Buchholz strength-of-schedule tiebreak ranks the luckier opponent-draw ahead of the stronger player — tracking opponent-draw luck (base p_luck 0.804910) far more than own skill (p_skill 0.597399), a ~3.13x luck-to-skill signal ratio at an even field. Buchholz measures whom you happened to play, not how good you are.

> **Status:** `complete`
> 📊 Model: Claude · effort high · verdict reproduction
> **Reproduction landed — APPROVE. Verifier byte-identical (sha256 f41f270b), results-dict digest 0e591bb4… MATCH, G1/G2/G3 all reproduce, all_pass=true.**

## Objective

Byte-identically reproduce the idea-engine verifier `swiss_buchholz_luck_amplifier.py` under SEED=20260717, confirm the disclosed results-dict sha256 `0e591bb44f57f72fdff6536417a3ba009b74dfb9c07f2c41073bdbd9876c0fa8`, and rule G1 -> G2 -> G3 against PROPOSAL 179's own criteria.

## GROUNDING (verified at HEAD)

GROUNDING: https://en.wikipedia.org/wiki/Swiss-system_tournament@1357112228 — live HTTP 200; documents Buchholz as the sum of all opponents' scores, i.e. the strength-of-schedule tiebreak this head decomposes into luck vs skill.

## Constraints honored

- stdlib-only (math, json, hashlib, random); SEED=20260717 pinned; Z_GATE=3.0.
- Verifier copied byte-identically from idea-engine (diff exit 0; sha256 f41f270b465c905a5ba1cc2655e07fb7b21ad84eab2a9037bf0c01a03f5423f8, git-blob 0d4a4b1e804dbbafebabff46cf48dc4e8ba753eb).
- WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest posture: sha256 of compact-canonical json.dumps(sort_keys=True, separators=(',',':')).
- In-process double-run asserted equal; separate cross-invocation stdout byte-matched.

## Gate plan (reproduced at HEAD), order G1 -> G2 -> G3

- **G1 — luck dominates (head):** base p_luck >= 0.70 AND z_luck >= 3.0. Expect p_luck 0.804910, z_luck 511.920239.
- **G2 — luck beats skill:** base ratio >= 3.0 AND z_diff >= 3.0 AND (p_luck − p_skill) >= 0.15. Expect ratio 3.130521, z_diff 234.751939, gap 0.207511.
- **G3 — robustness (shifted field σ=350, N=128, R=9):** dominance persists — shift p_luck >= 0.70 AND z_diff >= 3.0 AND (p_luck − p_skill) >= 0.10. Expect shift p_luck 0.870756, z_diff 265.698695, gap 0.183947. Dominance-gated, NOT ratio-gated: the shifted-field ratio compresses to 1.984682 as wider σ makes own-skill more legible — a disclosed caveat, not a failure.

## Probe questions (independent-audit checklist)

**1.** Does the sim-lab verifier copy diff byte-identically against the idea-engine source (sha256 f41f270b…, git-blob 0d4a4b1e…)?
**2.** Under SEED=20260717, does the in-process double-run assert equal and do two cross-invocation runs print byte-identical stdout?
**3.** Does the compact-canonical results-dict sha256 equal the disclosed 0e591bb44f57f72fdff6536417a3ba009b74dfb9c07f2c41073bdbd9876c0fa8?
**4.** Does the shipped G3 gate dominance (p_luck >= 0.70, z_diff >= 3, gap >= 0.10), matching this card's pre-registered G3 — i.e. no plan-vs-verifier divergence?
**5.** Is the base->shift ratio compression (3.130521 -> 1.984682) honestly disclosed, with G3 correctly gating dominance rather than the ratio?
**6.** Does G1 reproduce (base p_luck 0.804910 >= 0.70, z_luck 511.92 >= 3.0)?
**7.** Does G2 reproduce (base ratio 3.130521 >= 3.0, z_diff 234.75 >= 3.0, gap 0.207511 >= 0.15)?
**8.** Does the grounding URL resolve live and support Buchholz = sum of opponents' scores?

## Outcome

APPROVE. The idea-engine verifier copied byte-identically (diff exit 0; sha256 f41f270b465c905a5ba1cc2655e07fb7b21ad84eab2a9037bf0c01a03f5423f8, git-blob 0d4a4b1e804dbbafebabff46cf48dc4e8ba753eb) and reproduced deterministically (in-process double-run asserted equal; separate cross-invocation stdout byte-identical). Results-dict sha256 `0e591bb44f57f72fdff6536417a3ba009b74dfb9c07f2c41073bdbd9876c0fa8` MATCHES the disclosed digest. All three gates reproduce on the proposal's own criteria, all_pass=true:

- G1 (luck dominates): base p_luck 0.804910 >= 0.70, z_luck 511.920239 >= 3.0 — PASS.
- G2 (luck beats skill): base ratio 3.130521 >= 3.0, z_diff 234.751939 >= 3.0, gap 0.207511 >= 0.15 — PASS.
- G3 (robustness, σ=350 / N=128 / R=9): shift p_luck 0.870756 >= 0.70, z_diff 265.698695 >= 3.0, gap 0.183947 >= 0.10 — PASS.

Honesty: the card's pre-registered G3 is dominance-based and matches the shipped verifier's G3 exactly (no plan-vs-verifier divergence); the base->shift ratio compression (3.130521 -> 1.984682) is honestly disclosed as a caveat, with G3 correctly gating dominance not the ratio. The head — Buchholz tracks opponent-draw luck (p_luck 0.80) far more than own skill (p_skill 0.60), a systematic dominance — reproduces.

## ⟲ Previous-session review

V191 (post-money SAFE stacking tax, PR #265) landed APPROVE on a clean digest match; the lean 3-file sims/verdict-NNN layout (verifier copy + run-stdout.txt + probe-report.md) carried it. This card follows the same shape.

## 💡 Session idea

A cut-Buchholz companion head: quantify how much Median-Harkness / Modified-Median (discard highest+lowest opponent) attenuate the luck dominance vs raw Solkoff — the proposal names it out-of-scope, but it is the natural next GAME-slot decomposition.

**Recommendation: APPROVE — reproduction is byte-identical, the digest matches, all gates hold, and the gate scoping is honest.**
