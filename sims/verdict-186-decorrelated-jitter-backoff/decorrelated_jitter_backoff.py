#!/usr/bin/env python3
"""
Decorrelated jitter backoff -- a retry/backpressure law for fleets.

HEAD
----
When N clients back off after a shared failure using PLAIN exponential backoff
(no jitter), their retries stay SYNCHRONIZED: every client that collides in one
round reschedules to the same future instant, so each round the whole surviving
herd collides again. Total retry work then grows super-linearly in N and the
thundering herd re-forms round after round. Adding FULL JITTER -- sampling the
wait uniformly in [1, window] instead of taking the whole window -- DECORRELATES
the retries: the herd is smeared across the backoff window, per-slot contention
collapses toward server capacity, and both the total number of calls and the
repeated peak contention drop sharply. Adding randomness REDUCES total work.

GROUNDING
---------
Marc Brooker, "Exponential Backoff And Jitter", AWS Architecture Blog:
  https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
Documents (via simulation) that Full Jitter minimizes competing calls and total
work vs no-jitter exponential backoff ("we've reduced our call count by more
than half"; "The no-jitter exponential backoff approach is the clear loser. It
not only takes more work, but also takes more time").

METHOD
------
A slotted contention/drain model. N clients each need one success from a shared
server that clears at most K requests per slot; if more than K attempt in a
slot, K succeed (chosen at random) and the rest fail and reschedule after a
capped-exponential backoff window w(f)=min(CAP, BASE*2^f) on their f-th failure.
  * strategy "none":  retry delay = w(f)                  (synchronized)
  * strategy "full":  retry delay = U{1..w(f)}            (decorrelated)
  * strategy "equal": retry delay = w//2 + U{0..w-w//2}   (AWS "equal jitter", non-gated)

Pre-registered gates (z_gate = 3.0):
  G1  work reduction (tight Dirac herd, all N fail at t=0): full-jitter MEAN
      total attempts is >=3 sigma below the DETERMINISTIC no-jitter total, and
      the reduction fraction 1 - mean_full/total_none >= 0.30. (No-jitter's
      drain is deterministic in this regime, so it is an exact baseline and the
      z uses the full-jitter replication SE.)
  G2  thundering-herd flattening (same regime): the repeated post-herd peak
      contention -- the max attempts in any slot AFTER the unavoidable t=0 herd
      -- is >=3 sigma smaller under full jitter than the deterministic no-jitter
      value (N-K), i.e. jitter stops the herd re-forming at full strength.
  G3  robustness under a shifted arrival distribution (>=3 sigma, paired): when
      the synchronized herd is replaced by an over-dispersed (geometric) arrival
      smear -- a different generating distribution -- full jitter STILL reduces
      total work vs no-jitter on the SAME arrivals; the paired diff
      (none - full) is >=3 sigma positive across trials.

Determinism: every trial/arm draws from its own random.Random(<int seed>), so
output is byte-identical in-process AND across invocations. run() is called
twice and the two canonical dicts are asserted identical; the sha256 of the
canonical results dict is the disclosed digest.
Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.

Stdlib only.
"""

import hashlib
import heapq
import json
import random
import statistics

SEED = 20260717
Z_GATE = 3.0
N_CLIENTS = 200
CAPACITY = 10
BASE = 1
CAP = 64
TRIALS = 400
SMEAR_MEAN = 2.0
REDUCTION_FLOOR = 0.30


def r6(x):
    return round(float(x), 6)


def window(fail_count):
    w = BASE * (2 ** fail_count)
    return CAP if w > CAP else w


def delay_for(rng, fail_count, strategy):
    w = window(fail_count)
    if strategy == "none":
        return w
    if strategy == "full":
        return rng.randint(1, w)
    half = w // 2
    return half + rng.randint(0, w - half)


def simulate(seed, arrivals, strategy):
    rng = random.Random(seed)
    heap = [(arrivals[i], i, 0) for i in range(len(arrivals))]
    heapq.heapify(heap)
    herd_slot = min(arrivals)
    total_attempts = 0
    post_herd_peak = 0
    drain_time = 0
    while heap:
        t = heap[0][0]
        batch = []
        while heap and heap[0][0] == t:
            batch.append(heapq.heappop(heap))
        a = len(batch)
        total_attempts += a
        if t != herd_slot and a > post_herd_peak:
            post_herd_peak = a
        if t > drain_time:
            drain_time = t
        if a <= CAPACITY:
            continue
        survivors = set(rng.sample(range(a), CAPACITY))
        for j in range(a):
            if j in survivors:
                continue
            _, cid, fc = batch[j]
            nf = fc + 1
            d = delay_for(rng, nf, strategy)
            heapq.heappush(heap, (t + d, cid, nf))
    return {
        "total_attempts": total_attempts,
        "post_herd_peak": post_herd_peak,
        "drain_time": drain_time,
    }


def zscore(effect, se):
    return effect / se if se > 0 else 0.0


def run():
    tight = [0] * N_CLIENTS
    none_tight = simulate(SEED, tight, "none")
    full_totals, full_peaks, equal_totals = [], [], []
    for i in range(TRIALS):
        rf = simulate(SEED + 1009 * i, tight, "full")
        full_totals.append(rf["total_attempts"])
        full_peaks.append(rf["post_herd_peak"])
        re = simulate(SEED + 2003 * i, tight, "equal")
        equal_totals.append(re["total_attempts"])

    mean_full_total = statistics.fmean(full_totals)
    se_full_total = statistics.stdev(full_totals) / (TRIALS ** 0.5)
    eff1 = none_tight["total_attempts"] - mean_full_total
    z1 = zscore(eff1, se_full_total)
    reduction = 1.0 - mean_full_total / none_tight["total_attempts"]
    g1 = (z1 >= Z_GATE) and (reduction >= REDUCTION_FLOOR)

    mean_full_peak = statistics.fmean(full_peaks)
    se_full_peak = statistics.stdev(full_peaks) / (TRIALS ** 0.5)
    eff2 = none_tight["post_herd_peak"] - mean_full_peak
    z2 = zscore(eff2, se_full_peak)
    g2 = (z2 >= Z_GATE) and (mean_full_peak < none_tight["post_herd_peak"])

    mean_equal_total = statistics.fmean(equal_totals)

    diffs, none_smear, full_smear = [], [], []
    for i in range(TRIALS):
        arng = random.Random(SEED + 7919 * i)
        arrivals = sorted(int(arng.expovariate(1.0 / SMEAR_MEAN)) for _ in range(N_CLIENTS))
        rn = simulate(SEED + 31 * i, arrivals, "none")
        rfu = simulate(SEED + 53 * i, arrivals, "full")
        none_smear.append(rn["total_attempts"])
        full_smear.append(rfu["total_attempts"])
        diffs.append(rn["total_attempts"] - rfu["total_attempts"])
    mean_diff = statistics.fmean(diffs)
    se_diff = statistics.stdev(diffs) / (TRIALS ** 0.5)
    z3 = zscore(mean_diff, se_diff)
    g3 = (z3 >= Z_GATE) and (mean_diff > 0)

    all_pass = bool(g1 and g2 and g3)

    return {
        "meta": {
            "head": "decorrelated jitter backoff: adding random jitter to exponential retry backoff decorrelates the herd, cutting total retry work and repeated peak contention vs no-jitter backoff",
            "seed": SEED,
            "z_gate": Z_GATE,
            "n_clients": N_CLIENTS,
            "capacity": CAPACITY,
            "base": BASE,
            "cap": CAP,
            "trials": TRIALS,
            "smear_mean": SMEAR_MEAN,
            "reduction_floor": REDUCTION_FLOOR,
            "grounding": "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ (Brooker, AWS Architecture Blog; Full Jitter minimizes competing calls / total work)",
        },
        "tight_herd": {
            "none_total_attempts": none_tight["total_attempts"],
            "none_post_herd_peak": none_tight["post_herd_peak"],
            "none_drain_time": none_tight["drain_time"],
            "full_mean_total": r6(mean_full_total),
            "full_se_total": r6(se_full_total),
            "full_mean_post_herd_peak": r6(mean_full_peak),
            "full_se_post_herd_peak": r6(se_full_peak),
            "equal_mean_total": r6(mean_equal_total),
            "reduction_fraction": r6(reduction),
        },
        "smear_herd": {
            "none_mean_total": r6(statistics.fmean(none_smear)),
            "full_mean_total": r6(statistics.fmean(full_smear)),
            "mean_paired_diff": r6(mean_diff),
            "se_paired_diff": r6(se_diff),
        },
        "gates": {
            "G1_work_reduction_tight": {
                "none_total": none_tight["total_attempts"],
                "full_mean_total": r6(mean_full_total),
                "reduction_fraction": r6(reduction),
                "effect": r6(eff1),
                "z": r6(z1),
                "pass": bool(g1),
            },
            "G2_herd_flattening_tight": {
                "none_post_herd_peak": none_tight["post_herd_peak"],
                "full_mean_post_herd_peak": r6(mean_full_peak),
                "effect": r6(eff2),
                "z": r6(z2),
                "pass": bool(g2),
            },
            "G3_robust_shifted_arrivals": {
                "mean_paired_diff": r6(mean_diff),
                "se_paired_diff": r6(se_diff),
                "z": r6(z3),
                "pass": bool(g3),
            },
        },
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = run()
    r2 = run()
    assert canonical(r1) == canonical(r2), "non-deterministic run()"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    assert r1["all_pass"], "gates did not all pass"


if __name__ == "__main__":
    main()
