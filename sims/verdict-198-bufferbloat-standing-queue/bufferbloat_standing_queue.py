#!/usr/bin/env python3
"""PROPOSAL 185 - Bufferbloat / standing-queue latency: on a saturated
server, ENLARGING the buffer (finite queue capacity K) makes mean latency
grow ~linearly in K while goodput stays pinned at the service rate mu. A
bigger buffer buys a permanent standing queue, not throughput. M/M/1/K
discrete-event verifier, stdlib-only, deterministic under SEED, common
random numbers across the two buffer sizes. No disk writes. Prints the
whole results dict (pretty) then its canonical-JSON sha256.
WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY."""

import sys
import math
import json
import hashlib
import random
from collections import deque

SEED = 20260717
Z_GATE = 3.0


def r6(x):
    return round(float(x), 6)


def mean_std(vals):
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in vals) / (n - 1)
    return m, math.sqrt(v)


def z_pos(vals, null):
    m, s = mean_std(vals)
    n = len(vals)
    if s == 0.0:
        return 0.0
    return (m - null) / (s / math.sqrt(n))


def simulate(K, arr_times, serv, warm):
    """M/M/1/K FCFS. arr_times: absolute arrival times (sorted). serv[j]:
    service time for arrival j, consumed when j starts service. Returns
    (throughput, mean_sojourn_after_warmup)."""
    n = len(arr_times)
    t = 0.0
    nsys = 0
    fifo = deque()
    dep_time = float("inf")
    ai = 0
    served = 0
    sojourns = []
    tfinal = 0.0
    while ai < n or nsys > 0:
        next_arr = arr_times[ai] if ai < n else float("inf")
        if next_arr <= dep_time:
            t = next_arr
            if nsys < K:
                fifo.append((arr_times[ai], ai))
                nsys += 1
                if nsys == 1:
                    dep_time = t + serv[fifo[0][1]]
            ai += 1
        else:
            t = dep_time
            arr_t, idx = fifo.popleft()
            nsys -= 1
            served += 1
            if idx >= warm:
                sojourns.append(t - arr_t)
            tfinal = t
            if nsys > 0:
                dep_time = t + serv[fifo[0][1]]
            else:
                dep_time = float("inf")
    throughput = served / tfinal if tfinal > 0.0 else 0.0
    w = sum(sojourns) / len(sojourns) if sojourns else 0.0
    return throughput, w


def gen_streams(rng, n, lam, mu):
    arr = []
    t = 0.0
    for _ in range(n):
        t += rng.expovariate(lam)
        arr.append(t)
    serv = [rng.expovariate(mu) for _ in range(n)]
    return arr, serv


def paired_run(trials, n_arr, warm, mu, lam, k_small, k_large):
    """Common-random-numbers paired difference W_large - W_small and the
    two throughputs, per trial."""
    dW = []
    thr_s = []
    thr_l = []
    ws = []
    wl = []
    for i in range(trials):
        rng = random.Random(SEED + 1 + i)
        arr, serv = gen_streams(rng, n_arr, lam, mu)
        ts, w_s = simulate(k_small, arr, serv, warm)
        tl, w_l = simulate(k_large, arr, serv, warm)
        dW.append(w_l - w_s)
        thr_s.append(ts)
        thr_l.append(tl)
        ws.append(w_s)
        wl.append(w_l)
    return dW, thr_s, thr_l, ws, wl


def run():
    TRIALS = 40
    N_ARR = 20000
    WARM = 4000
    MU = 1.0
    R_BASE = 1.25
    R_SHIFT = 1.5
    K_SMALL = 25
    K_LARGE = 75
    EPS = 0.02

    lam_b = R_BASE * MU
    lam_s = R_SHIFT * MU

    dW, ts, tl, ws, wl = paired_run(TRIALS, N_ARR, WARM, MU, lam_b, K_SMALL, K_LARGE)
    g1_dW_mean, g1_dW_std = mean_std(dW)
    g1_z = z_pos(dW, 0.0)
    w_s_mean, _ = mean_std(ws)
    w_l_mean, _ = mean_std(wl)
    thr_s_mean, _ = mean_std(ts)
    thr_l_mean, _ = mean_std(tl)
    w_ratio = w_l_mean / w_s_mean if w_s_mean > 0 else 0.0
    g1_pass = (g1_dW_mean > 0.0) and (g1_z >= Z_GATE)
    thr_gap = abs(thr_s_mean - thr_l_mean)
    g2_pass = (thr_gap <= EPS * MU
               and thr_s_mean >= (1.0 - EPS) * MU
               and thr_l_mean >= (1.0 - EPS) * MU)

    dW2, ts2, tl2, ws2, wl2 = paired_run(TRIALS, N_ARR, WARM, MU, lam_s, K_SMALL, K_LARGE)
    g3_dW_mean, _ = mean_std(dW2)
    g3_z = z_pos(dW2, 0.0)
    thr_s2_mean, _ = mean_std(ts2)
    thr_l2_mean, _ = mean_std(tl2)
    thr_gap2 = abs(thr_s2_mean - thr_l2_mean)
    g3_pass = (g3_dW_mean > 0.0 and g3_z >= Z_GATE
               and thr_gap2 <= EPS * MU
               and thr_s2_mean >= (1.0 - EPS) * MU
               and thr_l2_mean >= (1.0 - EPS) * MU)

    gates = {
        "G1_latency_scales_with_buffer": g1_pass,
        "G2_no_goodput_dividend": g2_pass,
        "G3_robust_shifted_load": g3_pass,
    }
    order = ("G1_latency_scales_with_buffer",
             "G2_no_goodput_dividend",
             "G3_robust_shifted_load")
    all_pass = all(gates.values())
    first_failing = next((k for k in order if not gates[k]), None)

    return {
        "seed": SEED,
        "z_gate": Z_GATE,
        "trials": TRIALS,
        "n_arrivals": N_ARR,
        "warmup": WARM,
        "mu": MU,
        "load_base": R_BASE,
        "load_shift": R_SHIFT,
        "k_small": K_SMALL,
        "k_large": K_LARGE,
        "eps_throughput": EPS,
        "g1_dwait_mean": r6(g1_dW_mean),
        "g1_dwait_std": r6(g1_dW_std),
        "g1_z": r6(g1_z),
        "g1_w_small_mean": r6(w_s_mean),
        "g1_w_large_mean": r6(w_l_mean),
        "g1_w_ratio": r6(w_ratio),
        "g2_thr_small_mean": r6(thr_s_mean),
        "g2_thr_large_mean": r6(thr_l_mean),
        "g2_thr_gap": r6(thr_gap),
        "g3_dwait_mean": r6(g3_dW_mean),
        "g3_z": r6(g3_z),
        "g3_thr_small_mean": r6(thr_s2_mean),
        "g3_thr_large_mean": r6(thr_l2_mean),
        "g3_thr_gap": r6(thr_gap2),
        "gates": gates,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
    }


def _canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = run()
    r2 = run()
    assert _canon(r1) == _canon(r2), "non-deterministic double-run"
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + hashlib.sha256(_canon(r1).encode("utf-8")).hexdigest())
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
