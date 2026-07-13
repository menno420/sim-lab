#!/usr/bin/env python3
"""verdict-030: single-elimination seeding fairness -- is the standard 8-team
bracket exactly optimal? (idea-engine PROPOSAL 028)

Fully hermetic, fully EXACT: the entire world (tree topology, the 315-class
bracket census, five strength profiles, band constants) is constructed in-sim
from the pinned constants in the committed fixtures.json (the ONLY file read;
cross-checked against in-code literals at start). All arithmetic is
fractions.Fraction. ZERO RNG, ZERO seeds, ZERO floats -- byte-identical
re-run by construction, platform-independent.

Two structurally independent exact algorithms:
  Arm A -- winner-distribution recursion over subtrees.
  Arm B -- iterative enumeration of all 2^7 = 128 complete outcome paths.
Gate: exact rational equality on every (bracket, profile, objective) cell.

Decision (pre-registered, evaluated in this order):
  REJECT  iff Delta_a = 0 AND Delta_b = 0 exactly in ALL four decision
          profiles (checked FIRST -- the strictest claim).
  APPROVE iff Delta_a >= 1/200 in >= 1 profile OR Delta_b >= 1/100 in >= 1
          profile.
  NULL    otherwise (the sub-material straddle -- a finalized outcome).

Run: python3 sims/verdict-030-bracket-optimality/bracket_optimality_sim.py
Exit 0 iff all self-checks pass. Progress goes to stderr only.
"""

import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Pinned constants (must match fixtures.json -- cross-checked at start)
# ---------------------------------------------------------------------------

PROFILES = {
    "F0_flat_control_reporting_only": (100, 100, 100, 100, 100, 100, 100, 100),
    "F1_linear": (8, 7, 6, 5, 4, 3, 2, 1),
    "F2_geometric": (128, 64, 32, 16, 8, 4, 2, 1),
    "F3_top_heavy_one_star": (100, 8, 7, 6, 5, 4, 3, 2),
    "F4_near_flat": (107, 106, 105, 104, 103, 102, 101, 100),
}
DECISION_PROFILES = ("F1_linear", "F2_geometric", "F3_top_heavy_one_star",
                     "F4_near_flat")
ALL_PROFILES = ("F0_flat_control_reporting_only",) + DECISION_PROFILES

STANDARD_PRESENTATION = (1, 8, 4, 5, 3, 6, 2, 7)
RELABELING_REPRESENTATIVE = (7, 2, 6, 3, 5, 4, 8, 1)
BAND_A = Fraction(1, 200)   # 0.5 pp on P(best team wins)
BAND_B = Fraction(1, 100)   # 1.0 pp on P(1v2 final)
EXPECTED_CLASSES = 315
EXPECTED_PREIMAGES = 128

N_CHECKS = 0
N_FAILED = 0


def check(cond, label):
    global N_CHECKS, N_FAILED
    N_CHECKS += 1
    if not cond:
        N_FAILED += 1
        print("SELF-CHECK FAILED: %s" % label, file=sys.stderr)


def fixtures_crosscheck():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)
    for name, s in PROFILES.items():
        check(tuple(fx["strength_profiles"][name]) == s,
              "fixture profile %s matches in-code literal" % name)
    check(tuple(fx["strength_profiles"]["decision_profiles"]) ==
          DECISION_PROFILES, "fixture decision-profile list matches")
    check(tuple(fx["topology"]["standard_bracket_class"]) ==
          STANDARD_PRESENTATION, "fixture standard bracket matches")
    check(tuple(fx["topology"][
        "standard_bracket_noncanonical_representative_for_relabeling_check"])
        == RELABELING_REPRESENTATIVE, "fixture relabeling rep matches")
    check(fx["decision_rule"]["band_constant_a"] == "1/200" and
          BAND_A == Fraction(1, 200), "fixture band constant a = 1/200")
    check(fx["decision_rule"]["band_constant_b"] == "1/100" and
          BAND_B == Fraction(1, 100), "fixture band constant b = 1/100")


# ---------------------------------------------------------------------------
# Canonicalization + census
# ---------------------------------------------------------------------------

def canon(seq):
    """Recursive min-sort canonical form of a leaf tuple (length 1/2/4/8)."""
    if len(seq) == 1:
        return seq
    h = len(seq) // 2
    left, right = canon(seq[:h]), canon(seq[h:])
    return left + right if min(left) < min(right) else right + left


def census():
    """Enumerate all 8! leaf orders; return sorted tuple of the 315 classes."""
    counts = {}
    for perm in itertools.permutations(range(1, 9)):
        counts[canon(perm)] = counts.get(canon(perm), 0) + 1
    check(len(counts) == EXPECTED_CLASSES,
          "partition audit: exactly 315 canonical classes (got %d)"
          % len(counts))
    check(all(v == EXPECTED_PREIMAGES for v in counts.values()),
          "partition audit: every class has exactly 128 preimages")
    check(sum(counts.values()) == 40320,
          "partition audit: preimages sum to 8! = 40320")
    return tuple(sorted(counts))


def bkey(bracket):
    """Pinned display key: '1,8,4,5|2,7,3,6'."""
    return "%s|%s" % (",".join(map(str, bracket[:4])),
                      ",".join(map(str, bracket[4:])))


# ---------------------------------------------------------------------------
# Bradley-Terry match probabilities
# ---------------------------------------------------------------------------

def match_probs(strengths):
    """p[(i, j)] = P(team i beats team j), exact Fraction; teams 1..8."""
    p = {}
    for i in range(1, 9):
        for j in range(1, 9):
            if i != j:
                si, sj = strengths[i - 1], strengths[j - 1]
                p[(i, j)] = Fraction(si, si + sj)
    return p


# ---------------------------------------------------------------------------
# Arm A: winner-distribution recursion
# ---------------------------------------------------------------------------

def win_dist(leaves, p):
    """Exact distribution of the winner of the subtree over `leaves`."""
    if len(leaves) == 1:
        return {leaves[0]: Fraction(1)}
    h = len(leaves) // 2
    wl, wr = win_dist(leaves[:h], p), win_dist(leaves[h:], p)
    out = {}
    for i, wi in wl.items():
        out[i] = wi * sum((wr[j] * p[(i, j)] for j in wr), Fraction(0))
    for i, wi in wr.items():
        out[i] = out.get(i, Fraction(0)) + \
            wi * sum((wl[j] * p[(i, j)] for j in wl), Fraction(0))
    return out


def arm_a(bracket, p):
    """Return (P_best, P_12, root winner distribution, half distributions)."""
    h1, h2 = win_dist(bracket[:4], p), win_dist(bracket[4:], p)
    root = win_dist(bracket, p)
    p12 = (h1.get(1, Fraction(0)) * h2.get(2, Fraction(0)) +
           h1.get(2, Fraction(0)) * h2.get(1, Fraction(0)))
    return root.get(1, Fraction(0)), p12, root, h1, h2


# ---------------------------------------------------------------------------
# Arm B: complete outcome-path enumeration (iterative, bitmask-driven)
# ---------------------------------------------------------------------------

def arm_b(bracket, p):
    """Enumerate all 2^7 outcome paths of the 7 matches, round by round.

    Bit k of the mask decides match k (0 -> first-listed slot wins) in the
    fixed order QF1, QF2, QF3, QF4, SF1, SF2, F. Returns (P_best, P_12,
    winner distribution) accumulated over the 128 paths.
    """
    root = {t: Fraction(0) for t in bracket}
    p12 = Fraction(0)
    pbest = Fraction(0)
    total = Fraction(0)
    for mask in range(128):
        prob = Fraction(1)
        teams = list(bracket)
        bit = 0
        while len(teams) > 1:
            nxt = []
            for m in range(len(teams) // 2):
                a, b = teams[2 * m], teams[2 * m + 1]
                if (mask >> bit) & 1:
                    winner, loser = b, a
                else:
                    winner, loser = a, b
                prob *= p[(winner, loser)]
                nxt.append(winner)
                bit += 1
                if len(teams) == 2:          # this is the final
                    if {a, b} == {1, 2}:
                        p12 += prob
            teams = nxt
        champion = teams[0]
        root[champion] += prob
        if champion == 1:
            pbest += prob
        total += prob
    check(total == 1, "arm B: 128 path probabilities sum to exactly 1 (%s)"
          % bkey(bracket))
    return pbest, p12, root


# ---------------------------------------------------------------------------
# Exact quartiles (reporting-only; pinned linear-interpolation convention)
# ---------------------------------------------------------------------------

def quartiles(values):
    v = sorted(values)
    n = len(v)
    out = []
    for q in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        pos = (n - 1) * q
        lo = pos.numerator // pos.denominator     # floor
        frac = pos - lo
        val = v[lo] + frac * (v[lo + 1] - v[lo]) if frac else v[lo]
        out.append(val)
    return v[0], out[0], out[1], out[2], v[-1]


def fstr(x):
    return "%s/%s" % (x.numerator, x.denominator)


def fdec(x, places=6):
    """Display-only decimal string of a Fraction, correctly rounded."""
    scaled = x * 10 ** places
    q = (scaled.numerator * 2 + scaled.denominator) // (2 * scaled.denominator)
    sign = "-" if q < 0 else ""
    q = abs(q)
    return "%s%d.%0*d" % (sign, q // 10 ** places, places, q % 10 ** places)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fixtures_crosscheck()

    # Two-team degenerate identity checks (pinned fixtures).
    for (s1, s2) in ((128, 64), (107, 100)):
        d = win_dist((1, 2), {(1, 2): Fraction(s1, s1 + s2),
                              (2, 1): Fraction(s2, s1 + s2)})
        check(d[1] == Fraction(s1, s1 + s2),
              "two-team identity p_12 = %d/%d" % (s1, s1 + s2))
        check(d[1] + d[2] == 1, "two-team distribution sums to 1")

    print("census over 8! leaf orders ...", file=sys.stderr)
    brackets = census()
    standard = canon(STANDARD_PRESENTATION)
    check(standard in brackets, "standard bracket class is in the census")
    check(canon(RELABELING_REPRESENTATIVE) == standard,
          "relabeling representative canonicalizes to the standard class")

    results = {"profiles": {}, "self_checks": None, "decision": None}
    summary_lines = []
    approve_hits = []
    reject_all = True

    per_profile = {}
    for prof in ALL_PROFILES:
        print("profile %s ..." % prof, file=sys.stderr)
        s = PROFILES[prof]
        p = match_probs(s)

        vals_a, vals_b = {}, {}
        for br in brackets:
            pa, pb, root_a, h1, h2 = arm_a(br, p)
            pa_b, pb_b, root_b = arm_b(br, p)
            check(pa == pa_b, "arm A == arm B on P_best (%s, %s)"
                  % (prof, bkey(br)))
            check(pb == pb_b, "arm A == arm B on P_12 (%s, %s)"
                  % (prof, bkey(br)))
            check(root_a == root_b, "arm A == arm B on full winner "
                  "distribution (%s, %s)" % (prof, bkey(br)))
            check(sum(root_a.values(), Fraction(0)) == 1,
                  "sum_i W_root(i) = 1 (%s, %s)" % (prof, bkey(br)))
            vals_a[br], vals_b[br] = pa, pb

        # Relabeling invariance: the non-canonical representative reproduces
        # the canonical class's numbers exactly.
        ra, rb, _, _, _ = arm_a(RELABELING_REPRESENTATIVE, p)
        check(ra == vals_a[standard] and rb == vals_b[standard],
              "relabeling invariance on (%s)" % prof)

        if prof == "F0_flat_control_reporting_only":
            for br in brackets:
                root = win_dist(br, p)
                check(all(v == Fraction(1, 8) for v in root.values()),
                      "F0 closed form: P(each wins) = 1/8 (%s)" % bkey(br))
                split = (1 in br[:4]) != (2 in br[:4])
                want = Fraction(1, 16) if split else Fraction(0)
                check(vals_b[br] == want,
                      "F0 closed form: P_12 = %s (%s)"
                      % (fstr(want), bkey(br)))

        prof_res = {}
        for tag, vals, band in (("a_P_best", vals_a, BAND_A),
                                ("b_P_12", vals_b, BAND_B)):
            std_v = vals[standard]
            mx = max(vals.values())
            mn = min(vals.values())
            argmax = sorted(br for br, v in vals.items() if v == mx)
            argmin = sorted(br for br, v in vals.items() if v == mn)
            delta = mx - std_v
            rank = 1 + sum(1 for v in vals.values() if v > std_v)
            ties = sum(1 for v in vals.values() if v == std_v)
            q = quartiles(vals.values())
            prof_res[tag] = {
                "standard": fstr(std_v),
                "standard_dec": fdec(std_v),
                "max": fstr(mx), "max_dec": fdec(mx),
                "argmax": [bkey(b) for b in argmax],
                "delta": fstr(delta),
                "delta_pp": fdec(delta * 100, 4),
                "standard_rank_of_315": rank,
                "ties_at_standard_value": ties,
                "worst": fstr(mn), "worst_dec": fdec(mn),
                "argmin": [bkey(b) for b in argmin],
                "distribution_min_q1_med_q3_max": [fstr(x) for x in q],
                "distribution_dec": [fdec(x) for x in q],
                "band": fstr(band),
                "band_met": bool(delta >= band),
                "exactly_optimal": bool(delta == 0),
            }
        prof_res["argmax_a_vs_b_differ"] = (
            prof_res["a_P_best"]["argmax"] != prof_res["b_P_12"]["argmax"])
        results["profiles"][prof] = prof_res
        per_profile[prof] = prof_res

        if prof in DECISION_PROFILES:
            da = prof_res["a_P_best"]
            db = prof_res["b_P_12"]
            if not (da["exactly_optimal"] and db["exactly_optimal"]):
                reject_all = False
            if da["band_met"]:
                approve_hits.append("%s: Delta_a = %s (%s pp) >= 1/200"
                                    % (prof, da["delta"], da["delta_pp"]))
            if db["band_met"]:
                approve_hits.append("%s: Delta_b = %s (%s pp) >= 1/100"
                                    % (prof, db["delta"], db["delta_pp"]))

    # ------------------------------------------------------------------
    # Pre-registered decision, evaluated in the registered order.
    # ------------------------------------------------------------------
    if reject_all:
        ruling = "REJECT"
        reason = ("Delta_a = 0 AND Delta_b = 0 by exact rational equality "
                  "in ALL four decision profiles")
    elif approve_hits:
        ruling = "APPROVE"
        reason = "; ".join(approve_hits)
    else:
        ruling = "NULL"
        reason = ("the straddle: suboptimality exists but every gap is "
                  "sub-material (all Delta_a < 1/200 and all Delta_b < "
                  "1/100, not all zero)")
    results["decision"] = {
        "ruling": ruling,
        "evaluation_order": "REJECT (checked first) -> APPROVE -> NULL",
        "reason": reason,
        "approve_band_hits": approve_hits,
        "reject_condition_held": reject_all,
    }
    results["standard_bracket_canonical"] = bkey(standard)
    results["census"] = {"classes": len(brackets),
                         "preimages_per_class": EXPECTED_PREIMAGES,
                         "total_leaf_orders": 40320}

    check(ruling in ("APPROVE", "REJECT", "NULL"),
          "decision issues exactly one ruling")

    results["self_checks"] = {"passed": N_CHECKS - N_FAILED,
                              "failed": N_FAILED}

    out_path = os.path.join(HERE, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")

    # ------------------------------------------------------------------
    # stdout summary (deterministic)
    # ------------------------------------------------------------------
    print("verdict-030 bracket-optimality -- exact census, zero RNG")
    print("census: %d classes x %d preimages (8! = 40320 audited)"
          % (len(brackets), EXPECTED_PREIMAGES))
    print("standard bracket canonical form: %s" % bkey(standard))
    for prof in ALL_PROFILES:
        r = per_profile[prof]
        for tag, label in (("a_P_best", "P(best wins)"),
                           ("b_P_12", "P(1v2 final)")):
            t = r[tag]
            print("%s %s: std %s (%s) rank %d/315 (ties %d) | max %s (%s) "
                  "argmax %s | Delta %s = %s pp | worst %s (%s)"
                  % (prof, label, t["standard"], t["standard_dec"],
                     t["standard_rank_of_315"], t["ties_at_standard_value"],
                     t["max"], t["max_dec"], t["argmax"][0], t["delta"],
                     t["delta_pp"], t["worst"], t["worst_dec"]))
        print("%s argmax(a) != argmax(b): %s"
              % (prof, r["argmax_a_vs_b_differ"]))
    print("DECISION (%s): %s" % (results["decision"]["evaluation_order"],
                                 ruling))
    print("reason: %s" % reason)
    print("SELF-CHECKS: %d passed, %d failed" % (N_CHECKS - N_FAILED,
                                                 N_FAILED))
    return 1 if N_FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
