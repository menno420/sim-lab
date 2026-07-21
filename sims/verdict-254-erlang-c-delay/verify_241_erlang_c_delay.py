#!/usr/bin/env python3
"""PROPOSAL 241 - Erlang-C delay probability for an M/M/c pool of agents.

Claim (exact). Model a pool of c parallel agents as an M/M/c queue: Poisson
arrivals at rate lambda, exponential service at rate mu per agent, offered load
a = lambda/mu Erlangs (require a < c for stability), utilization rho = a/c. The
probability that an arriving task must WAIT -- it finds all c agents busy -- is
EXACTLY the Erlang-C formula

        C(c,a) = [ a^c/c! * c/(c-a) ]
                 / [ sum_{k=0}^{c-1} a^k/k!  +  a^c/c! * c/(c-a) ].

Headline exact rationals: C(2,1) = 1/3, C(10,6) = 1458/14393 (both
computed exactly with fractions.Fraction; see G1). This REFUTES two naive
foils, each on the same (c=2, a=1) Monte-Carlo sample:
  (F1) "delay probability = utilization rho = a/c" -- at c=2, a=1 that gives
       1/2, but the true delay probability is 1/3;
  (F2) "delay = blocking, i.e. Erlang-C = Erlang-B" -- Erlang-B B(2,1) = 1/5,
       not 1/3, so the loss (blocked-calls-cleared) probability is a different
       object from the delay (queued) probability.

SEED = 20260717. build_results() is a pure function of SEED and the module
constants (each Monte-Carlo run consumes its own random.Random(SEED)-derived
stream in a fixed event order; no wall-clock / PID / unordered-set iteration
enters the hashed payload), so an in-process double-run and a separate
re-invocation are byte-identical; results_sha256 is the sha256 of the canonical
results dict. Exact rationals are serialized via str(Fraction) and every float
(z-values, p_hat) is formatted as a fixed-precision f"{v:.10f}" string so the
hashed bytes are stable.

Four gates, each in its own direction:
  G1 EXACT      - three independent exact routes to C(c,a) agree bit-for-bit
                  (fractions.Fraction): the direct Erlang-C sum, the Erlang-B
                  bridge C = B/(1 - rho(1-B)), and the birth-death stationary
                  reconstruction. error_count must be 0.
  G2 MC AGREE   - a correct discrete-event M/M/c simulator's measured wait
                  fraction (by PASTA) agrees with C(c,a) at |z| < Z_ACCEPT for
                  (c=2, a=1 -> 1/3) and (c=10, a=6 -> C(10,6)). To keep the
                  binomial standard error honest under the queue's arrival-to-
                  arrival autocorrelation, the estimator records the wait-status
                  of every THIN-th post-warmup arrival (thinned arrival epochs
                  still satisfy PASTA, so the estimate stays unbiased for C while
                  consecutive recorded samples decorrelate); MC_N=200000 such
                  measured arrivals per run.
  G3 INVARIANCE - time-scale invariance: C depends on (c, a=lambda/mu) only.
                  Exactly, C(2,1) is identical for (lambda,mu) in
                  {(1,1),(3,3),(7,7)}; and the DES at (3,3) and (7,7) with c=2
                  both agree with 1/3 at |z| < Z_ACCEPT.
  G4 FALSIFY    - on the SAME (c=2,a=1) MC sample, the naive "delay = rho = 1/2"
                  and "delay = Erlang-B = 1/5" beliefs are both rejected at
                  |z| >= Z_REJECT; and exactly C(2,1) = 1/3 != 1/5 = B(2,1).

Stdlib only: json, hashlib, math, random, fractions.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# ---- gate constants -------------------------------------------------------
# Exact identity panel: (c, a) with a < c and a rational.
EXACT_PANEL = [
    (2, Fraction(1)),
    (3, Fraction(2)),
    (5, Fraction(3)),
    (10, Fraction(6)),
    (10, Fraction(17, 2)),
    (20, Fraction(15)),
]
WARMUP = 10_000            # arrivals discarded before measurement begins
MC_N = 200_000            # measured (thinned) arrivals per Monte-Carlo run
THIN = 50                 # record every THIN-th post-warmup arrival (decorrelation)
Z_ACCEPT = 3.0
Z_REJECT = 6.0


# ---- exact Erlang core (all fractions.Fraction) ---------------------------
def erlang_b(c, a):
    """Erlang-B loss probability B(c,a) via the stable recursion
    B(0,a)=1, B(k,a)=a*B(k-1,a)/(k + a*B(k-1,a)). Returns a Fraction."""
    B = Fraction(1)
    for k in range(1, c + 1):
        B = a * B / (k + a * B)
    return B


def erlang_c_direct(c, a):
    """Erlang-C delay probability, direct definition. Requires a < c.

        tail = a^c/c! * c/(c-a)
        S    = sum_{k=0}^{c-1} a^k/k!
        C    = tail / (S + tail)
    """
    if not a < c:
        raise ValueError("stability requires a < c")
    tail = a ** c / math.factorial(c) * Fraction(c, c - a)
    S = sum((a ** k) / math.factorial(k) for k in range(0, c))
    return tail / (S + tail)


def erlang_c_from_b(c, a):
    """Erlang-C from Erlang-B via the exact bridge C = B/(1 - rho(1-B)),
    rho = a/c. Requires a < c."""
    if not a < c:
        raise ValueError("stability requires a < c")
    B = erlang_b(c, a)
    rho = a / c
    return B / (1 - rho * (1 - B))


def erlang_c_stationary(c, a):
    """Erlang-C reconstructed from the M/M/c birth-death stationary
    distribution. Unnormalized weights w_n = a^n/n! for n <= c and, for the
    geometric tail n >= c, sum_{n>=c} w_n = a^c/c! * 1/(1-rho). Then
    P(wait) = P(n >= c) = tail / (head + tail), all exact Fraction."""
    if not a < c:
        raise ValueError("stability requires a < c")
    rho = a / c
    head = sum((a ** n) / math.factorial(n) for n in range(0, c))  # n = 0..c-1
    tail = (a ** c) / math.factorial(c) * (Fraction(1) / (1 - rho))
    return tail / (head + tail)


# ---- discrete-event M/M/c simulator ---------------------------------------
def simulate_mmc(c, lam, mu, seed, warmup, measured, thin=THIN):
    """Correct FIFO discrete-event M/M/c simulator. c servers, exponential
    interarrivals ~ Exp(lam) and services ~ Exp(mu). On each arrival the number
    in system (in-service + waiting) is inspected BEFORE the task is admitted;
    "must wait" is the event that this count is >= c (all servers busy). By
    PASTA the long-run wait frequency estimates C(c, a=lam/mu).

    The first `warmup` arrivals are discarded to clear the empty-start
    transient. Thereafter the wait-status of every `thin`-th arrival is
    RECORDED (thinned arrival epochs still satisfy PASTA, so the estimate stays
    unbiased for C); recording continues until `measured` samples are
    collected. Thinning spaces the recorded samples out over many arrivals so
    the queue's arrival-to-arrival autocorrelation decays between them and the
    binomial standard error sqrt(p0(1-p0)/measured) is an honest scale for the
    estimator's spread.

    Returns (wait_count, measured_count)."""
    import heapq
    rng = random.Random(seed)
    expovariate = rng.expovariate
    heappush = heapq.heappush
    heappop = heapq.heappop
    departures = []            # min-heap of in-service completion times (<= c)
    q = 0                      # number waiting in the FIFO queue
    next_arrival = expovariate(lam)
    arrivals_seen = 0          # arrivals past warmup (thinning index)
    seen_total = 0             # all arrivals (for warmup gate)
    wait_count = 0
    measured_count = 0
    while measured_count < measured:
        if departures and departures[0] <= next_arrival:
            # ---- departure event: a server frees ----
            clock = heappop(departures)
            if q > 0:
                q -= 1
                heappush(departures, clock + expovariate(mu))
        else:
            # ---- arrival event ----
            clock = next_arrival
            busy = len(departures)
            seen_total += 1
            if seen_total > warmup:
                arrivals_seen += 1
                if arrivals_seen % thin == 0:          # record every thin-th
                    measured_count += 1
                    if busy + q >= c:                  # all servers busy: waits
                        wait_count += 1
            # admit: free server -> immediate service, else join the queue
            if busy < c:
                heappush(departures, clock + expovariate(mu))
            else:
                q += 1
            next_arrival = clock + expovariate(lam)
    return wait_count, measured_count


def _z(p_hat, p0, n):
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (p_hat - p0) / se


def _f(v):
    """Fixed-precision float -> stable string for the hashed payload."""
    return f"{v:.10f}"


# ---- gates ----------------------------------------------------------------
def gate1_exact():
    error_count = 0
    rows = []
    exact_map = {}
    for c, a in EXACT_PANEL:
        cd = erlang_c_direct(c, a)
        cb = erlang_c_from_b(c, a)
        cs = erlang_c_stationary(c, a)
        agree = (cd == cb == cs)
        if not agree:
            error_count += 1
        key = f"C_{c}_{a}".replace("/", "_over_")
        exact_map[key] = str(cd)
        rows.append({
            "c": c,
            "a": str(a),
            "C_direct": str(cd),
            "C_from_b": str(cb),
            "C_stationary": str(cs),
            "three_routes_equal": agree,
        })
    ok = (error_count == 0)
    return ok, {
        "panel": rows,
        "C_2_1": str(erlang_c_direct(2, Fraction(1))),
        "C_10_6": str(erlang_c_direct(10, Fraction(6))),
        "exact_by_config": exact_map,
        "error_count": error_count,
        "pass_if": "error_count == 0 (direct == from_b == stationary, exact)",
    }


def gate2_mc_agreement(sample_c2):
    rows = []
    all_ok = True
    # headline 1 uses the shared (c=2, a=1) sample (also consumed by G4).
    p0_1 = float(erlang_c_direct(2, Fraction(1)))            # 1/3
    p0_2 = float(erlang_c_direct(10, Fraction(6)))           # C(10,6)
    configs = [
        (2, 1.0, 1.0, p0_1, Fraction(1), sample_c2),
        (10, 6.0, 1.0, p0_2, Fraction(6),
         simulate_mmc(10, 6.0, 1.0, SEED, WARMUP, MC_N)),
    ]
    for c, lam, mu, p0, a, sample in configs:
        wait_count, n = sample
        p_hat = wait_count / n
        z = _z(p_hat, p0, n)
        ok = abs(z) < Z_ACCEPT
        all_ok = all_ok and ok
        rows.append({
            "c": c,
            "lambda": _f(lam),
            "mu": _f(mu),
            "a": str(a),
            "measured": n,
            "wait_count": wait_count,
            "p_hat": _f(p_hat),
            "C_exact": str(erlang_c_direct(c, a)),
            "C_float": _f(p0),
            "z": _f(z),
            "z_accept": Z_ACCEPT,
            "ok": ok,
        })
    return all_ok, {
        "runs": rows,
        "pass_if": "abs(z) < Z_ACCEPT for both headline runs",
    }


def gate3_invariance():
    # (i) EXACT time-scale invariance: C(2,1) identical for (lambda,mu) giving a=1.
    exact_vals = []
    for lam, mu in [(1, 1), (3, 3), (7, 7)]:
        a = Fraction(lam, mu)                 # = 1
        exact_vals.append(erlang_c_direct(2, a))
    exact_identical = (exact_vals[0] == exact_vals[1] == exact_vals[2])
    mismatch_count = 0 if exact_identical else 1

    # (ii) MC invariance: DES at (3,3) and (7,7), c=2, both agree with 1/3.
    p0 = float(erlang_c_direct(2, Fraction(1)))
    mc_rows = []
    mc_ok = True
    for lam, mu in [(3.0, 3.0), (7.0, 7.0)]:
        wait_count, n = simulate_mmc(2, lam, mu, SEED, WARMUP, MC_N)
        p_hat = wait_count / n
        z = _z(p_hat, p0, n)
        ok = abs(z) < Z_ACCEPT
        if not ok:
            mismatch_count += 1
        mc_ok = mc_ok and ok
        mc_rows.append({
            "lambda": _f(lam),
            "mu": _f(mu),
            "a": "1",
            "measured": n,
            "wait_count": wait_count,
            "p_hat": _f(p_hat),
            "z": _f(z),
            "z_accept": Z_ACCEPT,
            "ok": ok,
        })
    ok = exact_identical and mc_ok
    return ok, {
        "exact_identical_C_2_1": exact_identical,
        "exact_value": str(exact_vals[0]),
        "mc_runs": mc_rows,
        "mismatch_count": mismatch_count,
        "pass_if": "exact C(2,1) identical across time scales AND both DES |z| < Z_ACCEPT",
    }


def gate4_falsify(sample_c2):
    wait_count, n = sample_c2
    p_hat = wait_count / n

    # (F1) naive "delay = utilization rho = 1/2" -- reject on the same sample.
    z_naive_rho = _z(p_hat, 0.5, n)
    rho_rejected = abs(z_naive_rho) >= Z_REJECT

    # (F2) naive "Erlang-C = Erlang-B". Exact: C(2,1) != B(2,1).
    C21 = erlang_c_direct(2, Fraction(1))
    B21 = erlang_b(2, Fraction(1))
    exact_distinct = (C21 != B21)
    z_naive_b = _z(p_hat, float(B21), n)          # B(2,1) = 1/5
    b_rejected = abs(z_naive_b) >= Z_REJECT

    ok = rho_rejected and exact_distinct and b_rejected
    return ok, {
        "naive_rho": {
            "claim": "delay probability == utilization rho == 1/2",
            "p_hat": _f(p_hat),
            "p_naive": _f(0.5),
            "z_naive_rho": _f(z_naive_rho),
            "z_reject": Z_REJECT,
            "rejected": rho_rejected,
        },
        "naive_erlang_b": {
            "claim": "delay == blocking, i.e. Erlang-C == Erlang-B",
            "C_2_1": str(C21),
            "B_2_1": str(B21),
            "exact_distinct": exact_distinct,
            "p_hat": _f(p_hat),
            "p_naive": _f(float(B21)),
            "z_naive_b": _f(z_naive_b),
            "z_reject": Z_REJECT,
            "rejected": b_rejected,
        },
        "pass_if": "abs(z_rho) >= Z_REJECT and C(2,1) != B(2,1) and abs(z_b) >= Z_REJECT",
    }


def build_results():
    # shared (c=2, a=1) MC sample, consumed by G2 headline-1 and G4.
    sample_c2 = simulate_mmc(2, 1.0, 1.0, SEED, WARMUP, MC_N)

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample_c2)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample_c2)

    gates = {
        "G1_exact_identity": {"name": "direct == from_b == stationary, exact Fraction",
                              "ok": g1_ok, **g1},
        "G2_montecarlo_agreement": {"name": "DES wait fraction agrees with Erlang-C (PASTA)",
                                    "ok": g2_ok, **g2},
        "G3_invariance": {"name": "time-scale invariance: C depends on (c,a) only",
                          "ok": g3_ok, **g3},
        "G4_falsifiability": {"name": "naive rho=1/2 and Erlang-B=1/5 both rejected",
                              "ok": g4_ok, **g4},
    }
    order = ["G1_exact_identity", "G2_montecarlo_agreement",
             "G3_invariance", "G4_falsifiability"]
    first_failing = next((g for g in order if not gates[g]["ok"]), None)
    all_pass = first_failing is None

    return {
        "claim": ("erlang_c_delay: for an M/M/c pool (Poisson arrivals rate "
                  "lambda, exp service rate mu per agent, offered load "
                  "a=lambda/mu < c, rho=a/c) the probability an arriving task "
                  "must WAIT is exactly Erlang-C C(c,a); C(2,1)=1/3, "
                  "C(10,6)=1458/14393; refutes delay=rho and "
                  "Erlang-C=Erlang-B"),
        "seed": SEED,
        "params": {
            "exact_panel": [[c, str(a)] for c, a in EXACT_PANEL],
            "warmup": WARMUP,
            "mc_n": MC_N,
            "z_accept": Z_ACCEPT,
            "z_reject": Z_REJECT,
        },
        "exact": {
            "C_2_1": str(erlang_c_direct(2, Fraction(1))),
            "C_10_6": str(erlang_c_direct(10, Fraction(6))),
        },
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    import sys
    selfcheck = "--selfcheck" in sys.argv
    results = build_results()
    c1 = canonical(results)
    c2 = canonical(build_results())          # independent in-process recompute
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    if selfcheck:
        print("SELFCHECK: byte-identical")
        print("results_sha256: " + digest)
        raise SystemExit(0 if results["all_gates_pass"] else 1)
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
