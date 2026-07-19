# VERDICT 188 — the pie-rule opening trap (reproduce PROPOSAL 175)

Under the PIE RULE (swap rule / cut-and-choose), the first player names an opening move and the second player may then choose to SWAP sides and inherit it. This makes an opening's raw strength NON-monotone in its value to the mover: the STRONGER the opening, the more certainly the opponent swaps to steal it, so a first player who ranks openings by win-probability and plays the strongest one hands the advantage away and LOSES. The mover's realised value is min(p, 1−p) over the swap decision, maximised not at the strongest move (p→1) but at the most BALANCED one (p→½): the pie rule rewards fairness, not force, and ranking openings on raw strength systematically selects the trap. This card reproduces the round-41 verifier and rules on it. **This card is provisional — work in-progress.**

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD:** this card lands `in-progress` on its first commit to hold the PR red under the substrate-gate, and flips to `complete` on the last commit once the reproduction below is recorded (sim directory, run-stdout, probe report in place and the heartbeat stamped). Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective

Reproduce `ideas/<lane>/pie_rule_opening_trap.py` (idea-engine, PROPOSAL 175) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered z-gates (G1 → G2 → G3) against the proposal's own pre-registered criteria, verify grounding live, and rule. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)

- Verifier sim copy (intended): `sims/verdict-188-pie-rule-opening-trap/pie_rule_opening_trap.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/<lane>/pie_rule_opening_trap.py` @ idea-engine main `TBD` (PROPOSAL 175, PR TBD). Reference file sha256 `TBD`, git blob `TBD` (to be read at HEAD; sim-copy match to be reconfirmed at copy time).
- Offset authority: PROPOSAL 175 → VERDICT 188 (+13), round-41 slot (P172→V185, P173→V186, P174→V187, next slot in the ladder).
- Pinned world constants (from the verifier, not invented): SEED=20260717 (in-source, env-inert) · Z_GATE=3.0 · TRIALS TBD. Mover realised value under the pie rule = min(p, 1−p) where p is the opening's win-probability for the mover; the swap decision keeps the opponent on the ≥½ side. Exact opening distributions, swap model, and per-gate trial counts to be taken verbatim from the committed verifier — TBD.
- Domain reference: the pie rule / swap rule in combinatorial games (e.g. Hex first-move advantage neutralised by the swap option). Durable anchor and live HTTP 200 recheck TBD this session.
- Disclosed digest: results-dict sha256 `TBD` (from PROPOSAL 175 gate criteria). Reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest (floats rounded 6 dp before hashing); printed to stdout, nothing written to disk. `main()` runs `compute()` twice, asserts `a == b`, canonicalizes, prints indent=2 dump, then `double_run_identical=true`, `all_pass=…`, `first_failing_gate=…`, and the `Results-JSON sha256 …` line. To be confirmed against the committed verifier.

## Constraints honored

Stdlib-only (`json`, `math`, `hashlib`, `random`, and any others the verifier declares); Python 3; no network and no disk writes by the verifier. SEED pinned in-source (`SEED = 20260717`); the file does not import `os` and reads no env var (env override expected inert). Verifier to be copied byte-identically (diff exit 0); no edits. Gates evaluated against the proposal's own pre-registered thresholds, not re-invented. Determinism to be confirmed across two separate invocations plus the in-process double-run assert.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — the swap steals the strongest opening: over the opening distribution, ranking by raw win-probability selects a move the opponent swaps into, so the mover's realised value min(p, 1−p) is strictly BELOW the balanced-opening value; pass = (realised-value gap / se ≥ 3.0) and (mean gap in the trap's favour). Proposal targets: TBD. Measured value TBD.
- G2 — the balanced opening is the pie-rule optimum: choosing the opening closest to p=½ maximises the mover's realised value against a swapping opponent; pass = (delta-value z ≥ 3.0) and (mean delta > 0 for the balanced move over the strongest move). Proposal targets: TBD. Measured value TBD.
- G3 — robustness under a shifted / noisier opening distribution or an imperfect swap decision: the ordering (strength ranks the trap, balance ranks the optimum) survives; pass = (mean gap / se ≥ 3.0) and (mean gap > 0). Proposal targets: TBD. Measured value TBD.
- all_pass = G1 AND G2 AND G3 (proposal reports **true**; to be reproduced). Measured TBD.

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Target: diff exit 0; reference file sha256 `TBD`, git blob `TBD`. Sim-copy hashes TBD.
2. Does the results-dict digest reproduce byte-exact? Target: printed `Results-JSON sha256 TBD` == disclosed. Reproduction TBD.
3. Is the run deterministic across invocations? Target: two separate `python3` runs byte-identical (diff exit 0) plus the in-process `assert a == b` double-run equality. Reproduction TBD.
4. Is the SEED honestly pinned? SEED=20260717 is a module-level source constant; the file imports no `os` and reads no env var — to be confirmed against the committed verifier.
5. Do all three gates pass in order with z ≥ 3.0? Target: TBD; all_pass=true, no failing gate. Measured TBD.
6. Is the mechanism sound, not a strawman? The mover's realised value is min(p, 1−p) because a rational opponent swaps whenever p>½; a stronger opening (higher p) therefore yields the opponent a stronger stolen position, and the mover is left below the swap floor — the trap is a consequence of the swap rule, not an artificially weak baseline. To be confirmed from the numbers.
7. Does grounding document the specific head? The pie rule neutralises first-move advantage and makes the strongest opening a liability under a swapping opponent; the durable anchor is the swap-rule definition and the min(p, 1−p) payoff algebra, not a verbatim heading string. Live HTTP 200 recheck TBD.
8. Real game-theory phenomenon or textbook toy? The swap rule is used in practice (Hex, Twixt and other first-move-advantaged games) precisely to force the opener toward a balanced move; the head is that ranking openings on raw strength selects the trap, with the balanced opening the honest optimum. To be affirmed in Outcome.

## Outcome

Reproduction pending — this card is born-red and `in-progress`. Measured results, verifier byte-identity, determinism, digest match, per-gate numbers, grounding recheck, and the ruling will be recorded here on the flip to `complete`, at which point the verdict high-water advances V187 → V188 (union-max, no regress). Contents above are provisional until the reproduction lands.

- **Verifier byte-identity:** TBD.
- **Determinism:** TBD.
- **Digest:** TBD.
- **Gates in order (measured vs proposal target):** TBD.
- **Grounding:** TBD.
- **Reproduction record paths:** `sims/verdict-188-pie-rule-opening-trap/{pie_rule_opening_trap.py, run-stdout.txt, probe-report.md}` (to be created).

**Ruling: PENDING** (born-red HOLD; verdict rendered here once the reproduction is in).

## ⟲ Previous-session review

VERDICT 187 (the IRR speed trap, reproduce PROPOSAL 174, round-41 VENTURE slot) landed APPROVE at sim-lab #261 (merge 5710bb2): results-dict digest `552e98a0…b3f2736f` MATCH, verifier byte-identical (file sha256 `13ecd4b4…6e1b0547`, git blob `3fb977e6…3067a`), all three gates PASS (G1 z=789.30, G2 delta-IRR z=756.06 / delta-MOIC |z|=1093.34, G3 z=251.42) on the proposal's own thresholds. The same reproduce-then-rule discipline carries here. This card continues the loop at the next slot (P175 → V188, +13) and, on its flip to `complete`, advances the verdict high-water V187 → V188 by union-max; no regression.

## 💡 Session idea

The last three heads (jitter herd, IRR speed, pie-rule swap) are all metric-non-monotonicity traps: a naive ranking (raw retry schedule, raw dollars-returned, raw opening strength) inverts once the strategic mechanism (jitter decorrelation, timing normalisation, the swap option) is priced in. A follow-up could pull these into one "selection-inverting metric" catalogue and pre-register the shared gate shape — a signed realised-value gap between the naive-optimal and the mechanism-aware-optimal choice — so future proposals in this family reuse a single audited harness instead of re-deriving the z-gate each time.

**Recommendation: HOLD (born-red). Card lands `in-progress` to keep the PR red under the substrate-gate; on reproduction it will confirm the disclosed digest and G1/G2/G3 against PROPOSAL 175's own thresholds and, if they match, APPROVE and advance the verdict high-water V187 → V188 (union-max, no regress).**
