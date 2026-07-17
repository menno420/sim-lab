#!/usr/bin/env python3
"""
VERDICT-108 simulation harness  --  verifies PROPOSAL-095:
"catch-up rubber-band as a proportional (delayed / derivative-augmented) feedback controller."

Stdlib-only, fully deterministic, principled Monte-Carlo (no analytic answers plugged in;
analytic values are used only as CROSS-CHECKS reported alongside the measured ones).

Registered signed-gap iterator (params d, beta):

    g(t+1) = g(t) + F - k*g(t-d) - beta*(g(t) - g(t-1)) + eps(t),
             eps ~ Normal(0, sigma^2),   F = 2*s,   g0 = 0,   g(-1)=g(-2)=0.

    base world  d=0,beta=0 :  g(t+1) = (1-k)*g(t) + F + eps          (AR(1) w/ drift)
    R3   world  d=1,beta=0 :  g(t+1) = g(t) + F - k*g(t-1) + eps     (char z^2 - z + k = 0, Jury boundary k=1)
    R4b  world  d=0,beta!=0:  flip-bifurcation boundary  k_crit = 2 - 2*beta  (z=-1 root)

Run:  python3 verdict108_sim.py     (exit 0 only if all self-checks pass)
"""

import hashlib
import json
import math
import random

# --------------------------------------------------------------------------------------
# World constants (registered)
# --------------------------------------------------------------------------------------
SEED     = 20260717
SIGMA    = 1.0
S_MAIN   = 0.5
F_MAIN   = 2.0 * S_MAIN            # = 1.0
T        = 4000
BURN     = 1000
G_CAP    = 1e6
N_REPS   = 400                     # main R1/R2 base sweep
N_AUX    = 150                     # auxiliary engagement sweeps (R3, s-sweep)
N_DIV    = 40                      # divergence-boundary probes (R3 cliff, R4b onset)
T_DIV    = 4000                    # keep long so marginal (|z|=1) stays sub-cap, unstable blows past
# R4a skill-off collapse: E is exactly 0 by symmetry when F=0, so we only need to drive the
# per-k skill_fidelity Monte-Carlo noise below threshold. F=0 mixes fast -> short T, many reps.
N_R4A    = 5000
T_R4A    = 500
BURN_R4A = 100
K_GRID   = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 1.9, 1.95, 2.05, 2.2]

# --------------------------------------------------------------------------------------
# RNG keying: independent gaussian stream per (world, k_index, rep), folded off a master SEED.
# repr() of a tuple of ints/small-decimals is deterministic; sha256 is not hash-randomized.
# --------------------------------------------------------------------------------------
def make_rng(world_id, ki, rep):
    key = (SEED, world_id, ki, rep)
    digest = hashlib.sha256(repr(key).encode("ascii")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def sgn(x):
    return 1 if x >= 0.0 else -1


# --------------------------------------------------------------------------------------
# Core simulator: one rep of the registered iterator.
# Returns per-rep observables (no trajectory stored).
# --------------------------------------------------------------------------------------
def simulate_rep(k, F, beta, d, rng, Tsteps=T, burn=BURN, gcap=G_CAP):
    # Trajectory indices 0..Tsteps-1 ; g(0)=0. Post-burn window is t in [burn, Tsteps).
    g_prev = 0.0          # g(idx-2)
    g_curr = 0.0          # g(idx-1) -> starts as g(0)

    flips = 0
    compares = 0
    psum = 0.0
    psumsq = 0.0
    pcount = 0
    diverged = False

    for idx in range(1, Tsteps):                     # produce g(1) .. g(Tsteps-1)
        eps = rng.gauss(0.0, SIGMA)
        delayed = g_curr if d == 0 else g_prev
        g_next = g_curr + F - k * delayed - beta * (g_curr - g_prev) + eps

        if abs(g_next) > gcap or g_next != g_next:   # divergence / NaN guard
            diverged = True
            g_prev, g_curr = g_curr, g_next
            break

        s_prev = sgn(g_curr)                         # sign(g(idx-1))
        g_prev = g_curr
        g_curr = g_next                              # now g_curr == g(idx)
        s_now = sgn(g_curr)                          # sign(g(idx))

        if idx >= burn:                              # t in [burn, Tsteps)
            compares += 1
            if s_now != s_prev:                      # lead change: sign(g(t)) != sign(g(t-1))
                flips += 1
            psum += g_curr
            psumsq += g_curr * g_curr
            pcount += 1

    lc_rate = 0.0 if (diverged or compares == 0) else flips / compares
    final_sign = sgn(g_curr)
    return {
        "lc_rate": lc_rate,
        "final_sign": final_sign,
        "diverged": diverged,
        "psum": 0.0 if diverged else psum,
        "psumsq": 0.0 if diverged else psumsq,
        "pcount": 0 if diverged else pcount,
    }


# --------------------------------------------------------------------------------------
# Sweep a k-grid for one world; compute E(k), se, lead_change_rate, skill_fidelity,
# var_measured, diverged_frac.
# --------------------------------------------------------------------------------------
def sweep(world_id, k_grid, F, beta, d, nreps, Tsteps=T, burn=BURN, want_var=True):
    out = {}
    for ki, k in enumerate(k_grid):
        lc_list = []
        n_div = 0
        n_final_pos = 0
        vsum = 0.0
        vsumsq = 0.0
        vcount = 0
        for rep in range(nreps):
            rng = make_rng(world_id, ki, rep)
            r = simulate_rep(k, F, beta, d, rng, Tsteps=Tsteps, burn=burn)
            lc_list.append(r["lc_rate"])
            if r["diverged"]:
                n_div += 1
            if r["final_sign"] == sgn(F) and F != 0.0:
                n_final_pos += 1
            elif F == 0.0 and r["final_sign"] > 0:
                n_final_pos += 1
            if want_var and not r["diverged"]:
                vsum += r["psum"]
                vsumsq += r["psumsq"]
                vcount += r["pcount"]

        skill_fidelity = n_final_pos / nreps
        c = 2.0 * skill_fidelity - 1.0
        E_reps = [lc * c for lc in lc_list]        # diverged reps have lc=0 -> E=0
        mean_E = sum(E_reps) / nreps
        if nreps > 1:
            var_E = sum((e - mean_E) ** 2 for e in E_reps) / (nreps - 1)
            se = math.sqrt(var_E / nreps)
        else:
            se = 0.0
        lead_change_rate = sum(lc_list) / nreps

        if want_var and vcount > 1:
            mean_g = vsum / vcount
            var_measured = vsumsq / vcount - mean_g * mean_g
        else:
            var_measured = None

        denom = k * (2.0 - k)
        var_analytic = (SIGMA * SIGMA / denom) if (d == 0 and beta == 0.0 and denom > 0) else None
        if var_measured is not None and var_analytic is not None:
            rel_err = abs(var_measured - var_analytic) / var_analytic
        else:
            rel_err = None

        out[k] = {
            "mean_E": mean_E,
            "se": se,
            "lead_change_rate": lead_change_rate,
            "skill_fidelity": skill_fidelity,
            "var_measured": var_measured,
            "var_analytic": var_analytic,
            "rel_err": rel_err,
            "diverged_frac": n_div / nreps,
        }
    return out


# --------------------------------------------------------------------------------------
# Divergence-boundary probe: find (last_stable_k, first_divergent_k) on a fine grid.
# A k is "divergent" if diverged_frac > 0.5.
# --------------------------------------------------------------------------------------
def boundary_bracket(world_id, k_fine, F, beta, d, nreps=N_DIV, Tsteps=T_DIV):
    rows = []
    for ki, k in enumerate(k_fine):
        n_div = 0
        for rep in range(nreps):
            rng = make_rng(world_id, ki, rep)
            r = simulate_rep(k, F, beta, d, rng, Tsteps=Tsteps)
            if r["diverged"]:
                n_div += 1
        frac = n_div / nreps
        rows.append((round(k, 4), frac, frac > 0.5))
    last_stable = None
    first_div = None
    for k, frac, is_div in rows:
        if not is_div:
            last_stable = k
        if is_div and first_div is None:
            first_div = k
    return {"rows": rows, "last_stable_k": last_stable, "first_divergent_k": first_div}


def argmax_interior(per_k, grid):
    # argmax over grid of mean_E; interior means not the first/last grid element
    best_k = None
    best_E = -1e18
    for k in grid:
        e = per_k[k]["mean_E"]
        if e > best_E:
            best_E = e
            best_k = k
    interior = (best_k != grid[0] and best_k != grid[-1])
    return best_k, best_E, interior


# ======================================================================================
# BUILD RESULTS
# ======================================================================================
def build_results():
    results = {"params": {
        "SEED": SEED, "SIGMA": SIGMA, "s_main": S_MAIN, "F_main": F_MAIN,
        "T": T, "BURN": BURN, "G_CAP": G_CAP, "N_REPS": N_REPS,
        "N_AUX": N_AUX, "N_DIV": N_DIV, "K_GRID": K_GRID,
    }}

    # ---- MAIN base sweep (d=0, beta=0, F=1.0) : R1 + R2 -------------------------------
    base = sweep(world_id=0, k_grid=K_GRID, F=F_MAIN, beta=0.0, d=0, nreps=N_REPS, want_var=True)
    results["per_k"] = {f"{k:.4f}": base[k] for k in K_GRID}

    # ---------- R1: interior argmax beats both endpoints by >= 3 sigma -----------------
    argk, argE, interior = argmax_interior(base, K_GRID)
    lo = base[0.2]; hi = base[2.2]
    def sigma_margin(a, se_a, b, se_b):
        comb = math.sqrt(se_a * se_a + se_b * se_b)
        return (a - b) / comb if comb > 0 else float("inf")
    m_lo = sigma_margin(argE, base[argk]["se"], lo["mean_E"], lo["se"])
    m_hi = sigma_margin(argE, base[argk]["se"], hi["mean_E"], hi["se"])
    R1_pass = interior and (m_lo >= 3.0) and (m_hi >= 3.0)
    results["R1"] = {
        "argmax_k": argk, "argmax_E": argE, "argmax_se": base[argk]["se"],
        "interior": interior,
        "endpoint_lo_k": 0.2, "endpoint_lo_E": lo["mean_E"], "endpoint_lo_se": lo["se"],
        "endpoint_hi_k": 2.2, "endpoint_hi_E": hi["mean_E"], "endpoint_hi_se": hi["se"],
        "margin_lo_sigma": m_lo, "margin_hi_sigma": m_hi,
        "pass": R1_pass,
    }

    # ---------- R2: cliff at k=2, var formula on stable arm ----------------------------
    div_205 = base[2.05]["diverged_frac"]
    div_22 = base[2.2]["diverged_frac"]
    R2a_pass = (div_205 > 0.99) and (div_22 > 0.99)
    m_cliff = sigma_margin(base[1.95]["mean_E"], base[1.95]["se"],
                           base[2.05]["mean_E"], base[2.05]["se"])
    R2b_pass = m_cliff >= 3.0
    stable_ks = [k for k in K_GRID if k < 2.0]
    rel_errs = {}
    max_rel = 0.0
    for k in stable_ks:
        re = base[k]["rel_err"]
        rel_errs[f"{k:.4f}"] = {
            "var_measured": base[k]["var_measured"],
            "var_analytic": base[k]["var_analytic"],
            "rel_err": re,
        }
        if re is not None and re > max_rel:
            max_rel = re
    R2c_pass = max_rel < 0.05
    cliff_bracket = boundary_bracket(world_id=10,
                                     k_fine=[1.7, 1.8, 1.9, 1.95, 2.0, 2.05, 2.1, 2.2],
                                     F=F_MAIN, beta=0.0, d=0)
    R2_pass = R2a_pass and R2b_pass and R2c_pass
    results["R2"] = {
        "R2a_div_2.05": div_205, "R2a_div_2.2": div_22, "R2a_pass": R2a_pass,
        "R2b_lastStable_1.95_E": base[1.95]["mean_E"], "R2b_first_2.05_E": base[2.05]["mean_E"],
        "R2b_margin_sigma": m_cliff, "R2b_pass": R2b_pass,
        "R2c_rel_errs": rel_errs, "R2c_max_rel_err": max_rel, "R2c_pass": R2c_pass,
        "cliff_bracket": cliff_bracket,
        "pass": R2_pass,
    }

    # ---------- R3: d=1 delayed world -------------------------------------------------
    d1 = sweep(world_id=1, k_grid=K_GRID, F=F_MAIN, beta=0.0, d=1, nreps=N_AUX, want_var=False)
    d1_argk, d1_argE, d1_interior = argmax_interior(d1, K_GRID)
    d1_cliff = boundary_bracket(world_id=11,
                                k_fine=[0.6, 0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3],
                                F=F_MAIN, beta=0.0, d=1)
    # s-sweep argmax interior across s in {0.3,0.5,0.7} -> F in {0.6,1.0,1.4}
    s_sweep = {}
    s_argmaxes = []
    for i, s in enumerate([0.3, 0.5, 0.7]):
        Fs = 2.0 * s
        sw = sweep(world_id=100 + i, k_grid=K_GRID, F=Fs, beta=0.0, d=1, nreps=N_AUX, want_var=False)
        ak, aE, ai = argmax_interior(sw, K_GRID)
        s_sweep[f"s={s}"] = {"F": Fs, "argmax_k": ak, "argmax_E": aE, "interior": ai}
        s_argmaxes.append(ak)
    all_s_interior = all(s_sweep[key]["interior"] for key in s_sweep)
    R3_boundary_ok = (d1_cliff["last_stable_k"] is not None and
                      d1_cliff["last_stable_k"] <= 1.05 and
                      d1_cliff["first_divergent_k"] is not None and
                      d1_cliff["first_divergent_k"] <= 1.25 and
                      d1_cliff["first_divergent_k"] >= 0.95)
    R3_pass = R3_boundary_ok and d1_interior and all_s_interior
    results["R3"] = {
        "argmax_k": d1_argk, "argmax_E": d1_argE, "interior": d1_interior,
        "cliff_bracket": d1_cliff,
        "boundary_halved_ok": R3_boundary_ok,
        "s_sweep": s_sweep, "s_sweep_argmax_vector": s_argmaxes,
        "all_s_interior": all_s_interior,
        "pass": R3_pass,
    }

    # ---------- R4a: s=0 (F=0) collapses E ~ 0 ---------------------------------------
    # True E is exactly 0 (symmetry: skill_fidelity=0.5). Use many reps at short T so the
    # residual Monte-Carlo noise in skill_fidelity is driven below threshold.
    zero = sweep(world_id=2, k_grid=K_GRID, F=0.0, beta=0.0, d=0,
                 nreps=N_R4A, Tsteps=T_R4A, burn=BURN_R4A, want_var=False)
    max_absE = max(abs(zero[k]["mean_E"]) for k in K_GRID)
    R4a_pass = max_absE < 0.05
    results["R4a"] = {
        "per_k_E": {f"{k:.4f}": zero[k]["mean_E"] for k in K_GRID},
        "per_k_skill_fidelity": {f"{k:.4f}": zero[k]["skill_fidelity"] for k in K_GRID},
        "max_absE": max_absE, "pass": R4a_pass,
    }

    # ---------- R4b: beta-sweep divergence onset == k_crit = 2 - 2*beta ---------------
    r4b = {}
    onset_ok = True
    beta_specs = [
        (0.0, 2.0, [1.7, 1.8, 1.9, 1.95, 2.0, 2.05, 2.1, 2.2]),
        (+0.5, 1.0, [0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3]),
        (-0.5, 3.0, [2.6, 2.7, 2.8, 2.9, 2.95, 3.0, 3.05, 3.1, 3.2]),
    ]
    for j, (beta, kcrit, kfine) in enumerate(beta_specs):
        br = boundary_bracket(world_id=200 + j, k_fine=kfine, F=F_MAIN, beta=beta, d=0)
        ls = br["last_stable_k"]; fd = br["first_divergent_k"]
        # predicted onset must sit inside (or at) the measured bracket, tol one grid step
        ok = (ls is not None and fd is not None and ls <= kcrit + 1e-9 and fd >= kcrit - 0.06)
        onset_ok = onset_ok and ok
        r4b[f"beta={beta}"] = {
            "k_crit_predicted": kcrit,
            "last_stable_k": ls, "first_divergent_k": fd,
            "bracket_contains_predicted": ok, "rows": br["rows"],
        }
    R4b_pass = onset_ok
    results["R4b"] = {"table": r4b, "pass": R4b_pass}

    results["R4"] = {"pass": R4a_pass and R4b_pass, "R4a_pass": R4a_pass, "R4b_pass": R4b_pass}

    return results


# ======================================================================================
# TWIN EVALUATORS  (two independent verdict deciders over the SAME results dict)
# ======================================================================================
def evaluator_ifchain(res):
    """Explicit ordered if-chain -> (verdict, first_failing_gate)."""
    if not res["R1"]["pass"]:
        return ("REFUTED", "R1")
    if not res["R2"]["pass"]:
        return ("REFUTED", "R2")
    if not res["R3"]["pass"]:
        return ("REFUTED", "R3")
    if not (res["R4"]["R4a_pass"] and res["R4"]["R4b_pass"]):
        return ("REFUTED", "R4")
    return ("CONFIRMED", None)


def evaluator_datadriven(res):
    """Data-driven scan over an ordered gate table -> (verdict, first_failing_gate)."""
    gate_order = ["R1", "R2", "R3", "R4"]
    gate_pass = {
        "R1": res["R1"]["pass"],
        "R2": res["R2"]["pass"],
        "R3": res["R3"]["pass"],
        "R4": res["R4"]["pass"],
    }
    first_fail = next((g for g in gate_order if not gate_pass[g]), None)
    verdict = "CONFIRMED" if first_fail is None else "REFUTED"
    return (verdict, first_fail)


# ======================================================================================
# SERIALIZATION / DIGEST
# ======================================================================================
def round_floats(obj, nd=8):
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            return None
        return round(obj, nd)
    if isinstance(obj, dict):
        return {k: round_floats(v, nd) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(v, nd) for v in obj]
    return obj


def digest_of(core):
    canon = json.dumps(round_floats(core), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ======================================================================================
# SELF-CHECKS  (>= 12 ; harness exits 0 only if all pass)
# ======================================================================================
FIX_EPS = [0.30442, 0.56871, 0.77846, -1.79728, 0.49040, -1.32501, 0.86948, -0.79502]
FIX_G   = [1.30442, 1.04694, 1.35968, -1.34115, 2.02686, -1.13575, 2.32378, -0.72453]


def iterate_fixture(eps_seq, k, F, beta, d):
    g_prev = 0.0
    g_curr = 0.0
    gs = []
    for eps in eps_seq:
        delayed = g_curr if d == 0 else g_prev
        g_next = g_curr + F - k * delayed - beta * (g_curr - g_prev) + eps
        g_prev = g_curr
        g_curr = g_next
        gs.append(g_curr)
    return gs


def run_self_checks(res):
    checks = {}

    # 1. FIXTURE ANCHOR: iterator reproduces disclosed rep0 first-8 eps->g to 5 decimals.
    gs = iterate_fixture(FIX_EPS, k=1.4, F=1.0, beta=0.0, d=0)
    checks["01_fixture_anchor"] = all(abs(a - b) < 1e-5 for a, b in zip(gs, FIX_G))

    # 2. base world reduces to AR(1) (1-k)g+F+eps
    k = 1.4
    g = 0.3
    eps = 0.1
    manual = g + 1.0 - k * g - 0.0 * (g - 0.0) + eps
    ar1 = (1 - k) * g + 1.0 + eps
    checks["02_base_is_AR1"] = abs(manual - ar1) < 1e-12

    # 3. R3 world d=1: term uses g(t-1)
    gc, gp = 0.5, 0.2
    d1 = gc + 1.0 - 1.4 * gp - 0.0 * (gc - gp) + 0.0
    checks["03_d1_uses_prev"] = abs(d1 - (gc + 1.0 - 1.4 * gp)) < 1e-12

    # 4. beta world matches (1-k-beta)g + beta*g_prev + F + eps
    gc, gp, beta, kk, F, e = 0.7, 0.3, 0.5, 1.0, 1.0, 0.05
    gen = gc + F - kk * gc - beta * (gc - gp) + e
    exp = (1 - kk - beta) * gc + beta * gp + F + e
    checks["04_beta_form"] = abs(gen - exp) < 1e-12

    # 5. RNG keyed reproducibility
    a = make_rng(0, 3, 7).gauss(0, 1)
    b = make_rng(0, 3, 7).gauss(0, 1)
    c = make_rng(0, 3, 8).gauss(0, 1)
    checks["05_rng_reproducible"] = (a == b) and (a != c)

    # 6. variance analytic helper positive on stable arm
    checks["06_var_formula_pos"] = all(res["per_k"][f"{k:.4f}"]["var_analytic"] > 0
                                       for k in K_GRID if k < 2.0)

    # 7. lead_change_rate in [0,1]
    checks["07_lc_in_range"] = all(0.0 <= res["per_k"][f"{k:.4f}"]["lead_change_rate"] <= 1.0
                                   for k in K_GRID)

    # 8. skill_fidelity in [0,1]
    checks["08_sf_in_range"] = all(0.0 <= res["per_k"][f"{k:.4f}"]["skill_fidelity"] <= 1.0
                                   for k in K_GRID)

    # 9. sgn correct
    checks["09_sgn"] = (sgn(0.5) == 1 and sgn(-0.5) == -1 and sgn(0.0) == 1)

    # 10. diverged rep => lc_rate 0  (unstable k=2.2 base world, single rep)
    r = simulate_rep(2.2, 1.0, 0.0, 0, make_rng(999, 0, 0), Tsteps=500)
    checks["10_diverged_lc0"] = r["diverged"] and r["lc_rate"] == 0.0

    # 11. stable rep does NOT diverge, produces samples
    r2 = simulate_rep(1.0, 1.0, 0.0, 0, make_rng(999, 0, 1), Tsteps=T)
    checks["11_stable_no_div"] = (not r2["diverged"]) and r2["pcount"] == (T - BURN)

    # 12. digest reproducible on same dict
    checks["12_digest_repro"] = digest_of(res) == digest_of(res)

    # 13. twin evaluators agree
    v1 = evaluator_ifchain(res)
    v2 = evaluator_datadriven(res)
    checks["13_twin_agree"] = (v1 == v2)

    # 14. grid endpoints are 0.2 and 2.2
    checks["14_grid_endpoints"] = (K_GRID[0] == 0.2 and K_GRID[-1] == 2.2)

    # 15. G_CAP divergence detection triggers on clearly-unstable pole
    r3 = simulate_rep(2.5, 1.0, 0.0, 0, make_rng(999, 0, 2), Tsteps=1000)
    checks["15_gcap_detect"] = r3["diverged"]

    return checks


# ======================================================================================
# REPORT
# ======================================================================================
def fmt(x, nd=5):
    if x is None:
        return "   n/a  "
    return f"{x:.{nd}f}"


def print_report(res, digest1, digest2, checks):
    P = res["params"]
    print("=" * 90)
    print("VERDICT-108  /  PROPOSAL-095  --  rubber-band as proportional feedback controller")
    print("=" * 90)
    print("MODEL:  g(t+1) = g(t) + F - k*g(t-d) - beta*(g(t)-g(t-1)) + eps,  eps~N(0,sigma^2)")
    print(f"PARAMS: F={P['F_main']} (s={P['s_main']}), sigma={P['SIGMA']}, T={P['T']}, "
          f"burn={P['BURN']}, G_CAP={P['G_CAP']:.0e}, N_REPS={P['N_REPS']}, seed={P['SEED']}")
    print()

    print("-" * 90)
    print("MAIN base sweep (d=0, beta=0):  k | E(k) +/- se | lead_change | skill_fid | "
          "var_meas | var_analytic | div_frac")
    print("-" * 90)
    for k in K_GRID:
        r = res["per_k"][f"{k:.4f}"]
        print(f"  k={k:<5} | E={fmt(r['mean_E'])} +/-{fmt(r['se'],5)} | "
              f"lc={fmt(r['lead_change_rate'],4)} | sf={fmt(r['skill_fidelity'],4)} | "
              f"var={fmt(r['var_measured'],4)} | ana={fmt(r['var_analytic'],4)} | "
              f"div={fmt(r['diverged_frac'],3)}")
    print()

    # R1
    r1 = res["R1"]
    print("-" * 90)
    print(f"[R1] interior optimum beats both endpoints by >=3 sigma")
    print(f"     argmax k = {r1['argmax_k']}  E={fmt(r1['argmax_E'])} +/- {fmt(r1['argmax_se'],5)}  "
          f"interior={r1['interior']}")
    print(f"     endpoint k=0.2 : E={fmt(r1['endpoint_lo_E'])} +/- {fmt(r1['endpoint_lo_se'],5)}  "
          f"margin={fmt(r1['margin_lo_sigma'],2)} sigma")
    print(f"     endpoint k=2.2 : E={fmt(r1['endpoint_hi_E'])} +/- {fmt(r1['endpoint_hi_se'],5)}  "
          f"margin={fmt(r1['margin_hi_sigma'],2)} sigma")
    print(f"     R1 => {'PASS' if r1['pass'] else 'FAIL'}")
    print()

    # R2
    r2 = res["R2"]
    print("-" * 90)
    print(f"[R2] instability cliff at k=2 + variance formula")
    print(f"  (a) diverged_frac k=2.05={fmt(r2['R2a_div_2.05'],3)}  k=2.2={fmt(r2['R2a_div_2.2'],3)}"
          f"  => {'PASS' if r2['R2a_pass'] else 'FAIL'}")
    print(f"  (b) last-stable 1.95 E={fmt(r2['R2b_lastStable_1.95_E'])} vs first-above-2 2.05 "
          f"E={fmt(r2['R2b_first_2.05_E'])}  margin={fmt(r2['R2b_margin_sigma'],2)} sigma"
          f"  => {'PASS' if r2['R2b_pass'] else 'FAIL'}")
    print(f"  (c) Var(g) vs sigma^2/(k(2-k)) on stable arm:")
    for k in [kk for kk in K_GRID if kk < 2.0]:
        e = r2["R2c_rel_errs"][f"{k:.4f}"]
        print(f"        k={k:<5} meas={fmt(e['var_measured'],4)} ana={fmt(e['var_analytic'],4)} "
              f"rel_err={fmt(e['rel_err'],5)}")
    print(f"      max rel_err={fmt(r2['R2c_max_rel_err'],5)} (<0.05?)  => "
          f"{'PASS' if r2['R2c_pass'] else 'FAIL'}")
    cb = r2["cliff_bracket"]
    print(f"  cliff bracket: last_stable={cb['last_stable_k']} first_divergent={cb['first_divergent_k']}"
          f" (analytic boundary k=2)")
    print(f"     R2 => {'PASS' if r2['pass'] else 'FAIL'}")
    print()

    # R3
    r3 = res["R3"]
    print("-" * 90)
    print(f"[R3] delay d=1 : Jury boundary k=1 (HALVED from 2), interior argmax")
    cb = r3["cliff_bracket"]
    print(f"     boundary bracket: last_stable={cb['last_stable_k']} first_divergent={cb['first_divergent_k']}"
          f"  (predicted k=1)  ok={r3['boundary_halved_ok']}")
    print(f"     argmax k={r3['argmax_k']}  E={fmt(r3['argmax_E'])}  interior={r3['interior']}")
    print(f"     s-sweep argmax (s=0.3,0.5,0.7 -> F=0.6,1.0,1.4): {r3['s_sweep_argmax_vector']}"
          f"  all_interior={r3['all_s_interior']}")
    for key, v in r3["s_sweep"].items():
        print(f"        {key} F={v['F']}: argmax_k={v['argmax_k']} E={fmt(v['argmax_E'])} "
              f"interior={v['interior']}")
    print(f"     R3 => {'PASS' if r3['pass'] else 'FAIL'}")
    print()

    # R4
    r4a = res["R4a"]; r4b = res["R4b"]
    print("-" * 90)
    print(f"[R4] dual control")
    print(f"  (a) skill-off s=0 (F=0) collapses E: max|E| across grid = {fmt(r4a['max_absE'],5)}"
          f" (~0?)  => {'PASS' if r4a['pass'] else 'FAIL'}")
    sfsamp = r4a["per_k_skill_fidelity"]["1.0000"]
    print(f"        (skill_fidelity at k=1.0 with F=0 = {fmt(sfsamp,4)} ~ 0.5 as expected)")
    print(f"  (b) beta-sweep divergence onset vs k_crit=2-2*beta:")
    for key, v in r4b["table"].items():
        print(f"        {key:<10} predicted k_crit={v['k_crit_predicted']:<4} "
              f"measured bracket=({v['last_stable_k']}, {v['first_divergent_k']})  "
              f"ok={v['bracket_contains_predicted']}")
    print(f"     R4a => {'PASS' if r4a['pass'] else 'FAIL'}   "
          f"R4b => {'PASS' if r4b['pass'] else 'FAIL'}")
    print()

    # twin evaluators
    v1 = evaluator_ifchain(res)
    v2 = evaluator_datadriven(res)
    print("-" * 90)
    print(f"TWIN EVALUATORS: if-chain={v1}  data-driven={v2}  AGREE={v1 == v2}")
    print()

    # self-checks
    print("-" * 90)
    print(f"SELF-CHECKS ({sum(checks.values())}/{len(checks)} passed):")
    for name, ok in checks.items():
        print(f"     {'ok ' if ok else 'FAIL'} {name}")
    print()

    # determinism
    print("-" * 90)
    print(f"DETERMINISM DIGEST run#1 = {digest1}")
    print(f"DETERMINISM DIGEST run#2 = {digest2}")
    print(f"DIGESTS IDENTICAL = {digest1 == digest2}")
    print()

    print("=" * 90)
    verdict, gate = v1
    print(f"FINAL VERDICT: {verdict}" + (f"  (first failing gate: {gate})" if gate else ""))
    print("=" * 90)


# ======================================================================================
# MAIN
# ======================================================================================
def main():
    # Run the WHOLE compute twice; digests must be byte-identical.
    res1 = build_results()
    digest1 = digest_of(res1)
    res2 = build_results()
    digest2 = digest_of(res2)

    checks = run_self_checks(res1)

    # attach twin agreement + digest + self checks to the results dict, write files
    v1 = evaluator_ifchain(res1)
    v2 = evaluator_datadriven(res1)
    if v1 != v2:
        raise SystemExit(f"TWIN EVALUATOR DISAGREEMENT: {v1} vs {v2}")

    res1["twin_agreement"] = {"ifchain": list(v1), "datadriven": list(v2), "agree": v1 == v2}
    res1["self_checks"] = checks
    res1["sha256"] = digest1

    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "results.json"), "w") as f:
        json.dump(round_floats(res1), f, sort_keys=True, indent=2)
    with open(os.path.join(here, "fixtures.json"), "w") as f:
        json.dump({
            "world_constants": {
                "SEED": SEED, "SIGMA": SIGMA, "s_main": S_MAIN, "F_main": F_MAIN,
                "T": T, "BURN": BURN, "G_CAP": G_CAP, "N_REPS": N_REPS, "K_GRID": K_GRID,
                "dynamics": "g(t+1)=g(t)+F-k*g(t-d)-beta*(g(t)-g(t-1))+eps",
            },
            "rep0_anchor": {
                "k": 1.4, "beta": 0.0, "d": 0, "F": 1.0, "g0": 0.0,
                "eps_0_7": FIX_EPS, "g_1_8_expected": FIX_G,
                "g_1_8_computed": iterate_fixture(FIX_EPS, 1.4, 1.0, 0.0, 0),
            },
        }, f, sort_keys=True, indent=2)

    print_report(res1, digest1, digest2, checks)

    all_ok = all(checks.values()) and (digest1 == digest2)
    if not all_ok:
        raise SystemExit("SELF-CHECKS OR DETERMINISM FAILED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
