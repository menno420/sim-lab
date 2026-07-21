#!/usr/bin/env python3
"""PROPOSAL 246 verifier — Gordon growth / dividend-discount model closed form.

Claim: the present value of a growing perpetuity with first cashflow D1 at t=1,
constant growth g and discount rate r (r > g > -1) is EXACTLY

    PV = D1 / (r - g)

the closed sum of the geometric series  sum_{t>=1} D1 (1+g)^{t-1} / (1+r)^t.

Four gates, each in its own direction:
  G1 EXACT identity      (fractions.Fraction, zero tolerance)
  G2 Monte-Carlo agree   (|z| < 3): stochastic-dividend DDM, i.i.d. paths
  G3 invariance/robust   (noise-structure invariance + exact shift invariance)
  G4 falsifiability      (naive level-perpetuity P=D1/r rejected at large |z|)

Stdlib only. Deterministic under SEED. Usage:
  python3 verify_246_gordon_growth_ddm.py              # canonical JSON + digest
  python3 verify_246_gordon_growth_ddm.py --selfcheck  # in-process double-run byte-identical
"""
import json, hashlib, math, random, sys
from fractions import Fraction as F

SEED     = 20260717
Z_ACCEPT = 3.0
Z_REJECT = 3.0
N_MC     = 100000
T_MC     = 160

def closed_form(D1, r, g):
    return D1 / (r - g)

def partial_sum(D1, r, g, T):
    total = F(0)
    onep_g, onep_r = 1 + g, 1 + r
    num = D1
    den = onep_r
    for _ in range(T):
        total += num / den
        num *= onep_g
        den *= onep_r
    return total

def exact_tail(D1, r, g, T):
    rho = (1 + g) / (1 + r)
    return (D1 / (r - g)) * (rho ** T)

def exact_finiteT_target(D1, r, g, T):
    rho = (1 + g) / (1 + r)
    return float((D1 / (r - g)) * (1 - rho ** T))

def gate1():
    battery = [
        (F(1), F(1,10),   F(0)),
        (F(1), F(1,10),   F(4,100)),
        (F(6), F(1,10),   F(2,100)),
        (F(3), F(1,5),    F(1,20)),
        (F(2), F(12,100), F(5,100)),
        (F(10),F(8,100),  F(3,100)),
        (F(5), F(7,100),  F(-2,100)),
        (F(100),F(15,100),F(6,100)),
        (F(7,2),F(9,100), F(1,100)),
        (F(1), F(1,4),    F(1,10)),
    ]
    anchors = [
        ((F(1), F(1,10),  F(0)),      F(10)),
        ((F(1), F(1,10),  F(4,100)),  F(50,3)),
        ((F(6), F(1,10),  F(2,100)),  F(75)),
        ((F(3), F(1,5),   F(1,20)),   F(20)),
        ((F(2), F(12,100),F(5,100)),  F(200,7)),
    ]
    T = 60
    mism = 0
    for (D1, r, g) in battery:
        cf    = closed_form(D1, r, g)
        recon = partial_sum(D1, r, g, T) + exact_tail(D1, r, g, T)
        fp_ok  = (cf * (r - g) == D1)
        rec_ok = (cf == D1 / (1 + r) + cf * (1 + g) / (1 + r))
        if not (recon == cf and fp_ok and rec_ok):
            mism += 1
    anchor_mism = sum(1 for (k, want) in anchors if closed_form(*k) != want)
    return {
        "name": "G1_exact_identity",
        "battery_size": len(battery),
        "T_terms": T,
        "mismatches": mism,
        "anchor_mismatches": anchor_mism,
        "max_discrepancy": 0,
        "z": None,
        "tolerance": "exact (fractions.Fraction, zero tolerance)",
        "pass": (mism == 0 and anchor_mism == 0),
    }

def mc_paths(D1, r, g, delta, N, T, rng):
    onep_g, onep_r = 1.0 + g, 1.0 + r
    lo, hi = 1.0 - delta, 1.0 + delta
    D0 = D1 / onep_g
    s1 = 0.0
    s2 = 0.0
    for _ in range(N):
        D = D0
        disc = 1.0
        pv = 0.0
        for _t in range(T):
            eps = lo if rng.random() < 0.5 else hi
            D *= onep_g * eps
            disc *= onep_r
            pv += D / disc
        s1 += pv
        s2 += pv * pv
    mean = s1 / N
    var = (s2 - N * mean * mean) / (N - 1)
    se = math.sqrt(var / N)
    return mean, se

def build_results():
    D1f, rf, gf = 1.0, 0.10, 0.04
    target = exact_finiteT_target(F(1), F(1,10), F(4,100), T_MC)
    naive_level = float(F(1) / F(1,10))            # D1/r = 10.0
    E_infinite  = float(F(1) / (F(1,10) - F(4,100)))  # 50/3

    g1 = gate1()

    rngA = random.Random(SEED)
    meanA, seA = mc_paths(D1f, rf, gf, 0.3, N_MC, T_MC, rngA)
    z_g2 = (meanA - target) / seA
    g2 = {
        "name": "G2_montecarlo_agreement",
        "headline": "D1=1, r=1/10, g=4/100",
        "N": N_MC, "T": T_MC, "delta": 0.3,
        "mean_hat": round(meanA, 10),
        "target_exact_finiteT": round(target, 10),
        "E_infinite": round(E_infinite, 10),
        "se": round(seA, 12),
        "z": round(z_g2, 10),
        "Z_ACCEPT": Z_ACCEPT,
        "independent_paths_no_thinning": True,
        "pass": abs(z_g2) < Z_ACCEPT,
    }

    rngB = random.Random(SEED + 1)
    meanB, seB = mc_paths(D1f, rf, gf, 0.5, N_MC, T_MC, rngB)
    zA = (meanA - target) / seA
    zB = (meanB - target) / seB
    z_two = (meanA - meanB) / math.sqrt(seA * seA + seB * seB)
    shifts = [F(1,100), F(3,100), F(1,2), F(-1,50)]
    sbat = [(F(1),F(1,10),F(4,100)), (F(6),F(1,10),F(2,100)), (F(2),F(12,100),F(5,100))]
    shift_mis = 0
    for (D1, r, g) in sbat:
        base = closed_form(D1, r, g)
        for c in shifts:
            if closed_form(D1, r + c, g + c) != base:
                shift_mis += 1
    g3 = {
        "name": "G3_invariance_robustness",
        "noise_configs": "A: delta=0.3 ; B: delta=0.5 (both mean-1)",
        "meanA": round(meanA, 10), "zA": round(zA, 10),
        "meanB": round(meanB, 10), "zB": round(zB, 10),
        "two_sample_z": round(z_two, 10),
        "shift_invariance_battery": len(sbat) * len(shifts),
        "shift_invariance_mismatches": shift_mis,
        "Z_ACCEPT": Z_ACCEPT,
        "pass": (abs(zA) < Z_ACCEPT and abs(zB) < Z_ACCEPT
                 and abs(z_two) < Z_ACCEPT and shift_mis == 0),
    }

    z_naive = (meanA - naive_level) / seA
    g4 = {
        "name": "G4_falsifiability",
        "naive_hypothesis": "level perpetuity P=D1/r (ignores growth)",
        "naive_value": round(naive_level, 10),
        "same_sample_mean": round(meanA, 10),
        "z_naive": round(z_naive, 10),
        "z_exact_for_contrast": round(z_g2, 10),
        "Z_REJECT": Z_REJECT,
        "pass": abs(z_naive) > Z_REJECT,
    }

    all_pass = g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]
    first_fail = None
    for gg in (g1, g2, g3, g4):
        if not gg["pass"]:
            first_fail = gg["name"]
            break
    return {
        "proposal": 246,
        "claim": "Gordon growth / DDM: PV of a growing perpetuity = D1/(r-g)",
        "seed": SEED,
        "closed_form": "PV = D1/(r-g)",
        "gates": {"G1": g1, "G2": g2, "G3": g3, "G4": g4},
        "all_gates_pass": all_pass,
        "first_failing_gate": first_fail,
        "decision": "PASS" if all_pass else "FAIL",
    }

def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))

def digest(results):
    return hashlib.sha256(canonical(results).encode()).hexdigest()

def main():
    if "--selfcheck" in sys.argv:
        r1 = build_results()
        r2 = build_results()
        assert canonical(r1) == canonical(r2), "SELFCHECK FAIL: double-run differs"
        print("SELFCHECK OK: in-process double-run byte-identical")
        print("results_sha256:", digest(r1))
        return
    results = build_results()
    assert canonical(results) == canonical(build_results()), "double-run differs"
    print(canonical(results))
    print("results_sha256:", digest(results))

if __name__ == "__main__":
    main()
