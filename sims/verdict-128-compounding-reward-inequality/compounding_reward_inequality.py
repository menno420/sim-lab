#!/usr/bin/env python3
"""
compounding_reward_inequality.py — reference verifier for PROPOSAL 115
(round-26, game slot).

The "compounding-reward inequality engine" in an in-game economy. Give every
player the SAME fair daily percentage bonus — each day your holdings change by a
random percentage g ~ Normal(MU_G, SIGMA_G) (a small positive average, no skill,
no choice, no edge) — and let it COMPOUND on the running total. After a season of
DAYS days the wealth distribution is log-normal and almost all the wealth
concentrates in a handful of players purely by compounding: identical players,
identical fair rewards, runaway inequality.

The mechanism (Gibrat 1931 / multiplicative stochastic processes): compounding an
iid daily log-return g_d makes terminal wealth

    W = W0 * prod_d exp(g_d) = W0 * exp( S ),   S = sum_d g_d.

Because the g_d are iid Normal(MU_G, SIGMA_G), the sum-of-independent-normals
identity gives S ~ Normal(DAYS*MU_G, DAYS*SIGMA_G^2) EXACTLY, so terminal wealth
is log-normal with terminal log-sd  sigma_T = SIGMA_G * sqrt(DAYS). The verifier
draws S directly per player (exactly equivalent to, and deterministic like, the
day-by-day product; no approximation). Concentration is a scale-free function of
sigma_T alone:

    Gini            = 2*Phi(sigma_T / sqrt(2)) - 1
    median / mean   = exp(-sigma_T^2 / 2)
    top-p share     = Phi(sigma_T - Phi^{-1}(1 - p))          (log-normal)

The counterintuitive core, isolated by a same-shocks control on the SAME S per
player:

  * COMPOUND regime:  W = W0 * exp(S)   -- percentages compound on the running
    total; log-normal, heavy right tail, the top decile owns most of the wealth.
  * ADDITIVE control: W = W0 * (1 + S)  -- the SAME daily percentages are paid on
    the STARTING stake and summed (they do NOT compound); terminal wealth is
    W0*(1 + Normal(DAYS*MU_G, DAYS*SIGMA_G^2)), symmetric, concentration collapses
    toward the fair share. Freezing compounding (not the randomness) removes the
    inequality -- so COMPOUNDING is the cause, not the luck.

Gates (all on the /se margin -- z on the ESTIMATED MEAN via se = std / sqrt(TRIALS),
the P104/P105/P106/P107/P108/P109/P110/P111/P112/P113/P114 convention):
  G1 concentration (headline): the COMPOUND top-decile wealth share is
     >= SHARE_MIN by >= 3 sigma (identical players, fair rewards, yet the top 10%
     own most of the wealth).
  G2 compounding-causes-it (control): the ADDITIVE top-decile share stays
     <= ADD_SHARE_MAX AND the COMPOUND-minus-ADDITIVE share gap is >= DELTA_MIN,
     both by >= 3 sigma -- freeze compounding, keep the same shocks, and the
     concentration collapses to the fair share, so it is caused by compounding.
  G3 closed-form anchor MATCH: the mean COMPOUND Gini reproduces
     2*Phi(sigma_T/sqrt(2))-1 and the mean COMPOUND top-decile share reproduces
     Phi(sigma_T - Phi^{-1}(1-TOP_FRAC)) within 3 sigma (|z| < 3).

stdlib only (random, math, json, hashlib); fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
N_PLAYERS = 5000       # identical players per season (top decile = 500)
DAYS = 200             # season length (compounding periods)
MU_G = 0.02            # mean daily log-return (a small positive "fair" bonus)
SIGMA_G = 0.10         # daily log-return sd (the percentage noise)
W0 = 100.0             # identical starting wealth
TRIALS = 200           # independent replications -> mean +/- se over TRIALS
SIGMA_GATE = 3.0       # gate threshold in sigma
TOP_FRAC = 0.10        # top decile (wealth-concentration cut)
SHARE_MIN = 0.40       # G1: min COMPOUND top-decile wealth share
ADD_SHARE_MAX = 0.20   # G2: max ADDITIVE top-decile share (fair-share ceiling)
DELTA_MIN = 0.25       # G2: min (compound share - additive share) gap


def norm_cdf(x):
    """Standard-normal CDF via the error function (stdlib math.erf)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p):
    """Standard-normal inverse CDF (Acklam's rational approximation; |err|<1e-9
    on the relevant central region). Used only for the closed-form top-share
    anchor, never inside the Monte Carlo draw."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)


def gini(sorted_asc):
    """Gini of a non-negative list already sorted ascending (n^2 mean-abs-diff
    form): G = (2*sum_i i*w_i)/(n*sum w) - (n+1)/n, i = 1..n."""
    n = len(sorted_asc)
    total = sum(sorted_asc)
    if total <= 0.0:
        return 0.0
    cum = 0.0
    for i, w in enumerate(sorted_asc, start=1):
        cum += i * w
    return (2.0 * cum) / (n * total) - (n + 1.0) / n


def top_share(sorted_asc, frac):
    """Wealth share held by the top `frac` fraction (by wealth) of the list."""
    n = len(sorted_asc)
    total = sum(sorted_asc)
    if total <= 0.0:
        return 0.0
    k = max(1, int(round(frac * n)))
    top = sum(sorted_asc[n - k:])
    return top / total


def simulate_replication(rng):
    """One season. Draw each player's cumulative daily-log-return S (the exact
    sum-of-independent-normals of DAYS iid Normal(MU_G, SIGMA_G) draws), then
    read the SAME S under the COMPOUND and the ADDITIVE regimes.

    Returns (compound_gini, compound_top_share, additive_top_share)."""
    mu_s = DAYS * MU_G
    sd_s = math.sqrt(DAYS) * SIGMA_G
    compound = []
    additive = []
    for _ in range(N_PLAYERS):
        s = rng.gauss(mu_s, sd_s)                 # S = sum_d g_d  (exact)
        compound.append(W0 * math.exp(s))         # compounds on the running total
        additive.append(max(0.0, W0 * (1.0 + s))) # same shocks, paid on the base
    compound.sort()
    additive.sort()
    return gini(compound), top_share(compound, TOP_FRAC), top_share(additive, TOP_FRAC)


def moments(values):
    """Return (mean, se) with se = sample-sd / sqrt(n) over the replications."""
    n = len(values)
    m = sum(values) / n
    var = max(sum(v * v for v in values) / n - m * m, 0.0)
    return m, math.sqrt(var / n)


def main():
    rng = random.Random(SEED)

    comp_ginis = []
    comp_shares = []
    add_shares = []
    gaps = []
    for _ in range(TRIALS):
        cg, cs, as_ = simulate_replication(rng)
        comp_ginis.append(cg)
        comp_shares.append(cs)
        add_shares.append(as_)
        gaps.append(cs - as_)

    mean_cg, se_cg = moments(comp_ginis)
    mean_cs, se_cs = moments(comp_shares)
    mean_as, se_as = moments(add_shares)
    mean_gap, se_gap = moments(gaps)

    # Closed-form log-normal anchors (scale-free in sigma_T = SIGMA_G*sqrt(DAYS)).
    sigma_t = SIGMA_G * math.sqrt(DAYS)
    gini_cf = 2.0 * norm_cdf(sigma_t / math.sqrt(2.0)) - 1.0
    share_cf = norm_cdf(sigma_t - norm_ppf(1.0 - TOP_FRAC))
    median_over_mean_cf = math.exp(-0.5 * sigma_t * sigma_t)

    # G1 -- concentration: COMPOUND top-decile share >= SHARE_MIN by >= 3 sigma.
    z_g1 = (mean_cs - SHARE_MIN) / se_cs if se_cs > 0 else float("inf")
    g1 = (z_g1 >= SIGMA_GATE) and (mean_cs >= SHARE_MIN)

    # G2 -- compounding-causes-it: ADDITIVE share low AND gap large, both >= 3 s.
    z_g2_add = (ADD_SHARE_MAX - mean_as) / se_as if se_as > 0 else float("inf")
    z_g2_gap = (mean_gap - DELTA_MIN) / se_gap if se_gap > 0 else float("inf")
    g2 = ((z_g2_add >= SIGMA_GATE) and (mean_as <= ADD_SHARE_MAX) and
          (z_g2_gap >= SIGMA_GATE) and (mean_gap >= DELTA_MIN))

    # G3 -- closed-form anchor MATCH: Gini and top-share within 3 sigma (|z|<3).
    z_g3_gini = (mean_cg - gini_cf) / se_cg if se_cg > 0 else float("inf")
    z_g3_share = (mean_cs - share_cf) / se_cs if se_cs > 0 else float("inf")
    g3 = (abs(z_g3_gini) < SIGMA_GATE) and (abs(z_g3_share) < SIGMA_GATE)

    all_pass = g1 and g2 and g3

    results = {
        "params": {
            "SEED": SEED, "N_PLAYERS": N_PLAYERS, "DAYS": DAYS,
            "MU_G": MU_G, "SIGMA_G": SIGMA_G, "W0": W0, "TRIALS": TRIALS,
            "SIGMA_GATE": SIGMA_GATE, "TOP_FRAC": TOP_FRAC,
            "SHARE_MIN": SHARE_MIN, "ADD_SHARE_MAX": ADD_SHARE_MAX,
            "DELTA_MIN": DELTA_MIN,
        },
        "anchors": {
            "sigma_T": round(sigma_t, 6),
            "gini_closed_form": round(gini_cf, 6),
            "top_share_closed_form": round(share_cf, 6),
            "median_over_mean_closed_form": round(median_over_mean_cf, 6),
        },
        "sim": {
            "compound_gini": round(mean_cg, 6), "se_compound_gini": round(se_cg, 6),
            "compound_top_share": round(mean_cs, 6), "se_compound_top_share": round(se_cs, 6),
            "additive_top_share": round(mean_as, 6), "se_additive_top_share": round(se_as, 6),
            "share_gap": round(mean_gap, 6), "se_share_gap": round(se_gap, 6),
        },
        "gates": {
            "G1_concentration": {"z": round(z_g1, 4),
                                 "compound_top_share": round(mean_cs, 6),
                                 "SHARE_MIN": SHARE_MIN, "pass": g1},
            "G2_compounding_causes_it": {"z_additive": round(z_g2_add, 4),
                                         "z_gap": round(z_g2_gap, 4),
                                         "additive_top_share": round(mean_as, 6),
                                         "share_gap": round(mean_gap, 6),
                                         "pass": g2},
            "G3_closed_form_anchor": {"z_gini": round(z_g3_gini, 4),
                                      "z_top_share": round(z_g3_share, 4),
                                      "compound_gini": round(mean_cg, 6),
                                      "gini_closed_form": round(gini_cf, 6),
                                      "compound_top_share": round(mean_cs, 6),
                                      "top_share_closed_form": round(share_cf, 6),
                                      "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("compounding_reward_inequality_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
