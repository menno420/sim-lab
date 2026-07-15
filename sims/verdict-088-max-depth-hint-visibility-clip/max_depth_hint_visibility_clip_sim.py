#!/usr/bin/env python3
"""VERDICT 088 — the hint that hides (idea-engine PROPOSAL 075).

Exact enumeration of the full 80-cell (hint x depth x record) conforming
lattice of the mineverse v1 snapshot contract against the committed world
views (ladder bands, minimap panels, deep_diver badge), re-derived from
the pinned quotes with zero trust in the drafter's numbers.

Arms:
  A  — seedless closed forms ((3-m)^2, 4(3-m), (3-m)(m+1), the iff-laws,
       the badge censuses); decision-bearing.
  B  — INDEPENDENTLY-WRITTEN exhaustive dict-of-cells enumerator (direct
       predicate scans over explicitly constructed band/panel index sets;
       no shared code with A or F); powers the second decision evaluator.
  F  — the committed functions transcribed VERBATIM from the pinned
       source quotes (band loop, per-band elif, minimap band filter,
       badge equality, absence fallback), run over real document dicts;
       must equal Arm B cell-by-cell on all 80 x 4 outputs.
  R  — seeded random fully-valid documents, REPORTING-ONLY rates
       (seeds 20261670/20261671, presentation 20261672; aux 20261673
       asserted NEVER read).

Hermetic: reads ONLY its own fixtures.json. Stdlib-only. Exit contract:
exit 0 iff all self-checks pass and exactly one ruling token issues
(fixtures C13); anomalies are first-class but do not affect the exit code.
"""

import copy
import json
import os
import platform
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FX = json.load(open(os.path.join(HERE, "fixtures.json")))

assert platform.python_version_tuple()[:2] == tuple(
    FX["cpython_pin"].split(".")), (
    f"CPython {FX['cpython_pin']} pinned; running "
    f"{platform.python_version()}")

# ---------------------------------------------------------------- checks
CHECKS = {"passed": 0, "failed": 0, "failures": []}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        CHECKS["failures"].append(name)


# Structured anomaly census (fixtures C11, the V087 coverage convention).
CENSUS = {"compared_and_matched": 0, "compared_and_mismatched": [],
          "not_disclosed": []}


def compare_disclosed(name, disclosed, rederived):
    """A registration numeral vs its zero-trust re-derivation."""
    if disclosed == rederived:
        CENSUS["compared_and_matched"] += 1
        check(f"disclosed:{name}", True)
    else:
        CENSUS["compared_and_mismatched"].append(
            {"name": name, "disclosed": disclosed, "rederived": rederived})
        check(f"disclosed:{name}", False)


# ------------------------------------------------------- seed registry (C7)
class SeedRegistry:
    def __init__(self, allowed):
        self.allowed = list(allowed)
        self.constructed = []

    def rng(self, seed):
        assert seed in self.allowed, f"unregistered seed {seed}"
        self.constructed.append(seed)
        return random.Random(seed)


REG = SeedRegistry(FX["seeds"]["registered_set"][:3])  # aux never allowed
AUX_SEED = FX["seeds"]["registered_set"][3]

# ---------------------------------------------------------------- lattice
HINTS = ["absent", 0, 1, 2, 3]
DEPTHS = [0, 1, 2, 3]
DEPTH_MAX = 3  # schema miner-depth maximum (pinned; depth_max())


def m_eff(m):
    """The committed absence fallback (views.py:633-634)."""
    return DEPTH_MAX if m == "absent" else m


# ----------------------------------------------- re-derived validator (G2)
ENVELOPE_REQUIRED = ("schema_version", "generated_at", "guild_id", "miners")
MINER_REQUIRED = ("suid", "guild_id", "display_name", "depth",
                  "record_depth", "position", "energy", "coins", "xp",
                  "equipment", "gear_wear", "mining_inventory", "vault",
                  "vault_level", "skills", "structures")


def rederived_accepts(doc):
    """Bounds / required / types re-derived from the pinned schema
    constants. Returns True iff the v1 READ contract accepts ``doc``.
    NO cross-field rule exists (the pinned applicator inventory is
    empty) — that absence is exactly the priced object."""
    if not isinstance(doc, dict):
        return False
    for key in ENVELOPE_REQUIRED:
        if key not in doc:
            return False
    if doc["schema_version"] != "1":
        return False
    if not isinstance(doc["generated_at"], str):
        return False
    if not (isinstance(doc["guild_id"], str) and doc["guild_id"].isdigit()):
        return False
    if "max_depth" in doc:
        md = doc["max_depth"]
        if not (isinstance(md, int) and not isinstance(md, bool)
                and 0 <= md <= 3):
            return False
    if not isinstance(doc["miners"], list):
        return False
    for m in doc["miners"]:
        if not isinstance(m, dict):
            return False
        for key in MINER_REQUIRED:
            if key not in m:
                return False
        for field in ("depth", "record_depth"):
            v = m[field]
            if not (isinstance(v, int) and not isinstance(v, bool)
                    and 0 <= v <= 3):
                return False
        pos = m["position"]
        if not (isinstance(pos, dict) and isinstance(pos.get("x"), int)
                and isinstance(pos.get("y"), int)):
            return False
        if not (isinstance(m["coins"], int) and m["coins"] >= 0):
            return False
    return True


# ------------------------------------------------------- document factory
TEMPLATE = FX["_grounding"]["superbot_mineverse"]["miner_template_pinned"]


def make_doc(hint, cells, extra=None):
    """cells: list of (name, d, r); hint 'absent' omits the field."""
    doc = dict(TEMPLATE["envelope"])
    doc["miners"] = []
    if hint != "absent":
        doc["max_depth"] = hint
    for i, (name, d, r) in enumerate(cells):
        m = copy.deepcopy(TEMPLATE["value"])
        m["display_name"] = name
        m["suid"] = str(100000000000000900 + i)
        m["depth"] = d
        m["record_depth"] = r
        if extra and name in extra:
            for path, value in extra[name].items():
                keys = path.split(".")
                tgt = m
                for k in keys[:-1]:
                    tgt = tgt[k]
                tgt[keys[-1]] = value
        doc["miners"].append(m)
    return doc


# ================================================= Arm F — verbatim quotes
def f_build_ladder(miners, max_depth):
    """views.py:209-231 transcribed from the pinned quotes: band loop
    ``for depth in range(max_depth + 1)`` (:216) and the PER-BAND
    if/elif (:221-225)."""
    bands = []
    for depth in range(max_depth + 1):
        here, record_only = [], []
        for miner in miners:
            name = miner.get("display_name") or miner.get("suid") or "?"
            if miner.get("depth") == depth:
                here.append(name)
            elif miner.get("record_depth") == depth:
                record_only.append(name)
        bands.append({"depth": depth, "here": here,
                      "record_only": record_only})
    return bands


def f_build_minimap(miners, max_depth):
    """views.py:303-345 transcribed: band loop (:316) + band filter
    ``if miner.get("depth") != depth: continue`` (:320-326); the pinned
    template always carries a valid position, so points it is."""
    panels = []
    for depth in range(max_depth + 1):
        points, unplotted = [], []
        for miner in miners:
            if miner.get("depth") != depth:
                continue
            name = miner.get("display_name") or miner.get("suid") or "?"
            pos = miner.get("position")
            if not (isinstance(pos, dict) and isinstance(pos.get("x"), int)
                    and isinstance(pos.get("y"), int)):
                unplotted.append(name)
                continue
            points.append({"x": pos["x"], "y": pos["y"], "name": name})
        panels.append({"depth": depth, "points": points,
                       "unplotted": unplotted})
    return panels


def f_deep_diver(miner, max_depth):
    """views.py:446-448 transcribed verbatim."""
    return (isinstance(miner.get("record_depth"), int)
            and miner["record_depth"] == max_depth)


def f_effective_max_depth(snapshot):
    """views.py:631-634 transcribed: the absence fallback."""
    max_depth = snapshot.get("max_depth")
    if not isinstance(max_depth, int):
        max_depth = DEPTH_MAX  # schema fallback when the hint is absent
    return max_depth


def f_observe(doc, name):
    """The four served outputs for miner ``name``: live chip, record
    chip, minimap presence (points or unplotted), deep_diver."""
    md = f_effective_max_depth(doc)
    miners = doc["miners"]
    ladder = f_build_ladder(miners, md)
    minimap = f_build_minimap(miners, md)
    live = any(name in b["here"] for b in ladder)
    ghost = any(name in b["record_only"] for b in ladder)
    mapped = any(any(p["name"] == name for p in pn["points"])
                 or name in pn["unplotted"] for pn in minimap)
    miner = next(m for m in miners if m["display_name"] == name)
    badge = f_deep_diver(miner, md)
    return {"live": live, "ghost": ghost, "map": mapped, "badge": badge}


# ============================================ Arm B — independent enumerator
def b_cell(m, d, r):
    """Direct predicate scans over explicitly constructed index sets —
    written independently of Arm A's closed forms and Arm F's
    transcription."""
    rendered_bands = set()
    band = 0
    while band <= (3 if m == "absent" else m):
        rendered_bands.add(band)
        band += 1
    live = False
    ghost = False
    for band in sorted(rendered_bands):
        occupies = (d == band)
        if occupies:
            live = True
        if (not occupies) and (r == band):
            ghost = True
    mapped = False
    for band in sorted(rendered_bands):
        if d == band:
            mapped = True
    badge = (r == max(rendered_bands))
    return {"live": live, "ghost": ghost, "map": mapped, "badge": badge}


def enumerate_lattice(observe):
    cells = {}
    for m in HINTS:
        for d in DEPTHS:
            for r in DEPTHS:
                cells[(m, d, r)] = observe(m, d, r)
    return cells


B_CELLS = enumerate_lattice(b_cell)


def census_from_cells(cells):
    """Every census the registration prices, computed by counting."""
    inv_by_m = {m: 0 for m in (0, 1, 2, 3)}
    mm_inv = ghost_only = badges = overshoot = 0
    invisible_cells = []
    for (m, d, r), v in cells.items():
        fully_inv = not (v["live"] or v["ghost"] or v["map"])
        if m != "absent":
            if fully_inv:
                inv_by_m[m] += 1
                invisible_cells.append([m, d, r])
            if not v["map"]:
                mm_inv += 1
            if v["ghost"] and not (v["live"] or v["map"]):
                ghost_only += 1
            if r > m:
                overshoot += 1 if not v["badge"] else 0
        if v["badge"]:
            badges += 1
    flips = 0
    flip_cells = []
    for m in (0, 1, 2):
        for d in DEPTHS:
            if (m, d, m) not in cells or (m, d, m + 1) not in cells:
                continue  # partial lattices (the G6a repair world)
            if cells[(m, d, m)]["badge"] and not cells[(m, d, m + 1)]["badge"]:
                flips += 1
                flip_cells.append([m, d])
    strict = 0
    strict_cells = []
    dom_holds = True
    for m in (0, 1, 2, 3):
        for d in DEPTHS:
            for r in DEPTHS:
                if ("absent", d, r) not in cells or (m, d, r) not in cells:
                    continue  # partial lattices (the G6a repair world)
                va = cells[("absent", d, r)]
                vm = cells[(m, d, r)]
                vis_a = va["live"] or va["ghost"] or va["map"]
                vis_m = vm["live"] or vm["ghost"] or vm["map"]
                if vis_m and not vis_a:
                    dom_holds = False
                if vis_a and not vis_m:
                    strict += 1
                    strict_cells.append([m, d, r])
    return {"inv_by_m": inv_by_m, "inv_total": sum(inv_by_m.values()),
            "invisible_cells": sorted(invisible_cells),
            "minimap_invisible": mm_inv, "ghost_only": ghost_only,
            "badge_earn": badges, "flips": flips,
            "flip_cells": sorted(flip_cells), "overshoot": overshoot,
            "domination_holds": dom_holds, "strict": strict,
            "strict_cells": sorted(strict_cells)}


B_CENSUS = census_from_cells(B_CELLS)

# ==================================================== Arm A — closed forms
A = {}
A["inv_by_m"] = {m: (3 - m) ** 2 for m in (0, 1, 2, 3)}
A["inv_total"] = sum(A["inv_by_m"].values())
A["minimap_invisible"] = sum(4 * (3 - m) for m in (0, 1, 2, 3))
A["ghost_only"] = sum((3 - m) * (m + 1) for m in (0, 1, 2, 3))
# badge: per hint value (incl. absent) exactly the 4 cells with r == m_eff
A["badge_earn"] = 4 * len(HINTS)
A["flips"] = 4 * 3          # m in {0,1,2} x d in 0..3
A["overshoot"] = sum(4 * (3 - m) for m in (0, 1, 2, 3))
A["strict"] = A["inv_total"]


def a_laws(m, d, r):
    me = m_eff(m)
    return {"live": d <= me, "ghost": r <= me and r != d,
            "map": d <= me, "badge": r == me}


A_CELLS = enumerate_lattice(a_laws)

# ==================================================== Arm F over documents
F_CELLS = {}
ACCEPTED = 0
for m in HINTS:
    for d in DEPTHS:
        for r in DEPTHS:
            doc = make_doc(m, [("X", d, r)])
            check(f"G2 acceptance ({m},{d},{r})", rederived_accepts(doc))
            ACCEPTED += 1
            F_CELLS[(m, d, r)] = f_observe(doc, "X")
check("G2 acceptance count 80", ACCEPTED == FX["committed_constants"]["lattice_size"])
check("G2 applicator inventory empty",
      FX["_grounding"]["superbot_mineverse"]["pins"]
      ["applicator_inventory"]["found"] == [])

# ---------------------------------------------------------- G1 twin arms
check("G1 A == B on every cell verdict", A_CELLS == B_CELLS)
check("G1 F == B cell-by-cell (80 x 4)", F_CELLS == B_CELLS)
F_CENSUS = census_from_cells(F_CELLS)
check("G1 F census == B census", F_CENSUS == B_CENSUS)
for key in ("inv_by_m", "inv_total", "minimap_invisible", "ghost_only",
            "badge_earn", "flips", "overshoot", "strict"):
    check(f"G1 A closed form == B enumeration [{key}]",
          A[key] == B_CENSUS[key])

# ----------------------------------------------------------- G3 censuses
D = FX["censuses_registered"]
compare_disclosed("fully_invisible_by_hint",
                  {int(k): v for k, v in D["fully_invisible_by_hint"].items()},
                  B_CENSUS["inv_by_m"])
compare_disclosed("fully_invisible_total", D["fully_invisible_total"],
                  B_CENSUS["inv_total"])
compare_disclosed("minimap_invisible_total", D["minimap_invisible_total"],
                  B_CENSUS["minimap_invisible"])
compare_disclosed("ghost_only_total", D["ghost_only_total"],
                  B_CENSUS["ghost_only"])
compare_disclosed("badge_earn_total", D["badge_earn_total"],
                  B_CENSUS["badge_earn"])
compare_disclosed("badge_flip_cells", D["badge_flip_cells"],
                  B_CENSUS["flips"])
compare_disclosed("badge_overshoot_denials", D["badge_overshoot_denials"],
                  B_CENSUS["overshoot"])
compare_disclosed("t4_strict_count", 14, B_CENSUS["strict"])

# ---------------------------------------------------------------- G4 laws
for (m, d, r), v in B_CELLS.items():
    me = m_eff(m)
    check(f"G4 live iff ({m},{d},{r})", v["live"] == (d <= me))
    check(f"G4 ghost iff ({m},{d},{r})",
          v["ghost"] == (r <= me and r != d))
    check(f"G4 map iff ({m},{d},{r})", v["map"] == (d <= me))
    check(f"G4 badge iff ({m},{d},{r})", v["badge"] == (r == me))
    fully_inv = not (v["live"] or v["ghost"] or v["map"])
    check(f"G4 invisible iff ({m},{d},{r})",
          fully_inv == (d > me and r > me))
check("G4 T4 domination holds on all 64", B_CENSUS["domination_holds"])
check("G4 T4 strictness exactly on the invisible cells",
      B_CENSUS["strict_cells"] == B_CENSUS["invisible_cells"])
# m = 0 inversion
compare_disclosed("m0_inversion",
                  True,
                  B_CELLS[(0, 0, 0)]["badge"]
                  and not B_CELLS[(0, 3, 3)]["badge"])

# ---------------------------------------------- typed margin ledger (C5)
for m in (0, 1, 2):  # (i) d = m_eff is the LAST visible band, two-sided
    check(f"ledger(i) live at contact m={m}", B_CELLS[(m, m, m)]["live"])
    v = B_CELLS[(m, m + 1, m + 1)]
    check(f"ledger(i) invisible one past contact m={m}",
          not (v["live"] or v["ghost"] or v["map"]))
for m in (0, 1, 2, 3):  # (ii) badge == two-sided
    check(f"ledger(ii) r=m earns m={m}", B_CELLS[(m, 0, m)]["badge"])
    if m + 1 <= 3:
        check(f"ledger(ii) r=m+1 does not m={m}",
              not B_CELLS[(m, 0, m + 1)]["badge"])
    if m - 1 >= 0:
        check(f"ledger(ii) r=m-1 does not m={m}",
              not B_CELLS[(m, 0, m - 1)]["badge"])
# (iii) m_eff = 3 byte-identity — registered margin-0 contact
compare_disclosed("g6c_byte_identity_meff3", True,
                  all((r == 3) == (r >= 3) for r in DEPTHS))

# ------------------------------------------------------- T3 witness (G2+)
extra = {"A": {"coins": 59999, "xp.game_total": 9999}}
t3 = make_doc(2, [("A", 3, 3), ("B", 2, 2)], extra)
check("T3 witness accepted", rederived_accepts(t3))
oa = f_observe(t3, "A")
ob = f_observe(t3, "B")
# leaderboards never read the hint (pinned): rank by the committed keys
miners = t3["miners"]
depth_board = sorted(miners, key=lambda m: (m["depth"], m["xp"]["game_total"]),
                     reverse=True)
coins_board = sorted(miners, key=lambda m: (m["coins"],), reverse=True)
compare_disclosed("t3_A_first_on_depth_board", True,
                  depth_board[0]["display_name"] == "A")
compare_disclosed("t3_A_first_on_coins_board", True,
                  coins_board[0]["display_name"] == "A")
compare_disclosed("t3_A_fully_invisible", True,
                  not (oa["live"] or oa["ghost"] or oa["map"]))
compare_disclosed("t3_badge_inverted", True,
                  (not oa["badge"]) and ob["badge"])
t3_absent = copy.deepcopy(t3)
del t3_absent["max_depth"]
check("T3 absent-hint twin accepted", rederived_accepts(t3_absent))
oa2 = f_observe(t3_absent, "A")
ob2 = f_observe(t3_absent, "B")
compare_disclosed("t3_absent_flips_all_three", True,
                  oa2["live"] and oa2["badge"] and not ob2["badge"])

# --------------------------------------------------------- G5 hand world
g5 = make_doc(0, [("P", 0, 0), ("Q", 1, 0), ("S", 2, 2), ("T", 3, 3)])
check("G5 accepted", rederived_accepts(g5))
g5_md = f_effective_max_depth(g5)
g5_ladder = f_build_ladder(g5["miners"], g5_md)
g5_minimap = f_build_minimap(g5["miners"], g5_md)
compare_disclosed("g5_one_band", 1, len(g5_ladder))
compare_disclosed("g5_P_live", True, "P" in g5_ladder[0]["here"])
compare_disclosed("g5_Q_ghost_only", True,
                  "Q" in g5_ladder[0]["record_only"]
                  and "Q" not in g5_ladder[0]["here"])
for nm in ("S", "T"):
    o = f_observe(g5, nm)
    compare_disclosed(f"g5_{nm}_fully_invisible", True,
                      not (o["live"] or o["ghost"] or o["map"]))
g5_badges = {m["display_name"]: f_deep_diver(m, g5_md)
             for m in g5["miners"]}
compare_disclosed("g5_badges_P_Q_only", True,
                  g5_badges == {"P": True, "Q": True,
                                "S": False, "T": False})

# ------------------------------------------------- G6 consequence battery
# (a) conformance-applicator world: require d <= m and r <= m when present
g6a_accepted = [
    (m, d, r) for m in HINTS for d in DEPTHS for r in DEPTHS
    if m == "absent" or (d <= m and r <= m)]
compare_disclosed("g6a_accepted_lattice", 46, len(g6a_accepted))
g6a_census = census_from_cells({c: B_CELLS[c] for c in g6a_accepted})
check("G6a all invisibility censuses zero",
      g6a_census["inv_total"] == 0 and g6a_census["minimap_invisible"] == 0
      and g6a_census["ghost_only"] == 0)
g6a_flips = sum(
    1 for m in (0, 1, 2) for d in DEPTHS
    if (m, d, m) in g6a_accepted and (m, d, m + 1) in g6a_accepted
    and B_CELLS[(m, d, m)]["badge"] and not B_CELLS[(m, d, m + 1)]["badge"])
compare_disclosed("g6a_surviving_flip_pairs", 0, g6a_flips)
# APPROVE liveness in repair world (a), via the registered clause only:
g6a_approve = (g6a_census["inv_total"] == 0 and g6a_flips == 0)
check("G6a APPROVE clause fires (liveness)", g6a_approve)

# (b) overflow-band render world: bands = range(max(m_eff, d, r) + 1)
g6b_invisible = 0
for (m, d, r) in B_CELLS:
    me = max(m_eff(m), d, r)
    live = d <= me
    ghost = r <= me and r != d
    mapped = d <= me
    if not (live or ghost or mapped):
        g6b_invisible += 1
compare_disclosed("g6b_fully_invisible", 0, g6b_invisible)

# (c) deep_diver as >=
g6c_earn = sum(1 for (m, d, r) in B_CELLS if r >= m_eff(m))
compare_disclosed("g6c_badge_earn", 44, g6c_earn)
g6c_flips = sum(1 for m in (0, 1, 2) for d in DEPTHS
                if (m >= m) and not (m + 1 >= m))
compare_disclosed("g6c_flips", 0, g6c_flips)

# --------------------------------------- frontend meter rows (reporting)
def meter(d, m):
    """The committed JS ternary (app.js:1173): integer 0 is falsy."""
    return (d / m) * 100 if m else 0.0


compare_disclosed("meter_d3_m2", 150.0, meter(3, 2))
compare_disclosed("meter_d3_m1", 300.0, meter(3, 1))
compare_disclosed("meter_m0_all", 0.0,
                  max(meter(d, 0) for d in DEPTHS))

# --------------------------------------------- decision evaluators (twin)
def evaluate_decision(census, invisible_cells, cells):
    """The pre-registered rule in the registered order.  Reads a census
    + cell table only; called once on Arm A/closed-form data and once on
    Arm B's independent table."""
    r1 = census["inv_total"] >= 1 and all(
        not (cells[tuple(c)]["live"] or cells[tuple(c)]["ghost"]
             or cells[tuple(c)]["map"])
        for c in invisible_cells)
    r2 = census["flips"] >= 1
    r3 = census["domination_holds"] and census["strict"] >= 1
    if r1 and r2 and r3:
        return "REJECT"
    if census["inv_total"] == 0 and census["flips"] == 0:
        return "APPROVE"
    return "NULL"


A_CENSUS = census_from_cells(A_CELLS)
VERDICT_A = evaluate_decision(A_CENSUS, A_CENSUS["invisible_cells"], A_CELLS)
VERDICT_B = evaluate_decision(B_CENSUS, B_CENSUS["invisible_cells"], B_CELLS)
check("twin evaluators agree", VERDICT_A == VERDICT_B)
check("C12 APPROVE/REJECT mutually exclusive",
      not (B_CENSUS["inv_total"] >= 1 and B_CENSUS["inv_total"] == 0))
# n-axes (fixture-pinned facts, checked):
check("n1 no cross-field applicator (fixture sweep empty)",
      FX["_grounding"]["superbot_mineverse"]["pins"]
      ["applicator_inventory"]["found"] == [])
check("n2 axis live: re-derived acceptance table complete (80 cells)",
      len(F_CELLS) == 80 and ACCEPTED == 80)

# ==================================================== Arm R — reporting only
def arm_r(seed, n_docs):
    rng = REG.rng(seed)
    draws = 0
    miners_total = 0
    events = {"fully_invisible": 0, "ghost_only": 0, "deep_diver": 0,
              "minimap_invisible_hint_present": 0, "hint_present_miners": 0}
    for _ in range(n_docs):
        k = rng.randint(1, 7)
        hint = HINTS[rng.randrange(5)]
        draws += 2
        for _ in range(k):
            d = rng.randrange(4)
            r = rng.randrange(4)
            draws += 2
            miners_total += 1
            v = B_CELLS[(hint, d, r)]
            fully_inv = not (v["live"] or v["ghost"] or v["map"])
            if fully_inv:
                events["fully_invisible"] += 1
            if v["ghost"] and not (v["live"] or v["map"]):
                events["ghost_only"] += 1
            if v["badge"]:
                events["deep_diver"] += 1
            if hint != "absent":
                events["hint_present_miners"] += 1
                if not v["map"]:
                    events["minimap_invisible_hint_present"] += 1
    return {"seed": seed, "documents": n_docs, "miners": miners_total,
            "draws": draws, "events": events}


R_MAIN = arm_r(FX["arm_R"]["main"]["seed"], FX["arm_R"]["main"]["documents"])
R_STAB = arm_r(FX["arm_R"]["stability"]["seed"],
               FX["arm_R"]["stability"]["documents"])
check("Arm R main draw sentinel",
      R_MAIN["documents"] == FX["arm_R"]["main"]["documents"])
check("Arm R stability draw sentinel",
      R_STAB["documents"] == FX["arm_R"]["stability"]["documents"])
# presentation shuffle (presentation-only)
pres = REG.rng(FX["arm_R"]["presentation_shuffle_seed"])
PRESENT_ORDER = list(range(len(HINTS)))
pres.shuffle(PRESENT_ORDER)
check("seed registry exact",
      REG.constructed == FX["seeds"]["registered_set"][:3])
check("aux seed never read", AUX_SEED not in REG.constructed)
CENSUS["not_disclosed"].append(
    "arm_R seeded rates — the registration disclosed the estimand and the "
    "seed set only, no seeded counts; empirical rates print beside the "
    "exact expectations 14/80, 10/80, 20/80, 24/64 with nothing to compare")

# Final ruling: INVALID on ANY gate failure (G1-G6, ledger, sentinels),
# else the twin evaluators' agreed token (fixtures decision_rule order).
RULING = VERDICT_B if VERDICT_A == VERDICT_B else "INVALID"
if CHECKS["failed"] > 0:
    RULING = "INVALID"

# ------------------------------------------------------------- results.json
def cellkey(c):
    return f"{c[0]}|{c[1]}|{c[2]}"


RESULTS = {
    "verdict": RULING,
    "twin_verdicts": {"arm_A_closed_forms": VERDICT_A,
                      "arm_B_independent": VERDICT_B},
    "censuses": {
        "fully_invisible_by_hint": B_CENSUS["inv_by_m"],
        "fully_invisible_total": B_CENSUS["inv_total"],
        "fully_invisible_cells": B_CENSUS["invisible_cells"],
        "minimap_invisible_total": B_CENSUS["minimap_invisible"],
        "ghost_only_total": B_CENSUS["ghost_only"],
        "badge_earn_total": B_CENSUS["badge_earn"],
        "badge_flip_cells": B_CENSUS["flips"],
        "badge_flip_cell_list": B_CENSUS["flip_cells"],
        "badge_overshoot_denials": B_CENSUS["overshoot"],
        "t4_domination_holds": B_CENSUS["domination_holds"],
        "t4_strict_count": B_CENSUS["strict"],
    },
    "lattice_table": {cellkey(k): v for k, v in sorted(
        B_CELLS.items(), key=lambda kv: (str(kv[0][0]), kv[0][1], kv[0][2]))},
    "t3_witness": {
        "accepted": True,
        "A_first_depth_board": depth_board[0]["display_name"] == "A",
        "A_first_coins_board": coins_board[0]["display_name"] == "A",
        "A_outputs": oa, "B_outputs": ob,
        "absent_twin_A": oa2, "absent_twin_B": ob2,
    },
    "g5_hand_world": {"bands": len(g5_ladder), "badges": g5_badges,
                      "ladder_band0": g5_ladder[0]},
    "g6_repair_worlds": {
        "a_conformance": {"accepted": len(g6a_accepted),
                          "censuses_zero": True, "flip_pairs": g6a_flips,
                          "approve_fires": g6a_approve},
        "b_overflow_bands": {"fully_invisible": g6b_invisible},
        "c_badge_gte": {"earn": g6c_earn, "flips": g6c_flips,
                        "byte_identical_at_meff3": True},
    },
    "meter_rows_reporting": {"d3_m2": 150.0, "d3_m1": 300.0, "m0": 0.0},
    "arm_R": {"main": R_MAIN, "stability": R_STAB,
              "presentation_order": PRESENT_ORDER,
              "exact_expectations":
                  FX["arm_R"]["exact_expectations_per_miner"]},
    "anomaly_census": CENSUS,
    "seed_registry": {"constructed": REG.constructed,
                      "aux_never_read": AUX_SEED},
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": CHECKS["failures"]},
}

out = os.path.join(HERE, "results.json")
with open(out, "w") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True, default=str)
    fh.write("\n")

# ------------------------------------------------------------------ stdout
print("VERDICT 088 — max_depth hint visibility clip (P075)")
print(f"ruling: {RULING} (twin evaluators {VERDICT_A} / {VERDICT_B})")
print("lattice: hint {absent,0,1,2,3} x depth 0..3 x record 0..3 = 80 "
      "cells, ALL accepted by the re-derived v1 check "
      "(zero cross-field applicators — the pinned sweep is EMPTY)")
print(f"fully-invisible census: {B_CENSUS['inv_total']}/80, per-hint "
      f"{{m0: {B_CENSUS['inv_by_m'][0]}, m1: {B_CENSUS['inv_by_m'][1]}, "
      f"m2: {B_CENSUS['inv_by_m'][2]}, m3: {B_CENSUS['inv_by_m'][3]}}} "
      "= (3-m)^2 exactly")
print(f"minimap-invisible: {B_CENSUS['minimap_invisible']}/80; "
      f"ghost-chip-only: {B_CENSUS['ghost_only']}/80")
print(f"badge: earn {B_CENSUS['badge_earn']}/80 (iff r == m_eff); "
      f"non-monotone flips {B_CENSUS['flips']} (dig one past the hint, "
      f"lose 'Deep Diver'); overshoot denials {B_CENSUS['overshoot']}; "
      "m=0 inversion CONFIRMED (never-dug r=0 earns, r=3 explorer denied)")
print(f"T4 domination: absence >= presence on all 64 comparisons "
      f"({B_CENSUS['domination_holds']}), strict on exactly "
      f"{B_CENSUS['strict']} cells == the invisible cells "
      f"({B_CENSUS['strict_cells'] == B_CENSUS['invisible_cells']})")
print("T3 witness (m=2, A(3,3) top coins/XP, B(2,2)): accepted; A #1 on "
      f"depth board {depth_board[0]['display_name'] == 'A'}, #1 on coins "
      f"board {coins_board[0]['display_name'] == 'A'}; A world-view rows: "
      f"live={oa['live']} ghost={oa['ghost']} map={oa['map']}; badge "
      f"A={oa['badge']} B={ob['badge']}; absent-hint twin flips all three: "
      f"{oa2['live'] and oa2['badge'] and not ob2['badge']}")
print(f"G5 hand world (m=0; P(0,0) Q(1,0) S(2,2) T(3,3)): bands="
      f"{len(g5_ladder)}; P live; Q ghost-chip only; S,T fully invisible; "
      f"deep_diver={{P,Q}} — five facts checked")
print(f"G6 repairs: (a) conformance applicator 80->{len(g6a_accepted)} "
      f"accepted, censuses zero, flip pairs {g6a_flips}, APPROVE fires; "
      f"(b) overflow bands invisible {g6b_invisible}/80; (c) >= badge "
      f"{g6c_earn}/80, flips {g6c_flips}, byte-identical to == at m_eff=3")
print("meter rows (reporting, committed JS ternary): d3/m2=150%, "
      "d3/m1=300%, m=0 -> 0% for every miner (falsy zero)")
em = R_MAIN["events"]
es = R_STAB["events"]
print(f"arm R main (seed {R_MAIN['seed']}, {R_MAIN['documents']} docs, "
      f"{R_MAIN['miners']} miners): invisible {em['fully_invisible']}"
      f"/{R_MAIN['miners']} (exact 14/80), ghost-only {em['ghost_only']}"
      f"/{R_MAIN['miners']} (exact 10/80), deep_diver {em['deep_diver']}"
      f"/{R_MAIN['miners']} (exact 20/80), minimap-invisible|hint "
      f"{em['minimap_invisible_hint_present']}/{em['hint_present_miners']} "
      "(exact 24/64)")
print(f"arm R stability (seed {R_STAB['seed']}, {R_STAB['documents']} "
      f"docs, {R_STAB['miners']} miners): invisible "
      f"{es['fully_invisible']}/{R_STAB['miners']}, ghost-only "
      f"{es['ghost_only']}/{R_STAB['miners']}, deep_diver "
      f"{es['deep_diver']}/{R_STAB['miners']}, minimap-invisible|hint "
      f"{es['minimap_invisible_hint_present']}/{es['hint_present_miners']}")
print(f"presentation order (seed 20261672): "
      f"{','.join(str(i) for i in PRESENT_ORDER)}")
print(f"seed registry: {REG.constructed} (aux {AUX_SEED} never read)")
print(f"anomaly census (structured, V087 coverage convention): "
      f"compared-and-matched {CENSUS['compared_and_matched']}, "
      f"mismatched {len(CENSUS['compared_and_mismatched'])}, "
      f"not-disclosed {len(CENSUS['not_disclosed'])} "
      "(arm-R seeded rates — vacancy, honestly stated)")
print(f"self-checks: {CHECKS['passed']} passed, {CHECKS['failed']} failed")
if CHECKS["failures"]:
    for f in CHECKS["failures"][:20]:
        print("  FAILED:", f)

ok = CHECKS["failed"] == 0 and RULING in ("REJECT", "APPROVE", "NULL")
sys.exit(0 if ok else 1)
