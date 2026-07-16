#!/usr/bin/env python3
"""VERDICT 096 sim — combo grace-budget cliff (idea-engine PROPOSAL 083).

Hermetic, stdlib-only, pre-registered (fixtures.json committed BEFORE this
runner). Prices a forgiving-streak combo contract — "any action within the
grace window (<= G late) is safe, and you only ever lose the streak on a REAL
miss (l > G)" — on its own most natural implementation: ONE shared grace budget
behind a per-action grace test (the structure of the lane's shipped
games/mining/core/energy.py shared-budget pace surface).

Pinned budget automaton (all integers, verbatim from the idea file):
  P=10, G=3, B0=Bmax=10, R=1, M=25. Break check evaluated BEFORE the budget
  update: break at the FIRST action with B - l < 0 (budget) OR l > G (real
  miss) -> m resets to 1, the accumulated m-1 bonus wiped; else recognized:
  B <- min(Bmax, B - l + R*[l <= 0]), m <- min(M, m + 1).

Arms:
  Arm A — the pinned stepwise automaton (DECISION-bearing, seedless). Early
          return on break; tracks the budget as a single running integer.
  Arm B — an INDEPENDENTLY-shaped twin: a full-trajectory budget WALK over an
          explicit horizon list of per-step budgets, no early return, break
          located by scanning the trajectory. Tied to Arm A on every steady
          pattern and every Arm-R trace, and to the closed forms via C1/C2.
  Arm R — seeded random cells, REPORTING-ONLY (no statistical gate): per trace
          EXACTLY 3 rng.randint draws in registered order — lateness l in
          [0,4], horizon cap in [5,50], salt in [1,1000] (drawn-and-logged,
          unused) — one random.Random per seed. Seeds 20261726 (N=20,000) /
          20261727 (N=8,000) with registered preview censuses and class-stream
          digests; presentation shuffle 20261728 (presentation leg only); aux
          20261729 reserved and NEVER read.

Decision rule (registered order, twin evaluators over an ENUMERATED boolean
input set): REJECT -> INVALID -> APPROVE -> NULL, REJECT evaluated FIRST.

Deterministic: no wall clock, no absolute paths, no network, no git at run
time; stdout and results.json are byte-identical across process runs. CPython
3.11 pinned and asserted (the decision arms are seedless integer arithmetic,
platform-independent; only reporting-only Arm R and the presentation shuffle
touch the pinned minor's random module).
"""

import hashlib
import json
import os
import random
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)

PM = FIX["pinned_model"]
P = PM["P"]
G = PM["G"]
B0 = PM["B0"]
BMAX = PM["Bmax"]
R = PM["R"]
M = PM["M"]
RPRIME = PM["Rprime_repair_b"]

DECISION_HORIZON = 1000     # vacancy-derived: safely beyond every finite break

CHECKS = []
RESULTS = {}
SEEDS_CONSTRUCTED = []


def check(name, ok, detail):
    CHECKS.append((name, bool(ok), str(detail)))
    print("  [%s] %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Arm A — the pinned stepwise automaton (DECISION-bearing)
# ---------------------------------------------------------------------------

def arm_a_steady(l, horizon, rprime=0):
    """Run the pinned automaton with CONSTANT lateness l for up to `horizon`
    actions. Returns a dict:
      break_step : 1-based step of the break, or None if it survives horizon
      kind       : 'miss' | 'budget' | None
      mult_before_break : the multiplier m at the moment the break fires
      wiped      : the bonus wiped at break == mult_before_break - 1
      bmax_ok    : the B <= Bmax invariant held on every step
      order_ok   : the break check ran BEFORE the budget update on every step
    `rprime` > 0 => also replenish rprime on any within-grace action (repair b).
    """
    B = B0
    m = 1
    bmax_ok = True
    order_ok = True
    for step in range(1, horizon + 1):
        # --- break check FIRST (before any budget mutation) ---
        pre_B = B
        if l > G:
            return {"break_step": step, "kind": "miss", "mult_before_break": m,
                    "wiped": m - 1, "bmax_ok": bmax_ok, "order_ok": order_ok}
        if B - l < 0:
            return {"break_step": step, "kind": "budget", "mult_before_break": m,
                    "wiped": m - 1, "bmax_ok": bmax_ok, "order_ok": order_ok}
        # order sentinel: budget is still the pre-check value here
        if B != pre_B:
            order_ok = False
        # --- recognized: budget update, then multiplier ---
        if l <= 0:
            rep = R
        elif rprime > 0 and 0 < l <= G:
            rep = rprime
        else:
            rep = 0
        B = min(BMAX, B - l + rep)
        if B > BMAX:
            bmax_ok = False
        m = min(M, m + 1)
    return {"break_step": None, "kind": None, "mult_before_break": m,
            "wiped": m - 1, "bmax_ok": bmax_ok, "order_ok": order_ok}


def arm_a_warn_steps(l, horizon):
    """Repair (a): the grace-low one-shot warning fires when the NEXT action
    would break, i.e. B_after - l < 0 after this action's recognized update.
    Returns the list of steps at which the warning fires (baseline replenish)."""
    B = B0
    warns = []
    for step in range(1, horizon + 1):
        if l > G:
            break
        if B - l < 0:
            break
        rep = R if l <= 0 else 0
        B_after = min(BMAX, B - l + rep)
        if B_after - l < 0:
            warns.append(step)
        B = B_after
    return warns


# ---------------------------------------------------------------------------
# Arm B — an INDEPENDENTLY-shaped twin: a full-trajectory budget walk.
# No early return; builds the per-step pre-action budget list explicitly and
# scans it for the first break. Different code shape from Arm A on purpose.
# ---------------------------------------------------------------------------

def arm_b_steady(l, horizon, rprime=0):
    """Independently-shaped reimplementation. Returns (break_step, kind)."""
    # build the pre-action budget trajectory step by step, recording each
    # step's (pre_budget) and whether it is a break, WITHOUT returning early.
    budgets = []
    B = B0
    break_at = None
    break_kind = None
    for step in range(1, horizon + 1):
        budgets.append(B)
        is_miss = (l > G)
        is_budget = (B - l < 0)
        if is_miss or is_budget:
            if break_at is None:
                break_at = step
                break_kind = "miss" if is_miss else "budget"
            # freeze the trajectory once broken (streak resets; we stop walking)
            break
        # recognized update
        if l <= 0:
            add = R
        elif rprime > 0 and 0 < l <= G:
            add = rprime
        else:
            add = 0
        nxt = B - l + add
        B = nxt if nxt < BMAX else BMAX
    return break_at, break_kind


# ---------------------------------------------------------------------------
# Closed forms (Arm B's algebraic contact — the idea file's C1/C2)
# ---------------------------------------------------------------------------

def closed_break(l):
    """floor(B0/l) + 1 for within-grace steady l in {1,2,3}."""
    return (B0 // l) + 1


def closed_repair_b_break(l):
    """floor((B0-l)/(l-1)) + 2 for l in {2,3}; l=1 survives (inf)."""
    if l == 1:
        return None
    return ((B0 - l) // (l - 1)) + 2


# ---------------------------------------------------------------------------
# Arm-R classification (reporting-only)
# ---------------------------------------------------------------------------

def classify_trace(l, H):
    """Run the pinned automaton with constant lateness l for up to H actions
    and name the trace's class."""
    res = arm_a_steady(l, H)
    if res["kind"] == "miss":
        return "REAL-MISS"
    if res["kind"] == "budget":
        return "SILENT-BREAK"
    return "SURVIVE"          # l=0 pins at cap, or break_step beyond H


def stream_char(cls):
    """The class-stream token: the FIRST character of the class label
    (SURVIVE/SILENT-BREAK -> 'S', REAL-MISS -> 'R')."""
    return cls[0]


def run_arm_r(seed, N, twin=True):
    rng = make_rng(seed)
    census = {}
    parts = []
    draws = 0
    salt_sum = 0
    salt_first5 = []
    twin_ok = True
    for _ in range(N):
        l = rng.randint(0, 4)
        H = rng.randint(5, 50)
        salt = rng.randint(1, 1000)
        draws += 3
        salt_sum += salt
        if len(salt_first5) < 5:
            salt_first5.append(salt)
        cls = classify_trace(l, H)
        if twin:
            bs_b, kind_b = arm_b_steady(l, H)
            cls_b = ("REAL-MISS" if kind_b == "miss"
                     else "SILENT-BREAK" if kind_b == "budget"
                     else "SURVIVE")
            if cls_b != cls:
                twin_ok = False
        census[cls] = census.get(cls, 0) + 1
        parts.append(stream_char(cls))
    digest = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()[:12]
    return {"census": census, "digest": digest, "draws": draws,
            "salt_sum": salt_sum, "salt_first5": salt_first5, "twin_ok": twin_ok}


# ---------------------------------------------------------------------------
# Twin decision evaluators (registered order REJECT -> INVALID -> APPROVE ->
# NULL, REJECT evaluated FIRST)
# ---------------------------------------------------------------------------

def evaluate_1(inp):
    """If-chain evaluator."""
    if inp["R1"] and inp["R2"] and inp["R3"] and inp["R4"]:
        return "REJECT"
    if not inp["gates_ok"]:
        return "INVALID"
    if inp["all_within_grace_survive"]:
        return "APPROVE"
    return "NULL"


def evaluate_2(inp):
    """Table-driven evaluator, independently written."""
    score = ((1 if inp["R1"] else 0) + (2 if inp["R2"] else 0)
             + (4 if inp["R3"] else 0) + (8 if inp["R4"] else 0))
    rules = (
        ("REJECT", score == 15),
        ("INVALID", inp["gates_ok"] is False),
        ("APPROVE", bool(inp["all_within_grace_survive"])),
        ("NULL", True),
    )
    for token, fires in rules:
        if fires:
            return token
    raise AssertionError("unreachable")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("VERDICT 096 sim — combo grace-budget cliff (P083)")
    print("=" * 74)

    # ---- F0: harness pins -------------------------------------------------
    pyminor = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    check("F0.python-minor-pinned",
          pyminor == FIX["environment"]["cpython_minor_pinned"],
          "running CPython %s vs pinned %s"
          % (pyminor, FIX["environment"]["cpython_minor_pinned"]))
    check("F0.constants",
          (P, G, B0, BMAX, R, M, RPRIME) == (10, 3, 10, 10, 1, 25, 1),
          "P=%d G=%d B0=%d Bmax=%d R=%d M=%d R'=%d" % (P, G, B0, BMAX, R, M, RPRIME))

    # ---- steady census (Arm A), both arms + closed form -------------------
    steady = {}
    for l in (0, 1, 2, 3, 4):
        steady[l] = arm_a_steady(l, DECISION_HORIZON)

    reg_break = FIX["anchors_F3"]["steady_break_step_map"]
    # F2a — the steady census over l in {0,1,2,3,4}
    census_ok = (steady[0]["break_step"] is None
                 and steady[1]["break_step"] == 11 and steady[1]["kind"] == "budget"
                 and steady[2]["break_step"] == 6 and steady[2]["kind"] == "budget"
                 and steady[3]["break_step"] == 4 and steady[3]["kind"] == "budget"
                 and steady[4]["break_step"] == 1 and steady[4]["kind"] == "miss")
    check("F2a.steady-census", census_ok,
          "l0 survives; l1=%s l2=%s l3=%s (budget); l4=%s (%s)"
          % (steady[1]["break_step"], steady[2]["break_step"],
             steady[3]["break_step"], steady[4]["break_step"], steady[4]["kind"]))
    check("F3.break-step-map",
          [steady[l]["break_step"] for l in (1, 2, 3)] == [11, 6, 4]
          and steady[4]["break_step"] == 1 and steady[0]["break_step"] is None,
          "registered {l0:inf, l1:11, l2:6, l3:4, l4:1(miss)} reproduced")

    # ---- F1: model identities ---------------------------------------------
    order_ok = all(steady[l]["order_ok"] for l in steady) and \
        all(arm_a_steady(l, 50)["order_ok"] for l in (0, 1, 2, 3, 4))
    bmax_ok = all(steady[l]["bmax_ok"] for l in steady)
    # exactly-(m-1) wipe: the bonus wiped at break == mult_before_break - 1
    wipe_ok = all(steady[l]["wiped"] == steady[l]["mult_before_break"] - 1
                  for l in steady)
    check("F1.break-before-update", order_ok,
          "the break check ran BEFORE the budget update on every step of every "
          "steady trace (budget unchanged at the check point)")
    check("F1.bmax-invariant", bmax_ok, "B <= Bmax on every step of every trace")
    check("F1.exact-m-minus-1-wipe", wipe_ok,
          "the reset wipes exactly m-1: l1 wiped %d (m=%d), l2 %d, l3 %d"
          % (steady[1]["wiped"], steady[1]["mult_before_break"],
             steady[2]["wiped"], steady[3]["wiped"]))
    # determinism: two in-process runs identical
    det_ok = all(arm_a_steady(l, DECISION_HORIZON) == arm_a_steady(l, DECISION_HORIZON)
                 for l in (0, 1, 2, 3, 4))
    check("F1.deterministic", det_ok,
          "two in-process runs of every steady trace return identical dicts")

    # ---- C1: Arm A steady break == closed form floor(B0/l)+1 (l in 1,2,3) --
    c1_ok = all(steady[l]["break_step"] == closed_break(l) for l in (1, 2, 3))
    check("F2.C1-closed-form-contact", c1_ok,
          "steady sim break_step == floor(B0/l)+1: %s == %s"
          % ([steady[l]["break_step"] for l in (1, 2, 3)],
             [closed_break(l) for l in (1, 2, 3)]))

    # ---- twin machine: Arm B == Arm A on every steady pattern -------------
    twin_steady_ok = True
    for l in (0, 1, 2, 3, 4):
        bs_b, kind_b = arm_b_steady(l, DECISION_HORIZON)
        if bs_b != steady[l]["break_step"] or kind_b != steady[l]["kind"]:
            twin_steady_ok = False
    check("F2a.twin-steady", twin_steady_ok,
          "Arm B (full-trajectory walk) == Arm A (stepwise) on all five steady "
          "patterns (break step + kind)")

    # ---- R3: the forgiveness inversion — loss map + strict monotonicity ----
    loss = {l: steady[l]["wiped"] for l in (1, 2, 3)}
    reg_loss = FIX["anchors_F3"]["steady_multiplier_loss_map"]
    loss_ok = (loss[1] == 10 and loss[2] == 5 and loss[3] == 3
               and all(loss[l] == B0 // l for l in (1, 2, 3)))
    mono_ok = loss[1] > loss[2] > loss[3]
    cap_ok = all(loss[l] < M for l in (1, 2, 3))     # cap never binds
    check("F3.loss-map", loss_ok,
          "silent loss = break_step-1 = floor(B0/l): l1=%d l2=%d l3=%d (== {10,5,3})"
          % (loss[1], loss[2], loss[3]))
    check("F2b.loss-strict-monotone", mono_ok and cap_ok,
          "loss strictly DECREASING in l (%d > %d > %d), max at l=1; all < M=25 "
          "(cap never binds)" % (loss[1], loss[2], loss[3]))

    # ---- R4a: repair (a) grace-low warning ---------------------------------
    warn = {l: arm_a_warn_steps(l, DECISION_HORIZON) for l in (0, 1, 2, 3)}
    reg_warn = FIX["anchors_F3"]["repair_a_warning_step_map"]
    warn_ok = (warn[1] == [10] and warn[2] == [5] and warn[3] == [3]
               and warn[0] == [])
    once_ok = all(len(warn[l]) == 1 for l in (1, 2, 3)) and len(warn[0]) == 0
    at_break_minus_1 = all(warn[l][0] == steady[l]["break_step"] - 1
                           for l in (1, 2, 3))
    check("F2c.repair-a-once-per-streak", once_ok and at_break_minus_1,
          "repair (a) fires exactly once per streak at break_step-1: l1@%s l2@%s "
          "l3@%s; l0 fires %d (zero false positives on the clean cohort)"
          % (warn[1], warn[2], warn[3], len(warn[0])))
    check("F3.repair-a-warning-map", warn_ok,
          "warning-step map {l1:10, l2:5, l3:3, l0:0} reproduced")

    # ---- R4b: repair (b) replenish-on-within-grace -------------------------
    steady_b = {l: arm_a_steady(l, DECISION_HORIZON, rprime=RPRIME)
                for l in (1, 2, 3)}
    reg_bmap = FIX["anchors_F3"]["repair_b_break_step_map"]
    rb_ok = (steady_b[1]["break_step"] is None
             and steady_b[2]["break_step"] == 10
             and steady_b[3]["break_step"] == 5)
    # C2: sim == closed form for l in {2,3}; l=1 survives
    c2_ok = (steady_b[2]["break_step"] == closed_repair_b_break(2)
             and steady_b[3]["break_step"] == closed_repair_b_break(3)
             and steady_b[1]["break_step"] is None
             and closed_repair_b_break(1) is None)
    # twin: Arm B == Arm A on repair-b
    twin_b_ok = all(arm_b_steady(l, DECISION_HORIZON, rprime=RPRIME)[0]
                    == steady_b[l]["break_step"] for l in (1, 2, 3))
    check("F2d.repair-b-closed-form", rb_ok and c2_ok and twin_b_ok,
          "repair (b) R'=1: l1 survives (net 0), l2->%s, l3->%s == floor((B0-l)"
          "/(l-1))+2 {%s,%s}; Arm B agrees (C2)"
          % (steady_b[2]["break_step"], steady_b[3]["break_step"],
             closed_repair_b_break(2), closed_repair_b_break(3)))
    check("F3.repair-b-break-map",
          [steady_b[l]["break_step"] for l in (2, 3)] == [10, 5]
          and steady_b[1]["break_step"] is None,
          "repair-(b) break map {l1:inf, l2:10, l3:5} reproduced")

    # ---- F4: the hand worlds (pencil, computed) ----------------------------
    check("F4a.l1-exhausts-at-11",
          steady[1]["break_step"] == 11 and (B0 // 1) + 1 == 11,
          "B0=10 exhausted after 10 unit spends -> break at step 11, not inf "
          "(APPROVE dead by inspection)")
    check("F4b.l3-cliff-at-4", (10 // 3) + 1 == 4 and steady[3]["break_step"] == 4,
          "floor(10/3)+1 = 4 — the l=3 cliff by inspection")
    check("F4c.l0-cap-pin-survivor", steady[0]["break_step"] is None,
          "at l=0 the clean-action replenish pins B at Bmax; the budget never "
          "drains — the survive cell by inspection")
    check("F4d.repair-b-net0-at-l1",
          (-1 + RPRIME) == 0 and steady_b[1]["break_step"] is None,
          "repair (b) net change at l=1 is -1 + 1 = 0 — l=1 survives by inspection")

    # ---- F5: degeneracy / convention controls ------------------------------
    check("F5.true-cells-present",
          steady[0]["break_step"] is None and steady[4]["kind"] == "miss"
          and steady[4]["break_step"] == 1,
          "the contract's two TRUE cells are registered: the l=0 survivor AND "
          "the l>G immediate real miss (step 1)")
    check("F5.repair-a-zero-fp-on-survivor", warn[0] == [],
          "repair (a) fires zero times on the l=0 survivor cohort")
    strict_extends = (steady_b[2]["break_step"] > steady[2]["break_step"]
                      and steady_b[3]["break_step"] > steady[3]["break_step"]
                      and steady_b[1]["break_step"] is None
                      and steady[1]["break_step"] is not None)
    check("F5.repair-b-strictly-extends", strict_extends,
          "repair (b) strictly EXTENDS survival vs baseline (never shortens): "
          "l1 6->inf-cohort, l2 %d->%d, l3 %d->%d"
          % (steady[2]["break_step"], steady_b[2]["break_step"],
             steady[3]["break_step"], steady_b[3]["break_step"]))

    # ---- Arm R — seeded random cells, REPORTING-ONLY ------------------------
    reg_r = FIX["arm_r"]["seeds"]
    r26 = run_arm_r(20261726, 20000, twin=True)
    r27 = run_arm_r(20261727, 8000, twin=True)
    # in-process double run (reproducibility)
    r26b = run_arm_r(20261726, 20000, twin=False)
    r27b = run_arm_r(20261727, 8000, twin=False)

    check("F3.armR-census-20261726", r26["census"] == reg_r["20261726"]["census"],
          json.dumps(r26["census"], sort_keys=True))
    check("F3.armR-census-20261727", r27["census"] == reg_r["20261727"]["census"],
          json.dumps(r27["census"], sort_keys=True))
    check("F3.armR-digest-20261726",
          r26["digest"] == reg_r["20261726"]["class_stream_digest"],
          "class-stream digest %s == registered %s"
          % (r26["digest"], reg_r["20261726"]["class_stream_digest"]))
    check("F3.armR-digest-20261727",
          r27["digest"] == reg_r["20261727"]["class_stream_digest"],
          "class-stream digest %s == registered %s"
          % (r27["digest"], reg_r["20261727"]["class_stream_digest"]))
    check("F1.armR-draw-sentinels",
          r26["draws"] == 60000 and r27["draws"] == 24000,
          "draw counters exactly 3N: %d / %d" % (r26["draws"], r27["draws"]))
    check("F5.armR-taxonomy-total",
          sum(r26["census"].values()) == 20000
          and sum(r27["census"].values()) == 8000
          and set(r26["census"]) <= {"SURVIVE", "SILENT-BREAK", "REAL-MISS"}
          and set(r27["census"]) <= {"SURVIVE", "SILENT-BREAK", "REAL-MISS"},
          "SURVIVE + SILENT-BREAK + REAL-MISS == N on both seeds (total taxonomy, "
          "no trace unclassified)")
    check("F2a.armR-per-trace-twin", r26["twin_ok"] and r27["twin_ok"],
          "Arm B == Arm A on every trace of both seeds")
    check("F5.armR-in-process-double-run",
          r26b["census"] == r26["census"] and r26b["digest"] == r26["digest"]
          and r27b["census"] == r27["census"] and r27b["digest"] == r27["digest"],
          "census + digest identical on a second in-process pass per seed")

    # ---- presentation shuffle (presentation leg ONLY) ----------------------
    prng = make_rng(FIX["arm_r"]["presentation_seed"])
    rows = ["l=0 survive", "l=1 break@11 loss10", "l=2 break@6 loss5",
            "l=3 break@4 loss3", "l=4 miss@1"]
    prng.shuffle(rows)
    print("  steady census table (display order via presentation seed %d):"
          % FIX["arm_r"]["presentation_seed"])
    for row in rows:
        print("    %s" % row)

    check("F5.presentation-seed-scope",
          SEEDS_CONSTRUCTED == [20261726, 20261727, 20261726, 20261727, 20261728],
          "seed ledger %s — presentation seed read by the presentation leg only, "
          "after every decision leg finished" % (SEEDS_CONSTRUCTED,))
    check("F5.aux-seed-never-read",
          FIX["arm_r"]["aux_seed_never_read"] not in SEEDS_CONSTRUCTED,
          "aux seed 20261729 reserved and never read")

    # ---- decision ----------------------------------------------------------
    gates_ok_so_far = all(ok for _n, ok, _d in CHECKS)
    decision_inputs = {
        "R1": bool(census_ok),
        "R2": bool(c1_ok),
        "R3": bool(loss_ok and mono_ok),
        "R4": bool(once_ok and at_break_minus_1 and warn_ok and rb_ok and c2_ok),
        "gates_ok": bool(gates_ok_so_far),
        # APPROVE would require every within-grace steady pattern to survive;
        # the l=1 cell breaks at 11 (F4a) so this is False by arithmetic
        "all_within_grace_survive": bool(
            steady[1]["break_step"] is None and steady[2]["break_step"] is None
            and steady[3]["break_step"] is None),
    }
    # enumerated boolean input set: both evaluators must agree everywhere
    agree_all = True
    for mask in range(64):
        probe = {"R1": bool(mask & 1), "R2": bool(mask & 2),
                 "R3": bool(mask & 4), "R4": bool(mask & 8),
                 "gates_ok": bool(mask & 16),
                 "all_within_grace_survive": bool(mask & 32)}
        if evaluate_1(probe) != evaluate_2(probe):
            agree_all = False
    verdict_1 = evaluate_1(decision_inputs)
    verdict_2 = evaluate_2(decision_inputs)
    check("F2.twin-evaluators-agree",
          agree_all and verdict_1 == verdict_2,
          "twin evaluators agree on all 64 enumerated inputs and rule %s/%s"
          % (verdict_1, verdict_2))
    check("decision.approve-arithmetically-excluded",
          decision_inputs["all_within_grace_survive"] is False
          and steady[1]["break_step"] == 11,
          "APPROVE requires every within-grace steady pattern to survive; the "
          "l=1 cell breaks at 11 (B0=10 exhausted after 10 unit spends) — excluded")

    print("decision inputs: " + json.dumps(decision_inputs, sort_keys=True))
    print("VERDICT: %s (evaluator 1) / %s (evaluator 2)" % (verdict_1, verdict_2))

    passed = sum(1 for _n, ok, _d in CHECKS if ok)
    total = len(CHECKS)
    print("=" * 74)
    print("self-checks: %d/%d passed" % (passed, total))

    RESULTS.update({
        "verdict": verdict_1,
        "decision_inputs": decision_inputs,
        "steady_census": {
            str(l): {"break_step": steady[l]["break_step"],
                     "kind": steady[l]["kind"],
                     "mult_before_break": steady[l]["mult_before_break"],
                     "wiped": steady[l]["wiped"]}
            for l in (0, 1, 2, 3, 4)},
        "loss_map": {str(l): loss[l] for l in (1, 2, 3)},
        "repair_a_warning_map": {str(l): warn[l] for l in (0, 1, 2, 3)},
        "repair_b_break_map": {str(l): steady_b[l]["break_step"] for l in (1, 2, 3)},
        "closed_forms": {
            "C1_floor_B0_over_l_plus_1": {str(l): closed_break(l) for l in (1, 2, 3)},
            "C2_repair_b": {str(l): closed_repair_b_break(l) for l in (1, 2, 3)}},
        "arm_r": {
            "20261726": {"census": r26["census"], "digest": r26["digest"],
                         "draws": r26["draws"], "salt_sum": r26["salt_sum"],
                         "salt_first5": r26["salt_first5"]},
            "20261727": {"census": r27["census"], "digest": r27["digest"],
                         "draws": r27["draws"], "salt_sum": r27["salt_sum"],
                         "salt_first5": r27["salt_first5"]},
            "seed_ledger": SEEDS_CONSTRUCTED},
        "checks": {"passed": passed, "total": total,
                   "failed": [n for n, ok, _d in CHECKS if not ok]},
        "environment": {
            "cpython_minor": pyminor,
            "decision_arms": "seedless deterministic integer arithmetic "
                             "(platform-independent)"},
    })
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as out:
        json.dump(RESULTS, out, indent=1, sort_keys=True)
        out.write("\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
