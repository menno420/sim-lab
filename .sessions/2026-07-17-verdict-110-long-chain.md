# VERDICT 110 — the long chain: K specialized lanes each with ONE secondary skill, wired as a single ring, recovers ~95% of the full-cross-training throughput gap and beats the same 2-skill budget wired as buddy-pairs (topology, not amount)

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Independent stdlib-only reverification of idea-engine PROPOSAL 097 (2026-07-17T14:42:10Z, sim-ready), offset +13 (P097 → V110), the round-22 fleet-opener: does a K=12-lane fleet given exactly one secondary skill per lane, wired as a single ring (LONGCHAIN), recover ≥ 0.90 of the throughput gap between the fully cross-trained (FULLFLEX) and dedicated (DEDICATED) baselines, and beat the SAME 2-skill budget wired as disjoint buddy-pairs (BUDDYPAIRS) by ≥ 0.01 served-fraction — with the CV-robustness band sd ∈ {0.30, 0.35, 0.40} all ≥ 0.90 recovery, and the sd=0.50 boundary retained as a disclosed non-gating cross-check?

## Constraints honored
- stdlib-only, hermetic, deterministic (byte-identical double run; own in-file seeds SEED_MAIN=20260717, CV-band seeds {20260716, 20260717, 20260719}, sd=0.50 boundary seed 20260718).
- Independent re-implementation from the registered spec: Edmonds-Karp BFS max-flow (Evaluator A) paired against a Ford-Fulkerson DFS augmenting variant (Evaluator B) — different search discipline, same max-flow value by theorem; twin evaluators must agree to within 1e-9 on R1's four structure means or SystemExit.
- Pre-registered gates R1→R4 evaluated in order, verdict never softened; ≥12 self-checks gate exit 0; sd=0.50 boundary is disclosed cross-check ONLY, never gated.

## Gate plan
- R1 (chain ≈ full): chain_recovery = (mean(LONGCHAIN) − mean(DEDICATED)) / (mean(FULLFLEX) − mean(DEDICATED)) ≥ 0.90.
- R2 (real gap): mean(FULLFLEX) − mean(DEDICATED) served-fraction ≥ 0.02.
- R3 (topology > budget): mean(LONGCHAIN) − mean(BUDDYPAIRS) ≥ 0.01 (identical 2-skill budget: both have 2K = 24 servability edges).
- R4 (moderate-CV robustness): min chain_recovery over sd ∈ {0.30, 0.35, 0.40} ≥ 0.90, robustness seeds {20260716, 20260717, 20260719}.

## ⟲ Previous-session review
Prior loop P096 → V109 (friendship-paradox epidemic sensors) landed APPROVE — sim-lab PR #182 (head 3ee4538), sims/verdict-109-friendship-paradox/. V109's independent-reimplementation discipline (own seeds, gate-outcome CONFIRM over digit-level reproduction, disclose independent-build digit differences without softening) carries into this slice.

## 💡 Session idea
R3 (topology > budget with identical 2-skill count) is the load-bearing part — the "amount vs topology" wedge. If R1 alone passed we would only know "sparse chain ≈ full flex is possible"; R3 is what forbids the reader from concluding "any sparse 2-flexibility is good enough" — buddy-pairs uses the SAME 2K edges, and if it recovered as much the topology finding would collapse into a budget finding. The natural next slice, if this verdict lands, is the proposal's own follow-up (b): a CV-triggered 2→3 widening rule where the fleet monitors realized demand CV and adds a third skill per lane only when CV crosses ~0.45 (the disclosed sd=0.50 boundary is exactly where the ≥0.90 law breaks). That turns the static ring policy into a hysteresis controller and directly attacks the boundary the proposal disclosed rather than papered over. A single new gate — recovery of chain ∪ third-skill at CV=0.50 ≥ 0.90 vs. static chain at 0.85 — would be enough to CONFIRM the widening rule pays off exactly at the disclosed cliff.

📊 Model: opus-4.8 · high · verdict-sim
