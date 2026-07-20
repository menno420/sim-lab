#!/usr/bin/env python3
"""PROPOSAL 228 / VERDICT 241 (+13 offset) -- Feller's no-return identity for the
simple symmetric random walk on Z: the probability the walk AVOIDS the origin
throughout the first 2n steps equals the probability it is AT the origin at time
2n, both equal to the central-binomial return probability u_{2n}=C(2n,n)/4^n.

HEAD statement
--------------
Take the simple symmetric random walk S_0=0, S_k = X_1+...+X_k with i.i.d.
X_i in {+1,-1} each with probability 1/2 (Feller, An Introduction to Probability
Theory Vol. I, Ch. III). Two events on the first 2n steps:
  RETURN:    S_{2n} = 0                          (at the origin at time 2n)
  NO-RETURN: S_1 != 0, S_2 != 0, ..., S_{2n} != 0 (never revisit 0 in 1..2n)
The return probability is the central-binomial term
  u_{2n} := P(S_{2n}=0) = C(2n,n) / 2^{2n} = C(2n,n) / 4^n.
Feller's identity: P(NO-RETURN over 1..2n) = u_{2n} EXACTLY -- avoiding the origin
is exactly as likely as landing on it. Equivalently, over all 2^{2n} equally-likely
sign sequences,
  #{paths with S_{2n}=0} = #{paths that never revisit 0 in 1..2n} = C(2n,n)
                                                       (EXACT integer identity),
so both events carry the same probability C(2n,n)/4^n.

Pre-registered gate battery (each in its own direction)
-------------------------------------------------------
G1  EQUALITY (exhaustive, exact): enumerate ALL 2^(2n) sign sequences for
    n in {1,2,3,4,5,6}. Assert A := #{S_{2n}=0} == B := #{never touch 0} ==
    C(2n,n), and Fraction(A,4^n)==Fraction(B,4^n)==Fraction(C(2n,n),4^n)==u_{2n}.
G2  AGREEMENT |z|<3: Monte-Carlo n=12 (24 steps), N_MC_MAIN walks; p_hat_return
    and p_hat_noreturn each vs the SHARED exact u_24 must give |z|<3 (both).
G3  INVARIANT + AGREEMENT: across n in {5,8,12,20}, p_hat_noreturn agrees with the
    exact u_{2n} at |z|<3 each, and the left/right symmetry P(strictly positive
    throughout) == P(strictly negative throughout) holds within |z|<3 at each n.
G4  REJECTION |z|>6: the naive independence fallacy "avoiding 0 over 2n steps
    behaves like n independent pairs" predicts P(no-return)=(1/2)^n; on the SAME
    n=12 MC sample as G2 the observed p_hat_noreturn (~0.161) rejects the naive
    2^-n (~0.000244) at |z|>6 (an enormous z) -- the fallacy is falsified.

Determinism: single random.Random(SEED) consumed in the fixed order G2 -> G3 -> G4
(G1 is exhaustive/RNG-free; G4 reuses G2's sample, drawing no fresh randomness).
build_results() is a pure function of SEED + fixed constants; main() runs it twice
in-process (asserts byte-identical canonical form) and a separate re-invocation is
byte-identical. Digest = sha256 of the whole results dict (no self-field), stdout only.
"""
import sys
import json
import math
import hashlib
import random
from math import comb
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
Z_REJECT = 6.0
EXACT_SIZES = (1, 2, 3, 4, 5, 6)
MC_SIZE = 12
N_MC_MAIN = 200_000
ROBUST_SIZES = (5, 8, 12, 20)
N_MC_ROBUST = 50_000


def u_2n(n):
    """Exact return probability u_{2n} = C(2n,n)/4^n as a Fraction."""
    return Fraction(comb(2 * n, n), 4 ** n)


def zscore(p_hat, p, N):
    """Standard one-proportion z of an estimate p_hat about true p over N draws."""
    return (p_hat - p) / math.sqrt(p * (1.0 - p) / N)


def exhaustive(n):
    """Enumerate all 2^(2n) sign sequences; count final-at-zero and never-zero."""
    steps = 2 * n
    total = 1 << steps
    at_zero = 0
    never_zero = 0
    for bits in range(total):
        s = 0
        hit = False
        for k in range(steps):
            s += 1 if (bits >> k) & 1 else -1
            if s == 0:
                hit = True
        if s == 0:
            at_zero += 1
        if not hit:
            never_zero += 1
    central = comb(2 * n, n)
    u = u_2n(n)
    counts_equal = (at_zero == never_zero == central)
    fracs_equal = (Fraction(at_zero, 4 ** n) == Fraction(never_zero, 4 ** n)
                   == Fraction(central, 4 ** n) == u)
    return {
        "n": n, "steps": steps, "paths": total,
        "count_at_zero": at_zero, "count_never_zero": never_zero,
        "central_binom": central, "u_2n": str(u),
        "counts_equal_exact": bool(counts_equal),
        "fractions_equal_exact": bool(fracs_equal),
    }


def mc_walks(rng, n, N):
    """N simple symmetric walks of 2n steps; count return / no-return / one-sided."""
    steps = 2 * n
    at_zero = 0
    noreturn = 0
    pos_only = 0
    neg_only = 0
    for _ in range(N):
        s = 0
        hit = False
        pos = True
        neg = True
        for _ in range(steps):
            s += 1 if rng.getrandbits(1) else -1
            if s == 0:
                hit = True
            if s <= 0:
                pos = False
            if s >= 0:
                neg = False
        if s == 0:
            at_zero += 1
        if not hit:
            noreturn += 1
        if pos:
            pos_only += 1
        if neg:
            neg_only += 1
    return {"n": n, "steps": steps, "samples": N,
            "count_at_zero": at_zero, "count_noreturn": noreturn,
            "count_pos_only": pos_only, "count_neg_only": neg_only}


def build_results():
    r = {"proposal": 228, "verdict": 241, "slot": "round-54 UNRELATED", "seed": SEED,
         "z_gate": Z_GATE, "z_reject": Z_REJECT,
         "mc_size": MC_SIZE, "n_mc_main": N_MC_MAIN, "n_mc_robust": N_MC_ROBUST}

    # G1 -- EXACT EQUALITY (exhaustive, Fraction). RNG-free.
    ex = [exhaustive(n) for n in EXACT_SIZES]
    g1_pass = all(e["counts_equal_exact"] and e["fractions_equal_exact"] for e in ex)
    r["gate1_exact_equality"] = {
        "direction": "EQUALITY",
        "sizes": list(EXACT_SIZES), "per_size": ex,
        "pass": bool(g1_pass)}

    rng = random.Random(SEED)

    # G2 -- MONTE-CARLO AGREEMENT vs the shared exact u_2n (|z|<3 both).
    g2raw = mc_walks(rng, MC_SIZE, N_MC_MAIN)
    u_main = u_2n(MC_SIZE)
    p_ret = g2raw["count_at_zero"] / N_MC_MAIN
    p_nor = g2raw["count_noreturn"] / N_MC_MAIN
    z_ret = zscore(p_ret, float(u_main), N_MC_MAIN)
    z_nor = zscore(p_nor, float(u_main), N_MC_MAIN)
    g2_pass = (abs(z_ret) < Z_GATE) and (abs(z_nor) < Z_GATE)
    r["gate2_mc_agreement"] = {
        "direction": "AGREEMENT |z|<%.1f" % Z_GATE,
        "n": MC_SIZE, "steps": 2 * MC_SIZE, "samples": N_MC_MAIN,
        "u_2n": str(u_main), "u_2n_float": round(float(u_main), 8),
        "count_at_zero": g2raw["count_at_zero"], "count_noreturn": g2raw["count_noreturn"],
        "p_hat_return": round(p_ret, 6), "z_return": round(z_ret, 6),
        "p_hat_noreturn": round(p_nor, 6), "z_noreturn": round(z_nor, 6),
        "pass": bool(g2_pass)}

    # G3 -- ROBUSTNESS / INVARIANCE across sizes + left/right symmetry.
    per_size = []
    for n in ROBUST_SIZES:
        d = mc_walks(rng, n, N_MC_ROBUST)
        u = u_2n(n)
        p_nr = d["count_noreturn"] / N_MC_ROBUST
        z_nr = zscore(p_nr, float(u), N_MC_ROBUST)
        p_pos = d["count_pos_only"] / N_MC_ROBUST
        p_neg = d["count_neg_only"] / N_MC_ROBUST
        var_sym = (p_pos * (1 - p_pos) / N_MC_ROBUST) + (p_neg * (1 - p_neg) / N_MC_ROBUST)
        z_sym = (p_pos - p_neg) / math.sqrt(var_sym) if var_sym > 0 else 0.0
        cell_pass = (abs(z_nr) < Z_GATE) and (abs(z_sym) < Z_GATE)
        per_size.append({
            "n": n, "steps": 2 * n, "samples": N_MC_ROBUST,
            "u_2n": str(u), "u_2n_float": round(float(u), 8),
            "count_noreturn": d["count_noreturn"],
            "p_hat_noreturn": round(p_nr, 6), "z_noreturn": round(z_nr, 6),
            "count_pos_only": d["count_pos_only"], "count_neg_only": d["count_neg_only"],
            "p_hat_pos_only": round(p_pos, 6), "p_hat_neg_only": round(p_neg, 6),
            "z_symmetry": round(z_sym, 6),
            "pass": bool(cell_pass)})
    g3_pass = all(x["pass"] for x in per_size)
    r["gate3_robustness"] = {
        "direction": "INVARIANT p_noreturn==u_2n across n + AGREEMENT left/right symmetry |z|<%.1f" % Z_GATE,
        "per_size": per_size, "pass": bool(g3_pass)}

    # G4 -- FALSIFIABILITY: reject the naive independence fallacy P(no-return)=2^-n
    # on the SAME n=12 MC sample as G2 (draws no fresh randomness).
    naive = Fraction(1, 2 ** MC_SIZE)
    z_naive = zscore(p_nor, float(naive), N_MC_MAIN)
    g4_pass = abs(z_naive) > Z_REJECT
    r["gate4_falsifiability"] = {
        "direction": "REJECTION |z|>%.1f (naive independence fallacy: P(no-return)=2^-n)" % Z_REJECT,
        "n": MC_SIZE, "samples": N_MC_MAIN,
        "naive_prediction": str(naive), "naive_float": round(float(naive), 8),
        "true_u_2n_float": round(float(u_main), 8),
        "p_hat_noreturn": round(p_nor, 6),
        "z_vs_naive": round(z_naive, 6),
        "rejected": bool(g4_pass),
        "pass": bool(g4_pass)}

    gates = {"gate1": r["gate1_exact_equality"]["pass"],
             "gate2": r["gate2_mc_agreement"]["pass"],
             "gate3": r["gate3_robustness"]["pass"],
             "gate4": r["gate4_falsifiability"]["pass"]}
    r["gates"] = gates
    r["first_failing_gate"] = next((k for k, v in gates.items() if not v), None)
    r["all_pass"] = bool(all(gates.values()))
    return r


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for k in ("gate1", "gate2", "gate3", "gate4"):
        print("%s: %s" % (k, "PASS" if r1["gates"][k] else "FAIL"))
    print("all_pass: %s" % r1["all_pass"])
    print("results_sha256: %s" % hashlib.sha256(c1.encode()).hexdigest())
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
