#!/usr/bin/env python3
"""VERDICT 038 / ORDER 005 SIM-REQUEST 2 — idle economy FEEL sim (superbot-idle SIM-001).

NUMERIC SIMULATION (method ladder rung 1): deterministic, integer-exact,
stdlib-only, NO RNG, no network, no git, no wall clock at run time. A single
run per (world, scenario) IS the distribution (the engine is pure and
integer-exact); determinism is proven by byte-identical re-run, not by seeds.
Zero seeds drawn; the fleet seed-registry high-water 20260775 (V037) is
untouched.

PROVENANCE — DRIVE THE REAL ENGINE AND THE REAL COMMITTED HARNESS
  ``fixtures/idle_engine/`` is a VENDOR COPY, byte-for-byte and COMPLETE
  (all 11 modules, ``__init__.py`` included, unmodified), of
  ``menno420/superbot-idle`` ``idle_engine/`` @
  ``d992c5688e802b28d11c0ec6c835fa54a87149ec``, plus the repo's own committed
  SIM-001 harness ``tools/simulate.py`` (byte-for-byte) — sha256 manifest in
  ``fixtures/MANIFEST.json``, re-verified at every run before anything is
  imported. The driver loads ONLY the six economy-surface modules through a
  synthetic package anchor so the byte-identical ``__init__.py`` — which
  pulls theme/render and with them the non-stdlib ``yaml`` — is never
  EXECUTED (the VERDICT 006/017 accommodation). The registered SIM-001 spec
  is NOT re-implemented: the vendored harness's own ``run_report`` /
  ``simulate_s2`` / ``simulate_s3`` produce every baseline and arm number;
  the single driver-level scenario variant (seed-count arm) is
  equivalence-GATED against the vendored ``simulate_s3`` at C=1.

Pre-registration: fixtures.json (committed BEFORE this runner; every anchor,
band, arm and decision rule quoted from it at run time).

Source: idea-engine control/inbox.md ORDER 005 SIM-REQUEST 2 @ 8218d66;
packet superbot-idle control/outbox.md SIM-001 @ d992c568; registered spec
docs/design/economy-v1.md § "Simulation request — SIM-001 (Q-0264)".

Run:  python3 sims/verdict-038-idle-economy-feel/idle_economy_feel_sim.py
Exit 0 iff every self-check passes. Writes results.json next to itself.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import platform
import statistics
import sys
import types

sys.dont_write_bytecode = True  # keep the byte-pinned fixtures/ tree pristine
from dataclasses import replace
from fractions import Fraction

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIX_DIR = os.path.join(BASE_DIR, "fixtures")
ENGINE_DIR = os.path.join(FIX_DIR, "idle_engine")

# --------------------------------------------------------------------------
# Vendored harness helpers (stdlib-only) — harness/simharness.py family,
# exactly as VERDICT 006/017 vendored them.
# --------------------------------------------------------------------------


class SelfCheck:
    """Assertion battery with a pass counter (harness/simharness.py)."""

    def __init__(self):
        self.passed = 0
        self.detail = []

    def check(self, cond, label):
        self.detail.append((bool(cond), label))
        if cond:
            self.passed += 1
        else:
            raise AssertionError("SELF-CHECK FAILED: " + label)
        return bool(cond)

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def frac_fields(fr: Fraction) -> dict:
    return {"exact": "%d/%d" % (fr.numerator, fr.denominator), "approx": float(fr)}


# --------------------------------------------------------------------------
# Fixture integrity FIRST: every vendored byte is manifest-pinned.
# --------------------------------------------------------------------------

with open(os.path.join(BASE_DIR, "fixtures.json"), "rb") as _fh:
    FIXTURE = json.loads(_fh.read().decode("utf-8"))
with open(os.path.join(FIX_DIR, "MANIFEST.json"), "rb") as _fh:
    MANIFEST = json.loads(_fh.read().decode("utf-8"))

PIN = "d992c5688e802b28d11c0ec6c835fa54a87149ec"
SC = SelfCheck()

SC.check(MANIFEST["pin_commit"] == PIN and FIXTURE["engine_pin"]["commit"] == PIN,
         "fixtures: MANIFEST + fixtures.json pin superbot-idle @ %s" % PIN[:7])
_names = sorted(MANIFEST["sha256"].keys())
SC.check(len(_names) == 12 and "tools/simulate.py" in _names,
         "fixtures: 12 manifest-listed files (11 engine modules + tools/simulate.py)")
for _name in _names:
    with open(os.path.join(FIX_DIR, *_name.split("/")), "rb") as fh:
        _digest = hashlib.sha256(fh.read()).hexdigest()
    SC.check(_digest == MANIFEST["sha256"][_name],
             "fixtures: %s sha256 matches manifest (byte-identical vendor)" % _name)

# Verified premise: NO generator purchase path at the pin (fm E#52 feed).
_purchase_defs = []
for _mod in sorted(f for f in os.listdir(ENGINE_DIR) if f.endswith(".py")):
    with open(os.path.join(ENGINE_DIR, _mod), "rb") as fh:
        for line in fh.read().decode("utf-8").splitlines():
            if line.strip().startswith("def purchase_"):
                _purchase_defs.append((_mod, line.strip().split("(")[0]))
SC.check(_purchase_defs == [("upgrades.py", "def purchase_upgrade"),
                            ("upgrades.py", "def purchase_upgrades")],
         "premise: purchase_upgrade/purchase_upgrades are the ONLY purchase "
         "functions at %s — no generator purchase path (honest-NULL scope)" % PIN[:7])

# --------------------------------------------------------------------------
# Load the vendored engine through a synthetic package anchor (init never
# executed), then the vendored committed harness as a plain module.
# --------------------------------------------------------------------------

_pkg = types.ModuleType("idle_engine")
_pkg.__path__ = [ENGINE_DIR]
_pkg.__package__ = "idle_engine"
sys.modules["idle_engine"] = _pkg

_state = importlib.import_module("idle_engine.state")
_upgrades = importlib.import_module("idle_engine.upgrades")
_prestige = importlib.import_module("idle_engine.prestige")
_achieve = importlib.import_module("idle_engine.achievements")
_engine = importlib.import_module("idle_engine.engine")
ECON = importlib.import_module("idle_engine.economy")

GameState = _state.GameState
GeneratorSpec = _state.GeneratorSpec
upgrade_cost = _upgrades.upgrade_cost
PrestigeSpec = _prestige.PrestigeSpec
prestige_percent = _prestige.prestige_percent
production_per_second = _engine.production_per_second
tick = _engine.tick

_spec = importlib.util.spec_from_file_location(
    "sim001_harness", os.path.join(FIX_DIR, "tools", "simulate.py"))
HARNESS = importlib.util.module_from_spec(_spec)
sys.modules["sim001_harness"] = HARNESS
_spec.loader.exec_module(HARNESS)

# Parameter parity: the fixture table must BE the vendored engine's table.
_PARAMS = {k: getattr(ECON, k) for k in (
    "UPGRADE_BASE_COST_SECONDS", "UPGRADE_COST_GROWTH_NUM",
    "UPGRADE_COST_GROWTH_DEN", "UPGRADE_EFFECT_PERCENT",
    "PRESTIGE_THRESHOLD", "PRESTIGE_AWARD_DIVISOR", "PRESTIGE_BONUS_PERCENT")}
for _k, _v in _PARAMS.items():
    SC.check(FIXTURE["parameters_verbatim_from_engine"][_k] == _v,
             "parity: fixture %s == engine %d" % (_k, _v))

CUR = "primary"
GEN = GeneratorSpec(spec_id="tier1", produces=CUR, base_rate=1)
BOOST1 = ECON.build_upgrade_spec("boost1", GEN)
PRES = ECON.build_prestige_spec(awards="prestige", measures=CUR)
THRESHOLD = PRES.threshold


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def rate_at(gen, up, pres, level: int, count: int = 1, prestige_units: int = 0) -> int:
    """REAL engine integer rate at a given boost1 level / count / prestige."""
    st = GameState(owned={gen.spec_id: count}, last_seen=0,
                   upgrades={up.spec_id: level} if level else {},
                   prestige={pres.awards: prestige_units} if prestige_units else {})
    return production_per_second(st, (gen,), (up,), (pres,)).get(CUR, 0)


def fresh_rate(gen, up, pres, count: int = 1) -> int:
    return rate_at(gen, up, pres, 0, count=count)


# --------------------------------------------------------------------------
# Driver-level S3 variant for the seed-count arm ONLY (the vendored
# _fresh_state hard-codes count 1). Mirrors the vendored simulate_s3 loop
# and REUSES its _greedy_buy/_maybe_prestige; equivalence-gated at C=1.
# --------------------------------------------------------------------------


def s3_count_variant(gen, up, pres, count: int, max_resets: int = 1):
    gens, ups, prs = (gen,), (up,), (pres,)
    state = GameState(owned={gen.spec_id: count}, last_seen=0)
    purchases, resets = [], []
    reset_start, reset_index = 0, 1
    events = 0
    while True:
        t = state.last_seen
        rate = production_per_second(state, gens, ups, prs).get(CUR, 0)
        if len(resets) >= max_resets:
            break
        if rate <= 0:
            raise RuntimeError("production stalled at rate 0 (t=%d)" % t)
        need_buy = upgrade_cost(up, state.upgrades.get(up.spec_id, 0)) - \
            state.balances.get(CUR, 0)
        need_pre = pres.threshold - state.lifetime.get(CUR, 0)
        dt = min(ceil_div(max(need_buy, 1), rate), ceil_div(max(need_pre, 1), rate))
        state = tick(state, gens, dt, ups, prs)
        state, _ = HARNESS._greedy_buy(state, up, purchases, reset_index, 3)
        state, reset_start, reset_index, _ = HARNESS._maybe_prestige(
            state, gen, up, pres, resets, reset_start, reset_index)
        events += 1
        if events > HARNESS.MAX_EVENTS:
            raise RuntimeError("event budget exceeded")
    return {"purchases_through_reset_3": purchases, "resets_head": resets,
            "first_prestige_t": resets[0]["t"] if resets else None}


# --------------------------------------------------------------------------
# B0 — baseline validity: the committed harness, full mode, at the pin.
# --------------------------------------------------------------------------

REPORT = HARNESS.run_report(quick=False)
_report_bytes = HARNESS.to_json(REPORT).encode("utf-8")
REPORT_SHA = hashlib.sha256(_report_bytes).hexdigest()

B0 = FIXTURE["b0_baseline_validity_anchors"]
_hp = B0["hard_from_packet"]
_hv = B0["hard_from_v006_cross_pins"]
_meas = REPORT["measures"]
_s3 = REPORT["scenarios"]["S3"]
_o6rows = REPORT["outputs"]["O6_prestige_stacking"]["rows"]
_o6_durs = [r["duration"] for r in _o6rows]
_o6_awards = [r["award"] for r in _o6rows]

_first_run_purch = [p for p in _s3["purchases_through_reset_3"] if p[1] == 1]
_first3_costs = [p[3] for p in _first_run_purch[:3]]
SC.check(_first3_costs == _hp["s3_first_three_purchase_costs"],
         "B0 packet: first three boost1 costs == %s" % _hp["s3_first_three_purchase_costs"])

_rates_l0_l5 = [rate_at(GEN, BOOST1, PRES, L) for L in range(6)]
SC.check(_rates_l0_l5 == _hp["rate_by_level_L0_to_L5"],
         "B0 packet: rate-by-level L0..L5 == %s (real engine)" % _hp["rate_by_level_L0_to_L5"])

SC.check(_meas["s3_first_prestige_t"] == _hp["s3_first_prestige_t_s"],
         "B0 packet: S3 first prestige t == %d s" % _hp["s3_first_prestige_t_s"])
_durs123 = _meas["s3_reset_durations"]
SC.check(_durs123[1] == _hp["s3_run2_duration_s"],
         "B0 packet: run-2 duration == %d s" % _hp["s3_run2_duration_s"])
R2 = Fraction(_durs123[1], _durs123[0])
SC.check(round(float(R2), 4) == _hp["run2_ratio_rounded_4dp"],
         "B0 packet: run-2 ratio rounds to %.4f (exact %s)" % (
             _hp["run2_ratio_rounded_4dp"], R2))
O6_FINAL = Fraction(_o6_durs[-1], _o6_durs[-2])
SC.check(round(float(O6_FINAL), 4) == _hp["o6_final_ratio_rounded_4dp"],
         "B0 packet: O6 final ratio rounds to %.4f (exact %s)" % (
             _hp["o6_final_ratio_rounded_4dp"], O6_FINAL))
_crit = {c["id"]: c["pass"] for c in REPORT["criteria"]}
SC.check(all(_crit["A%d" % i] for i in range(1, 10)),
         "B0 packet: A1..A9 all PASS at the pin (committed harness)")
SC.check(_crit["A10"] is False,
         "B0 packet: A10 FAIL under the strict literal reading (committed harness)")
_soft = B0["soft_from_packet"]["s3_resets_total_14d"]
_resets_total = REPORT["auxiliary"]["s3_resets_total"]
SC.check(abs(_resets_total - _soft["value"]) <= _soft["tolerance"],
         "B0 packet (soft ±%d): 14-day S3 resets total %d vs '~%d'" % (
             _soft["tolerance"], _resets_total, _soft["value"]))

SC.check(_meas["s3_first_purchase_t"] == _hv["A1_s3_first_purchase_t_s"],
         "B0 V006 pin: A1 first purchase t == 60 s")
SC.check(_meas["s3_purchases_by_900s"] == _hv["A2_s3_purchases_by_900s"],
         "B0 V006 pin: A2 purchases by 900 s == 12")
SC.check(_meas["s1_threshold_crossing_t"] == _hv["A4_s1_threshold_crossing_t_s"],
         "B0 V006 pin: A4 S1 threshold crossing == 100000 s")
SC.check(_meas["s2_2h_first_prestige_t"] == _hv["A5_s2_2h_first_prestige_t_s"],
         "B0 V006 pin: A5 S2(N=2) first prestige == 21600 s")
SC.check(_durs123 == _hv["s3_reset_durations_1_to_3"],
         "B0 V006 pin: S3 reset durations 1..3 == %s" % _hv["s3_reset_durations_1_to_3"])
_burst = REPORT["auxiliary"]["s2_visit_burst_minima"]
# Fixture AMENDMENT 1 (disclosed): V006's published (6,16) is the INCLUSIVE
# minimum (AMB-4 auxiliary); the strict-before values are reported and must
# still clear A7's own >= 2 band.
SC.check(_burst["N=2"]["including_prestige_visit"] == _hv["A7_min_levels_per_early_visit"]["N=2"]
         and _burst["N=8"]["including_prestige_visit"] == _hv["A7_min_levels_per_early_visit"]["N=8"],
         "B0 V006 pin: A7 INCLUSIVE burst minima (N=2,N=8) == (6,16) (fixture amendment 1)")
SC.check(_burst["N=2"]["strictly_before"] >= 2 and _burst["N=8"]["strictly_before"] >= 2,
         "B0: A7 strictly-before burst minima both >= 2 (the criterion's own band)")
SC.check(REPORT["auxiliary"]["s3_purchase_gaps"]["max_gap_between_purchases"]
         == _hv["A8_s3_max_purchase_gap_s"],
         "B0 V006 pin: A8 max purchase gap == 1215 s")
SC.check(_o6_awards[:3] == _hv["o6_awards_first_3"],
         "B0 V006 pin: O6 awards for resets 1..3 all == 1")

B0_VALID = True  # every check above raises on failure; reaching here == valid

# --------------------------------------------------------------------------
# ASK 1 — first-upgrade no-op: baseline felt table + registered arms.
# --------------------------------------------------------------------------

A1CFG = FIXTURE["ask1_first_upgrade_noop"]

RATE_TABLE = [{"level": L, "rate": rate_at(GEN, BOOST1, PRES, L)} for L in range(25)]
for row in RATE_TABLE:
    SC.check(row["rate"] == 1 + row["level"] // 4,
             "ask1: closed form rate(L)=1+L//4 confirmed at L=%d" % row["level"])

PURCHASE_FEEL = []
for k, p in enumerate(_first_run_purch, 1):
    t, _ri, level_after, cost, _bal = p
    rb, ra = rate_at(GEN, BOOST1, PRES, level_after - 1), rate_at(GEN, BOOST1, PRES, level_after)
    PURCHASE_FEEL.append({"purchase": k, "t": t, "cost": cost, "level_after": level_after,
                          "rate_before": rb, "rate_after": ra, "felt_delta": ra - rb})

FIRST_FELT = next(r["purchase"] for r in PURCHASE_FEEL if r["felt_delta"] > 0)
_first12 = PURCHASE_FEEL[:12]
_inert12 = [r for r in _first12 if r["felt_delta"] == 0]
INERT12_COUNT = len(_inert12)
INERT12_SPEND = Fraction(sum(r["cost"] for r in _inert12),
                         sum(r["cost"] for r in _first12))
SC.check(INERT12_COUNT == _hv["early_inert_purchases_of_first_12"],
         "B0 V006 pin: %d of the first 12 purchases are felt-inert" % INERT12_COUNT)
SC.check(FIRST_FELT == 4, "ask1: first FELT purchase is purchase 4 (levels 1-3 inert)")

_lvl_at_reset1 = _s3["resets_head"][0]["level_at_reset"]
SC.check(_lvl_at_reset1 == len(_first_run_purch),
         "ask1: run-1 purchase count == level at reset 1 (%d)" % _lvl_at_reset1)
FELT_FULL = sum(1 for r in PURCHASE_FEEL if r["felt_delta"] > 0)
FELT_SHARE_FULL = Fraction(FELT_FULL, len(PURCHASE_FEEL))
INERT_SPEND_FULL = Fraction(sum(r["cost"] for r in PURCHASE_FEEL if r["felt_delta"] == 0),
                            sum(r["cost"] for r in PURCHASE_FEEL))

ASK1_CONFIRMED = FIRST_FELT >= 2 and INERT12_SPEND >= Fraction(1, 2)

_bands = {"A1": (30, 180), "A3": (7200, 28800), "A4": (64800, 129600)}


def screen_arm(gen, up, pres, run, arm_desc):
    """A1/A2/A3/A4/A6 screening measures on a max_resets=1 run (fixture D5)."""
    purch = [p for p in run["purchases_through_reset_3"] if p[1] == 1]
    a1 = purch[0][0] if purch else None
    a2 = sum(1 for p in purch if p[0] <= 900)
    a3 = run["first_prestige_t"]
    r0 = fresh_rate(gen, up, pres, count=arm_desc.get("count", 1))
    a4 = ceil_div(THRESHOLD, r0)
    a6 = Fraction(a4, a3) if a3 else None
    ok = {"A1": a1 is not None and _bands["A1"][0] <= a1 <= _bands["A1"][1],
          "A2": a2 >= 5,
          "A3": a3 is not None and _bands["A3"][0] <= a3 <= _bands["A3"][1],
          "A4": _bands["A4"][0] <= a4 <= _bands["A4"][1],
          "A6": a6 is not None and Fraction(4) <= a6 <= Fraction(12)}
    r1_felt = rate_at(gen, up, pres, 1, count=arm_desc.get("count", 1)) > r0
    first_felt = None
    for L in range(1, 201):
        if rate_at(gen, up, pres, L, count=arm_desc.get("count", 1)) > \
           rate_at(gen, up, pres, L - 1, count=arm_desc.get("count", 1)):
            first_felt = L
            break
    return {**arm_desc, "purchase1_felt": r1_felt, "first_felt_purchase_index": first_felt,
            "A1_t": a1, "A2_count": a2, "A3_t": a3, "A4_t": a4,
            "A6": frac_fields(a6) if a6 else None,
            "in_band": ok, "all_screen_pass": all(ok.values()),
            "early_spend_purchases_1_3": sum(p[3] for p in purch[:3])}


ARMS1 = []
for E in A1CFG["arms"]["effect_percent"]:
    up2 = replace(BOOST1, effect_percent=E)
    run = HARNESS.simulate_s3(GEN, up2, PRES, max_resets=1)
    ARMS1.append(screen_arm(GEN, up2, PRES, run,
                            {"axis": "effect_percent", "value": E, "baseline": E == 25}))
for B in A1CFG["arms"]["base_rate"]:
    gen2 = GeneratorSpec(spec_id="tier1", produces=CUR, base_rate=B)
    up2 = ECON.build_upgrade_spec("boost1", gen2)  # engine's own cost rule: base_cost=B*60
    run = HARNESS.simulate_s3(gen2, up2, PRES, max_resets=1)
    ARMS1.append(screen_arm(gen2, up2, PRES, run,
                            {"axis": "base_rate", "value": B, "baseline": B == 1}))
# Seed-count arm: equivalence gate at C=1 first (fixture D10).
_var1 = s3_count_variant(GEN, BOOST1, PRES, count=1, max_resets=1)
_ref1 = HARNESS.simulate_s3(GEN, BOOST1, PRES, max_resets=1)
SC.check(_var1["purchases_through_reset_3"] == _ref1["purchases_through_reset_3"]
         and _var1["resets_head"] == _ref1["resets_head"]
         and _var1["first_prestige_t"] == _ref1["first_prestige_t"],
         "ask1: driver S3 count-variant ≡ vendored simulate_s3 at C=1 "
         "(exact purchase + reset trail)")
for C in A1CFG["arms"]["seed_count"]:
    run = s3_count_variant(GEN, BOOST1, PRES, count=C, max_resets=1)
    ARMS1.append(screen_arm(GEN, BOOST1, PRES, run,
                            {"axis": "seed_count", "value": C, "count": C,
                             "baseline": C == 1}))
for gn, gd in [tuple(v) for v in A1CFG["arms"]["growth_num_den"]]:
    up2 = replace(BOOST1, cost_growth_num=gn, cost_growth_den=gd)
    run = HARNESS.simulate_s3(GEN, up2, PRES, max_resets=1)
    ARMS1.append(screen_arm(GEN, up2, PRES, run,
                            {"axis": "growth", "value": "%d/%d" % (gn, gd),
                             "baseline": (gn, gd) == (115, 100)}))

# Registered closed-form predictions confirmed by the measured arms.
_min_felt = {}
for axis, base in (("effect_percent", 25), ("base_rate", 1), ("seed_count", 1)):
    vals = sorted(a["value"] for a in ARMS1 if a["axis"] == axis and a["purchase1_felt"])
    _min_felt[axis] = vals[0] if vals else None
SC.check(_min_felt["effect_percent"] == 100,
         "ask1 prediction: minimal felt EFFECT_PERCENT arm == 100")
SC.check(_min_felt["base_rate"] == 4, "ask1 prediction: minimal felt base_rate arm == 4")
SC.check(_min_felt["seed_count"] == 4, "ask1 prediction: minimal felt seed_count arm == 4")
SC.check(not any(a["purchase1_felt"] for a in ARMS1 if a["axis"] == "growth"),
         "ask1: growth axis is a non-lever for feltness (registered, confirmed)")

# Mechanical recommendation rule (fixture ask1 recommendation_rule).
_axis_base = {"effect_percent": 25, "base_rate": 1, "seed_count": 1}
_tie = {"effect_percent": 0, "base_rate": 1, "seed_count": 2}
_viable = []
for axis, mv in _min_felt.items():
    if mv is None:
        continue
    arm = next(a for a in ARMS1 if a["axis"] == axis and a["value"] == mv)
    if arm["all_screen_pass"]:
        mag = Fraction(max(mv, _axis_base[axis]), min(mv, _axis_base[axis]))
        _viable.append((mag, _tie[axis], axis, mv))
_viable.sort()
if _viable:
    ASK1_RECOMMENDATION = {"kind": "viable-minimal-arm",
                           "axis": _viable[0][2], "value": _viable[0][3]}
else:
    ASK1_RECOMMENDATION = {
        "kind": "min-visible-delta-floor",
        "detail": ("NO registered axis makes purchase 1 felt while keeping "
                   "A1/A2/A3/A4/A6 in-band — the registered fallback fires: the "
                   "packet's own third option, a min-visible-delta floor in the "
                   "effect fold (engine change, outside this sim's "
                   "no-reimplementation scope), routed with the per-axis felt "
                   "thresholds and their band damage as sizing evidence")}

# --------------------------------------------------------------------------
# ASK 2 — prestige payoff curve + registered lever arms.
# --------------------------------------------------------------------------

A2CFG = FIXTURE["ask2_prestige_payoff"]


def ladder_analysis(resets, bonus_percent):
    durs = [r["duration"] for r in resets]
    awards = [r["award"] for r in resets]
    cum_units = [r["prestige_after"] for r in resets]
    ratios = [Fraction(b, a) for a, b in zip(durs, durs[1:])]
    viol_drops = [ratios[i] - ratios[i + 1]
                  for i in range(len(ratios) - 1) if ratios[i + 1] < ratios[i]]
    strict_viol = [{"k": i + 3, "drop": frac_fields(ratios[i] - ratios[i + 1])}
                   for i in range(len(ratios) - 1) if ratios[i + 1] < ratios[i]]
    rows = []
    for i, r in enumerate(resets):
        rel_bonus = Fraction(bonus_percent, 100 + bonus_percent * (cum_units[i - 1] if i else 0))
        rows.append({"index": r["index"], "t": r["t"], "duration": r["duration"],
                     "award": r["award"], "cum_prestige_units": r["prestige_after"],
                     "cum_bonus_pct": 100 + bonus_percent * r["prestige_after"],
                     "ratio_to_prev": frac_fields(ratios[i - 1]) if i else None,
                     "felt_speedup": frac_fields(1 - ratios[i - 1]) if i else None,
                     "marginal_relative_bonus_at_award": frac_fields(rel_bonus)})
    tta = []
    for K in range(1, 21):
        hit = next((r["t"] for r in resets if r["prestige_after"] >= K), None)
        tta.append({"K": K, "t": hit})
    return {"rows": rows, "ratios": [frac_fields(x) for x in ratios],
            "viol_drops": viol_drops,
            "r2": ratios[0] if ratios else None,
            "r3": ratios[1] if len(ratios) > 1 else None,
            "r_last": ratios[-1] if ratios else None,
            "awards_all_1": all(a == 1 for a in awards),
            "strict_non_decreasing": not strict_viol,
            "strict_violations": strict_viol,
            "first_ratio": ratios[0] if ratios else None,
            "final_ratio": ratios[-1] if ratios else None,
            "trend_final_ge_first": bool(ratios) and ratios[-1] >= ratios[0],
            "time_to_award_K": tta}


BASE_LADDER = ladder_analysis(_o6rows_full := HARNESS.simulate_s3(
    GEN, BOOST1, PRES, max_resets=20)["resets_head"], _PARAMS["PRESTIGE_BONUS_PERCENT"])
# The dedicated ladder must BE the harness O6 ladder (same function, same args).
SC.check([r["duration"] for r in _o6rows_full] == _o6_durs,
         "ask2: dedicated 20-reset ladder ≡ the report's O6 ladder (durations)")
SC.check(BASE_LADDER["awards_all_1"],
         "ask2: every award across the 20-reset ladder == 1 (no award growth)")
# Engine cross-check of the marginal-bonus closed form at 5 units held.
SC.check(prestige_percent(GameState(prestige={"prestige": 5}), (PRES,)) == 150,
         "ask2: prestige_percent(5 units) == 150 (engine confirms +10%/unit)")

ASK2_CONFIRMED = ((1 - BASE_LADDER["r2"]) <= Fraction(1, 10)
                  and BASE_LADDER["awards_all_1"]
                  and BASE_LADDER["r_last"] >= BASE_LADDER["r2"])

ARMS2 = []
for bp in A2CFG["arms"]["prestige_bonus_percent"]:
    pres2 = PrestigeSpec(awards="prestige", measures=CUR, threshold=THRESHOLD,
                         award_divisor=_PARAMS["PRESTIGE_AWARD_DIVISOR"], bonus_percent=bp)
    lad = ladder_analysis(HARNESS.simulate_s3(GEN, BOOST1, pres2, max_resets=20)["resets_head"], bp)
    ARMS2.append({"axis": "prestige_bonus_percent", "value": bp, "baseline": bp == 10,
                  "ladder": lad})
for dv in A2CFG["arms"]["prestige_award_divisor"]:
    pres2 = PrestigeSpec(awards="prestige", measures=CUR, threshold=THRESHOLD,
                         award_divisor=dv,
                         bonus_percent=_PARAMS["PRESTIGE_BONUS_PERCENT"])
    lad = ladder_analysis(HARNESS.simulate_s3(GEN, BOOST1, pres2, max_resets=20)["resets_head"],
                          _PARAMS["PRESTIGE_BONUS_PERCENT"])
    ARMS2.append({"axis": "prestige_award_divisor", "value": dv, "baseline": dv == 100000,
                  "ladder": lad, "award_1": lad["rows"][0]["award"]})

_t9 = (Fraction(1, 2), Fraction(1))
_qual = []
_tie2 = {"prestige_bonus_percent": 0, "prestige_award_divisor": 1}
_base2 = {"prestige_bonus_percent": 10, "prestige_award_divisor": 100000}
for a in ARMS2:
    if a["baseline"]:
        continue
    lad = a["ladder"]
    if (lad["r2"] is not None and lad["r2"] <= Fraction(85, 100)
            and lad["r3"] is not None
            and _t9[0] <= lad["r2"] <= _t9[1] and _t9[0] <= lad["r3"] <= _t9[1]):
        mag = Fraction(max(a["value"], _base2[a["axis"]]), min(a["value"], _base2[a["axis"]]))
        _qual.append((mag, _tie2[a["axis"]], a["axis"], a["value"]))
_qual.sort()
ASK2_RECOMMENDATION = ({"kind": "qualifying-minimal-arm", "axis": _qual[0][2],
                        "value": _qual[0][3]} if _qual else
                       {"kind": "null-on-lever",
                        "detail": "no registered single-constant lever reaches r_2 <= 0.85 "
                                  "inside T9's band — the measured curve ships as the "
                                  "re-registration evidence (registered honest-NULL branch)"})

# --------------------------------------------------------------------------
# ASK 3 — A10 strict-vs-trend ruling + graduation, per the registered rule.
# --------------------------------------------------------------------------

A3CFG = FIXTURE["ask3_a10_ruling"]
WIGGLE = Fraction(str(A3CFG["wiggle_band"]))  # "0.02" -> exactly 1/50
SC.check(WIGGLE == Fraction(1, 50), "ask3: registered wiggle band parses to exactly 1/50")

_viol = BASE_LADDER["strict_violations"]
_viol_drops = BASE_LADDER["viol_drops"]
_max_drop = max(_viol_drops, default=Fraction(0))
_o6flag = REPORT["outputs"]["O6_prestige_stacking"]["super_geometric_shrinkage_flag"]

if BASE_LADDER["strict_non_decreasing"]:
    ASK3_RULING = "A10-PASS"
elif (all(d <= WIGGLE for d in _viol_drops)
      and BASE_LADDER["trend_final_ge_first"]
      and BASE_LADDER["final_ratio"] <= 1
      and _o6flag is False):
    ASK3_RULING = "TREND-PASS"
else:
    ASK3_RULING = "STRICT-FAIL-MATERIAL"

_a19_pass = all(_crit["A%d" % i] for i in range(1, 10))
if ASK3_RULING == "A10-PASS" and B0_VALID and _a19_pass:
    GRADUATION = "GRADUATE"
elif ASK3_RULING == "TREND-PASS" and B0_VALID and _a19_pass:
    GRADUATION = "GRADUATE-WITH-REWORDING"
else:
    GRADUATION = "NO-GRADUATE"

# --------------------------------------------------------------------------
# FEEL probes F1/F2/F3 per the registered bands.
# --------------------------------------------------------------------------

_early_ts = [p[0] for p in _first_run_purch if p[0] <= 900]
_early_gaps = [b - a for a, b in zip(_early_ts, _early_ts[1:])]
F1 = {"early_purchase_count": len(_early_ts),
      "median_early_gap_s": statistics.median(_early_gaps),
      "max_early_gap_s": max(_early_gaps),
      "a8_max_gap_s": _meas["s3_max_purchase_gap"],
      "a8_share": frac_fields(Fraction(_meas["s3_max_purchase_gap"],
                                       _meas["s3_first_prestige_t"])),
      "band_median": "<= 120 s", "band_a8": "< 25%"}
F1["pass_median"] = F1["median_early_gap_s"] <= 120
F1["pass_a8"] = Fraction(_meas["s3_max_purchase_gap"], _meas["s3_first_prestige_t"]) < Fraction(1, 4)

F2 = {"felt_share_first_12": frac_fields(Fraction(12 - INERT12_COUNT, 12)),
      "felt_share_full_run1": frac_fields(FELT_SHARE_FULL),
      "felt_inert_spend_share_first_12": frac_fields(INERT12_SPEND),
      "felt_inert_spend_share_full_run1": frac_fields(INERT_SPEND_FULL),
      "band": ">= 0.5 felt share, full run 1 (registered judgment line D9)"}
F2["pass"] = FELT_SHARE_FULL >= Fraction(1, 2)

_a6 = Fraction(_meas["s1_threshold_crossing_t"], _meas["s3_first_prestige_t"])
F3 = {"a6_ratio": frac_fields(_a6),
      "a7_min_levels": {"N=2": _burst["N=2"]["strictly_before"],
                        "N=8": _burst["N=8"]["strictly_before"]},
      "band_a6": "[4, 12]", "band_a7": ">= 2"}
F3["pass_a6"] = Fraction(4) <= _a6 <= Fraction(12)
F3["pass_a7"] = F3["a7_min_levels"]["N=2"] >= 2 and F3["a7_min_levels"]["N=8"] >= 2

# --------------------------------------------------------------------------
# Verdict mapping (fixture verdict_rule, evaluated in the registered order).
# --------------------------------------------------------------------------

if B0_VALID and (not _a19_pass or ASK3_RULING == "STRICT-FAIL-MATERIAL"):
    VERDICT = "reject"
elif B0_VALID and _a19_pass and _crit["A10"]:
    VERDICT = "approve"
elif B0_VALID and _a19_pass and ASK3_RULING == "TREND-PASS":
    VERDICT = "conditional"
else:
    VERDICT = "null"

# --------------------------------------------------------------------------
# Results + summary.
# --------------------------------------------------------------------------

RESULTS = {
    "sim": "verdict-038-idle-economy-feel",
    "engine_pin": PIN,
    "runtime_python": platform.python_version(),
    "harness_full_report_sha256": REPORT_SHA,
    "b0": {
        "valid": B0_VALID,
        "first_three_costs": _first3_costs,
        "rate_by_level_L0_L5": _rates_l0_l5,
        "s3_first_prestige_t": _meas["s3_first_prestige_t"],
        "s3_reset_durations_1_to_3": _durs123,
        "run2_ratio": frac_fields(R2),
        "o6_final_ratio": frac_fields(O6_FINAL),
        "criteria": {c["id"]: c["pass"] for c in REPORT["criteria"]},
        "criteria_detail": REPORT["criteria"],
        "s3_resets_total_14d": _resets_total,
        "s2_2h_first_prestige_t": _meas["s2_2h_first_prestige_t"],
        "s1_threshold_crossing_t": _meas["s1_threshold_crossing_t"],
        "a8_max_gap_s": _meas["s3_max_purchase_gap"],
        "a7_burst_minima": {"N=2": _burst["N=2"], "N=8": _burst["N=8"]},
    },
    "ask1": {
        "confirmed_inert": ASK1_CONFIRMED,
        "rate_table_L0_L24": RATE_TABLE,
        "purchase_feel_run1": PURCHASE_FEEL,
        "first_felt_purchase": FIRST_FELT,
        "inert_of_first_12": INERT12_COUNT,
        "inert_spend_share_first_12": frac_fields(INERT12_SPEND),
        "felt_share_full_run1": frac_fields(FELT_SHARE_FULL),
        "inert_spend_share_full_run1": frac_fields(INERT_SPEND_FULL),
        "run1_purchases": len(PURCHASE_FEEL),
        "min_felt_value_per_axis": _min_felt,
        "arms": ARMS1,
        "recommendation": ASK1_RECOMMENDATION,
    },
    "ask2": {
        "weak_payoff_confirmed": ASK2_CONFIRMED,
        "baseline_ladder": {k: v for k, v in BASE_LADDER.items()
                            if k not in ("r2", "r3", "r_last", "first_ratio", "final_ratio")},
        "r2": frac_fields(BASE_LADDER["r2"]),
        "felt_speedup_run2": frac_fields(1 - BASE_LADDER["r2"]),
        "arms": [{**{k: v for k, v in a.items() if k != "ladder"},
                  "r2": frac_fields(a["ladder"]["r2"]),
                  "r3": frac_fields(a["ladder"]["r3"]),
                  "awards_all_1": a["ladder"]["awards_all_1"],
                  "award_1": a["ladder"]["rows"][0]["award"],
                  "strict_non_decreasing": a["ladder"]["strict_non_decreasing"],
                  "trend_final_ge_first": a["ladder"]["trend_final_ge_first"],
                  "final_ratio": frac_fields(a["ladder"]["final_ratio"]),
                  "ladder_durations": [r["duration"] for r in a["ladder"]["rows"]]}
                 for a in ARMS2],
        "recommendation": ASK2_RECOMMENDATION,
    },
    "ask3": {
        "ruling": ASK3_RULING,
        "graduation": GRADUATION,
        "strict_violations": _viol,
        "violation_count": len(_viol),
        "max_single_step_drop": frac_fields(_max_drop),
        "wiggle_band": frac_fields(WIGGLE),
        "first_ratio": frac_fields(BASE_LADDER["first_ratio"]),
        "final_ratio": frac_fields(BASE_LADDER["final_ratio"]),
        "super_geometric_shrinkage_flag": _o6flag,
        "aux_resets_total_14d": _resets_total,
    },
    "feel_probes": {"F1_session_pacing": F1, "F2_meaningful_choice_cadence": F2,
                    "F3_idle_vs_active_balance": F3},
    "v017_chain": {
        "generator_purchase_path_at_pin": False,
        "generator_dependent_probes": "NULL by premise (honest NULL) — T10/A11 remain "
                                      "V017's conditional row (C2=900, R2=5, T10=1948 s)",
        "feeds": "fm owner-queue E#52 (with V017)",
    },
    "verdict": VERDICT,
    "seeds": {"drawn": 0, "fleet_high_water": 20260775, "note": "NO RNG anywhere"},
}


def _default(o):
    if isinstance(o, Fraction):
        return {"exact": "%d/%d" % (o.numerator, o.denominator), "approx": float(o)}
    raise TypeError(repr(o))


def main() -> int:
    payload = json.dumps(RESULTS, sort_keys=True, indent=1, default=_default) + "\n"
    with open(os.path.join(BASE_DIR, "results.json"), "w", encoding="utf-8") as fh:
        fh.write(payload)
    print("VERDICT 038 — idle economy FEEL sim @ %s" % PIN[:7])
    print("B0 baseline validity: VALID (every packet + V006 anchor reproduced exactly; "
          "soft anchor: %d resets vs ~80796)" % _resets_total)
    print("ASK1 first-upgrade no-op: %s — first felt purchase #%d; %d/12 early "
          "purchases inert (%.1f%% of early spend); felt share full run 1 = %s "
          "(%.1f%%); minimal felt arms: E=%s, base_rate=%s, count=%s; "
          "recommendation: %s"
          % ("CONFIRMED-INERT" if ASK1_CONFIRMED else "NOT-CONFIRMED",
             FIRST_FELT, INERT12_COUNT, 100 * float(INERT12_SPEND),
             frac_fields(FELT_SHARE_FULL)["exact"], 100 * float(FELT_SHARE_FULL),
             _min_felt["effect_percent"], _min_felt["base_rate"],
             _min_felt["seed_count"], ASK1_RECOMMENDATION["kind"]))
    print("ASK2 weak prestige payoff: %s — r2 = %s (%.2f%% faster), awards all 1 "
          "across 20 resets, r20 = %s; recommendation: %s"
          % ("CONFIRMED" if ASK2_CONFIRMED else "NOT-CONFIRMED",
             frac_fields(BASE_LADDER["r2"])["exact"],
             100 * float(1 - BASE_LADDER["r2"]),
             frac_fields(BASE_LADDER["r_last"])["exact"],
             json.dumps(ASK2_RECOMMENDATION, sort_keys=True)))
    print("ASK3 A10 ruling: %s — %d strict violations, max drop %s (band 1/50); "
          "trend %s -> %s rising; flag %s; graduation: %s"
          % (ASK3_RULING, len(_viol), frac_fields(_max_drop)["exact"],
             frac_fields(BASE_LADDER["first_ratio"])["exact"],
             frac_fields(BASE_LADDER["final_ratio"])["exact"], _o6flag, GRADUATION))
    print("FEEL: F1 median early gap %ss (<=120: %s), A8 share %.4f (<25%%: %s) | "
          "F2 felt share %.4f (>=0.5: %s) | F3 A6 %.4f in [4,12]: %s, A7 (%d,%d)>=2: %s"
          % (F1["median_early_gap_s"], F1["pass_median"],
             F1["a8_share"]["approx"], F1["pass_a8"],
             F2["felt_share_full_run1"]["approx"], F2["pass"],
             F3["a6_ratio"]["approx"], F3["pass_a6"],
             F3["a7_min_levels"]["N=2"], F3["a7_min_levels"]["N=8"], F3["pass_a7"]))
    print("VERDICT (registered mapping, REJECT-first order): %s" % VERDICT)
    print("harness full-report sha256: %s" % REPORT_SHA)
    return SC.report()


if __name__ == "__main__":
    raise SystemExit(main())
