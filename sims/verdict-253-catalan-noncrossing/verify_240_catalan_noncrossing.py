#!/usr/bin/env python3
"""PROPOSAL 240 - Catalan numbers count non-crossing handshakes.

Claim (exact). Fix 2n points labelled 0..2n-1 in circular order on a circle.
A perfect matching pairs them into n chords; there are (2n-1)!! = 1*3*5*...*
(2n-1) such matchings. Draw one uniformly at random. The probability it is
NON-CROSSING (no two chords cross) is EXACTLY

        P(n) = C_n / (2n-1)!!,

where C_n = binom(2n,n)/(n+1) is the n-th Catalan number, because the number
of non-crossing perfect matchings of 2n points is exactly C_n. Headline exact
values: n=2 -> 2/3 (3 matchings, 2 non-crossing); n=3 -> 1/3 (15 matchings,
5 non-crossing); n=4 -> C_4/7!! = 14/105 = 2/15.

Two chords (a,b),(c,d) on the labelled circle cross iff exactly one of {c,d}
lies strictly inside the arc from a to b. Concretely, with each chord written
so its smaller endpoint is first (a<b, c<d), they cross iff a<c<b<d or
c<a<d<b (standard interleaving test).

SEED = 20260717. build_results() is a pure function of SEED and the module
constants (each Monte-Carlo stream consumes its own random.Random(SEED) in a
fixed order; no wall-clock / PID / unordered-set iteration enters the hashed
payload), so an in-process double-run and a separate re-invocation are
byte-identical; results_sha256 is the sha256 of the canonical results dict.

Four gates, each in its own direction:
  G1 EXACT      - closed form == brute force, exact rational (fractions.Fraction).
                  C_n computed three independent ways (recurrence,
                  binom(2n,n)/(n+1), binom(2n,n)-binom(2n,n+1)) agree; brute-
                  force enumeration of all (2n-1)!! matchings counts exactly
                  C_n non-crossing ones; P_exact(n)=Fraction(C_n,(2n-1)!!)
                  equals the brute-force non_crossing/total EXACTLY.
  G2 MC AGREE   - sampled non-crossing frequency agrees with the exact P at
                  |z| < Z_ACCEPT, for n=3 (P=1/3) and n=4 (P=2/15).
  G3 INVARIANCE - the estimate is invariant under a random dihedral relabeling
                  (rotation + optional reflection) of the circle: the n=3 MC
                  still agrees at |z| < Z_ACCEPT; and, exactly, the brute-force
                  non-crossing COUNT is identical under all 2n rotations and
                  reflection for n in {3,4}.
  G4 FALSIFY    - on the SAME n=3 MC sample, the plausible naive belief
                  P_naive = 1/2 ("half of all matchings are planar") is
                  rejected at |z_naive| >= Z_REJECT; and the naive
                  "non-crossing count = 2^(n-1)" fails exactly (2^2=4 != 5=C_3).

Stdlib only: json, hashlib, math, random, fractions, itertools.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# ---- gate constants -------------------------------------------------------
N_EXACT = [2, 3, 4, 5, 6]        # n over which the three C_n routes must agree
N_BRUTE = [2, 3, 4]              # n over which we enumerate all matchings
MC_N = 200_000                   # Monte-Carlo trials per estimate
Z_ACCEPT = 3.0
Z_REJECT = 6.0


# ---- Catalan number, three independent exact routes -----------------------
def catalan_recurrence(n):
    """C_n via C_0=1, C_{k+1}=sum_{i=0}^{k} C_i*C_{k-1-i} (exact integers)."""
    C = [1]
    for k in range(1, n + 1):
        C.append(sum(C[i] * C[k - 1 - i] for i in range(k)))
    return C[n]


def catalan_binom_over_np1(n):
    """C_n = binom(2n,n)/(n+1) via Fraction; asserted integral."""
    val = Fraction(math.comb(2 * n, n), n + 1)
    assert val.denominator == 1, "binom(2n,n)/(n+1) not integral"
    return int(val)


def catalan_binom_difference(n):
    """C_n = binom(2n,n) - binom(2n,n+1) (exact integers)."""
    return math.comb(2 * n, n) - math.comb(2 * n, n + 1)


def double_factorial_odd(n):
    """(2n-1)!! = 1*3*5*...*(2n-1) = number of perfect matchings of 2n points."""
    prod = 1
    for k in range(1, 2 * n, 2):
        prod *= k
    return prod


# ---- crossing test and matching enumeration -------------------------------
def chords_cross(a, b, c, d):
    """Chords (a,b),(c,d) with a<b, c<d cross iff a<c<b<d or c<a<d<b."""
    return (a < c < b < d) or (c < a < d < b)


def is_noncrossing(matching):
    """matching: list of (a,b) with a<b. True iff no two chords cross."""
    for i in range(len(matching)):
        a, b = matching[i]
        for j in range(i + 1, len(matching)):
            c, d = matching[j]
            if chords_cross(a, b, c, d):
                return False
    return True


def all_matchings(points):
    """Yield every perfect matching of the list `points` as a list of (a,b),
    a<b. Pairs the first point with each remaining point recursively."""
    if not points:
        yield []
        return
    first = points[0]
    rest = points[1:]
    for i in range(len(rest)):
        partner = rest[i]
        remaining = rest[:i] + rest[i + 1:]
        edge = (first, partner) if first < partner else (partner, first)
        for sub in all_matchings(remaining):
            yield [edge] + sub


def random_matching(rng, m):
    """Uniform random perfect matching of m=2n points labelled 0..m-1.
    Greedy: pair the first unmatched point with a uniformly random other
    unmatched point -- uniform over all (2n-1)!! matchings."""
    remaining = list(range(m))
    chords = []
    while remaining:
        a = remaining.pop(0)
        j = rng.randrange(len(remaining))
        b = remaining.pop(j)
        chords.append((a, b) if a < b else (b, a))
    return chords


def relabel(matching, m, r, reflect):
    """Apply a dihedral relabeling to the circle labels: rotate by r, then
    optionally reflect (p -> -p mod m). Non-crossing is invariant under this."""
    def t(p):
        q = (p + r) % m
        if reflect:
            q = (-q) % m
        return q
    out = []
    for a, b in matching:
        x, y = t(a), t(b)
        out.append((x, y) if x < y else (y, x))
    return out


# ---- gates ----------------------------------------------------------------
def gate1_exact():
    error_count = 0
    catalan_rows = []
    for n in N_EXACT:
        c_rec = catalan_recurrence(n)
        c_bin = catalan_binom_over_np1(n)
        c_dif = catalan_binom_difference(n)
        agree = (c_rec == c_bin == c_dif)
        if not agree:
            error_count += 1
        catalan_rows.append({
            "n": n,
            "C_recurrence": c_rec,
            "C_binom_over_n_plus_1": c_bin,
            "C_binom_difference": c_dif,
            "three_routes_equal": agree,
        })

    brute_rows = []
    p_exact_map = {}
    for n in N_BRUTE:
        m = 2 * n
        total = 0
        noncrossing = 0
        for matching in all_matchings(list(range(m))):
            total += 1
            if is_noncrossing(matching):
                noncrossing += 1
        c_n = catalan_recurrence(n)
        dfact = double_factorial_odd(n)
        total_ok = (total == dfact)
        count_ok = (noncrossing == c_n)
        # exact rational identity: brute-force freq == closed form C_n/(2n-1)!!
        p_brute = Fraction(noncrossing, total)
        p_closed = Fraction(c_n, dfact)
        prob_ok = (p_brute == p_closed)
        if not (total_ok and count_ok and prob_ok):
            error_count += 1
        p_exact_map[str(n)] = str(p_closed)
        brute_rows.append({
            "n": n,
            "total_matchings": total,
            "double_factorial_2n_minus_1": dfact,
            "total_equals_double_factorial": total_ok,
            "noncrossing_count": noncrossing,
            "C_n": c_n,
            "noncrossing_equals_C_n": count_ok,
            "P_brute_fraction": str(p_brute),
            "P_closed_fraction": str(p_closed),
            "P_exact_equal": prob_ok,
        })

    ok = (error_count == 0)
    return ok, {
        "catalan_three_routes": catalan_rows,
        "brute_force_matchings": brute_rows,
        "P_exact": p_exact_map,
        "error_count": error_count,
        "pass_if": "error_count == 0",
    }


def _mc_estimate(n, trials):
    """Fresh seeded stream: fraction of `trials` uniform random matchings of
    2n points that are non-crossing. Returns (hits, trials)."""
    rng = random.Random(SEED)
    m = 2 * n
    hits = 0
    for _ in range(trials):
        matching = random_matching(rng, m)
        if is_noncrossing(matching):
            hits += 1
    return hits, trials


def _mc_estimate_dihedral(n, trials):
    """Like _mc_estimate but each trial applies a random dihedral relabeling
    (rotation r in [0,2n), optional reflection) to the labels before the
    crossing test. Non-crossing is invariant, so the estimate must still
    agree with P(n)."""
    rng = random.Random(SEED)
    m = 2 * n
    hits = 0
    for _ in range(trials):
        matching = random_matching(rng, m)
        r = rng.randrange(m)
        reflect = bool(rng.getrandbits(1))
        relabeled = relabel(matching, m, r, reflect)
        if is_noncrossing(relabeled):
            hits += 1
    return hits, trials


def _z(p_hat, p, k):
    se = math.sqrt(p * (1.0 - p) / k)
    return (p_hat - p) / se


def gate2_mc_agreement(sample_n3):
    rows = []
    all_ok = True
    # n=3 uses the shared sample (also consumed by G4); n=4 is independent.
    for n, sample in [(3, sample_n3), (4, _mc_estimate(4, MC_N))]:
        hits, k = sample
        p_hat = hits / k
        c_n = catalan_recurrence(n)
        p = float(Fraction(c_n, double_factorial_odd(n)))
        z = _z(p_hat, p, k)
        ok = abs(z) < Z_ACCEPT
        all_ok = all_ok and ok
        rows.append({
            "n": n,
            "trials": k,
            "hits": hits,
            "p_hat": round(p_hat, 6),
            "P_exact": str(Fraction(c_n, double_factorial_odd(n))),
            "P_float": round(p, 6),
            "z": round(z, 4),
            "z_accept": Z_ACCEPT,
            "ok": ok,
        })
    return all_ok, {
        "points": rows,
        "pass_if": "abs(z) < Z_ACCEPT for both n=3 and n=4",
    }


def gate3_invariance():
    # (a) Monte-Carlo under random dihedral relabeling, n=3, must agree with 1/3.
    hits, k = _mc_estimate_dihedral(3, MC_N)
    p_hat = hits / k
    p = float(Fraction(catalan_recurrence(3), double_factorial_odd(3)))
    z = _z(p_hat, p, k)
    mc_ok = abs(z) < Z_ACCEPT

    # (b) exact: brute-force non-crossing COUNT identical under all 2n rotations
    #     and reflection, for n in {3,4}.
    exact_rows = []
    exact_all_true = True
    for n in [3, 4]:
        m = 2 * n
        base = catalan_recurrence(n)
        matchings = list(all_matchings(list(range(m))))
        invariant = True
        for reflect in (False, True):
            for r in range(m):
                cnt = 0
                for matching in matchings:
                    if is_noncrossing(relabel(matching, m, r, reflect)):
                        cnt += 1
                if cnt != base:
                    invariant = False
        if not invariant:
            exact_all_true = False
        exact_rows.append({
            "n": n,
            "C_n": base,
            "count_invariant_over_all_rotations_and_reflection": invariant,
        })

    ok = mc_ok and exact_all_true
    return ok, {
        "mc_dihedral_n3": {
            "trials": k, "hits": hits,
            "p_hat": round(p_hat, 6),
            "P_exact": "1/3",
            "z": round(z, 4),
            "z_accept": Z_ACCEPT,
            "ok": mc_ok,
        },
        "exact_invariance": exact_rows,
        "exact_invariance_all_true": exact_all_true,
        "pass_if": "mc |z| < Z_ACCEPT AND exact invariance all True",
    }


def gate4_falsify(sample_n3):
    hits, k = sample_n3
    p_hat = hits / k

    # naive belief P_naive = 1/2 -- reject on the SAME n=3 sample.
    p_naive = 0.5
    z_naive = _z(p_hat, p_naive, k)
    naive_rejected = abs(z_naive) >= Z_REJECT

    # naive "non-crossing count = 2^(n-1)" fails exactly: 2^(3-1)=4 != 5=C_3.
    pow_val = 2 ** (3 - 1)
    c3 = catalan_recurrence(3)
    pow_fails = (pow_val != c3)

    ok = naive_rejected and pow_fails
    return ok, {
        "naive_half": {
            "claim": "P == 1/2 (half of all matchings are non-crossing)",
            "p_hat": round(p_hat, 6),
            "P_naive": p_naive,
            "z_naive": round(z_naive, 4),
            "z_reject": Z_REJECT,
            "rejected": naive_rejected,
        },
        "naive_power_of_two": {
            "claim": "non-crossing count == 2^(n-1)",
            "value_2_pow_n_minus_1_at_n3": pow_val,
            "C_3": c3,
            "fails": pow_fails,
        },
        "pass_if": "abs(z_naive) >= Z_REJECT and 2^(n-1) != C_n",
    }


def build_results():
    sample_n3 = _mc_estimate(3, MC_N)

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample_n3)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample_n3)

    gates = {
        "G1_exact_catalan": {"name": "closed form == brute force, exact rational",
                             "ok": g1_ok, **g1},
        "G2_montecarlo_agreement": {"name": "sampled non-crossing freq agrees with C_n/(2n-1)!!",
                                    "ok": g2_ok, **g2},
        "G3_invariance": {"name": "estimate invariant under dihedral relabeling; exact count invariant",
                          "ok": g3_ok, **g3},
        "G4_falsifiability": {"name": "naive P=1/2 rejected; 2^(n-1) count foil fails",
                              "ok": g4_ok, **g4},
    }
    order = ["G1_exact_catalan", "G2_montecarlo_agreement",
             "G3_invariance", "G4_falsifiability"]
    first_failing = next((g for g in order if not gates[g]["ok"]), None)
    all_pass = first_failing is None

    return {
        "claim": ("catalan_noncrossing: a uniformly random perfect matching of "
                  "2n circle points is non-crossing with probability exactly "
                  "C_n/(2n-1)!!, C_n = binom(2n,n)/(n+1); n=2->2/3, n=3->1/3, "
                  "n=4->2/15"),
        "seed": SEED,
        "params": {
            "n_exact": N_EXACT,
            "n_brute": N_BRUTE,
            "mc_trials": MC_N,
            "z_accept": Z_ACCEPT,
            "z_reject": Z_REJECT,
        },
        "P_exact": {str(n): str(Fraction(catalan_recurrence(n),
                                          double_factorial_odd(n)))
                    for n in N_BRUTE},
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    import sys
    selfcheck = "--selfcheck" in sys.argv
    c1 = canonical(build_results())
    c2 = canonical(build_results())
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    results = build_results()
    if selfcheck:
        print("selfcheck: in-process double-run BYTE-IDENTICAL")
        print("results_sha256: " + digest)
        raise SystemExit(0 if results["all_gates_pass"] else 1)
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
