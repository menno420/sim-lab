# VERDICT 188 — the pie-rule opening trap (reproduce PROPOSAL 175)

Under the PIE RULE (swap rule / cut-and-choose), the first player names an opening move and the second player may then choose to SWAP sides and inherit it. This makes an opening's raw strength NON-monotone in its value to the mover: the STRONGER the opening, the more certainly the opponent swaps to steal it, so a first player who ranks openings by win-probability and plays the strongest one hands the advantage away and LOSES. The mover's realised value is min(p, 1−p) over the swap decision, maximised not at the strongest move (p→1) but at the most BALANCED one (p→½): the pie rule rewards fairness, not force, and ranking openings on raw strength systematically selects the trap. This card reproduces the round-41 verifier and rules on it.

> **Status:** `complete`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD:** this card lands `in-progress` on its first commit to hold the PR red under the substrate-gate, and flips to `complete` on the last commit once the reproduction below is recorded (sim directory, run-stdout, probe report in place and the heartbeat stamped). Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective

Reproduce `ideas/superbot-games/pie_rule_opening_trap.py` (idea-engine, PROPOSAL 175) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered z-gates (G1 → G2 → G3) against the proposal's own pre-registered criteria, verify grounding live, and rule. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)

- Verifier sim copy (intended): `sims/verdict-188-pie-rule-opening-trap/pie_rule_opening_trap.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/superbot-games/pie_rule_opening_trap.py` @ idea-engine main `6dd9f3d` (PROPOSAL 175, PR #665, merge SHA `6dd9f3dc733301510f6571c0eb67b3858aa18379`). Reference file sha256 `7e89f6908d835cb5d9c72de6c149926ac61b20043fd537d300c21827f12f4e39`, git blob `ace21553a02343a058ed7f0a26bd58a05cd15daf` (read at HEAD; sim-copy match reconfirmed at copy time).
- Offset authority: PROPOSAL 175 → VERDICT 188 (+13), round-41 slot (P172→V185, P173→V186, P174→V187, next slot in the ladder).
- Pinned world constants (from the verifier, not invented): SEED=20260717 (in-source, env-inert) · Z_GATE=3.0 · N_GAMES=200000 games per condition. Mover realised value under the pie rule = min(f, 1−f) where f is the opening's win-probability for the mover; the swap decision keeps the opponent on the ≥½ side. Opening catalogues: BASE_OPENINGS=[0.50, 0.60, 0.70, 0.80, 0.90] (G1/G2 baseline world), SHIFT_OPENINGS=[0.50, 0.65, 0.78, 0.88, 0.95] (G3 robustness world). Each gate seeds its own `random.Random(SEED + k)` (G1 +11, G2 +22, G3 +33) and Bernoulli-samples realized wins at rate `realized_p(f, pie_rule)`; strongest = max(catalogue), most_balanced = argmin|f−0.5|. All constants taken verbatim from the committed verifier.
- Domain reference: the pie rule / swap rule in combinatorial games (e.g. Hex first-move advantage neutralised by the swap option) — https://en.wikipedia.org/wiki/Pie_rule, pinned `…/Pie_rule@1200819498` (oldid 1200819498). Durable anchor is the swap / take-over mechanic and the "neither too strong nor too weak" opening prescription. Live HTTP 200 reconfirmed this session.
- Disclosed digest: results-dict sha256 `72950442cc7509423256f28470c2281c9f79de3b601611b9feb931d083e8cb08` (from PROPOSAL 175 gate criteria). Reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest (floats rounded 6 dp before hashing); printed to stdout, nothing written to disk. `main()` runs `compute()` twice, asserts `a == b`, canonicalizes, prints indent=2 dump, then `double_run_identical=true`, `all_pass=…`, `first_failing_gate=…`, and the `Results-JSON sha256 …` line.

## Constraints honored

Stdlib-only (`json`, `math`, `hashlib`, `random`, and any others the verifier declares); Python 3; no network and no disk writes by the verifier. SEED pinned in-source (`SEED = 20260717`); the file does not import `os` and reads no env var (env override expected inert). Verifier to be copied byte-identically (diff exit 0); no edits. Gates evaluated against the proposal's own pre-registered thresholds, not re-invented. Determinism to be confirmed across two separate invocations plus the in-process double-run assert.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — the first-move edge exists WITHOUT the rule: the greedy-strongest opening (f=0.9, no swap) wins above fair; pass = (win_rate > 0.5) and (z_vs_half ≥ 3.0). Proposal target: win_rate > 0.5 by ≥ 3σ. Measured: win_rate 0.900505, z_vs_half +598.381968 → PASS.
- G2 — the trap: the SAME naive greedy-strongest opening (f=0.9) UNDER the swap rule inverts below fair, because a rational responder swaps into the 0.9-side and leaves the mover 1−0.9=0.1; pass = (win_rate < 0.5) and (z_vs_half ≤ −3.0). Proposal target: win_rate < 0.5 by ≥ 3σ. Measured: win_rate 0.10111, z_vs_half −591.72081 → PASS.
- G3 — robustness under a shifted opening catalogue ([0.50, 0.65, 0.78, 0.88, 0.95]): balanced play (opt_f=0.5) strictly dominates naive-strong play (naive_f=0.95) AND restores a fair game; pass = (gap_mean > 0) and (z_gap ≥ 3.0) and (opt within 2pp of 0.5). Proposal target: gap > 0 by ≥ 3σ with the balanced rate within 2pp of fair. Measured: opt_rate 0.50116 dominates naive_rate 0.04946, gap_mean 0.4517, z_gap +370.907761, opt_within_2pct_of_fair=true → PASS.
- all_pass = G1 AND G2 AND G3 (proposal reports **true**; reproduced). Measured: `all_pass=true`, `first_failing_gate=null`.

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Target: diff exit 0; reference file sha256 `7e89f690…f12f4e39`, git blob `ace21553…5cd15daf`. Sim-copy hashes IDENTICAL (diff exit 0).
2. Does the results-dict digest reproduce byte-exact? Target: printed `Results-JSON sha256 72950442…d083e8cb08` == disclosed. Reproduced — MATCH (exact).
3. Is the run deterministic across invocations? Target: two separate `python3` runs byte-identical (diff exit 0) plus the in-process `assert a == b` double-run equality. Reproduced — cross-invocation diff exit 0 plus the in-process double-run assert passed.
4. Is the SEED honestly pinned? SEED=20260717 is a module-level source constant; the file imports no `os` and reads no env var — to be confirmed against the committed verifier.
5. Do all three gates pass in order with |z| ≥ 3.0? Target: G1 z=+598.38, G2 z=−591.72, G3 z_gap=+370.91; all_pass=true, no failing gate. Measured: all three PASS in order, `all_pass=true`, `first_failing_gate=null`.
6. Is the mechanism sound, not a strawman? The mover's realised value is min(p, 1−p) because a rational opponent swaps whenever p>½; a stronger opening (higher p) therefore yields the opponent a stronger stolen position, and the mover is left below the swap floor — the trap is a consequence of the swap rule, not an artificially weak baseline. To be confirmed from the numbers.
7. Does grounding document the specific head? The pie rule neutralises first-move advantage and makes the strongest opening a liability under a swapping opponent; the durable anchor is the swap-rule definition and the min(f, 1−f) payoff algebra, not a verbatim heading string. Live HTTP 200 confirmed (Wikipedia "Pie rule", oldid 1200819498).
8. Real game-theory phenomenon or textbook toy? The swap rule is used in practice (Hex, Twixt and other first-move-advantaged games) precisely to force the opener toward a balanced move; the head is that ranking openings on raw strength selects the trap, with the balanced opening the honest optimum. To be affirmed in Outcome.

## Outcome

Reproduced clean. Measured results below.

- **Verifier byte-identity:** copied byte-identically from the idea-engine reference — `diff` exit 0; sim-copy file sha256 `7e89f6908d835cb5d9c72de6c149926ac61b20043fd537d300c21827f12f4e39`, git blob `ace21553a02343a058ed7f0a26bd58a05cd15daf` (both match the idea-engine reference at main `6dd9f3d`, merge SHA `6dd9f3dc733301510f6571c0eb67b3858aa18379`).
- **Determinism:** two separate invocations byte-identical (cross-invocation `diff` exit 0) plus the in-process `double_run_identical=true` (`main()` runs `run()` twice and asserts byte-identical compact-canonical serializations).
- **Digest:** printed `Results-JSON sha256 72950442cc7509423256f28470c2281c9f79de3b601611b9feb931d083e8cb08` == disclosed → **MATCH (exact)**.
- **Gates in order (measured vs proposal target):** G1 (first-move edge exists, NO pie rule; greedy-strongest opening_f=0.9) — win_rate 0.900505, z_vs_half +598.381968 (target > 0.5 by ≥ 3σ), PASS; G2 (the trap — naive-greedy opening_f=0.9 UNDER the pie rule) — win_rate 0.10111, z_vs_half −591.72081 (target < 0.5 by ≥ 3σ — the strongest opening now LOSES under the swap rule), PASS; G3 (robustness, shifted catalogue) — balanced opt_f=0.5 win_rate 0.50116 dominates naive_f=0.95 win_rate 0.04946, gap_mean 0.4517, z_gap +370.907761, opt_within_2pct_of_fair=true (target gap > 0 by ≥ 3σ, balanced within 2pp of fair), PASS. `all_pass=true`, `first_failing_gate=null`. Every field matches to the printed precision.
- **Mechanism:** under the swap rule the responder takes over the mover's side whenever f > 0.5, so the realized first-mover win prob = min(f, 1−f); the maximizer is f=0.5 (a fair game), and opening with the strongest (highest-f) move hands the advantage straight to the responder — the trap is a consequence of the rule, not an artificially weak baseline.
- **Grounding:** Wikipedia "Pie rule" — https://en.wikipedia.org/wiki/Pie_rule live HTTP 200; supports the swap / take-over mechanic and the "neither too strong nor too weak" opening prescription; pinned `…/Pie_rule@1200819498` (oldid 1200819498).
- **Reproduction record paths:** `sims/verdict-188-pie-rule-opening-trap/{pie_rule_opening_trap.py, run-stdout.txt, probe-report.md}`.

**Ruling: APPROVE.** The digest reproduced exactly and all three gates pass on the proposal's own thresholds; the algebra (realized first-mover value min(f, 1−f), maximised at the balanced f=0.5, not at the strongest opening) is textbook-sound and the mechanism is measured, not assumed. The verdict high-water advances V187 → V188 (union-max, no regress).

## ⟲ Previous-session review

VERDICT 187 (the IRR speed trap, reproduce PROPOSAL 174, round-41 VENTURE slot) landed APPROVE at sim-lab #261 (merge 5710bb2): results-dict digest `552e98a0…b3f2736f` MATCH, verifier byte-identical (file sha256 `13ecd4b4…6e1b0547`, git blob `3fb977e6…3067a`), all three gates PASS (G1 z=789.30, G2 delta-IRR z=756.06 / delta-MOIC |z|=1093.34, G3 z=251.42) on the proposal's own thresholds. The same reproduce-then-rule discipline carries here. This card continues the loop at the next slot (P175 → V188, +13) and, on its flip to `complete`, advances the verdict high-water V187 → V188 by union-max; no regression.

## 💡 Session idea

The last three heads (jitter herd, IRR speed, pie-rule swap) are all metric-non-monotonicity traps: a naive ranking (raw retry schedule, raw dollars-returned, raw opening strength) inverts once the strategic mechanism (jitter decorrelation, timing normalisation, the swap option) is priced in. A follow-up could pull these into one "selection-inverting metric" catalogue and pre-register the shared gate shape — a signed realised-value gap between the naive-optimal and the mechanism-aware-optimal choice — so future proposals in this family reuse a single audited harness instead of re-deriving the z-gate each time.

**Recommendation: APPROVE PROPOSAL 175 (the pie-rule opening trap). Reproduced byte-identical at SEED=20260717 with the disclosed digest `72950442…d083e8cb08` matching EXACTLY and G1/G2/G3 all passing on the proposal's own thresholds; the verdict high-water advances V187 → V188 (union-max, no regress below whatever is already there).**
