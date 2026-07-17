# VERDICT 111 — the referral bonus that maximizes viral coefficient R0 is strictly larger than the one that maximizes profit, so tuning for maximum virality overspends

> **Status:** `parked — verified, unlandable this session`
> 📊 Model: claude-sonnet-5 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD). PARKED, not
flipped to complete: the sim is written, run, and verified (all 3 gates
PASS, twins agree, 9/9 self-checks, byte-identical double run), and this
branch is pushed to origin — but this session's GitHub REST/GraphQL access
is disabled end-to-end (see `docs/CAPABILITIES.md` 2026-07-17 append: `gh
pr create`, `gh api .../pulls`, and even a Contents-API GET all refuse with
"GitHub access is not enabled for this session"). No PR could be opened, so
nothing can land this session. git-transport push/clone works fine (that's
how this branch exists on origin). Next session/venue with working GitHub
REST access: open the PR from this branch as-is (claim + sim + results are
already committed), verify the gates once more if you like, then flip this
card to complete as the normal last step.

## Objective
Independent stdlib-only reverification of idea-engine PROPOSAL 098 (2026-07-17T~15:47Z, sim-ready), offset +13 (P098 → V111), the round-22 venture slot: under a subcritical Galton-Watson referral cascade with a saturating per-attempt conversion probability q(b) and a bonus paid per successful referral, does profit Pi(b) peak at an INTERIOR bonus b*=4.5 whose viral coefficient R0=0.671 is strictly below the R0-maximizing bonus b_viral=8.0 (R0=0.736) — i.e. is "tune the referral bonus for maximum virality" a value trap that strictly overspends relative to the profit-optimal bonus?

## Constraints honored
- stdlib-only (random, math, json, hashlib), hermetic, deterministic (byte-identical double run verified: two full-process runs produced an identical results.json / sha256).
- Independent reimplementation from the registered spec, NOT the proposal's disclosed verifier (idea-engine ideas/venture-lab/referral_value_trap.py): own SEED=427100 (vs the proposal's disclosed 20260717), own N=3000 replications/level (vs 2000), offspring drawn as K independent Bernoulli(q) trials summed per individual rather than a categorical draw from a pre-built Binomial CDF.
- Pre-registered gates R1→R3 evaluated in the proposal's own order, verdict never softened; two independent gate-logic evaluators (if-chain vs table-driven scan) must agree on PASS/FAIL and first-failing-gate; 9/9 self-checks gate exit 0.

## Gate plan (from the proposal's pre-registration, unchanged)
- R1 (branching-anchor MATCH): |E_sim[T] − S/(1−m(b*))| / SE_T < 3σ.
- R2 (interior optimum): Pi̅(b*) exceeds BOTH Pi̅(0) and Pi̅(B_HI=6.0) by ≥3σ each.
- R3 (value-trap headline): Pi̅(b*) exceeds Pi̅(b_viral=8.0) by ≥3σ.

## ⟲ Previous-session review
Prior loop P097 → V110 (the long chain, K-lane process flexibility) landed APPROVE — sim-lab PR #183, sims/verdict-110-long-chain/. V110's independent-reimplementation discipline (own seeds, twin evaluators required to agree, gate-outcome CONFIRM over digit-level reproduction) carries into this slice. This is also the first slice of a fresh coordinator successor seat — the prior coordinator session ended via owner session-ender (~16:10Z 2026-07-17, idea-engine PR #488); the failsafe wake found the pacemaker chain closed and is resuming the standing continuous-pipeline mandate (idea-engine control/inbox.md ORDER 003/004/016) from this baton item, per idea-engine control/status.md's "successor's first pull" note.

## 💡 Session idea
The load-bearing gate is R3 (value trap): R1 only confirms the sim implements the branching process the closed form rests on, and R2 only establishes b* is a genuine interior peak rather than a monotone endpoint. R3 is what actually falsifies the folk belief — it says the SAME bonus that would be chosen by "maximize R0" strictly loses money relative to b*. A natural next slice if this verdict lands: the proposal's own model-basis caveat (§ "Model basis") flags that a flat one-time referral cost or a linear/convex q(b) can shrink or erase the b* < b_viral gap — a follow-up VERDICT sweeping the cost-structure assumption (per-referral vs flat bonus) would pin down how load-bearing the "saturating + per-referral" combination actually is, rather than leaving it as a declared-but-unswept caveat.

📊 Model: claude-sonnet-5 · high · verdict-sim
