#!/usr/bin/env python3
"""PROPOSAL 140 — gambler's ruin edge asymmetry (round-32 UNRELATED slot CLOSER).

Phenomenon (probability / random walks, a fleet-external pure-mechanism head). A
gambler starts with `i` units and bets one fixed unit per round against a house.
Each round the gambler wins one unit with probability p and loses one with
probability q = 1 - p. Play stops the FIRST time the fortune hits 0 (ruin) or a
target N (cash out). The probability of reaching the target N before ruin at 0
is the classical gambler's-ruin first-passage law:

    P(reach N before 0 | start i) = (1 - (q/p)^i) / (1 - (q/p)^N)   for p != 0.5,
                                  = i / N                            for p == 0.5.

Folk belief (inverted here): "the house edge is small — a ~1.5% edge only shaves a
percent or two off my chances, the penalty grows LINEARLY with the edge." FALSE.
Write r = q/p. For p < 0.5 the ruin penalty is EXPONENTIAL in the target distance,
not linear in the edge: dropping from a fair game (p=0.5, where P = i/N is a plain
ratio) to a game with only a small edge collapses the reach-your-target probability
by ORDERS OF MAGNITUDE once N is large, because (q/p)^N grows exponentially with N.
On the pinned world a symmetric fair-game start (i=100, N=200) has P = 0.5; nudging
p from 0.500 to 0.485 — a 1.5% edge — collapses P to ~0.002466, roughly a 200x drop,
NOT the ~1.5% (P ~ 0.485) a linear-in-the-edge intuition predicts. The penalty is
exponential in N, not linear in the edge.

Distinct from the prior UNRELATED-slot Kelly head P100 (kelly-overbet-ruin): P100 is
information theory — the GROWTH-OPTIMAL bet FRACTION f* = edge/odds that maximizes
long-run log-wealth and the overbetting ruin past 2f* on a MULTIPLICATIVE (geometric)
wealth process with proportional stakes. THIS head is the FIRST-PASSAGE ruin of an
ADDITIVE fixed-stake random walk between two absorbing barriers — no bet sizing, no
log-wealth, no growth rate; the object is P(hit N before 0), a boundary-crossing
probability governed by (q/p)^i, not a Kelly fraction. Different process (additive vs
multiplicative), different object (first-passage probability vs growth-optimal
fraction), different mechanism (exponential barrier ratio vs log-utility optimum).

Anchors (closed form, no RNG):
  CFG_MOD  p=0.48,  i=20,  N=40 : P = (1-(q/p)^20)/(1-(q/p)^40) = 0.16786226899... .
  CFG_FAIR p=0.50,  i=20,  N=40 : P = i/N = 0.5 exactly.
  CFG_EDGE p=0.485, i=100, N=200: P = (1-(q/p)^100)/(1-(q/p)^200) = 0.00246818501... .

Pre-registered gates (PASS iff ALL hold, in order CFG_MOD -> CFG_FAIR -> CFG_EDGE):
  CFG_MOD  VERIFIER-CORRECTNESS AGREEMENT: the Monte-Carlo reach-probability agrees
           with the exact closed form within z < 3 sigma. se = sqrt(mc*(1-mc)/trials)
           (Bernoulli over the walks). z = (mc - closed)/se. PASS on |z| < 3 — the
           simulator's walks-to-absorption reproduce the closed-form law.
  CFG_FAIR FAIR-GAME AGREEMENT: at p=0.5 the Monte-Carlo reach-probability agrees with
           the exact i/N = 0.5 within z < 3 sigma. se = sqrt(mc*(1-mc)/trials).
           z = (mc - closed)/se. PASS on |z| < 3 — the fair-game baseline is a plain
           ratio, no exponential term.
  CFG_EDGE COUNTERINTUITIVE HEADLINE (z >= 3): with a 1.5% edge the observed reach
           probability sits DOZENS of sigma BELOW the linear-intuition anchor L=0.485
           (the naive "a 1.5% edge costs ~1.5%"). z = (L - mc)/se with
           se = sqrt(mc*(1-mc)/trials) (Bernoulli over the walks). PASS on z >= 3 — the
           penalty is exponential in N, not linear in the edge.
"""

import hashlib
import json
import random

SEED = 20260717
SIGMA_GATE = 3.0
LINEAR_ANCHOR = 0.485  # naive "a 1.5% edge costs ~1.5%" -> P ~ 0.485 (CFG_EDGE)

# Config order is FIXED — the single pinned RNG stream is drawn sequentially in this
# order, so the run is deterministic (identical double-run -> identical results dict
# -> identical sha256).
CONFIGS = [
    {"name": "CFG_MOD", "p": 0.48, "i": 20, "N": 40, "trials": 200_000, "gate": "agree"},
    {"name": "CFG_FAIR", "p": 0.50, "i": 20, "N": 40, "trials": 200_000, "gate": "agree"},
    {"name": "CFG_EDGE", "p": 0.485, "i": 100, "N": 200, "trials": 100_000, "gate": "edge"},
]


def closed_form(p, i, N):
    """Gambler's-ruin reach-N-before-0 probability starting at i, barriers 0 and N."""
    if p == 0.5:
        return i / N
    r = (1.0 - p) / p  # q/p
    return (1.0 - r ** i) / (1.0 - r ** N)


def simulate(p, i, N, trials, rng):
    """Monte-Carlo `trials` fixed-stake walks from i to absorption at 0 or N.

    Each step is +1 with probability p else -1, off the single pinned stream. Counts
    the walks that reach N before 0. Returns the number of successes (reached N).
    """
    rand = rng.random
    successes = 0
    for _ in range(trials):
        pos = i
        while pos != 0 and pos != N:
            if rand() < p:
                pos += 1
            else:
                pos -= 1
        if pos == N:
            successes += 1
    return successes


def run():
    rng = random.Random(SEED)
    configs = {}
    all_gates_pass = True

    # Draw the configs sequentially off the single pinned stream, in the fixed order.
    for cfg in CONFIGS:
        name = cfg["name"]
        p, i, N, trials = cfg["p"], cfg["i"], cfg["N"], cfg["trials"]
        closed = closed_form(p, i, N)
        successes = simulate(p, i, N, trials, rng)
        mc = successes / trials
        se = (mc * (1.0 - mc) / trials) ** 0.5

        if cfg["gate"] == "edge":
            # Headline: observed reach probability is z >= 3 BELOW the linear anchor.
            z = (LINEAR_ANCHOR - mc) / se if se > 0 else float("inf")
            gate = z >= SIGMA_GATE
        else:
            # Agreement: Monte-Carlo matches the exact closed form within |z| < 3.
            z = (mc - closed) / se if se > 0 else float("inf")
            gate = abs(z) < SIGMA_GATE

        configs[name] = {
            "p": p,
            "i": i,
            "N": N,
            "trials": trials,
            "closed": closed,
            "mc": mc,
            "z": z,
            "gate": gate,
        }
        all_gates_pass = all_gates_pass and gate

    return {
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "linear_anchor": LINEAR_ANCHOR,
        "configs": configs,
        "all_gates_pass": all_gates_pass,
    }


def main():
    results = run()
    # WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest: the compact canonical
    # serialization of the whole results dict is the digest preimage; the digest is
    # printed to stdout ONLY and is never stored inside the dict.
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    # in-process double-run: run() twice, compact-hash both, assert byte-identical.
    results_2 = run()
    payload_2 = json.dumps(results_2, sort_keys=True, separators=(",", ":"))
    digest_2 = hashlib.sha256(payload_2.encode()).hexdigest()
    assert digest == digest_2, "non-deterministic: in-process double-run digests differ"

    # human-readable gate lines
    for cfg in CONFIGS:
        name = cfg["name"]
        c = results["configs"][name]
        print(
            f"{name:8s}:",
            "PASS" if c["gate"] else "FAIL",
            f"(z={c['z']:+.3f}, mc={c['mc']:.6f}, closed={c['closed']:.6f}, "
            f"p={c['p']}, i={c['i']}, N={c['N']}, trials={c['trials']})",
        )

    # the results JSON (pretty indent=2 stdout dump — distinct from the compact
    # hashed preimage) then the digest line
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)

    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
