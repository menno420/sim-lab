#!/usr/bin/env python3
"""Kleinrock's conservation law: scheduling a single-server dispatch queue is
ZERO-SUM. No non-preemptive work-conserving discipline can lower the
load-weighted mean wait sum_i rho_i W_i -- every rho-weighted second shaved
off short jobs is repaid, rho-weighted, by long jobs.

Head claim (conservation): in a single-server M/G/1 queue with two job
classes, sum_i rho_i W_i is INVARIANT across FIFO, priority-to-short and
priority-to-long. Priority-to-short slashes the short-job wait W1, but the
load-weighted amount it saves reappears as extra long-job wait W2. Scheduling
reorders WHO waits; it cannot reduce the aggregate.

Method. A discrete-event single-server simulator runs each discipline on the
SAME arrival + service realization (common random numbers), so the three
disciplines are compared on identical work. Over R independent replications:
  G1  the rho-weighted wait short jobs SAVE under priority-to-short is > 0
      and large (z >= 3 vs 0)                       -- scheduling really moves wait
  G2  the conservation leak |transfer_short - transfer_long| / transfer_short
      stays below 0.10 (z >= 3 below the ceiling)   -- the saving is paid back
  G3  the same leak stays below 0.10 under a SHIFTED class mix + utilization
      (z >= 3 below the ceiling)                     -- robustness

where transfer_short = rho1*(W1_fifo - W1_short) and
      transfer_long  = rho2*(W2_short - W2_fifo);
Kleinrock's law makes these two equal, so the leak -> 0.

Grounded in Kleinrock's conservation law (L. Kleinrock, "A conservation law
for a wide class of queueing disciplines", Naval Research Logistics Quarterly
12(2), 1965; "Queueing Systems Vol II", 1976). The everyday fleet-ops lesson:
tuning dispatch priorities is zero-sum on aggregate wait -- SLA design is
about which jobs wait, not about lowering total waiting.

Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. SEED pinned; two in-process
runs asserted identical; results dict plus its sha256 printed. Stdlib only.
"""

import hashlib
import json
import math
import random
from collections import deque

SEED = 20260717

# --- base two-class M/G/1 dispatch queue ---
S1 = 1.0        # short-job mean service time
S2 = 8.0        # long-job mean service time
P1 = 0.8        # fraction of arrivals that are short jobs
RHO = 0.85      # target server utilization
N_JOBS = 20000  # jobs per replication
WARMUP = 4000   # discarded warm-up completions
R_REPS = 30     # independent replications

# --- shifted (robustness) config ---
S1_SHIFT = 1.0
S2_SHIFT = 6.0
P1_SHIFT = 0.6
RHO_SHIFT = 0.80

G2_MAX_LEAK = 0.10   # conservation leak must fall below this ceiling
SIGMA = 3.0


def loads(p1, s1, s2, rho):
    """Return (lambda_total, rho1, rho2) for a class mix + utilization."""
    mean_service = p1 * s1 + (1.0 - p1) * s2
    lam = rho / mean_service
    rho1 = lam * p1 * s1
    rho2 = lam * (1.0 - p1) * s2
    return lam, rho1, rho2


def gen_jobs(rng, lam, p1, s1, s2, n):
    """One common arrival stream: (arrival, class, service). Class 1 = short."""
    jobs = []
    t = 0.0
    for _ in range(n):
        t += rng.expovariate(lam)
        if rng.random() < p1:
            c, s = 1, rng.expovariate(1.0 / s1)
        else:
            c, s = 2, rng.expovariate(1.0 / s2)
        jobs.append((t, c, s))
    return jobs


def simulate(jobs, discipline):
    """Single non-preemptive work-conserving server. Returns (meanW1, meanW2)
    over post-warmup completions. discipline: FIFO | PRIO_SHORT | PRIO_LONG."""
    n = len(jobs)
    i = 0
    now = 0.0
    done = 0
    sum1 = 0.0
    cnt1 = 0
    sum2 = 0.0
    cnt2 = 0
    if discipline == "FIFO":
        q = deque()
        while i < n or q:
            while i < n and jobs[i][0] <= now:
                q.append(jobs[i])
                i += 1
            if not q:
                now = jobs[i][0]
                continue
            a, c, s = q.popleft()
            w = now - a
            done += 1
            if done > WARMUP:
                if c == 1:
                    sum1 += w
                    cnt1 += 1
                else:
                    sum2 += w
                    cnt2 += 1
            now += s
    else:
        prio_short = discipline == "PRIO_SHORT"
        q1 = deque()
        q2 = deque()
        while i < n or q1 or q2:
            while i < n and jobs[i][0] <= now:
                a, c, s = jobs[i]
                (q1 if c == 1 else q2).append((a, s))
                i += 1
            if not q1 and not q2:
                now = jobs[i][0]
                continue
            if prio_short:
                src, cls = (q1, 1) if q1 else (q2, 2)
            else:
                src, cls = (q2, 2) if q2 else (q1, 1)
            a, s = src.popleft()
            w = now - a
            done += 1
            if done > WARMUP:
                if cls == 1:
                    sum1 += w
                    cnt1 += 1
                else:
                    sum2 += w
                    cnt2 += 1
            now += s
    w1 = sum1 / cnt1 if cnt1 else 0.0
    w2 = sum2 / cnt2 if cnt2 else 0.0
    return w1, w2


def zstat(vals, h0):
    """One-sample z of mean(vals) against null h0."""
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0.0:
        return m, sd, float("inf")
    return m, sd, (m - h0) / (sd / math.sqrt(n))


def run_config(base_seed, p1, s1, s2, rho):
    lam, rho1, rho2 = loads(p1, s1, s2, rho)
    transfers = []
    leaks = []
    w1f = []
    w2f = []
    w1s = []
    w2s = []
    cfifo = []
    cshort = []
    clong = []
    for r in range(R_REPS):
        rng = random.Random(base_seed + r)
        jobs = gen_jobs(rng, lam, p1, s1, s2, N_JOBS)
        w1_f, w2_f = simulate(jobs, "FIFO")
        w1_s, w2_s = simulate(jobs, "PRIO_SHORT")
        w1_l, w2_l = simulate(jobs, "PRIO_LONG")
        transfer_short = rho1 * (w1_f - w1_s)
        transfer_long = rho2 * (w2_s - w2_f)
        residual = transfer_short - transfer_long
        leak = abs(residual) / transfer_short if transfer_short > 0 else float("inf")
        transfers.append(transfer_short)
        leaks.append(leak)
        w1f.append(w1_f)
        w2f.append(w2_f)
        w1s.append(w1_s)
        w2s.append(w2_s)
        cfifo.append(rho1 * w1_f + rho2 * w2_f)
        cshort.append(rho1 * w1_s + rho2 * w2_s)
        clong.append(rho1 * w1_l + rho2 * w2_l)
    return {
        "lam": lam,
        "rho1": rho1,
        "rho2": rho2,
        "transfers": transfers,
        "leaks": leaks,
        "w1f": w1f,
        "w2f": w2f,
        "w1s": w1s,
        "w2s": w2s,
        "cfifo": cfifo,
        "cshort": cshort,
        "clong": clong,
    }


def rnd(x):
    return round(x, 6)


def mean(xs):
    return sum(xs) / len(xs)


def run():
    base = run_config(SEED, P1, S1, S2, RHO)
    shift = run_config(SEED + 100000, P1_SHIFT, S1_SHIFT, S2_SHIFT, RHO_SHIFT)

    t_mean, t_sd, t_z = zstat(base["transfers"], 0.0)
    g1 = t_mean > 0.0 and t_z >= SIGMA

    l_mean, l_sd, l_z_raw = zstat(base["leaks"], G2_MAX_LEAK)
    l_z = -l_z_raw
    g2 = l_mean < G2_MAX_LEAK and l_z >= SIGMA

    ls_mean, ls_sd, ls_z_raw = zstat(shift["leaks"], G2_MAX_LEAK)
    ls_z = -ls_z_raw
    g3 = ls_mean < G2_MAX_LEAK and ls_z >= SIGMA

    all_pass = g1 and g2 and g3
    order = [("G1", g1), ("G2", g2), ("G3", g3)]
    first_fail = next((name for name, ok in order if not ok), None)

    results = {
        "seed": SEED,
        "n_jobs": N_JOBS,
        "warmup": WARMUP,
        "reps": R_REPS,
        "s1": S1,
        "s2": S2,
        "p1": P1,
        "rho": RHO,
        "lam": rnd(base["lam"]),
        "rho1": rnd(base["rho1"]),
        "rho2": rnd(base["rho2"]),
        "w1_fifo": rnd(mean(base["w1f"])),
        "w1_prio_short": rnd(mean(base["w1s"])),
        "w2_fifo": rnd(mean(base["w2f"])),
        "w2_prio_short": rnd(mean(base["w2s"])),
        "conserved_fifo": rnd(mean(base["cfifo"])),
        "conserved_prio_short": rnd(mean(base["cshort"])),
        "conserved_prio_long": rnd(mean(base["clong"])),
        "transfer_short_mean": rnd(t_mean),
        "transfer_short_z": rnd(t_z),
        "leak_mean": rnd(l_mean),
        "leak_z": rnd(l_z),
        "shift_p1": P1_SHIFT,
        "shift_s2": S2_SHIFT,
        "shift_rho": RHO_SHIFT,
        "shift_leak_mean": rnd(ls_mean),
        "shift_leak_z": rnd(ls_z),
        "g1_swing_real": g1,
        "g2_conservation": g2,
        "g3_robust": g3,
        "all_pass": all_pass,
        "first_failing_gate": first_fail,
    }
    return results


def main():
    results = run()
    again = run()
    assert results == again, "non-deterministic: in-process double run diverged"

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print("Kleinrock conservation law verifier -- single-server M/G/1, common random numbers")
    print(f"  swing : W1_fifo={results['w1_fifo']:.6f} -> W1_prio_short={results['w1_prio_short']:.6f}  (short jobs jump the queue)")
    print(f"          W2_fifo={results['w2_fifo']:.6f} -> W2_prio_short={results['w2_prio_short']:.6f}  (long jobs pay it back)")
    print(f"  conserved sum(rho_i W_i): fifo={results['conserved_fifo']:.6f} prio_short={results['conserved_prio_short']:.6f} prio_long={results['conserved_prio_long']:.6f}")
    print(f"  G1 transfer_short_mean={results['transfer_short_mean']:+.6f}  z={results['transfer_short_z']:+.6f}")
    print(f"  G2 leak_mean={results['leak_mean']:.6f}  z={results['leak_z']:+.6f}  (ceiling 0.10)")
    print(f"  G3 shift_leak_mean={results['shift_leak_mean']:.6f}  z={results['shift_leak_z']:+.6f}  (ceiling 0.10)")
    print(f"  gates : G1={results['g1_swing_real']}  G2={results['g2_conservation']}  G3={results['g3_robust']}  all_pass={results['all_pass']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
