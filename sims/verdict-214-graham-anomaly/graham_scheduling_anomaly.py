#!/usr/bin/env python3
"""Empirical + exact validation of Graham's multiprocessing timing anomaly.

Graham (1969): greedy non-preemptive LIST SCHEDULING of precedence-constrained
jobs on m identical machines is NON-monotone in its inputs. Relaxing a
constraint -- adding a machine, shortening every job, or removing a precedence
edge -- can each STRICTLY INCREASE the makespan. Yet the greedy makespan is
provably at most (2 - 1/m) times the true optimum.

This file runs three PRE-REGISTERED gates and emits a byte-reproducible
determinism digest (whole-dict sha256, no self-field, stdout only):

  G1  surprise      REMOVE-ONE-EDGE non-monotonicity, wants HIGH z (null rate=0)
  G2  robustness    same effect under ADD-A-MACHINE and SHORTEN-ALL, z>=3 each
  G3  exactly-true  Fraction-exact (2 - 1/m) bound holds with ZERO violations

Determinism: SEED is fixed; each gate derives from its own freshly-seeded
random.Random(SEED + offset) so the run is byte-reproducible and gate streams
are independent (retuning one gate's N does not perturb another gate's draws).

stdlib only: random, math, hashlib, json, fractions, functools, itertools.
"""

import random
import math
import hashlib
import json
from fractions import Fraction
from functools import lru_cache

SEED = 20260717

# Sample sizes (pre-registered; see module docstring for the power targets).
N1_REMOVE_EDGE = 60000    # G1: eligible DAGs (p~0.09  ->  z1 ~ 70)
N2_ROBUST = 500000        # G2: rare levers (p~1e-4    ->  z ~ 7-8 each)
K_BOUND = 20000           # G3: small exact-optimum instances


# ---------------------------------------------------------------------------
# 1. Greedy non-preemptive list scheduling (event-driven, exact integers).
#    [VERBATIM from validated prototype -- do not alter.]
# ---------------------------------------------------------------------------
def list_schedule(times, prec, m, order):
    """Greedy non-preemptive list scheduling on m identical machines.

    times : dict job -> int duration
    prec  : dict job -> set of predecessors that must FULLY complete first
    m     : number of identical machines
    order : priority list (list of jobs); earliest = highest priority

    Whenever a machine is idle it immediately takes the earliest-in-`order`
    job whose predecessors have all completed and that is not running/done.
    Returns the integer makespan (max completion time).
    """
    completed = {}          # job -> completion time
    running = []            # list of [finish_time, job]
    remaining = set(order)  # jobs not yet started
    free = m
    t = 0

    while remaining or running:
        # Assign as many ready jobs as possible at the current time t.
        progressed = True
        while free > 0 and progressed:
            progressed = False
            for j in order:
                if j not in remaining:
                    continue
                preds = prec.get(j, ())
                if all((p in completed and completed[p] <= t) for p in preds):
                    running.append([t + times[j], j])
                    remaining.discard(j)
                    free -= 1
                    progressed = True
                    break

        if running:
            # Advance to the next completion event.
            t = min(f for f, _ in running)
            still = []
            for f, j in running:
                if f == t:
                    completed[j] = f
                    free += 1
                else:
                    still.append([f, j])
            running = still
        elif remaining:
            # No machine can make progress though jobs remain: only possible
            # with a cyclic prec (never happens for a valid DAG). Guard anyway.
            break

    return max(completed.values()) if completed else 0


# ---------------------------------------------------------------------------
# 2. True optimum makespan for SMALL instances (allows deliberate idling).
#    Non-delay (greedy) schedules do NOT always contain the makespan optimum
#    under precedence, so the search must be allowed to leave machines idle.
#    [VERBATIM from validated prototype -- do not alter.]
# ---------------------------------------------------------------------------
def optimal_makespan(times, prec, m):
    jobs = tuple(sorted(times))
    preds = {j: frozenset(prec.get(j, ())) for j in jobs}
    all_jobs = frozenset(jobs)
    total_work = sum(times.values())

    # Critical-path length of each job (longest predecessor chain incl. self),
    # used for a simple lower bound to prune.
    cp = {}
    for j in sorted(jobs):  # jobs sorted; preds are < j by construction, but be safe
        base = max((cp[p] for p in preds[j]), default=0)
        cp[j] = base + times[j]

    best = [total_work + 1]  # sequential upper bound

    @lru_cache(maxsize=None)
    def solve(completed_items, running_items):
        # completed_items: frozenset of (job, completion_time)
        # running_items:   frozenset of (job, finish_time), finish_time > current t
        completed = dict(completed_items)
        running = dict(running_items)

        done_makespan = max(completed.values()) if completed else 0

        if len(completed) == len(jobs) and not running:
            return done_makespan

        # current time = max completion among completed that are <= all running?
        # We advance an explicit clock: t is the latest event we have processed.
        t = done_makespan
        if running:
            # We are at the moment right after the most recent completion; the
            # current decision time is that instant. Determine it as the max of
            # completed times (jobs just finished) -- but a machine could also be
            # free from the very start. Use t = current decision time = the time
            # at which we are choosing, which is the max completed time, or 0.
            pass
        # Decision time: the instant we are standing at. Everything in completed
        # has completion_time <= t_now; everything running finishes > t_now.
        t_now = done_makespan
        # If nothing completed yet, t_now = 0.
        if not completed:
            t_now = 0

        free = m - len(running)

        ready = [
            j for j in jobs
            if j not in completed and j not in running
            and all((p in completed and completed[p] <= t_now) for p in preds[j])
        ]

        # Lower bound for pruning.
        remaining_work = total_work - sum(times[j] for j in completed) \
            - sum((times[j] - (fin - t_now)) for j, fin in running.items())
        lb = max(
            t_now + (remaining_work + m - 1) // m if m else t_now,
            max((cp[j] for j in jobs if j not in completed), default=t_now),
            max((fin for fin in running.values()), default=t_now),
        )
        if lb >= best[0]:
            return best[0]  # prune

        # Enumerate choices: any subset S of ready with |S| <= free.
        # If nothing is running, S must be non-empty (else no progress).
        from itertools import combinations
        max_start = min(free, len(ready))

        subsets = []
        low = 0 if running else 1
        for k in range(low, max_start + 1):
            for combo in combinations(ready, k):
                subsets.append(combo)
        if not subsets:
            # Nothing to start and something running: just advance time.
            subsets = [()]

        result = best[0]
        for S in subsets:
            new_running = dict(running)
            for j in S:
                new_running[j] = t_now + times[j]
            # Advance to next completion event.
            next_t = min(new_running.values())
            new_completed = dict(completed)
            still = {}
            for j, fin in new_running.items():
                if fin == next_t:
                    new_completed[j] = fin
                else:
                    still[j] = fin
            val = solve(
                frozenset(new_completed.items()),
                frozenset(still.items()),
            )
            if val < result:
                result = val
                if result < best[0]:
                    best[0] = result
        return result

    solve.cache_clear()
    return solve(frozenset(), frozenset())


# ---------------------------------------------------------------------------
# 3. Random instance generator: random DAG + integer times in [1..9].
#    [VERBATIM from validated prototype -- do not alter.]
# ---------------------------------------------------------------------------
def gen_instance(rng, n, m, edge_p=0.25):
    times = {j: rng.randint(1, 9) for j in range(n)}
    prec = {j: set() for j in range(n)}
    for j in range(n):
        for i in range(j):          # only earlier jobs -> acyclic
            if rng.random() < edge_p:
                prec[j].add(i)
    order = list(range(n))
    rng.shuffle(order)
    return times, prec, order


def _shorten(times):
    return {j: max(1, d - 1) for j, d in times.items()}


def _copy_prec(prec):
    return {j: set(s) for j, s in prec.items()}


def _stat(hits, N):
    """Binomial point estimate + one-sample z against null rate = 0.

    p_hat = hits/N ; SE = sqrt(p_hat(1-p_hat)/N) ; z = p_hat/SE.
    """
    p = hits / N if N else 0.0
    se = math.sqrt(p * (1 - p) / N) if N and 0 < p < 1 else 0.0
    if se > 0:
        z = p / se
    else:
        z = float('inf') if p > 0 else 0.0
    return p, se, z


# ---------------------------------------------------------------------------
# G1 -- REMOVE-ONE-EDGE anomaly (surprise; wants HIGH z, null rate = 0).
#   Over N1 random precedence DAGs (each with at least one edge), deleting one
#   random precedence edge -- a RELAXATION of the constraints -- STRICTLY
#   INCREASES the greedy list-schedule makespan at fixed m and fixed order.
#   A monotone-in-constraints scheduler would never do this: null rate = 0.
# ---------------------------------------------------------------------------
def gate_g1_remove_edge(N1):
    rng = random.Random(SEED)   # documented: G1 stream = Random(SEED)
    hits = 0
    collected = 0               # eligible DAGs seen (those with >=1 edge)
    while collected < N1:
        n = rng.randint(6, 12)
        m = rng.randint(2, 4)
        times, prec, order = gen_instance(rng, n, m)
        edges = [(j, i) for j in prec for i in prec[j]]
        if not edges:
            continue            # cannot remove an edge; redraw (not counted)
        collected += 1
        base = list_schedule(times, prec, m, order)
        j, i = edges[rng.randrange(len(edges))]
        prec2 = _copy_prec(prec)
        prec2[j].discard(i)
        after = list_schedule(times, prec2, m, order)
        if after > base:
            hits += 1
    return hits, N1


# ---------------------------------------------------------------------------
# G2 -- ADD-A-MACHINE and SHORTEN-ALL anomalies (robustness / two more levers).
#   Same non-monotonicity under two independent relaxations, both rare:
#     (i)  ADD-A-MACHINE : list_schedule(...,m+1) > list_schedule(...,m)
#     (ii) SHORTEN-ALL   : list_schedule(t-1,...,m) > list_schedule(t,...,m)
#   Also captures the FIRST add-a-machine witness for reporting.
# ---------------------------------------------------------------------------
def gate_g2_robust(N2):
    rng = random.Random(SEED + 1)   # documented: G2 stream = Random(SEED+1)
    add_hits = 0
    shorten_hits = 0
    witness = None
    for _ in range(N2):
        n = rng.randint(6, 12)
        m = rng.randint(2, 4)
        times, prec, order = gen_instance(rng, n, m)

        base = list_schedule(times, prec, m, order)

        # (i) add a machine, fixed order.
        more = list_schedule(times, prec, m + 1, order)
        if more > base:
            add_hits += 1
            if witness is None:
                witness = (dict(times), _copy_prec(prec), list(order),
                           m, base, more)

        # (ii) shorten every job by 1 (floor 1), fixed m/order.
        st = list_schedule(_shorten(times), prec, m, order)
        if st > base:
            shorten_hits += 1

    return add_hits, shorten_hits, N2, witness


# ---------------------------------------------------------------------------
# G3 -- EXACT (2 - 1/m) BOUND (exactly-true; wants ZERO violations).
#   Over K small instances (n <= 6, m in {2,3}), compare the worst greedy list
#   makespan (over several priority orders) against the exhaustively-computed
#   true optimum, using exact Fraction arithmetic. The closed-form bound
#   Fraction(2m-1, m) = 2 - 1/m must hold for every instance.
# ---------------------------------------------------------------------------
def gate_g3_bound(K):
    rng = random.Random(SEED + 2)   # documented: G3 stream = Random(SEED+2)
    checked = 0
    violations = 0
    max_ratio = Fraction(0, 1)
    max_ratio_info = None
    n_nontrivial = 0

    for _ in range(K):
        n = rng.randint(3, 6)       # n <= 6 keeps the branch search fast
        m = rng.randint(2, 3)       # m in {2,3}
        times, prec, order = gen_instance(rng, n, m)

        opt = optimal_makespan(times, prec, m)
        if opt == 0:
            continue

        # Worst greedy makespan over several priority orders -- the most
        # meaningful (and most stringent) test of the bound.
        worst = 0
        worst_order = None
        for _k in range(4):
            o = list(range(n))
            rng.shuffle(o)
            ls = list_schedule(times, prec, m, o)
            if ls > worst:
                worst = ls
                worst_order = o

        checked += 1
        ratio = Fraction(worst, opt)
        bound = Fraction(2 * m - 1, m)
        if ratio > bound:
            violations += 1
        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_info = (dict(times), _copy_prec(prec), worst_order,
                              m, worst, opt)
        if ratio > 1:
            n_nontrivial += 1

    return {
        "checked": checked,
        "violations": violations,
        "max_ratio": max_ratio,
        "max_ratio_info": max_ratio_info,
        "n_nontrivial": n_nontrivial,
    }


# ---------------------------------------------------------------------------
# Internal sanity check for optimal_makespan on tiny known cases (cheap).
# ---------------------------------------------------------------------------
def _validate_optimum():
    checks = []
    # two independent unit jobs on 2 machines -> 1
    checks.append(optimal_makespan({0: 1, 1: 1}, {0: set(), 1: set()}, 2) == 1)
    # chain 0->1->2 unit -> 3 on any m
    checks.append(optimal_makespan({0: 1, 1: 1, 2: 1},
                                   {0: set(), 1: {0}, 2: {1}}, 3) == 3)
    # 4 unit jobs on 2 machines, no prec -> 2
    checks.append(optimal_makespan({0: 1, 1: 1, 2: 1, 3: 1},
                                   {i: set() for i in range(4)}, 2) == 2)
    # 3 jobs times 2,2,2 on 2 machines -> 4
    checks.append(optimal_makespan({0: 2, 1: 2, 2: 2},
                                   {i: set() for i in range(3)}, 2) == 4)
    # opt never exceeds any list schedule
    rng = random.Random(999)
    ok = True
    for _ in range(300):
        n = rng.randint(3, 6)
        m = rng.randint(2, 3)
        times, prec, order = gen_instance(rng, n, m)
        opt = optimal_makespan(times, prec, m)
        ls = list_schedule(times, prec, m, order)
        if opt > ls:
            ok = False
            break
    checks.append(ok)
    return all(checks), checks


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("GRAHAM MULTIPROCESSING TIMING ANOMALY -- PRE-REGISTERED VALIDATION")
    print("SEED =", SEED)
    print("=" * 72)

    ok, checks = _validate_optimum()
    print("\n[validate] optimal_makespan tiny-case checks:", checks, "->", ok)
    assert ok, "optimal_makespan failed internal validation"

    # ---- G1 -----------------------------------------------------------------
    print(f"\n[running] G1 remove-one-edge, N1={N1_REMOVE_EDGE} eligible DAGs ...")
    g1_count, g1_N = gate_g1_remove_edge(N1_REMOVE_EDGE)
    g1_p, g1_se, g1_z = _stat(g1_count, g1_N)
    g1_pass = g1_z >= 10.0
    print("\n--- G1  SURPRISE: remove-one-edge  list(prec-e) > list(prec) -------")
    print(f"    null hypothesis (monotone in constraints): rate = 0")
    print(f"    count = {g1_count}   N1 = {g1_N}")
    print(f"    p_hat = {g1_p:.8f}   SE = {g1_se:.10f}")
    print(f"    z1    = {g1_z:.6f}   (want z1 >= 10; DIRECTION: HIGH z)")
    print(f"    PASS  = {g1_pass}")

    # ---- G2 -----------------------------------------------------------------
    print(f"\n[running] G2 add-a-machine + shorten-all, N2={N2_ROBUST} ...")
    g2_add, g2_short, g2_N, witness = gate_g2_robust(N2_ROBUST)
    ga_p, ga_se, ga_z = _stat(g2_add, g2_N)
    gs_p, gs_se, gs_z = _stat(g2_short, g2_N)
    g2_add_pass = ga_z >= 3.0
    g2_short_pass = gs_z >= 3.0
    print("\n--- G2  ROBUSTNESS: two independent relaxations (DIRECTION: HIGH z) -")
    print("  (i) ADD-A-MACHINE  list(m+1) > list(m), fixed order:")
    print(f"      count = {g2_add}   N2 = {g2_N}")
    print(f"      p_hat = {ga_p:.8f}   SE = {ga_se:.10f}   z = {ga_z:.6f}")
    print(f"      PASS  = {g2_add_pass}   (want z >= 3)")
    print("  (ii) SHORTEN-ALL  list(t-1) > list(t), fixed m/order:")
    print(f"      count = {g2_short}   N2 = {g2_N}")
    print(f"      p_hat = {gs_p:.8f}   SE = {gs_se:.10f}   z = {gs_z:.6f}")
    print(f"      PASS  = {g2_short_pass}   (want z >= 3)")

    if witness is None:
        raise SystemExit("G2 produced no add-a-machine witness (unexpected)")
    w_times, w_prec, w_order, w_m, w_ms_m, w_ms_m1 = witness
    print("\n  ADD-A-MACHINE WITNESS (first found in G2 stream):")
    print(f"      times = {w_times}")
    print(f"      prec  = { {k: sorted(v) for k, v in w_prec.items()} }")
    print(f"      order = {w_order}")
    print(f"      makespan on m   = {w_m}: {w_ms_m}")
    print(f"      makespan on m+1 = {w_m + 1}: {w_ms_m1}   <-- STRICTLY LARGER")

    # ---- G3 -----------------------------------------------------------------
    print(f"\n[running] G3 exact (2-1/m) bound, K={K_BOUND} small instances ...")
    g3 = gate_g3_bound(K_BOUND)
    mr = g3["max_ratio"]
    g3_pass = (g3["violations"] == 0) and (g3["n_nontrivial"] > 0)
    print("\n--- G3  EXACTLY-TRUE: list/opt <= (2m-1)/m = 2 - 1/m ---------------")
    print(f"    instances checked = {g3['checked']}")
    print(f"    violations        = {g3['violations']}   (MUST be 0)")
    print(f"    max ratio observed= {mr.numerator}/{mr.denominator} = {float(mr):.6f}")
    print(f"    instances with ratio > 1 (bound nontrivial) = {g3['n_nontrivial']}")
    print(f"    PASS  = {g3_pass}   (violations == 0 AND nontrivial > 0)")
    if g3["max_ratio_info"]:
        t_, p_, o_, m_, ls_, opt_ = g3["max_ratio_info"]
        print(f"    max-ratio witness: m={m_}  list={ls_}  opt={opt_}")
        print(f"        times = {t_}")
        print(f"        prec  = { {k: sorted(v) for k, v in p_.items()} }")
        print(f"        order = {o_}")

    all_pass = bool(g1_pass and g2_add_pass and g2_short_pass and g3_pass)

    # ---- determinism digest (whole-dict, no self-field, stdout only) --------
    results = {
        "seed": SEED,

        "g1_removeedge_N": g1_N,
        "g1_removeedge_count": g1_count,
        "g1_removeedge_p": f"{g1_p:.6f}",
        "g1_removeedge_z": f"{g1_z:.6f}",
        "g1_removeedge_pass": bool(g1_pass),

        "g2_addmachine_N": g2_N,
        "g2_addmachine_count": g2_add,
        "g2_addmachine_p": f"{ga_p:.6f}",
        "g2_addmachine_z": f"{ga_z:.6f}",
        "g2_addmachine_pass": bool(g2_add_pass),

        "g2_shorten_N": g2_N,
        "g2_shorten_count": g2_short,
        "g2_shorten_p": f"{gs_p:.6f}",
        "g2_shorten_z": f"{gs_z:.6f}",
        "g2_shorten_pass": bool(g2_short_pass),

        "g3_bound_instances": g3["checked"],
        "g3_bound_violations": g3["violations"],
        "g3_bound_max_ratio_num": mr.numerator,
        "g3_bound_max_ratio_den": mr.denominator,
        "g3_bound_nontrivial": g3["n_nontrivial"],
        "g3_bound_pass": bool(g3_pass),

        "witness_add_m": w_m,
        "witness_add_makespan_m": w_ms_m,
        "witness_add_makespan_m1": w_ms_m1,

        "all_pass": all_pass,
    }
    canon = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode()).hexdigest()

    print("\n" + "=" * 72)
    print("DETERMINISM DIGEST (canonical JSON, sha256; whole-dict, no self-field)")
    print("=" * 72)
    print(f"canonical_json = {canon}")
    print(f"all_pass = {'true' if all_pass else 'false'}")
    print(f"sha256 = {digest}")


if __name__ == "__main__":
    main()
