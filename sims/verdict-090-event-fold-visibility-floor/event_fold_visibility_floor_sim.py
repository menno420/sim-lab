#!/usr/bin/env python3
"""VERDICT 090 runner — the event-fold visibility floor (P077).

Prices idea-engine PROPOSAL 077: can the superbot-idle timed-events design
(docs/design/timed-events-scoping.md @ 884aeae) keep BOTH its committed
sentences — the piecewise-exact single-floor event fold
``x * E // 10^10`` with its graduation identity AND the "visibly richer
... in the exact T6 proportion" promise — on the committed lattice
(18 packs ship tier-1 base_rate 1)?

Three arms under the pre-registered discipline:

* **Arm A** — pure-integer lattice enumeration (seedless, exact,
  DECISION-bearing): the full 214,500-cell census, the T1 dead band, the
  staircase envelope by cross-multiplication (no floats anywhere), the
  three repair arms, the pencil worlds, the degeneracy controls.
* **Arm B** — INDEPENDENTLY-WRITTEN twin: a Fraction-based classifier
  (own nested loops, own factor order, ``fractions.Fraction`` + floor
  arithmetic — no shared fold code with Arm A) plus the closed-form
  staircase envelope; powers the second decision evaluator; exact-equal
  to Arm A through the FOUR typed must-equal contacts.
* **Arm R** — seeded window traces, REPORTING-ONLY, with the REGISTERED
  draw-order grammar (the V089 lesson applied by the drafter): seeds
  20261690/691/692, 10,000 traces each, 3 draws per trace; aux 20261693
  NEVER read; no statistical gate.

Hermetic: reads ONLY its sibling ``fixtures.json`` (committed before this
runner). Every fixture anchor is re-derived from scratch — a mismatch is
a first-class anomaly, never silently accepted. Exit contract: exit 0
iff every self-check passes; any failure exits 1 (INVALID).
"""

from __future__ import annotations

import itertools
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# battery scaffolding
# ---------------------------------------------------------------------------

PASSED = 0
FAILED = 0
FAILURES: list[str] = []


def check(name: str, cond: bool) -> bool:
    """One self-check: count it, remember failures, never raise."""
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        FAILURES.append(name)
    return cond


# anomaly census (disclosure-coverage convention, V087-V089): every
# disclosed anchor is compared and lands matched or mismatched; values the
# registration left unpinned are ledgered as vacancies, never match claims.
CENSUS_MATCHED: list[str] = []
CENSUS_MISMATCHED: list[str] = []
CENSUS_VACANT: list[str] = []


def compare(name: str, got: object, want: object) -> None:
    """Compare a re-derived value against a disclosed anchor (zero trust)."""
    if got == want:
        CENSUS_MATCHED.append(name)
    else:
        CENSUS_MISMATCHED.append(f"{name}: got {got!r}, disclosed {want!r}")
    check(f"anchor:{name}", got == want)


def vacant(name: str) -> None:
    CENSUS_VACANT.append(name)


# ---------------------------------------------------------------------------
# fixtures (the only input this runner ever reads)
# ---------------------------------------------------------------------------

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

check(
    "cpython minor pinned (registered battery line)",
    sys.version_info[:2] == tuple(int(p) for p in FIX["battery"]["cpython_pin"].split(".")),
)

EVENT_DEN = FIX["fold"]["event_denominator"]      # 10^10
TODAY_DEN = FIX["fold"]["today_denominator"]      # 10^8
GRID = tuple(FIX["event_grid"])                   # (110, 125, 150, 175, 200)
SWEEP_LO, SWEEP_HI = FIX["t1_all_e_sweep"]        # 101, 199
UP = FIX["economy_percents"]["upgrade_pct_per_level"]      # 25
PR = FIX["economy_percents"]["prestige_pct_per_unit"]      # 10
MS = FIX["economy_percents"]["milestone_pct_per_earned"]   # 5
BASES = tuple(FIX["lattice"]["base"])
COUNT_LO, COUNT_HI = FIX["lattice"]["count"]
L_LO, L_HI = FIX["lattice"]["upgrade_level"]
U_LO, U_HI = FIX["lattice"]["prestige_units"]
M_LO, M_HI = FIX["lattice"]["milestones"]
THEMES = tuple(FIX["theme_grid"])
G_MILLI = FIX["repair_arms"]["b_milli_ledger"]["G"]        # 1000
R_STAR = FIX["repair_arms"]["c_rate_floor"]["R_star"]      # 20
ANCH = FIX["f3_census_anchors"]

check("economy percents are the committed 25/10/5", (UP, PR, MS) == (25, 10, 5))
check("milestone rungs max is the committed 9", FIX["economy_percents"]["milestone_rungs_max"] == M_HI)
check(
    "base grid == committed base_rate value set {1, 5} ({1x18, 5x17} multiset, 0 balance blocks)",
    set(BASES) == {1, 5}
    and FIX["base_rate_multiset"]["1"] == 18
    and FIX["base_rate_multiset"]["5"] == 17
    and FIX["base_rate_multiset"]["balance_blocks"] == 0,
)


# ---------------------------------------------------------------------------
# Arm A — pure-integer lattice enumeration (seedless, exact, decision arm)
# ---------------------------------------------------------------------------

def pre_floor_product(b: int, c: int, L: int, u: int, m: int, t: int) -> int:
    """The committed six-factor pre-floor product x (all integer)."""
    return b * c * (100 + UP * L) * (100 + PR * u) * (100 + MS * m) * t


def rate_today(x: int) -> int:
    """engine.py's shipped single-floor fold (theme_pct included, // 10^8)."""
    return x // TODAY_DEN


def rate_event(x: int, e: int) -> int:
    """The doc's committed seventh-factor fold (event_pct inside, // 10^10)."""
    return x * e // EVENT_DEN


def frac_lt(a_num: int, a_den: int, b_num: int, b_den: int) -> bool:
    """a/b < c/d by cross-multiplication (positive denominators only)."""
    return a_num * b_den < b_num * a_den


def frac_str(num: int, den: int) -> str:
    """Reduced n/d string; whole ratios render bare (the registration's '1')."""
    g = math.gcd(num, den)
    num, den = num // g, den // g
    return str(num) if den == 1 else f"{num}/{den}"


LATTICE_AXES = (
    BASES,
    range(COUNT_LO, COUNT_HI + 1),
    range(L_LO, L_HI + 1),
    range(U_LO, U_HI + 1),
    range(M_LO, M_HI + 1),
    THEMES,
)

lattice_size = 0
alive_cells: list[tuple[int, int, int, int, int, int]] = []
alive_x: list[int] = []
alive_r0: list[int] = []
zero_cells: list[tuple[int, int, int, int, int, int]] = []
graduation_ok = True

for cell in itertools.product(*LATTICE_AXES):
    lattice_size += 1
    x = pre_floor_product(*cell)
    if (x * 100) // EVENT_DEN != x // TODAY_DEN:
        graduation_ok = False
    r0 = rate_today(x)
    if r0 >= 1:
        alive_cells.append(cell)
        alive_x.append(x)
        alive_r0.append(r0)
    else:
        zero_cells.append(cell)

# F1 identities
check("F1: graduation identity (x*100)//10^10 == x//10^8 on EVERY lattice cell", graduation_ok)
compare("lattice_size", lattice_size, ANCH["lattice_size"])
check("F1: size contact 214,500 = 2*25*13*11*10*3", lattice_size == 2 * 25 * 13 * 11 * 10 * 3)
compare("alive_count", len(alive_cells), ANCH["alive"])
compare("zero_rate_cell_count", len(zero_cells), ANCH["zero_rate_cell_count"])
compare(
    "zero_rate_cells_enumerated_by_name",
    [list(c) for c in zero_cells],
    FIX["lattice"]["zero_rate_cells"],
)

N_ALIVE = len(alive_cells)

# per-E census sweep (Arm A, integers only; ratios tracked by cross-mult)
dead_census_a: list[int] = []
dead_r20_a: list[int] = []
env_lo_hits: list[int] = []
env_hi_hits: list[int] = []
env_holds = True
max_ratio_a: dict[int, tuple[int, int, tuple[int, ...]]] = {}  # E -> (num, den, witness)
min_ratio_a: dict[int, tuple[int, int]] = {}
payers_at_200 = 0
e200_cert_ok = True

for e in GRID:
    dead = 0
    dead_r20 = 0
    lo_hits = 0
    hi_hits = 0
    best_n, best_d, best_cell = 0, 1, ()
    worst_n, worst_d = 0, 0  # unset sentinel
    for i in range(N_ALIVE):
        x = alive_x[i]
        r0 = alive_r0[i]
        re_ = x * e // EVENT_DEN
        if re_ == r0:
            dead += 1
            if r0 >= R_STAR:
                dead_r20 += 1
        # staircase envelope: floor(R*E/100) <= RE <= ceil((R+1)*E/100) - 1
        lo = r0 * e // 100
        hi = -((-(r0 + 1) * e) // 100) - 1
        if not (lo <= re_ <= hi):
            env_holds = False
        if re_ == lo:
            lo_hits += 1
        if re_ == hi:
            hi_hits += 1
        # realized/nominal = (RE/R0)/(E/100) = RE*100 / (R0*E)
        rn_num, rn_den = re_ * 100, r0 * e
        if frac_lt(best_n, best_d, rn_num, rn_den):
            best_n, best_d, best_cell = rn_num, rn_den, alive_cells[i]
        if worst_d == 0 or frac_lt(rn_num, rn_den, worst_n, worst_d):
            worst_n, worst_d = rn_num, rn_den
        if e == 200:
            if re_ > r0:
                payers_at_200 += 1
            if not (re_ >= 2 * r0 > r0):
                e200_cert_ok = False
    dead_census_a.append(dead)
    dead_r20_a.append(dead_r20)
    env_lo_hits.append(lo_hits)
    env_hi_hits.append(hi_hits)
    g = math.gcd(best_n, best_d)
    max_ratio_a[e] = (best_n // g, best_d // g, best_cell)
    g = math.gcd(worst_n, worst_d)
    min_ratio_a[e] = (worst_n // g, worst_d // g)

compare("dead_census_row", dead_census_a, ANCH["dead_census_row"])
compare("dead_at_rate_ge_20_row", dead_r20_a, ANCH["dead_at_rate_ge_20_row"])
check("F2/T2: e200 certificate floor(2r) >= 2*floor(r) > floor(r) on every alive cell", e200_cert_ok)
check("F2/T3: staircase envelope holds on every alive cell at every grid E", env_holds)
check(
    "F2/T3: BOTH envelope edges attained at every grid E",
    all(n > 0 for n in env_lo_hits) and all(n > 0 for n in env_hi_hits),
)
vacant("envelope edge-attainment counts per E (attainment registered as a boolean; counts undisclosed)")

jackpot_n, jackpot_d, jackpot_cell = max_ratio_a[110]
compare("jackpot_ratio_x110", f"{jackpot_n}/{jackpot_d}", ANCH["jackpot_ratio"])
check("F2/T3: jackpot witness is a rate-1 cell", rate_today(pre_floor_product(*jackpot_cell)) == 1)
witness = tuple(ANCH["jackpot_witness_cell"])
wx = pre_floor_product(*witness)
check(
    "F3: registered witness cell (1,1,0,2,8,110) attains the jackpot (rate 1 -> 2 at x1.10)",
    rate_today(wx) == 1 and rate_event(wx, 110) == 2
    and (rate_event(wx, 110) * 100 * jackpot_d == jackpot_n * rate_today(wx) * 110),
)
compare(
    "minimum_ratios_per_e",
    [frac_str(n, d) for (n, d) in (min_ratio_a[e] for e in GRID)],
    ANCH["minimum_ratios_per_e"],
)
compare("payers_at_x2_equals_alive (typed contact 4)", payers_at_200, len(alive_cells))
vacant("per-E realized/nominal MAXIMA beyond x1.10 (only the x1.10 jackpot 20/11 is disclosed; the other grid rows are reported in results.json)")

# T1 — the dead band on the canonical cell (cap-free, all-E sweep)
CANON = tuple(FIX["pencil_worlds"]["canonical_cell"])
cx = pre_floor_product(*CANON)
check("T1: canonical pre-floor product exactly 10^8", cx == 10**8)
check("T1: canonical committed rate exactly 1/s", rate_today(cx) == 1)
dead_e = [e for e in range(SWEEP_LO, SWEEP_HI + 1) if rate_event(cx, e) == rate_today(cx)]
compare("dead_e_count", len(dead_e), ANCH["dead_e_count"])
check("typed contact 1: dead-E count 99 == 199 - 101 + 1", len(dead_e) == SWEEP_HI - SWEEP_LO + 1 == 99)
first_paying = next(e for e in itertools.count(SWEEP_LO) if rate_event(cx, e) > rate_today(cx))
compare("first_paying_e", first_paying, ANCH["first_paying_e"])
check("margin ledger: first-paying contact is margin-0 (rate 1 -> 2 at E = 200)", rate_event(cx, 200) == 2)

one_up = (1, 1, 1, 0, 0, 100)
ox = pre_floor_product(*one_up)
check("T1: one-upgrade neighbour still dead at x1.50 (1.25*1.5 = 1.875 -> 1)", ox == 125_000_000 and rate_event(ox, 150) == 1 == rate_today(ox))
nb = (1, 1, 1, 0, 2, 100)
nx = pre_floor_product(*nb)
check(
    "T1: first x1.50-paying neighbour needs upgrade + two milestones (1.375*1.5 = 2.0625 -> 2)",
    nx == 137_500_000 and nx * 150 == 20_625_000_000 and rate_event(nx, 150) == 2 > rate_today(nx),
)

# T4 — the repair fork
# arm (a): V038's min-visible-delta floor
arm_a_re = max(rate_event(cx, 110), rate_today(cx) + 1)
arm_a_num, arm_a_den = arm_a_re * 100, rate_today(cx) * 110
g = math.gcd(arm_a_num, arm_a_den)
arm_a_ratio = (arm_a_num // g, arm_a_den // g)
compare("arm_a_overshoot_canonical_x110", f"{arm_a_ratio[0]}/{arm_a_ratio[1]}", ANCH["arm_a_overshoot_canonical_x110"])
check(
    "typed contact 2: arm (a) overshoot == x1.10 jackpot ratio, both 20/11",
    arm_a_ratio == (jackpot_n, jackpot_d) == (20, 11),
)

# arm (b): milli-granularity ledger G = 1000
milli_dead = 0
milli_min_delta_110 = None
for i in range(N_ALIVE):
    x = alive_x[i]
    r0m = x * G_MILLI // TODAY_DEN
    for e in GRID:
        rem = x * e * G_MILLI // EVENT_DEN
        if rem == r0m:
            milli_dead += 1
        if e == 110:
            d = rem - r0m
            if milli_min_delta_110 is None or d < milli_min_delta_110:
                milli_min_delta_110 = d
compare("arm_b_milli_census", milli_dead, ANCH["arm_b_milli_census"])
check(
    "arm (b) certificate: alive => x >= 10^8 => milli-delta at x1.10 >= 99",
    min(alive_x) >= TODAY_DEN and milli_min_delta_110 is not None and milli_min_delta_110 >= ANCH["arm_b_milli_certificate_bound"],
)
canon_milli_delta = cx * 110 * G_MILLI // EVENT_DEN - cx * G_MILLI // TODAY_DEN
compare("arm_b_milli_canonical_minimum", canon_milli_delta, ANCH["arm_b_milli_canonical_minimum"])
check("arm (b): the lattice x1.10 milli-delta minimum IS the canonical cell's 100", milli_min_delta_110 == canon_milli_delta)

# arm (c): rate-floor precondition R* = 20 — max deviation on R >= 20 cells
dev_n, dev_d = 0, 1  # max |realized/nominal - 1| tracked by cross-mult
dev_at: tuple[int, ...] = ()
for i in range(N_ALIVE):
    r0 = alive_r0[i]
    if r0 < R_STAR:
        continue
    x = alive_x[i]
    for e in GRID:
        re_ = x * e // EVENT_DEN
        num = abs(re_ * 100 - r0 * e)
        den = r0 * e
        if frac_lt(dev_n, dev_d, num, den):
            dev_n, dev_d = num, den
            dev_at = (e, r0)
g = math.gcd(dev_n, dev_d)
compare("arm_c_deviation_bound", f"{dev_n // g}/{dev_d // g}", ANCH["arm_c_deviation_bound"])
check("arm (c): deviation maximum attained at x1.10 on a rate-20 cell", dev_at == (110, 20))
check("arm (c): zero dead cells at rate >= 20 at any grid multiplier", all(v == 0 for v in dead_r20_a))

# T5 / F4 — pencil worlds: partition equivalence (closed form == tick loop)
FESTIVAL_S = FIX["pencil_worlds"]["festival_seconds"]
canon_extra = (rate_event(cx, 110) - rate_today(cx)) * FESTIVAL_S
compare("canonical_festival_extra_at_x110", canon_extra, FIX["pencil_worlds"]["canonical_festival_extra_at_x110"])
jx = pre_floor_product(*witness)
compare("jackpot_festival_extra_at_x110", (rate_event(jx, 110) - rate_today(jx)) * FESTIVAL_S, FIX["pencil_worlds"]["jackpot_festival_extra_at_x110"])

SEGMENTS = [(int(n), s) for n, s in FIX["pencil_worlds"]["calendar_segments"]]
CAL_CELLS = [tuple(c) for c in FIX["pencil_worlds"]["calendar_cells_sim_chosen"]]
vacant("pencil-calendar cell set (registered by COUNT 'four lattice cells' only; sim-chosen, disclosed in fixtures.json)")


def calendar_closed_form(x: int, e: int) -> int:
    return sum((rate_event(x, e) if s == "on" else rate_today(x)) * n for n, s in SEGMENTS)


def calendar_tick_loop(x: int, e: int) -> int:
    # the 1-second tick loop over the same absolute-time step function
    total = 0
    t = 0
    boundaries = []
    acc = 0
    for n, s in SEGMENTS:
        boundaries.append((acc, acc + n, s))
        acc += n
    for t in range(acc):
        seg = next(s for a, b, s in boundaries if a <= t < b)
        total += rate_event(x, e) if seg == "on" else rate_today(x)
    return total


calendar_equal = True
zero_delta_trace_seen = False
for c in CAL_CELLS:
    x = pre_floor_product(*c)
    for e in GRID:
        cf = calendar_closed_form(x, e)
        tl = calendar_tick_loop(x, e)
        if cf != tl:
            calendar_equal = False
        if c == CANON and e == 110 and rate_event(x, e) == rate_today(x):
            zero_delta_trace_seen = True
check("F4/T5: five-segment calendar closed-form == tick loop on four cells x all five grid E", calendar_equal)
check("F4/T5: the degenerate all-zero-delta trace is included (canonical at x1.10)", zero_delta_trace_seen)

# F5 — degeneracy / convention controls
# (i) theme-100 committed-packs sub-lattice (NULL axis i): non-flipping
sub_dead = []
for e in GRID:
    d = 0
    for i in range(N_ALIVE):
        if alive_cells[i][5] == 100 and alive_x[i] * e // EVENT_DEN == alive_r0[i]:
            d += 1
    sub_dead.append(d)
check(
    "F5(i): theme-100 sub-lattice non-flipping — canonical (a theme-100 cell) dead at four grid E, paying at x2.00",
    all(rate_event(cx, e) == rate_today(cx) for e in GRID[:4]) and rate_event(cx, 200) > rate_today(cx),
)
check("F5(i): deadness persists on the committed-packs sub-lattice (dead census > 0 below x2.00, 0 at x2.00)",
      all(d > 0 for d in sub_dead[:4]) and sub_dead[4] == 0)
vacant("theme-100 sub-lattice dead-census values (axis registered as non-flipping; values undisclosed — reported in results.json)")

# (ii) axis-cap bump (NULL axis ii): count/L/u one notch up; R1/R3 must not flip
bump_axes = (
    BASES,
    range(COUNT_LO, COUNT_HI + 2),
    range(L_LO, L_HI + 2),
    range(U_LO, U_HI + 2),
    range(M_LO, M_HI + 1),
    THEMES,
)
bump_dev_n, bump_dev_d = 0, 1
bump_milli_dead = 0
bump_dead_r20 = 0
for cell in itertools.product(*bump_axes):
    x = pre_floor_product(*cell)
    r0 = x // TODAY_DEN
    if r0 < 1:
        continue
    r0m = x * G_MILLI // TODAY_DEN
    for e in GRID:
        re_ = x * e // EVENT_DEN
        if x * e * G_MILLI // EVENT_DEN == r0m:
            bump_milli_dead += 1
        if r0 >= R_STAR:
            if re_ == r0:
                bump_dead_r20 += 1
            num = abs(re_ * 100 - r0 * e)
            den = r0 * e
            if frac_lt(bump_dev_n, bump_dev_d, num, den):
                bump_dev_n, bump_dev_d = num, den
g = math.gcd(bump_dev_n, bump_dev_d)
check(
    "F5(ii): cap-bump (26/13/11) non-flipping — R1 cap-free (canonical unchanged), arm (c) deviation still exactly 1/22, arm (b) census still 0, dead-at-R>=20 still 0",
    (bump_dev_n // g, bump_dev_d // g) == (1, 22) and bump_milli_dead == 0 and bump_dead_r20 == 0,
)

# E = 100 neutrality (the graduation identity restated on the alive list)
check("F5: E = 100 neutrality — event delta identically 0 on every alive cell",
      all(alive_x[i] * 100 // EVENT_DEN == alive_r0[i] for i in range(N_ALIVE)))

# named alt-fold control (REPORTING-ONLY, sim-chosen value — vacancy)
alt_dead_110 = 0
for i in range(N_ALIVE):
    ab, ac, aL, au, am, at_ = alive_cells[i]
    per_unit = ab * (100 + UP * aL) * (100 + PR * au) * (100 + MS * am) * at_
    alt_r0 = ac * (per_unit // TODAY_DEN)           # per-unit floor, count OUTSIDE
    alt_re = ac * (per_unit * 110 // EVENT_DEN)
    if alt_re == alt_r0:
        alt_dead_110 += 1
vacant("alt-fold (count OUTSIDE the floor) x1.10 dead census (control registered by NAME only; reporting)")
check("F5: alt-fold control is a DIFFERENT world (its x1.10 dead census differs from the committed fold's)",
      alt_dead_110 != dead_census_a[0])

# ---------------------------------------------------------------------------
# Arm B — independently-written Fraction classifier + closed-form envelope
# ---------------------------------------------------------------------------

def b_upgrade_pct(level: int) -> int:
    return 100 + 25 * level


def b_prestige_pct(units: int) -> int:
    return 100 + 10 * units


def b_milestone_pct(earned: int) -> int:
    return 100 + 5 * earned


def b_rate_fraction(b: int, c: int, L: int, u: int, m: int, t: int) -> Fraction:
    """The exact pre-floor rate as a rational: x / 10^8, built factor-wise."""
    f = Fraction(b) * c
    f *= Fraction(b_upgrade_pct(L), 100)
    f *= Fraction(b_prestige_pct(u), 100)
    f *= Fraction(b_milestone_pct(m), 100)
    f *= Fraction(t, 100)
    return f


b_dead_census: list[int] = [0 for _ in GRID]
b_alive = 0
b_env_ok = True
b_max_ratio: dict[int, Fraction] = {e: Fraction(0) for e in GRID}
b_min_ratio: dict[int, Fraction] = {}
b_dev_max = Fraction(0)
b_payers_200 = 0
ONE = Fraction(1)
NOMINAL = {e: Fraction(e, 100) for e in GRID}
_env_cache: dict[tuple[int, int], tuple[int, int]] = {}


def b_envelope(r0: int, e: int) -> tuple[int, int]:
    """Closed-form staircase envelope bounds for an integer rate r0 (Fractions)."""
    key = (r0, e)
    if key not in _env_cache:
        lo = math.floor(Fraction(r0) * NOMINAL[e])
        hi = math.ceil(Fraction(r0 + 1) * NOMINAL[e]) - 1
        _env_cache[key] = (lo, hi)
    return _env_cache[key]


for t in THEMES:  # deliberately different loop nesting than Arm A
    for m in range(M_LO, M_HI + 1):
        for u in range(U_LO, U_HI + 1):
            for L in range(L_LO, L_HI + 1):
                for c in range(COUNT_LO, COUNT_HI + 1):
                    for b in BASES:
                        r = b_rate_fraction(b, c, L, u, m, t)
                        r0 = math.floor(r)
                        if r0 < 1:
                            continue
                        b_alive += 1
                        for gi, e in enumerate(GRID):
                            q = r * NOMINAL[e]
                            re_ = q.numerator // q.denominator
                            if re_ == r0:
                                b_dead_census[gi] += 1
                            lo, hi = b_envelope(r0, e)
                            if not (lo <= re_ <= hi):
                                b_env_ok = False
                            ratio = Fraction(re_ * 100, r0 * e)
                            if ratio > b_max_ratio[e]:
                                b_max_ratio[e] = ratio
                            if e not in b_min_ratio or ratio < b_min_ratio[e]:
                                b_min_ratio[e] = ratio
                            if r0 >= 20:
                                dev = abs(ratio - ONE)
                                if dev > b_dev_max:
                                    b_dev_max = dev
                            if e == 200 and re_ > r0:
                                b_payers_200 += 1

check("Arm B: alive count == Arm A's (twin lattice walk)", b_alive == len(alive_cells))
check(
    "typed contact 3: x1.10 dead census — Arm A integer == Arm B Fraction classifier",
    b_dead_census[0] == dead_census_a[0],
)
check("Arm B: dead-census row exact-equal to Arm A on every grid E", b_dead_census == dead_census_a)
check("Arm B: closed-form staircase envelope holds (Fraction form)", b_env_ok)
check("Arm B: jackpot maximum == 20/11 at x1.10", b_max_ratio[110] == Fraction(20, 11))
check(
    "Arm B: per-E maxima/minima agree exactly with Arm A's cross-multiplied extremes",
    all(b_max_ratio[e] == Fraction(max_ratio_a[e][0], max_ratio_a[e][1]) for e in GRID)
    and all(b_min_ratio[e] == Fraction(*min_ratio_a[e]) for e in GRID),
)
check("Arm B: arm (c) deviation maximum == 1/22", b_dev_max == Fraction(1, 22))
check("Arm B: payers-at-x2.00 == Arm A's (typed contact 4, twin side)", b_payers_200 == payers_at_200)

# ---------------------------------------------------------------------------
# Arm R — seeded window traces, REPORTING-ONLY (registered draw grammar)
# ---------------------------------------------------------------------------

ARM_R = FIX["arm_r"]
TRACES = ARM_R["traces_per_seed"]
SEEDS = ARM_R["seeds_reporting_only"]
AUX_SEED = ARM_R["aux_seed_never_read"]
SEEDS_READ: set[int] = set()


def run_trace_set(seed: int) -> tuple[int, int, int]:
    """(dead_traces, total_extra_units, draws) under the REGISTERED grammar."""
    SEEDS_READ.add(seed)
    rng = random.Random(seed)  # one Random per trace set (registered)
    dead = 0
    extra = 0
    draws = 0
    for _ in range(TRACES):
        i = rng.randrange(N_ALIVE)          # draw 1: alive-cell index
        e = GRID[rng.randrange(len(GRID))]  # draw 2: E uniform over the grid tuple
        w = rng.randint(600, 86400)         # draw 3: window length, inclusive
        draws += 3
        x = alive_x[i]
        delta = x * e // EVENT_DEN - alive_r0[i]
        if delta == 0:
            dead += 1
        extra += delta * w
    return dead, extra, draws


arm_r_rows = {}
for seed in SEEDS:
    d1 = run_trace_set(seed)
    d2 = run_trace_set(seed)  # determinism sentinel: each seed reproduces itself
    check(f"Arm R: seed {seed} reproduces itself in-process", d1 == d2)
    check(f"Arm R: seed {seed} draw-count sentinel {ARM_R['draw_count_sentinel_per_seed']}", d1[2] == ARM_R["draw_count_sentinel_per_seed"])
    preview = ARM_R["disclosed_previews"][str(seed)]
    compare(f"arm_r_preview_{seed}", [d1[0], d1[1]], [preview["dead_traces"], preview["total_extra_units"]])
    arm_r_rows[str(seed)] = {"dead_traces": d1[0], "total_extra_units": d1[1], "draws": d1[2]}

check("Arm R: aux seed 20261693 NEVER read by any leg", AUX_SEED not in SEEDS_READ and SEEDS_READ == set(SEEDS))

# ---------------------------------------------------------------------------
# margin ledger (typed: every registered cell an exact equality/zero/saturation)
# ---------------------------------------------------------------------------

margin_ledger = {
    "first_paying_e_contact_margin0": first_paying == 200 and rate_event(cx, 200) - rate_today(cx) == 1,
    "dead_band_saturated_99_of_99": len(dead_e) == 99 == SWEEP_HI - SWEEP_LO + 1,
    "e200_census_zero_cell_certified": dead_census_a[4] == 0 and e200_cert_ok,
    "jackpot_equality_20_11": (jackpot_n, jackpot_d) == (20, 11),
    "overshoot_equals_jackpot": arm_a_ratio == (jackpot_n, jackpot_d),
    "deviation_equality_1_22": (dev_n // math.gcd(dev_n, dev_d), dev_d // math.gcd(dev_n, dev_d)) == (1, 22),
    "milli_minimum_exactly_100": canon_milli_delta == 100 and milli_min_delta_110 == 100,
    "payers_at_x2_equals_alive_saturated": payers_at_200 == len(alive_cells),
}
for k, v in margin_ledger.items():
    check(f"margin ledger: {k}", v)

# ---------------------------------------------------------------------------
# decision evaluators (twin, independently computed inputs; REJECT first)
# ---------------------------------------------------------------------------

def evaluate_a() -> str:
    r1 = (
        len(dead_e) == 99
        and first_paying == 200
        and rate_event(ox, 150) == rate_today(ox)
    )
    r2 = (
        dead_census_a == [4151, 675, 56, 14, 0]
        and (jackpot_n, jackpot_d) == (20, 11)
        and rate_today(pre_floor_product(*jackpot_cell)) == 1
        and env_holds
        and all(n > 0 for n in env_lo_hits)
        and all(n > 0 for n in env_hi_hits)
    )
    r3 = (
        arm_a_ratio == (20, 11)
        and milli_dead == 0
        and milli_min_delta_110 >= 99
        and (dev_n * 22 == dev_d)
        and all(v == 0 for v in dead_r20_a)
    )
    if r1 and r2 and r3:
        return "REJECT"
    if FAILED:
        return "INVALID"
    approve = all(d == 0 for d in dead_census_a) and all(
        Fraction(20, 21) <= Fraction(min_ratio_a[e][0], min_ratio_a[e][1])
        and Fraction(max_ratio_a[e][0], max_ratio_a[e][1]) <= Fraction(21, 20)
        for e in GRID
    )
    if approve:
        return "APPROVE"
    return "NULL"


def evaluate_b() -> str:
    r1 = (
        all(math.floor(b_rate_fraction(*CANON) * Fraction(e, 100)) == 1 for e in range(101, 200))
        and math.floor(b_rate_fraction(*CANON) * Fraction(200, 100)) == 2
        and math.floor(b_rate_fraction(1, 1, 1, 0, 0, 100) * Fraction(150, 100)) == 1
    )
    r2 = (
        b_dead_census == [4151, 675, 56, 14, 0]
        and b_max_ratio[110] == Fraction(20, 11)
        and b_env_ok
    )
    canon_r = b_rate_fraction(*CANON)
    canon_r0 = math.floor(canon_r)
    canon_re_110 = math.floor(canon_r * Fraction(110, 100))
    arm_a_b_side = max(canon_re_110, canon_r0 + 1)  # V038's min-delta floor, B-computed
    r3 = (
        Fraction(arm_a_b_side * 100, canon_r0 * 110) == Fraction(20, 11)
        and milli_dead == 0
        and b_dev_max == Fraction(1, 22)
    )
    if r1 and r2 and r3:
        return "REJECT"
    if FAILED:
        return "INVALID"
    if all(d == 0 for d in b_dead_census) and all(
        Fraction(20, 21) <= b_min_ratio[e] and b_max_ratio[e] <= Fraction(21, 20) for e in GRID
    ):
        return "APPROVE"
    return "NULL"


verdict_a = evaluate_a()
verdict_b = evaluate_b()
check("twin decision evaluators agree", verdict_a == verdict_b)
check("APPROVE and REJECT mutually exclusive by arithmetic (dead census both 0 and 4,151 impossible)",
      not (verdict_a == "REJECT" and all(d == 0 for d in dead_census_a)))
ruling = verdict_a if verdict_a == verdict_b else "INVALID"
if FAILED:
    ruling = "INVALID"

# ---------------------------------------------------------------------------
# results + stdout (canonical, timestamp-free)
# ---------------------------------------------------------------------------

results = {
    "verdict": ruling,
    "evaluators": {"arm_a": verdict_a, "arm_b": verdict_b},
    "lattice": {
        "size": lattice_size,
        "alive": len(alive_cells),
        "zero_rate_cells": [list(c) for c in zero_cells],
    },
    "t1_dead_band": {
        "canonical_cell": list(CANON),
        "pre_floor_product": cx,
        "rate_today": rate_today(cx),
        "dead_e_count": len(dead_e),
        "dead_e_range": [dead_e[0], dead_e[-1]],
        "first_paying_e": first_paying,
        "one_upgrade_dead_at_150": rate_event(ox, 150) == rate_today(ox),
        "first_paying_neighbour": {"cell": list(nb), "x": nx, "x_times_150": nx * 150, "rate_during": rate_event(nx, 150)},
        "festival_3600s_extra_at_x110": canon_extra,
    },
    "t2_census": {
        "grid": list(GRID),
        "dead_census_row": dead_census_a,
        "dead_at_rate_ge_20_row": dead_r20_a,
        "theme_100_sublattice_dead_row": sub_dead,
        "alt_fold_control_dead_x110_reporting": alt_dead_110,
    },
    "t3_jackpot": {
        "max_ratio_per_e": {str(e): frac_str(max_ratio_a[e][0], max_ratio_a[e][1]) for e in GRID},
        "max_ratio_witness_x110": list(jackpot_cell),
        "min_ratio_per_e": {str(e): frac_str(*min_ratio_a[e]) for e in GRID},
        "envelope_holds": env_holds,
        "envelope_lo_edge_hits_per_e": env_lo_hits,
        "envelope_hi_edge_hits_per_e": env_hi_hits,
        "jackpot_festival_extra_3600s": (rate_event(jx, 110) - rate_today(jx)) * FESTIVAL_S,
    },
    "t4_repair_fork": {
        "arm_a_overshoot_canonical_x110": f"{arm_a_ratio[0]}/{arm_a_ratio[1]}",
        "arm_b_milli_census_lattice_x_grid": milli_dead,
        "arm_b_milli_min_delta_x110": milli_min_delta_110,
        "arm_b_milli_canonical_delta_x110": canon_milli_delta,
        "arm_c_deviation_max": f"{dev_n // math.gcd(dev_n, dev_d)}/{dev_d // math.gcd(dev_n, dev_d)}",
        "arm_c_deviation_attained_at": list(dev_at),
    },
    "t5_partition_equivalence": {
        "calendar_segments": [[n, s] for n, s in SEGMENTS],
        "cells": [list(c) for c in CAL_CELLS],
        "closed_form_equals_tick_loop": calendar_equal,
        "degenerate_zero_delta_trace_included": zero_delta_trace_seen,
    },
    "cap_bump_control": {
        "arm_c_deviation_max": f"{bump_dev_n // math.gcd(bump_dev_n, bump_dev_d)}/{bump_dev_d // math.gcd(bump_dev_n, bump_dev_d)}",
        "arm_b_milli_census": bump_milli_dead,
        "dead_at_rate_ge_20": bump_dead_r20,
    },
    "arm_r_reporting_only": arm_r_rows,
    "typed_contacts": {
        "contact_1_dead_e_99": len(dead_e) == 99 == SWEEP_HI - SWEEP_LO + 1,
        "contact_2_overshoot_equals_jackpot_20_11": arm_a_ratio == (jackpot_n, jackpot_d) == (20, 11),
        "contact_3_dead_census_x110_a_equals_b": [dead_census_a[0], b_dead_census[0]],
        "contact_4_payers_at_x2_equals_alive": [payers_at_200, len(alive_cells)],
    },
    "margin_ledger": margin_ledger,
    "anomaly_census": {
        "compared_and_matched": len(CENSUS_MATCHED),
        "compared_and_mismatched": CENSUS_MISMATCHED,
        "vacant": CENSUS_VACANT,
    },
    "seed_registry": {
        "reporting_only": SEEDS,
        "aux_never_read": AUX_SEED,
        "seeds_read": sorted(SEEDS_READ),
    },
    "self_checks": {"passed": PASSED, "failed": FAILED, "failures": FAILURES},
}

out = json.dumps(results, indent=2, sort_keys=True) + "\n"
(HERE / "results.json").write_text(out, encoding="utf-8")

print("VERDICT 090 runner — the event-fold visibility floor (P077)")
print(f"ruling: {ruling} (evaluators {verdict_a}/{verdict_b})")
print(
    f"T1 dead band: canonical x = {cx}, rate {rate_today(cx)}/s; delta = 0 for {len(dead_e)}/99 integer E in 101..199; "
    f"first paying E = {first_paying} (rate 1 -> {rate_event(cx, 200)}); one-upgrade dead at x1.50: {rate_event(ox, 150) == 1}; "
    f"first paying neighbour 1.375*1.5 = 2.0625 -> {rate_event(nx, 150)}"
)
print(
    f"T2 census: lattice {lattice_size} = 2*25*13*11*10*3, alive {len(alive_cells)}, zero-rate cells {len(zero_cells)} "
    f"{[list(c) for c in zero_cells]}"
)
print(f"  dead row {dead_census_a} over E {list(GRID)}; dead at rate >= 20: {dead_r20_a}; theme-100 sub-lattice {sub_dead}")
print(
    f"T3 jackpot: max realized/nominal at x1.10 = {jackpot_n}/{jackpot_d} at cell {list(jackpot_cell)} (rate 1 -> 2); "
    f"minima per E {[frac_str(n, d) for (n, d) in (min_ratio_a[e] for e in GRID)]}; envelope holds: {env_holds}, "
    f"both edges attained at every E: {all(n > 0 for n in env_lo_hits) and all(n > 0 for n in env_hi_hits)}"
)
print(
    f"T4 repair fork: arm (a) overshoot {arm_a_ratio[0]}/{arm_a_ratio[1]} == jackpot; "
    f"arm (b) milli census {milli_dead} (min delta {milli_min_delta_110}, canonical {canon_milli_delta}); "
    f"arm (c) deviation {dev_n // math.gcd(dev_n, dev_d)}/{dev_d // math.gcd(dev_n, dev_d)} at {list(dev_at)}"
)
print(
    f"T5 partition equivalence: closed form == tick loop on {len(CAL_CELLS)} cells x {len(GRID)} E: {calendar_equal} "
    f"(degenerate zero-delta trace included: {zero_delta_trace_seen}); festival 3600 s pays canonical {canon_extra}, jackpot 3600"
)
print(
    f"controls: E = 100 neutral; cap-bump non-flip (dev {bump_dev_n // math.gcd(bump_dev_n, bump_dev_d)}/"
    f"{bump_dev_d // math.gcd(bump_dev_n, bump_dev_d)}, milli {bump_milli_dead}, dead-R>=20 {bump_dead_r20}); "
    f"alt-fold control dead census at x1.10 = {alt_dead_110} (reporting, named control)"
)
for seed in SEEDS:
    row = arm_r_rows[str(seed)]
    print(
        f"arm R (reporting-only): seed {seed} N={TRACES} draws={row['draws']} | dead traces {row['dead_traces']} | "
        f"total extra units {row['total_extra_units']}"
    )
print(f"typed contacts: 99 = 199-101+1 | overshoot == jackpot == 20/11 | dead census x1.10 A == B == {dead_census_a[0]} | payers at x2 == alive == {payers_at_200}")
print(f"margin ledger: {margin_ledger}")
print(
    f"anomaly census (disclosure coverage): {len(CENSUS_MATCHED)} compared-and-matched, "
    f"{len(CENSUS_MISMATCHED)} mismatched, {len(CENSUS_VACANT)} vacant"
)
print(f"anomalies: {'none' if not CENSUS_MISMATCHED else CENSUS_MISMATCHED}")
print(f"self-checks: {PASSED} passed, {FAILED} failed")
if FAILED:
    for f in FAILURES:
        print(f"  FAILED: {f}")
sys.exit(0 if FAILED == 0 else 1)
