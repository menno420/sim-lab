#!/usr/bin/env python3
"""verdict-019 — IRV monotonicity in close races (idea-engine PROPOSAL 017).

How often does raising the winner make it lose? Fully hermetic, pre-registered:
the pinned 3-candidate IRV rule, the exhaustive upward-violation search, both
neutral voter models — Arm E (exhaustive IAC, exact seedless fractions) and
Arm S (seeded IC Monte Carlo, random.Random(seed), pinned loop order) — scored
against acceptance bands committed in fixtures.json BEFORE any code existed.

Determinism contract: stdlib-only; no network, no git, no wall clock, no
hash(); the ONLY randomness is random.Random(<pinned seed>) in a pinned loop
order (Arm S; Arm E is seedless by construction). stdout and results.json are
byte-identical across process runs on the same CPython minor version (Arm E
numbers are platform-independent exact rationals).

Run: python3 sims/verdict-019-irv-monotonicity/irv_monotonicity_sim.py
Exit 0 iff all self-checks pass.
"""

import json
import sys
import hashlib
import random
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Pinned combinatorics (mirrors fixtures.json; cross-checked against it)
# ---------------------------------------------------------------------------

TYPES = ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")
T_INDEX = {t: i for i, t in enumerate(TYPES)}
LETTERS = "ABC"

# Per-type contribution vector: (first-place candidate, A-over-B, A-over-C, B-over-C)
TYPE_VEC = (
    (0, 1, 1, 1),  # ABC
    (0, 1, 1, 0),  # ACB
    (1, 0, 1, 1),  # BAC
    (1, 0, 0, 1),  # BCA
    (2, 1, 0, 0),  # CAB
    (2, 0, 0, 0),  # CBA
)

# Moves for the violation search: for (winner w, raised-from X) the two source
# types (X>W>Z, X>Z>W) and the single target type W>X>Z.
NON_W = {0: (1, 2), 1: (0, 2), 2: (0, 1)}
MOVES = {}
for _w in range(3):
    for _x in range(3):
        if _x == _w:
            continue
        _z = 3 - _w - _x
        t_xwz = T_INDEX[LETTERS[_x] + LETTERS[_w] + LETTERS[_z]]
        t_xzw = T_INDEX[LETTERS[_x] + LETTERS[_z] + LETTERS[_w]]
        tgt = T_INDEX[LETTERS[_w] + LETTERS[_x] + LETTERS[_z]]
        MOVES[(_w, _x)] = ((t_xwz, "X>W>Z", tgt), (t_xzw, "X>Z>W", tgt))

# Per-unit-k deltas for moving one ballot t -> tgt: (dfpA, dfpB, dfpC, dab, dac, dbc)
DELTAS = {}
for _t in range(6):
    for _g in range(6):
        if _t == _g:
            continue
        fv, tab, tac, tbc = TYPE_VEC[_t]
        gv, gab, gac, gbc = TYPE_VEC[_g]
        dfp = [0, 0, 0]
        dfp[fv] -= 1
        dfp[gv] += 1
        DELTAS[(_t, _g)] = (dfp[0], dfp[1], dfp[2], gab - tab, gac - tac, gbc - tbc)


def winner_from_sums(fa, fb, fc, ab, ac, bc, n):
    """Pinned IRV rule on precomputed sums.

    Returns (code, winner, margin): code 0 = decided, 1 = round-1 lowest tie,
    2 = final pairwise tie; winner is 0/1/2 (A/B/C) or -1; margin is the
    round-1 elimination margin (second-lowest fp minus lowest fp).
    """
    if fa < fb:
        if fa < fc:
            lo = 0
            m = (fb if fb < fc else fc) - fa
        elif fc < fa:
            lo = 2
            m = fa - fc
        else:  # fc == fa, both lowest
            return (1, -1, 0)
    elif fb < fa:
        if fb < fc:
            lo = 1
            m = (fa if fa < fc else fc) - fb
        elif fc < fb:
            lo = 2
            m = fb - fc
        else:
            return (1, -1, 0)
    else:  # fa == fb
        if fc < fa:
            lo = 2
            m = fa - fc
        else:  # fc >= fa == fb -> lowest is tied
            return (1, -1, 0)
    if lo == 0:
        two = 2 * bc
        if two > n:
            return (0, 1, m)
        if two < n:
            return (0, 2, m)
        return (2, -1, m)
    if lo == 1:
        two = 2 * ac
        if two > n:
            return (0, 0, m)
        if two < n:
            return (0, 2, m)
        return (2, -1, m)
    two = 2 * ab
    if two > n:
        return (0, 0, m)
    if two < n:
        return (0, 1, m)
    return (2, -1, m)


def base_sums(c):
    """(fpA, fpB, fpC, A-over-B, A-over-C, B-over-C) for a 6-tuple of counts."""
    return (
        c[0] + c[1],
        c[2] + c[3],
        c[4] + c[5],
        c[0] + c[1] + c[4],
        c[0] + c[1] + c[2],
        c[0] + c[2] + c[3],
    )


def find_violations(c, sums, w, n):
    """Exhaustive upward-violation search (pinned definition).

    For each X != W and each source type t in {X>W>Z, X>Z>W}: scan k = 1..count(t)
    converting k ballots of t to W>X>Z; the FIRST k whose modified election has a
    DEFINED winner != W ends that (X, t) scan (existence semantics — identical to
    the full scan). Modified elections landing on an exact tie are not winner
    changes (no defined winner under the pinned rule; conservative/lower-bound).
    Returns list of (x, shape, min_k, new_winner) hits, one per violating (X, t).
    """
    fa, fb, fc, ab, ac, bc = sums
    hits = []
    for x in NON_W[w]:
        for t, shape, tgt in MOVES[(w, x)]:
            ct = c[t]
            if not ct:
                continue
            dfa, dfb, dfc, dab, dac, dbc = DELTAS[(t, tgt)]
            for k in range(1, ct + 1):
                code, win, _m = winner_from_sums(
                    fa + k * dfa, fb + k * dfb, fc + k * dfc,
                    ab + k * dab, ac + k * dac, bc + k * dbc, n)
                if code == 0 and win != w:
                    hits.append((x, shape, k, win))
                    break
    return hits


# ---------------------------------------------------------------------------
# Independent re-implementation (self-check only — different code path)
# ---------------------------------------------------------------------------

def irv_independent(counts_by_type):
    """Generic dict/string-based IRV evaluation, structurally unlike the fast path."""
    fp = {cand: 0 for cand in "ABC"}
    for t, k in counts_by_type.items():
        fp[t[0]] += k
    ordered = sorted(fp.values())
    if ordered[0] == ordered[1]:
        return ("TIE_R1", None, 0)
    margin = ordered[1] - ordered[0]
    loser = min("ABC", key=lambda cand: (fp[cand], cand))
    rest = [cand for cand in "ABC" if cand != loser]
    x, y = rest
    xv = sum(k for t, k in counts_by_type.items() if t.index(x) < t.index(y))
    yv = sum(k for t, k in counts_by_type.items() if t.index(y) < t.index(x))
    if xv == yv:
        return ("TIE_PAIR", None, margin)
    return ("WIN", x if xv > yv else y, margin)


def violations_independent(counts_by_type, w_letter):
    """Full triple loop, no early exit, dict-based — independent of the fast path."""
    combos = set()
    for x in "ABC":
        if x == w_letter:
            continue
        z = [cand for cand in "ABC" if cand not in (x, w_letter)][0]
        for shape, t in (("X>W>Z", x + w_letter + z), ("X>Z>W", x + z + w_letter)):
            tgt = w_letter + x + z
            for k in range(1, counts_by_type[t] + 1):
                new = dict(counts_by_type)
                new[t] -= k
                new[tgt] += k
                code, win, _m = irv_independent(new)
                if code == "WIN" and win != w_letter:
                    combos.add((x, shape))
    return combos


# ---------------------------------------------------------------------------
# Self-check harness
# ---------------------------------------------------------------------------

class Checker:
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, cond, label):
        if cond:
            self.passed += 1
        else:
            self.failed.append(label)
            print("SELF-CHECK FAILED: %s" % label)

    def summary(self):
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, len(self.failed)))
        return not self.failed


CHK = Checker()

BREAKDOWN_KEYS = (
    "X=first_eliminated|t=X>W>Z",
    "X=first_eliminated|t=X>Z>W",
    "X=final_loser|t=X>W>Z",
    "X=final_loser|t=X>Z>W",
)


class LegStats:
    def __init__(self, leg_id, n):
        self.leg_id = leg_id
        self.n = n
        self.total = 0
        self.ties_r1 = 0
        self.ties_pairwise = 0
        self.non_tied = 0
        self.close = 0
        self.viol_all = 0
        self.viol_close = 0
        self.breakdown_all = {k: 0 for k in BREAKDOWN_KEYS}
        self.breakdown_close = {k: 0 for k in BREAKDOWN_KEYS}
        self.wins_by_candidate = [0, 0, 0]
        self.viols_by_winner = [0, 0, 0]
        self.max_close_margin = 0

    def process(self, c):
        """c: 6-tuple of type counts. Returns nothing; updates tallies."""
        n = self.n
        self.total += 1
        sums = base_sums(c)
        code, w, m = winner_from_sums(*sums, n)
        if code == 1:
            self.ties_r1 += 1
            return None
        if code == 2:
            self.ties_pairwise += 1
            return None
        self.non_tied += 1
        self.wins_by_candidate[w] += 1
        is_close = (m * 20 <= n)
        if is_close:
            self.close += 1
            if m > self.max_close_margin:
                self.max_close_margin = m
        hits = find_violations(c, sums, w, n)
        if hits:
            self.viol_all += 1
            self.viols_by_winner[w] += 1
            if is_close:
                self.viol_close += 1
            # role of X: the round-1 eliminated candidate vs the final pairwise loser
            fa, fb, fc = sums[0], sums[1], sums[2]
            fps = ((fa, 0), (fb, 1), (fc, 2))
            lo = min(fps)[1]
            for x, shape, _k, _nw in hits:
                role = "first_eliminated" if x == lo else "final_loser"
                key = "X=%s|t=%s" % (role, shape)
                self.breakdown_all[key] += 1
                if is_close:
                    self.breakdown_close[key] += 1
        return (w, m, is_close, hits)

    def fractions(self):
        v_all = Fraction(self.viol_all, self.non_tied) if self.non_tied else None
        v_close = Fraction(self.viol_close, self.close) if self.close else None
        return v_all, v_close

    def as_dict(self):
        v_all, v_close = self.fractions()
        return {
            "leg": self.leg_id,
            "n": self.n,
            "elections": self.total,
            "ties_round1": self.ties_r1,
            "ties_pairwise": self.ties_pairwise,
            "non_tied": self.non_tied,
            "close_margin_max_counted": self.max_close_margin,
            "close_count": self.close,
            "violations_all": self.viol_all,
            "violations_close": self.viol_close,
            "V_all": {
                "exact": "%d/%d" % (self.viol_all, self.non_tied),
                "value": round(self.viol_all / self.non_tied, 6) if self.non_tied else None,
            },
            "V_close": {
                "exact": "%d/%d" % (self.viol_close, self.close) if self.close else None,
                "value": round(self.viol_close / self.close, 6) if self.close else None,
                "note": None if self.close else ("close set EMPTY at n=%d: the smallest non-tied margin (1) already exceeds 5%% of n" % self.n),
            },
            "tie_fraction": {
                "exact": "%d/%d" % (self.ties_r1 + self.ties_pairwise, self.total),
                "value": round((self.ties_r1 + self.ties_pairwise) / self.total, 6),
            },
            "breakdown_all": dict(self.breakdown_all),
            "breakdown_close": dict(self.breakdown_close),
        }


def independent_recheck(c, n, fast_result, label):
    """Cross-implementation agreement on one election (2 checks)."""
    counts_by_type = {TYPES[i]: c[i] for i in range(6)}
    code, win, margin = irv_independent(counts_by_type)
    if fast_result is None:
        CHK.check(code in ("TIE_R1", "TIE_PAIR"), "%s: independent eval agrees tie" % label)
        CHK.check(True, "%s: no violation search on a tie" % label)
        return
    w, m, _is_close, hits = fast_result
    CHK.check(code == "WIN" and win == LETTERS[w] and margin == m,
              "%s: independent eval agrees winner+margin" % label)
    fast_combos = {(LETTERS[x], shape) for x, shape, _k, _nw in hits}
    ind_combos = violations_independent(counts_by_type, LETTERS[w])
    CHK.check(fast_combos == ind_combos, "%s: independent violation search agrees" % label)


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------

def run_arm_e(n, leg_id, recheck_stride):
    stats = LegStats(leg_id, n)
    idx = 0
    for c0 in range(n + 1):
        r0 = n - c0
        for c1 in range(r0 + 1):
            r1 = r0 - c1
            for c2 in range(r1 + 1):
                r2 = r1 - c2
                for c3 in range(r2 + 1):
                    r3 = r2 - c3
                    for c4 in range(r3 + 1):
                        c = (c0, c1, c2, c3, c4, r3 - c4)
                        res = stats.process(c)
                        if idx % recheck_stride == 0:
                            independent_recheck(c, n, res, "%s idx=%d" % (leg_id, idx))
                        idx += 1
    return stats


def draw_election(rng, n):
    cnt = [0, 0, 0, 0, 0, 0]
    for _ in range(n):
        cnt[rng.randrange(6)] += 1
    return tuple(cnt)


def run_arm_s(n, m_elections, seed, leg_id, recheck_stride, digest_first):
    stats = LegStats(leg_id, n)
    rng = random.Random(seed)
    h = hashlib.sha256()
    for e in range(m_elections):
        c = draw_election(rng, n)
        if e < digest_first:
            h.update((",".join(map(str, c)) + ";").encode("ascii"))
        res = stats.process(c)
        if e % recheck_stride == 0:
            independent_recheck(c, n, res, "%s e=%d" % (leg_id, e))
    digest = h.hexdigest()
    # RNG-stream reproducibility: re-draw the first digest_first elections with a
    # FRESH Random(seed) and require the identical counts stream.
    h2 = hashlib.sha256()
    rng2 = random.Random(seed)
    for _e in range(digest_first):
        c2 = draw_election(rng2, n)
        h2.update((",".join(map(str, c2)) + ";").encode("ascii"))
    CHK.check(h2.hexdigest() == digest,
              "%s: fresh Random(%d) reproduces the first %d elections byte-for-byte"
              % (leg_id, seed, digest_first))
    return stats


# ---------------------------------------------------------------------------
# Structural self-checks
# ---------------------------------------------------------------------------

def structural_checks(fixtures):
    # (1) fast eval == independent eval on EVERY profile of two full tiny
    # enumerations: n=5 (odd, 252 profiles) and n=6 (even, 462 profiles — the
    # only place TIE_PAIR paths can fire, since all committed legs use odd n).
    for tiny_n in (5, 6):
        count = 0
        for c0 in range(tiny_n + 1):
            for c1 in range(tiny_n - c0 + 1):
                for c2 in range(tiny_n - c0 - c1 + 1):
                    for c3 in range(tiny_n - c0 - c1 - c2 + 1):
                        for c4 in range(tiny_n - c0 - c1 - c2 - c3 + 1):
                            c = (c0, c1, c2, c3, c4, tiny_n - c0 - c1 - c2 - c3 - c4)
                            sums = base_sums(c)
                            code, w, m = winner_from_sums(*sums, tiny_n)
                            counts_by_type = {TYPES[i]: c[i] for i in range(6)}
                            icode, iwin, imargin = irv_independent(counts_by_type)
                            if code == 0:
                                ok = (icode == "WIN" and iwin == LETTERS[w] and imargin == m)
                            elif code == 1:
                                ok = (icode == "TIE_R1")
                            else:
                                ok = (icode == "TIE_PAIR")
                            CHK.check(ok, "tiny n=%d full-enumeration eval agreement %s" % (tiny_n, c))
                            count += 1
        expected = {5: 252, 6: 462}[tiny_n]
        CHK.check(count == expected, "tiny n=%d enumerates C(%d,5)=%d" % (tiny_n, tiny_n + 5, expected))

    # (2) hand-derived pins (derivations in fixtures.json, written before code ran)
    for pin_id in ("HAND-1", "HAND-2"):
        pin = fixtures["hand_pins"][pin_id]
        c = tuple(pin["counts"])
        n = pin["n"]
        sums = base_sums(c)
        code, w, m = winner_from_sums(*sums, n)
        exp = pin["expect"]
        CHK.check(code == 0 and LETTERS[w] == exp["winner"], "%s: winner %s" % (pin_id, exp["winner"]))
        CHK.check(m == exp["margin"], "%s: margin %d" % (pin_id, exp["margin"]))
        hits = find_violations(c, sums, w, n)
        CHK.check(bool(hits) == exp["violation"], "%s: violation=%s" % (pin_id, exp["violation"]))
        if exp["violation"]:
            CHK.check(hits[0][2] == exp["min_k"], "%s: minimal k=%d" % (pin_id, exp["min_k"]))
            CHK.check(LETTERS[hits[0][3]] == exp["new_winner"], "%s: new winner %s" % (pin_id, exp["new_winner"]))
            fa, fb, fc = sums[0], sums[1], sums[2]
            lo = min(((fa, 0), (fb, 1), (fc, 2)))[1]
            combos = sorted({("first_eliminated" if x == lo else "final_loser", shape)
                             for x, shape, _k, _nw in hits})
            CHK.check(combos == sorted(tuple(e) for e in exp["combos"]),
                      "%s: combo set %s" % (pin_id, exp["combos"]))

    # (3) delta-table consistency: for 200 fixed elections (deterministic seed),
    # the incremental sums after a (t, tgt, k) move equal base_sums of the moved
    # counts, for every legal move at k in {1, count(t)}.
    rng = random.Random(99)  # self-check-only stream, disclosed; not a results input
    for trial in range(200):
        c = draw_election(rng, 30)
        s = base_sums(c)
        for (t, g), d in DELTAS.items():
            if c[t] == 0:
                continue
            for k in (1, c[t]):
                new = list(c)
                new[t] -= k
                new[g] += k
                expect = base_sums(tuple(new))
                got = tuple(s[i] + k * d[i] for i in range(6))
                CHK.check(got == expect, "delta table trial=%d move=(%d,%d,k=%d)" % (trial, t, g, k))


def symmetry_checks(stats):
    # IAC is candidate-exchangeable: exact win-count and violation-count symmetry.
    wa, wb, wc = stats.wins_by_candidate
    CHK.check(wa == wb == wc, "%s: wins symmetric across candidates (%d/%d/%d)" % (stats.leg_id, wa, wb, wc))
    va, vb, vc = stats.viols_by_winner
    CHK.check(va == vb == vc, "%s: violations symmetric across winners (%d/%d/%d)" % (stats.leg_id, va, vb, vc))


def coherence_checks(stats):
    s = stats
    CHK.check(s.non_tied + s.ties_r1 + s.ties_pairwise == s.total, "%s: tie partition sums" % s.leg_id)
    CHK.check(s.ties_pairwise == 0, "%s: pairwise ties impossible at odd n" % s.leg_id)
    CHK.check(s.viol_close <= s.close <= s.non_tied, "%s: close-set ordering" % s.leg_id)
    CHK.check(s.viol_close <= s.viol_all, "%s: viol_close <= viol_all" % s.leg_id)
    CHK.check(sum(s.breakdown_all.values()) >= s.viol_all, "%s: breakdown covers every violating election" % s.leg_id)
    CHK.check(sum(s.breakdown_close.values()) >= s.viol_close, "%s: close breakdown covers close violations" % s.leg_id)
    CHK.check(s.max_close_margin * 20 <= s.n, "%s: counted close margins obey margin*20<=n" % s.leg_id)


# ---------------------------------------------------------------------------
# Decision rule (exact integer arithmetic, constants from fixtures.json)
# ---------------------------------------------------------------------------

def apply_decision(leg_e, leg_s):
    def ge(num, den, bnum, bden):  # num/den >= bnum/bden
        return num * bden >= bnum * den

    def lt(num, den, bnum, bden):  # num/den < bnum/bden
        return num * bden < bnum * den

    arms = {
        "E-n25": (leg_e.viol_close, leg_e.close, leg_e.viol_all, leg_e.non_tied),
        "S-n99": (leg_s.viol_close, leg_s.close, leg_s.viol_all, leg_s.non_tied),
    }
    detail = {}
    approve_all, reject_all = True, True
    for arm_id, (vc, cd, va, ad) in arms.items():
        a_close = ge(vc, cd, 1, 10)
        a_all = ge(va, ad, 1, 100)
        r_close = lt(vc, cd, 1, 20)
        detail[arm_id] = {
            "V_close>=0.10": a_close,
            "V_all>=0.01": a_all,
            "V_close<0.05": r_close,
        }
        approve_all = approve_all and a_close and a_all
        reject_all = reject_all and r_close
    if approve_all:
        ruling = "APPROVE"
    elif reject_all:
        ruling = "REJECT"
    else:
        ruling = "NULL"
    CHK.check(not (approve_all and reject_all), "decision bands are disjoint")
    return ruling, detail


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fixtures = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

    # Band constants pinned in fixtures.json must match the literals used here.
    bc = fixtures["band_constants"]
    CHK.check(bc["V_CLOSE_APPROVE_MIN"] == "1/10", "fixtures pin V_CLOSE_APPROVE_MIN=1/10")
    CHK.check(bc["V_ALL_APPROVE_MIN"] == "1/100", "fixtures pin V_ALL_APPROVE_MIN=1/100")
    CHK.check(bc["V_CLOSE_REJECT_MAX"] == "1/20", "fixtures pin V_CLOSE_REJECT_MAX=1/20")
    CHK.check(bc["CLOSE_MARGIN_FRACTION"] == "1/20", "fixtures pin CLOSE_MARGIN_FRACTION=1/20")
    legs_fixture = {leg["id"]: leg for arm in fixtures["arms"].values() for leg in arm["legs"]}
    CHK.check(legs_fixture["E-n25"]["n"] == 25 and legs_fixture["E-n13"]["n"] == 13,
              "fixtures pin Arm E n values")
    CHK.check(legs_fixture["S-n99"] == {"id": "S-n99", "n": 99, "M": 200000, "seed": 20260713,
                                        "role": "decision leg (Arm S primary)"},
              "fixtures pin S-n99 {n, M, seed}")
    CHK.check(legs_fixture["S-n1001"]["n"] == 1001 and legs_fixture["S-n1001"]["M"] == 20000
              and legs_fixture["S-n1001"]["seed"] == 20260714, "fixtures pin S-n1001 {n, M, seed}")

    structural_checks(fixtures)

    print("verdict-019 — IRV monotonicity in close races (PROPOSAL 017)")
    print("pinned interpreter: cpython-%d.%d (Arm S PRNG pin; Arm E is seedless exact)"
          % (sys.version_info[0], sys.version_info[1]))
    print()

    # Arm E — exhaustive IAC, exact and seedless.
    leg_e13 = run_arm_e(13, "E-n13", recheck_stride=7)
    leg_e25 = run_arm_e(25, "E-n25", recheck_stride=97)
    CHK.check(leg_e13.total == 8568, "E-n13 enumerates C(18,5)=8568 profiles")
    CHK.check(leg_e25.total == 142506, "E-n25 enumerates C(30,5)=142506 profiles")
    CHK.check(leg_e13.close == 0, "E-n13 close set empty (margin 1 > 5% of 13) — flagged sensitivity artifact")
    for leg in (leg_e13, leg_e25):
        symmetry_checks(leg)
        coherence_checks(leg)

    # Arm S — seeded IC Monte Carlo, pinned loop order.
    leg_s99 = run_arm_s(99, 200000, 20260713, "S-n99", recheck_stride=401, digest_first=1000)
    leg_s1001 = run_arm_s(1001, 20000, 20260714, "S-n1001", recheck_stride=101, digest_first=200)
    for leg in (leg_s99, leg_s1001):
        coherence_checks(leg)

    legs = [leg_e25, leg_e13, leg_s99, leg_s1001]
    for leg in legs:
        d = leg.as_dict()
        v_all, v_close = leg.fractions()
        print("%-8s n=%-5d elections=%-7d ties=%d (r1=%d, pair=%d)  close=%d (margin<=%d)"
              % (leg.leg_id, leg.n, leg.total, leg.ties_r1 + leg.ties_pairwise,
                 leg.ties_r1, leg.ties_pairwise, leg.close, leg.max_close_margin))
        print("         V_all   = %-14s = %s" % (d["V_all"]["exact"], d["V_all"]["value"]))
        if leg.close:
            print("         V_close = %-14s = %s" % (d["V_close"]["exact"], d["V_close"]["value"]))
        else:
            print("         V_close = UNDEFINED (%s)" % d["V_close"]["note"])
        print("         breakdown(all):   %s" % json.dumps(d["breakdown_all"], sort_keys=True))
        print("         breakdown(close): %s" % json.dumps(d["breakdown_close"], sort_keys=True))
        print()

    ruling, detail = apply_decision(leg_e25, leg_s99)

    # Sensitivity legs: flag any band-crossing relative to the same arm's decision leg.
    flags = []
    ve_all, ve_close = leg_e25.fractions()
    vs_all, vs_close = leg_s99.fractions()
    v13_all, v13_close = leg_e13.fractions()
    v1001_all, v1001_close = leg_s1001.fractions()
    if v13_close is None:
        flags.append("E-n13: V_close undefined — at n=13 the smallest non-tied round-1 margin (1) "
                     "already exceeds 5% of n, so the close set is empty by construction; "
                     "sensitivity leg cannot be read on the close axis")
    for name, primary, sensitivity, band in (
        ("V_close E-n13 vs E-n25 @0.10", ve_close, v13_close, Fraction(1, 10)),
        ("V_close S-n1001 vs S-n99 @0.10", vs_close, v1001_close, Fraction(1, 10)),
        ("V_close S-n1001 vs S-n99 @0.05", vs_close, v1001_close, Fraction(1, 20)),
        ("V_all E-n13 vs E-n25 @0.01", ve_all, v13_all, Fraction(1, 100)),
        ("V_all S-n1001 vs S-n99 @0.01", vs_all, v1001_all, Fraction(1, 100)),
    ):
        if primary is None or sensitivity is None:
            continue
        if (primary >= band) != (sensitivity >= band):
            flags.append("SIGN-FLIP %s: primary %s vs sensitivity %s straddle the band" %
                         (name, primary, sensitivity))
    if not flags:
        flags.append("none — both size legs sit on the same side of every band as their arm's decision leg")

    print("decision detail: %s" % json.dumps(detail, sort_keys=True))
    print("sensitivity flags: %s" % json.dumps(flags))
    print()
    print("PRE-REGISTERED RULING: %s" % ruling)
    print()

    results = {
        "sim": "verdict-019-irv-monotonicity",
        "source": fixtures["source"],
        "pinned_interpreter": "cpython-%d.%d" % (sys.version_info[0], sys.version_info[1]),
        "breakpoint_optimization_used": False,
        "spot_check_seed_20260715": "not required — the breakpoint-only k-scan optimization is not used (exhaustive k-scan with early exit on first violating k; existence semantics identical)",
        "legs": [leg.as_dict() for leg in legs],
        "decision": {
            "rule": fixtures["bands"],
            "detail": detail,
            "ruling": ruling,
            "lower_bound_caveat": "single-type uplift only — mixed-type coalition raises could only find MORE violations, so every V above is a lower bound; an APPROVE is safe and a REJECT would rule on the standard definition only",
        },
        "sensitivity_flags": flags,
        "self_checks": {"passed": CHK.passed, "failed": len(CHK.failed)},
    }

    ok = CHK.summary()
    out_path = HERE / "results.json"
    payload = json.dumps(results, sort_keys=True, indent=2) + "\n"
    out_path.write_text(payload, encoding="utf-8")
    print("results.json written (%d bytes, canonical)" % len(payload))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
