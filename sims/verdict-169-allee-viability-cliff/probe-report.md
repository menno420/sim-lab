# VERDICT 169 — Allee viability cliff: reproduction probe report

- **Timestamp (UTC):** 2026-07-19T05:32:18Z
- **Verifier source:** idea-engine `ideas/fleet/allee_viability_cliff.py` @ commit `9386fb80e4d0ea542328aff019a7f92df1e55625`
- **Posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY

## File identity (byte-identical copy)

- **sha256:** `3648ea198288dc6ebdfc5d11ee417ef209f1fab560d98ae50e1a5ed12fff9596`
- **git blob hash (hash-object):** `a18d55087bffc7c362810eae688f1656a1f31cb4`
- `diff` idea-engine source vs sim-lab copy: exit code **0** (byte-identical).

## Determinism

- Two separate process invocations (`SEED=20260717`), stdout captured each time; `diff run-stdout-1 run-stdout-2`: exit code **0** (byte-identical).
- Verifier also performs an in-process double run and asserts `results == again` ("non-deterministic: in-process double run diverged"); assertion held — both invocations exited 0.

## Results-dict digest

The verifier hashes the whole results dict via `json.dumps(results, sort_keys=True, separators=(",",":"))`; the dict carries no digest field (NO-SELF-FIELD). Digest read from STDOUT and independently recomputed from the printed JSON block.

- **Printed `Results-JSON sha256`:** `bbc42b796c1dab6fae0b4be5da91e277a737cfdd5fd61246700fe826600b9471`
- **Independently recomputed (stdout-only):** `bbc42b796c1dab6fae0b4be5da91e277a737cfdd5fd61246700fe826600b9471`
- **Disclosed:** `bbc42b796c1dab6fae0b4be5da91e277a737cfdd5fd61246700fe826600b9471`
- **Verdict:** **MATCH**

## Gates (against the proposal's own thresholds; APPROVE iff all hold; z_gate = 3.0)

| Gate | Observed | Threshold | Pass? |
|------|----------|-----------|-------|
| G1 doomed-below | p_below=1.000000, z1=+20.000000 | z1 ≥ 3 | **PASS** |
| G2 safe-above | p_above=0.000000, z2=+20.000000 | z2 ≥ 3 | **PASS** |
| G3 robust-shift | gap=0.822500, z3=+6.293250 (p_below_hi=0.9125, p_above_hi=0.09; gap_min=0.6) | z3 ≥ 3 | **PASS** |

`all_pass = True`, `first_failing_gate = null`, process exit code 0.

### Sanity — deterministic basin-boundary invariance

- **Observed basin boundaries:** `[30.0, 30.0, 30.0]` across (r,K) = (0.6,100), (0.3,150), (0.9,80).
- All three land exactly on A = 30.0, invariant across the pairs — step-function viability (unstable separatrix at A), not a smooth dose-response. Matches expectation `[30.0, 30.0, 30.0]`.

## Bottom line

Reproduces cleanly — byte-identical verifier, deterministic across runs, digest MATCHES the disclosed value, and all three gates pass with the basin boundary pinned exactly at A=30.
