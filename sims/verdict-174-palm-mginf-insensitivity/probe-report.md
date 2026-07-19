# Probe Report — VERDICT 174 / PROPOSAL 161: Palm / M/G/inf repair-pipeline insensitivity

**Reproduced:** 2026-07-19T08:20:00Z (UTC)
**Branch:** `claude/verdict-174-palm-mginf-insensitivity`

## Verifier provenance

| Field | Value |
|-------|-------|
| Source path (idea-engine) | `ideas/fleet/palm_spares_insensitivity.py` |
| Copy path (sim-lab) | `sims/verdict-174-palm-mginf-insensitivity/palm_spares_insensitivity.py` |
| git blob (short) | `da7466e` |
| git blob (full) | `da7466ec6c75c22993344dc1caf983babee2cccf` |
| sha256 | `9a8ba388887c270463a9713d63f96788d0eb552872a025807e0dd9c737c3fc21` |
| byte-identity `diff` exit | `0` |

Copied byte-identically from the idea-engine `origin/main` (commit `cfc5e72`) into the
sim-lab branch. Source and destination share the same sha256 and the destination
`git hash-object` reproduces blob `da7466e` (8479 bytes, 233 lines).

## Run

- **SEED:** `20260717` (hardcoded in the verifier; env `SEED=20260717` also set)
- Stdout captured to `run-stdout.txt`; process exit code `0` (`all_pass = true`).
- Pinned world: LAM=1.0, MEAN_S=10.0 → offered load LOAD=λ·E[S]=10.0 (Poisson(10) pipeline),
  HORIZON=60000, WARMUP=8000, CV_HI=3.0, CEIL=0.05, R=30 replications, three repair laws
  (deterministic CV=0, exponential CV=1, lognormal CV=3).

## Determinism

- **Check A — in-process double-run:** built into the verifier (`main()` runs `run()`
  twice and asserts the two dicts are equal before serializing). The assertion held; no
  `AssertionError`. PASS.
- **Check B — cross-invocation:** ran the verifier a second time with `SEED=20260717`;
  `diff` of the two stdout captures exited `0` (byte-identical). PASS.

## Digest (posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)

- **Printed by verifier:** `Results-JSON sha256: 9bbe2171bd7678fc7efa03c550f0afbcec438498b0553a1723ee078bf5ec13ef`
- **Independently computed from stdout:** `9bbe2171bd7678fc7efa03c550f0afbcec438498b0553a1723ee078bf5ec13ef`
- **Equals expected `9bbe2171…13ef`:** YES

## Gates

| Gate | Metric | Observed | z | PASS/FAIL |
|------|--------|----------|---|-----------|
| G1 pipeline-is-load (E[N] = λ·E[S]) | load_relerr_mean | 0.004443 | +68.279173 (vs ceiling 0.05) | PASS |
| G2 variance-insensitivity (CV=3 logn) | disp_relerr_mean | 0.021783 | +12.870661 (vs ceiling 0.05) | PASS |
| G3 distribution-free (CV 0/1/3, equal mean) | spread_mean | 0.031331 | +10.750843 (vs ceiling 0.05) | PASS |

`gates = [true, true, true]`, `first_failing_gate = null`, `all_pass = true`.

Readout (not a gate): the M/G/1 Pollaczek–Khinchine wait tax (1+CV²)/2 = 5.000000× at CV=3,
which the ample-server pipeline shows NONE of.

## Grounding

- `curl https://en.wikipedia.org/wiki/M/M/%E2%88%9E_queue` → HTTP **200** (resolves live).
  The M/M/∞ / M/G/∞ ample-server queue: stationary count is Poisson(λ·E[S]), insensitive to
  the service (repair) distribution beyond its mean (Palm's theorem, 1938; Sherbrooke METRIC,
  1968), so Var(N)=E[N] (dispersion 1.0) for every repair-law shape of the same mean.

## Verdict

**APPROVE.** Verifier byte-identical to the P161 source (`diff` exit 0, sha256 and git blob
match). The compact-canonical results-dict sha256 reproduced EXACTLY as
`9bbe2171bd7678fc7efa03c550f0afbcec438498b0553a1723ee078bf5ec13ef` (printed and independently
recomputed from stdout), byte-identical across the in-process double-run assert and two fresh
`python3` invocations. All three gates PASS in order G1 pipeline-is-load → G2
variance-insensitivity → G3 distribution-free (`all_pass=true`, `first_failing_gate=null`,
exit 0). The head reads correctly: the ample-server M/G/∞ pipeline is Poisson(λ·E[S]) with
dispersion 1.0, insensitive to repair-time variability — a CV=3 lognormal repair needs the same
spares as a deterministic one. The model-basis caveat (a finite-server M/G/1 waiting line
recovers the (1+CV²)/2 variance tax) is CONSERVATIVE-DIRECTION / DISCLOSED-DESCRIPTIVE and flips
no gate sign or order-of-magnitude.

## Artifacts in this directory

- `palm_spares_insensitivity.py` — the copied verifier (blob `da7466e`)
- `run-stdout.txt` — full run output including printed digest
- `probe-report.md` — this report
