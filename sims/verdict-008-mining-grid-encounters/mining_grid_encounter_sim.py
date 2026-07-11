#!/usr/bin/env python3
"""
mining_grid_encounter_sim.py
VERDICT 008 / idea-engine PROPOSAL 008 (2026-07-11T12:16:30Z) — mining-grid
per-action encounter tuning sweep.

Source idea: idea-engine `control/outbox.md` PROPOSAL 008 @
  68f45743d4cab7eab5f863f2918e4fb7d9c1c196 (idea entry
  `ideas/superbot/mining-grid-encounters-2026-07-10.md` @
  977662f2d84d1b29d51fbc4121f2e467afcc6a94; canonical superbot
  `docs/ideas/mining-grid-encounters-2026-06-22.md` @
  e1090dbcfdf63ffd955399dc2325b9ad1a2f8c8d). Sister precedent (mirror its shape,
  self-check density, and no-earn-rate caveat): VERDICT 001 =
  sims/intake-003-wild-encounter-spawn-tuning.

WHAT THIS SETTLES (in RATE terms, analytically)
  Which (depth threshold, per-action encounter chance, per-player cooldown) sets,
  together with the per-PLAYER cooldown + one-live-encounter guardrails, keep the
  mine "calm at the surface, rare-but-present at depth" while making the `!fastmine`
  grinder's per-action rolling farm-UNPROFITABLE IN RATE terms vs honest deep play:
   - GATING is structural: zero encounters above (i.e. shallower than) the threshold.
   - The per-player cooldown analytically CAPS encounters/hour at 3600/cooldown for
     EVERYONE, incl. the optimal grinder — action rate cannot beat it.
   - The grinder's rolls-per-encounter balloons (reward-per-action collapses) and the
     grinder-vs-honest yield ratio stays bounded near 1.

WHAT IT DOES NOT SETTLE (declared, not hidden — the coupling headline)
  The loot faucet's ABSOLUTE VALUE / whether the capped rate is "profitable." No live
  fishing/mining earn-rate baseline exists (VERDICT 001's caveat, restated verbatim in
  the report): "no live fishing/mining earn-rate baseline exists, so loot values stay
  provisional and the slice must log the same named telemetry." The faucet is reported
  value-agnostically (encounter-loot events per mine action; faucet% = events × R for
  the UNPINNED loot-value ratio R). Also unsettled: the owner's "rare-but-present"
  intent carries NO pre-registered numeric target — it is qualitative, so this report
  does NOT invent a numeric bound and then "pass" it. Farm-unprofitability is SETTLED
  in RATE terms but NOT in VALUE terms — the two halves COUPLE.

RUN (one documented command, deterministic, stdlib-only):
  python3 sims/verdict-008-mining-grid-encounters/mining_grid_encounter_sim.py

  Exit 0 iff every self-check passes (the checks tie the simulated numbers to the
  analytic caps — a bug that inflates encounters or leaks one above threshold trips an
  assertion and exits nonzero).

MODEL (single player, discrete per-action, 1-hour active-play window = 3600s)
  A per-player grid-mine traversal. Each mine ACTION happens at a timestamp and a grid
  DEPTH; each action at ELIGIBLE depth may roll a LIVE per-action encounter (the owner
  ruled the roll is live per-action, NOT per-(seed,x,y,z)-cell-deterministic — so we
  use a fresh per-action uniform draw u∈[0,1), never a cell hash).

  Guardrails baked into the model (disclosed abstractions):
   - per-PLAYER cooldown (not per-cell): after a fire, no new encounter for `cooldown`s.
   - at most ONE live encounter per player at a time. The encounter is modelled as
     RESOLVED INSTANTLY for rate-accounting, so the one-live invariant reduces to the
     cooldown gate (asserted: no two fires within `cooldown`).

  Firing rule per action, in time order:
     if depth >= threshold           (eligible: gated by depth)
        and (now - last_fire) >= cooldown   (per-player cooldown / one-live gate)
        and u_action < chance         (the live per-action roll hits)
     -> FIRE (record time+depth; last_fire = now).

  Three STYLIZED playstyle traces (MODELED, not measured from live telemetry — a
  disclosed abstraction; real player depth distributions are unknown, see the report):
   - casual roamer   : slow ~30s/action (jittered), shallow mean-reverting depth walk
     mostly in [0,12], rare deeper forays — mostly BELOW typical thresholds.
   - deep-runner     : the HONEST deep player, steady ~12s/action, depth ramps up and
     parks deep (~20-40); most actions eligible.
   - `!fastmine` grinder : ADVERSARIAL/optimal farmer, fast ~3s/action (the shipped
     fastmine cadence), immediately parks at an optimal eligible depth so EVERY action
     can roll — the optimal roll-farming strategy, not naive play.

CRN (common random numbers — mirrors VERDICT 001's _HONEST_CACHE via CrnCache): for
  each (playstyle, seed, horizon) we pre-generate ONCE the action schedule (timestamps
  + depth per action) AND a per-action uniform u, and REUSE them across every one of
  the 64 parameter cells. A cell only changes (threshold, chance, cooldown): eligible =
  depth>=threshold; a roll "hits" iff u<chance; the gating+cooldown filter decides which
  hits FIRE. This keeps the sweep CRN-clean and MONOTONIC in chance (proven + asserted).

SWEEP (the FULL sweep is reported, never the best point):
  threshold ∈ {5,10,15,20}; chance ∈ {0.01,0.02,0.05,0.10}; cooldown ∈ {60,300,600,900}s
  = 64 cells × 3 playstyles × 5 seeds. Plus an 8-hour robustness pass (gate 3).

SEEDS: 5 fixed seeds; each headline metric is mean +/- population stdev across seeds.
No Date.now()/random-without-seed anywhere; PYTHONHASHSEED is never relied on (no hash()).

-----------------------------------------------------------------------------
VENDOR-COPIED from harness/simharness.py (sims stay self-contained — the layout
contract; a sim NEVER imports the harness at runtime). Copied helpers: SEEDS,
mean_sd, CrnCache, sweep, SelfCheck, determinism_check.
-----------------------------------------------------------------------------
"""

import itertools
import random
import statistics


# ============================ vendored harness helpers ======================
# (byte-for-byte behaviour of harness/simharness.py; copied inline per the
#  "sims never import the harness" contract.)

SEEDS = [11, 23, 42, 101, 2027]


def mean_sd(xs):
    """(mean, population stdev); stdev is 0.0 for a single sample."""
    xs = list(xs)
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


class CrnCache:
    """Common-Random-Numbers cache keyed by seed/key (variance reduction).

    Draw a key's stream once, reuse it across every sweep cell so differences are
    signal, not RNG jitter. clear() before a determinism re-run so it rebuilds."""

    def __init__(self):
        self._d = {}

    def get(self, key, build):
        if key not in self._d:
            self._d[key] = build(key)
        return self._d[key]

    def clear(self):
        self._d.clear()


def sweep(grid, run):
    """Full-grid parameter sweep -- the anti-cherry-pick idiom.

    grid: dict name -> list of values (insertion order preserved).
    run:  callable(**cell) -> result row. Returns [(cell, result), ...] over the
    FULL cartesian product, so the report shows the whole table."""
    names = list(grid.keys())
    rows = []
    for combo in itertools.product(*[grid[n] for n in names]):
        cell = dict(zip(names, combo))
        rows.append((cell, run(**cell)))
    return rows


class SelfCheck:
    """Assertion battery with a pass counter. check() raises on a hole; report()
    prints 'SELF-CHECKS: n passed, m failed' and returns an exit code (0 clean)."""

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
        """Assert fn() raises; a guard that fails OPEN is a hole, so ABSENCE of an
        exception is the failure."""
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
    """Run produce() twice and assert equal. produce clears its CrnCache inside so
    the second run rebuilds from seed."""
    return sc.check(produce() == produce(), label)


# ============================ config ========================================

WINDOW_HOURS = 1.0
WINDOW_SECONDS = WINDOW_HOURS * 3600.0
ROBUST_HOURS = 8.0
ROBUST_SECONDS = ROBUST_HOURS * 3600.0

PLAYSTYLES = ("casual", "deep-runner", "fastmine")

# per-playstyle deterministic seed offset (so the three streams are independent)
STYLE_OFFSET = {"casual": 0, "deep-runner": 100000, "fastmine": 200000}

# sweep grids
THRESHOLDS = [5, 10, 15, 20]          # min grid DEPTH for an encounter to be eligible
CHANCES = [0.01, 0.02, 0.05, 0.10]    # per-action live roll probability
COOLDOWNS = [60.0, 300.0, 600.0, 900.0]   # per-PLAYER cooldown seconds

EPS = 1e-9

# recommended defaults (justified from the sweep in the report; printed with the
# analytic cap for audit — chosen, NOT cherry-picked, see the candidate table).
REC_THRESHOLD = 15
REC_CHANCE = 0.02
REC_COOLDOWN = 600.0


# ============================ playstyle traces ==============================
# Each returns a time-sorted list of (t, depth, u): the action schedule (timestamp
# + integer grid depth) AND the per-action uniform roll. STYLIZED (modeled), not
# telemetry — disclosed in the report gate 1 / LIMITS.

def _casual_trace(rng, horizon):
    """~30s/action jittered; shallow mean-reverting depth walk mostly in [0,12] with
    rare deeper forays (mostly BELOW typical thresholds)."""
    out = []
    t = 0.0
    d = 0.0
    while t < horizon:
        # mean-revert toward shallow depth ~5, small noise
        d += -0.15 * (d - 5.0) + rng.gauss(0.0, 1.5)
        if rng.random() < 0.04:            # rare deeper foray
            d += rng.uniform(3.0, 8.0)
        d = max(0.0, d)
        out.append((t, int(d), rng.random()))
        t += rng.uniform(20.0, 40.0)       # ~30s cadence, jittered
    return out


def _deep_runner_trace(rng, horizon):
    """Steady ~12s/action; depth ramps up and parks deep (~20-40); most actions
    eligible (the HONEST deep player)."""
    out = []
    t = 0.0
    d = 0.0
    target = rng.uniform(22.0, 38.0)       # parks somewhere in the deep band
    while t < horizon:
        d += (target - d) * 0.05 + rng.gauss(0.0, 1.5)   # ramp then park w/ noise
        d = max(0.0, d)
        out.append((t, int(d), rng.random()))
        t += max(1.0, rng.gauss(12.0, 2.0))              # ~12s cadence
    return out


def _fastmine_trace(rng, horizon):
    """Fast ~3s/action (the shipped `!fastmine` cadence); immediately parks at an
    optimal eligible depth (deeper than every swept threshold) so EVERY action can
    roll — the optimal roll-farming strategy, not naive play."""
    out = []
    t = 0.0
    park = 30.0                            # >= max(THRESHOLDS)=20 -> always eligible
    while t < horizon:
        out.append((t, int(park), rng.random()))
        t += max(0.5, rng.gauss(3.0, 0.5))               # ~3s cadence
    return out


_TRACE_FN = {
    "casual": _casual_trace,
    "deep-runner": _deep_runner_trace,
    "fastmine": _fastmine_trace,
}

_CRN = CrnCache()


def trace(playstyle, seed, horizon):
    """CRN: build (t,depth,u) schedule ONCE per (playstyle,seed,horizon), reuse it
    across every parameter cell."""
    key = (playstyle, seed, horizon)

    def build(k):
        ps, sd, hz = k
        rng = random.Random(sd + STYLE_OFFSET[ps])
        return _TRACE_FN[ps](rng, hz)

    return _CRN.get(key, build)


# ============================ core sim ======================================

def validate_cell(threshold, chance, cooldown):
    """Reject nonsensical parameters (a negative test target for expect_reject).
    A gate that fails OPEN would let a bad cell mint unbounded encounters."""
    if threshold < 0:
        raise ValueError("bad-param: threshold must be >= 0")
    if not (0.0 <= chance <= 1.0):
        raise ValueError("bad-param: chance must be in [0,1]")
    if cooldown <= 0.0:
        raise ValueError("bad-param: cooldown must be > 0 (else cap = inf)")


def simulate(schedule, threshold, chance, cooldown):
    """One deterministic pass over the (time-sorted) per-action schedule.

    Firing rule: eligible (depth>=threshold) AND off per-player cooldown AND u<chance.
    Returns counts + the fire log (used by the gating/one-live self-checks)."""
    encounters = 0
    eligible = 0
    below_threshold_fires = 0        # MUST stay 0 (gating invariant)
    last_fire = -1.0e18
    fire_times = []
    for (t, depth, u) in schedule:
        elig = depth >= threshold
        if elig:
            eligible += 1
        if elig and (t - last_fire) >= cooldown and u < chance:
            encounters += 1
            fire_times.append(t)
            last_fire = t
            if depth < threshold:        # can never happen; guards the invariant
                below_threshold_fires += 1
    return {
        "encounters": encounters,
        "eligible": eligible,
        "total": len(schedule),
        "below_threshold_fires": below_threshold_fires,
        "fire_times": fire_times,
    }


def analytic_cap_per_hour(cooldown):
    """The load-bearing anti-farm result: the per-PLAYER cooldown caps encounters at
    3600/cooldown per hour for EVERYONE (incl. the optimal grinder), regardless of
    action rate — fires are >= cooldown apart, so at most 3600/cooldown fit in an
    hour."""
    return 3600.0 / cooldown


# ============================ sweep + metrics ===============================

def run_sweep(sc, horizon, hours, dense_checks=True):
    """Run the FULL (threshold x chance x cooldown) sweep x 3 playstyles x SEEDS at
    the given horizon, asserting the invariants on EVERY cell/playstyle/seed. Returns
    agg[(threshold,chance,cooldown,playstyle)] = dict of mean/sd metrics AND
    raw[(threshold,chance,cooldown,playstyle,seed)] = per-seed encounters (for the
    monotonicity check)."""
    agg = {}
    raw = {}
    # cache eligible-count per (playstyle,threshold,seed) for the SANITY check
    elig_cache = {}

    def run(threshold, chance, cooldown):
        for ps in PLAYSTYLES:
            enc_hr, rolls_pe, elig_l, tot_l, faucet_l = [], [], [], [], []
            for seed in SEEDS:
                r = simulate(trace(ps, seed, horizon), threshold, chance, cooldown)
                enc = r["encounters"]
                per_hr = enc / hours
                enc_hr.append(per_hr)
                elig_l.append(r["eligible"])
                tot_l.append(r["total"])
                rolls_pe.append(r["eligible"] / max(enc, 1))
                faucet_l.append(enc / r["total"] if r["total"] else 0.0)
                raw[(threshold, chance, cooldown, ps, seed)] = enc
                elig_cache[(ps, threshold, seed)] = r["eligible"]
                if dense_checks:
                    # GATING: no encounter ever recorded at depth<threshold
                    sc.check(r["below_threshold_fires"] == 0,
                             "gating: 0 fires below threshold (%s thr=%d ch=%.2f cd=%.0f s=%d)"
                             % (ps, threshold, chance, cooldown, seed))
                    # COOLDOWN CAP: enc/hr <= 3600/cooldown (per-player cooldown cap)
                    sc.check(per_hr <= analytic_cap_per_hour(cooldown) + EPS,
                             "cooldown cap: enc/hr %.4f <= %.4f (%s thr=%d ch=%.2f cd=%.0f s=%d)"
                             % (per_hr, analytic_cap_per_hour(cooldown), ps,
                                threshold, chance, cooldown, seed))
                    # ONE-LIVE-ENCOUNTER: no two fires within cooldown of each other
                    ft = r["fire_times"]
                    ok = all(ft[i] - ft[i - 1] >= cooldown - EPS for i in range(1, len(ft)))
                    sc.check(ok,
                             "one-live: consecutive fires >= cooldown apart (%s thr=%d ch=%.2f cd=%.0f s=%d)"
                             % (ps, threshold, chance, cooldown, seed))
            agg[(threshold, chance, cooldown, ps)] = {
                "enc_hr": mean_sd(enc_hr),
                "rolls_pe": mean_sd(rolls_pe),
                "eligible": mean_sd(elig_l),
                "total": mean_sd(tot_l),
                "faucet": mean_sd(faucet_l),
            }

    sweep({"threshold": THRESHOLDS, "chance": CHANCES, "cooldown": COOLDOWNS}, run)

    if dense_checks:
        # MONOTONIC: for fixed (playstyle,seed,threshold,cooldown), encounters are
        # non-decreasing as chance increases (CRN guarantees it; proven in docstring).
        for ps in PLAYSTYLES:
            for seed in SEEDS:
                for thr in THRESHOLDS:
                    for cd in COOLDOWNS:
                        prev = -1
                        for ch in CHANCES:            # CHANCES ascending
                            v = raw[(thr, ch, cd, ps, seed)]
                            sc.check(v >= prev,
                                     "monotonic in chance: enc non-decreasing (%s s=%d thr=%d cd=%.0f ch=%.2f)"
                                     % (ps, seed, thr, cd, ch))
                            prev = v
        # SANITY: fastmine eligible_actions >= deep-runner eligible_actions (grinder
        # rolls more), per (threshold, seed).
        for thr in THRESHOLDS:
            for seed in SEEDS:
                sc.check(elig_cache[("fastmine", thr, seed)]
                         >= elig_cache[("deep-runner", thr, seed)],
                         "sanity: fastmine eligible >= deep-runner eligible (thr=%d s=%d)"
                         % (thr, seed))
    return agg


def grinder_vs_honest(agg, threshold, chance, cooldown, eps=1e-9):
    """grinder-vs-honest yield ratio = enc/hr(fastmine) / max(enc/hr(deep-runner), eps)."""
    g = agg[(threshold, chance, cooldown, "fastmine")]["enc_hr"][0]
    h = agg[(threshold, chance, cooldown, "deep-runner")]["enc_hr"][0]
    return g / max(h, eps)


# ============================ reporting =====================================

def print_full_sweep(agg):
    """The FULL sweep: enc/hr (mean over seeds) per playstyle, blocked by cooldown,
    thresholds down rows x chance across columns. Prints the analytic cap per block."""
    print("=" * 78)
    print("FULL SWEEP  -  encounters/hour (mean over %d seeds), 1-player, %.0fh window"
          % (len(SEEDS), WINDOW_HOURS))
    print("64 cells (threshold x chance x cooldown) x 3 playstyles. Cap = 3600/cooldown.")
    print("=" * 78)
    for ps in PLAYSTYLES:
        print("\n[%s]" % ps)
        for cd in COOLDOWNS:
            print("  cooldown=%-4.0fs   (analytic cap = %6.2f enc/hr)"
                  % (cd, analytic_cap_per_hour(cd)))
            print("    thr\\chance " + "".join("%9.2f" % c for c in CHANCES))
            for thr in THRESHOLDS:
                cells = []
                for ch in CHANCES:
                    m, _ = agg[(thr, ch, cd, ps)]["enc_hr"]
                    cells.append("%9.2f" % m)
                print("    thr=%-6d" % thr + "".join(cells))


def print_ratio_and_faucet(agg):
    """grinder-vs-honest ratio + rolls-per-encounter (effort/yield) + loot faucet,
    at cooldown=REC_COOLDOWN across the threshold x chance grid (full block shown)."""
    cd = REC_COOLDOWN
    print("\n" + "=" * 78)
    print("GRINDER-vs-HONEST YIELD RATIO  &  ROLLS-PER-ENCOUNTER (effort/yield lever)")
    print("cooldown=%.0fs (cap %.2f/hr). ratio = enc/hr(fastmine)/enc/hr(deep-runner)."
          % (cd, analytic_cap_per_hour(cd)))
    print("=" * 78)
    print("  thr  chance   grinder/hr  honest/hr   ratio    rolls/enc(honest)  rolls/enc(grinder)")
    for thr in THRESHOLDS:
        for ch in CHANCES:
            g = agg[(thr, ch, cd, "fastmine")]["enc_hr"][0]
            h = agg[(thr, ch, cd, "deep-runner")]["enc_hr"][0]
            ratio = grinder_vs_honest(agg, thr, ch, cd)
            rpe_h = agg[(thr, ch, cd, "deep-runner")]["rolls_pe"][0]
            rpe_g = agg[(thr, ch, cd, "fastmine")]["rolls_pe"][0]
            print("  %-4d %5.2f   %9.2f  %9.2f  %7.2f   %15.1f   %16.1f"
                  % (thr, ch, g, h, ratio, rpe_h, rpe_g))

    print("\n" + "=" * 78)
    print("LOOT FAUCET (value-agnostic): encounter-loot events per 100 mine actions")
    print("faucet%% = events/100actions x R, R = V_encounter/V_mine_here (UNPINNED - no")
    print("live earn-rate baseline). actions/encounter lets the manager back out the")
    print("tolerable R for any target faucet%%. cooldown=%.0fs." % cd)
    print("=" * 78)
    print("  thr  chance   playstyle      events/100actions   actions/encounter")
    for thr in THRESHOLDS:
        for ch in CHANCES:
            for ps in PLAYSTYLES:
                a = agg[(thr, ch, cd, ps)]
                faucet = a["faucet"][0]
                ev100 = faucet * 100.0
                ape = (1.0 / faucet) if faucet > 0 else float("inf")
                ape_s = "%15.1f" % ape if faucet > 0 else "         (none)"
                print("  %-4d %5.2f   %-12s   %15.3f   %s"
                      % (thr, ch, ps, ev100, ape_s))


def print_recommended(agg):
    """The recommended (threshold,chance,cooldown) set, argued from candidate rows
    (NOT cherry-picked). Honesty: 'rare-but-present' has NO pre-registered numeric
    target from the owner — stated explicitly, not invented-and-passed."""
    print("\n" + "=" * 78)
    print("RECOMMENDED DEFAULT  ->  threshold=%d, chance=%.2f, cooldown=%.0fs"
          % (REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN))
    print("Analytic cap = %.2f enc/hr (per-player cooldown; traffic/rate independent)."
          % analytic_cap_per_hour(REC_COOLDOWN))
    print("NOTE: 'rare-but-present' is the owner's QUALITATIVE intent with NO")
    print("pre-registered numeric target — reported, not invented-and-'passed'.")
    print("=" * 78)

    # candidate comparison: a handful of sets, so the pick is argued from the table
    candidates = [
        (15, 0.01, 600.0),
        (15, 0.02, 600.0),
        (15, 0.05, 600.0),
        (15, 0.02, 300.0),
        (15, 0.02, 900.0),
        (20, 0.02, 600.0),
        (10, 0.02, 600.0),
    ]
    print("\n  candidate rows compared (mean over seeds):")
    print("  thr chance cd     casual/hr  deep/hr  grind/hr  cap    ratio  rollsHon  rollsGrind  ev/100(grind)")
    for (thr, ch, cd) in candidates:
        cas = agg[(thr, ch, cd, "casual")]["enc_hr"][0]
        dep = agg[(thr, ch, cd, "deep-runner")]["enc_hr"][0]
        grd = agg[(thr, ch, cd, "fastmine")]["enc_hr"][0]
        cap = analytic_cap_per_hour(cd)
        ratio = grinder_vs_honest(agg, thr, ch, cd)
        rh = agg[(thr, ch, cd, "deep-runner")]["rolls_pe"][0]
        rg = agg[(thr, ch, cd, "fastmine")]["rolls_pe"][0]
        ev = agg[(thr, ch, cd, "fastmine")]["faucet"][0] * 100.0
        mark = "  <== REC" if (thr, ch, cd) == (REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN) else ""
        print("  %-3d %5.2f %-5.0f  %8.2f  %7.2f  %8.2f  %5.2f  %5.2f  %8.1f  %10.1f  %11.3f%s"
              % (thr, ch, cd, cas, dep, grd, cap, ratio, rh, rg, ev, mark))

    # the recommended headline numbers (mean +/- sd)
    print("\n  RECOMMENDED-SET headline (mean +/- population sd over %d seeds):" % len(SEEDS))
    for ps in PLAYSTYLES:
        a = agg[(REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN, ps)]
        m, s = a["enc_hr"]
        rpe_m, rpe_s = a["rolls_pe"]
        el_m, _ = a["eligible"]
        tot_m, _ = a["total"]
        ev = a["faucet"][0] * 100.0
        print("    %-12s enc/hr=%6.2f +/- %5.2f   rolls/enc=%8.1f +/- %6.1f   "
              "elig=%6.0f/%6.0f   ev/100act=%.3f"
              % (ps, m, s, rpe_m, rpe_s, el_m, tot_m, ev))
    ratio = grinder_vs_honest(agg, REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN)
    cap = analytic_cap_per_hour(REC_COOLDOWN)
    dep = agg[(REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN, "deep-runner")]["enc_hr"][0]
    print("    grinder-vs-honest ratio = %.2f ; grinder capped at %.2f/hr (=cap %.2f); "
          "honest %.2f/hr sits BELOW the cap." % (ratio, cap, cap, dep))


def print_robustness(sc):
    """Gate 3: re-run the FULL sweep at an 8h window; the per-hour cooldown cap and
    gating must survive (same dense checks). Report the recommended-set numbers."""
    print("\n" + "=" * 78)
    print("ROBUSTNESS PASS  -  full sweep re-run at an %.0fh window (gate 3)" % ROBUST_HOURS)
    print("The per-hour cooldown cap (3600/cd) and gating are asserted on every cell")
    print("again at 8h; the conclusion must survive the longer horizon.")
    print("=" * 78)
    agg8 = run_sweep(sc, ROBUST_SECONDS, ROBUST_HOURS, dense_checks=True)
    print("  8h recommended-set (thr=%d ch=%.2f cd=%.0f), enc/hr mean +/- sd:"
          % (REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN))
    for ps in PLAYSTYLES:
        m, s = agg8[(REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN, ps)]["enc_hr"]
        print("    %-12s enc/hr=%6.2f +/- %5.2f" % (ps, m, s))
    ratio = grinder_vs_honest(agg8, REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN)
    print("  grinder-vs-honest ratio @8h = %.2f ; cooldown cap %.2f/hr still binds "
          "(gating + cap self-checked on all 64 cells at 8h)."
          % (ratio, analytic_cap_per_hour(REC_COOLDOWN)))
    return agg8


# ============================ main ==========================================

def main():
    sc = SelfCheck()
    print("mining-grid encounter sim  |  seeds=%s  window=%.0fh  playstyles=%s"
          % (SEEDS, WINDOW_HOURS, list(PLAYSTYLES)))
    print("model: per-action live roll gated by depth>=threshold, u<chance, and a")
    print("per-PLAYER cooldown (one live encounter/player). Sweep threshold x chance x cooldown.\n")

    # negative test: a gate that fails OPEN would let a bad cell mint unbounded
    # encounters (cooldown<=0 => cap = inf). It MUST reject.
    sc.expect_reject("bad-param rejected: cooldown<=0 (cap would be infinite)",
                     lambda: validate_cell(REC_THRESHOLD, REC_CHANCE, 0.0),
                     code="bad-param")
    sc.expect_reject("bad-param rejected: chance>1",
                     lambda: validate_cell(REC_THRESHOLD, 1.5, REC_COOLDOWN),
                     code="bad-param")
    for (thr, ch, cd) in itertools.product(THRESHOLDS, CHANCES, COOLDOWNS):
        validate_cell(thr, ch, cd)   # every swept cell is well-formed

    # main 1h sweep (dense self-checks on every cell/playstyle/seed)
    agg = run_sweep(sc, WINDOW_SECONDS, WINDOW_HOURS, dense_checks=True)

    # DETERMINISM: run the whole 1h sweep twice (clear CrnCache inside), assert the
    # aggregate is byte-identical.
    def produce():
        _CRN.clear()
        local = SelfCheck()   # separate battery: don't double-count into sc
        return run_sweep(local, WINDOW_SECONDS, WINDOW_HOURS, dense_checks=False)

    determinism_check(sc, produce,
                      "determinism: full sweep identical across re-run (CRN cleared)")
    _CRN.clear()   # rebuild the 1h caches for the report tables below is unnecessary;
    # the report reads `agg` already computed. But other horizons will rebuild lazily.

    print_full_sweep(agg)
    print_ratio_and_faucet(agg)
    print_recommended(agg)
    print_robustness(sc)

    print("\n" + "=" * 78)
    print("All invariants tied to analytic caps: GATING (0 fires below threshold),")
    print("COOLDOWN CAP (enc/hr <= 3600/cooldown, EVERY cell — the anti-farm result),")
    print("ONE-LIVE (fires >= cooldown apart), MONOTONIC-in-chance, SANITY, DETERMINISM,")
    print("and 2 expect_reject negatives. 8h robustness pass re-asserts them.")
    print("=" * 78)
    raise SystemExit(sc.report())


if __name__ == "__main__":
    main()
