#!/usr/bin/env python3
"""
growth_cash_trough_trap.py  --  sim-lab verifier for "The growth cash-trough trap".

Counterintuitive claim: take TWO subscription ventures with IDENTICAL, POSITIVE
per-customer unit economics (lifetime value LTV > acquisition cost CAC). The one
that GROWS FASTER has a strictly DEEPER cash trough (a more negative low-water
cash position) and a higher probability of ruin for the same starting capital.
Growth CONSUMES cash even when every customer is individually profitable, because
CAC is paid UPFRONT while the margin trickles in over the customer's lifetime.
"Our unit economics are positive, so scale acquisition hard" is a ruin trap:
above a critical growth rate g_crit the firm's per-period cash flow is PERMANENTLY
negative despite LTV > CAC.

Model (discrete monthly periods, per-customer economics identical across regimes):
  - Acquisitions in period k: n_k ~ Poisson(A0 * g^k)  (geometric-growth funnel).
  - Each new customer costs CAC upfront (paid the period acquired).
  - Each active customer pays margin m every period it is active (incl. the period
    acquired), then churns at end of period with prob c (survival s = 1 - c);
    lifetime paying-periods ~ Geometric(c), mean 1/c, so LTV = m/c.
  - Cash flow period k:  CF_k = m * active_k  -  CAC * n_k.
  - Cumulative cash C_k = sum_{i<=k} CF_i.  Trough = min_k C_k (deepest low-water).
  - Ruin (reported): trough < -K0 for starting capital K0.

Analytic anchors (fluid limit, exact in expectation since E is linear):
  - E[active_k] = A0 * (g^{k+1} - s^{k+1}) / (g - s)        (s = 1 - c, g != s)
  - E[C_k]      = sum_{i=0}^{k} ( m*E[active_i] - CAC*A0*g^i )
  - CF asymptotically positive iff  m*g/(g - s) > CAC, i.e.  g < g_crit,
        g_crit = CAC * s / (CAC - m)     (below: cash recovers; above: permanent burn)
  - Cohort-0 truncated per-customer profit over the T-period horizon:
        pi0(T) = m * (1 - s^T) / c  -  CAC   (identical across g; the unit-economics control)

Gates (pre-registered, >=3 sigma):
  G1  cash-trough trap (headline): mean trough(g_high) is MORE NEGATIVE than
      mean trough(g_low) by >= 3 sigma -- faster growth => deeper trough.
  G2  identical positive unit economics (control): cohort-0 realized per-customer
      profit matches the truncated analytic pi0(T) within 3 sigma in BOTH regimes,
      is > 0 by >= 3 sigma, and the two regimes do NOT differ (|z| < 3 sigma) --
      so the trough gap is a TIMING/scale effect, not a unit-economics difference.
  G3  fluid anchor MATCH: sim mean cumulative cash C_k at each regime's own fluid
      trough period k* matches the closed-form E[C_{k*}] within 3 sigma (both regimes).

stdlib only: random, math, json, hashlib.
"""

import random
import math
import json
import hashlib

# ----------------------------------------------------------------------------
# Pinned parameters (chosen so LTV > CAC in BOTH regimes, g_low < g_crit < g_high,
# and every gate clears with a comfortable >=3-sigma margin).
# ----------------------------------------------------------------------------
SEED     = 20260717        # fixed integer seed -> fully deterministic run
T        = 24              # horizon in periods (months)
A0       = 10.0            # baseline acquisitions in period 0 (Poisson mean)
M        = 10.0            # margin collected per active customer per period
C_CHURN  = 0.10            # per-period churn prob (survival s = 0.90); mean life 1/c = 10
CAC      = 60.0            # upfront customer-acquisition cost
N_REPS   = 4000            # Monte-Carlo company trajectories per growth level
K0       = 3000.0          # starting capital (for reported ruin probability only)

# Growth sweep; g_low / g_high are the two headline regimes.
GROWTHS  = [1.05, 1.08, 1.15, 1.30]
G_LOW    = 1.05
G_HIGH   = 1.30

S_SURV   = 1.0 - C_CHURN   # per-period survival prob


# ----------------------------------------------------------------------------
# Analytic (fluid-limit) helpers
# ----------------------------------------------------------------------------
def fluid_active(k, g):
    """E[active customers] in period k under geometric acquisition A0*g^i."""
    if abs(g - S_SURV) < 1e-12:
        # degenerate g == s: active_k = A0 * (k+1) * s^k
        return A0 * (k + 1) * (S_SURV ** k)
    return A0 * (g ** (k + 1) - S_SURV ** (k + 1)) / (g - S_SURV)


def fluid_cumcash(g):
    """List E[C_0..C_{T-1}] of cumulative cash under the fluid limit."""
    cum = 0.0
    out = []
    for k in range(T):
        cf = M * fluid_active(k, g) - CAC * A0 * (g ** k)
        cum += cf
        out.append(cum)
    return out


def g_crit():
    """Growth rate above which per-period cash flow is permanently negative."""
    return CAC * S_SURV / (CAC - M)


def pi0_truncated():
    """Cohort-0 per-customer profit truncated at the T-period horizon."""
    return M * (1.0 - S_SURV ** T) / C_CHURN - CAC


# ----------------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------------
def _poisson(lam):
    """Knuth Poisson sampler (stdlib random only); normal approx for large lambda."""
    if lam <= 0.0:
        return 0
    if lam < 30.0:
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            k += 1
            p *= random.random()
            if p <= L:
                return k - 1
    val = int(round(random.gauss(lam, math.sqrt(lam))))
    return val if val > 0 else 0


def _binomial(n, p):
    """Binomial via Bernoulli sum for small n, normal approx for large n."""
    if n <= 0:
        return 0
    if n <= 80:
        return sum(1 for _ in range(n) if random.random() < p)
    val = int(round(random.gauss(n * p, math.sqrt(n * p * (1.0 - p)))))
    return 0 if val < 0 else (n if val > n else val)


def simulate(g):
    """One company trajectory. Returns (trough, cumcash_path, c0_profit)."""
    active = 0                 # all-cohort active customers
    cum = 0.0
    trough = float("inf")
    path = []
    # cohort-0 unit-economics control
    c0_active = 0
    c0_initial = 0
    c0_revenue = 0.0
    for k in range(T):
        lam = A0 * (g ** k)
        n_new = _poisson(lam)
        if k == 0:
            c0_initial = n_new
            c0_active = n_new
        # 1. acquire (pay CAC upfront); new customers join and pay this period
        cum -= CAC * n_new
        active += n_new
        # 2. revenue: all active (incl. just-acquired) pay margin m
        cum += M * active
        path.append(cum)               # cumulative cash after period k
        if cum < trough:
            trough = cum
        # cohort-0 revenue (its survivors pay m)
        c0_revenue += M * c0_active
        # 3. churn at end of period
        active = active - _binomial(active, C_CHURN)
        c0_active = c0_active - _binomial(c0_active, C_CHURN)
    if c0_initial > 0:
        c0_profit = (c0_revenue - CAC * c0_initial) / c0_initial
    else:
        c0_profit = None
    return trough, path, c0_profit


def run_level(g):
    """N_REPS trajectories at growth g; tracks trough, ruin, cohort-0, per-period path."""
    sum_tr = 0.0; sumsq_tr = 0.0
    ruins = 0
    n_c0 = 0; sum_c0 = 0.0; sumsq_c0 = 0.0
    sum_path = [0.0] * T
    sumsq_path = [0.0] * T
    for _ in range(N_REPS):
        tr, path, c0 = simulate(g)
        sum_tr += tr; sumsq_tr += tr * tr
        if tr < -K0:
            ruins += 1
        for k in range(T):
            sum_path[k] += path[k]
            sumsq_path[k] += path[k] * path[k]
        if c0 is not None:
            n_c0 += 1; sum_c0 += c0; sumsq_c0 += c0 * c0
    mean_tr = sum_tr / N_REPS
    var_tr = max((sumsq_tr - N_REPS * mean_tr * mean_tr) / (N_REPS - 1), 0.0)
    se_tr = math.sqrt(var_tr / N_REPS)
    mean_path = []
    se_path = []
    for k in range(T):
        mp = sum_path[k] / N_REPS
        vp = max((sumsq_path[k] - N_REPS * mp * mp) / (N_REPS - 1), 0.0)
        mean_path.append(mp)
        se_path.append(math.sqrt(vp / N_REPS))
    mean_c0 = sum_c0 / n_c0 if n_c0 else 0.0
    var_c0 = max((sumsq_c0 - n_c0 * mean_c0 * mean_c0) / (n_c0 - 1), 0.0) if n_c0 > 1 else 0.0
    se_c0 = math.sqrt(var_c0 / n_c0) if n_c0 else 0.0
    return {
        "g": g,
        "mean_trough": mean_tr, "se_trough": se_tr,
        "ruin_prob": ruins / N_REPS,
        "mean_path": mean_path, "se_path": se_path,
        "mean_c0_profit": mean_c0, "se_c0_profit": se_c0, "n_c0": n_c0,
    }


def z_diff(a, sea, b, seb):
    sd = math.sqrt(sea * sea + seb * seb)
    if sd == 0.0:
        return float("inf") if a != b else 0.0
    return (a - b) / sd


def main():
    random.seed(SEED)

    gcrit = g_crit()
    pi0 = pi0_truncated()
    ltv = M / C_CHURN

    print("=" * 78)
    print("THE GROWTH CASH-TROUGH TRAP  --  sim-lab verifier")
    print("=" * 78)
    print("Parameters (pinned):")
    print(f"  SEED={SEED}  T={T}  A0={A0}  M={M}  c={C_CHURN} (s={S_SURV})  CAC={CAC}")
    print(f"  N_REPS={N_REPS}  K0(start capital)={K0}  growth sweep={GROWTHS}")
    print(f"  LTV = m/c = {ltv}   per-customer profit (untruncated) = LTV-CAC = {ltv-CAC}")
    print(f"  g_crit = CAC*s/(CAC-m) = {gcrit:.6f}   (g<g_crit recovers; g>g_crit permanent burn)")
    print(f"  cohort-0 truncated profit pi0(T) = m*(1-s^T)/c - CAC = {pi0:.6f}  (>0, identical across g)")
    print(f"  g_low={G_LOW} (< g_crit)   g_high={G_HIGH} (> g_crit)")
    print()

    print(f"Running Monte-Carlo ({N_REPS} trajectories x {len(GROWTHS)} growth levels)...")
    levels = {}
    for g in GROWTHS:
        levels[g] = run_level(g)
        r = levels[g]
        fpath = fluid_cumcash(g)
        kstar = min(range(T), key=lambda i: fpath[i])
        print(f"  g={g:<5}: mean_trough={r['mean_trough']:14.2f} (se {r['se_trough']:9.2f})  "
              f"ruin_p={r['ruin_prob']:.3f}  fluid_kstar={kstar:2d} fluid_C*={fpath[kstar]:12.2f}  "
              f"pi0={r['mean_c0_profit']:7.3f}(se {r['se_c0_profit']:.3f})")
    print()

    Llow, Lhigh = levels[G_LOW], levels[G_HIGH]

    # ---- G1: cash-trough trap (deeper with growth) ----
    z_g1 = z_diff(Llow["mean_trough"], Llow["se_trough"],
                  Lhigh["mean_trough"], Lhigh["se_trough"])
    g1 = z_g1 >= 3.0

    # ---- G2: identical positive unit economics (control) ----
    z_low_anchor  = abs(Llow["mean_c0_profit"] - pi0) / Llow["se_c0_profit"] if Llow["se_c0_profit"] > 0 else 0.0
    z_high_anchor = abs(Lhigh["mean_c0_profit"] - pi0) / Lhigh["se_c0_profit"] if Lhigh["se_c0_profit"] > 0 else 0.0
    z_low_pos  = Llow["mean_c0_profit"] / Llow["se_c0_profit"] if Llow["se_c0_profit"] > 0 else 0.0
    z_high_pos = Lhigh["mean_c0_profit"] / Lhigh["se_c0_profit"] if Lhigh["se_c0_profit"] > 0 else 0.0
    z_lowhigh  = z_diff(Llow["mean_c0_profit"], Llow["se_c0_profit"],
                        Lhigh["mean_c0_profit"], Lhigh["se_c0_profit"])
    g2 = (z_low_anchor < 3.0 and z_high_anchor < 3.0 and
          z_low_pos >= 3.0 and z_high_pos >= 3.0 and abs(z_lowhigh) < 3.0)

    # ---- G3: fluid anchor MATCH at each regime's fluid trough period ----
    g3_parts = {}
    g3 = True
    for tag, L in [("low", Llow), ("high", Lhigh)]:
        fpath = fluid_cumcash(L["g"])
        kstar = min(range(T), key=lambda i: fpath[i])
        analytic_Ck = fpath[kstar]
        sim_Ck = L["mean_path"][kstar]
        se_Ck = L["se_path"][kstar]
        zk = abs(sim_Ck - analytic_Ck) / se_Ck if se_Ck > 0 else 0.0
        g3_parts[tag] = {"g": L["g"], "kstar": kstar, "analytic": analytic_Ck,
                         "sim": sim_Ck, "se": se_Ck, "abs_z": zk}
        g3 = g3 and (zk < 3.0)

    print("=" * 78)
    print("PRE-REGISTERED GATES")
    print("=" * 78)
    print(f"  G1 cash-trough trap: trough(g_high) more negative than trough(g_low) by >=3 sigma")
    print(f"     trough_low ={Llow['mean_trough']:.2f}  trough_high={Lhigh['mean_trough']:.2f}  "
          f"gap={Llow['mean_trough']-Lhigh['mean_trough']:.2f}  z={z_g1:.2f} -> {'PASS' if g1 else 'FAIL'}")
    print(f"  G2 identical positive unit economics (control):")
    print(f"     pi0 anchor low |z|={z_low_anchor:.2f} high |z|={z_high_anchor:.2f} (<3)  "
          f"positivity low z={z_low_pos:.2f} high z={z_high_pos:.2f} (>=3)  "
          f"low-vs-high |z|={abs(z_lowhigh):.2f} (<3)  -> {'PASS' if g2 else 'FAIL'}")
    print(f"  G3 fluid anchor MATCH at fluid trough period:")
    for tag, p in g3_parts.items():
        print(f"     g={p['g']} k*={p['kstar']}: sim C*={p['sim']:.2f} vs analytic {p['analytic']:.2f} "
              f"|z|={p['abs_z']:.2f}")
    print(f"     -> {'PASS' if g3 else 'FAIL'}")
    print()
    all_pass = g1 and g2 and g3
    print(f"  ALL GATES PASS: {all_pass}")
    print("=" * 78)

    # ---- results dict + sha256 ----
    results = {
        "params": {
            "SEED": SEED, "T": T, "A0": A0, "M": M, "C_CHURN": C_CHURN,
            "S_SURV": S_SURV, "CAC": CAC, "N_REPS": N_REPS, "K0": K0,
            "GROWTHS": GROWTHS, "G_LOW": G_LOW, "G_HIGH": G_HIGH,
        },
        "analytic": {
            "LTV": ltv, "profit_untruncated": ltv - CAC,
            "g_crit": gcrit, "pi0_truncated": pi0,
        },
        "levels": {
            f"{g}": {
                "mean_trough": levels[g]["mean_trough"],
                "se_trough": levels[g]["se_trough"],
                "ruin_prob": levels[g]["ruin_prob"],
                "mean_c0_profit": levels[g]["mean_c0_profit"],
                "se_c0_profit": levels[g]["se_c0_profit"],
            } for g in GROWTHS
        },
        "gates": {
            "G1_trough_trap": {"z_sigma": z_g1, "pass": g1,
                               "trough_low": Llow["mean_trough"], "trough_high": Lhigh["mean_trough"]},
            "G2_unit_economics": {
                "pi0_analytic": pi0,
                "z_low_anchor": z_low_anchor, "z_high_anchor": z_high_anchor,
                "z_low_pos": z_low_pos, "z_high_pos": z_high_pos,
                "z_low_vs_high": z_lowhigh, "pass": g2,
            },
            "G3_fluid_anchor": {tag: {"g": p["g"], "kstar": p["kstar"],
                                      "analytic": p["analytic"], "sim": p["sim"], "abs_z": p["abs_z"]}
                                for tag, p in g3_parts.items()},
            "G3_pass": g3,
            "all_pass": all_pass,
        },
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print("\nRESULTS DICT:")
    print(canonical)
    print(f"\nResults-dict sha256: {digest}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
