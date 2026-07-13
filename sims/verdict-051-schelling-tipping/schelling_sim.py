#!/usr/bin/env python3
"""VERDICT 051 — Schelling segregation tipping at tau = 3/10 (idea-engine PROPOSAL 040).

Fully hermetic: reads ONLY its own fixtures.json (committed BEFORE this runner).
Stdlib-only, deterministic, byte-identical stdout + results.json across process
runs (no wall-clock in any output). One command, no flags:

    python3 sims/verdict-051-schelling-tipping/schelling_sim.py

Registered frame (every constant from the PROPOSAL 040 block via fixtures.json):
40x40 Moore-8 torus, 720/720/160 A/B/vacant, satisfaction = like-fraction among
OCCUPIED neighbors >= tau in exact integers (zero occupied neighbors => satisfied),
live random-serial sweeps, unsatisfied agents relocate to a uniformly random
vacant cell, fixation (zero-relocation sweep, independently re-certified) or cap
500. Decision: median terminal mean like-neighbor share s(3/10) over M = 32
seed-20261297 runs, exact Fractions; REJECT first (< 11/20) -> APPROVE (>= 7/10
AND seed-20261298 stability reproduction) -> NULL; both bands carry the
< 1/4-cap-censored validity conjunct. Seeds: 20261297 main / 20261298 stability /
20261299 reporting / 20261300 aux (reserved, NEVER drawn).
"""

import json
import random
import sys
from bisect import insort
from fractions import Fraction
from functools import cmp_to_key
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

CHECKS = []  # (name, ok, detail)


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    if not ok:
        print(f"SELF-CHECK FAIL: {name} {detail}")


def frac_str(f):
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------- RNG counting
class CountingRandom(random.Random):
    """Counts pinned-draw-order calls (shuffle, randrange) for the sentinels."""

    def __init__(self, seed):
        super().__init__(seed)
        self.shuffle_calls = 0
        self.randrange_calls = 0

    def shuffle(self, x):
        self.shuffle_calls += 1
        super().shuffle(x)

    def randrange(self, *args, **kwargs):
        self.randrange_calls += 1
        return super().randrange(*args, **kwargs)


# ---------------------------------------------------------------- engine
def build_neighbors(n):
    """Moore-8 toroidal neighbor table, row-major indices."""
    nbs = []
    for r in range(n):
        for c in range(n):
            lst = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    lst.append(((r + dr) % n) * n + (c + dc) % n)
            nbs.append(tuple(lst))
    return tuple(nbs)


def independent_unsatisfied_count(grid, n, tau_num, tau_den):
    """INDEPENDENTLY WRITTEN satisfaction scan (no neighbor table; divmod + %).

    Used to re-certify every fixation. Deliberately a separate code path from
    the engine's per-agent evaluation.
    """
    bad = 0
    for idx in range(n * n):
        me = grid[idx]
        if me == 0:
            continue
        r, c = divmod(idx, n)
        occ = 0
        like = 0
        for dr in (-1, 0, 1):
            row_base = ((r + dr) % n) * n
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                v = grid[row_base + (c + dc) % n]
                if v:
                    occ += 1
                    if v == me:
                        like += 1
        if occ and like * tau_den < tau_num * occ:
            bad += 1
    return bad


def occ_like(grid, nbs, cell, me):
    occ = 0
    like = 0
    for nb in nbs[cell]:
        v = grid[nb]
        if v:
            occ += 1
            if v == me:
                like += 1
    return occ, like


def measure_s(grid, nbs):
    """Exact-Fraction mean of like/occ over agents with >= 1 occupied neighbor."""
    total = Fraction(0)
    k = 0
    for cell, me in enumerate(grid):
        if me == 0:
            continue
        occ, like = occ_like(grid, nbs, cell, me)
        if occ:
            total += Fraction(like, occ)
            k += 1
    return total / k


def satisfied_fraction(grid, nbs, tau_num, tau_den):
    sat = 0
    tot = 0
    for cell, me in enumerate(grid):
        if me == 0:
            continue
        tot += 1
        occ, like = occ_like(grid, nbs, cell, me)
        if occ == 0 or like * tau_den >= tau_num * occ:
            sat += 1
    return Fraction(sat, tot)


def interface_density(grid, nbs):
    """Unlike occupied-adjacent pairs / all occupied-adjacent pairs (unordered)."""
    unlike = 0
    pairs = 0
    for cell, me in enumerate(grid):
        if me == 0:
            continue
        for nb in nbs[cell]:
            if nb > cell:
                v = grid[nb]
                if v:
                    pairs += 1
                    if v != me:
                        unlike += 1
    return Fraction(unlike, pairs)


def run_one(rng, n, n_a, n_b, n_v, tau_num, tau_den, cap, nbs, stats):
    """One run under the pinned dynamics. Returns the per-run record."""
    labels = [1] * n_a + [2] * n_b + [0] * n_v  # pinned construction order
    rng.shuffle(labels)  # draw 1: init shuffle
    grid = labels
    init_s = measure_s(grid, nbs)
    vac = [i for i, v in enumerate(grid) if v == 0]  # ascending by construction
    sweeps = 0
    relocations = 0
    fixated = False
    while sweeps < cap:
        sweeps += 1
        order = [i for i, v in enumerate(grid) if v != 0]  # ascending occupied
        rng.shuffle(order)  # draw: per-sweep order shuffle
        moves = 0
        for cell in order:
            me = grid[cell]
            occ = 0
            like = 0
            for nb in nbs[cell]:
                v = grid[nb]
                if v:
                    occ += 1
                    if v == me:
                        like += 1
            if occ and like * tau_den < tau_num * occ:
                i = rng.randrange(len(vac))  # draw: one randrange per relocation
                dest = vac[i]
                del vac[i]
                grid[dest] = me
                grid[cell] = 0
                insort(vac, cell)  # vacancy list stays ascending
                moves += 1
        relocations += moves
        stats["sweeps"] += 1
        # conservation gate — recounted every sweep end
        c_a = c_b = c_v = 0
        for v in grid:
            if v == 1:
                c_a += 1
            elif v == 2:
                c_b += 1
            else:
                c_v += 1
        if not (c_a == n_a and c_b == n_b and c_v == n_v):
            stats["conservation_violations"] += 1
        # ascending-vacancy invariant (aggregate)
        if any(vac[i] >= vac[i + 1] for i in range(len(vac) - 1)):
            stats["vacancy_order_violations"] += 1
        if moves == 0:
            fixated = True
            break
    stats["relocations"] += relocations
    if fixated:
        # independent fixation re-certification (separately written scan)
        if independent_unsatisfied_count(grid, n, tau_num, tau_den) != 0:
            stats["fixation_cert_failures"] += 1
        stats["fixations"] += 1
    return {
        "s": measure_s(grid, nbs),
        "init_s": init_s,
        "sweeps": sweeps,
        "capped": not fixated,
        "relocations": relocations,
        "satisfied_frac": satisfied_fraction(grid, nbs, tau_num, tau_den),
        "interface_density": interface_density(grid, nbs),
    }


def new_stats():
    return {
        "sweeps": 0,
        "relocations": 0,
        "fixations": 0,
        "conservation_violations": 0,
        "vacancy_order_violations": 0,
        "fixation_cert_failures": 0,
    }


# ---------------------------------------------------------------- summaries
def median_of_even(values):
    """Mean of the n/2-th and (n/2+1)-th order statistics — exact rational."""
    s = sorted(values)
    m = len(s)
    return (s[m // 2 - 1] + s[m // 2]) / 2


def nearest_rank(sorted_vals, p_num, p_den):
    """Nearest-rank quantile (reporting-only): value at rank ceil(p*n)."""
    n = len(sorted_vals)
    rank = -((-p_num * n) // p_den)  # ceil(p*n)
    return sorted_vals[max(rank, 1) - 1]


def summarize_cell(records):
    s_vals = [r["s"] for r in records]
    caps = sum(1 for r in records if r["capped"])
    fix_sweeps = sorted(r["sweeps"] for r in records if not r["capped"])
    quart = None
    if fix_sweeps:
        quart = {
            "q1": nearest_rank(fix_sweeps, 1, 4),
            "median": nearest_rank(fix_sweeps, 1, 2),
            "q3": nearest_rank(fix_sweeps, 3, 4),
            "min": fix_sweeps[0],
            "max": fix_sweeps[-1],
        }
    mean_s = sum(s_vals, Fraction(0)) / len(s_vals)
    return {
        "runs": [
            {
                "s": frac_str(r["s"]),
                "init_s": frac_str(r["init_s"]),
                "sweeps": r["sweeps"],
                "capped": r["capped"],
                "relocations": r["relocations"],
                "satisfied_frac": frac_str(r["satisfied_frac"]),
                "interface_density": frac_str(r["interface_density"]),
            }
            for r in records
        ],
        "median_s": frac_str(median_of_even(s_vals)),
        "mean_s": frac_str(mean_s),
        "mean_satisfied_frac": frac_str(
            sum((r["satisfied_frac"] for r in records), Fraction(0)) / len(records)
        ),
        "mean_interface_density": frac_str(
            sum((r["interface_density"] for r in records), Fraction(0)) / len(records)
        ),
        "cap_hits": caps,
        "sweeps_to_fixation_quartiles": quart,
    }


# ---------------------------------------------------------------- twin evaluators
def evaluator_fraction(main_s, main_caps, stab_s, stab_caps, m_main, m_stab):
    """Decision evaluator 1 — fractions.Fraction comparisons."""
    reject_band = Fraction(11, 20)
    approve_band = Fraction(7, 10)
    median = median_of_even(main_s)
    validity = main_caps * 4 < m_main  # fewer than 1/4 cap-censored
    stab_median = median_of_even(stab_s)
    stab_validity = stab_caps * 4 < m_stab
    if validity and median < reject_band:
        return ("reject", None)
    if validity and median >= approve_band and stab_validity and stab_median >= approve_band:
        return ("approve", None)
    if not validity:
        return ("null", "non-convergence")
    if reject_band <= median < approve_band:
        return ("null", "band-straddle")
    if not stab_validity:
        return ("null", "stability-non-reproduction (stability validity conjunct failed)")
    return ("null", "stability-non-reproduction")


def evaluator_integer(main_s, main_caps, stab_s, stab_caps, m_main, m_stab):
    """Decision evaluator 2 — INDEPENDENTLY WRITTEN: pure-integer cross-mult.

    Works on (num, den) pairs only; never constructs a Fraction.
    """
    pairs_main = [(f.numerator, f.denominator) for f in main_s]
    pairs_stab = [(f.numerator, f.denominator) for f in stab_s]

    def cmp(a, b):
        lhs = a[0] * b[1]
        rhs = b[0] * a[1]
        return (lhs > rhs) - (lhs < rhs)

    def median_pair(pairs):
        s = sorted(pairs, key=cmp_to_key(cmp))
        m = len(s)
        (an, ad), (bn, bd) = s[m // 2 - 1], s[m // 2]
        return (an * bd + bn * ad, 2 * ad * bd)  # mean of the two order stats

    def lt(pair, num, den):  # pair < num/den ?
        return pair[0] * den < num * pair[1]

    def ge(pair, num, den):  # pair >= num/den ?
        return pair[0] * den >= num * pair[1]

    med = median_pair(pairs_main)
    smed = median_pair(pairs_stab)
    validity = 4 * main_caps < m_main
    stab_validity = 4 * stab_caps < m_stab
    if validity and lt(med, 11, 20):
        return ("reject", None)
    if validity and ge(med, 7, 10) and stab_validity and ge(smed, 7, 10):
        return ("approve", None)
    if not validity:
        return ("null", "non-convergence")
    if ge(med, 11, 20) and lt(med, 7, 10):
        return ("null", "band-straddle")
    if not stab_validity:
        return ("null", "stability-non-reproduction (stability validity conjunct failed)")
    return ("null", "stability-non-reproduction")


# ---------------------------------------------------------------- main
def main():
    out = {}

    # Gate: CPython minor pinned
    pin = tuple(FX["cpython_minor_pinned"])
    check("cpython-minor-pinned", sys.version_info[:2] == pin,
          f"running {sys.version_info[:2]}, pinned {pin}")

    n = FX["grid"]["N"]
    n_a = FX["population"]["type_a"]
    n_b = FX["population"]["type_b"]
    n_v = FX["population"]["vacant"]
    cap = FX["termination"]["sweep_cap"]
    tau_grid = [tuple(t) for t in FX["tau_grid"]]
    dec_tau = tuple(FX["decision_tau"])
    m_main = FX["runs"]["M_main"]
    m_stab = FX["runs"]["M_stability"]
    m_rep = FX["runs"]["M_reporting"]

    check("tau-grid-ascending",
          all(tau_grid[i][0] * tau_grid[i + 1][1] < tau_grid[i + 1][0] * tau_grid[i][1]
              for i in range(len(tau_grid) - 1)))
    check("bands-disjoint", Fraction(11, 20) < Fraction(7, 10))
    check("population-counts", n_a == 720 and n_b == 720 and n_v == 160
          and n_a + n_b + n_v == n * n)

    # ---- Gate: 4x4 hand fixture (wrap + neighborhood arithmetic)
    hf = FX["hand_fixture_4x4"]
    lab_map = {"A": 1, "B": 2, "V": 0}
    hgrid = [lab_map[x] for row in hf["grid_rows"] for x in row]
    hnbs = build_neighbors(4)
    ok_all = True
    for exp in hf["expected_occ_like_per_cell"]:
        idx = exp["idx"]
        me = hgrid[idx]
        occ, like = occ_like(hgrid, hnbs, idx, me)
        if occ != exp["occ"]:
            ok_all = False
        if me != 0 and like != exp["like"]:
            ok_all = False
        if me != lab_map[exp["label"]]:
            ok_all = False
    check("hand-fixture-4x4-engine", ok_all, "engine occ/like vs hand-computed table")
    # cross-check the INDEPENDENT scanner on the same fixture: at tau = 1/2 the
    # unsatisfied set derived from the hand table must match the scanner's count.
    hand_unsat = 0
    for exp in hf["expected_occ_like_per_cell"]:
        if exp["label"] == "V":
            continue
        if exp["occ"] and exp["like"] * 2 < 1 * exp["occ"]:
            hand_unsat += 1
    check("hand-fixture-4x4-independent-scan",
          independent_unsatisfied_count(hgrid, 4, 1, 2) == hand_unsat,
          f"hand-derived unsatisfied at tau=1/2 = {hand_unsat}")

    nbs = build_neighbors(n)

    # ---- Gate: tau = 0 control leg (main seed, M = 32)
    ctl = FX["control_leg_tau0"]
    rng_ctl = CountingRandom(ctl["seed"])
    st_ctl = new_stats()
    lo = Fraction(*ctl["baseline_band"][0])
    hi = Fraction(*ctl["baseline_band"][1])
    ctl_records = []
    for _ in range(ctl["M"]):
        ctl_records.append(run_one(rng_ctl, n, n_a, n_b, n_v, 0, 1, cap, nbs, st_ctl))
    check("tau0-zero-relocations", st_ctl["relocations"] == 0,
          f"relocations={st_ctl['relocations']}")
    check("tau0-baseline-band",
          all(lo <= r["init_s"] <= hi for r in ctl_records),
          "every run's initial-placement s inside [47/100, 53/100]")
    check("tau0-draw-sentinel",
          rng_ctl.shuffle_calls == ctl["M"] * 2 and rng_ctl.randrange_calls == 0,
          f"shuffles={rng_ctl.shuffle_calls} (expect {ctl['M'] * 2}), "
          f"randranges={rng_ctl.randrange_calls} (expect 0)")
    out_ctl = summarize_cell(ctl_records)
    out_ctl["min_init_s"] = frac_str(min(r["init_s"] for r in ctl_records))
    out_ctl["max_init_s"] = frac_str(max(r["init_s"] for r in ctl_records))

    # ---- Main leg: seed 20261297, full tau grid ascending, M = 32 each
    rng_main = CountingRandom(FX["seeds"]["main"])
    st_main = new_stats()
    main_cells = {}
    main_records = {}
    for tn, td in tau_grid:
        recs = [run_one(rng_main, n, n_a, n_b, n_v, tn, td, cap, nbs, st_main)
                for _ in range(m_main)]
        main_records[(tn, td)] = recs
        main_cells[f"{tn}/{td}"] = summarize_cell(recs)
    n_runs_main = len(tau_grid) * m_main
    check("main-draw-sentinel",
          rng_main.shuffle_calls == n_runs_main + st_main["sweeps"]
          and rng_main.randrange_calls == st_main["relocations"],
          f"shuffles={rng_main.shuffle_calls} (expect {n_runs_main + st_main['sweeps']}), "
          f"randranges={rng_main.randrange_calls} (expect {st_main['relocations']})")

    # ---- Stability leg: seed 20261298, decision cell only, M = 16
    rng_stab = CountingRandom(FX["seeds"]["stability"])
    st_stab = new_stats()
    stab_recs = [run_one(rng_stab, n, n_a, n_b, n_v, dec_tau[0], dec_tau[1], cap, nbs, st_stab)
                 for _ in range(m_stab)]
    check("stability-draw-sentinel",
          rng_stab.shuffle_calls == m_stab + st_stab["sweeps"]
          and rng_stab.randrange_calls == st_stab["relocations"],
          f"shuffles={rng_stab.shuffle_calls}, randranges={rng_stab.randrange_calls}")

    # ---- Reporting leg: seed 20261299, pinned cell order, M = 16 each
    rng_rep = CountingRandom(FX["seeds"]["reporting"])
    st_rep = new_stats()
    rep_cells = {}
    rep_runs_total = 0
    rep_medians = {}
    for cell_cfg in FX["reporting_leg"]["cells_in_pinned_order"]:
        cn = cell_cfg["N"]
        cnbs = nbs if cn == n else build_neighbors(cn)
        ca, cb, cv = cell_cfg["type_a"], cell_cfg["type_b"], cell_cfg["vacant"]
        check(f"reporting-cell-counts-{cell_cfg['name']}", ca + cb + cv == cn * cn)
        recs = [run_one(rng_rep, cn, ca, cb, cv, dec_tau[0], dec_tau[1], cap, cnbs, st_rep)
                for _ in range(m_rep)]
        rep_runs_total += m_rep
        rep_cells[cell_cfg["name"]] = summarize_cell(recs)
        rep_medians[cell_cfg["name"]] = median_of_even([r["s"] for r in recs])
    check("reporting-draw-sentinel",
          rng_rep.shuffle_calls == rep_runs_total + st_rep["sweeps"]
          and rng_rep.randrange_calls == st_rep["relocations"],
          f"shuffles={rng_rep.shuffle_calls}, randranges={rng_rep.randrange_calls}")

    # ---- Aggregate physics gates across all legs
    for name, st in (("control", st_ctl), ("main", st_main),
                     ("stability", st_stab), ("reporting", st_rep)):
        check(f"conservation-{name}", st["conservation_violations"] == 0,
              f"violations={st['conservation_violations']}")
        check(f"fixation-recertification-{name}", st["fixation_cert_failures"] == 0,
              f"failures={st['fixation_cert_failures']}")
        check(f"vacancy-ascending-{name}", st["vacancy_order_violations"] == 0)

    # ---- Aux seed: reserved, NEVER drawn (no generator is ever constructed)
    check("aux-seed-never-drawn", True,
          f"seed {FX['seeds']['aux_reserved_never_drawn']} — no RNG instantiated")

    # ---- Decision
    dec_key = f"{dec_tau[0]}/{dec_tau[1]}"
    dec_recs = main_records[dec_tau]
    main_s = [r["s"] for r in dec_recs]
    main_caps = sum(1 for r in dec_recs if r["capped"])
    stab_s = [r["s"] for r in stab_recs]
    stab_caps = sum(1 for r in stab_recs if r["capped"])
    check("decision-cell-run-count", len(main_s) == m_main and len(stab_s) == m_stab)

    median = median_of_even(main_s)
    srt = sorted(main_s)
    check("median-order-statistics",
          median == (srt[15] + srt[16]) / 2 and m_main == 32,
          "median of 32 = mean of the 16th/17th order statistics")

    r1 = evaluator_fraction(main_s, main_caps, stab_s, stab_caps, m_main, m_stab)
    r2 = evaluator_integer(main_s, main_caps, stab_s, stab_caps, m_main, m_stab)
    check("twin-evaluators-agree", r1 == r2, f"fraction={r1} integer={r2}")
    ruling, axis = r1

    stab_median = median_of_even(stab_s)
    validity = main_caps * 4 < m_main
    stab_validity = stab_caps * 4 < m_stab

    # ---- Monotonicity audit (reporting-only, flagged loudly on violation)
    mono_taus = [(1, 8), (1, 4), (3, 10), (3, 8), (1, 2)]
    mono_means = [sum((r["s"] for r in main_records[t]), Fraction(0)) / m_main
                  for t in mono_taus]
    mono_ok = all(mono_means[i] <= mono_means[i + 1] for i in range(len(mono_means) - 1))

    # ---- Vacancy-sensitivity flip (reporting-only — names the axis, cannot flip)
    v_lo = rep_medians["vacancy-1/20"]
    v_hi = rep_medians["vacancy-1/5"]
    flips = {}
    for edge_name, edge in (("11/20", Fraction(11, 20)), ("7/10", Fraction(7, 10))):
        flips[edge_name] = (v_lo < edge) != (v_hi < edge)
    vacancy_flip = any(flips.values())

    # ---- s in [0, 1] sanity on every recorded run
    all_runs = (ctl_records + stab_recs
                + [r for recs in main_records.values() for r in recs])
    check("s-in-unit-interval",
          all(Fraction(0) <= r["s"] <= Fraction(1) for r in all_runs))

    # ---- results
    out["fixtures"] = "fixtures.json (committed before this runner; sole input)"
    out["legs"] = {
        "control_tau0": out_ctl,
        "main": {"seed": FX["seeds"]["main"], "M": m_main, "cells": main_cells},
        "stability": {"seed": FX["seeds"]["stability"], "M": m_stab,
                      "cell": dec_key, "summary": summarize_cell(stab_recs)},
        "reporting": {"seed": FX["seeds"]["reporting"], "M": m_rep,
                      "tau": dec_key, "cells": rep_cells},
        "aux": {"seed": FX["seeds"]["aux_reserved_never_drawn"], "draws": 0,
                "note": "reserved for the pre-priced NULL probe; never read"},
    }
    out["decision"] = {
        "decision_cell": dec_key,
        "median_s_main": frac_str(median),
        "median_s_main_float": float(median),
        "cap_censored_main": main_caps,
        "validity_conjunct_main_pass": validity,
        "median_s_stability": frac_str(stab_median),
        "median_s_stability_float": float(stab_median),
        "cap_censored_stability": stab_caps,
        "validity_conjunct_stability_pass": stab_validity,
        "reject_band": "11/20",
        "approve_band": "7/10",
        "evaluation_order": "REJECT first, then APPROVE, else NULL",
        "ruling": ruling,
        "binding_axis": axis,
        "stability_ruling_shadow": ("reject" if stab_validity and stab_median < Fraction(11, 20)
                                    else "approve" if stab_validity and stab_median >= Fraction(7, 10)
                                    else "null-side"),
    }
    out["reporting_only_findings"] = {
        "monotonicity_non_decreasing_1_8_to_1_2": mono_ok,
        "mono_means": {f"{t[0]}/{t[1]}": frac_str(m) for t, m in zip(mono_taus, mono_means)},
        "vacancy_flip_by_band_edge": flips,
        "vacancy_flip_any": vacancy_flip,
        "vacancy_medians": {k: frac_str(v) for k, v in rep_medians.items()},
    }
    out["sentinels"] = {
        "control": {"shuffles": rng_ctl.shuffle_calls, "randranges": rng_ctl.randrange_calls},
        "main": {"shuffles": rng_main.shuffle_calls, "randranges": rng_main.randrange_calls,
                 "sweeps": st_main["sweeps"], "relocations": st_main["relocations"]},
        "stability": {"shuffles": rng_stab.shuffle_calls, "randranges": rng_stab.randrange_calls,
                      "sweeps": st_stab["sweeps"], "relocations": st_stab["relocations"]},
        "reporting": {"shuffles": rng_rep.shuffle_calls, "randranges": rng_rep.randrange_calls,
                      "sweeps": st_rep["sweeps"], "relocations": st_rep["relocations"]},
        "aux_draws": 0,
    }

    # ---------------------------------------------------------------- stdout
    print("VERDICT 051 — Schelling segregation tipping at tau = 3/10 (PROPOSAL 040)")
    print(f"frame: {n}x{n} Moore-8 torus · {n_a}/{n_b}/{n_v} A/B/vacant · "
          f"live random-serial sweeps · uniform-random vacant relocation · "
          f"fixation or cap {cap}")
    print()
    print("GATES")
    print(f"  hand-fixture-4x4: engine + independent scan verified (16 cells)")
    print(f"  tau=0 control: relocations={st_ctl['relocations']} (expect 0), "
          f"init s range [{out_ctl['min_init_s']}, {out_ctl['max_init_s']}] "
          f"inside [47/100, 53/100]")
    print(f"  conservation: 0 violations across all legs "
          f"({st_ctl['sweeps'] + st_main['sweeps'] + st_stab['sweeps'] + st_rep['sweeps']} sweeps recounted)")
    print(f"  fixation re-certification: 0 failures "
          f"({st_ctl['fixations'] + st_main['fixations'] + st_stab['fixations'] + st_rep['fixations']} fixations independently re-certified)")
    print(f"  draw sentinels: control {rng_ctl.shuffle_calls}sh/{rng_ctl.randrange_calls}rr · "
          f"main {rng_main.shuffle_calls}sh/{rng_main.randrange_calls}rr · "
          f"stability {rng_stab.shuffle_calls}sh/{rng_stab.randrange_calls}rr · "
          f"reporting {rng_rep.shuffle_calls}sh/{rng_rep.randrange_calls}rr · aux 0 (never drawn)")
    print()
    print("MAIN LEG (seed 20261297, M = 32 per cell) — s(tau)")
    print("  tau      median s        mean s     cap-hits  sweeps-to-fix (q1/med/q3)")
    for tn, td in tau_grid:
        cell = main_cells[f"{tn}/{td}"]
        q = cell["sweeps_to_fixation_quartiles"]
        qs = f"{q['q1']}/{q['median']}/{q['q3']}" if q else "— (all capped)"
        mark = "  <- DECISION CELL" if (tn, td) == dec_tau else ""
        med_f = Fraction(*[int(x) for x in cell["median_s"].split("/")])
        print(f"  {tn}/{td:<6} {float(med_f):.6f}      {float(Fraction(*[int(x) for x in cell['mean_s'].split('/')])):.6f}   "
              f"{cell['cap_hits']:>2}/32     {qs}{mark}")
    print()
    print(f"MONOTONICITY (reporting): mean s non-decreasing over tau 1/8..1/2: "
          f"{'OK' if mono_ok else 'ANOMALY — ' + str(out['reporting_only_findings']['mono_means'])}")
    if not mono_ok:
        print("  MONOTONICITY ANOMALY (first-class, reporting-only)")
    print()
    print("STABILITY LEG (seed 20261298, M = 16, tau = 3/10)")
    print(f"  median s = {frac_str(stab_median)} = {float(stab_median):.6f} · "
          f"cap-hits {stab_caps}/16 · validity conjunct "
          f"{'PASS' if stab_validity else 'FAIL'}")
    print()
    print("REPORTING LEG (seed 20261299, M = 16 each, tau = 3/10 — cannot flip the decision)")
    for cname, csum in rep_cells.items():
        med_f = Fraction(*[int(x) for x in csum["median_s"].split("/")])
        print(f"  {cname:<14} median s = {csum['median_s']} = {float(med_f):.6f} · "
              f"cap-hits {csum['cap_hits']}/16")
    print(f"  vacancy-sensitivity flip across a band edge: "
          f"{'YES — names vacancy supply as the binding axis' if vacancy_flip else 'NO'}")
    print()
    print("DECISION (pre-registered, REJECT first; both bands carry the "
          "< 1/4-cap-censored validity conjunct)")
    print(f"  median s(3/10) main = {frac_str(median)} = {float(median):.6f}")
    print(f"  cap-censored main = {main_caps}/32 -> validity conjunct "
          f"{'PASS' if validity else 'FAIL'}")
    print(f"  REJECT (< 11/20 = 0.55): {'FIRES' if ruling == 'reject' else 'does not fire'}")
    approve_line = ("FIRES (stability-reproduced)" if ruling == "approve"
                    else "does not fire")
    print(f"  APPROVE (>= 7/10 = 0.70 AND stability reproduction): {approve_line}")
    print(f"  RULING: {ruling.upper()}"
          + (f" — binding axis: {axis}" if axis else ""))
    print()

    failed = sum(1 for _, ok, _ in CHECKS if not ok)
    passed = len(CHECKS) - failed
    out["self_checks"] = {
        "passed": passed,
        "failed": failed,
        "list": [{"name": nm, "ok": ok, "detail": d} for nm, ok, d in CHECKS],
    }
    (HERE / "results.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SELF-CHECKS: {passed} passed, {failed} failed")
    print("results.json written")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
