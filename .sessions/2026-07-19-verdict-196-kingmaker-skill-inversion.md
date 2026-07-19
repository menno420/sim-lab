# VERDICT 196 — kingmaker skill-inversion (reproduce PROPOSAL 183)

Reproduces idea-engine PROPOSAL 183 (kingmaker skill-inversion) in the round-43 GAME slot: when an out-of-contention player retains a decisive residual choice, that kingmaker can reallocate the win to a lower-skill contender, so conditional on a kingmaker-active endgame the realized win ordering ranks opposite to underlying skill. The proposal's disclosed verifier is to be copied byte-identically into `sims/verdict-196-kingmaker-skill-inversion/` and re-run under `SEED=20260717` with an in-process double-run plus a separate cross-invocation, both required byte-identical, against the disclosed results-dict sha256.

> **Status:** `complete`
> 📊 Model: Claude Opus · high effort · verdict-reproduction

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red until the reproduction is in. It flips to `complete` on the last commit — after the verifier copy, run stdout, and probe report are committed and the `control/status.md` heartbeat is written. This hold is the only legitimate red on this PR; any other gate failure is a real defect.

## Objective
Confirm that the PROPOSAL 183 verifier reproduces byte-identically in sim-lab under seed control, that its disclosed results-dict digest matches, and that its own gates pass on their stated criteria — then rule VERDICT 196 strictly on what the reproduction shows.

## GROUNDING (verified at HEAD)
- Verifier source: idea-engine `ideas/superbot-games/kingmaker_skill_inversion.py` @ commit `d5bdd6b` (PROPOSAL 183, PR #684), file sha256 `8634096169e0c95914f22e292c7e583364ed24e70e68b2b78bd39108966cf478`, git blob `fd6e53b20b2f5a35f5b6cfe6962d5dfb18028cfb`.
- Disclosed results-dict digest to reproduce: `d928732259d7f54185db3ad5219322166bc2abd9f005667d2b1bd5873451432d`.
- Kingmaker anchor: a non-contending player's residual decision reallocates the win independently of skill ordering. Grounding: `https://en.wikipedia.org/w/index.php?title=Kingmaker_scenario&oldid=1356902639@e9cb88b52ad47a69805a725331f42fb4d6eae625` · fetched 2026-07-19.
- Seed: `SEED=20260717`; gate threshold `Z_GATE=3.0`.

## Constraints honored
- Stdlib-only Python 3 (hashlib, json, math, random); no third-party imports.
- Verifier to be copied byte-identically (`diff` exit 0 target); no edits to logic.
- Determinism: fixed seed; in-process double-run and cross-invocation both byte-identical.
- sim-lab records the reproduction only; no deploy.

## Gate plan (to reproduce at HEAD), order G1 → G2 → G3
- G1 inversion-exists: conditional on a kingmaker-active endgame, the lower-skill contender's realized win rate is significantly above the skill-implied null.
- G2 driver-isolation: the inversion is driven by the kingmaker's residual choice, not by variance in skill draws — isolate the kingmaker-active vs kingmaker-absent contrast.
- G3 robustness: the inversion persists as the skill gap between the kingmaker's remaining options narrows.
- G1 skill_is_real (stronger-win) 0.695125, z 174.525106 (>0.5) → pass; G2 inversion (spiteful kingmaker) 0.193235, z -274.378957 (<0.5, sign flip) → pass; G3 robustness (σ=1.5, spite 0.6) 0.410205, z -80.31509 (below baseline 0.695125, deepens) → pass. all_pass true.

## Probe questions (independent-audit checklist)
**1.** Does `diff` between the sim-lab copy and the disclosed PROPOSAL 183 verifier exit 0?
**2.** Does the in-process double-run assert byte-identical results, and does a separate second invocation reproduce the same `Results-JSON sha256`?
**3.** Does that printed digest equal the disclosed target digest?
**4.** Is G1's inversion-exists z above the `Z_GATE=3.0` threshold?
**5.** Does G2 isolate the kingmaker residual-choice driver from skill-draw variance?
**6.** Does G3 keep the inversion above the null as the remaining-option skill gap narrows?

## Outcome
APPROVE. Reproduction is byte-identical (`diff` exit 0) against the disclosed PROPOSAL 183 verifier; in-process double-run plus a separate cross-invocation both byte-match; the printed results-dict digest equals the disclosed target `d928732259d7f54185db3ad5219322166bc2abd9f005667d2b1bd5873451432d`; all three ordered gates pass (G1 skill_is_real 0.695125 z 174.525106; G2 inversion 0.193235 z -274.378957 sign-flip; G3 robustness 0.410205 z -80.31509 deepens; all_pass true) → VERDICT 196 = APPROVE.

## ⟲ Previous-session review
VERDICT 195 (pay-to-play cramdown, reproduce PROPOSAL 182) flipped its Outcome and Status together at reproduction confirmation, closing the card/ledger seam VERDICT 194 exposed. This session inherits that discipline: the born-red card makes in-flight work visible to parallel sessions, and the flip to complete is the single deliberate last step.

## 💡 Session idea
The kingmaker slot pairs naturally with the conversion-vs-dilution isolation pattern from VERDICT 195: both score an effect that comes from a discrete reallocation (a residual choice, a class conversion) rather than a continuous quantity change. Worth a proposal generalizing "reallocation-driven vs draw-variance-driven" scoring across the game-theory-lab endgame family.

**Recommendation: APPROVE — reproduces byte-identically, results-dict digest matches, all three ordered gates pass, grounding live.**
