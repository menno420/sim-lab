#!/usr/bin/env python3
"""Condorcet Jury Theorem for committees: a majority vote of n INDEPENDENT members,
each individually correct with probability p, is right with probability
    M(n, p) = sum_{k=(n+1)/2}^{n} C(n,k) * p^k * (1-p)^(n-k)   (n odd).
The counterintuitive head is the DARK SIDE. For p > 1/2 (each member better than a
coin flip) M(n,p) STRICTLY INCREASES in n and -> 1: bigger committees manufacture
near-certainty. But for p < 1/2 (each member worse than a coin flip) M(n,p)
STRICTLY DECREASES in n and -> 0: adding members makes the committee reliably
WRONG, and the best jury is a SINGLE voter. Committee SIZE amplifies whichever side
of 1/2 the individual competence sits on; only at p = 1/2 is M = 1/2 for every n.
The lever: vet member competence past 1/2 BEFORE enlarging the panel, never after.

Stdlib only (hashlib, json, math, random, fractions). Deterministic: SEED pinned;
a fresh random.Random(SEED) is created at the start of EACH full run, so both an
in-process double-run and separate cross-invocation reproduce byte-identical output.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the compact-canonical
results dict's own sha256 IS the digest; it is not a field inside the dict.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
T_MC = 200_000           # Monte-Carlo trials (G1, G3)
N_MC = 101               # committee size for the Monte-Carlo gates (odd)
ROUND_DP = 10            # fixed serialization precision for byte-stable floats
N_ENUM = (1, 3, 5, 7, 9)  # small odd sizes for the exhaustive-enumeration gate

# Competence cases. Exact Fractions for the enumeration gate; the MC gates reuse
# the same rationals as floats.
P_ABOVE = Fraction(3, 5)   # 0.60  -> majority climbs to 1
P_BELOW = Fraction(2, 5)   # 0.40  -> majority collapses to 0 (the dark side)
P_HALF = Fraction(1, 2)    # 0.50  -> knife edge, M = 1/2 for every odd n


def majority_correct_closed_form(n, p):
    """M(n,p) = sum_{k>n/2} C(n,k) p^k (1-p)^(n-k) as an exact Fraction (p Fraction)."""
    p = Fraction(p)
    q = 1 - p
    need = n // 2 + 1  # strict majority (n odd)
    total = Fraction(0)
    for k in range(need, n + 1):
        total += Fraction(math.comb(n, k)) * (p ** k) * (q ** (n - k))
    return total


def majority_correct_enumeration(n, p):
    """Exact M(n,p) by summing over ALL 2^n vote patterns (p Fraction).

    Each of the n members votes correct (bit 1) w.p. p, incorrect (bit 0) w.p. 1-p,
    independently; a pattern with c correct votes has probability p^c (1-p)^(n-c) and
    the majority is correct iff c > n/2. Sum the probabilities of majority-correct
    patterns. Independent of any closed form -- the firsthand exact witness.
    """
    p = Fraction(p)
    q = 1 - p
    need = n // 2 + 1
    total = Fraction(0)
    for pattern in range(1 << n):
        c = bin(pattern).count("1")
        if c >= need:
            total += (p ** c) * (q ** (n - c))
    return total


def mean_sd(vals):
    """Sample mean and standard deviation (ddof=1)."""
    n = len(vals)
    m = math.fsum(vals) / n
    var = math.fsum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


def mc_majority_rate_bernoulli(rng, n, p_float, trials):
    """Empirical majority-correct rate: each member votes correct iff U<p (Bernoulli)."""
    hits = 0
    outcomes = []
    for _ in range(trials):
        c = 0
        for _ in range(n):
            if rng.random() < p_float:
                c += 1
        ok = 1 if c >= (n // 2 + 1) else 0
        hits += ok
        outcomes.append(ok)
    return hits / trials, outcomes


def mc_majority_rate_heavytail(rng, n, p_float, trials):
    """Empirical majority-correct rate via a HEAVY-TAILED (Cauchy) latent signal,
    thresholded to the SAME competence p. Each member draws a standard-Cauchy score
    y = tan(pi*(V-1/2)), V~U(0,1), and votes correct iff y < tau, with the threshold
    tau = tan(pi*(p-1/2)) so P(correct) = P(V<p) = p EXACTLY, whatever the score
    distribution. A fresh, independent draw stream -- if the majority rate depends
    only on the competence p (distribution-free), it matches the Bernoulli world.
    """
    tau = math.tan(math.pi * (p_float - 0.5))
    hits = 0
    outcomes = []
    for _ in range(trials):
        c = 0
        for _ in range(n):
            y = math.tan(math.pi * (rng.random() - 0.5))
            if y < tau:
                c += 1
        ok = 1 if c >= (n // 2 + 1) else 0
        hits += ok
        outcomes.append(ok)
    return hits / trials, outcomes


def mc_majority_rate_monotone_paired(rng, n, p_float, trials):
    """Empirical majority-correct rate using a MONOTONE transform of the SAME latent
    draw and a correspondingly transformed threshold: member draws U~U(0,1), score
    g(U)=exp(U), votes correct iff g(U) < exp(p) <=> U < p. Bit-identical to the
    Bernoulli vote on the same U -- so on a shared random stream the majority
    outcomes are IDENTICAL, proving the rule reads only the threshold crossing, not
    the value. Returns the rate and the per-trial outcomes for an exact-equality check
    against a Bernoulli pass over the SAME stream.
    """
    thr = math.exp(p_float)
    hits = 0
    outcomes = []
    for _ in range(trials):
        c = 0
        for _ in range(n):
            u = rng.random()
            if math.exp(u) < thr:  # <=> u < p_float, monotone-transformed threshold
                c += 1
        ok = 1 if c >= (n // 2 + 1) else 0
        hits += ok
        outcomes.append(ok)
    return hits / trials, outcomes


def mc_majority_rate_bernoulli_stream(rng, n, p_float, trials):
    """Bernoulli majority vote consuming the SAME U draws in the SAME order as the
    monotone-paired pass (u < p), for a bit-identical cross-check."""
    hits = 0
    outcomes = []
    for _ in range(trials):
        c = 0
        for _ in range(n):
            u = rng.random()
            if u < p_float:
                c += 1
        ok = 1 if c >= (n // 2 + 1) else 0
        hits += ok
        outcomes.append(ok)
    return hits / trials, outcomes


def gate_g1(rng):
    """Statistical agreement (>=3 sigma band): the Monte-Carlo majority-correct rate
    at N_MC matches the exact closed form M(N_MC,p) within 3 standard errors, for
    BOTH an above-half and a below-half competence. Direction: |emp - cf| <= 3*se."""
    detail = {}
    ok = True
    for name, p in (("above_p0.60", P_ABOVE), ("below_p0.40", P_BELOW)):
        p_float = float(p)
        cf = float(majority_correct_closed_form(N_MC, p))
        rate, outcomes = mc_majority_rate_bernoulli(rng, N_MC, p_float, T_MC)
        se = math.sqrt(cf * (1 - cf) / T_MC)
        z = abs(rate - cf) / se if se > 0 else float("inf")
        case_ok = z <= Z_GATE
        ok = ok and case_ok
        detail[name] = {
            "closed_form": round(cf, ROUND_DP),
            "empirical_rate": round(rate, ROUND_DP),
            "abs_z": round(z, ROUND_DP),
            "within_3sigma": case_ok,
        }
    detail["direction"] = "abs(empirical - closed_form) <= 3*stderr (agreement)"
    return ok, detail


def gate_g2():
    """Exactly-true: exhaustive 2^n enumeration EQUALS the closed-form Fraction for
    every small odd n and every competence, AND the monotonicity direction holds
    exactly -- p>1/2 strictly increasing toward 1, p<1/2 strictly decreasing toward 0,
    p=1/2 flat at 1/2. Fraction-exact, no tolerance."""
    per_p = {}
    ok = True
    for name, p in (("p_3_5", P_ABOVE), ("p_2_5", P_BELOW), ("p_1_2", P_HALF)):
        grid = []
        enum_eq_closed = True
        for n in N_ENUM:
            enum = majority_correct_enumeration(n, p)
            closed = majority_correct_closed_form(n, p)
            if enum != closed:  # exact Fraction equality
                enum_eq_closed = False
            grid.append((n, closed))
        vals = [c for _, c in grid]
        if p > P_HALF:
            mono = all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
            direction = "strictly_increasing_toward_1"
            endpoint_ok = vals[-1] > vals[0] and vals[-1] > p
        elif p < P_HALF:
            mono = all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))
            direction = "strictly_decreasing_toward_0"
            endpoint_ok = vals[-1] < vals[0] and vals[-1] < p
        else:
            mono = all(v == P_HALF for v in vals)
            direction = "flat_at_one_half"
            endpoint_ok = all(v == P_HALF for v in vals)
        case_ok = enum_eq_closed and mono and endpoint_ok
        ok = ok and case_ok
        per_p[name] = {
            "enum_equals_closed_form_exact": enum_eq_closed,
            "M_grid": {str(n): str(c) for n, c in grid},
            "monotone_direction_holds": mono,
            "direction": direction,
            "endpoint_ok": endpoint_ok,
        }
    return ok, per_p


def gate_g3(rng):
    """Robustness / distribution-free shift: the majority-correct rate depends ONLY on
    the competence p (the threshold-crossing probability), not on the value
    distribution of each member's private signal. Two legs, both at N_MC, p=0.60:
      (a) EXACT: a monotone transform (exp) of the SAME uniform draw with a matched
          threshold yields BIT-IDENTICAL votes to a Bernoulli pass over the same
          stream -> the two majority-rate sequences are exactly equal (diff = 0).
      (b) STATISTICAL: an INDEPENDENT heavy-tailed (Cauchy) latent stream calibrated
          to the same competence p yields a majority rate within 3 sigma of the
          Bernoulli/closed-form value. Distribution-free confirmed.
    """
    p = P_ABOVE
    p_float = float(p)
    cf = float(majority_correct_closed_form(N_MC, p))

    # Leg (a): exact bit-identity under a monotone value transform (shared stream).
    rng_a = random.Random(SEED + 1)
    rate_mono, out_mono = mc_majority_rate_monotone_paired(rng_a, N_MC, p_float, T_MC)
    rng_b = random.Random(SEED + 1)  # SAME sub-stream -> identical draws
    rate_bern, out_bern = mc_majority_rate_bernoulli_stream(rng_b, N_MC, p_float, T_MC)
    exact_identical = out_mono == out_bern
    exact_rate_equal = rate_mono == rate_bern

    # Leg (b): independent heavy-tailed value distribution, same competence.
    rate_heavy, _ = mc_majority_rate_heavytail(rng, N_MC, p_float, T_MC)
    se = math.sqrt(cf * (1 - cf) / T_MC)
    z_heavy = abs(rate_heavy - cf) / se if se > 0 else float("inf")
    heavy_ok = z_heavy <= Z_GATE

    ok = exact_identical and exact_rate_equal and heavy_ok
    detail = {
        "closed_form": round(cf, ROUND_DP),
        "exact_leg": {
            "monotone_rate": round(rate_mono, ROUND_DP),
            "bernoulli_rate": round(rate_bern, ROUND_DP),
            "votes_bit_identical": exact_identical,
            "rate_exactly_equal": exact_rate_equal,
            "direction": "monotone value-transform leaves every vote identical (exact ==)",
        },
        "statistical_leg": {
            "heavytail_cauchy_rate": round(rate_heavy, ROUND_DP),
            "abs_z_vs_closed_form": round(z_heavy, ROUND_DP),
            "within_3sigma": heavy_ok,
            "direction": "abs(heavytail_rate - closed_form) <= 3*stderr (distribution-free)",
        },
    }
    return ok, detail


def compute():
    # Fresh RNG per full run: reproducible in-process AND cross-invocation.
    rng = random.Random(SEED)

    g1_ok, g1 = gate_g1(rng)
    g2_ok, g2 = gate_g2()
    g3_ok, g3 = gate_g3(rng)

    all_pass = g1_ok and g2_ok and g3_ok
    first_failing = None
    for gname, gok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok)):
        if not gok:
            first_failing = gname
            break

    return {
        "head": "condorcet-jury-committee",
        "seed": SEED,
        "constants": {
            "z_gate": Z_GATE, "T_mc": T_MC, "N_mc": N_MC,
            "N_enum": list(N_ENUM),
            "p_above": str(P_ABOVE), "p_below": str(P_BELOW), "p_half": str(P_HALF),
        },
        "g1_statistical_agreement": g1,
        "g2_exact_enumeration": g2,
        "g3_robustness_shift": g3,
        "gates": {
            "G1_statistical_3sigma": g1_ok,
            "G2_exact_enumeration": g2_ok,
            "G3_robustness_shift": g3_ok,
        },
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert canonical(r1) == canonical(r2), "non-deterministic: double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if r1["all_pass"] else "false"))
    g1a = r1["g1_statistical_agreement"]
    print("G1_above_abs_z=%s" % g1a["above_p0.60"]["abs_z"])
    print("G1_below_abs_z=%s" % g1a["below_p0.40"]["abs_z"])
    g3 = r1["g3_robustness_shift"]
    print("G3_exact_bit_identical=%s" % g3["exact_leg"]["votes_bit_identical"])
    print("G3_heavytail_abs_z=%s" % g3["statistical_leg"]["abs_z_vs_closed_form"])
    print("RESULTS_SHA256=%s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
