#!/usr/bin/env python3
"""verdict-014 - routine-cadence economics sim (idea-engine PROPOSAL 012 / INTAKE 012).

Seeded discrete-event replay of trigger-arrival trace T (the real ~12.2h corpus
reconstructed from idea-engine control/status.md history fc0bab6..531b109, plus
seeded Poisson / burst / empty-night variants) against policy grid
G = {failsafe-2h, failsafe-1h, failsafe-30m, failsafe-2h+chain-15m-while-work-open,
event-driven-only, hybrid(event-driven+failsafe-2h)} under cost model C
(1 worker-turn per pacemaker re-arm, 1 recon-worker-turn per failsafe sweep,
~0 marginal per webhook wake; units = worker-turns).

Question (PROPOSAL 012, verbatim intent): which policy minimizes worker-turns per
caught trigger subject to p95 catch-latency <= 2h, and is any policy strictly
dominated across all trace variants?

Stdlib-only. Deterministic: all seeds are committed constants below; no wall
clock, no unseeded randomness, no network. Exit 0 iff all self-checks pass.
stdout and results.json are byte-identical across re-runs.

Run: python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py
"""

import heapq
import json
import math
import os
import random
import sys

# ---------------------------------------------------------------------------
# Pins (all evidence SHAs; see labels.json for the full hand-audit ledger)
# ---------------------------------------------------------------------------

PINS = {
    "proposal": "idea-engine PROPOSAL 012, control/outbox.md @ ff48c2fad809ce7704bb66aafee42335efd5c3fd (lines 82-86)",
    "idea": "ideas/fleet/routine-cadence-economics-sim-2026-07-12.md @ 87f0dd2d0b0b9677302dd58fb24a2e3e3d39c9ff",
    "probe_verdict": "idea-engine PR #259, head fc90d7f",
    "trace_range": "idea-engine control/status.md history fc0bab6..531b109 (13 exclusive-range commits; 14 versions incl. fc0bab6)",
    "trace_read_at": "idea-engine origin/main ff48c2fad809ce7704bb66aafee42335efd5c3fd",
    "event_evidence": {
        "E1": "38f88576efcaf436fa80404816f791dff86672d5",
        "E2": "38f88576efcaf436fa80404816f791dff86672d5",
        "E3": "b5cc329038cf95ff5e373ff472b21b869f60ade2",
        "E4": "65cd284a5c37e0b07a7012e3ed37f44671fa7c76",
        "E5": "65cd284a5c37e0b07a7012e3ed37f44671fa7c76",
        "N3": "531b1098ef6d1d24d04ea9e111f2d74fc877caf8",
    },
    "sim_lab_base": "055245e9c5a694fac07eb51681eb67728dd91429",
}

# ---------------------------------------------------------------------------
# Trace T - embedded real corpus (minutes from 2026-07-12T00:00:00Z)
# ---------------------------------------------------------------------------
# E5 (fm roster gen #13) has NO recorded arrival time (labels.json G8): excluded
# from latency replay, included in the arrival-rate derivation (5 arrivals).
# All real arrivals are inbox-only (webhook-visible class EMPTY on the real
# trace - labels.json G11); visible flag False throughout.

REAL_ARRIVALS = [  # (id, t_min, webhook_visible)
    ("E1", 182.0, False),   # 03:02Z fm roster gen #11
    ("E2", 195.0, False),   # 03:15Z (early bound of 03:15-03:28Z window) fm restructure merges
    ("E3", 393.0, False),   # 06:33Z fm roster gen #12
    ("E4", 510.0, False),   # 08:30Z sim-lab ORDER 003
]
E2_LATE_BOUND_MIN = 208.0   # 03:28Z window late bound (sensitivity S5)
REAL_HORIZON_MIN = 732.0    # 00:00Z -> 12:12Z (531b109 heartbeat window end)
REAL_ARRIVAL_COUNT_FOR_RATE = 5  # E1..E5 (E5 timeless but real)

# Observed (historical) catches under the REAL night's mixed posture - used for
# the observed-vs-idealized audit only, never as replay input (labels.json).
OBSERVED_LATENCY_DEFA = {"E1": 178.0, "E2": 165.0, "E3": 87.0, "E4": 90.0}

# Catch definitions (E4 fork, labels.json G6):
#   def-A: catch = the wake that reads the trigger (E4 -> 90 min).
#   def-B: catch = done-when evidence landed; modeled as wake + EXEC_LAG_MIN,
#          the one measured execution lag (E4: 10:00:00Z sweep -> 10:31:24Z
#          evidence merge = 31.4 min), applied uniformly.
EXEC_LAG_MIN = 31.4

# ---------------------------------------------------------------------------
# Model constants (all committed; sensitivity sweeps below)
# ---------------------------------------------------------------------------

SYN_HORIZON_MIN = 720.0          # synthetic night = 12h
LAMBDA_PER_MIN = REAL_ARRIVAL_COUNT_FOR_RATE / REAL_HORIZON_MIN  # 5/732 ~ 0.0068/min ~ 0.41/h
LAMBDA_ALT_PER_MIN = 4.0 / REAL_HORIZON_MIN  # alt derivation: drop timeless E5 (sensitivity S8)
N_SEEDS = 40
BASE_SEED = 20260712
TAG_SEED_XOR = 0x5EED7A65        # dedicated tag stream (times identical across w)
W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]  # webhook-visible fraction (load-bearing unknown)
CHAIN_PERIOD_MIN = 15.0
WORK_MIN_DEFAULT = 120.0         # work stays open 2h after a catching wake (sensitivity S4)
P95_CONSTRAINT_MIN = 120.0       # p95 catch-latency <= 2h
EPS = 1e-9

POLICIES = [
    # (id, sweep_period_min or None, chain?, event-driven?)
    ("failsafe-2h", 120.0, False, False),
    ("failsafe-1h", 60.0, False, False),
    ("failsafe-30m", 30.0, False, False),
    ("failsafe-2h+chain-15m", 120.0, True, False),
    ("event-driven-only", None, False, True),
    ("hybrid(event+failsafe-2h)", 120.0, False, True),
]
POLICY_IDS = [p[0] for p in POLICIES]

# Primary channel-semantics assumptions (each swept in sensitivity):
#   chain_sweeps=False  - a pacemaker chain wake does NOT sweep inboxes. This is
#       the AS-OBSERVED semantics: E2 arrived 03:15-03:28Z while the chain was
#       alive and was not seen until the next fm-sweeping wake (labels.json E2).
#   webhook_wake_sweeps=True - a webhook wake is a full seat turn at ~0 marginal
#       cost (cost model C), so it also sweeps pending inbox arrivals. This is
#       OPTIMISTIC for the event-driven policies and untestable on the real
#       trace (webhook class empty); swept to False in sensitivity S3.
PRIMARY = {"chain_sweeps": False, "webhook_wake_sweeps": True}

# ---------------------------------------------------------------------------
# Discrete-event core
# ---------------------------------------------------------------------------


def run_policy(arrivals, horizon, sweep=None, chain=False, event=False, phase=0.0,
               work_min=WORK_MIN_DEFAULT, chain_sweeps=False, webhook_wake_sweeps=True):
    """Replay one night. arrivals = [(t_min, visible)]; returns (caught, uncaught_idx, turns).

    Wake kinds and costs (cost model C):
      sweep   - failsafe recon sweep, 1 worker-turn, catches all pending arrivals <= t.
      webhook - ~0 worker-turns; catches its own arrival; if webhook_wake_sweeps,
                also sweeps all pending arrivals <= t.
      chain   - pacemaker re-arm, 1 worker-turn; catches nothing unless chain_sweeps.
                Fires every CHAIN_PERIOD_MIN while work is open (work opens at any
                wake that catches >=1 arrival, for work_min minutes, windows merge).
    Same-time ordering: sweep before webhook before chain (deterministic).
    """
    events = []
    seq = 0

    def push(t, pri, kind, payload=None):
        nonlocal seq
        heapq.heappush(events, (t, pri, seq, kind, payload))
        seq += 1

    if sweep is not None:
        t = phase
        while t <= horizon + EPS:
            push(t, 0, "sweep")
            t += sweep
    if event:
        for i, (ta, vis) in enumerate(arrivals):
            if vis:
                push(ta, 1, "webhook", i)

    pending = {i: ta for i, (ta, _vis) in enumerate(arrivals)}
    caught = {}
    turns = 0
    work_until = -1.0
    chain_next = None  # time of the single outstanding scheduled chain fire

    while events:
        t, _pri, _seq, kind, payload = heapq.heappop(events)
        catches_now = []
        if kind == "sweep":
            turns += 1
            catches_now = [i for i in sorted(pending) if pending[i] <= t + EPS]
        elif kind == "webhook":
            if webhook_wake_sweeps:
                catches_now = [i for i in sorted(pending) if pending[i] <= t + EPS]
            elif payload in pending:
                catches_now = [payload]
        elif kind == "chain":
            turns += 1
            chain_next = None
            if chain_sweeps:
                catches_now = [i for i in sorted(pending) if pending[i] <= t + EPS]
        for i in catches_now:
            caught[i] = t
            del pending[i]
        if chain:
            if catches_now:
                work_until = max(work_until, t + work_min)
            if work_until > t + EPS and chain_next is None:
                nxt = t + CHAIN_PERIOD_MIN
                if nxt <= work_until + EPS and nxt <= horizon + EPS:
                    push(nxt, 2, "chain")
                    chain_next = nxt
    return caught, sorted(pending), turns


def nearest_rank(sorted_vals, q):
    """Nearest-rank percentile on a pre-sorted list (deterministic; inf allowed)."""
    n = len(sorted_vals)
    if n == 0:
        return None
    idx = max(0, math.ceil(q * n) - 1)
    return sorted_vals[idx]


def night_latencies(arrivals, caught):
    """def-A latency per arrival; inf if never caught."""
    out = []
    for i, (ta, _vis) in enumerate(arrivals):
        out.append(caught[i] - ta if i in caught else math.inf)
    return out


def cell_metrics(lat_a_pool, turns, n_arrivals, exec_lag):
    """Metrics for one (policy x variant) cell from pooled def-A latencies."""
    catches = sum(1 for x in lat_a_pool if x < math.inf)
    uncaught = n_arrivals - catches
    tpc = (turns / catches) if catches > 0 else math.inf
    out = {"turns": turns, "arrivals": n_arrivals, "catches": catches,
           "uncaught": uncaught, "turns_per_catch": tpc}
    for defn, lag in (("defA", 0.0), ("defB", exec_lag)):
        lats = sorted((x + lag if x < math.inf else math.inf) for x in lat_a_pool)
        med = nearest_rank(lats, 0.50)
        p95 = nearest_rank(lats, 0.95)
        missed = sum(1 for x in lats if x > P95_CONSTRAINT_MIN + EPS)
        if n_arrivals == 0:  # vacuous (empty night)
            med, p95, missed = 0.0, 0.0, 0
        out[defn] = {"median": med, "p95": p95,
                     "missed_gt_2h": missed,
                     "pass_p95_le_2h": (p95 is not None and p95 <= P95_CONSTRAINT_MIN + EPS)}
    return out


# ---------------------------------------------------------------------------
# Variant generators (seeded, committed constants; times identical across w)
# ---------------------------------------------------------------------------


def gen_poisson_times(seed, lam, horizon):
    rng = random.Random(seed)
    ts, t = [], 0.0
    while True:
        t += rng.expovariate(lam)
        if t > horizon:
            break
        ts.append(t)
    return ts


def gen_burst_times(seed, horizon):
    """Clustered arrivals: 2 bursts/night, 2-3 arrivals each within +/-20 min of a
    uniform center - mirrors the real night's E1/E2 cluster shape. E[total] = 5."""
    rng = random.Random(seed)
    ts = []
    for _ in range(2):
        center = rng.uniform(60.0, horizon - 60.0)
        size = 2 + rng.randrange(2)
        for _ in range(size):
            ts.append(min(max(center + rng.uniform(-20.0, 20.0), 0.0), horizon))
    return sorted(ts)


def tag_visible(seed, n, w):
    """Per-arrival webhook-visible tags: dedicated RNG stream so arrival TIMES are
    identical across w for the same seed, and tagging is monotone in w."""
    rng = random.Random(seed ^ TAG_SEED_XOR)
    return [rng.random() < w for _ in range(n)]


def build_nights(variant, w, lam=LAMBDA_PER_MIN):
    """Return (list-of-nights, horizon); each night = [(t, visible)]."""
    if variant == "real":
        return [[(t, vis) for (_id, t, vis) in REAL_ARRIVALS]], REAL_HORIZON_MIN
    if variant == "empty":
        return [[]], SYN_HORIZON_MIN
    nights = []
    for i in range(N_SEEDS):
        if variant == "poisson":
            seed = BASE_SEED + 1000 + i
            ts = gen_poisson_times(seed, lam, SYN_HORIZON_MIN)
        elif variant == "burst":
            seed = BASE_SEED + 2000 + i
            ts = gen_burst_times(seed, SYN_HORIZON_MIN)
        else:
            raise ValueError(variant)
        tags = tag_visible(seed, len(ts), w)
        nights.append(list(zip(ts, tags)))
    return nights, SYN_HORIZON_MIN


def compute_cell(policy, nights, horizon, overrides=None):
    """One (policy x variant-instance) cell: pooled over all nights."""
    pid, sweep, chain, event = policy
    ov = dict(PRIMARY)
    ov.update(overrides or {})
    lat_pool, turns_total, n_arr = [], 0, 0
    for arrivals in nights:
        caught, _unc, turns = run_policy(
            arrivals, horizon, sweep=sweep, chain=chain, event=event,
            phase=ov.get("phase", 0.0), work_min=ov.get("work_min", WORK_MIN_DEFAULT),
            chain_sweeps=ov["chain_sweeps"], webhook_wake_sweeps=ov["webhook_wake_sweeps"])
        lat_pool.extend(night_latencies(arrivals, caught))
        turns_total += turns
        n_arr += len(arrivals)
    return cell_metrics(lat_pool, turns_total, n_arr, EXEC_LAG_MIN)


# ---------------------------------------------------------------------------
# Sweep, winners, dominance
# ---------------------------------------------------------------------------

VARIANT_INSTANCES = ([("real", None)] +
                     [("poisson", w) for w in W_GRID] +
                     [("burst", w) for w in W_GRID] +
                     [("empty", None)])


def instance_key(variant, w):
    return variant if w is None else "%s-w%.2f" % (variant, w)


def compute_sweep():
    cells = {}
    nights_cache = {}
    for variant, w in VARIANT_INSTANCES:
        nights_cache[(variant, w)] = build_nights(variant, w)
    for policy in POLICIES:
        for variant, w in VARIANT_INSTANCES:
            nights, horizon = nights_cache[(variant, w)]
            cells[(policy[0], instance_key(variant, w))] = compute_cell(policy, nights, horizon)
    return cells


def winners(cells):
    """Per (variant-instance x def): min turns_per_catch among p95<=2h survivors.
    Ties broken by fewer turns, then grid order (simplest-first). Empty night has
    no catches -> winner n/a, standing cost reported instead."""
    out = {}
    for variant, w in VARIANT_INSTANCES:
        ik = instance_key(variant, w)
        for defn in ("defA", "defB"):
            surv = []
            for pid in POLICY_IDS:
                c = cells[(pid, ik)]
                if c[defn]["pass_p95_le_2h"] and c["catches"] > 0:
                    surv.append((c["turns_per_catch"], c["turns"], POLICY_IDS.index(pid), pid))
            key = "%s|%s" % (ik, defn)
            if variant == "empty":
                out[key] = {"winner": None,
                            "note": "no catches - standing cost/night: " + ", ".join(
                                "%s=%d" % (pid, cells[(pid, ik)]["turns"]) for pid in POLICY_IDS),
                            "survivors": []}
                continue
            surv.sort()
            if not surv:
                out[key] = {"winner": None, "note": "NO policy satisfies p95<=2h", "survivors": []}
                continue
            wtpc, _wt, _wi, wpid = surv[0]
            ties = [p for (t2, _a, _b, p) in surv if abs(t2 - wtpc) <= 1e-6 and p != wpid]
            margin = (surv[len(ties) + 1][0] - wtpc) if len(surv) > len(ties) + 1 else None
            out[key] = {"winner": wpid, "winner_turns_per_catch": wtpc, "ties": ties,
                        "margin_vs_next": margin,
                        "survivors": [p for (_t, _a, _b, p) in surv]}
    return out


DOM_METRICS = ("turns", "turns_per_catch", "p95", "missed")


def cell_vector(c, defn):
    p95 = c[defn]["p95"]
    return (float(c["turns"]), float(c["turns_per_catch"]),
            float(p95) if p95 is not None else 0.0, float(c[defn]["missed_gt_2h"]))


def dominance(cells):
    """A strictly dominates B iff A is no worse on every metric of every
    (variant-instance x def) cell and strictly better somewhere."""
    pairs = []
    for a in POLICY_IDS:
        for b in POLICY_IDS:
            if a == b:
                continue
            no_worse, strictly = True, False
            for variant, w in VARIANT_INSTANCES:
                ik = instance_key(variant, w)
                for defn in ("defA", "defB"):
                    va = cell_vector(cells[(a, ik)], defn)
                    vb = cell_vector(cells[(b, ik)], defn)
                    for xa, xb in zip(va, vb):
                        if xa > xb + 1e-9:
                            no_worse = False
                        elif xa < xb - 1e-9:
                            strictly = True
                if not no_worse:
                    break
            if no_worse and strictly:
                pairs.append({"dominator": a, "dominated": b})
    dominated = sorted({p["dominated"] for p in pairs})
    return {"pairs": pairs, "strictly_dominated_policies": dominated}


# ---------------------------------------------------------------------------
# Sensitivity runs
# ---------------------------------------------------------------------------


def compute_sensitivity(cells):
    sens = {}

    # S1 - catch-definition flips (from the main sweep).
    flips = []
    for (pid, ik), c in sorted(cells.items()):
        if c["catches"] > 0 and c["defA"]["pass_p95_le_2h"] != c["defB"]["pass_p95_le_2h"]:
            flips.append({"policy": pid, "instance": ik,
                          "defA_p95": c["defA"]["p95"], "defB_p95": c["defB"]["p95"]})
    sens["S1_catch_definition_flips"] = flips

    # S2 - chain wakes DO sweep (counterfactual vs the E2 live proof).
    s2 = {}
    chain_pol = POLICIES[3]
    for variant, w in VARIANT_INSTANCES:
        nights, horizon = build_nights(variant, w)
        c = compute_cell(chain_pol, nights, horizon, overrides={"chain_sweeps": True})
        s2[instance_key(variant, w)] = c
    sens["S2_chain_sweeps_true"] = {
        "cells": s2,
        "note": "counterfactual: primary uses chain_sweeps=False per the E2 live proof "
                "(seat awake on chain during 03:15-03:28Z arrivals, caught only at 06:0x)"}

    # S3 - webhook wakes do NOT sweep inboxes (pessimistic for event policies).
    s3 = {}
    for pol in (POLICIES[4], POLICIES[5]):
        for variant, w in VARIANT_INSTANCES:
            nights, horizon = build_nights(variant, w)
            c = compute_cell(pol, nights, horizon, overrides={"webhook_wake_sweeps": False})
            s3["%s|%s" % (pol[0], instance_key(variant, w))] = c
    sens["S3_webhook_wake_sweeps_false"] = s3

    # S4 - chain work-window length {60, 240} (primary 120), real + poisson-w0.
    s4 = {}
    for wm in (60.0, 240.0):
        for variant, w in (("real", None), ("poisson", 0.0)):
            nights, horizon = build_nights(variant, w)
            c = compute_cell(chain_pol, nights, horizon, overrides={"work_min": wm})
            s4["work_min=%d|%s" % (int(wm), instance_key(variant, w))] = c
    sens["S4_chain_work_window"] = s4

    # S5 - E2 arrival late bound (03:28Z instead of 03:15Z), real trace.
    late = [(t if _id != "E2" else E2_LATE_BOUND_MIN, vis) for (_id, t, vis) in REAL_ARRIVALS]
    s5 = {}
    for pol in POLICIES:
        s5[pol[0]] = compute_cell(pol, [late], REAL_HORIZON_MIN)
    sens["S5_E2_late_bound"] = s5

    # S6 - fold E1+E2 into one datapoint (probe's fold): drop E1, keep E2.
    folded = [(t, vis) for (_id, t, vis) in REAL_ARRIVALS if _id != "E1"]
    s6 = {}
    for pol in POLICIES:
        s6[pol[0]] = compute_cell(pol, [folded], REAL_HORIZON_MIN)
    sens["S6_fold_E1_E2"] = s6

    # S7 - cron phase on the real trace (fires at phase, phase+P, ...).
    s7 = {}
    for pol, phases in ((POLICIES[0], (0.0, 30.0, 60.0, 90.0)), (POLICIES[1], (0.0, 30.0))):
        for ph in phases:
            nights, horizon = build_nights("real", None)
            c = compute_cell(pol, nights, horizon, overrides={"phase": ph})
            s7["%s|phase=%d" % (pol[0], int(ph))] = c
    sens["S7_cron_phase_real"] = s7

    # S8 - alternative rate derivation lambda = 4/732 (drop timeless E5), w=0.
    s8 = {}
    s8_nights = []
    for i in range(N_SEEDS):
        seed = BASE_SEED + 3000 + i
        ts = gen_poisson_times(seed, LAMBDA_ALT_PER_MIN, SYN_HORIZON_MIN)
        s8_nights.append(list(zip(ts, tag_visible(seed, len(ts), 0.0))))
    for pol in POLICIES:
        s8[pol[0]] = compute_cell(pol, s8_nights, SYN_HORIZON_MIN)
    sens["S8_alt_lambda_4_over_732_w0"] = s8

    return sens


# ---------------------------------------------------------------------------
# Assemble results
# ---------------------------------------------------------------------------


def compute_all():
    cells = compute_sweep()
    win = winners(cells)
    dom = dominance(cells)
    sens = compute_sensitivity(cells)

    sweep_rows = []
    for pid in POLICY_IDS:
        for variant, w in VARIANT_INSTANCES:
            ik = instance_key(variant, w)
            c = cells[(pid, ik)]
            sweep_rows.append({"policy": pid, "instance": ik, **c})

    observed = {
        "note": "what the real night actually delivered under its nominal failsafe-2h "
                "posture (the 04:0xZ wake did not sweep fm): idealized replay understates "
                "real latency - the binding failure was sweep fidelity, not cadence",
        "observed_latencies_defA": OBSERVED_LATENCY_DEFA,
        "observed_p95_defA": nearest_rank(sorted(OBSERVED_LATENCY_DEFA.values()), 0.95),
    }
    # per-event idealized latencies for the audit (recomputed directly):
    caught, _u, _t = run_policy([(t, v) for (_i, t, v) in REAL_ARRIVALS], REAL_HORIZON_MIN, sweep=120.0)
    observed["idealized_failsafe_2h_latencies_defA"] = {
        REAL_ARRIVALS[i][0]: caught[i] - REAL_ARRIVALS[i][1] for i in range(len(REAL_ARRIVALS))}

    results = {
        "meta": {
            "sim": "verdict-014-routine-cadence-economics",
            "answers": "idea-engine PROPOSAL 012 (INTAKE 012, finalizes as VERDICT 014)",
            "units": "worker-turns (cost model C as-given: 1/sweep, 1/chain-re-arm, ~0/webhook wake)",
            "catch_definitions": {
                "defA": "latency to the wake that reads the trigger (E4 -> 90 min)",
                "defB": "latency to done-when evidence = wake + %.1f min measured exec lag (E4 -> 121.4 min)" % EXEC_LAG_MIN},
            "constraint": "p95 catch-latency <= 120 min, uncaught arrivals count as +inf",
            "percentile_method": "nearest-rank on pooled latencies (all seeds pooled)",
            "seeds": {"n": N_SEEDS, "base": BASE_SEED,
                      "poisson": "BASE+1000+i", "burst": "BASE+2000+i", "alt_lambda": "BASE+3000+i",
                      "tag_stream": "seed XOR 0x5EED7A65 (times identical across w)"},
            "lambda_per_min": LAMBDA_PER_MIN,
            "lambda_derivation": "5 real arrivals (E1..E5; E5 timeless but real) / 732 min window = 0.41/h; alt 4/732 in S8",
            "horizons_min": {"real": REAL_HORIZON_MIN, "synthetic": SYN_HORIZON_MIN},
            "primary_assumptions": PRIMARY,
        },
        "pins": PINS,
        "trace": {
            "arrivals": [{"id": i, "t_min": t, "webhook_visible": v} for (i, t, v) in REAL_ARRIVALS],
            "excluded": {"E5": "no recorded arrival time (labels.json G8) - rate-counted, not replayed"},
            "null_sweeps_observed": ["N1 06:0x", "N2 08:00Z", "N3 12:00Z"],
            "webhook_visible_class": "EMPTY on the real trace (labels.json G11)",
        },
        "grid": {
            "policies": POLICY_IDS,
            "variants": [instance_key(v, w) for (v, w) in VARIANT_INSTANCES],
            "w_grid": W_GRID,
            "defs": ["defA", "defB"],
        },
        "sweep": sweep_rows,
        "winners": win,
        "dominance": dom,
        "sensitivity": sens,
        "audit": {
            "observed_vs_idealized": observed,
            "hand_derived_expectations": "see self-check battery in this script (real-trace latencies, turns, chain fire count, def-B flip)",
        },
    }
    return results, cells


# ---------------------------------------------------------------------------
# JSON canonicalization (inf-safe, deterministic)
# ---------------------------------------------------------------------------


def sanitize(obj):
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(x) for x in obj]
    if isinstance(obj, float):
        if math.isinf(obj):
            return "inf"
        return round(obj, 4)
    return obj


def canon(obj):
    return json.dumps(sanitize(obj), sort_keys=True, indent=1, allow_nan=False)


# ---------------------------------------------------------------------------
# Self-checks
# ---------------------------------------------------------------------------

CHECKS = {"passed": 0, "failed": 0, "failures": []}


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        CHECKS["failures"].append(label)


def approx(a, b, tol=1e-6):
    if a is None or b is None:
        return a is b
    if math.isinf(a) or math.isinf(b):
        return a == b
    return abs(a - b) <= tol


def run_self_checks(results, cells):
    real = {pid: cells[(pid, "real")] for pid in POLICY_IDS}

    # -- hand-derived real-trace latencies (def-A), turns, catches ----------
    def lat_list(pid, sweep, phase=0.0, chain=False, event=False, arrivals=None):
        arr = arrivals or [(t, v) for (_i, t, v) in REAL_ARRIVALS]
        caught, unc, turns = run_policy(arr, REAL_HORIZON_MIN, sweep=sweep, phase=phase,
                                        chain=chain, event=event)
        return night_latencies(arr, caught), turns

    l2h, t2h = lat_list("failsafe-2h", 120.0)
    check(l2h == [58.0, 45.0, 87.0, 90.0], "real failsafe-2h defA latencies = [58,45,87,90]")
    check(t2h == 7, "real failsafe-2h turns = 7 sweeps")
    l1h, t1h = lat_list("failsafe-1h", 60.0)
    check(l1h == [58.0, 45.0, 27.0, 30.0], "real failsafe-1h defA latencies = [58,45,27,30]")
    check(t1h == 13, "real failsafe-1h turns = 13")
    l30, t30 = lat_list("failsafe-30m", 30.0)
    check(l30 == [28.0, 15.0, 27.0, 0.0], "real failsafe-30m defA latencies = [28,15,27,0]")
    check(t30 == 25, "real failsafe-30m turns = 25")
    check(l30[3] == 0.0, "E4 arrival exactly on a 30m fire -> latency 0 (edge)")

    # -- chain policy: hand-derived fire count -------------------------------
    arr = [(t, v) for (_i, t, v) in REAL_ARRIVALS]
    _c, _u, tch = run_policy(arr, REAL_HORIZON_MIN, sweep=120.0, chain=True)
    check(tch == 31, "real chain policy turns = 7 sweeps + 24 chain re-arms = 31 (hand-derived: windows [240,360] -> 8 fires, [480,720] merged -> 16)")
    check(approx(real["failsafe-2h+chain-15m"]["turns_per_catch"], 31.0 / 4.0),
          "real chain turns/catch = 7.75")

    # -- headline real-trace cells ------------------------------------------
    check(approx(real["failsafe-2h"]["turns_per_catch"], 1.75), "real failsafe-2h = 1.75 turns/catch")
    check(approx(real["failsafe-1h"]["turns_per_catch"], 3.25), "real failsafe-1h = 3.25 turns/catch")
    check(approx(real["failsafe-30m"]["turns_per_catch"], 6.25), "real failsafe-30m = 6.25 turns/catch")
    check(approx(real["failsafe-2h"]["defA"]["p95"], 90.0), "real failsafe-2h defA p95 = 90")
    check(approx(real["failsafe-2h"]["defB"]["p95"], 121.4), "real failsafe-2h defB p95 = 121.4 (the E4 2h01m fork)")
    check(real["failsafe-2h"]["defA"]["pass_p95_le_2h"] is True, "real failsafe-2h PASSES p95<=2h under def-A")
    check(real["failsafe-2h"]["defB"]["pass_p95_le_2h"] is False, "real failsafe-2h FAILS p95<=2h under def-B (by 1.4 min)")
    check(real["failsafe-2h"]["defB"]["missed_gt_2h"] == 1, "real failsafe-2h defB missed count = 1 (E4)")
    check(approx(real["failsafe-1h"]["defB"]["p95"], 89.4), "real failsafe-1h defB p95 = 89.4 (passes)")
    check(real["event-driven-only"]["catches"] == 0 and real["event-driven-only"]["turns"] == 0,
          "real event-driven-only: 0 catches, 0 turns (webhook class EMPTY)")
    check(real["event-driven-only"]["uncaught"] == 4, "real event-driven-only: all 4 arrivals uncaught")
    check(real["event-driven-only"]["defA"]["p95"] == math.inf, "real event-driven-only p95 = inf")

    # -- hybrid == failsafe-2h wherever w=0 ----------------------------------
    for ik in ("real", "poisson-w0.00", "burst-w0.00", "empty"):
        a, b = cells[("hybrid(event+failsafe-2h)", ik)], cells[("failsafe-2h", ik)]
        check(canon(a) == canon(b), "hybrid == failsafe-2h identically at %s (no webhook arrivals)" % ik)

    # -- observed vs idealized ------------------------------------------------
    obs = results["audit"]["observed_vs_idealized"]
    check(approx(obs["observed_p95_defA"], 178.0),
          "OBSERVED real-night p95 (defA) = 178 min - the real night VIOLATED the 2h p95 under its nominal failsafe-2h posture")
    check(obs["idealized_failsafe_2h_latencies_defA"]["E1"] == 58.0 and
          OBSERVED_LATENCY_DEFA["E1"] == 178.0,
          "idealized replay catches E1 at 04:00 (58 min) vs observed 06:0x (178 min): the 04:0x wake did not sweep fm - idealization gap disclosed")

    # -- empty-night standing costs ------------------------------------------
    empty_turns = [cells[(pid, "empty")]["turns"] for pid in POLICY_IDS]
    check(empty_turns == [7, 13, 25, 7, 0, 7], "empty-night standing turns = [7,13,25,7,0,7]")
    check(all(cells[(pid, "empty")]["catches"] == 0 for pid in POLICY_IDS), "empty night: zero catches everywhere")

    # -- structural invariants over the whole sweep ---------------------------
    for variant, w in VARIANT_INSTANCES:
        ik = instance_key(variant, w)
        c2, c1, c3 = cells[("failsafe-2h", ik)], cells[("failsafe-1h", ik)], cells[("failsafe-30m", ik)]
        check(c3["turns"] >= c1["turns"] >= c2["turns"], "turns monotone in cadence @ %s" % ik)
        if c2["arrivals"] > 0:
            for defn in ("defA", "defB"):
                check(c3[defn]["p95"] <= c1[defn]["p95"] + EPS <= c2[defn]["p95"] + 2 * EPS,
                      "p95 monotone in cadence @ %s %s" % (ik, defn))
        for pid in ("failsafe-2h", "failsafe-1h", "failsafe-30m", "failsafe-2h+chain-15m",
                    "hybrid(event+failsafe-2h)"):
            check(cells[(pid, ik)]["uncaught"] == 0, "failsafe-bearing policy catches everything @ %s %s" % (pid, ik))
        chn = cells[("failsafe-2h+chain-15m", ik)]
        check(chn["turns"] >= c2["turns"], "chain turns >= failsafe-2h turns @ %s" % ik)
        for defn in ("defA", "defB"):
            check(approx(chn[defn]["p95"], c2[defn]["p95"]),
                  "chain p95 == failsafe-2h p95 (chain wakes don't sweep, E2 live proof) @ %s %s" % (ik, defn))
            hyb = cells[("hybrid(event+failsafe-2h)", ik)]
            if c2["arrivals"] > 0:
                check(hyb[defn]["p95"] <= c2[defn]["p95"] + EPS, "hybrid p95 <= failsafe-2h p95 @ %s %s" % (ik, defn))

    # def-A latency bounded by sweep period for pure failsafe policies
    for (pid, period) in (("failsafe-2h", 120.0), ("failsafe-1h", 60.0), ("failsafe-30m", 30.0)):
        for variant, w in VARIANT_INSTANCES:
            c = cells[(pid, instance_key(variant, w))]
            if c["arrivals"] > 0:
                check(c["defA"]["p95"] <= period + EPS, "defA p95 <= period @ %s %s" % (pid, instance_key(variant, w)))

    # -- w-monotonicity of event-driven-only ---------------------------------
    for variant in ("poisson", "burst"):
        prev_catch = -1
        for w in W_GRID:
            c = cells[("event-driven-only", instance_key(variant, w))]
            check(c["catches"] >= prev_catch, "event-driven catches non-decreasing in w @ %s w=%.2f" % (variant, w))
            prev_catch = c["catches"]
        c0 = cells[("event-driven-only", instance_key(variant, 0.0))]
        c1w = cells[("event-driven-only", instance_key(variant, 1.0))]
        check(c0["catches"] == 0, "event-driven catches 0 at w=0 @ %s" % variant)
        check(c1w["uncaught"] == 0 and approx(c1w["defA"]["p95"], 0.0),
              "event-driven at w=1: all caught at latency 0 @ %s" % variant)
        # arrival times identical across w (tag-stream isolation)
        for pid in ("failsafe-2h",):
            arrs = {cells[(pid, instance_key(variant, w))]["arrivals"] for w in W_GRID}
            check(len(arrs) == 1, "arrival count identical across w @ %s" % variant)

    # -- seeded corpus sanity --------------------------------------------------
    n_poisson = cells[("failsafe-2h", "poisson-w0.00")]["arrivals"]
    check(130 <= n_poisson <= 270, "poisson total arrivals over %d nights in 2-sigma band (got %d)" % (N_SEEDS, n_poisson))
    n_burst = cells[("failsafe-2h", "burst-w0.00")]["arrivals"]
    check(4 * N_SEEDS <= n_burst <= 6 * N_SEEDS, "burst total arrivals in [160,240] (got %d)" % n_burst)

    # -- dominance claims the verdict rests on --------------------------------
    dom_pairs = {(p["dominator"], p["dominated"]) for p in results["dominance"]["pairs"]}
    check(("failsafe-2h", "failsafe-2h+chain-15m") in dom_pairs,
          "chain policy strictly dominated by plain failsafe-2h")
    check(("hybrid(event+failsafe-2h)", "failsafe-2h") in dom_pairs,
          "failsafe-2h strictly dominated by hybrid across the full grid (equal at w=0, better at w>0)")
    check("event-driven-only" not in results["dominance"]["strictly_dominated_policies"],
          "event-driven-only NOT dominated (wins at w=1, fails at w=0 - w is load-bearing)")
    check("failsafe-1h" not in results["dominance"]["strictly_dominated_policies"],
          "failsafe-1h not dominated")
    check("failsafe-30m" not in results["dominance"]["strictly_dominated_policies"],
          "failsafe-30m not dominated (buys p95 with turns)")

    # -- winners the verdict quotes -------------------------------------------
    wA = results["winners"]["real|defA"]
    check(wA["winner"] == "failsafe-2h" and wA["ties"] == ["hybrid(event+failsafe-2h)"],
          "real defA winner: failsafe-2h tied with hybrid at 1.75 turns/catch")
    wB = results["winners"]["real|defB"]
    check(wB["winner"] == "failsafe-1h", "real defB winner: failsafe-1h (2h family fails by 1.4 min)")
    for w in W_GRID:
        wc = results["winners"]["poisson-w%.2f|defA" % w]
        if w == 1.0:
            check(wc["winner"] == "event-driven-only", "poisson w=1 defA winner: event-driven-only (0 turns)")
        else:
            check(wc["winner"] in ("failsafe-2h", "hybrid(event+failsafe-2h)", "event-driven-only"),
                  "poisson w=%.2f defA winner sane" % w)

    # -- sensitivity claims -----------------------------------------------------
    s1 = results["sensitivity"]["S1_catch_definition_flips"]
    check(any(f["policy"] == "failsafe-2h" and f["instance"] == "real" for f in s1),
          "S1: the E4 catch-definition fork flips real failsafe-2h pass->fail")
    s5 = results["sensitivity"]["S5_E2_late_bound"]
    check(s5["failsafe-2h"]["defA"]["pass_p95_le_2h"] is True and
          s5["failsafe-2h"]["defB"]["pass_p95_le_2h"] is False,
          "S5: E2 late bound does not flip any real failsafe-2h constraint cell")
    s6 = results["sensitivity"]["S6_fold_E1_E2"]
    r6 = sorted((s6[p]["turns_per_catch"], p) for p in POLICY_IDS if s6[p]["catches"] > 0)
    r0 = sorted((real[p]["turns_per_catch"], p) for p in POLICY_IDS if real[p]["catches"] > 0)
    check([p for _t, p in r6] == [p for _t, p in r0],
          "S6: folding E1+E2 rescales turns/catch uniformly - ranking unchanged")
    s7 = results["sensitivity"]["S7_cron_phase_real"]
    check(s7["failsafe-2h|phase=90"]["defB"]["pass_p95_le_2h"] is True,
          "S7: phase=90 rescues failsafe-2h under def-B on THIS n=1 trace (p95 %.1f) - n=1 fragility, not a design rule"
          % s7["failsafe-2h|phase=90"]["defB"]["p95"])
    check(s7["failsafe-2h|phase=0"]["defB"]["pass_p95_le_2h"] is False,
          "S7: phase=0 failsafe-2h still fails def-B")
    s2 = results["sensitivity"]["S2_chain_sweeps_true"]["cells"]
    # Counterfactual chain-sweeps CAN be cheaper than the as-observed chain: the
    # chain fire at 510 (=480+30) coincides with E4's arrival and catches it at
    # latency 0, so the work window closes at 630 instead of being re-extended
    # by the 600 sweep (7 sweeps + 8 + 10 chain fires = 25 turns vs 31) - but it
    # stays far above plain failsafe-2h and never approaches the winner's cost.
    check(s2["real"]["turns"] == 25, "S2: chain-sweeps counterfactual real turns = 25 (hand-derived: windows [240,360] 8 fires + [480,630] 10 fires)")
    check(s2["real"]["turns"] > real["failsafe-2h"]["turns"],
          "S2: even sweeping chain wakes cost >> plain failsafe-2h (26 vs 7 turns)")
    check(s2["real"]["turns_per_catch"] > real["failsafe-2h"]["turns_per_catch"] + 1.0,
          "S2: chain-sweeps counterfactual never approaches the winner's turns/catch")
    check(s1 and all(f["policy"] in ("failsafe-2h", "failsafe-2h+chain-15m", "hybrid(event+failsafe-2h)") for f in s1),
          "S1: every catch-definition flip is in the failsafe-2h family (1h/30m never flip)")
    s3 = results["sensitivity"]["S3_webhook_wake_sweeps_false"]
    c = s3["event-driven-only|poisson-w1.00"]
    check(c["uncaught"] == 0, "S3: at w=1 event-driven catches all even without inbox-sweeping wakes")
    s8 = results["sensitivity"]["S8_alt_lambda_4_over_732_w0"]
    surv8 = [(s8[p]["turns_per_catch"], p) for p in POLICY_IDS
             if s8[p]["catches"] > 0 and s8[p]["defA"]["pass_p95_le_2h"]]
    check(min(surv8)[1] in ("failsafe-2h", "hybrid(event+failsafe-2h)"),
          "S8: alt-lambda derivation does not change the defA winner family")

    # -- labels.json consistency ------------------------------------------------
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "labels.json"), "r", encoding="utf-8") as fh:
        labels = json.load(fh)
    ev = {e["id"]: e for e in labels["events"]}
    for (eid, t, _v) in REAL_ARRIVALS:
        check(approx(ev[eid]["t_arrival_min"], t), "labels.json arrival time matches embedded constant for %s" % eid)
        check(ev[eid]["evidence_commit"] == PINS["event_evidence"][eid],
              "labels.json evidence SHA matches pin for %s" % eid)
        check(ev[eid]["tag"] == "inbox-only", "labels.json tag inbox-only for %s" % eid)
    check(ev["E5"]["t_arrival_min"] is None, "labels.json E5 arrival honestly null")
    check(len([e for e in labels["events"] if e["tag"] == "null-sweep"]) == 3, "labels.json carries 3 null sweeps")
    check(len(labels["gaps"]) == 12, "labels.json carries all 12 documented gaps")
    check(approx(ev["E2"]["t_arrival_min_late_bound"], E2_LATE_BOUND_MIN), "labels.json E2 late bound matches")

    # -- determinism (in-process double run) -------------------------------------
    results2, _cells2 = compute_all()
    check(canon(results) == canon(results2), "in-process double run: canonical results byte-identical")


# ---------------------------------------------------------------------------
# Report printing
# ---------------------------------------------------------------------------


def fmt(x, width=8):
    if x is None:
        return " " * (width - 3) + "n/a"
    if isinstance(x, float) and math.isinf(x):
        return " " * (width - 3) + "inf"
    if isinstance(x, float):
        return ("%" + str(width) + ".2f") % x
    return ("%" + str(width) + "d") % x


def print_table(results, cells):
    print("PER-CELL TABLE (policy x variant-instance; pooled over %d seeds for synthetics)" % N_SEEDS)
    print("units: worker-turns; latency minutes; defA = to catching wake, defB = +%.1f min exec lag" % EXEC_LAG_MIN)
    hdr = ("%-26s %-16s %6s %6s %5s %8s | %8s %8s %6s %4s | %8s %8s %6s %4s"
           % ("policy", "variant", "turns", "arrivs", "catch", "turns/ct",
              "A-med", "A-p95", "A-miss", "A-ok", "B-med", "B-p95", "B-miss", "B-ok"))
    print(hdr)
    print("-" * len(hdr))
    for pid in POLICY_IDS:
        for variant, w in VARIANT_INSTANCES:
            ik = instance_key(variant, w)
            c = cells[(pid, ik)]
            print("%-26s %-16s %6d %6d %5d %s | %s %s %6d %4s | %s %s %6d %4s" % (
                pid, ik, c["turns"], c["arrivals"], c["catches"], fmt(c["turns_per_catch"]),
                fmt(c["defA"]["median"]), fmt(c["defA"]["p95"]), c["defA"]["missed_gt_2h"],
                "PASS" if c["defA"]["pass_p95_le_2h"] else "FAIL",
                fmt(c["defB"]["median"]), fmt(c["defB"]["p95"]), c["defB"]["missed_gt_2h"],
                "PASS" if c["defB"]["pass_p95_le_2h"] else "FAIL"))
        print()

    print("WINNERS (min turns/catch s.t. p95<=2h):")
    for variant, w in VARIANT_INSTANCES:
        ik = instance_key(variant, w)
        for defn in ("defA", "defB"):
            k = "%s|%s" % (ik, defn)
            wv = results["winners"][k]
            if wv["winner"] is None:
                print("  %-22s %-4s -> %s" % (ik, defn, wv["note"]))
            else:
                ties = (" (tie: %s)" % ", ".join(wv["ties"])) if wv["ties"] else ""
                margin = ("margin +%.2f to next" % wv["margin_vs_next"]) if wv["margin_vs_next"] is not None else "no runner-up"
                print("  %-22s %-4s -> %s @ %.2f turns/catch%s; %s" % (
                    ik, defn, wv["winner"], wv["winner_turns_per_catch"], ties, margin))
    print()
    print("DOMINANCE (strict, across ALL variant-instances x both catch definitions):")
    for p in results["dominance"]["pairs"]:
        print("  %s strictly dominates %s" % (p["dominator"], p["dominated"]))
    print("  strictly dominated policies: %s" % (results["dominance"]["strictly_dominated_policies"] or "none"))
    print()
    print("KEY SENSITIVITIES:")
    print("  S1 catch-definition flips (pass<->fail on p95<=2h): %d cells, all in the failsafe-2h family"
          % len(results["sensitivity"]["S1_catch_definition_flips"]))
    s7 = results["sensitivity"]["S7_cron_phase_real"]
    print("  S7 cron phase (real, failsafe-2h defB p95): " + ", ".join(
        "ph=%s -> %.1f %s" % (k.split("=")[1], s7[k]["defB"]["p95"], "PASS" if s7[k]["defB"]["pass_p95_le_2h"] else "FAIL")
        for k in sorted(s7) if k.startswith("failsafe-2h")))
    print("  (full sensitivity blocks S1-S8 in results.json)")


def main():
    results, cells = compute_all()
    run_self_checks(results, cells)
    results["self_checks"] = {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                              "failures": CHECKS["failures"]}
    results["determinism"] = {
        "in_process_double_run": "byte-identical (self-checked)",
        "note": "no wall clock, no unseeded randomness, no network; seeds are committed constants"}

    print("=" * 100)
    print("verdict-014 - routine-cadence economics (idea-engine PROPOSAL 012 / INTAKE 012)")
    print("=" * 100)
    print()
    print_table(results, cells)
    print()

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "results.json")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(canon(results) + "\n")
    print("results.json written (%d bytes)" % os.path.getsize(out))
    print()
    print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
    for f in CHECKS["failures"]:
        print("  FAIL: %s" % f)
    return 1 if CHECKS["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
