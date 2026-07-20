# Probe Report — VERDICT 204 · PROPOSAL 191 (Penney's game second-mover advantage)

**Ruling: QUALIFIED** — substance APPROVE; grounding qualified.

Target: PROPOSAL 191 (idea-engine control/outbox.md, 2026-07-20T01:37:04Z), lane superbot-games. Offset +13 → VERDICT 204.

## Reproduction
- Verifier `penney_game_second_mover_advantage.py` copied **byte-identical** from idea-engine `ideas/superbot-games/` (landed PR #709 @ 4933729); `diff` exits 0.
- Deterministic: two separate invocations byte-identical; the in-process double-run assertion passes. stdlib-only, SEED=20260717.
- Results-dict `sha256 = 8942324fa0c31abf11a053bb56b98306709611f73b9a2ad344fe0034d87744f4` — full 64 hex, **byte-exact match** to the disclosed digest. Method: `sha256(json.dumps(results, sort_keys=True, separators=(",",":")))`.

## Gates (proposal's own criteria: ≥3σ headline + robustness, in order)
- **G1** base headline (min z ≥ 3, all 8 first-picks beaten): PASS — min_z = 58.90958, favor_frac = 1.0, 8/8 favor P2. Worst pick HTT(100) → HHT(110): worst_mc = 0.661, worst_exact = 0.666667 (= 2/3).
- **G2** sign+magnitude (favor_frac = 1.0 & min_edge ≥ 0.05): PASS — favor_frac = 1.0, min_edge = 0.161.
- **G3** robust shift L=4 (min z ≥ 3, all favor): PASS — min_z = 27.726515, 16/16 favor P2.
- **G4** exactly-true (|MC − exact Markov| ≤ 0.02): PASS — base_dev = 0.007067, shift_dev = 0.005933.
- `all_pass = true`, exit 0.

## Grounding assessment
The grounding pin is a **house self-reference** (github.com/menno420/idea-engine@45ad3eb), which the proposer honestly disclosed is a provenance/reachability pin, **not** a content citation. The substantive support is the exact absorbing-Markov mechanism (a proof), cross-checked by seeded Monte-Carlo (G4), plus the standard Penney (1969) / Conway leading-numbers theorem.

Judgment: the mathematical claim is exact and self-certifying — its truth rests on the Markov proof reproduced firsthand (byte-exact digest), not on any external source, so the result stands (not REJECT). But the house-pin provides **no content grounding**, and for a textbook result an external content citation was readily available at zero cost: Wikipedia "Penney's game" documents the non-transitivity and the 2:1 HTT/HHT worst case; Penney (1969); Conway's leading-numbers algorithm. Because a checkable content citation was available and warranted but was substituted with a provenance-only house-pin, the grounding is thin → **QUALIFIED** rather than clean APPROVE. The proposer's honest disclosure is credited.

Recommendation: future proposals of standard/textbook results should carry an external content citation alongside the firsthand verifier; reserve house-pins for provenance only.

## Verdict
**QUALIFIED.** The claim reproduces exactly and all four gates pass in order; approved on substance with a grounding qualification (provenance-only house-pin where an external content citation was available). done-when satisfied: byte-identical results-dict digest with all_pass=true, G1 ∧ G2 ∧ G3 ∧ G4 holding in order.
