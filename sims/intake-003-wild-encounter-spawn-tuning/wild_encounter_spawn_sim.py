#!/usr/bin/env python3
"""
wild_encounter_spawn_sim.py
INTAKE 003 / idea-engine PROPOSAL 003 (2026-07-10T20:10:06Z) — wild-encounter
activity-spawning tuning sweep.

Canonical idea: menno420/superbot docs/ideas/wild-encounters-activity-spawning-2026-06-20.md
@ fd638e3c0693687a62093aa6bd75954e238fa58d (pinned).

WHAT THIS SETTLES
  Which (spawn threshold, debounce window, per-claimer cooldown) sets, together with the
  one-live-spawn-per-channel guardrail, keep encounter spawns "rare-but-visible" across
  low/med/high traffic tiers while making paced-spam farming yield no edge over honest play.

WHAT IT DOES NOT SETTLE (declared, not hidden)
  Reward inflation vs. fishing/mining earn rates. No live earn-rate baseline exists in the
  source docs (fishing v1 shipped superbot #1033-#1041 with no published rate). This sim
  reports only the ABSOLUTE encounter mint rate (claims/day/channel); the ratio to
  fishing/mining is unmeasurable here -> see the report LIMITS + the named telemetry.

RUN (one documented command, deterministic, stdlib-only):
  python3 sims/intake-003-wild-encounter-spawn-tuning/wild_encounter_spawn_sim.py

  Exit 0 iff every self-check passes (the checks tie the simulated numbers to the analytic
  caps -> a bug that inflates spawns/claims trips an assertion and exits nonzero).

MODEL (single channel, discrete-event)
  - Honest messages: Poisson arrivals at a per-tier rate (EST), author uniform over N_users
    (EST). One honest trace per (tier, seed) is REUSED across every parameter set (common
    random numbers -> a fair, variance-reduced comparison across the sweep).
  - Debounced counter: a message increments the counter only if it lands >= debounce seconds
    after the previous COUNTED message. The counter accrues ONLY while no spawn is live (the
    conservative "no banking during a live spawn" design; the accrue-during-live variant is a
    stated LIMIT, not modeled).
  - At counter == threshold a spawn goes live (embed + Claim button); counter resets to 0.
  - ONE LIVE SPAWN PER CHANNEL: no new spawn accrues while one is live.
  - CLAIM: the first later message whose author is off per-claimer cooldown claims the live
    spawn (models "an active user clicks Claim"); that author goes on cooldown for `cooldown`
    seconds; the spawn clears and accrual resumes. Unclaimed spawns expire after SPAWN_TTL.
  - Adversarial FARMER (author id -1): a single account paced at a chosen inter-message gap,
    optionally amid honest high traffic, claiming every spawn its cooldown permits.

SEEDS: 5 fixed seeds; each headline metric is mean +/- population stdev across seeds.
No Date.now()/random-without-seed anywhere; PYTHONHASHSEED is never relied on (no hash()).
"""

import random
import statistics
from collections import defaultdict

# ----------------------------------------------------------------------------- config
SEEDS = [11, 23, 42, 101, 2027]
SIM_HOURS = 8.0
SIM_SECONDS = SIM_HOURS * 3600.0
SPAWN_TTL = 300.0            # seconds an unclaimed spawn stays live (EST)
FARMER = -1

# Traffic tiers: name -> (honest messages per minute [EST], N honest users [EST])
TIERS = {
    "low":  (0.5, 3),
    "med":  (3.0, 8),
    "high": (15.0, 25),
}
TIER_OFFSET = {"low": 0, "med": 1000, "high": 2000}   # deterministic per-tier seed offset

# sweep grids
THRESHOLDS = [12, 24, 36, 48]                 # debounced messages to trigger a spawn
DEBOUNCES  = [5.0, 10.0, 20.0, 30.0, 60.0]    # seconds
COOLDOWNS  = [60.0, 300.0, 900.0, 1800.0]     # seconds

# recommended defaults (justified in the report; printed with analytic caps for audit)
REC_THRESHOLD = 24
REC_DEBOUNCE  = 30.0
REC_COOLDOWN  = 900.0


# ----------------------------------------------------------------------------- traces
def gen_honest_messages(rng, rate_per_min, n_users, horizon):
    """Poisson arrivals; author uniform in [0, n_users). Returns time-sorted [(t, author)]."""
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


# ----------------------------------------------------------------------------- core sim
def simulate(messages, threshold, debounce, cooldown, horizon):
    """One deterministic pass over time-sorted messages."""
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
        if live and t > live_until:          # lazily expire an unclaimed spawn
            live = False
            unclaimed_expired += 1
        if not live:                         # accrue toward the next spawn
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
        else:                                # a spawn is live -> this message may claim it
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


def analytic_spawn_cap_per_hour(threshold, debounce):
    """Traffic-independent ceiling: >= (threshold-1)*debounce seconds between spawns."""
    return 3600.0 / ((threshold - 1) * debounce)


def analytic_farmer_claim_cap_per_hour(threshold, debounce, cooldown):
    """Farmer claims are bounded by BOTH the spawn ceiling and the per-claimer cooldown."""
    return min(analytic_spawn_cap_per_hour(threshold, debounce), 3600.0 / cooldown)


def mean_sd(xs):
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


# ----------------------------------------------------------------------------- caches
_HONEST_CACHE = {}
def honest_trace(tier, seed):
    key = (tier, seed)
    if key not in _HONEST_CACHE:
        rate, n_users = TIERS[tier]
        rng = random.Random(seed + TIER_OFFSET[tier])
        _HONEST_CACHE[key] = gen_honest_messages(rng, rate, n_users, SIM_SECONDS)
    return _HONEST_CACHE[key]


# ----------------------------------------------------------------------------- self-checks
_CHECKS = {"pass": 0, "detail": []}
def _check(cond, label):
    _CHECKS["detail"].append((bool(cond), label))
    if cond:
        _CHECKS["pass"] += 1
    else:
        raise AssertionError("SELF-CHECK FAILED: " + label)


# ----------------------------------------------------------------------------- experiments
def visibility_sweep():
    """spawns/hr and messages/spawn per tier per (threshold, debounce), meaned over seeds.
    Cooldown fixed at 300s; spawn count has only a mild second-order dependence on cooldown
    (via when a claim clears the live spawn and lets accrual resume) -- disclosed in the
    report, not asserted invariant."""
    print("=" * 78)
    print("VISIBILITY SWEEP  -  spawns/hour (mean over %d seeds), one channel, %.0fh window"
          % (len(SEEDS), SIM_HOURS))
    print("Ceiling = analytic traffic-independent cap 3600/((thr-1)*deb). Cooldown fixed 300s.")
    print("=" * 78)
    results = {}
    for tier in ("low", "med", "high"):
        rate, n_users = TIERS[tier]
        print("\n[%s tier]  honest ~%.1f msg/min, %d users" % (tier, rate, n_users))
        header = "  thr\\deb " + "".join("%9.0f" % d for d in DEBOUNCES)
        print(header)
        for thr in THRESHOLDS:
            row = []
            for deb in DEBOUNCES:
                per_seed = []
                for seed in SEEDS:
                    r = simulate(honest_trace(tier, seed), thr, deb, 300.0, SIM_SECONDS)
                    per_seed.append(r["spawns"] / SIM_HOURS)
                    # simulated spawn rate must not exceed the analytic traffic-independent ceiling
                    _check(r["spawns"] <= SIM_SECONDS / ((thr - 1) * deb) + 2,
                           "spawns <= analytic ceiling (%s thr=%d deb=%.0f)" % (tier, thr, deb))
                    _check(r["max_counter"] <= thr, "counter never exceeds threshold")
                    _check(r["claims"] <= r["spawns"], "claims <= spawns")
                    results[(tier, thr, deb)] = mean_sd(per_seed)
                m, s = results[(tier, thr, deb)]
                row.append("%6.2f" % m)
            print(("  thr=%-4d" % thr) + " " + "   ".join(row))
        # messages/spawn for the same grid (visibility as effort-per-spawn)
        print("  messages/spawn (mean; blank if 0 spawns):")
        for thr in THRESHOLDS:
            cells = []
            for deb in DEBOUNCES:
                sp = []
                for seed in SEEDS:
                    r = simulate(honest_trace(tier, seed), thr, deb, 300.0, SIM_SECONDS)
                    total_msgs = len(honest_trace(tier, seed))
                    sp.append((total_msgs / r["spawns"]) if r["spawns"] else float("nan"))
                vals = [x for x in sp if x == x]
                cells.append(("%8.0f" % (sum(vals) / len(vals))) if vals else "     -- ")
            print(("  thr=%-4d" % thr) + "".join(cells))
    return results


def antifarm_plateau():
    """Fixed recommended set; farmer paced from 4x-faster than debounce to 4x-slower.
    Shows claims/hr plateau + collapsing reward-per-message when spamming below debounce."""
    print("\n" + "=" * 78)
    print("ANTI-FARM  -  lone farmer, thr=%d deb=%.0f cd=%.0f  (recommended set)"
          % (REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN))
    print("Farmer claim ceiling (analytic) = %.2f/hr = min(spawn cap %.2f, cooldown cap %.2f)"
          % (analytic_farmer_claim_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN),
             analytic_spawn_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE),
             3600.0 / REC_COOLDOWN))
    print("=" * 78)
    print("  farmer_gap(s)   msgs_sent   claims/hr    reward_per_msg   (spam faster != more)")
    gaps = [REC_DEBOUNCE * m for m in (0.25, 0.5, 1.0, 2.0, 4.0)]
    for gap in gaps:
        cph, rpm, msent = [], [], []
        for seed in SEEDS:  # farmer trace is deterministic; seed only varies nothing here
            msgs = gen_farmer_messages(gap, SIM_SECONDS)
            r = simulate(msgs, REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN, SIM_SECONDS)
            fc = r["claims_by_user"].get(FARMER, 0)
            n = len(msgs)
            cph.append(fc / SIM_HOURS)
            rpm.append(fc / n if n else 0.0)
            msent.append(n)
            _check(fc / SIM_HOURS <=
                   analytic_farmer_claim_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN) + 0.5,
                   "farmer claims/hr <= analytic cap (gap=%.1f)" % gap)
        print("   %10.1f  %10d   %8.2f      %12.4f" %
              (gap, int(mean_sd(msent)[0]), mean_sd(cph)[0], mean_sd(rpm)[0]))
    print("  -> below debounce, extra messages are throttled: claims/hr flat, reward/msg falls.")


def antifarm_vs_honest():
    """Farmer amid honest HIGH traffic across the cooldown grid. Reports the farmer's claims/hr,
    total claims/hr, and the farmer's SHARE of all claims. The robust anti-farm result is the
    per-account cap = min(spawn ceiling, 3600/cooldown); in a busy channel honest regulars also
    out-race the farmer to the Claim button, so the farmer's share stays bounded."""
    print("\n" + "=" * 78)
    print("ANTI-FARM vs HONEST  -  farmer (gap=debounce) inside HIGH traffic, thr=%d deb=%.0f"
          % (REC_THRESHOLD, REC_DEBOUNCE))
    print("=" * 78)
    print("  cooldown(s)  farmer/hr  total/hr  farmer_share%  per-acct cap/hr (analytic)")
    for cd in COOLDOWNS:
        fr, tot, share = [], [], []
        for seed in SEEDS:
            msgs = gen_farmer_messages(REC_DEBOUNCE, SIM_SECONDS) + honest_trace("high", seed)
            r = simulate(msgs, REC_THRESHOLD, REC_DEBOUNCE, cd, SIM_SECONDS)
            fc = r["claims_by_user"].get(FARMER, 0)
            tc = r["claims"]
            fr.append(fc / SIM_HOURS)
            tot.append(tc / SIM_HOURS)
            share.append((fc / tc * 100.0) if tc else 0.0)
            cap = analytic_farmer_claim_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE, cd)
            _check(fc / SIM_HOURS <= cap + 0.5, "farmer claims/hr <= per-acct cap (cd=%.0f)" % cd)
        cap = analytic_farmer_claim_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE, cd)
        print("   %9.0f  %8.2f  %8.2f  %11.1f  %14.2f" %
              (cd, mean_sd(fr)[0], mean_sd(tot)[0], mean_sd(share)[0], cap))
    print("  -> fast spam is already worthless (see plateau); cooldown then caps & spreads claims.")


def recommended_headline():
    """The recommended set, printed per tier with mint proxy, plus farmer figures."""
    print("\n" + "=" * 78)
    print("RECOMMENDED DEFAULTS  ->  threshold=%d, debounce=%.0fs, cooldown=%.0fs"
          % (REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN))
    print("Analytic spawn ceiling %.2f/hr; farmer claim ceiling %.2f/hr (both traffic-independent)."
          % (analytic_spawn_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE),
             analytic_farmer_claim_cap_per_hour(REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN)))
    print("=" * 78)
    print("  tier   spawns/hr    claims/hr   unclaimed%%   claims/8h-window (mint proxy per channel)")
    for tier in ("low", "med", "high"):
        sp, cl, un, cw = [], [], [], []
        for seed in SEEDS:
            r = simulate(honest_trace(tier, seed), REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN, SIM_SECONDS)
            sp.append(r["spawns"] / SIM_HOURS)
            cl.append(r["claims"] / SIM_HOURS)
            un.append((r["unclaimed_expired"] / r["spawns"] * 100.0) if r["spawns"] else 0.0)
            cw.append(r["claims"])
        print("  %-5s   %7.2f    %8.2f    %8.1f    %12.1f" %
              (tier, mean_sd(sp)[0], mean_sd(cl)[0], mean_sd(un)[0], mean_sd(cw)[0]))
    # lone farmer at the recommended set
    fr = []
    for seed in SEEDS:
        msgs = gen_farmer_messages(REC_DEBOUNCE, SIM_SECONDS)
        r = simulate(msgs, REC_THRESHOLD, REC_DEBOUNCE, REC_COOLDOWN, SIM_SECONDS)
        fr.append(r["claims_by_user"].get(FARMER, 0) / SIM_HOURS)
    print("  lone farmer (optimal pacing): %.2f claims/hr for >=%d spam msgs/claim -> capped, no edge."
          % (mean_sd(fr)[0], REC_THRESHOLD))


def determinism_selftest():
    """Same seed twice -> identical results; ties the reproducibility gate to code."""
    a = simulate(honest_trace("med", 42), 24, 30.0, 900.0, SIM_SECONDS)
    _HONEST_CACHE.clear()
    b = simulate(honest_trace("med", 42), 24, 30.0, 900.0, SIM_SECONDS)
    _check(a == b, "determinism: identical results for identical seed")


def main():
    print("wild-encounter spawn-tuning sim  |  seeds=%s  window=%.0fh  ttl=%.0fs"
          % (SEEDS, SIM_HOURS, SPAWN_TTL))
    determinism_selftest()
    visibility_sweep()
    antifarm_plateau()
    antifarm_vs_honest()
    recommended_headline()
    print("\n" + "=" * 78)
    print("SELF-CHECKS: %d passed, 0 failed  (spawn/claim/farmer rates tied to analytic caps,"
          % _CHECKS["pass"])
    print("counter<=threshold, claims<=spawns, determinism). Exit 0.")
    print("=" * 78)


if __name__ == "__main__":
    main()
