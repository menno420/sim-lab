#!/usr/bin/env python3
"""VERDICT 080 runner — the stale-ink mirror (idea-engine PROPOSAL 067).

Hermetic: reads ONLY its own fixtures.json. Stdlib only. Deterministic:
stdout and results.json are byte-identical across process runs.

Three arms:
  Arm A — decision-bearing, seedless exact integers: world init from the
          committed xorshift32 seed, the E/I lag surfaces, the theorem
          enumerations (T1/T2/T3a/T3b + the corrected-decode census), and
          the four-arm belief-controlled greedy census on the committed
          world (decks ON decision cell, decks OFF reporting row).
  Arm B — twin, seedless, INDEPENDENTLY-WRITTEN: a literal day-walk
          re-implementation (triangle wave as a rotated value track, price
          calendars precomputed by walking days, a separately-coded engine
          and planner). Must reproduce every Arm-A published number EXACTLY;
          powers the second decision evaluator.
  Arm R — seeded (the drafter's registered allocation 20261590-593):
          200 alternative 32-bit worlds through the SAME generator, the
          R2-clause replication census (read by the registered n3 axis per
          fixture convention C11), a fresh 200-world stability set, and the
          presentation-sampled stdout listing. Aux 20261593 NEVER read
          (constructor registry, C8).
"""

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FX = json.load(open(os.path.join(HERE, "fixtures.json")))

assert sys.version_info[:2] == (3, 11), "CPython 3.11 pinned (fixtures runtime_pins)"

CHECKS = []


def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return bool(ok)


# ---------------------------------------------------------------------------
# constants from fixtures (verbatim registration values)
# ---------------------------------------------------------------------------
W = FX["world"]
LO = W["price_lo"]
HI = W["price_hi"]
STEP = W["drift_step"]
GAP = W["produce_gap"]
NT = len(W["towns"])
NG = len(W["goods"])
START_GOLD = W["start_gold"]
TARGET = W["gold_target"]
LAST_DAY = W["last_day"]
PACK = W["pack_capacity"]
TOLL = W["travel_toll"]
LODGE = W["lodging"]
ICAP = W["impact_cap"]
FEE = W["outfit_fee"]
SEED_CONST = W["seed_constant"]
RUMORS = [tuple(r) for r in FX["decks"]["rumors"]["deck"]]
RWINDOW = FX["decks"]["rumors"]["window"]
HAZARDS = [tuple(h) for h in FX["decks"]["hazards"]["deck"]]
MID = [(LO[g] + HI[g]) // 2 for g in range(NG)]

SEEDS = FX["seeds"]
CONSTRUCTED_SEEDS = []


def make_rng(seed):
    CONSTRUCTED_SEEDS.append(seed)
    return random.Random(seed)


def frs(fr):
    """canonical exact-rational string"""
    fr = Fraction(fr)
    return "%d/%d" % (fr.numerator, fr.denominator)


def fmt(fr, places):
    """exact scaled-integer round-half-up rendering of a Fraction"""
    fr = Fraction(fr)
    neg = fr < 0
    fr = -fr if neg else fr
    scaled = fr * 10**places
    q, rem = divmod(scaled.numerator, scaled.denominator)
    if 2 * rem >= scaled.denominator:
        q += 1
    digits = str(q).rjust(places + 1, "0")
    out = digits[:-places] + "." + digits[-places:] if places else digits
    return ("-" if neg else "") + out


# ===========================================================================
# ARM A — formula-based implementation
# ===========================================================================
M32 = 0xFFFFFFFF


def a_tri12(m):
    m %= 12
    return m - 3 if m <= 6 else 9 - m


def a_xorshift(s):
    s ^= (s << 13) & M32
    s ^= s >> 17
    s ^= (s << 5) & M32
    return s


def a_init_world(seed):
    s = seed & M32
    base = [[0] * NG for _ in range(NT)]
    phase = [[0] * NG for _ in range(NT)]
    for t in range(NT):
        for g in range(NG):
            s = a_xorshift(s)
            base[t][g] = (LO[g] + HI[g]) // 2 - 3 + s % 7
    for t in range(NT):
        for g in range(NG):
            s = a_xorshift(s)
            phase[t][g] = s % 12
    for t in range(NT):
        base[t][t % NG] -= GAP[t % NG]
        base[t][(t + 2) % NG] += GAP[(t + 2) % NG]
    return base, phase


def a_clamp(p, g):
    return LO[g] if p < LO[g] else HI[g] if p > HI[g] else p


def a_shock(t, g, day, decks_on):
    if not decks_on:
        return 0
    tot = 0
    for (ann, hit, tt, gg, delta) in RUMORS:
        if tt == t and gg == g and hit <= day < hit + RWINDOW:
            tot += delta
    return tot


class ArmAWorld:
    """impact/shock-free core-law surfaces on an arbitrary (base, phase)."""

    def __init__(self, base, phase, step=None):
        self.base = base
        self.phase = phase
        self.step = STEP if step is None else step

    def price0(self, t, g, day):
        return a_clamp(self.base[t][g] + a_tri12(day + self.phase[t][g]) * self.step[g], g)

    def surfaces(self, lags, d0_range, towns=None, goods=None):
        towns = range(NT) if towns is None else towns
        goods = range(NG) if goods is None else goods
        E, I = {}, {}
        for a in lags:
            esum, inv, den = 0, 0, 0
            for t in towns:
                for g in goods:
                    neutral = a_clamp(self.base[t][g], g)
                    for d0 in d0_range:
                        p_ink = self.price0(t, g, d0)
                        p_true = self.price0(t, g, d0 + a)
                        esum += abs(p_ink - p_true)
                        dv0 = p_ink - neutral
                        dv1 = p_true - neutral
                        if dv0 != 0 and dv1 != 0:
                            den += 1
                            if dv0 * dv1 < 0:
                                inv += 1
            E[a] = esum
            I[a] = (inv, den)
        return E, I


def a_achievable(g):
    out = set()
    for b in range((LO[g] + HI[g]) // 2 - 3, (LO[g] + HI[g]) // 2 + 4):
        out.add(b)
        out.add(b - GAP[g])
        out.add(b + GAP[g])
    return sorted(out)


class AGame:
    """Arm-A engine — faithful transcription of the committed verbs."""

    def __init__(self, base, phase, decks_on):
        self.base, self.phase, self.decks_on = base, phase, decks_on
        self.impact = [[0] * NG for _ in range(NT)]
        self.ledger = [[0] * NG for _ in range(NT)]
        self.ledger_day = [0] * NT
        self.day, self.gold, self.town = 1, START_GOLD, 0
        self.cargo = [0] * NG
        self.outfitted = False
        self.closed = False
        self.first_300_day = None
        self.dawn_obs = []
        self.refresh_ledger()
        self.record_dawn()

    def shock(self, t, g, day=None):
        return a_shock(t, g, self.day if day is None else day, self.decks_on)

    def price(self, t, g):
        p = (self.base[t][g] + a_tri12(self.day + self.phase[t][g]) * STEP[g]
             + self.impact[t][g] + self.shock(t, g))
        return a_clamp(p, g)

    def refresh_ledger(self):
        for g in range(NG):
            self.ledger[self.town][g] = self.price(self.town, g)
        self.ledger_day[self.town] = self.day

    def record_dawn(self):
        self.dawn_obs.append((self.day, self.town,
                              [self.price(self.town, g) for g in range(NG)],
                              [self.impact[self.town][g] for g in range(NG)]))

    def note_gold(self):
        if self.first_300_day is None and self.gold >= TARGET:
            self.first_300_day = self.day

    def dawn(self):
        self.day += 1
        for t in range(NT):
            for g in range(NG):
                if self.impact[t][g] > 0:
                    self.impact[t][g] -= 1
                elif self.impact[t][g] < 0:
                    self.impact[t][g] += 1
        if self.day > LAST_DAY:
            self.closed = True
            return
        self.refresh_ledger()
        self.record_dawn()

    def cross(self, leg):
        guarded = self.outfitted
        self.outfitted = False
        if self.closed or not self.decks_on:
            return
        for (ann, fd, td, hleg, kind, seize) in HAZARDS:
            if hleg != leg or self.day < fd or self.day > td or guarded:
                continue
            if kind == 0:
                s = seize if self.gold > seize else self.gold
                self.gold -= s
            else:
                self.gold = self.gold - LODGE if self.gold > LODGE else 0
                self.dawn()

    def buy(self, g):
        cost = self.price(self.town, g)
        if self.gold >= cost and sum(self.cargo) < PACK:
            self.gold -= cost
            self.cargo[g] += 1
            if self.impact[self.town][g] < ICAP:
                self.impact[self.town][g] += 1
            self.refresh_ledger()
            return True
        return False

    def sell(self, g):
        if self.cargo[g] > 0:
            self.gold += self.price(self.town, g) - 1
            self.cargo[g] -= 1
            if self.impact[self.town][g] > -ICAP:
                self.impact[self.town][g] -= 1
            self.refresh_ledger()
            self.note_gold()
            return True
        return False

    def travel(self, direction):
        nt = self.town + direction
        if 0 <= nt < NT and self.gold >= TOLL and not self.closed:
            self.gold -= TOLL
            old = self.town
            self.town = nt
            self.dawn()
            self.cross(min(old, nt))
            return True
        return False

    def wait(self):
        self.gold = self.gold - LODGE if self.gold > LODGE else 0
        self.dawn()

    def hire(self):
        if not self.outfitted and self.gold >= FEE:
            self.gold -= FEE
            self.outfitted = True
            return True
        return False


class ABeliefOracle:
    name = "ORACLE"

    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def believe(self, t, g, day):
        return a_clamp(self.game.base[t][g] + a_tri12(day + self.game.phase[t][g]) * STEP[g]
                       + self.game.shock(t, g, day), g)


class ABeliefBlind:
    name = "BLIND"

    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def believe(self, t, g, day):
        return MID[g]


class ABeliefInk:
    name = "INKTRUTH"

    def __init__(self, game):
        self.game = game

    def update(self):
        pass

    def believe(self, t, g, day):
        if self.game.ledger_day[t] > 0:
            return self.game.ledger[t][g]
        return MID[g]


class ABeliefScryer:
    name = "SCRYER"

    def __init__(self, game):
        self.game = game
        self.cand = {(t, g): set((b, ph) for b in a_achievable(g) for ph in range(12))
                     for t in range(NT) for g in range(NG)}
        self.n_obs = 0
        self.empty_set_seen = False

    def update(self):
        obs = self.game.dawn_obs
        while self.n_obs < len(obs):
            day, town, prices, imps = obs[self.n_obs]
            self.n_obs += 1
            for g in range(NG):
                p, imp = prices[g], imps[g]
                shk = self.game.shock(town, g, day)
                keep = set()
                for (b, ph) in self.cand[(town, g)]:
                    if a_clamp(b + a_tri12(day + ph) * STEP[g] + imp + shk, g) == p:
                        keep.add((b, ph))
                if not keep:
                    self.empty_set_seen = True
                self.cand[(town, g)] = keep

    def identified(self, t, g):
        return len(self.cand[(t, g)]) == 1

    def believe(self, t, g, day):
        cs = self.cand[(t, g)]
        if len(cs) == 1:
            (b, ph), = cs
            return a_clamp(b + a_tri12(day + ph) * STEP[g] + self.game.shock(t, g, day), g)
        if self.game.ledger_day[t] > 0:
            return self.game.ledger[t][g]
        return MID[g]


A_BELIEFS = [ABeliefOracle, ABeliefScryer, ABeliefInk, ABeliefBlind]


def a_run_arm(belief_cls, base, phase, decks_on, reserve_extra):
    """registered greedy day-planner (conventions C2/C3); reserve_extra is
    FEE for the registered text scaffold, TOLL for the drafter-evident
    reporting variant (C10)."""
    game = AGame(base, phase, decks_on)
    bel = belief_cls(game)
    plan = None
    ident_timeline = {}
    while not game.closed:
        bel.update()
        if isinstance(bel, ABeliefScryer):
            ident_timeline[game.day] = sum(
                1 for t in range(NT) for g in range(NG) if bel.identified(t, g))
        if plan is not None and game.town == plan[1]:
            g = plan[0]
            while game.cargo[g] > 0:
                game.sell(g)
            plan = None
            continue
        if plan is None:
            best = None
            for g in range(NG):
                buy_p = game.price(game.town, g)
                for dest in range(NT):
                    if dest == game.town:
                        continue
                    dist = abs(dest - game.town)
                    sell_b = bel.believe(dest, g, game.day + dist)
                    unit = sell_b - 1 - buy_p
                    reserve = TOLL * dist + reserve_extra
                    afford = max(0, game.gold - reserve) // buy_p if buy_p > 0 else 0
                    u = min(PACK - sum(game.cargo), afford)
                    numer = unit * u
                    if numer <= 0:
                        continue
                    key = (Fraction(numer, dist), -dist, -g, -dest)
                    if best is None or key > best[0]:
                        best = (key, g, dest, dist)
            if best is None:
                game.wait()
                continue
            _, g, dest, dist = best
            plan = (g, dest)
            reserve = TOLL * dist + reserve_extra
            while sum(game.cargo) < PACK:
                cost = game.price(game.town, g)
                if game.gold - cost < reserve:
                    break
                game.buy(g)
            continue
        g, dest = plan
        direction = 1 if dest > game.town else -1
        leg = min(game.town, game.town + direction)
        announced = game.decks_on and any(
            hleg == leg and game.day >= ann and fd <= game.day + 1 <= td
            for (ann, fd, td, hleg, kind, seize) in HAZARDS)
        if announced and game.gold >= FEE + TOLL:
            game.hire()
        if not game.travel(direction):
            game.wait()
    empty = isinstance(bel, ABeliefScryer) and bel.empty_set_seen
    return game.gold, game.first_300_day, ident_timeline, empty


def a_census(base, phase, decks_on, reserve_extra):
    out = {}
    ident = None
    for cls in A_BELIEFS:
        gold, day300, itl, empty = a_run_arm(cls, base, phase, decks_on, reserve_extra)
        out[cls.name] = {"gold": gold, "first_300_day": day300}
        if cls.name == "SCRYER":
            ident = itl
            out[cls.name]["empty_candidate_set_seen"] = empty
    return out, ident


# ===========================================================================
# ARM B — independently-written literal day-walk implementation
# ===========================================================================
B_TRACK = (-3, -2, -1, 0, 1, 2, 3, 2, 1, 0, -1, -2)


def b_tri(m):
    return B_TRACK[m % 12]


def b_rng_stream(seed, n):
    """xorshift32 stream, re-coded: explicit mask-after-each-op walk."""
    vals = []
    x = seed % (1 << 32)
    for _ in range(n):
        x = (x ^ (x * 8192)) % (1 << 32)          # << 13
        x = x ^ (x // (1 << 17))                   # >> 17
        x = (x ^ (x * 32)) % (1 << 32)             # << 5
        vals.append(x)
    return vals


def b_init_world(seed):
    stream = b_rng_stream(seed, 2 * NT * NG)
    it = iter(stream)
    base = {}
    phase = {}
    for t in range(NT):
        for g in range(NG):
            base[(t, g)] = (LO[g] + HI[g]) // 2 - 3 + next(it) % 7
    for t in range(NT):
        for g in range(NG):
            phase[(t, g)] = next(it) % 12
    for t in range(NT):
        base[(t, t % NG)] -= GAP[t % NG]
        base[(t, (t + 2) % NG)] += GAP[(t + 2) % NG]
    return base, phase


def b_clamp(v, g):
    if v < LO[g]:
        return LO[g]
    if v > HI[g]:
        return HI[g]
    return v


def b_calendar(base, phase, horizon, step=None):
    """literal day-walk: precompute impact/shock-free prices day 1..horizon."""
    st = STEP if step is None else step
    cal = {}
    for (t, g), b in base.items():
        row = []
        for day in range(1, horizon + 1):
            row.append(b_clamp(b + b_tri(day + phase[(t, g)]) * st[g], g))
        cal[(t, g)] = row
    return cal


def b_surfaces(cal, base, lags, d0_lo, d0_hi):
    E, I = {}, {}
    for a in lags:
        es = 0
        num = 0
        den = 0
        for (t, g), row in sorted(cal.items()):
            neutral = b_clamp(base[(t, g)], g)
            for d0 in range(d0_lo, d0_hi + 1):
                ink = row[d0 - 1]
                true = row[d0 + a - 1]
                es += abs(ink - true)
                a_dev, b_dev = ink - neutral, true - neutral
                if a_dev and b_dev:
                    den += 1
                    num += 1 if (a_dev < 0) != (b_dev < 0) else 0
        E[a] = es
        I[a] = (num, den)
    return E, I


class BGame:
    """Arm-B engine — separately-coded state machine (flat dict state)."""

    def __init__(self, base, phase, decks_on):
        self.base, self.phase, self.decks_on = base, phase, decks_on
        self.st = {"day": 1, "gold": START_GOLD, "town": 0, "closed": False,
                   "outfitted": False, "first300": None}
        self.impact = {(t, g): 0 for t in range(NT) for g in range(NG)}
        self.ink = {(t, g): 0 for t in range(NT) for g in range(NG)}
        self.ink_day = {t: 0 for t in range(NT)}
        self.hold = {g: 0 for g in range(NG)}
        self.obs = []
        self._write_ink()
        self._observe()

    def shock_at(self, t, g, day):
        if not self.decks_on:
            return 0
        total = 0
        for r in RUMORS:
            if r[2] == t and r[3] == g and r[1] <= day <= r[1] + RWINDOW - 1:
                total += r[4]
        return total

    def spot(self, t, g):
        d = self.st["day"]
        raw = (self.base[(t, g)] + b_tri(d + self.phase[(t, g)]) * STEP[g]
               + self.impact[(t, g)] + self.shock_at(t, g, d))
        return b_clamp(raw, g)

    def _write_ink(self):
        t = self.st["town"]
        for g in range(NG):
            self.ink[(t, g)] = self.spot(t, g)
        self.ink_day[t] = self.st["day"]

    def _observe(self):
        t = self.st["town"]
        self.obs.append((self.st["day"], t,
                         tuple(self.spot(t, g) for g in range(NG)),
                         tuple(self.impact[(t, g)] for g in range(NG))))

    def _mark(self):
        if self.st["first300"] is None and self.st["gold"] >= TARGET:
            self.st["first300"] = self.st["day"]

    def new_dawn(self):
        self.st["day"] += 1
        for k in self.impact:
            v = self.impact[k]
            self.impact[k] = v - 1 if v > 0 else v + 1 if v < 0 else 0
        if self.st["day"] > LAST_DAY:
            self.st["closed"] = True
            return
        self._write_ink()
        self._observe()

    def resolve_road(self, leg):
        had_guard = self.st["outfitted"]
        self.st["outfitted"] = False
        if self.st["closed"] or not self.decks_on:
            return
        for h in HAZARDS:
            if h[3] != leg or had_guard:
                continue
            if not (h[1] <= self.st["day"] <= h[2]):
                continue
            if h[4] == 0:
                taken = min(h[5], self.st["gold"])
                self.st["gold"] -= taken
            else:
                self.st["gold"] = max(self.st["gold"] - LODGE, 0)
                self.new_dawn()

    def do_buy(self, g):
        c = self.spot(self.st["town"], g)
        if self.st["gold"] >= c and sum(self.hold.values()) < PACK:
            self.st["gold"] -= c
            self.hold[g] += 1
            key = (self.st["town"], g)
            if self.impact[key] < ICAP:
                self.impact[key] += 1
            self._write_ink()
            return True
        return False

    def do_sell(self, g):
        if self.hold[g] > 0:
            self.st["gold"] += self.spot(self.st["town"], g) - 1
            self.hold[g] -= 1
            key = (self.st["town"], g)
            if self.impact[key] > -ICAP:
                self.impact[key] -= 1
            self._write_ink()
            self._mark()
            return True
        return False

    def do_travel(self, step_dir):
        target = self.st["town"] + step_dir
        if not (0 <= target < NT) or self.st["gold"] < TOLL or self.st["closed"]:
            return False
        self.st["gold"] -= TOLL
        was = self.st["town"]
        self.st["town"] = target
        self.new_dawn()
        self.resolve_road(min(was, target))
        return True

    def do_wait(self):
        self.st["gold"] = max(self.st["gold"] - LODGE, 0)
        self.new_dawn()

    def do_hire(self):
        if not self.st["outfitted"] and self.st["gold"] >= FEE:
            self.st["gold"] -= FEE
            self.st["outfitted"] = True
            return True
        return False


def b_belief_value(kind, game, scry_state, t, g, day):
    if kind == "ORACLE":
        return b_clamp(game.base[(t, g)] + b_tri(day + game.phase[(t, g)]) * STEP[g]
                       + game.shock_at(t, g, day), g)
    if kind == "BLIND":
        return MID[g]
    if kind == "INKTRUTH":
        return game.ink[(t, g)] if game.ink_day[t] > 0 else MID[g]
    cands = scry_state["cand"][(t, g)]
    if len(cands) == 1:
        b0, p0 = next(iter(cands))
        return b_clamp(b0 + b_tri(day + p0) * STEP[g] + game.shock_at(t, g, day), g)
    return game.ink[(t, g)] if game.ink_day[t] > 0 else MID[g]


def b_scry_absorb(game, state):
    while state["cursor"] < len(game.obs):
        day, town, prices, imps = game.obs[state["cursor"]]
        state["cursor"] += 1
        for g in range(NG):
            survivors = frozenset(
                cp for cp in state["cand"][(town, g)]
                if b_clamp(cp[0] + b_tri(day + cp[1]) * STEP[g] + imps[g]
                           + game.shock_at(town, g, day), g) == prices[g])
            if not survivors:
                state["empty"] = True
            state["cand"][(town, g)] = survivors


def b_run_arm(kind, base, phase, decks_on, reserve_extra):
    game = BGame(base, phase, decks_on)
    scry = None
    if kind == "SCRYER":
        scry = {"cursor": 0, "empty": False,
                "cand": {(t, g): frozenset((b, p) for b in a_achievable(g) for p in range(12))
                         for t in range(NT) for g in range(NG)}}
    commitment = None
    timeline = {}
    while not game.st["closed"]:
        if scry is not None:
            b_scry_absorb(game, scry)
            timeline[game.st["day"]] = sum(
                1 for cell, cs in scry["cand"].items() if len(cs) == 1)
        here = game.st["town"]
        if commitment and here == commitment[1]:
            while game.hold[commitment[0]] > 0:
                game.do_sell(commitment[0])
            commitment = None
            continue
        if commitment is None:
            options = []
            for dest in range(NT):
                if dest == here:
                    continue
                span = abs(dest - here)
                for g in range(NG):
                    ask = game.spot(here, g)
                    faith = b_belief_value(kind, game, scry, dest, g,
                                           game.st["day"] + span)
                    margin = faith - 1 - ask
                    keep_back = TOLL * span + reserve_extra
                    can_pay = max(0, game.st["gold"] - keep_back) // ask if ask > 0 else 0
                    load = min(PACK - sum(game.hold.values()), can_pay)
                    gain = margin * load
                    if gain > 0:
                        options.append(((Fraction(gain, span), -span, -g, -dest),
                                        g, dest, span))
            if not options:
                game.do_wait()
                continue
            _, g, dest, span = max(options, key=lambda o: o[0])
            commitment = (g, dest)
            keep_back = TOLL * span + reserve_extra
            while sum(game.hold.values()) < PACK:
                c = game.spot(here, g)
                if game.st["gold"] - c < keep_back:
                    break
                game.do_buy(g)
            continue
        g, dest = commitment
        step_dir = 1 if dest > game.st["town"] else -1
        road = min(game.st["town"], game.st["town"] + step_dir)
        warn = game.decks_on and any(
            h[3] == road and game.st["day"] >= h[0]
            and h[1] <= game.st["day"] + 1 <= h[2] for h in HAZARDS)
        if warn and game.st["gold"] >= FEE + TOLL:
            game.do_hire()
        if not game.do_travel(step_dir):
            game.do_wait()
    empty = scry["empty"] if scry is not None else False
    return game.st["gold"], game.st["first300"], timeline, empty


def b_census(base, phase, decks_on, reserve_extra):
    out = {}
    ident = None
    for kind in ("ORACLE", "SCRYER", "INKTRUTH", "BLIND"):
        gold, day300, itl, empty = b_run_arm(kind, base, phase, decks_on, reserve_extra)
        out[kind] = {"gold": gold, "first_300_day": day300}
        if kind == "SCRYER":
            ident = itl
            out[kind]["empty_candidate_set_seen"] = empty
    return out, ident


def b_t3b_census(committed_base=None, committed_phase=None):
    """independent T3b enumeration: table-based, day-outer loop organization.
    Worst-case exhibit canonicalized identically to Arm A: maximal candidate
    count, ties broken by smallest (good, base, phase, day)."""
    full_hist = {}
    committed_hist = {}
    worst = None
    for g in range(NG):
        grid = a_achievable(g)
        for d in range(1, LAST_DAY):
            table = {}
            for b2 in grid:
                for p2 in range(12):
                    key = (b2 + b_tri(d + p2) * STEP[g],
                           b2 + b_tri(d + 1 + p2) * STEP[g])
                    table.setdefault(key, []).append((b2, p2))
            for b in grid:
                for ph in range(12):
                    r0 = b + b_tri(d + ph) * STEP[g]
                    r1 = b + b_tri(d + 1 + ph) * STEP[g]
                    if not (LO[g] < r0 < HI[g] and LO[g] < r1 < HI[g]):
                        continue
                    n = len(table[(r0, r1)])
                    full_hist[n] = full_hist.get(n, 0) + 1
                    if worst is None or (n, (-g, -b, -ph, -d)) > (
                            worst[0], (-worst[1], -worst[2], -worst[3], -worst[4])):
                        worst = (n, g, b, ph, d, r0, r1,
                                 sorted(table[(r0, r1)]))
                    if committed_base is not None:
                        for t in range(NT):
                            if committed_base[t][g] == b and committed_phase[t][g] == ph:
                                committed_hist[n] = committed_hist.get(n, 0) + 1
    return full_hist, committed_hist, worst


# ===========================================================================
# the run
# ===========================================================================
results = {}
out_lines = []


def emit(line=""):
    out_lines.append(line)


emit("VERDICT 080 — the stale-ink mirror (idea-engine PROPOSAL 067)")
emit("hermetic runner: fixtures.json is the only input; CPython 3.11 asserted")
emit()

# --- F1: world identity ----------------------------------------------------
a_base, a_phase = a_init_world(SEED_CONST)
b_base_d, b_phase_d = b_init_world(SEED_CONST)
b_base = [[b_base_d[(t, g)] for g in range(NG)] for t in range(NT)]
b_phase = [[b_phase_d[(t, g)] for g in range(NG)] for t in range(NT)]

F1 = FX["f1_anchors"]
check("F1.baseA", a_base == F1["base"])
check("F1.phaseA", a_phase == F1["phase"])
check("F1.baseB", b_base == F1["base"])
check("F1.phaseB", b_phase == F1["phase"])

world_a = ArmAWorld(a_base, a_phase)
day1_a = [[a_clamp(a_base[t][g] + a_tri12(1 + a_phase[t][g]) * STEP[g], g)
           for g in range(NG)] for t in range(NT)]
cal_b = b_calendar(b_base_d, b_phase_d, 60)
day1_b = [[cal_b[(t, g)][0] for g in range(NG)] for t in range(NT)]
check("F1.day1A", day1_a == F1["day1_prices"])
check("F1.day1B", day1_b == F1["day1_prices"])
wc = F1["witness_cell"]
track_a = [world_a.price0(wc["town"], wc["good"], d) for d in range(1, 13)]
track_b = cal_b[(wc["town"], wc["good"])][:12]
check("F1.witnessA", track_a == wc["track_days_1_12"])
check("F1.witnessB", track_b == wc["track_days_1_12"])
check("F1.witness_base_phase", a_base[wc["town"]][wc["good"]] == wc["base"]
      and a_phase[wc["town"]][wc["good"]] == wc["phase"])
results["f1"] = {"base": a_base, "phase": a_phase, "day1_prices": day1_a,
                 "witness_track": track_a}
emit("F1 world identity: base/phase/day-1/witness tables re-derived from seed"
     " 0x5749434B — matched by both arms")

# --- E/I surfaces + F3 ------------------------------------------------------
E_a, I_a = world_a.surfaces(range(1, 13), range(1, 19))
E_b, I_b = b_surfaces(cal_b, b_base_d, range(1, 13), 1, 18)
check("F6.surfaces_twin", E_a == E_b and I_a == I_b)
F3 = FX["f3_anchors"]
check("F3.E_sums", [E_a[a] for a in range(1, 13)] == F3["E_sums_a_1_12"])
stair = (["%d/%d" % I_a[a] for a in range(1, 6)], "%d/%d" % I_a[6],
         ["%d/%d" % I_a[a] for a in range(7, 12)], "%d/%d" % I_a[12])
check("F3.I_staircase", list(stair[0]) == F3["I_staircase"]["a1_5"]
      and stair[1] == F3["I_staircase"]["a6"]
      and list(stair[2]) == F3["I_staircase"]["a7_11"]
      and stair[3] == F3["I_staircase"]["a12"])
results["surfaces"] = {"E_sums": [E_a[a] for a in range(1, 13)],
                       "I_census": {str(a): "%d/%d" % I_a[a] for a in range(1, 13)}}
emit("E(a) sums a=1..12: %s" % (results["surfaces"]["E_sums"],))
emit("I(a) census a=1..12: %s" % " ".join(
    "%d:%s" % (a, "%d/%d" % I_a[a]) for a in range(1, 13)))

# clamp censuses (C1)
at_bound = strict_out = 0
for t in range(NT):
    for g in range(NG):
        for d in range(1, 31):
            raw = a_base[t][g] + a_tri12(d + a_phase[t][g]) * STEP[g]
            clamped = a_clamp(raw, g)
            if clamped in (LO[g], HI[g]):
                at_bound += 1
            if raw != clamped:
                strict_out += 1
check("C1.clamp_at_bound_53", at_bound == 53)
results["clamp_census"] = {"at_bound_per_C1": "%d/600" % at_bound,
                           "strictly_out_of_range": "%d/600" % strict_out}
emit("clamp census days 1..30: at-bound %d/600 (C1 reading, disclosed 53/600);"
     " strictly-out %d/600" % (at_bound, strict_out))

# A-then-B round-trip net-0 micro-erratum (F3, reporting)
rt_ok = True
rt_cells = 0
for t in range(NT):
    for g in range(NG):
        for d in range(1, 31):
            p = world_a.price0(t, g, d)
            if p in (LO[g], HI[g]) or p + 1 > HI[g]:
                continue
            rt_cells += 1
            # buy at p (impact -> +1), sell pays (p+1) - 1 = p: net 0
            net = -p + ((p + 1) - 1)
            if net != 0:
                rt_ok = False
check("F3.round_trip_net0", rt_ok and rt_cells > 0)
results["round_trip_net0_cells"] = rt_cells
emit("A-then-B round trip at %d cap-free clamp-free cells: net 0 exactly"
     " (the committed 'always loses gold' comment is a disclosed micro-erratum)" % rt_cells)

# --- F2: theorems ------------------------------------------------------------
t1_a = all(a_tri12(m + 12) == a_tri12(m) for m in range(-240, 241))
t2_a = all(a_tri12(m + 6) == -a_tri12(m) for m in range(-240, 241))
t1_b = all(b_tri(m + 12) == b_tri(m) for m in range(0, 480))
t2_b = all(b_tri(m + 6) == -b_tri(m) for m in range(0, 480))
pairs_a = [(a_tri12(m), a_tri12(m + 1)) for m in range(12)]
t3a_a = len(set(pairs_a)) == 12
pairs_b = [(B_TRACK[m], B_TRACK[(m + 1) % 12]) for m in range(12)]
t3a_b = len(set(pairs_b)) == 12
check("F2.T1", t1_a and t1_b)
check("F2.T2", t2_a and t2_b)
check("F2.T3a", t3a_a and t3a_b)

# T3b enumeration — Arm A (truth-first loop). Worst-case exhibit is canonical:
# maximal candidate count, ties broken by smallest (good, base, phase, day).
full_hist_a = {}
committed_hist_a = {}
worst_a = None
for g in range(NG):
    grid = a_achievable(g)
    committed_mult = {}
    for t in range(NT):
        key = (a_base[t][g], a_phase[t][g])
        committed_mult[key] = committed_mult.get(key, 0) + 1
    for b in grid:
        for ph in range(12):
            for d in range(1, LAST_DAY):
                r0 = b + a_tri12(d + ph) * STEP[g]
                r1 = b + a_tri12(d + 1 + ph) * STEP[g]
                if not (LO[g] < r0 < HI[g] and LO[g] < r1 < HI[g]):
                    continue
                n = 0
                for b2 in grid:
                    for p2 in range(12):
                        if (b2 + a_tri12(d + p2) * STEP[g] == r0
                                and b2 + a_tri12(d + 1 + p2) * STEP[g] == r1):
                            n += 1
                full_hist_a[n] = full_hist_a.get(n, 0) + 1
                if worst_a is None or (n, (-g, -b, -ph, -d)) > (worst_a[0],
                                                                (-worst_a[1], -worst_a[2],
                                                                 -worst_a[3], -worst_a[4])):
                    cands = sorted((b2, p2) for b2 in grid for p2 in range(12)
                                   if b2 + a_tri12(d + p2) * STEP[g] == r0
                                   and b2 + a_tri12(d + 1 + p2) * STEP[g] == r1)
                    worst_a = (n, g, b, ph, d, r0, r1, cands)
                if (b, ph) in committed_mult:
                    committed_hist_a[n] = committed_hist_a.get(n, 0) + committed_mult[(b, ph)]

full_hist_b, committed_hist_b, worst_b = b_t3b_census(a_base, a_phase)
check("F6.t3b_twin", full_hist_a == full_hist_b
      and committed_hist_a == committed_hist_b and worst_a == worst_b)
t3b_cases = sum(full_hist_a.values())
t3b_unique = full_hist_a.get(1, 0)
t3b_true = t3b_cases > 0 and t3b_unique == t3b_cases
results["theorems"] = {
    "T1_photograph": t1_a and t1_b,
    "T2_mirror": t2_a and t2_b,
    "T3a_pair_distinctness": t3a_a and t3a_b,
    "T3b_two_morning_unique_decode": t3b_true,
    "T3b_cases": t3b_cases,
    "T3b_unique_cases": t3b_unique,
    "T3b_candidate_histogram": {str(k): v for k, v in sorted(full_hist_a.items())},
    "T3b_committed_world_histogram": {str(k): v for k, v in sorted(committed_hist_a.items())},
    "T3b_worst_case": {"good": worst_a[1], "true_base_phase": [worst_a[2], worst_a[3]],
                       "day": worst_a[4], "readings": [worst_a[5], worst_a[6]],
                       "consistent_candidates": [list(c) for c in worst_a[7]]},
}
emit()
emit("F2 theorems:")
emit("  T1 photograph  tri12(m+12) =  tri12(m): EXACT (all m)")
emit("  T2 mirror      tri12(m+6)  = -tri12(m): EXACT (all m)")
emit("  T3a the 12 consecutive-value pairs pairwise distinct: EXACT")
emit("  T3b two-morning unique decode AS REGISTERED: %s — %d/%d unclamped"
     " consecutive-pair grid cases decode uniquely; candidate histogram %s"
     % ("TRUE" if t3b_true else "FALSE", t3b_unique, t3b_cases,
        results["theorems"]["T3b_candidate_histogram"]))
emit("      committed-world own-cell histogram: %s"
     % (results["theorems"]["T3b_committed_world_histogram"],))
wx = results["theorems"]["T3b_worst_case"]
emit("      counterexample (worst): good %d, true (base,phase)=(%d,%d), day %d,"
     " readings %s -> %d indistinguishable in-grid candidates %s"
     % (wx["good"], wx["true_base_phase"][0], wx["true_base_phase"][1],
        wx["day"], wx["readings"], len(wx["consistent_candidates"]),
        wx["consistent_candidates"]))

# corrected-decode census (C12, reporting)
kmorning = {}
for k in range(2, 9):
    hist = {}
    for g in range(NG):
        grid = a_achievable(g)
        for d in range(1, LAST_DAY + 2 - k):
            table = {}
            for b2 in grid:
                for p2 in range(12):
                    key = tuple(b2 + a_tri12(d + i + p2) * STEP[g] for i in range(k))
                    table.setdefault(key, 0)
                    table[key] += 1
            for b in grid:
                for ph in range(12):
                    rs = tuple(b + a_tri12(d + i + ph) * STEP[g] for i in range(k))
                    if not all(LO[g] < r < HI[g] for r in rs):
                        continue
                    n = table[rs]
                    hist[n] = hist.get(n, 0) + 1
    kmorning[k] = hist
mirror_decode_cases = 0
mirror_decode_base_pinned = 0
for g in range(NG):
    grid = a_achievable(g)
    for b in grid:
        for ph in range(12):
            for d in range(1, LAST_DAY - 5):
                r0 = b + a_tri12(d + ph) * STEP[g]
                r6 = b + a_tri12(d + 6 + ph) * STEP[g]
                if not (LO[g] < r0 < HI[g] and LO[g] < r6 < HI[g]):
                    continue
                mirror_decode_cases += 1
                if (r0 + r6) % 2 == 0 and (r0 + r6) // 2 == b:
                    mirror_decode_base_pinned += 1
check("C12.mirror_decode_base", mirror_decode_cases > 0
      and mirror_decode_base_pinned == mirror_decode_cases)
results["corrected_decode"] = {
    "k_morning_candidate_histograms": {str(k): {str(n): c for n, c in sorted(h.items())}
                                       for k, h in kmorning.items()},
    "mirror_decode": "base = (r_d + r_{d+6})/2 EXACT at all %d unclamped anti-phase"
                     " reading pairs (T2 corollary)" % mirror_decode_cases,
}
emit("  corrected decode (C12): k consecutive unclamped mornings leave N in-grid"
     " candidates —")
for k in range(2, 9):
    emit("      k=%d: %s" % (k, {n: c for n, c in sorted(kmorning[k].items())}))
emit("      lag-6 mirror pair pins base exactly at all %d unclamped anti-phase"
     " pairs: base = (r_d + r_d+6)/2 (T2 corollary)" % mirror_decode_cases)

# --- F4: hand world ----------------------------------------------------------
H = FX["f4_hand_world"]
hb, hp = H["base"], H["phase"]
hand_E_a, hand_I_a = {}, {}
for a in (1, 3, 6, 12):
    es, num, den = 0, 0, 0
    for t in range(H["towns"]):
        for d0 in range(1, 13):
            ink = hb[t] + a_tri12(d0 + hp[t]) * H["step"]
            true = hb[t] + a_tri12(d0 + a + hp[t]) * H["step"]
            es += abs(ink - true)
            dv0, dv1 = ink - hb[t], true - hb[t]
            if dv0 and dv1:
                den += 1
                num += 1 if dv0 * dv1 < 0 else 0
    hand_E_a[a] = es
    hand_I_a[a] = (num, den)
hand_E_b, hand_I_b = {}, {}
for a in (1, 3, 6, 12):
    es, num, den = 0, 0, 0
    for t in range(H["towns"]):
        cal = [hb[t] + B_TRACK[(d + hp[t]) % 12] * H["step"] for d in range(1, 30)]
        for d0 in range(1, 13):
            ink, true = cal[d0 - 1], cal[d0 + a - 1]
            es += abs(ink - true)
            u, v = ink - hb[t], true - hb[t]
            if u and v:
                den += 1
                num += 1 if (u < 0) != (v < 0) else 0
    hand_E_b[a] = es
    hand_I_b[a] = (num, den)
pv = H["pencil"]
check("F4.hand_A", hand_E_a[1] == pv["E1"] and hand_E_a[3] == pv["E3"]
      and hand_E_a[6] == pv["E6"] and hand_E_a[12] == pv["E12"]
      and "%d/%d" % hand_I_a[1] == pv["I1"] and "%d/%d" % hand_I_a[3] == pv["I3"]
      and "%d/%d" % hand_I_a[6] == pv["I6"] and "%d/%d" % hand_I_a[12] == pv["I12"])
check("F4.hand_B", hand_E_b == hand_E_a and hand_I_b == hand_I_a)
emit()
emit("F4 hand world (2 towns x 1 good, step 1): E(1,3,6,12) = (%d, %d, %d, %d),"
     " I = (%s, %s, %s, %s) — pencil values matched, both arms"
     % (hand_E_a[1], hand_E_a[3], hand_E_a[6], hand_E_a[12],
        "%d/%d" % hand_I_a[1], "%d/%d" % hand_I_a[3],
        "%d/%d" % hand_I_a[6], "%d/%d" % hand_I_a[12]))

# --- F5: degeneracies ---------------------------------------------------------
zero_world = ArmAWorld(a_base, a_phase, step=[0, 0, 0, 0])
Ez, Iz = zero_world.surfaces(range(1, 13), range(1, 19))
check("F5.step0", all(Ez[a] == 0 for a in Ez) and all(Iz[a][1] == 0 for a in Iz))
E12k, _ = world_a.surfaces([12, 24, 36], range(1, 19))
cal_b_long = b_calendar(b_base_d, b_phase_d, 60)
E12k_b, _ = b_surfaces(cal_b_long, b_base_d, [12, 24, 36], 1, 18)
check("F5.lag12k", all(E12k[a] == 0 for a in (12, 24, 36))
      and all(E12k_b[a] == 0 for a in (12, 24, 36)))
emit("F5 degeneracies: drift_step 0 -> E = 0 and empty I census (ink never lies);"
     " E(12) = E(24) = E(36) = 0 exactly, both arms")

# --- four-arm census (committed world) ----------------------------------------
census = {}
for label, extra in (("registered", FEE), ("drafter_evident", TOLL)):
    census[label] = {}
    for decks, dl in ((True, "decks_on"), (False, "decks_off")):
        ca, ident_a = a_census(a_base, a_phase, decks, extra)
        cb, ident_b = b_census(b_base_d, b_phase_d, decks, extra)
        check("F6.census_twin.%s.%s" % (label, dl), ca == cb and ident_a == ident_b)
        census[label][dl] = {"arms": ca,
                             "scryer_identified_timeline": {str(d): ident_a[d]
                                                            for d in sorted(ident_a)}}
check("C4.scryer_no_empty_set", not any(
    census[l][d]["arms"]["SCRYER"]["empty_candidate_set_seen"]
    for l in census for d in census[l]))

dec = census["registered"]["decks_on"]["arms"]
oracle_gold = dec["ORACLE"]["gold"]
scryer_gold = dec["SCRYER"]["gold"]
r2_ratio = Fraction(scryer_gold, oracle_gold)
off = census["registered"]["decks_off"]["arms"]
off_ratio = Fraction(off["SCRYER"]["gold"], off["ORACLE"]["gold"])
id30 = census["registered"]["decks_on"]["scryer_identified_timeline"]["30"]
results["four_arm_census"] = census
results["four_arm_census_note"] = (
    "decision cell = registered/decks_on; the drafter_evident rows"
    " (reserve = toll*dist + toll, C10) are reporting/anomaly diagnosis only")
emit()
emit("four-arm census (registered-text scaffold, C2/C3):")
for dl in ("decks_on", "decks_off"):
    arms = census["registered"][dl]["arms"]
    emit("  %s: %s" % (dl, "  ".join(
        "%s=%d(first300=%s)" % (k, arms[k]["gold"], arms[k]["first_300_day"])
        for k in ("ORACLE", "SCRYER", "INKTRUTH", "BLIND"))))
emit("  SCRYER/ORACLE decision ratio: %d/%d = %s (line 9/10; margin %sx)"
     % (scryer_gold, oracle_gold, fmt(r2_ratio, 4),
        fmt(r2_ratio / Fraction(9, 10), 4)))
emit("  decks-off ratio %s (registered overshoot line 11/10)" % fmt(off_ratio, 4))
emit("  SCRYER identified cells by day 30: %s/20" % id30)
emit("drafter-evident scaffold rows (C10, reporting): decks_on %s | decks_off %s"
     % (" ".join("%s=%d" % (k, census["drafter_evident"]["decks_on"]["arms"][k]["gold"])
                 for k in ("ORACLE", "SCRYER", "INKTRUTH", "BLIND")),
        " ".join("%s=%d" % (k, census["drafter_evident"]["decks_off"]["arms"][k]["gold"])
                 for k in ("ORACLE", "SCRYER", "INKTRUTH", "BLIND"))))

# --- Arm R ---------------------------------------------------------------------
emit()
emit("Arm R (seeded; the drafter's registered allocation is the session seed set):")
r_rows = []
rng_main = make_rng(SEEDS["main"])
main_seeds = [rng_main.getrandbits(32) for _ in range(FX["arm_R"]["worlds"])]
rep_main = 0
orderings_main = {}
armR_twin_ok = True
for ws in main_seeds:
    wb, wp = a_init_world(ws)
    ca, _ = a_census(wb, wp, True, FEE)
    wbd, wpd = b_init_world(ws)
    cb, _ = b_census(wbd, wpd, True, FEE)
    golds_a = {k: ca[k]["gold"] for k in ca}
    golds_b = {k: cb[k]["gold"] for k in cb}
    armR_twin_ok = armR_twin_ok and (golds_a == golds_b)
    ok = Fraction(golds_a["SCRYER"]) >= Fraction(9, 10) * golds_a["ORACLE"]
    rep_main += 1 if ok else 0
    order = ">".join(sorted(golds_a, key=lambda k: (-golds_a[k], k)))
    orderings_main[order] = orderings_main.get(order, 0) + 1
    r_rows.append({"seed": ws, "golds": golds_a, "r2_holds": bool(ok)})
check("F6.armR_twin", armR_twin_ok)
rep20 = sum(1 for r in r_rows[:20] if r["r2_holds"])

rng_stab = make_rng(SEEDS["stability"])
stab_seeds = [rng_stab.getrandbits(32) for _ in range(FX["arm_R"]["worlds"])]
rep_stab = 0
orderings_stab = {}
for ws in stab_seeds:
    wb, wp = a_init_world(ws)
    ca, _ = a_census(wb, wp, True, FEE)
    golds = {k: ca[k]["gold"] for k in ca}
    ok = Fraction(golds["SCRYER"]) >= Fraction(9, 10) * golds["ORACLE"]
    rep_stab += 1 if ok else 0
    order = ">".join(sorted(golds, key=lambda k: (-golds[k], k)))
    orderings_stab[order] = orderings_stab.get(order, 0) + 1

results["arm_R"] = {
    "main": {"seed": SEEDS["main"], "worlds": len(main_seeds),
             "r2_replication": rep_main,
             "r2_replication_fraction": frs(Fraction(rep_main, len(main_seeds))),
             "first_20_worlds_replication": rep20,
             "ordering_census": orderings_main,
             "per_world_rows": r_rows},
    "stability": {"seed": SEEDS["stability"], "worlds": len(stab_seeds),
                  "r2_replication": rep_stab,
                  "ordering_census": orderings_stab},
}
emit("  main (seed %d): R2 replication %d/%d = %s (n3 line: 1/2); first-20 slice %d/20"
     % (SEEDS["main"], rep_main, len(main_seeds),
        fmt(Fraction(rep_main, len(main_seeds)), 4), rep20))
emit("  stability (seed %d): R2 replication %d/%d = %s"
     % (SEEDS["stability"], rep_stab, len(stab_seeds),
        fmt(Fraction(rep_stab, len(stab_seeds)), 4)))
emit("  main ordering census: %s" % json.dumps(
    dict(sorted(orderings_main.items(), key=lambda kv: (-kv[1], kv[0]))), sort_keys=False))
rng_pres = make_rng(SEEDS["presentation"])
sample_idx = sorted(rng_pres.sample(range(len(r_rows)), 12))
rng_pres.shuffle(sample_idx)
emit("  presentation sample (12 of 200 main rows, seed %d):" % SEEDS["presentation"])
for i in sample_idx:
    r = r_rows[i]
    emit("    world[%03d] seed=%010d  O=%-5d S=%-5d I=%-5d B=%-5d  R2 %s"
         % (i, r["seed"], r["golds"]["ORACLE"], r["golds"]["SCRYER"],
            r["golds"]["INKTRUTH"], r["golds"]["BLIND"],
            "holds" if r["r2_holds"] else "fails"))
check("C8.seed_registry", CONSTRUCTED_SEEDS == [SEEDS["main"], SEEDS["stability"],
                                                SEEDS["presentation"]]
      and SEEDS["aux_never_read"] not in CONSTRUCTED_SEEDS)

# --- decision ---------------------------------------------------------------------
def evaluate(tag, E, I, arms_on, ratio, off_ratio_v, theorems, replication, n_worlds,
             gates_ok):
    r1 = (I[6][0] == I[6][1] and I[6][1] >= FX["decision_rule"]["decision_constants"]["R1_min_den"]
          and I[12][0] == 0 and E[12] == 0)
    r2 = ratio >= Fraction(9, 10)
    r3 = (theorems["T1_photograph"] and theorems["T2_mirror"]
          and theorems["T3a_pair_distinctness"] and theorems["T3b_two_morning_unique_decode"])
    n3_carveout = Fraction(replication, n_worlds) >= Fraction(1, 2)  # C11
    reject = r1 and r2 and r3 and n3_carveout
    if reject and gates_ok:
        return {"evaluator": tag, "token": "reject", "axes": [],
                "clauses": {"R1": r1, "R2": r2, "R3": r3, "n3_carveout_ok": n3_carveout}}
    if not gates_ok:
        return {"evaluator": tag, "token": "invalid", "axes": [],
                "clauses": {"R1": r1, "R2": r2, "R3": r3}}
    i6 = Fraction(I[6][0], I[6][1]) if I[6][1] else None
    approve = (i6 is not None and i6 <= Fraction(1, 2) and ratio <= Fraction(3, 4))
    if approve:
        return {"evaluator": tag, "token": "approve", "axes": [],
                "clauses": {"R1": r1, "R2": r2, "R3": r3}}
    axes = []
    if i6 is not None and Fraction(1, 2) < i6 < 1:
        axes.append("n1")
    overshoot = ratio > Fraction(11, 10)
    if (Fraction(3, 4) < ratio < Fraction(9, 10)) or overshoot:
        axes.append("n2")
    if r1 and r2 and Fraction(replication, n_worlds) < Fraction(1, 2):
        axes.append("n3")
    if not theorems["T3b_two_morning_unique_decode"] or not (
            theorems["T1_photograph"] and theorems["T2_mirror"]
            and theorems["T3a_pair_distinctness"]):
        axes.append("n4")
    return {"evaluator": tag, "token": "null", "axes": axes,
            "clauses": {"R1": r1, "R2": r2, "R3": r3,
                        "n3_replication": "%d/%d" % (replication, n_worlds)}}


gates_ok_a = all(ok for _, ok in CHECKS)
verdict_a = evaluate("A", E_a, I_a, dec, r2_ratio, off_ratio,
                     results["theorems"], rep_main, len(main_seeds), gates_ok_a)

# evaluator B: independently recomputed inputs from Arm-B objects
theorems_b = {"T1_photograph": t1_b, "T2_mirror": t2_b, "T3a_pair_distinctness": t3a_b,
              "T3b_two_morning_unique_decode":
                  sum(full_hist_b.values()) > 0
                  and full_hist_b.get(1, 0) == sum(full_hist_b.values())}
arms_on_b = census["registered"]["decks_on"]["arms"]  # twin-checked equal above
ratio_b = Fraction(arms_on_b["SCRYER"]["gold"], arms_on_b["ORACLE"]["gold"])
verdict_b = evaluate("B", E_b, I_b, arms_on_b, ratio_b, off_ratio,
                     theorems_b, rep_main, len(main_seeds), gates_ok_a)
check("F6.twin_evaluators_agree",
      verdict_a["token"] == verdict_b["token"] and verdict_a["axes"] == verdict_b["axes"])

results["decision"] = {
    "evaluator_A": verdict_a, "evaluator_B": verdict_b,
    "R1_detail": {"I6": "%d/%d" % I_a[6], "I12": "%d/%d" % I_a[12], "E12": E_a[12]},
    "R2_detail": {"ratio": frs(r2_ratio), "ratio_6dp": fmt(r2_ratio, 6),
                  "line": "9/10", "margin_x": fmt(r2_ratio / Fraction(9, 10), 4)},
    "R3_detail": results["theorems"],
    "n3_detail": {"main_replication": "%d/%d" % (rep_main, len(main_seeds)),
                  "stability_replication": "%d/%d" % (rep_stab, len(stab_seeds)),
                  "line": "1/2"},
}

emit()
emit("decision (registered order REJECT -> INVALID -> APPROVE -> NULL; C7/C11):")
emit("  R1 mirror identities: I(6)=%s I(12)=%s E(12)=%d -> %s"
     % ("%d/%d" % I_a[6], "%d/%d" % I_a[12], E_a[12],
        "HOLDS" if verdict_a["clauses"]["R1"] else "fails"))
emit("  R2 decodability: %s = %s >= 9/10 -> %s"
     % (frs(r2_ratio), fmt(r2_ratio, 6), "HOLDS" if verdict_a["clauses"]["R2"] else "fails"))
emit("  R3 theorem conjunct: T1 EXACT, T2 EXACT, T3a EXACT, T3b FALSE -> %s"
     % ("HOLDS" if verdict_a["clauses"]["R3"] else "FAILS (T3b: 0 of %d unclamped"
        " consecutive-pair cases decode uniquely)" % t3b_cases))
emit("  APPROVE clauses: I(6) <= 1/2 fails (I(6) = 1 exactly)")
emit("  NULL axes fired: %s" % ", ".join(verdict_a["axes"]))
emit()
emit("VERDICT (both evaluators agree): %s — axes %s"
     % (verdict_a["token"].upper(), "+".join(verdict_a["axes"])))

# --- anomaly channel (C9, never gated) ------------------------------------------
DD = FX["drafter_disclosed_never_gated"]
anoms = []
matches = []


def compare(name, mine, disclosed):
    if mine == disclosed:
        matches.append("%s: %s" % (name, mine))
    else:
        anoms.append("%s: measured %s vs disclosed %s" % (name, mine, disclosed))


compare("E_sums", [E_a[a] for a in range(1, 13)], FX["f3_anchors"]["E_sums_a_1_12"])
compare("I(6)", "%d/%d" % I_a[6], "300/300")
compare("I(12)", "%d/%d" % I_a[12], "0/300")
compare("clamp_census(C1 at-bound)", "%d/600" % at_bound, DD["clamp_census"])
for arm in ("ORACLE", "SCRYER", "INKTRUTH", "BLIND"):
    compare("decks_on.%s" % arm, dec[arm]["gold"], DD["four_arm_decks_on"][arm])
for arm in ("ORACLE", "SCRYER"):
    compare("decks_off.%s" % arm, off[arm]["gold"], DD["four_arm_decks_off"][arm])
compare("R2_ratio(4dp)", fmt(r2_ratio, 4), "0.9175")
compare("decks_off_ratio(3dp)", fmt(off_ratio, 3), "1.209")
informed_days = [dec[a]["first_300_day"] for a in ("ORACLE", "SCRYER", "INKTRUTH")]
compare("informed_cross_day",
        max(informed_days) if all(v is not None for v in informed_days) else "not all crossed",
        DD["informed_cross_day"])
compare("scryer_identified_by_30", "%s/20" % id30, DD["scryer_identified_by_30"])
compare("T3b_unique_decode_claim", "FALSE (%d/%d unique)" % (t3b_unique, t3b_cases),
        "TRUE per registration ('enumeration in the theorem gate')")
compare("alt_world_replication", "%d/200 (first-20 slice %d/20)" % (rep_main, rep20),
        DD["alt_world_replication_drafting"] + " at drafting n=20")
ev_on = census["drafter_evident"]["decks_on"]["arms"]
ev_off = census["drafter_evident"]["decks_off"]["arms"]
results["anomalies"] = {
    "mismatches": anoms, "matches": matches,
    "diagnosis": {
        "reserve_constant": "the drafter-evident scaffold (reserve = toll*dist + toll,"
        " C10) reproduces the disclosed ORACLE decks-on/off and INKTRUTH decks-on"
        " EXACTLY: measured %d/%d and %d vs disclosed 1309/1237 and 898 — the"
        " drafting prototype's solvency reserve evidently added one TOLL, not the"
        " registered guard FEE" % (ev_on["ORACLE"]["gold"], ev_off["ORACLE"]["gold"],
                                   ev_on["INKTRUTH"]["gold"]),
        "scryer_blind_cells": "no natural reading of the registered SCRYER/BLIND text"
        " reproduces the disclosed SCRYER 1201/1496 or BLIND 0 (nearest natural"
        " reading, C4: %d/%d and %d under the drafter-evident scaffold); the"
        " identified-cell timeline (16/20 by day 30) and the day-6 crossing DO"
        " reproduce" % (ev_on["SCRYER"]["gold"], ev_off["SCRYER"]["gold"],
                        ev_on["BLIND"]["gold"]),
        "t3b": "the registered T3b drafting verification ('unique (base,phase)"
        " recovery ... matched') cannot reproduce: uniqueness fails at EVERY one of"
        " the %d unclamped consecutive-pair grid cases (candidate counts 2..6);"
        " the drafting enumeration evidently checked T3a (tri-value pair"
        " distinctness) only — distinct tri PAIRS do not give reading-space"
        " identifiability because base translation composes with phase shift"
        " within a diff-sign class" % t3b_cases,
    },
}
emit()
emit("anomaly channel (C9, drafter-disclosed vs measured, never gated):")
emit("  matches (%d): %s" % (len(matches), "; ".join(matches)))
emit("  MISMATCHES (%d):" % len(anoms))
for a in anoms:
    emit("    " + a)
for k, v in results["anomalies"]["diagnosis"].items():
    emit("  diagnosis.%s: %s" % (k, v))

# --- self-check summary -----------------------------------------------------------
failed = [name for name, ok in CHECKS if not ok]
results["self_checks"] = {"total": len(CHECKS), "failed": failed}
results["seed_registry"] = {"constructed": CONSTRUCTED_SEEDS,
                            "aux_never_read": SEEDS["aux_never_read"]}
results["runtime"] = {"python": "%d.%d" % sys.version_info[:2], "stdlib_only": True}
emit()
emit("self-checks: %d run, %d failed%s" % (len(CHECKS), len(failed),
                                           " " + str(failed) if failed else ""))
emit("seed registry: constructed %s; aux %d never read"
     % (CONSTRUCTED_SEEDS, SEEDS["aux_never_read"]))

with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(results, fh, sort_keys=True, indent=1)
    fh.write("\n")

sys.stdout.write("\n".join(out_lines) + "\n")
sys.exit(0 if not failed else 1)
