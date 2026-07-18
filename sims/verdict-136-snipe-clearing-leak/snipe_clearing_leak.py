#!/usr/bin/env python3
"""snipe_clearing_leak.py — reference simulation for PROPOSAL 123.

Hard-close auction sniping leaks competitive clearing value relative to a
soft-close (anti-snipe extension) auction, and the leak scales with the
late-bid transmission-failure rate q. Stdlib-only (random, math, json, hashlib).

Anchor: Roth & Ockenfels, "Last-Minute Bidding and the Rules for Ending
Second-Price Auctions", American Economic Review 92(4), 2002.

Model (paired, common random numbers):
  - K bidders, private valuations iid Uniform(0,1).
  - Soft close (anti-snipe / ascending English): the extension timer lets the
    full field respond, so price = second-highest of ALL K valuations, v_(2).
  - Hard close (sniping): each bidder submits one last-instant sealed bid that
    transmits with prob (1-q) (late-bid / server-tick failure rate = q).
    Second-price payment over the TRANSMITTED subset: winner pays the
    second-highest transmitted valuation, or 0 (reserve) if <2 transmit.
  - Leak (per auction) = P_soft - P_hard >= 0.

Gates (APPROVE iff G1 AND G2 AND G3, in order):
  G1 existence    : at q*=Q_STAR, mean leak > 0 with z = mean/se >= SIGMA_GATE.
  G2 dose-response: leak(Q_HI) - leak(Q_LO) > 0 with z >= SIGMA_GATE
                    (paired: common transmission draws => coupled, low-variance).
  G3 specificity  : at q=0 the two rules coincide; per-auction leak is EXACTLY
                    0 for every trial (max|leak| == 0.0) — the effect vanishes
                    when the friction is removed.
"""
import random, math, json, hashlib

SEED = 20260717
TRIALS = 100_000
K = 8
SIGMA_GATE = 3.0
Q_STAR = 0.15
Q_LO = 0.05
Q_HI = 0.25
Q_LEVELS = [0.0, Q_LO, Q_STAR, Q_HI]  # 0.0 first = placebo/specificity


def second_highest(vals):
    a = b = -1.0
    for x in vals:
        if x > a:
            b = a
            a = x
        elif x > b:
            b = x
    return b


def run():
    rng = random.Random(SEED)
    sum_leak = {q: 0.0 for q in Q_LEVELS}
    sumsq_leak = {q: 0.0 for q in Q_LEVELS}
    max_abs_placebo = 0.0
    sum_soft = 0.0
    sum_dose = 0.0
    sumsq_dose = 0.0

    for _ in range(TRIALS):
        vals = [rng.random() for _ in range(K)]
        tprob = [rng.random() for _ in range(K)]
        p_soft = second_highest(vals)
        sum_soft += p_soft
        leak_lo = leak_hi = 0.0
        for q in Q_LEVELS:
            transmitted = [vals[i] for i in range(K) if tprob[i] >= q]
            p_hard = second_highest(transmitted) if len(transmitted) >= 2 else 0.0
            leak = p_soft - p_hard
            sum_leak[q] += leak
            sumsq_leak[q] += leak * leak
            if q == 0.0 and abs(leak) > max_abs_placebo:
                max_abs_placebo = abs(leak)
            if q == Q_LO:
                leak_lo = leak
            if q == Q_HI:
                leak_hi = leak
        d = leak_hi - leak_lo
        sum_dose += d
        sumsq_dose += d * d

    n = TRIALS

    def mean_se_z(s, ss):
        mean = s / n
        var = max(ss / n - mean * mean, 0.0)
        se = math.sqrt(var / n)
        z = mean / se if se > 0 else 0.0
        return mean, se, z

    e_soft = sum_soft / n
    leak_star_mean, _, z_g1 = mean_se_z(sum_leak[Q_STAR], sumsq_leak[Q_STAR])
    dose_mean, _, z_g2 = mean_se_z(sum_dose, sumsq_dose)
    leak_lo_mean = sum_leak[Q_LO] / n
    leak_hi_mean = sum_leak[Q_HI] / n

    def theory_e_hard(q):
        p = 1.0 - q
        tot = 0.0
        for m in range(2, K + 1):
            pm = math.comb(K, m) * (p ** m) * (q ** (K - m))
            tot += pm * (m - 1) / (m + 1)
        return tot

    e_hard_theory_star = theory_e_hard(Q_STAR)
    e_hard_sim_star = e_soft - leak_star_mean
    theory_abs_err = abs(e_hard_sim_star - e_hard_theory_star)

    g1 = (leak_star_mean > 0.0) and (z_g1 >= SIGMA_GATE)
    g2 = (dose_mean > 0.0) and (z_g2 >= SIGMA_GATE)
    g3 = (max_abs_placebo == 0.0)
    all_pass = g1 and g2 and g3

    return {
        "seed": SEED,
        "trials": TRIALS,
        "K": K,
        "sigma_gate": SIGMA_GATE,
        "q_levels": Q_LEVELS,
        "e_soft": round(e_soft, 8),
        "e_soft_theory": round((K - 1) / (K + 1), 8),
        "leak_lo_mean": round(leak_lo_mean, 8),
        "leak_star_mean": round(leak_star_mean, 8),
        "leak_hi_mean": round(leak_hi_mean, 8),
        "leak_star_pct_of_clearing": round(100.0 * leak_star_mean / e_soft, 6),
        "z_g1_existence": round(z_g1, 4),
        "dose_mean": round(dose_mean, 8),
        "z_g2_dose_response": round(z_g2, 4),
        "max_abs_placebo_leak": round(max_abs_placebo, 12),
        "e_hard_sim_star": round(e_hard_sim_star, 8),
        "e_hard_theory_star": round(e_hard_theory_star, 8),
        "theory_abs_err": round(theory_abs_err, 8),
        "g1_existence": g1,
        "g2_dose_response": g2,
        "g3_specificity": g3,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print("G1 existence     :", "PASS" if results["g1_existence"] else "FAIL", "z=%.4f" % results["z_g1_existence"])
    print("G2 dose-response :", "PASS" if results["g2_dose_response"] else "FAIL", "z=%.4f" % results["z_g2_dose_response"])
    print("G3 specificity   :", "PASS" if results["g3_specificity"] else "FAIL", "max|placebo|=%.3e" % results["max_abs_placebo_leak"])
    print("ALL_PASS         :", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
