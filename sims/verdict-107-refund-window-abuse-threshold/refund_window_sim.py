#!/usr/bin/env python3
"""
VERDICT 107 - refund window as a conversion instrument (verifies idea-engine PROPOSAL 094, +13).

Independent stdlib-only reverification of the pre-registered claim:
  On the pinned world, net revenue is NON-MONOTONE in refund-window length W -
  safety-net conversion lift saturates while refund cost step-jumps once the
  window arms wardrobe abusers at W_abuse=14 - so the net-revenue-maximizing
  window is INTERIOR (W=13, the day before the wardrobe-extraction threshold).

PINNED WORLD (reproduced exactly from PROPOSAL 094 @ idea-engine 2026-07-17T09:48:38Z):
  W grid (idx 0..8): [0, 3, 6, 9, 12, 13, 14, 18, 30] days
  P=40.0, A=5000 product-views/rep
  conv(W) = c0 + dC*(1 - e^{-W/tau}); c0=0.030, dC=0.030, tau=6.0
  Per converted buyer: abuser w.p. phi=0.08; else dissatisfied w.p. d=0.20; else satisfied
  Honest dissatisfaction realized at t~Exp(rho=1/9 per day); refund iff t<=W  =>  P=1-e^{-rho*W}
  Wardrobe abuse refunds iff W>=W_abuse=14 (the step discontinuity)
  Refunded sale -> $0, kept -> P.  NR/rep = P*(n_buyers - n_refunds)
  N_REPS=400, SEED=20260717, string-keyed sha256-routed random.Random streams, stdlib-only.

PRE-REGISTERED RULE - APPROVE iff ALL hold, evaluated in order R1 -> R2 -> R3 -> R4:
  R1  argmax mean-netrev is INTERIOR (idx != 0, != 8) and beats BOTH W=0 and W=30 by >= 3 sigma
  R2  last-safe W=13 (idx5) outsells first-armed W=14 (idx6) by >= 3 sigma DESPITE higher conversion at W=14
  R3  argmax stays INTERIOR across phi in {0.06,0.07,0.08,0.09,0.10} and rho x {0.8,1.2} (7 sweep points)
  R4  with dC=0 (no conversion lift) argmax returns to W=0 by >= 3 sigma (folk monotone restored)

INDEPENDENT IMPLEMENTATION NOTE: this verifier aggregates the per-buyer Bernoulli/exponential
draws into exact binomial counts (sum-of-Bernoullis == Binomial; P(t<=W)=1-e^{-rho W}), sampled by
the geometric-gap method - semantically identical to the proposal's exact per-buyer draws but a
distinct code path. Gate OUTCOMES are what must agree; the results digest deliberately differs from
the proposal's c3cfdae... (disclosed independent reimplementation).
"""
import hashlib
import json
import math
import os
import random

# ----- pinned world -----
W_GRID = [0, 3, 6, 9, 12, 13, 14, 18, 30]
IDX_LAST_SAFE = 5    # W=13
IDX_FIRST_ARMED = 6  # W=14
P = 40.0
A = 5000
C0 = 0.030
DC = 0.030
TAU = 6.0
PHI = 0.08
DVAL = 0.20
RHO = 1.0 / 9.0
W_ABUSE = 14
N_REPS = 400
SEED = 20260717
MC_TOL = 0.015  # MC-vs-analytic reconciliation band (independent draws; observed reported in stdout)

HERE = os.path.dirname(os.path.abspath(__file__))


def conv(w, dc=DC):
    return C0 + dc * (1.0 - math.exp(-w / TAU))


def p_honest_refund(w, rho=RHO):
    return 1.0 - math.exp(-rho * w)


def make_rng(regime, rep):
    key = "%d:%s:%d" % (SEED, regime, rep)
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return random.Random(int.from_bytes(h, "big"))


def binomial(rng, n, p):
    """Exact Binomial(n, p) via geometric-gap sampling of Bernoulli successes. stdlib-only.

    Gap between successive successes is Geometric(p) on {1,2,...}; walk positions and
    count those <= n. Equivalent in distribution to summing n Bernoulli(p) draws.
    """
    if n <= 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    log_q = math.log1p(-p)  # ln(1-p) < 0
    count = 0
    pos = 0
    while True:
        u = rng.random()
        if u <= 0.0:
            u = 5e-324
        gap = 1 + int(math.log(u) / log_q)  # ceil of a positive value -> Geometric on {1,2,...}
        pos += gap
        if pos > n:
            break
        count += 1
    return count


def sim_window(regime, w, dc, phi, rho):
    cv = conv(w, dc)
    ph = p_honest_refund(w, rho)
    arms = (w >= W_ABUSE)
    total = 0.0
    total_sq = 0.0
    buyers_sum = 0
    refunds_sum = 0
    first_anchor = None
    for rep in range(N_REPS):
        rng = make_rng("%s:W%d" % (regime, w), rep)
        n_buyers = binomial(rng, A, cv)
        n_abuser = binomial(rng, n_buyers, phi)
        n_nonab = n_buyers - n_abuser
        n_dissat = binomial(rng, n_nonab, DVAL)
        abuse_ref = n_abuser if arms else 0
        honest_ref = binomial(rng, n_dissat, ph)
        n_ref = abuse_ref + honest_ref
        nr = P * (n_buyers - n_ref)
        total += nr
        total_sq += nr * nr
        buyers_sum += n_buyers
        refunds_sum += n_ref
        if rep == 0:
            first_anchor = {"n_buyers": n_buyers, "n_abuser": n_abuser,
                            "n_dissat": n_dissat, "n_refunds": n_ref, "netrev": nr}
    mean = total / N_REPS
    var = (total_sq - N_REPS * mean * mean) / (N_REPS - 1)
    if var < 0.0:
        var = 0.0
    se = math.sqrt(var / N_REPS)
    return {"W": w, "conv": cv, "p_honest": ph, "arms": arms,
            "mean_netrev": mean, "se": se,
            "buyers_mean": buyers_sum / float(N_REPS),
            "refunds_mean": refunds_sum / float(N_REPS),
            "first_anchor": first_anchor}


def analytic_netrev(w, dc=DC, phi=PHI, rho=RHO):
    cv = conv(w, dc)
    p_ref = phi * (1.0 if w >= W_ABUSE else 0.0) + (1.0 - phi) * DVAL * (1.0 - math.exp(-rho * w))
    return P * A * cv * (1.0 - p_ref)


def eval_grid(regime, dc=DC, phi=PHI, rho=RHO):
    return [sim_window(regime, w, dc, phi, rho) for w in W_GRID]


def argmax_idx(rows):
    best = 0
    for i in range(1, len(rows)):
        if rows[i]["mean_netrev"] > rows[best]["mean_netrev"]:
            best = i
    return best


def sigma_margin(a, b):
    denom = math.sqrt(a["se"] * a["se"] + b["se"] * b["se"])
    if denom <= 0.0:
        return float("inf")
    return (a["mean_netrev"] - b["mean_netrev"]) / denom


def compute():
    n_last = len(W_GRID) - 1

    # ---- R1: baseline interior optimum ----
    base = eval_grid("base")
    ai = argmax_idx(base)
    interior = (ai != 0 and ai != n_last)
    m_lo = sigma_margin(base[ai], base[0])
    m_hi = sigma_margin(base[ai], base[n_last])
    r1_pass = interior and (m_lo >= 3.0) and (m_hi >= 3.0)

    # ---- R2: abuse cliff, last-safe vs first-armed ----
    ls = base[IDX_LAST_SAFE]
    fa = base[IDX_FIRST_ARMED]
    m_r2 = sigma_margin(ls, fa)
    conv_higher_armed = (fa["conv"] > ls["conv"])
    r2_pass = (m_r2 >= 3.0) and conv_higher_armed

    # ---- R3: argmax interior across phi and rho sweep ----
    sweep = []
    for phi_s in [0.06, 0.07, 0.08, 0.09, 0.10]:
        g = eval_grid("r3phi_%03d" % int(round(phi_s * 1000)), dc=DC, phi=phi_s, rho=RHO)
        idx = argmax_idx(g)
        sweep.append({"kind": "phi", "value": phi_s, "argmax_idx": idx,
                      "argmax_W": W_GRID[idx], "interior": (idx != 0 and idx != n_last)})
    for rho_mult in [0.8, 1.2]:
        g = eval_grid("r3rho_%03d" % int(round(rho_mult * 100)), dc=DC, phi=PHI, rho=RHO * rho_mult)
        idx = argmax_idx(g)
        sweep.append({"kind": "rho_mult", "value": rho_mult, "argmax_idx": idx,
                      "argmax_W": W_GRID[idx], "interior": (idx != 0 and idx != n_last)})
    r3_pass = all(s["interior"] for s in sweep)

    # ---- R4: dC=0 knockout returns argmax to W=0 ----
    ko = eval_grid("r4knockout", dc=0.0)
    ko_ai = argmax_idx(ko)
    best_other = max((ko[i] for i in range(len(ko)) if i != 0),
                     key=lambda r: r["mean_netrev"])
    m_r4 = sigma_margin(ko[0], best_other)
    r4_pass = (ko_ai == 0) and (m_r4 >= 3.0)

    gates = {
        "R1": {"pass": r1_pass, "argmax_idx": ai, "argmax_W": W_GRID[ai], "interior": interior,
               "margin_vs_W0": m_lo, "margin_vs_W30": m_hi},
        "R2": {"pass": r2_pass, "margin": m_r2, "conv_higher_at_armed": conv_higher_armed,
               "conv_W13": ls["conv"], "conv_W14": fa["conv"],
               "netrev_W13": ls["mean_netrev"], "netrev_W14": fa["mean_netrev"]},
        "R3": {"pass": r3_pass, "sweep": sweep},
        "R4": {"pass": r4_pass, "argmax_idx": ko_ai, "argmax_W": W_GRID[ko_ai], "margin": m_r4},
    }
    return base, ko, gates


def evaluator_ifchain(gates):
    if not gates["R1"]["pass"]:
        return ("REJECT", "R1")
    if not gates["R2"]["pass"]:
        return ("REJECT", "R2")
    if not gates["R3"]["pass"]:
        return ("REJECT", "R3")
    if not gates["R4"]["pass"]:
        return ("REJECT", "R4")
    return ("APPROVE", None)


def evaluator_table(gates):
    for name in ("R1", "R2", "R3", "R4"):
        if not gates[name]["pass"]:
            return ("REJECT", name)
    return ("APPROVE", None)


def run_self_checks(base, gates):
    checks = []

    def chk(name, ok):
        checks.append({"name": name, "pass": bool(ok)})

    # 1 conv(0) == c0 exactly
    chk("conv(0)==c0", conv(0) == C0)
    # 2 conv strictly increasing across grid
    chk("conv-monotone-increasing", all(conv(W_GRID[i]) < conv(W_GRID[i + 1]) for i in range(len(W_GRID) - 1)))
    # 3 conv bounded above by c0+dC
    chk("conv-bounded-by-c0+dC", all(conv(w) < C0 + DC + 1e-12 for w in W_GRID))
    # 4 p_honest(0)==0
    chk("p_honest(0)==0", p_honest_refund(0) == 0.0)
    # 5 p_honest monotone increasing
    chk("p_honest-monotone", all(p_honest_refund(W_GRID[i]) <= p_honest_refund(W_GRID[i + 1]) for i in range(len(W_GRID) - 1)))
    # 6 MC vs analytic max rel-err within band
    max_rel = 0.0
    for row in base:
        an = analytic_netrev(row["W"])
        rel = abs(row["mean_netrev"] - an) / an
        if rel > max_rel:
            max_rel = rel
    chk("MC-vs-analytic-relerr<%.1f%%" % (MC_TOL * 100), max_rel < MC_TOL)
    # 7 baseline argmax interior (idx not endpoint)
    chk("baseline-argmax-interior", gates["R1"]["interior"])
    # 8 abuse arms exactly at W>=14 (W=13 off, W=14 on)
    chk("abuse-arms-at-W>=14", (base[IDX_LAST_SAFE]["arms"] is False) and (base[IDX_FIRST_ARMED]["arms"] is True))
    # 9 W=0 refunds ~ 0
    chk("W0-refunds~0", base[0]["refunds_mean"] < 0.5)
    # 10 all SE positive
    chk("all-SE-positive", all(r["se"] > 0.0 for r in base))
    # 11 buyers_mean ~ A*conv (rel-err < 2%)
    chk("buyers~A*conv", all(abs(r["buyers_mean"] - A * r["conv"]) / (A * r["conv"]) < 0.02 for r in base))
    # 12 ANALYTIC argmax interior & == W=13 (deterministic mechanism anchor)
    an_net = [analytic_netrev(w) for w in W_GRID]
    an_ai = max(range(len(W_GRID)), key=lambda i: an_net[i])
    chk("analytic-argmax==W13-interior", W_GRID[an_ai] == 13 and an_ai != 0 and an_ai != len(W_GRID) - 1)
    # 13 ANALYTIC R2: net(W13)>net(W14) while conv(14)>conv(13)
    chk("analytic-abuse-cliff", (analytic_netrev(13) > analytic_netrev(14)) and (conv(14) > conv(13)))
    # 14 ANALYTIC R4: dC=0 argmax returns to W=0
    an_ko = [analytic_netrev(w, dc=0.0) for w in W_GRID]
    an_ko_ai = max(range(len(W_GRID)), key=lambda i: an_ko[i])
    chk("analytic-knockout-argmax==W0", an_ko_ai == 0)
    # 15 twin evaluators agree
    chk("twins-agree", evaluator_ifchain(gates) == evaluator_table(gates))
    return checks, max_rel


def build_fixtures(base):
    return {
        "params": {"W_GRID": W_GRID, "P": P, "A": A, "C0": C0, "DC": DC, "TAU": TAU,
                   "PHI": PHI, "DVAL": DVAL, "RHO": RHO, "W_ABUSE": W_ABUSE,
                   "N_REPS": N_REPS, "SEED": SEED},
        "anchors": {
            "base_W13_rep0": base[IDX_LAST_SAFE]["first_anchor"],
            "base_W0_rep0": base[0]["first_anchor"],
            "analytic_netrev": {str(w): analytic_netrev(w) for w in W_GRID},
        },
    }


def fmt_report(base, gates, verdict, ffg, checks, max_rel, fixtures_sha):
    lines = []
    lines.append("=== VERDICT 107 - refund window as a conversion instrument (P094, +13) ===")
    lines.append("pinned world: W=%s P=%.1f A=%d conv=c0+dC(1-e^-W/tau) c0=%.3f dC=%.3f tau=%.1f"
                 % (W_GRID, P, A, C0, DC, TAU))
    lines.append("              phi=%.2f d=%.2f rho=1/9 W_abuse=%d | N_REPS=%d SEED=%d"
                 % (PHI, DVAL, W_ABUSE, N_REPS, SEED))
    lines.append("")
    lines.append("baseline grid (mean net revenue per rep +/- SE):")
    lines.append(" idx   W     conv    buyers   refunds       mean_netrev        SE")
    for i, r in enumerate(base):
        lines.append(" %2d  %4d  %.5f  %8.2f  %8.2f   %14.4f  %8.4f"
                     % (i, r["W"], r["conv"], r["buyers_mean"], r["refunds_mean"],
                        r["mean_netrev"], r["se"]))
    g1 = gates["R1"]
    lines.append("")
    lines.append("argmax: idx=%d W=%d (%s)" % (g1["argmax_idx"], g1["argmax_W"],
                                               "interior" if g1["interior"] else "ENDPOINT"))
    lines.append("")
    lines.append("R1 interior-optimum : %s  argmax W=%d beats W=0 by %.1f sigma and W=30 by %.1f sigma (need >=3, interior %s)"
                 % ("PASS" if g1["pass"] else "FAIL", g1["argmax_W"], g1["margin_vs_W0"], g1["margin_vs_W30"],
                    "OK" if g1["interior"] else "NO"))
    g2 = gates["R2"]
    lines.append("R2 abuse-cliff      : %s  W=13 nets %.2f vs W=14 %.2f by %.1f sigma; conv %.5f->%.5f (higher at W=14 %s)"
                 % ("PASS" if g2["pass"] else "FAIL", g2["netrev_W13"], g2["netrev_W14"], g2["margin"],
                    g2["conv_W13"], g2["conv_W14"], "OK" if g2["conv_higher_at_armed"] else "NO"))
    g3 = gates["R3"]
    sweep_desc = ", ".join("%s=%.2f->W%d%s" % (s["kind"], s["value"], s["argmax_W"],
                                               "" if s["interior"] else "(ENDPOINT!)")
                           for s in g3["sweep"])
    lines.append("R3 sweep-robust     : %s  argmax interior at all 7 sweep points: %s"
                 % ("PASS" if g3["pass"] else "FAIL", sweep_desc))
    g4 = gates["R4"]
    lines.append("R4 dC=0 knockout    : %s  argmax returns to W=%d by %.1f sigma (folk monotone restored)"
                 % ("PASS" if g4["pass"] else "FAIL", g4["argmax_W"], g4["margin"]))
    lines.append("")
    ic = evaluator_ifchain(gates)
    tb = evaluator_table(gates)
    lines.append("twin evaluators: if-chain=%s table=%s %s" % (ic, tb, "AGREE" if ic == tb else "DISAGREE"))
    npass = sum(1 for c in checks if c["pass"])
    lines.append("self-checks: %d/%d pass" % (npass, len(checks)))
    lines.append("MC-vs-analytic max rel-err: %.4f%% (band %.1f%%)" % (max_rel * 100, MC_TOL * 100))
    lines.append("fixtures.json sha256: %s" % fixtures_sha)
    lines.append("")
    lines.append("RULING: %s - first-failing-gate=%s" % (verdict, ffg))
    return "\n".join(lines) + "\n"


def main():
    base, ko, gates = compute()
    checks, max_rel = run_self_checks(base, gates)

    # twins
    ic = evaluator_ifchain(gates)
    tb = evaluator_table(gates)
    if ic != tb:
        raise SystemExit("TWIN DISAGREEMENT: ifchain=%s table=%s" % (ic, tb))
    verdict, ffg = ic

    # self-checks gate exit
    failed = [c["name"] for c in checks if not c["pass"]]
    if failed:
        raise SystemExit("SELF-CHECK FAILURE: %s" % failed)

    # fixtures: write-first / verify-thereafter, always byte-identical
    fixtures = build_fixtures(base)
    fx_bytes = json.dumps(fixtures, sort_keys=True, indent=2).encode("utf-8")
    fx_path = os.path.join(HERE, "fixtures.json")
    if os.path.exists(fx_path):
        with open(fx_path, "rb") as f:
            prior = f.read()
        if prior != fx_bytes:
            raise SystemExit("FIXTURE DRIFT: fixtures.json differs from committed anchor")
    with open(fx_path, "wb") as f:
        f.write(fx_bytes)
    fixtures_sha = hashlib.sha256(fx_bytes).hexdigest()

    # results.json
    results = {
        "verdict": verdict,
        "first_failing_gate": ffg,
        "world": {"W_GRID": W_GRID, "P": P, "A": A, "C0": C0, "DC": DC, "TAU": TAU,
                  "PHI": PHI, "DVAL": DVAL, "RHO": RHO, "W_ABUSE": W_ABUSE,
                  "N_REPS": N_REPS, "SEED": SEED},
        "baseline": [{"idx": i, "W": r["W"], "conv": r["conv"], "p_honest": r["p_honest"],
                      "arms": r["arms"], "mean_netrev": r["mean_netrev"], "se": r["se"],
                      "buyers_mean": r["buyers_mean"], "refunds_mean": r["refunds_mean"]}
                     for i, r in enumerate(base)],
        "knockout_dC0": [{"idx": i, "W": r["W"], "mean_netrev": r["mean_netrev"], "se": r["se"]}
                         for i, r in enumerate(ko)],
        "gates": gates,
        "twin": {"ifchain": list(ic), "table": list(tb), "agree": ic == tb},
        "self_checks": checks,
        "mc_vs_analytic_max_relerr": max_rel,
        "fixtures_sha256": fixtures_sha,
    }
    res_bytes = json.dumps(results, sort_keys=True, indent=2).encode("utf-8")
    res_path = os.path.join(HERE, "results.json")
    with open(res_path, "wb") as f:
        f.write(res_bytes)

    # run-stdout.txt (deterministic; no wall-clock)
    report = fmt_report(base, gates, verdict, ffg, checks, max_rel, fixtures_sha)
    out_path = os.path.join(HERE, "run-stdout.txt")
    with open(out_path, "wb") as f:
        f.write(report.encode("utf-8"))
    print(report, end="")


if __name__ == "__main__":
    main()
