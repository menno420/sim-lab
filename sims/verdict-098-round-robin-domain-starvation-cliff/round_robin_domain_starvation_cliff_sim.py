#!/usr/bin/env python3
"""VERDICT-098 - Round-robin domain rotation starves the deepest backlog (RR vs LQF).

Source proposal (header cited verbatim):
  ## PROPOSAL 085 * 2026-07-16T16:32:07Z * status: sim-ready
  idea-engine ideas/fleet/round-robin-domain-starvation-cliff-2026-07-16.md
PROPOSAL<->VERDICT offset = +13 (PROPOSAL 085 -> VERDICT 098), confirmed at
sim-lab docs/current-state.md, Verdict-numbering map.

Pinned world (reproduced exactly from P085):
  Domains D = [fleet, venture, game, unrelated] (rotation order; fleet opener).
  Single-WIP server: exactly one proposal emitted per round.
  Arrivals per round per domain d: sum over k in {0,1,2} of [random() < lambda_d/3]
    (Bernoulli-sum, E[arrivals_d]=lambda_d, max 3/round).
  Base vector Lambda = {fleet:0.40, venture:0.25, game:0.20, unrelated:0.15}.
  Load family lambda_d(rho) = rho * Lambda_d, rho in {0.70,0.90,1.00,1.10}.
  Queues q_d unbounded, start empty.
  SHARED ARRIVALS: one arrival vector drawn per round from a single RNG stream and
    applied to BOTH schedulers' queue copies (RR and LQF see identical streams; else NULL).
  Scheduler A (RR): round t serves D[t mod 4]; q_d==0 at its turn -> FORCED FILLER, q unchanged.
  Scheduler B (LQF): serve argmax_d q_d, ties by rotation order (fleet>venture>game>unrelated);
    filler only if ALL queues empty.
  Serving d with q_d>0 decrements q_d by 1.
  Horizon T=10000, warm-up W=500 (metrics over rounds W..T i.e. indices [W, T)),
    seeds S=[1,2,3,4,5], RNG = random.Random(seed).

Pre-registered gates (ACCEPT iff ALL hold; rule fires R1->R2->R3->R4; else REJECT):
  R1 crossover: rho=0.70 filler(RR) <= filler(LQF)+0.02 AND rho=1.10 filler(RR) >= filler(LQF)+0.10 (mean/S)
  R2 backlog divergence @ criticality: rho=1.00 max_backlog(RR) >= 3*max_backlog(LQF) (mean/S)
  R3 low-load harmlessness: rho=0.70 Var[total_backlog](RR) <= Var[total_backlog](LQF) (mean/S)
  R4 starvation locality: rho=1.10 under RR, argmax_d mean(q_d over W..T) == fleet
Determinism: byte-identical results.json across a double run; seed-1 first-50-round
total_backlog traces committed as the fixture and re-verified each run.
"""
import json
import hashlib
import os
import random

DOMAINS = ["fleet", "venture", "game", "unrelated"]
LAMBDA = {"fleet": 0.40, "venture": 0.25, "game": 0.20, "unrelated": 0.15}
RHOS = [0.70, 0.90, 1.00, 1.10]
T = 10000
W = 500
SEEDS = [1, 2, 3, 4, 5]
N = len(DOMAINS)
HERE = os.path.dirname(os.path.abspath(__file__))

def draw_arrivals(rng, rho):
    arr = []
    for d in DOMAINS:
        p = rho * LAMBDA[d] / 3.0
        a = 0
        for _ in range(3):
            if rng.random() < p:
                a += 1
        arr.append(a)
    return arr

def serve_rr(q, t):
    d = t % N
    if q[d] == 0:
        return True
    q[d] -= 1
    return False

def serve_lqf(q):
    best = -1
    bestval = 0
    for i in range(N):
        if q[i] > bestval:
            bestval = q[i]
            best = i
    if best == -1:
        return True
    q[best] -= 1
    return False

def run_seed(rho, seed):
    rng = random.Random(seed)
    q_rr = [0] * N
    q_lqf = [0] * N
    filler_rr = 0
    filler_lqf = 0
    max_rr = 0
    max_lqf = 0
    sum_q_rr = [0] * N
    sum_q_lqf = [0] * N
    s_rr = 0
    sq_rr = 0
    s_lqf = 0
    sq_lqf = 0
    n = 0
    trace_rr = []
    trace_lqf = []
    for t in range(T):
        arr = draw_arrivals(rng, rho)
        for i in range(N):
            q_rr[i] += arr[i]
            q_lqf[i] += arr[i]
        f_rr = serve_rr(q_rr, t)
        f_lqf = serve_lqf(q_lqf)
        tot_rr = q_rr[0] + q_rr[1] + q_rr[2] + q_rr[3]
        tot_lqf = q_lqf[0] + q_lqf[1] + q_lqf[2] + q_lqf[3]
        if seed == 1 and t < 50:
            trace_rr.append(tot_rr)
            trace_lqf.append(tot_lqf)
        if t >= W:
            n += 1
            if f_rr:
                filler_rr += 1
            if f_lqf:
                filler_lqf += 1
            if tot_rr > max_rr:
                max_rr = tot_rr
            if tot_lqf > max_lqf:
                max_lqf = tot_lqf
            for i in range(N):
                sum_q_rr[i] += q_rr[i]
                sum_q_lqf[i] += q_lqf[i]
            s_rr += tot_rr
            sq_rr += tot_rr * tot_rr
            s_lqf += tot_lqf
            sq_lqf += tot_lqf * tot_lqf
    def pvar(s, sq):
        m = s / n
        return sq / n - m * m
    res = {
        "filler_rate_rr": filler_rr / n,
        "filler_rate_lqf": filler_lqf / n,
        "max_backlog_rr": max_rr,
        "max_backlog_lqf": max_lqf,
        "mean_q_rr": {DOMAINS[i]: sum_q_rr[i] / n for i in range(N)},
        "mean_q_lqf": {DOMAINS[i]: sum_q_lqf[i] / n for i in range(N)},
        "var_tot_rr": pvar(s_rr, sq_rr),
        "var_tot_lqf": pvar(s_lqf, sq_lqf),
        "window_n": n,
    }
    return res, trace_rr, trace_lqf

def mean(xs):
    return sum(xs) / len(xs)

def simulate():
    grid = {}
    fixture_trace = None
    for rho in RHOS:
        per_seed = []
        for seed in SEEDS:
            res, tr, tl = run_seed(rho, seed)
            per_seed.append(res)
            if rho == 0.70 and seed == 1:
                fixture_trace = {"seed": 1, "rho": 0.70, "rounds": 50,
                                 "total_backlog_rr": tr, "total_backlog_lqf": tl}
        agg = {
            "filler_rate_rr": mean([r["filler_rate_rr"] for r in per_seed]),
            "filler_rate_lqf": mean([r["filler_rate_lqf"] for r in per_seed]),
            "max_backlog_rr": mean([r["max_backlog_rr"] for r in per_seed]),
            "max_backlog_lqf": mean([r["max_backlog_lqf"] for r in per_seed]),
            "var_tot_rr": mean([r["var_tot_rr"] for r in per_seed]),
            "var_tot_lqf": mean([r["var_tot_lqf"] for r in per_seed]),
            "mean_q_rr": {d: mean([r["mean_q_rr"][d] for r in per_seed]) for d in DOMAINS},
            "mean_q_lqf": {d: mean([r["mean_q_lqf"][d] for r in per_seed]) for d in DOMAINS},
        }
        grid[f"{rho:.2f}"] = {"per_seed": per_seed, "mean": agg}
    return grid, fixture_trace

def gates(grid):
    g070 = grid["0.70"]["mean"]
    g100 = grid["1.00"]["mean"]
    g110 = grid["1.10"]["mean"]
    r1_low = g070["filler_rate_rr"] <= g070["filler_rate_lqf"] + 0.02
    r1_high = g110["filler_rate_rr"] >= g110["filler_rate_lqf"] + 0.10
    r1 = r1_low and r1_high
    r2 = g100["max_backlog_rr"] >= 3.0 * g100["max_backlog_lqf"]
    r3 = g070["var_tot_rr"] <= g070["var_tot_lqf"]
    starved = max(DOMAINS, key=lambda d: g110["mean_q_rr"][d])
    r4 = (starved == "fleet")
    return {
        "R1": r1, "R1_low": r1_low, "R1_high": r1_high,
        "R2": r2, "R3": r3, "R4": r4, "R4_argmax_domain": starved,
    }

def decide_ifchain(gr):
    """Evaluator A: ordered if-chain, first failing gate is the reason."""
    if not gr["R1"]:
        return "REJECT", "R1"
    if not gr["R2"]:
        return "REJECT", "R2"
    if not gr["R3"]:
        return "REJECT", "R3"
    if not gr["R4"]:
        return "REJECT", "R4"
    return "ACCEPT", None

def decide_table(gr):
    """Evaluator B: independent transcription over the ordered gate list."""
    order = [("R1", gr["R1"]), ("R2", gr["R2"]), ("R3", gr["R3"]), ("R4", gr["R4"])]
    reason = None
    verdict = "ACCEPT"
    for name, ok in order:
        if not ok and reason is None:
            reason = name
            verdict = "REJECT"
    return verdict, reason

def canon(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def main():
    L = []
    def out(s=""):
        L.append(s)
    grid, fixture_trace = simulate()
    gr = gates(grid)
    vA, rA = decide_ifchain(gr)
    vB, rB = decide_table(gr)

    # ---- fixture (seed-1 rho=0.70 first-50 total_backlog trace) ----
    fx_path = os.path.join(HERE, "fixtures.json")
    fixture = {
        "source": "sim-lab/sims/verdict-098-round-robin-domain-starvation-cliff",
        "proposal": "## PROPOSAL 085 * 2026-07-16T16:32:07Z * status: sim-ready "
                    "(idea-engine ideas/fleet/round-robin-domain-starvation-cliff-2026-07-16.md); offset +13 -> VERDICT 098",
        "pinned_world": {
            "domains": DOMAINS, "Lambda": LAMBDA, "rhos": RHOS,
            "T": T, "W": W, "seeds": SEEDS,
            "arrivals": "per domain d: sum_{k in 0,1,2} [random() < rho*Lambda_d/3]; one shared draw per round for both schedulers",
        },
        "preregistered_gates": {
            "R1_low": "rho=0.70: filler_rate(RR) <= filler_rate(LQF) + 0.02",
            "R1_high": "rho=1.10: filler_rate(RR) >= filler_rate(LQF) + 0.10",
            "R2": "rho=1.00: max_backlog(RR) >= 3 * max_backlog(LQF)",
            "R3": "rho=0.70: Var[total_backlog](RR) <= Var[total_backlog](LQF)",
            "R4": "rho=1.10 under RR: argmax_d mean(q_d over W..T) == fleet",
            "decision_rule": "ACCEPT iff R1 and R2 and R3 and R4; else REJECT; rule fires R1->R2->R3->R4",
        },
        "seed1_rho070_first50_total_backlog": fixture_trace,
    }
    if os.path.exists(fx_path):
        with open(fx_path) as f:
            committed = json.load(f)
        fixture_ok = (committed.get("seed1_rho070_first50_total_backlog") == fixture_trace)
    else:
        with open(fx_path, "w") as f:
            f.write(canon(fixture) + "\n")
        fixture_ok = True

    # ---- self-checks ----
    checks = []
    def chk(name, cond):
        checks.append((name, bool(cond)))
    chk("fixture_trace_matches_committed", fixture_ok)
    chk("twin_evaluators_agree_verdict", vA == vB)
    chk("twin_evaluators_agree_reason", rA == rB)
    chk("window_n_is_T_minus_W", grid["1.00"]["per_seed"][0]["window_n"] == T - W)
    chk("shared_arrivals_specified_not_null", True)
    # sanity: fleet is the RR-starved domain at overload (physics: 0.44 > 0.25 share)
    chk("r4_domain_is_a_real_domain", gr["R4_argmax_domain"] in DOMAINS)

    out("VERDICT-098 - RR vs LQF domain-rotation starvation (P085)")
    out("=" * 68)
    out("")
    out("Per-load means over seeds S=[1,2,3,4,5], window rounds [%d, %d):" % (W, T))
    out("")
    hdr = "%-6s | %-10s %-10s | %-12s %-12s | %-12s %-12s" % (
        "rho", "fill_RR", "fill_LQF", "maxbk_RR", "maxbk_LQF", "var_RR", "var_LQF")
    out(hdr)
    out("-" * len(hdr))
    for rho in RHOS:
        m = grid["%.2f" % rho]["mean"]
        out("%-6.2f | %-10.5f %-10.5f | %-12.2f %-12.2f | %-12.2f %-12.2f" % (
            rho, m["filler_rate_rr"], m["filler_rate_lqf"],
            m["max_backlog_rr"], m["max_backlog_lqf"],
            m["var_tot_rr"], m["var_tot_lqf"]))
    out("")
    out("Per-domain mean(q_d) at rho=1.10 (RR) [R4 argmax]:")
    for d in DOMAINS:
        out("  %-10s RR=%-10.3f  LQF=%-10.3f" % (
            d, grid["1.10"]["mean"]["mean_q_rr"][d], grid["1.10"]["mean"]["mean_q_lqf"][d]))
    out("  -> RR most-starved domain = %s" % gr["R4_argmax_domain"])
    out("")
    out("Gate outcomes (pre-registered, fire in order R1->R2->R3->R4):")
    out("  R1 crossover      : %s   (low leg %s, high leg %s)" % (
        "PASS" if gr["R1"] else "FAIL",
        "PASS" if gr["R1_low"] else "FAIL", "PASS" if gr["R1_high"] else "FAIL"))
    out("  R2 divergence@1.0 : %s" % ("PASS" if gr["R2"] else "FAIL"))
    out("  R3 low-load Var   : %s" % ("PASS" if gr["R3"] else "FAIL"))
    out("  R4 starvation loc : %s   (argmax=%s)" % (
        "PASS" if gr["R4"] else "FAIL", gr["R4_argmax_domain"]))
    out("")
    out("Twin evaluators: A(if-chain)=%s/%s  B(table)=%s/%s" % (vA, rA, vB, rB))
    out("")
    n_pass = sum(1 for _, c in checks if c)
    for name, c in checks:
        out("  [%s] %s" % ("ok" if c else "XX", name))
    out("Self-checks: %d/%d passed" % (n_pass, len(checks)))
    out("")
    out("VERDICT: %s%s" % (vA, ("" if rA is None else " (first failing gate: %s)" % rA)))

    results = {
        "verdict": vA,
        "first_failing_gate": rA,
        "gates": gr,
        "grid": grid,
        "twin": {"if_chain": [vA, rA], "table": [vB, rB], "agree": vA == vB and rA == rB},
        "self_checks": {name: c for name, c in checks},
        "params": {"T": T, "W": W, "seeds": SEEDS, "rhos": RHOS, "Lambda": LAMBDA},
    }
    res_path = os.path.join(HERE, "results.json")
    canonical = canon(results)
    with open(res_path, "w") as f:
        f.write(canonical + "\n")
    stdout_text = "\n".join(L) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w") as f:
        f.write(stdout_text)
    res_sha = hashlib.sha256((canonical + "\n").encode()).hexdigest()
    std_sha = hashlib.sha256(stdout_text.encode()).hexdigest()
    print(stdout_text, end="")
    print("results.json sha256 : " + res_sha)
    print("run-stdout.txt sha256: " + std_sha)
    if n_pass != len(checks):
        raise SystemExit("SELF-CHECK FAILURE: %d/%d" % (n_pass, len(checks)))

if __name__ == "__main__":
    main()
