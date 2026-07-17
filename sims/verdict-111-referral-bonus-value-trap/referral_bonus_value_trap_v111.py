#!/usr/bin/env python3
"""
referral_bonus_value_trap_v111.py -- sim-lab VERDICT 111 (P098, offset +13).

Independent reimplementation of idea-engine PROPOSAL 098 ("the referral
bonus that maximizes viral coefficient R0 is strictly larger than the one
that maximizes profit"). This is NOT the proposal's disclosed verifier
(idea-engine ideas/venture-lab/referral_value_trap.py) -- own seed, own
offspring-generation method, own code structure. Reproduces the three
pre-registered gates (R1 anchor, R2 interior, R3 value-trap headline) from
the proposal doc, evaluated by two independent gate-logic evaluators
(if-chain and table-driven scan) that must agree.

Model (unchanged from the pre-registered spec -- this is what's being
verified, not what's being varied):
  Subcritical Galton-Watson referral cascade. Seed cohort S; each user makes
  K referral attempts, each converting with prob q(b) = q_max*(1-exp(-b/b0));
  offspring per user ~ Binomial(K, q(b)), R0(b) = K*q(b). Bonus b paid per
  successful referral. Pi(b) = S*(M - b*m(b))/(1 - m(b)).

Independence choices (deliberately different from the proposal's verifier):
  - Own SEED (427100, vs the proposal's disclosed 20260717).
  - Offspring drawn as K independent Bernoulli(q) trials summed per
    individual (a direct-count method), NOT a categorical draw from a
    pre-built Binomial CDF via bisect.
  - Own N=3000 replications per level (vs the proposal's N=2000).
  - Own analytic cross-check pass computed from first principles.

stdlib only: random, math, json, hashlib.
"""

import random
import math
import json
import hashlib

# ----------------------------------------------------------------------------
# Pinned world (from the proposal's pre-registered spec -- not ours to vary)
# ----------------------------------------------------------------------------
S = 1000            # seed cohort (generation 0)
K = 3                # referral attempts per user
Q_MAX = 0.25         # saturation prob per attempt
B0 = 2.0             # bonus half-saturation scale
M = 10.0             # net margin per signup
B_HI = 6.0           # bracketing high bonus for the interior-peak gate

GRID = [round(0.1 * i, 1) for i in range(0, 81)]   # 0.0 .. 8.0 step 0.1

# Independent run parameters (ours, not the proposal's)
SEED = 427100
N = 3000


def q_of_b(b):
    return Q_MAX * (1.0 - math.exp(-b / B0))


def m_of_b(b):
    return K * q_of_b(b)


def et_analytic(b):
    return S / (1.0 - m_of_b(b))


def pi_analytic(b):
    m = m_of_b(b)
    return S * (M - b * m) / (1.0 - m)


def find_b_star():
    profits = [pi_analytic(b) for b in GRID]
    idx = max(range(len(GRID)), key=lambda i: profits[i])
    return GRID[idx], idx, profits


def offspring_count(rng, q):
    """Binomial(K, q) via K independent Bernoulli(q) draws, summed.
    Deliberately different code path from a CDF/bisect categorical draw."""
    n = 0
    for _ in range(K):
        if rng.random() < q:
            n += 1
    return n


def simulate_one_cohort(rng, q):
    """One cohort replication -> total signups T (all generations incl. seed)."""
    total = S
    current = S
    while current > 0:
        nxt = 0
        for _ in range(current):
            nxt += offspring_count(rng, q)
        total += nxt
        current = nxt
    return total


def run_level(rng, b):
    q = q_of_b(b)
    sum_p = sum_p2 = 0.0
    sum_t = sum_t2 = 0.0
    for _ in range(N):
        T = simulate_one_cohort(rng, q)
        p = (M - b) * T + b * S
        sum_p += p
        sum_p2 += p * p
        sum_t += T
        sum_t2 += T * T
    mean_p = sum_p / N
    var_p = max((sum_p2 - N * mean_p * mean_p) / (N - 1), 0.0)
    se_p = math.sqrt(var_p / N)
    mean_t = sum_t / N
    var_t = max((sum_t2 - N * mean_t * mean_t) / (N - 1), 0.0)
    se_t = math.sqrt(var_t / N)
    return {
        "b": b, "q": q, "R0": m_of_b(b),
        "mean_profit": mean_p, "se_profit": se_p,
        "mean_T": mean_t, "se_T": se_t,
        "analytic_profit": pi_analytic(b), "analytic_ET": et_analytic(b),
    }


def z_diff(a, sea, b, seb):
    sd = math.sqrt(sea * sea + seb * seb)
    if sd == 0.0:
        return float("inf") if a != b else 0.0
    return (a - b) / sd


# ----------------------------------------------------------------------------
# Twin gate evaluators -- must agree on PASS/FAIL for every gate.
# Evaluator A: direct if-chain. Evaluator B: table-driven scan.
# ----------------------------------------------------------------------------
def evaluate_gates_ifchain(L0, Ls, Lh, Lv, b_star):
    z_r1 = abs(Ls["mean_T"] - et_analytic(b_star)) / Ls["se_T"] if Ls["se_T"] > 0 else 0.0
    r1 = z_r1 < 3.0
    z_r2a = z_diff(Ls["mean_profit"], Ls["se_profit"], L0["mean_profit"], L0["se_profit"])
    z_r2b = z_diff(Ls["mean_profit"], Ls["se_profit"], Lh["mean_profit"], Lh["se_profit"])
    r2 = (z_r2a >= 3.0) and (z_r2b >= 3.0)
    z_r3 = z_diff(Ls["mean_profit"], Ls["se_profit"], Lv["mean_profit"], Lv["se_profit"])
    r3 = z_r3 >= 3.0
    if not r1:
        first_fail = "R1"
    elif not r2:
        first_fail = "R2"
    elif not r3:
        first_fail = "R3"
    else:
        first_fail = None
    return {
        "R1": {"z": z_r1, "pass": r1},
        "R2": {"z_vs_zero": z_r2a, "z_vs_bhi": z_r2b, "pass": r2},
        "R3": {"z": z_r3, "pass": r3},
        "all_pass": r1 and r2 and r3,
        "first_failing_gate": first_fail,
    }


def evaluate_gates_table(L0, Ls, Lh, Lv, b_star):
    """Table-driven twin: same numeric inputs, scanned via a rule table
    instead of an if-chain, so a logic bug in one path is unlikely to be
    mirrored in the other."""
    rules = [
        ("R1", lambda: abs(Ls["mean_T"] - et_analytic(b_star)) / Ls["se_T"] if Ls["se_T"] > 0 else 0.0,
         lambda z: z < 3.0),
        ("R2a", lambda: z_diff(Ls["mean_profit"], Ls["se_profit"], L0["mean_profit"], L0["se_profit"]),
         lambda z: z >= 3.0),
        ("R2b", lambda: z_diff(Ls["mean_profit"], Ls["se_profit"], Lh["mean_profit"], Lh["se_profit"]),
         lambda z: z >= 3.0),
        ("R3", lambda: z_diff(Ls["mean_profit"], Ls["se_profit"], Lv["mean_profit"], Lv["se_profit"]),
         lambda z: z >= 3.0),
    ]
    rows = []
    first_fail = None
    for name, statfn, predicate in rules:
        z = statfn()
        ok = predicate(z)
        rows.append((name, z, ok))
        if not ok and first_fail is None:
            first_fail = name
    r1 = rows[0][2]
    r2 = rows[1][2] and rows[2][2]
    r3 = rows[3][2]
    # R1/R2 naming collapse to match the ifchain evaluator's gate grouping
    ff = None
    if not r1:
        ff = "R1"
    elif not r2:
        ff = "R2"
    elif not r3:
        ff = "R3"
    return {
        "rows": rows,
        "R1_pass": r1, "R2_pass": r2, "R3_pass": r3,
        "all_pass": r1 and r2 and r3,
        "first_failing_gate": ff,
    }


def main():
    rng = random.Random(SEED)

    b_star, star_idx, profits = find_b_star()
    b_viral = GRID[-1]
    b_zero = GRID[0]

    inc_ok = all(profits[i] <= profits[i + 1] + 1e-9 for i in range(0, star_idx))
    dec_ok = all(profits[i] >= profits[i + 1] - 1e-9 for i in range(star_idx, len(GRID) - 1))
    single_peaked = inc_ok and dec_ok
    interior = 0 < star_idx < len(GRID) - 1
    max_m = max(m_of_b(b) for b in GRID)
    subcritical = max_m < 1.0

    print("=" * 78)
    print("VERDICT 111 -- referral-bonus value trap (independent reimplementation)")
    print("=" * 78)
    print(f"own SEED={SEED} (proposal disclosed SEED=20260717 -- deliberately different)")
    print(f"own N={N} per level (proposal used N=2000)")
    print(f"b*={b_star} R0*={m_of_b(b_star):.6f}  b_viral={b_viral} R0_viral={m_of_b(b_viral):.6f}")
    print(f"subcritical(all m<1)={subcritical}  single_peaked={single_peaked}  interior={interior}")
    print()

    levels = {}
    for tag, b in [("b0", b_zero), ("bstar", b_star), ("bhi", B_HI), ("bviral", b_viral)]:
        levels[tag] = run_level(rng, b)
        r = levels[tag]
        print(f"  {tag:<7} b={b:>5}  mean_profit={r['mean_profit']:12.3f} (se {r['se_profit']:8.4f})  "
              f"mean_T={r['mean_T']:10.3f} (se {r['se_T']:7.4f})  "
              f"[analytic Pi={r['analytic_profit']:.3f} ET={r['analytic_ET']:.3f}]")

    L0, Ls, Lh, Lv = levels["b0"], levels["bstar"], levels["bhi"], levels["bviral"]

    gates_a = evaluate_gates_ifchain(L0, Ls, Lh, Lv, b_star)
    gates_b = evaluate_gates_table(L0, Ls, Lh, Lv, b_star)

    twins_agree = (
        gates_a["all_pass"] == gates_b["all_pass"]
        and gates_a["first_failing_gate"] == gates_b["first_failing_gate"]
    )

    print()
    print("=" * 78)
    print("PRE-REGISTERED GATES (evaluated by two independent evaluators)")
    print("=" * 78)
    print(f"  R1 branching-anchor MATCH: |z|={gates_a['R1']['z']:.2f}sigma < 3sigma -> "
          f"{'PASS' if gates_a['R1']['pass'] else 'FAIL'}")
    print(f"  R2 interior optimum: z_vs_zero={gates_a['R2']['z_vs_zero']:.2f}sigma, "
          f"z_vs_bhi={gates_a['R2']['z_vs_bhi']:.2f}sigma, both >=3sigma -> "
          f"{'PASS' if gates_a['R2']['pass'] else 'FAIL'}")
    print(f"  R3 value-trap headline: z={gates_a['R3']['z']:.2f}sigma >= 3sigma -> "
          f"{'PASS' if gates_a['R3']['pass'] else 'FAIL'}")
    print(f"  Evaluator A (if-chain)  all_pass={gates_a['all_pass']}  first_fail={gates_a['first_failing_gate']}")
    print(f"  Evaluator B (table)     all_pass={gates_b['all_pass']}  first_fail={gates_b['first_failing_gate']}")
    print(f"  TWINS AGREE: {twins_agree}")
    print()

    # ---- self-checks ----
    self_checks = []
    self_checks.append(("subcritical_all_grid", subcritical))
    self_checks.append(("single_peaked_analytic", single_peaked))
    self_checks.append(("b_star_strictly_interior", interior))
    self_checks.append(("b_star_matches_proposal_4_5", b_star == 4.5))
    self_checks.append(("b_viral_ne_b_star", b_viral != b_star))
    self_checks.append(("q_within_bounds_all_grid", all(0.0 <= q_of_b(b) <= Q_MAX for b in GRID)))
    self_checks.append(("b0_zero_profit_matches_analytic_exactly", abs(L0["mean_profit"] - L0["analytic_profit"]) < 1e-9))
    self_checks.append(("twins_agree_on_verdict", twins_agree))
    self_checks.append(("se_values_finite_nonneg", all(
        (r["se_profit"] >= 0.0) and (r["se_T"] >= 0.0) and math.isfinite(r["se_profit"]) and math.isfinite(r["se_T"])
        for r in (L0, Ls, Lh, Lv)
    )))
    n_pass = sum(1 for _, ok in self_checks if ok)
    print("SELF-CHECKS")
    for name, ok in self_checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"  {n_pass}/{len(self_checks)} self-checks pass")
    print()

    all_pass = gates_a["all_pass"] and twins_agree and (n_pass == len(self_checks))
    print(f"ALL GATES + TWINS + SELF-CHECKS PASS: {all_pass}")
    print("=" * 78)

    results = {
        "verdict": "V111", "proposal": "P098",
        "own_params": {"SEED": SEED, "N": N},
        "pinned_world": {
            "S": S, "K": K, "Q_MAX": Q_MAX, "B0": B0, "M": M, "B_HI": B_HI,
            "grid_min": GRID[0], "grid_max": GRID[-1], "grid_step": 0.1, "grid_n": len(GRID),
        },
        "analytic": {
            "b_star": b_star, "R0_star": m_of_b(b_star), "b_viral": b_viral, "R0_viral": m_of_b(b_viral),
            "subcritical": subcritical, "single_peaked": single_peaked, "interior": interior,
            "max_m_over_grid": max_m,
        },
        "sim": {k: {"b": v["b"], "mean_profit": v["mean_profit"], "se_profit": v["se_profit"],
                     "mean_T": v["mean_T"], "se_T": v["se_T"]} for k, v in levels.items()},
        "gates_evaluator_a": gates_a,
        "gates_evaluator_b": {"R1_pass": gates_b["R1_pass"], "R2_pass": gates_b["R2_pass"],
                               "R3_pass": gates_b["R3_pass"], "all_pass": gates_b["all_pass"],
                               "first_failing_gate": gates_b["first_failing_gate"]},
        "twins_agree": twins_agree,
        "self_checks": {name: ok for name, ok in self_checks},
        "self_checks_pass_count": n_pass,
        "self_checks_total": len(self_checks),
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    with open("results.json", "w") as fh:
        fh.write(canonical)

    print(f"\nResults JSON written to: results.json")
    print(f"Results-JSON sha256: {digest}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
