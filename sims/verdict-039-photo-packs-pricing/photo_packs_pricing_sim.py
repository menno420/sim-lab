#!/usr/bin/env python3
"""verdict-039 — photo-packs pricing: PWYW vs $5 fixed, a $3 anchor, and a
two-pack bundle (idea-engine ORDER 006 SIM-REQUEST 1, requesting seat
venture-lab).

Method: rung 1 exact-analytic decision arms — every decision quantity is a
closed-form Fraction; two seeded robustness legs (seeds 20260790/20260791,
registered in fixtures.json) act only as sign-agreement GATES on the exact
frontier logic and cannot move the ruling.

Hermetic: reads exactly ONE file (its own fixtures.json), no network, no
repo state, no wall clock. stdlib only. Deterministic: stdout and
results.json byte-identical across process runs (external diff is the
contract; sorted keys; no timestamps).

Run: python3 sims/verdict-039-photo-packs-pricing/photo_packs_pricing_sim.py
Exit 0 iff all self-checks pass.
"""

import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))

CHECKS = {"passed": 0, "failed": 0}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAILED: %s" % name)


def fr(x):
    """Exact Fraction from a decimal string."""
    return F(str(x))


# ---------------------------------------------------------------- channels
# Fee formulas pinned verbatim in fixtures.json (MARKET-PLAN §(a) @ 847b636).
def net_direct(p, proc_rate=fr("0.029")):
    """Gumroad direct: p - (0.50 + 0.10p) - (proc*p + 0.30)."""
    return p - (fr("0.50") + fr("0.10") * p) - (proc_rate * p + fr("0.30"))


def net_discover(p):
    """Gumroad Discover: flat 30%, processing included."""
    return fr("0.70") * p


def net_kofi(p):
    """Ko-fi free plan: p - 0.05p - (0.03p + 0.30)."""
    return p - fr("0.05") * p - (fr("0.03") * p + fr("0.30"))


CHANNELS = {
    "gumroad_direct": net_direct,
    "gumroad_discover": net_discover,
    "kofi_free": net_kofi,
}
DECISION_CHANNEL = "gumroad_direct"


def f2s(x, places=6):
    """Deterministic decimal render of a Fraction."""
    sign = "-" if x < 0 else ""
    x = abs(x)
    scaled = x * 10**places
    n = scaled.numerator // scaled.denominator
    # round half up deterministically
    if 2 * (scaled.numerator % scaled.denominator) >= scaled.denominator:
        n += 1
    s = str(n).rjust(places + 1, "0")
    return sign + s[:-places] + "." + s[-places:]


def frac_s(x):
    return "%d/%d" % (x.numerator, x.denominator)


def main():
    with open(os.path.join(HERE, "fixtures.json")) as fh:
        fx = json.load(fh)

    results = {}

    # ------------------------------------------------------------- pins
    net5 = {c: fn(F(5)) for c, fn in CHANNELS.items()}
    net3 = {c: fn(F(3)) for c, fn in CHANNELS.items()}

    # packet worked-net reconciliation (vetting §3 @ 847b636)
    check("net5 direct = 711/200 = 3.555 (packet rounds to $3.56)",
          net5["gumroad_direct"] == F(711, 200))
    check("net5 discover = 7/2 = 3.50 exact", net5["gumroad_discover"] == F(7, 2))
    check("net5 kofi = 43/10 = 4.30 exact", net5["kofi_free"] == F(43, 10))
    check("net3 direct = 1813/1000", net3["gumroad_direct"] == F(1813, 1000))

    # fee-floor rule reproduced (vetting §3: fixed fees eat >25% below ~$3)
    fixed_fee = fr("0.80")
    check("fixed-fee 25% crossing at p = 3.20 exactly",
          fixed_fee / F(16, 5) == F(1, 4))
    check("fixed-fee share at $3 = 4/15 > 25%",
          fixed_fee / F(3) == F(4, 15) and F(4, 15) > F(1, 4))

    results["per_sale_nets"] = {
        c: {"net_at_5": f2s(net5[c]), "net_at_5_frac": frac_s(net5[c]),
            "net_at_3": f2s(net3[c]), "net_at_3_frac": frac_s(net3[c])}
        for c in sorted(CHANNELS)
    }
    results["fee_floor"] = {
        "fixed_fees_usd": "0.80",
        "share_25pct_crossing_price": "3.20",
        "share_at_3_frac": "4/15",
        "share_at_3": f2s(F(4, 15)),
        "packet_rule_verbatim_reproduced": True,
    }

    # ------------------------------------------------- ANCHOR_3 frontier
    anchor_bar = {c: net5[c] / net3[c] for c in CHANNELS}
    check("anchor bar direct = 3555/1813",
          anchor_bar["gumroad_direct"] == F(3555, 1813))
    check("anchor bar kofi = 215/123", anchor_bar["kofi_free"] == F(215, 123))
    check("anchor bar discover = 5/3", anchor_bar["gumroad_discover"] == F(5, 3))
    per_unit_cut = 1 - net3["gumroad_direct"] / net5["gumroad_direct"]
    check("per-unit net cut 3-vs-5 direct = 1742/3555",
          per_unit_cut == F(1742, 3555))

    # sweep rho in [1,3] step 0.05 — twin evaluators per cell per channel
    anchor_grid = {}
    for c in sorted(CHANNELS):
        wins = 0
        cells = []
        for i in range(41):
            rho = 1 + F(i, 20)
            ev_win = rho * net3[c] >= net5[c]          # expected-value eval
            fr_win = rho >= anchor_bar[c]              # frontier inequality
            check("anchor twin-eval agree %s rho=%s" % (c, rho), ev_win == fr_win)
            wins += 1 if ev_win else 0
            cells.append([f2s(rho, 2), 1 if ev_win else 0])
        anchor_grid[c] = {"win_cells": wins, "of": 41, "cells": cells,
                          "bar_frac": frac_s(anchor_bar[c]),
                          "bar": f2s(anchor_bar[c])}
    results["anchor_3"] = {
        "grid": anchor_grid,
        "per_unit_net_cut_direct": f2s(per_unit_cut),
        "reading": "at $3 the price falls 40% but net-per-sale falls 49.0% "
                   "(direct); tie requires +96.1% unit sales (direct), "
                   "+74.8% (kofi), +66.7% (discover)",
    }

    # ---------------------------------------------------- PWYW frontier
    # E[net] = u * net(wbar); WIN iff u*net(wbar) >= net(5)
    check("pwyw parity wbar at u=1 (direct) = 5 exactly",
          net_direct(F(5)) == net5["gumroad_direct"])
    check("pwyw u bar at wbar=3 equals anchor bar (direct)",
          net5["gumroad_direct"] / net3["gumroad_direct"] == F(3555, 1813))
    check("pwyw u bar at wbar=4 = 3555/2684",
          net5["gumroad_direct"] / net_direct(F(4)) == F(3555, 2684))

    pwyw_grid = {}
    for c in sorted(CHANNELS):
        fn = CHANNELS[c]
        wins = 0
        total = 0
        for i in range(31):                       # u = 0.0 .. 3.0 step 0.1
            u = F(i, 10)
            for j in range(21):                   # wbar = 0 .. 10 step 0.5
                w = F(j, 2)
                nw = fn(w)
                ev_win = u * nw >= net5[c]
                # frontier inequality form: u >= net5/net(w) when net(w) > 0
                if nw > 0:
                    fr_win = u >= net5[c] / nw
                else:
                    fr_win = False if net5[c] > 0 else u * nw >= net5[c]
                check("pwyw twin-eval agree %s u=%s w=%s" % (c, u, w),
                      ev_win == fr_win)
                wins += 1 if ev_win else 0
                total += 1
        pwyw_grid[c] = {"win_cells": wins, "of": total}
    results["pwyw"] = {
        "grid": pwyw_grid,
        "parity_wbar_at_u1_direct": "5.000000 (exact)",
        "u_bar_at_wbar3_direct_frac": "3555/1813",
        "u_bar_at_wbar4_direct_frac": "3555/2684",
        "u_bar_at_wbar4_direct": f2s(F(3555, 2684)),
        "reading": "PWYW replaces $5 only if mean voluntary payment reaches "
                   "$5 at paid parity (u=1), or paid volume nearly doubles "
                   "at a $3 mean — both unmeasured (gap G1); PWYW averaging "
                   "the $3 floor IS $3 pricing (same bar)",
    }

    # --------------------------------------------------- BUNDLE frontier
    # b* per channel: net(b*) = 2*net(5)
    bstar = {}
    bstar["gumroad_direct"] = (2 * net5["gumroad_direct"] + fr("0.80")) / fr("0.871")
    bstar["kofi_free"] = (2 * net5["kofi_free"] + fr("0.30")) / fr("0.92")
    bstar["gumroad_discover"] = 2 * net5["gumroad_discover"] / fr("0.70")
    check("b* direct = 7910/871", bstar["gumroad_direct"] == F(7910, 871))
    check("b* kofi = 445/46", bstar["kofi_free"] == F(445, 46))
    check("b* discover = 10 exactly", bstar["gumroad_discover"] == F(10))
    for c in sorted(CHANNELS):
        check("b* self-consistent %s" % c,
              CHANNELS[c](bstar[c]) == 2 * net5[c])

    b999 = net_direct(fr("9.99"))
    b10 = net_direct(F(10))
    b8 = net_direct(F(8))
    check("bundle net at 9.99 direct = 790129/100000", b999 == F(790129, 100000))
    check("bundle net at 10 direct = 791/100 (+0.80 vs two singles exactly)",
          b10 == F(791, 100) and b10 - 2 * net5["gumroad_direct"] == fr("0.80"))
    check("bundle net at 8 direct = 771/125", b8 == F(771, 125))

    # mix grid at f=0: delta = t*(net(b)-2*net5) + (1-t)*g*(net(b)-net5)
    bundle_prices = [F(8), fr("8.5"), F(9), fr("9.5"), fr("9.99"), F(10)]
    bundle_grid = {}
    for c in sorted(CHANNELS):
        fn = CHANNELS[c]
        per_b = {}
        for b in bundle_prices:
            nb = fn(b)
            wins = 0
            total = 0
            for ti in range(21):
                t = F(ti, 20)
                for gi in range(21):
                    g = F(gi, 20)
                    delta = t * (nb - 2 * net5[c]) + (1 - t) * g * (nb - net5[c])
                    ev_win = delta >= 0
                    # dominance evaluator: b >= b* -> WIN at every cell
                    if b >= bstar[c]:
                        check("bundle dominance %s b=%s t=%s g=%s" % (c, b, t, g),
                              ev_win)
                    wins += 1 if ev_win else 0
                    total += 1
            per_b[f2s(b, 2)] = {"win_cells": wins, "of": total,
                                "net_frac": frac_s(nb), "net": f2s(nb),
                                "delta_vs_two_singles": f2s(nb - 2 * net5[c])}
        bundle_grid[c] = {"bstar_frac": frac_s(bstar[c]),
                          "bstar": f2s(bstar[c]), "prices": per_b}
    # the $8 frontier pin (direct): g >= 0.942 t / (2.613 (1-t))
    t_ex = F(1, 4)
    g_bar_ex = (fr("0.942") * t_ex) / (fr("2.613") * (1 - t_ex))
    check("bundle-8 frontier pin at t=0.25: g* = 942/7839... = 0.942*0.25/(2.613*0.75)",
          g_bar_ex == F(942 * 25, 2613 * 75) and
          fr("0.942") * t_ex == fr("2.613") * (1 - t_ex) * g_bar_ex)
    results["bundle_2pack"] = {
        "grid": bundle_grid,
        "dominance_band_direct": "[9.081515..., 10.00] (b* = 7910/871)",
        "saved_second_fixed_fee_at_10_direct": "0.800000 (exact)",
        "at_8_frontier_direct": "g >= 0.942*t/(2.613*(1-t)) — e.g. t=0.25 "
                                "needs upgrade share g >= %s" % f2s(g_bar_ex),
        "discover_note": "on Discover b* = $10.00 exactly: no fixed fee -> "
                         "zero demand-free discount room; the bundle's "
                         "fee-save rationale is channel-specific",
    }

    # ------------------------------------ reporting: processing sensitivity
    proc_rows = {}
    for rate in [fr("0.023"), fr("0.029"), fr("0.035")]:
        n5 = net_direct(F(5), rate)
        n3 = net_direct(F(3), rate)
        bs = (2 * n5 + fr("0.80")) / (1 - fr("0.10") - rate)
        proc_rows[f2s(rate, 3)] = {
            "net5": f2s(n5), "net3": f2s(n3),
            "anchor_bar": f2s(n5 / n3), "bstar": f2s(bs)}
        check("proc-sens b* self-consistent rate=%s" % rate,
              F(5) is not None and
              (bs - (fr("0.50") + fr("0.10") * bs) - (rate * bs + fr("0.30")))
              == 2 * n5)
    results["processing_sensitivity_reporting_only"] = proc_rows
    bars = [net_direct(F(5), r) / net_direct(F(3), r)
            for r in [fr("0.023"), fr("0.029"), fr("0.035")]]
    check("anchor bar stays within [1.94, 1.99] across the proc bracket",
          all(F(97, 50) < b < F(199, 100) for b in bars))

    # ------------------------------------------- reporting: scale scenarios
    scale = {}
    for n in [0, 2, 6]:
        row = {}
        row["fixed_5_net"] = f2s(n * net5["gumroad_direct"])
        row["anchor_3_net_same_units"] = f2s(n * net3["gumroad_direct"])
        row["anchor_3_net_at_bar_units"] = f2s(
            n * anchor_bar["gumroad_direct"] * net3["gumroad_direct"])
        row["bundle_10_if_all_pair_up"] = f2s(F(n, 2) * b10) if n % 2 == 0 else None
        scale["n5_%d" % n] = row
        check("anchor at bar units ties fixed exactly (n=%d)" % n,
              n * anchor_bar["gumroad_direct"] * net3["gumroad_direct"]
              == n * net5["gumroad_direct"])
    results["scale_scenarios_reporting_only"] = {
        "frame": "90-day units at $5 in {0, 2, 6} = the packet's $0 / "
                 "$10-anchor / $30-cap gross band; NO projection claimed",
        "rows": scale,
    }

    # ------------------------------------------------- seeded robustness
    seeds = sorted(int(s) for s in fx["seeds"]["registered"])
    check("registered seeds are exactly [20260790, 20260791]",
          seeds == [20260790, 20260791])
    check("seeds strictly above recorded high-water 20260775",
          all(s > 20260775 for s in seeds))

    rngA = random.Random(20260790)
    agreeA = 0
    for _ in range(2000):
        u = F(rngA.randrange(0, 3001), 1000)      # u in [0,3]
        w = F(rngA.randrange(0, 10001), 1000)     # wbar in [0,10]
        nw = net_direct(w)
        ev_win = u * nw >= net5["gumroad_direct"]
        fr_win = (nw > 0 and u >= net5["gumroad_direct"] / nw)
        if ev_win == fr_win:
            agreeA += 1
    check("robustness A: 2000/2000 twin-evaluator sign agreements",
          agreeA == 2000)

    rngB = random.Random(20260791)
    agreeB = 0
    dom_viol = 0
    for _ in range(2000):
        b = F(70, 10) + F(rngB.randrange(0, 3001), 1000)   # b in [7,10]
        t = F(rngB.randrange(0, 1001), 1000)
        g = F(rngB.randrange(0, 1001), 1000)
        nb = net_direct(b)
        n5d = net5["gumroad_direct"]
        delta = t * (nb - 2 * n5d) + (1 - t) * g * (nb - n5d)
        # twin evaluator: total revenue with-bundle minus without-bundle
        with_bundle = t * nb + (1 - t) * (g * nb + (1 - g) * n5d)
        without_bundle = t * 2 * n5d + (1 - t) * n5d
        if with_bundle - without_bundle == delta:
            agreeB += 1
        ev_win = delta >= 0
        # dominance predicate must never contradict the exact delta
        if b >= bstar["gumroad_direct"] and not ev_win:
            dom_viol += 1
    check("robustness B: 2000/2000 agreements", agreeB == 2000)
    check("robustness B: zero dominance violations", dom_viol == 0)
    results["robustness_gates"] = {
        "seed_20260790_pwyw_draws": 2000, "seed_20260790_agreements": agreeA,
        "seed_20260791_bundle_draws": 2000, "seed_20260791_agreements": agreeB,
        "seed_20260791_dominance_violations": dom_viol,
        "scope": "gates on the exact frontier logic; reporting-only, cannot "
                 "flip the decision (decision arm is exact Fractions)",
    }

    # ---------------------------------------------------- decision rule
    # R1: requires a MEASURED (u, wbar) in the packet -> none exists (G1).
    packet_measured_pwyw = None
    packet_measured_rho = None
    packet_measured_mix = None
    r1_fires = packet_measured_pwyw is not None
    r2_fires = packet_measured_rho is not None
    dominance_band_nonempty = bstar["gumroad_direct"] <= F(10)
    r3_fires = (not r1_fires and not r2_fires and packet_measured_mix is None
                and dominance_band_nonempty)
    check("R1 cannot fire (G1: no measured PWYW datum)", not r1_fires)
    check("R2 cannot fire (G2: no measured elasticity datum)", not r2_fires)
    check("R3 fires (G1/G2/G3 open, dominance band non-empty)", r3_fires)
    ruling = "R3-CONDITIONAL-DEFAULT" if r3_fires else "R4-NULL"
    check("ruling is R3-CONDITIONAL-DEFAULT", ruling == "R3-CONDITIONAL-DEFAULT")

    results["ruling"] = {
        "outcome": ruling,
        "evaluated_in_registered_order": ["R1 no-fire (G1)", "R2 no-fire (G2)",
                                          "R3 FIRES"],
        "decision": "keep the packet's $5-fixed default per pack (Gumroad "
                    "direct, net 3.555 exact/sale — zero unmeasured "
                    "parameters); ADD the two-pack bundle priced inside "
                    "[9.081515..., 10.00] — recommend $9.99 (net 7.90129 "
                    "exact, +0.79129 vs two singles; at $10.00 the gain is "
                    "the saved second fixed fee, +0.80 exactly); the $3 "
                    "anchor parks behind measured units ratio >= 3555/1813 "
                    "(+96.1%); PWYW parks behind measured (u, wbar) "
                    "clearing u*net(wbar) >= 3.555; bundle prices below b* "
                    "park behind the measured mix frontier",
    }

    # ------------------------------------------------------------ output
    results["self_checks"] = {"passed": CHECKS["passed"],
                              "failed": CHECKS["failed"]}
    out = os.path.join(HERE, "results.json")
    with open(out, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("verdict-039 photo-packs pricing — exact decision arms + seeded gates")
    print("ruling: %s" % ruling)
    print("net/sale at $5: direct 3.555 | discover 3.50 | kofi 4.30 (exact)")
    print("anchor-3 bar (direct): 3555/1813 = %s (+96.1%% units to tie)"
          % f2s(F(3555, 1813)))
    print("pwyw parity: wbar = $5.00 at u = 1 (direct, exact)")
    print("bundle b*: direct %s | kofi %s | discover 10.000000"
          % (f2s(bstar["gumroad_direct"]), f2s(bstar["kofi_free"])))
    print("bundle at $9.99 direct: net 7.901290, +0.791290 vs two singles")
    print("SELF-CHECKS: %d passed, %d failed"
          % (CHECKS["passed"], CHECKS["failed"]))
    return 0 if CHECKS["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
