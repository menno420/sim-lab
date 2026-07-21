#!/usr/bin/env python3
"""Slotted-ALOHA finite-n throughput ceiling -- self-certifying verifier.

Fleet framing: n agents contend for one shared slotted resource (a channel,
a lock, a token). Each agent independently transmits in a slot with
probability p. A slot SUCCEEDS iff exactly one agent transmits. The
single-slot success throughput is

    S(n, p) = n * p * (1 - p) ** (n - 1)          (exact, binomial)

maximised at the transmit probability p* = 1/n, giving the exact rational
ceiling

    S_max(n) = (1 - 1/n) ** (n - 1) = (n - 1) ** (n - 1) / n ** (n - 1)

which decreases monotonically to the limit 1/e ~= 0.367879... as n -> inf.
So an arbitrarily large contending fleet can utilise a shared slotted
resource at most about 36.8% of the time.

Four gates, each evaluated in its own direction:
  G1  EXACT optimality identity via fractions.Fraction (zero error).
  G2  Monte-Carlo agreement of empirical throughput at p*=1/n (|z| < 3).
  G3  invariance / robustness: relabeling invariance of the success count,
      plus exact monotone-decrease and the strict 1/e lower bound.
  G4  falsifiability: reject the naive "throughput == offered load == 1" rule.

stdlib only: json, hashlib, math, random, fractions.
Deterministic: SEED is a hardcoded module constant; the in-process double run
and a separate re-invocation are byte-identical.
"""
import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

NS = [2, 3, 4, 5, 8, 10, 16, 32, 64, 100]
MC_NS = [2, 3, 5, 10, 25, 100]
TRIALS = 200000
G3_N = 16
G3_TRIALS = 100000
GRID = 200
FALSIFY_MIN_Z = 6.0


def s_exact(n, p):
    """Exact single-slot success throughput S(n,p) = n p (1-p)^(n-1)."""
    p = Fraction(p)
    return n * p * (1 - p) ** (n - 1)


def s_max_exact(n):
    """Exact ceiling at p*=1/n: (1-1/n)^(n-1) = (n-1)^(n-1)/n^(n-1)."""
    return Fraction((n - 1) ** (n - 1), n ** (n - 1))


def gate_g1():
    """G1 -- EXACT identity + argmax optimality in pure rational arithmetic."""
    per_n = {}
    ok = True
    for n in NS:
        closed = s_max_exact(n)
        at_popt = s_exact(n, Fraction(1, n))
        identity_ok = (closed == at_popt)
        argmax_is_popt = True
        for k in range(1, GRID):
            if s_exact(n, Fraction(k, GRID)) > at_popt:
                argmax_is_popt = False
                break
        per_n[str(n)] = {
            "closed_form": str(closed),
            "float": round(float(closed), 12),
            "identity_ok": identity_ok,
            "argmax_is_popt": argmax_is_popt,
        }
        ok = ok and identity_ok and argmax_is_popt
    return {"pass": bool(ok), "grid": GRID, "per_n": per_n}


def run_mc(seed):
    """Simulate n independent Bernoulli(1/n) transmitters per slot; count the
    slots in which exactly one agent transmits (a success)."""
    rng = random.Random(seed)
    out = {}
    for n in MC_NS:
        succ = 0
        for _ in range(TRIALS):
            c = 0
            for _ in range(n):
                if rng.randrange(n) == 0:
                    c += 1
                    if c == 2:
                        break
            if c == 1:
                succ += 1
        out[n] = succ
    return out


def gate_g2(mc):
    """G2 -- empirical throughput at p*=1/n agrees with S_max(n), |z| < 3."""
    per_n = {}
    ok = True
    max_absz = 0.0
    for n in MC_NS:
        succ = mc[n]
        s_theory = float(s_max_exact(n))
        s_hat = succ / TRIALS
        se = math.sqrt(s_theory * (1 - s_theory) / TRIALS)
        z = (s_hat - s_theory) / se
        absz = abs(z)
        max_absz = max(max_absz, absz)
        passed = absz < 3.0
        per_n[str(n)] = {
            "trials": TRIALS,
            "successes": succ,
            "s_hat": round(s_hat, 8),
            "s_theory": round(s_theory, 8),
            "z": round(z, 4),
            "abs_z_lt_3": passed,
        }
        ok = ok and passed
    return {"pass": bool(ok), "trials_per_n": TRIALS,
            "max_abs_z": round(max_absz, 4), "per_n": per_n}


def gate_g3(seed):
    """G3 -- relabeling invariance of the success count, plus exact
    monotone-decrease and the strict 1/e lower bound."""
    rng = random.Random(seed)
    n = G3_N
    perm = list(range(n))
    prng = random.Random(seed ^ 0x5A5A5A5A)
    prng.shuffle(perm)
    bijection = (sorted(perm) == list(range(n)))
    succ_plain = 0
    succ_perm = 0
    for _ in range(G3_TRIALS):
        transmitters = [a for a in range(n) if rng.randrange(n) == 0]
        relabeled = [perm[a] for a in transmitters]
        if len(transmitters) == 1:
            succ_plain += 1
        if len(relabeled) == 1:
            succ_perm += 1
    relabel_invariant = bijection and (succ_plain == succ_perm) and succ_plain > 0
    exact_vals = [s_max_exact(k) for k in NS]
    monotone = all(exact_vals[i] > exact_vals[i + 1]
                   for i in range(len(exact_vals) - 1))
    inv_e = 1.0 / math.e
    above_limit = all(float(v) > inv_e for v in exact_vals)
    ok = relabel_invariant and monotone and above_limit
    return {
        "pass": bool(ok),
        "relabel": {
            "n": n, "trials": G3_TRIALS, "perm_is_bijection": bijection,
            "successes_plain": succ_plain, "successes_relabeled": succ_perm,
            "invariant": relabel_invariant,
        },
        "structure": {
            "monotone_decreasing_exact": monotone,
            "strictly_above_inv_e": above_limit,
            "inv_e": round(inv_e, 12),
        },
    }


def gate_g4(mc):
    """G4 -- falsifiability: the same data rejects the naive rule that the
    throughput equals the offered load G = n*p* = 1.0 (ignoring collisions)."""
    naive = 1.0
    per_n = {}
    ok = True
    min_absz = float("inf")
    for n in MC_NS:
        succ = mc[n]
        s_hat = succ / TRIALS
        s_theory = float(s_max_exact(n))
        se = math.sqrt(s_theory * (1 - s_theory) / TRIALS)
        z_naive = (s_hat - naive) / se
        absz = abs(z_naive)
        min_absz = min(min_absz, absz)
        rejected = absz > FALSIFY_MIN_Z
        per_n[str(n)] = {
            "s_hat": round(s_hat, 8),
            "naive_claim": naive,
            "z_vs_naive": round(z_naive, 2),
            "rejected": rejected,
        }
        ok = ok and rejected
    return {"pass": bool(ok),
            "naive_rule": "throughput == offered load n*p* == 1.0",
            "falsify_min_z": FALSIFY_MIN_Z,
            "min_abs_z": round(min_absz, 2), "per_n": per_n}


def compute_results():
    mc = run_mc(SEED)
    gates = {
        "G1": gate_g1(),
        "G2": gate_g2(mc),
        "G3": gate_g3(SEED),
        "G4": gate_g4(mc),
    }
    order = ["G1", "G2", "G3", "G4"]
    all_pass = all(gates[k]["pass"] for k in order)
    first_fail = next((k for k in order if not gates[k]["pass"]), None)
    return {
        "claim": ("slotted-ALOHA single-slot success throughput "
                  "S(n,p)=n*p*(1-p)^(n-1) is maximised at p*=1/n with exact "
                  "ceiling S_max(n)=(n-1)^(n-1)/n^(n-1), decreasing monotonically "
                  "to 1/e"),
        "seed": SEED,
        "params": {"NS": NS, "MC_NS": MC_NS, "trials": TRIALS, "grid": GRID,
                   "g3_n": G3_N, "g3_trials": G3_TRIALS,
                   "falsify_min_z": FALSIFY_MIN_Z},
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_fail,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute_results()
    r2 = compute_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    in_process_identical = (c1 == c2)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    summary = {
        "in_process_double_run_identical": in_process_identical,
        "results_sha256": digest,
        "all_gates_pass": r1["all_gates_pass"],
        "first_failing_gate": r1["first_failing_gate"],
        "decision": r1["decision"],
        "gate_z": {
            "G1_exact_error": "0 (exact rational identity)",
            "G2_max_abs_z": r1["gates"]["G2"]["max_abs_z"],
            "G4_min_abs_z": r1["gates"]["G4"]["min_abs_z"],
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("results_sha256=" + digest)
    if not in_process_identical:
        raise SystemExit("NON-DETERMINISTIC: in-process double run differs")
    if not r1["all_gates_pass"]:
        raise SystemExit("GATE FAILURE: " + str(r1["first_failing_gate"]))


if __name__ == "__main__":
    main()
