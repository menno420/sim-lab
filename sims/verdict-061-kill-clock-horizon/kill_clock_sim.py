#!/usr/bin/env python3
"""VERDICT 061 — kill-clock horizon (idea-engine PROPOSAL 050).

Is the venture products lane's shipped T+14 zero-sale kill clock right-sized
against the lane's own two OTHER committed clock values (the T+7 checkpoint
and the 30-day signal window) on expected proven-product throughput per
90 slot-days, across the pre-registered 3-prior x 3-build-downtime grid?

Arm A (DECISION, seedless, exact): the registered renewal dynamic program
over fractions.Fraction — G(h) = sum_p pi(p) * [ sum_{x=1..min(T,h)}
p*(1-p)^(x-1) * (1 + G(h-x-B)) + 1{T<h} * (1-p)^T * G(h-T-B) ], G(h<=0) = 0.
Every decision quantity exact. The ruling rides Arm A alone. A second,
independently-structured bookkeeping DP (full slot-day accounting + per-p
split) must reproduce Arm A's graduations as identical rationals.

Arm S (confirmation, seeded MC): N = 200,000 trajectories per (cell, clock)
via random.Random(20261337); pinned cell order (SKEPTIC, NEUTRAL, HOPEFUL) x
(B = 2, 5, 10), clock order (7, 14, 30) within a cell; pinned draw order
p-then-daily-trials (each live day exactly one Bernoulli draw). Agreement
gate |ArmS - ArmA| <= 3/200 absolute per leg AND >= 4*SE headroom asserted;
any breach invalidates the run. Seeds 20261337 main / 20261338 stability
(N = 20,000, widened gate <= 3/50) / 20261339 reporting-only legs
(N = 20,000 each) / 20261340 aux (reserved, NEVER read by any decision
number) — the ONLY four RNGs constructed, in pinned order.

Decision rule, registered, applied IN ORDER (margin m = 1/20 exact):
REJECT first, then APPROVE (with the stability-leg reproduction conjunct
through twin independently-written evaluators), else NULL (five axes).
Reporting-only legs can NEVER flip the decision.

Hermetic: reads only its own fixtures.json. Stdlib only. No wall-clock in
any output. Byte-identical stdout + results.json across process runs.

Run: python3 sims/verdict-061-kill-clock-horizon/kill_clock_sim.py
"""

import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
_CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)
        sys.exit(1)


def Fr(d):
    return Fraction(d["num"], d["den"])


def fr(x):
    return "%d/%d" % (x.numerator, x.denominator)


# ------------------------------------------------------------------- fixtures
with open(os.path.join(BASE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ------------------------------------------------------------- environment pin
check(platform.python_implementation() == "CPython", "interpreter is CPython")
check(list(sys.version_info[:2]) == FX["environment"]["cpython_minor"],
      "CPython minor version pinned in fixtures matches runner")

# --------------------------------------------------- transcription gates exact
P_GRID = [Fr(d) for d in FX["model"]["p_grid"]]
P_SENS = [Fr(d) for d in FX["model"]["sensitivity_p_grid"]]
PRIORS = [(pr["name"], [Fr(w) for w in pr["pmf"]])
          for pr in FX["model"]["priors_in_pinned_order"]]
BS = list(FX["model"]["build_downtime_B_in_pinned_order"])
TS = list(FX["model"]["clock_set_T_in_pinned_order"])
H_MAIN = FX["model"]["horizon_H"]
H_SENS = list(FX["model"]["sensitivity_H"])
T_SHIP = FX["model"]["shipped_clock_T"]
MARGIN = Fr(FX["decision_rule"]["margin_m"])
SWEEP = [Fr(d) for d in FX["decision_rule"]["margin_sweep"]]
GATE_MAIN = Fr(FX["arm_S"]["agreement_gate_abs"])
GATE_STAB = Fr(FX["arm_S"]["stability_gate_abs"])
N_MAIN = FX["arm_S"]["N_main"]
N_STAB = FX["arm_S"]["N_stability"]
N_REP = FX["arm_S"]["N_reporting"]
SEED_MAIN = FX["arm_S"]["seed_main"]
SEED_STAB = FX["arm_S"]["seed_stability"]
SEED_REP = FX["arm_S"]["seed_reporting"]
SEED_AUX = FX["arm_S"]["seed_aux"]

check(P_GRID == [Fraction(0), Fraction(1, 60), Fraction(1, 30),
                 Fraction(1, 14), Fraction(1, 7)], "transcription: p grid P")
check(P_SENS == [Fraction(0), Fraction(1, 90), Fraction(1, 45),
                 Fraction(1, 21), Fraction(1, 10)], "transcription: grid P'")
check([n for n, _ in PRIORS] == ["SKEPTIC", "NEUTRAL", "HOPEFUL"],
      "transcription: prior order")
check(PRIORS[0][1] == [Fraction(3, 4), Fraction(1, 10), Fraction(3, 40),
                       Fraction(1, 20), Fraction(1, 40)],
      "transcription: SKEPTIC pmf")
check(PRIORS[1][1] == [Fraction(1, 2)] + [Fraction(1, 8)] * 4,
      "transcription: NEUTRAL pmf")
check(PRIORS[2][1] == [Fraction(1, 4), Fraction(1, 4), Fraction(1, 4),
                       Fraction(3, 20), Fraction(1, 10)],
      "transcription: HOPEFUL pmf")
check(BS == [2, 5, 10] and TS == [7, 14, 30] and T_SHIP == 14,
      "transcription: B set, clock set, shipped clock")
check(H_MAIN == 90 and H_SENS == [60, 180], "transcription: H = 90, {60, 180}")
check(MARGIN == Fraction(1, 20) and SWEEP == [Fraction(1, 50), Fraction(1, 10)],
      "transcription: margin 1/20 and sweep {1/50, 1/10}")
check(GATE_MAIN == Fraction(3, 200) and GATE_STAB == Fraction(3, 50),
      "transcription: agreement gates 3/200 and 3/50")
check(N_MAIN == 200000 and N_STAB == 20000 and N_REP == 20000,
      "transcription: N = 200,000 / 20,000 / 20,000")
check([SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX] ==
      [20261337, 20261338, 20261339, 20261340],
      "transcription: seeds 20261337-340, strictly above high-water 20261336")
check(FX["decision_rule"]["reject_approve_cells_required"] == 7 and
      FX["decision_rule"]["skeptic_cells_required"] == 2,
      "transcription: 7-of-9 and 2-of-3-SKEPTIC band constants")
check(Fr(FX["gates"]["F4"]["hand_world"]["p"]) == Fraction(1, 2) and
      FX["gates"]["F4"]["hand_world"] == {"H": 6, "B": 1, "T": 2,
                                          "p": {"num": 1, "den": 2}},
      "transcription: hand world H=6, B=1, T=2, p=1/2")

CELLS = [(name, B) for name, _ in PRIORS for B in BS]
PMF = {name: pmf for name, pmf in PRIORS}


def cell_key(name, B):
    return "%s/B=%d" % (name, B)


# ------------------------------------------------- Arm A: registered scalar DP
def arm_a_G(pmf, ps, T, B, H):
    """The registered recursion, verbatim. Returns G[0..H] (G[h<=0] = 0)."""
    G = [Fraction(0)] * (H + 1)
    for h in range(1, H + 1):
        tot = Fraction(0)
        for p, w in zip(ps, pmf):
            if w == 0:
                continue
            q = 1 - p
            surv = Fraction(1)
            acc = Fraction(0)
            lim = T if T < h else h
            for x in range(1, lim + 1):
                rem = h - x - B
                cont = G[rem] if rem >= 1 else Fraction(0)
                acc += p * surv * (1 + cont)
                surv *= q
            if T < h:
                rem = h - T - B
                if rem >= 1:
                    acc += (q ** T) * G[rem]
            tot += w * acc
        G[h] = tot
    return G


def blocks_G(pmf, ps, T, B, H):
    """Graduation-blocks-slot world: a graduation counts 1 and BLOCKS the
    slot for the rest of the horizon (no renewal); kills renew as usual."""
    G = [Fraction(0)] * (H + 1)
    for h in range(1, H + 1):
        tot = Fraction(0)
        for p, w in zip(ps, pmf):
            if w == 0:
                continue
            q = 1 - p
            surv = Fraction(1)
            acc = Fraction(0)
            lim = T if T < h else h
            for x in range(1, lim + 1):
                acc += p * surv
                surv *= q
            if T < h:
                rem = h - T - B
                if rem >= 1:
                    acc += (q ** T) * G[rem]
            tot += w * acc
        G[h] = tot
    return G


# ------------------------- Arm A: independent bookkeeping DP (twin computation)
# Vector components (all exact Fractions):
NP = len(P_GRID)
K_GRAD, K_KILL, K_GDAY, K_KDAY, K_BPG, K_BPK, K_LIVE, K_LAUNCH, K_WASTE = range(9)
K_PG = 9            # per-p graduations: 9..9+NP-1
K_PK = 9 + NP       # per-p kills: 9+NP..9+2NP-1
NVEC = 9 + 2 * NP


def arm_a_book(pmf, ps, T, B, H, window=30):
    """Slot bookkeeping DP: expected graduations/kills, slot-day accounting
    (graduation-days + kill-days + build-days + live-at-horizon-days = h),
    launches, wasted graduations (kill forfeits vs the 30-day window), and
    the per-p graduation/kill split. Kill classified at T <= h (the kill
    decision fires at day T even when it coincides with horizon end; the
    scalar DP value is unaffected — h-T-B <= 0 contributes nothing there)."""
    zero = [Fraction(0)] * NVEC
    V = [list(zero) for _ in range(H + 1)]
    for h in range(1, H + 1):
        v = list(zero)
        v[K_LAUNCH] = Fraction(1)
        pend = []
        for i, (p, w) in enumerate(zip(ps, pmf)):
            if w == 0:
                continue
            q = 1 - p
            surv = Fraction(1)
            lim = T if T < h else h
            for x in range(1, lim + 1):
                wx = w * p * surv
                v[K_GRAD] += wx
                v[K_PG + i] += wx
                v[K_GDAY] += wx * x
                bd = B if h - x >= B else h - x
                v[K_BPG] += wx * bd
                rem = h - x - B
                if rem >= 1:
                    pend.append((wx, rem))
                surv *= q
            wns = w * surv
            if T <= h:
                v[K_KILL] += wns
                v[K_PK + i] += wns
                v[K_KDAY] += wns * T
                bd = B if h - T >= B else h - T
                v[K_BPK] += wns * bd
                v[K_WASTE] += wns * (1 - q ** (window - T))
                rem = h - T - B
                if rem >= 1:
                    pend.append((wns, rem))
            else:
                v[K_LIVE] += wns * h
        for wgt, rem in pend:
            vr = V[rem]
            for k in range(NVEC):
                if vr[k]:
                    v[k] += wgt * vr[k]
        V[h] = v
    return V[H]


# --------------------------------------------------------------- gates F1..F3
for name, pmf in PRIORS:
    check(sum(pmf) == 1, "F1: %s pmf sums to 1 exactly" % name)
    check(all(w >= 0 for w in pmf), "F1: %s pmf non-negative" % name)

P1_EXPECT = list(FX["gates"]["F2"]["p1_expected_at_H90"])
for H in [H_MAIN] + H_SENS:
    for T in TS:
        for B in BS:
            g0 = arm_a_G([Fraction(1)], [Fraction(0)], T, B, H)[H]
            check(g0 == 0, "F2: p=0 => G=0 at (T=%d,B=%d,H=%d)" % (T, B, H))
            g1 = arm_a_G([Fraction(1)], [Fraction(1)], T, B, H)[H]
            check(g1 == -(-H // (1 + B)),
                  "F2: p=1 => G=ceil(H/(1+B)) at (T=%d,B=%d,H=%d)" % (T, B, H))
check([-(-H_MAIN // (1 + B)) for B in BS] == P1_EXPECT == [30, 15, 9],
      "F2: p=1 values at H=90 are (30, 15, 9) for B=(2, 5, 10)")

for grid, gname in ((P_GRID, "P"), (P_SENS, "P'")):
    for p in grid:
        q = 1 - p
        prev = Fraction(-1)
        for T in TS:
            s = sum(p * q ** (x - 1) for x in range(1, T + 1))
            check(s == 1 - q ** T,
                  "F3: truncated-geometric identity, grid %s p=%s T=%d"
                  % (gname, fr(p), T))
            check(s >= prev,
                  "F3: per-launch graduation prob non-decreasing in T, "
                  "grid %s p=%s" % (gname, fr(p)))
            prev = s
for name, pmf in PRIORS:
    vals = [sum(w * (1 - (1 - p) ** T) for p, w in zip(P_GRID, pmf))
            for T in TS]
    check(vals == sorted(vals),
          "F3: per-launch graduation prob non-decreasing in T, prior %s" % name)

# ------------------------------------------------------------------- gate F4
HAND = FX["gates"]["F4"]["hand_world"]
hand_G = arm_a_G([Fraction(1)], [Fr(HAND["p"])], HAND["T"], HAND["B"],
                 HAND["H"])
for entry in FX["gates"]["F4"]["hand_chain"]:
    check(hand_G[entry["h"]] == Fr(entry["G"]),
          "F4: hand chain G(%d) = %s" % (entry["h"], fr(Fr(entry["G"]))))
check(hand_G[6] == Fraction(31, 16), "F4: hand world G = 31/16 exactly")

# --------------------------------------------- Arm A main tables + gates F5
GTAB = {}    # (name, B) -> {T: G exact}
BOOK = {}    # (name, B) -> {T: bookkeeping vector}
for name, B in CELLS:
    GTAB[(name, B)] = {}
    BOOK[(name, B)] = {}
    for T in TS:
        g = arm_a_G(PMF[name], P_GRID, T, B, H_MAIN)[H_MAIN]
        bk = arm_a_book(PMF[name], P_GRID, T, B, H_MAIN)
        check(bk[K_GRAD] == g,
              "twin Arm-A computations identical rationals: %s T=%d"
              % (cell_key(name, B), T))
        check(bk[K_GDAY] + bk[K_KDAY] + bk[K_BPG] + bk[K_BPK] + bk[K_LIVE]
              == H_MAIN,
              "F5c: slot-day accounting identity = H exactly: %s T=%d"
              % (cell_key(name, B), T))
        GTAB[(name, B)][T] = g
        BOOK[(name, B)][T] = bk

for name, _ in PRIORS:
    for T in TS:
        gs = [GTAB[(name, B)][T] for B in BS]
        check(gs[0] >= gs[1] >= gs[2],
              "F5a: G non-increasing in B, prior %s T=%d" % (name, T))

for B in BS:
    for T in TS:
        gdead = arm_a_G([Fraction(1)], [Fraction(0)], T, B, H_MAIN)[H_MAIN]
        bk = arm_a_book([Fraction(1)], [Fraction(0)], T, B, H_MAIN)
        renewals = bk[K_GRAD] + bk[K_KILL]
        check(gdead == 0 and bk[K_GRAD] == 0,
              "F5b: all-dead world exact zeros (T=%d,B=%d)" % (T, B))
        check(bk[K_KILL] == renewals,
              "F5b: all-dead kills == renewals (T=%d,B=%d)" % (T, B))
        check(bk[K_KILL] == (H_MAIN - T) // (T + B) + 1,
              "F5b: all-dead kill count matches closed form (T=%d,B=%d)"
              % (T, B))
        check(bk[K_KDAY] + bk[K_BPK] + bk[K_LIVE] == H_MAIN,
              "F5b: all-dead accounting (T=%d,B=%d)" % (T, B))

# --------------------------------------------- twin decision evaluators
DIRNAME = {7: "SHORTER", 14: "HELD", 30: "LONGER"}


def eval_one(tab, margin):
    """Evaluator ONE (procedural, Fraction arithmetic). Applies the
    registered band arithmetic; returns the PROVISIONAL class (REJECT /
    APPROVE_ARITH / NULL_ARITH) plus the full per-cell trace."""
    cells_out = {}
    over = []
    under = []
    for name, B in CELLS:
        g = tab[(name, B)]
        best = g[TS[0]]
        for T in TS[1:]:
            if g[T] > best:
                best = g[T]
        # argmax with ties to 14 first, then the earlier clock
        if g[14] == best:
            arg = 14
        elif g[7] == best:
            arg = 7
        else:
            arg = 30
        D = (best - g[14]) / g[14]
        d = DIRNAME[arg]
        cells_out[cell_key(name, B)] = (D, d)
        if D >= margin:
            over.append((name, B, d))
        else:
            under.append((name, B))
    sk_under = len([1 for name, B in under if name == "SKEPTIC"])
    if len(over) >= 7:
        dirs = set(d for _, _, d in over)
        if len(dirs) == 1 and dirs <= {"SHORTER", "LONGER"}:
            return "REJECT", cells_out, len(over), len(under), sk_under
    if len(under) >= 7 and sk_under >= 2:
        return "APPROVE_ARITH", cells_out, len(over), len(under), sk_under
    return "NULL_ARITH", cells_out, len(over), len(under), sk_under


def eval_two(tab, margin):
    """Evaluator TWO (independently written: pure-integer cross-multiplied
    comparisons, comprehension style). Same registered rule text."""
    mn, md = margin.numerator, margin.denominator

    def ge(a, b):  # a >= b for Fractions via integer cross-multiplication
        return a.numerator * b.denominator >= b.numerator * a.denominator

    trace = {}
    for name, B in CELLS:
        g = tab[(name, B)]
        arg = next(T for T in (14, 7, 30)
                   if all(ge(g[T], g[U]) for U in TS))
        best = g[arg]
        num = best - g[14]
        # D >= m  <=>  (best - G14) * md >= mn * G14   (all quantities >= 0)
        overm = ge(num * md, g[14] * mn)
        D = num / g[14]
        trace[cell_key(name, B)] = (D, DIRNAME[arg], overm)
    over_dirs = [d for _, (D, d, o) in sorted(trace.items()) if o]
    n_over = len(over_dirs)
    n_under = 9 - n_over
    sk_under = sum(1 for k, (D, d, o) in trace.items()
                   if k.startswith("SKEPTIC") and not o)
    cls = "NULL_ARITH"
    if n_over >= 7 and len(set(over_dirs)) == 1 and \
            over_dirs[0] in ("SHORTER", "LONGER"):
        cls = "REJECT"
    elif n_under >= 7 and sk_under >= 2:
        cls = "APPROVE_ARITH"
    cells_out = {k: (D, d) for k, (D, d, o) in trace.items()}
    return cls, cells_out, n_over, n_under, sk_under


def eval_both(tab, margin, label):
    r1 = eval_one(tab, margin)
    r2 = eval_two(tab, margin)
    check(r1[0] == r2[0], "twin evaluators agree on class: %s" % label)
    check(r1[1] == r2[1], "twin evaluators agree per-cell (D, dir): %s" % label)
    check(r1[2:] == r2[2:], "twin evaluators agree on counts: %s" % label)
    return r1


# ------------------------------------------------------------- Arm S (MC)
class CountingRandom(random.Random):
    """The counting RNG wrapper — every random() call is tallied so the
    per-seed draw sentinels are checked against an actual call count."""

    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


# the ONLY four RNGs constructed, in pinned order
RNG_MAIN = CountingRandom(SEED_MAIN)
RNG_STAB = CountingRandom(SEED_STAB)
RNG_REP = CountingRandom(SEED_REP)
RNG_AUX = CountingRandom(SEED_AUX)


def mc_leg(rng, pmf, ps, T, B, H, N, blocks=False):
    """One MC leg. Pinned draw order per trajectory: p from the cell prior
    (ONE uniform draw against the cumulative pmf), then daily sale trials
    day-by-day (each live day exactly ONE Bernoulli draw), repeating across
    renewals. Returns (sum_grads, sum_grads_sq, p_draws, day_draws,
    live_days_recorded, launches_recorded)."""
    cum = []
    acc = Fraction(0)
    for w in pmf:
        acc += w
        cum.append(float(acc))
    cum[-1] = 1.0
    pf = [float(p) for p in ps]
    rr = rng.random
    tg = 0
    tg2 = 0
    pdraws = 0
    daydraws = 0
    live = 0
    launches = 0
    for _ in range(N):
        rem = H
        g = 0
        while rem >= 1:
            pdraws += 1
            u = rr()
            i = 0
            while u >= cum[i]:
                i += 1
            p = pf[i]
            limit = T if T < rem else rem
            sold = 0
            if p == 0.0:
                for _ in range(limit):
                    rr()
                daydraws += limit
            else:
                for d in range(1, limit + 1):
                    if rr() < p:
                        sold = d
                        break
                daydraws += sold if sold else limit
            if sold:
                launches += 1
                live += sold
                g += 1
                if blocks:
                    rem = 0        # graduation BLOCKS the slot
                else:
                    rem = rem - sold - B
            elif T <= rem:         # kill at day T (even at horizon edge)
                launches += 1
                live += T
                rem = rem - T - B
            else:                  # censored live-at-horizon
                launches += 1
                live += rem
                rem = 0
        tg += g
        tg2 += g * g
    return tg, tg2, pdraws, daydraws, live, launches


def run_arm(rng, exact_tab, gate, N, H, grid, label, blocks=False):
    """27 legs in the pinned (cell, clock) order against exact_tab; the
    agreement gate + 4*SE headroom + draw sentinels asserted per leg."""
    legs = []
    ghat_tab = {}
    worst = Fraction(0)
    worst_leg = ""
    total_draws = 0
    for name, B in CELLS:
        ghat_tab[(name, B)] = {}
        for T in TS:
            tg, tg2, pd, dd, live, ln = mc_leg(
                rng, PMF[name], grid, T, B, H, N, blocks=blocks)
            check(dd == live,
                  "sentinel %s %s T=%d: daily-trial draws == recorded live "
                  "days" % (label, cell_key(name, B), T))
            check(pd == ln,
                  "sentinel %s %s T=%d: p-draws == recorded launches"
                  % (label, cell_key(name, B), T))
            total_draws += pd + dd
            ghat = Fraction(tg, N)
            ga = exact_tab[(name, B)][T]
            dev = abs(ghat - ga)
            var = (tg2 - N * (tg / N) ** 2) / (N - 1)
            sd = math.sqrt(var if var > 0 else 0.0)
            se4 = 4.0 * sd / math.sqrt(N)
            check(dev <= gate,
                  "arm agreement %s %s T=%d: |ArmS - ArmA| <= %s"
                  % (label, cell_key(name, B), T, fr(gate)))
            check(se4 <= float(gate),
                  "arm agreement %s %s T=%d: 4*SE headroom" %
                  (label, cell_key(name, B), T))
            if dev > worst:
                worst = dev
                worst_leg = "%s T=%d" % (cell_key(name, B), T)
            ghat_tab[(name, B)][T] = ghat
            legs.append({"cell": cell_key(name, B), "T": T, "N": N,
                         "sum_grads": tg, "Ghat": fr(ghat), "dev": fr(dev),
                         "dev_float": float(dev), "four_SE": se4,
                         "p_draws": pd, "day_draws": dd})
    return ghat_tab, legs, worst, worst_leg, total_draws


# ---------------------------------------------------------- decision (Arm A)
prov_cls, prov_cells, prov_over, prov_under, prov_sk = eval_both(
    GTAB, MARGIN, "Arm A provisional @ m=1/20")

# ------------------------------------------------------------- Arm S legs
mc_tab, mc_legs, mc_worst, mc_worst_leg, mc_draws = run_arm(
    RNG_MAIN, GTAB, GATE_MAIN, N_MAIN, H_MAIN, P_GRID, "main")
check(RNG_MAIN.calls == mc_draws,
      "sentinel seed 20261337: total random() calls == p-draws + daily-trial "
      "draws")

stab_tab, stab_legs, stab_worst, stab_worst_leg, stab_draws = run_arm(
    RNG_STAB, GTAB, GATE_STAB, N_STAB, H_MAIN, P_GRID, "stability")
check(RNG_STAB.calls == stab_draws,
      "sentinel seed 20261338: total random() calls == p-draws + daily-trial "
      "draws")
stab_cls, stab_cells, stab_over, stab_under, stab_sk = eval_both(
    stab_tab, MARGIN, "stability MC table @ m=1/20")

# ------------------------------------------- reporting-only worlds (Arm A)
G60 = {(n, B): {T: arm_a_G(PMF[n], P_GRID, T, B, 60)[60] for T in TS}
       for n, B in CELLS}
G180 = {(n, B): {T: arm_a_G(PMF[n], P_GRID, T, B, 180)[180] for T in TS}
        for n, B in CELLS}
GPRIME = {(n, B): {T: arm_a_G(PMF[n], P_SENS, T, B, H_MAIN)[H_MAIN]
                   for T in TS} for n, B in CELLS}
GBLK = {(n, B): {T: blocks_G(PMF[n], P_GRID, T, B, H_MAIN)[H_MAIN]
                 for T in TS} for n, B in CELLS}
for lbl, tab in (("H=60", G60), ("H=180", G180), ("P'", GPRIME),
                 ("blocks", GBLK)):
    for n, _ in PRIORS:
        for T in TS:
            gs = [tab[(n, B)][T] for B in BS]
            check(gs[0] >= gs[1] >= gs[2],
                  "F5a (world %s): G non-increasing in B, %s T=%d"
                  % (lbl, n, T))

# reporting-only MC confirmations, seed 20261339, pinned world order
rep_worlds = []
rep_draws_total = 0
for lbl, tab, H, grid, blocks in (
        ("H=60", G60, 60, P_GRID, False),
        ("H=180", G180, 180, P_GRID, False),
        ("P'", GPRIME, H_MAIN, P_SENS, False),
        ("blocks", GBLK, H_MAIN, P_GRID, True)):
    ttab, tlegs, tworst, tworst_leg, tdraws = run_arm(
        RNG_REP, tab, GATE_STAB, N_REP, H, grid, "reporting %s" % lbl,
        blocks=blocks)
    rep_draws_total += tdraws
    wcls, wcells, wover, wunder, wsk = eval_both(
        tab, MARGIN, "reporting world %s @ m=1/20" % lbl)
    rep_worlds.append({"world": lbl, "arith_class": wcls,
                       "over": wover, "under": wunder, "skeptic_under": wsk,
                       "cells": {k: {"D": fr(D), "D_float": float(D),
                                     "dir": d} for k, (D, d) in
                                 sorted(wcells.items())},
                       "G": {cell_key(n, B): {str(T): fr(tab[(n, B)][T])
                                              for T in TS}
                             for n, B in CELLS},
                       "mc_worst_dev": fr(tworst),
                       "mc_worst_dev_float": float(tworst),
                       "mc_worst_leg": tworst_leg,
                       "mc_legs": tlegs})
check(RNG_REP.calls == rep_draws_total,
      "sentinel seed 20261339: total random() calls == p-draws + daily-trial "
      "draws")
check(RNG_AUX.calls == 0,
      "sentinel seed 20261340 (aux): constructed in pinned order, RESERVED, "
      "zero draws — never read by any decision number")

# ------------------------------------------------------------- margin sweep
sweep_out = []
for m in SWEEP:
    scls, scells, sover, sunder, ssk = eval_both(
        GTAB, m, "margin sweep m=%s" % fr(m))
    sweep_out.append({"m": fr(m), "arith_class": scls, "over": sover,
                      "under": sunder, "skeptic_under": ssk})

# ---------------------------------------------------------------- final ruling
# Registered evaluation order: REJECT checked FIRST, then APPROVE (whose
# stability conjunct is the seed-20261338 leg reproducing the ruling through
# the twin evaluators), else NULL.
if prov_cls == "REJECT":
    FINAL = "reject"
    final_note = "REJECT fired on Arm A exact numbers (checked FIRST)"
elif prov_cls == "APPROVE_ARITH" and stab_cls == "APPROVE_ARITH":
    FINAL = "approve"
    final_note = ("REJECT does not fire (%d of 9 over-margin, 7 required); "
                  "APPROVE arithmetic fires (%d of 9 under margin, %d of 3 "
                  "SKEPTIC) AND the seed-20261338 stability leg reproduces "
                  "the ruling through both twin evaluators"
                  % (prov_over, prov_under, prov_sk))
else:
    FINAL = "null"
    if prov_cls == "APPROVE_ARITH":
        final_note = ("APPROVE arithmetic fired but the stability leg did "
                      "NOT reproduce it (stability class %s) — NULL"
                      % stab_cls)
    else:
        final_note = "neither REJECT nor APPROVE arithmetic fired — NULL"

# NULL axis bookkeeping (reported always; binding only on NULL)
over_cells = [(n, B, prov_cells[cell_key(n, B)][1]) for n, B in CELLS
              if prov_cells[cell_key(n, B)][0] >= MARGIN]
over_dirs = set(d for _, _, d in over_cells)
axis_flags = {
    "direction_straddle_among_over_margin_cells":
        len(over_dirs) > 1,
    "over_margin_cells_concentrate_in_one_B_column":
        len(set(B for _, B, _ in over_cells)) == 1 and len(over_cells) > 0,
    "margin_thin_ruling_flips_inside_sweep":
        any(s["arith_class"] != prov_cls for s in sweep_out),
    "arm_disagreement": False,   # gate passed or the run would have exited
    "sensitivity_straddle_world_class_differs":
        any(w["arith_class"] != prov_cls for w in rep_worlds),
}

# ------------------------------------------------------- drafter comparison
DRAFTER = FX["drafter_reference_never_gated"]
drafter_cmp = []
nonzero = {e["cell"]: e for e in DRAFTER["expected_nonzero_cells"]}
zero_cells_measured = 0
for n, B in CELLS:
    D, d = prov_cells[cell_key(n, B)]
    if D == 0:
        zero_cells_measured += 1
    exp = nonzero.get(cell_key(n, B))
    if exp is not None:
        drafter_cmp.append({
            "cell": cell_key(n, B),
            "drafter_D_approx": exp["D_approx"],
            "drafter_dir": exp["dir"],
            "measured_D": fr(D), "measured_D_float": float(D),
            "measured_dir": d,
            "matches_to_4dp": (round(float(D), 4) == exp["D_approx"]
                               and d == exp["dir"]),
        })
drafter_zero_match = (zero_cells_measured == DRAFTER["expected_D_zero_cells"])

# ------------------------------------------------------------------ output
def dtab_lines(tab, cells_eval):
    lines = []
    for n, B in CELLS:
        g = tab[(n, B)]
        D, d = cells_eval[cell_key(n, B)]
        lines.append(
            "  %-13s G(7)=%.6f  G(14)=%.6f  G(30)=%.6f  D=%.6f  dir=%s"
            % (cell_key(n, B), float(g[7]), float(g[14]), float(g[30]),
               float(D), d))
        # exact rationals for every G and D are committed in results.json
    return lines


out = []
out.append("VERDICT 061 — kill-clock horizon (idea-engine PROPOSAL 050)")
out.append("registration: %s" % FX["registration"]["proposal_header"])
out.append("environment: CPython %d.%d (pinned)" % tuple(sys.version_info[:2]))
out.append("")
out.append("ARM A (DECISION, exact Fractions, seedless) — 9 x 3 G table, "
           "H = 90:")
out.extend(dtab_lines(GTAB, prov_cells))
out.append("")
out.append("decision arithmetic @ m = 1/20 (twin evaluators agree): "
           "class=%s over=%d under=%d skeptic_under=%d"
           % (prov_cls, prov_over, prov_under, prov_sk))
out.append("ARM S main (seed 20261337, N = 200,000/leg, 27 legs): all legs "
           "within 3/200 + 4*SE headroom; worst |dev| = %.6f at %s"
           % (float(mc_worst), mc_worst_leg))
out.append("STABILITY (seed 20261338, N = 20,000/leg, gate 3/50): class=%s "
           "over=%d under=%d skeptic_under=%d; worst |dev| = %.6f at %s"
           % (stab_cls, stab_over, stab_under, stab_sk,
              float(stab_worst), stab_worst_leg))
out.append("")
out.append("REPORTING-ONLY (never flip the decision):")
for w in rep_worlds:
    out.append("  world %-7s arith_class=%s over=%d under=%d "
               "skeptic_under=%d mc_worst_dev=%.6f at %s"
               % (w["world"], w["arith_class"], w["over"], w["under"],
                  w["skeptic_under"], w["mc_worst_dev_float"],
                  w["mc_worst_leg"]))
for s in sweep_out:
    out.append("  margin sweep m=%-5s arith_class=%s over=%d under=%d "
               "skeptic_under=%d"
               % (s["m"], s["arith_class"], s["over"], s["under"],
                  s["skeptic_under"]))
out.append("  axis flags: %s" % json.dumps(axis_flags, sort_keys=True))
out.append("")
out.append("PER-CELL bookkeeping (Arm A exact, per clock T — kills / idle "
           "(build) days split post-grad+post-kill / live-at-horizon days / "
           "wasted graduations vs the 30-day window / launches):")
for n, B in CELLS:
    for T in TS:
        bk = BOOK[(n, B)][T]
        out.append(
            "  %-13s T=%-2d kills=%.4f idle=%.4f (pg=%.4f pk=%.4f) "
            "liveH=%.4f wasted=%.6f launches=%.4f"
            % (cell_key(n, B), T, float(bk[K_KILL]),
               float(bk[K_BPG] + bk[K_BPK]), float(bk[K_BPG]),
               float(bk[K_BPK]), float(bk[K_LIVE]), float(bk[K_WASTE]),
               float(bk[K_LAUNCH])))
out.append("")
out.append("PER-P conditional graduation split (Arm A exact, grads by true "
           "p row 0, 1/60, 1/30, 1/14, 1/7):")
for n, B in CELLS:
    for T in TS:
        bk = BOOK[(n, B)][T]
        out.append("  %-13s T=%-2d grads_by_p=[%s] kills_by_p=[%s]"
                   % (cell_key(n, B), T,
                      ", ".join("%.6f" % float(bk[K_PG + i])
                                for i in range(NP)),
                      ", ".join("%.6f" % float(bk[K_PK + i])
                                for i in range(NP))))
out.append("")
out.append("DRAFTER REFERENCE (disclosed, re-derived from scratch, compared "
           "NEVER gated): zero-D cells measured=%d expected=%d match=%s"
           % (zero_cells_measured, DRAFTER["expected_D_zero_cells"],
              drafter_zero_match))
for c in drafter_cmp:
    out.append("  %-13s drafter D~%.4f %s | measured D=%.6f %s | 4dp "
               "match=%s" % (c["cell"], c["drafter_D_approx"],
                             c["drafter_dir"], c["measured_D_float"],
                             c["measured_dir"], c["matches_to_4dp"]))
out.append("")
out.append("SENTINELS: seed 20261337 calls=%d; seed 20261338 calls=%d; "
           "seed 20261339 calls=%d; seed 20261340 (aux) calls=%d (reserved, "
           "never read by any decision number)"
           % (RNG_MAIN.calls, RNG_STAB.calls, RNG_REP.calls, RNG_AUX.calls))
out.append("")
out.append("RULING (registered evaluation order REJECT -> APPROVE -> NULL, "
           "m = 1/20 exact): %s" % FINAL.upper())
out.append("  %s" % final_note)

RESULTS = {
    "verdict": "VERDICT 061",
    "registration": FX["registration"],
    "environment": {"cpython": list(sys.version_info[:2])},
    "arm_A": {
        "H": H_MAIN,
        "G_table": {cell_key(n, B): {str(T): fr(GTAB[(n, B)][T])
                                     for T in TS} for n, B in CELLS},
        "D_table": {k: {"D": fr(D), "D_float": float(D), "dir": d}
                    for k, (D, d) in sorted(prov_cells.items())},
        "provisional_class": prov_cls,
        "over": prov_over, "under": prov_under, "skeptic_under": prov_sk,
        "bookkeeping": {
            cell_key(n, B): {
                str(T): {
                    "grads": fr(BOOK[(n, B)][T][K_GRAD]),
                    "kills": fr(BOOK[(n, B)][T][K_KILL]),
                    "grad_days": fr(BOOK[(n, B)][T][K_GDAY]),
                    "kill_days": fr(BOOK[(n, B)][T][K_KDAY]),
                    "build_days_post_grad": fr(BOOK[(n, B)][T][K_BPG]),
                    "build_days_post_kill": fr(BOOK[(n, B)][T][K_BPK]),
                    "live_at_horizon_days": fr(BOOK[(n, B)][T][K_LIVE]),
                    "launches": fr(BOOK[(n, B)][T][K_LAUNCH]),
                    "wasted_graduations_vs_30d_window":
                        fr(BOOK[(n, B)][T][K_WASTE]),
                    "grads_by_p": [fr(BOOK[(n, B)][T][K_PG + i])
                                   for i in range(NP)],
                    "kills_by_p": [fr(BOOK[(n, B)][T][K_PK + i])
                                   for i in range(NP)],
                } for T in TS
            } for n, B in CELLS
        },
    },
    "arm_S_main": {"seed": SEED_MAIN, "N": N_MAIN, "legs": mc_legs,
                   "worst_dev": fr(mc_worst), "worst_leg": mc_worst_leg},
    "stability": {"seed": SEED_STAB, "N": N_STAB, "legs": stab_legs,
                  "class": stab_cls, "over": stab_over, "under": stab_under,
                  "skeptic_under": stab_sk, "worst_dev": fr(stab_worst),
                  "worst_leg": stab_worst_leg,
                  "D_table": {k: {"D": fr(D), "D_float": float(D), "dir": d}
                              for k, (D, d) in sorted(stab_cells.items())}},
    "reporting_worlds": rep_worlds,
    "margin_sweep": sweep_out,
    "axis_flags": axis_flags,
    "drafter_comparison_never_gated": {
        "zero_D_cells_measured": zero_cells_measured,
        "zero_D_cells_expected": DRAFTER["expected_D_zero_cells"],
        "zero_D_match": drafter_zero_match,
        "nonzero_cells": drafter_cmp,
    },
    "sentinels": {
        "seed_20261337_calls": RNG_MAIN.calls,
        "seed_20261338_calls": RNG_STAB.calls,
        "seed_20261339_calls": RNG_REP.calls,
        "seed_20261340_calls": RNG_AUX.calls,
    },
    "ruling": {"final": FINAL, "note": final_note,
               "evaluation_order": ["REJECT (checked FIRST)",
                                    "APPROVE (with stability conjunct)",
                                    "NULL (five registered axes)"],
               "margin": fr(MARGIN)},
}

res_json = json.dumps(RESULTS, indent=2, sort_keys=True) + "\n"
with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(res_json)
check(len(res_json) > 1000, "results.json written")

out.append("SELF-CHECKS: %d passed, %d failed"
           % (_CHECKS["passed"], _CHECKS["failed"]))
body = "\n".join(out) + "\n"
sys.stdout.write(body)
