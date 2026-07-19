# VERDICT 171 — marketplace take-rate / rake hump: reproduction probe report

- **Timestamp (UTC):** 2026-07-19T06:22:46Z
- **Verifier source:** idea-engine `ideas/venture-lab/marketplace_take_rate_disintermediation.py`
- **Posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY

## File identity (byte-identical copy)

- **sha256:** `bcd15da1f16aca466c2771085a4d1ce2ea96a5a4d03d6d431036cb899156384c`
- **git blob hash (hash-object):** `49c3eaf039d9eaf9cea60720d76c955521e3c873`
- `diff` idea-engine source vs sim-lab copy: exit code **0** (byte-identical).

## Determinism

- Two separate process invocations (`SEED=20260717`), stdout captured each time; `diff run1 run2`: exit code **0** (byte-identical across two fresh processes). Both invocations exited 0.
- Verifier also performs an in-process double run (`a = run(); b = run()`) and asserts `a == b` ("non-deterministic: in-process double-run diverged"); the assertion held on every invocation. SEED is pinned in-source at `20260717` (not read from env), so the run is reproducible without external configuration.

## Results-dict digest

The verifier hashes the whole results dict via `json.dumps(a, sort_keys=True, separators=(",",":"))` then sha256; the dict carries no digest field (NO-SELF-FIELD). Digest read from STDOUT and independently recomputed from the printed JSON block.

- **Printed `sha256`:** `9b8be9fcc3e51afcff0561e43930aa5a38b32f803708c1602f7cf3d69e3b1f43`
- **Independently recomputed (stdout-only, re-dumped with `sort_keys=True, separators=(",",":")`):** `9b8be9fcc3e51afcff0561e43930aa5a38b32f803708c1602f7cf3d69e3b1f43`
- **Disclosed:** `9b8be9fcc3e51afcff0561e43930aa5a38b32f803708c1602f7cf3d69e3b1f43`
- **Verdict:** **MATCH**

## Gates (against the proposal's own thresholds; APPROVE iff all hold; z_gate = 3.0)

| Gate | Observed | Threshold | Pass? |
|------|----------|-----------|-------|
| G1 domination-sign | gap_mean=+0.080126, z=+592.387661, frac_dominant=1.0 (null gap=0) | z ≥ 3, gap > 0 | **PASS** |
| G2 relative-effect | rel_mean=+0.640656, z=+581.508639 (null rel=0.10) | z ≥ 3, rel ≥ 0.10 | **PASS** |
| G3 shifted-robustness | gap_mean=+0.087422, z=+1142.566654, frac_dominant=1.0 (optimum t*→0.175 under lower loyalty, null gap=0) | z ≥ 3, gap > 0 | **PASS** |

`all_pass = True`, `first_failing_gate = null`, process exit code 0.

### Hand-check — closed form vs Monte-Carlo

Interior monopoly optimum with `c ~ Uniform[0, C]` gives linear demand `S(t)=P(c≥t)=(C−t)/C`, so net revenue `R(t)=t·S(t)·GMV0` is a hump with argmax **t*=C/2**.

- **Base (C=0.50):** t*=0.25 → S(0.25)=(0.50−0.25)/0.50=0.5 → R=0.25·0.5=**0.12507** (of GMV0). Verifier `r_star_base_mean=0.12507`.
- **Aggressive (t=0.45):** S(0.45)=(0.50−0.45)/0.50=0.1 → R=0.45·0.1=**0.044944** (of GMV0). Verifier `r_max_base_mean=0.044944`.
- **Haircut:** (0.12507−0.044944)/0.12507 = **0.6407 ≈ 64%** relative revenue loss for overshooting the optimum — matches `rel_mean=0.640656`.

The closed-form values land exactly on the values the verifier prints, confirming the ~64% haircut of the optimum-region take (25%) vs the aggressive rake (45%).

## Bottom line

**APPROVE.** Reproduces cleanly — byte-identical verifier (sha256 as pinned), deterministic across two fresh processes plus the in-process double-run assertion, the results-dict digest MATCHES the disclosed value exactly, and all three gates pass with wide margins in order (G1 sign, G2 relative effect ≥ 10%, G3 shifted robustness). The closed-form optimum t*=C/2 and the 0.12507-vs-0.044944 revenue pair hand-check exactly against `R(t)=t·(C−t)/C`, and the Monte-Carlo measurements confirm the ~64% haircut. **APPROVE.**
