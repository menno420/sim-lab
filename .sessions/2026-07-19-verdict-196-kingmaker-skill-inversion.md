# VERDICT 196 — kingmaker skill-inversion (reproduce PROPOSAL 183)

Reproduces idea-engine PROPOSAL 183 (kingmaker skill-inversion) in the round-43 GAME slot: when an out-of-contention player retains a decisive residual choice, that kingmaker can reallocate the win to a lower-skill contender, so conditional on a kingmaker-active endgame the realized win ordering ranks opposite to underlying skill. The proposal's disclosed verifier is to be copied byte-identically into `sims/verdict-196-kingmaker-skill-inversion/` and re-run under `SEED=20260717` with an in-process double-run plus a separate cross-invocation, both required byte-identical, against the disclosed results-dict sha256.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · high effort · verdict-reproduction

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red until the reproduction is in. It flips to `complete` on the last commit — after the verifier copy, run stdout, and probe report are committed and the `control/status.md` heartbeat is written. This hold is the only legitimate red on this PR; any other gate failure is a real defect.

## Objective
Confirm that the PROPOSAL 183 verifier reproduces byte-identically in sim-lab under seed control, that its disclosed results-dict digest matches, and that its own gates pass on their stated criteria — then rule VERDICT 196 strictly on what the reproduction shows.

## GROUNDING (verified at HEAD)
- Verifier source: idea-engine PROPOSAL 183 disclosed verifier — [[fill: idea-engine path @ commit, file sha256, git blob]].
- Disclosed results-dict digest to reproduce: [[fill: sha256 from PROPOSAL 183 disclosure]].
- Kingmaker anchor: a non-contending player's residual decision reallocates the win independently of skill ordering. Grounding: [[fill: source URL @ pinned revision · fetched 2026-07-19]].
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
- [[fill: exact gate criteria and expected z-values once the verifier is copied]]

## Probe questions (independent-audit checklist)
**1.** Does `diff` between the sim-lab copy and the disclosed PROPOSAL 183 verifier exit 0?
**2.** Does the in-process double-run assert byte-identical results, and does a separate second invocation reproduce the same `Results-JSON sha256`?
**3.** Does that printed digest equal the disclosed target digest?
**4.** Is G1's inversion-exists z above the `Z_GATE=3.0` threshold?
**5.** Does G2 isolate the kingmaker residual-choice driver from skill-draw variance?
**6.** Does G3 keep the inversion above the null as the remaining-option skill gap narrows?

## Outcome
Pending — reproduction not yet executed. This card is the session's FIRST commit, born red per `.sessions/README.md`; Outcome and Status flip to `complete` together as the deliberate last step once the verifier copy, digest match, gate results, and probe report are committed.

## ⟲ Previous-session review
VERDICT 195 (pay-to-play cramdown, reproduce PROPOSAL 182) flipped its Outcome and Status together at reproduction confirmation, closing the card/ledger seam VERDICT 194 exposed. This session inherits that discipline: the born-red card makes in-flight work visible to parallel sessions, and the flip to complete is the single deliberate last step.

## 💡 Session idea
The kingmaker slot pairs naturally with the conversion-vs-dilution isolation pattern from VERDICT 195: both score an effect that comes from a discrete reallocation (a residual choice, a class conversion) rather than a continuous quantity change. Worth a proposal generalizing "reallocation-driven vs draw-variance-driven" scoring across the game-theory-lab endgame family.

**Recommendation: pending — hold red until reproduction confirms the digest and the gates rule.**
