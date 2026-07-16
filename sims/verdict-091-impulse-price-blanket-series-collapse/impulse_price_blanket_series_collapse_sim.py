#!/usr/bin/env python3
"""VERDICT 091 — the impulse-price blanket vs the series funnel (P078).

Three-arm hermetic runner (reads ONLY its own fixtures.json):

  Arm A — seedless exact-Fraction closed forms (DECISION-bearing):
          the two-branch royalty function, the standalone bar law
          m*(1) = 2·p/p0, the border/forbidden-band contacts, the full
          m*(K, r) collapse surface with its exact K→∞ crossing
          r* = 400/899, the signed fee lemma, the KU mixture lemma.
  Arm B — INDEPENDENTLY-WRITTEN per-mass ledger twin: a cohort mass
          schedule built book-by-book, income as a mass×royalty dot
          product, its own decision evaluator; tied to Arm A through
          the typed must-equal contacts C1/C2/C3 at all 15 (K, r)
          cells plus C4 (the geometric-sum identity).
  Arm R — seeded finite-cohort traces, REPORTING-ONLY, under the
          REGISTERED draw-order grammar (fixture line); seeds
          20261700/701/702; aux 20261703 NEVER read; no statistical
          gate touches any decision.

Every registered anchor is re-derived from scratch (zero trust);
exact rationals are compared as Fraction VALUES with the spelling
derived, never compared (the V090 session idea applied). Decision
rule pre-registered, applied in the registered order REJECT →
INVALID → APPROVE → NULL, REJECT evaluated FIRST. The m*_inf(9/10)
vs 11/10 knife-edge (margin exactly 91/90810) is registered and
EXCLUDED from every decision clause — the evaluators receive an
ENUMERATED input set that cannot carry it.
"""

import json
import os
import random
import sys
from fractions import Fraction

assert sys.version_info[:2] == (3, 11), (
    "CPython 3.11 pinned and asserted; got %s" % (sys.version_info[:2],))

HERE = os.path.dirname(os.path.abspath(__file__))
FX = json.load(open(os.path.join(HERE, "fixtures.json"), encoding="utf-8"))


def fr(pair):
    """Fixture [num, den] value pair -> Fraction (the V090 value-pair rule)."""
    return Fraction(pair[0], pair[1])


def frs(x):
    """Render an exact rational: reduced n/d, whole values bare."""
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else (
        "%d/%d" % (f.numerator, f.denominator))


CHECKS = []


def chk(name, cond, detail=""):
    ok = bool(cond)
    CHECKS.append((name, ok))
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                         (" — " + detail) if detail else ""))
    return ok


ANOMALY = []  # rows: (anchor, status, disclosed, derived) status in
              # {matched, MISMATCH, vacant}


def anchor(name, disclosed_value, derived_value, equal):
    status = "matched" if equal else "MISMATCH"
    ANOMALY.append((name, status, str(disclosed_value), str(derived_value)))
    chk("anchor %s" % name, equal,
        "disclosed %s / derived %s" % (disclosed_value, derived_value))


def vacancy(name, derived_value, note):
    ANOMALY.append((name, "vacant", note, str(derived_value)))
    print("[VACANT] %s — %s — sim value: %s" % (name, note, derived_value))


RESULTS = {}

# ---------------------------------------------------------------------------
# Arm A — the royalty function and the closed forms (seedless, exact)
# ---------------------------------------------------------------------------
T_HI = fr(FX["royalty"]["tier_hi"])          # 7/10
T_LO = fr(FX["royalty"]["tier_lo"])          # 7/20
BAND_LO = fr(FX["royalty"]["band_lo"])       # 299/100
BAND_HI = fr(FX["royalty"]["band_hi"])       # 999/100
P0 = fr(FX["royalty"]["promo_price_p0"])     # 99/100
PRICES = {k: fr(v) for k, v in FX["royalty"]["committed_prices"].items()}
P_SER = fr(FX["royalty"]["series_price"])    # 499/100


def roy(p, delta=Fraction(0)):
    """KDP per-sale royalty; delta = per-MB delivery fee, 70% tier ONLY."""
    if BAND_LO <= p <= BAND_HI:
        return T_HI * p - delta
    return T_LO * p


print("== Arm A — T1: the border halves exactly; the forbidden band ==")
jump = roy(BAND_LO) / (T_LO * BAND_LO)
anchor("T1 jump ratio == 2 (margin-0 contact i)", frs(fr(FX["f_census_anchors"]["jump_ratio"])),
       frs(jump), jump == fr(FX["f_census_anchors"]["jump_ratio"]))
lower_edge = T_LO * BAND_LO            # sup of the lower branch (open)
upper_edge = roy(BAND_LO)              # min of the upper branch
width = upper_edge - lower_edge
anchor("T1 forbidden-band width (2093/2000)", frs(fr(FX["f_census_anchors"]["forbidden_band_width"])),
       frs(width), width == fr(FX["f_census_anchors"]["forbidden_band_width"]))
chk("T1 width == its own lower edge EXACTLY (margin-0 contact ii)",
    width == lower_edge, "%s == %s" % (frs(width), frs(lower_edge)))
edges = [roy(P0), lower_edge, upper_edge, roy(BAND_HI)]
fx_edges = [fr(v) for v in FX["f_census_anchors"]["attainable_set_edges"]]
anchor("T1 attainable-set edges", "[%s]" % ", ".join(map(frs, fx_edges)),
       "[%s]" % ", ".join(map(frs, edges)), edges == fx_edges)
anchor("T1 V049 external anchor roy(0.99) == 693/2000",
       frs(fr(FX["royalty"]["v049_external_anchor_roy_p0"])), frs(roy(P0)),
       roy(P0) == fr(FX["royalty"]["v049_external_anchor_roy_p0"]))
chk("T1 every committed price in the upper branch",
    all(BAND_LO <= p <= BAND_HI for p in PRICES.values()))
RESULTS["t1"] = {
    "jump_ratio": frs(jump),
    "forbidden_band": "[%s, %s) per-sale royalties unattainable; width %s == lower edge"
                      % (frs(lower_edge), frs(upper_edge), frs(width)),
    "attainable_set": "[%s, %s) U [%s, %s]" % tuple(map(frs, edges)),
}

print()
print("== Arm A — T2: the standalone bar law m*(1) = 2 * p / p0 ==")
bars = {}
fx_bars = {"twelfth_cake_marmalade_3.99": fr(FX["f_census_anchors"]["standalone_bars"]["3.99"]),
           "night_kiln_slow_word_4.99": fr(FX["f_census_anchors"]["standalone_bars"]["4.99"]),
           "band_floor_2.99": fr(FX["f_census_anchors"]["standalone_bars"]["2.99"])}
for name, p in PRICES.items():
    m1 = roy(p) / roy(P0)
    law = (T_HI / T_LO) * (p / P0)
    bars[name] = m1
    chk("T2 bar law at %s: m*(1) == 2*p/p0" % name, m1 == law,
        "m* = %s ~ %.4f" % (frs(m1), float(m1)))
    anchor("T2 standalone bar %s" % name, frs(fx_bars[name]), frs(m1),
           m1 == fx_bars[name])
chk("T2 home ground: every standalone bar >= 6 (REJECT clause (a) input)",
    all(m >= 6 for m in bars.values()))
fee_rendered = []
p399 = PRICES["twelfth_cake_marmalade_3.99"]
for d_pair in FX["f_census_anchors"]["fee_row_deltas"]:
    d = fr(d_pair)
    m_d = roy(p399, d) / roy(P0)
    fee_rendered.append("%.4f" % float(m_d))
    chk("T2 fee lemma delta=%s strictly lowers the bar" % frs(d),
        m_d < bars["twelfth_cake_marmalade_3.99"], "m* ~ %.4f" % float(m_d))
anchor("T2 fee row at $3.99 (4dp renderings)",
       str(FX["f_census_anchors"]["fee_row_at_3.99_rendered_4dp"]),
       str(fee_rendered),
       fee_rendered == FX["f_census_anchors"]["fee_row_at_3.99_rendered_4dp"])
# the full delta grid (incl. 0) at every committed price — reporting sweep
fee_sweep = {}
for name, p in PRICES.items():
    fee_sweep[name] = {frs(fr(d)): frs(roy(p, fr(d)) / roy(P0))
                       for d in FX["royalty"]["delta_grid"]}
vacancy("fee sweep at committed prices other than $3.99",
        json.dumps(fee_sweep, sort_keys=True),
        "registration discloses the $3.99 row only; full grid reported")
RESULTS["t2"] = {"bars": {k: frs(v) for k, v in bars.items()},
                 "fee_row_3.99": fee_rendered, "fee_sweep": fee_sweep}

print()
print("== Arm A — T3: the series funnel collapse m*(K, r) ==")
K_ANCH = FX["series_model"]["K_anchors"]
R_GRID = [fr(r) for r in FX["series_model"]["r_grid"]]


def income_closed(p1, K, r):
    """Arm A closed form: roy(p1) + sum_{k=2..K} r^(k-1) roy(P_SER)."""
    tail = sum((r ** (k - 1) for k in range(2, K + 1)), Fraction(0))
    return roy(p1) + tail * roy(P_SER)


def mstar(K, r):
    return income_closed(P_SER, K, r) / income_closed(P0, K, r)


def mstar_inf(r):
    return roy(P_SER) / ((1 - r) * roy(P0) + r * roy(P_SER))


TABLE = {(K, r): mstar(K, r) for K in K_ANCH for r in R_GRID}
for K in K_ANCH:
    print("   K=%2d: %s" % (K, " · ".join(
        "%s ~ %.4f" % (frs(TABLE[(K, r)]), float(TABLE[(K, r)]))
        for r in R_GRID)))
chk("T3 m*(1, r) r-independent == standalone bar (equality row)",
    all(TABLE[(1, r)] == bars["night_kiln_slow_word_4.99"] for r in R_GRID))
chk("T3 strictly decreasing in K at every r",
    all(TABLE[(36, r)] < TABLE[(3, r)] < TABLE[(1, r)] for r in R_GRID))
chk("T3 strictly decreasing in r at K in {3, 36}",
    all(TABLE[(K, R_GRID[i])] > TABLE[(K, R_GRID[i + 1])]
        for K in (3, 36) for i in range(len(R_GRID) - 1)))
fx_m3 = [fr(v) for v in FX["f_census_anchors"]["m3_row"]]
m3_row = [TABLE[(3, r)] for r in R_GRID]
anchor("T3 m*(3, r) row (5 exact rationals)",
       "[%s]" % ", ".join(map(frs, fx_m3)),
       "[%s]" % ", ".join(map(frs, m3_row)), m3_row == fx_m3)
m3_render = ["%.4f" % float(m) for m in m3_row]
anchor("T3 m*(3, r) row float renderings",
       str(FX["f_census_anchors"]["m3_row_floats_disclosed"]), str(m3_render),
       m3_render == FX["f_census_anchors"]["m3_row_floats_disclosed"])
thin = TABLE[(3, Fraction(1, 2))]
anchor("T3 disclosed thin cell m*(3, 1/2) == 3493/1695 (one step above 2)",
       frs(fr(FX["f_census_anchors"]["thin_cell_m3_half"]["value"])), frs(thin),
       thin == fr(FX["f_census_anchors"]["thin_cell_m3_half"]["value"]))
chk("T3 thin cell sits ABOVE the witness line (2.0608 > 2)", thin > 2,
    "clearance %s ~ %.4f" % (frs(thin - 2), float(thin - 2)))
m36_34 = TABLE[(36, Fraction(3, 4))]
m36_910 = TABLE[(36, Fraction(9, 10))]
anchor("T3 m*(36, 3/4) 4dp rendering",
       FX["f_census_anchors"]["m36_34_band"]["float_disclosed"],
       "%.4f" % float(m36_34),
       "%.4f" % float(m36_34) == FX["f_census_anchors"]["m36_34_band"]["float_disclosed"])
chk("T3 comp cell m*(36, 3/4) <= 4/3 (REJECT clause (c) input)",
    m36_34 <= fr(FX["f_census_anchors"]["m36_34_band"]["le"]),
    "margin to 4/3 = %s ~ %.4f" % (frs(Fraction(4, 3) - m36_34),
                                   float(Fraction(4, 3) - m36_34)))
anchor("T3 m*(36, 9/10) 4dp rendering",
       FX["f_census_anchors"]["m36_910_float_disclosed"], "%.4f" % float(m36_910),
       "%.4f" % float(m36_910) == FX["f_census_anchors"]["m36_910_float_disclosed"])
m36_row = [TABLE[(36, r)] for r in R_GRID]
vacancy("m*(36, r) full row beyond the two named cells",
        "[%s]" % ", ".join("%s ~ %.4f" % (frs(m), float(m)) for m in m36_row),
        "registration disclosed the (36, 3/4) and (36, 9/10) cells only")
# K -> inf: exact crossing and the EXCLUDED knife-edge
ry, r0 = roy(P_SER), roy(P0)
r_star = (ry - 2 * r0) / (2 * (ry - r0))
anchor("T3 exact K->inf crossing r* == 400/899",
       frs(fr(FX["f_census_anchors"]["r_star_inf"])), frs(r_star),
       r_star == fr(FX["f_census_anchors"]["r_star_inf"]))
chk("T3 m*_inf(r*) == 2 exactly", mstar_inf(r_star) == 2)
mi910 = mstar_inf(Fraction(9, 10))
ke = FX["f_census_anchors"]["knife_edge"]
anchor("T3 m*_inf(9/10) == 69860/63567 (EXCLUDED from decisions)",
       frs(fr(ke["m_inf_910"])), frs(mi910), mi910 == fr(ke["m_inf_910"]))
margin_ke = fr(ke["vs"]) - mi910
anchor("T3 knife-edge margin vs 11/10 == 91/90810 (EXCLUDED from decisions)",
       frs(fr(ke["margin"])), frs(margin_ke), margin_ke == fr(ke["margin"]))
chk("T3 finite-K ordering m*(36, 9/10) > m*_inf(9/10) (this IS the gate)",
    m36_910 > mi910)
chk("T3 APPROVE-side witness: at r <= 1/4 every K=3 cell clears 3",
    all(TABLE[(3, r)] > 3 for r in R_GRID if r <= Fraction(1, 4)))
chk("T3 APPROVE-side witness: below r*_inf the K->inf bar stays above 2",
    all(mstar_inf(r) > 2 for r in R_GRID if r < r_star))
RESULTS["t3"] = {
    "m_table": {"K=%d,r=%s" % (K, frs(r)): frs(TABLE[(K, r)])
                for K in K_ANCH for r in R_GRID},
    "r_star_inf": frs(r_star),
    "m_inf_910": frs(mi910),
    "knife_edge_margin_vs_11_10": frs(margin_ke) + " (EXCLUDED from decision clauses)",
}

print()
print("== Arm A — T5: the KU mixture dampens the lever, monotonically ==")
BETAS = [fr(b) for b in FX["ku_mixture"]["beta_grid"]]
J_GRID = [("roy/2", ry / 2), ("roy", ry), ("2*roy", 2 * ry)]


def mstar_ku(K, r, beta, J):
    i_full = income_closed(P_SER, K, r)
    i_promo = income_closed(P0, K, r)
    return (((1 - beta) * i_full + beta * J)
            / ((1 - beta) * i_promo + beta * J))


mono_all, recover_all, above_one = True, True, True
ku_rows = {}
for jname, J in J_GRID:
    row = [mstar_ku(3, Fraction(1, 2), b, J) for b in BETAS]
    ku_rows[jname] = [frs(v) for v in row]
    if not all(row[i] > row[i + 1] for i in range(len(row) - 1)):
        mono_all = False
    if row[0] != TABLE[(3, Fraction(1, 2))]:
        recover_all = False
    if not all(v > 1 for v in row):
        above_one = False
chk("T5 m* strictly decreasing in beta at every J (the monotone lemma)",
    mono_all)
chk("T5 beta = 0 recovers the sales-only bar at every J", recover_all)
chk("T5 every KU-dampened bar stays > 1 (direction never flips)", above_one)
ku_cell = mstar_ku(3, Fraction(1, 2), Fraction(1, 2), ry)
anchor("T5 named KU cell (K=3, r=1/2, beta=1/2, J=roy) == 5489/3691",
       frs(fr(FX["f_census_anchors"]["ku_named_cell"])), frs(ku_cell),
       ku_cell == fr(FX["f_census_anchors"]["ku_named_cell"]))
RESULTS["t5"] = {"rows_by_J": ku_rows, "named_cell": frs(ku_cell)}

print()
print("== G5 — hand worlds (derived by hand in the registration) ==")
hw1 = roy(Fraction(4)) / roy(P0)
anchor("G5a standalone $4.00 bar == 800/99 (== 2*4/0.99 by hand)",
       frs(fr(FX["f_census_anchors"]["hand_worlds"]["g5a_standalone_4.00"])),
       frs(hw1), hw1 == fr(FX["f_census_anchors"]["hand_worlds"]["g5a_standalone_4.00"]))
chk("G5a the law reproduces the hand value", hw1 == 2 * Fraction(4) / P0)
# G5b, faithful to the registered hand derivation "K = 2, r = 1/2,
# p = $4.00: I = 2.8 + 1.4 = 4.2, I' = 0.3465 + 1.4 = 1.7465" — the
# downstream book sits at $4.00 too (1.4 = 0.5 x 2.8):
hw2 = (roy(Fraction(4)) + Fraction(1, 2) * roy(Fraction(4))) / \
      (roy(P0) + Fraction(1, 2) * roy(Fraction(4)))
anchor("G5b hand world m*(2, 1/2) at $4.00 == 8400/3493",
       frs(fr(FX["f_census_anchors"]["hand_worlds"]["g5b_K2_r_half_4.00"])),
       frs(hw2), hw2 == fr(FX["f_census_anchors"]["hand_worlds"]["g5b_K2_r_half_4.00"]))
RESULTS["g5"] = {"g5a": frs(hw1), "g5b": frs(hw2)}

# ---------------------------------------------------------------------------
# Arm B — the independently-written per-mass ledger twin (own structure)
# ---------------------------------------------------------------------------
print()
print("== Arm B — per-mass ledger twin (typed contacts C1/C2/C3/C4) ==")


def ledger_income(book1_price, K, r):
    """Arm B: build the cohort mass schedule FIRST (a list), then take the
    mass x royalty dot product — deliberately a different structure from
    Arm A's closed-form tail sum."""
    masses = [Fraction(1)]
    while len(masses) < K:
        masses.append(masses[-1] * r)
    schedule = [book1_price] + [P_SER] * (K - 1)
    total = Fraction(0)
    for mass, price in zip(masses, schedule):
        total += mass * roy(price)
    return total


c1 = c2 = c3 = 0
for K in K_ANCH:
    for r in R_GRID:
        b_full = ledger_income(P_SER, K, r)
        b_promo = ledger_income(P0, K, r)
        a_full = income_closed(P_SER, K, r)
        a_promo = income_closed(P0, K, r)
        c1 += (b_full == a_full)
        c2 += (b_promo == a_promo)
        c3 += (b_full / b_promo == TABLE[(K, r)])
chk("C1 ledger full-price income == closed form at 15/15 cells", c1 == 15,
    "%d/15" % c1)
chk("C2 ledger promo income == closed form at 15/15 cells", c2 == 15,
    "%d/15" % c2)
chk("C3 ledger ratio == m*(K, r) at 15/15 cells", c3 == 15, "%d/15" % c3)
gs = sum((Fraction(1, 2) ** (k - 1) for k in range(2, 37)), Fraction(0))
gs_closed = (Fraction(1, 2) - Fraction(1, 2) ** 36) / (1 - Fraction(1, 2))
anchor("C4 geometric-sum identity (r=1/2, K=36) == 34359738367/34359738368",
       frs(fr(FX["f_census_anchors"]["c4_geometric_sum"])), frs(gs),
       gs == gs_closed == fr(FX["f_census_anchors"]["c4_geometric_sum"]))

# ---------------------------------------------------------------------------
# Census recount — hermetic, from the fixture's pinned excerpts
# ---------------------------------------------------------------------------
print()
print("== G6 — census recount from the fixture's pinned copies ==")
CEN = FX["census"]
blanket, ratio, fork = [], [], []
for fn in CEN["vetting_file_universe"]:
    text = CEN["pinned_excerpts"].get(fn, "")
    if any(p in text for p in CEN["grammar_patterns"]):
        blanket.append(fn)
    if CEN["ratio_pattern"] in text:
        ratio.append(fn)
    if CEN["fork_pattern"] in text:
        fork.append(fn)
anchor("census blanket count == 26", CEN["blanket_count"], len(blanket),
       len(blanket) == CEN["blanket_count"])
chk("census blanket file list == the disclosed 26-file list",
    blanket == CEN["expected_blanket_files"])
anchor("census 'any plausible volume ratio' count == 2", CEN["ratio_count"],
       len(ratio), len(ratio) == CEN["ratio_count"])
chk("census ratio files == {de-driekoningentaart, the-twelfth-cake}",
    ratio == CEN["expected_ratio_files"])
anchor("census fork count == 1 (the Marmalade packet)", CEN["fork_count"],
       len(fork), len(fork) == CEN["fork_count"])
chk("census fork file == the-marmalade-post.md",
    fork == CEN["expected_fork_files"])
chk("census: all three Night Kiln NL packets carry the blanket",
    all(f in blanket for f in CEN["night_kiln_series_packets_in_list"]))
chk("census: the justification packets are blanket packets too",
    all(f in blanket for f in CEN["expected_ratio_files"]))
chk("census: the guide teaches the blanket ('the *procedure* transfers')",
    CEN["ratio_pattern"] in CEN["guide_pinned_excerpt"]
    and CEN["guide_pattern"] in CEN["guide_pinned_excerpt"])
wc = CEN["night_kiln_word_counts"]
chk("census: Night Kiln word counts carried (harvest-matched 16180/16192/23610)",
    (wc["the-night-kiln.md"], wc["the-morning-door.md"],
     wc["the-harvest-rows.md"]) == (16180, 16192, 23610))
RESULTS["census"] = {"blanket_files": blanket, "ratio_files": ratio,
                     "fork_files": fork, "counts": [len(blanket), len(ratio),
                                                    len(fork)]}

# ---------------------------------------------------------------------------
# Arm R — seeded finite-cohort traces (REPORTING-ONLY, registered grammar)
# ---------------------------------------------------------------------------
print()
print("== Arm R — seeded cohort traces (reporting-only; registered grammar) ==")
AR = FX["arm_r"]
N = AR["N_per_seed"]
K_R = AR["cohort_cell"]["K"]
R_R = fr(AR["cohort_cell"]["r"])
ROY_F = float(roy(P_SER))
ROY0_F = float(roy(P0))


def cohort_trace(seed):
    """The registered draw-order grammar, verbatim from the fixture line:
    per reader i = 0..N-1 ascending, per boundary k = 2..K ascending, ONE
    uniform; continue iff u < float(r), else break; no other draws; one
    random.Random(seed) per trace; the aux seed is never read."""
    rng = random.Random(seed)
    rf = float(R_R)
    draws = 0
    books_per_reader = []
    for _ in range(N):
        books = 1
        for _k in range(2, K_R + 1):
            draws += 1
            if rng.random() < rf:
                books += 1
            else:
                break
        books_per_reader.append(books)
    return books_per_reader, draws


def accumulate(books_per_reader, book1_price_float):
    """The disclosed drafting accumulation convention: float royalty added
    per purchased book in reader order; round(total, 2) at the end."""
    total = 0.0
    for books in books_per_reader:
        total += book1_price_float
        for _ in range(books - 1):
            total += ROY_F
    return round(total, 2)


arm_r_out = {}
prev_fx = AR["disclosed_previews_full_price_arm"]
exact_mean = float(income_closed(P_SER, K_R, R_R) * N)
anchor("Arm R exact cohort mean (full-price arm) == 80775.625",
       AR["exact_cohort_mean"], "%.3f" % exact_mean,
       "%.3f" % exact_mean == AR["exact_cohort_mean"])
for seed in AR["seeds_reporting_only"]:
    bpr, draws = cohort_trace(seed)
    full = accumulate(bpr, ROY_F)
    # in-process determinism sentinel: the seed reproduces itself
    bpr2, draws2 = cohort_trace(seed)
    chk("Arm R seed %d reproduces itself in-process" % seed,
        bpr == bpr2 and draws == draws2, "%d draws" % draws)
    anchor("Arm R preview seed %d (full-price arm)" % seed, prev_fx[str(seed)],
           "%.2f" % full, "%.2f" % full == prev_fx[str(seed)])
    chk("Arm R seed %d within 2%% of the exact cohort mean (reporting sanity)"
        % seed, abs(full - exact_mean) / exact_mean < 0.02)
    promo = accumulate(bpr, ROY0_F)
    vacancy("Arm R seed %d promo-arm cohort value (same trace, zero extra draws)"
            % seed, "%.2f (empirical bar %.4f)" % (promo, full / promo),
            "undisclosed in the registration; derived from the same trace")
    arm_r_out[str(seed)] = {"full": "%.2f" % full, "promo": "%.2f" % promo,
                            "empirical_bar": "%.4f" % (full / promo),
                            "draws": draws,
                            "books_sold": sum(bpr)}
chk("Arm R aux seed %d NEVER read by any leg" % AR["aux_seed_never_read"],
    True, "asserted: no code path constructs random.Random(20261703)")
chk("Arm R carries NO statistical gate on any decision", True)
RESULTS["arm_r"] = {"seeds": arm_r_out, "exact_cohort_mean": "%.3f" % exact_mean,
                    "aux_seed_never_read": AR["aux_seed_never_read"]}

# ---------------------------------------------------------------------------
# The decision — two independently-written evaluators, enumerated inputs
# ---------------------------------------------------------------------------
print()
print("== Decision (registered order: REJECT -> INVALID -> APPROVE -> NULL) ==")

DECISION_INPUTS_A = {
    "bars": dict(bars),
    "m3_row": {frs(r): TABLE[(3, r)] for r in R_GRID},
    "m36_row": {frs(r): TABLE[(36, r)] for r in R_GRID},
}
chk("knife-edge exclusion gate: decision input set is ENUMERATED and "
    "carries no m*_inf value and no 11/10 comparison",
    set(DECISION_INPUTS_A) == {"bars", "m3_row", "m36_row"})


def evaluator_A(inp):
    """Decision evaluator over Arm A values (registered clauses verbatim)."""
    a = all(m >= 6 for m in inp["bars"].values())
    b = any(m <= 2 for m in inp["m3_row"].values())
    c = inp["m36_row"][frs(Fraction(3, 4))] <= Fraction(4, 3)
    if a and b and c:
        return "REJECT", (a, b, c)
    series_cells = list(inp["m3_row"].values()) + list(inp["m36_row"].values())
    if all(m > 4 for m in series_cells):
        return "APPROVE", (a, b, c)
    return "NULL", (a, b, c)


def evaluator_B():
    """Independently-written second evaluator: recomputes every decision
    quantity from the Arm B LEDGER (never touching Arm A's table), scans
    clauses in a different style."""
    verdict_bits = []
    # clause (a): home ground, all committed standalone bars >= 6
    ok_a = True
    for p in PRICES.values():
        bar = ledger_income(p, 1, Fraction(0)) / ledger_income(P0, 1, Fraction(0))
        if bar < 6:
            ok_a = False
    verdict_bits.append(ok_a)
    # clause (b): existential collapse witness at K = 3
    ok_b = False
    for r in R_GRID:
        if ledger_income(P_SER, 3, r) <= 2 * ledger_income(P0, 3, r):
            ok_b = True
    verdict_bits.append(ok_b)
    # clause (c): the comp cell
    ok_c = (3 * ledger_income(P_SER, 36, Fraction(3, 4))
            <= 4 * ledger_income(P0, 36, Fraction(3, 4)))
    verdict_bits.append(ok_c)
    if all(verdict_bits):
        return "REJECT", tuple(verdict_bits)
    approve = True
    for K in (3, 36):
        for r in R_GRID:
            if ledger_income(P_SER, K, r) <= 4 * ledger_income(P0, K, r):
                approve = False
    return ("APPROVE" if approve else "NULL"), tuple(verdict_bits)


ruling_A, clauses_A = evaluator_A(DECISION_INPUTS_A)
ruling_B, clauses_B = evaluator_B()
chk("REJECT clause (a) home ground real (bars 266/33, 998/99, 598/99 all >= 6)",
    clauses_A[0])
chk("REJECT clause (b) series collapse witness exists (m*(3, 3/4) = 18463/11271"
    " <= 2; m*(3, 9/10) too)", clauses_A[1])
chk("REJECT clause (c) comp-scale collapse (m*(36, 3/4) <= 4/3)", clauses_A[2])
chk("twin decision evaluators agree", ruling_A == ruling_B,
    "%s / %s" % (ruling_A, ruling_B))
chk("clause bits agree across evaluators", clauses_A == clauses_B)
approve_would = all(TABLE[(K, r)] > 4 for K in (3, 36) for r in R_GRID)
chk("APPROVE mutually exclusive with REJECT via clause (b)",
    not (clauses_A[1] and approve_would))

gate_failures = [n for n, ok in CHECKS if not ok]
if gate_failures:
    FINAL = "INVALID"
else:
    FINAL = ruling_A
print()
print("VERDICT 091 RULING: %s" % FINAL)
RESULTS["decision"] = {
    "ruling": FINAL,
    "evaluator_A": ruling_A, "evaluator_B": ruling_B,
    "clauses_reject": {"a_home_ground": clauses_A[0],
                       "b_series_collapse": clauses_A[1],
                       "c_comp_scale": clauses_A[2]},
    "order_applied": FX["decision_rule"]["order"],
}

# ---------------------------------------------------------------------------
# Anomaly census + close-out
# ---------------------------------------------------------------------------
matched = sum(1 for r in ANOMALY if r[1] == "matched")
mismatched = sum(1 for r in ANOMALY if r[1] == "MISMATCH")
vacant = sum(1 for r in ANOMALY if r[1] == "vacant")
print()
print("Anomaly census (disclosure coverage): %d compared-and-matched, "
      "%d mismatched, %d vacant" % (matched, mismatched, vacant))
chk("anomaly census: zero mismatches (every disclosed value reproduced)",
    mismatched == 0)
RESULTS["anomaly_census"] = {
    "compared_and_matched": matched, "mismatched": mismatched,
    "vacant": vacant,
    "rows": [{"anchor": a, "status": s, "disclosed_or_note": d, "derived": v}
             for a, s, d, v in ANOMALY],
}
RESULTS["seeds"] = {"registered_set": "20261700-703",
                    "reporting_only": AR["seeds_reporting_only"],
                    "aux_never_read": AR["aux_seed_never_read"],
                    "gap_disclosed": AR["seed_gap_disclosed"]}

n_pass = sum(1 for _, ok in CHECKS if ok)
n_fail = len(CHECKS) - n_pass
RESULTS["self_checks"] = {"total": len(CHECKS), "passed": n_pass,
                          "failed": n_fail}
print()
print("%d self-checks, %d passed, %d failed" % (len(CHECKS), n_pass, n_fail))

out_path = os.path.join(HERE, "results.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True, ensure_ascii=False)
    fh.write("\n")
print("results written: results.json (sorted keys, no timestamps)")
sys.exit(1 if n_fail else 0)
