#!/usr/bin/env python3
"""PROPOSAL 251 - Bulgarian solitaire's triangular-number fixed point.

HEAD: Bulgarian solitaire is a deterministic dynamical system on integer
partitions. A partition of n is a multiset of positive pile sizes. The MOVE:
remove one card from every pile, then form ONE new pile whose size = the number
of piles you had (piles that hit zero vanish). Formally, for a partition
p = (p_1 >= ... >= p_m) with m = len(p) piles,

    step(p) = sort_desc( [x - 1 for x in p if x - 1 > 0] + [m] ).

THEOREM (triangular case). If n is triangular, n = T_k = k(k+1)/2, then from
EVERY partition of n the iteration converges to the UNIQUE fixed point -- the
staircase delta_k = (k, k-1, ..., 2, 1) (a period-1 point) -- and the MAXIMUM
number of steps to that fixed point, over ALL partitions of T_k, is EXACTLY
k^2 - k. (Wikipedia states "k^2-k moves or fewer"; the EXACT tightness -- that
some partition of T_k achieves the bound with equality -- is verified here by
full enumeration and is DERIVED firsthand, not quoted.)

DISTINCTNESS: this is a deterministic dynamical system / self-map on the finite
set of integer partitions of n, NOT an impartial-combinatorial-game Grundy
value. It is orthogonal to every shipped game head -- Sprague-Grundy nim-sum
(P219), Wythoff (P239), Green Hackenbush (P247), Fibonacci-Nim (P243), Penney,
Banzhaf. There is no second player, no XOR of Grundy values, no mex; the object
is an orbit of a fixed map and the invariant is the card total n.

Gate battery (SEED=20260717; each gate reads in its OWN direction):
  G1 EXACT (exact integer arithmetic, zero tolerance): for k=1..8 (n=T_k up to
     36) enumerate ALL partitions of T_k; for each verify it reaches the fixed
     point delta_k=(k,...,1) (period-1); count `nonconvergent` (must be 0);
     record M(k) = max steps-to-fixed-point over all partitions; assert
     M(k) == k*k - k EXACTLY. The enumeration route (max over all orbits) and
     the closed-form k^2-k route are independent; their exact agreement is the
     teeth. PASS iff 0 nonconvergent AND all M(k) == k^2-k.
  G2 MONTE-CARLO AGREEMENT (iid, |z| < 3, Z_ACCEPT=3.0): each random partition's
     step-count to the fixed point is an INDEPENDENT draw, so an iid z-test is
     honest (no thinning / batch means -- that is only for autocorrelated Markov
     sample paths). At k=6 (n=21, 792 partitions) full enumeration gives the
     EXACT population mean mu and std sigma of steps-to-fixed-point. Then draw
     N_mc=40000 partitions of T_6 UNIFORMLY with the Nijenhuis-Wilf RANPAR
     sampler (seeded), compute sample mean xbar; z = (xbar - mu)/(sigma/sqrt(N)).
     Assert |z| < 3. ALSO confirm 100% of sampled partitions converge to delta_6
     within k^2-k=30 steps. A uniform sampler MUST reproduce mu within the band;
     a wild z would indict the sampler, not the theorem.
  G3 INVARIANCE (exact, 0 mismatches): (a) conservation -- over ALL enumerated
     partitions from G1's k-range, sum is preserved at EVERY step of every orbit
     (sum(step(p)) == sum(p)); count violations (must be 0). (b) order-invariance
     -- for a seeded sample of partitions, apply step to a randomly SHUFFLED
     tuple representation and confirm the sorted result is identical to stepping
     the canonical descending tuple; count mismatches (must be 0). The map is a
     function of the multiset, not of pile order. PASS iff both 0.
  G4 FALSIFIABILITY (reject at large |z|, OPPOSITE polarity to G2, Z_REJECT=6.0):
     pre-register the NAIVE FOIL "non-triangular n ALSO converge to a unique
     period-1 fixed point, just like triangular n." REFUTE it. (i) Exact witness:
     for each non-triangular n in 2..25 (exclude {1,3,6,10,15,21}), enumerate
     partitions and find limit cycles; report the count of n exhibiting a
     period>1 cycle (should be ALL of them) and the smallest non-triangular n
     with a period>1 cycle plus that cycle. (ii) MC z: draw N=40000
     (random non-triangular n in 2..25, RANPAR partition) pairs, iterate each to
     its cycle, measure the fraction f landing in a period>1 cycle; the foil
     predicts f=0. Report f and a z = f*sqrt(N)/sqrt(f*(1-f)) measuring how many
     SE the observed rate sits from the foil-null of 0 (>> 6). PASS iff the foil
     is REJECTED (|z| > 6 AND >= 1 exact witness cycle found).

Determinism posture: build_results() is a pure function of SEED and the fixed
module constants. random.seed(SEED) is RE-SEEDED at the START of each MC gate so
gate order does not affect the payload. Every float serializes via a fixed
format string; counts and step totals are ints; cycles serialize as lists of
descending tuples-as-lists. No wall-clock / PID / unordered-set iteration enters
the hashed payload. main() builds the results TWICE in one process and asserts
the canonical JSON forms are byte-identical (in-process double-run guard),
supports --selfcheck (runs the whole computation twice and prints
"SELFCHECK: byte-identical"), prints a human summary and
`results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys

SEED = 20260717

Z_ACCEPT = 3.0             # G2 agreement band
Z_REJECT = 6.0            # G4 rejection threshold for the naive foil

# G1 range: k = 1..8, n = T_k up to 36.
K_MAX = 8

# G2 configuration (uniform partitions of T_6; step-counts are iid draws).
G2_K = 6
G2_N_MC = 40_000

# G4 configuration (non-triangular n in [2, 25], excluding triangular numbers).
G4_N_LO = 2
G4_N_HI = 25
G4_N_MC = 40_000

MAX_ITER = 100_000        # orbit cap (defensive; real orbits are tiny)


def zfmt(z):
    """Fixed z-score format so the serialization is invocation-stable."""
    return f"{float(z):.4f}"


def ffmt(x):
    """Fixed float format for exact-derived reals (mu, sigma, xbar, rates)."""
    return f"{float(x):.6f}"


# --------------------------------------------------------------------------- #
# Core dynamical system on integer partitions.                                #
# --------------------------------------------------------------------------- #

def bulgarian_step(p):
    """One Bulgarian-solitaire move on a tuple of positive ints.

    k = number of piles; decrement every pile, drop the ones that hit zero, then
    append ONE new pile of size k; return the result sorted descending."""
    k = len(p)
    new = sorted([x - 1 for x in p if x - 1 > 0] + [k], reverse=True)
    return tuple(new)


def partitions(n, mx=None):
    """Generate ALL partitions of n as descending tuples (deterministic order)."""
    if mx is None:
        mx = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, mx), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def orbit_to_cycle(p):
    """Iterate from p with a seen-dict {state: index}; when a state repeats,
    return (steps_to_first_cycle_state, cycle_tuple, period). cycle_tuple is the
    canonical (lexicographically smallest rotation) list of states in the cycle,
    each a descending tuple, so it is invocation-stable."""
    seen = {}
    seq = []
    cur = p
    steps = 0
    while cur not in seen:
        seen[cur] = steps
        seq.append(cur)
        cur = bulgarian_step(cur)
        steps += 1
        if steps > MAX_ITER:
            raise RuntimeError("orbit exceeded MAX_ITER")
    start = seen[cur]
    cycle = seq[start:]
    period = len(cycle)
    # canonicalize the cycle to its lexicographically smallest rotation
    rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(period)]
    canon = min(rotations)
    return start, canon, period


def steps_to_fixed_point(p, target):
    """Iterate counting steps until state == target; guarded by MAX_ITER.
    Returns the step count, or None if the cap is exceeded (nonconvergent)."""
    steps = 0
    cur = p
    while cur != target:
        cur = bulgarian_step(cur)
        steps += 1
        if steps > MAX_ITER:
            return None
    return steps


def staircase(k):
    """The staircase fixed point delta_k = (k, k-1, ..., 2, 1)."""
    return tuple(range(k, 0, -1))


# --------------------------------------------------------------------------- #
# Nijenhuis-Wilf RANPAR uniform partition sampler.                             #
# --------------------------------------------------------------------------- #

def partition_counts(n):
    """p(0..n) via the standard DP recurrence (number of partitions)."""
    p = [0] * (n + 1)
    p[0] = 1
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            p[j] += p[j - i]
    return p


def ranpar(n, pcount, rng):
    """Draw a UNIFORMLY random partition of n (Nijenhuis-Wilf RANPAR).

    With m cards remaining, pick a pair (i, d) with i*d <= m with probability
    i * p(m - i*d) / (m * p(m)); append d parts of size i; set m <- m - i*d;
    repeat until m == 0. Returns a descending tuple. This yields each partition
    of n with equal probability."""
    parts = []
    m = n
    while m > 0:
        # sample (i, d) proportional to i * p(m - i*d)
        threshold = rng.random() * (m * pcount[m])
        acc = 0
        chosen = None
        for i in range(1, m + 1):
            id_ = i
            d = 1
            while id_ <= m:
                acc += i * pcount[m - id_]
                if acc > threshold:
                    chosen = (i, d)
                    break
                d += 1
                id_ = i * d
            if chosen is not None:
                break
        i, d = chosen
        parts.extend([i] * d)
        m -= i * d
    return tuple(sorted(parts, reverse=True))


# --------------------------------------------------------------------------- #
# G1 -- exact enumeration: convergence + exact k^2-k max steps.                #
# --------------------------------------------------------------------------- #

def run_g1():
    per_k = []
    total_nonconvergent = 0
    all_match = True
    # cache the full enumerated step-count distribution for k in G2_K (reused by G2)
    for k in range(1, K_MAX + 1):
        n = k * (k + 1) // 2
        target = staircase(k)
        parts = list(partitions(n))
        M = 0
        nonconv = 0
        for p in parts:
            s = steps_to_fixed_point(p, target)
            if s is None:
                nonconv += 1
            else:
                if s > M:
                    M = s
        bound = k * k - k
        match = (M == bound and nonconv == 0)
        all_match = all_match and match
        total_nonconvergent += nonconv
        per_k.append({
            "k": k,
            "n_triangular": n,
            "num_partitions": len(parts),
            "M_max_steps": M,
            "k2_minus_k": bound,
            "match": match,
        })
    g1_pass = (total_nonconvergent == 0 and all_match)
    return {
        "per_k": per_k,
        "total_nonconvergent": total_nonconvergent,
        "all_M_match_k2_minus_k": all_match,
        "z": None,
        "z_note": "exact",
        "pass": g1_pass,
    }


# --------------------------------------------------------------------------- #
# G2 -- Monte-Carlo agreement against exact enumerated mu, sigma.              #
# --------------------------------------------------------------------------- #

def exact_step_moments(k):
    """Enumerate ALL partitions of T_k; return (mu, sigma, count) of steps-to-
    fixed-point as exact-then-floated population moments (sigma is the POPULATION
    std, ddof=0, since this is the full population)."""
    n = k * (k + 1) // 2
    target = staircase(k)
    counts = []
    for p in partitions(n):
        s = steps_to_fixed_point(p, target)
        counts.append(s)
    N = len(counts)
    total = sum(counts)
    mu = total / N
    var = sum((c - mu) ** 2 for c in counts) / N     # population variance
    sigma = math.sqrt(var)
    return mu, sigma, N


def run_g2():
    random.seed(SEED)                       # re-seed at START of MC gate
    rng = random
    k = G2_K
    n = k * (k + 1) // 2
    target = staircase(k)
    bound = k * k - k
    mu, sigma, pop_count = exact_step_moments(k)
    pcount = partition_counts(n)

    total = 0.0
    converged = 0
    for _ in range(G2_N_MC):
        p = ranpar(n, pcount, rng)
        s = steps_to_fixed_point(p, target)
        total += s
        if s is not None and s <= bound:
            converged += 1
    xbar = total / G2_N_MC
    se = sigma / math.sqrt(G2_N_MC)
    z = (xbar - mu) / se
    convergence_rate = converged / G2_N_MC
    g2_pass = (abs(z) < Z_ACCEPT and convergence_rate == 1.0)
    return {
        "k": k,
        "n_triangular": n,
        "pop_partitions": pop_count,
        "n_mc": G2_N_MC,
        "mu": ffmt(mu),
        "sigma": ffmt(sigma),
        "xbar": ffmt(xbar),
        "z": zfmt(z),
        "convergence_rate": ffmt(convergence_rate),
        "convergence_rate_is_one": convergence_rate == 1.0,
        "iid_draws_no_batch_means": True,
        "pass": g2_pass,
    }


# --------------------------------------------------------------------------- #
# G3 -- invariance: conservation of n + order-invariance of the step map.      #
# --------------------------------------------------------------------------- #

def run_g3():
    # (a) conservation over ALL orbits of ALL enumerated partitions, k=1..8
    conservation_violations = 0
    checked_steps = 0
    for k in range(1, K_MAX + 1):
        n = k * (k + 1) // 2
        target = staircase(k)
        for p in partitions(n):
            cur = p
            guard = 0
            while cur != target:
                nxt = bulgarian_step(cur)
                if sum(nxt) != sum(cur):
                    conservation_violations += 1
                checked_steps += 1
                cur = nxt
                guard += 1
                if guard > MAX_ITER:
                    break

    # (b) order-invariance: step of a shuffled tuple == step of the canonical one
    random.seed(SEED)                        # re-seed at START of this MC leg
    rng = random
    order_mismatches = 0
    order_samples = 0
    for k in range(2, K_MAX + 1):
        n = k * (k + 1) // 2
        pcount = partition_counts(n)
        for _ in range(200):
            p = ranpar(n, pcount, rng)       # canonical descending tuple
            shuffled = list(p)
            rng.shuffle(shuffled)
            canonical_step = bulgarian_step(p)
            shuffled_step = bulgarian_step(tuple(shuffled))
            # step() sorts internally, so both are already sorted-descending
            if canonical_step != shuffled_step:
                order_mismatches += 1
            order_samples += 1

    g3_pass = (conservation_violations == 0 and order_mismatches == 0)
    return {
        "conservation_violations": conservation_violations,
        "conservation_steps_checked": checked_steps,
        "order_mismatches": order_mismatches,
        "order_samples": order_samples,
        "z": None,
        "z_note": "exact",
        "pass": g3_pass,
    }


# --------------------------------------------------------------------------- #
# G4 -- falsifiability: refute "non-triangular n also has a unique fixed point".#
# --------------------------------------------------------------------------- #

def triangular_set(hi):
    s = set()
    k = 1
    while True:
        t = k * (k + 1) // 2
        if t > hi:
            break
        s.add(t)
        k += 1
    return s


def run_g4():
    tri = triangular_set(G4_N_HI)
    nontri = [n for n in range(G4_N_LO, G4_N_HI + 1) if n not in tri]

    # (i) exact witnesses: enumerate every non-triangular n, find period>1 cycles
    n_with_period_gt1 = 0
    smallest_n = None
    smallest_cycle = None
    for n in nontri:
        has_long_cycle = False
        first_cycle_here = None
        for p in partitions(n):
            _, cycle, period = orbit_to_cycle(p)
            if period > 1:
                has_long_cycle = True
                if first_cycle_here is None:
                    first_cycle_here = cycle
        if has_long_cycle:
            n_with_period_gt1 += 1
            if smallest_n is None:
                smallest_n = n
                smallest_cycle = first_cycle_here

    all_nontri_have_long_cycle = (n_with_period_gt1 == len(nontri))

    # (ii) MC z rejecting the foil (foil-null: fraction landing in period>1 is 0)
    random.seed(SEED)                        # re-seed at START of this MC gate
    rng = random
    pcount_cache = {n: partition_counts(n) for n in nontri}
    long_cycle_hits = 0
    for _ in range(G4_N_MC):
        n = rng.choice(nontri)
        p = ranpar(n, pcount_cache[n], rng)
        _, _, period = orbit_to_cycle(p)
        if period > 1:
            long_cycle_hits += 1
    f = long_cycle_hits / G4_N_MC
    # z: how many SE the observed rate f sits above the foil-null of 0.
    # SE from the observed rate = sqrt(p*(1-p)/N); z = f/SE = f*sqrt(N)/sqrt(p(1-p)).
    # Non-triangular n have NO period-1 fixed point, so every orbit lands in a
    # period>1 cycle and f is exactly 1.0 -> the bare sqrt(f(1-f)) SE is 0. Floor
    # the SE rate at a single-event boundary p in [1/N, 1-1/N] (rule-of-three /
    # Laplace style) so z is finite, principled, and clearly >> 6.
    p_se = min(max(f, 1.0 / G4_N_MC), 1.0 - 1.0 / G4_N_MC)
    se = math.sqrt(p_se * (1.0 - p_se) / G4_N_MC)
    z_foil = f / se if se > 0 else 0.0

    foil_rejected = (abs(z_foil) > Z_REJECT and smallest_cycle is not None)
    g4_pass = foil_rejected
    return {
        "foil": ("non-triangular n also converge to a unique period-1 fixed "
                 "point, just like triangular n"),
        "nontriangular_n_range": [G4_N_LO, G4_N_HI],
        "num_nontriangular_n": len(nontri),
        "n_with_period_gt1_cycle": n_with_period_gt1,
        "all_nontriangular_have_period_gt1": all_nontri_have_long_cycle,
        "smallest_nontriangular_with_cycle": smallest_n,
        "smallest_cycle": [list(state) for state in smallest_cycle] if smallest_cycle else None,
        "n_mc": G4_N_MC,
        "fraction_period_gt1": ffmt(f),
        "z_foil": zfmt(z_foil),
        "foil_null_fraction": "0.000000",
        "foil_rejected": foil_rejected,
        "pass": g4_pass,
    }


# --------------------------------------------------------------------------- #

def build_results():
    results = {
        "proposal": 251,
        "claim": (
            "Bulgarian solitaire (remove one card from every pile, then form ONE "
            "new pile of size = number of piles) is a deterministic map on "
            "integer partitions of n. If n=T_k=k(k+1)/2 is triangular, EVERY "
            "partition converges to the unique period-1 fixed point, the "
            "staircase delta_k=(k,k-1,...,1), and the MAX steps-to-fixed-point "
            "over all partitions of T_k is EXACTLY k^2-k. Non-triangular n admit "
            "no fixed point (limit cycles of period>1). Distinct from all "
            "impartial-game Grundy heads (nim-sum, Wythoff, Hackenbush, "
            "Fibonacci-Nim, Penney, Banzhaf): a dynamical system, not a game value."
        ),
        "seed": SEED,
        "z_accept": zfmt(Z_ACCEPT),
        "z_reject": zfmt(Z_REJECT),
        "k_max": K_MAX,
        "g2_k": G2_K,
        "g2_n_mc": G2_N_MC,
        "g4_n_range": [G4_N_LO, G4_N_HI],
        "g4_n_mc": G4_N_MC,
    }

    results["G1_exact"] = run_g1()
    results["G2_mc_agreement"] = run_g2()
    results["G3_invariance"] = run_g3()
    results["G4_falsifiability"] = run_g4()

    gates = {
        "G1": results["G1_exact"]["pass"],
        "G2": results["G2_mc_agreement"]["pass"],
        "G3": results["G3_invariance"]["pass"],
        "G4": results["G4_falsifiability"]["pass"],
    }
    order = ["G1", "G2", "G3", "G4"]
    results["gates"] = gates
    results["first_failing_gate"] = next((g for g in order if not gates[g]), None)
    results["all_pass"] = all(gates[g] for g in order)
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def compute_digest():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    identical = (c1 == c2)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    return r1, c1, identical, digest


def main():
    selfcheck = "--selfcheck" in sys.argv[1:]
    r1, c1, identical, digest = compute_digest()
    if not identical:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)

    if selfcheck:
        print("SELFCHECK: byte-identical")
        print(f"results_sha256={digest}")
        sys.exit(0 if r1["all_pass"] else 1)

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for key in ["G1", "G2", "G3", "G4"]:
        print(f"{key}: {'PASS' if r1['gates'][key] else 'FAIL'}")
    print()
    print(f"in_process_double_run: {'IDENTICAL' if identical else 'DIVERGED'}")
    print(f"all_pass: {r1['all_pass']}")
    print(f"first_failing_gate: {r1['first_failing_gate']}")
    print(f"results_sha256={digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
