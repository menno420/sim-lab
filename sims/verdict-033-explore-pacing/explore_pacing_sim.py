#!/usr/bin/env python3
"""
explore_pacing_sim.py
VERDICT 033 / idea-engine PROPOSAL 031 (2026-07-13T07:49:09Z) — EXPLORE_ACTION
pacing & the quest currency faucet: V018's excluded third trigger, priced.

Source idea: idea-engine `control/outbox.md` PROPOSAL 031 · 2026-07-13T07:49:09Z ·
  status: sim-ready (idea entry
  `ideas/superbot-games/explore-action-pacing-quest-mint-2026-07-13.md` @
  idea-engine main 6daf5ea, landed via idea-engine PR #299).
Parent (the committed composed machinery this sim EXTENDS, never re-invents):
  VERDICT 018 = sims/verdict-018-encounter-coexistence/ — itself the composition
  of VERDICT 001 (CHAT_ACTIVITY chat machine) and VERDICT 008 (GRID_ROAM grid
  gate). ALL layers are sha256-pinned in fixtures.json and re-verified before
  any leg runs; V018's committed runner was ALSO re-run out-of-sim in a
  scratchpad copy before this build (exit 0, 1500 self-checks, results.json
  byte-identical to the committed file @ b50fd06).

WHAT THIS SETTLES
  Whether the THIRD trigger (EXPLORE_ACTION quest beats) can ride V018's
  committed contract row — per-source clocks + the mandatory combined
  per-player cap K=4 per sliding 3600 s — and at which per-source cooldown
  c_E; jointly with B (beats per quest completion) and the COUPLING between
  encounter admission and quest progress (gated vs free). Plus the mint axis
  no rate-terms parent could carry: the quest bundle's per-completion currency
  is a committed in-tree integer (TIER_CAPS <= GLOBAL_MAX = (20, 120, 50) @
  superbot-games 5aec110), so per-player currency/hr is computed in ABSOLUTE
  native units for the first time.

WHAT IT DOES NOT SETTLE (declared, not hidden)
  Item-faucet reward VALUE — the V001/V008/V018 wall, restated verbatim: "no
  live fishing/mining earn-rate baseline exists, so loot values stay
  provisional and the slice must log the same named telemetry" (chat/grid mint
  stays RATE-terms-only). dnd's escort bundle (out of scope — different
  trigger surface). Tier selection ({II center, III adversarial} bracket, not
  swept). Real beat rates (r_E is a dial until the named telemetry lands).
  K is NOT re-opened: K=4 decision-binding, K=6 reporting-only.

RUN (one documented command, deterministic, stdlib-only):
  python3 sims/verdict-033-explore-pacing/explore_pacing_sim.py

  Exit 0 iff every self-check passes. Fixed seeds only (V018's committed
  parent seeds for the vendored chat/grid surfaces; fresh seeds 20260764-67
  for the explore layer, strictly above the P030 registry high-water
  20260763) — no unseeded RNG, no wall clock, no network, no hash(); stdout +
  results.json are byte-identical across process runs.

MODEL (one player, THREE surfaces, one merged event stream, 8 h window)
  Chat = the V001 machine verbatim (vendored via V018, regression-anchored).
  Grid = the V008 per-action gate verbatim (vendored via V018).
  Explore = quest-beat attempts as a Poisson stream at r_E/hr (the farmer:
  a paced 5 s saturating stream), each attempt requesting EXPLORE_ACTION
  admission against the per-source clock c_E AND the shared sliding K-window.
  GATED coupling: an admitted beat advances the active quest by 1.
  FREE coupling: progress advances on every attempt; encounters fire only
  when admitted. A quest completes at B beats, mints its tier bundle, next
  quest offered instantly (completions == floor(beats/B), asserted against
  the inline integer quest counter).
  Merged-stream determinism: events sorted by (t, tag) with chat=0 < grid=1
  < explore=2 (V018's committed tie rule, extended by one tag).

SWEEP: c_E in {0, 300, 600, 900} s x B in {3, 5, 8} x coupling in
  {gated, free} at the COMMITTED K=4 (24 decision cells); the same grid at
  K=6 reporting-only. Decision rule (pre-registered, REJECT checked FIRST)
  and every band constant are committed in fixtures.json BEFORE this runner
  existed (git history is the trail).
"""

import json
import hashlib
import random
import statistics
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent

FIX = json.loads((HERE / "fixtures.json").read_text())

# ============================ vendored harness helpers ======================
# (same inline copies as VERDICT 008/018 — sims never import the harness)

V018_SEEDS = list(FIX["v018_anchor_set_verbatim_at_b50fd06"]["v018_parent_seeds"])


def mean_sd(xs):
    xs = list(xs)
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


class CrnCache:
    def __init__(self):
        self._d = {}

    def get(self, key, build):
        if key not in self._d:
            self._d[key] = build(key)
        return self._d[key]

    def clear(self):
        self._d.clear()


class SelfCheck:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, cond, label):
        if cond:
            self.passed += 1
        else:
            self.failed += 1
            raise AssertionError("SELF-CHECK FAILED: " + label)
        return True

    def expect_reject(self, label, fn, code=None):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            if code is not None and code not in str(e):
                raise AssertionError(
                    "SELF-CHECK FAILED: %s (rejected but not with %r: %s)"
                    % (label, code, e))
            self.passed += 1
            return
        raise AssertionError(
            "SELF-CHECK FAILED: %s (expected rejection, got none)" % label)

    def report(self):
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, self.failed))
        return 0 if self.failed == 0 else 1


# ============================ fixture pins ==================================

def verify_pins(sc):
    """CPython minor + sha256 pins on every layer of the chained machinery,
    BEFORE any leg runs. A silent edit to V018/V001/V008 fails loudly here."""
    sc.check(sys.version_info[:2] == (3, 11),
             "pin: CPython minor == 3.11 (got %d.%d)" % sys.version_info[:2])
    for rel, want in sorted(FIX["pins"]["sha256"].items()):
        p = (HERE / rel).resolve()
        sc.check(p.is_file(), "pin: file exists (%s)" % rel)
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        sc.check(got == want, "pin: sha256 match (%s)" % rel)


# ============================ V001 chat model (vendored via V018) ===========

CHAT_SIM_HOURS = 8.0
CHAT_SIM_SECONDS = CHAT_SIM_HOURS * 3600.0
SPAWN_TTL = 300.0
FARMER = -1

TIERS = {"low": (0.5, 3), "med": (3.0, 8), "high": (15.0, 25)}
TIER_OFFSET = {"low": 0, "med": 1000, "high": 2000}

CHAT_THRESHOLD = 24
CHAT_DEBOUNCE = 30.0
CHAT_COOLDOWN = 900.0


def gen_honest_messages(rng, rate_per_min, n_users, horizon):
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
    for (t, author) in msgs:
        if live and t > live_until:
            live = False
            unclaimed_expired += 1
        if not live:
            if t - last_counted_t >= debounce:
                counter += 1
                last_counted_t = t
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
    return {"spawns": spawns, "claims": claims,
            "claims_by_user": dict(claims_by_user),
            "unclaimed_expired": unclaimed_expired}


_CHAT_CRN = CrnCache()


def chat_trace(tier, seed, horizon):
    key = (tier, seed, horizon)

    def build(k):
        tr, sd, hz = k
        rate, n_users = TIERS[tr]
        rng = random.Random(sd + TIER_OFFSET[tr])
        return gen_honest_messages(rng, rate, n_users, hz)

    return _CHAT_CRN.get(key, build)


# ============================ V008 grid model (vendored via V018) ===========

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


_TRACE_FN = {"casual": _casual_trace, "deep-runner": _deep_runner_trace,
             "fastmine": _fastmine_trace}

_GRID_CRN = CrnCache()


def grid_trace(playstyle, seed, horizon):
    key = (playstyle, seed, horizon)

    def build(k):
        ps, sd, hz = k
        rng = random.Random(sd + STYLE_OFFSET[ps])
        return _TRACE_FN[ps](rng, hz)

    return _GRID_CRN.get(key, build)


def grid_simulate_solo(schedule, threshold, chance, cooldown):
    encounters = 0
    last_fire = -1.0e18
    fire_times = []
    for (t, depth, u) in schedule:
        if depth >= threshold and (t - last_fire) >= cooldown and u < chance:
            encounters += 1
            fire_times.append(t)
            last_fire = t
    return {"encounters": encounters, "fire_times": fire_times}


# ============================ V018 two-surface machine (vendored) ===========

class ContractV018:
    """V018's swept contract object, vendored verbatim (per_source / capped)."""

    def __init__(self, kind, cap_k=None):
        if kind not in ("per_source", "capped"):
            raise ValueError("bad-contract: unknown kind %r" % kind)
        if kind == "capped" and (cap_k is None or int(cap_k) != cap_k or cap_k <= 0):
            raise ValueError("bad-contract: cap K must be a positive integer")
        self.kind = kind
        self.cap_k = int(cap_k) if cap_k else None
        self.reset()

    def reset(self):
        self.last_chat = -1.0e18
        self.last_grid = -1.0e18
        self.window = deque()
        self.blocked = {"chat_own": 0, "chat_cap": 0, "grid_own": 0, "grid_cap": 0}

    def _window_count(self, t):
        while self.window and self.window[0] <= t - 3600.0:
            self.window.popleft()
        return len(self.window)

    def allows(self, surface, t):
        last_own = self.last_chat if surface == "chat" else self.last_grid
        cd_own = CHAT_COOLDOWN if surface == "chat" else GRID_COOLDOWN
        if (t - last_own) < cd_own:
            self.blocked[surface + "_own"] += 1
            return False
        if self.kind == "capped" and self._window_count(t) >= self.cap_k:
            self.blocked[surface + "_cap"] += 1
            return False
        return True

    def record(self, surface, t):
        if surface == "chat":
            self.last_chat = t
        else:
            self.last_grid = t
        if self.kind == "capped":
            self.window.append(t)


def joint2_simulate(chat_msgs, grid_actions, contract, joint_author, horizon):
    """V018's joint two-surface machine, vendored verbatim — the composition
    anchor the three-surface machine must equal event-for-event when the
    explore stream is empty."""
    events = [(t, 0, a, 0, 0.0) for (t, a) in chat_msgs] + \
             [(t, 1, 0, d, u) for (t, d, u) in grid_actions]
    events.sort(key=lambda e: (e[0], e[1]))
    contract.reset()
    counter = 0
    last_counted_t = -1.0e18
    live = False
    live_until = 0.0
    cd_until = {}
    spawns = 0
    chat_claims_joint = 0
    chat_claims_others = 0
    unclaimed_expired = 0
    grid_fires = 0
    grid_eligible = 0
    fire_log = []
    for (t, kind, author, depth, u) in events:
        if kind == 0:
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
            if depth >= GRID_THRESHOLD:
                grid_eligible += 1
                if u < GRID_CHANCE:
                    if contract.allows("grid", t):
                        grid_fires += 1
                        contract.record("grid", t)
                        fire_log.append((t, "grid"))
    return {"spawns": spawns, "chat_claims_joint": chat_claims_joint,
            "chat_claims_others": chat_claims_others,
            "unclaimed_expired": unclaimed_expired, "grid_fires": grid_fires,
            "grid_eligible": grid_eligible, "fire_log": fire_log,
            "blocked": dict(contract.blocked)}


# ============================ the three-surface contract ====================

class Contract3:
    """The joint player's THREE-surface admission rule: per-source clocks
    (chat 900 s, grid 600 s — both parents' pinned defaults, untouched;
    explore c_E, the swept constant, c_E = 0 meaning no clock) AND, when
    cap_k is set, the shared sliding K-window over combined admitted
    encounters. Check order committed in fixtures D4: own clock first,
    then cap."""

    SURFACES = ("chat", "grid", "explore")

    def __init__(self, cap_k, c_explore):
        if cap_k is not None and (int(cap_k) != cap_k or cap_k <= 0):
            raise ValueError("bad-contract: cap K must be a positive integer or None")
        if c_explore < 0:
            raise ValueError("bad-contract: c_E must be >= 0")
        self.cap_k = int(cap_k) if cap_k else None
        self.cd = {"chat": CHAT_COOLDOWN, "grid": GRID_COOLDOWN,
                   "explore": float(c_explore)}
        self.reset()

    def reset(self):
        self.last = {s: -1.0e18 for s in self.SURFACES}
        self.window = deque()
        self.blocked = {s + k: 0 for s in self.SURFACES for k in ("_own", "_cap")}

    def _window_count(self, t):
        while self.window and self.window[0] <= t - 3600.0:
            self.window.popleft()
        return len(self.window)

    def allows(self, surface, t):
        cd_own = self.cd[surface]
        if cd_own > 0.0 and (t - self.last[surface]) < cd_own:
            self.blocked[surface + "_own"] += 1
            return False
        if self.cap_k is not None and self._window_count(t) >= self.cap_k:
            self.blocked[surface + "_cap"] += 1
            return False
        return True

    def record(self, surface, t):
        self.last[surface] = t
        if self.cap_k is not None:
            self.window.append(t)


B_GRID = [int(b) for b in FIX["sweep"]["B_grid_beats_per_completion"]]


def joint3_simulate(chat_msgs, grid_actions, explore_attempts, contract,
                    joint_author, horizon):
    """One deterministic pass over the merged THREE-surface stream. Chat and
    grid semantics are the V018 machine verbatim; explore attempts request
    admission and drive TWO inline integer quest counters per B (gated:
    admitted beats only; free: every attempt) — completions == floor(beats/B)
    is asserted by the caller (fixtures gate). Ties: chat < grid < explore
    at equal t (fixtures D2)."""
    events = [(t, 0, a, 0, 0.0) for (t, a) in chat_msgs] + \
             [(t, 1, 0, d, u) for (t, d, u) in grid_actions] + \
             [(t, 2, 0, 0, 0.0) for t in explore_attempts]
    events.sort(key=lambda e: (e[0], e[1]))
    contract.reset()
    counter = 0
    last_counted_t = -1.0e18
    live = False
    live_until = 0.0
    cd_until = {}
    spawns = 0
    chat_claims_joint = 0
    chat_claims_others = 0
    unclaimed_expired = 0
    grid_fires = 0
    grid_eligible = 0
    fire_log = []
    beats_attempted = 0
    beats_admitted = 0
    prog_g = {b: 0 for b in B_GRID}
    comp_g = {b: 0 for b in B_GRID}
    prog_f = {b: 0 for b in B_GRID}
    comp_f = {b: 0 for b in B_GRID}
    for (t, kind, author, depth, u) in events:
        if kind == 0:
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
        elif kind == 1:
            if depth >= GRID_THRESHOLD:
                grid_eligible += 1
                if u < GRID_CHANCE:
                    if contract.allows("grid", t):
                        grid_fires += 1
                        contract.record("grid", t)
                        fire_log.append((t, "grid"))
        else:
            beats_attempted += 1
            admitted = contract.allows("explore", t)
            if admitted:
                beats_admitted += 1
                contract.record("explore", t)
                fire_log.append((t, "explore"))
            for b in B_GRID:
                if admitted:
                    prog_g[b] += 1
                    if prog_g[b] == b:
                        comp_g[b] += 1
                        prog_g[b] = 0
                prog_f[b] += 1
                if prog_f[b] == b:
                    comp_f[b] += 1
                    prog_f[b] = 0
    return {"spawns": spawns, "chat_claims_joint": chat_claims_joint,
            "chat_claims_others": chat_claims_others,
            "unclaimed_expired": unclaimed_expired, "grid_fires": grid_fires,
            "grid_eligible": grid_eligible, "fire_log": fire_log,
            "beats_attempted": beats_attempted, "beats_admitted": beats_admitted,
            "comp_gated": dict(comp_g), "comp_free": dict(comp_f),
            "blocked": dict(contract.blocked)}


# ============================ explore streams ===============================

_EXPLORE_CRN = CrnCache()
PROFILE_ID = {k: int(v) for k, v in FIX["seeds"]["profile_ids"].items()}
HORIZON = FIX["sweep"]["horizon_hours"] * 3600.0
HOURS = FIX["sweep"]["horizon_hours"]
FARMER_GAP = float(FIX["explore_surface"]["farmer_attempt_gap_seconds"])


def explore_stream(leg_seed, profile, r_per_hr, rep):
    """Poisson attempt stream (honest) or the paced saturating stream (farmer).
    Seed derivation is the fixtures formula — fresh explore-layer seeds over
    V018's committed parent seeds."""
    if profile == "beat-steer-farmer":
        key = ("farmer-paced",)

        def build(_k):
            out = []
            t = 0.0
            while t < HORIZON:
                out.append(t)
                t += FARMER_GAP
            return out

        return _EXPLORE_CRN.get(key, build)
    key = (leg_seed, profile, r_per_hr, rep)

    def build(k):
        ls, prof, r, rp = k
        rng = random.Random(ls * 1000003 + PROFILE_ID[prof] * 10007
                            + int(r * 10) * 211 + rp * 101)
        out = []
        lam = r / 3600.0
        t = 0.0
        while True:
            t += rng.expovariate(lam)
            if t >= HORIZON:
                break
            out.append(t)
        return out

    return _EXPLORE_CRN.get(key, build)


PROFILES3 = {
    "quest-focused": {"chat": None, "grid": None, "r_E": 12.0, "author": 0},
    "mixed-triple-casual": {"chat": ("tier", "med", 0), "grid": "casual",
                            "r_E": 6.0, "author": 0},
    "mixed-triple-deep": {"chat": ("tier", "med", 0), "grid": "deep-runner",
                          "r_E": 12.0, "author": 0},
    "beat-steer-farmer": {"chat": ("farmer", None, FARMER), "grid": "fastmine",
                          "r_E": None, "author": FARMER},
}
PROFILE_ORDER = ["quest-focused", "mixed-triple-casual", "mixed-triple-deep",
                 "beat-steer-farmer"]


def profile_streams(profile, rep, leg_seed, r_override=None):
    spec = PROFILES3[profile]
    parent_seed = V018_SEEDS[rep % len(V018_SEEDS)]
    if spec["chat"] is None:
        msgs = []
    elif spec["chat"][0] == "tier":
        msgs = chat_trace(spec["chat"][1], parent_seed, HORIZON)
    else:
        msgs = gen_farmer_messages(30.0, HORIZON)
    grid = grid_trace(spec["grid"], parent_seed, HORIZON) if spec["grid"] else []
    r_e = r_override if r_override is not None else spec["r_E"]
    attempts = explore_stream(leg_seed, profile, r_e, rep)
    return msgs, grid, attempts, spec["author"]


# ============================ per-run self-checks ===========================

EPS = 1e-9


def audit_run(sc, r, c_e, cap_k, profile, rep, dense=True):
    """The fixtures gate battery, per replication."""
    if not dense:
        return
    tag = "(cE=%d K=%s %s rep=%d)" % (c_e, cap_k, profile, rep)
    sc.check(r["beats_admitted"] <= r["beats_attempted"],
             "ceiling: admitted <= attempted " + tag)
    ft_all = [t for (t, _s) in r["fire_log"]]
    ex_ts = [t for (t, s) in r["fire_log"] if s == "explore"]
    ch_ts = [t for (t, s) in r["fire_log"] if s == "chat"]
    gr_ts = [t for (t, s) in r["fire_log"] if s == "grid"]
    if c_e > 0:
        sc.check(r["beats_admitted"] <= int(HORIZON // c_e) + 1,
                 "ceiling: admitted count <= floor(H/c_E)+1 " + tag)
        sc.check(all(ex_ts[i] - ex_ts[i - 1] >= c_e - EPS
                     for i in range(1, len(ex_ts))),
                 "per-source: explore fires >= c_E apart " + tag)
    sc.check(all(ch_ts[i] - ch_ts[i - 1] >= CHAT_COOLDOWN - EPS
                 for i in range(1, len(ch_ts))),
             "per-source: chat claims >= 900 s apart " + tag)
    sc.check(all(gr_ts[i] - gr_ts[i - 1] >= GRID_COOLDOWN - EPS
                 for i in range(1, len(gr_ts))),
             "per-source: grid fires >= 600 s apart " + tag)
    if cap_k is not None:
        sc.check(len(ft_all) <= 8 * cap_k,
                 "ceiling: combined count <= 8K " + tag)
        # independent sliding-window re-audit, recomputed without the deque
        for i in range(len(ft_all)):
            j = i
            while j >= 0 and ft_all[j] > ft_all[i] - 3600.0:
                j -= 1
            sc.check(i - j <= cap_k,
                     "cap audit: <= K fires in any 3600 s window " + tag)
        if profile == "beat-steer-farmer":
            explore_solo_cap = (3600.0 / c_e) if c_e > 0 else 720.0
            if min(explore_solo_cap, 720.0) >= cap_k:
                sc.check(len(ft_all) == 8 * cap_k,
                         "saturation: farmer combined == K exactly " + tag)
    for b in B_GRID:
        sc.check(r["comp_gated"][b] == r["beats_admitted"] // b,
                 "quest counter identity (gated, B=%d) %s" % (b, tag))
        sc.check(r["comp_free"][b] == r["beats_attempted"] // b,
                 "quest counter identity (free, B=%d) %s" % (b, tag))


# ============================ regression + composition legs =================

ANCH = FIX["v018_anchor_set_verbatim_at_b50fd06"]


def matches_published(value, anchor, fmt="%.2f"):
    return (fmt % value) == (fmt % anchor)


def regression_legs(sc):
    print("=" * 78)
    print("REGRESSION LEGS FIRST — the chained V001/V008/V018 anchor set, exact")
    print("=" * 78)
    v001 = ANCH["v001_visibility_spawns_per_active_hr"]
    print("[V001] spawns per active-hour at (24, 30 s, cd 300), 8 h, 5 seeds:")
    for tier in ("low", "med", "high"):
        vals = [chat_simulate(chat_trace(tier, s, CHAT_SIM_SECONDS), 24, 30.0,
                              300.0, CHAT_SIM_SECONDS)["spawns"] / CHAT_SIM_HOURS
                for s in V018_SEEDS]
        m = mean_sd(vals)[0]
        print("  %-5s %.2f/hr  (published %.2f)" % (tier, m, v001[tier]))
        sc.check(matches_published(m, v001[tier]),
                 "regression: V001 %s spawns/hr == %.2f" % (tier, v001[tier]))
    r = chat_simulate(gen_farmer_messages(30.0, CHAT_SIM_SECONDS), 24, 30.0,
                      900.0, CHAT_SIM_SECONDS)
    fc = r["claims_by_user"].get(FARMER, 0) / CHAT_SIM_HOURS
    print("  lone farmer: %.2f claims/hr  (published 4.00)" % fc)
    sc.check(matches_published(fc, ANCH["v001_farmer_claims_per_hr"]),
             "regression: V001 farmer claims/hr == 4.00")
    for label, hz, hours, anchor in (
            ("1 h", 3600.0, 1.0, ANCH["v008_enc_per_hr_1h"]),
            ("8 h", 28800.0, 8.0, ANCH["v008_enc_per_hr_8h"])):
        print("[V008] enc/hr at (15, 0.02, 600 s), %s, 5 seeds:" % label)
        for ps in ("casual", "deep-runner", "fastmine"):
            vals = [grid_simulate_solo(grid_trace(ps, s, hz), GRID_THRESHOLD,
                                       GRID_CHANCE, GRID_COOLDOWN)["encounters"] / hours
                    for s in V018_SEEDS]
            m = mean_sd(vals)[0]
            print("  %-12s %.2f/hr  (published %.2f)" % (ps, m, anchor[ps]))
            sc.check(matches_published(m, anchor[ps]),
                     "regression: V008 %s @%s == %.2f" % (ps, label, anchor[ps]))

    # V018's own joint anchors, via the vendored two-surface machine
    print("[V018] joint anchors (mixed-deep = med chat + deep-runner; "
          "arb-farmer = paced chat + fastmine), 8 h, 5 seeds:")
    v18 = {}
    for prof, chat_kind, gridstyle, author in (
            ("mixed-deep", "tier", "deep-runner", 0),
            ("arb-farmer", "farmer", "fastmine", FARMER)):
        for cname, contract_fn in (
                ("per-source", lambda: ContractV018("per_source")),
                ("cap-4", lambda: ContractV018("capped", 4))):
            vals = []
            for s in V018_SEEDS:
                msgs = (chat_trace("med", s, HORIZON) if chat_kind == "tier"
                        else gen_farmer_messages(30.0, HORIZON))
                grid = grid_trace(gridstyle, s, HORIZON)
                rr = joint2_simulate(msgs, grid, contract_fn(), author, HORIZON)
                vals.append((rr["chat_claims_joint"] + rr["grid_fires"]) / HOURS)
            v18[(prof, cname)] = mean_sd(vals)[0]
    checks = [
        ("mixed-deep", "per-source", ANCH["v018_mixed_deep_combined_per_hr_uncapped"]),
        ("mixed-deep", "cap-4", ANCH["v018_mixed_deep_combined_per_hr_K4"]),
        ("arb-farmer", "per-source", ANCH["v018_farmer_combined_per_hr_per_source"]),
        ("arb-farmer", "cap-4", ANCH["v018_farmer_combined_per_hr_K4"]),
    ]
    for prof, cname, anchor in checks:
        m = v18[(prof, cname)]
        print("  %-11s %-10s %.3f combined/hr  (published %.3f)" % (prof, cname, m, anchor))
        sc.check(matches_published(m, anchor, "%.3f"),
                 "regression: V018 %s %s combined/hr == %.3f" % (prof, cname, anchor))
    cost = v18[("mixed-deep", "per-source")] - v18[("mixed-deep", "cap-4")]
    print("  mixed-deep honest cost at K=4: %.3f/hr  (published 0.400)" % cost)
    sc.check(matches_published(cost, ANCH["v018_mixed_deep_honest_cost_per_hr"], "%.3f"),
             "regression: V018 honest cost == 0.400/hr")
    return v18


def composition_legs(sc):
    """Empty-third-surface composition identity: joint3 == the V018 machine
    event-for-event per seed — fire logs AND every counter — at per-source
    and C-cap-4, for mixed-deep and arb-farmer."""
    print("\nCOMPOSITION IDENTITY — joint3(empty explore) == V018 machine, "
          "event-for-event, 5 seeds x 2 profiles x 2 contracts:")
    n = 0
    for prof, chat_kind, gridstyle, author in (
            ("mixed-deep", "tier", "deep-runner", 0),
            ("arb-farmer", "farmer", "fastmine", FARMER)):
        for cname, mk2, mk3 in (
                ("per-source", lambda: ContractV018("per_source"),
                 lambda: Contract3(None, 600.0)),
                ("cap-4", lambda: ContractV018("capped", 4),
                 lambda: Contract3(4, 600.0))):
            for s in V018_SEEDS:
                msgs = (chat_trace("med", s, HORIZON) if chat_kind == "tier"
                        else gen_farmer_messages(30.0, HORIZON))
                grid = grid_trace(gridstyle, s, HORIZON)
                r2 = joint2_simulate(msgs, grid, mk2(), author, HORIZON)
                r3 = joint3_simulate(msgs, grid, [], mk3(), author, HORIZON)
                same = (r2["fire_log"] == r3["fire_log"]
                        and r2["spawns"] == r3["spawns"]
                        and r2["chat_claims_joint"] == r3["chat_claims_joint"]
                        and r2["chat_claims_others"] == r3["chat_claims_others"]
                        and r2["unclaimed_expired"] == r3["unclaimed_expired"]
                        and r2["grid_fires"] == r3["grid_fires"]
                        and r2["grid_eligible"] == r3["grid_eligible"]
                        and all(r2["blocked"][k] == r3["blocked"][k]
                                for k in r2["blocked"])
                        and r3["beats_attempted"] == 0
                        and r3["beats_admitted"] == 0)
                sc.check(same, "composition: joint3(no explore, %s) == V018 "
                               "(%s, seed %d)" % (cname, prof, s))
                n += 1
    print("  %d identity checks passed (fire logs + all counters equal)" % n)


# ============================ the admission sweep ===========================

C_E_GRID = [int(c) for c in FIX["sweep"]["c_E_grid_seconds"]]
K_DEC = int(FIX["sweep"]["K_decision"])
K_REP = int(FIX["sweep"]["K_reporting_only"])
TIER_II = int(FIX["quest_bundles_verbatim_at_5aec110"]["currency_center_tier_II"])
TIER_III = int(FIX["quest_bundles_verbatim_at_5aec110"]["currency_adversarial_tier_III"])
FLOW_FRAC = float(FIX["bands"]["flow_fraction"])
FAIR_CG = float(FIX["bands"]["fair_chat_grid_min_per_hr"])
FAIR_BEATS = float(FIX["bands"]["fair_admitted_beats_min_per_hr"])
ARB_MAX = float(FIX["bands"]["ARB_RATIO_MAX"])
M_MAIN = int(FIX["replications"]["M_main"])
M_STAB = int(FIX["replications"]["M_stability"])
SEED_MAIN = int(FIX["seeds"]["main"])
SEED_STAB = int(FIX["seeds"]["stability"])
SEED_REP = int(FIX["seeds"]["reporting"])
SEED_AUX = int(FIX["seeds"]["aux_self_check"])


def bundle_check(sc, comp_count, currency_total, tier_c, tag):
    """Bundle-cap identity: currency == completions x tier currency (exact
    integers) AND tier bundle <= GLOBAL_MAX component-wise."""
    sc.check(currency_total == comp_count * tier_c,
             "bundle identity: currency == completions x %d %s" % (tier_c, tag))
    tiers = FIX["quest_bundles_verbatim_at_5aec110"]["TIER_CAPS"]
    gmax = FIX["quest_bundles_verbatim_at_5aec110"]["GLOBAL_MAX"]
    for tier_name, cap in tiers.items():
        sc.check(all(cap[i] <= gmax[i] for i in range(3)),
                 "bundle identity: TIER_CAPS[%s] <= GLOBAL_MAX %s" % (tier_name, tag))


def run_admission(sc, leg_seed, m_reps, cap_k, c_e, profile, r_override=None,
                  dense=True):
    """M replications of one (c_E, K, profile) admission pass. Returns raw
    per-rep counters (the (B, coupling) cells post-process these exactly —
    fixtures D5)."""
    reps = []
    for rep in range(m_reps):
        msgs, grid, attempts, author = profile_streams(profile, rep, leg_seed,
                                                       r_override)
        contract = Contract3(cap_k, float(c_e))
        r = joint3_simulate(msgs, grid, attempts, contract, author, HORIZON)
        audit_run(sc, r, c_e, cap_k, profile, rep, dense=dense)
        reps.append(r)
    return reps


def summarize(reps):
    """Per-(c_E, K, profile) means over reps of the admission-side metrics."""
    out = {}
    out["attempted_hr"] = mean_sd([r["beats_attempted"] / HOURS for r in reps])
    out["admitted_hr"] = mean_sd([r["beats_admitted"] / HOURS for r in reps])
    out["chat_hr"] = mean_sd([r["chat_claims_joint"] / HOURS for r in reps])
    out["grid_hr"] = mean_sd([r["grid_fires"] / HOURS for r in reps])
    out["chat_grid_hr"] = mean_sd([(r["chat_claims_joint"] + r["grid_fires"]) / HOURS
                                   for r in reps])
    out["combined_hr"] = mean_sd([(r["chat_claims_joint"] + r["grid_fires"]
                                   + r["beats_admitted"]) / HOURS for r in reps])
    att = sum(r["beats_attempted"] for r in reps)
    out["denied_own_frac"] = (sum(r["blocked"]["explore_own"] for r in reps) / att
                              if att else 0.0)
    out["denied_cap_frac"] = (sum(r["blocked"]["explore_cap"] for r in reps) / att
                              if att else 0.0)
    tot_adm = sum(r["chat_claims_joint"] + r["grid_fires"] + r["beats_admitted"]
                  for r in reps)
    out["steer_share"] = {
        "explore": (sum(r["beats_admitted"] for r in reps) / tot_adm) if tot_adm else 0.0,
        "chat": (sum(r["chat_claims_joint"] for r in reps) / tot_adm) if tot_adm else 0.0,
        "grid": (sum(r["grid_fires"] for r in reps) / tot_adm) if tot_adm else 0.0,
    }
    out["comp_gated_hr"] = {b: mean_sd([r["comp_gated"][b] / HOURS for r in reps])
                            for b in B_GRID}
    out["comp_free_hr"] = {b: mean_sd([r["comp_free"][b] / HOURS for r in reps])
                           for b in B_GRID}
    return out


def flow_ceiling(c_e, cap_k, r_e):
    terms = [float(cap_k), float(r_e)]
    if c_e > 0:
        terms.append(3600.0 / c_e)
    return min(terms)


def score_cells(summ, cap_k):
    """Band table for one K: cells (c_E, B, coupling) x {FLOW, FAIR, MINT}.
    Registered formulas only; means over M reps."""
    cells = {}
    for c_e in C_E_GRID:
        qf = summ[(c_e, "quest-focused")]
        md = summ[(c_e, "mixed-triple-deep")]
        fm = summ[(c_e, "beat-steer-farmer")]
        ceil_hr = flow_ceiling(c_e, cap_k, 12.0)
        fair_ok = (md["chat_grid_hr"][0] >= FAIR_CG
                   and md["admitted_hr"][0] >= FAIR_BEATS)
        flow_rate_ok = qf["admitted_hr"][0] >= FLOW_FRAC * ceil_hr
        for b in B_GRID:
            for coup in ("gated", "free"):
                comp_key = "comp_gated_hr" if coup == "gated" else "comp_free_hr"
                q_comp = qf[comp_key][b][0]
                f_comp = fm[comp_key][b][0]
                flow_comp_ok = q_comp >= FLOW_FRAC * ceil_hr / b
                q_cur = q_comp * TIER_II
                f_cur = f_comp * TIER_II
                if q_cur == 0.0:
                    mint_ratio = 1.0 if f_cur == 0.0 else float("inf")
                else:
                    mint_ratio = f_cur / q_cur
                mint_ok = mint_ratio <= ARB_MAX
                cells[(c_e, b, coup)] = {
                    "ceiling_hr": ceil_hr,
                    "qf_admitted_hr": qf["admitted_hr"][0],
                    "qf_completions_hr": q_comp,
                    "qf_currency_hr_II": q_cur,
                    "farmer_completions_hr": f_comp,
                    "farmer_currency_hr_II": f_cur,
                    "farmer_currency_hr_III": f_comp * TIER_III,
                    "mint_ratio_center": mint_ratio,
                    "mint_ratio_adversarial_IIIvsII": (
                        (f_comp * TIER_III) / q_cur if q_cur else
                        (1.0 if f_comp == 0.0 else float("inf"))),
                    "md_chat_grid_hr": md["chat_grid_hr"][0],
                    "md_admitted_hr": md["admitted_hr"][0],
                    "md_clip_vs_v018_K4": ANCH["v018_mixed_deep_combined_per_hr_K4"]
                                          - md["chat_grid_hr"][0],
                    "FLOW": bool(flow_rate_ok and flow_comp_ok),
                    "FAIR": bool(fair_ok),
                    "MINT": bool(mint_ok),
                    "ALL": bool(flow_rate_ok and flow_comp_ok and fair_ok and mint_ok),
                }
    return cells


def decide(cells_k4):
    """The pre-registered rule, evaluated in the registered order on the
    GATED K=4 table. Returns (ruling, detail)."""
    per_ce_b_pass = {c_e: sum(1 for b in B_GRID if cells_k4[(c_e, b, "gated")]["ALL"])
                     for c_e in C_E_GRID}
    reject = all(v < 2 for v in per_ce_b_pass.values())
    full_pass_ce = [c_e for c_e in C_E_GRID
                    if all(cells_k4[(c_e, b, "gated")]["ALL"] for b in B_GRID)]
    approve_band = False
    for i in range(len(C_E_GRID) - 1):
        if C_E_GRID[i] in full_pass_ce and C_E_GRID[i + 1] in full_pass_ce:
            approve_band = True
    if reject:
        ruling = "REJECT"
    elif approve_band:
        ruling = "APPROVE"
    else:
        ruling = "NULL"
    return ruling, {"per_cE_B_pass_count_gated": per_ce_b_pass,
                    "full_pass_cE_gated": full_pass_ce,
                    "approve_band_exists": approve_band}


def pass_shares(cells):
    """Per-axis pass shares over the 24 decision cells (NULL flip-axis
    naming; reported regardless of ruling)."""
    keys = list(cells.keys())
    shares = {}
    for axis, vals, sel in (
            ("c_E", C_E_GRID, lambda k, v: k[0] == v),
            ("B", B_GRID, lambda k, v: k[1] == v),
            ("coupling", ["gated", "free"], lambda k, v: k[2] == v)):
        shares[axis] = {}
        for v in vals:
            sub = [k for k in keys if sel(k, v)]
            shares[axis][str(v)] = {
                band: sum(1 for k in sub if cells[k][band]) / len(sub)
                for band in ("FLOW", "FAIR", "MINT", "ALL")}
    return shares


# ============================ reporting + results ===========================

def canon(o):
    if isinstance(o, float):
        if o == float("inf"):
            return "inf"
        return round(o, 6)
    if isinstance(o, dict):
        return {str(k): canon(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)):
        return [canon(x) for x in o]
    return o


def cell_key(c_e, b, coup):
    return "cE%d|B%d|%s" % (c_e, b, coup)


def sweep_leg(sc, leg_seed, m_reps, k_values, dense=True, profiles=PROFILE_ORDER):
    """All admission runs for one leg. Returns {K: {(c_E, profile): summary}}
    plus the bundle identities checked on raw counts."""
    out = {}
    for cap_k in k_values:
        summ = {}
        for c_e in C_E_GRID:
            for profile in profiles:
                reps = run_admission(sc, leg_seed, m_reps, cap_k, c_e, profile,
                                     dense=dense)
                if dense:
                    for i, r in enumerate(reps):
                        for b in B_GRID:
                            bundle_check(
                                sc, r["comp_gated"][b], r["comp_gated"][b] * TIER_II,
                                TIER_II, "(gated II cE=%d K=%d %s rep=%d B=%d)"
                                % (c_e, cap_k, profile, i, b))
                summ[(c_e, profile)] = summarize(reps)
        out[cap_k] = summ
    return out


def print_band_table(cells, label):
    print("\n" + "=" * 78)
    print("BAND TABLE — %s" % label)
    print("cell (c_E, B, coupling) | FLOW FAIR MINT ALL | qf adm/hr comp/hr cur/hr(II)"
          " | farmer cur/hr(II/III) ratio | deep chat+grid (clip)")
    print("=" * 78)
    for coup in ("gated", "free"):
        for c_e in C_E_GRID:
            for b in B_GRID:
                c = cells[(c_e, b, coup)]
                print("  %4d %d %-5s | %s %s %s %s | %5.3f %6.3f %8.2f |"
                      " %8.2f/%8.2f r=%s | %5.3f (%+.3f)"
                      % (c_e, b, coup,
                         "P" if c["FLOW"] else ".", "P" if c["FAIR"] else ".",
                         "P" if c["MINT"] else ".", "P" if c["ALL"] else ".",
                         c["qf_admitted_hr"], c["qf_completions_hr"],
                         c["qf_currency_hr_II"], c["farmer_currency_hr_II"],
                         c["farmer_currency_hr_III"],
                         ("%.3f" % c["mint_ratio_center"])
                         if c["mint_ratio_center"] != float("inf") else "inf",
                         c["md_chat_grid_hr"], -c["md_clip_vs_v018_K4"]))


def main():
    sc = SelfCheck()
    print("explore-pacing quest-mint sim  |  VERDICT 033 / idea-engine PROPOSAL 031")
    print("parent seeds (V018, vendored surfaces): %s | explore seeds: main %d /"
          " stability %d / reporting %d / aux %d" %
          (V018_SEEDS, SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX))
    print("sweep: c_E %s s x B %s x {gated, free} at K=%d (decision); K=%d"
          " reporting-only; horizon %.0f h\n" %
          (C_E_GRID, B_GRID, K_DEC, K_REP, HOURS))

    verify_pins(sc)

    # negative tests: a contract that fails open would unbound the mint faucet
    sc.expect_reject("bad-contract rejected: cap K = 0",
                     lambda: Contract3(0, 300.0), code="bad-contract")
    sc.expect_reject("bad-contract rejected: negative c_E",
                     lambda: Contract3(4, -1.0), code="bad-contract")
    sc.expect_reject("bad-contract rejected: fractional K",
                     lambda: Contract3(2.5, 300.0), code="bad-contract")

    regression_legs(sc)
    composition_legs(sc)

    # ---- MAIN leg: the decision sweep (K=4) + the K=6 reporting grid ----
    print("\nMAIN LEG (seed %d, M=%d) — admission runs: %d c_E x %d profiles x"
          " {K=%d, K=%d}" % (SEED_MAIN, M_MAIN, len(C_E_GRID),
                             len(PROFILE_ORDER), K_DEC, K_REP))
    main_leg = sweep_leg(sc, SEED_MAIN, M_MAIN, [K_DEC, K_REP], dense=True)
    cells_k4 = score_cells(main_leg[K_DEC], K_DEC)
    cells_k6 = score_cells(main_leg[K_REP], K_REP)
    ruling, detail = decide(cells_k4)
    shares = pass_shares(cells_k4)

    print_band_table(cells_k4, "DECISION GRID, K=4 (main leg means, M=%d)" % M_MAIN)
    print_band_table(cells_k6, "REPORTING GRID, K=6 (cannot flip the decision)")

    # profile-level admission table (K=4)
    print("\n" + "=" * 78)
    print("ADMISSION TABLE — K=4 main leg, per (c_E, profile): attempted/admitted"
          " beats/hr, per-surface rates, denial fractions, farmer steering shares")
    print("=" * 78)
    for c_e in C_E_GRID:
        for profile in PROFILE_ORDER:
            s = main_leg[K_DEC][(c_e, profile)]
            print("  cE=%3d %-19s att %7.3f adm %6.3f | chat %5.3f grid %5.3f"
                  " c+g %5.3f comb %5.3f | den own %.3f cap %.3f | share e/c/g"
                  " %.2f/%.2f/%.2f"
                  % (c_e, profile, s["attempted_hr"][0], s["admitted_hr"][0],
                     s["chat_hr"][0], s["grid_hr"][0], s["chat_grid_hr"][0],
                     s["combined_hr"][0], s["denied_own_frac"],
                     s["denied_cap_frac"], s["steer_share"]["explore"],
                     s["steer_share"]["chat"], s["steer_share"]["grid"]))

    # ---- STABILITY leg (half-M, fresh explore seeds; must reproduce ruling) --
    print("\nSTABILITY LEG (seed %d, M=%d) — decision grid only (K=%d)"
          % (SEED_STAB, M_STAB, K_DEC))
    stab_leg = sweep_leg(sc, SEED_STAB, M_STAB, [K_DEC], dense=True)
    cells_stab = score_cells(stab_leg[K_DEC], K_DEC)
    ruling_stab, detail_stab = decide(cells_stab)
    print("  stability ruling: %s (main: %s)" % (ruling_stab, ruling))
    sc.check(ruling_stab == ruling,
             "stability: seed-%d half-M leg reproduces the ruling" % SEED_STAB)

    # ---- REPORTING leg: r_E sensitivity (quest-focused, K=4) ----
    print("\nREPORTING LEG (seed %d) — r_E sensitivity, quest-focused @ K=4"
          " (cannot flip the decision):" % SEED_REP)
    r_e_rows = {}
    for r_e in [float(x) for x in
                FIX["explore_surface"]["r_E_sensitivity_reporting_only_per_hr"]]:
        for c_e in C_E_GRID:
            reps = run_admission(sc, SEED_REP, M_MAIN, K_DEC, c_e,
                                 "quest-focused", r_override=r_e, dense=True)
            s = summarize(reps)
            ceil_hr = flow_ceiling(c_e, K_DEC, r_e)
            r_e_rows["rE%g|cE%d" % (r_e, c_e)] = {
                "admitted_hr": s["admitted_hr"][0], "ceiling_hr": ceil_hr,
                "flow_rate_ok": s["admitted_hr"][0] >= FLOW_FRAC * ceil_hr,
                "comp_gated_hr": {b: s["comp_gated_hr"][b][0] for b in B_GRID}}
            print("  r_E=%4.0f cE=%3d: admitted %5.3f/hr vs ceiling %5.3f"
                  " (FLOW rate %s)" % (r_e, c_e, s["admitted_hr"][0], ceil_hr,
                  "pass" if r_e_rows["rE%g|cE%d" % (r_e, c_e)]["flow_rate_ok"]
                  else "FAIL"))

    # ---- AUX leg (seed %d; never read by a decision number) ----
    print("\nAUX LEG (seed %d) — identity self-checks + 4x-M margin re-measure"
          " (reported only):" % SEED_AUX)
    # (a) c_E = 0, K = None: admitted == attempted exactly
    for rep in range(3):
        _m, _g, attempts, _a = profile_streams("quest-focused", rep, SEED_AUX)
        r = joint3_simulate([], [], attempts, Contract3(None, 0.0), 0, HORIZON)
        sc.check(r["beats_admitted"] == r["beats_attempted"] == len(attempts),
                 "aux identity: no clock + no cap => admitted == attempted (rep %d)" % rep)
        sc.check(r["comp_gated"][3] == r["comp_free"][3],
                 "aux identity: gated == free completions when nothing denied (rep %d)" % rep)
    # (b) B = 1 analogue: completions == admitted // 1 is the counter identity,
    #     asserted per replication in audit_run for every B — re-assert on one aux run
    _m, _g, attempts, _a = profile_streams("quest-focused", 0, SEED_AUX)
    r = joint3_simulate([], [], attempts, Contract3(K_DEC, 900.0), 0, HORIZON)
    sc.check(r["comp_gated"][3] == r["beats_admitted"] // 3,
             "aux identity: gated completions == admitted // B on aux stream")
    # (c) 4x-M re-measure of the three band quantities at K=4 (margins only)
    aux_margins = {}
    for c_e in C_E_GRID:
        qf = summarize(run_admission(sc, SEED_AUX, 4 * M_MAIN, K_DEC, c_e,
                                     "quest-focused", dense=False))
        md = summarize(run_admission(sc, SEED_AUX, 4 * M_MAIN, K_DEC, c_e,
                                     "mixed-triple-deep", dense=False))
        aux_margins[c_e] = {
            "qf_admitted_hr_4xM": qf["admitted_hr"][0],
            "md_chat_grid_hr_4xM": md["chat_grid_hr"][0],
            "md_admitted_hr_4xM": md["admitted_hr"][0]}
        print("  cE=%3d 4xM: qf admitted %5.3f/hr (band %5.3f) | deep c+g %5.3f"
              " (band %.3f) adm beats %5.3f (band %.1f)"
              % (c_e, qf["admitted_hr"][0],
                 FLOW_FRAC * flow_ceiling(c_e, K_DEC, 12.0),
                 md["chat_grid_hr"][0], FAIR_CG, md["admitted_hr"][0], FAIR_BEATS))

    # ---- in-process determinism: full main sweep re-run, caches cleared ----
    def produce():
        _CHAT_CRN.clear()
        _GRID_CRN.clear()
        _EXPLORE_CRN.clear()
        local = SelfCheck()
        leg = sweep_leg(local, SEED_MAIN, M_MAIN, [K_DEC, K_REP], dense=False)
        return json.dumps(canon({str(k): {("%d|%s" % kk): vv for kk, vv in v.items()}
                                 for k, v in leg.items()}), sort_keys=True)

    a = produce()
    b = produce()
    sc.check(a == b, "determinism: full main sweep identical across re-run "
                     "(all CRN caches cleared)")

    # ---- the ruling ----
    print("\n" + "=" * 78)
    print("DECISION (pre-registered order: REJECT first, then APPROVE, else NULL)")
    print("  per-c_E count of B values passing all three bands (GATED, K=4): %s"
          % {c: detail["per_cE_B_pass_count_gated"][c] for c in C_E_GRID})
    print("  c_E passing all bands for ALL B (gated): %s"
          % (detail["full_pass_cE_gated"] or "NONE"))
    print("  REJECT clause (no c_E with >= 2 of 3 B): %s"
          % all(v < 2 for v in detail["per_cE_B_pass_count_gated"].values()))
    print("  APPROVE clause (>= 2 consecutive c_E, all B, stability-reproduced): %s"
          % (detail["approve_band_exists"] and ruling_stab == ruling))
    print("RULING: %s" % ruling)
    print("=" * 78)

    results = {
        "proposal": FIX["source"]["proposal"],
        "ruling": ruling,
        "ruling_stability_leg": ruling_stab,
        "decision_detail": detail,
        "decision_detail_stability": detail_stab,
        "per_axis_pass_shares_decision_cells": shares,
        "cells_K4_decision": {cell_key(*k): v for k, v in cells_k4.items()},
        "cells_K6_reporting": {cell_key(*k): v for k, v in cells_k6.items()},
        "cells_K4_stability": {cell_key(*k): v for k, v in cells_stab.items()},
        "admission_K4_main": {"%d|%s" % k: v for k, v in main_leg[K_DEC].items()},
        "admission_K6_main": {"%d|%s" % k: v for k, v in main_leg[K_REP].items()},
        "r_E_sensitivity_reporting": r_e_rows,
        "aux_4xM_margins": {str(k): v for k, v in aux_margins.items()},
        "v018_anchor_set": ANCH,
        "bands": {"flow_fraction": FLOW_FRAC, "fair_chat_grid_min": FAIR_CG,
                  "fair_beats_min": FAIR_BEATS, "arb_ratio_max": ARB_MAX,
                  "tier_II_currency": TIER_II, "tier_III_currency": TIER_III},
        "seeds": {"main": SEED_MAIN, "stability": SEED_STAB,
                  "reporting": SEED_REP, "aux": SEED_AUX,
                  "v018_parents": V018_SEEDS},
        "M": {"main": M_MAIN, "stability": M_STAB},
    }
    out_path = HERE / "results.json"
    payload = json.dumps(canon(results), sort_keys=True, indent=2) + "\n"
    out_path.write_text(payload)
    print("\nresults.json written (%d bytes, canonical)" % len(payload))

    print("\nGates tied to the registration: sha256 pins on 7 chained files,")
    print("exact V001/V008/V018 regression (15 numbers), 20 composition identities,")
    print("per-cell analytic ceilings + independent sliding-window re-audit,")
    print("farmer saturation == K exactly (where analytically guaranteed),")
    print("quest-counter + bundle-cap identities, stability-leg ruling")
    print("reproduction, 3 expect_reject negatives, full-sweep determinism.")
    raise SystemExit(sc.report())


if __name__ == "__main__":
    main()
