#!/usr/bin/env python3
"""VERDICT 047 — the 37% rule off its home objective (idea-engine PROPOSAL 036).

Exact cardinal-regret curve dV(N) and downside profile B(N) of the folk
look-then-leap cutoff r_folk(N) = clamp(floor((37N+50)/100), 1, N-1) under the
pinned secretary frame, over the full 379-cell (N, r) census x 2 objectives
(P_best, E[V]) x 2 conventions (must-choose decision-binding, walk-away
reporting-only).

Hermetic: reads ONLY its own fixtures.json (same directory). One command, no
flags. ALL arithmetic exact fractions.Fraction / exact integers — ZERO RNG,
ZERO floats anywhere in computation (decimal display columns are exact
decimal strings derived from Fractions by integer long division,
display-only). Byte-identical output on re-run BY CONSTRUCTION.

Two structurally independent arms, gated on EXACT RATIONAL EQUALITY per cell:

  Arm A — analytic closed forms (the drafting hand-derivation):
      P_best(r, N) = (r/N) * sum_{j=r}^{N-1} 1/j
      E_must[V](r, N) = (1/2) * (1 + r/(r+1) - r/N)
      E_walk[V](r, N) = 1/2 + r/(2(r+1)) - r/(2N) - r/(2(N+1))

  Arm B — independent combinatorial rank census (derived from first
  principles by direct finite counting, NOT a re-arrangement of Arm A):
      A cutoff policy CR(r) accepts at position j (r < j) iff candidate j is
      a running record AND the best of the first j-1 sits in the first r
      (the second clause is automatic at the FIRST record after r). Counting
      permutations with candidate j of overall rank k and ranks 1..k-1 all
      behind position j gives the joint acceptance mass
          P(accept at j, rank k) = [r/(j-1)] * (1/N) * C(N-k, j-1)/C(N-1, j-1)
      (the binomial-ratio family), for j = r+1 .. N, k = 1 .. N-j+1.
      Take-at-N legs: must-choose reaches position N unaccepted iff the best
      of the first N-1 sits in the first r; the position-N candidate's rank
      is then uniform (the forced leg), P = r/(N(N-1)) per rank. Walk-away
      ends empty iff the overall best sits in the first r.
      P_best is read off the rank-1 row; E[V] = sum_k P(rank k)*(N+1-k)/(N+1).

  Census gate — the algorithm-free third arm: full permutation enumeration at
  N in {5, 6, 7} (120/720/5040 orders), both objectives, both conventions,
  full selected-rank distribution at every r, equal to BOTH arms exactly.

Decision rule (pre-registered in fixtures.json, evaluated IN ORDER):
  REJECT  iff dV(N) <= 1/50 at EVERY swept N            (checked FIRST)
  APPROVE iff dV(N) >= 1/20 AND B(N) >= 3/20 at every N in {50, 100, 200}
  NULL    otherwise (an honest NULL is a finalized deliverable)

Seed registry: ZERO seeds drawn — fleet high-water 20261284 unchanged.
"""

import itertools
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- utilities

_CHECKS_PASSED = []
_CHECKS_FAILED = []


def check(name, cond):
    if cond:
        _CHECKS_PASSED.append(name)
    else:
        _CHECKS_FAILED.append(name)
        print(f"GATE FAILURE: {name}")


def pf(s):
    """Parse an exact 'num/den' fixture string into a Fraction."""
    num, den = s.split("/")
    return F(int(num), int(den))


def fs(fr):
    """Exact 'num/den' string for a Fraction."""
    return f"{fr.numerator}/{fr.denominator}"


def dec(fr, places=6):
    """Exact decimal display string (truncated) by integer long division.

    Display-only; no floats are created anywhere in this program.
    """
    sign = "-" if fr < 0 else ""
    a = abs(fr)
    ip, rem = divmod(a.numerator, a.denominator)
    digits = []
    for _ in range(places):
        rem *= 10
        d, rem = divmod(rem, a.denominator)
        digits.append(str(d))
    return f"{sign}{ip}." + "".join(digits)


def cell(fr):
    """results.json value: exact fraction string + display decimal."""
    return {"frac": fs(fr), "dec": dec(fr)}


# ---------------------------------------------------------------- Arm A

def armA_pbest(r, N):
    return F(r, N) * sum(F(1, j) for j in range(r, N))


def armA_emust(r, N):
    return F(1, 2) * (1 + F(r, r + 1) - F(r, N))


def armA_ewalk(r, N):
    return F(1, 2) + F(r, 2 * (r + 1)) - F(r, 2 * N) - F(r, 2 * (N + 1))


# ---------------------------------------------------------------- Arm B

def armB_prepare(N):
    """Precompute f[j][k-1] = (1/(j-1)) * (1/N) * C(N-k, j-1)/C(N-1, j-1)
    for j = 2..N, and suffix sums S[j0] = sum_{j=j0}^{N} f[j] (vector over k).
    Multiplying by r and summing j >= r+1 yields every cell in O(N) each.
    """
    comb = math.comb
    f = [None, None]  # f[0], f[1] unused
    for j in range(2, N + 1):
        cd = N * (j - 1) * comb(N - 1, j - 1)
        f.append([F(comb(N - k, j - 1), cd) for k in range(1, N + 1)])
    zero = [F(0)] * N
    S = [zero] * (N + 2)
    for j in range(N, 1, -1):
        S[j] = [S[j + 1][i] + f[j][i] for i in range(N)]
    return f, S


def armB_cell(N, f, S, r):
    """Selected-rank distributions and end-leg masses for CR(r) at N.

    Returns (must_dist, walk_dist, take_last, empty): lists indexed k-1.
    """
    walk = [r * S[r + 1][i] for i in range(N)]           # accept at j = r+1..N
    acc_pre = [r * (S[r + 1][i] - f[N][i]) for i in range(N)]  # j <= N-1
    take_last = 1 - sum(acc_pre)      # measured complement of acceptance mass
    forced_per_rank = take_last * F(1, N)   # forced position-N rank uniform
    must = [acc_pre[i] + forced_per_rank for i in range(N)]
    empty = 1 - sum(walk)
    return must, walk, take_last, empty


def ev_of(dist, N):
    """E[V] = sum_k P(rank k) * (N+1-k)/(N+1); an empty end contributes 0."""
    return sum(dist[k - 1] * F(N + 1 - k, N + 1) for k in range(1, N + 1))


# ---------------------------------------------------------------- census

def census(N):
    """Full permutation enumeration: selected-rank counts per r, per
    convention, plus take-last / end-empty counts. Returns dict r ->
    (must_counts, walk_counts, take_last_count, empty_count) with counts
    over N! orders. Algorithm-free: simulates the policy on every order.
    """
    out = {r: ([0] * N, [0] * N, 0, 0) for r in range(1, N)}
    for perm in itertools.permutations(range(1, N + 1)):
        # records: positions j >= 2 where perm[j-1] beats (rank <) all before
        recs = []
        m = perm[0]
        for j in range(2, N + 1):
            if perm[j - 1] < m:
                recs.append(j)
                m = perm[j - 1]
        for r in range(1, N):
            j = next((x for x in recs if x > r), None)
            must_counts, walk_counts, tl, ec = out[r]
            if j is None:
                walk_ec = True
                sel_must = perm[N - 1]
            else:
                walk_ec = False
                walk_counts[perm[j - 1] - 1] += 1
                sel_must = perm[j - 1] if j <= N - 1 else perm[N - 1]
            if walk_ec:
                ec += 1
            must_counts[sel_must - 1] += 1
            if j is None or j == N:
                tl += 1  # position-N candidate selected (record or forced)
            out[r] = (must_counts, walk_counts, tl, ec)
    return out


# ---------------------------------------------------------------- helpers

def argmax_ties(pairs):
    """pairs: list of (r, value). Return (best_value, [r ties, ascending])."""
    best = max(v for _, v in pairs)
    return best, [r for r, v in pairs if v == best]


def quartiles(dist, N):
    """min k with CDF(k) >= p for p in {1/4, 1/2, 3/4} (dist sums to 1)."""
    qs = []
    for p in (F(1, 4), F(1, 2), F(3, 4)):
        acc = F(0)
        for k in range(1, N + 1):
            acc += dist[k - 1]
            if acc >= p:
                qs.append(k)
                break
    return qs


# ---------------------------------------------------------------- main

def main():
    fx = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
    grid = fx["N_grid"]
    e_lo = pf(fx["e_bracket"]["lo"])
    e_hi = pf(fx["e_bracket"]["hi"])
    thr_reject = pf(fx["bands"]["REJECT"]["dV_threshold"])
    thr_app_dv = pf(fx["bands"]["APPROVE"]["dV_threshold"])
    thr_app_b = pf(fx["bands"]["APPROVE"]["B_threshold"])
    decision_cells = fx["bands"]["APPROVE"]["decision_cells"]

    print("=" * 78)
    print("VERDICT 047 — the 37% rule off its home objective")
    print("idea-engine PROPOSAL 036 · exact cardinal regret of look-then-leap")
    print("=" * 78)
    print(f"N grid: {grid} · cutoff family CR(r), r in 1..N-1 · "
          f"{sum(n - 1 for n in grid)} cells")
    print("all arithmetic exact Fraction / exact int · zero RNG · zero floats "
          "in computation")
    print(f"seed registry: {fx['seed_registry']['seeds_drawn']} seeds drawn · "
          f"fleet high-water {fx['seed_registry']['fleet_high_water']} unchanged")
    print()

    check("cells_total == 379 (registered)", sum(n - 1 for n in grid) == 379)

    # -------------------------------------------------- both arms, all cells
    per_n = {}
    arm_ns = sorted(set(grid) | {3, 4} | set(fx["census_gate"]["N"]))
    for N in arm_ns:
        f, S = armB_prepare(N)
        rows = {}
        for r in range(1, N):
            a_pb = armA_pbest(r, N)
            a_em = armA_emust(r, N)
            a_ew = armA_ewalk(r, N)
            must, walk, take_last, empty = armB_cell(N, f, S, r)
            b_pb_must = must[0]
            b_pb_walk = walk[0]
            b_em = ev_of(must, N)
            b_ew = ev_of(walk, N)
            rows[r] = dict(pb=a_pb, em=a_em, ew=a_ew, must=must, walk=walk,
                           take_last=take_last, empty=empty,
                           b_pb_must=b_pb_must, b_pb_walk=b_pb_walk,
                           b_em=b_em, b_ew=b_ew)
        per_n[N] = rows

        # gates per N (each aggregates all r for that N)
        check(f"N={N}: Arm A == Arm B, P_best (must rank-1 row), all r",
              all(rows[r]["pb"] == rows[r]["b_pb_must"] for r in rows))
        check(f"N={N}: Arm A == Arm B, P_best (walk rank-1 row), all r",
              all(rows[r]["pb"] == rows[r]["b_pb_walk"] for r in rows))
        check(f"N={N}: P(rank 1) identical across conventions, all r",
              all(rows[r]["b_pb_must"] == rows[r]["b_pb_walk"] for r in rows))
        check(f"N={N}: Arm A == Arm B, E_must[V], all r",
              all(rows[r]["em"] == rows[r]["b_em"] for r in rows))
        check(f"N={N}: Arm A == Arm B, E_walk[V], all r",
              all(rows[r]["ew"] == rows[r]["b_ew"] for r in rows))
        check(f"N={N}: convention identity E_must-E_walk == r/(2(N+1)) "
              f"(Arm B, both sides independently computed), all r",
              all(rows[r]["b_em"] - rows[r]["b_ew"] == F(r, 2 * (N + 1))
                  for r in rows))
        check(f"N={N}: convention identity on Arm A closed forms, all r",
              all(rows[r]["em"] - rows[r]["ew"] == F(r, 2 * (N + 1))
                  for r in rows))
        check(f"N={N}: never-leap P(take last | must) == r/(N-1), all r",
              all(rows[r]["take_last"] == F(r, N - 1) for r in rows))
        check(f"N={N}: never-leap P(end empty | walk) == r/N, all r",
              all(rows[r]["empty"] == F(r, N) for r in rows))
        check(f"N={N}: must-choose rank distribution sums to 1, all r",
              all(sum(rows[r]["must"]) == 1 for r in rows))
        check(f"N={N}: walk-away rank distribution sums to 1 - r/N, all r",
              all(sum(rows[r]["walk"]) == 1 - F(r, N) for r in rows))
        check(f"N={N}: E_must[V](N-1, N) == 1/2 exactly",
              rows[N - 1]["em"] == F(1, 2) and rows[N - 1]["b_em"] == F(1, 2))

    # -------------------------------------------------- classic anchors
    check("anchor: P_best(1, 3) == 1/2 (both arms)",
          per_n[3][1]["pb"] == F(1, 2) and per_n[3][1]["b_pb_must"] == F(1, 2))
    v4, t4 = argmax_ties([(r, per_n[4][r]["pb"]) for r in per_n[4]])
    check("anchor: N=4 optimal cutoff r*=1 with P_best 11/24",
          t4 == [1] and v4 == F(11, 24))
    v5, t5 = argmax_ties([(r, per_n[5][r]["pb"]) for r in per_n[5]])
    check("anchor: N=5 optimal cutoff r*=2 with P_best 13/30",
          t5 == [2] and v5 == F(13, 30))

    # -------------------------------------------------- census gate N in 5,6,7
    for N in fx["census_gate"]["N"]:
        fact = math.factorial(N)
        cen = census(N)
        rows = per_n[N]
        check(f"census N={N}: selected-rank distribution == Arm B (must), "
              f"all r, all k",
              all(F(cen[r][0][i], fact) == rows[r]["must"][i]
                  for r in cen for i in range(N)))
        check(f"census N={N}: selected-rank distribution == Arm B (walk), "
              f"all r, all k",
              all(F(cen[r][1][i], fact) == rows[r]["walk"][i]
                  for r in cen for i in range(N)))
        check(f"census N={N}: P_best == Arm A, all r",
              all(F(cen[r][0][0], fact) == rows[r]["pb"] for r in cen))
        check(f"census N={N}: E_must[V] == Arm A, all r",
              all(ev_of([F(c, fact) for c in cen[r][0]], N) == rows[r]["em"]
                  for r in cen))
        check(f"census N={N}: E_walk[V] == Arm A, all r",
              all(ev_of([F(c, fact) for c in cen[r][1]], N) == rows[r]["ew"]
                  for r in cen))
        check(f"census N={N}: take-last count == r/(N-1), all r",
              all(F(cen[r][2], fact) == F(r, N - 1) for r in cen))
        check(f"census N={N}: end-empty count == r/N, all r",
              all(F(cen[r][3], fact) == F(r, N) for r in cen))
    print(f"census gate: full permutation enumeration at "
          f"N in {fx['census_gate']['N']} "
          f"({'/'.join(str(math.factorial(n)) for n in fx['census_gate']['N'])} "
          f"orders) == both arms exactly")
    print()

    # -------------------------------------------------- decision numbers
    results_per_n = {}
    dV = {}
    Bmap = {}
    print("-" * 78)
    print("DECISION TABLE (must-choose; exact rationals, display decimals "
          "truncated)")
    print("-" * 78)
    header = (f"{'N':>4} {'r_folk':>6} {'r*_V':>8} {'r*_R':>8} "
              f"{'dV exact':>14} {'dV dec':>9} {'B exact':>16} {'B dec':>9}")
    print(header)
    for N in grid:
        rows = per_n[N]
        r_folk = min(max((37 * N + 50) // 100, 1), N - 1)

        ev_best, ev_ties = argmax_ties([(r, rows[r]["em"]) for r in rows])
        pb_best, pb_ties = argmax_ties([(r, rows[r]["pb"]) for r in rows])
        r_star_v = ev_ties[0]   # canonical = smallest tied r (ties reported)
        r_star_r = pb_ties[0]

        dv = ev_best - rows[r_folk]["em"]
        dV[N] = dv

        half_start = N // 2 + 1
        b = sum(rows[r_folk]["must"][k - 1] for k in range(half_start, N + 1))
        Bmap[N] = b

        dR = rows[r_star_r]["pb"] - rows[r_star_v]["pb"]
        shortfall = rows[r_star_r]["pb"] - rows[r_folk]["pb"]

        # floor(N/e) variant under the rational bracket (reporting-only)
        fl_hi = (N * e_hi.denominator) // e_hi.numerator   # floor(N / e_hi)
        fl_lo = (N * e_lo.denominator) // e_lo.numerator   # floor(N / e_lo)
        check(f"N={N}: floor(N/e) agrees under both e-bracket endpoints",
              fl_hi == fl_lo)
        r_e = min(max(fl_hi, 1), N - 1)
        dv_evar = ev_best - rows[r_e]["em"]
        shortfall_evar = rows[r_star_r]["pb"] - rows[r_e]["pb"]

        # walk-away frontier (reporting-only)
        ew_best, ew_ties = argmax_ties([(r, rows[r]["ew"]) for r in rows])

        # 1/e context: 1/e in (1/e_hi, 1/e_lo); bounds on P_best(r_folk)-1/e
        pb_folk = rows[r_folk]["pb"]
        diff_lo = pb_folk - 1 / e_lo    # lower bound of pb - 1/e
        diff_hi = pb_folk - 1 / e_hi    # upper bound of pb - 1/e

        q = {"r_folk": quartiles(rows[r_folk]["must"], N),
             "r_star_R": quartiles(rows[r_star_r]["must"], N),
             "r_star_V": quartiles(rows[r_star_v]["must"], N)}

        s = math.isqrt(N)
        results_per_n[str(N)] = {
            "r_folk": r_folk,
            "r_star_V_ties": ev_ties,
            "r_star_R_ties": pb_ties,
            "r_e_variant": r_e,
            "sqrtN_minus_1_context": s - 1,
            "E_must_at_r_star_V": cell(ev_best),
            "E_must_at_r_folk": cell(rows[r_folk]["em"]),
            "P_best_at_r_star_R": cell(rows[r_star_r]["pb"]),
            "P_best_at_r_star_V": cell(rows[r_star_v]["pb"]),
            "P_best_at_r_folk": cell(pb_folk),
            "dV": cell(dv),
            "B_bottom_half_at_r_folk_must": cell(b),
            "dR": cell(dR),
            "own_objective_shortfall": cell(shortfall),
            "e_variant_deltas": {"dV_evar": cell(dv_evar),
                                 "own_objective_shortfall_evar":
                                     cell(shortfall_evar)},
            "take_last_at_r_folk_must": cell(rows[r_folk]["take_last"]),
            "end_empty_at_r_folk_walk": cell(rows[r_folk]["empty"]),
            "walk_frontier": {
                "r_star_E_walk_ties": ew_ties,
                "E_walk_at_r_star": cell(ew_best),
                "E_walk_at_r_folk": cell(rows[r_folk]["ew"]),
                "r_star_P_best_ties": pb_ties,
                "note": "P_best is convention-independent (rank-1 row equal "
                        "in both conventions, gated)"},
            "P_best_r_folk_minus_1_over_e_bounds": {
                "lower": cell(diff_lo), "upper": cell(diff_hi)},
            "selected_rank_quartiles_must": q,
            "frontier": [
                {"r": r, "P_best": fs(rows[r]["pb"]),
                 "E_must": fs(rows[r]["em"]), "E_walk": fs(rows[r]["ew"]),
                 "P_best_dec": dec(rows[r]["pb"]),
                 "E_must_dec": dec(rows[r]["em"]),
                 "E_walk_dec": dec(rows[r]["ew"])}
                for r in sorted(rows)],
        }
        print(f"{N:>4} {r_folk:>6} {str(ev_ties):>8} {str(pb_ties):>8} "
              f"{fs(dv):>14} {dec(dv, 5):>9} {fs(b):>16} {dec(b, 5):>9}")

    print()
    print("REPORTING-ONLY columns (cannot flip the decision):")
    for N in grid:
        d = results_per_n[str(N)]
        print(f"  N={N:>3}: dR={d['dR']['frac']} ({d['dR']['dec']}) · "
              f"own-objective shortfall={d['own_objective_shortfall']['frac']}"
              f" ({d['own_objective_shortfall']['dec']}) · "
              f"take-last@r_folk={d['take_last_at_r_folk_must']['frac']} · "
              f"end-empty@r_folk={d['end_empty_at_r_folk_walk']['frac']} · "
              f"r_e={d['r_e_variant']} (dV_evar="
              f"{d['e_variant_deltas']['dV_evar']['frac']}) · "
              f"quartiles(must) folk={d['selected_rank_quartiles_must']['r_folk']}"
              f" r*_R={d['selected_rank_quartiles_must']['r_star_R']}"
              f" r*_V={d['selected_rank_quartiles_must']['r_star_V']} · "
              f"walk r*_E={d['walk_frontier']['r_star_E_walk_ties']} "
              f"E_walk*={d['walk_frontier']['E_walk_at_r_star']['frac']} · "
              f"P_best(r_folk)-1/e in "
              f"({d['P_best_r_folk_minus_1_over_e_bounds']['lower']['dec']}, "
              f"{d['P_best_r_folk_minus_1_over_e_bounds']['upper']['dec']})")
    print()

    # -------------------------------------------------- pre-registered ruling
    print("-" * 78)
    print("PRE-REGISTERED DECISION RULE — evaluated IN ORDER "
          "(exact Fraction comparisons)")
    print("-" * 78)
    reject_cells = {N: dV[N] <= thr_reject for N in grid}
    print(f"1. REJECT iff dV(N) <= 1/50 at EVERY swept N (checked FIRST):")
    for N in grid:
        rel = "<=" if reject_cells[N] else ">"
        print(f"     N={N:>3}: dV = {fs(dV[N])} ({dec(dV[N], 5)}) {rel} 1/50")
    reject = all(reject_cells.values())
    print(f"   REJECT {'FIRES' if reject else 'does not fire'}")

    approve = False
    if not reject:
        app_rows = {}
        print(f"2. APPROVE iff dV(N) >= 1/20 AND B(N) >= 3/20 at every "
              f"N in {decision_cells}:")
        for N in decision_cells:
            c1 = dV[N] >= thr_app_dv
            c2 = Bmap[N] >= thr_app_b
            app_rows[N] = c1 and c2
            print(f"     N={N:>3}: dV = {fs(dV[N])} ({dec(dV[N], 5)}) "
                  f"{'>=' if c1 else '<'} 1/20 · B = {fs(Bmap[N])} "
                  f"({dec(Bmap[N], 5)}) {'>=' if c2 else '<'} 3/20")
        approve = all(app_rows.values())
        print(f"   APPROVE {'FIRES' if approve else 'does not fire'}")

    verdict = "reject" if reject else ("approve" if approve else "null")
    print(f"3. NULL otherwise.")
    print()
    print(f"RULING: {verdict.upper()}")
    print()

    # drafting-liveness sanity note (non-binding, disclosed in fixtures)
    print("drafting-liveness context (non-binding): predicted dV "
          f"{fx['drafting_liveness_nonbinding']['dV_predicted']}; "
          f"B bracket {fx['drafting_liveness_nonbinding']['B_bracket']}")
    print()

    # -------------------------------------------------- self-check summary
    n_pass, n_fail = len(_CHECKS_PASSED), len(_CHECKS_FAILED)
    print(f"SELF-CHECKS: {n_pass} passed, {n_fail} failed")
    if n_fail:
        print("RUN INVALID — gate failure(s) listed above.")
        sys.exit(1)

    results = {
        "verdict": verdict,
        "decision_trace": {
            "order": ["REJECT", "APPROVE", "NULL"],
            "REJECT": {"rule": "dV(N) <= 1/50 at EVERY swept N",
                       "per_N": {str(N): {"dV": cell(dV[N]),
                                          "passes": reject_cells[N]}
                                 for N in grid},
                       "fires": reject},
            "APPROVE": {"rule": "dV(N) >= 1/20 AND B(N) >= 3/20 at every "
                                "N in {50, 100, 200}",
                        "per_N": {str(N): {"dV": cell(dV[N]),
                                           "B": cell(Bmap[N])}
                                  for N in decision_cells},
                        "fires": approve},
        },
        "per_N": results_per_n,
        "self_checks": {"passed": n_pass, "failed": n_fail},
        "seed_registry": fx["seed_registry"],
    }
    (HERE / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print("results.json written.")


if __name__ == "__main__":
    main()
