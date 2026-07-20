"""PROPOSAL 189 verifier — ski-rental keep-warm break-even.

Head: for an autoscaled / keep-warm resource (serverless instance, pooled
connection) you cannot safely pick "always keep warm" or "always tear down" —
each is UNBOUNDEDLY wasteful in the wrong idle regime. The break-even rule
(keep warm exactly until accumulated idle cost equals the cold-start cost B,
then tear down) is provably within 2x of the clairvoyant optimum in EVERY
regime; averaged over exponential idle with mean = B it costs e/(e-1) ~= 1.582x.

Grounded in the ski-rental problem / competitive analysis (2-competitive
deterministic break-even; randomized e/(e-1)).

Gates (pre-registered, >=3 sigma):
  G1 long-idle  — always-warm blows up (ratio ~5.5); break-even stays <2; paired z.
  G2 short-idle — always-cold blows up (ratio ~5.0); break-even stays <2; paired z.
  G3 matched    — break-even ratio ~= e/(e-1); robust to a hyperexponential shift.

DIGEST-POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The sha256 of the
compact canonical results dict IS the digest; stdout prints the pretty dump
(indent=2) and the digest line; no on-disk JSON.
"""
import hashlib
import json
import math
import random

SEED = 20260717

# ---- pinned world ----
B = 1.0                # cold-start (spin-up) cost; rent cost = 1 per unit idle time
R = 200000             # Monte-Carlo idle draws per arm
Z_MIN = 3.0
E_OVER_EM1 = math.e / (math.e - 1.0)   # 1.5819767...

MU_SHORT = 0.2
MU_MATCH = 1.0
MU_LONG = 5.0
H2_P = 0.5             # hyperexponential (mean 1.0) mixing weight
H2_M1 = 0.2
H2_M2 = 1.8


def _costs(t):
    """Per-instance costs for idle duration t (cold-start B, rent 1/unit)."""
    opt = t if t < B else B          # min(t, B): clairvoyant
    be = t if t < B else 2.0 * B     # break-even: warm to B, else rent B + cold-start B
    warm = t                         # always keep warm
    cold = B                         # always tear down immediately -> cold start every time
    return opt, be, warm, cold


def _exp_draws(rng, mu, n):
    return [rng.expovariate(1.0 / mu) for _ in range(n)]


def _hyper_draws(rng, n):
    out = []
    for _ in range(n):
        if rng.random() < H2_P:
            out.append(rng.expovariate(1.0 / H2_M1))
        else:
            out.append(rng.expovariate(1.0 / H2_M2))
    return out


def _summarize(draws):
    n = len(draws)
    s_opt = s_be = s_warm = s_cold = 0.0
    s_wb = s_wb2 = 0.0    # warm - be
    s_cb = s_cb2 = 0.0    # cold - be
    for t in draws:
        opt, be, warm, cold = _costs(t)
        s_opt += opt
        s_be += be
        s_warm += warm
        s_cold += cold
        wb = warm - be
        cb = cold - be
        s_wb += wb
        s_wb2 += wb * wb
        s_cb += cb
        s_cb2 += cb * cb
    m_opt = s_opt / n
    m_be = s_be / n
    m_warm = s_warm / n
    m_cold = s_cold / n
    return {
        "m_opt": m_opt, "m_be": m_be, "m_warm": m_warm, "m_cold": m_cold,
        "ratio_be": m_be / m_opt, "ratio_warm": m_warm / m_opt, "ratio_cold": m_cold / m_opt,
        "wb_mean": s_wb / n, "wb_se": math.sqrt(max(s_wb2 / n - (s_wb / n) ** 2, 0.0) / n),
        "cb_mean": s_cb / n, "cb_se": math.sqrt(max(s_cb2 / n - (s_cb / n) ** 2, 0.0) / n),
    }


def run():
    rng = random.Random(SEED)
    r = lambda x: round(x, 6)

    short = _summarize(_exp_draws(rng, MU_SHORT, R))
    match = _summarize(_exp_draws(rng, MU_MATCH, R))
    long_ = _summarize(_exp_draws(rng, MU_LONG, R))
    hyper = _summarize(_hyper_draws(rng, R))

    z_g1 = long_["wb_mean"] / long_["wb_se"]
    g1_pass = bool(z_g1 >= Z_MIN and long_["ratio_be"] < 2.0 and long_["ratio_warm"] > 2.0)

    z_g2 = short["cb_mean"] / short["cb_se"]
    g2_pass = bool(z_g2 >= Z_MIN and short["ratio_be"] < 2.0 and short["ratio_cold"] > 2.0)

    rel_err_match = abs(match["ratio_be"] - E_OVER_EM1) / E_OVER_EM1
    z_g3 = hyper["cb_mean"] / hyper["cb_se"]
    g3_pass = bool(rel_err_match < 0.02 and hyper["ratio_be"] < 2.0 and z_g3 >= Z_MIN)

    all_pass = bool(g1_pass and g2_pass and g3_pass)

    return {
        "world": {"seed": SEED, "B": r(B), "R": R, "z_min": r(Z_MIN),
                  "mu_short": r(MU_SHORT), "mu_match": r(MU_MATCH), "mu_long": r(MU_LONG),
                  "e_over_e_minus_1": r(E_OVER_EM1)},
        "g1_long_idle_warm_blowup": {
            "ratio_be": r(long_["ratio_be"]), "ratio_warm": r(long_["ratio_warm"]),
            "paired_warm_minus_be_mean": r(long_["wb_mean"]), "z": r(z_g1), "pass": g1_pass},
        "g2_short_idle_cold_blowup": {
            "ratio_be": r(short["ratio_be"]), "ratio_cold": r(short["ratio_cold"]),
            "paired_cold_minus_be_mean": r(short["cb_mean"]), "z": r(z_g2), "pass": g2_pass},
        "g3_matched_constant_and_shift": {
            "ratio_be_match": r(match["ratio_be"]), "e_over_e_minus_1": r(E_OVER_EM1),
            "rel_err": r(rel_err_match), "ratio_be_hyper": r(hyper["ratio_be"]),
            "z_hyper": r(z_g3), "pass": g3_pass},
        "all_pass": all_pass,
    }


def main():
    r1 = run()
    r2 = run()
    assert r1 == r2, "in-process double-run mismatch: non-deterministic"
    payload = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
