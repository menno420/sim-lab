#!/usr/bin/env python3
"""verdict-025 — entry-fee ticket envelope (idea-engine PROPOSAL 023).

Fully hermetic NUMERIC SIMULATION (method ladder rung 1): reads exactly ONE
file (its own committed fixtures.json pre-registration), touches no repo
state, no network, no wall clock (timing goes to stderr only, never into
stdout or results.json).

Dual-arm design per the pre-registration:
  Arm A — analytic, seedless, exact rationals: FUN tails for all 36 cells
          (T1 binomial via math.comb, REQUIRED to reproduce VERDICT 022's
          committed G1 reference values exactly; T2/T3 by exact
          integer-support DP convolution), the T1xR1 grinder two-boundary
          gambler's-ruin closed form (+ independent tridiagonal
          elimination, + the exact finite-horizon capped DP of the same
          chain), the exact T1xR1 casual wipe DP, the t=0 P_double = 1/3
          optional-stopping control.
  Arm S — seeded MC: random.Random(20260730) primary / 20260731 stability
          (half M) / 20260732 aggregation spot check / 20260733 aux
          self-checks; pinned loop order, one rng.random() per ticket.

Decision rule (registered in the idea file BEFORE any code; evaluated in
this order): REJECT / APPROVE / NULL — see fixtures.json
process.decision_rule_evaluated_in_this_order.

Run:  python3 sims/verdict-025-ticket-envelope/ticket_envelope_sim.py
Exit 0 iff every self-check passes. stdout + results.json byte-identical
across process runs (verified externally by diff of two complete runs).
"""

import itertools
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
check(sys.version_info[:2] == (3, 11), "CPython minor pinned: 3.11 required, got %s" % (sys.version_info[:2],))

B0_UNITS = 100          # B0 in F-units (B0 = 1000 chips, F = 10)
WIPE_UNITS = 10         # 0.1 * B0
GRIND_LO = 50           # 0.5 * B0
GRIND_HI = 200          # 2 * B0
BIG = 1 << 60

SHAPES = ["T1", "T2", "T3"]
PRIZES = {"T1": [2], "T2": [8, 3, 1], "T3": [25, 5]}
BASE_P = {"T1": [Fraction(1, 2)],
          "T2": [Fraction(1, 20), Fraction(1, 10), Fraction(3, 10)],
          "T3": [Fraction(3, 125), Fraction(2, 25)]}
BASE_P_FLOAT = {"T1": [0.5], "T2": [0.05, 0.10, 0.30], "T3": [0.024, 0.08]}
VAR_T0 = {"T1": 1.0, "T2": 3.4, "T3": 16.0}

T_ALL = [0.0, 0.01, 0.02, 0.05, 0.1]          # control first, ascending
T_GRID = [0.01, 0.02, 0.05, 0.1]              # decision grid
T_EXACT = {0.0: Fraction(0), 0.01: Fraction(1, 100), 0.02: Fraction(1, 50),
           0.05: Fraction(1, 20), 0.1: Fraction(1, 10)}
CAPS = [5, 25, 100]
POLICIES = ["R1", "R5", "RG", "MC"]

M_CASUAL = FIX["constants"]["M_casual"]
M_GRINDER = FIX["constants"]["M_grinder"]
M_COMPULSIVE = FIX["constants"]["M_compulsive"]
SEED_PRIMARY = FIX["constants"]["seed_primary"]
SEED_STABILITY = FIX["constants"]["seed_stability"]
SEED_SPOT = FIX["constants"]["seed_spot_check"]
SEED_AUX = FIX["constants"]["seed_aux"]

check(M_CASUAL == 5000 and M_GRINDER == 2000 and M_COMPULSIVE == 500,
      "fixture M constants")
check((SEED_PRIMARY, SEED_STABILITY, SEED_SPOT, SEED_AUX) ==
      (20260730, 20260731, 20260732, 20260733), "fixture seeds")
check(FIX["constants"]["B0"] == 1000 and FIX["constants"]["F"] == 10, "B0/F")
check([float(x) for x in FIX["constants"]["t_grid"]] == T_GRID, "t grid")
check(FIX["constants"]["c_grid"] == CAPS, "c grid")

# fixture cross-check: E[prize] = (1-t)*F exactly, per (shape, t); t=0 variances
for g in SHAPES:
    fx = FIX["constants"]["prize_schedules"][g]
    check(fx["prizes_units"] == PRIZES[g], "prize units %s" % g)
    check([Fraction(s) for s in fx["base_probs_exact"]] == BASE_P[g],
          "base probs %s" % g)
    for t, tf in T_EXACT.items():
        ev = sum((1 - tf) * q * pz for q, pz in zip(BASE_P[g], PRIZES[g]))
        check(ev == (1 - tf) * 1, "E[prize] = (1-t)*F exact: %s t=%s" % (g, t))
    m2 = sum(q * pz * pz for q, pz in zip(BASE_P[g], PRIZES[g]))
    check(m2 - 1 == Fraction(str(fx["per_ticket_variance_at_t0_units2"])),
          "t=0 per-ticket variance %s" % g)


def thresholds(g, t):
    """Cumulative float thresholds, computed once per (shape, take)."""
    out = []
    acc = 0.0
    for q in BASE_P_FLOAT[g]:
        acc += (1.0 - t) * q
        out.append(acc)
    return tuple(out)


# ================================================================= ARM A
note("[arm A] exact analytic arm ...")

FUN_EXACT = {}      # (g, t) -> Fraction P_ahead (R1 casual reference)
WIPE_EXACT = {}     # (g, t) -> Fraction P_wipe  (R1 casual)


def binom_tail_ge(p, n, k):
    return sum(Fraction(math.comb(n, w)) * p ** w * (1 - p) ** (n - w)
               for w in range(k, n + 1))


def binom_tail_le(p, n, k):
    return sum(Fraction(math.comb(n, w)) * p ** w * (1 - p) ** (n - w)
               for w in range(0, k + 1))


def round_net_dist(g, tf):
    """Single-ticket round net distribution in units, as (D, {net: int weight})."""
    probs = [(1 - tf) * q for q in BASE_P[g]]
    miss = 1 - sum(probs)
    outs = [(pz - 1, pr) for pz, pr in zip(PRIZES[g], probs)] + [(-1, miss)]
    D = 1
    for _, pr in outs:
        D = D * pr.denominator // math.gcd(D, pr.denominator)
    w = {}
    for net, pr in outs:
        w[net] = w.get(net, 0) + int(pr * D)
    check(sum(w.values()) == D, "round dist mass %s t=%s" % (g, tf))
    return D, w


def dp_100(g, tf):
    """Exact DP over 100 R1 rounds: returns (P_ahead, P_wipe) Fractions."""
    D, w = round_net_dist(g, tf)
    dist = {0: 1}
    for _ in range(100):
        nxt = {}
        for s, num in dist.items():
            for net, wt in w.items():
                k = s + net
                nxt[k] = nxt.get(k, 0) + num * wt
        dist = nxt
    total = D ** 100
    check(sum(dist.values()) == total, "DP mass = 1: %s t=%s" % (g, tf))
    check(len(dist) <= 2500, "DP support <= 2500: %s t=%s" % (g, tf))
    ahead = sum(n for s, n in dist.items() if s > 0)
    wipe = sum(n for s, n in dist.items() if s <= -90)
    return Fraction(ahead, total), Fraction(wipe, total)


for g in SHAPES:
    for t in T_ALL:
        tf = T_EXACT[t]
        pa, pw = dp_100(g, tf)
        if g == "T1":
            p = (1 - tf) / 2
            pa_b = binom_tail_ge(p, 100, 51)
            pw_b = binom_tail_le(p, 100, 5)
            check(pa == pa_b, "T1 DP == binomial ahead t=%s" % t)
            check(pw == pw_b, "T1 DP == binomial wipe t=%s" % t)
        FUN_EXACT[(g, t)] = pa
        WIPE_EXACT[(g, t)] = pw

# FUN monotone non-increasing in t, per shape
for g in SHAPES:
    seq = [FUN_EXACT[(g, t)] for t in T_ALL]
    check(all(a >= b for a, b in zip(seq, seq[1:])), "FUN monotone in t: %s" % g)

# cross-verdict identity gate: T1 FUN == VERDICT 022 committed G1 values
IDENT = FIX["identity_gate"]["parent_committed_G1_fun_exact"]
IDENT_MAP = {0.0: "G1|e=0", 0.01: "G1|e=1/100", 0.02: "G1|e=1/50",
             0.05: "G1|e=1/20", 0.1: "G1|e=1/10"}
identity_results = {}
for t, key in IDENT_MAP.items():
    mine = FUN_EXACT[("T1", t)]
    parent = Fraction(IDENT[key]["fraction"])
    ok = (mine == parent)
    check(ok, "IDENTITY GATE: T1 FUN(t=%s) == V022 %s" % (t, key))
    identity_results[key] = {"t": t, "equal": ok, "float": float(mine),
                             "parent_float": IDENT[key]["float"]}

# grinder T1xR1: closed form + elimination + capped finite-horizon DP
RUIN_UNCAPPED = {}
RUIN_CAPPED = {}


def ruin_closed(tf):
    p = (1 - tf) / 2
    if p == Fraction(1, 2):
        return Fraction(50, 150)
    r = (1 - p) / p
    return (1 - r ** 50) / (1 - r ** 150)


def ruin_elimination(tf):
    """Independent derivation: exact-Fraction forward elimination of the
    tridiagonal system h_s = p*h_{s+1} + q*h_{s-1}, h_0 = 0, h_150 = 1,
    states s = units - 50."""
    p = (1 - tf) / 2
    q = 1 - p
    # express h_{s+1} = alpha_s * h_1 + beta_s  (h_0 = 0, h_1 unknown)
    a_prev, b_prev = Fraction(1), Fraction(0)   # h_1
    a_pp, b_pp = Fraction(0), Fraction(0)       # h_0
    for _ in range(1, 150):
        # h_{s+1} = (h_s - q*h_{s-1}) / p
        a = (a_prev - q * a_pp) / p
        b = (b_prev - q * b_pp) / p
        a_pp, b_pp = a_prev, b_prev
        a_prev, b_prev = a, b
    # h_150 = a_prev*h1 + b_prev = 1
    h1 = (1 - b_prev) / a_prev
    # roll forward to h_50
    h_prev2, h_prev1 = Fraction(0), h1
    for _ in range(1, 50):
        h_next = (h_prev1 - q * h_prev2) / p
        h_prev2, h_prev1 = h_prev1, h_next
    return h_prev1


def ruin_capped_dp(t):
    """Exact same-capped quantity Arm S measures on T1xR1 grinder:
    finite-horizon absorption DP, 151 states, 4000 steps, float."""
    p = (1.0 - t) * 0.5
    q = 1.0 - p
    dist = [0.0] * 151
    dist[50] = 1.0            # start 100 units = state 50 above lower
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


for t in T_ALL:
    tf = T_EXACT[t]
    cf = ruin_closed(tf)
    el = ruin_elimination(tf)
    check(cf == el, "ruin closed form == elimination t=%s" % t)
    up, down, alive = ruin_capped_dp(t)
    check(abs(up + down + alive - 1.0) < 1e-12, "capped DP mass t=%s" % t)
    check(up <= float(cf) + 1e-9, "capped <= uncapped t=%s" % t)
    RUIN_UNCAPPED[t] = cf
    RUIN_CAPPED[t] = {"p_double": up, "p_half": down, "alive_at_cap": alive,
                      "uncapped_minus_capped": float(cf) - up}
check(RUIN_UNCAPPED[0.0] == Fraction(1, 3),
      "t=0 control: P_double = 1/3 exactly (optional stopping)")
seq = [RUIN_UNCAPPED[t] for t in T_ALL]
check(all(a >= b for a, b in zip(seq, seq[1:])), "P_double monotone in t")

note("[arm A] done — identity gate %s, t=0 control 1/3 %s"
     % (all(v["equal"] for v in identity_results.values()),
        RUIN_UNCAPPED[0.0] == Fraction(1, 3)))


# ================================================================= ARM S kernel
def play_T1(rr, ths, cap, pol, max_rounds, lower, upper):
    th, = ths
    bank = 100
    rounds = tickets = prizes = 0
    L = 0
    while rounds < max_rounds and lower < bank < upper:
        if pol == 0:
            b = 1
        elif pol == 1:
            b = 5 if bank >= 5 else bank
        elif pol == 2:
            b = cap if bank >= cap else bank
        else:
            b = 1 << (L if L < 7 else 7)
            if b > cap:
                b = cap
            if b > bank:
                b = bank
        w = 0
        for _ in range(b):
            if rr() < th:
                w += 1
        pz = 2 * w
        bank += pz - b
        rounds += 1
        tickets += b
        prizes += pz
        if pol == 3:
            if pz < b:
                L += 1
            elif pz > b:
                L = 0
    return bank, rounds, tickets, prizes


def play_T2(rr, ths, cap, pol, max_rounds, lower, upper):
    c1, c2, c3 = ths
    bank = 100
    rounds = tickets = prizes = 0
    L = 0
    while rounds < max_rounds and lower < bank < upper:
        if pol == 0:
            b = 1
        elif pol == 1:
            b = 5 if bank >= 5 else bank
        elif pol == 2:
            b = cap if bank >= cap else bank
        else:
            b = 1 << (L if L < 7 else 7)
            if b > cap:
                b = cap
            if b > bank:
                b = bank
        s = 0
        for _ in range(b):
            u = rr()
            if u < c3:
                if u < c1:
                    s += 8
                elif u < c2:
                    s += 3
                else:
                    s += 1
        bank += s - b
        rounds += 1
        tickets += b
        prizes += s
        if pol == 3:
            if s < b:
                L += 1
            elif s > b:
                L = 0
    return bank, rounds, tickets, prizes


def play_T3(rr, ths, cap, pol, max_rounds, lower, upper):
    c1, c2 = ths
    bank = 100
    rounds = tickets = prizes = 0
    L = 0
    while rounds < max_rounds and lower < bank < upper:
        if pol == 0:
            b = 1
        elif pol == 1:
            b = 5 if bank >= 5 else bank
        elif pol == 2:
            b = cap if bank >= cap else bank
        else:
            b = 1 << (L if L < 7 else 7)
            if b > cap:
                b = cap
            if b > bank:
                b = bank
        s = 0
        for _ in range(b):
            u = rr()
            if u < c2:
                s += 25 if u < c1 else 5
        bank += s - b
        rounds += 1
        tickets += b
        prizes += s
        if pol == 3:
            if s < b:
                L += 1
            elif s > b:
                L = 0
    return bank, rounds, tickets, prizes


PLAY = {"T1": play_T1, "T2": play_T2, "T3": play_T3}


# --------------------------------------------------- independently written twin
def twin_play(draws, g, t, cap, pol_name, profile):
    """Independently written twin kernel: consumes a recorded draw list,
    dict state, per-level threshold scan (its own cumulative arithmetic,
    identical summation order by construction)."""
    it = iter(draws)
    st = {"bank": 100, "rounds": 0, "tickets": 0, "prizes": 0, "streak": 0}
    lo, hi, mx = profile
    scaled = [(1.0 - t) * q for q in BASE_P_FLOAT[g]]
    pzs = PRIZES[g]
    while st["rounds"] < mx and lo < st["bank"] < hi:
        if pol_name == "R1":
            want = 1
        elif pol_name == "R5":
            want = 5
        elif pol_name == "RG":
            want = cap
        else:
            want = 2 ** st["streak"] if st["streak"] < 7 else 128
        n = min(want, cap, st["bank"])
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
        st["bank"] += got - n
        st["rounds"] += 1
        st["tickets"] += n
        st["prizes"] += got
        if pol_name == "MC":
            if got < n:
                st["streak"] += 1
            elif got > n:
                st["streak"] = 0
    leftover = sum(1 for _ in it)
    return (st["bank"], st["rounds"], st["tickets"], st["prizes"], leftover)


PROFILE_CASUAL = (0, BIG, 100)
PROFILE_GRINDER = (GRIND_LO, GRIND_HI, 4000)
PROFILE_COMPULSIVE = (0, BIG, 20000)
PROFILE_BY_NAME = {"casual": PROFILE_CASUAL, "grinder": PROFILE_GRINDER,
                   "compulsive": PROFILE_COMPULSIVE}


def make_tracer(rr, buf):
    def rrt():
        v = rr()
        buf.append(v)
        return v
    return rrt


# --------------------------------------------------------------- the sweep
def run_arm(seed, mc, mg, mp, label):
    rng = random.Random(seed)
    rr = rng.random
    expected_first = random.Random(seed).random()
    first_seen = []
    legs = {}
    total_tickets = 0
    n_twin = 0
    for g in SHAPES:
        play = PLAY[g]
        vg = VAR_T0[g]
        for t in T_ALL:
            ths = thresholds(g, t)
            for cap in CAPS:
                for pol_i, pol_name in enumerate(POLICIES):
                    key = "%s|t=%s|c=%d|%s" % (g, t, cap, pol_name)
                    # ---- casual
                    aheads = wipes = 0
                    sfinal = 0
                    lt = lp = 0
                    for rep in range(mc):
                        if rep == 0 or rep == mc - 1:
                            buf = []
                            f, rd, tk, pz = play(make_tracer(rr, buf), ths,
                                                 cap, pol_i, 100, 0, BIG)
                            tw = twin_play(buf, g, t, cap, pol_name,
                                           PROFILE_CASUAL)
                            check(tw == (f, rd, tk, pz, 0),
                                  "twin replay casual %s rep %d" % (key, rep))
                            if not first_seen:
                                first_seen.append(buf[0])
                            n_twin += 1
                        else:
                            f, rd, tk, pz = play(rr, ths, cap, pol_i,
                                                 100, 0, BIG)
                        if f != 100 + pz - tk:
                            check(False, "conservation casual %s" % key)
                        if f > 100:
                            aheads += 1
                        if f <= WIPE_UNITS:
                            wipes += 1
                        sfinal += f
                        lt += tk
                        lp += pz
                    bulk_checks(mc)  # per-replication conservation
                    if t == 0.0:
                        check(abs(lp - lt) <= 4 * math.sqrt(lt * vg) + 1e-9,
                              "Wald t=0 prize fairness casual %s" % key)
                    total_tickets += lt
                    cas = {"M": mc, "aheads": aheads, "wipes": wipes,
                           "P_ahead": aheads / mc, "P_wipe": wipes / mc,
                           "mean_final_units": sfinal / mc,
                           "expected_loss_frac": (100 - sfinal / mc) / 100,
                           "tickets": lt}
                    # ---- grinder
                    doubles = halves = caphits = 0
                    srounds = 0
                    lt2 = lp2 = 0
                    for rep in range(mg):
                        if rep == 0 or rep == mg - 1:
                            buf = []
                            f, rd, tk, pz = play(make_tracer(rr, buf), ths,
                                                 cap, pol_i, 4000,
                                                 GRIND_LO, GRIND_HI)
                            tw = twin_play(buf, g, t, cap, pol_name,
                                           PROFILE_GRINDER)
                            check(tw == (f, rd, tk, pz, 0),
                                  "twin replay grinder %s rep %d" % (key, rep))
                            n_twin += 1
                        else:
                            f, rd, tk, pz = play(rr, ths, cap, pol_i, 4000,
                                                 GRIND_LO, GRIND_HI)
                        if f != 100 + pz - tk:
                            check(False, "conservation grinder %s" % key)
                        if f >= GRIND_HI:
                            doubles += 1
                        elif f <= GRIND_LO:
                            halves += 1
                        else:
                            caphits += 1
                        srounds += rd
                        lt2 += tk
                        lp2 += pz
                    bulk_checks(mg)
                    if t == 0.0:
                        check(abs(lp2 - lt2) <= 4 * math.sqrt(lt2 * vg) + 1e-9,
                              "Wald t=0 prize fairness grinder %s" % key)
                    total_tickets += lt2
                    gri = {"M": mg, "doubles": doubles, "halves": halves,
                           "caphits": caphits, "P_double": doubles / mg,
                           "P_half": halves / mg, "cap_frac": caphits / mg,
                           "mean_rounds": srounds / mg, "tickets": lt2}
                    leg = {"casual": cas, "grinder": gri}
                    # ---- compulsive (R1 only)
                    if pol_name == "R1":
                        ruins = 0
                        rounds_list = []
                        lt3 = lp3 = 0
                        for rep in range(mp):
                            if rep == 0 or rep == mp - 1:
                                buf = []
                                f, rd, tk, pz = play(make_tracer(rr, buf),
                                                     ths, cap, pol_i, 20000,
                                                     0, BIG)
                                tw = twin_play(buf, g, t, cap, pol_name,
                                               PROFILE_COMPULSIVE)
                                check(tw == (f, rd, tk, pz, 0),
                                      "twin replay compulsive %s rep %d"
                                      % (key, rep))
                                n_twin += 1
                            else:
                                f, rd, tk, pz = play(rr, ths, cap, pol_i,
                                                     20000, 0, BIG)
                            if f != 100 + pz - tk:
                                check(False, "conservation compulsive %s" % key)
                            if f == 0:
                                ruins += 1
                                rounds_list.append(rd)
                            else:
                                rounds_list.append(BIG)  # censored -> +inf
                            lt3 += tk
                            lp3 += pz
                        bulk_checks(mp)
                        if t == 0.0:
                            check(abs(lp3 - lt3) <=
                                  4 * math.sqrt(lt3 * vg) + 1e-9,
                                  "Wald t=0 prize fairness compulsive %s" % key)
                        total_tickets += lt3
                        rounds_list.sort()
                        m1 = rounds_list[mp // 2 - 1]
                        m2 = rounds_list[mp // 2]
                        med = ">20000" if (m1 >= BIG or m2 >= BIG) \
                            else (m1 + m2) / 2
                        leg["compulsive"] = {"M": mp, "ruin_frac": ruins / mp,
                                             "median_rounds_to_ruin": med,
                                             "tickets": lt3}
                    legs[key] = leg
            note("[%s] %s t=%s done (tickets so far %d)"
                 % (label, g, t, total_tickets))
    # stream sentinels
    check(first_seen and first_seen[0] == expected_first,
          "%s: first draw == Random(seed).random()" % label)
    probe = random.Random(seed)
    pr = probe.random
    for _ in itertools.repeat(None, total_tickets):
        pr()
    check(pr() == rr(), "%s: post-sweep draw-count sentinel (%d draws)"
          % (label, total_tickets))
    return legs, total_tickets, n_twin


# --------------------------------------------------------- decision machinery
def band_eval_1(legs, mc, mg):
    """Evaluator 1: exact integer cross-multiplication on counts."""
    E = {}
    indet_pass = []
    fun_pass = {}
    for g in SHAPES:
        for t in T_GRID:
            fun_pass[(g, t)] = FUN_EXACT[(g, t)] >= Fraction(1, 4)
        for cap in CAPS:
            members = []
            for t in T_GRID:
                safe = all(20 * legs["%s|t=%s|c=%d|%s" % (g, t, cap, pn)]
                           ["casual"]["wipes"] <= mc for pn in POLICIES)
                sink = all(10 * legs["%s|t=%s|c=%d|%s" % (g, t, cap, pn)]
                           ["grinder"]["doubles"] <= mg for pn in POLICIES)
                det = all(100 * legs["%s|t=%s|c=%d|%s" % (g, t, cap, pn)]
                          ["grinder"]["caphits"] <= mg for pn in POLICIES)
                if fun_pass[(g, t)] and safe and sink:
                    if det:
                        members.append(t)
                    else:
                        indet_pass.append([g, t, cap])
            E[(g, cap)] = members
    # ruling, evaluated in the pre-registered order
    empty_shapes = [g for g in SHAPES
                    if all(not E[(g, cap)] for cap in CAPS)]
    approve_row = None
    for cap in CAPS:
        inter = set(T_GRID)
        for g in SHAPES:
            inter &= set(E[(g, cap)])
        band = [t for t in T_GRID if t in inter]
        for i in range(len(band) - 1):
            a, b = band[i], band[i + 1]
            if T_GRID.index(b) == T_GRID.index(a) + 1:
                approve_row = {"cap": cap, "band": band}
                break
        if approve_row:
            break
    if len(empty_shapes) >= 2:
        ruling = "reject"
    elif approve_row:
        ruling = "approve"
    else:
        ruling = "null"
    # per-axis envelope shares
    passing = set()
    for (g, cap), members in E.items():
        for t in members:
            passing.add((g, t, cap))
    shares = {"shape": {}, "take": {}, "cap": {}}
    for g in SHAPES:
        shares["shape"][g] = sum(1 for (gg, t, c) in passing if gg == g) / 12
    for t in T_GRID:
        shares["take"][str(t)] = \
            sum(1 for (g, tt, c) in passing if tt == t) / 9
    for cap in CAPS:
        shares["cap"][str(cap)] = \
            sum(1 for (g, t, c) in passing if c == cap) / 12
    spread = {ax: (max(d.values()) - min(d.values()))
              for ax, d in shares.items()}
    return {"envelope": {("%s|c=%d" % (g, c)): E[(g, c)]
                         for g in SHAPES for c in CAPS},
            "indeterminate_passes": indet_pass,
            "empty_shapes": empty_shapes,
            "approve_row": approve_row,
            "ruling": ruling,
            "per_axis_envelope_shares": shares,
            "per_axis_spread": spread}


def band_eval_2(legs, mc, mg):
    """Evaluator 2: independent code path, Fraction comparisons."""
    quarter, twentieth, tenth, hundredth = (Fraction(1, 4), Fraction(1, 20),
                                            Fraction(1, 10), Fraction(1, 100))
    env = {}
    for g in SHAPES:
        for cap in CAPS:
            good = []
            for t in T_GRID:
                cells = [legs["%s|t=%s|c=%d|%s" % (g, t, cap, pn)]
                         for pn in POLICIES]
                ok_fun = FUN_EXACT[(g, t)] >= quarter
                ok_safe = max(Fraction(cl["casual"]["wipes"],
                                       cl["casual"]["M"])
                              for cl in cells) <= twentieth
                ok_sink = max(Fraction(cl["grinder"]["doubles"],
                                       cl["grinder"]["M"])
                              for cl in cells) <= tenth
                ok_det = max(Fraction(cl["grinder"]["caphits"],
                                      cl["grinder"]["M"])
                             for cl in cells) <= hundredth
                if ok_fun and ok_safe and ok_sink and ok_det:
                    good.append(t)
            env["%s|c=%d" % (g, cap)] = good
    n_empty = sum(1 for g in SHAPES
                  if not any(env["%s|c=%d" % (g, c)] for c in CAPS))
    if n_empty >= 2:
        ruling = "reject"
    else:
        ruling = "null"
        for cap in CAPS:
            common = [t for t in T_GRID
                      if all(t in env["%s|c=%d" % (g, cap)] for g in SHAPES)]
            idx = [T_GRID.index(t) for t in common]
            if any(j - i == 1 for i, j in zip(idx, idx[1:])):
                ruling = "approve"
                break
    return {"envelope": env, "ruling": ruling}


# ================================================================= RUN
note("[arm S] primary leg, seed %d ..." % SEED_PRIMARY)
LEGS_P, DRAWS_P, TWIN_P = run_arm(SEED_PRIMARY, M_CASUAL, M_GRINDER,
                                  M_COMPULSIVE, "primary")
note("[arm S] stability leg, seed %d ..." % SEED_STABILITY)
LEGS_S, DRAWS_S, TWIN_S = run_arm(SEED_STABILITY, M_CASUAL // 2,
                                  M_GRINDER // 2, M_COMPULSIVE // 2,
                                  "stability")

EV1 = band_eval_1(LEGS_P, M_CASUAL, M_GRINDER)
EV2 = band_eval_2(LEGS_P, M_CASUAL, M_GRINDER)
check(EV1["ruling"] == EV2["ruling"], "twin decision evaluators: ruling")
check(EV1["envelope"] == EV2["envelope"], "twin decision evaluators: envelope")
EV1_S = band_eval_1(LEGS_S, M_CASUAL // 2, M_GRINDER // 2)
EV2_S = band_eval_2(LEGS_S, M_CASUAL // 2, M_GRINDER // 2)
check(EV1_S["ruling"] == EV2_S["ruling"], "twin evaluators (stability)")
check(EV1["ruling"] == EV1_S["ruling"],
      "STABILITY: half-M fresh-seed leg reproduces the ruling "
      "(primary %s vs stability %s)" % (EV1["ruling"], EV1_S["ruling"]))

# ------------------------------------------------------------ agreement gate
note("[gate] pooled 1.0 pp Arm-A agreement gate ...")
GATE = {"pooled": {}, "per_leg_deviations_over_1pp": [], "max_pooled_pp": 0.0}


def pooled_gate(quantity, g, t, exact_float, count_fn, m_p, m_s):
    tot = 0
    m = 0
    per = []
    for cap in CAPS:
        key = "%s|t=%s|c=%d|R1" % (g, t, cap)
        for legs, mm in ((LEGS_P, m_p), (LEGS_S, m_s)):
            cnt = count_fn(legs[key])
            tot += cnt
            m += mm
            dev = abs(cnt / mm - exact_float) * 100
            per.append(round(dev, 4))
            if dev > 1.0:
                GATE["per_leg_deviations_over_1pp"].append(
                    ["%s %s" % (quantity, key), round(dev, 4)])
    dev_pp = abs(tot / m - exact_float) * 100
    GATE["pooled"]["%s %s t=%s" % (quantity, g, t)] = {
        "pooled_M": m, "pooled_value": tot / m, "exact": exact_float,
        "deviation_pp": round(dev_pp, 4), "per_leg_pp": per}
    GATE["max_pooled_pp"] = max(GATE["max_pooled_pp"], dev_pp)
    check(dev_pp <= 1.0, "AGREEMENT GATE %s %s t=%s: %.4f pp"
          % (quantity, g, t, dev_pp))


for g in SHAPES:
    for t in T_ALL:
        pooled_gate("P_ahead", g, t, float(FUN_EXACT[(g, t)]),
                    lambda leg: leg["casual"]["aheads"], M_CASUAL,
                    M_CASUAL // 2)
        pooled_gate("P_wipe", g, t, float(WIPE_EXACT[(g, t)]),
                    lambda leg: leg["casual"]["wipes"], M_CASUAL,
                    M_CASUAL // 2)
for t in T_ALL:
    pooled_gate("P_double_capped", "T1", t, RUIN_CAPPED[t]["p_double"],
                lambda leg: leg["grinder"]["doubles"], M_GRINDER,
                M_GRINDER // 2)

# ------------------------------------------------------------ hand pins
note("[pins] hand-derived pin scenarios ...")
pin1 = FIX["hand_derived_pins"][0]
cnt = {"n": 0}


def rr_pin1():
    cnt["n"] += 1
    return 0.99


f, rd, tk, pz = play_T1(rr_pin1, thresholds("T1", 0.05), 100, 3, 100, 0, BIG)
e = pin1["expect"]
check((f, rd, tk) == (e["final_units"], e["rounds"], e["draws"]),
      "pin-1 main kernel (got final=%d rounds=%d draws=%d)" % (f, rd, tk))
check(cnt["n"] == e["draws"], "pin-1 draw count")
check((f > 100) == e["ahead"] and (f <= WIPE_UNITS) == e["wipe"],
      "pin-1 classification")
tw = twin_play([0.99] * e["draws"], "T1", 0.05, 100, "MC", PROFILE_CASUAL)
check(tw[:3] == (e["final_units"], e["rounds"], e["draws"]) and tw[4] == 0,
      "pin-1 twin kernel")

pin2 = FIX["hand_derived_pins"][1]
it = iter(pin2["draws"])
f, rd, tk, pz = play_T3(lambda: next(it), thresholds("T3", 0.1), 5, 2,
                        4000, GRIND_LO, GRIND_HI)
e = pin2["expect"]
check((f, rd, tk) == (e["final_units"], e["rounds"], e["draws"]),
      "pin-2 main kernel (got final=%d rounds=%d draws=%d)" % (f, rd, tk))
check(f >= GRIND_HI and e["outcome"] == "double", "pin-2 outcome double")
tw = twin_play(pin2["draws"], "T3", 0.1, 5, "RG", PROFILE_GRINDER)
check(tw[:3] == (e["final_units"], e["rounds"], e["draws"]) and tw[4] == 0,
      "pin-2 twin kernel")

# ------------------------------------------------------------ aux stream
note("[aux] seed %d R1-casual corroboration ..." % SEED_AUX)
rng_aux = random.Random(SEED_AUX)
rra = rng_aux.random
AUX = {}
for g in SHAPES:
    play = PLAY[g]
    for t in T_ALL:
        ths = thresholds(g, t)
        a = w = 0
        for _ in range(5000):
            fu, _, tku, pzu = play(rra, ths, 5, 0, 100, 0, BIG)
            if fu > 100:
                a += 1
            if fu <= WIPE_UNITS:
                w += 1
        for name, cnt2, exact in (("P_ahead", a, FUN_EXACT[(g, t)]),
                                  ("P_wipe", w, WIPE_EXACT[(g, t)])):
            ef = float(exact)
            se = math.sqrt(max(ef * (1 - ef), 1e-12) / 5000)
            check(abs(cnt2 / 5000 - ef) <= 4 * se + 1e-9,
                  "aux 4-SE corroboration %s %s t=%s" % (name, g, t))
            AUX["%s %s t=%s" % (name, g, t)] = {"mc": cnt2 / 5000, "exact": ef}

# ------------------------------------------------------------ spot check
note("[spot] seed %d aggregation spot check (reporting-only) ..." % SEED_SPOT)


def binom_inv(rng, n, p):
    """Binomial draw by CDF inversion, one uniform."""
    if n == 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    u = rng.random()
    q = 1.0 - p
    pmf = q ** n
    cdf = pmf
    k = 0
    while u >= cdf and k < n:
        pmf *= (n - k) / (k + 1) * (p / q)
        k += 1
        cdf += pmf
    return k


spot_t = 0.05
c1s, c2s, c3s = thresholds("T2", spot_t)
rngA = random.Random(SEED_SPOT)
rA = rngA.random
netsA = []
countsA = [0, 0, 0]
for _ in range(1000):
    s = 0
    for _ in range(100):
        u = rA()
        if u < c3s:
            if u < c1s:
                s += 8
                countsA[0] += 1
            elif u < c2s:
                s += 3
                countsA[1] += 1
            else:
                s += 1
                countsA[2] += 1
    netsA.append(s - 100)
rngB = random.Random(SEED_SPOT)
p1 = (1 - spot_t) * 0.05
p2 = (1 - spot_t) * 0.10
p3 = (1 - spot_t) * 0.30
netsB = []
countsB = [0, 0, 0]
for _ in range(1000):
    n8 = binom_inv(rngB, 100, p1)
    n3 = binom_inv(rngB, 100 - n8, p2 / (1 - p1))
    n1 = binom_inv(rngB, 100 - n8 - n3, p3 / (1 - p1 - p2))
    countsB[0] += n8
    countsB[1] += n3
    countsB[2] += n1
    netsB.append(8 * n8 + 3 * n3 + n1 - 100)
meanA = sum(netsA) / 1000
meanB = sum(netsB) / 1000
varA = sum((x - meanA) ** 2 for x in netsA) / 999
varB = sum((x - meanB) ** 2 for x in netsB) / 999
tol = 4 * math.sqrt((varA + varB) / 1000)
spot_ok = abs(meanA - meanB) <= tol
check(spot_ok, "aggregation spot check mean-net within 4 SE")
SPOT = {"mean_net_per_ticket_method": meanA, "mean_net_aggregated": meanB,
        "tolerance_4se": tol, "level_counts_per_ticket": countsA,
        "level_counts_aggregated": countsB, "agrees": spot_ok,
        "note": FIX["intake_time_decisions_disclosed"][7][:120] + "..."}

# ------------------------------------------------------------ anchors
nm_key = "T1|t=0.05|c=5|%s"
worst_wipe_nm = max(LEGS_P[nm_key % pn]["casual"]["P_wipe"]
                    for pn in POLICIES)
worst_double_nm = max(LEGS_P[nm_key % pn]["grinder"]["P_double"]
                      for pn in POLICIES)
sink_walls = {}
for g in ("T2", "T3"):
    vals = [max(LEGS_P["%s|t=%s|c=%d|%s" % (g, t, cap, pn)]
                ["grinder"]["P_double"] for pn in POLICIES)
            for t in T_GRID for cap in CAPS]
    sink_walls[g] = {"min": min(vals), "max": max(vals)}
ANCHORS = {
    "anchor_1_near_miss_transposed_cell_T1_t0.05_c5": {
        "parent_G1_e0.05_m0.05": {"FUN": 0.2738, "SINK": 0.0895,
                                  "SAFE_fail": 0.1358},
        "this_sim": {"FUN_exact": float(FUN_EXACT[("T1", 0.05)]),
                     "worst_policy_P_wipe": worst_wipe_nm,
                     "worst_policy_P_double": worst_double_nm,
                     "SAFE_band": 0.05,
                     "crosses_under_SAFE": worst_wipe_nm <= 0.05}},
    "anchor_2_sink_wall_vs_parent_0.195_0.323": {
        "parent_range": {"G2": [0.195, 0.323], "G3": [0.22, 0.296]},
        "this_sim_worst_policy_P_double_over_decision_cells": sink_walls},
    "anchor_3_t0_control": {
        "P_double_uncapped_exact": "1/3",
        "identity_gate_all_equal": all(v["equal"]
                                       for v in identity_results.values())},
    "anchor_4_expected_loss_price_tag":
        "per-cell expected_loss_frac in primary legs (casual)"}

# ------------------------------------------------------------ results
note("[results] writing results.json ...")


def fun_table():
    out = {}
    for (g, t), fr in sorted(FUN_EXACT.items()):
        out["%s|t=%s" % (g, t)] = {
            "P_ahead_float": float(fr), "P_ahead_fraction": str(fr),
            "P_wipe_float": float(WIPE_EXACT[(g, t)]),
            "P_wipe_fraction": str(WIPE_EXACT[(g, t)]),
            "FUN_pass": fr >= Fraction(1, 4)}
    return out


RESULTS = {
    "meta": {
        "sim": "verdict-025-ticket-envelope",
        "python": "cpython-%d.%d" % sys.version_info[:2],
        "seeds": {"primary": SEED_PRIMARY, "stability": SEED_STABILITY,
                  "spot_check": SEED_SPOT, "aux": SEED_AUX},
        "M": {"casual": M_CASUAL, "grinder": M_GRINDER,
              "compulsive": M_COMPULSIVE},
        "draw_counts": {"primary": DRAWS_P, "stability": DRAWS_S},
        "twin_replays": {"primary": TWIN_P, "stability": TWIN_S}},
    "arm_a": {
        "fun_and_wipe_exact": fun_table(),
        "ruin_T1xR1": {
            "uncapped_closed_form": {
                "t=%s" % t: {"float": float(RUIN_UNCAPPED[t]),
                             "fraction": str(RUIN_UNCAPPED[t])}
                for t in T_ALL},
            "capped_4000_dp": {"t=%s" % t: RUIN_CAPPED[t] for t in T_ALL},
            "t0_exact_third": str(RUIN_UNCAPPED[0.0])}},
    "identity_gate": identity_results,
    "agreement_gate": GATE,
    "primary": LEGS_P,
    "stability": LEGS_S,
    "decision": {
        "primary": {k: v for k, v in EV1.items()},
        "stability": {k: EV1_S[k] for k in
                      ("envelope", "empty_shapes", "approve_row", "ruling",
                       "indeterminate_passes")},
        "stability_reproduces_ruling": EV1["ruling"] == EV1_S["ruling"],
        "final_ruling": EV1["ruling"]},
    "chained_anchors": ANCHORS,
    "aux_reference_mc": AUX,
    "aggregation_spot_check": SPOT,
    "self_checks": {"passed": None, "failed": len(FAILED)},
}
RESULTS["self_checks"]["passed"] = N_CHECKS - len(FAILED)

out_path = os.path.join(HERE, "results.json")
with open(out_path, "w") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True, default=str)
    fh.write("\n")

# ------------------------------------------------------------ stdout summary
print("verdict-025 ticket-envelope — pre-registered dual-arm sim")
print("identity gate (T1-FUN == V022 G1-FUN, exact Fractions): %s"
      % ("PASS" if all(v["equal"] for v in identity_results.values())
         else "FAIL"))
print("t=0 control (T1xR1 uncapped P_double): %s == 1/3 %s"
      % (RUIN_UNCAPPED[0.0], RUIN_UNCAPPED[0.0] == Fraction(1, 3)))
print("agreement gate: max pooled deviation %.4f pp (band 1.0 pp) — %s"
      % (GATE["max_pooled_pp"],
         "PASS" if GATE["max_pooled_pp"] <= 1.0 else "FAIL"))
print("per-leg deviations > 1.0 pp (disclosed, non-gating): %d"
      % len(GATE["per_leg_deviations_over_1pp"]))
print("")
print("ENVELOPE E*(shape, cap) over t in {0.01, 0.02, 0.05, 0.10}:")
for g in SHAPES:
    for cap in CAPS:
        print("  E*(%s, c=%d) = %s" % (g, cap, EV1["envelope"]
                                       ["%s|c=%d" % (g, cap)]))
print("indeterminate-pass cells (cannot support APPROVE): %s"
      % EV1["indeterminate_passes"])
print("empty shapes (all caps): %s" % EV1["empty_shapes"])
print("per-axis envelope shares: %s" % json.dumps(
    EV1["per_axis_envelope_shares"], sort_keys=True))
print("per-axis spread: %s" % json.dumps(EV1["per_axis_spread"],
                                         sort_keys=True))
print("stability leg reproduces ruling: %s"
      % (EV1["ruling"] == EV1_S["ruling"]))
print("")
print("anchor 1 — transposed near-miss T1 (t=0.05, c=5): FUN %.4f (exact), "
      "worst-policy P_wipe %.4f (parent SAFE-fail 0.1358), worst-policy "
      "P_double %.4f (parent 0.0895); crosses under SAFE 0.05: %s"
      % (float(FUN_EXACT[("T1", 0.05)]), worst_wipe_nm, worst_double_nm,
         worst_wipe_nm <= 0.05))
print("anchor 2 — T2/T3 worst-policy P_double over decision cells: "
      "T2 [%.4f, %.4f], T3 [%.4f, %.4f] (parent wall G2 0.195-0.323, "
      "G3 0.220-0.296)"
      % (sink_walls["T2"]["min"], sink_walls["T2"]["max"],
         sink_walls["T3"]["min"], sink_walls["T3"]["max"]))
print("")
print("RULING (pre-registered order REJECT -> APPROVE -> NULL): %s"
      % EV1["ruling"].upper())
if EV1["approve_row"]:
    print("approve row: %s" % EV1["approve_row"])
print("")
print("SELF-CHECKS: %d passed, %d failed"
      % (N_CHECKS - len(FAILED), len(FAILED)))
if FAILED:
    print("FAILED CHECKS:")
    for m in FAILED:
        print("  - %s" % m)
sys.exit(1 if FAILED else 0)
