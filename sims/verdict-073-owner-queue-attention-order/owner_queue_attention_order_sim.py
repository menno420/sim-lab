#!/usr/bin/env python3
"""VERDICT 073 — owner-queue attention order (idea-engine PROPOSAL 062, INTAKE 062).

Hermetic, stdlib-only, deterministic. Reads ONLY its own fixtures.json.
Arm A (DECISION, seedless): integer prefix sums for completion clocks,
       exact fractions.Fraction for MEAN and V_gamma = sum gamma^{C_i} —
       full five-policy x two-accounting table, live curves, theorems.
Arm B (twin, seedless): INDEPENDENTLY-WRITTEN event-walk stepping the owner
       clock one interaction at a time (own order builders, own metrics);
       must reproduce every Arm-A published number EXACTLY.
Arm R (seeded, REPORTING-ONLY, no statistical gate): owner-sitting traces,
       budgets i.i.d. from the pinned pmf {3: 1/2, 8: 3/10, 21: 1/5} — main
       seed 20261385 (N = 100,000 episodes/policy), stability 20261386
       (N = 20,000), presentation shuffle 20261387; aux 20261388 NEVER read.
Pre-registered rule evaluated IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
Run: python3 owner_queue_attention_order_sim.py   (paths self-anchor)
"""

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
        print("SELF-CHECK FAIL: %s" % name)
    return bool(cond)


def fstr(x):
    """Canonical lowest-terms 'p/q' string (C7)."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return "%d/%d" % (x.numerator, x.denominator)


def ffl(x):
    """Float rendering via repr (C7)."""
    return repr(float(Fraction(x)))


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check("cpython-minor-pinned-3.11",
      sys.version_info[:2] == tuple(FX["cpython_minor_pinned"]))

ROWS = FX["rows_document_order"]
NSEQ = len(ROWS)
ROLL = FX["committed_rollups"]
DECISIONS = int(FX["decision_layer"]["items"])
LAYER = {"BATCHED": int(FX["decision_layer"]["accountings"]["BATCHED"]),
         "PER_ITEM": int(FX["decision_layer"]["accountings"]["PER_ITEM"])}
ACCTS = ["BATCHED", "PER_ITEM"]
POLICIES = list(FX["policies"]["canonical_order"])
GAMMAS = [Fraction(g) for g in FX["gamma_grid"]]
GAMMA_KEYS = list(FX["gamma_grid"])
G_DEC = Fraction(FX["gamma_decision"])
LINE_11_10 = Fraction(11, 10)
BANDS_R = FX["decision_bands"]["REJECT_any_of"]
BANDS_A = FX["decision_bands"]["APPROVE_all_of"]

# ---------------------------------------------------------------- F1 identity
ung = [r for r in ROWS if not r["gated"]]
gat = [r for r in ROWS if r["gated"]]
f1 = True
f1 &= check("F1-rows-28-ungated", len(ung) == ROLL["ungated_rows"] == 28)
f1 &= check("F1-rows-16-gated", len(gat) == ROLL["gated_sequences"] == 16)
f1 &= check("F1-ungated-sum-152",
            sum(r["clicks"] for r in ung) == ROLL["ungated_sum"] == 152)
f1 &= check("F1-gated-sum-110",
            sum(r["clicks"] for r in gat) == ROLL["gated_sum"] == 110)
f1 &= check("F1-total-262",
            sum(r["clicks"] for r in ROWS) == ROLL["clicks_total"] == 262)
f1 &= check("F1-44-sequences", NSEQ == ROLL["sequences"] == 44)
f1 &= check("F1-19-decisions", DECISIONS == ROLL["decisions"] == 19)
f1 &= check("F1-ungated-count-vector",
            [r["clicks"] for r in ung] == ROLL["ungated_count_vector"])
f1 &= check("F1-gated-count-vector",
            [r["clicks"] for r in gat] == ROLL["gated_count_vector"])
sent = FX["_provenance"]["harvested_quotes_pinned_68d57bb"]["current_state_rollup"]
f1 &= check("F1-rollups-in-committed-sentence",
            all(s in sent for s in ("19 decisions", "44 click-run",
                                    "262 unchecked owner clicks",
                                    "16 sequences hard-gated")))
GATE_F1 = f1


# ================================================================ Arm A
def arm_a_orders(rows):
    """Arm-A policy schedules: items ('L',) layer / ('S', i) sequence."""
    idx = list(range(len(rows)))
    ung_i = [i for i in idx if not rows[i]["gated"]]
    gat_i = [i for i in idx if rows[i]["gated"]]
    spt_all = sorted(idx, key=lambda i: (rows[i]["clicks"], i))
    lpt_all = sorted(idx, key=lambda i: (-rows[i]["clicks"], i))
    ung_spt = sorted(ung_i, key=lambda i: (rows[i]["clicks"], i))
    gat_spt = sorted(gat_i, key=lambda i: (rows[i]["clicks"], i))
    return {
        "DOC": [("L",)] + [("S", i) for i in idx],
        "SPT": [("L",)] + [("S", i) for i in spt_all],
        "LPT": [("L",)] + [("S", i) for i in lpt_all],
        "LAZY-DOC": ([("S", i) for i in ung_i] + [("L",)]
                     + [("S", i) for i in gat_i]),
        "LAZY-SPT": ([("S", i) for i in ung_spt] + [("L",)]
                     + [("S", i) for i in gat_spt]),
    }


def arm_a_clocks(schedule, rows, layer_cost):
    """Integer prefix sums -> completion clock per sequence index."""
    t = 0
    clocks = {}
    for item in schedule:
        if item[0] == "L":
            t += layer_cost
        else:
            i = item[1]
            t += rows[i]["clicks"]
            clocks[i] = t
    return clocks, t


def arm_a_metrics(clocks, T, nseq):
    cs = sorted(clocks.values())
    v = {}
    for g in GAMMAS:
        v[g] = sum((g ** c for c in cs), Fraction(0))
    arr = [0] * (T + 1)
    for c in cs:
        arr[c] += 1
    curve = []
    acc = 0
    for t in range(T + 1):
        acc += arr[t]
        curve.append(acc)
    return {"clocks": dict(clocks), "TTF": cs[0],
            "T22": cs[21] if nseq >= 22 else None,
            "MEAN": Fraction(sum(cs), nseq), "V": v, "curve": curve, "T": T}


def arm_a_world(rows):
    orders = arm_a_orders(rows)
    total = sum(r["clicks"] for r in rows)
    out = {}
    for acct in ACCTS:
        out[acct] = {}
        for pol in POLICIES:
            clocks, t_end = arm_a_clocks(orders[pol], rows, LAYER[acct])
            out[acct][pol] = arm_a_metrics(clocks, total + LAYER[acct],
                                           len(rows))
            out[acct][pol]["t_end"] = t_end
    return out, orders


A_MAIN, A_ORDERS = arm_a_world(ROWS)


# ================================================================ Arm B
def arm_b_orders(rows):
    """Arm-B policy schedules — explicit selection loops, no sorted()."""
    n = len(rows)

    def select(indices, largest_first):
        pool = list(indices)  # ascending document order
        out = []
        while pool:
            best = pool[0]
            for j in pool[1:]:
                if largest_first:
                    if rows[j]["clicks"] > rows[best]["clicks"]:
                        best = j
                else:
                    if rows[j]["clicks"] < rows[best]["clicks"]:
                        best = j
            out.append(best)
            pool.remove(best)
        return out

    idx = list(range(n))
    ung_i = []
    gat_i = []
    for i in idx:
        if rows[i]["gated"]:
            gat_i.append(i)
        else:
            ung_i.append(i)
    return {
        "DOC": [("L",)] + [("S", i) for i in idx],
        "SPT": [("L",)] + [("S", i) for i in select(idx, False)],
        "LPT": [("L",)] + [("S", i) for i in select(idx, True)],
        "LAZY-DOC": ([("S", i) for i in ung_i] + [("L",)]
                     + [("S", i) for i in gat_i]),
        "LAZY-SPT": ([("S", i) for i in select(ung_i, False)] + [("L",)]
                     + [("S", i) for i in select(gat_i, False)]),
    }


def arm_b_walk(schedule, rows, layer_cost):
    """Event-walk: one owner interaction per tick."""
    items = []
    for it in schedule:
        if it[0] == "L":
            items.append((None, layer_cost))
        else:
            items.append((it[1], rows[it[1]]["clicks"]))
    t = 0
    live = 0
    curve = [0]
    completions = []
    for seq, cost in items:
        rem = cost
        while rem > 0:
            t += 1
            rem -= 1
            if rem == 0 and seq is not None:
                live += 1
                completions.append((t, seq))
            curve.append(live)
    return completions, curve, t


def arm_b_metrics(completions, curve, t_end, nseq):
    clocks = {}
    for c, seq in completions:
        clocks[seq] = c
    ordered = []
    for c, _seq in completions:
        ordered.append(c)
    ordered.sort()
    total = 0
    for c in ordered:
        total += c
    v = {}
    for g in GAMMAS:
        acc = Fraction(0)
        for c in ordered:
            acc = acc + g ** c
        v[g] = acc
    return {"clocks": clocks, "TTF": ordered[0],
            "T22": ordered[21] if nseq >= 22 else None,
            "MEAN": Fraction(total, nseq), "V": v, "curve": curve,
            "T": t_end, "t_end": t_end}


def arm_b_world(rows):
    orders = arm_b_orders(rows)
    out = {}
    for acct in ACCTS:
        out[acct] = {}
        for pol in POLICIES:
            comps, curve, t_end = arm_b_walk(orders[pol], rows, LAYER[acct])
            out[acct][pol] = arm_b_metrics(comps, curve, t_end, len(rows))
    return out


B_MAIN = arm_b_world(ROWS)

# ---------------------------------------------------------------- F2 conservation
f2 = True
for acct in ACCTS:
    t_expect = ROLL["clicks_total"] + LAYER[acct]
    for pol in POLICIES:
        m = A_MAIN[acct][pol]
        f2 &= check("F2-final-clock-%s-%s" % (acct, pol),
                    m["t_end"] == t_expect and max(m["clocks"].values())
                    == t_expect)
        f2 &= check("F2-all-44-live-%s-%s" % (acct, pol),
                    len(m["clocks"]) == NSEQ
                    and m["curve"][t_expect] == NSEQ)
        steps = [m["curve"][t + 1] - m["curve"][t]
                 for t in range(len(m["curve"]) - 1)]
        f2 &= check("F2-curve-steps-%s-%s" % (acct, pol),
                    all(s in (0, 1) for s in steps)
                    and sum(steps) == NSEQ and m["curve"][0] == 0)
GATE_F2 = f2

# ---------------------------------------------------------------- F3 theorems
f3 = True
F3_FLAGS = {"exchange": True, "dominance": True, "anchor": True}
spt_seq_order = [it[1] for it in A_ORDERS["SPT"] if it[0] == "S"]
for acct in ACCTS:
    base = A_MAIN[acct]["SPT"]
    all_ok_mean = True
    all_ok_v = True
    for k in range(NSEQ - 1):
        swapped = list(spt_seq_order)
        swapped[k], swapped[k + 1] = swapped[k + 1], swapped[k]
        sched = [("L",)] + [("S", i) for i in swapped]
        clocks, _ = arm_a_clocks(sched, ROWS, LAYER[acct])
        m = arm_a_metrics(clocks, ROLL["clicks_total"] + LAYER[acct], NSEQ)
        i, j = spt_seq_order[k], spt_seq_order[k + 1]
        delta = Fraction(ROWS[j]["clicks"] - ROWS[i]["clicks"], NSEQ)
        if not (m["MEAN"] - base["MEAN"] == delta and delta >= 0):
            all_ok_mean = False
        for g in GAMMAS:
            if not m["V"][g] <= base["V"][g]:
                all_ok_v = False
    f3 &= check("F3a-exchange-mean-43-swaps-%s" % acct, all_ok_mean)
    f3 &= check("F3a-exchange-V-43-swaps-all-gamma-%s" % acct, all_ok_v)
    F3_FLAGS["exchange"] &= (all_ok_mean and all_ok_v)
    cs, cd, cl = (A_MAIN[acct][p]["curve"] for p in ("SPT", "DOC", "LPT"))
    dom1 = all(a >= b for a, b in zip(cs, cd))
    dom2 = all(a >= b for a, b in zip(cs, cl))
    f3 &= check("F3b-L_SPT-ge-L_DOC-%s" % acct, dom1)
    f3 &= check("F3b-L_SPT-ge-L_LPT-%s" % acct, dom2)
    cls_, cld = (A_MAIN[acct][p]["curve"] for p in ("LAZY-SPT", "LAZY-DOC"))
    dom3 = all(a >= b for a, b in zip(cls_, cld))
    f3 &= check("F3b-L_LAZYSPT-ge-L_LAZYDOC-%s" % acct, dom3)
    F3_FLAGS["dominance"] &= (dom1 and dom2 and dom3)
    anch = all(A_MAIN[acct]["SPT"]["V"][g] > A_MAIN[acct]["LPT"]["V"][g]
               for g in GAMMAS)
    f3 &= check("F3c-V-anchor-SPT-gt-LPT-%s" % acct, anch)
    F3_FLAGS["anchor"] &= anch
GATE_F3 = f3

# ---------------------------------------------------------------- F4 hand world
HW = FX["gates"]["F4_hand_world"]
HROWS = HW["rows"]
HA, _ho = arm_a_world(HROWS)
HB = arm_b_world(HROWS)
f4 = True
EXPECT4 = {"DOC": HW["expected"]["DOC"], "SPT": HW["expected"]["SPT"],
           "LAZY-SPT": HW["expected"]["LAZY"]}
for pol in ("DOC", "SPT", "LAZY-SPT"):
    exp = EXPECT4[pol]
    for arm_name, world in (("A", HA), ("B", HB)):
        m = world["BATCHED"][pol]
        got = sorted(m["clocks"].values())
        f4 &= check("F4-hand-%s-arm%s-clocks" % (pol, arm_name),
                    got == list(exp["clocks"]))
        f4 &= check("F4-hand-%s-arm%s-mean" % (pol, arm_name),
                    m["MEAN"] == Fraction(exp["MEAN"]))
        f4 &= check("F4-hand-%s-arm%s-ttf" % (pol, arm_name),
                    m["TTF"] == exp["TTF"])
GATE_F4 = f4

# ---------------------------------------------------------------- F5 gamma-mono
f5 = True
for acct in ACCTS:
    for pol in POLICIES:
        v = A_MAIN[acct][pol]["V"]
        f5 &= check("F5-gamma-monotone-%s-%s" % (acct, pol),
                    v[GAMMAS[0]] < v[GAMMAS[1]] < v[GAMMAS[2]])
GATE_F5 = f5


# ---------------------------------------------------------------- twin equality
def cells_equal(label, wa, wb, nseq):
    ok = True
    for acct in ACCTS:
        for pol in POLICIES:
            ma, mb = wa[acct][pol], wb[acct][pol]
            same = (ma["clocks"] == mb["clocks"]
                    and ma["curve"] == mb["curve"]
                    and ma["TTF"] == mb["TTF"] and ma["T22"] == mb["T22"]
                    and ma["MEAN"] == mb["MEAN"]
                    and all(ma["V"][g] == mb["V"][g] for g in GAMMAS)
                    and ma["t_end"] == mb["t_end"])
            ok &= check("F6-twin-equal-%s-%s-%s" % (label, acct, pol), same)
    return ok


TWIN_MAIN = cells_equal("main", A_MAIN, B_MAIN, NSEQ)
TWIN_HAND = cells_equal("hand", HA, HB, len(HROWS))


# ---------------------------------------------------------------- evaluators
def clause_values(world):
    """Registered comparisons: DOC vs best non-DOC, same accounting."""
    others = [p for p in POLICIES if p != "DOC"]
    out = {}
    for acct in ACCTS:
        cells = world[acct]
        best_mean_pol = min(others, key=lambda p: (cells[p]["MEAN"],
                                                   others.index(p)))
        best_v_pol = max(others, key=lambda p: (cells[p]["V"][G_DEC],
                                                -others.index(p)))
        best_ttf_pol = min(others, key=lambda p: (cells[p]["TTF"],
                                                  others.index(p)))
        out[acct] = {
            "gapMEAN": cells["DOC"]["MEAN"] - cells[best_mean_pol]["MEAN"],
            "best_MEAN_policy": best_mean_pol,
            "ratioV": cells[best_v_pol]["V"][G_DEC] / cells["DOC"]["V"][G_DEC],
            "best_V_policy": best_v_pol,
            "TTF_DOC": cells["DOC"]["TTF"],
            "TTF_best": cells[best_ttf_pol]["TTF"],
            "best_TTF_policy": best_ttf_pol,
        }
    return out


def evaluator_one(world, gates_ok):
    """Decision evaluator 1 (Arm-A numbers, Fraction band comparisons)."""
    cv = clause_values(world)
    b, p = cv["BATCHED"], cv["PER_ITEM"]
    r1 = b["gapMEAN"] >= Fraction(BANDS_R["R1_gapMEAN_BATCHED_min"])
    r2 = b["ratioV"] >= Fraction(BANDS_R["R2_ratioV_BATCHED_99_100_min"])
    r3 = b["TTF_DOC"] >= (BANDS_R["R3_TTF_DOC_over_best_BATCHED_min_factor"]
                          * b["TTF_best"])
    a1 = b["gapMEAN"] <= Fraction(BANDS_A["A1_gapMEAN_BATCHED_max"])
    a2 = b["ratioV"] < Fraction(BANDS_A["A2_ratioV_BATCHED_99_100_strictly_below"])
    a3 = b["TTF_DOC"] <= (BANDS_A["A3_TTF_DOC_over_best_BATCHED_max_factor"]
                          * b["TTF_best"])
    a4 = p["gapMEAN"] >= Fraction(BANDS_A["A4_gapMEAN_PER_ITEM_min"])
    a5 = p["TTF_DOC"] >= (BANDS_A["A5_TTF_DOC_over_best_PER_ITEM_min_factor"]
                          * p["TTF_best"])
    clauses = {"R1": r1, "R2": r2, "R3": r3,
               "A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5}
    if r1 or r2 or r3:
        token = "REJECT"
    elif not gates_ok:
        token = "INVALID"
    elif a1 and a2 and a3 and a4 and a5:
        token = "APPROVE"
    else:
        token = "NULL"
    return token, clauses, cv


def evaluator_two(world, gates_ok):
    """Decision evaluator 2 — independently written band logic (Arm-B
    numbers, integer cross-multiplication instead of Fraction compares)."""
    others = []
    for p in POLICIES:
        if p != "DOC":
            others.append(p)

    def stats(acct):
        cells = world[acct]
        gap = None
        for p in others:
            g = cells["DOC"]["MEAN"] - cells[p]["MEAN"]
            if gap is None or g > gap:
                gap = g
        vmax = None
        for p in others:
            v = cells[p]["V"][G_DEC]
            if vmax is None or v > vmax:
                vmax = v
        tbest = None
        for p in others:
            t = cells[p]["TTF"]
            if tbest is None or t < tbest:
                tbest = t
        return gap, vmax, cells["DOC"]["V"][G_DEC], cells["DOC"]["TTF"], tbest

    gap_b, vmax_b, vdoc_b, tdoc_b, tbest_b = stats("BATCHED")
    gap_p, _vm, _vd, tdoc_p, tbest_p = stats("PER_ITEM")
    # cross-multiplied comparisons (gap = num/den as Fraction fields)
    fire_r = (gap_b.numerator * 1 >= 10 * gap_b.denominator
              or 10 * vmax_b.numerator * vdoc_b.denominator
              >= 11 * vdoc_b.numerator * vmax_b.denominator
              or tdoc_b >= 3 * tbest_b)
    ok_a = (gap_b.numerator <= 8 * gap_b.denominator
            and 10 * vmax_b.numerator * vdoc_b.denominator
            < 11 * vdoc_b.numerator * vmax_b.denominator
            and tdoc_b <= 2 * tbest_b
            and gap_p.numerator >= 15 * gap_p.denominator
            and tdoc_p >= 4 * tbest_p)
    if fire_r:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if ok_a:
        return "APPROVE"
    return "NULL"


# ---------------------------------------------------------------- reporting legs
CV_MAIN = clause_values(A_MAIN)

BATCH_DOOR = {}
for pol in POLICIES:
    BATCH_DOOR[pol] = {
        "mean_price": A_MAIN["PER_ITEM"][pol]["MEAN"]
        - A_MAIN["BATCHED"][pol]["MEAN"],
        "ttf_factor": Fraction(A_MAIN["PER_ITEM"][pol]["TTF"],
                               A_MAIN["BATCHED"][pol]["TTF"]),
    }

LPT_ANCHOR = A_MAIN["BATCHED"]["LPT"]["MEAN"]

GAMMA_SWEEP = {}
for acct in ACCTS:
    GAMMA_SWEEP[acct] = {}
    for gk, g in zip(GAMMA_KEYS, GAMMAS):
        others = [p for p in POLICIES if p != "DOC"]
        vmax = max(A_MAIN[acct][p]["V"][g] for p in others)
        GAMMA_SWEEP[acct][gk] = vmax / A_MAIN[acct]["DOC"]["V"][g]
CROSSING_49_50 = GAMMA_SWEEP["BATCHED"]["49/50"] >= LINE_11_10

# ---- V020-exclusion leg (reporting-only, C10)
check("v020-exclusion-row-name",
      ROWS[43]["name"] == "V020 Probe (audience separation)"
      and ROWS[43]["clicks"] == 3 and ROWS[43]["gated"])
ROWS43 = ROWS[:43]
XA, _xo = arm_a_world(ROWS43)
XB = arm_b_world(ROWS43)
TWIN_EXCL = cells_equal("v020excl", XA, XB, len(ROWS43))


def clause_booleans(world):
    cv = clause_values(world)
    b, p = cv["BATCHED"], cv["PER_ITEM"]
    return {
        "R1": b["gapMEAN"] >= Fraction(BANDS_R["R1_gapMEAN_BATCHED_min"]),
        "R2": b["ratioV"] >= Fraction(BANDS_R["R2_ratioV_BATCHED_99_100_min"]),
        "R3": b["TTF_DOC"]
        >= BANDS_R["R3_TTF_DOC_over_best_BATCHED_min_factor"] * b["TTF_best"],
        "A1": b["gapMEAN"] <= Fraction(BANDS_A["A1_gapMEAN_BATCHED_max"]),
        "A2": b["ratioV"]
        < Fraction(BANDS_A["A2_ratioV_BATCHED_99_100_strictly_below"]),
        "A3": b["TTF_DOC"]
        <= BANDS_A["A3_TTF_DOC_over_best_BATCHED_max_factor"] * b["TTF_best"],
        "A4": p["gapMEAN"] >= Fraction(BANDS_A["A4_gapMEAN_PER_ITEM_min"]),
        "A5": p["TTF_DOC"]
        >= BANDS_A["A5_TTF_DOC_over_best_PER_ITEM_min_factor"] * p["TTF_best"],
    }, cv


CLAUSES_MAIN_BOOL, _ = clause_booleans(A_MAIN)
CLAUSES_EXCL_BOOL, CV_EXCL = clause_booleans(XA)
EXCL_IDENTICAL = CLAUSES_MAIN_BOOL == CLAUSES_EXCL_BOOL

# ================================================================ Arm R
CONSTRUCTED_SEEDS = []


class CountingRNG(object):
    def __init__(self, seed):
        CONSTRUCTED_SEEDS.append(seed)
        self._r = random.Random(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return self._r.random()

    def shuffle(self, x):
        self._r.shuffle(x)


def draw_budget(rng):
    """One pmf uniform per sitting; strict Fraction(u) < cdf inversion in
    ascending budget order (3, 8, 21) via exact integer cross-multiply."""
    u = rng.random()
    num, den = u.as_integer_ratio()
    if 2 * num < den:          # Fraction(u) < 1/2
        return 3
    if 5 * num < 4 * den:      # Fraction(u) < 4/5
        return 8
    return 21


def flat_items(schedule, rows, layer_cost):
    out = []
    for it in schedule:
        if it[0] == "L":
            out.append((None, layer_cost))
        else:
            out.append((it[1], rows[it[1]]["clicks"]))
    return out


def arm_r_leg(seed, n_episodes):
    """Owner-sitting trace at the decision cell (BATCHED), all 5 policies.

    Chunked walk of the policy's own item list (C6). Reporting-only."""
    rng = CountingRNG(seed)
    total_sittings = 0
    mismatches = 0
    leg = {}
    T = ROLL["clicks_total"] + LAYER["BATCHED"]
    for pol in POLICIES:
        items = flat_items(A_ORDERS[pol], ROWS, LAYER["BATCHED"])
        n_items = len(items)
        curve = A_MAIN["BATCHED"][pol]["curve"]
        sum_first = 0
        sum_l1 = 0
        sum_l3 = 0
        sum_l10 = 0
        sum_sit = 0
        for _ep in range(n_episodes):
            ptr = 0
            rem = items[0][1]
            live = 0
            cum = 0
            sit = 0
            first_sit = 0
            l1 = l3 = l10 = -1
            done = False
            while not done:
                b = draw_budget(rng)
                sit += 1
                while b > 0:
                    take = b if b < rem else rem
                    rem -= take
                    b -= take
                    cum += take
                    if rem == 0:
                        if items[ptr][0] is not None:
                            live += 1
                            if first_sit == 0:
                                first_sit = sit
                        ptr += 1
                        if ptr == n_items:
                            done = True
                            break
                        rem = items[ptr][1]
                if sit == 1:
                    l1 = live
                elif sit == 3:
                    l3 = live
                elif sit == 10:
                    l10 = live
                if curve[cum if cum <= T else T] != live:
                    mismatches += 1
            if l1 < 0:
                l1 = live
            if l3 < 0:
                l3 = live
            if l10 < 0:
                l10 = live
            sum_first += first_sit
            sum_l1 += l1
            sum_l3 += l3
            sum_l10 += l10
            sum_sit += sit
        total_sittings += sum_sit
        leg[pol] = {
            "mean_sittings_to_first_live": Fraction(sum_first, n_episodes),
            "mean_live_after_1_sitting": Fraction(sum_l1, n_episodes),
            "mean_live_after_3_sittings": Fraction(sum_l3, n_episodes),
            "mean_live_after_10_sittings": Fraction(sum_l10, n_episodes),
            "mean_sittings_per_episode": Fraction(sum_sit, n_episodes),
        }
    return leg, total_sittings, rng.calls, mismatches


R_MAIN, R_MAIN_SIT, R_MAIN_DRAWS, R_MAIN_MISS = arm_r_leg(
    FX["arm_r"]["seed_main"], FX["arm_r"]["N_main"])
R_STAB, R_STAB_SIT, R_STAB_DRAWS, R_STAB_MISS = arm_r_leg(
    FX["arm_r"]["seed_stability"], FX["arm_r"]["N_stability"])

SENT_MAIN = check("F6-armR-main-draw-sentinel", R_MAIN_DRAWS == R_MAIN_SIT)
SENT_STAB = check("F6-armR-stability-draw-sentinel",
                  R_STAB_DRAWS == R_STAB_SIT)

# presentation shuffle (C9) — stdout row order of ONE listing only
prng = CountingRNG(FX["arm_r"]["seed_presentation"])
SHUFFLED_CELLS = ["%s|%s" % (acct, pol) for acct in ACCTS for pol in POLICIES]
prng.shuffle(SHUFFLED_CELLS)

AUX_OK = check("F6-aux-seed-20261388-never-read",
               FX["arm_r"]["seed_aux_reserved_never_read"]
               not in CONSTRUCTED_SEEDS)
SEED_ORDER_OK = check("F6-constructed-seeds-pinned-order",
                      CONSTRUCTED_SEEDS == [FX["arm_r"]["seed_main"],
                                            FX["arm_r"]["seed_stability"],
                                            FX["arm_r"]["seed_presentation"]])

# ---------------------------------------------------------------- ruling
GATES_F6_INPROC = (TWIN_MAIN and TWIN_HAND and TWIN_EXCL and SENT_MAIN
                   and SENT_STAB and AUX_OK and SEED_ORDER_OK)
GATES_OK = (GATE_F1 and GATE_F2 and GATE_F3 and GATE_F4 and GATE_F5
            and GATES_F6_INPROC)

TOKEN_1, CLAUSES, CV = evaluator_one(A_MAIN, GATES_OK)
TOKEN_2 = evaluator_two(B_MAIN, GATES_OK)
TWIN_TOKENS_AGREE = check("F6-twin-decision-tokens-agree",
                          TOKEN_1 == TOKEN_2)
RULING = TOKEN_1

# NULL axes report (reported regardless of where the rule order landed)
b_cv = CV["BATCHED"]
ttf_ratio_b = Fraction(b_cv["TTF_DOC"], b_cv["TTF_best"])
side_dec = CLAUSES["R2"]  # ratioV(99/100) >= 11/10 at the decision cell
NULL_AXES = {
    "order-insensitive": bool(CLAUSES["A1"] and CLAUSES["A2"]
                              and CLAUSES["A3"]
                              and not (CLAUSES["A4"] and CLAUSES["A5"])),
    "band-straddle": bool(Fraction(8) < b_cv["gapMEAN"] < Fraction(10)
                          or Fraction(2) < ttf_ratio_b < Fraction(3)),
    "gamma-conditional": bool(any(
        (GAMMA_SWEEP["BATCHED"][gk] >= LINE_11_10) != side_dec
        for gk in ("49/50", "199/200"))),
    "twin-arm-disagreement": bool(TOKEN_1 != TOKEN_2),
}

# ---------------------------------------------------------------- drafter cmp
D = FX["drafter_disclosed_never_gated"]


def close(x, target, tol):
    return abs(float(x) - target) <= tol


DRAFTER_CMP = {
    "BATCHED_MEAN_DOC_exact_match":
        A_MAIN["BATCHED"]["DOC"]["MEAN"] == Fraction(D["BATCHED_MEAN_DOC"]),
    "BATCHED_MEAN_best_exact_match":
        min(A_MAIN["BATCHED"][p]["MEAN"] for p in POLICIES if p != "DOC")
        == Fraction(D["BATCHED_MEAN_best"]),
    "BATCHED_best_policy_match":
        CV["BATCHED"]["best_MEAN_policy"] == D["BATCHED_best_policy"],
    "BATCHED_gapMEAN_exact_match":
        CV["BATCHED"]["gapMEAN"] == Fraction(D["BATCHED_gapMEAN"]),
    "V99_DOC_float_match": close(A_MAIN["BATCHED"]["DOC"]["V"][G_DEC],
                                 D["V_99_100_DOC_approx"], 1e-3),
    "V99_SPT_float_match": close(A_MAIN["BATCHED"]["SPT"]["V"][G_DEC],
                                 D["V_99_100_SPT_approx"], 1e-3),
    "ratioV_99_float_match": close(CV["BATCHED"]["ratioV"],
                                   D["ratioV_99_100_approx"], 1e-3),
    "TTF_pair_BATCHED_match":
        CV["BATCHED"]["TTF_DOC"] == D["TTF_DOC_BATCHED"]
        and CV["BATCHED"]["TTF_best"] == D["TTF_best_BATCHED"],
    "PER_ITEM_MEAN_DOC_exact_match":
        A_MAIN["PER_ITEM"]["DOC"]["MEAN"] == Fraction(D["PER_ITEM_MEAN_DOC"]),
    "PER_ITEM_MEAN_best_exact_match":
        min(A_MAIN["PER_ITEM"][p]["MEAN"] for p in POLICIES if p != "DOC")
        == Fraction(D["PER_ITEM_MEAN_best"]),
    "PER_ITEM_best_policy_match":
        CV["PER_ITEM"]["best_MEAN_policy"] == D["PER_ITEM_best_policy"],
    "PER_ITEM_gapMEAN_exact_match":
        CV["PER_ITEM"]["gapMEAN"] == Fraction(D["PER_ITEM_gapMEAN"]),
    "TTF_pair_PER_ITEM_match":
        CV["PER_ITEM"]["TTF_DOC"] == D["TTF_DOC_PER_ITEM"]
        and CV["PER_ITEM"]["TTF_best"] == D["TTF_best_PER_ITEM"],
    "ratioV_49_50_float_match": close(GAMMA_SWEEP["BATCHED"]["49/50"],
                                      D["ratioV_49_50_approx"], 1e-3),
    "LPT_anchor_exact_match":
        LPT_ANCHOR == Fraction(D["LPT_anchor_MEAN_BATCHED"]),
    "batch_door_DOC_mean_price_18_exact":
        BATCH_DOOR["DOC"]["mean_price"]
        == Fraction(D["batch_door_mean_price_DOC"]),
    "batch_door_DOC_ttf_factor_approx_3_6":
        close(BATCH_DOOR["DOC"]["ttf_factor"],
              D["batch_door_TTF_factor_DOC_approx"], 0.1),
    "residual_sort_gain_approx_6_5":
        close(CV["BATCHED"]["gapMEAN"], D["residual_sort_gain_approx"], 0.1),
    "v020_exclusion_identical_match": EXCL_IDENTICAL,
    "expected_landing_match": RULING == D["expected_landing"].split()[0],
}

# ---------------------------------------------------------------- results.json


def vdict(m):
    return {gk: {"pq": fstr(m["V"][g]), "float": float(m["V"][g])}
            for gk, g in zip(GAMMA_KEYS, GAMMAS)}


def cell_json(m):
    return {
        "clocks_doc_index_order": [m["clocks"][i]
                                   for i in sorted(m["clocks"])],
        "TTF": m["TTF"], "T22": m["T22"],
        "MEAN": fstr(m["MEAN"]), "MEAN_float": float(m["MEAN"]),
        "V": vdict(m),
        "live_curve": " ".join(str(x) for x in m["curve"]),
        "final_clock": m["t_end"],
    }


def leg_json(leg, sittings, draws, mism):
    out = {"total_sittings": sittings, "uniform_draws": draws,
           "trace_vs_exact_curve_mismatches": mism}
    for pol in POLICIES:
        out[pol] = {k: {"pq": fstr(v), "float": float(v)}
                    for k, v in sorted(leg[pol].items())}
    return out


RESULTS = {
    "verdict": {
        "token": RULING,
        "twin_tokens": [TOKEN_1, TOKEN_2],
        "rule_order": FX["decision_rule_registered_order"],
        "clauses": {k: bool(v) for k, v in sorted(CLAUSES.items())},
        "null_axes_report": NULL_AXES,
    },
    "decision_inputs": {
        acct: {
            "gapMEAN": fstr(CV[acct]["gapMEAN"]),
            "gapMEAN_float": float(CV[acct]["gapMEAN"]),
            "best_MEAN_policy": CV[acct]["best_MEAN_policy"],
            "ratioV_99_100": fstr(CV[acct]["ratioV"]),
            "ratioV_99_100_float": float(CV[acct]["ratioV"]),
            "best_V_policy": CV[acct]["best_V_policy"],
            "TTF_DOC": CV[acct]["TTF_DOC"],
            "TTF_best": CV[acct]["TTF_best"],
            "best_TTF_policy": CV[acct]["best_TTF_policy"],
        } for acct in ACCTS
    },
    "table": {acct: {pol: cell_json(A_MAIN[acct][pol]) for pol in POLICIES}
              for acct in ACCTS},
    "gates": {"F1_data_identity": GATE_F1, "F2_conservation": GATE_F2,
              "F3_sequencing_theorems": GATE_F3, "F4_hand_world": GATE_F4,
              "F5_gamma_monotonicity": GATE_F5,
              "F6_battery_in_process": bool(GATES_F6_INPROC
                                            and TWIN_TOKENS_AGREE)},
    "hand_world": {pol: {"clocks": sorted(HA["BATCHED"][pol]["clocks"]
                                          .values()),
                         "MEAN": fstr(HA["BATCHED"][pol]["MEAN"]),
                         "TTF": HA["BATCHED"][pol]["TTF"]}
                   for pol in POLICIES},
    "reporting": {
        "batch_door_same_order": {
            pol: {"mean_price": fstr(BATCH_DOOR[pol]["mean_price"]),
                  "mean_price_float": float(BATCH_DOOR[pol]["mean_price"]),
                  "ttf_factor": fstr(BATCH_DOOR[pol]["ttf_factor"]),
                  "ttf_factor_float": float(BATCH_DOOR[pol]["ttf_factor"])}
            for pol in POLICIES},
        "LPT_anchor_MEAN_BATCHED": {"pq": fstr(LPT_ANCHOR),
                                    "float": float(LPT_ANCHOR)},
        "gamma_sweep_ratioV": {
            acct: {gk: {"pq": fstr(GAMMA_SWEEP[acct][gk]),
                        "float": float(GAMMA_SWEEP[acct][gk])}
                   for gk in GAMMA_KEYS} for acct in ACCTS},
        "gamma_49_50_crossing_BATCHED_ge_11_10": bool(CROSSING_49_50),
        "v020_exclusion": {
            "clauses_main": {k: bool(v)
                             for k, v in sorted(CLAUSES_MAIN_BOOL.items())},
            "clauses_excluded": {k: bool(v)
                                 for k, v in
                                 sorted(CLAUSES_EXCL_BOOL.items())},
            "identical": bool(EXCL_IDENTICAL),
            "excluded_world": {
                acct: {"gapMEAN": fstr(CV_EXCL[acct]["gapMEAN"]),
                       "gapMEAN_float": float(CV_EXCL[acct]["gapMEAN"]),
                       "ratioV_99_100_float": float(CV_EXCL[acct]["ratioV"]),
                       "TTF_DOC": CV_EXCL[acct]["TTF_DOC"],
                       "TTF_best": CV_EXCL[acct]["TTF_best"]}
                for acct in ACCTS},
        },
        "arm_R": {"main": leg_json(R_MAIN, R_MAIN_SIT, R_MAIN_DRAWS,
                                   R_MAIN_MISS),
                  "stability": leg_json(R_STAB, R_STAB_SIT, R_STAB_DRAWS,
                                        R_STAB_MISS)},
    },
    "drafter_comparison_never_gated": {k: bool(v) for k, v in
                                       sorted(DRAFTER_CMP.items())},
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8",
          newline="\n") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")

# ---------------------------------------------------------------- stdout
print("VERDICT 073 — owner-queue attention order (INTAKE 062)")
print("RULING: %s (twin tokens: %s / %s)" % (RULING, TOKEN_1, TOKEN_2))
print("clauses: R1:%s R2:%s R3:%s | A1:%s A2:%s A3:%s A4:%s A5:%s"
      % tuple(CLAUSES[k] for k in ("R1", "R2", "R3", "A1", "A2", "A3",
                                   "A4", "A5")))
bb, pp = CV["BATCHED"], CV["PER_ITEM"]
print("BATCHED: MEAN(DOC) = %s ~ %s | best %s = %s ~ %s | gapMEAN = %s ~ %s"
      % (fstr(A_MAIN["BATCHED"]["DOC"]["MEAN"]),
         ffl(A_MAIN["BATCHED"]["DOC"]["MEAN"]), bb["best_MEAN_policy"],
         fstr(A_MAIN["BATCHED"][bb["best_MEAN_policy"]]["MEAN"]),
         ffl(A_MAIN["BATCHED"][bb["best_MEAN_policy"]]["MEAN"]),
         fstr(bb["gapMEAN"]), ffl(bb["gapMEAN"])))
print("BATCHED: ratioV(99/100) = %s ~ %s (best V: %s) | TTF DOC %d vs best"
      " %d (%s)"
      % (fstr(bb["ratioV"]), ffl(bb["ratioV"]), bb["best_V_policy"],
         bb["TTF_DOC"], bb["TTF_best"], bb["best_TTF_policy"]))
print("PER-ITEM: MEAN(DOC) = %s ~ %s | best %s = %s ~ %s | gapMEAN = %s ~ %s"
      " | TTF DOC %d vs best %d (%s)"
      % (fstr(A_MAIN["PER_ITEM"]["DOC"]["MEAN"]),
         ffl(A_MAIN["PER_ITEM"]["DOC"]["MEAN"]), pp["best_MEAN_policy"],
         fstr(A_MAIN["PER_ITEM"][pp["best_MEAN_policy"]]["MEAN"]),
         ffl(A_MAIN["PER_ITEM"][pp["best_MEAN_policy"]]["MEAN"]),
         fstr(pp["gapMEAN"]), ffl(pp["gapMEAN"]), pp["TTF_DOC"],
         pp["TTF_best"], pp["best_TTF_policy"]))
print("V(99/100, BATCHED): " + " | ".join(
    "%s %s" % (pol, ffl(A_MAIN["BATCHED"][pol]["V"][G_DEC]))
    for pol in POLICIES))
print("T22 (BATCHED): " + " | ".join(
    "%s %d" % (pol, A_MAIN["BATCHED"][pol]["T22"]) for pol in POLICIES)
    + " || T22 (PER-ITEM): " + " | ".join(
    "%s %d" % (pol, A_MAIN["PER_ITEM"][pol]["T22"]) for pol in POLICIES))
print("batch door (same order, PER-ITEM minus BATCHED): " + " | ".join(
    "%s +%s mean, TTF x%s" % (pol, fstr(BATCH_DOOR[pol]["mean_price"]),
                              ffl(BATCH_DOOR[pol]["ttf_factor"]))
    for pol in POLICIES))
print("LPT anchor: MEAN(LPT, BATCHED) = %s ~ %s"
      % (fstr(LPT_ANCHOR), ffl(LPT_ANCHOR)))
print("gamma sweep ratioV BATCHED: " + " | ".join(
    "%s = %s" % (gk, ffl(GAMMA_SWEEP["BATCHED"][gk])) for gk in GAMMA_KEYS)
    + " || 49/50 crossing >= 11/10: %s (REPORTING only)" % CROSSING_49_50)
print("V020-exclusion leg: clauses identical: %s | excluded gapMEAN B = %s"
      " ~ %s, PI = %s ~ %s"
      % (EXCL_IDENTICAL, fstr(CV_EXCL["BATCHED"]["gapMEAN"]),
         ffl(CV_EXCL["BATCHED"]["gapMEAN"]),
         fstr(CV_EXCL["PER_ITEM"]["gapMEAN"]),
         ffl(CV_EXCL["PER_ITEM"]["gapMEAN"])))
print("theorems: exchange 43 swaps weakly worsen (both accountings): %s |"
      " pointwise dominance: %s | V(SPT) > V(LPT) all gamma both"
      " accountings: %s"
      % (F3_FLAGS["exchange"], F3_FLAGS["dominance"], F3_FLAGS["anchor"]))
print("F4 hand world: DOC %s MEAN %s | SPT %s MEAN %s | LAZY-SPT %s MEAN %s"
      % (sorted(HA["BATCHED"]["DOC"]["clocks"].values()),
         fstr(HA["BATCHED"]["DOC"]["MEAN"]),
         sorted(HA["BATCHED"]["SPT"]["clocks"].values()),
         fstr(HA["BATCHED"]["SPT"]["MEAN"]),
         sorted(HA["BATCHED"]["LAZY-SPT"]["clocks"].values()),
         fstr(HA["BATCHED"]["LAZY-SPT"]["MEAN"])))
print("arm-R main (reporting-only, seed %d, N=%d/policy): "
      % (FX["arm_r"]["seed_main"], FX["arm_r"]["N_main"]) + " | ".join(
      "%s first-live %s, after 1/3/10 sittings %s/%s/%s" % (
          pol, ffl(R_MAIN[pol]["mean_sittings_to_first_live"]),
          ffl(R_MAIN[pol]["mean_live_after_1_sitting"]),
          ffl(R_MAIN[pol]["mean_live_after_3_sittings"]),
          ffl(R_MAIN[pol]["mean_live_after_10_sittings"]))
      for pol in POLICIES))
print("arm-R draws: main %d (= sittings %d), curve mismatches %d |"
      " stability %d (= sittings %d), mismatches %d"
      % (R_MAIN_DRAWS, R_MAIN_SIT, R_MAIN_MISS, R_STAB_DRAWS, R_STAB_SIT,
         R_STAB_MISS))
print("null axes (report): %s"
      % json.dumps(NULL_AXES, sort_keys=True))
print("presentation-shuffled cell order (seed %d): %s"
      % (FX["arm_r"]["seed_presentation"], " ".join(SHUFFLED_CELLS)))
print("drafter comparison (never gated): %s"
      % json.dumps(DRAFTER_CMP, sort_keys=True))
print("SELF-CHECKS: %d passed, %d failed"
      % (CHECKS["passed"], CHECKS["failed"]))
if CHECKS["failed"]:
    sys.exit(1)
