#!/usr/bin/env python3
"""VERDICT-097 — Simpson's-paradox aggregation-reversal trap.

Independent stdlib-only verification of idea-engine PROPOSAL 084
(source header: `## PROPOSAL 084 · 2026-07-16T15:25:14Z · status: sim-ready`;
idea file ideas/fleet/simpsons-paradox-aggregation-reversal-2026-07-16.md,
landed idea-engine main @ 4b9db80 via PR #456). P084 -> V097 under the
constant +13 PROPOSAL<->VERDICT offset.

Structure mirrors VERDICT-096 (sim-lab PR #168):
  Arm A  -- pinned deterministic automaton over exact rational (Fraction)
            arithmetic; carries the DECISION-bearing computation.
  Arm B  -- an independently-shaped twin (integer roll-up + opposite-
            direction crossing walk) that must AGREE with Arm A on every
            typed contact C1..C3.
  Arm R  -- SEEDED, REPORTING-ONLY random 2x2x2 census; no statistical
            gate, registered 3-draw grammar per seed, per-seed census +
            12-hex class-stream digest. P084 is SEEDLESS: Arm R seeds are
            local reporting-only constants and consume NO seed-ledger block
            (next-free block 20261730 is untouched).
  Twin evaluators -- an if-chain evaluator and an independently transcribed
            table-driven evaluator that agree over the full enumerated
            boolean predicate space (16 rows).

Determinism: no wall-clock, no unseeded RNG, sorted iteration only; the
seedless core is exact rationals. Byte-identical across runs; results.json
and run-stdout.txt are sha256-digested and disclosed in REPORT.md.

Pre-registered decision rule (REJECT-first, mirrors P084's own):
  APPROVE  iff a uniform per-stratum ordering ALWAYS survives pooled
           aggregation (arithmetically excluded -> APPROVE unreachable);
  INVALID  on any falsifiability-gate failure F1..F5;
  NULL     if the exhibited reversal is a pure estimand/weight artifact
           that the standardization repair FAILS to resolve;
  REJECT   otherwise -- the naive "pooling preserves stratum ordering"
           claim is refuted by an exhibited reversal, AND a common-weight
           standardization restores the true (per-stratum) ordering.
  Precedence when several fire: REJECT > INVALID > APPROVE > NULL.
"""

from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction
from random import Random

HERE = os.path.dirname(os.path.abspath(__file__))
STRATA = ("small", "large")
TREATMENTS = ("A", "B")


def load_fixtures():
    with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
        return json.load(fh)


def build_cells(fx):
    return {(c["treatment"], c["stratum"]): (c["successes"], c["total"])
            for c in fx["cells"]}


def fr(pair):
    return Fraction(pair[0], pair[1])


# ---- Arm A : pinned automaton, decision-bearing -------------------------
def arm_a(cells, weight_sets):
    n = {t: cells[(t, "small")][1] + cells[(t, "large")][1] for t in TREATMENTS}
    per_stratum = {s: {t: fr(cells[(t, s)]) for t in TREATMENTS} for s in STRATA}
    a_dom = {s: per_stratum[s]["A"] > per_stratum[s]["B"] for s in STRATA}
    pooled = {t: Fraction(cells[(t, "small")][0] + cells[(t, "large")][0],
                          cells[(t, "small")][1] + cells[(t, "large")][1])
              for t in TREATMENTS}
    reversal = pooled["A"] < pooled["B"]
    margin = pooled["B"] - pooled["A"]

    aS, aL = fr(cells[("A", "small")]), fr(cells[("A", "large")])
    x_star = None
    for x in range(0, n["A"] + 1):
        if ((n["A"] - x) * aS + x * aL) / n["A"] <= pooled["B"]:
            x_star = x
            break
    real_x = cells[("A", "large")][1]

    std = {}
    for name in sorted(weight_sets):
        wS, wL = weight_sets[name]
        denom = wS + wL
        sa = (wS * fr(cells[("A", "small")]) + wL * fr(cells[("A", "large")])) / denom
        sb = (wS * fr(cells[("B", "small")]) + wL * fr(cells[("B", "large")])) / denom
        std[name] = (sa, sb, sa > sb)
    repair_restores = all(v[2] for v in std.values())

    return {
        "n": n, "per_stratum": per_stratum, "a_dominates_each": a_dom,
        "pooled": pooled, "reversal": reversal, "margin": margin,
        "x_star": x_star, "real_x": real_x,
        "real_past_crossing": real_x > x_star,
        "standardization": std, "repair_restores": repair_restores,
    }


# ---- Arm B : independently-shaped twin ----------------------------------
def arm_b(cells, weight_sets):
    pooled = {}
    for t in TREATMENTS:
        succ = sum(cells[(t, s)][0] for s in STRATA)
        tot = sum(cells[(t, s)][1] for s in STRATA)
        pooled[t] = Fraction(succ, tot)
    reversal = pooled["A"] < pooled["B"]
    margin = pooled["B"] - pooled["A"]
    a_dom = {s: fr(cells[("A", s)]) > fr(cells[("B", s)]) for s in STRATA}

    n_a = cells[("A", "small")][1] + cells[("A", "large")][1]
    aS, aL = fr(cells[("A", "small")]), fr(cells[("A", "large")])
    x_star = 0
    for x in range(n_a, -1, -1):
        if ((n_a - x) * aS + x * aL) / n_a > pooled["B"]:
            x_star = x + 1
            break

    wS, wL = weight_sets["pooled_marginal"]
    denom = wS + wL
    sa = (wS * fr(cells[("A", "small")]) + wL * fr(cells[("A", "large")])) / denom
    sb = (wS * fr(cells[("B", "small")]) + wL * fr(cells[("B", "large")])) / denom
    return {
        "pooled": pooled, "reversal": reversal, "margin": margin,
        "a_dominates_each": a_dom, "x_star": x_star,
        "std_pooled_marginal": (sa, sb, sa > sb),
    }


def contacts(a, b):
    return {
        "C1_pooled": a["pooled"] == b["pooled"],
        "C2_x_star": a["x_star"] == b["x_star"],
        "C3_std_pooled_marginal":
            a["standardization"]["pooled_marginal"] == b["std_pooled_marginal"],
        "C_margin": a["margin"] == b["margin"],
        "C_reversal": a["reversal"] == b["reversal"],
    }


def gates(cells, a, weight_sets):
    F1 = all(0 <= cells[(t, s)][0] <= cells[(t, s)][1]
             for t in TREATMENTS for s in STRATA)
    F2 = all(a["a_dominates_each"][s] for s in STRATA)
    F3 = a["reversal"]
    na, nb = a["n"]["A"], a["n"]["B"]
    F4 = Fraction(cells[("A", "large")][1], na) != Fraction(cells[("B", "large")][1], nb)
    F5 = all((wS + wL) > 0 for wS, wL in weight_sets.values())
    return {"F1": F1, "F2": F2, "F3": F3, "F4": F4, "F5": F5}


# ---- Twin evaluators : if-chain vs independently transcribed table ------
def decide_ifchain(gates_ok, uniform, survives, repaired):
    # precedence REJECT > INVALID > APPROVE > NULL
    if gates_ok and uniform and (not survives) and repaired:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if gates_ok and uniform and survives:
        return "APPROVE"
    return "NULL"


# Hand-transcribed independently of the if-chain above.
DECISION_TABLE = {
    (False, False, False, False): "INVALID",
    (False, False, False, True): "INVALID",
    (False, False, True, False): "INVALID",
    (False, False, True, True): "INVALID",
    (False, True, False, False): "INVALID",
    (False, True, False, True): "INVALID",
    (False, True, True, False): "INVALID",
    (False, True, True, True): "INVALID",
    (True, False, False, False): "NULL",
    (True, False, False, True): "NULL",
    (True, False, True, False): "NULL",
    (True, False, True, True): "NULL",
    (True, True, False, False): "NULL",
    (True, True, False, True): "REJECT",
    (True, True, True, False): "APPROVE",
    (True, True, True, True): "APPROVE",
}


def decide_table(gates_ok, uniform, survives, repaired):
    return DECISION_TABLE[(gates_ok, uniform, survives, repaired)]


# ---- Arm R : seeded, REPORTING-ONLY census ------------------------------
def classify_table(tbl):
    if any(tbl[(t, s)][1] == 0 for t in TREATMENTS for s in STRATA):
        return "degenerate"
    dom_small = fr(tbl[("A", "small")]) > fr(tbl[("B", "small")])
    dom_large = fr(tbl[("A", "large")]) > fr(tbl[("B", "large")])
    pa = Fraction(sum(tbl[("A", s)][0] for s in STRATA),
                  sum(tbl[("A", s)][1] for s in STRATA))
    pb = Fraction(sum(tbl[("B", s)][0] for s in STRATA),
                  sum(tbl[("B", s)][1] for s in STRATA))
    if dom_small and dom_large and pa < pb:
        return "reversal"
    if (not dom_small) and (not dom_large) and pb < pa:
        return "reversal"
    return "no_reversal"


def arm_r(seeds, draws):
    census = {}
    stream = []
    reversal_requires_diffweight = True
    for seed in sorted(seeds):
        rng = Random(seed)
        sc = {"reversal": 0, "no_reversal": 0, "degenerate": 0}
        for _ in range(draws):
            tbl = {}
            for t in TREATMENTS:
                for s in STRATA:
                    tot = rng.randint(1, 300)
                    succ = rng.randint(0, tot)
                    tbl[(t, s)] = (succ, tot)
            cls = classify_table(tbl)
            sc[cls] += 1
            stream.append(cls[0].upper())
            if cls == "reversal":
                na = tbl[("A", "small")][1] + tbl[("A", "large")][1]
                nb = tbl[("B", "small")][1] + tbl[("B", "large")][1]
                if Fraction(tbl[("A", "large")][1], na) == Fraction(tbl[("B", "large")][1], nb):
                    reversal_requires_diffweight = False
        census[str(seed)] = sc
    digest = hashlib.sha256("".join(stream).encode()).hexdigest()[:12]
    return {"census": census, "class_digest": digest,
            "reversal_requires_differential_weighting": reversal_requires_diffweight,
            "draws_per_seed": draws, "seeds": sorted(seeds)}


def canon(obj):
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): canon(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [canon(v) for v in obj]
    return obj


def main():
    fx = load_fixtures()
    cells = build_cells(fx)
    weight_sets = {k: tuple(v) for k, v in fx["weight_sets"].items()}
    seeds = fx["registered_seeds"]
    draws = fx["draws_per_seed"]

    a = arm_a(cells, weight_sets)
    b = arm_b(cells, weight_sets)
    c = contacts(a, b)
    g = gates(cells, a, weight_sets)
    gates_ok = all(g.values())
    uniform = all(a["a_dominates_each"].values())
    survives = not a["reversal"]
    repaired = a["repair_restores"]

    v_ifchain = decide_ifchain(gates_ok, uniform, survives, repaired)
    v_table = decide_table(gates_ok, uniform, survives, repaired)
    enum_agree = all(
        decide_ifchain(gg, uu, ss, rr) == decide_table(gg, uu, ss, rr)
        for gg in (False, True) for uu in (False, True)
        for ss in (False, True) for rr in (False, True)
    )
    r = arm_r(seeds, draws)

    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    chk("F1_integer_cells", g["F1"])
    chk("F2_per_stratum_A_dominates", g["F2"])
    chk("F3_pooled_reversal", g["F3"])
    chk("F4_differential_weighting", g["F4"])
    chk("F5_standardization_welldefined", g["F5"])
    chk("a_small_dominates", a["a_dominates_each"]["small"])
    chk("a_large_dominates", a["a_dominates_each"]["large"])
    chk("pooled_A_273_350", a["pooled"]["A"] == Fraction(273, 350))
    chk("pooled_B_289_350", a["pooled"]["B"] == Fraction(289, 350))
    chk("margin_16_350", a["margin"] == Fraction(16, 350))
    chk("margin_reduced_8_175", a["margin"] == Fraction(8, 175))
    chk("reversal_present", a["reversal"])
    chk("x_star_184", a["x_star"] == 184)
    chk("real_x_263", a["real_x"] == 263)
    chk("real_past_crossing", a["real_past_crossing"])
    chk("std_pooled_marginal_A_gt_B", a["standardization"]["pooled_marginal"][2])
    chk("std_uniform_A_gt_B", a["standardization"]["uniform"][2])
    chk("std_a_marginal_A_gt_B", a["standardization"]["a_marginal"][2])
    chk("std_b_marginal_A_gt_B", a["standardization"]["b_marginal"][2])
    chk("std_A_pooled_634983_762700",
        a["standardization"]["pooled_marginal"][0] == Fraction(634983, 762700))
    chk("std_B_pooled_6231_8000",
        a["standardization"]["pooled_marginal"][1] == Fraction(6231, 8000))
    chk("repair_restores_all_mixes", a["repair_restores"])
    chk("weight_invariance_four_mixes", len(a["standardization"]) == 4)
    chk("C1_pooled_agree", c["C1_pooled"])
    chk("C2_x_star_agree", c["C2_x_star"])
    chk("C3_std_agree", c["C3_std_pooled_marginal"])
    chk("C_margin_agree", c["C_margin"])
    chk("C_reversal_agree", c["C_reversal"])
    chk("twin_evaluators_enum_agree", enum_agree)
    chk("evaluators_agree_actual", v_ifchain == v_table)
    chk("verdict_is_REJECT", v_ifchain == "REJECT")
    chk("armR_reporting_only_diffweight", r["reversal_requires_differential_weighting"])
    chk("armR_digest_len_12", len(r["class_digest"]) == 12)

    n_pass = sum(1 for _, ok in checks if ok)
    n_total = len(checks)

    result = {
        "verdict": v_ifchain,
        "proposal": fx["proposal"],
        "source": fx["source"],
        "arm_a": {
            "pooled": a["pooled"], "reversal": a["reversal"], "margin": a["margin"],
            "x_star": a["x_star"], "real_x": a["real_x"],
            "real_past_crossing": a["real_past_crossing"],
            "a_dominates_each": a["a_dominates_each"],
            "standardization": {k: {"std_A": v[0], "std_B": v[1], "A_gt_B": v[2]}
                                for k, v in a["standardization"].items()},
            "repair_restores": a["repair_restores"],
        },
        "arm_b": {
            "pooled": b["pooled"], "x_star": b["x_star"],
            "std_pooled_marginal": {"std_A": b["std_pooled_marginal"][0],
                                    "std_B": b["std_pooled_marginal"][1],
                                    "A_gt_B": b["std_pooled_marginal"][2]},
        },
        "contacts": c,
        "gates": g,
        "twin_evaluators": {"ifchain": v_ifchain, "table": v_table,
                            "enumerated_agreement": enum_agree},
        "arm_r": r,
        "self_checks": {"passed": n_pass, "total": n_total,
                        "detail": {k: ok for k, ok in checks}},
    }

    canonical = json.dumps(canon(result), sort_keys=True, indent=2)
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        fh.write(canonical + "\n")
    digest = hashlib.sha256((canonical + "\n").encode()).hexdigest()

    L = []
    L.append("VERDICT-097 - Simpson's-paradox aggregation-reversal trap")
    L.append("verifies idea-engine PROPOSAL 084 (P084 -> V097, +13 offset)")
    L.append("")
    L.append("Per-stratum success rate (A vs B):")
    L.append("  small: A=%s (%.4f)  B=%s (%.4f)  A>B=%s"
             % (a["per_stratum"]["small"]["A"], float(a["per_stratum"]["small"]["A"]),
                a["per_stratum"]["small"]["B"], float(a["per_stratum"]["small"]["B"]),
                a["a_dominates_each"]["small"]))
    L.append("  large: A=%s (%.4f)  B=%s (%.4f)  A>B=%s"
             % (a["per_stratum"]["large"]["A"], float(a["per_stratum"]["large"]["A"]),
                a["per_stratum"]["large"]["B"], float(a["per_stratum"]["large"]["B"]),
                a["a_dominates_each"]["large"]))
    L.append("Pooled: A=%s (%.4f)  B=%s (%.4f)  -> reversal=%s"
             % (a["pooled"]["A"], float(a["pooled"]["A"]),
                a["pooled"]["B"], float(a["pooled"]["B"]), a["reversal"]))
    L.append("Reversal margin (B-A): %s (%.5f)" % (a["margin"], float(a["margin"])))
    L.append("Crossing x*: %d  (real large-stratum load x=%d, past crossing=%s)"
             % (a["x_star"], a["real_x"], a["real_past_crossing"]))
    L.append("Standardization (common weights) restores A>B on all %d mixes:"
             % len(a["standardization"]))
    for k in sorted(a["standardization"]):
        sa, sb, ok = a["standardization"][k]
        L.append("  %-16s std_A=%.5f std_B=%.5f  A>B=%s"
                 % (k, float(sa), float(sb), ok))
    L.append("Twin contacts (Arm A == Arm B): %s"
             % {k: c[k] for k in sorted(c)})
    L.append("Twin evaluators (if-chain / table) enumerated agreement: %s" % enum_agree)
    L.append("Arm R (seeded, REPORTING-ONLY, no gate) census: %s" % r["census"])
    L.append("Arm R class-stream digest: %s  (reversal-needs-diff-weight=%s)"
             % (r["class_digest"], r["reversal_requires_differential_weighting"]))
    L.append("")
    L.append("Self-checks: %d/%d PASS" % (n_pass, n_total))
    L.append("VERDICT: %s" % v_ifchain)
    L.append("results.json sha256: %s" % digest)
    stdout = "\n".join(L) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w", encoding="utf-8") as fh:
        fh.write(stdout)
    print(stdout, end="")

    if n_pass != n_total:
        raise SystemExit("SELF-CHECK FAILURE: %d/%d" % (n_pass, n_total))


if __name__ == "__main__":
    main()
