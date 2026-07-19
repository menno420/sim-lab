# VERDICT 172 — drop-rate median gap / geometric skew: reproduction probe report

- **Timestamp (UTC):** 2026-07-19T06:56:27Z
- **Verifier source:** idea-engine `ideas/superbot-games/drop_rate_median_gap.py` (PROPOSAL 159, round-37 GAME slot, P159 → V172, +13)
- **Posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ compact-canonical twist; every float rounded to 6 dp before serialization)
- **Model:** Claude Opus · high · review/verify

## File identity (byte-identical copy)

- **sha256:** `42cacd751354569e3f9571b098dc27b85027e271402ed99891a180d798fa6682`
- **git blob hash (hash-object):** `fe602dda5c0f0924c386423b7d7ca451fc965370`
- `diff` idea-engine source vs sim-lab copy: exit code **0** (byte-identical).
- Copy sha256 == source sha256 and copy git blob == source git blob (both verified against the source in the idea-engine clone).

## Determinism

- Two separate `python3` process invocations (`SEED=20260717`), full stdout captured each time; `diff run-stdout.txt run2`: exit code **0** (byte-identical across two fresh processes). Both invocations exited **0**.
- SEED is pinned in-source at `SEED = 20260717` (module constant, not read from env), so the run is reproducible without external configuration; the exported `SEED` env var is inert.
- The verifier also performs an in-process double run — `main()` calls `res1 = run(); res2 = run()`, computes `h1`/`h2` over each, and asserts `h1 == h2` ("non-deterministic: in-process double-run digests differ"). The assertion held on every invocation, and it prints `res1` then the `Results-JSON sha256:` line.

## Results-dict digest

The verifier rounds every float to 6 dp (`round_floats(res, 6)`), serializes the WHOLE dict compact-canonically (`json.dumps(..., sort_keys=True, separators=(",",":"))`), and takes the sha256; the dict carries **no** digest field (NO-SELF-FIELD). The digest was read from STDOUT and independently recomputed from the printed indent=2 JSON block by re-dumping it with the same compact-canonical settings and hashing.

- **Printed `Results-JSON sha256:`** `ff22cf37b81fb96bb36a1aeb1a4484479d31e1232b637efb0faf297bb852fb19`
- **Independently recomputed (stdout-only, re-dumped `sort_keys=True, separators=(",",":")` over the 6-dp dict):** `ff22cf37b81fb96bb36a1aeb1a4484479d31e1232b637efb0faf297bb852fb19`
- **Disclosed (expected):** `ff22cf37b81fb96bb36a1aeb1a4484479d31e1232b637efb0faf297bb852fb19`
- **Verdict:** **MATCH** (printed == recomputed == disclosed).

## Gates (against the proposal's own thresholds; APPROVE iff all hold in order G1 → G2 → G3; z_gate = 3.0, relerr ceiling = 0.05)

| Gate | Observed (verbatim from stdout) | Threshold | Pass? |
|------|----------------------------------|-----------|-------|
| G1 median-below-mean | z_skew=**+369.741566**, gap_mc=+0.305865, ratio_med_mean_mc=0.694135, relerr_ratio=0.005993 (null gap=0) | z ≥ 3, relerr ≤ 0.05 | **PASS** |
| G2 mean-is-majority-percentile | z_majority=**+761.720583**, frac_le_mean_mc=0.634140, relerr_frac=0.000272 (null=0.5) | z ≥ 3, relerr ≤ 0.05 | **PASS** |
| G3 scale-free robustness (p'=0.005) | z_skew=**+802.499080**, z_majority=**+706.081134**, relerr_ratio=0.001487, relerr_frac=0.000494 | both z ≥ 3, both relerr ≤ 0.05 | **PASS** |

`all_pass = true`, `first_failing_gate = null`, process **exit code 0**.

The `gates` array reports each gate's headline z (G3's is `min(z_skew, z_maj)` = 706.081134). All three land far above the 3-sigma floor with the closed-form relative errors well under the 0.05 ceiling.

### Hand-check — closed form vs Monte-Carlo

For `T ~ Geometric(p)` on `{1,2,…}`, `P(T=k) = (1−p)^(k−1)·p`:

| Landmark | Closed form | Base p=0.01 (MC) | Shift p'=0.005 (MC) |
|----------|-------------|-------------------|----------------------|
| mean = 1/p | 100 / 200 | true_mean=**100.0** | true_mean=**200.0** |
| exact median = ⌈ln2 / −ln(1−p)⌉ | ≈0.693/p → 69.3 / 138.6 | exact_median=**69** | exact_median=**139** |
| ratio median/mean → ln2 = **0.693147** | 0.693147 | ratio_med_mean_mc=**0.694135** | 0.693966 |
| gap fraction (mean−median)/mean → 1−ln2 = **0.306853** | 0.306853 | gap_mc=**0.305865** | 0.306034 |
| P(T ≤ mean) → 1−1/e = **0.632121** | 0.632121 | frac_le_mean_mc=**0.634140** | 0.632729 |

Also disclosed in `limits`: `median_over_mean_ln2=0.693147`, `p_le_mean_1_minus_inv_e=0.632121`, `tail_3_over_p_inv_e3=0.049787` (≈e⁻³, the ~5% grinding past triple the "expected" count). The reproduced Monte-Carlo numbers agree with every closed form to within the disclosed 0.05 relative-error ceiling (observed relerrs 0.0003–0.006), and the ratio→1/ln2≈1.442695 / gap→1−ln2 landmarks hold identically at both drop rates — confirming scale-freedom in p.

## Probe questions (independent-audit checklist)

**1. Does the results-dict sha256 reproduce the disclosed digest EXACTLY across a fresh cross-invocation double-run AND the script's in-process double-run assert, over the COMPACT-canonical serialization (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)?**
Yes. Reproduced digest `ff22cf37b81fb96bb36a1aeb1a4484479d31e1232b637efb0faf297bb852fb19` — printed by the script, independently recomputed from stdout, and equal to the disclosed value. Two fresh `python3` invocations produced byte-identical stdout (`diff` exit 0), and the in-process `h1 == h2` assertion held.

**2. Is the verifier byte-identical to the P159 source at its pinned idea-engine identity (`diff` exit 0, file sha256 / git blob matching)?**
Yes. `diff` exit **0**; copy git blob `fe602dda5c0f0924c386423b7d7ca451fc965370` and copy sha256 `42cacd751354569e3f9571b098dc27b85027e271402ed99891a180d798fa6682` both equal the source in `ideas/superbot-games/drop_rate_median_gap.py`.

**3. Do all three gates PASS in the pre-registered order G1 → G2 → G3 with the disclosed statistics (z_gate=3.0), all_pass=true, first_failing_gate=null, exit 0?**
Yes. G1 z=+369.741566, G2 z=+761.720583, G3 z_skew=+802.499080 / z_majority=+706.081134 — all ≥ 3; `all_pass=true`, `first_failing_gate=null`, exit **0**.

**4. Is the headline read correctly — the MEAN kill-count strictly exceeds the MEDIAN on the same empirically-drawn geometric kill-counts, ratio median/mean→ln2 and gap fraction→1−ln2 — and NOT "a 1-in-N drop rate means about N kills"?**
Yes. At p=0.01 the mean is 100 but the median is 69 (ratio 0.694135≈ln2; gap fraction 0.305865≈1−ln2), and 63.4% of players finish by the mean (→1−1/e). The kill-counts are drawn via inverse-CDF geometric sampling (`geometric_draw`), and mean/median are measured on those draws, not plugged from closed forms — the closed forms only enter the relerr match. The "N kills" folk belief conflates the mean of a right-skewed law with the typical (median) grind and is refuted.

**5. Is the model-basis caveat correctly weighed as CONSERVATIVE-DIRECTION / DISCLOSED-DESCRIPTIVE (clean APPROVE, not a defect)?**
Yes. The exact constants (ln2 ratio, 1−1/e mean-percentile, e⁻³ tail) are properties of the memoryless geometric law and are disclosed as scale-free-in-p descriptive fields, not universal law-independent claims — a memory-bearing per-kill model (pity timers, bad-luck protection) would move or collapse the gap, which the proposal names as the design mitigation it exists to motivate. No gate reads the exact ratio as a universal constant; the gates test gap-SIGN (G1), order-of-magnitude relative effect ≥ threshold (G2), and robustness under a rarer rate (G3). The caveat flips no gate sign and no order-of-magnitude — a clean APPROVE.

**6. Could the gap sign be a seed fluke? Is the effect structural, and is determinism confirmed both ways?**
Not a fluke. The mean > median gap holds at both the base world (p=0.01, z_skew=+369.74) and the rarer-drop re-draw (p'=0.005, z_skew=+802.50), with z-scores hundreds of sigma above the null — structural, not a seed artifact. Determinism is confirmed both ways: the in-process double-run digest assert (`h1 == h2`) and two `python3` invocations byte-identical (`diff` exit 0).

## Bottom line

**APPROVE.** Reproduces cleanly — byte-identical verifier (git blob `fe602dda`, sha256 `42cacd75`), deterministic across two fresh processes plus the in-process double-run assertion, the results-dict digest MATCHES the disclosed `ff22cf37…` exactly (printed == independently recomputed == disclosed), and all three gates pass in order (G1 median-below-mean → G2 mean-is-majority-percentile → G3 scale-free robustness) with z-scores hundreds of sigma above the 3-sigma floor. The Geometric(p) closed forms — mean=1/p, median≈ln2/p, median/mean→ln2≈0.693147, gap fraction→1−ln2≈0.306853, P(T≤mean)→1−1/e≈0.632121 — hand-check against the reproduced Monte-Carlo numbers to within the 0.05 ceiling at both p=0.01 and p'=0.005, confirming the scale-free skew. **APPROVE.**
