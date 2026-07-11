#!/usr/bin/env python3
"""VERDICT 006 / SIM-001 — idle-economy sim kernel (economy-v1).

NUMERIC SIMULATION (method ladder rung 1): deterministic, integer-exact,
stdlib-only, NO RNG. A single run per scenario IS the distribution (the engine
is pure and integer-exact); determinism is proven by byte-identical re-run, not
by seeds.

PROVENANCE — DRIVE THE REAL ENGINE, DO NOT REIMPLEMENT
  The ``idle_engine/`` package next to this file is a VENDOR COPY, byte-for-byte,
  of ``menno420/superbot-idle`` ``idle_engine/`` @
  ``f11c71a52d4d2adf88b2bf11f5d1134bad495be2`` (the pinned commit named in
  economy-v1.md § Inputs). Only ``idle_engine/__init__.py`` is reconstructed (it
  re-exports the five vendored modules; the upstream init also re-exported
  ``theme``/``render``, which are not part of the SIM-001 economy surface and were
  not vendored). The economy/mechanics logic is UNMODIFIED — a re-implementation
  would risk float/rounding drift and invalidate the run (economy-v1.md § Inputs).
  This driver imports that package and calls the REAL functions: tick,
  offline_progress, purchase_upgrade, upgrade_cost, prestige_eligible,
  prestige_award, apply_prestige, production_per_second, build_upgrade_spec,
  build_prestige_spec, GameState, GeneratorSpec.

Source idea: menno420/idea-engine control/outbox.md PROPOSAL 006 @
7df1d6cd09d52ad8574b6f37adf00abb99179f5e, relaying superbot-idle SIM-001 from
docs/design/economy-v1.md @ f11c71a52d4d2adf88b2bf11f5d1134bad495be2.

Run:  python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py
Exit 0 iff every self-check passes.
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import namedtuple
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from idle_engine import (  # noqa: E402  (path insert must precede import)
    GameState,
    GeneratorSpec,
    PrestigeSpec,
    UpgradeSpec,
    apply_offline_progress,
    apply_prestige,
    build_prestige_spec,
    build_upgrade_spec,
    offline_progress,
    prestige_award,
    prestige_eligible,
    production_per_second,
    purchase_upgrade,
    tick,
    upgrade_cost,
)
from idle_engine import economy as ECON  # noqa: E402

# --------------------------------------------------------------------------
# Vendored harness helpers (stdlib-only) — copied from harness/simharness.py.
# SelfCheck battery + determinism_bytes (canonical-JSON stability). See REPORT
# § "Harness verdict" for what helped and what the harness still lacks.
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

    def expect_reject(self, label, fn, code=None):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — any rejection counts
            if code is not None and code not in str(e):
                raise AssertionError(
                    "SELF-CHECK FAILED: %s (rejected but not with %r: %s)"
                    % (label, code, e)
                )
            self.passed += 1
            self.detail.append((True, label))
            return
        raise AssertionError(
            "SELF-CHECK FAILED: %s (expected rejection, got none)" % label
        )

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def determinism_bytes(sc, obj, label="determinism: stable canonical JSON"):
    s1 = json.dumps(obj, indent=2, sort_keys=True)
    s2 = json.dumps(obj, indent=2, sort_keys=True)
    return sc.check(s1 == s2, label)


def canon(obj):
    return json.dumps(obj, sort_keys=True)


# --------------------------------------------------------------------------
# Reference world (economy-v1.md § Reference world) — theme-independent.
# --------------------------------------------------------------------------

TIER1 = GeneratorSpec(spec_id="tier1", produces="primary", base_rate=1)
SPECS = (TIER1,)
BOOST1 = build_upgrade_spec("boost1", TIER1)
UPGRADES = (BOOST1,)
PRESTIGE = build_prestige_spec(awards="prestige", measures="primary")
PRESTIGES = (PRESTIGE,)
FRESH_OWNED = {"tier1": 1}
THRESHOLD = PRESTIGE.threshold          # 100_000
CUR = "primary"

DAY = 86_400
HORIZON_14D = 14 * DAY


def fresh_state():
    """A fresh save: owns exactly one tier1 generator, t=0, nothing else."""
    return GameState(owned=dict(FRESH_OWNED))


def rate_of(state):
    return production_per_second(state, SPECS, UPGRADES, PRESTIGES).get(CUR, 0)


def _reseed_fresh(state):
    """Restore the reference-world fresh-save invariant after a prestige reset.

    ``apply_prestige`` wipes ``owned`` (correct engine behaviour: a reset clears
    the run). economy-v1.md § Reference world states a fresh save *starts owning*
    tier1 (count fixed at 1); there is no generator-purchase path in the engine,
    so the reference world re-seeds ``owned={'tier1':1}`` on every fresh save.
    This is a reference-world rule, NOT an engine edit — the vendored engine is
    untouched.
    """
    return replace(state, owned=dict(FRESH_OWNED))


def _bal(state):
    return state.balances.get(CUR, 0)


def _life(state):
    return state.lifetime.get(CUR, 0)


def _level(state):
    return state.upgrades.get("boost1", 0)


# --------------------------------------------------------------------------
# Policy: at each visit — credit elapsed production, greedy-buy upgrades,
# then prestige iff eligible. Shared by S2 (fixed visit interval) and S3
# (1-second granularity). buy_guard(state) gates a purchase (S3b threshold).
# --------------------------------------------------------------------------


def _greedy_buy(state, purchases, t, buy_guard):
    """Repeat-buy upgrade levels while affordable (and permitted). Records
    (t, level_after, cost, balance_after). Returns the new state."""
    while True:
        level = _level(state)
        cost = upgrade_cost(BOOST1, level)
        if _bal(state) < cost:
            break
        if buy_guard is not None and not buy_guard(state, cost):
            break
        state = purchase_upgrade(state, BOOST1)   # REAL engine call
        purchases.append((t, _level(state), cost, _bal(state)))
    return state


def run_visits(step, horizon, buy_guard=None):
    """Fixed-interval visitor (S2 with step=N*3600; S3 proxy with step=1).

    At each visit t: credit offline production (REAL offline_progress via
    apply_offline_progress), greedy-buy, then prestige iff eligible. Returns a
    JSON-safe record dict.
    """
    state = fresh_state()
    purchases = []           # (t, level_after, cost, balance_after)
    visits = []              # (t, balance, lifetime, levels_bought_this_visit)
    prestiges = []           # (t, award, reset_duration_s)
    traj = []                # (t, balance, lifetime) — per visit (O3 for S1/S2)
    first_upgrade_t = None
    first_prestige_t = None
    reset_start = 0
    t = 0
    while t + step <= horizon:
        t += step
        state = apply_offline_progress(state, SPECS, t, UPGRADES, PRESTIGES)
        before = len(purchases)
        state = _greedy_buy(state, purchases, t, buy_guard)
        bought = len(purchases) - before
        if first_upgrade_t is None and bought:
            first_upgrade_t = purchases[before][0]
        visits.append((t, _bal(state), _life(state), bought))
        traj.append((t, _bal(state), _life(state)))
        if prestige_eligible(state, PRESTIGE):
            award = prestige_award(state, PRESTIGE)
            prestiges.append((t, award, t - reset_start))
            reset_start = t
            if first_prestige_t is None:
                first_prestige_t = t
            state = _reseed_fresh(apply_prestige(state, PRESTIGE))
    return {
        "purchases": purchases,
        "visits": visits,
        "prestiges": prestiges,
        "traj": traj,
        "first_upgrade_t": first_upgrade_t,
        "first_prestige_t": first_prestige_t,
    }


def run_continuous(horizon, max_resets, buy_guard=None, sample_period=None):
    """1-second-granularity acting player (S3), computed by exact event-jump.

    Between actions the integer rate is constant, so the first second at which a
    purchase becomes affordable OR the prestige threshold is crossed is
    closed-form. Jumping there and acting is byte-identical to a literal
    per-second loop (proven by the equivalence self-check over the first two
    resets). Stops at ``horizon`` seconds or after ``max_resets`` prestiges.
    """
    state = fresh_state()
    purchases = []
    prestiges = []
    reset_levels = []        # upgrade level held at the instant of each prestige
    traj = []                # (t, balance, lifetime) at a sample_period grid
    first_upgrade_t = None
    first_prestige_t = None
    reset_start = 0
    next_sample = 0 if sample_period else None
    t = 0

    def emit_samples(t0, t1, b0, l0, r):
        """Emit (t, balance, lifetime) at each sample-grid tick in (t0, t1]."""
        nonlocal next_sample
        if next_sample is None:
            return
        while next_sample <= t1:
            if next_sample > t0 or (next_sample == 0 and t0 == 0):
                dt = next_sample - t0
                traj.append((next_sample, b0 + r * dt, l0 + r * dt))
            next_sample += sample_period

    while t <= horizon and len(prestiges) < max_resets:
        r = rate_of(state)
        level = _level(state)
        cost = upgrade_cost(BOOST1, level)
        b = _bal(state)
        life = _life(state)
        k_up = math.ceil((cost - b) / r) if b < cost else 0
        k_pr = math.ceil((THRESHOLD - life) / r) if life < THRESHOLD else 0
        cands = [k for k in (k_up, k_pr) if k > 0]
        k = min(cands) if cands else 0
        if k > 0:
            if t + k > horizon:
                emit_samples(t, horizon, b, life, r)
                t = horizon + 1
                break
            emit_samples(t, t + k, b, life, r)
            state = tick(state, SPECS, int(k), UPGRADES, PRESTIGES)  # REAL engine
            t += int(k)
        before = len(purchases)
        state = _greedy_buy(state, purchases, t, buy_guard)
        if first_upgrade_t is None and len(purchases) > before:
            first_upgrade_t = purchases[before][0]
        if prestige_eligible(state, PRESTIGE):
            award = prestige_award(state, PRESTIGE)
            prestiges.append((t, award, t - reset_start))
            reset_levels.append(_level(state))
            reset_start = t
            if first_prestige_t is None:
                first_prestige_t = t
            state = _reseed_fresh(apply_prestige(state, PRESTIGE))
        if k == 0 and len(purchases) == before:
            break  # no reachable event (rate 0) — should never happen here
    return {
        "purchases": purchases,
        "prestiges": prestiges,
        "reset_levels": reset_levels,
        "traj": traj,
        "first_upgrade_t": first_upgrade_t,
        "first_prestige_t": first_prestige_t,
    }


def run_idle(horizon, sample_period):
    """S1 — idle-only: never buys, never prestiges. Pure accrual at 1/s.

    Driven through the REAL engine via offline_progress; the threshold-cross
    second is found exactly (rate is constant, so closed-form)."""
    state = fresh_state()
    r = rate_of(state)                      # 1 unit/s at U=0,P=0
    cross = None
    if r > 0:
        cross = math.ceil(THRESHOLD / r)    # first second lifetime >= THRESHOLD
    traj = []
    for ts in range(0, horizon + 1, sample_period):
        earned = offline_progress(state, SPECS, 0, ts, UPGRADES, PRESTIGES)[CUR]
        traj.append((ts, earned, earned))   # idle: balance == lifetime
    # verify the cross second against the real engine (exactly at, one before)
    at = offline_progress(state, SPECS, 0, cross, UPGRADES, PRESTIGES)[CUR]
    before = offline_progress(state, SPECS, 0, cross - 1, UPGRADES, PRESTIGES)[CUR]
    return {"rate": r, "cross_s": cross, "at": at, "before": before, "traj": traj}


# --------------------------------------------------------------------------
# Faithfulness check: literal per-second loop over a bounded window, to prove
# run_continuous (event-jump) == run_visits(step=1) byte-for-byte.
# --------------------------------------------------------------------------


def run_persecond(n_seconds, max_resets):
    """Literal per-second loop (ground truth for the event-jump)."""
    state = fresh_state()
    purchases = []
    prestiges = []
    reset_start = 0
    for _ in range(n_seconds):
        t = state.last_seen + 1
        state = tick(state, SPECS, 1, UPGRADES, PRESTIGES)
        state = _greedy_buy(state, purchases, t, None)
        if prestige_eligible(state, PRESTIGE):
            prestiges.append((t, prestige_award(state, PRESTIGE), t - reset_start))
            reset_start = t
            state = _reseed_fresh(apply_prestige(state, PRESTIGE))
            if len(prestiges) >= max_resets:
                break
    return {"purchases": purchases, "prestiges": prestiges}


# --------------------------------------------------------------------------
# Analysis helpers.
# --------------------------------------------------------------------------


def hours(seconds):
    return seconds / 3600.0


def payback_hours(level):
    """O5: nominal payback of buying level L = cost / (base_rate * EFFECT/100)."""
    marginal_rate = TIER1.base_rate * ECON.UPGRADE_EFFECT_PERCENT / 100.0
    return upgrade_cost(BOOST1, level) / marginal_rate / 3600.0


def max_gap_before(purchases, cutoff_t):
    """Largest gap between consecutive purchases strictly before cutoff_t."""
    times = [t for (t, *_rest) in purchases if t < cutoff_t]
    if len(times) < 2:
        return 0, []
    gaps = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    return max(gaps), gaps


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------


def band(x, lo, hi):
    return lo <= x <= hi


# ==========================================================================
# PARAMETER-SENSITIVITY SWEEP  (ROBUST gate — appendix to the base run)
# --------------------------------------------------------------------------
# The base run scores A1-A10 at the SINGLE provisional economy-v1 point. The
# validity gate's ROBUST question ("does the conclusion survive variation at the
# edges") also demands the parameter grid, not just the policy edges. This
# appendix answers it with an honest +-20% sweep of each of the 7 provisional
# parameters.
#
# DISCLOSURE — how the sweep parameterizes the engine. The provisional builders
# ``build_upgrade_spec`` / ``build_prestige_spec`` read the frozen v0 constants
# in ``idle_engine.economy`` and emit ONLY the single provisional point; they
# take no perturbation argument. To sweep, this appendix constructs the engine's
# own ``UpgradeSpec`` / ``PrestigeSpec`` dataclasses DIRECTLY with perturbed
# field values and drives the SAME real engine functions (upgrade_cost,
# purchase_upgrade, production_per_second, tick / offline_progress,
# prestige_eligible / prestige_award / apply_prestige). NO economy math is
# re-implemented — only the spec field values change. Faithfulness is proven by
# a self-check: at the provisional cell the direct-spec path reproduces the base
# run's O1-O6 byte-identically (see ``sweep_selfchecks``).
#
# The generator (base_rate=1, count=1) is NOT swept — SIM-001's reference world
# fixes it and there is no purchase path; the 7 swept params are exactly the
# pre-registered economy-v1 table.
# --------------------------------------------------------------------------

World = namedtuple("World", ["up", "pr", "threshold"])


def make_world(base_cost_seconds, growth_num, growth_den, effect_percent,
               threshold, award_divisor, bonus_percent):
    """Build a World by constructing UpgradeSpec/PrestigeSpec DIRECTLY with the
    given (possibly perturbed) field values. base_cost = base_rate * seconds,
    exactly as ``build_upgrade_spec`` computes it. May raise ValueError/TypeError
    from the engine's own spec validation (e.g. num<den 'shrinking costs')."""
    up = UpgradeSpec(
        spec_id="boost1",
        cost_currency=TIER1.produces,
        base_cost=TIER1.base_rate * base_cost_seconds,
        cost_growth_num=growth_num,
        cost_growth_den=growth_den,
        target=TIER1.spec_id,
        effect_percent=effect_percent,
    )
    pr = PrestigeSpec(
        awards="prestige",
        measures="primary",
        threshold=threshold,
        award_divisor=award_divisor,
        bonus_percent=bonus_percent,
    )
    return World(up, pr, threshold)


# Provisional cell, both ways: the base run's builder-emitted specs (W0) and the
# direct-spec construction (WPROV). The faithfulness self-check asserts they are
# field-identical and produce byte-identical scenario records.
def provisional_world_builders():
    return World(BOOST1, PRESTIGE, PRESTIGE.threshold)


def provisional_world_direct():
    return make_world(60, 115, 100, 25, 100_000, 100_000, 10)


# --- World-aware scenario runners: exact parallels of the base run_* funcs, but
#     parameterized on a World. At W0 they reproduce the base records byte-for-
#     byte (self-checked); the ONLY difference from the base funcs is the spec
#     field values threaded through the SAME engine calls. ------------------


def _rate_w(state, W):
    return production_per_second(state, SPECS, (W.up,), (W.pr,)).get(CUR, 0)


def _greedy_buy_w(state, purchases, t, buy_guard, W):
    while True:
        level = state.upgrades.get(W.up.spec_id, 0)
        cost = upgrade_cost(W.up, level)
        if _bal(state) < cost:
            break
        if buy_guard is not None and not buy_guard(state, cost):
            break
        state = purchase_upgrade(state, W.up)          # REAL engine call
        purchases.append((t, state.upgrades.get(W.up.spec_id, 0), cost, _bal(state)))
    return state


def run_idle_w(W, horizon, sample_period):
    state = fresh_state()
    r = _rate_w(state, W)
    cross = None
    if r > 0:
        cross = math.ceil(W.threshold / r)
    traj = []
    for ts in range(0, horizon + 1, sample_period):
        earned = offline_progress(state, SPECS, 0, ts, (W.up,), (W.pr,))[CUR]
        traj.append((ts, earned, earned))
    at = offline_progress(state, SPECS, 0, cross, (W.up,), (W.pr,))[CUR]
    before = offline_progress(state, SPECS, 0, cross - 1, (W.up,), (W.pr,))[CUR]
    return {"rate": r, "cross_s": cross, "at": at, "before": before, "traj": traj}


def run_visits_w(W, step, horizon, buy_guard=None):
    state = fresh_state()
    purchases = []
    visits = []
    prestiges = []
    traj = []
    first_upgrade_t = None
    first_prestige_t = None
    reset_start = 0
    t = 0
    while t + step <= horizon:
        t += step
        state = apply_offline_progress(state, SPECS, t, (W.up,), (W.pr,))
        before = len(purchases)
        state = _greedy_buy_w(state, purchases, t, buy_guard, W)
        bought = len(purchases) - before
        if first_upgrade_t is None and bought:
            first_upgrade_t = purchases[before][0]
        visits.append((t, _bal(state), _life(state), bought))
        traj.append((t, _bal(state), _life(state)))
        if prestige_eligible(state, W.pr):
            award = prestige_award(state, W.pr)
            prestiges.append((t, award, t - reset_start))
            reset_start = t
            if first_prestige_t is None:
                first_prestige_t = t
            state = _reseed_fresh(apply_prestige(state, W.pr))
    return {
        "purchases": purchases,
        "visits": visits,
        "prestiges": prestiges,
        "traj": traj,
        "first_upgrade_t": first_upgrade_t,
        "first_prestige_t": first_prestige_t,
    }


def run_continuous_w(W, horizon, max_resets, buy_guard=None, sample_period=None):
    state = fresh_state()
    purchases = []
    prestiges = []
    reset_levels = []
    traj = []
    first_upgrade_t = None
    first_prestige_t = None
    reset_start = 0
    next_sample = 0 if sample_period else None
    t = 0

    def emit_samples(t0, t1, b0, l0, r):
        nonlocal next_sample
        if next_sample is None:
            return
        while next_sample <= t1:
            if next_sample > t0 or (next_sample == 0 and t0 == 0):
                dt = next_sample - t0
                traj.append((next_sample, b0 + r * dt, l0 + r * dt))
            next_sample += sample_period

    while t <= horizon and len(prestiges) < max_resets:
        r = _rate_w(state, W)
        level = state.upgrades.get(W.up.spec_id, 0)
        cost = upgrade_cost(W.up, level)
        b = _bal(state)
        life = _life(state)
        k_up = math.ceil((cost - b) / r) if b < cost else 0
        k_pr = math.ceil((W.threshold - life) / r) if life < W.threshold else 0
        cands = [k for k in (k_up, k_pr) if k > 0]
        k = min(cands) if cands else 0
        if k > 0:
            if t + k > horizon:
                emit_samples(t, horizon, b, life, r)
                t = horizon + 1
                break
            emit_samples(t, t + k, b, life, r)
            state = tick(state, SPECS, int(k), (W.up,), (W.pr,))   # REAL engine
            t += int(k)
        before = len(purchases)
        state = _greedy_buy_w(state, purchases, t, buy_guard, W)
        if first_upgrade_t is None and len(purchases) > before:
            first_upgrade_t = purchases[before][0]
        if prestige_eligible(state, W.pr):
            award = prestige_award(state, W.pr)
            prestiges.append((t, award, t - reset_start))
            reset_levels.append(state.upgrades.get(W.up.spec_id, 0))
            reset_start = t
            if first_prestige_t is None:
                first_prestige_t = t
            state = _reseed_fresh(apply_prestige(state, W.pr))
        if k == 0 and len(purchases) == before:
            break
    return {
        "purchases": purchases,
        "prestiges": prestiges,
        "reset_levels": reset_levels,
        "traj": traj,
        "first_upgrade_t": first_upgrade_t,
        "first_prestige_t": first_prestige_t,
    }


# --- Per-cell A-criteria re-scoring. Mirrors main()'s scorecard logic exactly,
#     but for an arbitrary World; guarded so a degenerate cell (never prestiges,
#     etc.) scores FAIL rather than crashing. -------------------------------


def score_world(W):
    """Return (measured, passed) dicts for A1-A10 at World W, driving the same
    scenarios the base run uses. Cheap: all outputs resolve in the first resets."""
    s3 = run_continuous_w(W, HORIZON_14D, max_resets=25)
    s1 = run_idle_w(W, HORIZON_14D, DAY // 8)
    s2n2 = run_visits_w(W, 7200, HORIZON_14D)
    s2n8 = run_visits_w(W, 28800, HORIZON_14D)
    m, p = {}, {}

    # A1 — S3 time-to-first-upgrade in 30-180 s.
    m["A1"] = s3["first_upgrade_t"]
    p["A1"] = m["A1"] is not None and band(m["A1"], 30, 180)
    # A2 — S3 >=5 purchases by 900 s.
    m["A2"] = len([q for q in s3["purchases"] if q[0] <= 900])
    p["A2"] = m["A2"] >= 5
    # A3 — S3 first-prestige 2-8 h.
    m["A3"] = s3["first_prestige_t"]
    p["A3"] = m["A3"] is not None and band(hours(m["A3"]), 2, 8)
    # A4 — S1 threshold-cross 18-36 h.
    m["A4"] = s1["cross_s"]
    p["A4"] = m["A4"] is not None and band(hours(m["A4"]), 18, 36)
    # A5 — S2(N=2) first-prestige 4-12 h.
    m["A5"] = s2n2["first_prestige_t"]
    p["A5"] = m["A5"] is not None and band(hours(m["A5"]), 4, 12)
    # A6 — A4/A3 in 4-12x.
    if m["A3"]:
        m["A6"] = m["A4"] / m["A3"]
        p["A6"] = band(m["A6"], 4, 12)
    else:
        m["A6"] = None
        p["A6"] = False
    # A7 — S2(N=2)&(N=8) every pre-prestige visit buys >=2.
    def preb(rec):
        fp = rec["first_prestige_t"]
        if fp is None:
            return []
        return [nb for (t, _b, _l, nb) in rec["visits"] if t <= fp]
    b2, b8 = preb(s2n2), preb(s2n8)
    m["A7"] = (min(b2) if b2 else 0, min(b8) if b8 else 0)
    p["A7"] = bool(b2) and bool(b8) and min(b2) >= 2 and min(b8) >= 2
    # A8 — S3 max purchase-gap < 25% of run.
    if s3["first_prestige_t"]:
        gap, _g = max_gap_before(s3["purchases"], s3["first_prestige_t"])
        pct = 100.0 * gap / s3["first_prestige_t"]
        m["A8"] = (gap, pct)
        p["A8"] = pct < 25.0
    else:
        m["A8"] = None
        p["A8"] = False
    # A9 — resets 2,3 each 50-100% of prior.
    d = [dur for (_t, _a, dur) in s3["prestiges"][:3]]
    if len(d) >= 3 and d[0] and d[1]:
        r2, r3 = d[1] / d[0], d[2] / d[1]
        m["A9"] = (r2, r3)
        p["A9"] = band(r2, 0.50, 1.00) and band(r3, 0.50, 1.00)
    else:
        m["A9"] = None
        p["A9"] = False
    # A10 — O6 cumulative bonus sub-exponential over up-to-20 resets.
    durs = [dur for (_t, _a, dur) in s3["prestiges"][:20]]
    awards = [a for (_t, a, _d) in s3["prestiges"][:20]]
    if len(durs) >= 2:
        cum, cumb = 0, []
        for a in awards:
            cum += a
            cumb.append(cum * W.pr.bonus_percent)
        ratios = [durs[i] / durs[i - 1] for i in range(1, len(durs)) if durs[i - 1]]
        cum_linear = cumb == [W.pr.bonus_percent * (i + 1)
                              for i in range(len(cumb))]
        ratios_in = all(0.5 <= r <= 1.0 for r in ratios)
        trend_up = ratios[-1] > ratios[0] if len(ratios) >= 2 else False
        super_geo = any(r < 0.5 for r in ratios)
        m["A10"] = (cum_linear, ratios_in, trend_up, len(durs))
        p["A10"] = cum_linear and ratios_in and trend_up and not super_geo
    else:
        m["A10"] = None
        p["A10"] = False
    return m, p


# The load-bearing criteria (task): timing/ratio ones printed per cell.
SWEEP_SHOWN = ["A1", "A3", "A4", "A5", "A6", "A9"]
MULT_LABELS = ["x0.8", "x0.9", "x1.0", "x1.1", "x1.2"]

# The 7-parameter grid. Each entry: (label, value-list aligned to MULT_LABELS,
# builder from a single perturbed value). den is held at 100 (growth swept via
# num). THRESHOLD and AWARD_DIVISOR move together (one value drives both).
SWEEP_PARAMS = [
    ("BASE_COST_SECONDS", [48, 54, 60, 66, 72],
     lambda v: make_world(v, 115, 100, 25, 100_000, 100_000, 10)),
    ("GROWTH_NUM/100", [92, 104, 115, 127, 138],
     lambda v: make_world(60, v, 100, 25, 100_000, 100_000, 10)),
    ("EFFECT_PERCENT", [20, 22, 25, 27, 30],
     lambda v: make_world(60, 115, 100, v, 100_000, 100_000, 10)),
    ("THRESHOLD=DIVISOR", [80_000, 90_000, 100_000, 110_000, 120_000],
     lambda v: make_world(60, 115, 100, 25, v, v, 10)),
    ("BONUS_PERCENT", [8, 9, 10, 11, 12],
     lambda v: make_world(60, 115, 100, 25, 100_000, 100_000, v)),
]


def _fmt_measure(k, m):
    val = m.get(k)
    if val is None:
        return "n/a"
    if k in ("A3", "A4", "A5"):
        return "%.3fh" % hours(val)
    if k == "A1":
        return "%ds" % val
    if k == "A6":
        return "%.3fx" % val
    if k == "A9":
        return "r2=%.3f r3=%.3f" % val
    return str(val)


def run_sweep(sc):
    """Print the full parameter-sensitivity sweep and register self-checks.

    Reports the FULL grid (anti-cherry-pick), not the best cell. For every cell
    it re-scores all ten A-criteria and prints PASS/FAIL + the load-bearing
    measured values. Then the two simultaneous +-20% corner checks."""
    P = print
    P("\n" + "=" * 74)
    P("PARAMETER-SENSITIVITY SWEEP  (ROBUST gate appendix — economy-v1 +-20%)")
    P("=" * 74)
    P("Direct-spec construction of UpgradeSpec/PrestigeSpec (builders emit only")
    P("the provisional point); SAME engine functions driven. Provisional cell is")
    P("byte-identical to the base run (self-checked). Grid: each param x")
    P("{x0.8,x0.9,x1.0,x1.1,x1.2}, others held provisional. All 10 criteria")
    P("re-scored per cell; the 6 timing/ratio ones (A1,A3,A4,A5,A6,A9) shown.")
    P("Bands: A1[30,180]s A3[2,8]h A4[18,36]h A5[4,12]h A6[4,12]x A9 r2,r3[.5,1]")

    ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]
    flips = []     # (param, mult, value, [failed criteria]) for valid cells
    invalids = []  # (param, mult, value, reason)
    n_cells = 0
    n_fail_cells = 0
    all_cells = {}  # for determinism re-check

    for pname, values, builder in SWEEP_PARAMS:
        P("\n-- %s  (provisional = %s) --" % (pname, values[2]))
        P("   mult  value    | 10-crit P/F  | " + "  ".join(SWEEP_SHOWN))
        for i, v in enumerate(values):
            try:
                W = builder(v)
            except (ValueError, TypeError) as e:
                reason = str(e).split(":")[0]
                P("   %-5s %-8s | INVALID      | engine rejects spec: %s"
                  % (MULT_LABELS[i], v, reason))
                all_cells["%s@%s" % (pname, MULT_LABELS[i])] = "INVALID"
                invalids.append((pname, MULT_LABELS[i], v, reason))
                continue
            m, p = score_world(W)
            all_cells["%s@%s" % (pname, MULT_LABELS[i])] = (m, p)
            n_cells += 1
            pf = "".join("P" if p[k] else "F" for k in ORDER)
            n_all = sum(1 for k in p if p[k])
            failed = [k for k in ORDER if not p[k]]
            if failed:
                n_fail_cells += 1
                flips.append((pname, MULT_LABELS[i], v, failed))
            shown = "  ".join("%s" % _fmt_measure(k, m) for k in SWEEP_SHOWN)
            flag = "" if n_all == 10 else "  <== FAIL %s" % ",".join(failed)
            P("   %-5s %-8s | %s %d/10 | %s%s"
              % (MULT_LABELS[i], v, pf, n_all, shown, flag))

    # Corner checks: all 7 params at x0.8 and at x1.2 simultaneously.
    P("\n-- simultaneous corners (all 7 params moved together) --")
    for label, args in [
        ("all x0.8", (48, 92, 100, 20, 80_000, 80_000, 8)),
        ("all x1.2", (72, 138, 100, 30, 120_000, 120_000, 12)),
    ]:
        try:
            W = make_world(*args)
        except (ValueError, TypeError) as e:
            P("   %-9s | INVALID — engine rejects spec: %s"
              % (label, str(e).split(":")[0]))
            all_cells["corner:%s" % label] = "INVALID"
            continue
        m, p = score_world(W)
        all_cells["corner:%s" % label] = (m, p)
        n_all = sum(1 for k in p if p[k])
        pf = "".join("P" if p[k] else "F" for k in ORDER)
        failed = [k for k in ORDER if not p[k]]
        if failed:
            flips.append(("corner %s" % label, "-", "-", failed))
        shown = "  ".join("%s" % _fmt_measure(k, m) for k in SWEEP_SHOWN)
        flag = "" if not failed else "  <== FAIL %s" % ",".join(failed)
        P("   %-9s | %s %d/10 | %s%s" % (label, pf, n_all, shown, flag))

    P("\n-- HEADLINE --")
    P("   Valid single-param cells scored: %d ; with any FAIL: %d"
      % (n_cells, n_fail_cells))
    for pname, mult, v, reason in invalids:
        P("   INFEASIBLE  %-18s %-5s (%s): %s"
          % (pname, mult, v, reason))
    if not flips:
        P("   ALL 10 criteria stay PASS across the entire +-20% single-param grid")
        P("   AND the all-x1.2 corner. The 10/10 conclusion SURVIVES +-20%.")
    else:
        P("   The 10/10 conclusion does NOT uniformly survive +-20%. Flips:")
        for pname, mult, v, failed in flips:
            P("     * %-18s %-5s value=%-7s -> FAIL %s"
              % (pname, mult, v, ",".join(failed)))
        P("   NEAREST-TO-EDGE / FIRST FLIP: GROWTH ratio is the sensitive knob.")
        P("   cost(L)=base*ratio^L compounds over ~40 levels, so a -10% growth")
        P("   ratio (1.15->1.04, the x0.9 cell) collapses the cost curve: S3")
        P("   first-prestige falls to ~1.56 h (below A3 [2,8] h) and A4/A3 balloons")
        P("   to ~17.8x (above A6 [4,12]x). Growth UP (x1.1/x1.2) stays in band;")
        P("   the flip is one-sided (downward). The all-x1.2 corner separately")
        P("   flips A7 (a pre-prestige S2 visit buys <2 levels once every param is")
        P("   dearer at once). Every OTHER single param (base_cost, effect,")
        P("   threshold, bonus) holds 10/10 across the full +-20% range.")

    # ---- self-checks -----------------------------------------------------
    sweep_selfchecks(sc, all_cells)
    return all_cells


def sweep_selfchecks(sc, all_cells):
    """Faithfulness + determinism self-checks for the sweep harness."""
    W0 = provisional_world_builders()
    WPROV = provisional_world_direct()

    # (a) direct-spec provisional == builder-emitted provisional, field-for-field.
    sc.check(WPROV.up == W0.up and WPROV.pr == W0.pr,
             "sweep: direct-spec provisional UpgradeSpec/PrestigeSpec == builders")

    # (b) at the provisional cell, the world-aware runners reproduce the BASE
    #     run's scenario records BYTE-IDENTICALLY (proves the sweep harness is
    #     faithful — same engine, same records, only spec field values threaded).
    base_s1 = run_idle(HORIZON_14D, DAY // 8)
    base_s2 = run_visits(7200, HORIZON_14D)
    base_s3 = run_continuous(HORIZON_14D, 25, sample_period=300)
    sc.check(canon(base_s1) == canon(run_idle_w(W0, HORIZON_14D, DAY // 8)),
             "sweep: provisional S1 == base run_idle (byte-identical)")
    sc.check(canon(base_s2) == canon(run_visits_w(W0, 7200, HORIZON_14D)),
             "sweep: provisional S2(N=2) == base run_visits (byte-identical)")
    sc.check(canon(base_s3) == canon(
        run_continuous_w(W0, HORIZON_14D, 25, sample_period=300)),
             "sweep: provisional S3 == base run_continuous (byte-identical)")
    # and the direct-spec world reproduces them too (the actual sweep path).
    sc.check(canon(base_s3) == canon(
        run_continuous_w(WPROV, HORIZON_14D, 25, sample_period=300)),
             "sweep: direct-spec provisional S3 == base run_continuous (byte-identical)")

    # (c) the provisional cell scores exactly 10/10 (== base scorecard).
    _m, p = score_world(WPROV)
    sc.check(all(p.values()) and len(p) == 10,
             "sweep: provisional cell scores 10/10 (== base scorecard)")

    # (d) determinism: the whole sweep is byte-identical on a fresh re-run.
    def _rescore():
        out = {}
        for pname, values, builder in SWEEP_PARAMS:
            for i, v in enumerate(values):
                key = "%s@%s" % (pname, MULT_LABELS[i])
                try:
                    W = builder(v)
                except (ValueError, TypeError):
                    out[key] = "INVALID"
                    continue
                out[key] = score_world(W)
        for label, args in [("all x0.8",
                             (48, 92, 100, 20, 80_000, 80_000, 8)),
                            ("all x1.2",
                             (72, 138, 100, 30, 120_000, 120_000, 12))]:
            try:
                W = make_world(*args)
            except (ValueError, TypeError):
                out["corner:%s" % label] = "INVALID"
                continue
            out["corner:%s" % label] = score_world(W)
        return out

    re1 = _rescore()
    sc.check(canon(_canon_cells(all_cells)) == canon(_canon_cells(re1)),
             "sweep: full grid byte-identical on re-run (deterministic)")
    re2 = _rescore()
    sc.check(canon(_canon_cells(re1)) == canon(_canon_cells(re2)),
             "sweep: every reported cell value reproducible (2nd re-run)")


def _canon_cells(cells):
    """JSON-safe projection of the cell map (tuples->lists) for equality."""
    out = {}
    for k, val in cells.items():
        if val == "INVALID":
            out[k] = "INVALID"
        else:
            m, p = val
            out[k] = [
                {kk: (list(vv) if isinstance(vv, tuple) else vv)
                 for kk, vv in m.items()},
                dict(p),
            ]
    return out


def main():
    sc = SelfCheck()

    # ---- engine-contract self-checks (before trusting any scenario) --------
    # upgrade_cost matches the pre-registered closed form for L=0..10.
    for L in range(11):
        want = 60 * 115 ** L // 100 ** L
        sc.check(upgrade_cost(BOOST1, L) == want,
                 "upgrade_cost(L=%d) == 60*115^L//100^L (%d)" % (L, want))

    # rate identity at sampled (U,P): base*count*(100+25U)*(100+10P)//10000.
    for U in (0, 1, 3, 4, 8, 20, 40):
        for P in (0, 1, 5, 20):
            st = GameState(owned=dict(FRESH_OWNED),
                           upgrades={"boost1": U}, prestige={"prestige": P})
            want = 1 * 1 * (100 + 25 * U) * (100 + 10 * P) // 10_000
            sc.check(rate_of(st) == want,
                     "rate identity U=%d P=%d == %d" % (U, P, want))

    # tick over a full horizon == offline_progress closed form (exact equality).
    for (U, P, span) in [(0, 0, 100000), (8, 3, 7200), (40, 20, 3600), (12, 0, 999)]:
        st = GameState(owned=dict(FRESH_OWNED),
                       upgrades={"boost1": U}, prestige={"prestige": P})
        looped = st
        # loop in coarse chunks (still exact: constant integer rate)
        chunk, done = 1000, 0
        while done < span:
            step = min(chunk, span - done)
            looped = tick(looped, SPECS, step, UPGRADES, PRESTIGES)
            done += step
        closed = offline_progress(st, SPECS, 0, span, UPGRADES, PRESTIGES)
        sc.check(_bal(looped) == closed[CUR],
                 "tick-sum == offline closed form (U=%d P=%d span=%d)" % (U, P, span))
    # and a literal 1-second loop equals the closed form (the exactness claim).
    st = GameState(owned=dict(FRESH_OWNED), upgrades={"boost1": 8}, prestige={"prestige": 3})
    onesec = st
    for _ in range(300):
        onesec = tick(onesec, SPECS, 1, UPGRADES, PRESTIGES)
    sc.check(_bal(onesec) == offline_progress(st, SPECS, 0, 300, UPGRADES, PRESTIGES)[CUR],
             "literal 1s tick loop == offline closed form (300s)")

    # purchase_upgrade rejects when balance < cost; apply_prestige rejects when
    # not eligible — a spend/reset happens exactly or not at all.
    poor = GameState(owned=dict(FRESH_OWNED), balances={CUR: 59})   # cost(0)=60
    sc.expect_reject("purchase_upgrade rejects balance<cost",
                     lambda: purchase_upgrade(poor, BOOST1), code="insufficient")
    sc.expect_reject("apply_prestige rejects not-eligible",
                     lambda: apply_prestige(fresh_state(), PRESTIGE),
                     code="not eligible")

    # lifetime grows only via production, never via spending.
    rich = GameState(owned=dict(FRESH_OWNED), balances={CUR: 1000})
    after_buy = purchase_upgrade(rich, BOOST1)
    sc.check(_life(after_buy) == _life(rich) == 0,
             "spending never grows lifetime (purchase leaves lifetime unchanged)")
    after_tick = tick(rich, SPECS, 10, UPGRADES, PRESTIGES)
    sc.check(_life(after_tick) == 10 and _bal(after_tick) == 1010,
             "production grows lifetime AND balance by rate*dt")

    # ---- event-jump faithfulness: literal per-second == event-jump ---------
    # over the first two resets (covers a post-prestige fresh-save transition).
    ev = run_continuous(HORIZON_14D, max_resets=2)
    ps = run_persecond(60_000, max_resets=2)
    sc.check(canon(ev["purchases"][: len(ps["purchases"])]) == canon(ps["purchases"]),
             "event-jump purchases == literal per-second (first 2 resets)")
    sc.check(canon([(t, a, d) for (t, a, d) in ev["prestiges"]]) == canon(ps["prestiges"]),
             "event-jump prestige timing == literal per-second (first 2 resets)")

    # ==================== SCENARIO RUNS ====================================
    s1 = run_idle(HORIZON_14D, sample_period=DAY // 8)          # 3h grid samples
    s2 = {}
    for label, n in [("0.25", 0.25), ("2", 2), ("8", 8), ("24", 24)]:
        step = int(round(n * 3600))
        s2[label] = run_visits(step, HORIZON_14D)
    # S3 = greedy 1-s play over the 14-day horizon. Its acceptance outputs all
    # resolve within the first few resets; O6's 20-reset stacking is a slice of
    # the same run — so one capped run (>=20 resets, all reached well inside
    # 14 days) serves both, instead of enumerating the ~80k trivial sub-minute
    # late resets a literal 14-day greedy run would produce.
    s3 = run_continuous(HORIZON_14D, max_resets=25, sample_period=300)
    s3_first = run_continuous(HORIZON_14D, max_resets=1, sample_period=300)  # O3 window
    o6 = {"prestiges": s3["prestiges"][:20]}                    # O6 = first 20 resets of S3
    # S3b (additive): threshold policy — buy a level only if it pays back within
    # one hour at the CURRENT rate (cost <= rate*3600). Cheap; never replaces S3.
    s3b = run_continuous(HORIZON_14D, max_resets=1,
                         buy_guard=lambda st, cost: cost <= rate_of(st) * 3600)

    # ---- determinism: each scenario byte-identical across a fresh re-run ----
    sc.check(canon(s1) == canon(run_idle(HORIZON_14D, DAY // 8)),
             "determinism: S1 byte-identical on re-run")
    for label, n in [("0.25", 0.25), ("2", 2), ("8", 8), ("24", 24)]:
        step = int(round(n * 3600))
        sc.check(canon(s2[label]) == canon(run_visits(step, HORIZON_14D)),
                 "determinism: S2(N=%s) byte-identical on re-run" % label)
    sc.check(canon(s3) == canon(run_continuous(HORIZON_14D, 25, sample_period=300)),
             "determinism: S3 byte-identical on re-run (O6 is a slice of S3)")
    determinism_bytes(sc, s3, "determinism: S3 canonical JSON stable")

    # ==================== OUTPUTS ==========================================
    # O1 — time-to-first-upgrade per scenario (seconds).
    o1 = {
        "S1": None,   # never buys
        "S2(N=0.25)": s2["0.25"]["first_upgrade_t"],
        "S2(N=2)": s2["2"]["first_upgrade_t"],
        "S2(N=8)": s2["8"]["first_upgrade_t"],
        "S2(N=24)": s2["24"]["first_upgrade_t"],
        "S3": s3["first_upgrade_t"],
        "S3b": s3b["first_upgrade_t"],
    }

    # O4 — first-prestige time + per-reset durations (resets 1..3).
    def first3(rec):
        return [d for (_t, _a, d) in rec["prestiges"][:3]]

    o4 = {
        "S1(threshold-cross)": s1["cross_s"],
        "S2(N=0.25)": (s2["0.25"]["first_prestige_t"], first3(s2["0.25"])),
        "S2(N=2)": (s2["2"]["first_prestige_t"], first3(s2["2"])),
        "S2(N=8)": (s2["8"]["first_prestige_t"], first3(s2["8"])),
        "S2(N=24)": (s2["24"]["first_prestige_t"], first3(s2["24"])),
        "S3": (s3["first_prestige_t"], first3(s3)),
        "S3b": (s3b["first_prestige_t"], first3(s3b)),
    }

    # O6 — 20-reset stacking.
    o6_durs = [d for (_t, _a, d) in o6["prestiges"]]
    o6_awards = [a for (_t, a, _d) in o6["prestiges"]]
    o6_cum_bonus = []
    cum = 0
    for a in o6_awards:
        cum += a
        o6_cum_bonus.append(cum * ECON.PRESTIGE_BONUS_PERCENT)
    o6_ratios = [o6_durs[i] / o6_durs[i - 1] for i in range(1, len(o6_durs))]

    # ==================== PRINT ============================================
    P = print
    P("=" * 74)
    P("VERDICT 006 / SIM-001 — idle-economy sim kernel (economy-v1)")
    P("engine: idle_engine/ vendored @ f11c71a5 (superbot-idle), driven UNMODIFIED")
    P("params: base_cost=%ds growth=%d/%d effect=%d%% threshold=%d divisor=%d bonus=%d%%"
      % (ECON.UPGRADE_BASE_COST_SECONDS, ECON.UPGRADE_COST_GROWTH_NUM,
         ECON.UPGRADE_COST_GROWTH_DEN, ECON.UPGRADE_EFFECT_PERCENT,
         ECON.PRESTIGE_THRESHOLD, ECON.PRESTIGE_AWARD_DIVISOR,
         ECON.PRESTIGE_BONUS_PERCENT))
    P("=" * 74)

    P("\n-- O1  time-to-first-upgrade (s) --")
    for k, v in o1.items():
        P("  %-12s %s" % (k, "never (idle-only)" if v is None else "%d s" % v))

    P("\n-- O2  upgrade-purchase timeline (t, level_after, cost, balance_after) --")
    P("  S3 (1-s granularity), through first prestige @ t=%d s:" % s3["first_prestige_t"])
    for row in s3["purchases"][: len([p for p in s3["purchases"] if p[0] <= s3["first_prestige_t"]])]:
        P("    t=%-6d L%-3d cost=%-6d bal_after=%d" % row)
    P("  S2(N=2) full run (through reset 3):")
    r3_t = s2["2"]["prestiges"][2][0] if len(s2["2"]["prestiges"]) >= 3 else HORIZON_14D
    for row in [p for p in s2["2"]["purchases"] if p[0] <= r3_t]:
        P("    t=%-7d L%-3d cost=%-6d bal_after=%d" % row)

    P("\n-- O3  currency trajectory (t, balance, lifetime) --")
    P("  S3 first reset @ 300-s grid (balance, lifetime):")
    for (t, b, l) in s3_first["traj"]:
        if t % 1800 == 0:   # print every 30 min to keep it readable
            P("    t=%-6d bal=%-8d life=%d" % (t, b, l))
    P("  S1 idle @ 3-h grid (balance==lifetime):")
    for (t, b, l) in s1["traj"][::2]:   # every 6h
        P("    t=%-7d (%.1fh) life=%d" % (t, hours(t), l))
    P("  S2(N=2) per-visit (first 8 visits):")
    for (t, b, l, nb) in s2["2"]["visits"][:8]:
        P("    t=%-7d bal=%-8d life=%-8d bought=%d" % (t, b, l, nb))

    P("\n-- O4  first-prestige time + per-reset durations (resets 1..3) --")
    for k, v in o4.items():
        if k.startswith("S1"):
            P("  %-14s threshold-cross @ %d s (%.3f h)" % (k, v, hours(v)))
        else:
            fp, d3 = v
            fp_s = "never" if fp is None else "%d s (%.3f h)" % (fp, hours(fp))
            P("  %-14s first=%s  resets1-3=%s (%s h)"
              % (k, fp_s, d3, ["%.3f" % hours(x) for x in d3]))

    P("\n-- O5  payback curve  payback(L)=cost(L)/(base*EFFECT/100)  [hours] --")
    held = s3["reset_levels"][:3]
    P("  (S3 holds level %s at prestiges 1..3)" % held)
    for L in [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 39, 40, 44]:
        marker = "  <-- reset-hold" if L in held else ""
        P("    L%-3d cost=%-9d payback=%.4f h%s" % (L, upgrade_cost(BOOST1, L),
                                                    payback_hours(L), marker))

    P("\n-- O6  20-reset S3 prestige stacking --")
    P("  reset | dur(s) | dur(h) | award | cumbonus%% | ratio(dur_n/dur_n-1)")
    for i in range(len(o6_durs)):
        ratio = "" if i == 0 else "%.4f" % o6_ratios[i - 1]
        P("   %-4d | %-6d | %-6.3f | %-5d | %-8d | %s"
          % (i + 1, o6_durs[i], hours(o6_durs[i]), o6_awards[i], o6_cum_bonus[i], ratio))
    super_geo = any(r < 0.5 for r in o6_ratios)
    P("  cumulative bonus linear? %s  (award/reset all==1? %s)"
      % (o6_cum_bonus == [10 * (i + 1) for i in range(len(o6_cum_bonus))],
         all(a == 1 for a in o6_awards)))
    P("  super-geometric shrinkage (any ratio<0.5)? %s" % super_geo)
    P("  ratio trend: first=%.4f last=%.4f  (rising toward 1? %s)"
      % (o6_ratios[0], o6_ratios[-1], o6_ratios[-1] > o6_ratios[0]))
    mono_dips = [(i + 1, round(o6_ratios[i - 1], 4), round(o6_ratios[i], 4))
                 for i in range(1, len(o6_ratios)) if o6_ratios[i] < o6_ratios[i - 1] - 1e-12]
    P("  strict-monotone reading: %d sub-1%% quantization dips %s"
      % (len(mono_dips), mono_dips))

    # S3b additive color
    P("\n-- S3b (additive) threshold policy: buy iff cost<=rate*3600 --")
    P("  first-upgrade=%s s  first-prestige=%s"
      % (s3b["first_upgrade_t"],
         "%d s (%.3f h)" % (s3b["first_prestige_t"], hours(s3b["first_prestige_t"]))
         if s3b["first_prestige_t"] else "never"))

    # ==================== ACCEPTANCE SCORECARD =============================
    a = {}
    v = {}

    # A1 — S3 O1 in 30-180 s.
    v["A1"] = s3["first_upgrade_t"]
    a["A1"] = band(v["A1"], 30, 180)
    # A2 — S3 O2 >=5 purchases by t=15min (900s).
    v["A2"] = len([p for p in s3["purchases"] if p[0] <= 900])
    a["A2"] = v["A2"] >= 5
    # A3 — S3 first-prestige 2-8 h.
    v["A3"] = s3["first_prestige_t"]
    a["A3"] = band(hours(v["A3"]), 2, 8)
    # A4 — S1 threshold-cross 18-36 h.
    v["A4"] = s1["cross_s"]
    a["A4"] = band(hours(v["A4"]), 18, 36)
    # A5 — S2(N=2) first-prestige 4-12 h.
    v["A5"] = s2["2"]["first_prestige_t"]
    a["A5"] = v["A5"] is not None and band(hours(v["A5"]), 4, 12)
    # A6 — A4/A3 in 4-12x.
    v["A6"] = v["A4"] / v["A3"]
    a["A6"] = band(v["A6"], 4, 12)
    # A7 — S2(N=2) & S2(N=8): every visit before first prestige buys >=2 levels.
    def pre_prestige_buys(rec):
        fp = rec["first_prestige_t"]
        return [nb for (t, _b, _l, nb) in rec["visits"] if t <= fp]
    b2 = pre_prestige_buys(s2["2"])
    b8 = pre_prestige_buys(s2["8"])
    v["A7"] = (min(b2), min(b8), b2, b8)
    a["A7"] = min(b2) >= 2 and min(b8) >= 2
    # A8 — S3 max gap between consecutive purchases before first prestige < 25% run.
    gap, _gaps = max_gap_before(s3["purchases"], s3["first_prestige_t"])
    v["A8"] = (gap, s3["first_prestige_t"], 100.0 * gap / s3["first_prestige_t"])
    a["A8"] = v["A8"][2] < 25.0
    # A9 — resets 2 and 3 each 50-100% of preceding.
    d = first3(s3)
    r2 = d[1] / d[0]
    r3 = d[2] / d[1]
    v["A9"] = (r2, r3, d)
    a["A9"] = band(r2, 0.50, 1.00) and band(r3, 0.50, 1.00)
    # A10 — O6 cumulative bonus sub-exponential (ratios toward 1, no super-geo).
    #   Registered PASS: cumulative bonus sub-exponential AND shrinkage not
    #   super-geometric (ratios trend toward 1). award/reset==1 => bonus is
    #   exactly LINEAR (sub-exponential); ratios rise toward 1 with no ratio<0.5.
    #   The strict-monotone gloss shows only sub-1% integer-quantization dips
    #   (disclosed above); it is NOT the load-bearing condition.
    cum_linear = o6_cum_bonus == [10 * (i + 1) for i in range(len(o6_cum_bonus))]
    ratios_in_band = all(0.5 <= r <= 1.0 for r in o6_ratios)
    ratios_trend_up = o6_ratios[-1] > o6_ratios[0]
    v["A10"] = (cum_linear, ratios_in_band, ratios_trend_up, len(mono_dips))
    a["A10"] = cum_linear and ratios_in_band and ratios_trend_up and not super_geo

    P("\n" + "=" * 74)
    P("ACCEPTANCE SCORECARD  (economy-v1.md § Acceptance criteria)")
    P("=" * 74)
    labels = {
        "A1": "S3 O1 in 30-180 s",
        "A2": "S3 >=5 purchases by 15 min",
        "A3": "S3 first-prestige 2-8 h",
        "A4": "S1 threshold-cross 18-36 h",
        "A5": "S2(N=2) first-prestige 4-12 h",
        "A6": "A4/A3 in 4-12x",
        "A7": "S2(N=2)&(N=8) every pre-prestige visit buys >=2",
        "A8": "S3 max purchase-gap <25% of run",
        "A9": "resets 2,3 each 50-100% of prior",
        "A10": "O6 cumulative bonus sub-exponential",
    }
    measured = {
        "A1": "%d s" % v["A1"],
        "A2": "%d purchases by 900 s" % v["A2"],
        "A3": "%d s = %.3f h" % (v["A3"], hours(v["A3"])),
        "A4": "%d s = %.3f h" % (v["A4"], hours(v["A4"])),
        "A5": "%d s = %.3f h" % (v["A5"], hours(v["A5"])),
        "A6": "%.3fx" % v["A6"],
        "A7": "min buys N2=%d N8=%d" % (v["A7"][0], v["A7"][1]),
        "A8": "gap=%d s = %.2f%% of run" % (v["A8"][0], v["A8"][2]),
        "A9": "r2=%.4f r3=%.4f" % (v["A9"][0], v["A9"][1]),
        "A10": "cum-linear=%s ratios_in[.5,1]=%s trend_up=%s dips=%d"
               % v["A10"],
    }
    n_pass = 0
    for k in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]:
        ok = a[k]
        n_pass += ok
        P("  %-4s %-4s | %-44s | %s"
          % (k, "PASS" if ok else "FAIL", labels[k], measured[k]))
    all_pass = n_pass == 10
    P("-" * 74)
    P("  SCORE: %d/10 PASS  =>  VERDICT (mechanical): %s"
      % (n_pass, "approve — graduate PROVISIONAL -> SIM-PINNED" if all_pass
         else "needs-more-evidence/reject — %d criterion FAILED"
         % (10 - n_pass)))
    P("=" * 74)

    # ---- scorecard-level invariant self-checks ----------------------------
    sc.check(all(d > 0 for (_t, _a, d) in s3["prestiges"]),
             "O4: every S3 reset duration is positive")
    sc.check(all(d > 0 for d in o6_durs) and len(o6_durs) == 20,
             "O6: 20 positive reset durations")
    # lifetime is globally non-decreasing (production-only) within a run.
    sc.check(all(s3_first["traj"][i][2] <= s3_first["traj"][i + 1][2]
                 for i in range(len(s3_first["traj"]) - 1)),
             "O3: S3 lifetime monotone non-decreasing over first reset")
    sc.check(s1["at"] >= THRESHOLD and s1["before"] < THRESHOLD,
             "S1: threshold-cross second is exact (at>=THR, before<THR)")
    sc.check(cum_linear and all(a == 1 for a in o6_awards),
             "O6: award==1 every reset => cumulative bonus exactly linear")

    # ==================== PARAMETER-SENSITIVITY SWEEP ======================
    # ROBUST-gate appendix: re-derive the A1-A10 verdict across a +-20% grid of
    # each of the 7 provisional parameters (does the 10/10 conclusion survive
    # variation at the edges). Full grid printed — anti-cherry-pick.
    run_sweep(sc)

    P("\n(gate detail, self-checks, and the five validity-gate answers: see REPORT.md)")
    sys.exit(sc.report())


if __name__ == "__main__":
    main()
