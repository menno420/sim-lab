#!/usr/bin/env python3
"""
winners_curse_task_auction.py — reference verifier for PROPOSAL 101 (round-23,
FLEET-slot opener). Domain: multi-agent fleet economics — the winner's curse in a
common-value auction (Capen, Clapp & Campbell 1971; Milgrom & Weber 1982).

The trap: N agents compete to CLAIM a task whose true value V is COMMON (shared)
but unknown. Each agent i sees an unbiased-but-noisy private signal s_i = V + e_i
(e_i i.i.d., E[e_i]=0), and the highest signal wins the claim. Winning is itself
information: the winner is, by construction, the agent whose noise e_i was the
LARGEST of the N draws, so E[e_winner] = E[max of N noises] > 0. An agent that
commits resources sized to its OWN signal (bids b_i = s_i, "I value it at my
estimate") therefore overpays by that order-statistic bias and earns NEGATIVE
expected profit even though every individual estimate is unbiased. The cure is to
SHADE the bid down by the expected winning-noise, which grows with N.

For e ~ Uniform(-w, w), the expected maximum of N draws is
    E[max e] = w*(N-1)/(N+1),
so the naive winner's expected profit is exactly -w*(N-1)/(N+1) (closed form),
and shading every bid by that amount restores break-even (E[profit]=0).

Gates (all >= 3 sigma unless noted):
  G1 winner's-curse headline: the naive policy (bid = own signal) yields a
     mean winner profit that is NEGATIVE at >= 3 sigma — the winner systematically
     loses despite individually UNBIASED signals.
  G2 order-statistic shading cures it: the shaded policy (bid = signal minus
     w*(N-1)/(N+1)) beats the naive policy by >= 3 sigma AND is not significantly
     negative (mean_shaded >= -3*se_shaded, i.e. break-even or better).
  G3 analytic-anchor MATCH: the simulated naive mean winner profit matches the
     closed-form order-statistic bias -w*(N-1)/(N+1) within 3 sigma (|z| < 3).

Descriptive (not a gate): a bidder-count sweep showing the curse DEEPENS
monotonically with N (more competitors -> a more upward-biased winner).

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
N_BIDDERS = 8          # agents competing to claim each task (the headline world)
W_NOISE = 1.0          # signal-noise half-width; s_i = V + Uniform(-W_NOISE, +W_NOISE)
V_TRUE = 10.0          # common (shared) task value; agents observe only s_i, never V
N_AUCTIONS = 200_000   # independent common-value auctions (Monte-Carlo)
SWEEP_N = (2, 4, 8, 16)  # bidder counts for the "curse deepens with N" sweep
SWEEP_AUCTIONS = 50_000  # auctions per sweep point


def expected_max_noise(n, w):
    """E[max of n i.i.d. Uniform(-w, w)] = w*(n-1)/(n+1) (order-statistic mean)."""
    return w * (n - 1) / (n + 1)


def run_auctions(n_bidders, w, v_true, n_auctions, shade, rng):
    """Simulate n_auctions common-value first-price auctions.

    Each auction: draw n_bidders i.i.d. signals s = v_true + Uniform(-w, w); the
    highest signal wins and 'pays' its bid. Under bid = s - shade the realized
    winner profit is v_true - (s_win - shade) = -(s_win - v_true) + shade =
    -e_win + shade. Returns (mean_profit, se_profit) over the winners."""
    s = 0.0
    s2 = 0.0
    for _ in range(n_auctions):
        e_win = -w - 1.0  # below any possible noise draw
        for _b in range(n_bidders):
            e = rng.uniform(-w, w)
            if e > e_win:
                e_win = e
        profit = -e_win + shade
        s += profit
        s2 += profit * profit
    mean = s / n_auctions
    var = max(s2 / n_auctions - mean * mean, 0.0)
    se = math.sqrt(var / n_auctions)
    return mean, se


def z_diff(a, sea, b, seb):
    se = math.sqrt(sea * sea + seb * seb)
    return (a - b) / se if se > 0 else float("inf")


def main():
    rng = random.Random(SEED)

    shade_star = expected_max_noise(N_BIDDERS, W_NOISE)  # optimal bid shading

    # Headline world (N_BIDDERS): naive policy (shade 0) then shaded policy.
    mean_naive, se_naive = run_auctions(
        N_BIDDERS, W_NOISE, V_TRUE, N_AUCTIONS, 0.0, rng)
    mean_shaded, se_shaded = run_auctions(
        N_BIDDERS, W_NOISE, V_TRUE, N_AUCTIONS, shade_star, rng)

    # G1 winner's-curse headline: naive mean winner profit is NEGATIVE at >=3s.
    z_g1 = mean_naive / se_naive if se_naive > 0 else float("-inf")
    g1 = (mean_naive < 0.0) and (abs(z_g1) >= 3.0)

    # G2 shading cures it: shaded beats naive by >=3s AND is not sig. negative.
    z_g2 = z_diff(mean_shaded, se_shaded, mean_naive, se_naive)
    g2 = (z_g2 >= 3.0) and (mean_shaded >= -3.0 * se_shaded)

    # G3 anchor MATCH: naive mean profit == closed-form -w*(N-1)/(N+1).
    naive_closed = -expected_max_noise(N_BIDDERS, W_NOISE)
    z_g3 = abs(mean_naive - naive_closed) / se_naive if se_naive > 0 else float("inf")
    g3 = z_g3 < 3.0

    all_pass = g1 and g2 and g3

    # Descriptive: the curse deepens monotonically with the number of bidders.
    sweep = {}
    prev = None
    monotone = True
    for n in SWEEP_N:
        m, se = run_auctions(n, W_NOISE, V_TRUE, SWEEP_AUCTIONS, 0.0, rng)
        closed = -expected_max_noise(n, W_NOISE)
        sweep[str(n)] = {"mean_naive_profit": round(m, 6),
                         "se": round(se, 6),
                         "closed_form": round(closed, 6)}
        if prev is not None and not (m < prev - 1e-9):
            monotone = False
        prev = m

    results = {
        "params": {"SEED": SEED, "N_BIDDERS": N_BIDDERS, "W_NOISE": W_NOISE,
                   "V_TRUE": V_TRUE, "N_AUCTIONS": N_AUCTIONS,
                   "SWEEP_N": list(SWEEP_N), "SWEEP_AUCTIONS": SWEEP_AUCTIONS},
        "policy": {"shade_star": round(shade_star, 6),
                   "naive_profit_closed_form": round(naive_closed, 6)},
        "sim": {
            "mean_naive_profit": round(mean_naive, 6), "se_naive": round(se_naive, 6),
            "mean_shaded_profit": round(mean_shaded, 6), "se_shaded": round(se_shaded, 6),
        },
        "sweep_curse_deepens_with_N": sweep,
        "sweep_monotone_deepening": monotone,
        "gates": {
            "G1_winners_curse": {"z": round(z_g1, 2), "pass": g1},
            "G2_shading_cure": {"z_vs_naive": round(z_g2, 2), "pass": g2},
            "G3_anchor_match": {"z": round(z_g3, 2), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("winners_curse_task_auction_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
