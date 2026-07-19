#!/usr/bin/env python3
"""PROPOSAL 175 — pie-rule opening trap (round-41 GAME slot).

Head: under the pie / swap rule the second player may take over the first
player's position instead of replying, so a first player's realized win
probability from an opening o is min(f(o), 1 - f(o)), where f(o) is the mover's
win probability from that opening with no swap. Consequently the *strongest*
opening (largest f) becomes the *worst* choice under the rule -- the responder
simply swaps into it -- while a balanced opening (f ~= 0.5) is optimal.

Gates (ordered, z_gate = 3.0):
  G1  first-move edge exists WITHOUT the rule (greedy-strongest, no swap):
      win rate > 0.5 by >= 3 sigma.
  G2  the trap: greedy-strongest opening UNDER the rule inverts below fair --
      realized first-mover win rate < 0.5 by >= 3 sigma.
  G3  robustness under a shifted opening catalogue: balanced play strictly
      dominates naive-strong play by >= 3 sigma, and the balanced realized
      rate sits within 2 percentage points of a fair 0.5.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The results dict
carries no digest field; main() double-runs in-process, asserts byte-identical
compact-canonical serializations, and prints the pretty dump followed by the
sha256 of the compact-canonical form. Nothing is written to disk.
"""

import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0

# ---- committed world -------------------------------------------------------
# f(o) = P(first player wins from opening o under optimal continuation, NO swap).
# A genuine first-move edge means the catalogue reaches above 0.5.
BASE_OPENINGS = [0.50, 0.60, 0.70, 0.80, 0.90]   # baseline world for G1/G2
SHIFT_OPENINGS = [0.50, 0.65, 0.78, 0.88, 0.95]  # robustness world for G3
N_GAMES = 200000                                  # games per condition


def r6(x):
    return round(float(x), 6)


def summarize(vals):
    n = len(vals)
    mean = sum(vals) / n
    if n > 1:
        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    else:
        var = 0.0
    return {"n": n, "mean": r6(mean), "sd": r6(math.sqrt(var))}


def z_vs(vals, null):
    s = summarize(vals)
    sd = s["sd"]
    if sd == 0.0:
        return 0.0
    return (s["mean"] - null) / (sd / math.sqrt(s["n"]))


def realized_p(f, pie_rule):
    # Under the swap rule the responder takes the mover's side whenever the
    # opening favours the mover (f > 0.5), so the mover keeps only min(f, 1-f).
    if pie_rule:
        return min(f, 1.0 - f)
    return f


def play(rng, f, pie_rule, n):
    p = realized_p(f, pie_rule)
    return [1 if rng.random() < p else 0 for _ in range(n)]


def strongest(openings):
    return max(openings)


def most_balanced(openings):
    return min(openings, key=lambda f: abs(f - 0.5))


def run_g1():
    rng = random.Random(SEED + 11)
    f = strongest(BASE_OPENINGS)
    res = play(rng, f, False, N_GAMES)
    s = summarize(res)
    z = z_vs(res, 0.5)
    return {
        "opening_f": r6(f),
        "rule": "no-pie",
        "strategy": "greedy-strongest",
        "win_rate": s["mean"],
        "n": s["n"],
        "z_vs_half": r6(z),
        "pass": (s["mean"] > 0.5) and (z >= Z_GATE),
    }


def run_g2():
    rng = random.Random(SEED + 22)
    f = strongest(BASE_OPENINGS)
    res = play(rng, f, True, N_GAMES)
    s = summarize(res)
    z = z_vs(res, 0.5)
    return {
        "opening_f": r6(f),
        "rule": "pie",
        "strategy": "naive-greedy-strongest",
        "win_rate": s["mean"],
        "n": s["n"],
        "z_vs_half": r6(z),
        "pass": (s["mean"] < 0.5) and (z <= -Z_GATE),
    }


def run_g3():
    rng = random.Random(SEED + 33)
    f_naive = strongest(SHIFT_OPENINGS)
    f_opt = most_balanced(SHIFT_OPENINGS)
    naive = play(rng, f_naive, True, N_GAMES)
    opt = play(rng, f_opt, True, N_GAMES)
    s_naive = summarize(naive)
    s_opt = summarize(opt)
    diff = [o - nv for o, nv in zip(opt, naive)]
    s_diff = summarize(diff)
    z_gap = z_vs(diff, 0.0)
    fair = abs(s_opt["mean"] - 0.5) <= 0.02
    return {
        "rule": "pie",
        "shift_openings": [r6(x) for x in SHIFT_OPENINGS],
        "naive_f": r6(f_naive),
        "opt_f": r6(f_opt),
        "naive_rate": s_naive["mean"],
        "opt_rate": s_opt["mean"],
        "gap_mean": s_diff["mean"],
        "z_gap": r6(z_gap),
        "opt_within_2pct_of_fair": fair,
        "pass": (s_diff["mean"] > 0.0) and (z_gap >= Z_GATE) and fair,
    }


def run():
    g1 = run_g1()
    g2 = run_g2()
    g3 = run_g3()
    gates = [
        {"gate": "G1", "name": "first-move edge exists (no pie rule)", "pass": g1["pass"]},
        {"gate": "G2", "name": "strongest opening is losing under pie rule", "pass": g2["pass"]},
        {"gate": "G3", "name": "balanced dominates + restores fairness (shifted world)", "pass": g3["pass"]},
    ]
    first_failing = None
    for gt in gates:
        if not gt["pass"]:
            first_failing = gt["gate"]
            break
    return {
        "proposal": 175,
        "slot": "round-41 GAME",
        "head": "Under the pie/swap rule realized first-mover win prob = min(f, 1-f), so the strongest opening becomes the worst move: the first-move edge (G1) inverts below 0.5 for naive-strong play (G2) while balanced play dominates and restores a fair game (G3).",
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_games": N_GAMES,
        "base_openings": [r6(x) for x in BASE_OPENINGS],
        "g1": g1,
        "g2": g2,
        "g3": g3,
        "gates": gates,
        "all_pass": all(gt["pass"] for gt in gates),
        "first_failing_gate": first_failing,
    }


def main():
    r1 = run()
    r2 = run()
    c1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    c2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    assert c1 == c2, "in-process nondeterminism"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)


if __name__ == "__main__":
    main()
