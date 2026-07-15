#!/usr/bin/env python3
"""VERDICT 083 runner — the sample-window front-matter toll (idea-engine P070).

Hermetic: reads ONLY the fixtures.json beside this file. Zero repo/network
reads at verdict time. Every decision number is an exact Fraction.

Arms:
  A — seedless closed form C = q^(F+k) * 1[F+k <= B and k <= S] (decision-bearing)
  B — INDEPENDENTLY-WRITTEN brute unit-walk enumeration twin (exact-equal gated)
  R — seeded reader-trace MC at 3 cells, REPORTING-ONLY (no statistical gate)

Gates G1-G6 per the P070 registration; decision order REJECT -> INVALID ->
APPROVE -> NULL via twin independently-written evaluators.
"""

import json
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


def frac(s):
    return Fraction(s)


def fstr(x):
    return "%d/%d" % (x.numerator, x.denominator)


# ------------------------------------------------------- Arm A (closed form)
def ceil_frac_a(x):
    """Ceiling of a Fraction, Arm-A style: divmod on numerator/denominator."""
    d, m = divmod(x.numerator, x.denominator)
    return d + (1 if m else 0)


def budget_a(F, S, alpha):
    return ceil_frac_a(alpha * (F + S))


def conversion_a(F, S, alpha, q, k):
    """Closed form: C = q^(F+k) iff the k-th story unit is inside the budget."""
    B = budget_a(F, S, alpha)
    if k <= S and F + k <= B:
        return q ** (F + k)
    return Fraction(0)


# ------------------------------------------- Arm B (brute unit-walk twin)
def budget_b(F, S, alpha):
    """Ceiling via negated floor division — independent of Arm A's divmod."""
    return -((-alpha.numerator * (F + S)) // alpha.denominator)


def conversion_b(F, S, alpha, q, k):
    """Walk the truncated artifact unit by unit; never touches the closed form."""
    total = F + S
    B = budget_b(F, S, alpha)
    stop = B if B < total else total
    surv = Fraction(1)
    story_read = 0
    for pos in range(1, stop + 1):
        surv = surv * q  # the reader must survive reading this unit
        if pos > F:
            story_read += 1
            if story_read == k:
                return surv
    return Fraction(0)


# ------------------------------------------------------------- S* machinery
def sstar_closed(F, k, alpha):
    """min integer S with S >= k and alpha*(F+S) > F+k-1 (ceil(x) >= m iff x > m-1)."""
    T = Fraction(F + k - 1, 1) / alpha - F
    s = T.numerator // T.denominator + 1  # smallest integer strictly > T
    return max(s, k)


def sstar_scan(F, k, alpha, lo, hi):
    for S in range(lo, hi + 1):
        if S >= k and F + k <= budget_a(F, S, alpha):
            return S
    return None


# ------------------------------------------------------------------- grids
ALPHAS = [frac(a) for a in FIX["grids"]["alpha"]]
QS = [frac(q) for q in FIX["grids"]["q"]]
K_PROSE = FIX["grids"]["k_prose_screens"]
K_PB_SPREADS = FIX["grids"]["k_pb_spreads"]
DEC = FIX["grids"]["decision_cell"]
A_DEC = frac(DEC["alpha"])
Q_DEC = frac(DEC["q"])
K_DEC_PROSE = DEC["k_prose"]
K_DEC_PB_PAGES = 2 * DEC["k_pb_spreads"]

FORMATS = {}
for name, spec in FIX["formats"].items():
    FORMATS[name] = {"kind": spec["kind"], "S": spec["S"]}
check("fixture formats are the four committed ones",
      sorted(FORMATS) == ["EPISODE", "NOVELLA", "PB12", "PB15"])
check("NOVELLA S = ceil(27890/250) = 112",
      FORMATS["NOVELLA"]["S"] == -((-FIX["measured_constants"]["novella_words"]) // 250) == 112)
check("EPISODE S = ceil(8809/250) = 36",
      FORMATS["EPISODE"]["S"] == -((-FIX["measured_constants"]["episode_words"]) // 250) == 36)
check("PB15 S = 15 spreads x 2 = 30", FORMATS["PB15"]["S"] == 30)
check("PB12 S = 12 spreads x 2 = 24",
      FORMATS["PB12"]["S"] == 2 * FIX["measured_constants"]["dormouse_spreads"] == 24)


def policies(fmt):
    return FIX["policies"]["prose_F"] if FORMATS[fmt]["kind"] == "prose" \
        else FIX["policies"]["picture_book_F"]


def k_units(fmt, k_raw):
    """Hook in native units: screens for prose, pages (2/spread) for PB."""
    return k_raw if FORMATS[fmt]["kind"] == "prose" else 2 * k_raw


def k_grid(fmt):
    return K_PROSE if FORMATS[fmt]["kind"] == "prose" else K_PB_SPREADS


# --------------------------------------------------- full surfaces, both arms
surface_a = {}  # (fmt, alpha, k_raw, F, q) -> Fraction
surface_b = {}
geometry = {}   # (fmt, alpha, k_raw, F) -> dict(B, story_in_sample, margin, cliff)
knife_edges = []

for fmt, spec in FORMATS.items():
    S = spec["S"]
    for alpha in ALPHAS:
        for k_raw in k_grid(fmt):
            k = k_units(fmt, k_raw)
            for F in [0] + policies(fmt):  # F = 0 is the T1 reference (C2)
                Ba = budget_a(F, S, alpha)
                check("G1 budget twin (%s a=%s F=%d)" % (fmt, alpha, F),
                      Ba == budget_b(F, S, alpha))
                story = max(0, min(Ba - F, S))
                margin = Ba - F - k
                cliff = not (k <= S and F + k <= Ba)
                geometry[(fmt, alpha, k_raw, F)] = {
                    "B": Ba, "story_in_sample": story, "margin": margin, "cliff": cliff}
                if F > 0 and margin == 0 and not cliff:
                    knife_edges.append((fmt, str(alpha), k_raw, F))
                for q in QS:
                    ca = conversion_a(F, S, alpha, q, k)
                    cb = conversion_b(F, S, alpha, q, k)
                    surface_a[(fmt, alpha, k_raw, F, q)] = ca
                    surface_b[(fmt, alpha, k_raw, F, q)] = cb
                    check("G1 twin C (%s a=%s k=%d F=%d q=%s)" % (fmt, alpha, k_raw, F, q),
                          ca == cb)
                    check("cliff <=> C = 0 (%s a=%s k=%d F=%d q=%s)" % (fmt, alpha, k_raw, F, q),
                          (ca == 0) == cliff)

# ----------------------------------------------------------------- G2 (T1)
for fmt in FORMATS:
    for alpha in ALPHAS:
        for k_raw in k_grid(fmt):
            for q in QS:
                cells = [(F, surface_a[(fmt, alpha, k_raw, F, q)])
                         for F in [0] + policies(fmt)]
                alive = {F: c for F, c in cells if c != 0}
                if 0 in alive:
                    for F, c in alive.items():
                        check("G2 T1 C(F)/C(0) = q^F (%s a=%s k=%d q=%s F=%d)"
                              % (fmt, alpha, k_raw, q, F),
                              c / alive[0] == q ** F)
                Fs = sorted(alive)
                for i in range(len(Fs) - 1):
                    if Fs[i + 1] == Fs[i] + 1:
                        check("G2 T1 consecutive ratio = q (%s a=%s k=%d q=%s F=%d->%d)"
                              % (fmt, alpha, k_raw, q, Fs[i], Fs[i + 1]),
                              alive[Fs[i + 1]] / alive[Fs[i]] == q)

# ----------------------------------------------------------------- G3 (T2)
for fmt, spec in FORMATS.items():
    S = spec["S"]
    for alpha in ALPHAS:
        for k_raw in k_grid(fmt):
            k = k_units(fmt, k_raw)
            inds = []
            for F in range(0, 13):
                B = budget_a(F, S, alpha)
                inds.append(1 if (k <= S and F + k <= B) else 0)
            check("G3 T2 single-threshold flip in F (%s a=%s k=%d)" % (fmt, alpha, k_raw),
                  all(inds[i] >= inds[i + 1] for i in range(len(inds) - 1)))

lo, hi = FIX["grids"]["sstar_scan"]["S_range"]
for alpha in ALPHAS:
    for F in range(FIX["grids"]["sstar_scan"]["F_range"][0],
                   FIX["grids"]["sstar_scan"]["F_range"][1] + 1):
        for k in FIX["grids"]["sstar_scan"]["k_values"]:
            sc = sstar_closed(F, k, alpha)
            ss = sstar_scan(F, k, alpha, lo, hi)
            check("G3 S* formula = scan (a=%s F=%d k=%d)" % (alpha, F, k), sc == ss)
            if alpha == Fraction(1, 10):
                check("G3 S* = 9F + 10k - 9 (F=%d k=%d)" % (F, k),
                      sc == 9 * F + 10 * k - 9)

# ----------------------------------------------------------------- G4 (T3)
mix_support = [frac(s) for s in FIX["grids"]["mixture_T3"]["support"]]
mix_weights = [frac(w) for w in FIX["grids"]["mixture_T3"]["weights"]]


def surv_mix(n):
    return sum(w * (qv ** n) for w, qv in zip(mix_weights, mix_support))


for n in range(0, 30):
    check("G4 log-convexity n=%d" % n,
          surv_mix(n) * surv_mix(n + 2) > surv_mix(n + 1) ** 2)
for n in range(2, 30):
    check("G4 S(n) > S(1)^n n=%d" % n, surv_mix(n) > surv_mix(1) ** n)
depth = [surv_mix(n) / surv_mix(n + 3) for n in (1, 4, 8, 16)]
for i in range(len(depth) - 1):
    check("G4 depth-decreasing toll step %d" % i, depth[i] > depth[i + 1])

# ------------------------------------------------------------------ G5
g5 = FIX["hand_worlds_g5"]
S5, a5, k5, q5 = 10, Fraction(1, 2), 2, Fraction(1, 2)
c_f1 = conversion_a(1, S5, a5, q5, k5)
c_f5 = conversion_a(5, S5, a5, q5, k5)
check("G5 F=1 B=6", budget_a(1, S5, a5) == g5["F1"]["B"] == 6)
check("G5 F=1 C=1/8", c_f1 == frac(g5["F1"]["C"]) == Fraction(1, 8))
check("G5 F=5 B=8", budget_a(5, S5, a5) == g5["F5"]["B"] == 8)
check("G5 F=5 C=1/128", c_f5 == frac(g5["F5"]["C"]) == Fraction(1, 128))
check("G5 toll=16", c_f1 / c_f5 == frac(g5["toll"]) == 16)
check("G5 twin agrees", conversion_b(1, S5, a5, q5, k5) == c_f1
      and conversion_b(5, S5, a5, q5, k5) == c_f5)

# ------------------------------------------------------------------ G6
one = Fraction(1)
for fmt, spec in FORMATS.items():
    S = spec["S"]
    for alpha in ALPHAS:
        for k_raw in k_grid(fmt):
            k = k_units(fmt, k_raw)
            for F in policies(fmt):
                if F + k <= budget_a(F, S, alpha) and k <= S:
                    check("G6 q=1 => C=1 (%s a=%s k=%d F=%d)" % (fmt, alpha, k_raw, F),
                          conversion_a(F, S, alpha, one, k) == 1
                          and conversion_b(F, S, alpha, one, k) == 1)
            # alpha = 1: budget = whole artifact, no cliff with S >= k
            for F in policies(fmt):
                check("G6 alpha=1 no cliff (%s k=%d F=%d)" % (fmt, k_raw, F),
                      conversion_a(F, S, one, Q_DEC, k) != 0)
            # monotone non-increasing in F
            for q in QS:
                vals = [surface_a[(fmt, alpha, k_raw, F, q)] for F in [0] + policies(fmt)]
                check("G6 C monotone in F (%s a=%s k=%d q=%s)" % (fmt, alpha, k_raw, q),
                      all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1)))

# --- G6 census anchors (P070's own registered gating of the disclosed census)
AN = FIX["anchors_g6"]
k_pb_dec_raw = DEC["k_pb_spreads"]


def cell_a(fmt, F, q=Q_DEC, alpha=A_DEC):
    k_raw = K_DEC_PROSE if FORMATS[fmt]["kind"] == "prose" else k_pb_dec_raw
    return surface_a[(fmt, alpha, k_raw, F, q)]


def anchor(name, got, want, exact=True, places=4):
    if exact:
        ok = got == want
    else:
        ok = round(float(got), places) == round(float(want), places)
    if not check("G6 anchor %s" % name, ok):
        ANOMALIES.append("A%d: anchor %s — computed %s vs disclosed %s"
                         % (len(ANOMALIES) + 1, name, got, want))


c_nov_f1 = cell_a("NOVELLA", 1)
c_nov_f4 = cell_a("NOVELLA", 4)
toll_nov = c_nov_f1 / c_nov_f4
q4950 = Fraction(49, 50)
toll_q4950 = cell_a("NOVELLA", 1, q=q4950) / cell_a("NOVELLA", 4, q=q4950)
anchor("C(NOV,F=1)", c_nov_f1, frac(AN["C_NOV_F1"]))
anchor("C(NOV,F=4)", c_nov_f4, frac(AN["C_NOV_F4"]))
anchor("toll", toll_nov, frac(AN["toll_NOV"]))
anchor("toll@q=49/50", toll_q4950, frac(AN["toll_NOV_q4950"]))
anchor("S*(PB,F=2,k=1sp)", sstar_closed(2, 2, A_DEC), AN["sstar_pb_F2_k1spread"])
anchor("S*(PB,F=3,k=1sp)", sstar_closed(3, 2, A_DEC), AN["sstar_pb_F3_k1spread"])
anchor("S*(prose,F=1,k=3)", sstar_closed(1, 3, A_DEC), AN["sstar_prose_k3"]["F1"])
anchor("S*(prose,F=2,k=3)", sstar_closed(2, 3, A_DEC), AN["sstar_prose_k3"]["F2"])
anchor("S*(prose,F=4,k=3)", sstar_closed(4, 3, A_DEC), AN["sstar_prose_k3"]["F4"])

census = {}
for fmt in ("EPISODE", "PB15", "PB12", "NOVELLA"):
    k_raw = K_DEC_PROSE if FORMATS[fmt]["kind"] == "prose" else k_pb_dec_raw
    g = geometry[(fmt, A_DEC, k_raw, 4)]
    census[fmt] = g
    want = AN["cliff_census_decision_F4"][fmt]
    anchor("census %s B" % fmt, Fraction(g["B"]), Fraction(want["B"]))
    anchor("census %s story" % fmt, Fraction(g["story_in_sample"]),
           Fraction(want["story_in_sample"]))
    anchor("census %s cliff" % fmt, Fraction(int(g["cliff"])), Fraction(int(want["cliff"])))
cliff_count = sum(1 for g in census.values() if g["cliff"])
anchor("census count 3 of 4", Fraction(cliff_count), Fraction(3))

pb12_f2 = geometry[("PB12", A_DEC, k_pb_dec_raw, 2)]
anchor("PB12 F=2 B=3", Fraction(pb12_f2["B"]), Fraction(AN["PB12_legal_minimum"]["B"]))
anchor("PB12 F=2 story=1", Fraction(pb12_f2["story_in_sample"]),
       Fraction(AN["PB12_legal_minimum"]["story_in_sample"]))
anchor("PB12 F=2 cliff", Fraction(int(pb12_f2["cliff"])), Fraction(1))
anchor("PB12 cliff at every F", Fraction(int(all(
    geometry[("PB12", A_DEC, k_pb_dec_raw, F)]["cliff"] for F in (2, 3, 4)))), Fraction(1))

ep_f1 = geometry[("EPISODE", A_DEC, K_DEC_PROSE, 1)]
anchor("EPISODE F=1 B=4", Fraction(ep_f1["B"]), Fraction(AN["EPISODE_knife_edge"]["B"]))
anchor("EPISODE F=1 story=3", Fraction(ep_f1["story_in_sample"]), Fraction(3))
anchor("EPISODE F=1 margin=0", Fraction(ep_f1["margin"]), Fraction(0))
anchor("EPISODE F=1 survives", Fraction(int(not ep_f1["cliff"])), Fraction(1))
anchor("EPISODE cliffs from F=2", Fraction(int(all(
    geometry[("EPISODE", A_DEC, K_DEC_PROSE, F)]["cliff"] for F in (2, 3, 4)))), Fraction(1))

alpha_fifth = Fraction(1, 5)
fifth_clear = all(
    not geometry[(fmt, alpha_fifth,
                  K_DEC_PROSE if FORMATS[fmt]["kind"] == "prose" else k_pb_dec_raw, F)]["cliff"]
    for fmt in FORMATS for F in policies(fmt))
anchor("alpha=1/5 clears every committed format at every policy F",
       Fraction(int(fifth_clear)), Fraction(1))
anchor("T3 S(1)/S(4)", depth[0], Fraction(15019, 10000), exact=False)
anchor("T3 S(16)/S(19)", depth[-1], Fraction(10628, 10000), exact=False)

# ------------------------------------------------- knife-edge ledger (C5)
dec_clause_cells = [("NOVELLA", str(A_DEC), K_DEC_PROSE, 1),
                    ("NOVELLA", str(A_DEC), K_DEC_PROSE, 4),
                    ("EPISODE", str(A_DEC), K_DEC_PROSE, 4),
                    ("PB15", str(A_DEC), k_pb_dec_raw, 4),
                    ("PB12", str(A_DEC), k_pb_dec_raw, 4)]
knife_set = set(knife_edges)
check("C5 no decision clause rests on a margin-0 cell",
      not any(c in knife_set for c in dec_clause_cells))
check("C5 registered knife-edge instance present (EPISODE F=1 @ decision cell)",
      ("EPISODE", str(A_DEC), K_DEC_PROSE, 1) in knife_set)

# --------------------------------------------------------- decision (twins)
BANDS = {"toll_reject_min": Fraction(11, 10), "toll_approve_max": Fraction(21, 20),
         "cliff_reject_min": 3}


def evaluate_from_surface(surf):
    """Evaluator 1: reads a (fmt, alpha, k_raw, F, q) -> C surface."""
    def c(fmt, F, q=Q_DEC):
        k_raw = K_DEC_PROSE if FORMATS[fmt]["kind"] == "prose" else k_pb_dec_raw
        return surf[(fmt, A_DEC, k_raw, F, q)]
    cliffs = sum(1 for fmt in FORMATS if c(fmt, 4) == 0)
    toll = c("NOVELLA", 1) / c("NOVELLA", 4) if c("NOVELLA", 4) != 0 else None
    reject = cliffs >= BANDS["cliff_reject_min"] and toll is not None \
        and toll >= BANDS["toll_reject_min"]
    if reject:
        return "REJECT"
    if CHECKS["failed"]:
        return "INVALID"
    approve = cliffs == 0 and toll is not None and toll <= BANDS["toll_approve_max"]
    if approve:
        return "APPROVE"
    return "NULL"


def evaluate_recomputed():
    """Evaluator 2: recomputes its own numbers from Arm B, never reads Arm A."""
    cliffs = 0
    for fmt, spec in FORMATS.items():
        k = k_units(fmt, K_DEC_PROSE if spec["kind"] == "prose" else k_pb_dec_raw)
        if conversion_b(4, spec["S"], A_DEC, Q_DEC, k) == 0:
            cliffs += 1
    hi_c = conversion_b(1, FORMATS["NOVELLA"]["S"], A_DEC, Q_DEC, K_DEC_PROSE)
    lo_c = conversion_b(4, FORMATS["NOVELLA"]["S"], A_DEC, Q_DEC, K_DEC_PROSE)
    toll = hi_c / lo_c if lo_c != 0 else None
    if cliffs >= 3 and toll is not None and toll * 10 >= 11:
        return "REJECT"
    if CHECKS["failed"]:
        return "INVALID"
    if cliffs == 0 and toll is not None and toll * 20 <= 21:
        return "APPROVE"
    return "NULL"


# ------------------------------------------------------- Arm R (reporting)
SEED_REGISTRY = []


def make_rng(seed):
    SEED_REGISTRY.append(seed)
    return random.Random(seed)


def arm_r_leg(rng, fmt, F, n):
    spec = FORMATS[fmt]
    S = spec["S"]
    k = k_units(fmt, K_DEC_PROSE if spec["kind"] == "prose" else k_pb_dec_raw)
    B = budget_a(F, S, A_DEC)
    stop = min(B, F + S)
    qf = float(Q_DEC)
    conv = 0
    draws = 0
    for _ in range(n):
        story = 0
        for pos in range(1, stop + 1):
            draws += 1
            if rng.random() >= qf:
                break
            if pos > F:
                story += 1
                if story == k:
                    conv += 1
                    break
    return conv / n, draws


R = FIX["arm_r"]
cells_r = [(c["format"], c["F"]) for c in R["cells"]]
rng_main = make_rng(R["seed_main"])
rng_stab = make_rng(R["seed_stability"])
arm_r_rows = {}
for fmt, F in cells_r:
    c_hat, d = arm_r_leg(rng_main, fmt, F, R["n_main_traces"])
    arm_r_rows["main/%s-F%d" % (fmt, F)] = {
        "C_hat": repr(c_hat), "draws": d,
        "C_exact": fstr(cell_a(fmt, F)), "C_exact_float": repr(float(cell_a(fmt, F)))}
for fmt, F in cells_r:
    c_hat, d = arm_r_leg(rng_stab, fmt, F, R["n_stability_traces"])
    arm_r_rows["stability/%s-F%d" % (fmt, F)] = {
        "C_hat": repr(c_hat), "draws": d,
        "C_exact": fstr(cell_a(fmt, F)), "C_exact_float": repr(float(cell_a(fmt, F)))}
rng_pres = make_rng(R["seed_presentation"])
row_order = sorted(arm_r_rows)
rng_pres.shuffle(row_order)
check("C8 seed registry exact",
      SEED_REGISTRY == [R["seed_main"], R["seed_stability"], R["seed_presentation"]])
check("C8 aux seed never read", R["seed_aux_never_read"] not in SEED_REGISTRY)

# ---------------------------------------------------------------- rulings
ruling_1 = evaluate_from_surface(surface_a)
ruling_2 = evaluate_recomputed()
check("twin evaluators agree", ruling_1 == ruling_2)
RULING = ruling_1 if ruling_1 == ruling_2 else "INVALID"
if CHECKS["failed"]:
    RULING = "INVALID" if RULING not in ("REJECT",) else RULING
    # registered order: REJECT is evaluated before INVALID; a gate failure with
    # REJECT already fired is still reported in FAILURES below.

# ----------------------------------------------------------- publishable S*
sstar_tables = {}
for k in FIX["grids"]["sstar_scan"]["k_values"]:
    sstar_tables["k=%d" % k] = {
        "F=%d" % F: sstar_closed(F, k, A_DEC) for F in range(1, 6)}
publishability = {}
for fmt, spec in FORMATS.items():
    k = k_units(fmt, K_DEC_PROSE if spec["kind"] == "prose" else k_pb_dec_raw)
    publishability[fmt] = {
        "S": spec["S"],
        "S*_story_first": sstar_closed(1 if spec["kind"] == "prose" else 2, k, A_DEC),
        "S*_front_loaded": sstar_closed(4, k, A_DEC),
        "viable_story_first": spec["S"] >= sstar_closed(
            1 if spec["kind"] == "prose" else 2, k, A_DEC),
        "viable_front_loaded": spec["S"] >= sstar_closed(4, k, A_DEC)}

# ------------------------------------------------------------------ output
results = {
    "verdict": RULING,
    "evaluators": [ruling_1, ruling_2],
    "decision_cell": {
        "alpha": str(A_DEC), "q": str(Q_DEC), "k_prose_screens": K_DEC_PROSE,
        "k_pb_spreads": k_pb_dec_raw,
        "C_NOVELLA_F1": fstr(c_nov_f1), "C_NOVELLA_F1_float": repr(float(c_nov_f1)),
        "C_NOVELLA_F4": fstr(c_nov_f4), "C_NOVELLA_F4_float": repr(float(c_nov_f4)),
        "toll": fstr(toll_nov), "toll_float": repr(float(toll_nov)),
        "toll_at_q_49_50": fstr(toll_q4950), "toll_at_q_49_50_float": repr(float(toll_q4950)),
        "front_loaded_cliff_census": {f: dict(g) for f, g in census.items()},
        "front_loaded_cliff_count": cliff_count},
    "geometry": {
        "%s|a=%s|k=%d|F=%d" % kk: vv for kk, vv in sorted(
            ((k_[0], str(k_[1]), k_[2], k_[3]), v) for k_, v in geometry.items())},
    "conversion_surface": {
        "%s|a=%s|k=%d|F=%d|q=%s" % (f, a, kr, F, q): fstr(c)
        for (f, a, kr, F, q), c in sorted(
            ((f, str(a), kr, F, str(q)), c)
            for (f, a, kr, F, q), c in surface_a.items())},
    "sstar_tables_alpha_1_10": sstar_tables,
    "publishability_decision_hook": publishability,
    "knife_edge_ledger": ["%s|a=%s|k=%d|F=%d" % t for t in sorted(knife_edges)],
    "T3_mixture": {
        "S(1)": fstr(surv_mix(1)),
        "depth_toll_n_1_4_8_16": [fstr(d) for d in depth],
        "depth_toll_floats": [repr(float(d)) for d in depth]},
    "arm_r": {"row_order": row_order, "rows": arm_r_rows,
              "seed_registry": SEED_REGISTRY,
              "aux_never_read": R["seed_aux_never_read"]},
    "anomalies": ANOMALIES,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": FAILURES},
}
(HERE / "results.json").write_text(
    json.dumps(results, sort_keys=True, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8", newline="\n")

out = []
out.append("VERDICT 083 runner — sample-window front-matter toll (P070)")
out.append("ruling: %s (evaluators %s/%s)" % (RULING, ruling_1, ruling_2))
out.append("decision cell alpha=1/10, q=19/20, k*=3 screens / 1 spread:")
out.append("  C(NOVELLA, F=1) = %s ~ %s" % (fstr(c_nov_f1), float(c_nov_f1)))
out.append("  C(NOVELLA, F=4) = %s ~ %s" % (fstr(c_nov_f4), float(c_nov_f4)))
out.append("  toll = %s ~ %s (band 11/10)" % (fstr(toll_nov), float(toll_nov)))
out.append("  toll@q=49/50 = %s ~ %s (< 11/10: clause-(ii) witness)"
           % (fstr(toll_q4950), float(toll_q4950)))
out.append("  front-loaded cliff census (F=4): " + "  ".join(
    "%s: B=%d story=%d %s" % (f, g["B"], g["story_in_sample"],
                              "CLIFF" if g["cliff"] else "survives")
    for f, g in census.items()) + "  -> %d of 4" % cliff_count)
out.append("  PB12 legal-minimum F=2: B=%d story=%d CLIFF (hook needs 2) — "
           "under the cliff under ANY assembly" % (pb12_f2["B"], pb12_f2["story_in_sample"]))
out.append("  EPISODE F=1: B=4 story=3 margin=0 — named knife-edge, excluded, survives; "
           "cliffs from F=2")
out.append("S* @ alpha=1/10 (formula = scan, gated): " + json.dumps(sstar_tables))
out.append("publishability at the decision hook: " + json.dumps(
    publishability, sort_keys=True))
out.append("knife-edge ledger (margin-0 surviving cells, full grid): %s"
           % results["knife_edge_ledger"])
out.append("T3 depth toll S(n)/S(n+3), n=1/4/8/16: %s"
           % [round(float(d), 4) for d in depth])
out.append("arm R (reporting-only), published row order %s:" % row_order)
for key in row_order:
    r = arm_r_rows[key]
    out.append("  %s: C_hat=%s draws=%d beside exact %s ~ %s"
               % (key, r["C_hat"], r["draws"], r["C_exact"], r["C_exact_float"]))
out.append("anomalies vs disclosed landing: %s"
           % ("NONE" if not ANOMALIES else "; ".join(ANOMALIES)))
out.append("self-checks: %d passed, %d failed%s"
           % (CHECKS["passed"], CHECKS["failed"],
              "" if not FAILURES else " — " + "; ".join(FAILURES[:10])))
stdout_text = "\n".join(out) + "\n"
(HERE / "run-stdout.txt").write_text(stdout_text, encoding="utf-8", newline="\n")
sys.stdout.write(stdout_text)
sys.exit(0 if CHECKS["failed"] == 0 else 1)
