#!/usr/bin/env python3
"""verdict-034: Penney's game responder-edge decay -- does "never go first"
survive word length? (idea-engine PROPOSAL 032)

Fully hermetic, fully EXACT: the entire world (the word census, both
algorithms, band constants, the three classic anchor rationals) is
constructed in-sim from the pinned constants in the committed fixtures.json
(the ONLY file read; cross-checked against in-code literals at start). All
arithmetic is fractions.Fraction. ZERO RNG, ZERO seeds, ZERO floats --
byte-identical re-run by construction, platform-independent.

Two structurally independent exact algorithms per ordered-pair cell:
  Arm A -- Conway leading numbers (integer correlations; odds B over A =
           (L(A,A)-L(A,B)) : (L(B,B)-L(B,A))).
  Arm B -- first-step absorption analysis on the two-word prefix automaton
           (<= 2L-1 transient states, longest-suffix transitions, exact
           Gaussian elimination over Fraction).
Gate: exact rational equality on every cell (1,288 decision cells + the
12-cell L=2 anchor leg).

Decision (pre-registered, evaluated in this order; bands disjoint by
construction, 13/25 < 3/5):
  REJECT  iff V(5) <= 13/25 (checked FIRST).
  APPROVE iff V(L) >= 3/5 at ALL of L in {3, 4, 5}.
  NULL    otherwise (the straddle -- a finalized outcome pinning the curve).

Run: python3 sims/verdict-034-penney-decay/penney_decay_sim.py
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

ALPHABET = ("H", "T")
L_DECISION = (3, 4, 5)
L_ANCHOR = 2
EXPECTED_CELLS = {2: 12, 3: 56, 4: 240, 5: 992}
BAND_REJECT = Fraction(13, 25)    # REJECT iff V(5) <= 13/25 (checked FIRST)
BAND_APPROVE = Fraction(3, 5)     # APPROVE iff V(L) >= 3/5 at all L in {3,4,5}
ANCHOR_TH_HH = Fraction(3, 4)     # P(TH before HH)
ANCHOR_THH_HHH = Fraction(7, 8)   # P(THH before HHH)
ANCHOR_V3 = Fraction(2, 3)        # V(3), the Gardner-table floor
TWO_TO_ONE = Fraction(2, 3)       # 'beatable at >= 2:1' threshold

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
    check(tuple(fx["census"]["L_grid_decision"]) == L_DECISION,
          "fixture L grid matches in-code literal")
    check(fx["census"]["L_anchor_leg_reporting_only"] == L_ANCHOR,
          "fixture L=2 anchor leg matches")
    check({int(k): v for k, v in
           fx["census"]["expected_ordered_pair_cells"].items()} ==
          EXPECTED_CELLS, "fixture expected cell counts match")
    check(fx["decision_rule"]["band_constant_reject"] == "13/25" and
          BAND_REJECT == Fraction(13, 25), "fixture REJECT band = 13/25")
    check(fx["decision_rule"]["band_constant_approve"] == "3/5" and
          BAND_APPROVE == Fraction(3, 5), "fixture APPROVE band = 3/5")
    anchors = fx["classic_anchors_run_invalid_on_failure"]
    check(anchors["P_TH_before_HH"] == "3/4" and ANCHOR_TH_HH ==
          Fraction(3, 4), "fixture anchor P(TH before HH) = 3/4")
    check(anchors["P_THH_before_HHH"] == "7/8" and ANCHOR_THH_HHH ==
          Fraction(7, 8), "fixture anchor P(THH before HHH) = 7/8")
    check(anchors["V_3"] == "2/3" and ANCHOR_V3 == Fraction(2, 3),
          "fixture anchor V(3) = 2/3")


# ---------------------------------------------------------------------------
# Word machinery
# ---------------------------------------------------------------------------

def words(length):
    """All 2^L words of the given length, in fixed alphabet order."""
    return tuple("".join(w) for w in itertools.product(ALPHABET,
                                                       repeat=length))


def comp(word):
    """Bitwise complement: flip every character."""
    return "".join("T" if c == "H" else "H" for c in word)


def sigma(word):
    """Folk flip-rule beater: sigma(A) = (not a2) + a1 a2 ... a_(L-1)."""
    return ("T" if word[1] == "H" else "H") + word[:-1]


# ---------------------------------------------------------------------------
# Arm A: Conway leading numbers
# ---------------------------------------------------------------------------

def conway_corr(x, y):
    """L(X,Y) = sum_{k=1..L} delta_k * 2^(k-1); delta_k = 1 iff the last k
    chars of X equal the first k chars of Y. Pure integers."""
    n = 0
    for k in range(1, len(x) + 1):
        if x[len(x) - k:] == y[:k]:
            n += 1 << (k - 1)
    return n


def arm_a(a, b):
    """P(B before A) by Conway's odds; also returns the two differences for
    the positivity gate."""
    aa_ab = conway_corr(a, a) - conway_corr(a, b)
    bb_ba = conway_corr(b, b) - conway_corr(b, a)
    return Fraction(aa_ab, aa_ab + bb_ba), aa_ab, bb_ba


# ---------------------------------------------------------------------------
# Arm B: first-step absorption on the two-word prefix automaton
# ---------------------------------------------------------------------------

def arm_b(a, b):
    """P(B before A) by exact Gaussian elimination on the prefix automaton.

    Transient states: the proper prefixes of A and of B (incl. the empty
    string), <= 2L-1 of them. On flip c from state s: if s+c is A or B,
    absorb; else move to the longest suffix of s+c that is a transient
    state (the empty string always qualifies). Returns (P(B wins from the
    empty state), number of transient states).
    """
    length = len(a)
    states = sorted({a[:i] for i in range(length)} |
                    {b[:i] for i in range(length)},
                    key=lambda s: (len(s), s))
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    state_set = set(states)

    # Row i: x_i - sum_j T_ij x_j = c_i, where T_ij is the one-step
    # transition mass from state i to transient state j and c_i the
    # one-step absorption mass into B.
    half = Fraction(1, 2)
    mat = [[Fraction(0)] * n for _ in range(n)]
    rhs = [Fraction(0)] * n
    for s in states:
        i = idx[s]
        mat[i][i] += Fraction(1)
        for c in ALPHABET:
            t = s + c
            if t == b:
                rhs[i] += half
            elif t == a:
                pass  # absorbed into A: contributes 0
            else:
                nxt = None
                for k in range(min(len(t), length - 1), -1, -1):
                    suf = t[len(t) - k:] if k else ""
                    if suf in state_set:
                        nxt = suf
                        break
                check(nxt is not None,
                      "transition from %r on %r lands in a known state "
                      "(A=%s B=%s)" % (s, c, a, b))
                mat[i][idx[nxt]] -= half

    # Gaussian elimination with partial (first-nonzero) pivoting -- exact.
    for col in range(n):
        piv = None
        for r in range(col, n):
            if mat[r][col] != 0:
                piv = r
                break
        check(piv is not None,
              "automaton system is nonsingular (A=%s B=%s)" % (a, b))
        if piv != col:
            mat[col], mat[piv] = mat[piv], mat[col]
            rhs[col], rhs[piv] = rhs[piv], rhs[col]
        inv = Fraction(1) / mat[col][col]
        mat[col] = [v * inv for v in mat[col]]
        rhs[col] *= inv
        for r in range(n):
            if r != col and mat[r][col] != 0:
                f = mat[r][col]
                mat[r] = [vr - f * vc for vr, vc in zip(mat[r], mat[col])]
                rhs[r] -= f * rhs[col]

    return rhs[idx[""]], n


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
# Census over one length
# ---------------------------------------------------------------------------

def census(length):
    """Full ordered-pair census at one length. Returns (matrix, ws) where
    matrix[(A, B)] = exact P(B before A), both arms gated per cell."""
    ws = words(length)
    check(len(ws) == 2 ** length,
          "census size: exactly 2^%d words" % length)
    matrix = {}
    max_states = 0
    for a in ws:
        for b in ws:
            if a == b:
                continue
            p_a, d1, d2 = arm_a(a, b)
            p_b, nstates = arm_b(a, b)
            max_states = max(max_states, nstates)
            check(p_a == p_b,
                  "arm A == arm B exact rational equality (L=%d, A=%s, B=%s)"
                  % (length, a, b))
            check(d1 > 0 and d2 > 0,
                  "strictly positive Conway differences (L=%d, A=%s, B=%s)"
                  % (length, a, b))
            check(nstates <= 2 * length - 1,
                  "automaton state audit: <= 2L-1 transient states "
                  "(L=%d, A=%s, B=%s, got %d)" % (length, a, b, nstates))
            matrix[(a, b)] = p_a
    check(len(matrix) == EXPECTED_CELLS[length],
          "census size: exactly %d ordered-pair cells at L=%d"
          % (EXPECTED_CELLS[length], length))
    # Independently-computed antisymmetry + complement invariance, per cell.
    for (a, b), p in matrix.items():
        check(p + matrix[(b, a)] == 1,
              "antisymmetry P(B before A) + P(A before B) = 1 "
              "(L=%d, A=%s, B=%s)" % (length, a, b))
        check(matrix[(comp(a), comp(b))] == p,
              "complement invariance (L=%d, A=%s, B=%s)" % (length, a, b))
    # Absorbing states are exactly the two full words (distinct by census).
    check(len({a for a, _ in matrix} | {b for _, b in matrix}) ==
          2 ** length, "all words appear in the census at L=%d" % length)
    return matrix, ws, max_states


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fixtures_crosscheck()

    results = {"per_L": {}, "L2_anchor_leg": None, "decision": None,
               "self_checks": None}
    summary = []

    # ---- L = 2 anchor leg (reporting-only) -------------------------------
    print("L=2 anchor leg ...", file=sys.stderr)
    m2, ws2, mx2 = census(2)
    check(m2[("HH", "TH")] == ANCHOR_TH_HH,
          "classic anchor P(TH before HH) = 3/4")
    check(m2[("TH", "HT")] == Fraction(1, 2) and
          m2[("HT", "TH")] == Fraction(1, 2),
          "fair HT-vs-TH cell: exactly 1/2 both ways")
    results["L2_anchor_leg"] = {
        "cells": len(m2),
        "max_transient_states": mx2,
        "matrix": {"%s|%s" % k: fstr(v) for k, v in sorted(m2.items())},
        "anchor_P_TH_before_HH": fstr(m2[("HH", "TH")]),
        "fair_cell_HT_vs_TH": fstr(m2[("TH", "HT")]),
    }

    # ---- decision lengths -------------------------------------------------
    v_curve = {}
    for length in L_DECISION:
        print("L=%d census ..." % length, file=sys.stderr)
        matrix, ws, mxs = census(length)

        trap = {}        # A -> max_B P(B before A)
        argmax_b = {}    # A -> sorted list of optimal responses
        folk_p = {}      # A -> P(sigma(A) before A)
        for a in ws:
            vals = {b: matrix[(a, b)] for b in ws if b != a}
            mx = max(vals.values())
            trap[a] = mx
            argmax_b[a] = sorted(b for b, v in vals.items() if v == mx)
            s = sigma(a)
            check(s != a, "sigma(A) != A (L=%d, A=%s)" % (length, a))
            check(len(s) == length and s in vals,
                  "sigma(A) is a distinct length-L word (L=%d, A=%s)"
                  % (length, a))
            folk_p[a] = vals[s]

        v_l = min(trap.values())
        v_curve[length] = v_l
        argmin_a = sorted(a for a, v in trap.items() if v == v_l)
        o_num = sum(1 for a in ws if folk_p[a] == trap[a])
        o_l = Fraction(o_num, len(ws))
        s_l = max(trap[a] - folk_p[a] for a in ws)
        f21 = Fraction(sum(1 for a in ws if trap[a] >= TWO_TO_ONE), len(ws))

        if length == 3:
            check(matrix[("HHH", "THH")] == ANCHOR_THH_HHH,
                  "classic anchor P(THH before HHH) = 7/8")
            check(v_l == ANCHOR_V3, "classic anchor V(3) = 2/3")

        tq = quartiles(trap.values())
        fq = quartiles(folk_p.values())
        results["per_L"][str(length)] = {
            "cells": len(matrix),
            "max_transient_states": mxs,
            "V": fstr(v_l), "V_dec": fdec(v_l),
            "argmin_safest_first_picks": [
                {"A": a, "optimal_responses": argmax_b[a],
                 "P_response_beats_A": fstr(trap[a])} for a in argmin_a],
            "O_folk_optimality_share": fstr(o_l),
            "O_dec": fdec(o_l),
            "O_count": "%d/%d" % (o_num, len(ws)),
            "S_worst_shortfall": fstr(s_l), "S_dec": fdec(s_l),
            "f_2to1_share": fstr(f21), "f_2to1_dec": fdec(f21),
            "trap_table": {a: {"max_B": fstr(trap[a]),
                               "max_B_dec": fdec(trap[a]),
                               "argmax_B": argmax_b[a],
                               "sigma_A": sigma(a),
                               "P_sigma_before_A": fstr(folk_p[a]),
                               "sigma_optimal": folk_p[a] == trap[a],
                               "shortfall": fstr(trap[a] - folk_p[a])}
                           for a in ws},
            "trap_distribution_min_q1_med_q3_max": [fstr(x) for x in tq],
            "trap_distribution_dec": [fdec(x) for x in tq],
            "folk_distribution_min_q1_med_q3_max": [fstr(x) for x in fq],
            "folk_distribution_dec": [fdec(x) for x in fq],
            "matrix": {"%s|%s" % k: fstr(v) for k, v in sorted(matrix.items())},
        }
        summary.append(
            "L=%d: V=%s (%s) argmin %s | O=%s (%s) S=%s (%s) f2:1=%s (%s) "
            "| cells %d, max transient states %d"
            % (length, fstr(v_l), fdec(v_l), ",".join(argmin_a), fstr(o_l),
               fdec(o_l), fstr(s_l), fdec(s_l), fstr(f21), fdec(f21),
               len(matrix), mxs))

    # ------------------------------------------------------------------
    # Pre-registered decision, evaluated in the registered order.
    # ------------------------------------------------------------------
    if v_curve[5] <= BAND_REJECT:
        ruling = "REJECT"
        reason = ("V(5) = %s (%s) <= 13/25: the never-go-first maxim is an "
                  "L=3 curiosity -- longer words are the cheap fairness fix"
                  % (fstr(v_curve[5]), fdec(v_curve[5])))
    elif all(v_curve[k] >= BAND_APPROVE for k in L_DECISION):
        ruling = "APPROVE"
        reason = ("V(L) >= 3/5 at ALL swept lengths: " +
                  "; ".join("V(%d) = %s (%s)" % (k, fstr(v_curve[k]),
                                                 fdec(v_curve[k]))
                            for k in L_DECISION) +
                  " -- the responder edge is structural at every swept "
                  "length")
    else:
        ruling = "NULL"
        reason = ("the straddle: the measured decay curve is the citable "
                  "pin -- " +
                  "; ".join("V(%d) = %s (%s)" % (k, fstr(v_curve[k]),
                                                 fdec(v_curve[k]))
                            for k in L_DECISION))
    results["decision"] = {
        "ruling": ruling,
        "evaluation_order": "REJECT (checked first) -> APPROVE -> NULL; "
                            "bands disjoint by construction (13/25 < 3/5)",
        "reason": reason,
        "V_curve": {str(k): fstr(v_curve[k]) for k in L_DECISION},
        "V_curve_dec": {str(k): fdec(v_curve[k]) for k in L_DECISION},
        "band_reject_V5_le": fstr(BAND_REJECT),
        "band_approve_all_ge": fstr(BAND_APPROVE),
        "reject_condition_held": bool(v_curve[5] <= BAND_REJECT),
        "approve_condition_held": bool(all(v_curve[k] >= BAND_APPROVE
                                           for k in L_DECISION)),
    }
    check(ruling in ("APPROVE", "REJECT", "NULL"),
          "decision issues exactly one ruling")

    total_cells = sum(EXPECTED_CELLS[k] for k in L_DECISION)
    check(total_cells == 1288, "1,288 decision cells total")
    results["census_totals"] = {"decision_cells": total_cells,
                                "with_anchor_leg": total_cells +
                                EXPECTED_CELLS[2]}

    results["self_checks"] = {"passed": N_CHECKS - N_FAILED,
                              "failed": N_FAILED}

    out_path = os.path.join(HERE, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")

    # ------------------------------------------------------------------
    # stdout summary (deterministic)
    # ------------------------------------------------------------------
    print("verdict-034 penney-decay -- exact census, zero RNG")
    print("census: 56 + 240 + 992 = 1288 decision cells + 12 L=2 anchor "
          "cells, dual exact arms gated per cell")
    print("L=2 anchors: P(TH before HH) = %s; HT-vs-TH fair cell = %s"
          % (fstr(m2[("HH", "TH")]), fstr(m2[("TH", "HT")])))
    for line in summary:
        print(line)
    print("V curve: " + "; ".join("V(%d) = %s (%s)"
                                  % (k, fstr(v_curve[k]), fdec(v_curve[k]))
                                  for k in L_DECISION))
    print("DECISION (%s): %s" % (results["decision"]["evaluation_order"],
                                 ruling))
    print("reason: %s" % reason)
    print("SELF-CHECKS: %d passed, %d failed" % (N_CHECKS - N_FAILED,
                                                 N_FAILED))
    return 1 if N_FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
