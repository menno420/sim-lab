#!/usr/bin/env python3
"""PROPOSAL 151 - St. Petersburg cap-collapse (round-35 GAME slot).

PHENOMENON (one line)
    A doubling "press-your-luck" jackpot - flip a fair coin, the pot doubles on
    heads and you bank it on the first tails - has INFINITE expected value, yet
    once the house caps the payout at 2^M coins its fair ticket price collapses
    to exactly M/2 + 1 coins. The price grows only LOGARITHMICALLY in the cap:
    doubling the bankroll (M -> M+1) adds half a coin, not double the price.

FOLK BELIEF
    "Infinite expected value means the ticket is priceless - charge whatever you
    want, or, as a player, pay anything." False. A realistic payout ceiling
    truncates the divergent tail: the fair price is a handful of coins, and it
    is almost entirely INSENSITIVE to the cap (log, not linear). Pricing the
    jackpot as a fixed fraction of the maximum payout overcharges by orders of
    magnitude; pricing it by an uncapped Monte-Carlo average never converges.

GAME-DESIGN THESIS (reasoned to fuller form - Q-0254 duty)
    Any "double-or-bank" gamble feature inherits the St. Petersburg divergence:
    its uncapped expected value is infinite, so a designer CANNOT price the
    entry cost or the pity/insurance payout from an average - the sample mean of
    playtest runs grows without bound as more runs are added and is dominated by
    a few rare mega-jackpots. The only stable price is the closed form of the
    CAPPED game, EV_cap = (1 - p)*M + 1 along the critical curve p*r = 1, where
    the cap is r^M and p is the continue probability. That price is set by the
    number of BITS of bankroll, not by the headline jackpot - so a feature
    advertising "unlimited winnings" is worth ~M/2 coins, and buying a bigger
    max jackpot barely moves it. Price the cap, not the fantasy.

FORMAL MODEL (committed constants)
    Continue with prob p (pot *= r), bank on the first stop (prob 1 - p).
    Payout after k continues is r^k; the house caps it at r^M, so realized
    payout = r^min(k, M). Uncapped EV = (1-p) * sum_k (p*r)^k diverges iff
    p*r >= 1. The CAPPED closed form is
        EV_cap(p, r, M) = (1-p) * ((p*r)^M - 1)/(p*r - 1) + (p*r)^M ,
      which on the critical curve p*r = 1 reduces to (1 - p)*M + 1.
    Classic fair doubling p = 1/2, r = 2 (p*r = 1) gives EV_cap = M/2 + 1.
    Monte-Carlo means confirm the closed form and expose the scaling law.

PRE-REGISTERED GATES (APPROVE iff ALL hold, in order G1 -> G2 -> G3)
    G1 finite_price_collapse: at the nominal cap 2^M (M=12, cap=4096), the MC
        fair price is a small FINITE number and is >= 3 sigma BELOW half the
        maximum payout (cap/2 = 2048) - the infinite-EV jackpot is worth a
        handful of coins. (Disclosed anchor: MC mean matches M/2+1 = 7.)
    G2 sublinear_scaling: raising the cap from 2^6 to 2^12 raises the fair price
        by only ~3 coins (the +1/2-per-bit log rule), which is >= 3 sigma BELOW
        the increment a cap-PROPORTIONAL intuition predicts (price scaling with
        the jackpot would add ~252). Doubling the max jackpot does not double
        the price. (Disclosed anchor: measured increment matches the log rule.)
    G3 robust_under_shifted_coin: under a SHIFTED distribution - a biased coin
        p=0.4 with multiplier r=2.5 held on the same critical curve p*r=1 - the
        capped fair price stays finite and matches the GENERALIZED closed form
        (1-p)*M + 1 within 3 sigma, with the log-rule slope tracking (1-p)=0.6
        rather than 0.5. The finite-log-price phenomenon is not special to fair
        doubling.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY, P127+ compact-canonical twist:
    the results dict carries NO digest field; main() rounds every float to 6 dp,
    hashes the compact-canonical (sorted-keys, comma/colon-separated) JSON, and
    prints an indent=2 pretty dump then a `Results-JSON sha256:` line. In-process
    double-run must produce identical digests (determinism assert). No JSON is
    written to disk. Reference: en.wikipedia.org/wiki/St._Petersburg_paradox.
"""
import math
import json
import hashlib
import random

SEED = 20260717

P_CONT = 0.5
R = 2.0
CAP_BITS_NOMINAL = 12
SLOPE_BITS = [6, 8, 10, 12]
N_SAMPLES = 400000
SIGMA_GATE = 3.0

P_CONT_SHIFT = 0.4
R_SHIFT = 2.5
CAP_BITS_SHIFT = 10


def closed_form_ev(p_cont, r, m):
    pr = p_cont * r
    one_minus_p = 1.0 - p_cont
    if abs(pr - 1.0) < 1e-9:
        return one_minus_p * m + 1.0
    return one_minus_p * ((pr ** m - 1.0) / (pr - 1.0)) + pr ** m


def sample_payout(rng, p_cont, r, m):
    k = 0
    while rng.random() < p_cont:
        k += 1
        if k >= m:
            return r ** m
    return r ** k


def mc_mean(rng, p_cont, r, m, n):
    s = 0.0
    s2 = 0.0
    for _ in range(n):
        x = sample_payout(rng, p_cont, r, m)
        s += x
        s2 += x * x
    mean = s / n
    var = (s2 - n * mean * mean) / (n - 1)
    se = math.sqrt(var / n)
    return mean, se


def run():
    rng = random.Random(SEED)
    res = {}
    res["params"] = {
        "seed": SEED,
        "p_cont": P_CONT,
        "r": R,
        "cap_bits_nominal": CAP_BITS_NOMINAL,
        "slope_bits": SLOPE_BITS,
        "n_samples": N_SAMPLES,
        "sigma_gate": SIGMA_GATE,
        "p_cont_shift": P_CONT_SHIFT,
        "r_shift": R_SHIFT,
        "cap_bits_shift": CAP_BITS_SHIFT,
    }

    by_cap = {}
    for m in SLOPE_BITS:
        mean, se = mc_mean(rng, P_CONT, R, m, N_SAMPLES)
        cf = closed_form_ev(P_CONT, R, m)
        by_cap["m_%d" % m] = {
            "cap": R ** m,
            "mc_mean": mean,
            "se": se,
            "closed_form": cf,
            "z_anchor": (mean - cf) / se,
        }
    res["classic_by_cap"] = by_cap

    nom = by_cap["m_%d" % CAP_BITS_NOMINAL]
    cap_nom = R ** CAP_BITS_NOMINAL
    z_g1 = (cap_nom / 2.0 - nom["mc_mean"]) / nom["se"]
    g1 = (z_g1 >= SIGMA_GATE) and math.isfinite(nom["mc_mean"])
    res["g1_finite_price_collapse"] = {
        "cap": cap_nom,
        "half_cap": cap_nom / 2.0,
        "mc_fair_price": nom["mc_mean"],
        "closed_form": nom["closed_form"],
        "z": z_g1,
        "pass": g1,
    }

    m_lo = SLOPE_BITS[0]
    m_hi = SLOPE_BITS[-1]
    lo = by_cap["m_%d" % m_lo]
    hi = by_cap["m_%d" % m_hi]
    delta = hi["mc_mean"] - lo["mc_mean"]
    se_delta = math.sqrt(hi["se"] ** 2 + lo["se"] ** 2)
    delta_logrule = closed_form_ev(P_CONT, R, m_hi) - closed_form_ev(P_CONT, R, m_lo)
    delta_prop = lo["mc_mean"] * (R ** m_hi / R ** m_lo - 1.0)
    z_sublinear = (delta_prop - delta) / se_delta
    z_logrule = (delta - delta_logrule) / se_delta
    g2 = (z_sublinear >= SIGMA_GATE) and (abs(z_logrule) <= SIGMA_GATE) and (delta > 0.0)
    res["g2_sublinear_scaling"] = {
        "m_lo": m_lo,
        "m_hi": m_hi,
        "delta_measured": delta,
        "se_delta": se_delta,
        "delta_logrule_pred": delta_logrule,
        "delta_cap_proportional_pred": delta_prop,
        "z_sublinear": z_sublinear,
        "z_logrule_anchor": z_logrule,
        "pass": g2,
    }

    mean_s, se_s = mc_mean(rng, P_CONT_SHIFT, R_SHIFT, CAP_BITS_SHIFT, N_SAMPLES)
    cf_s = closed_form_ev(P_CONT_SHIFT, R_SHIFT, CAP_BITS_SHIFT)
    z_s = (mean_s - cf_s) / se_s
    cap_s = R_SHIFT ** CAP_BITS_SHIFT
    g3 = (abs(z_s) <= SIGMA_GATE) and math.isfinite(mean_s) and (mean_s < cap_s)
    res["g3_robust_shifted"] = {
        "p_cont": P_CONT_SHIFT,
        "r": R_SHIFT,
        "cap_bits": CAP_BITS_SHIFT,
        "cap": cap_s,
        "mc_fair_price": mean_s,
        "se": se_s,
        "closed_form": cf_s,
        "slope_per_bit_pred": 1.0 - P_CONT_SHIFT,
        "z_anchor": z_s,
        "pass": g3,
    }

    gates = [
        {"id": "G1", "name": "finite_price_collapse", "pass": g1, "z": z_g1},
        {"id": "G2", "name": "sublinear_scaling", "pass": g2, "z": z_sublinear},
        {"id": "G3", "name": "robust_under_shifted_coin", "pass": g3, "z": z_s},
    ]
    res["gates"] = gates
    res["all_pass"] = all(x["pass"] for x in gates)
    res["first_failing_gate"] = next((x["id"] for x in gates if not x["pass"]), None)
    return res


def round_floats(o, ndigits=6):
    if isinstance(o, float):
        return round(o, ndigits)
    if isinstance(o, dict):
        return {k: round_floats(v, ndigits) for k, v in o.items()}
    if isinstance(o, list):
        return [round_floats(v, ndigits) for v in o]
    return o


def canonical_sha256(res):
    blob = json.dumps(round_floats(res, 6), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    res1 = run()
    res2 = run()
    h1 = canonical_sha256(res1)
    h2 = canonical_sha256(res2)
    assert h1 == h2, "non-deterministic: in-process double-run digests differ"
    print(json.dumps(round_floats(res1, 6), indent=2, sort_keys=True))
    print("Results-JSON sha256: " + h1)
    raise SystemExit(0 if res1["all_pass"] else 1)


if __name__ == "__main__":
    main()
