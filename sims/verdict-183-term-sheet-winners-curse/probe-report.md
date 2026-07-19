# verdict-183 — term-sheet-winners-curse: independent-audit checklist

Mechanical reproduction of PROPOSAL 170's verifier. Factual record only; no verdict rendered here.

## Artifact identity
- File: `sims/verdict-183-term-sheet-winners-curse/term_sheet_winners_curse.py`
- sha256: `30f4c776a29061ea98144afdd6d5af7b2807bb8b32b67869f2a74a0079cd1dca`
- git blob: `93eac4e6c3c758c8f99411eeff28a24ca9cfd471`
- Byte-identity vs idea-engine source (`ideas/venture-lab/term_sheet_winners_curse.py`): `diff` exit 0.

## Determinism
- Fixed seed: `SEED = 20260717` (in-source constant; no env override).
- Invocation 1 exit: 0. Invocation 2 exit: 0.
- Cross-invocation stdout `diff` exit: 0.
- In-process double-run: `double_run_identical=true`.

## Results-JSON digest
- Reported: `e5cdbfec872e5879a66c13029e003fd37b8a8aa72738ec2b1ba7e18030b8e4f7`
- Expected: `e5cdbfec872e5879a66c13029e003fd37b8a8aa72738ec2b1ba7e18030b8e4f7`
- Comparison: MATCH
- Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.

## Aggregate
- `all_pass=true`

## Gates (observed vs pre-registered thresholds)
### G1 — winner overpays, deepens with K (gaussian), z_gate=3.0
- pass: true
- mean_excess K=2: −0.141221 · K=8: −0.355814
- z_winner_overpays: 1041.753878 (>=3) · z_deepens_with_n: 373.85128 (>=3)
### G2 — conditional-on-winning reversal, z_gate=3.0
- pass: true
- mean_excess_unconditional: +0.000385 (about 0) · mean_excess_winner: −0.355814
- z_reversal: 544.530293 (>=3)
### G3 — heavy-tail robustness (Laplace, sigma_heavy=0.35), z_gate=3.0
- pass: true
- mean_excess K=2: −0.185565 · K=8: −0.500907
- z_winner_overpays: 730.514721 (>=3) · z_deepens_with_n: 330.733505 (>=3)

## Meta (from output)
- seed: 20260717
- trials: 200000 · K in {2,8} · z_gate: 3.0
- V0: 1.0 · sigma: 0.25 · sigma_heavy: 0.35
- grounding URL: https://en.wikipedia.org/wiki/Winner%27s_curse (live HTTP 200 this session)
