# Probe report — VERDICT 196 (PROPOSAL 183 kingmaker skill-inversion)

State: reproduced — APPROVE

Reproduced 2026-07-19 20:53:48 UTC.

## Reproduction

- Verifier copied byte-identically from idea-engine `ideas/superbot-games/kingmaker_skill_inversion.py` (diff exit 0).
- File sha256 `8634096169e0c95914f22e292c7e583364ed24e70e68b2b78bd39108966cf478`; git blob `fd6e53b20b2f5a35f5b6cfe6962d5dfb18028cfb`.
- SEED=20260717, n_games=200000, z_gate=3.0, stdlib only.
- In-process double-run asserted equal (did not raise); separate cross-invocation byte-match (crossdiff exit 0).
- Emitted results-dict sha256 `d928732259d7f54185db3ad5219322166bc2abd9f005667d2b1bd5873451432d` MATCHES the disclosed target.

## Gates (proposal's own criteria)

Mechanism: the eliminated low qualifier becomes a kingmaker who picks the winner. A spiteful kingmaker targets the standings leader (stronger by skill), inverting the skill-to-win correlation.

- G1 skill_is_real_no_kingmaker — skill-decided stronger-win rate 0.695125 (> 0.5), z_vs_half 174.525106 — PASS. Without a kingmaker, real skill decides and the stronger contender wins most games.
- G2 inversion_spiteful_kingmaker — fully-spiteful stronger-win rate 0.193235 (< 0.5, the sign flip), z_vs_half -274.378957 — PASS. A fully spiteful kingmaker targeting the leader flips skill-to-win below even.
- G3 robustness_shifted_partial_spite — shifted σ=1.5 + partial spite 0.6 stronger-win rate 0.410205 (below baseline 0.695125), z_vs_half -80.31509, deepens true — PASS. The inversion persists (below baseline) under a wider skill spread and partial spite.
- all_pass = true

## Probe questions

**1.** Is the copied verifier byte-identical to the proposal head?
Yes — diff exit 0 against `ideas/superbot-games/kingmaker_skill_inversion.py`; git blob fd6e53b.

**2.** Is the output deterministic across separate interpreter invocations?
Yes — two independent runs at SEED=20260717 produced byte-identical stdout (crossdiff exit 0), and the in-process double-run asserts equality without raising.

**3.** Does the emitted results-dict digest match the disclosed sha256?
Yes — emitted `d928732259d7f54185db3ad5219322166bc2abd9f005667d2b1bd5873451432d` equals the disclosed target, full 64 hex.

**4.** What actually inverts the skill-to-win correlation?
The kingmaker. The eliminated low qualifier cannot win but can decide who does; when spiteful, it targets the standings leader — the contender who is stronger by skill — so skill starts predicting loss rather than win.

**5.** Is the sign flip real, or just noise near 0.5?
Real. G2's stronger-win rate 0.193235 sits far below 0.5 at z -274.38 — a decisive inversion, not a marginal wobble.

**6.** Does the effect survive a wider skill spread and only partial spite?
Yes — G3 shifts σ to 1.5 and sets spite to 0.6; stronger-win rate 0.410205 stays below the 0.695125 baseline (deepens true) at z -80.32, so the inversion is robust, not knife-edge.

**7.** Is the mechanism faithful to the real kingmaker scenario?
Yes — the Wikipedia grounding documents that a player unable to win can decide which other player wins, matching the verifier's eliminated-qualifier-picks-winner model.

**8.** Are the claimed z-scores reproduced, not merely asserted?
Yes — G1 z 174.525106, G2 z -274.378957, G3 z -80.31509 are all reproduced from the run at HEAD, matching the proposal's disclosed values.

## GROUNDING (verified at HEAD)

https://en.wikipedia.org/w/index.php?title=Kingmaker_scenario&oldid=1356902639@e9cb88b52ad47a69805a725331f42fb4d6eae625

Documents that a kingmaker scenario "in a game of three or more players is an endgame situation where a player who is unable to win has the capacity to determine which player among others will win" — supporting the eliminated-qualifier-picks-the-winner mechanism this head models.

**Recommendation: APPROVE — reproduces cleanly, digest matches, all three gates pass, grounding live.**
