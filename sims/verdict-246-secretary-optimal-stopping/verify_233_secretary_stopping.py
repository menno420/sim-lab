#!/usr/bin/env python3
"""
Secretary / best-choice optimal-stopping verifier -- PROPOSAL 233 (cross-cutting
FLEET slot: a selection/scheduling mechanism over a fleet of n sequentially
arriving candidates observed only by relative rank).

Claim: for n candidates of distinct qualities arriving in uniformly random order,
observed ONLY by relative rank, the threshold rule "reject the first r-1, then
take the first candidate that is better than every one seen so far" selects the
overall-best candidate with probability EXACTLY

    P(r,n) = ((r-1)/n) * sum_{i=r}^{n} 1/(i-1)          (r >= 2)
    P(1,n) = 1/n                                        ("just take the first")

The optimal cutoff r*(n) is the smallest r >= 1 with sum_{k=r}^{n-1} 1/k <= 1,
and the optimal win probability P(r*(n),n) -> 1/e ~= 0.36787944117144233 as
n -> infinity. This provably beats the naive "take the first candidate" rule,
which wins with probability exactly 1/n -> 0.

Deterministic, stdlib-only (json, hashlib, math, random, fractions, itertools).
SEED = 20260717. build_results() is a pure function of the seed and fixed
constants; main() runs it twice in-process and asserts byte-identical canonical
JSON, and a separate cross-invocation reproduces the same 64-hex digest. Every MC
pass instantiates its own random.Random(seed) so the payload is independent of
call order; no wall-clock, no PID, no unordered-set iteration in the hashed
payload.

Gates (each in its own direction, real teeth):
  G1  EXACT identity via fractions.Fraction. For n in {4,5,6,7}, brute-force over
      ALL n! orderings; for EVERY threshold r in {1..n} the empirical win fraction
      (win_count / n!) as a Fraction equals the closed form
      ((r-1)/n) * sum_{i=r}^{n} 1/(i-1) as a Fraction. ALSO argmax_r of the closed
      form equals r*(n) computed from "smallest r with sum_{k=r}^{n-1} 1/k <= 1".
      ALSO P(1,n) == Fraction(1,n) exactly. Every equality EXACT (Fraction ==).
  G2  Monte-Carlo agreement at n=MC_N under the OPTIMAL r*(n) rule: N=MC_TRIALS
      seeded random orderings, empirical win rate vs the exact closed form
      P(r*(n),n); z = (phat - p0)/sqrt(p0(1-p0)/N); PASS at |z| < Z_ACCEPT=3.0.
  G3  Invariance / robustness -- BOTH sub-checks must pass:
      (a) EXACT second route: a forward record-indicator DP that multiplies the
          RAW factors (1 - 1/s) (never the telescoped closed form) reproduces
          P(r,n) as a Fraction for all n in the G1 set and all r.
      (b) rank-only invariance in MC: re-run G2's pass but draw qualities from a
          DIFFERENT strictly-monotone distribution (quality = U**3, independent
          seed) -- because only relative rank matters the win rate is
          statistically identical, |z| < Z_ACCEPT vs the SAME p0.
  G4  FALSIFIABILITY: on the SAME MC sample as G2 the naive "take the first
      candidate" rule (r=1) wins at rate ~= 1/n. It is (i) statistically
      consistent with its OWN exact value 1/n (sanity anchor, |z| < Z_ACCEPT) yet
      (ii) REJECTS the optimal-rule target p0 = P(r*,n) at |z_naive| >= Z_REJECT=6.
"""
import json
import hashlib
import math
import random
from fractions import Fraction
from itertools import permutations

SEED = 20260717

# Exact-gate test set (full n! enumeration).
G1_NS = [4, 5, 6, 7]

# Monte-Carlo world (fixed constants).
MC_N = 100          # candidate-fleet size for the MC gates
MC_TRIALS = 200000  # seeded random orderings
G3B_SEED = SEED + 1  # independent stream for the rank-only invariance MC
Z_ACCEPT = 3.0      # |z| below this => agreement
Z_REJECT = 6.0      # |z_naive| at/above this => optimal claim rejected by naive

# Asymptotic target (reported, not gated -- it is irrational).
ONE_OVER_E = math.exp(-1)  # 1/e ~= 0.36787944117144233


def p_closed(r, n):
    """Direct closed form P(r,n) as an exact Fraction (P(1,n)=1/n)."""
    if r == 1:
        return Fraction(1, n)
    return Fraction(r - 1, n) * sum(Fraction(1, i - 1) for i in range(r, n + 1))


def r_star(n):
    """Smallest r >= 1 with sum_{k=r}^{n-1} 1/k <= 1 (exact rational)."""
    for r in range(1, n + 1):
        s = sum(Fraction(1, k) for k in range(r, n))  # k = r .. n-1
        if s <= 1:
            return r
    return n


def argmax_r(n):
    """r that maximises the closed form P(r,n); ties resolved to smallest r."""
    best_r = None
    best_p = None
    for r in range(1, n + 1):
        p = p_closed(r, n)
        if best_p is None or p > best_p:
            best_p = p
            best_r = r
    return best_r, best_p


def dp_win_prob(r, n):
    """Independent EXACT route: forward record-indicator DP.

    Records are the positions whose candidate beats all before it; position s is a
    record with probability 1/s. The rule stops at the first record time tau >= r,
    and wins iff no record occurs afterwards (i.e. the selected candidate is the
    global best). This multiplies the RAW factors (1 - 1/s) and never uses the
    telescoped forms (r-1)/(t-1) or t/n, so agreement with p_closed certifies the
    telescoping/closed form rather than restating it.
    """
    if r == 1:
        # tau = 1 always (position 1 is a record); win iff no later record.
        prob = Fraction(1)
        for s in range(2, n + 1):
            prob *= (1 - Fraction(1, s))
        return prob  # == 1/n
    total = Fraction(0)
    for t in range(r, n + 1):
        p_reject = Fraction(1)              # no record in positions r..t-1
        for s in range(r, t):
            p_reject *= (1 - Fraction(1, s))
        p_record_t = Fraction(1, t)         # position t is a record
        p_no_later = Fraction(1)            # no record in positions t+1..n
        for s in range(t + 1, n + 1):
            p_no_later *= (1 - Fraction(1, s))
        total += p_reject * p_record_t * p_no_later
    return total


def rule_select(perm, r):
    """Return the quality the threshold-r rule selects on ordering `perm`."""
    n = len(perm)
    if r == 1:
        return perm[0]
    benchmark = max(perm[:r - 1])
    for i in range(r - 1, n):
        if perm[i] > benchmark:
            return perm[i]
    return perm[-1]  # forced last if no record after the reject phase


def brute_win_count(r, n):
    """#orderings (over all n!) where the threshold-r rule picks the global best."""
    best = n
    cnt = 0
    for perm in permutations(range(1, n + 1)):
        if rule_select(perm, r) == best:
            cnt += 1
    return cnt


def gate1():
    """EXACT: empirical == closed form for every (r,n); argmax == r*; P(1,n)=1/n."""
    rows = {}
    ok = True
    for n in G1_NS:
        fact = math.factorial(n)
        rstar = r_star(n)
        amax_r, _ = argmax_r(n)
        argmax_matches = (amax_r == rstar)
        p1_ok = (p_closed(1, n) == Fraction(1, n))
        per_r = {}
        n_ok = argmax_matches and p1_ok
        for r in range(1, n + 1):
            wins = brute_win_count(r, n)
            emp = Fraction(wins, fact)
            closed = p_closed(r, n)
            eq = (emp == closed)
            n_ok = n_ok and eq
            per_r[str(r)] = {
                "win_count": wins,
                "n_factorial": fact,
                "empirical_fraction": str(emp),
                "closed_form_fraction": str(closed),
                "equal": eq,
            }
        ok = ok and n_ok
        rows[str(n)] = {
            "r_star": rstar,
            "argmax_r": amax_r,
            "argmax_equals_r_star": argmax_matches,
            "P1_equals_1_over_n": p1_ok,
            "P_r_star_fraction": str(p_closed(rstar, n)),
            "by_threshold": per_r,
            "pass": n_ok,
        }
    return ok, {"rows": rows, "pass": ok}


def gate2_gate4():
    """One MC pass at n=MC_N: feeds G2 (optimal r* agreement) and G4 (naive 1/n)."""
    n, N = MC_N, MC_TRIALS
    rstar = r_star(n)
    p0_frac = p_closed(rstar, n)
    p0 = float(p0_frac)

    rng = random.Random(SEED)
    base = list(range(1, n + 1))
    wins_opt = 0
    wins_naive = 0
    for _ in range(N):
        perm = rng.sample(base, n)
        if rule_select(perm, rstar) == n:
            wins_opt += 1
        if perm[0] == n:          # naive r=1: take the first candidate
            wins_naive += 1

    phat_opt = wins_opt / N
    z_opt = (phat_opt - p0) / math.sqrt(p0 * (1.0 - p0) / N)
    g2_ok = abs(z_opt) < Z_ACCEPT

    # Naive rule: exact own value is 1/n; reject the optimal target p0.
    p_naive_frac = Fraction(1, n)
    p_naive = float(p_naive_frac)
    phat_naive = wins_naive / N
    z_naive_self = (phat_naive - p_naive) / math.sqrt(p_naive * (1.0 - p_naive) / N)
    z_naive_vs_opt = (phat_naive - p0) / math.sqrt(p0 * (1.0 - p0) / N)
    naive_self_consistent = abs(z_naive_self) < Z_ACCEPT
    naive_rejects_optimal = abs(z_naive_vs_opt) >= Z_REJECT
    g4_ok = g2_ok and naive_self_consistent and naive_rejects_optimal

    g2 = {
        "n": n,
        "N": N,
        "r_star": rstar,
        "wins_optimal": wins_opt,
        "phat_optimal": round(phat_opt, 12),
        "p0_exact_fraction": str(p0_frac),
        "p0_float": round(p0, 16),
        "one_over_e": round(ONE_OVER_E, 17),
        "z_optimal": round(z_opt, 6),
        "z_accept": Z_ACCEPT,
        "pass": g2_ok,
    }
    g4 = {
        "n": n,
        "N": N,
        "naive_rule": "take the first candidate (r=1)",
        "naive_exact_fraction": str(p_naive_frac),
        "wins_naive": wins_naive,
        "phat_naive": round(phat_naive, 12),
        "z_naive_self": round(z_naive_self, 6),
        "naive_self_consistent": naive_self_consistent,
        "optimal_target_p0": round(p0, 16),
        "z_naive_vs_optimal": round(z_naive_vs_opt, 6),
        "z_reject": Z_REJECT,
        "naive_rejects_optimal": naive_rejects_optimal,
        "pass": g4_ok,
    }
    return g2_ok, g2, g4_ok, g4


def gate3():
    """(a) EXACT DP second route == closed form; (b) rank-only MC invariance."""
    # (a) forward record-indicator DP vs the direct closed form, exact Fractions.
    dp_rows = {}
    dp_ok = True
    for n in G1_NS:
        per_r = {}
        for r in range(1, n + 1):
            closed = p_closed(r, n)
            viadp = dp_win_prob(r, n)
            eq = (closed == viadp)
            dp_ok = dp_ok and eq
            per_r[str(r)] = {
                "closed_form_fraction": str(closed),
                "dp_route_fraction": str(viadp),
                "equal": eq,
            }
        dp_rows[str(n)] = per_r

    # (b) rank-only invariance: qualities drawn from U**3 (strictly monotone),
    # independent seed; win rate must agree with the SAME p0 at |z| < Z_ACCEPT.
    n, N = MC_N, MC_TRIALS
    rstar = r_star(n)
    p0 = float(p_closed(rstar, n))
    rng = random.Random(G3B_SEED)
    wins = 0
    for _ in range(N):
        q = [rng.random() ** 3 for _ in range(n)]
        best = max(q)
        if rule_select(q, rstar) == best:
            wins += 1
    phat_inv = wins / N
    z_inv = (phat_inv - p0) / math.sqrt(p0 * (1.0 - p0) / N)
    inv_ok = abs(z_inv) < Z_ACCEPT

    ok = dp_ok and inv_ok
    return ok, {
        "exact_dp_second_route": {"rows": dp_rows, "pass": dp_ok},
        "rank_only_mc_invariance": {
            "n": n,
            "N": N,
            "r_star": rstar,
            "quality_distribution": "U**3 (strictly monotone; rank-preserving)",
            "invariance_seed": G3B_SEED,
            "wins": wins,
            "phat": round(phat_inv, 12),
            "p0_float": round(p0, 16),
            "z_invariance": round(z_inv, 6),
            "z_accept": Z_ACCEPT,
            "pass": inv_ok,
        },
        "pass": ok,
    }


def build_results():
    g1_ok, g1 = gate1()
    g2_ok, g2, g4_ok, g4 = gate2_gate4()
    g3_ok, g3 = gate3()

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for idx, ok in ((1, g1_ok), (2, g2_ok), (3, g3_ok), (4, g4_ok)):
        if not ok:
            first_failing = idx
            break

    return {
        "seed": SEED,
        "claim": (
            "threshold rule (reject first r-1, then take first record) selects the "
            "best of n uniformly-ordered rank-observed candidates with probability "
            "P(r,n)=((r-1)/n) sum_{i=r}^{n} 1/(i-1); optimal P(r*(n),n) -> 1/e; "
            "naive take-first wins with probability 1/n"
        ),
        "r_star_test_set": {str(n): r_star(n) for n in G1_NS},
        "G1_exact_identity_brute_vs_closed": g1,
        "G2_monte_carlo_optimal_agreement": g2,
        "G3_invariance_dp_route_and_rank_only": g3,
        "G4_falsifiability_naive_take_first": g4,
        "gates": {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok},
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "sim-ready" if all_pass else "needs-more-grooming",
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + r1["decision"])
    if not r1["all_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
