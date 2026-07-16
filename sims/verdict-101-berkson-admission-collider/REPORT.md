# VERDICT 101 — APPROVE — a disjunctive selection gate over two INDEPENDENT axes manufactures a spurious quality tradeoff among admitted items (Berkson's paradox); the population correlation is zero, the admitted-cohort correlation goes strongly negative, it strengthens as admission tightens, and a single-gate control shows the disjunction is the sole cause (P088, berkson-admission-collider)

**Ruling: APPROVE** (no failing gate — all of R1→R2→R3→R4 hold). Source proposal
header cited verbatim: `## PROPOSAL 088 · 2026-07-16 · status: sim-ready`
(idea-engine PROPOSAL 088, registered spec `berkson-admission-collider-2026-07-16`);
P088 → V101 under the constant **+13** PROPOSAL↔VERDICT offset (the P087 → V100 precedent).

On the pinned world (n = 2000 items per run, seeds S = [1,2,3,4,5]) each item carries two
latent quality scores, novelty `N` and rigor `R`, each iid `Normal(0,1)` drawn from
**SEPARATE** `random.Random` streams — `random.Random(seed)` for `N`,
`random.Random(seed+10000)` for `R` — so the two axes share NO draws and `corr(N,R) = 0` in
the population **BY CONSTRUCTION**. Admission is a **DISJUNCTIVE collider gate**: admit iff
`N ≥ t OR R ≥ t`, with `a = b = t` calibrated so the marginal admit rate hits target `T`;
with independent axes each of tail probability `p = P(N ≥ t)` the OR admit rate is
`1 − (1−p)²`, so `p = 1 − √(1−T)` and `t = Φ⁻¹(1−p) = Φ⁻¹(√(1−T))`. Three stringency levels
`T ∈ {0.50, 0.25, 0.10}` (reference `T = 0.25`), calibrated thresholds `t(50%) = 0.544952`,
`t(25%) = 1.107798`, `t(10%) = 1.632219`. A single-gate control (the R4 falsifier) admits on
`N ≥ a` ALONE with `a = Φ⁻¹(1−0.25) = Φ⁻¹(0.75) = 0.674490`, matched to the same ≈25% marginal
admit rate. `Φ⁻¹` is Acklam's stdlib rational approximation; the metric is Pearson `r` in pure
stdlib — `ρ_full` over the full 2000 (R1), `ρ_admit` over each OR-gate admitted subset
(R2/R3), and `ρ_single` over the single-gate subset (R4). Pooling across the 5 seeds: pooled
mean = mean of the 5 per-seed ρ; `σ` = sample SD (ddof=1); `SE = σ/√5`.

P088 pre-registered an APPROVE rule requiring ALL four gates R1–R4. The measured run APPROVES:
the population correlation is a null `ρ_full = +0.000251` a full ≥3σ inside the ±0.03 band
(R1), the reference-stringency admitted-cohort correlation is `ρ_OR@25 = −0.587329` clearing
the −0.45 floor by **20.97σ** (R2), the dose-response is strictly monotone
`−0.457816 (50%) > −0.587329 (25%) > −0.685281 (10%)` with adjacent separations **14.34σ** and
**8.92σ** (R3), and the single-gate control sits at `ρ_single = −0.013478` inside the null band
(pooled-mean reading) and **43.35σ** from the OR effect (R4). Every measured number reproduces
the proposal's disclosed dry-sim EXACTLY from an INDEPENDENT re-implementation. Both
independently-written decision evaluators agree APPROVE/None on the measured gate outcomes.

10 self-checks, 10 passed, 0 failed; exit 0 on the accepted run; < 1 s/run; hermetic —
CPython 3, stdlib only, zero repo/network reads at verdict time. The two axes are drawn from
two separate seeded streams so `corr(N,R) = 0` in the population, and the seed-1
reference-stringency (25% OR-gate) admitted-subset size (537) with the first-20 admitted
(N,R) pairs (full precision via `repr`) plus the four calibrated thresholds are committed as
the fixture and re-verified each run. stdout + results.json byte-identical across two full
process runs by external diff + sha256:

- `results.json` sha256 `5b8060dcf584566bba2e5678909f272ab67759d7ab3f2f0f8d6b003eb5a0bf03`
- `run-stdout.txt` sha256 `9991aba274703847d32072bfa43a7ddfd03b948eb4365afdb47b29028f49181b`
- `fixtures.json` sha256 `09d61bd92960fecf6348be9725c9da70173d63e8a477cf00d3547070197d9132`

## The decision clauses (all measured)

- **R1 null anchor — PASS.** Over the FULL unselected 2000-item population the per-seed
  `ρ_full(N,R)` = [−0.001344, +0.009758, −0.016553, +0.000564, +0.008829], pooled mean
  **+0.000251**, SE 0.004738, so `|mean| + 3·SE = 0.014465 ≤ 0.03` — the anchor sits ≥3σ INSIDE
  the ±0.03 null band. The world's baseline is the stable no-correlation regime (N ⟂ R by
  construction), verified rather than assumed, so any post-selection correlation is genuinely
  selection-induced.
- **R2 effect @ T=0.25 — PASS.** Over the OR-gate admitted cohort at reference stringency the
  per-seed `ρ_OR` = [−0.598931, −0.601798, −0.591207, −0.567328, −0.577383], pooled mean
  **−0.587329**, SE 0.006550, so `mean + 3·SE = −0.567680 ≤ −0.45` — the mean clears the
  pre-registered anticorrelation floor `−ρ* = −0.45` by **20.97σ**. Conditioning on the
  disjunctive collider manufactures a strong negative correlation from independent axes.
- **R3 dose-response — PASS.** Pooled `mean ρ_OR` is strictly more negative as admission
  tightens: **−0.457816 (50%) > −0.587329 (25%) > −0.685281 (10%)** (order holds), with adjacent
  separations `sep(50,25) = 14.34σ` and `sep(25,10) = 8.92σ`, both ≥3σ. The collider bias scales
  monotonically with selection pressure — the tighter the "strong in at least one dimension"
  bar, the more illusory the observed tradeoff.
- **R4 mechanism isolation — PASS.** The single-gate control (admit on `N ≥ 0.674490` ALONE)
  yields per-seed `ρ_single` = [−0.044648, −0.024512, −0.022217, +0.021447, +0.002543], pooled
  mean **−0.013478** (`|mean| = 0.0135 ≤ 0.03`, ≈1.2 SE from exactly zero — indistinguishable
  from zero) on the POOLED-MEAN reading, AND `|ρ_OR@25 − ρ_single| = 0.573852` separated at
  **43.35σ**. Selecting on `N` alone conditions on `N` but says nothing about the independent
  `R`, so no correlation appears — the disjunction is proven the sole cause.
- **APPROVE fires.** All four gates hold in the registered order R1→R2→R3→R4, so the
  pre-registered rule (APPROVE iff R1∧R2∧R3∧R4) returns APPROVE with no failing gate. The
  REJECT world was genuinely reachable (a shared-stream population correlation failing R1, a
  non-monotone dose-response failing R3, or a single-gate control that ALSO anticorrelated
  failing R4) and did not come live.

## Disclosed correction — R4 control envelope (from the spec, honored)

One reading of the R4 control does NOT clear the stricter test, and the proposal discloses it:
`|mean_single| + 3·SE = 0.047985 > 0.03`. That is R1's grammar (≥3σ INSIDE the band) applied to
the R4 control, and it fails because the single-gate `ρ` is a finite-sample estimate of a
quantity that is EXACTLY zero — with ≈500 admitted items/seed the per-seed Pearson noise is
≈ 1/√500 ≈ 0.045, so the pooled 3σ envelope (0.048) pokes just past 0.03. R4 is therefore
registered on the LOOSER pooled-MEAN reading (`|mean| = 0.0135 ≤ 0.03`, ≈1.2 SE from zero),
NOT R1's stricter ≥3σ-inside reading — the latter belongs to the full-population anchor whose
4×-smaller SE (0.0047) clears it comfortably. This is disclosed, not silently tightened: the
DECISIVE R4 clause is the SEPARATION of the control from the OR effect, `|ρ_OR − ρ_single| =
0.573852` at **43.35σ**. The verifier honors the registered pooled-mean reading and does not
apply the ≥3σ-inside test to R4.

## Twin evaluators and agreement

Two independently-written decision evaluators score the SAME measured gate outcomes:

- **Evaluator A (if-chain):** applies R1→R2→R3→R4 as a short-circuit if-chain, returning the
  ruling token and the first gate whose predicate is False → **APPROVE / None**. (REJECT at
  R1/R3/R4, NULL at R2, INVALID if validity fails.)
- **Evaluator B (table-driven):** an independently transcribed table of (gate, outcome, token)
  rows, scanned in the registered order for the first False → **APPROVE / None**.

Both agree on BOTH the ruling token (APPROVE) AND the first-failing-gate reason (None), checked
by the self-check `twin_evaluators_agree`. The Acklam `Φ⁻¹` matches the three known verification
points to 6dp (`phi_inv_known_points_6dp`), the four calibrated thresholds match their 6dp
expectations (`thresholds_match_expected_6dp`), the population anchor sits ≥3σ inside the null
band (`stream_independence_r1_band`), the achieved admit rates are within 0.02 of every target
(`achieved_admit_rates_within_tol`), R2/R3/R4 each hold (`R2_effect_clears`,
`R3_monotone_and_separated`, `R4_mechanism_isolation`), the seed-1 reference-stringency admitted
size and first-20 (N,R) pairs match the committed fixture (`fixture_matches_committed`), and the
canonical JSON serialization is stable (`canonical_json_stable`) — 10/10.

## Margin ledger (typed; per-seed ρ, pooled mean ± SE, margin in σ)

| Gate | metric | per-seed ρ (S=[1,2,3,4,5]) | pooled mean | SE | margin |
|------|--------|-----------------------------|-------------|-----|--------|
| R1 | ρ_full (full 2000) | −0.001344, +0.009758, −0.016553, +0.000564, +0.008829 | **+0.000251** | 0.004738 | \|mean\|+3SE = 0.014465 ≤ 0.03 |
| R2 | ρ_OR @ 25% | −0.598931, −0.601798, −0.591207, −0.567328, −0.577383 | **−0.587329** | 0.006550 | clears −0.45 by **20.97σ** |
| R3 | ρ_OR @ 50% | −0.479498, −0.451610, −0.456768, −0.441687, −0.459516 | **−0.457816** | 0.006216 | sep(50,25) = **14.34σ** |
| R3 | ρ_OR @ 10% | −0.699610, −0.693032, −0.680951, −0.699971, −0.652843 | **−0.685281** | 0.008810 | sep(25,10) = **8.92σ** |
| R4 | ρ_single @ 25% | −0.044648, −0.024512, −0.022217, +0.021447, +0.002543 | **−0.013478** | 0.011502 | sep from ρ_OR = **43.35σ** |

- **R1 margin:** pooled mean +0.000251, SE 0.004738; `|mean| + 3·SE = 0.014465 ≤ 0.03` → PASS
  (≥3σ inside the null band).
- **R2 margin:** pooled mean −0.587329, SE 0.006550; `mean + 3·SE = −0.567680 ≤ −0.45` → PASS
  (the mean clears −ρ* by ≈20.97σ; the largest passable ρ* is 0.567680).
- **R3 margins:** order −0.457816 > −0.587329 > −0.685281 holds; separations 14.34σ (50↔25) and
  8.92σ (25↔10), both ≥3σ → PASS.
- **R4 margins:** control pooled mean −0.013478 (`|mean| ≤ 0.03`, pooled-mean reading) and
  `|ρ_OR − ρ_single| = 0.573852` at 43.35σ → PASS.

## Achieved admit-rate table (calibration check; pooled over S=[1,2,3,4,5])

| Gate | target T | achieved (pooled) | admit-n mean | within 0.02 |
|------|----------|-------------------|--------------|-------------|
| OR @ 50% | 0.50 | 0.5009 | 1001.8 | yes |
| OR @ 25% | 0.25 | 0.2513 | 502.6 | yes |
| OR @ 10% | 0.10 | 0.1005 | 201.0 | yes |
| single @ 25% | 0.25 | 0.2497 | 499.4 | yes |

Every achieved marginal admit rate is within 0.02 of its target, confirming the `Φ⁻¹`
calibration of the four thresholds; a rate miss would trip the INVALID guard.

## Threshold-calibration table (Φ⁻¹ via Acklam, verified to 6dp)

| threshold | formula | computed | expected 6dp | match |
|-----------|---------|----------|--------------|-------|
| OR t(50%) | Φ⁻¹(√0.50) | 0.5449521362 | 0.544952 | yes |
| OR t(25%) | Φ⁻¹(√0.75) | 1.1077977036 | 1.107798 | yes |
| OR t(10%) | Φ⁻¹(√0.90) | 1.6322187878 | 1.632219 | yes |
| single a  | Φ⁻¹(0.75) | 0.6744897502 | 0.674490 | yes |

Independent Φ⁻¹ verification points: `Φ⁻¹(0.975) = 1.959964`, `Φ⁻¹(0.75) = 0.674490`,
`Φ⁻¹(0.8660254) = 1.107798`, all matched to 6dp.

## Reproduction of the disclosed dry-sim

The proposal disclosed a live dry-sim table (`p088_drysim.py`, n = 2000, seeds 1..5, byte-
identical across two runs). This INDEPENDENT re-implementation reproduces it **exactly** —
every pooled mean, every per-seed value, every SE, and every gate margin:

| quantity | disclosed dry-sim | this verifier | match |
|----------|-------------------|---------------|-------|
| ρ_full pooled mean | +0.000251 | +0.000251 | yes |
| ρ_OR@50 pooled mean | −0.457816 | −0.457816 | yes |
| ρ_OR@25 pooled mean | −0.587329 | −0.587329 | yes |
| ρ_OR@10 pooled mean | −0.685281 | −0.685281 | yes |
| ρ_single pooled mean | −0.013478 | −0.013478 | yes |
| R2 margin | 20.97σ | 20.97σ | yes |
| R3 sep(50,25) / (25,10) | 14.34σ / 8.92σ | 14.34σ / 8.92σ | yes |
| R4 separation | 43.35σ | 43.35σ | yes |
| admit rates OR 50/25/10 | 0.5009 / 0.2513 / 0.1005 | 0.5009 / 0.2513 / 0.1005 | yes |
| admit rate single | 0.2497 | 0.2497 | yes |

No material discrepancy. Because the generative process is pinned identically (separate
per-axis `random.Random` streams, the +10 000 offset, `random.gauss`, the Acklam Φ⁻¹, and the
stdlib Pearson `r`), the numbers reproduce to full displayed precision — a genuine independent
re-derivation, not a copy of the drafter's script (which is not committed).

## Falsifiability gates (were real)

- **Stream independence (else INVALID / R1 fail):** the two axes are drawn from two SEPARATE
  `random.Random` streams offset by +10 000; if they shared draws, `ρ_full ≠ 0` and R1 would
  fail — the observed anticorrelation would then be confounded by a real population correlation
  rather than the collider. Measured `ρ_full = +0.000251`, a null.
- **Achieved admit rates (else INVALID):** every OR/single marginal admit rate is asserted
  within 0.02 of its target (0.5009 / 0.2513 / 0.1005 / 0.2497); a miss would mean the Φ⁻¹
  thresholds are miscalibrated → INVALID.
- **Single-gate control (R4 falsifier):** if admitting on `N` alone ALSO anticorrelated, the
  disjunctive-collider mechanism claim would be false → REJECT. Measured `ρ_single = −0.013478`,
  indistinguishable from zero and 43.35σ from the OR effect.
- **Dose-response monotonicity (R3):** a non-monotone `ρ_OR` across 50%/25%/10% would fail R3 →
  REJECT. Measured strictly monotone with ≥3σ adjacent separations.
- **Fixture pin:** the seed-1 reference-stringency admitted size (537) and the first-20 admitted
  (N,R) pairs (full precision via `repr`) plus the four thresholds are committed and re-derived
  each run — one misread of the gate order or the stream offset moves the fixture and trips
  `fixture_matches_committed`.

Any self-check failure blocks exit 0; a twin-evaluator disagreement, a determinism break, or an
admit-rate miss is the ONLY path to exit ≠ 0. The REJECT / NULL / INVALID worlds were reachable
and did not come live — all four gates pass.

## Scope boundaries (stated, per the registration)

- **Independence boundary:** `N` and `R` are independent BY CONSTRUCTION (separate streams,
  +10 000 offset). The ruling prices the collider on INDEPENDENT axes; correlated axes
  (population `corr(N,R) ≠ 0` — Berkson on top of a real correlation) are a named follow-up.
- **Gate boundary:** the gate is a DISJUNCTION (`N ≥ a OR R ≥ b`). An AND-gate (conjunctive
  selection) is a DIFFERENT collider with a different sign/geometry and a named follow-up, not
  this claim.
- **Metric boundary:** the metric is Pearson `r` (linear correlation) on the ADMITTED subset —
  the folk "tradeoff" object; a rank correlation is a named follow-up.
- **Sweep boundary:** the dose-response sweeps the marginal admit rate via symmetric calibrated
  thresholds `a = b`; asymmetric thresholds, unequal axis weights, continuous (soft) selection,
  and non-Gaussian axes are each named follow-ups, none in scope.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a fleet-external causal-inference head (no lane consumer); the deliverable is a citable
measured verdict plus a transferable selection-bias audit, fanned in to the fleet manager
(Q-0264). Per the proposal's pre-registered APPROVE consequence, paste-ready and
recommendation-first (Q-0263.2): **(1, recommended)** before reading a correlation OFF an
accepted / shipped / survived / merged cohort, ask whether the cohort was SELECTED on a
DISJUNCTION of the two axes ("strong in at least one dimension") — if so, the observed
anticorrelation is (at least partly) Berkson, not a real tradeoff, and the population
correlation may be zero; **(2)** the artifact has a DOSE-RESPONSE — it STRENGTHENS as the
acceptance bar TIGHTENS (−0.458 at 50% → −0.587 at 25% → −0.685 at 10%), so the most selective
cohorts show the most illusory tradeoff, and "we only look at the best work, so this must be
real" is exactly backwards; **(3)** the repair is to measure the correlation in the UNSELECTED
population (or model the selection), not the admitted cohort — a single-axis gate shows the true
zero (−0.013). Known co-consumers: any fleet surface that reads a two-dimensional quality
correlation off a selected set — the review-queue accepted-PR cohort, the merged-idea ledger,
any "our shipped work shows X trades off against Y" retrospective. Transferable audit: "is this
correlation measured on a cohort selected by a disjunction of the two variables, and if so what
does the UNSELECTED correlation say?"

## Seeds

**V101 consumes NO seed-ledger block.** The seeds are the in-file constants S = [1,2,3,4,5]
(two `random.Random` instances per seed, one per axis, the R stream offset by +10 000), a fixed
local realization set — NOT a draw from the fleet seed ledger. The next free ledger block stays
**20261730**, untouched (the P084/P085/P086/P087 SEEDLESS-baton precedent). The +10 000 offset
is the load-bearing construction: it makes the two axes independent so the population `ρ` is zero
and every post-selection anticorrelation is provably selection-induced; no seed touches the
decision rule, which is a deterministic gate-by-gate comparison of the seed-pooled ρ and their
separations.
