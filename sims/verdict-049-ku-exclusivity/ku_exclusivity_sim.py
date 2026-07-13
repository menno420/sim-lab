#!/usr/bin/env python3
"""VERDICT 049 — KU-exclusivity fork (idea-engine PROPOSAL 038, INTAKE 038).

Prices venture-lab PUBLISHING-PLAN.md §4's blanket "KDP Select: Yes" default
against the plan's own verified constants (@ venture-lab 79a1987, pinned via
the proposal block) under a per-reader-contact buy-vs-borrow mixture, over the
pre-registered 288-cell grid, in BOTH:

  Arm A — exact closed-form fractions.Fraction on ALL 288 cells, seedless;
  Arm S — seeded MC (M = 50,000 reader-contacts per (cell, arm), per-borrower
          read-through ~ Uniform(rt - 3/20, rt + 3/20), mean exactly rt).

Hermetic: stdlib-only, reads ONLY its own fixtures.json, writes results.json.
One command, no flags. Deterministic: stdout + results.json byte-identical
across two full process runs (external diff — no wall-clock in any output).

Decision (pre-registered in fixtures.json BEFORE this runner existed,
evaluated IN ORDER; the rules decide, not the drafting prediction):
  1. REJECT  iff W < 2/5 of 288 cells, stability-reproduced;
  2. APPROVE iff W >= 4/5 of 288 AND KU wins >= 4/5 of the 72 $4.99-tier
     cells, stability-reproduced;
  3. NULL    otherwise (flip axes named via per-axis win shares + b* map).

Seeds 20261289 main / 20261290 stability (half-M, must reproduce the ruling)
/ 20261291 reporting / 20261292 aux (registered, never drawn). New registry
high-water: 20261292.
"""

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- self-checks

PASSED = 0
FAILED = 0
FAIL_MSGS = []


def check(ok, label):
    global PASSED, FAILED
    if ok:
        PASSED += 1
    else:
        FAILED += 1
        FAIL_MSGS.append(label)
        print(f"SELF-CHECK FAIL: {label}")
    return ok


def F(s):
    return Fraction(s)


# ------------------------------------------------------------------- fixtures

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# CPython minor pinned and asserted (gate) — before anything else runs.
PY_PIN = tuple(FIX["runtime"]["cpython_minor"])
check(sys.implementation.name == "cpython" and sys.version_info[:2] == PY_PIN,
      f"CPython {PY_PIN} pinned (running {sys.implementation.name} "
      f"{sys.version_info[:2]})")

TITLES = [(t["name"], t["words"], t["KENP"]) for t in FIX["titles"]]
B_GRID = [F(x) for x in FIX["grids"]["b"]]
RT_GRID = [F(x) for x in FIX["grids"]["rt"]]
RATE_GRID = [F(x) for x in FIX["grids"]["rate"]]
P_GRID = [F(x) for x in FIX["grids"]["p"]]
KAPPA = F(FIX["pinned_constants"]["kappa"])
GAMMA = F(FIX["pinned_constants"]["gamma"])
KAPPA_PAIR = [F(x) for x in FIX["pinned_constants"]["kappa_sensitivity_pair"]]
GAMMA_PAIR = [F(x) for x in FIX["pinned_constants"]["gamma_sensitivity_pair"]]
WPK = FIX["pinned_constants"]["words_per_kenp"]
WPK_PAIR = FIX["pinned_constants"]["words_per_kenp_sensitivity_pair"]
SIZE_PAIR = [F(x) for x in FIX["pinned_constants"]["file_size_mb_sensitivity_pair"]]

BAND_LO = F(FIX["royalty"]["band_70"]["low"])
BAND_HI = F(FIX["royalty"]["band_70"]["high"])
MULT70 = F(FIX["royalty"]["band_70"]["multiplier"])
FEE_PER_MB = F(FIX["royalty"]["band_70"]["delivery_fee_per_mb"])
SIZE_PINNED = F(FIX["royalty"]["band_70"]["file_size_mb_pinned"])
MULT35 = F(FIX["royalty"]["band_35"]["multiplier"])

M_MAIN = FIX["arm_S"]["M_main"]
M_STAB = FIX["arm_S"]["M_stability"]
SEEDS = FIX["arm_S"]["seeds"]
Z_FW = FIX["agreement_gate"]["z_familywise"]

THIRD = Fraction(3, 400)   # Var-part of Uniform(rt-3/20, rt+3/20): E[U^2]=rt^2+3/400
RT_HALF_WIDTH = Fraction(3, 20)

TOTAL_CELLS = 288
TIER_499 = F("499/100")
TIER_CELLS = 72


def roy(p, size_mb=None):
    """Royalty per sale at list price p (exact Fraction), pinned rule."""
    if size_mb is None:
        size_mb = SIZE_PINNED
    if BAND_LO <= p <= BAND_HI:
        return MULT70 * p - FEE_PER_MB * size_mb
    return MULT35 * p


# Royalty-band anchor identities as pinned Fractions (gate, before any run).
for p_str, want in FIX["royalty"]["anchor_identities"].items():
    p_val = F(p_str[4:-1])
    check(roy(p_val) == F(want), f"royalty anchor roy({p_str[4:-1]}) == {want}")

# ------------------------------------------------------------------ Arm A

def kenp_of(words, wpk):
    # round-half-even is Python's round(); both pinned KENPs are far from .5
    # and gate-checked against the block's own 147/192 below.
    return round(Fraction(words, wpk))


check(kenp_of(27865, WPK) == 147 and TITLES[0][2] == 147,
      "KENP(ultramarine) == 147 by the kenp_rule and the fixture pin")
check(kenp_of(36434, WPK) == 192 and TITLES[1][2] == 192,
      "KENP(the-weigh-house) == 192 by the kenp_rule and the fixture pin")


def arm_values(K, b, rt, rate, p, kappa, gamma, size_mb=None):
    """Exact per-contact revenues (KU, WIDE) as Fractions."""
    beta = b / (1 + b)
    r = roy(p, size_mb)
    pr = rate * K * rt  # page-read income per borrow
    ku = (1 - beta) * ((1 - kappa) * r + kappa * pr) + beta * pr
    wide = (1 - beta) * r + beta * gamma * r
    return ku, wide


def variances(K, b, rt, rate, p, kappa, gamma):
    """Exact per-contact revenue variances (KU, WIDE) as Fractions."""
    beta = b / (1 + b)
    r = roy(p)
    rk = rate * K
    e_u2 = rt * rt + THIRD
    p_borrowish = beta + (1 - beta) * kappa
    ku_mean = (1 - beta) * ((1 - kappa) * r + kappa * rk * rt) + beta * rk * rt
    ku_e2 = p_borrowish * rk * rk * e_u2 + (1 - beta) * (1 - kappa) * r * r
    q = (1 - beta) + beta * gamma
    wide_mean = q * r
    wide_e2 = q * r * r
    return ku_e2 - ku_mean * ku_mean, wide_e2 - wide_mean * wide_mean


def build_cells(kappa=KAPPA, gamma=GAMMA, wpk=WPK, size_mb=None, rate_grid=None):
    """Full grid in the PINNED loop order: title, b, rt, rate, p."""
    cells = []
    grids = rate_grid if rate_grid is not None else RATE_GRID
    for (name, words, _pin) in TITLES:
        K = kenp_of(words, wpk)
        for b in B_GRID:
            for rt in RT_GRID:
                for rate in grids:
                    for p in P_GRID:
                        ku, wide = arm_values(K, b, rt, rate, p, kappa, gamma,
                                              size_mb)
                        cells.append({
                            "title": name, "K": K, "b": b, "rt": rt,
                            "rate": rate, "p": p, "ku": ku, "wide": wide,
                            "delta": ku - wide,
                        })
    return cells


CELLS = build_cells()
check(len(CELLS) == TOTAL_CELLS, "grid = 288 cells in pinned loop order")

W_A = sum(1 for c in CELLS if c["delta"] > 0)
W499_A = sum(1 for c in CELLS if c["p"] == TIER_499 and c["delta"] > 0)
check(sum(1 for c in CELLS if c["p"] == TIER_499) == TIER_CELLS,
      "the $4.99 tier is exactly 72 cells")

# ------------------------------------------------- exact-identity control legs

ctl1 = build_cells(kappa=Fraction(0), gamma=Fraction(0))
ok1 = all(c["delta"] == (c["b"] / (1 + c["b"])) * c["rate"] * c["K"] * c["rt"]
          for c in ctl1)
check(ok1, "control leg (kappa=0, gamma=0): Delta == beta*rate*KENP*rt "
           "EXACTLY on all 288 cells")
check(all(c["delta"] > 0 for c in ctl1),
      "control leg (kappa=0, gamma=0): KU wins every cell")

ctl2 = build_cells(kappa=Fraction(0), gamma=Fraction(0),
                   rate_grid=[Fraction(0)] * len(RATE_GRID))
check(all(c["delta"] == 0 for c in ctl2),
      "control leg (rate=0, kappa=0, gamma=0): arms identical, Delta == 0 "
      "on every cell")

# ------------------------------------------------------- monotonicity audits

def mono_ok(axis):
    """Delta nondecreasing along `axis` per cell (other coordinates fixed)."""
    groups = {}
    for c in CELLS:
        key = tuple((k, str(c[k])) for k in ("title", "b", "rt", "rate", "p")
                    if k != axis)
        groups.setdefault(key, []).append((c[axis], c["delta"]))
    for vals in groups.values():
        vals.sort(key=lambda t: t[0])
        for (_, d1), (_, d2) in zip(vals, vals[1:]):
            if d2 < d1:
                return False
    return True


check(mono_ok("rate"), "monotonicity: Delta nondecreasing in rate per cell")
check(mono_ok("rt"), "monotonicity: Delta nondecreasing in rt per cell")

# ------------------------------------------- reporting-only exact sweeps (W)

def W_of(cells):
    return sum(1 for c in cells if c["delta"] > 0)


GAMMA_SWEEP = {str(g): W_of(build_cells(gamma=g))
               for g in [GAMMA_PAIR[0], GAMMA, GAMMA_PAIR[1]]}
KAPPA_SWEEP = {str(k): W_of(build_cells(kappa=k))
               for k in [KAPPA_PAIR[0], KAPPA, KAPPA_PAIR[1]]}
WPK_SWEEP = {str(w): W_of(build_cells(wpk=w)) for w in [WPK_PAIR[0], WPK, WPK_PAIR[1]]}
SIZE_SWEEP = {str(s): W_of(build_cells(size_mb=s))
              for s in [SIZE_PAIR[0], SIZE_PINNED, SIZE_PAIR[1]]}

g_lo, g_pin, g_hi = (GAMMA_SWEEP[str(GAMMA_PAIR[0])], GAMMA_SWEEP[str(GAMMA)],
                     GAMMA_SWEEP[str(GAMMA_PAIR[1])])
check(g_lo >= g_pin >= g_hi,
      "monotonicity: W nonincreasing in gamma across its sensitivity pair")

# ---------------------------------------------------------------- Arm S (MC)

class CountingRandom(random.Random):
    """random.Random with a genuine per-instance draw counter."""

    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


def mc_ku(rng, M, beta_f, kappa_f, roy_f, rate_k_f, rt_lo_f, width_f):
    """KU arm: exactly 3 draws per contact (type, cannibalize, read-through)."""
    total = 0.0
    rnd = rng.random
    for _ in range(M):
        u1 = rnd()
        u2 = rnd()
        u3 = rnd()
        if u1 < beta_f or u2 < kappa_f:
            total += rate_k_f * (rt_lo_f + width_f * u3)
        else:
            total += roy_f
    return total / M


def mc_wide(rng, M, beta_f, gamma_f, roy_f):
    """WIDE arm: exactly 2 draws per contact (type, buy-anyway)."""
    total = 0.0
    rnd = rng.random
    for _ in range(M):
        u1 = rnd()
        u2 = rnd()
        if u1 < beta_f:
            if u2 < gamma_f:
                total += roy_f
        else:
            total += roy_f
    return total / M


def run_mc_leg(seed, M, cells, kappa, gamma, arms=("KU", "WIDE")):
    """One seeded leg over `cells` in pinned order, KU then WIDE per cell.

    Returns (per-cell dict list, draw count). Tolerances are computed (and the
    z >= 2.5 precheck asserted) by the caller BEFORE this function draws.
    """
    rng = CountingRandom(seed)
    width_f = float(2 * RT_HALF_WIDTH)
    out = []
    kappa_f = float(kappa)
    gamma_f = float(gamma)
    for c in cells:
        beta_f = float(c["b"] / (1 + c["b"]))
        roy_f = float(roy(c["p"]))
        row = {}
        if "KU" in arms:
            row["ku_s"] = mc_ku(rng, M, beta_f, kappa_f, roy_f,
                                float(c["rate"] * c["K"]),
                                float(c["rt"] - RT_HALF_WIDTH), width_f)
        if "WIDE" in arms:
            row["wide_s"] = mc_wide(rng, M, beta_f, gamma_f, roy_f)
        out.append(row)
    return out, rng.calls


# Tolerances pre-checked BEFORE any run (the P029/P030 design rule).
check(Z_FW >= 2.5, "agreement tolerances pre-checked as >= 2.5 sigma of the "
                   "registered-M estimators BEFORE any run (z_familywise = "
                   f"{Z_FW} >= 2.5)")

TOL = {}
for leg, M in (("main", M_MAIN), ("stability", M_STAB)):
    tols = []
    for c in CELLS:
        vku, vwide = variances(c["K"], c["b"], c["rt"], c["rate"], c["p"],
                               KAPPA, GAMMA)
        tols.append((Z_FW * (float(vku) / M) ** 0.5,
                     Z_FW * (float(vwide) / M) ** 0.5))
    TOL[leg] = tols
check(all(t[0] > 0 and t[1] > 0 for leg in TOL for t in TOL[leg]),
      "every per-cell tolerance computed and positive before any draw")

# Main leg (seed 20261289).
MC_MAIN, DRAWS_MAIN = run_mc_leg(SEEDS["main"], M_MAIN, CELLS, KAPPA, GAMMA)
EXP_DRAWS_MAIN = TOTAL_CELLS * M_MAIN * 5
check(DRAWS_MAIN == EXP_DRAWS_MAIN,
      f"draw-count sentinel, main leg: {DRAWS_MAIN} == 288*50000*(3+2) "
      f"= {EXP_DRAWS_MAIN}")

ok_ku = ok_wide = True
max_z_main = 0.0
for c, row, (tku, twide) in zip(CELLS, MC_MAIN, TOL["main"]):
    dku = abs(row["ku_s"] - float(c["ku"]))
    dwide = abs(row["wide_s"] - float(c["wide"]))
    max_z_main = max(max_z_main, dku / tku * Z_FW, dwide / twide * Z_FW)
    ok_ku = ok_ku and dku <= tku
    ok_wide = ok_wide and dwide <= twide
check(ok_ku, "agreement gate, main leg: |KU_S - KU_A| within tolerance on "
             "all 288 cells")
check(ok_wide, "agreement gate, main leg: |WIDE_S - WIDE_A| within tolerance "
               "on all 288 cells")

# Stability leg (seed 20261290, half-M).
MC_STAB, DRAWS_STAB = run_mc_leg(SEEDS["stability"], M_STAB, CELLS, KAPPA, GAMMA)
EXP_DRAWS_STAB = TOTAL_CELLS * M_STAB * 5
check(DRAWS_STAB == EXP_DRAWS_STAB,
      f"draw-count sentinel, stability leg: {DRAWS_STAB} == 288*25000*(3+2) "
      f"= {EXP_DRAWS_STAB}")

ok_ku = ok_wide = True
max_z_stab = 0.0
for c, row, (tku, twide) in zip(CELLS, MC_STAB, TOL["stability"]):
    dku = abs(row["ku_s"] - float(c["ku"]))
    dwide = abs(row["wide_s"] - float(c["wide"]))
    max_z_stab = max(max_z_stab, dku / tku * Z_FW, dwide / twide * Z_FW)
    ok_ku = ok_ku and dku <= tku
    ok_wide = ok_wide and dwide <= twide
check(ok_ku, "agreement gate, stability leg: |KU_S - KU_A| within tolerance "
             "on all 288 cells")
check(ok_wide, "agreement gate, stability leg: |WIDE_S - WIDE_A| within "
               "tolerance on all 288 cells")

# --------------------------------------------------------- twin evaluators

def evaluate_fraction(W, W499):
    """Evaluator 1: exact Fraction comparisons, pre-registered order."""
    share = Fraction(W, TOTAL_CELLS)
    tier = Fraction(W499, TIER_CELLS)
    if share < Fraction(2, 5):
        return "reject"
    if share >= Fraction(4, 5) and tier >= Fraction(4, 5):
        return "approve"
    return "null"


def evaluate_integer(W, W499):
    """Evaluator 2: independently-written pure-integer logic, same order."""
    if 5 * W < 2 * TOTAL_CELLS:
        return "reject"
    if 5 * W >= 4 * TOTAL_CELLS and 5 * W499 >= 4 * TIER_CELLS:
        return "approve"
    return "null"


def leg_ruling(mc_rows, label):
    W_s = sum(1 for c, r in zip(CELLS, mc_rows) if r["ku_s"] - r["wide_s"] > 0)
    W499_s = sum(1 for c, r in zip(CELLS, mc_rows)
                 if c["p"] == TIER_499 and r["ku_s"] - r["wide_s"] > 0)
    r1, r2 = evaluate_fraction(W_s, W499_s), evaluate_integer(W_s, W499_s)
    check(r1 == r2, f"twin evaluators agree on the {label} leg")
    return W_s, W499_s, r1


RULING_A_1 = evaluate_fraction(W_A, W499_A)
RULING_A_2 = evaluate_integer(W_A, W499_A)
check(RULING_A_1 == RULING_A_2, "twin evaluators agree on the exact Arm A table")
RULING = RULING_A_1

W_S_MAIN, W499_S_MAIN, RULING_S_MAIN = leg_ruling(MC_MAIN, "main MC")
W_S_STAB, W499_S_STAB, RULING_S_STAB = leg_ruling(MC_STAB, "stability MC")
check(RULING_S_MAIN == RULING, "main MC leg (seed 20261289) reproduces the "
                               "exact-arm ruling")
check(RULING_S_STAB == RULING, "STABILITY leg (seed 20261290, half-M) "
                               "reproduces the ruling")

# ----------------------------------- reporting-only legs (cannot flip; seed 20261291)

# Seeded MC spot-replication of the kappa/gamma sensitivity ENDPOINTS on the
# affected arm over the 72-cell $4.99 tier (runner design choice, disclosed in
# fixtures.json: the flagged default slice), agreement-checked at the same rule.
TIER = [c for c in CELLS if c["p"] == TIER_499]
rng_rep = CountingRandom(SEEDS["reporting"])
rep_agree = True
max_z_rep = 0.0
REP_ROWS = {}
for k_end in KAPPA_PAIR:  # ascending, pinned
    kappa_f = float(k_end)
    means = []
    for c in TIER:
        beta_f = float(c["b"] / (1 + c["b"]))
        m = mc_ku(rng_rep, M_MAIN, beta_f, kappa_f, float(roy(c["p"])),
                  float(c["rate"] * c["K"]),
                  float(c["rt"] - RT_HALF_WIDTH), float(2 * RT_HALF_WIDTH))
        ku_ex, _ = arm_values(c["K"], c["b"], c["rt"], c["rate"], c["p"],
                              k_end, GAMMA)
        vku, _ = variances(c["K"], c["b"], c["rt"], c["rate"], c["p"],
                           k_end, GAMMA)
        tol = Z_FW * (float(vku) / M_MAIN) ** 0.5
        d = abs(m - float(ku_ex))
        max_z_rep = max(max_z_rep, d / tol * Z_FW)
        rep_agree = rep_agree and d <= tol
        means.append(m)
    REP_ROWS[f"kappa={k_end}"] = means
for g_end in GAMMA_PAIR:  # ascending, pinned
    gamma_f = float(g_end)
    means = []
    for c in TIER:
        beta_f = float(c["b"] / (1 + c["b"]))
        m = mc_wide(rng_rep, M_MAIN, beta_f, gamma_f, float(roy(c["p"])))
        _, wide_ex = arm_values(c["K"], c["b"], c["rt"], c["rate"], c["p"],
                                KAPPA, g_end)
        _, vw = variances(c["K"], c["b"], c["rt"], c["rate"], c["p"],
                          KAPPA, g_end)
        tol = Z_FW * (float(vw) / M_MAIN) ** 0.5
        d = abs(m - float(wide_ex))
        max_z_rep = max(max_z_rep, d / tol * Z_FW)
        rep_agree = rep_agree and d <= tol
        means.append(m)
    REP_ROWS[f"gamma={g_end}"] = means

EXP_DRAWS_REP = TIER_CELLS * M_MAIN * 3 * 2 + TIER_CELLS * M_MAIN * 2 * 2
check(rng_rep.calls == EXP_DRAWS_REP,
      f"draw-count sentinel, reporting leg: {rng_rep.calls} == "
      f"72*50000*3*2 + 72*50000*2*2 = {EXP_DRAWS_REP}")
check(rep_agree, "reporting spot-leg (seed 20261291): MC means at the "
                 "kappa/gamma endpoints agree with the exact arms on the "
                 "72-cell $4.99 tier")

# b* crossover table: per (title, rt, rate, p), smallest swept b with Delta > 0.
BSTAR = []
for (name, words, _pin) in TITLES:
    for rt in RT_GRID:
        for rate in RATE_GRID:
            for p in P_GRID:
                row = None
                for b in B_GRID:  # ascending
                    K = kenp_of(words, WPK)
                    ku, wide = arm_values(K, b, rt, rate, p, KAPPA, GAMMA)
                    if ku - wide > 0:
                        row = str(b)
                        break
                BSTAR.append({"title": name, "rt": str(rt), "rate": str(rate),
                              "p": str(p), "b_star": row})
check(len(BSTAR) == 72, "b* crossover table has 72 rows")

# Per-axis win shares.
AXES = ("title", "b", "rt", "rate", "p")
AXIS_SHARES = {}
for ax in AXES:
    shares = {}
    for c in CELLS:
        key = str(c[ax])
        won, tot = shares.get(key, (0, 0))
        shares[key] = (won + (1 if c["delta"] > 0 else 0), tot + 1)
    AXIS_SHARES[ax] = {k: {"won": w, "of": t, "share": f"{w}/{t}"}
                       for k, (w, t) in shares.items()}

# Delta_rel distributions (exact Fractions; quartiles by median-of-halves).
def quartiles(fracs):
    s = sorted(fracs)
    n = len(s)

    def med(lst):
        m = len(lst)
        return (lst[m // 2 - 1] + lst[m // 2]) / 2 if m % 2 == 0 else lst[m // 2]

    return {"min": s[0], "q1": med(s[: n // 2]), "median": med(s),
            "q3": med(s[(n + 1) // 2:]), "max": s[-1]}


DREL_ALL = quartiles([c["ku"] / c["wide"] - 1 for c in CELLS])
DREL_TIER = {str(p): quartiles([c["ku"] / c["wide"] - 1
                                for c in CELLS if c["p"] == p])
             for p in P_GRID}

# ------------------------------------------------------------------ outputs

def fstr(x):
    return str(x)


def cell_row(c, mc, tol):
    se_ku = tol[0] / Z_FW
    se_wide = tol[1] / Z_FW
    return {
        "title": c["title"], "b": fstr(c["b"]), "rt": fstr(c["rt"]),
        "rate": fstr(c["rate"]), "p": fstr(c["p"]),
        "KU": fstr(c["ku"]), "WIDE": fstr(c["wide"]),
        "Delta": fstr(c["delta"]),
        "Delta_rel": fstr(c["ku"] / c["wide"] - 1),
        "KU_float": float(c["ku"]), "WIDE_float": float(c["wide"]),
        "KU_S": mc["ku_s"], "WIDE_S": mc["wide_s"],
        "mc_se_KU": se_ku, "mc_se_WIDE": se_wide,
        "win": c["delta"] > 0,
    }


RESULTS = {
    "identity": FIX["identity"],
    "runtime": {
        "cpython": f"{sys.version_info[0]}.{sys.version_info[1]}",
        "note": "no wall-clock anywhere in outputs — byte-identity by external diff",
    },
    "decision": {
        "ruling": RULING,
        "evaluation_order": ["REJECT", "APPROVE", "NULL"],
        "W_exact": {"W": W_A, "of": TOTAL_CELLS, "share": f"{W_A}/288",
                    "share_float": W_A / TOTAL_CELLS},
        "W_499_exact": {"W": W499_A, "of": TIER_CELLS,
                        "share": f"{W499_A}/72",
                        "share_float": W499_A / TIER_CELLS},
        "thresholds": {"REJECT": "W < 576/5 = 115.2",
                       "APPROVE": "W >= 1152/5 = 230.4 AND W_499 >= 288/5 = 57.6"},
        "mc_main": {"seed": SEEDS["main"], "M": M_MAIN, "W_S": W_S_MAIN,
                    "W499_S": W499_S_MAIN, "ruling": RULING_S_MAIN},
        "mc_stability": {"seed": SEEDS["stability"], "M": M_STAB,
                         "W_S": W_S_STAB, "W499_S": W499_S_STAB,
                         "ruling": RULING_S_STAB,
                         "reproduces": RULING_S_STAB == RULING},
        "twin_evaluators_agree": True,
    },
    "controls": {
        "kappa0_gamma0": {"identity": "Delta == beta*rate*KENP*rt exactly",
                          "ku_wins_all_288": all(c["delta"] > 0 for c in ctl1)},
        "rate0_kappa0_gamma0": {"identity": "Delta == 0 on every cell",
                                "holds": all(c["delta"] == 0 for c in ctl2)},
    },
    "agreement": {
        "z_familywise": Z_FW,
        "rule": FIX["agreement_gate"]["tolerance_rule"],
        "max_z_main": max_z_main, "max_z_stability": max_z_stab,
        "max_z_reporting": max_z_rep,
    },
    "sentinels": {
        "main": {"draws": DRAWS_MAIN, "expected": EXP_DRAWS_MAIN},
        "stability": {"draws": DRAWS_STAB, "expected": EXP_DRAWS_STAB},
        "reporting": {"draws": rng_rep.calls, "expected": EXP_DRAWS_REP},
        "aux_seed_20261292": "registered, never drawn",
    },
    "reporting_only": {
        "W_gamma_sweep": GAMMA_SWEEP,
        "W_kappa_sweep": KAPPA_SWEEP,
        "W_words_per_kenp_sweep": WPK_SWEEP,
        "W_file_size_sweep": SIZE_SWEEP,
        "per_axis_win_shares": AXIS_SHARES,
        "b_star_crossover": BSTAR,
        "delta_rel_overall": {k: fstr(v) for k, v in DREL_ALL.items()},
        "delta_rel_per_tier": {p: {k: fstr(v) for k, v in q.items()}
                               for p, q in DREL_TIER.items()},
    },
    "cells": [cell_row(c, mc, tol)
              for c, mc, tol in zip(CELLS, MC_MAIN, TOL["main"])],
}

# ------------------------------------------------------------------- report

print("VERDICT 049 — KU-exclusivity fork (PROPOSAL 038): 288-cell dual-arm sweep")
print(f"cpython {sys.version_info[0]}.{sys.version_info[1]} (pinned) · "
      f"seeds {SEEDS['main']}/{SEEDS['stability']}/{SEEDS['reporting']} "
      f"(aux {SEEDS['aux']} never drawn) · M={M_MAIN} main, {M_STAB} stability")
print()
print(f"Arm A (exact): W = {W_A}/288 = {W_A / 288:.4f} · $4.99 tier "
      f"W = {W499_A}/72 = {W499_A / 72:.4f}")
print(f"Arm S main   (seed {SEEDS['main']}): W_S = {W_S_MAIN}/288, "
      f"$4.99 W_S = {W499_S_MAIN}/72 → {RULING_S_MAIN}")
print(f"Arm S stab   (seed {SEEDS['stability']}): W_S = {W_S_STAB}/288, "
      f"$4.99 W_S = {W499_S_STAB}/72 → {RULING_S_STAB}")
print(f"max |z| main {max_z_main:.3f} / stability {max_z_stab:.3f} / "
      f"reporting {max_z_rep:.3f} (gate at z = {Z_FW})")
print()
print("Per-axis win shares (Arm A exact):")
for ax in AXES:
    parts = " · ".join(f"{k}: {v['share']}" for k, v in AXIS_SHARES[ax].items())
    print(f"  {ax:5s} {parts}")
print()
print("Sensitivity sweeps, W/288 (reporting-only, Arm A exact):")
print(f"  gamma {GAMMA_SWEEP} · kappa {KAPPA_SWEEP}")
print(f"  words-per-KENP {WPK_SWEEP} · file-size-MB {SIZE_SWEEP}")
print()
n_none = sum(1 for r in BSTAR if r["b_star"] is None)
print(f"b* crossover: {n_none}/72 rows have NO swept b at which KU wins; "
      f"full table in results.json")
print()
print(f"RULING: {RULING.upper()}  (pre-registered order REJECT -> APPROVE -> "
      f"NULL; the rules decide, not the drafting prediction)")
print()
print(f"SELF-CHECKS: {PASSED} passed, {FAILED} failed")
if FAILED:
    for m in FAIL_MSGS:
        print(f"  FAILED: {m}")

(HERE / "results.json").write_text(
    json.dumps(RESULTS, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

sys.exit(1 if FAILED else 0)
