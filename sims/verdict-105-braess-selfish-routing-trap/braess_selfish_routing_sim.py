"""VERDICT 105 - Braess's paradox in selfish task routing (idea-engine PROPOSAL 092, +13)

Pinned world
------------
Nodes {S,A,B,T}. Directed legs & latencies (x_leg = fraction of N agents on that leg):
    S->A : congestion, latency = x_SA
    S->B : constant  latency = 1
    A->T : constant  latency = 1
    B->T : congestion, latency = x_BT
    A->B : shortcut, constant latency = s  (present only when network is "open")
Routes:
    P (top):    S->A->T            cost = x_SA + 1
    Q (bottom): S->B->T            cost = 1 + x_BT
    Z (cross):  S->A->B->T (open)  cost = x_SA + s + x_BT
Leg loads:  x_SA = f_P + f_Z ; x_BT = f_Q + f_Z.

Dynamics: agent-level stochastic logit with inertia, SIMULTANEOUS revision.
Pinned globals: N=1000, BETA=12.0, ALPHA=0.10, R=120, N_SEEDS=30,
SEED_BASE=20260719, SIG=3.0. Per-seed statistic = mean realized round latency
L(t) over the last 30 rounds (t=91..120). Across seeds report mean mu and
sample std (ddof=1) sigma_s. Two-sample z with denominator floored at 1e-12.

Pre-registered rule (fires IN ORDER, never softened)
----------------------------------------------------
R1 paradox      : at s=0, mu_open > mu_closed AND z >= SIG.
R2 dose-response: over s-grid {0.0..1.2} (13 pts), excess(s)=mu_open-mu_closed is
                  monotone non-increasing (max upward violation <= MONO_TOL) AND
                  significance z(s) crosses below SIG at an interior s* (0<s*<1.2).
R3 robustness   : 9 cells N in {250,500,1000} x BETA in {6,12,24}, each at s=0:
                  mu_open>mu_closed AND z>=SIG, all same sign.
R4 social opt   : planner minimizes mean latency over the route simplex with the
                  shortcut OPEN at s=0 (grid step 0.001). Pass iff optimal shortcut
                  flow f_Z*==0 AND M* <= mu_closed (+ tiny tol).
VERDICT = APPROVE iff R1 & R2 & R3 & R4, else REJECT with first-failing gate.

Twin evaluators; byte-identical double run; stdlib only.
"""

import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- pinned world
N = 1000
BETA = 12.0
ALPHA = 0.10
R = 120
N_SEEDS = 30
SEED_BASE = 20260719
SIG = 3.0

# pre-registered tolerances (documented, pre-registered before results were read)
MONO_TOL = 1e-2      # cross-seed mean-noise floor for a 1000-agent stochastic system
R4_M_TOL = 1e-6      # tiny slack for the social-optimum <= mu_closed comparison

S_GRID = [round(0.1 * k, 1) for k in range(13)]          # 0.0 .. 1.2
R3_NS = [250, 500, 1000]
R3_BETAS = [6.0, 12.0, 24.0]

WINDOW = 30          # last-30-rounds averaging window


# ------------------------------------------------------------------ simulation
def config_hash(open_net, s, n_agents, beta):
    """Pure deterministic hash of a simulation configuration."""
    key = "%d|%.6f|%d|%.6f" % (int(open_net), float(s), int(n_agents), float(beta))
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(h[:15], 16)          # < 2**60


def run_one_seed(rng, open_net, s, n_agents, beta, alpha, rounds):
    """Simulate one seed; return mean realized round latency over the last WINDOW rounds."""
    n_routes = 3 if open_net else 2
    assign = [rng.randrange(n_routes) for _ in range(n_agents)]
    rnd = rng.random
    last = []
    threshold_round = rounds - WINDOW + 1          # first round of averaging window
    inv_n = 1.0 / n_agents
    for t in range(1, rounds + 1):
        c0 = assign.count(0)
        c1 = assign.count(1)
        c2 = assign.count(2) if open_net else 0
        f_P = c0 * inv_n
        f_Q = c1 * inv_n
        f_Z = c2 * inv_n
        x_SA = f_P + f_Z
        x_BT = f_Q + f_Z
        cost_P = x_SA + 1.0
        cost_Q = 1.0 + x_BT
        cost_Z = x_SA + s + x_BT
        # realized round latency, pre-revision fractions & costs
        L = f_P * cost_P + f_Q * cost_Q + f_Z * cost_Z
        if t >= threshold_round:
            last.append(L)
        # logit distribution over available routes (subtract min cost for stability)
        if open_net:
            cmin = cost_P
            if cost_Q < cmin:
                cmin = cost_Q
            if cost_Z < cmin:
                cmin = cost_Z
            w0 = math.exp(-beta * (cost_P - cmin))
            w1 = math.exp(-beta * (cost_Q - cmin))
            w2 = math.exp(-beta * (cost_Z - cmin))
            wsum = w0 + w1 + w2
            p0 = w0 / wsum
            p01 = p0 + w1 / wsum
            for i in range(n_agents):
                if rnd() < alpha:
                    v = rnd()
                    if v < p0:
                        assign[i] = 0
                    elif v < p01:
                        assign[i] = 1
                    else:
                        assign[i] = 2
        else:
            cmin = cost_P if cost_P < cost_Q else cost_Q
            w0 = math.exp(-beta * (cost_P - cmin))
            w1 = math.exp(-beta * (cost_Q - cmin))
            p0 = w0 / (w0 + w1)
            for i in range(n_agents):
                if rnd() < alpha:
                    if rnd() < p0:
                        assign[i] = 0
                    else:
                        assign[i] = 1
    return sum(last) / len(last)


def simulate(open_net, s, n_agents, beta):
    """Run all seeds for a config; return (mu, sigma_s, per_seed_list)."""
    cfg = config_hash(open_net, s, n_agents, beta)
    stats = []
    for i in range(N_SEEDS):
        seed_i = SEED_BASE + i
        rng = random.Random((seed_i * 1000003 + cfg) % (2 ** 63))
        stats.append(run_one_seed(rng, open_net, s, n_agents, beta, ALPHA, R))
    mu = mean(stats)
    sd = sample_std(stats)
    return mu, sd, stats


# --------------------------------------------------------------------- stats
def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def zscore(mu_o, mu_c, sig_o, sig_c, n):
    denom = math.sqrt(sig_o * sig_o / n + sig_c * sig_c / n)
    if denom < 1e-12:
        denom = 1e-12
    return (mu_o - mu_c) / denom


# ------------------------------------------------------------ social optimum
def social_optimum(s):
    """Grid search (step 0.001) over the route simplex, shortcut open.
    Parametrise f_Z=z, f_P=(1-z)p, f_Q=(1-z)(1-p); full z x p grid (~1e6 evals)."""
    best_M = float("inf")
    best_p = 0.0
    best_z = 0.0
    for zi in range(0, 1001):
        z = zi / 1000.0
        onez = 1.0 - z
        for pi in range(0, 1001):
            p = pi / 1000.0
            f_P = onez * p
            f_Q = onez * (1.0 - p)
            f_Z = z
            x_SA = f_P + f_Z
            x_BT = f_Q + f_Z
            M = f_P * (x_SA + 1.0) + f_Q * (1.0 + x_BT) + f_Z * (x_SA + s + x_BT)
            if M < best_M:
                best_M = M
                best_p = p
                best_z = z
    return best_p, best_z, best_M


# --------------------------------------------------------------- twin evaluators
GATE_ORDER = ("R1", "R2", "R3", "R4")


def decide_ifchain(gates):
    if not gates["R1"]["passed"]:
        return ("REJECT", "R1")
    if not gates["R2"]["passed"]:
        return ("REJECT", "R2")
    if not gates["R3"]["passed"]:
        return ("REJECT", "R3")
    if not gates["R4"]["passed"]:
        return ("REJECT", "R4")
    return ("APPROVE", None)


def decide_table(gates):
    for g in GATE_ORDER:
        if not gates[g]["passed"]:
            return ("REJECT", g)
    return ("APPROVE", None)


# ---------------------------------------------------------------------- helpers
def rnd(x):
    """Round any float (recursively through containers) to 9 dp for byte-stable output."""
    if isinstance(x, bool):
        return x
    if isinstance(x, float):
        return round(x, 9)
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v) for v in x]
    return x


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fmt(x):
    return "%.6f" % x


# --------------------------------------------------------------------- main
def main():
    out = []

    def emit(line=""):
        out.append(line)

    # ---- closed baseline (N=1000, BETA=12); s-independent
    mu_closed, sig_closed, _ = simulate(False, 0.0, N, BETA)

    # ---- R2 dose-response (open at each s) + R1 (s=0 point)
    dose = []
    for s in S_GRID:
        mu_o, sig_o, _ = simulate(True, s, N, BETA)
        excess = mu_o - mu_closed
        z = zscore(mu_o, mu_closed, sig_o, sig_closed, N_SEEDS)
        dose.append({"s": s, "mu_open": mu_o, "sigma_open": sig_o,
                     "excess": excess, "z": z})

    d0 = dose[0]
    mu_open0 = d0["mu_open"]
    z0 = d0["z"]

    # R1
    r1_pass = (mu_open0 > mu_closed) and (z0 >= SIG)
    gate_R1 = {"passed": r1_pass, "mu_open": mu_open0, "mu_closed": mu_closed,
               "gap": mu_open0 - mu_closed, "z": z0}

    # R2a monotonicity: max upward violation of excess across the grid
    mono_violation = 0.0
    for i in range(1, len(dose)):
        up = dose[i]["excess"] - dose[i - 1]["excess"]
        if up > mono_violation:
            mono_violation = up
    mono_pass = mono_violation <= MONO_TOL

    # R2b interior threshold s*: first grid s with z < SIG, linear-interp crossing
    s_star = None
    for j in range(1, len(dose)):
        if dose[j]["z"] < SIG:
            z_prev = dose[j - 1]["z"]
            z_cur = dose[j]["z"]
            s_prev = dose[j - 1]["s"]
            s_cur = dose[j]["s"]
            denom = (z_cur - z_prev)
            if denom == 0:
                s_star = s_cur
            else:
                s_star = s_prev + (SIG - z_prev) * (s_cur - s_prev) / denom
            break
    threshold_pass = (s_star is not None) and (0.0 < s_star < 1.2)

    r2_pass = mono_pass and threshold_pass
    gate_R2 = {"passed": r2_pass, "passed_mono": mono_pass,
               "passed_threshold": threshold_pass, "mono_violation": mono_violation,
               "mono_tol": MONO_TOL, "s_star": s_star}

    # ---- R3 robustness (9 cells)
    r3_cells = []
    signs = []
    min_z = float("inf")
    all_pass = True
    for n_cell in R3_NS:
        for beta_cell in R3_BETAS:
            if n_cell == N and beta_cell == BETA:
                mo, so = mu_open0, dose[0]["sigma_open"]
                mc, sc = mu_closed, sig_closed
            else:
                mo, so, _ = simulate(True, 0.0, n_cell, beta_cell)
                mc, sc, _ = simulate(False, 0.0, n_cell, beta_cell)
            zc = zscore(mo, mc, so, sc, N_SEEDS)
            cell_pass = (mo > mc) and (zc >= SIG)
            signs.append(1 if (mo - mc) > 0 else (-1 if (mo - mc) < 0 else 0))
            if zc < min_z:
                min_z = zc
            if not cell_pass:
                all_pass = False
            r3_cells.append({"N": n_cell, "beta": beta_cell, "mu_open": mo,
                             "mu_closed": mc, "z": zc, "passed": cell_pass})
    all_same_sign = len(set(signs)) == 1 and signs[0] == 1
    r3_pass = all_pass and all_same_sign
    gate_R3 = {"passed": r3_pass, "all_same_sign": all_same_sign, "min_z": min_z,
               "n_cells_passed": sum(1 for c in r3_cells if c["passed"])}

    # ---- R4 social optimum (shortcut open, s=0)
    p_star, z_star, m_star = social_optimum(0.0)
    r4_zero_flow = (z_star == 0.0)
    r4_below = (m_star <= mu_closed + R4_M_TOL)
    r4_pass = r4_zero_flow and r4_below
    gate_R4 = {"passed": r4_pass, "p_star": p_star, "z_star": z_star,
               "m_star": m_star, "mu_closed": mu_closed}
    social = {"p_star": p_star, "z_star": z_star, "m_star": m_star,
              "mu_closed": mu_closed, "passed": r4_pass}

    gates = {"R1": gate_R1, "R2": gate_R2, "R3": gate_R3, "R4": gate_R4}

    # ---- twins
    ver_if, gate_if = decide_ifchain(gates)
    ver_tb, gate_tb = decide_table(gates)
    twins_agree = (ver_if == ver_tb) and (gate_if == gate_tb)
    if not twins_agree:
        raise SystemExit("twin disagreement: ifchain=%s table=%s" %
                         ((ver_if, gate_if), (ver_tb, gate_tb)))
    verdict = ver_if
    first_failing_gate = gate_if

    # ---- self-checks
    checks = []

    def chk(name, ok):
        checks.append({"name": name, "ok": bool(ok)})

    chk("closed_mu_approx_1.5", abs(mu_closed - 1.5) <= 0.02)
    chk("open_s0_gt_closed", mu_open0 > mu_closed)
    chk("z_s0_ge_SIG", z0 >= SIG)
    chk("R2_monotonic", mono_pass)
    chk("s_star_interior", threshold_pass)
    for c in r3_cells:
        chk("r3_cell_N%d_b%d_signif" % (c["N"], int(c["beta"])),
            c["passed"] and (c["mu_open"] > c["mu_closed"]))
    chk("R4_zero_shortcut_flow", r4_zero_flow)
    chk("R4_m_star_approx_1.5", abs(m_star - 1.5) <= 0.01)

    # determinism placeholder: two in-process runs of one seed identical stat
    cfg_det = config_hash(True, 0.0, N, BETA)
    seed_det = SEED_BASE + 0
    a = run_one_seed(random.Random((seed_det * 1000003 + cfg_det) % (2 ** 63)),
                     True, 0.0, N, BETA, ALPHA, R)
    b = run_one_seed(random.Random((seed_det * 1000003 + cfg_det) % (2 ** 63)),
                     True, 0.0, N, BETA, ALPHA, R)
    chk("determinism_in_process", a == b)

    chk("params_pinned", (N == 1000 and BETA == 12.0 and ALPHA == 0.10 and
                          R == 120 and SEED_BASE == 20260719 and SIG == 3.0))
    chk("twins_agree", twins_agree)

    self_checks_passed = sum(1 for c in checks if c["ok"])
    self_checks_total = len(checks)
    all_self_checks_pass = self_checks_passed == self_checks_total

    # ---- fixtures drift guard
    fx = {
        "params": {"N": N, "BETA": BETA, "ALPHA": ALPHA, "R": R,
                   "N_SEEDS": N_SEEDS, "SEED_BASE": SEED_BASE, "SIG": SIG},
        "anchors": rnd({"mu_closed": mu_closed, "mu_open_s0": mu_open0,
                        "s_star": s_star if s_star is not None else -1.0,
                        "r4_z_star": z_star}),
    }
    fx_text = json.dumps(fx, sort_keys=True, indent=2) + "\n"
    fx_path = os.path.join(HERE, "fixtures.json")
    if os.path.exists(fx_path):
        with open(fx_path, "r") as fh:
            committed = fh.read()
        if committed != fx_text:
            raise SystemExit("fixture drift: committed fixtures.json != recomputed")
    else:
        with open(fx_path, "w") as fh:
            fh.write(fx_text)
    fixtures_sha256 = sha256_file(fx_path)

    # ---- build stdout
    emit("VERDICT 105 - Braess's paradox in selfish task routing "
         "(idea-engine PROPOSAL 092, +13)")
    emit("world: N=%d BETA=%s ALPHA=%s R=%d N_SEEDS=%d SEED_BASE=%d SIG=%s "
         "MONO_TOL=%s" % (N, BETA, ALPHA, R, N_SEEDS, SEED_BASE, SIG, MONO_TOL))
    emit("")
    emit("R1  paradox @ s=0 : mu_open=%s mu_closed=%s gap=%s z=%s  -> %s" %
         (fmt(mu_open0), fmt(mu_closed), fmt(mu_open0 - mu_closed), fmt(z0),
          "PASS" if r1_pass else "FAIL"))
    emit("")
    emit("dose-response (open vs closed, mu_closed=%s)" % fmt(mu_closed))
    emit("   s   mu_open   sigma_open    excess         z")
    for d in dose:
        emit("%5.1f  %8s  %10s  %8s  %10s" %
             (d["s"], fmt(d["mu_open"]), fmt(d["sigma_open"]),
              fmt(d["excess"]), fmt(d["z"])))
    emit("R2a max upward excess violation = %s (tol %s) -> %s" %
         (fmt(mono_violation), MONO_TOL, "PASS" if mono_pass else "FAIL"))
    emit("R2b interior s* = %s -> %s" %
         (fmt(s_star) if s_star is not None else "none",
          "PASS" if threshold_pass else "FAIL"))
    emit("")
    emit("R3 robustness (9 cells, s=0)")
    emit("     N  beta   mu_open  mu_closed          z  pass")
    for c in r3_cells:
        emit("%6d  %4d  %8s  %9s  %10s  %s" %
             (c["N"], int(c["beta"]), fmt(c["mu_open"]), fmt(c["mu_closed"]),
              fmt(c["z"]), "Y" if c["passed"] else "N"))
    emit("R3 all_same_sign=%s min_z=%s -> %s" %
         (all_same_sign, fmt(min_z), "PASS" if r3_pass else "FAIL"))
    emit("")
    emit("R4 social optimum @ s=0 : p*=%s f_Z*(z*)=%s M*=%s (mu_closed=%s) -> %s" %
         (fmt(p_star), fmt(z_star), fmt(m_star), fmt(mu_closed),
          "PASS" if r4_pass else "FAIL"))
    emit("")
    emit("gates:")
    for g in GATE_ORDER:
        emit("  %s passed=%s" % (g, gates[g]["passed"]))
    emit("")
    emit("twins: ifchain=%s table=%s agree=%s" %
         ((ver_if, gate_if), (ver_tb, gate_tb), twins_agree))
    emit("")
    emit("self-checks %d/%d" % (self_checks_passed, self_checks_total))
    for c in checks:
        emit("  [%s] %s" % ("ok" if c["ok"] else "XX", c["name"]))
    emit("")

    # ---- results.json
    results = {
        "verdict": verdict,
        "first_failing_gate": first_failing_gate,
        "world": {"N": N, "BETA": BETA, "ALPHA": ALPHA, "R": R,
                  "N_SEEDS": N_SEEDS, "SEED_BASE": SEED_BASE, "SIG": SIG,
                  "MONO_TOL": MONO_TOL, "R4_M_TOL": R4_M_TOL, "s_grid": S_GRID},
        "gates": gates,
        "dose_response": dose,
        "r3_cells": r3_cells,
        "social": social,
        "twin": {"agree": twins_agree, "ifchain": [ver_if, gate_if],
                 "table": [ver_tb, gate_tb]},
        "self_checks": checks,
        "self_checks_passed": self_checks_passed,
        "self_checks_total": self_checks_total,
        "fixtures_sha256": fixtures_sha256,
    }
    results_text = json.dumps(rnd(results), sort_keys=True, indent=2) + "\n"
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        fh.write(results_text)

    results_sha = sha256_file(os.path.join(HERE, "results.json"))
    emit("sha256 fixtures.json = %s" % fixtures_sha256)
    emit("sha256 results.json  = %s" % results_sha)
    emit("")
    emit("RULING: %s (first-failing gate: %s)" %
         (verdict, first_failing_gate if first_failing_gate else "none"))

    stdout_text = "\n".join(out) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w") as fh:
        fh.write(stdout_text)
    print(stdout_text, end="")

    # ---- exit contract
    if not (all_self_checks_pass and twins_agree):
        raise SystemExit("self-checks or twins failed: %d/%d, twins=%s" %
                         (self_checks_passed, self_checks_total, twins_agree))


if __name__ == "__main__":
    main()
