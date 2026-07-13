#!/usr/bin/env python3
"""VERDICT 056 — mineverse snapshot stale-indicator threshold (idea-engine PROPOSAL 045).

Hermetic, stdlib-only, deterministic. Reads ONLY fixtures.json (committed before
this runner — git-trail discipline). Arm A = the DECISION arm: seedless exact
Fraction renewal-reward enumeration (geometric mixture of n-fold convolutions of
the interval lattice, closed-form geometric tail — no truncation error). Arm S =
seeded timeline MC confirmation (seeds 20261317 main / 20261318 stability /
20261319 reporting; 20261320 aux reserved, NEVER constructed — asserted).
Decision rule pre-registered, evaluated IN ORDER, REJECT FIRST. Byte-identical
stdout + results.json across process runs (no wall-clock in any output).
"""

import json
import os
import random
import sys
from bisect import bisect_right
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}
ANOMALIES = []


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)


def anomaly(line):
    ANOMALIES.append(line)


# pinned interpreter (fixture python_minor)
_want = tuple(int(p) for p in FX["python_minor"].split("."))
check(sys.version_info[:2] == _want, "CPython minor pinned %s, running %d.%d" % (FX["python_minor"], sys.version_info[0], sys.version_info[1]))

T_GRID = list(FX["T_grid"])
FS_BAND = Fraction(*[int(p) for p in FX["bands"]["falsestale_max"].split("/")])
LAT_BAND = int(FX["bands"]["lat_max_s"])
L_REPORT = int(FX["bands"]["reporting_L_threshold_s"])

CONSTRUCTED_SEEDS = []


class CountingRandom(random.Random):
    """random.Random with a randrange call counter (draw sentinels)."""

    def __init__(self, seed):
        CONSTRUCTED_SEEDS.append(seed)
        super().__init__(seed)
        self.draws = 0

    def randrange(self, *args, **kwargs):
        self.draws += 1
        return super().randrange(*args, **kwargs)


# ------------------------------------------------------------------- Arm A
class ArmA(object):
    """Exact renewal-reward enumeration for one world (seedless).

    Gap G = sum of N i.i.d. uniform-integer intervals, N geometric
    (P(N=n) = f^(n-1)(1-f)). Exact pmf convolutions for n <= m with the
    n > m tail in closed form; m = smallest integer with m*lo > x_max so
    every tail term has S_n > every evaluated x (no truncation error).
    """

    def __init__(self, lo, hi, f_num, f_den, c_lo, c_hi, t_grid, cutoff=None):
        self.lo, self.hi = lo, hi
        self.c_lo, self.c_hi = c_lo, c_hi
        self.f = Fraction(f_num, f_den)
        self.t_grid = list(t_grid)
        self.x_max = max(t_grid) - c_lo  # largest x = T - c (c_lo most negative)
        m = 1
        while m * lo <= self.x_max:
            m += 1
        if cutoff is not None:
            assert cutoff >= m, "forced cutoff below closure"
            m = cutoff
        self.m = m
        span = hi - lo + 1
        base = {v: Fraction(1, span) for v in range(lo, hi + 1)}
        self.mean_i = sum(v * p for v, p in base.items())
        # n-fold convolutions, n = 1..m
        pmfs = [base]
        for _ in range(m - 1):
            prev = pmfs[-1]
            nxt = {}
            for g1, p1 in prev.items():
                for g2, p2 in base.items():
                    nxt[g1 + g2] = nxt.get(g1 + g2, Fraction(0)) + p1 * p2
            pmfs.append(nxt)
        for n, pmf in enumerate(pmfs, start=1):
            check(sum(pmf.values()) == 1, "conv n=%d pmf sums to 1 (world lo=%d hi=%d)" % (n, lo, hi))
            check(min(pmf) == n * lo and max(pmf) == n * hi, "conv n=%d support bounds" % n)
        one = Fraction(1)
        f = self.f
        p_n = [(f ** (n - 1)) * (one - f) for n in range(1, m + 1)]
        # truncated combined gap pmf (n <= m)
        trunc = {}
        for n, pmf in enumerate(pmfs, start=1):
            w = p_n[n - 1]
            if w == 0:
                continue
            for g, p in pmf.items():
                trunc[g] = trunc.get(g, Fraction(0)) + w * p
        self.trunc = trunc
        # geometric tail (n >= m+1), closed form
        k = m + 1
        self.tail_prob = f ** m  # P(N > m)
        if f == 0:
            self.tail_en = Fraction(0)
        else:
            # sum_{n>=k} n f^(n-1) (1-f) = (k f^(k-1) (1-f) + f^k) / (1-f)
            self.tail_en = (k * (f ** (k - 1)) * (one - f) + f ** k) / (one - f)
        e_n = Fraction(1) / (one - f)
        check(sum(p_n) + self.tail_prob == 1, "P(N) total mass exact")
        check(sum(n * p for n, p in zip(range(1, m + 1), p_n)) + self.tail_en == e_n, "E[N] identity exact")
        self.e_g = self.mean_i * e_n
        check(sum(g * p for g, p in trunc.items()) + self.mean_i * self.tail_en == self.e_g, "E[G] identity exact")
        # suffix arrays over sorted truncated support
        support = sorted(trunc)
        self.support = support
        sp, sm = [], []
        ap, am = Fraction(0), Fraction(0)
        for g in reversed(support):
            ap += trunc[g]
            am += trunc[g] * g
            sp.append(ap)
            sm.append(am)
        self.suf_prob = list(reversed(sp))  # suf_prob[i] = P_trunc(G >= support[i])
        self.suf_mass = list(reversed(sm))

    def _suffix(self, x):
        """(P_trunc(G > x), E_trunc[G; G > x]) via the suffix arrays."""
        i = bisect_right(self.support, x)
        if i >= len(self.support):
            return Fraction(0), Fraction(0)
        return self.suf_prob[i], self.suf_mass[i]

    def excess(self, x):
        """E[(G - x)+], exact (closed tail)."""
        p, m_ = self._suffix(x)
        return (m_ - x * p) + (self.mean_i * self.tail_en - x * self.tail_prob)

    def gap_gt(self, a):
        """P(G > a), exact for a <= x_max."""
        assert a <= self.x_max
        p, _ = self._suffix(a)
        return p + self.tail_prob

    def falsestale_c(self, t, c):
        return self.excess(t - c) / self.e_g

    def falsestale(self, t):
        span = self.c_hi - self.c_lo + 1
        acc = Fraction(0)
        for c in range(self.c_lo, self.c_hi + 1):
            acc += self.excess(t - c)
        return acc / span / self.e_g

    def _age_tables(self):
        if hasattr(self, "_cdf"):
            return
        a_max = self.x_max  # LAT needs cdf up to x_max - 1; build to x_max
        cdf = []
        acc = Fraction(0)
        for a in range(0, a_max + 1):
            acc += self.gap_gt(a) / self.e_g  # P(A = a) = P(G > a)/E[G]
            cdf.append(acc)
        self._cdf = cdf
        h = [Fraction(0)]  # H[x] = sum_{k=1..x} cdf[k-1] = E[(x - A)+]
        hacc = Fraction(0)
        for x in range(1, a_max + 1):
            hacc += cdf[x - 1]
            h.append(hacc)
        self._h = h
        check(all(cdf[i] <= cdf[i + 1] for i in range(len(cdf) - 1)), "age cdf non-decreasing")
        check(cdf[-1] <= 1, "age cdf bounded by 1")

    def age_pmf(self, a):
        return self.gap_gt(a) / self.e_g

    def lat_c(self, t, c):
        """E[max(0, T - A - c)] at fixed c (floor-age pmf, registered)."""
        self._age_tables()
        x = t - c
        if x <= 0:
            return Fraction(0)
        return self._h[x]

    def lat(self, t):
        span = self.c_hi - self.c_lo + 1
        acc = Fraction(0)
        for c in range(self.c_lo, self.c_hi + 1):
            acc += self.lat_c(t, c)
        return acc / span

    def p_l_gt(self, t, thr):
        """P(L > thr) = P(A < T - c - thr), exact."""
        self._age_tables()
        span = self.c_hi - self.c_lo + 1
        acc = Fraction(0)
        for c in range(self.c_lo, self.c_hi + 1):
            y = t - c - thr  # need A < y
            if y >= 1:
                acc += self._cdf[y - 1]
        return acc / span


# ------------------------------------------------------------------- Arm S
def build_timeline(rng, lo, hi, fail_kind, warmup, horizon):
    """Success timeline: founding success at t=0 (no draws), then per attempt:
    interval draw THEN fail-bit draw, until t >= warmup + horizon."""
    end = warmup + horizon
    span = hi - lo + 1
    successes = [0]
    attempts = 0
    state_fail = False  # burst chain: initial state ok at the founding success
    t = 0
    while t < end:
        i = lo + rng.randrange(span)
        t += i
        if fail_kind[0] == "iid":
            f_num, f_den = fail_kind[1], fail_kind[2]
            fail = rng.randrange(f_den) < f_num
        else:  # burst two-state Markov
            if state_fail:
                fail = rng.randrange(2) < 1
            else:
                fail = rng.randrange(48) < 1
            state_fail = fail
        attempts += 1
        if not fail:
            successes.append(t)
    return successes, attempts


def sample_leg(rng, successes, warmup, horizon, n_viewer, n_halt, c_lo, c_hi, t_grid):
    """Viewer samples then halt samples, CRN across the whole T grid.
    STALE iff floor_age + c >= T (== the registered strict rule under
    real-instant sampling; see fixtures indicator_equivalence_note); the
    integer-strict variant (>) rides alongside, reporting-only."""
    c_span = c_hi - c_lo + 1
    stale_ge = {t: 0 for t in t_grid}
    stale_gt = {t: 0 for t in t_grid}
    for _ in range(n_viewer):
        t = rng.randrange(warmup, warmup + horizon)
        c = c_lo + rng.randrange(c_span)
        age = t - successes[bisect_right(successes, t) - 1]
        perceived = age + c
        for tt in t_grid:
            if perceived >= tt:
                stale_ge[tt] += 1
            if perceived > tt:
                stale_gt[tt] += 1
    lat_sum = {t: 0 for t in t_grid}
    l_gt = {t: 0 for t in t_grid}
    for _ in range(n_halt):
        t = rng.randrange(warmup, warmup + horizon)
        c = c_lo + rng.randrange(c_span)
        age = t - successes[bisect_right(successes, t) - 1]
        for tt in t_grid:
            l = tt - age - c
            if l > 0:
                lat_sum[tt] += l
                if l > L_REPORT:
                    l_gt[tt] += 1
    fs = {t: Fraction(stale_ge[t], n_viewer) for t in t_grid}
    fs_strict = {t: Fraction(stale_gt[t], n_viewer) for t in t_grid}
    lat = {t: Fraction(lat_sum[t], n_halt) for t in t_grid}
    plgt = {t: Fraction(l_gt[t], n_halt) for t in t_grid}
    return fs, fs_strict, lat, plgt


def run_arm_s(seed_key, world, scenario_list=None):
    cfg = FX["arm_s"][seed_key]
    rng = CountingRandom(cfg["seed"])
    warmup, horizon = cfg["warmup_s"], cfg["horizon_s"]
    nv, nh = cfg["viewer_samples"], cfg["halt_samples"]
    out = {}
    worlds = scenario_list if scenario_list is not None else [("primary", world)]
    for name, w in worlds:
        d0 = rng.draws
        successes, attempts = build_timeline(rng, w["lo"], w["hi"], w["fail"], warmup, horizon)
        check(successes[0] == 0, "%s/%s founding success at t=0" % (seed_key, name))
        check(all(successes[i] < successes[i + 1] for i in range(len(successes) - 1)), "%s/%s successes strictly increasing" % (seed_key, name))
        fs, fs_strict, lat, plgt = sample_leg(rng, successes, warmup, horizon, nv, nh, w["c_lo"], w["c_hi"], T_GRID)
        drawn = rng.draws - d0
        check(drawn == 2 * attempts + 2 * nv + 2 * nh, "%s/%s draw sentinel 2*%d+2*%d+2*%d == %d" % (seed_key, name, attempts, nv, nh, drawn))
        for t in T_GRID:
            check(fs_strict[t] <= fs[t], "%s/%s strict variant <= ge variant at T=%d" % (seed_key, name, t))
        ts = sorted(T_GRID)
        check(all(fs[ts[i]] >= fs[ts[i + 1]] for i in range(len(ts) - 1)), "%s/%s Arm-S FALSESTALE monotone (CRN)" % (seed_key, name))
        check(all(lat[ts[i]] <= lat[ts[i + 1]] for i in range(len(ts) - 1)), "%s/%s Arm-S LAT monotone (CRN)" % (seed_key, name))
        out[name] = {"fs": fs, "fs_strict": fs_strict, "lat": lat, "plgt": plgt, "attempts": attempts, "draws": drawn, "successes": len(successes)}
    return out


# --------------------------------------------------------- twin evaluators
def evaluator_fraction(fs, lat):
    """Evaluator 1: Fraction comparisons. Returns (feas, tstar, shape, axis)."""
    feas = [t for t in T_GRID if fs[t] <= FS_BAND and lat[t] <= Fraction(LAT_BAND)]
    tstar = min(feas) if feas else None
    if not feas:
        return feas, tstar, "REJECT", None
    if 180 in feas and not any(t in feas for t in (90, 120)):
        return feas, tstar, "APPROVE-SHAPE", None
    if 180 not in feas:
        return feas, tstar, "NULL", "(i) under-provisioned"
    return feas, tstar, "NULL", "(ii) over-provisioned"


def evaluator_integer(fs, lat):
    """Evaluator 2: independently written, pure-integer cross-multiplication."""
    feas = []
    band_n, band_d = FS_BAND.numerator, FS_BAND.denominator
    for t in reversed(sorted(T_GRID)):  # different iteration order on purpose
        a, b = fs[t].numerator, fs[t].denominator
        c, d = lat[t].numerator, lat[t].denominator
        ok_fs = a * band_d <= band_n * b
        ok_lat = c <= LAT_BAND * d
        if ok_fs and ok_lat:
            feas.append(t)
    feas = sorted(feas)
    tstar = feas[0] if feas else None
    if len(feas) == 0:
        return feas, tstar, "REJECT", None
    has180 = any(t == 180 for t in feas)
    cheap = [t for t in feas if t * 1 <= 120]
    if has180 and len(cheap) == 0:
        return feas, tstar, "APPROVE-SHAPE", None
    if not has180:
        return feas, tstar, "NULL", "(i) under-provisioned"
    return feas, tstar, "NULL", "(ii) over-provisioned"


def frs(x):
    """Fraction -> 'num/den (float)' string, deterministic."""
    return "%d/%d (~%.9g)" % (x.numerator, x.denominator, float(x))


# ================================================================== gates
print("=" * 78)
print("VERDICT 056 - mineverse snapshot stale-indicator threshold (PROPOSAL 045)")
print("=" * 78)

# --- hand fixture (six scenarios, verbatim expectations) ---
gap_excess = lambda g, c, t: max(0, g - (t - c))
latency = lambda a, c, t: max(0, t - a - c)
indicator_stale = lambda a, c, t: (a + c) > t  # strict, pinned
check(gap_excess(60, 0, 180) == 0, "hand fixture 1: G=60,c=0,T=180 -> (G-x)+=0")
check(gap_excess(200, 10, 180) == 30, "hand fixture 2: G=200,c=+10,T=180 -> x=170,(G-x)+=30")
check(latency(40, -30, 90) == 80, "hand fixture 3: A=40,c=-30,T=90 -> L=80")
check(latency(100, 30, 120) == 0, "hand fixture 4: A=100,c=+30,T=120 -> L=0")
check(indicator_stale(155, 30, 180) is True, "hand fixture 5: perceived 185 > 180 -> STALE")
check(indicator_stale(155, 20, 180) is False, "hand fixture 6: perceived 175 <= 180 -> LIVE (strict)")
print("hand fixture: 6/6 scenarios exact")

# --- zero-disturbance identity leg (Arm A, exact values not tolerances) ---
zd = FX["zero_disturbance_identity"]
arm_zd = ArmA(zd["interval_lo"], zd["interval_hi"], zd["fail_num"], zd["fail_den"], zd["c_lo"], zd["c_hi"], T_GRID)
for t in T_GRID:
    check(arm_zd.falsestale(t) == 0, "zero-disturbance FALSESTALE(%d) == 0 exactly" % t)
    check(arm_zd.lat(t) == Fraction(t) - Fraction(59, 2), "zero-disturbance LAT(%d) == %d - 59/2 exactly" % (t, t))
for a in range(60):
    check(arm_zd.age_pmf(a) == Fraction(1, 60), "zero-disturbance age pmf uniform at a=%d" % a)
check(arm_zd.age_pmf(60) == 0, "zero-disturbance age pmf 0 at a=60")
print("zero-disturbance identity leg: exact (FALSESTALE == 0, LAT(T) == T - 59/2, age uniform {0..59})")

# --- primary world, Arm A (THE DECISION ARM) ---
P = FX["primary"]
arm_primary = ArmA(P["interval_lo"], P["interval_hi"], P["fail_num"], P["fail_den"], P["c_lo"], P["c_hi"], T_GRID)
check(arm_primary.m == FX["arm_a"]["tail_cutoff_n_primary"], "primary tail cutoff m == 8 (registered; 8*55=440 > 390)")
check(arm_primary.e_g == Fraction(1625, 24), "primary E[G] == 1625/24 exactly")

fs_a = {t: arm_primary.falsestale(t) for t in T_GRID}
lat_a = {t: arm_primary.lat(t) for t in T_GRID}
plgt_a = {t: arm_primary.p_l_gt(t, L_REPORT) for t in T_GRID}

# monotonicity (exact, hard gate)
check(all(fs_a[T_GRID[i]] >= fs_a[T_GRID[i + 1]] for i in range(len(T_GRID) - 1)), "Arm A FALSESTALE non-increasing in T (exact)")
check(all(lat_a[T_GRID[i]] <= lat_a[T_GRID[i + 1]] for i in range(len(T_GRID) - 1)), "Arm A LAT non-decreasing in T (exact)")
for t in T_GRID:
    if t - P["c_lo"] <= L_REPORT:  # L <= T - c_lo, so zero is guaranteed only for T + |c_lo| <= 300
        check(plgt_a[t] == 0, "Arm A P(L>300) == 0 exactly at T=%d (T - c_lo <= 300)" % t)

# FALSESTALE/age-table cross identity: P(A >= x) = E[(G - x)+]/E[G], exact
arm_primary._age_tables()
for t in T_GRID:
    for c in (-30, 0, 30):
        x = t - c
        check(arm_primary.excess(x) / arm_primary.e_g == 1 - arm_primary._cdf[x - 1], "renewal-reward == age-table complement at T=%d c=%+d" % (t, c))

# per-c recombination twin check (aggregate == mean of per-c splits)
span_c = P["c_hi"] - P["c_lo"] + 1
for t in T_GRID:
    acc_fs = sum(arm_primary.falsestale_c(t, c) for c in range(P["c_lo"], P["c_hi"] + 1)) / span_c
    acc_lat = sum(arm_primary.lat_c(t, c) for c in range(P["c_lo"], P["c_hi"] + 1)) / span_c
    check(acc_fs == fs_a[t], "per-c FALSESTALE recombines exactly at T=%d" % t)
    check(acc_lat == lat_a[t], "per-c LAT recombines exactly at T=%d" % t)

# LAT twin computation: prefix-table H vs direct pmf sum, exact
for t in T_GRID:
    for c in (-30, 0, 30):
        x = t - c
        direct = sum(arm_primary.age_pmf(a) * (x - a) for a in range(0, x))
        check(direct == arm_primary.lat_c(t, c), "LAT direct pmf sum == prefix table at T=%d c=%+d" % (t, c))

# excess twin computation: suffix arrays vs direct truncated sum, exact
for t in T_GRID:
    for c in (-30, 0, 30):
        x = t - c
        direct = sum(p * (g - x) for g, p in arm_primary.trunc.items() if g > x)
        direct += arm_primary.mean_i * arm_primary.tail_en - x * arm_primary.tail_prob
        check(direct == arm_primary.excess(x), "excess suffix == direct at T=%d c=%+d" % (t, c))

# --- tail-closure spot-check: n <= 8 + analytic tail vs direct n <= 12, exact equality ---
arm_12 = ArmA(P["interval_lo"], P["interval_hi"], P["fail_num"], P["fail_den"], P["c_lo"], P["c_hi"], T_GRID, cutoff=12)
for t in (90, 240):
    for c in (-30, 0, 30):
        x = t - c
        check(arm_primary.excess(x) == arm_12.excess(x), "tail closure exact at T=%d c=%+d (m=8 vs m=12)" % (t, c))
    check(arm_primary.falsestale(t) == arm_12.falsestale(t), "tail closure FALSESTALE(%d) exact (m=8 vs m=12)" % t)
print("tail-closure spot-check: n<=8 + analytic tail == direct n<=12, EXACT on T in {90,240} x c in {-30,0,+30}")

# --- Arm S: main confirmation leg (seed 20261317) ---
world_primary = {"lo": P["interval_lo"], "hi": P["interval_hi"], "fail": ("iid", P["fail_num"], P["fail_den"]), "c_lo": P["c_lo"], "c_hi": P["c_hi"]}
s_main = run_arm_s("main", world_primary)["primary"]

# agreement gate (hard; breach => NULL axis iii)
AGREE_FS = Fraction(1, 1000)
AGREE_LAT = Fraction(5)
agreement_breaches = []
for t in T_GRID:
    d_fs = abs(s_main["fs"][t] - fs_a[t])
    d_lat = abs(s_main["lat"][t] - lat_a[t])
    if d_fs > AGREE_FS:
        agreement_breaches.append("FALSESTALE T=%d |diff|=%s > 1/1000" % (t, frs(d_fs)))
    if d_lat > AGREE_LAT:
        agreement_breaches.append("LAT T=%d |diff|=%s > 5 s" % (t, frs(d_lat)))
    check(d_fs <= AGREE_FS, "agreement gate FALSESTALE T=%d (|diff| %s <= 1/1000)" % (t, frs(d_fs)))
    check(d_lat <= AGREE_LAT, "agreement gate LAT T=%d (|diff| %s <= 5 s)" % (t, frs(d_lat)))
    if t - P["c_lo"] <= L_REPORT:
        check(s_main["plgt"][t] == 0, "Arm S main P(L>300) == 0 at T=%d (T - c_lo <= 300)" % t)
agreement_ok = not agreement_breaches

# --- Arm S: stability leg (seed 20261318, fresh timeline) ---
s_stab = run_arm_s("stability", world_primary)["primary"]

# --- Arm S: reporting leg (seed 20261319): sensitivity + burst confirmations ---
SENS = FX["sensitivity_worlds"]
def sens_world(name):
    w = dict(world_primary)
    spec = SENS[name]
    if spec["vary"] == "interval":
        w["lo"], w["hi"] = spec["interval_lo"], spec["interval_hi"]
    elif spec["vary"] == "fail":
        w["fail"] = ("iid", spec["fail_num"], spec["fail_den"])
    elif spec["vary"] == "offset":
        w["c_lo"], w["c_hi"] = spec["c_lo"], spec["c_hi"]
    return w

scenario_order = FX["arm_s"]["reporting"]["scenario_order"]
scenarios = []
for name in scenario_order:
    if name == "burst":
        w = dict(world_primary)
        w["fail"] = ("burst",)
        scenarios.append((name, w))
    else:
        scenarios.append((name, sens_world(name)))
s_rep = run_arm_s("reporting", None, scenario_list=scenarios)

# --- sensitivity worlds, Arm A exact (reporting-only; straddle detection) ---
sens_a = {}
for name in scenario_order:
    if name == "burst":
        continue  # Arm S only, disclosed (no geometric closed form)
    w = sens_world(name)
    f_num, f_den = w["fail"][1], w["fail"][2]
    arm = ArmA(w["lo"], w["hi"], f_num, f_den, w["c_lo"], w["c_hi"], T_GRID)
    sens_a[name] = {
        "fs": {t: arm.falsestale(t) for t in T_GRID},
        "lat": {t: arm.lat(t) for t in T_GRID},
        "tail_cutoff_m": arm.m,
    }
    check(all(sens_a[name]["fs"][T_GRID[i]] >= sens_a[name]["fs"][T_GRID[i + 1]] for i in range(len(T_GRID) - 1)), "sens %s Arm A FALSESTALE monotone" % name)
    check(all(sens_a[name]["lat"][T_GRID[i]] <= sens_a[name]["lat"][T_GRID[i + 1]] for i in range(len(T_GRID) - 1)), "sens %s Arm A LAT monotone" % name)

# aux seed never constructed
check(FX["arm_s"]["aux"]["seed"] not in CONSTRUCTED_SEEDS, "aux seed 20261320 NEVER constructed")
check(sorted(set(CONSTRUCTED_SEEDS)) == [20261317, 20261318, 20261319], "constructed seeds exactly {20261317, 20261318, 20261319}")

# ============================================================ decision
feas1, tstar1, shape1, axis1 = evaluator_fraction(fs_a, lat_a)
feas2, tstar2, shape2, axis2 = evaluator_integer(fs_a, lat_a)
check(feas1 == feas2 and tstar1 == tstar2 and shape1 == shape2 and axis1 == axis2, "twin evaluators agree on Arm A (decision input)")

sfeas1, ststar1, sshape1, saxis1 = evaluator_fraction(s_stab["fs"], s_stab["lat"])
sfeas2, ststar2, sshape2, saxis2 = evaluator_integer(s_stab["fs"], s_stab["lat"])
check(sfeas1 == sfeas2 and ststar1 == ststar2 and sshape1 == sshape2 and saxis1 == saxis2, "twin evaluators agree on stability input")
stability_reproduces = (sshape1 == shape1)
check(stability_reproduces, "stability leg reproduces the Arm-A ruling shape (%s vs %s)" % (sshape1, shape1))

# straddle detection: primary-conjunct outcomes per sensitivity world vs primary
prim_conj = {
    "feas_empty": len(feas1) == 0,
    "in180": 180 in feas1,
    "cheap_empty": not any(t in feas1 for t in (90, 120)),
}
straddles = []
for name, tab in sorted(sens_a.items()):
    wfeas = [t for t in T_GRID if tab["fs"][t] <= FS_BAND and tab["lat"][t] <= Fraction(LAT_BAND)]
    conj = {
        "feas_empty": len(wfeas) == 0,
        "in180": 180 in wfeas,
        "cheap_empty": not any(t in wfeas for t in (90, 120)),
    }
    flips = [k for k in prim_conj if conj[k] != prim_conj[k]]
    if flips:
        straddles.append({"world": name, "flipped_conjuncts": flips, "feas": wfeas})

# burst direction (reporting, never invalidating): registration states bursts raise FALSESTALE at every T
burst_dir_violations = []
for t in T_GRID:
    if s_rep["burst"]["fs"][t] < fs_a[t]:
        burst_dir_violations.append(t)
if burst_dir_violations:
    anomaly("ANOMALY (reporting-only): burst-leg Arm-S FALSESTALE below primary Arm-A at T in %s (20k-sample noise possible; direction claim is the registration's)" % burst_dir_violations)

# final class, evaluated IN ORDER (REJECT FIRST)
if not agreement_ok:
    verdict_class, verdict_axis = "NULL", "(iii) arm disagreement — the agreement gate failed; no ruling issues"
elif shape1 == "REJECT":
    verdict_class, verdict_axis = "REJECT", None
elif shape1 == "APPROVE-SHAPE":
    if stability_reproduces:
        verdict_class, verdict_axis = "APPROVE", None
    else:
        verdict_class, verdict_axis = "NULL", "stability non-reproduction (arm-family, axis iii)"
else:
    verdict_class, verdict_axis = "NULL", axis1

# ============================================================ output
print()
print("PRIMARY WORLD - Arm A (DECISION ARM, exact Fractions) vs Arm S main (seed 20261317)")
print("%-5s %-34s %-30s %-34s %-26s" % ("T", "FALSESTALE ArmA", "FALSESTALE ArmS", "LAT ArmA (s)", "LAT ArmS (s)"))
for t in T_GRID:
    print("%-5d %-34s %-30s %-34s %-26s" % (t, frs(fs_a[t]), frs(s_main["fs"][t]), frs(lat_a[t]), frs(s_main["lat"][t])))
print()
print("bands: FALSESTALE <= 1/200 = 0.005 AND LAT <= 240 s")
print("Feas = %s   T* = %s" % (feas1, tstar1))
print("P(L>300) ArmA: %s" % {t: frs(plgt_a[t]) for t in T_GRID})
print()
print("stability leg (seed 20261318, 20k/20k): Feas_S = %s, shape %s -> reproduces: %s" % (sfeas1, sshape1, stability_reproduces))
print("agreement gate (main leg, hard): %s" % ("PASS on all 14 cells" if agreement_ok else "BREACH: " + "; ".join(agreement_breaches)))
print()
print("SENSITIVITY (Arm A exact, REPORTING-ONLY - cannot flip the decision)")
for name in sorted(sens_a):
    tab = sens_a[name]
    wfeas = [t for t in T_GRID if tab["fs"][t] <= FS_BAND and tab["lat"][t] <= Fraction(LAT_BAND)]
    print("  %-13s Feas = %-22s FS(120)=%s FS(150)=%s FS(180)=%s" % (name, wfeas, frs(tab["fs"][120]), frs(tab["fs"][150]), frs(tab["fs"][180])))
print("  burst (Arm S only, seed 20261319, 20k): FS(120)=%s FS(180)=%s LAT(180)=%s" % (frs(s_rep["burst"]["fs"][120]), frs(s_rep["burst"]["fs"][180]), frs(s_rep["burst"]["lat"][180])))
if straddles:
    for s in straddles:
        print("  STRADDLE (named axis, reporting-only): world %s flips %s (Feas -> %s)" % (s["world"], s["flipped_conjuncts"], s["feas"]))
for a in ANOMALIES:
    print(a)
print()
print("DECISION WALKTHROUGH (pre-registered order):")
print("  1. REJECT iff Feas = {} : Feas = %s -> %s" % (feas1, "FIRES" if verdict_class == "REJECT" else "does NOT fire"))
print("  2. APPROVE iff 180 in Feas AND Feas /\\ {90,120} = {} AND stability reproduces:")
print("     180 in Feas = %s; Feas /\\ {90,120} empty = %s; stability reproduces = %s -> %s" % (prim_conj["in180"], prim_conj["cheap_empty"], stability_reproduces, "FIRES" if verdict_class == "APPROVE" else "does not fire"))
print("  3. NULL otherwise -> %s" % (verdict_axis if verdict_class == "NULL" else "not reached"))
print()
print("VERDICT 056 CLASS: %s%s" % (verdict_class, (" - " + verdict_axis) if verdict_axis else ""))

# ------------------------------------------------------------ results.json
def table(d):
    return {str(t): {"exact": "%d/%d" % (d[t].numerator, d[t].denominator), "float": float(d[t])} for t in T_GRID}

results = {
    "verdict": "VERDICT 056",
    "proposal_header_verbatim": FX["proposal"]["header_verbatim"],
    "class": verdict_class,
    "null_axis": verdict_axis,
    "feasible_set_arm_a": feas1,
    "t_star": tstar1,
    "arm_a_primary": {
        "E_G": "1625/24",
        "tail_cutoff_m": arm_primary.m,
        "FALSESTALE": table(fs_a),
        "LAT": table(lat_a),
        "P_L_gt_300": table(plgt_a),
    },
    "arm_s_main": {
        "seed": 20261317,
        "attempts": s_main["attempts"],
        "successes": s_main["successes"],
        "draws": s_main["draws"],
        "FALSESTALE": table(s_main["fs"]),
        "FALSESTALE_integer_strict_variant": table(s_main["fs_strict"]),
        "LAT": table(s_main["lat"]),
        "P_L_gt_300": table(s_main["plgt"]),
        "agreement_gate": "PASS" if agreement_ok else agreement_breaches,
        "abs_diff_FALSESTALE": {str(t): float(abs(s_main["fs"][t] - fs_a[t])) for t in T_GRID},
        "abs_diff_LAT_s": {str(t): float(abs(s_main["lat"][t] - lat_a[t])) for t in T_GRID},
    },
    "arm_s_stability": {
        "seed": 20261318,
        "attempts": s_stab["attempts"],
        "draws": s_stab["draws"],
        "FALSESTALE": table(s_stab["fs"]),
        "LAT": table(s_stab["lat"]),
        "feas_from_stability": sfeas1,
        "shape": sshape1,
        "reproduces_arm_a_ruling": stability_reproduces,
    },
    "sensitivity_arm_a": {
        name: {
            "tail_cutoff_m": sens_a[name]["tail_cutoff_m"],
            "FALSESTALE": table(sens_a[name]["fs"]),
            "LAT": table(sens_a[name]["lat"]),
            "feas": [t for t in T_GRID if sens_a[name]["fs"][t] <= FS_BAND and sens_a[name]["lat"][t] <= Fraction(LAT_BAND)],
        }
        for name in sorted(sens_a)
    },
    "sensitivity_arm_s_confirmations": {
        name: {"FALSESTALE": table(s_rep[name]["fs"]), "LAT": table(s_rep[name]["lat"]), "attempts": s_rep[name]["attempts"], "draws": s_rep[name]["draws"]}
        for name in scenario_order
    },
    "straddles": straddles,
    "burst_direction_violations_reporting_only": burst_dir_violations,
    "per_c_split_T180": {
        str(c): {"FALSESTALE": "%d/%d" % (arm_primary.falsestale_c(180, c).numerator, arm_primary.falsestale_c(180, c).denominator), "LAT": float(arm_primary.lat_c(180, c))}
        for c in range(P["c_lo"], P["c_hi"] + 1)
    },
    "per_c_split_grid_c_in_-30_0_30": {
        "%+d" % c: {str(t): {"FALSESTALE": float(arm_primary.falsestale_c(t, c)), "LAT": float(arm_primary.lat_c(t, c))} for t in T_GRID}
        for c in (-30, 0, 30)
    },
    "constructed_seeds": sorted(set(CONSTRUCTED_SEEDS)),
    "anomalies": ANOMALIES,
    "self_checks": dict(CHECKS),
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=False)
    fh.write("\n")

print()
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
sys.exit(0 if CHECKS["failed"] == 0 else 1)
