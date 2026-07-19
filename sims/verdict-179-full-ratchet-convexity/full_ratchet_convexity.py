"""
Full-ratchet anti-dilution turns a down round into a convex transfer of
ownership from common (founders/employees) to the ratcheted investor, and
always exceeds the broad-based weighted-average outcome.

PROPOSAL 166 · round-39 VENTURE slot · targets sim-lab VERDICT 179 (+13)

PHENOMENON
  A down round issues new stock at price P_new = p * P_old, p in (0,1),
  d = 1 - p the drop. A prior preferred investor's anti-dilution resets their
  conversion price:
    full ratchet:             CP = P_new            -> as-converted shares *= 1/p
    broad-based weighted-avg: CP = P_old*(A+B)/(A+C)
        A = fully-diluted shares before the new issue
        B = money / P_old  (shares the money would buy at the old price)
        C = money / P_new  (shares actually issued)
  Extra as-converted shares handed to the investor:
    dAD = N_A * (P_old/CP - 1).
  For a full ratchet dAD_FR = N_A*(1/p - 1) = N_A*d/(1-d), convex in d.
  Founder ownership loss vs a no-anti-dilution baseline:
    loss = N_C/T - N_C/(T + dAD),  T = A0 + N_B.

FOLK BELIEF
  "Anti-dilution is anti-dilution; a d-percent down round costs founders about
   d-percent." Two errors: the ratchet formula is not a detail (full ratchet is
   strictly worse than weighted-average), and the share transfer is convex in
   the drop, not proportional -- doubling the drop more than doubles it.

PRE-REGISTERED GATES (order G1 -> G2 -> G3; APPROVE iff ALL hold, z_gate=3.0)
  G1  full-ratchet founder loss exceeds broad-based weighted-average founder
      loss on the same scenarios (paired mean diff > 0), z >= 3.
  G2  convexity of the ratchet share transfer: dAD_FR(2d) - 2*dAD_FR(d) > 0
      (super-linear), z >= 3 -> the proportional folk belief is rejected.
  G3  both G1 and G2 hold in a shifted world (heavier preferred stake, larger
      raise, deeper drops).
  Non-gated honesty disclosure: the ownership-FRACTION second difference
  nongated_fraction_convexity_mean is reported un-gated -- it is dampened by
  new-money issuance inflating the base and is NOT globally positive, so the
  convexity claim is scoped to the share transfer, not the fraction.

DIGEST POSTURE
  WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. Canonical (sort_keys, tight
  separators) JSON of the ordered results dict is hashed; its own sha256 is the
  digest, printed after a pretty indent=2 dump. Floats rounded to 6 dp. No
  self-referential digest field, no on-disk JSON.
"""

import hashlib
import json
import math
import random
import statistics

SEED = 20260717
Z_GATE = 3.0
N_SAMPLES = 4000
P_OLD = 1.0
A0 = 1.0  # pre-round fully-diluted cap, normalized


def r6(x):
    return round(float(x), 6)


def mean_se(xs):
    n = len(xs)
    mu = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    se = sd / math.sqrt(n)
    return mu, se


def zscore(mu, se):
    if se == 0.0:
        return math.inf if mu > 0.0 else (-math.inf if mu < 0.0 else 0.0)
    return mu / se


def extra_shares_full_ratchet(n_a, p):
    return n_a * (1.0 / p - 1.0)


def extra_shares_weighted_avg(n_a, money, p):
    b = money / P_OLD
    c = money / (P_OLD * p)
    cp = P_OLD * (A0 + b) / (A0 + c)
    return n_a * (P_OLD / cp - 1.0)


def founder_loss(n_c, n_b, d_ad):
    t = A0 + n_b
    return n_c / t - n_c / (t + d_ad)


def draw(rng, shifted):
    if shifted:
        pref = rng.uniform(0.30, 0.50)
        d = rng.uniform(0.15, 0.30)
        money = rng.uniform(0.40, 0.80)
    else:
        pref = rng.uniform(0.15, 0.35)
        d = rng.uniform(0.08, 0.24)
        money = rng.uniform(0.20, 0.50)
    n_a = pref * A0
    n_c = A0 - n_a
    return n_a, n_c, money, d


def world(rng, shifted):
    g1, g2, fconv = [], [], []
    for _ in range(N_SAMPLES):
        n_a, n_c, money, d = draw(rng, shifted)
        p = 1.0 - d
        n_b = money / p
        dad_fr = extra_shares_full_ratchet(n_a, p)
        dad_wa = extra_shares_weighted_avg(n_a, money, p)
        loss_fr = founder_loss(n_c, n_b, dad_fr)
        loss_wa = founder_loss(n_c, n_b, dad_wa)
        g1.append(loss_fr - loss_wa)

        p2 = 1.0 - 2.0 * d
        dad_fr2 = extra_shares_full_ratchet(n_a, p2)
        g2.append(dad_fr2 - 2.0 * dad_fr)

        n_b2 = money / p2
        loss_fr2 = founder_loss(n_c, n_b2, dad_fr2)
        fconv.append(loss_fr2 - 2.0 * loss_fr)
    return g1, g2, fconv


def run():
    rng = random.Random(SEED)
    b_g1, b_g2, b_fc = world(rng, shifted=False)
    s_g1, s_g2, s_fc = world(rng, shifted=True)

    mu1, se1 = mean_se(b_g1)
    z1 = zscore(mu1, se1)
    mu2, se2 = mean_se(b_g2)
    z2 = zscore(mu2, se2)
    sm1, ss1 = mean_se(s_g1)
    sz1 = zscore(sm1, ss1)
    sm2, ss2 = mean_se(s_g2)
    sz2 = zscore(sm2, ss2)
    fc_mu, _ = mean_se(b_fc)

    n_a0, n_c0, money0, d_sh = 0.25, 0.75, 0.35, 0.02
    p_sh = 1.0 - d_sh
    n_b_sh = money0 / p_sh
    cx_fr = founder_loss(n_c0, n_b_sh, extra_shares_full_ratchet(n_a0, p_sh))
    cx_wa = founder_loss(n_c0, n_b_sh, extra_shares_weighted_avg(n_a0, money0, p_sh))

    g1_pass = z1 >= Z_GATE and mu1 > 0.0
    g2_pass = z2 >= Z_GATE and mu2 > 0.0
    g3_pass = (sz1 >= Z_GATE and sm1 > 0.0) and (sz2 >= Z_GATE and sm2 > 0.0)

    first = None
    if not g1_pass:
        first = "G1"
    elif not g2_pass:
        first = "G2"
    elif not g3_pass:
        first = "G3"

    results = {
        "mechanism": "full_ratchet_antidilution_convexity",
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_samples": N_SAMPLES,
        "G1_fr_minus_wa_loss": {"mean": r6(mu1), "se": r6(se1), "z": r6(z1), "pass": g1_pass},
        "G2_transfer_convexity": {"mean": r6(mu2), "se": r6(se2), "z": r6(z2), "pass": g2_pass},
        "G3_shifted": {
            "fr_minus_wa_loss": {"mean": r6(sm1), "se": r6(ss1), "z": r6(sz1)},
            "transfer_convexity": {"mean": r6(sm2), "se": r6(ss2), "z": r6(sz2)},
            "pass": g3_pass,
        },
        "nongated_fraction_convexity_mean": r6(fc_mu),
        "nongated_shallow_crossover": {
            "drop": r6(d_sh),
            "loss_full_ratchet": r6(cx_fr),
            "loss_weighted_avg": r6(cx_wa),
            "gap": r6(cx_fr - cx_wa),
        },
        "all_pass": bool(g1_pass and g2_pass and g3_pass),
        "first_failing_gate": first,
    }
    return results


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def digest(d):
    return hashlib.sha256(canonical(d).encode("utf-8")).hexdigest()


def main():
    a = run()
    b = run()
    assert canonical(a) == canonical(b), "non-deterministic in-process double-run"
    print(json.dumps(a, indent=2, sort_keys=True))
    print("sha256:", digest(a))
    return 0 if a["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
