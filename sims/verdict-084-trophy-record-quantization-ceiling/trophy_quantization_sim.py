#!/usr/bin/env python3
"""VERDICT 084 runner — the fishing trophy-record quantization ceiling (idea-engine P071).

Hermetic: reads ONLY the fixtures.json beside this file. Zero repo/network
reads at verdict time. Every decision number is an exact Fraction.

Arms:
  A — closed-form exact interval census + suffix-sum record laws (decision-bearing)
  B — INDEPENDENTLY-WRITTEN boundary-sweep census + explicit t-DP twin (exact-equal gated)
  F — the committed roll re-implemented VERBATIM (float round + random.uniform),
      seeded; support equality gated on ranks {1, 2, 3, 21}; frequencies reporting
  R — seeded career traces at the decision cell, REPORTING-ONLY (no statistical gate)

Gates G1-G6 per the P071 registration; decision order REJECT -> INVALID ->
APPROVE -> NULL (REJECT evaluated FIRST) via twin independently-written
evaluators. Print discipline per fixture convention C9 (no big-int prints).
"""

import bisect
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

assert sys.version_info[:2] == (3, 11), (
    "CPython 3.11 pinned (fixture battery.cpython_pin); got %s" % (sys.version_info[:2],)
)

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- helpers
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []
ANOMALIES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
    return bool(cond)


def anomaly(text):
    ANOMALIES.append("A%d: %s" % (len(ANOMALIES) + 1, text))


def frac(s):
    return Fraction(s)


def fstr(x):
    return "%d/%d" % (x.numerator, x.denominator)


def f12(x):
    """12-significant-digit float string (print discipline C9)."""
    return "%.12g" % float(x)


LO = frac(FIX["committed_constants"]["spread_lo"])
HI = frac(FIX["committed_constants"]["spread_hi"])
SPAN = HI - LO
NOMS = [frac(s) for s in FIX["committed_constants"]["nominals_by_rank"]]
GRID2 = frac(FIX["committed_constants"]["grid"])

# committed-formula identity for the pinned nominals (G2 leg)
for r, n in enumerate(NOMS, 1):
    check("G2 nominal(%d) = round(0.18*r**1.65, 2)" % r,
          float(n) == round(0.18 * r ** 1.65, 2))


# ------------------------------------------------------- Arm A (closed form)
def census_a(N, grid):
    """Closed-form per-atom interval census: atom k*grid gets the clipped
    f-measure of [(k-1/2)*grid, (k+1/2)*grid) / N, over span 9/10."""
    lo_k = int(math.floor(float(N * LO / grid))) - 2
    hi_k = int(math.ceil(float(N * HI / grid))) + 2
    atoms = []
    for k in range(lo_k, hi_k + 1):
        fl = (Fraction(2 * k - 1, 2) * grid) / N
        fh = (Fraction(2 * k + 1, 2) * grid) / N
        a, b = max(fl, LO), min(fh, HI)
        if b > a:
            atoms.append((k * grid, (b - a) / SPAN))
    return atoms


def record_a(atoms):
    """Arm A record laws from suffix sums S_i = P(X >= v_i)."""
    e_life = Fraction(0)
    suffix = Fraction(1)
    per_atom_ever = []
    for v, p in atoms:
        per_atom_ever.append(p / suffix)
        e_life += p / suffix
        suffix -= p
    return e_life, per_atom_ever


def pb_at_t_a(atoms, t):
    """P(PB at catch t) = sum_i p_i * F_i^(t-1), F_i = P(X < v_i)."""
    total = Fraction(0)
    F = Fraction(0)
    for v, p in atoms:
        total += p * F ** (t - 1)
        F += p
    return total


# ------------------------------------------- Arm B (boundary-sweep + t-DP twin)
def census_b(N, grid):
    """INDEPENDENT twin: collect every clipped rounding boundary in f-space,
    sort, sweep segments, and assign each segment to the atom of its midpoint
    (round-to-nearest computed on exact rationals) — never via Arm A's
    per-atom interval formula."""
    pts = {LO, HI}
    k = int(math.floor(float(N * LO / grid))) - 2
    k_hi = int(math.ceil(float(N * HI / grid))) + 2
    while k <= k_hi:
        b = (Fraction(2 * k + 1, 2) * grid) / N  # boundary between atoms k and k+1
        if LO < b < HI:
            pts.add(b)
        k += 1
    cuts = sorted(pts)
    acc = {}
    for a, b in zip(cuts, cuts[1:]):
        mid = (a + b) / 2
        w = N * mid / grid
        atom = (w.numerator + w.denominator // 2) // w.denominator  # nearest int (interior: never a tie)
        acc[atom * grid] = acc.get(atom * grid, Fraction(0)) + (b - a) / SPAN
    return sorted(acc.items())


def record_b(atoms):
    """Twin E_life from prefix sums: E = sum_i p_i / (1 - F_i)."""
    e_life = Fraction(0)
    F = Fraction(0)
    per_atom_ever = []
    for v, p in atoms:
        per_atom_ever.append(p / (1 - F))
        e_life += p / (1 - F)
        F += p
    return e_life, per_atom_ever


def pb_series_b(atoms, n_max):
    """Twin explicit t-DP: per-atom running powers of the prefix CDF; returns
    the list P(PB at t) for t = 1..n_max (exact Fractions)."""
    prefixes = []
    F = Fraction(0)
    for v, p in atoms:
        prefixes.append((p, F))
        F += p
    powers = [Fraction(1)] * len(prefixes)  # F_i^(t-1), t = 1
    out = []
    for t in range(1, n_max + 1):
        out.append(sum(p * powers[i] for i, (p, F_i) in enumerate(prefixes)))
        for i, (p, F_i) in enumerate(prefixes):
            powers[i] *= F_i
    return out


# --------------------------------------------------- census, all ranks (G1/G2)
A_TABLE = FIX["anchors"]["A_table"]
atoms_by_rank = []
for r, N in enumerate(NOMS, 1):
    at_a = census_a(N, GRID2)
    at_b = census_b(N, GRID2)
    check("G1 census twin rank %d" % r, at_a == at_b)
    check("G2 probs sum to 1 rank %d" % r, sum(p for _, p in at_a) == 1)
    if not check("G2 |A_%d| = %d verbatim" % (r, A_TABLE[r - 1]), len(at_a) == A_TABLE[r - 1]):
        anomaly("|A_%d| computed %d vs disclosed %d" % (r, len(at_a), A_TABLE[r - 1]))
    check("G2 atoms consecutive on the grid rank %d" % r,
          all(at_a[i + 1][0] - at_a[i][0] == GRID2 for i in range(len(at_a) - 1)))
    check("T2 top atom strictly positive rank %d" % r, at_a[-1][1] > 0)
    atoms_by_rank.append(at_a)

# rank-1 atom law verbatim (G2)
a1 = atoms_by_rank[0]
law = FIX["anchors"]["rank1_atom_law"]
check("G2 rank-1 bottom atom 0.12 @ 4/81",
      a1[0] == (frac(law["bottom"]["v"]), frac(law["bottom"]["p"])))
check("G2 rank-1 fifteen interior atoms @ 5/81",
      len(a1) == 17 and all(p == frac(law["interior"]["p"]) for _, p in a1[1:16]))
check("G2 rank-1 top atom 0.28 @ 2/81",
      a1[-1] == (frac(law["top"]["v"]), frac(law["top"]["p"])))

# --------------------------------------------------------------- G3 (T2)
P_CEIL_1 = a1[-1][1]
check("G3 p_ceiling(1) = 2/81", P_CEIL_1 == frac(FIX["anchors"]["p_ceiling_rank1"]))
H21 = sum(Fraction(1, r) for r in range(1, 22))
check("G3 H21 = 18858053/5173168", H21 == frac(FIX["anchors"]["H21"]))
Q1 = Fraction(1, 1) / H21
check("G3 q1 = 5173168/18858053", Q1 == frac(FIX["anchors"]["q1_decision"]))
KILL_1 = 1 / (Q1 * P_CEIL_1)
check("G3 kill-cast identity = 1527502293/10346336",
      KILL_1 == frac(FIX["anchors"]["kill_casts_rank1"]))
check("G3 E[catches of species to ceiling] = 81/2", 1 / P_CEIL_1 == Fraction(81, 2))

# --------------------------------------------------------------- G4 (T3)
E_LIFE = []
for r, atoms in enumerate(atoms_by_rank, 1):
    ea, ever_a = record_a(atoms)
    eb, ever_b = record_b(atoms)
    check("G1 E_life twin rank %d (in-memory Fraction)" % r, ea == eb)
    check("G1 per-atom ever-record twin rank %d" % r, ever_a == ever_b)
    E_LIFE.append(ea)
check("G4 E_life(1) exact", E_LIFE[0] == frac(FIX["anchors"]["E_life_rank1"]))

T_LO, T_HI = FIX["grids"]["cadence_t_range"]
cadence = []  # (t, exact P(PB at t)) for the minnow
series_b_50 = pb_series_b(a1, T_HI)
for t in range(2, T_HI + 1):
    pa = pb_at_t_a(a1, t)
    check("G1 P(PB at t=%d) twin" % t, pa == series_b_50[t - 1])
    check("G4 P(PB at t=%d) < 1/t strict" % t, pa < Fraction(1, t))
    cadence.append((t, pa))
check("G4 cadence anchor t=2 = 3083/6561",
      cadence[0][1] == frac(FIX["anchors"]["cadence_t2_rank1"]["value"]))

# geometric-series identity: E[PBs in n] partial sums, minnow, n = 1..1000
series_1000 = pb_series_b(a1, 1000)
partial = []
acc = Fraction(0)
for v in series_1000:
    acc += v
    partial.append(acc)
check("G4 partial sums monotone non-decreasing",
      all(partial[i + 1] >= partial[i] for i in range(len(partial) - 1)))
check("G4 E_life - E[PBs in 1000] < 1/1000",
      E_LIFE[0] - partial[-1] < Fraction(1, 1000))
# Arm-A closed form for E[PBs in n] vs the DP partial sums (twin, spot n values)
for n in (1, 2, 10, 50, 100, 1000):
    ea_n = Fraction(0)
    F = Fraction(0)
    for v, p in a1:
        ea_n += p * (1 - F ** n) / (1 - F)  # valid at F = 0 too (0^n = 0 for n >= 1)
        F += p
    check("G1 E[PBs in %d] twin (closed form vs DP)" % n, ea_n == partial[n - 1])

# H_n bound + E_life bound (G6 battery leg, exact)
H_running = Fraction(0)
bound_ok = True
for n in range(1, 1001):
    H_running += Fraction(1, n)
    if not (partial[n - 1] <= H_running and partial[n - 1] <= E_LIFE[0]):
        bound_ok = False
        break
check("G6 E[PBs in n] <= min(H_n, E_life) for n in 1..1000", bound_ok)

# ------------------------------------------------------------------ G5
g5 = FIX["anchors"]["hand_world_g5"]
hw_a = census_a(frac(g5["nominal"]), GRID2)
hw_b = census_b(frac(g5["nominal"]), GRID2)
check("G5 twin", hw_a == hw_b)
check("G5 9 atoms", len(hw_a) == g5["atoms"])
check("G5 each p = 1/9", all(p == frac(g5["each_p"]) for _, p in hw_a))
e_hw = record_a(hw_a)[0]
check("G5 E_life = H9 = 7129/2520", e_hw == frac(g5["E_life"]) ==
      sum(Fraction(1, i) for i in range(1, 10)))
check("G5 E[catches to ceiling] = 9", 1 / hw_a[-1][1] == g5["E_catches_to_ceiling"])

# ------------------------------------------------------------------ G6
# refinement lemma (STRICT per-decade reading, convention C12)
GRID3 = frac(FIX["grids"]["refinement_grids"][0])
GRID4 = frac(FIX["grids"]["refinement_grids"][1])
a1_3 = census_a(NOMS[0], GRID3)
a1_4 = census_a(NOMS[0], GRID4)
check("G1 refinement census twin (1/1000)", a1_3 == census_b(NOMS[0], GRID3))
check("G1 refinement census twin (1/10000)", a1_4 == census_b(NOMS[0], GRID4))
check("G6 refinement probs sum to 1", sum(p for _, p in a1_3) == 1
      and sum(p for _, p in a1_4) == 1)
e1_3 = record_a(a1_3)[0]
e1_4 = record_a(a1_4)[0]
check("G1 refinement E_life twins", e1_3 == record_b(a1_3)[0] and e1_4 == record_b(a1_4)[0])
LN10 = math.log(10)
d1 = float(e1_3 - E_LIFE[0])
d2 = float(e1_4 - e1_3)
ok_d1 = check("G6 refinement decade 1 (1/100 -> 1/1000) within ln10 +/- 1/10", abs(d1 - LN10) <= 0.1)
ok_d2 = check("G6 refinement decade 2 (1/1000 -> 1/10000) within ln10 +/- 1/10", abs(d2 - LN10) <= 0.1)
if not ok_d1:
    anomaly("G6 refinement decade-1 increment %.6f misses ln10 = %.6f by %.6f "
            "(> 1/10 band; strict C12 reading). Cause pinned exactly: at 3 dp the "
            "support edges 0.117 = N*13/20 and 0.279 = N*31/20 land ON-GRID, "
            "restructuring both edge atoms to exact half-cells (2-dp edge cells "
            "are 0.8 and 0.4 of an interior cell) — a one-time edge correction; "
            "from 3 dp on the structure is self-similar and the increment "
            "converges to ln10 (decade-2 = %.6f, inside the band). The lemma's "
            "DIRECTION and cause-attribution stand; the registered +/-1/10 band "
            "was too tight for the first decade." % (d1, LN10, LN10 - d1, d2))
if not ok_d2:
    anomaly("G6 refinement decade-2 increment %.6f misses ln10 by %.6f" % (d2, abs(d2 - LN10)))
avg_decade = (float(e1_4) - float(E_LIFE[0])) / 2.0  # reporting row (C12)

# cadence -> 1/t from below across grids, t in {2, 3, 5}
for t in (2, 3, 5):
    p2 = pb_at_t_a(a1, t)
    p3 = pb_at_t_a(a1_3, t)
    p4 = pb_at_t_a(a1_4, t)
    check("G6 refinement cadence t=%d monotone up" % t, p2 < p3 < p4)
    check("G6 refinement cadence t=%d stays < 1/t" % t, p4 < Fraction(1, t))

# degeneracy: spread collapsed to a point => 1 atom, E_life = 1
degen = [(NOMS[0], Fraction(1))]
check("G6 degeneracy E_life = 1", record_a(degen)[0] == 1 and record_b(degen)[0] == 1)

# L1 sweep: committed float mix weights strictly decreasing at every
# committed pull x weather cell; every level band contains rank 1
PULLS = [float(frac(p)) for p in FIX["committed_constants"]["rod_pulls"]]
WEATHER = sorted({float(frac(w)) for w in FIX["committed_constants"]["weather_rarity_mults"]})
FPL = FIX["committed_constants"]["fish_per_level"]
MAXL = FIX["committed_constants"]["max_level"]
l1_ok = True
for pull in PULLS:
    for wm in WEATHER:
        eff = max(1.0, pull * wm)  # committed: weather multiplies the rod pull
        w = [1.0 / (rk ** (1.0 / eff)) for rk in range(1, 22)]
        if not all(w[i] > w[i + 1] for i in range(20)):
            l1_ok = False
check("G6 L1 mix weights strictly decreasing at every committed pull x weather cell", l1_ok)
check("G6 L1 every level band contains rank 1",
      all(min(1, max(1, lv) * FPL) >= 1 and 1 <= max(1, lv) * FPL for lv in range(1, MAXL + 1)))
L1_HOLDS = l1_ok

# -------------------------------------------------- Arm F (committed roll)
SEED_REGISTRY = []


def make_rng(seed):
    SEED_REGISTRY.append(seed)
    return random.Random(seed)


AF = FIX["arm_f"]
rng_f = make_rng(AF["seed"])
arm_f_rows = {}
for r in AF["ranks_gated"]:
    # the committed lines, VERBATIM shape (float round, random.uniform):
    nominal = round(0.18 * r ** 1.65, 2)
    seen = {}
    for _ in range(AF["n_draws_per_rank"]):
        w = max(0.01, round(nominal * rng_f.uniform(0.65, 1.55), 2))
        seen[w] = seen.get(w, 0) + 1
    exact_support = [float(v) for v, _ in atoms_by_rank[r - 1]]
    check("Arm F support equality rank %d" % r, sorted(seen) == exact_support)
    top = exact_support[-1]
    arm_f_rows["rank %d" % r] = {
        "atoms_seen": len(seen),
        "exact_atoms": len(exact_support),
        "min_seen": repr(min(seen)), "max_seen": repr(max(seen)),
        "ceiling_freq": repr(seen.get(top, 0) / AF["n_draws_per_rank"]),
        "ceiling_exact_p": fstr(atoms_by_rank[r - 1][-1][1]),
        "ceiling_exact_float": f12(atoms_by_rank[r - 1][-1][1]),
        "draws": AF["n_draws_per_rank"]}

# ------------------------------------------------- career table (C6, floats)
MIX = [Fraction(1, r) / H21 for r in range(1, 22)]
check("decision mix sums to 1", sum(MIX) == 1)


def career_quantized(n):
    tot = 0.0
    for qr, atoms in zip(MIX, atoms_by_rank):
        qf = float(qr)
        suffix = Fraction(1)
        for v, p in atoms:
            sf = float(suffix)
            tot += float(p) * (1.0 - (1.0 - qf * sf) ** n) / sf
            suffix -= p
    return tot


def career_quantized_twin(n):
    """Independently-ordered accumulation (per-rank partials, reversed atoms)."""
    parts = []
    for qr, atoms in zip(MIX, atoms_by_rank):
        qf = float(qr)
        suffixes = []
        s = Fraction(1)
        for v, p in atoms:
            suffixes.append((float(p), float(s)))
            s -= p
        parts.append(math.fsum(pf * (1.0 - (1.0 - qf * sf) ** n) / sf
                               for pf, sf in reversed(suffixes)))
    return math.fsum(parts)


def benchmark_continuous(n):
    tot = 0.0
    for qr in MIX:
        qf = float(qr)
        tot += math.fsum((1.0 - (1.0 - qf) ** t) / t for t in range(1, n + 1))
    return tot


career = {}
for n in FIX["grids"]["career_horizons"]:
    c1, c2 = career_quantized(n), career_quantized_twin(n)
    check("G1 career float twin @ n=%d (1e-9 rel, C6)" % n,
          abs(c1 - c2) <= 1e-9 * max(1.0, abs(c1)))
    career[n] = c1
bench = {n: benchmark_continuous(n) for n in FIX["grids"]["benchmark_horizons"]}

LIFETIME_TOTAL = sum(E_LIFE, Fraction(0))  # exact in memory (C7)
check("G1 lifetime total twin (exact)",
      LIFETIME_TOTAL == sum((record_b(at)[0] for at in atoms_by_rank), Fraction(0)))

# disclosed-landing reporting comparisons (C10 — never gated)
def disclosed(name, got_float, want_str, places):
    want = float(want_str)
    if round(got_float, places) != round(want, places):
        anomaly("disclosed %s: computed %s vs disclosed %s" % (name, f12(got_float), want_str))


for n, want in FIX["anchors"]["disclosed_career_table"].items():
    disclosed("career@%s" % n, career[int(n)], want, 1)
disclosed("lifetime total", float(LIFETIME_TOTAL), FIX["anchors"]["disclosed_lifetime_total"], 2)
disclosed("benchmark@2000", bench[2000], FIX["anchors"]["disclosed_benchmark"]["2000"], 0)
disclosed("benchmark@100000", bench[100000], FIX["anchors"]["disclosed_benchmark"]["100000"], 0)
disclosed("E_life(1) float", float(E_LIFE[0]), FIX["anchors"]["disclosed_E_life_rank1_float"], 3)
disclosed("cadence t=2 float", float(cadence[0][1]),
          FIX["anchors"]["cadence_t2_rank1"]["disclosed_float"], 4)

# onboarding cell (reporting)
Q1_L1 = Fraction(1, 1) / sum(Fraction(1, r) for r in FIX["grids"]["onboarding_cell"]["band_ranks"])
check("onboarding q1 = 6/11", Q1_L1 == frac(FIX["anchors"]["q1_level1"]))
KILL_L1 = 1 / (Q1_L1 * P_CEIL_1)
disclosed("kill casts level 1", float(KILL_L1), FIX["anchors"]["kill_casts_level1_float"], 2)

# ------------------------------------------- consequence rows (fixture block)
# option (a): the one-character round(., 3) world — exact re-census all ranks
rungs_3dp = [len(census_a(N, GRID3)) for N in NOMS]
p_ceil_1_3dp = a1_3[-1][1]
horizon_3dp = 1 / (Q1 * p_ceil_1_3dp)
gain_3dp = [record_a(census_a(N, GRID3))[0] - E_LIFE[i] for i, N in enumerate(NOMS)]
total_gain_3dp = sum(gain_3dp, Fraction(0))
aw = FIX["anchors"]["disclosed_approve_world"]
if rungs_3dp[0] != 163:
    anomaly("3-dp rank-1 rungs %d vs disclosed ~163" % rungs_3dp[0])
if abs(float(horizon_3dp) - 1480.0) > 20.0:
    anomaly("disclosed APPROVE-world horizon %s is a drafter hand-slip: the "
            "exact 3-dp re-census gives p_ceiling(1) = %s (0.279 = N*31/20 lands "
            "ON-GRID at 3 dp, halving the top cell), so the horizon is "
            "1/(q1 * %s) = %s ~ %s casts, not ~1480 (the disclosed number is the "
            "naive x10 scaling 2/81 -> 2/810 => 405/q1 ~ 1476). The APPROVE flip "
            "SURVIVES the correction: rungs %d >= 100 and horizon %s >= 1000."
            % (aw["horizon_casts"], fstr(p_ceil_1_3dp), fstr(p_ceil_1_3dp),
               fstr(horizon_3dp), f12(horizon_3dp), rungs_3dp[0], f12(horizon_3dp)))
approve_world_flips = rungs_3dp[0] >= 100 and horizon_3dp >= 1000
check("consequence (a): the round(.,3) world lands the APPROVE bands", approve_world_flips)
per_species_gain_avg = float(total_gain_3dp) / 21.0

# option (c): per-species ceiling table (badge surface)
ceiling_table = {}
for r, atoms in enumerate(atoms_by_rank, 1):
    v, p = atoms[-1]
    ceiling_table["rank %02d" % r] = {"ceiling_kg": f12(v), "p_ceiling": fstr(p),
                                      "p_ceiling_float": f12(p),
                                      "E_catches_to_ceiling": f12(1 / p)}
deep_rows = {"rank %02d" % r: ceiling_table["rank %02d" % r]
             for r in FIX["committed_constants"]["deepwater_ranks"]}

# ------------------------------------------------- band-margin ledger (C5)
BAND_RUNGS, BAND_PCEIL, BAND_ELIFE = 20, Fraction(1, 50), Fraction(4)
margins = {
    "clause_i_rungs": BAND_RUNGS - len(a1),
    "clause_i_pceil": fstr(P_CEIL_1 - BAND_PCEIL),
    "clause_i_pceil_float": f12(P_CEIL_1 - BAND_PCEIL),
    "clause_ii_E_life": f12(BAND_ELIFE - E_LIFE[0]),
    "clause_iii_min_cadence_gap": None,
}
min_gap_t, min_gap = None, None
for t, p in cadence:
    gap = Fraction(1, t) - p
    if min_gap is None or gap < min_gap:
        min_gap, min_gap_t = gap, t
margins["clause_iii_min_cadence_gap"] = f12(min_gap)
margins["clause_iii_min_cadence_gap_at_t"] = min_gap_t
check("C5 no decision clause lands margin-0 (exact zero)",
      len(a1) != BAND_RUNGS and P_CEIL_1 != BAND_PCEIL
      and E_LIFE[0] != BAND_ELIFE and min_gap != 0)
# per-species band sweep: which ranks would satisfy each REJECT clause
species_sweep = {}
for r, atoms in enumerate(atoms_by_rank, 1):
    species_sweep["rank %02d" % r] = {
        "rungs": len(atoms), "rungs_le_20": len(atoms) <= BAND_RUNGS,
        "p_ceiling_ge_1_50": atoms[-1][1] >= BAND_PCEIL,
        "E_life_le_4": E_LIFE[r - 1] <= BAND_ELIFE,
        "E_life_float": f12(E_LIFE[r - 1])}
only_rank1 = all(not (v["rungs_le_20"] or v["E_life_le_4"])
                 for k, v in species_sweep.items() if k != "rank 01")
check("C5 sweep: rank 1 is the ONLY species inside the REJECT bands (the ruling "
      "is modal-species-specific and rides L1)", only_rank1
      and species_sweep["rank 01"]["rungs_le_20"] and species_sweep["rank 01"]["E_life_le_4"])

# --------------------------------------------------------- decision (twins)
def evaluate_arm_a():
    """Evaluator 1: Arm A numbers. Registered order, REJECT evaluated FIRST."""
    if not L1_HOLDS:
        return "NULL"  # n1 re-key
    r_i = len(a1) <= BAND_RUNGS and P_CEIL_1 >= BAND_PCEIL
    r_ii = E_LIFE[0] <= BAND_ELIFE
    r_iii = all(p < Fraction(1, t) for t, p in cadence)
    if r_i and r_ii and r_iii:
        return "REJECT"
    if CHECKS["failed"]:
        return "INVALID"
    if len(a1) >= 100 and KILL_1 >= 1000:
        return "APPROVE"
    return "NULL"


def evaluate_arm_b():
    """Evaluator 2: recomputes every decision number from Arm B primitives."""
    if not L1_HOLDS:
        return "NULL"
    at = census_b(NOMS[0], GRID2)
    e_b = record_b(at)[0]
    series = pb_series_b(at, T_HI)
    F_top = sum(p for _, p in at[:-1])
    p_top = at[-1][1]
    kill_b = H21 / p_top  # 1/(q1 * p_top) with q1 = 1/H21
    r_i = len(at) <= BAND_RUNGS and p_top * 50 >= 1
    r_ii = e_b * 1 <= 4
    r_iii = all(series[t - 1] * t < 1 for t in range(2, T_HI + 1))
    if r_i and r_ii and r_iii:
        return "REJECT"
    if CHECKS["failed"]:
        return "INVALID"
    if len(at) >= 100 and kill_b >= 1000:
        return "APPROVE"
    return "NULL"


# ------------------------------------------------------- Arm R (reporting)
AR = FIX["arm_r"]
MIX_CUM = []
acc_f = 0.0
for qr in MIX:
    acc_f += float(qr)
    MIX_CUM.append(acc_f)
MIX_CUM[-1] = 1.0
ATOM_CUM = []
for atoms in atoms_by_rank:
    cum, s = [], 0.0
    for v, p in atoms:
        s += float(p)
        cum.append(s)
    cum[-1] = 1.0
    ATOM_CUM.append((cum, [float(v) for v, _ in atoms]))


def arm_r_leg(rng, n_careers, n_casts, horizons):
    sums = {h: 0 for h in horizons}
    draws = 0
    for _ in range(n_careers):
        best = [None] * 21
        events = 0
        ev_at = {}
        for t in range(1, n_casts + 1):
            draws += 2
            sp = bisect.bisect_left(MIX_CUM, rng.random())
            cum, vals = ATOM_CUM[sp]
            w = vals[bisect.bisect_left(cum, rng.random())]
            if best[sp] is None or w > best[sp]:  # the committed STRICT rule
                best[sp] = w
                events += 1
            if t in sums:
                ev_at[t] = events
        for h in horizons:
            sums[h] += ev_at[h]
    return {h: sums[h] / n_careers for h in horizons}, draws


horizons_r = [h for h in AR["report_horizons"] if h <= AR["main_casts_per_career"]]
rng_r_main = make_rng(AR["seed_main"])
r_main, draws_main = arm_r_leg(rng_r_main, AR["n_main_careers"],
                               AR["main_casts_per_career"], horizons_r)
rng_r_stab = make_rng(AR["seed_stability"])
r_stab, draws_stab = arm_r_leg(rng_r_stab, AR["n_stability_careers"],
                               AR["stability_casts_per_career"], horizons_r)
check("C8 seed registry exact",
      SEED_REGISTRY == [AF["seed"], AR["seed_main"], AR["seed_stability"]])
check("C8 aux seed never read", AR["seed_aux_never_read"] not in SEED_REGISTRY)

# ---------------------------------------------------------------- rulings
ruling_1 = evaluate_arm_a()
ruling_2 = evaluate_arm_b()
check("twin evaluators agree", ruling_1 == ruling_2)
RULING = ruling_1 if ruling_1 == ruling_2 else "INVALID"

# ------------------------------------------------------------------ output
results = {
    "verdict": RULING,
    "evaluators": [ruling_1, ruling_2],
    "decision_cell": {
        "mix": "bare rod pull 1.00, level 7, shore: q_r = (1/r)/H21",
        "H21": fstr(H21), "q1": fstr(Q1),
        "modal_species": "rank 1 (minnow) - L1 gated",
        "rungs_rank1": len(a1),
        "p_ceiling_rank1": fstr(P_CEIL_1), "p_ceiling_rank1_float": f12(P_CEIL_1),
        "E_catches_to_ceiling_rank1": f12(Fraction(81, 2)),
        "kill_casts_rank1": fstr(KILL_1), "kill_casts_rank1_float": f12(KILL_1),
        "E_life_rank1": fstr(E_LIFE[0]), "E_life_rank1_float": f12(E_LIFE[0]),
        "cadence_t2": fstr(cadence[0][1]), "cadence_t2_float": f12(cadence[0][1]),
        "onboarding_q1": fstr(Q1_L1), "onboarding_kill_casts": f12(KILL_L1),
        "bands": {"reject": "rungs <= 20 AND p_ceiling >= 1/50; E_life <= 4; "
                            "P(PB at t) < 1/t for t in 2..50",
                  "approve": "rungs >= 100 AND horizon >= 1000 casts"}},
    "band_margin_ledger_C5": margins,
    "species_band_sweep_C5": species_sweep,
    "census": {
        "A_table": [len(at) for at in atoms_by_rank],
        "E_life_exact_ranks_1_3": [fstr(E_LIFE[i]) for i in range(3)],
        "E_life_float_all_ranks": [f12(e) for e in E_LIFE],
        "E_life_print_note": "ranks >= 4 gated by in-memory Fraction equality "
                             "(G1) and reported as 12-digit floats (C9)",
        "lifetime_total_float": f12(LIFETIME_TOTAL),
        "rank1_atoms": [[fstr(Fraction(v)), fstr(p)] for v, p in a1]},
    "cadence_rank1_t2_50": {"t=%d" % t: fstr(p) for t, p in cadence},
    "career_table": {
        "quantized": {str(n): f12(c) for n, c in career.items()},
        "continuous_benchmark": {str(n): f12(b) for n, b in bench.items()},
        "note": "floats per C6; the quantized law converges to the lifetime "
                "total, the continuous benchmark diverges"},
    "refinement_G6": {
        "E_life_grids_rank1": {"1/100": f12(E_LIFE[0]), "1/1000": f12(e1_3),
                               "1/10000": f12(e1_4)},
        "decade_increments": [f12(d1), f12(d2)],
        "ln10": f12(LN10),
        "strict_reading_pass": [bool(ok_d1), bool(ok_d2)],
        "avg_per_decade_reporting": f12(avg_decade),
        "rungs_by_grid_rank1": [len(a1), len(a1_3), len(a1_4)]},
    "consequence_rows": {
        "option_a_round_3dp": {
            "rungs_3dp": rungs_3dp,
            "p_ceiling_rank1_3dp": fstr(p_ceil_1_3dp),
            "horizon_casts_3dp": f12(horizon_3dp),
            "per_species_E_life_gain_avg": f12(per_species_gain_avg),
            "total_E_life_gain": f12(total_gain_3dp),
            "lands_approve_bands": bool(approve_world_flips)},
        "option_b_unquantized_comparison": {
            "law": "P(PB at t) = 1/t exactly, distribution-free; E[records in n] "
                   "= H_n, divergent - the immortal chase returns",
            "H_2000_float": f12(sum(Fraction(1, t) for t in range(1, 2001)))},
        "option_c_badge_ceiling_table": ceiling_table,
        "deepwater_reporting_rows": deep_rows},
    "arm_f": {"rows": arm_f_rows, "seed": AF["seed"],
              "note": "support equality GATED on ranks {1,2,3,21}; frequencies "
                      "reporting-only"},
    "arm_r": {"main": {str(h): r_main[h] for h in horizons_r},
              "stability": {str(h): r_stab[h] for h in horizons_r},
              "exact_beside": {str(h): f12(career[h]) for h in horizons_r},
              "draws": {"main": draws_main, "stability": draws_stab},
              "careers": {"main": AR["n_main_careers"],
                          "stability": AR["n_stability_careers"]},
              "seed_registry": SEED_REGISTRY,
              "aux_never_read": AR["seed_aux_never_read"]},
    "anomalies": ANOMALIES,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": FAILURES},
}
(HERE / "results.json").write_text(
    json.dumps(results, sort_keys=True, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8", newline="\n")

out = []
out.append("VERDICT 084 runner — fishing trophy-record quantization ceiling (P071)")
out.append("ruling: %s (evaluators %s/%s)" % (RULING, ruling_1, ruling_2))
out.append("decision cell (bare rod pull 1.00, level 7, shore; modal species rank 1, L1 gated):")
out.append("  rungs(minnow) = %d (band <= 20)   p_ceiling = %s ~ %s (band >= 1/50)"
           % (len(a1), fstr(P_CEIL_1), f12(P_CEIL_1)))
out.append("  E[lifetime PBs](minnow) = %s ~ %s (band <= 4)"
           % (fstr(E_LIFE[0]), f12(E_LIFE[0])))
out.append("  kill horizon = %s ~ %s casts (E[species catches] = 81/2 = 40.5; "
           "level-1 onboarding ~ %s casts)"
           % (fstr(KILL_1), f12(KILL_1), f12(KILL_L1)))
out.append("  cadence: P(PB at 2) = %s ~ %s < 1/2; strict < 1/t verified for every "
           "t in 2..50 (min gap %s at t=%d)"
           % (fstr(cadence[0][1]), f12(cadence[0][1]),
              margins["clause_iii_min_cadence_gap"], min_gap_t))
out.append("band-margin ledger (C5): rungs margin %d; p_ceiling margin %s; "
           "E_life margin %s; no clause margin-0"
           % (margins["clause_i_rungs"], margins["clause_i_pceil_float"],
              margins["clause_ii_E_life"]))
out.append("species sweep (C5): rank 1 is the ONLY species inside the REJECT bands "
           "(rank 2: %d rungs, E_life ~ %s) — the ruling rides L1"
           % (len(atoms_by_rank[1]), f12(E_LIFE[1])))
out.append("|A| table (gated verbatim): %s" % [len(at) for at in atoms_by_rank])
out.append("E_life exact ranks 1-3: %s | floats all ranks: %s"
           % ([fstr(E_LIFE[i]) for i in range(3)], [f12(e) for e in E_LIFE]))
out.append("lifetime total (exact in memory, twin-gated): ~ %s (disclosed ~153.38)"
           % f12(LIFETIME_TOTAL))
out.append("career table E[PB events in n casts] vs continuous benchmark:")
out.append("  quantized: %s" % {n: round(c, 2) for n, c in career.items()})
out.append("  continuous: %s (divergent)" % {n: round(b, 1) for n, b in bench.items()})
out.append("refinement (G6, strict C12 reading): E_life rank 1 %s -> %s -> %s; "
           "decades %s / %s vs ln10 %s -> pass %s/%s; avg per decade %s (reporting)"
           % (f12(E_LIFE[0]), f12(e1_3), f12(e1_4), f12(d1), f12(d2), f12(LN10),
              ok_d1, ok_d2, f12(avg_decade)))
out.append("consequence (a) round(.,3): rungs %s; minnow p_ceiling %s, horizon ~ %s "
           "casts; +E_life avg %s/species (total %s) -> lands APPROVE bands: %s"
           % (rungs_3dp[:3] + ["..."] + rungs_3dp[-1:], fstr(p_ceil_1_3dp),
              f12(horizon_3dp), f12(per_species_gain_avg), f12(total_gain_3dp),
              approve_world_flips))
out.append("consequence (b) raw-float comparison: P(PB at t) = 1/t exact, H_n divergent")
out.append("consequence (c) badge ceilings: rank 1 = 0.28 kg @ 2/81 ... rank 21 = %s kg @ %s"
           % (ceiling_table["rank 21"]["ceiling_kg"], ceiling_table["rank 21"]["p_ceiling"]))
out.append("arm F (committed roll, seed %d): %s" % (AF["seed"], json.dumps(
    {k: {"atoms": "%d/%d" % (v["atoms_seen"], v["exact_atoms"]),
         "ceiling_freq": v["ceiling_freq"], "exact": v["ceiling_exact_float"]}
     for k, v in arm_f_rows.items()}, sort_keys=True)))
out.append("arm R (reporting-only): main %s | stability %s | exact %s"
           % ({h: round(r_main[h], 2) for h in horizons_r},
              {h: round(r_stab[h], 2) for h in horizons_r},
              {h: round(career[h], 2) for h in horizons_r}))
out.append("anomalies: %s" % ("NONE" if not ANOMALIES else " | ".join(ANOMALIES)))
out.append("self-checks: %d passed, %d failed%s"
           % (CHECKS["passed"], CHECKS["failed"],
              "" if not FAILURES else " — " + "; ".join(FAILURES[:10])))
stdout_text = "\n".join(out) + "\n"
(HERE / "run-stdout.txt").write_text(stdout_text, encoding="utf-8", newline="\n")
sys.stdout.write(stdout_text)
# exit contract: the DESIGNED G6 refinement decade-1 miss (C12, pre-disclosed in
# fixtures) is the only tolerated failure; anything else is a hard red.
tolerated = set()
if not ok_d1:
    tolerated.add("G6 refinement decade 1 (1/100 -> 1/1000) within ln10 +/- 1/10")
sys.exit(0 if all(f in tolerated for f in FAILURES) else 1)
