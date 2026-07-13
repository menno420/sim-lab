#!/usr/bin/env python3
"""VERDICT 041 — narrow-TAM cookbook pricing: $19 fixed vs PWYW.

Canonical case: Merge-Wall Cookbook $19 (idea-engine ORDER 006 SIM-REQUEST 3,
requesting seat venture-lab). Fully hermetic: reads exactly ONE file (its own
committed fixtures.json), stdlib-only, zero RNG (every decision quantity is a
closed-form Fraction), no timestamps in results.json, sorted keys. Exit 0 iff
every self-check passes.

Run: python3 sims/verdict-041-cookbook-pricing/cookbook_pricing_sim.py
"""

import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures.json"

CHECKS_PASSED = 0
CHECKS_FAILED = 0


def check(name, ok):
    global CHECKS_PASSED, CHECKS_FAILED
    if ok:
        CHECKS_PASSED += 1
    else:
        CHECKS_FAILED += 1
        print(f"SELF-CHECK FAIL: {name}")


def frac_str(f):
    f = Fraction(f)
    return f"{f.numerator}/{f.denominator}"


def main():
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Kernels (affine net(p) = a*p - b), from the pinned fee schedules.
    # Channel order is fixed and decision channel is FIRST.
    # ------------------------------------------------------------------
    P = Fraction(19)  # committed price, venture-lab merge-wall-cookbook.md §3
    kernels = {
        "gumroad_direct": (Fraction(871, 1000), Fraction(4, 5)),
        "kofi_free": (Fraction(23, 25), Fraction(3, 10)),
        "gumroad_discover": (Fraction(7, 10), Fraction(0)),
    }
    channel_order = ["gumroad_direct", "kofi_free", "gumroad_discover"]
    decision_channel = "gumroad_direct"

    def net(ch, p):
        a, b = kernels[ch]
        return a * p - b

    # Kernel constants re-derived from the quoted fee schedules (not just
    # asserted): direct = 1 - 0.10 - 0.029 proportional, 0.50 + 0.30 fixed.
    check("kernel direct a from fees", Fraction(1) - Fraction(10, 100) - Fraction(29, 1000) == kernels["gumroad_direct"][0])
    check("kernel direct b from fees", Fraction(50, 100) + Fraction(30, 100) == kernels["gumroad_direct"][1])
    check("kernel kofi a from fees", Fraction(1) - Fraction(5, 100) - Fraction(3, 100) == kernels["kofi_free"][0])
    check("kernel kofi b from fees", Fraction(30, 100) == kernels["kofi_free"][1])
    check("kernel discover a from fees", Fraction(1) - Fraction(30, 100) == kernels["gumroad_discover"][0])

    # ------------------------------------------------------------------
    # FIXED_19 arm — per-sale nets, exact (the zero-unmeasured-parameter arm).
    # ------------------------------------------------------------------
    net19 = {ch: net(ch, P) for ch in channel_order}
    check("net19 direct = 15749/1000", net19["gumroad_direct"] == Fraction(15749, 1000))
    check("net19 kofi = 859/50", net19["kofi_free"] == Fraction(859, 50))
    check("net19 discover = 133/10", net19["gumroad_discover"] == Fraction(133, 10))

    band_units = [0, 1, 2, 3]  # intake's conservative first-90-day band
    band_nets = {ch: [n * net19[ch] for n in band_units] for ch in channel_order}
    check("band nets direct", band_nets["gumroad_direct"] == [Fraction(0), Fraction(15749, 1000), Fraction(15749, 500), Fraction(47247, 1000)])
    check("band gross 0/19/38/57", [n * P for n in band_units] == [Fraction(0), Fraction(19), Fraction(38), Fraction(57)])

    # ------------------------------------------------------------------
    # Kernel-invariance theorem: at u = 1 the PWYW flip bar is w̄ = $19
    # exactly on EVERY affine kernel (same kernel both sides).
    # ------------------------------------------------------------------
    for ch in channel_order:
        a, b = kernels[ch]
        # solve a*w - b = a*19 - b  =>  w = 19; verify by strict bracketing
        check(f"parity wbar=19 exact on {ch} (tie)", net(ch, P) == net19[ch])
        check(f"parity wbar=19 exact on {ch} (below)", net(ch, P - Fraction(1, 100)) < net19[ch])
        check(f"parity wbar=19 exact on {ch} (above)", net(ch, P + Fraction(1, 100)) > net19[ch])

    # ------------------------------------------------------------------
    # u_min landmarks: u_min(w̄) = net19 / net(w̄) on the decision channel.
    # ------------------------------------------------------------------
    def u_min(ch, wbar):
        n = net(ch, wbar)
        return None if n <= 0 else net19[ch] / n

    landmarks_direct = {
        "3": Fraction(15749, 1813),
        "5": Fraction(15749, 3555),
        "10": Fraction(15749, 7910),
        "15": Fraction(15749, 12265),
        "19": Fraction(1),
        "29": Fraction(15749, 24459),
    }
    for w, expected in landmarks_direct.items():
        check(f"u_min direct at wbar={w}", u_min("gumroad_direct", Fraction(w)) == expected)
    check("u_min kofi at wbar=5 = 859/215", u_min("kofi_free", Fraction(5)) == Fraction(859, 215))
    check("u_min discover at wbar=5 = 19/5", u_min("gumroad_discover", Fraction(5)) == Fraction(19, 5))

    # ------------------------------------------------------------------
    # Split ladder: k paid takers gross-splitting one $19 on direct.
    # Each extra paid transaction costs exactly b = $0.80.
    # ------------------------------------------------------------------
    split_ladder = {}
    a_d, b_d = kernels["gumroad_direct"]
    for k in range(1, 6):
        total = k * net("gumroad_direct", P / k)
        expected = a_d * P - k * b_d
        check(f"split ladder k={k}", total == expected)
        split_ladder[str(k)] = {"net_exact": frac_str(total), "net_usd": float(total)}
    check("split ladder k=2 = 14.949", split_ladder["2"]["net_exact"] == frac_str(Fraction(14949, 1000)))
    check("split drag per extra transaction = 0.80", Fraction(split_ladder["1"]["net_exact"].split("/")[0]) / Fraction(split_ladder["1"]["net_exact"].split("/")[1]) - Fraction(split_ladder["2"]["net_exact"].split("/")[0]) / Fraction(split_ladder["2"]["net_exact"].split("/")[1]) == Fraction(4, 5))

    # ------------------------------------------------------------------
    # Fee-floor arithmetic (packet's own rule, reproduced exactly).
    # ------------------------------------------------------------------
    check("zero-profit payment floor 800/871", net("gumroad_direct", Fraction(800, 871)) == 0)
    check("fee-floor crossing p=3.20", Fraction(4, 5) / Fraction(16, 5) == Fraction(1, 4))
    fee_shares = {"3": Fraction(4, 5) / 3, "5": Fraction(4, 5) / 5, "19": Fraction(4, 5) / 19}
    check("fee share at $3 = 4/15", fee_shares["3"] == Fraction(4, 15))
    check("fee share at $5 = 16%", fee_shares["5"] == Fraction(4, 25))
    check("fee share at $19 = 4/95", fee_shares["19"] == Fraction(4, 95))

    # ------------------------------------------------------------------
    # PWYW grid: u ∈ 0.0..3.0 step 0.1 (31) × w̄ ∈ 0.0..29.0 step 0.5 (59)
    # = 1829 cells per channel. Twin evaluators per cell:
    #   E1 exact Fraction expected-value comparison
    #   E2 pure-integer cross-multiplied inequality
    # ------------------------------------------------------------------
    U_STEPS = 31   # ku = 0..30, u = ku/10
    W_STEPS = 59   # jw = 0..58, wbar = jw/2
    floors = [Fraction(0), Fraction(3), Fraction(5), Fraction(19)]
    win_counts = {ch: 0 for ch in channel_order}
    floor_win_counts = {ch: {str(int(m)): 0 for m in floors} for ch in channel_order}
    floor_cell_counts = {str(int(m)): 0 for m in floors}
    lose_counts = {ch: 0 for ch in channel_order}
    grid_cells = 0

    # integer forms: a = an/1000, b = bm/1000
    int_kernels = {"gumroad_direct": (871, 800), "kofi_free": (920, 300), "gumroad_discover": (700, 0)}
    for ch in channel_order:
        an, bm = int_kernels[ch]
        check(f"int kernel {ch} matches fractions", Fraction(an, 1000) == kernels[ch][0] and Fraction(bm, 1000) == kernels[ch][1])
        rhs = 20 * (19 * an - bm)  # net19 * 20000
        for ku in range(U_STEPS):
            u = Fraction(ku, 10)
            for jw in range(W_STEPS):
                wbar = Fraction(jw, 2)
                grid_cells += 1
                e1 = u * net(ch, wbar) >= net19[ch]
                e2 = ku * (an * jw - 2 * bm) >= rhs
                check(f"twin evaluators agree {ch} u={ku} w={jw}", e1 == e2)
                if e1:
                    win_counts[ch] += 1
                    for m in floors:
                        if wbar >= m:
                            floor_win_counts[ch][str(int(m))] += 1
                else:
                    lose_counts[ch] += 1
                if ch == decision_channel:
                    for m in floors:
                        if wbar >= m:
                            floor_cell_counts[str(int(m))] += 1
    check("grid cell count 3x1829", grid_cells == 3 * U_STEPS * W_STEPS)

    # Floor-mask coherence: a higher floor can only shrink the win region.
    for ch in channel_order:
        seq = [floor_win_counts[ch][str(int(m))] for m in floors]
        check(f"floor win counts monotone non-increasing {ch}", all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1)))
        check(f"win+lose = cells {ch}", win_counts[ch] + lose_counts[ch] == U_STEPS * W_STEPS)

    # PWYW_MIN19 per-PAID-SALE weak dominance: net(w̄) ≥ net(19) for every
    # grid payment w̄ ≥ 19 on every channel.
    for ch in channel_order:
        for jw in range(38, W_STEPS):
            check(f"min19 per-sale dominance {ch} jw={jw}", net(ch, Fraction(jw, 2)) >= net19[ch])

    # ------------------------------------------------------------------
    # Processing-rate bracket (reporting-only; kernel-invariance means the
    # u = 1 parity bar stays $19.00 at every rate — cannot flip anything).
    # ------------------------------------------------------------------
    bracket = {}
    for rate_pm in (23, 29, 35):  # per-mille processing rate
        a = Fraction(1) - Fraction(10, 100) - Fraction(rate_pm, 1000)
        b = Fraction(4, 5)
        n19 = a * P - b
        bracket[f"{rate_pm/10:.1f}%"] = {"net19_exact": frac_str(n19), "net19_usd": float(n19)}
        # parity invariance at this rate
        check(f"parity wbar=19 at rate {rate_pm}", a * P - b == n19 and a * (P - 1) - b < n19)
    check("bracket 2.3% net 15.863", bracket["2.3%"]["net19_exact"] == frac_str(Fraction(15863, 1000)))
    check("bracket 3.5% net 15.635", bracket["3.5%"]["net19_exact"] == frac_str(Fraction(15635, 1000)))

    # ------------------------------------------------------------------
    # Reads-leg bars (reporting-only; A4/G6): downloads per baseline buyer
    # = u/(1-z); ≥30 downloads in the kill window from B buyers needs
    # u/(1-z) ≥ 30/B.
    # ------------------------------------------------------------------
    reads_leg = {}
    for z_pct in (0, 25, 50, 75, 90):
        z = Fraction(z_pct, 100)
        mult = 1 / (1 - z)  # downloads per PAID take... times u gives total
        reads_leg[f"z={z_pct}%"] = {
            "downloads_per_baseline_buyer_at_u1": frac_str(mult),
            "u_needed_for_30_downloads_B3": frac_str(Fraction(30, 3) * (1 - z)),
            "u_needed_for_30_downloads_B1": frac_str(Fraction(30, 1) * (1 - z)),
        }
    check("reads bar z=0.9 B=3 u>=1", Fraction(30, 3) * Fraction(1, 10) == 1)
    check("reads bar z=0 B=3 u>=10", Fraction(30, 3) * 1 == 10)
    check("reads bar z=29/30 B=1 u>=1", Fraction(30) * Fraction(1, 30) == 1)

    # ------------------------------------------------------------------
    # DECISION RULE R1–R4, evaluated strictly in registered order.
    # ------------------------------------------------------------------
    gaps = fixtures["recorded_gaps_feeding_null_or_conditional"]
    g1_open = gaps[0].startswith("G1 (CRITICAL): NO measured PWYW")
    check("G1 recorded as open in fixtures", g1_open)

    # R1: needs a MEASURED (u, wbar) pair — none exists (G1).
    r1_fires = False  # no measured PWYW datum anywhere in the packet
    # R2: full-band dominance on the decision channel — prove FALSE by count.
    dc = decision_channel
    fixed_dominates = win_counts[dc] == 0
    pwyw_dominates = lose_counts[dc] == 0
    r2_fires = fixed_dominates or pwyw_dominates
    check("R2 structurally false: PWYW win region non-empty", win_counts[dc] > 0)
    check("R2 structurally false: FIXED win region non-empty", lose_counts[dc] > 0)
    # R3: G1 open and no full-band dominance.
    r3_fires = (not r1_fires) and (not r2_fires) and g1_open
    check("R3 fires", r3_fires)
    ruling = "R3-CONDITIONAL-DEFAULT" if r3_fires else ("R1" if r1_fires else ("R2" if r2_fires else "R4-NULL"))
    check("ruling is R3-CONDITIONAL-DEFAULT", ruling == "R3-CONDITIONAL-DEFAULT")

    # ------------------------------------------------------------------
    # results.json (sorted keys, no timestamps) + stdout summary.
    # ------------------------------------------------------------------
    results = {
        "arms": {
            "FIXED_19": {
                "net_per_sale": {ch: {"exact": frac_str(net19[ch]), "usd": float(net19[ch])} for ch in channel_order},
                "unmeasured_parameters": 0,
            },
            "PWYW": {
                "core_frontier": "u * net(wbar) >= net(19) per channel; direct: u*(0.871*wbar - 0.80) >= 15.749",
                "kernel_invariant_parity_bar_at_u1_usd": 19.0,
                "u_min_landmarks_direct": {w: {"exact": frac_str(v), "value": float(v)} for w, v in landmarks_direct.items()},
                "u_min_wbar5_kofi": {"exact": "859/215", "value": float(Fraction(859, 215))},
                "u_min_wbar5_discover": {"exact": "19/5", "value": 3.8},
                "unmeasured_parameters": "u, wbar, z (G1 — no PWYW measurement exists anywhere in the packet)",
            },
        },
        "band_render_direct_0_1_2_3_sales": {
            "gross_usd": [0.0, 19.0, 38.0, 57.0],
            "net_exact": [frac_str(x) for x in band_nets["gumroad_direct"]],
            "net_usd": [float(x) for x in band_nets["gumroad_direct"]],
        },
        "decision_rule_evaluation": {
            "R1_measured_pwyw_wins": "CANNOT FIRE — G1: no measured PWYW conversion, taker-rate, or mean-payment data exists anywhere in the repo; zero organic sales data for any product",
            "R2_full_band_dominance": {
                "fires": False,
                "pwyw_win_cells_decision_channel": win_counts[dc],
                "fixed_win_cells_decision_channel": lose_counts[dc],
                "note": "both regions non-empty — no arm dominates the registered band",
            },
            "R3_conditional_default": {
                "fires": True,
                "default": "committed $19 one-time fixed (zero unmeasured parameters; intake + vetting §3 + precedent chain $15 < $19 = template-packs rung < $29 SWTK live < $39 < $49)",
                "pwyw_parks_behind": "measured (u, wbar) clearing u*(0.871*wbar - 0.80) >= 15.749 on the decision channel; landmarks: u=1 needs wbar >= $19.00 exactly; wbar=$10 needs u >= 15749/7910 ~= 1.9910; wbar=$15 needs u >= 15749/12265 ~= 1.2841; the $3-floor variant needs u >= 15749/1813 ~= 8.6867",
                "min19_variant": "PWYW with $19 minimum (= $19 fixed + voluntary overpay) cannot lose per paid sale (per-sale dominance proven on every grid payment >= $19, every channel); parked on conversion-side risk (u unmeasured, G1)",
            },
            "R4_null": "not reached",
            "ruling": ruling,
        },
        "fee_floor": {
            "fee_share_at_3": {"exact": "4/15", "value": float(Fraction(4, 15))},
            "fee_share_at_5": {"exact": "4/25", "value": 0.16},
            "fee_share_at_19": {"exact": "4/95", "value": float(Fraction(4, 95))},
            "packet_rule_crossing_usd": 3.2,
            "zero_profit_payment_floor": {"exact": "800/871", "value": float(Fraction(800, 871))},
        },
        "grid": {
            "cells_per_channel": U_STEPS * W_STEPS,
            "channels": channel_order,
            "decision_channel": decision_channel,
            "floor_win_counts": floor_win_counts,
            "floor_cell_counts_decision_channel": floor_cell_counts,
            "pwyw_win_counts": win_counts,
            "u_grid": "0.0..3.0 step 0.1 (31)",
            "wbar_grid": "0.0..29.0 step 0.5 (59)",
        },
        "processing_rate_bracket_direct": bracket,
        "reads_leg_bars": reads_leg,
        "split_ladder_direct_gross19": split_ladder,
        "self_checks": {"failed": CHECKS_FAILED, "passed": CHECKS_PASSED},
    }
    # self_checks counted above are final except the JSON write itself.
    out = json.dumps(results, sort_keys=True, indent=2) + "\n"
    (HERE / "results.json").write_text(out, encoding="utf-8")

    print("VERDICT 041 — narrow-TAM cookbook pricing: $19 fixed vs PWYW (Merge-Wall Cookbook)")
    print(f"decision channel: {decision_channel}  net(19) = {frac_str(net19[dc])} = ${float(net19[dc])}")
    print(f"kernel-invariant parity bar at u=1: wbar = $19.00 exactly (all channels)")
    print(f"u_min landmarks direct: wbar=$10 -> {float(landmarks_direct['10']):.6f} · wbar=$15 -> {float(landmarks_direct['15']):.6f} · wbar=$5 -> {float(landmarks_direct['5']):.6f} · wbar=$3 -> {float(landmarks_direct['3']):.6f}")
    print(f"split ladder (gross $19): k=1 $15.749 · k=2 $14.949 · k=3 $14.149 · k=4 $13.349 · k=5 $12.549 (drag $0.80/transaction)")
    print(f"PWYW win cells (decision channel): {win_counts[dc]}/{U_STEPS * W_STEPS}; FIXED win cells: {lose_counts[dc]}/{U_STEPS * W_STEPS}")
    print(f"floor win counts direct: m=0 {floor_win_counts[dc]['0']} · m=3 {floor_win_counts[dc]['3']} · m=5 {floor_win_counts[dc]['5']} · m=19 {floor_win_counts[dc]['19']}")
    print(f"RULING: {ruling}")
    print(f"SELF-CHECKS: {CHECKS_PASSED} passed, {CHECKS_FAILED} failed")
    return 0 if CHECKS_FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
