#!/usr/bin/env python3
"""Bertrand's ballot theorem - firsthand verifier (PROPOSAL 220 -> VERDICT 233).

Counterintuitive-but-exactly-true: in a count where candidate A finishes with a
votes and B with b < a votes, and the ballots are opened in uniformly random
order, the probability that A is STRICTLY ahead of B at EVERY prefix of the
count (A leads throughout, never tied, never behind) is EXACTLY (a-b)/(a+b) -
it depends only on the winning margin ratio, NOT on A's vote share a/(a+b).
Equivalently, the number of countings in which A leads throughout equals
    (a-b)/(a+b) * C(a+b, a).

Stdlib-only. SEED=20260717, all randomness from a single random.Random(20260717)
consumed in a fixed, documented order: for each (a,b) in MC_PAIRS (in listed
order), MC_T ballot shuffles are drawn back-to-back via rng.shuffle before moving
to the next pair. Deterministic across in-process double-run and separate
cross-invocation.

Gate battery (each read in ITS OWN direction):
  G1 EXACT identity (Fraction, equality): for several (a,b), the brute-force
     favorable count over ALL distinct arrangements gives
     Fraction(brute, C(a+b,a)) == Fraction(a-b, a+b). PASS = exact equality.
  G2 EXACT scale-invariance (Fraction, equality): the probability depends only
     on the margin ratio - Fraction(a-b,a+b) == Fraction(k*a-k*b, k*a+k*b) for
     k in {2,3,5}, AND the brute count identity still holds for each enumerable
     scaled case. PASS = exact equality.
  G3 MONTE-CARLO agreement (|z| <= 3 PASS): empirical lead-throughout rate over
     MC_T shuffles agrees with (a-b)/(a+b) within 3 sigma.
  G4 FALSIFIABILITY (naive REJECTED at |z| > 5): the plausible-but-WRONG model
     "probability = a/(a+b)" (A's vote share / P(first vote is A)) is rejected
     by the SAME Monte-Carlo sample at large |z|, while the true (a-b)/(a+b)
     is NOT rejected (|z|<=3, from G3). An EXACT leg also confirms a corrupted
     favorable-count formula != the brute count.
"""
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction

SEED = 20260717
G1_PAIRS = [(3, 1), (4, 2), (5, 2), (5, 3), (6, 3), (7, 2)]  # exact identity
G2_BASE = (2, 1)                    # base margin ratio for scale-invariance
G2_KS = (2, 3, 5)                   # scale factors
MC_PAIRS = [(3, 1), (5, 2), (7, 3)]  # Monte-Carlo cells
MC_T = 200000                       # trials per Monte-Carlo cell
Z_AGREE = 3.0                       # G3 two-sided agreement band
Z_REJECT = 5.0                      # G4 falsifiability rejection floor


def comb(n, k):
    return math.comb(n, k)


def frac_str(f):
    return "{0}/{1}".format(f.numerator, f.denominator)


def leads_throughout(seq):
    """True iff the running (A-minus-B) lead is strictly positive at every
    prefix of seq (seq: iterable of +1 for an A ballot, -1 for a B ballot)."""
    running = 0
    for v in seq:
        running += v
        if running <= 0:
            return False
    return True


def brute_favorable(a, b):
    """Number of distinct A/B arrangements (a A's, b B's) in which A is strictly
    ahead at every prefix, by full enumeration over the C(a+b,a) placements of
    the A-ballots."""
    n = a + b
    count = 0
    for combo in itertools.combinations(range(n), a):
        aset = set(combo)
        seq = (1 if i in aset else -1 for i in range(n))
        if leads_throughout(seq):
            count += 1
    return count


# ---- G1: EXACT identity  brute/C(a+b,a) == (a-b)/(a+b) --------------------
def gate_g1():
    per_pair = {}
    ok = True
    for (a, b) in G1_PAIRS:
        total = comb(a + b, a)
        fav = brute_favorable(a, b)
        emp = Fraction(fav, total)
        closed = Fraction(a - b, a + b)
        eq = (emp == closed)
        ok = ok and eq
        per_pair["{0},{1}".format(a, b)] = {
            "favorable": fav,
            "total": total,
            "brute_prob": frac_str(emp),
            "closed_form": frac_str(closed),
            "equal": eq,
        }
    return ok, per_pair


# ---- G2: EXACT scale-invariance (margin-ratio only) -----------------------
def gate_g2():
    a0, b0 = G2_BASE
    base = Fraction(a0 - b0, a0 + b0)
    per_k = {}
    ratio_ok = True
    count_ok = True
    # k=1 base case included so the enumerable-count leg covers the base too.
    for k in (1,) + G2_KS:
        a, b = k * a0, k * b0
        scaled = Fraction(a - b, a + b)
        req = (scaled == base)
        ratio_ok = ratio_ok and req
        total = comb(a + b, a)
        fav = brute_favorable(a, b)
        cid = (Fraction(fav, total) == base)
        count_ok = count_ok and cid
        per_k[str(k)] = {
            "a": a,
            "b": b,
            "scaled_ratio": frac_str(scaled),
            "ratio_equals_base": req,
            "favorable": fav,
            "total": total,
            "brute_prob": frac_str(Fraction(fav, total)),
            "count_identity_holds": cid,
        }
    ok = ratio_ok and count_ok
    return ok, {
        "base_pair": [a0, b0],
        "base_ratio": frac_str(base),
        "per_k": per_k,
        "all_ratios_equal_base": ratio_ok,
        "all_count_identities_hold": count_ok,
    }


# ---- Monte-Carlo lead-throughout rate over T shuffles ---------------------
def mc_stats(rng, a, b, T):
    """Return (mean, se) of the lead-throughout indicator over T random ballot
    orderings. se = sqrt(p(1-p)/T) with p the empirical mean (binomial SE)."""
    ballot = [1] * a + [-1] * b
    hits = 0
    for _ in range(T):
        rng.shuffle(ballot)
        if leads_throughout(ballot):
            hits += 1
    mean = hits / T
    var = mean * (1.0 - mean)
    se = math.sqrt(var / T)
    return mean, se


# ---- G3: Monte-Carlo agreement with (a-b)/(a+b), |z| <= 3 -----------------
def gate_g3(rng, mc):
    per_pair = {}
    ok = True
    for (a, b) in MC_PAIRS:
        mean, se = mc[(a, b)]
        target = float(Fraction(a - b, a + b))
        z = (mean - target) / se
        good = (abs(z) <= Z_AGREE)
        ok = ok and good
        per_pair["{0},{1}".format(a, b)] = {
            "target": round(target, 9),
            "target_frac": frac_str(Fraction(a - b, a + b)),
            "mean": round(mean, 9),
            "se": round(se, 12),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    return ok, per_pair


# ---- G4: falsifiability - naive a/(a+b) REJECTED at |z| > 5 ----------------
def gate_g4(rng, mc):
    per_pair = {}
    naive_ok = True
    for (a, b) in MC_PAIRS:
        mean, se = mc[(a, b)]
        naive = float(Fraction(a, a + b))          # A's vote share = P(first is A)
        z_naive = (mean - naive) / se
        rejected = (abs(z_naive) > Z_REJECT)
        naive_ok = naive_ok and rejected
        per_pair["{0},{1}".format(a, b)] = {
            "naive_value": round(naive, 9),
            "naive_frac": frac_str(Fraction(a, a + b)),
            "mean": round(mean, 9),
            "z_naive": round(z_naive, 6),
            "naive_rejected": rejected,
        }
    # EXACT leg: a corrupted favorable-count formula must differ from the brute
    # count. Corrupt = A's-share count a/(a+b)*C(a+b,a) (the naive model's count)
    # which differs from (a-b)/(a+b)*C whenever b != 0.
    exact_leg_ok = True
    exact_leg = {}
    for (a, b) in G1_PAIRS:
        total = comb(a + b, a)
        fav = brute_favorable(a, b)
        corrupt = Fraction(a, a + b) * total       # wrong closed form's count
        neq = (corrupt != fav)
        exact_leg_ok = exact_leg_ok and neq
        exact_leg["{0},{1}".format(a, b)] = {
            "brute_favorable": fav,
            "corrupt_count": frac_str(Fraction(a, a + b) * total),
            "corrupt_neq_brute": neq,
        }
    ok = naive_ok and exact_leg_ok
    return ok, {
        "naive_model": "prob = a/(a+b) (A vote share / P(first vote is A))",
        "per_pair": per_pair,
        "all_naive_rejected": naive_ok,
        "exact_corrupt_count_leg": exact_leg,
        "all_corrupt_neq_brute": exact_leg_ok,
    }


def run_battery():
    rng = random.Random(SEED)
    # Draw ALL Monte-Carlo cells up front in fixed documented order so both G3
    # (agreement vs true) and G4 (rejection of naive) read the SAME samples.
    mc = {}
    for (a, b) in MC_PAIRS:
        mc[(a, b)] = mc_stats(rng, a, b, MC_T)

    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2()
    g3_ok, g3 = gate_g3(rng, mc)
    g4_ok, g4 = gate_g4(rng, mc)

    gates = {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok}
    sim_ready = all(gates.values())
    return {
        "proposal": 220,
        "verdict": 233,
        "theorem": "Bertrand ballot theorem (lead-throughout)",
        "slot": "round-52 UNRELATED (fleet->venture->game->unrelated)",
        "seed": SEED,
        "mc_pairs": [list(p) for p in MC_PAIRS],
        "mc_trials": MC_T,
        "g1_exact_identity": g1,
        "g2_scale_invariance": g2,
        "g3_montecarlo": g3,
        "g4_falsifiability": g4,
        "gates": gates,
        "sim_ready": sim_ready,
    }


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


if __name__ == "__main__":
    import sys

    r1 = run_battery()
    r2 = run_battery()
    d1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    d2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    determinism = (d1 == d2)
    sim_ready = r1["sim_ready"]
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    print("sim_ready={0}".format(sim_ready))
    sys.exit(0 if (sim_ready and determinism) else 1)
