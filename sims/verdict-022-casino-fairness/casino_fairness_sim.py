#!/usr/bin/env python3
"""VERDICT 022 — casino fairness envelope (idea-engine PROPOSAL 020).

Fully hermetic, stdlib-only, dual-arm pre-registered sim:
  Arm A (analytic, seedless, exact Fraction arithmetic): exact binomial FUN
    tails via math.comb; exact two-boundary gambler's-ruin closed forms for
    GRINDER on G1 x C (independently re-derived by tridiagonal elimination);
    e=0 control P_double = 1/3 exactly.
  Arm S (seeded MC): random.Random(20260721), pinned loop order, integer-chip
    bankroll walks; M = 5,000 casual / 2,000 grinder / 500 compulsive per
    cell-policy; 1.0 pp Arm-A agreement gate; half-M stability leg seed
    20260722 must reproduce the ruling.

Every constant is read from the committed pre-registration fixtures.json
(written BEFORE this runner) and cross-checked against the literals below.
No network, no git, no wall clock, no hash(). stdout and results.json are
byte-identical across process runs on the pinned CPython minor version.

Run:  python3 sims/verdict-022-casino-fairness/casino_fairness_sim.py
Exit 0 iff all self-checks pass.
"""

import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------- self-checks
CHECKS = 0
FAILS = []


def ck(cond, label):
    global CHECKS
    if cond:
        CHECKS += 1
    else:
        FAILS.append(label)


def ckn(n):
    """Bulk-count n passed checks (hot loops count locally, then report)."""
    global CHECKS
    CHECKS += n


# ------------------------------------------------------------------- constants
B0 = 1000
MIN_STAKE = 1
GS = [("G1", 1), ("G2", 5), ("G3", 19)]
E_GRID = [Fraction(1, 100), Fraction(1, 50), Fraction(1, 20), Fraction(1, 10)]
E_ALL = [Fraction(0)] + E_GRID  # pinned sweep order: e ascending, control first
MAXBETS = [50, 250, 1000]  # m in {0.05, 0.25, 1.0} of B0
M_GRID = [Fraction(1, 20), Fraction(1, 4), Fraction(1, 1)]
# policy tuples: (name, type, fraction-numerator) — type 0=F, 1=C, 2=M
POLICIES = [("F-0.01", 0, 1), ("F-0.05", 0, 5), ("F-0.10", 0, 10),
            ("C", 1, 0), ("M", 2, 0)]
C_STAKE = 50          # floor(0.05 * B0)
MART_BASE = 10        # floor(0.01 * B0)
REF_STAKE = 10        # FUN reference leg (analytic-only)
CASUAL_BETS = 100
GRIND_LO, GRIND_HI, GRIND_CAP = 500, 2000, 4000
COMP_CAP = 20000
M_CASUAL, M_GRINDER, M_COMPULSIVE = 5000, 2000, 500
SEED_PRIMARY, SEED_STABILITY, SEED_AUX = 20260721, 20260722, 20260723
FUN_BAND = Fraction(1, 4)
SAFE_BAND = Fraction(1, 20)
SINK_BAND = Fraction(1, 10)
GATE_PP = Fraction(1, 100)
WIPE_LINE = 100  # 0.1 * B0

ck(sys.version_info[:2] == (3, 11), "pinned CPython minor version 3.11")

# ------------------------------------------------- fixture cross-checks (pin 0)
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)
FC = FIX["constants"]
ck(FC["B0"] == B0, "fixture B0")
ck(FC["min_stake"] == MIN_STAKE, "fixture min_stake")
ck(FC["archetypes"] == {"G1": 1, "G2": 5, "G3": 19}, "fixture archetypes")
ck([Fraction(x) for x in FC["e_grid_exact"]] == E_GRID, "fixture e_grid exact")
ck(all(abs(float(f) - g) < 1e-12 for f, g in zip(E_GRID, FC["e_grid"])),
   "fixture e_grid floats")
ck(FC["e_control"] == 0.0, "fixture e_control")
ck(FC["maxbet_chips"] == MAXBETS, "fixture maxbet_chips")
ck([float(x) for x in M_GRID] == FC["m_grid"], "fixture m_grid")
ck(FC["M_casual"] == M_CASUAL and FC["M_grinder"] == M_GRINDER
   and FC["M_compulsive"] == M_COMPULSIVE, "fixture M per profile")
ck(FC["seed_primary"] == SEED_PRIMARY and FC["seed_stability"] == SEED_STABILITY,
   "fixture seeds")
ck(FC["agreement_gate_pp"] == 1.0, "fixture agreement gate")
ck("20260723" in FIX["intake_time_decisions_disclosed"][4], "fixture aux seed disclosed")
ck(all(mb == int(mf * B0) for mb, mf in zip(MAXBETS, M_GRID)), "MAXBET = m*B0")
ck(C_STAKE == B0 * 5 // 100 and MART_BASE == B0 // 100, "policy constants from B0")

# EV identity: p*k - (1-p) == -e exactly, for every (k, e)
for _, k in GS:
    for e in E_ALL:
        p = (1 - e) / (k + 1)
        ck(p * k - (1 - p) == -e, "EV identity k=%d e=%s" % (k, e))

# ------------------------------------------------------------------ Arm A: FUN
WMIN = {}
for gname, k in GS:
    wmin = 100 // (k + 1) + 1
    # independent scan: smallest w with w*(k+1) > 100
    scan = next(w for w in range(101) if w * (k + 1) > 100)
    ck(scan == wmin, "w_min scan %s" % gname)
    WMIN[gname] = wmin
ck(WMIN == {"G1": 51, "G2": 17, "G3": 6}, "w_min table matches pre-registration")


def fun_exact(k, e):
    """Exact binomial tail P(wins*(k+1) > 100) over 100 reference bets."""
    p = (1 - e) / (k + 1)
    q = 1 - p
    wmin = 100 // (k + 1) + 1
    total = Fraction(0)
    tail = Fraction(0)
    for w in range(101):
        term = math.comb(100, w) * p ** w * q ** (100 - w)
        total += term
        if w >= wmin:
            tail += term
    ck(total == 1, "binomial mass sums to 1 (k=%d e=%s)" % (k, e))
    return tail


ARM_A_FUN = {}
for gname, k in GS:
    prev = None
    for e in E_ALL:
        t = fun_exact(k, e)
        ARM_A_FUN[(gname, e)] = t
        if prev is not None:
            ck(t <= prev, "FUN tail monotone nonincreasing in e (%s)" % gname)
        prev = t

# --------------------------------------------------- Arm A: gambler's ruin G1xC


def ruin_closed(e):
    """P(reach +30 units before 0 | start 10), unit step 50 chips, G1 x C."""
    p = (1 - e) / 2
    if p == Fraction(1, 2):
        return Fraction(10, 30)
    r = (1 - p) / p
    return (1 - r ** 10) / (1 - r ** 30)


def ruin_eliminated(e):
    """Independent second derivation: exact tridiagonal forward elimination of
    h_i = p*h_{i+1} + q*h_{i-1}, h_0 = 0, h_30 = 1, on states 0..30."""
    p = (1 - e) / 2
    q = 1 - p
    # h_i = a_i + b_i * x with x = h_1 unknown
    a = [Fraction(0), Fraction(0)]
    b = [Fraction(0), Fraction(1)]
    for i in range(1, 30):
        # h_{i+1} = (h_i - q*h_{i-1}) / p
        a.append((a[i] - q * a[i - 1]) / p)
        b.append((b[i] - q * b[i - 1]) / p)
    x = (1 - a[30]) / b[30]
    return a[10] + b[10] * x


ARM_A_RUIN = {}
for e in E_ALL:
    cf = ruin_closed(e)
    el = ruin_eliminated(e)
    ck(cf == el, "ruin closed form == elimination (e=%s)" % e)
    ARM_A_RUIN[e] = cf
ck(ARM_A_RUIN[Fraction(0)] == Fraction(1, 3), "e=0 control P_double = 1/3 exactly")

# ------------------------------------------------------------- Arm S: sessions


def play_casual(rr, p, k, maxbet, ptype, num):
    """One casual session: 100 bets or bankroll < 1. One rr() draw per bet."""
    b = B0
    target = MART_BASE
    bets = 0
    won = 0
    lost = 0
    nw = 0
    while bets < CASUAL_BETS and b:
        if ptype == 0:
            s = b * num // 100
            if s < 1:
                s = 1
        elif ptype == 1:
            s = C_STAKE
        else:
            s = target
        if s > maxbet:
            s = maxbet
        if s > b:
            s = b
        bets += 1
        if rr() < p:
            gain = s * k
            b += gain
            won += gain
            nw += 1
            target = MART_BASE
        else:
            b -= s
            lost += s
            target = target + target
            if target > maxbet:
                target = maxbet
    return b, bets, won, lost, nw


def play_grinder(rr, p, k, maxbet, ptype, num):
    """One grinder session: to >= 2000 or <= 500, hard cap 4000 bets."""
    b = B0
    target = MART_BASE
    bets = 0
    won = 0
    lost = 0
    nw = 0
    while GRIND_LO < b < GRIND_HI and bets < GRIND_CAP:
        if ptype == 0:
            s = b * num // 100
            if s < 1:
                s = 1
        elif ptype == 1:
            s = C_STAKE
        else:
            s = target
        if s > maxbet:
            s = maxbet
        if s > b:
            s = b
        bets += 1
        if rr() < p:
            gain = s * k
            b += gain
            won += gain
            nw += 1
            target = MART_BASE
        else:
            b -= s
            lost += s
            target = target + target
            if target > maxbet:
                target = maxbet
    if b >= GRIND_HI:
        out = 2  # double
    elif b <= GRIND_LO:
        out = 0  # half
    else:
        out = 1  # cap-hit
    return b, bets, won, lost, nw, out


def play_compulsive(rr, p, k, maxbet, ptype, num):
    """One compulsive session (C policy): to ruin or 20,000 bets."""
    b = B0
    bets = 0
    won = 0
    lost = 0
    nw = 0
    while b and bets < COMP_CAP:
        s = C_STAKE
        if s > maxbet:
            s = maxbet
        if s > b:
            s = b
        bets += 1
        if rr() < p:
            gain = s * k
            b += gain
            won += gain
            nw += 1
        else:
            b -= s
            lost += s
    return b, bets, won, lost, nw


# ------------------------------------------------ twin (independent re-impl.)
def twin_session(draws, pf, k, maxbet, pname, profile):
    """Independently structured replay: dict state, name-keyed policy dispatch,
    per-bet stake-bound assertions. Consumes exactly the recorded draws.
    Returns (final, bets, checks_passed) and must match the main kernel."""
    st = {"bank": B0, "mart": MART_BASE, "bets": 0}
    frac = {"F-0.01": 1, "F-0.05": 5, "F-0.10": 10}
    local_checks = 0

    def raw_stake():
        if pname in frac:
            return max(1, st["bank"] * frac[pname] // 100)
        if pname == "C":
            return C_STAKE
        if pname == "REF":
            return REF_STAKE
        return st["mart"]

    def keep_going():
        if profile == "casual":
            return st["bets"] < CASUAL_BETS and st["bank"] >= 1
        if profile == "grinder":
            return GRIND_LO < st["bank"] < GRIND_HI and st["bets"] < GRIND_CAP
        return st["bank"] >= 1 and st["bets"] < COMP_CAP  # compulsive

    it = iter(draws)
    while keep_going():
        s = min(raw_stake(), maxbet, st["bank"])
        assert MIN_STAKE <= s <= maxbet, "twin stake in [1, MAXBET]"
        assert s <= st["bank"], "twin stake <= bankroll"
        local_checks += 2
        won = next(it) < pf
        st["bets"] += 1
        if won:
            st["bank"] += s * k
            st["mart"] = MART_BASE
        else:
            st["bank"] -= s
            st["mart"] = min(2 * st["mart"], maxbet)
    leftovers = sum(1 for _ in it)
    assert leftovers == 0, "twin consumed every recorded draw"
    local_checks += 1
    return st["bank"], st["bets"], local_checks


# ------------------------------------------------------------ hand-derived pins
def run_pins():
    for pin in FIX["hand_derived_pins"]:
        draws = list(pin["draws"])
        exp = pin["expect"]
        if pin["name"].startswith("pin-1"):
            pf = float((1 - Fraction(1, 20)) / 2)
            it = iter(draws)
            b, bets, won, lost, nw = play_casual(lambda: next(it), pf, 1, 1000, 2, 0)
            ck(b == exp["final"] and bets == exp["bets"], "pin-1 main kernel")
            ck((b > B0) == exp["ahead"] and (b <= WIPE_LINE) == exp["wipe"],
               "pin-1 classification")
            tb, tbets, tc = twin_session(draws, pf, 1, 1000, "M", "casual")
            ck(tb == exp["final"] and tbets == exp["bets"], "pin-1 twin")
            ckn(tc)
        else:
            pf = float((1 - Fraction(1, 10)) / 20)
            it = iter(draws)
            b, bets, won, lost, nw, out = play_grinder(lambda: next(it), pf, 19, 50, 0, 10)
            ck(b == exp["final"] and bets == exp["bets"], "pin-2 main kernel")
            ck({"double": 2, "half": 0}[exp["outcome"]] == (2 if b >= GRIND_HI else 0),
               "pin-2 outcome")
            tb, tbets, tc = twin_session(draws, pf, 19, 50, "F-0.10", "grinder")
            ck(tb == exp["final"] and tbets == exp["bets"], "pin-2 twin")
            ckn(tc)


run_pins()

# ------------------------------------------------------------------ full sweep


def sweep(seed, mc, mg, mp):
    """One full Arm-S sweep in the pinned loop order. Returns (counts, traces,
    total_bets, first_draw, sentinel)."""
    rng = random.Random(seed)
    rr = rng.random
    counts = {}
    traces = []
    total_bets = 0
    first_draw = [None]

    def make_recorder(store):
        def rec():
            v = rr()
            store.append(v)
            return v
        return rec

    for gname, k in GS:
        for e in E_ALL:
            pf = float((1 - e) / (k + 1))
            for maxbet in MAXBETS:
                for pname, ptype, num in POLICIES:
                    key = (gname, str(e), maxbet, pname)
                    # ---- casual
                    aheads = wipes = 0
                    fin_sum = 0
                    leg_bets = 0
                    leg_wins = 0
                    local = 0
                    for rep in range(mc):
                        if rep == 0 or rep == mc // 2:
                            store = []
                            b, bets, won, lost, nw = play_casual(
                                make_recorder(store), pf, k, maxbet, ptype, num)
                            traces.append((store, pf, k, maxbet, pname,
                                           "casual", b, bets))
                        else:
                            b, bets, won, lost, nw = play_casual(
                                rr, pf, k, maxbet, ptype, num)
                        if first_draw[0] is None:
                            first_draw[0] = traces[0][0][0]
                        assert b == B0 + won - lost, "casual conservation"
                        assert bets <= CASUAL_BETS and (bets == CASUAL_BETS or b == 0), \
                            "casual stop validity"
                        local += 2
                        total_bets += bets
                        leg_bets += bets
                        leg_wins += nw
                        if b > B0:
                            aheads += 1
                        if b <= WIPE_LINE:
                            wipes += 1
                        fin_sum += b
                    ckn(local)
                    # ---- grinder
                    doubles = halves = caps = 0
                    gb_sum = 0
                    gleg_wins = 0
                    local = 0
                    for rep in range(mg):
                        if rep == 0 or rep == mg // 2:
                            store = []
                            b, bets, won, lost, nw, out = play_grinder(
                                make_recorder(store), pf, k, maxbet, ptype, num)
                            traces.append((store, pf, k, maxbet, pname,
                                           "grinder", b, bets))
                        else:
                            b, bets, won, lost, nw, out = play_grinder(
                                rr, pf, k, maxbet, ptype, num)
                        assert b == B0 + won - lost, "grinder conservation"
                        assert (out == 2) == (b >= GRIND_HI) and \
                               (out == 0) == (b <= GRIND_LO) and \
                               (out == 1) == (GRIND_LO < b < GRIND_HI), \
                            "grinder outcome classification"
                        local += 2
                        if gname == "G1" and pname == "C" and out != 1:
                            assert b in (GRIND_LO, GRIND_HI), \
                                "G1xC exact boundary hit (unit steps of 50)"
                            local += 1
                        total_bets += bets
                        gb_sum += bets
                        gleg_wins += nw
                        if out == 2:
                            doubles += 1
                        elif out == 0:
                            halves += 1
                        else:
                            caps += 1
                    ckn(local)
                    # ---- compulsive (C policy only)
                    comp = None
                    if pname == "C":
                        ruins = 0
                        durations = []
                        cleg_bets = 0
                        cleg_wins = 0
                        local = 0
                        for rep in range(mp):
                            if rep == 0 or rep == mp // 2:
                                store = []
                                b, bets, won, lost, nw = play_compulsive(
                                    make_recorder(store), pf, k, maxbet, ptype, num)
                                traces.append((store, pf, k, maxbet, pname,
                                               "compulsive", b, bets))
                            else:
                                b, bets, won, lost, nw = play_compulsive(
                                    rr, pf, k, maxbet, ptype, num)
                            assert b == B0 + won - lost, "compulsive conservation"
                            assert (b == 0) or bets == COMP_CAP, "compulsive stop"
                            local += 2
                            total_bets += bets
                            cleg_bets += bets
                            cleg_wins += nw
                            if b == 0:
                                ruins += 1
                                durations.append(bets)
                            else:
                                durations.append(None)  # censored
                        ckn(local)
                        durations.sort(key=lambda d: (d is None, d))
                        lo_mid = durations[mp // 2 - 1]
                        hi_mid = durations[mp // 2]
                        if lo_mid is None or hi_mid is None:
                            med = ">%d" % COMP_CAP
                        else:
                            med = (lo_mid + hi_mid) / 2
                        comp = {"ruins": ruins, "median_bets_to_ruin": med,
                                "bets": cleg_bets, "wins": cleg_wins, "M": mp}
                    counts[key] = {
                        "casual": {"aheads": aheads, "wipes": wipes,
                                   "fin_sum": fin_sum, "bets": leg_bets,
                                   "wins": leg_wins, "M": mc},
                        "grinder": {"doubles": doubles, "halves": halves,
                                    "caps": caps, "bets_sum": gb_sum,
                                    "wins": gleg_wins, "M": mg},
                        "compulsive": comp,
                    }
    sentinel = rr()
    return counts, traces, total_bets, first_draw[0], sentinel


def verify_stream(seed, total_bets, first_draw, sentinel, label):
    probe = random.Random(seed)
    ck(probe.random() == first_draw, "first draw re-derived from fresh Random (%s)" % label)
    replay = random.Random(seed)
    rrr = replay.random
    for _ in range(total_bets):
        rrr()
    ck(rrr() == sentinel,
       "draw-count accounting: draws consumed == bets simulated (%s)" % label)


def verify_traces(traces, label):
    n = 0
    for store, pf, k, maxbet, pname, profile, b, bets in traces:
        tb, tbets, tc = twin_session(store, pf, k, maxbet, pname, profile)
        assert tb == b and tbets == bets, "twin trace-replay agrees (%s)" % label
        n += tc + 1
    ckn(n)
    return len(traces)


# --------------------------------------------------------- run both Arm-S legs
PRIMARY = sweep(SEED_PRIMARY, M_CASUAL, M_GRINDER, M_COMPULSIVE)
STABILITY = sweep(SEED_STABILITY, M_CASUAL // 2, M_GRINDER // 2, M_COMPULSIVE // 2)
verify_stream(SEED_PRIMARY, PRIMARY[2], PRIMARY[3], PRIMARY[4], "primary")
verify_stream(SEED_STABILITY, STABILITY[2], STABILITY[3], STABILITY[4], "stability")
N_TRACES = verify_traces(PRIMARY[1], "primary") + verify_traces(STABILITY[1], "stability")

# --------------------------------------------- aux self-check: reference-leg MC
AUX = {}
aux_rng = random.Random(SEED_AUX)
aux_rr = aux_rng.random
for gname, k in GS:
    for e in E_ALL:
        pf = float((1 - e) / (k + 1))
        aheads = 0
        local = 0
        for _ in range(M_CASUAL):
            wins = 0
            b = B0
            for _ in range(CASUAL_BETS):
                # reference policy: constant stake 10, never clipped
                # (bankroll >= 10 before every bet — cannot ruin mid-path)
                assert b >= REF_STAKE, "reference leg cannot ruin mid-path"
                if aux_rr() < pf:
                    b += REF_STAKE * k
                    wins += 1
                else:
                    b -= REF_STAKE
            assert (b > B0) == (wins * (k + 1) > 100), \
                "reference ahead iff wins*(k+1) > 100"
            local += CASUAL_BETS + 1
            if b > B0:
                aheads += 1
        ckn(local)
        exact = ARM_A_FUN[(gname, e)]
        se = math.sqrt(float(exact * (1 - exact)) / M_CASUAL)
        dev = abs(aheads / M_CASUAL - float(exact))
        ck(dev <= 4 * se + 1e-12,
           "aux reference MC within 4 SE of exact binomial (%s e=%s)" % (gname, e))
        AUX[(gname, str(e))] = {"mc": aheads / M_CASUAL, "exact": float(exact),
                                "dev": dev}

# --------------------------------------------------------------- e=0 fairness
# Win-indicator martingale (Wald): |wins - p*bets| <= 4*sqrt(bets*p*(1-p)) per
# e=0 leg; chip-level fairness E[final] = B0 then follows analytically from
# the exact EV identity + per-replication conservation (fixtures disclosure 8).
for counts, label in ((PRIMARY[0], "primary"), (STABILITY[0], "stability")):
    for gname, k in GS:
        p0 = 1.0 / (k + 1)
        for maxbet in MAXBETS:
            for pname, _, _ in POLICIES:
                cell = counts[(gname, "0", maxbet, pname)]
                profs = [("casual", cell["casual"]), ("grinder", cell["grinder"])]
                if cell["compulsive"] is not None:
                    profs.append(("compulsive", cell["compulsive"]))
                for prof, c in profs:
                    nb = c.get("bets", c.get("bets_sum"))
                    dev = abs(c["wins"] - p0 * nb)
                    tol = 4 * math.sqrt(nb * p0 * (1 - p0))
                    ck(dev <= tol,
                       "e=0 win-martingale fair (%s %s %s m=%d %s)"
                       % (label, gname, pname, maxbet, prof))

# ------------------------------------------------------------- agreement gate
GATE = {"per_edge": {}, "per_cap": {}, "pass": True}
for e in E_ALL:
    exact = ARM_A_RUIN[e]
    pooled_doubles = 0
    pooled_m = 0
    for maxbet in MAXBETS:
        c = PRIMARY[0][("G1", str(e), maxbet, "C")]["grinder"]
        pooled_doubles += c["doubles"]
        pooled_m += c["M"]
        dev_cap = abs(Fraction(c["doubles"], c["M"]) - exact)
        GATE["per_cap"]["e=%s|m=%d" % (e, maxbet)] = float(dev_cap)
    dev = abs(Fraction(pooled_doubles, pooled_m) - exact)
    ok = dev <= GATE_PP
    GATE["per_edge"]["e=%s" % e] = {"pooled_mc": pooled_doubles / pooled_m,
                                    "exact": float(exact), "dev_pp": float(dev) * 100,
                                    "pass": ok}
    ck(ok, "agreement gate (pooled, e=%s): |MC - exact| <= 1.0 pp" % e)
    if not ok:
        GATE["pass"] = False

# ------------------------------------------------------------------- decisions


def envelope_and_ruling(counts, mc, mg):
    """Evaluator #1: envelope sets + pre-registered ruling."""
    env = {}
    env_det = {}
    indet = {}
    for gname, k in GS:
        for mi, maxbet in enumerate(MAXBETS):
            passing = []
            det_passing = []
            indet_cells = []
            for e in E_GRID:
                fun_ok = ARM_A_FUN[(gname, e)] >= FUN_BAND
                safe_ok = True
                sink_ok = True
                determinate = True
                for pname, _, _ in POLICIES:
                    cell = counts[(gname, str(e), maxbet, pname)]
                    if 20 * cell["casual"]["wipes"] > mc:
                        safe_ok = False
                    if 10 * cell["grinder"]["doubles"] > mg:
                        sink_ok = False
                    if 100 * cell["grinder"]["caps"] > mg:
                        determinate = False
                if not determinate:
                    indet_cells.append(str(e))
                if fun_ok and safe_ok and sink_ok:
                    passing.append(str(e))
                    if determinate:
                        det_passing.append(str(e))
            env[(gname, mi)] = passing
            env_det[(gname, mi)] = det_passing
            indet[(gname, mi)] = indet_cells
    # REJECT first (pre-registered order)
    empty_gs = [g for g, _ in GS
                if all(not env[(g, mi)] for mi in range(3))]
    if len(empty_gs) >= 2:
        ruling = "REJECT"
        detail = "E* empty at every cap in %d/3 archetypes (%s)" % (
            len(empty_gs), ",".join(empty_gs))
    else:
        # APPROVE: some cap m* with >= 2 consecutive shared edges (determinate)
        band = None
        for mi in range(3):
            shared = set(env_det[("G1", mi)]) & set(env_det[("G2", mi)]) \
                & set(env_det[("G3", mi)])
            idx = sorted(E_GRID.index(Fraction(s)) for s in shared)
            for a, bb in zip(idx, idx[1:]):
                if bb == a + 1:
                    band = (mi, str(E_GRID[a]), str(E_GRID[bb]))
                    break
            if band:
                break
        if band:
            ruling = "APPROVE"
            detail = "shared band at m=%s: edges %s..%s" % (
                float(M_GRID[band[0]]), band[1], band[2])
        else:
            ruling = "NULL"
            detail = "neither REJECT nor APPROVE binds"
    return env, env_det, indet, ruling, detail, empty_gs


def ruling_second_opinion(counts, mc, mg):
    """Evaluator #2 (independently written): pure integer arithmetic, different
    traversal, no shared code with evaluator #1."""
    passes = {}
    for mi in (0, 1, 2):
        for g in ("G1", "G2", "G3"):
            k = {"G1": 1, "G2": 5, "G3": 19}[g]
            row = []
            for ei in (0, 1, 2, 3):
                e = E_GRID[ei]
                tail = ARM_A_FUN[(g, e)]
                good = tail.numerator * 4 >= tail.denominator  # tail >= 1/4
                worst_wipe = max(counts[(g, str(e), MAXBETS[mi], pn)]
                                 ["casual"]["wipes"] for pn, _, _ in POLICIES)
                worst_dbl = max(counts[(g, str(e), MAXBETS[mi], pn)]
                                ["grinder"]["doubles"] for pn, _, _ in POLICIES)
                worst_cap = max(counts[(g, str(e), MAXBETS[mi], pn)]
                                ["grinder"]["caps"] for pn, _, _ in POLICIES)
                good = good and worst_wipe * 20 <= mc and worst_dbl * 10 <= mg
                row.append((good, worst_cap * 100 <= mg))
            passes[(g, mi)] = row
    n_empty = 0
    for g in ("G1", "G2", "G3"):
        if not any(passes[(g, mi)][ei][0] for mi in (0, 1, 2) for ei in (0, 1, 2, 3)):
            n_empty += 1
    if n_empty >= 2:
        return "REJECT", passes
    for mi in (0, 1, 2):
        for ei in (0, 1, 2):
            if all(passes[(g, mi)][ei][0] and passes[(g, mi)][ei][1]
                   and passes[(g, mi)][ei + 1][0] and passes[(g, mi)][ei + 1][1]
                   for g in ("G1", "G2", "G3")):
                return "APPROVE", passes
    return "NULL", passes


ENV_P, ENVD_P, INDET_P, RULING_P, DETAIL_P, EMPTY_P = envelope_and_ruling(
    PRIMARY[0], M_CASUAL, M_GRINDER)
ENV_S, ENVD_S, INDET_S, RULING_S, DETAIL_S, EMPTY_S = envelope_and_ruling(
    STABILITY[0], M_CASUAL // 2, M_GRINDER // 2)
R2_P, PASSMAP_P = ruling_second_opinion(PRIMARY[0], M_CASUAL, M_GRINDER)
R2_S, _ = ruling_second_opinion(STABILITY[0], M_CASUAL // 2, M_GRINDER // 2)
ck(R2_P == RULING_P, "twin decision evaluators agree (primary)")
ck(R2_S == RULING_S, "twin decision evaluators agree (stability)")
for g, _ in GS:
    for mi in range(3):
        row = PASSMAP_P[(g, mi)]
        ck([str(E_GRID[ei]) for ei in range(4) if row[ei][0]] == ENV_P[(g, mi)],
           "evaluators agree on envelope set (%s, m=%s)" % (g, float(M_GRID[mi])))

# G1 C-leg band-side robustness: replace the noisy MC C-leg with Arm A exact
# for the SINK reading on G1 and confirm no envelope membership flips.
CLEG_FLIPS = []
for mi, maxbet in enumerate(MAXBETS):
    for e in E_GRID:
        mc_side = 10 * PRIMARY[0][("G1", str(e), maxbet, "C")]["grinder"]["doubles"] \
            <= M_GRINDER
        exact_side = ARM_A_RUIN[e] <= SINK_BAND
        if mc_side != exact_side:
            CLEG_FLIPS.append("e=%s|m=%d" % (e, maxbet))
ck(not CLEG_FLIPS or RULING_P != "APPROVE",
   "C-leg MC-vs-exact band side cannot silently carry an APPROVE")

# stability must reproduce the ruling (pre-registered)
STAB_OK = RULING_S == RULING_P
ck(STAB_OK, "stability leg reproduces the ruling")

FINAL = RULING_P if (GATE["pass"] and STAB_OK) else \
    ("INVALID (agreement gate failed)" if not GATE["pass"] else "NULL")
if not STAB_OK and GATE["pass"]:
    DETAIL_P += " — DEGRADED TO NULL: stability leg ruled %s" % RULING_S

# ---------------------------------------------------- REJECT gap quantification
GAP = {}
for gname, k in GS:
    for mi, maxbet in enumerate(MAXBETS):
        found = None
        for e in E_GRID:
            worst_dbl = max(PRIMARY[0][(gname, str(e), maxbet, pn)]
                            ["grinder"]["doubles"] for pn, _, _ in POLICIES)
            if worst_dbl * 10 <= M_GRINDER:
                found = e
                break
        GAP["%s|m=%s" % (gname, float(M_GRID[mi]))] = (
            {"smallest_SINK_passing_e": float(found),
             "FUN_there": float(ARM_A_FUN[(gname, found)])}
            if found is not None else
            {"smallest_SINK_passing_e": None,
             "note": "no edge in the grid passes SINK at this cap"})

# ------------------------------------------------------------ per-axis shares
SHARES = {"by_archetype": {}, "by_edge": {}, "by_cap": {}}
for gname, _ in GS:
    n = sum(1 for mi in range(3) for s in ENV_P[(gname, mi)])
    SHARES["by_archetype"][gname] = n / 12
for ei, e in enumerate(E_GRID):
    n = sum(1 for gname, _ in GS for mi in range(3)
            if str(e) in ENV_P[(gname, mi)])
    SHARES["by_edge"][str(e)] = n / 9
for mi in range(3):
    n = sum(1 for gname, _ in GS for s in ENV_P[(gname, mi)])
    SHARES["by_cap"][str(float(M_GRID[mi]))] = n / 12

# --------------------------------------------------------------------- output
def table(counts, mc, mg):
    out = {}
    for (gname, es, maxbet, pname), cell in sorted(counts.items()):
        key = "%s|e=%s|m=%d|%s" % (gname, es, maxbet, pname)
        cas, gr = cell["casual"], cell["grinder"]
        row = {
            "P_ahead": cas["aheads"] / mc,
            "P_wipe": cas["wipes"] / mc,
            "mean_final_casual": cas["fin_sum"] / mc,
            "P_double": gr["doubles"] / mg,
            "P_half": gr["halves"] / mg,
            "cap_frac": gr["caps"] / mg,
            "mean_bets_grinder": gr["bets_sum"] / mg,
        }
        if cell["compulsive"] is not None:
            row["compulsive_ruin_frac"] = \
                cell["compulsive"]["ruins"] / cell["compulsive"]["M"]
            row["compulsive_median_bets_to_ruin"] = \
                cell["compulsive"]["median_bets_to_ruin"]
        out[key] = row
    return out


RESULTS = {
    "meta": {
        "python": "cpython-%d.%d" % sys.version_info[:2],
        "seeds": {"primary": SEED_PRIMARY, "stability": SEED_STABILITY,
                  "aux_self_check": SEED_AUX},
        "M": {"casual": M_CASUAL, "grinder": M_GRINDER,
              "compulsive": M_COMPULSIVE, "stability": "half of each"},
        "total_bets": {"primary": PRIMARY[2], "stability": STABILITY[2]},
        "traces_replayed": N_TRACES,
    },
    "arm_a": {
        "fun_exact": {"%s|e=%s" % (g, e): {"fraction": "%d/%d" % (
            ARM_A_FUN[(g, e)].numerator, ARM_A_FUN[(g, e)].denominator),
            "float": float(ARM_A_FUN[(g, e)])}
            for g, _ in GS for e in E_ALL},
        "ruin_exact_G1xC": {"e=%s" % e: {"fraction": "%d/%d" % (
            ARM_A_RUIN[e].numerator, ARM_A_RUIN[e].denominator),
            "float": float(ARM_A_RUIN[e])} for e in E_ALL},
        "w_min": WMIN,
    },
    "agreement_gate": GATE,
    "aux_reference_mc": {k2: v for k2, v in
                         sorted(("%s|e=%s" % (g, e), AUX[(g, e)])
                                for (g, e) in AUX)},
    "primary": {
        "table": table(PRIMARY[0], M_CASUAL, M_GRINDER),
        "envelope": {"%s|m=%s" % (g, float(M_GRID[mi])): ENV_P[(g, mi)]
                     for g, _ in GS for mi in range(3)},
        "envelope_determinate": {"%s|m=%s" % (g, float(M_GRID[mi])):
                                 ENVD_P[(g, mi)]
                                 for g, _ in GS for mi in range(3)},
        "indeterminate_cells": {"%s|m=%s" % (g, float(M_GRID[mi])):
                                INDET_P[(g, mi)]
                                for g, _ in GS for mi in range(3)},
        "empty_archetypes": EMPTY_P,
        "ruling": RULING_P,
        "detail": DETAIL_P,
    },
    "stability": {
        "table": table(STABILITY[0], M_CASUAL // 2, M_GRINDER // 2),
        "envelope": {"%s|m=%s" % (g, float(M_GRID[mi])): ENV_S[(g, mi)]
                     for g, _ in GS for mi in range(3)},
        "empty_archetypes": EMPTY_S,
        "ruling": RULING_S,
    },
    "reject_gap_quantification": GAP,
    "per_axis_envelope_shares": SHARES,
    "c_leg_band_side_flips_G1": CLEG_FLIPS,
    "pvp_rake_identity": "even-money PvP with pot-rake r is G1 at e = r for "
                         "each symmetric player (analytic identity; the G1 row "
                         "prices the rake lane directly, no extra sim)",
    "final_ruling": FINAL,
    "self_checks": {"passed": None, "failed": None},  # filled below
}

RESULTS["self_checks"]["passed"] = CHECKS
RESULTS["self_checks"]["failed"] = len(FAILS)

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")

print("VERDICT 022 — casino fairness envelope (PROPOSAL 020)")
print("arm A exact FUN (reference leg, P_ahead):")
for g, _ in GS:
    print("  %s: %s" % (g, "  ".join("e=%s %.4f" % (e, float(ARM_A_FUN[(g, e)]))
                                     for e in E_ALL)))
print("arm A exact G1xC P_double: %s" %
      "  ".join("e=%s %.4f" % (e, float(ARM_A_RUIN[e])) for e in E_ALL))
print("agreement gate (pooled per edge, 1.0 pp): %s" %
      ("PASS" if GATE["pass"] else "FAIL"))
for k2 in sorted(GATE["per_edge"]):
    v = GATE["per_edge"][k2]
    print("  %s: MC %.4f vs exact %.4f (dev %.3f pp) %s" %
          (k2, v["pooled_mc"], v["exact"], v["dev_pp"],
           "ok" if v["pass"] else "FAIL"))
print("envelope E*(g, m) on the 4-edge grid (measured, primary):")
for g, _ in GS:
    for mi in range(3):
        print("  %s m=%s: {%s}%s" % (
            g, float(M_GRID[mi]), ", ".join(ENV_P[(g, mi)]) or "",
            " indeterminate:{%s}" % ", ".join(INDET_P[(g, mi)])
            if INDET_P[(g, mi)] else ""))
print("empty archetypes (E* empty at every cap): %s" % (EMPTY_P or "none"))
print("primary ruling: %s (%s)" % (RULING_P, DETAIL_P))
print("stability ruling (seed %d, half M): %s" % (SEED_STABILITY, RULING_S))
print("FINAL RULING: %s" % FINAL)
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS, len(FAILS)))
for f in FAILS:
    print("  FAILED: %s" % f)
sys.exit(0 if not FAILS else 1)
