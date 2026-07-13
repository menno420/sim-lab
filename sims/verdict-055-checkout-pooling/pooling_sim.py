#!/usr/bin/env python3
"""VERDICT 055 — checkout pooling folk law at rho = 9/10 (idea-engine PROPOSAL 044).

Hermetic, stdlib-only, deterministic. Reads ONLY fixtures.json (zero repo/network
reads); writes results.json + prints the decision tables. Every constant comes
verbatim from the idea doc via fixtures.json. Decision numbers are exact
fractions.Fraction end-to-end.

Engines: the decision path runs an O(1)-per-customer FIFO engine per
configuration; a literal tick-stepping reference engine implementing the
registered tick semantics (completions -> arrival -> index-order starts)
cross-validates the fast engine per-customer on the hand fixture AND on run 0
of every (leg, cell) — any mismatch aborts.
"""

import functools
import json
import os
import random
import sys
from collections import deque
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

_checks = {"passed": 0}


def check(cond, msg):
    if not cond:
        print("SELF-CHECK FAILED: %s" % msg)
        sys.exit(1)
    _checks["passed"] += 1


_seeds_used = []


class CountingRandom(object):
    """stdlib random.Random wrapped with a draw counter (the sentinel input)."""

    __slots__ = ("_r", "count")

    def __init__(self, seed):
        _seeds_used.append(seed)
        self._r = random.Random(seed)
        self.count = 0

    def randrange(self, n):
        self.count += 1
        return self._r.randrange(n)


# ---------------------------------------------------------------- fixtures

FX = json.load(open(os.path.join(HERE, "fixtures.json")))
FR = FX["frame"]
C = FR["c"]
T = FR["T"]
WARMUP = FR["warmup"]
DRAIN_CAP = FR["drain_cap"]
ADEN = FR["arrival_denominator"]
DECISION_A = FR["decision_A"]
PMF = {int(k): v for k, v in FR["service_pmf"].items()}
PMF_DEN = FR["service_pmf_denominator"]
LEGS = FX["legs"]
BANDS = FX["decision_rule"]["bands"]
REJECT_LT = Fraction(BANDS["reject_lt"])
APPROVE_GE = Fraction(BANDS["approve_ge"])
VALID_FRAC = Fraction(BANDS["validity_fraction"])

check(C == 3, "c == 3")
check(sys.version_info[0] == 3 and "%d.%d" % sys.version_info[:2] == FX["python_minor"],
      "CPython minor pinned to %s (running %d.%d)" % (FX["python_minor"], sys.version_info[0], sys.version_info[1]))

# Service lookup table, rebuilt from the pmf and asserted against the pinned rule
# u = randrange(10): u<3 -> 2, u<6 -> 3, u<8 -> 4, else 6.
SRV = []
for val in sorted(PMF):
    SRV.extend([val] * PMF[val])
SRV = tuple(SRV)
check(len(SRV) == PMF_DEN, "service lookup covers randrange(%d)" % PMF_DEN)
check(SRV == (2, 2, 2, 3, 3, 3, 4, 4, 6, 6), "service lookup matches the pinned rule")
_mean = Fraction(sum(SRV), PMF_DEN)
_es2 = Fraction(sum(s * s for s in SRV), PMF_DEN)
check(_mean == Fraction(FR["service_mean"]), "E[S] == 7/2")
check(_es2 == Fraction(FR["service_E_S2"]), "E[S^2] == 143/10")
check(_es2 - _mean * _mean == Fraction(FR["service_variance"]), "Var[S] == 41/20")
check((_es2 - _mean * _mean) / (_mean * _mean) == Fraction(FR["service_SCV"]), "SCV == 41/245")
for A in FR["load_grid_A"]:
    check(Fraction(A, ADEN) * _mean / C == Fraction(A, 30), "rho identity A=%d -> A/30" % A)


# ---------------------------------------------------------------- engines
#
# Stream = list of (arrival_tick, service, label), at most one arrival per tick,
# ticks strictly increasing. All engines consume the identical stream (common
# random numbers).

def gen_stream(rng, A, horizon):
    stream = []
    before = rng.count
    for t in range(horizon):
        if rng.randrange(ADEN) < A:
            u = rng.randrange(10)
            lab = rng.randrange(3)
            stream.append((t, SRV[u], lab))
    return stream, rng.count - before


def fast_pooled(stream):
    """One shared FIFO. start_k = max(arr_k, min free time); index-order tie
    to the lowest-index idle server (does not affect waits)."""
    f0 = f1 = f2 = 0
    waits = []
    startq = deque()
    maxq = 0
    end = 0
    busy = 0
    for (t, s, _lab) in stream:
        m = f0
        if f1 < m:
            m = f1
        if f2 < m:
            m = f2
        start = m if m > t else t
        if f0 == m:
            f0 = start + s
        elif f1 == m:
            f1 = start + s
        else:
            f2 = start + s
        waits.append(start - t)
        dep = start + s
        busy += s
        if dep > end:
            end = dep
        while startq and startq[0] < t:
            startq.popleft()
        startq.append(start)
        if len(startq) > maxq:
            maxq = len(startq)
    return waits, maxq, end, busy


def fast_split_random(stream):
    """Three FIFO lines joined by the stream label; register j serves line j."""
    free = [0, 0, 0]
    waits = []
    startq = (deque(), deque(), deque())
    maxq = 0
    end = 0
    busy = 0
    for (t, s, lab) in stream:
        f = free[lab]
        start = f if f > t else t
        free[lab] = start + s
        waits.append(start - t)
        dep = start + s
        busy += s
        if dep > end:
            end = dep
        sq = startq[lab]
        while sq and sq[0] < t:
            sq.popleft()
        sq.append(start)
        if len(sq) > maxq:
            maxq = len(sq)
    return waits, maxq, end, busy


def fast_split_jsq(stream):
    """Join-shortest-queue counting the customer in service; ties -> lowest index.
    Presence at the arrival step of tick t == departure time > t."""
    free = [0, 0, 0]
    waits = []
    deps = (deque(), deque(), deque())
    startq = (deque(), deque(), deque())
    routes = []
    maxq = 0
    end = 0
    busy = 0
    for (t, s, _lab) in stream:
        best = 0
        bestc = None
        for j in (0, 1, 2):
            dj = deps[j]
            while dj and dj[0] <= t:
                dj.popleft()
            cj = len(dj)
            if bestc is None or cj < bestc:
                bestc = cj
                best = j
        j = best
        routes.append(j)
        f = free[j]
        start = f if f > t else t
        free[j] = start + s
        waits.append(start - t)
        dep = start + s
        deps[j].append(dep)
        busy += s
        if dep > end:
            end = dep
        sq = startq[j]
        while sq and sq[0] < t:
            sq.popleft()
        sq.append(start)
        if len(sq) > maxq:
            maxq = len(sq)
    return waits, routes, maxq, end, busy


def tick_engine(stream, mode, cap):
    """Literal registered tick semantics: (1) completions (implicit via free_at),
    (2) arrival appended to its queue, (3) idle servers scanned index order 0,1,2
    pull queue heads; WAIT = t - arrival_tick. Event-skipping between ticks where
    nothing can change (exact). Returns None if still non-empty past cap."""
    n = len(stream)
    nq = 1 if mode == "POOLED" else 3
    queues = [deque() for _ in range(nq)]
    free_at = [0, 0, 0]
    waits = [None] * n
    routes = [None] * n
    i = 0
    t = 0
    maxq = 0
    busy = 0
    while True:
        if i < n and stream[i][0] == t:
            arrt, s, lab = stream[i]
            if mode == "POOLED":
                qi = 0
            elif mode == "SPLIT_RANDOM":
                qi = lab
            else:
                counts = [len(queues[j]) + (1 if free_at[j] > t else 0) for j in range(3)]
                qi = counts.index(min(counts))
            queues[qi].append((arrt, s, i))
            routes[i] = qi
            i += 1
            ql = max(len(q) for q in queues)
            if ql > maxq:
                maxq = ql
        for srv in range(3):
            if free_at[srv] <= t:
                q = queues[0] if mode == "POOLED" else queues[srv]
                if q:
                    arrt, s, idx = q.popleft()
                    waits[idx] = t - arrt
                    free_at[srv] = t + s
                    busy += s
        if i >= n and not any(queues):
            return waits, routes, maxq, (max(free_at) if n else 0), busy
        cand = []
        if i < n:
            cand.append(stream[i][0])
        if any(queues):
            cand.extend(f for f in free_at if f > t)
        t = min(cand)
        if t > cap:
            return None


def cross_check(stream, tag):
    """Fast engines vs the literal tick engine, per customer."""
    pw, pq, pe, pb = fast_pooled(stream)
    rw, rq, re_, rb = fast_split_random(stream)
    jw, jr, jq, je, jb = fast_split_jsq(stream)
    for mode, fast in (("POOLED", (pw, pq, pe, pb)),
                       ("SPLIT_RANDOM", (rw, rq, re_, rb)),
                       ("SPLIT_JSQ", (jw, jq, je, jb))):
        ref = tick_engine(stream, mode, 10 ** 9)
        check(ref is not None, "tick engine terminated (%s, %s)" % (tag, mode))
        tw, tr, tq, te, tb = ref
        check(fast[0] == tw, "tick-engine cross-check waits (%s, %s)" % (tag, mode))
        check(fast[1] == tq, "tick-engine cross-check max queue length (%s, %s)" % (tag, mode))
        check(fast[2] == te, "tick-engine cross-check drain end (%s, %s)" % (tag, mode))
        check(fast[3] == tb, "tick-engine cross-check busy ticks (%s, %s)" % (tag, mode))
        if mode == "SPLIT_JSQ":
            check(jr == tr, "tick-engine cross-check JSQ routes (%s)" % tag)


# ---------------------------------------------------------------- gate: hand fixture

HF = FX["hand_fixture"]
hf_stream = list(zip(HF["arrival_ticks"], HF["services"], HF["labels"]))
hf_exp = HF["expected"]
hp = fast_pooled(hf_stream)
hr = fast_split_random(hf_stream)
hj = fast_split_jsq(hf_stream)
check(hp[0] == hf_exp["POOLED_waits"], "hand fixture POOLED waits (0,0,0,1,0,0)")
check(Fraction(sum(hp[0]), len(hp[0])) == Fraction(hf_exp["POOLED_mean"]), "hand fixture POOLED mean 1/6")
check(hr[0] == hf_exp["SPLIT_RANDOM_waits"], "hand fixture SPLIT-RANDOM waits (0,3,0,4,0,0)")
check(Fraction(sum(hr[0]), len(hr[0])) == Fraction(hf_exp["SPLIT_RANDOM_mean"]), "hand fixture SPLIT-RANDOM mean 7/6")
check(hj[0] == hf_exp["SPLIT_JSQ_waits"], "hand fixture SPLIT-JSQ waits (0,0,0,1,0,0)")
check(Fraction(sum(hj[0]), len(hj[0])) == Fraction(hf_exp["SPLIT_JSQ_mean"]), "hand fixture SPLIT-JSQ mean 1/6")
check(hj[1] == hf_exp["SPLIT_JSQ_routes"], "hand fixture JSQ routes (0,1,2,0,1,1)")
check(Fraction(sum(hr[0]), len(hr[0])) / Fraction(sum(hp[0]), len(hp[0])) == Fraction(hf_exp["ratio_R"]),
      "hand fixture ratio R = 7")
cross_check(hf_stream, "hand-fixture")


# ---------------------------------------------------------------- run machinery

def frs(fr):
    return "%d/%d" % (fr.numerator, fr.denominator)


def p95(waits_sorted):
    n = len(waits_sorted)
    idx = -((-95 * n) // 100)  # ceil(0.95 n)
    return waits_sorted[idx - 1]


def run_cell(rng, A, M, leg_name, cross_check_run0):
    """M runs at load A drawn sequentially from the leg generator. Returns run dicts."""
    runs = []
    for m in range(M):
        stream, drew = gen_stream(rng, A, T)
        n_arr = len(stream)
        check(drew == T + 2 * n_arr, "draw sentinel T + 2*arrivals (%s A=%d run %d)" % (leg_name, A, m))
        if m == 0 and cross_check_run0:
            cross_check(stream, "%s-A%d-run0" % (leg_name, A))
        svc_sum = sum(s for (_t, s, _l) in stream)
        cohort_idx = [k for k, (t, _s, _l) in enumerate(stream) if WARMUP <= t < T]
        pw, pq, pe, pb = fast_pooled(stream)
        rw, rq, re_, rb = fast_split_random(stream)
        jw, jr, jq, je, jb = fast_split_jsq(stream)
        # stream identity: all three configurations consumed the same customers
        for tag, w, b in (("POOLED", pw, pb), ("SPLIT_RANDOM", rw, rb), ("SPLIT_JSQ", jw, jb)):
            check(len(w) == n_arr, "stream identity: started count (%s %s A=%d run %d)" % (tag, leg_name, A, m))
            check(b == svc_sum, "work conservation: busy server-ticks == started service sum (%s %s A=%d run %d)" % (tag, leg_name, A, m))
        run = {"run": m, "arrivals": n_arr, "draws": drew, "configs": {}}
        cohort_n = len(cohort_idx)
        valid = True
        why = []
        means = {}
        for tag, w, mq, e, b in (("POOLED", pw, pq, pe, pb),
                                 ("SPLIT_RANDOM", rw, rq, re_, rb),
                                 ("SPLIT_JSQ", jw, jq, je, jb)):
            cw = sorted(w[k] for k in cohort_idx)
            check(len(cw) == cohort_n, "cohort conservation (%s %s A=%d run %d)" % (tag, leg_name, A, m))
            mean = Fraction(sum(cw), cohort_n) if cohort_n else None
            means[tag] = mean
            util = Fraction(b, 3 * e) if e else Fraction(0)
            run["configs"][tag] = {
                "cohort_mean": frs(mean) if mean is not None else None,
                "p95": p95(cw) if cohort_n else None,
                "max_queue_len": mq,
                "utilization": frs(util),
                "drain_end_tick": e,
            }
            if e > DRAIN_CAP:
                valid = False
                why.append("drain-cap-exceeded:%s" % tag)
        if cohort_n and means["POOLED"] == 0:
            valid = False
            why.append("pooled-cohort-mean-zero")
        run["valid"] = valid
        run["invalid_reasons"] = why
        if valid and cohort_n:
            run["R"] = frs(means["SPLIT_RANDOM"] / means["POOLED"])
            run["R_jsq"] = frs(means["SPLIT_JSQ"] / means["POOLED"])
        else:
            run["R"] = None
            run["R_jsq"] = None
        run["_means"] = means
        runs.append(run)
    return runs


def median_fr(vals):
    s = sorted(vals)
    n = len(s)
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


# ---------------------------------------------------------------- legs

legs_out = {}
leg_summaries = []

# control leg FIRST (gate on the arrival machinery): A = 0, M = 4, own generator
# instance seeded with the main seed (fixtures.json legs.control).
ctrl_rng = CountingRandom(LEGS["control"]["seed"])
ctrl_runs = []
for m in range(LEGS["control"]["M"]):
    stream, drew = gen_stream(ctrl_rng, 0, T)
    check(len(stream) == 0, "A=0 control: zero arrivals (run %d)" % m)
    check(drew == T, "A=0 control: draw sentinel exactly T (run %d)" % m)
    pw, pq, pe, pb = fast_pooled(stream)
    check(len(pw) == 0 and pb == 0 and pe == 0, "A=0 control: zero starts, zero busy ticks (run %d)" % m)
    if m == 0:
        cross_check(stream, "control-A0-run0")
    ctrl_runs.append({"run": m, "arrivals": 0, "draws": drew, "valid": True})
check(ctrl_rng.count == LEGS["control"]["M"] * T, "A=0 control leg total draw sentinel")
legs_out["control"] = {"seed": LEGS["control"]["seed"], "A": 0, "M": LEGS["control"]["M"], "runs": ctrl_runs}

def leg_pass(leg_name, cross0):
    leg = LEGS[leg_name]
    rng = CountingRandom(leg["seed"])
    cells = {}
    expected_draws = 0
    for A in leg["A"]:  # ascending by fixture construction
        runs = run_cell(rng, A, leg["M"], leg_name, cross0)
        expected_draws += sum(r["draws"] for r in runs)
        cells[A] = runs
    check(rng.count == expected_draws, "per-leg draw-count sentinel (%s)" % leg_name)
    return cells

main_cells = leg_pass("main", True)
stab_cells = leg_pass("stability", True)
rep_cells = leg_pass("reporting", True)

check(LEGS["aux"]["seed"] not in _seeds_used, "aux seed 20261316 reserved - never read")
check(sorted(set(_seeds_used)) == sorted({LEGS["main"]["seed"], LEGS["stability"]["seed"],
                                          LEGS["reporting"]["seed"]}),
      "only the registered main/stability/reporting/control seeds were drawn from")


# ---------------------------------------------------------------- audits (reporting, never invalidating)

anomalies = []

def audit_leg(leg_name, A, runs):
    for r in runs:
        mp = r["_means"]["POOLED"]
        ms = r["_means"]["SPLIT_RANDOM"]
        if mp is not None and ms is not None and not (mp <= ms):
            anomalies.append("ANOMALY pooled-dominance %s A=%d run=%d: W(POOLED)=%s > W(SPLIT_RANDOM)=%s"
                             % (leg_name, A, r["run"], frs(mp), frs(ms)))

audit_leg("main", DECISION_A, main_cells[DECISION_A])
audit_leg("stability", DECISION_A, stab_cells[DECISION_A])
for A in LEGS["reporting"]["A"]:
    audit_leg("reporting", A, rep_cells[A])

# load monotonicity across A in {21, 24, 27} per configuration (cell mean of
# per-run cohort means, valid runs; A=27 from the main leg).
mono_cells = [(21, rep_cells[21]), (24, rep_cells[24]), (27, main_cells[DECISION_A])]
mono_table = {}
for cfg in ("POOLED", "SPLIT_RANDOM", "SPLIT_JSQ"):
    seq = []
    for A, runs in mono_cells:
        vals = [r["_means"][cfg] for r in runs if r["valid"]]
        seq.append((A, sum(vals) / len(vals)))
    mono_table[cfg] = seq
    for (a1, v1), (a2, v2) in zip(seq, seq[1:]):
        if not (v1 <= v2):
            anomalies.append("ANOMALY load-monotonicity %s: mean cohort wait A=%d (%s) > A=%d (%s)"
                             % (cfg, a1, frs(v1), a2, frs(v2)))


# ---------------------------------------------------------------- twin decision evaluators

def evaluator_one(main_runs, stab_runs):
    """Twin #1 — fractions.Fraction comparisons throughout."""
    total = len(main_runs)
    invalid = sum(1 for r in main_runs if not r["valid"])
    if not (Fraction(invalid, total) < VALID_FRAC):
        return ("NULL", "settlement-failure")
    med = median_fr([r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"] for r in main_runs if r["valid"]])
    if med < REJECT_LT:
        return ("REJECT", None)
    if med >= APPROVE_GE:
        st = len(stab_runs)
        sinv = sum(1 for r in stab_runs if not r["valid"])
        if Fraction(sinv, st) < VALID_FRAC:
            smed = median_fr([r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"] for r in stab_runs if r["valid"]])
            if smed >= APPROVE_GE:
                return ("APPROVE", None)
        return ("NULL", "stability-non-reproduction")
    return ("NULL", "band-straddle")


def _pair_cmp(a, b):
    x = a[0] * b[1] - b[0] * a[1]
    return -1 if x < 0 else (1 if x > 0 else 0)


def _pair_median(pairs):
    s = sorted(pairs, key=functools.cmp_to_key(_pair_cmp))
    n = len(s)
    if n % 2:
        return s[n // 2]
    (a, b), (c, d) = s[n // 2 - 1], s[n // 2]
    return (a * d + c * b, 2 * b * d)


def evaluator_two(main_pairs, main_flags, stab_pairs, stab_flags):
    """Twin #2 — independently written, pure-integer cross-multiplication.
    Bands hardwired as integers: R < 3/2 <=> 2n < 3d; R >= 2 <=> n >= 2d;
    validity <=> 4*invalid < total."""
    total = len(main_flags)
    invalid = total - sum(main_flags)
    if not (4 * invalid < total):
        return ("NULL", "settlement-failure")
    n, d = _pair_median([p for p, ok in zip(main_pairs, main_flags) if ok])
    if 2 * n < 3 * d:
        return ("REJECT", None)
    if n >= 2 * d:
        st = len(stab_flags)
        sinv = st - sum(stab_flags)
        if 4 * sinv < st:
            sn, sd = _pair_median([p for p, ok in zip(stab_pairs, stab_flags) if ok])
            if sn >= 2 * sd:
                return ("APPROVE", None)
        return ("NULL", "stability-non-reproduction")
    return ("NULL", "band-straddle")


main_runs = main_cells[DECISION_A]
stab_runs = stab_cells[DECISION_A]

verdict1 = evaluator_one(main_runs, stab_runs)

def _pairs(runs):
    pairs = []
    flags = []
    for r in runs:
        flags.append(1 if r["valid"] else 0)
        if r["valid"]:
            ratio = r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"]
            pairs.append((ratio.numerator, ratio.denominator))
        else:
            pairs.append((0, 1))  # placeholder, masked by its flag
    return pairs, flags

mp_, mf_ = _pairs(main_runs)
sp_, sf_ = _pairs(stab_runs)
verdict2 = evaluator_two(mp_, mf_, sp_, sf_)
check(verdict1 == verdict2, "twin decision evaluators agree (%s vs %s)" % (verdict1, verdict2))

VERDICT_CLASS, VERDICT_AXIS = verdict1

median_R = median_fr([r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"] for r in main_runs if r["valid"]])
median_R_stab = median_fr([r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"] for r in stab_runs if r["valid"]])


# ---------------------------------------------------------------- report

def cell_summary(leg_name, seed, A, runs, decision_cell):
    valid_runs = [r for r in runs if r["valid"]]
    Rs = [r["_means"]["SPLIT_RANDOM"] / r["_means"]["POOLED"] for r in valid_runs]
    Rjs = [r["_means"]["SPLIT_JSQ"] / r["_means"]["POOLED"] for r in valid_runs]
    out = {
        "leg": leg_name,
        "seed": seed,
        "A": A,
        "rho": "%d/30" % A,
        "M": len(runs),
        "invalid": len(runs) - len(valid_runs),
        "median_R": frs(median_fr(Rs)),
        "median_R_decimal": "%.6f" % float(median_fr(Rs)),
        "median_R_jsq": frs(median_fr(Rjs)),
        "median_R_jsq_decimal": "%.6f" % float(median_fr(Rjs)),
        "decision_cell": decision_cell,
    }
    for cfg in ("POOLED", "SPLIT_RANDOM", "SPLIT_JSQ"):
        means = [r["_means"][cfg] for r in valid_runs]
        p95s = sorted(r["configs"][cfg]["p95"] for r in valid_runs)
        out[cfg] = {
            "mean_of_cohort_means": frs(sum(means) / len(means)),
            "mean_of_cohort_means_decimal": "%.6f" % float(sum(means) / len(means)),
            "median_p95": p95s[len(p95s) // 2],
            "max_queue_len": max(r["configs"][cfg]["max_queue_len"] for r in valid_runs),
            "median_utilization": frs(median_fr([Fraction(r["configs"][cfg]["utilization"]) for r in valid_runs])),
            "max_drain_end_tick": max(r["configs"][cfg]["drain_end_tick"] for r in valid_runs),
        }
    return out

summaries = [
    cell_summary("main", LEGS["main"]["seed"], DECISION_A, main_runs, True),
    cell_summary("stability", LEGS["stability"]["seed"], DECISION_A, stab_runs, False),
]
for A in LEGS["reporting"]["A"]:
    summaries.append(cell_summary("reporting", LEGS["reporting"]["seed"], A, rep_cells[A], False))

print("VERDICT 055 - checkout pooling folk law at rho = 9/10 (idea-engine PROPOSAL 044)")
print("frame: c=%d T=%d warmup=%d drain_cap=%d arrivals randrange(%d)<A service pmf {2:3,3:3,4:2,6:2}/10 (E[S]=7/2, SCV=41/245)"
      % (C, T, WARMUP, DRAIN_CAP, ADEN))
print("hermetic: reads fixtures.json only; CPython %s asserted; exact Fractions at every decision point" % FX["python_minor"])
print("")
print("GATES")
print("  hand fixture (8-tick): POOLED (0,0,0,1,0,0) mean 1/6 | SPLIT-RANDOM (0,3,0,4,0,0) mean 7/6 | SPLIT-JSQ (0,0,0,1,0,0) mean 1/6, routes (0,1,2,0,1,1) | ratio R=7 ... PASS")
print("  tick-engine cross-check (literal completions->arrival->index-order-starts semantics) on the hand fixture + run 0 of every (leg, cell), per-customer equality, all three configurations ... PASS")
print("  A=0 control leg (M=%d, own generator on the main seed): zero arrivals, zero starts, zero busy ticks, per-run sentinel exactly T ... PASS" % LEGS["control"]["M"])
print("  work conservation (started service sum == busy server-ticks), stream identity across configurations, cohort conservation, per-run + per-leg draw sentinels (T + 2*arrivals) ... PASS")
print("  aux seed %d reserved - never constructed, never drawn ... PASS" % LEGS["aux"]["seed"])
print("  twin decision evaluators (Fraction comparisons vs pure-integer cross-multiplication): %s == %s ... PASS" % (verdict1, verdict2))
print("")
print("RESULTS (per cell; per-run tables in results.json)")
hdr = "  %-10s %-4s %-6s %-8s %-9s %-11s %-11s %-9s %-9s %-8s %-8s"
print(hdr % ("leg", "A", "rho", "M(inv)", "medianR", "meanW-POOL", "meanW-SPLIT", "medR-JSQ", "p95P/S/J", "maxq P/S", "util-med"))
for s in summaries:
    print(hdr % (
        s["leg"], s["A"], s["rho"], "%d(%d)" % (s["M"], s["invalid"]),
        s["median_R_decimal"],
        s["POOLED"]["mean_of_cohort_means_decimal"],
        s["SPLIT_RANDOM"]["mean_of_cohort_means_decimal"],
        s["median_R_jsq_decimal"],
        "%d/%d/%d" % (s["POOLED"]["median_p95"], s["SPLIT_RANDOM"]["median_p95"], s["SPLIT_JSQ"]["median_p95"]),
        "%d/%d" % (s["POOLED"]["max_queue_len"], s["SPLIT_RANDOM"]["max_queue_len"]),
        s["POOLED"]["median_utilization"],
    ))
print("")
print("AUDITS (reporting-only, never invalidating)")
if anomalies:
    for a in anomalies:
        print("  " + a)
else:
    print("  pooled-dominance: W(POOLED) <= W(SPLIT_RANDOM) on every valid run of every leg - no anomaly")
print("  load-monotonicity across A in {21,24,27}: " + "; ".join(
    "%s %s" % (cfg, " <= ".join("A%d %.4f" % (A, float(v)) for A, v in mono_table[cfg])) for cfg in ("POOLED", "SPLIT_RANDOM", "SPLIT_JSQ")))
print("")
print("DECISION (pre-registered, applied IN ORDER - REJECT first; bands 3/2 and 2; both bands carry the <1/4-invalid validity conjunct)")
mn = len(main_runs)
minv = mn - sum(1 for r in main_runs if r["valid"])
print("  validity conjunct (main): %d invalid of %d (< 1/4) ... %s" % (minv, mn, "PASS" if 4 * minv < mn else "FAIL"))
print("  median R (main, seed %d, A=%d, valid M=%d) = %s = %.6f" % (LEGS["main"]["seed"], DECISION_A, mn - minv, frs(median_R), float(median_R)))
print("  REJECT iff median R < 3/2: %s" % ("FIRES" if median_R < REJECT_LT else "does NOT fire"))
print("  APPROVE iff median R >= 2 AND stability reproduces: median >= 2 is %s; stability (seed %d, M=%d, %d invalid) median R = %s = %.6f -> %s"
      % (median_R >= APPROVE_GE, LEGS["stability"]["seed"], len(stab_runs),
         len(stab_runs) - sum(1 for r in stab_runs if r["valid"]),
         frs(median_R_stab), float(median_R_stab),
         "reproduces" if (median_R_stab >= APPROVE_GE and 4 * (len(stab_runs) - sum(1 for r in stab_runs if r["valid"])) < len(stab_runs)) else "does NOT reproduce"))
print("")
print("  VERDICT: %s%s" % (VERDICT_CLASS, ("" if VERDICT_AXIS is None else " (binding axis: %s)" % VERDICT_AXIS)))
print("")
print("SELF-CHECKS: %d passed, 0 failed" % _checks["passed"])

# ---------------------------------------------------------------- results.json

def strip(runs):
    out = []
    for r in runs:
        rr = {k: v for k, v in r.items() if not k.startswith("_")}
        out.append(rr)
    return out

results = {
    "verdict": "VERDICT 055",
    "proposal": FX["proposal"],
    "python_minor": FX["python_minor"],
    "decision": {
        "class": VERDICT_CLASS,
        "binding_axis": VERDICT_AXIS,
        "median_R_main": frs(median_R),
        "median_R_main_decimal": "%.6f" % float(median_R),
        "median_R_stability": frs(median_R_stab),
        "median_R_stability_decimal": "%.6f" % float(median_R_stab),
        "evaluators_agree": True,
        "rule": FX["decision_rule"],
    },
    "cell_summaries": summaries,
    "load_monotonicity_table": {cfg: [[A, frs(v)] for A, v in seq] for cfg, seq in mono_table.items()},
    "anomalies": anomalies,
    "self_checks_passed": _checks["passed"],
    "legs": {
        "control": legs_out["control"],
        "main": {"seed": LEGS["main"]["seed"], "cells": {str(DECISION_A): strip(main_runs)}},
        "stability": {"seed": LEGS["stability"]["seed"], "cells": {str(DECISION_A): strip(stab_runs)}},
        "reporting": {"seed": LEGS["reporting"]["seed"], "cells": {str(A): strip(rep_cells[A]) for A in LEGS["reporting"]["A"]}},
        "aux": {"seed": LEGS["aux"]["seed"], "draws": 0, "note": "reserved - never read"},
    },
}

with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")
