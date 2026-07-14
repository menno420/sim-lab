#!/usr/bin/env python3
"""VERDICT 062 — chicken-farm faucet self-balance (idea-engine PROPOSAL 051 / INTAKE 051).

Hermetic, stdlib-only, fully deterministic. Reads ONLY its own fixtures.json.
Arm A: seedless exact integer/Fraction decision trajectories (alone decision-bearing).
Arm S: seeded jittered robustness (random.Random with the four pre-registered
seeds 20261341-344 — the ONLY RNGs constructed).
Run: python3 farm_faucet_sim.py  (writes results.json next to itself; stdout is
the audit log — byte-identical across process runs, no wall-clock anywhere).
"""
import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ---------------------------------------------------------------- self-checks
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    line = "[check %03d] %s - %s" % (len(CHECKS), "PASS" if ok else "FAIL", name)
    if detail and not ok:
        line += " :: " + str(detail)
    print(line)


def frac_str(fr):
    fr = Fraction(fr)
    return "%d/%d" % (fr.numerator, fr.denominator)


# ---------------------------------------------------------------- constants
FC = FX["farm_constants"]
LAY = FC["LAY_INTERVAL_SECONDS"]
EV = FC["EGG_VALUE"]
MAX_CH = FC["MAX_CHICKENS"]
MAX_LVL = FC["MAX_COOP_LEVEL"]
BASE_CAP = FC["BASE_CAPACITY"]
CAP_PER = FC["CAPACITY_PER_LEVEL"]
BASE_HEN = FC["BASE_CHICKEN_PRICE"]
HEN_GROW = FC["CHICKEN_PRICE_GROWTH"]
BASE_COOP = FC["BASE_COOP_PRICE"]
COOP_GROW = FC["COOP_PRICE_GROWTH"]

CADENCES = FX["cadences_s"]
POLICIES = FX["policies"]
H_END = FX["horizon_days"] * 86400
WIN_LO = (FX["window_days_inclusive"][0] - 1) * 86400
WIN_DAYS = FX["window_days_inclusive"][1] - FX["window_days_inclusive"][0] + 1
P_MAX = Fraction(FX["p_max_days"])
E_DAILY = Fraction(*FX["E_daily_fraction"])
THR = Fraction(*FX["reject_threshold_fraction"])
SPEND_CAP = FX["spend_cap_multiple"] * E_DAILY
SEEDS = FX["seeds"]

check("cpython minor pinned == %s" % (tuple(FX["python_minor"]),),
      sys.version_info[:2] == tuple(FX["python_minor"]),
      sys.version)
check("seeds strictly above prior high-water 20261340",
      min(SEEDS.values()) > FX["seed_high_water_prior"]
      and sorted(SEEDS.values()) == [20261341, 20261342, 20261343, 20261344])
check("decision grid transcription (cadences, policies, kappa, band constants)",
      CADENCES == [900, 3600, 14400, 86400]
      and POLICIES == ["GREEDY", "PAIR", "HEN_ONLY", "COOP_ONLY", "ALT"]
      and FX["kappa"] == [1, 2] and THR == E_DAILY / 2
      and FX["reject_cells_required"] == 2 and FX["p_max_days"] == 14)


def cap_of(level):
    return BASE_CAP + CAP_PER * max(0, level)


def hen_price(current):
    return int(round(BASE_HEN * HEN_GROW ** max(0, current - 1)))


def coop_price(level):
    return int(round(BASE_COOP * COOP_GROW ** max(0, level)))


# F1 — price tables re-derived from the committed float formulas
hen_table = [hen_price(k + 1) for k in range(15)]
coop_table = [coop_price(k) for k in range(10)]
check("F1 hen price table (extras 0-14) re-derived == fixture",
      hen_table == FX["hen_price_table_extras_0_14"], hen_table)
check("F1 coop price table (L0-9) re-derived == fixture",
      coop_table == FX["coop_price_table_L0_9"], coop_table)
check("F1 coop ladder total == 44506",
      sum(coop_table) == FX["coop_ladder_total"], sum(coop_table))

# F4 — anchor
E_derived = sum(Fraction(w) * Fraction(lo + hi, 2) for lo, hi, w in FX["daily_tiers"]) / 100
check("F4 E[!daily] == 169201/100 exact", E_derived == E_DAILY, frac_str(E_derived))
check("F4 kappa*E == 169201/200 exact", E_derived / 2 == THR, frac_str(E_derived / 2))


# ---------------------------------------------------------------- engine
def settle(n, level, eggs, upd, now, lay=LAY):
    """farm.settle @ affd7ea, verbatim semantics."""
    c = cap_of(level)
    if n <= 0:
        return (min(eggs, c), now)
    if eggs >= c:
        return (c, now)
    elapsed = max(0, now - upd)
    iv = elapsed // lay
    ne = eggs + iv * n
    if ne >= c:
        return (c, now)
    return (ne, upd + iv * lay)


def R_rate(n, level, delta, ev=EV, lay=LAY):
    """Exact steady-state coins/day at cadence delta (Fraction)."""
    epc = delta // lay
    return Fraction(min(cap_of(level), n * epc) * ev * 86400, delta)


# F2 — settle identities on a pinned state grid
f2_ok = True
f2_detail = ""
state_grid = [(n, L, e) for n in (0, 1, 2, 5, 13, 100) for L in (0, 1, 5, 10)
              for e in (0, 1, cap_of(L) - 1, cap_of(L))]
for (n, L, e) in state_grid:
    for dt in (0, 1, 299, 300, 301, 899, 900, 3599, 86400):
        once = settle(n, L, e, 0, dt)
        # idempotence
        if settle(n, L, once[0], once[1], dt) != once:
            f2_ok, f2_detail = False, "idempotence (%s,%s,%s,%s)" % (n, L, e, dt)
        # composition second-by-second (docstring invariant), bounded window
        if dt <= 901:
            se, su = e, 0
            for t in range(1, dt + 1):
                se, su = settle(n, L, se, su, t)
            if (se, su) != once:
                f2_ok, f2_detail = False, "composition (%s,%s,%s,%s)" % (n, L, e, dt)
check("F2 settle idempotence + settling-every-second == settling-once (pinned grid)",
      f2_ok, f2_detail)
check("F2 cap clamp: eggs >= cap settles to (cap, now)",
      settle(3, 0, 25, 0, 1234) == (20, 1234) and settle(1, 0, 20, 0, 7) == (20, 7))
check("F2 zero-hen clock advance keeps eggs",
      settle(0, 0, 5, 0, 99999) == (5, 99999) and settle(0, 0, 0, 0, 50) == (0, 50))
check("F2 remainder preserved below cap (updated_at advances by iv*300 only)",
      settle(1, 0, 0, 0, 450) == (1, 300) and settle(2, 1, 3, 100, 1000) == (9, 1000))

# F3 — the L2 arithmetic gate: fresh farm, no collects
e6000 = settle(1, 0, 0, 0, FX["F3"]["t_full"])
e7200 = settle(1, 0, 0, 0, FX["F3"]["t_after"])
check("F3 exactly 40 coins collectible at t=6000s",
      e6000[0] * EV == FX["F3"]["coins_at_full"], e6000)
check("F3 zero further accrual at t=7200s", e7200[0] * EV == FX["F3"]["coins_at_full"], e7200)

# F5 — daily-hen-worthlessness identity
f5_ok = all(R_rate(2, L, 86400) - R_rate(1, L, 86400) == 0 for L in range(0, MAX_LVL + 1))
check("F5 2nd-hen marginal exactly 0 at Delta=86400 for EVERY coop level 0..10 (288>=170)",
      f5_ok)

# design ceiling row
ceil_ok = all(R_rate(100, 10, d) == FX["design_ceiling_row"][str(d)] for d in CADENCES)
check("design-ceiling row R(100,10,Delta) == {32640, 8160, 2040, 340}", ceil_ok,
      {d: frac_str(R_rate(100, 10, d)) for d in CADENCES})

# monotonicity: R non-decreasing in n and in L (pinned grid)
mono_nL = True
for d in CADENCES:
    for L in range(0, 11):
        for n in range(1, 30):
            if R_rate(n + 1, L, d) < R_rate(n, L, d):
                mono_nL = False
    for n in (1, 2, 8, 13, 100):
        for L in range(0, 10):
            if R_rate(n, L + 1, d) < R_rate(n, L, d):
                mono_nL = False
check("monotonicity: R non-decreasing in n and in L (pinned grid, all cadences)", mono_nL)


# ---------------------------------------------------------------- policies
class Ctx(object):
    """Per-(delta, policy, pmax, ev, lay) option memo. Plans qualified on
    positive marginal + payback <= pmax at the NOMINAL cadence."""

    def __init__(self, delta, policy, pmax=P_MAX, ev=EV, lay=LAY):
        self.delta = delta
        self.policy = policy
        self.pmax = pmax
        self.ev = ev
        self.lay = lay
        self.memo = {}

    def _qualify(self, kinds, price, n, L, n2, L2):
        base = R_rate(n, L, self.delta, self.ev, self.lay)
        after = R_rate(n2, L2, self.delta, self.ev, self.lay)
        marg = after - base
        if marg <= 0:
            return None
        payback = Fraction(price) / marg
        if payback > self.pmax:
            return None
        kind_ord = 0 if kinds[0] == "hen" else 1
        return ((payback, len(kinds), price, kind_ord), price, kinds, payback)

    def plans(self, n, L, alt_next=None):
        key = (n, L) if self.policy != "ALT" else (n, L, alt_next)
        got = self.memo.get(key)
        if got is not None:
            return got
        out = []
        pol = self.policy
        can_hen = n < MAX_CH
        can_coop = L < MAX_LVL
        if pol in ("GREEDY", "PAIR", "HEN_ONLY") or (pol == "ALT" and alt_next == "hen"):
            if can_hen:
                q = self._qualify(("hen",), hen_price(n), n, L, n + 1, L)
                if q:
                    out.append(q)
        if pol in ("GREEDY", "PAIR", "COOP_ONLY") or (pol == "ALT" and alt_next == "coop"):
            if can_coop:
                q = self._qualify(("coop",), coop_price(L), n, L, n, L + 1)
                if q:
                    out.append(q)
        if pol == "PAIR":
            if n + 2 <= MAX_CH:
                q = self._qualify(("hen", "hen"), hen_price(n) + hen_price(n + 1),
                                  n, L, n + 2, L)
                if q:
                    out.append(q)
            if can_hen and can_coop:
                q = self._qualify(("hen", "coop"), hen_price(n) + coop_price(L),
                                  n, L, n + 1, L + 1)
                if q:
                    out.append(q)
            if L + 2 <= MAX_LVL:
                q = self._qualify(("coop", "coop"), coop_price(L) + coop_price(L + 1),
                                  n, L, n, L + 2)
                if q:
                    out.append(q)
        out.sort(key=lambda p: p[0])
        self.memo[key] = out
        return out


def buy_loop(ctx, n, L, wallet, alt_next, t, log):
    """Execute the policy at a check-in. wallet None == WHALE (unbounded).
    Returns (n, L, wallet, alt_next, bought_any, walled_now)."""
    bought = False
    while True:
        plans = ctx.plans(n, L, alt_next)
        if not plans:
            return n, L, wallet, alt_next, bought, True
        chosen = None
        for pl in plans:
            if wallet is None or pl[1] <= wallet:
                chosen = pl
                break
        if chosen is None:
            return n, L, wallet, alt_next, bought, False
        _, total, kinds, payback = chosen
        for kd in kinds:
            price = hen_price(n) if kd == "hen" else coop_price(L)
            if log is not None:
                log.append({"kind": kd, "price": price,
                            "plan": "+".join(kinds),
                            "plan_payback_days": frac_str(payback),
                            "day": frac_str(Fraction(t, 86400))})
            if kd == "hen":
                n += 1
            else:
                L += 1
            if ctx.policy == "ALT":
                alt_next = "hen" if kd == "coop" else "coop"
        if wallet is not None:
            wallet -= total
            if wallet < 0:
                raise AssertionError("negative wallet")
        bought = True


def arm_A(delta, policy, pmax=P_MAX, whale=False, ev=EV, lay=LAY):
    """Seedless exact decision trajectory."""
    ctx = Ctx(delta, policy, pmax, ev, lay)
    n, L, eggs, upd = FC["STARTER_CHICKENS"], 0, 0, 0
    wallet = None if whale else 0
    alt_next = "coop"
    log = []
    wall_day = None
    kmax = H_END // delta
    for k in range(1, kmax + 1):
        t = k * delta
        e2, u2 = settle(n, L, eggs, upd, t, lay)
        if e2 > 0:
            if wallet is not None:
                wallet += e2 * ev
            eggs, upd = 0, t
        n, L, wallet, alt_next, bought, walled = buy_loop(ctx, n, L, wallet, alt_next, t, log)
        if bought:
            eggs, upd = 0, t
        if walled and wall_day is None:
            wall_day = Fraction(t, 86400)
    spend = sum(p["price"] for p in log)
    plateau = R_rate(n, L, delta, ev, lay)
    epc = delta // lay
    contributing = min(n, -(-cap_of(L) // epc)) if epc > 0 else 0
    zm_share = Fraction(n - contributing, n)
    return {
        "final_n": n, "final_L": L, "plateau": plateau, "wall_day": wall_day,
        "purchases": log, "spend": spend, "zm_hen_share": zm_share,
        "final_wallet": wallet,
    }


def arm_A_with_events(delta, policy, pmax=P_MAX, ev=EV, lay=LAY):
    """Same trajectory, recording the full per-check-in event log for the
    degenerate-identity gate and F6."""
    ctx = Ctx(delta, policy, pmax, ev, lay)
    n, L, eggs, upd = FC["STARTER_CHICKENS"], 0, 0, 0
    wallet = 0
    alt_next = "coop"
    events = []
    log = []
    kmax = H_END // delta
    for k in range(1, kmax + 1):
        t = k * delta
        e2, u2 = settle(n, L, eggs, upd, t, lay)
        coins = e2 * ev
        if e2 > 0:
            wallet += coins
            eggs, upd = 0, t
        else:
            coins = 0
        before = len(log)
        n, L, wallet, alt_next, bought, walled = buy_loop(ctx, n, L, wallet, alt_next, t, log)
        if bought:
            eggs, upd = 0, t
        events.append((t, e2, coins,
                       tuple((p["kind"], p["price"]) for p in log[before:]), wallet))
    return events


# ---------------------------------------------------------------- Arm S
def make_counted(seed):
    rng = random.Random(seed)
    base = rng.random
    count = [0]

    def rnd():
        count[0] += 1
        return base()

    return rnd, count


def gap_bounds(delta, width_num, width_den):
    lo = (delta * (width_den - width_num) + width_den - 1) // width_den
    hi = (delta * (width_den + width_num)) // width_den
    return lo, hi


def arm_S_cell(delta, policy, N, rnd, pmax=P_MAX, ev=EV, lay=LAY,
               width=(1, 2), skip_num=1, skip_den=10):
    """Jittered robustness cell. Returns (Sx, Sxx, attempts)."""
    ctx = Ctx(delta, policy, pmax, ev, lay)
    plans_of = ctx.plans
    lo, hi = gap_bounds(delta, width[0], width[1])
    span = hi - lo + 1
    skip_p = skip_num / skip_den
    h_end = H_END
    win_lo = WIN_LO
    is_alt = (policy == "ALT")
    Sx = 0
    Sxx = 0
    attempts = 0
    for _ in range(N):
        n = 1
        L = 0
        capv = cap_of(0)
        upd = 0
        wallet = 0
        alt_next = "coop"
        walled = False
        t = 0
        wcoins = 0
        while True:
            attempts += 1
            r1 = rnd()
            r2 = rnd()
            t += lo + int(r1 * span)
            if t > h_end:
                break
            if r2 < skip_p:
                continue
            e = ((t - upd) // lay) * n
            if e > capv:
                e = capv
            if e > 0:
                coins = e * ev
                wallet += coins
                upd = t
                if t > win_lo:
                    wcoins += coins
            if not walled:
                bought = False
                while True:
                    plans = plans_of(n, L, alt_next) if is_alt else plans_of(n, L)
                    if not plans:
                        walled = True
                        break
                    chosen = None
                    for pl in plans:
                        if pl[1] <= wallet:
                            chosen = pl
                            break
                    if chosen is None:
                        break
                    wallet -= chosen[1]
                    for kd in chosen[2]:
                        if kd == "hen":
                            n += 1
                        else:
                            L += 1
                            capv = cap_of(L)
                        if is_alt:
                            alt_next = "hen" if kd == "coop" else "coop"
                    bought = True
                if bought:
                    upd = t
        Sx += wcoins
        Sxx += wcoins * wcoins
    return Sx, Sxx, attempts


def arm_S_degenerate(delta, policy, pmax=P_MAX, ev=EV, lay=LAY):
    """Arm-S machinery at degenerate jitter: gap == delta, skip off, ZERO draws.
    Returns the event log for the identity gate."""
    ctx = Ctx(delta, policy, pmax, ev, lay)
    n, L, upd, wallet = 1, 0, 0, 0
    capv = cap_of(0)
    alt_next = "coop"
    walled = False
    t = 0
    events = []
    while True:
        t += delta
        if t > H_END:
            break
        e = ((t - upd) // lay) * n
        if e > capv:
            e = capv
        coins = 0
        if e > 0:
            coins = e * ev
            wallet += coins
            upd = t
        buys = []
        if not walled:
            while True:
                plans = ctx.plans(n, L, alt_next) if policy == "ALT" else ctx.plans(n, L)
                if not plans:
                    walled = True
                    break
                chosen = None
                for pl in plans:
                    if pl[1] <= wallet:
                        chosen = pl
                        break
                if chosen is None:
                    break
                wallet -= chosen[1]
                for kd in chosen[2]:
                    price = hen_price(n) if kd == "hen" else coop_price(L)
                    buys.append((kd, price))
                    if kd == "hen":
                        n += 1
                    else:
                        L += 1
                        capv = cap_of(L)
                    if policy == "ALT":
                        alt_next = "hen" if kd == "coop" else "coop"
            if buys:
                upd = t
        events.append((t, e, coins, tuple(buys), wallet))
    return events


def stats_of(Sx, Sxx, N):
    mean = Fraction(Sx, WIN_DAYS * N)
    var = Fraction(N * Sxx - Sx * Sx, N * (N - 1) * WIN_DAYS * WIN_DAYS)
    se = math.sqrt(var / N)
    return mean, se


# ---------------------------------------------------------------- evaluators
def evaluator_one(bestA, armS, spends, greedy_first3, greedy_walls, thr, kappa_note=False):
    """Twin evaluator #1 — Fraction comparisons, registered order (REJECT first)."""
    fired = [d for d in CADENCES if bestA[d] >= thr]
    if len(fired) >= FX["reject_cells_required"]:
        all_ok = True
        for d in fired:
            mean, se = armS[d]
            if not (mean > thr and float(mean - thr) >= 4.0 * se):
                all_ok = False
            if Fraction(spends[d]) > SPEND_CAP:
                all_ok = False
        if all_ok:
            return ("REJECT", fired)
    approve = all(bestA[d] < thr for d in CADENCES)
    approve = approve and all(armS[d][0] < thr for d in CADENCES)
    for d in CADENCES:
        p3 = greedy_first3[d]
        if len(p3) < 3 or any(pb > FX["approve_first3_payback_days"] for pb in p3):
            approve = False
    wall_hits = sum(1 for d in CADENCES
                    if greedy_walls[d] is not None
                    and greedy_walls[d] >= FX["approve_wall_day_min"])
    if wall_hits < FX["approve_wall_cells_required"]:
        approve = False
    if approve:
        return ("APPROVE", fired)
    return ("NULL", fired)


def evaluator_two(bestA, armS_raw, spends, greedy_first3, greedy_walls, thr):
    """Twin evaluator #2 — independently written, pure-integer cross-multiplication."""
    tn, td = thr.numerator, thr.denominator
    fired = []
    for d in CADENCES:
        p = bestA[d]
        if p.numerator * td >= tn * p.denominator:
            fired.append(d)
    n_fired = 0
    for d in CADENCES:
        p = bestA[d]
        n_fired += 1 if p.numerator * td >= tn * p.denominator else 0
    if n_fired >= 2:
        bad = 0
        for d in fired:
            Sx, Sxx, N = armS_raw[d]
            # mean > thr  <=>  Sx * td > tn * WIN_DAYS * N
            if not (Sx * td > tn * WIN_DAYS * N):
                bad += 1
                continue
            mean_f = Sx / (WIN_DAYS * N)
            var_f = (N * Sxx - Sx * Sx) / (N * (N - 1) * WIN_DAYS * WIN_DAYS)
            se_f = math.sqrt(var_f / N)
            if not (mean_f - (tn / td) >= 4.0 * se_f):
                bad += 1
                continue
            # spend*10 <= 3*169201  (30*E = 507603/10)
            if spends[d] * SPEND_CAP.denominator > SPEND_CAP.numerator:
                bad += 1
        if bad == 0:
            return ("REJECT", fired)
    ok = True
    for d in CADENCES:
        p = bestA[d]
        if not (p.numerator * td < tn * p.denominator):
            ok = False
        Sx, Sxx, N = armS_raw[d]
        if not (Sx * td < tn * WIN_DAYS * N):
            ok = False
        p3 = greedy_first3[d]
        if len(p3) < 3:
            ok = False
        else:
            for pb in p3:
                if pb.numerator > FX["approve_first3_payback_days"] * pb.denominator:
                    ok = False
    hits = 0
    for d in CADENCES:
        w = greedy_walls[d]
        if w is not None and w.numerator >= FX["approve_wall_day_min"] * w.denominator:
            hits += 1
    if hits < FX["approve_wall_cells_required"]:
        ok = False
    if ok:
        return ("APPROVE", fired)
    return ("NULL", fired)


# ================================================================ RUN
print("VERDICT 062 - chicken-farm faucet self-balance - hermetic run")
print("engine @ superbot affd7ea (fixtures verbatim); anchor E[!daily] = %s = 1692.01"
      % frac_str(E_DAILY))
print("REJECT band: plateau(best-of-family) >= %s = 846.005 coins/day at >= 2 of 4 cadences"
      % frac_str(THR))
print("")

results = {"meta": {
    "verdict": FX["verdict"], "intake": FX["intake"],
    "proposal_header": FX["proposal_header"],
    "python": "%d.%d" % sys.version_info[:2],
    "seeds": SEEDS,
}}

# ---- Arm A decision grid (run TWICE in-process, identity-checked)
grids = []
for _pass in range(2):
    grid = {}
    for d in CADENCES:
        for pol in POLICIES:
            grid[(d, pol)] = arm_A(d, pol)
    grids.append(grid)
ident = all(
    grids[0][k]["plateau"] == grids[1][k]["plateau"]
    and grids[0][k]["wall_day"] == grids[1][k]["wall_day"]
    and grids[0][k]["spend"] == grids[1][k]["spend"]
    and grids[0][k]["purchases"] == grids[1][k]["purchases"]
    for k in grids[0])
check("two in-process Arm-A grid computations identical", ident)
GRID = grids[0]

armA_out = {}
print("ARM A - closed-wallet decision grid (plateau coins/day exact; wall days; spend)")
for d in CADENCES:
    for pol in POLICIES:
        g = GRID[(d, pol)]
        armA_out["%d/%s" % (d, pol)] = {
            "plateau": frac_str(g["plateau"]),
            "plateau_float": float(g["plateau"]),
            "final_state": [g["final_n"], g["final_L"]],
            "wall_day": None if g["wall_day"] is None else frac_str(g["wall_day"]),
            "wall_day_float": None if g["wall_day"] is None else float(g["wall_day"]),
            "spend": g["spend"],
            "zero_marginal_hen_share": frac_str(g["zm_hen_share"]),
            "purchases": g["purchases"],
        }
        print("  D=%-6d %-9s plateau=%-12s (%.3f/day, %.4fx E) n=%-3d L=%-2d wall=%s spend=%d"
              % (d, pol, frac_str(g["plateau"]), float(g["plateau"]),
                 float(g["plateau"] / E_DAILY), g["final_n"], g["final_L"],
                 "%.4f" % float(g["wall_day"]) if g["wall_day"] is not None else "none",
                 g["spend"]))
results["armA_grid"] = armA_out

check("wall day exists (converged) for every decision cell",
      all(GRID[(d, p)]["wall_day"] is not None for d in CADENCES for p in POLICIES))
check("every executed purchase in every cell rode a plan payback <= 14 days",
      all(Fraction(*map(int, pu["plan_payback_days"].split("/"))) <= P_MAX
          for d in CADENCES for p in POLICIES for pu in GRID[(d, p)]["purchases"]))

# best-of-family
best_pol = {}
bestA = {}
for d in CADENCES:
    bp = POLICIES[0]
    bv = GRID[(d, POLICIES[0])]["plateau"]
    for pol in POLICIES[1:]:
        v = GRID[(d, pol)]["plateau"]
        if v > bv:
            bp, bv = pol, v
    best_pol[d] = bp
    bestA[d] = bv
print("")
print("BEST-OF-FAMILY per cadence vs threshold %s (= 846.005):" % frac_str(THR))
for d in CADENCES:
    print("  D=%-6d best=%-9s plateau=%-12s -> %s" % (
        d, best_pol[d], frac_str(bestA[d]),
        "FIRES (>= threshold)" if bestA[d] >= THR else "under threshold"))
results["best_of_family"] = {
    str(d): {"policy": best_pol[d], "plateau": frac_str(bestA[d]),
             "plateau_float": float(bestA[d]),
             "ratio_to_E_daily": float(bestA[d] / E_DAILY),
             "fires_kappa_half": bool(bestA[d] >= THR)} for d in CADENCES}

# monotonicity along divisor chain at each cell's final state
chain_ok = True
for d in CADENCES:
    for pol in POLICIES:
        g = GRID[(d, pol)]
        rates = [R_rate(g["final_n"], g["final_L"], dd) for dd in (86400, 14400, 3600, 900)]
        if any(rates[i + 1] < rates[i] for i in range(3)):
            chain_ok = False
check("monotonicity: plateau non-decreasing along divisor chain 86400->14400->3600->900 "
      "at every cell's final state", chain_ok)

# F6 hand trajectory
f6 = FX["F6"]
ev6 = arm_A_with_events(f6["delta"], f6["policy"])[:5]
f6_ok = True
for i in range(5):
    t, e2, coins, buys, wallet = ev6[i]
    want_buy = f6["buys"][i]
    buy_ok = (buys == ()) if want_buy is None else (
        len(buys) == 1 and buys[0][0] == want_buy[0] and buys[0][1] == want_buy[1])
    if not (e2 == f6["eggs"][i] and coins == f6["coins"][i] and buy_ok
            and wallet == f6["wallet_after"][i]):
        f6_ok = False
check("F6 hand trajectory D=3600 GREEDY check-ins 1-5 (eggs/coins/buys/wallet exact)",
      f6_ok, ev6)

# ---- degenerate-jitter identity gate (Arm S machinery vs Arm A, event-for-event)
degen_ok = True
for d in CADENCES:
    for pol in POLICIES:
        evA = arm_A_with_events(d, pol)
        evS = arm_S_degenerate(d, pol)
        if evA != evS:
            degen_ok = False
check("Arm-S degenerate jitter == Arm A EVENT-FOR-EVENT on all 20 decision cells "
      "(zero rng draws)", degen_ok)

# ---- Arm S headline (seed 20261341)
rnd_main, cnt_main = make_counted(SEEDS["armS_main"])
N_HL = FX["armS"]["N_headline"]
armS_stats = {}
armS_raw = {}
attempts_total = 0
print("")
print("ARM S - jittered robustness, seed %d, N=%d/cell "
      "(gaps uniform int [ceil(D/2), floor(3D/2)], skip 1/10, window days 76-90)"
      % (SEEDS["armS_main"], N_HL))
for d in CADENCES:
    for pol in POLICIES:
        Sx, Sxx, att = arm_S_cell(d, pol, N_HL, rnd_main)
        attempts_total += att
        mean, se = stats_of(Sx, Sxx, N_HL)
        armS_stats[(d, pol)] = (mean, se)
        armS_raw[(d, pol)] = (Sx, Sxx, N_HL)
        print("  D=%-6d %-9s mean=%.3f/day se=%.4f (ArmA %s)"
              % (d, pol, float(mean), se, frac_str(GRID[(d, pol)]["plateau"])))
check("Arm-S headline draw sentinel: draws == 2 x attempted check-ins",
      cnt_main[0] == 2 * attempts_total, (cnt_main[0], attempts_total))
results["armS_headline"] = {
    "%d/%s" % (d, p): {"Sx": armS_raw[(d, p)][0], "Sxx": armS_raw[(d, p)][1],
                       "N": N_HL, "mean": frac_str(armS_stats[(d, p)][0]),
                       "mean_float": float(armS_stats[(d, p)][0]),
                       "se": armS_stats[(d, p)][1]}
    for d in CADENCES for p in POLICIES}
results["armS_headline_draws"] = {"draws": cnt_main[0], "attempts": attempts_total}

# confirmation on firing cells (best-of-family policy per cadence)
fired_cells = [d for d in CADENCES if bestA[d] >= THR]
conf = {}
print("")
print("REJECT confirmation on firing cells (best policy, mean > 846.005 with >= 4*SE headroom; "
      "spend <= 30*E = %s):" % frac_str(SPEND_CAP))
for d in fired_cells:
    mean, se = armS_stats[(d, best_pol[d])]
    spend = GRID[(d, best_pol[d])]["spend"]
    ok = bool(mean > THR and float(mean - THR) >= 4.0 * se and Fraction(spend) <= SPEND_CAP)
    conf[d] = ok
    print("  D=%-6d mean=%.3f headroom=%.3f (4*SE=%.4f) spend=%d -> %s"
          % (d, float(mean), float(mean - THR), 4.0 * se, spend,
             "CONFIRMS" if ok else "FAILS"))
results["reject_confirmation"] = {str(d): conf[d] for d in fired_cells}

# ---- decision (twin evaluators, registered order)
armS_best = {d: armS_stats[(d, best_pol[d])] for d in CADENCES}
armS_best_raw = {d: armS_raw[(d, best_pol[d])] for d in CADENCES}
spends_best = {d: GRID[(d, best_pol[d])]["spend"] for d in CADENCES}
greedy_first3 = {}
greedy_walls = {}
for d in CADENCES:
    g = GRID[(d, "GREEDY")]
    greedy_first3[d] = [Fraction(*map(int, pu["plan_payback_days"].split("/")))
                        for pu in g["purchases"][:3]]
    greedy_walls[d] = g["wall_day"]

class1, fired1 = evaluator_one(bestA, armS_best, spends_best, greedy_first3,
                               greedy_walls, THR)
class2, fired2 = evaluator_two(bestA, armS_best_raw, spends_best, greedy_first3,
                               greedy_walls, THR)
check("twin evaluators agree on the headline class", class1 == class2, (class1, class2))
check("twin evaluators agree on the firing cells", fired1 == fired2, (fired1, fired2))

# ---- stability leg (seed 20261342, N=500, full grid, both evaluators)
rnd_st, cnt_st = make_counted(SEEDS["stability"])
N_ST = FX["armS"]["N_stability"]
st_stats = {}
st_raw = {}
st_att = 0
for d in CADENCES:
    for pol in POLICIES:
        Sx, Sxx, att = arm_S_cell(d, pol, N_ST, rnd_st)
        st_att += att
        st_stats[(d, pol)] = stats_of(Sx, Sxx, N_ST)
        st_raw[(d, pol)] = (Sx, Sxx, N_ST)
check("stability-leg draw sentinel: draws == 2 x attempts",
      cnt_st[0] == 2 * st_att, (cnt_st[0], st_att))
st_best = {d: st_stats[(d, best_pol[d])] for d in CADENCES}
st_best_raw = {d: st_raw[(d, best_pol[d])] for d in CADENCES}
st_c1, _ = evaluator_one(bestA, st_best, spends_best, greedy_first3, greedy_walls, THR)
st_c2, _ = evaluator_two(bestA, st_best_raw, spends_best, greedy_first3, greedy_walls, THR)
check("stability leg (seed 20261342, N=500) reproduces the ruling through BOTH twin "
      "evaluators", st_c1 == class1 and st_c2 == class1, (st_c1, st_c2, class1))
results["stability"] = {
    "class_eval1": st_c1, "class_eval2": st_c2,
    "means": {"%d/%s" % (d, p): frac_str(st_stats[(d, p)][0])
              for d in CADENCES for p in POLICIES},
    "draws": cnt_st[0], "attempts": st_att}

# ---- reporting legs (seed 20261343) + seedless reporting arms
rnd_rep, cnt_rep = make_counted(SEEDS["reporting"])
N_REP = FX["armS"]["N_reporting"]
rep = {}

rep_att_total = 0

# extra cadence columns (Arm A all policies; jittered mean for best policy)
extra = {}
for d in FX["reporting_cadences_s"]:
    col = {}
    bp, bv = POLICIES[0], None
    for pol in POLICIES:
        g = arm_A(d, pol)
        col[pol] = {"plateau": frac_str(g["plateau"]),
                    "plateau_float": float(g["plateau"]),
                    "final_state": [g["final_n"], g["final_L"]],
                    "wall_day": None if g["wall_day"] is None else frac_str(g["wall_day"]),
                    "spend": g["spend"]}
        if bv is None or g["plateau"] > bv:
            bp, bv = pol, g["plateau"]
    Sx, Sxx, att = arm_S_cell(d, bp, N_REP, rnd_rep)
    rep_att_total += att
    mean, se = stats_of(Sx, Sxx, N_REP)
    col["_best"] = bp
    col["_jittered_mean_best"] = {"mean": frac_str(mean), "mean_float": float(mean),
                                  "se": se, "N": N_REP}
    extra[str(d)] = col
rep["extra_cadences"] = extra

# kappa sweep (pure arithmetic on Arm-A best plateaus)
ks = {}
for a, b in FX["kappa_sweep"]:
    thr_k = E_DAILY * Fraction(a, b)
    fired_k = [d for d in CADENCES if bestA[d] >= thr_k]
    ks["%d/%d" % (a, b)] = {"threshold": frac_str(thr_k), "fired_cells": fired_k,
                            "fires_ge2": len(fired_k) >= 2}
rep["kappa_sweep"] = ks
check("margin-thin axis does NOT bind: >= 2 cells fire at BOTH kappa = 1/3 and 2/3",
      all(v["fires_ge2"] for v in ks.values()), ks)

# jitter-width legs (best policy per cadence, widths 1/4 and 3/4)
jw = {}
for d in CADENCES:
    for a, b in FX["jitter_width_legs"]:
        Sx, Sxx, att = arm_S_cell(d, best_pol[d], N_REP, rnd_rep, width=(a, b))
        rep_att_total += att
        mean, se = stats_of(Sx, Sxx, N_REP)
        jw["%d@%d/%d" % (d, a, b)] = {"policy": best_pol[d], "mean": frac_str(mean),
                                      "mean_float": float(mean), "se": se}
rep["jitter_widths"] = jw
jw_fire_ok = all(
    Fraction(*map(int, jw["%d@%d/%d" % (d, a, b)]["mean"].split("/"))) > THR
    for d in fired_cells for a, b in FX["jitter_width_legs"])
check("every firing cell stays over the band at BOTH jitter widths (1/4, 3/4)", jw_fire_ok)

# P_max sweep (Arm A, seedless)
pm = {}
for pmax_d in FX["p_max_sweep"]:
    tab = {}
    for d in CADENCES:
        for pol in POLICIES:
            g = arm_A(d, pol, pmax=Fraction(pmax_d))
            tab["%d/%s" % (d, pol)] = {
                "plateau": frac_str(g["plateau"]),
                "wall_day": None if g["wall_day"] is None else frac_str(g["wall_day"]),
                "spend": g["spend"]}
    pm[str(pmax_d)] = tab
rep["p_max_sweep"] = pm
wall_mono = True
for d in CADENCES:
    for pol in POLICIES:
        ws = []
        for pmax_d in (7, 14, 28):
            if pmax_d == 14:
                w = GRID[(d, pol)]["wall_day"]
            else:
                wd = pm[str(pmax_d)]["%d/%s" % (d, pol)]["wall_day"]
                w = None if wd is None else Fraction(*map(int, wd.split("/")))
            ws.append(Fraction(10 ** 9) if w is None else w)
        if not (ws[0] <= ws[1] <= ws[2]):
            wall_mono = False
check("monotonicity: wall day non-decreasing in P_max (7 -> 14 -> 28), every cell",
      wall_mono)

# WHALE leg (Arm A, unbounded wallet)
wh = {}
whale_ok = True
for d in CADENCES:
    for pol in POLICIES:
        g = arm_A(d, pol, whale=True)
        wh["%d/%s" % (d, pol)] = {"plateau": frac_str(g["plateau"]),
                                  "wall_day": None if g["wall_day"] is None
                                  else frac_str(g["wall_day"]),
                                  "spend": g["spend"]}
        if GRID[(d, pol)]["plateau"] > g["plateau"]:
            whale_ok = False
rep["whale"] = wh
check("monotonicity: closed-wallet plateau <= WHALE plateau, every cell", whale_ok)

# knob tables (Arm A grids at EGG_VALUE=1 and LAY_INTERVAL=600)
knob = {}
for label, ev_k, lay_k in (("EGG_VALUE=1", 1, LAY),
                           ("LAY_INTERVAL=600", EV, 600)):
    tab = {}
    for d in CADENCES:
        for pol in POLICIES:
            g = arm_A(d, pol, ev=ev_k, lay=lay_k)
            tab["%d/%s" % (d, pol)] = {
                "plateau": frac_str(g["plateau"]),
                "plateau_float": float(g["plateau"]),
                "final_state": [g["final_n"], g["final_L"]],
                "over_band": bool(g["plateau"] >= THR)}
    knob[label] = tab
rep["knob_table"] = knob
check("knob sanity: R scales linearly in EGG_VALUE (final-state spot identity)",
      all(R_rate(GRID[(d, p)]["final_n"], GRID[(d, p)]["final_L"], d, ev=1)
          == GRID[(d, p)]["plateau"] / 2 for d in CADENCES for p in POLICIES))

rep["design_ceiling_row"] = {str(d): frac_str(R_rate(100, 10, d)) for d in CADENCES}
results["reporting"] = rep
results["reporting_draws"] = {"draws": cnt_rep[0], "attempts": rep_att_total}
check("reporting-leg draw sentinel: draws == 2 x attempted check-ins",
      cnt_rep[0] == 2 * rep_att_total, (cnt_rep[0], rep_att_total))

# family-split reporting note (NULL axis, reporting-only when REJECT fires)
fam = {}
for d in CADENCES:
    wg = GRID[(d, "GREEDY")]["wall_day"]
    wp = GRID[(d, "PAIR")]["wall_day"]
    fam[str(d)] = {"greedy_wall": frac_str(wg), "pair_wall": frac_str(wp),
                   "pair_extends_days": float(wp - wg)}
results["family_split_note"] = fam

# ---- aux seed gate
aux = random.Random(SEEDS["aux_never_read"])
check("aux seed 20261344 constructed and NEVER read (getstate identity)",
      aux.getstate() == random.Random(SEEDS["aux_never_read"]).getstate())

# ---- drafter comparison (reported, NEVER gated)
dd = FX["drafter_disclosed"]
cmp_rows = []
anoms = []
for d in CADENCES:
    ours = GRID[(d, "GREEDY")]["plateau"]
    theirs = dd["greedy_plateaus_coins_per_day"][str(d)]
    same = (ours == theirs)
    cmp_rows.append({"delta": d, "ours_greedy": frac_str(ours), "drafter": theirs,
                     "match": same})
    if not same:
        anoms.append("drafter GREEDY plateau at D=%d (%s) NOT reproduced under the "
                     "registered P_max=14 - ours %s" % (d, theirs, frac_str(ours)))
p28_900 = pm["28"]["900/GREEDY"]["plateau"]
results["drafter_comparison"] = {
    "rows": cmp_rows,
    "drafter_900_matches_pmax28_column": p28_900 == "8064/1"
    and dd["greedy_plateaus_coins_per_day"]["900"] == 8064,
    "note": "comparison only, never gated",
}
results["anomalies"] = anoms
print("")
print("DRAFTER COMPARISON (never gated): " + ("ALL MATCH" if not anoms else "; ".join(anoms)))

# ---- final class
final_class = class1
results["decision"] = {
    "class": final_class,
    "fired_cells": fired1,
    "threshold": frac_str(THR),
    "evaluators_agree": class1 == class2,
    "stability_reproduces": st_c1 == class1 and st_c2 == class1,
}
print("")
print("DECISION (registered order, REJECT first): %s" % final_class)
print("  firing cells: %s of 4 cadences over %s coins/day: %s"
      % (len(fired1), frac_str(THR), fired1))
for d in fired1:
    print("  D=%-6d best=%-9s plateau=%s = %.4fx E[!daily]"
          % (d, best_pol[d], frac_str(bestA[d]), float(bestA[d] / E_DAILY)))

# ---- checks summary + write results
n_fail = sum(1 for _, ok in CHECKS if not ok)
results["self_checks"] = {"passed": len(CHECKS) - n_fail, "failed": n_fail}
print("")
print("SELF-CHECKS: %d passed, %d failed" % (len(CHECKS) - n_fail, n_fail))

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("results.json written")

sys.exit(1 if n_fail else 0)
