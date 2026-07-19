# VERDICT 190 — two-choices marginal probe (reproduce PROPOSAL 177)

## Probe report

Reproduction of idea-engine `ideas/fleet/two_choices_marginal_probe.py` (PROPOSAL 177, PR #670, idea-engine main `a1aa6a5`) byte-identical in sim-lab under SEED=20260717.

### Verifier byte-identity
- Copied via `cp`; `diff` source vs sim-copy → exit 0 (byte-identical).
- File sha256: `5fede409315a2523a6fc816c25445f8cf03a718ae384c02d1fb857475a98c7e6`
- git blob (`git hash-object`): `2b2f8aef18de9b8296656593c898fded23fe94f7`
- Both equal the idea-engine reference read at HEAD.

### Digest (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)
- Disclosed (PROPOSAL 177): `625b38309d4e6c8209a74f9123b23d56d769beb4ad592b917093d8c67d234c7f`
- Reproduced printed line: `Results-JSON sha256: 625b38309d4e6c8209a74f9123b23d56d769beb4ad592b917093d8c67d234c7f`
- **MATCH (exact, character-for-character).**

### Gates (proposal's own pre-registered thresholds: z ≥ 3.0, ratio ≥ 3.0)
| Gate | Statistic | Observed | Threshold | Result |
|------|-----------|----------|-----------|--------|
| G1 second-probe jump | gap_1_2 = maxload[1] − maxload[2]; z | gap 3.536, z **77.709782** | gap > 0, z ≥ 3 | **PASS** |
| G2 second-probe dominance | dom = second_gain − further_gain; z; ratio | second_gain 3.536, all_further 0.884, dom 2.652, z **46.693563**, ratio **4.0** | dom > 0, z ≥ 3, ratio ≥ 3 | **PASS** |
| G3 robust (m = n/2, load factor 2) | dom, z, ratio in regime B | second_gain 4.664, all_further 0.992, dom 3.672, z **52.81092**, ratio **4.701613** | dom > 0, z ≥ 3, ratio ≥ 3 | **PASS** |

`all_pass = true`; script exit code 0.

### Aggregate scoping (not per-step monotone)
The head is honestly gated as an AGGREGATE — one second probe vs all further probes COMBINED — not as a strictly shrinking per-step sequence. The per-step gaps in regime A confirm the non-monotonicity the doc discloses: `gap_1_2 = 3.536`, `gap_2_3 = 0.068`, `gap_3_4 = 0.816` (d=3→4 gap exceeds the d=2→3 gap; integer-granular at finite n). The ratio (second_gain / all_further_gain) ≈ 4.0 (regime A) and ≈ 4.70 (regime B) is what clears the ≥3 gate.

### Determinism
- Two separate cross-invocation `SEED=20260717 python3 …` runs produced **byte-identical** stdout (`diff` exit 0). **Double-run byte-match: YES.**
- Determinism source: explicit per-(regime, d, trial) seeding (`regime_seed + d·1_000_003 + t·7919`, `regime_seed = SEED + regime·50_000_017`); a single module-level `SEED = 20260717`.
- NOTE: this verifier's `main()` calls `run()` ONCE — there is no in-process double-run/assert (unlike the V188/V189 verifiers). Reproducibility is established here by two separate process invocations being byte-identical.

### SEED pinning
`SEED = 20260717` is a module-level in-source constant; the file imports no `os` and reads no env var, so the `SEED=20260717` env export is inert (the exported value merely coincides with the in-source constant).
