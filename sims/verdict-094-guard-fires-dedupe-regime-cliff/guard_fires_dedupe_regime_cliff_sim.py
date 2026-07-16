#!/usr/bin/env python3
"""VERDICT 094 sim — guard-fires dedupe regime cliff (idea-engine PROPOSAL 081).

Three-arm, hermetic, stdlib-only, pre-registered (fixtures.json committed
BEFORE this runner):

  Arm A — seedless faithful tail-slice replay of the pinned mechanism
          (append-only ledger of (key, t) lines; per fire batch ONE scan:
          whole-file read, JSON-parse capped at the last S = 200 lines,
          key visible iff a same-key line sits in the tail with age <= W =
          600 s strictly; verdict rows append first, always, keylessly) +
          the closed forms on their proven domains: p(c) = c*(floor(W/c)+1),
          leak = max(0, F-S) at V = 0, leak = min(F, F-S+V) on the
          saturated region, rotation period F/gcd(F, F-S), the quadratic
          read sum. Pure integer arithmetic, DECISION-bearing.
  Arm B — INDEPENDENTLY-WRITTEN depth-arithmetic twin replay over a
          differently-shaped log (no line list: a global line counter plus
          per-key last-append registers; visibility decided by
          depth-from-end arithmetic). Tied to Arm A through the typed
          must-equal contacts C1-C4.
  Arm R — seeded random scenario traces, REPORTING-ONLY (no statistical
          gate): per trace EXACTLY 4 rng.randint draws in registered order
          (F in [1,400], V in [0,8], c in [60,1200], R in [2,12]), one
          random.Random per seed. Seeds 20261718 (N = 20,000) / 20261719
          (N = 8,000); presentation shuffle 20261720 (presentation legs
          only); aux 20261721 reserved and NEVER read.

Decision rule (registered order, twin independently-written evaluators over
an ENUMERATED boolean input set): REJECT -> INVALID -> APPROVE -> NULL.

Deterministic: no wall clock, no absolute paths, no network, no git at run
time; stdout and results.json are byte-identical across process runs.
CPython 3.11 pinned and asserted.
"""

import itertools
import json
import math
import os
import random
import sys
from math import gcd

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)

S = FIX["world"]["source_constants"]["S"]
W = FIX["world"]["source_constants"]["W"]

CHECKS = []          # (name, ok(bool), detail)
RESULTS = {}         # measured values -> results.json
SEEDS_CONSTRUCTED = []


def check(name, ok, detail):
    CHECKS.append((name, bool(ok), str(detail)))
    print("  [%s] %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Arm A — faithful tail-slice replay (DECISION-bearing)
# ---------------------------------------------------------------------------

def replay(F, V, c, R, s=None, w=None, order="verdict_first", batches=None,
           window_off=False, scan_off=False, naive_ts=False, keyed=False,
           horizon=None, probe=False):
    """Faithful replay of the pinned mechanism. Returns per-run fire-append
    counts, per-run leaked-key tuples, cumulative reads/parses, and the two
    structural-identity flags (F1)."""
    s = S if s is None else s
    w = W if w is None else w
    ledger = []            # (key or None, t) - key None = verdict row
    per_run = []
    leaked = []
    reads = parses = 0
    fire_appends = vrows = 0
    length_identity_ok = True
    keyset_structural_ok = True
    index = {}             # keyed-repair arm only
    if batches is None:
        batches = [list(range(F))]
    r = 0
    while True:
        t = r * c
        if horizon is not None:
            if t > horizon:
                break
        elif r >= R:
            break
        if order == "verdict_first":
            for _ in range(V):
                ledger.append((None, t))
                vrows += 1
        appended_this_run = []
        for batch in batches:
            if keyed:
                keyset = set(k for k, ts in index.items() if t - ts <= w)
            else:
                reads += len(ledger)                    # read_text(): whole file
                if scan_off:
                    parses += len(ledger)
                    tail = ledger
                else:
                    parses += min(len(ledger), s)       # parse cap: last s lines
                    tail = ledger[-s:]
                if naive_ts:
                    keyset = set()                      # naive rows dedupe nothing
                elif window_off:
                    keyset = set(k for k, ts in tail if k is not None)
                else:
                    keyset = set(k for k, ts in tail
                                 if k is not None and t - ts <= w)
                if probe:
                    # F1 structural probe (independent second pass): the key
                    # set is exactly the in-window verdict-less keys of the
                    # last s lines; no verdict row (None) ever enters it.
                    lo = max(0, len(ledger) - s) if not scan_off else 0
                    independent = set()
                    for i in range(lo, len(ledger)):
                        ki, ti = ledger[i]
                        if ki is None:
                            continue
                        if window_off or t - ti <= w:
                            independent.add(ki)
                    if keyset != independent or None in keyset:
                        keyset_structural_ok = False
            for k in batch:
                if k in keyset:
                    continue
                ledger.append((k, t))
                fire_appends += 1
                if keyed:
                    index[k] = t
                appended_this_run.append(k)
        if order == "fires_first":
            for _ in range(V):
                ledger.append((None, t))
                vrows += 1
        # F1 ledger-length identity at every run boundary
        if len(ledger) != fire_appends + vrows:
            length_identity_ok = False
        per_run.append(len(appended_this_run))
        leaked.append(tuple(appended_this_run))
        r += 1
    return {"per_run": per_run, "leaked": leaked, "reads": reads,
            "parses": parses, "vrows": vrows, "fire_appends": fire_appends,
            "len_ok": length_identity_ok, "keyset_ok": keyset_structural_ok}


def p_law(c):
    return c * (W // c + 1)


def day_count_law(c):
    return 86400 // p_law(c) + 1


# ---------------------------------------------------------------------------
# Arm B — independently-written depth-arithmetic twin (no line list)
# ---------------------------------------------------------------------------

def arm_b(F, V, c, R, s=None, w=None):
    """Depth-arithmetic replay: a global line counter plus per-key
    last-append registers; a key is visible iff its most recent copy sits
    at depth <= s from the end AND its age is <= w (older copies are both
    deeper and older, so the last copy decides)."""
    s = S if s is None else s
    w = W if w is None else w
    total = 0
    last_line = {}
    last_t = {}
    per_run = []
    for r in range(R):
        t = r * c
        total += V                       # verdict rows: slots, no keys
        depth_base = total               # batch-start line count
        cnt = 0
        for k in range(F):
            if (k in last_line
                    and depth_base - last_line[k] <= s
                    and t - last_t[k] <= w):
                continue
            last_line[k] = total
            last_t[k] = t
            total += 1
            cnt += 1
        per_run.append(cnt)
    return per_run


# ---------------------------------------------------------------------------
# Arm R — seeded reporting-only scenario traces (registered draw grammar)
# ---------------------------------------------------------------------------

def arm_r_run(seed, traces):
    """(leak_regime_traces, max_per_run_burst, total_appends, draw_count)
    under the disclosed field realizations (fixtures _disclosures)."""
    rng = make_rng(seed)
    draws = leak_regime = max_burst = total_appends = 0
    for _ in range(traces):
        f = rng.randint(1, 400)
        v = rng.randint(0, 8)
        c = rng.randint(60, 1200)
        r = rng.randint(2, 12)
        draws += 4
        pr = arm_b(f, v, c, r)
        total_appends += sum(pr)
        if sum(pr[1:]) > 0:
            leak_regime += 1
        mb = max(pr)
        if mb > max_burst:
            max_burst = mb
    return leak_regime, max_burst, total_appends, draws


# ---------------------------------------------------------------------------
# twin decision evaluators (independently written)
# ---------------------------------------------------------------------------

def evaluator_one(r1, r2, r3, r4, gates_ok, approve_cond):
    if r1 and r2 and r3 and r4:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if approve_cond:
        return "APPROVE"
    return "NULL"


def evaluator_two(r1, r2, r3, r4, gates_ok, approve_cond):
    reject_votes = sum(1 for clause in (r1, r2, r3, r4) if clause)
    token = "NULL"
    if approve_cond:
        token = "APPROVE"
    if gates_ok is False:
        token = "INVALID"
    if reject_votes == 4:
        token = "REJECT"
    return token


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("VERDICT 094 sim — guard-fires dedupe regime cliff (PROPOSAL 081)")
    print("shipped-algorithm replay: W = %d s window, S = %d-line tail scan, "
          "verdict rows exempt-but-slot-occupying" % (W, S))

    A = FIX["anchors_F3"]
    CTRL = FIX["controls_F5"]

    # F0 — harness pins -----------------------------------------------------
    pyminor = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    pin = FIX["arm_r"]["cpython_pin"].split(" ")[0]
    check("F0.python-minor-pinned", pyminor == pin,
          "CPython %s (pinned %s; Arms A/B are seedless exact integer "
          "arithmetic, platform-independent)" % (pyminor, pin))
    check("F1.constants-echo", S == 200 and W == 600,
          "S = %d, W = %d echo the pinned source constants "
          "(_GUARD_FIRES_DEDUPE_SCAN / GUARD_FIRES_DEDUPE_WINDOW_S)" % (S, W))

    # F2a / C1 — the RENEWAL law --------------------------------------------
    cads = FIX["world"]["grids"]["cadence_grid"]
    day_replay = []
    for c in cads:
        rr = replay(1, 0, c, None, horizon=86400)
        day_replay.append(sum(rr["per_run"]))
    day_closed = [day_count_law(c) for c in cads]
    check("C1.day-table", day_replay == day_closed == A["day_table"],
          "replay day counts %s == closed law floor(86400/p(c))+1 == "
          "registered (131/121/97/81/73/144/131/97/73)" % (day_replay,))
    check("F1.p-mod-c", all(p_law(c) % c == 0 for c in cads),
          "p(c) = c*(floor(600/c)+1) == 0 (mod c) on all 9 cadences")
    wp = A["witness_pair"]
    ratio_num, ratio_den = wp["rate_ratio"]
    check("F2a.witness-pair",
          p_law(600) == wp["p600"] and p_law(601) == wp["p601"]
          and ratio_num * p_law(601) == ratio_den * p_law(600)
          and gcd(ratio_num, ratio_den) == 1,
          "p(600) = %d, p(601) = %d; steady-rate ratio r(601)/r(600) = "
          "p(600)/p(601) = %d/%d exactly (checking less often writes ~2x more)"
          % (p_law(600), p_law(601), ratio_num, ratio_den))
    check("F2a.non-monotone",
          day_replay[cads.index(601)] > day_replay[cads.index(600)]
          and day_replay[cads.index(601)] == max(day_replay),
          "day count at c = 601 (%d) > at c = 600 (%d) and is the grid "
          "maximum — the record rate is NON-monotone in cadence"
          % (day_replay[cads.index(601)], day_replay[cads.index(600)]))

    # F2b / C2 — the CLIFF and the rotating alibi ----------------------------
    Fgrid = FIX["world"]["grids"]["F_grid"]
    Vgrid = FIX["world"]["grids"]["V_grid"]
    grid_a = {}
    grid_b = {}
    len_ok = keyset_ok = True
    for f in Fgrid:
        for v in Vgrid:
            ra = replay(f, v, 1, 80, probe=(f in (200, 250) and v in (1, 50)))
            grid_a[(f, v)] = ra
            grid_b[(f, v)] = arm_b(f, v, 1, 80)
            len_ok &= ra["len_ok"]
            keyset_ok &= ra["keyset_ok"]
    check("F1.ledger-length-identity", len_ok,
          "ledger length == sum fire appends + sum verdict rows at every run "
          "boundary, all 40 grid cells")
    check("F1.keyset-structural", keyset_ok,
          "scan key set == the last-S-lines in-window verdict-less keys "
          "(independent second pass) and no verdict row ever enters it "
          "(instrumented probe cells)")

    leak_row = []
    for f in Fgrid:
        tail = grid_a[(f, 0)]["per_run"][40:]
        leak_row.append(tail[0] if len(set(tail)) == 1 else -1)
    check("F2b.leak-row", leak_row == A["leak_row_V0"]
          and leak_row == [max(0, f - S) for f in Fgrid],
          "V = 0 steady leak %s == max(0, F-200) == registered "
          "(0/0/0/0/1/50/100/200)" % (leak_row,))
    check("F2b.margin0-pair",
          leak_row[Fgrid.index(200)] == 0 and leak_row[Fgrid.index(201)] == 1,
          "F = 200 leaks 0/run forever; F = 201 leaks 1/run forever — the "
          "scan bound is a CLIFF, not a graceful degrader")

    rot_first = {}
    for f in (201, 250, 300, 400):
        period = f // gcd(f, f - S)
        rr = replay(f, 0, 1, period + 3)
        s2 = rr["leaked"][1]
        first = None
        for i in range(2, len(rr["leaked"])):
            if rr["leaked"][i] == s2:
                first = i + 1
                break
        rot_first[f] = (period, first)
    check("C2.rotation-first-repeat",
          all(rot_first[f][1] == 2 + rot_first[f][0] for f in rot_first)
          and [rot_first[f][0] for f in (201, 250, 300, 400)]
          == [A["rotation_periods"]["F%d" % f] for f in (201, 250, 300, 400)],
          "periods F/gcd(F, F-200) = %s (registered 201/5/3/2); run-2 leaked "
          "set first repeats at run 2 + period on all 4 cells (F = 201 at "
          "run 203)" % ([rot_first[f][0] for f in (201, 250, 300, 400)],))
    blocks = [sorted(grid_a[(250, 0)]["leaked"][i]) for i in (1, 2, 3)]
    reg_blocks = [list(range(b0, b1 + 1)) for b0, b1 in A["rotation_F250_blocks"]]
    check("F2b.rotation-blocks-F250",
          blocks == reg_blocks,
          "F = 250 leaked blocks runs 2/3/4 = 0-49 / 50-99 / 100-149 — the "
          "leaked identity ROTATES through a constant finding population")

    # F2c — COMPOUNDING displacement -----------------------------------------
    sat_cells = [(f, v) for f in Fgrid for v in Vgrid
                 if v >= S or f >= 2 * (S - v)]
    sat_ok = True
    sat_measured = {}
    for (f, v) in sat_cells:
        tail = grid_a[(f, v)]["per_run"][40:]
        law = min(f, f - S + v)
        sat_measured["%d_%d" % (f, v)] = tail[0] if len(set(tail)) == 1 else -1
        sat_ok &= all(x == law for x in tail)
    check("F2c.saturated-law", sat_ok and len(sat_cells) == 13,
          "steady leak == min(F, F-200+V) on all 13 qualifying cells "
          "(incl. the (400,V) row 201/205/250/400 and (300,50) = 150)")
    check("F2c.saturated-400-row",
          all(sat_measured["400_%d" % v] == A["saturated_400_row"]["V%d" % v]
              for v in (1, 5, 50, 200)),
          "(400, V) row = %s (registered 201/205/250/400)"
          % ([sat_measured["400_%d" % v] for v in (1, 5, 50, 200)],))
    check("F2c.saturated-300-50",
          sat_measured["300_50"] == A["saturated_300_50"],
          "(300, 50) = %d (registered 150; the F >= 2(S-V) boundary holds)"
          % sat_measured["300_50"])

    rb398 = replay(398, 1, 1, 80)
    rb397 = replay(397, 1, 1, 80)
    check("F2c.boundary-pair",
          all(x == 199 for x in rb398["per_run"][1:])
          and len(set(rb397["per_run"][1:])) > 1,
          "(398, 1) constant 199/run from run 2 (the saturated-law boundary); "
          "(397, 1) already non-constant (alternates %s)"
          % (sorted(set(rb397["per_run"][1:])),))

    pr2001 = grid_a[(200, 1)]["per_run"]
    o = A["orbit_200_1"]
    leak_phase = pr2001[1:]
    tail_sum = sum(pr2001[40:80])
    check("F2c.orbit-200-1",
          pr2001[:12] == o["prefix_12"]
          and max(leak_phase) == o["leak_phase_peak"]
          and leak_phase.index(max(leak_phase)) + 2 == o["peak_first_at_run"]
          and tail_sum == o["tail_mean_runs_41_80"] * 40
          and sum(leak_phase) == o["total_runs_2_80"],
          "(200, 1): prefix %s, leak-phase peak %d first at run %d, tail mean "
          "exactly %d (sum %d over 40 runs), total %d over runs 2-80 vs the "
          "naive one-for-one %d — ONE suppression per run compounds ~13x"
          % (pr2001[:12], max(leak_phase), leak_phase.index(max(leak_phase)) + 2,
             o["tail_mean_runs_41_80"], tail_sum, sum(leak_phase),
             o["naive_one_for_one_total"]))
    check("F2c.orbit-200-5",
          set(grid_a[(200, 5)]["per_run"][40:]) == {A["orbit_200_5_tail"]},
          "(200, 5) sustains exactly %d/run (runs 41-80)" % A["orbit_200_5_tail"])
    check("F2c.orbit-200-50",
          set(grid_a[(200, 50)]["per_run"][40:]) == {A["orbit_200_50_tail"]},
          "(200, 50) settles at exactly %d/run — 2x the naive 50"
          % A["orbit_200_50_tail"])
    pr25050 = grid_a[(250, 50)]["per_run"]
    cyc = A["orbit_250_50"]["cycle"]
    two_cycle_ok = all(pr25050[i] in cyc for i in range(40, 80)) and \
        all(pr25050[i] != pr25050[i + 1] for i in range(40, 79))
    check("F2c.orbit-250-50",
          two_cycle_ok and sum(pr25050[1:]) == A["orbit_250_50"]["total_runs_2_80"],
          "(250, 50) locks the exact 2-cycle {100, 150} (runs 41-80 alternate), "
          "total %d over runs 2-80 (registered 9850)" % sum(pr25050[1:]))
    pr150 = grid_a[(1, 50)]["per_run"]
    check("F2c.orbit-1-50",
          all(pr150[i] == (1 if i % 4 == 0 else 0) for i in range(80)),
          "(1, 50) re-records the single finding every 4th run by pure line "
          "displacement (period %d, no time expiry at c = 1)"
          % A["orbit_1_50_period"])

    comp_cells = [(f, v) for v in (1, 5, 50) for f in Fgrid
                  if not (v >= S or f >= 2 * (S - v))]
    ct = A["compounding_totals_runs_2_80"]
    reg_cells = [k for k in ct if k != "note"]
    totals_measured = dict(("%d_%d" % (f, v), sum(grid_a[(f, v)]["per_run"][1:]))
                           for (f, v) in comp_cells)
    check("F3.compounding-totals",
          all(totals_measured[k] == ct[k] for k in reg_cells),
          "all 13 registered compounding totals reproduced at their cells "
          "(969/2236/7771 @ F=199; 2315/7850 @ F=200; 1068/2389/7890 @ F=201; "
          "4260/5125/9850 @ F=250; 8057/8685 @ F=300)")

    # C3 — twin contact -------------------------------------------------------
    c3_ok = all(grid_b[cell] == grid_a[cell]["per_run"]
                for cell in comp_cells + sat_cells)
    c3_extra = all(grid_b[cell] == grid_a[cell]["per_run"]
                   for cell in grid_a)
    check("C3.twin-sequences", c3_ok,
          "Arm B (depth-arithmetic) == Arm A (tail-slice) per-run sequences "
          "EXACTLY on all 20 compounding cells x 80 runs and all 13 saturated "
          "cells (and on the whole 40-cell grid: %s — extra coverage)" % c3_extra)

    # F2d — BREATHING ---------------------------------------------------------
    bcell = FIX["world"]["grids"]["breathing_cell"]
    rbre = replay(bcell[0], 0, bcell[1], bcell[2], probe=True)
    expect_orbit = [201] + [1, 1, 199] * 7 + [1, 1]
    check("F2d.breathing-orbit",
          rbre["per_run"] == expect_orbit
          and sum(rbre["per_run"]) == A["breathing_orbit"]["total_24_runs"],
          "(201, 300, 24) orbit == 201, (1,1,199)x7, 1, 1 — total %d "
          "(registered 1610 vs the naive 'leaks 1/run' 224)"
          % sum(rbre["per_run"]))
    bre_b = arm_b(bcell[0], 0, bcell[1], bcell[2])
    check("F2d.breathing-twin", bre_b == rbre["per_run"],
          "Arm B reproduces the breathing orbit exactly (extra twin coverage)")
    rbw = replay(bcell[0], 0, bcell[1], bcell[2], window_off=True)
    check("F5.window-off-control",
          all(x == 1 for x in rbw["per_run"][1:]) and rbw["per_run"][0] == 201,
          "W -> infinity collapses the breathing cell to exactly 1/run after "
          "run 1 — the 199-bursts are EXPIRY, not the line bound")

    # F2e / C4 — the READ BILL ------------------------------------------------
    rs = FIX["world"]["grids"]["read_scenario"]
    rread = replay(rs[0], rs[1], rs[2], rs[3], probe=True)
    reg_reads = A["reads"]["scenario_400_0_60_11"]
    quad_sum = rs[0] * (rs[3] - 1) + (S) * sum(range(rs[3] - 2 + 1))
    last_run_lines = rs[0] + S * (rs[3] - 2)
    check("C4.read-census",
          rread["reads"] == reg_reads["lines_read"] == quad_sum
          and rread["parses"] == reg_reads["parses"]
          and last_run_lines == reg_reads["last_run_lines"],
          "(400, 0, 60, 11): %d cumulative lines read == the closed quadratic "
          "sum (registered 13,000; the last run alone reads %d) vs %d JSON "
          "parses (registered 2,000) — 'bounded scan' bounds parses, not reads"
          % (rread["reads"], last_run_lines, rread["parses"]))
    reg_bre = A["reads"]["breathing_201_300_24"]
    check("F2e.breathing-reads",
          rbre["reads"] == reg_bre["lines_read"]
          and rbre["parses"] == reg_bre["parses"],
          "breathing scenario pays %d lines read for %d parses "
          "(registered 20,122 / 4,600)" % (rbre["reads"], rbre["parses"]))
    rsoff = replay(rs[0], rs[1], rs[2], rs[3], scan_off=True)
    check("F5.scan-off-control", sum(rsoff["per_run"][1:]) == 0,
          "scan off (parse the whole file), window kept: the (400, 60) "
          "scenario leaks exactly 0 — the cap defends a cost already paid "
          "and buys the leak in exchange")

    # F2f — the TRUE SENTENCE (design point) ----------------------------------
    dp = FIX["world"]["grids"]["design_point"]
    dp_runs = {}
    dp_ok = True
    for f in dp["F"]:
        rr = replay(f, 0, dp["c"], dp["R"])
        dp_runs[str(f)] = rr["per_run"]
        dp_ok &= rr["per_run"] == [f] + [0] * (dp["R"] - 1)
    check("F2f.design-point", dp_ok,
          "F in {1, 50, 200}, V = 0, c = 60, R = 3: re-runs append exactly 0 "
          "— at its own design point the dedupe works exactly as designed")

    # F5 — remaining degeneracy/convention controls ---------------------------
    check("F5.V-ge-S-saturation",
          all(set(grid_a[(f, 200)]["per_run"][40:]) == {f} for f in Fgrid),
          "V = 200 >= S: leak == F exactly on all 8 F cells (the run's own "
          "verdict rows fill the whole tail before the scan)")

    flip_reg_ok = True
    flip_extra_ok = True
    for v in (1, 5, 50):
        for f in Fgrid:
            rff = replay(f, v, 1, 80, order="fires_first")
            same = rff["per_run"] == grid_a[(f, v)]["per_run"]
            if v == 5:
                flip_reg_ok &= same
            else:
                flip_extra_ok &= same
    check("F5.order-flip", flip_reg_ok,
          "verdict-first vs fires-first per-run sequences IDENTICAL on the 8 "
          "probed cells (F grid at V = 5, the disclosed realization; the "
          "V = 1 and V = 50 rows also invariant: %s — extra coverage) — the "
          "pinned order is not load-bearing there, verified not assumed"
          % flip_extra_ok)

    rsplit = replay(250, 0, 1, 80,
                    batches=[list(range(125)), list(range(125, 250))])
    check("F5.batch-split",
          sorted(set(rsplit["per_run"][40:])) == [50, 75]
          and sorted(set(grid_a[(250, 0)]["per_run"][40:])) == [50],
          "250 split as 125+125: steady per-run leak set {50, 75} vs "
          "one-batch {50} — the one-batch convention is LOAD-BEARING, "
          "census registered")

    rnaive = replay(200, 0, 1, 3, naive_ts=True)
    check("F5.naive-ts-fail-open",
          rnaive["per_run"] == [200, 200, 200]
          and grid_a[(200, 0)]["per_run"][:3] == [200, 0, 0],
          "naive-timestamp rows dedupe nothing: (200, 0, c=1, R=3) appends "
          "[200, 200, 200] vs aware [200, 0, 0] — the fail-open pre-fix world")

    sprime = [sum(replay(f, 0, 1, 80, s=1000)["per_run"][1:]) for f in Fgrid]
    r1001 = replay(1001, 0, 1, 80, s=1000)
    check("F5.S-prime-relocation",
          all(x == 0 for x in sprime)
          and set(r1001["per_run"][40:]) == {1},
          "S' = 1000: whole F-grid leak 0; margin cell F = 1001 leaks exactly "
          "1/run — the cliff RELOCATES, it does not dissolve")

    keyed_zero = all(sum(replay(f, v, 1, 80, keyed=True)["per_run"][1:]) == 0
                     for f in Fgrid for v in Vgrid)
    day_keyed = []
    for c in cads:
        rr = replay(1, 0, c, None, keyed=True, horizon=86400)
        day_keyed.append(sum(rr["per_run"]))
    check("F5.keyed-index-repair",
          keyed_zero and day_keyed == A["day_table"],
          "keyed {key: last_append_ts} index: leak 0 at EVERY (F, V) grid "
          "cell, and the renewal day table is PRESERVED on all 9 cadences "
          "(the repair kills displacement, not the window semantics)")

    # F4 — pencil worlds -------------------------------------------------------
    rp = replay(1, 0, 60, 2)
    check("F4.two-runs-60s", rp["per_run"] == [1, 0],
          "F = 1, two runs 60 s apart: the second scan sees one 60-s-old "
          "record -> 0 appends")
    check("F4.p601-one-line", 600 // 601 == 0 and p_law(601) == 601,
          "floor(600/601) = 0 => p(601) = 601 — a 601-second checker "
          "re-records EVERY run")
    check("F4.cliff-by-inspection",
          201 - S == 1 and all(x == 1 for x in grid_a[(201, 0)]["per_run"][1:]),
          "201 findings against a 200-line tail: exactly one invisible, "
          "every run, forever")
    j = 0
    while 50 * j < S:
        j += 1
    check("F4.depth-arithmetic-1-50", j == 4
          and all(pr150[i] == (1 if i % 4 == 0 else 0) for i in range(80)),
          "the fire sits at depth 50j+1 after j verdict-bearing runs; "
          "invisible iff 50j >= 200 => j = 4 — matches the replayed period")

    # Arm R — seeded reporting-only traces -------------------------------------
    seeds_fix = FIX["arm_r"]["seeds"]
    r18a = arm_r_run(20261718, seeds_fix["20261718"]["N"])
    r19a = arm_r_run(20261719, seeds_fix["20261719"]["N"])
    r18b = arm_r_run(20261718, seeds_fix["20261718"]["N"])
    r19b = arm_r_run(20261719, seeds_fix["20261719"]["N"])

    check("ArmR.preview-20261718",
          list(r18a[:3]) == seeds_fix["20261718"]["preview"],
          "(leak-regime, max burst, total appends) = %s (registered "
          "[19095, 400, 21187561])" % (list(r18a[:3]),))
    check("ArmR.preview-20261719",
          list(r19a[:3]) == seeds_fix["20261719"]["preview"],
          "(leak-regime, max burst, total appends) = %s (registered "
          "[7653, 400, 8512842])" % (list(r19a[:3]),))
    check("F1.armr-draw-sentinel",
          r18a[3] == seeds_fix["20261718"]["draws"]
          and r19a[3] == seeds_fix["20261719"]["draws"],
          "exactly 4N randint draws in registered order (F, V, c, R): "
          "%d / %d (registered 80,000 / 32,000)" % (r18a[3], r19a[3]))
    check("ArmR.determinism", r18a == r18b and r19a == r19b,
          "each seed reproduced itself exactly (in-process double run per seed)")

    # presentation leg (seed 20261720, reporting-only)
    roster = sorted(["day-table", "witness-pair", "leak-row", "rotation",
                     "saturated-law", "orbit-200-1", "compounding-totals",
                     "breathing-orbit", "read-census", "repairs"])
    prng = make_rng(20261720)
    prng.shuffle(roster)
    print("  [info] presentation-shuffle (seed 20261720, reporting-only): "
          + ", ".join(roster))
    check("ArmR.presentation-seed-scoped",
          SEEDS_CONSTRUCTED == [20261718, 20261719, 20261718, 20261719, 20261720],
          "seed ledger %s — 20261720 read by the presentation leg only, after "
          "every decision and preview leg finished" % (SEEDS_CONSTRUCTED,))
    check("ArmR.aux-seed-never-read", 20261721 not in SEEDS_CONSTRUCTED,
          "seed 20261721 never constructed (no random.Random(20261721) exists "
          "in this runner)")

    # ---- decision clauses ----------------------------------------------------
    R1 = (day_replay == day_closed == A["day_table"]
          and p_law(600) == 1200 and p_law(601) == 601
          and ratio_num == 1200 and ratio_den == 601)
    R2 = (leak_row == [0, 0, 0, 0, 1, 50, 100, 200]
          and leak_row == [max(0, f - S) for f in Fgrid]
          and all(rot_first[f][1] == 2 + rot_first[f][0] for f in rot_first)
          and [rot_first[f][0] for f in (201, 250, 300, 400)] == [201, 5, 3, 2]
          and blocks == reg_blocks)
    R3 = (sat_ok
          and all(x == 199 for x in rb398["per_run"][1:])
          and len(set(rb397["per_run"][1:])) > 1
          and pr2001[:12] == [200, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
          and pr2001[1] == 1 and max(leak_phase) == 19
          and leak_phase.index(19) + 2 == 20 and tail_sum == 560
          and sum(leak_phase) == 1025
          and set(grid_a[(200, 50)]["per_run"][40:]) == {100}
          and two_cycle_ok
          and all(pr150[i] == (1 if i % 4 == 0 else 0) for i in range(80)))
    R4 = (rbre["per_run"] == expect_orbit and sum(rbre["per_run"]) == 1610
          and all(x == 1 for x in rbw["per_run"][1:])
          and rread["reads"] == 13000 and rread["parses"] == 2000
          and rbre["reads"] == 20122 and rbre["parses"] == 4600
          and sum(rsoff["per_run"][1:]) == 0)

    check("R1.renewal-non-monotonicity", R1,
          "the day table exact on all 9 cadences; p(600) = 1200 / p(601) = 601 "
          "with rate ratio exactly 1200/601")
    check("R2.cliff-plus-alibi", R2,
          "steady leak == max(0, F-200) at V = 0 with the (200, 201) margin-0 "
          "pair; rotation periods 201/5/3/2 with the F = 250 block census")
    check("R3.compounding-displacement", R3,
          "the saturated law min(F, F-200+V) exact on every qualifying cell "
          "with the (398,1)/(397,1) boundary pair; the registered compounding "
          "orbits ((200,1) peak 19 @ run 20, tail mean 14, total 1025; "
          "(200,50) -> 100/run; (250,50) -> {100,150}; (1,50) -> period 4)")
    check("R4.breathing-plus-read-bill", R4,
          "the (201,300,24) orbit total 1610 with the window-off control at "
          "1/run; read censuses 13,000/2,000 and 20,122/4,600 with the "
          "scan-off control at leak 0")

    # APPROVE condition (honestly computed, arithmetically excluded)
    shipped_zero_census = all(
        sum(grid_a[(f, v)]["per_run"][1:]) == 0 for f in Fgrid for v in Vgrid)
    monotone_non_increasing = all(
        day_replay[i] >= day_replay[i + 1] for i in range(len(day_replay) - 1))
    approve_cond = shipped_zero_census and monotone_non_increasing
    check("F6.approve-witness-excluded", not approve_cond,
          "the shipped algorithm does NOT reproduce the keyed arm's zero-leak "
          "census (the (201, 0) cell leaks 1/run) and the renewal rate is NOT "
          "monotone (73 -> 144 at the 600 -> 601 step) — APPROVE cannot fire; "
          "checked honestly")

    # gates_ok = every non-decision check so far
    gates_ok = all(ok for name, ok, _ in CHECKS
                   if not name.startswith("R") and not name.startswith("F6.approve"))

    # twin evaluators over the ENUMERATED boolean input set
    combos_agree = all(
        evaluator_one(*combo) == evaluator_two(*combo)
        for combo in itertools.product((False, True), repeat=6))
    tok1 = evaluator_one(R1, R2, R3, R4, gates_ok, approve_cond)
    tok2 = evaluator_two(R1, R2, R3, R4, gates_ok, approve_cond)
    check("F6.twin-evaluators", combos_agree and tok1 == tok2,
          "all 64 enumerated boolean inputs agree; measured inputs -> %s / %s"
          % (tok1, tok2))

    ruling = tok1

    decision_inputs = {"R1": R1, "R2": R2, "R3": R3, "R4": R4,
                       "approve_cond": approve_cond, "gates_ok": gates_ok}
    print("decision inputs: " + json.dumps(decision_inputs, sort_keys=True))
    print("RULING: %s (twin evaluators agree: %s / %s)" % (ruling, tok1, tok2))

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    print("self-checks: %d total, %d passed, %d failed"
          % (total, passed, total - passed))

    # ---- results.json ---------------------------------------------------------
    RESULTS.update({
        "verdict": ruling,
        "decision_inputs": decision_inputs,
        "clauses": {"R1": R1, "R2": R2, "R3": R3, "R4": R4},
        "self_checks": {"total": total, "passed": passed,
                        "failed": total - passed},
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in CHECKS],
        "measured": {
            "day_table_replay": day_replay,
            "day_table_closed": day_closed,
            "day_table_keyed": day_keyed,
            "witness": {"p600": p_law(600), "p601": p_law(601),
                        "rate_ratio": [1200, 601]},
            "leak_row_V0": leak_row,
            "rotation": {"first_repeat_runs": {str(f): rot_first[f][1]
                                               for f in rot_first},
                         "periods": {str(f): rot_first[f][0]
                                     for f in rot_first},
                         "F250_blocks_runs_2_4": blocks},
            "saturated_cells": sat_measured,
            "boundary_pair": {"398_1_runs_2_13": rb398["per_run"][1:13],
                              "397_1_runs_2_13": rb397["per_run"][1:13]},
            "orbit_200_1": {"per_run_80": pr2001,
                            "leak_phase_peak": max(leak_phase),
                            "peak_first_at_run": leak_phase.index(max(leak_phase)) + 2,
                            "tail_sum_runs_41_80": tail_sum,
                            "total_runs_2_80": sum(leak_phase)},
            "orbit_200_5_tail": sorted(set(grid_a[(200, 5)]["per_run"][40:])),
            "orbit_200_50_tail": sorted(set(grid_a[(200, 50)]["per_run"][40:])),
            "orbit_250_50": {"tail_runs_41_48": pr25050[40:48],
                             "total_runs_2_80": sum(pr25050[1:])},
            "orbit_1_50_append_runs_first8": [i + 1 for i, x in enumerate(pr150)
                                              if x > 0][:8],
            "compounding_totals_all20": {"%d_%d" % (f, v): totals_measured["%d_%d" % (f, v)]
                                         for (f, v) in comp_cells},
            "breathing": {"orbit": rbre["per_run"],
                          "total": sum(rbre["per_run"]),
                          "window_off_per_run": rbw["per_run"],
                          "lines_read": rbre["reads"], "parses": rbre["parses"]},
            "read_scenario": {"lines_read": rread["reads"],
                              "parses": rread["parses"],
                              "last_run_lines": last_run_lines,
                              "scan_off_leak": sum(rsoff["per_run"][1:])},
            "design_point_per_run": dp_runs,
            "controls": {"order_flip_V5_invariant": flip_reg_ok,
                         "order_flip_V1_V50_invariant": flip_extra_ok,
                         "batch_split_tail_set": sorted(set(rsplit["per_run"][40:])),
                         "one_batch_tail_set": sorted(set(grid_a[(250, 0)]["per_run"][40:])),
                         "naive_ts_per_run": rnaive["per_run"],
                         "S_prime_grid_leaks": sprime,
                         "S_prime_1001_tail": sorted(set(r1001["per_run"][40:])),
                         "keyed_zero_leak_all_cells": keyed_zero},
            "arm_r": {
                "20261718": {"leak_regime": r18a[0], "max_burst": r18a[1],
                             "total_appends": r18a[2], "draws": r18a[3]},
                "20261719": {"leak_regime": r19a[0], "max_burst": r19a[1],
                             "total_appends": r19a[2], "draws": r19a[3]},
                "seed_ledger": SEEDS_CONSTRUCTED,
            },
        },
        "environment": {"cpython_minor": pyminor,
                        "decision_arms": "seedless exact integer arithmetic "
                                         "(platform-independent)"},
    })
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as out:
        json.dump(RESULTS, out, indent=1, sort_keys=True)
        out.write("\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
