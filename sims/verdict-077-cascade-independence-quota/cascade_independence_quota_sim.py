#!/usr/bin/env python3
"""VERDICT 077 runner — cascade independence quota (idea-engine PROPOSAL 064).

Three-arm, stdlib-only, hermetic (reads only its own fixtures.json):

  Arm A (DECISION, seedless)  — forward exact-Fraction absorbing-walk DP over
      states {lead -1, 0, 1, cascade-A, cascade-B} with the Binomial quota
      initial condition; ruin h() by direct substitution closed form;
      binomial pmf via math.comb.
  Arm B (twin, seedless)      — INDEPENDENTLY-WRITTEN backward memoized
      recursion W(agents-remaining, lead-or-cascade); ruin h() by Fraction
      Gaussian elimination; binomial pmf via Pascal-triangle recursion; must
      reproduce every Arm-A published number EXACTLY; powers the second
      decision evaluator (integer cross-multiplication band logic).
  Census (algorithm-free gate) — exhaustive enumeration of all 2^12 signal
      paths at N = 12, every grid p, every k <= 12; free-agent actions from
      the likelihood-ratio-derived action table over the literal observed
      history; equal to BOTH arms exactly.
  Arm R (seeded, REPORTING-ONLY) — literal 100-agent traces at the decision
      cell, k in {0, k*}; NO statistical gate rides it (convention C3/C4).

Every decision number is a seedless exact fractions.Fraction. Deterministic:
stdout + results.json byte-identical across process runs. Exit 0 iff every
self-check passes.
"""
import json
import random
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- utilities
def fr(s):
    """Parse an exact rational from 'a/b' or 'a'."""
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(s))


def canon(x):
    """Canonical exact rendering of a Fraction (convention C7)."""
    return "%d/%d" % (x.numerator, x.denominator)


CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)})
    return bool(ok)


# ---------------------------------------------------------------- Arm A
def h_arm_a(p):
    """Ruin h(l) = P(hit -2 before +2 | lead l), substitution closed form."""
    q = 1 - p
    h0 = q * q / (1 - 2 * p * q)
    return {-1: q + p * h0, 0: h0, 1: q * h0}


def lockin_arm_a(p):
    """Expected absorption time from lead 0: 2/(1-2pq)."""
    q = 1 - p
    return 2 / (1 - 2 * p * q)


def pmf_arm_a(k, p):
    q = 1 - p
    return [comb(k, i) * p**i * q ** (k - i) for i in range(k + 1)]


def quota_init_a(k, p, mirror=False):
    """State distribution after the k quota agents (Binomial initial
    condition). mirror=True runs the theta = B relabeling: a 'correct'
    signal is then a b-signal (lead step -1) and cascade-B is the CORRECT
    cascade; states keep raw #a-#b lead coordinates."""
    d = {-1: Fraction(0), 0: Fraction(0), 1: Fraction(0),
         "cA": Fraction(0), "cB": Fraction(0)}
    for i, w in enumerate(pmf_arm_a(k, p)):  # i = number of CORRECT signals
        L = 2 * i - k
        if mirror:
            L = -L
        if L >= 2:
            d["cA"] += w
        elif L <= -2:
            d["cB"] += w
        else:
            d[L] += w
    return d


def e_arm_a(k, p, h=None):
    h = h or h_arm_a(p)
    d = quota_init_a(k, p)
    return d["cB"] + sum(d[l] * h[l] for l in (-1, 0, 1))


def v_traj_arm_a(N, k, p, mirror=False):
    """Forward DP. Returns (V, accs, mass_ok, range_ok). accs[i-1] is agent
    i's accuracy; quota agents contribute exactly p each."""
    q = 1 - p
    up_pr, dn_pr = (q, p) if mirror else (p, q)  # prob of +1 / -1 lead step
    correct_casc = "cB" if mirror else "cA"
    d = quota_init_a(k, p, mirror=mirror)
    accs = [p] * k
    mass_ok = True
    range_ok = True
    for _ in range(k + 1, N + 1):
        if sum(d.values()) != 1:
            mass_ok = False
        acc = d[correct_casc] + (d[-1] + d[0] + d[1]) * p
        if not (0 <= acc <= 1):
            range_ok = False
        accs.append(acc)
        nd = {-1: Fraction(0), 0: Fraction(0), 1: Fraction(0),
              "cA": d["cA"], "cB": d["cB"]}
        for l in (-1, 0, 1):
            m = d[l]
            if m == 0:
                continue
            up, dn = l + 1, l - 1
            if up >= 2:
                nd["cA"] += m * up_pr
            else:
                nd[up] += m * up_pr
            if dn <= -2:
                nd["cB"] += m * dn_pr
            else:
                nd[dn] += m * dn_pr
        d = nd
    if sum(d.values()) != 1:
        mass_ok = False
    return sum(accs, Fraction(0)), accs, mass_ok, range_ok


# ---------------------------------------------------------------- Arm B
def gauss_solve(A, b):
    """Exact Gaussian elimination with partial (first-nonzero) pivoting."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [x - f * y for x, y in zip(M[r], M[col])]
    return [M[r][n] for r in range(n)]


def h_arm_b(p):
    """Ruin solve as a 3x3 linear system (states -1, 0, 1)."""
    q = 1 - p
    one, zero = Fraction(1), Fraction(0)
    A = [[one, -p, zero],      # h(-1) - p h(0)          = q
         [-q, one, -p],        # -q h(-1) + h(0) - p h(1) = 0
         [zero, -q, one]]      # -q h(0) + h(1)           = 0
    hm1, h0, h1 = gauss_solve(A, [q, zero, zero])
    return {-1: hm1, 0: h0, 1: h1}


def lockin_arm_b(p):
    """Expected absorption time system T(l) = 1 + p T(l+1) + q T(l-1)."""
    q = 1 - p
    one, zero = Fraction(1), Fraction(0)
    A = [[one, -p, zero],
         [-q, one, -p],
         [zero, -q, one]]
    sol = gauss_solve(A, [one, one, one])
    return sol[1]  # T(0)


def pascal_row(k):
    row = [1]
    for _ in range(k):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row


def pmf_arm_b(k, p):
    q = 1 - p
    row = pascal_row(k)
    return [row[i] * p**i * q ** (k - i) for i in range(k + 1)]


class ArmB:
    """Backward memoized recursion W(r, state) = expected correct actions
    among the r remaining free agents, conditioned theta = A."""

    def __init__(self, p):
        self.p = p
        self.q = 1 - p
        self.memo = {}

    def W(self, r, state):
        if r == 0:
            return Fraction(0)
        if state == "cA":
            return Fraction(r)
        if state == "cB":
            return Fraction(0)
        key = (r, state)
        got = self.memo.get(key)
        if got is not None:
            return got
        up = state + 1
        dn = state - 1
        s_up = "cA" if up >= 2 else up
        s_dn = "cB" if dn <= -2 else dn
        val = self.p * (1 + self.W(r - 1, s_up)) + self.q * self.W(r - 1, s_dn)
        self.memo[key] = val
        return val

    def init_dist(self, k):
        d = {-1: Fraction(0), 0: Fraction(0), 1: Fraction(0),
             "cA": Fraction(0), "cB": Fraction(0)}
        for i, w in enumerate(pmf_arm_b(k, self.p)):
            L = 2 * i - k
            if L >= 2:
                d["cA"] += w
            elif L <= -2:
                d["cB"] += w
            else:
                d[L] += w
        return d

    def V(self, N, k):
        d = self.init_dist(k)
        return k * self.p + sum(d[s] * self.W(N - k, s) for s in d)

    def e(self, k, h):
        d = self.init_dist(k)
        return d["cB"] + sum(d[l] * h[l] for l in (-1, 0, 1))

    def acc_traj(self, N, k):
        """acc_i = V(i,k) - V(i-1,k) for i > k; quota agents exactly p."""
        accs = [self.p] * k
        prev = k * self.p
        for i in range(k + 1, N + 1):
            cur = self.V(i, k)
            accs.append(cur - prev)
            prev = cur
        return accs


# ------------------------------------------------------- LR action table
def lr_action_table(p, max_lead):
    """Bayesian action table derived IN-SIM from the likelihood ratios
    (p/q)^(lead + s); strict preference acts on it, indifference follows own
    signal. Returns {(lead, s): action} for |lead| <= max_lead, s in {-1,+1}.
    Actions in {-1, +1} (b/a). Requires q > 0."""
    q = 1 - p
    table = {}
    for lead in range(-max_lead, max_lead + 1):
        for s in (-1, 1):
            lr = (p / q) ** (lead + s)
            if lr > 1:
                a = 1
            elif lr < 1:
                a = -1
            else:
                a = s
            table[(lead, s)] = a
    return table


# ---------------------------------------------------------------- census
def census(p, table):
    """All 2^12 signal paths at N = 12 (conditioned theta = A). Returns
    {k: (V, acc_traj)} for k = 0..12. Free-agent actions come from the
    LR-derived table over the literal revealed lead (quota actions reveal
    signals; pre-cascade free actions reveal signals; cascade actions are
    uninformative)."""
    N = 12
    q = 1 - p
    w_by_count = [p**c * q ** (N - c) for c in range(N + 1)]
    out = {}
    for k in range(N + 1):
        V = Fraction(0)
        acc = [Fraction(0)] * N
        for mask in range(1 << N):
            sigs = [1 if (mask >> i) & 1 else -1 for i in range(N)]
            c = bin(mask).count("1")
            w = w_by_count[c]
            lead = 0
            ncorr = 0
            corr_flags = []
            for i in range(1, N + 1):
                s = sigs[i - 1]
                if i <= k:
                    a = s
                    lead += s
                else:
                    a = table[(lead, s)]
                    informative = table[(lead, 1)] != table[(lead, -1)]
                    if informative:
                        lead += a  # a == s pre-cascade
                corr_flags.append(a == 1)
            for i, f in enumerate(corr_flags):
                if f:
                    acc[i] += w
            V += w * sum(corr_flags)
        out[k] = (V, acc)
    return out


# ---------------------------------------------------------------- Arm R
SEEDS_CONSTRUCTED = []


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


def frac_lt(u, num, den):
    """Fraction(u) < num/den, exact (convention C1)."""
    a, b = u.as_integer_ratio()
    return a * den < num * b


def arm_r_leg(seed, episodes, N, p, k_cells, table):
    """Literal-process traces; paired k-cells on the same draws (C2); the
    literal LR-rule process and the walk-shortcut process run on the SAME
    draws and must produce identical action sequences (C3)."""
    rng = make_rng(seed)
    pn, pd = p.numerator, p.denominator
    draws = 0
    stats = {k: {"correct": 0, "wrong_casc": 0, "right_casc": 0,
                 "unabsorbed": 0} for k in k_cells}
    c3_mismatch = 0
    for _ in range(episodes):
        u = rng.random()
        draws += 1
        theta = 1 if frac_lt(u, 1, 2) else -1
        sigs = []
        for _ in range(N):
            u = rng.random()
            draws += 1
            sigs.append(theta if frac_lt(u, pn, pd) else -theta)
        for k in k_cells:
            # literal LR-rule process
            lead = 0
            acts_lit = []
            for i in range(1, N + 1):
                s = sigs[i - 1]
                if i <= k:
                    a = s
                    lead += s
                else:
                    a = table[(lead, s)]
                    if table[(lead, 1)] != table[(lead, -1)]:
                        lead += a
                acts_lit.append(a)
            end_lead_lit = lead
            # walk-shortcut process (same draws)
            L = sum(sigs[:k])
            casc = 0
            if abs(L) >= 2:
                casc = 1 if L > 0 else -1
            lead_w = 0 if casc else L
            acts_walk = []
            for i in range(k, N):
                s = sigs[i]
                if casc:
                    acts_walk.append(casc)
                    continue
                acts_walk.append(s)
                lead_w += s
                if abs(lead_w) >= 2:
                    casc = 1 if lead_w > 0 else -1
            if acts_lit != list(sigs[:k]) + acts_walk:
                c3_mismatch += 1
            st = stats[k]
            st["correct"] += sum(1 for a in acts_lit if a == theta)
            if abs(end_lead_lit) >= 2:
                if (end_lead_lit > 0) == (theta > 0):
                    st["right_casc"] += 1
                else:
                    st["wrong_casc"] += 1
            else:
                st["unabsorbed"] += 1
    return draws, stats, c3_mismatch


# ---------------------------------------------------------------- evaluators
def evaluate_token_a(G, kstar, e_k, e_0, gates_ok):
    """Decision evaluator 1 (Arm-A numbers, Fraction comparisons), applied in
    the pre-registered order REJECT -> INVALID -> APPROVE -> NULL."""
    if G >= Fraction(6) and kstar >= 5 and 2 * e_k <= e_0:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if G <= Fraction(2) and kstar <= 2:
        return "APPROVE"
    return "NULL"


def evaluate_token_b(G, kstar, e_k, e_0, gates_ok):
    """Decision evaluator 2 (Arm-B numbers, integer cross-multiplication)."""
    r1 = G.numerator >= 6 * G.denominator
    r2 = kstar >= 5
    r3 = 2 * e_k.numerator * e_0.denominator <= e_0.numerator * e_k.denominator
    if r1 and r2 and r3:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    a1 = G.numerator <= 2 * G.denominator
    a2 = kstar <= 2
    if a1 and a2:
        return "APPROVE"
    return "NULL"


# ---------------------------------------------------------------- main
def main():
    out = {}
    check("runtime: CPython minor pinned 3.11",
          sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 11),
          "%s %d.%d" % (sys.implementation.name, *sys.version_info[:2]))

    grid = [fr(s) for s in FX["world"]["signal_correct_prob_grid"]]
    grid_s = FX["world"]["signal_correct_prob_grid"]
    p_dec = fr(FX["world"]["decision_p"])
    p_half = fr(FX["world"]["control_p"]["degeneracy"])
    p_one = fr(FX["world"]["control_p"]["perfect_anchor"])
    p_hand = fr(FX["anchors"]["hand_world"]["p"])
    Ns = FX["world"]["horizon_grid"]
    N_dec = FX["world"]["decision_N"]
    KMAX = 120

    # ---- F1: LR action table (grid p's + hand world; requires p > q) ----
    tables = {}
    for p, ps in list(zip(grid, grid_s)) + [(p_hand, "2/3")]:
        t = lr_action_table(p, 20)
        tables[ps] = t
        own = all(t[(l, s)] == s for l in (-1, 0, 1) for s in (-1, 1))
        casc = all(t[(l, s)] == (1 if l > 0 else -1)
                   for l in list(range(2, 21)) + list(range(-20, -1))
                   for s in (-1, 1))
        unbreak = all(t[(l, 1)] == t[(l, -1)] for l in
                      list(range(2, 21)) + list(range(-20, -1)))
        check("F1 action table @ p=%s (own-signal pre-cascade, herd at |lead|>=2, cascades never break)" % ps,
              own and casc and unbreak)

    # ---- Arm A / Arm B core objects ----
    h_a = {ps: h_arm_a(p) for p, ps in zip(grid, grid_s)}
    h_a["1/2"] = h_arm_a(p_half)
    h_a["2/3"] = h_arm_a(p_hand)
    h_a["1"] = h_arm_a(p_one)
    armb = {ps: ArmB(p) for p, ps in zip(grid, grid_s)}
    armb["1/2"] = ArmB(p_half)
    armb["2/3"] = ArmB(p_hand)
    armb["1"] = ArmB(p_one)

    for ps in ["11/20", "7/10", "4/5", "9/10", "1/2", "2/3", "1"]:
        hb = h_arm_b(armb[ps].p)
        check("F6 ruin solve twin-equal @ p=%s" % ps,
              all(h_a[ps][l] == hb[l] for l in (-1, 0, 1)))

    # ---- e(k) curves, both arms ----
    e_curves = {}
    for p, ps in zip(grid, grid_s):
        ea = [e_arm_a(k, p, h_a[ps]) for k in range(KMAX + 1)]
        eb = [armb[ps].e(k, h_arm_b(p)) for k in range(KMAX + 1)]
        check("F6 e-curve twin-equal @ p=%s (k 0..%d)" % (ps, KMAX), ea == eb)
        e_curves[ps] = ea

    # ---- V surfaces, both arms + mirror (theta = B symmetry gate) ----
    v_surface = {}
    traj_a = {}
    mass_all, range_all = True, True
    for p, ps in zip(grid, grid_s):
        v_surface[ps] = {}
        for N in Ns:
            kmax = min(N, KMAX)
            va = []
            for k in range(kmax + 1):
                V, accs, mok, rok = v_traj_arm_a(N, k, p)
                mass_all &= mok
                range_all &= rok
                va.append(V)
                if ps == FX["world"]["decision_p"] and N == N_dec:
                    traj_a[(ps, N, k)] = accs
            v_surface[ps][N] = va
            vb = [armb[ps].V(N, k) for k in range(kmax + 1)]
            check("F6 V-surface twin-equal @ (p=%s, N=%d)" % (ps, N), va == vb)
            vm = [v_traj_arm_a(N, k, p, mirror=True)[0] for k in range(kmax + 1)]
            check("F1 symmetry (theta=B mirror) V-surface equal @ (p=%s, N=%d)" % (ps, N), va == vm)
    check("F1 state-mass conservation at every DP step (sum = 1 exact)", mass_all)
    check("F1 every acc_i in [0, 1]", range_all)

    # mirror e-curves
    for p, ps in zip(grid, grid_s):
        # mirrored ruin g(l) = P(hit +2 before -2 | lead l) with up-step prob
        # q (theta = B: the CORRECT b-signal, prob p, steps the raw #a-#b
        # lead DOWN) — solved by its own substitution, not reflected from h:
        # g(1) = q + p*g(0); g(0) = q*g(1) + p*g(-1); g(-1) = q*g(0)
        q = 1 - p
        g0 = q * q / (1 - 2 * p * q)
        hm = {1: q + p * g0, 0: g0, -1: q * g0}

        def e_mirror(k):
            d = quota_init_a(k, p, mirror=True)
            return d["cA"] + sum(d[l] * hm[l] for l in (-1, 0, 1))

        check("F1 symmetry (theta=B mirror) e-curve equal @ p=%s" % ps,
              all(e_mirror(k) == e_curves[ps][k] for k in range(KMAX + 1)))

    # ---- V(N, N) = N*p gates ----
    for p, ps in zip(grid, grid_s):
        for N in (25, 100, 400):
            V_full = v_traj_arm_a(N, N, p)[0]
            check("F1 V(N,N) = N*p @ (p=%s, N=%d)" % (ps, N), V_full == N * p)

    # ---- F2a QUOTA-NULL ----
    for ps in grid_s:
        check("F2a QUOTA-NULL e identical k in {0,1,2} @ p=%s" % ps,
              e_curves[ps][0] == e_curves[ps][1] == e_curves[ps][2])
        for N in Ns:
            va = v_surface[ps][N]
            check("F2a QUOTA-NULL V identical k in {0,1,2} @ (p=%s, N=%d)" % (ps, N),
                  va[0] == va[1] == va[2])

    # ---- F2b PARITY (+ finite-horizon strictness, convention C8) ----
    for ps in grid_s:
        ok = all(e_curves[ps][2 * m + 1] == e_curves[ps][2 * m + 2]
                 for m in range(1, (KMAX - 2) // 2 + 1))
        check("F2b PARITY e(2m+1) = e(2m+2) for every m >= 1 @ p=%s" % ps, ok)
        for N in Ns:
            kmax = min(N, KMAX)
            strict = all(v_surface[ps][N][2 * m + 2] < v_surface[ps][N][2 * m + 1]
                         for m in range(1, (kmax - 2) // 2 + 1))
            check("F2b parity strictness V(N,2m+2) < V(N,2m+1), m >= 1 @ (p=%s, N=%d)" % (ps, N), strict)

    # ---- F2c harmonic identities + KNIFE-EDGE (convention C9) ----
    knife_dec = {}
    for p, ps in zip(grid, grid_s):
        q = 1 - p
        h = h_a[ps]
        check("F2c harmonic identities @ p=%s" % ps,
              h[0] == q * h[-1] + p * h[1] and h[1] == q * h[0] and h[-1] == q + p * h[0])
        ok = True
        for m in range(1, (KMAX - 1) // 2 + 1):
            pm = pmf_arm_a(2 * m, p)
            p_lo = pm[m - 1]  # L = -2
            p_hi = pm[m + 1]  # L = +2
            rhs = p_lo * (1 - q - p * h[-1]) - p_hi * q * h[1]
            lhs = e_curves[ps][2 * m] - e_curves[ps][2 * m + 1]
            if lhs != rhs:
                ok = False
            if ps == FX["world"]["decision_p"] and m <= 8:
                knife_dec[m] = lhs
        check("F2c KNIFE-EDGE decomposition exact for every m >= 1 @ p=%s" % ps, ok)
    ref = FX["anchors"]["knife_edge_reference"]
    check("F2c knife-edge reference e(2)-e(3) = 441/14500 @ (7/10, m=1)",
          knife_dec[1] == fr(ref["value"]))

    # ---- F3 closed-form anchors ----
    for ps in grid_s:
        p = fr(ps)
        q = 1 - p
        check("F3 e(0) = q^2/(1-2pq) = %s @ p=%s" % (FX["anchors"]["e0_by_grid_p"][ps], ps),
              e_curves[ps][0] == fr(FX["anchors"]["e0_by_grid_p"][ps])
              and e_curves[ps][0] == q * q / (1 - 2 * p * q))
    hh = FX["anchors"]["h_at_7_10"]
    check("F3 h at 7/10 = (237/580, 9/58, 27/580)",
          h_a["7/10"][-1] == fr(hh["h_minus1"]) and h_a["7/10"][0] == fr(hh["h_0"])
          and h_a["7/10"][1] == fr(hh["h_plus1"]))
    lock_a = {ps: lockin_arm_a(fr(ps)) for ps in grid_s}
    check("F3 lock-in 2/(1-2pq) = 100/29 @ 7/10",
          lock_a["7/10"] == fr(FX["anchors"]["lockin_at_7_10"]))
    for ps in grid_s:
        check("F6 lock-in twin-equal @ p=%s" % ps, lock_a[ps] == lockin_arm_b(fr(ps)))
    # p = 1 anchor: e = 0 and V = N exactly, every k
    e1 = [e_arm_a(k, p_one) for k in range(KMAX + 1)]
    check("F3 p=1 anchor e(k) = 0 for every k", all(x == 0 for x in e1))
    for N in Ns:
        kmax = min(N, KMAX)
        ok = all(v_traj_arm_a(N, k, p_one)[0] == N for k in range(kmax + 1))
        okb = all(armb["1"].V(N, k) == N for k in range(kmax + 1))
        check("F3 p=1 anchor V(N,k) = N for every k @ N=%d (both arms)" % N, ok and okb)

    # ---- F4 hand world ----
    hw = FX["anchors"]["hand_world"]
    hb23 = h_arm_b(p_hand)
    check("F4 hand world h = (7/15, 1/5, 1/15) (both arms)",
          h_a["2/3"][-1] == fr(hw["h"][0]) and h_a["2/3"][0] == fr(hw["h"][1])
          and h_a["2/3"][1] == fr(hw["h"][2]) and all(h_a["2/3"][l] == hb23[l] for l in (-1, 0, 1)))
    check("F4 hand world e(3) = 23/135 (both arms)",
          e_arm_a(3, p_hand) == fr(hw["e_3"]) and armb["2/3"].e(3, hb23) == fr(hw["e_3"]))
    check("F4 hand world V(6,3) = 350/81 (both arms)",
          v_traj_arm_a(6, 3, p_hand)[0] == fr(hw["V_6_3"]) and armb["2/3"].V(6, 3) == fr(hw["V_6_3"]))

    # ---- F5 degeneracy p = 1/2 ----
    e_half = [e_arm_a(k, p_half) for k in range(KMAX + 1)]
    check("F5 degeneracy e(k) = 1/2 for EVERY k", all(x == Fraction(1, 2) for x in e_half))
    for N in Ns:
        kmax = min(N, KMAX)
        ok = all(v_traj_arm_a(N, k, p_half)[0] == Fraction(N, 2) for k in range(kmax + 1))
        okb = all(armb["1/2"].V(N, k) == Fraction(N, 2) for k in range(kmax + 1))
        check("F5 degeneracy V(N,k) = N/2 for every k @ N=%d (both arms)" % N, ok and okb)

    # ---- census (N = 12, all 2^12 paths, every grid p, every k <= 12) ----
    for p, ps in zip(grid, grid_s):
        cen = census(p, tables[ps])
        ok_v, ok_acc = True, True
        for k in range(13):
            Vc, acc_c = cen[k]
            Va, accs_a, _, _ = v_traj_arm_a(12, k, p)
            if Vc != Va or Vc != armb[ps].V(12, k):
                ok_v = False
            if acc_c != accs_a or acc_c != armb[ps].acc_traj(12, k):
                ok_acc = False
        check("F6 census 2^12 V(12,k) equals BOTH arms, every k <= 12 @ p=%s" % ps, ok_v)
        check("F6 census 2^12 acc trajectory equals BOTH arms, every k <= 12 @ p=%s" % ps, ok_acc)

    # ---- k*, gain, runner-up tables ----
    kstar_tab, gain_tab, runner_tab, tie_counts = {}, {}, {}, {}
    for ps in grid_s:
        kstar_tab[ps], gain_tab[ps], runner_tab[ps], tie_counts[ps] = {}, {}, {}, {}
        for N in Ns:
            va = v_surface[ps][N]
            best = max(va)
            ks = min(k for k, v in enumerate(va) if v == best)
            tie_counts[ps][N] = sum(1 for v in va if v == best)
            second = max(v for k, v in enumerate(va) if k != ks)
            ru = min(k for k, v in enumerate(va) if k != ks and v == second)
            kstar_tab[ps][N] = ks
            gain_tab[ps][N] = best - va[0]
            runner_tab[ps][N] = {"k": ru, "margin": best - second}
    check("F6 k* interior (k* <= %d) at every cell" % FX["world"]["kstar_interiority_bound"],
          all(kstar_tab[ps][N] <= FX["world"]["kstar_interiority_bound"]
              for ps in grid_s for N in Ns))
    check("F6 k* twin-equal (Arm B recomputes argmax from its own V pass)",
          all(kstar_tab[ps][N] == min(
              k for k, v in enumerate([armb[ps].V(N, kk) for kk in range(min(N, KMAX) + 1)])
              if v == max(armb[ps].V(N, kk) for kk in range(min(N, KMAX) + 1)))
              for ps in grid_s for N in Ns))

    # ---- decision-cell numbers ----
    dps = FX["world"]["decision_p"]
    kstar = kstar_tab[dps][N_dec]
    V0 = v_surface[dps][N_dec][0]
    Vk = v_surface[dps][N_dec][kstar]
    G = gain_tab[dps][N_dec]
    e0 = e_curves[dps][0]
    ek = e_curves[dps][kstar]
    G_b = armb[dps].V(N_dec, kstar) - armb[dps].V(N_dec, 0)
    ek_b = armb[dps].e(kstar, h_arm_b(p_dec))
    e0_b = armb[dps].e(0, h_arm_b(p_dec))
    check("F6 decision numbers twin-equal (G, e(0), e(k*))",
          G == G_b and e0 == e0_b and ek == ek_b)

    # ---- bounded-learning exhibit + IR wedge (reporting) ----
    def maj(N, p):
        q = 1 - p
        tot = Fraction(0)
        for c in range(N + 1):
            w = comb(N, c) * p**c * q ** (N - c)
            if 2 * c > N:
                tot += w
            elif 2 * c == N:
                tot += w / 2
        return tot

    majority = {ps: {N: maj(N, fr(ps)) for N in Ns} for ps in grid_s}
    baseline = {ps: 1 - e_curves[ps][0] for ps in grid_s}
    acc0 = traj_a[(dps, N_dec, 0)]
    acck = traj_a[(dps, N_dec, kstar)]
    check("F6 decision-cell acc trajectories twin-equal (k in {0, k*})",
          acc0 == armb[dps].acc_traj(N_dec, 0) and acck == armb[dps].acc_traj(N_dec, kstar))
    sacrifice = sum((acc0[i] - p_dec for i in range(kstar)), Fraction(0))
    recovery = sum((acck[i] - acc0[i] for i in range(kstar, N_dec)), Fraction(0))
    check("C10 IR-wedge identity G = recovery - sacrifice (exact)", G == recovery - sacrifice)

    # ---- gates-so-far verdict input ----
    gates_ok_pre = all(c["ok"] for c in CHECKS)

    token_a = evaluate_token_a(G, kstar, ek, e0, gates_ok_pre)
    token_b = evaluate_token_b(G_b, kstar, ek_b, e0_b, gates_ok_pre)
    check("F6 twin decision evaluators agree on the token", token_a == token_b,
          "%s / %s" % (token_a, token_b))

    # ---- Arm R (seeded, REPORTING-ONLY) ----
    ar = FX["arm_R_params"]
    seeds = FX["seeds"]
    table_dec = tables[dps]
    draws_m, stats_m, c3_m = arm_r_leg(seeds["main"], ar["episodes_main"],
                                       N_dec, p_dec, [0, kstar], table_dec)
    draws_s, stats_s, c3_s = arm_r_leg(seeds["stability"], ar["episodes_stability"],
                                       N_dec, p_dec, [0, kstar], table_dec)
    check("F6 Arm-R draw sentinel main = %d" % ar["expected_draws_main"],
          draws_m == ar["expected_draws_main"], draws_m)
    check("F6 Arm-R draw sentinel stability = %d" % ar["expected_draws_stability"],
          draws_s == ar["expected_draws_stability"], draws_s)
    check("C3 literal LR-process == walk-shortcut process on every episode (both legs)",
          c3_m == 0 and c3_s == 0, "mismatches %d/%d" % (c3_m, c3_s))
    rng_pres = make_rng(seeds["presentation"])
    check("F6 aux seed %d NEVER read (constructor registry C12)" % seeds["aux_never_read"],
          sorted(SEEDS_CONSTRUCTED) == sorted([seeds["main"], seeds["stability"], seeds["presentation"]])
          and seeds["aux_never_read"] not in SEEDS_CONSTRUCTED,
          str(sorted(SEEDS_CONSTRUCTED)))

    def r_summary(stats, episodes):
        s = {}
        for k, st in stats.items():
            s[str(k)] = {
                "mean_correct_per_agent": st["correct"] / (episodes * N_dec),
                "wrong_cascade_freq_at_N": st["wrong_casc"] / episodes,
                "right_cascade_freq_at_N": st["right_casc"] / episodes,
                "unabsorbed_freq_at_N": st["unabsorbed"] / episodes,
            }
        return s

    armr = {"main": r_summary(stats_m, ar["episodes_main"]),
            "stability": r_summary(stats_s, ar["episodes_stability"])}

    # ---- drafter comparison (NEVER gated) ----
    d = FX["drafter_disclosed_never_gated"]
    comp = []

    def cmpf(name, computed, disclosed, tol):
        comp.append({"name": name, "computed": computed, "disclosed": disclosed,
                     "match": abs(computed - disclosed) <= tol})

    cmpf("V(100,0)", float(V0), d["V_100_0"], 1e-5)
    comp.append({"name": "k*(100,7/10)", "computed": kstar,
                 "disclosed": d["kstar_100_7_10"], "match": kstar == d["kstar_100_7_10"]})
    comp.append({"name": "runner-up k", "computed": runner_tab[dps][N_dec]["k"],
                 "disclosed": d["runner_up"]["k"],
                 "match": runner_tab[dps][N_dec]["k"] == d["runner_up"]["k"]})
    cmpf("runner-up margin", float(runner_tab[dps][N_dec]["margin"]), d["runner_up"]["margin"], 1e-5)
    cmpf("V(100,k*)", float(Vk), d["V_100_15"], 1e-5)
    cmpf("G(100,7/10)", float(G), d["G_100_7_10"], 1e-5)
    comp.append({"name": "e(0) exact", "computed": canon(e0), "disclosed": d["e_0_7_10"],
                 "match": e0 == fr(d["e_0_7_10"])})
    comp.append({"name": "e(k*) exact", "computed": canon(ek), "disclosed": d["e_15_7_10"],
                 "match": ek == fr(d["e_15_7_10"])})
    kt_ok = all(kstar_tab[ps][N] == d["kstar_table_all_odd"][ps][j]
                for ps in grid_s for j, N in enumerate(Ns))
    comp.append({"name": "k* table (12 cells)", "computed": str({ps: [kstar_tab[ps][N] for N in Ns] for ps in grid_s}),
                 "disclosed": str(d["kstar_table_all_odd"]), "match": kt_ok})
    gt_ok = all(abs(float(gain_tab[ps][N]) - d["gain_table"][ps][j]) <= 1e-3
                for ps in grid_s for j, N in enumerate(Ns))
    comp.append({"name": "gain table (12 cells)", "computed": str({ps: [round(float(gain_tab[ps][N]), 4) for N in Ns] for ps in grid_s}),
                 "disclosed": str(d["gain_table"]), "match": gt_ok})
    cmpf("majority(100,7/10)", float(majority["7/10"][100]),
         d["bounded_learning"]["majority_100_7_10_approx"], 1e-6)
    comp.append({"name": "baseline 1-e(0) @7/10", "computed": canon(baseline["7/10"]),
                 "disclosed": d["bounded_learning"]["baseline_crowd_accuracy_7_10"],
                 "match": baseline["7/10"] == fr(d["bounded_learning"]["baseline_crowd_accuracy_7_10"])})
    cmpf("IR sacrifice", float(sacrifice), d["ir_wedge"]["sacrifice_approx"], 0.05)
    cmpf("IR recovery", float(recovery), d["ir_wedge"]["recovery_approx"], 0.05)
    cmpf("expected wrong agents k=0", float(N_dec - V0), d["expected_wrong_agents_100"]["k0"], 0.01)
    cmpf("expected wrong agents k=k*", float(N_dec - Vk), d["expected_wrong_agents_100"]["kstar"], 0.01)
    cmpf("V(100,16)", float(v_surface[dps][N_dec][16]), d["V_100_16_approx"], 1e-3)
    all_odd = all(kstar_tab[ps][N] % 2 == 1 for ps in grid_s for N in Ns)
    comp.append({"name": "k* ODD at every cell", "computed": all_odd, "disclosed": True,
                 "match": all_odd})

    # ---- results.json ----
    out["fixtures"] = "fixtures.json (verbatim registration; sha over content not embedded — file is committed)"
    out["h"] = {ps: {str(l): canon(h_a[ps][l]) for l in (-1, 0, 1)}
                for ps in grid_s + ["1/2", "2/3", "1"]}
    out["lockin"] = {ps: {"exact": canon(lock_a[ps]), "float": float(lock_a[ps])} for ps in grid_s}
    out["e_curves"] = {ps: {"exact": [canon(x) for x in e_curves[ps]],
                            "float": [float(x) for x in e_curves[ps]]} for ps in grid_s}
    out["V_surface"] = {ps: {str(N): {"exact": [canon(x) for x in v_surface[ps][N]],
                                      "float": [float(x) for x in v_surface[ps][N]]}
                             for N in Ns} for ps in grid_s}
    out["kstar_table"] = {ps: {str(N): kstar_tab[ps][N] for N in Ns} for ps in grid_s}
    out["kstar_tie_counts"] = {ps: {str(N): tie_counts[ps][N] for N in Ns} for ps in grid_s}
    out["gain_table"] = {ps: {str(N): {"exact": canon(gain_tab[ps][N]),
                                       "float": float(gain_tab[ps][N])} for N in Ns} for ps in grid_s}
    out["runner_up"] = {ps: {str(N): {"k": runner_tab[ps][N]["k"],
                                      "margin_exact": canon(runner_tab[ps][N]["margin"]),
                                      "margin_float": float(runner_tab[ps][N]["margin"])}
                             for N in Ns} for ps in grid_s}
    out["knife_edge_decomposition_decision_p"] = {str(m): {"exact": canon(v), "float": float(v)}
                                                  for m, v in sorted(knife_dec.items())}
    out["bounded_learning"] = {
        "baseline_crowd_accuracy": {ps: {"exact": canon(baseline[ps]), "float": float(baseline[ps])}
                                    for ps in grid_s},
        "note": "1 - e(0) is N-INDEPENDENT by construction (no N in its formula); the majority benchmark is reporting-only (C6)",
        "majority_benchmark": {ps: {str(N): {"exact": canon(majority[ps][N]),
                                             "float": float(majority[ps][N])} for N in Ns}
                               for ps in grid_s},
    }
    out["ir_wedge"] = {"sacrifice": {"exact": canon(sacrifice), "float": float(sacrifice)},
                       "recovery": {"exact": canon(recovery), "float": float(recovery)},
                       "late_agent_acc_100_k0": {"exact": canon(acc0[-1]), "float": float(acc0[-1])},
                       "solo": {"exact": canon(p_dec), "float": float(p_dec)}}
    out["expected_wrong_agents_decision_cell"] = {"k0": float(N_dec - V0), "kstar": float(N_dec - Vk)}
    out["acc_trajectories_decision_cell"] = {
        "k0": {"exact": [canon(x) for x in acc0], "float": [float(x) for x in acc0]},
        "kstar": {"exact": [canon(x) for x in acck], "float": [float(x) for x in acck]}}
    out["decision"] = {
        "cell": {"p": dps, "N": N_dec},
        "V0": {"exact": canon(V0), "float": float(V0)},
        "kstar": kstar,
        "Vkstar": {"exact": canon(Vk), "float": float(Vk)},
        "G": {"exact": canon(G), "float": float(G)},
        "e0": {"exact": canon(e0), "float": float(e0)},
        "e_kstar": {"exact": canon(ek), "float": float(ek)},
        "clauses": {
            "REJECT_G_ge_6": bool(G >= 6),
            "REJECT_kstar_ge_5": bool(kstar >= 5),
            "REJECT_e_halving": bool(2 * ek <= e0),
            "APPROVE_G_le_2": bool(G <= 2),
            "APPROVE_kstar_le_2": bool(kstar <= 2),
        },
        "token_evaluator_A": token_a,
        "token_evaluator_B": token_b,
    }
    out["arm_R"] = {"params": ar, "seeds_constructed": sorted(SEEDS_CONSTRUCTED),
                    "aux_seed_never_read": seeds["aux_never_read"],
                    "legs": armr,
                    "exact_reference": {"V0_per_agent": float(V0 / N_dec),
                                        "Vkstar_per_agent": float(Vk / N_dec),
                                        "e0": float(e0), "e_kstar": float(ek)},
                    "note": "REPORTING-ONLY (no statistical gate, C4): wrong-cascade freq is at horizon N=100 vs the exact infinite-horizon e; unconditional over theta vs the theta=A-conditioned exact values (equal by the F1 symmetry gate)"}
    out["drafter_comparison_never_gated"] = comp
    out["checks"] = CHECKS
    out["all_checks_pass"] = all(c["ok"] for c in CHECKS)

    # ---- stdout ----
    print("VERDICT 077 — cascade independence quota (idea-engine PROPOSAL 064)")
    print("runtime: %s %d.%d.%d, stdlib-only, hermetic" % (
        sys.implementation.name, *sys.version_info[:3]))
    print()
    print("== decision cell (p=%s, N=%d) ==" % (dps, N_dec))
    print("V(100,0)   = %s = %r" % (canon(V0), float(V0)))
    print("k*         = %d (ties %d; runner-up k=%d by %r)" % (
        kstar, tie_counts[dps][N_dec], runner_tab[dps][N_dec]["k"],
        float(runner_tab[dps][N_dec]["margin"])))
    print("V(100,k*)  = %s = %r" % (canon(Vk), float(Vk)))
    print("G          = %s = %r  (REJECT needs >= 6, APPROVE needs <= 2)" % (canon(G), float(G)))
    print("e(0)       = %s = %r" % (canon(e0), float(e0)))
    print("e(k*)      = %s = %r  (halving line e(0)/2 = %r)" % (canon(ek), float(ek), float(e0 / 2)))
    print("expected wrong agents per 100: %r -> %r" % (float(N_dec - V0), float(N_dec - Vk)))
    print()
    print("== 12-cell k*/gain table (order presentation-shuffled, seed %d) ==" % seeds["presentation"])
    lines = []
    for ps in grid_s:
        for N in Ns:
            lines.append("p=%-5s N=%-3d  k*=%-3d gain=%-10r runner-up=(k=%d, %r)" % (
                ps, N, kstar_tab[ps][N], round(float(gain_tab[ps][N]), 6),
                runner_tab[ps][N]["k"], round(float(runner_tab[ps][N]["margin"]), 6)))
    rng_pres.shuffle(lines)
    for ln in lines:
        print(ln)
    print()
    print("== structure theorems ==")
    print("QUOTA-NULL: k in {0,1,2} identical e and V at every grid cell — gated F2a")
    print("PARITY: e(2m+1) = e(2m+2) for every m >= 1 at every grid p, and")
    print("        V(N,2m+2) < V(N,2m+1) strictly at every grid cell — gated F2b")
    print("KNIFE-EDGE: e(2m)-e(2m+1) = P(L=-2)(1-q-p*h(-1)) - P(L=+2)*q*h(1),")
    print("        exact for every m >= 1 at every grid p; reference e(2)-e(3) @7/10 = %s — gated F2c" % canon(knife_dec[1]))
    print("k* is ODD at every one of the 12 cells: %s (reporting; consequence of PARITY+strictness)" % all_odd)
    print()
    print("== bounded-learning exhibit (reporting) ==")
    for ps in grid_s:
        print("p=%-5s crowd cap 1-e(0) = %s = %r (N-independent); majority-of-N: %s; lock-in E = %r actions" % (
            ps, canon(baseline[ps]), float(baseline[ps]),
            ", ".join("N=%d: %r" % (N, round(float(majority[ps][N]), 7)) for N in Ns),
            float(lock_a[ps])))
    print("IR wedge @ decision cell: late free-rider acc_100(k=0) = %r > solo p = %r;" % (
        float(acc0[-1]), float(p_dec)))
    print("  quota sacrifice = %r, recovery = %r, G = recovery - sacrifice (exact, C10)" % (
        float(sacrifice), float(recovery)))
    print()
    print("== Arm R (seeded, REPORTING-ONLY; no statistical gate) ==")
    for leg, eps in (("main", ar["episodes_main"]), ("stability", ar["episodes_stability"])):
        for kk in ("0", str(kstar)):
            st = armr[leg][kk]
            print("%s leg (n=%d) k=%s: mean correct/agent %r (exact %r); wrong-casc@N %r (exact e = %r); unabsorbed %r" % (
                leg, eps, kk, round(st["mean_correct_per_agent"], 6),
                round(float((V0 if kk == "0" else Vk) / N_dec), 6),
                round(st["wrong_cascade_freq_at_N"], 6),
                round(float(e0 if kk == "0" else ek), 6),
                round(st["unabsorbed_freq_at_N"], 6)))
    print()
    print("== drafter comparison (NEVER gated) ==")
    n_match = sum(1 for c in comp if c["match"])
    print("%d/%d disclosed values reproduced; mismatches:" % (n_match, len(comp)),
          [c["name"] for c in comp if not c["match"]] or "none")
    print()
    n_fail = sum(1 for c in CHECKS if not c["ok"])
    print("== self-checks: %d total, %d failed ==" % (len(CHECKS), n_fail))
    for c in CHECKS:
        if not c["ok"]:
            print("FAIL: %s  [%s]" % (c["name"], c["detail"]))
    print()
    print("== RULING (pre-registered order REJECT -> INVALID -> APPROVE -> NULL) ==")
    print("evaluator A: %s   evaluator B: %s" % (token_a, token_b))

    (HERE / "results.json").write_text(
        json.dumps(out, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return 0 if all(c["ok"] for c in CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
