#!/usr/bin/env python3
"""
encounter_coexistence_sim.py
VERDICT 018 / idea-engine PROPOSAL 016 (2026-07-13T00:37:54Z) — encounter
coexistence: the shared engine's cooldown-namespace contract sweep.

Source idea: idea-engine `control/outbox.md` PROPOSAL 016 · 2026-07-13T00:37:54Z ·
  status: sim-ready (idea entry
  `ideas/superbot/encounter-coexistence-cooldown-contract-2026-07-13.md` @
  3ddaea8fd732d5108a303432ba019d88f5d52709; landed via idea-engine PR #279).
Parents (the two committed trace models this sim COMPOSES, never re-invents):
  VERDICT 001 = sims/intake-003-wild-encounter-spawn-tuning (CHAT_ACTIVITY:
  debounced counter -> spawn -> claim, per-claimer cooldown 900 s, pinned
  threshold=24 / debounce=30 s) and VERDICT 008 =
  sims/verdict-008-mining-grid-encounters (GRID_ROAM: per-action roll gated by
  depth>=15, chance=0.02, per-player cooldown 600 s). Both parent files are
  sha256-pinned in fixtures/MANIFEST.json and re-verified before any leg runs.
Shared seam under contract: superbot-games games/shared/encounter/interface.py
  @ 64b3371 (fixture byte-copy) — one resolution core, all three Q-0186
  triggers, ZERO cooldown/rate surface.

WHAT THIS SETTLES (in RATE terms)
  Which cooldown-namespace contract — (a) per-source clocks at the pinned
  defaults, (b) one shared per-player clock c in {600, 900} s, (c) per-source
  clocks + a combined per-player hourly cap K in {4, 6, 8} — keeps BOTH
  verdicts' pinned shapes simultaneously true for a single player who plays
  BOTH surfaces, bounds the combined interruption rate at the stricter solo
  ceiling (min(4, 6) = 4/hr, the Q-0087 bound the proposal names), and closes
  (or prices) the cross-surface cooldown-arbitrage channel neither solo sim
  could see. Regression legs FIRST: the vendored chat model must reproduce
  VERDICT 001's 0.93/3.00/4.38 spawns per active-hour and the 4-claims/hr
  farmer cap; the vendored grid model must reproduce VERDICT 008's
  0.20/2.80/5.20 enc/hr (1 h) and 0.05/2.95/4.88 (8 h) — exact, self-checked,
  before any joint cell counts (the VERDICT 017 baseline-leg discipline).

WHAT IT DOES NOT SETTLE (declared, not hidden)
  Reward VALUE. Restated verbatim from the parents: "no live fishing/mining
  earn-rate baseline exists, so loot values stay provisional and the slice
  must log the same named telemetry." Every combined-mint conclusion here is
  RATE/fraction-only. The third trigger (EXPLORE_ACTION, superbot-games quest
  beats) inherits the namespace rule by CONTRACT, not by this sweep — its
  pacing is lane-pinned. How much a real player interleaves chat and mining is
  unknown: the mixed profiles BRACKET it (mixed-casual, mixed-deep,
  arbitrage-optimal) and the report carries the bracket, not a point.

RUN (one documented command, deterministic, stdlib-only):
  python3 sims/verdict-018-encounter-coexistence/encounter_coexistence_sim.py

  Exit 0 iff every self-check passes. Fixed seeds only (the parents' own
  SEEDS; seeded streams ARE the committed trace models) — no unseeded RNG, no
  wall clock, no network, no hash(); stdout + results.json are byte-identical
  across process runs.

MODEL (one player, two surfaces, one merged event stream)
  Chat surface — the VERDICT 001 channel model, vendor-copied semantics:
  honest Poisson traffic per tier (or the lone paced farmer), debounced
  counter, one live spawn per channel, TTL 300 s, first off-cooldown message
  claims. The JOINT PLAYER is one author in the channel (author 0 in honest
  tiers; the farmer account in the farmer channel); every OTHER author keeps
  the plain V001 per-claimer 900 s cooldown (they are chat-only players, for
  whom every swept contract is identical — disclosed).
  Grid surface — the VERDICT 008 per-action model, vendor-copied semantics:
  CRN trace of (t, depth, u) per playstyle/seed; an action fires iff
  depth >= 15 AND the contract admits GRID_ROAM at t AND u < 0.02.
  The CONTRACT under sweep is the joint player's cross-surface admission rule:
    a  per-source: chat iff t - last_chat_claim >= 900; grid iff
       t - last_grid_fire >= 600 (the two verdicts' pinned clocks, untouched).
    b  shared(c): any encounter on either surface blocks BOTH for c seconds.
    c  cap(K): per-source clocks AND fewer than K combined encounters in the
       sliding (t-3600, t] window.
  Every admitted chat claim / grid fire records into the contract state.
  Merged-stream determinism: events sorted by (t, stream-tag); chat events
  drive only the channel machine, grid events only the roll gate.

SWEEP: 6 contract cells x 3 joint profiles (mixed-casual, mixed-deep,
  arb-farmer) x 5 seeds at an 8 h window, after 2 regression families. The
  FULL table is printed and committed to results.json; the winner comes from
  the rule committed in grid.json BEFORE results existed.
"""

import json
import hashlib
import random
import statistics
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ============================ vendored harness helpers ======================
# (byte-for-byte behaviour of harness/simharness.py; copied inline per the
#  "sims never import the harness" contract — same copies as VERDICT 008.)

SEEDS = [11, 23, 42, 101, 2027]


def mean_sd(xs):
    """(mean, population stdev); stdev is 0.0 for a single sample."""
    xs = list(xs)
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


class CrnCache:
    """Common-Random-Numbers cache keyed by seed/key (variance reduction)."""

    def __init__(self):
        self._d = {}

    def get(self, key, build):
        if key not in self._d:
            self._d[key] = build(key)
        return self._d[key]

    def clear(self):
        self._d.clear()


class SelfCheck:
    """Assertion battery with a pass counter."""

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
        except Exception as e:  # noqa: BLE001 -- any rejection counts
            if code is not None and code not in str(e):
                raise AssertionError(
                    "SELF-CHECK FAILED: %s (rejected but not with %r: %s)"
                    % (label, code, e))
            self.passed += 1
            self.detail.append((True, label))
            return
        raise AssertionError(
            "SELF-CHECK FAILED: %s (expected rejection, got none)" % label)

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def determinism_check(sc, produce,
                      label="determinism: identical output for identical seed"):
    return sc.check(produce() == produce(), label)


# ============================ fixture pins ==================================

def verify_manifest(sc):
    """Re-verify the sha256 pins BEFORE any leg runs: the seam fixture and the
    two parent trace-model files. A silent parent edit fails this sim loudly."""
    manifest = json.loads((HERE / "fixtures" / "MANIFEST.json").read_text())
    for rel, want in sorted(manifest["sha256"].items()):
        p = (HERE / rel).resolve()
        sc.check(p.is_file(), "manifest: pinned file exists (%s)" % rel)
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        sc.check(got == want, "manifest: sha256 match (%s)" % rel)


# ============================ VERDICT 001 chat model (vendored) =============
# Semantics copied from sims/intake-003-wild-encounter-spawn-tuning/
# wild_encounter_spawn_sim.py (sha256-pinned above): traces, debounce counter,
# one live spawn, TTL, claim rule, analytic caps — byte-equal behaviour is
# PROVEN by the regression legs, not assumed.

CHAT_SIM_HOURS = 8.0
CHAT_SIM_SECONDS = CHAT_SIM_HOURS * 3600.0
SPAWN_TTL = 300.0
FARMER = -1

TIERS = {
    "low":  (0.5, 3),
    "med":  (3.0, 8),
    "high": (15.0, 25),
}
TIER_OFFSET = {"low": 0, "med": 1000, "high": 2000}

CHAT_THRESHOLD = 24
CHAT_DEBOUNCE = 30.0
CHAT_COOLDOWN = 900.0


def gen_honest_messages(rng, rate_per_min, n_users, horizon):
    """Poisson arrivals; author uniform in [0, n_users). Time-sorted [(t, author)]."""
    out = []
    lam = rate_per_min / 60.0
    if lam <= 0.0:
        return out
    t = 0.0
    while True:
        t += rng.expovariate(lam)
        if t >= horizon:
            break
        out.append((t, rng.randrange(n_users)))
    return out


def gen_farmer_messages(gap, horizon):
    """A single farmer account paced exactly `gap` seconds apart from t=0."""
    out = []
    t = 0.0
    while t < horizon:
        out.append((t, FARMER))
        t += gap
    return out


def chat_simulate(messages, threshold, debounce, cooldown, horizon):
    """V001's one-pass channel machine (vendored, plain per-claimer cooldown)."""
    msgs = sorted(messages, key=lambda m: m[0])
    counter = 0
    last_counted_t = -1.0e18
    live = False
    live_until = 0.0
    cd_until = {}
    spawns = 0
    claims = 0
    claims_by_user = defaultdict(int)
    unclaimed_expired = 0
    max_counter = 0
    for (t, author) in msgs:
        if live and t > live_until:
            live = False
            unclaimed_expired += 1
        if not live:
            if t - last_counted_t >= debounce:
                counter += 1
                last_counted_t = t
                if counter > max_counter:
                    max_counter = counter
                if counter >= threshold:
                    spawns += 1
                    counter = 0
                    live = True
                    live_until = t + SPAWN_TTL
        else:
            if cd_until.get(author, -1.0e18) <= t:
                claims += 1
                claims_by_user[author] += 1
                cd_until[author] = t + cooldown
                live = False
    return {
        "spawns": spawns,
        "claims": claims,
        "claims_by_user": dict(claims_by_user),
        "unclaimed_expired": unclaimed_expired,
        "max_counter": max_counter,
    }


_CHAT_CRN = CrnCache()


def chat_trace(tier, seed, horizon):
    key = (tier, seed, horizon)

    def build(k):
        tr, sd, hz = k
        rate, n_users = TIERS[tr]
        rng = random.Random(sd + TIER_OFFSET[tr])
        return gen_honest_messages(rng, rate, n_users, hz)

    return _CHAT_CRN.get(key, build)


def chat_spawn_ceiling_per_hr(threshold, debounce):
    return 3600.0 / ((threshold - 1) * debounce)


# ============================ VERDICT 008 grid model (vendored) =============

GRID_THRESHOLD = 15
GRID_CHANCE = 0.02
GRID_COOLDOWN = 600.0
STYLE_OFFSET = {"casual": 0, "deep-runner": 100000, "fastmine": 200000}


def _casual_trace(rng, horizon):
    out = []
    t = 0.0
    d = 0.0
    while t < horizon:
        d += -0.15 * (d - 5.0) + rng.gauss(0.0, 1.5)
        if rng.random() < 0.04:
            d += rng.uniform(3.0, 8.0)
        d = max(0.0, d)
        out.append((t, int(d), rng.random()))
        t += rng.uniform(20.0, 40.0)
    return out


def _deep_runner_trace(rng, horizon):
    out = []
    t = 0.0
    d = 0.0
    target = rng.uniform(22.0, 38.0)
    while t < horizon:
        d += (target - d) * 0.05 + rng.gauss(0.0, 1.5)
        d = max(0.0, d)
        out.append((t, int(d), rng.random()))
        t += max(1.0, rng.gauss(12.0, 2.0))
    return out


def _fastmine_trace(rng, horizon):
    out = []
    t = 0.0
    park = 30.0
    while t < horizon:
        out.append((t, int(park), rng.random()))
        t += max(0.5, rng.gauss(3.0, 0.5))
    return out


_TRACE_FN = {
    "casual": _casual_trace,
    "deep-runner": _deep_runner_trace,
    "fastmine": _fastmine_trace,
}

_GRID_CRN = CrnCache()


def grid_trace(playstyle, seed, horizon):
    key = (playstyle, seed, horizon)

    def build(k):
        ps, sd, hz = k
        rng = random.Random(sd + STYLE_OFFSET[ps])
        return _TRACE_FN[ps](rng, hz)

    return _GRID_CRN.get(key, build)


def grid_simulate_solo(schedule, threshold, chance, cooldown):
    """V008's one-pass solo gate (vendored) — the grid regression anchor."""
    encounters = 0
    last_fire = -1.0e18
    fire_times = []
    for (t, depth, u) in schedule:
        if depth >= threshold and (t - last_fire) >= cooldown and u < chance:
            encounters += 1
            fire_times.append(t)
            last_fire = t
    return {"encounters": encounters, "fire_times": fire_times}


# ============================ the contract under sweep ======================

class Contract:
    """The joint player's cross-surface admission rule — the swept object.

    kinds: per_source (a), shared (b, param c), capped (c, param K on a
    sliding 3600 s window over COMBINED encounters)."""

    def __init__(self, kind, shared_c=None, cap_k=None,
                 chat_cd=CHAT_COOLDOWN, grid_cd=GRID_COOLDOWN):
        if kind not in ("per_source", "shared", "capped"):
            raise ValueError("bad-contract: unknown kind %r" % kind)
        if kind == "shared":
            if shared_c is None or shared_c <= 0:
                raise ValueError("bad-contract: shared clock c must be > 0")
        if kind == "capped":
            if cap_k is None or int(cap_k) != cap_k or cap_k <= 0:
                raise ValueError("bad-contract: cap K must be a positive integer")
        self.kind = kind
        self.shared_c = shared_c
        self.cap_k = int(cap_k) if cap_k else None
        self.chat_cd = chat_cd
        self.grid_cd = grid_cd
        self.reset()

    def reset(self):
        self.last_chat = -1.0e18
        self.last_grid = -1.0e18
        self.last_any = -1.0e18
        self.window = deque()
        self.blocked = {"chat_own": 0, "chat_cross": 0, "chat_cap": 0,
                        "grid_own": 0, "grid_cross": 0, "grid_cap": 0}

    def _window_count(self, t):
        while self.window and self.window[0] <= t - 3600.0:
            self.window.popleft()
        return len(self.window)

    def allows(self, surface, t, count_block=True):
        """True iff the contract admits an encounter on `surface` at time t.
        Block reasons are tallied for the report (own clock / cross-surface /
        combined cap)."""
        if self.kind == "shared":
            ok = (t - self.last_any) >= self.shared_c
            if not ok and count_block:
                # attribute: own-surface if the last encounter was same-surface
                last_own = self.last_chat if surface == "chat" else self.last_grid
                reason = "_own" if last_own == self.last_any else "_cross"
                self.blocked[surface + reason] += 1
            return ok
        # per_source and capped both start from the two pinned clocks
        last_own = self.last_chat if surface == "chat" else self.last_grid
        cd_own = self.chat_cd if surface == "chat" else self.grid_cd
        if (t - last_own) < cd_own:
            if count_block:
                self.blocked[surface + "_own"] += 1
            return False
        if self.kind == "capped" and self._window_count(t) >= self.cap_k:
            if count_block:
                self.blocked[surface + "_cap"] += 1
            return False
        return True

    def record(self, surface, t):
        if surface == "chat":
            self.last_chat = t
        else:
            self.last_grid = t
        self.last_any = t
        if self.kind == "capped":
            self.window.append(t)


def make_contract(cell_id):
    if cell_id == "A-per-source":
        return Contract("per_source")
    if cell_id == "B-shared-600":
        return Contract("shared", shared_c=600.0)
    if cell_id == "B-shared-900":
        return Contract("shared", shared_c=900.0)
    if cell_id.startswith("C-cap-"):
        return Contract("capped", cap_k=int(cell_id.rsplit("-", 1)[1]))
    raise ValueError("bad-contract: unknown cell %r" % cell_id)


CELL_IDS = ["A-per-source", "B-shared-600", "B-shared-900",
            "C-cap-4", "C-cap-6", "C-cap-8"]

# analytic combined ceilings per cell (self-check surface, from grid.json)
CELL_CEILING = {"A-per-source": 10.0, "B-shared-600": 6.0, "B-shared-900": 4.0,
                "C-cap-4": 4.0, "C-cap-6": 6.0, "C-cap-8": 8.0}
CELL_PRESERVES = {"A-per-source": True, "B-shared-600": False,
                  "B-shared-900": False, "C-cap-4": True, "C-cap-6": True,
                  "C-cap-8": True}


# ============================ the joint machine =============================

def joint_simulate(chat_msgs, grid_actions, contract, joint_author, horizon):
    """One deterministic pass over the merged two-surface stream.

    Chat events drive the V001 channel machine; the JOINT author's claim
    eligibility routes through the contract, every other author keeps the
    plain V001 900 s per-claimer clock. Grid events drive the V008 roll gate
    through the contract. Ties: chat before grid at equal t (committed)."""
    events = [(t, 0, a, 0, 0.0) for (t, a) in chat_msgs] + \
             [(t, 1, 0, d, u) for (t, d, u) in grid_actions]
    events.sort(key=lambda e: (e[0], e[1]))
    contract.reset()

    counter = 0
    last_counted_t = -1.0e18
    live = False
    live_until = 0.0
    cd_until = {}          # other authors' plain chat clocks
    spawns = 0
    chat_claims_joint = 0
    chat_claims_others = 0
    unclaimed_expired = 0
    grid_fires = 0
    grid_eligible = 0
    below_threshold_fires = 0
    fire_log = []          # (t, surface) for the joint player, both surfaces

    for (t, kind, author, depth, u) in events:
        if kind == 0:
            # ---- V001 channel machine (vendored semantics) ----
            if live and t > live_until:
                live = False
                unclaimed_expired += 1
            if not live:
                if t - last_counted_t >= CHAT_DEBOUNCE:
                    counter += 1
                    last_counted_t = t
                    if counter >= CHAT_THRESHOLD:
                        spawns += 1
                        counter = 0
                        live = True
                        live_until = t + SPAWN_TTL
            else:
                if author == joint_author:
                    if contract.allows("chat", t):
                        chat_claims_joint += 1
                        contract.record("chat", t)
                        fire_log.append((t, "chat"))
                        live = False
                else:
                    if cd_until.get(author, -1.0e18) <= t:
                        chat_claims_others += 1
                        cd_until[author] = t + CHAT_COOLDOWN
                        live = False
        else:
            # ---- V008 roll gate (vendored semantics) ----
            if depth >= GRID_THRESHOLD:
                grid_eligible += 1
                if u < GRID_CHANCE:
                    if contract.allows("grid", t):
                        grid_fires += 1
                        contract.record("grid", t)
                        fire_log.append((t, "grid"))
                        if depth < GRID_THRESHOLD:
                            below_threshold_fires += 1
            else:
                if u < GRID_CHANCE:
                    # roll would have hit but depth-gated: structural, no tally
                    pass

    return {
        "spawns": spawns,
        "chat_claims_joint": chat_claims_joint,
        "chat_claims_others": chat_claims_others,
        "unclaimed_expired": unclaimed_expired,
        "grid_fires": grid_fires,
        "grid_eligible": grid_eligible,
        "below_threshold_fires": below_threshold_fires,
        "fire_log": fire_log,
        "blocked": dict(contract.blocked),
    }


# ============================ regression legs ===============================

V001_VIS = {"low": 0.93, "med": 3.00, "high": 4.38}
V008_1H = {"casual": 0.20, "deep-runner": 2.80, "fastmine": 5.20}
V008_8H = {"casual": 0.05, "deep-runner": 2.95, "fastmine": 4.88}
EPS = 1e-9


def matches_published(value, anchor):
    """The parents published their headline rates as %.2f prints; the honest
    exact-reproduction check is therefore: the vendored model's mean, formatted
    exactly as the parent formatted it, equals the published figure."""
    return ("%.2f" % value) == ("%.2f" % anchor)


def regression_legs(sc):
    """The VERDICT 017 baseline-leg discipline: each parent's solo headline
    numbers must reproduce EXACTLY (to the published 2 dp) before any joint
    cell counts. A miss is a first-class finding, not a tuning knob."""
    print("=" * 78)
    print("REGRESSION LEGS FIRST — parents' solo headline rates, reproduced exactly")
    print("=" * 78)

    # -- V001 visibility (thr=24, deb=30, cd=300 — the published sweep leg) --
    print("[chat / VERDICT 001] spawns per active-hour at (24, 30 s), 8 h, 5 seeds:")
    for tier in ("low", "med", "high"):
        vals = [chat_simulate(chat_trace(tier, s, CHAT_SIM_SECONDS), 24, 30.0,
                              300.0, CHAT_SIM_SECONDS)["spawns"] / CHAT_SIM_HOURS
                for s in SEEDS]
        m = mean_sd(vals)[0]
        print("  %-5s %.2f/hr  (published %.2f)" % (tier, m, V001_VIS[tier]))
        sc.check(matches_published(m, V001_VIS[tier]),
                 "regression: V001 %s-tier spawns/hr == %.2f" % (tier, V001_VIS[tier]))

    # -- V001 farmer cap at the recommended set (24, 30, 900) --
    r = chat_simulate(gen_farmer_messages(30.0, CHAT_SIM_SECONDS), 24, 30.0,
                      900.0, CHAT_SIM_SECONDS)
    fc = r["claims_by_user"].get(FARMER, 0) / CHAT_SIM_HOURS
    print("  lone farmer (gap=debounce): %.2f claims/hr  (published 4.00, analytic cap 4.00)" % fc)
    sc.check(matches_published(fc, 4.0), "regression: V001 farmer claims/hr == 4.00")

    # -- V008 solo rates at (15, 0.02, 600), 1 h and 8 h --
    for label, hz, hours, anchor in (("1 h", 3600.0, 1.0, V008_1H),
                                     ("8 h", 28800.0, 8.0, V008_8H)):
        print("[grid / VERDICT 008] enc/hr at (15, 0.02, 600 s), %s, 5 seeds:" % label)
        for ps in ("casual", "deep-runner", "fastmine"):
            vals = [grid_simulate_solo(grid_trace(ps, s, hz), GRID_THRESHOLD,
                                       GRID_CHANCE, GRID_COOLDOWN)["encounters"] / hours
                    for s in SEEDS]
            m = mean_sd(vals)[0]
            print("  %-12s %.2f/hr  (published %.2f)" % (ps, m, anchor[ps]))
            sc.check(matches_published(m, anchor[ps]),
                     "regression: V008 %s enc/hr @%s == %.2f" % (ps, label, anchor[ps]))

    # -- composition identities: the joint machine with one surface empty must
    #    equal the parent machine (per-source contract = the pinned clocks) --
    for s in SEEDS:
        jm = joint_simulate(chat_trace("med", s, CHAT_SIM_SECONDS), [],
                            Contract("per_source"), 0, CHAT_SIM_SECONDS)
        pv = chat_simulate(chat_trace("med", s, CHAT_SIM_SECONDS), 24, 30.0,
                           900.0, CHAT_SIM_SECONDS)
        sc.check(jm["spawns"] == pv["spawns"]
                 and jm["chat_claims_joint"] == pv["claims_by_user"].get(0, 0)
                 and jm["chat_claims_joint"] + jm["chat_claims_others"] == pv["claims"]
                 and jm["unclaimed_expired"] == pv["unclaimed_expired"],
                 "composition: joint(chat-only) == V001 machine (med, seed %d)" % s)
        jg = joint_simulate([], grid_trace("deep-runner", s, 28800.0),
                            Contract("per_source"), 0, 28800.0)
        gv = grid_simulate_solo(grid_trace("deep-runner", s, 28800.0),
                                GRID_THRESHOLD, GRID_CHANCE, GRID_COOLDOWN)
        sc.check(jg["grid_fires"] == gv["encounters"]
                 and [t for (t, sfc) in jg["fire_log"]] == gv["fire_times"],
                 "composition: joint(grid-only) == V008 machine (deep-runner, seed %d)" % s)


def solo_8h_anchors():
    """Same-horizon solo per-surface rates for the joint comparison (P6):
    chat = author 0's claims/hr in the med-tier channel; farmer = the lone
    farmer's claims/hr; grid = each style's solo enc/hr at 8 h."""
    out = {"chat": {}, "grid": {}}
    vals = [chat_simulate(chat_trace("med", s, CHAT_SIM_SECONDS), 24, 30.0,
                          900.0, CHAT_SIM_SECONDS)["claims_by_user"].get(0, 0)
            / CHAT_SIM_HOURS for s in SEEDS]
    out["chat"]["med-author0"] = mean_sd(vals)[0]
    r = chat_simulate(gen_farmer_messages(30.0, CHAT_SIM_SECONDS), 24, 30.0,
                      900.0, CHAT_SIM_SECONDS)
    out["chat"]["farmer"] = r["claims_by_user"].get(FARMER, 0) / CHAT_SIM_HOURS
    for ps in ("casual", "deep-runner", "fastmine"):
        vals = [grid_simulate_solo(grid_trace(ps, s, 28800.0), GRID_THRESHOLD,
                                   GRID_CHANCE, GRID_COOLDOWN)["encounters"] / 8.0
                for s in SEEDS]
        out["grid"][ps] = mean_sd(vals)[0]
    return out


# ============================ the sweep =====================================

PROFILES = {
    "mixed-casual": {"chat": ("tier", "med", 0), "grid": "casual"},
    "mixed-deep":   {"chat": ("tier", "med", 0), "grid": "deep-runner"},
    "arb-farmer":   {"chat": ("farmer", None, FARMER), "grid": "fastmine"},
}
PROFILE_ORDER = ["mixed-casual", "mixed-deep", "arb-farmer"]
HONEST = ["mixed-casual", "mixed-deep"]
JOINT_HOURS = 8.0
JOINT_SECONDS = JOINT_HOURS * 3600.0
STRICTER_SOLO_CEILING = 4.0     # min(chat 4/hr, grid 6/hr) — the Q-0087 bound
ARB_RATIO_MAX = 2.0             # committed in grid.json (V008's 1.86 precedent)


def profile_streams(profile, seed):
    kind, tier, author = PROFILES[profile]["chat"]
    if kind == "tier":
        msgs = chat_trace(tier, seed, JOINT_SECONDS)
    else:
        msgs = gen_farmer_messages(30.0, JOINT_SECONDS)
    grid = grid_trace(PROFILES[profile]["grid"], seed, JOINT_SECONDS)
    return msgs, grid, author


def run_cell(cell_id, sc, dense_checks=True):
    """One contract cell x 3 profiles x 5 seeds. Returns per-profile metrics."""
    out = {}
    for profile in PROFILE_ORDER:
        chat_hr, grid_hr, comb_hr, spawns_hr, blocked_l, share_grid = [], [], [], [], [], []
        for seed in SEEDS:
            msgs, grid, author = profile_streams(profile, seed)
            contract = make_contract(cell_id)
            r = joint_simulate(msgs, grid, contract, author, JOINT_SECONDS)
            c_hr = r["chat_claims_joint"] / JOINT_HOURS
            g_hr = r["grid_fires"] / JOINT_HOURS
            k_hr = c_hr + g_hr
            chat_hr.append(c_hr)
            grid_hr.append(g_hr)
            comb_hr.append(k_hr)
            spawns_hr.append(r["spawns"] / JOINT_HOURS)
            blocked_l.append(r["blocked"])
            total = r["chat_claims_joint"] + r["grid_fires"]
            share_grid.append(r["grid_fires"] / total if total else 0.0)
            if dense_checks:
                sc.check(r["below_threshold_fires"] == 0,
                         "gating: 0 grid fires below depth threshold (%s %s s=%d)"
                         % (cell_id, profile, seed))
                sc.check(k_hr <= CELL_CEILING[cell_id] + EPS,
                         "combined <= cell analytic ceiling %.1f (%s %s s=%d)"
                         % (CELL_CEILING[cell_id], cell_id, profile, seed))
                ft = [t for (t, _s) in r["fire_log"]]
                if cell_id.startswith("B-shared"):
                    c = 600.0 if cell_id.endswith("600") else 900.0
                    sc.check(all(ft[i] - ft[i - 1] >= c - EPS
                                 for i in range(1, len(ft))),
                             "shared clock: combined fires >= c apart (%s %s s=%d)"
                             % (cell_id, profile, seed))
                else:
                    chat_ts = [t for (t, sfc) in r["fire_log"] if sfc == "chat"]
                    grid_ts = [t for (t, sfc) in r["fire_log"] if sfc == "grid"]
                    sc.check(all(chat_ts[i] - chat_ts[i - 1] >= CHAT_COOLDOWN - EPS
                                 for i in range(1, len(chat_ts))),
                             "per-source: chat claims >= 900 s apart (%s %s s=%d)"
                             % (cell_id, profile, seed))
                    sc.check(all(grid_ts[i] - grid_ts[i - 1] >= GRID_COOLDOWN - EPS
                                 for i in range(1, len(grid_ts))),
                             "per-source: grid fires >= 600 s apart (%s %s s=%d)"
                             % (cell_id, profile, seed))
                if cell_id.startswith("C-cap-"):
                    k = int(cell_id.rsplit("-", 1)[1])
                    # sliding-window audit, recomputed independently of the deque
                    for i in range(len(ft)):
                        j = i
                        while j >= 0 and ft[j] > ft[i] - 3600.0:
                            j -= 1
                        sc.check(i - j <= k,
                                 "cap audit: <= K fires in any 3600 s window (%s %s s=%d)"
                                 % (cell_id, profile, seed))
        out[profile] = {
            "chat_claims_hr": mean_sd(chat_hr),
            "grid_fires_hr": mean_sd(grid_hr),
            "combined_hr": mean_sd(comb_hr),
            "channel_spawns_hr": mean_sd(spawns_hr),
            "grid_mint_share": mean_sd(share_grid),
            "blocked": {key: mean_sd([b[key] for b in blocked_l])[0]
                        for key in blocked_l[0]},
        }
    return out


def score_cell(cell_id, cell, solo8):
    """P1..P6 from grid.json, mechanical. Returns (passes, fail_list, distortion)."""
    fails = []
    # P1 wild shape: med-tier channel spawns/hr in [0.5, 6.0] for honest mixed
    for p in HONEST:
        s = cell[p]["channel_spawns_hr"][0]
        if not (0.5 <= s <= 6.0):
            fails.append("P1(%s: spawns %.2f/hr outside [0.5,6.0])" % (p, s))
    # P2 grid shape: gating is self-checked structurally; present at depth; <= solo cap
    if not cell["mixed-deep"]["grid_fires_hr"][0] > 0.0:
        fails.append("P2(mixed-deep grid rate 0 — not present at depth)")
    for p in PROFILE_ORDER:
        g = cell[p]["grid_fires_hr"][0]
        if g > 6.0 + EPS:
            fails.append("P2(%s grid %.2f/hr > 6.0 solo cap)" % (p, g))
    # P3 chat farm cap
    for p in PROFILE_ORDER:
        c = cell[p]["chat_claims_hr"][0]
        if c > 4.0 + EPS:
            fails.append("P3(%s chat %.2f/hr > 4.0 per-claimer cap)" % (p, c))
    # P4 combined bound (the stricter solo ceiling)
    for p in PROFILE_ORDER:
        k = cell[p]["combined_hr"][0]
        if k > STRICTER_SOLO_CEILING + EPS:
            fails.append("P4(%s combined %.2f/hr > %.1f stricter solo ceiling)"
                         % (p, k, STRICTER_SOLO_CEILING))
    # P5 no material arbitrage
    honest_best = max(cell[p]["combined_hr"][0] for p in HONEST)
    arb = cell["arb-farmer"]["combined_hr"][0]
    ratio = arb / honest_best if honest_best > 0 else float("inf")
    if ratio > ARB_RATIO_MAX + EPS:
        fails.append("P5(arb/honest ratio %.2f > %.1f)" % (ratio, ARB_RATIO_MAX))
    # P6 no rate inflation vs same-horizon solo legs
    solo_chat = solo8["chat"]["med-author0"]
    solo_grid = {"mixed-casual": solo8["grid"]["casual"],
                 "mixed-deep": solo8["grid"]["deep-runner"]}
    for p in HONEST:
        if cell[p]["chat_claims_hr"][0] > solo_chat + 0.01:
            fails.append("P6(%s chat %.3f > solo %.3f)"
                         % (p, cell[p]["chat_claims_hr"][0], solo_chat))
        if cell[p]["grid_fires_hr"][0] > solo_grid[p] + 0.01:
            fails.append("P6(%s grid %.3f > solo %.3f)"
                         % (p, cell[p]["grid_fires_hr"][0], solo_grid[p]))
    # distortion (winner tie-break 2): honest per-surface |delta| sum
    distortion = 0.0
    for p in HONEST:
        distortion += abs(cell[p]["chat_claims_hr"][0] - solo_chat)
        distortion += abs(cell[p]["grid_fires_hr"][0] - solo_grid[p])
    return (len(fails) == 0, fails, distortion, ratio)


def added_constraint_rank(cell_id):
    """Winner tie-break 3: smallest added constraint. Per-source pure = 0;
    caps ranked by K descending permissiveness distance from 'nothing added'
    (lower K = tighter = larger rank); shared clocks ranked loosest-first."""
    order = {"A-per-source": 0, "C-cap-8": 1, "C-cap-6": 2, "C-cap-4": 3,
             "B-shared-900": 4, "B-shared-600": 5}
    return order[cell_id]


# ============================ reporting + results ===========================

def canon(o):
    """Canonicalize floats for byte-stable JSON."""
    if isinstance(o, float):
        return round(o, 6)
    if isinstance(o, dict):
        return {k: canon(v) for k, v in sorted(o.items())}
    if isinstance(o, (list, tuple)):
        return [canon(x) for x in o]
    return o


def main():
    sc = SelfCheck()
    print("encounter-coexistence contract sim  |  seeds=%s  joint window=%.0fh" %
          (SEEDS, JOINT_HOURS))
    print("contracts: %s" % CELL_IDS)
    print("profiles: %s (regression legs first)\n" % PROFILE_ORDER)

    verify_manifest(sc)

    # negative tests: a contract that fails OPEN would unbound the combined rate
    sc.expect_reject("bad-contract rejected: shared c <= 0",
                     lambda: Contract("shared", shared_c=0.0), code="bad-contract")
    sc.expect_reject("bad-contract rejected: cap K <= 0",
                     lambda: Contract("capped", cap_k=0), code="bad-contract")
    sc.expect_reject("bad-contract rejected: unknown kind",
                     lambda: Contract("global"), code="bad-contract")

    regression_legs(sc)
    solo8 = solo_8h_anchors()
    print("\nsame-horizon solo anchors (8 h): chat med author-0 %.3f claims/hr, "
          "farmer %.2f claims/hr; grid casual %.2f / deep %.2f / fastmine %.2f enc/hr"
          % (solo8["chat"]["med-author0"], solo8["chat"]["farmer"],
             solo8["grid"]["casual"], solo8["grid"]["deep-runner"],
             solo8["grid"]["fastmine"]))

    # ---- the full contract sweep ----
    cells = {}
    for cell_id in CELL_IDS:
        cells[cell_id] = run_cell(cell_id, sc, dense_checks=True)

    # determinism: whole sweep twice with caches cleared between
    def produce():
        _CHAT_CRN.clear()
        _GRID_CRN.clear()
        local = SelfCheck()
        return {cid: run_cell(cid, local, dense_checks=False) for cid in CELL_IDS}

    determinism_check(sc, produce,
                      "determinism: full contract sweep identical across re-run (CRN cleared)")

    # ---- print the FULL table ----
    print("\n" + "=" * 78)
    print("FULL CONTRACT SWEEP — per profile, mean over %d seeds, %.0f h window"
          % (len(SEEDS), JOINT_HOURS))
    print("combined = the joint player's chat claims + grid fires, per hour")
    print("=" * 78)
    scored = {}
    for cell_id in CELL_IDS:
        cell = cells[cell_id]
        ok, fails, distortion, ratio = score_cell(cell_id, cell, solo8)
        scored[cell_id] = (ok, fails, distortion, ratio)
        print("\n[%s]  ceiling %.1f/hr  preserves-pinned-defaults=%s"
              % (cell_id, CELL_CEILING[cell_id], CELL_PRESERVES[cell_id]))
        print("  profile        chat/hr  grid/hr  combined/hr  spawns/hr  grid-mint-share")
        for p in PROFILE_ORDER:
            row = cell[p]
            print("  %-13s %7.3f  %7.3f  %11.3f  %9.3f  %15.3f"
                  % (p, row["chat_claims_hr"][0], row["grid_fires_hr"][0],
                     row["combined_hr"][0], row["channel_spawns_hr"][0],
                     row["grid_mint_share"][0]))
        print("  arb-vs-honest-mixed ratio = %.3f ; honest distortion = %.4f"
              % (ratio, distortion))
        print("  blocked (arb-farmer, mean/run): %s"
              % json.dumps(canon(cell["arb-farmer"]["blocked"]), sort_keys=True))
        print("  score: %s%s" % ("PASS" if ok else "FAIL",
                                 "" if ok else "  " + "; ".join(fails)))

    # ---- the committed winner rule ----
    passing = [cid for cid in CELL_IDS if scored[cid][0]]
    winner = None
    if passing:
        winner = sorted(passing,
                        key=lambda cid: (not CELL_PRESERVES[cid],
                                         scored[cid][2],
                                         added_constraint_rank(cid)))[0]
    print("\n" + "=" * 78)
    print("WINNER RULE (committed in grid.json before results): passing cells = %s"
          % (passing if passing else "NONE"))
    if winner:
        print("WINNER: %s — %s" % (winner,
              "preserves both verdicts' pinned defaults" if CELL_PRESERVES[winner]
              else "re-pins a parent default"))
    print("=" * 78)

    # per-expectation self-checks on the headline shape of the answer
    sc.check(not scored["A-per-source"][0],
             "headline: pure per-source (a) FAILS — the arbitrage channel is real, "
             "coexistence effects are NOT negligible")
    sc.check(scored["A-per-source"][3] > ARB_RATIO_MAX,
             "headline: arbitrage ratio under (a) exceeds the committed 2.0 bound")
    for p in HONEST:
        k = cells["A-per-source"][p]["combined_hr"][0]
        sc.check(k <= STRICTER_SOLO_CEILING + EPS,
                 "headline: honest %s stays under the 4/hr bound even under (a)" % p)

    results = {
        "regression_legs": {
            "v001_visibility": V001_VIS, "v001_farmer": 4.0,
            "v008_1h": V008_1H, "v008_8h": V008_8H,
            "status": "all reproduced exactly (self-check-enforced)"},
        "solo_8h_anchors": solo8,
        "cells": {cid: {p: {k2: (v2 if not isinstance(v2, tuple) else list(v2))
                            for k2, v2 in cells[cid][p].items()}
                        for p in PROFILE_ORDER} for cid in CELL_IDS},
        "scores": {cid: {"pass": scored[cid][0], "fails": scored[cid][1],
                         "honest_distortion": scored[cid][2],
                         "arb_vs_honest_ratio": scored[cid][3],
                         "preserves_pinned_defaults": CELL_PRESERVES[cid],
                         "analytic_ceiling_hr": CELL_CEILING[cid]}
                   for cid in CELL_IDS},
        "passing_cells": passing,
        "winner": winner,
        "stricter_solo_ceiling_hr": STRICTER_SOLO_CEILING,
        "arb_ratio_max": ARB_RATIO_MAX,
    }
    out_path = HERE / "results.json"
    payload = json.dumps(canon(results), sort_keys=True, indent=2) + "\n"
    out_path.write_text(payload)
    print("\nresults.json written (%d bytes, canonical)" % len(payload))

    print("\n" + "=" * 78)
    print("Invariants tied to analytic caps: GATING (0 grid fires below depth),")
    print("per-cell COMBINED CEILING, per-source clock spacing / shared-clock spacing /")
    print("independent sliding-window cap audit, composition identities to BOTH parent")
    print("machines, exact regression to both verdicts' published numbers, manifest")
    print("sha256 pins, 3 expect_reject negatives, full-sweep determinism.")
    print("=" * 78)
    raise SystemExit(sc.report())


if __name__ == "__main__":
    main()
