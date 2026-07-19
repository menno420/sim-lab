# VERDICT 183 — term-sheet winner's curse (reproduce PROPOSAL 170)

The investor who wins a competitive VC round systematically overpays: with K bidders each forming an unbiased but noisy estimate of the company's intrinsic value and the highest bid winning, the winning valuation is the maximum order statistic of K unbiased draws and is therefore biased above true value — the classic common-value-auction winner's curse (Capen–Clapp–Campbell 1971). Reproduction of `term_sheet_winners_curse.py` at SEED=20260717 is byte-identical across invocations, the results-dict digest matches the disclosed `e5cdbfec…`, and all three pre-registered gates pass.

> **Status:** `complete`
> 📊 Model: Claude Opus · high · verdict-reproduction

**Born-red HOLD.** This card lands `in-progress` on its first commit to hold the PR red under the substrate-gate; it flips to `complete` on the last commit once the sim directory, run-stdout, and probe report are in place and the heartbeat is stamped. Red until the flip is the HOLD, not a defect.

## Objective
Reproduce PROPOSAL 170 (round-40 VENTURE slot, mapped to VERDICT 183 at the +13 offset) from a byte-identical copy of its verifier, confirm determinism and the disclosed digest, and evaluate the proposal against its OWN pre-registered gates G1 → G2 → G3. Factual reproduction only; verdict rendered in Outcome.

## GROUNDING (verified at HEAD)
- Verifier (sim copy): `sims/verdict-183-term-sheet-winners-curse/term_sheet_winners_curse.py`
- File sha256: `30f4c776a29061ea98144afdd6d5af7b2807bb8b32b67869f2a74a0079cd1dca`
- Git blob: `93eac4e6c3c758c8f99411eeff28a24ca9cfd471`
- Idea-engine source: `ideas/venture-lab/term_sheet_winners_curse.py`, landed in PR #655 (merge SHA `814ddbf`); copied byte-identically (diff exit 0).
- Offset authority: +13 (P168 to V181, P169 to V182); P170 to V183, round-40 VENTURE slot.
- Pinned world: SEED=20260717 · V0=1.0 · sigma=0.25 · sigma_heavy=0.35 · TRIALS=200000 · K in {2,8} · z_gate=3.0 · gaussian primary, Laplace robustness · bidders unshaded (bid = own estimate), winner = highest bid.
- Domain reference: Winner's curse (common-value auction; the max order statistic of K unbiased noisy estimates is biased high; Capen–Clapp–Campbell 1971) — https://en.wikipedia.org/wiki/Winner%27s_curse — verified live HTTP 200 this session.
- Disclosed digest: `e5cdbfec872e5879a66c13029e003fd37b8a8aa72738ec2b1ba7e18030b8e4f7`
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest.

## Constraints honored
- Verifier copied byte-identically from the idea-engine source; no edits.
- Stdlib-only (`json`, `hashlib`, `math`, `random`); Python 3.11.
- Seed pinned in-source (`SEED = 20260717`); no environment override.
- Gates evaluated against the proposal's own pre-registered thresholds, not re-invented.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3
- G1 — winner overpays and the overpayment deepens with K (gaussian): mean winner excess (V0 minus winning bid) negative and z>=3, and more negative at K=8 than K=2 with z>=3 on the difference.
- G2 — conditional-on-winning reversal: an unconditional single arbitrary bidder is unbiased (about 0) while the winner overpays, gap negative with z>=3.
- G3 — heavy-tail robustness (Laplace, sigma_heavy=0.35): winner still overpays at K=8 and deepens vs K=2, both z>=3.

## Probe questions (independent-audit checklist)
**1.** Is this the winner's curse or merely "max > mean" restated? The max of K unbiased draws having positive expected deviation IS the winner's curse; the economic claim is that a rational-looking winner overpays, which the −0.356 mean excess on V0=1.0 (about 36% overpayment at K=8) demonstrates.
**2.** Are the z>=3 values just an artifact of TRIALS=200000? Large N sharpens the z-statistic, but the effect size (mean excess −0.356, not about 0) is economically large independent of N; the gate reads both.
**3.** Is "deepening with K" trivial? It is the order-statistic prediction (bias grows in K); confirming it against the alternative that overpayment is flat in K is a real check, and z_deepens=373.85 (gaussian) rejects flatness.
**4.** Is the G2 reversal an artifact of different draw counts? The unconditional bidder is a single unbiased estimate (+0.000385 about 0); the winner is the max of K. The reversal is exactly the conditioning-on-winning effect, not a sampling artifact.
**5.** Gaussian-only artifact? G3 repeats under a heavier-tailed Laplace world and the curse deepens (−0.501 at K=8), so it is not tail-shape-specific.
**6.** Is determinism real? Cross-invocation `diff` exit 0 and the results-dict sha256 reproduces to the disclosed `e5cdbfec…`.
**7.** Cherry-picked sigma/K? Two K values and two distributions all pass; the direction is monotone, consistent with theory.
**8.** Real venture phenomenon or textbook toy? A term-sheet auction is a common-value auction on the company's intrinsic worth; the model maps the textbook result onto the round directly.

## Outcome
**APPROVE.** Reproduction is byte-exact and every pre-registered gate clears on the proposal's own criteria:
- Determinism: two separate invocations byte-identical (`diff` exit 0); in-process double-run identical (`double_run_identical=true`).
- Digest: results-dict sha256 `e5cdbfec…30b8e4f7` MATCHES the disclosed value.
- G1 (gaussian): mean excess K=2 −0.141221, K=8 −0.355814; z_winner_overpays 1041.75, z_deepens_with_n 373.85. PASS.
- G2 (reversal): unconditional +0.000385 (about 0) vs winner −0.355814; z_reversal 544.53. PASS.
- G3 (Laplace): mean excess K=2 −0.185565, K=8 −0.500907; z_winner_overpays 730.51, z_deepens_with_n 330.73. PASS.
- `all_pass=true`.

## ⟲ Previous-session review
VERDICT 182 (square-root safety staffing, reproduce P169) landed APPROVE at merge; its card and sim dir (`sqrt_safety_staffing.py`, digest `2597a505…`) are contiguous on main. This card continues the loop at the next slot (P170 to V183, +13) and advances the verdict high-water V182 to V183 by union-max; no regression.

## 💡 Session idea
The verifier reads winner excess against a known V0. A follow-up could report the winner's post-close realized return distribution (excess folded through a dilution/exit multiple) so the curse is expressed in fund-return units rather than valuation units — closer to how an LP would feel it.

**Recommendation: APPROVE — reproduce PROPOSAL 170; digest matches, all three gates pass on the proposal's own thresholds.**
