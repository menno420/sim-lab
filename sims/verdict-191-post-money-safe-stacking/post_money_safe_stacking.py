#!/usr/bin/env python3
"""PROPOSAL 178 — post-money SAFEs don't share dilution: stacking taxes founders convexly.

Head: for a stack of SAFEs with post-money ownership targets o_i = investment_i /
post_money_cap_i and aggregate x = sum(o_i), founders retain f_post = 1 - x under
post-money SAFEs but f_pre = 1/(1+x) under pre-money SAFEs (which convert on a common
base and so dilute each other). The post-money stacking tax f_pre - f_post = x**2/(1+x)
is strictly positive and convex in x: each added SAFE costs the founder disproportionately
more.

Grounding: a post-money SAFE holder's ownership is fixed and not diluted by other SAFEs
or the option-pool top-up; pre-money SAFEs share dilution. See the companion doc
ideas/venture-lab/post-money-safe-stacking-2026-07-19.md.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ twist) — the sha256 of
the compact-canonical results dict IS the digest; stdout is the pretty indent=2 dump
(floats 6 dp); no on-disk JSON. SEED pinned; compute() runs twice in-process and asserts
the two dicts are identical before printing.
"""
import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 200_000
Z_GATE = 3.0
RATIO_GATE = 3.0
X_CAP = 0.85  # reject stacks selling >85% via SAFEs (keeps 1-x a realistic float)

BASE = dict(k_lo=2, k_hi=6, inv_lo=0.25, inv_hi=2.0, cap_lo=5.0, cap_hi=20.0)
SHIFT = dict(k_lo=3, k_hi=8, inv_lo=0.25, inv_hi=2.0, cap_lo=3.0, cap_hi=12.0)


def draw_x(rng, d):
    """Draw one SAFE stack; return aggregate post-money ownership x = sum(o_i).
    Rejects (resamples) any stack with x >= X_CAP. Returns (x, rejects)."""
    rejects = 0
    while True:
        k = rng.randint(d["k_lo"], d["k_hi"])
        x = 0.0
        for _ in range(k):
            inv = rng.uniform(d["inv_lo"], d["inv_hi"])
            cap = rng.uniform(d["cap_lo"], d["cap_hi"])
            x += inv / cap
        if x < X_CAP:
            return x, rejects
        rejects += 1


def tax_of(x):
    """Founder retention gap: pre-money 1/(1+x) minus post-money (1-x) = x**2/(1+x)."""
    return 1.0 / (1.0 + x) - (1.0 - x)


def _stats(vals):
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    sd = math.sqrt(var)
    se = sd / math.sqrt(n)
    return n, mean, sd, se


def compute():
    rng = random.Random(SEED)

    base_tax = []
    base_x = []
    base_rejects = 0
    for _ in range(TRIALS):
        x, rej = draw_x(rng, BASE)
        base_rejects += rej
        base_x.append(x)
        base_tax.append(tax_of(x))

    n, mean_tax, sd_tax, se_tax = _stats(base_tax)
    z1 = mean_tax / se_tax

    order = sorted(range(n), key=lambda i: base_x[i])
    third = n // 3
    low_tax = [base_tax[i] for i in order[:third]]
    high_tax = [base_tax[i] for i in order[-third:]]
    _, mean_low, _, se_low = _stats(low_tax)
    _, mean_high, _, se_high = _stats(high_tax)
    ratio = mean_high / mean_low
    z2 = (mean_high - mean_low) / math.sqrt(se_high ** 2 + se_low ** 2)

    shift_tax = []
    shift_rejects = 0
    for _ in range(TRIALS):
        x, rej = draw_x(rng, SHIFT)
        shift_rejects += rej
        shift_tax.append(tax_of(x))
    _, mean_shift, _, se_shift = _stats(shift_tax)
    z3_pos = mean_shift / se_shift
    z3_inc = (mean_shift - mean_tax) / math.sqrt(se_shift ** 2 + se_tax ** 2)

    g1 = bool(z1 >= Z_GATE and mean_tax > 0.0)
    g2 = bool(ratio >= RATIO_GATE and z2 >= Z_GATE)
    g3 = bool(z3_pos >= Z_GATE and z3_inc >= Z_GATE and mean_shift > mean_tax)
    all_pass = bool(g1 and g2 and g3)

    return {
        "proposal": 178,
        "head": "post-money SAFEs don't share dilution; stacking tax = x^2/(1+x), convex in aggregate SAFE ownership x",
        "seed": SEED,
        "trials": TRIALS,
        "x_cap": X_CAP,
        "baseline": {
            "mean_tax": round(mean_tax, 6),
            "sd_tax": round(sd_tax, 6),
            "mean_x": round(sum(base_x) / n, 6),
            "rejects": base_rejects,
        },
        "gate_G1_postmoney_more_dilutive": {
            "mean_tax": round(mean_tax, 6),
            "z": round(z1, 6),
            "z_gate": Z_GATE,
            "pass": g1,
        },
        "gate_G2_convex_in_stack": {
            "mean_tax_low_x": round(mean_low, 6),
            "mean_tax_high_x": round(mean_high, 6),
            "ratio_high_over_low": round(ratio, 6),
            "ratio_gate": RATIO_GATE,
            "z_diff": round(z2, 6),
            "z_gate": Z_GATE,
            "pass": g2,
        },
        "gate_G3_robust_under_heavier_stacking": {
            "mean_tax_shift": round(mean_shift, 6),
            "mean_tax_base": round(mean_tax, 6),
            "z_positive": round(z3_pos, 6),
            "z_increase": round(z3_inc, 6),
            "z_gate": Z_GATE,
            "shift_rejects": shift_rejects,
            "pass": g3,
        },
        "all_pass": all_pass,
    }


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert r1 == r2, "non-deterministic: in-process double-run differs"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256 " + digest)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
