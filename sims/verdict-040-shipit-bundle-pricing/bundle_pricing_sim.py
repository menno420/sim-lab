#!/usr/bin/env python3
"""VERDICT 040 — Ship-It Bundle pricing: $59 vs $64 vs $68 anchor points.

Exact-analytic pricing sim (rung 1). Every decision quantity is a closed-form
fractions.Fraction expected value on the pre-registered packet constants
(fixtures.json, committed before this runner). The ONE registered seed
(20260880) drives a VALIDATION-ONLY leg (twin-evaluator agreement on random
retention draws) that cannot flip the decision.

Hermetic: reads only its own fixtures.json; no network, no repo state, no
wall clock. stdout + results.json byte-identical across process runs.
"""

import json
import math
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
        print("SELF-CHECK FAIL: %s" % name)


def main():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)

    # ---- constants from the pre-registration ----------------------------
    fee = fx["pinned_constants"]["gumroad_fee_schedule"]["value"]
    a_rate = F(1) - F(fee["platform_rate"]) - F(fee["processing_rate"])   # 871/1000
    b_flat = F(fee["platform_flat_usd"]) + F(fee["processing_flat_usd"])  # 4/5
    check("fee multiplier is 871/1000", a_rate == F(871, 1000))
    check("fee flat is 4/5", b_flat == F(4, 5))

    comp = fx["pinned_constants"]["bundle_components"]["value"]
    kit = F(comp["membership_kit_usd"])
    pack = F(comp["template_pack_usd"])
    sep_total = F(comp["separate_total_usd"])
    check("components sum to the separate total ($49+$19=$68)", kit + pack == sep_total)

    committed = F(fx["pinned_constants"]["committed_bundle_price_usd"]["value"])
    check("committed bundle price is $59", committed == 59)
    floor = F(fx["pinned_constants"]["bundle_price_floor_coherence"]["value"])
    anchors = [F(59), F(64), F(68)]
    check("every anchor clears the $49 coherence floor", all(p >= floor for p in anchors))
    check("$64 anchor is flagged unsourced in the fixtures (gap G3)",
          "NOT MEASURED / NOT SOURCED" in fx["pinned_constants"]["anchor_64_provenance"]["finding"])

    def net(P):
        return a_rate * P - b_flat

    net59, net64, net68 = net(F(59)), net(F(64)), net(F(68))
    # two separate transactions at suggested $19 paid
    net_separate = net(kit) + net(pack)
    net_kit_alone = net(kit)

    exp = fx["expected_exact_values_hand_derived"]
    check("net(59) hand pin", net59 == F(50589, 1000))
    check("net(64) hand pin", net64 == F(54944, 1000))
    check("net(68) hand pin", net68 == F(58428, 1000))
    check("separate-both hand pin", net_separate == F(57628, 1000))
    check("kit-alone hand pin", net_kit_alone == F(41879, 1000))
    check("bundle@68 saves exactly one fixed fee vs separate", net68 - net_separate == F(4, 5))
    check("seller cost of the $9 nudge", net_separate - net59 == F(7039, 1000))
    check("per-sale net ordering is monotone in price", net59 < net64 < net68)
    check("margin ladder (G6 reporting)", net_kit_alone < net59 < net64 < net_separate < net68)

    # ---- retention frontiers r*(hi vs lo) = net(lo)/net(hi) -------------
    r64v59 = net59 / net64
    r68v59 = net59 / net68
    r68v64 = net64 / net68
    check("frontier 64v59 hand pin", r64v59 == F(50589, 54944))
    check("frontier 68v59 hand pin", r68v59 == F(5621, 6492))
    check("frontier 68v64 hand pin", r68v64 == F(13736, 14607))
    check("uplift frame 59-vs-64 is the reciprocal", (net64 / net59) == F(54944, 50589))
    check("uplift frame 59-vs-68 is the reciprocal", (net68 / net59) == F(58428, 50589))

    # fee-free bounds (reporting-only sensitivity, gap G4)
    ff64v59, ff68v59, ff68v64 = F(59, 64), F(59, 68), F(16, 17)
    for nm, cited, free in (("64v59", r64v59, ff64v59), ("68v59", r68v59, ff68v59), ("68v64", r68v64, ff68v64)):
        check("fee-free bound brackets cited frontier within 0.19 pp (%s)" % nm,
              abs(cited - free) < F(19, 10000))
        check("cited frontier sits BELOW the fee-free bound (%s) — flat fee favors the higher price" % nm,
              cited < free)

    # buyer savings by anchor vs the committed copy claim
    savings = {"59": sep_total - F(59), "64": sep_total - F(64), "68": sep_total - F(68)}
    check("buyer saves $9 at $59 (committed copy TRUE)", savings["59"] == 9)
    check("buyer saves $4 at $64 (committed 'saves $9' copy FALSE)", savings["64"] == 4)
    check("buyer saves $0 at $68 (committed 'saves $9' copy FALSE, rationale void)", savings["68"] == 0)

    # materiality bound at the packet's own 0-2 sales/month
    mat_68 = 2 * (net68 - net59)
    mat_64 = 2 * (net64 - net59)
    check("materiality bound 59-vs-68 hand pin", mat_68 == F(15678, 1000))
    check("materiality bound 59-vs-64 hand pin", mat_64 == F(8710, 1000))

    # ---- twin evaluators -------------------------------------------------
    # Evaluator T1: direct expected-net product comparison (Fraction).
    def t1_hi_wins(r, net_hi, net_lo):
        return r * net_hi >= net_lo

    # Evaluator T2: frontier-inequality lookup (independently derived form:
    # r >= net_lo/net_hi, computed via cross-multiplication on integers).
    def t2_hi_wins(r, net_hi, net_lo):
        return r.numerator * net_hi.numerator * net_lo.denominator >= \
               r.denominator * net_lo.numerator * net_hi.denominator

    pairs = [("64_vs_59", net64, net59, r64v59),
             ("68_vs_59", net68, net59, r68v59),
             ("68_vs_64", net68, net64, r68v64)]

    grid = [F(i, 100) for i in range(101)]
    win_maps = {}
    grid_agree = 0
    for name, hi, lo, frontier in pairs:
        wins = []
        for r in grid:
            w1 = t1_hi_wins(r, hi, lo)
            w2 = t2_hi_wins(r, hi, lo)
            if w1 == w2:
                grid_agree += 1
            wins.append(w1)
        win_maps[name] = {
            "frontier_exact": "%d/%d" % (frontier.numerator, frontier.denominator),
            "frontier_decimal": "%.6f" % float(frontier),
            "win_cells_of_101": sum(wins),
            "first_winning_grid_point": ("%.2f" % float(grid[wins.index(True)])) if any(wins) else None,
        }
        # win cells = grid points >= frontier = 101 - ceil(frontier*100)
        expected_cells = 101 - math.ceil(frontier * 100)
        check("win-cell count matches exact frontier arithmetic (%s)" % name,
              sum(wins) == expected_cells)
    check("twin evaluators agree on all 303 grid cells", grid_agree == 303)

    # ---- seeded validation leg (cannot flip the decision) ---------------
    leg = fx["model"]["seeded_validation_leg"]
    seed = leg["seed"]
    check("registered seed is 20260880 (> visible high-water 20260775)", seed == 20260880 and seed > 20260775)
    rng = random.Random(seed)
    n_per = leg["N_per_pair"]
    mc = {}
    draws_total = 0
    mc_agree = True
    for name, hi, lo, frontier in pairs:
        wins1 = 0
        for _ in range(n_per):
            # exact rational draw: uniform on {0, 1, ..., 10^6} / 10^6
            r = F(rng.randrange(0, 1000001), 1000000)
            draws_total += 1
            w1 = t1_hi_wins(r, hi, lo)
            w2 = t2_hi_wins(r, hi, lo)
            if w1 != w2:
                mc_agree = False
            wins1 += int(w1)
        emp = F(wins1, n_per)
        exact_share = 1 - frontier  # P(U >= frontier) for U ~ U[0,1]
        # binomial 4-sigma band around the exact share
        se = math.sqrt(float(exact_share * frontier) / n_per)
        check("empirical win share within 4 sigma of exact frontier share (%s)" % name,
              abs(float(emp - exact_share)) <= 4 * se + 1e-12)
        mc[name] = {"empirical_win_share": "%.4f" % float(emp),
                    "exact_win_share": "%.6f" % float(exact_share)}
    check("twin evaluators agree on all 30000 seeded draws", mc_agree)
    check("draw-count sentinel exact", draws_total == 3 * n_per)

    # ---- decision rule, evaluated strictly in registered order ----------
    rule_trace = []
    # R1 MEASURED-DEMAND: fires iff the packet carries measured per-anchor demand.
    g1_open = "zero sales history" in fx["pinned_constants"]["zero_evidence_verbatim"]["text"]
    check("G1 is open by the packet's own verbatim text", g1_open)
    r1_fires = not g1_open
    rule_trace.append({"rule": "R1 MEASURED-DEMAND", "fires": r1_fires,
                       "why": "no measured per-anchor conversion exists — the packet's verbatim honest null (G1)"})
    # R2 DOMINANCE SCREEN: an anchor dominating at EVERY r in [0,1].
    # At r=0 every higher anchor earns 0 < net(lo); at r=1 the highest wins.
    r2_fires = False
    dom_check_low = all(not t1_hi_wins(F(0), hi, lo) for _, hi, lo, _ in pairs)
    dom_check_high = all(t1_hi_wins(F(1), hi, lo) for _, hi, lo, _ in pairs)
    check("no anchor dominates at every retention (R2 cannot fire)", dom_check_low and dom_check_high)
    rule_trace.append({"rule": "R2 DOMINANCE SCREEN", "fires": r2_fires,
                       "why": "net is increasing in P but retention is free on [0,1]; no dominant anchor exists"})
    # R3 CONDITIONAL-DEFAULT.
    r3_fires = (not r1_fires) and (not r2_fires) and g1_open
    rule_trace.append({"rule": "R3 CONDITIONAL-DEFAULT", "fires": r3_fires,
                       "why": "G1 open; $59 is the only anchor with zero unmeasured parameters AND committed packet "
                              "support (BUNDLE-LISTING § Pricing, OWNER-QUEUE click row, bundle-starter §3/§7); "
                              "$64/$68 park behind the measured-retention frontiers (and $64 has zero packet "
                              "provenance, G3; $68 voids the committed saves-$9 rationale)"})
    ruling = "R3-CONDITIONAL-DEFAULT — recommend $59" if r3_fires else "R4-NULL"
    check("exactly one rule fires", [r1_fires, r2_fires, r3_fires].count(True) == 1)

    # Twin decision evaluators: independently recompute the ruling from the flags.
    ruling_twin = ("R3-CONDITIONAL-DEFAULT — recommend $59"
                   if (g1_open and not r1_fires and not r2_fires) else "R4-NULL")
    check("twin decision evaluators agree on the ruling", ruling == ruling_twin)

    # ---- 8-question probe battery (one probe per question) --------------
    battery = [
        {"q": "1. What is this really?",
         "probe": "A discount-depth decision on a two-component Gumroad bundle with ZERO demand data: the only "
                  "committed constants are the component prices ($49 + $19 PWYW-suggested = $68 separate), the "
                  "cited fee schedule (net(P) = 0.871P − 0.80), and the already-committed $59 listing. "
                  "The $9 'nudge' costs the seller exactly $7.039 net per both-buyer (0.871·9 − 0.80 saved fee)."},
        {"q": "2. What is the possibility space?",
         "probe": "Charged price on the coherent band [$49, $68] (floor: bundle must not undercut the kit alone — "
                  "packet's own coherence rule); the three named anchors are points on it. Two readings of "
                  "'$64/$68 anchors' exist: charged price (modeled here) vs displayed comparison ($68-separate is "
                  "already committed in copy; a displayed $64 would be arithmetically FALSE since $49+$19=$68 — "
                  "eliminated by the packet's own anti-fake-anchor stance, G3)."},
        {"q": "3. Most advanced capability reachable by the simplest implementation?",
         "probe": "Exact closed-form frontier table — no MC needed for the decision: $64 beats $59 iff retention "
                  ">= 50589/54944 ~ 0.9207; $68 beats $59 iff >= 5621/6492 ~ 0.8658; $68 beats $64 iff >= "
                  "13736/14607 ~ 0.9404. Any future measured retention decides by lookup, no re-run."},
        {"q": "4. What breaks it?",
         "probe": "NOT MEASURED, all three: (a) demand/retention at any anchor (G1 — packet verbatim 'zero sales "
                  "history'); (b) the PWYW minimum (G2 — 'minimum owner's choice', so the $68 separate total "
                  "assumes the suggested $19 is paid); (c) fee exactness (G4 — cited '~2.9% + $0.30'; bounded: "
                  "fee-free frontiers differ by < 0.19 pp, cannot flip orderings)."},
        {"q": "5. What does it unlock?",
         "probe": "A self-superseding price rule: publish at the committed $59, and the first measured sales "
                  "signal (the packet's own T+14-style checkpoint discipline, SWTK precedent) converts to a "
                  "switch decision by frontier lookup. Materiality bound at the packet's own 0-2 sales/month: "
                  "choosing $59 over $68 costs at most $15.678/month net, over $64 at most $8.710/month — "
                  "the wrong-anchor risk is capped and small."},
        {"q": "6. What does it depend on?",
         "probe": "HARD GATE G5: the bundle cannot exist until the ⚑B membership-kit and ⚑D template-packs "
                  "publish clicks are executed (a Gumroad bundle references existing live products) — the pricing "
                  "verdict is serveable now, the publish click stays owner-gated; plus the Gumroad fee schedule "
                  "as cited and the $19-suggested PWYW basis of the $68 anchor (G2)."},
        {"q": "7. Which lane should build it?",
         "probe": "Nothing to build. venture-lab owns the click (price field already queued at $59 in "
                  "OWNER-QUEUE); sim-lab delivers the frontier table; the owner executes. No code, no new "
                  "artifact (the packet's own §1: a bundle has no artifact of its own)."},
        {"q": "8. What is the smallest shippable slice?",
         "probe": "Zero diff: ratify the committed $59 click exactly as queued. The verdict adds only the parked "
                  "switch rule (frontier table) to the ledger — no packet edit, no copy rewrite, no new click."},
    ]
    check("battery has exactly 8 probes", len(battery) == 8)

    # ---- results ---------------------------------------------------------
    results = {
        "decision": {
            "ruling": ruling,
            "recommendation": "$59 one-time fixed (the committed listing price) — the only anchor with zero "
                              "unmeasured parameters and committed packet support; $64/$68 park behind measured "
                              "retention frontiers (lookup table below)",
            "rule_trace": rule_trace,
        },
        "exact_nets_usd": {
            "net_59": "50.589", "net_64": "54.944", "net_68": "58.428",
            "net_separate_both_at_19": "57.628", "net_kit_alone": "41.879",
            "bundle68_minus_separate": "0.800",
            "seller_cost_of_9_dollar_nudge": "7.039",
        },
        "retention_frontiers": win_maps,
        "fee_free_frontier_bounds": {
            "64_vs_59": "59/64 = 0.921875", "68_vs_59": "59/68 = 0.867647", "68_vs_64": "16/17 = 0.941176",
            "note": "cited-fee frontiers sit within 0.19 pp BELOW these bounds; fee imprecision (G4) cannot flip",
        },
        "buyer_savings_by_anchor_usd": {"59": "9", "64": "4", "68": "0"},
        "materiality_bound_monthly_usd": {"59_vs_68_max": "15.678", "59_vs_64_max": "8.710",
                                          "basis": "packet's own conservative 0-2 sales/month (Q-0259.4)"},
        "seeded_validation_leg": {"seed": seed, "draws": draws_total, "per_pair": mc,
                                  "twin_agreement": "all draws"},
        "probe_battery_v0": battery,
        "self_checks": dict(CHECKS),
    }

    # self_checks embedded before final count; re-embed after all checks done
    results["self_checks"] = {"passed": CHECKS["passed"], "failed": CHECKS["failed"]}

    out_path = os.path.join(HERE, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")

    print("VERDICT 040 — Ship-It Bundle pricing ($59 vs $64 vs $68)")
    print("ruling: %s" % ruling)
    print("exact nets: $59 -> 50.589 | $64 -> 54.944 | $68 -> 58.428 (per-sale, cited Gumroad fees)")
    print("frontiers: 64v59 %s | 68v59 %s | 68v64 %s" % (
        win_maps["64_vs_59"]["frontier_decimal"],
        win_maps["68_vs_59"]["frontier_decimal"],
        win_maps["68_vs_64"]["frontier_decimal"]))
    print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
    return 1 if CHECKS["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
