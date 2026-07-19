# VERDICT 184 — reproduction report: proposal 171, the Colonel Blotto evenness trap

Factual firsthand reproduction of the committed verifier. No verdict rendered here — facts only.

## Files + hashes

| File | sha256 | git blob |
|------|--------|----------|
| `blotto_evenness_trap.py` | `5c8898378deb36c7196507d3ee8119893c96d34dfcf1921aacefd69ce9766132` | `63f8408d704ff36ac2eaa4c40060893adbdd3990` |

- Byte-identical copy of the supplied verifier source: `diff` exit 0.
- sha256 target `5c8898378deb36c7196507d3ee8119893c96d34dfcf1921aacefd69ce9766132` — MATCH.
- git blob target `63f8408d704ff36ac2eaa4c40060893adbdd3990` — MATCH.

## Reproduction

- Command: `SEED=20260717 python3 blotto_evenness_trap.py` (seed also pinned in source; env var harmless).
- Exit code: 0. `all_pass=true`, `first_failing_gate=null`.
- Full stdout captured in `run-stdout.txt`.

## Determinism

- Second independent invocation captured separately; `diff run-stdout.txt <run2>` exit 0 — byte-identical across invocations.
- The in-process double-run assertion (`run()` executed twice, compact-canonical serializations asserted equal before hashing) did NOT raise: clean exit 0, empty stderr on both runs.

## Results-JSON digest

- Reported: `05afdeffd9f44721fd6e71ee4595a024541b99976176bd30449b043c1755be63`
- Target:   `05afdeffd9f44721fd6e71ee4595a024541b99976176bd30449b043c1755be63`
- MATCH.

## Gate table (measured vs target, thresholds from proposal 171; Z_GATE=3.0)

| Gate | Metric | Measured | Target | Threshold | PASS/FAIL |
|------|--------|----------|--------|-----------|-----------|
| G1 evenness-beaten | mean battlefield share | 0.537637 | 0.537637 | share > 0.5 at z >= 3 | PASS |
| G1 | z | 25.27061 | 25.27061 | z >= 3.0 | PASS |
| G2 concede-arithmetic identity | mismatches | 0 | 0 | == 0 | PASS |
| G2 | checks | 14421 | 14421 | — | MATCH |
| G2 | deficit frontier B8 | 0.37 | 0.37 | frontier -> 1/2 | MATCH |
| G2 | deficit frontier B20 | 0.44 | 0.44 | — | MATCH |
| G2 | deficit frontier B40 | 0.47 | 0.47 | — | MATCH |
| G3 robustness (hetero-value, 40% deficit) | mean value-share | 0.788032 | 0.788032 | value-share > 0.5 at z >= 3, deepens vs baseline 0.537637 | PASS |
| G3 | z | 112.524168 | 112.524168 | z >= 3.0 | PASS |
| Non-gated deficit demo (d=0.4) | field-majority share | 0.553794 | 0.553794 | (corroboration) | MATCH |
| deficit demo | z | 40.335299 | 40.335299 | — | MATCH |

All three gates PASS in order (G1 -> G2 -> G3); `all_pass=true`; `first_failing_gate=null`.

## Factual answers to the doc's probe questions (from this run's output)

1. **What is this really?** A concentration-dominance result for fixed-budget contests: the run shows the concede-and-overload allocator winning a strict majority battlefield share (G1 mean 0.537637 > 0.5, z 25.27061) against a uniform splitter.
2. **What would make it false?** Any of G1/G2/G3 failing. In this run none failed: G1 share > 0.5 at 25.27 sigma, G2 0 mismatches over 14421 checks, G3 value-share 0.788032 > 0.5 at 112.52 sigma and deeper than the 0.537637 baseline.
3. **Simplest version that still bites?** The B=8 case: the G2 sweep confirms the concede-arithmetic identity holds exactly (0 mismatches) and the B8 majority-feasibility deficit frontier is 0.37 in this run.
4. **Counterintuitive core?** Equal budget does not buy equal share: measured equal-budget share is 0.537637 (> 0.5), and even at a 40% budget deficit the challenger still wins the field majority (deficit demo share 0.553794, z 40.335299).
5. **Where could I be fooling myself?** Weak-opponent worry — addressed here by G2's exact identity (0 mismatches / 14421 checks), which shows the win is the concede arithmetic rather than a tie-break or float artifact; results are across randomized boards (and randomized values in G3), not a single configuration.
6. **Determinism?** Confirmed: cross-invocation diff exit 0 (byte-identical stdout), in-process double-run assertion did not raise, results-dict sha256 `05afdeff...5be63` reproduced.
7. **Real or toy?** N/A to run output (framing claim); the run reproduces the pinned numeric gates the doc rests that framing on.
8. **How will we know it worked?** Criteria met in this run: G1/G2/G3 all PASS at Z_GATE=3.0, `all_pass=true`, `first_failing_gate=null`, exit 0, and the results-dict sha256 matches `05afdeffd9f44721fd6e71ee4595a024541b99976176bd30449b043c1755be63` across a deterministic double-run.

## Run parameters (from stdout)

- SEED 20260717; Z_GATE 3.0; battlefields B ~ randint[8,40]; budget T=B (uniform 1.0/field).
- G1 300 reps; deficit-demo 300 reps (d=0.4); G3 300 reps (d=0.4, values ~ U[0.2,5.0]).
- proposal 171; slot "round-40 GAME"; head "blotto_evenness_trap".
