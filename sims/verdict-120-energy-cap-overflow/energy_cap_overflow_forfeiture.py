#!/usr/bin/env python3
"""
energy_cap_overflow_forfeiture.py — reference verifier for PROPOSAL 107
(round-24, game slot).

The "energy-cap overflow-forfeiture tax" in free-to-play stamina/energy pacing:
stamina regenerates 1 unit per period up to a cap C. A player logs in at a
Poisson rate (inter-login gaps iid Exponential with mean MU periods) and spends
on login. The regen banked between two logins is capped at C, so the overflow
max(0, gap - C) is silently FORFEITED. The fraction of all regenerated stamina a
player actually gets to spend is the exact closed form

    U(mu) = E[min(gap, C)] / E[gap] = 1 - e^{-C/mu}          (exponential gaps)

a CONCAVE, saturating function of the cap: past C ~ mu, raising the cap adds
exponentially little usable energy, and a casual/busy player (large mu) forfeits
a fraction W(mu) = e^{-C/mu} of regenerated stamina that scales with absence.

Gates (all on the /se margin — z on the ESTIMATED MEAN via se = std / sqrt(TRIALS),
the P104/P105/P106 convention):
  G1 casual-forfeiture headline: the casual player (MU_CASUAL, cap C) mean waste
     fraction W_casual >= WASTE_MIN by >= 3 sigma (the cap forfeits most of a
     busy player's regenerated stamina).
  G2 frequency-regressivity control: casual waste fraction strictly exceeds the
     frequent player's (MU_FREQUENT) by >= 3 sigma (two-sample se) -- the
     forfeiture is monotone in the login gap, W ∝ e^{-C/mu}, so the tax is on
     ABSENCE, not a cap-independent constant.
  G3 closed-form anchor MATCH: mean usable fraction U_sim matches the exact
     1 - e^{-C/mu} within 3 sigma (|z| < 3) for BOTH scenarios -- reproduces the
     exponential-overflow formula, so G1's headline is 100% the overflow
     mechanism, not a sampling artifact.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
C = 120                # energy cap, in regen-units (e.g. 120 min at 1 unit/min)
MU_FREQUENT = 60       # frequent player mean inter-login gap (logs ~hourly)
MU_CASUAL = 480        # casual/busy player mean inter-login gap (logs ~8-hourly)
N_GAPS = 5000          # login gaps per replication (ratio-of-sums estimator)
TRIALS = 400           # independent replications -> mean +/- se over TRIALS
SIGMA_GATE = 3.0       # gate threshold in sigma
WASTE_MIN = 0.70       # G1 headline: casual waste fraction must reach this


def usable_fraction_closed(mu):
    """Exact usable (spendable) fraction of regenerated stamina, exponential gaps."""
    return 1.0 - math.exp(-C / mu)


def waste_fraction_closed(mu):
    """Exact overflow-forfeited fraction of regenerated stamina, exponential gaps."""
    return math.exp(-C / mu)


def simulate_scenario(mu, rng):
    """Monte-Carlo one scenario.

    Each of TRIALS replications draws N_GAPS iid Exponential(mean mu) login gaps
    and records that replication's utilization = sum(min(gap, C)) / sum(gap) and
    waste_frac = 1 - utilization. Returns (mean_util, se_util, mean_waste,
    se_waste) with se = sample-sd / sqrt(TRIALS) over the TRIALS replications.
    """
    su = su2 = sw = sw2 = 0.0
    for _ in range(TRIALS):
        sum_gap = 0.0
        sum_usable = 0.0
        for _ in range(N_GAPS):
            gap = rng.expovariate(1.0 / mu)
            sum_gap += gap
            sum_usable += gap if gap < C else C
        util = sum_usable / sum_gap
        waste = 1.0 - util
        su += util
        su2 += util * util
        sw += waste
        sw2 += waste * waste
    mu_util = su / TRIALS
    var_util = max(su2 / TRIALS - mu_util * mu_util, 0.0)
    se_util = math.sqrt(var_util / TRIALS)
    mu_waste = sw / TRIALS
    var_waste = max(sw2 / TRIALS - mu_waste * mu_waste, 0.0)
    se_waste = math.sqrt(var_waste / TRIALS)
    return mu_util, se_util, mu_waste, se_waste


def z_above(value, threshold, se):
    """One-sided z that value exceeds threshold, on its standard error."""
    return (value - threshold) / se if se > 0 else float("inf")


def z_diff(a, sea, b, seb):
    """Two-sample z that a exceeds b."""
    se = math.sqrt(sea * sea + seb * seb)
    return (a - b) / se if se > 0 else float("inf")


def z_match(value, anchor, se):
    """Two-sided |z| that value matches anchor within its standard error."""
    return abs(value - anchor) / se if se > 0 else float("inf")


def main():
    rng = random.Random(SEED)

    # Draw the frequent scenario first, then the casual scenario, off the one
    # seeded stream (order pinned for determinism).
    u_freq, se_u_freq, w_freq, se_w_freq = simulate_scenario(MU_FREQUENT, rng)
    u_cas, se_u_cas, w_cas, se_w_cas = simulate_scenario(MU_CASUAL, rng)

    u_freq_cf = usable_fraction_closed(MU_FREQUENT)
    u_cas_cf = usable_fraction_closed(MU_CASUAL)
    w_cas_cf = waste_fraction_closed(MU_CASUAL)
    w_freq_cf = waste_fraction_closed(MU_FREQUENT)

    # G1 — casual-forfeiture headline: W_casual >= WASTE_MIN by >= 3 sigma.
    z_g1 = z_above(w_cas, WASTE_MIN, se_w_cas)
    g1 = (z_g1 >= SIGMA_GATE) and (w_cas >= WASTE_MIN)

    # G2 — frequency-regressivity control: casual waste > frequent waste by >=3s.
    z_g2 = z_diff(w_cas, se_w_cas, w_freq, se_w_freq)
    g2 = (z_g2 >= SIGMA_GATE) and (w_cas > w_freq)

    # G3 — closed-form anchor MATCH (|z| < 3 for BOTH scenarios).
    z_g3_freq = z_match(u_freq, u_freq_cf, se_u_freq)
    z_g3_cas = z_match(u_cas, u_cas_cf, se_u_cas)
    g3 = (z_g3_freq < SIGMA_GATE) and (z_g3_cas < SIGMA_GATE)

    all_pass = g1 and g2 and g3

    results = {
        "params": {
            "SEED": SEED, "C": C, "MU_FREQUENT": MU_FREQUENT,
            "MU_CASUAL": MU_CASUAL, "N_GAPS": N_GAPS, "TRIALS": TRIALS,
            "SIGMA_GATE": SIGMA_GATE, "WASTE_MIN": WASTE_MIN,
        },
        "closed_form": {
            "U_frequent": round(u_freq_cf, 6), "U_casual": round(u_cas_cf, 6),
            "W_frequent": round(w_freq_cf, 6), "W_casual": round(w_cas_cf, 6),
        },
        "sim": {
            "U_frequent": round(u_freq, 6), "se_U_frequent": round(se_u_freq, 6),
            "U_casual": round(u_cas, 6), "se_U_casual": round(se_u_cas, 6),
            "W_frequent": round(w_freq, 6), "se_W_frequent": round(se_w_freq, 6),
            "W_casual": round(w_cas, 6), "se_W_casual": round(se_w_cas, 6),
        },
        "gates": {
            "G1_casual_forfeiture": {"z": round(z_g1, 4),
                                     "W_casual": round(w_cas, 6),
                                     "WASTE_MIN": WASTE_MIN, "pass": g1},
            "G2_frequency_regressivity": {"z": round(z_g2, 4),
                                          "W_casual": round(w_cas, 6),
                                          "W_frequent": round(w_freq, 6),
                                          "pass": g2},
            "G3_anchor_match": {"z_frequent": round(z_g3_freq, 4),
                                "z_casual": round(z_g3_cas, 4), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("energy_cap_overflow_forfeiture_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
