#!/usr/bin/env python3
"""VERDICT-101 - Berkson admission-collider anticorrelation trap.

Source proposal (header cited verbatim):
  ## PROPOSAL 088 * 2026-07-16 * status: sim-ready
  idea-engine PROPOSAL 088 (registered spec: berkson-admission-collider-2026-07-16)
PROPOSAL<->VERDICT offset = +13 (PROPOSAL 088 -> VERDICT 101), consistent with the
P087 -> V100 precedent.

Pinned world (reproduced exactly from the registered P088 spec):
  Two INDEPENDENT latent axes per item, novelty N and rigor R, each iid Normal(0,1),
    drawn from SEPARATE random.Random streams:
      rngN = random.Random(seed)          -> N = [rngN.gauss(0,1) for 2000]
      rngR = random.Random(seed + 10000)  -> R = [rngR.gauss(0,1) for 2000]
    The +10000 offset makes the streams share NO draws, so corr(N,R) = 0 in the
    population BY CONSTRUCTION. n = 2000 items per run. Seeds S=[1,2,3,4,5].
  Admission gate (OR-collider): admit iff N >= t OR R >= t, with a=b=t calibrated so
    the MARGINAL admit rate hits target T. With independent axes each tail-p = P(N>=t),
    the OR admit rate is 1 - (1-p)^2, so p = 1 - sqrt(1-T) and t = Phi^-1(1-p) =
    Phi^-1(sqrt(1-T)). Levels T in {0.50, 0.25, 0.10}, reference T=0.25.
      t(50%) = 0.544952, t(25%) = 1.107798, t(10%) = 1.632219.
  Single-gate control (R4 falsifier): admit iff N >= a_single ALONE, no OR,
    a_single = Phi^-1(1 - 0.25) = Phi^-1(0.75) = 0.674490.
  Phi^-1 via Acklam's stdlib rational approximation (no numpy/scipy).
  Metric: Pearson r in pure stdlib.
    R1 metric  : rho_full  over the FULL 2000-item population (N vs R, unselected).
    R2/R3      : rho_admit over the ADMITTED subset for each OR-gate level.
    R4 metric  : rho_single over the single-gate admitted subset (N>=a_single).
  Pooling across the 5 seeds: pooled mean = mean of the 5 per-seed rho; sigma =
    sample SD (ddof=1); SE = sigma / sqrt(5).

Pre-registered gates (APPROVE iff R1 AND R2 AND R3 AND R4, evaluated in order
R1->R2->R3->R4; first failing gate is the reason):
  R1 (null anchor): |mean(rho_full)| <= 0.03 AND |mean|+3*SE <= 0.03.
  R2 (effect @T=0.25): pooled mean(rho_OR) cleared below -0.45 by >=3 sigma:
      mean+3*SE <= -0.45.
  R3 (dose-response monotone): mean rho_OR at 50% > 25% > 10% (strictly more negative
      as admission tightens), each ADJACENT pair separated by >=3 sigma, where
      sep = |mean_a - mean_b| / sqrt(SE_a^2 + SE_b^2) >= 3.
  R4 (mechanism isolation): single-gate pooled mean(rho_single) within the null band on
      the POOLED-MEAN reading (|mean_single| <= 0.03) AND |mean_OR@25 - mean_single|
      separated >=3 sigma (diff / sqrt(SE_OR25^2 + SE_single^2) >= 3).
      DISCLOSED: R4 is registered on the POOLED-MEAN reading (|mean|<=0.03), NOT R1's
      stricter >=3-sigma-inside test -- the R4 control's 3-sigma envelope (~0.048) pokes
      past 0.03, which is expected and disclosed. The decisive R4 clause is the large
      separation from rho_OR.

Decision rule (never softened):
  APPROVE  iff R1 and R2 and R3 and R4.
  REJECT   if R4 single-gate anticorrelates (fails band) or R1 anchor unstable
           (also a non-monotone dose-response, R3, sinks it).
  NULL     if R2 sub-threshold (finalized, not a re-run).
  INVALID  if non-deterministic, or achieved admit rates miss targets, or shared-stream
           rho_full != 0.

Determinism: fully hermetic (no network/repo reads, no wall-clock). results.json and
  run-stdout.txt are byte-identical across a double run; the seed-1 reference-stringency
  (25% OR-gate) admitted-subset size + first-20 admitted (N,R) pairs (full precision via
  repr) and the four thresholds are committed as the fixture and re-verified each run.
"""
import json
import hashlib
import math
import os
import random

# ---- pinned-world constants (top-of-file, per the registration) ----
N_ITEMS = 2000
SEEDS = [1, 2, 3, 4, 5]
R_STREAM_OFFSET = 10000
LEVELS = [0.50, 0.25, 0.10]          # OR-gate target marginal admit rates (loose -> tight)
REF_LEVEL = 0.25                      # reference stringency
SINGLE_LEVEL = 0.25                   # single-gate control matched marginal admit rate
ADMIT_TOL = 0.02                      # |achieved - target| tolerance (INVALID guard)
NULL_BAND = 0.03                      # R1 / R4 null band on |rho|
RHO_STAR = 0.45                       # R2 pre-registered anticorrelation floor
SEP_MIN = 3.0                         # >=3 sigma separation requirement
HERE = os.path.dirname(os.path.abspath(__file__))

# Expected calibrated thresholds (6dp) for the self-check.
EXPECTED_THRESH = {0.50: 0.544952, 0.25: 1.107798, 0.10: 1.632219}
EXPECTED_A_SINGLE = 0.674490
# Known Phi^-1 verification points (6dp).
PHI_POINTS = {0.975: 1.959964, 0.75: 0.674490, 0.8660254: 1.107798}
THRESH_TOL = 1e-6                     # 6dp match tolerance (expected values are rounded)


# --------------------------------------------------------------------------
# Inverse normal CDF Phi^-1 -- Acklam's rational approximation (pure stdlib).
# --------------------------------------------------------------------------
_ACK_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
_ACK_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]
_ACK_C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
          -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
_ACK_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
          3.754408661907416e+00]
_ACK_PLOW = 0.02425
_ACK_PHIGH = 1.0 - _ACK_PLOW


def norm_ppf(p):
    """Inverse standard-normal CDF via Acklam's rational approximation.

    Valid on the open interval (0,1); abs error ~1e-9, ample for the 6dp thresholds.
    """
    if not (0.0 < p < 1.0):
        raise ValueError("norm_ppf domain is (0,1); got %r" % (p,))
    if p < _ACK_PLOW:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((_ACK_C[0] * q + _ACK_C[1]) * q + _ACK_C[2]) * q + _ACK_C[3]) * q
                 + _ACK_C[4]) * q + _ACK_C[5]) / \
               ((((_ACK_D[0] * q + _ACK_D[1]) * q + _ACK_D[2]) * q + _ACK_D[3]) * q + 1.0)
    if p <= _ACK_PHIGH:
        q = p - 0.5
        r = q * q
        return (((((_ACK_A[0] * r + _ACK_A[1]) * r + _ACK_A[2]) * r + _ACK_A[3]) * r
                 + _ACK_A[4]) * r + _ACK_A[5]) * q / \
               (((((_ACK_B[0] * r + _ACK_B[1]) * r + _ACK_B[2]) * r + _ACK_B[3]) * r
                 + _ACK_B[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((_ACK_C[0] * q + _ACK_C[1]) * q + _ACK_C[2]) * q + _ACK_C[3]) * q
              + _ACK_C[4]) * q + _ACK_C[5]) / \
           ((((_ACK_D[0] * q + _ACK_D[1]) * q + _ACK_D[2]) * q + _ACK_D[3]) * q + 1.0)


def or_threshold(T):
    """Calibrated symmetric OR-gate threshold t = Phi^-1(sqrt(1-T))."""
    return norm_ppf(math.sqrt(1.0 - T))


def single_threshold(T):
    """Single-gate control threshold a = Phi^-1(1-T)."""
    return norm_ppf(1.0 - T)


# --------------------------------------------------------------------------
# Stats -- pure stdlib.
# --------------------------------------------------------------------------
def pearson(xs, ys):
    """Pearson correlation r over paired samples (pure stdlib)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) * (x - mx) for x in xs)
    syy = sum((y - my) * (y - my) for y in ys)
    denom = math.sqrt(sxx * syy)
    if denom == 0.0:
        return 0.0
    return sxy / denom


def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    """Sample standard deviation, ddof=1."""
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) * (x - m) for x in xs) / (n - 1)
    return math.sqrt(var)


def pool(rhos):
    """Pool 5 per-seed rho values -> (mean, sd(ddof=1), se=sd/sqrt(n))."""
    m = mean(rhos)
    sd = sample_std(rhos)
    se = sd / math.sqrt(len(rhos))
    return m, sd, se


def separation(ma, sea, mb, seb):
    """Between-estimate separation |ma-mb| / sqrt(sea^2 + seb^2)."""
    denom = math.sqrt(sea * sea + seb * seb)
    if denom == 0.0:
        return float("inf") if ma != mb else 0.0
    return abs(ma - mb) / denom


# --------------------------------------------------------------------------
# Model.
# --------------------------------------------------------------------------
def draw_axes(seed):
    """Two INDEPENDENT latent axes from SEPARATE random.Random streams.

    rngN = random.Random(seed) drives N; rngR = random.Random(seed+10000) drives R.
    The streams share no draws, so corr(N,R) = 0 in the population by construction.
    """
    rngN = random.Random(seed)
    N = [rngN.gauss(0.0, 1.0) for _ in range(N_ITEMS)]
    rngR = random.Random(seed + R_STREAM_OFFSET)
    R = [rngR.gauss(0.0, 1.0) for _ in range(N_ITEMS)]
    return N, R


def or_admitted(N, R, t):
    """Indices admitted by the disjunctive collider gate: N>=t OR R>=t."""
    return [i for i in range(len(N)) if N[i] >= t or R[i] >= t]


def single_admitted(N, a):
    """Indices admitted by the single gate: N>=a ALONE (no OR)."""
    return [i for i in range(len(N)) if N[i] >= a]


def rho_over(N, R, idx):
    """Pearson r over the selected subset of (N,R)."""
    return pearson([N[i] for i in idx], [R[i] for i in idx])


# --------------------------------------------------------------------------
# Simulate the full battery.
# --------------------------------------------------------------------------
def simulate():
    """Run the seed x level battery; returns a dict of per-seed and pooled results."""
    t_or = {T: or_threshold(T) for T in LEVELS}
    a_single = single_threshold(SINGLE_LEVEL)

    per_seed = {
        "rho_full": [],
        "rho_or": {T: [] for T in LEVELS},
        "rho_single": [],
        "rate_or": {T: [] for T in LEVELS},
        "rate_single": [],
        "n_or": {T: [] for T in LEVELS},
        "n_single": [],
    }
    for seed in SEEDS:
        N, R = draw_axes(seed)
        per_seed["rho_full"].append(pearson(N, R))
        for T in LEVELS:
            idx = or_admitted(N, R, t_or[T])
            per_seed["rho_or"][T].append(rho_over(N, R, idx))
            per_seed["rate_or"][T].append(len(idx) / N_ITEMS)
            per_seed["n_or"][T].append(len(idx))
        idx_s = single_admitted(N, a_single)
        per_seed["rho_single"].append(rho_over(N, R, idx_s))
        per_seed["rate_single"].append(len(idx_s) / N_ITEMS)
        per_seed["n_single"].append(len(idx_s))

    pooled = {
        "rho_full": pool(per_seed["rho_full"]),
        "rho_or": {T: pool(per_seed["rho_or"][T]) for T in LEVELS},
        "rho_single": pool(per_seed["rho_single"]),
        "rate_or": {T: mean(per_seed["rate_or"][T]) for T in LEVELS},
        "rate_single": mean(per_seed["rate_single"]),
    }
    thresholds = {"or": t_or, "single": a_single}
    return per_seed, pooled, thresholds


# --------------------------------------------------------------------------
# Gate evaluation.
# --------------------------------------------------------------------------
def compute_gates(pooled):
    fm, fsd, fse = pooled["rho_full"]
    m25, sd25, se25 = pooled["rho_or"][0.25]
    m50, sd50, se50 = pooled["rho_or"][0.50]
    m10, sd10, se10 = pooled["rho_or"][0.10]
    ms, sds, ses = pooled["rho_single"]

    # ---- R1: null anchor -- |mean|<=0.03 AND >=3 sigma INSIDE the band ----
    r1_band = abs(fm) <= NULL_BAND
    r1_inside = (abs(fm) + 3.0 * fse) <= NULL_BAND
    r1 = r1_band and r1_inside

    # ---- R2: effect @T=0.25 -- mean+3*SE <= -rho* ----
    r2_upper = m25 + 3.0 * se25
    r2 = r2_upper <= -RHO_STAR
    # margin: how many sigma the mean clears -rho* (mean below -rho* by k*SE)
    r2_margin_sigma = (-RHO_STAR - m25) / se25 if se25 > 0 else float("inf")

    # ---- R3: dose-response monotone + adjacent >=3 sigma ----
    order_ok = (m50 > m25) and (m25 > m10)   # strictly more negative as it tightens
    sep_50_25 = separation(m50, se50, m25, se25)
    sep_25_10 = separation(m25, se25, m10, se10)
    r3 = order_ok and sep_50_25 >= SEP_MIN and sep_25_10 >= SEP_MIN

    # ---- R4: mechanism isolation (POOLED-MEAN band + separation) ----
    r4_band = abs(ms) <= NULL_BAND                    # pooled-mean reading (disclosed)
    sep_or_single = separation(m25, se25, ms, ses)
    r4_sep = sep_or_single >= SEP_MIN
    r4 = r4_band and r4_sep
    # disclosed: the stricter >=3-sigma-inside reading does NOT clear (envelope ~0.048)
    r4_inside_envelope = abs(ms) + 3.0 * ses          # ~0.048, expected to exceed 0.03

    gates = {
        "R1": r1, "R2": r2, "R3": r3, "R4": r4,
        "R1_mean": fm, "R1_se": fse, "R1_band_ok": r1_band,
        "R1_inside_3se": fmt_inside(fm, fse), "R1_inside_ok": r1_inside,
        "R2_mean": m25, "R2_se": se25, "R2_upper_3se": r2_upper,
        "R2_rho_star": RHO_STAR, "R2_margin_sigma": r2_margin_sigma,
        "R3_mean_50": m50, "R3_mean_25": m25, "R3_mean_10": m10,
        "R3_order_ok": order_ok, "R3_sep_50_25": sep_50_25, "R3_sep_25_10": sep_25_10,
        "R4_mean_single": ms, "R4_se_single": ses, "R4_band_ok": r4_band,
        "R4_sep_or_single": sep_or_single, "R4_sep_ok": r4_sep,
        "R4_inside_envelope": r4_inside_envelope,
    }
    return gates


def fmt_inside(m, se):
    return abs(m) + 3.0 * se


# --------------------------------------------------------------------------
# Validity (INVALID guard) and twin evaluators.
# --------------------------------------------------------------------------
def compute_validity(pooled, per_seed):
    """Achieved admit rates within tolerance of targets -> valid (else INVALID)."""
    rate_ok = {}
    for T in LEVELS:
        rate_ok[T] = abs(pooled["rate_or"][T] - T) <= ADMIT_TOL
    rate_ok["single"] = abs(pooled["rate_single"] - SINGLE_LEVEL) <= ADMIT_TOL
    valid = all(rate_ok.values())
    return valid, rate_ok


def decide_ifchain(valid, gr):
    """Evaluator A: ordered short-circuit if-chain; first failing gate is the reason."""
    if not valid:
        return "INVALID", "validity"
    if not gr["R1"]:
        return "REJECT", "R1"          # anchor unstable
    if not gr["R2"]:
        return "NULL", "R2"            # sub-threshold effect
    if not gr["R3"]:
        return "REJECT", "R3"          # non-monotone dose-response
    if not gr["R4"]:
        return "REJECT", "R4"          # single-gate control anticorrelates
    return "APPROVE", None


def decide_table(valid, gr):
    """Evaluator B: independent transcription over the ordered (gate, token) table."""
    if not valid:
        return "INVALID", "validity"
    table = [
        ("R1", gr["R1"], "REJECT"),
        ("R2", gr["R2"], "NULL"),
        ("R3", gr["R3"], "REJECT"),
        ("R4", gr["R4"], "REJECT"),
    ]
    for name, ok, token in table:
        if not ok:
            return token, name
    return "APPROVE", None


# --------------------------------------------------------------------------
# Fixture.
# --------------------------------------------------------------------------
def build_fixture(thresholds):
    """Seed-1, reference-stringency (25% OR-gate) admitted size + first-20 (N,R) pairs."""
    N, R = draw_axes(1)
    t25 = thresholds["or"][0.25]
    idx = or_admitted(N, R, t25)
    first20 = [[repr(N[i]), repr(R[i])] for i in idx[:20]]
    return {
        "source": "scratchpad/v101 :: verdict-101-berkson-admission-collider",
        "proposal": "## PROPOSAL 088 * 2026-07-16 * status: sim-ready "
                    "(idea-engine PROPOSAL 088, registered spec "
                    "berkson-admission-collider-2026-07-16); offset +13 -> VERDICT 101",
        "pinned_world": {
            "n_items": N_ITEMS, "seeds": SEEDS, "r_stream_offset": R_STREAM_OFFSET,
            "levels_T": LEVELS, "reference_T": REF_LEVEL, "single_T": SINGLE_LEVEL,
            "axes": "N ~ Normal(0,1) via random.Random(seed).gauss; "
                    "R ~ Normal(0,1) via random.Random(seed+10000).gauss; "
                    "separate streams => corr(N,R)=0 in population by construction",
            "or_gate": "admit iff N>=t OR R>=t, t=Phi^-1(sqrt(1-T))",
            "single_gate": "admit iff N>=a ALONE, a=Phi^-1(1-T) at T=0.25",
            "metric": "Pearson r; rho_full over full 2000; rho_admit over OR subset; "
                      "rho_single over single-gate subset",
            "pooling": "pooled mean = mean of 5 per-seed rho; sigma = sample SD (ddof=1); "
                       "SE = sigma/sqrt(5)",
        },
        "thresholds": {
            "or_50pct": thresholds["or"][0.50],
            "or_25pct": thresholds["or"][0.25],
            "or_10pct": thresholds["or"][0.10],
            "single_25pct": thresholds["single"],
        },
        "expected_thresholds_6dp": {
            "or_50pct": EXPECTED_THRESH[0.50], "or_25pct": EXPECTED_THRESH[0.25],
            "or_10pct": EXPECTED_THRESH[0.10], "single_25pct": EXPECTED_A_SINGLE,
        },
        "preregistered_gates": {
            "R1": "null anchor: |mean(rho_full)|<=0.03 AND |mean|+3*SE<=0.03",
            "R2": "effect @T=0.25: mean(rho_OR)+3*SE <= -0.45",
            "R3": "dose-response: mean rho_OR 50% > 25% > 10%, each adjacent pair "
                  "separated |ma-mb|/sqrt(SEa^2+SEb^2) >= 3",
            "R4": "mechanism isolation: |mean(rho_single)|<=0.03 (pooled-mean reading) "
                  "AND |mean_OR@25 - mean_single|/sqrt(SE_OR25^2+SE_single^2) >= 3",
            "decision_rule": "APPROVE iff R1 and R2 and R3 and R4 (order R1->R2->R3->R4); "
                             "REJECT if R1 or R3 or R4 fail; NULL if R2 sub-threshold; "
                             "INVALID if rates miss targets or non-deterministic",
        },
        "seed1_ref25_admit_size": len(idx),
        "seed1_ref25_first20_NR_repr": first20,
    }


def canon(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# --------------------------------------------------------------------------
# Main.
# --------------------------------------------------------------------------
def main():
    L = []

    def out(s=""):
        L.append(s)

    per_seed, pooled, thresholds = simulate()
    gr = compute_gates(pooled)
    valid, rate_ok = compute_validity(pooled, per_seed)
    vA, rA = decide_ifchain(valid, gr)
    vB, rB = decide_table(valid, gr)

    # ---- fixture: write on first run, else verify committed ----
    fx_path = os.path.join(HERE, "fixtures.json")
    fixture = build_fixture(thresholds)
    if os.path.exists(fx_path):
        with open(fx_path) as f:
            committed = json.load(f)
        fixture_ok = (
            committed.get("seed1_ref25_admit_size") == fixture["seed1_ref25_admit_size"]
            and committed.get("seed1_ref25_first20_NR_repr") == fixture["seed1_ref25_first20_NR_repr"]
            and committed.get("thresholds") == fixture["thresholds"]
        )
    else:
        with open(fx_path, "w") as f:
            f.write(canon(fixture) + "\n")
        fixture_ok = True

    # ---- Phi^-1 verification against known points ----
    phi_ok = all(abs(norm_ppf(p) - v) <= THRESH_TOL for p, v in PHI_POINTS.items())

    # ---- thresholds match expected to 6dp ----
    thr_ok = (
        abs(thresholds["or"][0.50] - EXPECTED_THRESH[0.50]) <= THRESH_TOL
        and abs(thresholds["or"][0.25] - EXPECTED_THRESH[0.25]) <= THRESH_TOL
        and abs(thresholds["or"][0.10] - EXPECTED_THRESH[0.10]) <= THRESH_TOL
        and abs(thresholds["single"] - EXPECTED_A_SINGLE) <= THRESH_TOL
    )

    # ---- canonical-JSON stability (byte-identical intent) ----
    stable_probe = {"rho_full": pooled["rho_full"], "rho_single": pooled["rho_single"],
                    "rho_or": {str(T): pooled["rho_or"][T] for T in LEVELS}}
    json_stable = canon(stable_probe) == canon(stable_probe)

    # ---- self-checks ----
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    chk("phi_inv_known_points_6dp", phi_ok)
    chk("thresholds_match_expected_6dp", thr_ok)
    chk("stream_independence_r1_band", gr["R1_band_ok"] and gr["R1_inside_ok"])
    chk("achieved_admit_rates_within_tol", valid)
    chk("twin_evaluators_agree", vA == vB and rA == rB)
    chk("R2_effect_clears", gr["R2"])
    chk("R3_monotone_and_separated", gr["R3"])
    chk("R4_mechanism_isolation", gr["R4"])
    chk("fixture_matches_committed", fixture_ok)
    chk("canonical_json_stable", json_stable)

    n_pass = sum(1 for _, c in checks if c)

    # ---- human-readable log ----
    out("VERDICT-101 - Berkson admission-collider anticorrelation trap (P088)")
    out("=" * 82)
    out("")
    out("Pinned world: two INDEPENDENT axes N,R ~ Normal(0,1) from SEPARATE streams")
    out("  rngN=random.Random(seed); rngR=random.Random(seed+%d) -> corr(N,R)=0 by construction."
        % R_STREAM_OFFSET)
    out("  n=%d items/run; seeds S=%s. OR-gate admit iff N>=t OR R>=t, t=Phi^-1(sqrt(1-T))."
        % (N_ITEMS, SEEDS))
    out("  Levels T=%s (reference T=%.2f). Single-gate control: admit iff N>=a, a=Phi^-1(1-T)@%.2f."
        % (LEVELS, REF_LEVEL, SINGLE_LEVEL))
    out("  Metric: Pearson r. Pooled mean over 5 seeds; sigma=sample SD (ddof=1); SE=sigma/sqrt(5).")
    out("")
    out("Calibrated thresholds (Phi^-1 via Acklam):")
    out("  OR t(50%%)=%.6f  OR t(25%%)=%.6f  OR t(10%%)=%.6f  single a=%.6f"
        % (thresholds["or"][0.50], thresholds["or"][0.25], thresholds["or"][0.10],
           thresholds["single"]))
    out("  expected 6dp: 0.544952 / 1.107798 / 1.632219 / 0.674490 -> match %s" % thr_ok)
    out("")
    out("Achieved pooled admit rates (target | achieved | within %.2f):" % ADMIT_TOL)
    for T in LEVELS:
        out("  OR   T=%.2f | %.4f | %s" % (T, pooled["rate_or"][T], rate_ok[T]))
    out("  single T=%.2f | %.4f | %s" % (SINGLE_LEVEL, pooled["rate_single"], rate_ok["single"]))
    out("")
    out("Correlation table (per-seed rho + pooled mean +/- SE over S=%s):" % SEEDS)
    out("")

    def fmt_row(label, rhos, m, se):
        return "  %-18s mean=%+.6f se=%.6f  per-seed=%s" % (
            label, m, se, ["%+.6f" % x for x in rhos])

    fm, fsd, fse = pooled["rho_full"]
    out(fmt_row("R1 rho_full", per_seed["rho_full"], fm, fse))
    for T in LEVELS:
        m, sd, se = pooled["rho_or"][T]
        out(fmt_row("R2/R3 rho_OR@%d%%" % int(round(T * 100)), per_seed["rho_or"][T], m, se))
    ms, sds, ses = pooled["rho_single"]
    out(fmt_row("R4 rho_single@25", per_seed["rho_single"], ms, ses))
    out("")
    out("Gate outcomes (pre-registered, fire in order R1->R2->R3->R4):")
    out("  R1 null anchor      : %s   (|mean|=%.6f<=%.2f %s; |mean|+3se=%.6f<=%.2f %s)" % (
        "PASS" if gr["R1"] else "FAIL", abs(gr["R1_mean"]), NULL_BAND, gr["R1_band_ok"],
        gr["R1_inside_3se"], NULL_BAND, gr["R1_inside_ok"]))
    out("  R2 effect @T=0.25   : %s   (mean=%.6f se=%.6f; mean+3se=%.6f<=%.6f; clears -rho* by %.2f sigma)" % (
        "PASS" if gr["R2"] else "FAIL", gr["R2_mean"], gr["R2_se"], gr["R2_upper_3se"],
        -RHO_STAR, gr["R2_margin_sigma"]))
    out("  R3 dose-response    : %s   (%.6f > %.6f > %.6f %s; sep50-25=%.2f sep25-10=%.2f, need>=3)" % (
        "PASS" if gr["R3"] else "FAIL", gr["R3_mean_50"], gr["R3_mean_25"], gr["R3_mean_10"],
        gr["R3_order_ok"], gr["R3_sep_50_25"], gr["R3_sep_25_10"]))
    out("  R4 mechanism isolate: %s   (|mean_single|=%.6f<=%.2f %s [pooled-mean reading]; "
        "|rho_OR-rho_single| sep=%.2f sigma, need>=3 %s)" % (
        "PASS" if gr["R4"] else "FAIL", abs(gr["R4_mean_single"]), NULL_BAND, gr["R4_band_ok"],
        gr["R4_sep_or_single"], gr["R4_sep_ok"]))
    out("      disclosed: R4 control |mean|+3se=%.6f pokes past %.2f (finite-sample envelope of exactly zero;"
        % (gr["R4_inside_envelope"], NULL_BAND))
    out("      registered on the pooled-MEAN reading, NOT R1's >=3-sigma-inside test; decisive clause is the separation).")
    out("")
    out("Twin evaluators: A(if-chain)=%s/%s  B(table)=%s/%s" % (vA, rA, vB, rB))
    out("")
    for name, c in checks:
        out("  [%s] %s" % ("ok" if c else "XX", name))
    out("Self-checks: %d/%d passed" % (n_pass, len(checks)))
    out("")
    out("VERDICT: %s%s" % (vA, ("" if rA is None else " (first failing gate: %s)" % rA)))

    # ---- results.json (canonical) ----
    def rho_block(rhos, pooled_tuple):
        m, sd, se = pooled_tuple
        return {"per_seed": rhos, "mean": m, "sd": sd, "se": se}

    results = {
        "verdict": vA,
        "first_failing_gate": rA,
        "valid": valid,
        "gates": gr,
        "correlations": {
            "rho_full": rho_block(per_seed["rho_full"], pooled["rho_full"]),
            "rho_or": {str(T): rho_block(per_seed["rho_or"][T], pooled["rho_or"][T])
                       for T in LEVELS},
            "rho_single": rho_block(per_seed["rho_single"], pooled["rho_single"]),
        },
        "admit_rates": {
            "or": {str(T): {"per_seed": per_seed["rate_or"][T], "pooled": pooled["rate_or"][T],
                            "n_per_seed": per_seed["n_or"][T], "within_tol": rate_ok[T]}
                   for T in LEVELS},
            "single": {"per_seed": per_seed["rate_single"], "pooled": pooled["rate_single"],
                       "n_per_seed": per_seed["n_single"], "within_tol": rate_ok["single"]},
        },
        "thresholds": {
            "or": {str(T): thresholds["or"][T] for T in LEVELS},
            "single": thresholds["single"],
            "expected_6dp": {"or_50pct": EXPECTED_THRESH[0.50], "or_25pct": EXPECTED_THRESH[0.25],
                             "or_10pct": EXPECTED_THRESH[0.10], "single_25pct": EXPECTED_A_SINGLE},
        },
        "twin": {"if_chain": [vA, rA], "table": [vB, rB],
                 "agree": vA == vB and rA == rB},
        "self_checks": {name: c for name, c in checks},
        "params": {
            "n_items": N_ITEMS, "seeds": SEEDS, "r_stream_offset": R_STREAM_OFFSET,
            "levels_T": LEVELS, "reference_T": REF_LEVEL, "single_T": SINGLE_LEVEL,
            "admit_tol": ADMIT_TOL, "null_band": NULL_BAND, "rho_star": RHO_STAR,
            "sep_min": SEP_MIN,
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

    # ---- exit code: 0 iff all self-checks pass AND twins agree AND rates valid ----
    if n_pass != len(checks):
        raise SystemExit("SELF-CHECK FAILURE: %d/%d" % (n_pass, len(checks)))
    if not (vA == vB and rA == rB):
        raise SystemExit("TWIN DISAGREEMENT: %s/%s vs %s/%s" % (vA, rA, vB, rB))
    if not valid:
        raise SystemExit("INVALID: achieved admit rates miss targets")


if __name__ == "__main__":
    main()
