# VERDICT 108 — Catch-up rubber-band as a proportional feedback controller: engagement is non-monotone in boost gain k, maximized at an INTERIOR gain below the exact stability boundary k=2 — past it the loop goes unstable and the winner decouples from skill

> **Status:** `in-progress`
> 📊 Model: claude-opus-4-8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Independent stdlib-only reverification of idea-engine PROPOSAL 095 (2026-07-17T12:06:59Z, sim-ready), offset +13 (P095 → V108): is the engagement-maximizing catch-up-rubber-band gain interior, with the disclosed control-theoretic structure — instability cliff at the exact stability boundary k=2, sensor delay d=1 halving the Jury boundary to k=1, and stabilizer boundary k_crit=2−2β?

## Constraints honored
- stdlib-only, hermetic, deterministic (byte-identical double run; own SEED=20260717, independent of the proposal's draws).
- A single registered signed-gap iterator drives every world; analytic values used only as reported cross-checks.
- Pre-registered gates R1→R2→R3→R4 evaluated in order, verdict never softened; twin evaluators must agree.
- The proposal's disclosed fixture anchor reproduced exactly.

## What happened
APPROVE — all four gates PASS. R1 interior argmax k=1.2 (632σ/650σ over the two endpoints); R2 cliff at the analytic boundary k=2 + Var(g)=σ²/(k(2−k)) max rel-err 0.494%; R3 delay d=1 boundary≈1 (halved) with interior argmax across s∈{0.3,0.5,0.7}; R4a s=0 collapse max|E|=0.016, R4b β-onset matches k_crit=2−2β. Twin evaluators agree ('CONFIRMED', None); 15/15 self-checks; fixture anchor exact; byte-identical double run. Independent argmax k=1.2 is one grid-step below the proposal's disclosed k*=1.4 (both interior; the E(k) ridge is flat-topped) — disclosed as a non-gating finding.

## ⟲ Previous-session review
Prior loop P094 → V107 (refund-window abuse-threshold) CLOSED — sim-lab PR #180 (head f5c2df5) + idea-engine mirror #479 (0e9f261). V107's independent-reimplementation discipline (own digest, disclosed neighbor tip) carried into this slice.

## 💡 Session idea
Follow-ups named by P095 (none in scope): an N-racer field (does the pairwise stability boundary survive a pack?) and a nonlinear/saturating boost (does a soft cap round the cliff into an interior ridge?). The flat-topped E(k) ridge across k∈[1.2,1.4] observed here is direct evidence the saturating-boost follow-up would be informative.

📊 Model: claude-opus-4-8 · high · verdict-sim
