#!/usr/bin/env python3
"""PROPOSAL 186 — follow-on reserve starvation (round-44 VENTURE slot).

Head: under a power-law venture portfolio a fund that HOLDS BACK a reserve
fraction to defend its pro-rata ownership in the eventual winners earns a higher
fund MOIC than a "spray-and-pray" fund that deploys everything into initial
checks and lets every follow-on round dilute it. Value is concentrated in a few
winners; multiplicative dilution taxes exactly those winners; so the un-defended
fund's MOIC is capped precisely where the return lives. Under-reserving does not
diversify away risk -- it starves the only positions that matter.

The mechanism holds only when the reserve you forgo on the initial check is
cheaper than the dilution you avoid on a defended winner, i.e. when
    (1 - RESERVE_FRAC) > (1 - DILUTION_PER_ROUND) ** FOLLOW_ROUNDS.
Pinned so 0.5 > 0.7**4 = 0.2401: reserve wins big on defended winners and loses
only a small, un-diluted-anyway slice on the (near-worthless) losers.

Grounded in the standard VC reserve / pro-rata-defense practice: a fund reserves
a large fraction of committed capital to buy its pro-rata in the later rounds of
its winners, because power-law outcomes concentrate return in a few names.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ twist) -- the
compact-canonical results dict's own sha256 IS the digest; the dict carries no
self-referential field; stdout is the pretty (indent=2, sort_keys) dump followed
by the digest line; nothing is written to disk.

Stdlib only. Deterministic: one local random.Random(SEED). Common random
numbers: within a market the reserve and spray funds see the SAME per-company
exit draws, so ΔMOIC is a clean paired difference (only the capital-allocation
policy differs). compute() runs twice in-process and the two dicts are asserted
identical.
"""
import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 50_000
Z_GATE = 3.0
CONCENTRATION_GATE = 0.75      # G2/G3: top-decile share of the paired edge

# ---- pinned world (committed constants) -----------------------------------
N_COMPANIES = 30
FUND = 100.0                   # committed capital ($M)
INITIAL_OWN = 0.10             # O0: ownership a full-fund initial check buys
EXIT_SCALE = 200.0             # exit value ($M) = EXIT_SCALE * paretovariate
RESERVE_FRAC = 0.50            # reserve fund holds back 50% for follow-ons
POWER_ALPHA = 1.6              # base Pareto exit-multiple tail (real concentration)
COLD_ALPHA = 1.4              # G3 robustness: steeper (fatter-winner) tail
DILUTION_PER_ROUND = 0.30      # un-defended ownership loss per follow-on round
FOLLOW_ROUNDS = 4              # follow-on rounds a held position is diluted over
WINNER_DECILE = 0.10           # top-decile = the winners
K_DEFEND = int(round(N_COMPANIES * WINNER_DECILE))   # defended count = 3
SIGNAL_NOISE = 0.4             # noise (log-space) on the interim winner signal

DILUTION_FACTOR = (1.0 - DILUTION_PER_ROUND) ** FOLLOW_ROUNDS   # 0.2401
# per-company edge coefficient (paired reserve - spray), factored:
_C = INITIAL_OWN * EXIT_SCALE / FUND
_DEF_COEF = _C * ((1.0 - RESERVE_FRAC) - DILUTION_FACTOR)       # defended: > 0
_UNDEF_COEF = -_C * DILUTION_FACTOR * RESERVE_FRAC              # un-defended: < 0


def _mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var)


def _z_gt0(xs):
    """One-sample z that E[xs] exceeds 0."""
    m, sd = _mean_sd(xs)
    se = sd / math.sqrt(len(xs)) if sd > 0 else 0.0
    z = m / se if se > 0 else float("inf")
    return m, sd, z


def _market(rng, alpha):
    """One market of TRIALS funds. Fresh draws off the shared stream.

    Within a fund both strategies see the same exit draws (common random
    numbers); only the capital policy differs. Returns the mean fund MOIC of
    each strategy, the paired ΔMOIC stats, and the top-decile edge share.
    """
    deltas = []
    spray_moics = []
    reserve_moics = []
    all_v = []
    all_edge = []
    for _ in range(TRIALS):
        v = [rng.paretovariate(alpha) for _ in range(N_COMPANIES)]
        # noisy interim signal, correlated with true exit value
        signal = [math.log(v[i]) + SIGNAL_NOISE * rng.gauss(0.0, 1.0)
                  for i in range(N_COMPANIES)]
        order = sorted(range(N_COMPANIES), key=lambda i: signal[i], reverse=True)
        defended = set(order[:K_DEFEND])

        sum_all = 0.0
        sum_def = 0.0
        for i in range(N_COMPANIES):
            vi = v[i]
            sum_all += vi
            if i in defended:
                sum_def += vi
                edge = _DEF_COEF * vi
            else:
                edge = _UNDEF_COEF * vi
            all_v.append(vi)
            all_edge.append(edge)
        sum_undef = sum_all - sum_def

        # spray MOIC = INITIAL_OWN*EXIT_SCALE*(1-d)^R*sum_all / FUND
        spray = INITIAL_OWN * EXIT_SCALE * DILUTION_FACTOR * sum_all / FUND
        reserve = ((1.0 - RESERVE_FRAC) * INITIAL_OWN * EXIT_SCALE
                   * (sum_def + DILUTION_FACTOR * sum_undef) / FUND)
        spray_moics.append(spray)
        reserve_moics.append(reserve)
        deltas.append(reserve - spray)

    # concentration: share of the gross positive paired edge captured by the
    # top-decile companies ranked by realised exit value.
    idx = sorted(range(len(all_v)), key=lambda j: all_v[j], reverse=True)
    top_n = int(round(WINNER_DECILE * len(all_v)))
    top_edge = 0.0
    for j in idx[:top_n]:
        top_edge += all_edge[j]
    pos_edge = sum(e for e in all_edge if e > 0.0)
    share = top_edge / pos_edge if pos_edge != 0 else 0.0

    d_mean, d_sd, d_z = _z_gt0(deltas)
    return {
        "spray_mean_moic": sum(spray_moics) / len(spray_moics),
        "reserve_mean_moic": sum(reserve_moics) / len(reserve_moics),
        "delta_mean": d_mean,
        "delta_std": d_sd,
        "delta_z": d_z,
        "topdecile_edge_share": share,
    }


def compute():
    rng = random.Random(SEED)
    base = _market(rng, POWER_ALPHA)      # base market
    cold = _market(rng, COLD_ALPHA)       # G3 robustness, fresh draws

    g1 = (base["delta_mean"] > 0.0) and (base["delta_z"] >= Z_GATE)
    g2 = base["topdecile_edge_share"] >= CONCENTRATION_GATE
    g3 = ((cold["delta_mean"] > 0.0) and (cold["delta_z"] >= Z_GATE)
          and (cold["topdecile_edge_share"] >= CONCENTRATION_GATE))
    all_pass = g1 and g2 and g3

    return {
        "proposal": 186,
        "head": ("follow-on reserve starvation: under a power-law portfolio a "
                 "fund reserving ~half its capital to defend pro-rata in the "
                 "winners out-MOICs a spray-and-pray fund, and the edge "
                 "concentrates in the defended top-decile winners"),
        "seed": SEED,
        "trials": TRIALS,
        "n_companies": N_COMPANIES,
        "fund": round(FUND, 6),
        "initial_own": round(INITIAL_OWN, 6),
        "exit_scale": round(EXIT_SCALE, 6),
        "reserve_frac": round(RESERVE_FRAC, 6),
        "power_alpha": round(POWER_ALPHA, 6),
        "cold_alpha": round(COLD_ALPHA, 6),
        "dilution_per_round": round(DILUTION_PER_ROUND, 6),
        "follow_rounds": FOLLOW_ROUNDS,
        "dilution_factor": round(DILUTION_FACTOR, 6),
        "winner_decile": round(WINNER_DECILE, 6),
        "k_defend": K_DEFEND,
        "signal_noise": round(SIGNAL_NOISE, 6),
        "spray_mean_moic": round(base["spray_mean_moic"], 6),
        "reserve_mean_moic": round(base["reserve_mean_moic"], 6),
        "delta_mean": round(base["delta_mean"], 6),
        "delta_std": round(base["delta_std"], 6),
        "gate_G1_z": round(base["delta_z"], 6),
        "gate_G1_pass": g1,
        "gate_G2_topdecile_edge_share": round(base["topdecile_edge_share"], 6),
        "gate_G2_concentration_gate": round(CONCENTRATION_GATE, 6),
        "gate_G2_pass": g2,
        "gate_G3_cold_spray_mean_moic": round(cold["spray_mean_moic"], 6),
        "gate_G3_cold_reserve_mean_moic": round(cold["reserve_mean_moic"], 6),
        "gate_G3_cold_delta_mean": round(cold["delta_mean"], 6),
        "gate_G3_cold_z": round(cold["delta_z"], 6),
        "gate_G3_cold_topdecile_edge_share": round(cold["topdecile_edge_share"], 6),
        "gate_G3_pass": g3,
        "all_pass": all_pass,
    }


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert r1 == r2, "non-deterministic: in-process double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256 " + digest)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
