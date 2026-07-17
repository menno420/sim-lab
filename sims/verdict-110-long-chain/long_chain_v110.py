#!/usr/bin/env python3
"""
VERDICT-110 independent verification simulator for idea-engine PROPOSAL-097
"the long chain: K specialized lanes each with ONE secondary skill wired as
a single ring recovers ~95% of the full-cross-training throughput gap."

Stdlib-only, deterministic. Independent re-implementation from the registered
spec. Builds four static servability graphs (DEDICATED, FULLFLEX, LONGCHAIN,
BUDDYPAIRS) over K=12 categories x K=12 lanes; draws i.i.d. per-category
demand max(0, Normal(mean=1.0, sd=SD_MAIN)); computes served = max-flow on
the source -> category -> lane -> sink graph via Edmonds-Karp (Evaluator A)
paired against a Ford-Fulkerson DFS augmenting variant (Evaluator B) on the
same four means (twin evaluator gate at 1e-9). Runs N_REPS=20000 at
SEED_MAIN=20260717 for the gated slice, the CV robustness band across
sd in {0.30, 0.35, 0.40} at seeds {20260716, 20260717, 20260719} for R4,
and sd=0.50 seed=20260718 as a DISCLOSED NON-GATING cross-check.

Gates R1->R2->R3->R4 in order. Verdict never softened. >=12 self-checks
gate exit 0. Byte-identical double run of the results dict enforced before
results.json is written once.

Run with no args -> full N_REPS=20000 gated run, writes results.json + fixtures.json.
Run with `smoke` arg -> quick N_REPS=500 direction check, no results written.
"""
import collections
import hashlib
import json
import math
import os
import random
import sys

# ---------------------------------------------------------------------------
# Registered constants (pre-registered spec)
# ---------------------------------------------------------------------------
K = 12
N_REPS = 20000
SEED_MAIN = 20260717
LANE_CAP = 1.0
MEAN = 1.0
SD_MAIN = 0.35
CV_BAND = [(0.30, 20260716), (0.35, 20260717), (0.40, 20260719)]
SD_BOUNDARY = 0.50
SEED_BOUNDARY = 20260718
N_BOOT = 200            # bootstrap resamples for R1 SEM (documented)
LARGE_CAP = 1e9         # "infinity" for cat->lane edges

# ---------------------------------------------------------------------------
# Static servability graphs (category i -> lane j allowed edges)
# ---------------------------------------------------------------------------
def edges_dedicated(k):
    return [(i, i) for i in range(k)]


def edges_fullflex(k):
    return [(i, j) for i in range(k) for j in range(k)]


def edges_longchain(k):
    # lane j serves cats j and (j-1) mod k  <=>  cat i is served by lanes i and (i+1) mod k
    # equivalently: (cat i, lane j) with j in {i, (i-1) mod k}
    # We express with the proposal's own convention: "lane i serves cat i and cat (i+1) mod K"
    # i.e. (cat c, lane l) present iff c == l or c == (l+1) mod K
    edges = []
    for l in range(k):
        edges.append(((l) % k, l))              # cat = lane
        edges.append(((l + 1) % k, l))          # cat = (lane + 1) mod K -- secondary
    return sorted(set(edges))


def edges_buddypairs(k):
    # lanes {2p, 2p+1} mutually cover cats {2p, 2p+1}. Requires K even.
    assert k % 2 == 0
    edges = []
    for p in range(k // 2):
        a, b = 2 * p, 2 * p + 1
        edges.append((a, a))
        edges.append((a, b))
        edges.append((b, a))
        edges.append((b, b))
    return sorted(set(edges))


STRUCTURES = {
    "DEDICATED": edges_dedicated(K),
    "FULLFLEX": edges_fullflex(K),
    "LONGCHAIN": edges_longchain(K),
    "BUDDYPAIRS": edges_buddypairs(K),
}


# ---------------------------------------------------------------------------
# Max-flow evaluators. Node layout: 0=source, 1..K=cats, K+1..2K=lanes, 2K+1=sink.
# ---------------------------------------------------------------------------
SOURCE = 0
def cat_node(i):
    return 1 + i
def lane_node(j):
    return 1 + K + j
SINK = 1 + 2 * K


def _build_residual(demand, allowed_edges):
    """Return residual graph as dict-of-dicts of capacities.
    We store only forward edges initially with their capacity; reverse edges start at 0.
    """
    n = SINK + 1
    cap = [dict() for _ in range(n)]
    # source -> cat_i with capacity demand[i]
    for i in range(K):
        cap[SOURCE][cat_node(i)] = demand[i]
        cap[cat_node(i)].setdefault(SOURCE, 0.0)
    # cat_i -> lane_j for allowed edges
    for (i, j) in allowed_edges:
        cap[cat_node(i)][lane_node(j)] = LARGE_CAP
        cap[lane_node(j)].setdefault(cat_node(i), 0.0)
    # lane_j -> sink with capacity LANE_CAP
    for j in range(K):
        cap[lane_node(j)][SINK] = LANE_CAP
        cap[SINK].setdefault(lane_node(j), 0.0)
    return cap


def maxflow_edmonds_karp(demand, allowed_edges):
    """Evaluator A: Edmonds-Karp (BFS shortest augmenting path in edges)."""
    cap = _build_residual(demand, allowed_edges)
    n = len(cap)
    total = 0.0
    while True:
        # BFS
        parent = [-1] * n
        parent[SOURCE] = SOURCE
        queue = collections.deque([SOURCE])
        found = False
        while queue:
            u = queue.popleft()
            # deterministic order: iterate neighbors sorted
            for v in sorted(cap[u].keys()):
                if parent[v] == -1 and cap[u][v] > 0.0:
                    parent[v] = u
                    if v == SINK:
                        found = True
                        break
                    queue.append(v)
            if found:
                break
        if not found:
            break
        # bottleneck along path
        bn = math.inf
        v = SINK
        while v != SOURCE:
            u = parent[v]
            bn = min(bn, cap[u][v])
            v = u
        # augment
        v = SINK
        while v != SOURCE:
            u = parent[v]
            cap[u][v] -= bn
            cap[v][u] += bn
            v = u
        total += bn
    return total


def maxflow_ford_fulkerson_dfs(demand, allowed_edges):
    """Evaluator B: Ford-Fulkerson with DFS augmenting path (iterative, deterministic order)."""
    cap = _build_residual(demand, allowed_edges)
    n = len(cap)
    total = 0.0
    while True:
        parent = [-1] * n
        parent[SOURCE] = SOURCE
        stack = [SOURCE]
        found = False
        while stack:
            u = stack.pop()
            if u == SINK:
                found = True
                break
            # deterministic order: push neighbors in reverse-sorted order so pop yields sorted order
            for v in sorted(cap[u].keys(), reverse=True):
                if parent[v] == -1 and cap[u][v] > 0.0:
                    parent[v] = u
                    stack.append(v)
        if not found:
            break
        bn = math.inf
        v = SINK
        while v != SOURCE:
            u = parent[v]
            bn = min(bn, cap[u][v])
            v = u
        v = SINK
        while v != SOURCE:
            u = parent[v]
            cap[u][v] -= bn
            cap[v][u] += bn
            v = u
        total += bn
    return total


# ---------------------------------------------------------------------------
# Demand draws (own in-file seeds)
# ---------------------------------------------------------------------------
def draw_demand(rng, sd):
    """max(0, Normal(MEAN, sd)) i.i.d. across K categories."""
    return [max(0.0, rng.gauss(MEAN, sd)) for _ in range(K)]


# ---------------------------------------------------------------------------
# Feasibility bound for self-check (min-cut trivial upper bound)
# ---------------------------------------------------------------------------
def feasibility_bound(demand):
    return min(sum(demand), K * LANE_CAP)


# ---------------------------------------------------------------------------
# One full pass at (sd, seed, n_reps).  Returns per-structure list of served
# values (Evaluator A) plus twin-evaluator-A/B means for gating.
# ---------------------------------------------------------------------------
STRUCT_NAMES = ("DEDICATED", "FULLFLEX", "LONGCHAIN", "BUDDYPAIRS")


def run_pass(sd, seed, n_reps, twin=False):
    """Return dict with per-structure list of served (Evaluator A). If twin=True,
    also compute Evaluator B means and return them.

    Rep i uses a fresh draw from the master rng; demand vectors are shared
    across the four structures within a rep (this is how the gates are defined).
    """
    rng = random.Random(seed)
    served_A = {name: [] for name in STRUCT_NAMES}
    served_B_means = None
    if twin:
        served_B_sum = {name: 0.0 for name in STRUCT_NAMES}
    for _ in range(n_reps):
        demand = draw_demand(rng, sd)
        for name in STRUCT_NAMES:
            edges = STRUCTURES[name]
            f = maxflow_edmonds_karp(demand, edges)
            served_A[name].append(f)
            if twin:
                g = maxflow_ford_fulkerson_dfs(demand, edges)
                served_B_sum[name] += g
                # Per-rep feasibility check woven in
                # (rare deep bug catch): |f - g| must be <= 1e-9
                if abs(f - g) > 1e-9:
                    raise SystemExit(
                        f"R1 twin-evaluator disagreement within a rep for {name}: "
                        f"A={f!r} B={g!r} delta={f-g!r}"
                    )
    if twin:
        served_B_means = {name: served_B_sum[name] / n_reps for name in STRUCT_NAMES}
    return served_A, served_B_means


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------
def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs, m=None):
    if m is None:
        m = mean(xs)
    if len(xs) < 2:
        return 0.0
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def sem(xs):
    return stdev(xs) / math.sqrt(len(xs))


def paired_diff_sem(a, b):
    """Paired-difference SEM over paired series a[i] - b[i]."""
    diffs = [ai - bi for ai, bi in zip(a, b)]
    return sem(diffs), mean(diffs)


def chain_recovery(m_dedicated, m_fullflex, m_longchain):
    denom = m_fullflex - m_dedicated
    if denom == 0:
        return float("nan")
    return (m_longchain - m_dedicated) / denom


def r1_bootstrap_sem(served, n_boot, seed_boot):
    """Bootstrap SEM of chain_recovery over paired resamples of the reps.

    Documented rule: N_BOOT bootstrap resamples (with replacement) over rep
    indices; for each resample recompute all four means and R1's ratio; SEM =
    stdev across the resamples.
    """
    n = len(served["DEDICATED"])
    rng = random.Random(seed_boot)
    recs = []
    ded = served["DEDICATED"]
    ff = served["FULLFLEX"]
    lc = served["LONGCHAIN"]
    for _ in range(n_boot):
        idxs = [rng.randrange(n) for _ in range(n)]
        md = sum(ded[i] for i in idxs) / n
        mf = sum(ff[i] for i in idxs) / n
        ml = sum(lc[i] for i in idxs) / n
        recs.append(chain_recovery(md, mf, ml))
    return stdev(recs)


# ---------------------------------------------------------------------------
# Canonical JSON hashing (sort_keys=True, separators=(",", ":"))
# ---------------------------------------------------------------------------
def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Fixtures for external readers
# ---------------------------------------------------------------------------
def build_fixtures():
    return {
        "spec_id": "VERDICT-110/PROPOSAL-097",
        "K": K,
        "lane_capacity": LANE_CAP,
        "demand": {
            "distribution": "max(0, Normal(mean=1.0, sd=SD)) i.i.d. across K categories",
            "sd_main": SD_MAIN,
            "cv_band_sd": [b[0] for b in CV_BAND],
            "cv_band_seeds": [b[1] for b in CV_BAND],
            "sd_boundary": SD_BOUNDARY,
            "seed_boundary": SEED_BOUNDARY,
            "seed_main": SEED_MAIN,
            "n_reps": N_REPS,
        },
        "structures": {
            name: {
                "edges": [list(e) for e in edges],
                "edge_count": len(edges),
            }
            for name, edges in STRUCTURES.items()
        },
    }


# ---------------------------------------------------------------------------
# Full pipeline (used both for the primary run and the byte-identical re-run)
# ---------------------------------------------------------------------------
def full_pipeline(n_reps, do_twin=True):
    """Execute all passes required for R1..R4 + sd=0.50 cross-check.

    Returns a plain dict suitable for canonical serialization.
    Does NOT include timing keys.
    """
    # ---- main slice: SEED_MAIN, SD_MAIN, N_REPS ----
    main_served, main_B_means = run_pass(SD_MAIN, SEED_MAIN, n_reps, twin=do_twin)
    means_A = {name: mean(main_served[name]) for name in STRUCT_NAMES}
    sems_A = {name: sem(main_served[name]) for name in STRUCT_NAMES}

    # per-rep dominance / feasibility self-checks (collected as bool aggregates)
    dominance_ff_ge_lc = True
    dominance_lc_ge_ded = True
    dominance_bp_ge_ded = True
    feasibility_all = True
    max_infeasible_gap = 0.0
    # Recompute demand feasibility bounds via re-run of RNG (deterministic)
    rng = random.Random(SEED_MAIN)
    for r in range(n_reps):
        demand = draw_demand(rng, SD_MAIN)
        bound = feasibility_bound(demand)
        for name in STRUCT_NAMES:
            v = main_served[name][r]
            # allow small numeric slack
            if v > bound + 1e-9:
                feasibility_all = False
                max_infeasible_gap = max(max_infeasible_gap, v - bound)
        if main_served["FULLFLEX"][r] + 1e-9 < main_served["LONGCHAIN"][r]:
            dominance_ff_ge_lc = False
        if main_served["LONGCHAIN"][r] + 1e-9 < main_served["DEDICATED"][r]:
            dominance_lc_ge_ded = False
        if main_served["BUDDYPAIRS"][r] + 1e-9 < main_served["DEDICATED"][r]:
            dominance_bp_ge_ded = False

    # ---- R1 twin-evaluator gate: A vs B means on the four structures ----
    twin_relerr = None
    twin_pass = True
    twin_details = {}
    if do_twin:
        twin_details["A_means"] = means_A
        twin_details["B_means"] = main_B_means
        max_re = 0.0
        for name in STRUCT_NAMES:
            a = means_A[name]
            b = main_B_means[name]
            re = abs(a - b)
            max_re = max(max_re, re)
        twin_relerr = max_re
        if max_re > 1e-9:
            twin_pass = False

    # ---- R1: chain_recovery ----
    r1_value = chain_recovery(means_A["DEDICATED"], means_A["FULLFLEX"], means_A["LONGCHAIN"])
    r1_threshold = 0.90
    r1_sem = r1_bootstrap_sem(main_served, N_BOOT, seed_boot=SEED_MAIN + 1)
    r1_margin_sigma = (r1_value - r1_threshold) / r1_sem if r1_sem > 0 else float("inf")
    r1_pass = r1_value >= r1_threshold

    # ---- R2: mean(FULLFLEX) - mean(DEDICATED) >= 0.02 (served-fraction) ----
    # served-fraction = served / K (fleet capacity is K)
    r2_gap_reps = [(f - d) / K for f, d in zip(main_served["FULLFLEX"], main_served["DEDICATED"])]
    r2_value = mean(r2_gap_reps)
    r2_sem = sem(r2_gap_reps)
    r2_threshold = 0.02
    r2_margin_sigma = (r2_value - r2_threshold) / r2_sem if r2_sem > 0 else float("inf")
    r2_pass = r2_value >= r2_threshold

    # ---- R3: mean(LONGCHAIN) - mean(BUDDYPAIRS) >= 0.01 (served-fraction) ----
    r3_gap_reps = [(l - b) / K for l, b in zip(main_served["LONGCHAIN"], main_served["BUDDYPAIRS"])]
    r3_value = mean(r3_gap_reps)
    r3_sem = sem(r3_gap_reps)
    r3_threshold = 0.01
    r3_margin_sigma = (r3_value - r3_threshold) / r3_sem if r3_sem > 0 else float("inf")
    r3_pass = r3_value >= r3_threshold

    # ---- R4: min chain_recovery over sd in CV band ----
    band_details = []
    for sd_v, seed_v in CV_BAND:
        served_band, _ = run_pass(sd_v, seed_v, n_reps, twin=False)
        m_ded = mean(served_band["DEDICATED"])
        m_ff = mean(served_band["FULLFLEX"])
        m_lc = mean(served_band["LONGCHAIN"])
        rec = chain_recovery(m_ded, m_ff, m_lc)
        # per-sd bootstrap SEM on chain_recovery (documented)
        rec_sem = r1_bootstrap_sem(served_band, N_BOOT, seed_boot=seed_v + 1)
        band_details.append({
            "sd": sd_v,
            "seed": seed_v,
            "mean_dedicated": m_ded,
            "mean_fullflex": m_ff,
            "mean_longchain": m_lc,
            "chain_recovery": rec,
            "chain_recovery_bootstrap_sem": rec_sem,
        })
    r4_min = min(bd["chain_recovery"] for bd in band_details)
    r4_min_idx = min(range(len(band_details)), key=lambda i: band_details[i]["chain_recovery"])
    r4_sem = band_details[r4_min_idx]["chain_recovery_bootstrap_sem"]
    r4_threshold = 0.90
    r4_margin_sigma = (r4_min - r4_threshold) / r4_sem if r4_sem > 0 else float("inf")
    r4_pass = r4_min >= r4_threshold

    # ---- sd=0.50 boundary (NON-gating cross-check) ----
    boundary_served, _ = run_pass(SD_BOUNDARY, SEED_BOUNDARY, n_reps, twin=False)
    b_ded = mean(boundary_served["DEDICATED"])
    b_ff = mean(boundary_served["FULLFLEX"])
    b_lc = mean(boundary_served["LONGCHAIN"])
    b_rec = chain_recovery(b_ded, b_ff, b_lc)

    # ---- Ruling (verdict never softened; stop at first failure) ----
    gates_ordered = [("R1", r1_pass), ("R2", r2_pass), ("R3", r3_pass), ("R4", r4_pass)]
    first_failing = None
    for name, ok in gates_ordered:
        if not ok:
            first_failing = name
            break
    if first_failing is None and twin_pass:
        ruling = "APPROVE"
    else:
        ruling = "REJECT"
        if not twin_pass and first_failing is None:
            first_failing = "TWIN_EVALUATOR_DISAGREEMENT"

    # ---- Self-checks (>=12) ----
    edge_counts = {name: len(edges) for name, edges in STRUCTURES.items()}
    checks = {
        "01_K_eq_12": (K == 12),
        "02_N_REPS_eq_20000": (n_reps == 20000),
        "03_SEED_MAIN_eq_20260717": (SEED_MAIN == 20260717),
        "04_LANE_CAP_eq_1": (LANE_CAP == 1.0),
        "05_CV_BAND_len_3": (len(CV_BAND) == 3),
        "06_feasibility_all_reps_all_structs": feasibility_all,
        "07_dominance_FULLFLEX_ge_LONGCHAIN": dominance_ff_ge_lc,
        "08_dominance_LONGCHAIN_ge_DEDICATED": dominance_lc_ge_ded,
        "09_dominance_BUDDYPAIRS_ge_DEDICATED": dominance_bp_ge_ded,
        "10_edges_LONGCHAIN_eq_BUDDYPAIRS_eq_2K": (edge_counts["LONGCHAIN"] == 2 * K and edge_counts["BUDDYPAIRS"] == 2 * K),
        # 11 (byte-identical double run) and 13 (sha stable) are validated
        # outside this function by main(); we surface true placeholders here.
        "11_double_run_byte_identical": True,
        "12_twin_evaluators_agree_within_1e-9": twin_pass,
        "13_results_sha256_stable_across_double_run": True,
    }
    checks_pass = all(checks.values())

    results = {
        "spec_id": "VERDICT-110/PROPOSAL-097",
        "config": {
            "K": K,
            "N_REPS": n_reps,
            "SEED_MAIN": SEED_MAIN,
            "LANE_CAP": LANE_CAP,
            "MEAN": MEAN,
            "SD_MAIN": SD_MAIN,
            "CV_BAND": [list(t) for t in CV_BAND],
            "SD_BOUNDARY": SD_BOUNDARY,
            "SEED_BOUNDARY": SEED_BOUNDARY,
            "N_BOOT": N_BOOT,
        },
        "edge_counts": edge_counts,
        "structures": {
            name: {
                "mean_served": means_A[name],
                "sem_served": sems_A[name],
                "mean_served_fraction": means_A[name] / K,
            }
            for name in STRUCT_NAMES
        },
        "gates": {
            "R1_chain_recovery": {
                "value": r1_value,
                "threshold": r1_threshold,
                "bootstrap_sem": r1_sem,
                "margin_sigma": r1_margin_sigma,
                "pass": r1_pass,
                "N_BOOT": N_BOOT,
            },
            "R2_full_minus_dedicated": {
                "value": r2_value,
                "threshold": r2_threshold,
                "sem": r2_sem,
                "margin_sigma": r2_margin_sigma,
                "pass": r2_pass,
                "note": "paired-difference SEM in served-fraction",
            },
            "R3_longchain_minus_buddypairs": {
                "value": r3_value,
                "threshold": r3_threshold,
                "sem": r3_sem,
                "margin_sigma": r3_margin_sigma,
                "pass": r3_pass,
                "note": "paired-difference SEM in served-fraction; identical 2K-edge budget",
            },
            "R4_cv_band_min_recovery": {
                "value": r4_min,
                "threshold": r4_threshold,
                "bootstrap_sem_at_min": r4_sem,
                "margin_sigma": r4_margin_sigma,
                "pass": r4_pass,
                "min_at_sd": band_details[r4_min_idx]["sd"],
                "min_at_seed": band_details[r4_min_idx]["seed"],
            },
        },
        "cv_band": band_details,
        "cross_check_sd_050": {
            "sd": SD_BOUNDARY,
            "seed": SEED_BOUNDARY,
            "mean_dedicated": b_ded,
            "mean_fullflex": b_ff,
            "mean_longchain": b_lc,
            "chain_recovery": b_rec,
            "note": "non-gating boundary disclosure",
        },
        "twin_evaluators": {
            "A_impl": "Edmonds-Karp (BFS)",
            "B_impl": "Ford-Fulkerson (DFS)",
            "A_means": means_A,
            "B_means": main_B_means,
            "max_abs_delta": twin_relerr,
            "agree_within_1e-9": twin_pass,
        },
        "ruling": ruling,
        "first_failing_gate": first_failing,
        "self_checks": checks,
        "self_checks_passed": sum(1 for v in checks.values() if v),
    }
    return results, main_served


# ---------------------------------------------------------------------------
# Table printer
# ---------------------------------------------------------------------------
def print_table(results):
    print()
    print("=" * 76)
    print("VERDICT 110 · long chain · P097 (+13) · independent stdlib reverification")
    print("=" * 76)
    structs = results["structures"]
    print(f"K={results['config']['K']}  N_REPS={results['config']['N_REPS']}  "
          f"SEED_MAIN={results['config']['SEED_MAIN']}  SD_MAIN={results['config']['SD_MAIN']}")
    print()
    print(f"{'Structure':<12} {'mean_served':>13} {'sem':>10} {'served_frac':>13}  edges")
    print("-" * 76)
    for name in STRUCT_NAMES:
        s = structs[name]
        ec = results["edge_counts"][name]
        print(f"{name:<12} {s['mean_served']:>13.6f} {s['sem_served']:>10.6f} "
              f"{s['mean_served_fraction']:>13.6f}  {ec}")
    print()
    r1 = results["gates"]["R1_chain_recovery"]
    r2 = results["gates"]["R2_full_minus_dedicated"]
    r3 = results["gates"]["R3_longchain_minus_buddypairs"]
    r4 = results["gates"]["R4_cv_band_min_recovery"]
    print(f"R1 chain_recovery = {r1['value']:.6f}  (>= {r1['threshold']}) "
          f"[bootstrap SEM {r1['bootstrap_sem']:.6f}, {r1['margin_sigma']:+.2f}σ] "
          f"-> {'PASS' if r1['pass'] else 'FAIL'}")
    print(f"R2 fullflex-dedicated served-frac gap = {r2['value']:.6f}  (>= {r2['threshold']}) "
          f"[SEM {r2['sem']:.6f}, {r2['margin_sigma']:+.2f}σ] "
          f"-> {'PASS' if r2['pass'] else 'FAIL'}")
    print(f"R3 longchain-buddypairs served-frac gap = {r3['value']:.6f}  (>= {r3['threshold']}) "
          f"[SEM {r3['sem']:.6f}, {r3['margin_sigma']:+.2f}σ] "
          f"-> {'PASS' if r3['pass'] else 'FAIL'}")
    print(f"R4 CV-band min recovery = {r4['value']:.6f} at sd={r4['min_at_sd']} "
          f"(>= {r4['threshold']}) [bootstrap SEM {r4['bootstrap_sem_at_min']:.6f}, "
          f"{r4['margin_sigma']:+.2f}σ] -> {'PASS' if r4['pass'] else 'FAIL'}")
    print("  CV band details:")
    for bd in results["cv_band"]:
        print(f"    sd={bd['sd']:.2f} seed={bd['seed']}: "
              f"chain_recovery={bd['chain_recovery']:.6f} "
              f"(boot SEM {bd['chain_recovery_bootstrap_sem']:.6f})")
    b = results["cross_check_sd_050"]
    print(f"cross-check sd={b['sd']:.2f} seed={b['seed']}: "
          f"chain_recovery={b['chain_recovery']:.6f} (non-gating boundary disclosure)")
    tw = results["twin_evaluators"]
    print(f"twin evaluators: A={tw['A_impl']}, B={tw['B_impl']}, "
          f"max|Δ|={tw['max_abs_delta']:.3e}, agree_within_1e-9={tw['agree_within_1e-9']}")
    print(f"self-checks passed: {results['self_checks_passed']}/{len(results['self_checks'])}")
    print("-" * 76)
    if results["ruling"] == "APPROVE":
        print("RULING: APPROVE (no failing gate)")
    else:
        print(f"RULING: REJECT — first-failing gate: {results['first_failing_gate']}")
    print("=" * 76)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == "smoke"
    n_reps = 500 if smoke else N_REPS
    print(f"[verdict-110] running {'SMOKE' if smoke else 'FULL'} pass (N_REPS={n_reps})")

    # Byte-identical double run of the whole pipeline. Both runs use the SAME
    # in-file seeds (SEED_MAIN, CV_BAND seeds, SEED_BOUNDARY), so if the code
    # is deterministic they MUST produce byte-identical canonical JSON.
    results_1, _ = full_pipeline(n_reps, do_twin=True)
    canon_1 = canonical({k: v for k, v in results_1.items() if k != "determinism"})
    sha_1 = sha256_hex(canon_1)

    if not smoke:
        results_2, _ = full_pipeline(n_reps, do_twin=True)
        canon_2 = canonical({k: v for k, v in results_2.items() if k != "determinism"})
        sha_2 = sha256_hex(canon_2)
        if canon_1 != canon_2:
            raise SystemExit(
                "byte-identical double run FAILED: canonical JSON differs between runs"
            )
        if sha_1 != sha_2:
            raise SystemExit(
                f"determinism sha256 mismatch: {sha_1} vs {sha_2}"
            )

    results_1["determinism"] = {
        "double_run_byte_identical": True if not smoke else "SKIPPED-in-smoke-mode",
        "results_sha256": sha_1,
    }

    print_table(results_1)

    if smoke:
        print("[smoke] not writing results.json / fixtures.json")
        # For a smoke run we still gate exit 0 on the non-N-dependent self-checks
        # (dominance + feasibility + edge counts + K).  R gates may fail at
        # very low N — do not gate exit code on them in smoke mode.
        smoke_checks = {k: v for k, v in results_1["self_checks"].items()
                        if k not in ("02_N_REPS_eq_20000",
                                     "11_double_run_byte_identical",
                                     "13_results_sha256_stable_across_double_run")}
        if not all(smoke_checks.values()):
            print("[smoke] non-N self-checks FAILED:", smoke_checks)
            sys.exit(2)
        sys.exit(0)

    # Full run: gate exit 0 on all self-checks
    if not all(results_1["self_checks"].values()):
        print("[verdict-110] self-checks FAILED:", results_1["self_checks"])
        sys.exit(2)
    # And also require >= 12 checks pass explicitly
    if results_1["self_checks_passed"] < 12:
        print(f"[verdict-110] only {results_1['self_checks_passed']} self-checks passed (<12)")
        sys.exit(2)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "results.json"), "w") as f:
        json.dump(results_1, f, indent=2, sort_keys=True)
    with open(os.path.join(here, "fixtures.json"), "w") as f:
        json.dump(build_fixtures(), f, indent=2, sort_keys=True)
    print(f"[verdict-110] wrote {os.path.join(here, 'results.json')} "
          f"and fixtures.json; results.json canonical sha256 = {sha_1}")


if __name__ == "__main__":
    main()
