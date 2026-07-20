# VERDICT 207 — PROPOSAL 194: newsvendor critical fractile

**Ruling: APPROVE**

## Target
PROPOSAL 194 (idea-engine, venture-lab lane), landed on origin/main: claim PR #721 → b111e75; proposal PR #722 (flip-complete 71324f5). Verifier: `ideas/venture-lab/newsvendor-critical-fractile-2026-07-20.py`, copied byte-identical into `sims/verdict-207-newsvendor-critical-fractile/`.

## Head
To maximize profit you stock a high-margin product ABOVE expected demand. The profit-maximizing order quantity is the critical-fractile quantile Q* = smallest Q with CDF(Q) ≥ (p−c)/(p−s), not the mean. For critical ratio > 1/2 (high margin) Q* sits strictly above the mean; for CR < 1/2 below; at CR = 1/2 it equals the median. The folk rule "order what you expect to sell" is exactly wrong.

## Reproduction
- Verifier copied byte-identical (`diff` exit 0); stdlib-only; SEED=20260717; process exit 0. Full stdout in `run-stdout.txt`.
- results-dict sha256 = `62acbcf62c3b94d9e6765a5681fef0ca8ba1b13c554bd6f882b653920f131b3e` — MATCHES the disclosed digest across all 64 hex.
- Determinism: in-process double-run identical (`double_run_identical=true`) AND separate cross-invocation byte-identical (`diff` exit 0, both SHAs equal).

## Gate evaluation (against the proposal's own criteria)
- **G1 — exactly-true (exact-Fraction argmax ≡ closed-form Q*): PASS.** high CR=4/5 → Q*=23, enum argmax=23, above mean 20 (exact_match); low CR=1/5 → Q*=17, below mean; mid CR=1/2 → Q*=20 = median. The headline high-margin case orders 23 > mean 20.
- **G2 — ≥3σ paired Monte-Carlo (T=200,000): PASS.** z_meandiff=133.997, z_means=50.477 (both ≫ 3, matching disclosure); mean_diff=+3.7016; Q*=23 beats mean-stocking Q=20.
- **G3 — shift/monotone CR sweep (c=0..10): PASS.** Q* grid [40,24,23,22,21,20,19,18,17,16,0]; monotone non-decreasing in CR; Q*≷median iff CR≷1/2.
- **G4 — marginal identity ΔE(Q)=(p−s)(CR−F(Q)): PASS.** Exact-Fraction equality for all Q in all three cases; sign structure ΔE>0 for Q<Q*, ≤0 for Q≥Q*.
- all_pass=true, first_failing_gate=null.

## Grounding
Wikipedia "Newsvendor model" revision 1363763252 (MediaWiki sha1 `ae457d1c0419c2c3f6aa5f911e31f98a8d7b50a0`, 2026-07-12) resolves and carries the critical fractile formula q = F⁻¹((p−c)/p). The article uses the salvage-free ratio (p−c)/p; the proposal's general (p−c)/(p−s) reduces to it exactly because all three pinned cases set salvage s=0. The caveat is fairly and honestly disclosed.

## Ruling: APPROVE
Head is correct and non-trivial (high-margin optimum strictly above the mean), all four gates pass by the proposal's own criteria, the disclosed digest matches byte-identically, output is deterministic across in-process and cross-invocation runs, and the external citation is honest.

📊 Model: Claude Opus · effort high · task-class verdict-reproduction
