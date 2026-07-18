#!/usr/bin/env python3
"""
checkpoint_interval_optimum.py — reference verifier for PROPOSAL 117 (round-27,
FLEET slot opener). Domain: fault-tolerant computing / long-running-job
checkpoint scheduling — the Young-Daly optimal checkpoint interval. A
fleet-domain pure-mechanism head.

The "checkpoint as often as you can afford it" trap. A long fleet job that can
crash and restart from its last checkpoint faces TWO competing wastes: the
checkpoint OVERHEAD (each checkpoint costs C, so more checkpoints = more direct
cost, ~C/tau per unit work) and the lost RECOMPUTE work (a crash discards
everything since the last checkpoint, ~tau/(2M) per unit work at MTBF M). Both
cannot be minimised at once: driving one to zero blows up the other. Intuition
says "to be safe against failures, checkpoint as often as possible" -- but total
wasted time is U-SHAPED in the checkpoint interval tau, with a unique INTERIOR
optimum. Young (1974) first-order / Daly (2006) higher-order:

    tau*   = sqrt(2 * C * M)            (optimal interval; SUBLINEAR in the MTBF)
    o*     = sqrt(2 * C / M)            (minimum overhead fraction at tau*)

so BOTH checkpointing far more often than tau* AND far less often waste strictly
MORE wall time than the optimum -- over-checkpointing is not "safer", it is
wasteful, exactly as wasteful (in the leading order) as the symmetric
under-checkpointing. And the optimal interval grows only as the SQUARE ROOT of
the MTBF: a 4x more reliable machine warrants only a 2x longer interval and
halves the achievable overhead.

Exact model (Daly 2006, restart cost R=0). Poisson failures at rate 1/M
(memoryless exponential inter-failure). A segment does tau useful work then a
checkpoint of cost C, so it is exposed to failure for L=tau+C; a crash at time
t<L costs t wall time and loses the segment (retry from the last checkpoint, no
restart cost). By memorylessness the expected wall time per SUCCESSFUL segment is
M*(exp(L/M)-1), so for total useful work W (= n_seg*tau) the exact expected
overhead fraction is

    O(tau) = (M/tau) * (exp((tau+C)/M) - 1) - 1

minimised at tau ~ sqrt(2CM) with minimum ~ sqrt(2C/M) (Taylor-expand
exp: O(tau) ~ C/tau + tau/(2M), a convex sum whose two terms cross at tau*). The
Monte-Carlo below reproduces O(tau) segment-by-segment with fresh exponential
draws; the exact O(tau) values are the closed-form anchors (no numpy/scipy).

Gates (all on the /se margin, the P104..P116 convention -- z on the estimated
MEAN via its standard error se = std / sqrt(TRIALS)):
  G1 over-checkpointing headline: checkpointing K=8x MORE often than the optimum
     (interval tau*/K) wastes strictly MORE wall time than tau* -- the frequent
     penalty overhead(tau*/K) - overhead(tau*) is at or above DELTA_MIN by
     >= 3 sigma. Inverts "checkpoint as often as possible is safest".
  G2 U-shape + square-root-law control: (a) checkpointing K=8x LESS often
     (interval tau**K) ALSO wastes strictly more, rare penalty
     overhead(tau**K) - overhead(tau*) >= DELTA_MIN by >= 3 sigma -- total waste
     is U-shaped with an INTERIOR optimum, neither extreme wins; AND (b) the
     square-root-law control: quadrupling the MTBF (M -> 4M) with the interval
     scaled to its NEW optimum tau*(4M)=2*tau* HALVES the optimum overhead
     (o* = sqrt(2C/M) scaling), overhead(tau*,M) - overhead(tau*(4M),4M) >=
     HALVE_MIN by >= 3 sigma -- isolating the sqrt law as the cause.
  G3 closed-form anchor MATCH: the three measured overheads reproduce the exact
     Daly law O(tau)=(M/tau)(exp((tau+C)/M)-1)-1 within 3 sigma each (optimum,
     frequent, rare) -- the effect IS the checkpoint-restart overhead law, and
     the Young optimum tau*=sqrt(2CM) with minimum overhead sqrt(2C/M) sit at
     the measured minimum.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
C = 1.0                # checkpoint cost (wall-time units per checkpoint)
M = 200.0              # mean time between failures (MTBF); failure rate 1/M
W = 40000.0            # total useful work per job (wall-time-equivalent units)
K = 8                  # extreme factor: frequent = tau*/K, rare = tau**K
TRIALS = 200           # independent experiments (the /se convention averages over these)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)
DELTA_MIN = 0.05       # G1/G2a floor on the extreme-vs-optimum overhead penalty
HALVE_MIN = 0.02       # G2b floor on the optimum-overhead drop when MTBF quadruples


def tau_star(cost, mtbf):
    """Young (1974) first-order optimal checkpoint interval sqrt(2*C*M)."""
    return math.sqrt(2.0 * cost * mtbf)


def daly_overhead(tau, cost, mtbf):
    """Exact expected overhead fraction O(tau)=(M/tau)(exp((tau+C)/M)-1)-1 (Daly 2006, R=0)."""
    return (mtbf / tau) * (math.exp((tau + cost) / mtbf) - 1.0) - 1.0


def run_job(rng, tau, cost, mtbf, total_work):
    """Simulate one job: accumulate total_work useful work in tau-sized segments,
    each followed by a cost-C checkpoint, under Poisson(1/mtbf) failures. Returns
    the overhead fraction wall/effective_work - 1. On a crash the partial segment
    is lost (retry from the last checkpoint, no restart cost)."""
    n_seg = max(1, round(total_work / tau))
    effective_work = n_seg * tau
    seg_len = tau + cost                     # exposure per attempt (work + checkpoint)
    wall = 0.0
    for _ in range(n_seg):
        while True:
            tf = rng.expovariate(1.0 / mtbf)   # time to next failure (memoryless)
            if tf >= seg_len:
                wall += seg_len                # segment + checkpoint completed
                break
            wall += tf                         # crashed mid-segment; lose the work, retry
    return wall / effective_work - 1.0


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)

    t_opt = tau_star(C, M)                    # 20.0 at C=1, M=200
    t_freq = t_opt / K                        # 2.5  (checkpoint 8x too often)
    t_rare = t_opt * K                        # 160.0 (checkpoint 8x too rarely)
    M2 = 4.0 * M                              # quadrupled MTBF for the sqrt-law control
    t_opt2 = tau_star(C, M2)                  # 40.0 = 2*t_opt (interval doubles, not quadruples)

    # Exact Daly closed-form anchors (R=0).
    anchor_opt = daly_overhead(t_opt, C, M)
    anchor_freq = daly_overhead(t_freq, C, M)
    anchor_rare = daly_overhead(t_rare, C, M)
    anchor_opt2 = daly_overhead(t_opt2, C, M2)
    young_o_star = math.sqrt(2.0 * C / M)     # first-order min overhead (descriptive)
    young_o_star2 = math.sqrt(2.0 * C / M2)   # first-order min overhead at 4M (descriptive)

    opt, freq, rare, opt2 = [], [], [], []
    for _ in range(TRIALS):
        opt.append(run_job(rng, t_opt, C, M, W))
        freq.append(run_job(rng, t_freq, C, M, W))
        rare.append(run_job(rng, t_rare, C, M, W))
        opt2.append(run_job(rng, t_opt2, C, M2, W))

    o_opt, se_opt = mean_se(opt)
    o_freq, se_freq = mean_se(freq)
    o_rare, se_rare = mean_se(rare)
    o_opt2, se_opt2 = mean_se(opt2)

    # G1 over-checkpointing headline: frequent penalty >= DELTA_MIN by >= 3 sigma.
    pen_freq = o_freq - o_opt
    se_pen_freq = math.sqrt(se_freq ** 2 + se_opt ** 2)
    z_g1 = (pen_freq - DELTA_MIN) / se_pen_freq if se_pen_freq > 0 else float("inf")
    g1 = z_g1 >= SIGMA_GATE

    # G2 U-shape + sqrt-law control.
    pen_rare = o_rare - o_opt
    se_pen_rare = math.sqrt(se_rare ** 2 + se_opt ** 2)
    z_g2_rare = (pen_rare - DELTA_MIN) / se_pen_rare if se_pen_rare > 0 else float("inf")
    halve = o_opt - o_opt2                    # optimum overhead should fall when MTBF quadruples
    se_halve = math.sqrt(se_opt ** 2 + se_opt2 ** 2)
    z_g2_halve = (halve - HALVE_MIN) / se_halve if se_halve > 0 else float("inf")
    g2 = (z_g2_rare >= SIGMA_GATE) and (z_g2_halve >= SIGMA_GATE)

    # G3 closed-form anchor MATCH: three overheads reproduce the exact Daly law.
    z_g3_opt = abs(o_opt - anchor_opt) / se_opt if se_opt > 0 else float("inf")
    z_g3_freq = abs(o_freq - anchor_freq) / se_freq if se_freq > 0 else float("inf")
    z_g3_rare = abs(o_rare - anchor_rare) / se_rare if se_rare > 0 else float("inf")
    g3 = (z_g3_opt < SIGMA_GATE) and (z_g3_freq < SIGMA_GATE) and (z_g3_rare < SIGMA_GATE)

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "C": C, "M": M, "W": W, "K": K, "TRIALS": TRIALS,
                   "SIGMA_GATE": SIGMA_GATE, "DELTA_MIN": DELTA_MIN, "HALVE_MIN": HALVE_MIN},
        "intervals": {"tau_star": round(t_opt, 6), "tau_frequent": round(t_freq, 6),
                      "tau_rare": round(t_rare, 6), "tau_star_4M": round(t_opt2, 6)},
        "anchor": {"daly_opt": round(anchor_opt, 6), "daly_frequent": round(anchor_freq, 6),
                   "daly_rare": round(anchor_rare, 6), "daly_opt_4M": round(anchor_opt2, 6),
                   "young_o_star": round(young_o_star, 6),
                   "young_o_star_4M": round(young_o_star2, 6)},
        "sim": {
            "overhead_opt": round(o_opt, 6), "se_opt": round(se_opt, 6),
            "overhead_frequent": round(o_freq, 6), "se_frequent": round(se_freq, 6),
            "overhead_rare": round(o_rare, 6), "se_rare": round(se_rare, 6),
            "overhead_opt_4M": round(o_opt2, 6), "se_opt_4M": round(se_opt2, 6),
            "penalty_frequent": round(pen_freq, 6), "se_penalty_frequent": round(se_pen_freq, 6),
            "penalty_rare": round(pen_rare, 6), "se_penalty_rare": round(se_pen_rare, 6),
            "halving_drop": round(halve, 6), "se_halving_drop": round(se_halve, 6),
        },
        "gates": {
            "G1_over_checkpointing": {"z": round(z_g1, 4), "pass": g1},
            "G2_ushape_sqrt_law": {
                "z_rare": round(z_g2_rare, 4), "z_halve": round(z_g2_halve, 4), "pass": g2},
            "G3_anchor_match": {
                "z_opt": round(z_g3_opt, 4), "z_frequent": round(z_g3_freq, 4),
                "z_rare": round(z_g3_rare, 4), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("checkpoint_interval_optimum_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
