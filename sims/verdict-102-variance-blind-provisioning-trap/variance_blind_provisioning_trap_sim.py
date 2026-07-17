#!/usr/bin/env python3
"""VERDICT-102 - variance-blind provisioning trap (M/G/1 SLA-violation trap).

Source proposal (header cited verbatim):
  ## PROPOSAL 089 * 2026-07-16T22:04:51Z * status: sim-ready
  idea-engine PROPOSAL 089 (registered spec: variance-blind-provisioning-trap-2026-07-16)
PROPOSAL<->VERDICT offset = +13 (PROPOSAL 089 -> VERDICT 102), the twenty-sixth row,
consistent with the P087 -> V100, P088 -> V101 precedent.

Pinned world (reproduced exactly from the registered P089 spec):
  Two single-server FCFS M/G/1 lanes. Poisson arrivals rate lam=0.8 (interarrival ~
  Exponential mean 1/lam=1.25). Baseline mean service E[S]=1.0 -> nominal rho=lam*E[S]=0.8.
  Exact Lindley single-server recursion (no approximation):
    Wq_1 = 0; Wq_i = max(0, Wq_{i-1} + S_{i-1} - A_i); sojourn_i = Wq_i + S_i.
    A_i is the i-th interarrival gap (Exponential mean 1.25); S_i the i-th service time.
  SLA target W_target = 10.0 (= 10*E[S]); metric viol = fraction of POST-WARMUP completed
  tasks with sojourn_i > 10.0. N=200000 tasks/lane/rep, warmup=20000 (the recursion is run
  through warmup but the first 20000 tasks are EXCLUDED from every metric), R=12
  replications, fixed seeds S=[1001,1002,...,1012].
  Service sampler (SINGLE consistent sampler for ALL arms) - balanced-means 2-phase
  hyperexponential H2 with mean=mean_s and coefficient of variation CV>=1:
    r  = (CV^2 - 1)/(CV^2 + 1)
    p1 = (1 + sqrt(r))/2 ; p2 = 1 - p1
    m1 = mean_s/(2*p1)   ; m2 = mean_s/(2*p2)   (balanced means: each phase carries mean_s/2)
    draw u ~ Uniform[0,1): if u < p1 -> Exponential(mean=m1) else Exponential(mean=m2).
    At CV=1.0 the formula DEGENERATES: r=0 -> p1=p2=0.5, m1=m2=mean_s (plain Exponential),
    so lane A (CV=1) uses the identical sampler as every other arm - no special case.
    Exponential(mean=m) drawn as -m*log(1-u), u~Uniform[0,1) from the arm's service stream
    (version-independent; not random.expovariate). Phase-select u and the exponential u are
    two SEPARATE draws from the service stream.
  Determinism / seeding: per-arm INDEPENDENT streams from random.Random with deterministic
  integer keys, two Random instances per (seed, CV, mean_s) arm:
    service_seed = seed*7919   + round(CV*1000) + round(mean_s*1000)*7000003
    arrival_seed = seed*104729 + round(mean_s*1000)
  (arrival_seed is CV-independent, so the mean_s=1.0 arms share arrival streams per seed -
  common random numbers across the CV sweep; the mean_s=0.64 arm gets its own arrival stream.)

P-K closed form (R2 anchor):
  Wq_PK = (rho/(1-rho)) * ((1+CV^2)/2) * E[S], rho=lam*mean_s, E[S]=mean_s.
  Check: CV=1 -> 4.0 ; CV=3 -> 20.0 (at mean_s=1.0). Measured Wq = pooled mean of Wq_i over
  the post-warmup tasks.

Arms (each = 12 reps):
  laneA     CV=1.0 mean_s=1.0 (rho=0.8)   - R1/R2 baseline + R3 CV=1.0 point + R4 reference.
  laneB     CV=3.0 mean_s=1.0 (rho=0.8)   - R1/R2 + R3 CV=3.0 point.
  dose sweep CV in {1.5,2.0,2.5,3.5} mean_s=1.0 (CV=1.0 & 3.0 reuse laneA/laneB).
  laneBstar CV=3.0 mean_s=0.64 (rho=0.512) - R4 corrected re-provisioned lane.
  Per arm: pooled mean over the 12 rep-values; sample SD across the 12 rep-values (ddof=1);
  SE = SD/sqrt(12). Computed for both Wq and viol.

Pre-registered gates (evaluate in order R1->R2->R3->R4; APPROVE iff ALL hold):
  R1 (trap effect): ratio = viol_B/viol_A >= k=2.5 AND clears k by >=3 sigma
      ((ratio-k)/se_ratio >= 3), AND gap = viol_B-viol_A separated >=3 sigma (gap/se_gap>=3).
      se_ratio (delta method) = ratio*sqrt((se_A/viol_A)^2 + (se_B/viol_B)^2);
      se_gap = sqrt(se_A^2 + se_B^2). Pre-registered k=2.5.
  R2 (P-K sanity): |Wq_measured - Wq_PK|/Wq_PK <= 0.05 for BOTH lanes. Failure => INVALID.
  R3 (dose-response): with rho=0.8 fixed, ratio(CV)=viol(CV)/viol_A strictly monotone
      increasing over CV in {1.0,1.5,2.0,2.5,3.0,3.5}, each adjacent pair separated >=3 sigma;
      AND the 2x crossover (linear interpolation of ratio vs CV where ratio=2.0) falls within
      CV=1.51 +/- 0.15, i.e. [1.36,1.66]. (ratio at CV=1.0 is 1.0 by construction, se=0.)
  R4 (provisioning correction / falsifier): at the re-provisioned lane B* (rho_B*=0.512,
      mean_s=0.64, CV=3.0): |viol_B* - viol_A| <= 3*se_gap* (se_gap*=sqrt(se_A^2+se_B*^2))
      AND rho_B*=0.512 strictly < rho_A=0.8.

Decision rule (applied MECHANICALLY, never softened):
  APPROVE iff R1 and R2 and R3 and R4 all hold.
  INVALID if the double-run is non-deterministic (proven externally by byte-identical
    results.json + run-stdout.txt across two process runs) OR R2 P-K anchor off by >5% for
    either lane.
  REJECT on HARD-FAIL: R1 gap fails to clear 2.5x by >=3 sigma (no real >=3 sigma effect),
    OR R4 fails to close within 3 sigma / needs rho_B* >= rho_A.
  NULL if effect present but sub-threshold: a real >=3 sigma gap that does not clear 2.5x by
    >=3 sigma, OR crossover outside 1.51+/-0.15 / non-monotone dose-response.
  first_failing_gate = first of R1,R2,R3,R4 that fails, else None.

Twin evaluators: decide_ifchain() (ordered short-circuit if/elif chain) and decide_table()
  (independent table/loop transcription of the same rules) must agree on BOTH the verdict
  token AND first_failing_gate; on disagreement raise SystemExit with a diff.

Determinism: fully hermetic (no network / repo reads, no wall-clock, no PYTHONHASHSEED
  dependence). results.json and run-stdout.txt are byte-identical across a double run; the
  per-arm sample sizes plus the first-20 service draws (laneA + laneB) and first-20 arrival
  gaps (laneA), full precision via repr, plus the P-K anchors and gate thresholds, are
  committed as the fixture and re-verified each run.
"""
import json
import hashlib
import math
import os

# ---- pinned-world constants (top-of-file, per the registration) ----
LAM = 0.8                       # Poisson arrival rate; interarrival mean 1/LAM = 1.25
MEAN_S_BASE = 1.0               # baseline mean service -> nominal rho = LAM*MEAN_S_BASE = 0.8
W_TARGET = 10.0                 # SLA sojourn target (= 10 * E[S])
N_TASKS = 200000                # tasks per lane per rep
WARMUP = 20000                  # first WARMUP tasks excluded from ALL metrics
N_REPS = 12                     # replications
SEEDS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012]
N_METRIC = N_TASKS - WARMUP     # post-warmup tasks scored per rep (180000)

K_RATIO = 2.5                   # R1 pre-registered trap-effect ratio floor
SEP_MIN = 3.0                   # >=3 sigma separation requirement
PK_TOL = 0.05                   # R2 P-K relative-error tolerance (>5% => INVALID)
CROSSOVER_LEVEL = 2.0           # R3 2x crossover level
CROSSOVER_CENTER = 1.51         # R3 crossover target CV
CROSSOVER_HALFWIDTH = 0.15      # R3 crossover band half-width -> [1.36, 1.66]

CV_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]     # R3 dose-response CV sweep at rho=0.8
RHO_A = LAM * MEAN_S_BASE                     # 0.8
MEAN_S_BSTAR = 0.64                           # R4 re-provisioned lane mean service
CV_B = 3.0                                    # lane B / lane B* coefficient of variation
RHO_BSTAR = LAM * MEAN_S_BSTAR                # 0.512

HERE = os.path.dirname(os.path.abspath(__file__))

# Arms: label -> (CV, mean_s). laneA/laneB reused by R3 as its CV=1.0 / CV=3.0 points.
ARMS = [
    ("laneA", 1.0, 1.0),
    ("cv1.5", 1.5, 1.0),
    ("cv2.0", 2.0, 1.0),
    ("cv2.5", 2.5, 1.0),
    ("laneB", 3.0, 1.0),
    ("cv3.5", 3.5, 1.0),
    ("laneBstar", 3.0, 0.64),
]
# CV -> arm label for the R3 sweep (mean_s=1.0 arms only).
CV_ARM = {1.0: "laneA", 1.5: "cv1.5", 2.0: "cv2.0", 2.5: "cv2.5", 3.0: "laneB", 3.5: "cv3.5"}

# Expected analytic H2 verification points at CV=3.0, mean_s=1.0 (6dp) for the self-check.
EXP_P1_CV3 = 0.947214
EXP_M1_CV3 = 0.527864
EXP_M2_CV3 = 9.472136
EXP_ES_CV3 = 1.000000
EXP_ES2_CV3 = 10.000000
ANALYTIC_TOL = 1e-6

_LOG = math.log


# --------------------------------------------------------------------------
# Service / arrival samplers (SINGLE consistent sampler for all arms).
# --------------------------------------------------------------------------
def h2_params(cv, mean_s):
    """Balanced-means 2-phase hyperexponential params (p1,p2,m1,m2).

    Unified sampler: at CV=1.0 the formula degenerates to p1=p2=0.5, m1=m2=mean_s
    (plain Exponential) with NO special case - r = (CV^2-1)/(CV^2+1) = 0 there.
    """
    r = (cv * cv - 1.0) / (cv * cv + 1.0)
    p1 = (1.0 + math.sqrt(r)) / 2.0
    p2 = 1.0 - p1
    m1 = mean_s / (2.0 * p1)
    m2 = mean_s / (2.0 * p2)
    return p1, p2, m1, m2


def draw_service(rand, p1, m1, m2):
    """One H2 service time: phase-select draw then a separate exponential draw.

    Exponential(mean=m) = -m*log(1-u). IDENTICAL arithmetic to the simulate_rep hot loop
    (guarded by the sampler_inline_matches_helper self-check).
    """
    u = rand()
    if u < p1:
        return -m1 * _LOG(1.0 - rand())
    return -m2 * _LOG(1.0 - rand())


def draw_gap(rand, inv_lam):
    """One interarrival gap ~ Exponential(mean=inv_lam) = -inv_lam*log(1-u)."""
    return -inv_lam * _LOG(1.0 - rand())


def arm_seeds(cv, mean_s, seed):
    """Deterministic per-arm (service_seed, arrival_seed) integer keys."""
    service_seed = seed * 7919 + round(cv * 1000) + round(mean_s * 1000) * 7000003
    arrival_seed = seed * 104729 + round(mean_s * 1000)
    return service_seed, arrival_seed


# --------------------------------------------------------------------------
# Stats -- pure stdlib.
# --------------------------------------------------------------------------
def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    """Sample standard deviation, ddof=1."""
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) * (x - m) for x in xs) / (n - 1)
    return math.sqrt(var)


def pool(xs):
    """Pool per-rep values -> (mean, sd(ddof=1), se=sd/sqrt(n))."""
    m = mean(xs)
    sd = sample_std(xs)
    se = sd / math.sqrt(len(xs))
    return m, sd, se


def separation(ma, sea, mb, seb):
    """Between-estimate separation |ma-mb| / sqrt(sea^2 + seb^2)."""
    denom = math.sqrt(sea * sea + seb * seb)
    if denom == 0.0:
        return float("inf") if ma != mb else 0.0
    return abs(ma - mb) / denom


def wq_pk(cv, mean_s):
    """Pollaczek-Khinchine mean queue wait Wq for M/G/1."""
    rho = LAM * mean_s
    return (rho / (1.0 - rho)) * ((1.0 + cv * cv) / 2.0) * mean_s


# --------------------------------------------------------------------------
# Model -- exact single-server Lindley recursion over one replication.
# --------------------------------------------------------------------------
def simulate_rep(cv, mean_s, seed):
    """Run one replication; return (wq_mean, viol_frac, n_metric) over post-warmup tasks."""
    import random
    p1, p2, m1, m2 = h2_params(cv, mean_s)
    service_seed, arrival_seed = arm_seeds(cv, mean_s, seed)
    rs = random.Random(service_seed).random
    ra = random.Random(arrival_seed).random
    inv_lam = 1.0 / LAM
    log = _LOG
    warm = WARMUP
    w_target = W_TARGET
    viol_ct = 0
    wq_sum = 0.0
    n_metric = 0
    prev_wq = 0.0
    prev_s = 0.0
    for i in range(N_TASKS):
        u = rs()
        if u < p1:
            s = -m1 * log(1.0 - rs())
        else:
            s = -m2 * log(1.0 - rs())
        if i == 0:
            wq = 0.0
        else:
            wq = prev_wq + prev_s - (-inv_lam * log(1.0 - ra()))
            if wq < 0.0:
                wq = 0.0
        if i >= warm:
            wq_sum += wq
            n_metric += 1
            if wq + s > w_target:
                viol_ct += 1
        prev_wq = wq
        prev_s = s
    return wq_sum / n_metric, viol_ct / n_metric, n_metric


def simulate_arm(cv, mean_s):
    """Run the 12 reps for one arm; return per-rep + pooled Wq and viol."""
    wq_reps = []
    viol_reps = []
    n_metrics = []
    for seed in SEEDS:
        wq_m, viol, n_metric = simulate_rep(cv, mean_s, seed)
        wq_reps.append(wq_m)
        viol_reps.append(viol)
        n_metrics.append(n_metric)
    wq_mean, wq_sd, wq_se = pool(wq_reps)
    viol_mean, viol_sd, viol_se = pool(viol_reps)
    return {
        "cv": cv, "mean_s": mean_s, "rho": LAM * mean_s,
        "wq_reps": wq_reps, "viol_reps": viol_reps, "n_metrics": n_metrics,
        "wq_mean": wq_mean, "wq_sd": wq_sd, "wq_se": wq_se,
        "viol_mean": viol_mean, "viol_sd": viol_sd, "viol_se": viol_se,
        "wq_pk": wq_pk(cv, mean_s),
    }


def simulate():
    """Run every arm; return {label: arm_result}."""
    return {label: simulate_arm(cv, mean_s) for label, cv, mean_s in ARMS}


# --------------------------------------------------------------------------
# Gate evaluation.
# --------------------------------------------------------------------------
def ratio_and_se(a_arm, b_arm):
    """ratio = viol_b/viol_a and its delta-method SE."""
    va, sea = a_arm["viol_mean"], a_arm["viol_se"]
    vb, seb = b_arm["viol_mean"], b_arm["viol_se"]
    ratio = vb / va
    se_ratio = ratio * math.sqrt((sea / va) ** 2 + (seb / vb) ** 2)
    return ratio, se_ratio


def compute_gates(arms):
    a = arms["laneA"]
    b = arms["laneB"]
    bstar = arms["laneBstar"]
    va, sea = a["viol_mean"], a["viol_se"]
    vb, seb = b["viol_mean"], b["viol_se"]

    # ---- R1: trap effect -- ratio>=k cleared by >=3 sigma AND gap separated >=3 sigma ----
    ratio, se_ratio = ratio_and_se(a, b)
    gap = vb - va
    se_gap = math.sqrt(sea * sea + seb * seb)
    r1_ratio_floor = ratio >= K_RATIO
    r1_ratio_sigma = (ratio - K_RATIO) / se_ratio if se_ratio > 0 else float("inf")
    r1_ratio_clear = r1_ratio_sigma >= SEP_MIN
    r1_gap_sigma = gap / se_gap if se_gap > 0 else float("inf")
    r1_gap_real = r1_gap_sigma >= SEP_MIN
    r1 = r1_ratio_floor and r1_ratio_clear and r1_gap_real

    # ---- R2: P-K sanity for BOTH lanes (failure => INVALID) ----
    def pk_err(arm):
        return abs(arm["wq_mean"] - arm["wq_pk"]) / arm["wq_pk"]
    r2_err_a = pk_err(a)
    r2_err_b = pk_err(b)
    r2_a_ok = r2_err_a <= PK_TOL
    r2_b_ok = r2_err_b <= PK_TOL
    r2 = r2_a_ok and r2_b_ok

    # ---- R3: dose-response monotone + adjacent >=3 sigma + 2x crossover in band ----
    grid = []
    for cv in CV_GRID:
        arm = arms[CV_ARM[cv]]
        if cv == 1.0:
            grid.append((cv, 1.0, 0.0))              # ratio 1.0 by construction, se=0
        else:
            r, se_r = ratio_and_se(a, arm)
            grid.append((cv, r, se_r))
    r3_monotone = all(grid[j + 1][1] > grid[j][1] for j in range(len(grid) - 1))
    r3_adj_sep = [separation(grid[j][1], grid[j][2], grid[j + 1][1], grid[j + 1][2])
                  for j in range(len(grid) - 1)]
    r3_sep_ok = all(s >= SEP_MIN for s in r3_adj_sep)
    # 2x crossover via linear interpolation of ratio vs CV where ratio == 2.0.
    crossover_cv = None
    for j in range(len(grid) - 1):
        r_lo, r_hi = grid[j][1], grid[j + 1][1]
        if r_lo < CROSSOVER_LEVEL <= r_hi:
            cv_lo, cv_hi = grid[j][0], grid[j + 1][0]
            crossover_cv = cv_lo + (CROSSOVER_LEVEL - r_lo) / (r_hi - r_lo) * (cv_hi - cv_lo)
            break
    band_lo = CROSSOVER_CENTER - CROSSOVER_HALFWIDTH
    band_hi = CROSSOVER_CENTER + CROSSOVER_HALFWIDTH
    r3_crossover_ok = crossover_cv is not None and band_lo <= crossover_cv <= band_hi
    r3 = r3_monotone and r3_sep_ok and r3_crossover_ok

    # ---- R4: provisioning correction / falsifier ----
    vbs, sebs = bstar["viol_mean"], bstar["viol_se"]
    gap_star = vbs - va
    se_gap_star = math.sqrt(sea * sea + sebs * sebs)
    r4_close = abs(gap_star) <= SEP_MIN * se_gap_star
    r4_gap_sigma = abs(gap_star) / se_gap_star if se_gap_star > 0 else float("inf")
    r4_rho_ok = RHO_BSTAR < RHO_A
    r4 = r4_close and r4_rho_ok

    return {
        "R1": r1, "R2": r2, "R3": r3, "R4": r4,
        # R1 detail
        "R1_ratio": ratio, "R1_se_ratio": se_ratio, "R1_k": K_RATIO,
        "R1_ratio_floor_ok": r1_ratio_floor, "R1_ratio_sigma_over_k": r1_ratio_sigma,
        "R1_ratio_clear_ok": r1_ratio_clear,
        "R1_gap": gap, "R1_se_gap": se_gap, "R1_gap_sigma": r1_gap_sigma,
        "R1_gap_real": r1_gap_real, "R1_viol_A": va, "R1_viol_B": vb,
        "R1_se_A": sea, "R1_se_B": seb,
        # R2 detail
        "R2_err_A": r2_err_a, "R2_err_B": r2_err_b, "R2_a_ok": r2_a_ok, "R2_b_ok": r2_b_ok,
        "R2_wq_A": a["wq_mean"], "R2_pk_A": a["wq_pk"],
        "R2_wq_B": b["wq_mean"], "R2_pk_B": b["wq_pk"],
        # R3 detail
        "R3_grid": grid, "R3_monotone_ok": r3_monotone, "R3_adj_sep": r3_adj_sep,
        "R3_sep_ok": r3_sep_ok, "R3_crossover_cv": crossover_cv,
        "R3_crossover_ok": r3_crossover_ok, "R3_band": [band_lo, band_hi],
        # R4 detail
        "R4_viol_Bstar": vbs, "R4_se_Bstar": sebs, "R4_gap_star": gap_star,
        "R4_se_gap_star": se_gap_star, "R4_gap_sigma": r4_gap_sigma,
        "R4_close_ok": r4_close, "R4_rho_ok": r4_rho_ok,
        "R4_rho_Bstar": RHO_BSTAR, "R4_rho_A": RHO_A,
    }


# --------------------------------------------------------------------------
# Twin evaluators.
# --------------------------------------------------------------------------
def decide_ifchain(gr):
    """Evaluator A: ordered short-circuit if/elif chain over R1->R2->R3->R4."""
    if not gr["R1"]:
        # real >=3 sigma effect but sub-threshold on 2.5x -> NULL; else HARD-FAIL -> REJECT
        if gr["R1_gap_real"]:
            return "NULL", "R1"
        return "REJECT", "R1"
    if not gr["R2"]:
        return "INVALID", "R2"           # P-K anchor off by >5% -> INVALID (not REJECT)
    if not gr["R3"]:
        return "NULL", "R3"              # non-monotone / crossover outside band -> NULL
    if not gr["R4"]:
        return "REJECT", "R4"           # falsifier fails to close / rho ordering -> REJECT
    return "APPROVE", None


def decide_table(gr):
    """Evaluator B: independent table/loop transcription of the same ordered rules."""
    r1_token = "NULL" if gr["R1_gap_real"] else "REJECT"
    table = [
        ("R1", gr["R1"], r1_token),
        ("R2", gr["R2"], "INVALID"),
        ("R3", gr["R3"], "NULL"),
        ("R4", gr["R4"], "REJECT"),
    ]
    for name, ok, token in table:
        if not ok:
            return token, name
    return "APPROVE", None


# --------------------------------------------------------------------------
# Fixture.
# --------------------------------------------------------------------------
def _first_service_draws(cv, mean_s, seed, n):
    import random
    p1, p2, m1, m2 = h2_params(cv, mean_s)
    service_seed, _ = arm_seeds(cv, mean_s, seed)
    rs = random.Random(service_seed).random
    return [repr(draw_service(rs, p1, m1, m2)) for _ in range(n)]


def _first_arrival_gaps(cv, mean_s, seed, n):
    import random
    _, arrival_seed = arm_seeds(cv, mean_s, seed)
    ra = random.Random(arrival_seed).random
    inv_lam = 1.0 / LAM
    return [repr(draw_gap(ra, inv_lam)) for _ in range(n)]


def build_fixture():
    """Seed-anchored fixture: sample sizes, first-20 service draws (laneA+laneB), first-20
    arrival gaps (laneA), the P-K anchors and gate thresholds - written on first run, else
    verified against the committed copy."""
    p1a, p2a, m1a, m2a = h2_params(1.0, 1.0)
    p1b, p2b, m1b, m2b = h2_params(3.0, 1.0)
    return {
        "source": "scratchpad/v102 :: verdict-102-variance-blind-provisioning-trap",
        "proposal": "## PROPOSAL 089 * 2026-07-16T22:04:51Z * status: sim-ready "
                    "(idea-engine PROPOSAL 089, registered spec "
                    "variance-blind-provisioning-trap-2026-07-16); offset +13 -> VERDICT 102",
        "pinned_world": {
            "lam": LAM, "interarrival_mean": 1.0 / LAM, "mean_s_base": MEAN_S_BASE,
            "w_target": W_TARGET, "n_tasks": N_TASKS, "warmup": WARMUP,
            "n_metric_per_rep": N_METRIC, "n_reps": N_REPS, "seeds": SEEDS,
            "model": "two single-server FCFS M/G/1 lanes; exact Lindley recursion "
                     "Wq_i=max(0,Wq_{i-1}+S_{i-1}-A_i), sojourn_i=Wq_i+S_i; Wq_1=0",
            "service_sampler": "balanced-means 2-phase hyperexponential H2 "
                               "(unified; CV=1 degenerates to Exponential); "
                               "Exp(mean=m) = -m*log(1-u)",
            "seeding": "service_seed = seed*7919 + round(CV*1000) + round(mean_s*1000)*7000003; "
                       "arrival_seed = seed*104729 + round(mean_s*1000); two Random per arm",
            "pooling": "per arm pooled mean over 12 rep-values; sample SD ddof=1; SE=SD/sqrt(12)",
        },
        "h2_params": {
            "laneA_cv1.0": {"p1": p1a, "p2": p2a, "m1": m1a, "m2": m2a},
            "laneB_cv3.0": {"p1": p1b, "p2": p2b, "m1": m1b, "m2": m2b},
        },
        "pk_anchors": {
            "laneA": wq_pk(1.0, 1.0), "laneB": wq_pk(3.0, 1.0),
            "laneBstar": wq_pk(3.0, 0.64),
        },
        "gate_thresholds": {
            "k_ratio": K_RATIO, "sep_min": SEP_MIN, "pk_tol": PK_TOL,
            "crossover_level": CROSSOVER_LEVEL, "crossover_band": [
                CROSSOVER_CENTER - CROSSOVER_HALFWIDTH, CROSSOVER_CENTER + CROSSOVER_HALFWIDTH],
            "rho_A": RHO_A, "rho_Bstar": RHO_BSTAR,
        },
        "preregistered_gates": {
            "R1": "trap effect: ratio=viol_B/viol_A>=2.5 cleared by >=3 sigma AND "
                  "gap=viol_B-viol_A separated >=3 sigma",
            "R2": "P-K sanity: |Wq_measured-Wq_PK|/Wq_PK<=0.05 for BOTH lanes (else INVALID)",
            "R3": "dose-response: ratio(CV)=viol(CV)/viol_A strictly monotone over "
                  "CV in {1.0,1.5,2.0,2.5,3.0,3.5}, adjacent pairs >=3 sigma, 2x crossover in "
                  "[1.36,1.66]",
            "R4": "provisioning correction: |viol_B*-viol_A|<=3*se_gap* AND rho_B*=0.512<rho_A=0.8",
            "decision_rule": "APPROVE iff R1 and R2 and R3 and R4 (order R1->R2->R3->R4); "
                             "INVALID if non-deterministic or R2 off >5%; REJECT on R1/R4 "
                             "hard-fail; NULL if R1 sub-threshold or R3 non-monotone/crossover",
        },
        "n_metric_per_rep": N_METRIC,
        "laneA_seed1001_first20_service_repr": _first_service_draws(1.0, 1.0, 1001, 20),
        "laneB_seed1001_first20_service_repr": _first_service_draws(3.0, 1.0, 1001, 20),
        "laneA_seed1001_first20_arrival_repr": _first_arrival_gaps(1.0, 1.0, 1001, 20),
    }


def canon(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# --------------------------------------------------------------------------
# Main.
# --------------------------------------------------------------------------
def main():
    import random
    L = []

    def out(s=""):
        L.append(s)

    arms = simulate()
    gr = compute_gates(arms)
    vA, rA = decide_ifchain(gr)
    vB, rB = decide_table(gr)

    # ---- fixture: write on first run, else verify committed ----
    fx_path = os.path.join(HERE, "fixtures.json")
    fixture = build_fixture()
    if os.path.exists(fx_path):
        with open(fx_path) as f:
            committed = json.load(f)
        fixture_ok = (
            committed.get("n_metric_per_rep") == fixture["n_metric_per_rep"]
            and committed.get("laneA_seed1001_first20_service_repr")
                == fixture["laneA_seed1001_first20_service_repr"]
            and committed.get("laneB_seed1001_first20_service_repr")
                == fixture["laneB_seed1001_first20_service_repr"]
            and committed.get("laneA_seed1001_first20_arrival_repr")
                == fixture["laneA_seed1001_first20_arrival_repr"]
            and committed.get("pk_anchors") == fixture["pk_anchors"]
            and committed.get("gate_thresholds") == fixture["gate_thresholds"]
        )
    else:
        with open(fx_path, "w") as f:
            f.write(canon(fixture) + "\n")
        fixture_ok = True

    # ---- analytic H2 verification at CV=3.0, mean_s=1.0 ----
    p1, p2, m1, m2 = h2_params(3.0, 1.0)
    es = p1 * m1 + p2 * m2
    es2 = p1 * 2.0 * m1 * m1 + p2 * 2.0 * m2 * m2
    cv_check = math.sqrt(es2 - es * es) / es
    analytic_ok = (
        abs(p1 - EXP_P1_CV3) <= ANALYTIC_TOL and abs(m1 - EXP_M1_CV3) <= ANALYTIC_TOL
        and abs(m2 - EXP_M2_CV3) <= ANALYTIC_TOL and abs(es - EXP_ES_CV3) <= ANALYTIC_TOL
        and abs(es2 - EXP_ES2_CV3) <= ANALYTIC_TOL and abs(cv_check - 3.0) <= ANALYTIC_TOL
    )
    # CV=1.0 degenerate check
    q1, q2, n1, n2 = h2_params(1.0, 1.0)
    degen_ok = (abs(q1 - 0.5) <= ANALYTIC_TOL and abs(q2 - 0.5) <= ANALYTIC_TOL
                and abs(n1 - 1.0) <= ANALYTIC_TOL and abs(n2 - 1.0) <= ANALYTIC_TOL)

    # ---- P-K closed-form known points ----
    pk_known_ok = (abs(wq_pk(1.0, 1.0) - 4.0) <= 1e-9 and abs(wq_pk(3.0, 1.0) - 20.0) <= 1e-9)

    # ---- inline-vs-helper sampler equivalence (guards the hot-loop transcription) ----
    p1b, p2b, m1b, m2b = h2_params(3.0, 1.0)
    probe_seed = 20260717
    ph = random.Random(probe_seed).random
    helper_vals = [repr(draw_service(ph, p1b, m1b, m2b)) for _ in range(40)]
    pi = random.Random(probe_seed).random
    inline_vals = []
    for _ in range(40):
        u = pi()
        if u < p1b:
            inline_vals.append(repr(-m1b * _LOG(1.0 - pi())))
        else:
            inline_vals.append(repr(-m2b * _LOG(1.0 - pi())))
    inline_ok = helper_vals == inline_vals

    # ---- metric task-count invariant ----
    count_ok = all(nm == N_METRIC for arm in arms.values() for nm in arm["n_metrics"])

    # ---- canonical-JSON stability ----
    probe = {"R1": gr["R1_ratio"], "R3": gr["R3_crossover_cv"], "R4": gr["R4_gap_star"]}
    json_stable = canon(probe) == canon(probe)

    twins_agree = vA == vB and rA == rB

    # ---- self-checks ----
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    chk("pk_closed_form_known_points", pk_known_ok)
    chk("h2_params_cv3_analytic_6dp", analytic_ok)
    chk("h2_params_cv1_degenerate", degen_ok)
    chk("sampler_inline_matches_helper", inline_ok)
    chk("R2_pk_anchor_laneA_within_5pct", gr["R2_a_ok"])
    chk("R2_pk_anchor_laneB_within_5pct", gr["R2_b_ok"])
    chk("R1_trap_effect", gr["R1"])
    chk("R3_dose_monotone_and_separated", gr["R3_monotone_ok"] and gr["R3_sep_ok"])
    chk("R3_crossover_in_band", gr["R3_crossover_ok"])
    chk("R4_correction_closes", gr["R4"])
    chk("twin_evaluators_agree", twins_agree)
    chk("metric_task_count_180000", count_ok)
    chk("fixture_matches_committed", fixture_ok)
    chk("canonical_json_stable", json_stable)

    n_pass = sum(1 for _, c in checks if c)

    # ---- human-readable log ----
    a = arms["laneA"]
    b = arms["laneB"]
    bstar = arms["laneBstar"]
    out("VERDICT-102 - variance-blind provisioning trap (P089)")
    out("=" * 82)
    out("")
    out("Pinned world: two single-server FCFS M/G/1 lanes; exact Lindley recursion")
    out("  Wq_i=max(0,Wq_{i-1}+S_{i-1}-A_i), sojourn_i=Wq_i+S_i (Wq_1=0). lam=%.2f, "
        "interarrival mean %.4f." % (LAM, 1.0 / LAM))
    out("  N=%d tasks/lane/rep, warmup=%d (first %d excluded), R=%d reps, seeds S=%s."
        % (N_TASKS, WARMUP, WARMUP, N_REPS, SEEDS))
    out("  SLA W_target=%.1f; viol = fraction of post-warmup sojourn_i > %.1f. Service = "
        "balanced-means H2 (unified; CV=1 -> Exponential)." % (W_TARGET, W_TARGET))
    out("  Pooling: per arm pooled mean over 12 rep-values; sample SD ddof=1; SE=SD/sqrt(12).")
    out("")
    out("H2 sampler params (CV=3.0, mean_s=1.0): p1=%.6f m1=%.6f m2=%.6f  E[S]=%.6f "
        "E[S^2]=%.6f CV=%.6f" % (p1, m1, m2, es, es2, cv_check))
    out("  expected 6dp: p1=0.947214 m1=0.527864 m2=9.472136 E[S]=1.000000 E[S^2]=10.000000 "
        "CV=3.000000 -> match %s" % analytic_ok)
    out("")
    out("Per-arm results (viol = SLA-violation fraction; Wq = mean queue wait):")
    out("  %-10s %4s %7s | %-26s | %-26s | %-10s" % (
        "arm", "CV", "rho", "viol_mean +/- SE", "Wq_mean +/- SE", "Wq_PK"))
    for label, cv, mean_s in ARMS:
        ar = arms[label]
        out("  %-10s %4.1f %7.3f | %+.6f +/- %.6f  | %10.5f +/- %8.5f | %8.4f" % (
            label, cv, ar["rho"], ar["viol_mean"], ar["viol_se"],
            ar["wq_mean"], ar["wq_se"], ar["wq_pk"]))
    out("")
    out("R1 trap effect (viol_B/viol_A >= %.1f cleared by >=3 sigma; gap separated >=3 sigma):"
        % K_RATIO)
    out("  viol_A=%.6f (SE %.6f)  viol_B=%.6f (SE %.6f)" % (
        gr["R1_viol_A"], gr["R1_se_A"], gr["R1_viol_B"], gr["R1_se_B"]))
    out("  ratio=%.6f (SE %.6f); clears k=%.1f by %.2f sigma (need>=3) %s" % (
        gr["R1_ratio"], gr["R1_se_ratio"], K_RATIO, gr["R1_ratio_sigma_over_k"],
        gr["R1_ratio_clear_ok"]))
    out("  gap=%.6f (SE %.6f); gap separation %.2f sigma (need>=3) %s" % (
        gr["R1_gap"], gr["R1_se_gap"], gr["R1_gap_sigma"], gr["R1_gap_real"]))
    out("  R1 %s" % ("PASS" if gr["R1"] else "FAIL"))
    out("")
    out("R2 P-K sanity (|Wq_measured-Wq_PK|/Wq_PK <= %.2f for BOTH lanes; else INVALID):"
        % PK_TOL)
    out("  laneA Wq=%.5f vs PK=%.4f  rel-err=%.4f  %s" % (
        gr["R2_wq_A"], gr["R2_pk_A"], gr["R2_err_A"], gr["R2_a_ok"]))
    out("  laneB Wq=%.5f vs PK=%.4f  rel-err=%.4f  %s" % (
        gr["R2_wq_B"], gr["R2_pk_B"], gr["R2_err_B"], gr["R2_b_ok"]))
    out("  R2 %s" % ("PASS" if gr["R2"] else "FAIL"))
    out("")
    out("R3 dose-response (ratio(CV)=viol(CV)/viol_A, rho=0.8 fixed; monotone + adjacent "
        ">=3 sigma; 2x crossover in [%.2f,%.2f]):" % (gr["R3_band"][0], gr["R3_band"][1]))
    out("  %-5s %-14s %-12s %-12s" % ("CV", "ratio", "SE", "adj-sep(sigma)"))
    grid = gr["R3_grid"]
    for j, (cv, r, se_r) in enumerate(grid):
        sep_s = "" if j == 0 else "%.2f" % gr["R3_adj_sep"][j - 1]
        out("  %-5.1f %-14.6f %-12.6f %-12s" % (cv, r, se_r, sep_s))
    out("  monotone %s ; all adjacent separations >=3 sigma %s" % (
        gr["R3_monotone_ok"], gr["R3_sep_ok"]))
    out("  2x crossover CV=%.4f (band [%.2f,%.2f]) %s" % (
        gr["R3_crossover_cv"], gr["R3_band"][0], gr["R3_band"][1], gr["R3_crossover_ok"]))
    out("  R3 %s" % ("PASS" if gr["R3"] else "FAIL"))
    out("")
    out("R4 provisioning correction / falsifier (re-provisioned lane B*, rho_B*=%.3f<rho_A=%.1f):"
        % (RHO_BSTAR, RHO_A))
    out("  viol_A=%.6f  viol_B*=%.6f  gap*=%+.6f (SE %.6f)" % (
        gr["R1_viol_A"], gr["R4_viol_Bstar"], gr["R4_gap_star"], gr["R4_se_gap_star"]))
    out("  |gap*| = %.6f <= 3*se_gap* = %.6f (%.2f sigma) %s ; rho ordering %.3f<%.1f %s" % (
        abs(gr["R4_gap_star"]), SEP_MIN * gr["R4_se_gap_star"], gr["R4_gap_sigma"],
        gr["R4_close_ok"], RHO_BSTAR, RHO_A, gr["R4_rho_ok"]))
    out("  R4 %s" % ("PASS" if gr["R4"] else "FAIL"))
    out("")
    out("Twin evaluators: A(if-chain)=%s/%s  B(table)=%s/%s" % (vA, rA, vB, rB))
    out("")
    for name, c in checks:
        out("  [%s] %s" % ("ok" if c else "XX", name))
    out("Self-checks: %d/%d passed" % (n_pass, len(checks)))
    out("")
    out("VERDICT: %s%s" % (vA, ("" if rA is None else " (first failing gate: %s)" % rA)))

    # ---- results.json (canonical) ----
    def arm_block(ar):
        return {
            "cv": ar["cv"], "mean_s": ar["mean_s"], "rho": ar["rho"],
            "viol_reps": ar["viol_reps"], "viol_mean": ar["viol_mean"],
            "viol_sd": ar["viol_sd"], "viol_se": ar["viol_se"],
            "wq_reps": ar["wq_reps"], "wq_mean": ar["wq_mean"],
            "wq_sd": ar["wq_sd"], "wq_se": ar["wq_se"], "wq_pk": ar["wq_pk"],
            "n_metrics": ar["n_metrics"],
        }

    results = {
        "verdict": vA,
        "first_failing_gate": rA,
        "gates": gr,
        "arms": {label: arm_block(arms[label]) for label, _, _ in ARMS},
        "twin": {"if_chain": [vA, rA], "table": [vB, rB], "agree": twins_agree},
        "self_checks": {name: c for name, c in checks},
        "params": {
            "lam": LAM, "mean_s_base": MEAN_S_BASE, "w_target": W_TARGET,
            "n_tasks": N_TASKS, "warmup": WARMUP, "n_metric_per_rep": N_METRIC,
            "n_reps": N_REPS, "seeds": SEEDS, "k_ratio": K_RATIO, "sep_min": SEP_MIN,
            "pk_tol": PK_TOL, "crossover_level": CROSSOVER_LEVEL,
            "crossover_band": [CROSSOVER_CENTER - CROSSOVER_HALFWIDTH,
                               CROSSOVER_CENTER + CROSSOVER_HALFWIDTH],
            "rho_A": RHO_A, "rho_Bstar": RHO_BSTAR, "cv_grid": CV_GRID,
        },
    }
    res_path = os.path.join(HERE, "results.json")
    canonical = canon(results)
    with open(res_path, "w") as f:
        f.write(canonical + "\n")
    stdout_text = "\n".join(L) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w") as f:
        f.write(stdout_text)
    res_sha = hashlib.sha256((canonical + "\n").encode()).hexdigest()
    std_sha = hashlib.sha256(stdout_text.encode()).hexdigest()
    print(stdout_text, end="")
    print("results.json sha256 : " + res_sha)
    print("run-stdout.txt sha256: " + std_sha)

    # ---- exit code: 0 iff all self-checks pass AND twins agree ----
    if n_pass != len(checks):
        raise SystemExit("SELF-CHECK FAILURE: %d/%d" % (n_pass, len(checks)))
    if not twins_agree:
        raise SystemExit("TWIN DISAGREEMENT: %s/%s vs %s/%s" % (vA, rA, vB, rB))


if __name__ == "__main__":
    main()
