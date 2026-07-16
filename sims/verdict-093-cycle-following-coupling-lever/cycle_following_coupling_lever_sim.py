#!/usr/bin/env python3
"""VERDICT 093 sim — cycle-following coupling lever (idea-engine PROPOSAL 080).

Three-arm, hermetic, stdlib-only, pre-registered (fixtures.json committed
BEFORE this runner):

  Arm A — seedless exact closed forms (DECISION-bearing): the harmonic law
          P = 1 - sum_{k=b+1}^{m} 1/k for b >= n, the per-length law m!/k,
          the marginal law b/m, the below-n correction terms m!/50 and
          m!/32, the decrement/alternating identities, the rational ln-2
          bracket. Pure Fraction/integer arithmetic, platform-independent.
  Arm B — independently-written brute enumerations (its own cycle walker,
          its own bookkeeping): full permutation loops at m in {4, 6, 8},
          fixed-element cycle-length tables, the 720-sigma repair and
          conjugation loops on all three pinned arrangements, the same-set
          and independent-sets pencil enumerations — plus the cycle-type
          PARTITION census (the third counting method). Tied to Arm A
          through the typed must-equal contacts C1-C4.
  Arm R — seeded random episodes, REPORTING-ONLY (no statistical gate):
          m = 100, one Fisher-Yates permutation per episode under the
          REGISTERED draw-order grammar (exactly 99 randrange draws,
          i = 99..1, one random.Random per seed). Seeds 20261714/20261715;
          presentation shuffle 20261716 (presentation legs only); aux
          20261717 reserved and NEVER read.

Decision rule (registered order, twin independently-written evaluators over
an ENUMERATED boolean input set): REJECT -> INVALID -> APPROVE -> NULL.

Deterministic: no wall clock, no absolute paths, no network, no git at run
time; stdout and results.json are byte-identical across process runs.
CPython 3.11 pinned and asserted.
"""

import itertools
import json
import math
import os
import random
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)

CHECKS = []          # (name, ok(bool), detail)
RESULTS = {}         # measured values -> results.json
SEEDS_CONSTRUCTED = []


def check(name, ok, detail):
    CHECKS.append((name, bool(ok), str(detail)))
    print("  [%s] %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# display conventions (disclosed in fixtures._disclosures.decimal_display)
# ---------------------------------------------------------------------------

def dec_rhu(fr, places):
    """Round-half-up decimal string of a non-negative Fraction."""
    scaled = fr * 10 ** places
    q, r = divmod(scaled.numerator, scaled.denominator)
    if 2 * r >= scaled.denominator:
        q += 1
    s = str(q).zfill(places + 1)
    return s[:-places] + "." + s[-places:]


def sig4(fr):
    """4-significant-digit mantissa/exponent string of a positive Fraction."""
    e = 0
    x = fr
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    m = x * 1000
    q, r = divmod(m.numerator, m.denominator)
    if 2 * r >= m.denominator:
        q += 1
    if q >= 10000:
        q //= 10
        e += 1
    s = str(q)
    return s[0] + "." + s[1:] + "e" + str(e)


# ---------------------------------------------------------------------------
# Arm A — seedless exact closed forms (DECISION-bearing)
# ---------------------------------------------------------------------------

def T_of(n):
    return sum(F(1, k) for k in range(n + 1, 2 * n + 1))


def P_of(n):
    return 1 - T_of(n)


def harmonic_success(m, b):
    """Closed-form joint pointer success for b >= m/2 (the harmonic law)."""
    assert 2 * b >= m
    return 1 - sum(F(1, k) for k in range(b + 1, m + 1))


def naive_harmonic_census(m, b):
    """The (wrong-below-n) naive census m! * (1 - sum 1/k) as an integer."""
    v = math.factorial(m) * (1 - sum(F(1, k) for k in range(b + 1, m + 1)))
    assert v.denominator == 1
    return v.numerator


# ---------------------------------------------------------------------------
# Arm B — independently-written enumerations (own walker, own bookkeeping)
# ---------------------------------------------------------------------------

def cycle_lengths(perm):
    """Cycle lengths of a permutation given as a tuple/list (own walker)."""
    m = len(perm)
    seen = [False] * m
    out = []
    for start in range(m):
        if seen[start]:
            continue
        length = 0
        x = start
        while not seen[x]:
            seen[x] = True
            x = perm[x]
            length += 1
        out.append(length)
    return out


def cycle_length_of(perm, elem):
    """Length of the cycle containing elem (separate bookkeeping)."""
    length = 0
    x = elem
    while True:
        x = perm[x]
        length += 1
        if x == elem:
            return length


def compose(a, b):
    """(a o b)(x) = a[b[x]]."""
    return tuple(a[b[x]] for x in range(len(a)))


def inverse(p):
    q = [0] * len(p)
    for i, v in enumerate(p):
        q[v] = i
    return tuple(q)


def brute_tables(m):
    """One full pass over S_m: (joint census per b, fixed-elem per-length,
    per-long-cycle-length counts, partition sanity)."""
    joint = [0] * (m + 1)              # joint[b] = #perms with max cycle <= b
    elem0 = [0] * (m + 1)              # elem0[l] = #perms with cyclen(0) == l
    longk = dict((k, 0) for k in range(1, m + 1))  # perms having a cycle of length exactly k > m/2
    partition_ok = True
    total = 0
    for p in itertools.permutations(range(m)):
        total += 1
        cs = cycle_lengths(p)
        if sum(cs) != m:
            partition_ok = False
        mx = max(cs)
        for b in range(mx, m + 1):
            joint[b] += 1
        elem0[cycle_length_of(p, 0)] += 1
        for k in set(cs):
            if 2 * k > m:
                longk[k] += 1
    return {"total": total, "joint": joint, "elem0": elem0,
            "longk": longk, "partition_ok": partition_ok}


# --- the third counting method: cycle-type partition census ---------------

def partitions(n, maxpart):
    if n == 0:
        yield ()
        return
    for p in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - p, p):
            yield (p,) + rest


def perms_of_cycle_type(m, part):
    counts = {}
    for k in part:
        counts[k] = counts.get(k, 0) + 1
    denom = 1
    for k, ck in counts.items():
        denom *= (k ** ck) * math.factorial(ck)
    return math.factorial(m) // denom


def partition_census(m, b):
    return sum(perms_of_cycle_type(m, part)
               for part in partitions(m, m) if max(part) <= b)


# ---------------------------------------------------------------------------
# Arm R — seeded reporting-only episode traces (registered draw grammar)
# ---------------------------------------------------------------------------

def arm_r_run(seed, episodes):
    """(wins, failing_episodes, failing_player_mass, draw_count)."""
    rng = make_rng(seed)
    wins = failing = mass = draws = 0
    for _ in range(episodes):
        p = list(range(100))
        for i in range(99, 0, -1):          # exactly m - 1 = 99 draws, i = 99..1
            j = rng.randrange(i + 1)
            draws += 1
            p[i], p[j] = p[j], p[i]
        cs = cycle_lengths(p)
        if max(cs) <= 50:
            wins += 1
        else:
            failing += 1
            mass += sum(c for c in cs if c > 50)
    return wins, failing, mass, draws


# ---------------------------------------------------------------------------
# twin decision evaluators (independently written)
# ---------------------------------------------------------------------------

def evaluator_one(r1, r2, r3, r4, gates_ok, approve_cond):
    if r1 and r2 and r3 and r4:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if approve_cond:
        return "APPROVE"
    return "NULL"


def evaluator_two(r1, r2, r3, r4, gates_ok, approve_cond):
    reject_votes = sum(1 for c in (r1, r2, r3, r4) if c)
    token = "NULL"
    if approve_cond:
        token = "APPROVE"
    if gates_ok is False:
        token = "INVALID"
    if reject_votes == 4:
        token = "REJECT"
    return token


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("VERDICT 093 sim — cycle-following coupling lever (PROPOSAL 080)")
    print("pure-math head: m = 2n boxes/players, one shared uniform permutation")

    # F0 — harness pins -----------------------------------------------------
    pyminor = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    check("F0.python-minor-pinned", pyminor == FIX["arm_r"]["cpython_pin"].split(" ")[0],
          "CPython %s (pinned %s; Arms A/B are platform-independent exact arithmetic)"
          % (pyminor, FIX["arm_r"]["cpython_pin"].split(" ")[0]))

    A = FIX["anchors_F3"]

    # Arm A small values ----------------------------------------------------
    P_small = [P_of(i) for i in range(1, 6)]
    reg_small = [F(*FIX["laws"]["P_small"]["P%d" % i]) for i in range(1, 6)]
    check("F1.P1-P5", P_small == reg_small,
          "P1..P5 == 1/2, 5/12, 23/60, 307/840, 893/2520 (exact Fractions)")

    # Arm B full enumerations at m in {4, 6, 8} ------------------------------
    tables = dict((m, brute_tables(m)) for m in (4, 6, 8))
    check("F1.factorial-counts",
          all(tables[m]["total"] == math.factorial(m) for m in (4, 6, 8)),
          "24 / 720 / 40,320 permutations enumerated")
    check("F1.cycle-partition",
          all(tables[m]["partition_ok"] for m in (4, 6, 8)),
          "cycle lengths of every enumerated permutation sum to m (m in {4, 6, 8})")

    # C2 / F2b — uniform cycle length of a fixed element --------------------
    c2_ok = True
    for m in (4, 6, 8):
        fm1 = math.factorial(m - 1)
        col = tables[m]["elem0"]
        c2_ok &= all(col[l] == fm1 for l in range(1, m + 1))
        c2_ok &= sum(col[1:]) == math.factorial(m)
    check("C2.uniform-cycle-length", c2_ok,
          "fixed element's cycle length uniform: (m-1)! per length, summing to m! (m in {4, 6, 8})")

    marg6 = [sum(tables[6]["elem0"][1:b + 1]) for b in (2, 3, 4)]
    check("F2b.marginals-m6", marg6 == [A["marginals_m6_of_720"]["b%d" % b] for b in (2, 3, 4)],
          "budget marginals at m = 6: %s of 720 (registered 240/360/480)" % marg6)

    marg_law_ok = True
    for m in (4, 6, 8):
        for b in range(1, m + 1):
            enum_marg = F(sum(tables[m]["elem0"][1:b + 1]), math.factorial(m))
            marg_law_ok &= enum_marg == F(b, m)
    check("F2b.marginal-law-b-over-m", marg_law_ok,
          "enumerated marginal == b/m exactly at every (m, b), m in {4, 6, 8} — R2's law")

    # F2a — the lever: three counting methods -------------------------------
    brute_census = dict((m, tables[m]["joint"][m // 2]) for m in (4, 6, 8))
    check("F2a.brute-census-m4", brute_census[4] == A["census_m4_b2"],
          "%d (registered 10)" % brute_census[4])
    check("F2a.brute-census-m6", brute_census[6] == A["census_m6_b3"],
          "%d (registered 276)" % brute_census[6])
    check("F2a.brute-census-m8", brute_census[8] == A["census_m8_b4"],
          "%d (registered 14,736)" % brute_census[8])

    closed_census = {}
    for m in (4, 6, 8):
        v = math.factorial(m) * P_of(m // 2)
        assert v.denominator == 1
        closed_census[m] = v.numerator
    check("F2a.harmonic-law-vs-brute",
          all(closed_census[m] == brute_census[m] for m in (4, 6, 8)),
          "m! * P_{m/2} == brute census at m in {4, 6, 8}")

    perlen6 = tables[6]["longk"]
    check("F2a.per-length-law-m6",
          all(perlen6[k] == math.factorial(6) // k for k in (4, 5, 6))
          and [perlen6[k] for k in (4, 5, 6)] == [FIX["laws"]["per_length_law_m6"]["k%d" % k] for k in (4, 5, 6)],
          "#{perms with a cycle of length exactly k > 3} = 6!/k: %s (registered 180/144/120)"
          % [perlen6[k] for k in (4, 5, 6)])

    part8 = partition_census(8, 4)
    part10 = partition_census(10, 5)
    closed10 = math.factorial(10) * P_of(5)
    assert closed10.denominator == 1
    check("F2a.partition-census-m8", part8 == brute_census[8],
          "%d == brute %d (independent counting method)" % (part8, brute_census[8]))
    check("F2a.partition-census-m10",
          part10 == A["census_m10_b5"] and part10 == closed10.numerator,
          "%d == 10! * 893/2520 (registered 1,285,920)" % part10)
    check("C1.counting-triangle",
          all(brute_census[m] == closed_census[m] for m in (4, 6, 8))
          and part8 == brute_census[8] and part10 == closed10.numerator,
          "brute == harmonic closed form at m in {4, 6, 8}; partition == brute at (8, 4); "
          "partition == closed form at (10, 5) — three methods, one number")

    # headline --------------------------------------------------------------
    P50 = P_of(50)
    T50 = T_of(50)
    p50_str = dec_rhu(P50, 10)
    check("F2a.headline-P50",
          p50_str == A["P50_decimal_10"]
          and [len(str(P50.numerator)), len(str(P50.denominator))] == A["P50_fraction_digits"],
          "P50 = %s (registered 0.3118278207), exact %d/%d-digit fraction"
          % (p50_str, len(str(P50.numerator)), len(str(P50.denominator))))

    ratio = P50 * F(2) ** 100
    pole = F(1, 2 ** 100)
    check("F2a.ratio", sig4(ratio) == A["ratio_P50_times_2pow100"],
          "P50 * 2^100 = %s (registered 3.953e29)" % sig4(ratio))
    check("F2a.pole-independent", sig4(pole) == A["pole_2_pow_minus_100"],
          "2^-100 = %s (registered 7.889e-31)" % sig4(pole))

    # same-set pole (Arm B enumeration; every n-set at m = 4, fixed set at m = 6)
    same_set_hits = 0
    for S in itertools.combinations(range(4), 2):
        for p in itertools.permutations(range(4)):
            contents = set(p[b] for b in S)
            if all(i in contents for i in range(4)):
                same_set_hits += 1
    fixed = (0, 1, 2)
    same6 = sum(1 for p in itertools.permutations(range(6))
                if all(i in set(p[b] for b in fixed) for i in range(6)))
    check("F2a.pole-same-set", same_set_hits == 0 and same6 == A["pole_same_set"],
          "same-set joint census 0 for every 2-set at m = 4 and the fixed 3-set at m = 6 (pigeonhole)")

    # F2c — the below-n breakdown (C4) ---------------------------------------
    true104 = partition_census(10, 4)
    naive104 = naive_harmonic_census(10, 4)
    corr104 = math.factorial(10) // 50
    true83_part = partition_census(8, 3)
    true83_brute = tables[8]["joint"][3]
    naive83 = naive_harmonic_census(8, 3)
    corr83 = math.factorial(8) // 32
    check("F2c.true-census-10-4",
          true104 == A["census_m10_b4_true"] and naive104 == A["census_m10_b4_naive"],
          "true %d = naive %d + %d (registered 632,736 = 560,160 + 72,576)"
          % (true104, naive104, true104 - naive104))
    check("F2c.true-census-8-3",
          true83_part == true83_brute == A["census_m8_b3_true"] and naive83 == A["census_m8_b3_naive"],
          "true %d (partition == brute) = naive %d + %d (registered 5,916 = 4,656 + 1,260)"
          % (true83_part, naive83, true83_part - naive83))
    check("C4.below-n-corrections",
          true104 - naive104 == corr104 == A["census_m10_b4_correction"]
          and true83_part - naive83 == corr83 == A["census_m8_b3_correction"],
          "corrections exactly +10!/50 = 72,576 at (10, 4) and +8!/32 = 1,260 at (8, 3)")

    # F2d — the adversary and the two repairs (C3) ---------------------------
    arr = FIX["world"]["adversary_arrangements_m6"]
    identity6 = tuple(arr["identity"])
    six_cycle = tuple(arr["six_cycle"])
    three3 = tuple(arr["three_plus_three"])

    adv_fail = [cycle_length_of(six_cycle, i) > 3 for i in range(6)]
    check("F2d.adversarial-6cycle-zero",
          all(adv_fail) and A["adversarial_pointer_m6_six_cycle"] == 0,
          "deterministic pointer on the 6-cycle: all 6 players fail at once (joint success 0)")

    rot100 = tuple((i + 1) % 100 for i in range(100))
    check("F2d.adversarial-100cycle-witness",
          all(cycle_length_of(rot100, i) == 100 for i in range(0, 100, 7)) and max(cycle_lengths(rot100)) == 100,
          "the m = 100 rotation is a single 100-cycle: every player's cycle exceeds b = 50 — all 100 fail at once")

    remap_census = {}
    conj_census = {}
    for name, pi in (("identity", identity6), ("six_cycle", six_cycle), ("three_plus_three", three3)):
        rc = 0
        cc = 0
        for sigma in itertools.permutations(range(6)):
            if max(cycle_lengths(compose(pi, sigma))) <= 3:          # pi o sigma
                rc += 1
            if max(cycle_lengths(compose(compose(inverse(sigma), pi), sigma))) <= 3:  # sigma^-1 pi sigma
                cc += 1
        remap_census[name] = rc
        conj_census[name] = cc
    check("F2d.remap-identity", remap_census["identity"] == A["repair_one_sided_census"],
          "one-sided remap census %d/720 on identity (registered 276)" % remap_census["identity"])
    check("F2d.remap-6cycle", remap_census["six_cycle"] == A["repair_one_sided_census"],
          "one-sided remap census %d/720 on the 6-cycle (registered 276)" % remap_census["six_cycle"])
    check("F2d.remap-3plus3", remap_census["three_plus_three"] == A["repair_one_sided_census"],
          "one-sided remap census %d/720 on 3+3 (registered 276)" % remap_census["three_plus_three"])
    check("F2d.conjugation-censuses",
          [conj_census[k] for k in ("identity", "six_cycle", "three_plus_three")]
          == [A["conjugation_censuses"][k] for k in ("identity", "six_cycle", "three_plus_three")],
          "conjugation censuses {%d, %d, %d} (registered {720, 0, 720} — cycle type frozen)"
          % (conj_census["identity"], conj_census["six_cycle"], conj_census["three_plus_three"]))
    check("C3.repair-contact",
          all(v == 276 for v in remap_census.values())
          and remap_census["identity"] == brute_census[6]
          and [conj_census[k] for k in ("identity", "six_cycle", "three_plus_three")] == [720, 0, 720],
          "remap == 276 == the uniform census for ALL THREE arrangements; conjugation {720, 0, 720}")

    # F2e — concentration + floor --------------------------------------------
    conc = F(50, 1) / T50
    check("F2e.concentration",
          dec_rhu(conc, 4) == A["E_failing_given_failure"],
          "E[# failing | joint failure] = 50/T50 = %s of 100 (registered 72.6562)" % dec_rhu(conc, 4))

    budget_rows = {}
    budget_ok = True
    for b in (55, 60, 75, 90):
        v = harmonic_success(100, b)
        budget_rows["b%d" % b] = dec_rhu(v, 10)
        budget_ok &= dec_rhu(v, 10) == A["budget_rows_decimal_10"]["b%d" % b]
    p99 = harmonic_success(100, 99)
    budget_ok &= p99 == F(99, 100)
    budget_rows["b99"] = "99/100 exactly"
    check("F2e.budget-rows", budget_ok,
          "P(b) at b = 55/60/75/90 = %s / %s / %s / %s; b = 99 == 99/100 exactly"
          % tuple(budget_rows["b%d" % b] for b in (55, 60, 75, 90)))

    decrement_ok = all(T_of(n + 1) - T_of(n) == F(1, (2 * n + 1) * (2 * n + 2))
                       for n in range(1, 200))
    check("F2e.decrement-identity", decrement_ok,
          "T_{n+1} - T_n == 1/((2n+1)(2n+2)) exactly for n = 1..199")
    check("F2e.monotone", decrement_ok,
          "hence P_n strictly decreasing (every decrement > 0), n = 1..199")

    alt_ok = all(T_of(n) == sum(F((-1) ** (j + 1), j) for j in range(1, 2 * n + 1))
                 for n in range(1, 200))
    check("F2e.alternating-identity", alt_ok,
          "T_n == the 2n-th partial sum of the alternating harmonic series, n = 1..199 "
          "(the pencil route to T_n < ln 2 FOREVER)")

    K = 60
    SK = sum(F(1, k * 2 ** k) for k in range(1, K + 1))
    tail = F(1, (K + 1) * 2 ** K)
    bracket_ok = (T50 < SK) and (tail > 0) and (tail < F(1, 10 ** 19))
    gap_lo = SK - T50
    gap_hi = SK + tail - T50
    check("F2e.ln2-bracket", bracket_ok,
          "S_60 < ln 2 < S_60 + 1/(61*2^60): T50 < S_60 certifies P50 > 1 - ln 2 "
          "(bracket width < 1e-19)")
    check("F2e.floor-gap",
          dec_rhu(gap_lo, 7) == A["floor_gap_n50_decimal_7"] == dec_rhu(gap_hi, 7),
          "gap = ln 2 - T50 in [%s, %s] at 7 places (registered 0.0049750)"
          % (dec_rhu(gap_lo, 7), dec_rhu(gap_hi, 7)))

    # F4 — pencil worlds ------------------------------------------------------
    m2_pointer = sum(1 for p in itertools.permutations(range(2))
                     if max(cycle_lengths(p)) <= 1)
    m2_indep_hits = 0
    fixed_arrangement = (0, 1)
    for choice0 in range(2):
        for choice1 in range(2):
            if fixed_arrangement[choice0] == 0 and fixed_arrangement[choice1] == 1:
                m2_indep_hits += 1
    check("F4.m2-lever",
          F(m2_pointer, 2) == F(1, 2) and F(m2_indep_hits, 4) == F(1, 4),
          "m = 2: pointer P1 = 1/2 (succeeds iff identity) vs independent baseline 1/4 "
          "— the lever visible in a two-box world")

    three_line_ok = all(F(1, 2 * n + 1) + F(1, 2 * n + 2) - F(1, n + 1)
                        == F(1, (2 * n + 1) * (2 * n + 2)) for n in range(1, 200))
    check("F4.decrement-three-lines", three_line_ok,
          "1/(2n+1) + 1/(2n+2) - 1/(n+1) == 1/((2n+1)(2n+2)) exactly, n = 1..199")

    check("F4.same-set-pigeonhole", same_set_hits == 0 and same6 == 0,
          "any fixed n-set leaves n numbers unseen — joint success 0 (enumerated at m = 4 for "
          "every 2-set and at m = 6)")

    m4_hits = 0
    arrangement4 = (0, 1, 2, 3)
    subsets4 = list(itertools.combinations(range(4), 2))
    for picks in itertools.product(subsets4, repeat=4):
        ok = True
        for player in range(4):
            target_box = arrangement4.index(player)
            if target_box not in picks[player]:
                ok = False
                break
        if ok:
            m4_hits += 1
    check("F4.independent-product",
          F(m4_hits, 6 ** 4) == F(1, 2) ** 4 and m4_hits == 81,
          "independent uniform n-subsets at m = 4, fixed arrangement: %d of 1296 == (1/2)^4"
          % m4_hits)

    # F5 — degeneracy controls ------------------------------------------------
    b_eq_m_ok = all(tables[m]["joint"][m] == math.factorial(m) for m in (4, 6))
    closed_b_eq_m = all(harmonic_success(m, m) == 1 for m in (4, 6, 8))
    check("F5.b-eq-m", b_eq_m_ok and closed_b_eq_m,
          "b = m gives P = 1 (closed form; brute census == m! at m in {4, 6})")

    b_m1_ok = all(tables[m]["joint"][m - 1] == math.factorial(m) - math.factorial(m - 1)
                  for m in (4, 6))
    closed_b_m1 = all(harmonic_success(m, m - 1) == 1 - F(1, m) for m in (4, 6, 8, 100))
    check("F5.b-eq-m-minus-1", b_m1_ok and closed_b_m1,
          "b = m - 1 gives exactly 1 - 1/m (only the full m-cycle kills; brute at m in {4, 6})")
    check("F5.b99-m100", p99 == F(99, 100),
          "b = 99 at m = 100 == 99/100 exactly")

    id_pointer_ok = all(cycle_length_of(identity6, i) == 1 for i in range(6))
    check("F5.identity-succeeds",
          id_pointer_ok and conj_census["identity"] == 720,
          "the identity arrangement succeeds under the deterministic pointer and under "
          "conjugation for every sigma (720/720)")
    check("F5.conjugation-control-3plus3", conj_census["three_plus_three"] == 720,
          "3+3 stays won 720/720 — relabeling cannot break what cycle type already blessed")

    # Arm R — seeded reporting-only traces ------------------------------------
    seeds_fix = FIX["arm_r"]["seeds"]
    r14a = arm_r_run(20261714, seeds_fix["20261714"]["N"])
    r15a = arm_r_run(20261715, seeds_fix["20261715"]["N"])
    r14b = arm_r_run(20261714, seeds_fix["20261714"]["N"])
    r15b = arm_r_run(20261715, seeds_fix["20261715"]["N"])

    check("ArmR.preview-20261714",
          list(r14a[:3]) == seeds_fix["20261714"]["preview"],
          "(wins, failing, mass) = %s (registered [6131, 13869, 1007767])" % (list(r14a[:3]),))
    check("ArmR.preview-20261715",
          list(r15a[:3]) == seeds_fix["20261715"]["preview"],
          "(wins, failing, mass) = %s (registered [2455, 5545, 403116])" % (list(r15a[:3]),))
    check("ArmR.draw-sentinels",
          r14a[3] == seeds_fix["20261714"]["draws"] and r15a[3] == seeds_fix["20261715"]["draws"],
          "exactly 99N randrange draws: %d / %d (registered 1,980,000 / 792,000)"
          % (r14a[3], r15a[3]))
    check("ArmR.determinism", r14a == r14b and r15a == r15b,
          "each seed reproduced itself exactly (in-process double run per seed)")

    trace_mean = dec_rhu(F(r14a[2], r14a[1]), 4)
    check("ArmR.concentration-trace",
          trace_mean == FIX["drafter_disclosed_landing"]["measured_concentration_trace"].split(" ")[0],
          "measured mean failing mass %s vs exact 50/T50 = %s (reporting-only; drafter's "
          "disclosed trace 72.6633)" % (trace_mean, dec_rhu(conc, 4)))

    # presentation leg (seed 20261716, reporting-only)
    roster = sorted(["census-triangle", "marginal-law", "below-n-corrections",
                     "repair-pair", "floor-bracket", "budget-rows",
                     "concentration", "headline-P50"])
    prng = make_rng(20261716)
    prng.shuffle(roster)
    print("  [info] presentation-shuffle (seed 20261716, reporting-only): " + ", ".join(roster))

    check("ArmR.presentation-seed-scoped",
          SEEDS_CONSTRUCTED == [20261714, 20261715, 20261714, 20261715, 20261716],
          "seed ledger %s — 20261716 read by the presentation leg only, after every decision "
          "and preview leg finished" % (SEEDS_CONSTRUCTED,))
    check("ArmR.aux-seed-never-read", 20261717 not in SEEDS_CONSTRUCTED,
          "seed 20261717 never constructed (no random.Random(20261717) exists in this runner)")

    # F1 Fisher-Yates per-episode sentinel (already summed; per-episode form)
    check("F1.fisher-yates-draws",
          r14a[3] == 99 * seeds_fix["20261714"]["N"] and r15a[3] == 99 * seeds_fix["20261715"]["N"],
          "the Fisher-Yates loop consumes exactly m - 1 = 99 draws per episode (i = 99..1)")

    # F3 — anchors, aggregated -----------------------------------------------
    f3_integers_ok = (
        brute_census[4] == 10 and brute_census[6] == 276 and brute_census[8] == 14736
        and part10 == 1285920 and true104 == 632736 and naive104 == 560160
        and true104 - naive104 == 72576 and true83_part == 5916 and naive83 == 4656
        and true83_part - naive83 == 1260 and marg6 == [240, 360, 480]
        and all(v == 276 for v in remap_census.values())
        and [conj_census[k] for k in ("identity", "six_cycle", "three_plus_three")] == [720, 0, 720]
        and same_set_hits == 0)
    check("F3.integer-anchors", f3_integers_ok,
          "every registered integer census reproduced verbatim (10 / 276 / 14,736 / 1,285,920 / "
          "632,736 = 560,160 + 72,576 / 5,916 / 240/360/480 / 276 x3 / {720, 0, 720} / 0)")

    f3_decimals_ok = (
        p50_str == "0.3118278207" and sig4(ratio) == "3.953e29" and sig4(pole) == "7.889e-31"
        and dec_rhu(conc, 4) == "72.6562" and budget_ok
        and dec_rhu(gap_lo, 7) == "0.0049750")
    check("F3.decimal-anchors", f3_decimals_ok,
          "every registered decimal anchor reproduced under the disclosed round-half-up "
          "convention (P50, ratio, pole, concentration, budget rows, floor gap)")

    # ---- decision clauses ----------------------------------------------------
    R1 = (all(brute_census[m] == closed_census[m] for m in (4, 6, 8))
          and part8 == brute_census[8] and part10 == 1285920
          and p50_str == "0.3118278207" and sig4(ratio) == "3.953e29"
          and sig4(pole) == "7.889e-31" and same_set_hits == 0 and same6 == 0)
    R2 = marg_law_ok and c2_ok and marg6 == [240, 360, 480]
    R3 = (dec_rhu(conc, 4) == "72.6562" and decrement_ok and bracket_ok
          and dec_rhu(gap_lo, 7) == "0.0049750" and alt_ok)
    R4 = (all(adv_fail)
          and conj_census["six_cycle"] == 0
          and [conj_census[k] for k in ("identity", "six_cycle", "three_plus_three")] == [720, 0, 720]
          and all(v == 276 for v in remap_census.values())
          and remap_census["identity"] == brute_census[6])

    check("R1.lever", R1,
          "the C1 triangle (10 / 276 / 14,736 / 1,285,920), P50 = 0.3118278207, "
          "ratio 3.953e29, poles 2^-100 and 0 — all exact")
    check("R2.marginal-invariance", R2,
          "every enumerated marginal exactly b/m ((m-1)! per length; 240/360/480 at m = 6) "
          "— the entire lift is pure dependence")
    check("R3.concentration-floor", R3,
          "50/T50 = 72.6562 of 100; decrement exactly 1/((2n+1)(2n+2)); "
          "P_n > 1 - ln 2 certified (gap 0.0049750)")
    check("R4.repairs", R4,
          "adversarial 2n-cycle zeroes the pointer; conjugation {720, 0, 720} (no-op); "
          "one-sided remap restores 276/720 == the uniform census on all three arrangements")

    # APPROVE condition (honestly computed, arithmetically excluded by C1)
    product_census_match = any(F(brute_census[m], math.factorial(m)) == F(1, 2) ** m
                               for m in (4, 6, 8))
    marginal_off = not marg_law_ok
    approve_cond = product_census_match or marginal_off
    check("F6.approve-witness-excluded", not approve_cond,
          "pointer census != the 2^-m product census at every enumerated m (276/720 != 720/2^6/720) "
          "and no enumerated marginal moved off b/m — APPROVE cannot fire beside the C1 triangle")

    # gates_ok = every non-R, non-decision check so far
    gates_ok = all(ok for name, ok, _ in CHECKS
                   if not name.startswith("R") and not name.startswith("F6.approve"))

    # twin evaluators over the ENUMERATED boolean input set
    combos_agree = all(
        evaluator_one(*combo) == evaluator_two(*combo)
        for combo in itertools.product((False, True), repeat=6))
    tok1 = evaluator_one(R1, R2, R3, R4, gates_ok, approve_cond)
    tok2 = evaluator_two(R1, R2, R3, R4, gates_ok, approve_cond)
    check("F6.twin-evaluators", combos_agree and tok1 == tok2,
          "all 64 enumerated boolean inputs agree; measured inputs -> %s / %s" % (tok1, tok2))

    ruling = tok1

    decision_inputs = {"R1": R1, "R2": R2, "R3": R3, "R4": R4,
                       "approve_cond": approve_cond, "gates_ok": gates_ok}
    print("decision inputs: " + json.dumps(decision_inputs, sort_keys=True))
    print("RULING: %s (twin evaluators agree: %s / %s)" % (ruling, tok1, tok2))

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    print("self-checks: %d total, %d passed, %d failed" % (total, passed, total - passed))

    # ---- results.json ---------------------------------------------------------
    RESULTS.update({
        "verdict": ruling,
        "decision_inputs": decision_inputs,
        "clauses": {"R1": R1, "R2": R2, "R3": R3, "R4": R4},
        "self_checks": {"total": total, "passed": passed, "failed": total - passed},
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in CHECKS],
        "measured": {
            "censuses": {"m4_b2": brute_census[4], "m6_b3": brute_census[6],
                         "m8_b4": brute_census[8], "m10_b5_partition": part10,
                         "m8_b4_partition": part8,
                         "m10_b4_true": true104, "m10_b4_naive": naive104,
                         "m8_b3_true": true83_part, "m8_b3_brute": true83_brute,
                         "m8_b3_naive": naive83},
            "per_length_law_m6": {str(k): perlen6[k] for k in (4, 5, 6)},
            "P_small": [[p.numerator, p.denominator] for p in P_small],
            "P50": {"decimal_10": p50_str,
                    "numerator_digits": len(str(P50.numerator)),
                    "denominator_digits": len(str(P50.denominator)),
                    "numerator": str(P50.numerator),
                    "denominator": str(P50.denominator)},
            "ratio_sig4": sig4(ratio), "pole_2pow_minus100_sig4": sig4(pole),
            "budget_rows": budget_rows,
            "concentration_exact_dec4": dec_rhu(conc, 4),
            "marginals_m6": marg6,
            "remap_censuses": remap_census, "conjugation_censuses": conj_census,
            "floor_gap_bracket_dec7": [dec_rhu(gap_lo, 7), dec_rhu(gap_hi, 7)],
            "ln2_bracket_K": K,
            "arm_r": {
                "20261714": {"wins": r14a[0], "failing": r14a[1], "mass": r14a[2],
                             "draws": r14a[3], "trace_mean_dec4": trace_mean},
                "20261715": {"wins": r15a[0], "failing": r15a[1], "mass": r15a[2],
                             "draws": r15a[3]},
                "seed_ledger": SEEDS_CONSTRUCTED,
            },
        },
        "environment": {"cpython_minor": pyminor,
                        "decision_arms": "seedless exact integer/Fraction arithmetic (platform-independent)"},
    })
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as out:
        json.dump(RESULTS, out, indent=1, sort_keys=True)
        out.write("\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
