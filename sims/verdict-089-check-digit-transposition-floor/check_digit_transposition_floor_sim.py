#!/usr/bin/env python3
"""VERDICT 089 runner — the check-digit transposition floor (idea-engine P076).

Hermetic: reads ONLY the fixtures.json beside this file. Zero repo/network
reads at verdict time. Every decision number is an exact integer.

Model: position-wise mod-10 schemes  sum_i sigma_i(d_i) = 0 (mod 10), each
sigma_i a permutation of Z10. An adjacent swap at boundary i escapes iff the
difference map tau(y) = sigma_i(y) - sigma_{i+1}(y) (mod 10) collides at the
swapped digits; the boundary census depends only on the quotient permutation
pi = sigma_i o sigma_{i+1}^-1 (lemma, spot-verified), so the whole design
space is the 10! quotient space — enumerated COMPLETELY here.

Arms:
  A — seedless exact integer counting (DECISION-bearing): the complete 10!
      quotient census + the Sigma-certificate checked symbolically beside it,
      the quotient-reduction lemma on the pinned 36-pair spot set, the 10x10
      linear weight grid + the 16-cell cross contact, the ISBN-10 / EAN-13 /
      ALL-ONES position censuses with full-code pattern counts, the Damm
      property gates + state censuses, degeneracy controls, pencil worlds.
  B — INDEPENDENTLY-WRITTEN twin (second decision evaluator's inputs): full
      length-4 word-level enumerations for LUHN / EAN-style / 11-ary / DAMM
      with the FOUR typed must-equal contacts and the ordered-pair
      multiplicity law asserted directly; its own reduced quotient census
      (pi(0) = 0 slice, pairwise-comparison U, x10 shift-orbit gate); its
      own boundary scans, grid scan, and ISBN/EAN/Damm re-derivations.
  R — seeded identifier careers, REPORTING-ONLY (no statistical gate; sole
      gates are the 600,000-draw sentinel and exact reproducibility).

Gates F1-F6 per the P076 registration; decision order REJECT -> INVALID ->
APPROVE -> NULL (REJECT evaluated FIRST) via twin independently-written
evaluators. Disclosed-anchor mismatches raise first-class anomalies
(structured census: matched / mismatched / vacant — the V087/V088
convention).
"""

import json
import random
import sys
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent

assert sys.version_info[:2] == (3, 11), (
    "CPython 3.11 pinned (fixture battery cpython pin); got %s" % (sys.version_info[:2],)
)

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- helpers
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []
ANOMALIES = []
COVERAGE = []  # structured anomaly census rows: (name, disclosed, computed, status)


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
    return bool(cond)


def anomaly(text):
    ANOMALIES.append("A%d: %s" % (len(ANOMALIES) + 1, text))


def cover(name, disclosed, computed):
    """Coverage row: disclosed-vs-computed comparison (matched/mismatched)."""
    status = "matched" if disclosed == computed else "MISMATCHED"
    COVERAGE.append({"name": name, "disclosed": disclosed, "computed": computed, "status": status})
    if status == "MISMATCHED":
        anomaly("disclosed %r = %r but computed %r (reporting comparison; see REPORT)" % (name, disclosed, computed))
    return status == "matched"


def vacancy(name, note):
    COVERAGE.append({"name": name, "disclosed": None, "computed": note, "status": "vacant"})


# seed factory registry (aux-never-read assert)
SEEDS_READ = []


def make_rng(seed):
    SEEDS_READ.append(seed)
    return random.Random(seed)


# =========================================================== Arm A (decision)
LUHN = list(FIX["luhn_fold"])
DAMM = [list(r) for r in FIX["damm_table"]]
ANCH = FIX["f3_census_anchors"]

# ---- F1: model identities -------------------------------------------------
check("F1 luhn fold law", LUHN == [(2 * d if d < 5 else 2 * d - 9) for d in range(10)])
check("F1 luhn fold is a permutation", sorted(LUHN) == list(range(10)))
UNITS = sorted(w for w in range(10) if any((w * x) % 10 == 1 for x in range(10)))
check("F1 units mod 10 = {1,3,7,9}", UNITS == [1, 3, 7, 9])
check("F1 units all odd", all(w % 2 == 1 for w in UNITS))
check("F1 certificate arithmetic", sum(range(10)) == 45 and 45 % 10 == 5 and 5 != 0)
cover("certificate perm_sum/mod/tau_sum", [45, 5, 0],
      [sum(range(10)), sum(range(10)) % 10, (45 - 45) % 10])


def damm_digest(word, table=DAMM):
    c = 0
    for d in word:
        c = table[c][d]
    return c


check("F1 damm digest determinism", all(
    damm_digest(w) == damm_digest(list(w)) for w in [(0,) * 4, (9, 8, 7, 6), (1, 2, 3, 4)]))

# ---- Arm A census machinery ------------------------------------------------


def U_of_perm(p):
    """Boundary census of quotient permutation p: ordered pairs (a,b), a!=b,
    with tau(a) == tau(b), tau(y) = p[y] - y mod 10. Count-based."""
    t = [0] * 10
    for y in range(10):
        t[(p[y] - y) % 10] += 1
    return sum(c * c for c in t) - 10


def full_census_A():
    """Complete 10! quotient census (the decision leg). Unrolled hot loop."""
    M = [tuple((v - i) % 10 for v in range(10)) for i in range(10)]
    M0, M1, M2, M3, M4, M5, M6, M7, M8, M9 = M
    hist = {}
    max_perms = []
    for p0, p1, p2, p3, p4, p5, p6, p7, p8, p9 in permutations(range(10)):
        t = [0] * 10
        t[M0[p0]] += 1; t[M1[p1]] += 1; t[M2[p2]] += 1; t[M3[p3]] += 1; t[M4[p4]] += 1
        t[M5[p5]] += 1; t[M6[p6]] += 1; t[M7[p7]] += 1; t[M8[p8]] += 1; t[M9[p9]] += 1
        u = (t[0] * t[0] + t[1] * t[1] + t[2] * t[2] + t[3] * t[3] + t[4] * t[4]
             + t[5] * t[5] + t[6] * t[6] + t[7] * t[7] + t[8] * t[8] + t[9] * t[9] - 10)
        hist[u] = hist.get(u, 0) + 1
        if u == 90:
            max_perms.append((p0, p1, p2, p3, p4, p5, p6, p7, p8, p9))
    return hist, max_perms


HIST_A, MAX_PERMS = full_census_A()
TOTAL_A = sum(HIST_A.values())
MIN_U = min(HIST_A)
MAX_U = max(HIST_A)

# F2(a) — the FLOOR
check("F2a histogram total 3628800", TOTAL_A == 3628800)
check("F2a no U=0 bin (certificate confirmed exhaustively)", 0 not in HIST_A)
check("F2a min U = 2", MIN_U == 2)
check("F2a minimizer count 46400", HIST_A[2] == 46400)
check("F2a max U = 90 with count 10", MAX_U == 90 and HIST_A[90] == 10)
ROTATIONS = sorted(tuple((y + c) % 10 for y in range(10)) for c in range(10))
check("F2a the 10 maximizers are exactly the rotations", sorted(MAX_PERMS) == ROTATIONS)
check("F2a support even-only", all(u % 2 == 0 for u in HIST_A))
cover("histogram support", FIX["histogram_disclosed_support"], sorted(HIST_A))
cover("min U / minimizers / max U / rotations / total",
      [ANCH["min_U"], ANCH["minimizer_count"], ANCH["max_U"], ANCH["rotation_count_at_max"], ANCH["histogram_total"]],
      [MIN_U, HIST_A[MIN_U], MAX_U, len(MAX_PERMS), TOTAL_A])

# Luhn's quotient cell + miss set
LUHN_U = U_of_perm(LUHN)
LUHN_TAU = [(LUHN[y] - y) % 10 for y in range(10)]
LUHN_MISS = sorted((a, b) for a in range(10) for b in range(10)
                   if a != b and LUHN_TAU[a] == LUHN_TAU[b])
check("F2a Luhn census = 2", LUHN_U == 2)
check("F2a Luhn miss set {(0,9),(9,0)}", LUHN_MISS == [(0, 9), (9, 0)])
cover("luhn boundary census + miss set",
      [ANCH["luhn_boundary_census"], [tuple(x) for x in ANCH["luhn_miss_set_ordered"]]],
      [LUHN_U, LUHN_MISS])

# quotient-reduction lemma on the 36-pair spot set (perms SIM-CHOSEN, disclosed)
SPOT = {k: list(v) for k, v in FIX["quotient_reduction_spot_set"]["perms"].items()}
for name_i, si in sorted(SPOT.items()):
    check("F1 spot perm %s is a permutation" % name_i, sorted(si) == list(range(10)))
INV = {}
for name, p in SPOT.items():
    inv = [0] * 10
    for y in range(10):
        inv[p[y]] = y
    INV[name] = inv
spot_pairs_checked = 0
for name_i, si in sorted(SPOT.items()):
    for name_j, sj in sorted(SPOT.items()):
        direct = sum(1 for a in range(10) for b in range(10)
                     if a != b and (si[a] + sj[b]) % 10 == (si[b] + sj[a]) % 10)
        quotient = [si[INV[name_j][x]] for x in range(10)]
        check("F2a lemma %s|%s" % (name_i, name_j), direct == U_of_perm(quotient))
        spot_pairs_checked += 1
check("F2a lemma spot set = 36 pairs", spot_pairs_checked == 36)
vacancy("quotient_reduction_spot_set perms",
        "registered by SIZE only (6 perms / 36 pairs); the six permutations are sim-chosen and disclosed in fixtures.json")

# shift-invariance (the x10 orbit fact behind Arm B's reduced census)
for name, p in sorted(SPOT.items()):
    for c in range(10):
        shifted = [(p[y] + c) % 10 for y in range(10)]
        check("F2a shift-invariance %s+%d" % (name, c), U_of_perm(shifted) == U_of_perm(p))

# ---- F2(b): the LINEAR ESCAPE ----------------------------------------------


def linear_adj_miss(w1, w2):
    return sum(1 for a in range(10) for b in range(10)
               if a != b and ((w1 - w2) * (a - b)) % 10 == 0)


def catches_all_singles(w):
    return all((w * (a - b)) % 10 != 0 for a in range(10) for b in range(10) if a != b)


GRID = {(w1, w2): linear_adj_miss(w1, w2) for w1 in range(10) for w2 in range(10)}
ALL_SINGLES = sorted((w1, w2) for w1 in range(10) for w2 in range(10)
                     if catches_all_singles(w1) and catches_all_singles(w2))
check("F2b 16 all-singles cells", len(ALL_SINGLES) == 16 and
      ALL_SINGLES == sorted(product(UNITS, UNITS)))
diag = [c for c in ALL_SINGLES if c[0] == c[1]]
offd = [c for c in ALL_SINGLES if c[0] != c[1]]
check("F2b diagonal 4 cells miss 90", len(diag) == 4 and all(GRID[c] == 90 for c in diag))
check("F2b off-diagonal 12 cells miss 10", len(offd) == 12 and all(GRID[c] == 10 for c in offd))
LINEAR_FLOOR = min(GRID[c] for c in ALL_SINGLES)
check("F2b linear floor = 10", LINEAR_FLOOR == 10)
ESCAPE_13 = sorted((a, b) for a in range(10) for b in range(10)
                   if a != b and ((1 - 3) * (a - b)) % 10 == 0)
check("F2b escape set at (1,3) is the ten |a-b|=5 ordered pairs",
      ESCAPE_13 == sorted((a, b) for a in range(10) for b in range(10) if abs(a - b) == 5))
cover("linear partition {16, 4x90, 12x10, floor}",
      [ANCH["linear_all_singles_cells"], ANCH["linear_partition"]["diagonal_miss"],
       ANCH["linear_partition"]["off_diagonal_miss"], ANCH["linear_floor"]],
      [len(ALL_SINGLES), GRID[diag[0]], GRID[offd[0]], LINEAR_FLOOR])
cover("ean escape set (ordered)", sorted(tuple(x) for x in ANCH["ean_escape_set_ordered"]), ESCAPE_13)

# cross contact: multiplicative quotient reproduces the grid count on all 16 unit cells
INV10 = {w: next(x for x in range(10) if (w * x) % 10 == 1) for w in UNITS}
for (w1, w2) in ALL_SINGLES:
    q = [(w1 * INV10[w2] * y) % 10 for y in range(10)]
    check("F2b cross contact (%d,%d)" % (w1, w2), U_of_perm(q) == GRID[(w1, w2)])

# ---- F2(c): REGRESSION + EXITS ----------------------------------------------
ISBN_W = FIX["schemes"]["ISBN10"]["weights"]
isbn_sub_missed = 0
isbn_sub_checks = 0
for w in ISBN_W:
    for a in range(11):
        for b in range(11):
            if a != b:
                isbn_sub_checks += 1
                if (w * (a - b)) % 11 == 0:
                    isbn_sub_missed += 1
isbn_tr_missed = 0
isbn_tr_checks = 0
for i in range(10):
    for j in range(i + 1, 10):
        for a in range(11):
            for b in range(11):
                if a != b:
                    isbn_tr_checks += 1
                    if ((ISBN_W[i] - ISBN_W[j]) * (a - b)) % 11 == 0:
                        isbn_tr_missed += 1
check("F2c ISBN-10 SUB census 0 (10x110 checks)", isbn_sub_missed == 0 and isbn_sub_checks == 10 * 110)
check("F2c ISBN-10 transposition census 0 every distance (45x110 checks)",
      isbn_tr_missed == 0 and isbn_tr_checks == 45 * 110)
cover("isbn10 censuses (sub, transpositions)",
      [ANCH["isbn10_sub_undetected"], ANCH["isbn10_transposition_undetected_every_distance"]],
      [isbn_sub_missed, isbn_tr_missed])

EAN_W = FIX["schemes"]["EAN13"]["weights"]
check("F1 EAN-13 weights alternate 1,3 over 13 positions",
      EAN_W == [1 if i % 2 == 0 else 3 for i in range(13)])
ean_sub = [sum(1 for a in range(10) for b in range(10) if a != b and (w * (a - b)) % 10 == 0)
           for w in EAN_W]
check("F2c EAN-13 SUB census 0 per position", all(x == 0 for x in ean_sub))
ean_adj = [sum(1 for a in range(10) for b in range(10)
               if a != b and ((EAN_W[i] - EAN_W[i + 1]) * (a - b)) % 10 == 0)
           for i in range(12)]
ean_d2 = [sum(1 for a in range(10) for b in range(10)
              if a != b and ((EAN_W[i] - EAN_W[i + 2]) * (a - b)) % 10 == 0)
          for i in range(11)]
check("F2c EAN-13 adjacent census 10/90 per boundary", ean_adj == [10] * 12)
check("F2c EAN-13 distance-2 census 90/90 per pair", ean_d2 == [90] * 11)
EAN_ADJ_PATTERNS = sum(ean_adj)
EAN_D2_PATTERNS = sum(ean_d2)
check("F2c EAN-13 full-code patterns 120 + 990",
      EAN_ADJ_PATTERNS == 120 and EAN_D2_PATTERNS == 990)
cover("ean13 censuses {adj/boundary, d2/pair, 120, 990}",
      [ANCH["ean13_adjacent_per_boundary"], ANCH["ean13_d2_per_pair"],
       ANCH["ean13_full_code_adjacent_patterns"], ANCH["ean13_full_code_d2_patterns"]],
      [ean_adj[0], ean_d2[0], EAN_ADJ_PATTERNS, EAN_D2_PATTERNS])

# ALL-ONES control
allones_sub = sum(1 for a in range(10) for b in range(10) if a != b and (1 * (a - b)) % 10 == 0)
allones_tr = sum(1 for a in range(10) for b in range(10) if a != b and ((1 - 1) * (a - b)) % 10 == 0)
check("F5 ALL-ONES catches every SUB", allones_sub == 0)
check("F5 ALL-ONES misses every transposition at every distance", allones_tr == 90)
cover("all-ones (sub, transposition/boundary)",
      [ANCH["all_ones_sub"], ANCH["all_ones_transposition_per_boundary_every_distance"]],
      [allones_sub, allones_tr])

# DAMM property gates + state censuses
check("F2c damm rows are permutations", all(sorted(r) == list(range(10)) for r in DAMM))
check("F2c damm columns are permutations",
      all(sorted(DAMM[r][c] for r in range(10)) == list(range(10)) for c in range(10)))
check("F2c damm zero diagonal", all(DAMM[d][d] == 0 for d in range(10)))
damm_sub = sum(1 for c in range(10) for a in range(10) for b in range(10)
               if a != b and DAMM[c][a] == DAMM[c][b])
damm_adj = sum(1 for c in range(10) for a in range(10) for b in range(10)
               if a != b and DAMM[DAMM[c][a]][b] == DAMM[DAMM[c][b]][a])
damm_d2 = sum(1 for c in range(10) for a in range(10) for b in range(10) for m in range(10)
              if a != b and DAMM[DAMM[DAMM[c][a]][m]][b] == DAMM[DAMM[DAMM[c][b]][m]][a])
check("F2c damm SUB state census 0/900", damm_sub == 0)
check("F2c damm ADJ state census 0/900", damm_adj == 0)
cover("damm state censuses {sub 0/900, adj 0/900, d2 958/9000 (reporting)}",
      [ANCH["damm_sub_state_census"][0], ANCH["damm_adj_state_census"][0],
       ANCH["damm_d2_state_census_reporting"][0]],
      [damm_sub, damm_adj, damm_d2])

# ---- F4: pencil worlds -------------------------------------------------------
pw_a = sum(1 for a in range(10) for b in range(10) if a != b and (a + b) % 10 == (b + a) % 10)
check("F4a weights (1,1): swap never changes the sum — 90/90", pw_a == 90)
check("F4b Luhn famous miss: 09 and 90 both digest 9 (left digit doubled)",
      (LUHN[0] + 9) % 10 == 9 and (LUHN[9] + 0) % 10 == 9)
check("F4c certificate three lines", sum(range(10)) == 45 and 45 % 10 == 5 and 0 != 5)

# ---- F5: degeneracy controls -------------------------------------------------
w0_sub = sum(1 for a in range(10) for b in range(10) if a != b and (0 * (a - b)) % 10 == 0)
check("F5 weight-0 position misses all 90 SUB", w0_sub == 90)
check("F5 identity quotient U = 90", U_of_perm(list(range(10))) == 90)
cover("degeneracy {weight-0 sub, identity-quotient U}",
      [FIX["degeneracy_f5"]["weight_zero_sub_missed"], FIX["degeneracy_f5"]["identity_quotient_U"]],
      [w0_sub, U_of_perm(list(range(10)))])

# ====================================================== Arm B (twin, indep.)
# Independently-written validators (no shared code with Arm A's algebra).


def luhn_valid_B(w):
    """Length-4 Luhn word, fold at 0-based positions 0 and 2 (fixture pin).
    Doubling written arithmetically, NOT via Arm A's fold list."""
    s = 0
    for i, d in enumerate(w):
        if i in (0, 2):
            dd = d * 2
            if dd > 9:
                dd -= 9
            s += dd
        else:
            s += d
    return s % 10 == 0


def ean_valid_B(w):
    return (w[0] * 1 + w[1] * 3 + w[2] * 1 + w[3] * 3) % 10 == 0


def mini11_valid_B(w):
    return (4 * w[0] + 3 * w[1] + 2 * w[2] + 1 * w[3]) % 11 == 0


def damm_valid_B(w):
    c = 0
    for d in w:
        c = DAMM[c][d]
    return c == 0


def word_census_B(valid_fn, symbols, d2_pairs=()):
    words = [w for w in product(range(symbols), repeat=4) if valid_fn(w)]
    sub = 0
    for w in words:
        for i in range(4):
            for x in range(symbols):
                if x != w[i]:
                    m = list(w)
                    m[i] = x
                    if valid_fn(tuple(m)):
                        sub += 1
    adj = 0
    for w in words:
        for i in range(3):
            if w[i] != w[i + 1]:
                m = list(w)
                m[i], m[i + 1] = m[i + 1], m[i]
                if valid_fn(tuple(m)):
                    adj += 1
    d2 = 0
    for w in words:
        for (i, j) in d2_pairs:
            if w[i] != w[j]:
                m = list(w)
                m[i], m[j] = m[j], m[i]
                if valid_fn(tuple(m)):
                    d2 += 1
    return {"valid": len(words), "sub": sub, "adj": adj, "d2": d2, "words": words}


B_LUHN = word_census_B(luhn_valid_B, 10)
B_EAN = word_census_B(ean_valid_B, 10, d2_pairs=((0, 2), (1, 3)))
B_MINI = word_census_B(mini11_valid_B, 11)
B_DAMM = word_census_B(damm_valid_B, 10)

check("F1 valid-word counts 1000/1000/1331/1000",
      (B_LUHN["valid"], B_EAN["valid"], B_MINI["valid"], B_DAMM["valid"]) == (1000, 1000, 1331, 1000))
check("F6 word-SUB = 0 across all four",
      B_LUHN["sub"] == B_EAN["sub"] == B_MINI["sub"] == B_DAMM["sub"] == 0)
cover("word_LUHN {valid,sub,adj}", [ANCH["word_LUHN"]["valid"], ANCH["word_LUHN"]["sub"], ANCH["word_LUHN"]["adj"]],
      [B_LUHN["valid"], B_LUHN["sub"], B_LUHN["adj"]])
cover("word_EAN {valid,sub,adj,d2}",
      [ANCH["word_EAN"]["valid"], ANCH["word_EAN"]["sub"], ANCH["word_EAN"]["adj"], ANCH["word_EAN"]["d2"]],
      [B_EAN["valid"], B_EAN["sub"], B_EAN["adj"], B_EAN["d2"]])
cover("word_MINI11 {valid,sub,adj}",
      [ANCH["word_MINI11"]["valid"], ANCH["word_MINI11"]["sub"], ANCH["word_MINI11"]["adj"]],
      [B_MINI["valid"], B_MINI["sub"], B_MINI["adj"]])
cover("word_DAMM {valid,sub,adj}",
      [ANCH["word_DAMM"]["valid"], ANCH["word_DAMM"]["sub"], ANCH["word_DAMM"]["adj"]],
      [B_DAMM["valid"], B_DAMM["sub"], B_DAMM["adj"]])

# multiplicity law, asserted directly (each ORDERED pair at a boundary sits in
# exactly 10 valid words) for the three mod-10 word schemes
for label, words in (("LUHN", B_LUHN["words"]), ("EAN", B_EAN["words"]), ("DAMM", B_DAMM["words"])):
    ok = True
    for i in range(3):
        for a in range(10):
            for b in range(10):
                n = sum(1 for w in words if w[i] == a and w[i + 1] == b)
                if n != 10:
                    ok = False
    check("F6 multiplicity law (10 valid words per ordered pair per boundary) %s" % label, ok)

# the FOUR typed must-equal contacts
TC = FIX["typed_contacts"]
check("F6 contact word-LUHN-ADJ 60 = 3*2*10", B_LUHN["adj"] == 60 == 3 * LUHN_U * 10 == TC["word_luhn_adj"]["value"])
check("F6 contact word-EAN-ADJ 300 = 3*10*10", B_EAN["adj"] == 300 == 3 * ean_adj[0] * 10 == TC["word_ean_adj"]["value"])
check("F6 contact word-EAN-D2 1800 = 2*90*10", B_EAN["d2"] == 1800 == 2 * ean_d2[0] * 10 == TC["word_ean_d2"]["value"])
check("F6 contact word-MINI11-ADJ 0 = 0", B_MINI["adj"] == 0 == TC["word_mini11_adj"]["value"])
check("F6 drafting-correction axis NOT reproduced (ordered counts, not 30/150/900)",
      (B_LUHN["adj"], B_EAN["adj"], B_EAN["d2"]) != (30, 150, 900))

# Arm B's own reduced quotient census: pi(0)=0 slice, pairwise-comparison U
def reduced_census_B():
    hist = {}
    for rest in permutations(range(1, 10)):
        p = (0,) + rest
        tau = [(p[y] - y) % 10 for y in range(10)]
        u = 0
        for a in range(10):
            ta = tau[a]
            for b in range(10):
                if a != b and ta == tau[b]:
                    u += 1
        hist[u] = hist.get(u, 0) + 1
    return hist


HIST_B = reduced_census_B()
check("F6 twin census: reduced slice totals 9!", sum(HIST_B.values()) == 362880)
check("F6 twin census: full = 10 x reduced on every bin",
      set(HIST_A) == set(HIST_B) and all(HIST_A[u] == 10 * HIST_B[u] for u in HIST_B))

# Arm B's own boundary scan for Luhn (digit-level, both orientations)
def luhn_boundary_miss_B(left_doubled):
    miss = set()
    for a in range(10):
        for b in range(10):
            if a == b:
                continue
            if left_doubled:
                if (LUHN[a] + b) % 10 == (LUHN[b] + a) % 10:
                    miss.add((a, b))
            else:
                if (a + LUHN[b]) % 10 == (b + LUHN[a]) % 10:
                    miss.add((a, b))
    return sorted(miss)


check("F6 twin Luhn boundary scan both orientations = {(0,9),(9,0)}",
      luhn_boundary_miss_B(True) == luhn_boundary_miss_B(False) == [(0, 9), (9, 0)])

# ================================================= decision evaluators (twin)


def evaluate_A():
    r1 = (MIN_U == 2 and 0 not in HIST_A and sum(range(10)) % 10 == 5
          and LUHN_U == 2 and LUHN_MISS == [(0, 9), (9, 0)] and LINEAR_FLOOR == 10)
    r2 = (isbn_sub_missed == 0 and isbn_tr_missed == 0
          and ean_adj == [10] * 12 and ean_d2 == [90] * 11
          and EAN_ADJ_PATTERNS == 120 and EAN_D2_PATTERNS == 990)
    r3 = (damm_sub == 0 and damm_adj == 0
          and all(sorted(r) == list(range(10)) for r in DAMM)
          and all(sorted(DAMM[r][c] for r in range(10)) == list(range(10)) for c in range(10))
          and all(DAMM[d][d] == 0 for d in range(10))
          and B_MINI["valid"] == 1331 and B_MINI["sub"] == 0 and B_MINI["adj"] == 0)
    if r1 and r2 and r3:
        return "REJECT"
    if CHECKS["failed"] > 0:
        return "INVALID"
    if MIN_U == 0 or (sum(ean_adj) == 0 and sum(ean_d2) == 0):
        return "APPROVE"
    return "NULL"


def evaluate_B():
    """Second evaluator, independently written over Arm-B-side quantities."""
    floor_ok = (min(HIST_B) == 2 and 0 not in HIST_B
                and sum(k * 0 + v for k, v in HIST_B.items()) == 362880)
    luhn_ok = (luhn_boundary_miss_B(True) == [(0, 9), (9, 0)]
               and B_LUHN["adj"] == 3 * 2 * 10)
    lin_ok = min(GRID[c] for c in ALL_SINGLES) == 10
    reject_1 = floor_ok and luhn_ok and lin_ok
    reject_2 = (isbn_sub_missed + isbn_tr_missed == 0
                and B_EAN["adj"] == 3 * 10 * 10 and B_EAN["d2"] == 2 * 90 * 10
                and 12 * (B_EAN["adj"] // 30) == 120 and 11 * (B_EAN["d2"] // 20) == 990)
    reject_3 = (B_DAMM["valid"] == 1000 and B_DAMM["sub"] == 0 and B_DAMM["adj"] == 0
                and B_MINI["valid"] == 1331 and B_MINI["sub"] == 0 and B_MINI["adj"] == 0
                and damm_sub == 0 and damm_adj == 0)
    if reject_1 and reject_2 and reject_3:
        return "REJECT"
    if CHECKS["failed"] > 0:
        return "INVALID"
    if 0 in HIST_B or (B_EAN["adj"] == 0 and B_EAN["d2"] == 0):
        return "APPROVE"
    return "NULL"


# ================================================= Arm R (reporting-only)
class CountingRng:
    def __init__(self, seed):
        self._r = make_rng(seed)
        self.draws = 0

    def randrange(self, n):
        self.draws += 1
        return self._r.randrange(n)


def luhn16_check(free15):
    """16-digit Luhn: positions 0..15 left-to-right, check at 15; doubling on
    even 0-based indices (every second from the right, check undoubled)."""
    s = 0
    for i, d in enumerate(free15):
        s += LUHN[d] if i % 2 == 0 else d
    return (10 - s % 10) % 10


def luhn16_valid(code):
    s = 0
    for i, d in enumerate(code):
        s += LUHN[d] if i % 2 == 0 else d
    return s % 10 == 0


def ean13_check(free12):
    s = sum(d * EAN_W[i] for i, d in enumerate(free12))
    return (10 - s % 10) % 10  # check weight 1


def ean13_valid(code):
    return sum(d * EAN_W[i] for i, d in enumerate(code)) % 10 == 0


def arm_r_leg(seed, n_episodes):
    rng = CountingRng(seed)
    res = {"luhn_adj": [0, 0], "ean_adj": [0, 0], "ean_d2": [0, 0]}
    for _ in range(n_episodes):
        free15 = [rng.randrange(10) for _ in range(15)]
        luhn_code = free15 + [luhn16_check(free15)]
        lb = rng.randrange(15)
        free12 = [rng.randrange(10) for _ in range(12)]
        ean_code = free12 + [ean13_check(free12)]
        eb = rng.randrange(12)
        ed = rng.randrange(11)
        if luhn_code[lb] != luhn_code[lb + 1]:
            res["luhn_adj"][1] += 1
            m = list(luhn_code)
            m[lb], m[lb + 1] = m[lb + 1], m[lb]
            if luhn16_valid(m):
                res["luhn_adj"][0] += 1
        if ean_code[eb] != ean_code[eb + 1]:
            res["ean_adj"][1] += 1
            m = list(ean_code)
            m[eb], m[eb + 1] = m[eb + 1], m[eb]
            if ean13_valid(m):
                res["ean_adj"][0] += 1
        if ean_code[ed] != ean_code[ed + 2]:
            res["ean_d2"][1] += 1
            m = list(ean_code)
            m[ed], m[ed + 2] = m[ed + 2], m[ed]
            if ean13_valid(m):
                res["ean_d2"][0] += 1
    return res, rng.draws


AR = FIX["arm_r"]
R_MAIN, DRAWS_MAIN = arm_r_leg(AR["seeds"]["main"], AR["n_main"])
R_MAIN2, DRAWS_MAIN2 = arm_r_leg(AR["seeds"]["main"], AR["n_main"])
R_STAB, DRAWS_STAB = arm_r_leg(AR["seeds"]["stability"], AR["n_stability"])
R_STAB2, _ = arm_r_leg(AR["seeds"]["stability"], AR["n_stability"])

check("F6 Arm-R draw-count sentinel: exactly 600000 draws at N=20000",
      DRAWS_MAIN == AR["draw_count_sentinel_main"] == 600000 == AR["n_main"] * AR["draws_per_episode"])
check("F6 Arm-R exact reproducibility (main + stability legs)",
      R_MAIN == R_MAIN2 and DRAWS_MAIN == DRAWS_MAIN2 and R_STAB == R_STAB2)
prev = AR["disclosed_preview_seed_20261680"]
cover("arm-R preview luhn_adj (reporting-only; stream-order-dependent)",
      prev["luhn_adj"], R_MAIN["luhn_adj"])
cover("arm-R preview ean_adj (reporting-only; stream-order-dependent)",
      prev["ean_adj"], R_MAIN["ean_adj"])
cover("arm-R preview ean_d2 (reporting-only; stream-order-dependent)",
      prev["ean_d2"], R_MAIN["ean_d2"])
cover("arm-R draw count", prev["draws"], DRAWS_MAIN)
check("F6 Arm-R EAN-D2 undetected rate = 1.0 (saturated cell, both legs)",
      R_MAIN["ean_d2"][0] == R_MAIN["ean_d2"][1] and R_STAB["ean_d2"][0] == R_STAB["ean_d2"][1])
vacancy("arm-R per-episode draw order", "sim-chosen (registration pins seeds/N/600,000-sentinel only); disclosed in fixtures.json")
vacancy("arm-R stability-leg values", "no disclosed stability numbers in the registration — printed as themselves")

# presentation leg (presentation seed ONLY)
pres_rng = make_rng(AR["seeds"]["presentation"])
pres_pairs = list(ESCAPE_13)
pres_rng.shuffle(pres_pairs)

check("F6 seed registry: exactly main/stability(x2 each)/presentation read; aux never read",
      sorted(set(SEEDS_READ)) == [20261680, 20261681, 20261682]
      and 20261683 not in SEEDS_READ)

# ================================================= margin ledger (typed)
MARGIN = {
    "luhn_on_floor": {"law": "Luhn U == global min U (ON the floor, x1.00 by construction)",
                      "holds": LUHN_U == MIN_U == 2},
    "ean_d2_saturated": {"law": "EAN D2 census == 90 == maximum possible (saturated cell)",
                         "holds": ean_d2[0] == 90 and all(x == 90 for x in ean_d2)},
    "damm_adj_zero": {"law": "Damm ADJ census == 0 == minimum possible (zero cell)",
                      "holds": damm_adj == 0},
}
for k, v in MARGIN.items():
    check("margin ledger cell %s" % k, v["holds"])

# ================================================= ruling
RULING_A = evaluate_A()
RULING_B = evaluate_B()
check("F6 twin evaluators agree on the ruling token", RULING_A == RULING_B)
RULING = RULING_A if RULING_A == RULING_B else "INVALID"
if CHECKS["failed"] > 0 and RULING == "REJECT":
    # the registered order puts REJECT first, but a red battery is reported
    RULING = "INVALID"

# ================================================= coverage census summary
n_matched = sum(1 for r in COVERAGE if r["status"] == "matched")
n_mismatched = sum(1 for r in COVERAGE if r["status"] == "MISMATCHED")
n_vacant = sum(1 for r in COVERAGE if r["status"] == "vacant")

# ================================================= results.json + stdout
results = {
    "verdict": RULING,
    "evaluators": {"A": RULING_A, "B": RULING_B},
    "decision_order": FIX["decision_rule"]["order"],
    "histogram_full_10fact": {str(k): HIST_A[k] for k in sorted(HIST_A)},
    "histogram_reduced_9fact_B": {str(k): HIST_B[k] for k in sorted(HIST_B)},
    "floor": {"min_U": MIN_U, "minimizer_count": HIST_A[MIN_U], "max_U": MAX_U,
              "maximizer_count": HIST_A[MAX_U], "maximizers_are_rotations": sorted(MAX_PERMS) == ROTATIONS,
              "total": TOTAL_A, "zero_bin": 0 in HIST_A},
    "certificate": {"perm_sum": 45, "perm_sum_mod10": 5, "tau_sum_mod10": 0, "injective_tau_impossible": True},
    "luhn": {"boundary_census": LUHN_U, "miss_set_ordered": LUHN_MISS, "tau": LUHN_TAU},
    "linear_grid": {"all_singles_cells": ALL_SINGLES, "diagonal_miss": 90, "off_diagonal_miss": 10,
                    "floor": LINEAR_FLOOR, "escape_set_at_1_3": ESCAPE_13},
    "isbn10": {"sub_undetected": isbn_sub_missed, "sub_checks": isbn_sub_checks,
               "transposition_undetected": isbn_tr_missed, "transposition_checks": isbn_tr_checks},
    "ean13": {"sub_per_position": ean_sub, "adj_per_boundary": ean_adj, "d2_per_pair": ean_d2,
              "full_code_adjacent_patterns": EAN_ADJ_PATTERNS, "full_code_d2_patterns": EAN_D2_PATTERNS},
    "all_ones": {"sub": allones_sub, "transposition_per_boundary": allones_tr},
    "damm": {"sub_state_census": [damm_sub, 900], "adj_state_census": [damm_adj, 900],
             "d2_state_census_reporting": [damm_d2, 9000]},
    "word_level_B": {
        "LUHN": {k: B_LUHN[k] for k in ("valid", "sub", "adj")},
        "EAN": {k: B_EAN[k] for k in ("valid", "sub", "adj", "d2")},
        "MINI11": {k: B_MINI[k] for k in ("valid", "sub", "adj")},
        "DAMM": {k: B_DAMM[k] for k in ("valid", "sub", "adj")},
    },
    "typed_contacts": {"word_luhn_adj": [B_LUHN["adj"], "3*2*10"],
                       "word_ean_adj": [B_EAN["adj"], "3*10*10"],
                       "word_ean_d2": [B_EAN["d2"], "2*90*10"],
                       "word_mini11_adj": [B_MINI["adj"], "0"],
                       "multiplicity_law_asserted": True,
                       "drafting_correction_unordered_counts_not_reproduced": True},
    "margin_ledger": {k: v["holds"] for k, v in MARGIN.items()},
    "arm_r": {"main": {"seed": AR["seeds"]["main"], "n": AR["n_main"], "draws": DRAWS_MAIN, **R_MAIN},
              "stability": {"seed": AR["seeds"]["stability"], "n": AR["n_stability"], "draws": DRAWS_STAB, **R_STAB},
              "exact_rates": {"luhn_adj": "2/90", "ean_adj": "10/90", "ean_d2": "90/90"},
              "presentation_seed": AR["seeds"]["presentation"],
              "aux_seed_never_read": AR["seeds"]["aux_never_read"] not in SEEDS_READ},
    "anomaly_census": {"rows": COVERAGE, "matched": n_matched, "mismatched": n_mismatched, "vacant": n_vacant},
    "anomalies": ANOMALIES,
    "self_checks": dict(CHECKS),
    "failures": FAILURES,
    "seeds_read_registry": sorted(set(SEEDS_READ)),
    "cpython": "3.11",
}
(HERE / "results.json").write_text(
    json.dumps(results, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def rate(pair):
    return "%d/%d ~ %.6g" % (pair[0], pair[1], pair[0] / pair[1] if pair[1] else float("nan"))


print("VERDICT 089 runner — the check-digit transposition floor (P076)")
print("ruling: %s (evaluators %s/%s)" % (RULING, RULING_A, RULING_B))
print("R1 floor: full 10! census total %d, min U = %d at %d quotients, max %d at %d (rotations: %s), no U=0 bin: %s"
      % (TOTAL_A, MIN_U, HIST_A[MIN_U], MAX_U, HIST_A[MAX_U], sorted(MAX_PERMS) == ROTATIONS, 0 not in HIST_A))
print("  certificate: sum(perm)=45, 45 mod 10 = 5 != 0 = sum(tau) mod 10 — injective tau impossible (symbolic + exhaustive)")
print("  histogram support: %s" % sorted(HIST_A))
print("  Luhn: census %d, miss set %s (ON the floor, x1.00 by construction); linear floor %d (5x)"
      % (LUHN_U, LUHN_MISS, LINEAR_FLOOR))
print("R2 regression: ISBN-10 SUB %d/1100, transpositions %d/4950 (every distance); EAN-13 adj %d/90 per boundary, d2 %d/90 per pair; full-code patterns %d + %d"
      % (isbn_sub_missed, isbn_tr_missed, ean_adj[0], ean_d2[0], EAN_ADJ_PATTERNS, EAN_D2_PATTERNS))
print("R3 exits: Damm gates rows/cols/diag PASS, SUB %d/900, ADJ %d/900 (D2 honesty row %d/9000, reporting); 11-ary word-level %d/%d/%d"
      % (damm_sub, damm_adj, damm_d2, B_MINI["valid"], B_MINI["sub"], B_MINI["adj"]))
print("word-level (Arm B): LUHN %d/%d/%d · EAN %d/%d/%d/%d · DAMM %d/%d/%d; contacts 60=3*2*10, 300=3*10*10, 1800=2*90*10, 0=0 (multiplicity law asserted)"
      % (B_LUHN["valid"], B_LUHN["sub"], B_LUHN["adj"],
         B_EAN["valid"], B_EAN["sub"], B_EAN["adj"], B_EAN["d2"],
         B_DAMM["valid"], B_DAMM["sub"], B_DAMM["adj"]))
print("twin census: reduced 9! slice x10 == full census on every bin: True")
print("EAN escape pairs (presentation shuffle, seed %d): %s" % (AR["seeds"]["presentation"], pres_pairs))
print("arm R (reporting-only): main seed %d N=%d draws=%d | luhn_adj %s (exact 2/90) | ean_adj %s (exact 10/90) | ean_d2 %s (exact 90/90)"
      % (AR["seeds"]["main"], AR["n_main"], DRAWS_MAIN,
         rate(R_MAIN["luhn_adj"]), rate(R_MAIN["ean_adj"]), rate(R_MAIN["ean_d2"])))
print("  stability seed %d N=%d draws=%d | luhn_adj %s | ean_adj %s | ean_d2 %s"
      % (AR["seeds"]["stability"], AR["n_stability"], DRAWS_STAB,
         rate(R_STAB["luhn_adj"]), rate(R_STAB["ean_adj"]), rate(R_STAB["ean_d2"])))
print("margin ledger: %s" % {k: v["holds"] for k, v in MARGIN.items()})
print("anomaly census (disclosure coverage): %d compared-and-matched, %d mismatched, %d vacant"
      % (n_matched, n_mismatched, n_vacant))
if ANOMALIES:
    print("anomalies: %s" % " | ".join(ANOMALIES))
else:
    print("anomalies: none")
print("self-checks: %d passed, %d failed%s"
      % (CHECKS["passed"], CHECKS["failed"], (" — " + ", ".join(FAILURES)) if FAILURES else ""))
sys.exit(0 if CHECKS["failed"] == 0 else 1)
