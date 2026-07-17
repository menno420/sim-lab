# VERDICT 102 — APPROVE — two single-server queues at the SAME utilization ρ = 0.8 meet the SLA at wildly different rates because the high-variance lane violates a 10× SLA target at a MULTIPLE of the low-variance lane's rate; the P–K mean-wait anchors both lanes, the violation ratio rises monotonically with the service coefficient of variation crossing 2× near CV ≈ 1.51, and re-provisioning the high-variance lane to a LOWER load ρ* = 0.512 closes the gap — proving variance, not utilization, sets SLA risk (P089, variance-blind-provisioning-trap)

**Ruling: APPROVE** (no failing gate — all of R1→R2→R3→R4 hold). Source proposal
header cited verbatim: `## PROPOSAL 089 · 2026-07-16T22:04:51Z · status: sim-ready`
(idea-engine PROPOSAL 089, registered spec `variance-blind-provisioning-trap-2026-07-16`);
P089 → V102 under the constant **+13** PROPOSAL↔VERDICT offset (the P087 → V100, P088 → V101
precedent).

On the pinned world (N = 200 000 tasks/lane/rep, warmup = 20 000, R = 12 reps, seeds
S = [1001…1012]) two single-server FCFS **M/G/1** lanes share the identical nominal load
`ρ = λ·E[S] = 0.8` (Poisson arrivals `λ = 0.8`, interarrival ~ Exponential mean 1.25, mean
service `E[S] = 1.0`) and differ ONLY in the service-time coefficient of variation: lane A is
`CV = 1` (exponential service, M/M/1) and lane B is `CV = 3` (balanced-means 2-phase
hyperexponential H2, same mean). The exact single-server **Lindley recursion**
`Wq_i = max(0, Wq_{i−1} + S_{i−1} − A_i)`, `sojourn_i = Wq_i + S_i` (`Wq_1 = 0`) is run per lane;
the metric `viol` is the fraction of post-warmup tasks whose sojourn exceeds the SLA target
`W_target = 10`. Service is the unified balanced-means H2 sampler (`CV = 1` degenerates to plain
exponential through the same code path); `Exp(mean = m)` is drawn as `−m·log(1 − u)`
(version-independent, not `random.expovariate`). Pooling across the 12 reps: pooled mean = mean
of the 12 per-rep values; SD = sample SD (ddof = 1); SE = SD/√12, for both `Wq` and `viol`.

P089 pre-registered an APPROVE rule requiring ALL four gates R1–R4. The measured run APPROVES:
the high-variance lane violates the SLA at `viol_B = 0.498021` versus `viol_A = 0.136890`, a
ratio **3.638** clearing the pre-registered 2.5× floor by **22.49σ** with the gap
`0.361131` separated at **95.58σ** (R1); the measured mean wait sits within **0.72 %** (lane A,
`Wq = 4.02873` vs P–K `4.0`) and **2.01 %** (lane B, `Wq = 19.59726` vs P–K `20.0`) of the
Pollaczek–Khinchine closed form (R2); the violation ratio is strictly monotone in CV with
adjacent separations 30.50 / 15.27 / 9.15 / 5.01 / 4.44σ and a 2× crossover at **CV = 1.5099**
inside [1.36, 1.66] (R3); and re-provisioning lane B to a LOWER load `ρ_B* = 0.512`
(`mean_s = 0.64`) drives its violation rate to `viol_B* = 0.136513`, a gap of **−0.000376**
(0.20σ) from lane A with `ρ_B* = 0.512 < ρ_A = 0.8` (R4). Both independently-written decision
evaluators agree APPROVE/None on the measured gate outcomes.

14 self-checks, 14 passed, 0 failed; exit 0 on the accepted run; ≈ 6 s/run; hermetic —
CPython 3, stdlib only, zero repo/network reads at verdict time, no wall clock, no
PYTHONHASHSEED dependence. The seed-1001 first-20 service draws (lanes A and B) and first-20
arrival gaps (lane A) full-precision via `repr`, plus the P–K anchors and gate thresholds, are
committed as the fixture and re-verified each run. stdout + results.json byte-identical across
two full process runs by external diff + sha256:

- `results.json` sha256 `6718bd00874e4720a9cd5744673d4a61cde56d80796dad2c66b598ff5f81e667`
- `run-stdout.txt` sha256 `00a204d1ebe9cd1feb423d5b5bd28e10e3c423e15b5e83e2b3215600cc1dfdbf`
- `fixtures.json` sha256 `2b56c254d0207ebbb07d2cfc8644c00a8a4e2ef7e6a170035c29dccc3a19b4f5`

## The decision clauses (all measured)

- **R1 trap effect — PASS.** Over equal-ρ lanes the low-variance lane A violates the SLA at
  pooled `viol_A = 0.136890` (SE 0.001660) and the high-variance lane B at
  `viol_B = 0.498021` (SE 0.003394). The ratio is **3.638115** (delta-method SE 0.050604),
  clearing the pre-registered 2.5× floor by `(3.638115 − 2.5)/0.050604 = ` **22.49σ**, and the
  gap `viol_B − viol_A = 0.361131` (SE 0.003778) is separated from zero at **95.58σ**. Same
  utilization, ~3.6× the SLA breach — the trap fires.
- **R2 P–K sanity — PASS.** The measured pooled mean queue wait matches the Pollaczek–Khinchine
  closed form `Wq_PK = (ρ/(1−ρ))·((1+CV²)/2)·E[S]` within 5 % for BOTH lanes: lane A
  `Wq = 4.02873` vs `Wq_PK = 4.0000` (rel-err **0.72 %**), lane B `Wq = 19.59726` vs
  `Wq_PK = 20.0000` (rel-err **2.01 %**). The queue dynamics are the correct M/G/1 process, so
  the violation gap is a real physical effect, not a simulation artifact. (Failure here would be
  INVALID, not REJECT — a miscalibrated queue.)
- **R3 dose-response — PASS.** With ρ = 0.8 fixed, `ratio(CV) = viol(CV)/viol_A` is strictly
  monotone increasing across the CV sweep and every adjacent pair is separated ≥3σ, and the 2×
  crossover (linear interpolation where ratio = 2.0) lands at **CV = 1.5099**, inside the
  registered band [1.36, 1.66]. The SLA-violation multiple scales smoothly with service
  variance — the more bursty the service, the more the equal-ρ provisioning under-delivers.
- **R4 provisioning correction / falsifier — PASS.** Re-provisioning lane B to a LOWER load
  `ρ_B* = 0.512` (`mean_s = 0.64`, `CV = 3` unchanged) yields `viol_B* = 0.136513` (SE
  0.000909), a gap `viol_B* − viol_A = −0.000376` (se_gap* 0.001893) of only **0.20σ** —
  statistically indistinguishable from lane A — with `ρ_B* = 0.512 < ρ_A = 0.8`. Lowering the
  variance-blind lane's utilization repairs the SLA exactly, proving variance (not ρ) set the
  risk; the falsifier (a gap that FAILED to close, or a "correction" that needed MORE load than
  lane A) was reachable and did not fire.
- **APPROVE fires.** All four gates hold in the registered order R1→R2→R3→R4, so the
  pre-registered rule (APPROVE iff R1∧R2∧R3∧R4) returns APPROVE with no failing gate. The
  REJECT world (R1 with no real 2.5× effect, or an R4 correction that failed to close) and the
  NULL world (a sub-threshold R1 or a non-monotone / mis-located R3 crossover) were genuinely
  reachable and did not come live.

## Margin ledger (typed; per-arm viol pooled mean ± SE, margin in σ)

| Gate | metric | measured | threshold | margin |
|------|--------|----------|-----------|--------|
| R1 | ratio = viol_B/viol_A | **3.638115** (SE 0.050604) | ≥ 2.5 by ≥3σ | clears 2.5× by **22.49σ** |
| R1 | gap = viol_B − viol_A | **0.361131** (SE 0.003778) | separated ≥3σ | **95.58σ** |
| R2 | lane A Wq vs P–K | 4.02873 vs 4.0000 | rel-err ≤ 0.05 | **0.0072** |
| R2 | lane B Wq vs P–K | 19.59726 vs 20.0000 | rel-err ≤ 0.05 | **0.0201** |
| R3 | ratio monotone in CV | strictly increasing | + adjacent ≥3σ | min adj sep **4.44σ** |
| R3 | 2× crossover CV | **1.5099** | ∈ [1.36, 1.66] | inside band |
| R4 | gap* = viol_B* − viol_A | **−0.000376** (se_gap* 0.001893) | \|·\| ≤ 3·se_gap* | **0.20σ** (≤ 3) |
| R4 | ρ ordering | ρ_B* = 0.512 | < ρ_A = 0.8 | holds |

## Per-arm table (pooled over the 12 reps; viol = SLA-violation fraction, Wq = mean queue wait)

| arm | CV | ρ | viol mean ± SE | Wq mean ± SE | Wq_PK | rel-err |
|-----|----|----|----------------|--------------|-------|---------|
| laneA | 1.0 | 0.800 | 0.136890 ± 0.001660 | 4.02873 ± 0.02993 | 4.0000 | 0.0072 |
| cv1.5 | 1.5 | 0.800 | 0.271714 ± 0.002948 | 6.58259 ± 0.06910 | 6.5000 | 0.0127 |
| cv2.0 | 2.0 | 0.800 | 0.376532 ± 0.002597 | 10.06266 ± 0.12160 | 10.0000 | 0.0063 |
| cv2.5 | 2.5 | 0.800 | 0.451250 ± 0.003036 | 14.50829 ± 0.31281 | 14.5000 | 0.0006 |
| laneB | 3.0 | 0.800 | 0.498021 ± 0.003394 | 19.59726 ± 0.27119 | 20.0000 | 0.0201 |
| cv3.5 | 3.5 | 0.800 | 0.544294 ± 0.004138 | 26.42483 ± 0.69439 | 26.5000 | 0.0028 |
| laneBstar | 3.0 | 0.512 | 0.136513 ± 0.000909 | 3.36346 ± 0.02707 | 3.3574 | 0.0018 |

Every measured mean wait is within 5 % of its P–K anchor (max rel-err 2.01 %, lane B), a
model-validity check across the whole sweep — a miss on lanes A or B would trip the R2 INVALID
guard.

## Dose-response ratio table (ρ = 0.8 fixed; ratio(CV) = viol(CV)/viol_A)

| CV | ratio | SE | adjacent separation (σ) |
|----|-------|-----|--------------------------|
| 1.0 | 1.000000 | 0.000000 (by construction) | — |
| 1.5 | 1.984913 | 0.032296 | 30.50 |
| 2.0 | 2.750624 | 0.038371 | 15.27 |
| 2.5 | 3.296447 | 0.045712 | 9.15 |
| 3.0 | 3.638115 | 0.050604 | 5.01 |
| 3.5 | 3.976147 | 0.056904 | 4.44 |

Strictly monotone; every adjacent pair separated ≥3σ (minimum 4.44σ, CV 3.0↔3.5). The 2×
crossover by linear interpolation of ratio vs CV where ratio = 2.0 falls on the [1.5, 2.0]
segment (ratio 1.984913 → 2.750624) at **CV = 1.50985**, inside the registered band
[1.36, 1.66]. The equal-ρ SLA-violation multiple doubles by CV ≈ 1.51 and keeps rising.

## R4 provisioning correction (the falsifier)

| quantity | lane A (ρ = 0.8, CV = 1) | lane B* (ρ = 0.512, CV = 3) |
|----------|--------------------------|------------------------------|
| viol pooled mean | 0.136890 | 0.136513 |
| viol SE | 0.001660 | 0.000909 |
| gap* = viol_B* − viol_A | — | −0.000376 |
| se_gap* = √(se_A² + se_B*²) | — | 0.001893 |
| separation | — | 0.20σ (≤ 3σ) |
| ρ | 0.800 | 0.512 (< 0.800) |

Lowering the high-variance lane's utilization from 0.8 to 0.512 drives its SLA-violation rate
to within 0.20σ of the low-variance lane — the correction closes and it genuinely needs LESS
load than lane A (`ρ_B* = 0.512 < ρ_A = 0.8`). Had the gap failed to close within 3σ, or had
the correction required `ρ_B* ≥ ρ_A`, R4 would REJECT; neither came live.

## Threshold / anchor calibration (verified analytically)

| item | formula | computed | expected | match |
|------|---------|----------|----------|-------|
| H2 p1 (CV = 3) | (1 + √((9−1)/(9+1)))/2 | 0.947214 | 0.947214 | yes |
| H2 m1 (CV = 3) | mean_s/(2·p1) | 0.527864 | 0.527864 | yes |
| H2 m2 (CV = 3) | mean_s/(2·p2) | 9.472136 | 9.472136 | yes |
| H2 E[S] (CV = 3) | p1·m1 + p2·m2 | 1.000000 | 1.000000 | yes |
| H2 E[S²] (CV = 3) | 2(p1·m1² + p2·m2²) | 10.000000 | 10.000000 | yes |
| H2 CV (CV = 3) | √(E[S²]−E[S]²)/E[S] | 3.000000 | 3.000000 | yes |
| P–K anchor (CV = 1) | (0.8/0.2)·(2/2)·1 | 4.000000 | 4.0 | yes |
| P–K anchor (CV = 3) | (0.8/0.2)·(10/2)·1 | 20.000000 | 20.0 | yes |

The unified sampler degenerates to plain exponential at CV = 1 (p1 = p2 = 0.5, m1 = m2 = mean_s),
verified as its own self-check.

## Twin evaluators and agreement

Two independently-written decision evaluators score the SAME measured gate outcomes:

- **Evaluator A (if-chain):** applies R1→R2→R3→R4 as a short-circuit if/elif chain, returning
  the ruling token and the first gate whose predicate is False → **APPROVE / None**. (R1 →
  NULL if a real ≥3σ gap is sub-threshold else REJECT; R2 → INVALID; R3 → NULL; R4 → REJECT.)
- **Evaluator B (table-driven):** an independently transcribed table of (gate, outcome, token)
  rows, scanned in the registered order for the first False → **APPROVE / None**.

Both agree on BOTH the ruling token (APPROVE) AND the first-failing-gate reason (None), checked
by the self-check `twin_evaluators_agree`. The 14 self-checks: the P–K closed form matches its
two known points (`pk_closed_form_known_points`), the H2 params match their 6dp analytics
(`h2_params_cv3_analytic_6dp`), the CV = 1 sampler degenerates
(`h2_params_cv1_degenerate`), the hot-loop service arithmetic matches the `draw_service` helper
byte-for-byte (`sampler_inline_matches_helper`), both P–K anchors sit within 5 %
(`R2_pk_anchor_laneA_within_5pct`, `R2_pk_anchor_laneB_within_5pct`), R1/R3/R4 each hold
(`R1_trap_effect`, `R3_dose_monotone_and_separated`, `R3_crossover_in_band`,
`R4_correction_closes`), the twins agree (`twin_evaluators_agree`), every rep scores exactly
180 000 post-warmup tasks (`metric_task_count_180000`), the fixture matches the committed copy
(`fixture_matches_committed`), and the canonical JSON serialization is stable
(`canonical_json_stable`) — 14/14.

## Falsifiability gates (were real)

- **R1 trap (else NULL/REJECT):** had the equal-ρ violation ratio failed to clear 2.5× by ≥3σ,
  or had the gap failed to separate, R1 would not pass. Measured ratio 3.638 at 22.49σ over 2.5,
  gap at 95.58σ.
- **R2 P–K anchor (else INVALID):** either lane's mean wait off the closed form by > 5 % marks
  the queue model miscalibrated. Measured 0.72 % / 2.01 %.
- **R3 dose-response (else NULL):** a non-monotone ratio-vs-CV curve, an adjacent pair under 3σ,
  or a 2× crossover outside [1.36, 1.66] fails R3. Measured strictly monotone, min adjacent
  separation 4.44σ, crossover CV = 1.5099.
- **R4 correction (else REJECT):** a re-provisioned lane B* whose violation gap failed to close
  within 3σ, or that required `ρ_B* ≥ ρ_A`, falsifies the "variance, not ρ" claim. Measured gap
  0.20σ with ρ_B* = 0.512 < 0.8.
- **Fixture pin:** the seed-1001 first-20 service draws (lanes A and B) and first-20 arrival
  gaps (lane A) plus the P–K anchors and gate thresholds are committed and re-derived each run —
  one misread of the Lindley order, the H2 params, or the stream seeding moves the fixture and
  trips `fixture_matches_committed`.

Any self-check failure blocks exit 0; a twin-evaluator disagreement is the only other path to
exit ≠ 0. The REJECT / NULL / INVALID worlds were reachable and did not come live — all four
gates pass.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a fleet-external operations / capacity-planning head (no single lane consumer); the
deliverable is a citable measured verdict plus a transferable provisioning audit, fanned in to
the fleet manager (Q-0264). Per the proposal's pre-registered APPROVE consequence, paste-ready
and recommendation-first (Q-0263.2): **(1, recommended)** never size a queue / worker pool /
rate limiter by utilization ρ alone when tail-latency or an SLA-breach fraction is the target —
two lanes at the SAME ρ = 0.8 breached a 10× SLA at 0.137 vs 0.498 (a 3.6× multiple) purely
because service variance differed (CV 1 vs 3); provision against the SERVICE-TIME VARIANCE, not
just the mean load; **(2)** the penalty has a DOSE-RESPONSE in CV — the equal-ρ violation
multiple crosses 2× by CV ≈ 1.51 and keeps climbing (3.6× at CV = 3, ~4.0× at CV = 3.5), so the
burstier the service the more a ρ-only capacity plan under-delivers; **(3)** the repair is to
re-provision the high-variance lane to a LOWER utilization (here ρ = 0.512 restored parity with
the low-variance lane to within 0.20σ) — the correction is real and quantifiable via the P–K
mean wait, not folklore. Known co-consumers: any fleet surface that provisions by average load
and reads an SLA/tail objective — worker-pool autoscaling, rate-limit budgeting, batch-window
sizing. Transferable audit: "is this capacity plan sized on mean utilization while the SLA is a
tail/threshold objective, and if so what is the service-time coefficient of variation?"

## Seeds

**V102 consumes NO seed-ledger block.** The seeds are the in-file constants S = [1001…1012]
(two `random.Random` instances per arm — one service stream, one arrival stream, keyed by the
deterministic integer formulas in the module header), a fixed local realization set — NOT a
draw from the fleet seed ledger. The next free ledger block stays **20261730**, untouched (the
V099/V100/V101 SEEDLESS-baton precedent). No seed touches the decision rule, which is a
deterministic gate-by-gate comparison of the rep-pooled `viol`/`Wq` and their separations.
