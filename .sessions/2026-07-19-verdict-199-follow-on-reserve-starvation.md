# VERDICT 199 — follow-on reserve starvation (reproduce PROPOSAL 186)

PROPOSAL 186 claims that under a power-law venture portfolio a fund that HOLDS BACK a reserve fraction (RESERVE_FRAC=0.50) to defend its pro-rata ownership in the eventual winners earns a strictly higher fund MOIC than a "spray-and-pray" fund that deploys everything into initial checks and lets every follow-on round dilute it. Dilution is multiplicative — (1−d)^R = 0.70^4 = 0.2401 — and lands hardest on exactly the power-law winners that carry the whole return, so spray's MOIC is capped where the value lives. The edge is contributed by the defended top-decile companies, not by the extra names spray buys. This verdict reproduces that mechanism byte-identically from the disclosed verifier.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · task-class simulation-reproduction
> **Result:** reproduced — results-dict sha256 b917778d…2950f MATCH across all 64 hex, all three gates PASS, deterministic. Head honestly scoped as regime-dependent (fat-tail + steep-dilution). APPROVE.

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red. It flips to `complete` on the last commit, after the verifier copy, run stdout, and probe report are committed and the control/status.md heartbeat is written.

## Objective

Reproduce PROPOSAL 186 byte-identically in sim-lab: copy the disclosed verifier `ideas/venture-lab/follow_on_reserve_starvation.py` (idea-engine @702e168) into `sims/verdict-199-follow-on-reserve-starvation/`, run it under the in-source SEED=20260717, confirm determinism (in-process double-run plus a separate cross-invocation, byte-identical stdout), and compare the results-dict sha256 to the disclosed digest `b917778d026e7beea3aff07e8e6b8f6afad7b8df099f39a2773214f79ec2950f` across all 64 hex characters.

## GROUNDING (verified at HEAD)

The mechanism rests on standard VC reserve / pro-rata-defense practice: because venture outcomes are power-law, a fund reserves a large fraction of committed capital to buy its pro-rata in the later rounds of its winners. The grounding source — GoingVC, "Follow On in Venture Capital" (https://www.goingvc.com/post/follow-on-in-venture-capital) — states verbatim "This is why so many managers fight for pro-rata rights to maintain their ownership stake in a company" and "Being able to 'double down' on the 'winners' in a portfolio is an important factor in the success of venture fund managers, especially those at the seed stage." The gated claim — reserving capital to defend pro-rata in the power-law winners raises fund MOIC — IS live-supported.

## Constraints honored

- stdlib only (hashlib, json, math, random); Python 3.
- SEED = 20260717 (in-source), Z_GATE = 3.0, TRIALS = 50000, N_COMPANIES = 30, FUND = 100.0, INITIAL_OWN = 0.10, EXIT_SCALE = 200.0, RESERVE_FRAC = 0.50, POWER_ALPHA = 1.6, COLD_ALPHA = 1.4, DILUTION_PER_ROUND = 0.30, FOLLOW_ROUNDS = 4, WINNER_DECILE = 0.10, K_DEFEND = 3, SIGNAL_NOISE = 0.4, CONCENTRATION_GATE = 0.75.
- Verifier copied byte-identically from idea-engine @702e168 (diff exit 0).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest; no on-disk JSON.

## Gate plan (to reproduce at HEAD), order G1 → G2 → G3

- **G1 — reserves beat spray (≥3σ):** paired ΔMOIC = MOIC(reserve) − MOIC(spray) > 0 at z ≥ 3.0. Expect ΔMOIC ≈ +0.431911, z ≈ +20.93; spray MOIC ≈ 3.836963, reserve MOIC ≈ 4.268874.
- **G2 — the edge is the winners (bound):** top-WINNER_DECILE (by realised exit value) share of the gross positive paired edge ≥ 0.75. Expect share ≈ 0.823121.
- **G3 — robust under a steeper power law (≥3σ):** at COLD_ALPHA = 1.4, paired ΔMOIC > 0 at z ≥ 3.0 AND top-decile share ≥ 0.75. Expect cold ΔMOIC ≈ +1.323610, z ≈ +15.91, cold share ≈ 0.874894.
- all_pass required; Z_GATE = 3.0. The gate plan pins the SAME constants the verifier carries (d=0.30, R=4, RESERVE_FRAC=0.50) — no plan-vs-verifier divergence.

## Probe questions

1. Does the results-dict sha256 from the in-branch run match the disclosed `b917778d…` digest across all 64 hex characters?
2. Is the copied verifier byte-identical to the idea-engine source (diff exit 0)?
3. Do the in-process double-run and a separate cross-invocation produce byte-identical stdout?
4. Is the head honestly scoped as regime-dependent — reserves beat spray only where `(1−RESERVE_FRAC) > (1−d)^R` holds AND the tail is fat enough — rather than as a universal law?

## Outcome

Reproduced byte-identically under the in-source SEED=20260717 (verifier copied from idea-engine @702e168, `diff` exit 0; file sha256 `3d3805429768437fc25a1a46d14df17d95b6101645051cf4481e94c83235e391`, git blob `8cf9962dc68a12e54bc242122362f118596174ff`). The in-process double-run assert holds and a separate cross-invocation produced byte-identical stdout (`diff` exit 0). `all_pass = true`.

| Gate | Metric | Value | z | Verdict |
|------|--------|-------|---|---------|
| G1 — reserves beat spray | ΔMOIC = MOIC(reserve) − MOIC(spray) | 0.431911 | 20.933485 | PASS |
| G2 — edge is the winners | top-decile share of positive edge | 0.823121 | — | PASS |
| G3 — robust (steeper tail α=1.4) | cold ΔMOIC | 1.323610 | 15.911868 | PASS |

Base spray MOIC = 3.836963, reserve MOIC = 4.268874 (ΔMOIC +0.431911). G3 cold spray MOIC = 5.008969, reserve MOIC = 6.332579 (ΔMOIC +1.323610, share 0.874894). dilution_factor = (1−0.30)^4 = 0.2401.

Results-dict sha256 = `b917778d026e7beea3aff07e8e6b8f6afad7b8df099f39a2773214f79ec2950f` — MATCHES the disclosed PROPOSAL 186 digest across all 64 hex characters (byte-grep, count 1, no truncation).

## Scoping-honesty finding

The head is honestly scoped as REGIME-DEPENDENT, not universal. The doc's "Caveats & crossovers (honest disclosure)" section states the algebraic boundary `(1−RESERVE_FRAC) > (1−d)^R` (pinned 0.5 > 0.2401) and discloses that at a thin tail (Pareto α = 2.0) the sign reverses (ΔMOIC < 0) — an explicit concrete counterexample. The head title is conditioned "under a power-law portfolio." The shipped verifier's params (RESERVE_FRAC=0.50, d=0.30, R=4, α=1.6/1.4) match the doc's pinned constants exactly — no leftover plan-vs-verifier divergence from any re-tune. One transparency asymmetry: the tail crossover gets a concrete reversing counterexample (α=2.0) while the dilution-schedule crossover is disclosed only algebraically (the condition + "Pinned so this reads 0.5 > 0.2401"), not with a worked mild-dilution counterexample. This does not rise to over-claiming — the mechanism section states the boundary condition openly — so the ruling is APPROVE with the asymmetry noted.

## ⟲ Previous-session review

Previous-session review: V198 (bufferbloat standing queue, PROPOSAL 185) landed with digest MATCH and all gates PASS; the ruled verdict high-water is carried in the idea-engine outbox, not in sim-lab. This card follows the same born-red HOLD flow and leaves sim-lab's verdict high-water reference at V198 — V199 is ruled via the idea-engine outbox mirror.

## 💡 Session idea

The verifier defends the top K_DEFEND=3 companies off a single noisy signal (SIGNAL_NOISE=0.4). A cheap orthogonal extension: sweep RESERVE_FRAC over {0.3, 0.4, 0.5, 0.6, 0.7} at fixed d/R/α and plot mean fund MOIC — the reserve/spray trade-off predicts an interior optimum (too little reserve starves the winners, too much under-writes the initial checks), which would locate the peak the companion "reserve-ratio interior optimum" head hypothesises without modeling capital exhaustion.

**Recommendation: APPROVE — reproduced byte-identically under the in-source SEED=20260717; the results-dict sha256 matches the disclosed digest across all 64 hex, all three gates PASS in order (G1 ΔMOIC=0.431911 z=20.93, G2 top-decile share 0.823121, G3 cold ΔMOIC=1.323610 z=15.91 share 0.874894), the run is deterministic across a separate invocation, the shipped params match the doc's pinned constants with no plan-vs-verifier divergence, and the head is honestly scoped as regime-dependent (the doc discloses both the fat-tail boundary with a concrete α=2.0 reversal and the algebraic dilution condition) rather than as a universal law.**
