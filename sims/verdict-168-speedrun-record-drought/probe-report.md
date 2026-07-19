# VERDICT 168 — speedrun record drought: independent reproduction probe report

Reproduction of PROPOSAL 155 (round-37 GAME slot, P155 → V168, +13). All
numbers below are from THIS clean-room reproduction: the verifier was copied
byte-identical from the idea-engine source, run three times as separate
processes, and the digest recomputed independently over the script's own
compact-canonical results-dict payload. Every claim cites the run-stdout
numbers.

## Reproduction inputs (identity)

- **Source verifier:** idea-engine `ideas/superbot-games/speedrun_record_drought.py`
  at idea-engine commit `2fea93e25b1cebee39be2282e513ef2fa9b21c52`
  (blob `add649478c0d2c95616c591551db5c8b10a7a9b4`, the exact blob named in the
  proposal's Grounding line).
- **Copied to:** `sims/verdict-168-speedrun-record-drought/speedrun_record_drought.py`.
- **File sha256 (source):** `e046621c9fc5c7c1ad5b46b9dc8e66e86c9fe5187781d19a797452e5f6212d18`
- **File sha256 (copy):**   `e046621c9fc5c7c1ad5b46b9dc8e66e86c9fe5187781d19a797452e5f6212d18` (identical)
- **git blob (copy):**   `add649478c0d2c95616c591551db5c8b10a7a9b4`
- **git blob (source):** `add649478c0d2c95616c591551db5c8b10a7a9b4` (identical)
- **byte count:** 10575 · **line count:** 282
- **Byte-identity `diff` exit code:** `0` (copy is byte-identical to source).

## Pinned world (from source)

SEED=20260717 (hard-coded constant in the source, not read from env), N1=100,
N2=10000 (= N1²), TRIALS=4000, SIGMA_GATE=3.0. G1/G2 base Exponential(1.0)
(`rng.expovariate(1.0)`); G3 base Pareto(2.5) (`rng.paretovariate(2.5)`). A
record is a strictly-new running minimum; attempt 1 always counts. count@N1 and
count@N2 captured within the SAME sequence under one `random.Random(SEED)`
stream. H(n) = exact Σ 1/k.

---

## Probe 1 — Does the results-dict sha256 reproduce the disclosed digest EXACTLY?

**YES — exact match.**

- **Reproduced digest:** `fa31d28495ab63c8ff9f1c502031da475bfa334c918fb29173fab26e8e489f26`
- **Disclosed digest:**  `fa31d28495ab63c8ff9f1c502031da475bfa334c918fb29173fab26e8e489f26`
- Character-for-character equal.

The digest posture is WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+
compact-canonical twist): the results dict carries NO digest field; `main()`
rounds every float to 6 dp and hashes the compact-canonical serialization
`json.dumps(round_floats(res,6), sort_keys=True, separators=(",",":"))` of the
whole dict (source lines 265–267). stdout prints the pretty `indent=2` view
followed by a `Results-JSON sha256:` line; the digest is NOT of the pretty dump.
Confirmed three ways:

- **Script self-report:** the printed `Results-JSON sha256:` line equals the
  disclosed digest.
- **Independent recompute:** parsing the pretty JSON body back to a dict and
  re-serializing it compact-canonical (sort_keys, `(",",":")` separators)
  reproduces `fa31d284…489f26` byte-for-byte, independent of the script's own
  hash call.
- **In-process double-run assert:** `main()` builds the dict twice (`run()`
  called for `res1` and `res2`) and asserts `h1 == h2` before printing
  (source lines 271–275); the assertion did NOT fire in any run. No JSON is
  written to disk.

## Probe 2 — Is the verifier byte-identical to the P155 source?

**YES.**

- `diff SOURCE COPY` exit code: `0`.
- File sha256 (source == copy): `e046621c9fc5c7c1ad5b46b9dc8e66e86c9fe5187781d19a797452e5f6212d18`.
- git blob of copy `add649478c0d2c95616c591551db5c8b10a7a9b4` equals git blob of
  the idea-engine source `add649478c0d2c95616c591551db5c8b10a7a9b4` — Git's own
  content-hash confirms byte-identity independently of `diff`, and this blob is
  the exact object named in the proposal's Grounding line.
- byte count 10575 · line count 282.

## Probe 3 — Determinism (in-process assert + cross-invocation)

**YES — deterministic on both checks.**

- **In-process double-run (check A):** the script itself runs `run()` twice and
  asserts the two compact-canonical digests are identical before printing; both
  runs exited `0` and the assert did not fire.
- **Cross-invocation double-run (check B):** three separate `python3` processes
  produced byte-identical stdout — `diff run1 run2` exit `0` and
  `diff run1 run3` exit `0`. All three exited `0`.

## Probe 4 — Do all three gates PASS in order G1 → G2 → G3, all_pass=true, first_failing_gate=null, exit 0?

**YES — all three PASS in order; all_pass=true; first_failing_gate=null; exit 0.**

Criteria are the proposal's own pre-registered gates (SIGMA_GATE = 3.0):

| Gate | Criterion (from doc) | Reproduced numbers | Check | Result |
|------|----------------------|--------------------|-------|--------|
| **G1 harmonic-law** | \|z\| < 3, z = (mean@N2 − H(N2))/se | mean_count_N2 = 9.773 vs H_N2 = 9.787606, se = 0.044841, z = −0.325727 | \|−0.325727\| = 0.326 < 3 ✓ | **PASS** |
| **G2 log-slowdown** | (a) z_linear ≥ 3 AND (b) \|z_ratio\| < 3 | linear_pred = 520.15, z_linear = +11381.841906; ratio_obs = 1.878881 vs ratio_null = 1.886812, se_ratio = 0.008083, z_ratio = −0.981196 | 11381.84 ≥ 3 ✓ AND \|−0.981196\| = 0.981 < 3 ✓ | **PASS** |
| **G3 distribution-free** | \|z\| < 3 vs H(N2), Pareto base | mean_count_N2 = 9.73 vs H_N2 = 9.787606, se = 0.044819, z = −1.285293 | \|−1.285293\| = 1.285 < 3 ✓ | **PASS** |

Every reproduced statistic equals the disclosed value to the printed 6 dp.
`all_pass: true`, `first_failing_gate: null`, process exit `0`.

## Probe 5 — Is the head read correctly (logarithmic, distribution-free), not a linear or seed artifact?

**Read correctly as a harmonic-law claim.** The head is an objective identity
of record statistics: the k-th attempt of a continuous i.i.d. sequence is a
new running minimum with probability exactly 1/k, so E[record count after N] =
H_N ≈ ln N + γ. Sanity checks from this reproduction:

- **Harmonic anchor tracks ln N + γ:** H(N1) = 5.187378 vs ln(100)+γ = 5.182386;
  H(N2) = 9.787606 vs ln(10000)+γ = 9.787556 — the exact harmonic sum matches
  the ln N + γ asymptotic to ~3–5 dp.
- **×100 attempts → ~1.887× records, not 100×:** ratio_null H(N2)/H(N1) =
  1.886812 and observed ratio 1.878881 agree to \|z_ratio\| = 0.98. Squaring the
  attempt count (100 → 10000) lifts the expected PB count only from 5.19 to
  9.77 — under 2×.
- **Record probability 1/k:** the N2 = 10000th attempt has a 1/10000 = 0.0001
  chance of being a PB — the arithmetic behind the drought.
- **The linear null is the fantasy the head kills:** the linear-accumulation
  null calibrated at N1 predicts 520.15 records at N2; the observed 9.773 sits
  z_linear = +11381.8σ below it. The huge z is the size of the effect (linear
  null ≈ 53× the true count), not statistical over-precision — the load-bearing
  two-sided test is the ratio anchor z_ratio = −0.98.
- **Distribution-free:** G3 swaps the Exponential base for a heavy-tailed
  Pareto(2.5) and recovers the SAME H(N2) within \|z\| = 1.285 — the cadence
  does not depend on the runner's time distribution, only on rank.

No gate reads the drought as a runner-plateau signal; all three measure the
stationary harmonic null, exactly as declared.

---

## Verdict

**APPROVE.** The verifier is byte-identical to the P155 source (diff exit 0,
matching sha256 and git blob `add64947…`); it reproduces the disclosed
results-dict digest `fa31d284…489f26` exactly (independently recomputed and
cross-invocation byte-identical); and all three pre-registered gates PASS in
order (G1 z = −0.33, G2 z_linear = +11381.84 / z_ratio = −0.98, G3 z = −1.29)
with all_pass = true, first_failing_gate = null, exit 0. Reproduction is clean
and complete.
