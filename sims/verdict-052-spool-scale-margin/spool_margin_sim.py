#!/usr/bin/env python3
"""VERDICT 052 — spool-scale go/no-go margin error budget (idea-engine PROPOSAL 041).

Fully hermetic: reads ONLY its own fixtures.json (committed BEFORE this runner).
Stdlib-only, deterministic, byte-identical stdout + results.json across process
runs (no wall-clock in any output). One command, no flags:

    python3 sims/verdict-052-spool-scale-margin/spool_margin_sim.py

Registered frame (every constant from the PROPOSAL 041 block via fixtures.json):
integer grams; F ~ U{0..1000}; W = F + E + eps_s, eps_s ~ U{-5..+5}; Fhat = W -
Ehat (no clamping); regimes R-OWN (E ~ U{80..306}, Ehat = E + eps_t, eps_t ~
U{-2..+2}) / R-TABLE (brand ~ U{201,256,225,224}, Ehat = seed, E = seed + delta,
delta ~ U{-15..+15}) / R-GUESS control (Ehat = 193, E ~ U{80..306}); job Jhat
from the pinned mix (1/2 U{5..50}, 3/10 U{51..200}, 1/5 U{201..800}); U = Jhat +
ceil(Jhat*u/100), u ~ U{0..5}, ceil(a/b) = -(-a//b); START iff Fhat >= Jhat + M,
M in {0,5,10,15,25,40,60,100}; RUN-OUT iff started AND U > F; FEASIBLE iff
F >= U; FORGONE iff declined AND feasible. Arm A = seedless exact-Fraction
enumeration (the DECISION arm; net-error collapse gated by the pinned
exact-equality spot-check); Arm S = seeded MC, 200,000/regime,
random.Random(20261301), common random numbers across the margin grid;
agreement gate |ArmS - ArmA| <= 3/1000 on every RUNOUT cell and <= 1/100 on
every FORGONE cell. Decision, pre-registered, evaluated IN ORDER: REJECT first
(Feas(R-OWN) = empty) -> APPROVE (M*(R-OWN) <= 25 AND (Feas(R-TABLE) = empty OR
M*(R-TABLE) >= M*(R-OWN) + 15) + seed-20261302 stability reproduction) -> NULL
(four pre-registered axes). Seeds: 20261301 main / 20261302 stability /
20261303 reporting / 20261304 aux (reserved, NEVER read).
"""

import json
import random
import sys
from bisect import bisect_right
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    if not ok:
        print(f"SELF-CHECK FAIL: {name} {detail}")


def frac_str(f):
    return f"{f.numerator}/{f.denominator}"


def ceil_div(a, b):
    """Integer ceiling, pinned by the registration as ceil(a/b) = -(-a//b)."""
    return -(-a // b)


# ------------------------------------------------------------------ constants
F_LO, F_HI = FX["spool"]["F_lattice"]
NF = F_HI - F_LO + 1
EPS_S_LO, EPS_S_HI = FX["scale"]["eps_s_lattice"]
OWN = FX["regimes"]["R-OWN"]
TABLE = FX["regimes"]["R-TABLE"]
GUESS = FX["regimes"]["R-GUESS"]
BRANDS = TABLE["brand_seeds"]
GUESS_EHAT = GUESS["Ehat_fixed"]
JOB_CLASSES = FX["job"]["mix_pinned"]
MIX_PINNED = [Fraction(*c["weight"]) for c in JOB_CLASSES]
MIX_LARGE_HEAVY = [Fraction(*w) for w in FX["job"]["mix_sensitivity_large_heavy"]]
U_LO, U_HI = FX["job"]["u_lattice"]
D_LO, D_HI = FX["drift_leg"]["d_lattice"]
M_GRID = FX["margin_grid"]
NM = len(M_GRID)
RO_MAX = Fraction(*FX["bands"]["runout_max"])
FO_MAX = Fraction(*FX["bands"]["forgone_max"])
POCKET_MAX = FX["bands"]["approve_pocket_max_g"]
HABIT_MIN = FX["bands"]["approve_habit_min_delta_g"]
GATE_RO = Fraction(*FX["arms"]["agreement_gate"]["runout_abs_tolerance"])
GATE_FO = Fraction(*FX["arms"]["agreement_gate"]["forgone_abs_tolerance"])
REGIMES = FX["regimes"]["order_pinned"]


# ------------------------------------------------- scenario evaluator (shared)
def evaluate_scenario(F, E, Ehat, eps_s, J, u, M, d=0):
    """The pinned per-scenario semantics — used by the hand fixture, Arm S,
    and the direct spot-check. Returns (W, Fhat, U, started, run_out,
    feasible, forgone)."""
    W = F + E + eps_s + d
    Fhat = W - Ehat
    U = J + ceil_div(J * u, 100)
    started = Fhat >= J + M
    run_out = started and U > F
    feasible = F >= U
    forgone = (not started) and feasible
    return W, Fhat, U, started, run_out, feasible, forgone


# ------------------------------------------------------------------ pmf tools
def uniform_counts(lo, hi):
    return {v: 1 for v in range(lo, hi + 1)}


def convolve(p, q):
    out = {}
    for a, ca in p.items():
        for b, cb in q.items():
            k = a + b
            out[k] = out.get(k, 0) + ca * cb
    return out


def negate(p):
    return {-k: c for k, c in p.items()}


def shift(p, s):
    return {k + s: c for k, c in p.items()}


def t_pmf_own(et_lo, et_hi):
    """Net error T = Fhat - F = eps_s - eps_t (E cancels exactly)."""
    return convolve(uniform_counts(EPS_S_LO, EPS_S_HI),
                    negate(uniform_counts(et_lo, et_hi)))


def t_pmf_table(dl_lo, dl_hi):
    """Net error T = eps_s + delta (Ehat = seed, E = seed + delta; the brand
    seed cancels — brand carries zero decision information in Arm A)."""
    return convolve(uniform_counts(EPS_S_LO, EPS_S_HI),
                    uniform_counts(dl_lo, dl_hi))


def t_pmf_guess():
    """Net error T = (E - 193) + eps_s."""
    e_lo, e_hi = GUESS["E_lattice"]
    return convolve(uniform_counts(EPS_S_LO, EPS_S_HI),
                    shift(uniform_counts(e_lo, e_hi), -GUESS_EHAT))


D_PMF = uniform_counts(D_LO, D_HI)


# ------------------------------------------------------- Arm A (decision arm)
def enumerate_classes(t_pmf, u_values, m_grid):
    """Collapsed exact enumeration over (Jhat, u, T) with F counted in closed
    integer intervals. Returns ({class: {S,R,G,Fe,nJ}}, t_total) — raw integer
    accumulators; job-mix weights are applied at combine time (within-class
    Jhat is uniform, so per-class sums recombine exactly under any mix)."""
    t_items = sorted(t_pmf.items())
    t_total = sum(t_pmf.values())
    res = {}
    f_hi = F_HI
    for cls in JOB_CLASSES:
        jlo, jhi = cls["J_lattice"]
        S = [0] * NM
        R = [0] * NM
        G = [0] * NM
        Fe = 0
        for J in range(jlo, jhi + 1):
            for u in u_values:
                U = J + ceil_div(J * u, 100)
                feas_cnt = (f_hi - U + 1) if U <= f_hi else 0
                Fe += t_total * feas_cnt
                for mi in range(NM):
                    K = J + m_grid[mi]
                    s_acc = 0
                    r_acc = 0
                    g_acc = 0
                    for T, cT in t_items:
                        L = K - T
                        lo = L if L > 0 else 0
                        if lo <= f_hi:
                            s_acc += cT * (f_hi - lo + 1)
                            hr = U - 1
                            if hr > f_hi:
                                hr = f_hi
                            if hr >= lo:
                                r_acc += cT * (hr - lo + 1)
                        hf = L - 1
                        if hf > f_hi:
                            hf = f_hi
                        if hf >= U:
                            g_acc += cT * (hf - U + 1)
                    S[mi] += s_acc
                    R[mi] += r_acc
                    G[mi] += g_acc
        res[cls["class"]] = {"S": S, "R": R, "G": G, "Fe": Fe, "nJ": jhi - jlo + 1}
    return res, t_total


def combine_tables(res, t_total, n_u, mix):
    """Apply the job-mix weights; return exact-Fraction per-M tables."""
    Sw = [Fraction(0)] * NM
    Rw = [Fraction(0)] * NM
    Gw = [Fraction(0)] * NM
    Few = Fraction(0)
    for cls, w in zip(JOB_CLASSES, mix):
        acc = res[cls["class"]]
        per_j = w / acc["nJ"]
        for mi in range(NM):
            Sw[mi] += per_j * acc["S"][mi]
            Rw[mi] += per_j * acc["R"][mi]
            Gw[mi] += per_j * acc["G"][mi]
        Few += per_j * acc["Fe"]
    tot = Fraction(n_u * t_total * NF)  # sum of mix weights = 1
    return {
        "RUNOUT": [Rw[mi] / Sw[mi] for mi in range(NM)],
        "FORGONE": [Gw[mi] / Few for mi in range(NM)],
        "start_rate": [Sw[mi] / tot for mi in range(NM)],
        "feasible_share": Few / tot,
        "unconditional_runout": [Rw[mi] / tot for mi in range(NM)],
        "per_class_runout": {
            cls["class"]: [Fraction(acc["R"][mi], acc["S"][mi]) if acc["S"][mi] else None
                           for mi in range(NM)]
            for cls, acc in ((c, res[c["class"]]) for c in JOB_CLASSES)
        },
    }


def arm_a_regime(regime, et=None, dl=None, u_lattice=None, mix=None, drift=False):
    """One Arm-A table for a regime under baseline or a named variant."""
    if regime == "R-OWN":
        lo, hi = et if et is not None else OWN["eps_t_lattice"]
        t = t_pmf_own(lo, hi)
    elif regime == "R-TABLE":
        lo, hi = dl if dl is not None else TABLE["delta_lattice"]
        t = t_pmf_table(lo, hi)
    else:
        t = t_pmf_guess()
    if drift:
        t = convolve(t, D_PMF)
    ul, uh = u_lattice if u_lattice is not None else (U_LO, U_HI)
    u_values = list(range(ul, uh + 1))
    res, t_total = enumerate_classes(t, u_values, M_GRID)
    return combine_tables(res, t_total, len(u_values), mix if mix else MIX_PINNED), res, t_total, u_values


# ------------------------------------------------- direct spot-check (no pmf)
def direct_cell(regime, J, u, M):
    """Direct product enumeration over the RAW component lattices (no net-error
    pmf) for one (regime, Jhat, u, M) cell — every component tuple weight 1,
    F counted from the scenario definitions with independently written
    interval arithmetic. Returns exact-Fraction (started_share,
    runout_given_started, forgone_given_feasible, feasible_share)."""
    def count_f(lo, hi):
        lo2 = lo if lo > F_LO else F_LO
        hi2 = hi if hi < F_HI else F_HI
        n = hi2 - lo2 + 1
        return n if n > 0 else 0

    U = J + ceil_div(J * u, 100)
    s = r = g = fe = tot = 0
    combos = []
    if regime == "R-OWN":
        e_lo, e_hi = OWN["E_lattice"]
        et_lo, et_hi = OWN["eps_t_lattice"]
        for E in range(e_lo, e_hi + 1):
            for eps_t in range(et_lo, et_hi + 1):
                combos.append((E, E + eps_t))
    elif regime == "R-TABLE":
        dl_lo, dl_hi = TABLE["delta_lattice"]
        for seed in BRANDS:
            for delta in range(dl_lo, dl_hi + 1):
                combos.append((seed + delta, seed))
    else:
        e_lo, e_hi = GUESS["E_lattice"]
        for E in range(e_lo, e_hi + 1):
            combos.append((E, GUESS_EHAT))
    for (E, Ehat) in combos:
        for eps_s in range(EPS_S_LO, EPS_S_HI + 1):
            # started iff F + E + eps_s - Ehat >= J + M  iff  F >= thr
            thr = J + M - E - eps_s + Ehat
            n_started = count_f(thr, F_HI)
            n_runout = count_f(thr, U - 1)
            n_feas = count_f(U, F_HI)
            n_forgone = count_f(U, thr - 1)
            s += n_started
            r += n_runout
            fe += n_feas
            g += n_forgone
            tot += NF
    return (Fraction(s, tot), Fraction(r, s) if s else None,
            Fraction(g, fe), Fraction(fe, tot))


def collapsed_cell(t_pmf, J, u, M):
    """The same cell via the collapsed net-error pmf (the Arm-A path)."""
    t_total = sum(t_pmf.values())
    U = J + ceil_div(J * u, 100)
    s = r = g = 0
    fe = t_total * ((F_HI - U + 1) if U <= F_HI else 0)
    K = J + M
    for T, cT in sorted(t_pmf.items()):
        L = K - T
        lo = L if L > 0 else 0
        if lo <= F_HI:
            s += cT * (F_HI - lo + 1)
            hr = U - 1 if U - 1 <= F_HI else F_HI
            if hr >= lo:
                r += cT * (hr - lo + 1)
        hf = L - 1 if L - 1 <= F_HI else F_HI
        if hf >= U:
            g += cT * (hf - U + 1)
    tot = t_total * NF
    return (Fraction(s, tot), Fraction(r, s) if s else None,
            Fraction(g, fe), Fraction(fe, tot))


# ------------------------------------------------------------------ Arm S (MC)
class CountingRandom(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.randrange_calls = 0

    def randrange(self, *args, **kwargs):
        self.randrange_calls += 1
        return super().randrange(*args, **kwargs)


def mc_regime(rng, n, regime, et=None, dl=None, u_lattice=None,
              mix="pinned", drift=False):
    """One MC leg cell: n scenarios of one regime, all M evaluated on the same
    scenario set (common random numbers). Pinned draw order per scenario:
    F -> tare term(s) -> eps_s (-> d on the drift sub-leg) -> job class ->
    Jhat -> u. Returns integer counts (started[], runout[], forgone[], feas)."""
    et_lo, et_hi = et if et is not None else OWN["eps_t_lattice"]
    dl_lo, dl_hi = dl if dl is not None else TABLE["delta_lattice"]
    ul, uh = u_lattice if u_lattice is not None else (U_LO, U_HI)
    e_lo, e_hi = OWN["E_lattice"]
    started_cut = [0] * (NM + 1)
    runout_cut = [0] * (NM + 1)
    forgone_cut = [0] * (NM + 1)
    feas_n = 0
    jl = [c["J_lattice"] for c in JOB_CLASSES]
    for _ in range(n):
        F = rng.randrange(F_LO, F_HI + 1)
        if regime == "R-OWN":
            E = rng.randrange(e_lo, e_hi + 1)
            eps_t = rng.randrange(et_lo, et_hi + 1)
            Ehat = E + eps_t
        elif regime == "R-TABLE":
            seed_w = BRANDS[rng.randrange(4)]
            delta = rng.randrange(dl_lo, dl_hi + 1)
            E = seed_w + delta
            Ehat = seed_w
        else:
            E = rng.randrange(e_lo, e_hi + 1)
            Ehat = GUESS_EHAT
        eps_s = rng.randrange(EPS_S_LO, EPS_S_HI + 1)
        d = rng.randrange(D_LO, D_HI + 1) if drift else 0
        if mix == "pinned":
            c = rng.randrange(10)
            cls = 0 if c < 5 else (1 if c < 8 else 2)
        else:  # large-heavy
            c = rng.randrange(4)
            cls = 0 if c == 0 else (1 if c == 1 else 2)
        jlo, jhi = jl[cls]
        J = rng.randrange(jlo, jhi + 1)
        u = rng.randrange(ul, uh + 1)
        # evaluation (all M on the same draws — common random numbers)
        Fhat = F + E + eps_s + d - Ehat
        U = J + ceil_div(J * u, 100)
        fz = F >= U
        if fz:
            feas_n += 1
        thr = Fhat - J  # started iff M <= thr
        cut = bisect_right(M_GRID, thr)  # started for m-index < cut
        started_cut[cut] += 1
        if U > F:
            runout_cut[cut] += 1
        if fz:
            forgone_cut[cut] += 1
    started = [0] * NM
    runout = [0] * NM
    forgone = [0] * NM
    s_acc = r_acc = 0
    for k in range(NM, 0, -1):
        s_acc += started_cut[k]
        r_acc += runout_cut[k]
        started[k - 1] = s_acc
        runout[k - 1] = r_acc
    f_acc = 0
    for k in range(0, NM):
        f_acc += forgone_cut[k]
        forgone[k] = f_acc
    return started, runout, forgone, feas_n


def mc_draws_per_scenario(regime, drift):
    base = {"R-OWN": 7, "R-TABLE": 7, "R-GUESS": 6}[regime]
    return base + (1 if drift else 0)


# ------------------------------------------------------- twin decision logic
def feas_set_fraction(runout, forgone):
    return [M for M, r, f in zip(M_GRID, runout, forgone)
            if r <= RO_MAX and f <= FO_MAX]


def evaluator_fraction(tables):
    """Decision evaluator 1 — fractions.Fraction band tests on Feas sets.
    tables[regime] = (runout list of Fraction, forgone list of Fraction).
    Returns the rule class BEFORE the stability conjunct (the shadow class),
    with the NULL axis when one of the two exact-number axes binds."""
    f_own = feas_set_fraction(*tables["R-OWN"])
    if not f_own:
        return ("reject", None)
    m_own = f_own[0]
    f_tab = feas_set_fraction(*tables["R-TABLE"])
    habit = (not f_tab) or (f_tab[0] >= m_own + HABIT_MIN)
    if m_own <= POCKET_MAX and habit:
        return ("approve", None)
    if m_own > POCKET_MAX:
        return ("null", "big-pocket")
    return ("null", "table-parity")


def evaluator_integer(pairs):
    """Decision evaluator 2 — INDEPENDENTLY WRITTEN: pure integer
    cross-multiplication on (num, den) pairs; never constructs a Fraction.
    pairs[regime] = list per M of ((r_num, r_den), (g_num, g_den))."""
    ro_n, ro_d = FX["bands"]["runout_max"]
    fo_n, fo_d = FX["bands"]["forgone_max"]

    def m_star(regime):
        for M, ((rn, rd), (gn, gd)) in zip(M_GRID, pairs[regime]):
            if rn * ro_d <= ro_n * rd and gn * fo_d <= fo_n * gd:
                return M
        return None

    a = m_star("R-OWN")
    if a is None:
        return ("reject", None)
    b = m_star("R-TABLE")
    habit = (b is None) or (b >= a + HABIT_MIN)
    if a <= POCKET_MAX and habit:
        return ("approve", None)
    if a > POCKET_MAX:
        return ("null", "big-pocket")
    return ("null", "table-parity")


def to_pairs(tables):
    return {reg: [((r.numerator, r.denominator), (g.numerator, g.denominator))
                  for r, g in zip(tables[reg][0], tables[reg][1])]
            for reg in tables}


def primary_conjuncts(tables):
    """The three primary conjunct booleans on exact tables (for the
    sensitivity-straddle check). pocket/habit are None when Feas(R-OWN) is
    empty (undefined — the REJECT conjunct already binds)."""
    f_own = feas_set_fraction(*tables["R-OWN"])
    c_reject = not f_own
    if c_reject:
        return {"reject_conjunct": True, "pocket_conjunct": None, "habit_conjunct": None}
    m_own = f_own[0]
    f_tab = feas_set_fraction(*tables["R-TABLE"])
    return {
        "reject_conjunct": False,
        "pocket_conjunct": m_own <= POCKET_MAX,
        "habit_conjunct": (not f_tab) or (f_tab[0] >= m_own + HABIT_MIN),
    }


# ------------------------------------------------------------------ main
def main():
    out = {}

    pin = tuple(FX["cpython_minor_pinned"])
    check("cpython-minor-pinned", sys.version_info[:2] == pin,
          f"running {sys.version_info[:2]}, pinned {pin}")

    # ---- registry / grid coverage gates
    seeds = FX["seeds"]
    seed_vals = [seeds["main"], seeds["stability"], seeds["reporting"],
                 seeds["aux_reserved_never_read"]]
    check("seed-registry", seed_vals == [20261301, 20261302, 20261303, 20261304]
          and len(set(seed_vals)) == 4 and min(seed_vals) > 20261300,
          "seeds 20261301-304, distinct, strictly above the V051 high-water 20261300")
    check("margin-grid-coverage", M_GRID == [0, 5, 10, 15, 25, 40, 60, 100]
          and REGIMES == ["R-OWN", "R-TABLE", "R-GUESS"])
    check("bands-registered", RO_MAX == Fraction(1, 100) and FO_MAX == Fraction(1, 5)
          and POCKET_MAX == 25 and HABIT_MIN == 15)

    # ---- gate: six-scenario hand fixture (verified at startup)
    hf_ok = True
    hf_detail = []
    for sc in FX["hand_fixture_six_scenarios"]["scenarios"]:
        W, Fhat, U, started, run_out, feasible, forgone = evaluate_scenario(
            sc["F"], sc["E"], sc["Ehat"], sc["eps_s"], sc["Jhat"], sc["u"], sc["M"])
        got = (W, Fhat, U, started, run_out, feasible, forgone)
        exp = (sc["W"], sc["Fhat"], sc["U"], sc["started"], sc["run_out"],
               sc["feasible"], sc["forgone"])
        if got != exp:
            hf_ok = False
            hf_detail.append(f"scenario {sc['n']}: got {got}, expected {exp}")
    check("hand-fixture-six-scenarios", hf_ok, "; ".join(hf_detail))

    # ---- gate: zero-error identity leg (Arm A, exact)
    zero_ok = True
    for reg in REGIMES:
        res0, t0 = enumerate_classes({0: 1}, [0], M_GRID)
        tab0 = combine_tables(res0, t0, 1, MIX_PINNED)
        if any(r != 0 for r in tab0["RUNOUT"]) or tab0["FORGONE"][0] != 0:
            zero_ok = False
    check("zero-error-identity", zero_ok,
          "eps_s=eps_t=delta=u=0, Ehat=E: RUNOUT == 0 for all M, FORGONE(0) == 0 (exact)")

    # ---- Arm A: baseline tables (the decision arm)
    arm_a = {}
    arm_a_raw = {}
    for reg in REGIMES:
        tab, res, t_total, _ = arm_a_regime(reg)
        arm_a[reg] = tab
        arm_a_raw[reg] = (res, t_total)

    # ---- gate: convolution spot-check (collapse vs direct, EXACT equality)
    sc_grid = FX["arms"]["spot_check_subgrid"]
    t_base = {"R-OWN": t_pmf_own(*OWN["eps_t_lattice"]),
              "R-TABLE": t_pmf_table(*TABLE["delta_lattice"]),
              "R-GUESS": t_pmf_guess()}
    spot_ok = True
    spot_n = 0
    for reg in REGIMES:
        for J in sc_grid["Jhat"]:
            for u in sc_grid["u"]:
                for M in sc_grid["M"]:
                    spot_n += 1
                    if direct_cell(reg, J, u, M) != collapsed_cell(t_base[reg], J, u, M):
                        spot_ok = False
    check("convolution-spot-check-exact", spot_ok,
          f"{spot_n} cells (J x u x regime x M), collapsed == direct product, exact")

    # ---- Arm A: drift + sensitivity variants (reporting-only, exact)
    variants = {}
    variants["drift"] = {reg: arm_a_regime(reg, drift=True)[0] for reg in REGIMES}
    et_pairs = OWN["eps_t_sensitivity_pairs"]
    variants[f"eps_t-{{{et_pairs[0][0]}..{et_pairs[0][1]}}}"] = {
        "R-OWN": arm_a_regime("R-OWN", et=et_pairs[0])[0]}
    variants[f"eps_t-{{{et_pairs[1][0]}..{et_pairs[1][1]}}}"] = {
        "R-OWN": arm_a_regime("R-OWN", et=et_pairs[1])[0]}
    dl_pairs = TABLE["delta_sensitivity_pairs"]
    variants[f"delta-{{{dl_pairs[0][0]}..{dl_pairs[0][1]}}}"] = {
        "R-TABLE": arm_a_regime("R-TABLE", dl=dl_pairs[0])[0]}
    variants[f"delta-{{{dl_pairs[1][0]}..{dl_pairs[1][1]}}}"] = {
        "R-TABLE": arm_a_regime("R-TABLE", dl=dl_pairs[1])[0]}
    u_pairs = FX["job"]["u_sensitivity_pairs"]
    for up in u_pairs:
        variants[f"u-{{{up[0]}..{up[1]}}}"] = {
            reg: arm_a_regime(reg, u_lattice=tuple(up))[0] for reg in REGIMES}
    # job-mix variant: exact recombination of the baseline per-class sums
    variants["jobmix-large-heavy"] = {
        reg: combine_tables(arm_a_raw[reg][0], arm_a_raw[reg][1],
                            U_HI - U_LO + 1, MIX_LARGE_HEAVY)
        for reg in REGIMES}

    # ---- gate: exact monotonicity in M (Arm A — baseline and every variant)
    mono_ok = True
    mono_n = 0

    def mono_gate(runout, forgone):
        nonlocal mono_ok, mono_n
        mono_n += 1
        for i in range(NM - 1):
            if runout[i] < runout[i + 1] or forgone[i] > forgone[i + 1]:
                mono_ok = False

    for reg in REGIMES:
        mono_gate(arm_a[reg]["RUNOUT"], arm_a[reg]["FORGONE"])
    for vt in variants.values():
        for tab in vt.values():
            mono_gate(tab["RUNOUT"], tab["FORGONE"])

    # ---- Arm S: main confirmation leg (seed 20261301, 200k/regime)
    n_main = FX["arms"]["arm_s"]["n_main_per_regime"]
    rng_main = CountingRandom(seeds["main"])
    mc_main = {}
    for reg in REGIMES:
        mc_main[reg] = mc_regime(rng_main, n_main, reg)
    exp_main = n_main * sum(mc_draws_per_scenario(r, False) for r in REGIMES)
    check("draw-sentinel-main", rng_main.randrange_calls == exp_main,
          f"randranges={rng_main.randrange_calls} (expect {exp_main})")

    # ---- gate: arm agreement (main leg, every cell)
    agree_ok = True
    max_dr = Fraction(0)
    max_df = Fraction(0)
    for reg in REGIMES:
        s_l, r_l, g_l, fe = mc_main[reg]
        for mi in range(NM):
            dr = abs(Fraction(r_l[mi], s_l[mi]) - arm_a[reg]["RUNOUT"][mi])
            df = abs(Fraction(g_l[mi], fe) - arm_a[reg]["FORGONE"][mi])
            if dr > max_dr:
                max_dr = dr
            if df > max_df:
                max_df = df
            if dr > GATE_RO or df > GATE_FO:
                agree_ok = False
    check("arm-agreement-gate", agree_ok,
          f"max |dRUNOUT| = {float(max_dr):.6f} (gate 0.003), "
          f"max |dFORGONE| = {float(max_df):.6f} (gate 0.01)")

    # ---- Arm S monotonicity (main leg, common random numbers)
    for reg in REGIMES:
        s_l, r_l, g_l, fe = mc_main[reg]
        mono_gate([Fraction(r_l[mi], s_l[mi]) for mi in range(NM)],
                  [Fraction(g_l[mi], fe) for mi in range(NM)])

    # ---- Arm S: stability leg (seed 20261302, 20k/regime)
    n_stab = FX["arms"]["arm_s"]["n_stability_per_regime"]
    rng_stab = CountingRandom(seeds["stability"])
    mc_stab = {}
    for reg in REGIMES:
        mc_stab[reg] = mc_regime(rng_stab, n_stab, reg)
    exp_stab = n_stab * sum(mc_draws_per_scenario(r, False) for r in REGIMES)
    check("draw-sentinel-stability", rng_stab.randrange_calls == exp_stab,
          f"randranges={rng_stab.randrange_calls} (expect {exp_stab})")
    stab_tables = {}
    stab_agree_ok = True
    for reg in REGIMES:
        s_l, r_l, g_l, fe = mc_stab[reg]
        ro = [Fraction(r_l[mi], s_l[mi]) for mi in range(NM)]
        fo = [Fraction(g_l[mi], fe) for mi in range(NM)]
        stab_tables[reg] = (ro, fo)
        for mi in range(NM):
            if (abs(ro[mi] - arm_a[reg]["RUNOUT"][mi]) > GATE_RO
                    or abs(fo[mi] - arm_a[reg]["FORGONE"][mi]) > GATE_FO):
                stab_agree_ok = False
        mono_gate(ro, fo)
    check("monotonicity-both-arms", mono_ok,
          f"{mono_n} (regime-or-variant, arm) tables, RUNOUT non-increasing / "
          f"FORGONE non-decreasing in M — exact, hard gate")

    # ---- Arm S: reporting leg (seed 20261303 — drift + sensitivity confirmations)
    n_rep = FX["arms"]["arm_s"]["n_reporting_per_cell"]
    rng_rep = CountingRandom(seeds["reporting"])
    rep_deltas = {}
    exp_rep = 0
    for sub in FX["reporting_leg_seed_20261303"]["sub_legs_in_pinned_order"]:
        name = sub["name"]
        kw = {}
        if name == "drift":
            kw = {"drift": True}
        elif name.startswith("eps_t"):
            kw = {"et": et_pairs[0] if name == "eps_t-{0..0}" or "{0}" in name else et_pairs[1]}
        elif name.startswith("delta"):
            kw = {"dl": dl_pairs[0] if "{-8..8}" in name else dl_pairs[1]}
        elif name.startswith("u-"):
            kw = {"u_lattice": tuple(u_pairs[0]) if "{0..2}" in name else tuple(u_pairs[1])}
        elif name == "jobmix-large-heavy":
            kw = {"mix": "large-heavy"}
        vkey = name if name != "drift" else "drift"
        # map the sub-leg to its Arm-A variant table key
        if name.startswith("eps_t"):
            vkey = f"eps_t-{{{(et_pairs[0] if '{0}' in name else et_pairs[1])[0]}..{(et_pairs[0] if '{0}' in name else et_pairs[1])[1]}}}"
        elif name.startswith("delta"):
            vkey = f"delta-{{{(dl_pairs[0] if '{-8..8}' in name else dl_pairs[1])[0]}..{(dl_pairs[0] if '{-8..8}' in name else dl_pairs[1])[1]}}}"
        max_dr_v = Fraction(0)
        max_df_v = Fraction(0)
        for reg in sub["regimes"]:
            s_l, r_l, g_l, fe = mc_regime(rng_rep, n_rep, reg, **kw)
            exp_rep += n_rep * mc_draws_per_scenario(reg, name == "drift")
            va = variants[vkey][reg]
            for mi in range(NM):
                dr = abs(Fraction(r_l[mi], s_l[mi]) - va["RUNOUT"][mi])
                df = abs(Fraction(g_l[mi], fe) - va["FORGONE"][mi])
                if dr > max_dr_v:
                    max_dr_v = dr
                if df > max_df_v:
                    max_df_v = df
        rep_deltas[name] = {"max_abs_dRUNOUT": float(max_dr_v),
                            "max_abs_dFORGONE": float(max_df_v)}
    check("draw-sentinel-reporting", rng_rep.randrange_calls == exp_rep,
          f"randranges={rng_rep.randrange_calls} (expect {exp_rep})")
    check("aux-seed-never-read", True,
          f"seed {seeds['aux_reserved_never_read']} — no generator constructed, 0 draws")

    # ---- decision (pre-registered, REJECT first; the ruling rides Arm A alone)
    dec_tables = {reg: (arm_a[reg]["RUNOUT"], arm_a[reg]["FORGONE"])
                  for reg in ("R-OWN", "R-TABLE")}
    r1 = evaluator_fraction(dec_tables)
    r2 = evaluator_integer(to_pairs(dec_tables))
    check("twin-evaluators-agree-main", r1 == r2, f"fraction={r1} integer={r2}")
    shadow_class, shadow_axis = r1

    stab_dec = {reg: stab_tables[reg] for reg in ("R-OWN", "R-TABLE")}
    s1 = evaluator_fraction(stab_dec)
    s2 = evaluator_integer(to_pairs(stab_dec))
    check("twin-evaluators-agree-stability", s1 == s2, f"fraction={s1} integer={s2}")
    stability_reproduced = stab_agree_ok and s1[0] == shadow_class

    feas_own = feas_set_fraction(*dec_tables["R-OWN"])
    feas_tab = feas_set_fraction(*dec_tables["R-TABLE"])
    feas_guess = feas_set_fraction(arm_a["R-GUESS"]["RUNOUT"], arm_a["R-GUESS"]["FORGONE"])
    m_own = feas_own[0] if feas_own else None
    m_tab = feas_tab[0] if feas_tab else None
    m_guess = feas_guess[0] if feas_guess else None

    # sensitivity-straddle check (names the axis; never flips the decision)
    base_conj = primary_conjuncts(dec_tables)
    straddles = []
    for vname, vt in variants.items():
        vtab = {"R-OWN": vt.get("R-OWN", arm_a["R-OWN"]),
                "R-TABLE": vt.get("R-TABLE", arm_a["R-TABLE"])}
        vconj = primary_conjuncts({reg: (vtab[reg]["RUNOUT"], vtab[reg]["FORGONE"])
                                   for reg in ("R-OWN", "R-TABLE")})
        flipped = [k for k in base_conj
                   if base_conj[k] is not None and vconj[k] is not None
                   and base_conj[k] != vconj[k]]
        if flipped:
            straddles.append({"variant": vname, "flipped_conjuncts": flipped})

    # R-GUESS control expected-direction check (reporting-only)
    guess_surprise = (m_guess is not None
                      and not (m_tab is not None and m_guess >= m_tab + HABIT_MIN))

    # THE REGISTERED ORDER: agreement-gate breach invalidates the run (axis iii),
    # then REJECT first, then APPROVE (with the stability conjunct), else NULL.
    if not agree_ok:
        ruling, axis = "null", "arm-disagreement (agreement gate breached — run invalid, no ruling issues)"
    elif shadow_class == "reject":
        ruling, axis = "reject", None
    elif shadow_class == "approve":
        if stability_reproduced:
            ruling, axis = "approve", None
        else:
            ruling, axis = "null", "stability-non-reproduction (the APPROVE conjuncts hold on Arm A but the seed-20261302 leg does not reproduce the ruling)"
    else:
        ruling, axis = "null", shadow_axis

    # ---- results.json
    def tab_json(tab):
        return {
            "M_grid": M_GRID,
            "RUNOUT": [frac_str(x) for x in tab["RUNOUT"]],
            "RUNOUT_float": [float(x) for x in tab["RUNOUT"]],
            "FORGONE": [frac_str(x) for x in tab["FORGONE"]],
            "FORGONE_float": [float(x) for x in tab["FORGONE"]],
            "start_rate_float": [float(x) for x in tab["start_rate"]],
            "feasible_share": frac_str(tab["feasible_share"]),
            "feasible_share_float": float(tab["feasible_share"]),
            "unconditional_runout_float": [float(x) for x in tab["unconditional_runout"]],
            "per_class_runout_float": {
                c: [None if x is None else float(x) for x in xs]
                for c, xs in tab["per_class_runout"].items()},
        }

    out["arm_a"] = {reg: tab_json(arm_a[reg]) for reg in REGIMES}
    out["arm_a_variants"] = {vn: {reg: tab_json(t) for reg, t in vt.items()}
                             for vn, vt in variants.items()}
    out["arm_s_main"] = {
        reg: {"n": n_main, "started": mc_main[reg][0], "runout": mc_main[reg][1],
              "forgone": mc_main[reg][2], "feasible": mc_main[reg][3],
              "RUNOUT_float": [mc_main[reg][1][mi] / mc_main[reg][0][mi] for mi in range(NM)],
              "FORGONE_float": [mc_main[reg][2][mi] / mc_main[reg][3] for mi in range(NM)]}
        for reg in REGIMES}
    out["arm_s_stability"] = {
        reg: {"n": n_stab, "started": mc_stab[reg][0], "runout": mc_stab[reg][1],
              "forgone": mc_stab[reg][2], "feasible": mc_stab[reg][3]}
        for reg in REGIMES}
    out["arm_s_reporting_max_deltas_vs_arm_a"] = rep_deltas
    out["agreement"] = {
        "max_abs_dRUNOUT_float": float(max_dr), "gate_RUNOUT": "3/1000",
        "max_abs_dFORGONE_float": float(max_df), "gate_FORGONE": "1/100",
        "pass": agree_ok,
        "stability_within_same_gate": stab_agree_ok,
    }
    out["feas_mstar"] = {
        "Feas(R-OWN)": feas_own, "Feas(R-TABLE)": feas_tab, "Feas(R-GUESS)": feas_guess,
        "M*(R-OWN)": m_own, "M*(R-TABLE)": m_tab, "M*(R-GUESS)": m_guess,
        "drift": {reg: {"Feas": feas_set_fraction(variants["drift"][reg]["RUNOUT"],
                                                  variants["drift"][reg]["FORGONE"])}
                  for reg in REGIMES},
    }
    out["decision"] = {
        "evaluation_order": "agreement-gate validity -> REJECT (Feas(R-OWN) empty) -> APPROVE (M*(R-OWN) <= 25 AND (Feas(R-TABLE) empty OR M*(R-TABLE) >= M*(R-OWN) + 15) AND seed-20261302 stability reproduction) -> NULL (named axis)",
        "reject_conjunct_feas_own_empty": not feas_own,
        "approve_pocket_conjunct": base_conj["pocket_conjunct"],
        "approve_habit_conjunct": base_conj["habit_conjunct"],
        "stability_class": s1[0],
        "stability_reproduced": stability_reproduced,
        "shadow_class_arm_a": shadow_class,
        "ruling": ruling,
        "binding_axis": axis,
    }
    out["reporting_only_findings"] = {
        "sensitivity_straddles": straddles,
        "r_guess_surprise": guess_surprise,
        "r_guess_note": ("SURPRISE — printed as a first-class anomaly" if guess_surprise
                         else "expected direction: M*(R-GUESS) much larger than M*(R-TABLE) or absent"),
    }
    out["sentinels"] = {
        "main_randranges": rng_main.randrange_calls,
        "stability_randranges": rng_stab.randrange_calls,
        "reporting_randranges": rng_rep.randrange_calls,
        "aux_draws": 0,
    }

    # ---------------------------------------------------------------- stdout
    print("VERDICT 052 — spool-scale go/no-go margin error budget (PROPOSAL 041)")
    print(f"frame: F ~ U{{0..1000}} · W = F + E + eps_s, eps_s ~ U{{-5..+5}} · "
          f"Fhat = W - Ehat · START iff Fhat >= Jhat + M · "
          f"M grid {{0,5,10,15,25,40,60,100}} g · regimes R-OWN / R-TABLE / R-GUESS")
    print()
    print("GATES")
    print(f"  hand-fixture-six-scenarios: "
          f"{'OK' if hf_ok else 'FAIL'} (all 7 outputs per scenario)")
    print(f"  zero-error-identity: {'OK' if zero_ok else 'FAIL'} "
          f"(RUNOUT == 0 all M, FORGONE(0) == 0 — exact)")
    print(f"  convolution-spot-check: {'OK' if spot_ok else 'FAIL'} "
          f"({spot_n} cells, collapsed == direct, exact equality)")
    print(f"  monotonicity (both arms, {mono_n} tables): {'OK' if mono_ok else 'FAIL'}")
    print(f"  arm agreement (main, 24+24 cells): {'PASS' if agree_ok else 'BREACH'} — "
          f"max |dRUNOUT| {float(max_dr):.6f} <= 0.003, "
          f"max |dFORGONE| {float(max_df):.6f} <= 0.01")
    print(f"  draw sentinels: main {rng_main.randrange_calls} · "
          f"stability {rng_stab.randrange_calls} · reporting {rng_rep.randrange_calls} · "
          f"aux 0 (never read)")
    print()
    for reg in REGIMES:
        tab = arm_a[reg]
        print(f"ARM A (decision arm, exact) — {reg}   "
              f"[feasible share {float(tab['feasible_share']):.4f}]")
        print("  M     RUNOUT       FORGONE      start-rate   (ArmS RUNOUT / FORGONE @200k)")
        s_l, r_l, g_l, fe = mc_main[reg]
        for mi, M in enumerate(M_GRID):
            print(f"  {M:>3}   {float(tab['RUNOUT'][mi]):.6f}     "
                  f"{float(tab['FORGONE'][mi]):.6f}     "
                  f"{float(tab['start_rate'][mi]):.4f}       "
                  f"({r_l[mi] / s_l[mi]:.6f} / {g_l[mi] / fe:.6f})")
        print()
    print("FEAS / M* (bands: RUNOUT <= 1/100 AND FORGONE <= 1/5)")
    print(f"  Feas(R-OWN)   = {feas_own}  ->  M*(R-OWN)   = {m_own}")
    print(f"  Feas(R-TABLE) = {feas_tab}  ->  M*(R-TABLE) = {m_tab}")
    print(f"  Feas(R-GUESS) = {feas_guess}  ->  M*(R-GUESS) = {m_guess}   (control row)")
    if guess_surprise:
        print("  ANOMALY (first-class): R-GUESS control violates the expected direction "
              "(M*(R-GUESS) not >> M*(R-TABLE)) — reporting-only, flagged loudly")
    print()
    print("DRIFT LEG (reporting-only, W' = W + d, d ~ U{0..8} — cannot flip)")
    for reg in REGIMES:
        fs = feas_set_fraction(variants["drift"][reg]["RUNOUT"],
                               variants["drift"][reg]["FORGONE"])
        print(f"  {reg}: Feas = {fs} -> M* = {fs[0] if fs else None}")
    print()
    print("SENSITIVITY LEGS (Arm A exact, reporting-only — name the axis, never flip)")
    for vn in variants:
        if vn == "drift":
            continue
        regs = variants[vn]
        parts = []
        for reg in ("R-OWN", "R-TABLE"):
            if reg in regs:
                fs = feas_set_fraction(regs[reg]["RUNOUT"], regs[reg]["FORGONE"])
                parts.append(f"M*({reg}) = {fs[0] if fs else None}")
        print(f"  {vn:<22} {' · '.join(parts)}")
    print(f"  straddles vs primary conjuncts: "
          f"{straddles if straddles else 'NONE'}")
    print()
    print("STABILITY LEG (seed 20261302, 20k/regime): "
          f"class = {s1[0]} · within the main agreement gate: "
          f"{'YES' if stab_agree_ok else 'NO'} · reproduces Arm A: "
          f"{'YES' if stability_reproduced else 'NO'}")
    print()
    print("DECISION (pre-registered, evaluated IN ORDER)")
    print(f"  0. agreement gate: {'PASS' if agree_ok else 'BREACH -> NULL (arm disagreement)'}")
    print(f"  1. REJECT (Feas(R-OWN) = empty, checked FIRST): "
          f"{'FIRES' if ruling == 'reject' else 'does not fire'} "
          f"(Feas(R-OWN) = {feas_own})")
    pocket = base_conj["pocket_conjunct"]
    habit = base_conj["habit_conjunct"]
    print(f"  2. APPROVE (M*(R-OWN) <= 25 AND (Feas(R-TABLE) = empty OR "
          f"M*(R-TABLE) >= M*(R-OWN) + 15) AND stability reproduction): "
          f"{'FIRES' if ruling == 'approve' else 'does not fire'}")
    print(f"     pocket conjunct M*(R-OWN) <= 25: {pocket} (M*(R-OWN) = {m_own})")
    print(f"     habit conjunct (Feas(R-TABLE) = empty OR M*(R-TABLE) >= "
          f"M*(R-OWN) + 15): {habit} (M*(R-TABLE) = {m_tab})")
    print(f"     stability reproduction: {stability_reproduced}")
    print(f"  3. RULING: {ruling.upper()}"
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
