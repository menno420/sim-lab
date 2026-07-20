#!/usr/bin/env python3
"""Weitzman's Pandora's Box: the optimal search order IGNORES expected rewards.

In sequential search with costly inspection (Weitzman 1979), you face N closed
boxes. Box i costs c_i to open; opening it reveals a reward R_i drawn from a known
discrete distribution. You open boxes one at a time (paying each cost) and may stop
at any moment and collect the single best reward seen so far (outside option 0). No
discounting. The optimal policy does NOT open boxes in decreasing order of expected
reward. It assigns each box a RESERVATION VALUE z_i solving

        c_i = E[(R_i - z_i)^+]

and opens boxes in decreasing order of z_i, stopping the moment the best reward in
hand is >= the largest reservation value among the still-closed boxes. Three
counterintuitive-but-exactly-true consequences:

  (a) you can rationally DECLINE to open a box whose EXPECTED prize exceeds every
      value you already hold (a low-z box is skipped though its mean beats best);
  (b) a LOWER-MEAN, HIGHER-SPREAD box can be optimal to open FIRST (z rewards
      upside-relative-to-cost, not the mean);
  (c) the index-rule expected value EXACTLY equals the brute-force optimum over ALL
      policies (Weitzman's theorem) — the simple index rule leaves nothing on the
      table.

This verifier is stdlib only (random, fractions.Fraction, hashlib, json, itertools).
ALL gate math on the reservation values and the exact-vs-index agreement is done in
fractions.Fraction — ZERO floating point in that math. Only the surprise-gate
z-score (which needs a square root) touches float, and it is rounded to a fixed
precision for byte-stable serialization.

Determinism: SEED pinned; a fresh random.Random(SEED) is created at the start of
EACH full run, so an in-process double-run AND a separate cross-invocation both
reproduce byte-identical output.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the compact-canonical
results dict's own sha256 IS the digest; it is not a field inside the dict.
"""
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction

SEED = 20260717
N_BOXES = 4             # boxes per instance
M_INSTANCES = 400       # random instances per regime
Z_GATE = 3.0            # surprise-gate sigma bar
ROUND_DP = 10           # fixed float serialization precision (surprise z only)


# --------------------------------------------------------------------------- #
# Reward distribution helpers (all exact Fraction).                           #
# --------------------------------------------------------------------------- #
def box_mean(box):
    """E[R_i] as an exact Fraction."""
    return sum(p * v for v, p in box["support"])


def reservation_value(box):
    """Solve c = E[(R - z)^+] for z as an exact Fraction.

    E(z) = sum_v p_v * max(v - z, 0) is continuous, piecewise-linear and strictly
    decreasing in z on (-inf, v_max]; it equals 0 at z = v_max and rises to +inf as
    z -> -inf, so for any cost c > 0 there is a unique root z < v_max. On the segment
    where exactly the top t support values exceed z, E(z) = A_t - z*B_t with
    A_t = sum_{top t} p*v and B_t = sum_{top t} p; scan t upward and return the first
    root that lands inside its segment. Everything is exact rational arithmetic.
    """
    c = box["cost"]
    supp = sorted(box["support"], key=lambda vp: vp[0])   # ascending by value
    vals = [v for v, _ in supp]
    probs = [p for _, p in supp]
    m = len(vals)
    # t = number of support values strictly greater than z, scanned 1..m.
    for t in range(1, m + 1):
        active = list(range(m - t, m))                    # indices of the top t
        A = sum(probs[j] * vals[j] for j in active)
        B = sum(probs[j] for j in active)                 # B > 0 for t >= 1
        z = (A - c) / B                                   # exact Fraction
        upper = vals[m - t]                               # smallest active value
        lower_ok = (t == m) or (z >= vals[m - t - 1])
        if z < upper and lower_ok:
            # Exactness assert: reconstruct E[(R - z)^+] and demand c EXACTLY.
            e = sum(p * max(v - z, Fraction(0)) for v, p in supp)
            assert e == c, f"reservation solve not exact: E={e} c={c}"
            return z
    raise AssertionError("no reservation root found (should be impossible for c>0)")


# --------------------------------------------------------------------------- #
# Exact policy evaluators over the search tree (memoized, exact Fraction).     #
# opened is a frozenset of box indices; best is the best reward in hand.       #
# --------------------------------------------------------------------------- #
def optimal_value(boxes):
    """Brute-force optimum V(opened,best) = max(stop->best, or for each unopened i:
    -c_i + E_{R_i}[V(opened+{i}, max(best,R_i))]) over ALL policies. Exact."""
    n = len(boxes)
    memo = {}

    def V(opened, best):
        key = (opened, best)
        if key in memo:
            return memo[key]
        val = best                                        # stop and take best
        for i in range(n):
            if i in opened:
                continue
            c = boxes[i]["cost"]
            exp = Fraction(0)
            for r, p in boxes[i]["support"]:
                exp += p * V(opened | {i}, max(best, r))
            val = max(val, -c + exp)
        memo[key] = val
        return val

    return V(frozenset(), Fraction(0))


def _argmax_index(boxes, unopened, key):
    """Index in `unopened` maximizing key(box); ties -> smallest index."""
    best_i = None
    best_k = None
    for i in sorted(unopened):
        k = key(boxes[i])
        if best_k is None or k > best_k:
            best_k = k
            best_i = i
    return best_i, best_k


def index_policy_value(boxes, zvals):
    """Same recursion, action FORCED to Weitzman's rule: if best < max remaining z,
    open the unopened box of maximal z; else stop. Exact Fraction."""
    n = len(boxes)
    memo = {}

    def V(opened, best):
        key = (opened, best)
        if key in memo:
            return memo[key]
        unopened = [i for i in range(n) if i not in opened]
        if not unopened:
            memo[key] = best
            return best
        i, maxz = _argmax_index(boxes, unopened, lambda b: zvals[b["_id"]])
        if best >= maxz:                                  # stopping rule
            memo[key] = best
            return best
        c = boxes[i]["cost"]
        exp = Fraction(0)
        for r, p in boxes[i]["support"]:
            exp += p * V(opened | {i}, max(best, r))
        memo[key] = -c + exp
        return memo[key]

    return V(frozenset(), Fraction(0))


def greedy_mean_value(boxes):
    """Same recursion, action FORCED to the mean-greedy heuristic: if best < max
    remaining E[R], open the unopened box of maximal E[R]; else stop. Exact."""
    n = len(boxes)
    means = [box_mean(b) for b in boxes]
    memo = {}

    def V(opened, best):
        key = (opened, best)
        if key in memo:
            return memo[key]
        unopened = [i for i in range(n) if i not in opened]
        if not unopened:
            memo[key] = best
            return best
        i, maxmean = _argmax_index(boxes, unopened, lambda b: means[b["_id"]])
        if best >= maxmean:                               # heuristic stopping rule
            memo[key] = best
            return best
        c = boxes[i]["cost"]
        exp = Fraction(0)
        for r, p in boxes[i]["support"]:
            exp += p * V(opened | {i}, max(best, r))
        memo[key] = -c + exp
        return memo[key]

    return V(frozenset(), Fraction(0))


# --------------------------------------------------------------------------- #
# Instance generation (seeded, small rational instances).                     #
# --------------------------------------------------------------------------- #
def gen_instance(rng):
    """One random N_BOXES instance: each box a small discrete reward on 0..10 with
    rational weights and a small positive rational opening cost."""
    boxes = []
    for bid in range(N_BOXES):
        m = rng.choice([2, 3])
        vals = sorted(rng.sample(range(0, 11), m))        # distinct ints 0..10
        weights = [rng.randint(1, 4) for _ in range(m)]
        tot = sum(weights)
        support = [(v, Fraction(w, tot)) for v, w in zip(vals, weights)]
        cost = Fraction(rng.randint(1, 5), rng.choice([1, 2]))  # 0.5 .. 5
        boxes.append({"_id": bid, "cost": cost, "support": support})
    return boxes


def scale_costs(boxes, factor):
    """Return a copy of an instance with every opening cost multiplied by factor."""
    return [
        {"_id": b["_id"], "cost": b["cost"] * factor, "support": list(b["support"])}
        for b in boxes
    ]


def instance_repr(boxes, zvals):
    """Serializable, exact description of one instance (for the witness dump)."""
    return {
        "boxes": [
            {
                "id": b["_id"],
                "cost": str(b["cost"]),
                "support": [[v, str(p)] for v, p in b["support"]],
                "mean": str(box_mean(b)),
                "reservation_z": str(zvals[b["_id"]]),
            }
            for b in boxes
        ]
    }


# --------------------------------------------------------------------------- #
# One regime = M instances put through all four evaluators.                   #
# --------------------------------------------------------------------------- #
def run_regime(rng, cost_factor):
    """Generate M instances (optionally cost-scaled) and evaluate every policy.

    Returns per-regime aggregates: exact-agreement mismatch count, the regret
    distribution (optimal - greedy), non-monotonicity counts, and a concrete
    witness of the optimum opening a lower-mean box first / declining a higher-mean
    box.
    """
    mismatch_count = 0
    regrets = []                                          # exact Fraction per instance
    n_positive = 0
    z_order_ne_mean_order = 0
    lower_mean_first = 0
    decline_higher_mean = 0
    witness = None

    for _ in range(M_INSTANCES):
        base = gen_instance(rng)
        boxes = scale_costs(base, cost_factor) if cost_factor != 1 else base
        zvals = {b["_id"]: reservation_value(b) for b in boxes}
        means = {b["_id"]: box_mean(b) for b in boxes}

        opt = optimal_value(boxes)
        idx = index_policy_value(boxes, zvals)
        grd = greedy_mean_value(boxes)

        if idx != opt:                                    # EXACT gate: exact Fraction
            mismatch_count += 1
        regret = opt - grd
        assert regret >= 0, f"greedy beat the optimum: regret={regret}"
        regrets.append(regret)
        if regret > 0:
            n_positive += 1

        # Non-monotonicity: does the reservation ordering differ from the mean order?
        z_order = sorted(range(N_BOXES), key=lambda i: (-zvals[i], i))
        mean_order = sorted(range(N_BOXES), key=lambda i: (-means[i], i))
        if z_order != mean_order:
            z_order_ne_mean_order += 1

        # (b) the optimum opens the max-z box FIRST (best=0 < max z); is that box a
        #     strictly-lower-mean box than the max-mean box?
        first_open = z_order[0]
        top_mean_box = mean_order[0]
        opens_first = zvals[first_open] > 0               # otherwise nothing is opened
        if opens_first and means[first_open] < means[top_mean_box]:
            lower_mean_first += 1
            if witness is None:
                witness = {
                    "instance": instance_repr(boxes, zvals),
                    "first_opened_box_by_z": first_open,
                    "first_opened_mean": str(means[first_open]),
                    "highest_mean_box": top_mean_box,
                    "highest_mean": str(means[top_mean_box]),
                    "optimal_value": str(opt),
                    "greedy_mean_value": str(grd),
                    "index_value": str(idx),
                    "note": "optimum opens box %d (mean %s, z %s) BEFORE the higher-"
                            "mean box %d (mean %s, z %s)" % (
                                first_open, str(means[first_open]),
                                str(zvals[first_open]), top_mean_box,
                                str(means[top_mean_box]), str(zvals[top_mean_box])),
                }

        # (a) does the index-optimal policy STOP at any reachable state while an
        #     unopened box still has E[R] > best in hand? (declining a higher-mean
        #     box). Enumerate reachable states under the index policy.
        if _index_policy_declines_higher_mean(boxes, zvals, means):
            decline_higher_mean += 1

    # Surprise statistic: mean regret and its >=3sigma z (float only here).
    Mf = len(regrets)
    mean_frac = sum(regrets) / Mf                         # exact Fraction
    xs = [float(r) for r in regrets]
    mean_f = float(mean_frac)
    var = math.fsum((x - mean_f) ** 2 for x in xs) / (Mf - 1)
    std_f = math.sqrt(var)
    se = std_f / math.sqrt(Mf)
    z = mean_f / se if se > 0 else float("inf")

    return {
        "cost_factor": cost_factor,
        "n_instances": Mf,
        "mismatch_count": mismatch_count,
        "mean_regret_exact": str(mean_frac),
        "mean_regret_float": round(mean_f, ROUND_DP),
        "std_regret": round(std_f, ROUND_DP),
        "z_regret": round(z, ROUND_DP),
        "n_positive_regret": n_positive,
        "z_order_ne_mean_order_count": z_order_ne_mean_order,
        "lower_mean_opened_first_count": lower_mean_first,
        "decline_higher_mean_count": decline_higher_mean,
        "witness": witness,
    }


def _index_policy_declines_higher_mean(boxes, zvals, means):
    """True iff, under the index policy, some REACHABLE state stops (best >= max
    remaining z) while an unopened box still has E[R] > best — consequence (a)."""
    n = len(boxes)
    seen = set()
    found = [False]

    def walk(opened, best):
        if found[0]:
            return
        key = (opened, best)
        if key in seen:
            return
        seen.add(key)
        unopened = [i for i in range(n) if i not in opened]
        if not unopened:
            return
        maxz = max(zvals[boxes[i]["_id"]] for i in unopened)
        if best >= maxz:                                  # index policy STOPS here
            if any(means[boxes[i]["_id"]] > best for i in unopened):
                found[0] = True
            return
        # otherwise open the max-z box and branch over its rewards
        i, _ = _argmax_index(boxes, unopened, lambda b: zvals[b["_id"]])
        for r, _p in boxes[i]["support"]:
            walk(opened | {i}, max(best, r))

    walk(frozenset(), Fraction(0))
    return found[0]


# --------------------------------------------------------------------------- #
# Full battery.                                                               #
# --------------------------------------------------------------------------- #
def compute():
    # Fresh RNG per full run -> reproducible in-process AND cross-invocation.
    rng = random.Random(SEED)

    base = run_regime(rng, cost_factor=1)                 # primary regime
    shift = run_regime(rng, cost_factor=3)                # robustness / shift regime

    # G1 EXACT: index_policy_value == optimal_value for EVERY instance (both regimes).
    g1_ok = (base["mismatch_count"] == 0 and shift["mismatch_count"] == 0)

    # G2 SURPRISE: mean regret > 0 at >= 3 sigma (primary regime). Direction: HIGH z
    # means the mean-greedy heuristic is genuinely, significantly SUBOPTIMAL.
    g2_ok = (base["z_regret"] >= Z_GATE
             and Fraction(base["mean_regret_exact"]) > 0)

    # G3 NON-MONOTONICITY witness: reservation order differs from mean order, and the
    # optimum opens a lower-mean box first / declines a higher-mean box (count > 0).
    g3_ok = (base["z_order_ne_mean_order_count"] > 0
             and base["lower_mean_opened_first_count"] > 0
             and base["decline_higher_mean_count"] > 0
             and base["witness"] is not None)

    # G4 ROBUSTNESS/SHIFT: shifted regime (costs x3) still exact (0 mismatches) and
    # surprise regret still positive at >= 3 sigma.
    g4_ok = (shift["mismatch_count"] == 0
             and shift["z_regret"] >= Z_GATE
             and Fraction(shift["mean_regret_exact"]) > 0)

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for gname, gok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok), ("G4", g4_ok)):
        if not gok:
            first_failing = gname
            break

    return {
        "head": "pandora-box-reservation-index",
        "seed": SEED,
        "constants": {
            "N_boxes": N_BOXES,
            "M_instances": M_INSTANCES,
            "z_gate": Z_GATE,
            "reward_support": "distinct ints on 0..10, rational weights 1..4",
            "cost_support": "Fraction(1..5, {1,2}) = 0.5..5",
        },
        "g1_exact_agreement": {
            "base_mismatch_count": base["mismatch_count"],
            "shift_mismatch_count": shift["mismatch_count"],
            "direction": "AGREEMENT — index_policy_value == optimal_value exactly "
                         "(Fraction); ZERO mismatches is the pass condition",
        },
        "g2_surprise_regret": {
            "mean_regret_exact": base["mean_regret_exact"],
            "mean_regret_float": base["mean_regret_float"],
            "std_regret": base["std_regret"],
            "z_regret": base["z_regret"],
            "n_positive_regret": base["n_positive_regret"],
            "n_instances": base["n_instances"],
            "direction": "HIGH z (>=3 sigma) — the mean-greedy heuristic is genuinely,"
                         " significantly SUBOPTIMAL vs the reservation-index optimum",
        },
        "g3_nonmonotonicity": {
            "z_order_ne_mean_order_count": base["z_order_ne_mean_order_count"],
            "lower_mean_opened_first_count": base["lower_mean_opened_first_count"],
            "decline_higher_mean_count": base["decline_higher_mean_count"],
            "witness": base["witness"],
            "direction": "reservation order != expected-reward order; the optimum "
                         "opens a lower-mean box FIRST and declines a higher-mean box",
        },
        "g4_robustness_shift": {
            "regime": "costs x3",
            "mismatch_count": shift["mismatch_count"],
            "mean_regret_exact": shift["mean_regret_exact"],
            "mean_regret_float": shift["mean_regret_float"],
            "std_regret": shift["std_regret"],
            "z_regret": shift["z_regret"],
            "n_positive_regret": shift["n_positive_regret"],
            "direction": "shifted regime still EXACT (0 mismatches) and surprise "
                         "regret stays positive at >= 3 sigma",
        },
        "gates": {
            "G1_exact_index_eq_optimal": g1_ok,
            "G2_surprise_regret_3sigma": g2_ok,
            "G3_nonmonotonicity_witness": g3_ok,
            "G4_robustness_shift": g4_ok,
        },
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert canonical(r1) == canonical(r2), "non-deterministic: double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if r1["all_pass"] else "false"))
    print("G1_base_mismatch=%s G1_shift_mismatch=%s"
          % (r1["g1_exact_agreement"]["base_mismatch_count"],
             r1["g1_exact_agreement"]["shift_mismatch_count"]))
    print("G2_z_regret=%s (mean_regret=%s, n_positive=%s/%s)"
          % (r1["g2_surprise_regret"]["z_regret"],
             r1["g2_surprise_regret"]["mean_regret_exact"],
             r1["g2_surprise_regret"]["n_positive_regret"],
             r1["g2_surprise_regret"]["n_instances"]))
    print("G3_z_order_ne_mean=%s lower_mean_first=%s decline_higher_mean=%s"
          % (r1["g3_nonmonotonicity"]["z_order_ne_mean_order_count"],
             r1["g3_nonmonotonicity"]["lower_mean_opened_first_count"],
             r1["g3_nonmonotonicity"]["decline_higher_mean_count"]))
    print("G4_shift_z_regret=%s (mismatch=%s)"
          % (r1["g4_robustness_shift"]["z_regret"],
             r1["g4_robustness_shift"]["mismatch_count"]))
    print("RESULTS_SHA256=%s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
