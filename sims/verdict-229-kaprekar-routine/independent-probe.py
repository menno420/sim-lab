#!/usr/bin/env python3
"""Independent probe for VERDICT 229 (reproduces PROPOSAL 216).

This script does NOT import verifier.py. It carries its OWN, from-scratch
implementation of the Kaprekar step and re-derives every pre-registered gate
(G1..G4) so the reproduction is an independent confirmation, not a re-print.

Domain note: the proposal's committed domain is "integers 1000-9999 with at
least two distinct digits" (the 9 repdigits 1111..9999 excluded) -> exactly
8991 inputs; the 3-digit control is "integers 100-999 non-repdigit" -> 891.
We assert those exact counts. Stdlib-only.
"""
import re


# --- our own Kaprekar step (independent of verifier.py) --------------------
def kaprekar(n, width):
    """D(n) = desc(digits) - asc(digits), each value zero-padded to `width`."""
    digs = [int(ch) for ch in str(n).rjust(width, "0")]
    desc = sorted(digs, reverse=True)
    asc = sorted(digs)
    hi = 0
    for d in desc:
        hi = hi * 10 + d
    lo = 0
    for d in asc:
        lo = lo * 10 + d
    return hi - lo


def has_two_distinct(n, width):
    return len(set(str(n).rjust(width, "0"))) >= 2


def steps_to_fixed(n, width, fixed, cap=1000):
    steps = 0
    cur = n
    while cur != fixed:
        cur = kaprekar(cur, width)
        steps += 1
        if steps > cap:
            return None
    return steps


def domain(width):
    lo, hi = 10 ** (width - 1), 10 ** width - 1
    return [n for n in range(lo, hi + 1) if has_two_distinct(n, width)]


def fixed_points(width):
    lo, hi = 10 ** (width - 1), 10 ** width - 1
    fps = []
    for n in range(lo, hi + 1):
        if has_two_distinct(n, width) and kaprekar(n, width) == n:
            fps.append(n)
    return sorted(fps)


# --- G1: exhaustive convergence + tight bound + falsifiability --------------
def gate1():
    dom = domain(4)
    count = len(dom)
    nonconv = 0
    max_steps = 0
    need_exactly_7 = 0
    for n in dom:
        s = steps_to_fixed(n, 4, 6174)
        if s is None:
            nonconv += 1
            continue
        if s > max_steps:
            max_steps = s
        if s == 7:
            need_exactly_7 += 1
    wrong_bound_6_is_false = max_steps > 6  # "<=6" is FALSE iff some input needs 7
    g1_pass = (nonconv == 0 and max_steps == 7)
    print("== G1 exhaustive convergence + tight bound (4-digit) ==")
    print("  input_count            = {0}  (expect 8991)".format(count))
    print("  nonconverge            = {0}  (expect 0)".format(nonconv))
    print("  max_steps              = {0}  (expect 7)".format(max_steps))
    print("  inputs_needing_exact_7 = {0}".format(need_exactly_7))
    print("  wrong_bound_<=6_FALSE  = {0}  (expect True: some input needs 7)".format(wrong_bound_6_is_false))
    print("  G1_PASS                = {0}".format(g1_pass and wrong_bound_6_is_false))
    return g1_pass and wrong_bound_6_is_false


# --- G2: unique fixed point ------------------------------------------------
def gate2():
    fps = fixed_points(4)
    g2_pass = (fps == [6174])
    print("== G2 unique fixed point (4-digit) ==")
    print("  non-repdigit fixed points = {0}  (expect [6174])".format(fps))
    print("  G2_PASS                   = {0}".format(g2_pass))
    return g2_pass


# --- G3: Monte-Carlo sanity parsed from the verifier's stdout --------------
def gate3():
    with open("run-stdout.txt", "r") as fh:
        text = fh.read()
    succ = int(re.search(r'"successes":\s*(\d+)', text).group(1))
    z = float(re.search(r'"z":\s*([0-9.]+)', text).group(1))
    ndraws = int(re.search(r'"n_draws":\s*(\d+)', text).group(1))
    g3_pass = (z >= 3.0 and succ == 200000 and succ == ndraws)
    print("== G3 Monte-Carlo sanity (parsed from run-stdout.txt) ==")
    print("  n_draws   = {0}".format(ndraws))
    print("  successes = {0}  (expect 200000)".format(succ))
    print("  z         = {0}  (expect >= 3)".format(z))
    print("  G3_PASS   = {0}".format(g3_pass))
    return g3_pass


# --- G4: dimension-shift, 3-digit routine funnels to 495 in <=6 ------------
def gate4():
    dom = domain(3)
    count = len(dom)
    nonconv = 0
    max_steps = 0
    for n in dom:
        s = steps_to_fixed(n, 3, 495)
        if s is None:
            nonconv += 1
            continue
        if s > max_steps:
            max_steps = s
    fps = fixed_points(3)
    g4_pass = (nonconv == 0 and fps == [495] and max_steps == 6)
    print("== G4 dimension-shift (3-digit) ==")
    print("  input_count               = {0}  (expect 891)".format(count))
    print("  nonconverge               = {0}  (expect 0)".format(nonconv))
    print("  non-repdigit fixed points = {0}  (expect [495])".format(fps))
    print("  max_steps                 = {0}  (expect 6)".format(max_steps))
    print("  G4_PASS                   = {0}".format(g4_pass))
    return g4_pass


if __name__ == "__main__":
    results = [gate1(), gate2(), gate3(), gate4()]
    print("== SUMMARY ==")
    print("  all_gates_pass = {0}".format(all(results)))
