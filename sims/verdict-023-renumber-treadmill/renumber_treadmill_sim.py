#!/usr/bin/env python3
"""VERDICT 023 — migration renumber-treadmill residual (idea-engine PROPOSAL 021).

Pre-registered continuous-time event sim of migration-number races under three
number-pick policies (P0 pick-at-open, P1 re-pick-at-push — the shipped
Option-1 checker's semantics, P3 assign-at-merge). Fully hermetic: stdlib
only, no network, no git, no wall clock, no hash(); the only file read is the
committed pre-registration (fixtures.json, same directory), and the runner
cross-checks its own literals against it at start. Deterministic: the only
randomness is random.Random(<pinned seed>) consumed in the pinned loop order;
stdout and results.json are byte-identical across process runs.

Run: python3 sims/verdict-023-renumber-treadmill/renumber_treadmill_sim.py
Exit 0 iff every self-check (incl. the validation gate) passes.
"""

import heapq
import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Pinned constants (cross-checked against the committed fixtures.json below).
# ---------------------------------------------------------------------------
LAMBDA_GRID = ((1, Fraction(1, 24)), (4, Fraction(1, 6)), (12, Fraction(1, 2)))
V_GRID = (0.25, 2.0, 24.0)
W_PRIMARY = 8.0
D_PRIMARY = 0.5
H_PRIMARY = 2000.0
WARMUP = 200.0
M_PRIMARY = 40
SEED_PRIMARY = 20260723
SEED_STABILITY = 20260724
M_STABILITY = 8
SEED_JITTER = 20260725
M_JITTER = 8
SEED_EXO = 20260726
M_EXO = 20000
M_SENS = 8
SEED_SENS = 20260723

POLICIES = ("P0", "P1", "P3")

R_MAX = Fraction(1, 10)
T_APPROVE_MAX = Fraction(1, 100)
T_REJECT_MIN = Fraction(1, 20)
APPROVE_CELLS_MIN = 8
REJECT_CELLS_MIN = 5
GATE_PP = 0.01  # 1.0 percentage point absolute

SENS_LEGS = (
    ("sens-d0.25", {"d": 0.25}),
    ("sens-d2", {"d": 2.0}),
    ("sens-W1", {"W": 1.0}),
    ("sens-W24", {"W": 24.0}),
)

ANCHOR_CELL = (12, 2.0)  # lambda=12/day, V=2 h (with d=0.5, P0) — the #1279 leg

CHECKS = {"passed": 0, "failed": 0}
FAILURES = []


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(label)


def cells_lexicographic():
    out = []
    for lam_day, lam_h in LAMBDA_GRID:
        for V in V_GRID:
            out.append((lam_day, lam_h, V))
    return out


def cell_key(lam_day, V):
    return "lam%02d|V%05.2f" % (lam_day, V)


# ---------------------------------------------------------------------------
# Arm A — exact, seedless exogenous single-PR closed forms.
# p(w) = 1 - e^(-lam*w); P(N>=1) = p(w1); P(N>=2) = p(w1)*p(w2);
# E[N] = p(w1)*e^(lam*w2). P0: w1 = W+V, w2 = d+V. P1: w1 = w2 = V.
# Each quantity computed twice by independent float paths (self-check).
# ---------------------------------------------------------------------------
def arm_a(lam, W, V, d, policy):
    if policy == "P0":
        w1, w2 = W + V, d + V
    elif policy == "P1":
        w1, w2 = V, V
    else:
        raise ValueError(policy)
    p1 = -math.expm1(-lam * w1)
    p_w2 = -math.expm1(-lam * w2)
    p2 = p1 * p_w2
    en = p1 * math.exp(lam * w2)
    # twin computations (independent float paths)
    p1_b = 1.0 - math.exp(-lam * w1)
    en_b = p1_b / (1.0 - (1.0 - math.exp(-lam * w2)))
    check(abs(p1 - p1_b) <= 1e-9 * max(p1, 1e-300),
          "arm A twin p1 lam=%s pol=%s" % (lam, policy))
    check(en_b == 0 or abs(en - en_b) <= 1e-9 * max(abs(en), abs(en_b)),
          "arm A twin E[N] lam=%s pol=%s" % (lam, policy))
    p3 = p1 * p_w2 * p_w2      # P(N>=3) = p(w1)*p(w2)^2 (anchor leg)
    p4 = p1 * p_w2 * p_w2 * p_w2
    return {"w1": w1, "w2": w2, "p_ge1": p1, "p_ge2": p2, "p_ge3": p3,
            "p_ge4": p4, "e_n": en}


# ---------------------------------------------------------------------------
# The endogenous engine (primary implementation): continuous-time event
# queue, events processed in (time, PR id) order. Event kinds:
# 0 = OPEN (arrival), 1 = PICK (P1 push re-pick), 2 = ATTEMPT.
# main is the integer max_main counter; pick takes max_main + 1; a merge
# attempt with held <= max_main is a collision; a successful merge asserts
# held == max_main + 1 (contiguity) and increments max_main.
# ---------------------------------------------------------------------------
def run_rep(arrivals, policy, W, V, d, H, warmup, jit=None, trace=None):
    """One replication. arrivals: ascending open times (all <= H).
    jit: None for fixed legs, else an rng whose expovariate redraws W (per PR,
    at open), V (per validation round: at open and at each collision), d (per
    fix: at each collision) at the pinned means. trace: list capturing jitter
    draws in draw order (for the independent replay).
    Returns the per-rep aggregate dict."""
    n = len(arrivals)
    open_t = arrivals
    held = [0] * n
    renum = [0] * n
    w_i = [W] * n
    v_i = [V] * n
    heap = []
    for i in range(n):
        heap.append((arrivals[i], i, 0))
    heapq.heapify(heap)
    push = heapq.heappush
    pop = heapq.heappop
    max_main = 0
    merges_all = 0
    collisions = 0
    holders = {}
    max_holders = 0
    merged_m = 0            # post-warmup merged count
    ren_total = 0           # their pooled renumbers
    tread2 = tread3 = tread4 = 0
    durations = []          # post-warmup merged durations, in merge order
    dur_sum = 0.0
    n_w = n_v = n_d = 0
    contiguity_ok = True
    p0 = policy == "P0"
    p1 = policy == "P1"
    p3 = policy == "P3"
    while heap:
        t, i, kind = pop(heap)
        if t > H:
            break
        if kind == 0:  # OPEN
            if jit is not None:
                w_i[i] = jit.expovariate(1.0 / W)
                v_i[i] = jit.expovariate(1.0 / V)
                n_w += 1
                n_v += 1
                if trace is not None:
                    trace.append(w_i[i])
                    trace.append(v_i[i])
            if p0:
                num = max_main + 1
                held[i] = num
                c = holders.get(num, 0) + 1
                holders[num] = c
                if c > max_holders:
                    max_holders = c
                push(heap, (t + w_i[i] + v_i[i], i, 2))
            elif p1:
                push(heap, (t + w_i[i], i, 1))
            else:  # P3
                push(heap, (t + w_i[i] + v_i[i], i, 2))
        elif kind == 1:  # PICK at push (P1 only)
            num = max_main + 1
            held[i] = num
            c = holders.get(num, 0) + 1
            holders[num] = c
            if c > max_holders:
                max_holders = c
            push(heap, (t + v_i[i], i, 2))
        else:  # ATTEMPT
            if p3:
                max_main += 1
                merges_all += 1
                if t > warmup:
                    merged_m += 1
                    dur = t - open_t[i]
                    dur_sum += dur
                    durations.append(dur)
                continue
            h = held[i]
            if h <= max_main:  # COLLISION — the held number is gone
                collisions += 1
                renum[i] += 1
                c = holders[h] - 1
                holders[h] = c
                if jit is not None:
                    d_draw = jit.expovariate(1.0 / d)
                    v_new = jit.expovariate(1.0 / V)
                    n_d += 1
                    n_v += 1
                    if trace is not None:
                        trace.append(d_draw)
                        trace.append(v_new)
                    v_i[i] = v_new
                else:
                    d_draw = d
                if p0:
                    # pick at fix START (now)
                    num = max_main + 1
                    held[i] = num
                    c2 = holders.get(num, 0) + 1
                    holders[num] = c2
                    if c2 > max_holders:
                        max_holders = c2
                    push(heap, (t + d_draw + v_i[i], i, 2))
                else:  # P1 — re-pick at the next push
                    push(heap, (t + d_draw, i, 1))
            else:  # MERGE
                if h != max_main + 1:
                    contiguity_ok = False
                max_main += 1
                merges_all += 1
                c = holders[h] - 1
                holders[h] = c
                if t > warmup:
                    merged_m += 1
                    N = renum[i]
                    ren_total += N
                    if N >= 2:
                        tread2 += 1
                    if N >= 3:
                        tread3 += 1
                    if N >= 4:
                        tread4 += 1
                    dur = t - open_t[i]
                    dur_sum += dur
                    durations.append(dur)
    if p3:
        max_holders = 1 if merges_all > 0 else 0
    return {"arrivals": n, "merged": merged_m, "ren_total": ren_total,
            "tread2": tread2, "tread3": tread3, "tread4": tread4,
            "durations": durations, "dur_sum": dur_sum,
            "collisions": collisions, "merges_all": merges_all,
            "max_main": max_main, "max_holders": max_holders,
            "contiguity_ok": contiguity_ok, "renum_sum_all": sum(renum),
            "n_w": n_w, "n_v": n_v, "n_d": n_d}


# ---------------------------------------------------------------------------
# Independent re-implementation (validity check): no heap, per-PR next-event
# scan with min(), merged-number SET membership as the collision test, and
# max-holders recomputed from recorded hold intervals by an overlap sweep.
# Must agree exactly (including float duration sums) on traced replications.
# ---------------------------------------------------------------------------
def replay_independent(arrivals, policy, W, V, d, H, warmup, jit_draws=None):
    n = len(arrivals)
    prs = [{"next_t": arrivals[i], "kind": "open", "held": None, "ren": 0,
            "w": W, "v": V, "done": False} for i in range(n)]
    merged_numbers = set()
    intervals = []  # (number, start, end)
    hold_start = [None] * n
    pos = 0
    merged_m = 0
    ren_total = 0
    tread2 = 0
    dur_sum = 0.0
    collisions = 0
    merges_all = 0
    while True:
        best = None
        for i in range(n):
            pr = prs[i]
            if pr["done"]:
                continue
            if best is None or (pr["next_t"], i) < best:
                best = (pr["next_t"], i)
        if best is None or best[0] > H:
            break
        t, i = best
        pr = prs[i]
        if pr["kind"] == "open":
            if jit_draws is not None:
                pr["w"] = jit_draws[pos]
                pr["v"] = jit_draws[pos + 1]
                pos += 2
            if policy == "P0":
                pr["held"] = len(merged_numbers) + 1
                hold_start[i] = t
                pr["next_t"] = t + pr["w"] + pr["v"]
                pr["kind"] = "attempt"
            elif policy == "P1":
                pr["next_t"] = t + pr["w"]
                pr["kind"] = "pick"
            else:
                pr["next_t"] = t + pr["w"] + pr["v"]
                pr["kind"] = "attempt"
        elif pr["kind"] == "pick":
            pr["held"] = len(merged_numbers) + 1
            hold_start[i] = t
            pr["next_t"] = t + pr["v"]
            pr["kind"] = "attempt"
        else:  # attempt
            if policy == "P3":
                merged_numbers.add(len(merged_numbers) + 1)
                merges_all += 1
                if t > warmup:
                    merged_m += 1
                    dur_sum += t - arrivals[i]
                pr["done"] = True
                continue
            if pr["held"] in merged_numbers:  # collision, by set membership
                collisions += 1
                pr["ren"] += 1
                intervals.append((pr["held"], hold_start[i], t))
                if jit_draws is not None:
                    d_draw = jit_draws[pos]
                    pr["v"] = jit_draws[pos + 1]
                    pos += 2
                else:
                    d_draw = d
                if policy == "P0":
                    pr["held"] = len(merged_numbers) + 1
                    hold_start[i] = t
                    pr["next_t"] = t + d_draw + pr["v"]
                else:
                    pr["held"] = None  # holds nothing until the next push
                    pr["next_t"] = t + d_draw
                    pr["kind"] = "pick"
            else:
                merged_numbers.add(pr["held"])
                merges_all += 1
                intervals.append((pr["held"], hold_start[i], t))
                if t > warmup:
                    merged_m += 1
                    ren_total += pr["ren"]
                    if pr["ren"] >= 2:
                        tread2 += 1
                    dur_sum += t - arrivals[i]
                pr["done"] = True
    # holds still open at end of horizon (censored PRs) also count
    for i in range(n):
        pr = prs[i]
        if not pr["done"] and pr["held"] is not None:
            intervals.append((pr["held"], hold_start[i], float("inf")))
    # max simultaneous holders from the interval log (overlap sweep per number)
    max_holders = 0
    by_num = {}
    for num, s, e in intervals:
        by_num.setdefault(num, []).append((s, e))
    for num, ivs in by_num.items():
        events = []
        for s, e in ivs:
            events.append((s, 1))
            events.append((e, -1))
        events.sort()
        cur = 0
        for _t, delta in events:
            cur += delta
            if cur > max_holders:
                max_holders = cur
    if policy == "P3":
        max_holders = 1 if merges_all > 0 else 0
    if jit_draws is not None:
        assert pos == len(jit_draws)
    return (merged_m, ren_total, tread2, dur_sum, collisions, merges_all,
            len(merged_numbers), max_holders)


# ---------------------------------------------------------------------------
# Leg runner: full 9-cell x 3-policy grid, one shared RNG stream, pinned
# loop order (cells lexicographic lam asc then V asc; policy P0, P1, P3;
# replications sequential). Per rep the only base draws are the arrival gaps.
# ---------------------------------------------------------------------------
def p95_index(n):
    return -(-95 * n // 100) - 1  # ceil(0.95*n) - 1 in pure integers


def run_leg(leg_id, seed, M, W, d, H, jitter=False, trace_stride=7):
    rng = random.Random(seed)
    results = {}
    total_gap_draws = 0
    total_arrivals = 0
    total_jit_draws = 0
    total_jit_expected = 0
    traces_checked = 0
    pair_index = 0
    n_reps = 0
    for (lam_day, lam_h, V) in cells_lexicographic():
        lam = float(lam_h)
        ck = cell_key(lam_day, V)
        per_pol = {}
        for policy in POLICIES:
            agg = {"merged": 0, "ren_total": 0, "tread2": 0, "tread3": 0,
                   "tread4": 0, "collisions": 0, "merges_all": 0,
                   "arrivals": 0, "dur_sum": 0.0, "max_holders": 0}
            durations = []
            take_trace = (pair_index % trace_stride) == 0
            for rep in range(M):
                n_reps += 1
                arrivals = []
                t = 0.0
                while True:
                    t += rng.expovariate(lam)
                    total_gap_draws += 1
                    if t > H:
                        break
                    arrivals.append(t)
                total_arrivals += len(arrivals)
                trace = [] if (jitter and take_trace and rep == 0) else None
                out = run_rep(arrivals, policy, W, V, d, H, WARMUP,
                              jit=(rng if jitter else None), trace=trace)
                # --- per-rep self-checks
                check(out["contiguity_ok"],
                      "main contiguity %s %s rep=%d leg=%s" % (ck, policy, rep, leg_id))
                check(out["max_main"] == out["merges_all"],
                      "max_main==merges %s %s rep=%d leg=%s" % (ck, policy, rep, leg_id))
                check(out["collisions"] == out["renum_sum_all"],
                      "collisions==renumbers %s %s rep=%d" % (ck, policy, rep))
                check(out["merged"] <= out["merges_all"],
                      "warmup filter subset %s %s rep=%d" % (ck, policy, rep))
                check(out["ren_total"] >= 2 * out["tread2"],
                      "tread accounting %s %s rep=%d" % (ck, policy, rep))
                if policy == "P3":
                    check(out["collisions"] == 0,
                          "P3 zero collisions %s rep=%d leg=%s (GATE)" % (ck, rep, leg_id))
                    if not jitter:
                        expected = sum(1 for a in arrivals if a + W + V <= H)
                        check(out["merges_all"] == expected,
                              "P3 merge count %s rep=%d" % (ck, rep))
                        check(all(abs(x - (W + V)) <= 1e-9
                                  for x in out["durations"]),
                              "P3 duration == W+V %s rep=%d" % (ck, rep))
                if not jitter and out["durations"]:
                    check(min(out["durations"]) >= W + V - 1e-9,
                          "duration floor %s %s rep=%d" % (ck, policy, rep))
                if jitter:
                    total_jit_draws += out["n_w"] + out["n_v"] + out["n_d"]
                    total_jit_expected += 2 * len(arrivals) + 2 * out["collisions"]
                if trace is not None:
                    ind = replay_independent(arrivals, policy, W, V, d, H,
                                             WARMUP, jit_draws=trace)
                    got = (out["merged"], out["ren_total"], out["tread2"],
                           out["dur_sum"], out["collisions"],
                           out["merges_all"], out["max_main"],
                           out["max_holders"])
                    check(ind == got,
                          "independent replay %s %s leg=%s" % (ck, policy, leg_id))
                    traces_checked += 1
                elif (not jitter) and take_trace and rep == 0:
                    ind = replay_independent(arrivals, policy, W, V, d, H,
                                             WARMUP)
                    got = (out["merged"], out["ren_total"], out["tread2"],
                           out["dur_sum"], out["collisions"],
                           out["merges_all"], out["max_main"],
                           out["max_holders"])
                    check(ind == got,
                          "independent replay %s %s leg=%s" % (ck, policy, leg_id))
                    traces_checked += 1
                for k in ("merged", "ren_total", "tread2", "tread3", "tread4",
                          "collisions", "merges_all", "arrivals"):
                    agg[k] += out[k]
                agg["dur_sum"] += out["dur_sum"]
                if out["max_holders"] > agg["max_holders"]:
                    agg["max_holders"] = out["max_holders"]
                durations.extend(out["durations"])
            m = agg["merged"]
            check(m > 0, "merged>0 %s %s leg=%s" % (ck, policy, leg_id))
            R = Fraction(agg["ren_total"], m) if m else None
            T = Fraction(agg["tread2"], m) if m else None
            durations.sort()
            mean_dur = agg["dur_sum"] / m if m else None
            p95_dur = durations[p95_index(len(durations))] if durations else None
            per_pol[policy] = {"R": R, "T": T, "counts": agg,
                               "mean_dur": mean_dur, "p95_dur": p95_dur}
            pair_index += 1
        # latency inflation vs the same cell's P3 leg (reporting-only)
        p3row = per_pol["P3"]
        for policy in ("P0", "P1"):
            row = per_pol[policy]
            row["infl_mean"] = (row["mean_dur"] / p3row["mean_dur"]
                                if row["mean_dur"] and p3row["mean_dur"] else None)
            row["infl_p95"] = (row["p95_dur"] / p3row["p95_dur"]
                               if row["p95_dur"] and p3row["p95_dur"] else None)
        results[ck] = per_pol
    check(total_gap_draws == total_arrivals + n_reps,
          "arrival draw-count accounting leg=%s" % leg_id)
    if jitter:
        check(total_jit_draws == total_jit_expected,
              "jitter draw-count accounting (2*arrivals + 2*collisions) leg=%s" % leg_id)
    return results, traces_checked


# ---------------------------------------------------------------------------
# Arm S exogenous mode: external Poisson appends (instant-merge external
# PRs), ONE focal PR per replication, truncated after the second collision
# (N recorded as 0, 1 or >=2 — all the 1.0 pp gate reads; disclosed in
# fixtures.json intake_time_decisions.3).
# ---------------------------------------------------------------------------
def run_focal(appends, policy, W, V, d):
    """Deterministic walk of one focal PR against the append times (ascending).
    Returns capped N in {0, 1, 2}. Same held/max discipline as the engine:
    max advances as appends merge instantly; pick takes max+1; collision at
    attempt iff held <= max."""
    if policy == "P0":
        pick1, att1 = 0.0, W + V
    else:
        pick1, att1 = W, W + V
    idx = 0
    max_main = 0
    na = len(appends)
    while idx < na and appends[idx] <= pick1:
        max_main += 1
        idx += 1
    held = max_main + 1
    while idx < na and appends[idx] <= att1:
        max_main += 1
        idx += 1
    if held > max_main:
        return 0
    if policy == "P0":
        pick2 = att1
        att2 = att1 + d + V
    else:
        pick2 = att1 + d
        att2 = pick2 + V
    while idx < na and appends[idx] <= pick2:
        max_main += 1
        idx += 1
    held = max_main + 1
    while idx < na and appends[idx] <= att2:
        max_main += 1
        idx += 1
    if held > max_main:
        return 1
    return 2


def replay_focal_independent(appends, policy, W, V, d):
    """Interval-membership re-formulation (different logic shape)."""
    if policy == "P0":
        pick1, att1 = 0.0, W + V
        pick2 = att1
        att2 = att1 + d + V
    else:
        pick1, att1 = W, W + V
        pick2 = att1 + d
        att2 = pick2 + V
    c1 = any(pick1 < a <= att1 for a in appends)
    if not c1:
        return 0
    c2 = any(pick2 < a <= att2 for a in appends)
    return 2 if c2 else 1


def run_exogenous(arm_a_table):
    rng = random.Random(SEED_EXO)
    out = {}
    max_dev = 0.0
    max_dev_where = None
    total_gap_draws = 0
    total_appends = 0
    n_focal = 0
    focal_index = 0
    traces_checked = 0
    for (lam_day, lam_h, V) in cells_lexicographic():
        lam = float(lam_h)
        ck = cell_key(lam_day, V)
        out[ck] = {}
        for policy in ("P0", "P1"):
            t_max = W_PRIMARY + V + D_PRIMARY + V
            n0 = n1 = n2 = 0
            take_trace = (focal_index % 5) == 0
            for rep in range(M_EXO):
                n_focal += 1
                appends = []
                t = 0.0
                while True:
                    t += rng.expovariate(lam)
                    total_gap_draws += 1
                    if t > t_max:
                        break
                    appends.append(t)
                total_appends += len(appends)
                N = run_focal(appends, policy, W_PRIMARY, V, D_PRIMARY)
                if take_trace and rep < 50:
                    ind = replay_focal_independent(appends, policy, W_PRIMARY,
                                                   V, D_PRIMARY)
                    check(ind == N, "exogenous replay %s %s rep=%d"
                          % (ck, policy, rep))
                    traces_checked += 1
                if N == 0:
                    n0 += 1
                elif N == 1:
                    n1 += 1
                else:
                    n2 += 1
            check(n0 + n1 + n2 == M_EXO,
                  "exogenous count conservation %s %s" % (ck, policy))
            p1_hat = Fraction(n1 + n2, M_EXO)
            p2_hat = Fraction(n2, M_EXO)
            a = arm_a_table[ck][policy]
            dev1 = abs(float(p1_hat) - a["p_ge1"])
            dev2 = abs(float(p2_hat) - a["p_ge2"])
            for dev, name in ((dev1, "P(N>=1)"), (dev2, "P(N>=2)")):
                check(dev <= GATE_PP,
                      "GATE exogenous vs Arm A %s %s %s dev=%.6f"
                      % (ck, policy, name, dev))
                if dev > max_dev:
                    max_dev = dev
                    max_dev_where = "%s %s %s" % (ck, policy, name)
            out[ck][policy] = {"n0": n0, "n1": n1, "n2plus": n2,
                               "p_ge1_hat": p1_hat, "p_ge2_hat": p2_hat,
                               "dev1_pp": dev1 * 100, "dev2_pp": dev2 * 100}
            focal_index += 1
    check(total_gap_draws == total_appends + n_focal,
          "exogenous draw-count accounting")
    return out, max_dev, max_dev_where, traces_checked


# ---------------------------------------------------------------------------
# Decision rule (pre-registered; exact Fractions on pooled integer counts,
# evaluated on the ENDOGENOUS P1 cells in the pinned order APPROVE ->
# REJECT -> NULL).
# ---------------------------------------------------------------------------
def median_fracs(vals):
    vs = sorted(vals)
    n = len(vs)
    if n == 0:
        return None
    if n % 2 == 1:
        return vs[n // 2]
    return (vs[n // 2 - 1] + vs[n // 2]) / 2


def decide(leg):
    cells = [cell_key(ld, V) for (ld, _lh, V) in cells_lexicographic()]
    approve_pass = []
    reject_cells = []
    for c in cells:
        row = leg[c]["P1"]
        if row["R"] <= R_MAX and row["T"] <= T_APPROVE_MAX:
            approve_pass.append(c)
        if row["T"] > T_REJECT_MIN:
            reject_cells.append(c)
    if len(approve_pass) >= APPROVE_CELLS_MIN:
        ruling = "APPROVE"
    elif len(reject_cells) >= REJECT_CELLS_MIN:
        ruling = "REJECT"
    else:
        ruling = "NULL"
    # per-axis APPROVE-pass shares + median T (the NULL axis-naming duty,
    # reported on every outcome)
    axes = {}
    axis_defs = (
        ("lambda", lambda ld, V: "lam%02d" % ld,
         ["lam01", "lam04", "lam12"]),
        ("V", lambda ld, V: "V%05.2f" % V,
         ["V00.25", "V02.00", "V24.00"]),
    )
    for aname, keyf, values in axis_defs:
        per_val = {}
        shares = []
        for v in values:
            sub = [cell_key(ld, V) for (ld, _lh, V) in cells_lexicographic()
                   if keyf(ld, V) == v]
            n_pass = sum(1 for c in sub if c in approve_pass)
            share = Fraction(n_pass, len(sub))
            med_t = median_fracs([leg[c]["P1"]["T"] for c in sub])
            per_val[v] = {"approve_pass_share": share, "median_T": med_t}
            shares.append(share)
        per_val["_spread"] = max(shares) - min(shares)
        axes[aname] = per_val
    # flip axis: larger APPROVE-pass share spread; tie -> larger median-T
    # range; tie -> V (the idea file's expected candidate), deterministic
    sp_l, sp_v = axes["lambda"]["_spread"], axes["V"]["_spread"]
    if sp_l != sp_v:
        flip_axis = "lambda" if sp_l > sp_v else "V"
    else:
        def t_range(ax):
            ts = [axes[ax][k]["median_T"] for k in axes[ax] if k != "_spread"]
            return max(ts) - min(ts)
        flip_axis = "lambda" if t_range("lambda") > t_range("V") else "V"
    return {"ruling": ruling, "approve_pass_cells": sorted(approve_pass),
            "approve_pass_count": len(approve_pass),
            "reject_cells": sorted(reject_cells),
            "reject_count": len(reject_cells),
            "n_cells": len(cells), "axes": axes, "flip_axis": flip_axis}


def decide_independent(leg):
    """Second, independently-written decision evaluator: integer
    cross-multiplication on the pooled counts, string flow. Must agree with
    decide() on the ruling and both cell sets."""
    passes = []
    rejects = []
    for (ld, _lh, V) in cells_lexicographic():
        c = cell_key(ld, V)
        cnt = leg[c]["P1"]["counts"]
        ren, t2, m = cnt["ren_total"], cnt["tread2"], cnt["merged"]
        ok_r = 10 * ren <= m          # R <= 0.10
        ok_t = 100 * t2 <= m          # T <= 0.01
        if ok_r and ok_t:
            passes.append(c)
        if 20 * t2 > m:               # T > 0.05
            rejects.append(c)
    if len(passes) >= 8:
        ruling = "APPROVE"
    elif len(rejects) >= 5:
        ruling = "REJECT"
    else:
        ruling = "NULL"
    return ruling, sorted(passes), sorted(rejects)


# ---------------------------------------------------------------------------
# Fixture cross-check.
# ---------------------------------------------------------------------------
def cross_check_fixtures():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)
    c = fx["constants"]
    check(tuple(c["lambda_grid_per_day"]) == tuple(ld for ld, _ in LAMBDA_GRID),
          "fixture lambda grid (per day)")
    check(tuple(Fraction(s) for s in c["lambda_grid_per_hour"])
          == tuple(lh for _, lh in LAMBDA_GRID), "fixture lambda grid (per hour)")
    check(tuple(c["V_grid_hours"]) == V_GRID, "fixture V grid")
    check(c["W_hours"] == W_PRIMARY, "fixture W")
    check(c["d_hours"] == D_PRIMARY, "fixture d")
    check(c["H_hours"] == H_PRIMARY, "fixture H")
    check(c["warmup_hours"] == WARMUP, "fixture warm-up")
    check(c["M_primary"] == M_PRIMARY, "fixture M primary")
    check(c["seed_primary"] == SEED_PRIMARY, "fixture primary seed")
    check(c["seed_stability"] == SEED_STABILITY, "fixture stability seed")
    check(c["M_stability"] == M_STABILITY, "fixture stability M")
    check(c["seed_jitter"] == SEED_JITTER, "fixture jitter seed")
    check(c["seed_exogenous"] == SEED_EXO, "fixture exogenous seed")
    check(c["M_exogenous_focal"] == M_EXO, "fixture exogenous M")
    check(tuple(c["policies"]) == POLICIES, "fixture policy order")
    b = fx["band_constants"]
    check(Fraction(b["R_MAX"]) == R_MAX, "fixture R_MAX")
    check(Fraction(b["T_APPROVE_MAX"]) == T_APPROVE_MAX, "fixture T approve")
    check(Fraction(b["T_REJECT_MIN"]) == T_REJECT_MIN, "fixture T reject")
    check(b["APPROVE_CELLS_MIN"] == APPROVE_CELLS_MIN, "fixture approve cells")
    check(b["REJECT_CELLS_MIN"] == REJECT_CELLS_MIN, "fixture reject cells")
    check(b["N_CELLS"] == 9, "fixture cell count")
    check(len(cells_lexicographic()) == 9, "9 cells")
    ro = fx["reporting_only_legs"]
    got_legs = tuple((l["id"], tuple(sorted(l["override"].items())))
                     for l in ro["sensitivity"])
    want_legs = tuple((lid, tuple(sorted(ov.items()))) for lid, ov in SENS_LEGS)
    check(got_legs == want_legs, "fixture sensitivity leg set")
    check(ro["sens_M"] == M_SENS, "fixture sens M")
    check(ro["sens_seed"] == SEED_SENS, "fixture sens seed")
    check(ro["stability_leg"]["M"] == M_STABILITY
          and ro["stability_leg"]["seed"] == SEED_STABILITY,
          "fixture stability leg")
    check(ro["jitter_leg"]["M"] == M_JITTER
          and ro["jitter_leg"]["seed"] == SEED_JITTER, "fixture jitter leg")
    check(fx["cpython_pin"] == "3.11", "fixture cpython pin")
    check(sys.version_info[:2] == (3, 11), "running on pinned cpython 3.11")
    dr = fx["decision_rule"]
    check(dr["evaluation_order"] == ["APPROVE", "REJECT", "NULL"],
          "fixture evaluation order")
    return fx


def run_hand_pins(fx):
    for name in ("HAND-1", "HAND-2"):
        pin = fx["hand_pins"][name]
        p = pin["params"]
        arr = [float(a) for a in p["arrivals"]]
        out = run_rep(arr, p["policy"], float(p["W"]), float(p["V"]),
                      float(p["d"]), float(p["H"]), float(p["warmup"]))
        e = pin["expect"]
        check(out["merged"] == e["merged"], "%s merged" % name)
        check(out["ren_total"] == e["renumbers"], "%s renumbers" % name)
        check(out["tread2"] == e["tread2"], "%s treadmill" % name)
        check(out["collisions"] == e["collisions"], "%s collisions" % name)
        check(out["max_main"] == e["max_main"], "%s max_main" % name)
        check(out["max_holders"] == e["max_holders"], "%s max holders" % name)
        check(out["dur_sum"] == e["dur_sum"], "%s duration sum" % name)
        # P3 companion on the same arrivals (the built-in control)
        out3 = run_rep(arr, "P3", float(p["W"]), float(p["V"]), float(p["d"]),
                       float(p["H"]), float(p["warmup"]))
        e3 = pin["expect_p3"]
        check(out3["merged"] == e3["merged"], "%s P3 merged" % name)
        check(out3["collisions"] == e3["collisions"], "%s P3 collisions" % name)
        check(out3["max_main"] == e3["max_main"], "%s P3 max_main" % name)
        check(out3["dur_sum"] == e3["dur_sum"], "%s P3 duration sum" % name)
        # independent replay must agree on the pins too
        ind = replay_independent(arr, p["policy"], float(p["W"]), float(p["V"]),
                                 float(p["d"]), float(p["H"]),
                                 float(p["warmup"]))
        check(ind[:3] == (e["merged"], e["renumbers"], e["tread2"])
              and ind[3] == e["dur_sum"] and ind[7] == e["max_holders"],
              "%s independent replay" % name)
    # HAND-2 re-scored at warmup 10.5 (tests the merge-instant filter)
    pin = fx["hand_pins"]["HAND-2"]
    p = pin["params"]
    arr = [float(a) for a in p["arrivals"]]
    out = run_rep(arr, p["policy"], float(p["W"]), float(p["V"]),
                  float(p["d"]), float(p["H"]), 10.5)
    ew = pin["expect_warmup_10_5"]
    check(out["merged"] == ew["merged"], "HAND-2 warmup merged")
    check(out["ren_total"] == ew["renumbers"], "HAND-2 warmup renumbers")
    check(out["tread2"] == ew["tread2"], "HAND-2 warmup treadmill")
    check(out["dur_sum"] == ew["dur_sum"], "HAND-2 warmup duration sum")


# ---------------------------------------------------------------------------
# Serialization helpers (deterministic).
# ---------------------------------------------------------------------------
def frac_str(fr):
    if fr is None:
        return None
    return "%d/%d" % (fr.numerator, fr.denominator)


def f6(x):
    if x is None:
        return None
    if isinstance(x, Fraction):
        x = x.numerator / x.denominator
    return round(x, 6)


def leg_table(leg, arm_a_table=None, full=False):
    out = {}
    for ck in sorted(leg.keys()):
        row = {}
        for policy in POLICIES:
            r = leg[ck][policy]
            cnt = r["counts"]
            entry = {
                "R_f": f6(r["R"]), "T_f": f6(r["T"]),
                "merged": cnt["merged"], "renumbers": cnt["ren_total"],
                "tread2": cnt["tread2"],
                "mean_dur_f": f6(r["mean_dur"]), "p95_dur_f": f6(r["p95_dur"]),
                "max_holders": cnt["max_holders"],
            }
            if full:
                entry["R"] = frac_str(r["R"])
                entry["T"] = frac_str(r["T"])
                entry["tread3"] = cnt["tread3"]
                entry["tread4"] = cnt["tread4"]
                entry["collisions_all"] = cnt["collisions"]
                entry["merges_all"] = cnt["merges_all"]
                entry["arrivals"] = cnt["arrivals"]
            if policy in ("P0", "P1"):
                entry["infl_mean_f"] = f6(r.get("infl_mean"))
                entry["infl_p95_f"] = f6(r.get("infl_p95"))
                if arm_a_table is not None:
                    a = arm_a_table[ck][policy]
                    amp = (float(r["R"]) / a["e_n"]) if a["e_n"] > 0 else None
                    entry["amplification_R_endo_over_ArmA_EN"] = f6(amp)
            row[policy] = entry
        out[ck] = row
    return out


def decision_block(dec):
    axes = {}
    for aname, per_val in dec["axes"].items():
        block = {}
        for k, v in per_val.items():
            if k == "_spread":
                block["spread"] = frac_str(v)
                block["spread_f"] = f6(v)
            else:
                block[k] = {"approve_pass_share": frac_str(v["approve_pass_share"]),
                            "approve_pass_share_f": f6(v["approve_pass_share"]),
                            "median_T": frac_str(v["median_T"]),
                            "median_T_f": f6(v["median_T"])}
        axes[aname] = block
    return {"ruling": dec["ruling"],
            "approve_pass_count": dec["approve_pass_count"],
            "approve_pass_cells": dec["approve_pass_cells"],
            "reject_count": dec["reject_count"],
            "reject_cells": dec["reject_cells"],
            "n_cells": dec["n_cells"], "flip_axis": dec["flip_axis"],
            "axes": axes}


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    fx = cross_check_fixtures()
    run_hand_pins(fx)

    # Arm A — exact closed forms for every cell x {P0, P1}
    arm_a_table = {}
    for (lam_day, lam_h, V) in cells_lexicographic():
        ck = cell_key(lam_day, V)
        arm_a_table[ck] = {}
        for policy in ("P0", "P1"):
            arm_a_table[ck][policy] = arm_a(float(lam_h), W_PRIMARY, V,
                                            D_PRIMARY, policy)

    # Validation gate part 1: Arm S exogenous vs Arm A
    exo, max_dev, max_dev_where, exo_traced = run_exogenous(arm_a_table)

    legs_out = {}
    decisions = {}

    # primary decision leg (endogenous)
    primary, traced_p = run_leg("primary", SEED_PRIMARY, M_PRIMARY, W_PRIMARY,
                                D_PRIMARY, H_PRIMARY)
    check(traced_p == 4, "primary trace coverage (strided (cell,policy) pairs)")
    dec = decide(primary)
    ind_ruling, ind_pass, ind_rej = decide_independent(primary)
    check(ind_ruling == dec["ruling"], "independent decision: ruling agrees")
    check(ind_pass == dec["approve_pass_cells"],
          "independent decision: APPROVE-pass set agrees")
    check(ind_rej == dec["reject_cells"],
          "independent decision: REJECT set agrees")
    legs_out["primary"] = leg_table(primary, arm_a_table, full=True)
    decisions["primary"] = decision_block(dec)

    # stability leg (must reproduce the ruling — done-when)
    stab, traced_s = run_leg("stability", SEED_STABILITY, M_STABILITY,
                             W_PRIMARY, D_PRIMARY, H_PRIMARY)
    check(traced_s == 4, "stability trace coverage")
    dec_stab = decide(stab)
    check(dec_stab["ruling"] == dec["ruling"],
          "stability leg (M=8, seed 20260724) reproduces the ruling")
    legs_out["stability"] = leg_table(stab)
    decisions["stability"] = decision_block(dec_stab)

    # sensitivity legs (reporting-only; scored under the same rule for the record)
    for lid, ov in SENS_LEGS:
        W = ov.get("W", W_PRIMARY)
        d = ov.get("d", D_PRIMARY)
        leg, traced_l = run_leg(lid, SEED_SENS, M_SENS, W, d, H_PRIMARY)
        check(traced_l == 4, "%s trace coverage" % lid)
        legs_out[lid] = leg_table(leg)
        decisions[lid] = decision_block(decide(leg))

    # jitter leg (reporting-only; seed pinned in the idea file)
    jit, traced_j = run_leg("jitter", SEED_JITTER, M_JITTER, W_PRIMARY,
                            D_PRIMARY, H_PRIMARY, jitter=True)
    check(traced_j == 4, "jitter trace coverage")
    legs_out["jitter"] = leg_table(jit)
    decisions["jitter"] = decision_block(decide(jit))

    # #1279 anchor leg (reporting-only): Arm A exact + the endogenous
    # measured counterparts at (lam=12/day, V=2, d=0.5, P0)
    ack = cell_key(*ANCHOR_CELL)
    a = arm_a_table[ack]["P0"]
    arow = primary[ack]["P0"]
    acnt = arow["counts"]
    anchor = {
        "cell": ack + " P0 (d=0.5)",
        "arm_a_E_N": f6(a["e_n"]), "arm_a_p_ge3": f6(a["p_ge3"]),
        "arm_a_p_ge4": f6(a["p_ge4"]),
        "endogenous_R": frac_str(arow["R"]), "endogenous_R_f": f6(arow["R"]),
        "endogenous_share_ge3": frac_str(Fraction(acnt["tread3"], acnt["merged"])),
        "endogenous_share_ge3_f": f6(Fraction(acnt["tread3"], acnt["merged"])),
        "endogenous_share_ge4": frac_str(Fraction(acnt["tread4"], acnt["merged"])),
        "endogenous_share_ge4_f": f6(Fraction(acnt["tread4"], acnt["merged"])),
        "note": "plausibility vs the n=1 #1279 anecdote (four renumbers, one afternoon), never a fit",
    }

    # exogenous table for the record
    exo_out = {}
    for ck in sorted(exo.keys()):
        exo_out[ck] = {}
        for policy in ("P0", "P1"):
            r = exo[ck][policy]
            a2 = arm_a_table[ck][policy]
            exo_out[ck][policy] = {
                "p_ge1_hat_f": f6(r["p_ge1_hat"]), "arm_a_p_ge1": f6(a2["p_ge1"]),
                "p_ge2_hat_f": f6(r["p_ge2_hat"]), "arm_a_p_ge2": f6(a2["p_ge2"]),
                "dev1_pp": f6(r["dev1_pp"]), "dev2_pp": f6(r["dev2_pp"]),
            }
    arm_a_out = {}
    for ck in sorted(arm_a_table.keys()):
        arm_a_out[ck] = {}
        for policy in ("P0", "P1"):
            a2 = arm_a_table[ck][policy]
            arm_a_out[ck][policy] = {k: f6(a2[k]) for k in
                                     ("w1", "w2", "p_ge1", "p_ge2", "p_ge3",
                                      "p_ge4", "e_n")}

    p3_collisions = sum(legs_out[l][ck]["P3"].get("collisions_all", 0)
                        for l in ("primary",) for ck in legs_out[l])
    # (per-rep P3 zero-collision checks already ran on EVERY endogenous leg)

    ok = CHECKS["failed"] == 0
    results = {
        "sim": "verdict-023-renumber-treadmill",
        "proposal": "idea-engine control/outbox.md PROPOSAL 021 · 2026-07-13T02:36:37Z · status: sim-ready",
        "python": "%d.%d" % sys.version_info[:2],
        "ruling": dec["ruling"],
        "validation_gate": {
            "exogenous_max_abs_dev_pp": f6(max_dev * 100),
            "exogenous_max_dev_where": max_dev_where,
            "gate_pp": 1.0,
            "p3_collisions_primary_pooled": p3_collisions,
            "p3_zero_collision_note": "per-replication P3 zero-collision checks ran on every endogenous leg (primary, stability, all sensitivity, jitter)",
        },
        "decision_detail": decisions,
        "tables": legs_out,
        "arm_a": arm_a_out,
        "exogenous": exo_out,
        "anchor_1279": anchor,
        "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"]},
        "failures": FAILURES[:50],
    }
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")

    p = decisions["primary"]
    print("VERDICT-023 migration renumber-treadmill residual — PROPOSAL 021")
    print("ruling: %s" % dec["ruling"])
    print("gate: exogenous vs Arm A max |dev| = %.4f pp (<= 1.0 pp: %s) at %s"
          % (max_dev * 100, "yes" if max_dev <= GATE_PP else "NO",
             max_dev_where))
    print("gate: endogenous P3 collisions == 0 on every leg (checked per rep)")
    print("P1 endogenous cells (R = renumbers/merged, T = share >=2):")
    for (ld, _lh, V) in cells_lexicographic():
        ck = cell_key(ld, V)
        row = primary[ck]["P1"]
        a2 = arm_a_table[ck]["P1"]
        amp = float(row["R"]) / a2["e_n"] if a2["e_n"] > 0 else float("nan")
        print("  %s  R=%-9s T=%-9s merged=%-6d amp(R/ArmA)=%.3f infl(mean)=%.3f"
              % (ck, f6(row["R"]), f6(row["T"]), row["counts"]["merged"], amp,
                 row["infl_mean"]))
    print("APPROVE-pass cells: %d/9 (need >=8); REJECT cells (T>0.05): %d/9 (need >=5)"
          % (p["approve_pass_count"], p["reject_count"]))
    for aname in ("lambda", "V"):
        ax = p["axes"][aname]
        vals = {k: v["approve_pass_share_f"] for k, v in ax.items()
                if k not in ("spread", "spread_f")}
        meds = {k: v["median_T_f"] for k, v in ax.items()
                if k not in ("spread", "spread_f")}
        print("axis %-6s approve-pass shares %s median T %s spread %s"
              % (aname, json.dumps(vals, sort_keys=True),
                 json.dumps(meds, sort_keys=True), ax["spread_f"]))
    print("flip axis: %s" % p["flip_axis"])
    print("stability leg ruling: %s" % decisions["stability"]["ruling"])
    for lid, _ov in SENS_LEGS:
        print("sensitivity %-10s ruling-under-rule: %s (reporting-only)"
              % (lid, decisions[lid]["ruling"]))
    print("jitter leg ruling-under-rule: %s (reporting-only)"
          % decisions["jitter"]["ruling"])
    print("anchor #1279 (lam12 V2 d0.5 P0): Arm A E[N]=%s P(N>=3)=%s P(N>=4)=%s | endo R=%s share>=3=%s share>=4=%s"
          % (anchor["arm_a_E_N"], anchor["arm_a_p_ge3"], anchor["arm_a_p_ge4"],
             anchor["endogenous_R_f"], anchor["endogenous_share_ge3_f"],
             anchor["endogenous_share_ge4_f"]))
    print("SELF-CHECKS: %d passed, %d failed"
          % (CHECKS["passed"], CHECKS["failed"]))
    if not ok:
        for fl in FAILURES[:20]:
            print("FAILED: %s" % fl)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
