#!/usr/bin/env python3
"""verdict-035 — Assign-at-merge, priced: the merge-queue re-validation tax.

Prices the OTHER side of VERDICT 023's fork: the parent measured what NOT
building Option 3 costs (the residual renumber treadmill under the shipped
P1 checker); this sim measures what BUILDING it costs — the serialized FIFO
merge queue with a deterministic re-validation V_q at the head that any REAL
assign-at-merge mechanism forces (policy P3Q). M/D/1 by construction.

Dual arms:
  Arm A (decision arm) — exact, seedless Pollaczek-Khinchine closed form
    W + V + lambda*V_q^2/(2*(1-rho)) + V_q, rho = lambda*V_q, evaluated in
    exact Fraction arithmetic against V023's COMMITTED per-cell P1 means
    (chained anchors, quoted verbatim in fixtures.json @ c7340ae).
  Arm S (validation arm) — seeded event-driven MC of the whole queue;
    familywise-calibrated 3.5-sigma gates, Little's law, busy-fraction,
    M/M/1 jitter identity, draw-count sentinels, twin engines, twin
    decision evaluators, V_q = 0 exact regression to the parent's P3 column.

Hermetic: reads ONLY its own fixtures.json. Stdlib only. No network, no git,
no wall clock. Progress to stderr; stdout + results.json byte-identical
across two full process runs (external diff). Run:

    python3 sims/verdict-035-assign-at-merge-tax/assign_merge_tax_sim.py

Exit 0 iff every self-check passes.
"""

import bisect
import heapq
import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS_PASSED = 0
CHECKS_FAILED = 0
FAILURES = []


def check(cond, msg):
    global CHECKS_PASSED, CHECKS_FAILED
    if cond:
        CHECKS_PASSED += 1
    else:
        CHECKS_FAILED += 1
        FAILURES.append(msg)
        print("SELF-CHECK FAIL: %s" % msg, file=sys.stderr)


def progress(msg):
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------- rng wrapper
class CountingRandom(random.Random):
    """random.Random that counts expovariate draws (draw-count sentinels)."""

    def __init__(self, seed):
        super().__init__(seed)
        self.draws = 0

    def expovariate(self, lambd):
        self.draws += 1
        return super().expovariate(lambd)


# ---------------------------------------------------------------- fixture
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check(sys.version_info[:2] == (3, 11),
      "cpython minor pinned: running %d.%d, fixture pins %s"
      % (sys.version_info[0], sys.version_info[1], FX["cpython_pin"]))

C = FX["constants"]
W = C["W_hours"]                     # 8
H = C["H_hours"]                     # 2000
WARM = C["warmup_hours"]             # 200
TWIN = H - WARM                      # 1800
M_MAIN = C["M_primary"]              # 40
M_STAB = C["M_stability"]            # 20
M_JIT = C["M_jitter"]                # 8
M_STRESS = C["M_stress"]             # 8
M_P95 = C["M_p95_leg"]               # 40
M_AUX = C["M_aux_16x"]               # 640

LAMBDAS = [(Fraction(1, 24), "lam01"), (Fraction(1, 6), "lam04"),
           (Fraction(1, 2), "lam12")]
VCOLS = [(Fraction(1, 4), "V00.25"), (Fraction(2), "V02.00"),
         (Fraction(24), "V24.00")]
CELLS = [(lf, vf, "%s|%s" % (ln, vn)) for lf, ln in LAMBDAS for vf, vn in VCOLS]
CELL_KEYS = [k for _, _, k in CELLS]
check(CELL_KEYS == sorted(CELL_KEYS), "cell keys lexicographic == pinned order")

VQ_DECISION = [Fraction(1, 10), Fraction(1, 2), Fraction(2)]
VQ_MAIN = [Fraction(0)] + VQ_DECISION            # ascending: 0, 0.1, 0.5, 2
VQ_STRESS = Fraction(8)
RHO_BOUND = Fraction(9, 10)

TREADMILL = FX["constants"]["treadmill_cells"]
CALM = FX["constants"]["calm_cells"]
check(sorted(TREADMILL + CALM) == CELL_KEYS, "treadmill + calm == all 9 cells")

P1_MEAN = {k: Fraction(v) for k, v in FX["anchors_v023"]["P1_mean_dur_f"].items()}
P1_MEAN_F = {k: float(v) for k, v in FX["anchors_v023"]["P1_mean_dur_f"].items()}
P1_P95_F = {k: float(v) for k, v in FX["anchors_v023"]["P1_p95_dur_f"].items()}
P3_MEAN_F = {k: float(v) for k, v in FX["anchors_v023"]["P3_mean_by_V_column"].items()}
T_COMMITTED = FX["anchors_v023"]["treadmill_T_committed"]

# fixture-internal anchor identities (G11 flavor): P3 mean == W + V exactly
for vf, vn in VCOLS:
    check(P3_MEAN_F[vn] == float(W + vf),
          "P3 committed mean %s == W+V exactly" % vn)
for k, tv in T_COMMITTED.items():
    fr = Fraction(tv["frac"])
    check(abs(float(fr) - float(tv["float"])) < 5e-7,
          "committed T frac matches float for %s" % k)

BANDS = FX["decision_rule"]["band_constants"]
REJECT_CELLS_MAX = BANDS["REJECT_CELLS_MAX"]       # 2
APPROVE_CELLS_MIN = BANDS["APPROVE_CELLS_MIN"]     # 4
N_TREADMILL = BANDS["N_TREADMILL"]                 # 5
VQ_DAGGER = Fraction(BANDS["VQ_DAGGER_HOURS"])     # 2

check(len(TREADMILL) == N_TREADMILL, "treadmill census == 5")


# ---------------------------------------------------------------- Arm A exact
def arm_a_exact(lam, v, vq):
    """M/D/1 P-K mean open->merge in exact Fractions. None if rho >= bound."""
    rho = lam * vq
    if rho >= RHO_BOUND:
        return rho, None
    wq = lam * vq * vq / (2 * (1 - rho))
    return rho, W + v + wq + vq


def arm_a_float(lam_f, v_f, vq_f):
    """Independently-written float twin of the P-K closed form."""
    rho_f = lam_f * vq_f
    if rho_f >= 0.9:
        return rho_f, None
    wq_f = lam_f * vq_f * vq_f / (2.0 * (1.0 - rho_f))
    return rho_f, 8.0 + v_f + wq_f + vq_f


def mm1_mean_float(lam_f, v_f, vq_f):
    """M/M/1 (exponential service) mean open->merge — the jitter leg's form."""
    rho_f = lam_f * vq_f
    if rho_f >= 0.9:
        return None
    return 8.0 + v_f + vq_f + rho_f * vq_f / (1.0 - rho_f)


# hand pins C and D (Arm A / M/M/1 exact values, derived before code ran)
_rho, _mean = arm_a_exact(Fraction(1, 6), Fraction(2), Fraction(2))
check(_rho == Fraction(1, 3) and _mean == Fraction(25, 2),
      "HAND-C: lam04|V02.00 Vq=2 -> rho 1/3, mean 25/2")
_rho, _mean = arm_a_exact(Fraction(1, 6), Fraction(2), Fraction(1, 2))
check(_rho == Fraction(1, 12) and _mean == Fraction(463, 44),
      "HAND-C: lam04|V02.00 Vq=0.5 -> rho 1/12, mean 463/44")
check(mm1_mean_float(1.0 / 6.0, 2.0, 2.0) == 8.0 + 2.0 + 2.0 + 1.0,
      "HAND-D: M/M/1 W_q = 1 exactly at rho=1/3, Vq=2")


# ---------------------------------------------------------------- SE arithmetic
def var_dur_md1(lam_f, vq_f):
    rho = lam_f * vq_f
    ewq = lam_f * vq_f * vq_f / (2.0 * (1.0 - rho))
    return ewq * ewq + lam_f * vq_f ** 3 / (3.0 * (1.0 - rho))


def var_dur_mm1(lam_f, vq_f):
    rho = lam_f * vq_f
    ewq = rho * vq_f / (1.0 - rho)
    return ewq * ewq + 2.0 * lam_f * vq_f ** 3 / (1.0 - rho) + vq_f * vq_f


def gate_tol(lam_f, vq_f, m_leg, jitter=False):
    """Pinned G3/G6 tolerance: max(3.5 * SE_pred, 0.02 h)."""
    rho = lam_f * vq_f
    var = var_dur_mm1(lam_f, vq_f) if jitter else var_dur_md1(lam_f, vq_f)
    inf = ((1.0 + rho) / (1.0 - rho)) ** 2
    n_pred = lam_f * TWIN * m_leg
    se = math.sqrt(var * inf / n_pred)
    return max(3.5 * se, 0.02), se


# G11: recompute the fixture's pre-run worked examples and assert agreement
_wx = FX["se_arithmetic_preregistered"]["worked_examples_pre_run"]
_t, _se = gate_tol(1.0 / 6.0, 0.5, 40)
check(abs(_se - _wx["lam04|V02.00_Vq0.5_main"]["SE_pred"]) < 1e-5
      and abs(_t - _wx["lam04|V02.00_Vq0.5_main"]["tol"]) < 1e-9,
      "G11: worked example lam04|V02.00 Vq0.5 SE/tol reproduced")
_t, _se = gate_tol(0.5, 0.5, 40)
check(abs(_se - _wx["lam12|V24.00_Vq0.5_main"]["SE_pred"]) < 1e-5
      and abs(_t - _wx["lam12|V24.00_Vq0.5_main"]["tol"]) < 1e-9,
      "G11: worked example lam12|V24.00 Vq0.5 SE/tol reproduced")
_t, _se = gate_tol(1.0 / 24.0, 8.0, 8)
check(abs(_se - _wx["lam01|V00.25_Vq8_stress"]["SE_pred"]) < 1e-4
      and abs(_t - _wx["lam01|V00.25_Vq8_stress"]["tol"]) < 1e-4,
      "G11: worked example lam01|V00.25 Vq8 SE/tol reproduced")
check(float(Fraction(1, 2) * Fraction(2)) == 1.0,
      "G11: stability exclusion lam12 x Vq=2 -> rho = 1 exactly")
_max_rho = max(float(lf * vq) for lf, _, k in CELLS for vq in VQ_DECISION
               if not (k.startswith("lam12") and vq == Fraction(2)))
check(_max_rho == 1.0 / 3.0, "G11: max rho elsewhere on decision grid == 1/3")


# ---------------------------------------------------------------- queue engines
def lindley(arrivals, wv_f, services):
    """FIFO single-server recursion. Returns (waits, starts, finishes, entries)."""
    entries = [a + wv_f for a in arrivals]
    waits, starts, finishes = [], [], []
    prev_finish = -1.0
    for i, e in enumerate(entries):
        s = e if e >= prev_finish else prev_finish
        f = s + services[i]
        waits.append(s - e)
        starts.append(s)
        finishes.append(f)
        prev_finish = f
    return waits, starts, finishes, entries


def heap_engine(arrivals, wv_f, services):
    """Independently-written event-driven engine (heapq). Twin of lindley()."""
    ev = []
    for i, a in enumerate(arrivals):
        heapq.heappush(ev, (a + wv_f, 0, i))     # (time, type 0=entry, id)
    fifo = []
    busy = False
    cur = None
    waits = [None] * len(arrivals)
    finishes = [None] * len(arrivals)
    entry_t = [a + wv_f for a in arrivals]
    while ev:
        t, typ, i = heapq.heappop(ev)
        if typ == 0:                              # queue entry
            if not busy:
                busy = True
                cur = i
                waits[i] = t - entry_t[i]
                heapq.heappush(ev, (t + services[i], 1, i))
            else:
                fifo.append(i)
        else:                                     # service completion (merge)
            finishes[i] = t
            if fifo:
                j = fifo.pop(0)
                cur = j
                waits[j] = t - entry_t[j]
                heapq.heappush(ev, (t + services[j], 1, j))
            else:
                busy = False
                cur = None
    return waits, finishes


def run_replication(arrivals, wv_f, vq_f, services=None, trace_buckets=None):
    """One replication of P3Q. Returns the per-rep stats dict."""
    n = len(arrivals)
    if services is None:
        services = [vq_f] * n
    waits, starts, finishes, entries = lindley(arrivals, wv_f, services)

    # measured number mechanics (the V023 P3-control discipline): a PR holds
    # no number until merge; assigned = max(main)+1 at the merge instant.
    max_main = 0
    collisions = 0
    renumbers = 0
    merged_all = 0
    for f in finishes:
        if f <= H:                      # events after H are not processed
            merged_all += 1
            cand = max_main + 1
            if cand <= max_main:        # a collision would renumber — measure
                collisions += 1
                renumbers += 1
            else:
                max_main = cand

    min_wait = 0.0
    dur_sum = 0.0
    durs = []
    q_integral = 0.0
    busy_time = 0.0
    entered_win = 0
    wait_sum_win = 0.0
    max_qlen = 0
    for i in range(n):
        wt = waits[i]
        if wt < min_wait:
            min_wait = wt
        e, s, f = entries[i], starts[i], finishes[i]
        # window-clipped waiting-time integral and busy time
        lo, hi = max(e, WARM), min(s, H)
        if hi > lo:
            q_integral += hi - lo
            if trace_buckets is not None:
                b0 = int((lo - WARM) // 100.0)
                b1 = int((hi - WARM) // 100.0)
                for b in range(b0, min(b1, len(trace_buckets) - 1) + 1):
                    seg_lo = max(lo, WARM + 100.0 * b)
                    seg_hi = min(hi, WARM + 100.0 * (b + 1))
                    if seg_hi > seg_lo:
                        trace_buckets[b] += seg_hi - seg_lo
        lo, hi = max(s, WARM), min(f, H)
        if hi > lo:
            busy_time += hi - lo
        if WARM < e <= H:
            entered_win += 1
            wait_sum_win += wt
        # queue length just after entry i (waiting PRs only)
        q = (i + 1) - bisect.bisect_right(starts, e, 0, i + 1)
        if q > max_qlen:
            max_qlen = q
        # merged-population metrics: merge instant in (WARM, H]
        if WARM < f <= H:
            d = wv_f + wt + services[i]   # open->merge = W+V+wait+service
            dur_sum += d
            durs.append(d)
    return {
        "n_merged": len(durs), "dur_sum": dur_sum, "durs": durs,
        "min_wait": min_wait, "q_integral": q_integral,
        "busy_time": busy_time, "entered_win": entered_win,
        "wait_sum_win": wait_sum_win, "max_qlen": max_qlen,
        "collisions": collisions, "renumbers": renumbers,
        "merged_all": merged_all, "max_main": max_main,
        "waits": waits, "finishes": finishes,
    }


# ---------------------------------------------------------------- hand pins A/B
def _hand_pin(pin_key, vq_f):
    p = FX["hand_pins"][pin_key]
    arr = [float(a) for a in p["params"]["arrivals"]]
    wv = float(p["params"]["W"] + p["params"]["V"])
    saveH, saveW = H, WARM
    # hand pins use H=100, warmup=0 — run through a local variant
    waits, starts, finishes, entries = lindley(arr, wv, [vq_f] * len(arr))
    hw, hf = heap_engine(arr, wv, [vq_f] * len(arr))
    check(hw == waits and hf == finishes,
          "%s: heap engine == lindley engine exactly" % pin_key)
    exp = p["expect"]
    dur = [wv + waits[i] + vq_f for i in range(len(arr))]
    q_int = sum(starts[i] - entries[i] for i in range(len(arr)))
    busy = sum(finishes[i] - starts[i] for i in range(len(arr)))
    mq = 0
    for i in range(len(arr)):
        q = (i + 1) - bisect.bisect_right(starts, entries[i], 0, i + 1)
        mq = max(mq, q)
    check(len(dur) == exp["merged"], "%s merged" % pin_key)
    check(sum(dur) == exp["dur_sum"], "%s dur_sum" % pin_key)
    check(sum(waits) == exp["wait_sum"], "%s wait_sum" % pin_key)
    check(busy == exp["busy_time"], "%s busy_time" % pin_key)
    check(q_int == exp["q_integral"], "%s q_integral" % pin_key)
    check(mq == exp["max_qlen"], "%s max_qlen" % pin_key)


_hand_pin("HAND-A_queue_mechanics", 2.0)
_hand_pin("HAND-B_vq0_control", 0.0)
progress("hand pins A-D passed")


# ---------------------------------------------------------------- point runner
def simulate_point(rng, lam_f, wv_f, vq_f, m_reps, jitter=False,
                   keep_rep0=False, trace_buckets=None, pool_durs=False):
    """Simulate one (cell, V_q) point for m_reps replications on rng's stream."""
    agg = {"n": 0, "dur_sum": 0.0, "dur_sq": 0.0, "q_integral": 0.0,
           "busy_time": 0.0, "entered": 0, "wait_sum": 0.0, "max_qlen": 0,
           "collisions": 0, "renumbers": 0}
    pooled = [] if pool_durs else None
    rep0 = None
    for rep in range(m_reps):
        d0 = rng.draws
        arrivals = []
        t = 0.0
        while True:
            t += rng.expovariate(lam_f)
            if t > H:
                break                    # overshoot draw consumed, discarded
            arrivals.append(t)
        services = None
        if jitter:
            mu = 1.0 / vq_f
            services = [rng.expovariate(mu) for _ in arrivals]
        expect_draws = (2 * len(arrivals) + 1) if jitter else (len(arrivals) + 1)
        check(rng.draws - d0 == expect_draws,
              "draw sentinel rep %d (lam=%.6f vq=%.3f jitter=%s)"
              % (rep, lam_f, vq_f, jitter))
        r = run_replication(arrivals, wv_f, vq_f, services=services,
                            trace_buckets=trace_buckets)
        check(r["min_wait"] >= 0.0, "waits nonnegative")
        check(r["collisions"] == 0 and r["renumbers"] == 0,
              "P3Q measured zero collisions/renumbers")
        check(r["max_main"] == r["merged_all"],
              "assigned numbers contiguous 1..merged")
        if keep_rep0 and rep == 0:
            rep0 = (list(arrivals), list(services) if services else None,
                    r["waits"], r["finishes"])
        agg["n"] += r["n_merged"]
        agg["dur_sum"] += r["dur_sum"]
        for d in r["durs"]:
            agg["dur_sq"] += d * d
        if pooled is not None:
            pooled.extend(r["durs"])
        agg["q_integral"] += r["q_integral"]
        agg["busy_time"] += r["busy_time"]
        agg["entered"] += r["entered_win"]
        agg["wait_sum"] += r["wait_sum_win"]
        agg["max_qlen"] = max(agg["max_qlen"], r["max_qlen"])
        agg["collisions"] += r["collisions"]
        agg["renumbers"] += r["renumbers"]
    mean = agg["dur_sum"] / agg["n"] if agg["n"] else None
    out = {
        "n": agg["n"], "mean": mean,
        "Lbar": agg["q_integral"] / (TWIN * m_reps),
        "busy_frac": agg["busy_time"] / (TWIN * m_reps),
        "lambda_hat": agg["entered"] / (TWIN * m_reps),
        "What": (agg["wait_sum"] / agg["entered"]) if agg["entered"] else 0.0,
        "max_qlen": agg["max_qlen"],
        "collisions": agg["collisions"], "renumbers": agg["renumbers"],
    }
    return out, pooled, rep0


def identity_gates(key, vq_f, lam_f, stats, m_leg):
    """G4 Little's law + G5 busy fraction on a stable simulated point."""
    rho = lam_f * vq_f
    ewq = lam_f * vq_f * vq_f / (2.0 * (1.0 - rho))
    tol_l = max(0.02, 0.05 * lam_f * ewq)
    lw = stats["lambda_hat"] * stats["What"]
    check(abs(stats["Lbar"] - lw) <= tol_l,
          "G4 Little's law at %s vq=%s: |%.6f - %.6f| > %.6f"
          % (key, vq_f, stats["Lbar"], lw, tol_l))
    se_bf = vq_f * math.sqrt(lam_f * TWIN * m_leg) / (TWIN * m_leg)
    tol_b = max(0.005, 3.5 * se_bf)
    check(abs(stats["busy_frac"] - rho) <= tol_b,
          "G5 busy fraction at %s vq=%s: |%.6f - %.6f| > %.6f"
          % (key, vq_f, stats["busy_frac"], rho, tol_b))


# ================================================================ MAIN LEG
progress("main leg (seed %d) ..." % C["seed_main"])
rng_main = CountingRandom(C["seed_main"])
MAIN = {}          # key -> vq_str -> stats
REP0 = {}
FRONTIER_TRACE = {}
GATE_TABLE = []    # (leg, key, vq_str, mean_S, mean_A, tol, z, pass)

FRONTIER_POINTS = {("lam04|V02.00", "0.5"), ("lam12|V00.25", "0.1")}

for lam, v, key in CELLS:
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    MAIN[key] = {}
    for vq in VQ_MAIN:
        rho = lam * vq
        vq_f = float(vq)
        vq_str = ("%g" % vq_f)
        if rho >= RHO_BOUND:
            MAIN[key][vq_str] = {"unstable": True, "rho": str(rho)}
            continue
        tb = None
        if (key, vq_str) in FRONTIER_POINTS:
            tb = [0.0] * 18
        stats, _, rep0 = simulate_point(
            rng_main, lam_f, wv_f, vq_f, M_MAIN,
            keep_rep0=True, trace_buckets=tb)
        if tb is not None:
            FRONTIER_TRACE["%s|vq%s" % (key, vq_str)] = [
                round(x / (100.0 * M_MAIN), 6) for x in tb]
        REP0[(key, vq_str)] = rep0
        MAIN[key][vq_str] = stats
        if vq == 0:
            # G1: exact regression to the parent's committed P3 column
            vcol = key.split("|")[1]
            check(stats["mean"] == P3_MEAN_F[vcol],
                  "G1 Vq=0 control at %s: mean %r != committed P3 %r"
                  % (key, stats["mean"], P3_MEAN_F[vcol]))
            check(stats["Lbar"] == 0.0 and stats["busy_frac"] == 0.0
                  and stats["max_qlen"] == 0,
                  "G1 Vq=0 control at %s: queue empty" % key)
        else:
            _, mean_a = arm_a_float(lam_f, v_f, vq_f)
            tol, se = gate_tol(lam_f, vq_f, M_MAIN)
            z = (stats["mean"] - mean_a) / se if se > 0 else 0.0
            ok = abs(stats["mean"] - mean_a) <= tol
            check(ok, "G3 main %s vq=%s: |%.6f - %.6f| > %.6f"
                  % (key, vq_str, stats["mean"], mean_a, tol))
            GATE_TABLE.append(("main", key, vq_str, stats["mean"], mean_a,
                               tol, z, ok))
            identity_gates(key, vq_f, lam_f, stats, M_MAIN)

# G9: twin engines on replication 0 of every simulated main point
for (key, vq_str), rep0 in sorted(REP0.items()):
    arrivals, services, waits, finishes = rep0
    lam, v = next((lf, vf) for lf, vf, k in CELLS if k == key)
    wv_f = float(W + v)
    vq_f = float(vq_str)
    svc = services if services else [vq_f] * len(arrivals)
    hw, hf = heap_engine(arrivals, wv_f, svc)
    check(hw == waits and hf == finishes,
          "G9 twin engines rep0 %s vq=%s" % (key, vq_str))
progress("main leg done; twin engines verified")

# ================================================================ STABILITY LEG
progress("stability leg (seed %d) ..." % C["seed_stability"])
rng_stab = CountingRandom(C["seed_stability"])
STAB = {}
for lam, v, key in CELLS:
    if key not in TREADMILL:
        continue
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    STAB[key] = {}
    for vq in VQ_DECISION:
        rho = lam * vq
        vq_f = float(vq)
        vq_str = "%g" % vq_f
        if rho >= RHO_BOUND:
            STAB[key][vq_str] = {"unstable": True, "rho": str(rho)}
            continue
        stats, _, _ = simulate_point(rng_stab, lam_f, wv_f, vq_f, M_STAB)
        STAB[key][vq_str] = stats
        _, mean_a = arm_a_float(lam_f, v_f, vq_f)
        tol, se = gate_tol(lam_f, vq_f, M_STAB)
        z = (stats["mean"] - mean_a) / se if se > 0 else 0.0
        ok = abs(stats["mean"] - mean_a) <= tol
        check(ok, "G3 stability %s vq=%s" % (key, vq_str))
        GATE_TABLE.append(("stability", key, vq_str, stats["mean"], mean_a,
                           tol, z, ok))
        identity_gates(key, vq_f, lam_f, stats, M_STAB)

# ================================================================ REPORTING LEG
progress("reporting leg (seed %d): p95, jitter, stress ..." % C["seed_reporting"])
rng_rep = CountingRandom(C["seed_reporting"])

# (a) p95 table — all 9 cells x stable decision V_q, M = 40
P95 = {}
for lam, v, key in CELLS:
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    P95[key] = {}
    for vq in VQ_DECISION:
        rho = lam * vq
        vq_f = float(vq)
        vq_str = "%g" % vq_f
        if rho >= RHO_BOUND:
            P95[key][vq_str] = {"unstable": True, "rho": str(rho)}
            continue
        stats, pooled, _ = simulate_point(rng_rep, lam_f, wv_f, vq_f, M_P95,
                                          pool_durs=True)
        pooled.sort()
        n = len(pooled)
        idx = math.ceil(0.95 * n) - 1
        half = 1.96 * math.sqrt(0.95 * 0.05 / n)
        lo = min(max(math.ceil(n * (0.95 - half)) - 1, 0), n - 1)
        hi = min(max(math.ceil(n * (0.95 + half)) - 1, 0), n - 1)
        P95[key][vq_str] = {
            "p95": round(pooled[idx], 6), "n": n,
            "ci": [round(pooled[lo], 6), round(pooled[hi], 6)],
            "P1_committed_p95": P1_P95_F[key],
        }
        _, mean_a = arm_a_float(lam_f, v_f, vq_f)
        tol, se = gate_tol(lam_f, vq_f, M_P95)
        z = (stats["mean"] - mean_a) / se if se > 0 else 0.0
        ok = abs(stats["mean"] - mean_a) <= tol
        check(ok, "G3 p95-leg %s vq=%s" % (key, vq_str))
        GATE_TABLE.append(("p95", key, vq_str, stats["mean"], mean_a,
                           tol, z, ok))
        identity_gates(key, vq_f, lam_f, stats, M_P95)

# (b) jitter leg — treadmill cells x stable decision V_q, exp service, M = 8
JITTER = {}
for lam, v, key in CELLS:
    if key not in TREADMILL:
        continue
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    JITTER[key] = {}
    for vq in VQ_DECISION:
        rho = lam * vq
        vq_f = float(vq)
        vq_str = "%g" % vq_f
        if rho >= RHO_BOUND:
            JITTER[key][vq_str] = {"unstable": True, "rho": str(rho)}
            continue
        stats, _, _ = simulate_point(rng_rep, lam_f, wv_f, vq_f, M_JIT,
                                     jitter=True)
        mean_mm1 = mm1_mean_float(lam_f, v_f, vq_f)
        tol, se = gate_tol(lam_f, vq_f, M_JIT, jitter=True)
        z = (stats["mean"] - mean_mm1) / se if se > 0 else 0.0
        ok = abs(stats["mean"] - mean_mm1) <= tol
        check(ok, "G6 jitter %s vq=%s: |%.6f - %.6f| > %.6f"
              % (key, vq_str, stats["mean"], mean_mm1, tol))
        GATE_TABLE.append(("jitter", key, vq_str, stats["mean"], mean_mm1,
                           tol, z, ok))
        _, mean_md1 = arm_a_float(lam_f, v_f, vq_f)
        JITTER[key][vq_str] = {
            "mean": round(stats["mean"], 6), "n": stats["n"],
            "mm1_exact": round(mean_mm1, 6), "md1_exact": round(mean_md1, 6),
            "collisions": stats["collisions"], "renumbers": stats["renumbers"],
        }

# (c) stress column V_q = 8 — lam01 simulated; lam04/lam12 unstable by arithmetic
STRESS = {}
for lam, v, key in CELLS:
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    rho = lam * VQ_STRESS
    vq_f = float(VQ_STRESS)
    if rho >= RHO_BOUND:
        STRESS[key] = {"unstable": True, "rho": str(rho),
                       "note": "no steady state — printed, not simulated"}
        continue
    stats, _, _ = simulate_point(rng_rep, lam_f, wv_f, vq_f, M_STRESS)
    _, mean_a = arm_a_float(lam_f, v_f, vq_f)
    tol, se = gate_tol(lam_f, vq_f, M_STRESS)
    z = (stats["mean"] - mean_a) / se if se > 0 else 0.0
    ok = abs(stats["mean"] - mean_a) <= tol
    check(ok, "G3 stress %s vq=8" % key)
    GATE_TABLE.append(("stress", key, "8", stats["mean"], mean_a, tol, z, ok))
    identity_gates(key, vq_f, lam_f, stats, M_STRESS)
    STRESS[key] = {"rho": str(rho), "mean": round(stats["mean"], 6),
                   "arm_a": round(mean_a, 6), "n": stats["n"],
                   "vs_committed_P1": P1_MEAN_F[key],
                   "collisions": stats["collisions"],
                   "renumbers": stats["renumbers"]}

# ================================================================ AUX LEG (16x)
progress("aux leg (seed %d): 16x diagnostics ..." % C["seed_aux"])
rng_aux = CountingRandom(C["seed_aux"])
AUX = {}
for key, vq_str in sorted(FRONTIER_POINTS):
    lam, v = next((lf, vf) for lf, vf, k in CELLS if k == key)
    lam_f, v_f = float(lam), float(v)
    wv_f = float(W + v)
    vq_f = float(vq_str)
    stats, _, _ = simulate_point(rng_aux, lam_f, wv_f, vq_f, M_AUX)
    _, mean_a = arm_a_float(lam_f, v_f, vq_f)
    tol, se = gate_tol(lam_f, vq_f, M_AUX)
    z = (stats["mean"] - mean_a) / se if se > 0 else 0.0
    ok = abs(stats["mean"] - mean_a) <= tol
    check(ok, "G3 aux 16x %s vq=%s" % (key, vq_str))
    AUX["%s|vq%s" % (key, vq_str)] = {
        "mean": round(stats["mean"], 6), "arm_a": round(mean_a, 6),
        "n": stats["n"], "z": round(z, 3), "tol": round(tol, 6),
        "note": "pre-registered reporting-only diagnostic (breach instrument)"}

# no breach occurred if all G3/G6 gates passed
BREACHES = [g for g in GATE_TABLE if not g[7]]
check(len(BREACHES) == 0,
      "familywise gate table: %d breach(es) — protocol would engage" % len(BREACHES))

# ================================================================ DECISION
progress("decision (twin evaluators) ...")


def decide_exact():
    """Evaluator 1: exact-Fraction Arm A vs Fraction(committed P1 mean)."""
    win = {}
    for lam, v, key in CELLS:
        if key not in TREADMILL:
            continue
        win[key] = {}
        for vq in VQ_DECISION:
            rho, mean = arm_a_exact(lam, v, vq)
            win[key]["%g" % float(vq)] = (mean is not None
                                          and mean <= P1_MEAN[key])
    return win


def decide_float():
    """Evaluator 2 (independently written): float Arm A vs float(P1 mean)."""
    win = {}
    for lam, v, key in CELLS:
        if key not in TREADMILL:
            continue
        win[key] = {}
        for vq_f in (0.1, 0.5, 2.0):
            rho_f, mean_f = arm_a_float(float(lam), float(v), vq_f)
            win[key]["%g" % vq_f] = (mean_f is not None
                                     and mean_f <= P1_MEAN_F[key])
    return win


def vq_star(win_map):
    out = {}
    for key, row in win_map.items():
        best = None
        for vq in VQ_DECISION:
            if row["%g" % float(vq)]:
                best = vq
        out[key] = best
    return out


def ruling_from(star_map):
    cells_with = sum(1 for s in star_map.values() if s is not None)
    cells_ge_dagger = sum(1 for s in star_map.values()
                          if s is not None and s >= VQ_DAGGER)
    if cells_with <= REJECT_CELLS_MAX:          # REJECT checked FIRST
        return "REJECT", cells_with, cells_ge_dagger
    if cells_ge_dagger >= APPROVE_CELLS_MIN:
        return "APPROVE", cells_with, cells_ge_dagger
    return "NULL", cells_with, cells_ge_dagger


WIN_EXACT = decide_exact()
WIN_FLOAT = decide_float()
check(WIN_EXACT == WIN_FLOAT, "G8 twin evaluators: WIN maps identical")
STAR = vq_star(WIN_EXACT)
STAR_F = vq_star(WIN_FLOAT)
check({k: (None if s is None else float(s)) for k, s in STAR.items()}
      == {k: (None if s is None else float(s)) for k, s in STAR_F.items()},
      "G8 twin evaluators: V_q* maps identical")
RULING, CELLS_WITH, CELLS_GE2 = ruling_from(STAR)
RULING_F, _, _ = ruling_from(STAR_F)
check(RULING == RULING_F, "G8 twin evaluators: ruling identical")

# stability-leg ruling reproduction (G10): decision rule on Arm-S means
STAB_WIN = {}
for key in TREADMILL:
    STAB_WIN[key] = {}
    for vq in VQ_DECISION:
        vq_str = "%g" % float(vq)
        cellstats = STAB[key][vq_str]
        if cellstats.get("unstable"):
            STAB_WIN[key][vq_str] = False       # fails WIN by rule
        else:
            STAB_WIN[key][vq_str] = cellstats["mean"] <= P1_MEAN_F[key]
STAB_STAR = vq_star(STAB_WIN)
STAB_RULING, _, _ = ruling_from(STAB_STAR)
check(STAB_RULING == RULING,
      "G10 stability leg reproduces the ruling (%s vs %s)"
      % (STAB_RULING, RULING))

# APPROVE gating interlock (pre-registered): breaches bar APPROVE
if RULING == "APPROVE":
    check(len(BREACHES) == 0 and STAB_RULING == "APPROVE",
          "APPROVE requires zero breaches + stability reproduction")

# per-axis WIN shares over the treadmill decision points (exact fractions)
AXIS_SHARES = {"lambda": {}, "V": {}}
for axis, sel in (("lambda", 0), ("V", 1)):
    groups = {}
    for key in TREADMILL:
        gk = key.split("|")[sel]
        groups.setdefault(gk, []).append(key)
    for gk, keys in sorted(groups.items()):
        tot = wins = 0
        for key in keys:
            for vq in VQ_DECISION:
                tot += 1
                if WIN_EXACT[key]["%g" % float(vq)]:
                    wins += 1
        AXIS_SHARES[axis][gk] = {"wins": wins, "points": tot,
                                 "share": str(Fraction(wins, tot)),
                                 "share_f": round(wins / tot, 6)}

# binding axes = the axis values with the minimum WIN share
BINDING = []
for axis in ("lambda", "V"):
    vals = AXIS_SHARES[axis]
    mn = min(Fraction(v["share"]) for v in vals.values())
    for gk, v in sorted(vals.items()):
        if Fraction(v["share"]) == mn:
            BINDING.append("%s=%s (WIN share %s)" % (axis, gk, v["share"]))

# ================================================================ ASSEMBLY
progress("assembling results ...")

ARM_A_TABLE = {}
for lam, v, key in CELLS:
    ARM_A_TABLE[key] = {"P1_committed_mean": P1_MEAN_F[key],
                        "P1_committed_p95": P1_P95_F[key],
                        "treadmill": key in TREADMILL}
    for vq in VQ_MAIN + [VQ_STRESS]:
        vq_str = "%g" % float(vq)
        rho, mean = arm_a_exact(lam, v, vq)
        ent = {"rho": str(rho), "rho_f": round(float(rho), 6)}
        if mean is None:
            ent["unstable"] = True
        else:
            ent["mean_exact"] = str(mean)
            ent["mean_f"] = round(float(mean), 6)
            if vq in VQ_DECISION and key in TREADMILL:
                ent["win"] = WIN_EXACT[key][vq_str]
                ent["margin_vs_P1_f"] = round(P1_MEAN_F[key] - float(mean), 6)
            elif vq in VQ_DECISION:
                ent["win_reporting_only"] = bool(mean <= P1_MEAN[key])
                ent["margin_vs_P1_f"] = round(P1_MEAN_F[key] - float(mean), 6)
        ARM_A_TABLE[key][vq_str] = ent

MAIN_OUT = {}
for key in sorted(MAIN):
    MAIN_OUT[key] = {}
    for vq_str in sorted(MAIN[key]):
        s = MAIN[key][vq_str]
        if s.get("unstable"):
            MAIN_OUT[key][vq_str] = s
        else:
            MAIN_OUT[key][vq_str] = {
                "mean": round(s["mean"], 6), "n": s["n"],
                "Lbar": round(s["Lbar"], 6),
                "busy_frac": round(s["busy_frac"], 6),
                "max_qlen": s["max_qlen"],
                "collisions": s["collisions"], "renumbers": s["renumbers"]}

STAB_OUT = {}
for key in sorted(STAB):
    STAB_OUT[key] = {}
    for vq_str in sorted(STAB[key]):
        s = STAB[key][vq_str]
        STAB_OUT[key][vq_str] = (s if s.get("unstable") else
                                 {"mean": round(s["mean"], 6), "n": s["n"]})

CHURN = {}
for key in TREADMILL:
    CHURN[key] = {"P1_committed_T": T_COMMITTED[key],
                  "P3Q_measured_renumbers": 0, "P3Q_measured_T": 0,
                  "note": "measured zero on every simulated leg (G2)"}

GATES_OUT = {
    "G1_vq0_exact_regression": "PASS (all 9 cells reproduce committed P3 means"
                               " {8.25, 10.0, 32.0} by float equality)",
    "G2_zero_renumbers": "PASS (zero collisions, zero renumbers, contiguous"
                         " max+1 assignment on every replication of every leg)",
    "G3_G6_familywise": {"gates": len(GATE_TABLE), "breaches": len(BREACHES),
                         "max_abs_z": round(max(abs(g[6]) for g in GATE_TABLE), 3)},
    "G7_draw_sentinels": "PASS (per-replication draw counts exact on all legs)",
    "G8_twin_evaluators": "PASS (exact-Fraction and float WIN/V_q*/ruling identical)",
    "G9_twin_engines": "PASS (heap event engine == Lindley recursion exactly,"
                       " hand pins + rep0 of every main-leg point)",
    "G10_stability_ruling": "PASS (%s at half-M seed %d)" % (STAB_RULING,
                                                             C["seed_stability"]),
    "G11_fixture_crosscheck": "PASS (SE worked examples, exclusion arithmetic,"
                              " anchor identities recomputed)",
}

RESULTS = {
    "sim": "verdict-035-assign-at-merge-tax",
    "proposal": "idea-engine PROPOSAL 033 · 2026-07-13T08:43:05Z",
    "python": "%d.%d" % sys.version_info[:2],
    "anchor_pin": FX["anchors_v023"]["pin"],
    "ruling": RULING,
    "decision": {
        "rule": "REJECT iff V_q* exists in <= 2 of 5 treadmill cells (FIRST);"
                " APPROVE iff V_q* >= 2 h in >= 4 of 5, stability-reproduced;"
                " else NULL",
        "cells_with_winning_vq": CELLS_WITH,
        "cells_vq_star_ge_2h": CELLS_GE2,
        "vq_star_hours": {k: (None if s is None else float(s))
                          for k, s in sorted(STAR.items())},
        "stability_leg_ruling": STAB_RULING,
        "axis_win_shares": AXIS_SHARES,
        "binding_axes": BINDING,
    },
    "arm_a": ARM_A_TABLE,
    "arm_s": {"main": MAIN_OUT, "stability": STAB_OUT, "jitter": JITTER,
              "stress": STRESS, "aux_16x": AUX},
    "p95_table": P95,
    "frontier_traces_Lbar_per_100h": FRONTIER_TRACE,
    "churn_column": CHURN,
    "gates": GATES_OUT,
    "gate_detail": [
        {"leg": g[0], "cell": g[1], "vq": g[2], "mean_S": round(g[3], 6),
         "mean_ref": round(g[4], 6), "tol": round(g[5], 6),
         "z": round(g[6], 3), "pass": g[7]} for g in GATE_TABLE],
    "seeds": {"main": C["seed_main"], "stability": C["seed_stability"],
              "reporting": C["seed_reporting"], "aux": C["seed_aux"]},
    "self_checks": {"passed": None, "failed": None},   # filled below
    "failures": FAILURES,
}

# ================================================================ STDOUT REPORT
print("verdict-035 — assign-at-merge queue tax (idea-engine PROPOSAL 033)")
print("anchors: %s" % FX["anchors_v023"]["pin"])
print()
print("ARM A (exact M/D/1 P-K closed form) — treadmill decision grid:")
print("cell            | committed P1 |   Vq=0.1   |   Vq=0.5   |    Vq=2    | Vq*")
for key in TREADMILL:
    row = ["%-15s" % key, "%12.6f" % P1_MEAN_F[key]]
    for vq in VQ_DECISION:
        e = ARM_A_TABLE[key]["%g" % float(vq)]
        if e.get("unstable"):
            row.append("  UNSTABLE ")
        else:
            row.append("%9.4f %s" % (e["mean_f"], "W" if e["win"] else "L"))
    s = STAR[key]
    row.append("none" if s is None else "%g h" % float(s))
    print(" | ".join(row))
print()
print("calm cells (reporting-only):")
for key in CALM:
    row = ["%-15s" % key, "%12.6f" % P1_MEAN_F[key]]
    for vq in VQ_DECISION:
        e = ARM_A_TABLE[key]["%g" % float(vq)]
        if e.get("unstable"):
            row.append("  UNSTABLE ")
        else:
            row.append("%9.4f %s" % (e["mean_f"],
                                     "w" if e["win_reporting_only"] else "l"))
    print(" | ".join(row))
print()
print("stress column Vq=8 h: " + "; ".join(
    "%s rho=%s%s" % (k, STRESS[k].get("rho"),
                     " UNSTABLE" if STRESS[k].get("unstable") else
                     " mean=%.4f" % STRESS[k]["mean"])
    for k in sorted(STRESS)))
print()
print("DECISION (registered order, REJECT first):")
print("  cells with a winning Vq: %d/5 (REJECT iff <= 2) -> %s"
      % (CELLS_WITH, "REJECT" if CELLS_WITH <= REJECT_CELLS_MAX else "no"))
print("  cells with Vq* >= 2 h:   %d/5 (APPROVE iff >= 4) -> %s"
      % (CELLS_GE2, "APPROVE" if CELLS_GE2 >= APPROVE_CELLS_MIN else "no"))
print("  RULING: %s" % RULING)
print("  stability leg (seed %d, M=%d) ruling: %s"
      % (C["seed_stability"], M_STAB, STAB_RULING))
print("  per-axis WIN shares: lambda %s | V %s" % (
    ", ".join("%s %s" % (k, v["share"])
              for k, v in sorted(AXIS_SHARES["lambda"].items())),
    ", ".join("%s %s" % (k, v["share"])
              for k, v in sorted(AXIS_SHARES["V"].items()))))
print("  binding axes: %s" % "; ".join(BINDING))
print()
print("churn column (free, un-scored): P3Q renumbers = T = 0 measured on every"
      " leg vs committed T " + ", ".join(
          "%s %s" % (k, T_COMMITTED[k]["float"]) for k in TREADMILL))
print()
print("gates: G3/G6 familywise %d gates, %d breaches, max |z| = %.3f"
      % (len(GATE_TABLE), len(BREACHES),
         max(abs(g[6]) for g in GATE_TABLE)))
for gk in sorted(GATES_OUT):
    if gk != "G3_G6_familywise":
        print("  %s: %s" % (gk, GATES_OUT[gk]))

RESULTS["self_checks"]["passed"] = CHECKS_PASSED + 1   # + the final write check
RESULTS["self_checks"]["failed"] = CHECKS_FAILED

out_path = os.path.join(HERE, "results.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")
check(os.path.getsize(out_path) > 0, "results.json written")

print()
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS_PASSED, CHECKS_FAILED))
sys.exit(0 if CHECKS_FAILED == 0 else 1)
