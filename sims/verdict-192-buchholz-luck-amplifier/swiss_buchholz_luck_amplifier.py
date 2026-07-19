#!/usr/bin/env python3
"""PROPOSAL 179 — Swiss-system Buchholz tiebreak is a luck amplifier.

Head: among players finishing tied on match points in a Swiss-system
tournament, the Buchholz ("strength of schedule") tiebreak ranks the luckier
opponent draw ahead of the more-skilled player. Buchholz measures whom you
happened to play, not how good you are.

stdlib-only; SEED pinned; deterministic; in-process double-run asserted.
Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY - the sha256 of the
compact-canonical results dict IS the digest; the dict carries no digest field.
"""
import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0


def elo_p(a, b):
    return 1.0 / (1.0 + 10.0 ** ((b - a) / 400.0))


def run_tournament(rng, n, rounds, sigma):
    theta = [rng.gauss(1500.0, sigma) for _ in range(n)]
    points = [0.0] * n
    opponents = [[] for _ in range(n)]
    played = [set() for _ in range(n)]
    for _ in range(rounds):
        order = sorted(range(n), key=lambda i: (-points[i], rng.random()))
        paired = [False] * n
        for ai in range(n):
            a = order[ai]
            if paired[a]:
                continue
            b = None
            for bi in range(ai + 1, n):
                cand = order[bi]
                if not paired[cand] and cand not in played[a]:
                    b = cand
                    break
            if b is None:
                for bi in range(ai + 1, n):
                    cand = order[bi]
                    if not paired[cand]:
                        b = cand
                        break
            if b is None:
                continue
            paired[a] = True
            paired[b] = True
            opponents[a].append(b)
            opponents[b].append(a)
            played[a].add(b)
            played[b].add(a)
            if rng.random() < elo_p(theta[a], theta[b]):
                points[a] += 1.0
            else:
                points[b] += 1.0
    buchholz = [sum(points[o] for o in opponents[i]) for i in range(n)]
    opp_skill = [sum(theta[o] for o in opponents[i]) for i in range(n)]
    return theta, points, buchholz, opp_skill


def measure(rng, n, rounds, sigma, n_tournaments):
    n_pairs = 0
    skill_hits = 0
    luck_hits = 0
    dsum = 0.0
    dsqsum = 0.0
    for _ in range(n_tournaments):
        theta, points, buch, opp = run_tournament(rng, n, rounds, sigma)
        groups = {}
        for i in range(n):
            groups.setdefault(points[i], []).append(i)
        for grp in groups.values():
            m = len(grp)
            for x in range(m):
                for y in range(x + 1, m):
                    a = grp[x]
                    b = grp[y]
                    if buch[a] == buch[b]:
                        continue
                    if theta[a] == theta[b] or opp[a] == opp[b]:
                        continue
                    winner = a if buch[a] > buch[b] else b
                    hi_theta = theta[a] if theta[a] > theta[b] else theta[b]
                    hi_opp = opp[a] if opp[a] > opp[b] else opp[b]
                    s = 1 if theta[winner] == hi_theta else 0
                    l = 1 if opp[winner] == hi_opp else 0
                    n_pairs += 1
                    skill_hits += s
                    luck_hits += l
                    d = l - s
                    dsum += d
                    dsqsum += d * d
    p_skill = skill_hits / n_pairs
    p_luck = luck_hits / n_pairs
    se_luck = math.sqrt(p_luck * (1.0 - p_luck) / n_pairs)
    z_luck = (p_luck - 0.5) / se_luck
    mean_d = dsum / n_pairs
    var_d = dsqsum / n_pairs - mean_d * mean_d
    se_d = math.sqrt(var_d / n_pairs)
    z_diff = mean_d / se_d if se_d > 0 else 0.0
    sig_luck = abs(p_luck - 0.5)
    sig_skill = abs(p_skill - 0.5)
    ratio = sig_luck / sig_skill if sig_skill > 1e-9 else 999.0
    ratio = min(ratio, 999.0)
    return {
        'n': n,
        'rounds': rounds,
        'sigma': sigma,
        'n_tournaments': n_tournaments,
        'n_pairs': n_pairs,
        'p_skill': round(p_skill, 6),
        'p_luck': round(p_luck, 6),
        'z_luck': round(z_luck, 6),
        'mean_d': round(mean_d, 6),
        'z_diff': round(z_diff, 6),
        'ratio': round(ratio, 6),
    }


def compute():
    base = measure(random.Random(SEED), 64, 7, 200.0, 1200)
    shift = measure(random.Random(SEED + 1), 128, 9, 350.0, 400)
    g1 = base['p_luck'] >= 0.70 and base['z_luck'] >= Z_GATE
    g2 = (base['ratio'] >= 3.0 and base['z_diff'] >= Z_GATE
          and (base['p_luck'] - base['p_skill']) >= 0.15)
    g3 = (shift['p_luck'] >= 0.70 and shift['z_diff'] >= Z_GATE
          and (shift['p_luck'] - shift['p_skill']) >= 0.10)
    return {
        'seed': SEED,
        'base': base,
        'shift': shift,
        'gates': {
            'G1_luck_dominates': bool(g1),
            'G2_luck_beats_skill': bool(g2),
            'G3_robust_shift': bool(g3),
        },
        'all_pass': bool(g1 and g2 and g3),
    }


def main():
    r1 = compute()
    r2 = compute()
    assert r1 == r2, "non-deterministic: in-process double-run mismatch"
    canonical = json.dumps(r1, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results-dict sha256: " + digest)


if __name__ == '__main__':
    main()
