#!/usr/bin/env python3
"""coordinated omission -- round-35 FLEET-slot verifier (PROPOSAL 149).

Phenomenon: a CLOSED-LOOP / synchronous load generator waits for each request
to return before issuing the next, so during a service stall it has exactly ONE
request outstanding -- it CANNOT send the requests it was scheduled to send, and
it silently OMITS the coordinated backlog those requests would have measured.
The measured latency distribution is therefore biased LOW: the p99/p99.9 the
closed loop reports can understate the truth by orders of magnitude, because the
MEASUREMENT METHOD (not the system under test) sets the observed tail.

One underlying single-server FIFO system, measured two ways over the SAME stall
schedule and the SAME per-request service times:

  * OPEN-LOOP (ground truth of user experience): requests ARRIVE at fixed times
    0, tau, 2*tau, ... regardless of whether prior requests have completed; each
    queues at its arrival time; the server processes FIFO and is FROZEN during a
    stall; latency_i = completion_i - arrival_i. Requests that arrive during a
    stall pile up -- the coordinated backlog, ~D/tau per stall.

  * CLOSED-LOOP (the flawed synchronous load generator): exactly ONE request
    outstanding; the next request is dispatched at the completion time of the
    previous (start t=0); identical server dynamics, stall schedule, service
    seed; latency = completion - dispatch. During a stall it records only ~1
    inflated sample (the single frozen request) and NEVER generates the backlog.

  * CO-CORRECTION (HdrHistogram style): for each closed sample L with L > tau,
    back-fill synthetic samples L-tau, L-2*tau, ... down to > tau, and union with
    the originals. This reconstructs the omitted coordinated samples and lifts the
    measured tail back toward the open-loop truth.

Gates (each z = mean/se across R independent replicates; require z >= 3.0; the
mechanism makes them land FAR above 3):
  * G1 tail-blindness   : x_i = log(open_p99_i / closed_p99_i), H0 mean 0
                          -> large positive z (open p99 >> closed p99).
  * G2 omitted-backlog  : x_i = open_stall_count_i - closed_stall_count_i, H0 0
                          -> large positive z (open backlog ~D/tau, closed ~1).
  * G3 correction-recov : x_i = log(corrected_p99_i / closed_p99_i), H0 0
                          -> large positive z (the CO correction lifts the tail).
    plus a descriptive mean recovery fraction
                          (corr_p99 - closed_p99) / (open_p99 - closed_p99).

Stdlib only (hashlib, json, math, random). WHOLE-DICT / NO-SELF-FIELD /
STDOUT-ONLY, with the P127+ twist: the results dict carries no self-referential
sha field, every float is rounded to 6 dp, the hashed preimage is the compact
canonical json.dumps(sort_keys=True, separators=(",",":")) of the whole dict,
the stdout DUMP is pretty indent=2, and no JSON is written to disk. Deterministic
under the pinned SEED; replicate i draws from random.Random(SEED + i); a double
run is byte-identical; exit 0 iff all three gates pass, else 1.
"""

import hashlib
import json
import math
import random

SEED = 20260717
R = 200                 # independent replicates (>= 150)
LAM = 1000.0            # intended request rate -> tau = 1/LAM = 1 ms
TAU = 1.0 / LAM         # inter-arrival = 0.001 s
T = 1.0                 # horizon (s)
MU_S = 0.0001           # mean base service time = 0.1 ms (utilisation MU_S/TAU = 0.1)
D = 0.05                # stall duration = 50 ms (D >> tau: D/tau = 50)
N_STALLS = 6            # stalls per replicate
N_SVC = 12000           # pre-generated service times per replicate (safe upper bound)
Q = 0.99               # percentile for the reported tail (p99)
Z_GATE = 3.0


def draw_stall_windows(rng):
    """n_stalls non-overlapping windows [s, s+D) in [0, T), one per equal cell,
    offset by a per-replicate uniform draw. Shared by open and closed loops."""
    cell = T / N_STALLS
    slack = cell - D
    windows = []
    for i in range(N_STALLS):
        s = i * cell + rng.random() * slack
        windows.append((s, s + D))
    windows.sort()
    return windows


def service_completion(begin, svc, stalls):
    """Completion time for a request that begins service at `begin` and needs
    `svc` seconds of processing, on a server FROZEN during each stall window.
    `stalls` is sorted ascending by start and non-overlapping."""
    current = begin
    remaining = svc
    for s, e in stalls:
        if e <= current:
            continue
        if s >= current + remaining:
            break
        if s <= current:
            current = e
        else:
            remaining -= (s - current)
            current = e
    return current + remaining


def overlaps_any(a, c, stalls):
    """True iff the interval [a, c) overlaps any stall window [s, e)."""
    for s, e in stalls:
        if s < c and e > a:
            return True
    return False


def percentile(xs, q):
    """Deterministic nearest-rank percentile."""
    if not xs:
        return 0.0
    s = sorted(xs)
    rank = math.ceil(q * len(s))
    if rank < 1:
        rank = 1
    return s[rank - 1]


def run_open(svc, stalls):
    """Open loop: arrivals at fixed times k*tau, FIFO, frozen during stalls."""
    latencies = []
    stall_count = 0
    server_free = 0.0
    k = 0
    while k * TAU < T:
        arrival = k * TAU
        begin = arrival if arrival > server_free else server_free
        completion = service_completion(begin, svc[k], stalls)
        latencies.append(completion - arrival)
        if overlaps_any(arrival, completion, stalls):
            stall_count += 1
        server_free = completion
        k += 1
    return latencies, stall_count


def run_closed(svc, stalls):
    """Closed loop: one request outstanding; dispatch next at prior completion."""
    latencies = []
    stall_count = 0
    dispatch = 0.0
    i = 0
    while dispatch < T:
        completion = service_completion(dispatch, svc[i], stalls)
        latencies.append(completion - dispatch)
        if overlaps_any(dispatch, completion, stalls):
            stall_count += 1
        dispatch = completion
        i += 1
    return latencies, stall_count


def co_correct(closed_latencies):
    """HdrHistogram-style coordinated-omission correction: for each sample L with
    L > tau, back-fill synthetic samples L-tau, L-2*tau, ... down to > tau, and
    union with the originals."""
    corrected = list(closed_latencies)
    for L in closed_latencies:
        if L > TAU:
            v = L - TAU
            while v > TAU:
                corrected.append(v)
                v -= TAU
    return corrected


def mean_std(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var)


def z_vs_zero(xs):
    """z = mean / se, se = sample-std / sqrt(n); tests H0 mean == 0."""
    m, sd = mean_std(xs)
    se = sd / math.sqrt(len(xs))
    z = m / se if se > 0 else 0.0
    return m, se, z


def run():
    g1_x = []   # log(open_p99 / closed_p99)
    g2_x = []   # open_stall_count - closed_stall_count
    g3_x = []   # log(corrected_p99 / closed_p99)
    recovery = []
    open_p99s = []
    closed_p99s = []
    corr_p99s = []
    open_counts = []
    closed_counts = []

    for i in range(R):
        rng = random.Random(SEED + i)
        stalls = draw_stall_windows(rng)
        svc = [rng.expovariate(1.0 / MU_S) for _ in range(N_SVC)]

        open_lat, open_cnt = run_open(svc, stalls)
        closed_lat, closed_cnt = run_closed(svc, stalls)
        corr_lat = co_correct(closed_lat)

        op = percentile(open_lat, Q)
        cp = percentile(closed_lat, Q)
        rp = percentile(corr_lat, Q)

        g1_x.append(math.log(op / cp))
        g2_x.append(float(open_cnt - closed_cnt))
        g3_x.append(math.log(rp / cp))
        recovery.append((rp - cp) / (op - cp))
        open_p99s.append(op)
        closed_p99s.append(cp)
        corr_p99s.append(rp)
        open_counts.append(open_cnt)
        closed_counts.append(closed_cnt)

    g1_m, g1_se, g1_z = z_vs_zero(g1_x)
    g2_m, g2_se, g2_z = z_vs_zero(g2_x)
    g3_m, g3_se, g3_z = z_vs_zero(g3_x)

    g1_pass = g1_z >= Z_GATE
    g2_pass = g2_z >= Z_GATE
    g3_pass = g3_z >= Z_GATE

    first_fail = None
    for name, ok in (("G1", g1_pass), ("G2", g2_pass), ("G3", g3_pass)):
        if not ok:
            first_fail = name
            break
    all_pass = g1_pass and g2_pass and g3_pass

    return {
        "mechanism": "coordinated-omission",
        "proposal": 149,
        "config": {
            "seed": SEED,
            "replicates": R,
            "lam": round(LAM, 6),
            "tau": round(TAU, 6),
            "horizon_T": round(T, 6),
            "mu_service": round(MU_S, 6),
            "utilisation": round(MU_S / TAU, 6),
            "stall_D": round(D, 6),
            "n_stalls": N_STALLS,
            "D_over_tau": round(D / TAU, 6),
            "n_svc": N_SVC,
            "percentile_q": round(Q, 6),
            "z_gate": round(Z_GATE, 6),
        },
        "descriptive": {
            "mean_open_p99": round(sum(open_p99s) / R, 6),
            "mean_closed_p99": round(sum(closed_p99s) / R, 6),
            "mean_corrected_p99": round(sum(corr_p99s) / R, 6),
            "mean_open_stall_count": round(sum(open_counts) / R, 6),
            "mean_closed_stall_count": round(sum(closed_counts) / R, 6),
            "mean_open_over_closed_p99": round(
                (sum(open_p99s) / R) / (sum(closed_p99s) / R), 6),
            "mean_recovery_fraction": round(sum(recovery) / R, 6),
        },
        "gates": {
            "G1_tail_blindness": {
                "statistic": "mean log(open_p99/closed_p99)",
                "mean": round(g1_m, 6),
                "se": round(g1_se, 6),
                "z": round(g1_z, 6),
                "pass": g1_pass,
            },
            "G2_omitted_backlog": {
                "statistic": "mean (open_stall_count - closed_stall_count)",
                "mean": round(g2_m, 6),
                "se": round(g2_se, 6),
                "z": round(g2_z, 6),
                "pass": g2_pass,
            },
            "G3_correction_recovery": {
                "statistic": "mean log(corrected_p99/closed_p99)",
                "mean": round(g3_m, 6),
                "se": round(g3_se, 6),
                "z": round(g3_z, 6),
                "pass": g3_pass,
            },
        },
        "all_pass": all_pass,
        "first_failing_gate": first_fail,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # in-process double-run determinism assertion
    results2 = run()
    payload2 = json.dumps(results2, sort_keys=True, separators=(",", ":"))
    digest2 = hashlib.sha256(payload2.encode("utf-8")).hexdigest()
    assert digest == digest2, "non-deterministic: %s != %s" % (digest, digest2)

    g = results["gates"]
    print("G1 tail-blindness    : mean log(open/closed p99)=%+.4f z=%+.4f %s" % (
        g["G1_tail_blindness"]["mean"], g["G1_tail_blindness"]["z"],
        "PASS" if g["G1_tail_blindness"]["pass"] else "FAIL"))
    print("G2 omitted-backlog   : mean(open-closed stall count)=%+.4f z=%+.4f %s" % (
        g["G2_omitted_backlog"]["mean"], g["G2_omitted_backlog"]["z"],
        "PASS" if g["G2_omitted_backlog"]["pass"] else "FAIL"))
    print("G3 correction-recov  : mean log(corr/closed p99)=%+.4f z=%+.4f %s" % (
        g["G3_correction_recovery"]["mean"], g["G3_correction_recovery"]["z"],
        "PASS" if g["G3_correction_recovery"]["pass"] else "FAIL"))
    print("recovery fraction    : %.4f  (open p99 %.6f  closed p99 %.6f  corr p99 %.6f)" % (
        results["descriptive"]["mean_recovery_fraction"],
        results["descriptive"]["mean_open_p99"],
        results["descriptive"]["mean_closed_p99"],
        results["descriptive"]["mean_corrected_p99"]))
    print("all_pass =", results["all_pass"], " first_failing_gate =",
          results["first_failing_gate"])
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
