"""VERDICT 106 - Retry-amplified metastable overload collapse (idea-engine PROPOSAL 093)

Pinned world
------------
A lane pool of c=100 lanes. Effective in-flight load x evolves as attempts =
base arrivals lambda + retries of failed attempts. Failure probability is a
logistic in utilization u = x/c:

    p(x) = p0 + (1-p0) * sigma(k*(u - theta)),  sigma(z)=1/(1+e^-z),  u = x/c

Mean-field steady state balances inflow against in-flight load:

    x = lambda + r * p(x) * x     <=>     F(x) = lambda + r*p(x)*x - x = 0

Fixed points are the roots of F. For r > r_c there are THREE roots (COLD~61 and
HOT~400 stable, an unstable middle); for r < r_c only COLD survives. r_c is the
saddle-node / fold value. A COLD-branch continuation quantity is handy:

    G(x) = x * (1 - r*p(x))       ( F(x)=0  <=>  G(x)=lambda )

The two folds of G (local max, local min in x) give the adiabatic sweep limits:
lambda_up  = G(x at local max) = highest lambda the COLD branch survives to,
lambda_down = G(x at local min) = lowest lambda the HOT branch survives to.

Pinned globals: c=100, p0=0.02, k=12.0, theta=1.05, r=0.85, lambda=60,
retry-budget cap b=0.20, SEED_BASE=20260721, SIG=3.0.
Collapsed mean-field fixed point x* = lambda/(1-r) = 60/0.15 = 400 (u=4.0).

Pre-registered rule (fires IN ORDER, never softened)
----------------------------------------------------
R1 bistability : at the pinned world F(x) has two stable roots COLD~61 and
                 HOT~400 split by one unstable middle root (a); AND a seeded
                 stochastic run started COLD stays healthy while started HOT
                 stays collapsed, separated by >= SIG sigma (b).
R2 hysteresis  : adiabatic lambda sweep gives lambda_up (COLD fold) and
                 lambda_down (HOT fold); width = lambda_up - lambda_down ~ 56,
                 AND the pinned lambda=60 shows coexistence (both stable).
R3 retry-lever : sweep r. Fold width is monotone non-decreasing in r; the
                 operating point lambda=60 becomes bistable above a critical
                 r_c ~ 0.566 (where lambda_down(r) crosses lambda=60); below
                 r_c the operating point is monostable (op-margin 0), above it
                 the op-margin is positive and monotone.
R4 knockout    : re-run R1 with a retry BUDGET cap b=0.20 applied
                 (x = lambda + min(r*p(x)*x, b*lambda) - x). Under the cap the
                 HOT root is eliminated: only COLD remains (monostable).
VERDICT = APPROVE iff R1 & R2 & R3 & R4, else REJECT with first-failing gate.

Twin independent evaluators (bisection vs secant root-finders; fold-via-G-extrema
vs fold-via-root-count; if-chain vs table decision) cross-check each other.
Deterministic; double run is byte-identical; stdlib only.
"""

import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- pinned world
C = 100.0            # lanes
P0 = 0.02            # baseline failure floor
K = 12.0             # sigmoid steepness
THETA = 1.05         # utilization threshold (slightly above capacity)
R_PIN = 0.85         # retry aggressiveness (pinned operating point)
LAM = 60.0           # base arrival rate (disclosed correction 70 -> 60)
B_CAP = 0.20         # retry-budget cap (R4 knockout)
SEED_BASE = 20260721 # this proposal's OWN pinned seed constant
SIG = 3.0            # sigma significance for stochastic separation

# stochastic-run globals (R1b)
N_REP = 24           # seeded replicates per start branch
T_STEPS = 400        # iterations per replicate
T_WINDOW = 120       # last-window steps averaged per replicate
NOISE = 0.5          # multiplicative (Poisson-style) noise scale

# pre-registered tolerances (fixed before results were read)
COLD_LO, COLD_HI = 55.0, 70.0     # admissible COLD root band (u ~ 0.55..0.70)
HOT_LO, HOT_HI = 380.0, 420.0     # admissible HOT root band (u ~ 3.8..4.2)
WIDTH_TARGET = 56.0               # proposal's claimed hysteresis width
WIDTH_TOL = 2.0                   # |width - 56| tolerance for an independent solve
RC_TARGET = 0.566                 # proposal's claimed critical r_c
RC_TOL = 0.02                     # |r_c - 0.566| tolerance
STAR_TOL = 0.5                    # |HOT - lambda/(1-r)| tolerance
STAB_TOL = 1e-6                   # sign guard for stability derivative
TWIN_TOL = 1e-4                   # cross-twin root agreement
MONO_TOL = 1e-6                   # downward-slack allowed in monotone width(r)

# R3 retry-aggressiveness grid
R_GRID = [round(0.30 + 0.05 * i, 2) for i in range(14)]   # 0.30 .. 0.95

# root-scan domains
X_MIN, X_MAX = 1e-3, 700.0


# --------------------------------------------------------------------- model
def sigmoid(z):
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def pfail(x):
    """Logistic failure probability at in-flight load x."""
    return P0 + (1.0 - P0) * sigmoid(K * (x / C - THETA))


def pfail_prime(x):
    """Analytic d p / d x."""
    s = sigmoid(K * (x / C - THETA))
    return (1.0 - P0) * s * (1.0 - s) * (K / C)


def F_balance(x, lam, r):
    """Steady-state residual (uncapped)."""
    return lam + r * pfail(x) * x - x


def F_prime(x, lam, r):
    """Analytic dF/dx (independent of lam)."""
    return r * (pfail(x) + x * pfail_prime(x)) - 1.0


def F_cap(x, lam, r, b):
    """Steady-state residual with a retry-budget cap: retries <= b*lambda."""
    retry = r * pfail(x) * x
    cap = b * lam
    if retry > cap:
        retry = cap
    return lam + retry - x


def G_cont(x, r):
    """COLD-branch continuation quantity: F(x)=0 <=> G(x)=lambda."""
    return x * (1.0 - r * pfail(x))


def G_prime(x, r):
    """Analytic dG/dx = -F'(x)."""
    return 1.0 - r * (pfail(x) + x * pfail_prime(x))


# ------------------------------------------------------- twin A: bisection roots
def roots_bisect(func, args, lo, hi, n):
    """Bracket sign changes on a dense grid, refine each by bisection."""
    step = (hi - lo) / n
    out = []
    xa = lo
    fa = func(xa, *args)
    for i in range(1, n + 1):
        xb = lo + i * step
        fb = func(xb, *args)
        if fa == 0.0:
            out.append(xa)
        elif fa * fb < 0.0:
            a, b, faa = xa, xb, fa
            for _ in range(100):
                m = 0.5 * (a + b)
                fm = func(m, *args)
                if faa * fm <= 0.0:
                    b = m
                else:
                    a, faa = m, fm
            out.append(0.5 * (a + b))
        xa, fa = xb, fb
    return _dedupe(out)


# ---------------------------------------------------------- twin B: secant roots
def roots_secant(func, args, lo, hi, n):
    """Coarse-bracket sign changes, refine each by the secant method."""
    step = (hi - lo) / n
    out = []
    xa = lo
    fa = func(xa, *args)
    for i in range(1, n + 1):
        xb = lo + i * step
        fb = func(xb, *args)
        if fa * fb < 0.0:
            p0x, p1x = xa, xb
            f0, f1 = fa, fb
            root = None
            for _ in range(100):
                denom = (f1 - f0)
                if denom == 0.0:
                    root = 0.5 * (p0x + p1x)
                    break
                p2 = p1x - f1 * (p1x - p0x) / denom
                if p2 < xa:
                    p2 = xa
                elif p2 > xb:
                    p2 = xb
                f2 = func(p2, *args)
                p0x, f0 = p1x, f1
                p1x, f1 = p2, f2
                if abs(f2) < 1e-13 or abs(p1x - p0x) < 1e-12:
                    root = p1x
                    break
            if root is None:
                root = p1x
            out.append(root)
        xa, fa = xb, fb
    return _dedupe(out)


def _dedupe(xs):
    xs = sorted(xs)
    out = []
    for x in xs:
        if not out or abs(x - out[-1]) > 1e-6:
            out.append(x)
    return out


def classify(func_prime, args, x):
    """Stable if dF/dx < 0 (dx/dt = F(x)); unstable if > 0."""
    d = func_prime(x, *args)
    if d < -STAB_TOL:
        return "stable"
    if d > STAB_TOL:
        return "unstable"
    return "marginal"


# ------------------------------------------------------------- folds (twin pair)
def folds_via_extrema(r):
    """Twin A fold finder: local max/min of G(x) via G'(x) sign changes."""
    xs_n = 12000
    step = (X_MAX - 1.0) / xs_n
    exts = []
    xa = 1.0
    ga = G_prime(xa, r)
    for i in range(1, xs_n + 1):
        xb = 1.0 + i * step
        gb = G_prime(xb, r)
        if ga * gb < 0.0:
            a, b, gaa = xa, xb, ga
            for _ in range(100):
                m = 0.5 * (a + b)
                gm = G_prime(m, r)
                if gaa * gm <= 0.0:
                    b = m
                else:
                    a, gaa = m, gm
            exts.append(0.5 * (a + b))
        xa, ga = xb, gb
    if len(exts) < 2:
        return None
    vals = [(x, G_cont(x, r)) for x in exts]
    lam_up = max(v for _, v in vals)
    lam_down = min(v for _, v in vals)
    x_up = [x for x, v in vals if v == lam_up][0]
    x_down = [x for x, v in vals if v == lam_down][0]
    return {"lam_up": lam_up, "lam_down": lam_down,
            "width": lam_up - lam_down, "x_up": x_up, "x_down": x_down}


def folds_via_rootcount(r, dlam=0.25):
    """Twin B fold finder: lambda-sweep root count; folds bound the 3-root window."""
    lo, hi = 2.0, 120.0
    n = int(round((hi - lo) / dlam))
    lam_lo3 = None
    lam_hi3 = None
    for i in range(n + 1):
        lam = lo + i * dlam
        rts = roots_bisect(F_balance, (lam, r), X_MIN, X_MAX, 3500)
        if len(rts) >= 3:
            if lam_lo3 is None:
                lam_lo3 = lam
            lam_hi3 = lam
    if lam_lo3 is None:
        return None
    # lambda_down ~ lam_lo3 (below it HOT gone), lambda_up ~ lam_hi3 (above it COLD gone)
    return {"lam_up": lam_hi3, "lam_down": lam_lo3,
            "width": lam_hi3 - lam_lo3}


# ------------------------------------------------------------ stochastic run R1b
def stochastic_branch(x0, rep):
    """One seeded replicate of the noisy map; mean utilization over last window."""
    seed = (SEED_BASE * 1000003 + rep * 7919 + int(round(x0 * 131.0))) % (2 ** 63)
    rng = random.Random(seed)
    x = x0
    acc = 0.0
    cnt = 0
    start = T_STEPS - T_WINDOW
    for t in range(T_STEPS):
        drift = LAM + R_PIN * pfail(x) * x
        # Poisson-style multiplicative noise (variance grows with load)
        x = drift + NOISE * math.sqrt(max(x, 0.0)) * rng.gauss(0.0, 1.0)
        if x < 0.1:
            x = 0.1
        if t >= start:
            acc += x / C
            cnt += 1
    return acc / cnt


def stochastic_separation(cold_x0, hot_x0):
    cold = [stochastic_branch(cold_x0, i) for i in range(N_REP)]
    hot = [stochastic_branch(hot_x0, i) for i in range(N_REP)]
    mc, sc = mean(cold), sample_std(cold)
    mh, sh = mean(hot), sample_std(hot)
    denom = math.sqrt(sc * sc / N_REP + sh * sh / N_REP)
    if denom < 1e-12:
        denom = 1e-12
    z = (mh - mc) / denom
    return {"cold_mean_u": mc, "cold_std_u": sc, "hot_mean_u": mh,
            "hot_std_u": sh, "sep_sigma": z}


# --------------------------------------------------------------------- stats
def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


# -------------------------------------------------------------- twin decisions
GATE_ORDER = ("R1", "R2", "R3", "R4")


def decide_ifchain(gates):
    if not gates["R1"]["passed"]:
        return ("REJECT", "R1")
    if not gates["R2"]["passed"]:
        return ("REJECT", "R2")
    if not gates["R3"]["passed"]:
        return ("REJECT", "R3")
    if not gates["R4"]["passed"]:
        return ("REJECT", "R4")
    return ("APPROVE", None)


def decide_table(gates):
    for g in GATE_ORDER:
        if not gates[g]["passed"]:
            return ("REJECT", g)
    return ("APPROVE", None)


# ---------------------------------------------------------------------- helpers
def rnd(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, float):
        return round(x, 9)
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v) for v in x]
    return x


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fmt(x):
    return "%.6f" % x


# --------------------------------------------------------------------- main
def main():
    out = []

    def emit(line=""):
        out.append(line)

    # ================================================== pinned-world fixed points
    args = (LAM, R_PIN)
    roots_a = roots_bisect(F_balance, args, X_MIN, X_MAX, 12000)
    roots_b = roots_secant(F_balance, args, X_MIN, X_MAX, 3000)
    # twin cross-check: same count and same positions
    twin_roots_agree = (len(roots_a) == len(roots_b) and
                        all(abs(a - b) <= TWIN_TOL
                            for a, b in zip(roots_a, roots_b)))
    if not twin_roots_agree:
        raise SystemExit("twin root-finders disagree: %s vs %s"
                         % (roots_a, roots_b))

    n_roots = len(roots_a)
    cold = roots_a[0] if n_roots >= 1 else None
    hot = roots_a[-1] if n_roots >= 1 else None
    middle = roots_a[1] if n_roots >= 3 else None

    cold_stab = classify(F_prime, args, cold) if cold is not None else "none"
    hot_stab = classify(F_prime, args, hot) if hot is not None else "none"
    mid_stab = classify(F_prime, args, middle) if middle is not None else "none"

    x_star = LAM / (1.0 - R_PIN)   # collapsed mean-field fixed point = 400

    # ---- R1a structural bistability
    r1a = (n_roots == 3 and
           COLD_LO <= cold <= COLD_HI and cold_stab == "stable" and
           HOT_LO <= hot <= HOT_HI and hot_stab == "stable" and
           mid_stab == "unstable")

    # ---- R1b stochastic separation
    sep = stochastic_separation(cold, hot)
    r1b = (sep["sep_sigma"] >= SIG and
           sep["cold_mean_u"] < 1.0 and sep["hot_mean_u"] > 2.0)

    r1_pass = r1a and r1b
    gate_R1 = {"passed": r1_pass, "passed_structure": r1a, "passed_stochastic": r1b,
               "n_roots": n_roots, "cold": cold, "cold_u": cold / C,
               "cold_stability": cold_stab, "middle": middle,
               "middle_stability": mid_stab, "hot": hot, "hot_u": hot / C,
               "hot_stability": hot_stab, "x_star_meanfield": x_star,
               "hot_minus_xstar": (hot - x_star) if hot is not None else None,
               "sep_sigma": sep["sep_sigma"], "cold_mean_u": sep["cold_mean_u"],
               "hot_mean_u": sep["hot_mean_u"], "cold_std_u": sep["cold_std_u"],
               "hot_std_u": sep["hot_std_u"]}

    # ================================================================ R2 hysteresis
    fold_a = folds_via_extrema(R_PIN)
    fold_b = folds_via_rootcount(R_PIN)
    # twin cross-check: fold widths agree to the lambda-sweep step
    folds_agree = (fold_a is not None and fold_b is not None and
                   abs(fold_a["lam_up"] - fold_b["lam_up"]) <= 0.5 and
                   abs(fold_a["lam_down"] - fold_b["lam_down"]) <= 0.5)
    if not folds_agree:
        raise SystemExit("twin fold finders disagree: %s vs %s" % (fold_a, fold_b))

    lam_up = fold_a["lam_up"]
    lam_down = fold_a["lam_down"]
    width = fold_a["width"]
    coexist = (lam_down < LAM < lam_up) and (n_roots == 3)
    width_ok = abs(width - WIDTH_TARGET) <= WIDTH_TOL
    r2_pass = width_ok and coexist
    gate_R2 = {"passed": r2_pass, "lam_up": lam_up, "lam_down": lam_down,
               "width": width, "width_target": WIDTH_TARGET, "width_tol": WIDTH_TOL,
               "width_ok": width_ok, "coexist_at_lam60": coexist,
               "lam_up_rootcount": fold_b["lam_up"],
               "lam_down_rootcount": fold_b["lam_down"]}

    # =============================================================== R3 retry-lever
    def op_margin(fd):
        # how far below lambda=60 the HOT branch survives (0 if op point monostable)
        if fd is None:
            return 0.0
        m = LAM - fd["lam_down"]
        return m if m > 0.0 else 0.0

    def op_bistable(fd):
        return fd is not None and (fd["lam_down"] < LAM < fd["lam_up"])

    r3_rows = []
    for r in R_GRID:
        fd = folds_via_extrema(r)
        w = fd["width"] if fd is not None else 0.0
        r3_rows.append({"r": r, "width": w, "lam_up": (fd["lam_up"] if fd else None),
                        "lam_down": (fd["lam_down"] if fd else None),
                        "op_margin": op_margin(fd), "op_bistable": op_bistable(fd)})

    # monotone non-decreasing fold width across r-grid
    max_width_drop = 0.0
    max_margin_drop = 0.0
    for i in range(1, len(r3_rows)):
        dw = r3_rows[i - 1]["width"] - r3_rows[i]["width"]
        dm = r3_rows[i - 1]["op_margin"] - r3_rows[i]["op_margin"]
        if dw > max_width_drop:
            max_width_drop = dw
        if dm > max_margin_drop:
            max_margin_drop = dm
    width_monotone = max_width_drop <= MONO_TOL
    margin_monotone = max_margin_drop <= MONO_TOL

    # r_c = onset of operating-point bistability: bisect lambda_down(r) = LAM
    def lam_down_of(r):
        fd = folds_via_extrema(r)
        return fd["lam_down"] if fd is not None else float("inf")

    r_lo, r_hi = 0.40, 0.75
    for _ in range(60):
        rm = 0.5 * (r_lo + r_hi)
        if lam_down_of(rm) > LAM:      # not yet bistable at op point
            r_lo = rm
        else:
            r_hi = rm
    r_c = 0.5 * (r_lo + r_hi)
    rc_ok = abs(r_c - RC_TARGET) <= RC_TOL

    # below r_c monostable at op point, above r_c bistable at op point
    below = [row for row in r3_rows if row["r"] < r_c - 1e-9]
    above = [row for row in r3_rows if row["r"] > r_c + 1e-9]
    onset_clean = (all(not row["op_bistable"] for row in below) and
                   all(row["op_bistable"] for row in above))

    r3_pass = width_monotone and margin_monotone and rc_ok and onset_clean
    gate_R3 = {"passed": r3_pass, "width_monotone": width_monotone,
               "margin_monotone": margin_monotone, "max_width_drop": max_width_drop,
               "max_margin_drop": max_margin_drop, "r_c": r_c,
               "rc_target": RC_TARGET, "rc_tol": RC_TOL, "rc_ok": rc_ok,
               "onset_clean": onset_clean}

    # ================================================================= R4 knockout
    capped = roots_bisect(F_cap, (LAM, R_PIN, B_CAP), X_MIN, X_MAX, 12000)
    n_capped = len(capped)
    n_uncapped = n_roots
    hot_present_uncapped = any(r > HOT_LO for r in roots_a)
    hot_present_capped = any(r > HOT_LO for r in capped)
    r4_pass = (n_uncapped == 3 and hot_present_uncapped and
               n_capped == 1 and (not hot_present_capped) and
               COLD_LO <= capped[0] <= COLD_HI)
    gate_R4 = {"passed": r4_pass, "b_cap": B_CAP, "n_roots_uncapped": n_uncapped,
               "n_roots_capped": n_capped, "hot_present_uncapped": hot_present_uncapped,
               "hot_present_capped": hot_present_capped,
               "capped_root": capped[0] if capped else None,
               "capped_root_u": (capped[0] / C) if capped else None,
               "cap_binds_at": B_CAP * LAM}

    gates = {"R1": gate_R1, "R2": gate_R2, "R3": gate_R3, "R4": gate_R4}

    # ---- twin decision procedures
    ver_if, gate_if = decide_ifchain(gates)
    ver_tb, gate_tb = decide_table(gates)
    twins_agree = (ver_if == ver_tb) and (gate_if == gate_tb)
    if not twins_agree:
        raise SystemExit("twin disagreement: ifchain=%s table=%s"
                         % ((ver_if, gate_if), (ver_tb, gate_tb)))
    verdict = ver_if
    first_failing_gate = gate_if

    # ---- self-checks
    checks = []

    def chk(name, ok):
        checks.append({"name": name, "ok": bool(ok)})

    chk("twin_roots_agree", twin_roots_agree)
    chk("three_fixed_points", n_roots == 3)
    chk("cold_near_61", abs(cold - 61.0) <= 6.0)
    chk("hot_equals_xstar_400", abs(hot - x_star) <= STAR_TOL)
    chk("cold_stable", cold_stab == "stable")
    chk("hot_stable", hot_stab == "stable")
    chk("middle_unstable", mid_stab == "unstable")
    # analytic vs numeric derivative at each root (independent derivative check)
    for label, xr in (("cold", cold), ("middle", middle), ("hot", hot)):
        h = 1e-4
        num = (F_balance(xr + h, *args) - F_balance(xr - h, *args)) / (2 * h)
        ana = F_prime(xr, *args)
        chk("Fprime_analytic_vs_numeric_%s" % label, abs(num - ana) <= 1e-4)
    chk("stochastic_separation_ge_SIG", sep["sep_sigma"] >= SIG)
    chk("stochastic_cold_healthy", sep["cold_mean_u"] < 1.0)
    chk("stochastic_hot_collapsed", sep["hot_mean_u"] > 2.0)
    chk("folds_twin_agree", folds_agree)
    chk("width_near_56", abs(width - WIDTH_TARGET) <= WIDTH_TOL)
    chk("coexist_at_lam60", coexist)
    chk("width_monotone_in_r", width_monotone)
    chk("op_margin_monotone_in_r", margin_monotone)
    chk("rc_near_0566", rc_ok)
    chk("rc_onset_clean", onset_clean)
    chk("cap_eliminates_hot", (n_capped == 1) and (not hot_present_capped))
    chk("uncapped_hot_present", hot_present_uncapped)
    # determinism: two in-process stochastic replicates identical
    a = stochastic_branch(cold, 0)
    b2 = stochastic_branch(cold, 0)
    chk("determinism_in_process", a == b2)
    chk("params_pinned", (C == 100.0 and P0 == 0.02 and K == 12.0 and
                          THETA == 1.05 and R_PIN == 0.85 and LAM == 60.0 and
                          B_CAP == 0.20 and SEED_BASE == 20260721 and SIG == 3.0))
    chk("twins_agree", twins_agree)

    self_checks_passed = sum(1 for c in checks if c["ok"])
    self_checks_total = len(checks)
    all_self_checks_pass = self_checks_passed == self_checks_total

    # ---- fixtures drift guard
    fx = {
        "params": {"C": C, "P0": P0, "K": K, "THETA": THETA, "R_PIN": R_PIN,
                   "LAM": LAM, "B_CAP": B_CAP, "SEED_BASE": SEED_BASE, "SIG": SIG},
        "anchors": rnd({"cold": cold, "middle": middle, "hot": hot,
                        "x_star": x_star, "lam_up": lam_up, "lam_down": lam_down,
                        "width": width, "r_c": r_c,
                        "sep_sigma": sep["sep_sigma"],
                        "n_roots_capped": n_capped}),
    }
    fx_text = json.dumps(fx, sort_keys=True, indent=2) + "\n"
    fx_path = os.path.join(HERE, "fixtures.json")
    if os.path.exists(fx_path):
        with open(fx_path, "r") as fh:
            committed = fh.read()
        if committed != fx_text:
            raise SystemExit("fixture drift: committed fixtures.json != recomputed")
    else:
        with open(fx_path, "w") as fh:
            fh.write(fx_text)
    fixtures_sha256 = sha256_file(fx_path)

    # ---- build stdout
    emit("VERDICT 106 - Retry-amplified metastable overload collapse "
         "(idea-engine PROPOSAL 093)")
    emit("world: c=%d p0=%s k=%s theta=%s r=%s lambda=%s b=%s SEED_BASE=%d SIG=%s"
         % (int(C), P0, K, THETA, R_PIN, LAM, B_CAP, SEED_BASE, SIG))
    emit("")
    emit("fixed points of F(x)=lambda+r*p(x)*x-x  (roots=%d)" % n_roots)
    emit("   name         x        u=x/c   dF/dx      stability")
    emit("   COLD   %9s   %7s   %8s   %s"
         % (fmt(cold), fmt(cold / C), fmt(F_prime(cold, *args)), cold_stab))
    if middle is not None:
        emit("   MIDDLE %9s   %7s   %8s   %s"
             % (fmt(middle), fmt(middle / C), fmt(F_prime(middle, *args)), mid_stab))
    emit("   HOT    %9s   %7s   %8s   %s"
         % (fmt(hot), fmt(hot / C), fmt(F_prime(hot, *args)), hot_stab))
    emit("   x* mean-field = lambda/(1-r) = %s  (HOT-x* = %s)"
         % (fmt(x_star), fmt(hot - x_star)))
    emit("")
    emit("R1a bistability structure -> %s" % ("PASS" if r1a else "FAIL"))
    emit("R1b stochastic (%d reps x %d steps): cold u=%s+-%s  hot u=%s+-%s  sep=%s sigma -> %s"
         % (N_REP, T_STEPS, fmt(sep["cold_mean_u"]), fmt(sep["cold_std_u"]),
            fmt(sep["hot_mean_u"]), fmt(sep["hot_std_u"]), fmt(sep["sep_sigma"]),
            "PASS" if r1b else "FAIL"))
    emit("R1 -> %s" % ("PASS" if r1_pass else "FAIL"))
    emit("")
    emit("R2 hysteresis: lambda_up=%s lambda_down=%s width=%s (target %s +-%s)"
         % (fmt(lam_up), fmt(lam_down), fmt(width), WIDTH_TARGET, WIDTH_TOL))
    emit("   root-count twin: lambda_up=%s lambda_down=%s ; coexist@lambda=60: %s"
         % (fmt(fold_b["lam_up"]), fmt(fold_b["lam_down"]), coexist))
    emit("R2 -> %s" % ("PASS" if r2_pass else "FAIL"))
    emit("")
    emit("R3 retry-lever sweep")
    emit("      r      width    lam_up   lam_down   op_margin  op_bistable")
    for row in r3_rows:
        emit("   %5.2f   %8s   %7s   %8s   %8s   %s"
             % (row["r"], fmt(row["width"]),
                fmt(row["lam_up"]) if row["lam_up"] is not None else "   -   ",
                fmt(row["lam_down"]) if row["lam_down"] is not None else "   -   ",
                fmt(row["op_margin"]), "Y" if row["op_bistable"] else "N"))
    emit("   width monotone (max drop %s<=%s): %s ; op-margin monotone (max drop %s): %s"
         % (fmt(max_width_drop), MONO_TOL, width_monotone,
            fmt(max_margin_drop), margin_monotone))
    emit("   r_c (op-point bistability onset, lambda_down=60) = %s (target %s +-%s)"
         % (fmt(r_c), RC_TARGET, RC_TOL))
    emit("R3 -> %s" % ("PASS" if r3_pass else "FAIL"))
    emit("")
    emit("R4 knockout (retry budget cap b=%s, binds at r*p*x > %s)"
         % (B_CAP, fmt(B_CAP * LAM)))
    emit("   uncapped roots=%d (HOT present=%s) ; capped roots=%d (HOT present=%s)"
         % (n_uncapped, hot_present_uncapped, n_capped, hot_present_capped))
    emit("   capped fixed point x=%s (u=%s)"
         % (fmt(capped[0]), fmt(capped[0] / C)))
    emit("R4 -> %s" % ("PASS" if r4_pass else "FAIL"))
    emit("")
    emit("gates:")
    for g in GATE_ORDER:
        emit("  %s passed=%s" % (g, gates[g]["passed"]))
    emit("")
    emit("twins: ifchain=%s table=%s agree=%s"
         % ((ver_if, gate_if), (ver_tb, gate_tb), twins_agree))
    emit("")
    emit("self-checks %d/%d" % (self_checks_passed, self_checks_total))
    for c in checks:
        emit("  [%s] %s" % ("ok" if c["ok"] else "XX", c["name"]))
    emit("")

    # ---- results.json
    results = {
        "verdict": verdict,
        "first_failing_gate": first_failing_gate,
        "world": {"C": C, "P0": P0, "K": K, "THETA": THETA, "R_PIN": R_PIN,
                  "LAM": LAM, "B_CAP": B_CAP, "SEED_BASE": SEED_BASE, "SIG": SIG,
                  "N_REP": N_REP, "T_STEPS": T_STEPS, "T_WINDOW": T_WINDOW,
                  "NOISE": NOISE, "r_grid": R_GRID,
                  "tolerances": {"WIDTH_TARGET": WIDTH_TARGET, "WIDTH_TOL": WIDTH_TOL,
                                 "RC_TARGET": RC_TARGET, "RC_TOL": RC_TOL,
                                 "STAR_TOL": STAR_TOL, "MONO_TOL": MONO_TOL}},
        "fixed_points": {"n_roots": n_roots, "cold": cold, "middle": middle,
                         "hot": hot, "x_star": x_star,
                         "cold_stability": cold_stab, "middle_stability": mid_stab,
                         "hot_stability": hot_stab},
        "gates": gates,
        "r3_sweep": r3_rows,
        "twin": {"agree": twins_agree, "ifchain": [ver_if, gate_if],
                 "table": [ver_tb, gate_tb], "roots_agree": twin_roots_agree,
                 "folds_agree": folds_agree},
        "self_checks": checks,
        "self_checks_passed": self_checks_passed,
        "self_checks_total": self_checks_total,
        "fixtures_sha256": fixtures_sha256,
    }
    results_text = json.dumps(rnd(results), sort_keys=True, indent=2) + "\n"
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        fh.write(results_text)

    results_sha = sha256_file(os.path.join(HERE, "results.json"))
    emit("sha256 fixtures.json = %s" % fixtures_sha256)
    emit("sha256 results.json  = %s" % results_sha)
    emit("")
    emit("RULING: %s (first-failing gate: %s)"
         % (verdict, first_failing_gate if first_failing_gate else "none"))

    stdout_text = "\n".join(out) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w") as fh:
        fh.write(stdout_text)
    print(stdout_text, end="")

    # ---- exit contract
    if not (all_self_checks_pass and twins_agree):
        raise SystemExit("self-checks or twins failed: %d/%d, twins=%s"
                         % (self_checks_passed, self_checks_total, twins_agree))


if __name__ == "__main__":
    main()
