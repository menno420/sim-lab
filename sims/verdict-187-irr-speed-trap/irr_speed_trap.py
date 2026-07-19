#!/usr/bin/env python3
"""PROPOSAL 174 - the IRR speed trap.

A venture fund's internal rate of return (IRR) is NOT monotone in the dollars it
returns to limited partners. A lower-MOIC fund that distributes faster out-IRRs a
higher-MOIC fund that distributes slower, so ranking funds on IRR can pick the one
that returns LESS money. And delaying the LP capital call with a subscription
credit line shortens the IRR clock, inflating the reported IRR even though LPs,
net of line interest, receive FEWER dollars.

Deterministic, stdlib-only (random, math, json, hashlib). SEED=20260717.
Three ordered z-gates (z_gate=3.0). Digest posture: WHOLE-DICT / NO-SELF-FIELD /
STDOUT-ONLY - the compact-canonical results dict's own sha256 is the digest;
floats rounded 6 dp before hashing. Target: sim-lab VERDICT 187 (+13 offset).
"""
import json
import math
import hashlib
import random

SEED = 20260717
Z_GATE = 3.0
TRIALS = 200000
TRIALS_G3 = 40000


def irr_bullet(moic, horizon):
    """IRR of invest 1 at t=0, receive `moic` at t=`horizon`: (1+r)^h = moic."""
    return moic ** (1.0 / horizon) - 1.0


def npv(rate, times, flows):
    s = 0.0
    for t, f in zip(times, flows):
        s += f / ((1.0 + rate) ** t)
    return s


def irr_bisect(times, flows, lo=-0.9999, hi=10.0, iters=120):
    """IRR via bisection for a standard invest-then-distribute stream."""
    flo = npv(lo, times, flows)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = npv(mid, times, flows)
        if (fm > 0.0) == (flo > 0.0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mean_se(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    se = math.sqrt(var / n)
    return m, se


def compute():
    res = {}

    # ---- Gate 1: speed beats magnitude (bullet funds) ----
    rng = random.Random(SEED)
    diffs = []
    inversions = 0
    for _ in range(TRIALS):
        m_s = rng.uniform(2.0, 3.0)   # slow-rich: more money
        t_s = rng.uniform(9.0, 13.0)  # ... returned slowly
        m_f = rng.uniform(1.15, 1.40)  # fast-poor: strictly less money
        t_f = rng.uniform(0.8, 1.6)   # ... returned fast
        r_s = irr_bullet(m_s, t_s)
        r_f = irr_bullet(m_f, t_f)
        diffs.append(r_f - r_s)
        if r_f > r_s:  # fast-poor out-IRRs slow-rich despite lower MOIC
            inversions += 1
    g1_mean, g1_se = mean_se(diffs)
    res["g1_irr_gap_mean"] = g1_mean
    res["g1_irr_gap_z"] = g1_mean / g1_se
    res["g1_inversion_fraction"] = inversions / TRIALS
    res["g1_pass"] = (g1_mean / g1_se >= Z_GATE) and (g1_mean > 0.0)
    # deterministic illustrative headline pair (no randomness)
    res["ex_slow_rich_irr"] = irr_bullet(2.4, 10.0)  # 2.4x in 10y
    res["ex_fast_poor_irr"] = irr_bullet(1.3, 1.5)   # 1.3x in 18mo

    # ---- Gate 2: subscription line raises IRR, LPs get fewer dollars ----
    rng = random.Random(SEED + 1)
    d_irr = []
    d_moic = []
    for _ in range(TRIALS):
        m = rng.uniform(2.0, 3.0)
        t = rng.uniform(9.0, 13.0)
        tau = rng.uniform(1.0, 3.0)   # capital call delayed to t=tau via the line
        c = rng.uniform(0.04, 0.10)   # line interest rate
        ic = (1.0 + c) ** tau - 1.0   # line interest on 1 unit over [0, tau]
        moic_base = m
        irr_base = irr_bullet(m, t)
        moic_line = m - ic            # LP receives less, net of line interest
        irr_line = irr_bullet(moic_line, t - tau)  # shorter IRR clock
        d_irr.append(irr_line - irr_base)
        d_moic.append(moic_line - moic_base)
    g2_dirr_mean, g2_dirr_se = mean_se(d_irr)
    g2_dmoic_mean, g2_dmoic_se = mean_se(d_moic)
    res["g2_delta_irr_mean"] = g2_dirr_mean
    res["g2_delta_irr_z"] = g2_dirr_mean / g2_dirr_se
    res["g2_delta_moic_mean"] = g2_dmoic_mean
    res["g2_delta_moic_z"] = g2_dmoic_mean / g2_dmoic_se
    res["g2_pass"] = (
        (g2_dirr_mean / g2_dirr_se >= Z_GATE)
        and (g2_dmoic_mean < 0.0)
        and (abs(g2_dmoic_mean / g2_dmoic_se) >= Z_GATE)
    )

    # ---- Gate 3: robustness under a shifted, staged (J-curve) distribution ----
    rng = random.Random(SEED + 2)
    diffs3 = []
    inv3 = 0
    for _ in range(TRIALS_G3):
        m_s = rng.uniform(2.2, 3.2)          # slow-rich, longer horizon
        t_s = rng.uniform(12.0, 16.0)
        m_f = rng.uniform(1.20, 1.45)         # fast-poor
        d0 = rng.uniform(2.0, 2.5)            # first distribution year
        slow_times = [0.0, 1.0, t_s]
        slow_flows = [-0.5, -0.5, m_s]        # staged calls, late bullet
        fast_times = [0.0, 1.0, d0, d0 + 1.0, d0 + 2.0]
        fast_flows = [-0.5, -0.5, m_f / 3.0, m_f / 3.0, m_f / 3.0]  # early spread
        r_s = irr_bisect(slow_times, slow_flows)
        r_f = irr_bisect(fast_times, fast_flows)
        diffs3.append(r_f - r_s)
        if r_f > r_s:
            inv3 += 1
    g3_mean, g3_se = mean_se(diffs3)
    res["g3_irr_gap_mean"] = g3_mean
    res["g3_irr_gap_z"] = g3_mean / g3_se
    res["g3_inversion_fraction"] = inv3 / TRIALS_G3
    res["g3_pass"] = (g3_mean / g3_se >= Z_GATE) and (g3_mean > 0.0)

    all_pass = res["g1_pass"] and res["g2_pass"] and res["g3_pass"]
    first_fail = None
    for g in ("g1_pass", "g2_pass", "g3_pass"):
        if not res[g]:
            first_fail = g
            break
    res["all_pass"] = all_pass
    res["first_failing_gate"] = first_fail
    return res


def canonicalize(d):
    out = {}
    for k, v in d.items():
        out[k] = round(v, 6) if isinstance(v, float) else v
    return out


def main():
    a = compute()
    b = compute()
    assert a == b, "non-deterministic: in-process double run differs"
    res = canonicalize(a)
    payload = json.dumps(res, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print(json.dumps(res, sort_keys=True, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if res["all_pass"] else "false"))
    print("first_failing_gate=%s" % (res["first_failing_gate"] if res["first_failing_gate"] else "null"))
    print("Results-JSON sha256 %s" % digest)
    raise SystemExit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
