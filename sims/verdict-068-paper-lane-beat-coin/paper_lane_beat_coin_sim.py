#!/usr/bin/env python3
"""VERDICT 068 — the paper lane's BEAT coin (INTAKE 057, idea-engine PROPOSAL 057).

Prices trading-strategy's committed cycle-window grading grammar
(docs/paper-lane-protocol.md §7/§9 A5/A6 @ d857e50) at the proposal's pinned model:
  (i)   identity gate: BEAT <=> R_F < 1, zero exceptions over the full lattice,
        both cost accountings (multiplicative equal-cost; fixed-notional dollar);
  (ii)  the exact null coin B(delta, drift) per drift cell (Arm A, exact Fractions);
  (iii) exact one-sided Neyman-Pearson count-test power at n = 8 (size <= 1/20),
        NULL vs SKILL at the committed drift, plus exact n*_50 / n*_80 rows.

Arm A: seedless exact fractions.Fraction / integer lattice + binomial arithmetic
       (alone decision-bearing). Arm S: seeded MC confirmation (seed 20261365,
       CRN across delta worlds, agreement gate |EST-EXACT| <= 1/100 absolute AND
       <= 4*SE per decision cell + power row). Stability seed 20261366 (twin
       evaluators). Reporting seed 20261367 (reporting legs only). Aux 20261368
       NEVER constructed. Hermetic: reads ONLY its own fixtures.json.
Decision rule pre-registered, applied IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
"""

import json
import math
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- environment pin
assert sys.implementation.name == "cpython", "CPython required"
assert sys.version_info[:2] == (3, 11), "CPython 3.11 pinned (fixtures _meta.cpython_pin)"

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ---------------------------------------------------------------- self-check ledger
CHECKS = []  # (name, ok, detail)


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    return bool(ok)


def fr(s):
    return Fr(s)


# ---------------------------------------------------------------- registered constants
UP = fr(FX["market"]["up_gross"])          # 101/100
DOWN = fr(FX["market"]["down_gross"])      # 99/100
S_MOVE = fr(FX["market"]["s"])             # 1/100
DRIFTS = {k: fr(v) for k, v in FX["market"]["drift_grid"].items()}
DRIFT_ORDER = ["ZERO", "COMMITTED", "DOUBLE"]

F_PMF = {int(k): fr(v) for k, v in FX["cycle"]["F_pmf"].items()}
T_PMF = {int(k): fr(v) for k, v in FX["cycle"]["T_pmf"].items()}
F_SUPPORT = sorted(F_PMF)
T_SUPPORT = sorted(T_PMF)

DELTAS = {k: fr(v) for k, v in FX["skill"]["delta_grid"].items()}
DELTA_ORDER = ["ANTI", "NULL", "SKILL", "STRONG"]  # ascending in delta

COST_F = Fr(FX["accounting"]["cost_bps_per_side"], 10000)   # f = 6/10000
COST_SIDE = 1 - COST_F                                       # 9994/10000
C2 = COST_SIDE * COST_SIDE
NOTIONAL = FX["protocol_quotes_at_d857e50"]["notional_usd"]

SIZE_BOUND = fr(FX["grading"]["size_bound"])                 # 1/20
N_DECISION = FX["grading"]["n_grid_decision"][0]             # 8
N_REPORTING = FX["grading"]["n_grid_reporting"]              # [16, 34]
NSTAR_TARGETS = [fr(x) for x in FX["grading"]["n_star_targets"]]
NSTAR_CAP = FX["grading"]["n_star_scan_max"]

BAND_COIN_FLOOR = fr(FX["bands"]["reject_coin_floor"])       # 13/25
BAND_COIN_CEIL = fr(FX["bands"]["approve_coin_ceiling"])     # 1/2
BAND_POW_FLOOR = fr(FX["bands"]["approve_power_floor"])      # 4/5
BAND_POW_CEIL = fr(FX["bands"]["reject_power_ceiling"])      # 1/2
AGREE_ABS = fr(FX["bands"]["agreement_abs"])                 # 1/100
AGREE_SE = FX["bands"]["agreement_se_mult"]                  # 4

SEEDS = FX["seeds"]
CONSTRUCTED_SEEDS = []


class CountingRandom(random.Random):
    """random.Random with a .random() call counter (draw-count sentinels)."""

    def __init__(self, seed):
        CONSTRUCTED_SEEDS.append(seed)
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


# ---------------------------------------------------------------- Arm A: lattice
def build_kstar(up, down, supports):
    """k*(F) = max{k in 0..F : up^k * down^(F-k) < 1}, exact integer scan; -1 if none."""
    out = {}
    for F in supports:
        ks = -1
        for k in range(F + 1):
            if up ** k * down ** (F - k) < 1:
                ks = k
        out[F] = ks
    return out


def lattice_tables(up, down):
    """Exact BEAT indicators from the full protocol arithmetic, both accountings.

    Returns (tab_mult, tab_dollar, stats) keyed (F, k, T, j)."""
    tab_m, tab_d = {}, {}
    exc_m = exc_d = flips = ties = 0
    max_second_order = Fr(0)
    for F in F_SUPPORT:
        for k in range(F + 1):
            RF = up ** k * down ** (F - k)
            ident = RF < 1
            if RF == 1:
                ties += 1
            for T in T_SUPPORT:
                for j in range(T + 1):
                    RT = up ** j * down ** (T - j)
                    # multiplicative equal-cost accounting
                    strat_m = RT * C2
                    bench_m = RF * RT * C2
                    bm = strat_m > bench_m
                    # fixed-notional dollar accounting
                    strat_d = NOTIONAL * (RT * COST_SIDE - (1 + COST_F))
                    bench_d = NOTIONAL * (RF * RT * COST_SIDE - (1 + COST_F))
                    bd = strat_d > bench_d
                    tab_m[(F, k, T, j)] = bm
                    tab_d[(F, k, T, j)] = bd
                    if bm != ident:
                        exc_m += 1
                    if bd != ident:
                        exc_d += 1
                    margin_d = strat_d - bench_d
                    margin_m_scaled = NOTIONAL * (strat_m - bench_m)
                    if (margin_d > 0) != (margin_m_scaled > 0) or (margin_d < 0) != (margin_m_scaled < 0):
                        flips += 1
                    so = abs(margin_d - margin_m_scaled)
                    if so > max_second_order:
                        max_second_order = so
    stats = {
        "exceptions_multiplicative": exc_m,
        "exceptions_dollar": exc_d,
        "sign_flips_dollar_vs_mult": flips,
        "tie_points": ties,
        "max_abs_second_order_usd": max_second_order,
        "lattice_points": sum((F + 1) for F in F_SUPPORT) * sum((T + 1) for T in T_SUPPORT),
    }
    return tab_m, tab_d, stats


def binom_pmf_list(n, p):
    q = 1 - p
    return [Fr(math.comb(n, i)) * p ** i * q ** (n - i) for i in range(n + 1)]


def coin_B(kstar, f_pmf, p_flat):
    """B = P(BEAT) = sum_F w_F * P(Bin(F, p_flat) <= k*(F)), exact."""
    total = Fr(0)
    for F, w in sorted(f_pmf.items()):
        pmf = binom_pmf_list(F, p_flat)
        total += w * sum(pmf[: kstar[F] + 1])
    return total


def np_test(n, B0, B1):
    """Smallest critical c with null upper tail <= 1/20; exact power at B1."""
    pmf0 = binom_pmf_list(n, B0)
    pmf1 = binom_pmf_list(n, B1)
    tail0 = Fr(0)
    crit = n + 1
    # scan c downward while tail stays <= size bound
    for c in range(n, -1, -1):
        if tail0 + pmf0[c] <= SIZE_BOUND:
            tail0 += pmf0[c]
            crit = c
        else:
            break
    power = sum(pmf1[crit:]) if crit <= n else Fr(0)
    size = tail0
    return crit, size, power


def expected_gross(pmf, p_up_day, up, down):
    ex = p_up_day * up + (1 - p_up_day) * down
    return sum(w * ex ** L for L, w in sorted(pmf.items()))


# ---------------------------------------------------------------- Arm A: main surface
KSTAR = build_kstar(UP, DOWN, F_SUPPORT + [2] + T_SUPPORT)  # includes F=2 hand world
TAB_M, TAB_D, LAT = lattice_tables(UP, DOWN)

check("identity.mult.zero_exceptions", LAT["exceptions_multiplicative"] == 0,
      f"exceptions={LAT['exceptions_multiplicative']} over {LAT['lattice_points']} points")
check("identity.dollar.zero_exceptions", LAT["exceptions_dollar"] == 0)
check("identity.dollar_vs_mult.zero_sign_flips", LAT["sign_flips_dollar_vs_mult"] == 0)
check("identity.tie_points_zero", LAT["tie_points"] == 0)

# twin evaluators on the lattice: E1 (threshold) vs E2 (protocol arithmetic tables)
twin_lattice_mismatch = 0
for F in F_SUPPORT:
    for k in range(F + 1):
        e1 = k <= KSTAR[F]
        for T in T_SUPPORT:
            for j in range(T + 1):
                if TAB_M[(F, k, T, j)] != e1 or TAB_D[(F, k, T, j)] != e1:
                    twin_lattice_mismatch += 1
check("twin.lattice.agree", twin_lattice_mismatch == 0, f"mismatches={twin_lattice_mismatch}")

# B surface: every (drift, delta) cell, exact
B_SURFACE = {}
for dname in DRIFT_ORDER:
    for dl in DELTA_ORDER:
        p_flat = DRIFTS[dname] - DELTAS[dl]
        B_SURFACE[(dname, dl)] = coin_B(KSTAR, F_PMF, p_flat)

# second-structure cross-check of B on the decision cells: direct lattice summation
for cell in [("ZERO", "NULL"), ("COMMITTED", "NULL"), ("COMMITTED", "SKILL"), ("DOUBLE", "NULL")]:
    p_flat = DRIFTS[cell[0]] - DELTAS[cell[1]]
    alt = Fr(0)
    for F, w in sorted(F_PMF.items()):
        pmf = binom_pmf_list(F, p_flat)
        for k in range(F + 1):
            if TAB_M[(F, k, T_SUPPORT[0], 0)]:
                alt += w * pmf[k]
    check(f"B.two_ways.{cell[0]}.{cell[1]}", alt == B_SURFACE[cell])

B0 = B_SURFACE[("COMMITTED", "NULL")]
B1 = B_SURFACE[("COMMITTED", "SKILL")]

# NP rows: n in {8, 16, 34} for SKILL and STRONG alternatives
NP_ROWS = {}
for n in [N_DECISION] + N_REPORTING:
    for altname in ["SKILL", "STRONG"]:
        crit, size, power = np_test(n, B0, B_SURFACE[("COMMITTED", altname)])
        NP_ROWS[(n, altname)] = {"crit": crit, "size": size, "power": power}
POWER_N8 = NP_ROWS[(N_DECISION, "SKILL")]["power"]
CRIT_N8 = NP_ROWS[(N_DECISION, "SKILL")]["crit"]

# n* rows: exact scan (minimal n with exact power >= target), cap NSTAR_CAP
NSTAR = {}
power_by_n = {}
found = {str(t): None for t in NSTAR_TARGETS}
for n in range(1, NSTAR_CAP + 1):
    crit, size, power = np_test(n, B0, B1)
    power_by_n[n] = power
    for t in NSTAR_TARGETS:
        key = str(t)
        if found[key] is None and power >= t:
            found[key] = n
    if all(v is not None for v in found.values()):
        break
WINDOWS_PER_YEAR = fr(FX["cycle"]["windows_per_year"])
for t in NSTAR_TARGETS:
    n = found[str(t)]
    NSTAR[str(t)] = {"n_windows": n, "years": None if n is None else Fr(n) / WINDOWS_PER_YEAR}
check("nstar.found_within_cap", all(v["n_windows"] is not None for v in NSTAR.values()))

# EV rows (exact): E[dollar delta per cycle] = NOTIONAL*(1-f)*E[R_T]*(1 - E[R_F])
EV_ROWS = {}
for dname, dl in [("ZERO", "NULL"), ("COMMITTED", "NULL"), ("COMMITTED", "SKILL"),
                  ("DOUBLE", "NULL"), ("COMMITTED", "STRONG"), ("COMMITTED", "ANTI")]:
    p_flat = DRIFTS[dname] - DELTAS[dl]
    p_pos = DRIFTS[dname] + DELTAS[dl]
    erf_ = expected_gross(F_PMF, p_flat, UP, DOWN)
    ert = expected_gross(T_PMF, p_pos, UP, DOWN)
    EV_ROWS[(dname, dl)] = {
        "E_RF": erf_, "E_RT": ert,
        "ev_dollar": NOTIONAL * COST_SIDE * ert * (1 - erf_),
        "ev_mult_scaled": NOTIONAL * C2 * ert * (1 - erf_),
    }
check("ev.zero_at_zero_drift", EV_ROWS[("ZERO", "NULL")]["ev_dollar"] == 0)
check("ev.negative_at_committed_null", EV_ROWS[("COMMITTED", "NULL")]["ev_dollar"] < 0)
check("ev.coin_vs_ev_split", B0 > Fr(1, 2) and EV_ROWS[("COMMITTED", "NULL")]["ev_dollar"] < 0,
      "null coin favors while EV charges")

# ---------------------------------------------------------------- controls F1-F5
# F1
check("F1.F_pmf_sums_1", sum(F_PMF.values()) == 1)
check("F1.T_pmf_sums_1", sum(T_PMF.values()) == 1)
for dname in DRIFT_ORDER:
    p = DRIFTS[dname]
    ex = p * UP + (1 - p) * DOWN
    check(f"F1.EX_drift_identity.{dname}", ex - 1 == S_MOVE * (2 * p - 1))
MEAN_CYCLE = sum(Fr(F) * w for F, w in F_PMF.items()) + sum(Fr(T) * w for T, w in T_PMF.items())
check("F1.mean_cycle_45_2", MEAN_CYCLE == Fr(45, 2))
IMPLIED_W18 = Fr(FX["cycle"]["trading_days_per_18mo"]) / MEAN_CYCLE
check("F1.windows_per_18mo_band",
      fr(FX["cycle"]["implied_windows_per_18mo_band"][0]) <= IMPLIED_W18 <= fr(FX["cycle"]["implied_windows_per_18mo_band"][1]),
      f"implied={IMPLIED_W18}")
check("F1.windows_per_year_pin", Fr(FX["cycle"]["trading_days_per_year"]) / MEAN_CYCLE == WINDOWS_PER_YEAR)

# F2: primality + no ties + kstar = F/2 at even F
def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True

check("F2.101_prime", is_prime(101))
no_tie = all(101 ** k * 99 ** (F - k) != 100 ** F for F in F_SUPPORT + [2] for k in range(F + 1))
check("F2.no_tie_over_support", no_tie)
check("F2.kstar_half_F", all(KSTAR[F] == F // 2 for F in F_SUPPORT), str({F: KSTAR[F] for F in F_SUPPORT}))

# F3
F3_EXPECTED = Fr(20656327, 33554432)
check("F3.B_null_zero_closed_form", B_SURFACE[("ZERO", "NULL")] == F3_EXPECTED,
      f"got {B_SURFACE[('ZERO', 'NULL')]}")

# F4 monotonicity
b_null = [B_SURFACE[(d, "NULL")] for d in DRIFT_ORDER]
check("F4.B_null_nonincreasing_in_drift", b_null[0] >= b_null[1] >= b_null[2])
for dname in DRIFT_ORDER:
    seq = [B_SURFACE[(dname, dl)] for dl in DELTA_ORDER]  # ascending delta
    check(f"F4.B_increasing_in_delta.{dname}", all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)))
pow_seq_n = [NP_ROWS[(n, "SKILL")]["power"] for n in [8, 16, 34]]
check("F4.power_nondecreasing_in_n", pow_seq_n[0] <= pow_seq_n[1] <= pow_seq_n[2], str([float(x) for x in pow_seq_n]))
for n in [8, 16, 34]:
    check(f"F4.power_nondecreasing_in_delta.n{n}",
          NP_ROWS[(n, "SKILL")]["power"] <= NP_ROWS[(n, "STRONG")]["power"])

# F5 hand world F = 2
check("F5.kstar_2_is_1", KSTAR[2] == 1)
for dname in DRIFT_ORDER:
    p = DRIFTS[dname]
    pmf2 = binom_pmf_list(2, p)
    check(f"F5.F2_hand.{dname}", sum(pmf2[:2]) == 1 - p * p)

# ---------------------------------------------------------------- Arm S machinery
F_KEYS = F_SUPPORT
F_CUM = []
acc = Fr(0)
for F in F_KEYS:
    acc += F_PMF[F]
    F_CUM.append(float(acc))
T_CUM = []
acc = Fr(0)
for T in T_SUPPORT:
    acc += T_PMF[T]
    T_CUM.append(float(acc))


def draw_len(u, cum, keys):
    for i, c in enumerate(cum):
        if u < c:
            return keys[i]
    return keys[-1]


def run_cycle_leg(rng, n_cycles, drift, delta_names, kstar, tab_m, tab_d,
                  f_cum=None, f_keys=None):
    """One MC block at a drift: n_cycles cycles, CRN across the delta worlds.

    Returns per-delta beat counts (mult-accounting), twin/accounting mismatch
    counters, and draw totals."""
    f_cum = f_cum or F_CUM
    f_keys = f_keys or F_KEYS
    p_up = DRIFTS[drift]
    thr_flat = {dl: float(p_up - DELTAS[dl]) for dl in delta_names}
    thr_pos = {dl: float(p_up + DELTAS[dl]) for dl in delta_names}
    beats = {dl: 0 for dl in delta_names}
    mism_twin = 0
    mism_acct = 0
    sumF = sumT = 0
    calls0 = rng.calls
    for _ in range(n_cycles):
        F = draw_len(rng.random(), f_cum, f_keys)
        us = [rng.random() for _ in range(F)]
        T = draw_len(rng.random(), T_CUM, T_SUPPORT)
        vs = [rng.random() for _ in range(T)]
        sumF += F
        sumT += T
        for dl in delta_names:
            tf = thr_flat[dl]
            tp = thr_pos[dl]
            k = sum(1 for u in us if u < tf)
            j = sum(1 for v in vs if v < tp)
            bm = tab_m[(F, k, T, j)]
            bd = tab_d[(F, k, T, j)]
            e1 = k <= kstar[F]
            if bm != e1:
                mism_twin += 1
            if bm != bd:
                mism_acct += 1
            if bm:
                beats[dl] += 1
    draws = rng.calls - calls0
    expected_draws = 2 * n_cycles + sumF + sumT
    return {"beats": beats, "twin_mismatch": mism_twin, "acct_mismatch": mism_acct,
            "draws": draws, "expected_draws": expected_draws, "n": n_cycles}


def run_season_leg(rng, n_seasons, drift, delta, crit, kstar, tab_m):
    p_up = DRIFTS[drift]
    tf = float(p_up - DELTAS[delta])
    tp = float(p_up + DELTAS[delta])
    hits = 0
    sum_days = 0
    calls0 = rng.calls
    wlen = FX["arm_s"]["season_length_windows"]
    for _ in range(n_seasons):
        b = 0
        for _w in range(wlen):
            F = draw_len(rng.random(), F_CUM, F_KEYS)
            k = sum(1 for _ in range(F) if rng.random() < tf)
            T = draw_len(rng.random(), T_CUM, T_SUPPORT)
            j = sum(1 for _ in range(T) if rng.random() < tp)
            sum_days += F + T
            if tab_m[(F, k, T, j)]:
                b += 1
        if b >= crit:
            hits += 1
    draws = rng.calls - calls0
    expected = n_seasons * wlen * 2 + sum_days
    return {"hits": hits, "n": n_seasons, "draws": draws, "expected_draws": expected}


def gate(est_num, est_den, exact, n):
    est = Fr(est_num, est_den)
    dev = abs(est - exact)
    abs_ok = dev <= AGREE_ABS
    se_ok = dev * dev * n <= AGREE_SE * AGREE_SE * exact * (1 - exact)
    return {"est": est, "dev": dev, "abs_ok": abs_ok, "se_ok": se_ok, "ok": abs_ok and se_ok}


DECISION_WORLDS = [tuple(x) for x in FX["arm_s"]["decision_worlds"]]


def run_confirmation(seed, n_cycles, n_seasons):
    """Full Arm-S pipeline: decision-world B cells + power/size season rows."""
    rng = CountingRandom(seed)
    out = {"cells": {}, "sentinel_ok": True, "twin_mismatch": 0, "acct_mismatch": 0}
    # drift blocks in registered decision-world order, CRN within a drift
    blocks = [("ZERO", ["NULL"]), ("COMMITTED", ["NULL", "SKILL"]), ("DOUBLE", ["NULL"])]
    for drift, dls in blocks:
        r = run_cycle_leg(rng, n_cycles, drift, dls, KSTAR, TAB_M, TAB_D)
        out["sentinel_ok"] &= (r["draws"] == r["expected_draws"])
        out["twin_mismatch"] += r["twin_mismatch"]
        out["acct_mismatch"] += r["acct_mismatch"]
        for dl in dls:
            exact = B_SURFACE[(drift, dl)]
            g = gate(r["beats"][dl], n_cycles, exact, n_cycles)
            out["cells"][f"B.{drift}.{dl}"] = g
    # power row: 8-window seasons under (COMMITTED, SKILL), gated
    ps = run_season_leg(rng, n_seasons, "COMMITTED", "SKILL", CRIT_N8, KSTAR, TAB_M)
    out["sentinel_ok"] &= (ps["draws"] == ps["expected_draws"])
    out["cells"]["power.n8.SKILL"] = gate(ps["hits"], n_seasons, POWER_N8, n_seasons)
    # size row: seasons under (COMMITTED, NULL), reported UNGATED (fixture C7)
    ss = run_season_leg(rng, n_seasons, "COMMITTED", "NULL", CRIT_N8, KSTAR, TAB_M)
    out["sentinel_ok"] &= (ss["draws"] == ss["expected_draws"])
    size_exact = NP_ROWS[(N_DECISION, "SKILL")]["size"]
    out["size_row_ungated"] = {"est": Fr(ss["hits"], n_seasons), "exact": size_exact}
    out["gates_all_ok"] = all(c["ok"] for k, c in out["cells"].items())
    return out


# headline leg (seed 20261365)
HEADLINE = run_confirmation(SEEDS["headline"], FX["arm_s"]["N_cycles_per_decision_world"],
                            FX["arm_s"]["N_seasons_power_row"])
check("armS.headline.sentinels", HEADLINE["sentinel_ok"])
check("armS.headline.twin_zero_mismatch", HEADLINE["twin_mismatch"] == 0)
check("armS.headline.accounting_zero_mismatch", HEADLINE["acct_mismatch"] == 0)
for cname, g in HEADLINE["cells"].items():
    check(f"armS.headline.gate.{cname}", g["ok"],
          f"est={float(g['est']):.6f} dev={float(g['dev']):.6f} abs_ok={g['abs_ok']} se_ok={g['se_ok']}")

# stability leg (seed 20261366)
STABILITY = run_confirmation(SEEDS["stability"], FX["arm_s"]["stability_N_cycles"],
                             FX["arm_s"]["stability_N_seasons"])
check("armS.stability.sentinels", STABILITY["sentinel_ok"])
check("armS.stability.twin_zero_mismatch", STABILITY["twin_mismatch"] == 0)
check("armS.stability.accounting_zero_mismatch", STABILITY["acct_mismatch"] == 0)
for cname, g in STABILITY["cells"].items():
    check(f"armS.stability.gate.{cname}", g["ok"],
          f"est={float(g['est']):.6f} dev={float(g['dev']):.6f} abs_ok={g['abs_ok']} se_ok={g['se_ok']}")

# ---------------------------------------------------------------- reporting legs (seed 20261367)
REPORTING = {"mc": {}, "exact": {}}
rrng = CountingRandom(SEEDS["reporting"])

# sensitivity s worlds: exact structure + MC confirm at (COMMITTED, NULL), ungated
for s_str in FX["market"]["s_sensitivity_pairs"]:
    s = fr(s_str)
    up_s, down_s = 1 + s, 1 - s
    ks_s = build_kstar(up_s, down_s, F_SUPPORT)
    ties_s = sum(1 for F in F_SUPPORT for k in range(F + 1) if up_s ** k * down_s ** (F - k) == 1)
    ident_exc = 0
    for F in F_SUPPORT:
        for k in range(F + 1):
            RF = up_s ** k * down_s ** (F - k)
            # multiplicative accounting sign check with representative R_T terms
            for T in T_SUPPORT:
                RT = up_s ** T * down_s ** 0
                if ((RT * C2 > RF * RT * C2) != (RF < 1)):
                    ident_exc += 1
    check(f"reporting.s{s_str.replace('/', '_')}.identity_holds", ident_exc == 0)
    check(f"reporting.s{s_str.replace('/', '_')}.tie_points_zero", ties_s == 0)
    tab_s = {}
    for F in F_SUPPORT:
        for k in range(F + 1):
            beat = k <= ks_s[F]
            for T in T_SUPPORT:
                for j in range(T + 1):
                    tab_s[(F, k, T, j)] = beat
    bexact = {d: coin_B(ks_s, F_PMF, DRIFTS[d]) for d in DRIFT_ORDER}
    r = run_cycle_leg(rrng, FX["arm_s"]["reporting_N_cycles"], "COMMITTED", ["NULL"], ks_s, tab_s, tab_s)
    check(f"reporting.s{s_str.replace('/', '_')}.sentinel", r["draws"] == r["expected_draws"])
    REPORTING["exact"][f"B_null.s={s_str}"] = {d: bexact[d] for d in DRIFT_ORDER}
    REPORTING["exact"][f"kstar.s={s_str}"] = ks_s
    REPORTING["mc"][f"B.s={s_str}.COMMITTED.NULL"] = {
        "est": Fr(r["beats"]["NULL"], r["n"]), "exact": bexact["COMMITTED"],
        "dev": abs(Fr(r["beats"]["NULL"], r["n"]) - bexact["COMMITTED"])}

# F-mix pairs (main s): exact + MC confirm at (COMMITTED, NULL), ungated
for mixname, mix in FX["cycle"]["F_mix_reporting_pairs"].items():
    fpmf = {int(k): fr(v) for k, v in mix.items()}
    check(f"reporting.fmix.{mixname}.pmf_sums_1", sum(fpmf.values()) == 1)
    bexact = coin_B(KSTAR, fpmf, DRIFTS["COMMITTED"])
    keys = sorted(fpmf)
    cum = []
    a = Fr(0)
    for F in keys:
        a += fpmf[F]
        cum.append(float(a))
    r = run_cycle_leg(rrng, FX["arm_s"]["reporting_N_cycles"], "COMMITTED", ["NULL"],
                      KSTAR, TAB_M, TAB_D, f_cum=cum, f_keys=keys)
    check(f"reporting.fmix.{mixname}.sentinel", r["draws"] == r["expected_draws"])
    REPORTING["exact"][f"B_null.COMMITTED.fmix={mixname}"] = bexact
    REPORTING["mc"][f"B.fmix={mixname}.COMMITTED.NULL"] = {
        "est": Fr(r["beats"]["NULL"], r["n"]), "exact": bexact,
        "dev": abs(Fr(r["beats"]["NULL"], r["n"]) - bexact)}

# STRONG / ANTI delta cells at COMMITTED: MC confirm, ungated
for dl in ["STRONG", "ANTI"]:
    r = run_cycle_leg(rrng, FX["arm_s"]["reporting_N_cycles"], "COMMITTED", [dl], KSTAR, TAB_M, TAB_D)
    check(f"reporting.delta.{dl}.sentinel", r["draws"] == r["expected_draws"])
    exact = B_SURFACE[("COMMITTED", dl)]
    REPORTING["mc"][f"B.COMMITTED.{dl}"] = {
        "est": Fr(r["beats"][dl], r["n"]), "exact": exact,
        "dev": abs(Fr(r["beats"][dl], r["n"]) - exact)}

# seed hygiene
check("seeds.constructed_exactly", CONSTRUCTED_SEEDS == [SEEDS["headline"], SEEDS["stability"], SEEDS["reporting"]],
      str(CONSTRUCTED_SEEDS))
check("seeds.aux_never_constructed", SEEDS["aux_reserved_never_constructed"] not in CONSTRUCTED_SEEDS)

# ---------------------------------------------------------------- decision procedure
CONTROL_PREFIXES = ("F1.", "F2.", "F3.", "F4.", "F5.", "identity.", "twin.", "B.two_ways.",
                    "armS.headline.sentinels", "armS.headline.twin", "armS.headline.accounting",
                    "armS.stability.sentinels", "armS.stability.twin", "armS.stability.accounting",
                    "seeds.", "nstar.", "ev.", "reporting.")
CONTROLS_OK = all(ok for name, ok, _ in CHECKS if name.startswith(CONTROL_PREFIXES))


def classify(conj_a, conj_b, conj_c, conj_d, controls_ok):
    """Registered order: REJECT -> INVALID -> APPROVE -> NULL."""
    if conj_a and conj_b and conj_c and conj_d and controls_ok:
        return "REJECT", "all four REJECT conjuncts fire"
    if (not controls_ok) or (not conj_d):
        return "INVALID", "controls misbehaving / agreement breach — report, no ruling"
    approve = (POWER_N8 >= BAND_POW_FLOOR) and (B0 <= BAND_COIN_CEIL)
    if approve:
        return "APPROVE", "power >= 4/5 at n=8 and B(NULL, COMMITTED) <= 1/2"
    if BAND_POW_CEIL <= POWER_N8 < BAND_POW_FLOOR:
        return "NULL", "power-straddle axis"
    if BAND_COIN_CEIL < B0 < BAND_COIN_FLOOR:
        return "NULL", "coin-straddle axis"
    return "NULL", "residual axis (named, never a re-run request)"


CONJ_A = LAT["exceptions_multiplicative"] == 0
CONJ_B = B0 >= BAND_COIN_FLOOR
CONJ_C = POWER_N8 < BAND_POW_CEIL
CONJ_D_HEAD = HEADLINE["gates_all_ok"]
CONJ_D_STAB = STABILITY["gates_all_ok"]

HEAD_CLASS, HEAD_WHY = classify(CONJ_A, CONJ_B, CONJ_C, CONJ_D_HEAD, CONTROLS_OK)
STAB_CLASS, STAB_WHY = classify(CONJ_A, CONJ_B, CONJ_C, CONJ_D_STAB, CONTROLS_OK)

STABILITY_REPRODUCES = (STAB_CLASS == HEAD_CLASS)
check("stability.reproduces_ruling", STABILITY_REPRODUCES, f"headline={HEAD_CLASS} stability={STAB_CLASS}")

if STABILITY_REPRODUCES:
    FINAL_CLASS, FINAL_WHY = HEAD_CLASS, HEAD_WHY
else:
    FINAL_CLASS, FINAL_WHY = "INVALID", (
        f"stability leg (seed {SEEDS['stability']}) lands {STAB_CLASS} vs headline {HEAD_CLASS} — "
        "'any agreement breach' clause, fixture C4")

# drafter comparison (never gated)
DRAFT = FX["drafter_disclosed_landing_never_trusted"]
DRAFT_CMP = {
    "B_NULL_COMMITTED_match": str(B0) == DRAFT["B_NULL_COMMITTED"],
    "B_NULL_ZERO_match": str(B_SURFACE[("ZERO", "NULL")]) == DRAFT["B_NULL_ZERO"],
    "crit_n8_match": CRIT_N8 == DRAFT["critical_count_n8"],
    "n_star_50_match": NSTAR[str(Fr(1, 2))]["n_windows"] == DRAFT["n_star_50"],
    "n_star_80_match": NSTAR[str(Fr(4, 5))]["n_windows"] == DRAFT["n_star_80"],
    "class_match": FINAL_CLASS.lower() in DRAFT["class"].lower(),
}

# ---------------------------------------------------------------- results + stdout
def fs(x):
    """Fraction -> {exact, float} pair for JSON."""
    if isinstance(x, Fr):
        return {"exact": f"{x.numerator}/{x.denominator}", "float": float(x)}
    return x


results = {
    "verdict": "VERDICT 068",
    "intake": "INTAKE 057",
    "class": FINAL_CLASS,
    "class_reason": FINAL_WHY,
    "headline_class": HEAD_CLASS,
    "stability_class": STAB_CLASS,
    "conjuncts": {
        "a_identity_zero_exceptions": CONJ_A,
        "b_coin_ge_13_25": CONJ_B,
        "c_power_n8_lt_1_2": CONJ_C,
        "d_armS_agreement_headline": CONJ_D_HEAD,
        "d_armS_agreement_stability": CONJ_D_STAB,
        "controls_ok": CONTROLS_OK,
    },
    "identity_gate": {k: (fs(v) if isinstance(v, Fr) else v) for k, v in LAT.items()},
    "kstar": {str(F): KSTAR[F] for F in sorted(KSTAR)},
    "B_surface": {f"{d}.{dl}": fs(B_SURFACE[(d, dl)]) for d in DRIFT_ORDER for dl in DELTA_ORDER},
    "np_rows": {f"n={n}.alt={a}": {"crit": v["crit"], "size": fs(v["size"]), "power": fs(v["power"])}
                for (n, a), v in sorted(NP_ROWS.items())},
    "n_star": {t: {"n_windows": v["n_windows"], "years": fs(v["years"])} for t, v in NSTAR.items()},
    "ev_rows": {f"{d}.{dl}": {k2: fs(v2) for k2, v2 in row.items()} for (d, dl), row in EV_ROWS.items()},
    "arm_s_headline": {
        "N_cycles": FX["arm_s"]["N_cycles_per_decision_world"],
        "N_seasons": FX["arm_s"]["N_seasons_power_row"],
        "cells": {k: {"est": fs(v["est"]), "dev": fs(v["dev"]), "abs_ok": v["abs_ok"],
                      "se_ok": v["se_ok"], "ok": v["ok"]} for k, v in HEADLINE["cells"].items()},
        "size_row_ungated": {"est": fs(HEADLINE["size_row_ungated"]["est"]),
                             "exact": fs(HEADLINE["size_row_ungated"]["exact"])},
        "sentinel_ok": HEADLINE["sentinel_ok"],
    },
    "arm_s_stability": {
        "N_cycles": FX["arm_s"]["stability_N_cycles"],
        "N_seasons": FX["arm_s"]["stability_N_seasons"],
        "cells": {k: {"est": fs(v["est"]), "dev": fs(v["dev"]), "abs_ok": v["abs_ok"],
                      "se_ok": v["se_ok"], "ok": v["ok"]} for k, v in STABILITY["cells"].items()},
        "sentinel_ok": STABILITY["sentinel_ok"],
        "reproduces_ruling": STABILITY_REPRODUCES,
    },
    "reporting": {
        "exact": {k: ({d: fs(x) for d, x in v.items()} if isinstance(v, dict) and all(isinstance(x, Fr) for x in v.values())
                      else (fs(v) if isinstance(v, Fr) else v))
                  for k, v in REPORTING["exact"].items()},
        "mc_ungated": {k: {"est": fs(v["est"]), "exact": fs(v["exact"]), "dev": fs(v["dev"])}
                       for k, v in REPORTING["mc"].items()},
    },
    "seeds": {"constructed": CONSTRUCTED_SEEDS, "aux_never_constructed": SEEDS["aux_reserved_never_constructed"]},
    "drafter_comparison_never_gated": DRAFT_CMP,
    "self_checks": {"passed": sum(1 for _, ok, _ in CHECKS if ok),
                    "failed": sum(1 for _, ok, _ in CHECKS if not ok),
                    "failures": [{"name": n, "detail": d} for n, ok, d in CHECKS if not ok]},
    "environment": {"implementation": sys.implementation.name,
                    "python_major_minor": f"{sys.version_info[0]}.{sys.version_info[1]}"},
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2, sort_keys=True)
    fh.write("\n")

# stdout report (deterministic — no wall-clock anywhere)
P = print
P("VERDICT 068 — the paper lane's BEAT coin (INTAKE 057)")
P("=" * 72)
P(f"identity gate: {LAT['exceptions_multiplicative']} exceptions (mult), "
  f"{LAT['exceptions_dollar']} (dollar), {LAT['sign_flips_dollar_vs_mult']} sign flips, "
  f"{LAT['tie_points']} ties over {LAT['lattice_points']} lattice points")
P(f"max |second-order cost asymmetry| = ${float(LAT['max_abs_second_order_usd']):.6f} "
  f"(exact {LAT['max_abs_second_order_usd']})")
P(f"k*(F): " + ", ".join(f"k*({F})={KSTAR[F]}" for F in F_SUPPORT))
P("-" * 72)
P("B(delta, drift) exact surface:")
for d in DRIFT_ORDER:
    for dl in DELTA_ORDER:
        b = B_SURFACE[(d, dl)]
        P(f"  B({dl:6s}, {d:9s}) = {float(b):.6f}  = {b}")
P("-" * 72)
P(f"NP count test, size <= 1/20, NULL vs SKILL @ COMMITTED:")
for n in [8, 16, 34]:
    v = NP_ROWS[(n, "SKILL")]
    P(f"  n={n:3d}: crit={v['crit']:3d}  size={float(v['size']):.6f}  power={float(v['power']):.6f}")
for t, v in NSTAR.items():
    P(f"  n*(power >= {t}) = {v['n_windows']} windows = {float(v['years']):.2f} years at the committed rate")
P("-" * 72)
P("EV rows (E[dollar delta per cycle], strategy minus B&H, dollar accounting):")
for (d, dl), row in EV_ROWS.items():
    P(f"  EV({dl:6s}, {d:9s}) = ${float(row['ev_dollar']):+.4f}   (E[R_F]={float(row['E_RF']):.6f})")
P("-" * 72)
P("Arm S headline gates (seed 20261365):")
for k, g in HEADLINE["cells"].items():
    P(f"  {k:24s} est={float(g['est']):.6f} dev={float(g['dev']):.6f} "
      f"abs_ok={g['abs_ok']} se_ok={g['se_ok']} -> {'PASS' if g['ok'] else 'FAIL'}")
P(f"  size row (ungated): est={float(HEADLINE['size_row_ungated']['est']):.6f} "
  f"exact={float(HEADLINE['size_row_ungated']['exact']):.6f}")
P("Arm S stability gates (seed 20261366): " +
  ("ALL PASS" if STABILITY["gates_all_ok"] else "BREACH — " +
   ", ".join(k for k, g in STABILITY["cells"].items() if not g["ok"])))
P("-" * 72)
P(f"conjunct (a) identity zero exceptions : {CONJ_A}")
P(f"conjunct (b) B(NULL, COMMITTED) >= 13/25 : {CONJ_B}  (B0 = {float(B0):.6f} vs 0.52)")
P(f"conjunct (c) power(n=8) < 1/2 : {CONJ_C}  (power = {float(POWER_N8):.6f}, crit = {CRIT_N8})")
P(f"conjunct (d) Arm-S agreement (headline) : {CONJ_D_HEAD}")
P(f"controls ok : {CONTROLS_OK}   stability reproduces : {STABILITY_REPRODUCES} "
  f"(headline {HEAD_CLASS} / stability {STAB_CLASS})")
P("=" * 72)
P(f"CLASS: {FINAL_CLASS} — {FINAL_WHY}")
P(f"SELF-CHECKS: {results['self_checks']['passed']} passed, {results['self_checks']['failed']} failed")
for f in results["self_checks"]["failures"]:
    P(f"  FAILED: {f['name']} — {f['detail']}")
P("drafter comparison (never gated): " + json.dumps(DRAFT_CMP, sort_keys=True))
