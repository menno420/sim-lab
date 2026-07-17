#!/usr/bin/env python3
"""
VERDICT 103 - big-pond badge-starvation inversion (idea-engine PROPOSAL 090, +13).

Independent stdlib-only hermetic simulation. Source proposal header
(idea-engine control/outbox.md, PROPOSAL 090 . 2026-07-17T02:45:45Z . sim-ready):

  On the pinned world - C=9 browse categories, T=[800,1000,1200,1400,1600,1800,
  2000,2200,2400] browse/day, p0=0.01, v0=5.0/day, badge lift b=1.5 (effective
  conv = p0*(1+b*badge)), committed rank-K competition g=[6,9,13,18,24,31,39,48,58],
  badge_c=1 iff v0+T_c*p0 >= g_c (-> badge=[1,1,1,1,0,0,0,0,0], crossover at
  index 4), H=90, N_REPS=400, SEED=20260717, exact Poisson thinning - does placing
  a single title in the maximum-audience category get DOMINATED by an interior pond?

Model. Daily sales in category c = baseline Poisson(v0) + browse conversions.
The browse stream is Poisson(T_c) arrivals thinned at per-browse probability
p_eff = p0*(1+b*badge_c); the exact thinning of a Poisson stream is itself
Poisson(T_c*p_eff). Baseline and conversions are independent Poissons, so the
day's total sales ~ Poisson(v0 + T_c*p_eff), drawn directly. Horizon total over
H days = sum of H independent daily draws.

Badge is earned, not given: badge_c=1 iff the un-badged expected daily rate
(v0 + T_c*p0) meets or beats the committed rank-K competition g_c. Where
competition rises faster than traffic the badge is unattainable, so the
multiplicative conversion lift never applies and the biggest pond starves.

Pre-registered decision rule (APPROVE iff ALL):
  R1  argmax mean-sales is interior (index != 8) AND beats index 8 by >= 3 sigma.
  R2  last-badged pond (idx 3) outsells first-unbadged pond (idx 4) by >= 3 sigma
      despite idx 4 carrying more browse traffic.
  R3  argmax stays interior across b in {1.0,1.25,1.5,1.75,2.0} (nominal g) and
      across g x {0.9,1.1} (nominal b) - the union of the two 1-D sweeps.
  R4  with b=0 (badge off) argmax returns to index 8 (max audience) by >= 3 sigma.

Twin evaluators (ordered if-chain + independent table scan) must agree on the
verdict token AND the first-failing gate, else SystemExit.

Determinism: one random.Random per (regime,rep,category), seeded from
int.from_bytes(sha256(f"{SEED}:{regime}:{rep}:{cat}").digest()[:8]). Byte-identical
across a double run. stdlib only.
"""

import hashlib
import json
import math
import os
import random

# ---- pinned world (committed; reproduces idea-engine PROPOSAL 090) ----
C = 9
T = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400]
P0 = 0.01
V0 = 5.0
B_NOMINAL = 1.5
G = [6, 9, 13, 18, 24, 31, 39, 48, 58]
H = 90
N_REPS = 400
SEED = 20260717
MAX_AUDIENCE = C - 1          # index 8
LAST_BADGED = 3
FIRST_UNBADGED = 4
SIGMA_MIN = 3.0

B_SWEEP = [1.0, 1.25, 1.5, 1.75, 2.0]
G_SCALE_SWEEP = [0.9, 1.1]

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------- stdlib statistics -------------------------------
def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def pool(xs):
    m = mean(xs)
    sd = sample_std(xs)
    return {"mean": m, "sd": sd, "se": sd / math.sqrt(len(xs))}


def separation(a, b):
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2)
    return (a["mean"] - b["mean"]) / se if se > 0 else float("inf")


# ------------------------- deterministic RNG streams --------------------------
def stream(regime, rep, cat):
    key = "{}:{}:{}:{}".format(SEED, regime, rep, cat)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], "big")
    return random.Random(seed)


def poisson(rng, lam):
    # Knuth's exact algorithm; per-day lam stays small (<= ~80).
    if lam <= 0.0:
        return 0
    limit = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= limit:
            return k - 1


# ------------------------------- the model ------------------------------------
def badge_vector(g_scale):
    thr = [g_scale * g for g in G]
    return [1 if (V0 + T[c] * P0) >= thr[c] else 0 for c in range(C)]


def daily_rate(c, b, badge):
    p_eff = P0 * (1.0 + b * badge[c])
    return V0 + T[c] * p_eff


def simulate(regime, b, g_scale, badge_off=False):
    badge = [0] * C if badge_off else badge_vector(g_scale)
    per_cat = [[] for _ in range(C)]
    for rep in range(N_REPS):
        for c in range(C):
            rng = stream(regime, rep, c)
            lam = daily_rate(c, b, badge)
            s = 0
            for _day in range(H):
                s += poisson(rng, lam)
            per_cat[c].append(s)
    pooled = [pool(per_cat[c]) for c in range(C)]
    return {"badge": badge, "pooled": pooled, "first_rep": [per_cat[c][0] for c in range(C)]}


def argmax_mean(pooled):
    best = 0
    for c in range(1, C):
        if pooled[c]["mean"] > pooled[best]["mean"]:
            best = c
    return best


# --------------------------------- gates --------------------------------------
def compute_gates():
    main = simulate("main", B_NOMINAL, 1.0)
    control = simulate("control", 0.0, 1.0, badge_off=True)
    bsweep = {b: simulate("bsweep:{}".format(b), b, 1.0) for b in B_SWEEP}
    gsweep = {gs: simulate("gsweep:{}".format(gs), B_NOMINAL, gs) for gs in G_SCALE_SWEEP}

    mp = main["pooled"]
    am = argmax_mean(mp)
    r1_sep = separation(mp[am], mp[MAX_AUDIENCE])
    R1 = (am != MAX_AUDIENCE) and (r1_sep >= SIGMA_MIN)

    r2_sep = separation(mp[LAST_BADGED], mp[FIRST_UNBADGED])
    R2 = (r2_sep >= SIGMA_MIN) and (T[FIRST_UNBADGED] > T[LAST_BADGED])

    r3_points = []
    for b in B_SWEEP:
        a = argmax_mean(bsweep[b]["pooled"])
        r3_points.append({"label": "b={}".format(b), "argmax": a, "interior": a != MAX_AUDIENCE})
    for gs in G_SCALE_SWEEP:
        a = argmax_mean(gsweep[gs]["pooled"])
        r3_points.append({"label": "g*{}".format(gs), "argmax": a, "interior": a != MAX_AUDIENCE})
    R3 = all(p["interior"] for p in r3_points)

    cp = control["pooled"]
    cam = argmax_mean(cp)
    runner = max((c for c in range(C) if c != MAX_AUDIENCE), key=lambda c: cp[c]["mean"])
    r4_sep = separation(cp[MAX_AUDIENCE], cp[runner])
    R4 = (cam == MAX_AUDIENCE) and (r4_sep >= SIGMA_MIN)

    return {
        "main": main, "control": control,
        "R1": {"passed": R1, "argmax": am, "beats_index": MAX_AUDIENCE, "sep_sigma": r1_sep},
        "R2": {"passed": R2, "last_badged": LAST_BADGED, "first_unbadged": FIRST_UNBADGED,
               "sep_sigma": r2_sep, "traffic_more_at_unbadged": T[FIRST_UNBADGED] > T[LAST_BADGED]},
        "R3": {"passed": R3, "points": r3_points},
        "R4": {"passed": R4, "argmax": cam, "runner_up": runner, "sep_sigma": r4_sep},
    }


# ---------------------------- twin evaluators ---------------------------------
def decide_ifchain(g):
    if not g["R1"]["passed"]:
        return "REJECT", "R1"
    if not g["R2"]["passed"]:
        return "REJECT", "R2"
    if not g["R3"]["passed"]:
        return "REJECT", "R3"
    if not g["R4"]["passed"]:
        return "REJECT", "R4"
    return "APPROVE", None


def decide_table(g):
    first_fail = None
    for name in ("R1", "R2", "R3", "R4"):
        if not g[name]["passed"]:
            first_fail = name
            break
    return ("APPROVE" if first_fail is None else "REJECT"), first_fail


# ------------------------------ fixtures --------------------------------------
def build_fixture(g):
    canon = stream("main", 0, 0)
    draws = [canon.random() for _ in range(8)]
    fx = {
        "seed": SEED, "C": C, "T": T, "p0": P0, "v0": V0, "b_nominal": B_NOMINAL,
        "g": G, "H": H, "n_reps": N_REPS,
        "badge_nominal": g["main"]["badge"],
        "badge_g_lo": badge_vector(0.9), "badge_g_hi": badge_vector(1.1),
        "main_first_rep_totals": g["main"]["first_rep"],
        "canonical_stream_first8": draws,
    }
    path = os.path.join(HERE, "fixtures.json")
    if os.path.exists(path):
        with open(path) as fh:
            committed = json.load(fh)
        if committed != fx:
            raise SystemExit("fixture drift: committed fixtures.json != recomputed anchors")
        return path, False
    with open(path, "w") as fh:
        fh.write(json.dumps(fx, sort_keys=True, indent=2) + "\n")
    return path, True


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# --------------------------------- main ---------------------------------------
def main():
    g = compute_gates()
    if_tok, if_ff = decide_ifchain(g)
    tb_tok, tb_ff = decide_table(g)
    twins_agree = (if_tok == tb_tok) and (if_ff == tb_ff)
    if not twins_agree:
        raise SystemExit("twin disagreement: ifchain={}/{} table={}/{}".format(if_tok, if_ff, tb_tok, tb_ff))
    verdict, first_fail = if_tok, if_ff

    mp = g["main"]["pooled"]
    cp = g["control"]["pooled"]
    badge = g["main"]["badge"]

    self_checks = []

    def chk(name, ok):
        self_checks.append({"name": name, "ok": bool(ok)})

    chk("badge_vector == [1,1,1,1,0,0,0,0,0]", badge == [1, 1, 1, 1, 0, 0, 0, 0, 0])
    chk("crossover_index == 4", (badge.index(0) if 0 in badge else -1) == 4)
    chk("main argmax interior", g["R1"]["argmax"] != MAX_AUDIENCE)
    chk("main argmax == last_badged idx3", g["R1"]["argmax"] == LAST_BADGED)
    chk("R1 passed", g["R1"]["passed"])
    chk("R1 sep >= 3", g["R1"]["sep_sigma"] >= SIGMA_MIN)
    chk("R2 passed", g["R2"]["passed"])
    chk("R2 unbadged pond has more traffic", T[FIRST_UNBADGED] > T[LAST_BADGED])
    chk("R2 sep >= 3", g["R2"]["sep_sigma"] >= SIGMA_MIN)
    chk("R3 all sweep points interior (7)", g["R3"]["passed"] and len(g["R3"]["points"]) == 7)
    chk("R4 control argmax == max-audience idx8", g["R4"]["argmax"] == MAX_AUDIENCE)
    chk("R4 sep >= 3", g["R4"]["sep_sigma"] >= SIGMA_MIN)
    chk("control badge all zero", g["control"]["badge"] == [0] * C)
    chk("twins agree", twins_agree)

    all_pass = all(c["ok"] for c in self_checks)

    fx_path, fx_written = build_fixture(g)
    fx_sha = sha256_file(fx_path)

    results = {
        "verdict": verdict,
        "first_failing_gate": first_fail,
        "world": {"C": C, "T": T, "p0": P0, "v0": V0, "b_nominal": B_NOMINAL, "g": G,
                  "H": H, "n_reps": N_REPS, "seed": SEED, "badge": badge,
                  "crossover_index": 4, "max_audience_index": MAX_AUDIENCE},
        "per_category": [
            {"index": c, "T": T[c], "badge": badge[c],
             "mean": mp[c]["mean"], "sd": mp[c]["sd"], "se": mp[c]["se"]} for c in range(C)],
        "control_per_category": [
            {"index": c, "T": T[c], "badge": g["control"]["badge"][c],
             "mean": cp[c]["mean"], "sd": cp[c]["sd"], "se": cp[c]["se"]} for c in range(C)],
        "gates": {
            "R1": {"passed": g["R1"]["passed"], "argmax": g["R1"]["argmax"],
                   "beats_index": MAX_AUDIENCE, "sep_sigma": g["R1"]["sep_sigma"]},
            "R2": {"passed": g["R2"]["passed"], "last_badged": LAST_BADGED,
                   "first_unbadged": FIRST_UNBADGED, "sep_sigma": g["R2"]["sep_sigma"],
                   "traffic_more_at_unbadged": g["R2"]["traffic_more_at_unbadged"]},
            "R3": {"passed": g["R3"]["passed"], "points": g["R3"]["points"]},
            "R4": {"passed": g["R4"]["passed"], "argmax": g["R4"]["argmax"],
                   "runner_up": g["R4"]["runner_up"], "sep_sigma": g["R4"]["sep_sigma"]},
        },
        "twin": {"ifchain": [if_tok, if_ff], "table": [tb_tok, tb_ff], "agree": twins_agree},
        "self_checks": self_checks,
        "self_checks_passed": sum(1 for c in self_checks if c["ok"]),
        "self_checks_total": len(self_checks),
        "fixtures_sha256": fx_sha,
    }

    res_path = os.path.join(HERE, "results.json")
    with open(res_path, "w") as fh:
        fh.write(json.dumps(results, sort_keys=True, indent=2) + "\n")
    res_sha = sha256_file(res_path)

    lines = []
    lines.append("VERDICT 103 - big-pond badge-starvation inversion (P090, +13)")
    lines.append("pinned world: C=%d T=%s p0=%s v0=%s b=%s H=%d N_REPS=%d SEED=%d" % (
        C, T, P0, V0, B_NOMINAL, H, N_REPS, SEED))
    lines.append("badge vector: %s (crossover index 4)" % badge)
    lines.append("")
    lines.append("per-category horizon sales (H=%d, %d reps):" % (H, N_REPS))
    lines.append("  idx   T  badge        mean        se")
    for c in range(C):
        tag = ""
        if c == g["R1"]["argmax"]:
            tag = "  <- argmax"
        elif c == MAX_AUDIENCE:
            tag = "  <- max-audience"
        lines.append("  %2d %5d    [%d]  %10.3f %9.4f%s" % (c, T[c], badge[c], mp[c]["mean"], mp[c]["se"], tag))
    lines.append("")
    lines.append("control (b=0): argmax idx%d mean %.3f (folk monotone)" % (g["R4"]["argmax"], cp[g["R4"]["argmax"]]["mean"]))
    lines.append("")
    lines.append("gates:")
    lines.append("  R1 interior-dominates : %s  argmax idx%d beats idx%d by %.1f sigma" % (
        g["R1"]["passed"], g["R1"]["argmax"], MAX_AUDIENCE, g["R1"]["sep_sigma"]))
    lines.append("  R2 badge-cliff        : %s  idx%d > idx%d by %.1f sigma (idx%d has more traffic)" % (
        g["R2"]["passed"], LAST_BADGED, FIRST_UNBADGED, g["R2"]["sep_sigma"], FIRST_UNBADGED))
    lines.append("  R3 robust-interior    : %s  %s" % (
        g["R3"]["passed"], " ".join("%s->idx%d" % (p["label"], p["argmax"]) for p in g["R3"]["points"])))
    lines.append("  R4 badge-off-control  : %s  argmax idx%d by %.1f sigma" % (
        g["R4"]["passed"], g["R4"]["argmax"], g["R4"]["sep_sigma"]))
    lines.append("")
    lines.append("twins: ifchain=%s/%s table=%s/%s agree=%s" % (if_tok, if_ff, tb_tok, tb_ff, twins_agree))
    lines.append("self-checks: %d/%d pass" % (results["self_checks_passed"], results["self_checks_total"]))
    for c in self_checks:
        lines.append("  [%s] %s" % ("ok" if c["ok"] else "XX", c["name"]))
    lines.append("")
    lines.append("results.json sha256:  %s" % res_sha)
    lines.append("fixtures.json sha256: %s" % fx_sha)
    lines.append("")
    ruling = "APPROVE" if (verdict == "APPROVE" and all_pass) else "REJECT"
    lines.append("RULING: %s (first-failing gate: %s)" % (ruling, first_fail if first_fail else "none"))
    text = "\n".join(lines) + "\n"

    out_path = os.path.join(HERE, "run-stdout.txt")
    with open(out_path, "w") as fh:
        fh.write(text)
    print(text, end="")

    if not (all_pass and twins_agree):
        raise SystemExit("self-checks failed or twins disagree")


if __name__ == "__main__":
    main()
