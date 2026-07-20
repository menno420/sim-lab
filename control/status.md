# sim-lab · status

updated: 2026-07-20T10:32Z · verdict high-water: **V220** (union-max over V219/V218, no regress).

VERDICT 220 (PROPOSAL 207 → V220, +13 offset, lane superbot-games) — **complete rent dissipation in the all-pay auction:** in a symmetric complete-information all-pay auction (prize V, n ≥ 2 risk-neutral bidders, highest bid wins, EVERYONE pays), the symmetric mixed-strategy equilibrium `F(b)=(b/V)^(1/(n−1))` burns total expected effort **exactly V, independent of n**, and every bidder's expected net payoff is **exactly zero** — adding rivals only thins the per-head slice to V/n. Reproduced on branch `claude/verdict-220-allpay` (PR #298). Ruling **APPROVE**: verifier copied byte-identical from idea-engine `ideas/superbot-games/allpay-rent-dissipation-2026-07-20.py` (`diff` source↔copy exit 0), reproduced under SEED=20260717, results-dict sha256 `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70` MATCH across all 64 hex (printed AND independently recomputed outside the verifier), deterministic (in-process double-run guard held at exit 0 + two cross-invocation processes byte-identical stdout), all three gates PASS each in its own direction (G1 EXACT-Fraction rent dissipation + break-even: revenue_residual_max=0, pi_residual_max=0 over n∈{2..8}×V∈{1,2,3,1/2}, self-certifying → G2 ≥3σ effect: n=5 measured_R=0.99836, z_below_naive=800.47 below the naive n·V/2=2.5, consistency within 3σ → G3 CONVERGENCE across 36 cells: max_dev_z=2.365573<3.0 worst cell n=8,V=2), overall `all_pass: True`. Grounding external + byte-pinned: Wikipedia "All-pay auction" oldid 1345188183, raw-wikitext sha1 `276dc7a58c201dce404fb2e3ef0006f072b01c8a`, firsthand-supports the break-even/revenue=V leg via the complete-info sentence "expected pay-offs are zero. The seller's expected revenue is equal to the value of the prize." Honest scope caveats recorded and NOT conflated (the page does not literally print "total bids=V" — exact R=V is derived firsthand from Π=0 + win-prob 1/n; the page's E[R]=1/3 worked example is the DIFFERENT incomplete-info IPV model, disclosed in Model basis) — the head is honestly scoped to complete-info, does not block APPROVE.

pointers:
- probe report: sims/verdict-220-all-pay-rent-dissipation/probe-report.md
- sim dir: sims/verdict-220-all-pay-rent-dissipation/ (verifier.py copy + run-stdout.txt + run-stdout-2.txt + probe-report.md)
- session card: .sessions/2026-07-20-verdict-220.md
- PR: #298 (branch claude/verdict-220-allpay)

health: green on main. The only red before the card flip is the designed born-red card HOLD (standing discipline); after the card flips to `complete`, merge-on-green lands PR #298. A red gate AFTER the flip is a real defect, not the HOLD.

non-contiguity: V137 (P124), V132 (P119), and the round-26 FLEET-slot V126 (P113) remain open BELOW the high-water — landing V220 does NOT imply every lower verdict is closed on both sides.

prior slice: VERDICT 219 (P206 independent positives multiply the odds — k-th-root diligence ladder, PR #298 predecessor branch `claude/verdict-219-diligence-screens`, APPROVE); high-water advanced V218 → V220 this stamp.

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
