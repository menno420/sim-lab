#!/usr/bin/env python3
"""PROPOSAL 129 — the correlated-vote Condorcet jury ceiling (round-30 FLEET slot).

Reference verifier. Stdlib only (random, math, json, hashlib) — no numpy/scipy.

Mechanism under test
--------------------
N agents each independently correct with marginal probability p > 1/2 decide a
binary question by MAJORITY VOTE. The Condorcet Jury Theorem says: under
INDEPENDENCE the majority is correct with probability -> 1 as N -> infinity.
But real fleets share an error source (one stale upstream, one shared prior,
one correlated feature). Model that with a one-factor latent-Gaussian probit:

    X_i = sqrt(rho) * C + sqrt(1 - rho) * eps_i,   C, eps_i ~ N(0, 1) iid,

agent i votes CORRECT iff X_i > tau, with tau = Phi^{-1}(1 - p) so the marginal
P(correct) = Phi(-tau) = p for EVERY agent regardless of rho. Pairwise latent
error-correlation is rho > 0.

Conditional on the common factor C, votes are independent with per-agent correct
probability q(C) = Phi((sqrt(rho) C - tau)/sqrt(1 - rho)); by the LLN the fraction
correct -> q(C), so as N -> infinity the majority is correct iff q(C) > 1/2 iff
C > tau/sqrt(rho). Hence the majority accuracy has a CLOSED-FORM CEILING

    A_inf = P(C > tau/sqrt(rho)) = Phi(Phi^{-1}(p) / sqrt(rho))  <  1   for rho > 0,

and A_inf -> 1 only as rho -> 0 (the Condorcet limit). More voters CANNOT buy
certainty once errors are correlated: accuracy plateaus at A_inf and the crowd
saturates near N ~ 1/rho.

Design (paired common-random-numbers): each trial draws one common factor C and
N_MAX idiosyncratic eps_i; the correlated world uses X_i = sqrt(rho) C +
sqrt(1-rho) eps_i, the INDEPENDENCE CONTROL uses the SAME eps_i with the common
factor removed (rho = 0), so the two worlds share every idiosyncratic draw and
the same marginal competence p — only rho differs.

Gates (pre-registered, order G1 -> G2 -> G3; z on the /se margin, the
P104..P128 convention: z = mean / (std/sqrt(TRIALS)) for paired-diff gates,
z = (Ahat - Atheory)/sqrt(Ahat(1-Ahat)/TRIALS) for the anchor):

  G1  correlation-ceiling existence -- at the SAME large N_HI and SAME competence
      p, mean(correct_indep - correct_corr) > 0 with z >= 3: correlation opens a
      persistent accuracy gap (the ceiling/floor) that independence removes.

  G2  Condorcet-convergence control -- the SAME voters, made independent, climb:
      mean(correct_indep(N_HI) - correct_indep(N_LO)) > 0 with z >= 3, and
      A_indep(N_HI) reaches near-certainty while A_corr(N_HI) plateaus below it.
      Isolates rho (not competence p) as the cause of the ceiling.

  G3  closed-form ceiling anchor -- measured A_corr(N) matches the exact finite-N
      theory A_theory(N) = E_C[P(Bin(N, q(C)) > N/2)] across the whole grid
      (full-grid max|z| < 3), the marginal A_corr(1) = p, the correlated grid is
      monotone non-decreasing, and A_theory(N_HI) sits within tolerance of the
      ceiling A_inf = Phi(Phi^{-1}(p)/sqrt(rho)) (saturation confirmed).

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The results dict never
carries a digest field; the disclosed digest is sha256 of the COMPACT canonical
serialization json.dumps(results, sort_keys=True, separators=(",", ":")). The
pretty indent=2 dump printed to stdout is NOT the digest preimage.
"""

import hashlib
import json
import math
import random

# ---- pinned world -----------------------------------------------------------
SEED = 20260717
P_COMPETENCE = 0.60          # per-agent marginal probability of a correct vote
RHO = 0.30                   # latent common-factor error correlation
TRIALS = 120000
N_GRID = (1, 3, 5, 9, 15, 25, 51, 101, 201, 501)   # odd N -> no majority ties
N_LO = 1
N_MID = 101
N_HI = 501
SIGMA_GATE = 3.0
N_MAX = max(N_GRID)


# ---- stdlib normal helpers --------------------------------------------------
def norm_cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def norm_ppf(p):
    """Inverse standard-normal CDF (Acklam's rational approximation)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


def binom_upper_tail(N, q, kmin):
    """P(Binomial(N, q) >= kmin), summed in log space for numeric safety."""
    if q <= 0.0:
        return 1.0 if kmin <= 0 else 0.0
    if q >= 1.0:
        return 1.0 if kmin <= N else 0.0
    lq, l1q = math.log(q), math.log(1.0 - q)
    total = 0.0
    for k in range(kmin, N + 1):
        lp = (math.lgamma(N + 1) - math.lgamma(k + 1) - math.lgamma(N - k + 1)
              + k * lq + (N - k) * l1q)
        total += math.exp(lp)
    return total


def majority_accuracy_theory(N, tau, sr, s1, npts=4001, lo=-9.0, hi=9.0):
    """Exact finite-N majority accuracy A(N)=E_C[P(Bin(N,q(C))>N/2)] by trapezoid.

    q(C)=Phi((sqrt(rho) C - tau)/sqrt(1-rho)); C~N(0,1). N is odd -> majority
    means the count of correct votes >= N//2 + 1.
    """
    kmin = (N // 2) + 1
    h = (hi - lo) / (npts - 1)
    inv_sqrt_2pi = 1.0 / math.sqrt(2.0 * math.pi)
    total = 0.0
    for i in range(npts):
        c = lo + i * h
        w = math.exp(-0.5 * c * c) * inv_sqrt_2pi
        q = norm_cdf((sr * c - tau) / s1)
        val = binom_upper_tail(N, q, kmin) * w
        total += val * (0.5 if (i == 0 or i == npts - 1) else 1.0)
    return total * h


# ---- Monte-Carlo simulation -------------------------------------------------
def simulate():
    tau = norm_ppf(1.0 - P_COMPETENCE)     # correct iff X > tau ; P(X>tau)=p
    sr = math.sqrt(RHO)
    s1 = math.sqrt(1.0 - RHO)
    grid = set(N_GRID)

    rng = random.Random(SEED)
    corr_correct = {n: 0 for n in N_GRID}   # count of trials with correlated majority correct
    ind_correct = {n: 0 for n in N_GRID}    # ... independent control

    # accumulators for the paired /se gate statistics
    g1_sum = 0.0   # ind(N_HI) - corr(N_HI)
    g1_sq = 0.0
    g2_sum = 0.0   # ind(N_HI) - ind(N_LO)
    g2_sq = 0.0

    for _ in range(TRIALS):
        c = rng.gauss(0.0, 1.0)
        base = sr * c
        cc = 0   # running count of correlated correct votes
        ic = 0   # running count of independent correct votes
        corr_hi = corr_lo = ind_hi = ind_lo = 0
        for i in range(N_MAX):
            e = rng.gauss(0.0, 1.0)
            if base + s1 * e > tau:
                cc += 1
            if e > tau:            # SAME eps, common factor removed (rho = 0)
                ic += 1
            n = i + 1
            if n in grid:
                thr = (n >> 1) + 1
                cmaj = 1 if cc >= thr else 0
                imaj = 1 if ic >= thr else 0
                corr_correct[n] += cmaj
                ind_correct[n] += imaj
                if n == N_HI:
                    corr_hi, ind_hi = cmaj, imaj
                if n == N_LO:
                    ind_lo = imaj
        d1 = ind_hi - corr_hi
        g1_sum += d1
        g1_sq += d1 * d1
        d2 = ind_hi - ind_lo
        g2_sum += d2
        g2_sq += d2 * d2

    A_corr = {n: corr_correct[n] / TRIALS for n in N_GRID}
    A_ind = {n: ind_correct[n] / TRIALS for n in N_GRID}
    A_theory = {n: majority_accuracy_theory(n, tau, sr, s1) for n in N_GRID}
    A_inf = norm_cdf(norm_ppf(P_COMPETENCE) / sr)

    def zstat(mean, sq):
        var = sq / TRIALS - mean * mean
        std = math.sqrt(var) if var > 0.0 else 0.0
        se = std / math.sqrt(TRIALS)
        return (mean / se) if se > 0.0 else float("inf")

    # G1 -- correlation-ceiling existence
    g1_mean = g1_sum / TRIALS
    g1_z = zstat(g1_mean, g1_sq)
    g1_pass = (g1_mean > 0.0) and (g1_z >= SIGMA_GATE)

    # G2 -- Condorcet-convergence control
    g2_mean = g2_sum / TRIALS
    g2_z = zstat(g2_mean, g2_sq)
    g2_pass = (g2_mean > 0.0) and (g2_z >= SIGMA_GATE) and (A_ind[N_HI] > A_corr[N_HI])

    # G3 -- closed-form ceiling anchor across the whole grid
    anchor_z = {}
    for n in N_GRID:
        a = A_corr[n]
        se = math.sqrt(a * (1.0 - a) / TRIALS) if 0.0 < a < 1.0 else 0.0
        anchor_z[n] = (a - A_theory[n]) / se if se > 0.0 else 0.0
    max_abs_anchor_z = max(abs(z) for z in anchor_z.values())
    corr_vals = [A_corr[n] for n in N_GRID]
    monotone = all(corr_vals[i + 1] >= corr_vals[i] - 4.0 / math.sqrt(TRIALS)
                   for i in range(len(corr_vals) - 1))
    marginal_ok = abs(A_corr[N_LO] - P_COMPETENCE) < SIGMA_GATE * math.sqrt(
        P_COMPETENCE * (1 - P_COMPETENCE) / TRIALS)
    ceiling_saturation = abs(A_theory[N_HI] - A_inf)
    g3_pass = ((max_abs_anchor_z < SIGMA_GATE) and monotone and marginal_ok
               and (ceiling_saturation < 0.01))

    all_pass = g1_pass and g2_pass and g3_pass

    results = {
        "world": {
            "seed": SEED, "p_competence": P_COMPETENCE, "rho": RHO,
            "trials": TRIALS, "n_grid": list(N_GRID),
            "n_lo": N_LO, "n_mid": N_MID, "n_hi": N_HI, "sigma_gate": SIGMA_GATE,
        },
        "anchors": {
            "tau": tau,
            "A_inf_ceiling": A_inf,
            "residual_error_1_minus_A_inf": 1.0 - A_inf,
            "n_eff_scale_inv_rho": 1.0 / RHO,
        },
        "A_corr": {str(n): A_corr[n] for n in N_GRID},
        "A_indep": {str(n): A_ind[n] for n in N_GRID},
        "A_theory": {str(n): A_theory[n] for n in N_GRID},
        "anchor_z": {str(n): anchor_z[n] for n in N_GRID},
        "gates": {
            "G1_ceiling_existence": {
                "mean_indep_minus_corr_at_hi": g1_mean, "z": g1_z,
                "A_corr_hi": A_corr[N_HI], "A_indep_hi": A_ind[N_HI],
                "pass": g1_pass,
            },
            "G2_condorcet_control": {
                "mean_indep_hi_minus_lo": g2_mean, "z": g2_z,
                "A_indep_hi": A_ind[N_HI], "A_corr_hi_plateau": A_corr[N_HI],
                "pass": g2_pass,
            },
            "G3_ceiling_anchor": {
                "max_abs_anchor_z": max_abs_anchor_z,
                "A_corr_1": A_corr[N_LO], "marginal_ok": marginal_ok,
                "monotone": monotone,
                "A_theory_hi": A_theory[N_HI], "A_inf": A_inf,
                "ceiling_saturation_gap": ceiling_saturation,
                "pass": g3_pass,
            },
        },
        "all_pass": all_pass,
    }
    return results


def main():
    results = simulate()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
