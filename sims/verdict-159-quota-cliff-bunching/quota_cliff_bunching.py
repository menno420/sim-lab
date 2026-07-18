#!/usr/bin/env python3
"""PROPOSAL 146 — venture slot (round-34) — sim-lab verifier.

Claim: a sales-comp ACCELERATOR with a CLIFF at 100% quota (marginal deals pay
a base rate below quota, an accelerated rate above) makes reps rationally
RE-TIME deals across the period boundary. A rep just UNDER quota near period
end PULLS FORWARD deals from next period to clear the cliff; a rep comfortably
OVER quota PUSHES BACK ("sandbags") marginal deals into next period to bank
toward next period's cliff. Both are individually rational.

Even when TRUE per-rep per-period demand is i.i.d. across periods (no real
quarter-to-quarter dependence), the OBSERVED (relocated) bookings exhibit three
artifacts absent from the TRUE counterfactual:
  G1 BUNCHING — excess mass in the [Q, Q(1+eps)] attainment band.
  G2 SPURIOUS NEGATIVE lag-1 autocorrelation of team-total bookings (a hot
     period borrows from the next), while the true series' autocorr ~ 0.
  G3 CONSERVATION + ROBUSTNESS — total horizon bookings are conserved
     (relocation moves timing, it does not create/destroy demand, proving the
     effect is a comp-plan ARTIFACT not real volatility), AND the G1/G2 effects
     survive under a SECOND true-demand distribution.

A naive analyst reading OBSERVED bookings concludes "our demand is volatile and
mean-reverting" and "the plan is well-calibrated — most reps land right at
quota"; both are cliff artifacts.

stdlib only (hashlib, json, math, random). Deterministic: one random.Random(SEED)
drawn in a single fixed-order stream. Digest posture: WHOLE-DICT /
NO-SELF-FIELD / STDOUT-ONLY (the results dict carries NO sha field; the compact
canonical sha256 is the digest; stdout dumps the pretty indent=2 form — the
P127+ TWIST). Every float in the results dict rounded to 6 decimals.
"""

import hashlib
import json
import math
import random

SEED = 20260717            # fleet-pinned

# ---- pinned world (committed constants; sim-lab must reproduce exactly) ----
N_REPS = 50                # reps on the team
N_PERIODS = 8              # selling periods over the horizon (e.g. quarters)
QUOTA = 12.0               # per-rep per-period quota (bookings units)
DEALS_PER = 12             # Dist A: fixed deal count per rep-period (mean amt 1)
PULL_WINDOW = 0.20         # rep with attainment in [1-PULL_WINDOW, 1) pulls fwd
OVER_THRESH = 0.20         # rep with attainment >= 1+OVER_THRESH banks accel
ACCEL_BANK_CAP = 0.50      # max extra (in quota units) an over-rep pulls forward
BAND_EPS = 0.10            # bunching band = attainment in [1, 1+BAND_EPS]
M_TRIALS = 800             # paired Monte-Carlo trials per distribution
SIGMA = 3.0                # gate threshold (sigma)
FP = 1e-9                  # float guard for band membership

DIST_A = "exponential_amount"   # DEALS_PER deals, amount ~ Exp(mean 1.0)
DIST_B = "poisson_count_unit"   # deal count ~ Poisson(DEALS_PER), unit amounts


# ---------- true-demand generators (per rep-period deal-amount lists) ----------
def draw_period_A(rng):
    """DEALS_PER deals, each amount ~ Exponential(mean 1.0)."""
    return [rng.expovariate(1.0) for _ in range(DEALS_PER)]


def _poisson(rng, lam):
    """Knuth Poisson sampler on the shared stream."""
    el = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= el:
            return k - 1


def draw_period_B(rng):
    """Poisson(DEALS_PER) unit deals (count randomness, fixed amount 1.0)."""
    n = _poisson(rng, float(DEALS_PER))
    return [1.0] * n


def draw_true(rng, dist):
    """A rep x period grid of true deal lists (i.i.d. across periods)."""
    gen = draw_period_A if dist == DIST_A else draw_period_B
    return [[gen(rng) for _ in range(N_PERIODS)] for _ in range(N_REPS)]


# ---------- deterministic rational relocation (the cliff response) ----------
def relocate(true_grid):
    """Apply the per-rep rational re-timing rule; return the observed grid.

    Both re-timings are PULL-FORWARD across the period boundary — deals move to
    the earlier period — because the comp plan is a pure above-quota ACCELERATOR
    (marginal deals below quota pay the base rate, above quota the accelerated
    rate). Each rep independently, processing periods left-to-right (causal):
      - JUST UNDER quota (attainment in [1-PULL_WINDOW, 1)): pull deals forward
        from the next period, smallest-first, until bookings reach quota (or the
        next period runs dry). Clears the cliff with minimal pulled volume, so
        the rep lands just at/above quota -> the BUNCHING band.
      - COMFORTABLY OVER quota (attainment >= 1+OVER_THRESH): the rep has cleared
        the cliff, so every additional deal now pays the ACCELERATED rate; it is
        rational to pull forward more of next period's deals (largest-first, up
        to ACCEL_BANK_CAP quota-units) and book them at the accelerated rate NOW.
        This is "a hot period borrows from the next" -> depletes the next period.
    Relocation only moves deals between EXISTING adjacent periods, so total
    horizon demand per rep is conserved exactly (no leak past the last period).
    """
    obs = [[list(true_grid[r][t]) for t in range(N_PERIODS)] for r in range(N_REPS)]
    for r in range(N_REPS):
        for t in range(N_PERIODS):
            if t + 1 >= N_PERIODS:
                continue  # no neighbour to trade with; horizon-conserving
            cur = obs[r][t]
            nxt = obs[r][t + 1]
            b = sum(cur)
            if b < QUOTA * (1.0 - FP) and b >= QUOTA * (1.0 - PULL_WINDOW):
                # clear the cliff: pull smallest-first from next until >= quota
                order = sorted(range(len(nxt)), key=lambda i: nxt[i])
                for i in order:
                    if b >= QUOTA * (1.0 - FP):
                        break
                    b += nxt[i]
                    cur.append(nxt[i])
                    nxt[i] = None
                obs[r][t + 1] = [d for d in nxt if d is not None]
            elif b >= QUOTA * (1.0 + OVER_THRESH):
                # bank the accelerator: pull largest-first from next up to the cap
                cap = QUOTA * ACCEL_BANK_CAP
                order = sorted(range(len(nxt)), key=lambda i: -nxt[i])
                pulled = 0.0
                for i in order:
                    if pulled >= cap:
                        break
                    cur.append(nxt[i])
                    pulled += nxt[i]
                    nxt[i] = None
                obs[r][t + 1] = [d for d in nxt if d is not None]
    return obs


# ---------- per-world statistics ----------
def band_count(grid):
    """Number of rep-periods whose attainment lands in [1, 1+BAND_EPS]."""
    c = 0
    for r in range(N_REPS):
        for t in range(N_PERIODS):
            a = sum(grid[r][t]) / QUOTA
            if a >= 1.0 - FP and a <= 1.0 + BAND_EPS + FP:
                c += 1
    return c


def team_totals(grid):
    """Team-total bookings per period (length N_PERIODS)."""
    return [sum(sum(grid[r][t]) for r in range(N_REPS)) for t in range(N_PERIODS)]


def lag1_autocorr(series):
    n = len(series)
    mean = sum(series) / n
    denom = sum((x - mean) ** 2 for x in series)
    if denom <= 0.0:
        return 0.0
    num = sum((series[t] - mean) * (series[t + 1] - mean) for t in range(n - 1))
    return num / denom


def horizon_total(grid):
    return sum(sum(sum(grid[r][t]) for t in range(N_PERIODS)) for r in range(N_REPS))


def zstat(diffs):
    """Paired Monte-Carlo difference z: mean / (stdev / sqrt(M))."""
    m = len(diffs)
    mean = sum(diffs) / m
    if m < 2:
        return mean, 0.0, 0.0
    var = sum((d - mean) ** 2 for d in diffs) / (m - 1)
    se = math.sqrt(var) / math.sqrt(m)
    z = mean / se if se > 0 else 0.0
    return mean, se, z


# ---------- one distribution's M-trial paired run ----------
def run_distribution(rng, dist):
    band_diffs = []          # observed_band - true_band  (per trial)
    ac_diffs = []            # observed_ac  - true_ac      (per trial)
    cons_rel = []            # |obs_total - true_total| / true_total
    obs_band_tot = 0
    true_band_tot = 0
    obs_ac_sum = 0.0
    true_ac_sum = 0.0
    for _ in range(M_TRIALS):
        true_grid = draw_true(rng, dist)
        obs_grid = relocate(true_grid)

        tb = band_count(true_grid)
        ob = band_count(obs_grid)
        band_diffs.append(ob - tb)
        true_band_tot += tb
        obs_band_tot += ob

        t_ac = lag1_autocorr(team_totals(true_grid))
        o_ac = lag1_autocorr(team_totals(obs_grid))
        ac_diffs.append(o_ac - t_ac)
        true_ac_sum += t_ac
        obs_ac_sum += o_ac

        tt = horizon_total(true_grid)
        ot = horizon_total(obs_grid)
        cons_rel.append(abs(ot - tt) / tt if tt > 0 else 0.0)

    band_mean, band_se, band_z = zstat(band_diffs)
    ac_mean, ac_se, ac_z = zstat(ac_diffs)
    return {
        "band_diff_mean": band_mean,
        "band_diff_se": band_se,
        "band_z": band_z,
        "obs_band_mean": obs_band_tot / M_TRIALS,
        "true_band_mean": true_band_tot / M_TRIALS,
        "ac_diff_mean": ac_mean,
        "ac_diff_se": ac_se,
        "ac_z": ac_z,
        "obs_ac_mean": obs_ac_sum / M_TRIALS,
        "true_ac_mean": true_ac_sum / M_TRIALS,
        "conservation_max_rel": max(cons_rel),
    }


def run():
    rng = random.Random(SEED)          # ONE stream, fixed order: Dist A then B
    a = run_distribution(rng, DIST_A)
    b = run_distribution(rng, DIST_B)

    # G1 BUNCHING (primary = Dist A): observed band excess, z >= 3 (one-sided).
    g1_pass = a["band_z"] >= SIGMA
    # G2 SPURIOUS NEGATIVE AUTOCORR (primary = Dist A): observed more negative
    # than counterfactual -> ac_diff_mean < 0, magnitude z >= 3 (one-sided).
    g2_pass = (a["ac_diff_mean"] < 0.0) and (abs(a["ac_z"]) >= SIGMA)
    # G3 CONSERVATION + ROBUSTNESS: horizon demand conserved in BOTH worlds
    # (artifact, not real), AND the G1/G2 effect survives under Dist B >= 3 sigma.
    CONS_TOL = 1e-6
    cons_ok = (a["conservation_max_rel"] <= CONS_TOL) and (b["conservation_max_rel"] <= CONS_TOL)
    robust_ok = (b["band_z"] >= SIGMA) and (b["ac_diff_mean"] < 0.0) and (abs(b["ac_z"]) >= SIGMA)
    g3_pass = cons_ok and robust_ok

    all_pass = g1_pass and g2_pass and g3_pass
    first_fail = None
    if not g1_pass:
        first_fail = "G1_bunching"
    elif not g2_pass:
        first_fail = "G2_spurious_neg_autocorr"
    elif not g3_pass:
        first_fail = "G3_conservation_robustness"

    def rnd(x):
        return round(x, 6)

    results = {
        "proposal": 146,
        "domain": "venture",
        "slot": "round-34 venture",
        "seed": SEED,
        "claim": "a 100%-quota comp cliff relocates deals across the period "
                 "boundary, so observed bookings show bunching + spurious "
                 "negative autocorrelation while demand is conserved (artifact "
                 "not real volatility)",
        "params": {
            "n_reps": N_REPS,
            "n_periods": N_PERIODS,
            "quota": QUOTA,
            "deals_per": DEALS_PER,
            "pull_window": PULL_WINDOW,
            "over_thresh": OVER_THRESH,
            "accel_bank_cap": ACCEL_BANK_CAP,
            "band_eps": BAND_EPS,
            "m_trials": M_TRIALS,
            "sigma": SIGMA,
            "conservation_tol": 1e-6,
            "dist_primary": DIST_A,
            "dist_alternate": DIST_B,
        },
        "dist_A": {
            "name": DIST_A,
            "band_diff_mean": rnd(a["band_diff_mean"]),
            "band_diff_se": rnd(a["band_diff_se"]),
            "band_z": rnd(a["band_z"]),
            "obs_band_mean": rnd(a["obs_band_mean"]),
            "true_band_mean": rnd(a["true_band_mean"]),
            "ac_diff_mean": rnd(a["ac_diff_mean"]),
            "ac_diff_se": rnd(a["ac_diff_se"]),
            "ac_z": rnd(a["ac_z"]),
            "obs_ac_mean": rnd(a["obs_ac_mean"]),
            "true_ac_mean": rnd(a["true_ac_mean"]),
            "conservation_max_rel": rnd(a["conservation_max_rel"]),
        },
        "dist_B": {
            "name": DIST_B,
            "band_diff_mean": rnd(b["band_diff_mean"]),
            "band_diff_se": rnd(b["band_diff_se"]),
            "band_z": rnd(b["band_z"]),
            "obs_band_mean": rnd(b["obs_band_mean"]),
            "true_band_mean": rnd(b["true_band_mean"]),
            "ac_diff_mean": rnd(b["ac_diff_mean"]),
            "ac_diff_se": rnd(b["ac_diff_se"]),
            "ac_z": rnd(b["ac_z"]),
            "obs_ac_mean": rnd(b["obs_ac_mean"]),
            "true_ac_mean": rnd(b["true_ac_mean"]),
            "conservation_max_rel": rnd(b["conservation_max_rel"]),
        },
        "gates": {
            "G1_bunching": {"z": rnd(a["band_z"]), "threshold_sigma": SIGMA,
                            "one_sided": True, "pass": bool(g1_pass)},
            "G2_spurious_neg_autocorr": {"z": rnd(a["ac_z"]), "threshold_sigma": SIGMA,
                                         "one_sided": True, "pass": bool(g2_pass)},
            "G3_conservation_robustness": {
                "conservation_max_rel_A": rnd(a["conservation_max_rel"]),
                "conservation_max_rel_B": rnd(b["conservation_max_rel"]),
                "robust_band_z_B": rnd(b["band_z"]),
                "robust_ac_z_B": rnd(b["ac_z"]),
                "threshold_sigma": SIGMA,
                "pass": bool(g3_pass),
            },
        },
        "first_failing_gate": first_fail,
        "all_pass": bool(all_pass),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    g = results["gates"]
    print("GATES: G1 z=%.3f pass=%s | G2 z=%.3f pass=%s | G3 pass=%s" % (
        g["G1_bunching"]["z"], g["G1_bunching"]["pass"],
        g["G2_spurious_neg_autocorr"]["z"], g["G2_spurious_neg_autocorr"]["pass"],
        g["G3_conservation_robustness"]["pass"]))
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
