# Probe Report — VERDICT 173 / PROPOSAL 160: Cauchy no-averaging

**Reproduced:** 2026-07-19T07:35:33Z (UTC)
**Branch:** `claude/verdict-173-cauchy-no-averaging`

## Verifier provenance

| Field | Value |
|-------|-------|
| Source path (idea-engine) | `ideas/fleet/cauchy_no_averaging.py` |
| Copy path (sim-lab) | `sims/verdict-173-cauchy-no-averaging/cauchy_no_averaging.py` |
| git blob (short) | `460d9ff` |
| git blob (full) | `460d9ffea7b80339ceebb4fb4cac1bd3d983d77a` |
| sha256 | `44584333508d599d0d5d845e063480f684374c51a61be87ed913ccd1672944a8` |
| byte-identity `diff` exit | `0` |

Copied byte-identically from the idea-engine `origin/main` (commit `bee1ebd`) into the
sim-lab branch. Source and destination share the same sha256 and the destination
`git hash-object` reproduces blob `460d9ff`.

## Run

- **SEED:** `20260717` (hardcoded in the verifier; env `SEED=20260717` also set)
- Stdout captured to `run-stdout.txt`; process exit code `0` (`all_pass = true`).

## Determinism

- **Check A — in-process double-run:** built into the verifier (`main()` runs `run()`
  twice and asserts the two canonical digests are equal). The assertion held; no
  `AssertionError`. PASS.
- **Check A — cross-invocation:** ran the verifier a second time with `SEED=20260717`;
  `diff` of the two stdout captures exited `0` (byte-identical). PASS.

## Digest (posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)

- **Printed by verifier:** `Results-JSON sha256: 413e56925e89e34148cb9286df0f392c1a9881fc9072c7683b9f181f39ae7b5c`
- **Independently computed from stdout:** `413e56925e89e34148cb9286df0f392c1a9881fc9072c7683b9f181f39ae7b5c`
- **Equals expected `413e5692…7b5c`:** YES

## Gates

| Gate | Metric | Observed | z | PASS/FAIL |
|------|--------|----------|---|-----------|
| G1 mean does NOT concentrate | mean_ratio | 1.016435 | +91.179099 (vs CLT null 0.1) | PASS |
| G2 median DOES concentrate | med_ratio | 0.106589 | +1103.622367 (vs null 1.0) | PASS |
| G3 robust (γ'=2.5, n'=200) mean | mean_ratio | 0.999453 | z_mean +105.248919 (vs CLT null 0.070711) | PASS |
| G3 robust (γ'=2.5, n'=200) median | med_ratio | 0.074954 | z_med +1871.391001 (vs null 1.0) | PASS |

`gates = [true, true, true]`, `first_failing_gate = null`, `all_pass = true`.

## Grounding

- `curl https://en.wikipedia.org/wiki/Cauchy_distribution` → HTTP **200** (resolves live).

## Artifacts in this directory

- `cauchy_no_averaging.py` — the copied verifier (blob `460d9ff`)
- `run-stdout.txt` — full run output including printed digest
- `probe-report.md` — this report
