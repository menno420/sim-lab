# verdict-102 · variance-blind-provisioning-trap

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 089
(`## PROPOSAL 089 · 2026-07-16T22:04:51Z · status: sim-ready`, registered spec
`variance-blind-provisioning-trap-2026-07-16`). P089 → V102 under the constant +13
PROPOSAL↔VERDICT offset (the P087 → V100, P088 → V101 precedent).

The head prices an operations folk belief: "if I provision two queues to the same
utilization ρ, they'll meet the same SLA." The claim is that this is FALSE — SLA violations
are variance-blind to ρ alone. Two single-server FCFS **M/G/1** lanes share the identical
nominal load `ρ = λ·E[S] = 0.8` (Poisson arrivals `λ = 0.8`, mean service `E[S] = 1.0`) but
differ ONLY in the coefficient of variation of service: lane A is `CV = 1` (Markovian,
exponential service) and lane B is `CV = 3` (a balanced-means 2-phase hyperexponential H2 with
the SAME mean). The exact single-server **Lindley recursion**
`Wq_i = max(0, Wq_{i−1} + S_{i−1} − A_i)`, `sojourn_i = Wq_i + S_i` is run per lane and the
metric is `viol` = the fraction of post-warmup tasks whose sojourn exceeds the SLA
`W_target = 10`. The high-variance lane violates the SLA at a MULTIPLE of the low-variance
lane's rate despite equal ρ (R1), the P–K mean-wait closed form anchors both lanes (R2), the
violation ratio rises MONOTONICALLY with CV crossing 2× near CV ≈ 1.51 (R3), and
**re-provisioning** lane B to a LOWER load `ρ_B* = 0.512` (via `mean_s = 0.64`) drives its
violation rate back to the low-variance lane's — the falsifier that isolates variance, not ρ,
as the cause (R4).

On a pinned world (N = 200 000 tasks/lane/rep, warmup = 20 000, R = 12 reps, seeds
S = [1001…1012]) each rep draws its own service stream `random.Random(service_seed)` and its
own arrival stream `random.Random(arrival_seed)`, with `Exp(mean = m)` sampled as
`−m·log(1 − u)` (version-independent, not `random.expovariate`). The balanced-means H2 uses
`p1 = (1 + √r)/2`, `r = (CV²−1)/(CV²+1)`, phase means `m1 = mean_s/(2p1)`, `m2 = mean_s/(2p2)`;
at `CV = 1` the formula degenerates (`r = 0 → p1 = p2 = 0.5`, `m1 = m2 = mean_s`) so lane A
uses the identical sampler with no special case. P089 pre-registered an APPROVE rule requiring
ALL four gates R1–R4. The measured run APPROVES: `viol_A = 0.136890`, `viol_B = 0.498021`,
ratio **3.638** clearing the 2.5× floor by **22.49σ** with the gap separated at **95.58σ**
(R1); measured `Wq` within **0.72 %** (lane A) and **2.01 %** (lane B) of the P–K anchor (R2);
a strictly monotone dose-response with adjacent separations 30.50 / 15.27 / 9.15 / 5.01 / 4.44σ
and a 2× crossover at **CV = 1.5099** inside [1.36, 1.66] (R3); and the re-provisioned lane B*
at `viol_B* = 0.136513`, a gap of **−0.000376** (0.20σ) from lane A with `ρ_B* = 0.512 < 0.8`
(R4). VERDICT **APPROVE**, first failing gate None.

## Run (one command)

```
python3 variance_blind_provisioning_trap_sim.py
```

Exit 0 iff every self-check passes (14/14) AND the twin evaluators agree. Deterministic:
`results.json` and `run-stdout.txt` are byte-identical across process runs — no wall clock, no
network, no git at run time, no PYTHONHASHSEED dependence. Stdlib only, CPython 3. ≈ 6 s/run.
Each arm uses two `random.Random` instances (one service, one arrival) keyed by
`service_seed = seed·7919 + round(CV·1000) + round(mean_s·1000)·7000003` and
`arrival_seed = seed·104729 + round(mean_s·1000)`; the arrival key is CV-independent, so the
`mean_s = 1.0` arms share arrival streams per seed (common random numbers across the CV sweep).

## Structure — one exact queue model + four gates + twin evaluators

- **Exact M/G/1 Lindley recursion** — no diffusion or heavy-traffic approximation; the
  waiting time of every task is computed from the previous task's wait + service − this task's
  interarrival gap, floored at zero. The first 20 000 tasks are run but excluded from all
  metrics (warmup); each rep scores exactly 180 000 post-warmup tasks.
- **Balanced-means H2 service sampler (unified)** — `CV ≥ 1` two-phase hyperexponential with
  matched mean; `CV = 1` degenerates to plain exponential through the same code path. Verified
  analytically at `CV = 3, mean_s = 1`: `p1 = 0.947214`, `m1 = 0.527864`, `m2 = 9.472136`,
  `E[S] = 1.000000`, `E[S²] = 10.000000`, `CV = 3.000000` to 1e-6.
- **P–K closed form** — `Wq_PK = (ρ/(1−ρ))·((1+CV²)/2)·E[S]`, verified at the two known
  points `CV = 1 → 4.0`, `CV = 3 → 20.0`; the R2 sanity gate anchors the measured mean wait to
  it within 5 % for both lanes.
- **Twin evaluators** — `decide_ifchain` (ordered short-circuit if/elif chain) and
  `decide_table` (independently transcribed table/loop) agree on the ruling token AND the
  first-failing gate over the measured gate outcomes — APPROVE/None both. A divergence raises
  `SystemExit` (exit ≠ 0).

## Decision rule (pre-registered, from P089)

**APPROVE iff R1 AND R2 AND R3 AND R4**, the rule firing in order R1→R2→R3→R4.

- **R1 trap effect:** `ratio = viol_B/viol_A ≥ 2.5` AND clears 2.5× by ≥3σ
  (`(ratio − 2.5)/se_ratio ≥ 3`) AND `gap = viol_B − viol_A` separated ≥3σ. Delta-method
  `se_ratio = ratio·√((se_A/viol_A)² + (se_B/viol_B)²)`, `se_gap = √(se_A² + se_B²)`.
- **R2 P–K sanity:** `|Wq_measured − Wq_PK|/Wq_PK ≤ 0.05` for BOTH lanes (failure ⇒ INVALID,
  not REJECT).
- **R3 dose-response:** with ρ = 0.8 fixed, `ratio(CV) = viol(CV)/viol_A` strictly monotone
  over `CV ∈ {1.0, 1.5, 2.0, 2.5, 3.0, 3.5}`, each adjacent pair separated ≥3σ, AND the 2×
  crossover (linear interpolation of ratio vs CV where ratio = 2.0) inside CV = 1.51 ± 0.15,
  i.e. [1.36, 1.66]. The CV = 1.0 point is `ratio = 1.0` by construction (se = 0).
- **R4 provisioning correction / falsifier:** at the re-provisioned lane B*
  (`ρ_B* = 0.512`, `mean_s = 0.64`, `CV = 3`): `|viol_B* − viol_A| ≤ 3·se_gap*` AND
  `ρ_B* = 0.512 < ρ_A = 0.8`.

- **REJECT** — R1 hard-fail (no real ≥3σ effect that clears 2.5×), OR R4 fails to close within
  3σ / needs `ρ_B* ≥ ρ_A`.
- **NULL** — R1 sub-threshold (a real ≥3σ gap that does NOT clear 2.5× by ≥3σ), OR R3
  non-monotone / crossover outside 1.51 ± 0.15.
- **INVALID** — the two process runs are not byte-identical (non-deterministic), OR the R2 P–K
  anchor is off by > 5 % for either lane.

`SE = SD/√12` with SD = sample SD (ddof = 1) across the 12 per-rep values. Full pinned world in
`fixtures.json`.

## Layout

- `fixtures.json` — the pinned world (λ, N, warmup, R, seeds, W_target), the H2 params for
  lanes A/B, the P–K anchors, the gate thresholds and decision rule, the source proposal
  header, and the seed-1001 first-20 service draws (lane A + lane B) and first-20 arrival gaps
  (lane A) full-precision via `repr` (the committed fixture, re-verified each run).
- `variance_blind_provisioning_trap_sim.py` — the single runner (`build_fixture` path +
  self-check `main`).
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs (byte-identical
  across a double run).
- `REPORT.md` — the verdict report (gate-by-gate table, P–K anchor table, dose-response ratio
  table with crossover, R4 correction, determinism digests).

**VERDICT: APPROVE** (first failing gate None) — 14/14 self-checks, exit 0, byte-identical
double run, twin evaluators agree APPROVE/None.
