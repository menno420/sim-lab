#!/usr/bin/env python3
"""VERDICT 066 — badge saturation: is the mineverse achievement catalog's
Coin Magnate line a wealth badge or an account-age badge under the hub's
own committed daily faucet? (idea-engine PROPOSAL 055)

Pinned committed model (all constants verbatim in fixtures.json, quoted at
superbot-mineverse@b983291 / superbot@3477594): badge rule
coins >= COIN_MAGNATE_THRESHOLD = 10_000; wallet = the hub shared wallet
("mutated only by economy_service"); faucet = _DAILY_TIERS — six
integer-uniform tiers, weights/100, E[!daily] = 169201/100 exact, one
claim per day (_DAILY_COOLDOWN = 86400). Player model (invented-but-
pinned): fresh wallet 0; per day claim w.p. p then spend floor(sigma*claim)
same day; T = first day wallet >= 10,000; season H = 90 days; grid
p in {1, 1/2, 1/4, 1/10} x sigma in {0, 1/2, 9/10}, DECISION world
sigma = 1/2; sigma in {0, 9/10} and H in {30, 180} reporting-only.

Arm A (DECISION, seedless): exact absorbing DP over integer wallet states
0..9999 (>= 10,000 absorbing), run-decomposed prefix-sum transitions,
every P(T <= n) an exact Fraction over denominator (2*10^6)^n (p on 20,
pmf on 10^5). Alone decision-bearing.
Arm S (robustness, seeded): MC N = 20,000/decision-cell,
random.Random(20261357), pinned draw order (claim-Bernoulli then
tier-then-uniform value exactly as economy_helpers._pick_daily draws it);
agreement <= 1/100 absolute on every decision P(T <= 90) cell AND
>= 4*SE headroom on every firing cell. Stability seed 20261358
(N = 10,000) reproduces the ruling through twin independently-written
evaluators. Reporting seed 20261359 (sigma worlds, H pair sanity). Aux
seed 20261360 NEVER read.

Decision rule pre-registered, applied IN ORDER: REJECT first (Arm A EXACT
at sigma = 1/2: P(T <= 90) >= 19/20 at >= 3 of 4 claim-rate cells AND
median T <= 14 days at the full-engagement (p = 1, sigma = 0) cell AND
every firing cell confirms in Arm S) -> APPROVE (P(T <= 90) <= 1/2 at
>= 2 of 4 AND >= 19/20 at <= 1, both arms, stability reproduced) -> NULL
(three named axes: band-straddle / concentration-miss / arm disagreement).
Gates F1-F5 + mechanical: run invalid on any failure.

Hermetic: reads ONLY its own fixtures.json. Stdlib-only. No wall-clock in
any output. CPython 3.11 pinned and asserted.

Run: python3 sims/verdict-066-badge-saturation/badge_saturation_sim.py
"""

import json
import math
import os
import random
import sys
from fractions import Fraction
from itertools import accumulate

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- checks --
_CHECKS = [0, 0]


def check(name, cond):
    if cond:
        _CHECKS[0] += 1
    else:
        _CHECKS[1] += 1
        print("SELF-CHECK FAIL: %s" % name)


def frac(s):
    """Parse an exact rational fixture string like '19/20' or '0'."""
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(s))


# ------------------------------------------------------------- fixtures ---
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check("cpython implementation", sys.implementation.name == "cpython")
check("cpython minor pinned == %s" % FX["meta"]["cpython_minor_pin"],
      "%d.%d" % sys.version_info[:2] == FX["meta"]["cpython_minor_pin"])

TIERS = [tuple(t) for t in FX["faucet"]["tiers"]]
WEIGHT_DEN = FX["faucet"]["weight_denominator"]
VALUE_DEN = FX["faucet"]["value_denominator"]
THRESHOLD = FX["badge"]["coin_magnate_threshold"]
P_DEN = FX["player_model"]["p_denominator"]
DAY_DEN = FX["player_model"]["day_denominator"]
H_SEASON = FX["player_model"]["season_horizon_days"]
H_PAIR = FX["player_model"]["H_reporting_pair"]
P_GRID = [frac(s) for s in FX["player_model"]["p_grid"]]          # 1 down to 1/10
SIGMA_GRID = [frac(s) for s in FX["player_model"]["sigma_grid"]]  # 0, 1/2, 9/10
DEC_SIGMA = frac(FX["player_model"]["decision_sigma"])
BAND = frac(FX["bands"]["reject"]["share_band"])                  # 19/20
MEDIAN_MAX = FX["bands"]["reject"]["median_conjunct_days"]        # 14
AGREE_ABS = float(frac(FX["bands"]["agreement_abs"]))             # 0.01
SE_MULT = FX["bands"]["agreement_se_multiplier"]                  # 4
SEEDS = FX["seeds"]
N_DEC = FX["trajectory_counts"]["decision_per_cell"]
N_STAB = FX["trajectory_counts"]["stability_per_cell"]
N_REP = FX["trajectory_counts"]["reporting_per_cell"]
CAP = FX["cstar_menu"]["wallet_cap"]
REEXPRESS = FX["cstar_menu"]["reexpress_thresholds"]
DAY_GRID = FX["fixture_level_choices_disclosed"]["stdout_day_grid"]

check("p grid denominators land on 20",
      all((P_DEN * p).denominator == 1 for p in P_GRID))
check("day denominator == 20 * 10^5", DAY_DEN == P_DEN * VALUE_DEN)

# ------------------------------------------------- F1: the anchor gate ----
per_value = {}   # claim value -> exact numerator over VALUE_DEN
check("weights sum to 100", sum(w for _, _, w in TIERS) == WEIGHT_DEN)
for lo, hi, w in TIERS:
    count = hi - lo + 1
    total_num = w * (VALUE_DEN // WEIGHT_DEN)   # w/100 over 10^5 -> w*1000
    check("tier [%d,%d] per-value numerator divides evenly" % (lo, hi),
          total_num % count == 0)
    pv = total_num // count
    for v in range(lo, hi + 1):
        per_value[v] = per_value.get(v, 0) + pv

derived_rows = [[lo, hi, per_value[lo]] for lo, hi, _ in TIERS]
check("per-value numerator table matches fixture derivation",
      derived_rows == FX["faucet"]["per_value_numerators_over_1e5_derived"])
check("pmf total mass == 1", sum(per_value.values()) == VALUE_DEN)
E_DAILY = Fraction(sum(n * v for v, n in per_value.items()), VALUE_DEN)
check("F1 anchor: E[!daily] == 169201/100 exact",
      E_DAILY == frac(FX["faucet"]["E_daily_exact"]))
E2_DAILY = Fraction(sum(n * v * v for v, n in per_value.items()), VALUE_DEN)
VAR_DAILY = E2_DAILY - E_DAILY * E_DAILY
SD_DAILY = math.sqrt(VAR_DAILY.numerator / VAR_DAILY.denominator)
# A1 reconciliation: the registration's Common '9' is exact over 10^4.
check("A1 reconciliation: Common per-value probability == 9/10^4 exactly",
      Fraction(per_value[500], VALUE_DEN) == Fraction(9, 10 ** 4))
check("A1 anomaly is real: 9/10^5 is NOT the Common per-value probability",
      Fraction(per_value[500], VALUE_DEN) != Fraction(9, 10 ** 5))
THRESH_IN_DAILIES = Fraction(THRESHOLD) / E_DAILY


# ----------------------------------------------- net transform + runs -----
def net_value(v, sigma):
    return v - (sigma.numerator * v) // sigma.denominator


def net_pmf(sigma):
    pmf = {}
    for v, n in per_value.items():
        w = net_value(v, sigma)
        pmf[w] = pmf.get(w, 0) + n
    return pmf


def run_decompose(pmf):
    """Maximal runs of consecutive integers with equal numerator."""
    runs = []
    for w in sorted(pmf):
        n = pmf[w]
        if runs and runs[-1][1] == w - 1 and runs[-1][2] == n:
            runs[-1][1] = w
        else:
            runs.append([w, w, n])
    return [tuple(r) for r in runs]


NET = {}
RUNS = {}
for sig in SIGMA_GRID:
    NET[sig] = net_pmf(sig)
    RUNS[sig] = run_decompose(NET[sig])
    check("net pmf mass == 1 at sigma=%s" % sig,
          sum(NET[sig].values()) == VALUE_DEN)
    check("run decomposition conserves mass at sigma=%s" % sig,
          sum(n * (hi - lo + 1) for lo, hi, n in RUNS[sig]) == VALUE_DEN)
    check("net values all positive at sigma=%s (wallet monotone)" % sig,
          min(NET[sig]) > 0)
check("F5 degenerate transform: sigma=0 net pmf == committed pmf identically",
      NET[Fraction(0)] == per_value)


# ------------------------------------------------ Arm A: absorbing DP -----
def absorbing_dp(sigma, p, C, days):
    """Exact absorbing DP; returns list absorbed[n] = integer numerator of
    P(T <= n) over DAY_DEN**n, n = 1..days. Mass conservation asserted
    every day (F5)."""
    runs = RUNS[sigma]
    a = int(p * P_DEN)
    noclaim = (P_DEN - a) * VALUE_DEN
    dist = [0] * C
    dist[0] = 1
    absorbed = 0
    denom = 1
    out = []
    conserved = True
    for _ in range(days):
        P = list(accumulate(dist, initial=0))          # len C+1
        Q = list(accumulate(P, initial=0))             # len C+2
        total = P[C]
        if noclaim:
            new = [noclaim * x for x in dist]
        else:
            new = [0] * C
        add_abs = 0
        for lo, hi, num in runs:
            m = a * num
            width = hi - lo + 1
            hc = min(hi, C - 1)
            if lo <= C - 1:
                seg = P[1: hc - lo + 2]
                new[lo: hc + 1] = [x + m * y
                                   for x, y in zip(new[lo: hc + 1], seg)]
            if hi + 1 <= C - 1:
                s1 = P[hi - lo + 2: C - lo + 1]
                s0 = P[1: C - hi]
                new[hi + 1: C] = [x + m * (u - w) for x, u, w
                                  in zip(new[hi + 1: C], s1, s0)]
            # mass sent to >= C by this run (hi < C here):
            add_abs += m * (width * total - (Q[C - lo + 1] - Q[C - hi]))
        absorbed = absorbed * DAY_DEN + add_abs
        denom *= DAY_DEN
        conserved = conserved and (sum(new) + absorbed == denom)
        dist = new
        out.append(absorbed)
    check("F5 mass conservation every day (sigma=%s p=%s C=%d days=%d)"
          % (sigma, p, C, days), conserved)
    return out


def p_le(absorbed, n):
    return Fraction(absorbed[n - 1], DAY_DEN ** n)


def median_from(absorbed):
    """Minimal n with P(T <= n) >= 1/2 (integer cross-mult); None if not
    reached within the computed horizon."""
    for n, num in enumerate(absorbed, start=1):
        if 2 * num >= DAY_DEN ** n:
            return n
    return None


# Horizons per cell (fixture-disclosed).
CELLS = []   # (sigma, p, days)
for p in P_GRID:
    CELLS.append((DEC_SIGMA, p, 180))
CELLS.append((Fraction(0), Fraction(1), 20))
for p in P_GRID[1:]:
    CELLS.append((Fraction(0), p, 90))
for p in P_GRID:
    CELLS.append((Fraction(9, 10), p, 90))

ARM_A = {}
for sigma, p, days in CELLS:
    ARM_A[(sigma, p)] = absorbing_dp(sigma, p, THRESHOLD, days)

# --------------------------------------------------- F2: identities -------
abs10 = ARM_A[(Fraction(0), Fraction(1))]
check("F2: P(T <= 1) == 0 at (1,0)", p_le(abs10, 1) == 0)
check("F2: P(T <= 2) == (2/100)^2 == 1/2500 exact at (1,0)",
      p_le(abs10, 2) == Fraction(1, 2500))
check("F2: T <= 20 with probability exactly 1 at (1,0)",
      p_le(abs10, 20) == 1)
for p in P_GRID:
    check("F2: P(T <= 3) == 0 at sigma=1/2 p=%s" % p,
          p_le(ARM_A[(DEC_SIGMA, p)], 3) == 0)

# Decision numbers (Arm A exact, alone decision-bearing).
DEC90 = [(p, p_le(ARM_A[(DEC_SIGMA, p)], 90)) for p in P_GRID]
MEDIAN_FULL = median_from(abs10)
MEDIANS_DEC = [(p, median_from(ARM_A[(DEC_SIGMA, p)])) for p in P_GRID]

# T law at (1,0): exact pmf to day 20 -> E, Var, CV.
pmf_T = []
prev = Fraction(0)
for n in range(1, 21):
    cur = p_le(abs10, n)
    pmf_T.append(cur - prev)
    prev = cur
check("T pmf at (1,0) sums to 1 exactly", sum(pmf_T) == 1)
E_T = sum(Fraction(n) * q for n, q in enumerate(pmf_T, start=1))
E_T2 = sum(Fraction(n * n) * q for n, q in enumerate(pmf_T, start=1))
VAR_T = E_T2 - E_T * E_T
CV_T = math.sqrt(VAR_T.numerator / VAR_T.denominator) / float(E_T)

# --------------------------------------------- F4: monotonicity gates -----
for sigma, p, days in CELLS:
    absn = ARM_A[(sigma, p)]
    check("F4: P(T <= n) non-decreasing in n (sigma=%s p=%s)" % (sigma, p),
          all(absn[i] * DAY_DEN <= absn[i + 1]
              for i in range(len(absn) - 1)))
for sigma in SIGMA_GRID:
    vals = []
    for p in P_GRID:  # descending p
        absn = ARM_A[(sigma, p)]
        n = min(90, len(absn))
        vals.append(p_le(absn, n))  # (1,0) cell: P(T<=20)==1==P(T<=90)
    check("F4: P(T <= 90) non-decreasing in p at sigma=%s" % sigma,
          all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1)))
    meds = []
    for p in P_GRID:
        m = median_from(ARM_A[(sigma, p)])
        meds.append(m if m is not None else 10 ** 9)
    check("F4: median T non-increasing in p at sigma=%s" % sigma,
          all(meds[i] <= meds[i + 1] for i in range(len(meds) - 1)))
for p in P_GRID:
    row = []
    for sigma in SIGMA_GRID:  # ascending sigma
        absn = ARM_A[(sigma, p)]
        n = min(90, len(absn))
        row.append(p_le(absn, n))
    check("F4: P(T <= 90) non-increasing in sigma at p=%s" % p,
          all(row[i] >= row[i + 1] for i in range(len(row) - 1)))

# ------------------------------------- C* menu: exact day-90 wallet law ---
def mixture_tails(sigma, days, cap):
    """Exact tail arrays of W_days per decision p, via W = S_K,
    K ~ Binomial(days, p) independent of claim values; S_k by exact capped
    convolution (monotone overflow bucket). Returns {p: suffix} where
    suffix[c] = integer numerator of P(W_days >= c) over DAY_DEN**days
    for c in 0..cap, suffix[cap+1] = bucket (mass strictly above cap)."""
    runs = RUNS[sigma]
    maxnet = max(hi for _, hi, _ in runs)
    sk = [0] * (cap + 1)
    sk[0] = 1
    bucket = 0
    acc = {}
    accb = {}
    for p in P_GRID:
        a = int(p * P_DEN)
        acc[p] = [0] * (cap + 1)
        accb[p] = 0
        w0 = math.comb(days, 0) * (P_DEN - a) ** days * VALUE_DEN ** days
        acc[p][0] += w0 * sk[0]
    conserved = True
    hi_support = 0
    for k in range(1, days + 1):
        width = min(hi_support + maxnet, cap + maxnet) + 1
        P = list(accumulate(sk, initial=0))
        total = P[-1]
        P.extend([total] * (width + 2 - len(P)))
        new = [0] * width
        for lo, hi, num in runs:
            hc = min(hi, width - 1)
            if lo <= width - 1:
                seg = P[1: hc - lo + 2]
                new[lo: hc + 1] = [x + num * y
                                   for x, y in zip(new[lo: hc + 1], seg)]
            if hi + 1 <= width - 1:
                s1 = P[hi - lo + 2: width - lo + 1]
                s0 = P[1: width - hi]
                new[hi + 1: width] = [x + num * (u - w) for x, u, w
                                      in zip(new[hi + 1: width], s1, s0)]
        bucket = bucket * VALUE_DEN + sum(new[cap + 1:])
        sk = new[:cap + 1]
        if len(sk) < cap + 1:
            sk.extend([0] * (cap + 1 - len(sk)))
        hi_support = min(hi_support + maxnet, cap)
        conserved = conserved and (sum(sk) + bucket == VALUE_DEN ** k)
        for p in P_GRID:
            a = int(p * P_DEN)
            if a == P_DEN and k < days:
                continue   # binomial weight is 0
            wk = (math.comb(days, k) * a ** k * (P_DEN - a) ** (days - k)
                  * VALUE_DEN ** (days - k))
            if wk == 0:
                continue
            top = min(hi_support, cap)
            tgt = acc[p]
            tgt[:top + 1] = [x + wk * y
                             for x, y in zip(tgt[:top + 1], sk[:top + 1])]
            accb[p] += wk * bucket
    check("C* machinery: S_k mass conservation every k (sigma=%s)" % sigma,
          conserved)
    tails = {}
    total_den = DAY_DEN ** days
    for p in P_GRID:
        suf = [0] * (cap + 2)
        suf[cap + 1] = accb[p]
        arr = acc[p]
        run_sum = accb[p]
        for c in range(cap, -1, -1):
            run_sum += arr[c]
            suf[c] = run_sum
        check("C* machinery: total mass == 1 exactly (sigma=%s p=%s)"
              % (sigma, p), suf[0] == total_den)
        tails[p] = suf
    return tails


TAILS = mixture_tails(DEC_SIGMA, H_SEASON, CAP)
TOTAL90 = DAY_DEN ** H_SEASON
CSTAR = {}
REEXP = {}
for p in P_GRID:
    suf = TAILS[p]
    check("cross-structure: P(W_90 >= 10000) == absorbing P(T <= 90) exact "
          "(p=%s)" % p,
          Fraction(suf[THRESHOLD], TOTAL90) == dict(DEC90)[p])
    cstar = None
    lo_i, hi_i = 1, CAP
    while lo_i <= hi_i:                       # binary search on monotone tail
        mid = (lo_i + hi_i) // 2
        if 2 * suf[mid] <= TOTAL90:
            cstar = mid
            hi_i = mid - 1
        else:
            lo_i = mid + 1
    check("C* found within the 100,000 cap (p=%s)" % p, cstar is not None)
    if cstar is not None:
        check("C* is minimal: tail(C*-1) > 1/2 >= tail(C*) (p=%s)" % p,
              2 * suf[cstar - 1] > TOTAL90 and 2 * suf[cstar] <= TOTAL90)
    CSTAR[p] = cstar
    REEXP[p] = {c: Fraction(suf[c], TOTAL90) for c in REEXPRESS}
    seq = [Fraction(suf[c], TOTAL90)
           for c in [THRESHOLD] + REEXPRESS]
    check("F4: P(T <= 90) non-increasing in threshold C (p=%s)" % p,
          all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1)))

# ----------------------------------------------- F3: static badge rows ----
CAT = FX["badge"]["catalog_constants"]
SLOTS = FX["badge"]["equipment_slots_closed_enum"]
check("closed slot enum has 9 slots", len(SLOTS) == 9)


def int_values(store):
    if not isinstance(store, dict):
        return []
    return [v for v in store.values() if isinstance(v, int)]


def earned_achievements(miner, max_depth):
    """Re-implemented verbatim from server/views.py @ b983291."""
    inventory = int_values(miner.get("mining_inventory"))
    skills = int_values(miner.get("skills"))
    wears = int_values(miner.get("gear_wear"))
    equipment = miner.get("equipment")
    equipment = equipment if isinstance(equipment, dict) else {}
    earned = []
    if isinstance(miner.get("record_depth"), int) \
            and miner["record_depth"] == max_depth:
        earned.append("deep_diver")
    if sum(inventory) >= CAT["PACKRAT_THRESHOLD"]:
        earned.append("packrat")
    if isinstance(miner.get("coins"), int) \
            and miner["coins"] >= CAT["COIN_MAGNATE_THRESHOLD"]:
        earned.append("coin_magnate")
    if all(equipment.get(slot) for slot in SLOTS):
        earned.append("fully_geared")
    if any(wear >= CAT["TOOL_BREAKER_WEAR"] for wear in wears):
        earned.append("tool_breaker")
    if len(skills) >= CAT["BALANCED_BUILD_MIN_SKILLS"] \
            and max(skills) - min(skills) <= CAT["BALANCED_BUILD_MAX_SPREAD"]:
        earned.append("balanced_build")
    if any(count == CAT["THE_ANSWER_COUNT"] for count in inventory):
        earned.append("the_answer")
    return earned


MINERS = FX["sample"]["miners"]
MAX_DEPTH = FX["sample"]["max_depth"]
STATIC_ROWS = {}
hits = {b: [] for b in FX["badge"]["catalog_order"]}
for miner in MINERS:
    earned = earned_achievements(miner, MAX_DEPTH)
    STATIC_ROWS[miner["display_name"]] = earned
    for b in earned:
        hits[b].append(miner["display_name"])
for badge, expect in FX["sample"]["registered_F3_hit_lists"].items():
    check("F3: %s hit list reproduces the calibration comments exactly"
          % badge, hits[badge] == expect)
for name, tot in FX["sample"]["registered_derived_table"]["pack_totals"].items():
    m = next(x for x in MINERS if x["display_name"] == name)
    check("F3: pack total %s == %d" % (name, tot),
          sum(int_values(m["mining_inventory"])) == tot)
for name, wmax in FX["sample"]["registered_derived_table"]["wear_max"].items():
    m = next(x for x in MINERS if x["display_name"] == name)
    check("F3: wear max %s == %d" % (name, wmax),
          max(int_values(m["gear_wear"])) == wmax)
check("F3: the 42-stone row (DeepDelver)",
      next(x for x in MINERS
           if x["display_name"] == "DeepDelver")["mining_inventory"]["stone"]
      == CAT["THE_ANSWER_COUNT"])
check("F3: deep_diver saturation - record_depth caps at max_depth 3, "
      "2 of 7 sample miners already hold it",
      MAX_DEPTH == 3 and len(hits["deep_diver"]) == 2)

# ------------------------------------------------------- Arm S (MC) -------
_RNG_LOG = []


def make_rng(seed):
    _RNG_LOG.append(seed)
    return random.Random(seed)


TIER_IDX = list(range(6))
TIER_W = [w for _, _, w in TIERS]
TIER_LOHI = [(lo, hi) for lo, hi, _ in TIERS]


def mc_leg(rng, sigmas, N, horizon):
    """Pinned loop order: sigma ascending, p descending, trajectories
    sequential; per day one claim-Bernoulli draw, value draw
    (tier-then-uniform) on claim days only; full horizon simulated."""
    out = {}
    for sigma in sigmas:
        sn, sd = sigma.numerator, sigma.denominator
        for p in P_GRID:
            pf = float(p)
            ber = 0
            val = 0
            succ = 0
            for _ in range(N):
                wallet = 0
                crossed = False
                for _day in range(horizon):
                    ber += 1
                    if rng.random() < pf:
                        val += 1
                        ti = rng.choices(TIER_IDX, weights=TIER_W, k=1)[0]
                        lo, hi = TIER_LOHI[ti]
                        v = rng.randint(lo, hi)
                        wallet += v - (sn * v) // sd
                        if not crossed and wallet >= THRESHOLD:
                            crossed = True
                if crossed:
                    succ += 1
            check("draw sentinel: bernoulli draws == N*horizon "
                  "(sigma=%s p=%s N=%d)" % (sigma, p, N),
                  ber == N * horizon)
            if p == 1:
                check("draw sentinel: value draws == bernoulli draws on "
                      "p=1 (sigma=%s N=%d)" % (sigma, N), val == ber)
            check("draw sentinel: value draws <= bernoulli draws "
                  "(sigma=%s p=%s N=%d)" % (sigma, p, N), val <= ber)
            out[(sigma, p)] = {"succ": succ, "N": N,
                               "bernoulli_draws": ber, "value_draws": val}
    return out


RNG_HEAD = make_rng(SEEDS["arm_s_headline"])
MC_HEAD = mc_leg(RNG_HEAD, [DEC_SIGMA], N_DEC, H_SEASON)
RNG_STAB = make_rng(SEEDS["stability"])
MC_STAB = mc_leg(RNG_STAB, [DEC_SIGMA], N_STAB, H_SEASON)
RNG_REP = make_rng(SEEDS["reporting"])
MC_REP = mc_leg(RNG_REP, [Fraction(0), Fraction(9, 10)], N_REP, H_SEASON)

check("mechanical: RNGs constructed in pinned order 20261357 -> 20261358 "
      "-> 20261359 and nothing else",
      _RNG_LOG == [SEEDS["arm_s_headline"], SEEDS["stability"],
                   SEEDS["reporting"]])
check("mechanical: aux seed 20261360 never constructed, never read",
      SEEDS["aux_never_read"] not in _RNG_LOG)


def mc_view(mc, sigma):
    """est/dev/SE per decision p against Arm A exact (exact-variance SE)."""
    view = {}
    for p in P_GRID:
        cell = mc[(sigma, p)]
        est = cell["succ"] / cell["N"]
        pa = dict(DEC90)[p] if sigma == DEC_SIGMA else None
        paf = float(pa)
        se = math.sqrt(paf * (1.0 - paf) / cell["N"])
        view[p] = {"est": est, "exact": paf, "dev": abs(est - paf),
                   "se": se, "succ": cell["succ"], "N": cell["N"]}
    return view


VIEW_HEAD = mc_view(MC_HEAD, DEC_SIGMA)
VIEW_STAB = mc_view(MC_STAB, DEC_SIGMA)

for p in P_GRID:   # registered Arm S agreement gate, every decision cell
    check("Arm S agreement <= 1/100 absolute (headline, p=%s)" % p,
          VIEW_HEAD[p]["dev"] <= AGREE_ABS)

# Reporting-only sanity (fixture-disclosed tolerance, never decision-bearing)
REP_TABLE = []
for sigma in [Fraction(0), Fraction(9, 10)]:
    for p in P_GRID:
        cell = MC_REP[(sigma, p)]
        absn = ARM_A[(sigma, p)]
        n = min(90, len(absn))
        exact = p_le(absn, n)
        est = cell["succ"] / cell["N"]
        dev = abs(est - float(exact))
        check("reporting MC sanity <= 0.025 (sigma=%s p=%s)" % (sigma, p),
              dev <= 0.025)
        REP_TABLE.append((sigma, p, exact, est, dev))


# ------------------------------------------------- twin evaluators --------
def evaluator_A(dec90, median_full, view):
    """Procedural, on Fractions + float MC. Registered order, REJECT first."""
    band = BAND
    firing = [p for p, f in dec90 if f >= band]
    confirm = all(view[p]["dev"] <= AGREE_ABS
                  and (view[p]["est"] - float(band)) >= SE_MULT * view[p]["se"]
                  for p in firing)
    reject_arith = (len(firing) >= FX["bands"]["reject"]
                    ["cells_at_or_above_band_required"]
                    and median_full is not None
                    and median_full <= MEDIAN_MAX)
    if reject_arith and confirm:
        return ("REJECT", None)
    le_half = [p for p, f in dec90 if f <= Fraction(1, 2)]
    s_le_half = [p for p, _ in dec90 if view[p]["est"] <= 0.5]
    s_firing = [p for p, _ in dec90 if view[p]["est"] >= float(band)]
    approve = (len(le_half) >= FX["bands"]["approve"]["le_half_cells_required"]
               and len(firing) <= FX["bands"]["approve"]["ge_band_cells_max"]
               and len(s_le_half) >= 2 and len(s_firing) <= 1)
    if approve:
        return ("APPROVE", None)
    if reject_arith and not confirm:
        return ("NULL", "arm-disagreement")
    if len(firing) >= 3 and not (median_full is not None
                                 and median_full <= MEDIAN_MAX):
        return ("NULL", "concentration-miss")
    return ("NULL", "band-straddle")


def evaluator_B(dec90, median_full, view):
    """Independently written: pure-integer cross-multiplication on the
    exact side, count flags + decision table."""
    flags = {}
    n_fire = n_half = ns_fire = ns_half = 0
    fire_ok = True
    for p, f in dec90:
        num, den = f.numerator, f.denominator
        fires = 20 * num >= 19 * den
        n_fire += 1 if fires else 0
        n_half += 1 if 2 * num <= den else 0
        cell = view[p]
        s20 = cell["succ"] * 20
        ns_fire += 1 if s20 >= 19 * cell["N"] else 0
        ns_half += 1 if 2 * cell["succ"] <= cell["N"] else 0
        if fires:
            agree = abs(cell["succ"] * den - cell["N"] * num) * 100 \
                <= cell["N"] * den
            head = (s20 - 19 * cell["N"]) >= SE_MULT * cell["se"] * 20 \
                * cell["N"]
            fire_ok = fire_ok and agree and head
    flags["F"] = n_fire >= 3
    flags["M"] = (median_full is not None) and (median_full <= 14)
    flags["C"] = fire_ok
    flags["L"] = n_half >= 2 and ns_half >= 2
    flags["U"] = n_fire <= 1 and ns_fire <= 1
    if flags["F"] and flags["M"] and flags["C"]:
        return ("REJECT", None)
    if flags["L"] and flags["U"]:
        return ("APPROVE", None)
    if flags["F"] and flags["M"] and not flags["C"]:
        return ("NULL", "arm-disagreement")
    if flags["F"] and not flags["M"]:
        return ("NULL", "concentration-miss")
    return ("NULL", "band-straddle")


RULING_A = evaluator_A(DEC90, MEDIAN_FULL, VIEW_HEAD)
RULING_B = evaluator_B(DEC90, MEDIAN_FULL, VIEW_HEAD)
check("twin evaluators agree on the headline ruling", RULING_A == RULING_B)
STAB_A = evaluator_A(DEC90, MEDIAN_FULL, VIEW_STAB)
STAB_B = evaluator_B(DEC90, MEDIAN_FULL, VIEW_STAB)
check("twin evaluators agree on the stability ruling", STAB_A == STAB_B)
check("stability leg (seed %d, N=%d) reproduces the ruling"
      % (SEEDS["stability"], N_STAB), STAB_A == RULING_A)
RULING = RULING_A

# ------------------------------------------ drafter comparison (never
# gated; reported first-class) --------------------------------------------
draft = FX["drafter_reference_never_gated"]
DRAFT_CMP = []
for (p, f), ref in zip(DEC90, draft["sigma_half_P_T_le_90"]):
    ours = "%.6f" % float(f)
    DRAFT_CMP.append(("sigma=1/2 p=%s" % p, ref, ours, ours == ref))
for (sigma, p, exact, _e, _d), ref in zip(
        [r for r in REP_TABLE if r[0] == Fraction(9, 10)],
        draft["sigma_910_P_T_le_90"]):
    ours = "%.6f" % float(exact)
    DRAFT_CMP.append(("sigma=9/10 p=%s" % p, ref, ours, ours == ref))
DRAFT_CMP.append(("median (1,0)", str(draft["full_engagement_median_sigma0"]),
                  str(MEDIAN_FULL),
                  MEDIAN_FULL == draft["full_engagement_median_sigma0"]))
med_half_p1 = median_from(ARM_A[(DEC_SIGMA, Fraction(1))])
DRAFT_CMP.append(("median (1, 1/2)", str(draft["median_sigma_half_p1"]),
                  str(med_half_p1),
                  med_half_p1 == draft["median_sigma_half_p1"]))

# ------------------------------------------------------------ output ------
LINES = []


def emit(s=""):
    LINES.append(s)


F = lambda x: "%.6f" % float(x)

emit("VERDICT 066 — badge saturation: Coin Magnate vs the committed daily "
     "faucet (idea-engine PROPOSAL 055)")
emit("python: cpython-%s (pinned) · stdlib-only · hermetic (reads only "
     "fixtures.json) · no wall-clock in output" % FX["meta"]["cpython_minor_pin"])
emit()
emit("[F1] anchor: E[!daily] = %s = %s exact · weights sum %d · SD[claim] "
     "= %.6f (exact Var %s)"
     % (E_DAILY, F(E_DAILY), WEIGHT_DEN, SD_DAILY, VAR_DAILY))
emit("     threshold 10,000 coins = %s = %.6f expected dailies"
     % (THRESH_IN_DAILIES, float(THRESH_IN_DAILIES)))
emit("     per-value numerators over 10^5 (derived, asserted): %s"
     % FX["faucet"]["per_value_numerators_over_1e5_derived"])
emit("     ANOMALY A1: the registration writes the Common row as 9/10^5; "
     "exact is 9/10^4 (= 90/10^5) — denominator slip, decision unaffected")
emit()
emit("[F3] static badge rows @ b983291 (re-implemented earned_achievements "
     "over the 7 fixture miners — calibration comments reproduce exactly):")
for m in MINERS:
    emit("     %-13s coins %6d · earned: %s"
         % (m["display_name"], m["coins"],
            ", ".join(STATIC_ROWS[m["display_name"]]) or "(none)"))
emit("     deep_diver saturation note: record_depth ∈ {0..%d} caps at the "
     "contract's own max_depth — 2 of 7 sample miners already hold it"
     % MAX_DEPTH)
emit()
emit("ARM A (DECISION, exact absorbing DP, alone decision-bearing) — "
     "sigma = 1/2:")
emit("  %-6s %-12s %-12s %-12s %-10s" % ("p", "P(T<=30)", "P(T<=90)",
                                         "P(T<=180)", "median T"))
for p in P_GRID:
    absn = ARM_A[(DEC_SIGMA, p)]
    med = median_from(absn)
    emit("  %-6s %-12s %-12s %-12s %-10s"
         % (p, F(p_le(absn, 30)), F(p_le(absn, 90)), F(p_le(absn, 180)),
            med if med is not None else ">180"))
emit("  exact decision cells P(T<=90): %s"
     % " · ".join("p=%s: %s…/…%s digits" % (p, str(f.numerator)[:12],
                                            len(str(f.denominator)))
                  for p, f in DEC90))
emit("  full-engagement (p=1, sigma=0): median T = %d · E[T] = %s = %.6f "
     "· Var[T] = %.6f · CV[T] = %.6f (the age-badge concentration mark)"
     % (MEDIAN_FULL, E_T, float(E_T), float(VAR_T), CV_T))
emit()
emit("sigma worlds (reporting-only, Arm A exact at H=90):")
emit("  %-8s %-6s %-12s %-10s" % ("sigma", "p", "P(T<=90)", "median T"))
for sigma in SIGMA_GRID:
    for p in P_GRID:
        absn = ARM_A[(sigma, p)]
        n = min(90, len(absn))
        med = median_from(absn)
        emit("  %-8s %-6s %-12s %-10s"
             % (sigma, p, F(p_le(absn, n)),
                med if med is not None else ">%d" % len(absn)))
emit()
emit("badge-share curves S(d) = P(T <= d), sigma = 1/2 (day · expected "
     "dailies claimed d·p · share):")
for p in P_GRID:
    absn = ARM_A[(DEC_SIGMA, p)]
    row = " · ".join("d=%d (%.1f): %s" % (d, float(p * d), F(p_le(absn, d)))
                     for d in DAY_GRID)
    emit("  p=%-5s %s" % (p, row))
emit()
emit("C* threshold menu (exact minimal C with P(T <= 90) <= 1/2, per "
     "decision cell) + committed threshold re-expressed:")
emit("  %-6s %-9s %-14s %-14s %-14s %-14s"
     % ("p", "C*", "P90@10000", "P90@20000", "P90@50000", "P90@100000"))
for p in P_GRID:
    emit("  %-6s %-9s %-14s %-14s %-14s %-14s"
         % (p, CSTAR[p], F(dict(DEC90)[p]), F(REEXP[p][20000]),
            F(REEXP[p][50000]), F(REEXP[p][100000])))
emit("  C* in expected dailies: %s"
     % " · ".join("p=%s: %.3f" % (p, CSTAR[p] / float(E_DAILY))
                  for p in P_GRID))
emit()
emit("ARM S (seed %d, N = %d/cell) — agreement vs Arm A exact "
     "(<= 1/100 abs; firing cells >= %d·SE headroom above 19/20):"
     % (SEEDS["arm_s_headline"], N_DEC, SE_MULT))
emit("  %-6s %-10s %-10s %-10s %-12s %-12s"
     % ("p", "est", "exact", "|dev|", "SE(exact)", "headroom/SE"))
for p in P_GRID:
    c = VIEW_HEAD[p]
    hr = ("%.2f" % ((c["est"] - 0.95) / c["se"])) if c["se"] > 0 else "inf"
    emit("  %-6s %-10.6f %-10.6f %-10.6f %-12.6g %-12s"
         % (p, c["est"], c["exact"], c["dev"], c["se"], hr))
emit("  draw totals: bernoulli %s · value %s"
     % (sum(v["bernoulli_draws"] for v in MC_HEAD.values()),
        sum(v["value_draws"] for v in MC_HEAD.values())))
emit()
emit("STABILITY (seed %d, N = %d/cell): class %s%s — %s"
     % (SEEDS["stability"], N_STAB, STAB_A[0],
        "" if STAB_A[1] is None else " (%s)" % STAB_A[1],
        "REPRODUCES" if STAB_A == RULING_A else "DOES NOT REPRODUCE"))
emit("REPORTING MC (seed %d, N = %d/cell, sanity only):"
     % (SEEDS["reporting"], N_REP))
for sigma, p, exact, est, dev in REP_TABLE:
    emit("  sigma=%-5s p=%-5s exact %s · est %.6f · |dev| %.6f"
         % (sigma, p, F(exact), est, dev))
emit()
emit("drafter-reference comparison (NEVER gated):")
for label, ref, ours, ok in DRAFT_CMP:
    emit("  %-18s drafter %-10s re-derived %-10s %s"
         % (label, ref, ours, "MATCH" if ok else "MISMATCH"))
emit()
emit("DECISION (pre-registered order, REJECT first; Arm A exact alone "
     "decision-bearing):")
firing = [p for p, f in DEC90 if f >= BAND]
emit("  REJECT rule: P(T<=90) >= 19/20 at >= 3 of 4 cells at sigma=1/2 -> "
     "%d of 4 fire (%s)"
     % (len(firing), ", ".join("p=%s" % p for p in firing)))
emit("               median T <= 14 at (p=1, sigma=0) -> median = %d"
     % MEDIAN_FULL)
emit("               every firing cell confirms in Arm S (1/100 + %d·SE) "
     "-> %s"
     % (SE_MULT,
        all(VIEW_HEAD[p]["dev"] <= AGREE_ABS
            and (VIEW_HEAD[p]["est"] - 0.95) >= SE_MULT * VIEW_HEAD[p]["se"]
            for p in firing)))
emit("  RULING: %s%s"
     % (RULING[0], "" if RULING[1] is None else " (axis: %s)" % RULING[1]))
emit()
emit("anomalies (first-class): A1 registration per-value Common-row "
     "denominator slip (9/10^5 written; 9/10^4 exact — forced by the "
     "registration's own weights-sum-100 and E = 169201/100) · A2 the "
     "outbox idea: blob pin 4df5043 is a pre-squash branch commit absent "
     "from idea-engine main history (HEAD 18f3171 copy verified "
     "constant-identical, authoritative) · A3 superbot _daily_weights "
     "streak-luck shift excluded by the registered base-weight model "
     "(streak-0 floor; direction REJECT-robust, anticipated by the "
     "registration)")
emit()
emit("SELF-CHECKS: %d passed, %d failed" % (_CHECKS[0], _CHECKS[1]))

STDOUT = "\n".join(LINES) + "\n"
sys.stdout.write(STDOUT)

# --------------------------------------------------------- results.json ---
results = {
    "verdict": "066",
    "proposal": FX["meta"]["proposal_header_verbatim"],
    "ruling": {"class": RULING[0], "null_axis": RULING[1]},
    "decision_cells_sigma_half_P_T_le_90_exact": {
        str(p): "%d/%d" % (f.numerator, f.denominator) for p, f in DEC90},
    "decision_cells_sigma_half_P_T_le_90_float": {
        str(p): float(f) for p, f in DEC90},
    "firing_cells": [str(p) for p in firing],
    "median_T": {
        "full_engagement_p1_sigma0": MEDIAN_FULL,
        "sigma_half": {str(p): m for p, m in MEDIANS_DEC}},
    "T_law_full_engagement": {
        "E_T_exact": str(E_T), "E_T": float(E_T),
        "Var_T_exact": str(VAR_T), "Var_T": float(VAR_T), "CV_T": CV_T,
        "pmf": [float(q) for q in pmf_T]},
    "anchor": {
        "E_daily_exact": str(E_DAILY),
        "Var_daily_exact": str(VAR_DAILY), "SD_daily": SD_DAILY,
        "threshold_in_expected_dailies_exact": str(THRESH_IN_DAILIES),
        "threshold_in_expected_dailies": float(THRESH_IN_DAILIES)},
    "badge_share_curves_sigma_half": {
        str(p): [float(p_le(ARM_A[(DEC_SIGMA, p)], d))
                 for d in range(1, 91)] for p in P_GRID},
    "H_pair_sigma_half": {
        str(p): {"30": float(p_le(ARM_A[(DEC_SIGMA, p)], 30)),
                 "180": float(p_le(ARM_A[(DEC_SIGMA, p)], 180))}
        for p in P_GRID},
    "sigma_worlds_P_T_le_90": {
        str(sigma): {str(p): float(p_le(ARM_A[(sigma, p)],
                                        min(90, len(ARM_A[(sigma, p)]))))
                     for p in P_GRID} for sigma in SIGMA_GRID},
    "cstar_menu": {
        str(p): {"C_star": CSTAR[p],
                 "C_star_in_expected_dailies": CSTAR[p] / float(E_DAILY),
                 "P90_at_committed_10000_exact":
                     "%d/%d" % (dict(DEC90)[p].numerator,
                                dict(DEC90)[p].denominator),
                 "P90_reexpressed": {str(c): float(REEXP[p][c])
                                     for c in REEXPRESS},
                 "P90_reexpressed_exact": {str(c): "%d/%d"
                                           % (REEXP[p][c].numerator,
                                              REEXP[p][c].denominator)
                                           for c in REEXPRESS}}
        for p in P_GRID},
    "arm_s_headline": {str(p): VIEW_HEAD[p] for p in P_GRID},
    "arm_s_stability": {str(p): VIEW_STAB[p] for p in P_GRID},
    "stability_class": {"class": STAB_A[0], "null_axis": STAB_A[1],
                        "reproduces": STAB_A == RULING_A},
    "reporting_mc": [{"sigma": str(s), "p": str(p), "exact": float(x),
                      "est": e, "dev": d} for s, p, x, e, d in REP_TABLE],
    "static_badge_rows": STATIC_ROWS,
    "F2_identities": {"P_T_le_1_p1_sigma0": str(p_le(abs10, 1)),
                      "P_T_le_2_p1_sigma0": str(p_le(abs10, 2)),
                      "P_T_le_20_p1_sigma0": str(p_le(abs10, 20)),
                      "P_T_le_3_sigma_half_all_p":
                          [str(p_le(ARM_A[(DEC_SIGMA, p)], 3))
                           for p in P_GRID]},
    "drafter_comparison_never_gated": [
        {"cell": label, "drafter": ref, "re_derived": ours, "match": ok}
        for label, ref, ours, ok in DRAFT_CMP],
    "anomalies": ["A1 registration Common per-value numerator denominator "
                  "slip (9/10^5 written, 9/10^4 exact)",
                  "A2 idea: blob pin 4df5043 pre-squash (HEAD 18f3171 "
                  "authoritative, constant-identical)",
                  "A3 _daily_weights streak-luck shift excluded by the "
                  "registered base-weight (streak-0) model; "
                  "REJECT-robust direction"],
    "rng_construction_order": _RNG_LOG,
    "aux_seed_never_read": SEEDS["aux_never_read"],
    "self_checks": {"passed": _CHECKS[0], "failed": _CHECKS[1]},
}
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1)
    fh.write("\n")

if _CHECKS[1]:
    sys.exit(1)
