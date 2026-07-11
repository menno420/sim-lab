#!/usr/bin/env python3
"""
robustness_wide.py
VERDICT 008 -- WIDER-VARIATION ROBUSTNESS PASS (empty-queue hardening addendum).

POST-VERDICT ROBUSTNESS APPENDIX. This does NOT re-open or change VERDICT 008
(finalized `needs-more-evidence`; the loot-VALUE half stays unsettled regardless).
It ONLY adversarially stress-tests the single load-bearing, analytic anti-farm
conclusion so the manager can see it survive WIDER variation than the base sweep:

  "The per-PLAYER cooldown analytically CAPS encounters at 3600/cooldown enc/hr for
   EVERYONE, including the optimal `!fastmine` grinder -- action rate cannot beat it,
   the grinder-vs-honest RATE ratio stays bounded, and reward-per-action collapses."

A robustness pass EARNS its keep only by trying to BREAK that claim. So this module
throws the nastiest adversaries at the RECOMMENDED default set (threshold=15,
chance=0.02, cooldown=600s) and a few neighboring cells, each seeded + multi-seed +
determinism-checked, and ASSERTS the cap still binds. If ANY variation made enc/hr
EXCEED 3600/cooldown, that would FLIP the conclusion and is reported as the headline
(structurally it must not: the cooldown gate is a hard floor on inter-fire spacing).

ADVERSARIAL VARIATIONS (each vs the analytic cap 3600/cooldown):
  1. EXTREME grinder cadence -- bot-speed action gaps 1.0s / 0.5s / 0.1s, parked deep.
     The key test: faster spam must NOT raise yield past the cap. Asserted on every seed.
  2. NON-PARKED grinder -- fastmine cadence but ROAMS depth (dips below threshold).
     Must yield <= the parked grinder (parking is optimal). Shares timing+roll stream
     with the parked grinder so the only difference is eligibility. Asserted per seed.
  3. BURST/BOUNDARY farmer -- the TIGHTEST adversary: fires as soon as the cooldown
     expires (times actions exactly on cooldown boundaries). It should APPROACH but
     never EXCEED the cap -- the ideal boundary farmer PINS to the cap (= the true
     worst-case grinder yield). A realistic bot-speed version sits just below. Asserted.
  4. AFK / bursty HONEST play -- honest deep-runner with random idle (AFK) gaps.
     enc/hr should DROP (fewer eligible actions), confirming honest players sit FURTHER
     below the cap. Asserted honest-AFK < cap and < the boundary farmer.
  5. WIDER param edges -- cooldown in {30,60,300,600,900,1800,3600}s x chance in
     {0.005,0.01,0.02,0.05,0.10,0.25,0.5} at threshold=15. The cap must hold across the
     WIDER grid; we report where the honest deep-runner crosses from "rare" (well below
     cap) to "cap-bound" (the chance ceiling beyond which even honest play saturates).

For each variation: enc/hr (mean +/- population sd over SEEDS), the analytic cap, the
grinder-vs-honest ratio, and rolls-per-encounter. DENSE self-checks (like the base sim):
cap holds on every cell/seed for every variation; boundary-farmer <= cap; non-parked <=
parked; honest-AFK < cap; determinism (whole pass run twice, identical). Ends on
`sys.exit(sc.report())` -- exit 0 iff clean.

RUN (from repo root; deterministic, stdlib-only):
  python3 sims/verdict-008-mining-grid-encounters/robustness_wide.py

REUSE: imports the SAME vendored helpers + model funcs from the base sim
(`mining_grid_encounter_sim`) via a sys.path insert on this file's own directory, so
there is exactly ONE model of record and this stays runnable standalone from repo root.
"""

import os
import random
import sys

# --- reuse the base sim's model + vendored harness helpers (one model of record) ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mining_grid_encounter_sim import (   # noqa: E402
    SEEDS, mean_sd, SelfCheck, determinism_check,
    simulate, analytic_cap_per_hour, validate_cell,
    trace, REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN, EPS,
    _CRN as BASE_CRN,
)

# ============================ config ========================================

WINDOW_HOURS = 1.0
WINDOW_SECONDS = WINDOW_HOURS * 3600.0

# recommended default set under stress (from the base sim / REPORT.md)
REC_CAP = analytic_cap_per_hour(REC_COOLDOWN)   # 6.00 enc/hr at cd=600s

# adversarial-trace seed offsets (kept clear of the base STYLE_OFFSETs 0/1e5/2e5)
OFF_U = 700000     # per-action roll stream (shared parked/non-parked)
OFF_D = 800000     # non-parked depth-roam stream
OFF_AFK = 900000   # honest-AFK stream

PARK = 30.0        # optimal park depth (>= every swept threshold -> always eligible)

# variation-1 bot-speed action gaps (seconds) and stress chances
EXTREME_GAPS = [1.0, 0.5, 0.1]
EXTREME_CHANCES = [REC_CHANCE, 0.10]

# variation-5 WIDER edges (threshold pinned at the recommended 15)
WIDE_COOLDOWNS = [30.0, 60.0, 300.0, 600.0, 900.0, 1800.0, 3600.0]
WIDE_CHANCES = [0.005, 0.01, 0.02, 0.05, 0.10, 0.25, 0.5]
SATURATE_FRAC = 0.90    # deep-runner "cap-bound" once enc/hr >= 0.90 * cap

# local CRN cache for the adversarial traces (base traces use BASE_CRN)
_ACRN = {}


def _cached(key, build):
    if key not in _ACRN:
        _ACRN[key] = build()
    return _ACRN[key]


# ============================ adversarial traces ============================
# Each returns a time-sorted list of (t, depth, u), matching the base model's
# schedule shape so the SAME `simulate()` runs them.

def extreme_grinder(seed, horizon, gap):
    """Bot-speed grinder: FIXED action gap, parked at the optimal depth, fresh
    seeded per-action roll. Faster `gap` => more rolls; the cap must still bind."""
    def build():
        rng = random.Random(seed + OFF_U + int(round(gap * 1000)))
        out, t = [], 0.0
        while t < horizon:
            out.append((t, int(PARK), rng.random()))
            t += gap
        return out
    return _cached(("extreme", seed, horizon, gap), build)


def grinder_pair(seed, horizon, gap=3.0):
    """(parked, non-parked) grinder pair sharing the SAME timing AND the SAME
    per-action roll stream -- the ONLY difference is depth eligibility. The parked
    grinder is eligible on every action (depth=PARK); the non-parked one roams and
    dips below threshold. Greedy-earliest firing on a superset of eligible actions
    can only fire >= as often, so non-parked <= parked (asserted per seed)."""
    def build():
        rng_u = random.Random(seed + OFF_U)
        rng_d = random.Random(seed + OFF_D)
        parked, nonparked = [], []
        t, d = 0.0, 20.0
        while t < horizon:
            u = rng_u.random()
            parked.append((t, int(PARK), u))
            # mean-revert around ~18 with noise + occasional shallow dip (< threshold)
            d += -0.2 * (d - 18.0) + rng_d.gauss(0.0, 4.0)
            if rng_d.random() < 0.10:
                d -= rng_d.uniform(6.0, 14.0)
            d = max(0.0, d)
            nonparked.append((t, int(d), u))
            t += gap
        return parked, nonparked
    return _cached(("pair", seed, horizon, gap), build)


def boundary_ideal(horizon, cooldown):
    """The TIGHTEST adversary, idealized: place an action exactly on every cooldown
    boundary with a guaranteed hit (u=0.0 < any chance>0). It fires at 0, cd, 2cd, ...
    -- one fire per cooldown -- so enc/hr == floor-of-the-cap == the cap itself. This
    is the true worst-case grinder yield; it APPROACHES the cap from below and, at
    exact boundary timing, EQUALS it. Seed-independent (hence sd=0)."""
    def build():
        out, t = [], 0.0
        while t < horizon:
            out.append((t, int(PARK), 0.0))
            t += cooldown
        return out
    return _cached(("boundary", horizon, cooldown), build)


def honest_afk(seed, horizon):
    """Honest deep-runner (parks ~22-38, ~12s cadence) BUT with random AFK idle
    bursts (60-600s) injected -- fewer actions => fewer eligible rolls => enc/hr
    DROPS, sitting further below the cap than the always-on deep-runner."""
    def build():
        rng = random.Random(seed + OFF_AFK)
        out, t, d = [], 0.0, 0.0
        target = rng.uniform(22.0, 38.0)
        while t < horizon:
            d += (target - d) * 0.05 + rng.gauss(0.0, 1.5)
            d = max(0.0, d)
            out.append((t, int(d), rng.random()))
            if rng.random() < 0.08:
                t += rng.uniform(60.0, 600.0)          # AFK idle burst
            else:
                t += max(1.0, rng.gauss(12.0, 2.0))    # normal ~12s cadence
        return out
    return _cached(("afk", seed, horizon), build)


# ============================ metric helper =================================

def enc_hr(schedule, threshold, chance, cooldown, hours=WINDOW_HOURS):
    """(result-dict, enc/hr, rolls-per-encounter) for one schedule at one cell."""
    r = simulate(schedule, threshold, chance, cooldown)
    per_hr = r["encounters"] / hours
    rpe = r["eligible"] / max(r["encounters"], 1)
    return r, per_hr, rpe


def _cap_ok(per_hr, cooldown):
    return per_hr <= analytic_cap_per_hour(cooldown) + EPS


# ============================ compute (pure) ================================
# compute() returns a results dict and runs NO self-checks (so it can be called
# twice for the determinism check). It clears BOTH CRN caches on entry so a re-run
# rebuilds every trace from seed.

def compute():
    BASE_CRN.clear()
    _ACRN.clear()
    hz, hrs = WINDOW_SECONDS, WINDOW_HOURS
    thr, cd = REC_THRESHOLD, REC_COOLDOWN

    res = {}

    # honest reference at the recommended set (base deep-runner) -- used for ratios
    href = [enc_hr(trace("deep-runner", s, hz), thr, REC_CHANCE, cd, hrs)[1]
            for s in SEEDS]
    res["honest_ref"] = mean_sd(href)

    # --- variation 1: EXTREME bot-speed cadence -------------------------------
    v1 = {}
    for gap in EXTREME_GAPS:
        for ch in EXTREME_CHANCES:
            per, rpe = [], []
            for s in SEEDS:
                _, h, r = enc_hr(extreme_grinder(s, hz, gap), thr, ch, cd, hrs)
                per.append(h)
                rpe.append(r)
            v1[(gap, ch)] = {"per": per, "enc_hr": mean_sd(per), "rpe": mean_sd(rpe)}
    res["v1"] = v1

    # --- variation 2: NON-PARKED vs PARKED grinder (same rolls) ---------------
    v2 = {}
    for ch in (REC_CHANCE, 0.10):
        pk, npk, pairs = [], [], []
        for s in SEEDS:
            p_sched, n_sched = grinder_pair(s, hz, gap=3.0)
            _, ph, _ = enc_hr(p_sched, thr, ch, cd, hrs)
            _, nh, _ = enc_hr(n_sched, thr, ch, cd, hrs)
            pk.append(ph)
            npk.append(nh)
            pairs.append((ph, nh))
        v2[ch] = {"parked": mean_sd(pk), "nonparked": mean_sd(npk), "pairs": pairs}
    res["v2"] = v2

    # --- variation 3: BOUNDARY / burst farmer (the tightest) ------------------
    # ideal (u=0, exact boundaries) pins to the cap; realistic = bot-speed 0.1s.
    _, bi_h, _ = enc_hr(boundary_ideal(hz, cd), thr, REC_CHANCE, cd, hrs)
    br = [enc_hr(extreme_grinder(s, hz, 0.1), thr, REC_CHANCE, cd, hrs)[1]
          for s in SEEDS]
    # also the ideal across the wider cooldowns (worst case per cooldown = the cap)
    bi_wide = {}
    for c in WIDE_COOLDOWNS:
        _, h, _ = enc_hr(boundary_ideal(hz, c), REC_THRESHOLD, REC_CHANCE, c, hrs)
        bi_wide[c] = (h, analytic_cap_per_hour(c))
    res["v3"] = {"ideal": bi_h, "cap": REC_CAP,
                 "realistic": mean_sd(br), "realistic_per": br,
                 "ideal_wide": bi_wide}

    # --- variation 4: AFK honest play -----------------------------------------
    afk, afk_rpe, deep = [], [], []
    for s in SEEDS:
        _, ah, ar = enc_hr(honest_afk(s, hz), thr, REC_CHANCE, cd, hrs)
        afk.append(ah)
        afk_rpe.append(ar)
        _, dh, _ = enc_hr(trace("deep-runner", s, hz), thr, REC_CHANCE, cd, hrs)
        deep.append(dh)
    res["v4"] = {"afk": mean_sd(afk), "afk_per": afk, "afk_rpe": mean_sd(afk_rpe),
                 "deep": mean_sd(deep), "boundary_ideal": bi_h}

    # --- variation 5: WIDER param edges (threshold=15) ------------------------
    # per (cooldown, chance): enc/hr per playstyle (casual/deep-runner/fastmine),
    # cap, and per-seed lists for the cap assertion.
    grid = {}
    for c in WIDE_COOLDOWNS:
        for ch in WIDE_CHANCES:
            row = {"cap": analytic_cap_per_hour(c)}
            for ps in ("casual", "deep-runner", "fastmine"):
                per = [enc_hr(trace(ps, s, hz), REC_THRESHOLD, ch, c, hrs)[1]
                       for s in SEEDS]
                row[ps] = {"per": per, "enc_hr": mean_sd(per)}
            grid[(c, ch)] = row
    # chance ceiling per cooldown: first chance where deep-runner mean >= frac*cap
    ceilings = {}
    for c in WIDE_COOLDOWNS:
        cap = analytic_cap_per_hour(c)
        ceil_ch = None
        for ch in WIDE_CHANCES:
            if grid[(c, ch)]["deep-runner"]["enc_hr"][0] >= SATURATE_FRAC * cap:
                ceil_ch = ch
                break
        ceilings[c] = ceil_ch
    res["v5"] = {"grid": grid, "ceilings": ceilings}

    return res


# ============================ self-checks ===================================

def run_checks(sc, res):
    hz, hrs = WINDOW_SECONDS, WINDOW_HOURS
    cd = REC_COOLDOWN

    # V1: bot-speed cadence -- cap binds on every gap/chance/seed; faster != higher.
    for gap in EXTREME_GAPS:
        for ch in EXTREME_CHANCES:
            for i, s in enumerate(SEEDS):
                h = res["v1"][(gap, ch)]["per"][i]
                sc.check(_cap_ok(h, cd),
                         "V1 cap: extreme gap=%.1fs ch=%.2f enc/hr %.4f <= %.4f (s=%d)"
                         % (gap, ch, h, REC_CAP, s))
    # faster spam does not raise the mean above the 3s baseline cap-bound plateau
    for ch in EXTREME_CHANCES:
        fastest = res["v1"][(0.1, ch)]["enc_hr"][0]
        sc.check(fastest <= REC_CAP + EPS,
                 "V1 plateau: fastest 0.1s grinder ch=%.2f mean %.4f <= cap %.4f"
                 % (ch, fastest, REC_CAP))

    # V2: non-parked <= parked on every seed (parking is optimal); both <= cap.
    for ch, d in res["v2"].items():
        for (ph, nh) in d["pairs"]:
            sc.check(nh <= ph + EPS,
                     "V2 non-parked <= parked: ch=%.2f nonparked %.4f <= parked %.4f"
                     % (ch, nh, ph))
            sc.check(_cap_ok(ph, cd) and _cap_ok(nh, cd),
                     "V2 cap: ch=%.2f parked %.4f & non-parked %.4f <= cap %.4f"
                     % (ch, ph, nh, REC_CAP))

    # V3: boundary farmer <= cap ALWAYS (ideal pins to it, never exceeds); realistic
    # sits at/under the cap on every seed.
    v3 = res["v3"]
    sc.check(v3["ideal"] <= REC_CAP + EPS,
             "V3 boundary-ideal <= cap: %.4f <= %.4f" % (v3["ideal"], REC_CAP))
    sc.check(v3["ideal"] >= REC_CAP - EPS,
             "V3 boundary-ideal PINS to cap (worst case = the cap): %.4f ~= %.4f"
             % (v3["ideal"], REC_CAP))
    for i, s in enumerate(SEEDS):
        h = v3["realistic_per"][i]
        sc.check(_cap_ok(h, cd),
                 "V3 realistic boundary (0.1s) enc/hr %.4f <= cap %.4f (s=%d)"
                 % (h, REC_CAP, s))
    for c, (h, cap) in v3["ideal_wide"].items():
        sc.check(h <= cap + EPS,
                 "V3 boundary-ideal <= cap across wider cd=%.0fs: %.4f <= %.4f"
                 % (c, h, cap))

    # V4: honest-AFK < cap on every seed, and AFK mean < the boundary farmer;
    # AFK also <= the always-on deep-runner (AFK only removes action time).
    v4 = res["v4"]
    for i, s in enumerate(SEEDS):
        h = v4["afk_per"][i]
        sc.check(h < REC_CAP - EPS,
                 "V4 honest-AFK strictly below cap: enc/hr %.4f < cap %.4f (s=%d)"
                 % (h, REC_CAP, s))
    sc.check(v4["afk"][0] < v4["boundary_ideal"] - EPS,
             "V4 honest-AFK mean %.4f < boundary farmer %.4f"
             % (v4["afk"][0], v4["boundary_ideal"]))
    sc.check(v4["afk"][0] <= v4["deep"][0] + EPS,
             "V4 honest-AFK mean %.4f <= always-on deep-runner %.4f (AFK drops yield)"
             % (v4["afk"][0], v4["deep"][0]))

    # V5: the cap holds on EVERY wider cell / playstyle / seed.
    for (c, ch), row in res["v5"]["grid"].items():
        cap = row["cap"]
        for ps in ("casual", "deep-runner", "fastmine"):
            for i, s in enumerate(SEEDS):
                h = row[ps]["per"][i]
                sc.check(h <= cap + EPS,
                         "V5 cap: cd=%.0fs ch=%.3f %s enc/hr %.4f <= %.4f (s=%d)"
                         % (c, ch, ps, h, cap, s))

    # parameter validators still reject the degenerate cells (cap would be infinite).
    sc.expect_reject("V-neg: cooldown<=0 rejected (cap would be infinite)",
                     lambda: validate_cell(REC_THRESHOLD, REC_CHANCE, 0.0),
                     code="bad-param")
    sc.expect_reject("V-neg: chance>1 rejected",
                     lambda: validate_cell(REC_THRESHOLD, 1.5, REC_COOLDOWN),
                     code="bad-param")


# ============================ determinism canon =============================

def _canon(res):
    """Flatten res into a comparison-stable tuple (whole pass identical on re-run)."""
    def ms(x):
        return (round(x[0], 9), round(x[1], 9))
    out = []
    out.append(("href", ms(res["honest_ref"])))
    out.append(("v1", tuple(sorted(
        (k, tuple(round(v, 9) for v in d["per"])) for k, d in res["v1"].items()))))
    out.append(("v2", tuple(sorted(
        (k, tuple((round(a, 9), round(b, 9)) for a, b in d["pairs"]))
        for k, d in res["v2"].items()))))
    out.append(("v3", (round(res["v3"]["ideal"], 9),
                       tuple(round(v, 9) for v in res["v3"]["realistic_per"]),
                       tuple(sorted((k, round(v[0], 9))
                                    for k, v in res["v3"]["ideal_wide"].items())))))
    out.append(("v4", (tuple(round(v, 9) for v in res["v4"]["afk_per"]),
                       ms(res["v4"]["deep"]))))
    out.append(("v5", tuple(sorted(
        (k, tuple(tuple(round(v, 9) for v in row[ps]["per"])
                  for ps in ("casual", "deep-runner", "fastmine")))
        for k, row in res["v5"]["grid"].items()))))
    return tuple(out)


# ============================ reporting =====================================

def print_report(res):
    bar = "=" * 78
    print(bar)
    print("WIDER-VARIATION ROBUSTNESS  |  seeds=%s  window=%.0fh" % (SEEDS, WINDOW_HOURS))
    print("Stressing recommended default set: threshold=%d, chance=%.2f, cooldown=%.0fs"
          % (REC_THRESHOLD, REC_CHANCE, REC_COOLDOWN))
    print("Analytic cap at cd=%.0fs = %.2f enc/hr. honest deep-runner ref = %.2f +/- %.2f/hr."
          % (REC_COOLDOWN, REC_CAP, res["honest_ref"][0], res["honest_ref"][1]))
    print("The single load-bearing claim under stress: enc/hr <= 3600/cooldown for ALL.")
    print(bar)

    # V1
    print("\n[1] EXTREME BOT-SPEED CADENCE (parked grinder; faster spam must NOT beat cap)")
    print("    gap(s) chance  enc/hr(mean+/-sd)  rolls/enc(mean)  cap    <=cap?")
    for gap in EXTREME_GAPS:
        for ch in EXTREME_CHANCES:
            m, s = res["v1"][(gap, ch)]["enc_hr"]
            rpe = res["v1"][(gap, ch)]["rpe"][0]
            ok = "yes" if m <= REC_CAP + EPS else "NO!!"
            print("    %5.1f  %5.2f   %6.2f +/- %4.2f     %9.1f     %5.2f  %s"
                  % (gap, ch, m, s, rpe, REC_CAP, ok))
    print("    -> faster mining does not raise yield; the cooldown floor caps it.")

    # V2
    print("\n[2] NON-PARKED vs PARKED GRINDER (same rolls; parking is optimal)")
    print("    chance  parked/hr        non-parked/hr    non-parked<=parked?")
    for ch in (REC_CHANCE, 0.10):
        d = res["v2"][ch]
        pm, ps_ = d["parked"]
        nm, ns = d["nonparked"]
        ok = "yes" if all(nh <= ph + EPS for ph, nh in d["pairs"]) else "NO!!"
        print("    %5.2f   %5.2f +/- %4.2f   %5.2f +/- %4.2f   %s"
              % (ch, pm, ps_, nm, ns, ok))
    print("    -> roaming off the optimal depth only LOSES yield; parking is the ceiling.")

    # V3
    v3 = res["v3"]
    close = v3["realistic"][0] / REC_CAP
    print("\n[3] BOUNDARY / BURST FARMER (the TIGHTEST adversary: fire on each cd boundary)")
    print("    ideal boundary farmer (exact boundaries, guaranteed hit): %.4f enc/hr"
          % v3["ideal"])
    print("    analytic cap                                             : %.4f enc/hr"
          % REC_CAP)
    print("    => the worst-case grinder yield PINS to the cap (ratio %.4f); never exceeds."
          % (v3["ideal"] / REC_CAP))
    print("    realistic bot-speed (0.1s) boundary farmer @ ch=%.2f     : %.2f +/- %.2f/hr"
          % (REC_CHANCE, v3["realistic"][0], v3["realistic"][1]))
    print("    => reaches %.1f%% of the cap at the recommended chance and STOPS there --"
          % (100.0 * close))
    print("       bot-speed saturates the cooldown floor but cannot punch through it.")
    print("    ideal boundary farmer vs cap across the WIDER cooldown edges:")
    print("      cd(s)   ideal/hr   cap/hr   <=cap?")
    for c in WIDE_COOLDOWNS:
        h, cap = v3["ideal_wide"][c]
        ok = "yes" if h <= cap + EPS else "NO!!"
        print("      %5.0f   %8.3f  %7.3f   %s" % (c, h, cap, ok))

    # V4
    v4 = res["v4"]
    print("\n[4] AFK / BURSTY HONEST PLAY (deep-runner with random idle gaps)")
    print("    honest-AFK enc/hr        : %.2f +/- %.2f  (rolls/enc %.1f)"
          % (v4["afk"][0], v4["afk"][1], v4["afk_rpe"][0]))
    print("    always-on deep-runner/hr : %.2f +/- %.2f" % (v4["deep"][0], v4["deep"][1]))
    print("    boundary farmer /hr      : %.2f   ;   cap %.2f" % (v4["boundary_ideal"], REC_CAP))
    print("    -> AFK DROPS honest yield (fewer eligible actions); honest sits FURTHER")
    print("       below the cap and below the boundary farmer -- honest never saturates.")

    # V5
    print("\n[5] WIDER PARAM EDGES (threshold=%d): enc/hr(deep-runner mean) vs cap, cap must hold"
          % REC_THRESHOLD)
    header = "    cd(s)\\chance " + "".join("%8.3f" % c for c in WIDE_CHANCES) + "   cap"
    print(header)
    for c in WIDE_COOLDOWNS:
        cells = []
        for ch in WIDE_CHANCES:
            cells.append("%8.2f" % res["v5"]["grid"][(c, ch)]["deep-runner"]["enc_hr"][0])
        print("    %8.0f  " % c + "".join(cells) + "  %6.2f" % analytic_cap_per_hour(c))
    print("\n    CHANCE CEILING -- smallest chance where the honest deep-runner reaches")
    print("    >= %.0f%% of the cap (crosses from 'rare' to 'cap-bound' / saturating):" % (100 * SATURATE_FRAC))
    print("      cd(s)   cap/hr   chance-ceiling(honest saturates)")
    for c in WIDE_COOLDOWNS:
        ch = res["v5"]["ceilings"][c]
        cap = analytic_cap_per_hour(c)
        txt = ("%.3f" % ch) if ch is not None else ">%.2f (never within grid)" % WIDE_CHANCES[-1]
        print("      %5.0f   %6.2f   %s" % (c, cap, txt))
    rec_ceiling = res["v5"]["ceilings"][REC_COOLDOWN]
    rc = ("%.3f" % rec_ceiling) if rec_ceiling is not None else ">0.5"
    print("    -> at the recommended cooldown=%.0fs the honest deep-runner only becomes"
          % REC_COOLDOWN)
    print("       cap-bound at chance ~ %s; the recommended chance %.2f keeps honest play"
          % (rc, REC_CHANCE))
    print("       WELL below the cap (rare-but-present), while the cap holds everywhere.")


# ============================ main ==========================================

def main():
    sc = SelfCheck()
    print("VERDICT 008 -- WIDER-VARIATION ROBUSTNESS (empty-queue hardening addendum)")
    print("POST-VERDICT: verdict UNCHANGED (needs-more-evidence); this only HARDENS the")
    print("analytic anti-farm cap against wider adversarial variation. Base sim untouched.\n")

    res = compute()
    run_checks(sc, res)

    # determinism: run the whole pass twice (both CRN caches cleared inside), assert
    # the flattened results are byte-identical.
    determinism_check(sc, lambda: _canon(compute()),
                      "determinism: whole robustness pass identical across re-run")
    # rebuild caches for the (already-computed) report tables below
    _ = compute()

    print_report(res)

    print("\n" + "=" * 78)
    print("SELF-CHECKS tie every variation to the analytic cap: V1 bot-speed cadence,")
    print("V2 non-parked<=parked, V3 boundary-farmer<=cap (pins to it), V4 honest-AFK<cap,")
    print("V5 cap holds across the WIDER cd x chance grid -- plus determinism + 2 negatives.")
    print("=" * 78)
    raise SystemExit(sc.report())


if __name__ == "__main__":
    main()
