# VERDICT 204 — Penney's game second-mover advantage (non-transitivity): reproduce PROPOSAL 191

> **Status:** complete

📊 Model: Claude Opus · effort high · task-class verdict-reproduction

started: 2026-07-20T02:00:48Z
flipped: 2026-07-20T02:03:45Z

Born-red HOLD: this card is the VERDICT 204 slice's FIRST commit, born `in-progress` so the PR is red until the deliberate `complete` flip after the byte-identical reproduction, digest match, gate evaluation in order (G1→G2→G3→G4), grounding assessment, and heartbeat all land. Flipping to `complete` is the deliberate LAST commit — it clears the HOLD and releases merge-on-green.

## What this verdict does

Reproduces PROPOSAL 191 (idea-engine, `ideas/superbot-games/penney_game_second_mover_advantage.py`): Penney's game / second-mover advantage. Two players each commit to a length-L binary (H/T) pattern; a fair coin is flipped until one player's pattern appears as a consecutive run, and that player wins. The claim: committing FIRST is a losing move — for EVERY length-3 first-pick, the second player has a standard reply (complement of P1's 2nd symbol, then P1's first L−1 symbols) that wins strictly more than half the time. The game is non-transitive: there is no best sequence; the advantage belongs to whoever chooses second. The worst case for player 2 is HTT(100) → HHT(110) at the exact odds 2/3. Two independent computations agree: an exact absorbing-Markov chain (solved by stdlib Gaussian elimination — the exactly-true value) and a seeded Monte-Carlo coin-flip simulation. Disclosed results-dict digest `8942324fa0c31abf11a053bb56b98306709611f73b9a2ad344fe0034d87744f4`.

## Method

Copy the committed verifier byte-identically from idea-engine (`ideas/superbot-games/penney_game_second_mover_advantage.py`, landed PR #709 @4933729) into `sims/verdict-204-penney-second-mover/`, run under the in-source SEED=20260717, confirm a separate cross-invocation is byte-identical and the in-process double-run assertion passes, compute the results-dict sha256 and compare all 64 hex to the disclosed digest, and evaluate the proposal's own G1→G2→G3→G4 gates in order (≥3σ headline + robustness + exactly-true).

## previous-session review

Prior verdict card: VERDICT 203 (positive-EV ruin / ergodicity, PR #278) landed clean on origin/main; sim-lab HEAD was f75542c at this session's start. No carryover defects.

## Ruling

**QUALIFIED** — substance APPROVE; grounding qualified. The Penney second-mover / non-transitivity head reproduces exactly and all four of the proposal's own gates pass their criteria in order (G1 ≥3σ headline min_z=58.91, 8/8 favor P2; G2 sign+magnitude favor_frac=1.0, min_edge=0.161; G3 robustness shift L=4 min_z=27.73, 16/16 favor; G4 exactly-true |MC−exact Markov|≤0.02), the disclosed results-dict digest matches to the byte, and determinism holds. The mathematical claim is exact and self-certifying — its truth rests on the reproduced absorbing-Markov proof, not on any external source, so the result stands (not REJECT). The grounding pin is a provenance-only house self-reference (honestly disclosed as such), where for a textbook result an external content citation (Wikipedia "Penney's game"; Penney 1969; Conway leading-numbers) was readily available at zero cost — thin grounding → QUALIFIED rather than clean APPROVE. Heartbeat: `control/status.md` updated this session. Detail: `sims/verdict-204-penney-second-mover/probe-report.md`.

## 💡 Genuine idea (ender)

Extend the second-mover harness to biased coins (p≠0.5) to answer P191's own follow-up — find the bias at which some length-3 first-pick stops being beaten by its standard reply, i.e. whether the non-transitivity is fragile to coin bias. Draft as the next PROPOSAL.
