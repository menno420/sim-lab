#!/usr/bin/env python3
"""VERDICT 037 — Ultramarine serial pricing (idea-engine ORDER 005 SIM-REQUEST 1, seat venture-lab).

Exact-analytic pricing comparison (rung 1, ZERO RNG — every quantity is a
closed-form Fraction). Reads every constant from the committed
pre-registration `fixtures.json` in this directory and touches nothing else.

Arms, per committed browsing reader (the packet's own frame):
  SERIAL       E[net] = r * (1 + p2 + p2*p3)        r = 0.70 * $2.99
  SINGLE       E[net] = s                            s = 0.70 * $4.99
  FREE_FUNNEL  E[net] = m * r * (q2 + q2*q3)         ep1 free (mechanism unpinned, gap G3)

Run:  python3 sims/verdict-037-venture-serial-pricing/serial_pricing_sim.py
Exit 0 iff all self-checks pass. Deterministic: byte-identical stdout and
results.json across runs (no RNG, no clock, sorted keys).
"""

import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))

CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAILED: %s" % label)


def frac_str(x):
    return "%s/%s" % (x.numerator, x.denominator)


def dec(x, places=6):
    """Exact decimal string of a Fraction, truncated-rounded half-even-free:
    round toward nearest with exact integer arithmetic (ties up)."""
    sign = "-" if x < 0 else ""
    x = abs(x)
    scaled = x * 10 ** places
    n = scaled.numerator // scaled.denominator
    rem = scaled - n
    if rem * 2 >= 1:
        n += 1
    s = str(n).rjust(places + 1, "0")
    return sign + s[:-places] + "." + s[-places:]


def bisect_root(f, lo, hi, iters=60):
    """Sign-change bisection with exact Fractions; returns (lo, hi) bracket."""
    flo, fhi = f(lo), f(hi)
    assert flo <= 0 <= fhi, "bad bracket"
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) <= 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def main():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
        fx = json.load(fh)

    # ---- constants from the pre-registration (verbatim pins) ----
    price_ep = F(fx["pinned_constants"]["price_per_episode_usd"]["value"])       # 2.99
    price_single = F(fx["pinned_constants"]["price_single_volume_usd"]["value"])  # 4.99
    roy = F(fx["pinned_constants"]["royalty_rate_70_band"]["value"])              # 0.70
    n_ep = fx["pinned_constants"]["episode_count"]["value"]
    check(n_ep == 3, "episode count is 3 (pinned)")
    check(price_ep == F(299, 100) and price_single == F(499, 100) and roy == F(7, 10),
          "pinned prices/royalty parse to the expected exact rationals")
    # 70%-band membership (CHECKLIST §4 pin): both prices inside $2.99–$9.99
    check(F(299, 100) <= price_ep <= F(999, 100), "per-episode price inside the 70% band")
    check(F(299, 100) <= price_single <= F(999, 100), "single-volume price inside the 70% band")

    r = roy * price_ep       # per-episode net
    s = roy * price_single   # single-volume net
    check(r == F(2093, 1000), "r = 2093/1000 (hand pin)")
    check(s == F(3493, 1000), "s = 3493/1000 (hand pin)")

    ratio = s / r
    B = ratio - 1
    check(ratio == F(499, 299), "s/r = 499/299 (hand pin)")
    check(B == F(200, 299), "breakeven B = 200/299 (hand pin)")

    # packet arithmetic reconciliation
    gross_full = 3 * price_ep
    net_full = 3 * r
    check(gross_full == F(897, 100), "full-run gross = $8.97 (packet pin)")
    check(net_full == F(6279, 1000), "full-run net exact = $6.279 (packet's ~6.27 is 2.09*3 rounding)")
    advantage_full = net_full / s
    check(F(17, 10) < advantage_full < F(18, 10), "full carry-through advantage ~1.80x, inside packet's '2-3x' claim only via gross framing — net is 1.80x")

    # ---- arm evaluators (twin: expected-value vs frontier-inequality) ----
    def serial_net(p2, p3):
        return r * (1 + p2 + p2 * p3)

    def serial_wins_ev(p2, p3):
        return serial_net(p2, p3) >= s

    def serial_wins_frontier(p2, p3):
        return p2 * (1 + p3) >= B

    def funnel_net(q2, q3, m=F(1)):
        return m * r * (q2 + q2 * q3)

    def funnel_wins_ev(q2, q3, m=F(1)):
        return funnel_net(q2, q3, m) >= s

    def funnel_wins_frontier(q2, q3, m=F(1)):
        return m * q2 * (1 + q3) >= ratio

    # ---- frontier landmarks (exact) ----
    p2_at_p3_1 = B / 2
    p2_at_p3_0 = B
    check(p2_at_p3_1 == F(100, 299), "serial breakeven p2 at p3=1 is 100/299")
    check(p2_at_p3_0 == F(200, 299), "serial breakeven p2 at p3=0 is 200/299")
    # symmetric root p + p^2 = B, bisection to < 1e-15
    lo, hi = bisect_root(lambda p: p + p * p - B, F(0), F(1))
    p_sym = (lo + hi) / 2
    check(hi - lo < F(1, 10**15), "symmetric serial root bracketed to <1e-15")
    check(F(45, 100) < p_sym < F(46, 100), "symmetric serial breakeven ~0.4586 in (0.45, 0.46)")

    q2_at_q3_1_m1 = ratio / 2
    check(q2_at_q3_1_m1 == F(499, 598), "funnel breakeven q2 at q3=1, m=1 is 499/598 (~0.8344)")
    lo, hi = bisect_root(lambda q: q + q * q - ratio, F(0), F(2))
    q_sym = (lo + hi) / 2
    check(F(88, 100) < q_sym < F(89, 100), "symmetric funnel breakeven ~0.8852 in (0.88, 0.89)")
    funnel_feasible_at_m1 = ratio <= 2
    check(funnel_feasible_at_m1, "funnel win region at m=1 is non-empty (needs q2(1+q3) >= 1.6689 <= 2)")

    # free-vs-serial identity: at equal rates, m=1, SERIAL - FREE = r exactly
    for a in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
        for b in (F(0), F(1, 2), F(1)):
            check(serial_net(a, b) - funnel_net(a, b) == r,
                  "identity SERIAL-FREE == r at rates (%s,%s)" % (a, b))

    # ---- 21x21 sweep grids (step 0.05), twin-evaluator agreement ----
    grid = [F(i, 20) for i in range(21)]
    serial_win_cells = 0
    serial_map_rows = []
    for p2 in grid:
        row = ""
        for p3 in grid:
            w_ev = serial_wins_ev(p2, p3)
            w_fr = serial_wins_frontier(p2, p3)
            check(w_ev == w_fr, "twin evaluators agree SERIAL p2=%s p3=%s" % (p2, p3))
            if w_ev:
                serial_win_cells += 1
            row += "W" if w_ev else "."
        serial_map_rows.append(row)
    # analytic count cross-check: cells with p2*(1+p3) >= 200/299
    analytic = sum(1 for p2 in grid for p3 in grid if p2 * (1 + p3) >= B)
    check(serial_win_cells == analytic, "serial WIN-cell count matches analytic frontier count")
    check(0 < serial_win_cells < 441, "serial win region is a proper subset of the grid")

    funnel_win_cells_m1 = 0
    for q2 in grid:
        for q3 in grid:
            w_ev = funnel_wins_ev(q2, q3)
            w_fr = funnel_wins_frontier(q2, q3)
            check(w_ev == w_fr, "twin evaluators agree FUNNEL q2=%s q3=%s" % (q2, q3))
            if w_ev:
                funnel_win_cells_m1 += 1
    check(0 < funnel_win_cells_m1 < serial_win_cells,
          "funnel (m=1) win region non-empty and strictly smaller than serial's")

    # m* table: minimum acquisition multiplier at symmetric conversion q
    m_star = {}
    for q in (F(1, 4), F(1, 2), F(3, 4), F(1)):
        m_req = ratio / (q * (1 + q))
        m_star[dec(q, 2)] = {"exact": frac_str(m_req), "decimal": dec(m_req)}
        check(funnel_wins_frontier(q, q, m_req), "m* is sufficient at q=%s" % q)
        check(not funnel_wins_frontier(q, q, m_req * F(999, 1000)), "0.999*m* is insufficient at q=%s" % q)

    # ---- delivery-fee sensitivity (REPORTING-ONLY, direction check) ----
    fee_rows = {}
    prevB = None
    for f_cents in (0, 5, 10, 15):
        f = F(f_cents, 100)
        r_f = r - roy * f     # fee deducted from the pre-royalty base (70% tier)
        s_f = s - roy * f
        B_f = s_f / r_f - 1
        fee_rows[dec(f, 2)] = {"B_exact": frac_str(B_f), "B_decimal": dec(B_f)}
        if prevB is not None:
            check(B_f > prevB, "delivery fee raises the serial breakeven (fee=%s)" % f)
        prevB = B_f
    check(fee_rows["0.00"]["B_exact"] == frac_str(B), "fee=0 row reproduces B exactly")

    # ---- decision rule (pre-registered order) ----
    gaps_open = fx["recorded_gaps_feeding_null_or_conditional"]
    measured_continuation_exists = False   # gap G1: packet states none measured
    measured_funnel_data_exists = False    # gap G2
    check(any(g.startswith("G1") for g in gaps_open), "gap G1 registered")
    check(any(g.startswith("G2") for g in gaps_open), "gap G2 registered")
    check(any(g.startswith("G3") for g in gaps_open), "gap G3 registered")

    ruling = None
    if measured_continuation_exists:
        ruling = "R1-SERIAL-WINS"
    elif B > 2:
        ruling = "R2-SINGLE-WINS-UNCONDITIONAL"
    elif (not measured_continuation_exists) and (not measured_funnel_data_exists) and 0 < B <= 2:
        ruling = "R3-CONDITIONAL-DEFAULT"
    else:
        ruling = "R4-NULL"
    check(ruling == "R3-CONDITIONAL-DEFAULT",
          "registered rule lands R3 (no measured rates in packet, 0 < B <= 2)")

    results = {
        "ruling": ruling,
        "recommendation": {
            "default_publish_arm": "SINGLE volume at $4.99 (net $3.493/sale exact; the only arm with zero unmeasured parameters; vetted band $3.99-$5.99, fallback $3.99)",
            "serial_parked_behind": "measured carry-through p2*(1+p3) >= 200/299 (~0.6689): e.g. p2 >= 33.4% if p3=100%, p2 >= 45.9% if p3=p2, p2 >= 66.9% if p3=0",
            "free_funnel_not_recommendable": "win bar m*q2*(1+q3) >= 499/299 (~1.6689) needs BOTH unmeasured behavior (>=83.4% conversion at m=1 even with perfect ep3 carry) AND an unpinned $0.00 platform mechanism (gap G3)"
        },
        "exact_constants": {
            "r_per_episode_net": {"exact": frac_str(r), "usd": dec(r, 3)},
            "s_single_net": {"exact": frac_str(s), "usd": dec(s, 3)},
            "B_serial_breakeven": {"exact": frac_str(B), "decimal": dec(B)},
            "s_over_r_funnel_bar": {"exact": frac_str(ratio), "decimal": dec(ratio)},
            "full_carrythrough_serial_net": {"exact": frac_str(net_full), "usd": dec(net_full, 3)},
            "full_carrythrough_advantage_net": {"exact": frac_str(advantage_full), "decimal": dec(advantage_full)}
        },
        "serial_frontier": {
            "p2_at_p3_1": {"exact": frac_str(p2_at_p3_1), "decimal": dec(p2_at_p3_1)},
            "p2_at_p3_eq_p2": {"decimal_pm_1e15": dec(p_sym)},
            "p2_at_p3_0": {"exact": frac_str(p2_at_p3_0), "decimal": dec(p2_at_p3_0)},
            "win_cells_of_441": serial_win_cells,
            "win_map_rows_p2_outer_p3_inner_step_0.05": serial_map_rows
        },
        "funnel_frontier": {
            "q2_at_q3_1_m1": {"exact": frac_str(q2_at_q3_1_m1), "decimal": dec(q2_at_q3_1_m1)},
            "q2_symmetric_m1": {"decimal_pm_1e15": dec(q_sym)},
            "win_cells_of_441_at_m1": funnel_win_cells_m1,
            "m_star_at_symmetric_q": m_star,
            "free_vs_serial_identity": "SERIAL - FREE == r exactly at equal rates, m=1 (free can only win via acquisition multiplier m)"
        },
        "delivery_fee_sensitivity_reporting_only": fee_rows,
        "self_checks": dict(CHECKS),
    }

    if CHECKS["failed"] == 0:
        out = json.dumps(results, indent=2, sort_keys=True) + "\n"
        with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
            fh.write(out)

    print("RULING: %s" % ruling)
    print("B (serial-vs-single carry-through breakeven) = %s = %s" % (frac_str(B), dec(B)))
    print("frontier: p2>=%s (p3=1) | p2~%s (p3=p2) | p2>=%s (p3=0)"
          % (dec(p2_at_p3_1), dec(p_sym), dec(p2_at_p3_0)))
    print("funnel bar at m=1: q2(1+q3) >= %s = %s (q2>=%s even at q3=1; symmetric ~%s)"
          % (frac_str(ratio), dec(ratio), dec(q2_at_q3_1_m1), dec(q_sym)))
    print("serial WIN cells: %d/441 · funnel(m=1) WIN cells: %d/441" % (serial_win_cells, funnel_win_cells_m1))
    print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
    return 0 if CHECKS["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
