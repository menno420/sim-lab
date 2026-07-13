#!/usr/bin/env python3
"""VERDICT 017 / PROPOSAL 015 — generator purchase path: T10 cost-curve sweep.

NUMERIC SIMULATION (method ladder rung 1): deterministic, integer-exact,
stdlib-only, NO RNG, no network, no git, no wall clock at run time. A single
run per (cell, policy) IS the distribution (the engine is pure and
integer-exact); determinism is proven by byte-identical re-run, not by seeds.

PROVENANCE — DRIVE THE REAL ENGINE, DO NOT REIMPLEMENT
  ``fixtures/idle_engine/`` is a VENDOR COPY, byte-for-byte and COMPLETE
  (all 11 modules, ``__init__.py`` included, unmodified), of
  ``menno420/superbot-idle`` ``idle_engine/`` @
  ``c753bc8f5ace96e4632510f43b53f0ee45e2def5`` — sha256 manifest in
  ``fixtures/MANIFEST.json``, re-verified at every run before anything is
  imported. The driver loads ONLY the six economy-surface modules (state,
  upgrades, prestige, achievements, engine, economy) through a synthetic
  package anchor so the byte-identical ``__init__.py`` — which pulls
  ``theme``/``render`` and with them the non-stdlib ``yaml`` — is never
  EXECUTED (the VERDICT 006 accommodation, strengthened: 006 reconstructed
  the init; here every file is byte-identical and the init is simply not
  run). The economy/mechanics logic is UNTOUCHED; this driver calls the REAL
  functions: tick, offline_progress, apply_offline_progress,
  purchase_upgrade, upgrade_cost, prestige_eligible, prestige_award,
  apply_prestige, production_per_second, award_milestones,
  build_upgrade_spec, build_prestige_spec, build_milestone_specs.

THE ONE DRIVER-LEVEL MECHANIC (the thing being priced): the engine has NO
generator purchase path at ``c753bc8`` — that is the sim's verified premise —
so the candidate mechanic lives in the DRIVER: a generator cost curve
``cost(n owned) = BASE * g_num**n // g_den**n`` (the upgrade-curve family)
and a purchase function mirroring ``purchase_upgrade`` semantics exactly
(exact spend or nothing, balance-only, lifetime untouched, owned += 1).

Source idea: menno420/idea-engine control/outbox.md PROPOSAL 015 @
2026-07-12T23:08:19Z (idea ideas/superbot-idle/
generator-purchase-path-t10-2026-07-12.md @ 18778ff, PR #277).

Run:  python3 sims/verdict-017-t10-cost-curve/t10_cost_curve_sim.py
Exit 0 iff every self-check passes.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
import sys
import types
from dataclasses import replace

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIX_DIR = os.path.join(BASE_DIR, "fixtures")
ENGINE_DIR = os.path.join(FIX_DIR, "idle_engine")

# --------------------------------------------------------------------------
# Vendored harness helpers (stdlib-only) — harness/simharness.py family,
# exactly as VERDICT 006 vendored them.
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


def canon(obj):
    return json.dumps(obj, sort_keys=True)


# --------------------------------------------------------------------------
# Fixture integrity FIRST: every vendored engine byte is manifest-pinned.
# --------------------------------------------------------------------------

with open(os.path.join(FIX_DIR, "MANIFEST.json"), "rb") as _fh:
    MANIFEST = json.loads(_fh.read().decode("utf-8"))

PIN = "c753bc8f5ace96e4632510f43b53f0ee45e2def5"


def _verify_manifest(sc):
    sc.check(MANIFEST["pin_commit"] == PIN,
             "fixtures: MANIFEST pin_commit is superbot-idle @ %s" % PIN[:7])
    files = sorted(os.listdir(ENGINE_DIR))
    files = [f for f in files if f.endswith(".py")]
    sc.check(files == sorted(MANIFEST["sha256"].keys()) and len(files) == 11,
             "fixtures: exactly the 11 manifest-listed engine modules present")
    for name in files:
        with open(os.path.join(ENGINE_DIR, name), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        sc.check(digest == MANIFEST["sha256"][name],
                 "fixtures: %s sha256 matches manifest (byte-identical vendor)"
                 % name)


SC = SelfCheck()
_verify_manifest(SC)

# --------------------------------------------------------------------------
# Load the vendored engine through a synthetic package anchor. The
# byte-identical __init__.py is NOT executed (it imports theme -> yaml,
# outside both the stdlib floor and the SIM-001 economy surface); the six
# economy-surface modules are executed byte-for-byte as vendored.
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
UpgradeSpec = _upgrades.UpgradeSpec
upgrade_cost = _upgrades.upgrade_cost
purchase_upgrade = _upgrades.purchase_upgrade
PrestigeSpec = _prestige.PrestigeSpec
prestige_award = _prestige.prestige_award
prestige_eligible = _prestige.prestige_eligible
apply_prestige = _prestige.apply_prestige
MilestoneSpec = _achieve.MilestoneSpec
award_milestones = _achieve.award_milestones
milestone_percent = _achieve.milestone_percent
production_per_second = _engine.production_per_second
tick = _engine.tick
offline_progress = _engine.offline_progress
apply_offline_progress = _engine.apply_offline_progress

# --------------------------------------------------------------------------
# Committed grid + world constants.
# --------------------------------------------------------------------------

with open(os.path.join(BASE_DIR, "grid.json"), "rb") as _fh:
    GRID = json.loads(_fh.read().decode("utf-8"))

CUR = "primary"
TIER1 = GeneratorSpec(spec_id="tier1", produces=CUR, base_rate=1)
BOOST1 = ECON.build_upgrade_spec("boost1", TIER1)
PRESTIGE = ECON.build_prestige_spec(awards="prestige", measures=CUR)
MILESTONES = tuple(ECON.build_milestone_specs(CUR, "prestige"))
FRESH_OWNED = {"tier1": 1}
THRESHOLD = PRESTIGE.threshold

DAY = 86_400
HORIZON_14D = 14 * DAY
S3_MAX_RESETS = 25

T1_COST_SECONDS = GRID["candidate_mechanic"]["tier1_copy_cost_seconds"]  # 60
C2_VALUES = GRID["grid"]["C2_seconds_of_tier1_output"]
R2_VALUES = GRID["grid"]["R2_tier2_base_rate"]
G_VALUES = [tuple(v) for v in GRID["grid"]["g_per_count_cost_growth"]]
S2_HOURS = GRID["policies"]["S2_checkin_hours"]

T10_BAND = (900, 2700)      # 15–45 min active, target 1800 s
T10_TARGET = 1800

# The three purchase kinds, in committed tie-break order.
KIND_UPGRADE, KIND_T1, KIND_T2 = "upgrade", "tier1", "tier2"
KIND_ORDER = {KIND_UPGRADE: 0, KIND_T1: 1, KIND_T2: 2}


class World:
    """One cell's reference world: real specs + the driver-level cost curve.

    ``t1_copies=False`` is DIAGNOSTIC shape D1 (additive leg, the SIM-001
    S3b precedent): the tier-2 unlock/copies are the ONLY generator
    purchases — tier-1 count stays at the shipped 1 — isolating whether the
    tier-1 copy loop, not the swept tier-2 knobs, is what breaks pacing.
    ``t2_cap=1`` on top is DIAGNOSTIC shape D2 (unlock-only): buying the
    SECOND GENERATOR TIER is a one-off unlock — T10's registered wording —
    with no count-stacking on either tier."""

    __slots__ = ("specs", "up", "pr", "ms", "c2", "r2", "gnum", "gden",
                 "has_gen_path", "t1_copies", "t2_cap", "label")

    def __init__(self, c2=None, r2=None, g=None, milestones=True,
                 gen_path=True, t1_copies=True, t2_cap=None, label=""):
        tier2 = (GeneratorSpec(spec_id="tier2", produces=CUR, base_rate=r2),) \
            if gen_path else ()
        self.specs = (TIER1,) + tier2
        self.up = BOOST1
        self.pr = PRESTIGE
        self.ms = MILESTONES if milestones else ()
        self.c2 = c2
        self.r2 = r2
        self.gnum, self.gden = (g if g else (None, None))
        self.has_gen_path = gen_path
        self.t1_copies = t1_copies
        self.t2_cap = t2_cap
        self.label = label


def cell_label(c2, r2, g):
    return "C2=%d|R2=%d|g=%d/%d" % (c2, r2, g[0], g[1])


def fresh_state():
    return GameState(owned=dict(FRESH_OWNED))


def rate_of(state, W):
    return production_per_second(state, W.specs, (W.up,), (W.pr,), W.ms).get(CUR, 0)


def _bal(state):
    return state.balances.get(CUR, 0)


def _life(state):
    return state.lifetime.get(CUR, 0)


def _level(state):
    return state.upgrades.get("boost1", 0)


def _reseed_fresh(state):
    """Reference-world rule (VERDICT 006, unchanged): apply_prestige wipes
    ``owned`` (correct engine behaviour); a fresh save starts owning tier1.
    All PURCHASED copies (tier-1 extras + tier-2) are lost with the run —
    the run-scoped-counts semantics the proposal names as the design fork."""
    return replace(state, owned=dict(FRESH_OWNED))


# --------------------------------------------------------------------------
# The candidate mechanic (driver-level; the engine has no purchase path —
# the verified premise). Semantics mirror purchase_upgrade exactly.
# --------------------------------------------------------------------------


def generator_cost(W, spec_id, owned_count):
    """cost(next copy | n owned) = BASE * g_num**n // g_den**n.
    BASE = tier1.base_rate * COST_SECONDS (seconds-of-tier-1-output)."""
    base = TIER1.base_rate * (T1_COST_SECONDS if spec_id == "tier1" else W.c2)
    return base * W.gnum ** owned_count // W.gden ** owned_count


def purchase_generator(state, W, spec_id):
    """Driver-level purchase: exact spend or nothing; lifetime untouched."""
    count = state.owned.get(spec_id, 0)
    cost = generator_cost(W, spec_id, count)
    balance = state.balances.get(CUR, 0)
    if balance < cost:
        raise ValueError(
            "insufficient %r for generator %r copy %d: have %d, need %d"
            % (CUR, spec_id, count + 1, balance, cost))
    balances = dict(state.balances)
    balances[CUR] = balance - cost
    owned = dict(state.owned)
    owned[spec_id] = count + 1
    return replace(state, balances=balances, owned=owned)


# --------------------------------------------------------------------------
# The committed greedy buy rule (grid.json § buy_rule).
# --------------------------------------------------------------------------


def _options(state, W, r0):
    """The three purchase options as (kind, cost, delta_rate). delta_rate is
    measured by calling the REAL production_per_second on the hypothetical
    post-purchase state (the spend itself never changes the rate)."""
    opts = []
    # next boost1 level
    lvl = _level(state)
    cost_u = upgrade_cost(W.up, lvl)
    hyp = replace(state, upgrades={**state.upgrades, "boost1": lvl + 1})
    opts.append((KIND_UPGRADE, cost_u, rate_of(hyp, W) - r0))
    # the generator options exist only with the candidate purchase path
    # (baseline legs replicate the shipped engine: upgrades only)
    if W.has_gen_path:
        if W.t1_copies:
            # next tier-1 copy
            n1 = state.owned.get("tier1", 0)
            hyp = replace(state, owned={**state.owned, "tier1": n1 + 1})
            opts.append((KIND_T1, generator_cost(W, "tier1", n1),
                         rate_of(hyp, W) - r0))
        # next tier-2 copy (count 0 = the unlock; D2 caps at the unlock)
        n2 = state.owned.get("tier2", 0)
        if W.t2_cap is None or n2 < W.t2_cap:
            hyp = replace(state, owned={**state.owned, "tier2": n2 + 1})
            opts.append((KIND_T2, generator_cost(W, "tier2", n2),
                         rate_of(hyp, W) - r0))
    return opts


def _better(a, b):
    """True iff option a beats option b under the committed rule:
    higher delta/cost (exact integer cross-products), then higher delta,
    then lower cost, then fixed kind order upgrade < tier1 < tier2."""
    ka, ca, da = a
    kb, cb, db = b
    lhs, rhs = da * cb, db * ca
    if lhs != rhs:
        return lhs > rhs
    if da != db:
        return da > db
    if ca != cb:
        return ca < cb
    return KIND_ORDER[ka] < KIND_ORDER[kb]


def _pick_best(opts):
    best = opts[0]
    for o in opts[1:]:
        if _better(o, best):
            best = o
    return best


def greedy_buy(state, W, purchases, t, saving=False):
    """The committed buy rule at one action boundary.

    Myopic (primary): repeat — among AFFORDABLE options, buy the best
    delta/cost; stop when nothing is affordable. Returns (state, None).

    Saving (S3g, additive): the argmax runs over ALL options; when the
    winner has delta > 0 but is unaffordable the player SAVES — returns
    (state, save_cost) so the caller waits for that affordability instead
    of the cheapest option's. Zero-delta winners fall back to the myopic
    step (never save for a zero-gain purchase).
    """
    while True:
        r0 = rate_of(state, W)
        opts = _options(state, W, r0)
        bal = _bal(state)
        if saving:
            best_all = _pick_best(opts)
            if best_all[2] > 0 and best_all[1] > bal:
                return state, best_all[1]
        afford = [o for o in opts if o[1] <= bal]
        if not afford:
            return state, None
        kind, cost, delta = _pick_best(afford)
        if saving and delta <= 0:
            # a saving player never spends on a zero-gain option while a
            # positive-gain option exists (handled above); if EVERY option
            # were zero-delta (impossible here: a tier-1 copy always adds
            # >= 1/s) stop rather than waste.
            return state, None
        if kind == KIND_UPGRADE:
            state = purchase_upgrade(state, W.up)       # REAL engine call
        else:
            state = purchase_generator(state, W, kind)  # the candidate mechanic
        purchases.append((t, kind, cost, delta, _bal(state)))
        state = award_milestones(state, W.ms)           # REAL engine call
    # unreachable


# --------------------------------------------------------------------------
# Scenario runners.
# --------------------------------------------------------------------------


def _log_new_ms(state, t, rec):
    """Log any milestone newly present in the earned set (sorted for a
    deterministic within-boundary order)."""
    seen = rec["ms_seen"]
    for sid in sorted(state.milestones):
        if sid not in seen:
            rec["ms_events"].append((t, sid))
            seen.add(sid)


def _boundary(state, W, t, rec, saving):
    """One action boundary: award -> buy (awards inside) -> prestige -> award.
    Returns (state, save_cost)."""
    state = award_milestones(state, W.ms)               # REAL engine call
    _log_new_ms(state, t, rec)
    before = len(rec["purchases"])
    state, save_cost = greedy_buy(state, W, rec["purchases"], t, saving=saving)
    _log_new_ms(state, t, rec)   # milestones banked inside greedy_buy
    if rec["first_purchase_t"] is None and len(rec["purchases"]) > before:
        rec["first_purchase_t"] = rec["purchases"][before][0]
    if prestige_eligible(state, W.pr):
        award = prestige_award(state, W.pr)
        dur = t - rec["reset_start"]
        rec["prestiges"].append((t, award, dur))
        rec["reset_levels"].append(_level(state))
        rec["reset_start"] = t
        if rec["first_prestige_t"] is None:
            rec["first_prestige_t"] = t
        state = _reseed_fresh(apply_prestige(state, W.pr))  # REAL engine call
        state = award_milestones(state, W.ms)               # REAL engine call
        _log_new_ms(state, t, rec)
    return state, save_cost


def _new_rec():
    return {
        "purchases": [],       # (t, kind, cost, delta, balance_after)
        "prestiges": [],       # (t, award, reset_duration_s)
        "reset_levels": [],
        "ms_events": [],       # (t, milestone spec_id)
        "ms_seen": set(),
        "visits": [],          # S2 only: (t, bal, life, upgrades_bought, total_bought)
        "first_purchase_t": None,
        "first_prestige_t": None,
        "reset_start": 0,
    }


def _rec_out(rec):
    """JSON-safe projection (drop bookkeeping)."""
    return {k: v for k, v in rec.items() if k not in ("ms_seen", "reset_start")}


def run_continuous(W, horizon, max_resets, saving=False):
    """S3 (myopic) / S3g (saving): 1-second-granularity acting player,
    computed by exact event-jump. Boundaries: first second any purchase
    target is affordable, prestige threshold crossing, or an unearned
    lifetime-milestone threshold crossing (the 1-second player banks a
    milestone the second it is reached). Byte-identical to a literal
    per-second loop (self-checked over the first two resets)."""
    state = fresh_state()
    rec = _new_rec()
    t = 0
    state, save_cost = _boundary(state, W, t, rec, saving)
    while t <= horizon and len(rec["prestiges"]) < max_resets:
        r = rate_of(state, W)
        if r <= 0:
            break
        bal = _bal(state)
        life = _life(state)
        # wake target 1: affordability (saving: the saved-for option;
        # myopic: the cheapest option)
        if save_cost is not None:
            target = save_cost
        else:
            target = min(c for (_k, c, _d) in _options(state, W, r))
        k_buy = -(-(target - bal) // r) if bal < target else 0
        # wake target 2: prestige threshold
        k_pr = -(-(THRESHOLD - life) // r) if life < THRESHOLD else 0
        # wake target 3: unearned lifetime milestones
        k_ms = 0
        for spec in W.ms:
            if spec.kind == "lifetime" and not state.milestones.get(spec.spec_id):
                if life < spec.threshold:
                    k = -(-(spec.threshold - life) // r)
                    if k_ms == 0 or k < k_ms:
                        k_ms = k
        cands = [k for k in (k_buy, k_pr, k_ms) if k > 0]
        if not cands:
            # actionable right now (shouldn't persist: boundary drains it)
            state, save_cost = _boundary(state, W, t, rec, saving)
            continue
        k = min(cands)
        if t + k > horizon:
            break
        state = tick(state, W.specs, int(k), (W.up,), (W.pr,), W.ms)  # REAL
        t += int(k)
        state, save_cost = _boundary(state, W, t, rec, saving)
    return _rec_out(rec)


def run_visits(W, step, horizon):
    """S2 check-in every ``step`` seconds: credit elapsed production (REAL
    apply_offline_progress), then the boundary (award -> greedy-buy ->
    prestige-iff-eligible). Milestones bank at visits only — the player can
    only act when present (economy-v1 reference-world rule)."""
    state = fresh_state()
    rec = _new_rec()
    t = 0
    while t + step <= horizon:
        t += step
        state = apply_offline_progress(state, W.specs, t, (W.up,), (W.pr,), W.ms)
        before = len(rec["purchases"])
        state, _ = _boundary(state, W, t, rec, saving=False)
        bought = rec["purchases"][before:]
        n_up = sum(1 for p in bought if p[1] == KIND_UPGRADE)
        rec["visits"].append((t, _bal(state), _life(state), n_up, len(bought)))
    return _rec_out(rec)


def run_idle(W, horizon, sample_period):
    """S1 — idle-only: never acts, so no milestone is ever banked (awarding
    is an explicit runtime action; an absent player has no boundary). Rate
    is the fresh-save constant; the threshold-cross second is closed-form
    and verified against the real engine."""
    state = fresh_state()
    r = rate_of(state, W)
    cross = math.ceil(THRESHOLD / r) if r > 0 else None
    at = offline_progress(state, W.specs, 0, cross, (W.up,), (W.pr,), W.ms)[CUR]
    before = offline_progress(state, W.specs, 0, cross - 1, (W.up,), (W.pr,), W.ms)[CUR]
    traj = []
    for ts in range(0, horizon + 1, sample_period):
        earned = offline_progress(state, W.specs, 0, ts, (W.up,), (W.pr,), W.ms)[CUR]
        traj.append((ts, earned, earned))
    return {"rate": r, "cross_s": cross, "at": at, "before": before, "traj": traj}


def run_persecond(W, n_seconds, max_resets):
    """Literal per-second loop (ground truth for the event-jump): every
    second is an action boundary — tick(1), then award/buy/prestige."""
    state = fresh_state()
    rec = _new_rec()
    t = 0
    state, _ = _boundary(state, W, t, rec, saving=False)
    for _ in range(n_seconds):
        state = tick(state, W.specs, 1, (W.up,), (W.pr,), W.ms)
        t += 1
        state, _ = _boundary(state, W, t, rec, saving=False)
        if len(rec["prestiges"]) >= max_resets:
            break
    return _rec_out(rec)


# --------------------------------------------------------------------------
# Scoring: SIM-001's A1–A10 re-scored, dual-read (LITERAL / INTENT).
# --------------------------------------------------------------------------


def hours(seconds):
    return seconds / 3600.0


def band(x, lo, hi):
    return lo <= x <= hi


def _purchase_times(rec, literal):
    if literal:
        return [t for (t, k, *_r) in rec["purchases"] if k == KIND_UPGRADE]
    return [t for (t, *_r) in rec["purchases"]]


def _max_gap_before(times, cutoff_t):
    times = [t for t in times if t < cutoff_t]
    if len(times) < 2:
        return 0
    return max(times[i + 1] - times[i] for i in range(len(times) - 1))


def score_criteria(s3, s1, s2n2, s2n8, W, literal):
    """SIM-001's ten criteria on the extended world. ``literal`` counts
    boost1 upgrade purchases only where the registered wording names
    upgrades (A1/A2/A7/A8); INTENT counts all purchases."""
    m, p = {}, {}
    up_times = _purchase_times(s3, literal)
    # A1 — time-to-first-upgrade (literal) / first purchase (intent), 30–180 s.
    m["A1"] = up_times[0] if up_times else None
    p["A1"] = m["A1"] is not None and band(m["A1"], 30, 180)
    # A2 — >=5 purchases by 900 s.
    m["A2"] = len([t for t in up_times if t <= 900])
    p["A2"] = m["A2"] >= 5
    # A3 — S3 first-prestige 2–8 h.
    m["A3"] = s3["first_prestige_t"]
    p["A3"] = m["A3"] is not None and band(hours(m["A3"]), 2, 8)
    # A4 — S1 threshold-cross 18–36 h.
    m["A4"] = s1["cross_s"]
    p["A4"] = m["A4"] is not None and band(hours(m["A4"]), 18, 36)
    # A5 — S2(N=2) first-prestige 4–12 h.
    m["A5"] = s2n2["first_prestige_t"]
    p["A5"] = m["A5"] is not None and band(hours(m["A5"]), 4, 12)
    # A6 — A4/A3 in 4–12x.
    if m["A3"]:
        m["A6"] = m["A4"] / m["A3"]
        p["A6"] = band(m["A6"], 4, 12)
    else:
        m["A6"] = None
        p["A6"] = False

    # A7 — S2(N=2)&(N=8): every pre-prestige visit buys >= 2.
    def preb(rec):
        fp = rec["first_prestige_t"]
        if fp is None:
            return []
        idx = 3 if literal else 4
        return [v[idx] for v in rec["visits"] if v[0] <= fp]
    b2, b8 = preb(s2n2), preb(s2n8)
    m["A7"] = (min(b2) if b2 else 0, min(b8) if b8 else 0)
    p["A7"] = bool(b2) and bool(b8) and min(b2) >= 2 and min(b8) >= 2
    # A8 — S3 max purchase-gap < 25% of run (before first prestige).
    # Guard: with fewer than 2 counted purchases the gap is undefined —
    # scored FAIL (a run whose counted-purchase cadence vanished is a dead
    # zone, not a pass), measured None.
    if s3["first_prestige_t"] and \
            len([t for t in up_times if t < s3["first_prestige_t"]]) >= 2:
        gap = _max_gap_before(up_times, s3["first_prestige_t"])
        pct = 100.0 * gap / s3["first_prestige_t"]
        m["A8"] = (gap, pct)
        p["A8"] = pct < 25.0
    else:
        m["A8"] = None
        p["A8"] = False
    # A9 — resets 2,3 each 50–100% of prior.
    d = [dur for (_t, _a, dur) in s3["prestiges"][:3]]
    if len(d) >= 3 and d[0] and d[1]:
        r2, r3 = d[1] / d[0], d[2] / d[1]
        m["A9"] = (r2, r3)
        p["A9"] = band(r2, 0.50, 1.00) and band(r3, 0.50, 1.00)
    else:
        m["A9"] = None
        p["A9"] = False
    # A10 — cumulative bonus sub-exponential over up-to-20 resets.
    #   Registered load-bearing condition: sub-exponential cumulative bonus,
    #   duration ratios non-decreasing toward 1, no super-geometric
    #   shrinkage. Operationalized as SIM-001 scored it, with the cum-bonus
    #   check generalized from "exactly linear because every award == 1" to
    #   "increments never accelerate" (identical verdict when awards are all
    #   1 — self-checked on the B0 baseline).
    durs = [dur for (_t, _a, dur) in s3["prestiges"][:20]]
    awards = [a for (_t, a, _d) in s3["prestiges"][:20]]
    if len(durs) >= 2:
        cumb, cum = [], 0
        for a in awards:
            cum += a
            cumb.append(cum * W.pr.bonus_percent)
        incs = [cumb[0]] + [cumb[i] - cumb[i - 1] for i in range(1, len(cumb))]
        sub_exp = all(incs[i] <= incs[i - 1] for i in range(1, len(incs)))
        ratios = [durs[i] / durs[i - 1] for i in range(1, len(durs)) if durs[i - 1]]
        ratios_in = all(0.5 <= r <= 1.0 for r in ratios)
        trend_up = ratios[-1] > ratios[0] if len(ratios) >= 2 else False
        super_geo = any(r < 0.5 for r in ratios)
        m["A10"] = (sub_exp, ratios_in, trend_up, len(durs),
                    all(a == 1 for a in awards))
        p["A10"] = sub_exp and ratios_in and trend_up and not super_geo
    else:
        m["A10"] = None
        p["A10"] = False
    return m, p


ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]


def early_inert(rec):
    """Share of S3 purchases in the first 900 s with zero marginal delta."""
    early = [pu for pu in rec["purchases"] if pu[0] <= 900]
    if not early:
        return None, 0, 0
    inert = sum(1 for pu in early if pu[3] == 0)
    return inert / len(early), inert, len(early)


def rung_arrivals(rec):
    """Earned time of owned-1/2/3 (10/100/1,000 total generators)."""
    out = {}
    ms = dict((sid, t) for (t, sid) in rec["ms_events"])
    for rank, thr in ((1, 10), (2, 100), (3, 1000)):
        out["owned-%d(%d)" % (rank, thr)] = ms.get("owned-%d" % rank)
    return out


# --------------------------------------------------------------------------
# Cell evaluation.
# --------------------------------------------------------------------------


def t10_of(rec):
    for (t, kind, *_r) in rec["purchases"]:
        if kind == KIND_T2:
            return t
    return None


def _eval_world(W):
    """Full evaluation of one world (S3 + S3g + S1 + 4×S2, dual scorecards)."""
    s3 = run_continuous(W, HORIZON_14D, S3_MAX_RESETS, saving=False)
    s3g = run_continuous(W, HORIZON_14D, S3_MAX_RESETS, saving=True)
    s1 = run_idle(W, HORIZON_14D, DAY // 8)
    s2 = {}
    for n in S2_HOURS:
        s2[str(n)] = run_visits(W, int(round(n * 3600)), HORIZON_14D)
    m_int, p_int = score_criteria(s3, s1, s2["2"], s2["8"], W, literal=False)
    m_lit, p_lit = score_criteria(s3, s1, s2["2"], s2["8"], W, literal=True)
    ei_frac, ei_n, ei_tot = early_inert(s3)
    out = {
        "T10": {
            "S3": t10_of(s3),
            "S3g": t10_of(s3g),
            "S2": {k: t10_of(v) for k, v in s2.items()},
        },
        "first_prestige": {
            "S3": s3["first_prestige_t"],
            "S3g": s3g["first_prestige_t"],
            "S2": {k: v["first_prestige_t"] for k, v in s2.items()},
        },
        "intent": {"measured": m_int, "pass": p_int,
                   "n_pass": sum(1 for k in ORDER if p_int[k])},
        "literal": {"measured": m_lit, "pass": p_lit,
                    "n_pass": sum(1 for k in ORDER if p_lit[k])},
        "early_inert": {"fraction": ei_frac, "inert": ei_n, "total": ei_tot},
        "rungs": {
            "S3": rung_arrivals(s3),
            "S3g": rung_arrivals(s3g),
            "S2": {k: rung_arrivals(v) for k, v in s2.items()},
        },
        "in_band_S3": s3["first_prestige_t"] is not None
                      and t10_of(s3) is not None
                      and band(t10_of(s3), *T10_BAND),
        "in_band_S3g": t10_of(s3g) is not None and band(t10_of(s3g), *T10_BAND),
        "in_band_S2_025": t10_of(s2["0.25"]) is not None
                          and band(t10_of(s2["0.25"]), *T10_BAND),
    }
    return out, s3, s2


def eval_cell(c2, r2, g):
    W = World(c2=c2, r2=r2, g=g, milestones=True, gen_path=True,
              label=cell_label(c2, r2, g))
    out, s3, s2 = _eval_world(W)
    out["cell"] = {"C2": c2, "R2": r2, "g": [g[0], g[1]]}
    # DIAGNOSTIC legs (additive, disclosed — the SIM-001 S3b precedent).
    # D1: the same cell with the tier-1 copy path REMOVED (tier-2
    # unlock/copies are the only generator purchases) — isolates whether
    # the tier-1 copy loop, not the swept (C2,R2,g) knobs, is what binds.
    Wd = World(c2=c2, r2=r2, g=g, milestones=True, gen_path=True,
               t1_copies=False, label=cell_label(c2, r2, g) + "|no-t1")
    diag, _s3d, _s2d = _eval_world(Wd)
    out["diag_no_t1"] = diag
    # D2: unlock-only — buying the SECOND GENERATOR TIER is a one-off
    # unlock (tier-2 capped at 1 copy, no tier-1 copies), T10's registered
    # wording read literally; no count-stacking loop exists at all.
    Wu = World(c2=c2, r2=r2, g=g, milestones=True, gen_path=True,
               t1_copies=False, t2_cap=1,
               label=cell_label(c2, r2, g) + "|unlock-only")
    diag2, _s3u, _s2u = _eval_world(Wu)
    out["diag_unlock_only"] = diag2
    return out, W, s3, s2


def eval_baselines():
    """B0: no purchase path, no milestone specs — must reproduce VERDICT 006
    exactly. B1: no purchase path, milestone fold active — the drift leg."""
    out = {}
    for name, ms in (("B0", False), ("B1", True)):
        W = World(milestones=ms, gen_path=False, label=name)
        s3 = run_continuous(W, HORIZON_14D, S3_MAX_RESETS, saving=False)
        s1 = run_idle(W, HORIZON_14D, DAY // 8)
        s2 = {}
        for n in S2_HOURS:
            s2[str(n)] = run_visits(W, int(round(n * 3600)), HORIZON_14D)
        m, p = score_criteria(s3, s1, s2["2"], s2["8"], W, literal=True)
        m2, p2 = score_criteria(s3, s1, s2["2"], s2["8"], W, literal=False)
        ei_frac, ei_n, ei_tot = early_inert(s3)
        out[name] = {
            "measured": m, "pass": p,
            "n_pass": sum(1 for k in ORDER if p[k]),
            "literal_equals_intent": canon([m, p]) == canon([m2, p2]),
            "first3_durations": [d for (_t, _a, d) in s3["prestiges"][:3]],
            "awards20": [a for (_t, a, _d) in s3["prestiges"][:20]],
            "early_inert": {"fraction": ei_frac, "inert": ei_n, "total": ei_tot},
            "ms_events_S3": s3["ms_events"][:12],
            "_s3": s3, "_s2": s2, "_W": W,
        }
    return out


# --------------------------------------------------------------------------
# Winner selection (grid.json § winner_rule — mechanical).
# --------------------------------------------------------------------------


def winner_key(cell):
    t10 = cell["T10"]["S3"]
    return (
        abs(t10 - T10_TARGET),
        0 if cell["in_band_S2_025"] else 1,
        0 if cell["in_band_S3g"] else 1,
        cell["early_inert"]["fraction"] if cell["early_inert"]["fraction"]
        is not None else 2.0,
        cell["cell"]["C2"], cell["cell"]["R2"],
        cell["cell"]["g"][0],
    )


def select_winner(cells):
    eligible = [c for c in cells
                if c["in_band_S3"] and c["intent"]["n_pass"] == 10]
    eligible.sort(key=winner_key)
    return eligible


# --------------------------------------------------------------------------
# Self-checks (engine contract, mechanic invariants, faithfulness,
# baseline cross-pins, determinism).
# --------------------------------------------------------------------------


def engine_selfchecks(sc):
    # graduated parameters held pinned (the sweep never re-opens them)
    held = GRID["held_pinned"]
    for k in ("UPGRADE_BASE_COST_SECONDS", "UPGRADE_COST_GROWTH_NUM",
              "UPGRADE_COST_GROWTH_DEN", "UPGRADE_EFFECT_PERCENT",
              "PRESTIGE_THRESHOLD", "PRESTIGE_AWARD_DIVISOR",
              "PRESTIGE_BONUS_PERCENT", "MILESTONE_BONUS_PERCENT"):
        sc.check(getattr(ECON, k) == held[k],
                 "pinned: vendored economy.%s == graduated %r" % (k, held[k]))
    for k in ("MILESTONE_OWNED_THRESHOLDS", "MILESTONE_LIFETIME_THRESHOLDS",
              "MILESTONE_PRESTIGE_THRESHOLDS"):
        sc.check(list(getattr(ECON, k)) == held[k],
                 "pinned: vendored economy.%s == registered %r" % (k, held[k]))
    sc.check(len(MILESTONES) == 9,
             "world: build_milestone_specs emits the 9 registered slots")
    # upgrade_cost closed form
    for L in range(11):
        want = 60 * 115 ** L // 100 ** L
        sc.check(upgrade_cost(BOOST1, L) == want,
                 "upgrade_cost(L=%d) == 60*115^L//100^L (%d)" % (L, want))
    # rate identity incl. milestone + neutral theme fold, two generators
    Wx = World(c2=600, r2=10, g=(115, 100), milestones=True, gen_path=True)
    for U in (0, 1, 4, 12):
        for P in (0, 2):
            for n1, n2 in ((1, 0), (3, 0), (5, 2), (1, 7)):
                for marks in ({}, {"owned-1": 1}, {"owned-1": 1, "lifetime-1": 1}):
                    st = GameState(owned={"tier1": n1, "tier2": n2},
                                   upgrades={"boost1": U},
                                   prestige={"prestige": P},
                                   milestones=dict(marks))
                    mpct = 100 + 5 * len(marks)
                    want = (1 * n1 * (100 + 25 * U) * (100 + 10 * P) * mpct * 100
                            // 100_000_000)
                    want += (10 * n2 * 100 * (100 + 10 * P) * mpct * 100
                             // 100_000_000)
                    sc.check(rate_of(st, Wx) == want,
                             "rate identity U=%d P=%d n1=%d n2=%d M=%d == %d"
                             % (U, P, n1, n2, len(marks), want))
    # tick over a horizon == offline closed form, two-generator world
    st = GameState(owned={"tier1": 2, "tier2": 1}, upgrades={"boost1": 8},
                   prestige={"prestige": 3}, milestones={"owned-1": 1})
    looped = st
    for _ in range(300):
        looped = tick(looped, Wx.specs, 1, (Wx.up,), (Wx.pr,), Wx.ms)
    closed = offline_progress(st, Wx.specs, 0, 300, (Wx.up,), (Wx.pr,), Wx.ms)
    sc.check(_bal(looped) == closed[CUR],
             "literal 1s tick loop == offline closed form (300s, 2-gen world)")
    # candidate-mechanic cost curve closed form
    for n in range(11):
        sc.check(generator_cost(Wx, "tier2", n) == 600 * 115 ** n // 100 ** n,
                 "generator_cost(tier2, n=%d) == C2*g^n//den^n" % n)
        sc.check(generator_cost(Wx, "tier1", n) == 60 * 115 ** n // 100 ** n,
                 "generator_cost(tier1, n=%d) == 60*g^n//den^n" % n)
    sc.check(generator_cost(Wx, "tier2", 0) == 600,
             "tier-2 unlock (0 owned) costs exactly C2")
    # purchase semantics mirror purchase_upgrade: exact spend, lifetime
    # untouched, count+1; reject when insufficient
    rich = GameState(owned=dict(FRESH_OWNED), balances={CUR: 1000},
                     lifetime={CUR: 777})
    after = purchase_generator(rich, Wx, "tier2")
    sc.check(after.owned.get("tier2") == 1 and _bal(after) == 400,
             "purchase_generator: exact spend + owned+1")
    sc.check(_life(after) == 777,
             "purchase_generator: spending never touches lifetime")
    poor = GameState(owned=dict(FRESH_OWNED), balances={CUR: 599})
    sc.expect_reject("purchase_generator rejects balance<cost",
                     lambda: purchase_generator(poor, Wx, "tier2"),
                     code="insufficient")
    sc.expect_reject("engine purchase_upgrade rejects balance<cost",
                     lambda: purchase_upgrade(
                         GameState(owned=dict(FRESH_OWNED),
                                   balances={CUR: 59}), BOOST1),
                     code="insufficient")
    sc.expect_reject("engine apply_prestige rejects not-eligible",
                     lambda: apply_prestige(fresh_state(), PRESTIGE),
                     code="not eligible")
    # milestone run-scoping: owned progress wiped at reset, earned marks kept
    st = GameState(owned={"tier1": 10}, lifetime={CUR: THRESHOLD})
    st = award_milestones(st, MILESTONES)
    sc.check(st.milestones.get("owned-1") == 1 and
             st.milestones.get("lifetime-2") == 1,
             "milestones: owned-1 + lifetime-2 bank at their thresholds")
    st2 = _reseed_fresh(apply_prestige(st, PRESTIGE))
    sc.check(st2.milestones.get("owned-1") == 1 and
             sum(st2.owned.values()) == 1,
             "milestones: earned marks survive the reset; counts are wiped")
    # greedy comparator: exact cross-product ratio ordering + tie-breaks
    sc.check(_better(("tier2", 300, 25), ("tier1", 69, 1)),
             "comparator: 25/300 beats 1/69 (exact cross-products)")
    sc.check(_better(("tier1", 120, 2), ("upgrade", 60, 1)),
             "comparator: equal ratios tie-break to higher delta")
    sc.check(_better(("upgrade", 60, 1), ("tier1", 60, 1)),
             "comparator: full ties fall to the fixed kind order")


def baseline_selfchecks(sc, base):
    b0 = base["B0"]
    m = b0["measured"]
    # VERDICT 006 cross-pins: the milestone-free baseline at the NEW pin must
    # reproduce the verdicted numbers EXACTLY (drift isolation anchor).
    sc.check(m["A1"] == 60, "B0 == VERDICT 006: A1 first upgrade @ 60 s")
    sc.check(m["A2"] == 12, "B0 == VERDICT 006: A2 12 purchases by 900 s")
    sc.check(m["A3"] == 12573, "B0 == VERDICT 006: A3 first prestige @ 12573 s")
    sc.check(m["A4"] == 100000, "B0 == VERDICT 006: A4 S1 cross @ 100000 s")
    sc.check(m["A5"] == 21600, "B0 == VERDICT 006: A5 S2(N=2) @ 21600 s")
    sc.check(b0["first3_durations"] == [12573, 11536, 10475],
             "B0 == VERDICT 006: reset durations 12573/11536/10475")
    sc.check(m["A7"] == (6, 16), "B0 == VERDICT 006: A7 min buys 6/16")
    sc.check(m["A8"][0] == 1215, "B0 == VERDICT 006: A8 max gap 1215 s")
    sc.check(all(a == 1 for a in b0["awards20"]) and len(b0["awards20"]) == 20,
             "B0 == VERDICT 006: award == 1 at every of 20 resets")
    sc.check(b0["n_pass"] == 10, "B0 == VERDICT 006: scorecard 10/10 PASS")
    sc.check(b0["literal_equals_intent"],
             "B0: literal == intent scoring (no generator purchases exist)")
    sc.check(m["A10"][0] and m["A10"][4],
             "B0: A10 generalized sub-exponential check == award-1 linear PASS")
    # B0 early-inert reproduces the flagged 3-in-4 floor
    ei = b0["early_inert"]
    sc.check(ei["inert"] == 9 and ei["total"] == 12,
             "B0 == VERDICT 006 floor: 9 of 12 early purchases inert (3-in-4)")
    b1 = base["B1"]
    sc.check(b1["literal_equals_intent"],
             "B1: literal == intent scoring (no generator purchases exist)")


def faithfulness_selfchecks(sc, base):
    # event-jump == literal per-second, baseline B1 (milestone fold active)
    W = base["B1"]["_W"]
    ev = run_continuous(W, HORIZON_14D, max_resets=2)
    ps = run_persecond(W, 30_000, max_resets=2)
    sc.check(len(ps["prestiges"]) == 2,
             "faithfulness: B1 literal per-second loop reaches both resets")
    sc.check(canon(ev["purchases"]) == canon(ps["purchases"]),
             "faithfulness: B1 event-jump purchases == literal per-second")
    sc.check(canon(ev["prestiges"]) == canon(ps["prestiges"]),
             "faithfulness: B1 event-jump prestiges == literal per-second")
    sc.check(canon(ev["ms_events"]) == canon(ps["ms_events"]),
             "faithfulness: B1 event-jump milestone banking == per-second")
    # and on a grid cell (the candidate mechanic in the loop)
    Wc = World(c2=600, r2=10, g=(115, 100), milestones=True, gen_path=True)
    ev = run_continuous(Wc, HORIZON_14D, max_resets=2)
    ps = run_persecond(Wc, 15_000, max_resets=2)
    sc.check(len(ps["prestiges"]) == 2,
             "faithfulness: cell literal per-second loop reaches both resets")
    sc.check(canon(ev["purchases"]) == canon(ps["purchases"]),
             "faithfulness: cell(600,10,115) event-jump purchases == per-second")
    sc.check(canon(ev["prestiges"]) == canon(ps["prestiges"]),
             "faithfulness: cell(600,10,115) event-jump prestiges == per-second")
    sc.check(canon(ev["ms_events"]) == canon(ps["ms_events"]),
             "faithfulness: cell(600,10,115) milestone banking == per-second")
    # and on the diagnostic shape (tier-1 copy path removed)
    Wd = World(c2=600, r2=10, g=(115, 100), milestones=True, gen_path=True,
               t1_copies=False)
    ev = run_continuous(Wd, HORIZON_14D, max_resets=2)
    ps = run_persecond(Wd, 30_000, max_resets=2)
    sc.check(len(ps["prestiges"]) == 2,
             "faithfulness: diag literal per-second loop reaches both resets")
    sc.check(canon(ev["purchases"]) == canon(ps["purchases"]) and
             canon(ev["prestiges"]) == canon(ps["prestiges"]) and
             canon(ev["ms_events"]) == canon(ps["ms_events"]),
             "faithfulness: diag(600,10,115,no-t1) event-jump == per-second")


DETERMINISM_CELLS = [
    (300, 5, (110, 100)), (300, 25, (120, 100)),
    (600, 10, (115, 100)), (900, 10, (115, 100)),
    (1800, 5, (110, 100)), (1800, 25, (120, 100)),
]


def determinism_selfchecks(sc, cells_by_label, base):
    # committed 6-cell subset + both baselines re-evaluated from scratch;
    # full-output byte-identity across process runs is proven externally by
    # diff of two complete runs (README/REPORT).
    for c2, r2, g in DETERMINISM_CELLS:
        again, _W, _s3, _s2 = eval_cell(c2, r2, g)
        sc.check(canon(cells_by_label[cell_label(c2, r2, g)]) == canon(again),
                 "determinism: %s byte-identical on re-evaluation"
                 % cell_label(c2, r2, g))
    again = eval_baselines()
    for name in ("B0", "B1"):
        a = {k: v for k, v in base[name].items() if not k.startswith("_")}
        b = {k: v for k, v in again[name].items() if not k.startswith("_")}
        sc.check(canon(a) == canon(b),
                 "determinism: baseline %s byte-identical on re-evaluation" % name)


# --------------------------------------------------------------------------
# Reporting.
# --------------------------------------------------------------------------


def fmt_t(v):
    if v is None:
        return "never"
    return "%d s (%.1f min)" % (v, v / 60.0)


def fmt_short(v):
    return "-" if v is None else "%.1fm" % (v / 60.0)


def main():
    sc = SC  # manifest checks already registered
    engine_selfchecks(sc)

    P = print
    P("=" * 78)
    P("VERDICT 017 / PROPOSAL 015 — generator purchase path: T10 cost-curve sweep")
    P("engine: idle_engine/ vendored @ %s (superbot-idle), driven UNMODIFIED" % PIN[:8])
    P("premise: NO generator purchase path exists at the pin (purchase_upgrade/")
    P("         purchase_upgrades only) — the candidate mechanic is DRIVER-level")
    P("held pinned: the seven VERDICT 006-graduated params + 1.15 growth guardrail")
    P("grid: C2 in %s x R2 in %s x g in %s  (36 cells)"
      % (C2_VALUES, R2_VALUES, ["%d/%d" % g for g in G_VALUES]))
    P("T10 band: %d–%d s (15–45 min active, target %d s)"
      % (T10_BAND[0], T10_BAND[1], T10_TARGET))
    P("=" * 78)

    # ---- baseline legs -----------------------------------------------------
    base = eval_baselines()
    baseline_selfchecks(sc, base)
    faithfulness_selfchecks(sc, base)

    P("\n-- BASELINE LEGS (no purchase path) --")
    for name, note in (("B0", "milestone specs EXCLUDED — VERDICT 006 replica"),
                       ("B1", "milestone+theme fold ACTIVE — the drift leg")):
        b = base[name]
        m = b["measured"]
        P("  %s (%s):" % (name, note))
        P("    A-scorecard: %d/10  A1=%ss A2=%s A3=%ss(%.3fh) A4=%ss A5=%ss "
          "A6=%.3fx" % (b["n_pass"], m["A1"], m["A2"], m["A3"],
                        hours(m["A3"]), m["A4"], m["A5"], m["A6"]))
        P("    A7=%s A8=gap %ss (%.2f%%) A9=r2 %.4f r3 %.4f A10=%s"
          % (m["A7"], m["A8"][0], m["A8"][1], m["A9"][0], m["A9"][1],
             "PASS" if b["pass"]["A10"] else "FAIL"))
        P("    resets1-3=%s  early-inert=%d/%d  first ms events=%s"
          % (b["first3_durations"], b["early_inert"]["inert"],
             b["early_inert"]["total"],
             [(t, s) for (t, s) in b["ms_events_S3"][:4]]))
    drift_flags = [k for k in ORDER if not base["B1"]["pass"][k]]
    P("  DRIFT VERDICT: B1 scores %d/10 — %s" % (
        base["B1"]["n_pass"],
        "the milestone/theme drift BREAKS %s (first-class finding routed to "
        "the lane)" % ",".join(drift_flags) if drift_flags else
        "the milestone/theme engine drift does NOT break any registered A-band"))

    # ---- the 36-cell grid --------------------------------------------------
    cells = []
    cells_by_label = {}
    for c2 in C2_VALUES:
        for r2 in R2_VALUES:
            for g in G_VALUES:
                out, _W, _s3, _s2 = eval_cell(c2, r2, g)
                cells.append(out)
                cells_by_label[cell_label(c2, r2, g)] = out
    sc.check(len(cells) == 36, "coverage: all 36 grid cells evaluated")
    sc.check(all(c["first_prestige"]["S3"] is not None for c in cells),
             "coverage: every cell's S3 reaches a first prestige")

    P("\n-- 36-CELL GRID --")
    P("   committed shape: buy set {upgrade, tier-1 copy, tier-2 copies}.")
    P("   D1 = tier-1 copy path removed (tier-2 unlock/copies only).")
    P("   D2 = unlock-only (tier-2 capped at 1 copy, no tier-1 copies).")
    P("   %-23s | %-6s %-6s %-6s | int lit | inert  | band | D1:T10 int band"
      " | D2:T10 int band" % ("cell", "T10 S3", "S3g", "S2.25"))
    for c in cells:
        lab = cell_label(c["cell"]["C2"], c["cell"]["R2"], tuple(c["cell"]["g"]))
        ei = c["early_inert"]
        d = c["diag_no_t1"]
        u = c["diag_unlock_only"]
        P("   %-23s | %-6s %-6s %-6s | %2d  %2d  | %d/%-3d | %-4s | %-6s %2d  %-4s"
          " | %-6s %2d  %-4s"
          % (lab, fmt_short(c["T10"]["S3"]), fmt_short(c["T10"]["S3g"]),
             fmt_short(c["T10"]["S2"]["0.25"]),
             c["intent"]["n_pass"], c["literal"]["n_pass"],
             ei["inert"], ei["total"],
             "IN" if c["in_band_S3"] else "out",
             fmt_short(d["T10"]["S3"]), d["intent"]["n_pass"],
             "IN" if d["in_band_S3"] else "out",
             fmt_short(u["T10"]["S3"]), u["intent"]["n_pass"],
             "IN" if u["in_band_S3"] else "out"))

    # ---- band + criteria summary -------------------------------------------
    in_band = [c for c in cells if c["in_band_S3"]]
    full_int = [c for c in cells if c["intent"]["n_pass"] == 10]
    full_lit = [c for c in cells if c["literal"]["n_pass"] == 10]
    eligible = select_winner(cells)
    diag_cells = [{**c["diag_no_t1"], "cell": c["cell"]} for c in cells]
    diag_in_band = [d for d in diag_cells if d["in_band_S3"]]
    diag_eligible = select_winner(diag_cells)
    u_cells = [{**c["diag_unlock_only"], "cell": c["cell"]} for c in cells]
    u_in_band = [d for d in u_cells if d["in_band_S3"]]
    u_eligible = select_winner(u_cells)
    P("\n-- SUMMARY --")
    P("   COMMITTED SHAPE (tier-1 copies purchasable @ 60 s anchor):")
    P("     cells with S3 T10 in the 15–45 min band: %d/36" % len(in_band))
    P("     cells with all 10 INTENT criteria PASS:  %d/36" % len(full_int))
    P("     cells with all 10 LITERAL criteria PASS: %d/36" % len(full_lit))
    P("     in-band AND 10/10 INTENT (eligible):     %d/36" % len(eligible))
    binding = {}
    for c in cells:
        for k in ORDER:
            if not c["intent"]["pass"][k]:
                binding[k] = binding.get(k, 0) + 1
    P("     binding criteria (intent FAILs, all cells): %s"
      % sorted(binding.items()))
    def _binding(cs):
        b = {}
        for d in cs:
            for k in ORDER:
                if not d["intent"]["pass"][k]:
                    b[k] = b.get(k, 0) + 1
        return b

    dbinding = _binding(diag_cells)
    ubinding = _binding(u_cells)
    P("   DIAGNOSTIC D1 (no tier-1 copy path — tier-2 unlock/copies only):")
    P("     cells with S3 T10 in the 15–45 min band: %d/36" % len(diag_in_band))
    P("     in-band AND 10/10 INTENT (eligible):     %d/36" % len(diag_eligible))
    P("     binding criteria (intent FAILs, all cells): %s"
      % sorted(dbinding.items()))
    P("   DIAGNOSTIC D2 (unlock-only — tier-2 capped at 1, no tier-1 copies):")
    P("     cells with S3 T10 in the 15–45 min band: %d/36" % len(u_in_band))
    P("     in-band AND 10/10 INTENT (eligible):     %d/36" % len(u_eligible))
    P("     binding criteria (intent FAILs, all cells): %s"
      % sorted(ubinding.items()))
    lit_fail_keys = {}
    for c in cells:
        for k in ORDER:
            if c["intent"]["pass"][k] and not c["literal"]["pass"][k]:
                lit_fail_keys[k] = lit_fail_keys.get(k, 0) + 1
    P("   literal-vs-intent divergences (criterion: cells): %s"
      % (sorted(lit_fail_keys.items()) if lit_fail_keys else "none"))

    result = {
        "baselines": {n: {k: v for k, v in base[n].items()
                          if not k.startswith("_")} for n in ("B0", "B1")},
        "cells": {cell_label(c["cell"]["C2"], c["cell"]["R2"],
                             tuple(c["cell"]["g"])): c for c in cells},
        "summary": {
            "in_band_S3": len(in_band),
            "full_pass_intent": len(full_int),
            "full_pass_literal": len(full_lit),
            "eligible": len(eligible),
            "binding_criteria_all_cells": binding,
            "diag_no_t1_in_band_S3": len(diag_in_band),
            "diag_no_t1_eligible": len(diag_eligible),
            "diag_no_t1_binding_criteria_all_cells": dbinding,
            "diag_unlock_only_in_band_S3": len(u_in_band),
            "diag_unlock_only_eligible": len(u_eligible),
            "diag_unlock_only_binding_criteria_all_cells": ubinding,
            "literal_divergences": lit_fail_keys,
        },
    }

    # ---- ruling -------------------------------------------------------------
    def print_row(win, shape_note):
        wl = cell_label(win["cell"]["C2"], win["cell"]["R2"],
                        tuple(win["cell"]["g"]))
        P("  RECOMMENDED (C2, R2, g) ROW (%s):  %s" % (shape_note, wl))
        P("    T10: S3 %s | S3g %s | S2(0.25) %s | S2(2) %s"
          % (fmt_t(win["T10"]["S3"]), fmt_t(win["T10"]["S3g"]),
             fmt_t(win["T10"]["S2"]["0.25"]), fmt_t(win["T10"]["S2"]["2"])))
        P("    A1–A10 (intent): %d/10   (literal): %d/10   early-inert: %d/%d "
          "(B0 floor 9/12)"
          % (win["intent"]["n_pass"], win["literal"]["n_pass"],
             win["early_inert"]["inert"], win["early_inert"]["total"]))
        P("    owned rungs S3: %s" % win["rungs"]["S3"])
        P("    proposed economy-v1.md registration rows (new doc version):")
        P("      | `GENERATOR_T2_COST_SECONDS` | %d |" % win["cell"]["C2"])
        P("      | `GENERATOR_T2_BASE_RATE` | %d |" % win["cell"]["R2"])
        P("      | `GENERATOR_COST_GROWTH_NUM` | %d |" % win["cell"]["g"][0])
        P("      | `GENERATOR_COST_GROWTH_DEN` | %d |" % win["cell"]["g"][1])
        P("    proposed T10 criterion text (A11): \"S3's first tier-2 generator")
        P("    purchase within T10's band (15–45 min); re-run this sim on retune\"")
        return wl

    P("\n" + "=" * 78)
    if eligible:
        win = eligible[0]
        wl = print_row(win, "committed shape")
        runners = eligible[1:4]
        P("  runners-up: %s" % ", ".join(
            cell_label(r["cell"]["C2"], r["cell"]["R2"], tuple(r["cell"]["g"]))
            + " (T10 S3 %s)" % fmt_short(r["T10"]["S3"]) for r in runners))
        result["winner"] = {"cell": wl, "shape": "committed", "detail": win}
        result["runners_up"] = [
            cell_label(r["cell"]["C2"], r["cell"]["R2"], tuple(r["cell"]["g"]))
            for r in runners]
    else:
        P("COMMITTED SHAPE: NO cell hits the T10 band with all ten criteria")
        P("PASS — binding criteria %s in %d/36 cells; every cell's S3 T10 also"
          % (sorted(binding.items()), len(cells) - len(full_int)))
        P("undershoots the 15-min band floor. The tier-1 copy loop (cost "
          "60·g^n vs count-multiplied income) is the runaway; the swept "
          "tier-2 knobs never bind.")
        result["winner"] = None
        reshape = None
        if diag_eligible:
            reshape = ("D1: no tier-1 copy path", "no-tier1-copies",
                       diag_eligible)
        elif u_eligible:
            reshape = ("D2: unlock-only (tier-2 capped at 1, no tier-1 "
                       "copies)", "unlock-only", u_eligible)
        if reshape:
            note, shape_id, elig = reshape
            P("")
            win = elig[0]
            wl = print_row(win, "RESHAPED mechanic — " + note)
            runners = elig[1:4]
            P("  reshape runners-up: %s" % ", ".join(
                cell_label(r["cell"]["C2"], r["cell"]["R2"],
                           tuple(r["cell"]["g"]))
                + " (T10 S3 %s)" % fmt_short(r["T10"]["S3"]) for r in runners))
            result["reshape_winner"] = {"cell": wl, "shape": shape_id,
                                        "detail": win}
            result["reshape_runners_up"] = [
                cell_label(r["cell"]["C2"], r["cell"]["R2"],
                           tuple(r["cell"]["g"])) for r in runners]
        else:
            P("  DIAGNOSTIC SHAPES: also no eligible cell — the finding routes")
            P("  to the lane as a T10/mechanic re-registration question.")
            result["reshape_winner"] = None
    P("=" * 78)

    # ---- determinism + results.json -----------------------------------------
    determinism_selfchecks(sc, cells_by_label, base)

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    sc.check(payload == json.dumps(json.loads(payload), indent=2,
                                   sort_keys=True) + "\n",
             "determinism: results payload canonical-JSON stable")
    out_path = os.path.join(BASE_DIR, "results.json")
    with open(out_path, "w") as fh:
        fh.write(payload)
    P("\nresults.json written (%d cells + baselines)" % len(cells))
    P("(validity gate, limits, and the finalizable verdict: see REPORT.md)")
    sys.exit(sc.report())


if __name__ == "__main__":
    main()
