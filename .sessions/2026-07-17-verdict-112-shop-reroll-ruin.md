# VERDICT 112 — shop-reroll ruin: in a K=3-item auto-battler/roguelike shop where the roll's best item is kept iff it clears an accept-threshold tau (else pay reroll cost C=0.05 and reroll), the net-utility-maximizing tau*=0.80 is strictly INTERIOR and greedy near-perfect rerolling (tau=0.95) is a value trap — U(tau)=E[M|M≥tau]−C·E[rerolls] is single-peaked below the greedy bar (P099, +13)

> **Status:** `complete`
> 📊 Model: opus-4.8 · high · review/verify

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the verdict artifacts + heartbeat.

## Objective
Reproduce idea-engine PROPOSAL 099 (2026-07-17T20:18:16Z, sim-ready), offset +13 (P099 → V112), the round-22 GAME slot: on the pinned world, is the net-utility-maximizing accept-threshold tau* strictly interior AND is greedy near-perfect rerolling (tau=0.95) strictly worse net-value? Run the DISCLOSED stdlib-only reference verifier (idea-engine `ideas/superbot-games/shop_reroll_ruin.py`) VERBATIM under the pinned SEED=20260717, confirm all three pre-registered gates hold at their thresholds, and confirm the results-dict sha256 reproduces `7d7d7ad834978e75508c0c645935d6214b97550328d07c19d5b88130c662622b` (or disclose any divergence with its boundary).

## Constraints honored
- stdlib-only (random, math, json, hashlib), hermetic, deterministic — byte-identical double run of the results dict enforced (in-process AND cross-invocation).
- REFERENCE-VERIFIER REPRODUCTION slice (run the proposal's own committed verifier verbatim, SEED-pinned, confirm the disclosed results-dict sha256) — the same posture as V111, distinct from an independent reimplementation: the proposal ships a stdlib verifier and pins the exact sha256, so the tightest verification is a byte-level reproduction of that artifact.
- SEED=20260717 is proposal-owned and SEEDLESS at the ledger (in-file pin, NOT a seed-ledger draw); no seed-ledger block consumed, next free block stays 20261730.

## Gate plan (proposal labels G1/G2/G3, all ≥3σ unless noted)
- G1 value-trap headline: U(tau*) − U(tau=TAU_GREEDY=0.95) ≥ 3σ — greedy near-perfect rerolling is strictly worse than the optimal threshold.
- G2 interior optimum: U(tau*) > U(tau=0) AND U(tau*) > U(tau=TAU_MAX=0.99), each ≥ 3σ — tau* is a genuine interior peak, not an endpoint.
- G3 analytic-anchor MATCH: simulated E[rerolls] at tau* matches the geometric count tau*^K/(1−tau*^K) within 3σ (|z| < 3).
- APPROVE iff G1 ∧ G2 ∧ G3 at their pre-registered thresholds; verdict never softened.

## Outcome — APPROVE (first-failing-gate None)
All three gates PASS, reproducing the proposal's disclosed dry-sim EXACTLY:
- G1 value-trap PASS — U(tau*)=0.854837 (se 0.000293) > U(TAU_GREEDY=0.95)=0.676363 (se 0.001021), z=**167.96σ** ≥3σ; greedy near-perfect rerolling leaves ~0.178 utility on the table.
- G2 interior optimum PASS — U(tau*)=0.854837 > U(tau=0)=0.750851 (se 0.000612) at z_vs_zero=**153.35σ** AND > U(TAU_MAX=0.99)=−0.632192 (se 0.005251) at z_vs_max=**282.75σ**, each ≥3σ; near-always-reroll is catastrophic (U<0).
- G3 analytic-anchor MATCH PASS — sim E[rerolls] at tau*=1.04947 (se 0.004612) vs geometric tau*^K/(1−tau*^K)=1.04918, |z|=**0.06σ** <3σ.

tau*=0.80 (analytic argmax of U on the GRID_STEP=0.01 grid), U(tau*)=0.854837 vs analytic 0.854918. The committed `results.json` is the CANONICAL hashed form (sort_keys, comma/colon-separated, `results_sha256` field omitted) so `sha256sum results.json` == the disclosed digest `7d7d7ad834978e75508c0c645935d6214b97550328d07c19d5b88130c662622b` — reproduced byte-identically in-process AND cross-invocation (separate `python3` process, fresh dir; stdout byte-identical, captured verbatim in `run-stdout.txt`). Verifier exits 0. Verdict never softened.

## ⟲ Previous-session review
Prior loop P098 → V111 (referral-bonus value trap) landed APPROVE — sim-lab PR #184 (merged to main, head 85f3948), sims/verdict-111-referral-value-trap/. V111's card baton explicitly named "round-22 game-slot PROPOSAL 099 → VERDICT 112 (+13)" as the successor's first pull — this session executes exactly that pull, so the handoff was accurate and complete. V111 and V112 share the reference-verifier-reproduction posture (byte-level digest match against the proposal's own committed stdlib verifier), distinct from V110's independent-reimplementation posture: the tightest check when a proposal ships a stdlib verifier and pins the exact sha256 is to reproduce that artifact byte-for-byte, and both landed to the digit. One carry-forward guard from doing both back-to-back: the P099 verifier's *own* out-path (`shop_reroll_ruin_results.json`, indent=2, WITH `results_sha256`) has a DIFFERENT sha than the disclosed digest — the digest is the canonical `json.dumps(..., separators=(",",":"))` over the dict MINUS `results_sha256`; committing that canonical form as `results.json` is what makes `sha256sum results.json` == the digest. Guard recipe: in a reproduction slice, verify the digest against the canonical hashed bytes (main()'s `canonical`/`digest`), not the verifier's indented file-write — anchor: `main()` in `shop_reroll_ruin.py`, the `canonical = json.dumps(results, sort_keys=True, separators=(",",":"))` line vs the `json.dump(results, fh, indent=2, ...)` file-write.

## 💡 Session idea
The value trap is proved under an *infinite-horizon, per-reroll-cost* model — but the real shop constraint is usually a FINITE GOLD BUDGET, not a smooth per-spin tax, and that flips the optimal policy from a fixed threshold to a STATE-DEPENDENT one. Replace "pay cost C per reroll" with "you hold B gold and each reroll costs c, so you get at most floor(B/c) rerolls," and the problem becomes a finite-horizon optimal-stopping DP: with r rerolls left, accept iff M ≥ tau_r, where the optimal bar tau_r is the continuation value V_r = E[max(M, V_{r−1})] and DECAYS as r → 0 (when you are down to your last reroll you should accept almost anything, tau_0 = 0). The natural next superbot-games slice pins B/c/K and pre-registers TWO gates: (1) the budget-aware declining-threshold policy {tau_r} strictly dominates the best single fixed threshold in expected kept-power-minus-spend at ≥3σ, and (2) tau_r is monotone non-increasing in depletion (tau_{r} ≥ tau_{r−1}, verified across the ladder), with the dominance gap WIDENING as the budget tightens (small B, where the fixed-threshold player most often runs dry mid-reroll and is forced to accept a bad item). That converts the one-number "set the accept bar at tau*" finding into the actionable roguelike-AI rule: your reroll bar should drop as your gold drops — a genuinely different mechanism (finite-horizon dynamic program vs infinite-horizon fixed point) from this slice and from the nearby combo-grace-budget-cliff (which is a combo-window budget, not an accept-threshold), seed-pinnable and ≥3σ-gateable.

📊 Model: opus-4.8 · high · review/verify
