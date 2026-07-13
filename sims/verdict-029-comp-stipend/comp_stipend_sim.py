#!/usr/bin/env python3
"""verdict-029 — comp/stipend envelope: the LAST routed lever (idea-engine
PROPOSAL 027).

Fully hermetic NUMERIC SIMULATION (method ladder rung 1): reads exactly ONE
file (its own committed fixtures.json pre-registration), touches no repo
state, no network, no wall clock (timing goes to stderr only, never into
stdout or results.json).

Dual-arm design per the pre-registration:
  Arm A — analytic, seedless, exact rationals: comp-shifted FUN for ALL 52
          cells (T1 binomial via math.comb; T2 exact integer-support DP
          convolution), exact casual-R1 wipe and E[session net incl. comp]
          per cell, the sigma=0 baseline Fractions REQUIRED to equal
          V022/V025's committed values by exact rational equality, the
          D1==D2 and D3==baseline FUN identities, the (sigma-t)*B0 farmer
          pump line, the exact banded-Fraction D3 stopper DP on T1 (with the
          b=1 variants cross-checked against the two-boundary gambler's-ruin
          closed form), V025's three-derivation T1xR1 baseline grinder ruin
          machinery, and the t=0 P_double = 1/3 optional-stopping control.
  Arm S — seeded MC: random.Random(20260752) primary / 20260753 stability
          (half M) / 20260754 reporting (t=0 control, compulsive, T3
          monotonicity spot cell, aggregated-draw spot check) / 20260755 aux
          (gate re-measures + the aggregation twin); pinned loop order, one
          rng.random() per ticket.

Decision rule (registered in the idea file BEFORE any code; evaluated in
this order): REJECT / APPROVE / NULL — see fixtures.json
process.decision_rule_evaluated_in_this_order.

Run:  python3 sims/verdict-029-comp-stipend/comp_stipend_sim.py
Exit 0 iff every self-check passes. stdout + results.json byte-identical
across process runs (verified externally by diff of two complete runs).
"""

import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(os.path.join(HERE, "fixtures.json")))

# ----------------------------------------------------------------- self-checks
N_CHECKS = 0
FAILED = []


def check(cond, msg):
    global N_CHECKS
    N_CHECKS += 1
    if not cond:
        FAILED.append(msg)
        print("SELF-CHECK FAILED: %s" % msg, file=sys.stderr)


def bulk_checks(n):
    """Register n passed checks counted in a hot loop."""
    global N_CHECKS
    N_CHECKS += n


def note(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()


# ----------------------------------------------------------------- constants
check(sys.version_info[:2] == (3, 11),
      "CPython minor pinned: 3.11 required, got %s" % (sys.version_info[:2],))

# centi-units: 1 cu = F/100 = 0.1 chip. B0 = 10000 cu, F = 100 cu.
B0C = 10000
FC = 100
WIPEC = 1000          # 0.1 * B0
GLOW = 5000           # grinder wealth lower band (0.5 * B0)
GHI = 20000           # grinder wealth upper band (2 * B0)
BIG = 1 << 60

SHAPES = ["T1", "T2"]
PRIZES = {"T1": [2], "T2": [8, 3, 1], "T3": [25, 5]}
BASE_P = {"T1": [Fraction(1, 2)],
          "T2": [Fraction(1, 20), Fraction(1, 10), Fraction(3, 10)],
          "T3": [Fraction(3, 125), Fraction(2, 25)]}
BASE_P_FLOAT = {"T1": [0.5], "T2": [0.05, 0.10, 0.30], "T3": [0.024, 0.08]}
VAR_T0 = {"T1": 1.0, "T2": 3.4, "T3": 16.0}

T_DEC = [0.05, 0.1]
T_EXACT = {0.0: Fraction(0), 0.05: Fraction(1, 20), 0.1: Fraction(1, 10)}
SIGMAS = [0.02, 0.05, 0.1, 0.2]
SIG_EXACT = {0.02: Fraction(1, 50), 0.05: Fraction(1, 20),
             0.1: Fraction(1, 10), 0.2: Fraction(1, 5)}
SIG_SHIFT_U = {0.02: 2, 0.05: 5, 0.1: 10, 0.2: 20}     # sigma*B0 in F-units
RHOS = [0.2, 0.4, 0.6, 0.8]
RHO_EXACT = {0.2: Fraction(1, 5), 0.4: Fraction(2, 5),
             0.6: Fraction(3, 5), 0.8: Fraction(4, 5)}
RHO5 = {0.2: 1, 0.4: 2, 0.6: 3, 0.8: 4}
POLICIES = ["R1", "R5", "RG", "MC"]
VARIANTS = [(b, tau, phi) for b in (1, 5) for tau in (110, 125, 150)
            for phi in (0, 50)]           # pinned: b asc, tau asc, phi asc

M_CASUAL = FIX["constants"]["M_casual"]
M_GRINDER = FIX["constants"]["M_grinder"]
M_COMPULSIVE = FIX["constants"]["M_compulsive"]
M_WASH = FIX["constants"]["M_wash"]
M_CAPCH = FIX["constants"]["M_capchaser"]
M_STOP = FIX["constants"]["M_stopper"]
SEED_PRIMARY = FIX["constants"]["seed_primary"]
SEED_STABILITY = FIX["constants"]["seed_stability"]
SEED_REPORTING = FIX["constants"]["seed_reporting"]
SEED_AUX = FIX["constants"]["seed_aux"]

check((M_CASUAL, M_GRINDER, M_COMPULSIVE, M_WASH, M_CAPCH, M_STOP) ==
      (5000, 2000, 500, 5000, 2000, 4000), "fixture M constants")
check((SEED_PRIMARY, SEED_STABILITY, SEED_REPORTING, SEED_AUX) ==
      (20260752, 20260753, 20260754, 20260755), "fixture seeds")
check(FIX["constants"]["B0"] == 1000 and FIX["constants"]["F"] == 10, "B0/F")
check(FIX["constants"]["cap_c"] == 5, "cap c = 5 fixed")
check([float(x) for x in FIX["constants"]["t_grid"]] == T_DEC, "t grid")
check(FIX["constants"]["sigma_grid"] == SIGMAS, "sigma grid")
check(FIX["constants"]["rho_grid"] == RHOS, "rho grid")

# fixture cross-check: E[prize] = (1-t)*F exactly, per (shape, t); variances
for g in ("T1", "T2", "T3"):
    fkey = g if g != "T3" else "T3_reporting_only"
    fx = FIX["constants"]["prize_schedules"][fkey]
    check(fx["prizes_units"] == PRIZES[g], "prize units %s" % g)
    check([Fraction(s) for s in fx["base_probs_exact"]] == BASE_P[g],
          "base probs %s" % g)
    for t in (0.0, 0.05, 0.1):
        tf = T_EXACT[t]
        ev = sum((1 - tf) * q * pz for q, pz in zip(BASE_P[g], PRIZES[g]))
        check(ev == (1 - tf) * 1, "E[prize] = (1-t)*F exact: %s t=%s" % (g, t))
    m2 = sum(q * pz * pz for q, pz in zip(BASE_P[g], PRIZES[g]))
    check(m2 - 1 == Fraction(str(fx["per_ticket_variance_at_t0_units2"])),
          "t=0 per-ticket variance %s" % g)

# design/size combos per (shape, t): baseline + 12 decision cells
DCOMBOS = ([("D1", s) for s in SIGMAS] + [("D2", s) for s in SIGMAS] +
           [("D3", r) for r in RHOS])


def cell_key(g, t, design, size):
    if design == "BASE":
        return "%s|t=%s|BASE" % (g, t)
    return "%s|t=%s|%s|%s" % (g, t, design, size)


def thresholds(g, t):
    out = []
    acc = 0.0
    for q in BASE_P_FLOAT[g]:
        acc += (1.0 - t) * q
        out.append(acc)
    return tuple(out)


# ================================================================= ARM A
note("[arm A] exact analytic arm ...")


def t1_binom_dist(tf):
    """Exact distribution of net units s = 2W - 100, W ~ Bin(100, (1-t)/2)."""
    p = (1 - tf) / 2
    return {2 * w - 100: Fraction(math.comb(100, w)) * p ** w *
            (1 - p) ** (100 - w) for w in range(101)}


def t2_dp_dist(tf):
    """Exact distribution of net units after 100 R1 rounds on T2."""
    probs = [(1 - tf) * q for q in BASE_P["T2"]]
    miss = 1 - sum(probs)
    outs = [(7, probs[0]), (2, probs[1]), (0, probs[2]), (-1, miss)]
    D = 1
    for _, pr in outs:
        D = D * pr.denominator // math.gcd(D, pr.denominator)
    w = {}
    for net, pr in outs:
        w[net] = w.get(net, 0) + int(pr * D)
    check(sum(w.values()) == D, "T2 round dist mass t=%s" % tf)
    dist = {0: 1}
    for _ in range(100):
        nxt = {}
        for s, num in dist.items():
            for net, wt in w.items():
                nxt[s + net] = nxt.get(s + net, 0) + num * wt
        dist = nxt
    total = D ** 100
    check(sum(dist.values()) == total, "T2 DP mass = 1 t=%s" % tf)
    check(len(dist) <= 2500, "T2 DP support t=%s" % tf)
    return {s: Fraction(n, total) for s, n in dist.items()}


NET_DIST = {}          # (g, t) -> {net units: Fraction}
for t in (0.0, 0.05, 0.1):
    NET_DIST[("T1", t)] = t1_binom_dist(T_EXACT[t])
    NET_DIST[("T2", t)] = t2_dp_dist(T_EXACT[t])

# T1 binomial vs an independent tail derivation (V025's binom_tail form)
for t in (0.0, 0.05, 0.1):
    p = (1 - T_EXACT[t]) / 2
    tail = sum(Fraction(math.comb(100, w)) * p ** w * (1 - p) ** (100 - w)
               for w in range(51, 101))
    frm = sum(pr for s, pr in NET_DIST[("T1", t)].items() if s > 0)
    check(tail == frm, "T1 dist == binomial tail t=%s" % t)


def fun_exact(g, t, design, size):
    """Exact reference-leg P_ahead incl. comp (Fraction)."""
    dist = NET_DIST[(g, t)]
    if design in ("BASE", "D3"):
        return sum(pr for s, pr in dist.items() if s > 0)
    shift = SIG_SHIFT_U[size]
    return sum(pr for s, pr in dist.items() if s > -shift)


def wipe_exact(g, t, design, size):
    """Exact casual-R1 P_wipe incl. comp (Fraction)."""
    dist = NET_DIST[(g, t)]
    if design == "BASE":
        return sum(pr for s, pr in dist.items() if s <= -90)
    if design == "D3":
        return Fraction(0)   # wealth at total ruin = rho*B0 >= 0.2*B0 > 0.1*B0
    shift = SIG_SHIFT_U[size]
    return sum(pr for s, pr in dist.items() if s <= -90 - shift)


def evnet_exact(g, t, design, size):
    """Exact casual-R1 E[session net incl. comp] in F-units (Fraction)."""
    dist = NET_DIST[(g, t)]
    if design == "BASE":
        return sum(pr * s for s, pr in dist.items())
    if design == "D3":
        rho = RHO_EXACT[size]
        return sum(pr * (Fraction(s) + rho * max(-s, 0))
                   for s, pr in dist.items())
    return sum(pr * s for s, pr in dist.items()) + SIG_SHIFT_U[size]


def evvar_exact(g, t, design, size):
    """Exact per-session variance of net incl. comp in F-units^2."""
    dist = NET_DIST[(g, t)]
    if design in ("BASE", "D1", "D2"):
        m1 = sum(pr * s for s, pr in dist.items())
        m2 = sum(pr * s * s for s, pr in dist.items())
        return m2 - m1 * m1        # constant shift leaves variance unchanged
    rho = RHO_EXACT[size]
    m1 = sum(pr * (Fraction(s) + rho * max(-s, 0)) for s, pr in dist.items())
    m2 = sum(pr * (Fraction(s) + rho * max(-s, 0)) ** 2
             for s, pr in dist.items())
    return m2 - m1 * m1


FUN_EXACT = {}
WIPE_EXACT = {}
EVNET_EXACT = {}
EVVAR_EXACT = {}
for g in SHAPES:
    for t in T_DEC:
        for design, size in [("BASE", None)] + DCOMBOS:
            k = cell_key(g, t, design, size)
            FUN_EXACT[k] = fun_exact(g, t, design, size)
            WIPE_EXACT[k] = wipe_exact(g, t, design, size)
            EVNET_EXACT[k] = evnet_exact(g, t, design, size)
            EVVAR_EXACT[k] = evvar_exact(g, t, design, size)

# analytic identities (pre-registered)
for g in SHAPES:
    for t in T_DEC:
        base = FUN_EXACT[cell_key(g, t, "BASE", None)]
        for r in RHOS:
            check(FUN_EXACT[cell_key(g, t, "D3", r)] == base,
                  "IDENTITY: D3-FUN == baseline-FUN %s t=%s rho=%s" % (g, t, r))
        for s in SIGMAS:
            check(FUN_EXACT[cell_key(g, t, "D1", s)] ==
                  FUN_EXACT[cell_key(g, t, "D2", s)],
                  "IDENTITY: D1-FUN == D2-FUN %s t=%s s=%s" % (g, t, s))
            # D1/D2 casual-R1 EV = (sigma - t)*B0 exactly (pump line)
            check(EVNET_EXACT[cell_key(g, t, "D1", s)] ==
                  (SIG_EXACT[s] - T_EXACT[t]) * 100,
                  "IDENTITY: (sigma-t)*B0 casual R1 %s t=%s s=%s" % (g, t, s))
# T1 ahead threshold matches the proposal's own form (wins > 50 - 50*sigma)
for t in T_DEC:
    p = (1 - T_EXACT[t]) / 2
    for s in SIGMAS:
        kmin = next(w for w in range(101)
                    if Fraction(w) > 50 - 50 * SIG_EXACT[s])
        tail = sum(Fraction(math.comb(100, w)) * p ** w * (1 - p) ** (100 - w)
                   for w in range(kmin, 101))
        check(tail == FUN_EXACT[cell_key("T1", t, "D1", s)],
              "T1 shifted threshold form t=%s sigma=%s" % (t, s))

# identity gate: sigma=0 baselines equal the committed parent Fractions
IDG = FIX["identity_gate"]
identity_results = {}
for t, key in ((0.0, "t=0"), (0.05, "t=0.05"), (0.1, "t=0.1")):
    mineT1 = sum(pr for s, pr in NET_DIST[("T1", t)].items() if s > 0)
    parent = Fraction(IDG["parent_committed_T1_fun_exact"][key]["fraction"])
    ok = mineT1 == parent
    check(ok, "IDENTITY GATE: T1 baseline FUN(t=%s) == V022/V025 committed" % t)
    identity_results["T1|%s" % key] = {"equal": ok, "float": float(mineT1)}
    mineT2 = sum(pr for s, pr in NET_DIST[("T2", t)].items() if s > 0)
    parent2 = Fraction(IDG["parent_committed_T2_fun_exact"][key]["fraction"])
    ok2 = mineT2 == parent2
    check(ok2, "IDENTITY GATE: T2 baseline FUN(t=%s) == V025 committed" % t)
    identity_results["T2|%s" % key] = {"equal": ok2, "float": float(mineT2)}
for t, key in ((0.05, "t=0.05"), (0.1, "t=0.1")):
    mine = sum(pr for s, pr in NET_DIST[("T2", t)].items() if s <= -90)
    parent = Fraction(IDG["parent_committed_T2_wipe_exact"][key]["fraction"])
    check(mine == parent, "IDENTITY GATE: T2 baseline wipe(t=%s)" % t)

# ----- baseline T1xR1 grinder ruin machinery (V025's three derivations, reused)
def ruin_closed(tf):
    p = (1 - tf) / 2
    if p == Fraction(1, 2):
        return Fraction(50, 150)
    r = (1 - p) / p
    return (1 - r ** 50) / (1 - r ** 150)


def ruin_elimination(tf):
    p = (1 - tf) / 2
    q = 1 - p
    a_prev, b_prev = Fraction(1), Fraction(0)
    a_pp, b_pp = Fraction(0), Fraction(0)
    for _ in range(1, 150):
        a = (a_prev - q * a_pp) / p
        b = (b_prev - q * b_pp) / p
        a_pp, b_pp = a_prev, b_prev
        a_prev, b_prev = a, b
    h1 = (1 - b_prev) / a_prev
    h_prev2, h_prev1 = Fraction(0), h1
    for _ in range(1, 50):
        h_next = (h_prev1 - q * h_prev2) / p
        h_prev2, h_prev1 = h_prev1, h_next
    return h_prev1


def ruin_capped_dp(t):
    p = (1.0 - t) * 0.5
    q = 1.0 - p
    dist = [0.0] * 151
    dist[50] = 1.0
    up = 0.0
    down = 0.0
    for _ in range(4000):
        nxt = [0.0] * 151
        for s in range(1, 150):
            m = dist[s]
            if m:
                nxt[s + 1] += m * p
                nxt[s - 1] += m * q
        down += nxt[0]
        up += nxt[150]
        nxt[0] = 0.0
        nxt[150] = 0.0
        dist = nxt
    return up, down, math.fsum(dist)


RUIN_UNCAPPED = {}
RUIN_CAPPED = {}
for t in (0.0, 0.05, 0.1):
    tf = T_EXACT[t]
    cf = ruin_closed(tf)
    el = ruin_elimination(tf)
    check(cf == el, "ruin closed form == elimination t=%s" % t)
    parent = Fraction(IDG["parent_committed_ruin_uncapped"]
                      ["t=%s" % (0 if t == 0.0 else t)]["fraction"])
    check(cf == parent, "IDENTITY GATE: uncapped ruin == V025 committed t=%s" % t)
    up, down, alive = ruin_capped_dp(t)
    check(abs(up + down + alive - 1.0) < 1e-12, "capped DP mass t=%s" % t)
    pc = IDG["parent_committed_ruin_capped_p_double"]["t=%s" %
                                                      (0 if t == 0.0 else t)]
    check(up == pc, "IDENTITY GATE: capped DP p_double == V025 committed t=%s" % t)
    RUIN_UNCAPPED[t] = cf
    RUIN_CAPPED[t] = {"p_double": up, "p_half": down, "alive_at_cap": alive}
check(RUIN_UNCAPPED[0.0] == Fraction(1, 3),
      "t=0 control: P_double = 1/3 exactly (optional stopping)")

# ----- D3 stopper: exact exit distribution per T1 variant (banded elimination)
def stopper_exact_T1(tf, b, tau, phi):
    """Exit-state distribution from start 100 units; exact Fractions."""
    p = (1 - tf) / 2
    states = list(range(phi + 1, tau))
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    rows = []
    for s in states:
        bb = min(b, s) if phi == 0 else b
        trans = {idx[s]: Fraction(1)}
        exits = {}
        for w in range(bb + 1):
            pr = Fraction(math.comb(bb, w)) * p ** w * (1 - p) ** (bb - w)
            ns = s + 2 * w - bb
            if ns >= tau or ns <= phi:
                exits[ns] = exits.get(ns, Fraction(0)) + pr
            else:
                trans[idx[ns]] = trans.get(idx[ns], Fraction(0)) - pr
        rows.append((trans, exits))
    for i in range(n):
        trans_i, exits_i = rows[i]
        piv = trans_i[i]
        trans_i = {c: v / piv for c, v in trans_i.items()}
        exits_i = {e: v / piv for e, v in exits_i.items()}
        rows[i] = (trans_i, exits_i)
        for j in range(i + 1, min(i + b + 1, n)):
            trans_j, exits_j = rows[j]
            f = trans_j.get(i)
            if f:
                for c, v in trans_i.items():
                    if c != i:
                        trans_j[c] = trans_j.get(c, Fraction(0)) - f * v
                for e, v in exits_i.items():
                    exits_j[e] = exits_j.get(e, Fraction(0)) - f * v
                del trans_j[i]
    sol = [None] * n
    for i in range(n - 1, -1, -1):
        trans_i, exits_i = rows[i]
        acc = dict(exits_i)
        for c, v in trans_i.items():
            if c > i:
                for e, pe in sol[c].items():
                    acc[e] = acc.get(e, Fraction(0)) - v * pe
        sol[i] = acc
    return sol[idx[100]]


note("[arm A] D3 stopper exact DP (24 chains) ...")
STOP_EXACT = {}     # (t, variant) -> {"exits": dist, "p_tau": Fr,
#                                      "ev": {rho: Fr}, "var": {rho: Fr}}
for t in T_DEC:
    tf = T_EXACT[t]
    for (b, tau, phi) in VARIANTS:
        d = stopper_exact_T1(tf, b, tau, phi)
        check(sum(d.values()) == 1, "stopper DP mass t=%s %s" % (t, (b, tau, phi)))
        if b == 1:
            # independent cross-check: two-boundary gambler's-ruin closed form
            p = (1 - tf) / 2
            r = (1 - p) / p
            a = 100 - phi
            span = tau - phi
            ptau_cf = (1 - r ** a) / (1 - r ** span)
            check(d.get(tau, Fraction(0)) == ptau_cf,
                  "stopper b=1 DP == ruin closed form t=%s %s" % (t, (tau, phi)))
        p_tau = sum(pr for e, pr in d.items() if e >= tau)
        ev = {}
        var = {}
        for r_ in RHOS:
            rho = RHO_EXACT[r_]
            w1 = sum(pr * (Fraction(e) + rho * max(100 - e, 0))
                     for e, pr in d.items())
            w2 = sum(pr * (Fraction(e) + rho * max(100 - e, 0)) ** 2
                     for e, pr in d.items())
            ev[r_] = w1 - 100
            var[r_] = w2 - w1 * w1
        STOP_EXACT[(t, (b, tau, phi))] = {"exits": d, "p_tau": p_tau,
                                          "ev": ev, "var": var}

D3_FARMER_EV_T1 = {}    # (t, rho) -> max exact EV over 12 variants (Fraction)
for t in T_DEC:
    for r_ in RHOS:
        D3_FARMER_EV_T1[(t, r_)] = max(STOP_EXACT[(t, v)]["ev"][r_]
                                       for v in VARIANTS)

note("[arm A] done — identity gate all-equal %s"
     % all(v["equal"] for v in identity_results.values()))


# ================================================================= ARM S kernel
def play(g, rr, ths, pol, mx, lo, hi, reb, rebcap, stip, rho5):
    """One session. Returns (bank_cu, rounds, tickets, prizes_cu, rebate_cu).
    lo/hi: wealth stop bands (lo = -1 disables the wealth stop: casual,
    compulsive). One rng.random() per ticket."""
    bank = 10000
    rounds = tickets = prizes = rebt = 0
    L = 0
    if g == "T1":
        th, = ths
    elif g == "T2":
        c1, c2, c3 = ths
    else:
        c1, c2 = ths
    while rounds < mx and bank >= 100:
        if pol == 0:
            b = 1
        elif pol == 3:
            b = 1 << (L if L < 7 else 7)
            if b > 5:
                b = 5
            u = bank // 100
            if b > u:
                b = u
        else:                       # R5 and RG are both min(5, units) at c=5
            b = bank // 100
            if b > 5:
                b = 5
        pz = 0
        if g == "T1":
            for _ in range(b):
                if rr() < th:
                    pz += 200
        elif g == "T2":
            for _ in range(b):
                u = rr()
                if u < c3:
                    if u < c1:
                        pz += 800
                    elif u < c2:
                        pz += 300
                    else:
                        pz += 100
        else:
            for _ in range(b):
                u = rr()
                if u < c2:
                    pz += 2500 if u < c1 else 500
        stake = 100 * b
        rb = 0
        if reb and rebt < rebcap:
            rb = reb * b
            if rebt + rb > rebcap:
                rb = rebcap - rebt
            rebt += rb
        bank += pz + rb - stake
        rounds += 1
        tickets += b
        prizes += pz
        if pol == 3:
            if pz < stake:
                L += 1
            elif pz > stake:
                L = 0
        if lo >= 0:
            if stip:
                wealth = bank + stip if tickets >= 100 else bank
            elif rho5 and bank < 10000:
                wealth = bank + rho5 * (10000 - bank) // 5
            else:
                wealth = bank
            if wealth >= hi or wealth <= lo:
                break
    return bank, rounds, tickets, prizes, rebt


def play_stopper(g, rr, ths, bmax, tau_cu, phi_cu):
    """D3 stopper farmer walk (rho-invariant; thresholds on bankroll)."""
    bank = 10000
    rounds = tickets = prizes = 0
    if g == "T1":
        th, = ths
    else:
        c1, c2, c3 = ths
    while bank >= 100 and phi_cu < bank < tau_cu and rounds < 200000:
        b = bank // 100
        if b > bmax:
            b = bmax
        pz = 0
        if g == "T1":
            for _ in range(b):
                if rr() < th:
                    pz += 200
        else:
            for _ in range(b):
                u = rr()
                if u < c3:
                    if u < c1:
                        pz += 800
                    elif u < c2:
                        pz += 300
                    else:
                        pz += 100
        bank += pz - 100 * b
        rounds += 1
        tickets += b
        prizes += pz
    return bank, rounds, tickets, prizes


def end_wealth(bank, tickets, stip, rho5):
    if stip:
        return bank + stip if tickets >= 100 else bank
    if rho5 and bank < 10000:
        return bank + rho5 * (10000 - bank) // 5
    return bank


# --------------------------------------------------- independently written twin
def twin_play(draws, g, t, pol_name, profile, design):
    """Independently written twin kernel: consumes a recorded draw list, dict
    state, per-level threshold scan, its own comp/wealth arithmetic."""
    it = iter(draws)
    st = {"bank": 10000, "rounds": 0, "tk": 0, "pz": 0, "rb": 0, "streak": 0}
    lo, hi, mx = profile
    dmode, dsize = design
    scaled = [(1.0 - t) * q for q in BASE_P_FLOAT[g]]
    pzs = [100 * z for z in PRIZES[g]]
    reb = int(SIG_EXACT[dsize] * 10000) // 100 if dmode == "D2" else 0
    rebcap = 2 * int(SIG_EXACT[dsize] * 10000) if dmode == "D2" else 0
    stipend = int(SIG_EXACT[dsize] * 10000) if dmode == "D1" else 0
    r5 = RHO5[dsize] if dmode == "D3" else 0

    def wealth_of():
        w = st["bank"]
        if dmode == "D1" and st["tk"] >= 100:
            w += stipend
        if dmode == "D3" and st["bank"] < 10000:
            w = st["bank"] + r5 * (10000 - st["bank"]) // 5
        return w

    while st["rounds"] < mx and st["bank"] >= 100:
        if pol_name == "R1":
            want = 1
        elif pol_name in ("R5", "RG"):
            want = 5
        else:
            want = 2 ** st["streak"] if st["streak"] < 7 else 128
        n = min(want, 5, st["bank"] // 100)
        got = 0
        for _ in range(n):
            u = next(it)
            acc = 0.0
            prize = 0
            for q, pz in zip(scaled, pzs):
                acc += q
                if u < acc:
                    prize = pz
                    break
            got += prize
        credit = 0
        if reb and st["rb"] < rebcap:
            credit = min(reb * n, rebcap - st["rb"])
            st["rb"] += credit
        st["bank"] += got + credit - 100 * n
        st["rounds"] += 1
        st["tk"] += n
        st["pz"] += got
        if pol_name == "MC":
            if got < 100 * n:
                st["streak"] += 1
            elif got > 100 * n:
                st["streak"] = 0
        if lo >= 0 and not (lo < wealth_of() < hi):
            break
    leftover = sum(1 for _ in it)
    return (st["bank"], st["rounds"], st["tk"], st["pz"], st["rb"], leftover)


def make_tracer(rr, buf):
    def rrt():
        v = rr()
        buf.append(v)
        return v
    return rrt


PROFILE_CASUAL = (-1, BIG, 100)
PROFILE_GRINDER = (GLOW, GHI, 4000)
PROFILE_COMPULSIVE = (-1, BIG, 20000)


# --------------------------------------------------------------- the sweep
def design_params(design, size):
    if design == "D1":
        return (0, 0, int(SIG_EXACT[size] * 10000), 0)
    if design == "D2":
        s_cu = int(SIG_EXACT[size] * 10000)
        return (s_cu // 100, 2 * s_cu, 0, 0)
    if design == "D3":
        return (0, 0, 0, RHO5[size])
    return (0, 0, 0, 0)


def run_leg(seed, mc, mg, mw, mcp, mst, label):
    rng = random.Random(seed)
    rr = rng.random
    expected_first = random.Random(seed).random()
    first_seen = []
    legs = {}
    stoppers = {}
    total_tickets = 0
    n_twin = 0
    for g in SHAPES:
        for t in T_DEC:
            ths = thresholds(g, t)
            for design, size in [("BASE", None)] + DCOMBOS:
                reb, rebcap, stip, rho5 = design_params(design, size)
                ck = cell_key(g, t, design, size)
                cellrec = {}
                for pol_i, pol_name in enumerate(POLICIES):
                    # ---- casual
                    aheads = wipes = 0
                    swealth = 0
                    lt = 0
                    for rep in range(mc):
                        if rep == 0 or rep == mc - 1:
                            buf = []
                            f, rd, tk, pz, rb = play(
                                g, make_tracer(rr, buf), ths, pol_i, 100,
                                -1, BIG, reb, rebcap, stip, rho5)
                            tw = twin_play(buf, g, t, pol_name,
                                           PROFILE_CASUAL, (design, size))
                            check(tw == (f, rd, tk, pz, rb, 0),
                                  "twin replay casual %s %s rep %d"
                                  % (ck, pol_name, rep))
                            if not first_seen:
                                first_seen.append(buf[0])
                            n_twin += 1
                        else:
                            f, rd, tk, pz, rb = play(g, rr, ths, pol_i, 100,
                                                     -1, BIG, reb, rebcap,
                                                     stip, rho5)
                        if f != 10000 + pz + rb - 100 * tk:
                            check(False, "conservation casual %s %s"
                                  % (ck, pol_name))
                        w = end_wealth(f, tk, stip, rho5)
                        if w > 10000:
                            aheads += 1
                        if w <= WIPEC:
                            wipes += 1
                        swealth += w
                        lt += tk
                    bulk_checks(mc)
                    total_tickets += lt
                    cas = {"M": mc, "aheads": aheads, "wipes": wipes,
                           "P_ahead": aheads / mc, "P_wipe": wipes / mc,
                           "sum_wealth_cu": swealth,
                           "net_total_cu": swealth - mc * 10000,
                           "mean_net_frac_B0": (swealth / mc - 10000) / 10000,
                           "tickets": lt}
                    # ---- grinder
                    doubles = halves = stranded = caphits = 0
                    swealth2 = 0
                    srounds = 0
                    lt2 = 0
                    for rep in range(mg):
                        if rep == 0 or rep == mg - 1:
                            buf = []
                            f, rd, tk, pz, rb = play(
                                g, make_tracer(rr, buf), ths, pol_i, 4000,
                                GLOW, GHI, reb, rebcap, stip, rho5)
                            tw = twin_play(buf, g, t, pol_name,
                                           PROFILE_GRINDER, (design, size))
                            check(tw == (f, rd, tk, pz, rb, 0),
                                  "twin replay grinder %s %s rep %d"
                                  % (ck, pol_name, rep))
                            n_twin += 1
                        else:
                            f, rd, tk, pz, rb = play(g, rr, ths, pol_i, 4000,
                                                     GLOW, GHI, reb, rebcap,
                                                     stip, rho5)
                        if f != 10000 + pz + rb - 100 * tk:
                            check(False, "conservation grinder %s %s"
                                  % (ck, pol_name))
                        w = end_wealth(f, tk, stip, rho5)
                        if w >= GHI:
                            doubles += 1
                        elif w <= GLOW:
                            halves += 1
                        elif rd >= 4000:
                            caphits += 1
                        else:
                            stranded += 1
                        swealth2 += w
                        srounds += rd
                        lt2 += tk
                    bulk_checks(mg)
                    total_tickets += lt2
                    gri = {"M": mg, "doubles": doubles, "halves": halves,
                           "stranded": stranded, "caphits": caphits,
                           "P_double": doubles / mg, "P_half": halves / mg,
                           "stranded_frac": stranded / mg,
                           "cap_frac": caphits / mg,
                           "sum_wealth_cu": swealth2,
                           "net_total_cu": swealth2 - mg * 10000,
                           "mean_rounds": srounds / mg, "tickets": lt2}
                    cellrec[pol_name] = {"casual": cas, "grinder": gri}
                # ---- farmer legs (D1 wash / D2 cap-chaser), per size
                if design == "D1":
                    snet = 0
                    lt3 = 0
                    for rep in range(mw):
                        f, rd, tk, pz, rb = play(g, rr, ths, 0, 100, -1, BIG,
                                                 0, 0, stip, 0)
                        if f != 10000 + pz - 100 * tk or rd != 100 or tk != 100:
                            check(False, "wash invariant %s" % ck)
                        snet += f + stip - 10000    # 100 tickets: qualified
                        lt3 += tk
                    bulk_checks(mw)
                    total_tickets += lt3
                    cellrec["farmer_wash"] = {
                        "M": mw, "net_total_cu": snet,
                        "mean_net_frac_B0": snet / mw / 10000, "tickets": lt3}
                if design == "D2":
                    snet = 0
                    lt3 = 0
                    capstops = 0
                    for rep in range(mcp):
                        bank = 10000
                        rounds = tk = pz = rbt = 0
                        th0 = ths[0] if g == "T1" else None
                        while rounds < 2000 and bank >= 100 and rbt < rebcap:
                            prize = 0
                            if g == "T1":
                                if rr() < th0:
                                    prize = 200
                            else:
                                u = rr()
                                if u < ths[2]:
                                    if u < ths[0]:
                                        prize = 800
                                    elif u < ths[1]:
                                        prize = 300
                                    else:
                                        prize = 100
                            credit = min(reb, rebcap - rbt)
                            rbt += credit
                            bank += prize + credit - 100
                            rounds += 1
                            tk += 1
                            pz += prize
                        if bank != 10000 + pz + rbt - 100 * tk:
                            check(False, "cap-chaser conservation %s" % ck)
                        if rbt >= rebcap:
                            capstops += 1
                        snet += bank - 10000
                        lt3 += tk
                    bulk_checks(mcp)
                    total_tickets += lt3
                    cellrec["farmer_capchaser"] = {
                        "M": mcp, "net_total_cu": snet, "cap_stops": capstops,
                        "mean_net_frac_B0": snet / mcp / 10000, "tickets": lt3}
                legs[ck] = cellrec
            # ---- D3 stopper block (rho-invariant walks), per (shape, t)
            for (b, tau, phi) in VARIANTS:
                vk = "%s|t=%s|stopper|b=%d|tau=%d|phi=%d" % (g, t, b, tau, phi)
                succ = 0
                lt4 = 0
                guard = 0
                net_by_rho = {str(r_): 0 for r_ in RHOS}
                for rep in range(mst):
                    f, rd, tk, pz = play_stopper(g, rr, ths, b,
                                                 tau * 100, phi * 100)
                    if f != 10000 + pz - 100 * tk:
                        check(False, "stopper conservation %s" % vk)
                    if rd >= 200000:
                        guard += 1
                    if f >= tau * 100:
                        succ += 1
                    for r_ in RHOS:
                        w = f + RHO5[r_] * (10000 - f) // 5 if f < 10000 else f
                        net_by_rho[str(r_)] += w - 10000
                    lt4 += tk
                bulk_checks(mst)
                check(guard == 0, "stopper guard hits %s" % vk)
                total_tickets += lt4
                stoppers[vk] = {"M": mst, "success": succ,
                                "p_tau": succ / mst,
                                "net_total_cu_by_rho": net_by_rho,
                                "tickets": lt4}
            note("[%s] %s t=%s done (tickets so far %d)"
                 % (label, g, t, total_tickets))
    # stream sentinels
    check(first_seen and first_seen[0] == expected_first,
          "%s: first draw == Random(seed).random()" % label)
    probe = random.Random(seed)
    pr = probe.random
    for _ in range(total_tickets):
        pr()
    check(pr() == rr(), "%s: post-sweep draw-count sentinel (%d draws)"
          % (label, total_tickets))
    return legs, stoppers, total_tickets, n_twin


# --------------------------------------------------------- MINT machinery
def mint_legs(legs, stoppers, g, t, design, size):
    """Enumerate the MINT legs for a cell. Each: (name, Fraction value in
    F-units) — exact-where-covered per fixtures disclosure 3."""
    ck = cell_key(g, t, design, size)
    out = []
    # casual R1: exact (Arm A)
    out.append(("casual_R1_exact", EVNET_EXACT[ck]))
    for pn in POLICIES:
        if pn != "R1":
            c = legs[ck][pn]["casual"]
            out.append(("casual_%s_mc" % pn,
                        Fraction(c["net_total_cu"], c["M"] * 100)))
        gr = legs[ck][pn]["grinder"]
        out.append(("grinder_%s_mc" % pn,
                    Fraction(gr["net_total_cu"], gr["M"] * 100)))
    if design == "D1":
        out.append(("farmer_wash_exact",
                    (SIG_EXACT[size] - T_EXACT[t]) * 100))
    elif design == "D2":
        if SIG_EXACT[size] == T_EXACT[t]:
            out.append(("farmer_capchaser_exact_knife_edge", Fraction(0)))
        else:
            f = legs[ck]["farmer_capchaser"]
            out.append(("farmer_capchaser_mc",
                        Fraction(f["net_total_cu"], f["M"] * 100)))
    elif design == "D3":
        if g == "T1":
            out.append(("farmer_stopper_exact_dp", D3_FARMER_EV_T1[(t, size)]))
        else:
            best = None
            for (b, tau, phi) in VARIANTS:
                vk = "%s|t=%s|stopper|b=%d|tau=%d|phi=%d" % (g, t, b, tau, phi)
                s = stoppers[vk]
                v = Fraction(s["net_total_cu_by_rho"][str(size)],
                             s["M"] * 100)
                if best is None or v > best:
                    best = v
            out.append(("farmer_stopper_mc_max", best))
    return out


# --------------------------------------------------------- decision machinery
def band_eval_1(legs, stoppers):
    """Evaluator 1: integer cross-multiplication on counts; Fractions only
    where the quantity is itself exact."""
    cells = {}
    for g in SHAPES:
        for t in T_DEC:
            for design, size in DCOMBOS:
                ck = cell_key(g, t, design, size)
                fun = 4 * FUN_EXACT[ck].numerator >= FUN_EXACT[ck].denominator
                safe = all(20 * legs[ck][pn]["casual"]["wipes"] <=
                           legs[ck][pn]["casual"]["M"] for pn in POLICIES)
                sink = all(10 * legs[ck][pn]["grinder"]["doubles"] <=
                           legs[ck][pn]["grinder"]["M"] for pn in POLICIES)
                det = all(100 * legs[ck][pn]["grinder"]["caphits"] <=
                          legs[ck][pn]["grinder"]["M"] for pn in POLICIES)
                ml = mint_legs(legs, stoppers, g, t, design, size)
                mx = ml[0][1]
                mxn = ml[0][0]
                for nm, v in ml[1:]:
                    if v > mx:
                        mx, mxn = v, nm
                mint = mx.numerator <= 0
                boundary = mx.numerator == 0
                cells[ck] = {"FUN": fun, "SAFE": safe, "SINK": sink,
                             "DET": det, "MINT": mint, "boundary": boundary,
                             "mint_max_leg": mxn,
                             "mint_max_units": float(mx),
                             "all_four": fun and safe and sink and mint,
                             "rescue_full": (fun and safe and sink and mint
                                             and det),
                             "clean": (fun and safe and sink and mint and det
                                       and not boundary)}
    return cells


def band_eval_2(legs, stoppers):
    """Evaluator 2: independent code path, straight Fraction comparisons."""
    quarter = Fraction(1, 4)
    twentieth = Fraction(1, 20)
    tenth = Fraction(1, 10)
    hundredth = Fraction(1, 100)
    cells = {}
    for g in SHAPES:
        for t in T_DEC:
            for design, size in DCOMBOS:
                ck = cell_key(g, t, design, size)
                ok_fun = FUN_EXACT[ck] >= quarter
                ok_safe = max(Fraction(legs[ck][pn]["casual"]["wipes"],
                                       legs[ck][pn]["casual"]["M"])
                              for pn in POLICIES) <= twentieth
                ok_sink = max(Fraction(legs[ck][pn]["grinder"]["doubles"],
                                       legs[ck][pn]["grinder"]["M"])
                              for pn in POLICIES) <= tenth
                ok_det = max(Fraction(legs[ck][pn]["grinder"]["caphits"],
                                      legs[ck][pn]["grinder"]["M"])
                             for pn in POLICIES) <= hundredth
                vals = mint_legs(legs, stoppers, g, t, design, size)
                mx = max(v for _, v in vals)
                cells[ck] = {"FUN": ok_fun, "SAFE": ok_safe, "SINK": ok_sink,
                             "DET": ok_det, "MINT": mx <= 0,
                             "boundary": mx == 0,
                             "all_four": (ok_fun and ok_safe and ok_sink
                                          and mx <= 0),
                             "rescue_full": (ok_fun and ok_safe and ok_sink
                                             and mx <= 0 and ok_det),
                             "clean": (ok_fun and ok_safe and ok_sink and
                                       mx <= 0 and ok_det and mx != 0)}
    return cells


def ruling_from(cells):
    """Registered order: REJECT -> APPROVE -> NULL (fixtures
    process.decision_rule_evaluated_in_this_order)."""
    targets = {"C1": ("T1", 0.1), "C2": ("T2", 0.05)}
    summary = {}
    for cname, (g, t) in targets.items():
        clean = []
        boundary_res = []
        indet_pass = []
        for design, size in DCOMBOS:
            c = cells[cell_key(g, t, design, size)]
            if c["clean"]:
                clean.append([design, size])
            elif c["rescue_full"] and c["boundary"]:
                boundary_res.append([design, size])
            elif c["all_four"] and not c["DET"]:
                indet_pass.append([design, size])
        summary[cname] = {"clean_rescues": clean,
                          "boundary_rescues": boundary_res,
                          "indeterminate_all_four": indet_pass}
    nothing_anywhere = all(
        not s["clean_rescues"] and not s["boundary_rescues"]
        and not s["indeterminate_all_four"] for s in summary.values())
    if nothing_anywhere:
        return "reject", summary, None
    # APPROVE: some design with >= 2 consecutive clean sizes at C1
    approve_row = None
    for design, sizes in (("D1", SIGMAS), ("D2", SIGMAS), ("D3", RHOS)):
        flags = [cells[cell_key("T1", 0.1, design, s)]["clean"]
                 for s in sizes]
        for i in range(len(sizes) - 1):
            if flags[i] and flags[i + 1]:
                band = [s for s, f in zip(sizes, flags) if f]
                approve_row = {"design": design, "band": band}
                break
        if approve_row:
            break
    if approve_row:
        return "approve", summary, approve_row
    return "null", summary, None


def axis_shares(cells):
    passing = [(g, t, d, s) for g in SHAPES for t in T_DEC
               for d, s in DCOMBOS
               if cells[cell_key(g, t, d, s)]["clean"]]
    shares = {"design": {}, "size_index": {}, "take": {}, "shape": {}}
    for d in ("D1", "D2", "D3"):
        shares["design"][d] = sum(1 for c in passing if c[2] == d) / 16
    for i in range(4):
        sz = {"D1": SIGMAS, "D2": SIGMAS, "D3": RHOS}
        shares["size_index"]["idx%d" % i] = sum(
            1 for c in passing if sz[c[2]][i] == c[3]) / 12
    for t in T_DEC:
        shares["take"][str(t)] = sum(1 for c in passing if c[1] == t) / 24
    for g in SHAPES:
        shares["shape"][g] = sum(1 for c in passing if c[0] == g) / 24
    return shares, sorted("%s|t=%s|%s|%s" % c for c in passing)


# ================================================================= RUN
note("[arm S] primary leg, seed %d ..." % SEED_PRIMARY)
LEGS_P, STOP_P, DRAWS_P, TWIN_P = run_leg(
    SEED_PRIMARY, M_CASUAL, M_GRINDER, M_WASH, M_CAPCH, M_STOP, "primary")
note("[arm S] stability leg, seed %d ..." % SEED_STABILITY)
LEGS_S, STOP_S, DRAWS_S, TWIN_S = run_leg(
    SEED_STABILITY, M_CASUAL // 2, M_GRINDER // 2, M_WASH // 2, M_CAPCH // 2,
    M_STOP // 2, "stability")

CELLS_1 = band_eval_1(LEGS_P, STOP_P)
CELLS_2 = band_eval_2(LEGS_P, STOP_P)
for ck in CELLS_1:
    for kx in ("FUN", "SAFE", "SINK", "DET", "MINT", "boundary",
               "rescue_full", "clean"):
        check(CELLS_1[ck][kx] == CELLS_2[ck][kx],
              "twin evaluators agree %s %s" % (ck, kx))
RUL_P, RESCUE_P, APPROVE_ROW_P = ruling_from(CELLS_1)
RUL_P2, _, _ = ruling_from(CELLS_2)
check(RUL_P == RUL_P2, "twin evaluators: ruling")

CELLS_1S = band_eval_1(LEGS_S, STOP_S)
CELLS_2S = band_eval_2(LEGS_S, STOP_S)
RUL_S, RESCUE_S, APPROVE_ROW_S = ruling_from(CELLS_1S)
RUL_S2, _, _ = ruling_from(CELLS_2S)
check(RUL_S == RUL_S2, "twin evaluators (stability): ruling")
check(RUL_P == RUL_S,
      "STABILITY: half-M fresh-seed leg reproduces the ruling "
      "(primary %s vs stability %s)" % (RUL_P, RUL_S))

SHARES_P, PASSING_P = axis_shares(CELLS_1)

# D3 casual wipe = 0 exactly: assert the MC saw zero wipes on every D3 casual
for g in SHAPES:
    for t in T_DEC:
        for r_ in RHOS:
            ck = cell_key(g, t, "D3", r_)
            for legs in (LEGS_P, LEGS_S):
                for pn in ("R1",):
                    check(legs[ck][pn]["casual"]["wipes"] == 0,
                          "D3 R1-casual wipe == 0 exactly %s" % ck)

# ------------------------------------------------------------ agreement gates
note("[gate] pooled 1.0 pp agreement gates + 4-SE EV gates ...")
GATE = {"points": {}, "breaches": [], "max_pp": 0.0}


def gate_point(name, exact_float, pairs, kind="prob"):
    """pairs: list of (count, M). Pools counts; 1.0 pp band; z from
    predicted binomial SE at the exact value."""
    tot = sum(c for c, _ in pairs)
    m = sum(mm for _, mm in pairs)
    dev_pp = abs(tot / m - exact_float) * 100
    se_pp = math.sqrt(max(exact_float * (1 - exact_float), 1e-12) / m) * 100
    z = dev_pp / se_pp if se_pp > 0 else 0.0
    GATE["points"][name] = {"pooled_M": m, "pooled_value": tot / m,
                            "exact": exact_float,
                            "deviation_pp": round(dev_pp, 4),
                            "predicted_se_pp": round(se_pp, 4),
                            "z": round(z, 2), "breach": dev_pp > 1.0}
    GATE["max_pp"] = max(GATE["max_pp"], dev_pp)
    if dev_pp > 1.0:
        GATE["breaches"].append(name)


# FUN + wipe points (pooled per fixtures gate_calibration_disclosure)
for g in SHAPES:
    for t in T_DEC:
        base_ck = cell_key(g, t, "BASE", None)
        # baseline-class FUN: BASE + 4 D3 legs (exact identity), both MC legs
        pairs = []
        wpairs_base = []
        for legs, mm in ((LEGS_P, M_CASUAL), (LEGS_S, M_CASUAL // 2)):
            pairs.append((legs[base_ck]["R1"]["casual"]["aheads"], mm))
            wpairs_base.append((legs[base_ck]["R1"]["casual"]["wipes"], mm))
            for r_ in RHOS:
                pairs.append((legs[cell_key(g, t, "D3", r_)]
                              ["R1"]["casual"]["aheads"], mm))
        gate_point("FUN %s t=%s baseline-class" % (g, t),
                   float(FUN_EXACT[base_ck]), pairs)
        gate_point("WIPE %s t=%s baseline" % (g, t),
                   float(WIPE_EXACT[base_ck]), wpairs_base)
        for s in SIGMAS:
            pairs = []
            wpairs = []
            for legs, mm in ((LEGS_P, M_CASUAL), (LEGS_S, M_CASUAL // 2)):
                for d in ("D1", "D2"):
                    ckd = cell_key(g, t, d, s)
                    pairs.append((legs[ckd]["R1"]["casual"]["aheads"], mm))
                    wpairs.append((legs[ckd]["R1"]["casual"]["wipes"], mm))
            gate_point("FUN %s t=%s sigma=%s" % (g, t, s),
                       float(FUN_EXACT[cell_key(g, t, "D1", s)]), pairs)
            gate_point("WIPE %s t=%s sigma=%s" % (g, t, s),
                       float(WIPE_EXACT[cell_key(g, t, "D1", s)]), wpairs)
# baseline T1 grinder P_double vs capped DP
for t in T_DEC:
    ckb = cell_key("T1", t, "BASE", None)
    pairs = [(LEGS_P[ckb]["R1"]["grinder"]["doubles"], M_GRINDER),
             (LEGS_S[ckb]["R1"]["grinder"]["doubles"], M_GRINDER // 2)]
    gate_point("P_double_capped T1 t=%s baseline R1" % t,
               RUIN_CAPPED[t]["p_double"], pairs)
# D3 T1 stopper P(tau)
for t in T_DEC:
    for (b, tau, phi) in VARIANTS:
        vk = "T1|t=%s|stopper|b=%d|tau=%d|phi=%d" % (t, b, tau, phi)
        pairs = [(STOP_P[vk]["success"], M_STOP),
                 (STOP_S[vk]["success"], M_STOP // 2)]
        gate_point("P_tau %s" % vk,
                   float(STOP_EXACT[(t, (b, tau, phi))]["p_tau"]), pairs)

# EV gates at 4x predicted SE (EVs are not probabilities; disclosure 13)
EV_GATES = {}


def ev_gate(name, exact_units, var_units2, total_cu, m):
    mean_units = total_cu / m / 100
    se = math.sqrt(var_units2 / m)
    ok = abs(mean_units - exact_units) <= 4 * se + 1e-9
    EV_GATES[name] = {"mc_mean_units": round(mean_units, 4),
                      "exact_units": round(exact_units, 6),
                      "se_units": round(se, 4), "pass": ok}
    check(ok, "EV gate 4-SE: %s (mc %.3f exact %.3f se %.3f)"
          % (name, mean_units, exact_units, se))


for g in SHAPES:
    for t in T_DEC:
        for design, size in [("BASE", None)] + DCOMBOS:
            ck = cell_key(g, t, design, size)
            var = float(EVVAR_EXACT[ck])
            tot = (LEGS_P[ck]["R1"]["casual"]["net_total_cu"] +
                   LEGS_S[ck]["R1"]["casual"]["net_total_cu"])
            mm = M_CASUAL + M_CASUAL // 2
            ev_gate("casualR1 %s" % ck, float(EVNET_EXACT[ck]), var, tot, mm)
            if design == "D1":
                totw = (LEGS_P[ck]["farmer_wash"]["net_total_cu"] +
                        LEGS_S[ck]["farmer_wash"]["net_total_cu"])
                mw2 = M_WASH + M_WASH // 2
                ev_gate("wash %s" % ck,
                        float((SIG_EXACT[size] - T_EXACT[t]) * 100),
                        var, totw, mw2)
# D3 T1 stopper EVs vs exact DP
for t in T_DEC:
    for (b, tau, phi) in VARIANTS:
        vk = "T1|t=%s|stopper|b=%d|tau=%d|phi=%d" % (t, b, tau, phi)
        ex = STOP_EXACT[(t, (b, tau, phi))]
        for r_ in RHOS:
            tot = (int(STOP_P[vk]["net_total_cu_by_rho"][str(r_)]) +
                   int(STOP_S[vk]["net_total_cu_by_rho"][str(r_)]))
            mm = M_STOP + M_STOP // 2
            ev_gate("stopper %s rho=%s" % (vk, r_), float(ex["ev"][r_]),
                    float(ex["var"][r_]), tot, mm)
# D2 cap-chaser Wald sign asserts (skipped inside 0.03 of the knife edge)
for g in SHAPES:
    for t in T_DEC:
        for s in SIGMAS:
            if abs(s - t) < 0.03 - 1e-12:
                continue
            ck = cell_key(g, t, "D2", s)
            tot = (LEGS_P[ck]["farmer_capchaser"]["net_total_cu"] +
                   LEGS_S[ck]["farmer_capchaser"]["net_total_cu"])
            want_pos = s > t
            check((tot > 0) == want_pos and tot != 0,
                  "cap-chaser Wald sign %s (total %d, sigma-t %.2f)"
                  % (ck, tot, s - t))

# ------------------------------------------------- aux 8x re-measures of breaches
note("[aux] seed %d — 8x re-measure of %d gate breaches ..."
     % (SEED_AUX, len(GATE["breaches"])))
rng_aux = random.Random(SEED_AUX)
rra = rng_aux.random
AUX_REMEASURE = {}
AUX_DRAWS = {"n": 0}


def rra_counting():
    AUX_DRAWS["n"] += 1
    return rra()


for name in list(GATE["breaches"]):
    pt = GATE["points"][name]
    m8 = 8 * pt["pooled_M"]
    parts = name.split()
    cnt = 0
    if name.startswith("P_tau"):
        vk = parts[1]
        seg = vk.split("|")
        g = seg[0]
        t = float(seg[1].split("=")[1])
        b = int(seg[3].split("=")[1])
        tau = int(seg[4].split("=")[1])
        phi = int(seg[5].split("=")[1])
        ths = thresholds(g, t)
        for _ in range(m8):
            f, rd, tk, pz = play_stopper(g, rra_counting, ths, b,
                                         tau * 100, phi * 100)
            if f >= tau * 100:
                cnt += 1
    elif name.startswith("P_double_capped"):
        t = float(parts[2].split("=")[1])
        ths = thresholds("T1", t)
        for _ in range(m8):
            f, rd, tk, pz, rb = play("T1", rra_counting, ths, 0, 4000,
                                     GLOW, GHI, 0, 0, 0, 0)
            if f >= GHI:
                cnt += 1
    else:
        quant, g, tpart, cls = parts[0], parts[1], parts[2], parts[3]
        t = float(tpart.split("=")[1])
        ths = thresholds(g, t)
        if cls.startswith("sigma"):
            s = float(cls.split("=")[1])
            stip = int(SIG_EXACT[s] * 10000)   # measure via the D1 leg
            rho5 = 0
        else:
            stip = 0
            rho5 = 0
        for _ in range(m8):
            f, rd, tk, pz, rb = play(g, rra_counting, ths, 0, 100, -1, BIG,
                                     0, 0, stip, rho5)
            w = end_wealth(f, tk, stip, rho5)
            if quant == "FUN":
                if w > 10000:
                    cnt += 1
            else:
                if w <= WIPEC:
                    cnt += 1
    dev_pp = abs(cnt / m8 - pt["exact"]) * 100
    ok = dev_pp <= 1.0
    AUX_REMEASURE[name] = {"M_8x": m8, "value": cnt / m8,
                           "exact": pt["exact"],
                           "deviation_pp": round(dev_pp, 4), "pass": ok}
    check(ok, "AUX 8x re-measure within 1.0 pp: %s (%.4f pp)" % (name, dev_pp))

# ------------------------------------------------------------ hand pins
note("[pins] hand-derived pin scenarios ...")
pins = FIX["hand_derived_pins"]


def run_pin(idx, g, t, draws, pol_i, profile, params):
    it = iter(draws)
    cntbox = {"n": 0}

    def rp():
        cntbox["n"] += 1
        return next(it)
    lo, hi, mx = profile
    f, rd, tk, pz, rb = play(g, rp, thresholds(g, t), pol_i, mx, lo, hi,
                             *params)
    return f, rd, tk, pz, rb, cntbox["n"]


# pin-1: D2 rebate + casual early-death, RG all-loss
e = pins[0]["expect"]
f, rd, tk, pz, rb, nd = run_pin(1, "T1", 0.05, [0.99] * 200, 2,
                                PROFILE_CASUAL, design_params("D2", 0.2))
check((rd, tk, pz, rb, f) == (e["rounds"], e["tickets"], e["prizes_cu"],
                              e["rebate_cu"], e["final_bank_cu"]),
      "pin-1 main kernel (got f=%d rd=%d tk=%d pz=%d rb=%d)"
      % (f, rd, tk, pz, rb))
check(nd == e["draws"], "pin-1 draw count")
w = end_wealth(f, tk, 0, 0)
check((w > 10000) == e["ahead"] and (w <= WIPEC) == e["wipe"],
      "pin-1 classification")
tw = twin_play([0.99] * e["draws"], "T1", 0.05, "RG", PROFILE_CASUAL,
               ("D2", 0.2))
check(tw[:3] == (e["final_bank_cu"], e["rounds"], e["tickets"])
      and tw[5] == 0, "pin-1 twin kernel")

# pin-2: D2 cap-chaser stops exactly at the cap
e = pins[1]["expect"]
draws2 = [0.2, 0.99] * 100
it2 = iter(draws2)
bank = 10000
rounds = tk2 = pz2 = rbt = 0
while rounds < 2000 and bank >= 100 and rbt < 4000:
    u = next(it2)
    prize = 200 if u < 0.475 else 0
    credit = min(20, 4000 - rbt)
    rbt += credit
    bank += prize + credit - 100
    rounds += 1
    tk2 += 1
    pz2 += prize
check((rounds, tk2, pz2, rbt, bank) ==
      (e["rounds"], e["tickets"], e["prizes_cu"], e["rebate_cu"],
       e["final_bank_cu"]), "pin-2 cap-chaser (got %s)"
      % [rounds, tk2, pz2, rbt, bank])
check(bank - 10000 == e["net_cu"], "pin-2 net")
check(sum(1 for _ in it2) == 0 and e["draws"] == 200, "pin-2 draw count")

# pin-3: D1 qualification at exactly 100 tickets + wipe with stipend
e = pins[2]["expect"]
f, rd, tk, pz, rb, nd = run_pin(3, "T1", 0.05, [0.99] * 100, 1,
                                PROFILE_CASUAL, design_params("D1", 0.05))
w = end_wealth(f, tk, 500, 0)
check((rd, tk, pz, f, w) == (e["rounds"], e["tickets"], e["prizes_cu"],
                             e["final_bank_cu"], e["wealth_cu"]),
      "pin-3 main kernel (got f=%d rd=%d tk=%d w=%d)" % (f, rd, tk, w))
check(nd == e["draws"], "pin-3 draw count")
check((w > 10000) == e["ahead"] and (w <= WIPEC) == e["wipe"],
      "pin-3 classification")

# pin-4: D3 stranded grinder
e = pins[3]["expect"]
f, rd, tk, pz, rb, nd = run_pin(4, "T1", 0.1, [0.99] * 100, 0,
                                PROFILE_GRINDER, design_params("D3", 0.8))
w = end_wealth(f, tk, 0, 4)
check((rd, tk, f, w) == (e["rounds"], e["tickets"], e["final_bank_cu"],
                         e["wealth_cu"]),
      "pin-4 main kernel (got f=%d rd=%d w=%d)" % (f, rd, w))
check(nd == e["draws"], "pin-4 draw count")
check(not (w >= GHI) and not (w <= GLOW) and rd < 4000,
      "pin-4 outcome stranded")

# pin-5: D1 stipend jump crosses the double line at qualification
e = pins[4]["expect"]
draws5 = [0.2] * 95 + [0.2, 0.99, 0.99, 0.99, 0.99]
f, rd, tk, pz, rb, nd = run_pin(5, "T1", 0.05, draws5, 1,
                                PROFILE_GRINDER, design_params("D1", 0.2))
w = end_wealth(f, tk, 2000, 0)
check((rd, tk, pz, f, w) == (e["rounds"], e["tickets"], e["prizes_cu"],
                             e["final_bank_cu"], e["wealth_cu"]),
      "pin-5 main kernel (got f=%d rd=%d tk=%d pz=%d w=%d)"
      % (f, rd, tk, pz, w))
check(nd == e["draws"], "pin-5 draw count")
check(w >= GHI, "pin-5 outcome double (by the stipend jump)")
tw = twin_play(draws5, "T1", 0.05, "R5", PROFILE_GRINDER, ("D1", 0.2))
check(tw[:3] == (e["final_bank_cu"], e["rounds"], e["tickets"])
      and tw[5] == 0, "pin-5 twin kernel")

# ------------------------------------------------------------ reporting legs
note("[reporting] seed %d — t=0 control, compulsive, T3 spot, aggregation ..."
     % SEED_REPORTING)
rng_rep = random.Random(SEED_REPORTING)
rrp = rng_rep.random
REP_DRAWS = {"n": 0}


def rrp_c():
    REP_DRAWS["n"] += 1
    return rrp()


REPORTING = {}
# (1) t=0 control: T1 casual R1, T1 grinder R1, T2 casual R1 — baseline
t0 = {}
for legname, g, prof, m in (("T1_casual_R1", "T1", PROFILE_CASUAL, M_CASUAL),
                            ("T1_grinder_R1", "T1", PROFILE_GRINDER,
                             M_GRINDER),
                            ("T2_casual_R1", "T2", PROFILE_CASUAL, M_CASUAL)):
    ths0 = thresholds(g, 0.0)
    lo, hi, mx = prof
    aheads = wipes = doubles = 0
    lt = lp = 0
    for _ in range(m):
        f, rd, tk, pz, rb = play(g, rrp_c, ths0, 0, mx, lo, hi, 0, 0, 0, 0)
        if f != 10000 + pz - 100 * tk:
            check(False, "conservation t=0 %s" % legname)
        if f > 10000:
            aheads += 1
        if f <= WIPEC:
            wipes += 1
        if f >= GHI:
            doubles += 1
        lt += tk
        lp += pz
    bulk_checks(m)
    vg = VAR_T0[g]
    check(abs(lp - 100 * lt) <= 4 * math.sqrt(lt * vg) * 100 + 1e-9,
          "Wald t=0 prize fairness %s" % legname)
    t0[legname] = {"M": m, "P_ahead": aheads / m, "P_wipe": wipes / m,
                   "P_double": doubles / m, "tickets": lt}
    if legname == "T1_casual_R1":
        ef = float(sum(pr for s, pr in NET_DIST[("T1", 0.0)].items() if s > 0))
        se = math.sqrt(ef * (1 - ef) / m)
        check(abs(aheads / m - ef) <= 4 * se + 1e-9,
              "t=0 control T1 FUN within 4 SE of exact 0.4602...")
    if legname == "T2_casual_R1":
        ef = float(sum(pr for s, pr in NET_DIST[("T2", 0.0)].items() if s > 0))
        se = math.sqrt(ef * (1 - ef) / m)
        check(abs(aheads / m - ef) <= 4 * se + 1e-9,
              "t=0 control T2 FUN within 4 SE of exact")
    if legname == "T1_grinder_R1":
        ef = RUIN_CAPPED[0.0]["p_double"]
        se = math.sqrt(ef * (1 - ef) / m)
        check(abs(doubles / m - ef) <= 4 * se + 1e-9,
              "t=0 control capped P_double within 4 SE of capped DP "
              "(uncapped exact = 1/3)")
REPORTING["t0_control"] = t0
# (2) compulsive block: baseline + D2 cells (D1/D3 == baseline by identity)
comp = {}
for g in SHAPES:
    for t in T_DEC:
        ths = thresholds(g, t)
        for design, size in [("BASE", None)] + [("D2", s) for s in SIGMAS]:
            reb, rebcap, stip, rho5 = design_params(design, size)
            ruins = 0
            rounds_list = []
            lt = 0
            for _ in range(M_COMPULSIVE):
                f, rd, tk, pz, rb = play(g, rrp_c, ths, 0, 20000, -1, BIG,
                                         reb, rebcap, stip, rho5)
                if f != 10000 + pz + rb - 100 * tk:
                    check(False, "conservation compulsive %s"
                          % cell_key(g, t, design, size))
                if f < 100:
                    ruins += 1
                    rounds_list.append(rd)
                else:
                    rounds_list.append(BIG)
                lt += tk
            bulk_checks(M_COMPULSIVE)
            rounds_list.sort()
            m1 = rounds_list[M_COMPULSIVE // 2 - 1]
            m2 = rounds_list[M_COMPULSIVE // 2]
            med = ">20000" if (m1 >= BIG or m2 >= BIG) else (m1 + m2) / 2
            comp[cell_key(g, t, design, size)] = {
                "M": M_COMPULSIVE, "ruin_frac": ruins / M_COMPULSIVE,
                "median_rounds_to_ruin": med, "tickets": lt}
comp["identity_note"] = ("D1/D3 compulsive == baseline by identity "
                         "(end-of-session comp cannot alter the in-session "
                         "walk); see fixtures disclosure 7")
REPORTING["compulsive"] = comp
# (3) T3 monotonicity spot cell
ths3 = thresholds("T3", 0.05)
spotres = {}
for legname, params in (("baseline", (0, 0, 0, 0)),
                        ("D1_sigma_0.2", (0, 0, 2000, 0))):
    doubles = 0
    lt = 0
    for _ in range(M_GRINDER):
        f, rd, tk, pz, rb = play("T3", rrp_c, ths3, 0, 4000, GLOW, GHI,
                                 *params)
        if f != 10000 + pz - 100 * tk:
            check(False, "conservation T3 spot %s" % legname)
        w = end_wealth(f, tk, params[2], 0)
        if w >= GHI:
            doubles += 1
        lt += tk
    bulk_checks(M_GRINDER)
    spotres[legname] = {"M": M_GRINDER, "P_double": doubles / M_GRINDER,
                        "tickets": lt}
check(spotres["D1_sigma_0.2"]["P_double"] >= spotres["baseline"]["P_double"],
      "T3 monotonicity spot cell: comp weakly RAISES P_double "
      "(baseline %.4f vs D1 sigma=0.2 %.4f)"
      % (spotres["baseline"]["P_double"],
         spotres["D1_sigma_0.2"]["P_double"]))
REPORTING["t3_monotonicity_spot"] = spotres
# (4) aggregated-draw spot check (V025's clause; part B on the aux stream)
spot_t = 0.05
c1s, c2s, c3s = thresholds("T2", spot_t)
netsA = []
for _ in range(1000):
    s = 0
    for _ in range(100):
        u = rrp_c()
        if u < c3s:
            if u < c1s:
                s += 8
            elif u < c2s:
                s += 3
            else:
                s += 1
    netsA.append(s - 100)


def binom_inv(rngf, n, p):
    if n == 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    u = rngf()
    q = 1.0 - p
    pmf = q ** n
    cdf = pmf
    k = 0
    while u >= cdf and k < n:
        pmf *= (n - k) / (k + 1) * (p / q)
        k += 1
        cdf += pmf
    return k


p1 = (1 - spot_t) * 0.05
p2 = (1 - spot_t) * 0.10
p3 = (1 - spot_t) * 0.30
netsB = []
for _ in range(1000):
    n8 = binom_inv(rra_counting, 100, p1)
    n3 = binom_inv(rra_counting, 100 - n8, p2 / (1 - p1))
    n1 = binom_inv(rra_counting, 100 - n8 - n3, p3 / (1 - p1 - p2))
    netsB.append(8 * n8 + 3 * n3 + n1 - 100)
meanA = sum(netsA) / 1000
meanB = sum(netsB) / 1000
varA = sum((x - meanA) ** 2 for x in netsA) / 999
varB = sum((x - meanB) ** 2 for x in netsB) / 999
tol = 4 * math.sqrt((varA + varB) / 1000)
spot_ok = abs(meanA - meanB) <= tol
check(spot_ok, "aggregation spot check mean-net within 4 SE")
REPORTING["aggregation_spot_check"] = {
    "mean_net_per_ticket_method": meanA, "mean_net_aggregated": meanB,
    "tolerance_4se": tol, "agrees": spot_ok,
    "note": "reporting-only; every decision number uses per-ticket draws; "
            "part B (aggregated twin) rides the aux stream"}

# ------------------------------------------------------------ anchors
note("[anchors] baseline-reproduction vs V025 committed rows ...")
PARENT_ROWS = FIX["chained_anchors_reporting_only"][
    "parent_committed_baseline_rows_c5"]
ANCHOR_RESULTS = {}
for g in SHAPES:
    for t in T_DEC:
        tstr = "0.05" if t == 0.05 else "0.1"
        ck = cell_key(g, t, "BASE", None)
        for pn in POLICIES:
            prow = PARENT_ROWS["%s|t=%s|c=5|%s" % (g, tstr, pn)]
            mine_c = LEGS_P[ck][pn]["casual"]
            mine_g = LEGS_P[ck][pn]["grinder"]
            entry = {}
            for qname, mycnt, mym, pcnt, pm in (
                    ("P_wipe", mine_c["wipes"], mine_c["M"],
                     prow["wipes"], prow["casual_M"]),
                    ("P_ahead", mine_c["aheads"], mine_c["M"],
                     prow["aheads"], prow["casual_M"]),
                    ("P_double", mine_g["doubles"], mine_g["M"],
                     prow["doubles"], prow["grinder_M"]),
                    ("cap_frac", mine_g["caphits"], mine_g["M"],
                     prow["caphits"], prow["grinder_M"])):
                pme = mycnt / mym
                ppa = pcnt / pm
                pool = (mycnt + pcnt) / (mym + pm)
                tol2 = max(4 * math.sqrt(max(pool * (1 - pool), 1e-12) *
                                         (1 / mym + 1 / pm)), 0.004)
                ok = abs(pme - ppa) <= tol2
                entry[qname] = {"mine": pme, "parent": ppa,
                                "tol": round(tol2, 5), "pass": ok}
                check(ok, "ANCHOR baseline row %s|t=%s %s %s "
                      "(mine %.4f parent %.4f tol %.4f)"
                      % (g, t, pn, qname, pme, ppa, tol2))
            ANCHOR_RESULTS["%s|t=%s|%s" % (g, t, pn)] = entry
# expected-loss price tag at the incumbent
inc_c = LEGS_P[cell_key("T1", 0.05, "BASE", None)]["R1"]["casual"]
inc_worst = max(-LEGS_P[cell_key("T1", 0.05, "BASE", None)][pn]["casual"]
                ["mean_net_frac_B0"] for pn in POLICIES)
ANCHOR_RESULTS["incumbent_price_tag"] = {
    "parent": {"casual_R1": 0.05155, "worst_policy": 0.2518},
    "mine": {"casual_R1": -inc_c["mean_net_frac_B0"],
             "worst_policy": inc_worst}}
check(abs(-inc_c["mean_net_frac_B0"] - 0.05155) < 0.02,
      "incumbent casual price tag ~5.2% of B0 reproduced")

# ------------------------------------------------------------ house-net table
HOUSE_NET = {}
for g in SHAPES:
    for t in T_DEC:
        for design, size in [("BASE", None)] + DCOMBOS:
            ck = cell_key(g, t, design, size)
            HOUSE_NET[ck] = {
                "casual_R1_frac_B0_exact": float(-EVNET_EXACT[ck]) / 100,
                "casual_R1_frac_B0_mc":
                    -LEGS_P[ck]["R1"]["casual"]["mean_net_frac_B0"],
                "worst_policy_frac_B0_mc":
                    max(-LEGS_P[ck][pn]["casual"]["mean_net_frac_B0"]
                        for pn in POLICIES)}

# ------------------------------------------------------------ signature table
SIGNATURE = {}
for design, sizes in (("D1", SIGMAS), ("D2", SIGMAS), ("D3", RHOS)):
    for g in SHAPES:
        for t in T_DEC:
            row = {}
            for s in sizes:
                c = CELLS_1[cell_key(g, t, design, s)]
                row[str(s)] = {k: c[k] for k in
                               ("FUN", "SAFE", "SINK", "MINT", "DET",
                                "boundary", "clean")}
                row[str(s)]["mint_max_leg"] = c["mint_max_leg"]
                row[str(s)]["mint_max_units"] = round(c["mint_max_units"], 4)
            SIGNATURE["%s|%s|t=%s" % (design, g, t)] = row

# ------------------------------------------------------------ results
note("[results] writing results.json ...")


def fun_wipe_table():
    out = {}
    for g in SHAPES:
        for t in T_DEC:
            for design, size in [("BASE", None)] + DCOMBOS:
                ck = cell_key(g, t, design, size)
                out[ck] = {
                    "FUN_float": float(FUN_EXACT[ck]),
                    "FUN_fraction": str(FUN_EXACT[ck]),
                    "FUN_pass": FUN_EXACT[ck] >= Fraction(1, 4),
                    "wipe_R1_float": float(WIPE_EXACT[ck]),
                    "EVnet_R1_units_float": float(EVNET_EXACT[ck]),
                    "EVnet_R1_fraction": str(EVNET_EXACT[ck])}
    return out


def stopper_table():
    out = {}
    for t in T_DEC:
        for v in VARIANTS:
            ex = STOP_EXACT[(t, v)]
            out["T1|t=%s|b=%d|tau=%d|phi=%d" % ((t,) + v)] = {
                "p_tau_float": float(ex["p_tau"]),
                "p_tau_fraction": str(ex["p_tau"]),
                "ev_units_by_rho": {str(r_): float(ex["ev"][r_])
                                    for r_ in RHOS}}
    return out


RESULTS = {
    "meta": {
        "sim": "verdict-029-comp-stipend",
        "python": "cpython-%d.%d" % sys.version_info[:2],
        "seeds": {"primary": SEED_PRIMARY, "stability": SEED_STABILITY,
                  "reporting": SEED_REPORTING, "aux": SEED_AUX},
        "M": {"casual": M_CASUAL, "grinder": M_GRINDER,
              "compulsive": M_COMPULSIVE, "wash": M_WASH,
              "capchaser": M_CAPCH, "stopper": M_STOP},
        "draw_counts": {"primary": DRAWS_P, "stability": DRAWS_S,
                        "reporting": REP_DRAWS["n"], "aux": AUX_DRAWS["n"]},
        "twin_replays": {"primary": TWIN_P, "stability": TWIN_S}},
    "arm_a": {
        "fun_wipe_evnet_exact": fun_wipe_table(),
        "d1_d2_farmer_pump_line":
            {"%s" % t: {str(s): str((SIG_EXACT[s] - T_EXACT[t]) * 100)
                        for s in SIGMAS} for t in T_DEC},
        "d3_stopper_exact": stopper_table(),
        "d3_farmer_ev_max_T1": {"t=%s|rho=%s" % (t, r_):
                                float(D3_FARMER_EV_T1[(t, r_)])
                                for t in T_DEC for r_ in RHOS},
        "ruin_T1xR1_baseline": {
            "t=%s" % t: {"uncapped_float": float(RUIN_UNCAPPED[t]),
                         "uncapped_fraction": str(RUIN_UNCAPPED[t]),
                         "capped_p_double": RUIN_CAPPED[t]["p_double"]}
            for t in (0.0, 0.05, 0.1)},
        "t0_exact_third": str(RUIN_UNCAPPED[0.0])},
    "identity_gate": identity_results,
    "agreement_gate": GATE,
    "ev_gates": EV_GATES,
    "aux_remeasure_8x": AUX_REMEASURE,
    "primary": LEGS_P,
    "primary_stoppers": STOP_P,
    "stability": LEGS_S,
    "stability_stoppers": STOP_S,
    "cells_primary": CELLS_1,
    "cells_stability": CELLS_1S,
    "decision": {
        "primary_ruling": RUL_P,
        "primary_rescue_summary": RESCUE_P,
        "primary_approve_row": APPROVE_ROW_P,
        "stability_ruling": RUL_S,
        "stability_rescue_summary": RESCUE_S,
        "stability_reproduces_ruling": RUL_P == RUL_S,
        "per_axis_clean_pass_shares": SHARES_P,
        "clean_passing_cells": PASSING_P,
        "final_ruling": RUL_P},
    "signature_table": SIGNATURE,
    "house_net_table": HOUSE_NET,
    "reporting": REPORTING,
    "chained_anchors": ANCHOR_RESULTS,
    "self_checks": {"passed": None, "failed": len(FAILED)},
}
RESULTS["self_checks"]["passed"] = N_CHECKS - len(FAILED)

out_path = os.path.join(HERE, "results.json")
with open(out_path, "w") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True, default=str)
    fh.write("\n")

# ------------------------------------------------------------ stdout summary
print("verdict-029 comp-stipend envelope — pre-registered dual-arm sim")
print("identity gate (sigma=0 Fractions == V022/V025 committed, exact): %s"
      % ("PASS" if all(v["equal"] for v in identity_results.values())
         else "FAIL"))
print("t=0 control (T1xR1 uncapped P_double): %s == 1/3 %s"
      % (RUIN_UNCAPPED[0.0], RUIN_UNCAPPED[0.0] == Fraction(1, 3)))
print("agreement gates: %d points, max pooled deviation %.4f pp, "
      "breaches %d (all within 1.0 pp at the 8x aux re-measure: %s)"
      % (len(GATE["points"]), GATE["max_pp"], len(GATE["breaches"]),
         all(v["pass"] for v in AUX_REMEASURE.values())
         if AUX_REMEASURE else "n/a"))
print("EV gates (4-SE): %d points, all pass: %s"
      % (len(EV_GATES), all(v["pass"] for v in EV_GATES.values())))
print("")
print("TARGET-CELL RESCUE SUMMARY (primary):")
for cname in ("C1", "C2"):
    s = RESCUE_P[cname]
    print("  %s: clean %s · boundary %s · indeterminate-all-four %s"
          % (cname, s["clean_rescues"], s["boundary_rescues"],
             s["indeterminate_all_four"]))
print("clean all-four-pass cells (48-cell grid): %s" % PASSING_P)
print("per-axis clean pass shares: %s"
      % json.dumps(SHARES_P, sort_keys=True))
print("stability leg reproduces ruling: %s (primary %s, stability %s)"
      % (RUL_P == RUL_S, RUL_P, RUL_S))
print("")
print("anchor — V025 surviving cell reproduced: worst-policy P_wipe %.4f "
      "(parent 0.0024), P_double %.4f (parent 0.0000)"
      % (max(LEGS_P[cell_key('T1', 0.05, 'BASE', None)][pn]["casual"]
             ["P_wipe"] for pn in POLICIES),
         max(LEGS_P[cell_key('T1', 0.05, 'BASE', None)][pn]["grinder"]
             ["P_double"] for pn in POLICIES)))
print("anchor — C2 near-miss reproduced: worst-policy P_wipe %.4f "
      "(parent 0.0608)"
      % max(LEGS_P[cell_key('T2', 0.05, 'BASE', None)][pn]["casual"]
            ["P_wipe"] for pn in POLICIES))
print("anchor — incumbent price tag: casual %.4f (parent 0.0516), "
      "worst %.4f (parent 0.2518)"
      % (ANCHOR_RESULTS["incumbent_price_tag"]["mine"]["casual_R1"],
         ANCHOR_RESULTS["incumbent_price_tag"]["mine"]["worst_policy"]))
print("T3 monotonicity spot: baseline P_double %.4f -> D1 sigma=0.2 %.4f "
      "(weakly raised: %s)"
      % (REPORTING["t3_monotonicity_spot"]["baseline"]["P_double"],
         REPORTING["t3_monotonicity_spot"]["D1_sigma_0.2"]["P_double"],
         REPORTING["t3_monotonicity_spot"]["D1_sigma_0.2"]["P_double"] >=
         REPORTING["t3_monotonicity_spot"]["baseline"]["P_double"]))
print("")
print("RULING (pre-registered order REJECT -> APPROVE -> NULL): %s"
      % RUL_P.upper())
if APPROVE_ROW_P:
    print("approve row: %s" % APPROVE_ROW_P)
print("")
print("SELF-CHECKS: %d passed, %d failed"
      % (N_CHECKS - len(FAILED), len(FAILED)))
if FAILED:
    print("FAILED CHECKS:")
    for m in FAILED:
        print("  - %s" % m)
sys.exit(1 if FAILED else 0)
