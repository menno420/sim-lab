#!/usr/bin/env python3
"""PROPOSAL 168 verifier — Condorcet voting-cycle paradox (round-39 UNRELATED slot).

Head: rational (transitive) individual preferences compose into an INTRANSITIVE
collective majority. Under impartial culture (every strict ranking of m
candidates equally likely), a random electorate fails to have a Condorcet
winner -- a candidate who beats every other in pairwise majority -- at a
documented positive rate (~8.7% for m=3, rising steeply with m). The folk
belief that consistent individuals compose into a consistent group ranking
is false.

Grounding: https://en.wikipedia.org/wiki/Condorcet_paradox (oldid 1360635422).
Documented impartial-culture no-Condorcet-winner rates: m=3,n=101 -> 8.690%;
asymptotic m=3 -> 8.77%; candidate scaling (25 voters) 3/4/5/7 -> 8.4/16.6/24.2/35.7%.

stdlib only. Deterministic: a fresh random.Random(SEED) drives every draw, so an
in-process double-run and any cross-invocation reproduce byte-identical results.
Digest posture: the compact-canonical results dict's own sha256 IS the disclosed
digest (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY).
"""

import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0


def r6(x):
    return round(float(x), 6)


def random_ranking(rng, m):
    r = list(range(m))
    rng.shuffle(r)
    return r


def plackett_luce_ranking(rng, weights):
    items = list(range(len(weights)))
    order = []
    for _ in range(len(weights)):
        total = 0.0
        for i in items:
            total += weights[i]
        thresh = rng.random() * total
        acc = 0.0
        chosen = items[-1]
        for i in items:
            acc += weights[i]
            if acc >= thresh:
                chosen = i
                break
        order.append(chosen)
        items.remove(chosen)
    return order


def has_condorcet_winner(rankings, m):
    n = len(rankings)
    wins = [[0] * m for _ in range(m)]
    for order in rankings:
        pos = [0] * m
        for idx, cand in enumerate(order):
            pos[cand] = idx
        for i in range(m):
            pi = pos[i]
            for j in range(i + 1, m):
                if pi < pos[j]:
                    wins[i][j] += 1
                else:
                    wins[j][i] += 1
    half = n / 2.0
    for i in range(m):
        beats_all = True
        for j in range(m):
            if i == j:
                continue
            if not (wins[i][j] > half):
                beats_all = False
                break
        if beats_all:
            return True
    return False


def cycle_rate(rng, m, n_voters, n_trials, weights=None):
    no_winner = 0
    for _ in range(n_trials):
        if weights is None:
            rankings = [random_ranking(rng, m) for _ in range(n_voters)]
        else:
            rankings = [plackett_luce_ranking(rng, weights) for _ in range(n_voters)]
        if not has_condorcet_winner(rankings, m):
            no_winner += 1
    return no_winner, n_trials


def z_vs_ref(k, n, p0):
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (k / n - p0) / se


def z_from_zero(k, n):
    if k == 0:
        return 0.0
    p = k / n
    se = math.sqrt(p * (1.0 - p) / n)
    return p / se


def z_diff(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    if se == 0.0:
        return 0.0
    return (p1 - p2) / se


def run():
    rng = random.Random(SEED)

    N_PRIMARY = 40000
    N_SCALE = 10000
    N_ROBUST = 20000
    N_VOTERS = 101
    DOC_M3_N101 = 0.08690

    k3, n3 = cycle_rate(rng, 3, N_VOTERS, N_PRIMARY)
    p3 = k3 / n3
    z_head = z_from_zero(k3, n3)
    z_match = z_vs_ref(k3, n3, DOC_M3_N101)

    ms = [3, 4, 5, 7]
    scale = {}
    for m in ms:
        km, nm = cycle_rate(rng, m, N_VOTERS, N_SCALE)
        scale[m] = (km, nm)

    mono_zs = []
    mono_ok = True
    for a, b in zip(ms, ms[1:]):
        ka, na = scale[a]
        kb, nb = scale[b]
        z = z_diff(kb, nb, ka, na)
        mono_zs.append(z)
        if not (z >= Z_GATE):
            mono_ok = False

    weights3 = [1.00, 0.85, 0.72]
    kr, nr = cycle_rate(rng, 3, N_VOTERS, N_ROBUST, weights=weights3)
    z_robust = z_from_zero(kr, nr)

    results = {
        "meta": {
            "seed": SEED,
            "z_gate": r6(Z_GATE),
            "n_voters": N_VOTERS,
            "doc_m3_n101": r6(DOC_M3_N101),
            "doc_asymptotic_m3": r6(0.0877),
        },
        "primary_m3": {
            "n_trials": n3,
            "no_condorcet_winner": k3,
            "rate": r6(p3),
            "z_vs_zero": r6(z_head),
            "z_vs_documented": r6(z_match),
        },
        "scaling": {
            str(m): {
                "n_trials": scale[m][1],
                "no_condorcet_winner": scale[m][0],
                "rate": r6(scale[m][0] / scale[m][1]),
            }
            for m in ms
        },
        "monotone_step_z": [r6(z) for z in mono_zs],
        "robustness_tilt_m3": {
            "weights": [r6(w) for w in weights3],
            "n_trials": nr,
            "no_condorcet_winner": kr,
            "rate": r6(kr / nr),
            "z_vs_zero": r6(z_robust),
        },
        "gates": {},
    }

    g1 = z_head >= Z_GATE
    g2a = abs(z_match) < Z_GATE
    g2b = mono_ok
    g3 = z_robust >= Z_GATE
    results["gates"] = {
        "G1_head_cycles_exist": bool(g1),
        "G2a_matches_documented_rate": bool(g2a),
        "G2b_monotone_in_candidates": bool(g2b),
        "G3_robust_under_tilt": bool(g3),
    }
    results["all_pass"] = bool(g1 and g2a and g2b and g3)
    return results


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = run()
    r2 = run()
    c1, c2 = canonical(r1), canonical(r2)
    assert c1 == c2, "in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    assert r1["all_pass"], "gates did not all pass"


if __name__ == "__main__":
    main()
