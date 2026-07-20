#!/usr/bin/env python3
"""PROPOSAL 215 — Stackelberg commitment / first-mover advantage (round-51 GAME slot).

Head: in a linear-demand quantity duopoly, a leader who PUBLICLY COMMITS to an
output before the rival moves earns a strictly HIGHER payoff than it gets in the
simultaneous-move Cournot (Nash) equilibrium -- even though committing throws
away the ability to adjust and appears to hand the rival information. With
inverse demand P(Q)=A-Q, symmetric marginal cost C and m=A-C>0, the closed
forms are

    pi_cournot  = m^2 / 9   (each firm, simultaneous Nash)
    pi_leader   = m^2 / 8   (the committed leader, subgame-perfect)
    pi_follower = m^2 / 16   (the follower)

so the commitment advantage pi_leader - pi_cournot = m^2/8 - m^2/9 = m^2/72 > 0
for EVERY market size m>0. Folk intuition ("keeping your options open is worth
something; moving first only leaks your hand") is exactly wrong here: the value
comes precisely from the INABILITY to revise -- credible commitment shapes the
rival's best response in the leader's favour.

Gate battery (each direction stated):
  G1  SIGNIFICANCE (Monte-Carlo, wants mean>0 AND z >= +Z_GATE): against an
      epsilon-noisy (boundedly-rational) follower who deviates uniformly by
      {-2..+2} units from its best response, the leader's REALIZED commitment
      payoff still beats the Cournot payoff on average -- mean(gap) > 0 with
      z_vs_0 >= 3 sigma. Direction: upper-tail, z >= +Z_GATE.
  G2  EXACT (closed-form vs EXHAUSTIVE integer-grid enumeration, fractions.
      Fraction, wants == and >): on the pinned world, brute-force enumeration of
      every leader quantity with an exact-argmax best-responding follower gives a
      best-commit leader profit that EQUALS the closed form m^2/8 EXACTLY, the
      simultaneous pure-Nash (Cournot) profit EQUALS m^2/9 EXACTLY, the follower
      profit EQUALS m^2/16 EXACTLY, and leader > cournot STRICTLY. Directions:
      ==, ==, ==, then >.
  G3  ROBUSTNESS / SHIFT (wants == and > and z>=+Z_GATE): the exact result and
      the advantage persist under a scaled world (m=24) and a cost-shifted world
      (same m=12 via A=15,C=3, showing only m matters), and the Monte-Carlo
      advantage persists under the scaled world (mean>0, z >= 3 sigma).
  G4  FALSIFIABILITY (wants a wrong accounting REJECTED, direction !=): the naive
      STATIC-FOLLOWER accounting -- which prices the leader's commitment as if the
      follower ignored it and kept its Cournot quantity -- yields a leader profit
      that is NOT equal to the true best-response value (wrong != true) and in
      fact sits BELOW Cournot (wrong < cournot < true), so ignoring the follower's
      reaction is correctly rejected and would flip the sign of the advantage.
      Directions: wrong != true (rejected), wrong < cournot < true.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The results dict
carries no digest field; main() runs build_results() twice in-process, asserts
byte-identical compact-canonical serializations, prints the pretty dump, then
prints `results_sha256: <hex>` over the compact-canonical form. Nothing is
written to disk; a second separate process reproduces the identical dict/digest.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
GRID_MAX = 48          # integer quantity grid 0..GRID_MAX (covers m up to 24)
N_DRAWS = 200000       # Monte-Carlo draws per significance leg
EPS_SUPPORT = (-2, -1, 0, 1, 2)   # boundedly-rational follower deviation support


def r6(x):
    return round(float(x), 6)


def frac_pair(fr):
    fr = Fraction(fr)
    return [fr.numerator, fr.denominator]


# ---- exact single-firm profit and best response (integer grid) --------------

def firm_profit(q_self, q_other, A, C):
    """Exact profit of a firm producing q_self given rival q_other.

    Inverse demand P(Q) = A - Q (slope 1), constant marginal cost C, no fixed
    cost.  Price is floored at 0 (units below the choke price never occur on the
    relevant grid, but the floor keeps the accounting well-defined).
    """
    price = A - q_self - q_other
    if price < 0:
        price = 0
    return Fraction((price - C) * q_self)


def exact_br(q_other, A, C):
    """Exact profit-maximising best-response output (a Fraction).

    Backward induction: the follower observes q_other and picks q to maximise
    q*(A-q_other-q-C).  The interior optimum is (A-C-q_other)/2, floored at 0.
    This is the follower's TRUE reaction function -- the leader anticipates it.
    """
    q = Fraction(A - C - q_other, 2)
    return q if q > 0 else Fraction(0)


# ---- exhaustive enumeration of the two regimes ------------------------------

def enumerate_world(A, C):
    """Backward-induction enumeration: leader grid x exact follower reaction.

    Stackelberg -- the leader is enumerated EXHAUSTIVELY over the integer
    quantity grid; the follower plays its EXACT (Fraction) best response to each
    committed quantity; the leader keeps the commitment with the highest exact
    profit.  Cournot -- exhaustively scan integer profiles for a mutual EXACT
    best response (pure Nash); the symmetric one is the Cournot equilibrium.
    """
    best_qL = 0
    best_leader_pi = None
    best_qF = Fraction(0)
    for qL in range(GRID_MAX + 1):
        qF = exact_br(qL, A, C)
        pi_L = firm_profit(qL, qF, A, C)
        if best_leader_pi is None or pi_L > best_leader_pi:
            best_leader_pi = pi_L
            best_qL = qL
            best_qF = qF
    follower_pi = firm_profit(best_qF, best_qL, A, C)

    # Cournot: mutual exact-best-response integer profiles (pure Nash).
    nash = []
    for q1 in range(GRID_MAX + 1):
        for q2 in range(GRID_MAX + 1):
            if exact_br(q2, A, C) == q1 and exact_br(q1, A, C) == q2:
                nash.append((q1, q2))
    sym = [(a, b) for (a, b) in nash if a == b]
    q_cournot = sym[0][0]
    cournot_pi = firm_profit(q_cournot, q_cournot, A, C)
    return {
        "leader_q": best_qL,
        "follower_q": frac_pair(best_qF),
        "leader_profit": frac_pair(best_leader_pi),
        "follower_profit": frac_pair(follower_pi),
        "cournot_q": q_cournot,
        "cournot_profit": frac_pair(cournot_pi),
        "n_symmetric_nash": len(sym),
    }


def closed_forms(m):
    return {
        "m": m,
        "cournot": frac_pair(Fraction(m * m, 9)),
        "leader": frac_pair(Fraction(m * m, 8)),
        "follower": frac_pair(Fraction(m * m, 16)),
        "advantage": frac_pair(Fraction(m * m, 72)),
    }


# ---- Monte-Carlo significance vs an epsilon-noisy follower -------------------

def mc_gap(A, C, seed):
    """Realized leader-commitment gap over Cournot with a noisy follower."""
    m = A - C
    qL = m // 2                       # Stackelberg leader commit (m even -> exact)
    br = int(exact_br(qL, A, C))      # follower best response (integral here)
    cournot = Fraction(m * m, 9)
    cournot_f = float(cournot)
    rng = random.Random(seed)
    s = 0.0
    ss = 0.0
    for _ in range(N_DRAWS):
        eps = rng.choice(EPS_SUPPORT)
        qF = br + eps
        if qF < 0:
            qF = 0
        elif qF > GRID_MAX:
            qF = GRID_MAX
        realized = float(firm_profit(qL, qF, A, C))
        gap = realized - cournot_f
        s += gap
        ss += gap * gap
    mean = s / N_DRAWS
    var = ss / N_DRAWS - mean * mean
    if var < 0:
        var = 0.0
    sd = math.sqrt(var)
    z = 0.0 if sd == 0.0 else mean / (sd / math.sqrt(N_DRAWS))
    return {
        "A": A, "C": C, "m": m, "commit_qL": qL,
        "follower_br": br, "draws": N_DRAWS, "seed": seed,
        "mean_gap": r6(mean), "sd_gap": r6(sd), "z_vs_0": r6(z),
    }


# ---- gates ------------------------------------------------------------------

def build_results():
    # Pinned world: A=12, C=0 -> m=12 (all optima land on integer grid points).
    A0, C0 = 12, 0
    m0 = A0 - C0
    enum0 = enumerate_world(A0, C0)
    cf0 = closed_forms(m0)

    # G1 -- significance on the pinned world.
    g1_mc = mc_gap(A0, C0, SEED + 11)

    # G2 -- exact closed-form == exhaustive enumeration.
    leader_eq = enum0["leader_profit"] == cf0["leader"]
    cournot_eq = enum0["cournot_profit"] == cf0["cournot"]
    follower_eq = enum0["follower_profit"] == cf0["follower"]
    leader_gt_cournot = Fraction(*enum0["leader_profit"]) > Fraction(*enum0["cournot_profit"])
    g2_pass = bool(leader_eq and cournot_eq and follower_eq and leader_gt_cournot)

    # G3 -- robustness / shift.
    A1, C1 = 24, 0          # scaled world, m=24
    A2, C2 = 15, 3          # cost-shifted world, same m=12
    enum1 = enumerate_world(A1, C1)
    cf1 = closed_forms(A1 - C1)
    enum2 = enumerate_world(A2, C2)
    cf2 = closed_forms(A2 - C2)
    shift1_exact = bool(
        enum1["leader_profit"] == cf1["leader"]
        and enum1["cournot_profit"] == cf1["cournot"]
        and enum1["follower_profit"] == cf1["follower"]
        and Fraction(*enum1["leader_profit"]) > Fraction(*enum1["cournot_profit"])
    )
    shift2_exact = bool(
        enum2["leader_profit"] == cf2["leader"]
        and enum2["cournot_profit"] == cf2["cournot"]
        and enum2["follower_profit"] == cf2["follower"]
        and Fraction(*enum2["leader_profit"]) > Fraction(*enum2["cournot_profit"])
    )
    g3_mc = mc_gap(A1, C1, SEED + 33)
    g3_pass = bool(
        shift1_exact and shift2_exact
        and g3_mc["mean_gap"] > 0.0 and g3_mc["z_vs_0"] >= Z_GATE
    )

    # G1 gate decision (uses the MC leg computed above).
    g1_pass = bool(g1_mc["mean_gap"] > 0.0 and g1_mc["z_vs_0"] >= Z_GATE)

    # G4 -- falsifiability: static-follower accounting is rejected.
    qL0 = enum0["leader_q"]                          # true committed leader qty
    true_leader = Fraction(*enum0["leader_profit"])  # follower best-responds
    q_cournot = enum0["cournot_q"]
    # WRONG model: follower ignores the commitment and keeps its Cournot quantity.
    wrong_leader = firm_profit(qL0, q_cournot, A0, C0)
    cournot = Fraction(*enum0["cournot_profit"])
    wrong_rejected = wrong_leader != true_leader
    directional = (true_leader > cournot) and (wrong_leader < cournot)
    g4_pass = bool(wrong_rejected and directional)
    g4 = {
        "commit_qL": qL0,
        "static_follower_q": q_cournot,
        "true_leader_profit": frac_pair(true_leader),
        "wrong_static_leader_profit": frac_pair(wrong_leader),
        "cournot_profit": frac_pair(cournot),
        "wrong_rejected_neq_true": bool(wrong_rejected),
        "true_gt_cournot": bool(true_leader > cournot),
        "wrong_lt_cournot": bool(wrong_leader < cournot),
    }

    gates = {
        "G1_significance": g1_pass,
        "G2_exact_enumeration": g2_pass,
        "G3_robustness_shift": g3_pass,
        "G4_falsifiability": g4_pass,
    }
    ordered = ["G1_significance", "G2_exact_enumeration", "G3_robustness_shift", "G4_falsifiability"]
    first_failing = next((g for g in ordered if not gates[g]), None)

    return {
        "proposal": 215,
        "slot": "round-51 GAME",
        "head": (
            "In a linear-demand quantity duopoly the leader who PUBLICLY COMMITS to an "
            "output earns strictly more than in the simultaneous Cournot equilibrium "
            "(pi_leader=m^2/8 > pi_cournot=m^2/9, advantage m^2/72>0): G1 the advantage "
            "survives a noisy follower at >=3 sigma; G2 exhaustive integer-grid enumeration "
            "matches the closed forms EXACTLY (Fraction) with leader>cournot; G3 it holds "
            "under scaled and cost-shifted worlds; G4 the static-follower accounting that "
            "ignores the reaction is correctly rejected (and would flip the sign)."
        ),
        "seed": SEED,
        "z_gate": Z_GATE,
        "grid_max": GRID_MAX,
        "eps_support": list(EPS_SUPPORT),
        "pinned_world": {"A": A0, "C": C0, "m": m0},
        "closed_forms_pinned": cf0,
        "enum_pinned": enum0,
        "g1_significance": g1_mc,
        "g2_exact": {
            "leader_eq": bool(leader_eq),
            "cournot_eq": bool(cournot_eq),
            "follower_eq": bool(follower_eq),
            "leader_gt_cournot": bool(leader_gt_cournot),
        },
        "g3_shift": {
            "scaled_world": {"A": A1, "C": C1, "enum": enum1, "closed": cf1, "exact": shift1_exact},
            "cost_shift_world": {"A": A2, "C": C2, "enum": enum2, "closed": cf2, "exact": shift2_exact},
            "mc_scaled": g3_mc,
        },
        "g4_falsifiability": g4,
        "gates": gates,
        "all_pass": bool(all(gates.values())),
        "first_failing_gate": first_failing,
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        print("NON-DETERMINISTIC: in-process double-run diverged", file=sys.stderr)
        sys.exit(3)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print()
    for name in sorted(r1["gates"]):
        print(f"{name}: {'PASS' if r1['gates'][name] else 'FAIL'}")
    print(f"all_pass: {r1['all_pass']}")
    print(f"results_sha256: {digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
