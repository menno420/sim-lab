#!/usr/bin/env python3
"""VERDICT 082 runner — the WIP-cap dryness floor (idea-engine PROPOSAL 069).

Closed 2-station cyclic loop (CONWIP): K tokens between drafting and
verdicting, state n = unverdicted in-flight in {0..K}, births at rate
lambda iff n < K, deaths at rate mu iff n > 0, r = lambda/mu.

Three arms:
  Arm A (DECISION, seedless) — the truncated-geometric closed form,
        exact Fractions at every grid cell.
  Arm B (twin, seedless)     — INDEPENDENTLY-WRITTEN exact stationary
        solve: build the (K+1)-state generator Q and solve pi*Q = 0,
        sum(pi) = 1 by Fraction Gaussian elimination. Must reproduce
        every Arm-A number EXACTLY.
  Arm R (seeded, REPORTING-ONLY) — discrete-event traces of the literal
        loop at the decision cell under three service shapes at the same
        pinned means. NO statistical gate rides Arm R.

Hermetic: reads ONLY its own fixtures.json. Stdlib-only. Byte-identical
stdout + results.json across process runs (CPython 3.11 pinned).
"""

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------
# self-check machinery
# ----------------------------------------------------------------------
CHECKS = {"passed": 0, "failed": 0, "failures": []}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        CHECKS["failures"].append(name)
        print("SELF-CHECK FAILED: %s" % name)
    return bool(cond)


def frac(s):
    """Parse a fixture 'p/q' or 'p' string into an exact Fraction."""
    return Fraction(s)


def fstr(x):
    """Serialize a Fraction as 'p/q' (canonical, C11)."""
    return "%d/%d" % (x.numerator, x.denominator)


def ffloat(x):
    """Presentation-only float rendering (C7)."""
    return repr(float(x))


# ----------------------------------------------------------------------
# Arm A — truncated-geometric closed form (DECISION-bearing)
# ----------------------------------------------------------------------
def arm_a_pi(K, r):
    """pi(j) = r^j / sum_{i=0}^{K} r^i, exact."""
    denom = sum(r ** i for i in range(K + 1))
    return [r ** j / denom for j in range(K + 1)]


def arm_a_metrics(K, r):
    """All published metrics at one cell, exact Fractions (mu = 1, C1)."""
    pi = arm_a_pi(K, r)
    lam, mu = r, Fraction(1)
    D = pi[0]
    B = pi[K]
    TH = mu * (1 - pi[0])            # in units of mu
    E = TH / min(lam, mu)
    W = Fraction(K) / TH             # in units of 1/mu
    return {"pi": pi, "D": D, "B": B, "TH": TH, "E": E, "W": W,
            "lam": lam, "mu": mu}


# ----------------------------------------------------------------------
# Arm B — independently-written generator solve (twin)
# ----------------------------------------------------------------------
def arm_b_pi(K, r):
    """Stationary law via pi*Q = 0, sum(pi) = 1, Fraction Gaussian elim.

    Deliberately shares NO code with arm_a_pi: builds the full
    (K+1)x(K+1) generator of the birth-death chain (birth rate lambda = r
    for n < K, death rate mu = 1 for n > 0) and solves the transposed
    balance system with the normalization row appended.
    """
    n = K + 1
    lam, mu = r, Fraction(1)
    # generator Q: Q[i][j] = rate i -> j, diagonal = -row-sum
    Q = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        if i < K:
            Q[i][i + 1] = lam
        if i > 0:
            Q[i][i - 1] = mu
        Q[i][i] = -sum(Q[i][j] for j in range(n) if j != i)
    # balance: sum_i pi_i Q[i][j] = 0 for all j  ->  A x = b with
    # A[j][i] = Q[i][j]; replace last equation by normalization.
    A = [[Q[i][j] for i in range(n)] for j in range(n)]
    b = [Fraction(0)] * n
    A[n - 1] = [Fraction(1)] * n
    b[n - 1] = Fraction(1)
    # Gaussian elimination with partial (first-nonzero) pivoting, exact.
    for col in range(n):
        piv = None
        for row in range(col, n):
            if A[row][col] != 0:
                piv = row
                break
        if piv is None:
            raise ArithmeticError("singular balance system")
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        inv = 1 / A[col][col]
        A[col] = [v * inv for v in A[col]]
        b[col] = b[col] * inv
        for row in range(n):
            if row != col and A[row][col] != 0:
                f = A[row][col]
                A[row] = [A[row][j] - f * A[col][j] for j in range(n)]
                b[row] = b[row] - f * b[col]
    return b  # pi as list of Fractions


def arm_b_metrics(K, r):
    pi = arm_b_pi(K, r)
    lam, mu = r, Fraction(1)
    D = pi[0]
    B = pi[K]
    TH = mu * (1 - pi[0])
    E = TH / min(lam, mu)
    W = Fraction(K) / TH
    return {"pi": pi, "D": D, "B": B, "TH": TH, "E": E, "W": W,
            "lam": lam, "mu": mu}


# ----------------------------------------------------------------------
# deterministic-service exact exhibit (reporting-only)
# ----------------------------------------------------------------------
def d_det(K, r):
    val = 1 - Fraction(K) * r / (1 + r)
    return val if val > 0 else Fraction(0)


def k_det(r):
    """min K with D_det = 0: ceil((1 + r)/r)."""
    q = (1 + r) / r
    return int(q) if q.denominator == 1 else int(q) + 1


# ----------------------------------------------------------------------
# K*(r, d) safe-cap scan (reporting; C2)
# ----------------------------------------------------------------------
def k_star(r, d):
    if r <= 1 and (1 - r) >= d:
        return None  # unreachable — the T2 frontier theorem, not a timeout
    K = 1
    while arm_a_pi(K, r)[0] > d:
        K += 1
    return K


# ----------------------------------------------------------------------
# Arm R — discrete-event traces (seeded, REPORTING-ONLY)
# ----------------------------------------------------------------------
def simulate_loop(K, n_cycles, draft_sampler, verdict_sampler):
    """Continuous-time trace of the closed loop; returns time-average
    D-hat, B-hat (C4) and the number of (draft, verdict) service starts.

    Initial condition n = K (pipe full, C5). Draw order pinned (C6): at
    every event epoch, any station-1 (drafting) start draws FIRST, then
    any station-2 (verdicting) start.
    """
    INF = float("inf")
    n = K
    t = 0.0
    t_dry = 0.0
    t_blocked = 0.0
    draft_starts = 0
    verdict_starts = 0
    # station-1 works iff n < K; station-2 works iff n > 0
    next_draft = INF
    next_verdict = INF
    if n < K:
        next_draft = t + draft_sampler()
        draft_starts += 1
    if n > 0:
        next_verdict = t + verdict_sampler()
        verdict_starts += 1
    completions = 0
    while completions < n_cycles:
        t_next = min(next_draft, next_verdict)
        dt = t_next - t
        if n == 0:
            t_dry += dt
        if n == K:
            t_blocked += dt
        t = t_next
        if next_draft <= next_verdict:
            # drafting completion: birth
            n += 1
            next_draft = INF
        else:
            # verdict completion: death
            n -= 1
            next_verdict = INF
            completions += 1
        # event epoch: start new services, station-1 draw first (C6)
        if n < K and next_draft == INF:
            next_draft = t + draft_sampler()
            draft_starts += 1
        if n > 0 and next_verdict == INF:
            next_verdict = t + verdict_sampler()
            verdict_starts += 1
    return {"D_hat": t_dry / t, "B_hat": t_blocked / t,
            "draft_starts": draft_starts, "verdict_starts": verdict_starts,
            "total_time": t}


def arm_r(fix):
    """Three service shapes x (main, stability) legs; draw counting."""
    cellK = fix["grids"]["decision_cell"]["K"]
    S_d = float(frac(fix["measured_constants"]["S_d"]))
    S_v = float(frac(fix["measured_constants"]["S_v"]))
    gaps = [float(g) for g in fix["measured_constants"]["burst_gaps_seconds"]]
    out = {}
    for leg, seed_key, n_key in (
        ("main", "seed_main", "n_main_cycles"),
        ("stability", "seed_stability", "n_stability_cycles"),
    ):
        rng = random.Random(fix["arm_r"][seed_key])
        SEED_REGISTRY.append(fix["arm_r"][seed_key])
        n_cycles = fix["arm_r"][n_key]
        draws = {"n": 0}

        def counted(fn):
            def inner():
                draws["n"] += 1
                return fn()
            return inner

        legs = {}
        # shape 1: exponential (both stations draw; 1 draw per start)
        draws["n"] = 0
        res = simulate_loop(
            cellK, n_cycles,
            counted(lambda: rng.expovariate(1.0 / S_d)),
            counted(lambda: rng.expovariate(1.0 / S_v)))
        expected = res["draft_starts"] + res["verdict_starts"]
        check("arm-R %s exponential draw-count sentinel" % leg,
              draws["n"] == expected)
        legs["exponential"] = {"D_hat": repr(res["D_hat"]),
                               "B_hat": repr(res["B_hat"]),
                               "draws": draws["n"]}
        # shape 2: deterministic (zero draws)
        draws["n"] = 0
        res = simulate_loop(cellK, n_cycles, lambda: S_d, lambda: S_v)
        check("arm-R %s deterministic draw-count sentinel (0)" % leg,
              draws["n"] == 0)
        legs["deterministic"] = {"D_hat": repr(res["D_hat"]),
                                 "B_hat": repr(res["B_hat"]),
                                 "draws": 0}
        # shape 3: measured two-point empirical mix (drafting side only
        # draws — uniform over the four pinned gaps; S_v degenerate, C6)
        draws["n"] = 0
        res = simulate_loop(
            cellK, n_cycles,
            counted(lambda: gaps[int(rng.random() * 4.0) & 3]),
            lambda: S_v)
        check("arm-R %s empirical draw-count sentinel" % leg,
              draws["n"] == res["draft_starts"])
        legs["empirical"] = {"D_hat": repr(res["D_hat"]),
                             "B_hat": repr(res["B_hat"]),
                             "draws": draws["n"]}
        out[leg] = legs
    return out


SEED_REGISTRY = []


# ----------------------------------------------------------------------
# twin decision evaluators (independently written)
# ----------------------------------------------------------------------
def evaluator_one(vals, bands, gates_green):
    """Evaluator 1 (fed Arm-A numbers): literal registered order."""
    # REJECT first
    if (vals["D3_rhat"] >= bands["rej_D3"] and
            all(v >= bands["rej_grid"] for v in vals["D3_all_r"]) and
            vals["D12_rhat"] >= bands["rej_D12"] and
            vals["B3_rhat"] >= bands["rej_B3"]):
        if gates_green:
            return "REJECT"
    if not gates_green:
        return "INVALID"
    if vals["D3_rhat"] <= bands["app_D3"] and vals["B3_rhat"] <= bands["app_B3"]:
        return "APPROVE"
    return "NULL"


def evaluator_two(vals, bands, gates_green):
    """Evaluator 2 (fed Arm-B numbers): written separately — walks the
    clause list as data and short-circuits in the registered order."""
    reject_clauses = [
        vals["D3_rhat"] - bands["rej_D3"] >= 0,
        min(vals["D3_all_r"]) - bands["rej_grid"] >= 0,
        vals["D12_rhat"] - bands["rej_D12"] >= 0,
        vals["B3_rhat"] - bands["rej_B3"] >= 0,
    ]
    if gates_green and False not in reject_clauses:
        return "REJECT"
    if not gates_green:
        return "INVALID"
    approve_clauses = [
        bands["app_D3"] - vals["D3_rhat"] >= 0,
        bands["app_B3"] - vals["B3_rhat"] >= 0,
    ]
    if False not in approve_clauses:
        return "APPROVE"
    return "NULL"


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main():
    check("CPython 3.11 pinned",
          sys.version_info[:2] == (3, 11))
    fix = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
    check("cpython pin matches fixture",
          fix["battery_f6"]["cpython_pin"] == "3.11")

    # --- re-derive the anchors from the pinned gap integers (F3) -------
    gaps = fix["measured_constants"]["burst_gaps_seconds"]
    S_d = Fraction(sum(gaps), len(gaps))
    check("S_d = 3973/2 from the pinned burst gaps",
          S_d == frac(fix["measured_constants"]["S_d"]))
    S_v = frac(fix["measured_constants"]["S_v"])
    r_hat = S_v / S_d
    check("r_hat re-derived = 4492/3973",
          r_hat == frac(fix["anchors_f3"]["r_hat"]))
    nb = fix["measured_constants"]["night_burst"]
    r2 = S_v / Fraction(nb["total_seconds"], nb["gaps"])
    check("r2 re-derived = 40428/30847",
          r2 == frac(fix["anchors_f3"]["r2"]))
    lt = fix["measured_constants"]["lifetime"]
    r_life = S_v / Fraction(lt["total_seconds"], lt["gaps"])
    check("r_life re-derived = 150482/391243",
          r_life == frac(fix["anchors_f3"]["r_life"]))

    K_grid = fix["grids"]["K"]
    r_grid = [frac(s) for s in fix["grids"]["r"]]
    r_names = fix["grids"]["r"]
    check("r_hat sits in the registered r grid", r_hat in r_grid)
    check("r2 sits in the registered r grid", r2 in r_grid)

    # --- Arms A and B over the full grid -------------------------------
    surface = {}
    for K in K_grid:
        for rn, r in zip(r_names, r_grid):
            a = arm_a_metrics(K, r)
            b = arm_b_metrics(K, r)
            # F6: twin exactness on every number
            check("F6 twin pi exact-equal K=%d r=%s" % (K, rn),
                  a["pi"] == b["pi"])
            for m in ("D", "B", "TH", "E", "W"):
                check("F6 twin %s exact-equal K=%d r=%s" % (m, K, rn),
                      a[m] == b[m])
            # F1: chain identities
            pi = a["pi"]
            lam, mu = a["lam"], a["mu"]
            check("F1 sum(pi)=1 K=%d r=%s" % (K, rn),
                  sum(pi) == 1)
            check("F1 detailed balance K=%d r=%s" % (K, rn),
                  all(lam * pi[j] == mu * pi[j + 1] for j in range(K)))
            check("F1 flow identity K=%d r=%s" % (K, rn),
                  lam * (1 - pi[K]) == mu * (1 - pi[0]))
            # F1: pi*Q = 0 residual exactly zero (Arm B's own generator)
            n = K + 1
            Q = [[Fraction(0)] * n for _ in range(n)]
            for i in range(n):
                if i < K:
                    Q[i][i + 1] = lam
                if i > 0:
                    Q[i][i - 1] = mu
                Q[i][i] = -sum(Q[i][j] for j in range(n) if j != i)
            resid = [sum(pi[i] * Q[i][j] for i in range(n)) for j in range(n)]
            check("F1 pi*Q=0 residual zero K=%d r=%s" % (K, rn),
                  all(v == 0 for v in resid))
            # F1: efficiency identities
            if r >= 1:
                check("F1 E=1-D (r>=1) K=%d r=%s" % (K, rn),
                      a["E"] == 1 - a["D"])
            if r <= 1:
                check("F1 E=1-B (r<=1) K=%d r=%s" % (K, rn),
                      a["E"] == 1 - a["B"])
            # F2a: T1 positivity with the exact lower bound
            lb = Fraction(1, K + 1) * min(Fraction(1), r ** (-K))
            check("F2a T1 D>0 K=%d r=%s" % (K, rn), a["D"] > 0)
            check("F2a T1 lower bound K=%d r=%s" % (K, rn), a["D"] >= lb)
            surface[(K, rn)] = a

    # F2b: strict monotone decrease of D in K (every r-column) and in r
    # (every K-row)
    for rn in r_names:
        col = [surface[(K, rn)]["D"] for K in K_grid]
        check("F2b D strictly decreasing in K at r=%s" % rn,
              all(col[i] > col[i + 1] for i in range(len(col) - 1)))
    for K in K_grid:
        row = [surface[(K, rn)]["D"] for rn in r_names]
        # the registered r grid is listed in increasing order — assert it
        check("r grid increasing (precondition) K=%d" % K,
              all(r_grid[i] < r_grid[i + 1] for i in range(len(r_grid) - 1)))
        check("F2b D strictly decreasing in r at K=%d" % K,
              all(row[i] > row[i + 1] for i in range(len(row) - 1)))
    # F2b frontier: D(40, 1/2) in (1 - r, 1 - r + 1e-10)
    fr = fix["grids"]["frontier_check_cell"]
    rF = frac(fr["r"])
    D40 = arm_a_pi(fr["K"], rF)[0]
    check("F2b frontier D(40,1/2) > 1 - r", D40 > 1 - rF)
    check("F2b frontier D(40,1/2) < 1 - r + 1e-10",
          D40 < (1 - rF) + Fraction(1, 10 ** 10))
    # F2c: T3 balanced knee at r = 1
    for K in K_grid:
        a = surface[(K, "1")]
        check("F2c T3 uniform at r=1 K=%d" % K,
              all(p == Fraction(1, K + 1) for p in a["pi"]))
        check("F2c T3 D=B=1/(K+1) K=%d" % K,
              a["D"] == a["B"] == Fraction(1, K + 1))
        check("F2c T3 TH=K/(K+1)*mu K=%d" % K,
              a["TH"] == Fraction(K, K + 1))
    check("F2c T3 Delta-D(3->4, r=1) = 1/20",
          surface[(3, "1")]["D"] - surface[(4, "1")]["D"] == Fraction(1, 20))

    # --- F3 census anchors ---------------------------------------------
    anch = fix["anchors_f3"]
    rhn = fix["grids"]["decision_cell"]["r"]
    check("F3 D(3, r_hat)",
          surface[(3, rhn)]["D"] == frac(anch["D_3_rhat"]))
    check("F3 D(3, r_hat) construction identity",
          surface[(3, rhn)]["D"] ==
          Fraction(3973 ** 3,
                   3973 ** 3 + 3973 ** 2 * 4492 +
                   3973 * 4492 ** 2 + 4492 ** 3))
    check("F3 B(3, r_hat)",
          surface[(3, rhn)]["B"] == frac(anch["B_3_rhat"]))
    check("F3 D(3, r2)",
          surface[(3, "40428/30847")]["D"] == frac(anch["D_3_r2"]))
    check("F3 D(3, 1) = 1/4", surface[(3, "1")]["D"] == frac(anch["D_3_1"]))
    check("F3 D(3, 1/2) = 8/15",
          surface[(3, "1/2")]["D"] == frac(anch["D_3_half"]))
    check("F3 D(3, 2) = 1/15",
          surface[(3, "2")]["D"] == frac(anch["D_3_2"]))
    check("F3 D(12, r_hat) exact rational pin",
          surface[(12, rhn)]["D"] == frac(anch["D_12_rhat"]))
    check("F3 D_det(3, r_hat) = 0",
          d_det(3, r_hat) == frac(anch["D_det_3_rhat"]))
    check("F3 K_det(r_hat) = 2", k_det(r_hat) == anch["K_det_rhat"])

    # --- F4 hand worlds --------------------------------------------------
    for rn, r in zip(r_names, r_grid):
        check("F4 K=1 hand world D=1/(1+r) at r=%s" % rn,
              surface[(1, rn)]["D"] == 1 / (1 + r))
    check("F4 K=2, r=2 hand world pi=(1/7,2/7,4/7)",
          arm_a_pi(2, Fraction(2)) ==
          [Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)])
    check("F4 K=3, r=1 uniform quarter",
          surface[(3, "1")]["pi"] == [Fraction(1, 4)] * 4)

    # --- F5 swap symmetry + grid-end orderings ---------------------------
    for K in K_grid:
        for rn, r in zip(r_names, r_grid):
            pi_r = surface[(K, rn)]["pi"]
            pi_inv = arm_a_pi(K, 1 / r)
            check("F5 swap symmetry K=%d r=%s" % (K, rn),
                  all(pi_r[j] == pi_inv[K - j] for j in range(K + 1)))
        check("F5 D(K,r)=B(K,1/r) K=%d (grid ends)" % K,
              surface[(K, "1/2")]["D"] == arm_a_metrics(K, Fraction(2))["B"])
        check("F5 grid-end ordering D K=%d" % K,
              surface[(K, "1/2")]["D"] > surface[(K, "2")]["D"])
        check("F5 grid-end ordering B K=%d" % K,
              surface[(K, "1/2")]["B"] < surface[(K, "2")]["B"])

    # --- K*(r, d) safe-cap table (reporting) ------------------------------
    d_list = [Fraction(1, 10), Fraction(1, 20), Fraction(1, 100)]
    kstar_table = {}
    for rn, r in zip(r_names, r_grid):
        kstar_table[rn] = ["unreachable" if k_star(r, d) is None
                           else k_star(r, d) for d in d_list]
    # spot identities: at r = 1, D = 1/(K+1) <= d gives K = 9/19/99
    check("K* spot r=1 -> [9, 19, 99]", kstar_table["1"] == [9, 19, 99])
    check("K* consistency at the decision cell: K*(r_hat, 1/10) > 3 "
          "(the committed cap misses the 1/10 band)",
          kstar_table[rhn][0] > 3)

    # --- reporting extras -------------------------------------------------
    D3_life = arm_a_pi(3, r_life)[0]
    D12_2 = arm_a_pi(12, Fraction(2))[0]
    check("reporting D(12, 2) = 1/8191 (the deep-cap APPROVE-side witness)",
          D12_2 == Fraction(1, 8191))
    ddet_table = {rn: fstr(d_det(3, r)) for rn, r in zip(r_names, r_grid)}

    # --- Arm R (seeded, reporting-only) -----------------------------------
    armr = arm_r(fix)
    check("seed registry exact (main, stability; pinned order)",
          SEED_REGISTRY == [fix["arm_r"]["seed_main"],
                            fix["arm_r"]["seed_stability"]])
    # presentation shuffle (C9): row order of the published Arm-R table
    pres = random.Random(fix["arm_r"]["seed_presentation"])
    SEED_REGISTRY.append(fix["arm_r"]["seed_presentation"])
    row_keys = ["exponential", "deterministic", "empirical"]
    pres.shuffle(row_keys)
    check("aux seed 20261613 never read (constructor registry)",
          fix["arm_r"]["seed_aux_never_read"] not in SEED_REGISTRY and
          len(SEED_REGISTRY) == 3)

    # --- decision ----------------------------------------------------------
    bands = {
        "rej_D3": frac(fix["decision"]["reject"]["D3_rhat_min"]),
        "rej_grid": frac(fix["decision"]["reject"]["D3_all_grid_r_min"]),
        "rej_D12": frac(fix["decision"]["reject"]["D12_rhat_min"]),
        "rej_B3": frac(fix["decision"]["reject"]["B3_rhat_min"]),
        "app_D3": frac(fix["decision"]["approve"]["D3_rhat_max"]),
        "app_B3": frac(fix["decision"]["approve"]["B3_rhat_max"]),
    }
    gates_green = CHECKS["failed"] == 0
    vals_a = {
        "D3_rhat": surface[(3, rhn)]["D"],
        "D3_all_r": [surface[(3, rn)]["D"] for rn in r_names],
        "D12_rhat": surface[(12, rhn)]["D"],
        "B3_rhat": surface[(3, rhn)]["B"],
    }
    b3 = arm_b_metrics(3, r_hat)
    b12 = arm_b_metrics(12, r_hat)
    vals_b = {
        "D3_rhat": b3["D"],
        "D3_all_r": [arm_b_metrics(3, r)["D"] for r in r_grid],
        "D12_rhat": b12["D"],
        "B3_rhat": b3["B"],
    }
    token_a = evaluator_one(vals_a, bands, gates_green)
    token_b = evaluator_two(vals_b, bands, gates_green)
    check("F6 twin evaluators agree", token_a == token_b)
    ruling = token_a if token_a == token_b else "INVALID"

    # anchor-fragility NULL axis probe (registered, disarmed at drafting):
    check("anchor agreement on the headline clause (r_hat vs r2)",
          (surface[(3, rhn)]["D"] >= bands["rej_D3"]) ==
          (surface[(3, "40428/30847")]["D"] >= bands["rej_D3"]))

    # disclosed-landing comparison (C10; anomalies named, never gated)
    disclosed = {
        "D(3,r_hat) = 62712728317/304425042745":
            surface[(3, rhn)]["D"] == Fraction(62712728317, 304425042745),
        "B(3,r_hat) = 90639863488/304425042745":
            surface[(3, rhn)]["B"] == Fraction(90639863488, 304425042745),
        "D(12,r_hat) ~ 0.0332081 (stated precision)":
            abs(float(surface[(12, rhn)]["D"]) - 0.0332081) < 5e-8,
        "D_det(3,r_hat) = 0 exactly": d_det(3, r_hat) == 0,
        "D(3,r_life) ~ 0.629 (stated precision)":
            abs(float(D3_life) - 0.629) < 5e-4,
        "D(12,2) = 1/8191": D12_2 == Fraction(1, 8191),
        "margin headline 2.06x":
            abs(float(surface[(3, rhn)]["D"] / Fraction(1, 10)) - 2.06) < 5e-3,
        "margin backpressure 1.49x":
            abs(float(surface[(3, rhn)]["B"] / Fraction(1, 5)) - 1.49) < 5e-3,
    }
    anomalies = [k for k, v in disclosed.items() if not v]

    # --- publish -------------------------------------------------------------
    results = {
        "verdict": "082",
        "ruling": ruling,
        "tokens": {"evaluator_one_on_arm_a": token_a,
                   "evaluator_two_on_arm_b": token_b},
        "decision_cell": {
            "K": 3, "r": fstr(r_hat),
            "D": fstr(surface[(3, rhn)]["D"]),
            "D_float": ffloat(surface[(3, rhn)]["D"]),
            "B": fstr(surface[(3, rhn)]["B"]),
            "B_float": ffloat(surface[(3, rhn)]["B"]),
            "D12": fstr(surface[(12, rhn)]["D"]),
            "D12_float": ffloat(surface[(12, rhn)]["D"]),
            "D_det": fstr(d_det(3, r_hat)),
            "K_det": k_det(r_hat),
        },
        "surfaces": {
            "%d|%s" % (K, rn): {
                "D": fstr(surface[(K, rn)]["D"]),
                "D_float": ffloat(surface[(K, rn)]["D"]),
                "B": fstr(surface[(K, rn)]["B"]),
                "TH_over_mu": fstr(surface[(K, rn)]["TH"]),
                "E": fstr(surface[(K, rn)]["E"]),
                "W_times_mu": fstr(surface[(K, rn)]["W"]),
            }
            for K in K_grid for rn in r_names
        },
        "kstar_table_d_1_10__1_20__1_100": kstar_table,
        "d_det_row_K3": ddet_table,
        "reporting": {
            "D(3, r_life)": fstr(D3_life),
            "D(3, r_life)_float": ffloat(D3_life),
            "D(12, 2)": fstr(D12_2),
            "frontier_D(40,1/2)_minus_half_float":
                ffloat(D40 - Fraction(1, 2)),
        },
        "arm_r": armr,
        "arm_r_published_row_order": row_keys,
        "seed_registry": SEED_REGISTRY,
        "anomalies_vs_disclosed_landing": anomalies,
        "disclosed_landing_rows_checked": len(disclosed),
        "self_checks": {"passed": CHECKS["passed"],
                        "failed": CHECKS["failed"],
                        "failures": CHECKS["failures"]},
    }
    out = json.dumps(results, sort_keys=True, ensure_ascii=True, indent=2)
    (HERE / "results.json").write_text(out + "\n", encoding="utf-8")

    print("VERDICT 082 runner — WIP-cap dryness floor (P069)")
    print("ruling: %s (evaluators %s/%s)" % (ruling, token_a, token_b))
    print("decision cell K=3, r_hat=%s:" % fstr(r_hat))
    print("  D  = %s ~ %s" % (fstr(surface[(3, rhn)]["D"]),
                              ffloat(surface[(3, rhn)]["D"])))
    print("  B  = %s ~ %s" % (fstr(surface[(3, rhn)]["B"]),
                              ffloat(surface[(3, rhn)]["B"])))
    print("  D(12, r_hat) ~ %s" % ffloat(surface[(12, rhn)]["D"]))
    print("  D_det(3, r_hat) = %s (K_det = %d)" % (
        fstr(d_det(3, r_hat)), k_det(r_hat)))
    print("grid D(3, r): %s" % "  ".join(
        "%s -> %s" % (rn, fstr(surface[(3, rn)]["D"])) for rn in r_names))
    print("K* table (d = 1/10, 1/20, 1/100): %s" % json.dumps(
        kstar_table, sort_keys=True))
    print("D(3, r_life) = %s ~ %s" % (fstr(D3_life), ffloat(D3_life)))
    print("arm R (reporting-only), published row order %s:" % row_keys)
    for leg in ("main", "stability"):
        for shape in row_keys:
            row = armr[leg][shape]
            print("  %s/%s: D_hat=%s B_hat=%s draws=%d" % (
                leg, shape, row["D_hat"], row["B_hat"], row["draws"]))
    print("anomalies vs disclosed landing: %s" % (anomalies or "NONE"))
    print("self-checks: %d passed, %d failed" % (
        CHECKS["passed"], CHECKS["failed"]))
    if CHECKS["failed"]:
        print("FAILURES: %s" % CHECKS["failures"])
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
