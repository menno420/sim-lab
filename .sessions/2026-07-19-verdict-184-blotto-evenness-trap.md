# VERDICT 184 — the Colonel Blotto evenness trap (reproduce PROPOSAL 171)

Equal budget does NOT buy equal share: on B battlefields each won by whoever commits strictly more, a concede-and-overload allocator that abandons a minority of fields (allocates zero) and pours its whole budget over the rest wins a strict MAJORITY of battlefields against an equal-budget uniform splitter — and holds that majority while spending up to nearly HALF LESS budget. Spreading evenly is a dominated strategy; concentration beats distribution. Reproduction of `blotto_evenness_trap.py` at SEED=20260717 is targeted to be byte-identical across invocations, the results-dict digest is targeted to match the disclosed `05afdeff…`, and all three pre-registered gates (G1 → G2 → G3, plus the non-gated deficit demo) are expected to pass. **This card is provisional — work in-progress.**

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD.** This card lands `in-progress` on its first commit to hold the PR red under the substrate-gate; it flips to `complete` on the last commit once the sim directory, run-stdout, and probe report are in place and the heartbeat is stamped. Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective
Reproduce PROPOSAL 171 (round-40 GAME slot, mapped to VERDICT 184 at the +13 offset) from a byte-identical copy of its verifier, confirm determinism and the disclosed digest, and evaluate the proposal against its OWN pre-registered gates G1 → G2 → G3 (plus the non-gated deficit demo). Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)
- Verifier (sim copy, intended): `sims/verdict-184-blotto-evenness-trap/blotto_evenness_trap.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/superbot-games/blotto_evenness_trap.py`.
- Offset authority: +13 (P168 → V181, P169 → V182, P170 → V183); P171 → V184, round-40 GAME slot.
- Pinned world: SEED=20260717 · Z_GATE=3.0 · battlefields B ~ randint[8,40] · budget T=B (uniform allocation = 1.0/field) · G1 300 reps (equal budget, unit values) · deficit-demo 300 reps (d=0.4) · G3 300 reps (d=0.4, values ~ U[0.2,5.0]). Independent streams: G1 Random(SEED+11), deficit-demo Random(SEED+22), G3 Random(SEED+33); G2 is a deterministic full sweep.
- Domain reference: Colonel Blotto game — https://en.wikipedia.org/wiki/Blotto_game (permalink oldid=1346038465, fetched 2026-07-19; the uniform split is NOT uniquely optimal, the lopsided allocation is a co-equilibrium). To be re-verified live this session.
- Disclosed digest: `05afdeffd9f44721fd6e71ee4595a024541b99976176bd30449b043c1755be63`
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the results dict carries no digest field; `main()` runs `run()` twice, asserts the two compact-canonical (sorted-keys, 6-dp-rounded) serializations are identical, prints the indent=2 dump, then the `Results-JSON sha256:` line. No JSON is written to disk.

## Constraints honored
- Verifier to be copied byte-identically from the idea-engine source; no edits.
- Stdlib-only (`math`, `json`, `hashlib`, `random`); Python 3.
- Seed pinned in-source (`SEED = 20260717`); no environment override.
- Gates to be evaluated against the proposal's own pre-registered thresholds, not re-invented.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3
- G1 — evenness-beaten (head): across 300 randomized-B contests the equal-budget concede-and-overload allocator's mean battlefield share is strictly above 0.5 at ≥3 sigma, rejecting the "equal budget ⇒ equal 0.5 share" folk null (target mean_share 0.537637, z 25.27061).
- G2 — concede-arithmetic identity (mechanism anchor): over the deterministic (B, k, deficit) sweep the real concede-and-overload game's share equals the closed-form concede-arithmetic prediction with EXACTLY zero mismatches, and the majority-feasibility deficit frontier climbs toward 1/2 as B grows (target 0 mismatches / 14421 checks; frontier B8 0.37, B20 0.44, B40 0.47).
- G3 — robustness / heterogeneous-value deficit (shifted world): under random per-field values AND a 40% budget deficit the value-targeted concede-and-overload still wins >0.5 of total VALUE at ≥3 sigma AND deepens vs the homogeneous equal-budget baseline (target mean_value_share 0.788032 > baseline 0.537637, z 112.524168).
- Non-gated corroboration — deficit demo (d=0.4): the challenger spends 40% LESS and still wins the field majority (target share 0.553794, z 40.335299).

## Probe questions (independent-audit checklist)
**1.** Is this the Blotto concentration-dominance law or merely "max > mean" restated? A field is decided by the LOCAL comparison, not the global budget, so conceding a minority of fields and overloading the rest is a genuine allocation result — to be demonstrated by G1's mean_share > 0.5, not asserted.
**2.** Is the win the concede arithmetic or a float/tie artifact? G2's exact identity (0 mismatches over 14421 cases) is to prove the game's share equals the closed-form concede prediction, with the head regime winning strictly (no result rests on tie-breaking).
**3.** Homogeneous-unit-value artifact? G3 repeats under random per-field values plus a 40% deficit; the value-share must still exceed 0.5 and deepen versus the baseline.
**4.** Is a weak opponent cherry-picked? The uniform splitter is precisely the intuitive folk optimum this head indicts; the equilibrium/mixed-strategy regime and the past-1/2 deficit are disclosed as crossovers, not asserted.
**5.** Does the "cheaper AND still wins" claim hold? The deficit demo (d=0.4) is to show the challenger takes the field majority while spending 40% less; the G2 frontier prices how far the deficit can go (→ 1/2 as B grows).
**6.** Is determinism real? To be confirmed by cross-invocation `diff` exit 0 and the results-dict sha256 reproducing to the disclosed `05afdeff…`.
**7.** Cherry-picked B or seed? Results are across randomized boards B ~ randint[8,40] (and randomized values in G3), not one configuration; SEED=20260717 pinned.
**8.** Real or toy? Colonel Blotto is the textbook model for RTS/MOBA lane and army-split decisions, tower-defense placement, stat/power budgeting, and (per the cited article) voting and auction bidding — the uniform-is-dominated result is the documented core.

## Outcome
**PENDING — reproduction not yet in.** This card is born-red and provisional. On the flip commit this section will record: determinism (cross-invocation `diff` exit 0; in-process double-run identical), digest match/mismatch against the disclosed `05afdeff…4721…5be63`, and the per-gate G1/G2/G3 (+ deficit-demo) results measured against the proposal's own thresholds. The verdict (APPROVE / QUALIFY / REJECT) is rendered here only once the run stdout is committed — not before.

## ⟲ Previous-session review
VERDICT 183 (term-sheet winner's curse, reproduce P170) landed APPROVE at merge (sim-lab #257 @ 27f02ed): byte-exact reproduction (`term_sheet_winners_curse.py`), digest `e5cdbfec…30b8e4f7` MATCH, all three gates passing on the proposal's own criteria. This card continues the loop at the next slot (P171 → V184, +13, round-40 GAME) and, on its flip to `complete`, will advance the verdict high-water V183 → V184 by union-max; no regression.

## 💡 Session idea
The verifier pins a FIXED uniform splitter as the opponent (the folk strategy the head indicts). A follow-up could add a best-responding or mixed-strategy opponent and measure how the concede-and-overload margin erodes as the opponent approaches a Blotto equilibrium — turning the disclosed "equilibrium regime" crossover into its own gated verifier, and pricing exactly how much of the win is the uniform-splitter assumption versus the concede arithmetic.

**Recommendation: PROVISIONAL — reproduce PROPOSAL 171; born-red hold, verdict to be rendered on the flip once the digest is confirmed against `05afdeff…` and G1/G2/G3 are evaluated on the proposal's own thresholds.**
