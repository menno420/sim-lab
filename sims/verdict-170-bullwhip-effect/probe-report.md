# VERDICT 170 — Bullwhip effect (order-variance amplification): reproduction probe report

- **Timestamp (UTC):** 2026-07-19T05:50:00Z
- **Verifier source:** idea-engine `ideas/fleet/bullwhip_order_variance_amplification.py`
- **Posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY

## File identity (byte-identical copy)

- **sha256:** `9a8f54f24f0c17afa74a9ab7c4a4a86bc13063e18a4f1b200a68d7742abdd987`
- **git blob hash (hash-object):** `2bad2e2dbbc2f315c9a97d4bd0210ac76decaf96`
- `diff` idea-engine source vs sim-lab copy: exit code **0** (byte-identical).

## Determinism

- Two additional separate process invocations (`SEED=20260717`), stdout captured each time; `diff run-stdout.txt run2` and `diff run-stdout.txt run3`: exit code **0** both (byte-identical across three fresh processes).
- Verifier also performs an in-process double run and asserts `results == again` ("non-deterministic: in-process double run diverged"); assertion held — every invocation exited 0.

## Results-dict digest

The verifier hashes the whole results dict via `json.dumps(results, sort_keys=True, separators=(",",":"))`; the dict carries no digest field (NO-SELF-FIELD). Digest read from STDOUT and independently recomputed from the printed JSON block.

- **Printed `Results-JSON sha256`:** `b45986240123fd6f922ce4f4a72d6a2c76ab7d3d8edb2da3b2d76b4efa13a49b`
- **Independently recomputed (stdout-only, re-dumped with `sort_keys=True, separators=(",",":")`):** `b45986240123fd6f922ce4f4a72d6a2c76ab7d3d8edb2da3b2d76b4efa13a49b`
- **Disclosed:** `b45986240123fd6f922ce4f4a72d6a2c76ab7d3d8edb2da3b2d76b4efa13a49b`
- **Verdict:** **MATCH**

## Gates (against the proposal's own thresholds; APPROVE iff all hold; z_gate = 3.0)

| Gate | Observed | Threshold | Pass? |
|------|----------|-----------|-------|
| G1 amplification-real | ratio_mean=2.499097, z=+880.399457 (null ratio=1) | z ≥ 3 | **PASS** |
| G2 matches-formula | relerr_mean=0.002767, z=+104.491569 (closed-form target 2.5, ceiling 0.05) | z ≥ 3 | **PASS** |
| G3 distribution-free (shift) | shift_relerr_mean=0.005070, z=+91.810513 (closed-form target 8.5, ceiling 0.05) | z ≥ 3 | **PASS** |

`all_pass = True`, `first_failing_gate = null`, process exit code 0.

### Hand-check — closed form vs Monte-Carlo

Closed form (Chen–Drezner–Ryan–Simchi-Levi): `Var(Q)/Var(D) = 1 + 2L/p + 2L²/p²`.

- **Base (L=4, p=8):** r = 4/8 = 0.5 → 1 + 2(0.5) + 2(0.5)² = 1 + 1 + 0.5 = **2.5**. Matches `formula_ratio_base=2.5`; measured `ratio_mean=2.499097` (relerr 0.0028).
- **Shift (L=6, p=4):** r = 6/4 = 1.5 → 1 + 2(1.5) + 2(1.5)² = 1 + 3 + 4.5 = **8.5**. Matches `formula_ratio_shift=8.5`; measured `shift_ratio_mean=8.495599` (relerr 0.0051).

Both hand-computed targets land exactly on the values the verifier prints, and the Monte-Carlo ratios sit within 0.3–0.6% of them.

## Bottom line

**APPROVE.** Reproduces cleanly — byte-identical verifier (sha256 as pinned), deterministic across three fresh processes plus the in-process double-run assertion, the results-dict digest MATCHES the disclosed value exactly, and all three gates pass with wide margins. The closed-form ratios 2.5 (base) and 8.5 (shift) hand-check exactly against `1 + 2L/p + 2L²/p²` and the Monte-Carlo measurements confirm them.
