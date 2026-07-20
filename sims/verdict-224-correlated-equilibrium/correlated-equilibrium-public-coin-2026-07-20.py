#!/usr/bin/env python3
"""
PROPOSAL 211 - A voluntary public coin beats every Nash equilibrium in Chicken.

Committed model: the game of Chicken, payoffs (row, col), actions
Dare (D) / Chicken-out (C):
    D,D = (0,0)   D,C = (7,2)   C,D = (2,7)   C,C = (6,6)

A public correlating device draws one of three cards
    (C,C), (D,C), (C,D)   each with probability 1/3
and privately *recommends* the matching move to each player. Obeying is
voluntary; nobody is bound. Claim (exactly true): obedience is a best
response for both players (the device is a correlated equilibrium), it
pays each player exactly 5, strictly above the symmetric mixed Nash
equilibrium's 14/3, and it lifts total welfare to 10 - above every Nash
equilibrium (pure = 9, mixed = 28/3).

Deterministic, Python stdlib only. SEED = 20260717.

Gates (all must hold):
  G1  exact CE validity + payoff - every obedience constraint holds under
      exact Fraction arithmetic (slacks >= 0) and the device pays (5, 5).
  G2  statistical dominance (>= 3 sigma) - Monte-Carlo realized per-player
      payoff under the device exceeds independent mixed-NE play, z >= 3.
  G3  robustness band - for mutual reward w in {5, 5.25, 5.5, 5.75, 6}
      the device stays a valid CE and strictly out-pays the mixed NE.
  G4  exactly-true agreement - closed-form CE payoff == exhaustive
      enumeration over recommendations == 5 (Fraction); per-player gap
      == 1/3 and total-welfare gap == 2/3, exact.
"""
import hashlib
import json
import math
import random
from fractions import Fraction as F

SEED = 20260717
N = 200_000

D, C = 0, 1  # Dare, Chicken-out


def payoffs(w=F(6)):
    T, R, S, P = F(7), F(w), F(2), F(0)
    return {(D, D): (P, P), (D, C): (T, S), (C, D): (S, T), (C, C): (R, R)}


DEVICE = [((C, C), F(1, 3)), ((D, C), F(1, 3)), ((C, D), F(1, 3))]


def mixed_ne(w=F(6)):
    pay = payoffs(w)
    T, R, S, P = pay[(D, C)][0], pay[(C, C)][0], pay[(C, D)][0], pay[(D, D)][0]
    q = (T - R) / (T - R + S - P)          # opponent Dares with prob q
    val = q * P + (1 - q) * T
    return q, val


def device_payoff(w=F(6)):
    pay = payoffs(w)
    row = sum(p * pay[cell][0] for cell, p in DEVICE)
    col = sum(p * pay[cell][1] for cell, p in DEVICE)
    return row, col


def device_payoff_enumerated(w=F(6)):
    pay = payoffs(w)
    row = F(0)
    col = F(0)
    for cell, p in DEVICE:                  # exhaustive over the 3 recommendations
        row += p * pay[cell][0]
        col += p * pay[cell][1]
    return row, col


def device_valid_ce(w=F(6)):
    pay = payoffs(w)
    slacks = []
    for a in (D, C):
        cards = [(cell, p) for cell, p in DEVICE if cell[0] == a]
        mass = sum(p for _, p in cards)
        if mass == 0:
            continue

        def exp_payoff(action):
            return sum((p / mass) * pay[(action, cell[1])][0] for cell, p in cards)

        obey = exp_payoff(a)
        for dev in (D, C):
            if dev != a:
                slacks.append(obey - exp_payoff(dev))  # >= 0 required
    return all(s >= 0 for s in slacks), slacks


def monte_carlo(seed, n):
    rng = random.Random(seed)
    pay = payoffs()
    cells = [cell for cell, _ in DEVICE]
    q = float(mixed_ne()[0])
    dev_m = dev_s = ne_m = ne_s = 0.0
    for i in range(1, n + 1):
        xd = float(pay[cells[rng.randrange(3)]][0])       # device: uniform 1/3 card
        a_row = D if rng.random() < q else C              # mixed NE: independent
        a_col = D if rng.random() < q else C
        xn = float(pay[(a_row, a_col)][0])
        d1 = xd - dev_m
        dev_m += d1 / i
        dev_s += d1 * (xd - dev_m)
        d2 = xn - ne_m
        ne_m += d2 / i
        ne_s += d2 * (xn - ne_m)
    var_dev = dev_s / (n - 1)
    var_ne = ne_s / (n - 1)
    return dev_m, var_dev, ne_m, var_ne


def r6(x):
    return round(float(x), 6)


def frac(x):
    return str(F(x))


def main():
    w0 = F(6)

    ce_row, ce_col = device_payoff(w0)
    ce_row_e, ce_col_e = device_payoff_enumerated(w0)
    valid, slacks = device_valid_ce(w0)
    q_ne, ne_val = mixed_ne(w0)
    pure_total = F(7) + F(2)
    mixed_total = 2 * ne_val
    best_nash_total = max(pure_total, mixed_total)
    ce_total = ce_row + ce_col
    per_player_gap = ce_row - ne_val
    total_gap = ce_total - best_nash_total

    dev_m, var_dev, ne_m, var_ne = monte_carlo(SEED, N)
    dev_m2, var_dev2, ne_m2, var_ne2 = monte_carlo(SEED, N)
    determinism_ok = (dev_m, var_dev, ne_m, var_ne) == (dev_m2, var_dev2, ne_m2, var_ne2)
    se = math.sqrt(var_dev / N + var_ne / N)
    z = (dev_m - ne_m) / se

    band = [F(5), F(21, 4), F(11, 2), F(23, 4), F(6)]
    robustness = []
    band_ok = True
    for w in band:
        v_ok, _ = device_valid_ce(w)
        d_row, _ = device_payoff(w)
        _, m_val = mixed_ne(w)
        dominates = d_row > m_val
        band_ok = band_ok and v_ok and dominates
        robustness.append({
            "w": frac(w),
            "valid_ce": v_ok,
            "ce_payoff": frac(d_row),
            "mixed_ne_payoff": frac(m_val),
            "dominates": dominates,
        })

    g1 = bool(valid and ce_row == F(5) and ce_col == F(5))
    g2 = bool(dev_m > ne_m and z >= 3.0)
    g3 = bool(band_ok)
    g4 = bool(
        ce_row == ce_row_e == F(5)
        and per_player_gap == F(1, 3)
        and total_gap == F(2, 3)
        and ne_val == F(14, 3)
    )
    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4}

    results = {
        "proposal": "P211-correlated-equilibrium-public-coin-chicken",
        "seed": SEED,
        "n": N,
        "model": {
            "game": "chicken",
            "payoffs": {"DD": "0,0", "DC": "7,2", "CD": "2,7", "CC": "6,6"},
            "device": "cards (C,C),(D,C),(C,D) each prob 1/3",
        },
        "exact": {
            "ce_payoff_row": frac(ce_row),
            "ce_payoff_col": frac(ce_col),
            "ce_total_welfare": frac(ce_total),
            "device_valid_ce": bool(valid),
            "obedience_slacks": [frac(s) for s in slacks],
            "mixed_ne_dare_prob": frac(q_ne),
            "mixed_ne_payoff": frac(ne_val),
            "pure_nash_total": frac(pure_total),
            "mixed_nash_total": frac(mixed_total),
            "best_nash_total": frac(best_nash_total),
            "per_player_gap_vs_mixed_ne": frac(per_player_gap),
            "total_welfare_gap_vs_best_nash": frac(total_gap),
        },
        "statistical": {
            "mean_device": r6(dev_m),
            "var_device": r6(var_dev),
            "mean_mixed_ne": r6(ne_m),
            "var_mixed_ne": r6(var_ne),
            "z_score": r6(z),
            "determinism_in_process": determinism_ok,
        },
        "robustness": robustness,
        "gates": gates,
        "sim_ready": bool(all(gates.values()) and determinism_ok),
    }

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("results_sha256=" + digest)
    return 0 if results["sim_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
