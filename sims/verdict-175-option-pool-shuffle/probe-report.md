# VERDICT 175 — option-pool-shuffle — reproduction report

Clean-room reproduction of `ideas/venture-lab/option_pool_shuffle.py`
(idea-engine PROPOSAL 162). All numbers below are measured in this session.

## Verifier provenance

- Source: `/home/user/idea-engine/ideas/venture-lab/option_pool_shuffle.py`
- Copied to: `sims/verdict-175-option-pool-shuffle/option_pool_shuffle.py`
- Byte-identical to source: `diff` exit **0**
- `sha256sum`: `8624c977ad2381e52485230f616266a9fb1d64ccd53961a7f62d60926ae6c7b6`
- `git hash-object` (blob): `60990ecbc8a152177d3b16989ea0a87581dbe2c3`

## Run posture

- SEED: **20260717** (a module constant `SEED`; not env/argv-driven)
- N = 4000 paired draws per regime
- Digest posture (as disclosed by the paired doc): WHOLE-DICT / NO-SELF-FIELD /
  STDOUT-ONLY — the ordered results dict does NOT contain its own hash; floats
  are `round()`-ed to 6 dp; the preimage is the compact canonical JSON
  `json.dumps(results, sort_keys=True, separators=(",",":"))` encoded UTF-8,
  hashed with sha256.

## Determinism

- In-process double run byte-identical: **True** (asserted by `main()` and
  re-confirmed by calling `run()` twice).
- Cross-invocation (two separate `python3` processes): stdout `diff` exit **0**
  — BYTE-IDENTICAL.
- Both process invocations exited **0** (all_pass true).

## Results-dict digest

- Computed (verifier's own print): `f588004512fce81ea824be9fec0c95a3ba2f3e2a8ec03af5867b526bbcb5b4b5`
- Independently recomputed with the disclosed posture: `f588004512fce81ea824be9fec0c95a3ba2f3e2a8ec03af5867b526bbcb5b4b5`
- Disclosed value: `f588004512fce81ea824be9fec0c95a3ba2f3e2a8ec03af5867b526bbcb5b4b5`
- Verdict: **MATCH**

## Gates — measured statistics

### G1 — investor post-money fraction invariant to pool size q (rejects pro-rata null)
- shuffle_change_absmean = **0.0** (below 6 dp)
- prorata_minus_shuffle_change_mean = **-0.0283**
- se = **0.000146**
- z = **194.139005**
- pass = **true** (z >= 3.0 and |divergence| > 0)

### G2 — founders→investor transfer equals closed form q·t
- transfer_mean = **0.04526**
- predicted_qt_mean = **0.04526**
- relerr_mean = **0.0** (below 6 dp, < 1e-3 ceiling)
- z = **260.109119**
- pass = **true**

### G3 — robust under shifted (mega-round) distribution
- shuffle_change_absmean = **0.0**
- prorata_minus_shuffle_change_mean = **-0.024062**
- se = **9.8e-05**
- z = **246.501756**
- pass = **true**

### Decision
- all_pass = **true**, first_failing_gate = **null**

All three measured gate results match the doc's disclosed values exactly.

## Algebra sanity check (closed form)

The pre-money "shuffle" cap table has three slices summing to 1: investor t,
pool q, founders 1 − t − q. The investor pays I for post-money P+I, so
t = I/(P+I) is fixed by the money and **does not depend on q** (dt/dq = 0). The
pro-rata null instead dilutes all holders by (1−q), landing the investor at
t(1−q). The extra amount the pre-money pool hands the investor is therefore

    transfer = t − t(1−q) = q·t = q·I/(P+I).

Independently checked numerically for several (t, q): transfer equals q·t to
machine precision in every case. This matches the verifier: G1's invariance
(shuffle_change_absmean = 0.0) and G2's identity (transfer_mean =
predicted_qt_mean = 0.04526, relerr 0.0) agree with the closed form.

## Grounding

- `curl -sS -o /dev/null -w "%{http_code}" https://venturehacks.com/option-pool-shuffle`
  → HTTP **200** (live, through the configured proxy).

## Verdict

Clean-room re-run reproduces the disclosed results-dict sha256, is
deterministic in-process and cross-invocation, and G1 ∧ G2 ∧ G3 all PASS on the
proposal's own criteria (all_pass = true). The measured numbers agree with the
q·t closed form.
