# Probe report — VERDICT 191: post-money SAFE stacking tax (PROPOSAL 178)

**Ruling: APPROVE.** Reproduction of the committed verifier is byte-identical and deterministic; the disclosed results-dict digest matches; all three ordered gates pass on the proposal's own thresholds.

## Source & reproduction
- Verifier source: idea-engine `ideas/venture-lab/post_money_safe_stacking.py` (git blob `51a14a48`, 159 lines / 5365 bytes, stdlib-only).
- Reproduction copy: `sims/verdict-191-post-money-safe-stacking/post_money_safe_stacking.py`.
- Byte-identity: `diff source copy` exit 0; copy sha256 `bfde226f62ee5c6579e4fe54f5f56440646fb85295900662998a0791d057b2cc`; git blob `51a14a48`.
- Determinism: `main()` runs `compute()` twice with `assert r1 == r2` (in-process double-run guard); a separate second invocation is byte-identical (`diff run1 run2` exit 0). SEED=20260717 pinned at source.

## Digest
- Disclosed results-dict sha256 (stdout): `78758a602a36ba32bc1fd97b77820c97e86abbe7828a160ddbdd22ae7e8b2549`.
- Proposal disclosure: `78758a602a36ba32bc1fd97b77820c97e86abbe7828a160ddbdd22ae7e8b2549`.
- **MATCH** (all 64 hex). Posture: whole-dict sha256 over the compact-canonical dict, stdout-only, no on-disk JSON.

## Gates (order G1 → G2 → G3, thresholds from the proposal)
| Gate | Claim | Statistic | Threshold | Result |
|------|-------|-----------|-----------|--------|
| G1 | post-money strictly more dilutive | mean_tax 0.127846, z 631.562768 | z ≥ 3.0 | PASS |
| G2 | convex in stack size | ratio_high/low 6.338353, z_diff 824.297 | ratio ≥ 3.0, z ≥ 3.0 | PASS |
| G3 | robust under heavier stacking | mean_shift 0.229045 > base 0.127846, z_positive 1074.028387, z_increase 344.175738 | z ≥ 3.0 | PASS |

`all_pass = true`, `first_failing_gate = null`. Baseline: mean_x 0.403207, sd_tax 0.090528, rejects 4862; shift_rejects 260788; trials 200000; x_cap 0.85.

## Algebra
Post-money SAFE ownership is fixed at conversion, so stacking dilution falls on founders; pre-money SAFEs convert on a common base and dilute each other. Founders retain `1 − x` (post) vs `1/(1+x)` (pre). Stacking tax = `1/(1+x) − (1 − x) = x²/(1+x)`, strictly positive and convex for `x > 0`. At the sampled mean_x 0.403207 the closed form gives 0.403207²/1.403207 ≈ 0.1159, consistent with the simulated mean_tax 0.127846 given the x-distribution over [0, 0.85].

## External grounding
Wikipedia "Simple agreement for future equity" — HTTP 200, oldid 1361062477 (last edited 25 June 2026): "Under this structure, the dilution from issuing several SAFEs falls on the founders rather than being shared among the SAFE holders." Supports the post-money mechanism.

## Run
Full stdout committed at `run-stdout.txt`. Two invocations byte-identical.
