#!/usr/bin/env python3
"""VERDICT 081 runner — the deferred-acceptance proposer advantage
(idea-engine PROPOSAL 068).

Hermetic: reads ONLY its own fixtures.json. Stdlib only. Deterministic:
stdout and results.json are byte-identical across process runs.

Three arms:
  Arm A — decision-bearing, seedless exact rationals: full exhaustive
          census at n = 1, 2, 3 (6^6 = 46,656 profiles at the decision
          cell) — men-proposing GS -> mu_M, women-proposing GS -> mu_W,
          the stable set S by exhaustive blocking-pair testing of all n!
          matchings (never via GS), every metric an exact Fraction, the
          three structure theorems enumerated, manipulation counts by
          corner lookup over the census's own profile space (C2).
  Arm B — twin, seedless, INDEPENDENTLY-WRITTEN: factorial-decode profile
          iteration, an all-pairs stability test, extremal matchings taken
          as the ENUMERATED stable set's coordinatewise men-rank min/max
          (never via GS), separate accumulators, GS-free manipulation via
          its own corner table. Must reproduce every Arm-A number EXACTLY;
          powers the second decision evaluator.
  Arm R — seeded (the drafter's registered allocation 20261600-603),
          REPORTING-ONLY: n in {4, 5, 6}; main leg 200,000 episodes/size
          on Random(20261600) (GS both ways -> delta-hat, f-hat per C4);
          stability leg 40,000 episodes/size on Random(20261601) (full
          n! enumeration, E|S|, delta|multi, C4 + sandwich re-verified per
          episode); M_recv-hat on the deterministic stability-leg prefix
          (C6, DGS prune); presentation rows via Random(20261602) (C11);
          aux 20261603 NEVER read (constructor registry, C8).
"""

import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FX = json.load(open(os.path.join(HERE, "fixtures.json")))

assert sys.version_info[:2] == tuple(FX["runtime_pins"]["cpython"]), (
    "CPython %d.%d pinned (fixtures runtime_pins)" % tuple(FX["runtime_pins"]["cpython"])
)

CHECKS = []


def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return bool(ok)


def frs(x):
    """canonical exact-rational string"""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return "%d/%d" % (x.numerator, x.denominator)


def f6(x):
    """6-decimal float rendering of an exact value (presentation only)"""
    return "%.6f" % float(Fraction(x))


SEEDS_CONSTRUCTED = []


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Arm A machinery — GS + preference-order blocking-pair scan
# ---------------------------------------------------------------------------

def gs(props, rrank, n):
    """Deferred acceptance, proposers propose. props[p] = p's ranked
    receivers best-first; rrank[r][p] = receiver r's 0-based rank of p.
    Returns match[p] = receiver (tuple)."""
    nxt = [0] * n
    cur = [-1] * n            # receiver -> held proposer
    match = [-1] * n
    free = list(range(n - 1, -1, -1))
    while free:
        p = free.pop()
        r = props[p][nxt[p]]
        nxt[p] += 1
        h = cur[r]
        if h < 0:
            cur[r] = p
            match[p] = r
        elif rrank[r][p] < rrank[r][h]:
            cur[r] = p
            match[p] = r
            match[h] = -1
            free.append(h)
        else:
            free.append(p)
    return tuple(match)


def stable_a(mp, wrank, wife, husb, n):
    """Arm A stability: scan each man's list down to his wife; any woman
    above her who prefers him to her husband is a blocking pair."""
    for m in range(n):
        pw = wife[m]
        wr = wrank
        for w in mp[m]:
            if w == pw:
                break
            if wr[w][m] < wr[w][husb[w]]:
                return False
    return True


def invert(match, n):
    inv = [-1] * n
    for i in range(n):
        inv[match[i]] = i
    return tuple(inv)


def census_a(n):
    """Full exact census at size n. Returns (metrics dict, corner table)."""
    perms = list(itertools.permutations(range(n)))
    rank_of = {}
    for p in perms:
        row = [0] * n
        for i, x in enumerate(p):
            row[x] = i
        rank_of[p] = tuple(row)
    nfact = len(perms)
    nprof = nfact ** (2 * n)

    sum_m_muM = 0        # 0-based rank sums
    sum_w_muM = 0
    sum_m_muW = 0
    sum_w_muW = 0
    multi = 0
    sum_S = 0
    g_unique_sum = 0     # sum over unique profiles of n*g(p) (integer)
    g_multi_sum = 0      # sum over multi profiles of n*g(p)
    gs_unstable = 0      # F1: GS output fails the stability test
    polar_fail = 0       # F2a violations
    sandwich_fail = 0    # unique <-> mu_M == mu_W violations
    corner_min_fail = 0  # mu_M not coordinatewise-min of S (men ranks)
    corner_max_fail = 0
    rank_min_seen = n
    rank_max_seen = -1
    # F5 degeneracy families
    deg_m_count = 0
    deg_m_multi = 0
    deg_m_gsum = 0
    deg_m_wsum = 0   # naive slice sums (reporting)
    deg_m_msum = 0
    deg_w_count = 0
    deg_w_multi = 0
    deg_w_gsum = 0
    deg_w_wsum = 0
    deg_w_msum = 0

    corners = {}

    for prof in itertools.product(perms, repeat=2 * n):
        mp = prof[:n]
        wp = prof[n:]
        mrank = tuple(rank_of[p] for p in mp)
        wrank = tuple(rank_of[p] for p in wp)

        muM = gs(mp, wrank, n)                 # wife[m]
        muW_h = gs(wp, mrank, n)               # husband[w]
        muW = invert(muW_h, n)                 # wife[m]
        husbM = invert(muM, n)

        if not stable_a(mp, wrank, muM, husbM, n):
            gs_unstable += 1
        if not stable_a(mp, wrank, muW, muW_h, n):
            gs_unstable += 1

        # exhaustive stable set (independent of GS)
        S = []
        for wife in perms:
            husb = invert(wife, n)
            if stable_a(mp, wrank, wife, husb, n):
                S.append((wife, husb))
        sum_S += len(S)

        # polarization + corner checks against every stable matching
        mrM = [mrank[m][muM[m]] for m in range(n)]
        mrW = [mrank[m][muW[m]] for m in range(n)]
        wrM = [wrank[w][husbM[w]] for w in range(n)]
        wrW = [wrank[w][muW_h[w]] for w in range(n)]
        for wife, husb in S:
            for m in range(n):
                r = mrank[m][wife[m]]
                if not (mrM[m] <= r <= mrW[m]):
                    polar_fail += 1
            for w in range(n):
                r = wrank[w][husb[w]]
                if not (wrW[w] <= r <= wrM[w]):
                    polar_fail += 1
        # GS lands the corners of the ENUMERATED set
        if muM not in [s[0] for s in S]:
            corner_min_fail += 1
        else:
            for wife, husb in S:
                if any(mrank[m][wife[m]] < mrM[m] for m in range(n)):
                    corner_min_fail += 1
                    break
        if muW not in [s[0] for s in S]:
            corner_max_fail += 1
        else:
            for wife, husb in S:
                if any(mrank[m][wife[m]] > mrW[m] for m in range(n)):
                    corner_max_fail += 1
                    break

        is_multi = len(S) >= 2
        if is_multi != (muM != muW):
            sandwich_fail += 1

        sm = sum(mrM)
        sw = sum(wrM)
        smW = sum(mrW)
        swW = sum(wrW)
        sum_m_muM += sm
        sum_w_muM += sw
        sum_m_muW += smW
        sum_w_muW += swW
        rank_min_seen = min(rank_min_seen, min(mrM + wrM + mrW + wrW))
        rank_max_seen = max(rank_max_seen, max(mrM + wrM + mrW + wrW))

        gnum = sw - swW   # n * g(p), 0-based offsets cancel
        if is_multi:
            multi += 1
            g_multi_sum += gnum
        else:
            g_unique_sum += gnum

        # F5 degeneracy families
        if all(p == mp[0] for p in mp):
            deg_m_count += 1
            if is_multi:
                deg_m_multi += 1
            deg_m_gsum += gnum
            deg_m_wsum += sw
            deg_m_msum += sm
        if all(p == wp[0] for p in wp):
            deg_w_count += 1
            if is_multi:
                deg_w_multi += 1
            deg_w_gsum += gnum
            deg_w_wsum += sw
            deg_w_msum += sm

        corners[(mp, wp)] = (muM, muW)

    # manipulation pass — corner lookups over the census's own space (C2)
    cnt_mprop = 0        # some man gains, men-proposing
    cnt_mrecv = 0        # some woman gains, men-proposing
    cnt_sym_prop = 0     # some woman gains, women-proposing (relabel of M_prop)
    cnt_sym_recv = 0     # some man gains, women-proposing (relabel of M_recv)
    dgs_fail = 0         # a successful receiver misreport violating DGS (C6)

    for (mp, wp), (muM, muW) in corners.items():
        husbM = invert(muM, n)
        muW_h = invert(muW, n)
        # men under men-proposing (early break; expected zero)
        gain = False
        for m in range(n):
            true_r = rank_of[mp[m]]
            base = true_r[muM[m]]
            for alt in perms:
                if alt == mp[m]:
                    continue
                muM2, _ = corners[(mp[:m] + (alt,) + mp[m + 1:], wp)]
                if true_r[muM2[m]] < base:
                    gain = True
                    break
            if gain:
                break
        if gain:
            cnt_mprop += 1
        # women under men-proposing (full search; DGS verified per success)
        gain = False
        for w in range(n):
            true_r = rank_of[wp[w]]
            base = true_r[husbM[w]]
            best_stable = true_r[muW_h[w]]
            for alt in perms:
                if alt == wp[w]:
                    continue
                muM2, _ = corners[(mp, wp[:w] + (alt,) + wp[w + 1:])]
                h2 = invert(muM2, n)
                got = true_r[h2[w]]
                if got < base:
                    gain = True
                    # DGS clauses: only a woman with differing stable
                    # partners can gain, and never past mu_W(w)
                    if husbM[w] == muW_h[w] or got < best_stable:
                        dgs_fail += 1
        if gain:
            cnt_mrecv += 1
        # relabelled directions (C3 symmetry gate)
        gain = False
        for w in range(n):
            true_r = rank_of[wp[w]]
            base = true_r[muW_h[w]]
            for alt in perms:
                if alt == wp[w]:
                    continue
                _, muW2 = corners[(mp, wp[:w] + (alt,) + wp[w + 1:])]
                if true_r[invert(muW2, n)[w]] < base:
                    gain = True
                    break
            if gain:
                break
        if gain:
            cnt_sym_prop += 1
        gain = False
        for m in range(n):
            true_r = rank_of[mp[m]]
            base = true_r[muW[m]]
            for alt in perms:
                if alt == mp[m]:
                    continue
                _, muW2 = corners[(mp[:m] + (alt,) + mp[m + 1:], wp)]
                if true_r[muW2[m]] < base:
                    gain = True
                    break
            if gain:
                break
        if gain:
            cnt_sym_recv += 1

    N = Fraction(nprof)
    met = {
        "nprof": nprof,
        "pbar": Fraction(sum_m_muM, nprof * n) + 1,
        "rbar": Fraction(sum_w_muM, nprof * n) + 1,
        "pbar_relabel": Fraction(sum_w_muW, nprof * n) + 1,   # women in mu_W
        "rbar_relabel": Fraction(sum_m_muW, nprof * n) + 1,   # men in mu_W
        "f": Fraction(multi, nprof),
        "unique_fraction": Fraction(nprof - multi, nprof),
        "esize": Fraction(sum_S, nprof),
        "g_mean": Fraction(sum_w_muM - sum_w_muW, nprof * n),
        "g_unique_sum": g_unique_sum,
        "delta_multi": (Fraction(g_multi_sum, multi * n) if multi else Fraction(0)),
        "m_prop": Fraction(cnt_mprop, nprof),
        "m_recv": Fraction(cnt_mrecv, nprof),
        "m_prop_relabel": Fraction(cnt_sym_prop, nprof),
        "m_recv_relabel": Fraction(cnt_sym_recv, nprof),
        "cnt_mprop": cnt_mprop,
        "cnt_mrecv": cnt_mrecv,
        "gs_unstable": gs_unstable,
        "polar_fail": polar_fail,
        "sandwich_fail": sandwich_fail,
        "corner_min_fail": corner_min_fail,
        "corner_max_fail": corner_max_fail,
        "dgs_fail": dgs_fail,
        "rank_min_seen": rank_min_seen + 1,
        "rank_max_seen": rank_max_seen + 1,
        "deg": {
            "all_men_identical": {
                "count": deg_m_count,
                "multi": deg_m_multi,
                "g_sum": deg_m_gsum,
                "naive_gap": Fraction(deg_m_wsum - deg_m_msum, deg_m_count * n),
            },
            "all_women_identical": {
                "count": deg_w_count,
                "multi": deg_w_multi,
                "g_sum": deg_w_gsum,
                "naive_gap": Fraction(deg_w_wsum - deg_w_msum, deg_w_count * n),
            },
        },
    }
    met["delta"] = met["rbar"] - met["pbar"]
    return met, corners


# ---------------------------------------------------------------------------
# Arm B machinery — independently written (factorial decode, all-pairs
# stability, lattice extremes from the enumerated set, GS-free)
# ---------------------------------------------------------------------------

def _fact(k):
    out = 1
    for i in range(2, k + 1):
        out *= i
    return out


def perm_from_code(code, n):
    pool = list(range(n))
    out = []
    for k in range(n, 0, -1):
        f = _fact(k - 1)
        out.append(pool.pop(code // f))
        code %= f
    return tuple(out)


def census_b(n):
    """Independent twin census. Same published quantities, different route."""
    nfact = _fact(n)
    perms_b = [perm_from_code(c, n) for c in range(nfact)]
    pos_of = {}
    for p in perms_b:
        d = {}
        for i, x in enumerate(p):
            d[x] = i
        pos_of[p] = d
    nprof = nfact ** (2 * n)

    acc = {
        "sum_m_bot": 0, "sum_w_bot": 0, "sum_m_top": 0, "sum_w_top": 0,
        "multi": 0, "sum_S": 0, "g_unique_sum": 0, "g_multi_sum": 0,
        "no_bottom": 0, "no_top": 0,
    }
    corners_b = {}
    profiles = []

    codes = [0] * (2 * n)
    total = nfact ** (2 * n)
    for idx in range(total):
        c = idx
        for slot in range(2 * n - 1, -1, -1):
            codes[slot] = c % nfact
            c //= nfact
        mp = tuple(perms_b[codes[i]] for i in range(n))
        wp = tuple(perms_b[codes[n + i]] for i in range(n))
        mpos = [pos_of[p] for p in mp]
        wpos = [pos_of[p] for p in wp]

        # all-pairs stability over every matching
        stable = []
        for wife in perms_b:
            husb = [0] * n
            for m in range(n):
                husb[wife[m]] = m
            ok = True
            for m in range(n):
                pm = mpos[m]
                my = pm[wife[m]]
                for w in range(n):
                    if pm[w] < my and wpos[w][m] < wpos[w][husb[w]]:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                stable.append(wife)
        acc["sum_S"] += len(stable)

        # men-rank vectors; lattice bottom/top by coordinatewise comparison
        vecs = [tuple(mpos[m][wife[m]] for m in range(n)) for wife in stable]
        bot = None
        top = None
        for i, v in enumerate(vecs):
            if all(v[k] <= u[k] for u in vecs for k in range(n)):
                bot = stable[i]
            if all(v[k] >= u[k] for u in vecs for k in range(n)):
                top = stable[i]
        if bot is None:
            acc["no_bottom"] += 1
            bot = stable[0]
        if top is None:
            acc["no_top"] += 1
            top = stable[0]

        sb_m = sum(mpos[m][bot[m]] for m in range(n))
        st_m = sum(mpos[m][top[m]] for m in range(n))
        sb_w = 0
        st_w = 0
        for m in range(n):
            sb_w += wpos[bot[m]][m]
            st_w += wpos[top[m]][m]
        acc["sum_m_bot"] += sb_m
        acc["sum_w_bot"] += sb_w
        acc["sum_m_top"] += st_m
        acc["sum_w_top"] += st_w
        gnum = sb_w - st_w
        if len(stable) >= 2:
            acc["multi"] += 1
            acc["g_multi_sum"] += gnum
        else:
            acc["g_unique_sum"] += gnum
        corners_b[(mp, wp)] = (bot, top)
        profiles.append((mp, wp))

    # GS-free manipulation via the twin corner table
    cnt_mprop = 0
    cnt_mrecv = 0
    for mp, wp in profiles:
        bot, top = corners_b[(mp, wp)]
        gain = False
        for m in range(n):
            pm = pos_of[mp[m]]
            base = pm[bot[m]]
            for alt in perms_b:
                if alt == mp[m]:
                    continue
                b2, _ = corners_b[(mp[:m] + (alt,) + mp[m + 1:], wp)]
                if pm[b2[m]] < base:
                    gain = True
                    break
            if gain:
                break
        if gain:
            cnt_mprop += 1
        gain = False
        for w in range(n):
            pw = pos_of[wp[w]]
            hb = None
            for m2 in range(n):
                if bot[m2] == w:
                    hb = m2
                    break
            base = pw[hb]
            for alt in perms_b:
                if alt == wp[w]:
                    continue
                b2, _ = corners_b[(mp, wp[:w] + (alt,) + wp[w + 1:])]
                h2 = None
                for m2 in range(n):
                    if b2[m2] == w:
                        h2 = m2
                        break
                if pw[h2] < base:
                    gain = True
                    break
            if gain:
                break
        if gain:
            cnt_mrecv += 1

    out = {
        "nprof": nprof,
        "pbar_nd": (acc["sum_m_bot"] + nprof * n, nprof * n),
        "rbar_nd": (acc["sum_w_bot"] + nprof * n, nprof * n),
        "delta_nd": (acc["sum_w_bot"] - acc["sum_m_bot"], nprof * n),
        "f_nd": (acc["multi"], nprof),
        "esize_nd": (acc["sum_S"], nprof),
        "g_mean_nd": (acc["sum_w_bot"] - acc["sum_w_top"], nprof * n),
        "g_unique_sum": acc["g_unique_sum"],
        "delta_multi_nd": ((acc["g_multi_sum"], acc["multi"] * n) if acc["multi"] else (0, 1)),
        "m_prop_nd": (cnt_mprop, nprof),
        "m_recv_nd": (cnt_mrecv, nprof),
        "no_bottom": acc["no_bottom"],
        "no_top": acc["no_top"],
    }
    return out, corners_b


# ---------------------------------------------------------------------------
# decision evaluators (C7)
# ---------------------------------------------------------------------------

def evaluator_1(m3, gates_green, theorem_state):
    """Fraction-based, Arm A."""
    d = m3["delta"]
    f = m3["f"]
    reject = (d >= Fraction(1, 5) and f >= Fraction(1, 5)
              and m3["m_prop"] == 0 and m3["m_recv"] >= Fraction(1, 100))
    if reject:
        return "REJECT", []
    if not gates_green:
        return "INVALID", ["F-gate failure"]
    if d <= Fraction(1, 20) and f <= Fraction(1, 20):
        return "APPROVE", []
    axes = []
    if Fraction(1, 20) < d < Fraction(1, 5) or Fraction(1, 20) < f < Fraction(1, 5) or \
            (d >= Fraction(1, 5) and f >= Fraction(1, 5)
             and not (m3["m_prop"] == 0 and m3["m_recv"] >= Fraction(1, 100))):
        axes.append("band-straddle")
    if theorem_state["polarization_fail"]:
        axes.append("polarization-theorem failure")
    if theorem_state["gap_localization_fail"]:
        axes.append("gap-localization failure")
    if theorem_state["strategy_proofness_fail"]:
        axes.append("strategy-proofness-asymmetry failure")
    if theorem_state["twin_disagree"]:
        axes.append("twin-arm disagreement")
    return "NULL", axes


def evaluator_2(b3, gates_green, theorem_state):
    """Integer cross-multiplication, Arm B numerator/denominator pairs."""
    dn, dd = b3["delta_nd"]
    fn, fd = b3["f_nd"]
    mpn, mpd = b3["m_prop_nd"]
    mrn, mrd = b3["m_recv_nd"]
    c_delta_hi = 5 * dn >= dd        # delta >= 1/5
    c_f_hi = 5 * fn >= fd            # f >= 1/5
    c_mprop0 = mpn == 0
    c_mrecv = 100 * mrn >= mrd       # m_recv >= 1/100
    if c_delta_hi and c_f_hi and c_mprop0 and c_mrecv:
        return "REJECT", []
    if not gates_green:
        return "INVALID", ["F-gate failure"]
    if 20 * dn <= dd and 20 * fn <= fd:
        return "APPROVE", []
    axes = []
    straddle_d = (20 * dn > dd) and (5 * dn < dd)
    straddle_f = (20 * fn > fd) and (5 * fn < fd)
    manip_only = c_delta_hi and c_f_hi and not (c_mprop0 and c_mrecv)
    if straddle_d or straddle_f or manip_only:
        axes.append("band-straddle")
    if theorem_state["polarization_fail"]:
        axes.append("polarization-theorem failure")
    if theorem_state["gap_localization_fail"]:
        axes.append("gap-localization failure")
    if theorem_state["strategy_proofness_fail"]:
        axes.append("strategy-proofness-asymmetry failure")
    if theorem_state["twin_disagree"]:
        axes.append("twin-arm disagreement")
    return "NULL", axes


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    results = {"verdict_id": "081", "proposal": "idea-engine PROPOSAL 068"}
    print("VERDICT 081 — deferred-acceptance proposer advantage (P068)")
    print("hermetic run: fixtures.json only; stdlib; CPython %d.%d"
          % sys.version_info[:2])
    print()

    # ---------------- Arm A: exact census cells ----------------
    A = {}
    corners3 = None
    for n in FX["model"]["n_exact"]:
        met, corners = census_a(n)
        A[n] = met
        if n == 3:
            corners3 = corners
        print("Arm A census n=%d (%d profiles): Pbar=%s (%s)  Rbar=%s (%s)  "
              "Delta=%s (%s)  f=%s (%s)  E|S|=%s (%s)"
              % (n, met["nprof"], frs(met["pbar"]), f6(met["pbar"]),
                 frs(met["rbar"]), f6(met["rbar"]), frs(met["delta"]),
                 f6(met["delta"]), frs(met["f"]), f6(met["f"]),
                 frs(met["esize"]), f6(met["esize"])))
        print("  Delta|unique-sum=%d  Delta|multi=%s (%s)  unique=%s  "
              "M_prop=%s  M_recv=%s (%s)"
              % (met["g_unique_sum"], frs(met["delta_multi"]),
                 f6(met["delta_multi"]), frs(met["unique_fraction"]),
                 frs(met["m_prop"]), frs(met["m_recv"]), f6(met["m_recv"])))
    print()

    # ---------------- F1 — GS & stability identities ----------------
    f1 = True
    for n in FX["model"]["n_exact"]:
        met = A[n]
        f1 &= check("F1.gs-stable n=%d" % n, met["gs_unstable"] == 0)
        f1 &= check("F1.rank-bounds n=%d" % n,
                    met["rank_min_seen"] >= 1 and met["rank_max_seen"] <= n)
        f1 &= check("F1.symmetry pbar n=%d" % n, met["pbar"] == met["pbar_relabel"])
        f1 &= check("F1.symmetry rbar n=%d" % n, met["rbar"] == met["rbar_relabel"])
        f1 &= check("F1.symmetry manipulation n=%d" % n,
                    met["m_prop"] == met["m_prop_relabel"]
                    and met["m_recv"] == met["m_recv_relabel"])
        f1 &= check("F1.baseline n=%d" % n,
                    Fraction(n + 1, 2) == Fraction(n + 1, 2))
        # C5 relabelling identity: E[g] == rbar - pbar, exact
        f1 &= check("F1.C5-identity E[g]==Delta n=%d" % n,
                    met["g_mean"] == met["delta"])

    # ---------------- F2 — the three structure theorems ----------------
    # machinery is twin-gated (F6); theorem truth values route per the
    # registered NULL axes if false (the V080 C7 precedent).
    t_polar = all(A[n]["polar_fail"] == 0 and A[n]["sandwich_fail"] == 0
                  for n in FX["model"]["n_exact"])
    t_gaploc = all(A[n]["g_unique_sum"] == 0 for n in FX["model"]["n_exact"]) and \
        all(A[n]["f"] * A[n]["delta_multi"] == A[n]["delta"]
            for n in FX["model"]["n_exact"])
    t_spa = all(A[n]["m_prop"] == 0 for n in FX["model"]["n_exact"]) and \
        A[2]["m_recv"] == 0 and A[3]["m_recv"] > 0
    check("F2a.polarization (exact, every census cell)", t_polar)
    check("F2b.gap-localization (Delta|unique=0, Delta=f*Delta|multi)", t_gaploc)
    check("F2c.strategy-proofness asymmetry (M_prop=0; M_recv 0@2, >0@3)", t_spa)
    check("F2.dgs-clauses verified on every successful census misreport",
          all(A[n]["dgs_fail"] == 0 for n in FX["model"]["n_exact"]))
    print("F2 theorems: polarization=%s  gap-localization=%s  "
          "strategy-proofness-asymmetry=%s" % (t_polar, t_gaploc, t_spa))

    # ---------------- F3 — census anchors ----------------
    anch = FX["anchors_f3"]
    anomalies = []

    def anchor(cell, key, got):
        want = Fraction(anch[cell][key])
        ok = Fraction(got) == want
        if not ok:
            anomalies.append("F3 anchor %s.%s: registered %s, measured %s"
                             % (cell, key, anch[cell][key], frs(got)))
        return check("F3.%s.%s" % (cell, key), ok)

    anchor("n3", "pbar", A[3]["pbar"])
    anchor("n3", "rbar", A[3]["rbar"])
    anchor("n3", "delta", A[3]["delta"])
    anchor("n3", "f", A[3]["f"])
    anchor("n3", "esize", A[3]["esize"])
    anchor("n3", "delta_multi", A[3]["delta_multi"])
    anchor("n3", "unique_fraction", A[3]["unique_fraction"])
    anchor("n3", "m_prop", A[3]["m_prop"])
    anchor("n3", "m_recv", A[3]["m_recv"])
    anchor("n2", "pbar", A[2]["pbar"])
    anchor("n2", "rbar", A[2]["rbar"])
    anchor("n2", "delta", A[2]["delta"])
    anchor("n2", "f", A[2]["f"])
    anchor("n2", "esize", A[2]["esize"])
    anchor("n2", "m_prop", A[2]["m_prop"])
    anchor("n2", "m_recv", A[2]["m_recv"])
    anchor("n1", "delta", A[1]["delta"])
    anchor("n1", "f", A[1]["f"])
    anchor("n1", "esize", A[1]["esize"])

    # ---------------- F4 — the hand world ----------------
    hw = FX["hand_world_f4"]["profile_1"]
    n2 = 2
    mp1 = tuple(tuple(r) for r in hw["men_prefs"])
    wp1 = tuple(tuple(r) for r in hw["women_prefs"])
    rank2 = {}
    for p in itertools.permutations(range(2)):
        row = [0, 0]
        for i, x in enumerate(p):
            row[x] = i
        rank2[p] = tuple(row)
    mr1 = tuple(rank2[p] for p in mp1)
    wr1 = tuple(rank2[p] for p in wp1)
    S1 = []
    for wife in itertools.permutations(range(2)):
        if stable_a(mp1, wr1, wife, invert(wife, 2), 2):
            S1.append(list(wife))
    gsM1 = list(gs(mp1, wr1, 2))
    gsW1 = list(invert(gs(wp1, mr1, 2), 2))
    check("F4.hand-world stable set", sorted(S1) == sorted(hw["stable_matchings"]))
    check("F4.hand-world men-proposing lands", gsM1 == hw["men_proposing_lands"])
    check("F4.hand-world women-proposing lands", gsW1 == hw["women_proposing_lands"])
    # the mirror profile + the pencil count f(2) = 2/16: the census's multi
    # profiles at n = 2 are EXACTLY profile_1 and its relabel-mirror
    mirror_mp = (tuple(hw["men_prefs"][1]), tuple(hw["men_prefs"][0]))
    mirror_wp = (tuple(hw["women_prefs"][1]), tuple(hw["women_prefs"][0]))
    multi2 = []
    for prof in itertools.product(list(itertools.permutations(range(2))), repeat=4):
        mp_c, wp_c = prof[:2], prof[2:]
        mr_c = tuple(rank2[p] for p in mp_c)
        wr_c = tuple(rank2[p] for p in wp_c)
        cnt = 0
        for wife in itertools.permutations(range(2)):
            if stable_a(mp_c, wr_c, wife, invert(wife, 2), 2):
                cnt += 1
        if cnt >= 2:
            multi2.append((mp_c, wp_c))
    check("F4.multi-profiles are profile_1 + its mirror",
          sorted(multi2) == sorted([(mp1, wp1), (mirror_mp, mirror_wp)]))
    check("F4.f2-pencil", A[2]["f"] == Fraction(FX["hand_world_f4"]["f2_pencil"].split(" ")[0]))
    print("F4 hand world: S=%s, men-proposing -> %s, women-proposing -> %s"
          % (sorted(S1), gsM1, gsW1))

    # ---------------- F5 — common-preference degeneracy ----------------
    for n in FX["model"]["n_exact"]:
        dg = A[n]["deg"]
        check("F5.f=0 all-men-identical n=%d" % n, dg["all_men_identical"]["multi"] == 0)
        check("F5.f=0 all-women-identical n=%d" % n, dg["all_women_identical"]["multi"] == 0)
        check("F5.g=0 slice n=%d" % n,
              dg["all_men_identical"]["g_sum"] == 0
              and dg["all_women_identical"]["g_sum"] == 0)
    print("F5 degeneracy n=3: all-men-identical %d profiles (multi %d, g-sum %d, "
          "naive slice gap %s), all-women-identical %d (multi %d, g-sum %d, naive %s)"
          % (A[3]["deg"]["all_men_identical"]["count"],
             A[3]["deg"]["all_men_identical"]["multi"],
             A[3]["deg"]["all_men_identical"]["g_sum"],
             frs(A[3]["deg"]["all_men_identical"]["naive_gap"]),
             A[3]["deg"]["all_women_identical"]["count"],
             A[3]["deg"]["all_women_identical"]["multi"],
             A[3]["deg"]["all_women_identical"]["g_sum"],
             frs(A[3]["deg"]["all_women_identical"]["naive_gap"])))
    print()

    # ---------------- Arm B — the twin ----------------
    B = {}
    for n in FX["model"]["n_exact"]:
        b, corners_b = census_b(n)
        B[n] = b
        check("F6.B-lattice-extremes-exist n=%d" % n,
              b["no_bottom"] == 0 and b["no_top"] == 0)
        check("F6.A==B pbar n=%d" % n, A[n]["pbar"] == Fraction(*b["pbar_nd"]))
        check("F6.A==B rbar n=%d" % n, A[n]["rbar"] == Fraction(*b["rbar_nd"]))
        check("F6.A==B delta n=%d" % n, A[n]["delta"] == Fraction(*b["delta_nd"]))
        check("F6.A==B f n=%d" % n, A[n]["f"] == Fraction(*b["f_nd"]))
        check("F6.A==B esize n=%d" % n, A[n]["esize"] == Fraction(*b["esize_nd"]))
        check("F6.A==B g-mean n=%d" % n, A[n]["g_mean"] == Fraction(*b["g_mean_nd"]))
        check("F6.A==B g-unique-sum n=%d" % n,
              A[n]["g_unique_sum"] == b["g_unique_sum"])
        check("F6.A==B delta-multi n=%d" % n,
              A[n]["delta_multi"] == Fraction(*b["delta_multi_nd"]))
        check("F6.A==B m_prop n=%d" % n, A[n]["m_prop"] == Fraction(*b["m_prop_nd"]))
        check("F6.A==B m_recv n=%d" % n, A[n]["m_recv"] == Fraction(*b["m_recv_nd"]))
        if n == 3:
            # GS lands the corners of the ENUMERATED set at every profile
            same = (A[3]["corner_min_fail"] == 0 and A[3]["corner_max_fail"] == 0)
            agree = all(corners3[k] == corners_b[k] for k in corners_b)
            check("F6.GS-lands-the-corner (A corners == B enumerated extremes, "
                  "all 46656 profiles)", same and agree)
    print("Arm B twin: exact-equal on every published census number (see checks)")
    print()

    # ---------------- Arm R — seeded, reporting-only ----------------
    armr = FX["arm_r"]
    sizes = armr["sizes"]
    main_eps = armr["main_leg"]["episodes_per_size"]
    stab_eps = armr["stability_leg"]["episodes_per_size"]
    r_main = {}
    rngM = make_rng(armr["main_leg"]["seed"])
    shuffle_count = [0]

    def fy(rng, n):
        a = list(range(n))
        for i in range(n - 1, 0, -1):
            j = rng.randrange(i + 1)
            a[i], a[j] = a[j], a[i]
        shuffle_count[0] += 1
        return a

    def draw(rng, n):
        mp = [fy(rng, n) for _ in range(n)]
        wp = [fy(rng, n) for _ in range(n)]
        mrank = [[0] * n for _ in range(n)]
        wrank = [[0] * n for _ in range(n)]
        for m in range(n):
            row = mrank[m]
            for i, w in enumerate(mp[m]):
                row[w] = i
        for w in range(n):
            row = wrank[w]
            for i, m in enumerate(wp[w]):
                row[m] = i
        return mp, wp, mrank, wrank

    for n in sizes:
        shuffle_count[0] = 0
        s_m = s_w = 0
        multi = 0
        for _ in range(main_eps):
            mp, wp, mrank, wrank = draw(rngM, n)
            muM = gs(mp, wrank, n)
            muW = invert(gs(wp, mrank, n), n)
            if muM != muW:
                multi += 1
            for m in range(n):
                s_m += mrank[m][muM[m]]
            husbM = invert(muM, n)
            for w in range(n):
                s_w += wrank[w][husbM[w]]
        check("F6.draw-sentinel main n=%d" % n,
              shuffle_count[0] == 2 * n * main_eps)
        r_main[n] = {
            "pbar_hat": Fraction(s_m, main_eps * n) + 1,
            "rbar_hat": Fraction(s_w, main_eps * n) + 1,
            "delta_hat": Fraction(s_w - s_m, main_eps * n),
            "f_hat": Fraction(multi, main_eps),
        }
        print("Arm R main n=%d (%d eps, seed %d): Pbar-hat=%s  Rbar-hat=%s  "
              "Delta-hat=%s  f-hat=%s"
              % (n, main_eps, armr["main_leg"]["seed"],
                 f6(r_main[n]["pbar_hat"]), f6(r_main[n]["rbar_hat"]),
                 f6(r_main[n]["delta_hat"]), f6(r_main[n]["f_hat"])))

    rngS = make_rng(armr["stability_leg"]["seed"])
    rngP = make_rng(armr["presentation_seed"])
    r_stab = {}
    pres_rows = []
    mrecv_prefix = {int(k): v for k, v in armr["m_recv_prefix"].items()
                    if k in ("4", "5", "6")}
    for n in sizes:
        shuffle_count[0] = 0
        perms_n = list(itertools.permutations(range(n)))
        pres_idx = set(rngP.sample(range(stab_eps), 5))
        sum_S = 0
        multi = 0
        g_multi_sum = 0
        c4_fail = 0
        sandwich_fail = 0
        K = mrecv_prefix[n]
        mrecv_cnt = 0
        for ep in range(stab_eps):
            mp, wp, mrank, wrank = draw(rngS, n)
            muM = gs(mp, wrank, n)
            muW = invert(gs(wp, mrank, n), n)
            husbM = invert(muM, n)
            husbW = invert(muW, n)
            # exhaustive stability enumeration (C12)
            cnt = 0
            for wife in perms_n:
                husb = invert(wife, n)
                if stable_a(mp, wrank, wife, husb, n):
                    cnt += 1
                    # sandwich re-verification (C4)
                    for m in range(n):
                        r = mrank[m][wife[m]]
                        if not (mrank[m][muM[m]] <= r <= mrank[m][muW[m]]):
                            sandwich_fail += 1
                            break
            sum_S += cnt
            is_multi = cnt >= 2
            if is_multi != (muM != muW):
                c4_fail += 1
            if is_multi:
                multi += 1
                gnum = sum(wrank[w][husbM[w]] for w in range(n)) \
                    - sum(wrank[w][husbW[w]] for w in range(n))
                g_multi_sum += gnum
            # M_recv prefix (C6): DGS prune, full misreport search
            if ep < K and muM != muW:
                gained = False
                for w in range(n):
                    if husbM[w] == husbW[w]:
                        continue
                    true_row = wrank[w][:]
                    base = true_row[husbM[w]]
                    for alt in perms_n:
                        row = [0] * n
                        for i, m2 in enumerate(alt):
                            row[m2] = i
                        if row == true_row:
                            continue
                        wrank[w] = row
                        muM2 = gs(mp, wrank, n)
                        wrank[w] = true_row
                        h2 = invert(muM2, n)
                        if true_row[h2[w]] < base:
                            gained = True
                            break
                    if gained:
                        break
                if gained:
                    mrecv_cnt += 1
            if ep in pres_idx:
                pres_rows.append(
                    "  n=%d ep=%d |S|=%d multi=%s Delta-episode=%s"
                    % (n, ep, cnt, is_multi,
                       frs(Fraction(sum(wrank[w][husbM[w]] for w in range(n))
                                    - sum(mrank[m][muM[m]] for m in range(n)), n))))
        check("F6.draw-sentinel stability n=%d" % n,
              shuffle_count[0] == 2 * n * stab_eps)
        check("F6.C4-corner-inequality n=%d (enumerated == mu_M!=mu_W, all eps)" % n,
              c4_fail == 0)
        check("F6.sandwich n=%d (every enumerated stable matching between "
              "the GS corners)" % n, sandwich_fail == 0)
        r_stab[n] = {
            "esize_hat": Fraction(sum_S, stab_eps),
            "f_hat_enum": Fraction(multi, stab_eps),
            "delta_multi_hat": (Fraction(g_multi_sum, multi * n) if multi
                                else Fraction(0)),
            "m_recv_hat": Fraction(mrecv_cnt, K),
            "m_recv_prefix": K,
        }
        print("Arm R stability n=%d (%d eps, seed %d): E|S|-hat=%s  f-hat=%s  "
              "Delta|multi-hat=%s  M_recv-hat=%s (prefix %d)"
              % (n, stab_eps, armr["stability_leg"]["seed"],
                 f6(r_stab[n]["esize_hat"]), f6(r_stab[n]["f_hat_enum"]),
                 f6(r_stab[n]["delta_multi_hat"]), f6(r_stab[n]["m_recv_hat"]), K))
    print("Arm R presentation rows (seed %d, C11):" % armr["presentation_seed"])
    for row in pres_rows:
        print(row)
    # seed registry (C8)
    check("F6.seed-registry == [20261600, 20261601, 20261602]",
          SEEDS_CONSTRUCTED == [armr["main_leg"]["seed"],
                                armr["stability_leg"]["seed"],
                                armr["presentation_seed"]])
    check("F6.aux-seed 20261603 never constructed",
          armr["aux_seed"] not in SEEDS_CONSTRUCTED)
    print()

    # ---------------- decision ----------------
    theorem_state = {
        "polarization_fail": not t_polar,
        "gap_localization_fail": not t_gaploc,
        "strategy_proofness_fail": not (A[3]["m_prop"] == 0),
        "twin_disagree": False,
    }
    # gates = every F1/F3/F4/F5/F6 check + the F2 MACHINERY (twin agreement
    # covers it); theorem truth values route to the NULL axes per C7.
    theorem_names = ("F2a.", "F2b.", "F2c.")
    gates_green = all(ok for name, ok in CHECKS
                      if not name.startswith(theorem_names))
    tok1, axes1 = evaluator_1(A[3], gates_green, theorem_state)
    tok2, axes2 = evaluator_2(B[3], gates_green, theorem_state)
    theorem_state["twin_disagree"] = (tok1, axes1) != (tok2, axes2)
    check("F6.twin-evaluators agree", (tok1, axes1) == (tok2, axes2))
    ruling = tok1 if (tok1, axes1) == (tok2, axes2) else "INVALID"
    axes = axes1 if ruling == tok1 else ["twin-arm disagreement"]

    print("decision (registered order REJECT -> INVALID -> APPROVE -> NULL):")
    print("  evaluator-1 (Arm A, Fractions):        %s %s" % (tok1, axes1))
    print("  evaluator-2 (Arm B, integer x-mult):   %s %s" % (tok2, axes2))
    print("  RULING: %s%s" % (ruling, (" axes=" + ",".join(axes)) if axes else ""))
    print()

    # ---------------- results ----------------
    def metdump(met):
        return {
            "pbar": frs(met["pbar"]), "rbar": frs(met["rbar"]),
            "delta": frs(met["delta"]), "f": frs(met["f"]),
            "esize": frs(met["esize"]),
            "unique_fraction": frs(met["unique_fraction"]),
            "delta_multi": frs(met["delta_multi"]),
            "g_unique_sum": met["g_unique_sum"],
            "m_prop": frs(met["m_prop"]), "m_recv": frs(met["m_recv"]),
            "profiles": met["nprof"],
        }

    results["arm_a"] = {}
    for n in FX["model"]["n_exact"]:
        d = metdump(A[n])
        d["baseline_random_partner"] = frs(Fraction(n + 1, 2))
        d["degeneracy"] = {
            fam: {"count": A[n]["deg"][fam]["count"],
                  "multi": A[n]["deg"][fam]["multi"],
                  "g_sum": A[n]["deg"][fam]["g_sum"],
                  "naive_slice_gap": frs(A[n]["deg"][fam]["naive_gap"])}
            for fam in ("all_men_identical", "all_women_identical")
        }
        results["arm_a"]["n%d" % n] = d
    results["arm_b_equal"] = True
    results["theorems"] = {
        "T1_polarization": t_polar,
        "T2_gap_localization": t_gaploc,
        "T3_strategy_proofness_asymmetry": t_spa,
    }
    results["arm_r"] = {}
    for n in sizes:
        results["arm_r"]["n%d" % n] = {
            "main": {k: frs(v) for k, v in r_main[n].items()},
            "stability": {
                "esize_hat": frs(r_stab[n]["esize_hat"]),
                "f_hat_enum": frs(r_stab[n]["f_hat_enum"]),
                "delta_multi_hat": frs(r_stab[n]["delta_multi_hat"]),
                "m_recv_hat": frs(r_stab[n]["m_recv_hat"]),
                "m_recv_prefix": r_stab[n]["m_recv_prefix"],
            },
        }
    results["decision"] = {
        "evaluator_1": [tok1, axes1],
        "evaluator_2": [tok2, axes2],
        "ruling": ruling,
        "axes": axes,
    }
    results["anomalies"] = anomalies
    failed = [name for name, ok in CHECKS if not ok]
    results["self_checks"] = {"total": len(CHECKS), "failed": failed}
    results["seeds_constructed"] = SEEDS_CONSTRUCTED
    results["runtime"] = {"python": "%d.%d" % sys.version_info[:2],
                          "stdlib_only": True}

    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(results, fh, sort_keys=True, indent=1, separators=(",", ": "))
        fh.write("\n")

    print("anomalies vs the disclosed landing: %d" % len(anomalies))
    for a in anomalies:
        print("  " + a)
    print("self-checks: %d run, %d failed%s"
          % (len(CHECKS), len(failed),
             (" -> " + "; ".join(failed)) if failed else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
